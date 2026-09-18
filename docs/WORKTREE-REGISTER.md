# WORKTREE REGISTER - every checkout on this machine, who is writing what in it, right now

E99 s47 (2026-09-15): parallel work is the requirement, and the cost is paid with AWARENESS - every agent reads this
file at start and updates its row at every commit. The operator, 2026-09-16, closing P62's first draft: *"isn't a
better way to just check git before pushing to main and always preferring non-destructive methods?"* - so this page
is a hand table plus a checklist, and `git` carries every other fact. It exists because two lanes appended rulings
blind on 2026-09-16 and collided on E99 s49 (the audio lane renumbered to s54), and because worktrees existed that no
board named. `git worktree list` is the census; `content/video_engine/tests/test_worktree_register.py` fails when a
worktree has no row here or a ruling number appears twice - it runs in the checklist below, before main.

Rules while a lane is live:
- A shared file (`OPERATOR-RULINGS.md`, `CAPABILITIES.md`, `BACKLOG.md`, the queue) is committed by ONE lane at a
  time, and the commit message names any text another lane wrote that rides along.
- Ruling numbers: claim the NEXT free `E99 s<n>` here BEFORE writing it; a script that appends a ruling reads the
  last number on disk at run time, never from memory.
- The engine lock (`scene-evidence-engine.mjs`, `kinetics/**`, `species/**`, `build_scene_timeline_f.py`, the player
  template) has one holder PER WORKTREE; name the slice.
- A second agent works in its own worktree off main - `git worktree add <path> -b <lane>/<slug> main` - a worktree,
  never a clone: it shares the objects, the LFS store and the commit hooks (which resolve from the main checkout, so
  a hook change merges to main first). Its row lands here before its first commit; sprawl is accepted while the row
  names it (s47).
- The docs layers are BUILD OUTPUT (P63 / P64): gitignored, rebuilt by the write, never committed and never claimed;
  each worktree carries its own `docs/.layers/`.

## Before anything reaches main - the checklist (only git, nothing destructive)

1. In the lane's worktree: `git fetch`, then `git merge main` - a merge, never a rebase of a shared branch.
2. Run, unpiped, from that worktree: `python -m pytest content/video_engine/tests/test_worktree_register.py content/video_engine/tests/test_golden_frames.py -q` (a duplicate ruling number or an unregistered worktree fails here, before main).
3. A conflict on `OPERATOR-RULINGS.md` or `review-answers.jsonl`: keep both sides. A duplicate ruling number: the INCOMING lane takes the next free number and fixes its citations in the same commit (`rg "E99 s<n>"`).
4. If the engine moved on either side: the goldens re-pinned ONCE, in one commit, the sha table in the message.
5. From main: `git merge --ff-only <branch>`; then update the lane's row in `docs/WORKTREE-REGISTER.md` (last merge).
6. Never `--force`, never amend after a push, never delete a branch or a worktree without the operator's word, never `git add -A`; deletions in an index-only commit. Push only on the operator's fresh word in chat.

## The rows

