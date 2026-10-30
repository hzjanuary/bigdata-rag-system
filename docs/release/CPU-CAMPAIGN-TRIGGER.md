# Prepared single CPU campaign for existing Draft PR #1

**PREPARED, NOT INSTALLED OR EXECUTED.** The original independent campaign remains
unconsumed. Do not copy this workflow into `.github/workflows`, create/apply its
label, dispatch, or rerun anything without the final operator decision. This is
not an approval for another model or for generation.

## Exact target and prerequisites

- Repository `hzjanuary/bigdata-rag-system`, existing same-repository Draft PR #1,
  feature branch `feat/spec-001-oss-rag-core`, target main.
- Reviewed/tested source: `d54b899d665b04dff2db3bd8b7415f96d8b36c9a`.
- Genuine PR CI run `41008651605`: source PASS; actual image jobs retain expected
  OS security FAIL. Source artifact ID `12956337422`, ZIP digest
  `sha256:5669244d1b93f2d434129427926d72cd557acc9622558d3779f211480c7b78cc`.
  Its archive/manifest/checksums were independently downloaded and verified.
- Source archive SHA-256:
  `71d0ec6409dde0a07df21d5bc477cfcba6dcec16a5ac455053a6dddefa38f2df`.
- Official model only: `sentence-transformers/all-MiniLM-L6-v2`, revision
  `10dbd2f06a8baf40ad285b037edda610c1b9a57c`, ONNX SHA-256
  `6fd5d72fe4589f189f8ebc006442dbb529bb7ce38f8082112682524616046452`.
  Acquisition at this source SHA permits only the ONNX file and tokenizer with
  exact byte/hash/revision checks, official Hugging Face URLs, 20-second requests
  and a 180-second total deadline. No model cache or mirror substitution.

## Concrete mechanism

The complete [prepared workflow](cpu-once.workflow.yml) is inert under `docs/`.
After a separate review/installation decision, its intended installed path is
`.github/workflows/spec001-cpu-once.yml`. No active workflow was changed during
the JUnit correction. A normal push/synchronize does not start this campaign.

The trigger is **pull_request.labeled** by owner `hzjanuary` on PR #1, with the
exact label `spec001-cpu-once-d54b899d665b04dff2db3bd8b7415f96d8b36c9a`.
The owner must apply that label through the GitHub UI or their own authenticated
CLI after inspecting the installed workflow and source outcome. The agent has
not created the label or performed this action.

This avoids the already-spent `pull_request.opened` event and the default-branch
limitations of manual dispatch. `workflow_dispatch`, `repository_dispatch`,
`issue_comment` and `workflow_run` are not used. PR label events are documented
in [GitHub's trigger reference](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#pull_request);
the same reference states the default-branch prerequisite for dispatch. An
ordinary rerun retains its original SHA/ref and is not a way to test new source:
[GitHub rerun behavior](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/re-run-workflows-and-jobs).

The prepared workflow checks out the **exact reviewed target**, not a moving
branch or PR merge ref. Its later installation commit is a different identity,
recorded as `workflow_sha`/`pr_head_sha` in the consumption report. The guard
requires that target to remain an ancestor and permits only docs and this one
workflow path in the intervening diff, including prior paths for renames. Runtime,
packaging, other workflow changes, incomplete comparisons, more than ten intervening
commits, changed PR state/head, missing source history/artifact or API errors stop
before acquisition. It does not claim the installation HEAD itself was CPU-tested.

## Single-use controls and limits

1. The entire workflow uses one fixed concurrency group with cancellation disabled.
   Duplicate label events are serialized; they do not run campaigns in parallel.
2. Both jobs reject `run_attempt != 1`. UI/CLI full-job or single-job reruns cannot
   run the acquisition/campaign. The CPU job also checks this in a shell step.
3. Before any model acquisition, the reservation job queries the pinned source's
   check runs and refuses an existing `spec001-cpu-pr1-consumed` marker. It then
   writes that marker and a checksummed `consumption.json` artifact. A marker is a
   **budget reservation, not an acceptance or security PASS**; its neutral status
   does not change any existing source/image gate.
4. Only the reservation job requests `checks: write`; the CPU job has read-only
   repository access. The built-in ephemeral GitHub App token is used solely for
   GitHub API checks/marker creation, never model inference. No new PAT, private
   credentials or paid account are needed. These job-specific permissions are
   proposed only: no repository permission/settings change has been made.
5. The template expires at **2026-10-31 00:00:00 UTC** (07:00 Vietnam). It fails
   closed thereafter. This is less than one day from preparation, bounding the
   period in which its check marker must survive. Do not extend the deadline or
   change the target silently.
6. Budget is conservatively consumed at marker creation, even if checkout/build,
   download or acceptance later fails. Preserve its check ID, run ID, source and
   workflow SHAs, acquisition/acceptance step outcomes and actual raw reports.
   There is no automatic retry, rollback or deletion of the marker.

[GitHub Checks API](https://docs.github.com/en/rest/checks/runs#create-a-check-run)
supports the marker through GitHub App tokens with checks write permission. The
[built-in token is a GitHub App installation token](https://docs.github.com/en/actions/concepts/security/github_token).
Checks/run/artifact retention is finite; current [GitHub retention documentation](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository)
describes configurable retention and its application to checks. The expiry avoids
depending on a marker beyond that retention window.

**Limit:** this is not an immutable external single-use authority. An administrator
could delete check history, alter the guard/permissions, or install another workflow.
GitHub's live checks-write policy/label execution has not been exercised because
doing so would consume the campaign. API, marker or permission failure must stop;
never fall back to an unguarded campaign. Static validation is not live trigger
verification. The owner must review the installed definition and perform the one
final label action; do not claim absolute exactly-once execution under admin changes.

## Allowed campaign and evidence

Fresh GitHub-hosted Ubuntu 24.04, clean checkout, fresh CPU images/private runtime
configuration, existing bounded official acquisition and one synthetic TXT/PDF/DOCX
Qdrant campaign. The script records 384-dimensional vectors and tokenization
metadata, masked mean pooling/L2 reference tolerances, actual chunk
provenance/page citations, isolation, hybrid/rerank, durable jobs/retry/crash recovery,
outage/recovery, independent restore and resource limits. No generation/provider
call, paid inference, release, deploy, push, merge or image publication step exists.

The reservation artifact and final campaign artifact have the unchanged evidence
guard and checksum manifest. Failed/partial outcomes remain evidence, never PASS.
Collect artifact ZIP digests, every manifest checksum, actual model revision/file
hashes, host/source/image identity, vectors/Qdrant state/citations and consumption
marker. RAG-20 stays BLOCKED until that genuine campaign completes successfully;
RAG-15 and RAG-21 retain their independent live/security blockers.

## Final operator action required

Review this inert template, the exact target/source artifact, the limited check-write
permission and the expiry. If approved, install it with a normal feature-branch push
and review that installation SHA/diff; then apply the exact owner label to PR #1
once before expiry. This turn neither installs nor executes it. If the deadline or
retained prerequisites expire first, request a new explicit operator decision rather
than silently refreshing the authority or consuming a replacement campaign.
