# CHART DISCIPLINE — portable

Model-agnostic, renderer-agnostic. A fresh agent with only this repo
must be able to QC and build production charts from this page.
Template-enforced reference implementation:
`docs/content-video-engine/samples/scene-evidence-player.template.html`
(+ doc 29 §9.22–9.23). Extracted 2026-08-30, Steel and Paper QC.

## The acceptance gate (operator ruling)

**"The charts need to fully communicate their own story without
narration."** Mute the audio, screenshot the chart, hand it to a
stranger. If any ink needs the voiceover to explain it, the chart is
not done.

## The ten failure classes (each shipped past a linter once)

1. **Anonymous reference line** — every series is named, dashed
   averages/trends/benchmarks included; a late-fading series' label
   fades in WITH it.
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
    slow narration-keyed landing.

## Standing analyst-grade rules (doc 29 §9.22)

Lines not bar-trios for series; y-format + units; x-ticks in their own
reserved band; ylabel floats inside the plot top-left (FT style) —
suppressed on paneled charts (panel titles own that corner, unit ticks
carry the units); end labels ≤~6 chars; hline labels right-aligned at
the line's end, alternating above/below when stacked; combo convention
= event-bar histogram under a price line; source line never collides
with the axis.

## Validation doctrine

Never trust a detector, effect, or fix not validated against a known
ground-truth case; verify on the final deliverable, not an
intermediate. (Three plausible stutter detectors all failed the one
known-real case; a crossfade "fix" masked an incomplete cut.)

11. **Insider shorthand** - a nickname is not a label ("the yardstick"),
    a citation is not a key ("BEA via FRED"). Every series names what
    it tracks, inline, in audience words; nicknames only alongside
    their descriptor; acronyms glossed in plain words. The audit
    question: could a stranger say what each line IS?
