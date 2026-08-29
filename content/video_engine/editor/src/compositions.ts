import type { ComponentType } from "react";
import type { CalculateMetadataFunction } from "remotion";
import {
  DocumentaryComposition,
  DocumentaryMotionComposition,
} from "./Documentary";
import { EditorialComposition } from "./Editorial";
import { EvidenceCarousel3D, LongPlateOrbit } from "./Evidence3DProto";
import {
  calculateFinance2DStickMetadata,
  defaultFinance2DStickProps,
  Finance2DStickProof,
} from "./Finance2DStickProof";
import {
  calculateFinanceSketchbookMetadata,
  defaultFinanceSketchbookProps,
  FinanceSketchbookProof,
} from "./FinanceSketchbookProof";
import {
  calculateFinanceStealthWealthMetadata,
  defaultFinanceStealthWealthProps,
  FinanceStealthWealthProof,
} from "./FinanceStealthWealthProof";
import {
  calculateEditorialMotionMetadata,
  defaultEditorialMotionProps,
  EditorialMotionComposition,
} from "./EditorialMotion";
import {
  defaultProductionEvidenceProps,
  ProductionEvidenceComposition,
  type ProductionEvidenceCompositionProps,
} from "./ProductionEvidenceComposition";
import {
  calculateProductionTimelineMetadata,
  defaultProductionTimelineProps,
  ProductionTimelineComposition,
  type ProductionTimelineCompositionProps,
} from "./ProductionTimelineComposition";
import {
  defaultKenBurnsEffectProofProps,
  KenBurnsEffectProof,
  type KenBurnsEffectProofProps,
} from "./KenBurnsEffectProof";
import {
  defaultTransitionEvidence60sProofProps,
  TransitionEvidence60sProof,
  type TransitionEvidence60sProofProps,
} from "./TransitionEvidence60sProof";
import {
  calculateAutopilotElevenLabsRecutMetadata,
  defaultAutopilotElevenLabsRecutProps,
  AutopilotElevenLabsRecut,
  type AutopilotElevenLabsRecutProps,
} from "./AutopilotElevenLabsRecut";
import type {
  DocumentaryProps,
  DocumentaryTreatment,
  EditManifest,
  EditorialMotionProps,
  EditorialProps,
  Finance2DStickProofProps,
  FinanceSketchbookProofProps,
  FinanceStealthWealthProofProps,
} from "./types";

/** The editor, Player, and renderer must stay on this exact Remotion release. */
export const REMOTION_VERSION = "4.0.502" as const;

export type CompositionFolder = "Editorial" | "Documentary" | "Finance" | "Console" | "Autopilot";

export type CompositionMetadata<Props extends Record<string, unknown>> = {
  readonly durationInFrames: number;
  readonly fps: number;
  readonly width: number;
  readonly height: number;
  readonly calculateMetadata: CalculateMetadataFunction<Props>;
};

/**
 * Browser-safe composition contract shared by the Remotion root and future
 * Player/renderer consumers. Props remain plain JSON; executable behavior is
 * limited to the imported React component and metadata callback.
 */
export type CompositionDefinition<Props extends Record<string, unknown>> = {
  readonly id: string;
  readonly folder: CompositionFolder;
  readonly component: ComponentType<Props>;
  readonly defaultProps: Props;
  readonly metadata: CompositionMetadata<Props>;
};

type RegistryDefinition<
  Id extends string,
  Folder extends CompositionFolder,
  Props extends Record<string, unknown>,
> = CompositionDefinition<Props> & {
  readonly id: Id;
  readonly folder: Folder;
};

