# Security model and threat analysis

Scope: one trusted operator, one API instance and worker, SQLite WAL, private Qdrant. Workspace capabilities permit independent client authorization; owner has administrative access to all workspaces. Host root, Docker administrator and authorized owner are trusted. No SaaS isolation claim.

| Boundary / threat | Required control | Verification |
| --- | --- | --- |
| Anonymous API / content, trace, deletion disclosure | Fail-closed bearer auth, no wildcard CORS, public health reveals only readiness | Route inventory and negative API tests |
| Capability for A selects B / confused deputy | ACL lookup before all operations; opaque server UUIDs; no client collection names | Two-workspace adversarial read/job/upload/delete tests |
| Slug/path traversal, Unicode aliases, symlinks | ASCII slug and UUID grammars; private storage; no arbitrary server path API; no-follow import opens | Encoded traversal, symlink, collision tests |
| Malicious upload / zip bomb / parser exhaustion | Stream cap; extension/signature validation; DOCX entry/expanded caps; subprocess CPU/memory/deadline; text/chunk/file/job caps | Oversize/bomb/timeout/invalid-format tests |
| Crash or Qdrant outage mid-index / partial results | SQLite manifest authoritative; staged vectors invisible until atomic commit; durable job states and checkpoints; idempotent point/document IDs | Failure injection, cancellation, actual restart/outage tests |
| Retry resets collection / data loss | No ingest reset operation; explicit workspace-ID deletion confirmation, tombstone and audit | Retry, cross-workspace deletion and confirmation tests |
| Retrieved document prompt injection / exfiltration | No document tools; bounded lower-trust context; fixed system contract; authorized persisted citation allowlist; no provider by default | Hostile document and invalid citation adapter tests |
| Provider loops / accidental spend / secret leaks | Explicit enable, no startup call, one request, token/context/time/rate caps; sanitized errors | Mock HTTP transport and log redaction tests; LIVE separately gated |
| Files/logs/images disclose data | 0600 config, 0700 state; no prompt/text/path logging; allowlisted build context and tracked-file gate | Permission/symlink checks, artifact and image inventory |
| Dependency/supply chain compromise | Locked hashes, pinned image digests, SBOM and raw vulnerability/license findings | Clean clone install, CI/scanners; image GO independently gated |
| Backup inconsistency | Stop writers; SQLite backup plus Qdrant snapshot; isolated restore with source/manifest comparison | Disposable backup/restore rehearsal |

Residual limits: an LLM can still be influenced by hostile text; citation validation proves attribution membership, not semantic entailment. Parser sandbox is resource containment, not a hostile-code VM. Local administrator can access plaintext documents/model/index. SQLite is single-instance; no concurrent multi-host writers. TLS/authenticated reverse proxy is required before any Internet exposure. Remote inference sends selected excerpts to that provider and requires an operator privacy decision.
