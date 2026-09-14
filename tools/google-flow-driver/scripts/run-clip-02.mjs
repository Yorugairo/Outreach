import { chromium } from 'playwright-core';
import fs from 'node:fs';
import path from 'node:path';
import { execSync } from 'node:child_process';

async function main() {
  const browser = await chromium.connectOverCDP('http://127.0.0.1:9223');
  const flow = browser.contexts()[0].pages()[0];
  const outputDir = 'C:\\Users\\Snipe\\Downloads\\Outreach Program\\content\\video_engine\\projects\\systems-and-blowups\\korea-memory-toll\\omni-video\\clips';
  const outputPath = path.join(outputDir, 'clip-02-newsroom-to-customs.mp4');
  const framesDir = path.join(outputDir, 'clip-02-frames');

  fs.mkdirSync(outputDir, { recursive: true });
  fs.mkdirSync(framesDir, { recursive: true });

  console.log('[clip-02] Starting Clip 02: Newsroom -> Customs Dock Two-Point Transition');

  // Dismiss any lingering overlay
  await flow.keyboard.press('Escape');
  await flow.waitForTimeout(400);

  // 1. PIN START FRAME: Character observing television (Still 02)
  console.log('[clip-02] Step 1: Pinning Start Frame: Character observing television (Still 02)...');
  const startBtn = flow.locator('button.empty-chip:has-text("Start")').first();
  await startBtn.click();
  await flow.waitForTimeout(1000);

  const optStart = flow.locator('[role="option"]:has-text("Character observing television"), .asset-item:has-text("Character observing television")').first();
  console.log('[clip-02] Found Start item count:', await optStart.count());
  await optStart.click();
  await flow.waitForTimeout(800);

  const addBtnStart = flow.getByRole('button', { name: /Add to prompt|Add|Select/i }).filter({ visible: true }).first();
  if (await addBtnStart.count() > 0) {
    console.log('[clip-02] Clicking Add to prompt for Start...');
    await addBtnStart.click({ force: true });
    await flow.waitForTimeout(1000);
  }

  await flow.keyboard.press('Escape');
  await flow.waitForTimeout(500);

  // 2. PIN END FRAME: Character standing at shipping terminal (Still 03)
  console.log('[clip-02] Step 2: Pinning End Frame: Character standing at shipping terminal (Still 03)...');
  const endBtn = flow.locator('button.empty-chip:has-text("End")').first();
  await endBtn.click();
  await flow.waitForTimeout(1000);

  const optEnd = flow.locator('[role="option"]:has-text("Character standing at shipping"), .asset-item:has-text("Character standing at shipping")').first();
  console.log('[clip-02] Found End item count:', await optEnd.count());
  await optEnd.click();
  await flow.waitForTimeout(800);

  const addBtnEnd = flow.getByRole('button', { name: /Add to prompt|Add|Select/i }).filter({ visible: true }).first();
  if (await addBtnEnd.count() > 0) {
    console.log('[clip-02] Clicking Add to prompt for End...');
    await addBtnEnd.click({ force: true });
    await flow.waitForTimeout(1000);
  }

  await flow.keyboard.press('Escape');
  await flow.waitForTimeout(500);

  // 3. VERIFY BOTH FRAMES HAVE IMAGES
  const frameStatus = await flow.evaluate(() => {
    return Array.from(document.querySelectorAll('.frame-trigger')).map(el => ({
      text: el.innerText.trim(),
      hasImg: Boolean(el.querySelector('img'))
    }));
  });
  console.log('[clip-02] Frame status:', JSON.stringify(frameStatus, null, 2));

  // 4. ATTACH CHARACTER CHIP
  const editor = flow.locator("div.ProseMirror, div[contenteditable='true']").first();
  await editor.click({ force: true });
  await flow.waitForTimeout(300);

  console.log('[clip-02] Inserting @HollowStickMike character chip...');
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

  // 5. INSERT TRANSITION PROMPT
  await editor.click({ force: true });
  await flow.keyboard.press('Control+End');
  await flow.waitForTimeout(300);

  const promptText = ' Continuing from the starting frame: The scene smoothly transitions from the broadcast newsroom into the industrial Busan shipping container customs dock. The character remains centered in his slate navy suit. As the studio walls slide away, the towering twilight cranes, shipping containers, and harbor customs floor emerge, settling precisely into the ending frame at second 10. Completely silent video.';
  console.log('[clip-02] Inserting transition prompt text...');
  await flow.keyboard.insertText(promptText);
  await flow.waitForTimeout(1000);

  // 6. TRIGGER GENERATION
  const submitBtn = flow.locator("button:has-text('arrow_forward'), button[aria-label*='Start generation'], button[aria-label*='Submit']").last();
  console.log('[clip-02] Clicking submit button...');
  await submitBtn.click();
  await flow.waitForTimeout(4000);

  // 7. POLL FOR GENERATION COMPLETION
  console.log('[clip-02] Polling for generation completion...');
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
      console.log(`[clip-02] Video generated in ~${Math.round(elapsed)}s!`);
      completed = true;
      break;
    }

    if (status.progress.length > 0) {
      console.log(`[clip-02] Progress: ${status.progress.join(', ')} (${Math.round(elapsed)}s)`);
    }

    await flow.waitForTimeout(4000);
  }

  if (!completed) {
    throw new Error('Video generation timed out after 6 minutes.');
  }

  await flow.waitForTimeout(3000);

  // 8. OPEN NEWEST CARD AND DOWNLOAD
  console.log('[clip-02] Clicking newest media item to download...');
  await flow.mouse.click(355, 140);
  await flow.waitForTimeout(2000);

  const downloadBtn = flow.locator('button[aria-label*="Download scene"], button:has-text("download")').filter({ visible: true }).first();
  if (await downloadBtn.count() > 0) {
    console.log('[clip-02] Found download button! Capturing download...');
    const [ download ] = await Promise.all([
      flow.waitForEvent('download', { timeout: 30000 }).catch(() => null),
      downloadBtn.click()
    ]);

    if (download) {
      console.log('[clip-02] Download caught! Saving to:', outputPath);
      await download.saveAs(outputPath);
    } else {
      await flow.waitForTimeout(5000);
    }
  }

  // 9. VERIFY AND EXTRACT FRAMES
  if (fs.existsSync(outputPath) && fs.statSync(outputPath).size > 100000) {
    console.log(`[clip-02] Successfully saved video (${fs.statSync(outputPath).size} bytes) to ${outputPath}`);
    console.log('[clip-02] Extracting 10 frames with ffmpeg...');
    const framePattern = path.join(framesDir, 'frame-%02d.png');
    execSync(`ffmpeg -y -i "${outputPath}" -vf "fps=1" "${framePattern}"`, { stdio: 'inherit' });
    console.log('[clip-02] Frames extracted successfully to', framesDir);
  } else {
    throw new Error('Clip 02 video could not be downloaded or was too small.');
  }

  await browser.close();
}

main().catch(err => {
  console.error('[clip-02] Error:', err);
  process.exit(1);
});
