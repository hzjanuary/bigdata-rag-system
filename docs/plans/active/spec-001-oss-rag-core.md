# SPEC-001 execution plan

Current checkpoint: independent campaign41040402221 at runtime287212b verified
41/41 PASS, attempt1; artifact ZIP and every manifest size/hash verified. RAG20 PASS,
RAG12 PASS, RAG15 BLOCKED, RAG21 FAIL: **22 PASS / one FAIL / one BLOCKED**.
SOURCE-ONLY READY FOR OWNER DECISION; plan remains active. STOP before any push of
new reconciliation evidence, Draft transition, merge/tag/release/image publication.
Both CPU authorizations are consumed; no rerun or additional campaign.

Started 2026-10-29. Branch: `feat/spec-001-oss-rag-core`.
Authoritative requirements: `docs/specs/SPEC-001-open-source-rag-core.md` (unchanged).

## Baseline evidence, before implementation

- HEAD and origin/main: `74931fedcf99408e8b15b9052c0e8aed1fd6d8fc`; 17 historical commits; no tags. No history rewrite or remote mutation.
- Worktree initially contained only two untracked operator-provided planning files: SPEC-001 and OSS-ROADMAP. Preserve both.
- All 21 tracked files inventoried. No operator documents, upload/database directories, model caches or credentials in checkout. No `.env`. Git history scan: gitleaks container, `git /repo --redact=100 --log-opts=--all`, 17 commits / 262574 bytes, zero findings. This is a detector result, not a proof of absence.
- Static regression: API has no authentication dependencies; wildcard credentialed CORS; `/pipeline/start` accepts `source_dir` and `reset_db=True`; upload reads whole file; deletion directly exposed. Both API entrypoints and Streamlit bypass security. Embedding initialization may download weights. Groq is required and enrichment can make calls. Qdrant deletion is part of ingestion. Compose publishes Qdrant on all interfaces, disables UI CORS/XSRF, uses unpinned CUDA runtime.
- Docker 29.9.2 and Python 3.12.3 available. Existing unrelated containers/volumes must remain untouched. Qdrant v1.13.4 available locally; no approved embedding download yet.

## Decisions and sequence

1. S0: record baseline, threat model and unmodified full acceptance matrix before runtime edits. Commit.
2. S1: replace unsafe legacy executable paths with thin wrappers over typed config, private bootstrap, authenticated API/CLI and durable SQLite domain. Single operator owner; workspace-scoped capabilities for clients. No account seed by migration.
3. S2: bounded isolated extraction; durable serialized worker; idempotent documents; staged Qdrant points and transactional SQLite publication. Explicit local ONNX embedding installation, dense/BM25 RRF and deterministic bounded reranker. No implicit resets.
4. S3: optional explicit OpenAI-compatible adapter with hard ceilings and citation validation; authenticated opt-in UI; sanitized audit; restart/cancel/backup tests.
5. S4: lock/install, non-root CPU image/Compose, exact source/artifact/secret gates, SBOM/license/security scans, CI and complete operator docs. Disposable real Qdrant and clean-clone runs. No remote CI/publish without approval.
6. Audit RAG-01..24 individually with exact tested SHA/image and raw evidence. Commit coherent changes; preserve active plan if approval-dependent/live gates remain blocked.

## Acceptance tracking

The full matrix is in `docs/release/verification.md`. Each criterion starts NOT_RUN. Test doubles cannot satisfy RAG-11/15/18/20. Source preview and image security have independent decisions.

## Original external constraints / pending evidence (follow-up supersedes authorization)

- RAG-11: approved acquisition and ONE same-project CPU/Qdrant campaign are COMPLETE (34 checks); no further model campaign authorized.
- RAG-15: LIVE generation deliberately BLOCKED until separate approval and operator credentials; do not request secrets in chat.
- RAG-20: local secure CPU Compose verified; a separate pristine Linux host/VM remains unqualified and needs a separately authorized environment/model campaign.
- RAG-21: remote GitHub CI requires a push, prohibited in current scope. Local image gates fail on 44/43/44 HIGH OS findings (core/Qdrant/UI), no listed fixes; image distribution remains NO-GO.
- Publication, tags, remote deploy and touching existing volumes remain prohibited.

## Execution log

### Final independent acceptance and source-only decision (2026-10-30)

