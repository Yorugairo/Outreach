/* species/spiral.mjs - THE PAGE VORTEX (P57 T22 / R26-101; doc 29 s9.31 "The page VORTEX - how a page leaves,
   and how it returns"; CAPABILITIES.md "The page VORTEX"). SOURCE OF TRUTH, inlined into the scene-evidence
   player by sync_kinetics.py between KINETICS:BEGIN spiral and KINETICS:END, AFTER squash - the one thing it
   imports is that module's `scaleBy`, which is the engine's own.

   NEITHER a species kind NOR a dock payload: a PAGE TRANSITION. So it registers no painter and declares no
   SPACE - it follows verdict.mjs's and record.mjs's precedent, where the engine's own slot calls the painter BY
   NAME (`lpSpiral(st, scene, t, pg)`, the last act of paintLedger's frame). Promoted from inline engine code
   with every golden byte-identical (`spiral-return`, `spiral-return@proof-retract`, `spiral-return@proof-fade`):
   each literal below is the value the inline code carried, to the digit, and no expression was re-associated.

   THE GROUPING DECISION (R26-101 proposed one module for both directions; this module makes it): ONE module
   holds the page's spiral IN and the vortex RETRACT, and both cards - `page_enter:spiral` and
   `page_exit:retract` - point at this file. Not because the two resemble each other, but because on disk they
   are not two things at all: `lpSpiral` is ONE function with ONE map (`lpVortex`) driven by ONE pair of clocks
   (`spiralClocks`), and the only difference between leaving and coming back is which clock wins the Math.max on
   uc and uf. Splitting the file would mean copying the map, the particles and the painter into both halves and
   keeping them in step by hand - the exact drift sync_kinetics.py exists to refuse.

   WHEN (CAPABILITIES.md "The page VORTEX", verbatim): "the page's argument is over and the next thing is a
   different page or a plate - it leaves by the vortex; the same data in another form is E58's verb, never a
   vortex".

   THE LAW - RETRACT AS A VORTEX (operator, 2026-09-05: "a true spiral of everything getting sucked back into
   the cream as if a vortex / whirlpool"; "a way tighter vortex, almost celestial" - three turns, the core
   spinning four times the rim): every colour on the page is a PARTICLE - each ink glyph, each bar, value, tick
   and label, each pill, each point of the series line - with a home position and a distance r from the drain
   (the board centre). The map is analytic in u (FINDING-the-animation-math s3: a seek renderer may only use
   closed forms):
     the drain takes the centre first     ui  = clamp((u - LAG*rn) / (1 - LAG)),  rn = r / Rmax
     the radius falls slowly, then fast   r'  = r * (1 - ui^R_FALL)
     differential rotation (the whirl)    th  = TURNS * 2pi * ui * (CORE_BASE + CORE_GAIN * (1 - rn)^CORE_FALL)
     stretch along the flow, area kept    diag(1+a, 1/(1+a)) about the tangent (s4), a = ALPHA * 4ui(1-ui)
     the particle shrinks                 s   = (1 - ui)^SHRINK
   The series line is re-drawn from its mapped points, so it curls into the drain like a noodle. Phase two: the
   crisp charcoal fades and the STAINS it settled over are sucked down the same drain. A page declared
   enter:"spiral" ARRIVES by the same map run backwards (E25: a returning chart is not drawn like new);
   exit:"cut" skips the retract (a punch that must land on the last line, E40 #5: no species over a spiral out).
   Idle frames touch nothing - the early-out reads no layout, because reading it re-snaps text a sub-pixel on the
   punched page and every golden would move. The dials are the operator's and ours (42 s42.5), not findings. */
import { scaleBy } from "../kinetics/squash.mjs";

