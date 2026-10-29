import io
import json
import subprocess
import zipfile

import numpy as np
import pytest
from defusedxml.common import DefusedXmlException
from pypdf import PdfWriter

from rag_core.embedding import OnnxEmbedder, mean_pool_normalize
from rag_core.errors import RagError
from rag_core.parsers import MAX_TEXT, extract, isolated_extract
from rag_core.service import Service, rank


def test_real_isolated_text_parser():
    text = "Orchard irrigation uses rainwater. " * 80
    chunks = isolated_extract(text.encode(), ".txt")
    assert len(chunks) > 1
    assert all(c["page"] is None for c in chunks)
    assert all(text[c["start"] : c["end"]] == c["text"] for c in chunks)
    assert all(len(c["text"]) <= 800 for c in chunks)


def test_docx_parser_has_no_fabricated_page():
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as z:
        z.writestr(
            "word/document.xml",
            '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>Original synthetic orchard evidence.</w:t></w:r></w:p></w:body></w:document>',
        )
    result = isolated_extract(buffer.getvalue(), ".docx")
    assert result[0]["page"] is None
    assert "orchard" in result[0]["text"]


def test_pdf_page_limit_and_encryption():
    writer = PdfWriter()
    for _ in range(101):
        writer.add_blank_page(width=100, height=100)
    buffer = io.BytesIO()
    writer.write(buffer)
    with pytest.raises(RagError, match="pdf_limit"):
        extract(buffer.getvalue(), ".pdf")
    writer = PdfWriter()
    writer.add_blank_page(width=100, height=100)
    writer.encrypt("private")
    buffer = io.BytesIO()
    writer.write(buffer)
    with pytest.raises(RagError, match="pdf_limit"):
        extract(buffer.getvalue(), ".pdf")


@pytest.mark.parametrize(
    "data,ext",
    [
        (b"\0\0", ".txt"),
        (b"\xff", ".txt"),
        (b"not pdf", ".pdf"),
        (b"not zip", ".docx"),
        (b"empty", ".exe"),
        (b"", ".txt"),
        (b"x" * (MAX_TEXT + 1), ".txt"),
    ],
)
def test_parser_rejects_invalid_or_oversized(data, ext):
    with pytest.raises((RagError, UnicodeError)):
        extract(data, ext)


def test_docx_zip_bomb_and_xml_entities():
    for content in [
        "x" * (9 * 1024 * 1024),
        '<!DOCTYPE x [<!ENTITY boom SYSTEM "file:///etc/passwd">]><x>&boom;</x>',
    ]:
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("word/document.xml", content)
        with pytest.raises((RagError, DefusedXmlException)):
            extract(buffer.getvalue(), ".docx")


def test_parser_deadline_and_crash(monkeypatch):
    def timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired("parser", 15)

    monkeypatch.setattr(subprocess, "run", timeout)
    with pytest.raises(RagError, match="parser_timeout"):
        isolated_extract(b"test", ".txt")
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *a, **kw: subprocess.CompletedProcess("parser", -9, b"", b"SECRET"),
    )
    with pytest.raises(RagError, match="parser_rejected"):
        isolated_extract(b"test", ".txt")


def test_masked_mean_pool_and_l2():
    hidden = np.array([[[1.0, 0.0], [0.0, 1.0], [100.0, 100.0]]])
    result = mean_pool_normalize(hidden, [[1, 1, 0]])
    np.testing.assert_allclose(result, [[2**-0.5, 2**-0.5]], atol=1e-7)
    np.testing.assert_allclose(np.linalg.norm(result, axis=1), [1])


def test_no_model_autodownload(settings):
    with pytest.raises(RagError, match="model_not_installed"):
        OnnxEmbedder(settings).encode(["test"])


def test_ingest_restart_idempotent_source_citation(service, spaces):
    wid = spaces[0]["id"]
    text = "Orchard irrigation uses rainwater stored in a blue tank."
    job = service.submit("owner", wid, "orchard.txt", text.encode())
    assert job["state"] == "QUEUED"
    assert service.search("owner", wid, "orchard")["status"] == "no_match"
    restarted = Service(service.settings, embedder=service.embedder, vectors=service.vectors)
    restarted.recover()
    assert restarted.run_one()
    assert restarted.job("owner", wid, job["id"])["state"] == "COMPLETED"
    found = restarted.search("owner", wid, "orchard rainwater")
    assert found["status"] == "matched"
    hit = found["matches"][0]
    persisted = restarted.chunk("owner", wid, hit["id"])
    assert hit["excerpt"] == text[persisted["start"] : persisted["end"]]
    assert hit["document"] == job["document"]
    assert hit["page"] is None
    assert hit["citation"] == f"{wid}:{job['document']}:{hit['id']}"
    assert restarted.submit("owner", wid, "renamed.txt", text.encode())["id"] == job["id"]
    assert len(restarted.documents("owner", wid)) == 1
    other = restarted.submit("owner", wid, "orchard.txt", b"Other distinct rainwater content")
    restarted.run_one()
    assert other["document"] != job["document"]
    assert len(restarted.documents("owner", wid)) == 2
    assert not service.vectors.deleted


