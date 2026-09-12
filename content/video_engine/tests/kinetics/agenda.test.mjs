// P52 T8 - THE NUMBERED AGENDA (EXPLORATION-REVIEW-2026-09-10.md:58, Bravos's "China's Gameplan 1 | 2"). One
// declaration, not `figure` plus `note`: 2-4 numbered rows, each revealed on its OWN word, the block laid out for
// the full list from the first frame, and every row holding at a NAMED idle. These tests pin all four.
import { test } from "node:test";
import assert from "node:assert/strict";
import { IDLE_KINDS } from "../../scripts/kinetics/idle.mjs";
import { AGENDA, agendaRows, agendaLayout, agendaRowF, agendaPose, paintAgenda } from "../../scripts/species/agenda.mjs";

const near = (a, b, eps = 1e-9) => Math.abs(a - b) <= eps;
const BOX = { x: 1180, y: 180, w: 660, h: 520 };
const ROWS = [{ text: "A Treasury page" }, { text: "Your phone" }, { text: "The bill", sub: "$4,500" }];
const agenda = (o = {}) => Object.assign({ kind: "agenda", at: 6, dur: 10, rows: ROWS,
                                           target: { kind: "region", x0: 0.61, y0: 0.17, x1: 0.96, y1: 0.65 } }, o);

// ---------------------------------------------------------------- the dials and the bounds
test("the dials are the agenda's, and the bounds are the ones the compiler holds", () => {
  assert.equal(AGENDA.MIN_ROWS, 2, "one row is a note, not an agenda");
  assert.ok(AGENDA.MAX_ROWS >= 3 && AGENDA.MAX_ROWS <= 4, "five is a checklist nobody holds at phone size");
  assert.ok(AGENDA.ROW_S > 0 && AGENDA.RULE_S > 0 && AGENDA.STEP > 0);
  assert.ok(AGENDA.NUM_SIZE > AGENDA.TEXT_SIZE, "the number is the biggest thing in the row - it is what was counted");
  assert.ok(AGENDA.SUB_SIZE < AGENDA.TEXT_SIZE);
});

// ---------------------------------------------------------------- the rows
test("the rows are numbered 1..n unless a row names its own number", () => {
  assert.deepEqual(agendaRows(agenda()).map((r) => r.n), ["1", "2", "3"]);
  assert.deepEqual(agendaRows(agenda({ rows: [{ text: "a", n: 4 }, { text: "b" }] })).map((r) => r.n), ["4", "2"]);
  assert.deepEqual(agendaRows(agenda()).map((r) => r.text), ["A Treasury page", "Your phone", "The bill"]);
  assert.deepEqual(agendaRows(agenda()).map((r) => r.sub), ["", "", "$4,500"]);
  assert.equal(agendaRows(agenda({ rows: [1, 2, 3, 4, 5, 6].map((i) => ({ text: String(i) })) })).length, AGENDA.MAX_ROWS,
               "the bound holds in the module too, not only in the compiler");
  assert.deepEqual(agendaRows({ at: 3 }), [], "no rows is no agenda, never a crash");
});

test("one row per WORD: STEP after the row before, and a row's own `at` wins", () => {
  const rows = agendaRows(agenda());
  for (let i = 0; i < rows.length; i++) assert.ok(near(rows[i].at, 6 + i * AGENDA.STEP), `row ${i}`);
  const named = agendaRows(agenda({ rows: [{ text: "a" }, { text: "b", at: 9.4 }, { text: "c", at: 11.2 }] }));
  assert.deepEqual(named.map((r) => r.at), [6, 9.4, 11.2]);
  const slow = agendaRows(agenda({ step: 1.2 }));
  assert.deepEqual(slow.map((r) => r.at), [6, 7.2, 8.4]);
});

