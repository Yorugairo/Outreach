# The casebook - defects the operator caught in a frame, and what fixed them

Each case is a folder: `before.png` and `after.png` (540x960, half of the 9:16 stage, seeked with the engine's own
capture, `render_baseline.render_frame`), and `CASE.md` - the operator's words with their ledger row
(`docs/operator-ledger/LEDGER.jsonl` id + timestamp), the defect as a viewer sees it, the fix commit, and the gate
that now catches it or `none - JUDGE (gate owed)`.

A case teaches what a gate cannot yet: read the frame, not the diff. Add one whenever the operator catches something
on screen that the gates passed. The parent writes this folder (P54 T5).

## By defect family

| family | case | gate |
| --- | --- | --- |
| labels | [the ring on the tip label](ring-on-the-tip-label/CASE.md) | none - JUDGE (gate owed) |
| labels | [the name on the neighbour's line](name-on-the-neighbour-line/CASE.md) | none - JUDGE (gate owed) |
| transitions | [the empty cream, chart to chart](empty-cream-chart-to-chart/CASE.md) | M31 (FAIL) |
| the episode as a whole | [the thin one-shot](the-thin-one-shot/CASE.md) | none - JUDGE (no gate can) |
