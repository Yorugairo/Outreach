import React from "react"; import { registerRoot, Composition } from "remotion"; import { YenChart } from "./YenChart";
// panel in the plate's quiet zone (top third); 9s: 0.35 enter, 2.3 draw, marker, bar, hold
const Root: React.FC = () => (<Composition id="YenChart" component={YenChart} durationInFrames={270} fps={30} width={1080} height={1920}
  defaultProps={{ x: 60, y: 120, w: 960, h: 520 }} />);
registerRoot(Root);
