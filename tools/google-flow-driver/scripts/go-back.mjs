import { chromium } from 'playwright-core';
import path from 'node:path';

async function main() {
  const browser = await chromium.connectOverCDP('http://127.0.0.1:9223');
  const flow = browser.contexts()[0].pages()[0];
  const outDir = 'C:\\Users\\Snipe\\Downloads\\Outreach Program\\content\\video_engine\\projects\\systems-and-blowups\\korea-memory-toll\\omni-video\\clips';

  // Click back button or navigate to project URL
  const backBtn = flow.locator('button:has-text("arrow_back")').first();
  if (await backBtn.count() > 0) {
    console.log('Clicking back button...');
    await backBtn.click();
    await flow.waitForTimeout(1500);
  } else {
    console.log('Navigating to project URL...');
    await flow.goto('https://flow.google.com/project/d171ec1f-d4a2-4b79-b76e-32460193dccc');
    await flow.waitForTimeout(2000);
  }

  await flow.screenshot({ path: path.join(outDir, 'after-back.png') });
  console.log('Saved after-back.png');

  await browser.close();
}

main().catch(err => console.error(err));
