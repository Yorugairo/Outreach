// P50 T4 - THE FLOW DIAGRAM (the Bravos flow diagram, shots 82-86). The whole diagram is a pure function of t,
// sp.at and sp.swap.at: the frame draws round, the chips land in order, the clothoid arrows draw one at a time
// by length, and on a LATER word ONE node un-draws and is replaced in the same spot while the arrows stand.
// These tests pin the schedule, the swap's two halves, the anchors the arrows are fitted to, and that nothing
// is remembered between calls.
import { test } from "node:test";
import assert from "node:assert/strict";
import { CHIP, chipLand } from "../../scripts/species/chip.mjs";
import { clothoid, clothoidAt, clothoidFit, curvatureOf } from "../../scripts/kinetics/clothoid.mjs";
import { FLOW, flowLayout, flowClock, flowBoxF, flowDashes, flowSwapPhase, flowNodeAt, flowPose,
         flowEdgeF, flowAnchors, flowHead, flowEdgeIndex, paintFlow,
         flowEdgePts, flowRingPoint, flowTokenStart, flowTokens, flowTokenSpeed, flowTokenStyle,
         flowFailIndex, flowFailAt, flowFailSplit, flowFailInk } from "../../scripts/species/flow.mjs";
import { springPop } from "../../scripts/kinetics/spring.mjs";

const near = (a, b, eps = 1e-9) => Math.abs(a - b) <= eps;
const BOX = { x: 200, y: 400, w: 1500, h: 420 };
const flow = (o = {}) => Object.assign({
  kind: "flow", at: 4, dur: 18, target: { kind: "region", x0: 0.1, y0: 0.37, x1: 0.9, y1: 0.76 },
  nodes: [{ id: "plant", icon: "factory", label: "PLANTS" },
          { id: "freight", icon: "ship", label: "FREIGHT" },
          { id: "price", icon: "coins", label: "PRICE" }],
  edges: [["plant", "freight"], ["freight", "price"]], tag: "1973",
}, o);
const SWAP = { at: 11, node: "freight", icon: "cpu", label: "CHIPS" };

test("the dials are the diagram's, and every clock is a real window", () => {
  for (const k of ["BOX_S", "NODE_STEP", "EDGE_S", "SWAP_OUT_S", "SWAP_IN_S", "TAG_S"]) assert.ok(FLOW[k] > 0, k);
  assert.ok(FLOW.BOX_LEAD > 0 && FLOW.BOX_LEAD < 1, "the first chip lands while the frame is still drawing");
  assert.ok(FLOW.ENTER_K > 0 && FLOW.ENTER_K < 1, "the two arrow tangents are UNEQUAL - equal ones are a circular arc");
  assert.ok(FLOW.SWAP_IN_S > FLOW.SWAP_OUT_S, "the eye lands on what arrived, not on what left");
  assert.ok(FLOW.MIN_K > 0 && FLOW.MIN_K < 1 && FLOW.DASH > FLOW.DASH_GAP);
});

// ---------------------------------------------------------------- the layout
test("three nodes stand in a ROW inside the box, at full size when the box has the room", () => {
  const lay = flowLayout(BOX, 3);
  assert.equal(lay.column, false);
  assert.equal(lay.k, 1, "a box this size needs no shrinking");
  assert.equal(lay.cells.length, 3);
  const xs = lay.cells.map((c) => c.x);
  assert.ok(xs[0] < xs[1] && xs[1] < xs[2], "in declaration order, left to right");
  assert.ok(near(xs[1] - xs[0], xs[2] - xs[1], 1e-9), "evenly pitched");
  for (const c of lay.cells) {
    assert.ok(c.x - lay.half > BOX.x && c.x + lay.half < BOX.x + BOX.w, "inside the box");
    assert.ok(c.y > BOX.y && c.y < BOX.y + BOX.h);
  }
  assert.ok(lay.cells[0].y < BOX.y + BOX.h / 2, "the card sits above centre - the label hangs beneath it");
});

test("a box taller than it is wide lays the nodes out as a COLUMN (a portrait build's box is)", () => {
  const lay = flowLayout({ x: 100, y: 200, w: 700, h: 1500 }, 3);
  assert.equal(lay.column, true);
  const ys = lay.cells.map((c) => c.y);
  assert.ok(ys[0] < ys[1] && ys[1] < ys[2]);
  assert.ok(lay.cells.every((c) => c.x === 450), "one column, centred in the box");
});

test("a box too small for the cards shrinks the whole diagram rather than overlapping them", () => {
  const tight = flowLayout({ x: 0, y: 0, w: 600, h: 240 }, 3);
  assert.ok(tight.k < 1 && tight.k >= FLOW.MIN_K, tight.k);
  assert.ok(tight.half * 2 < 600 / 3, "the cards no longer touch");
  const absurd = flowLayout({ x: 0, y: 0, w: 60, h: 30 }, 6);
  assert.equal(absurd.k, FLOW.MIN_K, "and it never shrinks past the floor - that box was a mistake, not a diagram");
});

// ---------------------------------------------------------------- the schedule
test("THE NODE LANDING ORDER: the frame starts, then one chip after another, NODE_STEP apart", () => {
  const sp = flow(), C = flowClock(sp);
  assert.deepEqual(C.box, [4, 4 + FLOW.BOX_S]);
  assert.ok(near(C.nodeAt[0], sp.at + FLOW.BOX_S * FLOW.BOX_LEAD));
  assert.ok(C.nodeAt[0] > C.box[0] && C.nodeAt[0] < C.box[1], "the first chip lands while the frame is drawing");
  for (let i = 1; i < 3; i++) assert.ok(near(C.nodeAt[i] - C.nodeAt[i - 1], FLOW.NODE_STEP), i);
  assert.ok(near(C.landed, C.nodeAt[2] + CHIP.LAND_S));
  assert.ok(near(flowBoxF(sp, sp.at), 0) && near(flowBoxF(sp, sp.at + FLOW.BOX_S), 1));
  assert.equal(flowBoxF(sp, sp.at - 1), 0);
  assert.equal(flowBoxF(sp, sp.at + 99), 1);
});

