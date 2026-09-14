import { chromium } from 'playwright-core';
const browser = await chromium.connectOverCDP('http://127.0.0.1:9223');
const flow = browser.contexts().flatMap(c => c.pages()).find(p => /flow\.google\.com/.test(p.url()));
const info = await flow.evaluate(() => {
  const btn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.trim() === 'tune');
  let box = btn; for (let i = 0; i < 4 && box.parentElement; i++) box = box.parentElement;
  const vis = e => { const r = e.getBoundingClientRect(); return [Math.round(r.x), Math.round(r.y), Math.round(r.width), Math.round(r.height)]; };
  return {
    viewport: [innerWidth, innerHeight, document.documentElement.scrollHeight],
    tuneBox: vis(btn), tuneAria: btn.getAttribute('aria-label'),
    composerText: box.innerText.replace(/\s+/g, ' ').slice(0, 400),
    composerHtml: box.outerHTML.slice(0, 2500),
    textareas: Array.from(document.querySelectorAll('textarea,[contenteditable=true]')).map(t => [t.tagName, t.getAttribute('placeholder') || t.getAttribute('aria-label'), ...vis(t)]),
  };
});
console.log(JSON.stringify(info, null, 1));
await flow.screenshot({ path: 'runtime/composer.png', clip: { x: 0, y: Math.max(0, info.viewport[1] - 260), width: info.viewport[0], height: 260 } });
await browser.close();
