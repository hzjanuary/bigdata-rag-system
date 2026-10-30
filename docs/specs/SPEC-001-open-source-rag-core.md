# SPEC-001 - Open-Source Multi-Workspace RAG Core

Status: PROPOSED - not implemented or accepted
Repository: https://github.com/hzjanuary/bigdata-rag-system
Observed default-branch baseline: `74931fedcf99408e8b15b9052c0e8aed1fd6d8fc` (2026-10-28 inspection)
Proposed implementation branch: `feat/spec-001-oss-rag-core`
Release target: `v0.1.0` as an early source preview only after separate publication review; inspect existing tags first.

## 1. Outcome

Transform the existing easyResearch Big Data prototype into a reproducible, useful, open-source, self-hosted **multi-workspace document RAG engine**. Preserve RAG, document ingestion, embeddings, Qdrant, hybrid retrieval, reranking and attributable answers. Do not copy Multi-Agent OS's LangGraph workflow architecture or remove Qdrant simply for uniformity. Prefer an API/CLI-first core with an optional UI.

Definition: a new operator can clone the source, configure a clean local installation, create a workspace, ingest a permitted small document corpus, search and retrieve grounded citations on CPU, restart services without losing committed state, and optionally generate answers through a real explicitly configured provider. No bundled personal data or default paid requests.

## 2. Observed starting point (static code review; not runtime verification)

- `api_main.py`: FastAPI query, search, upload, pipeline, workspace deletion, metrics, trace and log-deletion endpoints. Those routes currently have no visible authorization dependency; the app enables permissive CORS. See `api_main.py` around lines 280-306 and 336-640.
- `api_main.py` accepts a request-controlled `source_dir` in `/pipeline/start`; uploads read the complete file into memory; workspace deletion is directly exposed. See around lines 422-574.
- `config.py` `_safe_name()` only replaces spaces/hyphens, without validating slash, `..`, Unicode normalization or aliases. Workspace identity must not be inferred to be safe from the current method.
- `core/rag_engine.py`: Groq-specific answer generation; dense + BM25 + reranking and source metadata. `core/pipeline.py` includes clean/enrich/chunk/embed; global in-memory pipeline status and an optional `reset_db` path.
- `core/observability.py`: JSONL pipeline traces/metrics; privacy of queries, snippets and source paths is not sufficiently bounded by current public API design.
- `docker-compose.yml`: Qdrant ports 6333/6334 and API/UI listen on all host interfaces; Streamlit uses disabled CORS/XSRF protection in the example. `Dockerfile` defaults to a CUDA/PyTorch image and installs build tooling into the final image.
- `requirements.txt`: broad lower-bounded dependencies, CUDA-index requirement and no reproducible lock. MIT LICENSE is already present. The reviewed tree has no dedicated tests or GitHub Actions.
- README presents a fixed sample dataset/RTX 3050 environment and calls the prototype production-grade; this is not evidence of broad self-host compatibility.

Before making edits, Codex must re-read the **actual local HEAD**, working tree, history and operator data. Treat the observations above as baseline hypotheses if local code has advanced.

## 3. Product boundaries

### Keep
- Authenticated workspaces and independent document collections.
- PDF, DOCX and text ingestion where safe parsers are installed; explicitly version the supported formats.
- Dense retrieval, BM25/hybrid ranking, optional cross-encoder reranking, verified source metadata and source snippets.
- CPU-first operation; an opt-in GPU profile if hardware and model compatibility are validated.
- Qdrant as the vector database; optional Streamlit is a separate opt-in service, not an unprotected administrative surface.

### Replace / remove
- Dataset-specific branding, hard-coded user hardware assumptions and automatically enabled sample imports.
- Global pipeline status and unsafe reset/delete defaults.
- Groq-only mandatory generation; use a small, explicit, vendor-neutral provider interface with real adapters as warranted.
- Unguarded administrative endpoints; caller-chosen absolute ingest paths; permissive network exposure/CORS.
- Silent partial indexing, misleading citations, fixture/fake provider fallback, deceptive production-readiness claims.

### Not in v0.1 scope
- Distributed multitenant SaaS, enterprise SSO, Kubernetes, guaranteed exactly-once external side effects, billion-document benchmarks, arbitrary web crawling, automatic cloud resource provisioning.
- A promise that remote LLM inference is private/local, or that user-generated content is trusted.

## 4. Target architecture

```text
Operator CLI / optional authenticated UI
              |
FastAPI: auth, workspace ACL, upload, job, search, ask, health
              |
       Application services
        /          |         \
SQLite WAL*   Bounded job      Retriever
metadata/jobs worker        dense + BM25 + rerank
        |          |              |
   file manifest  extraction   Qdrant collections
   and audit      -> chunk      + versioned model metadata
                   -> embed
                      |
           Explicit LLM adapter (optional; no silent remote calls)
```

