# MP-FED-LIQUIDITY prerequisite baseline — 2026-09-18

Parent-verified baseline before engine edits. Branch `codex/Astra`, heavily dirty checkout preserved. No commits/pushes. Historical register row says engine FREE; parent now holds sequential T11–T15 episode prerequisite lease, starting T11 only. No other engine writer was dispatched in this task. The read-only T2 agent was interrupted by the parent after redundant parent verification, to keep four total active agents; no operator interruption is implied.

## Exact parent tests

- `python -m pytest content/video_engine/tests/test_worktree_register.py content/video_engine/tests/test_golden_frames.py -q`: **158 passed in 347.12s**, exit 0.
- `python -m pytest content/video_engine/tests/test_page_boxes.py content/video_engine/tests/test_chart_transitions.py -q`: **123 passed in 71.78s**, exit 0.

## Open prerequisite findings

| Row | Baseline | Action |
|---|---|---|
| R26-235 | `ledger_page.py:1547` returns None for full_stage; measurement script deduplicates only by ink and aspect. | T11 distinct measured variant; T12 serves it. Never re-key portrait ink. |
| R26-230 | `CAPTION_ANCHOR` exists at ledger_page.py:1159; full-stage geometry comments describe constraints but explicit top/bottom bands remain owed (BACKLOG:661). | T13 named bands and both-aspect proof; retain caption size. |
| R26-222 | BACKLOG:653 records same unchanged x ticks duplicated by y-only rescale handover. | T14 compiler correction with before/mid/after proof; do not relax M28. |
| R26-231 | page_build_spec validates per-series minimum, but row-span validation remains owed (BACKLOG:662). | T15 rejects oversized total build plus leave envelope by row. |
| R26-236 | H builder:715 still sets plate_idle_paints True; s84 requires long-form Ken Burns alone. | Episode builder sets false; do not modify H or short defaults. |

## Dirty baseline custody

The three production Python files had no Git diff. Pre-existing `page-boxes.v1.json` changes only player_sha256 from `43f21d504ae1e7e0587d43fb043991d9ac46f4bd9979bd68a3979d7dfc0cad00` to `3660f540df9f984ef614634fdccc46b3c726d767c7375b89b88aa45738b11cf8`. BACKLOG R26-241 documents a prior remeasurement with unchanged boxes. Preserve this change; do not call it our fix or broaden scope to staleness redesign.

| File | SHA-256 before patch |
|---|---|
| measure_page_boxes.py | 4cc4de66551eb255fc733f1c66d50377d2667e91a35104bcbe5ca46be1c595e8 |
| ledger_page.py | 96116bb02cdabc7f775c401d3ea8dbc74e8ed50a164fadf9f041237fab26fa5e |
| build_scene_timeline_f.py | 2dd4390986a9e5cf79256dd9d817c002ed395262165739628911f5a2262510ae |
| page-boxes.v1.json | d4ffdb590b78bc8d2cf57e7cae42b5cf51e5ced7a1ddbf5bb34ce68ca9a060e0 |

## Human decisions

HG1 approved in s85. Inherited caption size, end-tag form, final voice and plate balance remain unanswered in the reviewed handoff/s84 record; preserve current caption size and label Kokoro as scratch. No asset or media approval inferred. Next free ruling s86.

Recall: docs/WORKTREE-REGISTER.md, Hand-off 2026-09-18 — fixture, bands, two compiler rows, then body.
Recall: docs/portable/OPERATOR-RULINGS.md, E99 s82/s83/s84 — full-stage page, stationary interior type, one lead pointer, Ken Burns alone for long form.
Recall: docs/content-video-engine/BACKLOG.md:666 — full-stage measured fixture is missing, not an absent renderer.