test("THE ARROW DRAW FRACTION PER EDGE: one arrow at a time, EDGE_S each, after the last chip has landed", () => {
  const sp = flow(), C = flowClock(sp);
  assert.equal(C.edgeAt.length, 2);
  assert.ok(near(C.edgeAt[0], C.landed + FLOW.EDGE_LAG), "a breath after the last landing");
  assert.ok(near(C.edgeAt[1] - C.edgeAt[0], FLOW.EDGE_S), "one per EDGE_S, in declaration order");
  for (let j = 0; j < 2; j++) {
    assert.equal(flowEdgeF(sp, j, C.edgeAt[j] - 0.001), 0);
    assert.ok(near(flowEdgeF(sp, j, C.edgeAt[j] + FLOW.EDGE_S / 2), 0.5));
    assert.ok(near(flowEdgeF(sp, j, C.edgeAt[j] + FLOW.EDGE_S), 1, 1e-12));
    assert.equal(flowEdgeF(sp, j, 99), 1);
  }
  assert.ok(near(flowEdgeF(sp, 0, C.edgeAt[1]), 1, 1e-12), "the first arrow is in before the second leaves");
  assert.ok(near(C.tagAt, C.edgeAt[1] + FLOW.EDGE_S + FLOW.TAG_LAG), "the year stamps last");
});

test("the frame is drawn as DASHES round the perimeter, each stopping at the corner it reaches", () => {
  const d = flowDashes(BOX);
  assert.ok(d.length > 8);
  for (let i = 0; i < d.length; i++) {
    assert.ok(near(d[i].t0, i / d.length, 1e-12) && near(d[i].t1, (i + 1) / d.length, 1e-12), "in order round the box");
    const len = Math.hypot(d[i].b.x - d[i].a.x, d[i].b.y - d[i].a.y);
    assert.ok(len > 0 && len <= FLOW.DASH + 1e-9, `dash ${i} is ${len}`);
    for (const p of [d[i].a, d[i].b]) {   // a dash that cut a corner would leave the box's own edges
      const onV = near(p.x, BOX.x) || near(p.x, BOX.x + BOX.w), onH = near(p.y, BOX.y) || near(p.y, BOX.y + BOX.h);
      assert.ok(onV || onH, `dash ${i} has an end off the box: ${JSON.stringify(p)}`);
    }
    assert.ok(near(d[i].a.x, d[i].b.x) || near(d[i].a.y, d[i].b.y), `dash ${i} cuts a corner`);
  }
  assert.ok(near(d[0].a.x, BOX.x) && near(d[0].a.y, BOX.y), "the nib starts at the top-left, as a hand would");
});

// ---------------------------------------------------------------- the swap (Bravos's rhyme)
test("THE SWAP: the standing node's landing runs BACKWARD, then the new one's runs forward in the same spot", () => {
  const sp = flow({ swap: SWAP });
  const at = (t) => flowNodeAt(sp, 1, t);
  const before = at(SWAP.at - 0.01);
  assert.deepEqual([before.icon, before.label, before.u, before.alpha, before.swapping], ["ship", "FREIGHT", 1, 1, false]);
  const out0 = at(SWAP.at), outH = at(SWAP.at + FLOW.SWAP_OUT_S / 2);
  assert.equal(out0.icon, "ship", "the old glyph is still the one un-drawing");
  assert.ok(near(out0.u, 1) && near(out0.alpha, 1));
  assert.ok(near(outH.u, 0.5) && near(outH.alpha, 0.5), "half out: the landing half run back, the ink half gone");
  assert.equal(outH.swapping, true);
  const in0 = at(SWAP.at + FLOW.SWAP_OUT_S), inH = at(SWAP.at + FLOW.SWAP_OUT_S + FLOW.SWAP_IN_S / 2);
  assert.equal(in0.icon, "cpu", "the new glyph owns the spot the moment the old one is gone");
  assert.ok(near(in0.u, 0));
  assert.ok(near(inH.u, 0.5) && inH.label === "CHIPS" && near(inH.alpha, 1));
  const done = at(SWAP.at + FLOW.SWAP_OUT_S + FLOW.SWAP_IN_S + 5);
  assert.deepEqual([done.icon, done.label, done.u, done.alpha, done.swapping], ["cpu", "CHIPS", 1, 1, false]);
});

test("... and THE REST STANDS: no other node moves, and no arrow is redrawn", () => {
  const sp = flow({ swap: SWAP });
  for (const t of [SWAP.at - 0.01, SWAP.at + 0.15, SWAP.at + 0.4, SWAP.at + 3]) {
    for (const i of [0, 2]) {
      const n = flowNodeAt(sp, i, t);
      assert.deepEqual([n.u, n.alpha, n.swapping], [1, 1, false], `node ${i} at ${t}`);
      assert.equal(n.icon, sp.nodes[i].icon);
    }
    assert.equal(flowEdgeF(sp, 0, t), 1);
    assert.equal(flowEdgeF(sp, 1, t), 1);
  }
});

test("a diagram with no swap never changes, and a swap naming no node changes nothing either", () => {
  const plain = flow();
  assert.deepEqual(flowSwapPhase(plain, 99), { phase: "none", u: 1 });
  const n = flowNodeAt(plain, 1, 99);
  assert.deepEqual([n.icon, n.u, n.alpha], ["ship", 1, 1]);
  const other = flow({ swap: Object.assign({}, SWAP, { node: "nobody" }) });
  for (let i = 0; i < 3; i++) assert.equal(flowNodeAt(other, i, 99).icon, other.nodes[i].icon);
});

test("the landing IS the chip's: flowPose(u) is chipLand at that u, so a node and a lone chip land alike", () => {
  for (let i = 0; i <= 20; i++) {
    const u = i / 20, a = flowPose(u), b = chipLand(u * CHIP.LAND_S, 0);
    assert.ok(near(a.scale, b.scale) && near(a.dy, b.dy) && near(a.fade, b.fade), `u=${u}`);
  }
  assert.deepEqual(flowPose(-3), flowPose(0));
  assert.deepEqual(flowPose(9), flowPose(1));
});

