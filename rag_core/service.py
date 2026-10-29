import hashlib
import math
import threading
import time
import uuid
from collections import Counter
from pathlib import Path

from .embedding import OnnxEmbedder
from .errors import RagError
from .parsers import isolated_extract
from .settings import MAX_FILE, Settings, filename, identifier
from .store import Store
from .vectors import Vectors


def tokenize(text: str) -> list[str]:
    import re

    return re.findall(r"\w+", text.casefold())[:2000]


def rank(
    query: str, chunks: list[dict], dense: list[tuple[str, float]], rerank: bool
) -> list[dict]:
    """BM25 k1=1.5,b=.75 + RRF(k=60); optional deterministic term-coverage rerank."""
    terms = set(tokenize(query))
    if not terms or not chunks:
        return []
    tokens = {c["id"]: Counter(tokenize(c["text"])) for c in chunks}
    avg = sum(sum(t.values()) for t in tokens.values()) / len(chunks)
    lexical = {}
    for cid, tf in tokens.items():
        score = 0.0
        for term in terms:
            df = sum(term in t for t in tokens.values())
            freq = tf[term]
            idf = math.log(1 + (len(chunks) - df + 0.5) / (df + 0.5))
            score += (
                idf * freq * 2.5 / (freq + 1.5 * (0.25 + 0.75 * sum(tf.values()) / max(avg, 1)))
            )
        if score > 0:
            lexical[cid] = score
    bm_order = sorted(lexical, key=lambda c: (-lexical[c], c))[:64]
    dense_scores = {cid: score for cid, score in dense if score >= 0.35}
    dense_order = sorted(dense_scores, key=lambda c: (-dense_scores[c], c))
    fused = {}
    for order in (bm_order, dense_order):
        for i, cid in enumerate(order):
            fused[cid] = fused.get(cid, 0) + 1 / (60 + i + 1)
    candidates = []
    for chunk in chunks:
        cid = chunk["id"]
        if cid not in fused:
            continue
        coverage = len(terms.intersection(tokens[cid])) / len(terms)
        score = fused[cid] + (0.02 * coverage if rerank else 0)
        candidates.append(
            {
                **chunk,
                "excerpt": chunk["text"][:800],
                "ranking": {
                    "dense_cosine": dense_scores.get(cid),
                    "bm25": lexical.get(cid, 0),
                    "rrf": fused[cid],
                    "reranker": "term-coverage-v1" if rerank else "disabled",
                    "term_coverage": coverage if rerank else None,
                    "score": score,
                },
            }
        )
    return sorted(candidates, key=lambda c: (-c["ranking"]["score"], c["id"]))


