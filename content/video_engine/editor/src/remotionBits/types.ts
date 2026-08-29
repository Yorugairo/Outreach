import type { ComponentType, CSSProperties } from "react";

/** JSON-safe styles intentionally limited to the properties used by the palette. */
export type RemotionBitStyle = Pick<
  CSSProperties,
  | "alignItems"
  | "backgroundColor"
  | "border"
  | "borderRadius"
  | "color"
  | "display"
  | "fontFamily"
  | "fontSize"
  | "fontWeight"
  | "gap"
  | "justifyContent"
  | "letterSpacing"
  | "lineHeight"
  | "padding"
  | "textAlign"
  | "textShadow"
  | "width"
  | "height"
  | "overflow"
>;

export type RemotionBitAssetMap = Readonly<Record<string, string>>;

export type RemotionBitCommonProps = {
  durationInFrames?: number;
  style?: RemotionBitStyle;
  color?: string;
  backgroundColor?: string;
  fontSize?: number;
};

export type TranscriptCaptionLineGroup = 1 | 2;

/**
 * The render-safe word timing contract.  A token is copied and frozen by the
 * canonical caption adapter before it reaches a Remotion frame renderer.
 */
export type TranscriptCaptionToken = Readonly<{
  text: string;
  startFrame: number;
  endFrame: number;
  lineGroup?: TranscriptCaptionLineGroup;
}>;

/** Snapshot-compatible input accepted by the protected caption conversion path. */
export type TranscriptCaptionTokenInput = {
  readonly text?: string;
  readonly word?: string;
  readonly w?: string;
  readonly startFrame?: number;
  readonly start_frame?: number;
  readonly endFrame?: number;
  readonly end_frame?: number;
  readonly lineGroup?: TranscriptCaptionLineGroup;
  readonly line_group?: TranscriptCaptionLineGroup;
  readonly line?: TranscriptCaptionLineGroup;
};

export type TranscriptCaptionLine = Readonly<{
  lineGroup: TranscriptCaptionLineGroup;
  tokens: readonly TranscriptCaptionToken[];
}>;

export type TranscriptCaptionProps = RemotionBitCommonProps & {
  readonly componentId?: "transcript_caption";
  readonly tokens: readonly (TranscriptCaptionToken | TranscriptCaptionTokenInput)[];
  readonly activeColor?: string;
};

/** Naming aliases used by callers that refer to the renderer as word-timed. */
export type CanonicalWordTimedCaptionToken = TranscriptCaptionToken;
export type WordTimedCaptionToken = TranscriptCaptionToken;
export type WordTimedCaptionProps = TranscriptCaptionProps;

export type FadeInProps = RemotionBitCommonProps & {
  text?: string;
};

export type BlurInProps = RemotionBitCommonProps & {
  text?: string;
  blurAmount?: number;
};

export type WordByWordProps = RemotionBitCommonProps & {
  text?: string;
  staggerFrames?: number;
};

export type SlideFromLeftProps = RemotionBitCommonProps & {
  text?: string;
  distance?: number;
};

export type BasicTypewriterProps = RemotionBitCommonProps & {
  text?: string;
  typeSpeedFrames?: number;
  showCursor?: boolean;
};

export type BasicCounterProps = RemotionBitCommonProps & {
  from?: number;
  to?: number;
  prefix?: string;
  postfix?: string;
  decimals?: number;
};

export type ListRevealProps = RemotionBitCommonProps & {
  items?: readonly string[];
  staggerFrames?: number;
};

export type GridStaggerProps = RemotionBitCommonProps & {
  items?: readonly string[];
  columns?: number;
  staggerFrames?: number;
};

export type MosaicReframeProps = RemotionBitCommonProps & {
  images?: readonly string[];
  assetMap?: RemotionBitAssetMap;
  tileCount?: number;
};

export type CardStackProps = RemotionBitCommonProps & {
  cards?: readonly string[];
  staggerFrames?: number;
};

export type KenBurnsProps = RemotionBitCommonProps & {
  images?: readonly string[];
  assetMap?: RemotionBitAssetMap;
  /** Absolute composition frame at which this local reframe begins. */
  startFrame?: number;
  scaleFrom?: number;
  scaleTo?: number;
  direction?: "left" | "right" | "up" | "down";
};

export type RemotionBitPropsById = {
  "fade-in": FadeInProps;
  "blur-in": BlurInProps;
  "word-by-word": WordByWordProps;
  "slide-from-left": SlideFromLeftProps;
  "basic-typewriter": BasicTypewriterProps;
  "basic-counter": BasicCounterProps;
  "list-reveal": ListRevealProps;
  "grid-stagger": GridStaggerProps;
  "mosaic-reframe": MosaicReframeProps;
  "3d-card-stack": CardStackProps;
  "ken-burns-effect": KenBurnsProps;
};

export type RemotionBitId = keyof RemotionBitPropsById;

/** Union of the JSON-safe prop bags accepted by the closed bit registry. */
export type RemotionBitProps = {
  [K in RemotionBitId]: Partial<RemotionBitPropsById[K]>;
}[RemotionBitId];

export type RemotionBitRenderContext = {
  assetMap?: RemotionBitAssetMap;
};

/** A discriminated bit request suitable for JSON timeline props. */
export type RemotionBitInput = {
  [K in RemotionBitId]: {
    id: K;
    props?: Partial<RemotionBitPropsById[K]>;
  };
}[RemotionBitId];

export type RemotionBitDefinition<K extends RemotionBitId> = {
  readonly id: K;
  readonly name: string;
  readonly packageVersion: "0.2.0";
  readonly component: ComponentType<RemotionBitPropsById[K]>;
  readonly defaultProps: RemotionBitPropsById[K];
};

export type RemotionBitRegistry = {
  readonly [K in RemotionBitId]: RemotionBitDefinition<K>;
};
