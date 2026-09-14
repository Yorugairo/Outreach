import { chromium } from 'playwright-core';

async function main() {
  const browser = await chromium.connectOverCDP('http://127.0.0.1:9223');
  const pages = browser.contexts().flatMap(c => c.pages());
  const flow = pages.find(p => p.url().includes('flow.google.com') || p.url().includes('labs.google/fx/tools/flow')) || pages[0];

  const startBtn = flow.locator('button.empty-chip:has-text("Start")').first();
  console.log('[test-action] Start button count:', await startBtn.count());

  let chooserTriggered = false;
  flow.once('filechooser', (fc) => {
    chooserTriggered = true;
    console.log('[test-action] Native filechooser opened!');
  });

  await startBtn.click();
  await flow.waitForTimeout(1500);

  console.log('[test-action] Chooser triggered:', chooserTriggered);

  const openElements = await flow.evaluate(() => {
    return Array.from(document.querySelectorAll('[role="dialog"], [role="listbox"], [role="menu"], .picker, .modal, .popover, [class*="picker"], [class*="dialog"]')).map(el => ({
      tag: el.tagName,
      role: el.getAttribute('role'),
      className: el.className,
      text: (el.innerText || '').slice(0, 150)
    }));
  });

  console.log('[test-action] Open modal elements:', JSON.stringify(openElements, null, 2));

  await flow.keyboard.press('Escape');
  await browser.close();
}

main().catch(err => console.error(err));
