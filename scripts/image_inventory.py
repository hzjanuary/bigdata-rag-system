"""Verify image payload exclusions, non-root identity, locked runtime and no model cache."""

import argparse
import json
import subprocess
import tomllib
from pathlib import Path

from packaging.requirements import Requirement
from packaging.utils import canonicalize_name

parser = argparse.ArgumentParser()
parser.add_argument("image")
args = parser.parse_args()
info = json.loads(subprocess.check_output(["docker", "image", "inspect", args.image]))[0]
assert info["Config"]["User"] == "10001:10001"
script = """
import importlib.metadata as m,json,pathlib,os
assert os.getuid()==10001
for root in ('/app','/private','/opt/venv'):
 for p in pathlib.Path(root).rglob('*'):
  assert p.name not in {'.env','config.json','metadata.sqlite3','tokenizer.json','model.onnx'}
  assert p.suffix not in {'.safetensors','.onnx','.sqlite3'}
assert not pathlib.Path('/usr/bin/gcc').exists()
assert not pathlib.Path('/usr/bin/git').exists()
assert not pathlib.Path('/usr/local/lib/python3.12/site-packages/pip').exists()
assert not pathlib.Path('/usr/local/lib/python3.12/ensurepip').exists()
print(json.dumps(sorted([{'name':d.metadata['Name'],'version':d.version} for d in m.distributions()],key=lambda x:x['name'].lower())))
"""
output = subprocess.check_output(
    [
        "docker",
        "run",
        "--rm",
        "--network",
        "none",
        "--read-only",
        "--cap-drop",
        "ALL",
        "--security-opt",
        "no-new-privileges",
        "--entrypoint",
        "python",
        args.image,
        "-c",
        script,
    ]
)
packages = json.loads(output)
root = Path(__file__).resolve().parents[1]
expected = {}
for line in (root / "requirements.txt").read_text().splitlines():
    if not line or line.startswith(("#", " ", "--")):
        continue
    requirement = Requirement(line.rstrip(" \\"))
    if requirement.marker is None or requirement.marker.evaluate():
        expected[canonicalize_name(requirement.name)] = next(iter(requirement.specifier)).version
project = tomllib.loads((root / "pyproject.toml").read_text())["project"]
expected[canonicalize_name(project["name"])] = project["version"]
actual = {canonicalize_name(p["name"]): p["version"] for p in packages}
if actual != expected:
    raise ValueError("image distributions do not match locked runtime requirements")
print(
    json.dumps(
        {
            "image_id": info["Id"],
            "source_revision": info["Config"]["Labels"].get("org.opencontainers.image.revision"),
            "size": info["Size"],
            "packages": packages,
            "locked_runtime": "PASS",
            "inventory": "PASS",
        },
        indent=2,
    )
)
