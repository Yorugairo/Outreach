import { chromium } from 'playwright-core';
const browser = await chromium.connectOverCDP('http://127.0.0.1:9223');
const flow = browser.contexts().flatMap(c => c.pages()).find(p => /flow\.google\.com/.test(p.url()));
await flow.locator('text=Characters').first().click(); await flow.waitForTimeout(1200);
const info = await flow.evaluate(() => {
  const el = Array.from(document.querySelectorAll('*')).find(e => e.children.length === 0 && e.textContent.trim() === 'Mike2');
  let tile = el; for (let i = 0; i < 3 && tile.parentElement; i++) tile = tile.parentElement;
  return { leaf: el.tagName + '.' + el.className, leafHtml: el.outerHTML.slice(0, 200), tileTag: tile.tagName + '.' + tile.className, tileHtml: tile.outerHTML.replace(/\s+/g,' ').slice(0, 1200),
           siblings: Array.from(tile.parentElement.children).map(c => c.tagName + '.' + c.className).slice(0, 8) };
});
console.log(JSON.stringify(info, null, 1));
await flow.locator('text=All media').first().click(); await flow.waitForTimeout(600);
await browser.close();
