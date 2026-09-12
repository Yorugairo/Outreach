// P52 T8 - THE RING'S DASHED-ELLIPSE FORM AND ITS FLAG CHIP (EXPLORATION-REVIEW-2026-09-10.md:57 #5). The form
// widens, the USE does not: E56 (a ring circles a number or a point on a CHART) lives in the compiler, and this
// module carries no opinion about what it is pointed at. What it does carry: the callout's own pads (so the dashed
// form rings exactly where the circle would), a dash-by-dash draw with no rotation anywhere, and a flag chip whose
// placement math is the chip module's.
import { test } from "node:test";
import assert from "node:assert/strict";
import { CHIP, chipLand } from "../../scripts/species/chip.mjs";
import { RING, ringEllipse, ringPerimeter, ringSamples, ringPointAt, ringDashes, ringDrawF, ringDashF,
         ringFlagPlace, ringFlagPose, ringPose, paintRing } from "../../scripts/species/ring.mjs";

const near = (a, b, eps = 1e-9) => Math.abs(a - b) <= eps;
const DATUM = { x: 1180, y: 520, w: 0, h: 0 };            // a datum on a line page resolves to a POINT
const BAR = { x: 900, y: 300, w: 120, h: 420 };           // ... and a bar to a box
const ring = (o = {}) => Object.assign({ kind: "ring", at: 8, dur: 6, form: "dashed",
                                         target: { kind: "datum", index: 150 } }, o);

// ---------------------------------------------------------------- the form, and E56's place
test("the module paints ONE form, and the circle is not it", () => {
  assert.equal(RING.FORM, "dashed");
  assert.equal(RING.RX_PAD, 22, "the engine's calloutPath rx pad, verbatim - the two forms ring the same place");
  assert.equal(RING.RY_PAD, 18, "... and its ry pad");
  assert.ok(RING.DRAW_S > 0 && RING.DASH > 0 && RING.DASH_GAP > 0);
  assert.ok(RING.FLAG_K > 0 && RING.FLAG_K < 1, "a flag is smaller than a board chip: a label on a datum");
});

test("E56 is the COMPILER's: the painter never reads what it was pointed at", () => {
  const src = paintRing.toString() + ringEllipse.toString() + ringPose.toString();
  assert.ok(!/target\s*\.\s*kind/.test(src), "the use is refused at build time (_validate_ring), never softened here");
  assert.ok(!/label.*digit|\\d/.test(src));
});

// ---------------------------------------------------------------- the ellipse
test("the ellipse rings the datum where the hand's circle would: w/2 + RX_PAD by h/2 + RY_PAD", () => {
  const e = ringEllipse(BAR, 0);
  assert.deepEqual([e.cx, e.cy], [BAR.x + BAR.w / 2, BAR.y + BAR.h / 2]);
  assert.ok(near(e.rx, BAR.w / 2 + RING.RX_PAD) && near(e.ry, BAR.h / 2 + RING.RY_PAD));
  const p = ringEllipse(DATUM, 0);
  assert.deepEqual([p.rx, p.ry], [RING.MIN_RX, RING.MIN_RY], "a bare point takes the minimum, not a zero ring");
  const padded = ringEllipse(BAR, 40);
  assert.ok(padded.rx > e.rx && padded.ry > e.ry, "`pad` is how wide the hand rings it - the callout's own dial");
});

test("the perimeter is Ramanujan's, and it agrees with the polyline it cuts", () => {
  for (const e of [ringEllipse(DATUM, 0), ringEllipse(BAR, 0), { cx: 0, cy: 0, rx: 300, ry: 60 }]) {
    let len = 0;
    const N = 4000;
    for (let i = 1; i <= N; i++) {
      const a0 = (i - 1) / N * Math.PI * 2, a1 = i / N * Math.PI * 2;
      len += Math.hypot(e.rx * (Math.cos(a1) - Math.cos(a0)), e.ry * (Math.sin(a1) - Math.sin(a0)));
    }
    const rel = Math.abs(ringPerimeter(e) - len) / len;
    assert.ok(rel < 1e-4, `${JSON.stringify(e)}: ${rel}`);
  }
  const circle = ringPerimeter({ cx: 0, cy: 0, rx: 100, ry: 100 });
  assert.ok(near(circle, Math.PI * 200, 1e-9), "a circle is the closed case, exactly");
});