// ---------------------------------------------------------------- the arrows
test("an arrow leaves one card's EDGE and enters the next's, on two UNEQUAL tangents", () => {
  const lay = flowLayout(BOX, 3), a = lay.cells[0], b = lay.cells[1];
  const an = flowAnchors(a, b, lay.half);
  assert.ok(an.p0.x > a.x + lay.half, "it starts clear of the first card");
  assert.ok(an.p1.x < b.x - lay.half, "and stops clear of the second");
  /* the air is EDGE_GAP along the TANGENT it leaves on, not along x - the exit is turned off the chord */
  const sq = (th) => lay.half / Math.max(Math.abs(Math.cos(th)), Math.abs(Math.sin(th)));
  assert.ok(near(Math.hypot(an.p0.x - a.x, an.p0.y - a.y) - sq(an.t0), FLOW.EDGE_GAP, 1e-9), "EDGE_GAP clear of the square");
  assert.ok(near(Math.hypot(an.p1.x - b.x, an.p1.y - b.y) - sq(an.t1 + Math.PI), FLOW.EDGE_GAP, 1e-9));
  assert.ok(Math.abs(an.t0 - an.chord) > 0 && Math.abs(an.t1 - an.chord) > 0, "both tangents are turned off the chord");
  assert.notEqual(Math.abs(an.t0 - an.chord).toFixed(6), Math.abs(an.t1 - an.chord).toFixed(6));
  /* and the fitter accepts them: one clothoid, curvature a straight line in s and never changing sign */
  const fit = clothoidFit(an.p0, an.t0, an.p1, an.t1);
  assert.ok(fit.ok);
  assert.ok(Math.abs(fit.dk) > 1e-6, "a real clothoid, not a circular arc - the RAMP is the point (42 s42.4); equal tangents would give A = 0");
  /* and the ramp is what the doc promises: curvature a straight line in arclength, measured on the drawn samples.
     The arrow's last quarter bends the other way - that is the settle INTO the second card, one gentle inflection
     on a monotone dk/ds, not the cubic's ripple. */
  const pts = [], N = 120;
  for (let i = 0; i < N; i++) pts.push(clothoidAt(fit, i / (N - 1)));
  const k = curvatureOf(pts);
  let worst = 0;
  for (let i = 1; i < N - 1; i++) worst = Math.max(worst, Math.abs(k[i] - pts[i].k));
  assert.ok(worst < 1e-7, `measured vs analytic curvature on the arrow: ${worst}`);
  for (let i = 2; i < N - 1; i++) assert.ok(k[i] <= k[i - 1] + 1e-9, `the arrow's curvature is not monotone at ${i}`);
});

test("the arrowhead sits at the polyline's far end, along the tangent it arrives on", () => {
  const pts = [{ x: 0, y: 0 }, { x: 100, y: 0 }, { x: 200, y: 0 }];
  const d = flowHead(pts);
  assert.match(d, /^M[\d.-]+ [\d.-]+ L200\.00 0\.00 L/);
  assert.ok(!/NaN/.test(d));
  assert.equal(flowHead([{ x: 1, y: 1 }]), "", "one point is not a direction");
});

test("the edges are resolved BY NAME, and a name that is not a node is dropped rather than drawn wrong", () => {
  assert.deepEqual(flowEdgeIndex(flow()), [[0, 1], [1, 2]]);
  assert.deepEqual(flowEdgeIndex(flow({ edges: [["price", "plant"], ["ghost", "plant"]] })), [[2, 0], [-1, 0]]);
  assert.deepEqual(flowEdgeIndex({ nodes: [], edges: [["a", "b"]] }), [[-1, -1]]);
});

// ---------------------------------------------------------------- pure function of t
test("a seek IS the play: the same t gives the same bits, in any order, with nothing remembered", () => {
  const sp = flow({ swap: SWAP });
  const read = (t) => JSON.stringify([flowClock(sp), [0, 1, 2].map((i) => flowNodeAt(sp, i, t)), [0, 1].map((j) => flowEdgeF(sp, j, t)), flowBoxF(sp, t)]);
  const forward = [], backward = [];
  for (let i = 0; i <= 400; i++) forward.push(read(i / 25));
  for (let i = 400; i >= 0; i--) backward.unshift(read(i / 25));
  assert.deepEqual(backward, forward);
  assert.equal(read(11.08), forward[277]);
});

test("nothing in the module reaches for a clock or a random", () => {
  const src = [paintFlow, flowClock, flowNodeAt, flowEdgeF, flowLayout, flowAnchors, flowDashes].map((f) => f.toString()).join("\n");
  assert.ok(!/Math\.random|Date\.now|new Date|performance\./.test(src), src);
});

// ---------------------------------------------------------------- the painter, on a stub surface
const stub = (sp, t, target) => {
  const made = [];
  const el = (tag, cls, parent, at) => { const e = { tag, cls, at: at || {}, kids: [], textContent: "", setAttribute(k, v) { this.at[k] = v; }, getAttribute(k) { return this.at[k]; } };
    made.push(e); if (parent && parent.kids) parent.kids.push(e); return e; };
  const geo = JSON.stringify({ vb: [0, 0, 24, 24], el: [{ t: "path", a: { d: "M12 16h.01" } }] });
  const ctx = { sp, t, svg: { kids: [] }, el, A: { "icon:factory": geo, "icon:ship": geo, "icon:coins": geo, "icon:cpu": geo },
    resolveTarget: () => target, drawOn: (p, k) => p.setAttribute("stroke-dashoffset", k.toFixed(3)),
    hash: () => 0.5, idle: () => ({ scale: 1, dx: 0, dy: 0 }), seed: 1, si: 0 };
  paintFlow(ctx);
  return made;
};

test("the painter draws nothing without a resolved REGION, and the whole diagram with one", () => {
  const sp = flow({ swap: SWAP });
  assert.equal(stub(sp, 12, null).length, 0, "the targeting law: no room declared, nothing painted");
  assert.equal(stub(sp, 12, { x: 0, y: 0, w: 0, h: 0 }).length, 0, "a point is not a room");
  const made = stub(sp, 12, BOX);
  assert.ok(made.filter((e) => e.cls === "flowbox").length > 8, "the frame's dashes");
  assert.equal(made.filter((e) => e.cls === "flowarrow").length, 4, "two arrows and two heads");
  assert.equal(made.filter((e) => e.cls === "chipcard").length, 3, "three cards");
  assert.equal(made.filter((e) => e.cls === "chiplab").map((e) => e.textContent).join("|"), "PLANTS|CHIPS|PRICE");
  assert.equal(made.filter((e) => e.cls === "flowtag")[0].textContent, "1973");
});

