// P52 T10 - the caption's arrival as ONE envelope with per-word offsets
// [DERIVED: HyperFrames staggered-fade-up] (content/video_engine/hyperframes/HARVEST-2026-09-07.md:27).
// The three things this pins: the dials are the harvest's, the envelope is ONE function shifted per word
// (so a page cannot crowd itself), and the word CLOCK survives - a word spoken later than the stagger
// arrives on its own onset, to the bit. Plus the seek test: the arrival is a pure function of t.
import { test } from "node:test";
import assert from "node:assert/strict";
import { FADE_UP, fadeUpDials, staggerStarts, fadeUpAt, fadeUpPage, staggerSpan,
  LIFE, LIVES, lifeDials, popAt, lifeAt, lifePage }
  from "../../scripts/kinetics/stagger.mjs";
import { minJerk } from "../../scripts/kinetics/ease.mjs";

const dnum = (f, t, h = 1e-6) => (f(t + h) - f(t - h)) / (2 * h);

test("the dials are the harvested ones: rise 22 px, scale from 0.92, blur 5 px, stagger 0.055 s", () => {
  assert.equal(FADE_UP.RISE_PX, 22);
  assert.equal(FADE_UP.FROM_SCALE, 0.92);
  assert.equal(FADE_UP.BLUR_PX, 5);
  assert.equal(FADE_UP.STAGGER_S, 0.055);
  assert.ok(FADE_UP.DUR_S > FADE_UP.STAGGER_S, "the envelope is longer than the stagger - the words overlap, which is the point");
  assert.ok(Object.isFrozen(FADE_UP), "the dials are frozen");
});

test("the envelope's two ends are exact, and every channel moves together across ONE span", () => {
  const start = 3.5, end = start + FADE_UP.DUR_S;
  for (const t of [start - 1, start - 1e-9, start]) {
    const f = fadeUpAt(t, start);
    assert.equal(f.e, 0); assert.equal(f.o, 0);
    assert.equal(f.y, FADE_UP.RISE_PX); assert.equal(f.s, FADE_UP.FROM_SCALE); assert.equal(f.b, FADE_UP.BLUR_PX);
  }
  for (const t of [end, end + 1e-9, end + 10]) {
    const f = fadeUpAt(t, start);
    assert.equal(f.e, 1); assert.equal(f.o, 1);
    assert.equal(f.y, 0); assert.equal(f.s, 1); assert.equal(f.b, 0);
  }
  // monotone, in range, and the three channels are the SAME progress read three ways
  let prev = { y: Infinity, s: -Infinity, b: Infinity };
  for (let i = 0; i <= 400; i++) {
    const t = start + (i / 400) * FADE_UP.DUR_S, f = fadeUpAt(t, start);
    assert.ok(f.y <= prev.y + 1e-12 && f.y >= 0 && f.y <= FADE_UP.RISE_PX, `y ${f.y}`);
    assert.ok(f.s >= prev.s - 1e-12 && f.s >= FADE_UP.FROM_SCALE && f.s <= 1, `scale ${f.s}`);
    assert.ok(f.b <= prev.b + 1e-12 && f.b >= 0 && f.b <= FADE_UP.BLUR_PX, `blur ${f.b}`);
    assert.equal(f.e, Math.min(1, minJerk((t - start) / FADE_UP.DUR_S)));   // minJerk, clamped: its quintic overshoots 1 by 4e-16 just under u = 1
    assert.ok(Math.abs(f.y - FADE_UP.RISE_PX * (1 - f.e)) < 1e-12);
    assert.ok(Math.abs(f.b - FADE_UP.BLUR_PX * (1 - f.e)) < 1e-12);
    prev = f;
  }
});

