import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import React from "react";
import { describe, test } from "vitest";
import {
  buildProductionTimelineItemStyle,
  buildProductionTimelineSequences,
  calculateProductionTimelineMetadata,
  evidenceRevealGeometry,
  evaluateProductionTimelineKeyframes,
  PRODUCTION_TIMELINE_ITEM_TYPES,
  type ProductionTimelineItem,
} from "../ProductionTimelineComposition";
import {
  CURATED_REMOTION_BITS,
  REMOTION_BIT_IDS,
  REMOTION_BITS_REGISTRY,
  normalizeRemotionBitAsset,
  renderRemotionBit,
} from "../remotionBits";

const timelineItems: ProductionTimelineItem[] = [
  { item_id: "scene", item_type: "scene", start_frame: 0, end_frame: 24, locked: false, locked_fields: [], title: "Scene" },
  { item_id: "cue", item_type: "cue", start_frame: 24, end_frame: 48, locked: true, locked_fields: ["word_timing"], excerpt: "Cue" },
  { item_id: "caption", item_type: "caption", start_frame: 48, end_frame: 72, locked: false, locked_fields: [], text: "Caption" },
  { item_id: "overlay", item_type: "overlay", start_frame: 72, end_frame: 96, locked: false, locked_fields: [], display_text: "Overlay" },
  { item_id: "stamp", item_type: "teacher_stamp", start_frame: 96, end_frame: 120, locked: true, locked_fields: ["approval"], text: "Approved" },
  { item_id: "evidence", item_type: "evidence", start_frame: 120, end_frame: 144, locked: true, locked_fields: ["approval"], label: "Evidence" },
  { item_id: "world", item_type: "world_plate", start_frame: 144, end_frame: 168, locked: false, locked_fields: [], component_id: "world-plate" },
  { item_id: "narration", item_type: "narration", start_frame: 168, end_frame: 192, locked: true, locked_fields: ["audio_source"] },
];

const remotionBitItem: ProductionTimelineItem = {
  id: "bit",
  type: "remotion_bit",
  from: 12,
  durationInFrames: 36,
  componentId: "fade-in",
  props: { text: "Bit" },
  transform: { x: 0.2, y: -0.1, scaleX: 1.1, scaleY: 0.9, rotation: 8, opacity: 0.8, zIndex: 4 },
  keyframes: {
    x: [{ frame: 12, value: 0, easing: "linear" }, { frame: 24, value: 0.4, easing: "linear" }],
    opacity: [{ frame: 12, value: 1 }, { frame: 24, value: 0.5, easing: "linear" }],
  },
};

const canonicalRemotionBitItem: ProductionTimelineItem = {
  item_id: "canonical-bit",
  item_type: "remotion_bit",
  start_frame: 20,
  end_frame: 44,
  locked: false,
  locked_fields: [],
  component_id: "basic-counter",
  bit_props: { from: 10, to: 20 },
};

