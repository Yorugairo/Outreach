# CHART DISCIPLINE — portable

Audited against the record 2026-09-13 (P54, docs/operator-ledger/PORTABLE-AUDIT.md).

Model-agnostic, renderer-agnostic. A fresh agent with only this repo
must be able to QC and build production charts from this page READ WITH
the later chart law below - this page alone is no longer sufficient.
Template-enforced reference implementation:
`docs/content-video-engine/samples/scene-evidence-player.template.html`
(+ doc 29 §9.22–9.23). Extracted 2026-08-30, Steel and Paper QC.

## Later chart law (read these with this page)

Each ruling lives in `docs/portable/OPERATOR-RULINGS.md` under its id;
the ruling wins wherever this page or doc 29 differs.

- **E25** - a chart proves the sentence being spoken and leaves; it
  never survives a plate change; a return re-enters spotlit on the new
  datum; a dock holds 10s at most, 6s in the opening minute (gate M12).
- **E28** - the sign is geometry (a drop is a bar going DOWN from
  zero); a selected axis states its rule on the page; the first-glance
  read is the viewer's. Addenda: the label is data too; sign is colour
  too. Amended 2026-09-08: the light follows the sentence (a held
  focus light releases on the first word of the next sentence).
- **E43** - on a short the chart carries the number; a beat the named
  screen carries is not a viewer miss.
- **E50** - deployed life 6-8 s from the LAST data mark, 12 s at
  most, then it un-draws or becomes the next thing. Amended
  2026-09-08: the 6 s is a floor that binds only on a page that
  arrives built (a page that draws is exempt; gate M21), and a built
  page never mounts.
- **E52** - a page cites in one compact line; a chart reads with no
  caption (title = the claim, every series named with its value at its
  end, the unit on the axis, the selection stated); the math is drawn.
- **E53** - chart form is law: the perception hierarchy (pie/donut and
  treemap only under their four-condition exceptions); never a stacked
  bar; bars discrete, lines continuous; one unit before two, and two
  scales are an OVERLAY, never tiers; a policy rate is a rule; the gap
  is drawn; a declared colour outranks a default; the label lives at
  the line's end. Addendum 2026-09-09: a value already on the chart is
  never a reference line.
- **E56** - a ring circles a number or a point on a chart, nothing
  else (compiler-gated); a picture's focus is a light; every new
  addition passes the life check.
- **E58** - a chart changes STATE (rescale, extend, recast, morph,
  park) and never cuts to another chart of the same data; a cut still
  wins between different arguments (gate M23).
- **E60** - the breakthrough is a rescale: the bar builds to the
  comparator's level, then shoots while the scale rewrites under it;
  never a break glyph.
- **E64** - a chart becomes another chart by re-writing itself or by
  morphing, never by a cut; the axes hand over by re-writing.
- **E67** - the field's inks are electric and high-contrast on the
  charcoal, the live line blooms, grey is never a default; the chart
  is the thumbnail (its landing frame reads at 320 px wide).

## The acceptance gate (operator ruling)

**"The charts need to fully communicate their own story without
narration."** Mute the audio, screenshot the chart, hand it to a
stranger. If any ink needs the voiceover to explain it, the chart is
not done.

## The eleven failure classes (each shipped past a linter once)

1. **Anonymous reference line** — every series is named at its end;
   a late-fading series' label fades in WITH it. A dashed reference
   rule is only for a number an institution SETS (a policy rate, a
   target, a threshold, a covenant): in its own live colour, named at
   its end, inside the scale (E53 §5); a value already on the chart is
   never drawn again as a reference line (E53 addendum, 2026-09-09).
2. **Accidental annotation** — an annotation offset from its point
   gets a visible leader to the point, and self-contained wording
   ("Jun '26 print: -3.7% — the one weak month, reversed next print").
3. **Dateless time axis** — time series always get date ticks; the
   x-baseline is a layout constant, never computed through the value
   transform (log charts silently lost their ticks to a
   double-transform).
4. **Fixed layout vs variable data** — measure rendered text,
   distribute space, then degrade gracefully: glyph-squeeze small
   overflows (<~7%), shrink type for big ones; never clip mid-word.
5. **Mid-number wraps** — compact values never break ("7 of / 8");
   wrap whole units instead (a tag chip drops below intact).
6. **Full bars swallow numerals** — near-100% fills carry their
   numeral INSIDE the fill's end.
7. **Ink on ink** — text over data lines gets a translucent backing
   chip sized to the text; measured empty space is better, the chip is
   the net.
8. **Wrong-origin transforms** — skew/rotate about the wrong origin
   displaces by ~tan(angle)×distance; pivot on the element's own
   corner (highlighter sweeps lost 20–50px of their right end to
   this).
9. **Authored vs auto-synced values** — if a build syncs display
   values from data channels, keep authored values off the channels
   the sync owns (a badge's "94%" became a series label).
10. **Shared payloads across showings** — narration-keyed reveal
    timings resolved for a first showing render a re-showing EMPTY. A
    re-showing is a RECAP: short hold = fast fill (sub-12s → rows
    ~0.8s apart, compressed cell offsets); first showings keep the
    slow narration-keyed landing. A re-showing is never a HOLD: a
    chart never survives a plate change and, if the narrative returns
    to it, it re-enters spotlit on the new datum (E25); when the sentence
    needs the same data at another scale, with more of it or in
    another form, the standing page CHANGES STATE on the word and
    never cuts to a second chart of it (E58).

11. **Insider shorthand** - a nickname is not a label ("the yardstick"),
    a citation is not a key ("BEA via FRED"). Every series names what
    it tracks, inline, in audience words; nicknames only alongside
    their descriptor; acronyms glossed in plain words. The audit
    question: could a stranger say what each line IS?

## Standing analyst-grade rules (doc 29 §9.22, as amended by E52/E53)

Bars for discrete buckets in equidistant slots, lines for continuous
phenomena on the time axis, never a stacked bar (E53 §2-3); y-format + units; x-ticks in their own
reserved band; ylabel floats inside the plot top-left (FT style) —
suppressed on paneled charts (panel titles own that corner, unit ticks
carry the units); every series named inline at its terminal point in its own colour,
with its value, in a reserved right gutter - never a legend box
(E52 §2, E53 §8); end labels stay short (~6 chars; the right margin is
120px - §9.22, not withdrawn); where a plot has no gutter the fallback is
the sub, a compromise to be fixed, not a pattern to copy (E53 §8); hline labels right-aligned at
the line's end, alternating above/below when stacked; two units only when they must be read AGAINST
each other, and then an OVERLAY, never separate tiers: the bars keep
the plot, their own zero and every gridline, the line rides over them
on its own scale, owns no axis and carries a terminal tag (E53 §4); source line never collides
with the axis.

**Name the aggregation** (P54 K11). A per-unit figure states its rule
on the page - value-weighted (total USD / total kg across partners) or
a simple mean of rows - because the two part: the HBM-class $/kg read
95,408 value-weighted against 78,173 as a simple mean, 22% apart, with
partner rows running from 225 to 396,075. The spoken figure and the
docked figure come from the same data pull; the ledger's figures moved
several-fold within four days (Steel and Paper, 2026-08-29,
`9cb9df7e5ca0`).

## Validation doctrine

Never trust a detector, effect, or fix not validated against a known
ground-truth case; verify on the final deliverable, not an
intermediate. (Three plausible stutter detectors all failed the one
known-real case; a crossfade "fix" masked an incomplete cut.)
