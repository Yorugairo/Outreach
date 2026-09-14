import { chromium } from 'playwright-core';

async function main() {
  const browser = await chromium.connectOverCDP('http://127.0.0.1:9223');
  const pages = browser.contexts().flatMap(c => c.pages());
  const flow = pages.find(p => p.url().includes('flow.google.com') || p.url().includes('labs.google/fx/tools/flow')) || pages[0];
  console.log('[test-start] Page URL:', flow.url());

  const startBtn = flow.locator('button').filter({ hasText: /^Start$/i }).first();
  console.log('[test-start] Start button found:', await startBtn.count());

  // Check if clicking startBtn triggers filechooser or opens a picker
  let chooserTriggered = false;
  flow.once('filechooser', () => {
    chooserTriggered = true;
    console.log('[test-start] Filechooser event triggered!');
  });

  await startBtn.click();
  await flow.waitForTimeout(1500);

  console.log('[test-start] Chooser triggered:', chooserTriggered);

  // Check what new dialogs or listboxes appeared
  const dialogs = await flow.evaluate(() => {
    const list = [];
    document.querySelectorAll('[role="dialog"], [role="listbox"], [role="menu"]').forEach(el => {
      const rect = el.getBoundingClientRect();
      if (rect.width > 0 && rect.height > 0) {
        list.push({
          tag: el.tagName,
          role: el.getAttribute('role'),
          text: (el.innerText || '').slice(0, 100),
          width: Math.round(rect.width),
          height: Math.round(rect.height)
        });
      }
    });
    return list;
  });

  console.log('[test-start] Visible Dialogs/Pickers:', JSON.stringify(dialogs, null, 2));

  // Press escape to close any opened picker
  await flow.keyboard.press('Escape');
  await browser.close();
}

main().catch(err => {
  console.error('[test-start] Error:', err.message);
  process.exit(1);
});
