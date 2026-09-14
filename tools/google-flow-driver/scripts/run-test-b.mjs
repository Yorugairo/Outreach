import { chromium } from 'playwright-core';
import fs from 'node:fs';
import path from 'node:path';
import { execSync } from 'node:child_process';

async function main() {
  const browser = await chromium.connectOverCDP('http://127.0.0.1:9223');
  const flow = browser.contexts()[0].pages()[0];
  const outputDir = 'C:\\Users\\Snipe\\Downloads\\Outreach Program\\content\\video_engine\\projects\\systems-and-blowups\\korea-memory-toll\\omni-video\\clips';
  const outputPath = path.join(outputDir, 'test-02-harbor-action-intra.mp4');
  const framesDir = path.join(outputDir, 'test-02-action-frames');

  fs.mkdirSync(outputDir, { recursive: true });
  fs.mkdirSync(framesDir, { recursive: true });

  console.log('[test-b] Starting Test B: Intra-shot Harbor Action Two-Point Interpolation');

  // Dismiss any overlay
  await flow.keyboard.press('Escape');
  await flow.waitForTimeout(400);

  // Check if Start is pinned
  const startStatus = await flow.evaluate(() => {
    const startEl = document.querySelector('.frame-trigger:first-child, button.chip-container');
    return Boolean(startEl && startEl.querySelector('img'));
  });
  console.log('[test-b] Start frame already pinned:', startStatus);

  if (!startStatus) {
    console.log('[test-b] Pinning Start Frame...');
    const startBtn = flow.locator('button.empty-chip:has-text("Start")').first();
    await startBtn.click();
    await flow.waitForTimeout(1000);
    const optStart = flow.locator('[role="option"]:has-text("still-01-busan-container-toll.png"), .asset-item:has-text("still-01-busan-container-toll.png")').first();
    await optStart.click();
    await flow.waitForTimeout(800);
    const addBtn = flow.getByRole('button', { name: /Add to prompt|Add|Select/i }).filter({ visible: true }).first();
    await addBtn.click();
    await flow.waitForTimeout(800);
    await flow.keyboard.press('Escape');
    await flow.waitForTimeout(500);
  }

  // Pin End Frame
  console.log('[test-b] Pinning End Frame: Man standing behind wooden desk...');
  const endBtn = flow.locator('button.empty-chip:has-text("End")').first();
  await endBtn.click();
  await flow.waitForTimeout(1000);

  const optEnd = flow.locator('[role="option"]:has-text("Man standing behind wooden desk"), .asset-item:has-text("Man standing behind wooden desk")').first();
  console.log('[test-b] Found End asset item count:', await optEnd.count());
  await optEnd.click();
  await flow.waitForTimeout(800);

  const addBtnEnd = flow.getByRole('button', { name: /Add to prompt/i }).filter({ visible: true }).first();
  if (await addBtnEnd.count() > 0) {
    console.log('[test-b] Clicking Add to prompt for End...');
    await addBtnEnd.click({ force: true });
    await flow.waitForTimeout(1000);
  }

  await flow.keyboard.press('Escape');
  await flow.waitForTimeout(500);

  // Verify both frame triggers have images
  const frameStatus = await flow.evaluate(() => {
    return Array.from(document.querySelectorAll('.frame-trigger')).map(el => ({
      text: el.innerText.trim(),
      hasImg: Boolean(el.querySelector('img'))
    }));
  });
  console.log('[test-b] Frame status:', JSON.stringify(frameStatus, null, 2));

  // Focus editor and attach character chip
  const editor = flow.locator("div.ProseMirror, div[contenteditable='true']").first();
  await editor.click({ force: true });
  await flow.waitForTimeout(300);

  console.log('[test-b] Inserting @HollowStickMike chip...');
  await flow.keyboard.type('@');
  await flow.waitForTimeout(800);
  const charOpt = flow.locator('[role="option"]:has-text("HollowStickMike"), .asset-item:has-text("HollowStickMike")').first();
  if (await charOpt.count() > 0) {
    await charOpt.click();
    await flow.waitForTimeout(600);
    const addCharBtn = flow.getByRole('button', { name: /Add to prompt|Add/i }).filter({ visible: true }).first();
    if (await addCharBtn.count() > 0) await addCharBtn.click({ force: true });
    await flow.waitForTimeout(800);
  }

  // Type prompt text
  await editor.click({ force: true });
  await flow.keyboard.press('Control+End');
  await flow.waitForTimeout(300);

  const promptText = ' Continuing from the starting frame: The character stands calmly in his harbor office in his slate navy suit. As evening arrives over the harbor, he turns smoothly towards the tall glass window to watch the distant shipping cranes, settling into the ending pose at second 10. Completely silent video.';
  console.log('[test-b] Inserting prompt text...');
  await flow.keyboard.insertText(promptText);
  await flow.waitForTimeout(1000);

  // Click Submit
  const submitBtn = flow.locator("button:has-text('arrow_forward'), button[aria-label*='Start generation'], button[aria-label*='Submit']").last();
  console.log('[test-b] Clicking submit button...');
  await submitBtn.click();
  await flow.waitForTimeout(4000);

  // Poll for completion
  console.log('[test-b] Polling for generation completion...');
  const startTime = Date.now();
  let completed = false;

  while (Date.now() - startTime < 360000) {
    const status = await flow.evaluate(() => {
      const progress = Array.from(document.querySelectorAll('*'))
        .filter(el => el.children.length === 0 && /\b\d+%\b/.test(el.innerText))
        .map(el => el.innerText.trim());
      const failed = document.querySelector('.error, [role="alert"]')?.innerText || null;
      return { progress, failed };
    });

    if (status.failed) {
      throw new Error(`Generation failed: ${status.failed}`);
    }

    const elapsed = (Date.now() - startTime) / 1000;
    if (elapsed > 20 && status.progress.length === 0) {
      console.log(`[test-b] Video generated in ~${Math.round(elapsed)}s!`);
      completed = true;
      break;
    }

    if (status.progress.length > 0) {
      console.log(`[test-b] Progress: ${status.progress.join(', ')} (${Math.round(elapsed)}s)`);
    }

    await flow.waitForTimeout(4000);
  }

  if (!completed) {
    throw new Error('Video generation timed out after 6 minutes.');
  }

  await flow.waitForTimeout(3000);

  // Download via scene download button
  console.log('[test-b] Opening newest item and downloading...');
  const newestThumbnail = flow.locator('img[alt*="Man"], img[alt*="Character"]').first();
  await newestThumbnail.click();
  await flow.waitForTimeout(2000);

  const downloadBtn = flow.locator('button[aria-label*="Download scene"], button:has-text("download")').filter({ visible: true }).first();
  if (await downloadBtn.count() > 0) {
    console.log('[test-b] Clicking Download scene...');
    const [ download ] = await Promise.all([
      flow.waitForEvent('download', { timeout: 30000 }).catch(() => null),
      downloadBtn.click()
    ]);

    if (download) {
      console.log('[test-b] Download event captured! Saving to:', outputPath);
      await download.saveAs(outputPath);
    } else {
      await flow.waitForTimeout(5000);
    }
  }

  if (fs.existsSync(outputPath) && fs.statSync(outputPath).size > 1000) {
    console.log(`[test-b] Successfully saved video (${fs.statSync(outputPath).size} bytes)!`);
    console.log('[test-b] Extracting 10 frames with ffmpeg...');
    const framePattern = path.join(framesDir, 'frame-%02d.png');
    execSync(`ffmpeg -y -i "${outputPath}" -vf "fps=1" "${framePattern}"`, { stdio: 'inherit' });
    console.log('[test-b] Extracted frames to', framesDir);
  } else {
    throw new Error('Video file was not created or empty');
  }

  await browser.close();
}

main().catch(err => {
  console.error('[test-b] Error:', err);
  process.exit(1);
});
