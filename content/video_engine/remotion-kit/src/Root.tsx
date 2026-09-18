import React from "react";
import { Composition } from "remotion";
import { NetworkNodesOutro } from "./NetworkNodesOutro";

// The card is 6.2 s (authoring/audio.py OUTRO_S); the frame counts below are that
// duration at each composition's fps: 186/30 = 6.200 s, 149/24 = 6.208 s.
const OUTRO_FRAMES_30 = 186;
const OUTRO_FRAMES_24 = 149;

// One source of truth for the card's copy and palette: the portrait composition's
// values, unchanged since the 2026-09-02 render. The "subscribe" (outro-yt) and
// cream (outro-brand) variants are render-time --props overrides, not new defaults.
const OUTRO_DEFAULT_PROPS = {
  headline: "It's not magic.\nIt's mechanics.",
  tagline: "Thanks for watching — follow for the next teardown.",
  showHandle: true,
  handle: "@MoneyPhysicsHQ",
  nodeColor: "#a78bfa",
  textColor: "#f5f5f5",
  backgroundColor: "#030014",
};

export const RemotionRoot: React.FC = () => {
  return (
    <>
      {/* 9:16 - the shipped short card. Unchanged: renders pixel-identical. */}
      <Composition
        id="Outro"
        component={NetworkNodesOutro}
        durationInFrames={OUTRO_FRAMES_30}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={OUTRO_DEFAULT_PROPS}
      />

      {/* 16:9 for the long form (R26-210 / audit G-06). The component is already
          aspect-free - it reads width/height/fps from useVideoConfig(). */}
      <Composition
        id="OutroLandscape"
        component={NetworkNodesOutro}
        durationInFrames={OUTRO_FRAMES_30}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={OUTRO_DEFAULT_PROPS}
      />

      {/* 24 fps sibling: fps is a composition property in Remotion, not a prop,
          so the long-form 24 fps build (E99 s36) needs its own composition. */}
      <Composition
        id="OutroLandscape24"
        component={NetworkNodesOutro}
        durationInFrames={OUTRO_FRAMES_24}
        fps={24}
        width={1920}
        height={1080}
        defaultProps={OUTRO_DEFAULT_PROPS}
      />
    </>
  );
};
