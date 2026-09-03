import assert from 'node:assert/strict';
import test from 'node:test';
import { ImageRunnerError, SerialImageRunner } from '../extension/src/image-runner.js';

function item(overrides = {}) {
  return {
    item_id: 'item-1',
    idempotency_key: 'i'.repeat(64),
    request_id: 'request-1',
    settings: { quantity: 1 },
    output_path: 'assets/quarantine/flow/item-1.png',
    ...overrides,
  };
}

function harness({ gate = null } = {}) {
  let snapshots = 0;
  const calls = { prepare: 0, submit: 0, wait: 0, download: 0, import: 0 };
  const driver = {
    snapshot() {
      snapshots += 1;
      return snapshots < 2
        ? { media: { items: [{ id: 'stale', status: 'settled', settled: true }], failures: [] } }
        : { media: { items: [
          { id: 'stale', status: 'settled', settled: true },
          { id: 'new-1', url: 'https://cdn.example/new-1.png', status: 'settled', settled: true },
        ], failures: [] } };
    },
    async prepare() { calls.prepare += 1; return { ok: true, state: 'ready_to_submit' }; },
    async submit() { calls.submit += 1; return { ok: true, state: 'submitted' }; },
    async waitForGeneration() { calls.wait += 1; await gate; return { ok: true, state: 'completed' }; },
  };
  const runner = new SerialImageRunner({
    driver,
    pollIntervalMs: 0,
    stabilityPolls: 2,
    timeoutMs: 1000,
    downloader: async () => { calls.download += 1; return { downloadId: 11, path: 'downloads/item-1.png' }; },
    importer: async ({ outputPath, itemId }) => { calls.import += 1; return { output_path: outputPath, item_id: itemId, sha256: 'a'.repeat(64) }; },
  });
  return { runner, calls };
}

test('serial image runner excludes stale media and records quarantined immutable result', async () => {
  const { runner, calls } = harness();
  const result = await runner.run(item());
  assert.equal(result.status, 'completed');
  assert.equal(result.outputs.length, 1);
  assert.equal(result.outputs[0].media.id, 'new-1');
  assert.equal(result.outputs[0].import.review_state, undefined);
  assert.equal(calls.prepare, 1);
  assert.equal(calls.submit, 1);
  assert.equal(calls.download, 1);
  assert.equal(calls.import, 1);
  assert.equal(Object.isFrozen(result), true);
});

test('a second request cannot submit while one request is active', async () => {
  let release;
  const gate = new Promise((resolve) => { release = resolve; });
  const { runner } = harness({ gate });
  const first = runner.run(item());
  await new Promise((resolve) => setImmediate(resolve));
  await assert.rejects(runner.run(item({ item_id: 'item-2', idempotency_key: 'j'.repeat(64), request_id: 'request-2' })), (error) => error instanceof ImageRunnerError && error.code === 'active_request_exists');
  release();
  await first;
});

test('restart/resume skips completed items and never resubmits their idempotency key', async () => {
  const { runner, calls } = harness();
  const result = await runner.runBatch([
    item({ status: 'completed', result: { output_path: 'assets/quarantine/flow/item-1.png' } }),
  ]);
  assert.equal(result.skipped_count, 1);
  assert.equal(result.completed_count, 1);
  assert.equal(calls.submit, 0);
});
