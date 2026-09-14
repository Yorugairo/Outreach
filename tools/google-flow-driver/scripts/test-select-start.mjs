import { chromium } from 'playwright-core';

async function main() {
  const browser = await chromium.connectOverCDP('http://127.0.0.1:9223');
  const flow = browser.contexts()[0].pages()[0];

  const startBtn = flow.locator('button.empty-chip:has-text("Start")').first();
  await startBtn.click();
  await flow.waitForTimeout(800);

  // Click the option for still-01-busan-container-toll.png
  const opt = flow.locator('[role="option"]:has-text("still-01-busan-container-toll.png"), .asset-item:has-text("still-01-busan-container-toll.png")').first();
  console.log('[test-select] Option found:', await opt.count());
  await opt.click();
  await flow.waitForTimeout(1000);

  // Check if there is an Add button or if it inserted directly
  const addBtn = flow.getByRole('button', { name: /Add|Select/i }).filter({ visible: true }).first();
  if (await addBtn.count() > 0) {
    console.log('[test-select] Clicking Add button...');
    await addBtn.click();
    await flow.waitForTimeout(1000);
  }

  // Check what the start chip looks like now
  const chips = await flow.evaluate(() => {
    return Array.from(document.querySelectorAll('button, div')).filter(el => {
      const cls = el.className || '';
      return typeof cls === 'string' && (cls.includes('chip') || cls.includes('frame'));
    }).map(el => ({
      tag: el.tagName,
      className: el.className,
      text: (el.innerText || '').slice(0, 50),
      hasImg: Boolean(el.querySelector('img'))
    }));
  });

  console.log('[test-select] Chips after selection:', JSON.stringify(chips, null, 2));

  await browser.close();
}

main().catch(err => console.error(err));
