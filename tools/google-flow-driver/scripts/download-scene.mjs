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

  console.log('[download-scene] Clicking download button for scene...');
  const downloadBtn = flow.locator('button[aria-label*="Download scene"], button:has-text("download")').filter({ visible: true }).first();

  if (await downloadBtn.count() > 0) {
    console.log('[download-scene] Found download button, clicking...');
    
    // Listen for download event
    const [ download ] = await Promise.all([
      flow.waitForEvent('download', { timeout: 30000 }).catch(() => null),
      downloadBtn.click()
    ]);

    if (download) {
      console.log('[download-scene] Download event captured! Saving to:', outputPath);
      await download.saveAs(outputPath);
    } else {
      console.log('[download-scene] No download event caught directly. Checking recent downloads or video network requests...');
      // Check if file was saved in default download directory or check network
      await flow.waitForTimeout(4000);
    }
  }

  // Check if outputPath exists
  if (fs.existsSync(outputPath) && fs.statSync(outputPath).size > 1000) {
    console.log(`[download-scene] Successfully downloaded video (${fs.statSync(outputPath).size} bytes)!`);
    console.log('[download-scene] Extracting 10 frames with ffmpeg...');
    const framePattern = path.join(framesDir, 'frame-%02d.png');
    execSync(`ffmpeg -y -i "${outputPath}" -vf "fps=1" "${framePattern}"`, { stdio: 'inherit' });
    console.log('[download-scene] Extracted frames to', framesDir);
  } else {
    console.log('[download-scene] Output file not found yet. Checking downloads directory or page inspect.');
  }

  await browser.close();
}

main().catch(err => {
  console.error('[download-scene] Error:', err);
  process.exit(1);
});
