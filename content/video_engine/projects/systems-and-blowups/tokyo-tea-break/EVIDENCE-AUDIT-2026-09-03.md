# Tokyo Tea Break — evidence & chart audit, 2026-09-03

Every figure that reaches the screen, where it comes from, and whether it can be
checked. Compared against the working pattern in `steel-and-paper/evidence/`, whose
builder header states the standard: *"Real series are fetched live (FRED / Yahoo);
cited figures are marked CITED and carry their source on the document itself…
Nothing here is estimated."*

**Verdict: one chart of six evidence surfaces is real. The rest are asserted in HTML.**
And one of them now contradicts the script.

---

## 1. What exists

| surface | where it lives | built from | sourced | verdict |
|---|---|---|---|---|
| Hedged-yield bars (5.0 / −5.5 / −0.5) | `evidence/tokyo-hedged-yield.{page,series}.json` | **hand-authored JSON** | "Bloomberg / Bank of Japan / US Treasury data" | **WARN** |
| TIC foreign holdings — Japan $1,120.4 B (14.5%), China $770.2 B, UK $745.8 B | **hardcoded in `player.html`** | nothing | none | **FAIL** |
| "Cable Finance Consensus" newsroom ticker | hardcoded in `player.html` | nothing | n/a (satire) | INFO |
| "Actionable Strategy Rules" dock | hardcoded in `player.html` | nothing | none | **FAIL — contradicts the script** |
| `ledger-page-tokyo-v1.html` | `hyperframes/compositions/` | hand-authored | n/a | **WARN — off-palette** |
| Plate 09's blank board (chart dock) | plate PNG | — | — | OK, waiting for a real chart |

## 2. FAIL — the strategy dock contradicts the current narration

It still renders:

> **RULE 01: TRIM DURATION** — Exit 20Y+ Long-Duration Treasuries (TLT / Zero-Coupon drag)
> **RULE 02: DUMP REFI DEBT** — Dump corporations refinancing heavy debt maturities this year.

That is the assignment the operator cut on 2026-09-03 as unusable for a Shorts
audience. The narration now says: *this was never a bond story — pull up your biggest
holding and find its P/E.* Rendering today would put a sell order on screen that the
voice never gives.

