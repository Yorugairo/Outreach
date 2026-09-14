import { chromium } from 'playwright-core';

async function main() {
  const browser = await chromium.connectOverCDP('http://127.0.0.1:9223');
  const flow = browser.contexts()[0].pages()[0];

  const state = await flow.evaluate(() => {
    // Check start and end chips
    const frameTriggers = Array.from(document.querySelectorAll('.frame-trigger, .chip-container, button.empty-chip')).map(el => ({
      tag: el.tagName,
      className: el.className,
      text: (el.innerText || '').replace(/\s+/g, ' ').trim(),
      hasImg: Boolean(el.querySelector('img')),
      imgSrc: el.querySelector('img')?.src || null
    }));

    // Check editor content and chips
    const editor = document.querySelector("div[data-slate-editor='true'], div[contenteditable='true']");
    const chips = Array.from(document.querySelectorAll('.mention-chip')).map(c => c.innerText.trim());

    return {
      frameTriggers,
      editorText: editor ? editor.innerText.replace(/\s+/g, ' ').trim() : null,
      mentionChips: chips
    };
  });

  console.log('[composer state]:', JSON.stringify(state, null, 2));
  await browser.close();
}

main().catch(err => console.error(err));
