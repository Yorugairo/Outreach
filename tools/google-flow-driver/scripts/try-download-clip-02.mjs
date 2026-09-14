import { chromium } from 'playwright-core';
import fs from 'node:fs';
import path from 'node:path';
import { execSync } from 'node:child_process';

async function main() {
  const browser = await chromium.connectOverCDP('http://127.0.0.1:9223');
  const flow = browser.contexts()[0].pages()[0];
  const outputDir = 'C:\\Users\\Snipe\\Downloads\\Outreach Program\\content\\video_engine\\projects\\systems-and-blowups\\korea-memory-toll\\omni-video\\clips';
  const outputPath = path.join(outputDir, 'clip-02-newsroom-to-customs.mp4');
  const framesDir = path.join(outputDir, 'clip-02-frames');

  fs.mkdirSync(outputDir, { recursive: true });
  fs.mkdirSync(framesDir, { recursive: true });

  console.log('[download-clip-02] Locating Download scene button...');
  const downloadBtn = flow.locator('button[aria-label*="Download scene"], button:has-text("download")').filter({ visible: true }).first();

  console.log('Download button count:', await downloadBtn.count());

  if (await downloadBtn.count() > 0) {
    console.log('Found Download scene button! Waiting for download event...');
    const [ download ] = await Promise.all([
      flow.waitForEvent('download', { timeout: 30000 }).catch(() => null),
      downloadBtn.click()
    ]);

    if (download) {
      console.log('Download caught! Saving to:', outputPath);
      await download.saveAs(outputPath);
    } else {
      console.log('Download event not triggered by click, waiting 4s...');
      await flow.waitForTimeout(4000);
    }
  }

  // Check file size
  if (fs.existsSync(outputPath)) {
    const size = fs.statSync(outputPath).size;
    console.log(`Output file exists: ${size} bytes`);
    if (size > 500000) {
      console.log('Extracting 10 frames with ffmpeg...');
      const framePattern = path.join(framesDir, 'frame-%02d.png');
      execSync(`ffmpeg -y -i "${outputPath}" -vf "fps=1" "${framePattern}"`, { stdio: 'inherit' });
      console.log('Frames extracted successfully to', framesDir);
    } else {
      console.log('File is too small (<500KB), might still be generating or an image');
    }
  } else {
    console.log('Output file does not exist yet');
  }

  await browser.close();
}

main().catch(err => console.error(err));
