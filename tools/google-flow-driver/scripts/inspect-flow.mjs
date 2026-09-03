// Inspect the live Flow tab over CDP. Opens the generation settings panel via the UNIQUE
// model pill, targets the mode toggle by EXACT accessible name (the left-nav item is
// "View videos"; the toggle is "Video"), dumps how the selected mode is marked, and -
// only with CLICK=1 - selects Video. Nothing is submitted. Zero credits.
import { chromium } from 'playwright-core';
import fs from 'node:fs';
import path from 'node:path';

const OUT = 'C:/Users/Snipe/Downloads/Outreach Program/review/claims/mp-host-transitions-v1';
const browser = await chromium.connectOverCDP('http://127.0.0.1:9223');
const pages = browser.contexts().flatMap(c => c.pages());
const flow = pages.find(p => p.url().includes('labs.google/fx/tools/flow')) || pages[0];
console.log('inspecting:', flow.url());

const attrs = async (loc) => {
  const n = await loc.count();
  const out = [];
  for (let i = 0; i < n; i++) {
    const el = loc.nth(i);
    out.push(await el.evaluate(e => ({
      tag: e.tagName, role: e.getAttribute('role'), text: (e.innerText || '').replace(/\s+/g, ' ').trim().slice(0, 40),
      pressed: e.getAttribute('aria-pressed'), checked: e.getAttribute('aria-checked'), selected: e.getAttribute('aria-selected'),
      state: e.getAttribute('data-state'), cls: (e.className || '').toString().slice(0, 80),
    })));
  }
  return out;
};

// 1. open the settings panel from the unique model pill (bottom composer)
const pill = flow.locator("button").filter({ hasText: /Nano Banana|Veo|Imagen/ }).last();
console.log('pill:', await pill.innerText().catch(() => '?'));
await pill.click(); await flow.waitForTimeout(800);

// 2. the mode toggles, by EXACT name - never the nav's "View videos"
const modeImage = flow.getByRole('button', { name: /^(image\s*)?Image$/ }).or(flow.getByRole('tab', { name: /^(image\s*)?Image$/ })).or(flow.getByRole('radio', { name: /Image$/ }));
const modeVideo = flow.getByRole('button', { name: /^(videocam\s*)?Video$/ }).or(flow.getByRole('tab', { name: /^(videocam\s*)?Video$/ })).or(flow.getByRole('radio', { name: /Video$/ }));
console.log('Image toggle:', JSON.stringify(await attrs(modeImage)));
console.log('Video toggle:', JSON.stringify(await attrs(modeVideo)));

if (process.env.CLICK === '1' && await modeVideo.count() > 0) {
  await modeVideo.first().click(); await flow.waitForTimeout(1200);
  console.log('clicked Video toggle');
  console.log('Image toggle after:', JSON.stringify(await attrs(modeImage)));
  console.log('Video toggle after:', JSON.stringify(await attrs(modeVideo)));
}
// 3. everything the panel now offers (model / ratio / duration / resolution / count)
const t = await flow.locator("button, [role='button'], [role='tab'], [role='radio'], [role='option'], [role='menuitem']").allInnerTexts();
const panel = [...new Set(t.map(s => s.replace(/\s+/g, ' ').trim()).filter(s => s && s.length < 70))]
  .filter(s => /Image|Video|Veo|Banana|Imagen|\d+s\b|720p|1080p|4K|x[1-4]\b|16:9|9:16|Fast|Quality|Lite|Pro|credit/i.test(s));
console.log('panel:', JSON.stringify(panel));
console.log('pill now:', await pill.innerText().catch(() => '?'));
await flow.screenshot({ path: path.join(OUT, 'flow-video-mode.png') });
fs.writeFileSync(path.join(OUT, 'flow-video-mode.json'), JSON.stringify({ url: flow.url(), panel }, null, 2));
await browser.close();
