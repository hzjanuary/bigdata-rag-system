"""Fail-closed operator approval/consumption policy; imports never acquire a model."""

import argparse
import datetime as dt
import hashlib
import io
import json
import os
import re
import stat
import subprocess
import tarfile
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from collections import Counter
from pathlib import Path

REPO = "hzjanuary/bigdata-rag-system"
OWNER = "hzjanuary"
BRANCH = "feat/spec-001-oss-rag-core"
WORKFLOW = ".github/workflows/spec001-cpu-once.yml"
CAMPAIGN = "spec001-pr1-cpu-qdrant-remediation-2"
MARKER = "spec001-cpu-pr1-remediation-2-consumed"
PREFIX = "cpuq2:"
WINDOW_START = dt.datetime(2026, 10, 30, 10, tzinfo=dt.UTC)
DEADLINE = dt.datetime(2026, 10, 31, tzinfo=dt.UTC)
SHA = re.compile(r"[0-9a-f]{40}")
MODEL = "sentence-transformers/all-MiniLM-L6-v2"
REVISION = "10dbd2f06a8baf40ad285b037edda610c1b9a57c"
ONNX = "6fd5d72fe4589f189f8ebc006442dbb529bb7ce38f8082112682524616046452"
DIRECTORY = Path(".local/ci-evidence")
RECEIPT = DIRECTORY / "consumption.json"


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def activation(event, env, checkout, now=None):
    """Validate local event before any API request or write."""
    pr = event.get("pull_request", {})
    head = pr.get("head", {})
    target = head.get("sha", "")
    clock = now or dt.datetime.now(dt.UTC)
    require(clock >= WINDOW_START, "approval_window_not_open")
    require(clock < DEADLINE, "approval_window_expired")
    require(env.get("GITHUB_EVENT_NAME") == "pull_request", "wrong_event")
    require(event.get("action") == "labeled", "wrong_action")
    require(env.get("GITHUB_RUN_ATTEMPT") == "1", "rerun_forbidden")
    require(env.get("GITHUB_RUN_ID", "").isdigit(), "missing_run_identity")
    require(env.get("GITHUB_REPOSITORY") == REPO, "wrong_repository")
    require(event.get("repository", {}).get("full_name") == REPO, "wrong_event_repository")
    require(event.get("repository", {}).get("owner", {}).get("login") == OWNER, "wrong_owner")
    require(event.get("number") == 1 and pr.get("number") == 1, "wrong_pr")
    require(head.get("repo", {}).get("full_name") == REPO, "fork_forbidden")
    require(head.get("ref") == BRANCH, "wrong_branch")
    require(pr.get("base", {}).get("ref") == "main", "wrong_base")
    require(env.get("GITHUB_ACTOR") == OWNER, "unapproved_actor")
    require(event.get("sender", {}).get("login") == OWNER, "unapproved_sender")
    require(bool(SHA.fullmatch(target)), "invalid_sha")
    require(event.get("label", {}).get("name") == PREFIX + target, "wrong_label_or_sha")
    require(checkout == target, "checkout_sha_mismatch")
    require(pr.get("state") == "open" and pr.get("draft") is True, "not_open_draft")
    return target


def current_pr(api, target):
    pr = api("/pulls/1")
    require(
        pr["number"] == 1
        and pr["state"] == "open"
        and pr["draft"] is True
        and pr["head"]["repo"]["full_name"] == REPO
        and pr["head"]["ref"] == BRANCH
        and pr["head"]["sha"] == target
        and pr["base"]["ref"] == "main"
        and PREFIX + target in [label["name"] for label in pr["labels"]],
        "current_pr_or_label_changed",
    )


