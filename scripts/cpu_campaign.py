"""Fail-closed operator approval/consumption policy; imports never acquire a model."""

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

REPO = "hzjanuary/bigdata-rag-system"
OWNER = "hzjanuary"
BRANCH = "feat/spec-001-oss-rag-core"
WORKFLOW = ".github/workflows/spec001-cpu-once.yml"
CAMPAIGN = "spec001-pr1-cpu-qdrant-once"
MARKER = "spec001-cpu-pr1-consumed"
PREFIX = "cpuq1:"
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
    require((now or dt.datetime.now(dt.UTC)) < DEADLINE, "approval_window_expired")
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


def authorize(api, event, env, checkout, now=None):
    target = activation(event, env, checkout, now)
    current_pr(api, target)
    anchor = api("/actions/runs/41006993655")
    require(
        anchor["head_sha"] == "11736f527612fc659a201b13e38d13c7278e1476", "missing_history_anchor"
    )
    require(anchor["status"] == "completed", "invalid_history_anchor")
    runs = []
    for filename in ("ci.yml", "spec001-cpu-once.yml"):
        items = complete_list(api, f"/actions/workflows/{filename}/runs", "workflow_runs")
        require(bool(items), "missing_workflow_history")
        runs.extend(items)
    require(any(str(r["id"]) == env["GITHUB_RUN_ID"] for r in runs), "missing_current_run")
    proofs = []
    for run in runs:
        if str(run["id"]) == env["GITHUB_RUN_ID"]:
            require(run["run_attempt"] == 1 and run["head_sha"] == target, "current_run_mismatch")
            continue
        jobs = complete_list(api, f"/actions/runs/{run['id']}/jobs?filter=all", "jobs")
        require(bool(jobs), "missing_job_evidence")
        for job in jobs:
            if job["name"] in {"campaign", "independent-cpu", "cpu", "reserve"}:
                require(
                    job.get("conclusion") == "skipped",
                    "previous_campaign_attempt_or_missing_consumption",
                )
        if run["path"] == WORKFLOW:
            require(any(j["name"] == "campaign" for j in jobs), "missing_campaign_job_evidence")
        if run["head_sha"] == target and run["path"] == ".github/workflows/ci.yml":
            source = [j for j in jobs if j["name"] == "source" and j.get("conclusion") == "success"]
            if source:
                steps = source[0]["steps"]
                require(
                    all(
                        any(s["name"] == name and s["conclusion"] == "success" for s in steps)
                        for name in (
                            "Exact archive and historical secret gates",
                            "Verify exported reports",
                        )
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
                        proofs.append(
                            {
                                "source_run_id": run["id"],
                                "source_artifact_id": artifact["id"],
                                "source_artifact_digest": artifact["digest"],
                            }
                        )
    require(bool(proofs), "no_successful_exact_sha_source_verification")
    for sha in {target, *(r["head_sha"] for r in runs)}:
        require(bool(SHA.fullmatch(sha)), "invalid_history_sha")
        checks = complete_list(
            api, f"/commits/{sha}/check-runs?filter=all&check_name={MARKER}", "check_runs"
        )
        require(not checks, "campaign_already_consumed")
    return {
        "campaign_id": CAMPAIGN,
        "source_sha": target,
        "run_id": env["GITHUB_RUN_ID"],
        "workflow_sha": env.get("WORKFLOW_SHA"),
        "run_attempt": 1,
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
    marker = api(f"/check-runs/{int(record['marker_id'])}")
    require(
        marker["head_sha"] == target
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
                "consumed": False,
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
