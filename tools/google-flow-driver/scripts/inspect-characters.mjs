// Read-only: open the project's Characters view and dump every character card's name and
// description text - Flow's OWN terminology for the host. Navigation only; nothing generated.
import { chromium } from 'playwright-core';
import fs from 'node:fs';
const OUT = 'C:/Users/Snipe/Downloads/Outreach Program/review/claims/mp-host-transitions-v1';
const browser = await chromium.connectOverCDP('http://127.0.0.1:9223');
const flow = browser.contexts().flatMap(c => c.pages()).find(p => p.url().includes('labs.google/fx/tools/flow'));
const nav = flow.getByRole('button', { name: /Characters/ }).or(flow.getByText(/^(accessibility_new\s*)?Characters$/)).first();
if (await nav.count()) { await nav.click(); await flow.waitForTimeout(1500); }
await flow.screenshot({ path: `${OUT}/flow-characters.png` });
const cards = await flow.locator("[class*='card'], [role='listitem'], article, a[href*='character'], div:has(> img)").allInnerTexts();
const texts = [...new Set(cards.map(t => t.replace(/\s+/g, ' ').trim()).filter(t => t && t.length > 3 && t.length < 400))];
console.log('character-ish texts:', JSON.stringify(texts.slice(0, 20), null, 1));
// try opening the first character card to read its saved description
const first = flow.getByText(/Untitled Character|Character/).first();
if (await first.count()) { await first.click(); await flow.waitForTimeout(1500); await flow.screenshot({ path: `${OUT}/flow-character-open.png` });
  const body = (await flow.locator('body').innerText()).replace(/\s+/g, ' ');
  const m = body.match(/.{0,200}(description|prompt|appearance|wearing|suit|glasses|locs).{0,300}/i);
  console.log('open card text near identity words:', m ? m[0] : '(none found)');
}
fs.writeFileSync(`${OUT}/flow-characters.json`, JSON.stringify({ texts }, null, 2));
await browser.close();
