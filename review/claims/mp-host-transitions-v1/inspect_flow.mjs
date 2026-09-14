// Read-only look at the live Flow tab over CDP: screenshot + the generation-mode/settings text.
// Never clicks, never types. Run from tools/google-flow-driver so its playwright resolves.
import { chromium } from 'playwright';
import fs from 'node:fs';
import path from 'node:path';

const OUT = 'C:/Users/Snipe/Downloads/Outreach Program/review/claims/mp-host-transitions-v1';
const browser = await chromium.connectOverCDP('http://127.0.0.1:9223');
const pages = browser.contexts().flatMap(c => c.pages());
const flow = pages.find(p => p.url().includes('labs.google/fx/tools/flow')) || pages[0];
console.log('tabs:', pages.map(p => p.url()).join(' | '));
console.log('inspecting:', flow?.url());
if (!flow) { console.log('no page'); process.exit(1); }

await flow.screenshot({ path: path.join(OUT, 'flow-state.png'), fullPage: false });

// Every button/pill text - the mode toggle and the settings pill live here
const buttons = await flow.locator("button, div[role='button'], [role='tab']").allInnerTexts();
const trimmed = buttons.map(t => t.replace(/\s+/g, ' ').trim()).filter(t => t && t.length < 60);
console.log('buttons/pills:', JSON.stringify([...new Set(trimmed)].slice(0, 80)));
console.log('video elements:', await flow.locator('video').count(), ' img elements:', await flow.locator('img').count());
console.log('file inputs:', await flow.locator("input[type='file']").count());
fs.writeFileSync(path.join(OUT, 'flow-state.json'), JSON.stringify({ url: flow.url(), buttons: [...new Set(trimmed)] }, null, 2));
await browser.close();
