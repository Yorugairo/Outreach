import React from "react";
import { AbsoluteFill, Img, Sequence, interpolate, staticFile, useCurrentFrame } from "remotion";
import { KenBurnsAdapter } from "./remotionBits";
import { TransitionSeries, linearTiming } from "@remotion/transitions";
import { bookFlip } from "@remotion/transitions/book-flip";

export type KenBurnsEffectProofProps = Record<string, unknown>;

export const defaultKenBurnsEffectProofProps: KenBurnsEffectProofProps = {};

const PLATES = {
  memory: "current-bubble-five-minute-v1/memory-three-supports-v1.png",
  index: "current-bubble-fresh-60s-v1/index-fund-weighted-inflows-v2.png",
  evidence: "current-bubble-five-minute-v2/evidence-sp500-concentration-v1.svg",
} as const;

const WorldPlate: React.FC<{
  image: string;
  startFrame: number;
  durationInFrames: number;
  direction: "left" | "right" | "up" | "down";
  style?: React.CSSProperties;
}> = ({ image, startFrame, durationInFrames, direction, style }) => (
  <div style={{ width: 1920, height: 1080, overflow: "hidden", backgroundColor: "#06111a", ...style }}>
    <KenBurnsAdapter
      images={[image]}
      startFrame={startFrame}
      durationInFrames={durationInFrames}
      direction={direction}
      scaleFrom={1.01}
      scaleTo={1.055}
    />
  </div>
);

const StaticEvidence: React.FC = () => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, 12], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return (
    <div
      style={{
        position: "absolute",
        left: "50%",
        top: "48%",
        width: "42%",
        transform: "translate(-50%, -50%)",
        opacity,
        backgroundColor: "#f7f3e9",
        boxShadow: "0 20px 52px rgba(3, 10, 16, .38)",
      }}
    >
      <Img src={staticFile(PLATES.evidence)} style={{ width: "100%", display: "block" }} />
    </div>
  );
};

/**
 * 12-second visual proof:
 * local Ken Burns -> native 3D flip -> stable evidence.
 */
export const KenBurnsEffectProof: React.FC<KenBurnsEffectProofProps> = () => (
  <AbsoluteFill style={{ backgroundColor: "#06111a", overflow: "hidden" }}>
    <TransitionSeries>
      <TransitionSeries.Sequence durationInFrames={144}>
        <WorldPlate image={PLATES.memory} startFrame={0} durationInFrames={144} direction="right" />
      </TransitionSeries.Sequence>
      <TransitionSeries.Transition
        presentation={bookFlip({ direction: "from-right" })}
        timing={linearTiming({ durationInFrames: 20 })}
      />
      <TransitionSeries.Sequence durationInFrames={234}>
        <WorldPlate image={PLATES.index} startFrame={0} durationInFrames={234} direction="left" />
        <Sequence from={102} durationInFrames={132} premountFor={12}>
          <StaticEvidence />
        </Sequence>
      </TransitionSeries.Sequence>
    </TransitionSeries>
  </AbsoluteFill>
);