def complete_list(api, path, key):
    """Bounded complete pagination; absent/truncated/inconsistent evidence rejects."""
    rows = []
    total = None
    for page in range(1, 11):
        result = api(path + ("&" if "?" in path else "?") + f"per_page=100&page={page}")
        count = result["total_count"]
        require(isinstance(count, int) and 0 <= count <= 1000, "unbounded_history")
        require(total is None or total == count, "history_changed_during_read")
        total = count
        batch = result[key]
        require(isinstance(batch, list), "invalid_history")
        rows.extend(batch)
        if len(rows) == total:
            require(len({row["id"] for row in rows}) == total, "duplicate_history")
            return rows
        require(batch and len(rows) < total, "incomplete_history")
    raise ValueError("incomplete_history")


OLD_RUN = 41029994294
OLD_SHA = "ba78e94d82b7972e96a9bae962cbb8ada73d6619"
OLD_CAMPAIGN = "spec001-pr1-cpu-qdrant-once"
OLD_MARKER = "spec001-cpu-pr1-consumed"
OLD_MARKER_ID = 123977248159
OLD_JOB_ID = 123977173196
OLD_ARTIFACT = 12966475279
OLD_ARTIFACT_DIGEST = "sha256:1caddf93d9ecb1616eac35cd925c6bff1bcdf89fbfe82607de3e3195d3fb5863"
OLD_FAILURE = b"AssertionError: API process restart preserves job and retrieval"


def verified_zip(content, digest):
    require("sha256:" + hashlib.sha256(content).hexdigest() == digest, "archive_digest_mismatch")
    with zipfile.ZipFile(io.BytesIO(content)) as archive:
        entries = archive.infolist()
        require(
            0 < len(entries) <= 50 and sum(e.file_size for e in entries) <= 10_000_000,
            "archive_budget",
        )
        require(
            all(
                e.file_size <= 2_000_000
                and re.fullmatch(r"[A-Za-z0-9_.-]+", e.filename)
                and e.filename not in {".", ".."}
                and not stat.S_ISLNK(e.external_attr >> 16)
                for e in entries
            ),
            "unsafe_archive_member",
        )
        require(len({e.filename for e in entries}) == len(entries), "duplicate_archive_member")
        require(archive.testzip() is None, "archive_crc_mismatch")
        files = {e.filename: archive.read(e.filename) for e in entries}
    rows = json.loads(files["checksums.json"])["files"]
    require(
        len(rows) == len(files) - 1
        and {r["path"] for r in rows} == set(files) - {"checksums.json"},
        "archive_manifest_mismatch",
    )
    for row in rows:
        data = files[row["path"]]
        require(
            row["bytes"] == len(data) and row["sha256"] == hashlib.sha256(data).hexdigest(),
            "archive_file_mismatch",
        )
    return files


