import { chromium } from 'playwright-core';

async function main() {
  const browser = await chromium.connectOverCDP('http://127.0.0.1:9223');
  const pages = browser.contexts().flatMap(c => c.pages());
  const flow = pages.find(p => p.url().includes('flow.google.com') || p.url().includes('labs.google/fx/tools/flow')) || pages[0];

  const info = await flow.evaluate(() => {
    const btns = Array.from(document.querySelectorAll('button')).filter(b => b.innerText.includes('Start'));
    return btns.map(b => ({
      outerHTML: b.outerHTML,
      innerText: b.innerText,
      rect: b.getBoundingClientRect()
    }));
  });

  console.log('[inspect] Start buttons:', JSON.stringify(info, null, 2));
  await browser.close();
}

main().catch(err => console.error(err));
