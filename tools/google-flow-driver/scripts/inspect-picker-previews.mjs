import { chromium } from 'playwright-core';
import fs from 'node:fs';

async function main() {
  const browser = await chromium.connectOverCDP('http://127.0.0.1:9223');
  const flow = browser.contexts()[0].pages()[0];

  // Open asset picker to inspect items and their preview images
  const startBtn = flow.locator('button.empty-chip:has-text("Start")').first();
  await startBtn.click();
  await flow.waitForTimeout(1000);

  const items = await flow.evaluate(async () => {
    const opts = Array.from(document.querySelectorAll('[role="option"], .asset-item'));
    return opts.map(opt => ({
      text: opt.innerText.trim(),
      imgSrc: opt.querySelector('img')?.src || null
    }));
  });

  console.log('Picker items:', JSON.stringify(items.slice(0, 10), null, 2));

  await flow.keyboard.press('Escape');
  await browser.close();
}

main().catch(err => console.error(err));
