"""Explicit operator action only; official pinned repo, verify Git/LFS integrity."""

import argparse
import hashlib
import json
import os
from pathlib import Path
from urllib.request import urlopen

from rag_core.settings import MODEL_ID, MODEL_REVISION

FILES = ["onnx/model.onnx", "tokenizer.json"]
EXPECTED_ONNX = "6fd5d72fe4589f189f8ebc006442dbb529bb7ce38f8082112682524616046452"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--accept-license-and-download", action="store_true", required=True)
    parser.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args()
    if args.destination.exists() or args.destination.is_symlink():
        parser.error("destination must not exist")
    os.umask(0o077)
    api = f"https://huggingface.co/api/models/{MODEL_ID}/revision/{MODEL_REVISION}?blobs=true"
    with urlopen(api, timeout=30) as response:
        metadata = json.load(response)
    assert metadata["sha"] == MODEL_REVISION
    assert metadata["cardData"]["license"] == "apache-2.0"
    args.destination.mkdir(parents=True, mode=0o700)
    files = {entry["rfilename"]: entry for entry in metadata["siblings"]}
    manifest = {
        "model_id": MODEL_ID,
        "revision": MODEL_REVISION,
        "license": "Apache-2.0",
        "files": {},
    }
    for name in FILES:
        entry = files[name]
        target = args.destination / name
        target.parent.mkdir(exist_ok=True, mode=0o700)
        with urlopen(
            f"https://huggingface.co/{MODEL_ID}/resolve/{MODEL_REVISION}/{name}", timeout=60
        ) as response:
            with target.open("xb") as output:
                size = 0
                while chunk := response.read(1024 * 1024):
                    size += len(chunk)
                    if size > entry["size"]:
                        raise RuntimeError("download exceeds declared size")
                    output.write(chunk)
        content = target.read_bytes()
        digest = hashlib.sha256(content).hexdigest()
        assert len(content) == entry["size"]
        if "lfs" in entry:
            assert digest == entry["lfs"]["sha256"] == EXPECTED_ONNX
        else:
            git_blob = b"blob " + str(len(content)).encode() + b"\0" + content
            assert hashlib.sha1(git_blob).hexdigest() == entry["blobId"]  # Git object verification
        manifest["files"][name] = {
            "sha256": digest,
            "size": len(content),
            "git_blob": entry["blobId"],
        }
    (args.destination / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