def verify_known_failure(api):
    """Exactly one immutable, actually consumed prior attempt; never a broad waiver."""
    old = api(f"/actions/runs/{OLD_RUN}")
    require(
        old["id"] == OLD_RUN
        and old["head_sha"] == OLD_SHA
        and old["path"] == WORKFLOW
        and old["event"] == "pull_request"
        and old["run_attempt"] == 1
        and old["status"] == "completed"
        and old["conclusion"] == "failure"
        and old["actor"]["login"] == OWNER,
        "previous_run_inconsistent",
    )
    marker = api(f"/check-runs/{OLD_MARKER_ID}")
    require(
        marker["id"] == OLD_MARKER_ID
        and marker["name"] == OLD_MARKER
        and marker["head_sha"] == OLD_SHA
        and marker["external_id"] == OLD_CAMPAIGN + ":" + str(OLD_RUN)
        and marker["status"] == "completed"
        and marker["conclusion"] == "neutral"
        and marker["app"]["slug"] == "github-actions",
        "previous_marker_missing_or_inconsistent",
    )
    jobs = complete_list(api, f"/actions/runs/{OLD_RUN}/jobs?filter=all", "jobs")
    campaigns = [j for j in jobs if j["name"] == "campaign"]
    require(
        len(campaigns) == 1
        and campaigns[0]["id"] == OLD_JOB_ID
        and campaigns[0]["conclusion"] == "failure",
        "previous_attempt_history_inconsistent",
    )
    require(
        all(
            j["name"] in {"campaign", "configuration"}
            and (j["name"] == "campaign" or j["conclusion"] == "skipped")
            for j in jobs
        ),
        "unexpected_previous_job",
    )
    steps = campaigns[0]["steps"]
    expected = {
        "Fail-closed history and consumption reservation": "success",
        "Bounded official pinned model acquisition": "success",
        "ONE synthetic CPU embedding and Qdrant acceptance": "failure",
        "Export sanitized outcome and measured campaign time": "success",
    }
    require(
        all(
            any(s["name"] == n and s["conclusion"] == c for s in steps) for n, c in expected.items()
        ),
        "previous_failure_steps_missing",
    )
    require(
        [s["name"] for s in steps if s.get("conclusion") == "failure"]
        == ["ONE synthetic CPU embedding and Qdrant acceptance"],
        "unexpected_previous_failure",
    )
    artifact = api(f"/actions/artifacts/{OLD_ARTIFACT}")
    require(
        artifact["id"] == OLD_ARTIFACT
        and not artifact["expired"]
        and artifact["digest"] == OLD_ARTIFACT_DIGEST,
        "previous_artifact_missing_or_changed",
    )
    files = verified_zip(
        api.download(f"/actions/artifacts/{OLD_ARTIFACT}/zip", 2_000_000), OLD_ARTIFACT_DIGEST
    )
    receipt = json.loads(files["consumption.json"])
    require(
        receipt["campaign_id"] == OLD_CAMPAIGN
        and receipt["consumed"] is True
        and receipt["run_id"] == str(OLD_RUN)
        and receipt["source_sha"] == OLD_SHA
        and receipt["run_attempt"] == 1
        and receipt["marker_id"] == OLD_MARKER_ID
        and receipt["acquisition_outcome"] == "success"
        and receipt["acceptance_outcome"] == "failure"
        and receipt["execution"]["result"] == "FAIL"
        and receipt["execution"]["failure_class"] == "AssertionError"
        and receipt["verified_model"]["model_id"] == MODEL
        and receipt["verified_model"]["revision"] == REVISION
        and receipt["verified_model"]["files"]["onnx/model.onnx"]["sha256"] == ONNX,
        "previous_consumption_inconsistent",
    )
    logs = api.download(f"/actions/runs/{OLD_RUN}/logs", 2_000_000)
    with zipfile.ZipFile(io.BytesIO(logs)) as archive:
        require(
            len(archive.infolist()) <= 100
            and sum(e.file_size for e in archive.infolist()) <= 2_000_000,
            "previous_log_budget",
        )
        require(
            archive.testzip() is None
            and any(OLD_FAILURE in archive.read(e) for e in archive.infolist()),
            "previous_failure_logs_missing",
        )
    return {
        "run_id": OLD_RUN,
        "source_sha": OLD_SHA,
        "marker_id": OLD_MARKER_ID,
        "consumed": True,
        "result": "FAIL",
        "artifact_id": OLD_ARTIFACT,
        "artifact_digest": OLD_ARTIFACT_DIGEST,
        "logs_sha256": hashlib.sha256(logs).hexdigest(),
    }


