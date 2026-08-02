import React from "react";
import {
  Img,
  Sequence,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { Audio, Video } from "@remotion/media";
import type {
  Aspect,
  CaptionLayer,
  EditManifest,
  EditorialProps,
  EditClip,
  OverlayLayer,
  TimelineClip,
  TransitionKind,
} from "./types";

const DEFAULT_SAFE_STYLE: React.CSSProperties = {
  color: "#ffffff",
  fontFamily: "Arial, sans-serif",
  fontSize: 56,
  fontWeight: 700,
  lineHeight: 1.15,
  textAlign: "center",
  textShadow: "0 3px 12px rgba(0, 0, 0, 0.75)",
};

const DEFAULT_OVERLAY_STYLE: React.CSSProperties = {
  color: "#ffffff",
  fontFamily: "Arial, sans-serif",
  fontSize: 42,
  fontWeight: 700,
  lineHeight: 1.15,
  textShadow: "0 2px 8px rgba(0, 0, 0, 0.65)",
};

const asNumber = (value: unknown, fallback: number): number => {
  return typeof value === "number" && Number.isFinite(value) ? value : fallback;
};

export const profileForAspect = (aspect: Aspect) => {
  if (aspect === "vertical") {
    return { width: 1080, height: 1920, fps: 30 };
  }
  return { width: 1920, height: 1080, fps: 60 };
};

export const resolveAsset = (source: string): string => {
  const normalized = source.replaceAll("\\", "/");
  if (/^(https?:|data:|blob:|file:)/i.test(normalized)) {
    return normalized;
  }
  // Relative assets under editor/public use staticFile(), which keeps the
  // composition valid when the local project is rendered from another cwd.
  if (/^public\//i.test(normalized)) {
    return staticFile(normalized.slice("public/".length));
  }
  if (normalized.startsWith("/")) {
    return `file://${normalized}`;
  }
  if (/^[A-Za-z]:\//.test(normalized)) {
    return `file:///${normalized}`;
  }
  return staticFile(normalized);
};

export const transitionDuration = (
  clip: EditClip,
  fps: number,
): number => {
  const kind = clip.transition ?? "continuous";
  if (kind !== "crossfade" && kind !== "match_cut") {
    return 0;
  }
  if (typeof clip.transition_frames === "number") {
    return Math.max(0, Math.round(clip.transition_frames));
  }
  return Math.max(0, Math.round(fps * 0.3));
};

export const buildTimeline = (
  manifest: Pick<EditManifest, "clips" | "fps">,
): TimelineClip[] => {
  let cursor = 0;
  return manifest.clips.map((clip, index) => {
    const duration = Math.max(1, Math.round(clip.duration_in_frames));
    const requestedOverlap =
      index === 0 ? 0 : transitionDuration(clip, manifest.fps);
    const previousDuration =
      index === 0 ? duration : Math.max(1, Math.round(manifest.clips[index - 1].duration_in_frames));
    const overlap = Math.min(
      requestedOverlap,
      Math.floor(previousDuration / 2),
      Math.floor(duration / 2),
    );
    const from = index === 0 ? 0 : cursor - overlap;
    cursor = from + duration;
    return {
      ...clip,
      duration_in_frames: duration,
      transition_frames: overlap,
      transition: clip.transition ?? "continuous",
      from,
    };
  });
};

const transitionOpacity = (
  frame: number,
  kind: TransitionKind,
  duration: number,
): number => {
  if (kind !== "crossfade" && kind !== "match_cut") {
    return 1;
  }
  return interpolate(frame, [0, Math.max(1, duration)], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
};

const transitionTransform = (
  frame: number,
  kind: TransitionKind,
  duration: number,
): string => {
  if (kind !== "match_cut") {
    return "none";
  }
  const progress = interpolate(frame, [0, Math.max(1, duration)], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const scale = interpolate(progress, [0, 1], [1.025, 1]);
  return `scale(${scale})`;
};

const ClipLayer: React.FC<{ clip: TimelineClip }> = ({ clip }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const kind = clip.transition ?? "continuous";
  const duration = transitionDuration(clip, fps);
  const opacity = transitionOpacity(frame, kind, duration);
  const transform = transitionTransform(frame, kind, duration);
  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        opacity,
        transform,
      }}
    >
      <Video
        src={resolveAsset(clip.src)}
        muted
        objectFit="contain"
        style={{
          width: "100%",
          height: "100%",
        }}
      />
    </div>
  );
};

