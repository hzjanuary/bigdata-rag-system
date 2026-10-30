import copy
import datetime as dt
import importlib.util
import json
import sys
import urllib.parse
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).parents[1]
spec = importlib.util.spec_from_file_location("cpu_campaign", ROOT / "scripts/cpu_campaign.py")
policy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(policy)
TARGET = "a" * 40
NOW = dt.datetime(2026, 10, 30, 5, tzinfo=dt.UTC)


@pytest.fixture
def approval():
    pr = {
        "number": 1,
        "state": "open",
        "draft": True,
        "labels": [{"name": policy.PREFIX + TARGET}],
        "head": {"sha": TARGET, "ref": policy.BRANCH, "repo": {"full_name": policy.REPO}},
        "base": {"ref": "main"},
    }
    event = {
        "action": "labeled",
        "number": 1,
        "pull_request": pr,
        "label": {"name": policy.PREFIX + TARGET},
        "sender": {"login": policy.OWNER},
        "repository": {"full_name": policy.REPO, "owner": {"login": policy.OWNER}},
    }
    env = {
        "GITHUB_EVENT_NAME": "pull_request",
        "GITHUB_REPOSITORY": policy.REPO,
        "GITHUB_ACTOR": policy.OWNER,
        "GITHUB_RUN_ATTEMPT": "1",
        "GITHUB_RUN_ID": "30",
    }
    return event, env


@pytest.mark.parametrize(
    "field,value",
    [
        ("label.name", "cpuq1:wrong"),
        ("label.name", policy.PREFIX + "b" * 40),
        ("number", 2),
        ("pull_request.number", 2),
        ("sender.login", "outsider"),
        ("pull_request.head.repo.full_name", "outsider/fork"),
        ("pull_request.head.ref", "main"),
        ("repository.full_name", "other/repo"),
        ("repository.owner.login", "other"),
        ("pull_request.head.sha", "A" * 40),
        ("pull_request.draft", False),
        ("pull_request.state", "closed"),
        ("action", "synchronize"),
    ],
    ids=[
        "invalid-label",
        "stale-label-sha",
        "other-pr",
        "other-payload-pr",
        "other-sender",
        "fork",
        "other-branch",
        "other-repository",
        "other-owner",
        "invalid-sha",
        "not-draft",
        "closed",
        "synchronize",
    ],
)
def test_invalid_approval_cannot_reach_api(approval, field, value):
    event, env = approval
    obj = event
    parts = field.split(".")
    for part in parts[:-1]:
        obj = obj[part]
    obj[parts[-1]] = value
    calls = []
    with pytest.raises(ValueError):
        policy.authorize(lambda *args: calls.append(args), event, env, TARGET, NOW)
    assert calls == []


@pytest.mark.parametrize(
    "field,value",
    [
        ("GITHUB_ACTOR", "outsider"),
        ("GITHUB_RUN_ATTEMPT", "2"),
        ("GITHUB_EVENT_NAME", "push"),
        ("GITHUB_EVENT_NAME", "workflow_dispatch"),
        ("GITHUB_REPOSITORY", "wrong/repo"),
        ("GITHUB_RUN_ID", ""),
    ],
    ids=["other-actor", "rerun", "push", "manual-dispatch", "other-repo", "no-run-id"],
)
def test_environment_rejects_before_api(approval, field, value):
    event, env = approval
    env[field] = value
    with pytest.raises(ValueError):
        policy.activation(event, env, TARGET, NOW)


def test_stale_checkout_and_expiry_reject(approval):
    event, env = approval
    with pytest.raises(ValueError, match="checkout"):
        policy.activation(event, env, "b" * 40, NOW)
    with pytest.raises(ValueError, match="expired"):
        policy.activation(event, env, TARGET, policy.DEADLINE)


