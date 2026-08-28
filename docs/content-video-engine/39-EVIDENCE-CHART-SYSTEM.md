# 39 — Evidence Chart System

The house design system for every evidence document that docks over a world
plate. One system, all species. Derived by running the `dataviz` method
against our own surface and validating with its script — not by taste.

Companion to doc 29 (evidence & motion standards). Where 29 says *what
counts as evidence*, this says *what it looks like*.

---

## 0. What makes our case different

The reference method assumes a dashboard: hover tooltips, a table view, a
filter row, light and dark modes. **We have none of those.** Our charts
are rendered frames in a video. Three consequences drive every decision
below:

1. **No tooltip, no table view.** The method allows tooltips to carry the
   values a chart doesn't directly label. We have no such fallback, so
   **selective direct labelling is mandatory, not optional** — if a value
   matters, it is drawn on the chart or it is unreadable forever.
2. **Dwell is 12–20 seconds, often less** (doc 29 §9.13). A reader gets
   one pass. This makes **emphasis the default form** and rules out dense
   multi-series categorical work.
3. **Single theme, dark, deliberately.** The document is opaque on a dark
   ground so it separates from the illustrated plate behind it. No light
   mode, no `prefers-color-scheme` — a committed single look, painted
   explicitly.

---

## 1. Surface and ink

Chart surface is `#16181c` — the same ground the delivered charts already
use. All contrast figures measured against it.

| Role | Hex | Contrast |
|---|---|---|
| Chart surface | `#16181c` | — |
| Primary ink (title, values) | `#f2f2ef` | 15.85:1 |
| Secondary ink (subtitle, legend) | `#b9bcc4` | 9.35:1 |
| Muted ink (axis ticks, source line) | `#8b8f98` | 5.48:1 |
| De-emphasis series (context in emphasis form) | `#6b6f78` | 3.53:1 |
| Gridline (hairline, solid) | `#24262b` | 1.17:1 — recessive |
| Baseline / axis rule | `#33363d` | 1.47:1 |

## 2. Categorical palette — validated, fixed order

Four slots. Hues carry the channel's plate accents so an episode reads as
one object, while sharpness and the opaque ground do the separating.

| Slot | Hue | Hex | Contrast |
|---|---|---|---|
| 1 | crimson | `#e5484d` | 4.54:1 |
| 2 | teal | `#1fa892` | 5.99:1 |
| 3 | amber | `#c98500` | 5.79:1 |
| 4 | cobalt | `#4a7fd6` | 4.48:1 |

Validator, dark mode, surface `#16181c`:
- **Adjacent pairlist (bars, lines, stacks) — all four slots PASS.**
  Worst adjacent CVD ΔE 9.7 (deutan); worst adjacent normal-vision ΔE 20.5.
- **All-pairs (scatter, small multiples) — first three PASS**, with one
  **WARN**: crimson ↔ amber sits at CVD ΔE 6.3 (deutan), inside the 6–8
  band. That is legal **only with secondary encoding** — which our medium
  already forces, since every series is direct-labelled.

Two standing rules from that warn:
- **Assign in fixed order, never cycled.** Colour follows the entity.
- **In a two-series chart, prefer crimson + teal** (ΔE 9.7). Reach for
  amber as a third, never as the partner to crimson alone.

**Never** a fifth generated hue. Past four: fold to "Other", facet into
small multiples, or change the form.

Text never wears a series colour. Identity comes from the coloured mark
beside the text.

## 3. Type scale — sized for video, not a screen

Expressed as a fraction of authored chart width `W` so it survives any
render size. **Author at 2× the dock's placed width** (a solo finance dock
is 1056px per doc 29 §9.10, so author at **2112 × 960**; the delivered
1760 × 800 charts are acceptable legacy). **Stat tiles author shorter —
2112 × 640** — since a tile has no plot to give height to.

| Role | Fraction of W | at W=2112 | Weight |
|---|---|---|---|
| Title | 0.030 | 63px | 600 |
| Subtitle / deck | 0.019 | 40px | 400 |
| **Direct label / value** | 0.024 | 51px | 600 |
| Legend | 0.018 | 38px | 500 |
| Axis tick | 0.017 | 36px | 400 |
| Source line | 0.014 | 30px | 400 |
| Hero figure (stat tile) | 0.085 | 180px | 600 |

Rationale: at a 0.5 placement downscale on a 1080p frame, the smallest
essential text lands near 18px — the practical floor for phone viewing.
Anything below the source line is decoration and does not belong.

