import { chromium } from 'playwright-core';
import fs from 'node:fs';
import path from 'node:path';
import { execSync } from 'node:child_process';

async function main() {
  const browser = await chromium.connectOverCDP('http://127.0.0.1:9223');
  const flow = browser.contexts()[0].pages()[0];
  const outputDir = 'C:\\Users\\Snipe\\Downloads\\Outreach Program\\content\\video_engine\\projects\\systems-and-blowups\\korea-memory-toll\\omni-video\\clips';
  const outputPath = path.join(outputDir, 'test-02-harbor-to-newsroom.mp4');
  const framesDir = path.join(outputDir, 'test-02-frames');

  fs.mkdirSync(outputDir, { recursive: true });
  fs.mkdirSync(framesDir, { recursive: true });

  // Let's click the item with alt="Man transitioning to newsroom"
  const item = flow.locator('img[alt*="Man transitioning to newsroom"]').first();
  console.log('Item count:', await item.count());
  if (await item.count() > 0) {
    await item.click();
    await flow.waitForTimeout(1500);
  }

  // Let's check if a video element or dialog opened
  const pageState = await flow.evaluate(() => {
    const vids = Array.from(document.querySelectorAll('video')).map(v => v.src || v.getAttribute('src'));
    const downloadBtns = Array.from(document.querySelectorAll('button, a'))
      .filter(el => /download|arrow_downward|save/i.test(el.innerText || el.getAttribute('aria-label') || ''))
      .map(el => ({ text: el.innerText, aria: el.getAttribute('aria-label') }));

    return { vids, downloadBtns };
  });

  console.log('Page state after clicking thumbnail:', JSON.stringify(pageState, null, 2));

  // If video element exists, download it
  if (pageState.vids.length > 0 && pageState.vids[0]) {
    const src = pageState.vids[0];
    console.log('Found video URL:', src);
    const response = await flow.context().request.get(src);
    const videoBuffer = await response.body();
    fs.writeFileSync(outputPath, videoBuffer);
    console.log(`Saved video to ${outputPath} (${videoBuffer.length} bytes)`);

    // Extract frames
    const framePattern = path.join(framesDir, 'frame-%02d.png');
    execSync(`ffmpeg -y -i "${outputPath}" -vf "fps=1" "${framePattern}"`, { stdio: 'inherit' });
    console.log('Extracted frames successfully to', framesDir);
  } else {
    // Let's take a screenshot so we see what clicking it did
    await flow.screenshot({ path: path.join(outputDir, 'after-click-newsroom.png') });
    console.log('Saved after-click-newsroom.png');
  }

  await browser.close();
}

main().catch(err => console.error(err));