*Use SQLite WAL as the **single-instance default** for durable metadata/jobs; document concurrency/backup limitations. If tests demonstrate a concrete need for PostgreSQL, present a migration decision with evidence instead of adding it reflexively. Qdrant remains the vector index. An implementer may propose a better minimal durable store with rationale, but acceptance criteria must remain intact.

### Configuration and startup
- `rag config init` generates a private, mode-0600 config and storage directories mode 0700; refuse overwriting initialized installations. No API token or workspace is seeded by database migrations.
- `rag doctor`, `rag workspace create/list`, `rag ingest`, `rag job show`, `rag search`, `rag ask` and `rag workspace delete --confirm` are required CLI journeys. Naming may differ only if documented consistently.
- Default provider configuration is **disabled**. Retrieval without LLM credentials must work, while `ask` fails explicitly if the operator has not configured a real generation adapter. No automatic provider call on startup/health/config validation.
- CPU-first compose uses private Docker networking, loopback host API binding, unexposed Qdrant, non-root runtime where supported, health checks, persistent volumes, pinned supported images/dependencies and a minimal runtime image. Optional GPU/UI profiles must be separately enabled.
- Embedding models must be explicitly selected/downloaded with documented license, disk requirements and first-run cost. Do not auto-download large models during tests or service startup. Record embedding ID, dimension, normalization and index schema for each workspace.

### Workspace and document safety
- Identity is an opaque server-issued workspace ID, not a filesystem path. Validate user-provided slugs strictly and reject traversal, Unicode aliases and collection collisions.
- Every workspace query, ingest, export, deletion, metrics and trace action enforces its ACL. Initial release may support a single owner/admin; if claiming multiple users, implement and prove isolation.
- Ingestion accepts a bounded, streamed upload or admin-approved configured import directory, never an arbitrary client-supplied filesystem path. Bound file size/count, extracted text length, decompression, CPU/time, concurrency and permitted MIME/extensions. Handle symlinks and duplicate filenames safely.
- Use stable document IDs, content hashes and source-page/chunk provenance. No implicit collection reset; replacing a document is idempotent and atomic at the manifest level, and failed jobs must not appear as complete.
- Persist job states (`QUEUED/RUNNING/COMPLETED/FAILED/CANCELLED`) and checkpoints safely; restart/recovery semantics must be documented, including uncertain work and at-least-once risks. Do not silently re-run non-idempotent deletion or paid enrichment.
- Deletion requires explicit operator action, scope confirmation and an audit event; tests must prove cross-workspace deletion is impossible.

### Retrieval and generation contracts
- Search returns real document IDs, chunk/source/page metadata, bounded excerpts, actual ranking provenance, and structured no-match output; never fabricate citations or source URLs.
- Version embedding/index metadata and detect incompatible query-vs-index dimensions before performing retrieval; perform migrations or reindex only on explicit command.
- Reranker must have a bounded CPU path, explicit opt-out and reproducible rank tests. Label metrics correctly: do not represent a score-threshold heuristic as benchmark hit rate/MRR.
- Treat document text, snippets and tool content as untrusted, lower-trust data; do not follow instructions from retrieved documents. Answer generation may use only citations from retrieved, authorized chunks. Empty retrieval -> explicit no-evidence response, not a confident answer.
- Provider adapters have strict timeouts, explicit budget/token limits, structured errors, secret redaction and zero automatic paid fallback by default. Erroring providers never become success placeholders.

### Security, privacy and observability
- Auth required for workspace content, operations, metrics and traces; public health cannot reveal secrets. Use owner key or documented authenticated roles, compare securely, and fail closed on missing/placeholder secrets.
- Default CORS restricted; optional UI protected by the same auth boundary. Rate, body-size and concurrency limits; explicit TLS/reverse-proxy advice for Internet deployment.
- Opt-in traces must not dump document text, user prompts, credentials or arbitrary source paths by default. Provide sanitized request/job IDs, latency, selected provider/model, error class and measured metrics. Test redaction end-to-end.
- Add exact tracked-file secret scanning, private-path/index gate, source/image manifest verification, SBOM, license inventory/NOTICE and OS/Python security scans; preserve raw findings and distinguish source preview from secure image approval.
- Inventory licenses for base images, Qdrant, embeddings/rerankers, OCR/document parsers and dependencies. Existing project MIT covers only project-owned source.

## 5. Implementation stages

**S0 - Baseline and threat model**: inventory existing endpoints, real imports, datasets/models, Git history secrets and ownership; record clean source SHA, deployment behavior, privacy/data flows; save historical Git access. Create a durable implementation plan and baseline regression/negative tests before refactoring.

**S1 - Auth and domain core**: typed settings and strict workspace IDs/ACL; thin API/domain split; CLI/config bootstrap and explicit destructive operations. Disable exposed unsafe routes and broad CORS.

