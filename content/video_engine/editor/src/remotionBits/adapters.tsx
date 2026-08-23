import React from "react";
import { Img, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import {
  AnimatedCounter,
  AnimatedText,
  StaggeredMotion,
  TypeWriter,
} from "remotion-bits";
import type {
  BasicCounterProps,
  BasicTypewriterProps,
  BlurInProps,
  CardStackProps,
  FadeInProps,
  GridStaggerProps,
  KenBurnsProps,
  ListRevealProps,
  MosaicReframeProps,
  RemotionBitAssetMap,
  RemotionBitStyle,
  SlideFromLeftProps,
  WordByWordProps,
} from "./types";

const DEFAULT_TEXT = "Production motion";
const DEFAULT_LIST = ["Evidence", "Context", "Decision"] as const;
const DEFAULT_GRID = ["01", "02", "03", "04", "05", "06", "07", "08", "09"] as const;
const DEFAULT_CARDS = ["A", "B", "C", "D", "E"] as const;

const finite = (value: number | undefined, fallback: number): number =>
  typeof value === "number" && Number.isFinite(value) ? value : fallback;

const positiveFrames = (value: number | undefined, fallback: number): number =>
  Math.max(1, Math.round(finite(value, fallback)));

const clamp = (value: number, minimum: number, maximum: number): number =>
  Math.min(maximum, Math.max(minimum, value));

const shellStyle = (style: RemotionBitStyle | undefined): React.CSSProperties => ({
  width: "100%",
  height: "100%",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  ...style,
});

const textStyle = (
  style: RemotionBitStyle | undefined,
  color: string | undefined,
  fontSize: number | undefined,
): React.CSSProperties => ({
  color: color ?? "#f4f0e7",
  fontSize: fontSize ?? 64,
  fontFamily: "Inter, Arial, sans-serif",
  lineHeight: 1.1,
  ...style,
});

const motionFrames = (value: number | undefined, fps: number): number =>
  positiveFrames(value, Math.max(1, Math.round(fps)));

export const normalizeRemotionBitAsset = (source: string | undefined): string | undefined => {
  if (typeof source !== "string" || !source.trim()) return undefined;
  const normalized = source.replaceAll("\\", "/").trim();
  // The production console exposes only hash-checked, opaque IDs beneath this
  // loopback route.  Keep all other absolute/browser/network paths closed.
  if (/^\/media\/[A-Za-z0-9._~!$&'()*+,;=:@%\-]+$/.test(normalized)) {
    return normalized;
  }
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
  return staticFile(withoutPublic);
};

export const resolveRemotionBitAsset = (
  source: string | undefined,
  assetMap: RemotionBitAssetMap | undefined,
): string | undefined => {
  if (!source) return undefined;
  return normalizeRemotionBitAsset(assetMap?.[source] ?? source);
};

export const FadeInAdapter: React.FC<FadeInProps> = ({
  text = DEFAULT_TEXT,
  durationInFrames,
  style,
  color,
  fontSize,
}) => {
  const { fps } = useVideoConfig();
  const duration = motionFrames(durationInFrames, fps);
  return (
    <div style={shellStyle(style)}>
      <AnimatedText
        transition={{ opacity: [0, 1], frames: [0, duration], duration, easing: "easeOutCubic" }}
        style={textStyle(undefined, color, fontSize)}
      >
        {text}
      </AnimatedText>
    </div>
  );
};

export const BlurInAdapter: React.FC<BlurInProps> = ({
  text = DEFAULT_TEXT,
  blurAmount = 14,
  durationInFrames,
  style,
  color,
  fontSize,
}) => {
  const { fps } = useVideoConfig();
  const duration = motionFrames(durationInFrames, fps);
  return (
    <div style={shellStyle(style)}>
      <AnimatedText
        transition={{
          opacity: [0, 1],
          blur: [Math.max(0, blurAmount), 0],
          frames: [0, duration],
          duration,
          easing: "easeOutCubic",
        }}
        style={textStyle(undefined, color, fontSize)}
      >
        {text}
      </AnimatedText>
    </div>
  );
};

export const WordByWordAdapter: React.FC<WordByWordProps> = ({
  text = DEFAULT_TEXT,
  staggerFrames = 4,
  durationInFrames,
  style,
  color,
  fontSize,
}) => {
  const { fps } = useVideoConfig();
  const duration = motionFrames(durationInFrames, fps);
  return (
    <div style={shellStyle(style)}>
      <AnimatedText
        transition={{
          opacity: [0, 1],
          y: [18, 0],
          split: "word",
          splitStagger: Math.max(0, Math.round(staggerFrames)),
          frames: [0, duration],
          duration,
          easing: "easeOutCubic",
        }}
        style={textStyle(undefined, color, fontSize)}
      >
        {text}
      </AnimatedText>
    </div>
  );
};

export const SlideFromLeftAdapter: React.FC<SlideFromLeftProps> = ({
  text = DEFAULT_TEXT,
  distance = 160,
  durationInFrames,
  style,
  color,
  fontSize,
}) => {
  const { fps } = useVideoConfig();
  const duration = motionFrames(durationInFrames, fps);
  return (
    <div style={shellStyle(style)}>
      <AnimatedText
        transition={{
          opacity: [0, 1],
          x: [-Math.abs(distance), 0],
          frames: [0, duration],
          duration,
          easing: "easeOutCubic",
        }}
        style={textStyle(undefined, color, fontSize)}
      >
        {text}
      </AnimatedText>
    </div>
  );
};

export const BasicTypewriterAdapter: React.FC<BasicTypewriterProps> = ({
  text = "Frame-accurate type",
  typeSpeedFrames = 3,
  showCursor = true,
  style,
  color,
  fontSize,
}) => (
  <div style={shellStyle(style)}>
    <TypeWriter
      text={text}
      typeSpeed={Math.max(1, Math.round(typeSpeedFrames))}
      cursor={showCursor}
      transition={{ opacity: [0, 1], frames: [0, 1], duration: 1 }}
      style={textStyle(undefined, color, fontSize)}
    />
  </div>
);

export const BasicCounterAdapter: React.FC<BasicCounterProps> = ({
  from = 0,
  to = 100,
  prefix = "",
  postfix = "",
  decimals = 0,
  durationInFrames,
  style,
  color,
  fontSize,
}) => {
  const { fps } = useVideoConfig();
  const duration = motionFrames(durationInFrames, fps);
  return (
    <div style={shellStyle(style)}>
      <AnimatedCounter
        transition={{
          values: [from, to],
          frames: [0, duration],
          duration,
          easing: "easeInOutCubic",
        }}
        prefix={prefix}
        postfix={postfix}
        toFixed={Math.max(0, Math.round(decimals))}
        style={textStyle(undefined, color, fontSize)}
      />
    </div>
  );
};

export const ListRevealAdapter: React.FC<ListRevealProps> = ({
  items = DEFAULT_LIST,
  staggerFrames = 5,
  durationInFrames,
  style,
  color,
  fontSize,
  backgroundColor,
}) => {
  const { fps } = useVideoConfig();
  const duration = motionFrames(durationInFrames, fps);
  return (
    <div style={{ ...shellStyle(style), backgroundColor: backgroundColor ?? "#111827", padding: 40 }}>
      <StaggeredMotion
        transition={{
          opacity: [0, 1],
          y: [24, 0],
          frames: [0, duration],
          duration,
          stagger: Math.max(0, Math.round(staggerFrames)),
          easing: "easeOutCubic",
        }}
        style={{ display: "flex", flexDirection: "column", gap: 14, width: "min(80%, 720px)" }}
      >
        {items.map((item, index) => (
          <div
            key={`${index}-${item}`}
            style={{
              color: color ?? "#f4f0e7",
              fontSize: fontSize ?? 34,
              fontFamily: "Inter, Arial, sans-serif",
              padding: "18px 24px",
              borderRadius: 10,
              backgroundColor: "rgba(255,255,255,0.1)",
            }}
          >
            {item}
          </div>
        ))}
      </StaggeredMotion>
    </div>
  );
};

export const GridStaggerAdapter: React.FC<GridStaggerProps> = ({
  items = DEFAULT_GRID,
  columns = 3,
  staggerFrames = 3,
  durationInFrames,
  style,
  color,
  fontSize,
  backgroundColor,
}) => {
  const { fps } = useVideoConfig();
  const duration = motionFrames(durationInFrames, fps);
  const safeColumns = clamp(Math.round(columns), 1, 8);
  return (
    <div style={{ ...shellStyle(style), backgroundColor: backgroundColor ?? "#09090b", padding: 48 }}>
      <StaggeredMotion
        transition={{
          opacity: [0, 1],
          scale: [0.72, 1],
          frames: [0, duration],
          duration,
          stagger: Math.max(0, Math.round(staggerFrames)),
          staggerDirection: "center",
          easing: "easeOutCubic",
        }}
        style={{
          display: "grid",
          gridTemplateColumns: `repeat(${safeColumns}, minmax(0, 1fr))`,
          gap: 18,
          width: "min(86%, 840px)",
        }}
      >
        {items.map((item, index) => (
          <div
            key={`${index}-${item}`}
            style={{
              aspectRatio: "1",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: color ?? "#f4f0e7",
              fontSize: fontSize ?? 30,
              fontFamily: "Inter, Arial, sans-serif",
              borderRadius: 14,
              backgroundColor: index % 2 === 0 ? "#2563eb" : "#7c3aed",
            }}
          >
            {item}
          </div>
        ))}
      </StaggeredMotion>
    </div>
  );
};

type MosaicGeometry = { x: number; y: number; width: number; height: number; rotate: number };

const mosaicGeometry = (index: number, count: number, phase: "grid" | "feature" | "cascade"): MosaicGeometry => {
  const safeCount = Math.max(1, count);
  if (phase === "feature") {
    if (index === 0) return { x: 0, y: 0, width: 58, height: 58, rotate: 0 };
    const slot = index - 1;
    const column = slot % 3;
    const row = Math.floor(slot / 3);
    return { x: 60 + column * 13.5, y: row * 19.5, width: 12, height: 18, rotate: 0 };
  }
  if (phase === "cascade") {
    const offset = safeCount === 1 ? 0 : index / (safeCount - 1);
    return { x: offset * 68, y: offset * 68, width: 25, height: 25, rotate: -12 + index * 3 };
  }
  const columns = Math.min(4, safeCount);
  const rows = Math.ceil(safeCount / columns);
  const gap = 2;
  const width = (100 - gap * (columns - 1)) / columns;
  const height = (100 - gap * (rows - 1)) / rows;
  return {
    x: (index % columns) * (width + gap),
    y: Math.floor(index / columns) * (height + gap),
    width,
    height,
    rotate: 0,
  };
};

const blendGeometry = (a: MosaicGeometry, b: MosaicGeometry, progress: number): MosaicGeometry => ({
  x: a.x + (b.x - a.x) * progress,
  y: a.y + (b.y - a.y) * progress,
  width: a.width + (b.width - a.width) * progress,
  height: a.height + (b.height - a.height) * progress,
  rotate: a.rotate + (b.rotate - a.rotate) * progress,
});

const MosaicTile: React.FC<{
  index: number;
  count: number;
  source?: string;
  frame: number;
  fps: number;
}> = ({ index, count, source, frame, fps }) => {
  const first = mosaicGeometry(index, count, "grid");
  const second = mosaicGeometry(index, count, "feature");
  const third = mosaicGeometry(index, count, "cascade");
  const featureProgress = interpolate(frame, [Math.round(fps * 0.7), Math.round(fps * 1.35)], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: (value) => value * value * (3 - 2 * value),
  });
  const cascadeProgress = interpolate(frame, [Math.round(fps * 1.9), Math.round(fps * 2.5)], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: (value) => value * value * (3 - 2 * value),
  });
  const featureGeometry = blendGeometry(first, second, featureProgress);
  const geometry = blendGeometry(featureGeometry, third, cascadeProgress);
  const tileStyle: React.CSSProperties = {
    position: "absolute",
    left: `${geometry.x}%`,
    top: `${geometry.y}%`,
    width: `${geometry.width}%`,
    height: `${geometry.height}%`,
    transform: `rotate(${geometry.rotate}deg)`,
    borderRadius: 10,
    overflow: "hidden",
    backgroundColor: index % 2 === 0 ? "#14532d" : "#1d4ed8",
    boxShadow: "0 18px 34px rgba(0,0,0,0.28)",
  };
  return source ? (
    <div style={tileStyle}>
      <Img src={source} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
    </div>
  ) : (
    <div style={{ ...tileStyle, display: "flex", alignItems: "center", justifyContent: "center", color: "#fff", fontSize: 28 }}>
      {String(index + 1).padStart(2, "0")}
    </div>
  );
};

