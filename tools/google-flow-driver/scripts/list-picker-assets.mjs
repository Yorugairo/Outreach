import { chromium } from 'playwright-core';

async function main() {
  const browser = await chromium.connectOverCDP('http://127.0.0.1:9223');
  const flow = browser.contexts()[0].pages()[0];

  const startBtn = flow.locator('button.empty-chip:has-text("Start")').first();
  await startBtn.click();
  await flow.waitForTimeout(1000);

  const assets = await flow.evaluate(() => {
    return Array.from(document.querySelectorAll('[role="option"], .asset-item')).map(el => {
      const title = el.querySelector('.asset-title')?.innerText || el.innerText || '';
      const img = el.querySelector('img')?.src || '';
      return { title: title.replace(/\s+/g, ' ').trim(), img };
    });
  });

  console.log('Available assets in picker:', JSON.stringify(assets, null, 2));

  await flow.keyboard.press('Escape');
  await browser.close();
}

main().catch(err => console.error(err));
