import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import {
  PaidVideoRunner,
  VideoRunnerError,
  validateVideoPreflight,
} from '../extension/src/video-runner.js';

const HASH = 'a'.repeat(64);

function request(overrides = {}) {
  return {
    action: 'video_hook_generation',
    item_id: 'hook-001',
    idempotency_key: HASH,
    semantic_binding: { sentence_id: 'sentence-001', beat_id: 'beat-001' },
    project_url: 'https://labs.google/fx/tools/flow/project/example',
    requested_settings: {
      model: 'Veo 3',
      mode: 'video',
      aspect_ratio: '16:9',
      duration_seconds: 8,
      quantity: 1,
    },
    references: [{ path: 'references/host.png', sha256: HASH }],
    capability_snapshot: {
      snapshot_id: 'capability-001',
      expires_at: '2099-01-01T00:00:00Z',
      offerings: [{
        action: 'video_hook_generation',
        model: 'Veo 3',
        mode: 'video',
        aspect_ratio: '16:9',
        duration_seconds: 8,
        quantity: 1,
        displayed_credit_label: '4 credits',
        credit_state: 'positive',
        credits_per_generation: 4,
      }],
    },
    budget_policy: { kind: 'paid', expected_credits: 4, max_credits: 4 },
    approval_policy: { state: 'operator_approved', approval_id: 'approval-001', expected_account_verified: true },
    fallback: { provider: 'remotion_hyperframes', reason: 'Use deterministic Remotion/HyperFrames motion when Flow blocks.' },
    output_path: 'assets/quarantine/flow/hook-001.mp4',
    ...overrides,
  };
}

function root() {
  return {
    getAttribute(name) {
      return {
        'data-flow-account-verified': 'true',
        'data-flow-project-url': 'https://labs.google/fx/tools/flow/project/example',
      }[name] ?? null;
    },
  };
}

function observation(overrides = {}) {
  return {
    ok: true,
    root: { ok: true, element: root() },
    settings: {
      values: { model: 'Veo 3', mode: 'video', ratio: '16:9', duration: '8s', quantity: '1' },
    },
    references: { count: 1 },
    account: { verified: true },
    credit: { known: true, paid: true, cost: 4, observed: '4 credits' },
    media: { items: [], failures: [] },
    ...overrides,
  };
}

function harness({ submit = async () => ({ ok: true }), creditValues = [0, 4] } = {}) {
  let snapshotCount = 0;
  let creditIndex = 0;
  const calls = { prepare: 0, submit: 0, wait: 0, download: 0, imports: [], creditEvents: [] };
  const driver = {
    snapshot() {
      snapshotCount += 1;
      if (snapshotCount <= 2) return observation();
      return observation({
        media: { items: [{ id: 'new-video-001', requestId: 'hook-001', url: 'https://cdn.example/hook-001.mp4', status: 'settled', settled: true }], failures: [] },
      });
    },
    async prepare() { calls.prepare += 1; return { ok: true, state: 'ready_to_submit' }; },
    async submit() { calls.submit += 1; return submit(); },
    async waitForGeneration() { calls.wait += 1; return { ok: true, state: 'completed' }; },
  };
  const runner = new PaidVideoRunner({
    driver,
    timeoutMs: 1000,
    pollIntervalMs: 0,
    stabilityPolls: 2,
    downloader: async ({ itemId, requestId, media }) => {
      calls.download += 1;
      return { downloadId: 77, path: 'downloads/hook-001.mp4', itemId, requestId, mediaId: media.id };
    },
    importer: async (context) => {
      calls.imports.push(context);
      return { output_path: context.outputPath, output_sha256: HASH, review_state: 'quarantined', render_eligible: false };
    },
    creditReader: async () => creditValues[Math.min(creditIndex++, creditValues.length - 1)],
    creditRecorder: { record: async (event) => { calls.creditEvents.push(event); } },
  });
  return { runner, calls };
}

test('paid video preflight verifies exact settings, displayed cost, approval, ceiling, and fallback', () => {
  const result = validateVideoPreflight(request(), observation());
  assert.equal(result.ok, true);
  assert.equal(result.credits.expected, 4);
  assert.equal(result.credits.max, 4);
  assert.equal(result.approval.approval_id, 'approval-001');
  assert.equal(result.fallback.provider, 'remotion_hyperframes');
  assert.equal(Object.isFrozen(result), true);
});

