# Post-v0.1.0 repository branding and retirement review

**Preparation only. Do not merge this PR, rename, change GitHub metadata, disable
workflows or publish anything without the owner's separate approval.**

Read-only audit on 2026-10-30 unexpectedly found that repository ID **1157806659**
already has canonical name **hzjanuary/multi-workspace-rag-engine**, the requested
About description and the proposed topics. Requests to the original name resolve
to the same repository. This preparation did not perform that external rename or
metadata update. No second rename is needed while this state holds.

## Intended brand and compatibility boundary

- Repository/product name: **Multi-Workspace RAG Engine**.
- Canonical repository: https://github.com/hzjanuary/multi-workspace-rag-engine.
- About description: Self-hosted, CPU-first multi-workspace RAG engine with secure document ingestion, ONNX embeddings, Qdrant hybrid search, durable jobs, and source-grounded citations.
- Reviewed settings payload: [repository-settings.json](repository-settings.json).
- Reviewed topic list: [repository-topics.json](repository-topics.json). Its 17 topics
  already match current About metadata; this is a prepared payload, not a PUT request.
- Reference audit: [repository-reference-audit.json](repository-reference-audit.json),
  based on release commit bd2c25ed51a462e6cfe2053a6286a8e55b7f5a70.

README/SECURITY current branding and canonical links may change without changing
referenced run/artifact IDs. CONTRIBUTING clarifies ordinary source CI versus
consumed historical campaigns. Operational names deliberately remain compatible:
`workspace-rag-core`, `rag`, `rag_core`, API title `Workspace RAG Core`, local
`workspace-rag-{core,qdrant,ui}:local` image tags, RAG_* environment variables,
config/storage locations and existing branches. LICENSE/NOTICE, production code,
CLI/schema, dependency locks, Docker/Compose, models and all CI bytes are unchanged.
This is not a package/API/container rename or a new runtime qualification.

## Historical identities that must not be rewritten

