import { generateInterpolationClip } from "./generate-interpolation-clip.mjs";

async function main() {
  const result = await generateInterpolationClip({
    startQuery: "Man inspecting silicon wafer",
    endQuery: "Person standing at trading works",
    characterName: "HollowStickMike",
    prompt: "Continuing from the starting frame: The scene smoothly transitions as the camera glides from the cleanroom laboratory into the quiet financial trading desk. The stick figure character remains composed in his slate navy suit and glasses. The glowing silicon stepper machinery dissolves into the warm ambient multi-monitor workstation, settling precisely into the ending frame at second 10. Completely silent video.",
    outputPath: "C:\\Users\\Snipe\\Downloads\\Outreach Program\\content\\video_engine\\projects\\systems-and-blowups\\korea-memory-toll\\omni-video\\clips\\clip-04-cleanroom-to-workstation.mp4",
    framesDir: "C:\\Users\\Snipe\\Downloads\\Outreach Program\\content\\video_engine\\projects\\systems-and-blowups\\korea-memory-toll\\omni-video\\clips\\clip-04-frames"
  });

  console.log("[run-clip-04] Success:", JSON.stringify(result));
}

main().catch(err => {
  console.error("[run-clip-04] Error:", err.message);
  process.exit(1);
});
