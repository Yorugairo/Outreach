# Work Order — Slide Semantic Registration + Figure Extraction

Register 86 approved source slides against a closed claim vocabulary and
extract every factual numeral printed on them. Output is one JSON document
per deck, conforming to `slide_semantic_registration.schema.json`.

## Why this exists

Our narration is already semantically registered: every narration cue carries
`claim_refs` from a controlled vocabulary. The slides carry none. So when the
system picks which slide to show under a given line, it is comparing prose to
prose instead of looking up a shared key. Your output supplies the missing
half of that join.

A second use: figures you extract become on-screen stat badges. A badge
asserts that its number appears **verbatim** in the slide behind it. If your
`value` string does not match what is printed, the badge is a false claim on
a finance channel. Precision here matters more than coverage.

## Inputs in this directory

| File | What it is |
| --- | --- |
| `slides/<slide_id>.png` | The 86 slides, full resolution, 1376x768 |
| `slide-index.json` | Per slide: `slide_id`, `deck_id`, `sha256`, `image_file`, and the existing label/summary |
| `claim-vocabulary.json` | **21 claims — a CLOSED set.** id, text, classification, publisher |
| `taxonomy.json` | Controlled terms for actors / objects / mechanisms / worlds |
| `slide_semantic_registration.schema.json` | The output contract. Read it; field descriptions carry rules not repeated here |

## Output

One file per deck, in this directory:

```
registration.memory-supercycle.json
registration.silicon-antidote.json
registration.silicon-reality-gap.json
registration.silicon-silent-triopoly.json
registration.silicon-value-software-bubble.json
registration.sovereign-memory-infrastructure.json
```

Work deck by deck. Finish and write one file before starting the next.

## Per slide, produce

### 1. Frozen keys — copy, never alter

`slide_id` and `sha256` are copied verbatim from `slide-index.json`. They bind
the registration to a specific image file. **Do not rename anything.** If you
believe a slide is mislabelled, say so in `notes`; do not act on it.

### 2. `claim_refs` — from the closed set only

Read `claim-vocabulary.json`. Match on the claim **text**, not the id slug.
Order by centrality: `claim_refs[0]` is what the slide principally evidences.

- A slide may support several claims. List them.
- If no claim fits, use `"claim_refs": []` **and** give `unmatched_reason`.
  An honest empty is correct and useful. A guessed claim is a silent error we
  cannot detect later — it corrupts the join it is meant to fix.
- Never write a claim id that is not in the vocabulary. The validator rejects
  the whole file on one invented id.

### 3. `semantic_id` — the alias

```
<claim_refs[0]>.<role>.<form>-v1
sp500-top-ten-concentration.evidence.chart-v1
hbm-capacity-trade-ratio.evidence.diagram-v1
```

- The claim segment **must equal `claim_refs[0]`**. That is what makes this a
  lookup key rather than a decorative name.
- `role`: `evidence` (supports the claim) · `context` (frames it without
  proving it) · `countercase` (argues against it).
- `form`: `chart` · `table` · `diagram` · `timeline` · `quote` · `photo` ·
  `composite`.
- If two slides in a deck would collide, increment: `-v2`, `-v3`.
- When `claim_refs` is empty, use `unregistered` as the claim segment.

### 4. `headline`

One sentence, max 90 characters, stating what this slide asserts — in plain
declarative language. Not the printed title unless the title is itself the
assertion. "HBM production ejects two to three standard DRAM wafers" is a
headline. "The Root of the Shortage" is a title.

### 5. `figures[]` — verbatim numerals

Extract every printed number that states a fact. Exclude page numbers, axis
tick marks and footnote markers.

**The `value` rule.** Transcribe the numeral **exactly as typeset**, including
symbols, separators, ranges and qualifiers:

| On the slide | Correct `value` | Wrong |
| --- | --- | --- |
| 18% | `18%` | `0.18`, `18 percent` |
| $140B+ | `$140B+` | `$140B`, `140000000000` |
| 2 to 3 | `2 to 3` | `2-3`, `2.5` |
| ~5 years | `~5 years` | `5 years`, `5` |
| 3.0 : 1 | `3.0 : 1` | `3:1`, `3.0` |
| 11 Trillion won | `11 Trillion won` | `11T won`, `11000000000000` |
| 18% (2025) to 23% (2026) | two figures, `18%` and `23%`, each with its own `period` | `18-23%` |

Never normalise, convert, round, or expand. If a value is genuinely
unreadable, omit the figure rather than guessing at it.

Each figure also needs `label` (what it measures, in the slide's own wording),
`context_sentence` (the sentence or caption carrying it, transcribed),
`location` (which region — see the schema enum), and `is_headline` (true for
the one or two numbers a viewer should take away; these become badges).

Add `unit` and `period` where the slide states them separately.

A slide with no factual numerals gets `"figures": []`. That is a normal result
for a conceptual diagram.

### 6. `taxonomy` and `confidence`

Taxonomy terms come from `taxonomy.json` only; omit an axis rather than invent
a term. Set `confidence` honestly — `low` on dense, ambiguous, or
stretched-match slides. Low-confidence rows get human review; over-claiming
`high` is what turns a review queue into an undetected error.

## Self-check before writing each deck file

1. Every `slide_id` and `sha256` matches `slide-index.json` exactly.
2. Every claim id appears in `claim-vocabulary.json`.
3. Every `semantic_id` starts with its own `claim_refs[0]` and is unique.
4. Every `figures[].value` is a string you can point to in the image.
5. Slide count matches the deck's count in `slide-index.json`.
6. The document validates against the schema.

## When finished

Write `approvals.json`:

```json
{
  "decks_completed": ["..."],
  "slides_registered": 86,
  "slides_unmatched": 0,
  "figures_extracted": 0,
  "low_confidence": ["slide_id", "..."],
  "notes": "anything a reviewer should look at first"
}
```

Prompt adaptation is permitted between attempts — you may add constraints or
restate a rule to improve your own accuracy. You may not weaken the verbatim
rule, the closed-vocabulary rule, or the no-rename rule.
