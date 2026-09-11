/* species/tiers.mjs - N-TIER PAGES (P50 T9; BACKLOG R26-24; Bravos shots 35-36's two-panel SPR).
   SOURCE OF TRUTH, inlined into the scene-evidence player by sync_kinetics.py between
   KINETICS:BEGIN tiers and KINETICS:END, AFTER ease (it uses minJerk). Its region sits with the
   kinetics laws rather than in the species block at the foot of the file, for the reason span.mjs
   gives: a PAGE's math is called by builders and by the perform layer, both written hundreds of
   lines above the species block, and a const has to exist before the function that closes over it.

   WHEN: the sentence compares the SAME quantity across two, three or four subjects over the same
   period - Japan's reserve and America's, one unit, one decade. That is a small multiple: N bands
   stacked, each with its own y-scale and its own honest zero (E53 s4), sharing ONE x. It is NOT the
   overlay: when two series must be read AGAINST each other, E53 s4 says they belong on one plot with
   the bars keeping the zero and the line riding over them (`tiers: true` on a combo page, the
   macro-chart intake's Archetype 1). Separating those would throw away the comparison. Separate
   bands are for the comparison that is made by SHAPE, band against band, on a shared time axis.

   THE LAW, all of it a pure function of the page's geometry and the build fraction c:
     bands   - the plot is cut into N equal bands with a gutter of GAP of a band's height between
               them. The MIRROR of ledger_page.tier_bands (python, the compiler's dock placement):
               one law in two languages, the same two dials, pinned on both sides.
     domain  - each band's own y-scale, from an HONEST ZERO by default: a band whose zero is dropped
               exaggerates its own shape, and a page of small multiples is read shape against shape.
               A band may opt out (`from_zero: false` in its axes) and the page's judge row says so.
     ticks   - TICKS gridlines a band, and the unit written once per band beside its own top tick:
               a band is a chart, and a chart with no unit is a number with no meaning.
     draw    - the bands draw IN TURN: band i starts at its own share of the build clock, and a
               `build_to` per tier (a tier IS a series index on this page) puts each band on its own
               WORD instead. The drop of one band is measured by the bracket in its `form: "bar"`.
   The dials are ours to tune (42 s42.5), not findings. */
import { minJerk } from "../kinetics/ease.mjs";

export const TIERS = Object.freeze({
  GAP: 0.20,        /* the gutter between two bands, as a share of a band's own height - ledger_page.TIER_GAP is the same number in python [DERIVED, read off the first frame: at 0.10 a band's name sat on the floor tick label of the band above] */
  PAD: 0.08,        /* headroom over a band's tallest value, as a share of its own span: a line that touches its band's ceiling reads as clipped */
  TICKS: 2,         /* gridlines a band (the combo's tiered case uses 2-3 for the same reason: a short band wants fewer ticks) */
  NAME_DY: 6,       /* the band's NAME sits this far above the band's top edge, in the chart's viewBox units - inside the gutter, clear of the band above's floor label */
  STAGGER: 0.34,    /* the share of the build clock between one band's start and the next one's */
  MIN_H: 46,        /* a band shorter than this in viewBox units cannot carry a scale and a name; the compiler's ceiling of 4 is what keeps it from happening */
});

const tier01 = (v) => Math.min(1, Math.max(0, v));

/* THE BANDS: N boxes between `top` and `bot`, top to bottom, each {y0, y1, h}. */
export const tierBands = (top, bot, n, gap = TIERS.GAP) => {
  const k = Math.max(0, n | 0);
  if (!k) return [];
  const h = (bot - top) / (k + (k - 1) * gap);
  return Array.from({ length: k }, (_, i) => {
    const y0 = top + i * h * (1 + gap);
    return { y0, y1: y0 + h, h };
  });
};

/* THE DOMAIN of one band: its own values, with the zero kept honest unless the band drops it. The
   pad is one-sided on a from-zero band (the floor IS the claim) and two-sided when it is not. */
export const tierDomain = (vals, fromZero = true) => {
  /* a null or empty datum is NOT a zero (Number(null) is 0, which would put a floor under a band that has none) */
  const nums = (vals || []).filter((v) => v !== null && v !== undefined && v !== "" && Number.isFinite(+v)).map(Number);
  if (!nums.length) return [0, 1];
  let lo = Math.min(...nums), hi = Math.max(...nums);
  if (fromZero) { lo = Math.min(0, lo); hi = Math.max(0, hi); }
  const span = hi - lo || Math.abs(hi) || 1;
  hi += span * TIERS.PAD;
  if (!fromZero) lo -= span * TIERS.PAD;
  return [lo, hi];
};

/* a value's y inside its band */
export const tierY = (band, lo, hi, v) => band.y1 - (Number(v) - lo) / ((hi - lo) || 1) * band.h;

/* the nice gridline values of a band: TICKS of them inside the domain, the zero always among them
   when the domain holds it (an honest zero that is not drawn is not read) */
export const tierTicks = (lo, hi, n = TIERS.TICKS) => {
  const raw = (hi - lo) / Math.max(1, n);
  const e = Math.pow(10, Math.floor(Math.log10(Math.max(1e-12, raw)))), f = raw / e;
  const step = e * (f <= 1 ? 1 : f <= 2 ? 2 : f <= 5 ? 5 : 10);
  const out = [];
  for (let v = Math.ceil(lo / step - 1e-9) * step; v <= hi + 1e-9; v += step) out.push(Math.abs(v) < step * 1e-6 ? 0 : v);
  return out;
};

/* THE BUILD: band i starts at i * STAGGER of the clock and draws over what is left of it, so the
   bands arrive in turn even before a word is put on them. A `build_to` per tier overrides this by
   capping the band's own stroke - the caps machinery is the page's, not ours. */
export const tierStagger = (i, n) => (n <= 1 ? 0 : Math.min(0.9, (i | 0) * TIERS.STAGGER));
export const tierBuildK = (c, i, n) => minJerk(tier01((c - tierStagger(i, n)) / Math.max(0.05, 1 - tierStagger(n - 1, n))));
