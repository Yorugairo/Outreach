/* species/tippill.mjs - THE TIP-RIDING PILL (P50 T11; R26-34; E53 s8). SOURCE OF TRUTH, inlined into the scene-evidence
   player by sync_kinetics.py between KINETICS:BEGIN tippill and KINETICS:END, AFTER spring (it uses springPop).
   A dense line that is drawing has a tip and nothing else; the pill is the tip's LIFE - the thing that says which line
   this is while it is still being drawn, instead of a label that appears once it stops.
     X_pill(u) = P_tip(u) + D_offset, a LEADER from the tip to the pill, the pill popping in on springPop(Mp = 0.05) at
     a declared milestone (the datum the sentence turns on), and at the end of the draw the pill settles onto the
     terminal tag's place and the TAG takes over - E53 s8 is unchanged, the pill is what happens before it.
   It carries no painter: it is not a species kind (nothing targets it), it is a line page's option (`;pill=` on the
   plate id -> `page.tip_pill`), so the module is the math and the page's builder is the only caller.
   Every value here is a pure function of the line's points and the fraction of it that is drawn: the pop runs in the
   LINE's own progress rather than in seconds, so a seek to any t paints exactly what playing to it would. */
import { springPop } from "../kinetics/spring.mjs";

export const TIPPILL = Object.freeze({
  DX: 30,          /* D_offset, x: the pill rides AHEAD of the tip by half a pill's height, so the nib is never covered and the eye reads pill-then-tip [DERIVED: the 6 px tip circle plus the 24 px the leader needs to be seen as a leader] */
  DY: -40,         /* D_offset, y: above the tip - a line that falls has its own space below it, and a pill under the tip would sit on the axis labels */
  POP_MP: 0.05,    /* R26-34's named overshoot: springPop(Mp = 0.05) - one notch past the standing pop (SPRING.MP 0.04) because the pill arrives on a WORD */
  POP_F: 0.06,     /* the pop's span as a share of the line's length: at the pen's speed (E50's two-thirds law) that is ~0.3 s on our pages, and it must end while the tip is still at the milestone */
  SETTLE: 0.10,    /* the last share of the draw: the pill leaves the tip and lands on the tag's place. It is 0.10 because the terminal tag fades IN over exactly the last tenth of the draw (lpPaintChart) - one place, one string, no double label */
  LEAD_GAP: 7,     /* the leader stops this far short of the tip and of the pill: a line that touches either reads as a stem, not a leader */
  PAD_X: 14, PAD_Y: 9,   /* the pill's padding around its type [DERIVED: the rail pill's own 2px/6px at 13px scaled to the chart's 19-34px name] */
});

/* ---- the line's arc length ------------------------------------------------------------------------------------- */
export const polyCum = (pts) => {
  const cum = [0];
  for (let i = 1; i < pts.length; i++) cum.push(cum[i - 1] + Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]));
  return cum;
};
/* P_tip(u): the point at fraction u of the polyline's ARC LENGTH (what a dash offset draws to), and the unit tangent
   there - the pill's offset is applied in the page's frame, but the leader is drawn from the tip itself. */
export const tipAt = (pts, u) => {
  const n = pts.length;
  if (!n) return null;
  if (n === 1) return { p: [pts[0][0], pts[0][1]], t: [1, 0], i: 0 };
  const cum = polyCum(pts), L = cum[n - 1], s = Math.max(0, Math.min(1, u)) * L;
  let i = 0;
  while (i < n - 2 && cum[i + 1] < s) i++;
  const a = pts[i], b = pts[i + 1], seg = Math.max(1e-9, cum[i + 1] - cum[i]), k = Math.max(0, Math.min(1, (s - cum[i]) / seg));
  const p = [a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k], d = Math.hypot(b[0] - a[0], b[1] - a[1]) || 1;
  return { p, t: [(b[0] - a[0]) / d, (b[1] - a[1]) / d], i };
};
/* the fraction of the line's length at which a DATUM sits - how a milestone index becomes a milestone in u */
export const fracAtIndex = (pts, index) => {
  const cum = polyCum(pts), L = cum[cum.length - 1] || 1, i = Math.max(0, Math.min(pts.length - 1, index | 0));
  return cum[i] / L;
};

/* the pill kept ON the stage. X_pill = P_tip + D_offset is where it WANTS to be; a long tag riding a line that ends
   at the right edge would put half its string off the page (read off the first frame, 2026-09-11). The law is the
   offset, then the clamp - stated here so the caller cannot forget it and a test can pin it.
   `span` is the pill's own ink relative to its anchor point, [left, right] - the caller measures its box (a tag is
   written from its end, or its middle, and may carry a badge chip of its own; no character count gets that right). */
export const pillSpan = (x, span) => [x + span[0], x + span[1]];
export const pillClamp = (x, span, x0, x1) => {
  const [lo, hi] = pillSpan(x, span);
  if (hi - lo >= x1 - x0) return x;            /* wider than the stage: leave it where it is, the author wrote it */
  if (lo < x0) return x + (x0 - lo);
  if (hi > x1) return x - (hi - x1);
  return x;
};

