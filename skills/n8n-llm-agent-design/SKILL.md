---
name: n8n-llm-agent-design
description: Standard for designing and reviewing ANY n8n flow that uses an LLM (AI Agent, Basic LLM Chain, chat model node, or HTTP call to an LLM API). Use BEFORE writing or editing an agent's system prompt, when a flow includes an LLM, when replies/classification are low-quality, or when deciding what belongs in the prompt vs in code. Covers prompt structure (who/input/task/output/rules), prompt sizing & instruction-following limits, moving deterministic rules to code, few-shot examples, and when/how to fine-tune on real data. Kuki custom skill.
domain: ops
---

# n8n LLM Agent Design

The standard for **every** n8n flow that uses an LLM (AI Agent, Basic LLM Chain, chat model, or an HTTP node calling an LLM API). Goal: agents that reliably DO what we want — not bloated prompts that hallucinate and ignore the rules that matter.

> **Consult this skill whenever a flow includes an LLM, BEFORE writing or editing its prompt.** Evidence base: deep research 2026-06 (Anthropic & OpenAI prompting guides; ManyIFEval / IFEval / ScaledIF instruction-following studies).

---

## The 3 rules (in order of impact)

### 1. Deterministic-first — keep it OUT of the LLM
Anything a clear `if/then` can decide MUST be **code**, never the LLM. The LLM is probabilistic; code is reliable. This is the single biggest reliability win.

Move to a **Code pre-filter** (before the LLM) and a **Code post-validator** (after):
- **Language detection / locale routing** (e.g., what language to reply in) — NEVER let the LLM guess. (This is why agents reply in Russian.)
- **Hard skips by pattern**: links/promo/spam regex, tag-only comments, blocklists.
- **Anti-repetition / dedup**: pass "already used" as data; reject repeats in code.
- **Output validation**: enforce JSON shape, max length, allowed values, strip artifacts.

```
trigger → [Code pre-filter: locale, hard-skips, context] → [LLM: judgment only] → [Code post-validator: schema, length, dedup] → action
```

**When reviewing an existing flow:** every rule in the prompt that *could* be code is a finding → move it. (A prompt full of "detect language", "skip if @handle", "don't repeat" is doing code's job badly.)

### 2. Prompt structure & size — few, ordered, positive
Structure every system prompt in this order (validated by Anthropic & OpenAI):

1. **WHO** — role/identity (1-2 lines).
2. **INPUT** — exactly what variables the node receives.
3. **TASK** — what to do with the input (one paragraph).
4. **OUTPUT** — the exact format; prefer a JSON schema / structured output.
5. **RULES** — only the *judgment* rules the LLM truly needs.

**Sizing (evidence):** joint instruction-following collapses as rules pile up — GPT-4o falls from **0.94 (1 rule) → 0.21 (10 rules)**; small models (gpt-4o-mini class) far worse (≈0.80 → ≈0.00). So:
- Keep to **~5–8 principles**, not 15+ sections. More than that = you're putting deterministic rules in the prompt (see rule 1) → move them out.
- Prefer **positive** instructions ("react to what they actually say") over long "DON'T" lists.
- Put the few **critical** rules at the **start AND end** (models lose the middle — "lost in the middle").
- A short **decision procedure** with a **safe default** ("when in doubt → skip/abstain") beats more rules.
- **3–5 diverse few-shot examples** > long example lists. Curate them from REAL failures.
- One delimiter style (markdown headers OR XML), **consistent** end-to-end. Don't mix.

### 3. Fine-tune when you have real data — the model carries the voice, not the prompt
When a corpus of real `(input → ideal output)` examples exists, **fine-tune the base model** instead of cramming behavior into the prompt. A fine-tuned model bakes in voice/format/implicit rules → the prompt shrinks dramatically and consistency jumps.
- Use **real gold outputs** (e.g., the human's own past replies), filtered to the **current** desired style (data evolves → use a recent window).
- **Clean the targets** (strip artifacts that aren't intent, e.g. legacy `@mentions`).
- Format: **JSONL**, `{"messages":[{system},{user},{assistant}]}`, with the **same system prompt** you'll use at inference.
- Hundreds of examples suffice; thousands is plenty. Keep a held-out validation set.
- Fine-tuning does **not** replace the prompt or the code gates. **End state = fine-tuned model + thin prompt + deterministic gates.**
- Re-tune when the desired style changes.

**If self-serve fine-tuning is unavailable** (e.g. OpenAI disabled it for new orgs, 2026) → get the SAME benefit without training:
- **Dynamic few-shot / retrieval**: index the gold examples (embeddings or simple keyword match); per request, inject the 5–10 most similar `(input → ideal output)` pairs as examples. The model mimics the real voice on the fly, the pool updates instantly, no training cost.
- **Use a stronger base model**: the rule-overload collapse is mostly a *small-model* problem. A frontier model (gpt-5-mini class vs gpt-4o-mini) follows many rules reliably — often removing the need to fine-tune at all.
- Or fine-tune an **open model** on another platform (Together/Fireworks/Replicate) and call it via HTTP, only if a baked-in model is truly required.

---

## Checklist (building OR reviewing an LLM flow)
- [ ] Every deterministic rule is in **code**, not the prompt (locale, hard-skips, dedup, validation)
- [ ] Prompt follows **WHO / INPUT / TASK / OUTPUT / RULES**
- [ ] **≤ ~8 principles**; critical ones at start+end; positive framing
- [ ] Output is a **validated schema**; a post-validator enforces it
- [ ] A **safe default** is defined ("when in doubt → skip/abstain")
- [ ] **3–5 real-failure examples**, not long lists
- [ ] If real gold data exists → **fine-tune**; prompt stays thin
- [ ] Reviewed against the model's instruction-following limits (smaller model ⇒ fewer rules ⇒ fine-tune sooner)

---

## Why (evidence, 2026-06 deep research)
- Instruction-following degrades with rule count (ManyIFEval/IFEval/ScaledIF): joint satisfaction craters, worst on small/non-reasoning models. Individual rules stay fine — it's *simultaneous* rules that fail.
- "Lost in the middle": long context is processed non-uniformly; the start and end are privileged.
- Anthropic & OpenAI prompting guides both recommend the role → instructions → output → examples structure with consistent delimiters and task examples near the input.
- Caveat: strongest length/rule-count evidence is from synthetic atomic-constraint benchmarks; treat exact thresholds as directional, not laws.
