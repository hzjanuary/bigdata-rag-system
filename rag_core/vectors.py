from qdrant_client import QdrantClient, models

from .errors import RagError
from .settings import Settings, identifier


def collection(wid: str) -> str:
    return "rag_" + identifier(wid)


class Vectors:
    def __init__(self, settings: Settings):
        self.dimension = settings.dimension
        self.client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_key,
            timeout=5,
            check_compatibility=False,
        )

    def ready(self) -> bool:
        try:
            self.client.get_collections()
            return True
        except Exception:
            return False

    def ensure(self, wid: str, create: bool = False):
        name = collection(wid)
        try:
            if not self.client.collection_exists(name):
                if not create:
                    raise RagError("index_missing", 503)
                self.client.create_collection(
                    name,
                    vectors_config=models.VectorParams(
                        size=self.dimension, distance=models.Distance.COSINE
                    ),
                )
            config = self.client.get_collection(name).config.params.vectors
            if (
                not isinstance(config, models.VectorParams)
                or config.size != self.dimension
                or config.distance != models.Distance.COSINE
            ):
                raise RagError("index_dimension_mismatch", 409)
        except RagError:
            raise
        except Exception:
            raise RagError("qdrant_unavailable", 503) from None

    def upsert(self, wid: str, chunks: list[dict], vectors: list[list[float]]):
        if len(chunks) != len(vectors) or any(len(v) != self.dimension for v in vectors):
            raise RagError("embedding_dimension_error", 409)
        self.ensure(wid, create=True)
        try:
            for start in range(0, len(chunks), 32):
                points = [
                    models.PointStruct(
                        id=c["id"],
                        vector=v,
                        payload={"workspace": wid, "document": c["document"], "chunk": c["id"]},
                    )
                    for c, v in zip(
                        chunks[start : start + 32], vectors[start : start + 32], strict=True
                    )
                ]
                self.client.upsert(collection(wid), points=points, wait=True)
        except Exception:
            raise RagError("qdrant_unavailable", 503) from None

    def search(
        self, wid: str, vector: list[float], documents: list[str]
    ) -> list[tuple[str, float]]:
        if len(vector) != self.dimension:
            raise RagError("embedding_dimension_error", 409)
        self.ensure(wid)
        try:
            points = self.client.query_points(
                collection(wid),
                query=vector,
                query_filter=models.Filter(
                    must=[
                        models.FieldCondition(key="workspace", match=models.MatchValue(value=wid)),
                        models.FieldCondition(key="document", match=models.MatchAny(any=documents)),
                    ]
                ),
                limit=64,
                with_payload=False,
            ).points
            return [(str(p.id).replace("-", ""), p.score) for p in points]
        except Exception:
            raise RagError("qdrant_unavailable", 503) from None

    def delete(self, wid: str):
        try:
            if self.client.collection_exists(collection(wid)):
                self.client.delete_collection(collection(wid))
        except Exception:
            raise RagError("qdrant_unavailable", 503) from None
