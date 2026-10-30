"""Record a bounded public runner environment; never dump environment variables."""

import json
import os
import platform
import subprocess
from pathlib import Path

out = Path(".local/ci-evidence")
out.mkdir(parents=True, exist_ok=True)
value = {
    "source_sha": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
    "os_release": Path("/etc/os-release").read_text(),
    "kernel": platform.release(),
    "python": platform.python_version(),
    "docker_server": subprocess.check_output(
        ["docker", "version", "--format", "{{.Server.Version}}"], text=True
    ).strip(),
    "github_hosted": os.environ.get("GITHUB_ACTIONS") == "true"
    and os.environ.get("RUNNER_ENVIRONMENT") == "github-hosted",
    "runner": {
        name: os.environ.get(name)
        for name in [
            "RUNNER_OS",
            "RUNNER_ARCH",
            "RUNNER_ENVIRONMENT",
            "ImageOS",
            "ImageVersion",
            "GITHUB_RUN_ID",
            "GITHUB_RUN_ATTEMPT",
            "GITHUB_EVENT_NAME",
        ]
    },
}
(out / "environment.json").write_text(json.dumps(value, indent=2) + "\n")
print(json.dumps(value))
