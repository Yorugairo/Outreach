// P52 T6 - THE NEWSREEL BAND. The band's whole visual state is a pure function of t, sp.at, sp.hold and the run's
// measured width: the bar opens on the house spring, the run crawls and WRAPS by the modulo against a stable upper
// bound (two copies, a width apart - no seam), the strap writes, and when `hold` ends the band retreats. These
// tests pin the wrap (the mechanism taken from RU-4), the beat table, the mask's stable id, the hold-as-a-life and
// that nothing is remembered between calls.
import { test } from "node:test";
import assert from "node:assert/strict";
import { springPop } from "../../scripts/kinetics/spring.mjs";
import { NEWSREEL, reelItems, reelRun, reelWidth, crawlX, reelSpeed, reelStand, reelPose, edgeId, edgeStops, paintNewsreel }
  from "../../scripts/species/newsreel.mjs";

const near = (a, b, eps = 1e-9) => Math.abs(a - b) <= eps;
const HEADS = ["Treasury Secretary Bessent Boosts Buybacks of Long-Dated Debt",
               "US Treasury to Buy Up to $6 Billion in Long-Dated Debt",
               "Kevin Warsh: A new regime is needed at the Fed"];
const reel = (o = {}) => Object.assign({
  kind: "newsreel", at: 5, dur: 12, headlines: HEADS.slice(), strap: "the wire, 2026", dateline: "SEPT 2026",
  target: { kind: "region", x0: 0.0, y0: 0.78, x1: 1.0, y1: 0.92 },
}, o);

// ---------------------------------------------------------------- the dials and the beat table
test("the dials are the band's, and every clock in the beat table is a real window", () => {
  assert.ok(NEWSREEL.SPEED > 0 && NEWSREEL.BAND_H > 0 && NEWSREEL.BAND_H < 0.3, "a band is a strip, not a panel");
  assert.ok(NEWSREEL.EDGE > 0 && NEWSREEL.EDGE < 0.5, "the dissolve eats the edge, never the headline");
  assert.ok(NEWSREEL.HAIRLINE > 0 && NEWSREEL.HAIRLINE < 0.2, "the band opens FROM a line of ink, not from nothing");
  assert.ok(NEWSREEL.TYPE < 1 && NEWSREEL.STRAP_TYPE < NEWSREEL.TYPE, "the tape is under the caption's size, the strap under the tape's");
  for (const k of ["BAR_FOR", "CRAWL", "STRAP", "STRAP_FOR", "EXIT_FOR"]) assert.ok(NEWSREEL.BEATS[k] > 0, k);
});

test("the beat table SUMS the way RU-4's plan reads: the crawl starts inside the open, the strap after it", () => {
  const B = NEWSREEL.BEATS;
  assert.equal(B.BAR, 0, "the band starts opening on the species' own `at`");
  assert.ok(B.CRAWL < B.BAR_FOR, "the run is moving before the band has finished opening - a still strip is never on screen");
  assert.ok(B.STRAP >= B.BAR_FOR, "the strap writes onto an open band");
  assert.ok(B.BAR_FOR + B.EXIT_FOR < 1.0, "the arrival and the retreat together fit inside one beat");
  assert.ok(B.STRAP + B.STRAP_FOR < 1.0, "the strap is written before the sentence is over");
});

// ---------------------------------------------------------------- the run and its stable upper bound
test("the run is the author's headlines with the house bullet between them, and nothing else", () => {
  assert.deepEqual(reelItems(reel()), HEADS);
  assert.equal(reelRun(HEADS).split(NEWSREEL.BULLET).length - 1, 2, "two bullets between three headlines");
  assert.ok(reelRun(HEADS).startsWith(HEADS[0]) && reelRun(HEADS).endsWith(HEADS[2]));
  assert.deepEqual(reelItems({ headlines: ["  a headline  ", "", "   ", 7, null] }), ["a headline"], "blank and non-string are dropped");
  assert.deepEqual(reelItems({}), []);
});

