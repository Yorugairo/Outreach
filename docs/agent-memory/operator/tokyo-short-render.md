---
name: tokyo-short-render
description: "Tokyo: v1 rendered 09-06; every cut since is the engine's TEST BED, not a release candidate - never ask for a render (no reproductions); portrait needs RENDER_ASPECT=9:16"
metadata: 
  node_type: memory
  type: project
  originSessionId: 45114c3b-258a-4ca8-9aaf-b674a804cc7e
  modified: 2026-09-10T21:02:45.870Z
---

The Tokyo short's final render exists: `content/video_engine/projects/systems-and-blowups/tokyo-tea-break/build-short/render/tokyo-short-full-1440p.mp4` in the MAIN checkout (1440x2560, 30 fps, 88.83 s, 2026-09-06 05:39), quarantined until the operator approves. The project lives only in the main checkout - not in the sweet-villani worktree.

**Why:** the first attempt captured landscape (2560x1440) because `render_episode.py` needs `RENDER_ASPECT=9:16` besides RENDER_BUILD / RENDER_URL / RENDER_NAME, with `serve_player.py 8731 build-short` up. The viewer re-read on the final take (six measured windows) still fails V01 on `[promise]`/`[rehook]` at 0:30-0:45 and `[ring]`; the operator ruled the 0:30-0:45 misses are not misses on a short (E43: the chart carries the number, conjoined beats are the doctrine). The viewer tools' stem bug (runner/scorer vs gate runner) is fixed at 7b54636.

**How to apply:** render a short with the full env line (recorded in BACKLOG "The day's read" row 3). Read V01 on a short beat by beat against the SCREENS file before it binds; the tool fix is backlog R26-0. Still open on Tokyo: the muted-caption judge (V-a) on the render, the operator's approval. See [gitignored-artifacts-live-in-worktree](gitignored-artifacts-live-in-worktree.md) (this one is the exception: main checkout) and [viewer-perception-test](viewer-perception-test.md).

**Render standard (operator, 2026-09-06):** shorts render ONCE at 1440x2560 (device scale 4/3) for every platform - YouTube gives 1440p+ uploads the better codec tier and the same file serves Facebook/Instagram; no 1080 variant, no RENDER_SCALE switch needed. The operator watches v2 in the PLAYER before any render (a render is only after the word).

**2026-09-09 - the remake on the 09-09 engine (983f5f5):** rebuilt on everything the tariff short taught; gates 0 FAIL / 2 WARN /
14 PASS (M16 1.7 s, M18 clean). Applied: the fab plate replaces the toll-gate clip in its measured place (leaves at the turn),
two lights (wafer, then a glide to the whole fab on "works"), the bed -20 breathing over both thrown cards. The take was already
tight (174 WPM, no gap over the caps). Watch on :8738 (`tokyo-short-player-b`; :8733 is another session's build-morph-demo
server). The 09-06 render is behind the build; a new render needs the word. Open on the watch: the Fed card's ~0.6 s overlap with
the caption strip before its snap; the empty plot held under the docks (37-39 s, 55-60 s). Notes: `REMAKE-2026-09-09.md`.

**2026-09-10 - the P48 cut BESIDE the remake (HG4):** `TOKYO_BUILD_DIR=build-short-p48 python build_short.py` builds into
`build-short-p48/` (the env var is how a cut under review never overwrites the watched build), served by `tokyo-short-player-p48`
on :8740 (main's AND the worktree's launch.json; the worktree entries need absolute paths). Row 2 rescales to the Feb-Jun
window on "The Treasury's table" (E58), the two treasury figures write on the windowed line (no month subs, June above its
point), the un-draw moved to "The opponent" (M21 read 14.1 s on "Two numbers"). Gate 0 FAIL / 2 WARN (M11 no sound cue, M21
s06 0.2 s short - both pre-existing on :8738), M23 PASS, no frozen run. Stills sent. Two builds await the operator: :8738 (the
09-09 remake) and :8740 (the P48 cut); a render only on the word, and only of the one they pick.

