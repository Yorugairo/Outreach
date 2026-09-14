import { chromium } from 'playwright-core';

async function main() {
  const browser = await chromium.connectOverCDP('http://127.0.0.1:9223');
  const flow = browser.contexts()[0].pages()[0];
  const startBtn = flow.locator('button.empty-chip:has-text("Start"), .frame-trigger:has-text("Start")').first();
  if (await startBtn.count() > 0) await startBtn.click();
  await flow.waitForTimeout(1000);
  const items = await flow.evaluate(() => {
    return Array.from(document.querySelectorAll('[role="option"], .asset-item')).map(el => ({
      text: (el.innerText || '').replace(/\s+/g, ' ').trim(),
      img: el.querySelector('img')?.src || null
    }));
  });
  console.log(JSON.stringify(items, null, 2));
  await flow.keyboard.press('Escape');
  await browser.close();
}

main().catch(err => console.error(err));
