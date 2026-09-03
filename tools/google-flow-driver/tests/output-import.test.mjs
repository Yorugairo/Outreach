import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import {
  OutputImportError,
  importOutput,
  validateOutputFile,
} from '../native-host/import-output.mjs';
import { handleNativeRequest } from '../native-host/host.mjs';
import { assertMetadataOnly } from '../shared/contracts.mjs';
import { createQueue } from '../shared/queue.mjs';

const PNG = Buffer.concat([
  Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]),
  Buffer.from('flow-test-image'),
]);

async function fixture() {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'flow-import-'));
  const downloadsRoot = path.join(root, 'downloads');
  const quarantineRoot = path.join(root, 'project', 'assets', 'quarantine', 'flow');
  await fs.mkdir(downloadsRoot, { recursive: true });
  await fs.mkdir(quarantineRoot, { recursive: true });
  const sourcePath = path.join(downloadsRoot, 'flow-item.png');
  await fs.writeFile(sourcePath, PNG);
  return { root, downloadsRoot, projectRoot: path.join(root, 'project'), quarantineRoot, sourcePath };
}

test('output import validates, hashes, and keeps media quarantined and immutable', async () => {
  const f = await fixture();
  try {
    const validation = await validateOutputFile(f.sourcePath);
    assert.equal(validation.mimeType, 'image/png');
    const result = await importOutput({
      sourcePath: f.sourcePath,
      downloadsRoot: f.downloadsRoot,
      projectRoot: f.projectRoot,
      quarantineRoot: f.quarantineRoot,
      outputPath: 'item-1.png',
      itemId: 'item-1',
      requestId: 'request-1',
      downloadId: 42,
    });
    assert.equal(result.review_state, 'quarantined');
    assert.equal(result.render_eligible, false);
    assert.equal(result.project_relative_path, 'assets/quarantine/flow/item-1.png');
    assert.equal(result.sha256, crypto.createHash('sha256').update(PNG).digest('hex'));
    assert.doesNotThrow(() => assertMetadataOnly(result));
    assert.equal(Object.isFrozen(result), true);
    const reused = await importOutput({
      sourcePath: f.sourcePath,
      downloadsRoot: f.downloadsRoot,
      projectRoot: f.projectRoot,
      quarantineRoot: f.quarantineRoot,
      outputPath: 'item-1.png',
    });
    assert.equal(reused.reused, true);
  } finally {
    await fs.rm(f.root, { recursive: true, force: true });
  }
});

test('output import rejects escapes, invalid bytes, and immutable destination conflicts', async () => {
  const f = await fixture();
  try {
    await assert.rejects(
      importOutput({ sourcePath: f.sourcePath, downloadsRoot: f.downloadsRoot, projectRoot: f.projectRoot, quarantineRoot: f.quarantineRoot, outputPath: '../outside.png' }),
      (error) => error instanceof OutputImportError && error.code === 'unsafe_quarantine_path',
    );
    await fs.writeFile(path.join(f.downloadsRoot, 'bad.png'), 'not-an-image');
    await assert.rejects(
      importOutput({ sourcePath: path.join(f.downloadsRoot, 'bad.png'), downloadsRoot: f.downloadsRoot, projectRoot: f.projectRoot, quarantineRoot: f.quarantineRoot, outputPath: 'bad.png' }),
      (error) => error instanceof OutputImportError && error.code === 'invalid_media_bytes',
    );
    const destination = path.join(f.quarantineRoot, 'item-1.png');
    await fs.writeFile(destination, Buffer.from('different'));
    await assert.rejects(
      importOutput({ sourcePath: f.sourcePath, downloadsRoot: f.downloadsRoot, projectRoot: f.projectRoot, quarantineRoot: f.quarantineRoot, outputPath: 'item-1.png' }),
      (error) => error instanceof OutputImportError && error.code === 'destination_conflict',
    );
  } finally {
    await fs.rm(f.root, { recursive: true, force: true });
  }
});

test('native import dispatch fixes project and download roots outside caller control', async () => {
  const f = await fixture();
  try {
    const queue = createQueue({
      projectRoot: f.projectRoot,
      runtimeRoot: path.join(f.projectRoot, '.codex', 'flow-runtime'),
      downloadsRoot: f.downloadsRoot,
    });
    const response = await handleNativeRequest({
      request_id: 'native-import-1',
      method: 'import_output',
      params: {
        source_path: f.sourcePath,
        output_path: 'assets/quarantine/flow/native-item.png',
        item_id: 'native-item',
        request_id: 'request-native-item',
        download_id: 17,
      },
    }, queue, {
      projectRoot: f.projectRoot,
      downloadsRoot: f.downloadsRoot,
      quarantineRoot: f.quarantineRoot,
    });
    assert.equal(response.ok, true);
    assert.equal(response.result.project_relative_path, 'assets/quarantine/flow/native-item.png');
    assert.doesNotThrow(() => assertMetadataOnly(response));
  } finally {
    await fs.rm(f.root, { recursive: true, force: true });
  }
});

test('video outputs use the same signature-validated immutable quarantine path', async () => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'flow-video-import-'));
  const projectRoot = path.join(root, 'project');
  const downloadsRoot = path.join(root, 'downloads');
  await fs.mkdir(projectRoot, { recursive: true });
  await fs.mkdir(downloadsRoot, { recursive: true });
  const sourcePath = path.join(downloadsRoot, 'hook.mp4');
  await fs.writeFile(sourcePath, Buffer.concat([Buffer.from([0, 0, 0, 24]), Buffer.from('ftypisom'), Buffer.alloc(32)]));
  const result = await importOutput({
    sourcePath,
    downloadsRoot,
    projectRoot,
    outputPath: 'assets/quarantine/flow/hook.mp4',
    itemId: 'video-hook-1',
  });
  assert.equal(result.mime_type, 'video/mp4');
  assert.equal(result.project_relative_path, 'assets/quarantine/flow/hook.mp4');
  assert.equal(result.review_state, 'quarantined');
  assert.equal(result.render_eligible, false);
});
