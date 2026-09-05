import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig, Easing } from "remotion";
import data from "../yen-evidence.json";

// Brand evidence register: near-black instrument dropped onto the paper world, near-white
// type, tabular monospace numerals, coral = alarm. The line DRAWS (a state change), then
// the Aug 5 marker and the Nikkei bar land. Source line always printed. Alpha elsewhere.
const G = "#1B1E23", INK = "#F2F2F2", CORAL = "#ED6A4A", TEAL = "#178C83", DIM = "rgba(242,242,242,0.55)";
const ease = Easing.bezier(0.215, 0.61, 0.355, 1);

export const YenChart: React.FC<{ x: number; y: number; w: number; h: number }> = ({ x, y, w, h }) => {
  const frame = useCurrentFrame(); const { fps } = useVideoConfig(); const t = frame / fps;
  const pts: [string, number][] = data.usdjpy as any;
  const vals = pts.map(p => p[1]); const lo = Math.min(...vals) - 1, hi = Math.max(...vals) + 1;
  const padL = 96, padR = 40, padT = 92, padB = 78;
  const cw = w - padL - padR, ch = h - padT - padB;
  const X = (i: number) => padL + (i / (pts.length - 1)) * cw;
  const Y = (v: number) => padT + (1 - (v - lo) / (hi - lo)) * ch;
  const enter = interpolate(t, [0, 0.35], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: ease });
  const draw  = interpolate(t, [0.3, 2.6], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.inOut(Easing.quad) });
  const iAug5 = pts.findIndex(p => p[0] === "2024-08-05"); const iPeak = vals.indexOf(Math.max(...vals));
  const mark  = interpolate(t, [2.7, 3.1], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: ease });
  const bar   = interpolate(t, [3.2, 3.8], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: ease });
  const n = Math.max(2, Math.round(draw * pts.length));
  const path = pts.slice(0, n).map((p, i) => `${i === 0 ? "M" : "L"}${X(i).toFixed(1)},${Y(p[1]).toFixed(1)}`).join(" ");
  const mono = "Consolas, ui-monospace, monospace", sans = "Inter, 'Segoe UI', Arial, sans-serif";
  return (
    <AbsoluteFill style={{ backgroundColor: "transparent" }}>
      <div style={{ position: "absolute", left: x, top: y, width: w, height: h, background: G, borderRadius: 6,
        opacity: enter, transform: `translateY(${(1 - enter) * 14}px)`, boxShadow: "0 8px 30px rgba(37,49,60,0.25)" }}>
        <div style={{ position: "absolute", left: padL, top: 26, color: INK, fontFamily: sans, fontWeight: 800, fontSize: 30, letterSpacing: "0.01em" }}>USD / JPY · summer 2024</div>
        <div style={{ position: "absolute", left: padL, top: 60, color: DIM, fontFamily: sans, fontSize: 20 }}>dollars per yen falling = yen getting stronger</div>
        <svg width={w} height={h} style={{ position: "absolute", inset: 0 }}>
          {[lo + 2, (lo + hi) / 2, hi - 2].map((v, i) => (
            <g key={i}><line x1={padL} x2={w - padR} y1={Y(v)} y2={Y(v)} stroke="rgba(242,242,242,0.12)" strokeWidth={1} />
              <text x={padL - 12} y={Y(v) + 7} fill={DIM} fontFamily={mono} fontSize={20} textAnchor="end">{v.toFixed(0)}</text></g>))}
          <path d={path} fill="none" stroke={CORAL} strokeWidth={4.5} strokeLinecap="round" strokeLinejoin="round" />
          {mark > 0 && iAug5 >= 0 && <>
            <line x1={X(iAug5)} x2={X(iAug5)} y1={padT} y2={h - padB} stroke={CORAL} strokeWidth={1.5} strokeDasharray="4 5" opacity={mark} />
            <circle cx={X(iAug5)} cy={Y(vals[iAug5])} r={9 * mark} fill={CORAL} />
            <circle cx={X(iPeak)} cy={Y(vals[iPeak])} r={6 * mark} fill={INK} />
            <text x={X(iPeak) + 12} y={Y(vals[iPeak]) - 10} fill={INK} fontFamily={mono} fontSize={22} opacity={mark}>{vals[iPeak].toFixed(1)}</text>
            <text x={X(iAug5) - 12} y={Y(vals[iAug5]) + 36} fill={CORAL} fontFamily={mono} fontSize={26} fontWeight={700} textAnchor="end" opacity={mark}>{vals[iAug5].toFixed(1)}</text>
            <text x={X(iAug5) - 12} y={Y(vals[iAug5]) + 62} fill={DIM} fontFamily={sans} fontSize={19} textAnchor="end" opacity={mark}>Aug 5</text>
          </>}
          {[0, Math.floor((pts.length - 1) / 2), pts.length - 1].map(i => (
            <text key={i} x={X(i)} y={h - padB + 30} fill={DIM} fontFamily={sans} fontSize={19} textAnchor={i === 0 ? "start" : i === pts.length - 1 ? "end" : "middle"}>{pts[i][0].slice(5).replace("-", "/")}</text>))}
        </svg>
        {bar > 0 && <div style={{ position: "absolute", right: padR, top: 26, opacity: bar, transform: `translateY(${(1 - bar) * 8}px)`, textAlign: "right" }}>
          <div style={{ color: DIM, fontFamily: sans, fontSize: 19 }}>Nikkei 225, Aug 5</div>
          <div style={{ color: CORAL, fontFamily: mono, fontSize: 44, fontWeight: 700, lineHeight: 1 }}>−12.4%</div>
          <div style={{ color: DIM, fontFamily: sans, fontSize: 17 }}>one day</div>
        </div>}
        <div style={{ position: "absolute", left: padL, bottom: 18, color: "rgba(242,242,242,0.45)", fontFamily: sans, fontSize: 17 }}>Source: FRED — DEXJPUS (Board of Governors), NIKKEI225 (Nikkei Inc.)</div>
      </div>
    </AbsoluteFill>
  );
};
