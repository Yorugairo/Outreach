import { chromium } from 'playwright-core';
const browser = await chromium.connectOverCDP('http://127.0.0.1:9223');
const flow = browser.contexts().flatMap(c => c.pages()).find(p => /flow\.google\.com/.test(p.url()));
const state = () => flow.evaluate(() => ({
  agent: document.querySelector('flow-agent-mode-toggle-chip button')?.getAttribute('aria-pressed'),
  buttons: Array.from(document.querySelectorAll('button')).map(b => b.innerText.trim().replace(/\s+/g,' ')).filter(t => t && t.length < 60 && !/^(home|more_vert|search|filter_list|add|help|settings_2|expand_content)$/.test(t)),
}));
console.log('before', JSON.stringify(await state()));
await flow.click('flow-agent-mode-toggle-chip button');
await flow.waitForTimeout(1200);
console.log('after ', JSON.stringify(await state()));
await browser.close();