class History:
    def __init__(self, approval):
        self.pr = copy.deepcopy(approval[0]["pull_request"])
        self.calls = []
        self.ci = [
            self.run(20, ".github/workflows/ci.yml"),
            self.run(
                41006993655, ".github/workflows/ci.yml", "11736f527612fc659a201b13e38d13c7278e1476"
            ),
        ]
        self.trigger = [self.run(30, policy.WORKFLOW), self.run(29, policy.WORKFLOW)]
        steps = [
            {"name": n, "conclusion": "success"}
            for n in (
                "Exact archive and historical secret gates",
                "Verify exported reports",
                "Run actions/upload-artifact@pinned",
            )
        ]
        self.jobs = {
            20: [{"id": 201, "name": "source", "conclusion": "success", "steps": steps}],
            29: [
                {"id": 291, "name": "configuration", "conclusion": "success"},
                {"id": 292, "name": "campaign", "conclusion": "skipped"},
            ],
            41006993655: [{"id": 11, "name": "independent-cpu", "conclusion": "skipped"}],
        }
        self.artifacts = [
            {"id": 50, "name": "source-20", "expired": False, "digest": "sha256:" + "f" * 64}
        ]
        self.checks = []

    def run(self, number, path, sha=TARGET):
        return {
            "id": number,
            "path": path,
            "head_sha": sha,
            "status": "completed",
            "run_attempt": 1,
        }

    def __call__(self, path, value=None):
        assert value is None, "Authorization/history tests must perform no API writes"
        self.calls.append(path)
        path = urllib.parse.urlsplit(path).path
        if path == "/pulls/1":
            return self.pr
        if path == "/actions/runs/41006993655":
            return self.ci[1]
        if "/workflows/" in path:
            rows, key = (self.ci if "/ci.yml/" in path else self.trigger), "workflow_runs"
        elif path.endswith("/jobs"):
            rows, key = self.jobs[int(path.split("/")[3])], "jobs"
        elif path.endswith("/artifacts"):
            rows, key = self.artifacts, "artifacts"
        elif path.endswith("/check-runs"):
            rows, key = self.checks, "check_runs"
        else:
            raise AssertionError("Unexpected API path")
        return {"total_count": len(rows), key: rows}


def test_complete_unconsumed_exact_head_source_proof(approval):
    event, env = approval
    api = History(approval)
    record = policy.authorize(api, event, env, TARGET, NOW)
    assert record["source_sha"] == TARGET and record["source_run_id"] == 20
    assert record["source_artifact_id"] == 50
    assert "consumed" not in record  # Read-only verification cannot consume the campaign.
    assert len(policy.PREFIX + TARGET) <= 50


@pytest.mark.parametrize(
    "defect",
    [
        "moved-head",
        "removed-label",
        "failed-source",
        "stale-source",
        "missing-artifact",
        "missing-digest",
        "expired-artifact",
        "failed-export",
        "failed-secret",
        "prior-attempt",
        "missing-job-evidence",
        "prior-marker",
        "missing-history",
    ],
)
def test_uncertain_or_used_campaign_fails_closed(approval, defect):
    event, env = approval
    api = History(approval)
    if defect == "moved-head":
        api.pr["head"]["sha"] = "b" * 40
    if defect == "removed-label":
        api.pr["labels"] = []
    if defect == "failed-source":
        api.jobs[20][0]["conclusion"] = "failure"
    if defect == "stale-source":
        api.ci[0]["head_sha"] = "b" * 40
    if defect == "missing-artifact":
        api.artifacts = []
    if defect == "missing-digest":
        api.artifacts[0].pop("digest")
    if defect == "expired-artifact":
        api.artifacts[0]["expired"] = True
    if defect == "failed-export":
        api.jobs[20][0]["steps"][1]["conclusion"] = "failure"
    if defect == "failed-secret":
        api.jobs[20][0]["steps"][0]["conclusion"] = "failure"
    if defect == "prior-attempt":
        api.jobs[29][1]["conclusion"] = "failure"
    if defect == "missing-job-evidence":
        api.jobs[29] = []
    if defect == "prior-marker":
        api.checks = [{"id": 7}]
    if defect == "missing-history":
        api.trigger = []
    with pytest.raises((ValueError, KeyError)):
        policy.authorize(api, event, env, TARGET, NOW)


def test_incomplete_pagination_and_api_failure_never_pass():
    with pytest.raises(ValueError, match="incomplete"):
        policy.complete_list(lambda _: {"total_count": 1, "jobs": []}, "/history", "jobs")

    def unavailable(_):
        raise OSError("API unavailable")

    with pytest.raises(OSError):
        policy.complete_list(unavailable, "/history", "jobs")


def test_missing_consumption_cannot_authorize_acquisition(approval):
    _, env = approval
    with pytest.raises(KeyError):
        policy.verify_receipt(lambda _: pytest.fail("No API expected"), {}, TARGET, env)
    record = {"campaign_id": policy.CAMPAIGN, "consumed": False}
    with pytest.raises(ValueError, match="missing_consumption"):
        policy.verify_receipt(lambda _: pytest.fail("No API expected"), record, TARGET, env)


