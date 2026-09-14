// P57 T21 / R26-99 - THE RECORD DOCUMENT PROMOTED (the P55 T7 recipe). The promotion's proof is that every
// golden is byte-identical, so what this file pins is that the module still carries the INLINE ENGINE's numbers
// and arithmetic - and above all THE CLOCK: the stroke is the NARRATOR's (CAPABILITIES "Record-document
// species"), so every instant below is derived from the word ONSETS the take handed us, never from a
// characters-per-second dial. The fixture is the `record-typewriter` golden's own payload, so the two frames
// the parent read are pinned here as numbers as well as pixels.
import { test } from "node:test";
import assert from "node:assert/strict";
import { RECORD, recordTyped, recordSpan, recordTypeClock, recordCut, recordSweep, recordLanded,
         paintRecord } from "../../scripts/species/record.mjs";

const near = (a, b, eps = 1e-9) => Math.abs(a - b) <= eps;

// the `record-typewriter` golden's payload, verbatim (tests/golden/build_golden_sources.py REC_WORDS / REC_HL / REC_END)
const WORDS = [["The", 5.00], ["record", 5.34], ["types", 5.72], ["its", 6.06], ["quotation", 6.30],
               ["word", 6.88], ["by", 7.22], ["word,", 7.50], ["on", 7.90], ["the", 8.12],
               ["narrator's", 8.36], ["own", 8.90], ["clock.", 9.16]];
const REC = { words: WORDS, hl: [4, 4], end: 9.66 };
const FRAME_T = 7.62;      // the golden's judged instant
const PROOF_T = 10.26;     // record-typewriter@proof-attr: the landing

// ---------------------------------------------------------------- the dials, as the inline code carried them
test("every dial is the inline engine's literal, to the digit, and frozen", () => {
  assert.ok(Object.isFrozen(RECORD));
  assert.equal(RECORD.TYPE_FRAC, 0.72, "const span = Math.max(0.08, (next - ts) * 0.72)");
  assert.equal(RECORD.SPAN_MIN, 0.08, "the same Math.max's floor");
  assert.equal(RECORD.SWEEP_S, 0.2, "const swept = Math.max(0, Math.min(1, (t - ts) / 0.2))");
  assert.equal(RECORD.ATTR_AFTER, 0.15, 'st.attr.classList.toggle("shown", t > r.end + 0.15)');
  assert.equal(RECORD.SRC_AFTER, 0.45, 'st.src.classList.toggle("shown", t > r.end + 0.45)');
  assert.equal(RECORD.HL_CLASS, "hw");
  assert.equal(RECORD.CUR_CLASS, "pcur");
});

// ---------------------------------------------------------------- THE TYPE CLOCK AGAINST THE WORD ONSETS
test("no word before the first onset, and each lands on ITS OWN onset", () => {
  assert.equal(recordTyped(WORDS, 4.99), -1);
  assert.equal(recordTyped(WORDS, 5.00), 0, "the onset itself is typed (<=, not <)");
  for (let k = 0; k < WORDS.length; k++) {
    assert.equal(recordTyped(WORDS, WORDS[k][1]), k, `word ${k} lands at ${WORDS[k][1]}`);
    assert.equal(recordTyped(WORDS, WORDS[k][1] - 1e-6), k - 1, `and not a frame earlier`);
  }
  assert.equal(recordTyped(WORDS, 99), WORDS.length - 1, "past the end, the quotation stands whole");
});

test("a word types over 0.72 of its own gap to the NEXT onset - the narrator's clock, not a characters/s dial", () => {
  const ts = WORDS[7][1], next = WORDS[8][1];           // "word," 7.50 -> "on" 7.90: a 0.40 s gap
  assert.ok(near(recordSpan(ts, next), 0.288), "0.40 * 0.72");
  assert.equal(recordTypeClock(ts, ts, next), 0, "nothing of it at its onset");
  assert.ok(near(recordTypeClock(ts + 0.144, ts, next), 0.5), "half way through its own span");
  assert.equal(recordTypeClock(ts + 0.288, ts, next), 1, "whole by onset + span, before the next word begins");
  assert.equal(recordTypeClock(ts + 5, ts, next), 1, "and clamped after it");
  assert.equal(recordTypeClock(ts - 5, ts, next), 0, "and before it");
  // the same word at half the gap types twice as fast: the stroke follows the take
  assert.ok(recordSpan(ts, ts + 0.20) < recordSpan(ts, next), "a hurried word is a hurried stroke");
});

test("two onsets a frame apart still get a stroke: the span floors at SPAN_MIN", () => {
  assert.equal(recordSpan(7.50, 7.51), RECORD.SPAN_MIN, "0.01 * 0.72 is under the floor");
  assert.equal(recordSpan(7.50, 7.50), RECORD.SPAN_MIN, "and so is a zero gap - never a divide by zero");
});

