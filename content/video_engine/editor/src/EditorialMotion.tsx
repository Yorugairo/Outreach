import React from "react";
import {
  Audio,
  CalculateMetadataFunction,
  Img,
  Sequence,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import type {
  EditorialMotionAudio,
  EditorialMotionCamera,
  EditorialMotionLayer,
  EditorialMotionLayerRole,
  EditorialMotionOverlay,
  EditorialMotionPlan,
  EditorialMotionProps,
  EditorialMotionRenderProfile,
  EditorialMotionShot,
  EditorialMotionTransition,
} from "./types";

const COLORS = {
  paper: "#F4EBDD",
  ink: "#1F252A",
  background: "#171B20",
  rust: "#A44A32",
  indigo: "#324C73",
};

const BASE_TEXT: React.CSSProperties = {
  fontFamily: "Inter, Arial, sans-serif",
  color: COLORS.ink,
  lineHeight: 1.18,
};

const DIAGNOSTIC_TEXT: React.CSSProperties = {
  position: "absolute",
  zIndex: 1000,
  padding: "8px 11px",
  background: "rgba(15, 19, 24, 0.9)",
  color: "#EAF7F3",
  fontFamily: "Roboto Mono, Consolas, monospace",
  fontSize: 18,
  lineHeight: 1.35,
  letterSpacing: 0.2,
  whiteSpace: "pre-wrap",
};

const finite = (value: number | undefined, fallback: number): number =>
  typeof value === "number" && Number.isFinite(value) ? value : fallback;

const clamp = (value: number, minimum: number, maximum: number): number =>
  Math.min(maximum, Math.max(minimum, value));

/**
 * Return a public-relative path only.  Renderer props are untrusted JSON, so
 * remote, absolute, and traversal paths fail closed before staticFile().
 */
export const normalizeEditorialMotionAsset = (
  source: string | undefined,
): string | undefined => {
  if (typeof source !== "string" || !source.trim()) return undefined;
  const normalized = source.replaceAll("\\", "/").trim();
  if (
    /^(?:https?:|data:|blob:|file:|javascript:)/i.test(normalized) ||
    normalized.startsWith("/") ||
    /^[A-Za-z]:\//.test(normalized)
  ) {
    return undefined;
  }
  const withoutPublic = normalized
    .replace(/^public\//i, "")
    .replace(/^(?:\.\/)+/, "");
  const segments = withoutPublic.split("/");
  if (
    !withoutPublic ||
    segments.some((segment) => !segment || segment === "." || segment === "..")
  ) {
    return undefined;
  }
  return withoutPublic;
};

/** Resolve an approved asset ID from the editor/public asset boundary. */
export const resolveEditorialMotionAsset = (
  assetId: string | undefined,
  assetMap: Record<string, string>,
): string | undefined => {
  if (!assetId) return undefined;
  const path = normalizeEditorialMotionAsset(assetMap[assetId]);
  return path ? staticFile(path) : undefined;
};

/** Resolve the canonical narration path without allowing a second clock/path. */
export const resolveEditorialMotionAudio = (
  audio: EditorialMotionAudio | undefined,
): string | undefined => {
  const path = normalizeEditorialMotionAsset(audio?.path);
  return path ? staticFile(path) : undefined;
};

/** Resolve only job-local, hash-validated SFX staged by the render service. */
export const resolveEditorialMotionSoundEffect = (
  effectId: string,
  soundEffectMap: Record<string, string> | undefined,
): string | undefined => {
  const path = normalizeEditorialMotionAsset(soundEffectMap?.[effectId]);
  return path ? staticFile(path) : undefined;
};

export type EditorialMotionTimelineItem = {
  shot: EditorialMotionShot;
  from: number;
  duration: number;
  coreDuration: number;
  transitionOutDuration: number;
};

const transitionFrames = (
  transition: EditorialMotionTransition | undefined,
  fps: number,
): number => {
  if (!transition || transition.kind === "hard_cut" || transition.kind === "match_cut") {
    return 0;
  }
  const seconds = clamp(finite(transition.duration_s, 0.3), 0, 1.5);
  return Math.max(0, Math.round(seconds * fps));
};

/** Build a stable frame timeline from the plan's continuous second clock. */
export const buildEditorialMotionTimeline = (
  plan: Pick<EditorialMotionPlan, "shots">,
  fps: number,
): EditorialMotionTimelineItem[] => {
  return plan.shots.map((shot) => {
    const coreDuration = Math.max(1, Math.round(Math.max(0, shot.duration_s) * fps));
    const transitionOutDuration = transitionFrames(shot.transition_out, fps);
    return {
      shot,
      from: Math.max(0, Math.round(Math.max(0, shot.start_s) * fps)),
      duration: coreDuration + transitionOutDuration,
      coreDuration,
      transitionOutDuration,
    };
  });
};

const ease = (value: number, easing: EditorialMotionCamera["easing"]): number => {
  const t = clamp(value, 0, 1);
  if (easing === "linear") return t;
  // Both named bounded easings intentionally use the same deterministic
  // smoothstep curve; this keeps low-resolution and full renders identical.
  return t * t * (3 - 2 * t);
};

const cameraProgress = (
  camera: EditorialMotionCamera,
  frame: number,
  fps: number,
  coreDuration: number,
): number => {
  if (camera.kind === "locked" || camera.amount === 0 || camera.move_s <= 0) return 0;
  const holdIn = Math.max(0, Math.round(camera.hold_in_s * fps));
  const move = Math.max(0, Math.round(camera.move_s * fps));
  if (frame <= holdIn) return 0;
  const movementFrame = Math.min(Math.max(0, frame - holdIn), move);
  // Clamp camera movement to the shot's authored duration.  An extended
  // outgoing transition is a hold, never an opportunity for new motion.
  const boundedFrame = Math.min(movementFrame, Math.max(0, coreDuration - holdIn));
  return ease(move <= 0 ? 0 : boundedFrame / move, camera.easing);
};

const cameraPhase = (
  camera: EditorialMotionCamera,
  frame: number,
  fps: number,
  coreDuration: number,
): "hold" | "move" | "settle" => {
  if (camera.kind === "locked" || camera.move_s <= 0 || camera.amount === 0) return "hold";
  const holdIn = Math.max(0, Math.round(camera.hold_in_s * fps));
  const move = Math.max(0, Math.round(camera.move_s * fps));
  if (frame <= holdIn) return "hold";
  if (frame < Math.min(coreDuration, holdIn + move)) return "move";
  return "settle";
};

const directionVector = (
  direction: EditorialMotionCamera["direction"],
): { x: number; y: number } => {
  switch (direction) {
    case "left":
      return { x: -1, y: 0 };
    case "right":
      return { x: 1, y: 0 };
    case "up":
      return { x: 0, y: -1 };
    case "down":
      return { x: 0, y: 1 };
    default:
      return { x: 0, y: 0 };
  }
};

const cameraTransform = (
  camera: EditorialMotionCamera,
  focal: { x: number; y: number },
  progress: number,
  parallaxFactor = 1,
): string => {
  const amount = clamp(Math.abs(finite(camera.amount, 0)), 0, 0.06) * parallaxFactor;
  if (camera.kind === "locked" || amount <= 0 || progress <= 0) return "none";
  const vector = directionVector(camera.direction);
  if (
    camera.kind === "push_settle" ||
    camera.kind === "pull_settle" ||
    camera.direction === "toward_focal_point"
  ) {
    const scale = camera.kind === "pull_settle" ? 1 - amount * progress : 1 + amount * progress;
    return `scale(${scale})`;
  }
  if (camera.kind === "lateral_reveal" || camera.kind === "foreground_parallax" || camera.kind === "cut_on_motion") {
    const fallbackDirection = camera.direction || "right";
    const resolvedVector = directionVector(fallbackDirection);
    const x = (vector.x || resolvedVector.x) * amount * progress * 100;
    const y = (vector.y || resolvedVector.y) * amount * progress * 100;
    return `translate(${x}%, ${y}%)`;
  }
  return "none";
};

const actionName = (layer: EditorialMotionLayer, shot: EditorialMotionShot): string => {
  if (layer.action?.trim()) return layer.action.trim().toLowerCase();
  if (layer.role === "character" || layer.role === "prop") {
    return (shot.subject_action || "locked").trim().toLowerCase();
  }
  if (layer.role === "ambient") {
    return (shot.ambient_actions[0] || "locked").trim().toLowerCase();
  }
  if (layer.role === "diagram" && shot.information_reveal) {
    return shot.information_reveal.trim().toLowerCase();
  }
  return "locked";
};

const actionProgress = (frame: number, duration: number, fps: number): number => {
  const intro = Math.max(1, Math.min(Math.round(fps * 0.8), Math.floor(duration * 0.45)));
  return ease(interpolate(frame, [0, intro], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }), "smoothstep");
};

const layerExitProgress = (
  layer: EditorialMotionLayer,
  frame: number,
  fps: number,
): number | undefined => {
  const timing = layer.timing;
  if (!timing) return undefined;
  const start = Math.max(0, Math.round(timing.exit_at_s * fps));
  const duration = Math.max(1, Math.round(timing.exit_duration_s * fps));
  return clamp((frame - start) / duration, 0, 1);
};

type LayerActionStyle = Pick<React.CSSProperties, "transform" | "transformOrigin" | "opacity" | "clipPath" | "filter">;

/** Local, authored layer motion. Unknown actions deliberately remain still. */
const layerActionStyle = (
  action: string,
  frame: number,
  duration: number,
  fps: number,
): LayerActionStyle => {
  const progress = actionProgress(frame, duration, fps);
  if (/^(?:locked|none|hold|still)$/i.test(action)) return {};
  if (/character[_ -]?enter|enter[_ -]?(?:from[_ -]?)?(?:left|right)?/.test(action)) {
    const fromRight = /right/.test(action);
    return {
      opacity: progress,
      transform: `translateX(${(fromRight ? 1 : -1) * (1 - progress) * 18}%)`,
    };
  }
  if (/gesture|reach|nod|turn|react/.test(action)) {
    return {
      transform: `translateY(${Math.sin(progress * Math.PI) * -1.5}%) rotate(${Math.sin(progress * Math.PI * 2) * 1.2}deg)`,
      transformOrigin: "50% 88%",
    };
  }
  if (/lamp[_ -]?flicker|window[_ -]?light|light[_ -]?flicker|ambient[_ -]?pulse/.test(action)) {
    return {
      opacity: 0.88 + 0.1 * (0.5 + 0.5 * Math.sin((frame / Math.max(1, duration)) * Math.PI * 8)),
      filter: "brightness(1.04)",
    };
  }
  if (/paper[_ -]?reveal|reveal|wipe|trace|draw/.test(action)) {
    return { clipPath: `inset(0 ${(1 - progress) * 100}% 0 0)` };
  }
  if (/settle|land|drop/.test(action)) {
    return { transform: `translateY(${(1 - progress) * -3}%)` };
  }
  // Do not invent a generic fallback transform: a camera is not a visual
  // event, and unknown layer actions must fail as a deterministic still.
  return {};
};

const roleDefaultZ = (role: EditorialMotionLayerRole): number => {
  switch (role) {
    case "world":
      return 0;
    case "depth":
      return 1;
    case "ambient":
      return 2;
    case "character":
    case "prop":
      return 4;
    case "diagram":
      return 5;
    default:
      return 1;
  }
};

const layerObjectFit = (role: EditorialMotionLayerRole): React.CSSProperties["objectFit"] =>
  role === "world" || role === "depth" || role === "ambient" ? "cover" : "contain";

/** A deliberately rough, local ink-and-paper puff for a narration-timed exit. */
const SmokePuff: React.FC<{
  layer: EditorialMotionLayer;
  frame: number;
  fps: number;
}> = ({ layer, frame, fps }) => {
  if (layer.timing?.exit_effect !== "smoke_puff") return null;
  const start = Math.max(0, Math.round(layer.timing.exit_at_s * fps));
  const duration = Math.max(1, Math.round((layer.timing.exit_effect_duration_s || layer.timing.exit_duration_s) * fps));
  const progress = clamp((frame - start) / duration, 0, 1);
  if (progress <= 0 || progress >= 1) return null;
  const layout = layer.layout || { x: 0.35, y: 0.3, width: 0.3, height: 0.45 };
  return (
    <svg
      viewBox="0 0 300 220"
      style={{
        position: "absolute",
        left: `${(layout.x + layout.width * 0.12) * 100}%`,
        top: `${(layout.y + layout.height * 0.30) * 100}%`,
        width: `${layout.width * 70}%`,
        height: `${layout.height * 54}%`,
        zIndex: (layer.z_index ?? roleDefaultZ(layer.role)) + 1,
        opacity: (1 - progress) * 0.92,
        transform: `translate(${progress * 3}px, ${-progress * 16}px) scale(${0.72 + progress * 0.66})`,
        transformOrigin: "50% 68%",
        pointerEvents: "none",
      }}
    >
      <path
        d="M36 180 C12 163 22 132 53 126 C39 98 58 76 87 83 C82 53 115 32 143 49 C159 20 202 31 205 66 C236 56 262 83 246 112 C278 137 255 174 220 173 C204 199 164 198 145 178 C119 207 72 202 69 177 C55 186 44 186 36 180 Z"
        fill="rgba(222, 207, 169, 0.92)"
        stroke="rgba(53, 44, 33, 0.84)"
        strokeWidth="5"
        strokeLinejoin="round"
      />
      <path
        d="M70 154 C87 139 106 143 112 160 M136 91 C151 79 172 86 176 105 M188 150 C201 136 220 139 231 151"
        fill="none"
        stroke="rgba(141, 119, 81, 0.58)"
        strokeWidth="4"
        strokeLinecap="round"
      />
    </svg>
  );
};

const MotionLayer: React.FC<{
  layer: EditorialMotionLayer;
  shot: EditorialMotionShot;
  assetMap: Record<string, string>;
  frame: number;
  duration: number;
  fps: number;
}> = ({ layer, shot, assetMap, frame, duration, fps }) => {
  const src = resolveEditorialMotionAsset(layer.asset_id, assetMap);
  if (!src) return null;
  const camera = shot.camera;
  const focal = shot.focal_point;
  const progress = cameraProgress(camera, frame, fps, duration);
  const actionStyle = layerActionStyle(actionName(layer, shot), frame, duration, fps);
  const exitProgress = layerExitProgress(layer, frame, fps);
  // Foreground parallax is intentionally per-layer.  The world remains locked
  // while depth/foreground plates move by a bounded authored amount.
  const foregroundAction = /foreground|parallax/.test(actionName(layer, shot));
  const cameraStyle = camera.kind === "foreground_parallax"
    ? cameraTransform(camera, focal, progress, layer.role === "depth" || layer.role === "ambient" || foregroundAction ? 1 : 0)
    : cameraTransform(camera, focal, progress);
  const transforms = [
    cameraStyle,
    actionStyle.transform,
    exitProgress !== undefined && exitProgress > 0 ? `scale(${1 - exitProgress * 0.06})` : undefined,
  ].filter((value) => value && value !== "none");
  const maskSrc = layer.mask_asset_id ? resolveEditorialMotionAsset(layer.mask_asset_id, assetMap) : undefined;
  const layout = layer.layout;
  const layerOpacity = typeof actionStyle.opacity === "number" ? actionStyle.opacity : 1;
  return (
    <>
      <Img
        src={src}
        style={{
          position: "absolute",
          inset: layout ? undefined : 0,
          left: layout ? `${clamp(layout.x, 0, 1) * 100}%` : undefined,
          top: layout ? `${clamp(layout.y, 0, 1) * 100}%` : undefined,
          width: layout ? `${clamp(layout.width, 0.001, 1) * 100}%` : "100%",
          height: layout ? `${clamp(layout.height, 0.001, 1) * 100}%` : "100%",
          objectFit: layout?.fit || layerObjectFit(layer.role),
          objectPosition: `${clamp(focal.x, 0, 1) * 100}% ${clamp(focal.y, 0, 1) * 100}%`,
          zIndex: layer.z_index ?? roleDefaultZ(layer.role),
          transform: transforms.length ? transforms.join(" ") : "none",
          transformOrigin: actionStyle.transformOrigin || `${clamp(focal.x, 0, 1) * 100}% ${clamp(focal.y, 0, 1) * 100}%`,
          opacity: layerOpacity * (exitProgress === undefined ? 1 : 1 - exitProgress),
          clipPath: actionStyle.clipPath,
          filter: actionStyle.filter,
          maskImage: maskSrc ? `url(${maskSrc})` : undefined,
          WebkitMaskImage: maskSrc ? `url(${maskSrc})` : undefined,
        }}
      />
      {exitProgress === undefined ? null : <SmokePuff layer={layer} frame={frame} fps={fps} />}
    </>
  );
};

const transitionInOpacity = (
  transition: EditorialMotionTransition | undefined,
  frame: number,
  fps: number,
): number => {
  const duration = transitionFrames(transition, fps);
  if (!transition || duration <= 0) return 1;
  // A match cut is intentionally a direct cut.  Its authored motif/reason
  // explains the adjacency; adding a synthetic zoom would violate the locked
  // camera default and invent motion not present in the plan.
  if (transition.kind === "match_cut" || transition.kind === "hard_cut") return 1;
  if (transition.kind !== "crossfade" && transition.kind !== "chapter_fade") return 1;
  return interpolate(frame, [0, duration], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
};

const transitionInClipPath = (
  transition: EditorialMotionTransition | undefined,
  frame: number,
  fps: number,
): string | undefined => {
  if (!transition || transition.kind !== "paper_wipe") return undefined;
  const duration = transitionFrames(transition, fps);
  const progress = interpolate(frame, [0, Math.max(1, duration)], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return `inset(0 ${(1 - progress) * 100}% 0 0)`;
};

const TransitionOutOverlay: React.FC<{
  transition: EditorialMotionTransition | undefined;
  frame: number;
  coreDuration: number;
  fps: number;
}> = ({ transition, frame, coreDuration, fps }) => {
  if (!transition || frame < coreDuration) return null;
  const duration = transitionFrames(transition, fps);
  if (duration <= 0) return null;
  const progress = interpolate(frame - coreDuration, [0, duration], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  if (transition.kind === "chapter_fade") {
    return <div style={{ position: "absolute", inset: 0, zIndex: 900, background: COLORS.background, opacity: progress }} />;
  }
  if (transition.kind === "paper_wipe") {
    return (
      <div
        style={{
          position: "absolute",
          inset: 0,
          zIndex: 900,
          background: COLORS.paper,
          transform: `translateX(${(1 - progress) * -100}%)`,
        }}
      />
    );
  }
  return null;
};

const overlayText = (overlay: EditorialMotionOverlay): string =>
  overlay.text || overlay.label || overlay.citation_id || "";

const overlayPosition = (overlay: EditorialMotionOverlay): React.CSSProperties => {
  switch (overlay.position) {
    case "top":
      return { left: "8%", right: "8%", top: "9%" };
    case "center":
      return { left: "12%", right: "12%", top: "42%", transform: "translateY(-50%)" };
    case "rail":
      return { left: "8%", right: "8%", bottom: "7%" };
    case "bottom":
    default:
      return { left: "8%", right: "8%", bottom: "12%" };
  }
};

const MotionOverlay: React.FC<{
  overlay: EditorialMotionOverlay;
  assetMap: Record<string, string>;
  frame: number;
  fps: number;
  shotDuration: number;
}> = ({ overlay, assetMap, frame, fps, shotDuration }) => {
  const from = Math.max(0, Math.round(finite(overlay.from_s, 0) * fps));
  const duration = Math.max(1, Math.round(finite(overlay.duration_s, shotDuration / fps) * fps));
  if (frame < from || frame >= from + duration) return null;
  const fade = Math.min(Math.round(fps * 0.14), Math.floor(duration / 2));
  const opacity = fade <= 0
    ? 1
    : interpolate(frame - from, [0, fade, Math.max(fade, duration - fade), duration], [0, 1, 1, 0], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      });
  const kind = overlay.kind || "text";
  const text = overlayText(overlay);
  const base: React.CSSProperties = {
    position: "absolute",
    zIndex: 20,
    opacity,
    ...overlayPosition(overlay),
    color: kind === "citation" ? COLORS.indigo : COLORS.ink,
    fontFamily: kind === "citation" ? "Roboto Mono, Consolas, monospace" : "Inter, Arial, sans-serif",
    fontSize: kind === "citation" ? 21 : 32,
    fontWeight: kind === "citation" ? 500 : 700,
    letterSpacing: kind === "citation" ? 0.2 : 0,
    padding: kind === "citation" ? "0" : "10px 14px",
    background: kind === "citation" ? "transparent" : `${COLORS.paper}E8`,
    borderLeft: kind === "citation" ? undefined : `6px solid ${COLORS.rust}`,
    textAlign: "left",
    ...overlay.style,
  };
  if (kind === "image" && overlay.src) {
    const src = normalizeEditorialMotionAsset(overlay.src);
    if (!src) return null;
    return <Img src={staticFile(src)} style={{ ...base, objectFit: "contain" }} />;
  }
  if (kind === "box") {
    return <div style={{ ...base, right: "8%", bottom: "12%", minHeight: 50, background: "rgba(0,0,0,0.34)" }} />;
  }
  if (!text) return null;
  return <div style={base}>{text}</div>;
};

const NarrationCaption: React.FC<{ shot: EditorialMotionShot; frame: number; fps: number; duration: number }> = ({ shot, frame, fps, duration }) => {
  if (!shot.narration_excerpt.trim()) return null;
  const fade = Math.min(Math.round(fps * 0.14), Math.floor(duration / 2));
  const opacity = fade <= 0
    ? 1
    : interpolate(frame, [0, fade, Math.max(fade, duration - fade), duration], [0, 1, 1, 0], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      });
  return (
    <div
      style={{
        position: "absolute",
        left: "8%",
        right: "8%",
        bottom: "12%",
        zIndex: 15,
        opacity,
        padding: "10px 14px",
        background: `${COLORS.paper}E8`,
        borderLeft: `6px solid ${COLORS.rust}`,
        fontFamily: "Inter, Arial, sans-serif",
        color: COLORS.ink,
        fontSize: 27,
        lineHeight: 1.18,
      }}
    >
      {shot.narration_excerpt}
    </div>
  );
};

const InformationReveal: React.FC<{ shot: EditorialMotionShot; frame: number; fps: number; duration: number }> = ({ shot, frame, fps, duration }) => {
  const information = shot.information_reveal.trim();
  if (!information || /^(?:none|locked|n\/a)$/i.test(information)) return null;
  const revealFrames = Math.max(1, Math.min(Math.round(fps * 0.7), Math.floor(duration * 0.5)));
  const opacity = interpolate(frame, [0, revealFrames], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const surface = shot.information_surface || {
    mode: "floating_label" as const,
    x: 0.54,
    y: 0.14,
    width: 0.38,
    height: 0.16,
    text_align: "left" as const,
  };
  if (surface.mode === "none") return null;
  const integrated = surface.mode === "surface_ink";
  return (
    <div style={{
      position: "absolute",
      left: `${surface.x * 100}%`,
      top: `${surface.y * 100}%`,
      width: `${surface.width * 100}%`,
      minHeight: `${surface.height * 100}%`,
      zIndex: 14,
      opacity,
      padding: integrated ? 0 : "8px 12px",
      background: integrated ? "transparent" : `${COLORS.indigo}E8`,
      color: integrated ? "#2B2117" : "#F5FAFF",
      fontFamily: integrated ? "Georgia, 'Times New Roman', serif" : "Roboto Mono, Consolas, monospace",
      fontWeight: integrated ? 700 : 500,
      fontSize: integrated ? 25 : 22,
      lineHeight: 1.12,
      letterSpacing: integrated ? 0.6 : 0,
      textAlign: surface.text_align || "left",
      textShadow: integrated ? "0 1px 0 rgba(255,245,218,0.34)" : "none",
    }}>
      {information}
    </div>
  );
};

/**
 * Ambient actions can be authored even when the approved asset map contains
 * only a world plate.  Keep these effects localized and translucent; never
 * animate the entire world plate as a substitute for environmental motion.
 */
const AmbientActionEffects: React.FC<{ shot: EditorialMotionShot; frame: number; duration: number }> = ({ shot, frame, duration }) => {
  if (!shot.ambient_actions.length) return null;
  return (
    <>
      {shot.ambient_actions.map((rawAction, index) => {
        const action = rawAction.trim().toLowerCase();
        const progress = frame / Math.max(1, duration);
        const pulse = 0.12 + 0.1 * (0.5 + 0.5 * Math.sin(progress * Math.PI * 8 + index));
        if (/lamp[_ -]?flicker|light[_ -]?flicker|ambient[_ -]?pulse/.test(action)) {
          return (
            <div
              key={`ambient:${index}:${action}`}
              style={{
                position: "absolute",
                right: "14%",
                top: "16%",
                width: "28%",
                height: "34%",
                zIndex: 3,
                opacity: pulse,
                background: "radial-gradient(circle at 70% 34%, rgba(255, 224, 158, 0.9), rgba(255, 224, 158, 0) 68%)",
                mixBlendMode: "screen",
                pointerEvents: "none",
              }}
            />
          );
        }
        if (/window[_ -]?light|sun[_ -]?beam/.test(action)) {
          return (
            <div
              key={`ambient:${index}:${action}`}
              style={{
                position: "absolute",
                left: "8%",
                top: "0",
                width: "42%",
                height: "100%",
                zIndex: 3,
                opacity: 0.12 + pulse,
                background: "linear-gradient(112deg, rgba(255,244,205,0.62), rgba(255,244,205,0) 58%)",
                mixBlendMode: "screen",
                pointerEvents: "none",
              }}
            />
          );
        }
        if (/smoke[_ -]?drift/.test(action)) {
          return (
            <div
              key={`ambient:${index}:${action}`}
              style={{
                position: "absolute",
                right: `${8 + progress * 9}%`,
                bottom: "8%",
                width: "35%",
                height: "42%",
                zIndex: 3,
                opacity: 0.16,
                background: "radial-gradient(ellipse at 40% 70%, rgba(45,39,34,0.68), rgba(45,39,34,0) 70%)",
                filter: "blur(9px)",
                pointerEvents: "none",
              }}
            />
          );
        }
        if (/cloud[_ -]?drift/.test(action)) {
          const easedDrift = ease(progress, "smoothstep");
          return (
            <div
              key={`ambient:${index}:${action}`}
              style={{
                position: "absolute",
                left: "3%",
                top: "3%",
                width: "78%",
                height: "31%",
                zIndex: 2,
                opacity: 0.14,
                background: [
                  "radial-gradient(ellipse at 10% 48%, rgba(190,202,211,0.62) 0 7%, rgba(190,202,211,0) 20%)",
                  "radial-gradient(ellipse at 27% 36%, rgba(174,190,202,0.55) 0 9%, rgba(174,190,202,0) 23%)",
                  "radial-gradient(ellipse at 48% 54%, rgba(190,202,211,0.52) 0 8%, rgba(190,202,211,0) 22%)",
                  "radial-gradient(ellipse at 72% 32%, rgba(174,190,202,0.5) 0 10%, rgba(174,190,202,0) 24%)",
                  "radial-gradient(ellipse at 92% 52%, rgba(190,202,211,0.5) 0 8%, rgba(190,202,211,0) 21%)",
                ].join(","),
                filter: "blur(0.7px)",
                mixBlendMode: "screen",
                transform: `translateX(${easedDrift * 2.4}%)`,
                pointerEvents: "none",
              }}
            />
          );
        }
        if (/river[_ -]?flow|ship[_ -]?wake/.test(action)) {
          const flow = ease(progress, "smoothstep");
          const wake = /ship/.test(action);
          return (
            <div
              key={`ambient:${index}:${action}`}
              style={{
                position: "absolute",
                left: wake ? "26%" : "0",
                bottom: wake ? "5%" : "0",
                width: wake ? "46%" : "100%",
                height: wake ? "18%" : "24%",
                zIndex: 3,
                opacity: wake ? 0.24 : 0.18,
                overflow: "hidden",
                background: wake
                  ? "repeating-radial-gradient(ellipse at 50% 135%, rgba(241, 232, 205, 0.82) 0 2px, rgba(241, 232, 205, 0) 3px 16px)"
                  : "repeating-linear-gradient(174deg, rgba(117, 165, 171, 0) 0 8px, rgba(185, 217, 210, 0.56) 9px 11px, rgba(117, 165, 171, 0) 12px 21px)",
                backgroundSize: wake ? "138% 120%" : "150% 100%",
                backgroundPosition: wake ? `${50 + flow * 11}% 100%` : `${flow * 18}% 0`,
                maskImage: wake
                  ? "linear-gradient(to top, black, rgba(0,0,0,0.5) 55%, transparent)"
                  : "linear-gradient(to top, black, rgba(0,0,0,0.72) 55%, transparent)",
                pointerEvents: "none",
              }}
            />
          );
        }
        if (/leaves[_ -]?flutter|paper[_ -]?dust/.test(action)) {
          return (
            <div
              key={`ambient:${index}:${action}`}
              style={{
                position: "absolute",
                left: `${18 + progress * 22}%`,
                top: `${10 + Math.sin(progress * Math.PI * 2) * 3}%`,
                width: 12,
                height: 7,
                zIndex: 3,
                opacity: 0.48,
                borderRadius: "70% 15% 70% 15%",
                background: /paper/.test(action) ? "#D6C49D" : COLORS.rust,
                transform: `rotate(${progress * 140}deg)`,
                boxShadow: /paper/.test(action)
                  ? "70px 40px 0 #D6C49D, 180px 90px 0 #D6C49D"
                  : "90px 55px 0 #A44A32, 220px 115px 0 #7B3D2D",
                pointerEvents: "none",
              }}
            />
          );
        }
        return null;
      })}
    </>
  );
};

const DiagnosticBurnIn: React.FC<{
  shot: EditorialMotionShot;
  frame: number;
  fps: number;
  duration: number;
  renderProfile?: EditorialMotionRenderProfile;
}> = ({ shot, frame, fps, duration, renderProfile }) => {
  const phase = cameraPhase(shot.camera, frame, fps, duration);
  const profile = renderProfile ? ` | proof=${renderProfile.width}x${renderProfile.height}` : "";
  return (
    <div style={{ ...DIAGNOSTIC_TEXT, left: 18, top: 18 }}>
      {`shot=${shot.shot_id}\nfocal=${shot.focal_point.x.toFixed(3)},${shot.focal_point.y.toFixed(3)}\ncamera=${shot.camera.kind} phase=${phase} amount=${clamp(Math.abs(shot.camera.amount), 0, 0.06).toFixed(3)}\ntransition_in=${shot.transition_in.kind}: ${shot.transition_in.reason}\ncut=${shot.transition_out.kind}: ${shot.transition_out.reason}${profile}`}
    </div>
  );
};

const ShotFrame: React.FC<{
  item: EditorialMotionTimelineItem;
  assetMap: Record<string, string>;
  overlayMap: Record<string, EditorialMotionOverlay>;
  diagnostic: boolean;
  captionPolicy: "platform" | "burned_in";
  citationPolicy: "on_screen" | "credits_only";
  renderProfile?: EditorialMotionRenderProfile;
}> = ({ item, assetMap, overlayMap, diagnostic, captionPolicy, citationPolicy, renderProfile }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const shot = item.shot;
  const opacity = transitionInOpacity(shot.transition_in, frame, fps);
  const clipPath = transitionInClipPath(shot.transition_in, frame, fps);
  const withinCore = frame < item.coreDuration;
  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        overflow: "hidden",
        background: COLORS.paper,
        opacity,
        clipPath,
        ...BASE_TEXT,
      }}
    >
      {shot.layers.map((layer, index) => (
        <MotionLayer
          key={`${shot.shot_id}:${layer.asset_id}:${index}`}
          layer={layer}
          shot={shot}
          assetMap={assetMap}
          frame={Math.min(frame, item.coreDuration)}
          duration={item.coreDuration}
          fps={fps}
        />
      ))}
      {withinCore ? <AmbientActionEffects shot={shot} frame={frame} duration={item.coreDuration} /> : null}
      {withinCore && captionPolicy === "burned_in" ? <NarrationCaption shot={shot} frame={frame} fps={fps} duration={item.coreDuration} /> : null}
      {withinCore ? <InformationReveal shot={shot} frame={frame} fps={fps} duration={item.coreDuration} /> : null}
      {withinCore
        ? shot.overlay_ids.map((overlayId) => {
            const overlay = overlayMap[overlayId];
            if (citationPolicy === "credits_only" && overlay?.kind === "citation") return null;
            return overlay ? (
              <MotionOverlay
                key={`${shot.shot_id}:overlay:${overlayId}`}
                overlay={overlay}
                assetMap={assetMap}
                frame={frame}
                fps={fps}
                shotDuration={item.coreDuration}
              />
            ) : null;
          })
        : null}
      <TransitionOutOverlay transition={shot.transition_out} frame={frame} coreDuration={item.coreDuration} fps={fps} />
      {diagnostic ? <DiagnosticBurnIn shot={shot} frame={Math.min(frame, item.coreDuration)} fps={fps} duration={item.coreDuration} renderProfile={renderProfile} /> : null}
    </div>
  );
};