test("a row is revealed on its own word and never before, and no row overtakes the one above it", () => {
  const sp = agenda({ rows: [{ text: "a" }, { text: "b", at: 9 }, { text: "c", at: 12 }] });
  assert.deepEqual(agendaPose(sp, 5.9).rows.map((r) => r.fade), [0, 0, 0]);
  assert.equal(agendaPose(sp, 8.9).shown, 1);
  assert.equal(agendaPose(sp, 11.9).shown, 2);
  assert.equal(agendaPose(sp, 13).shown, 3);
  assert.equal(agendaPose(sp, 13).done, 3);
  let prev = 0;
  for (let i = 0; i <= 400; i++) { const s = agendaPose(sp, i / 20).shown; assert.ok(s >= prev); prev = s; }
});

test("a row arrives by being WRITTEN: the number first, the rule drawn, the text rising into place", () => {
  const sp = agenda({ rows: [{ text: "a" }] });
  const at = 6;
  assert.deepEqual(Object.entries(agendaRowF(sp, at - 0.01, 0)).filter(([, v]) => v !== 0 && v !== AGENDA.ROW_DY).length, 0,
                   "before its word the row is nothing at all");
  const lead = agendaRowF(sp, at + AGENDA.NUM_LEAD * 0.5, 0);
  assert.ok(lead.num > 0 && lead.text === 0, "the row is numbered, THEN said");
  assert.ok(lead.rule > 0, "the hand's rule is already running under it");
  const mid = agendaRowF(sp, at + AGENDA.NUM_LEAD + AGENDA.ROW_S / 2, 0);
  assert.ok(mid.text > 0 && mid.text < 1 && mid.dy > 0 && mid.dy < AGENDA.ROW_DY, JSON.stringify(mid));
  const done = agendaRowF(sp, at + AGENDA.NUM_LEAD + AGENDA.ROW_S + 1, 0);
  assert.deepEqual([done.num, done.rule, done.text, done.dy, done.fade], [1, 1, 1, 0, 1]);
  assert.deepEqual(agendaRowF(sp, 99, 7), { num: 0, rule: 0, text: 0, dy: AGENDA.ROW_DY, fade: 0 }, "a row that is not there");
});

// ---------------------------------------------------------------- the block
test("the block is laid out for the FULL list: a row that arrives never pushes the one above it", () => {
  const two = agendaLayout(BOX, 2), three = agendaLayout(BOX, 3);
  assert.equal(three.rows.length, 3);
  for (let i = 1; i < 3; i++) assert.ok(near(three.rows[i].y - three.rows[i - 1].y, AGENDA.ROW_H * three.k), "one pitch, every row");
  assert.ok(three.k <= 1 && three.k >= AGENDA.MIN_K);
  assert.ok(two.rows[0].y > three.rows[0].y, "a shorter list sits lower in the same box - it is centred, not top-aligned");
  assert.deepEqual(JSON.stringify(agendaLayout(BOX, 3)), JSON.stringify(three), "the layout is a pure function of the box and the count - t is not in it");
  for (const r of three.rows) {
    assert.ok(r.textX > r.numX, "the text starts in the same gutter on every row");
    assert.ok(near(r.textX - r.numX, AGENDA.NUM_W * three.k));
    assert.ok(r.ruleY > r.y, "the rule is drawn under the row");
  }
});

test("a narrow box scales the whole block by ONE k, never row by row", () => {
  const tight = agendaLayout({ x: 0, y: 0, w: 300, h: 200 }, 3);
  assert.ok(tight.k < 1 && tight.k >= AGENDA.MIN_K);
  const pitches = tight.rows.slice(1).map((r, i) => r.y - tight.rows[i].y);
  for (const p of pitches) assert.ok(near(p, pitches[0]));
});

// ---------------------------------------------------------------- pure function of t
test("a seek IS the play: the same t gives the same bits, in any order, with nothing remembered", () => {
  const sp = agenda({ idle: "breath" });
  const forward = [], backward = [];
  for (let i = 0; i <= 400; i++) forward.push(JSON.stringify(agendaPose(sp, i / 20)));
  for (let i = 400; i >= 0; i--) backward.unshift(JSON.stringify(agendaPose(sp, i / 20)));
  assert.deepEqual(backward, forward);
  assert.equal(JSON.stringify(agendaPose(sp, 7.35)), forward[147]);
});