test("the CUT is whole glyphs of a string slice - never a half-drawn character", () => {
  assert.equal(recordCut("word,", 0), 0);
  assert.equal(recordCut("word,", 1), 5);
  assert.equal(recordCut("word,", 0.41666666666666663), 2, "the golden's own instant: `wo`");
  for (let n = 0; n <= 20; n++) {
    const c = recordCut("quotation", n / 20);
    assert.ok(Number.isInteger(c) && c >= 0 && c <= 9);
  }
});

// ---------------------------------------------------------------- THE HIGHLIGHT WINDOW
test("the marker sweeps one word over SWEEP_S from that word's onset, on a cubic-out", () => {
  const ts = WORDS[4][1];                                // "quotation" 6.30 - the pulled phrase
  assert.equal(recordSweep(ts, ts), 0, "no stroke at the onset");
  assert.ok(near(recordSweep(ts + 0.1, ts), 1 - Math.pow(0.5, 3)), "0.875 at the half - out-cubic, front-loaded");
  assert.ok(recordSweep(ts + 0.1, ts) > 0.5, "the marker leads the word, as a highlighter does");
  assert.equal(recordSweep(ts + RECORD.SWEEP_S, ts), 1, "landed by onset + SWEEP_S");
  assert.equal(recordSweep(ts + 4, ts), 1, "and held, clamped");
  assert.equal(recordSweep(ts - 4, ts), 0, "and nothing before the word is said");
});

// ---------------------------------------------------------------- THE LANDING
test("the attribution and the source line hang off the quotation's own end", () => {
  assert.deepEqual(recordLanded(REC.end, REC.end), { attr: false, src: false }, "not while the line is still being said");
  assert.deepEqual(recordLanded(REC.end + 0.2, REC.end), { attr: true, src: false }, "who said it, first");
  assert.deepEqual(recordLanded(REC.end + 0.5, REC.end), { attr: true, src: true }, "then where it is on file");
});

// ---------------------------------------------------------------- THE PAINTER, over a fake DOM
const fakeDOM = () => {
  const el = () => ({ className: "", textContent: "", style: {}, kids: [],
                      append(...n) { this.kids.push(...n); } });
  globalThis.document = { createDocumentFragment: el, createElement: el,
                          createTextNode: (s) => ({ text: s }) };
  const flag = () => ({ shown: null, classList: { toggle: function (c, v) { this.owner.shown = v; } } });
  const mk = () => { const f = flag(); f.classList.owner = f; return f; };
  const st = { r: REC, q: { frag: null, replaceChildren(f) { this.frag = f; } }, attr: mk(), src: mk() };
  return st;
};
const textOf = (st) => st.q.frag.kids.map((n) => ("text" in n ? n.text : n.textContent)).join("");
const marks = (st) => st.q.frag.kids.filter((n) => n.className === RECORD.HL_CLASS);

test("THE GOLDEN'S INSTANT (record-typewriter, t 7.62): seven words whole, the eighth cut to `wo`", () => {
  const st = fakeDOM();
  paintRecord(st, FRAME_T);
  assert.equal(textOf(st), "The record types its quotation word by wo");
  assert.equal(marks(st).length, 1, "one word under the marker (hl [4, 4])");
  assert.equal(marks(st)[0].textContent, "quotation", "and the space after it is NOT in the stroke");
  assert.equal(marks(st)[0].style.backgroundSize, "100% 100%", "swept 1.32 s before the instant, at rest");
  assert.equal(st.attr.shown, false);
  assert.equal(st.src.shown, false);
  assert.equal(st.q.frag.kids.at(-1).className, RECORD.CUR_CLASS, "the cursor is always last");
});

test("the space after the pulled phrase is a text node OUTSIDE the stroke (Tokyo 2026-09-10)", () => {
  const st = fakeDOM();
  paintRecord(st, FRAME_T);
  const after = st.q.frag.kids[st.q.frag.kids.indexOf(marks(st)[0]) + 1];
  assert.deepEqual(after, { text: " " }, "a marker that swallows the space runs on past the quotation");
});

test("THE PROOF INSTANT (@proof-attr, t 10.26): the quotation whole, both feet shown", () => {
  const st = fakeDOM();
  paintRecord(st, PROOF_T);
  assert.equal(textOf(st), "The record types its quotation word by word, on the narrator's own clock.");
  assert.equal(st.attr.shown, true);
  assert.equal(st.src.shown, true);
});

test("before the first onset the paper is empty but for the cursor - and nothing is stored between frames", () => {
  const st = fakeDOM();
  paintRecord(st, 0);
  assert.equal(textOf(st), "");
  paintRecord(st, PROOF_T);
  const whole = textOf(st);
  paintRecord(st, FRAME_T);                       // scrub BACK: the frame is a pure function of t
  assert.equal(textOf(st), "The record types its quotation word by wo");
  paintRecord(st, PROOF_T);
  assert.equal(textOf(st), whole, "and forward again to the same pixels");
});
