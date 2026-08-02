import React from "react";
import {
  Img,
  Sequence,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { EditorialMotionComposition } from "./EditorialMotion";
import type {
  DocumentaryFunction,
  DocumentaryCharacterLayer,
  DocumentaryProps,
  DocumentaryShot,
  DocumentaryTreatment,
  DocumentaryVisualBeat,
  EditorialMotionProps,
  MotionRecipe,
} from "./types";

const COLORS = {
  paper: "#F4EBDD",
  ink: "#1F252A",
  background: "#171B20",
  surface: "#2B3136",
  rust: "#A44A32",
  indigo: "#324C73",
  jade: "#2C7666",
  ochre: "#C18B45",
  muted: "#A7A092",
};

const SAFE_TEXT: React.CSSProperties = {
  fontFamily: "Inter, Arial, sans-serif",
  color: COLORS.ink,
  lineHeight: 1.18,
};

const unwrapTreatment = (props: DocumentaryProps): DocumentaryTreatment => {
  return "schema_version" in props ? props : props.treatment;
};

const assetMapFor = (props: DocumentaryProps): Record<string, string> => {
  return "asset_map" in props && props.asset_map ? props.asset_map : {};
};

/** Resolve only a local editor/public asset. Remote URLs and file paths fail closed. */
export const resolveDocumentaryAsset = (
  assetId: string | undefined,
  assetMap: Record<string, string>,
): string | undefined => {
  if (!assetId) return undefined;
  const source = assetMap[assetId];
  if (!source) return undefined;
  const normalized = source.replaceAll("\\", "/").replace(/^public\//i, "");
  if (
    /^(?:https?:|data:|blob:|file:)/i.test(normalized) ||
    normalized.startsWith("/") ||
    /^[A-Za-z]:\//.test(normalized) ||
    normalized.split("/").includes("..")
  ) {
    return undefined;
  }
  return staticFile(normalized);
};

const firstAsset = (
  shot: DocumentaryShot,
  assetMap: Record<string, string>,
  beat?: DocumentaryVisualBeat,
): string | undefined =>
  resolveDocumentaryAsset(beat?.asset_ids?.[0] || shot.asset_ids?.[0], assetMap);

const shotTitle = (shot: DocumentaryShot): string => {
  return shot.purpose || shot.function.replaceAll("_", " ").replace(/^./, (value) => value.toUpperCase());
};

const CitationRail: React.FC<{ shot: DocumentaryShot }> = ({ shot }) => {
  const citations = shot.citations || [];
  if (!citations.length) return null;
  const labels = citations.map((citation) =>
    typeof citation === "string" ? citation : citation.label || citation.citation_id,
  );
  return (
    <div
      style={{
        position: "absolute",
        left: "8%",
        right: "8%",
        bottom: "7%",
        color: COLORS.indigo,
        fontFamily: "Roboto Mono, monospace",
        fontSize: 22,
        textAlign: "left",
        letterSpacing: 0.2,
      }}
    >
      {labels.join("  ·  ")}
    </div>
  );
};

const motionTransform = (
  recipe: MotionRecipe | undefined,
  progress: number,
): string => {
  switch (recipe) {
    case "detail_punch":
      return `scale(${1 + Math.min(1, progress * 2.4) * 0.09})`;
    case "masked_reveal":
      return `translateX(${(1 - progress) * -7}%) scale(1.04)`;
    case "map_trace":
    case "split_compare":
      return `translateX(${(1 - progress) * 5}%) scale(1.03)`;
    case "comic_pop":
      return `scale(${0.9 + Math.min(1, progress * 3) * 0.1}) rotate(${(1 - progress) * -1.2}deg)`;
    case "type_build":
      return `translateY(${(1 - progress) * 4}%)`;
    case "paper_transition":
      return `translateX(${(1 - progress) * -4}%) rotate(${(1 - progress) * -0.5}deg)`;
    case "evidence_highlight":
      return `scale(${1.04 - progress * 0.04})`;
    case "parallax_push":
      return `scale(${1 + progress * 0.04})`;
    default:
      // A legacy shot without an explicit visual beat stays locked.  The
      // editorial-motion plan owns camera movement; never invent a whole-plate
      // zoom as a fallback for missing motion metadata.
      return "none";
  }
};

const LocalAsset: React.FC<{ shot: DocumentaryShot; assetMap: Record<string, string>; beat?: DocumentaryVisualBeat }> = ({
  shot,
  assetMap,
  beat,
}) => {
  const frame = useCurrentFrame();
  const src = firstAsset(shot, assetMap, beat);
  if (!src) return null;
  const progress = interpolate(frame, [0, 90], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const isArchive = shot.function === "archival_portrait" || shot.function === "artifact_cold_open";
  return (
    <Img
      src={src}
      style={{
        position: "absolute",
        left: "10%",
        top: "26%",
        width: "80%",
        height: "54%",
        objectFit: "contain",
        opacity: isArchive ? 0.92 : 1,
        transform: motionTransform(beat?.motion_recipe, progress),
        filter: isArchive ? "sepia(0.24) saturate(0.76)" : "none",
      }}
    />
  );
};

const characterMotionTransform = (
  motion: DocumentaryCharacterLayer["motion"],
  progress: number,
): string => {
  const eased = progress * progress * (3 - 2 * progress);
  switch (motion) {
    case "enter_from_left":
      return `translateX(${(1 - eased) * -120}%) scale(${0.96 + eased * 0.04})`;
    case "enter_from_right":
      return `translateX(${(1 - eased) * 120}%) scale(${0.96 + eased * 0.04})`;
    case "rise":
      return `translateY(${(1 - eased) * 90}%) scale(${0.98 + eased * 0.02})`;
    case "pop":
      return `scale(${0.82 + eased * 0.18}) rotate(${(1 - eased) * -1.4}deg)`;
    case "float":
      return `translateY(${Math.sin(progress * Math.PI * 2) * 1.5}px)`;
    case "settle":
    default:
      return `translateY(${(1 - eased) * -18}px)`;
  }
};

const CharacterLayerView: React.FC<{
  layer: DocumentaryCharacterLayer;
  assetMap: Record<string, string>;
}> = ({ layer, assetMap }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const src = resolveDocumentaryAsset(layer.asset_id, assetMap);
  if (!src) return null;
  const duration = Math.max(1, Math.round(layer.duration_s * fps));
  const introFrames = Math.min(Math.round(fps * 0.8), Math.max(1, Math.floor(duration / 2)));
  const progress = interpolate(frame, [0, introFrames], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const fadeOutFrames = Math.min(Math.round(fps * 0.35), Math.max(1, Math.floor(duration / 3)));
  const opacity = interpolate(
    frame,
    [0, Math.min(6, introFrames), Math.max(introFrames, duration - fadeOutFrames), duration],
    [0, 1, 1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );
  return (
    <div
      style={{
        position: "absolute",
        left: `${layer.x}%`,
        top: `${layer.y}%`,
        width: `${layer.width}%`,
        height: `${layer.height}%`,
        zIndex: layer.z_index ?? 3,
        opacity,
        transform: characterMotionTransform(layer.motion, progress),
        transformOrigin: "center bottom",
        background: `${COLORS.paper}F2`,
        border: `4px solid ${COLORS.ink}`,
        boxShadow: `10px 10px 0 ${COLORS.rust}`,
        overflow: "hidden",
      }}
    >
      <Img src={src} style={{ width: "100%", height: "100%", objectFit: "contain" }} />
      {layer.label ? (
        <div
          style={{
            position: "absolute",
            left: 12,
            bottom: 10,
            padding: "5px 9px",
            background: COLORS.ink,
            color: COLORS.paper,
            fontFamily: "Roboto Mono, monospace",
            fontSize: 18,
            letterSpacing: 0.6,
          }}
        >
          {layer.label}
        </div>
      ) : null}
    </div>
  );
};

const CharacterLayers: React.FC<{
  layers: DocumentaryCharacterLayer[];
  assetMap: Record<string, string>;
}> = ({ layers, assetMap }) => {
  const { fps } = useVideoConfig();
  return (
    <>
      {layers.map((layer) => {
        const from = Math.max(0, Math.round(layer.from_s * fps));
        const duration = Math.max(1, Math.round(layer.duration_s * fps));
        return (
          <Sequence key={layer.id} from={from} durationInFrames={duration} premountFor={Math.min(fps, from)}>
            <CharacterLayerView layer={layer} assetMap={assetMap} />
          </Sequence>
        );
      })}
    </>
  );
};

const VectorTreatment: React.FC<{ functionName: DocumentaryFunction }> = ({ functionName }) => {
  const frame = useCurrentFrame();
  const progress = interpolate(frame, [0, 24], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  if (functionName === "migration_map_timeline") {
    return (
      <div style={{ position: "absolute", left: "12%", right: "12%", top: "46%", height: 12, background: COLORS.jade, transform: `scaleX(${progress})`, transformOrigin: "left" }}>
        {[0, 25, 50, 75, 100].map((value) => (
          <span key={value} style={{ position: "absolute", left: `${value}%`, top: -10, width: 30, height: 30, borderRadius: "50%", background: value === 0 || value === 100 ? COLORS.rust : COLORS.indigo, border: `4px solid ${COLORS.ink}`, transform: "translateX(-50%)" }} />
        ))}
      </div>
    );
  }
  if (functionName === "lineage_graph" || functionName === "concept_mechanics_cutaway") {
    return (
      <svg viewBox="0 0 100 60" style={{ position: "absolute", left: "14%", top: "31%", width: "72%", height: "48%" }}>
        <path d="M15 34 L50 20 L85 34 M50 20 L50 48" fill="none" stroke={COLORS.jade} strokeWidth="2" strokeDasharray={functionName === "concept_mechanics_cutaway" ? "0" : "5 2"} />
        {[{ x: 15, y: 34 }, { x: 50, y: 20 }, { x: 85, y: 34 }, { x: 50, y: 48 }].map((point, index) => (
          <circle key={index} cx={point.x} cy={point.y} r={index === 1 ? 5 : 4} fill={index === 3 ? COLORS.ochre : COLORS.indigo} stroke={COLORS.ink} strokeWidth="1.5" />
        ))}
      </svg>
    );
  }
  if (functionName === "document_quote_closeup") {
    return (
      <div style={{ position: "absolute", left: "17%", right: "17%", top: "36%", height: "36%", background: "#FFFDF7", border: `5px solid ${COLORS.ink}`, boxShadow: `12px 12px 0 ${COLORS.rust}` }}>
        {[0, 1, 2, 3].map((index) => <div key={index} style={{ position: "absolute", left: "9%", right: index === 2 ? "30%" : "9%", top: `${22 + index * 17}%`, height: 4, background: index === 1 ? COLORS.rust : COLORS.muted }} />)}
      </div>
    );
  }
  if (functionName === "illustrated_reconstruction") {
    return (
      <div style={{ position: "absolute", left: "25%", right: "25%", top: "35%", height: "42%", background: COLORS.ochre, clipPath: "polygon(50% 0, 100% 100%, 0 100%)", border: `4px solid ${COLORS.ink}` }} />
    );
  }
  return (
    <div style={{ position: "absolute", left: "22%", right: "22%", top: "38%", height: "34%", border: `5px solid ${COLORS.rust}`, background: COLORS.surface, opacity: 0.92 }} />
  );
};

const ShotFrame: React.FC<{
  shot: DocumentaryShot;
  assetMap: Record<string, string>;
  beat?: DocumentaryVisualBeat;
  characterLayers?: DocumentaryCharacterLayer[];
}> = ({ shot, assetMap, beat, characterLayers }) => {
  const functionName = shot.visual_type || shot.function;
  const frame = useCurrentFrame();
  const titleOpacity = interpolate(frame, [0, 12], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const label = functionName === "illustrated_reconstruction" ? shot.illustration_label || "ILLUSTRATION / RECONSTRUCTION" : undefined;
  return (
    <div style={{ width: "100%", height: "100%", background: COLORS.paper, overflow: "hidden", ...SAFE_TEXT }}>
      <div style={{ position: "absolute", inset: 0, background: `linear-gradient(135deg, ${COLORS.paper}, #eadac5)`, opacity: 0.72 }} />
      <div style={{ position: "absolute", left: "8%", right: "8%", top: "9%", opacity: titleOpacity, fontSize: 52, fontWeight: 700, letterSpacing: 1.2, textTransform: "uppercase" }}>{shotTitle(shot)}</div>
      <VectorTreatment functionName={functionName} />
      <LocalAsset shot={shot} assetMap={assetMap} beat={beat} />
      <CharacterLayers layers={characterLayers || shot.character_layers || []} assetMap={assetMap} />
      {beat ? <div style={{ position: "absolute", left: "8%", bottom: "13%", maxWidth: "70%", padding: "10px 14px", background: `${COLORS.paper}E8`, borderLeft: `7px solid ${COLORS.rust}`, fontSize: 24 }}>{beat.narration_excerpt}</div> : null}
      {label ? <div style={{ position: "absolute", left: "8%", top: "23%", padding: "7px 13px", background: COLORS.ink, color: COLORS.paper, fontFamily: "Roboto Mono, monospace", fontSize: 22, letterSpacing: 1 }}>{label}</div> : null}
      <CitationRail shot={shot} />
    </div>
  );
};

const LegacyDocumentaryComposition: React.FC<DocumentaryProps> = (props) => {
  const treatment = unwrapTreatment(props);
  const assetMap = assetMapFor(props);
  const { fps } = useVideoConfig();
  let cursor = 0;
  const timeline = treatment.shots.map((shot) => {
    const duration = Math.max(1, Math.round(shot.duration_in_frames || (shot.duration_s || 2) * fps));
    const item = { shot, from: cursor, duration };
    cursor += duration;
    return item;
  });
  return (
    <div style={{ width: "100%", height: "100%", background: COLORS.background, overflow: "hidden" }}>
      {timeline.map(({ shot, from, duration }) => (
        <Sequence key={String(shot.shot_id)} from={from} durationInFrames={duration} premountFor={Math.max(1, Math.min(from, 2 * fps))}>
          {shot.parameters?.visual_beats?.length ? (() => {
            let beatCursor = 0;
            return shot.parameters.visual_beats.map((beat) => {
              const beatDuration = Math.max(1, Math.round(beat.duration_s * fps));
              const beatFrom = beatCursor;
              beatCursor += beatDuration;
              return (
                <Sequence key={beat.coverage_slot_id} from={beatFrom} durationInFrames={beatDuration} premountFor={Math.min(fps, beatFrom)}>
                  <ShotFrame
                    shot={shot}
                    assetMap={assetMap}
                    beat={beat}
                    characterLayers={beat.character_layers || []}
                  />
                </Sequence>
              );
            });
          })() : <ShotFrame shot={shot} assetMap={assetMap} />}
        </Sequence>
      ))}
      <div style={{ position: "absolute", right: "8%", top: "9%", color: COLORS.indigo, fontFamily: "Roboto Mono, monospace", fontSize: 20 }}>HISTORY / DOCUMENTARY V4</div>
    </div>
  );
};

export const DocumentaryComposition: React.FC<DocumentaryProps> = LegacyDocumentaryComposition;

/** Dedicated motion-plan entrypoint kept beside the legacy Documentary lane. */
export const DocumentaryMotionComposition: React.FC<EditorialMotionProps> = (props) => (
  <EditorialMotionComposition {...props} />
);

export { unwrapTreatment };