test("the arrival neither snaps nor sags: zero velocity at both ends (the minimum-jerk envelope)", () => {
  const start = 0.4, y = (t) => fadeUpAt(t, start).y;
  assert.ok(Math.abs(dnum(y, start + 1e-4)) < 0.2, "no snap at the arrival's start");
  assert.ok(Math.abs(dnum(y, start + FADE_UP.DUR_S - 1e-4)) < 0.2, "no sag at its end");
  const mid = dnum(y, start + FADE_UP.DUR_S / 2);
  assert.ok(Math.abs(mid) > 50, `the middle carries the motion (${mid} px/s)`);
});

test("ONE envelope, per-word offsets: word j is word 0 shifted by its own offset", () => {
  const starts = staggerStarts([null, null, null, null], 1.0);
  for (let j = 0; j < starts.length; j++) {
    for (let i = 0; i <= 40; i++) {
      const t = 1.0 + i / 40, a = fadeUpAt(t + (starts[j] - starts[0]), starts[j]), b = fadeUpAt(t, starts[0]);
      // one law, one shape: the only difference between two words is WHEN (the offsets are sums of 0.055,
      // so the shifted argument differs from the unshifted one by float noise, never by the shape)
      for (const k of ["e", "o", "y", "s", "b"]) assert.ok(Math.abs(a[k] - b[k]) < 1e-12, `word ${j} ${k} at ${t}: ${a[k]} vs ${b[k]}`);
    }
  }
  const page = fadeUpPage(1.1, starts);
  assert.equal(page.length, starts.length);
  page.forEach((f, j) => assert.deepEqual(f, fadeUpAt(1.1, starts[j])));
  // the page's whole arrival: the last offset plus one envelope
  assert.ok(Math.abs(staggerSpan(starts) - (3 * FADE_UP.STAGGER_S + FADE_UP.DUR_S)) < 1e-12);
});

test("no two words arrive together: the starts rise by at least the stagger, even when the onsets crowd", () => {
  const crowded = [2.0, 2.0, 2.01, 2.02, 2.02, 2.03];          // an estimated take's near-simultaneous onsets
  const starts = staggerStarts(crowded, 2.0);
  for (let j = 1; j < starts.length; j++) {
    assert.ok(starts[j] - starts[j - 1] >= FADE_UP.STAGGER_S - 1e-12, `gap ${starts[j] - starts[j - 1]}`);
  }
  // and they land on distinct 60 fps frames - overlapping action (no shared start frame)
  const frames = starts.map((s) => Math.floor(s * 60));
  assert.equal(new Set(frames).size, frames.length, `frames ${frames}`);
});

test("THE WORD CLOCK SURVIVES: an onset later than the stagger is kept exactly (E21's per-word entry)", () => {
  const spoken = [10.0, 10.3, 10.62, 11.4];                    // a measured take: every gap beats the stagger
  assert.deepEqual(staggerStarts(spoken, 10.0), spoken);
  // a mixed page: the crowded pair is separated, the far word keeps its own time
  const mixed = staggerStarts([5.0, 5.01, 6.0], 5.0);
  assert.equal(mixed[0], 5.0);
  assert.ok(Math.abs(mixed[1] - (5.0 + FADE_UP.STAGGER_S)) < 1e-12);
  assert.equal(mixed[2], 6.0);
});

test("a missing onset falls to the previous word plus the stagger; an onset before the page is clamped to it", () => {
  const starts = staggerStarts([null, 1.4, undefined, NaN], 1.0);
  assert.equal(starts[0], 1.0);
  assert.equal(starts[1], 1.4);
  assert.ok(Math.abs(starts[2] - (1.4 + FADE_UP.STAGGER_S)) < 1e-12);
  assert.ok(Math.abs(starts[3] - (1.4 + 2 * FADE_UP.STAGGER_S)) < 1e-12);
  assert.deepEqual(staggerStarts([0.5], 2.0), [2.0], "a word cannot arrive before its page");
  assert.deepEqual(staggerStarts([], 2.0), []);
});