def audit_history(api, current_run=None, target=None):
    require(current_run != str(OLD_RUN), "old_run_cannot_authorize_remediation")
    previous = verify_known_failure(api)
    anchor = api("/actions/runs/41006993655")
    require(
        anchor["head_sha"] == "11736f527612fc659a201b13e38d13c7278e1476"
        and anchor["status"] == "completed",
        "missing_history_anchor",
    )
    runs = []
    for filename in ("ci.yml", "spec001-cpu-once.yml"):
        items = complete_list(api, f"/actions/workflows/{filename}/runs", "workflow_runs")
        require(bool(items), "missing_workflow_history")
        runs.extend(items)
    require(
        sum(r["id"] == OLD_RUN for r in runs) == 1, "previous_run_missing_from_complete_history"
    )
    if current_run is not None:
        require(any(str(r["id"]) == current_run for r in runs), "missing_current_run")
    jobs_by_run = {}
    for run in runs:
        if run["id"] == OLD_RUN:
            require(
                run["head_sha"] == OLD_SHA
                and run["run_attempt"] == 1
                and run["status"] == "completed"
                and run["conclusion"] == "failure"
                and run["path"] == WORKFLOW,
                "previous_run_list_inconsistent",
            )
            continue  # The ONLY exception, after exact receipt/marker/jobs/log verification.
        if str(run["id"]) == current_run:
            require(
                run["run_attempt"] == 1 and run["head_sha"] == target and run["path"] == WORKFLOW,
                "current_run_mismatch",
            )
            continue
        jobs = complete_list(api, f"/actions/runs/{run['id']}/jobs?filter=all", "jobs")
        require(bool(jobs), "missing_job_evidence")
        jobs_by_run[run["id"]] = jobs
        for job in jobs:
            if job["name"] in {"campaign", "independent-cpu", "cpu", "reserve"}:
                require(
                    job.get("conclusion") == "skipped",
                    "unexpected_campaign_attempt_or_missing_consumption",
                )
        if run["path"] == WORKFLOW:
            require(any(j["name"] == "campaign" for j in jobs), "missing_campaign_job_evidence")
    old_marker_count = 0
    for sha in {r["head_sha"] for r in runs} | ({target} if target else set()):
        require(bool(SHA.fullmatch(sha)), "invalid_history_sha")
        require(
            not complete_list(
                api, f"/commits/{sha}/check-runs?filter=all&check_name={MARKER}", "check_runs"
            ),
            "remediation_campaign_already_consumed",
        )
        old = complete_list(
            api, f"/commits/{sha}/check-runs?filter=all&check_name={OLD_MARKER}", "check_runs"
        )
        require(
            all(sha == OLD_SHA and m["id"] == OLD_MARKER_ID for m in old), "unexpected_old_marker"
        )
        old_marker_count += len(old)
    require(old_marker_count == 1, "previous_marker_missing_from_history")
    return {"previous": previous, "runs": runs, "jobs": jobs_by_run}


def source_archive_proof(api, artifact, target):
    files = verified_zip(
        api.download(f"/actions/artifacts/{artifact['id']}/zip", 2_000_000), artifact["digest"]
    )
    manifest = json.loads(files["source-manifest.json"])
    attestation = json.loads(files["archive-verification.json"])
    digest = hashlib.sha256(files["source.tar"]).hexdigest()
    require(
        manifest["source_sha"] == target
        and attestation["source_sha"] == target
        and attestation["result"] == "PASS"
        and attestation["archive_sha256"] == digest,
        "source_archive_identity_mismatch",
    )
    expected = {r["path"]: r["sha256"] for r in manifest["files"]}
    seen = set()
    with tarfile.open(fileobj=io.BytesIO(files["source.tar"])) as archive:
        for member in archive:
            if member.isdir():
                continue
            require(
                member.isfile()
                and member.name not in seen
                and member.name in expected
                and member.size <= 2_000_000,
                "source_archive_member_mismatch",
            )
            require(
                hashlib.sha256(archive.extractfile(member).read()).hexdigest()
                == expected[member.name],
                "source_archive_file_mismatch",
            )
            seen.add(member.name)
    require(seen == set(expected), "source_archive_incomplete")
    return digest


