# Security policy

This is an early self-hosted source preview. No version currently has an SLA or
production certification. Supported security testing targets the current SPEC-001
branch with Python 3.12, one API process, private Qdrant and the pinned CPU model.
See docs/security-model.md for threats, trust boundaries and limitations.

**Security Notice before installation:** v0.1.0 is an early source-only preview,
not a production-certified release. The verified independent CPU/Qdrant campaign
passed 41/41, but image security still FAILS. Per-image HIGH package findings from
retained actual Trivy reports are:

| Image variant | HIGH | CRITICAL |
| --- | --- | --- |
| Core API/worker | 44 | 0 |
| Qdrant | 43 | 0 |
| Optional UI | 44 | 0 |

These counts are not additive unique-CVE totals. Raw reports and scanner exit 1
remain retained; no CVE suppression, severity reduction or gate exception is used.
Pinned builds and default isolation do not resolve these OS findings. No prebuilt
Docker image is approved for publication or production use. Source-only readiness
is a separate owner decision; the complete CI workflow remains FAIL.

RAG-15 remains BLOCKED: genuine generative LLM answering has not been live-verified.
Generation defaults to disabled. No provider availability, billing, privacy or answer
quality claim follows from embedding/Qdrant tests. A new live-provider campaign
needs separate explicit authorization. Current evidence/provenance and limitations:
[verification ledger](docs/release/verification.md).

Do not open an issue containing credentials, source documents, prompts, private
paths, backup files or raw operator logs. Use the repository's GitHub private
vulnerability reporting feature if enabled. If no private reporting channel is
available, open a content-free issue requesting one; do not publish exploit details
or send sensitive data through an unverified address. This policy does not promise
that a private channel has already been enabled on GitHub.

Default protections: generated private owner config, independent workspace
capabilities, API ACLs, no public content/trace/admin endpoints, no wildcard CORS,
loopback API binding, private Qdrant, bounded isolated parsers, no automatic model
acquisition or paid generation, and fixed public error codes. The operator owns
host/TLS/proxy security, backups, trusted local file permissions and provider policy.
No Internet exposure is safe merely because these defaults exist.

Locked dependencies and image digests do not prove vulnerability-free software.
Keep raw scan findings and review source-preview and image-security decisions
separately in docs/release/verification.md. Do not bypass scanner failures or disable
gates to publish. No remote publication is authorized by this document.
