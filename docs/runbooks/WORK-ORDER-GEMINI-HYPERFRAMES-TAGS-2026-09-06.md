# Work order — tag the HyperFrames report's figures and name our roots (2026-09-06)

**To:** the Gemini research lane (profile `video-researcher`). **From:** the Claude lane of `Outreach Program`, repo root
`C:/Users/Snipe/Downloads/Outreach Program`. Reply shape: `report-landed`. **Skills:** none needed (a text revision); use
`python content/video_engine/scripts/docs_find.py "<term>"` for every claim you check against our docs.

## Why

`docs/research/motion/HYPERFRAMES_MOTION_TRANSITIONS_RESEARCH_BLUEPRINT.md` passed the intake's form (16 proof lines, the
NOT FOUND block, the layers rebuilt) and was triaged (`docs/content-video-engine/HYPERFRAMES-INTAKE-2026-09-06.md`). Three
things fail the intake's proof discipline and need a revision pass, in place, same file:

1. **Twelve figures carry no source or tag.** Each must carry either a proof line (`[Metric | value | authority | URL | Verified
   2026-09-06]`) quoting the page it is on, or `[DERIVED: from <what>, <how>]` if you computed or compressed it, or
   `[UNVERIFIED]` if you cannot place it. The twelve, by report line: 18 (60-70 % CSS continuations), 44 (1-2 % breathing - it IS
   on `/prompting/motion`; add the proof line to the rule), 48 (4-8 % push-in - same), 66 (`back.out` range), 80 (1.1-4.0 s per
   idea - the page says "1.5-4 s per idea" and "1.1 s per beat"; say which and tag the compression), 110 and 172 (the "2-frame
   perceptual dip" / "black hole cut" - **not on `/prompting/capstone`**; either find the page that says it and cite it, or mark it
   `[DERIVED: inference]` in your own voice), 181 (the `t/0.0667` drift over 60 s - no measurement; mark `[UNVERIFIED]` or measure
   it), 226-228 (the ARAP invariants ΔC ≤ 0.06 W / Δθ ≤ 15° / area ≥ 0.60 - **these are this repo's own numbers**,
   `docs/content-video-engine/TRANSITIONS-REVIEW-2026-09-06.md` TR-7 and `briefs/ANSWERS-RESEARCH-BRIEF-animation-craft.md:390-396`;
   attribute them to our docs, not to HyperFrames), 274 (dissolve 0.35-0.45 s - tie it to the tier table's proof line or tag it),
   275 (the "0.50 s calm / 0.35 s fast WIPE benchmarks" - not in your own tier table and `WIPE_S` is not a symbol in our engine,
   the constant is `WIPE` at the player template; cite or remove), 278 (the transition "fits inside the gap"), 280 (the cream
   scales 1.02 → 1.00).
2. **§8 "settles" our open items with the vendor's defaults where this repo holds measurements.** Rewrite §8 as "what
   HyperFrames would say about each open item", one paragraph each, and beside each state what our measurement already says,
   citing it: TR-1 is closed by `docs/content-video-engine/46-REFERENCE-RHYTHM.md` §46.5 (36 hard cuts / 35 dips / 28 blur-zooms,
   `measure_cut_kinds.py`, 99 boundaries); the wipe is retired as the default by ruling E47 §3 (`docs/portable/OPERATOR-RULINGS.md`);
   M13's placement is doc 46 §46.6 (3 frames before the next word's onset, measured). Where the vendor and the measurement
   disagree, say so; do not resolve it - the parent does.
3. **The NOT FOUND block names only the vendor's roots.** Add what you searched on OUR side (the docs you opened by path, the
   `docs_find.py` queries you ran) so the report can say what is new to this repo.

Also: the report says both "every hold carries a 1-2 % breathing idle" (line 44, from `/prompting/motion`) and "holds must
stay still; slow drifting or artificial breathing reads as unfinished work" (line 301, from `/prompting/storyboards`). Keep
both, and add one line naming the contradiction and which page says which.

## Landing

Same file, revised in place; then `python content/video_engine/scripts/build_docs_layers.py --write` and `--check` green.
Working files under `docs/research/runs/hyperframes_motion/`.

## Reply

`POSITION`, `PATHS WRITTEN` (absolute, bare paths one per line), `DISAGREEMENTS` (if you think a figure IS sourced, say where),
`PREREQUISITES`, `NOT FOUND WHERE I LOOKED`; then the count: how many of the twelve got a proof line, a DERIVED tag, an
UNVERIFIED tag. Under 150 words after the grammar.