// ---------------------------------------------------------------- the dashes
test("the ellipse is cut into dashes on the DASH : GAP rhythm, starting at the TOP and running clockwise", () => {
  const e = ringEllipse(BAR, 0), dashes = ringDashes(e);
  assert.ok(dashes.length >= 6, `${dashes.length} dashes`);
  assert.ok(near(dashes.length, Math.round(ringPerimeter(e) / (RING.DASH + RING.DASH_GAP)), 0.5));
  const first = dashes[0].d.match(/-?\d+(?:\.\d+)?/g).map(Number);
  assert.ok(near(first[0], e.cx, 0.05) && near(first[1], e.cy - e.ry, 0.05), "the nib starts at the top of the ellipse");
  const second = dashes[1].d.match(/-?\d+(?:\.\d+)?/g).map(Number);
  assert.ok(second[0] > first[0], "... and runs clockwise: the next dash is to its right");
  for (let i = 0; i < dashes.length; i++) {
    assert.ok(near(dashes[i].t0, i / dashes.length) && near(dashes[i].t1, (i + 1) / dashes.length));
  }
  assert.equal(dashes[dashes.length - 1].t1, 1, "the dashes tile the whole draw: no dash is left unowned");
  // the mark : span ratio IS the dial's - the air between two dashes is what makes it read as dashed
  const arc = (d) => { const n = d.match(/-?\d+(?:\.\d+)?/g).map(Number); return Math.hypot(n[n.length - 2] - n[0], n[n.length - 1] - n[1]); };
  const gapRatio = RING.DASH / (RING.DASH + RING.DASH_GAP);
  assert.ok(Math.abs(arc(dashes[0].d) / (ringPerimeter(e) / dashes.length) - gapRatio) < 0.08, "a 2:1 dash-to-air rhythm");
});

test("the dashes are cut BY LENGTH, so a tall ellipse rings as evenly as a round one", () => {
  const poly = (d) => { const n = d.match(/-?\d+(?:\.\d+)?/g).map(Number); let L = 0;
    for (let i = 2; i < n.length; i += 2) L += Math.hypot(n[i] - n[i - 2], n[i + 1] - n[i - 1]); return L; };
  for (const e of [ringEllipse(BAR, 0), ringEllipse(DATUM, 0), { cx: 500, cy: 500, rx: 340, ry: 52 }]) {
    const lens = ringDashes(e).map((d) => poly(d.d));
    const lo = Math.min(...lens), hi = Math.max(...lens);
    assert.ok((hi - lo) / hi < 0.02, `${JSON.stringify(e)}: dashes ${lo.toFixed(2)}..${hi.toFixed(2)} px`);
    assert.ok(Math.abs(hi - RING.DASH) / RING.DASH < 0.25, `a dash is about DASH long: ${hi.toFixed(1)} px`);
  }
  const tab = ringSamples(ringEllipse(BAR, 0));
  assert.ok(Math.abs(tab.per - ringPerimeter(ringEllipse(BAR, 0))) / tab.per < 1e-4, "the table and the closed form agree");
  const top = ringPointAt(tab, 0), half = ringPointAt(tab, tab.per / 2);
  const e0 = ringEllipse(BAR, 0);
  assert.ok(Math.abs(top[1] - (e0.cy - e0.ry)) < 0.05 && Math.abs(half[1] - (e0.cy + e0.ry)) < 0.6,
            "half the perimeter round a symmetric ellipse is the far side of it");
});

test("NOTHING SPINS: the dashes' geometry is the SAME at every t - only how much is drawn changes", () => {
  const e = ringEllipse(BAR, 0);
  assert.deepEqual(ringDashes(e).map((d) => d.d), ringDashes(e).map((d) => d.d));
  const sp = ring();
  const at = (t) => stub(sp, t).made.filter((x) => x.cls === "rngdash").map((x) => x.at.d);
  const mid = at(8.4), done = at(9.5);
  assert.ok(mid.length > 0 && done.length >= mid.length);
  assert.deepEqual(mid, done.slice(0, mid.length), "a dash already passed is simply there - it does not move or turn");
});

