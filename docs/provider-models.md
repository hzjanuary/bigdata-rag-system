# Models, generation and license boundaries

## Explicit local embeddings

Official source: https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
Revision: `10dbd2f06a8baf40ad285b037edda610c1b9a57c` (Apache-2.0 model card).
Only `onnx/model.onnx` (90,405,214 bytes) and `tokenizer.json` (466,247 bytes) are
required. Installer verifies the official revision API, file size, ONNX LFS SHA-256
and tokenizer Git blob ID; writes an integrity manifest to the ignored private cache.
The runtime independently rechecks the pinned hashes on load, not only that manifest.
No Hugging Face model loader or network download is used at runtime.

ONNX SHA-256: `6fd5d72fe4589f189f8ebc006442dbb529bb7ce38f8082112682524616046452`.
`be50c3628f2bf5bb5e3a7f17b1f74611b2561a3a27eeab05e5aa30f411572037` is the SHA-256 of tokenizer.json.
The upstream `1_Pooling/config.json` specifies mean-token pooling and dimension 384.
Implementation uses attention-mask mean pooling, 256-token truncation, L2
normalization and ONNX CPUExecutionProvider only. Telemetry is explicitly disabled.

A single download requires about 91 MB; allow additional runtime/dependency disk
space and roughly 500 MB inference RAM. Acquisition uses network/disk/time, never
a paid model API. The accepted model is general English; multilingual/long-document
quality is not claimed. Text chunking is character-based and embedding truncation
can omit trailing subword tokens for unusually dense text. Persisted citations
still refer to full actual chunks. A new model/revision/schema requires an explicit
future migration, not an automatic reindex or compatibility bypass.

No weights are bundled in source/images. Operators must review the upstream license
and retain required notices when redistributing weights. No external reranker/OCR
model is used; term-coverage-v1 is project-owned deterministic code. Synthetic
example documents are MIT project material. Qdrant is Apache-2.0; Python and Debian
OS packages have their own licenses. See NOTICE, SBOM and license inventory.

## Optional real generation

Production supports one vendor-neutral OpenAI-compatible `POST /chat/completions`
adapter. It is disabled by default. There is no fixture provider, fake completion,
automatic remote fallback, startup provider check or credential discovery.

Edit the private config only after deciding that the provider may receive the
question and selected document excerpts:

```json
{
  "generation_enabled": true,
  "provider_url": "https://your-explicit-provider.example/v1",
  "provider_model": "your-explicit-model",
  "provider_key_env": "RAG_PROVIDER_KEY",
  "provider_timeout": 20,
  "provider_max_tokens": 256,
  "provider_context_chars": 6000
}
```

These fields are additions/edits to the initialized config, not a complete config.
Supply the key through that process environment privately. The adapter checks the
key only when `ask` is requested, not on startup. It sends at most one request,
max 512 requested output tokens, 8000 evidence characters, 16k serialized request
bytes, 32 KiB response, and one generation per 10 seconds per API process. No
retries, tools, contextualization calls or paid enrichment exist. Configured wall
budget is at most 30 seconds, enforced by a killable HTTP subprocess in addition
to bounded connect/read operations. Provider-side billing
and actual token enforcement remain the operator/provider's responsibility.

Document text is untrusted. The system prompt forbids following document
instructions; the adapter permits only citations in the authorized evidence and
requires actual citation markers. No-evidence and disabled/provider/time/budget/
invalid-citation states are explicit. Membership validation cannot guarantee
semantic grounding or defeat every prompt injection; review generated output.
No automatic embedding or LLM call is made for health/config validation.

LIVE generation acceptance requires separate approval and a bounded test with the
operator's own privately configured provider. Mock HTTP tests prove contracts only.
No real provider/model availability, pricing or answer-quality claim is made.
