import { generateInterpolationClip } from "./generate-interpolation-clip.mjs";

async function main() {
  const result = await generateInterpolationClip({
    startQuery: "Person standing at trading works",
    endQuery: "Character walking in shipping yard",
    characterName: "HollowStickMike",
    prompt: "Continuing from the starting frame: The scene smoothly transitions as the camera moves past the financial trading monitors into the expansive outdoor shipping yard. The stick figure character remains composed in his slate navy suit and glasses as he begins walking along the painted road. The indoor terminals dissolve into long rows of parked passenger cars beneath the overcast industrial sky, settling precisely into the ending frame at second 10. Completely silent video.",
    outputPath: "C:\\Users\\Snipe\\Downloads\\Outreach Program\\content\\video_engine\\projects\\systems-and-blowups\\korea-memory-toll\\omni-video\\clips\\clip-05-workstation-to-autolot.mp4",
    framesDir: "C:\\Users\\Snipe\\Downloads\\Outreach Program\\content\\video_engine\\projects\\systems-and-blowups\\korea-memory-toll\\omni-video\\clips\\clip-05-frames"
  });

  console.log("[run-clip-05] Success:", JSON.stringify(result));
}

main().catch(err => {
  console.error("[run-clip-05] Error:", err.message);
  process.exit(1);
});
