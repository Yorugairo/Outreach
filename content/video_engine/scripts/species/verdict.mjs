/* species/verdict.mjs - THE VERDICT STACK (P55 T7; doc 29 s9.24 / s9.24b; docs/portable/MOTION-GRAMMAR.md, the
   extraction of the scene-evidence player's `stackbox`/`drawStack`; the Steel and Paper verdict beat, 2026-08-30).
   SOURCE OF TRUTH, inlined into the scene-evidence player by sync_kinetics.py between KINETICS:BEGIN verdict and
   KINETICS:END. It imports `idle` - the rails of the SHORT's form carry a named idle kind (E49) - so its region sits
   after idle's, beside the dock painters it replaced (before `drawStack`).

   A DOCK PAYLOAD, not a species kind: this module registers NO painter. The engine's dock slot calls paintVerdict
   by name from its `drawStack` (P55 T7's decision: a DOCK_PAINTERS registry waits for a third dock painter -
   recorded, not built). Promoted from inline engine code with every frame byte-identical (the goldens
   `verdict-stack`, `verdict-stack@proof-burst`): each literal below is the value the inline code carried.

   WHEN: the episode's verdict line names the proofs it rests on - the stack re-presents documents ALREADY docked
   elsewhere, one per verbatim beat, and clears on the pivot line (`clear_at`).

   THE LAW: the stack re-presents documents already docked; the dance is the FOCUS HAND-OFF; every pose is a pure
   function of t (scrub-safe - nothing is stored between frames).

   PHASES and the BLENDS they came from (the operator's references of 2026-08-31, LEDGER ddc90e1656f9):
     enter  - one card at a time on its word beat, from depth: translateZ ENTER_Z, swung ENTER_SWING px to its
              side, rotateY ENTER_ROT_Y, over ENTER_S on an out-cubic (remotion-bits transform3d-showcase).
     focus  - large near stage centre (ACTIVE_X +/- ACTIVE_DX, ACTIVE_Y + row * ACTIVE_ROW_DY, ACTIVE_W px wide)
              while its phrase is spoken, drifting (the hyperframes-opening-v1 focus hand-off).
     recede - when the NEXT card's beat lands (the last card: LAST_RECEDE_LEAD before clear_at) it returns over
              RECEDE_S on an in-out cubic to one of the nine SPOTS - the page re-composes as a mosaic (remotion-bits
              mosaic-reframe). On the SHORT's form those spots are laid in READING BANDS (E99 s43): 1-2 across the
              top left to right, 3-4 across the bottom, 5-6 top, 7-8 bottom, 9 top.
     idle   - railed cards float on the drift (DRIFT_* / BOB_*), tilted by TILTS; on the SHORT's form that float is a
              NAMED idle kind (E49: IDLE_KIND "live" = breath + drift), sized by IDLE_DRIFT_PX / IDLE_BREATH_AMP and
              phased IDLE_PHASE per card, so no two rails breathe in step.
     burst  - on clear_at each card is thrown radially along its own bearing from the stage centre, spinning,
              BURST_STAGGER apart over BURST_S (remotion-bits fracture-reassemble, inferred); removed at
              clear_at + REMOVE_AFTER.
   TWO SURFACES, ONE CHOREOGRAPHY (P61 T7): `VERDICT` is the full-frame form; `VERDICT_9X16` re-lays the SAME five
   phases for a short. `verdictDials(portrait)` hands the painter one or the other - nothing else differs.
   The dials below are ours to tune (42 s42.5), not findings. doc 29 s9.24's translateZ -940 is stale: the code is -700. */

import { idleXf } from "../kinetics/idle.mjs";

