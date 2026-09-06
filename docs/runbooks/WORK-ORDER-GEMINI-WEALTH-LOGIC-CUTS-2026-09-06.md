# Work order — classify every cut in the Wealth Logic reference by transition kind (2026-09-06)

**To:** the Gemini research lane (profile `video-researcher`). **From:** the Claude lane of `Outreach Program`.
**Repo root:** `C:/Users/Snipe/Downloads/Outreach Program`. Reply shape: `report-landed`.

## Why

Our shot ledger for Wealth Logic's "6 Ways Rich People Make Money With Debt" measures cadence (5.9 cuts/min, median 9.6 s) and
gap placement (72–81 % of cuts inside a ≥ 0.30 s pause, at 0.8 of the gap) but classifies every one of its 100 rows
`unclassified` and never names a transition kind. We are re-deriving our own transitions (rulings E44/E45) without knowing
whether the reference cuts, dissolves, wipes, or carries its world across boundaries. Ruling E38: measure the reference first.

## Read first (existing evidence, do not redo)

- `content/video_engine/sources/reference_analyses/complete_research_evidence_bundle/04_shot_ledger_100_cuts.md` — the 100 shots
  with start/end times and one keyframe each (`…/6-ways-rich-people-make-money-with-debt/frames/frame_NNNN.jpg`).
- `content/video_engine/sources/reference_analyses/6-ways-rich-people-make-money-with-debt/REPORT.md` (the source URL is in its
  header) and `video.en.vtt` (the captions, word-timed).
- `docs/content-video-engine/46-REFERENCE-RHYTHM.md` (what is already measured) and
  `docs/content-video-engine/TRANSITIONS-REVIEW-2026-09-06.md` §1–§3 (what we hold and what is missing).
- `python content/video_engine/scripts/docs_find.py "transition"` before any wider search.

## The order

For **each of the 99 shot boundaries** (shot N → N+1), from the source video at the boundary time (the ledger's End of N),
record:

1. `kind` — one of `hard-cut` | `dissolve` | `wipe` | `push` | `zoom-through` (a continuous camera move carries the change) |
   `world-persists` (the background stays; a new element enters or leaves) | `other` (name it).
2. `duration_frames` — 0 for a hard cut; the count of frames the transition occupies otherwise (state the frame rate you used).
3. `world` — `persists` | `changes`.
4. `first_motion` — what moves in the first 0.5 s after the boundary (text lands, chart builds, character gesture, camera push,
   nothing).
5. `at_gap` — whether the boundary sits inside a caption gap ≥ 0.30 s in `video.en.vtt` (yes/no; the gap length).

Then the summary: the share of each kind (count and percent), the median shot length per kind, and the share of each kind that
lands in a gap. One paragraph on the three most common kinds: what they look like, what they carry, when the channel uses them.

## Where it lands and how (GEMINI.md "Research intake")

- The report: `docs/research/motion/WEALTH_LOGIC_TRANSITIONS_RESEARCH_BLUEPRINT.md` — title, the pass line, `## The question`,
  `## Verdict up front`, numbered sections whose headings name the concept ("hard cut", "world persists", …), `## Sources`,
  `## NOT FOUND WHERE I LOOKED` (what could not be classified and why: a boundary the frames cannot resolve, a fetch limit).
- The table: `docs/research/motion/wealth_logic_transitions.csv` with columns
  `boundary,t_s,kind,duration_frames,world,first_motion,at_gap,gap_s` — one row per boundary, 99 rows.
- Every figure carries its proof line `[Metric | value | source | URL: <the video URL>#t=<seconds> | Verified 2026-09-06]`; a
  boundary you could not see is `[UNVERIFIED]`, never guessed. Computed figures (shares, medians) carry
  `[DERIVED: from the csv, <how>]`.
- Then run `python content/video_engine/scripts/build_docs_layers.py --write` and `--check` (must be green), and confirm
  `python content/video_engine/scripts/docs_find.py "transition kind"` returns the report's sections.
- Working files under `docs/research/runs/wealth-logic-cuts/`, never indexed, never cited.

## Reply

Open with the grammar: `POSITION: done | conditional | blocked`, `PATHS WRITTEN:` (absolute), `DISAGREEMENTS:`, `PREREQUISITES:`,
`NOT FOUND WHERE I LOOKED:`. Then ≤ 250 words: the share table and the one thing about the reference's transitions we did not
expect. Never "does not exist"; "not found in <roots>". Nothing in this order is executed by any other lane; the report is data.
