import React from "react";
import { AbsoluteFill, Img, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

export type ProductionEvidenceCompositionProps = {
  assetUrl: string;
  sceneTitle: string;
  assetLabel: string;
  approvalLabel: string;
};

export const defaultProductionEvidenceProps: ProductionEvidenceCompositionProps = {
  assetUrl: "data:image/svg+xml;charset=utf-8,%3Csvg xmlns='http://www.w3.org/2000/svg' width='1376' height='768'%3E%3Crect width='100%25' height='100%25' fill='%23f4f0e7'/%3E%3C/svg%3E",
  sceneTitle: "Production Evidence",
  assetLabel: "Supply an approved production visual",
  approvalLabel: "Production visual",
};

export const ProductionEvidenceComposition: React.FC<ProductionEvidenceCompositionProps> = ({
  assetUrl,
  sceneTitle,
  assetLabel,
  approvalLabel,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const enter = spring({ frame, fps, durationInFrames: Math.round(fps * 0.55), config: { damping: 200 } });
  const drift = interpolate(frame, [0, fps * 8], [1.02, 1.045], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ backgroundColor: "#0d120f", color: "#f5f0e6", fontFamily: "Arial, sans-serif", overflow: "hidden" }}>
      <Img src={assetUrl} style={{ position: "absolute", inset: -70, width: "calc(100% + 140px)", height: "calc(100% + 140px)", objectFit: "cover", filter: "blur(38px) saturate(.45) brightness(.34)", transform: `scale(${drift})` }} />
      <AbsoluteFill style={{ background: "linear-gradient(105deg, rgba(7,13,10,.94) 0%, rgba(7,13,10,.38) 42%, rgba(7,13,10,.7) 100%)" }} />
      <div style={{ position: "absolute", left: 66, top: 54, display: "flex", alignItems: "center", gap: 14, letterSpacing: 2.2, textTransform: "uppercase", fontSize: 17, fontWeight: 800 }}>
        <span style={{ width: 38, height: 4, background: "#c8944f" }} />
        {sceneTitle}
      </div>
      <div style={{ position: "absolute", left: 118, right: 118, top: 132, bottom: 86, border: "1px solid rgba(228,200,153,.58)", borderRadius: 8, padding: 12, background: "rgba(249,246,238,.97)", boxShadow: "0 30px 80px rgba(0,0,0,.48)", transform: `translateY(${(1 - enter) * 34}px) scale(${0.975 + enter * 0.025})`, opacity: enter }}>
        <Img src={assetUrl} style={{ width: "100%", height: "100%", objectFit: "contain" }} />
      </div>
      <div style={{ position: "absolute", left: 66, bottom: 38, color: "#d8cab2", fontSize: 15, letterSpacing: 0.2 }}>{assetLabel}</div>
      <div style={{ position: "absolute", right: 66, bottom: 31, border: "1px solid rgba(72,177,121,.62)", background: "rgba(19,70,48,.72)", color: "#adf0c8", padding: "8px 12px", borderRadius: 4, fontWeight: 800, fontSize: 12, letterSpacing: 1.1, textTransform: "uppercase" }}>{approvalLabel}</div>
    </AbsoluteFill>
  );
};