**Same day, round 2 (the operator's two cuts):** the chart PARKS up-left on "Two numbers" and the fingers land beside it (a
dock never covers a living chart - "space we could be using"); row 4 carries `;then=ev-japan-selling-v1:bars:3` (the tariff
short's month-by-month object, copied into Tokyo's objects with provenance) and RECASTS into the signed bars on "The
Treasury prints"; "your first number" is a NOTE (a figure at the June bar crossed the May bar - measured); the fab card lands
beside the PARKED bars on "pledged". Four transitions on :8740; M21 WARN s02 16.5 s (the chart lives beside the agenda by
the operator's ask - their call against E50). Bravos's camera MEASURED for P49 (`claude-watch/camera.json`): 37/45 held
compositions camera-still, every chart and diagram; the camera moves only on the map and one collage push - P49 amended:
LOCKED is the default.


**2026-09-10 evening - :8738 and :8740 CLOSED OUT (operator: "8740>8738, thats good work ... close out the 8738 and 8740"):**
the DEFAULT `build-short` (:8738) now carries the P48 cut; `build-short-p48/` (:8740) is redundant. Added the same evening:
the pledge's EVIDENCE - a RECORD dock (the Nikkei lede of 12 Nov 2024 typed on paper under the parked bars on "pledged",
the highlighter on "at least 10 trillion yen" as the narrator says it; source on disk `evidence/sources/nikkei-2024-11-12-...txt`)
handing the band to the fab card on "works"; and the CAMERA variant beside it: `TOKYO_CAMERA=1 TOKYO_BUILD_DIR=build-short-cam`
-> :8742 (`tokyo-short-player-cam`): the attention pull on the row-2 landings + the fab card, the ARRIVAL on the ring instead of
the snap. Both gate PASS. The breakthrough bars (bonds 1.52 % vs chips 36.59 % a year, scale stated to 8 %) exist as a proof
(:8739/breakthrough-proof.html), NOT in the cut - where it would go is "it beats our bonds", the fab card's beat today.
Traps: a record's META `record` is filled while the rows are built, so `evidence-dock.json` must be written AFTER the rows;
the record paper's height is its typed text (five lines grew into the caption strip - the excerpt ends at "semiconductor...").
Render only on the word; the operator picks :8738 (locked camera) or :8742 (the camera) first.

**Same evening, the breakthrough's second pass:** the zigzag cut was wrong (a broken-axis mark says "abbreviated"). Bravos
MEASURED at 8:01.8-8:03.2: a "?" track, the bar shoots to the frame's edge WHILE the axis rescales (0-450 -> 0-1500, the others
collapse to stubs), overshoots, settles, a value capsule counts up on the axis. Built two mechanics, both from the COMPARATOR's
level (the tallest honest bar): `overflow: "burst"` (Bravos: the shoot + the rescale, glow) and `overflow: "stack"` (the operator's
A: one comparator per 0.06 s step at the stated scale, off the page). Proofs :8739/breakthrough-proof.html + breakthrough-stack-
proof.html. The operator picks the mechanic and where it goes ("it beats our bonds"). :8742 is served by `tokyo-short-player-cam`
(http://127.0.0.1:8742/player.html).

**2026-09-10 night - the breakthrough IS in the cut (operator: "Yes, It should go into Tokyo 'Beat our bonds'"):** row 4's third
chart state; the parked monthly bars recast into the ten-year bars on "to chips," (56.85), the chips bar holds at the bonds'
level with the plant beneath, the BURST lands on "bonds." (59.05-59.65) in the parked slot (park 0.52, plant at 0.59, no light).
Rules that moved: a park stands until the next park (a recast no longer un-parks); the page's source line rides the park.
Traps: an object's `build_s` is a STRING after load_series (parse_float=str) - read it with to_number; a spotlight darkens the
whole page (never light a card while the page must be read); the run's hold starts at the END of the state's build_s, not at
the bars' landing. Both :8738 and :8742 carry it; render only on the word.

**Same night, the pledge beat re-staged (operator: "pop the card centered exactly as it is, and move it and resize it to that
slot on the right when we pop the next card"):** the record pops centred in the band on "pledged", holds 1.41 s, parks over 0.7 s
to the slot beside the parked chart on "to chips," as the plant lands beneath; both stand through the burst, leave on "And here's";
the read-out ends at "through fiscal 2030...". The mechanism is the DOCK READ->PARK: a centred dock may name `read` (the box it
pops at), `read_s`, `park_s`; a centred card sits on either slot (slot 1 never got a place before); the record's type is in cqw of
the dock's width so the park resizes without a rewrap. Trap: `place` is computed only for slot 0 unless the dock is centred.

**2026-09-10, the watch: "8742>8738".** The operator read the camera cut over the locked cut - P49's HG1 (the landing pull's
dials) and HG2 (the arrival replaces the snap on the ring) are CLOSED (E59 amended); `TOKYO_CAMERA` now defaults to 1, so
`build-short` (:8738) IS the camera cut and :8742 is the same build (`TOKYO_CAMERA=0` rebuilds the locked variant). The tariff
short's approved cut keeps its snap until re-cut. Render only on the word.

**Same night, the UN-PARK (operator: "if they're going to leave the chart should either re-take center stage, or they might as
well stay til the transition"):** a park now moves from where the chart stands, so `chart_to park scale 1.0` grows it back; row 4
un-parks 0.3 s after "And here's" (0.9 s) and the ten-year bars hold large under "nobody says" until the Meta page mounts. The
compiler admits exactly 1.0 (0.96-0.99 are still "not a park").

**2026-09-11 - DO NOT ASK FOR A RENDER.** The operator: "why do we want to render tokyo, when we're adding all of these
improvements??" - their rule (no reproductions; reach the new level, then produce NEW content) applies: v1 rendered 09-06 and
every cut since is a reproduction. Tokyo is the TEST BED (gates, goldens, every mechanism proven on it), not a release
candidate. The render word matters again only for a new short made at the new level on the one-shot bar. Stop listing
"the render word" under "still yours".
