import { chromium } from 'playwright-core';

async function main() {
  const browser = await chromium.connectOverCDP('http://127.0.0.1:9223');
  const flow = browser.contexts()[0].pages()[0];

  const info = await flow.evaluate(() => {
    const ed = document.querySelector("div[contenteditable='true']");
    const triggers = Array.from(document.querySelectorAll('.frame-trigger')).map(el => ({
      text: el.innerText.trim(),
      hasImg: Boolean(el.querySelector('img')),
      src: el.querySelector('img')?.src || null
    }));
    const buttons = Array.from(document.querySelectorAll('button')).map(b => ({
      text: b.innerText.trim(),
      aria: b.getAttribute('aria-label') || '',
      disabled: b.disabled
    })).filter(b => b.text.includes('arrow_forward') || b.aria.includes('Start generation') || b.text.includes('Start'));

    return {
      hasEditor: Boolean(ed),
      editorText: ed ? ed.innerText.trim() : null,
      triggers,
      buttons
    };
  });

  console.log('Editor info:', JSON.stringify(info, null, 2));
  await browser.close();
}

main().catch(err => console.error(err));