Typeface: the system sans throughout (`system-ui, -apple-system,
"Segoe UI", sans-serif`). **No serif or display face anywhere**, including
hero figures — a display face reads as decoration and undercuts the
document's credibility. Proportional figures on hero and standalone
values; `tabular-nums` only in axis ticks and any aligned column.

## 4. Marks

| Mark | Spec (at W=2112; scale proportionally) |
|---|---|
| Line | 5px, round join/cap |
| Bar / column | **≤ 45% of its band** (never an absolute px cap — see note), rounded data-end where the renderer supports it, square at baseline |
| Marker / end-dot | r ≥ 11px, filled, with a 5px surface-colour ring |
| Area fill | series hue at ~10% opacity — a wash, never a block |
| Gridline / axis | 2px **solid** hairline, recessive. Never dashed |
| Surface gap | 5px in surface colour between touching bars/segments |

Weights are the reference specs scaled for video (the reference's 2px line
would vanish at broadcast downscale). Never draw a border around a mark to
separate it — the gap and the ring are the mechanism.

Two notes from building the first samples:

- **Bar width is proportional, not absolute.** The reference's "≤24px"
  assumes a dashboard with many bars; translated literally to a 2112px
  video document it produces threads. The rule's *reason* is "never fill
  the slot; leave the band's leftover as air," so we express it as a
  fraction of the band. A three-column document at 44% of band is correct.
- **Rounded data-ends are renderer-dependent.** HTML/SVG rounds natively;
  matplotlib output ships square ends, which is acceptable — the surface
  gap, not the corner radius, is what separates marks. Do not contort a
  renderer to chase the radius.

## 5. Threshold and annotation marks (our addition)

The reference method has no vocabulary for "this crossed a historic line,"
which several of our documents need.

- **Threshold rule.** A 2px **dashed** horizontal line in muted ink with a
  right-aligned label above it. Dashing is *reserved for thresholds* —
  which is exactly why gridlines must stay solid. A dash on this system
  always means "reference level, not data."
- **Peak / trough annotation.** A 2px leader from the point to a label set
  in secondary ink, with the date and value on two lines. Maximum **two
  per chart** — past that the eye has nowhere to rest in 15 seconds.
- **Era band.** A `rgba(255,255,255,0.04)` vertical band behind a named
  span, labelled in muted ink at the top of the plot. For "the mania",
  "the dot-com peak", and similar.
- **Callout value.** The single number the narration is speaking gets the
  direct-label treatment at 0.024W in primary ink, never a series colour.

## 6. Form selection — the 15-second test

Given the dwell budget, form is chosen by what a reader can finish.

| The document's job | Form | Colour job |
|---|---|---|
| One number is the whole point | **Stat tile / hero figure** | none — ink only |
| A single value against a limit | **Meter** | one hue + track |
| One series is the story | **Emphasis** — accent + `#6b6f78` context | 1 hue + gray |
| Trend over time, one subject | Line, optional 10% area | slot 1 |
| Two subjects compared | Two lines, both direct-labelled | slots 1 + 2 |
| Magnitude across ≤ 6 categories | Column | slot 1 for all |
| Before → after | Dumbbell | one hue, two shades |
| Part-to-whole | Stacked bar, ≤ 4 segments | slots in order |

**Emphasis is the default.** If a chart has more than two colours, justify
it. If the story is "this one number," it is a stat tile — a one-bar bar
chart is an anti-pattern, and several documents in the Steel and Paper
queue (7% of GDP, $822B in leases, 94% of operating cash flow) are stat
tiles, not charts.

**Never** a dual axis. Two measures of different scale become two
documents, small multiples, or both indexed to 100 at t0 on one axis.

## 7. Required chrome on every evidence document

A document is only evidence if a viewer can check it. Every render carries,
without exception:

1. **Title** — the claim in plain words, sentence case.
2. **Source line**, bottom-left, muted: publisher, series, and window —
   e.g. `Data: Yahoo Finance, ^TNX · 1998-01 to 2002-01`, or
   `Figures via Bravos Research`, or `Campbell & Turner railway share index`.
3. **Verbatim numerals.** Any figure a badge quotes must appear on the
   document exactly as the badge states it (doc 29 §9.8 / ruling B3).
4. **No production scaffolding** — no slot ids, no claim ids, no approval
   state, ever.

## 8. Checks before a document ships

- [ ] Form chosen by §6 — and it is not a chart when it should be a tile
- [ ] Palette slots assigned in fixed order; ≤ 4; crimson+teal for a pair
- [ ] Validator re-run if any hue changed
- [ ] Every value the narration speaks is **directly labelled** (no
      tooltip exists to fall back on)
