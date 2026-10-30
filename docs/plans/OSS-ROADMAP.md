# BigData RAG - OSS Implementation Roadmap

Planning baseline: main `74931fedcf99408e8b15b9052c0e8aed1fd6d8fc`; SPEC-001 is authoritative. This file is a proposed roadmap, not a claim of runtime validation.

## Release posture

- v0.1 source-preview scope: a secure CPU-first RAG service where real operator documents can be ingested and cited per workspace, using Qdrant for vectors and optional real answer generation.
- Qdrant is intrinsic to this product. Optional Streamlit/GPU cannot weaken API authorization and must not be required for fresh bootstrapping.
- Do not import example big datasets or download models automatically as a shortcut to a green smoke test.

| Sequence | Work package | Required output | Exit gate |
| --- | --- | --- | --- |
| S0 | Inventory and threat model | Endpoint/ACL matrix, tracked data/history audit, dataset/model licenses, baseline SHA, failing regression cases | No hard-coded user data in intended source, security defect reproduction captured |
| S1 | Auth and workspace boundary | Operator config init, strict workspace IDs, ACL on query/ingest/metrics/delete, CLI, restricted CORS | Traversal, cross-workspace and anonymous deletion tests rejected |
| S2 | Safe durable indexing | Bounded uploads/parsers, durable job store, content hashes, Qdrant collection IDs, atomic completion visibility | Real Qdrant job/restart/idempotency tests pass; no implicit reset |
| S3 | Retrieval quality and citations | CPU model install, dimensions/index version, BM25/dense/RRF, rerank, source page/chunk IDs | Real small test corpus returns verifiable citations and no-match signal |
| S4 | Generation and optional UI | Real provider boundary, prompt-injection constraints, budgets, redacted traces, opt-in authenticated Streamlit | No provider config => truthful error; no fabricated answer/source or silent paid call |
| S5 | Release packaging and checks | Pinned CPU image/deps, private Compose, CI, licenses/SBOM, backup/restore, docs | Complete RAG-01..24 matrix, tested source/image identity and source-vs-image signoff |

## First local actions for Codex

1. Inspect actual local HEAD, data directories, model caches and any historical dataset material without touching retained documents.
2. Reproduce API risks: no auth on `/workspaces`/`/pipeline/start`, unchecked `source_dir`, simplistic `_safe_name` and broad Compose host ports. Do not demonstrate destructive deletion on real collections.
3. Test corpus must be original or explicitly licensed and non-sensitive. Record its hash, exact embedding model/version, dimension and Qdrant schema.
4. Create feature branch and a durable plan. Start auth and workspace isolation **before** exposure or adding new ingestion modes.

## Evidence policy

- Offline unit fixtures cannot substitute for a genuine Qdrant + CPU embedding model run or a real generation response.
- Source preview may be considered separately from image-security approval; do not disable OS CVE scans.
- An ingestion job is not COMPLETE until the committed state is independently readable after restart.
- Backup/restore rehearsals use disposable isolated collections/databases; never reset existing Qdrant volumes.
- No provider calls, dataset downloads, push, merge, image publication or credential capture without authorization.
