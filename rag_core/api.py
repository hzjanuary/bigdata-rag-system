import asyncio
import fcntl
import hashlib
import os
import threading
import time
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, ConfigDict, Field

from .errors import RagError
from .generation import Generator
from .service import Service
from .settings import MAX_FILE, Settings, load_settings


class WorkspaceInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    slug: str = Field(max_length=48)


class QueryInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str = Field(min_length=1, max_length=1000)
    limit: int = Field(default=5, ge=1, le=10)
    rerank: bool = True


def create_app(
    settings: Settings | None = None, *, service: Service | None = None, start_worker: bool = True
) -> FastAPI:
    settings = settings or load_settings()
    service = service or Service(settings)
    generator = Generator(settings)
    stop = threading.Event()

    @asynccontextmanager
    async def lifespan(app):
        os.umask(0o077)
        fd = os.open(
            settings.state_dir / "instance.lock", os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600
        )
        try:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                raise RagError("single_instance_required", 503) from None
            service.recover()

            def work():
                while not stop.is_set():
                    if not service.run_one():
                        stop.wait(0.2)

            worker = threading.Thread(target=work, name="rag-worker", daemon=False)
            if start_worker:
                worker.start()
            try:
                yield
            finally:
                stop.set()
                if start_worker:
                    await asyncio.to_thread(worker.join)
        finally:
            os.close(fd)

    app = FastAPI(
        title="Workspace RAG Core",
        version="0.1.0",
        lifespan=lifespan,
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
    app.state.service = service
    app.state.generator = generator
    rate_lock, windows = threading.Lock(), {}
    inflight = 0

    @app.middleware("http")
    async def boundary(request: Request, call_next):
        nonlocal inflight
        admitted = False
        try:
            with rate_lock:
                if inflight >= 16:
                    raise RagError("concurrency_limit", 429)
                inflight += 1
                admitted = True
            if request.url.path != "/health":
                header = request.headers.get("authorization", "")
                if not header.startswith("Bearer ") or len(header) > 256:
                    raise RagError("unauthorized", 401)
                token = header[7:]
                request.state.principal = service.store.authenticate(token)
                digest = hashlib.sha256(token.encode()).hexdigest()
                now = int(time.monotonic() // 60)
                with rate_lock:
                    if len(windows) > 128:
                        windows.clear()
                    minute, count = windows.get(digest, (now, 0))
                    count = count + 1 if minute == now else 1
                    windows[digest] = (now, count)
                if count > 120:
                    raise RagError("rate_limit", 429)
            content_length = request.headers.get("content-length")
            if content_length and (
                not content_length.isdecimal() or int(content_length) > MAX_FILE
            ):
                raise RagError("request_size_limit", 413)
            # Bound JSON bodies too, including chunked requests; raw upload is streamed in route.
            if request.method in {"POST", "PUT", "PATCH"} and not request.url.path.endswith(
                "/documents"
            ):
                data = bytearray()
                async with asyncio.timeout(20):
                    async for part in request.stream():
                        if len(data) + len(part) > 16_384:
                            raise RagError("request_size_limit", 413)
                        data.extend(part)
                request._body = bytes(data)
            return await call_next(request)
        except RagError as exc:
            return JSONResponse({"error": exc.code}, status_code=exc.status)
        except TimeoutError:
            return JSONResponse({"error": "request_timeout"}, status_code=408)
        except Exception:
            return JSONResponse({"error": "internal_error"}, status_code=500)
        finally:
            if admitted:
                with rate_lock:
                    inflight -= 1

    @app.exception_handler(RagError)
    async def domain_error(request, exc):
        return JSONResponse({"error": exc.code}, status_code=exc.status)

    @app.exception_handler(RequestValidationError)
    async def validation_error(request, exc):
        return JSONResponse({"error": "invalid_request"}, status_code=422)

    def principal(request: Request) -> str:
        return request.state.principal

    @app.get("/health")
    def health():
        ready = service.vectors.ready()
        return JSONResponse(
            {"status": "ready" if ready else "unavailable"}, status_code=200 if ready else 503
        )

    @app.get("/workspaces")
    def workspaces(p: str = Depends(principal)):
        return service.store.list_workspaces(p)

    @app.post("/workspaces", status_code=201)
    def create_workspace(body: WorkspaceInput, p: str = Depends(principal)):
        return service.store.create_workspace(p, body.slug)

    @app.delete("/workspaces/{wid}")
    def delete_workspace(wid: str, confirm: str, p: str = Depends(principal)):
        service.delete_workspace(p, wid, confirm)
        return {"status": "deleted"}

    @app.post("/workspaces/{wid}/documents", status_code=202)
    async def ingest(wid: str, request: Request, filename: str, p: str = Depends(principal)):
        from .settings import filename as validate_filename

        service.store.workspace(p, wid)
        validate_filename(filename)
        expected = {
            "txt": {"text/plain", "application/octet-stream"},
            "pdf": {"application/pdf", "application/octet-stream"},
            "docx": {
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "application/octet-stream",
            },
        }
        if (
            request.headers.get("content-type", "").split(";")[0]
            not in expected[filename.rsplit(".", 1)[1]]
        ):
            raise RagError("unsupported_mime", 415)
        data = bytearray()
        try:
            async with asyncio.timeout(20):
                async for chunk in request.stream():
                    if len(data) + len(chunk) > MAX_FILE:
                        raise RagError("file_size_limit", 413)
                    data.extend(chunk)
        except TimeoutError:
            raise RagError("request_timeout", 408) from None
        return await asyncio.to_thread(service.submit, p, wid, filename, bytes(data))

    @app.get("/workspaces/{wid}/documents")
    def documents(wid: str, p: str = Depends(principal)):
        return service.documents(p, wid)

    @app.get("/workspaces/{wid}/documents/{did}/content")
    def content(wid: str, did: str, p: str = Depends(principal)):
        from .settings import identifier

        service.store.workspace(p, wid)
        identifier(did)
        with service.store.connect() as db:
            row = db.execute(
                "SELECT content FROM documents WHERE workspace=? AND id=?", (wid, did)
            ).fetchone()
        if not row:
            raise RagError("document_not_found", 404)
        return Response(
            row[0],
            media_type="application/octet-stream",
            headers={"Content-Disposition": "attachment", "X-Content-Type-Options": "nosniff"},
        )

    @app.get("/workspaces/{wid}/chunks/{cid}")
    def chunk(wid: str, cid: str, p: str = Depends(principal)):
        return service.chunk(p, wid, cid)

    @app.get("/workspaces/{wid}/jobs/{jid}")
    def job(wid: str, jid: str, p: str = Depends(principal)):
        return service.job(p, wid, jid)

    @app.post("/workspaces/{wid}/jobs/{jid}/cancel")
    def cancel(wid: str, jid: str, p: str = Depends(principal)):
        return service.cancel(p, wid, jid)

    @app.post("/workspaces/{wid}/search")
    def search(wid: str, body: QueryInput, p: str = Depends(principal)):
        return service.search(p, wid, body.query, body.limit, body.rerank)

    @app.post("/workspaces/{wid}/ask")
    def ask(wid: str, body: QueryInput, p: str = Depends(principal)):
        service.store.workspace(p, wid)
        return generator.ask(service, p, wid, body.query)

    @app.get("/workspaces/{wid}/events")
    def events(wid: str, p: str = Depends(principal)):
        return service.store.events(p, wid)

    return app
