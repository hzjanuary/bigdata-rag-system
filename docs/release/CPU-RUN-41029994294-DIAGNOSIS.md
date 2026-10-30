# Run 41029994294: offline restart diagnosis

The genuine [hosted run](https://github.com/hzjanuary/bigdata-rag-system/actions/runs/41029994294)
tested `ba78e94d82b7972e96a9bae962cbb8ada73d6619`, attempt 1. Reservation and
official pinned acquisition succeeded. The campaign is **consumed and FAIL**;
marker `123977248159` is retained. No rerun/label/marker mutation or model acquisition
was performed during this investigation.

Artifact `12966475279` was downloaded and its ZIP SHA-256 verified:
`1caddf93d9ecb1616eac35cd925c6bff1bcdf89fbfe82607de3e3195d3fb5863`.
ZIP CRC and every manifest file checksum/size pass. Original bytes/logs remain
under ignored `.local/cpu-run-diagnosis-41029994294/`; hashes and sanitized analysis
are in [machine evidence](evidence/cpu-run-41029994294-diagnosis.json).

## What the hosted evidence establishes

There are 21 PASS checks before the restart checkpoint, including genuine CPU ONNX
pooling/L2, real TXT/PDF/DOCX indexing, PDF page citations, hybrid/rerank, isolation,
idempotence and disabled generation. Model revision is
`10dbd2f06a8baf40ad285b037edda610c1b9a57c`, ONNX SHA-256
`6fd5d72fe4589f189f8ebc006442dbb529bb7ce38f8082112682524616046452`.
Actual pooling reference error is `1.7898752063816303e-08`, batch/single error 0;
provider is CPUExecutionProvider only.

The exception is the named assertion, after the health wait succeeded. However,
the original private runner result was **not uploaded** and is unavailable. Both
raw reporting and sanitization omit the post-restart job/search values at this
checkpoint. The boolean combines job completion with exact retrieval equality and
short-circuits. It therefore cannot prove which operand failed on that hosted run.
Do not infer a missing job or a particular post-restart float from the public report.
Later outage/crash/restore phases did not execute.

## Separating the failure modes

| Concern | Hosted evidence | Controlled offline reproduction |
| --- | --- | --- |
| Durable job state | Post-restart state not exported | First job COMPLETED; all three job rows unchanged |
| SQLite/index contents | No post-restart snapshot | Four chunks unchanged by identity/content hash |
| Qdrant persistence | Only API was restarted at the failed step; no post-state exported | Two collections' full point/vector/payload hashes unchanged across API restart; also recovered unchanged after Qdrant restart |
| API readiness | Health wait reached HTTP 200 | Health and search HTTP 200 after actual API process replacement |
| Retrieval identity/order/citations | Only pre-restart result exported | Identical ordered hits, metadata, source text/citations and all other fields |
| Exact equality | Combined assertion FAIL | False solely because one BM25 float changed by one ULP |

Offline reproduction used the already cached, independently hash-verified model,
existing local Qdrant image, fresh private SQLite state/volume, synthetic corpus,
real CPU embeddings and two API processes with hash seeds 0 and 1. API connections
were restricted to loopback; Qdrant telemetry was disabled. It was a bounded local
restart diagnosis, not a second independent-host acceptance campaign. Created state
and the stopped Qdrant container/volume are retained; original operator data is untouched.

One auxiliary local Qdrant-restart observation initially timed out because Docker
reassigned the randomly published host port. Server logs show recovered collections;
rediscovering the assigned port yielded readiness 200 and identical hashes. Both
the failed observation and follow-up are preserved. The hosted campaign uses fixed
Compose internal DNS, so this local probe plumbing is not attributed to that run.

## Confirmed production mechanism and focused regression

`rank()` creates query terms as a set and adds BM25 contributions in its iteration
order. Python process hash randomization changes that order; floating-point addition
is not associative. Holding corpus and dense scores fixed in 12 fresh offline Python
processes reproduces three distinct BM25 encodings. This requires neither ONNX nor
Qdrant and isolates the production arithmetic from storage/readiness.

The actual local API restart changed only:

```text
matches[0].ranking.bm25
3.292419763002416 -> 3.2924197630024166
absolute delta = 4.440892098500626e-16 (1 ULP)
```

This establishes a real cross-process numerical nondeterminism defect and a
matching cause for the named assertion locally. It is strongly consistent with the
hosted failure; the missing hosted post-state prevents proving it was that run's
only difference. No local evidence indicates lost jobs, points or reordered hits.
Exact dictionary comparison exposes the defect; it is not dismissed as a bad test.

New `tests/test_rank_process_stability.py` preserves the full ordered output and
scores and compares three fresh hash-seeded processes. Results actually executed:

- Current production: **one FAIL**, reproducing the determinism violation.
- Isolated package copy with one-line proposal: **one PASS**.
- Existing deterministic suite, explicitly excluding the new red regression:
  **154 PASS / one skipped**. New test Ruff/Black checks pass.

Production source remains unchanged. Proposed patch is retained at
`.local/cpu-run-diagnosis-41029994294/proposed-deterministic-bm25.patch`:

```diff
-        for term in terms:
+        for term in sorted(terms):
```

Canonical traversal is the minimal remediation. Merely rounding scores, fixing a
global process hash seed or relaxing equality would hide the confirmed defect.
Separately, improve the checkpoint to record sanitized job state, ordered before/
after identities and numeric differences **before** asserting; split job/readiness/
retrieval assertions and explicitly whitelist that diagnostic block in the exporter.
Do not export credentials/configuration or database rows. Existing tolerant restore
comparison accepts the local ULP delta diagnostically; it was not used to relabel
the hosted run PASS or weaken the restart criterion.

## Disposition and authorization boundary

RAG-12 explicitly requires deterministic dense/BM25/rerank. Its former PASS tests
covered within-process behavior; the new counterexample makes it **FAIL pending
correction**. Current assessment: **20 PASS / two FAIL / two BLOCKED**. RAG-15/20
stay BLOCKED; RAG-21's known image-security FAIL is unchanged.

A fresh independent-host verification needs **new explicit authorization and a
reviewed campaign identity/budget**. The original campaign was consumed and stopped
before later required scenarios. Preserve its marker/history; do not reapply the
label, rerun that workflow, reacquire a model or bypass replay guards. This turn
only diagnoses and proposes: no production patch, commit, push, merge or publication.
