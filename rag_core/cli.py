import argparse
import json
import os
import stat
import sys
from pathlib import Path

import httpx

from .errors import RagError
from .settings import MAX_FILE, config_path, filename, initialize, load_settings


def read_local(path: Path) -> bytes:
    """CLI-only local import. No symlink component or non-regular input accepted."""
    path = path.absolute()
    for component in [*path.parents, path]:
        if component.is_symlink():
            raise RagError("unsafe_import_path")
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, "rb") as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode):
            raise RagError("regular_file_required")
        if info.st_size > MAX_FILE:
            raise RagError("file_size_limit", 413)
        data = stream.read(MAX_FILE + 1)
        if len(data) > MAX_FILE:
            raise RagError("file_size_limit", 413)
        return data


def parser():
    root = argparse.ArgumentParser(prog="rag")
    root.add_argument("--config", type=Path, default=config_path())
    root.add_argument(
        "--token-env", help="Read a workspace capability from this environment variable"
    )
    commands = root.add_subparsers(dest="command", required=True)
    config = commands.add_parser("config").add_subparsers(dest="action", required=True)
    config.add_parser("init").add_argument("--state-dir", type=Path, required=True)
    commands.add_parser("doctor")
    backup = commands.add_parser("backup").add_subparsers(dest="action", required=True)
    backup.add_parser("create").add_argument("--destination", type=Path, required=True)
    backup.add_parser("restore").add_argument("--source", type=Path, required=True)
    serve = commands.add_parser("serve")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", default=8000, type=int)
    workspace = commands.add_parser("workspace").add_subparsers(dest="action", required=True)
    workspace.add_parser("create").add_argument("slug")
    workspace.add_parser("list")
    delete = workspace.add_parser("delete")
    delete.add_argument("workspace")
    delete.add_argument("--confirm", required=True, help="Exact server-issued workspace ID")
    ingest = commands.add_parser("ingest")
    ingest.add_argument("workspace")
    ingest.add_argument("file", type=Path)
    job = commands.add_parser("job").add_subparsers(dest="action", required=True)
    for action in ("show", "cancel"):
        sub = job.add_parser(action)
        sub.add_argument("workspace")
        sub.add_argument("job")
    for name in ("search", "ask"):
        sub = commands.add_parser(name)
        sub.add_argument("workspace")
        sub.add_argument("query")
        sub.add_argument("--no-rerank", action="store_true")
    for name in ("documents", "events"):
        commands.add_parser(name).add_argument("workspace")
    return root


def execute(args):
    if args.command == "config":
        initialize(args.config, args.state_dir)
        return {"status": "initialized", "generation": "disabled"}
    settings = load_settings(args.config)
    if args.command == "backup":
        from . import backup

        if args.token_env:
            raise RagError("offline_owner_config_required", 403)
        return (
            backup.create(settings, args.destination)
            if args.action == "create"
            else backup.restore(settings, args.source)
        )
    if args.command == "serve":
        import uvicorn

        from .api import create_app

        # One worker only; access logs would disclose query-string filenames.
        uvicorn.run(
            create_app(settings),
            host=args.host,
            port=args.port,
            access_log=False,
            log_level="warning",
            limit_concurrency=32,
            timeout_keep_alive=5,
        )
        return None
    token = os.environ.get(args.token_env, "") if args.token_env else settings.owner_token
    if args.token_env and not token:
        raise RagError("capability_environment_missing")
    method, path, kwargs = "GET", "/workspaces", {}
    if args.command == "doctor":
        with httpx.Client(base_url=settings.api_url, timeout=10, trust_env=False) as client:
            response = client.get("/health")
            auth = client.get("/workspaces", headers={"Authorization": "Bearer " + token})
        if response.status_code != 200 or auth.status_code != 200:
            raise RagError("service_not_ready", 503)
        return {
            "status": "ready",
            "generation_enabled": settings.generation_enabled,
            "model_configured": settings.model_dir is not None,
        }
    if args.command == "workspace":
        if args.action == "create":
            method, kwargs = "POST", {"json": {"slug": args.slug}}
        elif args.action == "delete":
            method, path, kwargs = (
                "DELETE",
                f"/workspaces/{args.workspace}",
                {"params": {"confirm": args.confirm}},
            )
    else:
        from .settings import identifier

        identifier(args.workspace)
        base = f"/workspaces/{args.workspace}"
        if args.command == "ingest":
            name = filename(args.file.name)
            method, path = "POST", base + "/documents"
            kwargs = {
                "params": {"filename": name},
                "content": read_local(args.file),
                "headers": {"Content-Type": "application/octet-stream"},
            }
        elif args.command == "job":
            identifier(args.job)
            path = base + f"/jobs/{args.job}"
            if args.action == "cancel":
                method, path = "POST", path + "/cancel"
        elif args.command in {"search", "ask"}:
            method, path = "POST", base + "/" + args.command
            kwargs = {"json": {"query": args.query, "rerank": not args.no_rerank}}
        else:
            path = base + "/" + args.command
    headers = {"Authorization": "Bearer " + token, **kwargs.pop("headers", {})}
    with httpx.Client(
        base_url=settings.api_url, timeout=40, trust_env=False, follow_redirects=False
    ) as client:
        response = client.request(method, path, headers=headers, **kwargs)
    if response.is_error:
        # Never echo arbitrary proxy/provider bodies, credentials or server exceptions.
        allowed = response.json().get("error", "api_request_failed")
        if not isinstance(allowed, str) or not __import__("re").fullmatch(r"[a-z_]{1,64}", allowed):
            allowed = "api_request_failed"
        raise RagError(allowed, response.status_code)
    return response.json()


def main():
    os.umask(0o077)
    args = parser().parse_args()
    try:
        result = execute(args)
        if result is not None:
            print(json.dumps(result, indent=2))
    except RagError as exc:
        print(json.dumps({"error": exc.code}), file=sys.stderr)
        raise SystemExit(1) from None
    except (OSError, ValueError, httpx.HTTPError):
        print(json.dumps({"error": "local_or_network_error"}), file=sys.stderr)
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
