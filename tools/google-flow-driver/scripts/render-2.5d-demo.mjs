import { chromium } from 'playwright-core';
import { execSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';

async function main() {
  const browser = await chromium.connectOverCDP('http://127.0.0.1:9223');
  const context = browser.contexts()[0];
  const page = await context.newPage();

  const htmlPath = path.resolve('content/video_engine/projects/systems-and-blowups/korea-memory-toll/omni-video/demo-2.5d-motion.html');
  console.log('[render-2.5d] Loading:', htmlPath);
  await page.goto(`file:///${htmlPath.replace(/\\/g, '/')}`);
  await page.waitForTimeout(1000);

  const framesDir = path.resolve('content/video_engine/projects/systems-and-blowups/korea-memory-toll/omni-video/clips/temp-frames');
  fs.mkdirSync(framesDir, { recursive: true });

  const viewport = page.locator('#viewport');
  const fps = 24;
  const durationSec = 6;
  const totalFrames = fps * durationSec;

  console.log(`[render-2.5d] Capturing ${totalFrames} frames...`);
  for (let f = 0; f < totalFrames; f++) {
    const timeMs = (f / fps) * 1000;
    // Step deterministic animation clock in page
    await page.evaluate((t) => {
      // Manual render step
      window.manualStep?.(t);
    }, timeMs);

    const frameFile = path.join(framesDir, `frame-${String(f).padStart(4, '0')}.png`);
    await viewport.screenshot({ path: frameFile });
  }

  await page.close();
  await browser.close();

  const outputMp4 = path.resolve('content/video_engine/projects/systems-and-blowups/korea-memory-toll/omni-video/clips/clip-01-2.5d-motion.mp4');
  console.log('[render-2.5d] Stitching with ffmpeg to:', outputMp4);

  const ffmpegCmd = `ffmpeg -y -framerate ${fps} -i "${framesDir}/frame-%04d.png" -c:v libx264 -pix_fmt yuv420p "${outputMp4}"`;
  execSync(ffmpegCmd, { stdio: 'inherit' });

  // Cleanup temp frames
  fs.rmSync(framesDir, { recursive: true, force: true });
  console.log('[render-2.5d] Done! Saved to:', outputMp4);
}

main().catch(err => console.error(err));
