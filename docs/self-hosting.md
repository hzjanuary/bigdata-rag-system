# Self-hosting (Linux CPU)

Use Python 3.12 and the frozen lock. Defaults do not create accounts, ingest datasets,
fetch models or contact a generator. `rag config init` is an explicit private setup;
refusing an existing config/state is deliberate. Keep config and state outside Git.
The local CLI defaults to `~/.config/rag-core/config.json`; `RAG_CONFIG` or `--config`
selects another private file. Permissions must be 0600 config and 0700 state, owned
by the running UID, with no symlink components. Never chmod private state world-readable.

Follow README's Docker bootstrap as your host UID. Set RAG_UID/RAG_GID for Compose
so the API can read that config and the host-owned model cache. The defaults use
UID/GID 10001. Qdrant independently runs as 10001 with a named persistent volume
initialized by the derivative image. No retained volume is chowned or migrated.
Start a new project for experiments; retain old prototype volumes untouched.

Containers have read-only roots, dropped capabilities, no-new-privileges, bounded
CPU/RAM/PIDs and tmpfs. API binds 127.0.0.1; Qdrant has no host ports and telemetry
is disabled. Qdrant is attached only to an internal Docker network. The API also has an
ingress bridge, required for loopback port publishing on current Docker releases;
that bridge permits outbound connections, but generation remains disabled unless
explicitly enabled in the private operator config. Readiness tests
Qdrant; missing weights cause explicit model_not_installed during ingest/search,
not a silent download. `/health` does not load or validate the model or a provider.
A model integrity mismatch produces a fixed error. Correct the operator-selected
path; do not replace weights under a running installation.

The Dockerfile uses locked wheel hashes and digest-pinned Python/uv stages. It does
not install compilers, Git, CUDA, OCR or datasets into the runtime. Build provenance
is the `org.opencontainers.image.revision` label plus local image ID recorded by
the acceptance run; a local image ID is not a published registry RepoDigest.
Builds are dependency-reproducible, not promised byte-identical across timestamps.

Optional UI (not part of the default image):

```bash
docker compose -f docker-compose.yml -f docker-compose.ui.yml --profile ui build ui
docker compose -f docker-compose.yml -f docker-compose.ui.yml --profile ui up -d ui
```

The UI binds loopback:8501, retains CORS/XSRF protection, and is only an HTTP API
client. A capability is entered in its password field; every API call enforces ACL.
It has no config, state, model or Qdrant mount. Disable external browser telemetry
(the packaged command sets gatherUsageStats=false). GPU execution is intentionally
not supplied without hardware/model validation. CPU is the supported path.

For remote access, put an authenticated TLS reverse proxy in front, restrict trusted
origins, enforce connection/body/header timeouts, and protect the host and Docker
socket. Do not publish Qdrant. This repository does not deploy or provision that
proxy for you. A private isolated Qdrant with only the API as client is the default
trust boundary; use a Qdrant key for an independently managed Qdrant and store it
only in private config. Do not reuse a capability as a provider key.

Remote generation requires an explicit operator config change and privacy
decision. The API ingress bridge permits outbound connections; Qdrant remains only
on the internal network. Retain loopback API binding and configure the provider
privately as described in provider-models.md. Never enable a provider as an implicit
health/startup check. No live provider test is authorized by local installation.

One API process and one writer are supported. Do not set multiple Uvicorn workers,
share SQLite on NFS or scale replicas. Graceful shutdown waits for the bounded
worker; SIGKILL recovery replays only idempotent indexing. See backup-restore.md.
