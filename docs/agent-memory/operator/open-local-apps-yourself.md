---
name: open-local-apps-yourself
description: "when a lane needs a local app running (Antigravity for the Gemini bridge, a dev server, a GUI tool), launch it yourself - the session has bypass permissions; never stop to ask the operator to open it (2026-09-13)"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 45114c3b-258a-4ca8-9aaf-b674a804cc7e
  modified: 2026-09-13T07:07:07.838Z
---

The Gemini bridge order sat queued after a reboot because Antigravity was not running, and I asked the operator to open
it. The operator: *"You should have just opened antigravity, you have bypass permissions. It's open now."*

**Why:** a stopped lane waiting on a click the agent could make itself costs the operator a round trip and the work an
hour; the permission to act was already there.

**How to apply:** when a send, build or check needs a local app or server up (Antigravity / its language server for
`bridge_send.py`, a preview server, ComfyUI, Suno/Flow sessions already logged in), start it (Start-Process, the app's
launcher, `preview_start`), wait for it to be ready, and continue. Still never print the language server's command line
or the CSRF token, and still ask before driving a logged-in web session where [flow-driving-consent](flow-driving-consent.md) applies.

Related: [p46-bridge-state](p46-bridge-state.md), [codex-fulfillment-flow](codex-fulfillment-flow.md)
