// P69 T28b / R26-300 - THE TEST CARD READS ON A PHONE: the checklist's `profile: "phone"`. The profile is one frozen
// dial set - the type, the header, the title, the row pitch and the highlighter band scaled together on the dock's own
// canvas - and a checklist that names no profile gets CHECKLIST itself, so the default card cannot move.
import { test } from "node:test";
import assert from "node:assert/strict";
import * as C from "../../scripts/species/checklist.mjs";

const { CHECKLIST, CHECKLIST_PROFILES, checklistDials, checklistRowY, buildChecklist, checklistHeader, checklistColumns } = C;
const PHONE = { profile: "phone", head: ["Ask", "Steel", "Paper"],
  rows: [{ cells: ["1  Scarce?", "sold out", "on belief"] }, { cells: ["2  Cash or paper?", "earns cash", "issues paper"] },
         { cells: ["3  Used tomorrow?", "still used", "needs the story"] }] };
const CH = 480, CELL_MIN = 54;

test("no profile is the default card: CHECKLIST itself, the same object", () => {
  assert.equal(checklistDials({ head: [], rows: [] }), CHECKLIST);
  assert.equal(checklistDials({ head: [], rows: [], profile: null }), CHECKLIST);
});

test("an unknown profile is refused by name", () => {
  assert.throws(() => checklistDials({ profile: "tablet" }), /checklist profile 'tablet' is not one of phone/);
});

test("the phone profile is frozen and sets the type at the floor, the pitch and the band together", () => {
  const P = CHECKLIST_PROFILES.phone;
  assert.ok(Object.isFrozen(CHECKLIST_PROFILES) && Object.isFrozen(P) && Object.isFrozen(P.TYPE) && Object.isFrozen(P.CANVAS));
  assert.equal(checklistDials(PHONE), P);
  assert.ok(P.TYPE.CELL_PX >= CELL_MIN && P.TYPE.HEAD_PX >= CELL_MIN && P.TYPE.TITLE_PX >= CELL_MIN, JSON.stringify(P.TYPE));
  assert.deepEqual([P.ROW0_DY, P.ROW_PITCH], [130, 90]);
  assert.ok(P.BAND_H > P.TYPE.CELL_PX && P.BAND_H < P.ROW_PITCH, "the band is taller than the type and leaves air between rows");
  assert.ok(P.BAND_RISE < P.TYPE.CELL_PX, "the band rises no higher than the type");
  assert.equal(P.HL_FROM_COL, 1, "a phone card is a question and its two answers - both answers take the marker");
  assert.deepEqual([...P.COLORS], [CHECKLIST.COLORS[0], CHECKLIST.COLORS[2], CHECKLIST.COLORS[3]],
                   "the question, steel and paper keep the default card's colours - the detail column is gone");
});

test("the phone rows fill the canvas: the last row's baseline in its lower third, the rule inside it", () => {
  const P = CHECKLIST_PROFILES.phone;
  const ys = [0, 1, 2].map((i) => checklistRowY(P.CANVAS.PT, i, P));
  assert.deepEqual(ys, [226, 316, 406]);
  assert.ok(ys[2] >= CH * 2 / 3 && ys[2] + P.RULE_DY < CH - P.CANVAS.SRC_DY - P.TYPE.SRC_PX, JSON.stringify(ys));
});

const stubMk = () => {
  const made = [];
  const mk = (tag, at, txt, parent) => { const e = { tag, at, txt, parent: parent || "svg" }; made.push(e); return e; };
  return { made, mk };
};

test("the build sizes the head and the cells, bands both answers and rules the full width", () => {
  const P = CHECKLIST_PROFILES.phone, { made, mk } = stubMk();
  const cv = P.CANVAS;
  const out = buildChecklist(PHONE, { mk, slot: 0, PL: cv.PL, PT: cv.PT, CW: 1056, PR: cv.PR, kin: () => false });
  const head = made.filter((e) => e.tag === "text" && e.at.class === "csr");
  assert.deepEqual(head.map((e) => e.at.style), Array(3).fill(`font-size:${P.TYPE.HEAD_PX}px`));
  const cells = made.filter((e) => e.tag === "text" && e.at.class === "cs");
  assert.ok(cells.length === 9 && cells.every((e) => e.at.style === `font-size:${P.TYPE.CELL_PX}px`));
  assert.deepEqual(out.rowEls[0].cells.map((c) => !!c.band), [false, true, true]);
  const band = out.rowEls[0].cells[1].band.at;
  assert.deepEqual([band.y, band.height], [226 - P.BAND_RISE, P.BAND_H]);
  const rule = made.find((e) => e.tag === "line");
  assert.deepEqual([rule.at.x1, rule.at.x2], [cv.PL, 1056 - cv.PR]);
  assert.equal(out.chkFit.V, P, "the painter reads the profile the build used");
  assert.equal(out.chkFit.usable, 1056 - cv.PL - P.FIT_MARGIN);
});

test("the default build writes no style and hands CHECKLIST to the painter", () => {
  const { made, mk } = stubMk();
  const out = buildChecklist({ head: ["Q", "W", "S", "P"], rows: [{ cells: ["a", "b", "c", "d"] }] },
                             { mk, slot: 0, PL: 64, PT: 96, CW: 1056, PR: 120, kin: () => false });
  assert.ok(made.every((e) => !("style" in e.at)));
  assert.equal(out.chkFit.V, CHECKLIST);
});

test("the phone header: the title at its size and place, no sub, the source short at the foot", () => {
  const P = CHECKLIST_PROFILES.phone, { made, mk } = stubMk();
  const fit = checklistHeader({ title: "The test", sub: "", src: "golden" }, mk, 1056, CH, P);
  assert.deepEqual(made.map((e) => [e.at.class, e.at.y, e.at.style]),
                   [["ct", P.CANVAS.TITLE_Y, `font-size:${P.TYPE.TITLE_PX}px`],
                    ["csr", CH - P.CANVAS.SRC_DY, `font-size:${P.TYPE.SRC_PX}px`]]);
  assert.deepEqual(fit.map(([, w]) => w), [1056 - 56, 1056 - 56]);
});

test("the phone fit keeps the question column natural - it types - and squeezes only the answers", () => {
  const P = CHECKLIST_PROFILES.phone;
  const fit = checklistColumns([484, 274, 406], 1000, P);   /* row 20's full cells at 58 px, MEASURED: over the 1000 span */
  assert.equal(fit.xs[1] - fit.xs[0], 484 + P.FIT_PAD, "the question keeps its natural width and its air");
  assert.ok(Math.abs(fit.scale2 - (1000 - 520) / (310 + 442)) < 1e-12);
  assert.ok(Math.abs(fit.xs[2] + (406 + P.FIT_PAD) * fit.scale2 - (P.FIT_X0 + 1000)) < 1e-9, "the columns end at the span");
  const roomy = checklistColumns([233, 274, 351], 1000, P);   /* the golden's in-budget cells: no squeeze, the slack spread */
  assert.equal(roomy.scale2, 1);
  assert.equal(roomy.extra, (1000 - (233 + 274 + 351 + 3 * P.FIT_PAD)) / 3);
  const dflt = checklistColumns([400, 300, 200], 600);   /* the default card squeezes every column, as it always did */
  assert.ok(Math.abs(dflt.scale2 - 600 / 978) < 1e-12);
});
