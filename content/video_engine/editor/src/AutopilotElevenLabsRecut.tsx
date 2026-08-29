import React from "react";
import { AbsoluteFill, Audio, interpolate, Sequence, staticFile, useCurrentFrame } from "remotion";
import { Video } from "@remotion/media";
import { BasicCounterAdapter, BasicTypewriterAdapter, KenBurnsAdapter, WordByWordAdapter } from "./remotionBits";

export type AutopilotVisualRange = {
  readonly id: string;
  readonly target_start: number;
  readonly target_end: number;
  readonly source_start: number;
  readonly source_end: number;
  readonly mode: "ken_burns_still" | "video";
};

export type AutopilotCaptionCue = {
  readonly id: string;
  readonly start: number;
  readonly end: number;
  readonly text: string;
};

export type AutopilotCounterCallout = {
  readonly id: string;
  readonly start: number;
  readonly end: number;
  readonly from: number;
  readonly to: number;
  readonly prefix?: string;
  readonly postfix?: string;
  readonly label: string;
  readonly side: "left" | "right";
};

export type AutopilotElevenLabsRecutProps = {
  readonly schema_version?: string;
  readonly fps: number;
  readonly width: number;
  readonly height: number;
  readonly durationInFrames: number;
  readonly visualTrack: string;
  readonly narrationAudio: string;
  readonly marketContextStill: string;
  readonly kenBurnsRanges: readonly AutopilotVisualRange[];
  readonly captionCues: readonly AutopilotCaptionCue[];
  readonly callouts: readonly AutopilotCounterCallout[];
};

export const defaultAutopilotElevenLabsRecutProps: AutopilotElevenLabsRecutProps = {
  fps: 24,
  width: 1920,
  height: 1080,
  durationInFrames: 1,
  visualTrack: "autopilot-elevenlabs-recut-v1/retimed-visual-track.mp4",
  narrationAudio: "autopilot-elevenlabs-recut-v1/elevenlabs-narration.mp3",
  marketContextStill: "autopilot-elevenlabs-recut-v1/market-context-still.png",
  kenBurnsRanges: [],
  captionCues: [],
  callouts: [],
};

const frames = (seconds: number, fps: number) => Math.max(1, Math.round(seconds * fps));

const CaptionCue: React.FC<{ cue: AutopilotCaptionCue; fps: number }> = ({ cue, fps }) => {
  const revealDuration = Math.min(frames(cue.end - cue.start, fps), Math.max(10, cue.text.split(/\s+/).length * 3));
  return (
    <div
      style={{
        position: "absolute",
        left: "8%",
        right: "8%",
        bottom: "4.5%",
        height: 74,
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        whiteSpace: "nowrap",
      }}
    >
      <WordByWordAdapter
        text={cue.text}
        staggerFrames={2}
        durationInFrames={revealDuration}
        color="#fffaf0"
        fontSize={38}
        style={{
          width: "100%",
          textAlign: "center",
          fontWeight: 720,
          letterSpacing: 0.2,
          textShadow: "0 2px 5px rgba(0,0,0,.72)",
        }}
      />
    </div>
  );
};

/**
 * The Bits Ken Burns component is image-only. Apply its camera grammar to the
 * video as one continuous move across the whole cut—not a reset for every
 * sentence range—so a shared source shot never appears to jump in place.
 */
