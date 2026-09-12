/* SPACE: stage */
/* species/agenda.mjs - THE NUMBERED AGENDA (P52 T8; EXPLORATION-REVIEW-2026-09-10.md:58, the Bravos
   "China's Gameplan  1 | 2" board: numbered rows revealed in turn). SOURCE OF TRUTH, inlined into the
   scene-evidence player by sync_kinetics.py between KINETICS:BEGIN agenda and KINETICS:END, AFTER idle -
   it imports it, and the import order IS the region order.
   THE MODULE RULE (the operator, 2026-09-11): a species is a module here, never a branch in the engine's
   body. The last statement registers the painter in SPECIES_PAINTERS; node, where no such registry exists,
   still imports the file for the pure math below.

   WHEN: the sentence SETS AN AGENDA - "two numbers", "three things", "here's what nobody says". The review
   says `figure` plus `note` COULD compose it; the module is what makes it ONE declaration, so the rows
   cannot drift out of step with the count the sentence gave.

   THE LAW, all of it a pure function of t:
     the block  - 2 to 4 rows stacked in the declared box, each ROW_H tall at the block's own scale k (one
                  scale for the whole block: a row is never a different size from its neighbour). The rows
                  are laid out for the FULL agenda from the first frame, so a row that arrives never pushes
                  the one above it - the list was always that long, the viewer just had not been shown it.
     a row      - revealed on its OWN WORD (`rows[i].at`, or STEP after the row before it when the author
                  gives the block one `at`): the NUMBER is written first, a hairline RULE draws under the row
                  left to right by the nib (kinetics/stroke.mjs's curvature law through the engine's drawOn),
                  and the text rises ROW_DY to its place and fades in over ROW_S. A list being written, not a
                  list appearing.
     hold       - every row carries a NAMED idle (E49, one of IDLE_KINDS; `breath` unless the row names
                  another), each at its OWN phase off the seed, so the agenda is never bit-identical frame to
                  frame and no two rows breathe in step. `idle: "none"` is declared stillness.
   Nothing is stored: every visual reads from t and the rows' own `at`, so a scrubbed frame is the played
   frame. The dials below are ours to tune (42 s42.5), not findings. */
import { idleXf } from "../kinetics/idle.mjs";

export const AGENDA = Object.freeze({
  MIN_ROWS: 2,       /* one row is a note, not an agenda; the compiler holds this bound and so does the layout */
  MAX_ROWS: 4,       /* ... and five is a checklist nobody holds in their head at phone size (doc 29 s9.33's recap) */
  ROW_H: 132,        /* one row's own height in STAGE px: the number, its text and the air under the rule */
  NUM_W: 92,         /* the number's column - a fixed gutter, so every text starts on the same x */
  NUM_SIZE: 64,      /* the numeral's type: the biggest thing in the row (it is what the sentence counted) */
  TEXT_SIZE: 54,     /* ... the row's own words ... */
  SUB_SIZE: 34,      /* ... and its sub, when the sentence gave the row two halves */
  ROW_S: 0.42,       /* the text's rise and fade - a row arrives inside a word, never across two */
  ROW_DY: 26,        /* ... from this far below its place */
  RULE_S: 0.5,       /* the hairline under the row, drawn by the nib on its own clock */
  RULE_DY: 22,       /* ... that far under the row's baseline */
  NUM_LEAD: 0.12,    /* the number is written this long before the text starts rising: the row is numbered, then said */
  STEP: 0.34,        /* the default word pitch when the block names one `at` [DERIVED: doc 46, 178 WPM] */
  MIN_K: 0.45,       /* the smallest the block may be scaled to before it stops being read - under it the box was too small */
});

const ag01 = (v) => Math.min(1, Math.max(0, v));
const agEase = (u) => 1 - Math.pow(1 - ag01(u), 3);   /* the species ease, written here so the math needs no context */

/* THE ROWS as the painter reads them: the author's list, numbered from 1 unless a row names its own number,
   each with the instant it is revealed (its own `at`, else STEP after the row before). */
export const agendaRows = (sp) => {
  const rows = Array.isArray(sp.rows) ? sp.rows.slice(0, AGENDA.MAX_ROWS) : [];
  const step = Number.isFinite(+sp.step) && +sp.step > 0 ? +sp.step : AGENDA.STEP;
  return rows.map((r, i) => ({
    i,
    n: Number.isFinite(+((r || {}).n)) ? String(+r.n) : String(i + 1),
    text: (r || {}).text == null ? "" : String(r.text),
    sub: (r || {}).sub == null ? "" : String(r.sub),
    at: Number.isFinite(+((r || {}).at)) ? +r.at : +sp.at + i * step,
  }));
};

/* THE BLOCK in a declared box: one scale for every row, and each row's own baseline in stage px. The block is
   laid out for the FULL list from the first frame - the rows do not close up as they arrive. */
