"""Real Qdrant service contract, fixture vectors only; no model inference/download."""

import os

import pytest
from qdrant_client import models

from rag_core.errors import RagError
from rag_core.service import Service
from rag_core.settings import Settings
from rag_core.vectors import Vectors, collection


@pytest.mark.integration
def test_real_qdrant_committed_isolation_retry_dimensions(settings, service):
    url = os.environ.get("RAG_TEST_QDRANT_URL")
    if not url or os.environ.get("RAG_TEST_QDRANT_ISOLATED") != "yes":
        pytest.skip("requires an explicitly isolated disposable Qdrant service")
    configured = Settings(**{**settings.model_dump(), "qdrant_url": url})
    vectors = Vectors(configured)
    actual = Service(configured, embedder=service.embedder, vectors=vectors)
    a = actual.store.create_workspace("owner", "contract-alpha")
    b = actual.store.create_workspace("owner", "contract-beta")
    try:
        wid = a["id"]
        first = actual.submit("owner", wid, "original.txt", b"Orchard rainwater blue tank")
        actual.run_one()
        assert actual.job("owner", wid, first["id"])["state"] == "COMPLETED"
        found = actual.search(wid, wid, "rainwater")
        assert found["status"] == "matched"
        assert actual.search(b["id"], b["id"], "rainwater")["status"] == "no_match"
        assert (
            actual.submit("owner", wid, "copy.txt", b"Orchard rainwater blue tank")["id"]
            == first["id"]
        )
        with pytest.raises(RagError):
            actual.delete_workspace(b["id"], wid, wid)
        # Check the actual server's metadata, then use a separately created empty
        # workspace to prove incompatible dimensions fail without an implicit reset.
        assert vectors.client.get_collection(collection(wid)).config.params.vectors.size == 384
        vectors.client.create_collection(
            collection(b["id"]),
            vectors_config=models.VectorParams(size=768, distance=models.Distance.COSINE),
        )
        with pytest.raises(RagError, match="index_dimension_mismatch"):
            vectors.ensure(b["id"])
        assert actual.search(wid, wid, "rainwater") == found
    finally:
        # Only IDs allocated by this test; never discover or delete other collections.
        for workspace in (a, b):
            vectors.delete(workspace["id"])
