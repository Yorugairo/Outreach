/* SPACE: page */
/* species/solo.mjs - SOLO, THE ON-WORD ISOLATE (P69 T37; the Bravos harvest v2's rank 2: A12 "peers ghost, one series
   stays lit", 8 of 9 videos, with A49 "one bar ignites, the rest dim"). SOURCE OF TRUTH, inlined into the scene-evidence
   player by sync_kinetics.py between KINETICS:BEGIN solo and KINETICS:END, AFTER ease (it reads minJerk) and beside
   lit_stretch's region, for the reason span.mjs gives: a PAGE species' math is called by the page's PERFORM layer, and
   a const has to exist before the function that closes over it is built.

   WHEN (`SPECIES_WHEN["solo"]`, build_scene_timeline_f.py): the sentence narrows to ONE series ("look at China's",
   "Chipmakers doubling") or names ONE bar in a field ("the third largest") - and on that word every other series or
   bar of the page mutes while the named one keeps its ink. Never when the comparison between them is the claim.

   THE FRAME it was harvested from: JPN 05:23.5 (docs/research/runs/bravos-watch/nB1eXWQlW58/luna-recovery/
   focus-05-treasury-holdings/frames/frame_0008.jpg) - Japan's line bright, China's and the UK's thin and dim, the
   legend row, the axes and the title exactly as they were. So a solo reaches the OTHER marks' own ink and nothing
   else: a line's stroke, its lead point and its end tag; a bar's rect, its range band and its value. The key, the
   axes, a bar's category name, the title stay ("Keep the ghosted legend readable", the use-when guide, P JPN).

   THE DIM is E67's: the muted history of a series is its own hue at 0.45 (the engine's buildLedgerLine; LP_MUTED), and
   P69 T45's member `light` dims a bar's other tiles to the same 0.45. It is one number here, not a second one. The long
   form's spec measured Bravos lower - unlit bars at ~0.38x, context lines at ~0.3 (BRAVOS-LONGFORM-CHART-SPEC.md (c)9)
   - and names moving 0.45 as the operator's call; until that call this dial IS E67's, under every profile.

   THE LAW, a pure function of t:
     the events - every `solo` on the page names ONE key (`s:<series>` or `b:<bar>`); every `unsolo`, and every verb
                  that REPLACES the page after the first solo (a recast, a morph, a remake - the lit stretch's own leave
                  rule), names none. In time order; at one instant a release gives way to a solo.
     the alpha  - a mark's alpha starts at 1 and each event, from its `at`, eases it on min-jerk over its `dur` toward
                  its target: 1 for the named mark (and for every mark on a release), SOLO.DIM for every other mark of
                  the SAME kind (a series solo never dims a bar). Each event starts from where the last one left the
                  mark at its word, so a second solo HANDS OVER - no frame jumps - and an unsolo eases every mark back.
     the write  - onto channels the chart's own paint never writes: a stroke's, a bar's and a band's `opacity`
                  ATTRIBUTE (the chart writes their style, and the soft bars' feet and shadows already read the bar's
                  attribute - lpBarSoftPaint), and `fill-opacity` on the lead point, the end tag and the value (the chart
                  writes their `opacity`). At full ink the attribute is REMOVED, so every frame before the word - and
                  every page with no solo at all - is the page it was, to the byte.
     the light  - a lit stretch (species/lit_stretch.mjs) on a muted series mutes WITH its series: it is painted first
                  in the frame and the solo multiplies what it wrote. A light on the named series keeps its ink. */
import { minJerk } from "../kinetics/ease.mjs";

export const SOLO = Object.freeze({
  DIM: 0.45,     /* E67: the page's own muted alpha - the history's, the member light's (see the header on (c)9) */
  MIN_S: 0.2,    /* the mute's shortest ease: under it the dim is a flicker (build_scene_timeline_f.SOLO_DUR_S) */
  MAX_S: 1.5,    /* ... and its longest: past it the isolate is a fade the word has left behind */
  EPS: 5e-4,     /* an alpha this close to 1 is full ink: the attribute is removed, never written as 1.000 */
});

