import hashlib
import hmac
import json
import os
import secrets
import sqlite3
import time
import uuid
from contextlib import contextmanager

from .errors import RagError
from .settings import Settings, identifier, private_path, slug

DDL = """
CREATE TABLE IF NOT EXISTS workspaces (
 id TEXT PRIMARY KEY, slug TEXT UNIQUE NOT NULL, capability_hash TEXT NOT NULL,
 metadata TEXT NOT NULL, state TEXT NOT NULL DEFAULT 'ACTIVE');
CREATE TABLE IF NOT EXISTS jobs (
 id TEXT PRIMARY KEY, workspace TEXT NOT NULL REFERENCES workspaces(id),
 document TEXT NOT NULL, filename TEXT NOT NULL, content BLOB,
 state TEXT NOT NULL, checkpoint TEXT NOT NULL, error TEXT,
 created REAL NOT NULL, updated REAL NOT NULL);
CREATE TABLE IF NOT EXISTS documents (
 id TEXT NOT NULL, workspace TEXT NOT NULL REFERENCES workspaces(id),
 filename TEXT NOT NULL, content_hash TEXT NOT NULL, content BLOB NOT NULL,
 PRIMARY KEY(workspace,id));
CREATE TABLE IF NOT EXISTS chunks (
 id TEXT PRIMARY KEY, workspace TEXT NOT NULL, document TEXT NOT NULL,
 page INTEGER, ordinal INTEGER NOT NULL, start INTEGER NOT NULL, end INTEGER NOT NULL,
 text TEXT NOT NULL, FOREIGN KEY(workspace,document) REFERENCES documents(workspace,id));
CREATE TABLE IF NOT EXISTS audit (
 seq INTEGER PRIMARY KEY, event TEXT NOT NULL, workspace TEXT, job TEXT, created REAL NOT NULL);
CREATE INDEX IF NOT EXISTS job_queue ON jobs(state,created);
CREATE INDEX IF NOT EXISTS chunk_scope ON chunks(workspace,document);
"""


def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


class Store:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.path = settings.state_dir / "metadata.sqlite3"
        private_path(settings.state_dir, directory=True)
        if not self.path.exists():
            fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o600)
            os.close(fd)
        private_path(self.path)
        for suffix in ("-wal", "-shm"):
            if (settings.state_dir / (self.path.name + suffix)).is_symlink():
                raise RagError("unsafe_private_path")
        with self.connect() as db:
            db.execute("PRAGMA journal_mode=WAL")
            db.executescript(DDL)

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        try:
            yield db
            db.commit()
        except BaseException:
            db.rollback()
            raise
        finally:
            db.close()

    def authenticate(self, token: str) -> str:
        if hmac.compare_digest(token, self.settings.owner_token):
            return "owner"
        digest = token_hash(token)
        with self.connect() as db:
            rows = db.execute(
                "SELECT id,capability_hash FROM workspaces WHERE state='ACTIVE'"
            ).fetchall()
        for row in rows:
            if hmac.compare_digest(digest, row["capability_hash"]):
                return row["id"]
        raise RagError("unauthorized", 401)

    def workspace(self, principal: str, wid: str, deleting: bool = False) -> dict:
        identifier(wid)
        if principal not in {"owner", wid}:
            raise RagError("workspace_not_found", 404)
        with self.connect() as db:
            row = db.execute("SELECT * FROM workspaces WHERE id=?", (wid,)).fetchone()
        if not row or (row["state"] != "ACTIVE" and not deleting):
            raise RagError("workspace_not_found", 404)
        if json.loads(row["metadata"]) != self.settings.index_metadata:
            raise RagError("index_version_mismatch", 409)
        return dict(row)

    def owner(self, principal: str):
        if principal != "owner":
            raise RagError("owner_required", 403)

    def create_workspace(self, principal: str, name: str) -> dict:
        self.owner(principal)
        slug(name)
        wid, capability = uuid.uuid4().hex, secrets.token_hex(32)
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            if db.execute("SELECT count(*) FROM workspaces").fetchone()[0] >= 64:
                raise RagError("workspace_limit", 429)
            try:
                db.execute(
                    "INSERT INTO workspaces(id,slug,capability_hash,metadata) VALUES(?,?,?,?)",
                    (wid, name, token_hash(capability), json.dumps(self.settings.index_metadata)),
                )
            except sqlite3.IntegrityError:
                raise RagError("slug_exists", 409) from None
            self.audit(db, "workspace_created", wid)
        return {
            "id": wid,
            "slug": name,
            "capability": capability,
            "index": self.settings.index_metadata,
        }

    def list_workspaces(self, principal: str) -> list[dict]:
        with self.connect() as db:
            rows = db.execute(
                "SELECT id,slug,state FROM workspaces WHERE state='ACTIVE' AND (?='owner' OR id=?) ORDER BY slug",
                (principal, principal),
            ).fetchall()
        return [dict(row) for row in rows]

    @staticmethod
    def audit(db, event: str, wid: str | None = None, job: str | None = None):
        db.execute(
            "INSERT INTO audit(event,workspace,job,created) VALUES(?,?,?,?)",
            (event, wid, job, time.time()),
        )

    def events(self, principal: str, wid: str) -> list[dict]:
        self.workspace(principal, wid)
        with self.connect() as db:
            return [
                dict(r)
                for r in db.execute(
                    "SELECT * FROM audit WHERE workspace=? ORDER BY seq DESC LIMIT 100", (wid,)
                )
            ]
