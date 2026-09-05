import React from "react"; import { registerRoot, Composition } from "remotion"; import { Captions } from "./Captions";
import data from "../captions-yen.json";
const Root: React.FC = () => (
  <Composition id="Captions" component={Captions} durationInFrames={data.durationInFrames} fps={data.fps} width={1080} height={1920}
    defaultProps={{ groups: data.groups, ink: "#25313C", accent: "#ED6A4A", anchorY: 1230, fontSize: 72 }} />
);
registerRoot(Root);
