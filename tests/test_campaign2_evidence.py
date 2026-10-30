"""Policy-unit ZIPs only; genuine prior-run archives are separately audited read-only."""

import hashlib
import importlib.util
import io
import json
import tarfile
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]
spec = importlib.util.spec_from_file_location("second_policy", ROOT / "scripts/cpu_campaign.py")
policy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(policy)


def zipped(files):
    rows = [
        {"path": n, "bytes": len(d), "sha256": hashlib.sha256(d).hexdigest()}
        for n, d in files.items()
    ]
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w") as archive:
        for n, d in files.items():
            archive.writestr(n, d)
        archive.writestr("checksums.json", json.dumps({"files": rows}))
    return out.getvalue()


class PriorEvidence:
    def __init__(self, monkeypatch):
        self.run = {
            "id": policy.OLD_RUN,
            "head_sha": policy.OLD_SHA,
            "path": policy.WORKFLOW,
            "event": "pull_request",
            "run_attempt": 1,
            "status": "completed",
            "conclusion": "failure",
            "actor": {"login": policy.OWNER},
        }
        self.marker = {
            "id": policy.OLD_MARKER_ID,
            "name": policy.OLD_MARKER,
            "head_sha": policy.OLD_SHA,
            "external_id": policy.OLD_CAMPAIGN + ":" + str(policy.OLD_RUN),
            "status": "completed",
            "conclusion": "neutral",
            "app": {"slug": "github-actions"},
        }
        self.steps = [
            {"name": n, "conclusion": c}
            for n, c in {
                "Fail-closed history and consumption reservation": "success",
                "Bounded official pinned model acquisition": "success",
                "ONE synthetic CPU embedding and Qdrant acceptance": "failure",
                "Export sanitized outcome and measured campaign time": "success",
            }.items()
        ]
        self.jobs = [
            {
                "id": policy.OLD_JOB_ID,
                "name": "campaign",
                "conclusion": "failure",
                "steps": self.steps,
            },
            {"id": 2, "name": "configuration", "conclusion": "skipped"},
        ]
        self.receipt = {
            "campaign_id": policy.OLD_CAMPAIGN,
            "consumed": True,
            "run_id": str(policy.OLD_RUN),
            "source_sha": policy.OLD_SHA,
            "run_attempt": 1,
            "marker_id": policy.OLD_MARKER_ID,
            "acquisition_outcome": "success",
            "acceptance_outcome": "failure",
            "execution": {"result": "FAIL", "failure_class": "AssertionError"},
            "verified_model": {
                "model_id": policy.MODEL,
                "revision": policy.REVISION,
                "files": {"onnx/model.onnx": {"sha256": policy.ONNX}},
            },
        }
        self.monkeypatch = monkeypatch
        self.repack()
        out = io.BytesIO()
        with zipfile.ZipFile(out, "w") as archive:
            archive.writestr("failed-step.txt", policy.OLD_FAILURE)
        self.logs = out.getvalue()

    def repack(self):
        self.data = zipped({"consumption.json": json.dumps(self.receipt).encode()})
        digest = "sha256:" + hashlib.sha256(self.data).hexdigest()
        self.monkeypatch.setattr(policy, "OLD_ARTIFACT_DIGEST", digest)
        self.artifact = {"id": policy.OLD_ARTIFACT, "expired": False, "digest": digest}

    def __call__(self, path, value=None):
        assert value is None, "Historical validation cannot write or consume"
        if path == f"/actions/runs/{policy.OLD_RUN}":
            return self.run
        if path == f"/check-runs/{policy.OLD_MARKER_ID}":
            return self.marker
        if path.startswith(f"/actions/runs/{policy.OLD_RUN}/jobs?"):
            return {"total_count": len(self.jobs), "jobs": self.jobs}
        if path == f"/actions/artifacts/{policy.OLD_ARTIFACT}":
            return self.artifact
        raise AssertionError("Unexpected historical API request")

    def download(self, path, limit):
        assert limit == 2_000_000
        if path == f"/actions/artifacts/{policy.OLD_ARTIFACT}/zip":
            return self.data
        if path == f"/actions/runs/{policy.OLD_RUN}/logs":
            return self.logs
        raise AssertionError("Unexpected archive request")


