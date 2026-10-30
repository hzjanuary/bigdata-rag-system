import fcntl
import os

import pytest
from qdrant_client import QdrantClient, models

from rag_core import backup
from rag_core.errors import RagError
from rag_core.service import Service
from rag_core.settings import Settings
from rag_core.vectors import Vectors, collection


def local_vectors(settings):
    vectors = Vectors(settings)
    vectors.client = QdrantClient(":memory:")
    return vectors


def test_qdrant_contract_dimensions_and_filters(settings):
    vectors = local_vectors(settings)
    a, b = "a" * 32, "b" * 32
    cid, did = "c" * 32, "d" * 32
    with pytest.raises(RagError, match="embedding_dimension_error"):
        vectors.upsert(a, [{"id": cid}], [[1.0, 0.0]])
    vectors.client.create_collection(
        collection(a), vectors_config=models.VectorParams(size=768, distance=models.Distance.COSINE)
    )
    with pytest.raises(RagError, match="index_dimension_mismatch"):
        vectors.ensure(a)
    vectors.client.delete_collection(collection(a))
    vector = [1.0] + [0.0] * 383
    chunks = [{"id": cid, "document": did}]
    vectors.upsert(a, chunks, [vector])
    assert vectors.search(a, vector, [did])[0][0] == cid
    assert vectors.search(a, vector, ["e" * 32]) == []
    vectors.ensure(b, create=True)
    assert vectors.search(b, vector, [did]) == []


def test_backup_restore_contract_and_tamper(settings, tmp_path, monkeypatch, service):
    vectors = local_vectors(settings)
    service.vectors = vectors
    workspace = service.store.create_workspace("owner", "original")
    wid = workspace["id"]
    queued = service.submit("owner", wid, "original.txt", b"Orchard rainwater blue tank")
    service.run_one()
    pending = service.submit("owner", wid, "pending.txt", b"Pending ingestion record")
    expected = service.search("owner", wid, "orchard")
    monkeypatch.setattr(backup, "Vectors", lambda s: vectors)
    destination = tmp_path / "backup"
    result = backup.create(settings, destination)
    assert result == {"status": "backed_up", "points": 1}
    with pytest.raises(RagError, match="backup_destination_exists"):
        backup.create(settings, destination)
    restore_state = tmp_path / "restored"
    restore_state.mkdir(mode=0o700)
    restored_settings = Settings(**{**settings.model_dump(), "state_dir": restore_state})
    restored_vectors = local_vectors(restored_settings)
    monkeypatch.setattr(backup, "Vectors", lambda s: restored_vectors)
    assert backup.restore(restored_settings, destination)["points"] == 1
    restored = Service(restored_settings, vectors=restored_vectors, embedder=service.embedder)
    assert restored.search("owner", wid, "orchard") == expected
    assert restored.job("owner", wid, queued["id"])["state"] == "COMPLETED"
    assert restored.job("owner", wid, pending["id"])["state"] == "QUEUED"
    assert restored.store.authenticate(workspace["capability"]) == wid
    with pytest.raises(RagError, match="restore_requires_empty_installation"):
        backup.restore(restored_settings, destination)
    (destination / "vectors.jsonl").write_text("{}\n")
    with pytest.raises(RagError, match="backup_integrity_error"):
        backup.restore(restored_settings, destination)


def test_backup_requires_stopped_api(settings, tmp_path):
    fd = os.open(settings.state_dir / "instance.lock", os.O_CREAT | os.O_RDWR, 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        with pytest.raises(RagError, match="stop_api_before_backup_restore"):
            backup.create(settings, tmp_path / "backup")
    finally:
        os.close(fd)
