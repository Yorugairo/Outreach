# The Great American Debt Trap - what the engine can now do for it (advice, 2026-09-27)

Written by the engine lane for the production lane. It maps the episode's own chart priorities
(`AMERICAN-DEBT-TRAP-CURRENT-EVIDENCE-2026-09-20.md` "Evidence and chart priorities") and the V15 first act
(`projects/systems-and-blowups/american-debt-trap/SHOT-TABLE-V15.py`) to what landed on `main` in the last week.
Every name below is a CAPABILITIES row title in `docs/content-video-engine/CAPABILITIES.md` - read the row before
authoring; its grammar and limits are the truth, not this page. Recipes live in `content/video_engine/effects/recipes/`
(pick by `use_when`). Retrieval first: `python content/video_engine/scripts/docs_find.py "<term>"`.

## First: rebuild V15 on today's engine and diff it

V15's `pilot-clean` was compiled on last week's engine. Rebuild and compare frames before judging anything:
- a recast's title / sub / source now hand over WHOLE (no half-written titles) - P72 T26 / T53 (j);
- cards are placed at the aspect they are DRAWN at (R26-348): an unauthored square or tall still can land small on a
  busy page - give any card that must read large a box (`centre` + `centre_w/x/y`);
- a chart card keeps its source line at any size (P72 T53 (f));
- played == cold (R26-397): a played render now equals what the gates measured;
- the 16:9 source line is UNCHANGED (R26-357 is parked, not landed).

## The six chart priorities -> what to use

1. **Debt timeline ($38T / $39T / $40T crossings, the 154-day interval).**
   - A line page with the crossings marked, or **THE DATED EVENT TIMELINE** (P73 T2) if the dates carry the beat.
   - **THE BOX ROUND THE LAST MOVE** (`span form: "box"`, P72 T46g) round the last $39T -> $40T stretch, the
     interval written as the span's label from the derived dates (never "a trillion every 70 days").
   - **THE AXIS TAG** with `guide: "rule"` (P72 T53 (i)) for a full-height dated rule on "August 18, 2026".
   - The level join (P71 T10) draws a dashed level from one datum to another and writes the gap - good for $38T -> $40T.
   - Do NOT project a $41T date: a projection is an estimate (E77) and needs its own source.
2. **Interest burden (21.71 cents of each revenue dollar).**
   - **The fill gauge** (`;form=gauge`, P70 T3): one share of one whole fills a capsule - the "one revenue dollar" picture.
   - **THE EQUATION ROW** (P70 T6) + `recipe:the-formula-by-its-words` (P71 T34): "1,052 / 4,845 = 21.71%" written in
     spoken order, and it must be TRUE (the page checks the arithmetic). V15 already uses `chart_to compare` for this
     beat; the equation row is the alternative when the sentence says the division out loud.
   - Label it "FY2026 October-August, preliminary" on the page (E28 / the evidence doc).
3. **Rate timeline (policy range vs 10/20/30-year yields).**
   - **SOLO** (P69 T37): on its word the other lines mute and the 20-year keeps its ink; the lines bloom (s117).
   - **A page's later states** (P72 T26): `then=<series>:<variant>:domain=<lo>,<hi>` gives a later state its own scale;
     `undraw` with `recede: true` fades the chrome while the line leaves.
   - The axis tag / dated rule for the observation date. Avoid **THE LEAD-LAG BRACKET** (P71 T27) here - it writes a
     lag and implies cause, which the evidence doc forbids ("never imply same-day movement proves a single cause").
4. **Household receipt (same loan, 6.01% vs 6.95%: $2,005.61 vs $2,211.97, +$206.36/month).**
   - **A BAR RE-VALUED, THEN TO NOW** (`chart_to compare` with `from`, P71 T24): one bar re-values from the old rate's
     payment to the new one - the $206 moves in front of the viewer, not a static two-bar chart.
   - The level join writes the +$206.36 gap between the two bar tops. **THE LEADER** (P72 T53 (h)) can point a written
     figure back at the bar it compares to; its computed label is a RATIO - for a difference use the level join.
   - **THE BALANCE SCALE** (P70 T7) for "pay the card off vs keep the cash" ($1,249.95 a year vs liquidity) - both
     true at once, which is exactly the evidence doc's caveat.
   - Every household number is ILLUSTRATIVE: the page title or sub must say so (the evidence doc's rule).
5. **Exposure map (fixed mortgage / variable card or HELOC / new refinancing).**
   - A flow `layout: hub` (used in `recipe:rise-turn-consequence`, P71 T35): the household at the hub, its debts on
     the rim, the link that RESETS failing on its word. (No check mark on a rim node yet - R26-414 (b).)
   - **A VERDICT ON A CHART TILE** (P71 T19): a tick / cross lands on its word - "fixed: doesn't reset" vs "variable:
     resets".
6. **Optional 1942-1951 rate cap (explicitly historical).**
   - `recipe:the-epoch-walk` (P71 T34): a named era shaded, then the line carried on - keeps history a separate layer.
   - **THE INSET ECHO, THEN THE QUESTION** (P71 T33): today's yield parked left, the capped era as a twin beside it, a
     "?" at the end - the rhyme shown, the policy left open. A same-measure twin shares the host's `domain`.

## Also new and useful

- **THE ICEBERG STAGE** (P72 T53 (a), `recipe:the-hidden-base`): visible vs hidden under a waterline. It fits "the
  debt you see vs the debt that must reset" ONLY with a sourced maturity / reset split - none is in the evidence yet.
- **THE GROUP BRACKET** (P72 T53 (b)): one span over several bars under one label ("all of this resets").
- **THE LEADER**: a headline figure arcs back to the number it dwarfs, the multiple on the arc.
- The chapter pill (P70 T9) to hold an act name across cuts.

## Watch-outs (rulings that bind here)

- **No fake documents or generated logos** (standing rule): V15's disabled "renewal letter" prop stays disabled unless
  it is visibly an illustration that imitates no real institution; a record card must show a REAL document.
- V15 already rejected generic UI stamps over narrative art - prefer motivated props, documents or ledgers.
- A number on a plate is never painted: every figure lands as a docked, sourced card or on a ledger page.
- "Business Risk at JPMorgan" is the only confirmed credential (the evidence doc).
- The ledger's notes stop at V14 while V15 files exist: record V15's state in `PRODUCTION-LEDGER.md` first.
- The YouTube voice is still unchosen (P68-HG3) - the same decision blocks this episode and the AMD one.
