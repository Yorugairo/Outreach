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

  console.log("[submit-clip-03] Checking composer state...");
  const editor = flow.locator("div.ProseMirror, div[contenteditable='true']").first();
  await editor.click({ force: true });
  await flow.waitForTimeout(300);

  // Clear existing text if any
  await flow.keyboard.press("Control+A");
  await flow.waitForTimeout(200);
  await flow.keyboard.press("Backspace");
  await flow.waitForTimeout(300);

  // Check if HollowStickMike chip is present
  const chipCount = await flow.locator(".mention-chip:has-text('HollowStickMike')").count();
  if (chipCount === 0) {
    console.log("[submit-clip-03] Inserting @HollowStickMike chip...");
    await flow.keyboard.type("@");
    await flow.waitForTimeout(800);

    const charOpt = flow.locator("[role='option']:has-text('HollowStickMike'), .asset-item:has-text('HollowStickMike')").first();
    if (await charOpt.count() > 0) {
      await charOpt.click();
      await flow.waitForTimeout(600);
      const addBtn = flow.locator("button.detail-add-to-prompt-btn, button:has-text('Add to prompt')").first();
      if (await addBtn.count() > 0) {
        await addBtn.click();
        await flow.waitForTimeout(800);
      }
    }
  }

  // Insert safe audited prompt
  const safePrompt = " Continuing from the starting frame: The scene smoothly transitions as the camera moves past the harbor shipping containers into the high-tech cleanroom laboratory. The stick figure character remains centered in his slate navy suit and glasses. The harbor cranes dissolve into the glowing circular silicon wafer stepper machine, settling precisely into the ending frame at second 10. Completely silent video.";
  console.log("[submit-clip-03] Inserting prompt...");
  await editor.click({ force: true });
  await flow.keyboard.press("Control+End");
  await flow.waitForTimeout(200);
  await flow.keyboard.insertText(safePrompt);
  await flow.waitForTimeout(800);

  // Verify full setup before submitting
  const statusBefore = await flow.evaluate(() => {
    const triggers = Array.from(document.querySelectorAll(".frame-trigger, .chip-container")).map(el => ({
      text: el.innerText.trim(),
      hasImg: Boolean(el.querySelector("img"))
    }));
    const chips = Array.from(document.querySelectorAll(".mention-chip")).map(c => c.innerText.trim());
    return { triggers, chips };
  });
  console.log("[submit-clip-03] Preflight status:", JSON.stringify(statusBefore, null, 2));

  // Click Submit
  console.log("[submit-clip-03] Submitting generation...");
  const submitBtn = flow.locator("button[aria-label*='Start generation'], button:has-text('arrow_forward')").last();
  await submitBtn.click();
  await flow.waitForTimeout(4000);

  // Poll for completion
  console.log("[submit-clip-03] Polling for generation progress...");
  const startTime = Date.now();
  let completed = false;

  while (Date.now() - startTime < 360000) {
    const status = await flow.evaluate(() => {
      const progress = Array.from(document.querySelectorAll("*"))
        .filter(el => el.children.length === 0 && /\b\d+%\b/.test(el.innerText))
        .map(el => el.innerText.trim());
      const failed = document.querySelector(".error, [role='alert']")?.innerText || null;
      return { progress, failed };
    });

    if (status.failed) {
      throw new Error("Generation failed: " + status.failed);
    }

    const elapsed = (Date.now() - startTime) / 1000;
    if (elapsed > 20 && status.progress.length === 0) {
      console.log("[submit-clip-03] Video generation finished in ~" + Math.round(elapsed) + "s!");
      completed = true;
      break;
    }

    if (status.progress.length > 0) {
      console.log("[submit-clip-03] Progress: " + status.progress.join(", ") + " (" + Math.round(elapsed) + "s elapsed)");
    }

    await flow.waitForTimeout(4000);
  }

  if (!completed) {
    throw new Error("Video generation timed out after 6 minutes.");
  }

  await flow.waitForTimeout(3000);

  // Click the top-left completed card to open player
  console.log("[submit-clip-03] Opening newest video card...");
  await flow.mouse.click(355, 140);
  await flow.waitForTimeout(2000);

  const downloadBtn = flow.locator("button[aria-label*='Download scene'], button:has-text('download')").filter({ visible: true }).first();
  if (await downloadBtn.count() > 0) {
    console.log("[submit-clip-03] Downloading scene video...");
    const [ download ] = await Promise.all([
      flow.waitForEvent("download", { timeout: 30000 }).catch(() => null),
      downloadBtn.click()
    ]);

    if (download) {
      console.log("[submit-clip-03] Download captured! Saving to:", outputPath);
      await download.saveAs(outputPath);
    } else {
      await flow.waitForTimeout(5000);
    }
  }

  if (fs.existsSync(outputPath) && fs.statSync(outputPath).size > 100000) {
    console.log("[submit-clip-03] Successfully saved Clip 03 video (" + fs.statSync(outputPath).size + " bytes) to " + outputPath);
    console.log("[submit-clip-03] Extracting 10 frames with ffmpeg...");
    const framePattern = path.join(framesDir, "frame-%02d.png");
    execSync("ffmpeg -y -i \"" + outputPath + "\" -vf \"fps=1\" \"" + framePattern + "\"", { stdio: "inherit" });
    console.log("[submit-clip-03] Extracted frames successfully to " + framesDir);
  } else {
    throw new Error("Clip 03 video file could not be saved or was too small.");
  }

  await browser.close();
}

main().catch(err => {
  console.error("[submit-clip-03] Error:", err);
  process.exit(1);
});
