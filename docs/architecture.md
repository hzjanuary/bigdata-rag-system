# Architecture and API contract

One API process owns a nonblocking OS file lock; a second process fails startup.
A single background worker drains SQLite WAL jobs. SQLite is the authoritative
manifest and audit store; Qdrant is the vector index, with one collection per
server-issued 128-bit workspace ID. User slugs never become paths or collection
names. Qdrant payloads hold opaque IDs only; document text stays in private SQLite.
No external orchestrator, agents, automatic enrichment or global reset is used.

All routes except `GET /health` require `Authorization: Bearer TOKEN`. The owner
key is generated only by explicit init. Workspace creation returns an independent
256-bit capability once; only its SHA-256 digest is stored. A capability permits
content/jobs/search/cancel/events for its one workspace, not owner administration.
Owner access to all workspaces is intentional. Protect owner config accordingly.
No browser CORS origins are enabled; docs/OpenAPI, public metrics and traces are absent.

| Method / path | Contract |
| --- | --- |
| GET /health | 200 ready or 503 unavailable for Qdrant, no host/config/model details; no generation or model acquisition |
| GET /workspaces | Only caller-authorized active workspaces |
| POST /workspaces | Owner; JSON slug matching `[a-z][a-z0-9-]{0,47}`; unique, strict ASCII |
| DELETE /workspaces/{id}?confirm={id} | Owner; exact ID confirmation, tombstone and audit; Qdrant outage leaves DELETING and requires explicit retry |
| POST /workspaces/{id}/documents?filename=orchard.txt | Raw streamed bytes, permitted MIME and strict basename; 202 durable job |
| GET /workspaces/{id}/documents | Committed document IDs, filenames and SHA-256 |
| GET /workspaces/{id}/documents/{document}/content | Authorized original bytes as attachment, octet-stream/nosniff |
| GET /workspaces/{id}/chunks/{chunk} | Persisted text, offsets, page, ordinal, document/hash; citation verification |
| GET /workspaces/{id}/jobs/{job} | State/checkpoint/fixed error codes, never uploaded bytes |
| POST /workspaces/{id}/jobs/{job}/cancel | Cancellation of queued/running work; no publishing partial data |
| POST /workspaces/{id}/search | JSON query, limit 1..10, rerank boolean; matched/no_match, verifiable excerpts and ranking provenance |
| POST /workspaces/{id}/ask | Same query; generation_disabled by default; optional real bounded adapter |
| GET /workspaces/{id}/events | Last 100 sanitized metadata audit records; no text, queries, credentials or paths |

## Ingestion and recovery

A document ID hashes format + content hash. A chunk ID is UUIDv5(workspace,
document:ordinal). The durable job stores input before returning 202; stages are
stored/extracted/embedded/indexed/committed. States: QUEUED, RUNNING, COMPLETED,
FAILED, CANCELLED. Parsing is an isolated subprocess (10 CPU seconds, 512 MiB address
space, 15-second wall timeout, 32 file descriptors, no output files). UTF-8, PDF
text-only and DOCX paragraph extraction v1 are supported; no OCR, macros, external
relationships or embedded content are executed. TXT/DOCX page is null, PDF page is
one-based. Offsets refer to the exact extracted page text; chunks retain that text.

Qdrant upserts deterministic IDs with wait=true. Only after all writes acknowledge
does one SQLite transaction insert document/chunks and mark COMPLETED. Search
filters vectors by committed document IDs and joins persisted chunks; staged or
orphaned vectors cannot appear. Cancelled/failed jobs publish no manifest. Startup
under the exclusive lock returns uncertain RUNNING jobs to QUEUED. Repeated upserts
are idempotent; no collection is cleared. Failed jobs retain bounded input for
explicit resubmission; completed/cancelled jobs release their job input. Input is
retained once in the immutable source document for citation/export verification.
No paid call is part of a job or restart recovery. There is no exactly-once claim.

Bounds: 4 MiB upload, 20-second upload/JSON receive deadline, 16 KiB JSON, 100 PDF
pages, 2 MiB decoded PDF page stream, 8 MiB total expanded DOCX with <=256 entries
and <=200 compression ratio, 200k extracted characters, <=320 chunks/document,
4096 committed chunks/workspace, 128 jobs/workspace, 2048 jobs/installation,
32 queued/running jobs globally, 64 workspaces. Limits reject rather than truncate
accepted source text. Queries: 1000 chars, 64 dense and lexical candidates, <=10
results, <=800 chars/excerpt. API: 16 simultaneous requests, 120 authenticated
requests/key/minute; server connection cap 32. Reverse proxy must also enforce
connection/header/body limits; use loopback/private networking until configured.

## Retrieval and generation

Pinned MiniLM ONNX model: 384 dimensions, max 256 tokens, attention-mask mean pooling
and L2 normalization. Index metadata includes exact model/revision, dimension,
normalization and chunk/index schema. Query detects metadata and Qdrant dimension
mismatch; no automatic migration. Dense cosine >=.35 and positive BM25 contribute
to RRF(k=60). Optional deterministic CPU term-coverage reranker adds .02*coverage.
Ties use chunk ID. This is a transparent lexical reranker, not a cross-encoder or
benchmark-quality claim. No learned reranking model is downloaded. No-match uses
these declared relevance rules; similarity thresholds are not measured hit rate/MRR.

The optional OpenAI-compatible adapter uses one request, no tools/fallback/retries,
explicit HTTPS endpoint (HTTP only on loopback), configured model and key environment.
Retrieved content remains lower-trust data in a separate JSON user message. Returned
citation IDs must belong to authorized persisted chunks, with explicit in-answer
markers. This verifies citation membership, not factual entailment. See provider
docs for ceilings and limitations. No prompt/answer traces are stored.
