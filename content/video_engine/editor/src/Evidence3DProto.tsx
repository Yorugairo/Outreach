/**
 * E2 prototype — Transform3D motion controls for the evidence layer.
 *
 * Two treatments under doc 29's motion_rule (every move encodes a fact):
 *  - EvidenceCarousel3D: a rapid evidence list as a Z-stacked rail; the
 *    camera STEP is the enumeration — one step per exhibit, badges land
 *    on arrival, passed exhibits recede (demotion = literal Z recession).
 *  - LongPlateOrbit: a long hold carried by a slow quaternion micro-orbit
 *    plus parallax instead of a static ken-burns; amplitude stays inside
 *    the "1% focal push" spirit (max ~2.5deg, no fake-3D blur).
 */
import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { Scene3D, Element3D } from "remotion-bits";

const CREAM = "#F4E6C7";
const CHARCOAL = "#25313C";
const COBALT = "#1769C2";
const TEAL = "#178C83";
const SUNFLOWER = "#F5B72E";
const CORAL = "#ED6A4A";

const EXHIBITS = [
  { title: "RAILWAY STOCKS", figure: "+100%", tag: "IN 3 YEARS", accent: SUNFLOWER },
  { title: "SHARE OF GDP", figure: "8%", tag: "PAST THE 7% LINE", accent: CORAL },
  { title: "THE RATE TRIGGER", figure: "6.5%", tag: "FED, 2000", accent: COBALT },
  { title: "AI DEBT, 2026 YTD", figure: "$244B", tag: "AND RISING", accent: CORAL },
  { title: "HBM CAPACITY", figure: "100%", tag: "COMMITTED THRU 2027", accent: TEAL },
];

const STEP_FRAMES = 42; // 1.4s per exhibit @30fps: land, read, step

const Doc: React.FC<{ e: (typeof EXHIBITS)[number]; lit: number }> = ({ e, lit }) => (
  <div
    style={{
      width: 620,
      height: 400,
      background: CREAM,
      border: `3.5px solid ${CHARCOAL}`,
      borderRadius: 14,
      boxShadow: `14px 14px 0px ${CHARCOAL}`,
      padding: "34px 40px",
      filter: `brightness(${0.72 + 0.28 * lit})`,
      display: "flex",
      flexDirection: "column",
      justifyContent: "space-between",
      fontFamily: "Inter, Arial, sans-serif",
    }}
  >
    <div style={{ fontSize: 30, fontWeight: 800, color: CHARCOAL }}>{e.title}</div>
    <div style={{ fontSize: 110, fontWeight: 800, color: e.accent, lineHeight: 1 }}>
      {e.figure}
    </div>
    <div style={{ fontSize: 22, fontWeight: 700, color: CHARCOAL, opacity: 0.75 }}>
      {e.tag}
    </div>
  </div>
);

export const EvidenceCarousel3D: React.FC = () => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();
  const progress = frame / STEP_FRAMES; // exhibit index, fractional
  const cameraX = interpolate(progress, [0, EXHIBITS.length - 1], [0, (EXHIBITS.length - 1) * 700]);

  return (
    <AbsoluteFill style={{ background: CHARCOAL }}>
      <Scene3D width={width} height={height} perspective={1600}>
        {EXHIBITS.map((e, i) => {
          const arrive = i * STEP_FRAMES;
          const landed = interpolate(frame, [arrive - 16, arrive], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          });
          const passed = Math.max(0, Math.min(1, progress - i));
          const lit = landed * (1 - 0.6 * passed);
          return (
            <Element3D
              key={e.title}
              transform={{
                translate: [
                  i * 700 - cameraX,
                  40 * (1 - landed),
                  -900 * (1 - landed) - 420 * passed,
                ],
                rotate: [0, (1 - landed) * -28 + passed * 14, 0],
                scale: 1 - 0.12 * passed,
              }}
              style={{ opacity: Math.max(landed, 0.001) }}
            >
              <Doc e={e} lit={lit} />
            </Element3D>
          );
        })}
      </Scene3D>
    </AbsoluteFill>
  );
};

export const LongPlateOrbit: React.FC<{ src?: string }> = ({ src }) => {
  const frame = useCurrentFrame();
  const { durationInFrames, width, height } = useVideoConfig();
  const t = frame / durationInFrames;
  const yaw = Math.sin(t * Math.PI * 2) * 2.2;
  const pitch = Math.cos(t * Math.PI * 2) * 1.2;
  const push = interpolate(t, [0, 1], [0, 60]);

  return (
    <AbsoluteFill style={{ background: "#04090e" }}>
      <Scene3D width={width} height={height} perspective={2200}>
        <Element3D
          transform={{ translate: [0, 0, push], rotate: [pitch, yaw, 0], scale: 1.08 }}
        >
          {src ? (
            <img src={src} width={width} height={height} style={{ objectFit: "cover" }} />
          ) : (
            <div
              style={{
                width,
                height,
                background: `linear-gradient(135deg, ${CHARCOAL}, #0a1620 70%)`,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: CREAM,
                fontFamily: "Inter, Arial, sans-serif",
                fontSize: 44,
                fontWeight: 700,
              }}
            >
              world plate stand-in — slow quaternion micro-orbit
            </div>
          )}
        </Element3D>
      </Scene3D>
    </AbsoluteFill>
  );
};
