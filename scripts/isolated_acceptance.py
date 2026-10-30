"""ONE explicit local model campaign: real CPU image/Qdrant, crash/outage/restore.

Never run by CI or startup. Requires pre-acquired verified model; downloads nothing.
Only creates isolated Compose projects named spec001-<random>. No operator volumes.
"""

import argparse
import hashlib
import io
import json
import os
import re
import socket
import subprocess
import time
import uuid
import zipfile
from pathlib import Path

import httpx
from pypdf import PdfWriter
from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject

from rag_core.settings import initialize

ROOT = Path(__file__).resolve().parents[1]


def run(command, *, env=None, input=None):
    result = subprocess.run(command, env=env, input=input, capture_output=True, timeout=180)
    if result.returncode:
        diagnostics = ROOT / ".local" / "acceptance-subprocess.log"
        with diagnostics.open("ab") as output:
            output.write(result.stdout + b"\n" + result.stderr + b"\n")
        # No command/header/config text in public exceptions.
        raise RuntimeError("local acceptance subprocess failed; inspect private runner logs")
    return result.stdout.decode()


def wait(check, seconds=45):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        try:
            value = check()
            if value:
                return value
        except (httpx.HTTPError, AssertionError):
            pass
        time.sleep(0.15)
    raise RuntimeError("acceptance observation timeout; inspect the existing container handles")


def pdf_document():
    writer = PdfWriter()
    for text in [
        "Synthetic Cedar Orchard grows apples.",
        "The blue rainwater tank holds 240 liters.",
    ]:
        page = writer.add_blank_page(width=600, height=800)
        font = writer._add_object(
            DictionaryObject(
                {
                    NameObject("/Type"): NameObject("/Font"),
                    NameObject("/Subtype"): NameObject("/Type1"),
                    NameObject("/BaseFont"): NameObject("/Helvetica"),
                }
            )
        )
        page[NameObject("/Resources")] = DictionaryObject(
            {NameObject("/Font"): DictionaryObject({NameObject("/F1"): font})}
        )
        stream = DecodedStreamObject()
        stream.set_data(f"BT /F1 14 Tf 40 740 Td ({text}) Tj ET".encode())
        page[NameObject("/Contents")] = writer._add_object(stream)
    out = io.BytesIO()
    writer.write(out)
    return out.getvalue()