test("the draw runs 0 -> 1 over DRAW_S and only ever forward; a dash is 0 before the nib reaches it", () => {
  const sp = ring();
  assert.equal(ringDrawF(sp, 7.9), 0);
  assert.equal(ringDrawF(sp, 8), 0);
  assert.ok(near(ringDrawF(sp, 8 + RING.DRAW_S / 2), 0.5));
  assert.equal(ringDrawF(sp, 8 + RING.DRAW_S), 1);
  assert.equal(ringDrawF(sp, 40), 1);
  let prev = -1;
  for (let i = 0; i <= 400; i++) { const f = ringDrawF(sp, i / 20); assert.ok(f >= prev); prev = f; }
  const dashes = ringDashes(ringEllipse(BAR, 0));
  assert.equal(ringDashF(0.0, dashes[2]), 0);
  assert.equal(ringDashF(1.0, dashes[2]), 1);
  assert.ok(near(ringDashF((dashes[2].t0 + dashes[2].t1) / 2, dashes[2]), 0.5));
});

// ---------------------------------------------------------------- the flag chip
test("the flag is optional, and its landing is the CHIP's own - off the instant the ellipse closes", () => {
  assert.equal(ringPose(ring(), 12).flag, null, "no flag declared, no flag painted");
  const sp = ring({ flag: "THE FLOOR", flag_icon: "landmark" });
  const lands = 8 + RING.DRAW_S + RING.FLAG_LAG;
  assert.equal(ringFlagPose(sp, lands - 0.01).fade, 0);
  for (let i = 0; i <= 20; i++) {
    const t = lands + (i / 20) * CHIP.LAND_S;
    assert.deepEqual(ringFlagPose(sp, t), chipLand(t, lands, {}), "the chip module's law, not a second landing");
  }
  const settled = ringFlagPose(sp, lands + CHIP.LAND_S * 2);
  assert.deepEqual([settled.u, settled.scale, settled.dy, settled.fade], [1, 1, 0, 1]);
});

test("the flag stands beside the ellipse, and takes the side that has the room", () => {
  const e = ringEllipse(BAR, 0);
  const right = ringFlagPlace(e, null, 1920);
  assert.equal(right.side, "right");
  assert.ok(right.x > e.cx + e.rx, "clear of the ring, by FLAG_GAP plus the card's own half");
  assert.ok(near(right.x - (e.cx + e.rx), RING.FLAG_GAP + CHIP.SIZE * RING.FLAG_K / 2));
  assert.equal(right.y, e.cy, "beside the datum, not above it");
  const edge = ringFlagPlace({ cx: 1850, cy: 400, rx: 60, ry: 40 }, null, 1920);
  assert.equal(edge.side, "left", "a card that would leave the stage goes to the other side");
  assert.equal(ringFlagPlace(e, "left", 1920).side, "left", "the author's side wins");
  assert.equal(ringFlagPlace({ cx: 1850, cy: 400, rx: 60, ry: 40 }, "right", 1920).side, "right");
});

// ---------------------------------------------------------------- pure function of t
test("a seek IS the play: the same t gives the same bits, in any order, with nothing remembered", () => {
  const sp = ring({ flag: "THE FLOOR", flag_icon: "landmark", idle: "breath" });
  const forward = [], backward = [];
  for (let i = 0; i <= 400; i++) forward.push(JSON.stringify(ringPose(sp, i / 20)));
  for (let i = 400; i >= 0; i--) backward.unshift(JSON.stringify(ringPose(sp, i / 20)));
  assert.deepEqual(backward, forward);
  assert.equal(JSON.stringify(ringPose(sp, 9.35)), forward[187]);
});

test("nothing in the module reaches for a clock or a random", () => {
  const src = paintRing.toString() + ringDashes.toString() + ringPose.toString() + ringFlagPlace.toString();
  assert.ok(!/Math\.random|Date\.now|new Date|performance\./.test(src), src);
});

// ---------------------------------------------------------------- the painter, on a stub surface
const GEO = JSON.stringify({ vb: [0, 0, 24, 24], el: [{ t: "path", a: { d: "M12 16h.01" } }] });

function stub(sp, t, opts = {}) {
  const made = [], idles = [], drawn = [];
  const el = (tag, cls, parent, at) => {
    const e = { tag, cls, at: Object.assign({}, at), kids: [], textContent: "",
                setAttribute(k, v) { this.at[k] = v; }, getAttribute(k) { return this.at[k]; } };
    made.push(e); if (parent && parent.kids) parent.kids.push(e); return e;
  };
  paintRing({ sp, t, svg: { kids: [] }, el, A: { "icon:landmark": GEO },
              resolveTarget: () => (opts.noTarget ? null : Object.assign({}, opts.box || BAR)),
              drawOn: (p, k) => { drawn.push(k); p.setAttribute("stroke-dashoffset", k.toFixed(3)); },
              hash: (a, b, c) => ((a + b * 11 + c) % 100) / 100, seed: 7, si: 0,
              idle: (kind, tt, ph) => { idles.push([kind, ph]); return { scale: 1, dx: 0, dy: 0 }; },
              ease: (k) => k, STAGE_W: 1920, STAGE_H: 1080 });
  return { made, idles, drawn };
}