test("reelWidth is the run's own width plus ONE gap - measured when the caller can measure, estimated when it cannot", () => {
  const measured = reelWidth(HEADS, () => 4000);
  assert.equal(measured, 4000 + NEWSREEL.GAP);
  const est = reelWidth(HEADS, null);
  assert.ok(est > reelRun(HEADS).length, "the estimate scales with the run, and is an upper bound, never a fraction");
  assert.equal(reelWidth([], () => 4000), 0, "no headlines, no run, no width");
  for (const bad of [() => 0, () => -3, () => NaN, "nope"])
    assert.equal(reelWidth(HEADS, bad), est, "a measure that answers nothing falls back to the estimate");
});

// ---------------------------------------------------------------- the modulo wrap (RU-4 mechanism 1)
test("THE WRAP: crawlX(tc + width / speed) == crawlX(tc) - the tape has no seam", () => {
  const width = reelWidth(HEADS, () => 3971.5), speed = NEWSREEL.SPEED, period = width / speed;
  for (let i = 0; i <= 40; i++) {
    const tc = i * 0.37;
    assert.ok(near(crawlX(tc + period, width, speed), crawlX(tc, width, speed), 1e-6), `tc=${tc}`);
  }
  assert.ok(near(crawlX(0, width, speed), 0), "at the crawl's own zero the run stands at its place");
  assert.ok(near(crawlX(period / 2, width, speed), -width / 2, 1e-6), "half a period is half a width to the left");
});

test("the crawl only ever moves LEFT, inside [-width, 0], and a width away is the second copy's place", () => {
  const width = 2400, speed = 200;
  for (let i = 0; i <= 500; i++) {
    const x = crawlX(i * 0.05, width, speed);
    assert.ok(x <= 0 && x > -width, `x=${x}`);
  }
  const tc = 7.3, x = crawlX(tc, width, speed);
  assert.ok(x + width > 0 && x + width <= width, "the second copy is always the one entering from the right");
  assert.equal(crawlX(5, 0, speed), 0, "a run with no width does not move");
  assert.equal(crawlX(5, -12, speed), 0);
});

test("the speed is the author's when they wrote one, the dial when they did not, and never zero or backwards", () => {
  assert.equal(reelSpeed(reel()), NEWSREEL.SPEED);
  assert.equal(reelSpeed(reel({ speed_px_s: 96 })), 96);
  for (const bad of [0, -50, "fast", null]) assert.equal(reelSpeed(reel({ speed_px_s: bad })), NEWSREEL.SPEED, String(bad));
  assert.ok(crawlX(1, 1000, 0) === crawlX(1, 1000, NEWSREEL.SPEED), "a zero speed falls back to the dial rather than freezing the tape");
});

// ---------------------------------------------------------------- the pose (the open, the strap, the retreat)
test("the bar opens on the house spring from HAIRLINE to 1, and there is nothing before `at`", () => {
  const sp = reel();
  assert.equal(reelPose(sp, sp.at - 0.01).open, 0);
  assert.equal(reelPose(sp, sp.at - 0.01).on, false);
  assert.ok(near(reelPose(sp, sp.at).open, NEWSREEL.HAIRLINE));
  for (let i = 0; i < 20; i++) {   // the closed end is the float-exact case below: (at + BAR_FOR) - at is not BAR_FOR to the bit
    const u = i / 20, t = sp.at + u * NEWSREEL.BEATS.BAR_FOR;
    assert.ok(near(reelPose(sp, t).open, NEWSREEL.HAIRLINE + (1 - NEWSREEL.HAIRLINE) * springPop(u)), `u=${u}`);
  }
  assert.ok(near(reelPose(sp, sp.at + NEWSREEL.BEATS.BAR_FOR).open, 1, 3e-3), "the open settles on the band's own height");
  assert.equal(reelPose(sp, sp.at + NEWSREEL.BEATS.BAR_FOR * 2).open, 1, "past its clock the spring is clamped: exactly the band's height, to the bit");
});

