import { chromium } from 'playwright-core';
import fs from 'node:fs';
import path from 'node:path';

async function main() {
  const browser = await chromium.connectOverCDP('http://127.0.0.1:9223');
  const flow = browser.contexts()[0].pages()[0];
  const outputDir = 'C:\\Users\\Snipe\\Downloads\\Outreach Program\\content\\video_engine\\projects\\systems-and-blowups\\korea-memory-toll\\omni-video\\clips';
  const outputPath = path.join(outputDir, 'clip-01-busan-frames-test.mp4');

  console.log('[test-generate] Target output:', outputPath);

  // Dismiss any lingering overlay backdrop from the asset picker
  await flow.keyboard.press('Escape');
  await flow.waitForTimeout(500);
  await flow.evaluate(() => {
    const backdrop = document.querySelector('.cdk-overlay-backdrop');
    if (backdrop) backdrop.click();
  });
  await flow.waitForTimeout(500);

  // 1. Focus prompt editor
  const editor = flow.locator("div.ProseMirror, div[contenteditable='true']").first();
  await editor.click({ force: true });
  await flow.waitForTimeout(300);

  // Clear any leftover text
  await flow.keyboard.press('Control+A');
  await flow.waitForTimeout(200);
  await flow.keyboard.press('Backspace');
  await flow.waitForTimeout(400);

  // Type kinetic delta prompt
  const prompt = 'Continuing from the starting frame: The character stands calmly beside his desk, holding his coffee cup while gazing out the window at the harbor. Outside, twilight shipping cranes slowly adjust and lower a container. At second 5, the character lifts the coffee cup slightly and holds it steady. Locked-off static tripod camera. Completely silent video.';
  console.log('[test-generate] Inserting prompt...');
  await flow.keyboard.insertText(prompt);
  await flow.waitForTimeout(1000);

  // Take baseline videos
  const prevVideos = await flow.evaluate(() => {
    return Array.from(document.querySelectorAll('video'))
      .map(v => v.src || v.getAttribute('src'))
      .filter(s => Boolean(s) && /getMediaUrlRedirect|flow-content\.google\/|\/asb\//.test(s));
  });
  console.log('[test-generate] Baseline videos:', prevVideos.length);

  // Click Submit
  const submitBtn = flow.locator("button:has-text('arrow_forward'), button[aria-label*='Start generation'], button[aria-label*='Submit']").last();
  console.log('[test-generate] Clicking generate button...');
  await submitBtn.click();
  await flow.waitForTimeout(3000);

  // Wait for new video URL
  console.log('[test-generate] Waiting for generation to finish...');
  const startTime = Date.now();
  let settledSrc = null;

  while (Date.now() - startTime < 300000) {
    const currentSrc = await flow.evaluate((prevs) => {
      const vids = Array.from(document.querySelectorAll('video'))
        .map(v => v.src || v.getAttribute('src'))
        .filter(s => Boolean(s) && /getMediaUrlRedirect|flow-content\.google\/|\/asb\//.test(s));
      for (const s of vids) {
        if (!prevs.includes(s)) return s;
      }
      return null;
    }, prevVideos);

    if (currentSrc) {
      settledSrc = currentSrc;
      break;
    }
    await flow.waitForTimeout(3000);
  }

  if (!settledSrc) {
    throw new Error('Video generation timed out after 5 minutes.');
  }

  console.log('[test-generate] Video generated! Endpoint:', settledSrc);

  // Download video bytes
  const videoBytes = await flow.evaluate(async (src) => {
    const resp = await fetch(src);
    const blob = await resp.blob();
    const arrayBuf = await blob.arrayBuffer();
    return Array.from(new Uint8Array(arrayBuf));
  }, settledSrc);

  fs.mkdirSync(outputDir, { recursive: true });
  fs.writeFileSync(outputPath, Buffer.from(videoBytes));
  console.log(`[test-generate] Successfully saved video (${videoBytes.length} bytes) to ${outputPath}`);

  await browser.close();
}

main().catch(err => {
  console.error('[test-generate] Error:', err.message);
  process.exit(1);
});
