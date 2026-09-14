import { chromium } from 'playwright-core';

async function main() {
  const browser = await chromium.connectOverCDP('http://127.0.0.1:9223');
  const flow = browser.contexts()[0].pages()[0];

  const media = await flow.evaluate(() => {
    return Array.from(document.querySelectorAll('img')).map(img => ({
      alt: img.getAttribute('alt') || '',
      src: img.src || '',
      width: img.naturalWidth || img.width,
      height: img.naturalHeight || img.height
    })).filter(m => m.width > 100);
  });

  console.log('Project images count:', media.length);
  console.log(JSON.stringify(media.slice(0, 10), null, 2));

  await browser.close();
}

main().catch(err => console.error(err));
