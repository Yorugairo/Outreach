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

  console.log("[download-clip-03] Locating Download scene button...");
  const downloadBtn = flow.locator("button[aria-label*='Download scene'], button:has-text('download')").filter({ visible: true }).first();

  console.log("Download button count:", await downloadBtn.count());

  if (await downloadBtn.count() > 0) {
    console.log("Found Download scene button! Listening for download or network response...");

    let capturedUrl = null;
    const responseHandler = async (res) => {
      const url = res.url();
      if (url.includes(".mp4") || url.includes("flow-content.google") || url.includes("getMediaUrlRedirect") || url.includes("videoplayback")) {
        if (res.headers()["content-type"]?.includes("video") || url.includes(".mp4")) {
          console.log("[network] Video response captured:", url.slice(0, 100));
          capturedUrl = url;
        }
      }
    };
    flow.on("response", responseHandler);

    const [ download ] = await Promise.all([
      flow.waitForEvent("download", { timeout: 15000 }).catch(() => null),
      downloadBtn.click()
    ]);

    if (download) {
      console.log("Download caught via waitForEvent! Saving to:", outputPath);
      await download.saveAs(outputPath);
    } else {
      console.log("waitForEvent did not catch download. Checking network or file system...");
      await flow.waitForTimeout(5000);
      if (capturedUrl) {
        console.log("Fetching captured video URL:", capturedUrl);
        const resp = await flow.context().request.get(capturedUrl);
        const buf = await resp.body();
        if (buf.length > 50000) {
          fs.writeFileSync(outputPath, buf);
          console.log("Saved via captured network URL!");
        }
      }
    }
  }

  // Check file size
  if (fs.existsSync(outputPath)) {
    const size = fs.statSync(outputPath).size;
    console.log(`Output file exists: ${size} bytes`);
    if (size > 500000) {
      console.log("Extracting 10 frames with ffmpeg...");
      const framePattern = path.join(framesDir, "frame-%02d.png");
      execSync(`ffmpeg -y -i "${outputPath}" -vf "fps=1" "${framePattern}"`, { stdio: "inherit" });
      console.log("Frames extracted successfully to", framesDir);
    }
  } else {
    console.log("Output file does not exist yet.");
  }

  await browser.close();
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});