test("the painter shows the diagram mid-build, and the swapped card at its own opacity", () => {
  const sp = flow({ swap: SWAP }), C = flowClock(sp);
  const half = stub(sp, C.edgeAt[0] + FLOW.EDGE_S / 2, BOX).filter((e) => e.cls === "flowarrow");
  assert.equal(half.length, 1, "the second arrow has not left yet");
  assert.ok(+half[0].at["stroke-dashoffset"] > 0 && +half[0].at["stroke-dashoffset"] < 1, "the first is drawing");
  const mid = stub(sp, SWAP.at + FLOW.SWAP_OUT_S / 2, BOX).filter((e) => e.tag === "g" && e.at.opacity !== undefined);
  const ops = mid.map((e) => +e.at.opacity);
  assert.ok(ops.some((v) => near(v, 0.5, 0.01)), `the un-drawing card is half gone: ${ops}`);
  assert.equal(ops.filter((v) => v > 0.99).length, 2, "the other two stand at full");
});

// ---------------------------------------------------------------- P71 T11: the ring and the tokens
const RING_BOX = { x: 480, y: 130, w: 960, h: 900 };
const IDS4 = ["capex", "chips", "cloud", "profit"];
const loop = (n = 4, o = {}) => {
  const ids = IDS4.concat(["rates", "banks"]).slice(0, n);
  return flow(Object.assign({ layout: "ring", tag: undefined,
    nodes: ids.map((id) => ({ id, icon: "factory", label: id.toUpperCase() })),
    edges: ids.map((id, i) => [id, ids[(i + 1) % n]]), tokens: { from_at: 9, n: 2 } }, o));
};
const inCard = (p, c, half) => Math.abs(p.x - c.x) < half && Math.abs(p.y - c.y) < half;
/* ... or in the label under it, down to its baseline (CHIP.LABEL_DY below the card), the label no wider than the card */
const inLabel = (p, c, lay) => Math.abs(p.x - c.x) < lay.half && p.y >= c.y + lay.half && p.y <= c.y + lay.half + CHIP.LABEL_DY * lay.k;
const wrap = (a) => Math.atan2(Math.sin(a), Math.cos(a));

test("THE RING: n nodes on the ellipse inscribed in the box, the first at 12 o'clock, the rest clockwise at equal angles", () => {
  for (const n of [3, 4, 5, 6]) {
    const lay = flowLayout(RING_BOX, n, { layout: "ring" });
    assert.equal(lay.ring, true);
    assert.equal(lay.cells.length, n);
    assert.ok(near(lay.cells[0].x, RING_BOX.x + RING_BOX.w / 2, 1e-9), "the first at 12 o'clock");
    const lift = lay.cells[0].y - flowRingPoint(lay, 0, n).y;
    lay.cells.forEach((c, i) => {   /* every cell is its ring point lifted by the same share - card + label centre on the ring */
      const p = flowRingPoint(lay, i, n);
      assert.ok(near(c.x, p.x, 1e-9) && near(c.y - p.y, lift, 1e-9), `node ${i} on the ring`);
      assert.ok(c.x - lay.half >= RING_BOX.x && c.x + lay.half <= RING_BOX.x + RING_BOX.w, `node ${i} inside the box`);
      assert.ok(c.y - lay.half >= RING_BOX.y && c.y + lay.half <= RING_BOX.y + RING_BOX.h, `node ${i} inside the box`);
    });
    /* clockwise on screen: the signed area of the polygon (y down) is positive */
    let area = 0;
    lay.cells.forEach((a, i) => { const b = lay.cells[(i + 1) % n]; area += a.x * b.y - b.x * a.y; });
    assert.ok(area > 0, `clockwise (n ${n})`);
  }
});

test("a ring in a box too small for it shrinks the diagram, never below MIN_K, and its nodes never overlap", () => {
  const big = flowLayout(RING_BOX, 4, { layout: "ring" }), small = flowLayout({ x: 0, y: 0, w: 520, h: 480 }, 6, { layout: "ring" });
  assert.equal(big.k, 1);
  assert.ok(small.k < 1 && small.k >= FLOW.MIN_K, `k ${small.k}`);
  for (let i = 0; i < 6; i++) for (let j = i + 1; j < 6; j++) {
    const a = small.cells[i], b = small.cells[j];
    assert.ok(Math.hypot(a.x - b.x, a.y - b.y) >= 2 * small.half, `cards ${i} and ${j} apart`);
  }
  assert.equal(flowLayout({ x: 0, y: 0, w: 60, h: 60 }, 5, { layout: "ring" }).k, FLOW.MIN_K, "the floor, as the row's");
});

test("a ring arrow leaves its card ALONG the ring (its bow is the ring's tangent) and crosses no card and no label, n 3-6, wide and tall", () => {
  for (const box of [RING_BOX, { x: 150, y: 420, w: 1620, h: 600 }, { x: 300, y: 80, w: 700, h: 920 }]) {
    for (const n of [3, 4, 5, 6]) {
      const lay = flowLayout(box, n, { layout: "ring" });
      for (let i = 0; i < n; i++) {
        const j = (i + 1) % n, a = lay.cells[i], b = lay.cells[j];
        const an = flowAnchors(a, b, lay.half, lay.bows[i]);
        assert.ok(near(wrap(an.t0 - flowRingPoint(lay, i, n).tangent), 0, 1e-9), "the tangent");
        assert.ok(lay.bows[i] > 0, `the arrow bows OUTWARD (n ${n}, edge ${i}: ${lay.bows[i]})`);
        const pts = flowEdgePts(lay, i, j);
        for (const p of pts) lay.cells.forEach((c, m) => assert.ok(!inCard(p, c, lay.half) && !inLabel(p, c, lay),
          `STOP CONDITION: box ${JSON.stringify(box)} n ${n} edge ${i}->${j} (bow ${lay.bows[i].toFixed(3)} rad) crosses card ${m} or its label`));
      }
    }
  }
});

test("off a ring, flowEdgePts is the arrow the painter always drew (FLOW.BOW, the same anchors, the same fit)", () => {
  const lay = flowLayout(BOX, 3);
  const an = flowAnchors(lay.cells[0], lay.cells[1], lay.half);
  assert.deepEqual(flowEdgePts(lay, 0, 1), clothoid(an.p0, an.t0, an.p1, an.t1, FLOW.SAMPLES));
  assert.deepEqual(flowAnchors(lay.cells[0], lay.cells[1], lay.half), flowAnchors(lay.cells[0], lay.cells[1], lay.half, FLOW.BOW, 0));
  const ring = flowLayout(RING_BOX, 4, { layout: "ring" }), down = flowAnchors(ring.cells[1], ring.cells[2], ring.half, ring.bows[1], ring.below);
  assert.ok(down.p0.y > ring.cells[1].y + ring.half + CHIP.LABEL_DY, "the 3 o'clock arrow leaves BELOW its label");
});

