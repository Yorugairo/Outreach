import { chromium } from 'playwright-core';
const browser = await chromium.connectOverCDP('http://127.0.0.1:9223');
const pages = browser.contexts().flatMap(c => c.pages());
console.log('tabs:', pages.map(p => p.url()));
const flow = pages.find(p => /flow\.google\.com|labs\.google\/fx/.test(p.url())) || pages[0];
await flow.bringToFront();
const info = await flow.evaluate(() => ({
  url: location.href, title: document.title,
  chips: Array.from(document.querySelectorAll('.mention-chip')).map(c => c.innerText.trim()),
  buttons: Array.from(document.querySelectorAll('button')).map(b => b.innerText.trim().replace(/\s+/g,' ')).filter(t => t && t.length < 40),
  dialogs: Array.from(document.querySelectorAll('[role=dialog]')).map(d => d.innerText.trim().slice(0,120)),
}));
console.log(JSON.stringify(info, null, 1));
await flow.screenshot({ path: 'C:/Users/Snipe/AppData/Local/Temp/claude/C--Users-Snipe-Downloads-Outreach-Program--claude-worktrees-sweet-villani-1c3a16/45114c3b-258a-4ca8-9aaf-b674a804cc7e/scratchpad/flow_state.png' });
await browser.close();
