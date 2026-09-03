import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';

const testDir = path.dirname(fileURLToPath(import.meta.url));
const manifestPath = path.resolve(testDir, '..', 'extension', 'manifest.json');
const serviceWorkerPath = path.resolve(testDir, '..', 'extension', 'src', 'service-worker.js');

test('flow extension manifest is constrained MV3 shell', async () => {
  const raw = await fs.readFile(manifestPath, 'utf8');
  const manifest = JSON.parse(raw);

  assert.equal(manifest.manifest_version, 3);
  assert.equal(typeof manifest.minimum_chrome_version, 'string');
  assert.equal(parseInt(manifest.minimum_chrome_version, 10), 114);
  assert.equal(manifest.background?.service_worker, 'src/service-worker.js');
  assert.equal(manifest.background?.type, 'module');
  assert.equal(manifest.side_panel?.default_path, 'src/sidepanel.html');
  assert.equal(manifest.permissions?.length, 5);
  assert.deepEqual([...manifest.permissions].sort(), ['debugger', 'downloads', 'nativeMessaging', 'sidePanel', 'storage'].sort());
  assert.equal(manifest.host_permissions?.length, 1);
  assert.equal(manifest.host_permissions[0], 'https://labs.google/fx/*');
  assert.equal(manifest.content_scripts?.length, 1);
  assert.deepEqual(manifest.content_scripts[0].matches, ['https://labs.google/fx/*']);
  assert.deepEqual(manifest.content_scripts[0].js, ['dist/content-script.bundle.js']);
  assert.equal(manifest.content_scripts[0].run_at, 'document_idle');
});

test('service worker uses durable state and a long-lived native port', async () => {
  const source = await fs.readFile(serviceWorkerPath, 'utf8');
  assert.match(source, /chrome\.storage\.local/);
  assert.match(source, /chrome\.runtime\.connectNative/);
  assert.doesNotMatch(source, /chrome\.runtime\.sendNativeMessage/);
  assert.doesNotMatch(source, /onMessageExternal/);
});

test('service worker binds the serial browser executor to native queue lifecycle', async () => {
  const source = await fs.readFile(serviceWorkerPath, 'utf8');
  assert.match(source, /createImageRunner/);
  assert.match(source, /FLOW_DRIVER_CONTENT_READY/);
  assert.match(source, /method: 'claim_next'/);
  assert.match(source, /method: 'import_output'/);
  assert.match(source, /method: 'complete'/);
  assert.match(source, /method: 'fail'/);
  assert.match(source, /chrome\.debugger\.attach/);
  assert.match(source, /Input\.insertText/);
  assert.match(source, /FLOW_UI_ARM_BOUNDED_IMAGE/);
  assert.doesNotMatch(source, /requestId:\s*job\.item_id/);
});
