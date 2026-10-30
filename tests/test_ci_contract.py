from pathlib import Path

import yaml


def workflow():
    return yaml.safe_load((Path(__file__).parents[1] / ".github/workflows/ci.yml").read_text())


def test_image_gates_never_convert_known_findings_to_success():
    data = workflow()
    job = data["jobs"]["images"]
    assert set(job["strategy"]["matrix"]["variant"]) == {"core", "qdrant", "ui"}
    step = next(s for s in job["steps"] if s.get("name") == "Unchanged HIGH/CRITICAL security gate")
    assert "--exit-code 1" in step["run"] and "--severity HIGH,CRITICAL" in step["run"]
    assert "continue-on-error" not in step and "|| true" not in step["run"]
    assert job["strategy"]["fail-fast"] is False


def test_model_campaign_never_runs_on_normal_push_or_synchronize():
    assert "independent-cpu" not in workflow()["jobs"]
    data = yaml.safe_load(
        (Path(__file__).parents[1] / ".github/workflows/spec001-cpu-once.yml").read_text()
    )
    job = data["jobs"]["campaign"]
    assert "github.event_name == 'pull_request'" in job["if"]
    assert "github.event.action == 'labeled'" in job["if"]
    assert "head.repo.full_name == github.repository" in job["if"]
    assert "github.event.pull_request.number == 1" in job["if"]
    assert "github.run_attempt == 1" in job["if"]
    assert "format('cpuq1:{0}', github.event.pull_request.head.sha)" in job["if"]
    assert job["runs-on"] == "ubuntu-24.04"
    steps = "\n".join(s.get("run", "") for s in job["steps"])
    assert "--accept-license-and-download" in steps
    assert "--approved-local-model-test" in steps
    assert "provider_key" not in steps.lower() and "rag ask" not in steps


def test_only_allowlisted_evidence_directory_uploaded():
    for job in workflow()["jobs"].values():
        uploads = [
            s for s in job["steps"] if s.get("uses", "").startswith("actions/upload-artifact@")
        ]
        assert len(uploads) == 1
        assert "steps.evidence_guard.outcome == 'success'" in uploads[0]["if"]
        assert uploads[0]["with"]["path"] == ".local/ci-evidence/"
        assert any("scripts/evidence_gate.py" in s.get("run", "") for s in job["steps"])
