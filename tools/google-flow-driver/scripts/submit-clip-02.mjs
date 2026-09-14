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

  console.log('[submit-clip-02] Clicking Start generation button...');
  const submitBtn = flow.locator("button[aria-label*='Start generation'], button:has-text('arrow_forward')").last();
  await submitBtn.click();
  await flow.waitForTimeout(4000);

  // Poll for completion
  console.log('[submit-clip-02] Polling for generation progress...');
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
      console.log(`[submit-clip-02] Video generation finished in ~${Math.round(elapsed)}s!`);
      completed = true;
      break;
    }

    if (status.progress.length > 0) {
      console.log(`[submit-clip-02] Progress: ${status.progress.join(', ')} (${Math.round(elapsed)}s elapsed)`);
    }

    await flow.waitForTimeout(4000);
  }

  if (!completed) {
    throw new Error('Video generation timed out after 6 minutes.');
  }

  await flow.waitForTimeout(3000);

  // Click the top-left completed card to open player
  console.log('[submit-clip-02] Opening newest video card...');
  await flow.mouse.click(355, 140);
  await flow.waitForTimeout(2000);

  const downloadBtn = flow.locator('button[aria-label*="Download scene"], button:has-text("download")').filter({ visible: true }).first();
  if (await downloadBtn.count() > 0) {
    console.log('[submit-clip-02] Found Download scene button! Downloading...');
    const [ download ] = await Promise.all([
      flow.waitForEvent('download', { timeout: 30000 }).catch(() => null),
      downloadBtn.click()
    ]);

    if (download) {
      console.log('[submit-clip-02] Download event captured! Saving to:', outputPath);
      await download.saveAs(outputPath);
    } else {
      await flow.waitForTimeout(5000);
    }
  }

  if (fs.existsSync(outputPath) && fs.statSync(outputPath).size > 100000) {
    console.log(`[submit-clip-02] Successfully saved Clip 02 video (${fs.statSync(outputPath).size} bytes) to ${outputPath}`);
    console.log('[submit-clip-02] Extracting 10 frames with ffmpeg...');
    const framePattern = path.join(framesDir, 'frame-%02d.png');
    execSync(`ffmpeg -y -i "${outputPath}" -vf "fps=1" "${framePattern}"`, { stdio: 'inherit' });
    console.log('[submit-clip-02] Extracted frames successfully to', framesDir);
  } else {
    throw new Error('Clip 02 video file could not be saved or was too small.');
  }

  await browser.close();
}

main().catch(err => {
  console.error('[submit-clip-02] Error:', err);
  process.exit(1);
});