- Verified actual hosted Ubuntu24.04 run41040402221 at exact runtime287212be8f5683221d2449158331e59d4c639c15,
  attempt1, CPU-only pinned MiniLM revision/hash, all41 real checks PASS including
  exact restart ranking, isolation/citations, worker crash, outage/retry and separate
  SQLite/Qdrant backup/restore. ZIP30a57bc2c2a7df2a6b0399936134a05e88d5df8da00ff8465e05f9458734164c,
  CRC/exact manifest/file sizes/SHA-256 verified; complete actual logs retained.
- RAG20's unchanged original loopback/private-network/clean-Linux requirement is
  met by reviewed default Compose source and fresh hosted execution. RAG12 remains
  PASS; 22/1/1. Do not equate CPU success with generative/image qualification.
- Preserved cpuq1 run41029994294/marker123977248159 consumed FAIL and cpuq2
  marker124011605279 consumed PASS evidence. Original private operands remain
  unavailable. No marker/label reset, model acquisition or campaign during review.
- Preserved unpushed e2dc537 and runtime/packaging identity. New README, SECURITY,
  checklist, ledger and JSON are documentation/evidence-only. Development license
  inventory now includes all92 existing locked tools; no dependency/lock change.
- Local194 PASS/one skipped, actual Qdrant contract1 PASS; quality/lock/audit/license,
  Compose and final source/archive/secret checks recorded in verification.md.
  Known host Docker subnet exhaustion retained; successful disposable contract
  probe uses existing bridge without deleting data or changing runtime source.
- Reviewed active main rulesets read-only: required source status/up-to-date PR,
  resolved threads, no force push/deletion/bypass. PR#1 remains open/Draft at287212b.
  Source CI PASS; three image jobs FAIL at unchanged known HIGH gates. No all-green claim.
- Early source-only v0.1.0 pre-release is ready for an explicit owner decision;
  Docker images remain unapproved and RAG15 live generation remains BLOCKED.
  No merge/tag/release/deploy/rename/publication is performed or inferred.

- S0 checkpoint (0b09ca5): baseline/history detector completed before runtime implementation began.

### Local implementation progress (2026-10-30)

- S1/S2/S3 implemented in local runtime commit 8fa3c35 plus the following focused hardening changes: fail-closed ACLs/private bootstrap, durable idempotent manifest/Qdrant indexing, CPU ONNX embeddings, bounded parsers, hybrid retrieval/citations, disabled-by-default real provider adapter, CLI, and private backup/restore.
- User explicitly approved ONE isolated acceptance campaign with the pinned MiniLM ONNX model. Acquired only the ONNX file and tokenizer from the official pinned repository into ignored .local cache; upstream revision, LFS SHA-256 and Git blob integrity verified. No other model or generation authorized.
- Current deterministic tests pass; actual Qdrant contract and final CPU corpus/restart/restore evidence are being gathered. No live model acceptance result is claimed until that campaign completes.
- S4 packaging/docs/CI/gates prepared. Runtime Python vulnerability audit: zero known vulnerabilities after updating the initially vulnerable pypdf/Starlette pins. Initial CPU image OS scan finds inherited Debian HIGH vulnerabilities without listed fixes; retain raw output and keep image-security NO-GO, with no gate bypass.
- Docker 29 internal-only networks suppress host port publishing. Corrected topology: Qdrant internal only, API also attached to an ingress bridge with loopback-only host binding; optional UI on ingress only. The API bridge permits outbound connectivity, while generation stays disabled in config. Docs updated accordingly.
- Previous goal turns classified as progress: runtime, tests and packaging changed authoritative state. No goal-owned acceptance process was live on resume; missing prior process handles were revalidated with OS/container state before restarting checks.

### Delivery audit (2026-10-30)

- Runtime/packaging F: 02ad20787fd5a8c475aa0efa2e0802e98fb74d8b; final tests/independent clone U: 0e476bd16ec75c189c58616b4f4eae9688acfed7. Difference: one startup-security test, no runtime change.
- 99 deterministic tests passed / one actual-Qdrant test skipped in that run; the same real-Qdrant contract passed separately (1). One approved model campaign passed all 34 checks including actual worker SIGKILL, Qdrant stop/restart, source/page/chunk checks and independent backup/restore. All test data/volumes retained, stopped.
- Final images are non-root and inventoried; exact OCI descriptors, labels, model hashes, SBOM/raw scan hashes and runtime-content attestation are in docs/release/evidence/. Full raw OS/image SBOMs and findings remain in ignored .local/scans/.
- Two installer metadata files differ between the CPU-tested and final image only by verified build timestamps/RECORD checksum; all executable/library/license bytes match. No byte-identical image claim.
- Current source and archive gates, full-history detector review, locked install, licenses and Python security checks completed. Raw image HIGH/CRITICAL gates deliberately fail (exit 1); no inference in CI or remote provider call was made.
- Acceptance: 21 PASS / 2 BLOCKED / 1 FAIL. Source-preview NO-GO and image-security NO-GO are independent. Do not archive this plan while RAG-15, pristine-host qualification, remote CI and image-security disposition are outstanding.
- No push, merge, Git tag, public source/image release, remote deployment or paid/generative call. Required next approvals and exact blockers are in docs/release/verification.md.

