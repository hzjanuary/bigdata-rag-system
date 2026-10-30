"""Exercise actual pytest XML and the unchanged artifact guard in subprocesses."""

import hashlib
import json
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]


def run_pytest(report, *tests):
    return subprocess.run(
        [sys.executable, "-m", "pytest", "-q", f"--junitxml={report}", *tests],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=60,
    )


def export_reports(directory):
    return subprocess.run(
        [sys.executable, "scripts/evidence_gate.py", str(directory)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=10,
    )


def assert_exported(report):
    result = export_reports(report.parent)
    assert result.returncode == 0, result.stderr
    rows = json.loads((report.parent / "checksums.json").read_text())["files"]
    assert rows == [
        {
            "path": report.name,
            "sha256": hashlib.sha256(report.read_bytes()).hexdigest(),
            "bytes": report.stat().st_size,
        }
    ]


def test_large_payload_cases_export_bounded_junit(tmp_path):
    report = tmp_path / "junit.xml"
    expected = {
        "test_parser_rejects_invalid_or_oversized": {
            "invalid-nul",
            "invalid-utf8",
            "malformed-pdf",
            "malformed-docx",
            "unsupported-extension",
            "empty-text",
            "oversized-text",
        },
        "test_gate_catches_bypasses": {
            "root-env",
            "nested-env",
            "model-cache",
            "binary-pdf",
            "upload",
            "database",
            "symlink",
            "literal-bearer",
            "private-key",
            "private-path",
            "binary-nul",
            "oversized-text",
        },
        "test_stdin_input_validation": {
            "missing-filename",
            "traversal-filename",
            "oversized-stdin",
            "filename-with-file",
        },
    }
    result = run_pytest(
        report,
        "tests/test_ingestion.py::test_parser_rejects_invalid_or_oversized",
        "tests/test_artifacts.py::test_gate_catches_bypasses",
        "tests/test_cli.py::test_stdin_input_validation",
    )
    assert result.returncode == 0, result.stdout + result.stderr
    root = ET.parse(report).getroot()
    cases = list(root.iter("testcase"))
    assert len(cases) == 23
    names = [case.attrib["name"] for case in cases]
    assert len(set(names)) == 23
    assert max(map(len, names)) < 100
    for test, ids in expected.items():
        assert {name for name in names if name.startswith(test + "[")} == {
            f"{test}[{case_id}]" for case_id in ids
        }
    suite = root.find("testsuite")
    assert suite is not None
    assert {key: int(suite.attrib[key]) for key in ("tests", "failures", "errors", "skipped")} == {
        "tests": 23,
        "failures": 0,
        "errors": 0,
        "skipped": 0,
    }
    assert b"x" * 1000 not in report.read_bytes()
    assert report.stat().st_size < 2_000_000
    assert_exported(report)


def test_failed_and_skipped_results_remain_in_exported_junit(tmp_path):
    # Deliberate child-suite failure verifies real reporting, not a fabricated XML fixture.
    test_file = tmp_path / "test_reporting.py"
    test_file.write_text(
        "import pytest\n"
        "def test_pass():\n    assert True\n"
        "def test_failure():\n    assert False, 'SYNTHETIC-FAILURE-DETAILS'\n"
        "def test_skip():\n    pytest.skip('SYNTHETIC-SKIP-REASON')\n"
    )
    reports = tmp_path / "reports"
    reports.mkdir()
    report = reports / "junit.xml"
    result = run_pytest(report, str(test_file))
    assert result.returncode == 1
    root = ET.parse(report).getroot()
    cases = {case.attrib["name"]: case for case in root.iter("testcase")}
    assert set(cases) == {"test_pass", "test_failure", "test_skip"}
    failure = cases["test_failure"].find("failure")
    skipped = cases["test_skip"].find("skipped")
    assert failure is not None and "SYNTHETIC-FAILURE-DETAILS" in failure.text
    assert skipped is not None and "SYNTHETIC-SKIP-REASON" in skipped.attrib["message"]
    suite = root.find("testsuite")
    assert suite is not None
    assert {key: int(suite.attrib[key]) for key in ("tests", "failures", "errors", "skipped")} == {
        "tests": 3,
        "failures": 1,
        "errors": 0,
        "skipped": 1,
    }
    assert_exported(report)


@pytest.mark.parametrize(
    "name,data",
    [("junit.xml", b"x" * 2_000_001), ("model.onnx", b"weights"), ("junit.xml", b"\0binary")],
    ids=["oversized-report", "unauthorized-model", "binary-report"],
)
def test_export_guard_still_rejects_invalid_artifacts(tmp_path, name, data):
    (tmp_path / name).write_bytes(data)
    result = export_reports(tmp_path)
    assert result.returncode != 0
    assert "ValueError" in result.stderr
    assert not (tmp_path / "checksums.json").exists()
