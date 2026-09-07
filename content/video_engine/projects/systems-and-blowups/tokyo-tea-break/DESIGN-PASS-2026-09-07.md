# Tokyo v3 — the design pass (2026-09-07, `/design-engine`)

The operator, after the third watch: *"This is really good, I think we just need design-taste polishing & chart discipline
now. Mostly that Fed hasn't moved chart. But also to find the best placement style for the docks. Cited sources should take
up minimal space, not maximal. Charts need to make sense with no captions, so labels need to be better. And we should consider
if there's better / more compact / more interesting ways to show the same information. We should spotlight the chart on both
graphs showing the math. We should consider showing a third perspective on the chart which is Japan's rate of selling
against the [rise in rates]."*

The design system in force is ours, not a template: E22 (the ledger page's signature — cream ground, charcoal to the deckle,
Kalam ink), E28 (a chart reads right at a glance — sign as geometry, unit ticks, a stated selection), the brand tokens
(charcoal ground 60 / chalk 30 / coral + sunflower 10), doc 29 §9.23b (series named inline, labels never overprint). The
skill's four stages map onto that: tokens = the brand sheet; style = the ledger page; implementation = the player and its
species; the anti-slop gate = E28 + the motion gates. Everything below was built and is in the v3 build on :8731.

## 1. The Fed page (the ring, the wrapping words)

**Audit of the first version (the card the operator saw).** Three lines on one scale: the 30-year mortgage at 6–7 % pushed
the axis to 3.5–7, so the Fed's flat step and the 10-year's climb (both near 4 %) sat in the bottom third; two inline names
landed at the same corner and overprinted; the sub was a proof sentence in three lines; the source line was the three FRED
IDs and two institutions in two lines of 40 px ink — the largest text on the page after the title.

**What changed.**
- **Two lines, one scale.** Fed funds (grey, `deemph`) against the 10-year (coral). They sit a point apart, so the axis is
  3.5–5 and the step in December and the climb from February fill the frame. The mortgage stays on the object (`mortgage`)
  and is the third NOTE, not a third line.
- **Names that carry the value.** `Fed funds 3.75%`, `10-year 4.77%` — short, so §9.23b's push-apart keeps them one line
  apart at the corner where the portrait layout puts a high-ending line's name.
- **The math, spotlit.** A `bracket` on the 10-year from its February low to its latest: **+80 bp / 10-year Treasury, since
  its February low**, in coral, written 0.55 s after the snap. The holdings page already carries its math (−$122.6B / a tenth
  of the pile on row 4; the two treasury figures on row 2).
- **The sub says what the lines are** in one line: *Fed funds, unchanged since Dec 2025, against the 10-year Treasury, %*.
- **The source is a citation, not a paragraph:** `FRED · Freddie Mac · Sep 2026` at 26 px, 60 % ink, one line
  (`src_style: compact`, opt-in per object — goldens untouched). The IDs, the URLs and the sha256 of every CSV stay in the
  object's `proof`; the dossier carries the rest. The holdings and Meta pages take the same style through their evidence
  builders (`build_tokyo_evidence.py`), so the build's copy of the objects carries it.
- **No captions needed to read it:** title (the claim), sub (what the lines are), the grey flat line named with its rate, the
  coral line named with its rate and bracketed with its rise, `%` on the axis, months on the x-axis, the notes underneath.

## 2. The third perspective — Japan's RATE of selling

`evidence/build_japan_selling.py` derives `ev-japan-selling-v1` from the holdings object on disk (no second fetch): the
month-on-month change in Japan's holdings, Feb–Jun 2026, as **signed bars** — a drop goes DOWN and is blood red, a rise goes
up and is green (E28). Feb +14.0, Mar −47.7, Apr +18.3, May −66.8, Jun −26.4 ($bn); the facts carry the net since the peak
(−122.6, the bracket's number) and the sum of the down months (−140.9). It is honest about the two up months, which the
line hides. It rides as a chart card (`chart_card.py --aspect 9:16`, the bars variant) thrown onto the holdings page on
*"here's what nobody says"* (59.8 s) — after the June print figure, before the Meta page mounts — centred.

Against the 10-year: the Fed page's bracket (+80 bp from the February low) and the first two notes are the other half of
the sentence; a combined chart was rejected on E28 grounds — the `combo` builder draws every bar upward from the base (no
sign), and a line on a second axis has no unit ticks. Two honest charts beat one clever one.

## 3. Dock placement — the study

How a solo card sits on a portrait ledger page today: `page_place` picks the widest free band (above / right / left / below /
foot), ties to the quiet zone, then `DOCK_BAND_ORDER`; a card arrives at READING size (~74 % of the stage width, upper
middle), holds `read_s`, then parks to the small band card over `park_s`. A dock shorter than read + park never parks — it
lives at the reading rect. On the portrait holdings page the winning band is *above*, which is over the title.

| placement | when it is right | when it is wrong |
|---|---|---|
| **above (today's default)** — the reading rect over the title and the chart's top | while the chart is still BUILDING and the card is a cutaway (the panel on "Three men") | after the chart has landed: it hides the data the sentence is about |
| **centred in the band above the caption** (`centre: True`, new) — the reading width, capped at 58 % of the stage height, centred in the top 64 % | when the chart has LEFT (after an undraw — the two fingers over the figures), when the card IS the point (the host's last line, the selling card), when the card will snap up to be the world | over a chart that is still the proof |
| **right quiet zone** — the parked small card | landscape pages with a real column; never on portrait (the chart is 74 % wide) | every portrait page |
| **below the caption band** — 72–90 % of the stage | never for a chart card (too small to read); a badge strip at most | YouTube's own controls sit there |

**Recommendation (applied to v3):** *above* stays the default while a page builds; *centred* is the author's call once the
chart has left or the card is the point. v3 now centres the two fingers (the line is un-drawn by then), the selling card,
and the host on the Fed page. A future default could flip to *centred* whenever the page's last data mark is behind the
dock's enter (E50's clock knows) — backlog R26-22.

## 4. Sources, everywhere

Every Tokyo object now carries `src_style: compact` and a short `src` (institution · month): `US Treasury TIC Table 5 ·
2026-09`, `Yahoo Finance · FRED DGS10 · 2026-09`, `FRED · Freddie Mac · Sep 2026`, `US Treasury TIC · 2026-09-05`. The
provenance (URLs, IDs, hashes, fetch dates) lives on the object and in the dossier, where a reader can check it; the page
cites, it does not footnote.

## 5. Open

- The 10-year's inline name sits at the lower-right corner (the portrait rule for a line ending high), away from its line's
  end; the bracket names the line at the top. A name that rides the line's end when there is room beside is a small layout
  slice (`nameBelow` only when the name would collide).
- The Meta page's callout ring on the 4 % bar strikes through the `$665` value (pre-existing; not this pass).
- A default flip to centred placement after the last data mark (R26-22).
- RU-2 badge-stamp's two-spring landing (R26-20) is still the next kinetics port.
