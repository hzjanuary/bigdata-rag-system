# SPEC-001 verification ledger — 2026-10-30

**Follow-up stopped after a new CI evidence-export defect.** Normal push completed
at `11736f527612fc659a201b13e38d13c7278e1476`; one [Draft PR #1](https://github.com/hzjanuary/bigdata-rag-system/pull/1)
targets main. Both genuine Actions runs finished FAIL. The user permitted observing
the original red OS security gate but explicitly required stopping on new defects.
No correction/rerun/model acquisition followed this new failure. The final evidence
documentation is retained locally without another push/CI trigger.

## Follow-up outcome and stop decision

Full machine-readable evidence, checksums, job steps, local image identities and
public runner metadata: [follow-up report](evidence/followup-remote-ci.json).
Original failure investigation: [Phase 1](evidence/followup-phase1.json).

| Remote run at pushed HEAD `11736f5` | Observed result |
| --- | --- |
| [Push 41006969209](https://github.com/hzjanuary/bigdata-rag-system/actions/runs/41006969209) | FAIL: source report export; image and independent CPU jobs SKIPPED |
| [Draft PR 41006993655](https://github.com/hzjanuary/bigdata-rag-system/actions/runs/41006993655) | FAIL: same export defect; image and independent CPU jobs SKIPPED |

The source job ran on a genuine GitHub-hosted Ubuntu **24.04.5 LTS**, image
`20261026.354.1`, kernel `7.0.0-1017-azure`, Python `3.12.15`, Docker `28.0.4`.
Both runs passed frozen lock/install, Ruff/format, Black, MyPy, **109 tests / one
skipped**, tracked source/private-path checks, exact source archive/current/history
secret checks, development license inventory, zero-finding Python audit, Python
SBOM, Compose validation and **one real Qdrant contract test** using fixture vectors.
These are genuine source-job results; the overall job is FAIL.

`Verify exported reports` then raised `ValueError: binary or oversized source
artifact`. Local reproduction identifies default pytest parameter IDs containing
resource-limit payloads: JUnit is **6,407,084 bytes**, with testcase names up to
4,194,361 characters, versus the unchanged **2,000,000-byte** artifact limit.
The retained local XML has no NUL bytes. Its exact hash is in the report; remote
XML bytes are unavailable because upload correctly stayed blocked. This is an
evidence-generation defect, not a passing security result. No regression correction
was applied after the stop instruction took effect.

Both artifact APIs returned **zero artifacts**. Complete run logs were downloaded;
their ZIP CRCs and local SHA-256 checksums were verified. These log ZIPs are not
workflow artifacts: artifact download/checksum acceptance is **NOT_AVAILABLE**.
Raw local JUnit, logs, API responses and original scans remain under ignored
`.local/followup-20261030/`, with hashes in the report. No credentials/model/state
directories were exported.

The **independent CPU/model campaign did not start**: no hosted model download,
embedding output, Qdrant acceptance state or citations exist for it. Its one-campaign
authorization remains unconsumed. RAG-20 stays BLOCKED. The exact approved model is
`sentence-transformers/all-MiniLM-L6-v2`, revision
`10dbd2f06a8baf40ad285b037edda610c1b9a57c`, ONNX SHA-256
`6fd5d72fe4589f189f8ebc006442dbb529bb7ce38f8082112682524616046452`.
The older local 34-check campaign below remains historical evidence only.

Before push, the same 109-test suite, separate real Qdrant test and source/tooling
gates passed locally. All three actual local images were rebuilt, inventoried as
applicable, and scanned for vulnerabilities/licenses/SBOM; core config smoke passed.
Development Python inventory covers 92 packages with zero unknown licenses;
core/UI runtime Python license gates passed. Raw OS/application license scans and
SBOMs are retained separately; this is no blanket legal certification. The pushed
source tar SHA-256 is
`7fa57545faeb9a0b7508c90161bcaa5457db450f1354464cadc15d9fb27f386c`.
New local image IDs/labels and raw scan checksums are recorded in the report,
distinct from the preserved historical images below. There was no fresh local
model campaign in this follow-up.

**Exact original FAIL:** RAG-21 requires “Locked CI passes unit/integration/security/CLI/image/license
checks without inference.” The original failure was actual image gates exiting 1
on Debian OS findings, with no failing deterministic RAG function test identified.
Stable/security package candidates equal installed versions; reviewed Debian fixes
remain in testing/unstable. No small supported stable update was available, so no
base migration or security-policy change was applied. Current local findings remain
**core 44 HIGH / Qdrant 43 HIGH / optional UI 44 HIGH**, zero CRITICAL; each image
has eight distinct HIGH CVEs. Counts are package findings per image, never a summed
unique-CVE count. DB identity and HIGH records match the original scans. Non-root,
missing affected components and Compose restrictions are disclosed mitigations,
not exceptions. Raw CVEs, thresholds and gates remain unchanged. RAG-21 now also
includes the newly observed report-export failure. Remote image scans were SKIPPED,
so no refreshed remote vulnerability result is claimed.

**Source-only v0.1.0 preview recommendation: NO-GO pending correction and verification.**
The source test results are positive, but the new export defect prevents verifiable
CI artifacts and the independent CPU campaign is incomplete. The smallest proposed
next correction is short explicit pytest IDs for large payload cases plus a bounded
JUnit regression, preserving payloads/assertions and the 2 MB guard. Resuming also
needs a one-shot CPU trigger on this existing Draft PR: its `opened` event already
passed, so a normal synchronize event will not run the model job. No second PR or
old-code rerun was attempted. Work stops for the user's decision as instructed.

**Docker image approval remains NO-GO** independently of source readiness. LIVE
generation remains RAG-15 BLOCKED; the [separate authorization proposal](LIVE-LLM-AUTHORIZATION-PROPOSAL.md)
is prepared, with no provider request made. No merge, tag, release, deployment,
paid/generative call or image publication occurred.

## Preserved original local handoff

Local implementation and evidence are delivered. **Publication is not authorized.**
The authoritative RAG-01..24 conditions in SPEC-001 are unchanged. The plan remains
active because LIVE generation, independent host qualification, remote CI and image
security signoff are incomplete. This ledger deliberately does not call those PASS.

## Tested identities

- Original baseline: `74931fedcf99408e8b15b9052c0e8aed1fd6d8fc`; history retained.
- **F** (final runtime/packaging): `02ad20787fd5a8c475aa0efa2e0802e98fb74d8b`.
- **U** (final tests and independently cloned install): `0e476bd16ec75c189c58616b4f4eae9688acfed7`. Its only change from F is a startup-security test. Subsequent delivery commits contain documentation/evidence only; compare production paths against F before release.
- **L** (one approved real-model campaign): ingest/retrieval/crash at `7edabab7990945fa3e960d912d24179090e47b37`; corrected read-only restore and final verification at `657cb5ceb3b92a0f46d743700387d21103351f7d`. All 34 checks passed in the same retained disposable campaign `spec001-b475944503`. No model was reacquired and no generation/provider call occurred.
- **A** (attestation): the preserved CPU-tested container identifies image `sha256:707303da9d3ad0dc3b848abf9d7b7e52d341e3578b9289e2979158bd6def4158`. All 2,686 executable/library/license files match the final runtime image. Two installer metadata files differ: only numeric `uv_cache.json` timestamps and their RECORD digest. These differences are disclosed; images are **not** claimed byte-identical. The Qdrant executable SHA-256 is identical across campaign/final images. See [attestation](evidence/runtime-attestation.json).

| Final local artifact (Linux amd64, UID 10001) | OCI image index digest |
| --- | --- |
| Core | `sha256:1dcee1bdcff9537a4ad508862f3967ff329335fbb4f71c7c29cbd28fe5346640` |
| Qdrant derivative | `sha256:d9bbc4b11a2a7ae6ca86849280131d7c134a84602ae10317d118cc2a1cb4d647` |
| Optional UI | `sha256:f3cbbbdb849765cd0290f25d3c1dca69f71d4f6d5499b59b0734d9674d850e01` |

These are local OCI descriptors/RepoDigest metadata, **not evidence of registry
publication**. All OCI source labels identify F. See [provenance](evidence/provenance.json)
and [locked image inventory](evidence/image-inventory.json). The exact final source
archive/file manifest and checksums are retained under `.local/artifacts/`; they
are generated after the evidence commit to avoid a self-referential manifest.

## Commands and evidence keys

| Key | Executed command / scope | Evidence |
| --- | --- | --- |
| U | `uv sync --frozen`; `uv run pytest -q --junitxml=.local/junit-final.xml`; `uv run ruff check .`; `uv run ruff format --check rag_core scripts tests` | [unit tests](evidence/unit-tests.json): **99 passed, 1 skipped**, zero failures/errors; network forbidden in deterministic tests. The skipped real-Qdrant test is run separately as Q. |
| Q | `uv run python scripts/ci_qdrant.py` against a fresh disposable actual Qdrant image | `.local/qdrant-contract-final.log`: **1 passed**, fixture vectors only, no inference. Image F. |
| C | `git clone --no-local --branch feat/spec-001-oss-rag-core ...`; fresh venv; locked install, tests, source inventory, CLI init/help | [clean clone](evidence/clean-clone.json): U, all six checks PASS, 99 passed/1 skipped, no tracked models/databases or host config. A separate cache was cold-verified at F, then reused only by this task. |
| L | `uv run python scripts/isolated_acceptance.py --approved-local-model-test --model-dir .local/models/minilm-10dbd2f --evidence docs/release/evidence/real-cpu-qdrant.json` and same-project continuation scripts | [real CPU/Qdrant report](evidence/real-cpu-qdrant.json): 34 PASS, individual tested source/image identities and failed attempts retained. Resume project: `spec001-b475944503`; continuations: `resume_restore_acceptance.py`, `verify_restored_campaign.py`, each with the explicit approved-test flag and same project/evidence/model directory. |
| I | `docker build --network=host --build-arg SOURCE_REVISION=F ...`; `uv run python scripts/image_inventory.py workspace-rag-core:local` | F; image inventory enforces non-root, no compiler/Git/pip/model/data/config payload and exact locked runtime distributions. Build host-network exception resolved ambient bridge DNS only; failed logs remain `.local/build/`. |
| S | `uv run python scripts/source_gate.py`; `git archive`; `uv run python scripts/verify_archive.py ARCHIVE MANIFEST`; gitleaks exact archive scan and `scripts/history_secret_gate.py` | Final tracked/archive manifests in `.local/artifacts/`; current source scan has zero findings. Full history has exactly one reviewed public tokenizer Git-hash false positive, not a credential. [Review](evidence/history-secret-review.json); unknown findings fail. No detector rules/commits are disabled. |
| D | `uv run pip-audit --require-hashes --disable-pip --no-deps -r requirements.txt`; `cyclonedx-py requirements`; `scripts/license_gate.py` for development and actual images | [Python audit](evidence/python-audit.json): zero known findings. [Development inventory](license-inventory.json), [runtime](runtime-license-inventory.json), [UI](ui-license-inventory.json), [Python SBOM](evidence/python-sbom.json). |
| V | Actual Trivy image scans and CycloneDX generation; `trivy image --scanners vuln --severity HIGH,CRITICAL --exit-code 1` on all three final images | [Raw-report hashes, counts, DB identity](evidence/image-security.json), [actual nonzero gate exits](evidence/image-gate-exits.json). Raw JSON and actual OS/application SBOMs: `.local/scans/{core,qdrant,ui}.{json,cdx.json}`. |
| UI | Read-only/no-data-mount optional UI container, GET `/` and `/_stcore/health` | [HTTP smoke](evidence/ui-smoke.json), F: PASS. Browser interaction is NOT_RUN; backend ACL is independently covered by U/L. No UI search/generation was run. |

## Exact acceptance statuses

Status scope is the complete authoritative criterion, not merely its easiest subtest.
F/U/L/A above supply exact source/image identities for every referenced evidence key.

| ID | Status | Evidence and limits |
| --- | --- | --- |
| RAG-01 | PASS | C + I + S: independent locked clean-clone install, exact source/archive and actual locked image inventory. |
| RAG-02 | PASS | U production-embedder startup regression forbids loading/inference; default worker/health starts with no workspace seed. L starts actual images without acquisition/provider calls. |
| RAG-03 | PASS | U private-init permissions, no DB/account/data seed, overwrite refusal and symlink checks; C actual CLI init. |
| RAG-04 | PASS | U iterates all sensitive routes and rejects anonymous/placeholder auth; L actual anonymous rejection; private missing/invalid config fails closed. |
| RAG-05 | PASS | U UUID/slug/filename traversal, encoded separators, Unicode aliases, collision, symlink and no-follow import tests. Server IDs are issued, not inferred from names. |
| RAG-06 | PASS | U every content/job/upload/export/chunk/event/delete route with two capabilities; L actual cross-workspace search/delete denial and restored ACL checks. Owner intentionally administers all workspaces. |
| RAG-07 | PASS | U file/MIME/JSON/chunked body/text/page/archive/CPU/deadline bounds; stdin and no-follow local import; L actual isolated TXT/PDF/DOCX extraction. |
| RAG-08 | PASS | U durable checkpoint/recovery/idempotence; L actual duplicate upload, process restart and RUNNING-worker SIGKILL recovery. Immutable documents are content-addressed; same filename with new content adds a version, without overwriting an original. |
| RAG-09 | PASS | U partial Qdrant-write failure and cancellation immediately before publication; committed-manifest filtering hides staged points. L real worker crash preserves prior acknowledged state and completes idempotently. |
| RAG-10 | PASS | U + Q + L: no ingest reset/delete path; retries preserve collections; destructive scope/confirmation audited. L CLI deletes only a newly created empty trial workspace. |
| RAG-11 | PASS | L + A: approved official pinned MiniLM ONNX, CPU-only pooling/normalization reference, real Qdrant, synthetic TXT/PDF/DOCX corpus, persisted retrieval/citations. No fixture satisfies this row. |
| RAG-12 | PASS | U reproducible BM25/RRF/term-coverage rerank and opt-out; Q actual server dimension mismatch/filter contracts; L dense+BM25 provenance; A final runtime code/binary equivalence. |
| RAG-13 | PASS | L actual source byte/hash download, persisted chunks and PDF page 2; TXT/DOCX page null, no fabricated URL; actual unrelated query returns no_match. U failure/no-match integrity. |
| RAG-14 | PASS | U real-adapter mock HTTP contracts for disabled/default, bounded calls/deadline/tokens/response, hostile text and invalid citations; L generation_disabled. No production fixture or fake fallback. |
| RAG-15 | BLOCKED | **LIVE generation not authorized**, not run. No external provider/credential/availability/answer-quality claim. Separate approval and privately configured credentials are required. |
| RAG-16 | PASS | L actual authenticated CLI/API doctor/create/list/ingest/job/search/delete journeys; U route ACL/CLI validation; optional UI is API-only, no privileged mounts/Qdrant network. UI HTTP startup PASS; visual browser UX NOT_RUN. |
| RAG-17 | PASS | U error/caplog/stdout redaction with secret/content/path sentinels, including CLI storage failures; default access/prompt traces absent; authenticated fixed-schema events only. |
| RAG-18 | PASS | L actual Qdrant stop -> readiness/search 503; restart restores identical committed retrieval. U/Q outage and dimension contracts. |
| RAG-19 | PASS | L actual private logical backup and read-only restore to a separate Qdrant, exact source hashes/manifests/jobs/capability hashes, ranking within 1e-6 float round-trip tolerance. Original documents/volumes untouched. |
| RAG-20 | BLOCKED | Local secure CPU Compose verified by L/I. The follow-up source job ran on genuine hosted Ubuntu, but its prerequisite export failed and independent-cpu was SKIPPED. No independent real-model stack qualification is claimed. |
| RAG-21 | FAIL | Original actual image gates exit **1** (V; unchanged 44/43/44 HIGH). Follow-up remote source subchecks pass, but overall CI FAILS at evidence export; remote image jobs SKIPPED. Exact runs and new defect are recorded above. |
| RAG-22 | PASS | S exact tracked-file/archive inventory and adversarial bypass tests; I excludes private/model/index data and unused bundled ONNX demo graphs; no operator fixtures in source. One historical public-hash detector finding independently reviewed, not hidden. |
| RAG-23 | PASS | C + L README/CLI walkthrough; required architecture/self-host/provider/security/backup/contribution/license/NOTICE/release docs and inventories present. No production, GPU, OCR, provider-quality or benchmark claims. |
| RAG-24 | PASS | This explicit review separates source preview, actual model evidence, LIVE provider scope, remote CI and image security. Neither publication decision is inferred from deterministic tests. |

Totals: **21 PASS, 2 BLOCKED, 1 FAIL**. Previous PASS rows retain their stated
historical evidence scope; they are not a claim that the full current hosted stack
was requalified. No acceptance criterion was edited to obtain PASS.

## Model integrity and the one approved campaign

Official repository: `sentence-transformers/all-MiniLM-L6-v2`.
Revision: `10dbd2f06a8baf40ad285b037edda610c1b9a57c`, Apache-2.0.
Only ONNX (90,405,214 bytes) and tokenizer (466,247 bytes) were acquired into ignored
private `.local/models/minilm-10dbd2f`. [Acquisition proof](evidence/model-acquisition.json).

- ONNX SHA-256: `6fd5d72fe4589f189f8ebc006442dbb529bb7ce38f8082112682524616046452`.
- `be50c3628f2bf5bb5e3a7f17b1f74611b2561a3a27eeab05e5aa30f411572037` is the tokenizer SHA-256.
- Official revision/LFS/Git-blob integrity checked at acquisition; runtime checks independently repeated.
- 384-dimensional masked mean pooling, L2 norms and padded-batch/single invariance verified against an independent einsum reference; maximum observed error about `1.8e-8`; CPUExecutionProvider only.
- Five committed chunks across synthetic TXT, two PDF pages, DOCX and recovery text. Raw corpus hashes and actual source/page/chunk proofs in L. No personal document, original README dataset or chat transcript used.
- Early terminal failures (read-only `docker cp`, WAL sidecars, local Docker address-pool exhaustion) are retained in L's prior attempts and private logs. Stdin import and standalone snapshot restore were corrected. Only the same retained campaign/projects were resumed. No successful test is claimed for a failed attempt.
- To free a Docker subnet, only the already-stopped disposable original API container and its empty ingress network were removed after saving inspect/log evidence. No operator container/network or any document/volume was deleted. All campaign data, backup directories and Qdrant volumes remain private and stopped.

## Original publication-readiness review (historical; follow-up decision above)

**Source-preview decision: NO-GO for publication now.** Local source, model, ACL,
license and clean-clone evidence is positive, but independent clean-host qualification
and actual remote CI remain incomplete. No push/merge/Git tag/source release was
performed or authorized. A reviewer must separately authorize the next publication
steps; this decision is independent of the binary-image decision.

**Image-security decision: NO-GO.** Trivy DB updated `2026-10-30T01:01:11Z`; final
core **44 HIGH**, Qdrant **43 HIGH**, UI **44 HIGH** OS package findings; zero CRITICAL.
No fix version is listed for those HIGH findings in this scan. Lower severities and
Rust SBOM findings remain in the raw reports. Python findings are zero after updating
pypdf/Starlette and optional Pillow/PyArrow, removing unused pip/demo graphs, and
excluding the entire unused Qdrant web UI component (not merely its SBOM). No CVE
suppression, severity downgrade or gate bypass was used. Absence of a listed fix is
not a vulnerability waiver; exploitability and upstream remediation still need review.

Residual product limits: single-instance SQLite and trusted host/owner, no SaaS or
SSO claim, immutable append of new content instead of automatic in-place replacement,
no OCR/GPU validation, English MiniLM/truncation/threshold quality limits, logical
backup RAM/storage requirements, and citation membership rather than semantic proof
of every generated sentence. UI browser UX and LIVE remote generation are untested.
The follow-up separately authorized one pristine-host/model campaign, which did
not start because its source prerequisite failed. No source/image publication,
remote deployment, live provider check or paid request is authorized by these findings.
