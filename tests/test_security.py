import json
import stat
import uuid
from pathlib import Path

import pytest
from pydantic import ValidationError

from rag_core.cli import read_local
from rag_core.errors import RagError
from rag_core.settings import (
    MAX_FILE,
    Settings,
    filename,
    identifier,
    initialize,
    load_settings,
    slug,
)


@pytest.mark.parametrize(
    "value",
    [
        "../x",
        "..",
        "/etc",
        "a/b",
        "a\\b",
        "%2e%2e",
        "ALPHA",
        "álpha",
        "ａｌｐｈａ",
        "a_b",
        "a.b",
        "",
        "a" * 49,
    ],
)
def test_slug_rejects_aliases(value):
    with pytest.raises(RagError):
        slug(value)


@pytest.mark.parametrize(
    "value", ["../", str(uuid.uuid4()), "%2f", "0" * 31, "A" * 32, "x" * 32, ""]
)
def test_opaque_identifier(value):
    with pytest.raises(RagError):
        identifier(value)


@pytest.mark.parametrize(
    "name", ["../x.txt", "/x.txt", "a\\x.txt", "a..txt", "á.txt", "x.exe", "x.TXT"]
)
def test_filename_validation(name):
    with pytest.raises(RagError):
        filename(name)


def test_private_init_and_refuse_overwrite(tmp_path):
    config = tmp_path / "private" / "config.json"
    state = tmp_path / "state"
    initialize(config, state)
    settings = load_settings(config)
    assert stat.S_IMODE(config.stat().st_mode) == 0o600
    assert stat.S_IMODE(state.stat().st_mode) == 0o700
    assert len(settings.owner_token) == 64
    assert not settings.generation_enabled
    assert list(state.iterdir()) == []
    before = config.read_bytes()
    with pytest.raises(RagError):
        initialize(config, state)
    assert config.read_bytes() == before
    config.chmod(0o644)
    with pytest.raises(RagError):
        load_settings(config)


@pytest.mark.parametrize("token", ["", "change-me", "your_api_key_here", "0" * 64])
def test_placeholder_owner_rejected(settings, token):
    with pytest.raises(ValidationError):
        Settings(**{**settings.model_dump(), "owner_token": token})


def test_symlink_config_state_and_import(tmp_path, settings):
    source = tmp_path / "source.txt"
    source.write_text("allowed")
    link = tmp_path / "alias.txt"
    link.symlink_to(source)
    with pytest.raises(RagError):
        read_local(link)
    directory = tmp_path / "directory"
    directory.symlink_to(tmp_path, target_is_directory=True)
    with pytest.raises(RagError):
        read_local(directory / "source.txt")
    with pytest.raises(RagError):
        initialize(directory / "config.json", tmp_path / "newstate")
    source.write_bytes(b"x" * (MAX_FILE + 1))
    with pytest.raises(RagError):
        read_local(source)
    assert read_local(Path(__file__))


def test_database_symlink_rejected(settings, tmp_path):
    from rag_core.store import Store

    target = tmp_path / "valuable"
    target.write_text("untouched")
    (settings.state_dir / "metadata.sqlite3").symlink_to(target)
    with pytest.raises(RagError):
        Store(settings)
    assert target.read_text() == "untouched"


def test_all_routes_require_auth(client):
    for route in client.app.routes:
        if route.path == "/health":
            continue
        path = (
            route.path.replace("{wid}", "a" * 32)
            .replace("{jid}", "b" * 32)
            .replace("{cid}", "c" * 32)
            .replace("{did}", "d" * 32)
        )
        for method in route.methods:
            response = client.request(method, path, json={})
            assert response.status_code == 401, (method, path, response.text)
            response = client.request(
                method, path, json={}, headers={"Authorization": "Bearer change-me"}
            )
            assert response.status_code == 401