export type CompositionRegistryEntry =
  | RegistryDefinition<"Editorial", "Editorial", EditorialProps>
  | RegistryDefinition<"Documentary", "Documentary", DocumentaryProps>
  | RegistryDefinition<"EditorialMotion", "Editorial", EditorialMotionProps>
  | RegistryDefinition<"FinanceSketchbookProof", "Finance", FinanceSketchbookProofProps>
  | RegistryDefinition<"FinanceStealthWealthProof", "Finance", FinanceStealthWealthProofProps>
  | RegistryDefinition<"Finance2DStickProof", "Finance", Finance2DStickProofProps>
  | RegistryDefinition<"ProductionEvidence", "Console", ProductionEvidenceCompositionProps>
  | RegistryDefinition<"ProductionTimeline", "Console", ProductionTimelineCompositionProps>
  | RegistryDefinition<"KenBurnsEffectProof", "Console", KenBurnsEffectProofProps>
  | RegistryDefinition<"TransitionEvidence60sProof", "Console", TransitionEvidence60sProofProps>
  | RegistryDefinition<"AutopilotElevenLabsRecut", "Autopilot", AutopilotElevenLabsRecutProps>;

const defaultManifest: EditManifest = {
  schema_version: "edit_manifest.v1",
  aspect: "landscape",
  fps: 60,
  width: 1920,
  height: 1080,
  duration_in_frames: 1,
  clips: [],
  captions: [],
  overlays: [],
};

const defaultDocumentaryTreatment: DocumentaryTreatment = {
  schema_version: "visual_treatment.v2",
  source_kind: "documentary",
  art_bible_id: "combat-history-longform-cutout-fork-v1",
  art_bible_hash: "0".repeat(64),
  shot_plan_hash: "0".repeat(64),
  research_hash: "0".repeat(64),
  asset_manifest_hash: "0".repeat(64),
  episode_id: "history-of-bjj",
  duration_s: 2,
  shots: [
    {
      shot_id: "chapter-cta",
      treatment_id: "treatment-chapter-cta",
      function: "chapter_cta",
      visual_type: "chapter_cta",
      purpose: "History of BJJ",
      duration_s: 2,
      asset_ids: [],
      citations: [],
    },
  ],
};

export const calculateMetadata: CalculateMetadataFunction<EditorialProps> = ({ props }) => {
  // Remotion merges CLI input props with defaultProps. A raw edit manifest
  // therefore still contains the default `manifest` wrapper; prefer the raw
  // contract whenever its discriminator is present.
  const manifest = "schema_version" in props ? props : props.manifest;
  const profile = manifest.aspect === "vertical"
    ? { width: 1080, height: 1920, fps: 30 }
    : { width: 1920, height: 1080, fps: 60 };
  return {
    durationInFrames: Math.max(1, Math.round(manifest.duration_in_frames)),
    width: Math.max(1, Math.round(manifest.width || profile.width)),
    height: Math.max(1, Math.round(manifest.height || profile.height)),
    fps: Math.max(1, Math.round(manifest.fps || profile.fps)),
  };
};

export const calculateDocumentaryMetadata: CalculateMetadataFunction<DocumentaryProps> = ({ props }) => {
  const treatment = "schema_version" in props ? props : props.treatment;
  return {
    durationInFrames: Math.max(1, Math.round(treatment.duration_s * 30)),
    width: 1920,
    height: 1080,
    fps: 30,
  };
};

/**
 * The sole source of truth for editor compositions. Keep entries ordered for
 * stable CLI output and place only JSON-serializable props in defaultProps.
 */
