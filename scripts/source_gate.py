"""Exact tracked-file inventory gate; staged additions are included by git ls-files."""

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path, PurePosixPath

ROOT_FILES = {
    ".env.example",
    ".gitignore",
    ".dockerignore",
    "LICENSE",
    "NOTICE",
    "README.md",
    "SECURITY.md",
    "CONTRIBUTING.md",
    "Dockerfile",
    "Dockerfile.qdrant",
    "Dockerfile.ui",
    "docker-compose.yml",
    "docker-compose.ui.yml",
    "pyproject.toml",
    "uv.lock",
    "requirements.txt",
    "api_main.py",
    "main.py",
    "config.py",
    "app.py",
}
PREFIXES = ("rag_core/", "tests/", "scripts/", "docs/", "examples/", ".github/workflows/")
SUFFIXES = {".py", ".md", ".json", ".jsonl", ".yml", ".yaml", ".txt", ".xml", ".toml"}
FORBIDDEN = {
    ".local",
    ".env",
    ".venv",
    "uploads",
    "database",
    "qdrant_storage",
    "__pycache__",
    "node_modules",
    "models",
    ".git",
}


def inspect(name: str, data: bytes, *, symlink=False):
    parts = PurePosixPath(name).parts
    if symlink or not parts or any(p in FORBIDDEN or p in {"..", "."} for p in parts):
        raise ValueError("private path or symlink")
    if name not in ROOT_FILES and not (name.startswith(PREFIXES) and Path(name).suffix in SUFFIXES):
        raise ValueError("unapproved source artifact")
    if len(data) > 2_000_000 or b"\0" in data:
        raise ValueError("binary or oversized source artifact")
    if Path(name).suffix == ".json":

        def private_keys(value):
            if isinstance(value, dict):
                return any(
                    k in {"owner_token", "qdrant_key", "capability_hash"} or private_keys(v)
                    for k, v in value.items()
                )
            return isinstance(value, list) and any(private_keys(v) for v in value)

        if private_keys(json.loads(data)):
            raise ValueError("private configuration or database metadata")
    # Real credential patterns; detector history scan is a separate non-optional gate.
    if re.search(
        rb"(?:gsk_[A-Za-z0-9]{32,}|sk-(?:proj-)?[A-Za-z0-9_-]{32,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|AKIA[A-Z0-9]{16})",
        data,
    ):
        raise ValueError("credential pattern")
    if re.search(rb"(?:/home/[^/\s]+/(?:uploads|database|\.config)/|Bearer [0-9a-f]{64})", data):
        raise ValueError("private path or literal bearer")


def inventory(root: Path):
    files = subprocess.check_output(["git", "ls-files", "-z"], cwd=root).decode().split("\0")
    rows = []
    for name in filter(None, files):
        path = root / name
        data = path.read_bytes()
        inspect(name, data, symlink=path.is_symlink())
        rows.append({"path": name, "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)})
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    rows = inventory(root)
    # Never track this manifest inside itself: output belongs to ignored evidence staging.
    value = {
        "source_sha": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root)
        .decode()
        .strip(),
        "files": rows,
    }
    if args.output:
        args.output.write_text(json.dumps(value, indent=2) + "\n")
    print(f"Source inventory PASS: {len(rows)} exact tracked files")


if __name__ == "__main__":
    main()
