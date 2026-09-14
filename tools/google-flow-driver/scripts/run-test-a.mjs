import { chromium } from 'playwright-core';
import fs from 'node:fs';
import path from 'node:path';
import { execSync } from 'node:child_process';

async function main() {
  const browser = await chromium.connectOverCDP('http://127.0.0.1:9223');
  const flow = browser.contexts()[0].pages()[0];
  const outputDir = 'C:\\Users\\Snipe\\Downloads\\Outreach Program\\content\\video_engine\\projects\\systems-and-blowups\\korea-memory-toll\\omni-video\\clips';
  const outputPath = path.join(outputDir, 'test-02-harbor-to-newsroom.mp4');
  const framesDir = path.join(outputDir, 'test-02-frames');

  fs.mkdirSync(outputDir, { recursive: true });
  fs.mkdirSync(framesDir, { recursive: true });

  console.log('[test-a] Starting Test A: Harbor to Newsroom Two-Point Transition');

  // Dismiss any lingering overlay backdrop
  await flow.keyboard.press('Escape');
  await flow.waitForTimeout(400);

  // 1. PIN START FRAME
  console.log('[test-a] Step 1: Pinning Start Frame...');
  const startBtn = flow.locator('button.empty-chip:has-text("Start"), .frame-trigger:has-text("Start")').first();
  if (await startBtn.count() > 0) {
    await startBtn.click();
    await flow.waitForTimeout(1000);

    const optStart = flow.locator('[role="option"]:has-text("still-01-busan-container-toll.png"), .asset-item:has-text("still-01-busan-container-toll.png")').first();
    if (await optStart.count() > 0) {
      console.log('[test-a] Clicking still-01 asset item...');
      await optStart.click();
      await flow.waitForTimeout(800);

      const addBtn = flow.getByRole('button', { name: /Add to prompt|Add|Select/i }).filter({ visible: true }).first();
      if (await addBtn.count() > 0) {
        console.log('[test-a] Clicking Add to prompt button for Start...');
        await addBtn.click();
        await flow.waitForTimeout(1000);
      }
    }
  }

  // Dismiss any lingering overlay
  await flow.keyboard.press('Escape');
  await flow.waitForTimeout(500);

  // 2. PIN END FRAME
  console.log('[test-a] Step 2: Pinning End Frame...');
  const endBtn = flow.locator('button.empty-chip:has-text("End"), .frame-trigger:has-text("End")').first();
  if (await endBtn.count() > 0) {
    await endBtn.click();
    await flow.waitForTimeout(1000);

    const optEnd = flow.locator('[role="option"]:has-text("Character observing television"), .asset-item:has-text("Character observing television")').first();
    if (await optEnd.count() > 0) {
      console.log('[test-a] Clicking newsroom asset item...');
      await optEnd.click();
      await flow.waitForTimeout(800);

      const addBtn = flow.getByRole('button', { name: /Add to prompt|Add|Select/i }).filter({ visible: true }).first();
      if (await addBtn.count() > 0) {
        console.log('[test-a] Clicking Add to prompt button for End...');
        await addBtn.click();
        await flow.waitForTimeout(1000);
      }
    }
  }

  // Dismiss any lingering overlay
  await flow.keyboard.press('Escape');
  await flow.waitForTimeout(500);

  // 3. VERIFY BOTH FRAMES ARE PINNED
  const frameStatus = await flow.evaluate(() => {
    const triggers = Array.from(document.querySelectorAll('.frame-trigger, .chip-container, button.empty-chip')).map(el => ({
      tag: el.tagName,
      text: (el.innerText || '').trim(),
      hasImg: Boolean(el.querySelector('img'))
    }));
    return triggers;
  });
  console.log('[test-a] Frame triggers status:', JSON.stringify(frameStatus, null, 2));

  // 4. VERIFY CHARACTER CHIP
  const editor = flow.locator("div.ProseMirror, div[contenteditable='true']").first();
  await editor.click({ force: true });
  await flow.waitForTimeout(300);

  const chipCount = await flow.locator('.mention-chip:has-text("HollowStickMike")').count();
  console.log('[test-a] HollowStickMike chip count:', chipCount);

  if (chipCount === 0) {
    console.log('[test-a] Inserting @HollowStickMike chip...');
    await flow.keyboard.type('@');
    await flow.waitForTimeout(800);
    const charOpt = flow.locator('[role="option"]:has-text("HollowStickMike"), .asset-item:has-text("HollowStickMike")').first();
    if (await charOpt.count() > 0) {
      await charOpt.click();
      await flow.waitForTimeout(600);
      const addBtn = flow.getByRole('button', { name: /Add to prompt|Add/i }).filter({ visible: true }).first();
      if (await addBtn.count() > 0) await addBtn.click();
      await flow.waitForTimeout(800);
    }
  }

  // 5. INSERT PROMPT
  await editor.click({ force: true });
  await flow.keyboard.press('Control+End');
  await flow.waitForTimeout(300);

  const promptText = ' Continuing from the starting frame: The scene smoothly transitions from the quiet harbor desk into the financial broadcast newsroom. The character remains composed and centered in his slate navy suit. As the room shifts, the television news anchors and live upward market indicators emerge in the studio background, settling precisely into the ending frame at second 10. Completely silent video.';
  console.log('[test-a] Inserting transition prompt text...');
  await flow.keyboard.insertText(promptText);
  await flow.waitForTimeout(1000);

  // Baseline videos
  const prevVideos = await flow.evaluate(() => {
    return Array.from(document.querySelectorAll('video'))
      .map(v => v.src || v.getAttribute('src'))
      .filter(s => Boolean(s) && /getMediaUrlRedirect|flow-content\.google\/|\/asb\//.test(s));
  });
  console.log('[test-a] Baseline video count:', prevVideos.length);

  // 6. TRIGGER GENERATION
  const submitBtn = flow.locator("button:has-text('arrow_forward'), button[aria-label*='Start generation'], button[aria-label*='Submit']").last();
  console.log('[test-a] Clicking submit button...');
  await submitBtn.click();
  await flow.waitForTimeout(3000);

  // 7. WAIT FOR GENERATION TO COMPLETE
  console.log('[test-a] Waiting for generation to complete (polling every 3s)...');
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

  console.log('[test-a] Video generation complete! URL:', settledSrc);

  // 8. DOWNLOAD VIDEO BYTES
  let videoBuffer;
  try {
    const videoBytes = await flow.evaluate(async (src) => {
      const resp = await fetch(src);
      const blob = await resp.blob();
      const arrayBuf = await blob.arrayBuffer();
      return Array.from(new Uint8Array(arrayBuf));
    }, settledSrc);
    videoBuffer = Buffer.from(videoBytes);
    console.log(`[test-a] Downloaded ${videoBuffer.length} bytes via evaluate fetch.`);
  } catch (err) {
    console.log('[test-a] Evaluate fetch failed, downloading via APIRequestContext...', err.message);
    const response = await flow.context().request.get(settledSrc);
    videoBuffer = await response.body();
    console.log(`[test-a] Downloaded ${videoBuffer.length} bytes via request context.`);
  }

  fs.writeFileSync(outputPath, videoBuffer);
  console.log(`[test-a] Saved video to ${outputPath}`);

  // 9. EXTRACT FRAMES WITH FFMPEG
  console.log('[test-a] Extracting 10 frames with ffmpeg...');
  const framePattern = path.join(framesDir, 'frame-%02d.png');
  execSync(`ffmpeg -y -i "${outputPath}" -vf "fps=1" "${framePattern}"`, { stdio: 'inherit' });
  console.log('[test-a] Extracted frames to', framesDir);

  await browser.close();
}

main().catch(err => {
  console.error('[test-a] Fatal error:', err);
  process.exit(1);
});
