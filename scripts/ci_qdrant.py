"""Disposable actual Qdrant integration, with fixture vectors and no inference."""

import json
import os
import subprocess
import time
import uuid

import httpx


def run(*args, **kwargs):
    return subprocess.check_output(list(args), text=True, **kwargs).strip()


def main():
    name = "spec001-ci-" + uuid.uuid4().hex[:12]
    network = name + "-net"
    run("docker", "network", "create", network)
    cid = None
    try:
        cid = run(
            "docker",
            "run",
            "-d",
            "--rm",
            "--name",
            name,
            "--network",
            network,
            "--publish",
            "127.0.0.1::6333",
            "--read-only",
            "--cap-drop",
            "ALL",
            "--security-opt",
            "no-new-privileges",
            "--memory",
            "512m",
            "--cpus",
            "1",
            "--pids-limit",
            "128",
            "--tmpfs",
            "/qdrant/storage:uid=10001,gid=10001,mode=0700",
            "--tmpfs",
            "/qdrant/snapshots:uid=10001,gid=10001,mode=0700",
            "-e",
            "QDRANT__TELEMETRY_DISABLED=true",
            "workspace-rag-qdrant:local",
        )
        info = json.loads(run("docker", "inspect", cid))[0]
        port = info["NetworkSettings"]["Ports"]["6333/tcp"][0]["HostPort"]
        url = "http://127.0.0.1:" + port
        deadline = time.monotonic() + 45
        while True:
            try:
                if httpx.get(url + "/readyz", timeout=1, trust_env=False).status_code == 200:
                    break
            except httpx.HTTPError:
                pass
            if time.monotonic() > deadline:
                raise RuntimeError("inspect the existing disposable Qdrant container")
            time.sleep(0.2)
        subprocess.run(
            ["uv", "run", "pytest", "-q", "tests/test_qdrant_integration.py"],
            env={**os.environ, "RAG_TEST_QDRANT_URL": url, "RAG_TEST_QDRANT_ISOLATED": "yes"},
            check=True,
        )
    finally:
        if cid:
            subprocess.run(["docker", "stop", cid], check=True, stdout=subprocess.DEVNULL)
        subprocess.run(["docker", "network", "rm", network], check=True, stdout=subprocess.DEVNULL)


if __name__ == "__main__":
    main()
