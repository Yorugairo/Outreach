# Slide Semantic Registration — systems-and-blowups

Returned 2026-08-24, validated **PASS**: 86/86 slides, 340 verbatim figures,
0 errors, 0 low-confidence, 4 honest unmatched (narrative/background slides
with stated reasons).

## What this is

The missing half of a one-sided join. Narration cues already carried
`claim_refs` from a closed vocabulary; the slides carried none, so slide
selection was comparing prose to prose instead of looking up a shared key.
These documents give every approved slide a `claim_refs` list, a
`semantic_id` alias, a plain-language `headline`, taxonomy terms, and every
factual numeral printed on it, transcribed verbatim.

## Files

| File | Role |
| --- | --- |
| `registration.<deck>.json` × 6 | the registration documents — the deliverable |
| `claim-vocabulary.json` | the 21-claim closed set the refs point into |
| `taxonomy.json` | controlled terms for actors / objects / mechanisms / worlds |
| `slide-index.json` | frozen join keys: `slide_id`, `deck_id`, `sha256` |
| `approvals.json` | the returning model's own completion report |
| `WORK-ORDER.md` | the instructions it worked from |

Slide images themselves live in the **p29-remotion-console** worktree at
`content/video_engine/projects/systems-and-blowups/sources/decks/teacher-stamped-production-visuals/`.
`sha256` in `slide-index.json` binds each registration row to a specific
image file — the validator rejects any row whose hash was altered.

## Revalidate

```bash
python content/video_engine/scripts/validate_slide_registration.py content/video_engine/projects/systems-and-blowups/registration
```

Structural checks only. It cannot confirm that a transcribed numeral really
appears in an image, but it rejects invented claim ids, altered join keys,
semantic ids that do not encode their own claim, duplicate aliases, and
missing slides.

## Figures are on-screen assertions

Each `figures[].value` is transcribed exactly as typeset — symbols,
separators, ranges and qualifiers intact, never normalised. A stat badge
built from one asserts that the number appears **verbatim** in the slide
behind it, so any transformation of these strings breaks that guarantee.

## Open follow-ups

1. Merge into the deck manifest in the p29 worktree (cross-branch — deliberate
   decision, not automatic).
2. Switch the scene-evidence generator from lexical matching to registered
   lookup. The lexical path was a stopgap for exactly this absence; with
   `claim_refs` on both sides the join becomes a key lookup.
3. Re-plan evidence distribution. The 33/12/15 front-loading in the v4 cut was
   an asset-availability artefact, not an editorial choice — the full
   86-slide catalogue is now selectable.
