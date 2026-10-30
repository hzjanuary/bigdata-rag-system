"""Finish the SAME approved campaign after a terminal read-only restore failure.

Uses retained original/restore projects and a new backup destination. No downloads,
new corpus/model, collection resets, overwrites or provider calls.
"""

import argparse
import hashlib
import json
import math
import os
import re
import sqlite3
import uuid

import httpx
from isolated_acceptance import ROOT, run, wait


def equivalent_search(left, right):
    if left["status"] != right["status"] or len(left["matches"]) != len(right["matches"]):
        return False
    for old, new in zip(left["matches"], right["matches"], strict=True):
        old, new = dict(old), dict(new)
        a, b = old.pop("ranking"), new.pop("ranking")
        if old != new or a.keys() != b.keys():
            return False
        for key in a:
            if isinstance(a[key], float) and isinstance(b[key], float):
                if not math.isclose(a[key], b[key], rel_tol=1e-6, abs_tol=1e-6):
                    return False
            elif a[key] != b[key]:
                return False
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--approved-local-model-test", action="store_true", required=True)
    parser.add_argument("--project", required=True)
    parser.add_argument("--model-dir", required=True)
    parser.add_argument("--evidence", type=__import__("pathlib").Path, required=True)
    args = parser.parse_args()
    if not re.fullmatch(r"spec001-[0-9a-f]{10}", args.project):
        parser.error("invalid disposable project")
    os.umask(0o077)
    previous = json.loads(args.evidence.read_text())
    if (
        previous["project"] != args.project
        or previous["result"] != "FAIL"
        or not any(
            c["name"] == "offline real Qdrant + SQLite consistent backup"
            for c in previous["checks"]
        )
    ):
        raise ValueError("requires the verified terminal restore failure for this campaign")
    root = ROOT / ".local" / args.project
    restored_root = ROOT / ".local" / (args.project + "-restore")
    settings = json.loads((root / "config/config.json").read_text())
    restored_settings = json.loads((restored_root / "config/config.json").read_text())
    port = json.loads((root / "handles.json").read_text())["port"]
    env = {
        **os.environ,
        "RAG_PRIVATE_DIR": str(root),
        "RAG_MODEL_DIR": str(__import__("pathlib").Path(args.model_dir).resolve()),
        "RAG_UID": str(os.getuid()),
        "RAG_GID": str(os.getgid()),
        "RAG_PORT": str(port),
    }
    restored_env = {**env, "RAG_PRIVATE_DIR": str(restored_root)}
    compose = ["docker", "compose", "-p", args.project, "-f", str(ROOT / "docker-compose.yml")]
    restore_compose = [
        "docker",
        "compose",
        "-p",
        args.project + "-restore",
        "-f",
        str(ROOT / "docker-compose.yml"),
    ]
    source = run(["git", "rev-parse", "HEAD"]).strip()
    image = run(
        ["docker", "image", "inspect", "workspace-rag-core:local", "--format", "{{.Id}}"]
    ).strip()
    report = dict(previous)
    report["prior_attempts"] = previous.get("prior_attempts", []) + [
        {k: previous[k] for k in ("source_sha", "image_id", "checks", "result", "failure_class")}
    ]
    report["source_sha"], report["image_id"] = source, image
    report["checks"] = [
        {**c, "tested_source_sha": previous["source_sha"], "tested_image_id": previous["image_id"]}
        for c in previous["checks"]
    ]
    report.pop("failure_class", None)
    report["resume_method"] = "same retained projects; new uniquely named backup; no reingest/reset"
    client = httpx.Client(
        base_url=f"http://127.0.0.1:{port}",
        headers={"Authorization": "Bearer " + settings["owner_token"]},
        timeout=15,
        trust_env=False,
    )

    def check(name, condition):
        assert condition, name
        report["checks"].append(
            {"name": name, "status": "PASS", "tested_source_sha": source, "tested_image_id": image}
        )

    def get(method, path, **kwargs):
        response = client.request(method, path, **kwargs)
        assert response.is_success, response.status_code
        return response.json()

    def cp(command, restored=False):
        return run(
            (restore_compose if restored else compose) + command,
            env=restored_env if restored else env,
        )

    try:
        cp(["up", "-d", "--no-build"])
        wait(lambda: client.get("/health").status_code == 200)
        spaces = get("GET", "/workspaces")
        wid = next(w["id"] for w in spaces if w["slug"] == "orchard")
        query = {"query": "What is the blue rainwater tank capacity?"}
        expected = get("POST", f"/workspaces/{wid}/search", json=query)
        with sqlite3.connect(f"file:{root / 'state/metadata.sqlite3'}?mode=ro", uri=True) as db:
            first = db.execute(
                "SELECT id,document FROM jobs WHERE workspace=? AND filename='orchard.txt' AND state='COMPLETED' ORDER BY created LIMIT 1",
                (wid,),
            ).fetchone()
            history = db.execute("SELECT id,state,checkpoint FROM jobs ORDER BY id").fetchall()
        check(
            "final image reads retained real corpus and citations",
            expected["status"] == "matched"
            and any(m["page"] == 2 and "240" in m["excerpt"] for m in expected["matches"]),
        )
        # This new EMPTY workspace supplies a known capability for a live restore-ACL check.
        capability = get(
            "POST", "/workspaces", json={"slug": "restore-cap-" + uuid.uuid4().hex[:6]}
        )
        cp(["stop", "api"])
        qid = cp(["ps", "-q", "qdrant"]).strip()
        network = next(
            iter(json.loads(run(["docker", "inspect", qid]))[0]["NetworkSettings"]["Networks"])
        )
        backup_name = "backup-retry-" + uuid.uuid4().hex[:8]
        result = json.loads(
            run(
                [
                    "docker",
                    "run",
                    "--rm",
                    "--network",
                    network,
                    "--user",
                    f"{os.getuid()}:{os.getgid()}",
                    "-v",
                    f"{root}:/private",
                    "workspace-rag-core:local",
                    "backup",
                    "create",
                    "--destination",
                    "/private/" + backup_name,
                ]
            )
        )
        check(
            "standalone SQLite snapshot and acknowledged vector backup",
            result["status"] == "backed_up" and result["points"] == 5,
        )
        snapshot = root / backup_name
        with sqlite3.connect(
            (snapshot / "metadata.sqlite3").as_uri() + "?mode=ro&immutable=1", uri=True
        ) as db:
            check(
                "snapshot needs no WAL or SHM on a read-only mount",
                db.execute("PRAGMA journal_mode").fetchone()[0] == "delete",
            )
        cp(["up", "-d", "--no-build", "qdrant"], restored=True)
        rid = cp(["ps", "-q", "qdrant"], restored=True).strip()
        wait(
            lambda: json.loads(run(["docker", "inspect", rid]))[0]["State"]["Health"]["Status"]
            == "healthy"
        )
        rnetwork = next(
            iter(json.loads(run(["docker", "inspect", rid]))[0]["NetworkSettings"]["Networks"])
        )
        restored = json.loads(
            run(
                [
                    "docker",
                    "run",
                    "--rm",
                    "--network",
                    rnetwork,
                    "--user",
                    f"{os.getuid()}:{os.getgid()}",
                    "-v",
                    f"{restored_root}:/private",
                    "-v",
                    f"{snapshot}:/restore-source:ro",
                    "workspace-rag-core:local",
                    "backup",
                    "restore",
                    "--source",
                    "/restore-source",
                ]
            )
        )
        check(
            "actual read-only restore into independent Qdrant acknowledged",
            restored["points"] == result["points"],
        )
        cp(["up", "-d", "--no-build", "api"], restored=True)
        client.headers["Authorization"] = "Bearer " + restored_settings["owner_token"]
        wait(lambda: client.get("/health").status_code == 200)
        observed = get("POST", f"/workspaces/{wid}/search", json=query)
        check(
            "restored ranking citations pages and excerpts agree (1e-6 float tolerance)",
            equivalent_search(expected, observed),
        )
        source_bytes = client.get(f"/workspaces/{wid}/documents/{first[1]}/content").content
        check(
            "restored original source hash exact",
            hashlib.sha256(source_bytes).hexdigest()
            == hashlib.sha256((ROOT / "examples/corpus/orchard.txt").read_bytes()).hexdigest(),
        )
        with sqlite3.connect(
            f"file:{restored_root / 'state/metadata.sqlite3'}?mode=ro", uri=True
        ) as db:
            check(
                "entire durable job history survived restore",
                db.execute("SELECT id,state,checkpoint FROM jobs ORDER BY id").fetchall()
                == history,
            )
        cap_headers = {"Authorization": "Bearer " + capability["capability"]}
        visible = client.get("/workspaces", headers=cap_headers)
        check(
            "pre-backup capability survives restore with exact scope",
            visible.status_code == 200 and [w["id"] for w in visible.json()] == [capability["id"]],
        )
        check(
            "restored capability cannot read another workspace",
            client.get(f"/workspaces/{wid}/documents", headers=cap_headers).status_code == 404,
        )
        # Complete the CLI's destructive management path on a new EMPTY trial workspace.
        trial = get("POST", "/workspaces", json={"slug": "delete-trial-" + uuid.uuid4().hex[:6]})
        deleted = json.loads(
            cp(
                [
                    "exec",
                    "-T",
                    "api",
                    "rag",
                    "workspace",
                    "delete",
                    trial["id"],
                    "--confirm",
                    trial["id"],
                ],
                restored=True,
            )
        )
        check(
            "actual CLI scoped confirmed deletion preserves corpus",
            deleted["status"] == "deleted" and len(get("GET", f"/workspaces/{wid}/documents")) == 3,
        )
        report["result"] = "PASS"
        report["backup_manifest_sha256"] = hashlib.sha256(
            (snapshot / "manifest.json").read_bytes()
        ).hexdigest()
    except BaseException as exc:
        report["result"], report["failure_class"] = "FAIL", type(exc).__name__
        raise
    finally:
        cp(["stop"])
        cp(["stop"], restored=True)
        client.close()
        args.evidence.write_text(json.dumps(report, indent=2) + "\n")
        print(
            json.dumps(
                {
                    "result": report["result"],
                    "checks": len(report["checks"]),
                    "project": args.project,
                }
            )
        )


if __name__ == "__main__":
    main()
