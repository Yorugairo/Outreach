import { chromium } from 'playwright-core';
import fs from 'node:fs';
import path from 'node:path';
import { execSync } from 'node:child_process';

async function main() {
  const browser = await chromium.connectOverCDP('http://127.0.0.1:9223');
  const flow = browser.contexts()[0].pages()[0];
  const outputDir = 'C:\\Users\\Snipe\\Downloads\\Outreach Program\\content\\video_engine\\projects\\systems-and-blowups\\korea-memory-toll\\omni-video\\clips';
  const outputPath = path.join(outputDir, 'test-02-harbor-action-intra.mp4');
  const framesDir = path.join(outputDir, 'test-02-action-frames');

  fs.mkdirSync(outputDir, { recursive: true });
  fs.mkdirSync(framesDir, { recursive: true });

  console.log('[download-test-b] Clicking the top-left video card (Test B)...');

  // Click at the center of the first video card (x: 355, y: 140)
  await flow.mouse.click(355, 140);
  await flow.waitForTimeout(2000);

  // Check if player opened and find download button or video element
  const info = await flow.evaluate(() => {
    const vids = Array.from(document.querySelectorAll('video')).map(v => v.src || v.getAttribute('src'));
    const btns = Array.from(document.querySelectorAll('button, a')).map(b => ({
      text: (b.innerText || '').trim(),
      aria: b.getAttribute('aria-label') || ''
    }));
    return { vids, btns };
  });

  console.log('Player info:', JSON.stringify(info, null, 2));

  // If download button is present
  const downloadBtn = flow.locator('button[aria-label*="Download scene"], button:has-text("download")').filter({ visible: true }).first();

  if (await downloadBtn.count() > 0) {
    console.log('Found download button! Capturing download event...');
    const [ download ] = await Promise.all([
      flow.waitForEvent('download', { timeout: 30000 }).catch(() => null),
      downloadBtn.click()
    ]);

    if (download) {
      console.log('Download caught! Saving to:', outputPath);
      await download.saveAs(outputPath);
    }
  }

  // Fallback: If video src is in the DOM
  if (!fs.existsSync(outputPath) || fs.statSync(outputPath).size < 10000) {
    const validSrc = info.vids.find(s => s && s.length > 20);
    if (validSrc) {
      console.log('Downloading via APIRequestContext from:', validSrc);
      const resp = await flow.context().request.get(validSrc);
      const buf = await resp.body();
      fs.writeFileSync(outputPath, buf);
    }
  }

  if (fs.existsSync(outputPath) && fs.statSync(outputPath).size > 100000) {
    console.log(`Successfully saved Test B video (${fs.statSync(outputPath).size} bytes) to ${outputPath}`);
    console.log('Extracting 10 frames with ffmpeg...');
    const framePattern = path.join(framesDir, 'frame-%02d.png');
    execSync(`ffmpeg -y -i "${outputPath}" -vf "fps=1" "${framePattern}"`, { stdio: 'inherit' });
    console.log('Frames extracted successfully to', framesDir);
  } else {
    throw new Error('Test B video could not be downloaded');
  }

  await browser.close();
}

main().catch(err => {
  console.error('[download-test-b] Error:', err);
  process.exit(1);
});
