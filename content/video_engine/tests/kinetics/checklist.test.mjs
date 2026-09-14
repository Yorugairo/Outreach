// P55 T7 - THE TEST CARD, promoted from the engine's inline checklist build and drawChart branch with every frame
// byte-identical. These tests pin the row/cell clock, the recap switch at RECAP_S, the type-on rate, the highlighter
// sweep fraction, the column auto-fit and the build's element order.
import { test } from "node:test";
import assert from "node:assert/strict";
import { CHECKLIST, checklistRowY, checklistRecap, checklistRowDelay, checklistCellClock, checklistTyped, checklistSweep,
         checklistColumns, buildChecklist, paintChecklist } from "../../scripts/species/checklist.mjs";

const near = (a, b, eps = 1e-9) => Math.abs(a - b) <= eps;

test("the dials carry the inline code's values, frozen", () => {
  assert.ok(Object.isFrozen(CHECKLIST) && Object.isFrozen(CHECKLIST.COLORS) && Object.isFrozen(CHECKLIST.OFFS));
  assert.deepEqual([...CHECKLIST.COLORS], ["#f4f6f8", "#dce3ea", "#3bc9b0", "#ff8a8c"]);
  assert.deepEqual([CHECKLIST.ROW0_DY, CHECKLIST.ROW_PITCH, CHECKLIST.RECAP_S, CHECKLIST.TYPE_S, CHECKLIST.SWEEP_S], [64, 58, 12, 0.045, 0.55]);
  assert.deepEqual([...CHECKLIST.OFFS], [0, 0.6, 1.0, 1.6]);
  assert.deepEqual([...CHECKLIST.RECAP_OFFS], [0, 0.25, 0.45, 0.7]);
});

test("rows are pitched ROW_PITCH apart from ROW0_DY below the plot top", () => {
  assert.equal(checklistRowY(96, 0), 160);
  assert.equal(checklistRowY(96, 3), 96 + 64 + 3 * 58);
});

test("the recap switch: a hold under 12 s is a recap, 12 s is not", () => {
  assert.equal(checklistRecap({ enter: 10, exit: 21.9 }), true);
  assert.equal(checklistRecap({ enter: 10, exit: 22 }), false);
  assert.equal(checklistRowDelay({ d: 6 }, 2, true), 1.6);
  assert.equal(checklistRowDelay({ d: 6 }, 2, false), 6);
});

test("the cell clock: the row delay less the cell's offset, the fourth offset reused past column 3", () => {
  assert.equal(checklistCellClock(5, 1, 0, false), 4);
  assert.ok(near(checklistCellClock(5, 1, 2, false), 3));
  assert.ok(near(checklistCellClock(5, 1, 3, false), 2.4));
  assert.ok(near(checklistCellClock(5, 1, 7, false), 2.4));
  assert.ok(near(checklistCellClock(5, 1, 3, true), 3.3));
});

test("the type-on rate: one character per TYPE_S, never negative", () => {
  assert.equal(checklistTyped(-1), 0);
  assert.equal(checklistTyped(0), 0);
  assert.equal(checklistTyped(0.046), 1);
  assert.equal(checklistTyped(0.45), Math.floor(0.45 / 0.045));
});

test("the highlighter sweep: 0 before its offset, an out-cubic over SWEEP_S, then held at 1", () => {
  assert.equal(checklistSweep(-0.2), 0);
  assert.equal(checklistSweep(0), 0);
  assert.ok(near(checklistSweep(0.275), 1 - Math.pow(0.5, 3)));
  assert.equal(checklistSweep(0.55), 1);
  assert.equal(checklistSweep(3), 1);
});

test("the column auto-fit: slack spreads evenly, a deficit squeezes proportionally", () => {
  const roomy = checklistColumns([100, 100, 100], 900);
  assert.equal(roomy.scale2, 1);
  assert.equal(roomy.extra, (900 - 378) / 3);
  assert.deepEqual(roomy.xs, [64, 64 + 126 + 174, 64 + 2 * (126 + 174)]);
  const tight = checklistColumns([400, 300, 200], 600);
  assert.ok(near(tight.scale2, 600 / 978));
  assert.equal(tight.extra, 0);
  assert.ok(near(tight.xs[2] - tight.xs[0], (426 + 326) * 600 / 978));
});

const stubMk = () => {
  const made = [];
  const mk = (tag, at, txt, parent) => { const e = { tag, at, txt, parent: parent || "svg" }; made.push(e); return e; };
  return { made, mk };
};

test("the build keeps the inline element order: headers, then per row its cells (bands from column 2) and a rule", () => {
  const { made, mk } = stubMk();
  const spec = { head: ["Q", "WHERE", "STEEL", "PAPER"], rows: [{ cells: ["Is it?", "here", "yes", ""] }, { cells: ["And?", "there", "no", "maybe"], delay: 7 }] };
  const out = buildChecklist(spec, { mk, slot: 0, PL: 64, PT: 96, CW: 1056, PR: 120, kin: () => false });
  assert.deepEqual(made.slice(0, 4).map((e) => e.tag), ["text", "text", "text", "text"]);
  assert.deepEqual(made.slice(4, 14).map((e) => e.tag), ["g", "text", "g", "text", "g", "defs", "clipPath", "rect", "rect", "text"]);
  assert.equal(out.rowEls.length, 2);
  assert.deepEqual(out.rowEls.map((r) => [r.d, r.y]), [[0, 160], [7, 218]]);
  assert.equal(out.rowEls[0].cells[3].band, null, "an empty answer cell gets no band");
  const band = out.rowEls[0].cells[2].band;
  assert.deepEqual([band.at.x, band.at.y, band.at.width, band.at.height, band.at.rx, band.at.opacity, band.at.fill], [56, 139, 10, 30, 4, 0.28, "#3bc9b0"]);
  assert.equal(out.chkFit.usable, 1056 - 64 - 28);
  assert.equal(out.rowEls[0].cells[0].tx.txt, "", "the question cell starts empty - it types on");
});

test("the painter types, fades and sweeps on tRel without a DOM measure", () => {
  const attrs = () => ({ at: {}, setAttribute(k, v) { this.at[k] = v; } });
  const tx = Object.assign(attrs(), { textContent: "" });
  const q = { el: attrs(), tx, txt: "Is it steel?", ci: 0, sweep: null };
  const bandEl = attrs();
  const a = { el: Object.assign(attrs(), { querySelector: () => bandEl }), tx: Object.assign(attrs(), { textContent: "yes" }), txt: "yes", ci: 2, sweep: attrs(), bandCls: "hl", room: 100 };
  const st = { rowEls: [{ d: 1, cells: [q, attrs(), a], y: 160 }] };
  st.rowEls[0].cells[1] = { el: attrs(), tx: attrs(), txt: "x", ci: 1, sweep: null };
  paintChecklist(st, 1.2, { enter: 0, exit: 30 });
  assert.equal(q.tx.textContent, "Is it ".slice(0, checklistTyped(0.2)));
  assert.equal(q.el.at.opacity, (0.2 / 0.35).toFixed(2));
  assert.equal(a.sweep.at.width, "0.0", "the answer's sweep has not started (+1.0)");
  paintChecklist(st, 3, { enter: 0, exit: 30 });
  assert.equal(a.sweep.at.width, (1 * Math.min(300 + 18, 100 + 12)).toFixed(1));
  assert.equal(bandEl.at.width, (112).toFixed(1));
});
