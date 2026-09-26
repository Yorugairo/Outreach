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

   THE DIM was E67's 0.45 until the operator's call the long form's spec named ((c)9): E99 s117 (2), on our solo beside
   Bravos JPN 05:20 / 05:23.5 - Bravos "fades theirs to a higher contrast", so "a SOLO lifts the named line's bloom
   further and fades the others harder and thinner than E67's 0.45, so the contrast between the lit and the muted
   matches Bravos's". Three dials, set from measure_line_bloom.py's read of the Bravos band
   (content/video_engine/assets/bravos-line-bloom.v1.json; the numbers in tests/test_line_bloom.py): DIM, the muted
   marks' alpha; THIN, a muted stroke's width at a full mute; LIFT, the named line's halo radius at a full lift (it eases
   INTO the primary's three layers - the engine's lpSoloBloom - and a muted line's halo eases OUT: "a context or muted
   line never blooms"). E67's HISTORY stays at 0.45 (E99 s78 (2)) - a different mark, and not this dial. P69 T45's
   member `light` keeps its own 0.45 (LPMEMBER.DIM).

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
                  in the frame and the solo multiplies what it wrote. A light on the named series keeps its ink.

   THE LONG FORM'S CHROME (P71 T30; the Bravos harvest v2's S9, "the legend chip turns accent when its series is
   isolated": STK 04:14, BOOM 00:55 / 01:04 / 01:07 / 15:32 / 15:58.5). JPN keeps its legend; STK and BOOM fill the
   named series' legend LABEL with the page's one accent - whatever the series' colour (BOOM 00:56: the teal "Dotcom
   Boom" in crimson) - and leave its dash its colour. So on a LONG-FORM page (the state carries `lfType`) the solo also
   reaches the key and the end badge, on its own clock; a short's page has neither and is left exactly as it was:
     the key pill  - the named series' pill fills with the page's accent at its LIFT (SOLO_ACCENT.FILL, `--lp-acc`: the
                     sunflower callout capsule with charcoal type - P71 T9's axis_tag made the same mapping), laid as an
                     inset box-shadow, a channel the pill's build and the badge ladder never write, removed at rest; its
                     dot keeps its line's colour. Every other pill takes the solo's alpha on its opacity (the ladder
                     rewrites it every frame, before the perform layer runs - the lit stretch's own pattern).
     the end badge - the named line's end tag (its value and its chip) turns the page's accent, its type easing
                     from its series' ink to the accent at the lift; the others mute with their series (fill-opacity,
                     above). A capsule drawn by the tag's own stroke was tried and read as letter-shaped blobs on the
                     frame (the first cut's frame read), and a boxed badge needs a rect the line builder does not
                     draw - so the badge's light is its ink. Its style is stashed on the element at the first lit
                     frame (SOLO_ACCENT.STASH) and handed back to the attribute at rest - so an unsolo, or a seek back
                     before the word, is the page it was. */
import { minJerk } from "../kinetics/ease.mjs";

export const SOLO = Object.freeze({
  DIM: 0.42,     /* E99 s117 (2): the muted marks' alpha - harder than E67's 0.45: lit/muted 5.24 at 1024 px (Bravos 3.39-5.29; 0.30 read 5.9, over it) */
  THIN: 0.45,    /* ... a muted stroke's width at a full mute, as a share of its own - thinner, so the lit line carries the plot */
  LIFT: 1.5,     /* ... the named line's halo radius at a full lift: its share of the plot's contrast at 320 px 0.63 (Bravos 0.57-0.74) */
  MIN_S: 0.2,    /* the mute's shortest ease: under it the dim is a flicker (build_scene_timeline_f.SOLO_DUR_S) */
  MAX_S: 1.5,    /* ... and its longest: past it the isolate is a fade the word has left behind */
  EPS: 5e-4,     /* an alpha this close to 1 is full ink: the attribute is removed, never written as 1.000 */
});

/* P71 T30: the long form's chrome on a solo - the key pill and the end badge take the page's accent */
export const SOLO_ACCENT = Object.freeze({
  FILL: "var(--lp-acc)",   /* the page's one accent (#F5B72E, the template's callout capsule `rect.cpill`); the pill's name keeps its charcoal KEY_INK */
  STASH: "data-solo-style",   /* an end badge's own style attribute, kept while it is lit ("" = it had none) */
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

/* THE LEVEL of the mark `key` at t: from `start`, each event eases it from where the previous one left it at the event's
   word toward its target - `named` for the mark it names, `other` for every other mark of the same kind, `release` on a
   release (and for a mark of the other kind, which a solo never touches) */
export const soloLevel = (evs, key, t, { start, named, other, release }) => {
  let a = start;
  for (let k = 0; k < (evs || []).length; k++) {
    const e = evs[k];
    if (t < e.at) break;
    const nx = evs[k + 1], end = nx && nx.at <= t ? nx.at : t;
    const want = e.key === null || e.key[0] !== String(key)[0] ? release : e.key === key ? named : other;
    const u = solo01((end - e.at) / e.dur);
    a = u >= 1 ? want : a + (want - a) * solo01(minJerk(u));   /* it LANDS exactly (1 + (0.45 - 1) is 0.44999999999999996) */
  }
  return a;
};

/* THE ALPHA of the mark `key` at t: 1, SOLO.DIM for the others on a solo, 1 again on a release */
export const soloAlpha = (evs, key, t, dim = SOLO.DIM) => soloLevel(evs, key, t, { start: 1, named: 1, other: dim, release: 1 });

/* THE LIFT of the mark `key` at t (E99 s117 (2)): 0, then 1 for the named line while its solo stands, 0 on a release */
export const soloLift = (evs, key, t) => soloLevel(evs, key, t, { start: 0, named: 1, other: 0, release: 0 });

/* one alpha onto one element's channel: full ink REMOVES the attribute (the page with no solo, to the byte) */
export const soloWrite = (el, attr, a) => {
  if (!el) return;
  if (a >= 1 - SOLO.EPS) el.removeAttribute(attr);
  else el.setAttribute(attr, Math.max(0, a).toFixed(3));
};

/* P71 T30: one colour at a share `u` of its full ink - the colour itself at full (so a landed light is the accent's own) */
export const soloMix = (col, u) => (u >= 1 - SOLO.EPS ? col : "color-mix(in srgb, " + col + " " + (100 * solo01(u)).toFixed(1) + "%, transparent)");

/* ... one element's STYLE lit by `props` ([property, value] pairs), or handed back at rest (`props` null): the first lit
   write stashes the attribute on the element, the rest restores it to the byte - a pure function of t over the DOM */
export const soloStyle = (el, props) => {
  if (!el || !el.style) return;
  const had = el.getAttribute(SOLO_ACCENT.STASH);
  if (!props) {
    if (had === null) return;
    if (had === "") el.removeAttribute("style"); else el.setAttribute("style", had);
    el.removeAttribute(SOLO_ACCENT.STASH);
    return;
  }
  if (had === null) el.setAttribute(SOLO_ACCENT.STASH, el.getAttribute("style") || "");
  for (const [k, v] of props) el.style.setProperty(k, v);
};

/* ... the END BADGE at lift `u`: its words (the value and its chip's) ease from their series' ink to the accent */
export const soloBadge = (pp, u) => {
  const nm = pp && pp.name, chip = nm && nm.querySelector ? nm.querySelector("tspan.tagchip") : null;
  if (!nm) return;
  if (u <= SOLO.EPS) { soloStyle(nm, null); soloStyle(chip, null); return; }
  const ink = (own) => (u >= 1 - SOLO.EPS ? SOLO_ACCENT.FILL
    : "color-mix(in srgb, " + SOLO_ACCENT.FILL + " " + (100 * u).toFixed(1) + "%, " + (own || "currentColor") + ")");
  soloStyle(nm, [["fill", ink(nm.getAttribute("fill"))]]);
  soloStyle(chip, [["fill", ink(chip && chip.getAttribute("fill"))]]);
};

/* ... a KEY PILL at alpha `a` and lift `u`: the others fade with their series, the named one fills with the accent */
export const soloKey = (kp, a, u) => {
  if (!kp || !kp.el || !kp.el.style) return;
  if (a < 1 - SOLO.EPS) kp.el.style.opacity = ((+kp.el.style.opacity || 0) * a).toFixed(3);
  if (u > SOLO.EPS) kp.el.style.setProperty("box-shadow", "inset 0 0 0 999px " + soloMix(SOLO_ACCENT.FILL, u));
  else kp.el.style.removeProperty("box-shadow");
};

/* THE PAINTER (P69 T37). `sd` is the perform layer's built solo (`evs`, the page's `lits`), `st` the page state - every
   chart state of it is written (a rescale's derived state carries the same series), so a seek into any state is the
   play. It reads nothing from the engine but its arguments; `ctx` is the page species context - its `bloom` and `thin`
   (P69 T37b) are the two engine writers a solo drives. */
export const paintSolo = (sd, t, st, ctx) => {
  const states = st && Array.isArray(st.states) && st.states.length ? st.states : [st];
  for (const S of states) {
    const lf = !!(S && S.lfType);   /* P71 T30: a long-form page's chrome follows the solo too */
    for (const pp of (S && S.paths) || []) {
      const key = "s:" + (pp.si | 0), a = soloAlpha(sd.evs, key, t), m = solo01((1 - a) / (1 - SOLO.DIM)), lift = soloLift(sd.evs, key, t);
      soloWrite(pp.p, "opacity", a); soloWrite(pp.tip, "fill-opacity", a); soloWrite(pp.name, "fill-opacity", a);
      /* E99 s117 (2): the named line's bloom lifts, a muted one's halo leaves and its stroke thins - the engine's DOM
         work, handed in through the page context (absent, a bare test, the alpha above is the whole solo) */
      if (ctx && ctx.bloom) ctx.bloom(S, pp, lift, m, SOLO.LIFT);
      if (ctx && ctx.thin) ctx.thin(S, pp, m, SOLO.THIN);
      if (lf) soloBadge(pp, lift);
    }
    if (lf) for (const kp of (S && S.keyPills) || []) {
      if (kp.panel != null) continue;   /* a panels page's key follows its panel focus (lpPaintPanelKey), not a series solo */
      const key = "s:" + (kp.series | 0);
      soloKey(kp, soloAlpha(sd.evs, key, t), soloLift(sd.evs, key, t));
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