const defaultHash = "0".repeat(64);

export const defaultEditorialMotionProps: EditorialMotionProps = {
  plan: {
    schema_version: "editorial_motion_plan.v1",
    source_storyboard_hash: defaultHash,
    source_beat_plan_hash: defaultHash,
    scene_bundle_hashes: [defaultHash],
    scene_flow_graph_hash: defaultHash,
    asset_map_hash: defaultHash,
    audio_manifest_hash: defaultHash,
    pacing_recipe_hash: defaultHash,
    duration_s: 2,
    shots: [
      {
        shot_id: "editorial-motion-placeholder",
        parent_beat_ids: ["placeholder-beat"],
        parent_scene_bundle_id: "placeholder-scene",
        start_s: 0,
        duration_s: 2,
        word_range: { start_index: 0, end_index: 0 },
        narration_excerpt: "",
        purpose: "establish",
        shot_scale: "wide",
        focal_point: { x: 0.5, y: 0.5 },
        layers: [{ asset_id: "placeholder", role: "world" }],
        subject_action: "locked",
        ambient_actions: [],
        information_reveal: "none",
        camera: { kind: "locked", amount: 0, easing: "linear", hold_in_s: 2, move_s: 0, hold_out_s: 0 },
        transition_in: { kind: "hard_cut", reason: "opening frame" },
        transition_out: { kind: "hard_cut", reason: "end of excerpt" },
        audio_bridge: "continuous_narration",
        provider_motion: { requirement: "none", fallback: "locked_hold" },
        overlay_ids: [],
        uniqueness_signature: "wide:locked:placeholder",
      },
    ],
    provider_calls: 0,
    revision_only: true,
    artifact_hash: defaultHash,
  },
  asset_map: {},
  // Keep the registration preview renderable without pretending that a
  // canonical narration file exists in the editor's public directory.
  canonical_audio: { path: "", start_s: 0, volume: 1 },
  overlay_map: {},
  caption_policy: "platform",
  citation_policy: "credits_only",
  diagnostic: false,
};