export const VERDICT = Object.freeze({
  SPOTS: Object.freeze([           /* the nine rail spots [left %, top %, width %]: four across the top, mid-frame flanks, three along the bottom - the centre stays open for the active card */
    Object.freeze([2, 5, 24]), Object.freeze([27, 3, 22]), Object.freeze([51, 4, 22]), Object.freeze([74, 5, 24]),
    Object.freeze([1, 40, 22]), Object.freeze([77, 40, 22]),
    Object.freeze([4, 62, 26]), Object.freeze([37, 66, 24]), Object.freeze([68, 62, 26])]),
  TILTS: Object.freeze([-3, 2, -2, 3, -2.5, 2.5]),   /* the railed card's tilt in deg, cycled by index */
  CARD_W: 1056,          /* the docked document's aspect: width ... */
  CARD_H: 480,           /* ... and height (hpx = wpx * CARD_H / CARD_W) */
  ACTIVE_X: 930,         /* the focus pose's centre x in stage px ... */
  ACTIVE_DX: 70,         /* ... alternating +/- this by index (odd right, even left) */
  ACTIVE_Y: 400,         /* the focus pose's centre y in stage px ... */
  ACTIVE_ROW_DY: 26,     /* ... stepped down this per row ... */
  ACTIVE_ROWS: 3,        /* ... cycling over this many rows (i % 3) */
  ACTIVE_W: 840,         /* the focus pose's width in stage px (scale = ACTIVE_W / rail width) */
  BURST_NORM_X: 700,     /* the burst's x normaliser in landscape px (kept as a fraction of REF_W, 2026-09-08) */
  BURST_NORM_Y: 460,     /* the burst's y normaliser in landscape px (a fraction of REF_H) */
  ORIGIN_X: 0.5,         /* the burst throws radially FROM here, as a fraction of the stage: full-frame it is the ... */
  ORIGIN_Y: 0.5,         /* ... stage centre (the short's form throws from the centre of its safe box instead) */
  IDLE_KIND: null,       /* the RAILED cards' idle: full-frame keeps the inline drift/bob below; the short's form names an E49 kind */
  REF_W: 1920,           /* the landscape stage the normalisers were measured on: width ... */
  REF_H: 1080,           /* ... and height */
  ENTER_S: 0.9,          /* the enter's clock (out-cubic) */
  ENTER_SWING: 460,      /* the enter's side swing in px, signed by the card's dir */
  ENTER_RISE: -90,       /* the enter's vertical offset in px (from above) */
  ENTER_Z: -700,         /* the enter's depth: translateZ px (doc 29 s9.24's -940 is stale) */
  ENTER_ROT_Y: 30,       /* the enter's rotateY in deg, signed by dir */
  RECEDE_S: 1.0,         /* the recede's clock (in-out cubic) */
  LAST_RECEDE_LEAD: 0.9, /* the last card recedes this long before clear_at */
  DRIFT_W: 0.55,         /* the x drift's angular rate (rad/s) ... */
  DRIFT_PHASE: 1.7,      /* ... phased per index */
  DRIFT_X_REST: 8,       /* the x drift amplitude on the rail ... */
  DRIFT_X_ACTIVE: 26,    /* ... plus this much more in focus */
  BOB_W: 0.7,            /* the y bob's angular rate (rad/s) ... */
  BOB_PHASE: 2.1,        /* ... phased per index */
  BOB_REST: 5,           /* the y bob amplitude on the rail ... */
  BOB_ACTIVE: 14,        /* ... plus this much more in focus */
  DRIFT_SCALE: 0.008,    /* the scale breath in focus, times the drift */
  DRIFT_ROT: 0.6,        /* the rotation drift in focus (deg), times the drift */
  Z_SWITCH: 0.5,         /* the blend above which the card is on top ... */
  Z_ACTIVE: 9,           /* ... at this z-index ... */
  Z_RAIL: 7,             /* ... and below it at this one */
  BURST_X: 560,          /* the burst's x throw in px along the bearing */
  BURST_Y: 420,          /* the burst's y throw in px along the bearing */
  BURST_Z: 340,          /* the burst's translateZ toward the viewer */
  BURST_SPIN: 24,        /* the burst's spin in deg, signed by dir */
  BURST_SCALE: 0.22,     /* the burst's added scale */
  BURST_STAGGER: 0.06,   /* card i bursts this long after card i-1 */
  BURST_S: 0.5,          /* each card's burst clock (quadratic in) */
  REMOVE_AFTER: 1.4,     /* the stackbox is removed this long after clear_at ... */
  MOUNT_LEAD: 0.5,       /* ... and when t is earlier than the dock's enter less this */
});

/* G-l's vertical safe box on a 1080x1920 stage (scripts/gate_vertical_safe_box.py SAFE_X / SAFE_Y): platform chrome
   covers the top 280, the bottom 480 and the right 200 px of a short, so nothing the viewer must read lives outside
   [x0, x1, y0, y1]. Every 9:16 spot below is inside it WITH its idle and its breath, measured 2026-09-15. */
const VERDICT_SAFE_9X16 = Object.freeze([80, 880, 280, 1340]);

