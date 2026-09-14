import { chromium } from 'playwright-core';
import fs from 'node:fs';
import path from 'node:path';

async function runClip({ startText, endText, prompt, outputPath }) {
  const browser = await chromium.connectOverCDP('http://127.0.0.1:9223');
  const flow = browser.contexts()[0].pages()[0];

  fs.mkdirSync(path.dirname(outputPath), { recursive: true });

  // Dismiss any overlays
  await flow.keyboard.press('Escape');
  await flow.waitForTimeout(300);

  // 1. PIN START FRAME
  const startBtn = flow.locator('button.empty-chip:has-text("Start"), .frame-trigger:has-text("Start")').first();
  if (await startBtn.count() > 0) {
    await startBtn.click();
    await flow.waitForTimeout(800);
    const item = flow.locator(`[role="option"]:has-text("${startText}"), .asset-item:has-text("${startText}")`).first();
    await item.click();
    await flow.waitForTimeout(600);
    const addBtn = flow.locator('button.detail-add-to-prompt-btn, button:has-text("Add to prompt")').first();
    await addBtn.click();
    await flow.waitForTimeout(800);
  }

  await flow.keyboard.press('Escape');
  await flow.waitForTimeout(400);

  // 2. PIN END FRAME
  const endBtn = flow.locator('button.empty-chip:has-text("End"), .frame-trigger:has-text("End")').first();
  if (await endBtn.count() > 0) {
    await endBtn.click();
    await flow.waitForTimeout(800);
    const item = flow.locator(`[role="option"]:has-text("${endText}"), .asset-item:has-text("${endText}")`).first();
    await item.click();
    await flow.waitForTimeout(600);
    const addBtn = flow.locator('button.detail-add-to-prompt-btn, button:has-text("Add to prompt")').first();
    await addBtn.click();
    await flow.waitForTimeout(800);
  }

  await flow.keyboard.press('Escape');
  await flow.waitForTimeout(400);

  // 3. ATTACH CHARACTER CHIP & INSERT PROMPT
  const editor = flow.locator("div.ProseMirror, div[contenteditable='true']").first();
  await editor.click({ force: true });
  await flow.keyboard.press('Control+A');
  await flow.keyboard.press('Backspace');
  await flow.waitForTimeout(200);

  await flow.keyboard.type('@');
  await flow.waitForTimeout(800);
  const charOpt = flow.locator('[role="option"]:has-text("HollowStickMike"), .asset-item:has-text("HollowStickMike")').first();
  if (await charOpt.count() > 0) {
    await charOpt.click();
    await flow.waitForTimeout(600);
    const addCharBtn = flow.locator('button.detail-add-to-prompt-btn, button:has-text("Add to prompt")').first();
    if (await addCharBtn.count() > 0) await addCharBtn.click();
    await flow.waitForTimeout(800);
  }

  await editor.click({ force: true });
  await flow.keyboard.press('Control+End');
  await flow.waitForTimeout(200);
  await flow.keyboard.insertText(' ' + prompt);
  await flow.waitForTimeout(600);

  // 4. SUBMIT
  const submitBtn = flow.locator("button[aria-label*='Start generation'], button:has-text('arrow_forward')").last();
  await submitBtn.click();
  console.log('[chain] Generation submitted. Waiting for completion...');

  // Wait until generation finishes
  const startTime = Date.now();
  let completed = false;

  while (Date.now() - startTime < 360000) {
    await flow.waitForTimeout(5000);
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
    if (elapsed > 30 && status.progress.length === 0) {
      console.log(`[chain] Render completed in ~${Math.round(elapsed)}s.`);
      completed = true;
      break;
    }
  }

  if (!completed) throw new Error('Timed out');

  await flow.waitForTimeout(2000);

  // 5. DOWNLOAD
  await flow.mouse.click(355, 140);
  await flow.waitForTimeout(2000);

  const downloadBtn = flow.locator('button[aria-label*="Download scene"], button:has-text("download")').filter({ visible: true }).first();
  if (await downloadBtn.count() > 0) {
    const [ download ] = await Promise.all([
      flow.waitForEvent('download', { timeout: 30000 }).catch(() => null),
      downloadBtn.click()
    ]);
    if (download) {
      await download.saveAs(outputPath);
      console.log(`[chain] Downloaded: ${outputPath} (${fs.statSync(outputPath).size} bytes)`);
    }
  }

  await browser.close();
}

const args = {
  startText: 'Character standing at shipping',
  endText: 'Man inspecting silicon wafer',
  prompt: 'Continuing from the starting frame: The scene smoothly transitions as the camera moves past the harbor shipping containers into the high-tech cleanroom laboratory. The stick figure character remains centered in his slate navy suit and glasses. The harbor cranes dissolve into the glowing circular silicon wafer stepper machine, settling precisely into the ending frame at second 10. Completely silent video.',
  outputPath: 'C:\\Users\\Snipe\\Downloads\\Outreach Program\\content\\video_engine\\projects\\systems-and-blowups\\korea-memory-toll\\omni-video\\clips\\clip-03-customs-to-cleanroom.mp4'
};

runClip(args).catch(err => {
  console.error('[chain] Error:', err.message);
  process.exit(1);
});