describe("production timeline composition", () => {
  test("keeps the eight timeline item kinds closed and frame-based", () => {
    assert.deepEqual(PRODUCTION_TIMELINE_ITEM_TYPES, [
      "scene",
      "cue",
      "caption",
      "overlay",
      "teacher_stamp",
      "evidence",
      "world_plate",
      "narration",
    ]);

    const sequences = buildProductionTimelineSequences(timelineItems, 24);
    assert.equal(sequences.length, 8);
    assert.deepEqual(
      sequences.map(({ from, durationInFrames, premountFor }) => ({ from, durationInFrames, premountFor })),
      timelineItems.map(({ start_frame, end_frame }) => ({ from: start_frame!, durationInFrames: end_frame! - start_frame!, premountFor: 24 })),
    );

    const bitSequence = buildProductionTimelineSequences([remotionBitItem], 24)[0];
    assert.deepEqual(
      { from: bitSequence.from, durationInFrames: bitSequence.durationInFrames, premountFor: bitSequence.premountFor },
      { from: 12, durationInFrames: 36, premountFor: 24 },
    );
    const canonicalBitSequence = buildProductionTimelineSequences([canonicalRemotionBitItem], 24)[0];
    assert.deepEqual(
      { from: canonicalBitSequence.from, durationInFrames: canonicalBitSequence.durationInFrames },
      { from: 20, durationInFrames: 24 },
    );
  });

  test("metadata expands to cover authored item frame ranges", () => {
    const props = {
      width: 1280,
      height: 720,
      fps: 24,
      durationInFrames: 12,
      items: [{ item_id: "late", item_type: "caption", start_frame: 40, end_frame: 60, locked: false, locked_fields: [], text: "late" }],
    } as const;
    const metadata = calculateProductionTimelineMetadata({
      defaultProps: {},
      props,
      abortSignal: new AbortController().signal,
      compositionId: "test",
      isRendering: false,
    });
    assert.deepEqual(metadata, { width: 1280, height: 720, fps: 24, durationInFrames: 60 });
  });

  test("evaluates editor keyframes against absolute frames and keeps center-origin layout", () => {
    assert.deepEqual(evaluateProductionTimelineKeyframes(remotionBitItem, 6, 12), { x: 0.2, opacity: 0.75 });
    const style = buildProductionTimelineItemStyle(remotionBitItem, 6, 24, 36, 12);
    assert.equal(style.left, "70%");
    assert.equal(style.top, "40%");
    assert.equal(style.width, "72%" );
    assert.equal(style.height, "66%" );
    assert.equal(style.transformOrigin, "center center");
    assert.match(String(style.transform), /translate\(-50%, -50%\)/);
    assert.match(String(style.transform), /scaleX\(1\.1\)/);
    const worldStyle = buildProductionTimelineItemStyle(timelineItems[6], 0, 24, 24, 144);
    assert.equal(worldStyle.width, "100%");
    assert.equal(worldStyle.height, "100%");
    assert.equal(worldStyle.opacity, 1);
    const captionStyle = buildProductionTimelineItemStyle(timelineItems[2], 0, 24, 24, 48);
    assert.equal(captionStyle.overflow, "visible");
  });

  test("reveals one evidence source with a serpentine hand lifecycle", () => {
    assert.deepEqual(evidenceRevealGeometry(0, 30, 90), {progress: 0, row: 0, rowProgress: 0, handX: 0, handY: .58 / 6, handVisible: false});
    const drawing = evidenceRevealGeometry(15, 30, 90);
    assert.equal(drawing.handVisible, true);
    assert.ok(drawing.progress > 0 && drawing.progress < 1);
    assert.equal(evidenceRevealGeometry(90, 30, 90).handVisible, false);
  });

  test("each sequence is premounted and uses the shared composition path", () => {
    const source = readFileSync(new URL("../ProductionTimelineComposition.tsx", import.meta.url), "utf8");
    assert.match(source, /<Sequence[\s\S]*premountFor=\{sequence\.premountFor\}/);
    assert.doesNotMatch(source, /fetch\s*\(/);
    assert.doesNotMatch(source, /https?:\/\//);
    assert.match(source, /case "teacher_stamp":[\s\S]*resolveTimelineAsset\(item, assetMap\)[\s\S]*<Img/);
    assert.match(source, /EVIDENCE_REVEAL_ROWS = 6/);
    assert.match(source, /whiteboard-draw-hand-a-v1/);
    assert.match(source, /overlayKind === "arrow"/);
    assert.doesNotMatch(source, /item\.label \?\? item\.text \?\? "Evidence"/);
    assert.doesNotMatch(source, /item\.text \?\? item\.label \?\? "Overlay"/);
    assert.match(source, /const copy = item\.display_text/);
    assert.match(source, /diagnosticMode=\{props\.diagnosticMode === true\}/);
  });
});

describe("curated Remotion Bits adapters", () => {
  test("registry is exactly the eleven reviewed names", () => {
    assert.deepEqual(REMOTION_BIT_IDS, [
      "fade-in",
      "blur-in",
      "word-by-word",
      "slide-from-left",
      "basic-typewriter",
      "basic-counter",
      "list-reveal",
      "grid-stagger",
      "mosaic-reframe",
      "3d-card-stack",
      "ken-burns-effect",
    ]);
    assert.deepEqual(Object.keys(REMOTION_BITS_REGISTRY), [...REMOTION_BIT_IDS]);
    assert.equal(CURATED_REMOTION_BITS.length, 11);
    assert.deepEqual(
      CURATED_REMOTION_BITS.map(({ name }) => name),
      [
        "Fade In",
        "Blur In",
        "Word by Word",
        "Slide from Left",
        "Basic Typewriter",
        "Basic Counter",
        "List Reveal",
        "Grid Stagger",
        "Mosaic Reframe",
        "3D Card Stack",
        "Ken Burns Effect",
      ],
    );
  });

  test("every allowlisted adapter renders from typed default props", () => {
    for (const id of REMOTION_BIT_IDS) {
      const definition = REMOTION_BITS_REGISTRY[id];
      assert.equal(definition.packageVersion, "0.2.0");
      assert.equal(React.isValidElement(renderRemotionBit(id)), true, id);
    }
  });

  test("asset resolution fails closed for live or escaping sources", () => {
    assert.equal(normalizeRemotionBitAsset("https://example.com/image.png"), undefined);
    assert.equal(normalizeRemotionBitAsset("../outside.png"), undefined);
    assert.equal(normalizeRemotionBitAsset("C:/outside.png"), undefined);
    assert.equal(normalizeRemotionBitAsset("/media/wrong-bubble-elevators-v2"), "/media/wrong-bubble-elevators-v2");
    assert.equal(normalizeRemotionBitAsset("/media/../../outside.png"), undefined);
    assert.equal(normalizeRemotionBitAsset("approved/image.png"), "/approved/image.png");
  });
});