export const LP_RETRACT = Object.freeze({
  COLOURS: 1.0,       /* phase one, in seconds: the colours down the drain at the scene's end */
  CHARCOAL: 1.0,      /* phase two: the crisp charcoal fades to the stains, and the stains follow them down */
  IN: 1.6,            /* the RETURN: the same map run backwards over this long at the scene's start */
  TURNS: 3.0,         /* how many turns the rim makes - "a way tighter vortex, almost celestial" (operator) */
  LAG: 0.25,          /* the drain takes the centre first: a particle at the rim waits this share of u */
  ALPHA: 0.85,        /* the area-preserving stretch along the flow, at its peak (u = 0.5) */
  RECT_FADE: 0.3,     /* phase two: the share of uf the charcoal's own fade takes */
  R_FALL: 1.7,        /* the radius falls slowly then fast: r * (1 - ui^this) [the engine's `Math.pow(ui, 1.7)`] */
  CORE_BASE: 0.4,     /* the rim's share of the whirl ... */
  CORE_GAIN: 1.6,     /* ... and what the core adds on top of it (the core spins ~4x the rim: spiral arms, not a wheel) */
  CORE_FALL: 1.5,     /* how sharply that gain falls off with the normalised radius: (1 - rn)^this */
  SHRINK: 0.7,        /* the particle shrinks as (1 - ui)^this */
  IN_FIELD: 0.55,     /* the RETURN's phases: the stains surface over the first this much of the return ... */
  IN_COLOUR_AT: 0.4,  /* ... and the colours unwind from here ... */
  IN_COLOUR_S: 0.6,   /* ... over this much of it [the engine's `(ui - 0.4) / 0.6`] */
  LINE_W: 8,          /* the series line thins as it curls in: this many px at rest ... */
  LINE_RATE: 1.15,    /* ... reaching nothing at uc = 1/this ... */
  LINE_FALL: 0.7,     /* ... on this power ... */
  LINE_MIN: 0.5,      /* ... over a floor of this many px, so the noodle never vanishes before its home does */
});

/* the engine's clamp01, verbatim - so the module stands alone under `node --test` */
const sp01 = (v) => Math.min(1, Math.max(0, v));

/* THE TWO CLOCKS, and the whole of the grouping decision in six lines: how far the colours (uc) and the field
   (uf) are down the drain at t. The RETRACT runs off the scene's END (its last COLOURS + CHARCOAL, skipped by
   exit "cut"); the RETURN runs off its START, backwards, and wins by Math.max - the field surfaces first, the
   colours follow. A page that does both in one scene is a page that leaves the way it came. */
export const spiralClocks = (t, a, z, exit, enter, R = LP_RETRACT) => {
  let uc = 0, uf = 0;
  const to = t - (z - R.COLOURS - R.CHARCOAL);
  if (exit !== "cut" && to > 0) { uc = sp01(to / R.COLOURS); uf = sp01((to - R.COLOURS) / R.CHARCOAL); }
  if (enter === "spiral") {   /* the field surfaces first, the colours follow */
    const ui = sp01((t - a) / R.IN);
    uf = Math.max(uf, 1 - sp01(ui / R.IN_FIELD)); uc = Math.max(uc, 1 - sp01((ui - R.IN_COLOUR_AT) / R.IN_COLOUR_S));   /* the stains surface over the first 0.9 s, the colours unwind over the last 1 s */
  }
  return { uc, uf };
};

/* THE MAP: one particle's home (x, y) to where it stands at u, about the drain c with the space's own Rmax.
   Pure, closed-form and the only geometry in the file - both directions are this function under two clocks. */
