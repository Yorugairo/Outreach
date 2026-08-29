import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import React from "react";
import { describe, test } from "vitest";
import {
  CANONICAL_TRANSCRIPT_CAPTION_ID,
  REMOTION_BIT_IDS,
  TranscriptCaptionAdapter,
  buildTranscriptCaptionLines,
  getRevealedTranscriptCaptionTokens,
  normalizeTranscriptCaptionTokens,
  projectTranscriptCaptionText,
  renderRemotionBit,
  renderTranscriptCaption,
  type TranscriptCaptionToken,
} from "../remotionBits";

const shortCue = [
  { text: "Price,", startFrame: 0, endFrame: 4 },
  { text: "moves", startFrame: 4, endFrame: 8 },
  { text: "fast!", startFrame: 8, endFrame: 12 },
] as const;

describe("canonical transcript_caption adapter", () => {
  test("normalizes snapshot words into immutable frame tokens without changing text", () => {
    const source = [
      { text: "Read", start_frame: 2, end_frame: 5 },
      { text: "this", startFrame: 5, endFrame: 9 },
    ];

    const tokens = normalizeTranscriptCaptionTokens(source);

    assert.deepEqual(tokens, [
      { text: "Read", startFrame: 2, endFrame: 5 },
      { text: "this", startFrame: 5, endFrame: 9 },
    ]);
    assert.equal(Object.isFrozen(tokens), true);
    assert.equal(Object.isFrozen(tokens[0]), true);
    assert.throws(
      () => normalizeTranscriptCaptionTokens([{ text: "bad", startFrame: 5, endFrame: 5 }]),
      /endFrame must be greater than startFrame/,
    );
  });

  test("projects punctuation exactly and activates every token at its canonical start", () => {
    const tokens = normalizeTranscriptCaptionTokens(shortCue);

    assert.equal(projectTranscriptCaptionText(tokens), "Price, moves fast!");
    assert.deepEqual(getRevealedTranscriptCaptionTokens(tokens, -1), []);
    assert.deepEqual(getRevealedTranscriptCaptionTokens(tokens, 3).map(({ text }) => text), ["Price,"]);
    assert.deepEqual(getRevealedTranscriptCaptionTokens(tokens, 4).map(({ text }) => text), ["Price,", "moves"]);
    assert.deepEqual(getRevealedTranscriptCaptionTokens(tokens, 8).map(({ text }) => text), ["Price,", "moves", "fast!"]);
  });

  test("keeps a stable maximum-two-line layout and attaches punctuation to its preceding line", () => {
    const tokens = normalizeTranscriptCaptionTokens([
      { text: "A", startFrame: 0, endFrame: 2, lineGroup: 1 },
      { text: "stable", startFrame: 2, endFrame: 4, lineGroup: 1 },
      { text: "layout", startFrame: 4, endFrame: 6, lineGroup: 1 },
      { text: ",", startFrame: 6, endFrame: 7, lineGroup: 2 },
      { text: "keeps", startFrame: 7, endFrame: 9, lineGroup: 2 },
      { text: "words", startFrame: 9, endFrame: 11, lineGroup: 2 },
      { text: "attached.", startFrame: 11, endFrame: 14, lineGroup: 2 },
    ]);

    const first = buildTranscriptCaptionLines(tokens);
    const second = buildTranscriptCaptionLines(tokens);

    assert.equal(first.length, 2);
    assert.equal(first.every((line) => line.tokens.length > 0), true);
    assert.deepEqual(first.map((line) => projectTranscriptCaptionText(line.tokens)), [
      "A stable layout,",
      "keeps words attached.",
    ]);
    assert.deepEqual(first, second);
    assert.equal(first.flatMap((line) => line.tokens).length, tokens.length);
    assert.equal(first.flatMap((line) => line.tokens).some((token) => token.text === "," && token.lineGroup !== 1), false);
  });

  test("handles fast canonical starts without a fixed stagger or a second caption bit", () => {
    const tokens = normalizeTranscriptCaptionTokens([
      { text: "Fast", startFrame: 0, endFrame: 3 },
      { text: "words", startFrame: 1, endFrame: 3 },
      { text: "can", startFrame: 1, endFrame: 4 },
      { text: "land.", startFrame: 2, endFrame: 5 },
    ]);

    assert.deepEqual(getRevealedTranscriptCaptionTokens(tokens, 1).map(({ text }) => text), ["Fast", "words", "can"]);
    assert.deepEqual(getRevealedTranscriptCaptionTokens(tokens, 2).map(({ text }) => text), ["Fast", "words", "can", "land."]);
    assert.equal(CANONICAL_TRANSCRIPT_CAPTION_ID, "transcript_caption");
    assert.equal(REMOTION_BIT_IDS.includes(CANONICAL_TRANSCRIPT_CAPTION_ID as never), false);
    assert.equal(React.isValidElement(renderRemotionBit("word-by-word", { text: "legacy" })), true);

    const source = readFileSync(new URL("../remotionBits/wordTimedCaption.tsx", import.meta.url), "utf8");
    assert.doesNotMatch(source, /AnimatedText|splitStagger|staggerFrames/);
  });

  test("exposes one protected renderer while keeping canonical props immutable", () => {
    const tokens = normalizeTranscriptCaptionTokens(shortCue) as readonly TranscriptCaptionToken[];
    const element = renderTranscriptCaption({ tokens, style: { color: "#fff" } });

    assert.equal(element.type, TranscriptCaptionAdapter);
    assert.equal(element.props.componentId, CANONICAL_TRANSCRIPT_CAPTION_ID);
    assert.equal(Object.isFrozen(element.props.tokens), true);
    assert.equal(element.props.tokens, tokens);
  });
});
