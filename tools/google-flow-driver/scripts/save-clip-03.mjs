import { chromium } from "playwright-core";
import fs from "node:fs";
import path from "node:path";
import { execSync } from "node:child_process";

async function main() {
  const browser = await chromium.connectOverCDP("http://127.0.0.1:9223");
  const flow = browser.contexts()[0].pages()[0];
  const outputDir = "C:\\Users\\Snipe\\Downloads\\Outreach Program\\content\\video_engine\\projects\\systems-and-blowups\\korea-memory-toll\\omni-video\\clips";
  const outputPath = path.join(outputDir, "clip-03-customs-to-cleanroom.mp4");
  const framesDir = path.join(outputDir, "clip-03-frames");

  fs.mkdirSync(outputDir, { recursive: true });
  fs.mkdirSync(framesDir, { recursive: true });

  // 1. Check all videos currently in DOM
  let vids = await flow.evaluate(() => {
    return Array.from(document.querySelectorAll("video"))
      .map(v => v.src || v.getAttribute("src"))
      .filter(s => s && s.length > 10);
  });
  console.log("Current video sources in DOM:", vids);

  // If player not open or src not found, click the top-left card
  if (vids.length === 0) {
    console.log("No video in DOM, clicking top-left card (360, 90)...");
    await flow.mouse.click(360, 90);
    await flow.waitForTimeout(2000);
    vids = await flow.evaluate(() => {
      return Array.from(document.querySelectorAll("video"))
        .map(v => v.src || v.getAttribute("src"))
        .filter(s => s && s.length > 10);
    });
    console.log("Video sources after click:", vids);
  }

  // Also check download button if present
  const downloadBtn = flow.locator("button[aria-label*='Download scene'], button:has-text('download')").filter({ visible: true }).first();
  console.log("Download button visible count:", await downloadBtn.count());

  const targetSrc = vids.find(s => s.includes('getMediaUrlRedirect') || s.includes('flow-content.google') || s.includes('/asb/')) || vids[0];
  if (!targetSrc) {
    throw new Error("Could not find any video source in page");
  }

  console.log("Target video URL:", targetSrc);

  let videoBuffer;
  try {
    const videoBytes = await flow.evaluate(async (src) => {
      const resp = await fetch(src);
      const blob = await resp.blob();
      const arrayBuf = await blob.arrayBuffer();
      return Array.from(new Uint8Array(arrayBuf));
    }, targetSrc);
    videoBuffer = Buffer.from(videoBytes);
    console.log("Downloaded " + videoBuffer.length + " bytes via page evaluate.");
  } catch (err) {
    console.log("Evaluate fetch failed, using request context:", err.message);
    const response = await flow.context().request.get(targetSrc);
    videoBuffer = await response.body();
    console.log("Downloaded " + videoBuffer.length + " bytes via request context.");
  }

  if (videoBuffer && videoBuffer.length > 50000) {
    fs.writeFileSync(outputPath, videoBuffer);
    console.log("Saved video to " + outputPath + " (" + videoBuffer.length + " bytes)");

    console.log("Extracting 10 frames with ffmpeg...");
    const framePattern = path.join(framesDir, "frame-%02d.png");
    execSync("ffmpeg -y -i \"" + outputPath + "\" -vf \"fps=1\" \"" + framePattern + "\"", { stdio: "inherit" });
    console.log("Extracted frames to " + framesDir);
  } else {
    throw new Error("Downloaded video buffer too small or empty");
  }

  await browser.close();
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});
