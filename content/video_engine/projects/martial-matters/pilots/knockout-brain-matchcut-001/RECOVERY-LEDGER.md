# Knockout Brain Match-Cut — Recovery Ledger

Status: recovery complete. All recovered media is `review_only` and
`render_eligible=false` pending operator review.

## Acceptance criteria

- Recover the highest-quality publicly accessible source for the supplied Short
  and, if identifiable, its underlying fight footage.
- Recover the official UFC Henderson–Bisping knockout clip in the highest
  publicly accessible quality.
- Preserve the news angle with primary-source support for the case language;
  distinguish allegation, charge, acquittal/dismissal, and verified outcome.
- Record source URLs, retrieval commands, SHA-256, codec, dimensions, frame
  rate, duration, audio streams, and exact knockout time ranges.
- Produce contact sheets for operator inspection. Do not promote or publish.

## Lanes

| Lane | Owner | Write set | State |
|---|---|---|---|
| Supplied Short and underlying bout | Luna `recover_source_fight` | `assets/raw/source-short/` | complete; parent probed, hash-checked, and inspected |
| Henderson–Bisping official clip | Luna `recover_hendo_bisping` | `assets/raw/henderson-bisping/` | complete; parent probed, hash-checked, and inspected |
| Case-source verification | Luna `recover_case_sources` | `research/case/` | complete; parent hash-checked |

## Known starting evidence

- Supplied Short: `https://youtube.com/shorts/ID0sgoVzFNQ`
- Format inventory exposes a 1080x1920 AVC source (`137`) plus 1080p VP9/AV1
  variants; the earlier 360x640 watch copy is not the recovery ceiling.
- Official first-fight highlight: `https://www.ufc.com/video/160276`; UFC's
  published result is Sean Sharaf over Gable Steveson by KO (left hand) at
  0:12 of round one. The supplied Short's `Sean Sherriff` / `10 seconds`
  wording is not source-accurate.
- Official comparison source: `https://www.ufc.com/video/49967`
- Case wording floor: describe the 2019 matter as criminal sexual-conduct
  allegations and a no-charge prosecutorial decision unless a stronger primary
  record is recovered. A quoted fighter accusation is not an adjudicated fact.
- Existing temporary observations are not custody artifacts and must not be
  treated as recovered deliverables.

## Parent integration checklist

- [x] Inspect all receipts and direct artifacts.
- [x] Verify hashes and media metadata independently.
- [x] Inspect contact sheets and knockout windows.
- [x] Reconcile case wording to primary sources.
- [x] Keep all artifacts quarantined pending operator decision.
