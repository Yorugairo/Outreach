/* SPACE: stage */
/* species/freeze.mjs - THE FREEZE BEAT (P69 T49; E99 s99). SOURCE OF TRUTH, inlined into the scene-evidence player by
   sync_kinetics.py between KINETICS:BEGIN freeze and KINETICS:END, AFTER ease and lit_stretch (it reads minJerk and the
   lit stretch's look) and after the engine's SPECIES_PAINTERS declaration, which the registration reaches.

   THE RULING. E99 s99 (the operator, 2026-09-23): "Light can become motion when it's highlighting and moving along a
   length, blinking, or when it actually stops motion when the light comes on I think. Bravos does this well." - "a light
   that comes on as everything else STOPS is a punctuation beat - the freeze is the event". A light that simply sits on
   a thing stays an annotation (s91), and a light is never the move when a named thing should ARRIVE (s71): this one is
   neither, because what it does is STOP the frame round it.

   WHEN (`SPECIES_WHEN["freeze"]`, build_scene_timeline_f.py): the TURN of the argument lands on ONE number or thing -
   the line the whole row builds to - and the stage stops on it.

   NOT `beat_freeze` (doc 29 s9.27). That is a BOUNDARY move: the chart's final state freezes as a hit, then a
   directional-stretch cut into the next plate. This beat is inside a scene, and life comes back.

   THE LAW, a pure function of t:
     the windows - every `freeze` species on every scene, [at, at + dur] clipped to its scene's span, sorted and merged,
                   read ONCE when the player mounts (freezeWindows). The engine's LIFE CLOCK is t with the frozen time
                   before t taken out (lifeClock): inside a window it stands still, outside it runs at speed, and it
                   never jumps - after the beat every idle carries on from exactly where it stopped, one beat behind t.
                   A thing whose life is counted from an ORIGIN (the Ken Burns push from its scene's start, a clip from
                   its mount) takes the scene clock (sceneClock), which counts only the beats after that origin, so a
                   scene after a beat starts its push at its own start. With no window the clock IS t, the same number,
                   so a build without a freeze paints the string it always painted.
     what stops  - the engine hands the life clock to every LIFE on the stage, by name: the idle of every class (the
                   page, the pills, the docks, the caption strip - idleCssFor), a stage species' own idle (ctx.idle:
                   the ring's breath, a held light's, a chip's, the agenda's rows), the plate's idle and drift, the
                   Ken Burns push, the vector map's world idle, the live page's spark and glow (R26-228), the caption
                   boil, the steam, and an ambient clip (a clip world, an alive plane, a video dock). What it does NOT
                   stop is an authored EVENT: the voice goes on, so the caption's words keep arriving, and the compiler
                   refuses any other species that fires inside the beat (`one light`).
     the light   - ONE light at the resolved target, in the page's one light colour (the relight's sunflower). It comes
                   ON over ON_S (min-jerk, at most RAMP_MAX of the beat), HOLDS perfectly still through the middle - it
                   is part of the stopped frame, so it does not breathe - and goes over OFF_S as life resumes, gone at
                   the beat's end. A target that resolves to a POINT (a datum on a line) is a lit point: the lit
                   stretch's comet head standing still (LIT's halo over its head, lpBloom's form). A target that
                   resolves to a BOX (a bar, a prop's or a mark's region) is a lit EDGE round it - never a fill over the
                   thing it names.
   The dials are ours to tune (42 s42.5), not findings. */
import { minJerk } from "../kinetics/ease.mjs";
import { LIT } from "./lit_stretch.mjs";

export const FREEZE = Object.freeze({
  MIN_S: 0.4,        /* the beat's dial: shorter reads as a dropped frame ... */
  MAX_S: 1.2,        /* ... longer, as the still frame E49 refuses */
  ON_S: 0.12,        /* the light comes ON - quick, a switch, never a slow fade */
  OFF_S: 0.18,       /* ... and goes as life resumes */
  RAMP_MAX: 0.25,    /* each ramp is at most this share of the beat, so the shortest beat still holds a middle */
  CORE_PX: 18,       /* the lit point's radius, stage px - read on the golden: at 12 it was the lead spark turned yellow, not a light coming on */
  PAD: 10,           /* the lit edge's air round a box, stage px */
  EDGE_PX: 4,        /* the lit edge's width, stage px */
  EDGE_RX: 10,       /* ... and its corner */
  POINT_PX: 6,       /* a resolved box smaller than this both ways is a POINT */
  COLOR: "#F5B72E",  /* the relight's sunflower - the engine's PS.RELIGHT_COL, mirrored (a module imports nothing of the engine's) */
});

const fz01 = (v) => Math.min(1, Math.max(0, v));
const fzNum = (v) => typeof v === "number" && Number.isFinite(v);