def docx_document():
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w") as archive:
        archive.writestr(
            "word/document.xml",
            '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>The synthetic Willow Library lends books for twenty-one days.</w:t></w:r></w:p></w:body></w:document>',
        )
    return out.getvalue()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--approved-local-model-test", action="store_true", required=True)
    parser.add_argument("--model-dir", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument(
        "--resume-project",
        help="Continue the same stopped disposable campaign after a verified terminal failure",
    )
    args = parser.parse_args()
    os.umask(0o077)
    if args.resume_project and not re.fullmatch(r"spec001-[0-9a-f]{10}", args.resume_project):
        parser.error("invalid disposable project ID")
    project = args.resume_project or "spec001-" + uuid.uuid4().hex[:10]
    root = ROOT / ".local" / project
    config = root / "config" / "config.json"
    if args.resume_project:
        handles = json.loads((root / "handles.json").read_text())
        port = handles["port"]
    else:
        root.mkdir(parents=True, mode=0o700)
        initialize(config, root / "state")
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            port = sock.getsockname()[1]
    settings = json.loads(config.read_text())
    settings.update(
        state_dir="/private/state", qdrant_url="http://qdrant:6333", model_dir="/private/model"
    )
    config.write_text(json.dumps(settings))
    env = {
        **os.environ,
        "RAG_PRIVATE_DIR": str(root),
        "RAG_MODEL_DIR": str(args.model_dir.resolve()),
        "RAG_UID": str(os.getuid()),
        "RAG_GID": str(os.getgid()),
        "RAG_PORT": str(port),
    }
    compose = ["docker", "compose", "-p", project, "-f", str(ROOT / "docker-compose.yml")]
    checks = []
    report = {
        "project": project,
        "source_sha": run(["git", "rev-parse", "HEAD"]).strip(),
        "model": json.loads((args.model_dir / "manifest.json").read_text()),
        "image_id": run(
            ["docker", "image", "inspect", "workspace-rag-core:local", "--format", "{{.Id}}"]
        ).strip(),
        "qdrant_image_id": run(
            ["docker", "image", "inspect", "workspace-rag-qdrant:local", "--format", "{{.Id}}"]
        ).strip(),
        "checks": checks,
    }
    if args.resume_project:
        previous = json.loads(args.evidence.read_text())
        if previous["project"] != project or previous["result"] != "FAIL":
            raise ValueError("resume requires the terminal failed report for this campaign")
        report["prior_attempts"] = previous.get("prior_attempts", []) + [
            {
                k: previous[k]
                for k in ("source_sha", "image_id", "checks", "result", "failure_class")
            }
        ]
    # Save live handles immediately, allowing authoritative inspection after interruption.
    (root / "handles.json").write_text(
        json.dumps({"project": project, "port": port, "compose": compose}, indent=2)
    )

    def cp(*args):
        return run(compose + list(args), env=env)

    def cli(*args, content=None):
        return json.loads(
            run(compose + ["exec", "-T", "api", "rag", *args], env=env, input=content)
        )

    def check(name, condition):
        assert condition, name
        checks.append({"name": name, "status": "PASS"})

    client = httpx.Client(
        base_url=f"http://127.0.0.1:{port}",
        timeout=12,
        trust_env=False,
        headers={"Authorization": "Bearer " + settings["owner_token"]},
    )

    def request(method, path, **kwargs):
        response = client.request(method, path, **kwargs)
        assert response.is_success, (method, path, response.status_code, response.text)
        return response.json()

    def terminal(wid, jid):
        value = request("GET", f"/workspaces/{wid}/jobs/{jid}")
        return value if value["state"] in {"COMPLETED", "FAILED", "CANCELLED"} else None

    restore_compose = None
    restore_env = None
    try:
        cp("up", "-d", "--no-build")
        wait(lambda: client.get("/health").status_code == 200)
        check(
            "actual image + private non-root Qdrant CPU readiness",
            cli("doctor")["status"] == "ready",
        )
        check(
            "anonymous API rejected",
            httpx.get(client.base_url.join("/workspaces"), trust_env=False).status_code == 401,
        )
        if args.resume_project:
            existing = {workspace["slug"]: workspace for workspace in cli("workspace", "list")}
            a = existing["orchard"]
            b = cli("workspace", "create", "library-" + uuid.uuid4().hex[:6])
        else:
            a, b = cli("workspace", "create", "orchard"), cli("workspace", "create", "library")
        wa, wb = a["id"], b["id"]
        check("CLI/API workspace parity", cli("workspace", "list") == request("GET", "/workspaces"))
        # Independent mask-weighted mean and normalization reference on actual model outputs.
        reference = """
import json,numpy as np
from rag_core.embedding import OnnxEmbedder
from rag_core.settings import load_settings
m=OnnxEmbedder(load_settings()); texts=['rainwater tank','The synthetic library lends paper books for twenty-one days.']
v=np.asarray(m.encode(texts)); single=np.asarray(m.encode([texts[0]]))[0]
t=m.tokenizer.encode_batch(texts); mask=np.asarray([x.attention_mask for x in t],dtype=np.int64)
x={'input_ids':np.asarray([x.ids for x in t],dtype=np.int64),'attention_mask':mask,'token_type_ids':np.asarray([x.type_ids for x in t],dtype=np.int64)}
h=m.session.run(None,{k:v for k,v in x.items() if k in {i.name for i in m.session.get_inputs()}})[0]
ref=np.einsum('bth,bt->bh',h,mask)/mask.sum(1)[:,None]; ref/=np.linalg.norm(ref,axis=1)[:,None]
assert np.max(np.abs(v-ref))<1e-5
assert np.max(np.abs(v[0]-single))<1e-5
assert np.max(np.abs(np.linalg.norm(v,axis=1)-1))<1e-5
print(json.dumps({'dimension':v.shape[1],'pooling':'mask-weighted-mean','normalization':'l2','reference_max_abs_error':float(np.max(np.abs(v-ref))),'providers':m.session.get_providers()}))
"""
        pooling = json.loads(cp("exec", "-T", "api", "python", "-c", reference))
        report["pooling"] = pooling
        check(
            "actual ONNX mask mean, L2, batch/single invariance",
            pooling["dimension"] == 384 and pooling["providers"] == ["CPUExecutionProvider"],
        )
        original = (ROOT / "examples/corpus/orchard.txt").read_bytes()
        first = cli("ingest", wa, "-", "--filename", "orchard.txt", content=original)
        check(
            "real TXT ingestion completes",
            wait(lambda: terminal(wa, first["id"]))["state"] == "COMPLETED",
        )
        pdf, docx = pdf_document(), docx_document()
        jobs = []
        for wid, name, content in [(wa, "orchard.pdf", pdf), (wb, "library.docx", docx)]:
            job = request(
                "POST",
                f"/workspaces/{wid}/documents",
                params={"filename": name},
                content=content,
                headers={"Content-Type": "application/octet-stream"},
            )
            jobs.append(job)
            check(
                "real " + name + " ingestion completes",
                wait(lambda wid=wid, jid=job["id"]: terminal(wid, jid))["state"] == "COMPLETED",
            )
        report["corpus_sha256"] = {
            name: hashlib.sha256(content).hexdigest()
            for name, content in [
                ("orchard.txt", original),
                ("orchard.pdf", pdf),
                ("library.docx", docx),
            ]
        }
        query = {"query": "What is the blue rainwater tank capacity?"}
        found = request("POST", f"/workspaces/{wa}/search", json=query)
        check(
            "actual dense + BM25 + rerank retrieves rainwater evidence",
            found["status"] == "matched"
            and any(
                m["ranking"]["dense_cosine"] is not None and m["ranking"]["bm25"] > 0
                for m in found["matches"]
            ),
        )
        check("CLI/API search parity", cli("search", wa, query["query"]) == found)
        check(
            "actual PDF page 2 provenance",
            any(
                m["filename"] == "orchard.pdf" and m["page"] == 2 and "240" in m["excerpt"]
                for m in found["matches"]
            ),
        )
        for match in found["matches"]:
            persisted = request("GET", f"/workspaces/{wa}/chunks/{match['id']}")
            check(
                "persisted authorized citation " + match["id"],
                match["excerpt"] == persisted["text"][:800]
                and match["citation"] == f"{wa}:{persisted['document']}:{persisted['id']}",
            )
        source = client.get(f"/workspaces/{wa}/documents/{first['document']}/content")
        check(
            "original source download hash",
            source.status_code == 200 and source.content == original,
        )
        repeated = cli("ingest", wa, "-", "--filename", "orchard.txt", content=original)
        check(
            "duplicate ingestion idempotent",
            repeated["id"] == first["id"]
            and len(request("GET", f"/workspaces/{wa}/documents")) == 2,
        )
        cap = {"Authorization": "Bearer " + b["capability"]}
        check(
            "cross-workspace search denied",
            client.post(f"/workspaces/{wa}/search", headers=cap, json=query).status_code == 404,
        )
        check(
            "cross-workspace deletion denied",
            client.delete(f"/workspaces/{wa}", params={"confirm": wa}, headers=cap).status_code
            == 403,
        )
        check(
            "no-match explicit on unrelated query",
            request("POST", f"/workspaces/{wa}/search", json={"query": "zxqv123987unmatchable"})[
                "status"
            ]
            == "no_match",
        )
        check(
            "generation remains disabled",
            client.post(f"/workspaces/{wa}/ask", json=query).json()
            == {"error": "generation_disabled"},
        )
        cp("restart", "api")
        wait(lambda: client.get("/health").status_code == 200)
        check(
            "API process restart preserves job and retrieval",
            cli("job", "show", wa, first["id"])["state"] == "COMPLETED"
            and request("POST", f"/workspaces/{wa}/search", json=query) == found,
        )
        cp("stop", "qdrant")
        check("real Qdrant outage readiness 503", client.get("/health").status_code == 503)
        check(
            "real Qdrant outage search 503",
            client.post(f"/workspaces/{wa}/search", json=query).status_code == 503,
        )
        cp("start", "qdrant")
        wait(lambda: client.get("/health").status_code == 200)
        check(
            "Qdrant restart preserves committed points",
            request("POST", f"/workspaces/{wa}/search", json=query) == found,
        )
        # Force an actual crash while a live worker awaits Qdrant, then recover durable job.
        qid, aid = cp("ps", "-q", "qdrant").strip(), cp("ps", "-q", "api").strip()
        run(["docker", "update", "--restart=no", aid])
        run(["docker", "pause", qid])
        crash = request(
            "POST",
            f"/workspaces/{wa}/documents",
            params={"filename": "recovery.txt"},
            content=b"Synthetic recovery document: citrus trees use stored rainwater.",
            headers={"Content-Type": "text/plain"},
        )
        wait(
            lambda: request("GET", f"/workspaces/{wa}/jobs/{crash['id']}")["state"] == "RUNNING",
            seconds=4,
        )
        run(["docker", "kill", "--signal=KILL", aid])
        run(["docker", "unpause", qid])
        run(["docker", "start", aid])
        wait(lambda: client.get("/health").status_code == 200)
        check(
            "actual RUNNING worker crash recovers without reset",
            wait(lambda: terminal(wa, crash["id"]))["state"] == "COMPLETED"
            and len(request("GET", f"/workspaces/{wa}/documents")) == 3,
        )
        expected_after_crash = request("POST", f"/workspaces/{wa}/search", json=query)
        cp("stop", "api")
        network = json.loads(run(["docker", "inspect", qid]))[0]["NetworkSettings"]["Networks"]
        network = next(iter(network))
        offline = [
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
        ]
        backed = json.loads(run(offline + ["backup", "create", "--destination", "/private/backup"]))
        check(
            "offline real Qdrant + SQLite consistent backup",
            backed["status"] == "backed_up" and backed["points"] >= 5,
        )
        # Restore into a second brand-new isolated installation, never original collections.
        restore_project = project + "-restore"
        restore_root = ROOT / ".local" / restore_project
        restore_root.mkdir(mode=0o700)
        initialize(restore_root / "config/config.json", restore_root / "state")
        restored = json.loads((restore_root / "config/config.json").read_text())
        restored.update(
            state_dir="/private/state", qdrant_url="http://qdrant:6333", model_dir="/private/model"
        )
        (restore_root / "config/config.json").write_text(json.dumps(restored))
        restore_env = {**env, "RAG_PRIVATE_DIR": str(restore_root)}
        restore_compose = [
            "docker",
            "compose",
            "-p",
            restore_project,
            "-f",
            str(ROOT / "docker-compose.yml"),
        ]
        run(restore_compose + ["up", "-d", "--no-build", "qdrant"], env=restore_env)
        rqid = run(restore_compose + ["ps", "-q", "qdrant"], env=restore_env).strip()
        wait(
            lambda: json.loads(run(["docker", "inspect", rqid]))[0]["State"]["Health"]["Status"]
            == "healthy"
        )
        rnetwork = next(
            iter(json.loads(run(["docker", "inspect", rqid]))[0]["NetworkSettings"]["Networks"])
        )
        restored_result = json.loads(
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
                    f"{restore_root}:/private",
                    "-v",
                    f"{root / 'backup'}:/restore-source:ro",
                    "workspace-rag-core:local",
                    "backup",
                    "restore",
                    "--source",
                    "/restore-source",
                ]
            )
        )
        check(
            "restore to empty independent Qdrant acknowledged",
            restored_result["points"] == backed["points"],
        )
        run(restore_compose + ["up", "-d", "--no-build", "api"], env=restore_env)
        client.headers["Authorization"] = "Bearer " + restored["owner_token"]
        wait(lambda: client.get("/health").status_code == 200)
        check(
            "restored source/manifests/ranking/job history intact",
            request("POST", f"/workspaces/{wa}/search", json=query) == expected_after_crash
            and request("GET", f"/workspaces/{wa}/jobs/{first['id']}")["state"] == "COMPLETED"
            and client.get(f"/workspaces/{wa}/documents/{first['document']}/content").content
            == original,
        )
        check(
            "restored workspace capability remains scoped",
            client.get(
                f"/workspaces/{wa}/documents",
                headers={"Authorization": "Bearer " + b["capability"]},
            ).status_code
            == 404,
        )
        report["result"] = "PASS"
    except BaseException as exc:
        report["result"] = "FAIL"
        report["failure_class"] = type(exc).__name__
        raise
    finally:
        # Keep local private state/volumes for audit; stop only these known projects.
        try:
            cp("stop")
            if restore_compose:
                run(restore_compose + ["stop"], env=restore_env)
        finally:
            client.close()
            args.evidence.write_text(json.dumps(report, indent=2) + "\n")
            print(
                json.dumps(
                    {"result": report.get("result"), "checks": len(checks), "project": project}
                )
            )


if __name__ == "__main__":
    main()
