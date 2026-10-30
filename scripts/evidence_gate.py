"""Inspect only explicitly exported CI reports; never upload installation directories."""

import argparse
import hashlib
import json
from pathlib import Path

from source_gate import inspect

parser = argparse.ArgumentParser()
parser.add_argument("directory", type=Path)
args = parser.parse_args()
rows = []
for path in sorted(args.directory.iterdir()):
    if path.is_symlink() or not path.is_file():
        raise ValueError("non-regular CI artifact")
    if path.name == "checksums.json":
        continue
    data = path.read_bytes()
    if path.suffix == ".tar":
        # Source archive has its independent exact member/hash verifier.
        if path.name != "source.tar":
            raise ValueError("unapproved binary artifact")
    else:
        inspect("docs/release/evidence/" + path.name, data)
    rows.append({"path": path.name, "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)})
(args.directory / "checksums.json").write_text(json.dumps({"files": rows}, indent=2) + "\n")
print(f"Verified {len(rows)} allowlisted CI report artifacts")
