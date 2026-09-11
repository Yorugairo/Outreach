// P50 T4 - THE FLOW DIAGRAM (the Bravos flow diagram, shots 82-86). The whole diagram is a pure function of t,
// sp.at and sp.swap.at: the frame draws round, the chips land in order, the clothoid arrows draw one at a time
// by length, and on a LATER word ONE node un-draws and is replaced in the same spot while the arrows stand.
// These tests pin the schedule, the swap's two halves, the anchors the arrows are fitted to, and that nothing
// is remembered between calls.
import { test } from "node:test";
import assert from "node:assert/strict";
import { CHIP, chipLand } from "../../scripts/species/chip.mjs";
import { clothoidAt, clothoidFit, curvatureOf } from "../../scripts/kinetics/clothoid.mjs";
import { FLOW, flowLayout, flowClock, flowBoxF, flowDashes, flowSwapPhase, flowNodeAt, flowPose,
         flowEdgeF, flowAnchors, flowHead, flowEdgeIndex, paintFlow } from "../../scripts/species/flow.mjs";

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