- [ ] Gridlines solid; dashes only on thresholds
- [ ] Title + source line present; numerals verbatim
- [ ] Rendered and **looked at** — label collisions, overflow, geometry
- [ ] Checked against the reference anti-pattern list

## 9. Provenance

Palette and checks produced with the `dataviz` skill's validator
(`validate_palette.js`), dark mode, surface `#16181c`, 2026-08-25.
Re-run it whenever a hue changes:

```bash
node scripts/validate_palette.js "#e5484d,#1fa892,#c98500,#4a7fd6" --mode dark --surface "#16181c"
```

---

## 10. The record document — typewriter + highlighter

> **APPROVED by the operator, 2026-08-25** — species and motion both.
> This is the standing treatment for quotes, transcripts, and filing
> extracts.

Operator design call, 2026-08-25: *"for quotes and earnings documents etc
where we want to produce direct information, we should do typewriter +
highlighter."*

This gives the evidence layer **two species**, and the split is
information design, not decoration — a viewer knows within a beat which
kind of claim they are looking at:

| Species | Ground | Face | Carries |
|---|---|---|---|
| **Data document** (§1–§9) | dark `#16181c` | system sans | a measurement |
| **Record document** (this section) | paper `#f0eadc` | typewriter | something said or filed |

It also resolves the standing tension with ruling B2. A record document
is not a manufactured info card: it is a *record* — dated, attributed,
verbatim, with the marked phrase being the one the narration speaks. The
ban in B2 targets prose we wrote and dressed up as evidence. This is the
opposite: words someone else is on record saying, presented as the
document they came from.

### Tokens

| Role | Hex | Contrast on paper |
|---|---|---|
| Paper | `#f0eadc` | — |
| Ink (body, values) | `#17150f` | 15.22:1 |
| Meta (header, kicker, source) | `#6b665c` | 4.76:1 |
| Rule / dot leaders | `#cdc5b4` | — |
| Highlighter | `rgba(245,201,63,0.72)` | ink over it: **12.5:1** |

Highlighter is a CSS gradient with soft ends
(`linear-gradient(101deg, transparent .4%, var(--hl) 1.8%, var(--hl)
98.2%, transparent 99.6%)`) so it reads as a marker stroke rather than a
filled rectangle. Where the phrase wraps, each line gets its own stroke —
correct, and what a real marker does.

### Rules

1. **One highlight per document**, and it marks *exactly* the phrase or
   figure the narration speaks. Never a second, never decorative. The
   highlight is the callout — it replaces the badge for this species.
2. **Verbatim or nothing.** The body text is the source's words or the
   filing's figures, unedited. Ellipses are allowed; paraphrase is not.
   If we cannot quote it exactly, it is not a record document.
3. **Required chrome:** outlet/source + date in the header rule;
   a kicker naming the speaker and context; the body; an attribution
   line (name, title, organisation); a source line at the foot.
4. **Size to content.** A transcript runs `2112 × 960`; a short filing
   extract runs `2112 × 760`. Never pad a short document to a tall canvas
   — the dead space reads as a design error.
5. **Dot leaders** (`4px dotted`) between label and value on any
   filing/figure extract. They carry the eye and reinforce the species.
6. **No charts on paper, no prose on the dark ground.** A document that
   wants both is two documents.

### Type (at W=2112)

| Role | Size | Notes |
|---|---|---|
| Header (outlet · date) | 30px | uppercase, `.16em` tracking, meta |
| Kicker | 34px | meta |
| Quote body | 62px | line-height 1.44 |
| Figure rows | 46px | line-height 1.62, values bold |
| Attribution | 36px | name bold |
| Source line | 28px | meta, above a hairline |

Face: `"Lucida Sans Typewriter", "Courier New", monospace`. Chosen over
Courier New alone, which is too thin to survive the placement downscale.

**On §3's "no serif or display face anywhere":** that rule governs
*charts*, and its reason is that a decorative face on a hero figure
undercuts a measurement. A record document has the opposite job — the
typewriter is what makes it read as a record rather than a graphic. Same
lesson as doc 29 §9.14: a rule's reason is its scope.

### Production

HTML + CSS, exported headless:

```bash
msedge.exe --headless=new --disable-gpu --hide-scrollbars \
  --screenshot="<out>.png" --window-size=2112,960 \
  --virtual-time-budget=6000 "file:///<in>.html"
```

Matplotlib is the wrong tool here — inline phrase highlighting needs real
text flow. Note: the exporter will silently keep a stale PNG if the file
already exists; delete the target first, or verify the timestamp.

### 10.1 The record document is ANIMATED — it reads along with the voice

