---
name: review-server-no-store
description: "The operator judges in the review player (localhost:8733); a browser-cached player.html made a fixed callout look broken and a Flow clip look frozen - serve builds with Cache-Control no-store (serve_player.py) and prove live playback, not just seeked frames"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 45114c3b-258a-4ca8-9aaf-b674a804cc7e
  modified: 2026-09-05T11:17:57.892Z
---

**What happened (2026-09-05).** Two operator complaints were not what they looked like: a callout ring "on the wrong month" was a cached `player.html` from before the datum fix, and "every Flow clip holds after ~2 s" was per-frame seeking on clips with one keyframe in 240 (the frame renderer, which awaits each seek, never showed it). The operator concluded the Flow lane was broken and that the character stopped moving; both readings were the editor's, not the video's.

**Why:** the review server was `python -m http.server`, which lets Chrome cache; and I verified frames by seeking, which is not what the operator does - he presses play.

**How to apply:** the `tokyo-short-player` launch config now runs `serve_player.py 8733 build-short` with `Cache-Control: no-store`; keep every review server on that script. Clip worlds PLAY during live playback and are re-encoded with a keyframe every 12 frames (`build_short.seekable_clip`). Before telling the operator to look, prove the thing in LIVE play (playwright: press play, sample the clip's `currentTime` / a strip's darkness across the boundary), not only with `render_baseline.frame_png`. And when a complaint contradicts a fix already committed, check what build the browser is holding before touching code. See [file-links-never-open](file-links-never-open.md), [our-artifacts-beat-outside-advice](our-artifacts-beat-outside-advice.md).
