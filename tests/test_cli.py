import io
import types

import httpx
import pytest

from rag_core import cli
from rag_core.errors import RagError
from rag_core.settings import MAX_FILE


def test_bounded_stdin_upload(settings, monkeypatch):
    monkeypatch.setattr(cli, "load_settings", lambda _: settings)
    monkeypatch.setattr(
        cli.sys, "stdin", types.SimpleNamespace(buffer=io.BytesIO(b"Synthetic stdin orchard"))
    )
    captured = []

    def handle(request):
        captured.append(request)
        assert request.content == b"Synthetic stdin orchard"
        assert request.url.params["filename"] == "orchard.txt"
        return httpx.Response(202, json={"state": "QUEUED"})

    original = httpx.Client
    monkeypatch.setattr(
        cli.httpx, "Client", lambda **kw: original(**kw, transport=httpx.MockTransport(handle))
    )
    args = cli.parser().parse_args(["ingest", "a" * 32, "-", "--filename", "orchard.txt"])
    assert cli.execute(args) == {"state": "QUEUED"}
    assert len(captured) == 1


@pytest.mark.parametrize(
    "arguments,data,code",
    [
        (["-"], b"text", "stdin_filename_required"),
        (["-", "--filename", "../escape.txt"], b"text", "invalid_filename"),
        (["-", "--filename", "large.txt"], b"x" * (MAX_FILE + 1), "file_size_limit"),
        (["file.txt", "--filename", "other.txt"], b"text", "filename_only_with_stdin"),
    ],
    ids=["missing-filename", "traversal-filename", "oversized-stdin", "filename-with-file"],
)
def test_stdin_input_validation(settings, monkeypatch, arguments, data, code):
    monkeypatch.setattr(cli, "load_settings", lambda _: settings)
    monkeypatch.setattr(cli.sys, "stdin", types.SimpleNamespace(buffer=io.BytesIO(data)))
    args = cli.parser().parse_args(["ingest", "a" * 32, *arguments])
    with pytest.raises(RagError, match=code):
        cli.execute(args)


def test_storage_errors_never_echo_private_paths(monkeypatch, capsys):
    import sqlite3

    monkeypatch.setattr(cli.sys, "argv", ["rag", "doctor"])

    def fail(_):
        raise sqlite3.OperationalError("/private/operator/credentials SECRET-SENTINEL")

    monkeypatch.setattr(cli, "execute", fail)
    with pytest.raises(SystemExit):
        cli.main()
    captured = capsys.readouterr()
    assert captured.err.strip() == '{"error": "storage_error"}'