export const lpVortex = (x, y, c, Rmax, u) => {
  const dx = x - c.x, dy = y - c.y, r = Math.hypot(dx, dy) || 1e-6, phi = Math.atan2(dy, dx), rn = Math.min(1, r / Rmax);
  const ui = sp01((u - LP_RETRACT.LAG * rn) / (1 - LP_RETRACT.LAG));
  const rr = r * (1 - Math.pow(ui, LP_RETRACT.R_FALL)), th = LP_RETRACT.TURNS * 2 * Math.PI * ui * (LP_RETRACT.CORE_BASE + LP_RETRACT.CORE_GAIN * Math.pow(1 - rn, LP_RETRACT.CORE_FALL));   /* the core spins ~4x the rim: spiral arms, not a wheel */
  const a = LP_RETRACT.ALPHA * 4 * ui * (1 - ui), s = Math.pow(1 - ui, LP_RETRACT.SHRINK);
  const ang = phi + th;
  const q = scaleBy(s, a);   /* the area-preserving stretch along the tangent (42 s42.3 helper, P43 T4) */
  return { x: c.x + rr * Math.cos(ang), y: c.y + rr * Math.sin(ang), th: th * 180 / Math.PI, tan: ang * 180 / Math.PI + 90, sx: q.sx, sy: q.sy, ui };
};
/* a CSS transform (HTML particle, its own centre as origin) and an SVG one (user units) for the same map */
export const lpVortexCss = (v, hx, hy) => "translate(" + (v.x - hx).toFixed(2) + "px," + (v.y - hy).toFixed(2) + "px) rotate(" + v.tan.toFixed(2) + "deg) scale(" + v.sx.toFixed(4) + "," + v.sy.toFixed(4) + ") rotate(" + (v.th - v.tan).toFixed(2) + "deg)";
export const lpVortexSvg = (v, hx, hy) => "translate(" + v.x.toFixed(2) + " " + v.y.toFixed(2) + ") rotate(" + v.tan.toFixed(2) + ") scale(" + v.sx.toFixed(4) + " " + v.sy.toFixed(4) + ") rotate(" + (v.th - v.tan).toFixed(2) + ") translate(" + (-hx).toFixed(2) + " " + (-hy).toFixed(2) + ")";
export const lpHome = (page, el) => {   /* an element's untransformed centre in page px (SVG has no offsetLeft) */
  const pr = page.getBoundingClientRect(), r = el.getBoundingClientRect();
  if (!pr.width || !pr.height) return { x: 0, y: 0 };
  return { x: (r.left - pr.left + r.width / 2) / pr.width * page.offsetWidth, y: (r.top - pr.top + r.height / 2) / pr.height * page.offsetHeight };
};
/* the particles, measured once at build (untransformed): page-px ones (glyphs, pills), chart ones (viewBox units),
   and the drain in each space - the chart's meet mapping and the field's stretch mapping are inverted from the page */
/* P48 (operator, 2026-09-10: "the swirl should take the whole drawn chart with it; the swirl leads to a clean plate"): the
   vortex drains the ACTIVE chart state - after a rescale or an extend that is the derived state, not the page's own - while
   the glyphs and pills it drains are the page's (shared by every state). Particles are cached per state. */
export const lpParticles = (st, page, S) => {
  S = S || st;
  const glyphs = [...st.glyphs, ...(st.rtGlyphs || [])].map((g) => ({ el: g, ...lpHome(page, g) }));   /* P47 T2: a retitle's glyphs ride the vortex too */
  const pills = [...(st.badges || []), ...(st.keyPills || []), ...(S !== st ? S.keyPills || [] : [])]   /* P69 T10: and the key rail's (M1: the active state's too) */
    .map((b) => ({ el: b.el, ...lpHome(page, b.el) }));
  const skip = new Set([...S.paths.map((p) => p.p), ...S.paths.map((p) => p.tip)]);
  const svg = [...S.chart.children].filter((e) => !skip.has(e) && e.tagName !== "defs").map((e) => {
    let b; try { b = e.getBBox(); } catch (x) { b = { x: 0, y: 0, width: 0, height: 0 }; }
    return { el: e, x: b.x + b.width / 2, y: b.y + b.height / 2 };
  });
  const c = { x: page.offsetWidth * st.boardCentre.x / 100, y: page.offsetHeight * st.boardCentre.y / 100 };
  const pr = page.getBoundingClientRect(), cr = S.chart.getBoundingClientRect(), vb = S.chart.viewBox.baseVal;
  const cw = cr.width / pr.width * page.offsetWidth, ch = cr.height / pr.height * page.offsetHeight;
  const cx0 = (cr.left - pr.left) / pr.width * page.offsetWidth, cy0 = (cr.top - pr.top) / pr.height * page.offsetHeight;
  const k = Math.min(cw / (vb.width || 1), ch / (vb.height || 1)) || 1;   /* xMidYMid meet */
  const cChart = { x: (c.x - cx0 - (cw - vb.width * k) / 2) / k, y: (c.y - cy0 - (ch - vb.height * k) / 2) / k };
  const fr = st.field.getBoundingClientRect(), fsvg = st.field.querySelector("svg"), fvb = fsvg ? fsvg.viewBox.baseVal : { width: 1690, height: 907 };
  const cField = { x: (c.x - (fr.left - pr.left) / pr.width * page.offsetWidth) / (fr.width / pr.width * page.offsetWidth || 1) * fvb.width,
                   y: (c.y - (fr.top - pr.top) / pr.height * page.offsetHeight) / (fr.height / pr.height * page.offsetHeight || 1) * fvb.height };
  const Rpage = Math.hypot(page.offsetWidth, page.offsetHeight) / 2;
  return { glyphs, pills, svg, c, cChart, cField, Rpage, Rchart: Rpage / k, Rfield: Math.hypot(fvb.width, fvb.height) / 2 };
};
/* THE NOODLE'S WIDTH at uc, as the style string the painter sets (the "px" is the painter's): the series line
   thins from LINE_W to LINE_MIN as it curls into the drain, reaching the floor at uc = 1 / LINE_RATE. */