def authorize(api, event, env, checkout, now=None):
    target = activation(event, env, checkout, now)
    current_pr(api, target)
    history = audit_history(api, env["GITHUB_RUN_ID"], target)
    proofs = []
    for run in history["runs"]:
        if run["head_sha"] != target or run["path"] != ".github/workflows/ci.yml":
            continue
        source = [
            j
            for j in history["jobs"][run["id"]]
            if j["name"] == "source" and j.get("conclusion") == "success"
        ]
        if not source:
            continue
        steps = source[0]["steps"]
        require(
            all(
                any(s["name"] == n and s["conclusion"] == "success" for s in steps)
                for n in ("Exact archive and historical secret gates", "Verify exported reports")
            )
            and any(
                "actions/upload-artifact@" in s["name"] and s["conclusion"] == "success"
                for s in steps
            ),
            "missing_source_export_evidence",
        )
        artifacts = complete_list(api, f"/actions/runs/{run['id']}/artifacts", "artifacts")
        for artifact in artifacts:
            if artifact["name"] == f"source-{run['id']}" and not artifact["expired"]:
                require(
                    bool(re.fullmatch(r"sha256:[0-9a-f]{64}", artifact["digest"])),
                    "missing_artifact_digest",
                )
                archive_digest = source_archive_proof(api, artifact, target)
                proofs.append(
                    {
                        "source_run_id": run["id"],
                        "source_artifact_id": artifact["id"],
                        "source_artifact_digest": artifact["digest"],
                        "source_archive_sha256": archive_digest,
                    }
                )
    require(bool(proofs), "no_successful_exact_sha_source_verification")
    return {
        "campaign_id": CAMPAIGN,
        "source_sha": target,
        "run_id": env["GITHUB_RUN_ID"],
        "workflow_sha": env.get("WORKFLOW_SHA"),
        "run_attempt": 1,
        "prior_campaign": history["previous"],
        **proofs[-1],
    }


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        raise ValueError("api_redirect_refused")


class GitHubAPI:
    def __init__(self):
        self.opener = urllib.request.build_opener(NoRedirect)
        self.calls = 0

    def __call__(self, path, value=None):
        self.calls += 1
        require(self.calls <= 120, "api_request_budget")
        request = urllib.request.Request(
            "https://api.github.com/repos/" + REPO + path,
            data=None if value is None else json.dumps(value).encode(),
            headers={
                "Authorization": "Bearer " + os.environ["GH_TOKEN"],
                "Accept": "application/vnd.github+json",
                "Content-Type": "application/json",
            },
        )
        with self.opener.open(request, timeout=15) as response:
            raw = response.read(2_000_001)
        require(len(raw) <= 2_000_000, "api_response_limit")
        return json.loads(raw)

    def download(self, path, limit):
        """Official GitHub archive redirect, no token forwarded, bounded/no retry."""
        self.calls += 1
        require(self.calls <= 120 and limit <= 2_000_000, "api_download_budget")

        class RedirectResponse(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, *args, **kwargs):
                return None

        opener = urllib.request.build_opener(RedirectResponse)
        request = urllib.request.Request(
            "https://api.github.com/repos/" + REPO + path,
            headers={
                "Authorization": "Bearer " + os.environ["GH_TOKEN"],
                "Accept": "application/vnd.github+json",
            },
        )
        try:
            try:
                response = opener.open(request, timeout=20)
            except urllib.error.HTTPError as exc:
                require(exc.code == 302, "evidence_download_status")
                location = exc.headers["Location"]
                url = urllib.parse.urlsplit(location)
                host = url.hostname or ""
                require(
                    url.scheme == "https"
                    and not url.username
                    and not url.password
                    and url.port in (None, 443)
                    and (
                        host == "github.com"
                        or host.endswith((".githubusercontent.com", ".blob.core.windows.net"))
                    ),
                    "evidence_download_origin",
                )
                # The signed archive URL is never logged or given an auth header.
                response = opener.open(urllib.request.Request(location), timeout=20)
            with response:
                content = response.read(limit + 1)
        except Exception:
            raise ValueError("evidence_download_failed") from None
        require(len(content) <= limit, "evidence_download_size")
        return content


