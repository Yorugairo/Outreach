import { chromium } from 'playwright-core';
const browser = await chromium.connectOverCDP('http://127.0.0.1:9223');
const flow = browser.contexts().flatMap(c => c.pages()).find(p => /flow\.google\.com/.test(p.url()));
const ids = await flow.evaluate(() => Array.from(document.querySelectorAll('img[src*="flow-content.google/image/"]')).map(i => (i.src.match(/image\/([0-9a-f-]{36})/)||[])[1]).filter(Boolean));
console.log('images in DOM order (first 12):', JSON.stringify(ids.slice(0, 12)));
console.log('total img tiles:', ids.length, 'unique:', new Set(ids).size);
await browser.close();
