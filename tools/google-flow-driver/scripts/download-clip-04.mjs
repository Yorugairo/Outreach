import { chromium } from "playwright-core";
import fs from "node:fs";
import path from "node:path";
import { execSync } from "node:child_process";

async function main() {
  const browser = await chromium.connectOverCDP("http://127.0.0.1:9223");
  const flow = browser.contexts()[0].pages()[0];
  const outputDir = "C:\\Users\\Snipe\\Downloads\\Outreach Program\\content\\video_engine\\projects\\systems-and-blowups\\korea-memory-toll\\omni-video\\clips";
  const outputPath = path.join(outputDir, "clip-04-cleanroom-to-workstation.mp4");
  const framesDir = path.join(outputDir, "clip-04-frames");

  fs.mkdirSync(outputDir, { recursive: true });
  fs.mkdirSync(framesDir, { recursive: true });

  console.log("[download-clip-04] Locating Download scene button...");
  let downloadBtn = flow.locator("button[aria-label*='Download scene'], button:has-text('download')").filter({ visible: true }).first();
  let count = await downloadBtn.count();
  console.log("Download button count:", count);

  if (count === 0) {
    console.log("Modal not open, clicking top card in grid at (350, 220)...");
    await flow.mouse.click(350, 220);
    await flow.waitForTimeout(2000);
    downloadBtn = flow.locator("button[aria-label*='Download scene'], button:has-text('download')").filter({ visible: true }).first();
    count = await downloadBtn.count();
    console.log("Download button count after click:", count);
  }

  if (count > 0) {
    console.log("Triggering download...");
    const [ download ] = await Promise.all([
      flow.waitForEvent("download", { timeout: 20000 }).catch(() => null),
      downloadBtn.click()
    ]);

    if (download) {
      console.log("Captured download! Saving to:", outputPath);
      await download.saveAs(outputPath);
    }
  }

  if (fs.existsSync(outputPath) && fs.statSync(outputPath).size > 100000) {
    console.log("Saved Clip 04 video (" + fs.statSync(outputPath).size + " bytes) to " + outputPath);
    console.log("Extracting frames with ffmpeg...");
    const framePattern = path.join(framesDir, "frame-%02d.png");
    execSync(`ffmpeg -y -i "${outputPath}" -vf "fps=1" "${framePattern}"`, { stdio: "inherit" });
    console.log("Frames extracted successfully to " + framesDir);
  } else {
    console.log("Output file does not exist yet or too small.");
  }

  await browser.close();
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});
