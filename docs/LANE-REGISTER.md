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
| P61 parent (Claude/Fable) + its Opus lanes | main checkout, this register's author | P61 T11 (the record) - every build slice landed 2026-09-16; four cards on the queue (HG7b, HG2b-2, HG2-2, HG6-2) | the queue (`review-queue.v1.json` + `REVIEW-QUEUE.md`), the P61 plan, `CAPABILITIES.md` rows 37 / 119 (written, uncommitted - ride with the audio lane's row), `BACKLOG.md` rows R26-137..151 | FREE - T7c landed 2026-09-16; next holder P61 T14 (after P63 lands) | E99 s49-s53 (committed); next free after the audio lane's s54: **s55** | layers: P61 parent, the T7c commit pass (2026-09-16 ~13:30) - clears after the commit |
| audio / voice lane (Claude) | main checkout | chain G tone chain, `tempo_edit`, the ten-test restoration of `test_authoring_kit.py` | `authoring/audio.py`, `audio_synth.py`, `master_vo_tone.py`, `audio_spectrum.py`, `tempo_edit.py`, the audio tests, `scripts/hooks/test_deletions.py` + `.git/hooks/commit-msg`, doc 37, `.env.example`, `RECALL-RECEIPT.md`, `OPERATOR-RULINGS.md` (s48, s54), `CAPABILITIES.md` (the VO tone row + the test-deletion row; **carries the P61 lane's rows 37 / 119 riding along, as this register asked**). **NOT `gate_opening_structure.py`** - that beat-tag/delivery-mark change is not the audio lane's, was not in the tree at this session's start and neither audio agent wrote it; owner unknown, left unstaged | none | E99 s48, s54 (committed) | layers: audio lane, after its commits - the restoration is done and the effects-catalog DRIFT cleared; the rebuild folds in the P61 lane's verdict-stack catalogue change | NOTE from the P61 parent 2026-09-16: the staged `scripts/hooks/test_deletions.py` crashed on Windows (cp1252 decode of a UTF-8 diff -> `.stdout` None) and blocked every commit; the WORKTREE copy is patched (`encoding="utf-8", errors="replace"` in `_git`) - re-stage it before committing; and under a pathspec-limited commit the hook audits the STAGED diff, not the commit's - that fix is yours |
| package lane (Gemini / Flow, via the bridge) | main checkout (`ai-slower-useful-faster/`, `normal-for-which-bridge/package-2026-09-15/`), the `MP-NORMAL-OUTREACH` plan | scripts B / C, thumbnails, the outreach package | its project folders only | none | none | none |
