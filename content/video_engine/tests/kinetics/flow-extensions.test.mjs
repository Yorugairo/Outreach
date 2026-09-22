// T20 - reversible flow edges, analyst-proxy operators, and the opt-in phone profile.
// These are pure-clock and painter-contract tests; browser/font acceptance remains a parent-owned proof.
import { test } from "node:test";
import assert from "node:assert/strict";
import { CHIP } from "../../scripts/species/chip.mjs";
import {
  FLOW, flowClock, flowEdgesAt, flowLayout, flowNodeAt, paintFlow,
} from "../../scripts/species/flow.mjs";

const BOX = { x: 200, y: 360, w: 1500, h: 440 };
const base = (overrides = {}) => Object.assign({
  kind: "flow", at: 4, dur: 20, target: { kind: "region", x0: .1, y0: .3, x1: .9, y1: .8 },
  nodes: [
    { id: "assets", icon: "coins", label: "FED\nASSETS" },
    { id: "cash", icon: "landmark", label: "GOVERNMENT\nCASH" },
    { id: "overnight", icon: "coins", label: "OVERNIGHT\nCASH" },
  ],
  edges: [["assets", "cash"], ["cash", "overnight"]], tag: "PROXY",
}, overrides);

const readEdges = (sp, t) => {
  const out = flowEdgesAt(sp, t);
  return { phase: out.phase, stateIndex: out.stateIndex,
    edges: out.edges.map(({ edge, fraction, phase, fromIndex, toIndex, kind, operator }) =>
      ({ edge, fraction, phase, fromIndex, toIndex, kind, operator })) };
};

const stub = (sp, t, target = BOX) => {
  const made = [];
  const el = (tag, cls, parent, attrs) => {
    const e = { tag, cls, at: attrs || {}, kids: [], textContent: "",
      setAttribute(k, v) { this.at[k] = v; }, getAttribute(k) { return this.at[k]; } };
    made.push(e); if (parent && parent.kids) parent.kids.push(e); return e;
  };
  const geo = JSON.stringify({ vb: [0, 0, 24, 24], el: [{ t: "path", a: { d: "M12 16h.01" } }] });
  const ctx = { sp, t, svg: { kids: [] }, el,
    A: { "icon:coins": geo, "icon:landmark": geo }, resolveTarget: () => target,
    drawOn: (p, k) => p.setAttribute("stroke-dashoffset", k.toFixed(3)),
    hash: () => .5, idle: () => ({ scale: 1, dx: 0, dy: 0 }), seed: 1, si: 0 };
  paintFlow(ctx); return made;
};

test("state-fit constants and absolute edge-state boundaries are explicit", () => {
  assert.equal(FLOW.EDGE_RETRACT_S, .30);
  assert.equal(FLOW.STATE_RETRACT_S, .30);
  assert.equal(FLOW.EDGE_S, .34);
  const sp = base({ edge_states: [{ at: 10, edges: [["assets", "overnight"], ["overnight", "cash"]] }] });
  const C = flowClock(sp), end = 10 + FLOW.EDGE_RETRACT_S + 2 * FLOW.EDGE_S;
  assert.ok(10 >= C.tagEnd, `state begins after initial tagEnd ${C.tagEnd}`);
  assert.equal(readEdges(sp, 10).phase, "retract");
  assert.ok(readEdges(sp, 10).edges.every((e) => e.fraction === 1));
  assert.equal(readEdges(sp, 10 + FLOW.EDGE_RETRACT_S).phase, "draw");
  assert.ok(readEdges(sp, 10 + FLOW.EDGE_RETRACT_S).edges.every((e) => e.fraction === 0));
  const mid = readEdges(sp, 10 + FLOW.EDGE_RETRACT_S + FLOW.EDGE_S);
  assert.equal(mid.phase, "draw");
  assert.ok(Math.abs(mid.edges[0].fraction - 1) < 1e-9);
  assert.equal(mid.edges[1].fraction, 0);
  assert.equal(readEdges(sp, end).phase, "steady");
  assert.deepEqual(readEdges(sp, end).edges.map((e) => e.edge), [["assets", "overnight"], ["overnight", "cash"]]);
});

