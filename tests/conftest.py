import hashlib
import socket

import pytest
from fastapi.testclient import TestClient

from rag_core.api import create_app
from rag_core.errors import RagError
from rag_core.service import Service
from rag_core.settings import Settings


class FixtureEmbedder:
    """Test injection only; never registered as a configurable provider/model."""

    dimension = 384

    def encode(self, texts):
        values = []
        for text in texts:
            vector = [0.0] * 384
            for term in text.lower().split():
                vector[int(hashlib.sha256(term.encode()).hexdigest()[:8], 16) % 384] += 1
            norm = sum(v * v for v in vector) ** 0.5 or 1
            values.append([v / norm for v in vector])
        return values


class FixtureVectors:
    def __init__(self):
        self.points = {}
        self.outage = False
        self.fail_after_write = False
        self.deleted = []

    def ready(self):
        return not self.outage

    def upsert(self, wid, chunks, vectors):
        if self.outage:
            raise RagError("qdrant_unavailable", 503)
        self.points.setdefault(wid, {}).update(
            {c["id"]: (c, v) for c, v in zip(chunks, vectors, strict=True)}
        )
        if self.fail_after_write:
            raise RagError("qdrant_unavailable", 503)

    def search(self, wid, vector, documents):
        if self.outage:
            raise RagError("qdrant_unavailable", 503)
        return sorted(
            [
                (cid, sum(a * b for a, b in zip(v, vector, strict=True)))
                for cid, (c, v) in self.points.get(wid, {}).items()
                if c["document"] in documents
            ],
            key=lambda x: -x[1],
        )[:64]

    def delete(self, wid):
        if self.outage:
            raise RagError("qdrant_unavailable", 503)
        self.deleted.append(wid)
        self.points.pop(wid, None)


@pytest.fixture
def settings(tmp_path):
    state = tmp_path / "state"
    state.mkdir(mode=0o700)
    return Settings(
        state_dir=state, owner_token=hashlib.sha256(b"unique-test-owner-only").hexdigest()
    )


@pytest.fixture
def service(settings):
    return Service(settings, embedder=FixtureEmbedder(), vectors=FixtureVectors())


@pytest.fixture
def client(service):
    with TestClient(create_app(service.settings, service=service, start_worker=False)) as client:
        yield client


@pytest.fixture
def owner(settings):
    return {"Authorization": "Bearer " + settings.owner_token}


@pytest.fixture
def spaces(service):
    a = service.store.create_workspace("owner", "alpha")
    b = service.store.create_workspace("owner", "beta")
    return a, b


@pytest.fixture(autouse=True)
def forbid_network(request, monkeypatch):
    if request.node.get_closest_marker("integration") or request.node.get_closest_marker(
        "live_model"
    ):
        return

    def reject(*args, **kwargs):
        raise AssertionError("Network forbidden in deterministic tests")

    monkeypatch.setattr(socket, "create_connection", reject)
    monkeypatch.setattr(socket.socket, "connect", reject)