test("the crawl's clock starts at BEATS.CRAWL and runs from zero - the band is open before the tape moves", () => {
  const sp = reel();
  assert.equal(reelPose(sp, sp.at).crawl, 0);
  assert.ok(near(reelPose(sp, sp.at + NEWSREEL.BEATS.CRAWL).crawl, 0), "the crawl's clock opens at zero, not at a float's width of it");
  assert.ok(near(reelPose(sp, sp.at + NEWSREEL.BEATS.CRAWL + 2).crawl, 2));
});

test("the strap WRITES over STRAP_FOR and is never half-written before its beat", () => {
  const sp = reel(), B = NEWSREEL.BEATS;
  assert.ok(near(reelPose(sp, sp.at + B.STRAP).strap, 0));
  assert.ok(near(reelPose(sp, sp.at + B.STRAP + B.STRAP_FOR / 2).strap, 0.5));
  assert.ok(near(reelPose(sp, sp.at + B.STRAP + B.STRAP_FOR).strap, 1), "the write is closed at the end of its own clock, to the float");
  assert.equal(reelPose(sp, sp.at + 9).strap, 1);
});

test("`hold` is a LIFE: the band stands for it and RETREATS over EXIT_FOR; without one it stands for `dur`", () => {
  const sp = reel({ hold: 6 }), B = NEWSREEL.BEATS;
  assert.equal(reelStand(sp), 6);
  assert.equal(reelStand(reel()), 12, "no hold: the species' own window");
  assert.equal(reelStand(reel({ hold: 0 })), 12);
  assert.equal(reelPose(sp, sp.at + 5.9).exit, 0);
  assert.ok(near(reelPose(sp, sp.at + 6).exit, 0));
  assert.ok(near(reelPose(sp, sp.at + 6 + B.EXIT_FOR / 2).exit, 0.5));
  const mid = reelPose(sp, sp.at + 6 + B.EXIT_FOR / 2);
  assert.ok(mid.on && mid.open < 0.6 && near(mid.alpha, 0.5), "mid-retreat the band is half shut and half there");
  const gone = reelPose(sp, sp.at + 6 + B.EXIT_FOR);
  assert.equal(gone.on, false, "the retreat ends the band - nothing is painted after it");
  assert.equal(reelPose(sp, sp.at + 40).on, false);
  assert.ok(reelPose(reel(), reel().at + 11.9).on, "a band with no hold is up until its own window ends");
});

// ---------------------------------------------------------------- the mask
test("the edge mask's id is stable per species index, and the stops eat only the last EDGE of the band", () => {
  assert.equal(edgeId(0), "nredge0");
  assert.equal(edgeId(3), edgeId(3));
  assert.notEqual(edgeId(3), edgeId(4), "two bands in one window never share a mask");
  const stops = edgeStops();
  assert.deepEqual(stops.map((s) => s.stop), [1, 1, 0]);
  assert.ok(near(stops[1].offset, 1 - NEWSREEL.EDGE));
  assert.equal(stops[0].offset, 0, "the LEFT edge is hard - it is the column the head stands in");
});

// ---------------------------------------------------------------- pure function of t
test("a seek IS the play: the same t gives the same bits, in any order, with nothing remembered", () => {
  const sp = reel({ hold: 7 });
  const forward = [], backward = [];
  for (let i = 0; i <= 300; i++) forward.push(JSON.stringify(reelPose(sp, i / 20)));
  for (let i = 300; i >= 0; i--) backward.unshift(JSON.stringify(reelPose(sp, i / 20)));
  assert.deepEqual(backward, forward);
  assert.equal(JSON.stringify(reelPose(sp, 7.35)), forward[147]);
});

test("nothing in the module reaches for a clock or a random", () => {
  const src = [paintNewsreel, reelPose, crawlX, reelWidth, reelRun, edgeStops].map((f) => f.toString()).join("\n");
  assert.ok(!/Math\.random|Date\.now|new Date|performance\./.test(src), src);
});

