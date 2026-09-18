/* R26-191 (E99 s75, 2026-09-17) - WHERE THE SPLIT VALUE ROW'S SECOND LINE GOES: INSIDE ITS OWN BAR.

   R26-53 (`f67c5ed`, 2026-09-11) fits a page's whole value row into its slots at ONE size and, when the
   widest label will not fit even at the tick size - the floor, because a value smaller than the page's own
   tick label is not reading matter - it SPLITS the row: "odd bars' values ride one line further out". That
   push is what the weak-prints page cannot afford. Eight bars of six-glyph signed percentages in portrait
   (`ledger:ev-weak-prints-v1:bars:7`, made 2026-09-16) exhaust the fit, and one line further out is, for a
   drop, the MONTH-TICK ROW and, for the one rise, the risen badge's own band - the operator, on the frame:
   *"why are we still colliding ont he charts with labels and axes?"*

   THE RULE (the parent's route 2, BACKLOG R26-191): the second line goes INSIDE its bar WHEN THE BAR CAN
   HOLD IT - the whole box, both ways. The place inside is not a taste: it is the one place furthest from the
   row it was split away from, because the first row's labels all stand BEYOND their tips, so the box sits
   FLUSH on the bar's ZERO-LINE edge, horizontally centred on the bar as it already was. The type's own
   metrics give it its air with no new dial: a box is ASC + DESC of the size and the digits' cap band is
   about 0.72 of it, so a box flush on the baseline edge stands (ASC - 0.72) = 0.20 em of the bar's own fill
   off the zero line at that end. [DERIVED: Arial's cap height 0.716 em, Inter's 0.727 - the page's two
   faces; a signed percentage is digits, a minus and a %, all inside the cap band.]

   BOTH WAYS, and the WIDTH is the one that bites: the weak-prints page's bars are 51.1 units wide and its
   numbers 126.75, so a number written inside one of them is two thirds charcoal ON THE CHARCOAL FIELD -
   nothing at all (rendered and read at 0:44 before this law existed; the frame is the judge, never the
   diff). A bar that cannot hold the box - too short or too narrow - does not get a number at all, and the
   ROW THINS instead (`lfThinRow`): the page keeps the MINIMUM, the MAXIMUM and the LAST bar (the one a
   badge points at), each on its OWN SIGN SIDE where the unsplit path already puts it - under a drop, over a
   rise - and every other bar goes unlabelled, the axis carrying the scale. The first build of this law
   mirrored the label across the zero line instead, and the parent refused the frame: a drop's number stood
   ABOVE the line and the rise's below it, which is E28 backwards (*"a drop is a bar going DOWN from a zero
   baseline"* - sign is geometry, and a label's place is part of that sign). E25 is the other half: a chart
   proves ONE sentence - here "seven of the eight fell", the count and the sign, not eight numbers. A page
   that wants every value labelled at this density must widen the chart or shorten its labels (drop the unit
   into the axis); the engine will not shrink a number under the tick size, and it will not move one to the
   wrong side of the line to make room.

   AND TWO TICK LABELS NEVER TOUCH (`lfTickYear` / `lfTickKeep`): the FIRST tick yields its year suffix -
   "Oct '24" -> "Oct" - when the page already states the range in its sub or its cite (the engine checks;
   a year is never deleted from a page that does not say it elsewhere), and if two still touch the LATER of
   the two yields its label entirely, except that the LAST tick never yields - it closes the range and it is
   the one a badge points at - so its neighbour goes instead. "Touch" is the overlap gate's own hairline
   (2 units), so a row no gate would fault is left exactly as it was.

   Pure: the strings, the sizes and the geometry, never t. The engine calls it once at BUILD, from
   `lpFitValues`, so a cold seek and a warm play answer the same number (R26-28). */

export const LF = Object.freeze({
  MIN_RATIO: 4.5,   /* the contrast a label inside a bar must clear against the bar's own fill. WCAG's own
                       floor for type this large is 3.0; this is the BODY floor, because the number on the
                       bar is the page's argument and it is read at thumbnail scale (E67) */
  CAP: 0.72,        /* [DERIVED: Arial .716 / Inter .727] the digits' cap height as a share of the size -
                       carried here for the air a test measures, never for a place (the box is the place) */
});

const LF_HEX = /^#([0-9a-f]{3}|[0-9a-f]{6})$/i;
const LF_FUN = /^rgba?\(\s*([0-9.]+)[\s,]+([0-9.]+)[\s,]+([0-9.]+)/i;

/* ONE colour as [r, g, b] in 0-255, in every form the DOM hands back (`#abc`, `#aabbcc`, `rgb(r, g, b)`,
   `rgba(r, g, b, a)`, the space-separated modern form), or null for anything else - `none`, a keyword, an
   unresolved `var(--lp-neg)` on a page that is not laid out yet. Null is a REFUSAL, not a default: the
   caller must not write a number inside a bar whose fill it could not measure. */
export const lfRgb = (c) => {
  const s = String(c == null ? "" : c).trim();
  const h = LF_HEX.exec(s);
  if (h) {
    const d = h[1];
    return d.length === 3 ? [0, 1, 2].map((i) => parseInt(d[i] + d[i], 16))
                          : [0, 2, 4].map((i) => parseInt(d.slice(i, i + 2), 16));
  }
  const f = LF_FUN.exec(s);
  if (!f) return null;
  const v = [1, 2, 3].map((i) => Math.max(0, Math.min(255, Math.round(parseFloat(f[i])))));
  return v.some((n) => !Number.isFinite(n)) ? null : v;
};

/* WCAG 2.1 relative luminance of a colour (a string or an [r, g, b]); null when it is not a colour. */
export const lfLum = (c) => {
  const v = Array.isArray(c) ? c : lfRgb(c);
  if (!v) return null;
  const lin = v.map((n) => { const u = n / 255; return u <= 0.03928 ? u / 12.92 : Math.pow((u + 0.055) / 1.055, 2.4); });
  return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2];
};

