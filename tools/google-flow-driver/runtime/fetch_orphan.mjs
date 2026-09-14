import { chromium } from 'playwright-core';
import fs from 'node:fs';
const browser = await chromium.connectOverCDP('http://127.0.0.1:9223');
const flow = browser.contexts().flatMap(c => c.pages()).find(p => /flow\.google\.com/.test(p.url()));
const src = await flow.evaluate(() => Array.from(document.querySelectorAll('img[src*="flow-content.google/image/"]')).map(i => i.src).find(s => s.includes('86509336')));
const bytes = await flow.evaluate(async (u) => { const r = await fetch(u); const b = await r.arrayBuffer(); return Array.from(new Uint8Array(b)); }, src);
const out = 'C:/Users/Snipe/AppData/Local/Temp/claude/C--Users-Snipe-Downloads-Outreach-Program--claude-worktrees-sweet-villani-1c3a16/45114c3b-258a-4ca8-9aaf-b674a804cc7e/scratchpad/orphan-86509336.png';
fs.writeFileSync(out, Buffer.from(bytes)); console.log('saved', bytes.length, 'bytes');
await browser.close();
