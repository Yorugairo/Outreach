import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';

import { validateComposerState } from '../src/composer-guard.mjs';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../..');
const DIAGNOSTIC_FIXTURE = path.join(ROOT, 'docs/research/runs/fed-flow-composer-recovery/pre-reset-composer-fixture.json');
const CHARACTER_ID = 'dab5d902-9559-44bb-9fea-4823c52de93f';
const MEDIA_ID = 'd9daed6d-e54f-4fec-b060-dcd41e308a3e';
const EXPECTED = [
  { type: 'entity', id: CHARACTER_ID, name: 'Mike2' },
  { type: 'media', id: MEDIA_ID, name: 'hero-fab-constraint-v1.png' },
];

function fixture() {
  const snapshot = JSON.parse(fs.readFileSync(DIAGNOSTIC_FIXTURE, 'utf8'));
  snapshot.composerRoot = { ...snapshot.composerRoot, count: 1, visible: true };
  snapshot.editor = { ...snapshot.editor, count: 1, visible: true };
  snapshot.entityTrayBindings = [{ entityId: CHARACTER_ID, thumbnailKey: 'mike2-thumb-1' }];
  snapshot.pendingOverlaysCount = snapshot.pendingOverlays.length;
  snapshot.tray = {
    ...snapshot.tray,
    trayChips: snapshot.tray.trayChips.map((chip) => (
      chip.isCharacter ? { ...chip, thumbnailKey: 'mike2-thumb-1', visible: true } : { ...chip, visible: true }
    )),
  };
  return snapshot;
}

function zeroSnapshot() {
  const snapshot = fixture();
  snapshot.editor = { ...snapshot.editor, text: '', inlineChipsCount: 0, inlineChips: [] };
  snapshot.entityTrayBindings = [];
  snapshot.tray = { trayElementsCount: 0, trayChips: [] };
  return snapshot;
}

test('zero/reset is valid only with one visible root and no references or pending context', () => {
  const result = validateComposerState(zeroSnapshot(), [], { mode: 'zero' });
  assert.equal(result.ok, true, result.errors.join('\n'));
});

test('zero/reset rejects non-empty observed editor text', () => {
  const snapshot = zeroSnapshot();
  snapshot.editor.text = 'stale prompt';
  const result = validateComposerState(snapshot, [], { mode: 'zero' });
  assert.equal(result.ok, false);
  assert.ok(result.errors.some((error) => /zero\/reset.*text/i.test(error)));
});

test('prepared mode rejects an empty observed editor', () => {
  const snapshot = fixture();
  snapshot.editor.text = '';
  const result = validateComposerState(snapshot, EXPECTED);
  assert.equal(result.ok, false);
  assert.ok(result.errors.some((error) => /prepared.*text/i.test(error)));
});

test('prepared composer accepts the intended references with identity evidence', () => {
  const result = validateComposerState(fixture(), EXPECTED);
  assert.equal(result.ok, true, result.errors.join('\n'));
});

test('two inline references with three tray items fail closed', () => {
  const snapshot = fixture();
  snapshot.tray.trayChips = [...snapshot.tray.trayChips, {
    tagName: 'button', className: 'chip-container', ariaLabel: 'Ingredient',
    isCharacter: false, providerId: 'unexpected-media', hasRemoveControl: true,
  }];
  snapshot.tray.trayElementsCount = 3;
  const result = validateComposerState(snapshot, EXPECTED);
  assert.equal(result.ok, false);
  assert.ok(result.errors.some((error) => /tray.*count|unexpected tray/i.test(error)));
});

test('wrong active composer root is not accepted', () => {
  const snapshot = fixture();
  snapshot.composerRoot.count = 2;
  const result = validateComposerState(snapshot, EXPECTED);
  assert.equal(result.ok, false);
  assert.ok(result.errors.some((error) => /composer root/i.test(error)));
});