test("the dials are overridable as ONE preset, and the default preset is untouched", () => {
  const quiet = fadeUpDials({ RISE_PX: 12, DUR_S: 0.5 });
  assert.equal(quiet.RISE_PX, 12); assert.equal(quiet.DUR_S, 0.5);
  assert.equal(quiet.BLUR_PX, FADE_UP.BLUR_PX); assert.equal(quiet.STAGGER_S, FADE_UP.STAGGER_S);
  assert.equal(fadeUpAt(0.25, 0, quiet).y, 12 * (1 - minJerk(0.5)));
  assert.equal(FADE_UP.RISE_PX, 22);
  const st = staggerStarts([null, null], 0, 0.2);
  assert.deepEqual(st, [0, 0.2], "the stagger is a dial too");
});

test("THE SEEK TEST: frame N evaluated directly is the frame the scrub gives, bit-identical", () => {
  const starts = staggerStarts([0.5, 0.52, 0.9], 0.5), dt = 1 / 60;
  let walked = null;
  for (let n = 0; n <= 37; n++) walked = fadeUpPage(n * dt, starts);   // played in from zero
  assert.deepEqual(walked, fadeUpPage(37 * dt, starts));               // sought cold
  // and the starts themselves are a pure function of the page, not of the order it was read in
  assert.deepEqual(staggerStarts([0.5, 0.52, 0.9], 0.5), starts);
});


// ---- E90 (P57 T14): the caption's LIFE - the pop leads, the stagger rides under it ----------------
// What these pin: the three settings are NAMED and different pictures; the blend is a composition, not a
// switch (its rise and blur are the stagger's at the word's own onset); the POP LEADS (its clock is spent
// before the stagger reaches its middle); and the whole thing is the pure function of t the file promises.

const CH = ["e", "o", "y", "s", "b", "tilt"];

test("three NAMED settings, and the one number the pop got stronger by is stated", () => {
  assert.deepEqual([...LIVES], ["pop", "stagger", "blend"]);
  assert.ok(Object.isFrozen(LIVES) && Object.isFrozen(LIFE), "the settings and the dials are frozen");
  assert.equal(LIFE.POP_LEAD, 1.22, "E90 s2 'a little stronger': the base's 1.16 plus one notch");
  assert.equal(LIFE.POP_S, 0.2, "the shipped stage pop's window, unchanged");
  assert.equal(LIFE.ANTICIP_S, 0.05, "the shipped pop's anticipation - this is HOW the pop leads");
  const soft = lifeDials({ POP_LEAD: 1.16 });
  assert.equal(soft.POP_LEAD, 1.16); assert.equal(soft.POP_S, LIFE.POP_S);
  assert.equal(LIFE.POP_LEAD, 1.22, "the default preset is untouched by an override");
});

test("the blend at u = 0 IS the stagger's start - the rise is the envelope's own, from its full height", () => {
  const start = 4.0, b = lifeAt(start, start, "blend"), s = lifeAt(start, start, "stagger");
  assert.equal(b.y, FADE_UP.RISE_PX);
  assert.equal(b.y, s.y);
  assert.equal(b.b, 0, "the blend takes no blur: a 5 px blur at the onset is the word unreadable as it is said");
  assert.equal(b.e, 0, "nothing has landed at the onset");
  // and the pop is ALREADY under way there, which is the lead: the word is big and shrinking, not small and growing
  assert.ok(b.s > 1, `the pop's scale still rides above rest at the onset (${b.s})`);
  assert.equal(b.s, popAt(start, start).s, "the blend's SCALE is the pop's, on top of the stagger's y");
  assert.equal(b.o, 1, "the word is lit on the pop's clock, not faded in behind the stagger");
});

test("the blend is a COMPOSITION, channel by channel - the pop's scale and tilt, the stagger's rise, no blur", () => {
  const start = 3.0;
  for (let i = 0; i <= 200; i++) {
    const t = start - 0.1 + (i / 200) * (FADE_UP.DUR_S + 0.2);
    const b = lifeAt(t, start, "blend"), p = popAt(t, start), f = lifeAt(t, start, "stagger");
    assert.equal(b.s, p.s, `scale at ${t}`);
    assert.equal(b.tilt, p.tilt, `tilt at ${t}`);
    assert.equal(b.y, f.y, `y at ${t}`);
    assert.equal(b.b, 0, `blur at ${t} - the blend leaves the blur to the stagger setting`);
    assert.equal(b.o, Math.max(p.o, f.o), `opacity at ${t}`);
    assert.equal(b.e, Math.min(p.e, f.e), `landed at ${t}`);
  }
});

