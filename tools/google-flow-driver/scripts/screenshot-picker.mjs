import { chromium } from 'playwright-core';
import path from 'node:path';

async function main() {
  const browser = await chromium.connectOverCDP('http://127.0.0.1:9223');
  const flow = browser.contexts()[0].pages()[0];
  const outDir = 'C:\\Users\\Snipe\\Downloads\\Outreach Program\\content\\video_engine\\projects\\systems-and-blowups\\korea-memory-toll\\omni-video\\stills\\inspect';

  // Open asset picker
  const startBtn = flow.locator('button.empty-chip:has-text("Start"), .frame-trigger:has-text("Start")').first();
  if (await startBtn.count() > 0) await startBtn.click();
  await flow.waitForTimeout(1000);

  // Take screenshot of the picker dialog/viewport
  const picker = flow.locator('cdk-virtual-scroll-viewport, .asset-picker, [role="listbox"]').first();
  if (await picker.count() > 0) {
    await picker.screenshot({ path: path.join(outDir, 'asset-picker-view.png') });
    console.log('Saved asset-picker-view.png');
  }

  await flow.keyboard.press('Escape');
  await browser.close();
}

main().catch(err => console.error(err));
