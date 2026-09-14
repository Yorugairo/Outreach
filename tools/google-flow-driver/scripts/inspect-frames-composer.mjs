import { chromium } from 'playwright-core';

async function main() {
  const browser = await chromium.connectOverCDP('http://127.0.0.1:9223');
  const pages = browser.contexts().flatMap(c => c.pages());
  const flow = pages.find(p => p.url().includes('flow.google.com') || p.url().includes('labs.google/fx/tools/flow')) || pages[0];
  console.log('[inspect] Page URL:', flow.url());

  const elements = await flow.evaluate(() => {
    const results = [];
    document.querySelectorAll('input[type="file"]').forEach((inp) => {
      results.push({
        type: 'file_input',
        name: inp.name || '',
        id: inp.id || '',
        accept: inp.accept || '',
        visible: inp.offsetParent !== null,
        className: inp.className
      });
    });

    const buttons = document.querySelectorAll('button, div[role="button"], [role="tab"]');
    buttons.forEach(btn => {
      const rect = btn.getBoundingClientRect();
      const text = (btn.innerText || '').replace(/\s+/g, ' ').trim();
      const ariaLabel = btn.getAttribute('aria-label') || '';
      if (rect.top > window.innerHeight * 0.5 && (text || ariaLabel)) {
        results.push({
          type: 'button',
          tag: btn.tagName,
          text: text.slice(0, 50),
          ariaLabel,
          role: btn.getAttribute('role'),
          top: Math.round(rect.top),
          left: Math.round(rect.left),
          width: Math.round(rect.width),
          height: Math.round(rect.height),
          visible: rect.width > 0 && rect.height > 0
        });
      }
    });

    return results;
  });

  console.log('[inspect] Composer Elements:');
  console.log(JSON.stringify(elements, null, 2));

  await browser.close();
}

main().catch(err => {
  console.error('[inspect] Error:', err.message);
  process.exit(1);
});