def test_exact_known_consumed_failure_is_accounted_for(monkeypatch):
    api = PriorEvidence(monkeypatch)
    record = policy.verify_known_failure(api)
    assert record["run_id"] == policy.OLD_RUN and record["marker_id"] == policy.OLD_MARKER_ID
    assert record["consumed"] is True and record["result"] == "FAIL"
    assert policy.CAMPAIGN == "spec001-pr1-cpu-qdrant-remediation-2"
    assert policy.MARKER == "spec001-cpu-pr1-remediation-2-consumed" and policy.PREFIX == "cpuq2:"


@pytest.mark.parametrize(
    "defect",
    [
        "run-sha",
        "run-attempt",
        "run-result",
        "actor",
        "marker-id",
        "marker-name",
        "marker-external",
        "marker-status",
        "expired-artifact",
        "artifact-digest",
        "archive-tamper",
        "unconsumed-receipt",
        "wrong-receipt-marker",
        "missing-log-failure",
        "extra-failed-step",
        "extra-attempt",
        "missing-marker",
    ],
)
def test_previous_attempt_exception_rejects_every_inconsistency(monkeypatch, defect):
    api = PriorEvidence(monkeypatch)
    if defect == "run-sha":
        api.run["head_sha"] = "f" * 40
    if defect == "run-attempt":
        api.run["run_attempt"] = 2
    if defect == "run-result":
        api.run["conclusion"] = "success"
    if defect == "actor":
        api.run["actor"]["login"] = "other"
    if defect == "marker-id":
        api.marker["id"] = 9
    if defect == "marker-name":
        api.marker["name"] = policy.MARKER
    if defect == "marker-external":
        api.marker["external_id"] = "other"
    if defect == "marker-status":
        api.marker["conclusion"] = "success"
    if defect == "expired-artifact":
        api.artifact["expired"] = True
    if defect == "artifact-digest":
        api.artifact["digest"] = "sha256:" + "0" * 64
    if defect == "archive-tamper":
        api.data = api.data + b"tamper"
    if defect == "unconsumed-receipt":
        api.receipt["consumed"] = False
        api.repack()
    if defect == "wrong-receipt-marker":
        api.receipt["marker_id"] = 1
        api.repack()
    if defect == "missing-log-failure":
        api.logs = zipped({"other.txt": b"not the expected failure"})
    if defect == "extra-failed-step":
        api.steps.append({"name": "unexpected failure", "conclusion": "failure"})
    if defect == "extra-attempt":
        api.jobs.append({"id": 3, "name": "campaign", "conclusion": "failure"})
    if defect == "missing-marker":
        api.marker = {}
    with pytest.raises((ValueError, KeyError)):
        policy.verify_known_failure(api)


def source_files(target):
    data = b"public source\n"
    name = "rag_core/example.py"
    stream = io.BytesIO()
    with tarfile.open(fileobj=stream, mode="w") as archive:
        member = tarfile.TarInfo(name)
        member.size = len(data)
        archive.addfile(member, io.BytesIO(data))
    tar = stream.getvalue()
    manifest = {
        "source_sha": target,
        "files": [{"path": name, "sha256": hashlib.sha256(data).hexdigest()}],
    }
    return {
        "source.tar": tar,
        "source-manifest.json": json.dumps(manifest).encode(),
        "archive-verification.json": json.dumps(
            {
                "source_sha": target,
                "result": "PASS",
                "archive_sha256": hashlib.sha256(tar).hexdigest(),
            }
        ).encode(),
    }


def test_source_artifact_is_verified_not_just_trusted_by_name():
    target = "a" * 40
    files = source_files(target)
    data = zipped(files)

    class API:
        def download(self, path, limit):
            assert path == "/actions/artifacts/50/zip" and limit == 2_000_000
            return data

    artifact = {"id": 50, "digest": "sha256:" + hashlib.sha256(data).hexdigest()}
    assert (
        policy.source_archive_proof(API(), artifact, target)
        == hashlib.sha256(files["source.tar"]).hexdigest()
    )
    with pytest.raises(ValueError, match="identity"):
        policy.source_archive_proof(API(), artifact, "b" * 40)
    artifact["digest"] = "sha256:" + "0" * 64
    with pytest.raises(ValueError, match="digest"):
        policy.source_archive_proof(API(), artifact, target)


def test_archive_manifest_and_oversize_checks_still_fail_closed():
    data = zipped({"unexpected.bin": b"x" * 2_000_001})
    with pytest.raises(ValueError, match="unsafe_archive"):
        policy.verified_zip(data, "sha256:" + hashlib.sha256(data).hexdigest())
