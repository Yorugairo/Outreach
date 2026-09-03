import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import { DurableFlowQueue } from '../shared/queue.mjs';

async function makeQueue(options = {}) {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'flow-queue-'));
  return {
    root,
    queue: new DurableFlowQueue({ runtimeRoot: path.join(root, 'runtime'), projectRoot: root, ...options }),
  };
}

function job(overrides = {}) {
  return {
    job_id: 'image-job-001',
    idempotency_key: 'a'.repeat(64),
    batch_id: 'image-batch-001',
    item_id: 'item-001',
    action: 'image_generation',
    output_path: 'quarantine/flow/item-001.png',
    ...overrides,
  };
}

test('queue writes, claims, completes atomically and suppresses duplicate idempotency keys', async () => {
  const { root, queue } = await makeQueue();
  const first = await queue.enqueue(job());
  assert.equal(first.created, true);
  const duplicate = await queue.enqueue(job({ job_id: 'different-job-should-not-run' }));
  assert.equal(duplicate.duplicate, true);
  assert.equal(duplicate.job.job_id, 'image-job-001');

  const claimed = await queue.claimNext();
  assert.equal(claimed.status, 'active');
  assert.equal(claimed.attempt, 1);
  const completed = await queue.complete(claimed.job_id, {
    provider_media_id: 'flow-media-001',
    output_path: claimed.output_path,
    output_sha256: 'b'.repeat(64),
  });
  assert.equal(completed.status, 'completed');
  assert.equal((await queue.get(claimed.job_id)).state, 'completed');

  const files = await fs.readdir(path.join(root, 'runtime', 'events'));
  assert.equal(files.length, 3);
  assert.ok(files.every((name) => /^\d{12}-[a-z_]+\.json$/.test(name)));
  assert.equal((await fs.readdir(path.join(root, 'runtime', 'queue', 'pending'))).length, 0);
  assert.equal((await fs.readdir(path.join(root, 'runtime', 'queue', 'active'))).length, 0);
  assert.equal((await fs.readdir(path.join(root, 'runtime', 'queue', 'completed'))).length, 1);
  assert.equal((await fs.readdir(path.join(root, 'runtime', 'queue', 'index'))).length, 1);
  assert.equal((await fs.readdir(path.join(root, 'runtime', 'queue', 'completed'))).some((name) => name.endsWith('.tmp')), false);
});

test('active jobs recover to pending in deterministic order after restart', async () => {
  const { root } = await makeQueue({ autoRecover: false });
  const first = new DurableFlowQueue({ runtimeRoot: path.join(root, 'runtime'), projectRoot: root, autoRecover: false });
  await first.enqueue(job({ job_id: 'job-b', idempotency_key: 'b'.repeat(64) }));
  await first.enqueue(job({ job_id: 'job-a', idempotency_key: 'c'.repeat(64) }));
  assert.equal((await first.claimNext()).job_id, 'job-a');
  assert.equal((await first.claimNext()).job_id, 'job-b');

  const restarted = new DurableFlowQueue({ runtimeRoot: path.join(root, 'runtime'), projectRoot: root });
  const status = await restarted.status();
  assert.equal(status.counts.active, 0);
  assert.equal(status.counts.pending, 2);
  assert.deepEqual((await restarted.claimNext()).job_id, 'job-a');
});

test('queue restart finishes a terminal transition already persisted before a move', async () => {
  const { root } = await makeQueue({ autoRecover: false });
  const queue = new DurableFlowQueue({ runtimeRoot: path.join(root, 'runtime'), projectRoot: root, autoRecover: false });
  await queue.enqueue(job({ job_id: 'terminal-job', idempotency_key: 'g'.repeat(64) }));
  const claimed = await queue.claimNext();
  const activePath = path.join(root, 'runtime', 'queue', 'active', `${claimed.job_id}.json`);
  await fs.writeFile(activePath, `${JSON.stringify({ ...claimed, status: 'completed', result: { output_sha256: 'h'.repeat(64) } })}\n`);

  const restarted = new DurableFlowQueue({ runtimeRoot: path.join(root, 'runtime'), projectRoot: root });
  const recovered = await restarted.get(claimed.job_id);
  assert.equal(recovered.state, 'completed');
});

test('queue rejects paths outside the configured project root', async () => {
  const { root, queue } = await makeQueue();
  await assert.rejects(
    queue.enqueue(job({ output_path: '../outside.png', idempotency_key: 'd'.repeat(64) })),
    /escapes configured root/,
  );
});

test('queue refuses a job id collision with a different idempotency key', async () => {
  const { queue } = await makeQueue();
  await queue.enqueue(job());
  await assert.rejects(
    queue.enqueue(job({ idempotency_key: 'f'.repeat(64) })),
    /job_id already belongs/,
  );
});

