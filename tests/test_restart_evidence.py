import copy
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


helper = load("acceptance_helpers")
policy = load("cpu_campaign")


def observation():
    state = {
        "documents": [{"id": "d", "workspace": "w", "content_hash": "h"}],
        "chunks": [
            {
                "id": "c",
                "workspace": "w",
                "document": "d",
                "page": 2,
                "ordinal": 0,
                "start": 0,
                "end": 20,
                "text_sha256": "hash",
            }
        ],
    }
    search = {
        "status": "matched",
        "matches": [
            {
                "id": "c",
                "workspace": "w",
                "document": "d",
                "citation": "w:d:c",
                "filename": "synthetic.pdf",
                "page": 2,
                "excerpt": "PRIVATE-CONTENT-SENTINEL",
                "ranking": {"bm25": 3.292419763002416},
            }
        ],
    }
    return state, search


@pytest.mark.parametrize(
    "defect",
    ["ready", "job", "document", "chunk", "status", "hit", "citation", "score", "extra-score"],
    ids=str,
)
def test_each_restart_condition_is_observable_before_assertion(defect):
    state, search = observation()
    before = helper.restart_observation(200, "COMPLETED", state, search)
    state, search = copy.deepcopy(state), copy.deepcopy(search)
    ready, job = 200, "COMPLETED"
    expected = {
        "ready": "API readiness",
        "job": "persisted job",
        "document": "persisted document",
        "chunk": "persisted chunk",
        "status": "retrieval status",
        "hit": "retrieval hit",
        "citation": "source citation",
        "score": "exact ranking",
        "extra-score": "exact ranking",
    }
    if defect == "ready":
        ready = 503
    if defect == "job":
        job = "QUEUED"
    if defect == "document":
        state["documents"][0]["id"] = "other"
    if defect == "chunk":
        state["chunks"][0]["text_sha256"] = "other"
    if defect == "status":
        search["status"] = "no_match"
    if defect == "hit":
        search["matches"][0]["id"] = "other"
    if defect == "citation":
        search["matches"][0]["citation"] = "wrong"
    if defect == "score":
        search["matches"][0]["ranking"]["bm25"] = 3.2924197630024166
    if defect == "extra-score":
        search["matches"][0]["ranking"]["unexpected"] = 1
    after = helper.restart_observation(ready, job, state, search)
    diagnostic = helper.restart_comparison(before, after)
    assert len(diagnostic["checks"]) == 8
    assert not next(v for k, v in diagnostic["checks"].items() if k.startswith(expected[defect]))
    assert diagnostic["before"] == before and diagnostic["after"] == after
    if defect == "score":
        assert diagnostic["ranking_differences"][0]["absolute_delta"] == 4.440892098500626e-16
        assert diagnostic["checks"]["source citation provenance after API restart"] is True
    assert "PRIVATE-CONTENT-SENTINEL" not in json.dumps(diagnostic)


def test_public_restart_projection_rejects_unlisted_private_material():
    state, search = observation()
    before = helper.restart_observation(200, "COMPLETED", state, search)
    diagnostic = helper.restart_comparison(before, copy.deepcopy(before))
    assert all(diagnostic["checks"].values())
    diagnostic["private_config"] = "DO-NOT-EXPORT"
    diagnostic["after"]["credentials"] = "DO-NOT-EXPORT"
    diagnostic["before"]["documents"][0]["raw_document"] = "DO-NOT-EXPORT"
    public = policy.public_acceptance({"api_restart": diagnostic, "checks": [], "result": "PASS"})
    encoded = json.dumps(public)
    assert "DO-NOT-EXPORT" not in encoded and "PRIVATE-CONTENT-SENTINEL" not in encoded
    assert all(public["api_restart"]["checks"].values())
    assert public["api_restart"]["before"]["search"]["matches"][0]["citation"] == "w:d:c"


def test_missing_search_is_failure_not_fabricated_no_match():
    state, search = observation()
    before = helper.restart_observation(200, "COMPLETED", state, search)
    after = helper.restart_observation(200, None, state, None, 503)
    diagnostic = helper.restart_comparison(before, after)
    assert diagnostic["after"]["search"] is None
    assert not diagnostic["checks"]["retrieval status after API restart"]
    assert not diagnostic["checks"]["persisted job COMPLETED after API restart"]


@pytest.mark.parametrize(
    "arguments",
    [
        ["--project", "../unsafe"],
        ["--project", "spec001-1234567890", "--resume-project", "spec001-1234567890"],
    ],
    ids=["unsafe-project", "fresh-resume-conflict"],
)
def test_local_network_project_option_rejects_unsafe_reuse(arguments, monkeypatch, tmp_path):
    monkeypatch.syspath_prepend(str(ROOT / "scripts"))
    campaign = load("isolated_acceptance")
    monkeypatch.setattr(
        "sys.argv",
        [
            "campaign",
            "--approved-local-model-test",
            "--model-dir",
            str(tmp_path / "absent-model"),
            "--evidence",
            str(tmp_path / "result.json"),
            *arguments,
        ],
    )
    with pytest.raises(SystemExit) as caught:
        campaign.main()
    assert caught.value.code == 2
    assert not (tmp_path / "result.json").exists()
