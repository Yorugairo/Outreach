import { chromium } from 'playwright-core';
import fs from 'node:fs';
import path from 'node:path';
import { execSync } from 'node:child_process';

async function main() {
  const browser = await chromium.connectOverCDP('http://127.0.0.1:9223');
  const flow = browser.contexts()[0].pages()[0];
  const outputDir = 'C:\\Users\\Snipe\\Downloads\\Outreach Program\\content\\video_engine\\projects\\systems-and-blowups\\korea-memory-toll\\omni-video\\clips';
  const outputPath = path.join(outputDir, 'test-02-harbor-to-newsroom-completed.mp4');
  const framesDir = path.join(outputDir, 'test-02-frames');

  fs.mkdirSync(outputDir, { recursive: true });
  fs.mkdirSync(framesDir, { recursive: true });

  console.log('[download-new] Inspecting completed video card...');

  // The first card in the grid is the newly finished video. Let's click it to open the player.
  const firstCard = flow.locator('.asset-item, .card, [role="button"], div').filter({ has: flow.locator('i:has-text("play_arrow"), span:has-text("play_arrow"), [data-icon="play"]') }).first();
  console.log('First card found count:', await firstCard.count());

  // Let's get all video elements or click the first card
  const cards = flow.locator('div').filter({ hasText: /play_arrow/ });
  console.log('Play arrow elements:', await cards.count());

  // Click the top-left video item in the gallery
  const galleryItems = flow.locator('cdk-virtual-scroll-viewport .asset-item, .gallery-item, .asset-card, div.asset-wrapper').first();
  // Or simply click at the coordinates of the first card from the screenshot (x: ~360, y: ~90)
  // Let's evaluate to find the exact element that corresponds to the first item:
  const firstVideoData = await flow.evaluate(async () => {
    // Find all video cards or thumbnails
    const items = Array.from(document.querySelectorAll('.asset-item, [role="gridcell"], .grid-item, div')).filter(el => {
      return el.querySelector('i')?.innerText === 'play_arrow' || el.innerText?.includes('play_arrow');
    });

    return items.map(el => ({
      tag: el.tagName,
      className: el.className,
      text: el.innerText?.slice(0, 50)
    }));
  });

  console.log('Video cards detected:', JSON.stringify(firstVideoData.slice(0, 5), null, 2));

  // Let's click the top-left card
  await flow.mouse.click(360, 90);
  await flow.waitForTimeout(1500);

  // Now inspect the video tag in the player modal
  const playerVideoSrc = await flow.evaluate(() => {
    const vids = Array.from(document.querySelectorAll('video'));
    return vids.map(v => v.src || v.getAttribute('src'));
  });

  console.log('Player video sources:', playerVideoSrc);

  const activeSrc = playerVideoSrc.find(s => s && s.length > 10);
  if (!activeSrc) {
    throw new Error('No active video source found after clicking card');
  }

  console.log('Active video source:', activeSrc);

  // Download video buffer
  let videoBuffer;
  try {
    const videoBytes = await flow.evaluate(async (src) => {
      const resp = await fetch(src);
      const blob = await resp.blob();
      const arrayBuf = await blob.arrayBuffer();
      return Array.from(new Uint8Array(arrayBuf));
    }, activeSrc);
    videoBuffer = Buffer.from(videoBytes);
    console.log(`Downloaded ${videoBuffer.length} bytes via page evaluate.`);
  } catch (err) {
    console.log('Evaluate fetch failed, using request context:', err.message);
    const response = await flow.context().request.get(activeSrc);
    videoBuffer = await response.body();
    console.log(`Downloaded ${videoBuffer.length} bytes via request context.`);
  }

  fs.writeFileSync(outputPath, videoBuffer);
  console.log(`Saved video to ${outputPath}`);

  // Extract frames
  console.log('Extracting 10 frames with ffmpeg...');
  const framePattern = path.join(framesDir, 'frame-%02d.png');
  execSync(`ffmpeg -y -i "${outputPath}" -vf "fps=1" "${framePattern}"`, { stdio: 'inherit' });
  console.log('Extracted frames to', framesDir);

  await browser.close();
}

main().catch(err => {
  console.error('[download-new] Error:', err);
  process.exit(1);
});