def test_intact_marker_source_and_current_head_required_before_acquisition(approval):
    event, env = approval
    record = {
        "campaign_id": policy.CAMPAIGN,
        "consumed": True,
        "source_sha": TARGET,
        "run_id": "30",
        "run_attempt": 1,
        "marker_id": 7,
        "source_artifact_id": 50,
        "source_artifact_digest": "sha256:" + "f" * 64,
        "source_run_id": 20,
    }
    responses = {
        "/check-runs/7": {
            "head_sha": TARGET,
            "name": policy.MARKER,
            "external_id": policy.CAMPAIGN + ":30",
        },
        "/actions/artifacts/50": {"expired": False, "digest": record["source_artifact_digest"]},
        "/actions/runs/20": {"head_sha": TARGET},
        "/pulls/1": event["pull_request"],
    }
    policy.verify_receipt(responses.__getitem__, record, TARGET, env)
    responses["/check-runs/7"]["head_sha"] = "b" * 40
    with pytest.raises(ValueError, match="marker_mismatch"):
        policy.verify_receipt(responses.__getitem__, record, TARGET, env)


def test_public_export_drops_configuration_and_database_rows():
    raw = {
        "checks": [{"name": "actual test", "status": "PASS"}],
        "result": "FAIL",
        "private_config": "DO-NOT-EXPORT",
        "state_before_backup": {
            "collections": [],
            "committed_chunks": 1,
            "jobs": [{"state": "COMPLETED", "filename": "DO-NOT-EXPORT"}],
        },
    }
    report = policy.public_acceptance(raw)
    assert "DO-NOT-EXPORT" not in json.dumps(report)
    assert report["state_before_backup"]["job_states"] == {"COMPLETED": 1}
    assert report["checks"][-1]["status"] == "FAIL"


def test_inactive_cli_has_no_api_or_consumption(approval, tmp_path, monkeypatch):
    event, env = approval
    event["action"] = "synchronize"
    path = tmp_path / "event.json"
    path.write_text(json.dumps(event))
    monkeypatch.setenv("GITHUB_EVENT_PATH", str(path))
    monkeypatch.setenv("GITHUB_RUN_ID", env["GITHUB_RUN_ID"])
    monkeypatch.setattr(sys, "argv", ["cpu_campaign", "inactive"])
    monkeypatch.setattr(policy, "DIRECTORY", tmp_path / "evidence")
    monkeypatch.setattr(policy.subprocess, "check_output", lambda *a, **k: TARGET)
    monkeypatch.setattr(
        policy, "GitHubAPI", lambda: pytest.fail("Inactive check must not call API")
    )
    policy.main()
    report = json.loads((policy.DIRECTORY / "trigger-inactive.json").read_text())
    assert report["consumed"] is False and report["model_download_started"] is False


def test_workflow_has_one_guarded_acquisition_and_no_provider():
    workflow = yaml.safe_load((ROOT / policy.WORKFLOW).read_text())
    events = workflow.get("on", workflow.get(True))
    assert events["pull_request"]["types"] == ["synchronize", "labeled"]
    assert "pull_request_target" not in events and "workflow_dispatch" not in events
    assert workflow["concurrency"]["cancel-in-progress"] is False
    job = workflow["jobs"]["campaign"]
    for clause in (
        "github.event.action == 'labeled'",
        "github.actor == 'hzjanuary'",
        "github.run_attempt == 1",
    ):
        assert clause in job["if"]
    runs = [s.get("run", "") for s in job["steps"]]
    assert sum("scripts/acquire_model.py" in run for run in runs) == 1
    assert next(i for i, run in enumerate(runs) if "cpu_campaign.py verify" in run) < next(
        i for i, run in enumerate(runs) if "scripts/acquire_model.py" in run
    )
    assert "cpu_campaign.py reserve" in "\n".join(runs)
    assert "--resume-project" not in "\n".join(runs)
    assert all(
        word not in "\n".join(runs).lower()
        for word in ("rag ask", "groq", "openrouter", "provider_key")
    )
    assert "acquire_model" not in json.dumps(workflow["jobs"]["configuration"])
    assert job["runs-on"] == "ubuntu-24.04"
