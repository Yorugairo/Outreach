import { chromium } from 'playwright-core';
import path from 'node:path';

async function main() {
  const browser = await chromium.connectOverCDP('http://127.0.0.1:9223');
  const flow = browser.contexts()[0].pages()[0];
  const outDir = 'C:\\Users\\Snipe\\Downloads\\Outreach Program\\content\\video_engine\\projects\\systems-and-blowups\\korea-memory-toll\\omni-video\\clips';

  const editor = flow.locator("div.ProseMirror, div[contenteditable='true']").first();
  await editor.click({ force: true });
  await flow.waitForTimeout(300);

  // Clear text
  await flow.keyboard.press('Control+A');
  await flow.waitForTimeout(200);
  await flow.keyboard.press('Backspace');
  await flow.waitForTimeout(300);

  // Insert @HollowStickMike chip
  console.log('Inserting @HollowStickMike chip...');
  await flow.keyboard.type('@');
  await flow.waitForTimeout(800);

  const charOpt = flow.locator('[role="option"]:has-text("HollowStickMike"), .asset-item:has-text("HollowStickMike")').first();
  if (await charOpt.count() > 0) {
    await charOpt.click();
    await flow.waitForTimeout(600);
    const addBtn = flow.locator('button.detail-add-to-prompt-btn, button:has-text("Add to prompt")').first();
    if (await addBtn.count() > 0) {
      await addBtn.click();
      await flow.waitForTimeout(800);
    }
  }

  // Check state
  const state = await flow.evaluate(() => {
    const triggers = Array.from(document.querySelectorAll('.frame-trigger')).map(el => ({
      text: el.innerText.trim(),
      hasImg: Boolean(el.querySelector('img'))
    }));
    const chips = Array.from(document.querySelectorAll('.mention-chip')).map(c => c.innerText.trim());
    return { triggers, chips };
  });

  console.log('State before prompt text:', JSON.stringify(state, null, 2));

  // Insert safe audited prompt
  const safePrompt = ' Continuing from the starting frame: The scene smoothly transitions as the camera glides from the studio room into the outdoor cargo shipping terminal. The stick figure character remains centered in his slate navy suit and glasses. The indoor desks and wall monitors gently move aside as the towering twilight harbor cranes and cargo containers appear, settling precisely into the ending frame at second 10. Completely silent video.';
  await editor.click({ force: true });
  await flow.keyboard.press('Control+End');
  await flow.waitForTimeout(200);
  await flow.keyboard.insertText(safePrompt);
  await flow.waitForTimeout(800);

  await flow.screenshot({ path: path.join(outDir, 'clip-02-ready-to-submit.png') });
  console.log('Saved clip-02-ready-to-submit.png');

  await browser.close();
}

main().catch(err => console.error(err));
