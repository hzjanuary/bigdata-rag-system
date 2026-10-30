"""Compare every source archive member with the exact tracked-file manifest."""

import argparse
import hashlib
import json
import tarfile
from pathlib import Path

from source_gate import inspect

parser = argparse.ArgumentParser()
parser.add_argument("archive", type=Path)
parser.add_argument("manifest", type=Path)
args = parser.parse_args()
manifest = json.loads(args.manifest.read_text())
expected = {f["path"]: f["sha256"] for f in manifest["files"]}
seen = set()
with tarfile.open(args.archive) as archive:
    for member in archive:
        if member.isdir():
            continue
        if not member.isfile() or member.name in seen or member.name not in expected:
            raise ValueError("unexpected source archive entry")
        data = archive.extractfile(member).read()
        inspect(member.name, data)
        if hashlib.sha256(data).hexdigest() != expected[member.name]:
            raise ValueError("source archive hash mismatch")
        seen.add(member.name)
if seen != set(expected):
    raise ValueError("source archive file set mismatch")
print(
    json.dumps(
        {
            "result": "PASS",
            "source_sha": manifest["source_sha"],
            "files": len(seen),
            "archive_sha256": hashlib.sha256(args.archive.read_bytes()).hexdigest(),
        }
    )
)
