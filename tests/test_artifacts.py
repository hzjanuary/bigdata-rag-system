import importlib.util
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location(
    "source_gate", Path(__file__).parents[1] / "scripts/source_gate.py"
)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


@pytest.mark.parametrize(
    "path,data,symlink",
    [
        (".env", b"credential", False),
        ("docs/.env", b"credential", False),
        (".local/model.onnx", b"weights", False),
        ("docs/data.pdf", b"%PDF-", False),
        ("uploads/document.txt", b"content", False),
        ("docs/operator.sqlite3", b"data", False),
        ("rag_core/config.json", b"{}", True),
        ("docs/x.json", b"Bearer " + b"0" * 64, False),
        ("docs/key.txt", b"-----BEGIN " + b"PRIVATE KEY-----", False),
        ("docs/private-path.txt", b"/home/person/" + b".config/rag/config.json", False),
        ("docs/x.txt", b"\0binary", False),
        ("docs/large.txt", b"x" * 2_000_001, False),
    ],
)
def test_gate_catches_bypasses(path, data, symlink):
    with pytest.raises(ValueError):
        gate.inspect(path, data, symlink=symlink)


def test_gate_accepts_documented_source():
    gate.inspect("rag_core/service.py", b"public source")
    gate.inspect("examples/corpus/orchard.txt", b"Original MIT synthetic document")


def test_historical_secret_review_rejects_new_findings():
    location = Path(__file__).parents[1] / "scripts/history_secret_gate.py"
    module_spec = importlib.util.spec_from_file_location("history_gate", location)
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    with pytest.raises(ValueError, match="unreviewed"):
        module.review(
            [{"Fingerprint": "different:commit:path:generic-api-key:12"}], location.parents[1]
        )
    assert module.review([], location.parents[1]) == []