test("THE TOKENS wait for from_at AND for their own arrow to be drawn", () => {
  const sp = loop(4, { tokens: { from_at: 6.2, n: 2 } }), C = flowClock(sp), lay = flowLayout(RING_BOX, 4, { layout: "ring" });
  assert.ok(C.edgeAt[0] + FLOW.EDGE_S < 6.2 && 6.2 < C.edgeAt[1] + FLOW.EDGE_S, "the fixture's from_at falls inside the arrows' own draw");
  sp.edges.forEach((_, j) => assert.equal(flowTokenStart(sp, j), Math.max(6.2, C.edgeAt[j] + FLOW.EDGE_S)));
  assert.deepEqual(flowTokens(sp, 6.199, lay), [], "nothing before from_at");
  const t = C.edgeAt[1] + FLOW.EDGE_S + 0.2, edges = new Set(flowTokens(sp, t, lay).map((k) => k.edge));
  assert.ok(edges.has(0) && edges.has(1) && !edges.has(2) && !edges.has(3), `only drawn arrows carry tokens: ${[...edges]}`);
  assert.deepEqual(flowTokens(flow(), 20, lay), [], "no tokens declared, none drawn");
  assert.equal(flowTokenStart(flow(), 0), Infinity);
});

test("a token moves at ONE speed per unit of arc, the n tokens a 1/n lap apart, and wraps to the tail at the head", () => {
  const sp = loop(4, { tokens: { from_at: 9, n: 3, speed: 200 } }), lay = flowLayout(RING_BOX, 4, { layout: "ring" });
  const v = flowTokenSpeed(sp, lay);
  assert.ok(v > 0 && v <= 200, `the one speed ${v}`);
  const t0 = flowTokenStart(sp, 0), L = flowTokens(sp, t0 + 0.01, lay).find((k) => k.edge === 0).L;
  const at = (t) => flowTokens(sp, t, lay).filter((k) => k.edge === 0);
  const a = at(t0 + 0.3).find((k) => k.i === 0), b = at(t0 + 0.7).find((k) => k.i === 0);
  assert.ok(near(b.s - a.s, v * 0.4, 1e-9), `constant speed by arc: ${b.s - a.s}`);
  assert.equal(at(t0 + 0.9 * L / v / 3).length, 1, "token 1 has not left the tail yet");
  const steady = at(t0 + 2.5 * L / v);
  assert.equal(steady.length, 3);
  const ss = steady.map((k) => k.s).sort((x, y) => x - y);
  assert.ok(near(ss[1] - ss[0], L / 3, 1e-6) && near(ss[2] - ss[1], L / 3, 1e-6), `evenly spaced: ${ss}`);
  const lapped = at(t0 + 1.25 * L / v).find((k) => k.i === 0);
  assert.equal(lapped.lap, 1);
  assert.ok(near(lapped.u, 0.25, 1e-9), "back from the tail");
});

test("a token fades in off the tail and out into the head, full in between; its point lies ON its arrow", () => {
  const sp = loop(4, { tokens: { from_at: 9, n: 1, speed: 200 } }), lay = flowLayout(RING_BOX, 4, { layout: "ring" });
  const t0 = flowTokenStart(sp, 0), L = flowTokens(sp, t0, lay).find((k) => k.edge === 0).L, v = flowTokenSpeed(sp, lay);
  const tok = (u) => flowTokens(sp, t0 + u * L / v, lay).find((k) => k.edge === 0);
  assert.equal(tok(0).alpha, 0);
  assert.ok(near(tok(FLOW.TOKEN_FADE / 2).alpha, 0.5, 1e-6));
  assert.equal(tok(0.5).alpha, 1);
  assert.ok(near(tok(1 - FLOW.TOKEN_FADE / 2).alpha, 0.5, 1e-6));
  const pts = flowEdgePts(lay, 0, 1), m = tok(0.5);
  const d = Math.min(...pts.slice(1).map((q, i) => { const p = pts[i], vx = q.x - p.x, vy = q.y - p.y;
    const u = Math.max(0, Math.min(1, ((m.x - p.x) * vx + (m.y - p.y) * vy) / (vx * vx + vy * vy)));
    return Math.hypot(m.x - p.x - u * vx, m.y - p.y - u * vy); }));
  assert.ok(d < 1e-6, `on the polyline: ${d}`);
});

test("the tokens are a pure function of t: a seek IS the play, in any order, with nothing remembered", () => {
  const sp = loop(), lay = flowLayout(RING_BOX, 4, { layout: "ring" }), ts = [14.2, 10.1, 12.73, 10.1, 14.2];
  const once = ts.map((t) => JSON.stringify(flowTokens(sp, t, lay)));
  assert.equal(once[0], once[4]);
  assert.equal(once[1], once[3]);
  const src = [flowTokens, flowTokenStart, flowEdgePts, flowRingPoint].map((f) => f.toString()).join("\n");
  assert.ok(!/Math\.random|Date\.now|new Date|performance\./.test(src));
});

test("the painter lays a ring flow on its ring and draws each token as a plain DOT in the arrow's ink", () => {
  const sp = loop(), t = flowTokenStart(sp, 3) + 0.9;
  const made = stub(sp, t, RING_BOX), lay = flowLayout(RING_BOX, 4, { layout: "ring" });
  const cards = made.filter((e) => e.tag === "g" && /translate/.test(e.at.transform || "") && e.at.opacity !== undefined && !e.cls);
  assert.equal(cards.length, 4);
  cards.forEach((g, i) => { const [x, y] = g.at.transform.match(/translate\(([-\d.]+) ([-\d.]+)\)/).slice(1).map(Number);
    assert.ok(Math.abs(x - lay.cells[i].x) < 0.06 && Math.abs(y - lay.cells[i].y) < 0.06, `card ${i} on its ring cell`); });
  assert.equal(made.filter((e) => e.cls === "flowarrow").length, 8, "four arrows, four heads");
  const dots = made.filter((e) => e.cls === "flowtoken");
  const live = flowTokens(sp, t, lay).filter((k) => k.alpha > 0);
  assert.equal(dots.length, live.length);
  assert.ok(dots.length >= 4);
  dots.forEach((d) => { assert.equal(d.tag, "circle"); assert.equal(d.at.style, flowTokenStyle(lay.k, false));
    assert.equal(+d.at.r, +(FLOW.TOKEN_R * lay.k).toFixed(2)); });
  assert.match(dots[0].at.style, /^fill:#F2F2F2;stroke:#F5B72E;stroke-width:5\.00;filter:drop-shadow\(0 0 10\.00px rgba\(245,183,46,0\.55\)\)$/,
    "a chalk core, the arrow ink as its rim, lpBloom's halo");
  assert.ok(made.indexOf(dots[0]) < made.findIndex((e) => e.cls === "chipcard"), "under the cards");
});

