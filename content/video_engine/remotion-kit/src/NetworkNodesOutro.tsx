import React, { useMemo } from "react";
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

const seeded = (seed: number) => {
  const x = Math.sin(seed * 9999.123) * 43758.5453;
  return x - Math.floor(x);
};

function hexToRgba(hex: string, alpha: number): string {
  const clean = hex.replace("#", "").trim();
  const full =
    clean.length === 3 ? clean.split("").map((c) => c + c).join("") : clean;
  const int = parseInt(full, 16) || 0;
  const r = (int >> 16) & 255;
  const g = (int >> 8) & 255;
  const b = int & 255;
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

type Node = {
  x: number;
  y: number;
  size: number;
  speed: number;
  phase: number;
  drift: number;
  pulseSpeed: number;
};

type Ember = {
  x: number;
  y: number;
  size: number;
  speed: number;
  phase: number;
  sway: number;
};

const NODE_COUNT = 38;
const EMBER_COUNT = 10;
// tuned for the 1080x1920 canvas (original 220 was set against 1920x1080)
const CONNECTION_DISTANCE = 260;

export const NetworkNodesOutro: React.FC<{
  headline: string;
  tagline: string;
  showHandle: boolean;
  handle: string;
  nodeColor: string;
  textColor: string;
  backgroundColor: string;
  accentWord?: string;
  accentColor?: string;
  glow?: number;
}> = ({
  headline,
  tagline,
  showHandle,
  handle,
  nodeColor,
  textColor,
  backgroundColor,
  accentWord = "",
  accentColor = "#ED6A4A",
  glow = 0.18,
}) => {
  const frame = useCurrentFrame();
  const { fps, width, height, durationInFrames } = useVideoConfig();
  const t = frame / fps;

  const nodes = useMemo<Node[]>(() => {
    const arr: Node[] = [];
    for (let i = 0; i < NODE_COUNT; i++) {
      arr.push({
        x: seeded(i * 1.1) * 100,
        y: seeded(i * 2.3) * 100,
        size: 2 + seeded(i * 3.7) * 4,
        speed: 0.2 + seeded(i * 4.1) * 0.5,
        phase: seeded(i * 5.3) * Math.PI * 2,
        drift: 6 + seeded(i * 6.7) * 14,
        pulseSpeed: 0.4 + seeded(i * 7.9) * 1.2,
      });
    }
    return arr;
  }, []);

  const embers = useMemo<Ember[]>(() => {
    const arr: Ember[] = [];
    for (let i = 0; i < EMBER_COUNT; i++) {
      arr.push({
        x: seeded(i * 11.3 + 50) * 100,
        y: seeded(i * 12.7 + 50) * 100,
        size: 2 + seeded(i * 13.1 + 50) * 3,
        speed: 4 + seeded(i * 14.5 + 50) * 6,
        phase: seeded(i * 15.9 + 50) * Math.PI * 2,
        sway: 10 + seeded(i * 16.3 + 50) * 20,
      });
    }
    return arr;
  }, []);

  const positionedNodes = nodes.map((n) => {
    const dx = Math.sin(t * n.speed + n.phase) * n.drift;
    const dy = Math.cos(t * n.speed * 0.7 + n.phase * 1.3) * n.drift * 0.7;
    const x = (n.x + dx + 100) % 100;
    const y = (n.y + dy + 100) % 100;
    const pulse = 0.4 + 0.6 * (0.5 + 0.5 * Math.sin(t * n.pulseSpeed + n.phase));
    return { ...n, x, y, pulse };
  });

  const positionedEmbers = embers.map((e) => {
    const travel = (t * e.speed) % 130;
    const y = (e.y - travel + 130) % 130;
    const x = e.x + Math.sin(t * 0.6 + e.phase) * (e.sway / width) * 100;
    const opacity = 0.15 + 0.45 * (0.5 + 0.5 * Math.sin(t * 1.2 + e.phase));
    return { ...e, x, y, opacity };
  });

  const sceneFade = interpolate(
    frame,
    [durationInFrames - 25, durationInFrames],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  const headlineSpring = spring({
    frame,
    fps,
    config: { damping: 16, stiffness: 90, mass: 0.8 },
    durationInFrames: 22,
  });
  const headlineOpacity = interpolate(headlineSpring, [0, 1], [0, 1]);
  const headlineScale = interpolate(headlineSpring, [0, 1], [0.85, 1]);

  const taglineSpring = spring({
    frame: frame - 8,
    fps,
    config: { damping: 16, stiffness: 90, mass: 0.8 },
    durationInFrames: 22,
  });
  const taglineOpacity = interpolate(taglineSpring, [0, 1], [0, 1]);
  const taglineY = interpolate(taglineSpring, [0, 1], [16, 0]);

  const handleSpring = spring({
    frame: frame - 16,
    fps,
    config: { damping: 16, stiffness: 90, mass: 0.8 },
    durationInFrames: 22,
  });
  const handleOpacity = interpolate(handleSpring, [0, 1], [0, 1]);
  const handleScale = interpolate(handleSpring, [0, 1], [0.85, 1]);

  return (
    <AbsoluteFill
      style={{ backgroundColor, overflow: "hidden", opacity: sceneFade }}
    >
      <svg
        width={width}
        height={height}
        style={{ position: "absolute", inset: 0, pointerEvents: "none" }}
      >
        {positionedNodes.map((a, i) =>
          positionedNodes.slice(i + 1).map((b, j) => {
            const ax = (a.x / 100) * width;
            const ay = (a.y / 100) * height;
            const bx = (b.x / 100) * width;
            const by = (b.y / 100) * height;
            const dist = Math.hypot(ax - bx, ay - by);
            if (dist > CONNECTION_DISTANCE) return null;
            const opacity = (1 - dist / CONNECTION_DISTANCE) * 0.2;
            return (
              <line
                key={`${i}-${j}`}
                x1={ax}
                y1={ay}
                x2={bx}
                y2={by}
                stroke={nodeColor}
                strokeWidth={1}
                opacity={opacity}
              />
            );
          })
        )}
      </svg>

      {positionedNodes.map((n, i) => (
        <div
          key={i}
          style={{
            position: "absolute",
            left: `${n.x}%`,
            top: `${n.y}%`,
            width: n.size,
            height: n.size,
            backgroundColor: nodeColor,
            borderRadius: "50%",
            transform: "translate(-50%, -50%)",
            opacity: n.pulse,
            boxShadow: `0 0 ${n.size * 3}px ${n.size}px ${hexToRgba(nodeColor, 0.5 * glow / 0.18)}`,
          }}
        />
      ))}

      {positionedEmbers.map((e, i) => (
        <div
          key={i}
          style={{
            position: "absolute",
            left: `${e.x}%`,
            top: `${e.y}%`,
            width: e.size,
            height: e.size,
            backgroundColor: nodeColor,
            borderRadius: "50%",
            transform: "translate(-50%, -50%)",
            opacity: e.opacity,
            boxShadow: `0 0 ${e.size * 4}px ${e.size * 1.5}px ${hexToRgba(nodeColor, 0.6 * glow / 0.18)}`,
            filter: "blur(0.5px)",
          }}
        />
      ))}

      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
        <div
          style={{
            position: "absolute",
            width: 900,
            height: 900,
            borderRadius: "50%",
            backgroundColor: nodeColor,
            opacity: glow,
            filter: "blur(160px)",
            mixBlendMode: "screen",
          }}
        />

        <div
          style={{
            position: "relative",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            gap: 26,
            padding: "0 80px",
          }}
        >
          <div
            style={{
              color: textColor,
              fontSize: 84,
              fontWeight: 700,
              fontFamily: "'Inter', system-ui, sans-serif",
              letterSpacing: "-0.02em",
              textAlign: "center",
              lineHeight: 1.1,
              whiteSpace: "pre-line",
              opacity: headlineOpacity,
              transform: `scale(${headlineScale})`,
            }}
          >
            {headline.split(/(\s+)/).map((part, i) =>
              accentWord && part.replace(/[^\w]/g, "").toLowerCase() === accentWord.toLowerCase()
                ? <span key={i} style={{ color: accentColor }}>{part}</span> : <React.Fragment key={i}>{part}</React.Fragment>)}
          </div>

          <div
            style={{
              color: hexToRgba(textColor, 0.6),
              fontSize: 34,
              fontWeight: 500,
              fontFamily: "'Inter', system-ui, sans-serif",
              textAlign: "center",
              opacity: taglineOpacity,
              transform: `translateY(${taglineY}px)`,
            }}
          >
            {tagline}
          </div>

          {showHandle && (
            <div
              style={{
                marginTop: 22,
                padding: "16px 44px",
                borderRadius: 999,
                border: `1px solid ${hexToRgba(nodeColor, 0.4)}`,
                backgroundColor: hexToRgba(nodeColor, 0.1),
                opacity: handleOpacity,
                transform: `scale(${handleScale})`,
              }}
            >
              <span
                style={{
                  color: nodeColor,
                  fontSize: 34,
                  fontWeight: 600,
                  fontFamily: "'Inter', system-ui, sans-serif",
                  letterSpacing: "0.02em",
                }}
              >
                {handle}
              </span>
            </div>
          )}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
