import fs from 'node:fs';
import path from 'node:path';
import { chromium } from 'playwright-core';

export class FlowCdpDriver {
  constructor(options = {}) {
    this.port = options.port || 9223;
    this.browser = null;
    this.flowPage = null;
  }

  async getWsEndpoint() {
    // 1. Check dedicated automation profile DevToolsActivePort first (Port 9223)
    const flowProfilePath = path.join('C:\\Users\\Snipe\\.flow-chrome-profile', 'DevToolsActivePort');
    if (fs.existsSync(flowProfilePath)) {
      const lines = fs.readFileSync(flowProfilePath, 'utf8').trim().split(/\r?\n/);
      return `ws://127.0.0.1:${lines[0]}${lines[1]}`;
    }

    // 2. Direct connection to dedicated port 9223
    try {
      return 'http://127.0.0.1:9223';
    } catch {}

    // 3. Fallback to default Chrome User Data port 9222
    const defaultPath = path.join(
      process.env.LOCALAPPDATA || '',
      'Google', 'Chrome', 'User Data', 'DevToolsActivePort'
    );
    if (fs.existsSync(defaultPath)) {
      const lines = fs.readFileSync(defaultPath, 'utf8').trim().split(/\r?\n/);
      return `ws://127.0.0.1:${lines[0]}${lines[1]}`;
    }

    return `http://127.0.0.1:9222`;
  }

  async connect() {
    const endpoint = await this.getWsEndpoint();
    try {
      this.browser = await chromium.connectOverCDP(endpoint);
    } catch (e) {
      // If 9223 fails, try 9222
      if (!endpoint.includes('9222')) {
        this.browser = await chromium.connectOverCDP('http://127.0.0.1:9222');
      } else {
        throw e;
      }
    }
    return this.browser;
  }

  async getFlowPage(targetUrl = null) {
    if (!this.browser) await this.connect();
    
    // Scan existing open tabs
    for (const ctx of this.browser.contexts()) {
      for (const page of ctx.pages()) {
        const url = page.url();
        if (url.includes('labs.google/fx/tools/flow')) {
          this.flowPage = page;
          if (targetUrl && url !== targetUrl) {
            await page.goto(targetUrl, { waitUntil: 'domcontentloaded' });
          }
          await page.bringToFront().catch(() => {});
          return this.flowPage;
        }
      }
    }

    // If not found, navigate active page or open new page
    const ctx = this.browser.contexts()[0];
    const page = ctx.pages()[0] || await ctx.newPage();
    const dest = targetUrl || 'https://labs.google/fx/tools/flow';
    await page.goto(dest, { waitUntil: 'domcontentloaded' });
    this.flowPage = page;
    await page.bringToFront().catch(() => {});
    return this.flowPage;
  }

  async configureSettings({ ratio = null, duration = null, resolution = null } = {}) {
    const page = this.flowPage;
    if (!page) throw new Error('No active Flow page');

    // Only open settings modal if at least one explicit setting was specified
    if (!ratio && !duration && !resolution) {
      return; // Preserve existing project canvas settings
    }

    // Click settings pill (e.g. "Video · 720p · 6s")
    const pill = page.locator("button:has-text('Video'), div[role='button']:has-text('Video'), button:has-text('720p'), button:has-text('1080p')").last();
    if (await pill.count() > 0) {
      await pill.click();
      await page.waitForTimeout(600);

      // Select Ratio ONLY if explicitly requested ('9:16' or '16:9')
      if (ratio === '9:16' || ratio === '16:9') {
        const ratioTarget = ratio;
        const ratioBtn = page.locator(`button:has-text('${ratioTarget}'), div[role='button']:has-text('${ratioTarget}')`).first();
        if (await ratioBtn.count() > 0) {
          await ratioBtn.click();
          await page.waitForTimeout(300);
        }
      }

      // Select Duration only if specified (e.g. 4, 6, 8)
      if (duration) {
        const durTarget = `${duration}s`;
        const durBtn = page.locator(`button:has-text('${durTarget}'), div[role='button']:has-text('${durTarget}')`).first();
        if (await durBtn.count() > 0) {
          await durBtn.click();
          await page.waitForTimeout(200);
        }
      }

      // Select Resolution only if specified ('720p' or '1080p')
      if (resolution) {
        const resBtn = page.locator(`button:has-text('${resolution}')`).first();
        if (await resBtn.count() > 0) {
          await resBtn.click();
          await page.waitForTimeout(200);
        }
      }

      // Close settings modal cleanly
      await page.keyboard.press('Escape');
      await page.waitForTimeout(400);
    }
  }

