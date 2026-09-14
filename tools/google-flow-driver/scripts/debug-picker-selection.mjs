import { chromium } from 'playwright-core';
import path from 'node:path';

async function main() {
  const browser = await chromium.connectOverCDP('http://127.0.0.1:9223');
  const flow = browser.contexts()[0].pages()[0];
  const outDir = 'C:\\Users\\Snipe\\Downloads\\Outreach Program\\content\\video_engine\\projects\\systems-and-blowups\\korea-memory-toll\\omni-video\\clips';

  // 1. Click Start
  const startBtn = flow.locator('button.empty-chip:has-text("Start")').first();
  console.log('Start button count:', await startBtn.count());
  await startBtn.click();
  await flow.waitForTimeout(1000);

  // Take screenshot of picker
  await flow.screenshot({ path: path.join(outDir, 'picker-open.png') });
  console.log('Saved picker-open.png');

  // Find the option for "Character observing television"
  const opt = flow.locator('[role="option"]:has-text("Character observing television"), .asset-item:has-text("Character observing television")').first();
  console.log('Option count:', await opt.count());
  await opt.click();
  await flow.waitForTimeout(1000);

  // Take screenshot after clicking option
  await flow.screenshot({ path: path.join(outDir, 'picker-after-click.png') });
  console.log('Saved picker-after-click.png');

  // Dump all buttons in the overlay
  const overlayButtons = await flow.evaluate(() => {
    const pane = document.querySelector('.cdk-overlay-pane, .cdk-overlay-container');
    if (!pane) return [];
    return Array.from(pane.querySelectorAll('button, [role="button"]')).map(b => ({
      text: (b.innerText || '').trim(),
      aria: b.getAttribute('aria-label') || '',
      className: b.className
    }));
  });

  console.log('Overlay buttons:', JSON.stringify(overlayButtons, null, 2));

  await flow.keyboard.press('Escape');
  await browser.close();
}

main().catch(err => console.error(err));