### Authorized follow-up (2026-10-30, supersedes previous execution prohibitions)

- User now authorizes normal feature-branch push, ONE Draft PR to main, genuine
  GitHub Actions and ONE independent Ubuntu 24.04 CPU/MiniLM/Qdrant campaign.
- Phase 1 identified the exact original FAIL: RAG-21, whose image-security gates
  actually return 1 for known Debian OS findings; remote CI was not run. Supported
  stable package candidates equal installed versions; no ordinary RAG function
  defect caused this failure. Original evidence/raw scans preserved under
  .local/followup-20261030/baseline, with hashes.
- User explicitly selected observational CI while RAG-21 remains FAIL. No CVE
  suppression, severity reduction, gate exception or unsupported distro mixing.
- New CI separates source checks, three image/security/license/SBOM jobs and the
  single CPU campaign (same-repository Draft PR opened event only). Push or PR
  synchronization does not download models or perform inference.
- Local verification tooling adds locked Black/MyPy, bounded official acquisition
  (two pinned files, fixed byte limits, 180-second wall limit), precise tokenizer,
  pooling/L2/embedding evidence and actual failed-index retry/resource checks.
- Generative LLM inference, merge, Git tag, release/deploy and image publication
  remain prohibited. RAG-15 stays BLOCKED; separate proposal is in release/.
- Remote run IDs, actual host evidence, artifacts and final source-only readiness
  will be recorded only after genuine CI completes. Plan remains active meanwhile.

### Remote CI stop checkpoint (2026-10-30)

- Normal push completed at `11736f527612fc659a201b13e38d13c7278e1476`; exactly one
  Draft PR targets main: https://github.com/hzjanuary/bigdata-rag-system/pull/1.
  No force push/history rewrite/merge/tag/publication/deployment occurred.
- Genuine push run 41006969209 and PR run 41006993655 both completed FAIL on
  GitHub-hosted Ubuntu 24.04.5. Source subchecks passed: 109 deterministic tests,
  one separate actual Qdrant contract, frozen lock, Ruff/Black/MyPy, source/archive,
  current/history secrets, Python audit/license/SBOM and Compose checks.
- NEW defect: report export rejects JUnit containing payload-sized default pytest
  IDs. Local XML is 6,407,084 bytes, exceeding the unchanged 2,000,000-byte guard.
  Both uploads were correctly skipped, artifact APIs returned zero artifacts,
  image jobs and independent-cpu were SKIPPED. Downloaded full log ZIPs pass CRC
  checks; hashes/API results are preserved in the follow-up evidence report.
- STOPPED under the user's explicit new-defect condition. No implementation fix,
  regression test, CI rerun or model download/inference followed discovery. Final
  docs/evidence are committed locally without push to avoid another CI trigger.
- Original RAG-21 FAIL remains: supported Debian updates unavailable for known
  HIGH findings (core 44 / Qdrant 43 / UI 44, zero CRITICAL), unchanged gates and
  raw reports preserved. New report-export failure also prevents CI PASS.
- RAG-20 remains BLOCKED: hosted source execution is not the required real CPU
  model/Qdrant campaign. The one independent campaign authorization is unconsumed.
  No fresh embedding outputs, Qdrant acceptance state or citations can be claimed.
- Next proposed bounded correction, NOT APPLIED: short explicit pytest IDs for
  large payload cases and bounded-JUnit regression, preserving original test
  payloads/assertions and artifact limit. On authorized resume, define one explicit
  CPU trigger for the existing Draft PR; synchronize will not run its opened-only
  job. Do not create another PR or rerun old code to consume the campaign.
- Acceptance remains 21 PASS / 1 FAIL / 2 BLOCKED with historical PASS scope stated.
  Source-only preview NO-GO pending export correction, CI artifacts and independent
  CPU campaign. Docker image approval stays independently NO-GO; RAG-15 remains
  BLOCKED and no generative campaign is authorized. Active plan is not complete.