export const spiralLineWidth = (uc, R = LP_RETRACT) =>
  (R.LINE_W * Math.pow(1 - Math.min(1, uc * R.LINE_RATE), R.LINE_FALL) + R.LINE_MIN).toFixed(2);

/* THE PAINTER, called by name from the engine's ledger slot (no registry - verdict.mjs's precedent). */
export const lpSpiral = (st, scene, t, pg) => {
  const a = scene.span ? scene.span[0] : 0, z = scene.span ? scene.span[1] : Infinity;
  const { uc, uf } = spiralClocks(t, a, z, pg.exit, pg.enter);   /* how far the colours, the field, are down the drain */
  const on = uc > 0 || uf > 0;
  const S = (st.states && st.states[st.active | 0]) || st;   /* the chart the drain takes: the active state's */
  if (!on && !S.spiralOn) return;   /* idle: touch no style, read no layout (either re-snaps text a sub-pixel on the punched page) */
  S.spiralOn = on;
  if (!S.parts) S.parts = lpParticles(st, st.page, S);
  const P = S.parts;
  for (const g of P.glyphs) g.el.style.transform = uc > 0 ? lpVortexCss(lpVortex(g.x, g.y, P.c, P.Rpage, uc), g.x, g.y) + " rotate(var(--tilt))" : "";
  for (const p of P.pills) if (uc > 0) p.el.style.transform = lpVortexCss(lpVortex(p.x, p.y, P.c, P.Rpage, uc), p.x, p.y);
  for (const q of P.svg) {
    if (uc > 0) { const v = lpVortex(q.x, q.y, P.cChart, P.Rchart, uc); q.el.style.transformOrigin = ""; q.el.style.transform = ""; q.el.setAttribute("transform", lpVortexSvg(v, q.x, q.y)); }
    else q.el.removeAttribute("transform");
  }
  /* the series line curls in point by point; the tips hide */
  S.paths.forEach((pp, i) => {
    const pts = (S.linePts || [])[i];
    if (!pts) return;
    if (uc > 0) {
      const d = pts.map(([x, y], k) => { const v = lpVortex(x, y, P.cChart, P.Rchart, uc); return (k ? "L" : "M") + v.x.toFixed(1) + " " + v.y.toFixed(1); }).join(" ");
      pp.p.setAttribute("d", d); pp.p.setAttribute("stroke-dashoffset", 0); pp.p.style.strokeWidth = spiralLineWidth(uc) + "px"; pp.tip.style.display = "none";
    } else { pp.p.setAttribute("d", pts.map(([x, y], k) => (k ? "L" : "M") + x.toFixed(1) + " " + y.toFixed(1)).join(" ")); pp.p.style.strokeWidth = ""; pp.tip.style.display = ""; }
  });
  /* phase two: the crisp charcoal fades to the stains beneath, and the stains go down the drain */
  st.rect.style.opacity = uf > 0 ? (1 - sp01(uf / LP_RETRACT.RECT_FADE)).toFixed(3) : "";
  if (st.fieldPlate) st.fieldPlate.style.opacity = uf > 0 ? (1 - sp01(uf / LP_RETRACT.RECT_FADE)).toFixed(3) : st.fieldPlate.style.opacity;
  for (const bl of st.blobs) {
    if (uf > 0) { const v = lpVortex(bl.cx, bl.cy, P.cField, P.Rfield, uf); bl.c.setAttribute("transform", "translate(" + v.x.toFixed(1) + " " + v.y.toFixed(1) + ") rotate(" + v.th.toFixed(1) + ") scale(" + (bl.R * v.sx).toFixed(2) + " " + (bl.R * v.sy).toFixed(2) + ")"); }
    /* else: the soak beat has already painted the blob's home transform this frame */
  }
  for (const sk of st.strokes || []) sk.p.style.opacity = uf > 0 ? (1 - uf).toFixed(3) : "";
};
