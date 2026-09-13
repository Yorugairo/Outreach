---
name: flow-driver-traps
description: Google Flow plate dispatch - the live lane is create_flow_image over CDP via stdio (bridge lane retired); Agent mode hides the settings pill; character listing must read the Characters view; grid baseline must refill before the observer
metadata: 
  node_type: memory
  type: project
  originSessionId: 45114c3b-258a-4ca8-9aaf-b674a804cc7e
  modified: 2026-09-08T19:43:33.641Z
---

Plates roll through `tools/google-flow-driver/mcp/server.mjs` (`create_flow_image`, Nano Banana Pro, zero credit) over
CDP to the OPERATOR's automation Chrome (`--user-data-dir=C:\Users\Snipe\.flow-chrome-profile --remote-debugging-port=9223`,
signed in; a script never enters credentials). The MCP need not be attached to the session: speak JSON-RPC over stdio
(precedent `review/claims/mp-host-transitions-v1/dispatch_batch.py`; the tariff one is
`japan-tariff-trick/omni-video/dispatch_crossings_map.py <order.json>`). `flow_enqueue_batch` / `capability_snapshot`
is the RETIRED extension bridge (2026-09-03) - never cite it as a blocker.

**Why:** three defects cost a morning on 2026-09-08. (1) Flow's composer gained an **Agent mode** that replaces the
settings pill (`🍌 Nano Banana Pro crop_9_16 x1`) with a chat bar; the chip sticks per project, so `configureSettings`
toggles it off. (2) `listProjectCharacters` scanned the All-media grid and returned on the first hit - the three visible
strip tiles - so live characters (`Mike2`, `Mike`, `StickMike`) were reported missing; it now reads the library's
**Characters view** (`flow-character-tile .character-tile-name`). (3) Leaving that view empties the media grid; a
generation-observer baseline taken before it refills claims the PREVIOUS roll's output as new and downloads it again
(byte-identical sha across two orders). The driver now waits for the grid to refill to its pre-navigation count.

**How to apply:** after any Flow UI drift, probe from inside the driver package (`runtime/*.mjs`, gitignored - playwright-core
resolves only there) before touching the driver. Check every landed sha against the previous roll's. A re-roll is a NEW
order file, never an overwrite. The character reference drags in a whole WORLD, not just the figure: operator, 2026-09-08,
"HollowStickMike is the truest" - it stays the reference on the tariff short; geography defects are prompt defects.
Related: [mp-host-identity](mp-host-identity.md), [flow-driving-consent](flow-driving-consent.md), [judge-the-frame-not-the-diff](judge-the-frame-not-the-diff.md).

**E57 (2026-09-10) routing by size:** an entire episode's plates -> a bridge WORK-ORDER to Gemini (cheaper than generating here); one to a few plates -> drive the MCP ourselves (`create_flow_image` over CDP, ask first).

