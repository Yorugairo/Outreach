import { chromium } from 'playwright-core';

async function main() {
  const browser = await chromium.connectOverCDP('http://127.0.0.1:9223');
  const flow = browser.contexts()[0].pages()[0];

  // Dismiss any open modals/overlays
  await flow.keyboard.press('Escape');
  await flow.waitForTimeout(300);

  // Check current Start / End / chips
  const info = await flow.evaluate(() => {
    const startChip = document.querySelector('.frame-trigger:nth-child(1), button.empty-chip');
    const chips = Array.from(document.querySelectorAll('.mention-chip')).map(c => c.innerText.trim());
    return {
      chips,
      buttons: Array.from(document.querySelectorAll('button')).map(b => b.innerText.trim()).filter(t => t.length > 0 && t.length < 30)
    };
  });
  console.log('Current state:', JSON.stringify(info, null, 2));

  await browser.close();
}

main().catch(err => console.error(err));
