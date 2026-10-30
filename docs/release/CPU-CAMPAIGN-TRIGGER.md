# Installed one-time CPU/Qdrant trigger — PR #1

Installed configuration is verified without activation. **The owner must perform
the final label action separately. No label is created/applied during preparation.**
The earlier template at `cpu-once.workflow.yml` is historical, not the installed
policy. Its older ancestor-SHA allowance and fixed old target are superseded.

## Identity and explicit activation

Active workflow: `.github/workflows/spec001-cpu-once.yml`. Policy implementation:
`scripts/cpu_campaign.py`. Only same-repository open Draft PR #1 from
`hzjanuary/bigdata-rag-system`, branch `feat/spec-001-oss-rag-core`, base main,
with both event sender and GitHub actor `hzjanuary` may activate.

Label format: **`cpuq1:<exact lowercase full 40-character current PR head SHA>`**.
`cpuq1:` identifies this PR's CPU embedding/Qdrant acceptance campaign. The full
label is 46 characters. The actual activation SHA/label is resolved and reported
only AFTER pushing the final implementation; do not use d54b899 or an ancestor.
An embedded constant cannot equal the hash of its own commit, so the operator's
exact-SHA label is the explicit review/approval binding.

The event head, label, actual checkout, live PR head, source CI head and consumption
receipt must match exactly. No ancestor allowance or moving-branch checkout. The
live PR/label and persistent receipt are rechecked immediately before acquisition.

Uses `pull_request.labeled`, never `pull_request_target`. Push/synchronize execute
only the read-only `configuration` job, which emits `consumed: false` and never
calls the API or a model command. `campaign` is SKIPPED. The old opened-only CPU
job was removed from ci.yml; source/image jobs and security thresholds are intact.
There is no dispatch/manual-rerun fallback or default-branch assumption. See
[GitHub events](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#pull_request).

## Before any model acquisition

- Owner/PR/repository/branch/base/event/label/SHA validation occurs before API calls.
- `run_attempt` must be 1 in job expressions and the policy. Workflow/job reruns
  cannot acquire or run the campaign.
- Complete bounded read-only Actions history is required for ci.yml and the new
  workflow, including all job attempts. A prior unskipped campaign/CPU/reservation
  job, absent job history, incomplete pagination, missing original run anchor or
  API error rejects. No prior-attempt result is treated as unused without evidence.
- Exact-SHA source job must have succeeded, including secret/export/upload steps,
  and have a nonexpired source artifact with SHA-256 digest. Known image gate FAIL
  does not become PASS and does not invalidate the separately verified source job.
- Check-run consumption markers are checked across every source SHA visible in
  both histories. Only after these checks is one persistent marker reserved.
- A checked receipt and marker plus source artifact/run identity and current PR
  are required again before acquisition. Missing evidence has no fallback.

One fixed workflow concurrency group serializes preparation and activation events
without cancelling an active campaign. The marker is written BEFORE building or
downloading. Reservation conservatively consumes the authorization even if a later
step fails. A previous campaign job that started but failed before reservation
blocks automatic retry, without pretending its budget was actually consumed.
The neutral marker records usage only; it does not certify acceptance or bypass
any security check. Preparation does not create it.

Only the campaign job requests checks write for that marker; Actions history and
PR reads use the built-in ephemeral token. Model/acceptance steps do not receive
that token as an environment variable. There is no PAT or new account/billing.
The approval window remains **2026-10-31 00:00 UTC (07:00 Vietnam)**, with no
automatic extension. API calls are bounded, single attempt, official GitHub only;
redirects and oversized replies fail closed.

## Authorized model, stack and public evidence

Only `sentence-transformers/all-MiniLM-L6-v2`, revision
`10dbd2f06a8baf40ad285b037edda610c1b9a57c`. Expected ONNX SHA-256:
`6fd5d72fe4589f189f8ebc006442dbb529bb7ce38f8082112682524616046452`.
Unchanged acquisition permits exactly ONNX plus tokenizer, official pinned Hugging
Face URLs, fixed sizes/hashes, 20-second requests and a 180-second total deadline.
No model substitution, mirror, retry, paid/generative provider or external search.

A fresh GitHub-hosted Ubuntu 24.04 runner builds CPU/core and Qdrant locally, then
runs the existing synthetic TXT/PDF/DOCX campaign once. It checks CPUExecutionProvider,
masked pooling/L2, actual indexing/citations/isolation/hybrid/rerank, durable jobs,
worker crash, outage/restart and independent restore without destructive reset.
No generation config or provider credential is enabled. No release/image publish.

Public artifacts contain bounded environment metadata, acquisition hash proof and
consumption/execution evidence with campaign/run/source/workflow identities, actual
image IDs, CPU vectors/tolerances, citations, individual checks and measured elapsed
time. Raw acceptance output stays outside the export directory. Export projection
drops configuration, unknown fields and SQLite job rows, keeping only state counts
and Qdrant collection summaries. No weights, documents, credentials, backups or DB
files are uploaded. Existing evidence gate and 2,000,000-byte per-file limit apply;
checksums manifest and GitHub artifact ZIP digests protect exported files. Failures
remain FAIL; expected model pins are distinguished from actually verified metadata.

## Replay limitations and final operator procedure

GitHub labels are not a mathematically exactly-once authority. Administrative
deletion of runs/checks, policy/permission changes or another workflow can defeat
history controls. Retention is finite. The fixed short approval window bounds the
marker lifetime; source/history/artifact/permission failures reject, never retry
unguarded. A rejected or partial activation needs a separate operator investigation,
not a normal rerun. Live marker-write permission is not exercised in preparation.

1. Read the final reported remote PR head SHA and the source CI/artifact evidence.
2. Recheck PR #1 still has that exact head, remains Draft and source CI is PASS;
   wait for both inactive-configuration runs to complete. Review installed files.
3. As `hzjanuary`, create the exact `cpuq1:<reported full SHA>` label and apply it
   to existing PR #1 ONCE before expiry. This is the separate activation action;
   the agent does not do it in this task. Do not use an older SHA or another PR.
4. Preserve run/marker IDs and all raw/checksummed outcomes. Do not remove/re-add
   the label or rerun jobs. Inspect partial failures before any further authority.

Until actual independent acceptance succeeds, RAG-20 remains BLOCKED. RAG-15 stays
BLOCKED (no live generation authorization); RAG-21 stays FAIL on known OS findings.