// ---------------------------------------------------------------- the painter, on a stub surface
const stub = () => {
  const made = [];
  const el = (tag, cls, parent, at) => {
    const e = { tag, cls, at: Object.assign({}, at || {}), kids: [], textContent: "",
                setAttribute(k, v) { this.at[k] = v; }, getAttribute(k) { return this.at[k]; } };
    made.push(e); if (parent && parent.kids) parent.kids.push(e); return e;
  };
  return { made, el };
};
const ctxFor = (sp, t, target) => {
  const s = stub();
  return Object.assign(s, { ctx: { sp, t, si: 2, svg: { kids: [] }, el: s.el,
    resolveTarget: (tg) => (target === undefined ? (tg && tg.kind === "region"
      ? { x: tg.x0 * 1080, y: tg.y0 * 1920, w: (tg.x1 - tg.x0) * 1080, h: (tg.y1 - tg.y0) * 1920 } : null) : target) } });
};

test("the painter draws nothing without a resolved region, without headlines, or before the band's word", () => {
  let s = ctxFor(reel(), 6, null); paintNewsreel(s.ctx);
  assert.equal(s.made.length, 0, "the targeting law: no resolved region, nothing painted");
  s = ctxFor(reel({ headlines: [] }), 6); paintNewsreel(s.ctx);
  assert.equal(s.made.length, 0, "an empty run paints no band - the compiler refuses the row too");
  s = ctxFor(reel(), 4.9); paintNewsreel(s.ctx);
  assert.equal(s.made.length, 0);
  s = ctxFor(reel({ hold: 2 }), 5 + 2 + NEWSREEL.BEATS.EXIT_FOR + 0.01); paintNewsreel(s.ctx);
  assert.equal(s.made.length, 0, "after the retreat the band is gone, not a hairline left behind");
  s = ctxFor(reel(), 6, { x: 0, y: 1500, w: 0, h: 0 }); paintNewsreel(s.ctx);
  assert.equal(s.made.length, 0, "a region with no area is not a band");
});

test("the painter draws ONE band: the strip, its rule, the coral tab, TWO copies of the run, the strap and the dateline", () => {
  const s = ctxFor(reel(), 7.0);
  paintNewsreel(s.ctx);
  const cls = s.made.filter((e) => e.cls).map((e) => e.cls);
  assert.deepEqual(cls, ["nreel", "nrband", "nrrule", "nrtab", "nrcrawl", "nrrun", "nrrun", "nrstrap", "nrdate"], cls.join(","));
  const runs = s.made.filter((e) => e.cls === "nrrun");
  assert.equal(runs[0].textContent, reelRun(HEADS));
  assert.equal(runs[1].textContent, reelRun(HEADS), "the second copy IS the run - the wrap is two copies, not a reflow");
  const w = +s.made.find((e) => e.cls === "nrcrawl").at["data-reelw"];
  assert.ok(near(+runs[1].at.x - +runs[0].at.x, w, 0.02), "the copies sit exactly one width apart");
  assert.equal(s.made.find((e) => e.cls === "nrdate").textContent, "SEPT 2026");
  assert.equal(s.made.find((e) => e.cls === "nrstrap").textContent, "the wire, 2026");
  assert.ok(s.made.find((e) => e.tag === "mask").at.id === edgeId(2), "the mask carries this species' own stable id");
  assert.ok(s.made.find((e) => e.cls === "nrcrawl").at.mask.includes(edgeId(2)));
});

test("the band is drawn at the DECLARED region, scaled about its own foot, and the crawl moves between two frames", () => {
  const sp = reel(), y0 = 0.78 * 1920, h = (0.92 - 0.78) * 1920;
  const s = ctxFor(sp, 7.0); paintNewsreel(s.ctx);
  const band = s.made.find((e) => e.cls === "nrband");
  assert.equal(+band.at.y, Math.round(y0 * 10) / 10);
  assert.ok(near(+band.at.height, h, 0.05));
  assert.ok(s.made[0].at.transform.includes(String((y0 + h).toFixed(1))), "the open scales about the band's own bottom edge");
  const x = (t) => { const q = ctxFor(sp, t); paintNewsreel(q.ctx); return +q.made.filter((e) => e.cls === "nrrun")[0].at.x; };
  assert.ok(x(8.0) < x(7.0), "the tape runs left");
  assert.equal(x(7.0), x(7.0), "and the same t gives the same x");
});