/* THE WINDOWS: [[a, b], ...] from the timeline's scenes - clipped to the scene, sorted, overlaps merged. Frozen. */
export const freezeWindows = (scenes) => {
  const ws = [];
  for (const sc of scenes || []) {
    const span = (sc && sc.span) || [];
    for (const sp of (sc && sc.species) || []) {
      if (!sp || sp.kind !== "freeze" || !fzNum(sp.at) || !fzNum(sp.dur) || !(sp.dur > 0)) continue;
      const a = fzNum(span[0]) ? Math.max(sp.at, span[0]) : sp.at, b = fzNum(span[1]) ? Math.min(sp.at + sp.dur, span[1]) : sp.at + sp.dur;
      if (b > a) ws.push([a, b]);
    }
  }
  ws.sort((p, q) => p[0] - q[0] || p[1] - q[1]);
  const out = [];
  for (const w of ws) {
    const last = out[out.length - 1];
    if (last && w[0] <= last[1]) last[1] = Math.max(last[1], w[1]);
    else out.push([w[0], w[1]]);
  }
  return Object.freeze(out.map((w) => Object.freeze(w)));
};

/* the frozen seconds before t */
export const frozenBefore = (ws, t) => {
  let s = 0;
  for (const [a, b] of ws || []) { if (t <= a) break; s += Math.min(t, b) - a; }
  return s;
};

/* THE LIFE CLOCK: t, with the frozen time before it taken out. No window: t itself, the same number. */
export const lifeClock = (ws, t) => (ws && ws.length ? t - frozenBefore(ws, t) : t);

/* ... counted from an ORIGIN t0 (a scene's start, a clip's mount): only the beats after t0 hold it back */
export const sceneClock = (ws, t, t0) => (ws && ws.length ? t0 + (lifeClock(ws, t) - lifeClock(ws, t0)) : t);

/* is the stage frozen at t - [a, b): at the beat's end life has resumed */
export const frozenAt = (ws, t) => (ws || []).some(([a, b]) => t >= a && t < b);

/* THE LIGHT'S POSE at t: its level f (0 off, 1 on). The held middle is exactly 1 - one pose, the stopped frame's. */
export const freezePose = (sp, t) => {
  const D = Math.max(0.001, +sp.dur || 0), d = t - +sp.at;
  if (!(d >= 0) || d >= D) return { f: 0 };
  const on = Math.min(FREEZE.ON_S, D * FREEZE.RAMP_MAX), off = Math.min(FREEZE.OFF_S, D * FREEZE.RAMP_MAX);
  if (d < on) return { f: fz01(minJerk(d / on)) };
  if (d > D - off) return { f: fz01(minJerk((D - d) / off)) };
  return { f: 1 };
};

/* THE FORM the light takes, from the box the target resolved to (stage px), or null */
export const freezeForm = (b) => {
  if (!b || !fzNum(b.x) || !fzNum(b.y)) return null;
  const w = fzNum(b.w) ? b.w : 0, h = fzNum(b.h) ? b.h : 0;
  if (w < FREEZE.POINT_PX && h < FREEZE.POINT_PX) {
    return { kind: "point", cx: b.x + w / 2, cy: b.y + h / 2, r: FREEZE.CORE_PX, glow: FREEZE.CORE_PX * LIT.GLOW_K / LIT.HEAD_K };
  }
  return { kind: "box", x: b.x - FREEZE.PAD, y: b.y - FREEZE.PAD, w: w + 2 * FREEZE.PAD, h: h + 2 * FREEZE.PAD,
           glow: FREEZE.EDGE_PX * LIT.GLOW_K };
};

/* the halo's colour: the light's own, at LIT's alpha */
export const freezeHalo = (px, a = LIT.GLOW_A, hex = FREEZE.COLOR) => {
  const n = parseInt(String(hex).slice(1), 16);
  return "drop-shadow(0 0 " + px.toFixed(2) + "px rgba(" + ((n >> 16) & 255) + "," + ((n >> 8) & 255) + "," + (n & 255) + "," + a + "))";
};

/* THE PAINTER. ctx is the engine's species context (SPECIES_PAINTERS in the player): the declaration, the clock, the
   layer already chosen for a datum (beneath any card) or anything else (above), and the shared helpers by name. */
export function paintFreeze(ctx) {
  const { sp, t, svg, el, resolveTarget } = ctx;
  const pose = freezePose(sp, t);
  if (pose.f <= 0) return;
  const form = freezeForm(resolveTarget(sp.target));
  if (!form) return;   /* the targeting law: no resolved target, nothing painted */
  const g = el("g", "frz", svg, { opacity: pose.f.toFixed(3) });
  if (form.kind === "point") {
    const r = form.r * (0.7 + 0.3 * pose.f);   /* a light switching on swells a little as it brightens; held, it is its size */
    const dot = el("circle", "frz-light", g, { cx: form.cx.toFixed(1), cy: form.cy.toFixed(1), r: r.toFixed(2), fill: FREEZE.COLOR });
    dot.style.filter = freezeHalo(form.glow);
    return;
  }
  const rect = el("rect", "frz-edge", g, { x: form.x.toFixed(1), y: form.y.toFixed(1), width: form.w.toFixed(1), height: form.h.toFixed(1),
                                           rx: FREEZE.EDGE_RX, fill: "none", stroke: FREEZE.COLOR, "stroke-width": FREEZE.EDGE_PX });
  rect.style.filter = freezeHalo(form.glow);
}

/* the module rule's registration: a plain assignment (inline_text keeps it), guarded so `node --test` can import this
   file for the math above without the engine's registry */
if (typeof SPECIES_PAINTERS !== "undefined") SPECIES_PAINTERS.freeze = paintFreeze;
