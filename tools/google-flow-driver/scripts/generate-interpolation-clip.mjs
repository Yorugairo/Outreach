import { chromium } from "playwright-core";
import fs from "node:fs";
import path from "node:path";
import { execSync } from "node:child_process";

/**
 * Universal Two-Point Continuous Frame Interpolation Runner for Google Flow
 * Pins Start Frame + End Frame + Character Chip, submits audited prompt,
 * monitors generation, downloads finished MP4, and extracts frames.
 */
export async function generateInterpolationClip({
  startQuery,
  endQuery,
  characterName = "HollowStickMike",
  prompt,
  outputPath,
  framesDir = null,
  timeoutMs = 360000
}) {
  if (!startQuery || !endQuery || !prompt || !outputPath) {
    throw new Error("Missing required arguments: startQuery, endQuery, prompt, outputPath");
  }

  const targetDir = path.dirname(outputPath);
  fs.mkdirSync(targetDir, { recursive: true });
  if (framesDir) fs.mkdirSync(framesDir, { recursive: true });

  const browser = await chromium.connectOverCDP("http://127.0.0.1:9223");
  const flow = browser.contexts()[0].pages()[0];

  console.log(`[clip-runner] Starting interpolation: "${startQuery}" -> "${endQuery}"`);

  // Clear any existing overlays or scene edit view
  if (flow.url().includes('/edit/')) {
    const backBtn = flow.locator("button[aria-label*='Back'], button:has-text('arrow_back')").first();
    if (await backBtn.count() > 0) {
      await backBtn.click();
      await flow.waitForTimeout(1000);
    } else {
      await flow.keyboard.press("Escape");
      await flow.waitForTimeout(800);
    }
  } else {
    await flow.keyboard.press("Escape");
    await flow.waitForTimeout(400);
  }

  // 1. PIN START FRAME
  console.log(`[clip-runner] Pinning Start frame: "${startQuery}"...`);
  const startBtn = flow.locator("button.empty-chip:has-text('Start'), .frame-trigger:has-text('Start')").first();
  if (await startBtn.count() > 0) {
    await startBtn.click();
    await flow.waitForTimeout(1000);
    const startItem = flow.locator(`[role="option"]:has-text("${startQuery}"), .asset-item:has-text("${startQuery}")`).first();
    if (await startItem.count() === 0) {
      throw new Error(`Start asset matching "${startQuery}" not found in picker`);
    }
    await startItem.click();
    await flow.waitForTimeout(800);
    const addBtn = flow.locator("button.detail-add-to-prompt-btn, button:has-text('Add to prompt')").first();
    if (await addBtn.count() > 0) {
      await addBtn.click();
      await flow.waitForTimeout(1000);
    }
  }

  // 2. PIN END FRAME
  console.log(`[clip-runner] Pinning End frame: "${endQuery}"...`);
  const endBtn = flow.locator("button.empty-chip:has-text('End'), .frame-trigger:has-text('End')").first();
  if (await endBtn.count() > 0) {
    await endBtn.click();
    await flow.waitForTimeout(1000);
    const endItem = flow.locator(`[role="option"]:has-text("${endQuery}"), .asset-item:has-text("${endQuery}")`).first();
    if (await endItem.count() === 0) {
      throw new Error(`End asset matching "${endQuery}" not found in picker`);
    }
    await endItem.click();
    await flow.waitForTimeout(800);
    const addBtn = flow.locator("button.detail-add-to-prompt-btn, button:has-text('Add to prompt')").first();
    if (await addBtn.count() > 0) {
      await addBtn.click();
      await flow.waitForTimeout(1000);
    }
  }

  // 3. ATTACH CHARACTER CHIP & INSERT PROMPT
  const editor = flow.locator("div.ProseMirror, div[contenteditable='true']").first();
  await editor.click({ force: true });
  await flow.waitForTimeout(300);
  await flow.keyboard.press("Control+A");
  await flow.waitForTimeout(150);
  await flow.keyboard.press("Backspace");
  await flow.waitForTimeout(300);

  if (characterName) {
    console.log(`[clip-runner] Attaching character chip: @${characterName}...`);
    await flow.keyboard.type("@");
    await flow.waitForTimeout(800);
    const charOpt = flow.locator(`[role="option"]:has-text("${characterName}"), .asset-item:has-text("${characterName}")`).first();
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

  console.log("[clip-runner] Inserting transition prompt text...");
  await editor.click({ force: true });
  await flow.keyboard.press("Control+End");
  await flow.waitForTimeout(200);
  await flow.keyboard.insertText(" " + prompt.trim());
  await flow.waitForTimeout(800);

  // 4. PREFLIGHT VERIFICATION
  const preflight = await flow.evaluate(() => {
    const triggers = Array.from(document.querySelectorAll(".frame-trigger, .chip-container")).map(el => ({
      hasImg: Boolean(el.querySelector("img"))
    }));
    const chips = Array.from(document.querySelectorAll(".mention-chip")).map(c => c.innerText.trim());
    return {
      pinnedCount: triggers.filter(t => t.hasImg).length,
      chips
    };
  });
  console.log("[clip-runner] Preflight verification:", JSON.stringify(preflight));

  // 5. SUBMIT GENERATION
  console.log("[clip-runner] Submitting generation...");
  const submitBtn = flow.locator("button[aria-label*='Start generation'], button:has-text('arrow_forward')").last();
  await submitBtn.click();
  await flow.waitForTimeout(4000);

  // 6. POLL PROGRESS
  console.log("[clip-runner] Polling generation progress...");
  const startTime = Date.now();
  let completed = false;

  while (Date.now() - startTime < timeoutMs) {
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
      console.log(`[clip-runner] Render completed in ~${Math.round(elapsed)}s!`);
      completed = true;
      break;
    }

    if (status.progress.length > 0) {
      console.log(`[clip-runner] Progress: ${status.progress.join(", ")} (${Math.round(elapsed)}s elapsed)`);
    }

    await flow.waitForTimeout(4000);
  }

  if (!completed) {
    throw new Error("Generation timed out after " + Math.round(timeoutMs / 1000) + "s.");
  }

  await flow.waitForTimeout(3000);

  // 7. OPEN CARD & DOWNLOAD
  console.log("[clip-runner] Opening newest video card...");
  let downloadBtn = flow.locator("button[aria-label*='Download scene'], button:has-text('download')").filter({ visible: true }).first();
  if (await downloadBtn.count() === 0) {
    await flow.mouse.click(350, 220);
    await flow.waitForTimeout(2000);
    downloadBtn = flow.locator("button[aria-label*='Download scene'], button:has-text('download')").filter({ visible: true }).first();
    if (await downloadBtn.count() === 0) {
      await flow.mouse.click(355, 140);
      await flow.waitForTimeout(2000);
      downloadBtn = flow.locator("button[aria-label*='Download scene'], button:has-text('download')").filter({ visible: true }).first();
    }
  }

  if (await downloadBtn.count() > 0) {
    console.log("[clip-runner] Capturing video download...");
    const [ download ] = await Promise.all([
      flow.waitForEvent("download", { timeout: 30000 }).catch(() => null),
      downloadBtn.click()
    ]);

    if (download) {
      await download.saveAs(outputPath);
      console.log(`[clip-runner] Downloaded video: ${outputPath} (${fs.statSync(outputPath).size} bytes)`);
    }
  }

  // 8. EXTRACT FRAMES IF REQUESTED
  if (fs.existsSync(outputPath) && fs.statSync(outputPath).size > 100000) {
    if (framesDir) {
      console.log("[clip-runner] Extracting 10 frames with ffmpeg...");
      const framePattern = path.join(framesDir, "frame-%02d.png");
      execSync(`ffmpeg -y -i "${outputPath}" -vf "fps=1" "${framePattern}"`, { stdio: "inherit" });
      console.log(`[clip-runner] Extracted frames to: ${framesDir}`);
    }
  } else {
    throw new Error("Resulting MP4 was missing or under 100KB.");
  }

  await browser.close();
  return { outputPath, size: fs.statSync(outputPath).size };
}
