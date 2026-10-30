# CPU/Qdrant remediation campaign 2 — installed preparation, owner activation only

> **COMPLETED / CONSUMED — historical preparation below.** Owner activation ran
> campaign `41040402221` once at source `287212be8f5683221d2449158331e59d4c639c15`:
> 41/41 PASS, attempt 1. Marker `124011605279` remains permanently consumed.
> Do not apply/reapply a label, rerun, reset or acquire another model package.
> Both cpuq1 and cpuq2 authorizations are consumed. See the current
> [verification ledger](verification.md) and [verified evidence](evidence/final-independent-acceptance.json).

The owner authorizes **at most ONE additional independently triggered campaign**.
Preparation never creates/applies a label, reserves a marker or downloads a model.
The final reviewed SHA and exact label are reported only after normal push and
successful genuine source CI. No ancestor or moving-branch allowance.

## Identity, window and budget

- Campaign: `spec001-pr1-cpu-qdrant-remediation-2`.
- New marker: `spec001-cpu-pr1-remediation-2-consumed`.
- Label: `cpuq2:<exact lowercase 40-character current PR #1 HEAD SHA>`.
- Existing workflow path: `.github/workflows/spec001-cpu-once.yml`; displayed name
  `spec001-cpu-remediation-2-pr1`. Policy: `scripts/cpu_campaign.py`.
- Same repository `hzjanuary/bigdata-rag-system`, owner sender and actor `hzjanuary`,
  feature branch `feat/spec-001-oss-rag-core`, main base, open Draft PR #1.
- Fixed window: **2026-10-30 10:00:00 UTC through 2026-10-31 00:00:00 UTC**
  (expiry 07:00 Vietnam). Both boundaries are enforced; no automatic extension.
- At most one new campaign attempt and one bounded official model acquisition;
  zero generative/paid API requests, fallback providers, mirrors or retries.

Only `sentence-transformers/all-MiniLM-L6-v2`, revision
`10dbd2f06a8baf40ad285b037edda610c1b9a57c`, ONNX SHA-256
`6fd5d72fe4589f189f8ebc006442dbb529bb7ce38f8082112682524616046452`.
Unchanged acquisition permits exactly the ONNX file and tokenizer, fixed sizes/
hashes/upstream metadata, official Hugging Face repository, 20-second requests and
180-second total bound. Local validation reuses existing verified cache; no local
model acquisition occurred.

## The first campaign remains permanently accounted for

The ONLY accepted prior attempt is run **41029994294**, attempt 1, original head
`ba78e94d82b7972e96a9bae962cbb8ada73d6619`, failed campaign job `123977173196`.
Its consumed marker is **123977248159**, named `spec001-cpu-pr1-consumed`, external
ID `spec001-pr1-cpu-qdrant-once:41029994294`, created by GitHub Actions.

Required public artifact: **12966475279**, ZIP digest
`sha256:1caddf93d9ecb1616eac35cd925c6bff1bcdf89fbfe82607de3e3195d3fb5863`.
The guard checks the real run/actor/head/status/attempt/job steps, real marker,
nonexpired artifact, ZIP digest/CRC/exact checksum manifest and consumption receipt.
Receipt must retain consumed=true, successful pinned acquisition, failed acceptance
and the original source/marker/model identity. Downloaded original logs must retain
`AssertionError: API process restart preserves job and retrieval`.

The private runner result was never uploaded. Validating all retained public failure
evidence does not reconstruct its post-restart values or prove there was no additional
hosted cause. The preserved [diagnosis](CPU-RUN-41029994294-DIAGNOSIS.md) records that
limit. No marker/record is deleted, reset, relabeled unused or broadly exempted.

## Preconditions and replay controls

1. Label/event/checkout/live PR/source verification/receipt SHA identities match
   exactly. Wrong owner, repository, branch, PR, stale SHA, old cpuq1 label or rerun
   rejects before acquisition. Both job expressions and policy require attempt 1.
