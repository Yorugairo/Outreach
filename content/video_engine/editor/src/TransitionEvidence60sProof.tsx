import React from "react";
import { AbsoluteFill, Audio, Img, Sequence, staticFile, useCurrentFrame } from "remotion";
import { TransitionSeries, linearTiming } from "@remotion/transitions";
import { bookFlip } from "@remotion/transitions/book-flip";
import { wipe } from "@remotion/transitions/wipe";
import {
  buildProductionTimelineItemStyle,
  EvidenceRevealCard,
  type ProductionTimelineCompositionProps,
  type ProductionTimelineItem,
} from "./ProductionTimelineComposition";
import { KenBurnsAdapter, renderTranscriptCaption } from "./remotionBits";

export type TransitionEvidence60sProofProps = ProductionTimelineCompositionProps;

export const defaultTransitionEvidence60sProofProps: TransitionEvidence60sProofProps = {
  schema_version: "production_console_snapshot.v2",
  snapshot_id: "current-bubble-transition-evidence-60s-v4",
  width: 1920,
  height: 1080,
  fps: 30,
  durationInFrames: 1800,
  backgroundColor: "#0b1015",
  assetMap: {},
  items: [],
};

const itemType = (item: ProductionTimelineItem) => item.item_type ?? item.type;
const itemId = (item: ProductionTimelineItem) => item.item_id ?? item.id ?? "timeline-item";
const itemFrom = (item: ProductionTimelineItem) => Math.max(0, Math.round(item.start_frame ?? item.from ?? 0));
const itemDuration = (item: ProductionTimelineItem) => Math.max(1, Math.round(item.durationInFrames ?? ((item.end_frame ?? itemFrom(item)) - itemFrom(item))));
const clamp = (value: number, minimum: number, maximum: number) => Math.min(maximum, Math.max(minimum, value));

const sourceFor = (item: ProductionTimelineItem, assetMap: Readonly<Record<string, string>>) => {
  const assetId = item.assetId ?? item.asset_id;
  return assetId ? assetMap[assetId] : undefined;
};

const WorldPlate: React.FC<{
  item: ProductionTimelineItem;
  assetMap: Readonly<Record<string, string>>;
  direction: "left" | "right" | "up" | "down";
}> = ({ item, assetMap, direction }) => {
  const source = sourceFor(item, assetMap);
  if (!source) return <AbsoluteFill style={{ backgroundColor: "#0b1015" }} />;
  return (
    <AbsoluteFill>
      <KenBurnsAdapter
        images={[source]}
        durationInFrames={itemDuration(item)}
        direction={direction}
        scaleFrom={1.008}
        scaleTo={1.045}
      />
    </AbsoluteFill>
  );
};

const BookFlipBreak: React.FC<{
  outgoing: ProductionTimelineItem;
  incoming: ProductionTimelineItem;
  assetMap: Readonly<Record<string, string>>;
}> = ({ outgoing, incoming, assetMap }) => {
  const outgoingSource = sourceFor(outgoing, assetMap);
  const incomingSource = sourceFor(incoming, assetMap);
  if (!outgoingSource || !incomingSource) return null;
  return (
    <TransitionSeries>
      <TransitionSeries.Sequence durationInFrames={20}>
        <Img src={staticFile(outgoingSource)} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
      </TransitionSeries.Sequence>
      <TransitionSeries.Transition presentation={bookFlip({ direction: "from-right" })} timing={linearTiming({ durationInFrames: 20 })} />
      <TransitionSeries.Sequence durationInFrames={20}>
        <Img src={staticFile(incomingSource)} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
      </TransitionSeries.Sequence>
    </TransitionSeries>
  );
};

const WipeBreak: React.FC<{
  outgoing: ProductionTimelineItem;
  incoming: ProductionTimelineItem;
  assetMap: Readonly<Record<string, string>>;
}> = ({ outgoing, incoming, assetMap }) => {
  const outgoingSource = sourceFor(outgoing, assetMap);
  const incomingSource = sourceFor(incoming, assetMap);
  if (!outgoingSource || !incomingSource) return null;
  return (
    <TransitionSeries>
      <TransitionSeries.Sequence durationInFrames={16}>
        <Img src={staticFile(outgoingSource)} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
      </TransitionSeries.Sequence>
      <TransitionSeries.Transition presentation={wipe({ direction: "from-left" })} timing={linearTiming({ durationInFrames: 16 })} />
      <TransitionSeries.Sequence durationInFrames={16}>
        <Img src={staticFile(incomingSource)} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
      </TransitionSeries.Sequence>
    </TransitionSeries>
  );
};

const EvidenceLayer: React.FC<{
  item: ProductionTimelineItem;
  assetMap: Readonly<Record<string, string>>;
  fps: number;
}> = ({ item, assetMap, fps }) => {
  const frame = useCurrentFrame();
  const durationInFrames = itemDuration(item);
  const source = sourceFor(item, assetMap);
  const handSource = assetMap["whiteboard-draw-hand-a-v1"];
  return (
    <div style={buildProductionTimelineItemStyle(item, frame, fps, durationInFrames, itemFrom(item))}>
      <EvidenceRevealCard item={item} source={source ? staticFile(source) : undefined} handSource={handSource ? staticFile(handSource) : undefined} frame={frame} fps={fps} durationInFrames={durationInFrames} />
    </div>
  );
};