const MovingVisualTrack: React.FC<{
  src: string;
  durationInFrames: number;
}> = ({ src, durationInFrames }) => {
  const frame = useCurrentFrame();
  const progress = interpolate(frame, [0, Math.max(1, durationInFrames - 1)], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const x = interpolate(progress, [0, 1], [-0.35, 0.35]);
  const y = interpolate(progress, [0, 1], [0.18, -0.18]);
  const scale = interpolate(progress, [0, 1], [1.012, 1.045]);
  return (
    <div
      style={{
        position: "absolute",
        inset: -16,
        transform: `scale(${scale}) translate(${x}%, ${y}%)`,
        transformOrigin: "center center",
      }}
    >
      <Video src={staticFile(src)} muted objectFit="cover" style={{ width: "100%", height: "100%" }} />
    </div>
  );
};

const CounterCallout: React.FC<{ callout: AutopilotCounterCallout; fps: number }> = ({ callout, fps }) => {
  const frame = useCurrentFrame();
  const durationInFrames = frames(callout.end - callout.start, fps);
  const inFrames = Math.min(10, Math.max(1, Math.round(fps / 2)));
  const opacity = Math.min(1, Math.max(0, frame / inFrames));
  const sideStyle = callout.side === "left" ? { left: 96, textAlign: "left" as const } : { right: 96, textAlign: "right" as const };
  return (
    <div
      style={{
        position: "absolute",
        top: 68,
        width: 500,
        opacity,
        ...sideStyle,
      }}
    >
      <div style={{ height: 94, display: "flex", justifyContent: callout.side === "left" ? "flex-start" : "flex-end" }}>
        <BasicCounterAdapter
          from={callout.from}
          to={callout.to}
          prefix={callout.prefix}
          postfix={callout.postfix}
          durationInFrames={Math.max(1, Math.min(durationInFrames - inFrames, Math.round(fps * 1.2)))}
          fontSize={84}
          color="#f7d68e"
          style={{ fontWeight: 760, textShadow: "0 2px 10px rgba(0,0,0,.8)" }}
        />
      </div>
      <div style={{ height: 30, display: "flex", justifyContent: callout.side === "left" ? "flex-start" : "flex-end" }}>
        <BasicTypewriterAdapter
          text={callout.label}
          typeSpeedFrames={2}
          showCursor={false}
          fontSize={22}
          color="#fffaf0"
          style={{ fontWeight: 700, letterSpacing: 1.5, textShadow: "0 2px 8px rgba(0,0,0,.84)" }}
        />
      </div>
    </div>
  );
};

/**
 * A full recut of the supplied Autopilot visual source. The canonical audio
 * is the full ElevenLabs MP3; source picture is retimed upstream on sentence
 * boundaries and this composition adds only controlled motion and overlays.
 */
export const AutopilotElevenLabsRecut: React.FC<AutopilotElevenLabsRecutProps> = (props) => {
  const fps = props.fps || 24;
  return (
    <AbsoluteFill style={{ backgroundColor: "#11100d", overflow: "hidden" }}>
      <MovingVisualTrack src={props.visualTrack} durationInFrames={props.durationInFrames} />
      {props.kenBurnsRanges.map((range) => (
        <Sequence
          key={range.id}
          from={frames(range.target_start, fps)}
          durationInFrames={frames(range.target_end - range.target_start, fps)}
          premountFor={fps}
        >
          <KenBurnsAdapter
            images={[props.marketContextStill]}
            durationInFrames={frames(range.target_end - range.target_start, fps)}
            direction="left"
            scaleFrom={1.02}
            scaleTo={1.045}
          />
        </Sequence>
      ))}
      {props.callouts.map((callout) => (
        <Sequence
          key={callout.id}
          from={frames(callout.start, fps)}
          durationInFrames={frames(callout.end - callout.start, fps)}
          premountFor={fps}
        >
          <CounterCallout callout={callout} fps={fps} />
        </Sequence>
      ))}
      {props.captionCues.map((cue) => (
        <Sequence
          key={cue.id}
          from={frames(cue.start, fps)}
          durationInFrames={frames(cue.end - cue.start, fps)}
          premountFor={fps}
        >
          <CaptionCue cue={cue} fps={fps} />
        </Sequence>
      ))}
      <Audio src={staticFile(props.narrationAudio)} />
    </AbsoluteFill>
  );
};

export const calculateAutopilotElevenLabsRecutMetadata = ({ props }: { props: AutopilotElevenLabsRecutProps }) => ({
  durationInFrames: Math.max(1, Math.round(props.durationInFrames)),
  width: Math.max(1, Math.round(props.width)),
  height: Math.max(1, Math.round(props.height)),
  fps: Math.max(1, Math.round(props.fps)),
});