test("nothing in the module reaches for a clock or a random", () => {
  const src = paintAgenda.toString() + agendaPose.toString() + agendaLayout.toString() + agendaRows.toString();
  assert.ok(!/Math\.random|Date\.now|new Date|performance\./.test(src), src);
});

// ---------------------------------------------------------------- the painter, on a stub surface
function stub(sp, t, opts = {}) {
  const made = [], idles = [], drawn = [];
  const el = (tag, cls, parent, at) => {
    const e = { tag, cls, at: Object.assign({}, at), kids: [], textContent: "",
                setAttribute(k, v) { this.at[k] = v; }, getAttribute(k) { return this.at[k]; } };
    made.push(e); if (parent && parent.kids) parent.kids.push(e); return e;
  };
  paintAgenda({ sp, t, svg: { kids: [] }, el,
                resolveTarget: () => (opts.noTarget ? null : { x: BOX.x, y: BOX.y, w: BOX.w, h: BOX.h }),
                drawOn: (p, k) => { drawn.push(k); p.setAttribute("stroke-dashoffset", k.toFixed(3)); },
                hash: (a, b, c) => ((a + b * 13 + c) % 100) / 100, seed: 5, si: 2,
                idle: (kind, tt, ph) => { idles.push([kind, ph]); return { scale: 1, dx: 0, dy: 0 }; },
                ease: (k) => k, STAGE_W: 1920, STAGE_H: 1080 });
  return { made, idles, drawn };
}

test("the painter draws nothing when the target does not resolve", () => {
  assert.equal(stub(agenda(), 12, { noTarget: true }).made.length, 0, "the targeting law: no resolved target, nothing painted");
});

test("the painter writes one number, one rule and one text per revealed row - and the sub when the row has one", () => {
  const sp = agenda();
  const one = stub(sp, 6.05);
  assert.equal(one.made.filter((e) => e.cls === "agnum").length, 1, "one row is up, not three");
  assert.equal(one.made.filter((e) => e.cls === "agrow").length, 0, "its text has not started rising yet (NUM_LEAD)");
  const all = stub(sp, 12);
  assert.deepEqual(all.made.filter((e) => e.cls === "agnum").map((e) => e.textContent), ["1", "2", "3"]);
  assert.deepEqual(all.made.filter((e) => e.cls === "agrow").map((e) => e.textContent), ROWS.map((r) => r.text));
  assert.deepEqual(all.made.filter((e) => e.cls === "agsub").map((e) => e.textContent), ["$4,500"]);
  assert.equal(all.made.filter((e) => e.cls === "agrule").length, 3);
  assert.deepEqual(all.drawn, [1, 1, 1], "the rules are drawn by the same hand every other mark uses");
});

test("every row holds at a NAMED idle, each at its own phase; 'none' is declared stillness", () => {
  const dflt = stub(agenda(), 12);
  assert.deepEqual([...new Set(dflt.idles.map((i) => i[0]))], ["breath"]);
  assert.ok(IDLE_KINDS.includes("breath") && IDLE_KINDS.includes("drift"));
  assert.equal(new Set(dflt.idles.map((i) => i[1])).size, 3, "no two rows breathe in step (E49)");
  assert.deepEqual([...new Set(stub(agenda({ idle: "drift" }), 12).idles.map((i) => i[0]))], ["drift"]);
  assert.equal(stub(agenda({ idle: "none" }), 12).idles.length, 0);
});

test("NOTHING SPINS: no attribute the painter writes carries a rotation, at any t", () => {
  for (const t of [5.9, 6.0, 6.2, 6.5, 7.1, 9.0, 16.0]) {
    for (const e of stub(agenda(), t).made) {
      for (const [k, v] of Object.entries(e.at)) assert.ok(!/rotate|skew|matrix/.test(String(v)), `${t}: ${e.tag}.${k} = ${v}`);
    }
  }
});
