# LANE REGISTER - who is writing what, right now

E99 s47 (2026-09-15): parallel work is the requirement, and the cost is paid with AWARENESS - every agent reads this file at
start and updates its row at every commit. It exists because two lanes appended rulings to `OPERATOR-RULINGS.md` blind on
2026-09-16 and collided on E99 s49 (the audio lane renumbered to s54), and because a docs-layer build ran twice at once.
P62 makes this the worktree register; until then it is the lane register for one checkout.

Rules while a lane is live:
- A shared file (`OPERATOR-RULINGS.md`, `CAPABILITIES.md`, `BACKLOG.md`, the generated `docs/*` layers) is committed by ONE
  lane at a time, and the commit message names any text the other lane wrote that rides along.
- Ruling numbers: claim the NEXT free `E99 s<n>` here BEFORE writing it; a script that appends a ruling reads the last number
  on disk at run time, never from memory.
- The engine lock (`scene-evidence-engine.mjs`, `kinetics/**`, `species/**`, `build_scene_timeline_f.py`, the player template)
  has one holder; name the slice.
- `build_docs_layers.py --write` runs by one lane at a time; write "layers: <lane> <time>" here first, clear it after.

| lane | session / checkout | live slice | write set (beyond the slice's own) | engine lock | rulings claimed | layers build |
| --- | --- | --- | --- | --- | --- | --- |
| P61 parent (Claude/Fable) + its Opus lanes | main checkout, this register's author | P61 T7b (verdict rails) then T13, T3b, T3c, T6b, T11 | the queue (`review-queue.v1.json` + `REVIEW-QUEUE.md`), the P61 plan, `CAPABILITIES.md` rows 37 / 119 (written, uncommitted - ride with the audio lane's row), `BACKLOG.md` rows R26-137..151 | HELD by T7b | E99 s49-s53 (committed); next free after the audio lane's s54: **s55** | none in progress |
| audio / voice lane (Claude) | main checkout | chain G tone chain, `tempo_edit`, the ten-test restoration of `test_authoring_kit.py` | `authoring/audio.py`, `audio_synth.py`, `master_vo_tone.py`, `audio_spectrum.py`, `tempo_edit.py`, the audio tests, doc 37, `.env.example`, `OPERATOR-RULINGS.md` (s48, s54), `CAPABILITIES.md` (the VO tone row), `gate_opening_structure.py` | none | E99 s48, s54 | will rebuild after the restoration - say so here first |
| package lane (Gemini / Flow, via the bridge) | main checkout (`ai-slower-useful-faster/`, `normal-for-which-bridge/package-2026-09-15/`), the `MP-NORMAL-OUTREACH` plan | scripts B / C, thumbnails, the outreach package | its project folders only | none | none | none |