**Correction (operator, 2026-09-03):** my first draft of this row said the ticker was
the defect. It is not, and no rule says so. Doc 36 §5.6 forbids *personalized
directives* — the imperative, not the instance. The doctrine positively wants tickers:
doc 34 praises the Identify beat for naming "actual tickers," doc 36 §204 works in
"ticker-level figures," and doc 37 §4b carries a pronunciation standard for them
(spoken name per the operator's ear-probe, "AVAV" → "A-V-A-V" or "AeroVironment") —
which nobody writes for something never said.

**And the deeper problem is the advice itself** (operator, same date): *"exiting 20
year treasuries is still useless advice on a youtube short."* Nobody watching a
90-second Short holds 20-year Treasuries. Removing the imperative would only have made
it politely useless — the same audience error as the bond assignment, left standing on
screen after the script had already been fixed.

So this dock is not rehabilitated, it is **replaced by evidence**. "Actionable Strategy
Rules" was never a dock species anyway: a dock carries proof — a chart, a record, a
stat card — not a bulleted opinion. What the script now teaches is the transmission
from yields to equity multiples, and that has a real, checkable shape: **the same
company's fair value at a 3% discount rate versus 5%**, or high-P/E versus low-P/E
derating as yields rise. That is a chart, it proves the sentence the narration
actually speaks, and the viewer can run it on their own holding.

Tickers stay welcome as instances — a named fund is what makes an abstraction
touchable (doc 32), and doc 37 §4b spells a reached-narration ticker as spoken, not
lettered. They just cannot be the payload of an order.

## 3. FAIL — the TIC table is asserted, not sourced

Japan $1,120.4 B / 14.5%, China $770.2 B, UK $745.8 B live only as HTML in the
player. No evidence file, no manifest entry, no sha256, no date, no series id.

The figures are plausible and the underlying data is public and monthly — the US
Treasury publishes TIC "Major Foreign Holders of Treasury Securities." That is
exactly why this is fixable and exactly why it is not acceptable as-is: **a
retrievable number asserted from memory is the fabrication risk the dossier rule
exists to stop.** It also now carries the whole weight of the precise figure, because
the narration was changed to "over a trillion" and the screen is the only place
`$1.1T` still appears.

## 4. WARN — the one real chart cannot be re-fetched

`tokyo-hedged-yield` passes our own validator (`ledger_page.py` builds it clean —
`judge: []`, signed values, zero baseline, badges keyed to bars, emphasized bar keeps
its sign colour). The geometry is right. The provenance is not:

- there is **no builder script**, so the numbers were typed, not computed;
- the source line reads "Bloomberg / Bank of Japan / US Treasury data" — three
  institutions and no series. Compare steel-and-paper's, which reads
  `BEA via FRED · (Y033RC1Q027SBEA + Y001RC1Q027SBEA) ÷ GDP`;
- no date. **The 5.0% ten-year is the live exposure** — the 10-year last printed 5%
  in October 2023, and the script says "this month."

The hedge cost is derivable from the rate differential rather than quotable, so the
builder should compute it and show its inputs: US 10Y (FRED `DGS10`), the JPY basis,
and the date of both.

## 5. WARN — the ledger composition is off-palette

`ledger-page-tokyo-v1.html` uses `#E05A47`, `#61A8FF`, `#FF7B80`, `#D13438`,
`#F5B72E`. The ground is roughly right (`#F4E6C7` cream, `#25313C` charcoal) but the
accents are not the channel's. E28 fixes sign as geometry and colour: drops
`#B0201F`, rises `#2E9E5B`, sunflower reserved for the callout pill and focus ring.

## 6. The renderer question, measured

`player.html` shares **zero** code with `scene-evidence-player.template.html` — every
template marker is absent (`LP_FOCUS_AT`, `buildLedgerBars`, `stagePop`, `drawChart`,
`drawRecord`: 0 occurrences each). It is a GSAP fork with hardcoded scenes, and the
evidence above is hardcoded *inside* it, which is why none of it has provenance.

Rebuilding on the template is right, and it is not a flag flip. The template is
**1920×1080 in ~a dozen structural places**: `#stage` and `#species` (fixed px +
`viewBox 0 0 1920 1080`), `fitStage`'s `scale(w/1920)`, dock widths 864 / 1056, the
stackcard's `1056/480` aspect, the LP box math, and the caption safe-zone percentages.
A 9:16 mode means turning those constants into two variables and re-deriving the dock
geometry — real work, on the one renderer everything else depends on.

What the template gives back, all of which the fork reimplements or lacks: `drawChart`
animating `.series.json` sidecars, the ledger-page species with E22's deckle and E28's
sign colours, STAGE captions, the cross-reveal wipe, choreography gates, and
`gate_motion_density` (which cannot run at all today — there is no `timeline.json`).

---

## Recommended order

**Evidence first, renderer second.** Rebuilding the player around unsourced numbers
only moves the problem into a better-looking box.

1. **Replace the strategy dock with a chart.** Not a reworded rule list — advice
   about 20-year Treasuries is useless to this audience however it is phrased, and a
   dock carries proof, not opinion. Build the discount-rate chart: one company's value
   at 3% versus 5%, or P/E derating against yields. It proves the sentence the
   narration speaks and the viewer can run it on their own holding.
2. **Write `evidence/build_tokyo_evidence.py`** on the steel-and-paper pattern: fetch
   `DGS10` from FRED, compute the hedge cost from the rate differential, emit both
   charts as `.series.json` sidecars with real source lines and a fetch date, and add
   the TIC holdings as a third, sourced from the Treasury's own release.
3. **Write `EVIDENCE-DOSSIER.md`** — every figure the script speaks, with its series
   and date. The script currently speaks: over a trillion (TIC), five and a half
   percent (hedge cost), five percent (DGS10), sixty-three (a joke, mark it as one).
4. **Re-palette the ledger composition** to E28.
5. **Then** the renderer: add a 9:16 mode to the template and drive the short from a
   `timeline.json`, which also switches the motion gate back on.

Steps 1–4 are independent of the renderer decision and are owed either way.