const CaptionLayer: React.FC<{
  item: ProductionTimelineItem;
  evidenceItems: readonly ProductionTimelineItem[];
  fps: number;
}> = ({ item, evidenceItems, fps }) => {
  const frame = useCurrentFrame();
  const absoluteFrame = itemFrom(item) + frame;
  const activeEvidence = evidenceItems
    .filter((evidence) => itemFrom(evidence) <= absoluteFrame && absoluteFrame < itemFrom(evidence) + itemDuration(evidence))
    .sort((left, right) => itemFrom(right) - itemFrom(left))[0];
  const evidenceLayout = activeEvidence?.layout;
  const captionLayout = evidenceLayout
    ? {
        ...item.layout,
        x: evidenceLayout.x ?? item.layout?.x,
        y: clamp((evidenceLayout.y ?? 0) - ((evidenceLayout.height ?? 0.42) / 2) - 0.12, -0.32, 0.34),
      }
    : item.layout;
  const positioned = { ...item, layout: captionLayout, backgroundColor: "transparent" };
  return (
    <div style={buildProductionTimelineItemStyle(positioned, frame, fps, itemDuration(item), itemFrom(item))}>
      {renderTranscriptCaption({
        tokens: item.word_tokens ?? [],
        color: item.color ?? "#fffaf0",
        fontSize: item.fontSize ?? 42,
        backgroundColor: "transparent",
        style: { textShadow: "0 2px 10px rgba(3, 10, 16, .96), 0 0 2px rgba(3, 10, 16, .96)" },
      })}
    </div>
  );
};

const BREAK_TYPES = new Map<number, "book_flip" | "wipe" | "cut">([
  [72, "cut"],
  [386, "book_flip"],
  [691, "wipe"],
  [1175, "cut"],
  [1592, "book_flip"],
]);
const directions: readonly ("left" | "right" | "up" | "down")[] = ["right", "left", "up", "right", "left", "down"];

/**
 * A review-only composition: canonical narration/timings and approved evidence
 * remain unchanged; only world-plate motion and scene-break presentation vary.
 */
export const TransitionEvidence60sProof: React.FC<TransitionEvidence60sProofProps> = (props) => {
  const items = props.items ?? props.timeline?.items ?? [];
  const assetMap = props.assetMap ?? props.asset_map ?? {};
  const fps = props.fps ?? 30;
  const worlds = items.filter((item) => itemType(item) === "world_plate").sort((left, right) => itemFrom(left) - itemFrom(right));
  const evidenceItems = items.filter((item) => itemType(item) === "evidence");
  const captionItems = items.filter((item) => itemType(item) === "caption");
  const narrationItems = items.filter((item) => itemType(item) === "narration");

  return (
    <AbsoluteFill style={{ backgroundColor: props.backgroundColor ?? "#0b1015", overflow: "hidden" }}>
      {worlds.map((world, index) => (
        <Sequence key={itemId(world)} from={itemFrom(world)} durationInFrames={itemDuration(world)}>
          <WorldPlate item={world} assetMap={assetMap} direction={directions[index % directions.length]} />
        </Sequence>
      ))}

      {worlds.slice(1).map((incoming, index) => {
        const outgoing = worlds[index];
        const boundary = itemFrom(incoming);
        const transition = BREAK_TYPES.get(boundary);
        if (!transition || transition === "cut") return null;
        const durationInFrames = transition === "wipe" ? 16 : 20;
        const from = boundary - Math.floor(durationInFrames / 2);
        return (
          <Sequence key={`${transition}-${boundary}`} from={from} durationInFrames={durationInFrames}>
            {transition === "book_flip" ? <BookFlipBreak outgoing={outgoing} incoming={incoming} assetMap={assetMap} /> : null}
            {transition === "wipe" ? <WipeBreak outgoing={outgoing} incoming={incoming} assetMap={assetMap} /> : null}
          </Sequence>
        );
      })}

      {evidenceItems.map((item) => (
        <Sequence key={itemId(item)} from={itemFrom(item)} durationInFrames={itemDuration(item)}>
          <EvidenceLayer item={item} assetMap={assetMap} fps={fps} />
        </Sequence>
      ))}

      {captionItems.map((item) => (
        <Sequence key={itemId(item)} from={itemFrom(item)} durationInFrames={itemDuration(item)}>
          <CaptionLayer item={item} evidenceItems={evidenceItems} fps={fps} />
        </Sequence>
      ))}

      {narrationItems.map((item) => {
        const source = sourceFor(item, assetMap);
        return source ? <Audio key={itemId(item)} src={staticFile(source)} volume={item.volume ?? 1} /> : null;
      })}
    </AbsoluteFill>
  );
};
