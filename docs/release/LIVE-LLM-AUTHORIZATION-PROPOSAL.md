# Separate LIVE LLM proposal — NOT AUTHORIZED / NOT EXECUTED

RAG-15 explicitly requires one genuine provider-generated grounded answer. All
current model acceptance uses CPU embeddings only. No generation or provider
availability/credential check is performed by this verification campaign.

Proposed future operator-approved test:

- Provider: OpenAI API, explicit HTTPS `https://api.openai.com/v1`.
- Exact proposed model: `gpt-4.1-mini-2025-04-14`. Revalidate public availability and
  account access at approval time; never substitute another model automatically.
  The official page currently marks this snapshot deprecated; it is not a long-term
  availability promise. A different model requires a new specific proposal.
- Privacy: send only the fictional orchard question and <=1500 characters from
  authorized synthetic chunks. No operator documents, tokens, paths or chat history.
  API data is not used for training by default; standard abuse-monitoring retention
  can be up to 30 days. Do not claim zero retention without an approved account policy.
  See [official data controls](https://developers.openai.com/api/docs/guides/your-data).
- Billing: requires an already funded, explicitly approved operator API account;
  do not enable billing or buy credits. Public model pricing is $0.40/million input
  tokens and $1.60/million output tokens; recheck prices before authorization.
  With <=16000 conservative input-token upper bound and <=128 output tokens,
  estimated inference charge is below $0.007, excluding taxes/account conditions.
  Proposed operator spend allowance: at most $0.01. Provider billing cannot be
  hard-capped solely by an application token parameter.
  [Official model/pricing](https://developers.openai.com/api/docs/models/gpt-4.1-mini).
- Maximum requests: **1 total**; no retry, failover, startup check, tool or enrichment.
- Maximum requested output: **128 tokens**; context 1500 chars; request body <=16kB;
  response <=32KiB; hard subprocess wall deadline 20 seconds.
- Credential: operator configures the existing private environment variable locally;
  never send it in chat, source, GitHub secrets for this campaign, logs or artifacts.
- Evidence: tested source/image SHA, persisted authorized chunk IDs/hash/page,
  request count and configured ceilings, provider model/usage/latency/status,
  returned sentence with a valid persisted citation, and manual semantic grounding
  against the fictional source. Publish no key or private request header.
- Failure/incomplete/invalid citation: fail honestly and keep RAG-15 BLOCKED. A
  second call or a different model requires new explicit approval.

This file is a proposal, not permission and not a selectable fixture provider.
