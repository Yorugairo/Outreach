// P73 T3 - THE POST CARD: a press card whose header is a social post. The header's rows and the face its pulled
// phrase is set in are pure functions of the dock entry the compiler wrote, so the painter only mounts them.
import { test } from "node:test";
import assert from "node:assert/strict";
import { PRESS, PRESS_FACES, pressFace, pressFaceFor, pressHeader, pressHeadStep, pressRest, pressXf }
  from "../../scripts/species/press.mjs";

const POST = { kind: "press", source: "X / @dylan522p, 19 Sep 2026", style: "post",
  post: { name: "Dylan Patel", handle: "@dylan522p", when: "19 Sep 2026, 16:41 UTC",
          counts: "392,513 views as of 26 Sep 2026" } };

test("a post's header is the poster's row over the meta row, in the order the author typed them", () => {
  assert.deepEqual(pressHeader(POST), {
    style: "post", poster: ["Dylan Patel", "@dylan522p"], meta: ["19 Sep 2026, 16:41 UTC", "392,513 views as of 26 Sep 2026"] });
});

test("a post with no counts has an empty right cell, never a made-up one", () => {
  const d = { ...POST, post: { ...POST.post } };
  delete d.post.counts;
  assert.deepEqual(pressHeader(d).meta, ["19 Sep 2026, 16:41 UTC", ""]);
});

test("the masthead is the default: a card with no style, or a style with no post, is the source strip it was", () => {
  const plain = { kind: "press", source: "The Herald, 4 Mar 2026" };
  assert.deepEqual(pressHeader(plain), { style: "masthead", poster: null, meta: ["The Herald, 4 Mar 2026"] });
  assert.deepEqual(pressHeader({ ...plain, style: "post" }), pressHeader(plain));
  assert.deepEqual(pressHeader(null), { style: "masthead", poster: null, meta: [""] });
});

test("the post face is one of the three offered, and a post keeps it whatever the dial says", () => {
  assert.ok(PRESS_FACES[PRESS.POST_FACE], "POST_FACE names a face that is already on the page");
  for (const dial of [undefined, "house", "serif", "condensed", "typo"]) {
    assert.equal(pressFaceFor(POST, dial), PRESS_FACES[PRESS.POST_FACE]);
  }
});

test("a masthead card follows the dial exactly as pressFace does", () => {
  for (const dial of [undefined, "house", "serif", "condensed", "typo"]) {
    assert.equal(pressFaceFor({ kind: "press" }, dial), pressFace(dial));
    assert.equal(pressFaceFor(null, dial), pressFace(dial));
  }
});

test("the head step puts a header's bottom exactly on the edge of the card in front, one step back", () => {
  // the card's box: top 330, H 400; the header's bottom 96 px below its top. Posed one step back with the head step,
  // that point lands on y = 330 - the top of the card in front (the pile's one box) - and not a pixel lower.
  const H = 400, hb = 96, box = { x: 432, y: 330, w: 1056, h: H };
  const step = pressHeadStep(H, hb);
  const rest = pressRest(1, { STEP_PX: step });
  const q = pressXf(box, { dx: 0, dy: rest.dy, scale: rest.scale, sx: 1, skew: 0 })({ x: 500, y: 330 + hb, w: 1, h: 0 });
  assert.ok(Math.abs(q.y - 330) < 1e-9, String(q.y));
});

test("the head step grows with the header and with the card, and an unknown length asks for none", () => {
  assert.ok(pressHeadStep(400, 120) > pressHeadStep(400, 80));
  assert.ok(pressHeadStep(500, 80) > pressHeadStep(400, 80));
  for (const [H, hb] of [[0, 80], [400, 0], [NaN, 80], [400, undefined]]) assert.equal(pressHeadStep(H, hb), 0);
});
