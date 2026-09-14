import { chromium } from 'playwright-core';

async function main() {
  const browser = await chromium.connectOverCDP('http://127.0.0.1:9223');
  const flow = browser.contexts()[0].pages()[0];

  const data = await flow.evaluate(() => {
    // Find all images and their nearest parent buttons/links/cards
    const imgs = Array.from(document.querySelectorAll('img')).map(img => {
      const rect = img.getBoundingClientRect();
      let parent = img.parentElement;
      while (parent && parent !== document.body && !parent.getAttribute('role') && !parent.className.includes('card') && !parent.className.includes('item')) {
        parent = parent.parentElement;
      }
      return {
        src: img.src?.slice(0, 80),
        alt: img.alt,
        rect: { x: Math.round(rect.x), y: Math.round(rect.y), w: Math.round(rect.width), h: Math.round(rect.height) },
        parentRole: parent?.getAttribute('role'),
        parentClass: parent?.className?.slice(0, 50)
      };
    });

    const videos = Array.from(document.querySelectorAll('video')).map(v => ({
      src: v.src || v.getAttribute('src'),
      rect: v.getBoundingClientRect()
    }));

    return {
      imgs: imgs.slice(0, 10),
      videos
    };
  });

  console.log(JSON.stringify(data, null, 2));
  await browser.close();
}

main().catch(err => console.error(err));
