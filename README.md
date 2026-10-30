# Workspace RAG Core — early source preview

Private, CPU-first document retrieval with Qdrant, SQLite job metadata, an authenticated
API and CLI. Ingest UTF-8 text, PDF text pages and DOCX paragraphs, then search with
dense embeddings, BM25, reciprocal-rank fusion and a deterministic term-coverage
reranker. Every result identifies the stored document, chunk, source hash and real
PDF page (TXT/DOCX page is null). Generation is disabled by default.

This replaces the historical easyResearch prototype. Existing uploads/collections
are **not migrated or reset** automatically. Preserve old volumes and check out the
original history separately if needed. This is a single-instance self-hosted core,
not a distributed SaaS. See [verification](docs/release/verification.md) for actual
tested identities, limitations and separate source/image release decisions.

## Local first run (Linux, Python 3.12)

Install [uv](https://docs.astral.sh/uv/), then:

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
uv run rag workspace delete WORKSPACE_ID --confirm WORKSPACE_ID
```

`rag ingest` imports one bounded regular local file; it rejects symlinks in every
path component. It uploads bytes through the authenticated API. The server never
accepts a caller-chosen filesystem path. Duplicate content with the same format
returns its existing job; reusing a filename with different content adds a new
immutable document. Deletion is owner-only and requires the exact ID.

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
Fixtures are never selectable production models/providers. The explicit
`scripts/isolated_acceptance.py` campaign requires prior model authorization and a
preinstalled model, downloads nothing, and tests actual images, Qdrant, crash,
outage and independent backup/restore using synthetic data. It is never run by CI.

Read [security](SECURITY.md), [contribution](CONTRIBUTING.md), [architecture](docs/architecture.md),
[backup/restore](docs/backup-restore.md), [NOTICE](NOTICE) and [MIT license](LICENSE).
Third-party weights, packages and OS files retain their own licenses. No source,
image, tag or remote deployment is published by this implementation workflow.
