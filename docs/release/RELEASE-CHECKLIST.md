# Source-only v0.1.0 owner decision checklist

**SOURCE-ONLY READY FOR OWNER DECISION**, subject to the exact final source archive
and checks recorded in verification.md. This is an early pre-release source preview,
not production certification. This checklist grants no push/merge/tag/release,
deployment or image-publication authority.

## Completed evidence, with separate boundaries

- [x] Exact runtime source `287212be8f5683221d2449158331e59d4c639c15`; later
  documentation/evidence-only changes are attested separately, with no executable
  or packaging delta. Preserve local e2dc537 rather than rewriting history.
- [x] Genuine independent GitHub-hosted Ubuntu24.04 campaign41040402221, attempt1:
  **41/41 PASS**, exact official MiniLM revision/hash, CPU-only pooling/L2, actual
  Qdrant, synthetic TXT/PDF/DOCX, citations/isolation/hybrid/restart, worker crash,
  outage/retry, independent SQLite/Qdrant backup and restore.
- [x] Campaign artifact ZIP digest, CRC, exact checksum manifest and every exported
  file verified. Both campaign markers/labels retained: cpuq1 consumed/FAIL,
  cpuq2 consumed/PASS. No third campaign or rerun authorized by reconciliation.
- [x] Exact original RAG-20 requirement satisfied; RAG-12 remains PASS. Current
  matrix **22 PASS / one FAIL / one BLOCKED**, not all criteria PASS.
- [x] Deterministic source/recovery tests, real Qdrant contract, Ruff/Black/MyPy,
  lock, source/archive/private-path/current/history secret gates, license inventory
  and dependency audit checked; actual rerun results are in the ledger.
- [x] MIT project LICENSE and third-party NOTICE reviewed. Python development,
  runtime and optional UI licenses retain their own scope; development-only GPL/
  LGPL audit tools are not relicensed or bundled into the core runtime.
- [x] Prominent README/SECURITY notice before installation. No tracked credentials,
  operator state, weights or backup files; source archive is exact and hashed.
- [x] Genuine source CI PASS at tested runtime SHA; overall source/image workflow
  FAIL because image gates still exit1. Preserve raw per-image reports/SBOM/licenses.
- [x] Existing main rulesets reviewed read-only: PR path, resolved threads, source
  status from GitHub Actions with up-to-date policy, no deletion/force push, no
  bypass actors. Classic protection API404 does not negate active rulesets.

## Still unresolved, and not waived

- RAG-21 **FAIL**: core44 HIGH / Qdrant43 HIGH / UI44 HIGH OS findings, zero CRITICAL
  in retained scans. Per-image package counts are not summed as unique CVEs.
  No prebuilt Docker image is approved for publication. Local source builds inherit
  findings; source-preview readiness is not a security certification or image waiver.
- RAG-15 **BLOCKED**: no authorized real generative answer verification. Generation
  remains disabled; provider/privacy/billing/semantic grounding need separate review.
- Product limits: single writer/SQLite instance and trusted host/owner, English model
  and 256-token truncation, text-only PDF/DOCX parsing without OCR, no GPU/distributed
  deployment validation, no production performance/SLA claim. See operator docs.

## Exact owner-authorized steps before publication

- [ ] Owner explicitly accepts this repository's source-only preview scope and the
  unresolved image/live boundaries. Decisions about other repositories do not apply.
- [ ] Approve normal push of documentation/evidence-only commits if they should
  become the release source. Preserve history and runtime287212b attestation; do not
  rerun consumed campaigns just because documentation HEAD changes.
- [ ] Obtain genuine required source CI on the final pushed PR HEAD, with main
  up-to-date and all existing rules satisfied. Resolve review threads and transition
  Draft PR #1 only with authorization. No bypass, force push or automatic merge.
- [ ] If any executable/packaging input changes during reconciliation/merge, stop
  for a new verification decision. Documentation-only ancestry is not permission
  to claim a different runtime was tested.
- [ ] Owner separately approves merging PR #1 and the exact release commit/tag,
  version and GitHub pre-release scope. None is performed by this checklist.
- [ ] Generate source-only archive from that approved commit, verify every member/
  hash against its manifest, and publish SHA-256 with LICENSE/NOTICE/security
  notice and correct runtime-versus-documentation provenance.
- [ ] Release notes disclose 22/1/1, RAG-15 unverified, RAG-21 FAIL, all three distinct
  image findings and production limitations. No statement that all CI is green.
- [ ] Publish only specifically approved source assets. No Docker registry upload,
  deployment, repository rename or generative inference is included.
