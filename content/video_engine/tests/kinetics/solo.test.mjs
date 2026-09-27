// P69 T37 - SOLO (the Bravos harvest v2 rank 2: A12 "peers ghost, one series stays lit", A49 "one bar ignites, the
// rest dim"). On its word every other series or bar of the page mutes to E67's dim and the named one keeps its ink;
// `unsolo` - or a verb that replaces the page - restores. These tests pin the dial, the events, the alpha law (a pure
// function of t, continuous across a hand-over), the painter's writes and the module rule.
import { test } from "node:test";
import assert from "node:assert/strict";
import { SOLO, SOLO_ACCENT, soloKeyOf, soloEvents, soloAlpha, soloLift, soloWrite, paintSolo } from "../../scripts/species/solo.mjs";

const near = (a, b, eps = 1e-9) => Math.abs(a - b) <= eps;
const solo = (o = {}) => Object.assign({ kind: "solo", at: 10, dur: 0.5, series: 1 }, o);

test("the dim is E99 s117's: harder than E67's 0.45, a thinner muted stroke and a lifted named halo (P69 T37b)", () => {
  assert.ok(SOLO.DIM < 0.45 && SOLO.DIM > 0.2, "fades the others harder than E67's 0.45 (s117 (2))");
  assert.ok(SOLO.THIN > 0 && SOLO.THIN < 1, "and thinner");
  assert.ok(SOLO.LIFT > 1, "and lifts the named line's bloom further");
  assert.ok(SOLO.MIN_S > 0 && SOLO.MAX_S > SOLO.MIN_S && SOLO.EPS > 0 && SOLO.EPS < 0.01);
});

// ---------------------------------------------------------------- the events
test("a solo keys the ONE mark it names - a series on a line page, a bar on a bars page", () => {
  assert.equal(soloKeyOf(solo()), "s:1");
  assert.equal(soloKeyOf({ kind: "solo", bar: 2 }), "b:2");
  assert.equal(soloKeyOf({ kind: "unsolo" }), null);
});

test("the events run in time order; a release at the same instant as a solo gives way to it", () => {
  const ev = soloEvents([solo({ at: 14, series: 2 }), solo()], [{ at: 12, dur: 0.4 }, { at: 14, dur: 1 }]);
  assert.deepEqual(ev.map((e) => [e.at, e.key]), [[10, "s:1"], [12, null], [14, null], [14, "s:2"]]);
  assert.ok(ev.every((e) => e.dur > 0));
});

// ---------------------------------------------------------------- the alpha
test("before its word nothing is muted; on it the others ease to DIM and the named one keeps its ink", () => {
  const ev = soloEvents([solo()], []);
  for (const k of ["s:0", "s:1", "s:2"]) assert.equal(soloAlpha(ev, k, 9.99), 1);
  assert.equal(soloAlpha(ev, "s:1", 10.25), 1);
  assert.ok(near(soloAlpha(ev, "s:0", 10.25), 1 - (1 - SOLO.DIM) * 0.5), "min-jerk is symmetric: half the word, half the mute");
  assert.equal(soloAlpha(ev, "s:0", 10.5), SOLO.DIM);
  assert.equal(soloAlpha(ev, "s:2", 60), SOLO.DIM, "and it HOLDS until something restores it");
});

test("a second solo HANDS OVER from where the first left every mark - no jump at its word", () => {
  const ev = soloEvents([solo(), solo({ at: 10.2, series: 2 })], []);
  const eps = 1e-6;
  for (const k of ["s:0", "s:1", "s:2"]) {
    assert.ok(Math.abs(soloAlpha(ev, k, 10.2 - eps) - soloAlpha(ev, k, 10.2 + eps)) < 1e-4, k);
  }
  assert.equal(soloAlpha(ev, "s:2", 11), 1);
  assert.equal(soloAlpha(ev, "s:1", 11), SOLO.DIM);
  assert.equal(soloAlpha(ev, "s:0", 11), SOLO.DIM);
});

