import { runGoogleFlowManifestEval } from "./fixtures/01-google-flow-manifest-validation";
import { runRemotionTimelineEval } from "./fixtures/02-remotion-timeline-invariants";
import { runEvidenceDockEval } from "./fixtures/03-evidence-dock-choreography";
import { runScriptHumanizerEval } from "./fixtures/04-script-humanizer-validation";
import { runDiskAsBusEval } from "./fixtures/05-disk-as-bus-isolation";

async function runAllEvals() {
  console.log("===================================================================");
  console.log("🎬  2026 Video Engine & Outreach Deterministic Eval Suite");
  console.log("===================================================================\n");

  const results = await Promise.all([
    runGoogleFlowManifestEval(),
    runRemotionTimelineEval(),
    runEvidenceDockEval(),
    runScriptHumanizerEval(),
    runDiskAsBusEval(),
  ]);

  let totalScore = 0;
  let maxScore = 0;

  for (const r of results) {
    totalScore += r.score;
    maxScore += r.maxScore;
    const badge = r.passed ? "✅ PASS" : "❌ FAIL";
    console.log(`${badge} [${r.category}] ${r.name} (${r.score}/${r.maxScore} pts)`);
    console.log(`   └─ ${r.details}`);
  }

  const percentage = Math.round((totalScore / maxScore) * 100);
  console.log("\n-------------------------------------------------------------------");
  console.log(`Scorecard: ${totalScore} / ${maxScore} pts (${percentage}%)`);
  console.log("-------------------------------------------------------------------");

  if (percentage < 100) {
    process.exit(1);
  }
}

runAllEvals().catch((err) => {
  console.error("Eval runner error:", err);
  process.exit(1);
});