2. Complete bounded run/job-attempt history is required for both CI workflows.
   Original failure must still appear exactly once and retain its exact status.
   Every other unskipped campaign/CPU/reservation job rejects, including attempts
   that failed before writing a consumption marker. Missing/inconsistent evidence,
   incomplete pagination and API errors reject; there is no unguarded fallback.
3. Across all visible source SHAs, exactly the known original marker is required;
   any unexpected old marker or any new remediation marker rejects.
4. The current exact SHA needs successful source/secret/export/upload steps and a
   nonexpired source artifact. The guard downloads that ZIP, verifies GitHub digest,
   every manifest file size/hash and the source tar's exact members/hashes/SHA.
   Known image HIGH failures remain red and do not become a source/security PASS.
5. One shared workflow concurrency group serializes all versions/events. After all
   checks, reserve the distinct new marker BEFORE building/downloading. Verify its
   receipt, original failure evidence, source artifact/run and current PR again
   immediately before acquisition. Original run ID cannot impersonate a new run.
6. Reservation conservatively consumes the new budget even on subsequent failure.
   A started/rejected new attempt also blocks automatic retry. No rerun, label
   remove/re-add, reset or reinterpretation as unused is allowed.

Read-only preparation audit uses a client that rejects every API write. Only the
live campaign job has checks-write permission for its own reservation; model steps
receive no token environment. Official GitHub archive redirects are bounded and
never forwarded an Authorization header. API/archive downloads have fixed byte/time
limits and no retries. No new credential/account/billing is introduced.

Push/synchronize execute only the offline configuration check; campaign is SKIPPED.
Receipts say `consumed_by_this_event=false`, not that an old budget is unused.
No `pull_request_target`, workflow_dispatch/default-branch assumption or new PR.
[GitHub event reference](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#pull_request).

Administrative deletion of history/checks, retention changes or policy edits prevent
an absolute mathematically exactly-once guarantee. The short fixed window and
fail-closed evidence requirements bound that risk; missing history never authorizes
another attempt. Live reservation write is not exercised during preparation.

## Complete fresh-host path and evidence

Fresh GitHub-hosted Ubuntu 24.04, exact checkout, fresh private synthetic configuration
and actual CPU/core+Qdrant images. All previously unexecuted stages remain mandatory:
TXT/PDF/DOCX, CPU-only pooling/L2, hybrid/rerank/isolation/citations, exact deterministic
API restart, durable jobs, Qdrant outage/retry, RUNNING worker crash/recovery and
independent backup/restore. The local corrected path passed all 41 checks; that is
local evidence, not independent host qualification.

Restart evidence is captured BEFORE eight individual assertions: readiness, job,
document/chunk identities, retrieval status, ordered hits, provenance and exact score
fingerprints/deltas. No loose numerical tolerance replaces this deterministic check.
Only allowlisted metadata/hashes/synthetic results are public. No raw operator
content, credentials, capability tokens, configuration, SQLite files or Qdrant backup
contents. Unknown fields are stripped; exact fingerprints still detect schema drift.

Campaign receipts retain old and new identities separately, actual model/CPU/Qdrant/
image results and measured elapsed time. Existing 2,000,000-byte per-file evidence
gate, checksum manifest and GitHub artifact ZIP digest remain mandatory. Partial
failures remain FAIL; no result is invented for unexecuted stages.

## Separate final owner action

After final source CI/artifacts and SHA review, confirm PR #1 still has that exact
head, remains Draft, and inactive configuration runs are complete. As `hzjanuary`,
create/apply the exact **cpuq2:<reported final full SHA>** label once before expiry.
Do not reapply cpuq1 or rerun the old workflow. Preparation stops before creating
or attaching cpuq2. If anything expires or changes, obtain a new explicit decision.

RAG-12 may be PASS only on demonstrated corrected deterministic evidence. RAG-20
stays BLOCKED until this independent campaign succeeds. RAG-15 remains BLOCKED;
RAG-21 remains FAIL while known image security findings are unresolved. No merge,
release/tag, image publication, deployment or generative campaign is authorized.
