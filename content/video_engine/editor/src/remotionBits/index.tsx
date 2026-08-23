import React from "react";
import {
  BasicCounterAdapter,
  BasicTypewriterAdapter,
  BlurInAdapter,
  CardStackAdapter,
  FadeInAdapter,
  GridStaggerAdapter,
  KenBurnsAdapter,
  ListRevealAdapter,
  MosaicReframeAdapter,
  SlideFromLeftAdapter,
  WordByWordAdapter,
} from "./adapters";
import type {
  RemotionBitDefinition,
  RemotionBitId,
  RemotionBitInput,
  RemotionBitPropsById,
  RemotionBitRegistry,
  RemotionBitRenderContext,
} from "./types";

export * from "./adapters";
export * from "./types";
export * from "./wordTimedCaption";

export const REMOTION_BIT_IDS = [
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
] as const satisfies readonly RemotionBitId[];

export const REMOTION_BIT_NAMES: { readonly [K in RemotionBitId]: string } = {
  "fade-in": "Fade In",
  "blur-in": "Blur In",
  "word-by-word": "Word by Word",
  "slide-from-left": "Slide from Left",
  "basic-typewriter": "Basic Typewriter",
  "basic-counter": "Basic Counter",
  "list-reveal": "List Reveal",
  "grid-stagger": "Grid Stagger",
  "mosaic-reframe": "Mosaic Reframe",
  "3d-card-stack": "3D Card Stack",
  "ken-burns-effect": "Ken Burns Effect",
};

export const REMOTION_BITS_REGISTRY = {
  "fade-in": {
    id: "fade-in",
    name: REMOTION_BIT_NAMES["fade-in"],
    packageVersion: "0.2.0",
    component: FadeInAdapter,
    defaultProps: { text: "Fade In" },
  },
  "blur-in": {
    id: "blur-in",
    name: REMOTION_BIT_NAMES["blur-in"],
    packageVersion: "0.2.0",
    component: BlurInAdapter,
    defaultProps: { text: "Blur In" },
  },
  "word-by-word": {
    id: "word-by-word",
    name: REMOTION_BIT_NAMES["word-by-word"],
    packageVersion: "0.2.0",
    component: WordByWordAdapter,
    defaultProps: { text: "Word by Word" },
  },
  "slide-from-left": {
    id: "slide-from-left",
    name: REMOTION_BIT_NAMES["slide-from-left"],
    packageVersion: "0.2.0",
    component: SlideFromLeftAdapter,
    defaultProps: { text: "Slide from Left" },
  },
  "basic-typewriter": {
    id: "basic-typewriter",
    name: REMOTION_BIT_NAMES["basic-typewriter"],
    packageVersion: "0.2.0",
    component: BasicTypewriterAdapter,
    defaultProps: { text: "Basic Typewriter" },
  },
  "basic-counter": {
    id: "basic-counter",
    name: REMOTION_BIT_NAMES["basic-counter"],
    packageVersion: "0.2.0",
    component: BasicCounterAdapter,
    defaultProps: { from: 0, to: 100 },
  },
  "list-reveal": {
    id: "list-reveal",
    name: REMOTION_BIT_NAMES["list-reveal"],
    packageVersion: "0.2.0",
    component: ListRevealAdapter,
    defaultProps: { items: ["Evidence", "Context", "Decision"] },
  },
  "grid-stagger": {
    id: "grid-stagger",
    name: REMOTION_BIT_NAMES["grid-stagger"],
    packageVersion: "0.2.0",
    component: GridStaggerAdapter,
    defaultProps: { items: ["01", "02", "03", "04", "05", "06", "07", "08", "09"] },
  },
  "mosaic-reframe": {
    id: "mosaic-reframe",
    name: REMOTION_BIT_NAMES["mosaic-reframe"],
    packageVersion: "0.2.0",
    component: MosaicReframeAdapter,
    defaultProps: { tileCount: 12 },
  },
  "3d-card-stack": {
    id: "3d-card-stack",
    name: REMOTION_BIT_NAMES["3d-card-stack"],
    packageVersion: "0.2.0",
    component: CardStackAdapter,
    defaultProps: { cards: ["A", "B", "C", "D", "E"] },
  },
  "ken-burns-effect": {
    id: "ken-burns-effect",
    name: REMOTION_BIT_NAMES["ken-burns-effect"],
    packageVersion: "0.2.0",
    component: KenBurnsAdapter,
    defaultProps: {},
  },
} as const satisfies RemotionBitRegistry;

