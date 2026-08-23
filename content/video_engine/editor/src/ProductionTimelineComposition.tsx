import React from "react";
import {
  AbsoluteFill,
  Audio,
  CalculateMetadataFunction,
  Img,
  Sequence,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import {
  REMOTION_BIT_IDS,
  renderRemotionBit,
  renderTranscriptCaption,
  type RemotionBitId,
  type RemotionBitInput,
  type RemotionBitProps,
  type RemotionBitRenderContext,
  type TranscriptCaptionTokenInput,
  normalizeRemotionBitAsset,
} from "./remotionBits";

export const PRODUCTION_TIMELINE_ITEM_TYPES = [
  "scene",
  "cue",
  "caption",
  "overlay",
  "teacher_stamp",
  "evidence",
  "world_plate",
  "narration",
] as const;

export type ProductionTimelineCanonicalItemType = (typeof PRODUCTION_TIMELINE_ITEM_TYPES)[number];
export type ProductionTimelineItemType = ProductionTimelineCanonicalItemType | "remotion_bit";
export type ProductionTimelineLegacyItemType = ProductionTimelineItemType | "annotation";

export type ProductionTimelineLayout = {
  x?: number;
  y?: number;
  width?: number;
  height?: number;
  scale?: number;
  scaleX?: number;
  scaleY?: number;
  rotate?: number;
  rotation?: number;
  opacity?: number;
  z?: number;
  zIndex?: number;
  fit?: "contain" | "cover";
};

export type ProductionTimelineTransform = {
  x?: number;
  y?: number;
  scale?: number;
  scaleX?: number;
  scaleY?: number;
  rotation?: number;
  opacity?: number;
  z?: number;
  zIndex?: number;
  crop?: {
    x?: number;
    y?: number;
    width?: number;
    height?: number;
  };
};

/** A normalized crop of the source image, independent of the item canvas box. */
export type ProductionTimelineSourceCrop = {
  x?: number;
  y?: number;
  width?: number;
  height?: number;
};

export type ProductionTimelineKeyframeProperty =
  | "x"
  | "y"
  | "scaleX"
  | "scaleY"
  | "rotation"
  | "opacity"
  | "zIndex";

export type ProductionTimelineKeyframe = {
  frame: number;
  value: number;
  easing?: "linear" | "smoothstep" | "ease_in" | "ease_out" | "ease_in_out";
  springPreset?: "gentle" | "snappy" | "bouncy";
};

export type ProductionTimelineKeyframes = Partial<
  Record<ProductionTimelineKeyframeProperty, readonly ProductionTimelineKeyframe[]>
>;

export const PRODUCTION_TIMELINE_COMPONENT_IDS = [
  "caption",
  "text-overlay",
  "annotation",
  "teacher-stamp",
  "world-plate",
  "evidence-plate",
  "shape",
  "chart",
  ...REMOTION_BIT_IDS,
] as const;

export type ProductionTimelineComponentId =
  | (typeof PRODUCTION_TIMELINE_COMPONENT_IDS)[number]
  | "bit-fade-in"
  | "bit-blur-in"
  | "bit-word-by-word"
  | "bit-slide-from-left"
  | "bit-basic-typewriter"
  | "bit-basic-counter"
  | "bit-list-reveal"
  | "bit-grid-stagger"
  | "bit-mosaic-reframe"
  | "bit-3d-card-stack"
  | "bit-ken-burns";

export type ProductionTimelineLockedField =
  | "text"
  | "word_timing"
  | "asset_id"
  | "asset_hash"
  | "approval"
  | "evidence_eligibility"
  | "source_ref"
  | "audio_source";

export type ProductionTimelineItemBase = {
  item_id: string;
  item_type: ProductionTimelineItemType;
  start_frame: number;
  end_frame: number;
  locked: boolean;
  locked_fields: readonly ProductionTimelineLockedField[];
  source_ref?: string;
  scene_id?: string;
  cue_id?: string;
  asset_id?: string;
  sha256?: string;
  component_id?: ProductionTimelineComponentId;
  preset_id?: string;
  presetId?: string;
  start_word?: number;
  end_word?: number;
  text?: string;
  display_text?: string;
  citation_id?: string;
  diagnostic_label?: string;
  caption_preset?: "compact" | "word_by_word";
  word_tokens?: readonly TranscriptCaptionTokenInput[];
  excerpt?: string;
  style_id?: string;
  evidence_eligible?: boolean;
  x?: number;
  y?: number;
  scale?: number;
  scaleX?: number;
  scaleY?: number;
  rotation?: number;
  z?: number;
  transform?: ProductionTimelineTransform;
  sourceCrop?: ProductionTimelineSourceCrop;
  keyframes?: ProductionTimelineKeyframes;
  /** In-memory aliases retained for small Player fixtures. */
  id?: string;
  type?: ProductionTimelineLegacyItemType;
  from?: number;
  durationInFrames?: number;
  premountFor?: number;
  zIndex?: number;
  opacity?: number;
  layout?: ProductionTimelineLayout;
  assetId?: string;
  componentId?: ProductionTimelineComponentId;
  props?: RemotionBitProps;
  bit?: RemotionBitInput;
  title?: string;
  subtitle?: string;
  backgroundColor?: string;
  color?: string;
  fontSize?: number;
  label?: string;
  status?: "approved" | "review_only";
  volume?: number;
  overlayKind?: "text" | "annotation" | "shape" | "arrow";
  overlay_kind?: "text" | "annotation" | "shape" | "arrow";
  /** Compatibility aliases for the revision JSON/editor boundary. */
  bit_id?: RemotionBitId;
  bit_props?: RemotionBitProps;
};

type ProductionTimelineItemCommonFields = Omit<ProductionTimelineItemBase, "item_id" | "item_type" | "start_frame" | "end_frame" | "locked" | "locked_fields"> & {
  item_id?: string;
  item_type?: ProductionTimelineItemType;
  start_frame?: number;
  end_frame?: number;
  locked?: boolean;
  locked_fields?: readonly ProductionTimelineLockedField[];
  title?: string;
  subtitle?: string;
  backgroundColor?: string;
  color?: string;
  fontSize?: number;
  label?: string;
  status?: "approved" | "review_only";
  volume?: number;
};

type ProductionTimelineLegacyItemBase = ProductionTimelineItemCommonFields & {
  id: string;
  type: ProductionTimelineLegacyItemType;
  from: number;
  durationInFrames: number;
};

type ProductionTimelineItemFor<
  K extends ProductionTimelineItemType,
  Fields extends object = Record<never, never>,
> =
  | (ProductionTimelineItemBase & { item_type: K; type?: K } & Fields)
  | (ProductionTimelineLegacyItemBase & { type: K; item_type?: K } & Fields);

type ProductionTimelineLegacyItemFor<
  K extends ProductionTimelineLegacyItemType,
  Fields extends object = Record<never, never>,
> = ProductionTimelineLegacyItemBase & { type: K; item_type?: K } & Fields;

export type ProductionTimelineSceneItem = ProductionTimelineItemFor<"scene", {
  title?: string;
  subtitle?: string;
  backgroundColor?: string;
}>;

export type ProductionTimelineCueItem = ProductionTimelineItemFor<"cue", {
  title?: string;
  color?: string;
  fontSize?: number;
  backgroundColor?: string;
}>;

export type ProductionTimelineCaptionItem = ProductionTimelineItemFor<"caption", {
  color?: string;
  fontSize?: number;
  backgroundColor?: string;
}>;

export type ProductionTimelineOverlayItem = ProductionTimelineItemFor<"overlay", {
  label?: string;
  color?: string;
  fontSize?: number;
  backgroundColor?: string;
}>;

export type ProductionTimelineTeacherStampItem = ProductionTimelineItemFor<"teacher_stamp", {
  text?: string;
  status?: "approved" | "review_only";
}>;

export type ProductionTimelineEvidenceItem = ProductionTimelineItemFor<"evidence", {
  label?: string;
  color?: string;
}>;

export type ProductionTimelineWorldPlateItem = ProductionTimelineItemFor<"world_plate", {
  label?: string;
}>;

export type ProductionTimelineNarrationItem = ProductionTimelineItemFor<"narration", {
  volume?: number;
}>;

export type ProductionTimelineRemotionBitItem = ProductionTimelineItemFor<"remotion_bit", {
  component_id?: ProductionTimelineComponentId;
  componentId?: ProductionTimelineComponentId;
  preset_id?: string;
  presetId?: string;
  props?: RemotionBitProps;
}>;

/** Compatibility item emitted by the editor for non-text overlay surfaces. */
export type ProductionTimelineAnnotationItem = ProductionTimelineLegacyItemFor<"annotation", {
  label?: string;
  color?: string;
  fontSize?: number;
  backgroundColor?: string;
}>;

export type ProductionTimelineItem =
  | ProductionTimelineSceneItem
  | ProductionTimelineCueItem
  | ProductionTimelineCaptionItem
  | ProductionTimelineOverlayItem
  | ProductionTimelineTeacherStampItem
  | ProductionTimelineEvidenceItem
  | ProductionTimelineWorldPlateItem
  | ProductionTimelineNarrationItem
  | ProductionTimelineRemotionBitItem
  | ProductionTimelineAnnotationItem;

export type ProductionTimelineCompositionProps = {
  schema_version?: "editorial_timeline_revision.v1" | "production_console_snapshot.v2";
  snapshot_id?: string;
  project_id?: string;
  composition_id?: string;
  width?: number;
  height?: number;
  fps?: number;
  durationInFrames?: number;
  duration_in_frames?: number;
  items?: readonly ProductionTimelineItem[];
  timeline?: { readonly items: readonly ProductionTimelineItem[] };
  tracks?: readonly ProductionTimelineTrack[];
  project_profile?: ProductionTimelineProjectProfile;
  assets?: readonly ProductionTimelineAsset[];
  approved_assets?: readonly ProductionTimelineAsset[];
  assetMap?: Readonly<Record<string, string>>;
  asset_map?: Readonly<Record<string, string>>;
  backgroundColor?: string;
  diagnosticMode?: boolean;
};

export type ProductionTimelineTrack = {
  track_id: string;
  kind: "scenes" | "cues" | "captions" | "overlays" | "teacher_stamp" | "evidence" | "world_plates" | "narration";
  label?: string;
  order?: number;
  editable?: boolean;
  items: readonly ProductionTimelineItem[];
};

export type ProductionTimelineAsset = {
  asset_id: string;
  path: string;
  label?: string;
  sha256?: string;
};

export type ProductionTimelineProjectProfile = {
  fps: number;
  width: number;
  height: number;
  duration_frames: number;
  audio?: {
    audio_id: string;
    path: string;
    sha256?: string;
  };
};

export const defaultProductionTimelineProps: Required<
  Pick<ProductionTimelineCompositionProps, "width" | "height" | "fps" | "durationInFrames" | "items" | "assetMap">
> & Pick<ProductionTimelineCompositionProps, "schema_version" | "backgroundColor"> = {
  schema_version: "production_console_snapshot.v2",
  width: 1920,
  height: 1080,
  fps: 30,
  durationInFrames: 300,
  items: [],
  assetMap: {},
  backgroundColor: "#0b1015",
};

export type ProductionTimelineSequence = {
  readonly item: ProductionTimelineItem;
  readonly from: number;
  readonly durationInFrames: number;
  readonly premountFor: number;
};

const finite = (value: number | undefined, fallback: number): number =>
  typeof value === "number" && Number.isFinite(value) ? value : fallback;

const positiveInteger = (value: number | undefined, fallback: number): number =>
  Math.max(1, Math.round(finite(value, fallback)));

const clamp = (value: number, minimum: number, maximum: number): number =>
  Math.min(maximum, Math.max(minimum, value));

type ProductionTimelineRenderItemType = ProductionTimelineLegacyItemType | undefined;

const itemType = (item: ProductionTimelineItem): ProductionTimelineRenderItemType =>
  item.item_type ?? item.type;

const itemId = (item: ProductionTimelineItem): string => item.item_id ?? item.id ?? "timeline-item";

const itemFrom = (item: ProductionTimelineItem): number =>
  Math.max(0, Math.round(finite(item.start_frame, finite(item.from, 0))));

const itemDuration = (item: ProductionTimelineItem): number => {
  const rangeDuration = finite(item.end_frame, itemFrom(item)) - itemFrom(item);
  return positiveInteger(item.durationInFrames, rangeDuration);
};

const itemPremount = (item: ProductionTimelineItem, fps: number): number =>
  Math.max(1, Math.round(finite(item.premountFor, fps)));

export const buildProductionTimelineSequences = (
  items: readonly ProductionTimelineItem[],
  fps: number,
): ProductionTimelineSequence[] =>
  items.map((item) => ({
    item,
    from: itemFrom(item),
    durationInFrames: itemDuration(item),
    premountFor: itemPremount(item, positiveInteger(fps, 30)),
  }));

const timelineItems = (
  props: ProductionTimelineCompositionProps,
): readonly ProductionTimelineItem[] => {
  if (props.items) return props.items;
  if (props.timeline?.items) return props.timeline.items;
  return props.tracks?.flatMap((track) => track.items) ?? [];
};

const timelineAssetMap = (
  props: ProductionTimelineCompositionProps,
): Readonly<Record<string, string>> => {
  const records = [...(props.assets ?? []), ...(props.approved_assets ?? [])];
  const recordMap = Object.fromEntries(records.map((asset) => [asset.asset_id, asset.path]));
  const audio = props.project_profile?.audio;
  return {
    ...recordMap,
    ...(audio ? { [audio.audio_id]: audio.path } : {}),
    ...(props.asset_map ?? {}),
    ...(props.assetMap ?? {}),
  };
};

const resolveTimelineAsset = (
  item: ProductionTimelineItem,
  assetMap: Readonly<Record<string, string>>,
): string | undefined => {
  const assetId = item.assetId ?? item.asset_id;
  const source = assetId ?? (itemType(item) === "narration" ? item.source_ref : undefined);
  return normalizeRemotionBitAsset(source ? assetMap[source] ?? source : undefined);
};

const componentBitId = (
  componentId: ProductionTimelineComponentId | undefined,
): RemotionBitId | undefined => {
  if (!componentId) return undefined;
  if (componentId === "bit-ken-burns") return "ken-burns-effect";
  const withoutPrefix = componentId.startsWith("bit-") ? componentId.slice(4) : componentId;
  return REMOTION_BIT_IDS.includes(withoutPrefix as RemotionBitId)
    ? (withoutPrefix as RemotionBitId)
    : undefined;
};

const bitInput = (item: ProductionTimelineItem): RemotionBitInput | undefined => {
  if (item.bit) return item.bit;
  const bitId = item.bit_id ?? componentBitId(item.component_id ?? item.componentId);
  if (!bitId) return undefined;
  return {
    id: bitId,
    props: item.bit_props ?? item.props,
  } as RemotionBitInput;
};

const keyframeProgress = (
  progress: number,
  easing: ProductionTimelineKeyframe["easing"] = "smoothstep",
): number => {
  const t = clamp(progress, 0, 1);
  switch (easing) {
    case "linear":
      return t;
    case "ease_in":
      return t * t;
    case "ease_out":
      return 1 - (1 - t) * (1 - t);
    case "ease_in_out":
    case "smoothstep":
    default:
      return t * t * (3 - 2 * t);
  }
};

const interpolateProductionTimelineKeyframes = (
  keyframes: readonly ProductionTimelineKeyframe[] | undefined,
  frame: number,
): number | undefined => {
  if (!keyframes?.length) return undefined;
  const normalized = keyframes
    .filter((keyframe) => Number.isFinite(keyframe.frame) && Number.isFinite(keyframe.value))
    .map((keyframe) => ({...keyframe}))
    .sort((left, right) => left.frame - right.frame);
  if (!normalized.length) return undefined;
  if (normalized.length === 1 || frame <= normalized[0].frame) return normalized[0].value;
  const last = normalized[normalized.length - 1];
  if (frame >= last.frame) return last.value;
  for (let index = 0; index < normalized.length - 1; index += 1) {
    const left = normalized[index];
    const right = normalized[index + 1];
    if (frame <= right.frame) {
      const span = Math.max(1, right.frame - left.frame);
      const progress = keyframeProgress((frame - left.frame) / span, left.easing);
      return left.value + (right.value - left.value) * progress;
    }
  }
  return last.value;
};

export type ProductionTimelineAnimatedValues = Partial<
  Record<ProductionTimelineKeyframeProperty, number>
>;

/** Evaluate editor-authored absolute-frame keyframes for a sequence frame. */
export const evaluateProductionTimelineKeyframes = (
  item: ProductionTimelineItem,
  frame: number,
  sequenceFrom = itemFrom(item),
): ProductionTimelineAnimatedValues => {
  const values: ProductionTimelineAnimatedValues = {};
  const absoluteFrame = sequenceFrom + frame;
  for (const property of ["x", "y", "scaleX", "scaleY", "rotation", "opacity", "zIndex"] as const) {
    const value = interpolateProductionTimelineKeyframes(item.keyframes?.[property], absoluteFrame);
    if (value !== undefined) values[property] = value;
  }
  return values;
};

const EDITOR_CANVAS_WIDTH = 0.72;
const EDITOR_CANVAS_HEIGHT = 0.66;

/**
 * Build the same normalized, center-origin geometry used by EditorCanvasOverlay.
 * The editor's x/y values are offsets from canvas center, not top-left positions.
 */
export const buildProductionTimelineItemStyle = (
  item: ProductionTimelineItem,
  frame: number,
  fps: number,
  durationInFrames: number,
  sequenceFrom = itemFrom(item),
): React.CSSProperties => {
  const layout = item.layout;
  const transform = item.transform;
  const keyframes = evaluateProductionTimelineKeyframes(item, frame, sequenceFrom);
  const entranceFrames = Math.max(1, Math.min(Math.round(fps * 0.25), Math.floor(durationInFrames / 2)));
  const entrance = interpolate(frame, [0, entranceFrames], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const x = finite(keyframes.x, finite(transform?.x, finite(layout?.x, finite(item.x, 0))));
  const y = finite(keyframes.y, finite(transform?.y, finite(layout?.y, finite(item.y, 0))));
  const scale = finite(transform?.scale, finite(layout?.scale, finite(item.scale, 1)));
  const scaleX = finite(keyframes.scaleX, finite(transform?.scaleX, finite(layout?.scaleX, finite(item.scaleX, scale))));
  const scaleY = finite(keyframes.scaleY, finite(transform?.scaleY, finite(layout?.scaleY, finite(item.scaleY, scale))));
  const rotate = finite(
    keyframes.rotation,
    finite(transform?.rotation, finite(layout?.rotate, finite(layout?.rotation, finite(item.rotation, 0)))),
  );
  const cropWidth = finite(transform?.crop?.width, finite(layout?.width, 1));
  const cropHeight = finite(transform?.crop?.height, finite(layout?.height, 1));
  const opacity = clamp(
    finite(keyframes.opacity, finite(transform?.opacity, finite(layout?.opacity, finite(item.opacity, 1)))),
    0,
    1,
  );
  const zIndex = Math.round(
    finite(keyframes.zIndex, finite(transform?.zIndex, finite(transform?.z, finite(layout?.zIndex, finite(item.zIndex, finite(layout?.z, finite(item.z, 0))))))),
  );
  if (itemType(item) === "world_plate") {
    return {
      position: "absolute",
      left: `${50 + x * 100}%`,
      top: `${50 + y * 100}%`,
      width: "100%",
      height: "100%",
      transform: `translate(-50%, -50%) scaleX(${Math.max(0.001, scaleX)}) scaleY(${Math.max(0.001, scaleY)}) rotate(${rotate}deg)`,
      transformOrigin: "center center",
      opacity,
      zIndex,
      overflow: itemType(item) === "caption" ? "visible" : "hidden",
    };
  }
  return {
    position: "absolute",
    left: `${50 + x * 100}%`,
    top: `${50 + y * 100}%`,
    width: `${clamp(cropWidth, 0.001, 1) * EDITOR_CANVAS_WIDTH * 100}%`,
    height: `${clamp(cropHeight, 0.001, 1) * EDITOR_CANVAS_HEIGHT * 100}%`,
    transform: `translate(-50%, -50%) scaleX(${Math.max(0.001, scaleX)}) scaleY(${Math.max(0.001, scaleY)}) rotate(${rotate}deg)`,
    transformOrigin: "center center",
    opacity: itemType(item) === "evidence" ? opacity : opacity * entrance,
    zIndex,
    overflow: itemType(item) === "caption" ? "visible" : "hidden",
  };
};

const renderBitForItem = (
  item: ProductionTimelineItem,
  assetMap: Readonly<Record<string, string>>,
  durationInFrames: number,
): React.ReactElement | null => {
  const input = bitInput(item);
  if (!input) return null;
  const context: RemotionBitRenderContext = { assetMap };
  return renderRemotionBit(
    {
      id: input.id,
      props: {
        ...input.props,
        durationInFrames: input.props?.durationInFrames ?? durationInFrames,
      },
    } as RemotionBitInput,
    context,
  );
};

const textSurface = (
  text: string,
  color: string,
  fontSize: number,
  backgroundColor: string | undefined,
): React.ReactElement => (
  <div
    style={{
      width: "100%",
      height: "100%",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      padding: 28,
      boxSizing: "border-box",
      color,
      fontFamily: "Inter, Arial, sans-serif",
      fontSize,
      lineHeight: 1.12,
      textAlign: "center",
      backgroundColor,
    }}
  >
    {text}
  </div>
);

const captionSurface = (text: string, color: string, backgroundColor?: string): React.ReactElement => (
  <div
    style={{
      width: "100%",
      height: "100%",
      display: "flex",
      alignItems: "center",
      padding: "12px 18px",
      boxSizing: "border-box",
      color,
      fontFamily: "Inter, Arial, sans-serif",
      fontSize: 28,
      fontWeight: 650,
      lineHeight: 1.12,
      textAlign: "left",
      backgroundColor: backgroundColor ?? "rgba(7, 24, 34, .78)",
      borderLeft: "4px solid #d5a65b",
      borderRadius: 5,
    }}
  >
    {text}
  </div>
);

const EVIDENCE_REVEAL_ROWS = 6;

export const evidenceRevealGeometry = (frame: number, fps: number, durationInFrames: number) => {
  const revealFrames = Math.max(1, Math.min(durationInFrames - 1, Math.round(fps * 1.05)));
  const progress = interpolate(frame, [0, revealFrames], [0, 1], {extrapolateLeft: "clamp", extrapolateRight: "clamp"});
  const sweep = Math.min(EVIDENCE_REVEAL_ROWS - Number.EPSILON, progress * EVIDENCE_REVEAL_ROWS);
  const row = Math.min(EVIDENCE_REVEAL_ROWS - 1, Math.floor(sweep));
  const rowProgress = sweep - row;
  return {
    progress,
    row,
    rowProgress,
    handX: row % 2 === 0 ? rowProgress : 1 - rowProgress,
    handY: (row + .58) / EVIDENCE_REVEAL_ROWS,
    handVisible: progress > 0 && progress < .995,
  };
};

export const EvidenceRevealCard: React.FC<{
  item: ProductionTimelineItem;
  source?: string;
  handSource?: string;
  frame: number;
  fps: number;
  durationInFrames: number;
}> = ({item, source, handSource, frame, fps, durationInFrames}) => {
  const geometry = evidenceRevealGeometry(frame, fps, durationInFrames);
  // Crop the source non-destructively. The source itself remains hash-bound and
  // the bottom/right edge is retained so a teacher stamp is never clipped.
  const rawCrop = item.sourceCrop;
  const cropX = clamp(finite(rawCrop?.x, 0), 0, 0.99);
  const cropY = clamp(finite(rawCrop?.y, 0), 0, 0.99);
  const cropWidth = clamp(finite(rawCrop?.width, 1 - cropX), 0.01, 1 - cropX);
  const cropHeight = clamp(finite(rawCrop?.height, 1 - cropY), 0.01, 1 - cropY);
  const clipId = `evidence-reveal-${itemId(item).replace(/[^a-zA-Z0-9_-]/g, "-")}`;
  const rects = Array.from({length: EVIDENCE_REVEAL_ROWS}, (_, row) => {
    const completed = geometry.progress * EVIDENCE_REVEAL_ROWS - row;
    const rowProgress = clamp(completed, 0, 1);
    const x = row % 2 === 0 ? 0 : 1 - rowProgress;
    return <rect key={row} x={x} y={row / EVIDENCE_REVEAL_ROWS} width={rowProgress} height={1 / EVIDENCE_REVEAL_ROWS + .004} />;
  });
  return (
    <div style={{width: "100%", height: "100%", position: "relative", overflow: "hidden", backgroundColor: "#f7f3e9", border: "2px solid rgba(28,35,43,.74)", boxShadow: "0 8px 24px rgba(6,12,17,.28)"}}>
      <svg width="0" height="0" style={{position: "absolute"}} aria-hidden><defs><clipPath id={clipId} clipPathUnits="objectBoundingBox">{rects}</clipPath></defs></svg>
      {source ? <Img src={source} style={{position: "absolute", left: `${-(cropX / cropWidth) * 100}%`, top: `${-(cropY / cropHeight) * 100}%`, width: `${100 / cropWidth}%`, height: `${100 / cropHeight}%`, objectFit: "fill", clipPath: `url(#${clipId})`}} /> : null}
      {geometry.handVisible && handSource ? <Img src={handSource} style={{position: "absolute", left: `${geometry.handX * 100}%`, top: `${geometry.handY * 100}%`, width: "31%", height: "auto", transform: `translate(-50%, -82%) rotate(${geometry.row % 2 === 0 ? -7 : 7}deg)`, transformOrigin: "50% 90%", pointerEvents: "none", filter: "drop-shadow(0 4px 5px rgba(0,0,0,.24))"}} /> : null}
    </div>
  );
};

const renderTimelineItem = (
  item: ProductionTimelineItem,
  assetMap: Readonly<Record<string, string>>,
  durationInFrames: number,
  frame: number,
  fps: number,
  diagnosticMode: boolean,
): React.ReactElement | null => {
  const bit = renderBitForItem(item, assetMap, durationInFrames);
  if (bit) return bit;

  switch (itemType(item)) {
    case "scene":
      return (
        <div
          style={{
            width: "100%",
            height: "100%",
            display: "flex",
            flexDirection: "column",
            justifyContent: "flex-end",
            padding: 56,
            boxSizing: "border-box",
            color: "#f4f0e7",
            backgroundColor: item.backgroundColor ?? "#19222d",
            fontFamily: "Inter, Arial, sans-serif",
          }}
        >
          {item.title ? <div style={{ fontSize: 56, fontWeight: 800 }}>{item.title}</div> : null}
          {item.subtitle ? <div style={{ marginTop: 12, fontSize: 24, opacity: 0.78 }}>{item.subtitle}</div> : null}
        </div>
      );
    case "cue":
      return textSurface(
        item.excerpt ?? item.display_text ?? item.title ?? "",
        item.color ?? "#d9e7f4",
        item.fontSize ?? 28,
        item.backgroundColor ?? "rgba(25, 42, 58, 0.92)",
      );
    case "caption":
      if (item.caption_preset === "word_by_word" && item.word_tokens?.length) {
        return renderTranscriptCaption({
          tokens: item.word_tokens,
          color: item.color ?? "#ffffff",
          backgroundColor: item.backgroundColor,
          fontSize: item.fontSize ?? 28,
          style: {
            textShadow: "0 2px 10px rgba(3, 10, 16, .96), 0 0 2px rgba(3, 10, 16, .96)",
          },
        });
      }
      return captionSurface(item.text ?? item.excerpt ?? "", item.color ?? "#ffffff", item.backgroundColor);
    case "overlay":
    case "annotation": {
      const source = resolveTimelineAsset(item, assetMap);
      if (source) {
        return <Img src={source} style={{ width: "100%", height: "100%", objectFit: "contain" }} />;
      }
      const overlayKind = item.overlayKind ?? item.overlay_kind;
      if (overlayKind === "arrow") {
        const markerId = `arrow-${itemId(item).replace(/[^a-zA-Z0-9_-]/g, "-")}`;
        return (
          <svg viewBox="0 0 100 100" width="100%" height="100%" aria-label="Evidence leader line">
            <defs><marker id={markerId} markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L0,6 L7,3 z" fill="#f4efe2" /></marker></defs>
            <path d="M8 88 C 31 70, 55 45, 90 12" fill="none" stroke="#f4efe2" strokeWidth="4" strokeLinecap="round" markerEnd={`url(#${markerId})`} />
          </svg>
        );
      }
      if (overlayKind === "shape") {
        return <div style={{width: "100%", height: "100%", border: "4px solid #f4efe2", boxSizing: "border-box", borderRadius: 12}} />;
      }
      const copy = item.display_text;
      if (copy) {
        return textSurface(copy, item.color ?? "#ffffff", item.fontSize ?? 36, item.backgroundColor);
      }
      if (diagnosticMode) {
        return textSurface(
          item.diagnostic_label ?? item.citation_id ?? item.source_ref ?? itemId(item),
          "#f5c96a",
          22,
          "rgba(12,18,24,.82)",
        );
      }
      return null;
    }
    case "teacher_stamp": {
      const source = resolveTimelineAsset(item, assetMap);
      return source ? (
        <Img src={source} style={{ width: "100%", height: "100%", objectFit: "contain" }} />
      ) : (
        <div
          style={{
            width: "100%",
            height: "100%",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            color: item.status === "review_only" ? "#f4cf8b" : "#a7f3c0",
            fontFamily: "Inter, Arial, sans-serif",
            fontWeight: 800,
            fontSize: 22,
            letterSpacing: 1.4,
            textTransform: "uppercase",
          }}
        >
          {item.text ?? (item.status === "review_only" ? "Review only" : "Approved visual")}
        </div>
      );
    }
    case "evidence": {
      const source = resolveTimelineAsset(item, assetMap);
      const handSource = normalizeRemotionBitAsset(assetMap["whiteboard-draw-hand-a-v1"]);
      return <EvidenceRevealCard item={item} source={source} handSource={handSource} frame={frame} fps={fps} durationInFrames={durationInFrames} />;
    }
    case "world_plate": {
      const source = resolveTimelineAsset(item, assetMap);
      return source ? (
        <Img src={source} style={{ width: "100%", height: "100%", objectFit: item.layout?.fit ?? "cover" }} />
      ) : (
        <div style={{ width: "100%", height: "100%", backgroundColor: "#111827" }} />
      );
    }
    case "narration": {
      const source = resolveTimelineAsset(item, assetMap);
      return source ? <Audio src={source} volume={clamp(finite(item.volume, 1), 0, 1)} /> : null;
    }
    case "remotion_bit":
      return null;
    default:
      return null;
  }
};

const TimelineSequence: React.FC<{
  sequence: ProductionTimelineSequence;
  assetMap: Readonly<Record<string, string>>;
  fps: number;
  diagnosticMode: boolean;
}> = ({ sequence, assetMap, fps, diagnosticMode }) => {
  const { item } = sequence;
  return (
    <Sequence
      from={sequence.from}
      durationInFrames={sequence.durationInFrames}
      premountFor={sequence.premountFor}
    >
      <TimelineItemContent
        item={item}
        assetMap={assetMap}
        fps={fps}
        from={sequence.from}
        durationInFrames={sequence.durationInFrames}
        diagnosticMode={diagnosticMode}
      />
    </Sequence>
  );
};

const TimelineItemContent: React.FC<{
  item: ProductionTimelineItem;
  assetMap: Readonly<Record<string, string>>;
  fps: number;
  from: number;
  durationInFrames: number;
  diagnosticMode: boolean;
}> = ({ item, assetMap, fps, from, durationInFrames, diagnosticMode }) => {
  const frame = useCurrentFrame();
  const rendered = renderTimelineItem(item, assetMap, durationInFrames, frame, fps, diagnosticMode);
  if (!rendered) return null;
  return (
    <div
      style={buildProductionTimelineItemStyle(item, frame, fps, durationInFrames, from)}
      data-timeline-item-id={itemId(item)}
      data-timeline-item-type={itemType(item)}
    >
      <div style={{ width: "100%", height: "100%" }}>{rendered}</div>
    </div>
  );
};

export const calculateProductionTimelineMetadata: CalculateMetadataFunction<ProductionTimelineCompositionProps> = ({ props }) => {
  const profile = props.project_profile;
  const fps = positiveInteger(props.fps ?? profile?.fps, 30);
  const items = timelineItems(props);
  const sequences = buildProductionTimelineSequences(items, fps);
  const authoredDuration = positiveInteger(
    props.durationInFrames ?? props.duration_in_frames ?? profile?.duration_frames,
    1,
  );
  const contentDuration = sequences.reduce(
    (maximum, sequence) => Math.max(maximum, sequence.from + sequence.durationInFrames),
    1,
  );
  return {
    durationInFrames: Math.max(authoredDuration, contentDuration),
    fps,
    width: positiveInteger(props.width ?? profile?.width, 1920),
    height: positiveInteger(props.height ?? profile?.height, 1080),
  };
};

export const ProductionTimelineComposition: React.FC<ProductionTimelineCompositionProps> = (props) => {
  const { fps } = useVideoConfig();
  const assetMap = timelineAssetMap(props);
  const sequences = buildProductionTimelineSequences(timelineItems(props), fps);
  return (
    <AbsoluteFill style={{ backgroundColor: props.backgroundColor ?? "#0b1015", overflow: "hidden" }}>
      {sequences.map((sequence) => (
        <TimelineSequence
          key={itemId(sequence.item)}
          sequence={sequence}
          assetMap={assetMap}
          fps={fps}
          diagnosticMode={props.diagnosticMode === true}
        />
      ))}
    </AbsoluteFill>
  );
};
