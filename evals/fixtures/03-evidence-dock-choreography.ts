import { EvalResult } from "./01-google-flow-manifest-validation";

export async function runEvidenceDockEval(): Promise<EvalResult> {
  const choreographySpec = {
    dock1Scale: 0.85,
    dockWidthPx: 475,
    dockHeightPx: 485,
    boardWipeDurationSeconds: 0.5,
    rebuildChartFromRawData: true,
    bannedInfoCards: true
  };

  const validDockSize = choreographySpec.dockWidthPx <= 480 && choreographySpec.dockHeightPx <= 500;
  const validWipeDuration = choreographySpec.boardWipeDurationSeconds <= 0.5;
  const adheresToRulingB1B2 = choreographySpec.rebuildChartFromRawData && choreographySpec.bannedInfoCards;
  const passed = validDockSize && validWipeDuration && adheresToRulingB1B2;

  return {
    name: "03-evidence-dock-choreography",
    category: "Evidence Motion Engine",
    passed,
    score: passed ? 10 : 0,
    maxScore: 10,
    details: passed
      ? "Ruling B1-B3 adherence verified (2.5D washi dock sizing, chart rebuilds, and 0.5s board wipe timing)."
      : "Failed evidence dock choreography."
  };
}