const CaptionLayerView: React.FC<{
  caption: CaptionLayer;
  aspect: Aspect;
}> = ({ caption, aspect }) => {
  const frame = useCurrentFrame();
  const fadeFrames = Math.min(4, Math.floor(caption.duration_in_frames / 2));
  const opacity = fadeFrames <= 0
    ? 1
    : interpolate(frame, [0, fadeFrames, caption.duration_in_frames - fadeFrames, caption.duration_in_frames], [0, 1, 1, 0], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      });
  const safeBottom = aspect === "vertical" ? "16%" : "8%";
  return (
    <div
      style={{
        position: "absolute",
        left: "8%",
        right: "8%",
        bottom: safeBottom,
        opacity,
        ...DEFAULT_SAFE_STYLE,
        ...caption.style,
      }}
    >
      {caption.text}
    </div>
  );
};

const OverlayLayerView: React.FC<{ overlay: OverlayLayer }> = ({ overlay }) => {
  const frame = useCurrentFrame();
  const fadeFrames = Math.min(4, Math.floor(overlay.duration_in_frames / 2));
  const opacity = fadeFrames <= 0
    ? 1
    : interpolate(frame, [0, fadeFrames, overlay.duration_in_frames - fadeFrames, overlay.duration_in_frames], [0, 1, 1, 0], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      });
  const style: React.CSSProperties = {
    position: "absolute",
    left: "8%",
    top: "12%",
    opacity,
    ...DEFAULT_OVERLAY_STYLE,
    ...overlay.style,
  };
  if (overlay.kind === "image" && overlay.src) {
    return <Img src={resolveAsset(overlay.src)} style={{ ...style, objectFit: "contain" }} />;
  }
  if (overlay.kind === "box") {
    return <div style={{ ...style, right: "8%", bottom: "12%", backgroundColor: "rgba(0,0,0,0.5)", borderRadius: 16 }} />;
  }
  return <div style={style}>{overlay.text ?? overlay.kind}</div>;
};

export const unwrapManifest = (props: EditorialProps): EditManifest => {
  if ("schema_version" in props) {
    return props;
  }
  return props.manifest;
};

export const EditorialComposition: React.FC<EditorialProps> = (props) => {
  const manifest = unwrapManifest(props);
  const timeline = buildTimeline(manifest);
  const aspect = manifest.aspect;
  const audioFrom = Math.max(0, Math.round(manifest.audio?.from ?? 0));
  const audioDuration = Math.max(
    1,
    Math.min(
      Math.round(manifest.audio?.duration_in_frames ?? manifest.duration_in_frames - audioFrom),
      Math.max(1, manifest.duration_in_frames - audioFrom),
    ),
  );
  return (
    <div style={{ backgroundColor: "#10141c", width: "100%", height: "100%", overflow: "hidden" }}>
      {timeline.map((clip) => (
        <Sequence
          key={clip.id}
          from={clip.from}
          durationInFrames={clip.duration_in_frames}
          premountFor={Math.max(1, Math.min(clip.from, 2 * manifest.fps))}
        >
          <ClipLayer clip={clip} />
        </Sequence>
      ))}
      {manifest.overlays.map((overlay) => (
        <Sequence
          key={overlay.id}
          from={overlay.from}
          durationInFrames={overlay.duration_in_frames}
          premountFor={Math.max(1, Math.min(overlay.from, manifest.fps))}
        >
          <OverlayLayerView overlay={overlay} />
        </Sequence>
      ))}
      {manifest.captions.map((caption) => (
        <Sequence
          key={caption.id}
          from={caption.from}
          durationInFrames={caption.duration_in_frames}
          premountFor={Math.max(1, Math.min(caption.from, manifest.fps))}
        >
          <CaptionLayerView caption={caption} aspect={aspect} />
        </Sequence>
      ))}
      {manifest.audio?.src ? (
        <Sequence from={audioFrom} durationInFrames={audioDuration} premountFor={Math.min(audioFrom, manifest.fps)}>
          <Audio src={resolveAsset(manifest.audio.src)} volume={manifest.audio.volume ?? 1} />
        </Sequence>
      ) : null}
    </div>
  );
};