- Details, exact source/image digests, model revision/hash, run URLs and retained
  log/report hashes: `docs/release/verification.md` and
  `docs/release/evidence/followup-remote-ci.json`.

### Authorized JUnit correction (2026-10-30)

- Original local XML 6,407,084 bytes; fresh before-fix reproduction 6,407,083 bytes
  (timing serialization differs). Actual retained push/PR logs show the same
  unchanged source/evidence size guard rejecting export.
- All three payload-sized default IDs required correction: parser (200,048 name
  characters), artifact guard (2,000,050), stdin (4,194,361). Explicit short unique
  IDs preserve every original AST node other than the added ids keyword.
- Five focused regressions exercise actual child pytest XML: all 23 original large
  payload cases, accurate failure/skip reporting, checksum export, and continued
  rejection of oversized/unauthorized/binary artifacts. The bounded-name regression
  fails against a retained detached a9b68db worktree, passes after correction.
- Full deterministic suite 114 PASS / one skipped; actual Qdrant contract one PASS
  using existing disposable image, no rebuild. Lock/Ruff/format/Black/MyPy pass;
  license inventory 92 approved packages; Python audit zero; history gate retains
  only the reviewed immutable public-hash false positive.
- Actual CI pytest command emits valid unique-name JUnit of 13,067 bytes; all 110
  previous cases remain and five regressions were added. Artifact gate unchanged.
  No runtime/packaging/workflow changes; no release image rebuild or model call.
- Next: exact source/archive/current/history secret gates, normal feature push,
  existing Draft PR update, genuine source/image CI and artifact/hash collection.
  Only after source outcome is verified, prepare a reviewed explicit one-time CPU
  trigger without executing it. Keep RAG-15/20 BLOCKED and RAG-21 FAIL.

### JUnit correction remote completion and trigger preparation (2026-10-30)

- Normal push preserved a9b68db and advanced existing Draft PR #1 to exact tested
  SHA d54b899d665b04dff2db3bd8b7415f96d8b36c9a. No active workflow/runtime/package
  change, force push, second PR or history rewrite.
- Push run 41008646193 and synchronize run 41008651605 completed: source PASS;
  core/Qdrant/UI jobs FAIL solely at unchanged HIGH/CRITICAL exit-1 gates;
  independent-cpu SKIPPED. Hosted JUnit is 13,082 bytes in each run, 114 PASS /
  one skipped. Actual Qdrant/source/archive/secrets/license/audit gates PASS.
- Eight uploaded artifacts downloaded/verified: GitHub ZIP digests, CRCs, exact
  manifests, every file size/hash, source archive at tested SHA. Three raw image
  reports/SBOM/license scans per run retained unchanged. Core 44 HIGH, Qdrant 43,
  UI 44, zero CRITICAL; exact HIGH records and licenses match baseline.
- New JUnit defect RESOLVED; RAG-21 remains FAIL on original image conditions.
  RAG-15 and RAG-20 remain BLOCKED; 21 PASS / 1 FAIL / 2 BLOCKED retained.
- Prepared docs/release/cpu-once.workflow.yml is inert; no .github workflow change
  or operator label action. Reviewed exact target d54b899, PR #1 owner/SHA label,
  serialized single-use check marker before acquisition, first-attempt guards,
  fixed expiry 2026-10-31 00:00 UTC, pinned official model checks unchanged.
  YAML/embedded Python statically validated; live permissions/trigger NOT_RUN.
- Final operator review/install/label action required. Check retention/admin
  deletion limits documented; no absolute immutable exactly-once guarantee.
  Source artifact/history/API/permission errors stop before download; no unguarded
  fallback, new PR, ordinary rerun or automatic synchronize model campaign.
- Original independent model campaign remains unconsumed, zero downloads or
  embedding/generative calls. No local release-image rebuild. Source-only review
  is supported by PASS source CI; final preview awaits independent CPU evidence
  and separate release decision. Docker approval remains NO-GO.
- Final evidence/template committed locally without push to stop after remote
  verification and avoid more CI. All historical logs/XML/scans/state preserved;
  full results in docs/release/evidence/junit-correction-ci.json and verification.md.

### Explicit trigger implementation authorization (2026-10-30)

- Preserved 1ccf0d0 and all previous evidence. Installed dedicated workflow and
  standard-library approval/history/consumption/export helper. Replaced only the
  obsolete CPU block in ci.yml; source/image/security/artifact jobs remain intact.