/* THE SHORT'S FORM (P61 T7; BACKLOG R26-82; E99 s21 - "our cards in steel and paper felt much more alive, and also it
   didn't just place them horizontally, we had real choreography and movement, which then made the burst better").
   The SAME five phases; only the geometry is re-laid, because on a 1080x1920 stage the landscape dials FLATTEN four of
   them (measured on the golden forced to 9:16, 2026-09-15): SPOTS 1-4 are % of a 16:9 frame, so they land at y 53-92
   of 1920 - a horizontal row, inside the platform's top chrome - while both flank spots (1 % and 77 %) hang off the
   edges at x -88 and x 1061, and the focus pose (ACTIVE_X 930, ACTIVE_W 840) runs 223 px past the right edge.
   THE NINE SPOTS ARE LAID IN READING BANDS (P61 T7b; E99 s43, the operator on the first mosaic: "I realized we
   probably don't want to be sending peoples eyes scattered everywhere, probably to do 1-2 on top, left to right since
   thats how people read. then 3-4, on bottom, 5-6 on top, 7-8 on bottom etc."). Two bands - one ABOVE the focus card,
   one BELOW it - take the proofs two at a time, and inside a band the pair runs LEFT TO RIGHT:
       TOP    row 0: proofs 1, 2         BOTTOM row 0: proofs 3, 4
       TOP    row 1: proofs 5, 6, 9      BOTTOM row 1: proofs 7, 8
   so every recede hands the eye to the place a reader looks next instead of to a random hole. s21's "asymmetric
   SPOTS" is AMENDED by s43: the asymmetry lives in SIZE (22.2-32.2 % wide) and TILT, never in ORDER.
   WHY 5 AND 6 TAKE A SECOND ROW rather than standing to the right of 1 and 2: the width is spent. Proofs 1 and 2 are
   348 + 340 px of the 776 px the safe box leaves once a card's tilt, idle walk and breath are allowed for; four
   across that line puts every top card at 194 px - 18 % of the stage, under the focus card's 1.4x rail bar and under
   reading size. Two rows of two is the same reading path, one line further down.
   WHY PROOF 9 STANDS TO THE RIGHT OF 6 rather than opening a third row: the band's HEIGHT is spent. The top band runs
   y[286, 614] - 328 px - and its two rows already use y[286, 476] and y[452, 605]; a third row would crush all five
   cards in the band. Its WIDTH was not spent: 288 + 272 + 240 = 800 px with two 6-12 % corner overlaps, and proof 9
   is the smallest card of the nine, which is what lets that line hold three.
   THE BANDS CLEAR THE FOCUS CARD, which is the rule the landscape SPOTS state as "the centre stays open". It is
   690 x 314 px centred at (480, 790-834), so with its own drift and breath it owns y[614, 1010] across nearly the
   whole safe width; a rail spot inside that band is not overlapped, it is BURIED (the first lay-out of this form lost
   a whole card behind proof 8). Every spot below ends above y 605 or begins below y 1019, and every one of them -
   its tilt's bounding box, its 6.5 px idle walk and its 1 % breath included - sits inside x[80, 880] y[280, 1340].
   They cover 45 % of the box, the reference's own 45 %: doc 29 s9.24's "scattered asymmetric SPOTS keep the plate
   visible through the gaps" is a DENSITY as much as a placement, and the density survives the bands - the rows
   overlap by a card corner, never by a face. Their centres straddle the safe box's centre on both axes, which is what
   makes the burst a radial fan rather than a landscape throw.
   THE BANDS ARE NOT A TABLE. The two bands start at different left margins (104 / 175 px) and row 1 is staggered
   under row 0's aisle, so the seven rails standing at the mosaic take FIVE column starts - a reading path, not a
   ruled grid. */
const VERDICT_SPOTS_9X16 = Object.freeze([
  Object.freeze([9.6, 15.6, 32.2]),    /* [left %, top %, width %] - TOP band, row 0: proof 1 opens the line at the left ... */
  Object.freeze([45.0, 16.2, 31.5]),   /* ... proof 2 finishes it to the right - "1-2 on top, left to right" */
  Object.freeze([16.2, 53.6, 31.1]),   /* BOTTOM band, row 0: proof 3 opens the line under the focus card ... */
  Object.freeze([48.9, 54.2, 29.6]),   /* ... proof 4 to its right - "then 3-4, on bottom" */
  Object.freeze([9.3, 24.1, 26.7]),    /* TOP band, row 1: proof 5 back at the left margin, the next line up top ... */
  Object.freeze([33.0, 24.5, 25.2]),   /* ... proof 6 to its right - "5-6 on top" */
  Object.freeze([9.3, 61.4, 27.8]),    /* BOTTOM band, row 1: proof 7 at the left ... */
  Object.freeze([40.0, 61.0, 29.3]),   /* ... proof 8 to its right - "7-8 on bottom" */
  Object.freeze([56.7, 23.8, 22.2])]); /* TOP band, row 1: proof 9 - the smallest card - closes that line to the right of 6 */

