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

   THE PAGE FORM (`form: "page"`, P61 T8) - the operator, E99 s16: *"still need the beautified agenda page,
   which i think we discussed as basically just being the plate version of our list effect."* The form above is
   the DOCK form: a block parked in the box it was given, which at three rows left the upper two thirds of the
   plate empty (`species-proof@proof-agenda.png`, BACKLOG R26-80). The page form is the SAME list on a plate of
   its own, and the model is Steel and Paper's three-question TEST card (the operator's pointer, E93 s3): a
   mounted ground, a title that says what the list is, a mark per row, and the whole thing filling its box.
     the board  - the block takes the WHOLE box, inset by PAGE_PAD, with the TITLE's room reserved at the top
                  when the block names one. The compiler refuses a page form whose region is smaller than
                  AGENDA_PAGE_COVER of the frame (build_scene_timeline_f._validate_agenda), so "the page fills
                  its own plate" is held at compile time and not only by the painter.
     a row      - the rows divide the remaining height EXACTLY between them: N rows, one pitch, no air left
                  over, and ONE scale k for the block as before (rowH / ROW_H, capped at PAGE_MAX_K - the dock
                  form's cap of 1 is what kept the rows body-sized on a plate). A row carries its own PLATE
                  (the ground the test card has and the dock form has not), its numeral in a MEDALLION the nib
                  draws, its text, its sub set as a FIGURE rather than grey furniture, and its rule drawn full
                  width along its bottom edge by the same hand the dock form uses.
     the stamp  - E93: *"i think agenda rows should carry icons, the icons can be stamped on after each sentence
                  is read"*. The row's CATALOGUED icon (an `asset_id` of
                  assets/icons/finance_icons_catalog.v1.json, `render_eligible` only - E94) lands at the row's
                  right PAGE_STAMP_LAG after that row's sentence is FULLY written, falling from PAGE_STAMP_FROM
                  over PAGE_STAMP_S and taking the stop-motion SQUASH on impact (PAGE_SQUASH, relaxing over
                  PAGE_SETTLE_S). Never before its sentence has been read: the stamp's whole clock hangs off
                  `agendaRowRead`, which is the row's own word plus NUM_LEAD plus ROW_S.
                  The glyph is the OPERATOR'S OWN cutout carried in the asset map as `prop:<asset_id>` (PROP_KEY
                  here, PROP_PREFIX in the compiler) - this module never invents an image and never reads a path.
   The page form paints NEW classes (`agplate`, `agmed`, `agtitle`, `agfig`, `agicon`) whose look is set by the
   painter as presentation attributes rather than in the player's CSS, because P61 T8's write set does not carry
   the template; the four dials PAGE_INK / PAGE_EDGE / PAGE_GOLD / PAGE_CHALK restate the template's own species
   palette (#05131e, #8a94a0, #F5B72E, #F2F2F2) so the page form and the dock form are visibly one species.
   THE DOCK FORM IS UNTOUCHED: `form` absent takes exactly the code below, so every committed golden is
   byte-identical.
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
  /* ---- THE PAGE FORM (P61 T8; E99 s16 the plate version of the list, E93 the stamped icon, R26-80) ---- */
  PAGE_FORM: "page",       /* the ONE word `form` takes - the compiler refuses any other by name */
  PROP_KEY: "prop:",       /* the asset map's key for a CATALOGUED cutout (build_scene_timeline_f.PROP_PREFIX) */
  PAGE_PAD: 48,            /* the daylight between the board and the block, in STAGE px */
  PAGE_TITLE_H: 158,       /* the title's ROOM, reserved at the top of the board before a row is placed ... */
  PAGE_TITLE_SIZE: 62,     /* ... and the title's own type (the test card's lesson: a list says what it is) */
  PAGE_TITLE_K: 1.15,      /* ... which follows the block's scale only this far: a title names the list, it never shouts over it */
  PAGE_MAX_K: 1.8,         /* the page form scales the rows UP to fill the board; the dock form is capped at 1 */
  PAGE_ROW_PAD: 28,        /* the daylight inside a row: the medallion off the plate's edge, the text off the medallion */
  PAGE_MED: 0.30,          /* the numeral's medallion radius, as a share of its row's height ... */
  PAGE_MED_W: 3.5,         /* ... and the ring's width, the nib drawing it on the row's own clock */
  PAGE_ICON: 0.70,         /* the stamped icon's side, as a share of its row's height ... */
  PAGE_ICON_GAP: 44,       /* ... and the daylight kept off the row's right edge (wider than the stamp's own overshoot, so a falling icon never crosses its plate) */
  PAGE_TEXT_Y: 0.46,       /* the row text's baseline, as a share of the row's height ... */
  PAGE_SUB_Y: 0.79,        /* ... and the sub's under it (one place for both, so no row is laid out differently) */
  PAGE_PLATE_A: 0.30,      /* the row plate's ground, at this opacity - a mount, never a box that fights the type */
  PAGE_PLATE_R: 14,        /* ... with this corner */
  PAGE_STAMP_LAG: 0.12,    /* E93: the breath between the row's sentence being READ and its icon landing ... */
  PAGE_STAMP_S: 0.26,      /* ... the fall's own clock ... */
  PAGE_STAMP_FROM: 1.45,   /* ... the scale it falls FROM (a stamp comes down onto the page, it never grows out of it) ... */
  PAGE_SETTLE_S: 0.14,     /* ... and the squash relaxing after the impact */
  PAGE_SQUASH: 0.14,       /* the stop-motion squash ON IMPACT: wider by this much, and as much shorter */
  PAGE_FADE_S: 0.1,        /* the stamp's opacity ramp - never a pop out of nothing */
  PAGE_INK: "#05131e",     /* the row plate's ground - the count array's own tile ink (the template's `.catile`) */
  PAGE_EDGE: "#8a94a0",    /* ... and the muted-ink outline every species frame uses (the template's `.agrule`) */
  PAGE_GOLD: "#F5B72E",    /* the medallion's ring: the numeral's own sunflower (the template's `.agnum`) */
  PAGE_CHALK: "#F2F2F2",   /* the title's chalk (the template's `.agrow`) */
  PAGE_HALO: "rgba(27,30,35,.85)",      /* the type's halo, as every species' type carries it */
  PAGE_FACE: "Inter, Arial, sans-serif",  /* the house sans - set here because the new classes have no CSS */
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
    icon: (r || {}).icon == null ? "" : String(r.icon),   /* P61 T8 / E93: the page form's catalogued stamp; "" in the dock form */
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

/* IS THIS THE PAGE FORM? One word, and only one: `form: "page"`. Anything else is the dock form here and a
   refusal in the compiler - a species that silently ignores a word it was given is a species that lies. */
export const agendaIsPage = (sp) => String((sp || {}).form || "") === AGENDA.PAGE_FORM;

/* THE PAGE's BLOCK in the board it was given: the rows divide the height that is left after the title's room
   EXACTLY between them, so a three-row page is a three-row PAGE and not a paragraph in a corner. One scale k
   for the whole block, as in the dock form - a row is never a different size from its neighbour. Every number
   below is a pure function of the box, the count and whether the block named a title. */
export const agendaPageLayout = (box, n, hasTitle) => {
  const N = Math.max(1, Math.min(AGENDA.MAX_ROWS, n | 0));
  const pad = AGENDA.PAGE_PAD;
  const x = (box.x || 0) + pad, w = Math.max(1, (box.w || 0) - 2 * pad);
  const top = (box.y || 0) + pad + (hasTitle ? AGENDA.PAGE_TITLE_H : 0);
  const h = Math.max(1, (box.y || 0) + (box.h || 0) - pad - top);
  const rowH = h / N;
  const icon = rowH * AGENDA.PAGE_ICON, medR = rowH * AGENDA.PAGE_MED;
  const medX = x + AGENDA.PAGE_ROW_PAD + medR;
  const textX = medX + medR + AGENDA.PAGE_ROW_PAD;
  const textW = Math.max(1, x + w - icon - AGENDA.PAGE_ICON_GAP - AGENDA.PAGE_ROW_PAD - textX);
  const k = Math.max(AGENDA.MIN_K, Math.min(AGENDA.PAGE_MAX_K, rowH / AGENDA.ROW_H, textW / (11 * AGENDA.TEXT_SIZE)));
  const rows = [];
  for (let i = 0; i < N; i++) {
    const rt = top + i * rowH;
    rows.push({ i, x, w, top: rt, h: rowH, medX, medY: rt + rowH / 2, medR,
                numX: medX, numY: rt + rowH / 2 + AGENDA.NUM_SIZE * k * 0.35,
                textX, textW, y: rt + rowH * AGENDA.PAGE_TEXT_Y, subY: rt + rowH * AGENDA.PAGE_SUB_Y,
                ruleY: rt + rowH, ruleW: w,
                iconX: x + w - AGENDA.PAGE_ICON_GAP - icon, iconY: rt + (rowH - icon) / 2, iconS: icon });
  }
  return { k, x, w, top, h, rowH, rows, page: true,
           titleX: x + AGENDA.PAGE_ROW_PAD, titleY: (box.y || 0) + pad + AGENDA.PAGE_TITLE_SIZE,
           titleRuleY: (box.y || 0) + pad + AGENDA.PAGE_TITLE_H * 0.72 };
};

/* WHEN a row's SENTENCE HAS BEEN READ (E93's own instant): its own word, plus the lead the number takes, plus
   the rise - the instant `agendaRowF` reaches fade 1. Null for a row that is not there. */
export const agendaRowRead = (sp, i) => {
  const row = agendaRows(sp)[i | 0];
  return row ? row.at + AGENDA.NUM_LEAD + AGENDA.ROW_S : null;
};

/* THE STAMP at t (E93), a pure function of the row's own read instant: nothing at all until PAGE_STAMP_LAG
   after the sentence is read, then the icon falls from PAGE_STAMP_FROM over PAGE_STAMP_S and SQUASHES on
   impact, the squash relaxing over PAGE_SETTLE_S. `on` is the whole claim the test reads: an icon is never on
   the page before its sentence has been. */
export const agendaStampF = (sp, t, i) => {
  const read = agendaRowRead(sp, i);
  if (read === null) return { on: false, u: 0, fade: 0, scale: AGENDA.PAGE_STAMP_FROM, sx: 1, sy: 1 };
  const d = t - (read + AGENDA.PAGE_STAMP_LAG);
  if (!(d > 0)) return { on: false, u: 0, fade: 0, scale: AGENDA.PAGE_STAMP_FROM, sx: 1, sy: 1 };
  const u = ag01(d / AGENDA.PAGE_STAMP_S), e = agEase(u);
  const rel = ag01((d - AGENDA.PAGE_STAMP_S) / AGENDA.PAGE_SETTLE_S);
  const sq = u >= 1 ? AGENDA.PAGE_SQUASH * (1 - rel) : 0;   /* the squash begins AT the impact - stop motion, not a cushion */
  return { on: true, u, fade: ag01(d / AGENDA.PAGE_FADE_S),
           scale: AGENDA.PAGE_STAMP_FROM + (1 - AGENDA.PAGE_STAMP_FROM) * e, sx: 1 + sq, sy: 1 / (1 + sq) };
};

/* THE PAINTER. ctx is the engine's species context (SPECIES_PAINTERS in the player): the declaration, the
   clock, the layer and the shared helpers by name. One group per row, its transform carrying the rise and the
   row's own idle - nothing rotates, and the rule is drawn by the same hand every other mark on the stage uses. */
export function paintAgenda(ctx) {
  if (agendaIsPage(ctx.sp)) return paintAgendaPage(ctx);   /* P61 T8: the plate version; the dock form below is untouched */
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

/* THE PAGE PAINTER (P61 T8). The same context, the same helpers, the same targeting law - a different SPACE to
   fill: the whole board rather than a parked block. Row by row, in the order the test card reads: the mount, the
   medallion the nib draws, the numeral, the text, the sub as a figure, the rule along the row's own bottom edge,
   and E93's icon stamped on once that row's sentence has been read. Nothing rotates and nothing is stored. */
export function paintAgendaPage(ctx) {
  const { sp, t, svg, el, A, resolveTarget, drawOn, hash, idle, seed, si } = ctx;
  const b = resolveTarget(sp.target);
  if (!b) return;   /* the targeting law: no resolved target, nothing painted */
  const pose = agendaPose(sp, t), rows = agendaRows(sp);
  const title = sp.title == null ? "" : String(sp.title);
  const lay = agendaPageLayout(b, pose.rows.length, !!title);
  const kind = sp.idle === "none" ? "none" : (sp.idle || "breath");
  const g = el("g", "", svg, {});
  if (title) {   /* the title's room: written on the block's own word, before the first row is numbered */
    const tf = ag01((t - +sp.at) / AGENDA.ROW_S);
    if (tf > 0) {
      const tt = el("text", "agtitle", g, { x: lay.titleX.toFixed(1), y: lay.titleY.toFixed(1), opacity: tf.toFixed(3),
                                           "font-size": (AGENDA.PAGE_TITLE_SIZE * Math.min(lay.k, AGENDA.PAGE_TITLE_K)).toFixed(1), "font-family": AGENDA.PAGE_FACE,
                                           "font-weight": "800", "letter-spacing": "1.5", fill: AGENDA.PAGE_CHALK,
                                           "paint-order": "stroke", stroke: AGENDA.PAGE_HALO, "stroke-width": "9" });
      tt.textContent = title;
      const d = "M" + lay.titleX.toFixed(1) + " " + lay.titleRuleY.toFixed(1) +
                " L" + (lay.titleX + lay.w - 2 * AGENDA.PAGE_ROW_PAD).toFixed(1) + " " + lay.titleRuleY.toFixed(1);
      drawOn(el("path", "agrule", g, { d }), tf);   /* the title's own rule closes its room off the list */
    }
  }
  pose.rows.forEach((r, i) => {
    if (r.num <= 0) return;   /* a row before its word is not on the board at all */
    const place = lay.rows[i];
    const ix = kind === "none" ? { scale: 1, dx: 0, dy: 0 } : idle(kind, t, hash(seed | 0, (si | 0) * 17 + i, 991));
    const rg = el("g", "", g, { transform: "translate(" + ix.dx.toFixed(2) + " " + (r.dy * lay.k + ix.dy).toFixed(2) + ")" });
    el("rect", "agplate", rg, { x: place.x.toFixed(1), y: place.top.toFixed(1), width: place.w.toFixed(1),
                                height: place.h.toFixed(1), rx: AGENDA.PAGE_PLATE_R, fill: AGENDA.PAGE_INK,
                                opacity: (r.num * AGENDA.PAGE_PLATE_A).toFixed(3) });
    drawOn(el("circle", "agmed", rg, { cx: place.medX.toFixed(1), cy: place.medY.toFixed(1), r: place.medR.toFixed(1),
                                       fill: "none", stroke: AGENDA.PAGE_GOLD, "stroke-width": AGENDA.PAGE_MED_W }), r.num);
    const num = el("text", "agnum", rg, { x: place.numX.toFixed(1), y: place.numY.toFixed(1), "text-anchor": "middle",
                                          opacity: r.num.toFixed(3), "font-size": (AGENDA.NUM_SIZE * lay.k * ix.scale).toFixed(1) });
    num.textContent = r.row.n;
    if (r.rule > 0) {   /* the row's own bottom edge, drawn left to right by the hand the dock form uses */
      const d = "M" + place.x.toFixed(1) + " " + place.ruleY.toFixed(1) +
                " L" + (place.x + place.ruleW).toFixed(1) + " " + place.ruleY.toFixed(1);
      drawOn(el("path", "agrule", rg, { d }), r.rule);
    }
    if (r.fade > 0 && r.row.text) {
      const tx = el("text", "agrow", rg, { x: place.textX.toFixed(1), y: place.y.toFixed(1),
                                           opacity: r.fade.toFixed(3), "font-size": (AGENDA.TEXT_SIZE * lay.k * ix.scale).toFixed(1) });
      tx.textContent = r.row.text;
    }
    if (r.fade > 0 && r.row.sub) {   /* R26-80: the sub is a FIGURE on a page, never grey furniture in a corner */
      const sb = el("text", "agfig", rg, { x: place.textX.toFixed(1), y: place.subY.toFixed(1), opacity: (r.fade * 0.95).toFixed(3),
                                           "font-size": (AGENDA.SUB_SIZE * lay.k).toFixed(1), "font-family": AGENDA.PAGE_FACE,
                                           "font-weight": "700", fill: AGENDA.PAGE_GOLD, "paint-order": "stroke",
                                           stroke: AGENDA.PAGE_HALO, "stroke-width": "6" });
      sb.textContent = r.row.sub;
    }
    const st = agendaStampF(sp, t, i);   /* E93: the icon, once the sentence has been read - and not one frame before */
    const uri = A ? A[AGENDA.PROP_KEY + ((rows[i] || {}).icon || "")] : null;
    if (st.on && uri) {
      const cx = place.iconX + place.iconS / 2, cy = place.iconY + place.iconS / 2;
      el("image", "agicon", rg, { x: place.iconX.toFixed(1), y: place.iconY.toFixed(1),
                                  width: place.iconS.toFixed(1), height: place.iconS.toFixed(1),
                                  href: uri, preserveAspectRatio: "xMidYMid meet", opacity: st.fade.toFixed(3),
                                  transform: "translate(" + cx.toFixed(1) + " " + cy.toFixed(1) + ") scale(" +
                                             (st.scale * st.sx).toFixed(4) + " " + (st.scale * st.sy).toFixed(4) +
                                             ") translate(" + (-cx).toFixed(1) + " " + (-cy).toFixed(1) + ")" });
    }
  });
}

/* the module rule's registration: a plain assignment (inline_text keeps it), guarded so `node --test` can
   import this file for the math above without the engine's registry */
if (typeof SPECIES_PAINTERS !== "undefined") SPECIES_PAINTERS.agenda = paintAgenda;
