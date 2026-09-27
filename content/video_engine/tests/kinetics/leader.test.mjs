// P72 T53 (h) / R26-414 (a) - THE LEADER (the Bravos harvest v2's R35, STK 0:02-0:10): a curved pointer from a figure,
// a datum or a point to a datum or a bar's printed value, drawn by length on its word, a head at the target, an optional
// ring round it and the multiple on the arc. These tests pin the clock, the arc (vecmap's clothoid law, restated by value
// and pinned equal here), the ends (the flow's edge law on a box, the polar radius on a ring), the side (the author's
// bend, else the first clear candidate), the pill's pop (axis_tag's), the leave, and the painter reached only through
// what the builder hands it.
import { test } from "node:test";
import assert from "node:assert/strict";
import { LEADER, leaderPose, leaderPillScale, leaderCentre, leaderOut, leaderUp, leaderArc, leaderAlong, leaderHead,
         leaderPillBox, leaderCost, leaderChoose, paintLeader } from "../../scripts/species/leader.mjs";
import { ARC, arcHead } from "../../scripts/species/vecmap.mjs";
import { AXTAG } from "../../scripts/species/axis_tag.mjs";
import { curvatureOf } from "../../scripts/kinetics/clothoid.mjs";

const near = (a, b, eps = 1e-6) => Math.abs(a - b) <= eps;
const sp = (o = {}) => Object.assign({ kind: "leader", at: 10, dur: 2 }, o);

test("the arc's dials ARE the vector map's arc: one hand draws every generated arc", () => {
  assert.equal(LEADER.BOW, ARC.BOW);
  assert.equal(LEADER.ENTER_K, ARC.ENTER_K);
  assert.equal(LEADER.SAMPLES, ARC.SAMPLES);
  assert.equal(LEADER.HEAD_PX, ARC.HEAD);
  assert.equal(LEADER.HEAD_A, ARC.HEAD_A);
  assert.ok(LEADER.BOWS[0] === LEADER.BOW && LEADER.BOWS.every((b, i) => i === 0 || b > LEADER.BOWS[i - 1]), "the arc's own bow first, then wider");
  assert.equal(LEADER.BEND_MAX, LEADER.BOWS[LEADER.BOWS.length - 1]);
});

test("the clock: nothing before the word; the shaft draws first, the head lands as it arrives, the pill pops last", () => {
  assert.equal(leaderPose(sp(), 9.99).on, false);
  const p0 = leaderPose(sp(), 10);
  assert.equal(p0.on, true);
  assert.equal(p0.shaft, 0);
  assert.equal(p0.head, 0);
  const pe = leaderPose(sp(), 12);
  for (const k of ["shaft", "head", "ring", "label"]) assert.equal(pe[k], 1, k);
  assert.ok(LEADER.HEAD[0] < LEADER.SHAFT[1] && LEADER.HEAD[1] > LEADER.SHAFT[1] - 0.1, "the head lands as the shaft arrives");
  assert.ok(LEADER.LABEL[0] > LEADER.SHAFT[0] && LEADER.LABEL[1] === 1, "the multiple lands inside the word, never after it");
  const pm = leaderPose(sp(), 10 + 2 * (LEADER.SHAFT[0] + LEADER.SHAFT[1]) / 2);
  assert.ok(near(pm.shaft, 0.5, 1e-9), "min-jerk: half the shaft's window is half its length");
});

test("the pill pops on axis_tag's spring from the label's window", () => {
  assert.equal(leaderPillScale(sp(), 10 + 2 * LEADER.LABEL[0] - 0.01), 0);
  assert.ok(leaderPillScale(sp(), 10 + 2 * LEADER.LABEL[0] + AXTAG.POP_S * 0.5) > 0);
  assert.equal(leaderPillScale(sp(), 10 + 2 * LEADER.LABEL[0] + AXTAG.POP_S), 1);
});

test("the ends: a box's edge by the flow's law, a ring's by its polar radius, a point itself - each `gap` clear", () => {
  const box = [100, 200, 300, 260];   // 200 x 60, centre (200, 230)
  assert.deepEqual(leaderCentre(box), [200, 230]);
  const e = leaderOut(box, 0, 10);
  assert.ok(near(e[0], 310) && near(e[1], 230), "to the right: the box's right edge + the gap");
  const u = leaderOut(box, -Math.PI / 2, 0);
  assert.ok(near(u[0], 200) && near(u[1], 200), "up: its top edge");
  const d = leaderOut(box, Math.atan2(1, 1), 0);
  assert.ok(near(d[1], 260) && near(d[0], 230), "a diagonal leaves by the side it meets first (the short one)");
  const ring = { cx: 0, cy: 0, rx: 40, ry: 20 };
  assert.ok(near(leaderOut(ring, 0, 5)[0], 45) && near(leaderOut(ring, Math.PI / 2, 0)[1], 20));
  assert.deepEqual(leaderOut([50, 60], 0, 0), [50, 60]);
});

