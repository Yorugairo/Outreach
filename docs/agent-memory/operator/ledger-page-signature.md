---
name: ledger-page-signature
description: The channel-defining plate-chart species (E22) - settled form after five operator corrections on 2026-09-03 (no outline, addendum 7); what was refused and why
metadata: 
  node_type: memory
  type: project
  originSessionId: 45114c3b-258a-4ca8-9aaf-b674a804cc7e
  modified: 2026-09-03T05:44:52.816Z
---

The LEDGER PAGE is the Money Physics signature (ruling E22, doc 29 s9.26;
P35). Settled form, 2026-09-03 (final, E22 addenda 4-7), after a day of live corrections:

1. A PLAIN cream page rolls out - the ground is a GENERATED world plate
   in the woodblock/vox/washi register (`page.plate`); the flat hex
   #F4E6C7 "reads dull yellow" and is only the fallback.
2. A half savor (0.8s), still and empty.
3. The FIELD: the charcoal fills the PAPER up to its DECKLE (made
   procedurally from the generated blank page; `page.field_plate`
   cross-fades over the plain page) - the deckle edge appears only as the
   ink arrives; that is the hand-drawn feel without roughness. The page
   sits on the CREAM ground (white beyond the deckle read as broken).
   Fallback when no inked plate: scribble or soak filling the board box.
4. NO LINE (addendum 7: "drop the outline entirely ... useless here, not
   pulling weight") - the charcoal arriving on the cream IS the edge.
   `page.board` (the deckle's innermost rectangle, measured from the paper
   mask) stays as the punch centre and the chart box.
5. Ink writes title/source in the HANDWRITING face as the punch begins;
   the chart builds crisp on exact value strings; focus at 7.4s.

**Refused in one sitting (do not retry):** the drawn outline itself
(addendum 7); blob bloom-and-contract (ink-bleed-reveal's mechanism -
"that's not what I meant by bleed"); a gap between ink and edge; coffee-ring stains on the margin ("the
coffee isn't a good look"); a charcoal halo overrunning the board
unevenly ("no, that's not right either"); fibre texture on the paper.
Operator: "just a plain cream background, then the scribble/soak, then
the line draw."

**Why:** the page is a chalkboard on paper - its power is the ink
arriving and the line closing it, not the paper performing. Decoration
on the paper made it read as a prop.

**How to apply:** the species lives in the player template
(`world.kind == "ledger"`, `const LP`); shot rows are
`ledger:<series>:<variant>[:<emphasize>[:<quiet_zone>]]`;
`ledger_page.py` validates the series. Plates come through the claim
lane (claim `steel-and-paper-ledger-page-v1`), reviewed by contact sheet.
See [screen-never-still](screen-never-still.md), [money-physics-brand-sheet](money-physics-brand-sheet.md),
[codex-fulfillment-flow](codex-fulfillment-flow.md).

The hand is **Kalam** (HG2 decided 2026-09-03; OFL; Google Fonts link in the
template head, Inter fallback). See [chart-reads-at-a-glance-e28](chart-reads-at-a-glance-e28.md).