test('stale media identity fails both inline and tray coverage', () => {
  const snapshot = fixture();
  snapshot.editor.inlineChips[1] = { ...snapshot.editor.inlineChips[1], mentionId: 'stale-media' };
  snapshot.tray.trayChips[1] = { ...snapshot.tray.trayChips[1], providerId: 'stale-media' };
  const result = validateComposerState(snapshot, EXPECTED);
  assert.equal(result.ok, false);
  assert.ok(result.errors.some((error) => /media|unexpected|missing/i.test(error)));
});

test('conflicting known aliases on one inline chip fail closed', () => {
  const snapshot = fixture();
  snapshot.editor.inlineChips[0] = {
    ...snapshot.editor.inlineChips[0], entityId: 'stale-entity', mentionId: CHARACTER_ID,
  };
  const result = validateComposerState(snapshot, EXPECTED);
  assert.equal(result.ok, false);
  assert.ok(result.errors.some((error) => /inline chip.*exactly match|inline.*identity/i.test(error)));
});

test('conflicting known aliases on one media tray item fail closed', () => {
  const snapshot = fixture();
  snapshot.tray.trayChips[1] = {
    ...snapshot.tray.trayChips[1], providerId: MEDIA_ID, mediaId: 'stale-media',
  };
  const result = validateComposerState(snapshot, EXPECTED);
  assert.equal(result.ok, false);
  assert.ok(result.errors.some((error) => /media tray chip|media.*id/i.test(error)));
});

test('a non-visible tray chip is not accepted as intended coverage', () => {
  const snapshot = fixture();
  snapshot.tray.trayChips[0] = { ...snapshot.tray.trayChips[0], visible: false };
  const result = validateComposerState(snapshot, EXPECTED);
  assert.equal(result.ok, false);
  assert.ok(result.errors.some((error) => /tray chip 0 visibility/i.test(error)));
});

test('a tray chip without visibility evidence fails closed', () => {
  const snapshot = fixture();
  delete snapshot.tray.trayChips[1].visible;
  const result = validateComposerState(snapshot, EXPECTED);
  assert.equal(result.ok, false);
  assert.ok(result.errors.some((error) => /tray chip 1 visibility/i.test(error)));
});

test('wrong character identity or thumbnail binding fails closed', () => {
  const snapshot = fixture();
  snapshot.editor.inlineChips[0] = {
    ...snapshot.editor.inlineChips[0], text: 'OtherCharacter', entityId: 'other-entity', mentionId: 'other-entity',
  };
  snapshot.entityTrayBindings = [{ entityId: 'other-entity', thumbnailKey: 'other-thumb' }];
  snapshot.tray.trayChips[0] = { ...snapshot.tray.trayChips[0], thumbnailKey: 'other-thumb' };
  const result = validateComposerState(snapshot, EXPECTED);
  assert.equal(result.ok, false);
  assert.ok(result.errors.some((error) => /entity|character|Mike2/i.test(error)));
});

test('missing context observation blocks instead of passing by omission', () => {
  const snapshot = fixture();
  delete snapshot.contextChips;
  const result = validateComposerState(snapshot, EXPECTED);
  assert.equal(result.ok, false);
  assert.ok(result.errors.some((error) => /contextChips/i.test(error)));
});

test('pending picker or context selection blocks the prepared state', () => {
  const snapshot = fixture();
  snapshot.pendingOverlays = [{ kind: 'picker', state: 'open' }];
  const result = validateComposerState(snapshot, EXPECTED);
  assert.equal(result.ok, false);
  assert.ok(result.errors.some((error) => /pending/i.test(error)));
});

test('missing pending overlay count is unknown evidence, not an implicit zero', () => {
  const snapshot = fixture();
  delete snapshot.pendingOverlaysCount;
  const result = validateComposerState(snapshot, EXPECTED);
  assert.equal(result.ok, false);
  assert.ok(result.errors.some((error) => /pendingOverlaysCount/i.test(error)));
});
