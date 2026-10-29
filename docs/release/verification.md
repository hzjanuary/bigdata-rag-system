# SPEC-001 verification ledger

Baseline: `74931fedcf99408e8b15b9052c0e8aed1fd6d8fc`. Implementation not yet verified.
The authoritative acceptance wording remains in SPEC-001; no criterion is relaxed here.

| ID | Status | Required evidence |
| --- | --- | --- |
| RAG-01 | NOT_RUN | Fresh clone locked install, source and image inventory |
| RAG-02 | NOT_RUN | Offline startup has no acquisition/inference |
| RAG-03 | NOT_RUN | Private init permissions and overwrite rejection |
| RAG-04 | NOT_RUN | Anonymous/placeholder rejection on every sensitive route |
| RAG-05 | NOT_RUN | Traversal, alias, symlink and collision tests |
| RAG-06 | NOT_RUN | Independent workspace capabilities isolation |
| RAG-07 | NOT_RUN | Upload/import/parser/resource bounds |
| RAG-08 | NOT_RUN | Persisted jobs/checkpoints/restart/idempotency |
| RAG-09 | NOT_RUN | Failed/cancelled jobs and atomic visibility |
| RAG-10 | NOT_RUN | No implicit reset; authorized explicit delete |
| RAG-11 | BLOCKED | Actual licensed CPU model + Qdrant corpus; model download approval pending |
| RAG-12 | NOT_RUN | Dense/BM25/rerank and dimension enforcement |
| RAG-13 | NOT_RUN | Actual source/page/chunk integrity and no match |
| RAG-14 | NOT_RUN | Disabled/default provider and real adapter contract |
| RAG-15 | BLOCKED | Separate approval for bounded LIVE provider run required |
| RAG-16 | NOT_RUN | CLI/API equivalent authenticated journeys; UI boundary |
| RAG-17 | NOT_RUN | End-to-end error/log/trace secret/content redaction |
| RAG-18 | NOT_RUN | Actual Qdrant stop/restart, readiness and durable metadata |
| RAG-19 | NOT_RUN | Disposable consistent backup/restore rehearsal |
| RAG-20 | NOT_RUN | Secure CPU Compose and clean Linux actual image run |
| RAG-21 | NOT_RUN | Locked local checks and actual remote CI separately |
| RAG-22 | NOT_RUN | Exact tracked-source and artifact exclusion adversaries |
| RAG-23 | NOT_RUN | Required docs/license inventory and independent walkthrough |
| RAG-24 | NOT_RUN | Separate source/model/remote-CI/image publication review |

Source-preview: NO-GO pending implementation and evidence. Image security: NO-GO pending actual image scans and disposition. No publication authorized.