- Exact current PR #1 head is approved through owner-only `cpuq1:<full SHA>` label.
  No old ancestor target: SHA is resolved after final implementation push and must
  match checkout/event/live PR/source CI/receipt. No label created/applied.
- Complete bounded read-only run/job-attempt/marker history, exact-SHA source
  upload proof, first-attempt checks, fixed concurrency, pre-acquisition persistent
  reservation and live head/receipt recheck fail closed. Previous unskipped attempts
  block retries even when consumption evidence is missing; no fabricated unused state.
- Model/revision/hash/acquisition/acceptance unchanged. Public export excludes raw
  DB rows/private configuration. No runtime/package change, download/model call,
  generative provider, paid API, publication or consumption during preparation.
- 154 deterministic PASS / one skipped, one separate actual Qdrant PASS, lock,
  Ruff/Black/MyPy, license/audit and actionlint syntax/expression checks PASS.
  Next: source/archive/secret gates, normal push, existing PR #1 update and genuine
  source/configuration CI; record exact remote SHA/label and stop before activation.

### Installed trigger: final operator boundary (2026-10-30)

- Normal push preserved 1ccf0d0; final remote PR #1 head
  ba78e94d82b7972e96a9bae962cbb8ada73d6619. Owner activation label, determined
  AFTER push: cpuq1:ba78e94d82b7972e96a9bae962cbb8ada73d6619.
- Source runs 41012209423 (push), 41012213478 (PR): source PASS, 154 tests / one
  skipped, actual Qdrant and all source/security/license/tooling checks PASS.
  Image jobs FAIL solely at known HIGH/CRITICAL gates, raw reports/exits retained.
- Trigger runs 41012209492 / 41012213570: configuration PASS, campaign SKIPPED.
  Inactive receipts explicitly consumed=false, model_download_started=false.
  API confirms labels empty, marker count zero, installed workflow byte match.
- All ten artifacts downloaded and verified: GitHub ZIP digests, CRCs, manifests,
  per-file sizes/hashes, exact source archive. No new HIGH/CRITICAL/license records;
  per image core44/Qdrant43/UI44 HIGH, zero CRITICAL; no gate changes or exceptions.
- STOP before operator action. No label creation/application, marker, model command,
  CPU acceptance, generation, merge/tag/release/deploy/image publication occurred.
  Operator must review exact remote head, then apply the exact label once before
  fixed expiry 2026-10-31 00:00 UTC. Admin/retention replay limits documented.
- Remote machine evidence: docs/release/evidence/cpu-trigger-remote.json; local
  evidence docs commit kept without another push to preserve reviewed activation
  head. RAG-15/20 BLOCKED, RAG-21 FAIL; 21 PASS / 1 FAIL / 2 BLOCKED, plan active.

### Consumed campaign diagnosis (2026-10-30)

- Owner-triggered run 41029994294 at ba78e94: reservation/acquisition PASS; 21
  checks PASS, then named API-restart assertion FAIL. Artifact 12966475279 ZIP
  digest/CRCs/manifest verified. Private result never uploaded; hosted post-job/
  retrieval values unavailable. Preserve all original evidence and marker123977248159.
- Bounded offline diagnosis with existing verified model, fresh private synthetic
  state and existing local Qdrant image: actual API restart retains COMPLETED jobs,
  chunks and points/vectors, readiness200 and exact hit order/text/citations. Only
  BM25 differs by one ULP. Twelve pure hash-seeded processes isolate set-order
  floating summation; no inference/storage dependency needed for counterexample.
- New focused regression intentionally FAILS current production and PASSES the
  one-line sorted-term proposal in an isolated copied package. Existing tests
  (new red test excluded explicitly)154 PASS/one skipped. Production untouched.
- Preserve an auxiliary diagnostic timeout caused by changed ephemeral Docker host
  port; rediscovery confirms Qdrant200 and unchanged point hashes. Do not attribute
  local probe plumbing to original internal-DNS Compose campaign.
- RAG-12 now FAIL due confirmed determinism defect; RAG-15/20 BLOCKED, RAG-21 FAIL:
  20 PASS/two FAIL/two BLOCKED. Proposed correction and safe split checkpoint
  diagnostics await review. Original hosted operand/delta cannot be proven from
  exported data; do not claim original run PASS or blanket storage failure.