export const COMPOSITION_REGISTRY = [
  {
    id: "Editorial",
    folder: "Editorial",
    component: EditorialComposition,
    defaultProps: { manifest: defaultManifest },
    metadata: {
      durationInFrames: 1,
      fps: 60,
      width: 1920,
      height: 1080,
      calculateMetadata,
    },
  },
  {
    id: "Documentary",
    folder: "Documentary",
    component: DocumentaryComposition,
    defaultProps: { treatment: defaultDocumentaryTreatment },
    metadata: {
      durationInFrames: 60,
      fps: 30,
      width: 1920,
      height: 1080,
      calculateMetadata: calculateDocumentaryMetadata,
    },
  },
  {
    id: "EditorialMotion",
    folder: "Editorial",
    component: EditorialMotionComposition,
    defaultProps: defaultEditorialMotionProps,
    metadata: {
      durationInFrames: 60,
      fps: 30,
      width: 1920,
      height: 1080,
      calculateMetadata: calculateEditorialMotionMetadata,
    },
  },
  {
    id: "FinanceSketchbookProof",
    folder: "Finance",
    component: FinanceSketchbookProof,
    defaultProps: defaultFinanceSketchbookProps,
    metadata: {
      durationInFrames: 1458,
      fps: 24,
      width: 1920,
      height: 1080,
      calculateMetadata: calculateFinanceSketchbookMetadata,
    },
  },
  {
    id: "FinanceStealthWealthProof",
    folder: "Finance",
    component: FinanceStealthWealthProof,
    defaultProps: defaultFinanceStealthWealthProps,
    metadata: {
      durationInFrames: 2520,
      fps: 24,
      width: 1920,
      height: 1080,
      calculateMetadata: calculateFinanceStealthWealthMetadata,
    },
  },
  {
    id: "Finance2DStickProof",
    folder: "Finance",
    component: Finance2DStickProof,
    defaultProps: defaultFinance2DStickProps,
    metadata: {
      durationInFrames: 1458,
      fps: 24,
      width: 1920,
      height: 1080,
      calculateMetadata: calculateFinance2DStickMetadata,
    },
  },
  {
    id: "ProductionEvidence",
    folder: "Console",
    component: ProductionEvidenceComposition,
    defaultProps: defaultProductionEvidenceProps,
    metadata: {
      durationInFrames: 240,
      fps: 30,
      width: 1376,
      height: 768,
      calculateMetadata: () => ({ durationInFrames: 240, fps: 30, width: 1376, height: 768 }),
    },
  },
  {
    id: "ProductionTimeline",
    folder: "Console",
    component: ProductionTimelineComposition,
    defaultProps: defaultProductionTimelineProps,
    metadata: {
      durationInFrames: 300,
      fps: 30,
      width: 1920,
      height: 1080,
      calculateMetadata: calculateProductionTimelineMetadata,
    },
  },
  {
    id: "KenBurnsEffectProof",
    folder: "Console",
    component: KenBurnsEffectProof,
    defaultProps: defaultKenBurnsEffectProofProps,
    metadata: {
      durationInFrames: 360,
      fps: 30,
      width: 1920,
      height: 1080,
      calculateMetadata: () => ({ durationInFrames: 360, fps: 30, width: 1920, height: 1080 }),
    },
  },
  {
    id: "TransitionEvidence60sProof",
    folder: "Console",
    component: TransitionEvidence60sProof,
    defaultProps: defaultTransitionEvidence60sProofProps,
    metadata: {
      durationInFrames: 1800,
      fps: 30,
      width: 1920,
      height: 1080,
      calculateMetadata: calculateProductionTimelineMetadata,
    },
  },
  {
    id: "AutopilotElevenLabsRecut",
    folder: "Autopilot",
    component: AutopilotElevenLabsRecut,
    defaultProps: defaultAutopilotElevenLabsRecutProps,
    metadata: {
      durationInFrames: 1,
      fps: 24,
      width: 1920,
      height: 1080,
      calculateMetadata: calculateAutopilotElevenLabsRecutMetadata,
    },
  },
  {
    id: "DocumentaryMotion",
    folder: "Documentary",
    component: DocumentaryMotionComposition,
    defaultProps: defaultEditorialMotionProps,
    metadata: {
      durationInFrames: 60,
      fps: 30,
      width: 1920,
      height: 1080,
      calculateMetadata: calculateEditorialMotionMetadata,
    },
  },
  {
    id: "EvidenceCarousel3D",
    folder: "Prototypes",
    component: EvidenceCarousel3D,
    defaultProps: {},
    metadata: { durationInFrames: 300, fps: 30, width: 1920, height: 1080 },
  },
  {
    id: "LongPlateOrbit",
    folder: "Prototypes",
    component: LongPlateOrbit,
    defaultProps: {},
    metadata: { durationInFrames: 300, fps: 30, width: 1920, height: 1080 },
  },
] as const satisfies readonly CompositionRegistryEntry[];

export type CompositionId = (typeof COMPOSITION_REGISTRY)[number]["id"];