  async uploadReferences(filePaths = []) {
    const page = this.flowPage;
    if (!page) throw new Error('No active Flow page');
    if (!filePaths || filePaths.length === 0) return;

    const validPaths = filePaths.filter(p => fs.existsSync(p));
    if (validPaths.length === 0) {
      throw new Error(`None of the provided reference paths exist: ${filePaths.join(', ')}`);
    }

    const fileInput = page.locator("input[type='file']").first();
    if (await fileInput.count() === 0) {
      throw new Error("Could not find file input in Flow page.");
    }

    // Pass up to 3 references simultaneously
    const uploadList = validPaths.slice(0, 3);
    await fileInput.setInputFiles(uploadList);
    await page.waitForTimeout(1500);
  }

  async setPrompt(promptText) {
    const page = this.flowPage;
    if (!page) throw new Error('No active Flow page');

    const editor = page.locator("div[data-slate-editor='true'], div[contenteditable='true']").first();
    if (await editor.count() === 0) {
      throw new Error("Could not find prompt editor in Flow page.");
    }

    await editor.click();
    await editor.fill(promptText);
    await page.waitForTimeout(500);
  }

  async triggerGeneration() {
    const page = this.flowPage;
    if (!page) throw new Error('No active Flow page');

    let submitBtn = page.locator("button[aria-label*='Submit'], button[aria-label*='Generate'], button:has-text('arrow_forward'), button:has-text('➔')").first();
    if (await submitBtn.count() === 0) {
      submitBtn = page.locator("button:has(svg)").last();
    }
    if (await submitBtn.count() === 0) {
      throw new Error("Could not find submit button on Flow page.");
    }

    await submitBtn.click();
    await page.waitForTimeout(2000);
  }

  async waitForGenerationAndDownload(rawOutputPath, timeoutMs = 180000) {
    const page = this.flowPage;
    if (!page) throw new Error('No active Flow page');

    const startTime = Date.now();
    let prevVideoSrc = null;
    const existingVideo = page.locator("video").first();
    if (await existingVideo.count() > 0) {
      prevVideoSrc = await existingVideo.getAttribute("src");
    }

    console.log(`[FlowCdpDriver] Waiting for video generation to complete (timeout: ${timeoutMs}ms)...`);

    let settledSrc = null;
    while (Date.now() - startTime < timeoutMs) {
      const currentVideo = page.locator("video").first();
      if (await currentVideo.count() > 0) {
        const src = await currentVideo.getAttribute("src");
        if (src && src.includes('getMediaUrlRedirect')) {
          if (!prevVideoSrc || src !== prevVideoSrc) {
            settledSrc = src;
            break;
          }
        }
      }
      await page.waitForTimeout(3000);
    }

    if (!settledSrc) {
      throw new Error(`Video generation timed out after ${timeoutMs}ms.`);
    }

    console.log(`[FlowCdpDriver] Video generation finished! Source endpoint: ${settledSrc}`);

    const videoBytes = await page.evaluate(async (src) => {
      const resp = await fetch(src);
      const blob = await resp.blob();
      const arrayBuf = await blob.arrayBuffer();
      return Array.from(new Uint8Array(arrayBuf));
    }, settledSrc);

    fs.mkdirSync(path.dirname(rawOutputPath), { recursive: true });
    fs.writeFileSync(rawOutputPath, Buffer.from(videoBytes));
    console.log(`[FlowCdpDriver] Successfully saved raw video (${videoBytes.length} bytes) to ${rawOutputPath}`);
    return rawOutputPath;
  }
}