export const calculateEditorialMotionMetadata: CalculateMetadataFunction<EditorialMotionProps> = ({ props }) => {
  const profile = props.render_profile || props.low_res;
  const fps = Math.max(1, Math.round(finite(profile?.fps, 30)));
  return {
    durationInFrames: Math.max(1, Math.round(Math.max(0.01, props.plan.duration_s) * fps)),
    width: Math.max(1, Math.round(finite(profile?.width, 1920))),
    height: Math.max(1, Math.round(finite(profile?.height, 1080))),
    fps,
  };
};

export const EditorialMotionComposition: React.FC<EditorialMotionProps> = (props) => {
  const { fps } = useVideoConfig();
  const timeline = buildEditorialMotionTimeline(props.plan, fps);
  const audioSrc = resolveEditorialMotionAudio(props.canonical_audio);
  const audioStart = Math.max(0, Math.round(finite(props.canonical_audio.start_s, props.plan.source_start_s || 0) * fps));
  const renderProfile = props.render_profile || props.low_res;
  return (
    <div style={{ width: "100%", height: "100%", overflow: "hidden", background: COLORS.background }}>
      {timeline.map((item) => (
        <Sequence
          key={item.shot.shot_id}
          from={item.from}
          durationInFrames={item.duration}
          premountFor={Math.max(1, Math.min(item.from, 2 * fps))}
        >
          <ShotFrame
            item={item}
            assetMap={props.asset_map}
            overlayMap={props.overlay_map}
            diagnostic={props.diagnostic === true}
            captionPolicy={props.caption_policy || "platform"}
            citationPolicy={props.citation_policy || "credits_only"}
            renderProfile={renderProfile}
          />
        </Sequence>
      ))}
      {audioSrc ? (
        <Audio
          src={audioSrc}
          startFrom={audioStart}
          volume={props.canonical_audio.volume ?? 1}
        />
      ) : null}
      {timeline.flatMap((item) => (item.shot.sound_effects || []).map((effect) => {
        const src = resolveEditorialMotionSoundEffect(effect.id, props.sound_effect_map);
        if (!src) return null;
        return (
          <Sequence
            key={`${item.shot.shot_id}:sfx:${effect.id}:${effect.at_s}`}
            from={item.from + Math.max(0, Math.round(effect.at_s * fps))}
            durationInFrames={Math.max(1, Math.round(effect.duration_s * fps))}
          >
            <Audio src={src} volume={effect.volume} />
          </Sequence>
        );
      }))}
    </div>
  );
};