export const agendaLayout = (box, n) => {
  const N = Math.max(1, Math.min(AGENDA.MAX_ROWS, n | 0));
  const h = N * AGENDA.ROW_H, w = AGENDA.NUM_W + 12 * AGENDA.TEXT_SIZE;   /* the widest row we lay out for: a dozen ems of text */
  const k = Math.max(AGENDA.MIN_K, Math.min(1, (box.h || h) / h, (box.w || w) / w));
  const x = box.x + (box.w ? Math.max(0, (box.w - w * k) / 2) : 0);
  const y = box.y + (box.h ? Math.max(0, (box.h - h * k) / 2) : 0);
  const rows = [];
  for (let i = 0; i < N; i++) rows.push({ i, x, y: y + (i + 0.62) * AGENDA.ROW_H * k,
                                          numX: x, textX: x + AGENDA.NUM_W * k,
                                          ruleY: y + (i + 0.62) * AGENDA.ROW_H * k + AGENDA.RULE_DY * k,
                                          ruleW: (AGENDA.NUM_W + 9 * AGENDA.TEXT_SIZE) * k });
  return { k, w, h, rows };
};

/* ONE ROW's arrival at t: the number's write, the rule's draw and the text's rise, all off the row's own word. */
export const agendaRowF = (sp, t, i) => {
  const row = agendaRows(sp)[i | 0];
  if (!row) return { num: 0, rule: 0, text: 0, dy: AGENDA.ROW_DY, fade: 0 };
  const d = t - row.at;
  const num = ag01(d / (AGENDA.ROW_S * 0.6));
  const text = ag01((d - AGENDA.NUM_LEAD) / AGENDA.ROW_S);
  return { num, rule: ag01(d / AGENDA.RULE_S), text,
           dy: AGENDA.ROW_DY * (1 - agEase(text)), fade: text };
};

/* ONE ENTRY: every row's arrival at t, and how many rows are fully in - from the declaration alone. */
export const agendaPose = (sp, t) => {
  const rows = agendaRows(sp).map((r, i) => Object.assign({ row: r }, agendaRowF(sp, t, i)));
  return { rows, shown: rows.filter((r) => r.fade > 0).length, done: rows.filter((r) => r.fade >= 1).length };
};

/* THE PAINTER. ctx is the engine's species context (SPECIES_PAINTERS in the player): the declaration, the
   clock, the layer and the shared helpers by name. One group per row, its transform carrying the rise and the
   row's own idle - nothing rotates, and the rule is drawn by the same hand every other mark on the stage uses. */
export function paintAgenda(ctx) {
  const { sp, t, svg, el, resolveTarget, drawOn, hash, idle, seed, si } = ctx;
  const b = resolveTarget(sp.target);
  if (!b) return;   /* the targeting law: no resolved target, nothing painted */
  const pose = agendaPose(sp, t), lay = agendaLayout(b, pose.rows.length);
  const kind = sp.idle === "none" ? "none" : (sp.idle || "breath");
  const g = el("g", "", svg, {});
  pose.rows.forEach((r, i) => {
    if (r.num <= 0) return;   /* a row before its word is not on the board at all */
    const place = lay.rows[i];
    const ix = kind === "none" ? { scale: 1, dx: 0, dy: 0 } : idle(kind, t, hash(seed | 0, (si | 0) * 17 + i, 991));
    const rg = el("g", "", g, { transform: "translate(" + ix.dx.toFixed(2) + " " + (r.dy * lay.k + ix.dy).toFixed(2) + ")" });
    const num = el("text", "agnum", rg, { x: place.numX.toFixed(1), y: place.y.toFixed(1),
                                          opacity: r.num.toFixed(3), "font-size": (AGENDA.NUM_SIZE * lay.k * ix.scale).toFixed(1) });
    num.textContent = r.row.n;
    if (r.rule > 0) {   /* the hairline the hand draws under the row, left to right */
      const d = "M" + place.numX.toFixed(1) + " " + place.ruleY.toFixed(1) + " L" + (place.numX + place.ruleW).toFixed(1) + " " + place.ruleY.toFixed(1);
      drawOn(el("path", "agrule", rg, { d }), r.rule);
    }
    if (r.fade > 0 && r.row.text) {
      const tx = el("text", "agrow", rg, { x: place.textX.toFixed(1), y: place.y.toFixed(1),
                                           opacity: r.fade.toFixed(3), "font-size": (AGENDA.TEXT_SIZE * lay.k * ix.scale).toFixed(1) });
      tx.textContent = r.row.text;
    }
    if (r.fade > 0 && r.row.sub) {
      const sb = el("text", "agsub", rg, { x: place.textX.toFixed(1), y: (place.ruleY + AGENDA.SUB_SIZE * lay.k).toFixed(1),
                                           opacity: (r.fade * 0.9).toFixed(3), "font-size": (AGENDA.SUB_SIZE * lay.k).toFixed(1) });
      sb.textContent = r.row.sub;
    }
  });
}

/* the module rule's registration: a plain assignment (inline_text keeps it), guarded so `node --test` can
   import this file for the math above without the engine's registry */
if (typeof SPECIES_PAINTERS !== "undefined") SPECIES_PAINTERS.agenda = paintAgenda;