const solo01 = (v) => Math.min(1, Math.max(0, v));

/* the ONE mark a solo names: a line page's series, or a bars page's bar; null for a release */
export const soloKeyOf = (sp) => (sp && Number.isInteger(sp.bar) ? "b:" + sp.bar
  : sp && Number.isInteger(sp.series) ? "s:" + sp.series : null);

/* THE EVENTS in time order: `solos` name their key, `releases` ({at, dur}: an unsolo, a verb that replaces the page)
   name none; at one instant a release sorts first, so the solo at that instant is the state that stands */
export const soloEvents = (solos, releases) => [
  ...(solos || []).map((sp) => ({ at: +sp.at, dur: Math.max(0.001, +sp.dur || SOLO.MIN_S), key: soloKeyOf(sp) })),
  ...(releases || []).map((r) => ({ at: +r.at, dur: Math.max(0.001, +r.dur || SOLO.MIN_S), key: null })),
].filter((e) => Number.isFinite(e.at)).sort((a, b) => a.at - b.at || (a.key === null ? 0 : 1) - (b.key === null ? 0 : 1));

/* THE ALPHA of the mark `key` at t: each event eases it from where the previous one left it at the event's word */
export const soloAlpha = (evs, key, t, dim = SOLO.DIM) => {
  let a = 1;
  for (let k = 0; k < (evs || []).length; k++) {
    const e = evs[k];
    if (t < e.at) break;
    const nx = evs[k + 1], end = nx && nx.at <= t ? nx.at : t;
    const want = e.key === null || e.key === key || e.key[0] !== String(key)[0] ? 1 : dim;
    const u = solo01((end - e.at) / e.dur);
    a = u >= 1 ? want : a + (want - a) * solo01(minJerk(u));   /* it LANDS exactly (1 + (0.45 - 1) is 0.44999999999999996) */
  }
  return a;
};

/* one alpha onto one element's channel: full ink REMOVES the attribute (the page with no solo, to the byte) */
export const soloWrite = (el, attr, a) => {
  if (!el) return;
  if (a >= 1 - SOLO.EPS) el.removeAttribute(attr);
  else el.setAttribute(attr, Math.max(0, a).toFixed(3));
};

/* THE PAINTER (P69 T37). `sd` is the perform layer's built solo (`evs`, the page's `lits`), `st` the page state - every
   chart state of it is written (a rescale's derived state carries the same series), so a seek into any state is the
   play. It reads nothing from the engine but its arguments; `ctx` is the page species context, unused. */
export const paintSolo = (sd, t, st, ctx) => {
  const states = st && Array.isArray(st.states) && st.states.length ? st.states : [st];
  for (const S of states) {
    for (const pp of (S && S.paths) || []) {
      const a = soloAlpha(sd.evs, "s:" + (pp.si | 0), t);
      soloWrite(pp.p, "opacity", a); soloWrite(pp.tip, "fill-opacity", a); soloWrite(pp.name, "fill-opacity", a);
    }
    ((S && S.bars) || []).forEach((b, i) => {
      const a = soloAlpha(sd.evs, "b:" + (Number.isInteger(b.i) ? b.i : i), t);
      soloWrite(b.bar, "opacity", a); soloWrite(b.band, "opacity", a); soloWrite(b.val, "fill-opacity", a);
    });
  }
  for (const ld of sd.lits || []) {
    const a = soloAlpha(sd.evs, "s:" + (ld.si | 0), t);
    if (a < 1 - SOLO.EPS) ld.g.setAttribute("opacity", ((+ld.g.getAttribute("opacity") || 0) * a).toFixed(3));
  }
};

/* THE MODULE RULE, the page half of it: the last statement registers the painter, a plain guarded assignment. */
if (typeof PAGE_PAINTERS !== "undefined") PAGE_PAINTERS.solo = paintSolo;
