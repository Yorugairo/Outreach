import { chromium } from 'playwright-core';

async function main() {
  const browser = await chromium.connectOverCDP('http://127.0.0.1:9223');
  const flow = browser.contexts()[0].pages()[0];

  // Dismiss any overlays
  await flow.keyboard.press('Escape');
  await flow.waitForTimeout(300);

  const state = await flow.evaluate(() => {
    const frameTriggers = Array.from(document.querySelectorAll('.frame-trigger, .chip-container, button.empty-chip')).map(el => ({
      tag: el.tagName,
      className: el.className,
      text: el.innerText.trim(),
      hasImg: Boolean(el.querySelector('img'))
    }));

    const editor = document.querySelector("div[contenteditable='true']");
    const chips = Array.from(document.querySelectorAll('.mention-chip')).map(c => c.innerText.trim());

    return {
      frameTriggers,
      editorText: editor ? editor.innerText.trim() : '',
      chips
    };
  });

  console.log('Current composer state:', JSON.stringify(state, null, 2));
  await browser.close();
}

main().catch(err => console.error(err));
