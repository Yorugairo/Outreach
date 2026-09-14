/* species/verdict.mjs - THE VERDICT STACK (P55 T7; doc 29 s9.24 / s9.24b; docs/portable/MOTION-GRAMMAR.md, the
   extraction of the scene-evidence player's `stackbox`/`drawStack`; the Steel and Paper verdict beat, 2026-08-30).
   SOURCE OF TRUTH, inlined into the scene-evidence player by sync_kinetics.py between KINETICS:BEGIN verdict and
   KINETICS:END. It imports nothing; its region sits beside the dock painters it replaced (before `drawStack`).

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
              RECEDE_S on an in-out cubic to one of the nine asymmetric SPOTS - the page re-composes as a mosaic
              (remotion-bits mosaic-reframe).
     idle   - railed cards float on the drift (DRIFT_* / BOB_*), tilted by TILTS.
     burst  - on clear_at each card is thrown radially along its own bearing from the stage centre, spinning,
              BURST_STAGGER apart over BURST_S (remotion-bits fracture-reassemble, inferred); removed at
              clear_at + REMOVE_AFTER.
   The dials below are ours to tune (42 s42.5), not findings. doc 29 s9.24's translateZ -940 is stale: the code is -700. */

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
           bx: (cx - stageW / 2) / (stageW * V.BURST_NORM_X / V.REF_W), by: (cy - stageH / 2) / (stageH * V.BURST_NORM_Y / V.REF_H) };
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
  const dx = item.adx * a + drift * (V.DRIFT_X_REST + V.DRIFT_X_ACTIVE * a);
  const dy = item.ady * a + Math.cos(t * V.BOB_W + i * V.BOB_PHASE) * (V.BOB_REST + V.BOB_ACTIVE * a);
  const sc = 1 + (item.asc - 1) * a + drift * V.DRIFT_SCALE * a;
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