export const VERDICT_9X16 = Object.freeze(Object.assign({}, VERDICT, {
  SPOTS: VERDICT_SPOTS_9X16,
  SAFE: VERDICT_SAFE_9X16,
  ACTIVE_X: 480,         /* the focus pose's centre x: the safe box's own centre, not the stage's (the right 200 px are chrome) */
  ACTIVE_DX: 20,         /* ... alternating +/- this by index, so two proofs in a row are not the same picture */
  ACTIVE_Y: 790,         /* ... and its centre y, a touch above the box's centre so the caption strip stays clear */
  ACTIVE_ROW_DY: 22,     /* ... stepped down this per row, cycling over ACTIVE_ROWS - small, because the band it owns is what the rails have to clear */
  ACTIVE_W: 690,         /* the focus card is 63.9 % of the stage width - 1.5x to 2.1x every rail card (the reference runs 1.65x-1.96x) */
  ENTER_SWING: 300,      /* a portrait frame is 1080 wide: the landscape 460 px swing would start the card off-stage */
  ENTER_RISE: -130,      /* ... and it has height to fall through instead */
  BURST_NORM_X: 320,     /* the bearing's normalisers, re-measured on the portrait stage ... */
  BURST_NORM_Y: 430,
  REF_W: 1080,           /* ... which is this one */
  REF_H: 1920,
  ORIGIN_X: (VERDICT_SAFE_9X16[0] + VERDICT_SAFE_9X16[1]) / 2 / 1080,   /* the burst is radial FROM THE MOSAIC'S OWN CENTRE - */
  ORIGIN_Y: (VERDICT_SAFE_9X16[2] + VERDICT_SAFE_9X16[3]) / 2 / 1920,   /* the safe box's centre, which is where the wall is */
  BURST_X: 620,          /* the throw, on the portrait frame's own axes: wider than the frame ... */
  BURST_Y: 900,          /* ... and much taller, because down and up is where a short has room */
  IDLE_KIND: "live",     /* E49: the railed cards' idle is a NAMED kind (breath + drift), sized by the two dials below ... */
  IDLE_DRIFT_PX: 6.5,    /* ... the walk's half-width in stage px (idle.mjs's 2.0 is for a pill, not a 400 px card) ... */
  IDLE_BREATH_AMP: 0.010,/* ... and a 1.0 % inhale, above rest only */
  IDLE_PHASE: 0.137,     /* ... phased this far apart per card, so no two rails breathe in step */
}));

/* WHICH DIALS: the stage's own shape, unless the payload names a form (build_scene_timeline_f.stack_entry). */
export const verdictDials = (portrait) => (portrait ? VERDICT_9X16 : VERDICT);

const verdict01 = (v) => Math.min(1, Math.max(0, v));

/* THE RAIL SPOT and the focus pose of card i, from the stage size: the base CSS rect is the rail spot, the focus
   pose is a transform relative to it; bx/by are the burst's normalised offset from the stage centre. */
export const verdictGeometry = (i, stageW, stageH, V = VERDICT) => {
  const [L, T, W] = V.SPOTS[i % V.SPOTS.length];
  const wpx = W / 100 * stageW, hpx = wpx * V.CARD_H / V.CARD_W;
  const cx = L / 100 * stageW + wpx / 2, cy = T / 100 * stageH + hpx / 2;
  const acx = V.ACTIVE_X + (i % 2 ? V.ACTIVE_DX : -V.ACTIVE_DX), acy = V.ACTIVE_Y + (i % V.ACTIVE_ROWS) * V.ACTIVE_ROW_DY;
  return { L, T, W,
           tilt: V.TILTS[i % V.TILTS.length],
           dir: i % 2 ? 1 : -1,
           adx: acx - cx, ady: acy - cy, asc: V.ACTIVE_W / wpx,
           bx: (cx - V.ORIGIN_X * stageW) / (stageW * V.BURST_NORM_X / V.REF_W),
           by: (cy - V.ORIGIN_Y * stageH) / (stageH * V.BURST_NORM_Y / V.REF_H) };
};

/* when card i hands the focus on: the next card's beat, or LAST_RECEDE_LEAD before the clear for the last */
export const verdictNextAt = (items, i, clearAt, V = VERDICT) =>
  i + 1 < items.length ? items[i + 1].at : clearAt - V.LAST_RECEDE_LEAD;

