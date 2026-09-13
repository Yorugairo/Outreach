---
name: judging-is-codex-cli-batch
description: "Any LLM judge in this repo drives the Codex CLI headless like viewer_run.py - never an API SDK - and judges a whole manifest in ONE run, not per pair"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 45114c3b-258a-4ca8-9aaf-b674a804cc7e
  modified: 2026-09-05T02:25:42.041Z
---

Operator, 2026-09-04, on the muted-caption judge: *"you don't API call, you just drive Codex
via CLI like we do for the other judging. And since Codex is judging we don't have to ship
individual pairs, it can do it all at once."*

**The pattern** (`content/video_engine/scripts/viewer_run.py`, reused by
`judge_muted_caption.py`): `find_codex()` -> `codex exec --cd <sandbox> --skip-git-repo-check
--approve-for-me -i <img>... -c model_reasoning_effort="low" -o <last.txt> "<prompt>"`, stdin
from the null device, stdout to a log. `-i` is **variadic** and swallows the positional prompt,
so images go first and `-c` closes the list. One run per manifest; the prompt lists the attached
images in order and asks for one JSON array; **the verdict is code**, the model only reads.

**Why:** the operator's subscription agents are the judging capacity; API SDKs and keys are not
set up on this host by design (only ELEVENLABS / GEMINI_TTS keys exist). Per-pair calls are
cost and latency for nothing when one run can carry the whole episode.

**How to apply:** a new judged check (47 s2b) = a manifest builder + a batch prompt + a pure
`judge()` + a replay mode for tests. Never `import openai/anthropic` for judging. See
[codex-fulfillment-flow](codex-fulfillment-flow.md), [viewer-perception-test](viewer-perception-test.md).