test('cost mismatch, missing approval, and an insufficient ceiling block before submit', () => {
  const mismatch = validateVideoPreflight(request(), observation({ credit: { known: true, paid: true, cost: 5, observed: '5 credits' } }));
  assert.equal(mismatch.ok, false);
  assert.ok(mismatch.failures.some((failure) => failure.code === 'displayed_cost_mismatch'));

  const approval = validateVideoPreflight(request({ approval_policy: { state: 'not_requested', approval_id: null, expected_account_verified: true } }), observation());
  assert.equal(approval.ok, false);
  assert.ok(approval.failures.some((failure) => failure.code === 'operator_approval_required'));

  const ceiling = validateVideoPreflight(request({ budget_policy: { kind: 'paid', expected_credits: 4, max_credits: 3 } }), observation());
  assert.equal(ceiling.ok, false);
  assert.ok(ceiling.failures.some((failure) => failure.code === 'credit_ceiling_exceeded'));
});

test('batch-scoped displayed cost and explicitly unknown cost are handled fail-closed', () => {
  const batchCost = validateVideoPreflight(request(), observation({
    credit: { known: true, paid: true, batchCost: 4, observed: '4 credits for this batch' },
  }));
  assert.equal(batchCost.ok, true);
  assert.equal(batchCost.displayed_cost.scope, 'batch');

  const unknown = validateVideoPreflight(request(), observation({
    credit: { known: false, paid: true, cost: 4, observed: '4 credits' },
  }));
  assert.equal(unknown.ok, false);
  assert.ok(unknown.failures.some((failure) => failure.code === 'displayed_cost_unknown'));
});

test('runner submits only after preflight, associates the exact new video, quarantines it, and records actual credits', async () => {
  const { runner, calls } = harness();
  const result = await runner.run(request());
  assert.equal(result.status, 'completed');
  assert.equal(result.outputs.length, 1);
  assert.equal(result.outputs[0].media.id, 'new-video-001');
  assert.equal(calls.prepare, 1);
  assert.equal(calls.submit, 1);
  assert.equal(calls.download, 1);
  assert.equal(calls.imports[0].requestId, 'hook-001');
  assert.equal(result.credits.actual, 4);
  assert.equal(result.credits.failed_attempt_credits, 0);
  assert.equal(result.fallback.provider, 'remotion_hyperframes');
  assert.equal(result.review_state, 'quarantined');
  assert.equal(result.render_eligible, false);
  assert.equal(result.quarantine.render_eligible, false);
  assert.equal(Object.isFrozen(result), true);
  assert.equal(calls.creditEvents.length, 1);
  assert.equal(calls.creditEvents[0].outcome, 'completed');
});

test('failed paid attempts record actual credits and are not relabeled as unspent', async () => {
  const { runner, calls } = harness({
    submit: async () => { throw new Error('provider rejected after submit'); },
    creditValues: [0, 4],
  });
  await assert.rejects(runner.run(request()), (error) => {
    assert.ok(error instanceof VideoRunnerError);
    assert.equal(error.result.status, 'failed');
    assert.equal(error.result.credits.actual, 4);
    assert.equal(error.result.credits.failed_attempt_credits, 4);
    return true;
  });
  assert.equal(calls.submit, 1);
  assert.equal(calls.creditEvents.length, 1);
  assert.equal(calls.creditEvents[0].outcome, 'failed');
  assert.equal(calls.creditEvents[0].failed_attempt_credits, 4);
});

test('completed item is skipped on retry/restart without submitting again', async () => {
  const { runner, calls } = harness();
  const first = await runner.run(request());
  const second = await runner.run({ ...request(), status: 'completed', result: first });
  assert.equal(second.skipped, true);
  assert.equal(calls.submit, 1);
});

test('service worker routes authored video actions through the paid runner', () => {
  const source = readFileSync(new URL('../extension/src/service-worker.js', import.meta.url), 'utf8');
  assert.match(source, /import \{ createVideoRunner, FLOW_VIDEO_ACTIONS \}/);
  assert.match(source, /FLOW_VIDEO_ACTIONS\.includes\(job\.action \|\| job\.batch_action\)/);
  assert.match(source, /isVideoJob \? createVideoRunner : createImageRunner/);
  assert.match(source, /credits: error\?\.credits \|\| error\?\.result\?\.credits \|\| null/);
});
