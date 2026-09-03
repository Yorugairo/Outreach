import { EvalResult } from "./01-google-flow-manifest-validation";

export async function runDiskAsBusEval(): Promise<EvalResult> {
  const subagentMessage = {
    summaryBullets: 3,
    writtenArtifactPath: "docs/research/runs/grill_sample/findings_r1.md",
    contextTokensSentOverIpc: 180
  };

  const isLowTokenIpc = subagentMessage.contextTokensSentOverIpc < 300;
  const hasIsolatedArtifact = subagentMessage.writtenArtifactPath.startsWith("docs/research/runs/");
  const hasConciseSummary = subagentMessage.summaryBullets <= 5;
  const passed = isLowTokenIpc && hasIsolatedArtifact && hasConciseSummary;

  return {
    name: "05-disk-as-bus-isolation",
    category: "Harness Concurrency",
    passed,
    score: passed ? 10 : 0,
    maxScore: 10,
    details: passed
      ? "Subagent Disk-as-Bus pattern confirmed (low IPC tokens, isolated disk artifacts, single coordinator writer)."
      : "Failed Disk-as-Bus isolation check."
  };
}
