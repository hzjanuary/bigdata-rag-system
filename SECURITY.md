# Security policy

This is an early self-hosted source preview. No version currently has an SLA or
production certification. Supported security testing targets the current SPEC-001
branch with Python 3.12, one API process, private Qdrant and the pinned CPU model.
See docs/security-model.md for threats, trust boundaries and limitations.

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