def write_report(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n")


def verify_receipt(api, record, target, env):
    require(record["campaign_id"] == CAMPAIGN and record["consumed"] is True, "missing_consumption")
    require(
        record["source_sha"] == target and record["run_id"] == env["GITHUB_RUN_ID"],
        "receipt_mismatch",
    )
    require(record["run_attempt"] == 1, "receipt_rerun")
    previous = verify_known_failure(api)
    require(
        all(
            record["prior_campaign"][key] == previous[key]
            for key in (
                "run_id",
                "source_sha",
                "marker_id",
                "consumed",
                "result",
                "artifact_id",
                "artifact_digest",
            )
        ),
        "prior_campaign_receipt_inconsistent",
    )
    marker = api(f"/check-runs/{int(record['marker_id'])}")
    require(
        marker["id"] == record["marker_id"]
        and marker["status"] == "completed"
        and marker["conclusion"] == "neutral"
        and marker["app"]["slug"] == "github-actions"
        and marker["head_sha"] == target
        and marker["name"] == MARKER
        and marker["external_id"] == CAMPAIGN + ":" + env["GITHUB_RUN_ID"],
        "marker_mismatch",
    )
    artifact = api(f"/actions/artifacts/{int(record['source_artifact_id'])}")
    require(
        not artifact["expired"] and artifact["digest"] == record["source_artifact_digest"],
        "source_artifact_changed",
    )
    source = api(f"/actions/runs/{int(record['source_run_id'])}")
    require(source["head_sha"] == target, "source_run_changed")
    current_pr(api, target)


def public_acceptance(raw):
    """Explicit export projection: no SQLite job rows/config/backup/database payload."""
    result = {
        k: raw[k]
        for k in (
            "project",
            "source_sha",
            "image_id",
            "qdrant_image_id",
            "result",
            "failure_class",
            "corpus_sha256",
        )
        if k in raw
    }
    result["checks"] = [{"name": c["name"], "status": c["status"]} for c in raw["checks"]]
    if "pooling" in raw:
        fields = (
            "dimension",
            "pooling",
            "normalization",
            "reference_max_abs_error",
            "batch_single_max_abs_error",
            "l2_norms",
            "embeddings",
            "truncation",
            "padding",
            "providers",
        )
        result["pooling"] = {k: raw["pooling"][k] for k in fields if k in raw["pooling"]}
    if "search_results" in raw:
        fields = ("id", "document", "filename", "page", "citation", "excerpt", "ranking")
        result["search_results"] = {
            "status": raw["search_results"]["status"],
            "matches": [
                {k: hit[k] for k in fields if k in hit} for hit in raw["search_results"]["matches"]
            ],
        }
    if "api_restart" in raw:
        source = raw["api_restart"]
        allowed = ("phase", "ready_status", "job_http_status", "search_http_status")
        restart = {k: source[k] for k in allowed if k in source}
        for side in ("before", "after"):
            if side not in source:
                continue
            view = source[side]
            observation = {k: view[k] for k in ("ready_status", "job_state", "search_http_status")}
            observation["documents"] = [
                {k: d[k] for k in ("id", "workspace", "content_hash")} for d in view["documents"]
            ]
            observation["chunks"] = [
                {
                    k: c[k]
                    for k in (
                        "id",
                        "workspace",
                        "document",
                        "page",
                        "ordinal",
                        "start",
                        "end",
                        "text_sha256",
                    )
                }
                for c in view["chunks"]
            ]
            observation["search"] = None
            if view["search"] is not None:
                fields = (
                    "id",
                    "workspace",
                    "document",
                    "filename",
                    "content_hash",
                    "page",
                    "ordinal",
                    "start",
                    "end",
                    "citation",
                    "excerpt_sha256",
                    "provenance_sha256",
                    "ranking_sha256",
                )
                scores = ("dense_cosine", "bm25", "rrf", "reranker", "term_coverage", "score")
                observation["search"] = {
                    "status": view["search"]["status"],
                    "matches": [
                        {
                            **{k: m[k] for k in fields if k in m},
                            "ranking": {k: m["ranking"][k] for k in scores if k in m["ranking"]},
                        }
                        for m in view["search"]["matches"]
                    ],
                }
            restart[side] = observation
        names = (
            "API readiness after restart",
            "persisted job COMPLETED after API restart",
            "persisted document identities after API restart",
            "persisted chunk identities after API restart",
            "retrieval status after API restart",
            "retrieval hit IDs and order after API restart",
            "source citation provenance after API restart",
            "exact ranking scores after API restart",
        )
        restart["checks"] = {k: source["checks"][k] for k in names if k in source.get("checks", {})}
        restart["ranking_differences"] = [
            {k: d[k] for k in ("hit_index", "field", "before", "after", "absolute_delta") if k in d}
            for d in source.get("ranking_differences", [])
            if d["field"] in {"dense_cosine", "bm25", "rrf", "reranker", "term_coverage", "score"}
        ]
        result["api_restart"] = restart
    for name in ("state_before_backup", "state_after_restore"):
        if name in raw:
            state = raw[name]
            result[name] = {
                "collections": [
                    {k: c[k] for k in ("workspace", "points", "dimension", "status")}
                    for c in state["collections"]
                ],
                "committed_chunks": state["committed_chunks"],
                "job_states": dict(Counter(j["state"] for j in state["jobs"])),
            }
    if raw.get("result") == "FAIL" and not any(c["status"] == "FAIL" for c in result["checks"]):
        result["checks"].append({"name": "campaign execution", "status": "FAIL"})
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("operation", choices=["inactive", "reserve", "verify", "finish"])
    operation = parser.parse_args().operation
    event = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text())
    env = dict(os.environ)
    checkout = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    if operation == "inactive":
        require(event.get("action") != "labeled", "inactive_check_cannot_activate")
        write_report(
            DIRECTORY / "trigger-inactive.json",
            {
                "campaign_id": CAMPAIGN,
                "source_sha": checkout,
                "run_id": env["GITHUB_RUN_ID"],
                "consumed_by_this_event": False,
                "authorization_state": "not_evaluated_in_configuration",
                "model_download_started": False,
            },
        )
        return
    if operation == "finish":
        if not RECEIPT.is_file():
            return  # Never invent a consumption marker when reservation failed.
        record = json.loads(RECEIPT.read_text())
        record.update(
            acquisition_outcome=env.get("ACQUISITION_OUTCOME"),
            acceptance_outcome=env.get("ACCEPTANCE_OUTCOME"),
            elapsed_seconds=(
                dt.datetime.now(dt.UTC) - dt.datetime.fromisoformat(record["reserved_at"])
            ).total_seconds(),
        )
        raw = Path(".local/cpu-private-result.json")
        if raw.is_file():
            accepted = json.loads(raw.read_text())
            require(accepted["source_sha"] == record["source_sha"], "acceptance_source_mismatch")
            require(
                accepted["model"]["model_id"] == MODEL
                and accepted["model"]["revision"] == REVISION
                and accepted["model"]["files"]["onnx/model.onnx"]["sha256"] == ONNX,
                "acceptance_model_mismatch",
            )
            record["execution"] = public_acceptance(accepted)
            record["verified_model"] = accepted["model"]
        record["expected_model"] = {"id": MODEL, "revision": REVISION, "onnx_sha256": ONNX}
        write_report(RECEIPT, record)
        return
    api = GitHubAPI()
    if operation == "reserve":
        record = authorize(api, event, env, checkout)
        marker = api(
            "/check-runs",
            {
                "name": MARKER,
                "head_sha": checkout,
                "status": "completed",
                "conclusion": "neutral",
                "external_id": CAMPAIGN + ":" + env["GITHUB_RUN_ID"],
                "output": {
                    "title": "CPU campaign budget reserved before acquisition",
                    "summary": "Consumption record only; not acceptance/security PASS; no retry.",
                },
            },
        )
        record.update(
            marker_id=marker["id"], consumed=True, reserved_at=dt.datetime.now(dt.UTC).isoformat()
        )
        verify_receipt(api, record, checkout, env)
        write_report(RECEIPT, record)
    else:
        target = activation(event, env, checkout)
        require(RECEIPT.is_file() and not RECEIPT.is_symlink(), "missing_consumption_receipt")
        record = json.loads(RECEIPT.read_text())
        verify_receipt(api, record, target, env)


if __name__ == "__main__":
    main()