- No commit/push, production patch, marker removal, label reapplication, workflow
  rerun, model acquisition or second live campaign. Fresh independent-host campaign
  requires separate explicit authorization/budget; preserve consumed attempt.

### Authorized deterministic remediation (2026-10-30)

- One production line canonicalizes term traversal; algorithm/parameters/thresholds/
  schema/citations/ACL unchanged. Original regression preserved/red, fixed six-seed
  test green; twelve probes bit-identical. RRF/dense/rerank/no-match unchanged.
- Restart checkpoint now captures safe before/after readiness/job/document/chunk/
  status/ordered-hit/provenance/ranking evidence before eight independent exact
  assertions. No tolerance substitution or raw database/config/document upload.
- 168 deterministic PASS/one skipped; real Qdrant contract PASS; quality/lock,
  license92/audit0/source/archive/secret/history gates PASS.
- Real cached CPU model + corrected image full local path 41 PASS including crash,
  outage/retry and standalone backup/restore. Zero model reacquisition. Preserve
  initial zero-check failure caused by exhausted host IP pools; explicit fresh
  project/network option and four checked-IPAM networks avoid deleting retained data.
- RAG-12 PASS on evidence, RAG-15/20 BLOCKED, RAG-21 FAIL: 21/1/2. Old hosted
  run41029994294/marker123977248159 remain consumed/FAIL, no reinterpretation.
- Next authorized step: normal push and actual source CI. Unexpected new source
  failures stop before activation preparation. Only then implement/audit cpuq2's
  distinct identity/marker/label, preserving exactly the known prior failure and
  rejecting all other attempts/missing history. Never create/apply activation label.

### Additional campaign preparation after corrected source CI (2026-10-30)

- Corrected source59a7103: source jobs41035999451/41036006533 PASS (168 tests/one
  skipped); ten artifacts downloaded/digests/manifests verified. Actual image gates
  preserve known HIGH failure behavior; no unexpected source failure.
- Separate policy `spec001-pr1-cpu-qdrant-remediation-2`, marker
  `spec001-cpu-pr1-remediation-2-consumed`, prefixcpuq2. Fixed window Oct30 10:00
  through Oct31 00:00 UTC; exact SHA resolved only after final push/CI.
- Read-only actual GitHub audit validates exact oldrun41029994294, actor/job/steps,
  consumed marker123977248159, pinned ZIP/receipt/checksums and failure logs. Only
  that verified old failure is exempted; missing history/markers, every other
  started attempt or new marker rejects. No reinterpretation as unused.
- Downloaded source ZIP/tar membership and hashes required for exact target; new
  reservation/receipt and original proof/current PR rechecked before acquisition.
  No retries; concurrency and rerun guards retained; admin/retention limits explicit.
- 194 tests PASS/one skipped, quality/actionlint green. New policy not activated,
  no model acquisition, no new marker or label. Final normal push/CI then stop at
  owner activation boundary, retaining RAG-15/20 BLOCKED and RAG-21 FAIL.

### Final cpuq2 operator boundary (2026-10-30)

- Final remote head287212be8f5683221d2449158331e59d4c639c15; future owner label
  cpuq2:287212be8f5683221d2449158331e59d4c639c15. Never created/applied here.
- Final source runs41038452232/41038457036: source PASS, 194 tests/one skipped,
  actual Qdrant/source/secret/license/audit gates green; images only known HIGH FAIL.
  Configuration runs41038452175/41038457194 PASS with campaign SKIPPED.
- Ten final plus ten initial-fix artifacts preserved/verified: ZIP digests/CRC,
  exact manifests and source tar. No changed HIGH/license records, unchanged gates.
- Read-only final audit verifies17 accessible runs, old marker/receipt/pinned ZIP/
  failure logs and final source archive. Original cpuq1 label/marker untouched,
  old consumed=true FAIL remains; new marker count0 and no new acquisition/campaign.
- Separate identity remediation-2/prefixcpuq2, fixed windowOct30 10:00--Oct31 00:00
  UTC; strict known-one-old-attempt accounting and complete source/archive proof.
  Owner must review exact head then activate once separately; fail closed on any
  missing/inconsistent record. No rerun/reset, no automatic extension, admin limits
  documented. Stop here before activation.
- RAG12 PASS on demonstrated determinism and local CPU41-check path; RAG15/20
  BLOCKED, RAG21 FAIL:21/1/2. No release/merge/tag/deploy/image publication/generation.
  Final docs evidence retained locally without push, preserving reviewed head.