test("a named glyph token draws the SOURCED icon, and a flow without tokens draws none", () => {
  const sp = loop(4, { tokens: { from_at: 9, glyph: "coins" } }), t = flowTokenStart(sp, 3) + 0.9;
  const made = stub(sp, t, RING_BOX), toks = made.filter((e) => e.cls === "flowtoken");
  assert.ok(toks.length > 0 && toks.every((e) => e.tag === "g" && /stroke:#F5B72E/.test(e.at.style)));
  assert.ok(toks.every((e) => e.kids.length === 1 && e.kids[0].at.d === "M12 16h.01"), "the geometry verbatim");
  const plain = loop();
  delete plain.tokens;
  assert.equal(stub(plain, t, RING_BOX).filter((e) => e.cls === "flowtoken").length, 0);
  assert.equal(stub(loop(4, { operators: ["-", "-", "-", "-"] }), t, RING_BOX).filter((e) => e.cls === "flowtoken").length, 0,
    "an operator row carries none (the compiler refuses the pair)");
});

test("the token READS as a thing on the arrow: six arrow strokes across, a chalk core lighter than the arrow ink, the ink as its rim", () => {
  assert.ok(2 * FLOW.TOKEN_R >= 2.5 * 5, "the parent's floor: >= 2.5 x the 5 px arrow stroke");
  assert.ok(2 * FLOW.TOKEN_R / 5 >= 6, `${2 * FLOW.TOKEN_R / 5} strokes across`);
  const lum = (hex) => { const c = [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16) / 255)
    .map((v) => (v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4)); return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]; };
  assert.ok(lum(FLOW.TOKEN_CORE) > lum(FLOW.TOKEN_INK), "the core is lighter than its rim");
  assert.equal(FLOW.TOKEN_RIM, 5, "the rim at the arrow's own width");
  assert.equal(flowTokenStyle(1, true), "fill:#F4E6C7;stroke:#25313C;stroke-width:5.00", "phone: cream core, charcoal rim, no halo");
});

test("no arrow is crossed in under TOKEN_MIN_CROSS_S: the one speed is capped by the SHORTEST arrow, and a slower row keeps its own", () => {
  const lay = flowLayout(RING_BOX, 4, { layout: "ring" }), fast = loop(4, { tokens: { from_at: 9, speed: 900 } });
  const Ls = [0, 1, 2, 3].map((j) => { const t = flowTokenStart(fast, j) + 0.001; return flowTokens(fast, t, lay).find((k) => k.edge === j).L; });
  const v = flowTokenSpeed(fast, lay);
  assert.ok(near(v, Math.min(...Ls) / FLOW.TOKEN_MIN_CROSS_S, 1e-9), `capped: ${v}`);
  Ls.forEach((L) => assert.ok(L / v >= FLOW.TOKEN_MIN_CROSS_S - 1e-9, `an arrow of ${L} px in ${L / v} s`));
  assert.equal(FLOW.TOKEN_MIN_CROSS_S, 0.49, "the floor is Bravos DOM 03:27's fastest measured edge crossing, never our own read");
  const slow = loop(4, { tokens: { from_at: 9, speed: 60 } });
  assert.equal(flowTokenSpeed(slow, lay), 60, "the row's own slower speed stands");
  assert.equal(flowTokenSpeed(slow, null), 60);
});

// ---------------------------------------------------------------- P71 T17: the hub and the failed link
const HUB_BOX = { x: 480, y: 90, w: 960, h: 930 };
const RIMS = ["b1", "b2", "b3", "b4", "b5", "b6", "b7", "b8"];
const hubFlow = (rim = 4, o = {}) => flow(Object.assign({ layout: "hub", tag: undefined,
  nodes: [{ id: "market", icon: "coins", label: "MARKET" }].concat(RIMS.slice(0, rim).map((id) => ({ id, icon: "factory", label: id.toUpperCase() }))),
  edges: RIMS.slice(0, rim).map((id) => ["market", id]) }, o));

test("THE HUB: node 0 at the box's centre, the rim on T11's ellipse - the first at 12 o'clock, clockwise - 3 to 8 of them, none overlapping", () => {
  for (const box of [HUB_BOX, { x: 150, y: 300, w: 1620, h: 720 }, { x: 300, y: 60, w: 760, h: 960 }]) {
    for (let rim = 3; rim <= 8; rim++) {
      const lay = flowLayout(box, rim + 1, { layout: "hub" });
      assert.equal(lay.hub, true);
      assert.equal(lay.cells.length, rim + 1);
      const lift = (box.y + box.h / 2) - lay.cells[0].y;
      assert.ok(near(lay.cells[0].x, box.x + box.w / 2, 1e-9) && lift > 0, "the hub at the centre, card + label centred on it");
      assert.ok(near(lay.cells[1].x, lay.cells[0].x, 1e-9) && lay.cells[1].y < lay.cells[0].y, "the first rim node at 12 o'clock");
      lay.cells.slice(1).forEach((c, i) => {
        const p = flowRingPoint(lay, i, rim);
        assert.ok(near(c.x, p.x, 1e-9) && near(c.y + lift, p.y, 1e-9), `rim ${i} on the ring, lifted as the hub is`);
        assert.ok(c.x - lay.half >= box.x - 1e-9 && c.x + lay.half <= box.x + box.w + 1e-9 && c.y - lay.half >= box.y - 1e-9, `rim ${i} inside the box`);
      });
      let area = 0;
      const r = lay.cells.slice(1);
      r.forEach((a, i) => { const b = r[(i + 1) % rim]; area += a.x * b.y - b.x * a.y; });
      assert.ok(area > 0, `clockwise (rim ${rim})`);
      for (let i = 0; i <= rim; i++) for (let j = i + 1; j <= rim; j++) {
        const a = lay.cells[i], b = lay.cells[j];
        assert.ok(Math.abs(a.x - b.x) >= 2 * lay.half || Math.abs(a.y - b.y) >= 2 * lay.half, `cards ${i} and ${j} apart (rim ${rim})`);
      }
      assert.ok(lay.k >= FLOW.MIN_K && lay.k <= 1);
    }
  }
});

