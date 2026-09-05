import React from "react";
import { Composition } from "remotion";
import { NetworkNodesOutro } from "./NetworkNodesOutro";

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="Outro"
      component={NetworkNodesOutro}
      durationInFrames={186}
      fps={30}
      width={1080}
      height={1920}
      defaultProps={{
        headline: "It's not magic.\nIt's mechanics.",
        tagline: "Thanks for watching — follow for the next teardown.",
        showHandle: true,
        handle: "@MoneyPhysicsHQ",
        nodeColor: "#a78bfa",
        textColor: "#f5f5f5",
        backgroundColor: "#030014",
      }}
    />
  );
};