test("the arc is a clothoid with the arc's unequal tangents: it LIFTS toward the page's top when asked, and meets both ends", () => {
  const A = [800, 100, 900, 150], B = [200, 400];
  const up = leaderUp(leaderCentre(A), leaderCentre(B));
  const pts = leaderArc(A, B, LEADER.BOW, up, [0, 0]);
  assert.equal(pts.length, LEADER.SAMPLES);
  const mid = leaderAlong(pts, 0.5), chordMidY = (pts[0].y + pts[pts.length - 1].y) / 2;
  assert.ok(mid.y < chordMidY - 20, "the up side bows ABOVE the chord (svg y down)");
  const down = leaderArc(A, B, LEADER.BOW, -up, [0, 0]);
  assert.ok(leaderAlong(down, 0.5).y > chordMidY + 20, "... and the other side below it");
  assert.ok(near(pts[pts.length - 1].x, 200, 1e-6) && near(pts[pts.length - 1].y, 400, 1e-6), "the tip on a point target");
  assert.ok(pts[0].x <= 800 + 1e-6 || pts[0].y >= 150 - 1e-6, "the tail on the source box's outline, not inside it");
  const k = curvatureOf(pts.map((p) => ({ x: p.x, y: p.y }))).slice(1, -1), dk = k.slice(1).map((v, i) => v - k[i]);
  assert.ok(dk.every((v) => v >= -1e-6) || dk.every((v) => v <= 1e-6), "dk/ds is one sign along it: an Euler spiral, never a Bezier's ripple");
  const straight = leaderArc([0, 0], [100, 0], 0, 1, [0, 0]);
  assert.ok(straight.every((p) => near(p.y, 0, 1e-6)), "bend 0 is the chord");
});

test("along the arc by length; the head is the arc's own arrowhead (arcHead) at the leader's arm", () => {
  const pts = leaderArc([0, 0], [300, 0], 0.6, -1, [0, 0]);
  const m0 = leaderAlong(pts, 0), m1 = leaderAlong(pts, 1);
  assert.ok(near(m0.x, pts[0].x) && near(m1.x, pts[pts.length - 1].x, 1e-9));
  assert.equal(leaderHead(pts, ARC.HEAD, ARC.HEAD_A), arcHead(pts), "the same two strokes as the map's arc");
  assert.equal(leaderHead([pts[0]], 10, 0.4), "");
});

test("the cost: a word under the arc or the pill dominates; off the box next; ink last", () => {
  const pts = leaderArc([0, 300], [600, 300], 0, 1, [0, 0]);   // a straight run along y 300
  const g = { words: [], ink: [], W: 1000, H: 560, pill: null, pad: 0 };
  assert.equal(leaderCost(pts, g), 0);
  assert.ok(leaderCost(pts, Object.assign({}, g, { words: [[100, 290, 150, 310]] })) >= LEADER.WORD_COST);
  const inkOnly = leaderCost(pts, Object.assign({}, g, { ink: [[100, 290, 150, 310]] }));
  assert.ok(inkOnly > 0 && inkOnly < LEADER.WORD_COST);
  assert.ok(leaderCost(pts, Object.assign({}, g, { W: 500 })) >= LEADER.EDGE_COST);
  const pb = leaderPillBox(pts, [60, 30]);
  assert.ok(near((pb[0] + pb[2]) / 2, 300, 1e-6) && near((pb[1] + pb[3]) / 2, 300, 1e-6), "the pill at the arc's half length");
  assert.ok(leaderCost(pts, Object.assign({}, g, { pill: [60, 30], words: [[280, 250, 320, 280]], pad: 6 })) >= LEADER.WORD_COST,
            "a pill on a word costs");
});

test("the side: the author's bend stands (s106); else the first clear candidate - up, then wider, then down", () => {
  const A = [700, 100, 800, 140], B = [200, 400];
  const up = leaderUp(leaderCentre(A), leaderCentre(B));
  const g = { words: [], ink: [], W: 1000, H: 560, pill: null, gaps: [0, 0] };
  assert.deepEqual([leaderChoose(A, B, g).sign, leaderChoose(A, B, g).bow], [up, LEADER.BOW], "nothing in the way: the arc's own bow, lifted");
  const high = leaderArc(A, B, LEADER.BOW, up, [0, 0]), m = leaderAlong(high, 0.5);
  const word = [m.x - 30, m.y - 30, m.x + 30, m.y + 30];   // a word right where the lifted arc runs
  const pick = leaderChoose(A, B, Object.assign({}, g, { words: [word] }));
  assert.equal(pick.cost, 0, "a clear candidate exists and is taken");
  assert.ok(!(pick.sign === up && pick.bow === LEADER.BOW), "the arc steps off the word");
  const forced = leaderChoose(A, B, Object.assign({}, g, { words: [word] }), 0.5 / LEADER.BEND_MAX);
  assert.equal(forced.authored, true);
  assert.equal(forced.sign, up);
  assert.ok(near(forced.bow, 0.5) && forced.cost >= LEADER.WORD_COST, "the authored bend stands on the word - reported by its cost, never moved");
  assert.equal(leaderChoose(A, B, g, -1).sign, -up, "a negative bend sags");
  assert.equal(leaderChoose(A, B, g, 0).bow, 0, "bend 0: straight");
});

