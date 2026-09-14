import { chromium } from 'playwright-core';
import path from 'node:path';
import fs from 'node:fs';

async function main() {
  const browser = await chromium.connectOverCDP('http://127.0.0.1:9223');
  const flow = browser.contexts()[0].pages()[0];
  const outDir = 'C:\\Users\\Snipe\\Downloads\\Outreach Program\\content\\video_engine\\projects\\systems-and-blowups\\korea-memory-toll\\omni-video\\clips';

  // Take screenshot of current page
  await flow.screenshot({ path: path.join(outDir, 'flow-current-status.png'), fullPage: false });
  console.log('Saved flow-current-status.png');

  // Check texts, toasts, error banners, video elements, cards
  const pageState = await flow.evaluate(() => {
    const toasts = Array.from(document.querySelectorAll('.snack-bar, [role="alert"], .error, .toast, .mat-snack-bar-container')).map(el => el.innerText.trim());
    const videos = Array.from(document.querySelectorAll('video')).map(v => ({
      src: v.src || v.getAttribute('src'),
      paused: v.paused,
      duration: v.duration
    }));
    const buttons = Array.from(document.querySelectorAll('button')).map(b => (b.innerText || b.getAttribute('aria-label') || '').trim()).filter(Boolean);
    const progress = Array.from(document.querySelectorAll('[role="progressbar"], .progress, .loading, .spinner')).length;

    return {
      toasts,
      videos,
      progressCount: progress,
      buttons: buttons.slice(-15)
    };
  });

  console.log('Page state:', JSON.stringify(pageState, null, 2));

  await browser.close();
}

main().catch(err => console.error(err));
