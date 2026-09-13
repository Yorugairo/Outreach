---
name: gitignored-artifacts-live-in-worktree
description: "ep1's audio master, evidence card PNGs, sound cues and prior renders are gitignored and live in the sweet-villani worktree checkout, not main; sync with cp -n before a build or render"
metadata: 
  node_type: memory
  type: project
  originSessionId: 45114c3b-258a-4ca8-9aaf-b674a804cc7e
  modified: 2026-09-05T01:48:38.547Z
---

**The build inputs git does not carry** (2026-09-04): `build-f/audio/episode*.mp3` (the
ElevenLabs master), `steel-and-paper/evidence/objects/*.png` (the evidence cards - only the
`.series.json` sidecars are committed), `steel-and-paper/sound/*.mp3` (Suno + freesound cues),
`build-f/player.html` (81 MB build output) and `build-f/render/*.mp4`.

They were all present in
`C:/Users/Snipe/Downloads/Outreach Program/.claude/worktrees/sweet-villani-1c3a16/...` (the
worktree checkout from the Sep 3 render session) and absent in the main checkout, where all
of 2026-09-04's commits landed. `build_scene_timeline_f.py` failed with
`UnidentifiedImageError ... ev-bravos-original-v1.series.json` because `find_asset` fell
through to the sidecar when the PNG was missing.

**How to apply:** before building or rendering an episode in main, `cp -n` those directories
from the worktree (already done for ep1 on 2026-09-04; Tokyo's `plates/`, `omni-video/`,
`comfy-video/` may need the same). The `:8731` episode-player server must be started via the
`episode-player` launch config (preview_start) - a backgrounded `python -m http.server` dies
with its bash task. See [worktree-read-scope](worktree-read-scope.md), [worktree-sprawl](worktree-sprawl.md).

**Update 2026-09-08 (flattening the worktrees):** every gitignored artifact in the sweet-villani worktree's
`steel-and-paper/build-f` (133 files, 1.33 GB: the 1440p master render, the world PNGs, the proofs) and the two
`runtime/claim-packs` summaries were copied into the MAIN checkout, new files only - main lacks nothing from that
worktree now, and every commit on its branch is on main. The worktree can be removed from a session that is NOT
sitting in it. The OTHER Claude worktree (`content-generation-system-52f077`, branch spark-animations, 902 behind,
14 GB untracked: animatic/, media/, content/video_engine/) has NOT been preserved yet - inventory before removal.