export const MosaicReframeAdapter: React.FC<MosaicReframeProps> = ({
  images,
  assetMap,
  tileCount = 12,
  style,
  backgroundColor,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const count = clamp(Math.round(tileCount), 1, 12);
  const sources = (images ?? []).slice(0, count).map((source) => resolveRemotionBitAsset(source, assetMap));
  return (
    <div style={{ ...shellStyle(style), backgroundColor: backgroundColor ?? "#09090b" }}>
      <div style={{ position: "relative", width: "78%", height: "78%" }}>
        {Array.from({ length: count }, (_, index) => (
          <MosaicTile key={index} index={index} count={count} source={sources[index]} frame={frame} fps={fps} />
        ))}
      </div>
    </div>
  );
};

export const CardStackAdapter: React.FC<CardStackProps> = ({
  cards = DEFAULT_CARDS,
  staggerFrames = 3,
  durationInFrames,
  style,
  color,
  fontSize,
  backgroundColor,
}) => {
  const { fps } = useVideoConfig();
  const duration = motionFrames(durationInFrames, fps);
  return (
    <div style={{ ...shellStyle(style), backgroundColor: backgroundColor ?? "#111827", perspective: 1200 }}>
      <StaggeredMotion
        transition={{
          opacity: [0, 1],
          y: [80, 0],
          frames: [0, duration],
          duration,
          stagger: Math.max(0, Math.round(staggerFrames)),
          easing: "easeOutCubic",
        }}
        style={{ position: "relative", width: "min(34%, 280px)", aspectRatio: "0.72", transformStyle: "preserve-3d" }}
      >
        {cards.map((card, index) => {
          const centered = index - (cards.length - 1) / 2;
          return (
            <div key={`${index}-${card}`} style={{ position: "absolute", inset: 0, transformStyle: "preserve-3d" }}>
              <div
                style={{
                  width: "100%",
                  height: "100%",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  color: color ?? "#fff",
                  fontSize: fontSize ?? 72,
                  fontFamily: "Inter, Arial, sans-serif",
                  backgroundColor: index % 2 === 0 ? "#f59e0b" : "#7c2d12",
                  border: "4px solid rgba(255,255,255,0.18)",
                  borderRadius: 24,
                  boxShadow: "0 25px 50px rgba(0,0,0,0.42)",
                  transform: `translateX(${centered * 34}px) translateZ(${index * -18}px) rotateZ(${centered * 7}deg) rotateY(${centered * -4}deg)`,
                }}
              >
                {card}
              </div>
            </div>
          );
        })}
      </StaggeredMotion>
    </div>
  );
};

export const KenBurnsAdapter: React.FC<KenBurnsProps> = ({
  images,
  assetMap,
  startFrame = 0,
  scaleFrom = 1.08,
  scaleTo = 1.2,
  direction = "right",
  durationInFrames,
  style,
  backgroundColor,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const duration = motionFrames(durationInFrames, fps);
  const localFrame = Math.max(0, frame - Math.round(startFrame));
  const sources = (images ?? []).map((source) => resolveRemotionBitAsset(source, assetMap)).filter(
    (source): source is string => Boolean(source),
  );
  const imageIndex = sources.length
    ? Math.min(sources.length - 1, Math.floor((localFrame / duration) * sources.length))
    : -1;
  const source = imageIndex >= 0 ? sources[imageIndex] : undefined;
  const progress = interpolate(localFrame, [0, duration], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const shift = (progress - 0.5) * 5;
  const x = direction === "left" ? -shift : direction === "right" ? shift : 0;
  const y = direction === "up" ? -shift : direction === "down" ? shift : 0;
  const imageStyle: React.CSSProperties = {
    position: "absolute",
    inset: -5,
    width: "110%",
    height: "110%",
    objectFit: "cover",
    transform: `scale(${interpolate(progress, [0, 1], [scaleFrom, scaleTo])}) translate(${x}%, ${y}%)`,
  };
  return (
    <div style={{ ...shellStyle(style), backgroundColor: backgroundColor ?? "#030712", overflow: "hidden" }}>
      {source ? (
        <Img src={source} style={imageStyle} />
      ) : (
        <div style={{ width: "100%", height: "100%", background: "linear-gradient(135deg, #1e3a8a, #111827)" }} />
      )}
    </div>
  );
};
