# SCRIPT G — RECORD CHAIN (RUN 2026-08-30 — take recorded, chain complete)

**Outcome:** 12.90 min take (385.2s + 388.9s chained), whisper gate caught
a real vocalized tail tone (killed by the defended join; seam −91 dB),
15 edit pauses inserted (runtime 788.6s), 32 docks pinned in the retime,
close re-authored to G's beats, all 47 docks topic-exit audited, captions
regenerated. Choreography: all slots clean incl. clash gates.
Remaining: operator join listen · filmstrips · full playthrough.

Every stage, its tool, its verified status. Nothing here is remembered.

| # | Stage | Tool | Status |
|---|---|---|---|
| 1 | **Freeze** — final chart refetch; badges auto-sync; verify NARRATION figures vs frozen sidecars (613/105/21/21 · 28/23/65 · 17/14) | chart builders (divergence, capital_formation_share, krx, smh, tnx…) + badge-chart sync in the timeline builder | RUNNABLE — narration-figure check is a manual read of the VERBATIM lines against the sidecars, listed here so it cannot be skipped |
| 2 | **Record** — chained two-part master, `--go` (~13.2k credits, 1 attempt) | `record_chained_take.py` (wired to SCRIPT-G-VO, split at the pivot) | **PREFLIGHT CLEAN** — 17 paragraphs, 3+3 tags, no stacks, split on the X5 seam, edit-pause plan present |
| 2b | **Whisper gate** — transcribe what was ACTUALLY said (no script knowledge), diff against the VO text; FAIL on insertions/deletions or WER > 5%. Catches the class alignment cannot: vocalized tags (the 0:08 "thumb"), dropped lines | `verify_take_whisper.py` (**built this pass**, operator call 2026-08-30; faster-whisper base.en, reads the recorder's manifest) | RUNNABLE (take-dependent) |
| 3 | **Word timeline** — merge parts, trim provider tail to the 1.2s settle | `build_timeline_f.py` (reads `vo-f/audio` — same dir the recorder writes) | RUNNABLE (take-dependent) |
| 4 | **Edit pauses** — insert the 15 owed silences at anchor word boundaries; shift words/sentences; emit `episode-paused.mp3` | `insert_edit_pauses.py` (**built this pass** — the chain had no tool for its own plan) | RUNNABLE (take-dependent); idempotence-guarded |
| 5 | **Karp rebind** — the record payload's typed-word times are absolute against the OLD take; recompute from the new timeline (type-on over the intro, stroke on the narrator's "paying for tokens…" words) | retime substep — small, deterministic from words + anchors | PLANNED (blocked on take) |
| 6 | **Dock retime** — shift all 75 windows + 41 docks onto the new clock. NOW DETERMINISTIC: every dock carries a VERBATIM anchor in Script G (41/41 verified), so each maps to its anchor's new word time; plate windows shift with their docks/beats | retime pass (anchors → word times → deltas) | PLANNED (blocked on take) — the alignment work this pass did is what makes it mechanical |
| 7 | **Choreography gates** | `emit_choreography.py` | RUNNABLE — currently ALL SLOTS CLEAN on the pre-retime table |
| 8 | **Filmstrips** — three boundary classes, played frames, vs the locked reference | doc 29 §9.16 procedure (browser) | PROCEDURE DOCUMENTED |

## Evidence alignment (this pass)

- **41/41 docked assets anchor VERBATIM in Script G** (enumerated; zero
  failures). Two orphans found and fixed: ev-divergence re-anchored to the
  new chart beat; **ev-equip-ipp-gdp RETIRED from the cut** (its beat no
  longer exists) with **ev-capital-formation-v1 taking its windows** —
  the yardstick now docks at its own beat, badges 28%/23% verbatim.
- The 12 deck slides that never had anchors recorded now carry them, each
  tagged `claim` or `contextual` — the next rewrite's alignment check
  starts from zero blind spots.