Operator clarification, 2026-08-25: typewriter + highlighter are
**motion**, not a static treatment. The document types on and the marker
sweeps as the narration speaks the words. A still document held for 15
seconds is dead air; a document that reads along is synchronised evidence.

**The timing source is the words sidecar, never frames-per-character.**
This is the whole point. A generic typewriter runs at N frames per
character; ours runs off the canonical word timings already driving the
kinetic captions (doc 29 C2). The document and the captions therefore
cannot drift from each other or from the voice, because all three read
the same file.

| Parameter | Value | Why |
|---|---|---|
| Character reveal | word's own span × 0.72 | finishes each word just before the next begins |
| Marker sweep, per word | **0.20s**, ease-out cubic | fast enough to feel like a stroke, not a wipe |
| Marker trigger | that word's timestamp | the mark lands as the word is said |
| Attribution fade-in | END + 0.15s, 0.35s ease-out | settles after the quote lands |
| Source line fade-in | END + 0.45s | last, quietest |
| Cursor | solid block, follows the text | blinks **only** when idle (t > END) |

**Implementation rules**

1. **String slicing, never per-character opacity.** Per-character opacity
   jitters layout and destroys subpixel rendering. (Rule carried over
   verbatim from the `remotion-video-creation` reference, which is
   installed locally at `~/.codex/skills/remotion-video-creation`.)
2. **Per-word strokes, not one stroke across the phrase.** A single
   absolutely-positioned stroke measures the inline box as one rectangle
   and breaks the moment the phrase wraps to a new line — it overshoots
   the line end. Each highlighted word carries its own stroke; wrapping
   then works by construction. Fold the trailing space *into* the span so
   consecutive words read as one marker pass rather than separate boxes.
3. **Animate `transform: scaleX` with `transformOrigin: left center`,
   not `background-size`.** The reference implementation does this and it
   is correct: a transform is GPU-composited, while animating
   `background-size` forces a repaint every frame. The prototype uses
   `background-size` for brevity; **production must use scaleX.**
4. **Spring, not linear.** The reference uses
   `spring({fps, frame, config:{damping:200}, delay, durationInFrames})`.
   Ease-out cubic is an acceptable substitute where spring is unavailable.
5. **Honour `prefers-reduced-motion`** — render the settled final state,
   no typing, no sweep, no cursor.
6. **One phrase marked, still.** §10 rule 1 holds under motion: one
   highlight per document, on exactly the words the narration speaks.

**Prototype:** `evidence/prototypes/record-document-motion.html`. Append
`?t=SECONDS` to freeze any frame — used for contact-sheet review and
filmstrip export, since headless capture cannot record motion.

**Production route:** the scene-evidence player already owns a word-timed
renderer for captions; the record document is a second consumer of that
same timing feed, not a new pipeline. Remotion remains available for the
editor lane.

## 11. Data documents animate too — the line is drawn by narration beats

Operator question, 2026-08-25: keep charts as they are, or move to manim?
**Answer: keep them code-rendered, and animate them in the player.**

Manim is installed (0.20.1) and was considered. It is the wrong tool for
evidence documents, for one decisive reason and three supporting ones:

- **It renders on its own clock.** Manim emits a video file on an
  internal timeline. Our motion must run off the canonical word timings
  (§10.1), so a manim chart would need render → align → re-render on
  every timing change. The player consumes the words sidecar directly.
- Its visual identity is strongly recognisable and is not ours; restyling
  it to §1–§2 fights the framework.
- Its strength is constructing mathematical objects, not financial time
  series. (No LaTeX on PATH here either, so its typesetting is degraded.)
- Video output is harder to dock, mask and layer than a live SVG element.

**Manim keeps a place in the kit for mechanism explainers** — a named
Money Physics format — where genuine math exposition is the content.
Not for evidence documents.

### The beat-keyed draw

The important idea, and the thing that makes this better than a chart
appearing whole: **the chart's own clock is keyed to narration beats, not
to linear playback.** The draw is defined as a small keyframe table
mapping narration seconds to progress along the data:

```js
const DRAW_KEYS = [
  [0.30, 0.00],   // chrome settled, pen down
  [4.00, 0.355],  // reaches the Oct-1845 peak as "today's money" lands
  [5.40, 0.355],  // HOLDS while the voice turns ("Then the stocks…")
  [8.00, 1.00]    // completes the decline on "sixty percent"
];
```

The hold at the peak is the point. The line waits at its high while the
narration pivots, then falls exactly as the words describe the fall. A
chart that merely animates left-to-right at constant speed does not do
this, and it is the difference between decoration and evidence.

### Mechanics