test("at u = 1 every setting is the REST POSE, exactly", () => {
  const start = 2.0, end = start + Math.max(FADE_UP.DUR_S, LIFE.POP_S);
  for (const kind of LIVES) {
    for (const t of [end, end + 1e-9, end + 10]) {
      const f = lifeAt(t, start, kind);
      assert.equal(f.e, 1, kind); assert.equal(f.o, 1, kind); assert.equal(f.y, 0, kind);
      assert.equal(f.s, 1, `${kind} scale ${f.s} - both factors land on exactly 1, so the product is rest`);
      assert.equal(f.b, 0, kind); assert.equal(f.tilt, 0, kind);
    }
  }
});

test("THE POP LEADS: its peak is past before the stagger reaches its middle", () => {
  const start = 1.0, mid = start + FADE_UP.DUR_S / 2;
  let peak = { s: -Infinity, t: null };
  for (let i = 0; i <= 2000; i++) {
    const t = start - LIFE.ANTICIP_S + (i / 2000) * (LIFE.POP_S + 0.2), s = popAt(t, start).s;
    if (s > peak.s) peak = { s, t };
  }
  assert.ok(Math.abs(peak.s - LIFE.POP_LEAD) < 1e-9, `the pop's peak scale is POP_LEAD (${peak.s})`);
  assert.ok(peak.t < mid, `the pop peaks at ${peak.t}, the stagger's middle is ${mid}`);
  // and the pop's whole clock is SPENT by then - it leads, the stagger is still carrying the word
  assert.equal(popAt(mid, start).e, 1, "the pop has landed by the stagger's middle");
  assert.ok(lifeAt(mid, start, "stagger").e < 0.75, "the stagger is still arriving there");
  // ONE arrival, not two events: once the pop's clock is spent nothing scales above rest again
  for (let i = 0; i <= 400; i++) {
    const t = start + LIFE.POP_S + (i / 400) * FADE_UP.DUR_S;
    assert.ok(lifeAt(t, start, "blend").s <= 1 + 1e-12, `the blend re-pops at ${t}`);
  }
});

test("the three settings are three different pictures at one t", () => {
  const start = 0.5, t = start + 0.01;
  const [p, s, b] = LIVES.map((k) => lifeAt(t, start, k));
  const differs = (a, c) => CH.some((k) => Math.abs(a[k] - c[k]) > 1e-9);
  assert.ok(differs(p, s), "the pop is not the stagger");
  assert.ok(differs(p, b), "the pop is not the blend");
  assert.ok(differs(s, b), "the stagger is not the blend");
  assert.equal(p.y, 0, "the pop alone does not move the word - the base never did");
  assert.equal(s.tilt, 0, "the stagger drops the tilt: punctuation is what it removes");
  assert.ok(b.y > 0 && b.s > 1, "the blend has the stagger's rise AND the pop's scale");
});

test("a pure function of t: two calls agree, and a cold seek is the played frame", () => {
  const starts = staggerStarts([0.5, 0.52, 0.9], 0.5), dt = 1 / 60;
  for (const kind of LIVES) {
    assert.deepEqual(lifeAt(0.63, 0.5, kind), lifeAt(0.63, 0.5, kind));
    let walked = null;
    for (let n = 0; n <= 37; n++) walked = lifePage(n * dt, starts, kind);
    assert.deepEqual(walked, lifePage(37 * dt, starts, kind), kind);
  }
});

test("an unknown setting THROWS - a typo never silently paints the base", () => {
  assert.throws(() => lifeAt(1, 1, "blended"), /blended/);
  assert.throws(() => lifeAt(1, 1, "blended"), /pop, stagger, blend/);
});