test("the painter draws nothing when the target does not resolve, and nothing before its word", () => {
  assert.equal(stub(ring(), 9, { noTarget: true }).made.length, 0, "the targeting law: no resolved target, nothing painted");
  assert.equal(stub(ring(), 7.9).made.length, 0);
});

test("the painter draws the dashes it has reached, the label, and the flag card with its sourced glyph", () => {
  const sp = ring({ label: "$1,239.3B", flag: "THE FLOOR", flag_icon: "landmark" });
  const mid = stub(sp, 8.3);
  assert.ok(mid.made.filter((e) => e.cls === "rngdash").length > 0);
  assert.ok(mid.made.filter((e) => e.cls === "rngdash").length < ringDashes(ringEllipse(BAR, 0)).length, "mid-draw: not every dash yet");
  assert.equal(mid.made.find((e) => e.cls === "lab").textContent, "$1,239.3B");
  assert.equal(mid.made.filter((e) => e.cls === "chipcard").length, 0, "the flag waits for the ring to close");
  const done = stub(sp, 12);
  assert.equal(done.made.filter((e) => e.cls === "rngdash").length, ringDashes(ringEllipse(BAR, 0)).length);
  assert.equal(done.made.filter((e) => e.cls === "chipcard").length, 1, "the flag card is the CHIP's card");
  assert.equal(done.made.filter((e) => e.cls === "chipglyph").length, 1);
  assert.equal(done.made.find((e) => e.cls === "chiplab").textContent, "THE FLOOR");
  const card = done.made.find((e) => e.cls === "chipcard");
  assert.equal(+card.at.width, CHIP.SIZE);
  assert.equal(+card.at.rx, CHIP.RX, "the chip module's own card geometry, reused whole");
  assert.equal(stub(ring({ flag: "on", flag_icon: "landmark" }), 12).made.filter((e) => e.cls === "chiplab").length, 0,
               "`flag: on` is a flag with no words");
});

test("the label never hides under the flag: it moves above the ellipse when the card takes that side", () => {
  const e = ringEllipse(BAR, 0);
  const bare = stub(ring({ label: "1,074" }), 12).made.find((x) => x.cls === "lab");
  assert.ok(+bare.at.x > e.cx + e.rx, "with no flag it is written where the engine's callout writes it");
  const flagged = stub(ring({ label: "1,074", flag: "THE PEAK", flag_icon: "landmark" }), 12).made.find((x) => x.cls === "lab");
  assert.ok(+flagged.at.x < e.cx, "with a flag on the right it starts at the ellipse's left edge ...");
  assert.ok(+flagged.at.y < e.cy - e.ry, "... and above its top, clear of the card");
  const left = stub(ring({ label: "1,074", flag: "THE PEAK", flag_icon: "landmark", flag_side: "left" }), 12).made.find((x) => x.cls === "lab");
  assert.ok(+left.at.x > e.cx + e.rx, "and back to the right when the flag takes the left");
});

test("NOTHING SPINS: no attribute the painter writes carries a rotation, at any t", () => {
  const sp = ring({ label: "$1,239.3B", flag: "THE FLOOR", flag_icon: "landmark", idle: "breath" });
  for (const t of [8.0, 8.1, 8.4, 8.6, 9.0, 12.0, 14.0]) {
    for (const e of stub(sp, t).made) {
      for (const [k, v] of Object.entries(e.at)) assert.ok(!/rotate|skew|matrix/.test(String(v)), `${t}: ${e.tag}.${k} = ${v}`);
    }
  }
});

test("the ring holds at a NAMED idle, and 'none' is declared stillness", () => {
  assert.deepEqual(stub(ring(), 12).idles.map((i) => i[0]), ["breath"]);
  assert.deepEqual(stub(ring({ idle: "drift" }), 12).idles.map((i) => i[0]), ["drift"]);
  assert.equal(stub(ring({ idle: "none" }), 12).idles.length, 0);
});