/* THE POSE before the clear: enter -> focus -> recede -> idle. a = the pose blend (0 rail, 1 focus). */
export const verdictPose = (item, i, t, nextAt, clearAt, V = VERDICT) => {
  const e = verdict01((t - item.at) / V.ENTER_S);
  const ee = 1 - Math.pow(1 - e, 3);
  const r = verdict01((t - nextAt) / V.RECEDE_S);
  const rr = r < 0.5 ? 4 * r * r * r
                     : 1 - Math.pow(-2 * r + 2, 3) / 2;
  const a = ee * (1 - rr);
  const drift = Math.sin(t * V.DRIFT_W + i * V.DRIFT_PHASE);
  /* THE RAIL'S LIFE. The short's form names an E49 idle kind for the RAILED share of the pose (a = 0), sized by its
     own dials and phased per card; the FOCUS share keeps the continuous wander the hyperframes hand-off asks for
     (s9.24b: "the active card drifts continuously; railed cards hold almost still"). Full-frame keeps the inline
     drift/bob it shipped with, expression for expression - every landscape frame is byte-identical. */
  const ix = V.IDLE_KIND ? idleXf(V.IDLE_KIND, t, i * V.IDLE_PHASE,
                                  { DRIFT_PX: V.IDLE_DRIFT_PX, BREATH_AMP: V.IDLE_BREATH_AMP }) : null;
  const dx = ix ? item.adx * a + ix.dx * (1 - a) + drift * V.DRIFT_X_ACTIVE * a
                : item.adx * a + drift * (V.DRIFT_X_REST + V.DRIFT_X_ACTIVE * a);
  const dy = ix ? item.ady * a + ix.dy * (1 - a) + Math.cos(t * V.BOB_W + i * V.BOB_PHASE) * V.BOB_ACTIVE * a
                : item.ady * a + Math.cos(t * V.BOB_W + i * V.BOB_PHASE) * (V.BOB_REST + V.BOB_ACTIVE * a);
  const sc = (ix ? 1 + (ix.scale - 1) * (1 - a) : 1) + (item.asc - 1) * a + drift * V.DRIFT_SCALE * a;
  return { tx: dx + (1 - ee) * V.ENTER_SWING * item.dir,
           ty: dy + (1 - ee) * V.ENTER_RISE,
           tz: (1 - ee) * V.ENTER_Z,
           rotY: (1 - ee) * V.ENTER_ROT_Y * item.dir,
           rot: item.tilt * (1 - a) + drift * V.DRIFT_ROT * a,
           scale: sc, opacity: ee, z: a > V.Z_SWITCH ? V.Z_ACTIVE : V.Z_RAIL, a };
};

/* THE BURST from clear_at: card i thrown along its own bearing (bx, by), BURST_STAGGER after card i-1. */
export const verdictBurst = (item, i, t, clearAt, V = VERDICT) => {
  const cb = verdict01((t - clearAt - i * V.BURST_STAGGER) / V.BURST_S);
  const cbe = cb * cb;
  return { cb, tx: cbe * V.BURST_X * item.bx, ty: cbe * V.BURST_Y * item.by, tz: cbe * V.BURST_Z,
           rot: item.tilt + cbe * V.BURST_SPIN * item.dir, scale: 1 + cbe * V.BURST_SCALE, opacity: 1 - cb };
};

/* THE PAINTER: writes every card's pose at t. Returns false when the stack is outside its life (the stackbox is
   removed - the caller forgets its state), true otherwise. */
export function paintVerdict(st, t, d, V = VERDICT) {
  if (t > st.clear_at + V.REMOVE_AFTER || t < d.enter - V.MOUNT_LEAD) {
    st.sb.remove(); return false;
  }
  st.items.forEach((it, i) => {
    if (t >= st.clear_at) {
      const b = verdictBurst(it, i, t, st.clear_at, V);
      it.card.style.opacity = b.opacity.toFixed(2);
      it.card.style.transform =
        `translate(${b.tx}px, ${b.ty}px)` +
        ` translateZ(${b.tz}px)` +
        ` rotate(${b.rot}deg)` +
        ` scale(${b.scale})`;
      return;
    }
    const p = verdictPose(it, i, t, verdictNextAt(st.items, i, st.clear_at, V), st.clear_at, V);
    it.card.style.opacity = p.opacity.toFixed(2);
    it.card.style.zIndex = p.z;
    it.card.style.transform =
      `translate(${p.tx.toFixed(1)}px,` +
      ` ${p.ty.toFixed(1)}px)` +
      ` translateZ(${p.tz}px)` +
      ` rotateY(${p.rotY}deg)` +
      ` rotate(${p.rot.toFixed(2)}deg)` +
      ` scale(${p.scale.toFixed(3)})`;
  });
  return true;
}