export const CURATED_REMOTION_BITS = REMOTION_BIT_IDS.map(
  (id) => REMOTION_BITS_REGISTRY[id],
) as readonly RemotionBitDefinition<RemotionBitId>[];

export const REMOTION_BIT_REGISTRY = REMOTION_BITS_REGISTRY;
export const REMOTION_BITS_CATALOG = CURATED_REMOTION_BITS;

const withContext = <K extends RemotionBitId>(
  id: K,
  props: Partial<RemotionBitPropsById[K]> | undefined,
  context: RemotionBitRenderContext | undefined,
): RemotionBitPropsById[K] => {
  const merged = {
    ...REMOTION_BITS_REGISTRY[id].defaultProps,
    ...props,
  } as RemotionBitPropsById[K];
  if (context?.assetMap && (id === "mosaic-reframe" || id === "ken-burns-effect")) {
    return { ...merged, assetMap: context.assetMap } as RemotionBitPropsById[K];
  }
  return merged;
};

const renderById = <K extends RemotionBitId>(
  id: K,
  props: Partial<RemotionBitPropsById[K]> | undefined,
  context: RemotionBitRenderContext | undefined,
): React.ReactElement => {
  const resolved = withContext(id, props, context);
  switch (id) {
    case "fade-in":
      return <FadeInAdapter {...resolved} />;
    case "blur-in":
      return <BlurInAdapter {...resolved} />;
    case "word-by-word":
      return <WordByWordAdapter {...resolved} />;
    case "slide-from-left":
      return <SlideFromLeftAdapter {...resolved} />;
    case "basic-typewriter":
      return <BasicTypewriterAdapter {...resolved} />;
    case "basic-counter":
      return <BasicCounterAdapter {...resolved} />;
    case "list-reveal":
      return <ListRevealAdapter {...resolved} />;
    case "grid-stagger":
      return <GridStaggerAdapter {...resolved} />;
    case "mosaic-reframe":
      return <MosaicReframeAdapter {...resolved} />;
    case "3d-card-stack":
      return <CardStackAdapter {...resolved} />;
    case "ken-burns-effect":
      return <KenBurnsAdapter {...resolved} />;
    default:
      return assertNever(id);
  }
};

const assertNever = (value: never): never => {
  throw new Error(`Unknown curated Remotion Bit: ${String(value)}`);
};

export function renderRemotionBit(
  input: RemotionBitInput,
  context?: RemotionBitRenderContext,
): React.ReactElement;
export function renderRemotionBit<K extends RemotionBitId>(
  id: K,
  props?: Partial<RemotionBitPropsById[K]>,
  context?: RemotionBitRenderContext,
): React.ReactElement;
export function renderRemotionBit(
  inputOrId: RemotionBitInput | RemotionBitId,
  propsOrContext?: Partial<RemotionBitPropsById[RemotionBitId]> | RemotionBitRenderContext,
  context?: RemotionBitRenderContext,
): React.ReactElement {
  if (typeof inputOrId === "string") {
    return renderById(
      inputOrId,
      propsOrContext && "assetMap" in propsOrContext ? undefined : propsOrContext,
      context ?? (propsOrContext && "assetMap" in propsOrContext ? propsOrContext : undefined),
    );
  }
  return renderById(inputOrId.id, inputOrId.props, propsOrContext as RemotionBitRenderContext | undefined);
}