/* the leader's far end (R26-42, P52 T2): ON the capsule's boundary, at the edge nearest the tip - never inside it.
   `box` is the pill's ink about its anchor, {x, y, w, h} (pillBox's shape, placed by the caller: a tag written from
   its end puts the anchor on the box's edge, one written from its middle at the centre; a badge chip widens it).
   The first cut ran the leader to the ANCHOR, which for an end-anchored tag sits inside the box - the line vanished
   behind its own capsule. Without a box, `span` ([left, right] about the anchor) gives the horizontal extent and
   the vertical is unbounded; without either the terminus is the anchor itself. The ray from the anchor toward the
   tip is cut where it leaves the rect (the capsule's rounded corners sit inside the rect, so a point on the rect
   is on or outside the capsule); an anchor outside its own box ends the leader at the anchor. */
export const leaderEnd = (tip, pill, box, span) => {
  const dx = tip[0] - pill[0], dy = tip[1] - pill[1], d = Math.hypot(dx, dy) || 1, ux = dx / d, uy = dy / d;
  const r = box ? [pill[0] + box.x, pill[1] + box.y, pill[0] + box.x + box.w, pill[1] + box.y + box.h]
          : span ? [pill[0] + span[0], -Infinity, pill[0] + span[1], Infinity] : null;   /* a span bounds x alone */
  if (!r) return { p: [pill[0], pill[1]], t: 0 };
  const e = 1e-9, inside = pill[0] >= r[0] - e && pill[0] <= r[2] + e && pill[1] >= r[1] - e && pill[1] <= r[3] + e;
  if (!inside) return { p: [pill[0], pill[1]], t: 0 };
  const tx = ux > 0 ? (r[2] - pill[0]) / ux : ux < 0 ? (r[0] - pill[0]) / ux : Infinity;
  const ty = uy > 0 ? (r[3] - pill[1]) / uy : uy < 0 ? (r[1] - pill[1]) / uy : Infinity;
  const t = Math.max(0, Math.min(tx, ty, d));          /* never past the tip: a box that swallows the tip has no leader */
  return { p: [pill[0] + ux * t, pill[1] + uy * t], t };
};

/* ---- the pill ---------------------------------------------------------------------------------------------------- */
/* the whole state at a drawn fraction u. `o.milestone` is the fraction the pill pops at (0 = with the first ink),
   `o.tag` the terminal tag's settled [x, y] - the place the pill hands over at. Nothing here reads the DOM. */
export const pillAt = (pts, u, o = {}) => {
  const P = Object.assign({}, TIPPILL, o.dials || {});
  const tip = tipAt(pts, u);
  if (!tip) return null;
  const m = Math.max(0, Math.min(1, o.milestone == null ? 0 : o.milestone));
  const pop = springPop(Math.max(0, Math.min(1, (u - m) / Math.max(1e-6, P.POP_F))), P.POP_MP);
  /* the settle: over the last SETTLE of the draw the pill leaves the tip for the tag's place, and the tag takes over
     as it lands - `handover` is what the caller cross-fades on (1 = the tag owns the name) */
  const s0 = 1 - P.SETTLE;
  const k = u >= 1 ? 1 : (P.SETTLE > 0 ? Math.max(0, Math.min(1, (u - s0) / P.SETTLE)) : 0);   /* the draw's end IS the hand-over, whatever the float says about 1 - 0.1 + 0.1 */
  const b = o.bounds, span = o.span;
  const rideX = b && span ? pillClamp(tip.p[0] + P.DX, span, b[0], b[1]) : tip.p[0] + P.DX;
  const ride = [rideX, tip.p[1] + P.DY];
  const land = o.tag ? [o.tag[0], o.tag[1]] : ride;
  /* at k = 1 the pill IS the tag's place - exactly, not within a float - because the tag is drawn there next frame */
  const pill = k >= 1 ? [land[0], land[1]] : [ride[0] + (land[0] - ride[0]) * k, ride[1] + (land[1] - ride[1]) * k];
  /* the leader, short of both ends; it fades with the settle (the pill is no longer the tip's). Its far end is the
     capsule's NEAR EDGE (leaderEnd, R26-42), not the anchor - `o.box` from the caller's pillBox, `o.span` as a fallback */
  const end = leaderEnd(tip.p, pill, o.box, o.span).p;
  const dx = end[0] - tip.p[0], dy = end[1] - tip.p[1], d = Math.hypot(dx, dy) || 1;
  const gap = Math.min(P.LEAD_GAP, d / 3), ux = dx / d, uy = dy / d;
  return {
    on: u > m && u < 1,
    tip: tip.p,
    pill,
    scale: pop,
    pop,
    settle: k,
    handover: k,
    leader: [[tip.p[0] + ux * gap, tip.p[1] + uy * gap], [end[0] - ux * gap, end[1] - uy * gap]],
    leaderOpacity: 1 - k,
  };
};

/* the pill's box for a measured text width - the caller measures its own type, the shape is the module's */
export const pillBox = (w, h, o = {}) => {
  const P = Object.assign({}, TIPPILL, o.dials || {});
  const bw = w + 2 * P.PAD_X, bh = h + 2 * P.PAD_Y;
  return { w: bw, h: bh, x: -bw / 2, y: -bh / 2, r: Math.min(bh / 2, 12) };
};
