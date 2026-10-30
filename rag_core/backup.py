"""Offline, private, consistent backup; no operator volume deletion or automatic overwrite."""

import fcntl
import hashlib
import json
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

from qdrant_client import models

from .errors import RagError
from .settings import Settings, private_path
from .store import Store
from .vectors import Vectors, collection


@contextmanager
def offline(settings):
    fd = os.open(
        settings.state_dir / "instance.lock", os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600
    )
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise RagError("stop_api_before_backup_restore", 409) from None
        yield
    finally:
        os.close(fd)


def create(settings: Settings, destination: Path) -> dict:
    if destination.exists() or destination.is_symlink():
        raise RagError("backup_destination_exists")
    for part in destination.absolute().parents:
        if part.is_symlink():
            raise RagError("unsafe_private_path")
    with offline(settings):
        store, vectors = Store(settings), Vectors(settings)
        destination.mkdir(parents=True, mode=0o700)
        dbpath = destination / "metadata.sqlite3"
        with store.connect() as source:
            target = sqlite3.connect(dbpath)
            try:
                source.backup(target)
                # A portable standalone backup must not need WAL/SHM sidecars on
                # a read-only backup mount.
                target.execute("PRAGMA journal_mode=DELETE")
            finally:
                target.close()
        dbpath.chmod(0o600)
        count = 0
        with (destination / "vectors.jsonl").open("x") as out:
            for workspace in store.list_workspaces("owner"):
                wid = workspace["id"]
                with store.connect() as db:
                    committed = {
                        r[0] for r in db.execute("SELECT id FROM chunks WHERE workspace=?", (wid,))
                    }
                if not committed:
                    continue
                vectors.ensure(wid)
                offset, seen = None, set()
                while True:
                    points, offset = vectors.client.scroll(
                        collection(wid),
                        limit=64,
                        offset=offset,
                        with_vectors=True,
                        with_payload=True,
                    )
                    for p in points:
                        cid = str(p.id).replace("-", "")
                        if cid in committed:
                            out.write(
                                json.dumps(
                                    {
                                        "workspace": wid,
                                        "id": cid,
                                        "vector": p.vector,
                                        "payload": p.payload,
                                    }
                                )
                                + "\n"
                            )
                            seen.add(cid)
                            count += 1
                    if offset is None:
                        break
                if seen != committed:
                    raise RagError("backup_index_inconsistent", 409)
        (destination / "vectors.jsonl").chmod(0o600)
        manifest = {
            "format": 1,
            "index": settings.index_metadata,
            "points": count,
            "files": {
                name: hashlib.sha256((destination / name).read_bytes()).hexdigest()
                for name in ("metadata.sqlite3", "vectors.jsonl")
            },
        }
        (destination / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
        (destination / "manifest.json").chmod(0o600)
        return {"status": "backed_up", "points": count}


def restore(settings: Settings, source: Path) -> dict:
    private_path(source, directory=True)
    manifest = json.loads(private_path(source / "manifest.json").read_bytes())
    if manifest.get("format") != 1 or manifest.get("index") != settings.index_metadata:
        raise RagError("backup_version_mismatch")
    for name in ("metadata.sqlite3", "vectors.jsonl"):
        content = private_path(source / name).read_bytes()
        if hashlib.sha256(content).hexdigest() != manifest["files"].get(name):
            raise RagError("backup_integrity_error")
    with offline(settings):
        store, vectors = Store(settings), Vectors(settings)
        with store.connect() as db:
            if (
                db.execute("SELECT count(*) FROM workspaces").fetchone()[0]
                or db.execute("SELECT count(*) FROM jobs").fetchone()[0]
            ):
                raise RagError("restore_requires_empty_installation")
        backup_db = sqlite3.connect(
            (source / "metadata.sqlite3").absolute().as_uri() + "?mode=ro&immutable=1", uri=True
        )
        try:
            if backup_db.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                raise RagError("backup_integrity_error")
            workspaces = [
                r[0] for r in backup_db.execute("SELECT id FROM workspaces WHERE state='ACTIVE'")
            ]
            committed = {
                r[0]: r[1:] for r in backup_db.execute("SELECT id,workspace,document FROM chunks")
            }
            for wid in workspaces:
                if vectors.client.collection_exists(collection(wid)):
                    raise RagError("restore_collection_exists")
            points = [
                json.loads(line) for line in (source / "vectors.jsonl").read_text().splitlines()
            ]
            if len(points) != len(committed) or {p["id"] for p in points} != set(committed):
                raise RagError("backup_index_inconsistent")
            for p in points:
                if len(p["vector"]) != settings.dimension or tuple(committed[p["id"]]) != (
                    p["workspace"],
                    p["payload"]["document"],
                ):
                    raise RagError("backup_index_inconsistent")
            for wid in workspaces:
                subset = [p for p in points if p["workspace"] == wid]
                if not subset:
                    continue
                vectors.ensure(wid, create=True)
                for start in range(0, len(subset), 32):
                    vectors.client.upsert(
                        collection(wid),
                        points=[
                            models.PointStruct(id=p["id"], vector=p["vector"], payload=p["payload"])
                            for p in subset[start : start + 32]
                        ],
                        wait=True,
                    )
            # Publish restored metadata only after all acknowledged vectors exist.
            with store.connect() as target:
                backup_db.backup(target)
        finally:
            backup_db.close()
    return {"status": "restored", "points": len(points)}
