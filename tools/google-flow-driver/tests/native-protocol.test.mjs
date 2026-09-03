import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import {
  NativeProtocolError,
  decodeNativeMessages,
  encodeNativeMessage,
  handleNativeRequest,
} from '../native-host/host.mjs';
import { DurableFlowQueue } from '../shared/queue.mjs';

test('native framing handles partial and multiple little-endian messages', () => {
  const first = encodeNativeMessage({ request_id: 'one', method: 'ping' });
  const second = encodeNativeMessage({ request_id: 'two', method: 'status' });
  const combined = Buffer.concat([first, second]);
  const partial = decodeNativeMessages(combined.subarray(0, first.length - 2));
  assert.deepEqual(partial.messages, []);
  const decoded = decodeNativeMessages(Buffer.concat([partial.remainder, combined.subarray(first.length - 2)]));
  assert.deepEqual(decoded.messages.map((message) => message.request_id), ['one', 'two']);
  assert.equal(decoded.remainder.length, 0);
  assert.equal(first.readUInt32LE(0), first.length - 4);
});

test('native framing rejects binary payloads and oversize frames', () => {
  assert.throws(() => encodeNativeMessage({ bytes: Buffer.from('media') }), NativeProtocolError);
  const oversized = Buffer.alloc(4);
  oversized.writeUInt32LE(64 * 1024 * 1024 + 1, 0);
  assert.throws(() => decodeNativeMessages(oversized), /64 MiB/);
  assert.throws(
    () => encodeNativeMessage({ diagnostic: Array.from({ length: 5 }, () => 'x'.repeat(240 * 1024)) }),
    /1 MiB/,
  );
});

test('native protocol exposes queue metadata without media bytes', async () => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'flow-native-'));
  const queue = new DurableFlowQueue({ runtimeRoot: path.join(root, 'runtime'), projectRoot: root });
  const enqueued = await handleNativeRequest({
    request_id: 'enqueue-1',
    method: 'enqueue',
    params: {
      job: {
        job_id: 'native-job-001',
        idempotency_key: 'e'.repeat(64),
        output_path: 'quarantine/native.png',
      },
    },
  }, queue);
  assert.equal(enqueued.ok, true);
  assert.equal(enqueued.result.created, true);

  const status = await handleNativeRequest({ request_id: 'status-1', method: 'status' }, queue);
  assert.equal(status.ok, true);
  assert.equal(status.result.counts.pending, 1);
  assert.equal(Object.hasOwn(status.result, 'bytes'), false);

  const duplicate = await handleNativeRequest({
    request_id: 'enqueue-2',
    method: 'enqueue',
    params: { job: { job_id: 'different', idempotency_key: 'e'.repeat(64), output_path: 'quarantine/native.png' } },
  }, queue);
  assert.equal(duplicate.result.duplicate, true);
});

test('native dispatch exposes durable pause, resume, retry, and status controls', async () => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'flow-native-controls-'));
  const queue = new DurableFlowQueue({ runtimeRoot: path.join(root, 'runtime'), projectRoot: root });
  const request = (request_id, method, params = {}) => handleNativeRequest({ request_id, method, params }, queue);

  const enqueued = await request('enqueue-controls', 'enqueue', {
    job: {
      job_id: 'native-controls-job',
      idempotency_key: 'n'.repeat(64),
      output_path: 'quarantine/native-controls.png',
    },
  });
  assert.equal(enqueued.ok, true);

  const paused = await request('pause-controls', 'pause_queue');
  assert.equal(paused.ok, true);
  assert.equal(paused.result.paused, true);
  assert.equal((await request('status-paused', 'status')).result.paused, true);
  assert.equal((await request('claim-paused', 'claim_next')).result.job, null);

  const resumed = await request('resume-controls', 'resume_queue');
  assert.equal(resumed.result.paused, false);
  const claimed = await request('claim-controls', 'claim_next');
  assert.equal(claimed.result.job.status, 'active');
  await request('fail-controls', 'fail', { job_id: claimed.result.job.job_id, error: { code: 'retryable' } });

  const retried = await request('retry-controls', 'retry_job', { job_id: claimed.result.job.job_id });
  assert.equal(retried.ok, true);
  assert.equal(retried.result.job.status, 'pending');
  assert.equal(retried.result.job.attempt, 1);

  const claimAgain = await request('claim-again-controls', 'claim_next');
  await request('complete-controls', 'complete', { job_id: claimAgain.result.job.job_id, result: { ok: true } });
  const completedRetry = await request('retry-completed-controls', 'retry_job', { job_id: claimAgain.result.job.job_id });
  assert.equal(completedRetry.ok, false);
  assert.equal(completedRetry.error.code, 'invalid_transition');
});