test("flowEdgesAt is cold-seek safe and reverse arrows do not reland nodes", () => {
  const sp = base({ edge_states: [
    { at: 10, edges: [["assets", "overnight"], ["overnight", "cash"]] },
    { at: 11.0, edges: [["cash", "assets"]] },
  ] });
  const C = flowClock(sp), times = [C.tagEnd, 10, 10.11, 10.3, 10.47, 10.98, 11, 11.15, 11.3, 11.64, 13];
  const forward = times.map((t) => readEdges(sp, t));
  const backward = times.slice().reverse().map((t) => readEdges(sp, t)).reverse();
  assert.deepEqual(backward, forward);
  const standing = sp.nodes.map((_, i) => flowNodeAt(sp, i, 10));
  for (const t of [10, 10.15, 10.3, 10.64, 11, 11.15, 11.3, 11.64, 13]) {
    assert.deepEqual(sp.nodes.map((_, i) => flowNodeAt(sp, i, t)), standing, `nodes stable at ${t}`);
  }
});

test("operator mode draws a timed midpoint minus, never an arrow shaft or head", () => {
  const sp = base({ operators: ["-", "-"] });
  const C = flowClock(sp), made = stub(sp, C.edgeAt[0] + FLOW.EDGE_S / 2);
  const operators = made.filter((e) => e.cls === "flowoperator");
  assert.equal(operators.length, 1, "one minus is in flight at the first edge clock");
  assert.equal(made.filter((e) => e.cls === "flowarrow").length, 0);
  assert.match(operators[0].at.d, /^M[-\d.]+ [-\d.]+ L[-\d.]+ [-\d.]+$/);
  assert.match(operators[0].at.style, /stroke:/);
  assert.ok(+operators[0].at["stroke-dashoffset"] > 0 && +operators[0].at["stroke-dashoffset"] < 1);
  const settled = stub(sp, C.edgeAt[1] + FLOW.EDGE_S).filter((e) => e.cls === "flowoperator");
  assert.equal(settled.length, 2);
  assert.ok(settled.every((e) => e.at["stroke-dashoffset"] === "1.000"));
  const lay = flowLayout(BOX, sp.nodes.length);
  for (const operator of settled) {
    const coords = operator.at.d.match(/-?\d+(?:\.\d+)?/g).map(Number);
    assert.ok(Math.abs(coords[1] - lay.cells[0].y) < .01, "minus shares the terms' centerline");
    assert.equal(coords[1], coords[3]);
  }
});

test("landscape-phone reserves multiline label space and writes explicit label/tag sizes", () => {
  const sp = base({ readability: "landscape-phone" }), C = flowClock(sp);
  const lay = flowLayout(BOX, sp.nodes.length, { readability: "landscape-phone", labels: sp.nodes.map((n) => n.label) });
  assert.equal(lay.labelLines, 2);
  assert.equal(lay.labelH, 2 * FLOW.PHONE_LABEL_LINE_H);
  assert.ok(lay.labelDy > CHIP.LABEL_DY);
  const made = stub(sp, C.tagAt + FLOW.TAG_S);
  const labels = made.filter((e) => e.cls === "chiplab");
  assert.equal(labels.length, 3);
  assert.ok(labels.every((e) => /font-size:45px/.test(e.at.style)));
  assert.equal(labels[0].kids.filter((e) => e.tag === "tspan").length, 2);
  const tag = made.find((e) => e.cls === "flowtag");
  assert.ok(tag && /font-size:48px/.test(tag.at.style));
  assert.ok(made.filter((e) => e.cls === "flowbox").every((e) => /stroke:#25313C/.test(e.at.style)));
  assert.ok(made.filter((e) => e.cls === "flowarrow").every((e) => /stroke:#25313C/.test(e.at.style)));
  assert.ok(made.filter((e) => e.cls === "chipcard").every((e) => /fill:#F4E6C7/.test(e.at.style)));
  assert.ok(made.filter((e) => e.cls === "chipglyph").every((e) => /stroke:#25313C/.test(e.at.style)));
});

test("absent extension fields stay on the legacy arrow path and clock", () => {
  const sp = base();
  const C = flowClock(sp), made = stub(sp, C.edgeAt[1] + FLOW.EDGE_S);
  assert.equal(made.filter((e) => e.cls === "flowoperator").length, 0);
  assert.equal(made.filter((e) => e.cls === "flowarrow").length, 4);
  assert.equal(made.filter((e) => e.cls === "chiplab")[0].at.style, undefined);
  const legacyTag = stub(sp, C.tagAt + FLOW.TAG_S).find((e) => e.cls === "flowtag");
  assert.equal(legacyTag.at.style, "font-size:34px");
  assert.deepEqual(readEdges(sp, C.edgeAt[1] + FLOW.EDGE_S).edges.map((e) => e.edge), sp.edges);
});