test("a SPOKE is straight - no bow, so a set of spokes never reads as a pinwheel - and crosses no card and no label, rim 3-8", () => {
  for (const box of [HUB_BOX, { x: 150, y: 300, w: 1620, h: 720 }]) {
    for (let rim = 3; rim <= 8; rim++) {
      const lay = flowLayout(box, rim + 1, { layout: "hub" });
      for (let i = 1; i <= rim; i++) for (const [a, b] of [[0, i], [i, 0]]) {
        const pts = flowEdgePts(lay, a, b), p0 = pts[0], p1 = pts[pts.length - 1];
        const dev = Math.max(...pts.map((p) => Math.abs((p1.x - p0.x) * (p.y - p0.y) - (p1.y - p0.y) * (p.x - p0.x)) / Math.hypot(p1.x - p0.x, p1.y - p0.y)));
        assert.ok(dev < 0.01, `spoke ${a}->${b} straight (${dev})`);
        for (const p of pts) lay.cells.forEach((c, m) => assert.ok(!inCard(p, c, lay.half) && !inLabel(p, c, lay),
          `box ${JSON.stringify(box)} rim ${rim} spoke ${a}->${b} crosses card ${m} or its label`));
      }
    }
  }
});

test("THE HUB'S CLOCK: the hub lands first; unnamed spokes draw together (Bravos DOM 04:22); a named rim word draws its spoke then lands its node (out) or lands its node then draws its spoke (in)", () => {
  const sp = hubFlow(4), C = flowClock(sp), first = sp.at + FLOW.BOX_S * FLOW.BOX_LEAD, D = first + CHIP.LAND_S + FLOW.EDGE_LAG;
  assert.equal(C.hub, true);
  assert.ok(near(C.nodeAt[0], first, 1e-12));
  C.edgeAt.forEach((a) => assert.ok(near(a, D, 1e-12), "every unnamed spoke on the same instant"));
  C.nodeAt.slice(1).forEach((a) => assert.ok(near(a, D + FLOW.EDGE_S, 1e-12), "each rim node lands as its spoke arrives"));
  const named = hubFlow(4, { edges: [["market", "b1"], ["b2", "market"], ["market", "b3"], ["b4", "market"]] });
  named.nodes[1].at = 7.0; named.nodes[2].at = 7.8;
  const N = flowClock(named);
  assert.ok(near(N.edgeAt[0], 7.0, 1e-12) && near(N.nodeAt[1], 7.0 + FLOW.EDGE_S, 1e-12), "out: the spoke on the word, the node at its end");
  assert.ok(near(N.nodeAt[2], 7.8, 1e-12) && near(N.edgeAt[1], 7.8 + FLOW.EDGE_S, 1e-12), "in: the node on the word, then its spoke");
  assert.ok(near(N.edgeAt[3], D + FLOW.EDGE_S, 1e-12) && near(N.nodeAt[4], D, 1e-12), "an unnamed inward rim takes the default word");
  assert.ok(near(N.tagAt, Math.max(...N.edgeAt) + FLOW.EDGE_S + FLOW.TAG_LAG, 1e-12));
  assert.ok(near(flowEdgeF(named, 0, 7.0 + FLOW.EDGE_S / 2), 0.5, 1e-9), "a spoke draws over EDGE_S (DOM 04:22 measured ~0.35 s)");
  assert.deepEqual(Object.keys(flowClock(flow())).sort(), ["box", "edgeAt", "landed", "nodeAt", "tagAt", "tagEnd"], "a row's clock is what it was");
});

test("T11's tokens ride the spokes, each from its own spoke drawn", () => {
  const sp = hubFlow(4, { tokens: { from_at: 5.0, n: 1 } }), lay = flowLayout(HUB_BOX, 5, { layout: "hub" });
  sp.nodes[3].at = 7.0;
  const C = flowClock(sp);
  sp.edges.forEach((_, j) => assert.equal(flowTokenStart(sp, j), Math.max(5.0, C.edgeAt[j] + FLOW.EDGE_S)));
  const t = C.edgeAt[0] + FLOW.EDGE_S + 0.3, on = new Set(flowTokens(sp, t, lay).map((k) => k.edge));
  assert.ok(on.has(0) && on.has(1) && on.has(3) && !on.has(2), `the late spoke carries none yet: ${[...on]}`);
});

const FAIL_AT = 9.0;
const failing = (o = {}) => hubFlow(4, Object.assign({ fail: { edge: ["market", "b2"], at: FAIL_AT }, tokens: { from_at: 5.0, n: 2 } }, o));

test("THE FAILED LINK's clock: nothing before its word; the disc springs in on BOOM's measured pop, the X in the chip's two strokes, the edge reddening and retracting over CROSS_S", () => {
  const sp = failing();
  assert.equal(flowFailIndex(sp), 1);
  assert.equal(flowFailIndex(hubFlow(4)), -1);
  assert.equal(flowFailIndex(failing({ fail: { edge: ["b1", "b2"], at: FAIL_AT } })), -1, "an edge the diagram does not draw fails nothing");
  assert.equal(flowFailAt(sp, FAIL_AT - 1e-6), null);
  assert.equal(flowFailAt(hubFlow(4), 20), null);
  const peak = flowFailAt(sp, FAIL_AT + 0.167);
  assert.ok(Math.abs(peak.scale - (FLOW.FAIL_POP_FROM + (1 - FLOW.FAIL_POP_FROM) * springPop(0.167 / FLOW.FAIL_POP_S, FLOW.FAIL_MP))) < 1e-12);
  let best = 0, tBest = 0;
  for (let i = 0; i <= 900; i++) { const f = flowFailAt(sp, FAIL_AT + i / 1000); if (f.scale > best) { best = f.scale; tBest = i / 1000; } }
  assert.ok(Math.abs(best - 1.21) < 0.01, `the overshoot BOOM measured (55 / 46 px): ${best}`);
  assert.ok(Math.abs(tBest - 0.167) < 0.01, `the peak where BOOM's is (0.167 s): ${tBest}`);
  const half = flowFailAt(sp, FAIL_AT + CHIP.CROSS_S / 2);
  assert.deepEqual(half.strokes, [1, 0], "the first stroke done at half, the second not begun - the chip's law");
  assert.ok(near(half.u, 0.5, 1e-12));
  const done = flowFailAt(sp, FAIL_AT + 5);
  assert.deepEqual(done.strokes, [1, 1]);
  assert.equal(done.u, 1);
  assert.ok(near(done.scale, 1, 1e-12) && done.fade === 1);
});

