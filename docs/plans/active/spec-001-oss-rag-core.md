# SPEC-001 execution plan

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

## External constraints / pending evidence

- RAG-11: approved acquisition and ONE same-project CPU/Qdrant campaign are COMPLETE (34 checks); no further model campaign authorized.
- RAG-15: LIVE generation deliberately BLOCKED until separate approval and operator credentials; do not request secrets in chat.
- RAG-20: local secure CPU Compose verified; a separate pristine Linux host/VM remains unqualified and needs a separately authorized environment/model campaign.
- RAG-21: remote GitHub CI requires a push, prohibited in current scope. Local image gates fail on 44/43/44 HIGH OS findings (core/Qdrant/UI), no listed fixes; image distribution remains NO-GO.
- Publication, tags, remote deploy and touching existing volumes remain prohibited.

## Execution log

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