| path | branch | lane / owner | purpose | live slice | write set (beyond the slice's own) | engine lock | rulings claimed | last merge to main |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `C:/Users/Snipe/Downloads/Outreach Program` | `main` | P62 parent (Claude/Fable) + its Opus lanes - this register's author | doctrine, gates, evidence, review; P61 / P63 / P64 complete | P65 THE RECIPE LAB + P66 THE SHAPE COMPILER + P67 THE VERIFIED RECEIPT AND THE CRITIC running IN PARALLEL as delegated slices on main (the operator, 2026-09-16: "yes, run them in parallel"); forty waves committed 2026-09-17 (9380ea7 .. c615ebd: the door plan, s73 + the survivorship audit, s74, the sixth pass with its review fixes, the change-report fix, the transform-first chooser with the calendar base, the ninth pass - an authored entry stands; the calendar base v7 carded then RULED by s77 - THE COMPILER IS STOPPED, P66 retired; s75/s76/s77 written; the figure regression of 09-14 restored and the bars-page label row thinned (R26-191); TOKYO TEA BREAK v2 built by hand on the approved cut's structure (`REBUILD-TREATMENT-V2.md`, `build_short_v2.py`), read on frames beside the approved cut, the voice through chain G, the operator: "tokyo tea looks good" / "render tokyo tea @ 1440p 24 fps" - RENDERED from `build-v2-frozen-c/` (1440x2560, 24 fps, 88.83 s, -15.1 LUFS; the card `tokyo-tea-break-v2-the-rebuild` on the queue); next: the operator's watch of the render and the history dial); E99 s69 / s70 / s71 written (the gates guide; recipes are timings that compose; the vocabulary is the record's; a light is never the move; the throw is signature); the parent read every rendition on its sheet beside the approved cut before the cards returned: on the queue - the re-proved set (six recipes carrying their mechanism; two named as not on this bed), the first real batch (twelve plate-carries-a-card candidates, all read), the generated base v7 with its critic (ten of eleven instants the same as the approved cut, the recast BUILDING after the engine's keyed-false line); one-shot #3's card still on the queue; next: the Opus one-shot on the compiler's base, then Astra's | the queue (`review-queue.v1.json` + `REVIEW-QUEUE.md`), the plans, `CAPABILITIES.md` / `BACKLOG.md` rows it owns | FREE - no holder since P61 T14 (2026-09-16) | E99 s49-s53, s55-s65 (committed); s66 (claimed 2026-09-16, written); s67 (claimed 2026-09-16, written); s68 (claimed 2026-09-16, written); s69 (claimed 2026-09-17, written); s70 (claimed 2026-09-17, written); s71 (claimed 2026-09-17, written); s72 (claimed 2026-09-17, written); s73 (claimed 2026-09-17, written); s74 (claimed 2026-09-17, written); s75 (claimed 2026-09-17, written); s76 (claimed 2026-09-17, written); s77 (claimed 2026-09-17, written); s78 (claimed 2026-09-17, written); s79 (claimed 2026-09-18, written); s80 (claimed 2026-09-18, written); next free: **s81** | is main |
| `C:/Users/Snipe/Downloads/Outreach Program` | `main` | audio / voice lane (Claude) | chain G tone chain, `tempo_edit`, the ten-test restoration of `test_authoring_kit.py` | its own | `authoring/audio.py`, `audio_synth.py`, `master_vo_tone.py`, `audio_spectrum.py`, `tempo_edit.py`, the audio tests, `scripts/hooks/test_deletions.py` + `.git/hooks/commit-msg`, doc 37, `.env.example`; **not `gate_opening_structure.py`** (its short-mode tag fix landed as cd53b6d on the operator's word). NOTE from the P62 parent: under a pathspec-limited commit `test_deletions.py` audits the STAGED diff, not the commit's - that fix is yours | none | E99 s48, s54 (committed) | is main |
| `C:/Users/Snipe/Downloads/Outreach Program` | `main` | package lane (Gemini / Flow, via the bridge) | scripts B / C, thumbnails, the outreach package (`ai-slower-useful-faster/`, `normal-for-which-bridge/package-2026-09-15/`, the `MP-NORMAL-OUTREACH` plan) | its own | its project folders only | none | none | is main |
| `C:/Users/Snipe/.codex/worktrees/f10b/Outreach Program` | `codex/stickly-woodblock-variant` | codex (Astra), August | DORMANT - unmerged: 1 commit (808eb14, 2026-08-23), 1169 behind main; 534 dirty files; 55 plate-library rows resolve into it (`build_plate_library.py:9`, B2) | none | none | none | none | never |
| `C:/Users/Snipe/.codex/worktrees/p29-remotion-console/Outreach Program` | `codex/p31-semantic-evidence-and-word-timed-captions` | codex (Astra), August | DORMANT - unmerged: 0, 1165 behind main | none | none | none | none | merged (0 ahead) |
| `C:/Users/Snipe/Downloads/Outreach Program/.claude/worktrees/content-generation-system-52f077` | `claude/spark-animations-marketing-cc6738` | Claude, August | DORMANT - unmerged: 0, 1173 behind main; 8,893 untracked / 20,620 ignored files never inventoried | none | none | none | none | merged (0 ahead) |
| `C:/Users/Snipe/Downloads/Outreach Program/.claude/worktrees/sweet-villani-1c3a16` | `claude/content-generation-system-52f077` | Claude - the P61 / P62 parent's session cwd | DORMANT as a checkout - every edit and commit of the parent lands in main; unmerged: 2 commits on the branch (the CLAUDE.md / AGENTS.md stabilisation, superseded on main), 703 behind; flattened into main 2026-09-08; removable only from a session not sitting in it, on the operator's word | none | none | none | none | 2026-09-08 (flattened) |
