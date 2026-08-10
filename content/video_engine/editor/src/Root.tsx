import React from "react";
import {
  Composition,
  type CalculateMetadataFunction,
} from "remotion";
import { EditorialComposition } from "./Editorial";
import { DocumentaryComposition, DocumentaryMotionComposition } from "./Documentary";
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
  calculateFinance2DStickMetadata,
  defaultFinance2DStickProps,
  Finance2DStickProof,
} from "./Finance2DStickProof";
import {
  calculateEditorialMotionMetadata,
  defaultEditorialMotionProps,
} from "./EditorialMotion";
import type { DocumentaryProps, EditManifest, EditorialProps } from "./types";

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

const defaultDocumentaryTreatment = {
  schema_version: "visual_treatment.v2" as const,
  source_kind: "documentary" as const,
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
      function: "chapter_cta" as const,
      visual_type: "chapter_cta" as const,
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

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="Editorial"
        component={EditorialComposition}
        durationInFrames={1}
        fps={60}
        width={1920}
        height={1080}
        defaultProps={{ manifest: defaultManifest }}
        calculateMetadata={calculateMetadata}
      />
      <Composition
        id="Documentary"
        component={DocumentaryComposition}
        durationInFrames={60}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{ treatment: defaultDocumentaryTreatment }}
        calculateMetadata={calculateDocumentaryMetadata}
      />
      <Composition
        id="EditorialMotion"
        component={DocumentaryMotionComposition}
        durationInFrames={60}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={defaultEditorialMotionProps}
        calculateMetadata={calculateEditorialMotionMetadata}
      />
      <Composition
        id="FinanceSketchbookProof"
        component={FinanceSketchbookProof}
        durationInFrames={1458}
        fps={24}
        width={1920}
        height={1080}
        defaultProps={defaultFinanceSketchbookProps}
        calculateMetadata={calculateFinanceSketchbookMetadata}
      />
      <Composition
        id="FinanceStealthWealthProof"
        component={FinanceStealthWealthProof}
        durationInFrames={2520}
        fps={24}
        width={1920}
        height={1080}
        defaultProps={defaultFinanceStealthWealthProps}
        calculateMetadata={calculateFinanceStealthWealthMetadata}
      />
      <Composition
        id="Finance2DStickProof"
        component={Finance2DStickProof}
        durationInFrames={1458}
        fps={24}
        width={1920}
        height={1080}
        defaultProps={defaultFinance2DStickProps}
        calculateMetadata={calculateFinance2DStickMetadata}
      />
    </>
  );
};
