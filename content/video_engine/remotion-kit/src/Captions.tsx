import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig, Easing } from "remotion";
type Tok = { w: string; kw: boolean }; type Grp = { start: number; end: number; tokens: Tok[] };
// doc 29 Part 5: one fixed anchor, transparent glyphs + shadow, no pill; groups punch in
// scale 1.14->1.0, y 12->0, power3.out. Ink dark for cream paper; accent = woodblock red.
const power3out = Easing.bezier(0.215, 0.61, 0.355, 1);
export const Captions: React.FC<{ groups: Grp[]; ink: string; accent: string; anchorY: number; fontSize: number }> =
({ groups, ink, accent, anchorY, fontSize }) => {
  const frame = useCurrentFrame(); const { fps } = useVideoConfig(); const t = frame / fps;
  const g = groups.find(x => t >= x.start && t < x.end); if (!g) return null;
  const p = interpolate(t - g.start, [0, 0.30], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: power3out });
  const scale = interpolate(p, [0, 1], [1.14, 1]); const y = interpolate(p, [0, 1], [12, 0]);
  return (
    <AbsoluteFill style={{ backgroundColor: "transparent" }}>
      <div style={{ position: "absolute", left: 60, right: 60, top: anchorY, transform: `translateY(${y}px) scale(${scale})`,
        transformOrigin: "50% 50%", opacity: p, textAlign: "center", fontFamily: "Inter, 'Segoe UI', Arial, sans-serif",
        fontWeight: 700, fontSize, lineHeight: 1.15, color: ink, letterSpacing: "-0.01em",
        WebkitTextStroke: "5px #F4E6C7", paintOrder: "stroke fill",
        textShadow: "0 0 6px rgba(244,230,199,1), 0 2px 14px rgba(244,230,199,0.95), 0 0 28px rgba(244,230,199,0.85)" }}>
        {g.tokens.map((tok, i) => <span key={i} style={{ color: tok.kw ? accent : ink }}>{tok.w}{i < g.tokens.length - 1 ? " " : ""}</span>)}
      </div>
    </AbsoluteFill>
  );
};
