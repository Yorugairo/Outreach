---
name: opening-minute-e24
description: "Ruling E24 (2026-09-03) - the opening minute answers the thumbnail, matches the packaging's tension, and never opens on a full unannotated chart; gates G45/J12, M10, M11; roadmap-by-0:45 DECISION open"
metadata: 
  node_type: memory
  type: project
  originSessionId: 45114c3b-258a-4ca8-9aaf-b674a804cc7e
  modified: 2026-09-03T07:16:19.893Z
---

An outside analyst's drop-off read of Steel and Paper, which the operator
checked against the analytics ("checks out"), became ruling E24 and doc 29
s9.29 on 2026-09-03:

1. **Confirm the click.** The first sentence ANSWERS THE THUMBNAIL. The
   operator's framing: "it must answer the thumbnail, which is easiest done
   with the title, because the title is the words packaged with the
   thumbnail." No greeting, no lore, no history first. Gate G45 checks the
   title words in the first two sentences as a PROXY; J12 is the reader's
   verdict on the thumbnail itself (the gate prints the thumbnail path).
2. **Match the packaging's tension.** Anchor 0-10s, complication 10-25s,
   roadmap by 0:45. DECIDED 2026-09-03: the promise window is 0:30-0:45
   (`PROMISE_WIN`), G09 FAILs past 0:45; doc 38's 0:60 is superseded.
3. **Never open on the full chart.** Charts are evidence, not the hook. In
   the first minute no still over 6s (M10); the first chart enters between
   the 8s paradox and 20s WITH a targeted species (spotlight / callout /
   punch on its divergence) and a sound hit (M11). Ep1 landed a full
   unannotated chart at 0:09.5 and held it - the named failure mode; the
   drop is at 0:45-1:00.

**Why it generalizes:** the opening is where the viewer is convinced the
evidence will be worth the time, not where the evidence is presented; a
chart's job in the first minute is to prove one sentence, spotlit, then
leave.

**How to apply:** run `run_script_gates.py ... --title "<title>"
--thumb-file <thumbnail.png>`; author the first chart row with a species
entry (spotlight/callout/punch, declared target) and a sound cue; the
re-script (REWRITE-ORDER-G) must pass G45/M10/M11 before recording.
See [screen-never-still](screen-never-still.md), [ledger-page-signature](ledger-page-signature.md).

**Shipped 2026-09-03 (commit eb52f86):** G45/J12/M10/M11 and E25's M12
are in the gates; ep1 baselines: opening gate 28 FAIL (G45: the first
sentence 'The safest thing you own looks like this' answers none of
ai/bubble/real/survives/steel/paper), motion gate 8 FAIL (M10 three
stills over 6s in the first minute; M11 the first chart at 0:09.5 full and
unannotated; M12 twenty-five chart docks held as homework).