class Service:
    def __init__(self, settings: Settings, *, embedder=None, vectors=None, extractor=None):
        self.settings = settings
        self.store = Store(settings)
        self.embedder = embedder if embedder is not None else OnnxEmbedder(settings)
        self.vectors = vectors if vectors is not None else Vectors(settings)
        self.extractor = extractor if extractor is not None else isolated_extract
        self.worker_lock = threading.Lock()
        self.operation_lock = threading.RLock()

    def submit(self, principal: str, wid: str, name: str, data: bytes) -> dict:
        self.store.workspace(principal, wid)
        filename(name)
        if not data or len(data) > MAX_FILE:
            raise RagError("file_size_limit", 413)
        digest = hashlib.sha256(data).hexdigest()
        # Parser format participates in identity; filenames do not overwrite documents.
        did = hashlib.sha256((Path(name).suffix + digest).encode()).hexdigest()[:32]
        jid, now = uuid.uuid4().hex, time.time()
        with self.store.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            self._active(db, wid)
            previous = db.execute(
                "SELECT id FROM jobs WHERE workspace=? AND document=? AND state IN ('QUEUED','RUNNING','COMPLETED') ORDER BY created DESC LIMIT 1",
                (wid, did),
            ).fetchone()
            if previous:
                return self.job(principal, wid, previous["id"])
            count = db.execute("SELECT count(*) FROM jobs WHERE workspace=?", (wid,)).fetchone()[0]
            active = db.execute(
                "SELECT count(*) FROM jobs WHERE state IN ('QUEUED','RUNNING')"
            ).fetchone()[0]
            total = db.execute("SELECT count(*) FROM jobs").fetchone()[0]
            if count >= 128 or active >= 32 or total >= 2048:
                raise RagError("job_limit", 429)
            db.execute(
                "INSERT INTO jobs VALUES(?,?,?,?,?,'QUEUED','stored',NULL,?,?)",
                (jid, wid, did, name, data, now, now),
            )
            self.store.audit(db, "ingest_queued", wid, jid)
        return self.job(principal, wid, jid)

    @staticmethod
    def _active(db, wid):
        row = db.execute("SELECT state FROM workspaces WHERE id=?", (wid,)).fetchone()
        if not row or row[0] != "ACTIVE":
            raise RagError("workspace_not_found", 404)

    def job(self, principal: str, wid: str, jid: str) -> dict:
        self.store.workspace(principal, wid)
        identifier(jid)
        with self.store.connect() as db:
            row = db.execute(
                "SELECT id,workspace,document,filename,state,checkpoint,error,created,updated FROM jobs WHERE id=? AND workspace=?",
                (jid, wid),
            ).fetchone()
        if not row:
            raise RagError("job_not_found", 404)
        return dict(row)

    def cancel(self, principal: str, wid: str, jid: str) -> dict:
        self.job(principal, wid, jid)
        with self.store.connect() as db:
            db.execute(
                "UPDATE jobs SET state='CANCELLED',content=NULL,updated=? WHERE id=? AND workspace=? AND state IN ('QUEUED','RUNNING')",
                (time.time(), jid, wid),
            )
            self.store.audit(db, "ingest_cancelled", wid, jid)
        return self.job(principal, wid, jid)

    def recover(self):
        # Called only under the process-wide exclusive worker lock at startup.
        with self.store.connect() as db:
            db.execute(
                "UPDATE jobs SET state='QUEUED',checkpoint='recovered',updated=? WHERE state='RUNNING'",
                (time.time(),),
            )

    def checkpoint(self, jid: str, stage: str):
        with self.store.connect() as db:
            if (
                db.execute(
                    "UPDATE jobs SET checkpoint=?,updated=? WHERE id=? AND state='RUNNING'",
                    (stage, time.time(), jid),
                ).rowcount
                != 1
            ):
                raise RagError("job_cancelled")

    def run_one(self) -> bool:
        if not self.worker_lock.acquire(blocking=False):
            return False
        try:
            with self.store.connect() as db:
                db.execute("BEGIN IMMEDIATE")
                row = db.execute(
                    "SELECT * FROM jobs WHERE state='QUEUED' ORDER BY created LIMIT 1"
                ).fetchone()
                if not row:
                    return False
                job = dict(row)
                db.execute(
                    "UPDATE jobs SET state='RUNNING',updated=? WHERE id=?", (time.time(), job["id"])
                )
            try:
                self.store.workspace("owner", job["workspace"])
                chunks = self.extractor(job["content"], Path(job["filename"]).suffix)
                for chunk in chunks:
                    chunk["id"] = uuid.uuid5(
                        uuid.UUID(job["workspace"]), f"{job['document']}:{chunk['ordinal']}"
                    ).hex
                    chunk["document"] = job["document"]
                self.checkpoint(job["id"], "extracted")
                vectors = self.embedder.encode([c["text"] for c in chunks])
                self.checkpoint(job["id"], "embedded")
                # Serialize destructive operations against index side effects and publication.
                with self.operation_lock:
                    self.store.workspace("owner", job["workspace"])
                    with self.store.connect() as db:
                        existing = db.execute(
                            "SELECT count(*) FROM chunks WHERE workspace=?", (job["workspace"],)
                        ).fetchone()[0]
                    if existing + len(chunks) > 4096:
                        raise RagError("workspace_chunk_limit", 429)
                    self.vectors.upsert(job["workspace"], chunks, vectors)
                    self.checkpoint(job["id"], "indexed")
                    with self.store.connect() as db:
                        db.execute("BEGIN IMMEDIATE")
                        self._active(db, job["workspace"])
                        state = db.execute(
                            "SELECT state FROM jobs WHERE id=?", (job["id"],)
                        ).fetchone()[0]
                        if state != "RUNNING":
                            raise RagError("job_cancelled")
                        db.execute(
                            "INSERT OR IGNORE INTO documents VALUES(?,?,?,?,?)",
                            (
                                job["document"],
                                job["workspace"],
                                job["filename"],
                                hashlib.sha256(job["content"]).hexdigest(),
                                job["content"],
                            ),
                        )
                        for c in chunks:
                            db.execute(
                                "INSERT OR IGNORE INTO chunks VALUES(?,?,?,?,?,?,?,?)",
                                (
                                    c["id"],
                                    job["workspace"],
                                    job["document"],
                                    c["page"],
                                    c["ordinal"],
                                    c["start"],
                                    c["end"],
                                    c["text"],
                                ),
                            )
                        db.execute(
                            "UPDATE jobs SET state='COMPLETED',checkpoint='committed',content=NULL,updated=? WHERE id=?",
                            (time.time(), job["id"]),
                        )
                        self.store.audit(db, "ingest_committed", job["workspace"], job["id"])
            except Exception as exc:
                error = exc.code if isinstance(exc, RagError) else "indexing_failed"
                with self.store.connect() as db:
                    db.execute(
                        "UPDATE jobs SET state='FAILED',error=?,updated=? WHERE id=? AND state='RUNNING'",
                        (error, time.time(), job["id"]),
                    )
                    self.store.audit(db, "ingest_failed", job["workspace"], job["id"])
            return True
        finally:
            self.worker_lock.release()

    def documents(self, principal: str, wid: str) -> list[dict]:
        self.store.workspace(principal, wid)
        with self.store.connect() as db:
            return [
                dict(r)
                for r in db.execute(
                    "SELECT id,filename,content_hash FROM documents WHERE workspace=? ORDER BY id",
                    (wid,),
                )
            ]

    def chunk(self, principal: str, wid: str, cid: str) -> dict:
        self.store.workspace(principal, wid)
        identifier(cid)
        with self.store.connect() as db:
            row = db.execute(
                "SELECT c.*,d.filename,d.content_hash FROM chunks c JOIN documents d ON c.workspace=d.workspace AND c.document=d.id WHERE c.workspace=? AND c.id=?",
                (wid, cid),
            ).fetchone()
        if not row:
            raise RagError("chunk_not_found", 404)
        return dict(row)

    def search(
        self, principal: str, wid: str, query: str, limit: int = 5, rerank: bool = True
    ) -> dict:
        self.store.workspace(principal, wid)
        if not query.strip() or len(query) > 1000 or not 1 <= limit <= 10:
            raise RagError("invalid_query")
        with self.operation_lock:
            with self.store.connect() as db:
                chunks = [
                    dict(r)
                    for r in db.execute(
                        "SELECT c.*,d.filename,d.content_hash FROM chunks c JOIN documents d ON c.workspace=d.workspace AND c.document=d.id WHERE c.workspace=? ORDER BY c.id",
                        (wid,),
                    )
                ]
            if not chunks:
                return {"status": "no_match", "matches": []}
            dense = self.vectors.search(
                wid, self.embedder.encode([query])[0], sorted({c["document"] for c in chunks})
            )
            matches = rank(query, chunks, dense, rerank)[:limit]
            for m in matches:
                m.pop("text")
                m["citation"] = f"{wid}:{m['document']}:{m['id']}"
            return {"status": "matched" if matches else "no_match", "matches": matches}

    def delete_workspace(self, principal: str, wid: str, confirmation: str):
        self.store.owner(principal)
        self.store.workspace(principal, wid, deleting=True)
        if confirmation != wid:
            raise RagError("confirmation_mismatch")
        with self.operation_lock:
            with self.store.connect() as db:
                db.execute("UPDATE workspaces SET state='DELETING' WHERE id=?", (wid,))
                db.execute(
                    "UPDATE jobs SET state='CANCELLED',content=NULL WHERE workspace=? AND state IN ('QUEUED','RUNNING')",
                    (wid,),
                )
                self.store.audit(db, "workspace_delete_requested", wid)
            self.vectors.delete(wid)
            with self.store.connect() as db:
                db.execute("DELETE FROM chunks WHERE workspace=?", (wid,))
                db.execute("DELETE FROM documents WHERE workspace=?", (wid,))
                db.execute("UPDATE jobs SET content=NULL WHERE workspace=?", (wid,))
                db.execute("UPDATE workspaces SET state='DELETED' WHERE id=?", (wid,))
                self.store.audit(db, "workspace_deleted", wid)
