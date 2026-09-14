import { chromium } from 'playwright-core';

async function main() {
  const browser = await chromium.connectOverCDP('http://127.0.0.1:9223');
  const flow = browser.contexts()[0].pages()[0];

  // Dismiss any overlays
  await flow.keyboard.press('Escape');
  await flow.waitForTimeout(400);

  // 1. PIN START FRAME
  console.log('Pinning Start frame with button.detail-add-to-prompt-btn...');
  const startBtn = flow.locator('button.empty-chip:has-text("Start")').first();
  if (await startBtn.count() > 0) {
    await startBtn.click();
    await flow.waitForTimeout(1000);

    const item = flow.locator('.asset-item:has-text("Character observing television")').first();
    console.log('Start option count:', await item.count());
    await item.click();
    await flow.waitForTimeout(800);

    const addBtn = flow.locator('button.detail-add-to-prompt-btn').first();
    console.log('Add button count:', await addBtn.count());
    await addBtn.click();
    await flow.waitForTimeout(1000);
  }

  // 2. PIN END FRAME
  console.log('Pinning End frame with button.detail-add-to-prompt-btn...');
  const endBtn = flow.locator('button.empty-chip:has-text("End")').first();
  if (await endBtn.count() > 0) {
    await endBtn.click();
    await flow.waitForTimeout(1000);

    const item = flow.locator('.asset-item:has-text("Character standing at shipping")').first();
    console.log('End option count:', await item.count());
    await item.click();
    await flow.waitForTimeout(800);

    const addBtn = flow.locator('button.detail-add-to-prompt-btn').first();
    console.log('Add button count:', await addBtn.count());
    await addBtn.click();
    await flow.waitForTimeout(1000);
  }

  // 3. CHECK RESULT
  const state = await flow.evaluate(() => {
    const triggers = Array.from(document.querySelectorAll('.frame-trigger')).map(el => ({
      text: el.innerText.trim(),
      hasImg: Boolean(el.querySelector('img')),
      src: el.querySelector('img')?.src?.slice(0, 60) || null
    }));
    return triggers;
  });

  console.log('Frame triggers after pinning:', JSON.stringify(state, null, 2));

  await browser.close();
}

main().catch(err => console.error(err));