Keep original strings and bytes in SPEC-001/roadmap/execution plans, verification
ledger, release notes, docs/release/evidence/*, historical workflow templates,
scripts/cpu_campaign.py and .github/workflows/spec001-cpu-once.yml. Those names and
URLs identify the repository as tested; a global replacement would falsify history.
The script's original REPO constant is intentional. Do not substitute the new name
or relax guards to make a consumed campaign executable again.

- Release ID 428936675, annotated tag v0.1.0 object
  1cbd31e09216d44a63685cffe5c212b35264d7a6, release commit
  bd2c25ed51a462e6cfe2053a6286a8e55b7f5a70.
- Independently tested runtime 287212be8f5683221d2449158331e59d4c639c15.
- cpuq1 run 41029994294: FAIL/consumed, marker 123977248159.
- cpuq2 run 41040402221: 41/41 PASS/consumed, marker 124011605279; artifact SHA-256
  30a57bc2c2a7df2a6b0399936134a05e88d5df8da00ff8465e05f9458734164c.
- Both labels, attempts, logs, sanitized receipts and original artifacts remain.
  Never reset, reapply, rerun or reinterpret a budget as unused.
- SPEC-001 remains 22 PASS / one FAIL / one BLOCKED: RAG-15 BLOCKED live generation,
  RAG-21 FAIL image security. Core 44 / Qdrant 43 / UI 44 HIGH, zero CRITICAL in recorded
  scans; separate per-image findings, not additive unique CVEs. No gate waiver.

Original v0.1.0 ZIP SHA-256:
394459890e7eca3899d6278607931855a587445964b2fe728d2470d07489f6fc.
Original tar.gz SHA-256:
9b270a1246cac5e58f3bea6c04b518513afd48de0ff65771807c6e983873074d.
Retain those original bytes and records. GitHub-generated archives include the repo
name in their root directory, so a rename changes that directory and can change the
container checksum while all 115 release file contents/modes remain identical.
Record newly downloaded container checksums separately; do not overwrite old
checksums, move the tag, edit historical receipts or create a replacement release.
[GitHub archive guarantees](https://docs.github.com/en/repositories/working-with-files/using-files/downloading-source-code-archives).

## Consumed workflow retirement proposal — no state change in this PR

Prefer **manually disable the existing workflow**, retaining its exact file and
workflow ID **401427716** (`spec001-cpu-remediation-2-pr1`). No deletion/move/rename
of the workflow, scripts, historical runs, artifacts, markers or activation labels.
This preserves the strongest audit trail and requires no workflow/test rewrites.
Keep locked-core/source and all three image/security jobs enabled unchanged.

Before the approved disable action, inspect its current run queue: disabling does
not cancel already running jobs. If any campaign job is unexpectedly active, stop
and report it rather than triggering/cancelling/retrying it automatically.
GitHub documents that a disabled workflow cannot trigger or rerun historical jobs
until enabled again. Administrators can re-enable it, so this is not irreversible
exactly-once protection. Consumption markers/history and original fail-closed
owner/PR/SHA/window guards remain necessary evidence. Missing/expired history is
never permission to run again. Preserve local raw evidence before Actions retention
expires; do not extend/reupload it through another campaign.
[GitHub disable/re-enable semantics](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/disable-and-enable-workflows).

This PR deliberately leaves the active workflow byte-identical and does not issue
a disable API request. A future decision to replace it with an inert notice must
be a separate reviewed workflow change with regression coverage. Do not broaden
push/label conditions, add workflow_dispatch to the campaign, change REPO, remove
reservation checks or restore acquisition commands under a new identity.

## Redirects and CI impacts

GitHub redirects repository web traffic and Git clone/fetch/push from the original
name. Verify concrete PR/release/run/artifact links after cutover; artifact access
still requires permissions and unexpired retention. Never reuse `bigdata-rag-system`
for another repository: that breaks the historical-name redirects.
GitHub Pages URLs and calls to hosted Actions do not receive those same guarantees.
Current has_pages=false; no hosted action.yml or self-repository `uses:` reference
was found. External callers/integrations cannot be exhaustively discovered from
source alone. [GitHub rename behavior](https://docs.github.com/en/repositories/creating-and-managing-repositories/renaming-a-repository).

Update local remotes explicitly after owner review; renaming the local folder is
optional and not part of this change. Audit external badges/webhooks/OIDC subjects,
GitHub App permissions, package/registry identities and scripts keyed to full_name;
no deployment, secret or package migration is implied. None are changed here.

The existing locked-core workflow has no repository-name comparison; required job
context **source** and Actions integration 15368 stay unchanged. PR events run it
for this new documentation branch; push events are limited to the historical
feat/spec-001-oss-rag-core branch. No automatic main/tag run is claimed. After an
approved merge, an explicitly approved `workflow_dispatch` of ci.yml on main can
verify the final documentation commit without CPU inference. Do not change these
triggers or security thresholds as part of branding.

The historical CPU workflow still has an old-name identity guard. That should fail
closed after rename, and is never a reason to update its identity or execute it.
Its synchronize-only configuration job can emit an inactive receipt for PRs;
opening this PR does not activate a CPU campaign. Proposed manual disable retires
both that noise and campaign entry points without changing source CI.

Keep all three main rulesets active, same IDs and no bypass actors:
26194925 PR/resolved threads; 26194913 deletion/non-fast-forward prohibition;
26194964 strict up-to-date required **source** from integration 15368. A rename must
not be used to recreate the repository or replace these rules with weaker settings.
Read actual effective rules after any owner action; stop if they differ.

## Owner-only cutover commands — NOT executed during preparation

First review this PR and its source/secret/license/workflow results. Merge only
through normal PR rules after separate approval; no force push, auto-merge or
ruleset edits. Fetch that approved merged documentation before using its payloads.
The current API already reports the target name, so the guarded PATCH below should
be a **no-op** in today's state. Do not rename back just to exercise a procedure.

```bash
set -euo pipefail
current_repo=$(gh api repositories/1157806659 --jq '.full_name')
case "$current_repo" in
  hzjanuary/bigdata-rag-system|hzjanuary/multi-workspace-rag-engine) ;;
  *) printf '%s\n' 'Unexpected repository identity; STOP' >&2; exit 1 ;;
esac

# Only after separate approval of CPU workflow retirement, and an empty campaign queue:
gh workflow disable 401427716 --repo "$current_repo"
test "$(gh api "repos/$current_repo/actions/workflows/401427716" --jq '.state')" = disabled_manually

# Only after separate approval of the metadata/rename action:
if [ "$current_repo" = hzjanuary/bigdata-rag-system ]; then
  gh api --method PATCH "repos/$current_repo" \
    --input docs/maintenance/repository-settings.json
else
  printf '%s\n' 'Already renamed; no rename request sent.'
fi

# Optional approved topic replacement; payload already matches today's topics:
gh api --method PUT repos/hzjanuary/multi-workspace-rag-engine/topics \
  --input docs/maintenance/repository-topics.json

git remote set-url origin https://github.com/hzjanuary/multi-workspace-rag-engine.git
git remote -v
```

Then read repository ID/name/description/topics, three rulesets/effective source
requirements, workflow disabled state, PR and release IDs, annotated tag object and
peeled commit. Verify both markers and attempts remain unchanged. Test old-name
redirects without creating a new old-name repository. Download source archives and
compare every release file hash/mode against bd2c25e, recording new container hashes
as a separate rename observation. Confirm no uploaded assets/image publication or
deployments. Do not infer tag contents from the current main README.

If any required check or rule blocks the PR, report the exact condition and stop.
Known image HIGH failures remain visible; this branding PR does not approve image
publication or another model/provider campaign. Stop after preparation for review.
