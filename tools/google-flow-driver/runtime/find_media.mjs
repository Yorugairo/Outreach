import { chromium } from 'playwright-core';
const browser = await chromium.connectOverCDP('http://127.0.0.1:9223');
const pages = browser.contexts().flatMap(c => c.pages());
console.log('tabs:', pages.map(p => p.url()));
const flow = pages.find(p => /flow\.google\.com/.test(p.url()));
const info = await flow.evaluate((needle) => {
  const html = document.documentElement.outerHTML;
  const i = html.indexOf(needle);
  const ids = Array.from(document.querySelectorAll('img[src*="flow-content.google/image/"]')).map(im => (im.src.match(/image\/([0-9a-f-]{36})/)||[])[1]).filter(Boolean);
  return { url: location.href, needleAt: i, around: i >= 0 ? html.slice(Math.max(0, i-300), i+120).replace(/\s+/g,' ') : null, newest: ids.slice(0, 6) };
}, '499a2cb4');
console.log(JSON.stringify(info, null, 1));
await browser.close();