test("unsolo restores every mark on its own clock", () => {
  const ev = soloEvents([solo()], [{ at: 20, dur: 1 }]);
  assert.equal(soloAlpha(ev, "s:0", 19.9), SOLO.DIM);
  assert.ok(near(soloAlpha(ev, "s:0", 20.5), SOLO.DIM + (1 - SOLO.DIM) * 0.5));
  assert.equal(soloAlpha(ev, "s:0", 21), 1);
  assert.equal(soloAlpha(ev, "s:1", 20.5), 1, "the named one never moved");
});

test("a solo mutes marks of its OWN kind: a series solo never dims a bar, nor a bar solo a line", () => {
  const ev = soloEvents([solo()], []);
  assert.equal(soloAlpha(ev, "b:0", 11), 1);
  const evb = soloEvents([{ kind: "solo", at: 10, dur: 0.5, bar: 0 }], []);
  assert.equal(soloAlpha(evb, "s:0", 11), 1);
  assert.equal(soloAlpha(evb, "b:1", 11), SOLO.DIM);
});

test("a seek IS the play: the same t gives the same alpha in any order", () => {
  const ev = soloEvents([solo(), solo({ at: 10.3, series: 0 })], [{ at: 12, dur: 0.6 }]);
  const ts = [10.1, 12.3, 10.4, 10.1, 13, 12.3, 9];
  const a = ts.map((t) => ["s:0", "s:1", "s:2"].map((k) => soloAlpha(ev, k, t)).join());
  const b = [...ts].reverse().map((t) => ["s:0", "s:1", "s:2"].map((k) => soloAlpha(ev, k, t)).join()).reverse();
  assert.deepEqual(a, b);
});

// ---------------------------------------------------------------- the painter
const rec = (init = {}) => { const a = { ...init }; return { a, setAttribute: (k, v) => { a[k] = String(v); },
  getAttribute: (k) => (k in a ? a[k] : null), removeAttribute: (k) => { delete a[k]; } }; };

test("a write at full ink REMOVES the attribute - the page before the word is the page with no solo", () => {
  const el = rec({ opacity: SOLO.DIM.toFixed(3) });
  soloWrite(el, "opacity", 1);
  assert.equal(el.getAttribute("opacity"), null);
  soloWrite(el, "opacity", SOLO.DIM);
  assert.equal(el.getAttribute("opacity"), SOLO.DIM.toFixed(3));
  soloWrite(null, "opacity", 0.5);   /* a mark with no such element writes nothing */
});

const linePage = () => {
  const pp = (si, muted = false) => ({ si, muted, p: rec(), tip: rec({ opacity: "1" }), name: rec({ opacity: "1" }) });
  const st = { paths: [pp(0), pp(1), pp(2)], bars: [] };
  st.states = [st, { paths: [pp(0), pp(1)], bars: [] }];   /* a derived chart state (a rescale) carries the same series */
  return st;
};

test("THE PAINTER mutes every other series' stroke, lead point and end tag on EVERY chart state", () => {
  const st = linePage(), sd = { evs: soloEvents([solo()], []), lits: [] };
  paintSolo(sd, 9, st, {});
  for (const S of st.states) for (const pp of S.paths) assert.equal(pp.p.getAttribute("opacity"), null);
  paintSolo(sd, 11, st, {});
  for (const S of st.states) for (const pp of S.paths) {
    const want = pp.si === 1 ? null : SOLO.DIM.toFixed(3);
    assert.equal(pp.p.getAttribute("opacity"), want, "stroke " + pp.si);
    assert.equal(pp.tip.getAttribute("fill-opacity"), want, "tip " + pp.si);
    assert.equal(pp.name.getAttribute("fill-opacity"), want, "tag " + pp.si);
    assert.equal(pp.name.getAttribute("opacity"), "1", "the chart's own reveal channel is never touched");
  }
});

