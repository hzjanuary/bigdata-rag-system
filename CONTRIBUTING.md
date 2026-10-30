# Contributing

Use Python 3.12 and `uv sync --frozen`. Run `uv run pytest -q`, `uv run ruff check .`
and `uv run ruff format --check rag_core scripts tests`. Deterministic tests reject
network connections; use explicit Python test injection, never a configurable fake
embedding model or completion provider. Keep model weights and personal documents
outside tracked files and build contexts.

Preserve the public contracts in docs/architecture.md and SPEC-001. New routes must
have anonymous, workspace-isolation and redaction tests. Parser/index changes need
failure/restart/atomic-visibility coverage. No retry may clear collections. New
model/provider acquisition, live generation, external side effects or publication
requires separate operator authorization; CI never runs inference.

Update pyproject.toml and uv.lock together. Regenerate hashed requirements with
`uv export --frozen --no-dev --no-emit-project -o requirements.txt`, then run the
runtime/optional license inventory and security checks. Keep image bases and CI
actions pinned to immutable digests/SHAs; retain original scan output and separate
source from image release decisions. Include a license review for new packages.

Make focused commits on a local feature branch. Explain user-visible behavior,
security boundaries and meaningful test evidence. No source/image publish, push,
tag or remote deployment happens without the operator's explicit approval.
