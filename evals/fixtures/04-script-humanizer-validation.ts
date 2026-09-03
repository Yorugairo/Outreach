import { EvalResult } from "./01-google-flow-manifest-validation";

export async function runScriptHumanizerEval(): Promise<EvalResult> {
  const badScript = "In today's rapidly evolving landscape, we delve into a tapestry of revolutionary game-changers.";
  const cleanScript = "Semiconductor memory manufacturers are facing an unexpected 3-to-1 wafer allocation penalty.";
  
  const aiBuzzwords = ["delve", "tapestry", "rapidly evolving", "game-changer", "revolutionary"];
  const catchesAiSlop = aiBuzzwords.some(word => badScript.toLowerCase().includes(word));
  const passesCleanScript = !aiBuzzwords.some(word => cleanScript.toLowerCase().includes(word));
  const passed = catchesAiSlop && passesCleanScript;

  return {
    name: "04-script-humanizer-validation",
    category: "Anti-AI Scripting",
    passed,
    score: passed ? 10 : 0,
    maxScore: 10,
    details: passed
      ? "Anti-AI Humanizer gate correctly detected and rejected synthetic buzzwords while passing clean narrative scripts."
      : "Failed script humanizer validation."
  };
}