// ---- the painter, with recorders and no DOM ----------------------------------------------------------------------------

const el = () => ({ a: {}, setAttribute(k, v) { this.a[k] = String(v); }, getAttribute(k) { return this.a[k]; } });

const built = (o = {}) => Object.assign({
  sp: sp(), g: el(), shaft: el(), head: { kind: "arrow", el: el() }, ring: null, pill: null, k: 2, words: [],
  pick: { sign: -1, bow: LEADER.BOW }, leave: null,
  fromShape: (st) => (st.noFrom ? null : [700, 100, 800, 140]),
  toShape: (st) => (st.noTo ? null : [200, 400]),
}, o);

test("the painter: hidden before its word; the shaft draws by length; whole at the word's end with its head", () => {
  const sd = built();
  paintLeader(sd, 9.9, {}, {});
  assert.equal(sd.g.a.opacity, "0");
  paintLeader(sd, 10 + 2 * 0.3, {}, {});
  assert.equal(sd.g.a.opacity, "1.000");
  const part = +sd.shaft.a["stroke-dashoffset"];
  assert.ok(part > 0 && part < 1, "part-way along its own length");
  assert.ok(sd.shaft.a.d.startsWith("M"), sd.shaft.a.d);
  paintLeader(sd, 12, {}, {});
  assert.equal(sd.shaft.a["stroke-dashoffset"], "0.0000");
  assert.equal(sd.head.el.a.opacity, "1.000");
  const tip = sd.shaft.a.d.trim().split(/[ML]/).filter(Boolean).pop().trim().split(/\s+/).map(Number);
  assert.ok(near(Math.hypot(tip[0] - 200, tip[1] - 400), LEADER.GAP_PX / 2, 0.01), "the tip stops GAP_PX (stage) short of the target: " + tip);
});

test("a dot head grows as it lands; a ring draws round the target and the tip stops at the ring", () => {
  const ring = { g: el(), rx: 60, ry: 40, dashes: [0, 1, 2, 3].map((i) => ({ p: el(), t0: i / 4, t1: (i + 1) / 4, box: [-5, -5, 5, 5] })) };
  const sd = built({ head: { kind: "dot", el: el() }, ring });
  paintLeader(sd, 12, {}, {});
  assert.equal(+sd.head.el.a.r, LEADER.DOT_PX / 2);
  assert.equal(ring.g.a.transform, "translate(200.0 400.0) scale(0.50000)", "the ring on the target's centre, 1/k");
  assert.ok(ring.dashes.every((d) => d.p.a.opacity === "1"));
  const tip = sd.shaft.a.d.trim().split(/[ML]/).filter(Boolean).pop().trim().split(/\s+/).map(Number);
  const r = Math.hypot((tip[0] - 200) / (60 / 2), (tip[1] - 400) / (40 / 2));
  assert.ok(r > 1, "the tip stands OUTSIDE the ring, never through it: " + r);
  const onWord = built({ ring: { g: el(), rx: 60, ry: 40, dashes: [{ p: el(), t0: 0, t1: 1, box: [-5, -5, 5, 5] }] }, words: [[195, 395, 205, 405]] });
  paintLeader(onWord, 12, {}, {});
  assert.equal(onWord.ring.dashes[0].p.a.opacity, "0", "a dash on the page's words stays undrawn (level_join's law)");
});

test("the pill rides the arc's middle and pops; an end the window dropped hides it; it leaves on its clock", () => {
  const sd = built({ pill: { g: el() } });
  paintLeader(sd, 10 + 2 * LEADER.LABEL[0] - 0.01, {}, {});
  assert.equal(sd.pill.g.a.opacity, "0");
  paintLeader(sd, 12, {}, {});
  assert.equal(sd.pill.g.a.opacity, "1");
  assert.match(sd.pill.g.a.transform, /^translate\([\d.]+ [\d.]+\) scale\(1\.0000\)$/);
  const gone = built();
  paintLeader(gone, 12, { noTo: true }, {});
  assert.equal(gone.g.a.opacity, "0");
  paintLeader(gone, 12, { noFrom: true }, {});
  assert.equal(gone.g.a.opacity, "0");
  const lv = built({ leave: { at: 20, dur: 1 } });
  paintLeader(lv, 20.5, {}, {});
  assert.equal(lv.g.a.opacity, "0.500");
  paintLeader(lv, 21.1, {}, {});
  assert.equal(lv.g.a.opacity, "0");
});
