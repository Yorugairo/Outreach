# Fed liquidity pilot check scope

This is the episode-local contract for the T16 reporting adapter. It does not
change a gate or turn a partial take into a whole-episode result.

**scope schema:** `fed-liquidity.prefix-scope.v1`

## Named build inputs

The build must contain exactly one `*.timeline.json`, named
`fed-liquidity-pilot.timeline.json`. `timeline.json` is the selected take's
word clock and is not a compiled timeline. The adapter reads these raw reports
without rewriting them:

| path | role |
|---|---|
| `GATES-MOTION.md` | existing motion gate rows |
| `SELF-WATCH.md` | existing self-watch and one-shot rows |
| `layout-probe.json` | existing measured layout report |
| `seam-frames.json` | existing measured seam report |

The report's custody is supplied by `BUILD-RECEIPT.json`, schema
`fed-liquidity.build-receipt.v1`. Every path in that receipt is relative to
the episode root (the build's parent), and every SHA-256 field is a 64-digit
hex string. Required receipt fields are:

```json
{
  "schema": "fed-liquidity.build-receipt.v1",
  "script": {"path": "SCRIPT-VO.txt", "sha256": "…"},
  "take": {
    "id": "…",
    "audio": {"path": "…", "sha256": "…"},
    "words": {"path": "…", "sha256": "…"}
  },
  "timeline": {"path": "build-pilot/fed-liquidity-pilot.timeline.json", "sha256": "…"},
  "player": {"path": "build-pilot/player.html", "sha256": "…"},
  "reports": [
    {"path": "build-pilot/GATES-MOTION.md", "sha256": "…"},
    {"path": "build-pilot/SELF-WATCH.md", "sha256": "…"},
    {"path": "build-pilot/layout-probe.json", "sha256": "…"},
    {"path": "build-pilot/seam-frames.json", "sha256": "…"}
  ],
  "assets": {"manifest": {"path": "…", "sha256": "…"}},
  "source_custody": [{"path": "…", "sha256": "…"}],
  "asset_custody": [{"path": "…", "sha256": "…"}],
  "prefix": {
    "sections": ["S01", "S02", "S03", "S04", "S05", "S06", "S07", "S08", "S09"],
    "start_s": 0,
    "end_s": 0,
    "spoken_end_s": 0,
    "end_word_index": 0,
    "measured_from": "take-word-clock"
  },
  "parent_reads": {
    "visual": {
      "status": "READ",
      "evidence": {"path": "review/parent-read-visual.json", "sha256": "…"},
      "read_at": "…"
    },
    "audio": {
      "status": "READ",
      "evidence": {"path": "review/parent-read-audio.json", "sha256": "…"},
      "read_at": "…"
    }
  }
}
```

Each `parent_reads.*.evidence` reference is episode-relative and is checked
with the same path and SHA-256 custody contract as the build receipt. The
referenced file must be a non-empty JSON object with this schema:

```json
{
  "schema": "fed-liquidity.parent-read.v1",
  "kind": "visual",
  "timeline_sha256": "<receipt timeline sha256>",
  "script_sha256": "<receipt script sha256>",
  "audio_sha256": "<receipt take.audio sha256>",
  "observations": [{"at_s": 0, "note": "synthetic review observation"}]
}
```

The `kind` must match its declaration (`visual` or `audio`), all three
digests must match the receipt references, and `observations` must be a
non-empty array. Missing, empty, malformed, mismatched, or outside-root
evidence blocks the PREFIX result. `status: READ` and non-empty `read_at`
remain required. This contract proves evidence custody only; it does not
establish that a human actually watched or listened, and it never grants
automatic human approval.

The four report references must name the exact reviewed build's reports;
their hashes and producer-specific build/player/timeline bindings are checked.
Empty, malformed, rowless, stale or wrong-build reports block review.

`prefix.spoken_end_s` and zero-based `end_word_index` bind the measured
P06/S09 closing word in the selected take. `prefix.end_s` may include only
measured silence through the next word's onset (or the actual take duration
at the final word), never an invented tail or a crossed word. The bound word
clock must match the bound script. The zero values above illustrate field
shape only; production values must be measured and satisfy validation.
The 175–190 second planning estimate is not accepted. The two parent reads are
required for a review-ready result; media metadata alone is not a read.

## Row policy

M01–M34, M36, and M41 remain applicable inside the measured prefix. A real
FAIL inside that span blocks. Only an explicit timestamp at or after the
prefix end may be labelled outside. A missing or ambiguous timestamp blocks.

M35, M37, M38, and M39 are whole-cut distribution floors and are
`DEFERRED_TO_FULL_EPISODE` in prefix mode, never a passing row. The final
ring/outro is likewise deferred. M40 remains `JUDGE`; M42 remains `INFO`.
Any other unexpected FAIL is blocking. Full-episode mode must not consume
these prefix deferrals.

The adapter emits `PILOT-REVIEW.md` with a `PREFIX` heading only. It never
rewrites the raw reports and never emits a whole-cut verdict.
