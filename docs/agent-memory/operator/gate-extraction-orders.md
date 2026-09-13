---
name: gate-extraction-orders
description: "an extraction/synthesis order over on-disk material (to Gemini or any lane) ships with a mechanical --verify gate, small chunks, a per-item coverage table and no crib - the ungated 2026-09-13 reasoning order came back skimmed with 13/14 invented paths"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 45114c3b-258a-4ca8-9aaf-b674a804cc7e
  modified: 2026-09-13T08:35:54.961Z
---

The P54 T11 reasoning order (1,446 exchanges, 3.6 MB, one order) came back from Gemini in 9 minutes: 13 of 14
"proposed home" / "searched" paths did not exist, its counts were copied from `TRIAGE.jsonl`, 14 of 32 items duplicated
the triage, one quote was misattributed, one item was invented. The operator: *"it's probably because we didn't force it
to gate and proof itself."* The Opus triage batches (<= 70 rows, an opened anchor per verdict, ids reconciled per batch)
held; the same model's gated web research holds too.

**Why:** a form-only reply check lets a plausible synthesis through; a corpus too big for one turn gets skimmed; a
triage file in reach becomes a crib; at scale a model fills gaps with names that fit the repo's conventions.

**How to apply:**
- Chunk: one date range / <= ~100 items per order.
- Require a coverage table: one row per input id (kept / nothing / recorded at `path:heading`).
- Pass `bridge_send.py --verify "<cmd>"`: a script that FAILs unless every cited path exists, every quote is a substring
  of its cited input, every "not found" term returns 0 `docs_find` hits, and the counts equal its own rows.
- Give ids to skip, never the prior verdicts.
- Still read the result as a draft ([research-gate-tiers](research-gate-tiers.md)): the verifier proves form and citation, not judgement.
- **Judgement goes to Opus, not Gemini (operator, 2026-09-13).** The gated Gemini retest passed the verifier but called
  10/11 recorded items "unrecorded". The operator: *"might as well have the opus agent do the reasoning/logic extract,
  gemini is failing"*. On-computer extraction that needs a recorded/unrecorded call runs as Opus `explorer` batches
  (~380 KB each) with docs_find + rg over code docstrings + memory bodies. Gemini stays on gated web research and librarian work.

Related: [three-lane-harness](three-lane-harness.md), [judging-is-codex-cli-batch](judging-is-codex-cli-batch.md)