/* WCAG contrast between two colours, the lighter over the darker; null when either will not parse. */
export const lfContrast = (a, b) => {
  const la = lfLum(a), lb = lfLum(b);
  if (la == null || lb == null) return null;
  return (Math.max(la, lb) + 0.05) / (Math.min(la, lb) + 0.05);
};

/* THE INK THAT READS ON A FILL: the best of the inks offered, or null when none of them clears `min`.
   Ties go to the first ink offered, so the caller's order is the page's preference (the board's charcoal
   before the cream). The inks are the caller's - this module owns no palette. */
export const lfOnInk = (fill, inks, min = LF.MIN_RATIO) => {
  let best = null;
  for (const ink of inks || []) {
    const r = lfContrast(ink, fill);
    if (r == null || r < min) continue;
    if (!best || r > best.ratio) best = { ink, ratio: r };
  }
  return best;
};

/* WHERE A SPLIT ROW'S SECOND LABEL GOES, as the label's own BASELINE y:
     { where: "inside", y }  the box flush on the bar's zero-line edge, inside the bar
     { where: "thin", y: null }  the bar cannot hold it: nothing goes in, and the caller THINS the row
                                 (`lfThinRow`) rather than move a number off its own side of the line
   `base` the zero line, `end` the bar's far end (its tip), `neg` which way the bar hangs, `size` the row's
   fitted size with the page's own `asc` / `desc` (LPVAL.ASC / LPVAL.LAB_DESC - one source, passed in),
   `bw` the bar's width against `labW` the label's measured one; `reads` false when no ink reads on the
   bar's fill, which keeps the number off it however tall it is. A width it was not given is a width it did
   not measure: nothing goes in. */
export const lfSplitRow = (o) => {
  const boxH = (o.asc + o.desc) * o.size, h = Math.abs(o.end - o.base);
  if (h >= boxH && +o.bw >= +o.labW && o.reads !== false) {
    return { where: "inside", y: o.neg ? o.base + o.asc * o.size : o.base - o.desc * o.size, boxH };
  }
  return { where: "thin", y: null, boxH };
};

/* THE ROW THINNED to the labels the page's sentence needs: the MINIMUM, the MAXIMUM and the LAST bar, as
   indices into the row, ascending and deduped. Ties go to the first bar that holds the extreme - a page
   with two equal lows labels the earlier one, which is the one its sentence reached first. Everything else
   goes unlabelled; the axis still prints the scale, and the callout still owns its own bar's number. */
export const lfThinRow = (vals) => {
  const n = (vals || []).length;
  if (!n) return [];
  let lo = 0, hi = 0;
  for (let i = 1; i < n; i++) { if (vals[i] < vals[lo]) lo = i; if (vals[i] > vals[hi]) hi = i; }
  return [...new Set([lo, hi, n - 1])].sort((a, b) => a - b);
};

/* A TICK LABEL'S YEAR SUFFIX - "Oct '24" -> { base: "Oct", year: "'24" }, "Q3 2024" -> { base: "Q3",
   year: "2024" } - or null when it carries none. The caller decides whether the page may lose it. */
const LF_YEAR = /^(.+?)[\s\u00a0]+('\d{2}|\d{4})$/;
export const lfTickYear = (s) => {
  const m = LF_YEAR.exec(String(s == null ? "" : s).trim());
  return m ? { base: m[1].trim(), year: m[2] } : null;
};

/* WHICH TICK LABELS STAY, left to right: a boolean per box ([x, w], in the chart's own units, in axis
   order). Two labels TOUCH when they overlap by more than `hair` - the overlap gate's own hairline, so a
   row no gate would fault is returned untouched. The LATER of a touching pair yields; the LAST tick never
   does (it closes the range and a badge points at it), so its neighbour yields instead. Greedy and left to
   right: every drop removes a touch, so the answer has none. */
export const lfTickKeep = (boxes, hair = 2) => {
  const n = (boxes || []).length, keep = (boxes || []).map(() => true);
  if (n < 2) return keep;
  let prev = 0;
  for (let i = 1; i < n; i++) {
    const gap = boxes[i][0] - (boxes[prev][0] + boxes[prev][1]);
    if (gap >= -hair) { prev = i; continue; }
    if (i === n - 1) { keep[prev] = false; prev = i; }   /* the last tick stays; its neighbour goes */
    else keep[i] = false;                                /* otherwise the later of the two goes */
  }
  return keep;
};
