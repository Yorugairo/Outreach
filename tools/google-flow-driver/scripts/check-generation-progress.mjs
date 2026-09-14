import { chromium } from 'playwright-core';

async function main() {
  const browser = await chromium.connectOverCDP('http://127.0.0.1:9223');
  const flow = browser.contexts()[0].pages()[0];

  const info = await flow.evaluate(() => {
    // Find generating cards or progress text
    const textNodes = Array.from(document.querySelectorAll('*'))
      .filter(el => el.children.length === 0 && /\b\d+%\b/.test(el.innerText))
      .map(el => el.innerText.trim());

    const videos = Array.from(document.querySelectorAll('video')).map(v => v.src || v.getAttribute('src')).filter(Boolean);

    return {
      progressTexts: textNodes,
      totalVideos: videos.length,
      latestVideo: videos[0] || null
    };
  });

  console.log('Progress check:', JSON.stringify(info, null, 2));
  await browser.close();
}

main().catch(err => console.error(err));