test('pause state persists across restart, blocks claims, and resumes safely', async () => {
  const { root, queue } = await makeQueue();
  await queue.enqueue(job({ job_id: 'pause-job', idempotency_key: 'p'.repeat(64) }));

  const paused = await queue.pause();
  assert.equal(paused.paused, true);
  const control = JSON.parse(await fs.readFile(path.join(root, 'runtime', 'queue', 'control.json'), 'utf8'));
  assert.equal(control.paused, true);
  assert.equal(await queue.claimNext(), null);

  const restarted = new DurableFlowQueue({ runtimeRoot: path.join(root, 'runtime'), projectRoot: root });
  assert.equal((await restarted.status()).paused, true);
  assert.equal(await restarted.claimNext(), null);

  const resumed = await restarted.resume();
  assert.equal(resumed.paused, false);
  const claimed = await restarted.claimNext();
  assert.equal(claimed.job_id, 'pause-job');
  assert.equal(claimed.attempt, 1);

  const events = await Promise.all(
    (await fs.readdir(path.join(root, 'runtime', 'events')))
      .map(async (name) => JSON.parse(await fs.readFile(path.join(root, 'runtime', 'events', name), 'utf8'))),
  );
  assert.ok(events.some((event) => event.type === 'queue_paused'));
  assert.ok(events.some((event) => event.type === 'queue_resumed'));
});

test('retry requeues only failed or cancelled jobs without consuming an attempt', async () => {
  const { queue: invalidQueue } = await makeQueue();
  await invalidQueue.enqueue(job({ job_id: 'retry-pending', idempotency_key: 'q'.repeat(64) }));
  await assert.rejects(invalidQueue.retry('retry-pending'), /pending/);
  const active = await invalidQueue.claimNext();
  await assert.rejects(invalidQueue.retry(active.job_id), /active/);

  const { root, queue } = await makeQueue();
  await queue.enqueue(job({ job_id: 'retry-failed', idempotency_key: 'r'.repeat(64) }));
  const claimed = await queue.claimNext();
  const failed = await queue.fail(claimed.job_id, { code: 'temporary' });
  const retried = await queue.retry(claimed.job_id);
  assert.equal(retried.status, 'pending');
  assert.equal(retried.attempt, failed.attempt);
  assert.equal(retried.job_id, failed.job_id);
  assert.equal(retried.idempotency_key, failed.idempotency_key);
  assert.equal((await queue.get(claimed.job_id)).state, 'pending');
  const retryEventName = (await fs.readdir(path.join(root, 'runtime', 'events')))
    .find((name) => name.endsWith('-retry.json'));
  const retryEvent = JSON.parse(await fs.readFile(path.join(root, 'runtime', 'events', retryEventName), 'utf8'));
  assert.equal(retryEvent.type, 'retry');
  assert.equal(retryEvent.attempt, failed.attempt);

  const claimedAgain = await queue.claimNext();
  assert.equal(claimedAgain.attempt, failed.attempt + 1);
  const completed = await queue.complete(claimedAgain.job_id, { ok: true });
  await assert.rejects(queue.retry(completed.job_id), (error) => {
    assert.equal(error.code, 'invalid_transition');
    return /completed/.test(error.message);
  });

  await queue.enqueue(job({ job_id: 'retry-cancelled', idempotency_key: 's'.repeat(64) }));
  const cancelledClaim = await queue.claimNext();
  await queue.cancel(cancelledClaim.job_id, 'operator_cancelled');
  const cancelledRetry = await queue.retry(cancelledClaim.job_id);
  assert.equal(cancelledRetry.status, 'pending');
  assert.equal(cancelledRetry.attempt, cancelledClaim.attempt);

  const events = await queue.list();
  assert.equal(events.filter((entry) => entry.state === 'pending').length, 1);
});

test('sequential reference DAG holds dependent job until prerequisite completes and hydrates output path', async () => {
  const { root, queue } = await makeQueue();
  await queue.enqueue(job({ job_id: 'job-01', idempotency_key: '1'.repeat(64), output_path: 'quarantine/job-01.png' }));
  await queue.enqueue(job({
    job_id: 'job-02',
    idempotency_key: '2'.repeat(64),
    depends_on: 'job-01',
    references: [{ from_job: 'job-01', asset_id: 'char-01' }],
    output_path: 'quarantine/job-02.png',
  }));

  // First claim must be job-01 because job-02 depends on job-01
  const first = await queue.claimNext();
  assert.equal(first.job_id, 'job-01');

  // Second claim while job-01 is active returns null
  const second = await queue.claimNext();
  assert.equal(second, null);

  // Complete job-01 with quarantine output
  await queue.complete(first.job_id, {
    output_path: 'quarantine/job-01.png',
    output_sha256: '9'.repeat(64),
    outputs: [{ import: { output_path: 'quarantine/job-01.png', sha256: '9'.repeat(64) } }],
  });

  // Now job-02 is unblocked and claimed with hydrated reference
  const claimedJob2 = await queue.claimNext();
  assert.equal(claimedJob2.job_id, 'job-02');
  assert.equal(claimedJob2.references.length, 1);
  assert.equal(claimedJob2.references[0].path, 'quarantine/job-01.png');
  assert.equal(claimedJob2.references[0].sha256, '9'.repeat(64));
});

