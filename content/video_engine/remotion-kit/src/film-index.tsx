import React from "react"; import { registerRoot, Composition } from "remotion"; import { FilmFrame } from "./FilmFrame";
const Root: React.FC = () => (<Composition id="FilmFrame" component={FilmFrame} durationInFrames={2070} fps={30} width={1080} height={1920}
  defaultProps={{ strip: "#25313C", hole: "#F4E6C7", scratch: "#25313C", grain: 0.08, scratchIntensity: 0.35, stripH: 56 }} />);
registerRoot(Root);
