import { chromium } from 'playwright-core';
import fs from 'node:fs';
import path from 'node:path';

async function main() {
  const browser = await chromium.connectOverCDP('http://127.0.0.1:9223');
  const flow = browser.contexts()[0].pages()[0];
  const outputDir = 'C:\\Users\\Snipe\\Downloads\\Outreach Program\\content\\video_engine\\projects\\systems-and-blowups\\korea-memory-toll\\omni-video\\clips';
  const outputPath = path.join(outputDir, 'test-02-harbor-to-newsroom.mp4');

  console.log('[test-transition] Starting Test 2: Harbor to Newsroom transition');

  // Dismiss any lingering overlay
  await flow.keyboard.press('Escape');
  await flow.waitForTimeout(400);

  // 1. PIN START FRAME
  console.log('[test-transition] Pinning Start Frame: still-01-busan-container-toll.png');
  const startBtn = flow.locator('.frame-trigger:has-text("Start"), button.empty-chip:has-text("Start")').first();
  if (await startBtn.count() > 0) {
    await startBtn.click();
    await flow.waitForTimeout(800);
    const optStart = flow.locator('[role="option"]:has-text("still-01-busan-container-toll.png"), .asset-item:has-text("still-01-busan-container-toll.png")').first();
    if (await optStart.count() > 0) {
      await optStart.click();
      await flow.waitForTimeout(600);
      const addBtn = flow.getByRole('button', { name: /Add|Select/i }).filter({ visible: true }).first();
      if (await addBtn.count() > 0) await addBtn.click();
      await flow.waitForTimeout(1000);
    }
  }

  // Dismiss any backdrop
  await flow.keyboard.press('Escape');
  await flow.waitForTimeout(400);

  // 2. PIN END FRAME
  console.log('[test-transition] Pinning End Frame: Character observing television (still-02)');
  const endBtn = flow.locator('.frame-trigger:has-text("End"), button.empty-chip:has-text("End")').first();
  if (await endBtn.count() > 0) {
    await endBtn.click();
    await flow.waitForTimeout(800);
    const optEnd = flow.locator('[role="option"]:has-text("Character observing television"), .asset-item:has-text("Character observing television")').first();
    if (await optEnd.count() > 0) {
      await optEnd.click();
      await flow.waitForTimeout(600);
      const addBtn = flow.getByRole('button', { name: /Add|Select/i }).filter({ visible: true }).first();
      if (await addBtn.count() > 0) await addBtn.click();
      await flow.waitForTimeout(1000);
    }
  }

  // Dismiss any backdrop
  await flow.keyboard.press('Escape');
  await flow.waitForTimeout(500);

  // 3. ENSURE CHARACTER CHIP IS ATTACHED
  const editor = flow.locator("div.ProseMirror, div[contenteditable='true']").first();
  await editor.click({ force: true });
  await flow.waitForTimeout(300);

  const chipCount = await flow.locator('.mention-chip:has-text("HollowStickMike")').count();
  console.log('[test-transition] HollowStickMike chip count:', chipCount);

  if (chipCount === 0) {
    console.log('[test-transition] Attaching @HollowStickMike character chip...');
    await flow.keyboard.type('@');
    await flow.waitForTimeout(800);
    const charOpt = flow.locator('[role="option"]:has-text("HollowStickMike"), .asset-item:has-text("HollowStickMike")').first();
    if (await charOpt.count() > 0) {
      await charOpt.click();
      await flow.waitForTimeout(600);
      const addBtn = flow.getByRole('button', { name: /Add to prompt/i }).filter({ visible: true }).first();
      if (await addBtn.count() > 0) await addBtn.click();
      await flow.waitForTimeout(800);
    }
  }

  // 4. INSERT KINETIC DELTA PROMPT
  await editor.click({ force: true });
  await flow.keyboard.press('Control+End');
  await flow.waitForTimeout(300);

  const prompt = ' Continuing from the starting frame: The scene smoothly transitions from the quiet harbor desk into the financial broadcast newsroom. The character remains composed and centered in his slate navy suit. As the room shifts, the television news anchors and live upward market indicators emerge in the studio background, settling precisely into the ending frame at second 10. Completely silent video.';
  console.log('[test-transition] Inserting prompt text...');
  await flow.keyboard.insertText(prompt);
  await flow.waitForTimeout(1000);

  // Take baseline videos
  const prevVideos = await flow.evaluate(() => {
    return Array.from(document.querySelectorAll('video'))
      .map(v => v.src || v.getAttribute('src'))
      .filter(s => Boolean(s) && /getMediaUrlRedirect|flow-content\.google\/|\/asb\//.test(s));
  });
  console.log('[test-transition] Baseline videos:', prevVideos.length);

  // 5. TRIGGER GENERATION
  const submitBtn = flow.locator("button:has-text('arrow_forward'), button[aria-label*='Start generation'], button[aria-label*='Submit']").last();
  console.log('[test-transition] Triggering generation...');
  await submitBtn.click();
  await flow.waitForTimeout(3000);

  // 6. WAIT AND DOWNLOAD
  console.log('[test-transition] Waiting for generation to complete...');
  const startTime = Date.now();
  let settledSrc = null;

  while (Date.now() - startTime < 360000) {
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
    throw new Error('Video generation timed out after 6 minutes.');
  }

  console.log('[test-transition] Video generated! Source:', settledSrc);

  const videoBytes = await flow.evaluate(async (src) => {
    const resp = await fetch(src);
    const blob = await resp.blob();
    const arrayBuf = await blob.arrayBuffer();
    return Array.from(new Uint8Array(arrayBuf));
  }, settledSrc);

  fs.mkdirSync(outputDir, { recursive: true });
  fs.writeFileSync(outputPath, Buffer.from(videoBytes));
  console.log(`[test-transition] Successfully saved video (${videoBytes.length} bytes) to ${outputPath}`);

  await browser.close();
}

main().catch(err => {
  console.error('[test-transition] Error:', err.message);
  process.exit(1);
});