| Element | Technique |
|---|---|
| Line draw | SVG `stroke-dashoffset` from `getTotalLength()` → 0 |
| Area wash | same path closed to the baseline, revealed by an animated `clipPath` rect that tracks the line's x |
| Bars | `transform: scaleY` with `transform-origin: bottom` |
| Annotation arrival | opacity fade, 0.35s, at the timestamp of the word that names it |
| Chrome (grid, ticks, band, threshold) | fades in first, before the pen goes down |

Annotations are **triggered by their word**, not by the line reaching
them: the peak label lands on "today's money", the trough label on "sixty
percent". Cap at two per chart (§5).

### Two bugs worth not repeating

1. **Building the point list, do not add the axis origin to the data x.**
   `X0 + ANCH[0][0] + …` silently produced x ≈ 3685 and drew the whole
   path off-canvas — the chart rendered with correct chrome and an
   invisible line, which looks like a draw bug rather than a data bug.
2. **Watch operator precedence in the clip width.**
   `PW*p + PL.l>0 ? a : b` evaluates `(PW*p + PL.l) > 0` and always takes
   the first branch. Compute the clip explicitly from the path's own x
   range.

Both were caught only by rendering and looking (§8, last check). The
validator cannot see either.

**Prototype:** `evidence/prototypes/data-document-motion.html`, with the
same `?t=SECONDS` freeze for filmstrip export.

## 12. The instrument reading — our own measurement

A third species, added 2026-08-25 after the operator surfaced the SCML
ledger (`~/.claude/Claude Work/Claude Files/scml-ledger/scml-ledger`) —
a live alt-data pipeline: 27 workers, a 42-name watchlist, and a memory
tripwire that derives **$/kg by grade from Korea Customs export
statistics** (HS 8542.32).

| Species | Ground | Face | Carries |
|---|---|---|---|
| Data document (§1–§9) | dark | sans | a measurement from public data |
| Record document (§10) | paper | typewriter | something said or filed |
| **Instrument reading** (§12) | dark | sans | **our own measurement** |

**Why it is its own species.** A data document says "here is the public
record." An instrument reading says "here is a number nobody else
publishes, and here is the apparatus that produced it." The apparatus is
part of the evidence — a reading without its method and its as-of date is
not evidence, it is an assertion. This is the format that lets Money
Physics compete on something other than chart-reading (ruling A3).

### Mandatory chrome — all six, no exceptions

1. **Reading period**, in the eyebrow, top right — the period the DATA
   covers, never the date it was computed.
2. **Method line** — source, series/HS code, and what the number is.
3. **The tripwire** — the threshold, stated as a falsifiable condition.
4. **Status** — triggered or not, in plain words.
5. **Signal class** — `leading` / `confirming`, per the ledger's own
   framing (`scml/research/memory_watch.py` labels every alert).
6. **The caveat that would embarrass us if omitted** — publication lag,
   and what the measure is *not*.

### The lag rule (learned the hard way)

`scml.cli memtrend` prints `eval_date` — the date the monitor ran. The
underlying customs release is for a much earlier period. On 2026-08-28
the CLI showed readings stamped 08-28, 07-01 and 06-30 with **identical
values**; querying `trade_facts` directly showed the actual reporting
period was **2026-05**, roughly a three-month publication lag.

> **Never take the CLI's display date as the reading date.** Query
> `period_label` / `period_start` and publish that. Publishing an
> evaluation date as a data date states a stale number as current, which
> is the same class of error as the GDP-peak overclaim (§ dossier).

### Open data-quality issue

`trade_facts` currently holds **two rows per grade per period** with
different unit values (2026-05 HBM-class: 123,622 and 83,779; DRAM:
31,374 and 77,557). The CLI surfaces one. Until that is resolved, an
instrument card must not present a single figure as definitive — either
reconcile upstream, or show the range. **Flagged to the operator, not
silently resolved.**

### Standing constraints

- **Refresh before publishing.** `scml.cli status` reported source health
  DEGRADED with 27 stale/empty workers. A stale instrument is worse than
  no instrument, because it looks live.
- **Licensing pass** before air: DART, KRX, Comtrade and FINRA carry
  redistribution terms. Derived charts are near-certainly fine;
  republishing feeds may not be.
- **No advice framing.** The ledger emits BULL/BEAR/RISK theses and a
  watchlist. On air these become mechanisms and disclosed positions,
  never recommendations (DOCTRINE-CORE, "no advice framing").
- **The `.env` never appears on screen.** It holds live keys (DART, FRED,
  data.go.kr, OpenRouter, Gemini). Any screen capture of the CLI is
  checked for it first.

**Built:** `evidence/ev-instrument-memory.html` → `objects/`, sized to
content at 2112 × 1150.
