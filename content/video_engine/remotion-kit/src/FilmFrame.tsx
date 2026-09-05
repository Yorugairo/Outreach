import React, { useMemo } from "react";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
// Persistent film apparatus (from MotionKit "Film Burn Intro", title + burn removed): sprocket strips,
// grain, scratches, faint flicker. Runs the whole length as an ALPHA layer over the picture.
const seeded = (s: number) => { const x = Math.sin(s * 3141.592) * 43758.5453; return x - Math.floor(x); };
export const FilmFrame: React.FC<{ strip: string; hole: string; scratch: string; grain: number; scratchIntensity: number; stripH: number }> =
({ strip, hole, scratch, grain, scratchIntensity, stripH }) => {
  const frame = useCurrentFrame(); const { width, height, durationInFrames } = useVideoConfig();
  const holes = Array.from({ length: 12 });
  const scratches = useMemo(() => Array.from({ length: 48 }, (_, i) => ({
    x: seeded(i * 1.7) * 100, delay: Math.floor(seeded(i * 3.1) * durationInFrames), len: 120 + seeded(i * 5.3) * 500,
    op: 0.10 + seeded(i * 7.9) * 0.25, w: 1 + seeded(i * 9.1) * 1.5, rot: (seeded(i * 11.3) - 0.5) * 4 })), [durationInFrames]);
  const flicker = seeded(frame * 13.7) > 0.93 ? 0.04 : 0;
  const Strip = ({ top }: { top: boolean }) => (
    <div style={{ position: "absolute", left: 0, right: 0, [top ? "top" : "bottom"]: 0, height: stripH, backgroundColor: strip,
      display: "flex", alignItems: "center", justifyContent: "space-around" }}>
      {holes.map((_, i) => <div key={i} style={{ width: 34, height: 22, backgroundColor: hole, borderRadius: 4, opacity: 0.92 }} />)}
    </div>);
  return (
    <AbsoluteFill style={{ backgroundColor: "transparent", overflow: "hidden" }}>
      <Strip top /><Strip top={false} />
      {scratches.map((s, i) => { const f = frame - s.delay; if (f < 0 || f > 9) return null;
        const o = s.op * scratchIntensity * interpolate(f, [0, 3, 9], [0, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
        return <div key={i} style={{ position: "absolute", left: `${s.x}%`, top: stripH + seeded(i * 2.2) * (height - 2 * stripH - s.len),
          width: s.w, height: s.len, backgroundColor: scratch, opacity: o, transform: `rotate(${s.rot}deg)` }} />; })}
      <AbsoluteFill style={{ top: stripH, bottom: stripH, opacity: grain, mixBlendMode: "overlay", pointerEvents: "none",
        backgroundImage: `url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='300' height='300'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='3' stitchTiles='stitch' seed='${frame % 7}'/></filter><rect width='300' height='300' filter='url(%23n)'/></svg>")`,
        backgroundSize: "300px 300px" }} />
      <AbsoluteFill style={{ backgroundColor: "#000", opacity: flicker, pointerEvents: "none" }} />
    </AbsoluteFill>);
};