def test_isolation_every_route(client, service, owner, spaces):
    a, b = spaces
    cap = {"Authorization": "Bearer " + a["capability"]}
    assert client.get("/workspaces", headers=cap).json() == [
        {"id": a["id"], "slug": "alpha", "state": "ACTIVE"}
    ]
    job = service.submit("owner", b["id"], "private.txt", b"secret beta content")
    service.run_one()
    chunk = service.search("owner", b["id"], "beta")["matches"][0]
    root = "/workspaces/" + b["id"]
    cases = [
        ("GET", "/documents", {}),
        (
            "POST",
            "/documents?filename=x.txt",
            {"content": b"x", "headers": {**cap, "Content-Type": "text/plain"}},
        ),
        ("GET", f"/jobs/{job['id']}", {}),
        ("POST", f"/jobs/{job['id']}/cancel", {}),
        ("GET", f"/chunks/{chunk['id']}", {}),
        ("GET", f"/documents/{job['document']}/content", {}),
        ("POST", "/search", {"json": {"query": "secret"}}),
        ("POST", "/ask", {"json": {"query": "secret"}}),
        ("GET", "/events", {}),
        ("DELETE", "?confirm=" + b["id"], {}),
    ]
    for method, suffix, kwargs in cases:
        kwargs.setdefault("headers", cap)
        response = client.request(method, root + suffix, **kwargs)
        assert response.status_code in {403, 404}, (suffix, response.text)
        assert "secret beta" not in response.text
    assert client.post("/workspaces", headers=cap, json={"slug": "unallowed"}).status_code == 403
    assert service.documents("owner", b["id"])


def test_cors_unsafe_routes_and_validation(client, owner, spaces):
    assert (
        "access-control-allow-origin"
        not in client.get("/health", headers={"Origin": "https://evil.invalid"}).headers
    )
    for old in [
        "/pipeline/start",
        "/upload",
        "/metrics",
        "/traces",
        "/logs",
        "/ask",
        "/batch/query",
    ]:
        assert client.post(old, headers=owner).status_code in {404, 405}
    for value in ["%2e%2e", "%252f", "not-an-id"]:
        assert client.get(f"/workspaces/{value}/documents", headers=owner).status_code in {400, 404}
    assert client.post("/workspaces", headers=owner, json={"slug": "alpha"}).status_code == 409
    response = client.post(
        "/workspaces", headers=owner, json={"slug": "bad", "secret": "SENSITIVE-SENTINEL"}
    )
    assert response.status_code == 422
    assert "SENSITIVE" not in response.text


def test_body_limits_and_mime(client, owner, spaces):
    wid = spaces[0]["id"]
    endpoint = f"/workspaces/{wid}/documents?filename=test.txt"
    assert (
        client.post(
            endpoint, headers={**owner, "Content-Type": "text/plain"}, content=b"x" * (MAX_FILE + 1)
        ).status_code
        == 413
    )
    assert (
        client.post(
            endpoint, headers={**owner, "Content-Type": "image/png"}, content=b"abc"
        ).status_code
        == 415
    )
    assert client.post("/workspaces", headers=owner, content=b"x" * 20000).status_code == 413

    def oversized():
        for _ in range(65):
            yield b"x" * 65536

    assert (
        client.post(
            endpoint, headers={**owner, "Content-Type": "text/plain"}, content=oversized()
        ).status_code
        == 413
    )


def test_secret_redaction(client, owner, service, spaces, caplog, capsys):
    wid = spaces[0]["id"]
    secret = "SENSITIVE-SENTINEL-NOT-FOR-LOGS"
    service.extractor = lambda *args: (_ for _ in ()).throw(
        RuntimeError(secret + "/private/path " + service.settings.owner_token)
    )
    job = service.submit("owner", wid, "private.txt", secret.encode())
    service.run_one()
    public = json.dumps(service.job("owner", wid, job["id"]))
    audit = client.get(f"/workspaces/{wid}/events", headers=owner).text
    captured = capsys.readouterr()
    for output in (public, audit, caplog.text, captured.out, captured.err):
        assert secret not in output
        assert service.settings.owner_token not in output
        assert "/private/path" not in output
    assert "indexing_failed" in public


def test_no_seed(service):
    assert service.store.list_workspaces("owner") == []
    with service.store.connect() as db:
        assert db.execute("SELECT count(*) FROM jobs").fetchone()[0] == 0
