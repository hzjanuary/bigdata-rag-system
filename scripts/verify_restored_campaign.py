"""Complete read verification of the SAME already-restored disposable campaign.

Use only after the report proves read-only restore was acknowledged. This phase
never reingests, repeats restore, resets collections, or acquires model files.
"""

import argparse
import hashlib
import json
import os
import re
import sqlite3
import uuid
from pathlib import Path

import httpx
from isolated_acceptance import ROOT, run, wait
from resume_restore_acceptance import equivalent_search


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--approved-local-model-test", action="store_true", required=True)
    parser.add_argument("--project", required=True)
    parser.add_argument("--model-dir", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    if not re.fullmatch(r"spec001-[0-9a-f]{10}", args.project):
        parser.error("invalid disposable project")
    os.umask(0o077)
    old = json.loads(args.evidence.read_text())
    if (
        old["project"] != args.project
        or old["result"] != "FAIL"
        or not any(
            c["name"] == "actual read-only restore into independent Qdrant acknowledged"
            for c in old["checks"]
        )
    ):
        raise ValueError("requires acknowledged restore and a terminal observation/startup failure")
    root, target = ROOT / ".local" / args.project, ROOT / ".local" / (args.project + "-restore")
    target_settings = json.loads((target / "config/config.json").read_text())
    port = json.loads((root / "handles.json").read_text())["port"]
    env = {
        **os.environ,
        "RAG_PRIVATE_DIR": str(root),
        "RAG_MODEL_DIR": str(args.model_dir.resolve()),
        "RAG_UID": str(os.getuid()),
        "RAG_GID": str(os.getgid()),
        "RAG_PORT": str(port),
    }
    target_env = {**env, "RAG_PRIVATE_DIR": str(target)}
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
    report = dict(old)
    report["source_sha"], report["image_id"] = source, image
    report["prior_attempts"] = old.get("prior_attempts", []) + [
        {k: old[k] for k in ("source_sha", "image_id", "checks", "result", "failure_class")}
    ]
    report.pop("failure_class", None)
    report["checks"] = list(old["checks"])
    client = httpx.Client(
        base_url=f"http://127.0.0.1:{port}",
        headers={"Authorization": "Bearer " + target_settings["owner_token"]},
        timeout=15,
        trust_env=False,
    )

    def check(name, condition):
        assert condition, name
        report["checks"].append(
            {"name": name, "status": "PASS", "tested_source_sha": source, "tested_image_id": image}
        )

    try:
        run(compose + ["up", "-d", "--no-build", "qdrant"], env=env)
        qid = run(compose + ["ps", "-q", "qdrant"], env=env).strip()
        wait(
            lambda: json.loads(run(["docker", "inspect", qid]))[0]["State"]["Health"]["Status"]
            == "healthy"
        )
        network = next(
            iter(json.loads(run(["docker", "inspect", qid]))[0]["NetworkSettings"]["Networks"])
        )
        with sqlite3.connect(f"file:{root / 'state/metadata.sqlite3'}?mode=ro", uri=True) as db:
            wid = db.execute("SELECT id FROM workspaces WHERE slug='orchard'").fetchone()[0]
            original_jobs = db.execute(
                "SELECT id,state,checkpoint FROM jobs ORDER BY id"
            ).fetchall()
            original_docs = db.execute(
                "SELECT workspace,id,content_hash FROM documents ORDER BY workspace,id"
            ).fetchall()
            original_spaces = db.execute(
                "SELECT id,capability_hash FROM workspaces ORDER BY id"
            ).fetchall()
            first = db.execute(
                "SELECT document FROM jobs WHERE filename='orchard.txt' AND state='COMPLETED' ORDER BY created LIMIT 1"
            ).fetchone()[0]
        query = "What is the blue rainwater tank capacity?"
        code = (
            'import json; from rag_core.settings import load_settings; from rag_core.service import Service; s=Service(load_settings()); print(json.dumps(s.search("owner",'
            + json.dumps(wid)
            + ","
            + json.dumps(query)
            + ")))"
        )
        expected = json.loads(
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
                    "-v",
                    f"{args.model_dir.resolve()}:/private/model:ro",
                    "--entrypoint",
                    "python",
                    "workspace-rag-core:local",
                    "-c",
                    code,
                ]
            )
        )
        run(restore_compose + ["up", "-d", "--no-build", "api"], env=target_env)
        wait(lambda: client.get("/health").status_code == 200)
        response = client.post(f"/workspaces/{wid}/search", json={"query": query})
        check(
            "restored hybrid ranking citations and excerpts agree (1e-6 float tolerance)",
            response.status_code == 200 and equivalent_search(expected, response.json()),
        )
        body = client.get(f"/workspaces/{wid}/documents/{first}/content")
        check(
            "restored original source hash exact",
            body.status_code == 200
            and hashlib.sha256(body.content).digest()
            == hashlib.sha256((ROOT / "examples/corpus/orchard.txt").read_bytes()).digest(),
        )
        with sqlite3.connect(f"file:{target / 'state/metadata.sqlite3'}?mode=ro", uri=True) as db:
            check(
                "all job states checkpoints manifests and capability hashes survive",
                db.execute("SELECT id,state,checkpoint FROM jobs ORDER BY id").fetchall()
                == original_jobs
                and db.execute(
                    "SELECT workspace,id,content_hash FROM documents ORDER BY workspace,id"
                ).fetchall()
                == original_docs
                and db.execute("SELECT id,capability_hash FROM workspaces ORDER BY id").fetchall()
                == original_spaces,
            )
        # The capability created before the successful backup is stored only in
        # its original report process; exact hash comparison above proves retention.
        cap_response = client.post(
            "/workspaces", json={"slug": "verify-cap-" + uuid.uuid4().hex[:6]}
        )
        assert cap_response.status_code == 201
        cap = cap_response.json()
        headers = {"Authorization": "Bearer " + cap["capability"]}
        visible = client.get("/workspaces", headers=headers)
        check(
            "post-restore capability has exact workspace scope",
            visible.status_code == 200
            and [w["id"] for w in visible.json()] == [cap["id"]]
            and client.get(f"/workspaces/{wid}/documents", headers=headers).status_code == 404,
        )
        deleted = json.loads(
            run(
                restore_compose
                + [
                    "exec",
                    "-T",
                    "api",
                    "rag",
                    "workspace",
                    "delete",
                    cap["id"],
                    "--confirm",
                    cap["id"],
                ],
                env=target_env,
            )
        )
        check(
            "actual CLI confirmed deletion preserves unrelated corpus",
            deleted["status"] == "deleted"
            and len(client.get(f"/workspaces/{wid}/documents").json()) == 3,
        )
        # Code attestation ties the earlier ingest evidence to the final core:
        # the indexing/retrieval/parser/model modules have identical bytes.
        relevant = [
            "service.py",
            "store.py",
            "parsers.py",
            "embedding.py",
            "vectors.py",
            "settings.py",
        ]
        previous_revision = (
            old["prior_attempts"][-1]["source_sha"]
            if old.get("prior_attempts")
            else old["source_sha"]
        )
        matches = {}
        for name in relevant:
            before = run(["git", "show", previous_revision + ":rag_core/" + name]).encode()
            now = (ROOT / "rag_core" / name).read_bytes()
            # run() strips a final newline; compare normalized final newline only.
            matches[name] = (
                hashlib.sha256(before.rstrip(b"\n")).hexdigest()
                == hashlib.sha256(now.rstrip(b"\n")).hexdigest()
            )
        check(
            "final ingest retrieval parser and model source matches tested modules",
            all(matches.values()),
        )
        report["module_attestation"] = {"compared_source": previous_revision, "matches": matches}
        report["result"] = "PASS"
    except BaseException as exc:
        report["result"], report["failure_class"] = "FAIL", type(exc).__name__
        raise
    finally:
        run(compose + ["stop"], env=env)
        run(restore_compose + ["stop"], env=target_env)
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
