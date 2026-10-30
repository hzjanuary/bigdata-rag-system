"""Explicit acquisition: official pinned repo, fixed sizes/hashes and a wall deadline."""

import argparse
import hashlib
import json
import os
import signal
from pathlib import Path
from urllib.request import urlopen

from rag_core.embedding import ONNX_SHA256, VOCAB_GIT_OBJECT
from rag_core.settings import MODEL_ID, MODEL_REVISION

FILES = ("onnx/model.onnx", "tokenizer.json")
SIZES = {"onnx/model.onnx": 90_405_214, "tokenizer.json": 466_247}
VOCAB_SHA256 = "be50c3628f2bf5bb5e3a7f17b1f74611b2561a3a27eeab05e5aa30f411572037"


def validate_metadata(metadata):
    if (
        metadata.get("sha") != MODEL_REVISION
        or metadata.get("cardData", {}).get("license") != "apache-2.0"
    ):
        raise ValueError("model_revision_or_license_mismatch")
    files = {entry["rfilename"]: entry for entry in metadata["siblings"]}
    for name in FILES:
        if files.get(name, {}).get("size") != SIZES[name]:
            raise ValueError("model_file_size_mismatch")
    if files[FILES[0]].get("lfs", {}).get("sha256") != ONNX_SHA256:
        raise ValueError("model_upstream_digest_mismatch")
    if files[FILES[1]].get("blobId") != VOCAB_GIT_OBJECT:
        raise ValueError("vocabulary_upstream_object_mismatch")
    return files


def verify_file(name, content, entry):
    digest = hashlib.sha256(content).hexdigest()
    expected = ONNX_SHA256 if name == FILES[0] else VOCAB_SHA256
    if len(content) != SIZES[name] or digest != expected:
        raise ValueError("download_integrity_error")
    if name == FILES[1]:
        blob = b"blob " + str(len(content)).encode() + b"\0" + content
        if hashlib.sha1(blob).hexdigest() != entry["blobId"]:
            raise ValueError("download_git_object_mismatch")
    return digest


def deadline(_signum, _frame):
    raise TimeoutError("model_acquisition_deadline")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--accept-license-and-download", action="store_true", required=True)
    parser.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args()
    if args.destination.exists() or args.destination.is_symlink():
        parser.error("destination must not exist")
    for parent in args.destination.absolute().parents:
        if parent.is_symlink():
            parser.error("symlink destination component")
    os.umask(0o077)
    previous = signal.signal(signal.SIGALRM, deadline)
    signal.alarm(180)
    try:
        api = f"https://huggingface.co/api/models/{MODEL_ID}/revision/{MODEL_REVISION}?blobs=true"
        with urlopen(api, timeout=20) as response:
            metadata = json.loads(response.read(2_000_001))
        files = validate_metadata(metadata)
        args.destination.mkdir(parents=True, mode=0o700)
        manifest = {
            "model_id": MODEL_ID,
            "revision": MODEL_REVISION,
            "license": "Apache-2.0",
            "files": {},
        }
        for name in FILES:
            target = args.destination / name
            target.parent.mkdir(exist_ok=True, mode=0o700)
            with urlopen(
                f"https://huggingface.co/{MODEL_ID}/resolve/{MODEL_REVISION}/{name}", timeout=20
            ) as response:
                with target.open("xb") as output:
                    size = 0
                    while chunk := response.read(1024 * 1024):
                        size += len(chunk)
                        if size > SIZES[name]:
                            raise ValueError("download_size_limit")
                        output.write(chunk)
            digest = verify_file(name, target.read_bytes(), files[name])
            manifest["files"][name] = {
                "sha256": digest,
                "size": size,
                "git_blob": files[name]["blobId"],
            }
        (args.destination / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
        print(json.dumps(manifest, indent=2))
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, previous)


if __name__ == "__main__":
    main()
