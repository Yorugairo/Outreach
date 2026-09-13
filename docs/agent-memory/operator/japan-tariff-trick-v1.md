---
name: japan-tariff-trick-v1
description: The Japan tariff short - second cut APPROVED 2026-09-09 ('tight sounds right, approved, render it'): the dead-space-killed Chirp take (scene_1-tight, the build default), no reference line, the fab pledge dock with the light on the wafer; rendered at 1440x2560 in MAIN's build-short/render/
metadata:
  type: project
  originSessionId: 45114c3b-258a-4ca8-9aaf-b674a804cc7e
  modified: 2026-09-09T04:46:40.255Z
---

**Status 2026-09-08 (the second day):** the operator approved the short in the player - the plates (map v9, their own
Flow edit; the two chart cards), the card-then-snap arrival, the Chirp voice (E54: no ElevenLabs body; real people judge
the cuts side-by-side), the bed at -20 LU breathing +4 dB over both landings. Rendered once at 1440x2560, 89.37 s,
2681 frames, -15.9 LUFS integrated: `content/video_engine/projects/systems-and-blowups/japan-tariff-trick/build-short/render/japan-short-full-1440p.mp4`
in the MAIN checkout (gitignored - it exists only on this machine; 47.5 MiB, over the app's 30 MiB upload limit).
Player on :8734 (`preview_start japan-short-player`). The render's shard 0 died once ("encoder pipe closed", Errno 22 at
t=10.5 with four workers); re-running the one shard (`--frames 0 671 --part .../part-00.mp4`) and concatenating by hand
worked - the concat list needs an ABSOLUTE `RENDER_BUILD` (ffmpeg resolves entries against the list file's directory).

**Why:** the retention read on this short is the engine's work on a voice real people already answered for - not a voice test.

**How to apply:** the next short starts from this build (`build_short.py` is the shot table of record: throw+snap rows,
`dur:"hold"` lights with `until`, `;idle=live`, `BED_LU -20`, `BED_SWELL_DB 4`). Open on this project: TR-14 ink bloom
(the second-lever seam), the $6,240 DERIVED line (REVIEW-CLAUDE decision 1), the story-bar colour token (backlog).
History: v1 built 2026-09-07 from Gemini's hand-off on the Chirp take; $122.6B verified live; decisions in REVIEW-CLAUDE.md.
See [voice-lane-split](voice-lane-split.md), [recall-before-propose](recall-before-propose.md), [chart-form-rulings-e50-e53](chart-form-rulings-e50-e53.md).

**2026-09-09 (the watch of the render):** three defects + a pace question. (1) The receipt page's dashed "Toyota's bill"
line read as a mis-label of Detroit - a bar is never a reference line (E53 addendum); gone. (2) The pledge dock (Tokyo's
toll-gate clip) was useless without the plant (E55); the operator generated the fab plate by hand in Flow (Downloads ->
`omni-video/stills/sig-i-fab-wafer.png`, with the two package thumbnails as alternates) - it ships CENTRED in an authored
box measured from the page's ink, the ring on the wafer at "semiconductors". (3) The take had never had doc 37 s14's
dead-space kill: `retime_take.py --gaps --tempo 1.06` -> three candidate clocks (`scene_1-tight/-x106/-fast.words.json`,
the mp3s gitignored, re-creatable in seconds); `build_short.py --take scene_1-fast` is what the player on :8734 shows
(80.8 s runtime, 199.5 WPM, 0 FAIL / 0 WARN). The operator picks BY EAR; the 09-08 render is now behind the source - a
new render after the word. Known and accepted: the thrown holdings card overlaps the caption strip for ~1 s before the
snap (the approved cut had it). The Whisper gate's numeral normalization fails every take (TR-15).

**2026-09-09, later:** the operator heard tight (:8734) against fast (:8735) and chose TIGHT - "tight sounds right, approved,
render it". `build_short.py`'s default clock is now `scene_1-tight` (the mp3 is gitignored; recreate with
`retime_take.py scene_1.mp3 --gaps --out scene_1-tight`, deterministic). The ring on the wafer became the LIGHT (E56: a ring
circles a number or a point on a chart only; compiler-gated). Rendered once at 1440x2560 (85.28 s) - the file of record is
`build-short/render/japan-short-full-1440p.mp4`; the 09-08 render sits beside it as `-superseded`. `render_episode.py` now
re-runs a failed shard once.
**Rendered 2026-09-09 07:44** - `build-short/render/japan-short-full-1440p.mp4`: 1440x2560, 85.27 s, 2558 frames, 52.5 MB,
-15.8 LUFS integrated (main checkout, gitignored, over the app's 30 MiB upload limit - desktop only). The render needed the
player server THREADED (`serve_player.py`, e038c4a): one held connection wedged every other client and all four shards
timed out on Page.goto; render against `japan-short-player-render` (:8736), never the watched player's port. Known,
accepted: a thrown card overlaps the caption strip ~1 s before its snap (both cards; the approved cut had it).

