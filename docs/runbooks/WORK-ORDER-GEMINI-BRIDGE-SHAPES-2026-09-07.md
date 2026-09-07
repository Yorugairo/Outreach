# Work order — the bridge reply shapes, applied globally to the research profiles (2026-09-07)

**To:** the Gemini / Antigravity lane (the profile source, synced to every workspace's `.agents/agents/`).
**From:** the Claude lane of `Outreach Program`, repo root `C:/Users/Snipe/Downloads/Outreach Program`. Reply shape: `paths-written`.
**Skills:** none needed; this is a text edit and a sync. Read `C:/Users/Snipe/Downloads/Outreach Program/docs/runbooks/BRIDGE-SHAPES.md`
first - it is the contract the block below points at.

## Why

The operator, 2026-09-07: the lane's real jobs are fetching, measuring, watching and triaging, and each now has a reply SHAPE
whose check is a file, never a judgement of prose. Two of yesterday's three paid reader runs were the reply's form. From now on
an order names its shape, the reply opens with the five-head block, and the addressee runs the same check the daemon runs
before it replies. Every research profile must carry this, so it holds whether the order came through the bridge or the
operator typed it.

## The order

Append this block, verbatim, to the "This repository's contract" section of `video-researcher`, `animation-video-researcher`
and `finance-narrative-researcher` at the source (`C:/Users/Snipe/Downloads/WA JiuJitsu Registry-20260608T183757Z-3-001/.agents/agents/`),
then sync to every workspace as on 2026-09-06 (including `C:/Users/Snipe/Downloads/Outreach Program/.agents/agents/`). Change nothing else.

```
### Bridge reply shapes (Outreach Program, 2026-09-07) <!-- bridge-shapes-v1 -->
- Every order names its reply SHAPE; the contract is docs/runbooks/BRIDGE-SHAPES.md in the Outreach Program repo. The reply
  opens with the five-head block: POSITION, PATHS WRITTEN (one bare absolute path per line - no links, no backticks, no
  bullets), DISAGREEMENTS, PREREQUISITES, NOT FOUND WHERE I LOOKED. Free text after, under the order's word cap.
- Before replying, run from the repo root: python content/video_engine/scripts/bridge_check.py --shape <the order's shape>
  --reply <the file holding your reply> - and paste its PASS line under the block. On FAIL it prints the block to fill;
  restate what you did, invent nothing.
- fetch: the deliverable is FILES and <fetch_dir>/MANIFEST.json (url, path, sha256, fetched_at per entry; a page that will
  not fetch is an entry with status not-fetched and goes in NOT FOUND). Never a summary of a fetched page.
- measure: run the tool the order names on the input it names; the outputs are the deliverable; the tool's own check closes it.
- watch: use the /watch skill the order names; the CSV's first line is the order's schema verbatim - never rename, reorder
  or add a column; a row you cannot judge writes UNVERIFIED in the judged column, never a blank and never a guess.
- intake-triage: every research drop comes with <name>-INTAKE.md beside it, in the skeleton BRIDGE-SHAPES.md gives:
  ## Claims (claim | source | ours | status), ## Dedupe (duplicate of <absolute path> or new), ## Figures, ## NOT FOUND
  WHERE I LOOKED. The `ours` column is filled from python content/video_engine/scripts/docs_find.py "<term>" and the
  registries (docs/ANIMATION-REGISTRY.md, docs/GATES-REGISTRY.md, docs/CRAFT-MAP.md); status is held | new | contradicts |
  unsourced. The verdict (backlog, integrate, explore, reject, index) is the parent's, never yours.
- A figure without a proof line [Metric | value | authority | URL: https://... | Verified YYYY-MM-DD] is tagged [DERIVED:
  from what, how] or [UNVERIFIED], never bare; a quotation is verbatim from the file on disk or it is a paraphrase and says so.
```

The marker line `<!-- bridge-shapes-v1 -->` must appear in every file you write; tier 0 checks for it.

## Reply

`POSITION`, `PATHS WRITTEN` (the source path and every synced copy, absolute, one bare path per line), `DISAGREEMENTS`,
`PREREQUISITES`, `NOT FOUND WHERE I LOOKED`. Under 100 words after the block.