def test_failed_partial_vectors_not_visible_retry_does_not_reset(service, spaces):
    wid = spaces[0]["id"]
    first = service.submit("owner", wid, "stable.txt", b"Stable orchard evidence")
    service.run_one()
    service.vectors.fail_after_write = True
    failed = service.submit("owner", wid, "uncommitted.txt", b"Uncommitted submarine evidence")
    service.run_one()
    assert service.job("owner", wid, failed["id"])["state"] == "FAILED"
    assert len(service.vectors.points[wid]) == 2
    assert service.search("owner", wid, "submarine")["status"] == "no_match"
    assert len(service.documents("owner", wid)) == 1
    service.vectors.fail_after_write = False
    retry = service.submit("owner", wid, "uncommitted.txt", b"Uncommitted submarine evidence")
    service.run_one()
    assert retry["id"] != failed["id"]
    assert service.job("owner", wid, retry["id"])["state"] == "COMPLETED"
    assert service.job("owner", wid, first["id"])["state"] == "COMPLETED"
    assert len(service.vectors.points[wid]) == 2
    assert len(service.documents("owner", wid)) == 2
    assert not service.vectors.deleted


def test_cancel_after_index_ack_before_publication(service, spaces):
    wid = spaces[0]["id"]
    job = service.submit("owner", wid, "cancel.txt", b"Cancelled orchard evidence")
    upsert = service.vectors.upsert

    def cancel_during_upsert(*args):
        upsert(*args)
        service.cancel("owner", wid, job["id"])

    service.vectors.upsert = cancel_during_upsert
    service.run_one()
    assert service.job("owner", wid, job["id"])["state"] == "CANCELLED"
    assert service.search("owner", wid, "orchard")["status"] == "no_match"
    assert service.documents("owner", wid) == []


def test_recover_running_job_and_checkpoint(service, spaces):
    wid = spaces[0]["id"]
    job = service.submit("owner", wid, "recover.txt", b"Recover orchard evidence")
    with service.store.connect() as db:
        db.execute("UPDATE jobs SET state='RUNNING',checkpoint='embedded' WHERE id=?", (job["id"],))
    restored = Service(service.settings, embedder=service.embedder, vectors=service.vectors)
    restored.recover()
    assert restored.job("owner", wid, job["id"])["checkpoint"] == "recovered"
    restored.run_one()
    assert restored.job("owner", wid, job["id"])["checkpoint"] == "committed"


def test_delete_confirmation_tombstone_outage_and_scope(service, spaces):
    a, b = spaces
    for ws in (a, b):
        service.submit("owner", ws["id"], "orchard.txt", b"Orchard evidence")
        service.run_one()
    with pytest.raises(RagError):
        service.delete_workspace("owner", a["id"], b["id"])
    assert len(service.documents("owner", a["id"])) == 1
    with pytest.raises(RagError):
        service.delete_workspace(a["id"], b["id"], b["id"])
    service.vectors.outage = True
    with pytest.raises(RagError, match="qdrant_unavailable"):
        service.delete_workspace("owner", a["id"], a["id"])
    with pytest.raises(RagError):
        service.documents("owner", a["id"])
    service.vectors.outage = False
    service.delete_workspace("owner", a["id"], a["id"])
    assert len(service.documents("owner", b["id"])) == 1
    assert service.vectors.deleted == [a["id"]]
    with service.store.connect() as db:
        assert (
            db.execute("SELECT state FROM workspaces WHERE id=?", (a["id"],)).fetchone()[0]
            == "DELETED"
        )
        assert (
            db.execute("SELECT count(*) FROM chunks WHERE workspace=?", (a["id"],)).fetchone()[0]
            == 0
        )


def test_qdrant_outage_is_not_empty_success(service, spaces, client, owner):
    wid = spaces[0]["id"]
    service.submit("owner", wid, "orchard.txt", b"Orchard evidence")
    service.run_one()
    service.vectors.outage = True
    response = client.post(f"/workspaces/{wid}/search", headers=owner, json={"query": "orchard"})
    assert response.status_code == 503
    assert response.json() == {"error": "qdrant_unavailable"}
    assert client.get("/health").status_code == 503


def test_model_metadata_mismatch(service, spaces):
    wid = spaces[0]["id"]
    with service.store.connect() as db:
        db.execute(
            "UPDATE workspaces SET metadata=? WHERE id=?", (json.dumps({"dimension": 768}), wid)
        )
    with pytest.raises(RagError, match="index_version_mismatch"):
        service.search("owner", wid, "query")


def test_ranking_reproducible_rerank_and_no_match():
    chunks = [
        {"id": "a", "text": "orchard rainwater irrigation"},
        {"id": "b", "text": "rainwater tank"},
    ]
    dense = [("b", 0.8), ("a", 0.7)]
    first = rank("orchard rainwater", chunks, dense, True)
    assert first == rank("orchard rainwater", chunks, list(reversed(dense)), True)
    assert first[0]["id"] == "a"
    assert first[0]["ranking"]["reranker"] == "term-coverage-v1"
    assert rank("orchard", chunks, dense, False)[0]["ranking"]["reranker"] == "disabled"
    assert rank("xylophone", chunks, [("a", 0.1)], True) == []