**S2 - Reproducible ingest/index/retrieval**: CPU-first Qdrant, explicit embedding installation, bounded parsers, durable job state, idempotent content hash/manifest, hybrid retrieval, dimension validation and grounded citations. No external LLM dependency for retrieval.

**S3 - Optional generation/UI/observability**: real provider adapter, fail-closed budgets, optional authenticated UI, privacy-safe traces, recovery tests, cancellation and backup/restore rehearsal.

**S4 - OSS release engineering**: locked deps, clean archive/image, licenses, scan gates, CI, complete docs and operator walkthrough, source-only publication decision. Keep image publication separately gated on actual vulnerability disposition.

## 6. Acceptance matrix (evidence required, not optimistic status)

| ID | Verifiable condition |
| --- | --- |
| RAG-01 | Fresh clone and locked install build without user data or credentials; source and image inventory verified. |
| RAG-02 | Startup does not import datasets, query paid LLMs or auto-download models. |
| RAG-03 | `config init` creates secure private config, no account/data seed, refuses overwrite. |
| RAG-04 | Auth rejects anonymous and placeholder credentials for all content/mutation/trace routes. |
| RAG-05 | Workspace IDs reject `../`, encoded separators, aliases, symlinks and collisions. |
| RAG-06 | Two authorized workspaces cannot see, query, ingest or delete each other's documents. |
| RAG-07 | Upload and import enforce parser, file, payload, extraction and resource bounds. |
| RAG-08 | Ingest job and checkpoints survive process restart; duplicates are idempotent. |
| RAG-09 | Failed/cancelled ingest never reports complete or leaks partially published index state. |
| RAG-10 | No collection clear/reset without a distinct explicitly authorized operation. |
| RAG-11 | CPU-first real Qdrant + actual embedding model can index and retrieve a small licensed test corpus. |
| RAG-12 | Dense/BM25/rerank are deterministic and model/index dimensions are enforced. |
| RAG-13 | Search returns only actual sources and verifiable page/chunk provenance; zero-hit case is explicit. |
| RAG-14 | Generation is disabled without real configured provider, no fake fallback or fabricated citations. |
| RAG-15 | One separately authorized, bounded real provider answer is grounded in persisted retrieved chunks (LIVE; remains BLOCKED until approved/tested). |
| RAG-16 | CLI and API perform equivalent authenticated read/manage journeys; optional UI cannot bypass ACL. |
| RAG-17 | Logs/traces and errors do not contain raw document content, tokens or sensitive paths by default. |
| RAG-18 | Real Qdrant interruption and restart preserve acknowledged metadata and yield truthful readiness. |
| RAG-19 | Isolated backup/restore rehearsal preserves workspaces, manifests, index consistency and job history. |
| RAG-20 | Default Docker Compose binds API to loopback and Qdrant to private network; CPU path verified on clean Linux host. |
| RAG-21 | Locked CI passes unit/integration/security/CLI/image/license checks without inference. |
| RAG-22 | Secrets, private paths and dataset files are excluded from tracked source and release artifacts; adversarial tests catch bypass. |
| RAG-23 | README supports clean first-run; SECURITY/CONTRIBUTING/NOTICE/LICENSE and provider/model license boundaries are accurate. |
| RAG-24 | Source-preview readiness, live-model evidence, actual remote CI and image security signoff are reported separately. |

Rules: label each PASS, FAIL, BLOCKED or NOT_RUN with a command, artifact and **tested source/image identity**. Test doubles may verify contracts but cannot satisfy real embedding/model requirements. Do not change criteria to make the matrix green.

## 7. Documentation and delivery

Deliver `README.md`, `docs/architecture.md`, `docs/self-hosting.md`, `docs/provider-models.md`, `docs/security-model.md`, `docs/backup-restore.md`, `docs/release/verification.md`, `docs/release/RELEASE-CHECKLIST.md`, `SECURITY.md`, `CONTRIBUTING.md`, `LICENSE`, `NOTICE`, an examples directory with a small explicitly licensed corpus and source references, and a comprehensive test suite. Keep the initial source history accessible, never rewrite automatically.

Expected handoff: implementation branch/HEAD and clean worktree, exact tested source and image digests, acceptance status, residual risks, runnable local commands, test evidence, documentation links and a GO/NO-GO decision for **source preview** distinct from Docker image distribution.

## 8. Non-negotiable operational constraints

Never use real operator keys, documents or ChatGPT chat transcripts as test fixtures. Do not push, merge, tag, publish, deploy, delete retained data, turn on billing or perform live LLM calls without a **separate, explicit** authorization. All local experiments must be isolated and reversible. If release is blocked, finish the implementation/evidence and report the blocker instead of bypassing checks.
