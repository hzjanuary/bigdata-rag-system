"""Full-history gitleaks scan with one evidence-backed public model-hash review.

No detector rules/paths/commits are disabled. Unknown findings or scanner errors fail.
The historical commit is immutable; the exact line is checked independently.
"""

import hashlib
import json
import subprocess
from pathlib import Path

SCANNER = (
    "zricethezav/gitleaks@sha256:c00b6bd0aeb3071cbcb79009cb16a60dd9e0a7c60e2be9ab65d25e6bc8abbb7f"
)
REVISION = "8fa3c3501f6ad0e2ba454ba7e72bc2ddc7341e86"
FINGERPRINT = REVISION + ":rag_core/embedding.py:generic-api-key:12"
PUBLIC_LINE_SHA256 = "a4bcca059e76bc87a31eead8355b5b20a74ef9612a7f6eef38cf894571deec35"


def review(findings, root):
    reviewed = []
    for finding in findings:
        if finding.get("Fingerprint") != FINGERPRINT:
            raise ValueError("unreviewed historical secret finding")
        content = subprocess.check_output(
            ["git", "show", REVISION + ":rag_core/embedding.py"], cwd=root
        )
        line = content.splitlines(keepends=True)[11]
        if hashlib.sha256(line).hexdigest() != PUBLIC_LINE_SHA256:
            raise ValueError("historical public-hash line mismatch")
        reviewed.append(
            {
                "fingerprint": FINGERPRINT,
                "classification": "public tokenizer Git blob integrity hash",
                "evidence": "docs/release/evidence/model-acquisition.json; official pinned Hugging Face Git blob metadata",
                "line_sha256": PUBLIC_LINE_SHA256,
            }
        )
    return reviewed


def main():
    root = Path(__file__).resolve().parents[1]
    output = root / ".local"
    output.mkdir(exist_ok=True)
    raw = output / "history-secrets.json"
    result = subprocess.run(
        [
            "docker",
            "run",
            "--rm",
            "-v",
            f"{root}:/repo:ro",
            "-v",
            f"{output}:/output",
            SCANNER,
            "git",
            "/repo",
            "--redact=100",
            "--log-opts=--all",
            "--no-banner",
            "--report-format",
            "json",
            "--report-path",
            "/output/history-secrets.json",
        ],
        capture_output=True,
    )
    (output / "history-secrets.log").write_bytes(result.stdout + result.stderr)
    if result.returncode not in {0, 1} or not raw.is_file():
        raise RuntimeError("historical secret scanner failed")
    findings = json.loads(raw.read_text())
    reviewed = review(findings, root)
    if (result.returncode == 1) != bool(findings):
        raise RuntimeError("scanner result/report inconsistency")
    report = {
        "result": "PASS" if not findings else "PASS_WITH_REVIEWED_PUBLIC_HASH",
        "raw_scanner_exit": result.returncode,
        "reviewed": reviewed,
        "unreviewed_findings": 0,
    }
    (output / "history-secret-review.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
