import fs from 'node:fs';
import crypto from 'node:crypto';
import path from 'node:path';
import { chromium } from 'playwright-core';

// Flow moved hosts on 2026-09-04 (labs.google/fx/tools/flow -> flow.google.com). Match either,
// and match a target by its project id so a redirect never looks like a different page.
export const FLOW_HOSTS = ['labs.google/fx/tools/flow', 'flow.google.com'];
export const isFlowUrl = (url) => FLOW_HOSTS.some((h) => String(url || '').includes(h));
export const flowProjectId = (url) => (String(url || '').match(/\/project\/([0-9a-f-]{36})/i) || [])[1] || null;
export const sameFlowTarget = (url, target) => {
  if (!target) return false;
  if (String(url).includes(target)) return true;
  const a = flowProjectId(url); const b = flowProjectId(target);
  return Boolean(a && b && a === b);
};

export class FlowCdpDriver {
  constructor(options = {}) {
    this.port = options.port || 9223;
    this.browser = null;
    this.flowPage = null;
    this.idleTimer = null;
    this.idleTimeoutMs = options.idleTimeoutMs || 60000;
  }

  resetIdleTimer() {
    if (this.idleTimer) clearTimeout(this.idleTimer);
    this.idleTimer = setTimeout(() => {
      console.log('[FlowCdpDriver] Idle timeout (60s) reached - auto-closing CDP connection.');
      this.disconnect().catch(() => {});
    }, this.idleTimeoutMs);
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
    
    // Scan existing open tabs - prefer an open project page
    for (const ctx of this.browser.contexts()) {
      for (const page of ctx.pages()) {
        const url = page.url();
        if (targetUrl && sameFlowTarget(url, targetUrl)) {
          this.flowPage = page;
          await page.bringToFront().catch(() => {});
          return this.flowPage;
        }
        if (!targetUrl && isFlowUrl(url) && flowProjectId(url)) {
          this.flowPage = page;
          await page.bringToFront().catch(() => {});
          return this.flowPage;
        }
      }
    }

    for (const ctx of this.browser.contexts()) {
      for (const page of ctx.pages()) {
        const url = page.url();
        if (isFlowUrl(url)) {
          this.flowPage = page;
          if (targetUrl && !sameFlowTarget(url, targetUrl)) {
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
    const dest = targetUrl || 'https://flow.google.com';
    await page.goto(dest, { waitUntil: 'domcontentloaded' });
    this.flowPage = page;
    await page.bringToFront().catch(() => {});
    this.resetIdleTimer();
    return this.flowPage;
  }

  async getProjectDetails() {
    const page = await this.getFlowPage();
    this.resetIdleTimer();

    const title = await page.title();
    const url = page.url();
    const genState = await this.readGenerationState();
    const characters = await this.listProjectCharacters();
    const media = await this.listProjectMedia();

    return {
      title,
      url,
      ratio: genState.pillText.includes('crop_9_16') ? '9:16' : (genState.pillText.includes('crop_16_9') ? '16:9' : 'default'),
      model: genState.modelText || genState.pillText,
      characters,
      mediaCount: media.length,
      media: media.slice(0, 10)
    };
  }

  async listProjectCharacters() {
    const page = await this.getFlowPage();
    this.resetIdleTimer();

    // 1. Scan DOM for character image alt tags and cards
    const names = await page.evaluate(() => {
      const set = new Set();
      document.querySelectorAll('img[alt]').forEach(img => {
        const alt = img.getAttribute('alt')?.trim();
        const systemLabels = ['Generated image', 'Character preview image', 'Google Flow', 'User profile image', 'Video thumbnail', 'Character reference image'];
        if (alt && !systemLabels.includes(alt) && !alt.startsWith('http')) {
          set.add(alt);
        }
      });
      // Also look for character text nodes on canvas cards
      document.querySelectorAll('span, p').forEach(el => {
        const txt = el.innerText?.trim();
        if (txt && txt.length > 1 && txt.length < 25 && !txt.includes('\n')) {
          if (el.className?.includes('gwpfqt') || el.closest('[class*="character"]')) {
            set.add(txt);
          }
        }
      });
      return Array.from(set);
    });

    if (names.length > 0) return names;

    // 2. Query @-mention dialog Characters tab if not visible on canvas
    try {
      const editor = page.locator("div[data-slate-editor='true'], div[contenteditable='true']").first();
      if (await editor.count() > 0) {
        await editor.click();
        await page.keyboard.type('@');
        await page.waitForTimeout(500);

        const dialog = page.locator('div[role="dialog"]');
        const charBtn = dialog.locator('button').filter({ hasText: /Characters/i }).first();
        if (await charBtn.count() > 0) {
          await charBtn.click();
          await page.waitForTimeout(500);

          const dialogNames = await dialog.evaluate(el => {
            const found = [];
            el.querySelectorAll('img[alt]').forEach(img => {
              const alt = img.getAttribute('alt')?.trim();
              if (alt && alt !== 'Character preview image') found.push(alt);
            });
            return found;
          });
          await page.keyboard.press('Escape');
          return dialogNames;
        }
        await page.keyboard.press('Escape');
      }
    } catch {}

    return names;
  }

  async listProjectMedia() {
    const page = await this.getFlowPage();
    this.resetIdleTimer();

    return await page.evaluate(() => {
      const media = [];
      document.querySelectorAll('img').forEach(img => {
        const src = img.src;
        if (src && (src.includes('getMediaUrlRedirect') || src.includes('googleusercontent'))) {
          media.push({
            alt: img.getAttribute('alt') || '',
            src,
            width: img.naturalWidth || 0,
            height: img.naturalHeight || 0,
            type: 'image'
          });
        }
      });
      return media;
    });
  }

  // Click a control INSIDE the settings panel by its exact visible label. Flow prefixes
  // labels with an icon ligature word ("videocam Video", "crop_16_9 16:9"), so the
  // pattern allows one leading token. It never matches by substring: the left nav's
  // "View videos" contains "Video" and clicking it closes the panel (seen live).
  /** The drawer's mode toggle: two radios named "image Image" / "videocam Video" (an icon word leads
   *  the label). Click the one for `mode` and VERIFY aria-checked - an unverified optional click left
   *  image mode selected and the video model family absent (2026-09-05). */
  async selectMode(mode) {
    const page = this.flowPage;
    const want = mode === 'image' ? /Image/ : /Video/;   // case-sensitive: the icon word is 'videocam', the label 'Video'
    // The radios' labels are readable through innerText but NOT through Playwright's hasText filter
    // (2026-09-05, redesigned drawer) - so walk the visible radios and read each one.
    const find = async () => {
      const radios = page.locator('[role="radio"]').filter({ visible: true });
      const n = await radios.count();
      for (let i = 0; i < n; i++) {
        const txt = (await radios.nth(i).innerText().catch(() => '')).replace(/\s+/g, ' ').trim();
        if (want.test(txt)) return radios.nth(i);
      }
      return null;
    };
    // the drawer animates open after the pill click: poll before concluding it is closed
    let radio = null;
    for (let i = 0; i < 8 && !radio; i++) { radio = await find(); if (!radio) await page.waitForTimeout(400); }
    if (!radio) {
      // the drawer is not open: open it from the settings pill and look again
      const pill = this.settingsPill();
      if (await pill.count() > 0) { await pill.first().click({ timeout: 8000 }); }
      for (let i = 0; i < 8 && !radio; i++) { await page.waitForTimeout(400); radio = await find(); }
    }
    if (!radio) {
      const seen = await page.locator('[role="radio"]').filter({ visible: true }).allInnerTexts().catch(() => []);
      const pills = await page.locator('button').filter({ visible: true }).allInnerTexts().catch(() => []);
      throw new Error(`Flow mode toggle for "${mode}" not found in the settings drawer (visible radios: ${JSON.stringify(seen.map(s => s.replace(/\s+/g, ' ').trim()))}; visible buttons with x1-4/crop: ${JSON.stringify(pills.map(s => s.replace(/\s+/g, ' ').trim()).filter(s => /x[1-4]|crop_/.test(s)))})`);
    }
    if ((await radio.getAttribute('aria-checked')) !== 'true') {
      await radio.click({ timeout: 8000 });
      await page.waitForTimeout(700);
    }
    const checked = await radio.getAttribute('aria-checked');
    if (checked !== 'true') throw new Error(`Flow mode "${mode}" did not take (aria-checked=${checked})`);
    console.log(`[FlowCdpDriver] mode: ${mode} (verified)`);
  }

  async clickExact(label, { required = true } = {}) {
    const page = this.flowPage;
    const esc = label.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const re = new RegExp(`^(?:[^a-z0-9]*[a-z_0-9]+\\s+|[^a-z0-9]+\\s*)?${esc}$`, 'i');
    const candidates = [
      page.getByRole('button', { name: re }),
      page.getByRole('tab', { name: re }),
      page.getByRole('radio', { name: re }),
      page.getByRole('option', { name: re }),
      page.getByRole('menuitem', { name: re }),
      page.getByText(re, { exact: true }),
      page.locator('button, [role="option"], div[role="button"]').filter({ hasText: new RegExp(esc, 'i') }),
    ];
    // Prefer a VISIBLE match: the drawer keeps hidden controls in the DOM (the old Image/Video toggle
    // is a mat-icon with the text and no box), and the first hidden match used to eat the whole
    // 30 s click timeout. An optional control gets a short timeout and never throws.
    for (const loc of candidates) {
      const vis = loc.filter({ visible: true });
      const n = await vis.count().catch(() => 0);
      if (n > 0) {
        try {
          await vis.first().click({ timeout: required ? 30000 : 4000 });
          await page.waitForTimeout(350);
          return true;
        } catch (e) {
          if (required) throw e;
        }
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

    // Ensure any open preview or lightbox is dismissed so the composer is active
    let initial = await this.readGenerationState();
    if (!initial.pillText) {
      await page.keyboard.press('Escape');
      await page.waitForTimeout(400);
      initial = await this.readGenerationState();
    }

    const currentText = `${initial.modelText} ${initial.pillText}`.toLowerCase();
    const isImage = mode === 'image';
    const matchesModel = !model || currentText.includes(model.toLowerCase()) || (isImage && /banana|imagen/i.test(currentText));
    const matchesRatio = !ratio || currentText.includes(ratio.replace(':', '_')) || currentText.includes(ratio);
    const matchesMode = isImage ? /banana|imagen/i.test(currentText) : !/banana|imagen/i.test(currentText);
    // a plain string, not a template literal: inside a template literal '\b' is a BACKSPACE, so 'x4' never
    // matched, and every second still re-clicked a hidden 'Image' tab until it timed out (2026-09-04)
    const matchesCount = !count || new RegExp('x' + count + '\\b').test(currentText);

    if (matchesMode && matchesModel && matchesRatio && matchesCount) {
      console.log(`[FlowCdpDriver] Settings already match active session: "${currentText}". Preserving current drawer.`);
      return initial;
    }

    let pill = this.settingsPill();
    if (await pill.count() === 0) {
      await page.keyboard.press('Escape');
      await page.waitForTimeout(500);
      pill = this.settingsPill();
    }
    if (await pill.count() === 0) throw new Error('Flow settings pill not found (composer button ending in x1..x4).');
    await pill.click();
    await page.waitForTimeout(700);

    // Mode first - it changes which controls exist below it. On the redesigned drawer (2026-09-04) there is
    // no Image/Video toggle at all: the mode follows the model family picked from the 'Select model family'
    // dropdown (Nano Banana Pro = image, Omni / Veo = video), so the toggle click is optional and the
    // credits/pill checks below are what prove the mode.
    await this.selectMode(mode);
    if (mode !== 'image' && submode) await this.clickExact(submode === 'frames' ? 'Frames' : 'Ingredients', { required: false });
    if (ratio === '9:16' || ratio === '16:9') {
      const iconName = ratio === '9:16' ? 'crop_9_16' : 'crop_16_9';
      const clicked = await this.clickExact(ratio, { required: false });
      if (!clicked) {
        const ratioLoc = page.locator(`button[aria-label*="${ratio}"], button:has-text("${iconName}"), button:has-text("${ratio}")`).first();
        if (await ratioLoc.count() > 0) {
          await ratioLoc.click();
          await page.waitForTimeout(350);
        }
      }
    }

    if (model) {
      // The model dropdown is the panel button carrying the dropdown glyph; open it, pick by exact name.
      const dd = page.locator('button').filter({ hasText: /arrow_drop_down/ }).first();
      if (await dd.count() > 0) { await dd.click(); await page.waitForTimeout(500); }
      await this.clickExact(model);
    }
    if (resolution) await this.clickExact(resolution, { required: false });
    if (duration) await this.clickExact(`${duration}s`, { required: false });
    if (count) await this.clickExact(`x${count}`, { required: false });

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
    if (mode !== 'image' && state.credits === null) {
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

    const uploadList = validPaths.slice(0, 3);
    const fileInput = page.locator("input[type='file']").first();
    if (await fileInput.count() > 0) {
      // Legacy Flow: a bare file input beside the composer.
      await fileInput.setInputFiles(uploadList);
      await page.waitForTimeout(1500);
      return;
    }

    // New Flow (flow.google.com, 2026-09): uploads go through the '@' asset picker - "Upload media"
    // opens a native chooser, the file is selected in the picker, and "Add to prompt" drops a
    // media mention-chip into the composer. Call AFTER setPrompt, which clears the composer.
    for (const filePath of uploadList) {
      const editor = page.locator("div[data-slate-editor='true'], div[contenteditable='true']").first();
      await editor.click();
      await page.keyboard.press('End');
      await page.keyboard.type(' @');
      await page.waitForTimeout(900);
      // Reuse a previous upload: the picker lists project assets by filename and a media option
      // inserts on click. Only upload when the name is not there (operator, 2026-09-04).
      const baseName = path.basename(filePath);
      await page.keyboard.type(baseName);
      await page.waitForTimeout(900);
      const existing = page.locator(`[role="option"]:has(.asset-title:text-is("${baseName}"))`).first();
      if (await existing.count() > 0) {
        await existing.click();
        await page.waitForTimeout(900);
        const reused = page.locator("div[contenteditable='true'] .mention-chip[data-reference-type='media']");
        if (await reused.count() === 0) throw new Error(`Existing asset ${baseName} was clicked but no media chip landed.`);
        console.log(`[FlowCdpDriver] Reference reused from project assets: ${baseName}`);
        await page.keyboard.press('End');
        continue;
      }
      for (let i = 0; i < baseName.length; i++) await page.keyboard.press('Backspace');
      await page.waitForTimeout(400);
      const uploadBtn = page.getByText(/Upload media/i).first();
      if (await uploadBtn.count() === 0) throw new Error('Asset picker did not offer "Upload media".');
      const [chooser] = await Promise.all([page.waitForEvent('filechooser', { timeout: 10000 }), uploadBtn.click()]);
      await chooser.setFiles(filePath);
      await page.waitForTimeout(4000);
      const addBtn = page.getByRole('button', { name: /Add to prompt/i }).first();
      if (await addBtn.count() === 0) throw new Error(`Upload of ${path.basename(filePath)} did not reach "Add to prompt".`);
      await addBtn.click();
      await page.waitForTimeout(900);
      const chip = page.locator("div[contenteditable='true'] .mention-chip[data-reference-type='media']");
      if (await chip.count() === 0) throw new Error(`Upload of ${path.basename(filePath)} left no media chip in the composer.`);
      console.log(`[FlowCdpDriver] Reference attached as a media chip: ${path.basename(filePath)}`);
      await page.keyboard.press('End');
    }
  }

  async setPrompt(promptText, { characters = [] } = {}) {
    const page = this.flowPage;
    if (!page) throw new Error('No active Flow page');
    this.resetIdleTimer();

    const editor = page.locator("div[data-slate-editor='true'], div[contenteditable='true']").first();
    if (await editor.count() === 0) {
      throw new Error("Could not find prompt editor in Flow page.");
    }

    await editor.click();
    await page.keyboard.press('Control+A');
    await page.keyboard.press('Backspace');
    await page.waitForTimeout(200);

    // If character names are provided, insert them via the @ mention popover
    if (characters && characters.length > 0) {
      // A literal '@' in the prompt TEXT re-opens the picker while the text is being typed and
      // the character never binds - Tokyo 2026-09-04: 5 of 6 clips drew a stranger, one printed
      // "@StickMike" on the page. The chip is the only way a character enters a prompt.
      if (/@/.test(promptText)) {
        throw new Error(`Prompt text contains '@' (${promptText.match(/@\S*/)[0]}); name the character in \`references\` and write "he"/"the character" in the text - the chip binds, typed text does not.`);
      }
      for (const charName of characters) {
        console.log(`[FlowCdpDriver] Attaching native character chip: "${charName}"`);
        await page.keyboard.type('@');
        await page.waitForTimeout(600);

        // New Flow (flow.google.com, 2026-09): '@' opens an asset picker listbox whose search field
        // takes focus - type the name to filter, then click the option that is a Character.
        const listbox = page.locator('[role="listbox"]');
        const dialog = page.locator('div[role="dialog"]');
        if (await listbox.count() > 0) {
          await page.keyboard.type(charName);
          await page.waitForTimeout(800);
          // Media inserts on click; a Character is SELECTED on click (preview pane) and inserted by
          // the picker's "Add to prompt" button. Observed 2026-09-04 on the redesigned picker.
          const option = page.locator(`[role="option"]:has(.asset-title:text-is("${charName}"))`).first();
          if (await option.count() > 0) {
            await option.click();
            await page.waitForTimeout(700);
            const addBtn = page.getByRole('button', { name: /Add to prompt/i }).first();
            if (await addBtn.count() > 0) {
              await addBtn.click();
              await page.waitForTimeout(700);
            }
            // the chip must be THIS character's - a stale chip from a previous prompt, or a media
            // chip, satisfied a bare count check and let five clips go out unbound (2026-09-04)
            const chips = page.locator("div[contenteditable='true'] .mention-chip");
            const texts = await chips.allInnerTexts();
            const mine = texts.filter((x) => x.replace(/^@/, '').trim().toLowerCase() === charName.toLowerCase());
            if (mine.length > 0) {
              console.log(`[FlowCdpDriver] Character chip attached: "${charName}" (${texts.join(' | ')})`);
            } else {
              throw new Error(`Character "${charName}" was selected but no mention-chip named "${charName}" landed in the composer (chips: ${JSON.stringify(texts)}).`);
            }
          } else {
            console.warn(`[FlowCdpDriver] No option for "${charName}" in the asset picker; closing.`);
            await page.keyboard.press('Escape');
          }
          // the chip insert leaves focus in the composer; just move the caret to the end
          await page.keyboard.press('End');
        } else if (await dialog.count() > 0) {
          const charBtn = dialog.locator('button').filter({ hasText: /Characters/i }).first();
          if (await charBtn.count() > 0) {
            await charBtn.click();
            await page.waitForTimeout(600);
          }

          // Look for image with alt or card with text matching character name
          const target = dialog.locator(`img[alt="${charName}"], [role="button"]:has-text("${charName}"), button:has-text("${charName}")`).first();
          if (await target.count() > 0) {
            await target.click();
            await page.waitForTimeout(500);
          } else {
            console.warn(`[FlowCdpDriver] Character card for "${charName}" not found in @ dialog; closing.`);
            await page.keyboard.press('Escape');
          }
        }
      }
    }

    // Strip leading @CharacterName from promptText if we already attached it as a chip
    let body = promptText;
    for (const charName of characters) {
      const re = new RegExp(`^\\s*@?${charName}\\s*,?\\s*`, 'i');
      body = body.replace(re, '');
    }

    if (body.trim().length > 0) {
      const prefix = characters && characters.length > 0 ? ' ' : '';
      await page.keyboard.insertText(prefix + body.trim());
      await page.waitForTimeout(500);
      // E29: verify what LANDED. Scenes after the first in a batch were generating the previous
      // scene's picture (Tokyo stills, 2026-09-04) - the composer text is read back and must carry
      // this prompt's opening words and nothing like twice its length (a leftover prompt).
      const landed = (await editor.innerText().catch(() => '')).replace(/\s+/g, ' ').trim();
      const head = body.trim().slice(0, 40).replace(/\s+/g, ' ');
      if (!landed.includes(head)) {
        throw new Error(`Prompt did not land in the composer (expected "${head}...", composer reads "${landed.slice(0, 80)}").`);
      }
      if (landed.length > body.trim().length * 1.6 + 40) {
        throw new Error(`Composer carries more than this prompt (${landed.length} chars for a ${body.trim().length}-char prompt) - a previous prompt was not cleared: "${landed.slice(0, 80)}"`);
      }
      console.log(`[FlowCdpDriver] Prompt verified in the composer (${landed.length} chars).`);
    }
  }

  async triggerGeneration() {
    const page = this.flowPage;
    if (!page) throw new Error('No active Flow page');
    // The baseline for "what is new" is taken HERE, before the submit click. Taken after it, a fast
    // render was already listed and the next scene claimed it - three Tokyo stills came back shifted
    // by one scene (2026-09-04).
    this.preSubmit = await page.evaluate(() => ({
      images: Array.from(document.querySelectorAll("img[src*='getMediaUrlRedirect'], img[src*='flow-content.google/'], img[src*='/asb/']")).map(i => i.src),
      videos: Array.from(document.querySelectorAll('video')).map(v => v.src || v.getAttribute('src'))
        .filter(s => Boolean(s) && /getMediaUrlRedirect|flow-content\.google\/|\/asb\//.test(s)),
    }));

    let submitBtn = page.locator("button:has-text('arrow_forward'), button:has-text('Create'), button[aria-label*='Submit'], button[aria-label*='Generate']").last();
    if (await submitBtn.count() > 0 && await submitBtn.isVisible()) {
      await submitBtn.click();
    } else {
      // Fallback: press Enter inside the composer
      const editor = page.locator("div[contenteditable='true']").first();
      if (await editor.count() > 0) {
        await editor.focus();
        await editor.press('Enter');
      } else {
        throw new Error("Could not find submit button or composer editor on Flow page.");
      }
    }
    await page.waitForTimeout(2000);
  }

  async waitForGenerationAndDownload(rawOutputPath, timeoutMs = 420000, mode = 'video', { excludeFiles = [], count = 1 } = {}) {
    const page = this.flowPage;
    if (!page) throw new Error('No active Flow page');
    // An uploaded reference re-renders on the canvas as a brand-new CDN URL, which looks exactly
    // like a finished generation. Any candidate whose bytes equal a reference file is skipped.
    // Flow re-encodes uploads, so bytes differ; a 16x16 average-hash computed in the page catches
    // the re-render regardless of container format. Hamming distance <= 12 of 256 bits = same picture.
    const aHashInPage = async (src) => page.evaluate(async (u) => {
      const blob = await (await fetch(u)).blob();
      const bmp = await createImageBitmap(blob);
      const c = document.createElement('canvas'); c.width = 16; c.height = 16;
      const g = c.getContext('2d'); g.drawImage(bmp, 0, 0, 16, 16);
      const d = g.getImageData(0, 0, 16, 16).data; const v = [];
      for (let i = 0; i < d.length; i += 4) v.push(0.299 * d[i] + 0.587 * d[i + 1] + 0.114 * d[i + 2]);
      const mean = v.reduce((a, b) => a + b, 0) / v.length;
      return { bits: v.map(x => (x > mean ? '1' : '0')).join(''), w: bmp.width, h: bmp.height };
    }, src);
    const hamming = (a, b) => { let n = 0; for (let i = 0; i < a.length; i++) if (a[i] !== b[i]) n++; return n; };
    const excludeSigs = [];
    for (const f of excludeFiles.filter(f => fs.existsSync(f))) {
      const b64 = fs.readFileSync(f).toString('base64');
      const ext = path.extname(f).slice(1).toLowerCase().replace('jpg', 'jpeg');
      excludeSigs.push(await aHashInPage(`data:image/${ext};base64,${b64}`));
    }
    const looksLikeReference = async (src) => {
      if (excludeSigs.length === 0) return false;
      const sig = await aHashInPage(src);
      return excludeSigs.some(r => hamming(r.bits, sig.bits) <= 12);
    };

    const isImage = mode === 'image';
    const startTime = Date.now();

    if (isImage) {
      console.log(`[FlowCdpDriver] Waiting for image generation to complete (timeout: ${timeoutMs}ms)...`);
      const prevList = (this.preSubmit && this.preSubmit.images) || await page.evaluate(() => {
        return Array.from(document.querySelectorAll("img[src*='getMediaUrlRedirect'], img[src*='flow-content.google/'], img[src*='/asb/']")).map(i => i.src);
      });
      this.preSubmit = null;

      const collected = [];
      let lastFoundAt = Date.now();
      // an image downloaded earlier in this session is never "new" again (same defect as the video
      // path: the page lists an earlier output after the baseline is taken; its signed URL may also
      // have expired, which is the "Failed to fetch" that killed the stills batch, 2026-09-04)
      this.seenImageIds = this.seenImageIds || new Set();
      const idOf = (s) => s.split('?')[0];
      while (Date.now() - startTime < timeoutMs) {
        this.resetIdleTimer();
        const currentSrc = await page.evaluate(({ prevs, seen, count }) => {
          const idOf = (s) => s.split('?')[0];
          // Flow lists renders NEWEST FIRST. Only the top `count` tiles can be this generation's output;
          // an unseen image further down is an older render the lazy grid loaded late, and claiming it
          // shifted three stills by one scene (2026-09-04). Positional, not "first unseen anywhere".
          const imgs = Array.from(document.querySelectorAll("img[src*='getMediaUrlRedirect'], img[src*='flow-content.google/'], img[src*='/asb/']")).map(i => i.src);
          for (let i = 0; i < Math.min(count, imgs.length); i++) {
            const s = imgs[i];
            if (!prevs.includes(s) && !seen.includes(idOf(s))) return s;
          }
          return null;
        }, { prevs: prevList, seen: Array.from(this.seenImageIds), count });

        if (currentSrc) {
          let bytes = null;
          try {
            bytes = await page.evaluate(async (src) => {
              const resp = await fetch(src);
              if (!resp.ok) throw new Error('HTTP ' + resp.status);
              const buf = await (await resp.blob()).arrayBuffer();
              return Array.from(new Uint8Array(buf));
            }, currentSrc);
          } catch (e) {
            console.warn(`[FlowCdpDriver] Could not fetch ${currentSrc.slice(0, 80)} (${e.message}); skipping it.`);
            this.seenImageIds.add(idOf(currentSrc));
            prevList.push(currentSrc);
            await page.waitForTimeout(2500);
            continue;
          }
          prevList.push(currentSrc);
          this.seenImageIds.add(idOf(currentSrc));
          // Flow's asset-service '/asb/' entries are PREVIEW thumbnails (286x512, ~20 KB); the render is the
          // flow-content.google/image URL. Three Tokyo stills came back as thumbnails (2026-09-04).
          if (bytes.length < 120000 && /\/asb\//.test(currentSrc)) {
            console.log(`[FlowCdpDriver] Ignoring preview thumbnail (${bytes.length} bytes): ${currentSrc.slice(0, 80)}`);
            await page.waitForTimeout(2500);
            continue;
          }
          if (collected.some(c => c.src === currentSrc)) {
            // the 'first tile shifted' branch can hand back a src already taken
          } else if (await looksLikeReference(currentSrc)) {
            console.log(`[FlowCdpDriver] Ignoring re-rendered reference upload: ${currentSrc.slice(0, 80)}`);
          } else {
            collected.push({ src: currentSrc, bytes });
            lastFoundAt = Date.now();
            console.log(`[FlowCdpDriver] Output ${collected.length}/${count} landed: ${currentSrc.slice(0, 80)}`);
            if (collected.length >= count) break;
          }
        } else if (collected.length > 0 && Date.now() - lastFoundAt > 45000) {
          console.warn(`[FlowCdpDriver] Only ${collected.length}/${count} outputs after 45s of quiet; taking what landed.`);
          break;
        }
        await page.waitForTimeout(2500);
      }

      if (collected.length === 0) {
        throw new Error(`Image generation timed out after ${timeoutMs}ms.`);
      }

      // first output at the requested path, the rest as -2, -3, ... beside it (x2..x4 rolls)
      fs.mkdirSync(path.dirname(rawOutputPath), { recursive: true });
      const saved = [];
      collected.forEach(({ bytes }, i) => {
        const target = i === 0 ? rawOutputPath : rawOutputPath.replace(/(\.[a-z0-9]+)$/i, `-${i + 1}$1`);
        fs.writeFileSync(target, Buffer.from(bytes));
        console.log(`[FlowCdpDriver] Saved raw image ${i + 1}/${collected.length} (${bytes.length} bytes) to ${target}`);
        saved.push(target);
      });
      this.lastSavedOutputs = saved;
      return rawOutputPath;
    }

    // Video mode: snapshot all existing video URLs to diff reliably
    const prevVideoList = (this.preSubmit && this.preSubmit.videos) || await page.evaluate(() => {
      return Array.from(document.querySelectorAll('video'))
        .map(v => v.src || v.getAttribute('src'))
        .filter(s => Boolean(s) && /getMediaUrlRedirect|flow-content\.google\/|\/asb\//.test(s));
    });
    this.preSubmit = null;

    console.log(`[FlowCdpDriver] Waiting for video generation to complete (timeout: ${timeoutMs}ms, baseline videos: ${prevVideoList.length})...`);

    let settledSrc = null;
    while (Date.now() - startTime < timeoutMs) {
      this.resetIdleTimer();

      // a video downloaded EARLIER in this session is never "new" again - the page lists the previous
      // scene's output after the baseline was taken and scene 2 got scene 1's file (Tokyo, 2026-09-04).
      // Compared by media id (the path before '?'): the signed query differs on every listing.
      this.seenVideoIds = this.seenVideoIds || new Set();
      const seen = Array.from(this.seenVideoIds);
      const currentSrc = await page.evaluate(({ prevs, seen }) => {
        const idOf = (s) => s.split('?')[0];
        const vids = Array.from(document.querySelectorAll('video'))
          .map(v => v.src || v.getAttribute('src'))
          .filter(s => Boolean(s) && /getMediaUrlRedirect|flow-content\.google\/|\/asb\//.test(s));
        for (const s of vids) {
          if (!prevs.includes(s) && !seen.includes(idOf(s))) return s;
        }
        return null;
      }, { prevs: prevVideoList, seen });

      if (currentSrc) {
        settledSrc = currentSrc;
        break;
      }
      await page.waitForTimeout(3000);
    }

    if (!settledSrc) {
      throw new Error(`Video generation timed out after ${timeoutMs}ms.`);
    }

    this.seenVideoIds.add(settledSrc.split('?')[0]);
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

  async disconnect() {
    if (this.browser) {
      await this.browser.close().catch(() => {});
      this.browser = null;
      this.flowPage = null;
    }
  }
}

