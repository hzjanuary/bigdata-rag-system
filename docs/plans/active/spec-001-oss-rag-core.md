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

- RAG-11: model acquisition requires explicit operator approval; question submitted. No model download until granted.
- RAG-15: LIVE generation deliberately BLOCKED until separate approval and operator credentials; do not request secrets in chat.
- Remote GitHub CI requires a push, prohibited in current scope; report separately.
- Publication, tags, remote deploy and touching existing volumes remain prohibited.

## Execution log

- S0 baseline and history detector completed; runtime implementation has not begun at this commit.
