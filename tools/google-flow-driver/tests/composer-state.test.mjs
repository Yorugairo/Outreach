import assert from 'node:assert/strict';
import {after, before, test} from 'node:test';
import {chromium} from 'playwright-core';
import {captureComposerState, assertLiveComposerState} from '../src/composer-state.mjs';

let browser;
let page;
before(async () => {
  browser = await chromium.launch({channel: 'chrome', headless: true});
  const context = await browser.newContext({offline: true});
  page = await context.newPage();
});
after(async () => { await browser?.close(); });

const style = '<style>flow-prompt-box,.ProseMirror{display:block;width:600px;min-height:80px}.chip-container{width:50px;height:50px}</style>';
const media = '<button class="chip-container"><img alt="Ingredient image" src="https://flow-content.google/image/d9daed6d-e54f-4fec-b060-dcd41e308a3e?Signature=do-not-record"></button>';
const character = '<button class="chip-container"><img alt="Character ingredient image" src="https://lh3.googleusercontent.com/asb/character-sheet?secret=omit"><mat-icon class="type-badge">accessibility_new</mat-icon></button>';
const mentions = '<span class="mention-chip" data-reference-type="entity" data-entity-id="mike-id" data-mention-id="mike-id">Mike2</span><span class="mention-chip" data-reference-type="media" data-mention-id="d9daed6d-e54f-4fec-b060-dcd41e308a3e">hero-fab-constraint-v1.png</span>';
async function snapshot(body) {
  await page.setContent(style + body);
  return captureComposerState(page);
}

test('zero state ignores gallery images and Start generation control', async () => {
  const state = await snapshot('<img src="https://example.org/gallery"><flow-prompt-box><div class="ProseMirror" contenteditable="true"></div><button type="submit" aria-label="Start generation">Start generation</button></flow-prompt-box>');
  assert.equal(state.composerRoot.count, 1);
  assert.equal(state.composerRoot.visible, true);
  assert.equal(state.editor.visible, true);
  assert.equal(state.editor.text, '');
  assert.deepEqual(state.contextChips, []);
  assert.deepEqual(state.tray.trayChips, []);
});

test('captures inline and tray separately, strips signed URLs, never guesses character mapping', async () => {
  const state = await snapshot(`<flow-prompt-box>${character}${media}<div class="ProseMirror">${mentions}</div></flow-prompt-box>`);
  assert.equal(state.editor.inlineChipsCount, 2);
  assert.equal(state.tray.trayElementsCount, 2);
  assert.equal(state.tray.trayChips[1].providerId, 'd9daed6d-e54f-4fec-b060-dcd41e308a3e');
  assert.equal(state.tray.trayChips[0].providerId, null);
  assert.deepEqual(state.entityTrayBindings, []);
  assert.ok(!JSON.stringify(state).includes('Signature'));
  assert.ok(!JSON.stringify(state).includes('secret'));
});

test('stale third tray image cannot hide behind two inline chips', async () => {
  const state = await snapshot(`<flow-prompt-box>${character}${media}${media}<div class="ProseMirror">${mentions}</div></flow-prompt-box>`);
  assert.equal(state.editor.inlineChipsCount, 2);
  assert.equal(state.tray.trayElementsCount, 3);
});

test('multiple or hidden roots do not resolve to first editor', async () => {
  const state = await snapshot('<flow-prompt-box><div class="ProseMirror"></div></flow-prompt-box><flow-prompt-box><div class="ProseMirror"></div></flow-prompt-box>');
  assert.equal(state.composerRoot.count, 2);
  assert.equal(state.editor.count, 0);
  const hidden = await snapshot('<flow-prompt-box style="display:none"><div class="ProseMirror"></div></flow-prompt-box>');
  assert.equal(hidden.composerRoot.visible, false);
});

test('unknown composer images, edit context and open picker remain explicit', async () => {
  const state = await snapshot('<flow-prompt-box><div class="ProseMirror"></div><img src="https://example.org/stale"><div class="edit-context">Edit source</div></flow-prompt-box><div role="listbox">Picker selection</div>');
  assert.equal(state.contextChips.length, 2);
  assert.equal(state.contextChips[1].unknown, true);
  assert.equal(state.pendingOverlaysCount, 1);
});

test('live wrapper refuses extra reference and missing character identity evidence', async () => {
  const refs = [
    {type: 'entity', id: 'mike-id', name: 'Mike2'},
    {type: 'media', id: 'd9daed6d-e54f-4fec-b060-dcd41e308a3e', name: 'hero-fab-constraint-v1.png'},
  ];
  const bindings = [{entityId: 'mike-id', thumbnailKey: 'https://lh3.googleusercontent.com/asb/character-sheet'}];
  await snapshot(`<flow-prompt-box>${character}${media}<div class="ProseMirror">${mentions}</div></flow-prompt-box>`);
  await assert.rejects(() => assertLiveComposerState(page, refs), /Composer guard failed/);
  await assertLiveComposerState(page, refs, bindings);
  await snapshot(`<flow-prompt-box>${character}${media}${media}<div class="ProseMirror">${mentions}</div></flow-prompt-box>`);
  await assert.rejects(() => assertLiveComposerState(page, refs, bindings), /Composer guard failed/);
});
