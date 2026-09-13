---
name: flow-driving-consent
description: "Google Flow MCP / Chrome driving is STANDING-APPROVED (2026-09-04): image generation is free, 10,000 credits/MONTH + 50 free/day, use it freely for assets and thumbnail tests; the old per-action consent rule is retired. Still no agent-owned lanes."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 45114c3b-258a-4ca8-9aaf-b674a804cc7e
  modified: 2026-09-04T23:35:58.372Z
---

**Standing authorization, operator 2026-09-04:** *"I get 10,000 flow credits per month, +50
free per day. Image generation is free, you are always free to use Google MCP for image generation
and to test thumbnails, etc. Cost is basically a non-issue, and the Google Flow Chrome was
set up specifically for this — you are always approved for MCP use."*

So: **drive Flow through the MCP / CDP driver without asking**, for stills, model sheets,
thumbnail tests, and video rolls within the budget (10,000/month + 50/day; video costs credits, images do not). The earlier rule ("never drive the
Flow session without an explicit go per action") is **retired** — it was written when
credits looked scarce and the Chrome was the operator's own working session; it is now a
dedicated automation Chrome (CDP port 9222).

What still holds:
- **Output stays in review quarantine** until the operator approves a contact sheet
  (`approved` is set by the operator, never by code). Free generation removes the ask, not
  the review.
- **Name a bound character, do not re-describe him** (`@Mike`); the recognised style phrase
  is the one directive that rides beside the binding — see [mp-host-identity](mp-host-identity.md).
- **No agent-owned lanes.** On 2026-09-04 I once extended a session-consent rule into
  "don't plan `parallax-runner.mjs`, it's the Flow lane" and a fully specified defect sat
  unowned for a day. Operator: *"There's no such thing as Gemini's territory."* Research
  agents explore; they don't hold ownership. Expect to verify and correct Gemini's code.
- Paid **audio** (ElevenLabs) is a different lane and still needs confirmation — see
  [local-whisper-no-paid-stt](local-whisper-no-paid-stt.md).

**How to apply:** when an asset, sheet, or thumbnail variant would help, generate it — then
put the contact sheet in front of the operator. Record each roll as a provider job with the
prompt hash so what was sent is auditable. See [codex-fulfillment-flow](codex-fulfillment-flow.md),
[ai-baselines-operator-corrects](ai-baselines-operator-corrects.md).
