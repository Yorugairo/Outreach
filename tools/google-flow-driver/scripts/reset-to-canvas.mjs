import { chromium } from 'playwright-core';
import path from 'node:path';

async function main() {
  const browser = await chromium.connectOverCDP('http://127.0.0.1:9223');
  const flow = browser.contexts()[0].pages()[0];
  const outDir = 'C:\\Users\\Snipe\\Downloads\\Outreach Program\\content\\video_engine\\projects\\systems-and-blowups\\korea-memory-toll\\omni-video\\clips';

  // Check if back button or close button is visible
  const backBtn = flow.locator('button:has-text("arrow_back")').first();
  if (await backBtn.count() > 0) {
    console.log('Clicking back button...');
    await backBtn.click();
    await flow.waitForTimeout(1000);
  }

  // Dismiss any overlays
  await flow.keyboard.press('Escape');
  await flow.waitForTimeout(500);

  await flow.screenshot({ path: path.join(outDir, 'flow-current-canvas.png') });
  console.log('Saved flow-current-canvas.png');

  await browser.close();
}

main().catch(err => console.error(err));
