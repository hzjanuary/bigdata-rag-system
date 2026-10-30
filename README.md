# Multi-Workspace RAG Engine — early source preview

Self-hosted, CPU-first multi-workspace RAG engine with secure document ingestion, ONNX embeddings, Qdrant hybrid search, durable jobs, and source-grounded citations.

Private, CPU-first document retrieval with Qdrant, SQLite job metadata, an authenticated
API and CLI. Ingest UTF-8 text, PDF text pages and DOCX paragraphs, then search with
dense embeddings, BM25, reciprocal-rank fusion and a deterministic term-coverage
reranker. Every result identifies the stored document, chunk, source hash and real
PDF page (TXT/DOCX page is null). Generation is disabled by default.

> **Security Notice — early source-only v0.1.0 preview.** This is experimental
> self-hosted source, not a production-certified deployment. Independent CPU/Qdrant
> acceptance passed 41/41 on GitHub-hosted Ubuntu 24.04; that does not clear image
> security. Existing Trivy HIGH findings remain **core 44, Qdrant 43, optional UI 44**
> (separate per-image package findings, not summed unique CVEs). Image security jobs
> remain FAIL; **no prebuilt Docker images are approved for publication**. Building
> locally inherits these unresolved OS findings. Real generative LLM answering has
> **not** been live-verified (RAG-15); keep generation disabled unless separately
> authorized and privately configured. Read [SECURITY.md](SECURITY.md) and the
> [actual acceptance/CI evidence](docs/release/verification.md) before installation.
> Independently review dependencies, OS packages, model/provider data policies,
> credentials, network exposure and your deployment environment. CPU embeddings,
> real Qdrant indexing/retrieval and source citations have independent verification;
> unrestricted Internet exposure is not certified. Raw per-image security reports:
> [core](https://github.com/hzjanuary/multi-workspace-rag-engine/actions/runs/41038457036/artifacts/12969555839),
> [Qdrant](https://github.com/hzjanuary/multi-workspace-rag-engine/actions/runs/41038457036/artifacts/12968453916),
> [UI](https://github.com/hzjanuary/multi-workspace-rag-engine/actions/runs/41038457036/artifacts/12968877744).

This replaces the historical easyResearch prototype. Existing uploads/collections
are **not migrated or reset** automatically. Preserve old volumes and check out the
original history separately if needed. This is a single-instance self-hosted core,
not a distributed SaaS. See [verification](docs/release/verification.md) for actual
tested identities, limitations and separate source/image release decisions.

Repository branding follows `hzjanuary/multi-workspace-rag-engine`. Existing package,
CLI, API title, image tags and private config/storage names remain compatible.
See the [reference audit and rename/retirement review](docs/maintenance/repository-rebranding.md);
v0.1.0 and original campaign records retain their historical identities.

## Local first run (Linux, Python 3.12)

Use Python 3.12 and [uv](https://docs.astral.sh/uv/) (verified CI uses uv 0.9.7), then:

```bash
uv sync --frozen
uv run rag --config "$HOME/.config/rag-core/config.json" config init \
  --state-dir "$HOME/.local/share/rag-core"
```

Init creates mode-0600 config and mode-0700 storage, refuses overwrite and creates
no workspace. Do not paste the private config or capability into chat, issues or logs.
Run your own private Qdrant, or follow the isolated Docker setup below. The default
Qdrant URL is loopback. No model, dataset or provider is contacted on startup.

Embedding acquisition is a separate explicit step (about 91 MB download; allow
roughly 500 MB RAM for inference). Read [model licenses and privacy](docs/provider-models.md):

```bash
uv run python scripts/acquire_model.py --accept-license-and-download \
  --destination .local/models/minilm-10dbd2f
```

Only `onnx/model.onnx` and `tokenizer.json` are acquired from the pinned official
repository. The installer refuses an existing destination and verifies upstream
Git/LFS integrity. Set `model_dir` in the private JSON to that directory's absolute
path; set `qdrant_url` to your private Qdrant address. Model files remain private.

```bash
uv run rag serve
# In a second terminal, using the same private config:
uv run rag doctor
uv run rag workspace create research
# Save the returned capability privately; substitute the returned opaque ID below.
uv run rag ingest WORKSPACE_ID examples/corpus/orchard.txt
uv run rag job show WORKSPACE_ID JOB_ID
uv run rag search WORKSPACE_ID 'How is rainwater stored?'
uv run rag search WORKSPACE_ID 'How is rainwater stored?' --no-rerank
uv run rag ask WORKSPACE_ID 'How is rainwater stored?'
# ask returns generation_disabled until explicitly configured.
```

`rag ingest` imports one bounded regular local file; it rejects symlinks in every
path component. It uploads bytes through the authenticated API. The server never
accepts a caller-chosen filesystem path. Duplicate content with the same format
returns its existing job; reusing a filename with different content adds a new
immutable document. Deletion is owner-only and requires the exact ID.

Optional cleanup, only for the workspace you intend to delete:

```bash
uv run rag workspace delete WORKSPACE_ID --confirm WORKSPACE_ID
```

For a workspace client, put its capability in a private process environment and
use `rag --token-env RAG_WORKSPACE_TOKEN search WORKSPACE_ID 'question'`. The owner
can administer all workspaces; a capability authorizes exactly one. The owner
config remains trusted administrative material. See [API contracts](docs/architecture.md).

## Private CPU Docker Compose

```bash
docker compose build
mkdir -p .local/operator
# Bootstrap as your host UID, without root-owned operator files:
docker run --rm --user "$(id -u):$(id -g)" \
  -v "$PWD/.local/operator:/private" workspace-rag-core:local \
  config init --state-dir /private/state
```

Edit `.local/operator/config/config.json` locally: `qdrant_url` is
`http://qdrant:6333`; `model_dir` is `/private/model`. Use the explicit acquisition
above first. If retrieval is not needed yet, `model_dir` can stay null. Then:

```bash
export RAG_UID="$(id -u)" RAG_GID="$(id -g)"
docker compose up -d
# API is loopback-only on port 8000. Qdrant has no published port.
docker compose exec -T api rag doctor
docker compose exec -T api rag workspace create research
# Stream a permitted local file through stdin; no writable container root is needed.
docker compose exec -T api rag ingest WORKSPACE_ID - --filename orchard.txt \
  < examples/corpus/orchard.txt
```

Qdrant uses a persistent project-scoped volume. Do not use `docker compose down -v`.
Do not point experimental projects at retained operator volumes. Qdrant stays on an internal network; the API also uses an ingress bridge for
loopback port publishing. Generation is disabled in private config by default. Full setup, opt-in UI, storage, TLS and
provider egress are in [self-hosting](docs/self-hosting.md). GPU execution is not
validated or shipped; no automatic GPU detection or CUDA download occurs.

## Development and evidence

```bash
uv run pytest -q
uv run ruff check .
uv run ruff format --check rag_core scripts tests
uv run python scripts/source_gate.py
uv run pip-audit --require-hashes --disable-pip --no-deps -r requirements.txt
```

Deterministic tests forbid network access and inject fixtures through Python only.
Fixtures are never selectable production models/providers. The independent campaign
at [run 41040402221](https://github.com/hzjanuary/multi-workspace-rag-engine/actions/runs/41040402221)
passed all 41 real CPU/Qdrant checks at runtime source
`287212be8f5683221d2449158331e59d4c639c15`. RAG-20 is PASS; overall SPEC-001 remains
**22 PASS / one FAIL / one BLOCKED**, including image-security FAIL and live
generation BLOCKED. The complete CI workflow is not green.

`scripts/isolated_acceptance.py` downloads nothing and uses a preinstalled model.
It tests actual images, Qdrant, crash/outage and independent backup/restore with
synthetic data. Hosted execution required a separately authorized owner label;
both historical campaign budgets are consumed. Do not reapply labels or rerun them.
Ordinary source CI never downloads the embedding model or invokes generation.

Read [security](SECURITY.md), [contribution](CONTRIBUTING.md), [architecture](docs/architecture.md),
[backup/restore](docs/backup-restore.md), [NOTICE](NOTICE) and [MIT license](LICENSE).
Third-party weights, packages and OS files retain their own licenses. No source,
image, tag or remote deployment is published by this implementation workflow.
