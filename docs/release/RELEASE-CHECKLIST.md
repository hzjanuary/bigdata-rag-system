# Publication review checklist

This checklist does not authorize publication. Source preview and image distribution
have independent decisions in verification.md; LIVE provider inference stays separate.

- [ ] Verify exact reviewed source SHA, clean worktree, baseline ancestry and unchanged authoritative spec.
- [x] Run all deterministic tests, lint/format, hashed locked install and independent clean clone walkthrough. (U/C: 99 passed; separate Q: 1 passed.)
- [x] Verify tracked-file/source archive inventory, current/history secret scans, private data exclusions and license gate. Exact archive is generated after the delivery commit; raw/model hash review remains disclosed.
- [ ] Retain exact source archive checksum, CPU image manifest/config identity and OCI source label.
- [x] Verify actual approved CPU model checksum/revision, pooling/normalization, TXT/PDF/DOCX corpus and persisted citations. One same-project campaign: 34 checks PASS.
- [x] Verify real Qdrant outage/restart, actual worker crash recovery, no ingest reset, independent backup/restore and ACL.
- [ ] Review runtime and optional UI dependency/license SBOM, OS/Python scanner raw reports and unresolved findings.
- [ ] Report actual remote CI state. A local workflow file or local green tests are not remote CI success.
- [ ] Keep LIVE provider RAG-15 BLOCKED until a separate approved bounded real call and evidence exist.
- [x] Record source-preview GO/NO-GO separately from image-security GO/NO-GO, with residual risks and reviewer rationale. Both NO-GO for distinct reasons; see verification.md.
- [ ] Obtain separate permission before any push, tag, merge, source/image publication or remote deployment.

GPU is unvalidated and not shipped. The optional UI is a client behind the same API
boundary; its image has a separate SBOM/security surface and must be scanned before
it is distributed. Do not infer image approval from a source-preview decision.
