import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';

import { buildCapabilitySnapshot, CapabilityCaptureError } from '../extension/src/capability-capture.js';
import { sha256 } from '../shared/contracts.mjs';
import { createQueue } from '../shared/queue.mjs';
import { handleNativeRequest } from '../native-host/host.mjs';
import { writeCapabilitySnapshot } from '../native-host/write-capability.mjs';

function observation(overrides = {}) {
  return {
    ok: true,
    selectorVersion: 'flow-selectors.v1',
    root: { ok: true, projectId: 'project-001', accountVerified: false },
    settings: { ambiguous: false, unexpectedMenuCount: 0, values: { mode: 'image', model: 'Nano Banana Pro 2', ratio: '16:9', duration: null, quantity: '2' } },
    credit: { known: true, zero: true, paid: false, cost: 0, observed: '0 credits' },
    page: { url: 'https://labs.google/fx/tools/flow/project/project-001' },
    ...overrides,
  };
}

test('operator-confirmed UI observation becomes a current zero-credit capability snapshot', async () => {
  const snapshot = await buildCapabilitySnapshot({
    observation: observation(),
    accountMarker: 'primary-flow-account',
    operatorConfirmedAccount: true,
    extensionVersion: '0.1.0',
    observedAt: '2026-08-09T13:00:00.000Z',
  });
  assert.equal(snapshot.offerings[0].action, 'image_generation');
  assert.equal(snapshot.offerings[0].credits_per_generation, 0);
  assert.equal(snapshot.offerings[0].duration_seconds, null);
  const core = { ...snapshot };
  delete core.artifact_hash;
  assert.equal(snapshot.artifact_hash, sha256(core));
});

test('unknown price, unconfirmed account, and ambiguous settings fail closed', async () => {
  const common = { accountMarker: 'primary', extensionVersion: '0.1.0' };
  await assert.rejects(buildCapabilitySnapshot({ observation: observation(), ...common }), (error) => error instanceof CapabilityCaptureError && error.code === 'account_not_confirmed');
  await assert.rejects(buildCapabilitySnapshot({ observation: observation({ credit: { known: false } }), operatorConfirmedAccount: true, ...common }), (error) => error.code === 'credit_unknown');
  await assert.rejects(buildCapabilitySnapshot({ observation: observation({ settings: { ambiguous: true, values: {} } }), operatorConfirmedAccount: true, ...common }), (error) => error.code === 'settings_ambiguous');
});

test('native writer persists one immutable root-constrained capability artifact', async () => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'flow-capability-'));
  const snapshot = await buildCapabilitySnapshot({ observation: observation(), accountMarker: 'primary', operatorConfirmedAccount: true, extensionVersion: '0.1.0' });
  const outputPath = 'provider-jobs/smoke.capability.v1.json';
  const first = await writeCapabilitySnapshot({ projectRoot: root, outputPath, snapshot });
  assert.equal(first.existing, false);
  const second = await writeCapabilitySnapshot({ projectRoot: root, outputPath, snapshot });
  assert.equal(second.existing, true);
  await assert.rejects(writeCapabilitySnapshot({ projectRoot: root, outputPath: '../outside.json', snapshot }), /escapes configured root/);
  await assert.rejects(writeCapabilitySnapshot({ projectRoot: root, outputPath, snapshot: { ...snapshot, account: { marker: 'other', verified: true } } }), /artifact_hash is stale/);
});

test('native protocol writes capability only beneath its fixed project root', async () => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'flow-capability-native-'));
  const snapshot = await buildCapabilitySnapshot({ observation: observation(), accountMarker: 'primary', operatorConfirmedAccount: true, extensionVersion: '0.1.0' });
  const queue = createQueue({ projectRoot: root, runtimeRoot: path.join(root, '.codex', 'flow-runtime') });
  const response = await handleNativeRequest({
    request_id: 'capability-1',
    method: 'write_capability_snapshot',
    params: { output_path: 'provider-jobs/current.capability.v1.json', snapshot },
  }, queue, { projectRoot: root });
  assert.equal(response.ok, true);
  assert.equal(response.result.output_path, 'provider-jobs/current.capability.v1.json');
  const escaped = await handleNativeRequest({
    request_id: 'capability-2',
    method: 'write_capability_snapshot',
    params: { output_path: '../outside.json', snapshot },
  }, queue, { projectRoot: root });
  assert.equal(escaped.ok, false);
  assert.equal(escaped.error.code, 'unsafe_path');
});