test("THE PAINTER mutes every other bar and its value, and never the bar's name", () => {
  const bar = (i) => ({ i, bar: rec(), val: rec({ opacity: "1" }), lab: rec({ opacity: "1" }), band: i === 0 ? rec() : null });
  const st = { paths: [], bars: [bar(0), bar(1), bar(2)] };
  st.states = [st];
  paintSolo({ evs: soloEvents([{ kind: "solo", at: 10, dur: 0.5, bar: 2 }], []), lits: [] }, 11, st, {});
  assert.equal(st.bars[0].bar.getAttribute("opacity"), SOLO.DIM.toFixed(3));
  assert.equal(st.bars[0].band.getAttribute("opacity"), SOLO.DIM.toFixed(3), "a range's band is the bar's own ink");
  assert.equal(st.bars[1].val.getAttribute("fill-opacity"), SOLO.DIM.toFixed(3));
  assert.equal(st.bars[2].bar.getAttribute("opacity"), null);
  for (const b of st.bars) assert.equal(b.lab.getAttribute("fill-opacity"), null, "the category name is the key");
});

test("a lit stretch on a muted series mutes with it (after the light painted this frame); one on the named series keeps its ink", () => {
  const st = linePage();
  const lit = (si) => ({ si, g: rec({ opacity: "1.000" }) });
  const sd = { evs: soloEvents([solo()], []), lits: [lit(0), lit(1)] };
  paintSolo(sd, 11, st, {});
  assert.equal(sd.lits[0].g.getAttribute("opacity"), SOLO.DIM.toFixed(3));
  assert.equal(sd.lits[1].g.getAttribute("opacity"), "1.000");
  sd.lits[0].g.setAttribute("opacity", "0");   /* a light the lit painter hid stays hidden */
  paintSolo(sd, 11, st, {});
  assert.equal(sd.lits[0].g.getAttribute("opacity"), "0.000");
});

test("the painter reaches the engine ONLY through its arguments - no clock, no random, no DOM of its own", async () => {
  const { readFile } = await import("node:fs/promises");
  const src = await readFile(new URL("../../scripts/species/solo.mjs", import.meta.url), "utf-8");
  for (const bad of ["Date.now", "performance.now", "Math.random", "document.", "window.", "requestAnimationFrame"]) {
    assert.ok(!src.includes(bad), bad);
  }
  assert.match(src.split(/\r?\n/)[0], /^\/\* SPACE: page \*\/$/);   // a Windows checkout is CRLF
  assert.match(src.trimEnd().split(/\r?\n/).pop(), /PAGE_PAINTERS\.solo = paintSolo;$/);
});

// ---------------------------------------------------------------- P69 T37b: the lift, the fade and the thinning
test("the LIFT eases the named line in on its word, holds, hands over and eases out on a release (s117 (2))", () => {
  const ev = soloEvents([solo(), solo({ at: 14, series: 2 })], [{ at: 20, dur: 1 }]);
  assert.equal(soloLift(ev, "s:1", 9.9), 0, "nothing before the word");
  assert.ok(near(soloLift(ev, "s:1", 10.25), 0.5), "min-jerk: half the word, half the lift");
  assert.equal(soloLift(ev, "s:1", 11), 1);
  assert.equal(soloLift(ev, "s:0", 11), 0, "an other series is never lifted");
  assert.equal(soloLift(ev, "s:1", 14.5), 0, "the hand-over takes the lift to the next named line");
  assert.equal(soloLift(ev, "s:2", 14.5), 1);
  assert.equal(soloLift(ev, "s:2", 21), 0, "a release lands every line back on its own bloom");
  assert.equal(soloLift(ev, "b:1", 11), 0, "a series solo never lifts a bar");
});