test("the failed edge SEVERS: its two halves each retract FAIL_RETRACT of their own length from the middle, and the disc sits in the gap at the arc's midpoint", () => {
  const lay = flowLayout(HUB_BOX, 5, { layout: "hub" }), pts = flowEdgePts(lay, 0, 2);
  const L = (q) => q.slice(1).reduce((s, p, i) => s + Math.hypot(p.x - q[i].x, p.y - q[i].y), 0), whole = L(pts);
  const cut = flowFailSplit(pts, 1);
  assert.ok(near(L(cut.a), whole / 2 * (1 - FLOW.FAIL_RETRACT), 1e-6) && near(L(cut.b), whole / 2 * (1 - FLOW.FAIL_RETRACT), 1e-6));
  assert.ok(near(cut.a[0].x, pts[0].x, 1e-9) && near(cut.b[cut.b.length - 1].x, pts[pts.length - 1].x, 1e-9), "the ends stay at their cards");
  const g = Math.hypot(cut.b[0].x - cut.a[cut.a.length - 1].x, cut.b[0].y - cut.a[cut.a.length - 1].y);
  assert.ok(g > 0 && near(g, whole * FLOW.FAIL_RETRACT, 0.5), `the gap: ${g}`);
  const none = flowFailSplit(pts, 0);
  assert.ok(near(L(none.a) + L(none.b), whole, 1e-6), "u 0: whole");
  assert.ok(Math.hypot(cut.mid.x - (cut.a[cut.a.length - 1].x + cut.b[0].x) / 2, cut.mid.y - (cut.a[cut.a.length - 1].y + cut.b[0].y) / 2) < 0.5, "the disc in the gap");
  assert.equal(flowFailInk(false, 0), FLOW.TOKEN_INK.toLowerCase());
  assert.equal(flowFailInk(false, 1), FLOW.FAIL_INK.toLowerCase());
  assert.equal(flowFailInk(true, 1), FLOW.FAIL_INK.toLowerCase());
  assert.equal(flowFailInk(true, 0), FLOW.PHONE_TOKEN_INK.toLowerCase());
});

test("the disc is BOOM's measured badge: 0.198 of the card, the X 0.53 of its radius, a white X on the neg ink", () => {
  assert.equal(FLOW.FAIL_D, 0.198);
  assert.equal(FLOW.FAIL_INK, "#FF4D4D", "the template's --lp-neg (chip.mjs's TAB_INK.sell)");
  assert.equal(FLOW.FAIL_MARK, "#FFFFFF");
  assert.ok(FLOW.FAIL_X > 0.4 && FLOW.FAIL_X < 0.7 && FLOW.FAIL_X_W > 0.05 && FLOW.FAIL_X_W < 0.2);
});

test("the painter: before the word the failing flow paints exactly what the plain one does; after it, two red halves, the head, the disc and its X; the nodes stay", () => {
  const sp = failing(), plain = hubFlow(4, { tokens: { from_at: 5.0, n: 2 } });
  const strip = (m) => JSON.stringify(m.map((e) => [e.tag, e.cls, e.at, e.textContent]));
  for (const t of [2, 5.5, 7, FAIL_AT - 0.001]) assert.equal(strip(stub(sp, t, HUB_BOX)), strip(stub(plain, t, HUB_BOX)), `t ${t}`);
  const made = stub(sp, FAIL_AT + 2, HUB_BOX);
  const arrows = made.filter((e) => e.cls === "flowarrow");
  assert.equal(arrows.length, 9, "three whole spokes with heads, and the failed one's two halves and its head");
  const red = arrows.filter((e) => /stroke:#ff4d4d/i.test(e.at.style || ""));
  assert.equal(red.length, 3, "the failed spoke's two halves and its head, in the neg ink");
  assert.equal(made.filter((e) => e.cls === "chipcard").length, 5, "its nodes stay");
  const disc = made.filter((e) => e.cls === "flowfaildisc"), marks = made.filter((e) => e.cls === "flowfailmark");
  assert.equal(disc.length, 1);
  assert.match(disc[0].at.style, /fill:#FF4D4D/);
  assert.equal(marks.length, 2);
  assert.ok(marks.every((m) => /stroke:#FFFFFF/.test(m.at.style)));
  assert.ok(made.indexOf(disc[0]) > made.map((e) => e.cls).lastIndexOf("chipcard"), "the disc over the world, after the cards");
  const lay = flowLayout(HUB_BOX, 5, { layout: "hub" });
  assert.equal(made.filter((e) => e.cls === "flowtoken").length, flowTokens(sp, FAIL_AT + 2, lay).filter((k) => k.alpha > 0).length);
  assert.ok(flowTokens(sp, FAIL_AT + 2, lay).every((k) => k.edge !== 1), "a severed link carries no money");
  const mid = flowTokens(sp, FAIL_AT + CHIP.CROSS_S / 2, lay).filter((k) => k.edge === 1);
  const before = flowTokens(plain, FAIL_AT + CHIP.CROSS_S / 2, lay).filter((k) => k.edge === 1);
  assert.equal(mid.length, before.length);
  mid.forEach((k, i) => assert.ok(near(k.alpha, before[i].alpha * 0.5, 1e-12), "its tokens fade on the retract"));
});

test("the hub and its failure are a pure function of t: a seek IS the play", () => {
  const sp = failing(), lay = flowLayout(HUB_BOX, 5, { layout: "hub" });
  const read = (t) => JSON.stringify([flowClock(sp), flowFailAt(sp, t), flowTokens(sp, t, lay), [0, 1, 2, 3].map((j) => flowEdgeF(sp, j, t))]);
  const fwd = [], back = [];
  for (let i = 0; i <= 300; i++) fwd.push(read(i / 25));
  for (let i = 300; i >= 0; i--) back.unshift(read(i / 25));
  assert.deepEqual(back, fwd);
  const src = [flowFailAt, flowFailSplit, flowFailInk, flowFailIndex].map((f) => f.toString()).join("\n");
  assert.ok(!/Math\.random|Date\.now|new Date|performance\./.test(src));
});
