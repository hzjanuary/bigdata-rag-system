# SPEC-001 verification ledger — 2026-10-30

## Final remediation source verified — STOP before cpuq2 activation

Final remote PR #1 head: **`287212be8f5683221d2449158331e59d4c639c15`**.
Exact future owner label: **`cpuq2:287212be8f5683221d2449158331e59d4c639c15`**.
No cpuq2 label or marker was created/applied; this campaign is not started/consumed.

| Genuine final run | Observed conclusion |
| --- | --- |
| [Source push41038452232](https://github.com/hzjanuary/bigdata-rag-system/actions/runs/41038452232) | source PASS, 194 tests / one skipped; images FAIL only at known security gates |
| [Source PR41038457036](https://github.com/hzjanuary/bigdata-rag-system/actions/runs/41038457036) | source PASS, 194 tests / one skipped; same image gate results |
| [cpuq2 configuration push41038452175](https://github.com/hzjanuary/bigdata-rag-system/actions/runs/41038452175) | configuration PASS, campaign SKIPPED |
| [cpuq2 configuration PR41038457194](https://github.com/hzjanuary/bigdata-rag-system/actions/runs/41038457194) | configuration PASS, campaign SKIPPED |

All ten final artifacts were downloaded and verified (GitHub ZIP digests/CRC, exact
manifests, every file size/hash and source archive); ten earlier fix artifacts also
remain verified. Final source tar SHA-256:
`95b9ef21d11df4d98678e85bb38b1906f92326394e0b1097426a318535c9e0b6`.
Raw image reports/SBOM/license findings and actual exit1 remain: core44 HIGH,
Qdrant43 HIGH, UI44 HIGH, zero CRITICAL; no new/removed HIGH records or license
changes, no suppression or threshold change. No unexpected source/privacy/integrity
failure. [Complete final evidence](evidence/remediation-campaign-2-ready.json).

Actual read-only audit at final SHA verified 17 accessible runs, the exact old
consumed marker/failure ZIP/receipt/logs and final source ZIP/tar. Old marker
123977248159 and cpuq1 label remain intact; new remediation marker count is zero.
Signed archive ZIP container hashes for logs are recorded per download rather than
assumed byte-stable; original artifact's pinned digest and named log failure remain
mandatory. Private original post-state remains unavailable, with no stronger causal
claim than the diagnosed mechanism.

RAG-12 PASS is supported by original-red/corrected-green process tests, twelve
bit-identical probes, eight exact real CPU API-restart checks and full 41-PASS local
CPU/Qdrant/crash/outage/restore path. This Linux Mint evidence does not qualify the
independent host. RAG-15/20 stay BLOCKED, RAG-21 FAIL; totals **21 PASS / one FAIL /
two BLOCKED**. The additional independent authority is prepared, not consumed.

Campaign `spec001-pr1-cpu-qdrant-remediation-2`; marker
`spec001-cpu-pr1-remediation-2-consumed`. Owner must separately review this exact
head/source evidence and apply the exact cpuq2 label once inside **2026-10-30 10:00
through 2026-10-31 00:00 UTC** (expiry07:00 Vietnam). No automatic retry/extension,
old marker reset or old-label reapplication. [Operator procedure](CPU-CAMPAIGN-2.md).
Admin/retention limits preclude an absolute exactly-once claim; live reservation
write is intentionally not exercised during preparation.

Final evidence documentation is retained in a local commit without another push,
keeping the reviewed activation head stable. No merge/tag/release/image publication,
deployment, generative inference or paid API request occurred. Source-preview
publication remains a separate decision after independent evidence; Docker approval
remains blocked by known OS findings.

## Policy preparation checkpoint before final push (historical)

## Corrected source CI verified; separate remediation policy prepared inactive

Fix source `59a7103314eba9d63863774ca55d65e5f21dc7a5` passed genuine source jobs
in [push41035999451](https://github.com/hzjanuary/bigdata-rag-system/actions/runs/41035999451)
and [PR41036006533](https://github.com/hzjanuary/bigdata-rag-system/actions/runs/41036006533).
Both have 168 PASS / one skipped, actual Qdrant and source/secret/license/audit gates
PASS. All ten artifacts (including inactive configuration) were downloaded/verified.
Image gates remain FAIL on unchanged known HIGH records; no unexpected source defect.

Only after that verification, prepared the separately authorized policy:
`spec001-pr1-cpu-qdrant-remediation-2`, marker
`spec001-cpu-pr1-remediation-2-consumed`, label `cpuq2:<final reviewed full SHA>`.
The exact activation head must be resolved after final policy push/CI. Fixed UTC
window 2026-10-30 10:00 through 2026-10-31 00:00. No label/marker/download/hosted
campaign is triggered in preparation. [Instructions](CPU-CAMPAIGN-2.md).

Actual read-only GitHub audit validated all accessible history, original run/job/
marker, pinned original ZIP checksum/manifests/receipt and named-failure logs, plus
the verified source tar. The old consumed attempt is the ONLY precise exception;
every other attempt/marker/missing record rejects. New-marker reservation remains
before acquisition; receipt/old failure/current head are rechecked. New source ZIP
and tar are verified, not merely trusted by artifact name. No public/private
historical values are reconstructed or reset. Original private post-state limitation
is retained. Tests: **194 PASS / one skipped**; policy mismatch/archive checks and
actionlint pass. No production change beyond canonical BM25 traversal.

[Preparation evidence](evidence/remediation-campaign-2-preparation.json) separates
the local 41-PASS path, verified source CI, old consumed failure and new unconsumed
authority. Next: final normal push and source/inactive CI, exact head/label report,
then STOP for owner action. RAG-12 PASS, RAG-15/20 BLOCKED, RAG-21 FAIL: 21/1/2.

## BM25 corrected: deterministic/local CPU proof complete, source CI pending

The only production change is sorted query-term traversal. The original six-process
regression still fails on preserved original code; the corrected test passes at
seeds 0/1/2/3/7/11. Twelve independent probes produce identical ordered results,
with RRF/dense/reranker and all non-BM25 fields unchanged. No-match and rerank opt-out
controls pass. Local suite: **168 PASS / one skipped**, actual Qdrant contract one
PASS; Ruff/format/Black/MyPy, frozen lock, license92, zero-finding dependency audit
and source/archive/current/history secret gates pass.

Corrected core image plus cached official model completed **41/41 real local CPU/
Qdrant checks**, including eight exact restart diagnostics, outage/retry, actual
RUNNING-worker SIGKILL/recovery and independent backup/restore. Model was not
reacquired. Original failed local startup (exhausted Docker default subnet pools,
zero checks) remains retained; four new explicit nonoverlapping IPAM networks were
created for the new project/restore, without deleting retained state/networks.
[Local evidence](evidence/bm25-remediation-local.json) identifies exact tested source,
image labels/digests, vectors/tolerances, provenance, hashes and every check.

Restart observations contain safe identities/content hashes and exact score deltas
before individual assertions. Full response fingerprints prevent unknown schema
fields from being silently ignored by public projection. Inactive event receipts
now state consumed_by_this_event=false, without incorrectly resetting a historical
campaign budget. No original cpuq1 evidence/marker was changed.

RAG-12 is **PASS on demonstrated corrected behavior**, totals **21 PASS / one FAIL /
two BLOCKED**. RAG-20 is still BLOCKED: this Linux Mint run is local evidence only.
The hosted failure stays consumed/FAIL with its missing post-state limitation.
Next: normal push/source CI; only after successful source evidence prepare the
separately authorized cpuq2 policy. No activation label or new hosted campaign.

## Initial correction checkpoint (historical)

Only production change: canonical BM25 term traversal (`for term in sorted(terms)`).
Formula/parameters/RRF/dense/reranker/schema/ACL/thresholds remain unchanged. Six-seed
regression fails on preserved original source and passes after correction; twelve
fresh processes now give identical outputs. Other ranking fields match the original
probe exactly. Restart diagnostics capture readiness/job/identity/status/order/
provenance/exact scores before individual assertions, with hash-only content and a
strict public projection. No numerical tolerance replaces deterministic checks.

Existing diagnosis/run41029994294/marker evidence is preserved, including the
distinction between reproduced local mechanism and unavailable hosted post-state.
Local source-quality and focused tests pass; corrected full CPU image/model/Qdrant
verification is pending before push. RAG-12 remains FAIL until that proof is recorded.
The owner separately authorizes preparation of one additional campaign; it must
have new cpuq2 identity/marker and a separate exact-SHA owner label after source CI.
No second independent campaign or activation is performed during preparation.

## Consumed hosted campaign 41029994294 — failed restart checkpoint, diagnosed offline

The owner subsequently activated run
[41029994294](https://github.com/hzjanuary/bigdata-rag-system/actions/runs/41029994294)
at ba78e94. Model acquisition/reservation succeeded; 21 checks passed before
`AssertionError: API process restart preserves job and retrieval`. Marker
123977248159 is **consumed and retained**. Raw private runner result was not
uploaded; the checksum-verified artifact contains only pre-restart retrieval.
No original post-restart job/search values can be reconstructed from that artifact.

[Diagnosis](CPU-RUN-41029994294-DIAGNOSIS.md) and
[machine evidence](evidence/cpu-run-41029994294-diagnosis.json) preserve original
hashes/logs and distinguish direct hosted observations from offline reproduction.
Real cached CPU model + local API/Qdrant reproduction retained COMPLETED jobs,
SQLite chunks, vector hashes, readiness, identities/order/citations. Only one BM25
float changed by 4.440892098500626e-16. Pure fresh-process probes isolate unordered
set traversal/non-associative summation as the production mechanism. Original
hosted post-state is unavailable, so its exact operand/delta remains unproven.

A new cross-process regression fails on unchanged production and passes with a
one-line canonical-term-order proposal in an isolated copy. Production is not
patched, committed or pushed. RAG-12 is now FAIL on newly confirmed nondeterminism;
current totals **20 PASS / two FAIL / two BLOCKED**. RAG-15/20 stay BLOCKED and
RAG-21's known image FAIL remains. A fresh independent campaign needs new explicit
authorization; no marker/label/rerun/download or second live campaign occurred.

## Previous operator activation boundary (historical)

Final remote PR #1 head is **`ba78e94d82b7972e96a9bae962cbb8ada73d6619`**.
The exact future operator label is
**`cpuq1:ba78e94d82b7972e96a9bae962cbb8ada73d6619`**.
It was resolved after normal push, not copied from a previous tested revision.
Earlier local evidence commit `1ccf0d0` is preserved in pushed history.

| Actual run at final remote head | Outcome |
| --- | --- |
| [Source/image push 41012209423](https://github.com/hzjanuary/bigdata-rag-system/actions/runs/41012209423) | source PASS; three image jobs FAIL only at known security gate |
| [Source/image PR 41012213478](https://github.com/hzjanuary/bigdata-rag-system/actions/runs/41012213478) | source PASS; three image jobs FAIL only at known security gate |
| [Trigger push 41012209492](https://github.com/hzjanuary/bigdata-rag-system/actions/runs/41012209492) | configuration PASS; campaign SKIPPED |
| [Trigger PR synchronize 41012213570](https://github.com/hzjanuary/bigdata-rag-system/actions/runs/41012213570) | configuration PASS; campaign SKIPPED |

Both source jobs passed 154 tests / one skipped, actual Qdrant contract, lock,
quality, source/archive/current/history secrets, license/audit/SBOM and Compose.
JUnit is 17,978 / 17,977 bytes, valid unique-name XML under the unchanged 2 MB gate.
All **10 artifacts** were downloaded and verified against GitHub ZIP digests, CRCs,
exact checksum manifests and every file size/hash. Six actual image reports retain
44/43/44 HIGH (core/Qdrant/UI), zero CRITICAL, identical HIGH/fix/license records;
actual security exits are 1. No severity change, CVE suppression or image approval.

Downloaded inactive receipts explicitly show `consumed=false` and
`model_download_started=false`. Read-only API checks confirm PR labels empty,
consumption marker count zero, and installed workflow bytes equal reviewed local
bytes. No activation label/marker/model download/CPU campaign/generative call was
created or executed. Source/trigger tests establish valid inactive configuration;
live label handling/check-write permission is deliberately untested at this boundary.

Complete machine-readable [remote evidence](evidence/cpu-trigger-remote.json) records
all run IDs, artifact digests, source/image identities and retained log hashes.
[Operator instructions](CPU-CAMPAIGN-TRIGGER.md) describe exact-head history/source
checks, the reservation, fixed expiry and replay limits. Operator must review this
head and apply the exact label separately, as `hzjanuary`, to PR #1 once before
**2026-10-31 00:00 UTC (07:00 Vietnam)**. Missing history/evidence or any mismatch
rejects before acquisition; no rerun or automatic extension fallback. Administrative
history deletion/policy changes preclude a mathematical exactly-once guarantee.

Final evidence is committed locally after remote verification without another
push, keeping this activation head stable. RAG-15 and RAG-20 remain BLOCKED;
RAG-21 remains FAIL. Totals **21 PASS / 1 FAIL / 2 BLOCKED**. Stop before activation;
no source/image release, merge, tag, deployment or generative campaign is authorized.

## Trigger local verification checkpoint before push (historical)

Explicit authorization now covers implementing/pushing the trigger, without
activation. `.github/workflows/spec001-cpu-once.yml` and `scripts/cpu_campaign.py`
replace the obsolete opened-only CPU job; source/image CI and all severity/artifact
gates are unchanged. Push/synchronize run only a configuration check, whose receipt
states consumed=false; the campaign job requires the owner label on PR #1.

The template's old ancestor allowance is removed. Label format is
`cpuq1:<exact lowercase 40-character current PR head SHA>`; the final SHA is resolved
AFTER push, and must equal label/event/checkout/live-PR/source-CI/receipt identities.
No embedded old source SHA or workflow_dispatch/default-branch assumption.

Complete read-only Actions/job-attempt history and exact-SHA source export proof
are required. Missing/incomplete history, any prior unskipped campaign job, marker,
rerun, stale SHA, wrong owner/PR/repo/branch or API failure rejects before model
acquisition. One concurrency group and a persistent pre-download reservation marker
limit replay; admin deletion/retention/permission changes remain documented limits.
The original fixed expiry stays 2026-10-31 00:00 UTC; no automatic retry/extension.

Local checks: 154 deterministic PASS / one skipped (40 new policy regressions),
separate actual Qdrant contract one PASS, lock/Ruff/Black/MyPy, 92-package license
inventory and zero-finding dependency audit. Official actionlint v1.7.12 syntax and
event-expression checks PASS; tool archive SHA-256 verified against official release
metadata. Existing acquisition/acceptance and runtime/packaging inputs unchanged.
Public acceptance projection strips raw SQLite job rows/configuration and preserves
synthetic citations/vectors/collection summaries, individual checks and measured time.
No label, marker, acquisition or independent campaign was executed. RAG-15/20 remain
BLOCKED, RAG-21 FAIL; 21 PASS / 1 FAIL / 2 BLOCKED. Remote outcome will be appended
after genuine CI, then work stops at the separate operator label action.

## JUnit correction: remote verification complete

Normal push preserved `a9b68db` and advanced existing Draft PR #1 to exact tested
SHA **`d54b899d665b04dff2db3bd8b7415f96d8b36c9a`**. No active workflow, runtime or
packaging input changed. Only short `ids` were added to three existing parameter
lists, with five focused regressions. [Local evidence](evidence/junit-correction.json)
and [remote evidence](evidence/junit-correction-ci.json) retain the original failure,
before/after hashes, job results, every artifact digest and raw-report checksum.

The expansion was caused by pytest's default IDs serializing synthetic byte
payloads in parser, source-artifact and stdin tests. Original testcase names were
200,048 / 2,000,050 / 4,194,361 characters respectively. Adding IDs only to the parser
would still leave the report oversized. AST comparison proves the three original
files are otherwise identical: no payload, case, exception or assertion changed.

| Evidence | Original retained | Fresh before fix | Local after fix | Both hosted runs |
| --- | --- | --- | --- | --- |
| Full-suite JUnit bytes | 6,407,084 | 6,407,083 | 13,067 | 13,082 each |
| Export guard | FAIL | FAIL | PASS | PASS |

Timing/path serialization explains small size differences; the artifact limit is
still **2,000,000 bytes**. The full actual CI pytest command was used. Corrected XML
has 115 unique classname/name pairs, maximum name length 97, **114 PASS / one
skipped / zero errors/failures**; every previous case remains. The focused regression
fails on the retained detached `a9b68db` checkout and passes after correction. It
executes all 23 affected cases, checks actual XML/checksum export, preserves real
child-suite failure/skip details, and rejects oversized/unauthorized/binary exports.
No failure truncation or JUnit/security exclusion was introduced.

| Genuine Actions run at tested SHA | Source | Core / Qdrant / UI | Independent CPU |
| --- | --- | --- | --- |
| [Push 41008646193](https://github.com/hzjanuary/bigdata-rag-system/actions/runs/41008646193) | PASS | FAIL / FAIL / FAIL | SKIPPED |
| [PR synchronize 41008651605](https://github.com/hzjanuary/bigdata-rag-system/actions/runs/41008651605) | PASS | FAIL / FAIL / FAIL | SKIPPED |

Both source jobs passed full deterministic tests, actual Qdrant integration,
frozen lock, Ruff/format/Black/MyPy, source/archive/private-path/current/history
secret checks, license inventory, zero-finding Python audit, SBOM and Compose.
All **eight artifacts uploaded and were downloaded**: one source plus three image
artifacts per run. GitHub ZIP digests, CRCs, exact manifest membership and every
file byte size/SHA-256 passed verification. Both source archives match the 94-file
manifest at tested SHA; archive SHA-256 is
`71d0ec6409dde0a07df21d5bc477cfcba6dcec16a5ac455053a6dddefa38f2df`.
Raw ZIPs, extracted reports, full logs and API responses remain under ignored
`.local/junit-resume-20261030/remote/`; their hashes are in the remote evidence.

All six actual hosted image builds/license/SBOM/export steps completed; each image
job failed **only** its unchanged HIGH/CRITICAL gate, actual exit **1** confirmed
in downloaded logs. Per run: core **44 HIGH**, Qdrant **43 HIGH**, optional UI
**44 HIGH**, zero CRITICAL. Each has eight distinct HIGH CVEs; package findings
are not summed into an invented unique-CVE count. Exact ID/package/version/severity/
fix tuples and license records match preserved local scans; no new finding or
exception. Hosted scanners fetched fresh DBs, but standalone DB metadata was not
exported: identical DB identity is not claimed. Raw scanner reports remain intact.

Local checks rerun: **114 PASS / one skipped**, five focused regressions, separate
actual Qdrant contract **one PASS**, lock, Ruff/format/Black/MyPy (13 modules), source/
archive/current/history secret gates, 92-package approved license inventory and
zero-finding dependency audit. Existing disposable Qdrant image was reused; no
local release-image rebuild, model acquisition or CPU/model rerun occurred.

**Independent campaign: NOT_STARTED, authorization unconsumed.** Both hosted model
jobs SKIPPED as required by the unchanged opened-only condition. The inert
[one-time workflow template](cpu-once.workflow.yml) and [operator instructions](CPU-CAMPAIGN-TRIGGER.md)
are prepared outside `.github/workflows`. They bind PR #1 and exact tested SHA,
require the owner's SHA-specific label action, serialize runs, block reruns, reserve
a persistent check marker before acquisition and expire at 2026-10-31 00:00 UTC.
YAML and both embedded Python blocks were statically validated; no live check-write
permission/trigger claim, installation, label action or consumption occurred. Admin
deletion/modification cannot be prevented absolutely; final operator review,
installation and explicit label action are required. No dispatch/default-branch
assumption, new PR or automatic synchronize campaign is used.

**Source-only preview recommendation:** source is reviewable and remote source CI
is PASS; final preview readiness remains pending the independent CPU campaign and
an explicit source-release decision. **Docker image approval remains NO-GO** due
known HIGH findings. RAG-15/20 stay BLOCKED and RAG-21 stays FAIL, totals unchanged
at **21 PASS / 1 FAIL / 2 BLOCKED**. The new JUnit defect is corrected with genuine
remote artifact evidence. No merge/tag/release/deploy/image publication/generative
call occurred. Final docs/template are committed locally after CI, without another
push; the remote tested SHA above is kept distinct from the local evidence HEAD.
Final draft secret scanning detected one public-prose false positive in the trigger
instructions; the wording was rephrased and scan passed. Original redacted finding,
public-line hash and both scan logs are preserved in the remote evidence report.
No detector rule, allowlist or security exception changed.

## Local correction checkpoint before push (historical)

**JUnit correction resumed under explicit authorization.** Historical failure and
stop evidence below remain unchanged. Only three parametrized-test ID lists and
focused regression tests changed; runtime, packaging, workflow, payloads/assertions
and the 2,000,000-byte artifact guard are unchanged. Local full-suite JUnit is now
13,067 bytes: **114 PASS / one skipped**, and the existing export gate accepts it.
The regression fails against preserved commit `a9b68db` and passes after correction.
One real Qdrant contract passes separately; no image rebuild/model download/inference
was performed. [Local correction evidence](evidence/junit-correction.json) records
AST preservation, report hashes and reporting/security regressions. A normal push
to existing Draft PR #1 and genuine remote verification are pending. The one-time
independent CPU campaign remains unconsumed and will not be started automatically.

## Preserved previous remote stop checkpoint

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
| RAG-12 | PASS | Canonical term traversal fixed the confirmed defect. Original regression fails; corrected six-seed and twelve-process checks pass with exact full outputs. Real cached CPU/Qdrant API restart has unchanged identities/order/citations and exactly identical ranking scores; RRF/dense/rerank/no-match controls pass. See bm25-remediation-local.json; original failure remains historical evidence. |
| RAG-13 | PASS | L actual source byte/hash download, persisted chunks and PDF page 2; TXT/DOCX page null, no fabricated URL; actual unrelated query returns no_match. U failure/no-match integrity. |
| RAG-14 | PASS | U real-adapter mock HTTP contracts for disabled/default, bounded calls/deadline/tokens/response, hostile text and invalid citations; L generation_disabled. No production fixture or fake fallback. |
| RAG-15 | BLOCKED | **LIVE generation not authorized**, not run. No external provider/credential/availability/answer-quality claim. Separate approval and privately configured credentials are required. |
| RAG-16 | PASS | L actual authenticated CLI/API doctor/create/list/ingest/job/search/delete journeys; U route ACL/CLI validation; optional UI is API-only, no privileged mounts/Qdrant network. UI HTTP startup PASS; visual browser UX NOT_RUN. |
| RAG-17 | PASS | U error/caplog/stdout redaction with secret/content/path sentinels, including CLI storage failures; default access/prompt traces absent; authenticated fixed-schema events only. |
| RAG-18 | PASS | L actual Qdrant stop -> readiness/search 503; restart restores identical committed retrieval. U/Q outage and dimension contracts. |
| RAG-19 | PASS | L actual private logical backup and read-only restore to a separate Qdrant, exact source hashes/manifests/jobs/capability hashes, ranking within 1e-6 float round-trip tolerance. Original documents/volumes untouched. |
| RAG-20 | BLOCKED | Hosted campaign 41029994294 consumed authorization and passed 21 checks, then failed restart assertion before remaining outage/crash/restore scenarios. Local diagnosis is not independent-host completion. New explicit campaign authorization required; preserve original marker. |
| RAG-21 | FAIL | Latest source jobs/artifacts PASS in runs 41012209423/41012213478 at ba78e94 (154 PASS, one skipped). All three actual hosted image jobs per run execute and security gates exit **1**, unchanged 44/43/44 HIGH. Raw reports/checksums preserved, no suppression. |
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