test("the painter hands the engine each line's lift and mute - the named line lifted, the others muted - and nothing else", () => {
  const st = linePage(), calls = [];
  const ctx = { bloom: (S, pp, lift, m, k) => calls.push(["bloom", pp.si, lift, m, k]), thin: (S, pp, m, w) => calls.push(["thin", pp.si, m, w]) };
  paintSolo({ evs: soloEvents([solo()], []), lits: [] }, 11, st, ctx);
  const b = calls.filter((c) => c[0] === "bloom"), th = calls.filter((c) => c[0] === "thin");
  assert.deepEqual(b.map((c) => [c[1], c[2], c[3], c[4]]), st.states.flatMap((S) => S.paths).map((pp) => [pp.si, pp.si === 1 ? 1 : 0, pp.si === 1 ? 0 : 1, SOLO.LIFT]));
  assert.deepEqual(th.map((c) => [c[1], c[2], c[3]]), st.states.flatMap((S) => S.paths).map((pp) => [pp.si, pp.si === 1 ? 0 : 1, SOLO.THIN]));
  calls.length = 0;
  paintSolo({ evs: soloEvents([solo()], []), lits: [] }, 9, st, ctx);
  assert.ok(calls.every((c) => (c[0] === "bloom" ? c[2] === 0 && c[3] === 0 : c[2] === 0)), "before the word: every line at its own base");
});

// ---------------------------------------------------------------- P71 T30: the long form's key pill and end badge (S9)
const styled = (init = {}, style = null) => {
  const el = rec(init), props = {};
  el.style = { setProperty: (k, v) => { props[k] = String(v); }, removeProperty: (k) => { delete props[k]; }, props,
               get opacity() { return props.opacity || ""; }, set opacity(v) { props.opacity = String(v); } };
  if (style !== null) el.a.style = style;
  return el;
};
const lfPage = () => {
  const chip = (si) => styled({ fill: "#C" + si });
  const pp = (si) => { const name = styled({ fill: "#N" + si, opacity: "1" }, "fill:#N" + si + ";"), c = chip(si);
    name.querySelector = (sel) => (sel === "tspan.tagchip" ? c : null); return { si, muted: false, p: rec(), tip: rec(), name, chip: c }; };
  const kp = (series, panel = null) => { const el = styled(); el.style.opacity = "1"; return { el, series, panel }; };
  const st = { paths: [pp(0), pp(1), pp(2)], bars: [], lfType: { form: "value" }, keyPills: [kp(0), kp(1), kp(2)] };
  st.states = [st];
  return st;
};

test("P71 T30: on a long-form page the named series' key pill fills with the accent and the others fade with their series", () => {
  const st = lfPage(), sd = { evs: soloEvents([solo()], [{ at: 20, dur: 1 }]), lits: [] };
  paintSolo(sd, 9, st, {});
  for (const kp of st.keyPills) assert.ok(!("box-shadow" in kp.el.style.props) && kp.el.style.opacity === "1", "before the word: the key it was");
  for (const kp of st.keyPills) kp.el.style.opacity = "1";   /* the badge ladder rewrites the opacity every frame */
  paintSolo(sd, 11, st, {});
  assert.equal(st.keyPills[1].el.style.props["box-shadow"], "inset 0 0 0 999px " + SOLO_ACCENT.FILL, "landed: the accent's own colour");
  assert.equal(st.keyPills[1].el.style.opacity, "1");
  for (const i of [0, 2]) {
    assert.equal(st.keyPills[i].el.style.opacity, SOLO.DIM.toFixed(3));
    assert.ok(!("box-shadow" in st.keyPills[i].el.style.props));
  }
  for (const kp of st.keyPills) kp.el.style.opacity = "1";
  paintSolo(sd, 10.25, st, {});
  assert.match(st.keyPills[1].el.style.props["box-shadow"], /color-mix\(in srgb, var\(--lp-acc\) 50\.0%, transparent\)/, "half the word, half the fill");
  for (const kp of st.keyPills) kp.el.style.opacity = "1";
  paintSolo(sd, 22, st, {});
  for (const kp of st.keyPills) assert.ok(!("box-shadow" in kp.el.style.props) && kp.el.style.opacity === "1", "a release hands the key back");
});

