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

  // Click a control INSIDE the settings panel by its exact visible label. Flow prefixes
  // labels with an icon ligature word ("videocam Video", "crop_16_9 16:9"), so the
  // pattern allows one leading token. It never matches by substring: the left nav's
  // "View videos" contains "Video" and clicking it closes the panel (seen live).
  async clickExact(label, { required = true } = {}) {
    const page = this.flowPage;
    const esc = label.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const re = new RegExp(`^(?:[a-z_0-9]+\\s+)?${esc}$`, 'i');
    const candidates = [
      page.getByRole('button', { name: re }),
      page.getByRole('tab', { name: re }),
      page.getByRole('radio', { name: re }),
      page.getByRole('option', { name: re }),
      page.getByRole('menuitem', { name: re }),
      page.getByText(re, { exact: true }),
    ];
    for (const loc of candidates) {
      if (await loc.count() > 0) {
        await loc.first().click();
        await page.waitForTimeout(350);
        return true;
      }
    }
    if (required) throw new Error(`Flow settings control not found: "${label}"`);
    return false;
  }

  // The composer pill is the one button whose text ends in the output count ("... x2").
  // It is unique, unlike anything containing "Video".
  settingsPill() {
    // With the panel open the count buttons ("x1".."x4") also end in xN - exclude bare tokens.
    return this.flowPage.locator('button').filter({ hasText: /x[1-4]\s*$/ }).filter({ hasNotText: /^\s*x[1-4]\s*$/ }).last();
  }

  async readGenerationState() {
    const page = this.flowPage;
    const pill = this.settingsPill();
    const pillText = (await pill.count()) ? (await pill.innerText()).replace(/\s+/g, ' ').trim() : '';
    const creditsLoc = page.getByText(/Generating will use/i).first();
    const creditsText = (await creditsLoc.count()) ? (await creditsLoc.innerText()).replace(/\s+/g, ' ').trim() : '';
    const m = creditsText.match(/(\d+)\s*credits?/i);
    const dd = page.locator('button').filter({ hasText: /arrow_drop_down/ }).first();
    const modelText = (await dd.count()) ? (await dd.innerText()).replace(/arrow_drop_down/g, '').replace(/\s+/g, ' ').trim() : '';
    return { pillText, creditsText, modelText, credits: m ? parseInt(m[1], 10) : null };
  }

  async configureSettings({
    mode = 'video', submode = 'ingredients', model = null,
    ratio = null, duration = null, resolution = null, count = 1, maxCredits = null,
  } = {}) {
    const page = this.flowPage;
    if (!page) throw new Error('No active Flow page');

    const pill = this.settingsPill();
    if (await pill.count() === 0) throw new Error('Flow settings pill not found (composer button ending in x1..x4).');
    await pill.click();
    await page.waitForTimeout(700);

    // Mode first - it changes which controls exist below it.
    await this.clickExact(mode === 'image' ? 'Image' : 'Video');
    if (mode !== 'image' && submode) await this.clickExact(submode === 'frames' ? 'Frames' : 'Ingredients', { required: false });
    if (ratio === '9:16' || ratio === '16:9') await this.clickExact(ratio);

    if (model) {
      // The model dropdown is the panel button carrying the dropdown glyph; open it, pick by exact name.
      const dd = page.locator('button').filter({ hasText: /arrow_drop_down/ }).first();
      if (await dd.count() > 0) { await dd.click(); await page.waitForTimeout(500); }
      await this.clickExact(model);
    }
    if (resolution) await this.clickExact(resolution);
    if (duration) await this.clickExact(`${duration}s`);
    if (count) await this.clickExact(`x${count}`);

    // READ BACK: credits line while the panel is open (it lives inside it), pill after it closes.
    const open = await this.readGenerationState();
    await page.keyboard.press('Escape');
    await page.waitForTimeout(500);
    const closed = await this.readGenerationState();
    const state = { pillText: closed.pillText || open.pillText, creditsText: open.creditsText || closed.creditsText,
                    modelText: open.modelText || closed.modelText, credits: open.credits ?? closed.credits };
    const problems = [];
    // The video-mode pill reads "Video · 720p · 6s ..." with no model; the model shows on the dropdown.
    const shown = `${state.modelText} ${state.pillText}`.toLowerCase();
    if (model && !shown.includes(model.toLowerCase())) {
      problems.push(`model "${model}" not selected (dropdown: "${state.modelText}", pill: "${state.pillText}")`);
    }
    if (mode !== 'image' && /banana|imagen/i.test(state.pillText)) {
      problems.push(`pill shows an IMAGE model in video mode (pill: "${state.pillText}")`);
    }
    if (mode !== 'image' && state.credits === 0) {
      problems.push('credits read 0 - that is the Image-mode signature, Flow is not in Video mode');
    }
    if (state.credits === null) {
      problems.push(`could not read the credits line (saw: "${state.creditsText}")`);
    }
    if (maxCredits != null && state.credits != null && state.credits > maxCredits) {
      problems.push(`scene would cost ${state.credits} credits, over its maxCredits ${maxCredits}`);
    }
    if (problems.length) {
      throw new Error(`REFUSED to submit - generation state not as declared:\n  - ${problems.join('\n  - ')}`);
    }

    console.log(`[FlowCdpDriver] settings verified: ${state.modelText} | ${state.pillText} | ${state.creditsText}`);
    return state;
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

  async waitForGenerationAndDownload(rawOutputPath, timeoutMs = 420000) {
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