test("P71 T30: the named line's end badge turns the accent; a release restores its style to the byte", () => {
  const st = lfPage(), sd = { evs: soloEvents([solo()], [{ at: 20, dur: 1 }]), lits: [] };
  paintSolo(sd, 11, st, {});
  const nm = st.paths[1].name, chip = st.paths[1].chip;
  assert.equal(nm.style.props.fill, SOLO_ACCENT.FILL, "landed: the accent's own colour");
  assert.ok(!("stroke" in nm.style.props), "its light is its ink - no capsule stroke");
  assert.equal(chip.style.props.fill, SOLO_ACCENT.FILL, "the chip's words turn with the tag's");
  assert.equal(nm.getAttribute(SOLO_ACCENT.STASH), "fill:#N1;", "the tag's own style is kept while it is lit");
  assert.equal(chip.getAttribute(SOLO_ACCENT.STASH), "", "a chip with no style of its own keeps that too");
  for (const i of [0, 2]) assert.ok(!("fill" in st.paths[i].name.style.props) && st.paths[i].name.getAttribute(SOLO_ACCENT.STASH) === null);
  paintSolo(sd, 10.25, st, {});
  assert.equal(nm.style.props.fill, "color-mix(in srgb, var(--lp-acc) 50.0%, #N1)", "half the word, half the way to the accent");
  paintSolo(sd, 22, st, {});
  assert.equal(nm.getAttribute("style"), "fill:#N1;");
  assert.equal(nm.getAttribute(SOLO_ACCENT.STASH), null);
  assert.equal(chip.getAttribute("style"), null, "the chip had no style attribute, and has none again");
});

test("P71 T30: a short's page (no long-form type) and a panels page's key are left exactly as they were", () => {
  const st = lfPage();
  delete st.lfType;
  paintSolo({ evs: soloEvents([solo()], []), lits: [] }, 11, st, {});
  for (const pp of st.paths) assert.ok(!("fill" in pp.name.style.props) && pp.name.getAttribute(SOLO_ACCENT.STASH) === null);
  for (const kp of st.keyPills) assert.ok(!("box-shadow" in kp.el.style.props) && kp.el.style.opacity === "1");
  const lf = lfPage();
  for (const kp of lf.keyPills) kp.panel = 0;
  paintSolo({ evs: soloEvents([solo()], []), lits: [] }, 11, lf, {});
  for (const kp of lf.keyPills) assert.ok(!("box-shadow" in kp.el.style.props) && kp.el.style.opacity === "1");
});

// ---------------------------------------------------------------- P72 T53 (d) (R26-412 (d)): the box waits for its tag
// P71 T34's isolate beat, draft 1 (the golden `solo-badge-waits`): the page built to the dot-com high, the tech line's
// solo landed, and the lines carried on to today AFTER it - T46d's accent box stood filled and EMPTY at the plot's right
// while the tag (opacity 0 until its line arrives) waited. The box takes the tag's own visibility: no tag, no box.
test("T53 (d): the end badge's box is not drawn while its tag is off the page, and fills with the tag as it arrives", () => {
  const withBox = (tagOp, styleOp = "") => {
    const st = lfPage(), pp = st.paths[1];
    pp.name.a.opacity = tagOp;
    pp.name.style.opacity = styleOp;
    pp.name.getBBox = () => ({ x: 100, y: 50, width: 200, height: 30 });
    pp.badge = styled();
    paintSolo({ evs: soloEvents([solo()], []), lits: [] }, 11, st, {});
    return pp.badge;
  };
  assert.equal(withBox("0").getAttribute("opacity"), "0.000", "the tag waits for its line: the accent box is not drawn");
  assert.equal(withBox("1", "0").getAttribute("opacity"), "0.000", "nor while the tag is hidden by its style (a transition's hand-over)");
  assert.equal(withBox("0.5").getAttribute("opacity"), "0.500", "the box arrives WITH the tag, never ahead of it");
  assert.equal(withBox("1").getAttribute("opacity"), "1.000", "a standing tag: T46d's box, to the byte");
  assert.equal(withBox(undefined).getAttribute("opacity"), "1.000", "a tag with no opacity of its own is on the page");
});
