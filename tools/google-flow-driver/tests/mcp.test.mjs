import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import { sha256 } from '../shared/contracts.mjs';
import { DurableFlowQueue } from '../shared/queue.mjs';
import { MCP_TOOL_DEFINITIONS, makeToolHandlers } from '../mcp/tools.mjs';

const REQUIRED_TOOLS = [
  'flow_bridge_status',
  'flow_capture_capabilities',
  'flow_validate_batch',
  'flow_preflight_batch',
  'flow_enqueue_batch',
  'flow_batch_status',
  'flow_pause_queue',
  'flow_resume_queue',
  'flow_retry_item',
  'flow_cancel_job',
  'flow_capture_diagnostic',
];

function withArtifactHash(core) {
  return { ...core, artifact_hash: sha256(core) };
}

async function createManifestFixture(root) {
  const outputRoot = path.join(root, 'output');
  const referencesRoot = path.join(root, 'references');
  const artifactRoot = path.join(root, 'artifacts');
  const outputPath = 'output';
  const manifestPath = path.join(root, 'batch.manifest.json');
  const capabilityPath = path.join(artifactRoot, 'capability.json');
  const referencePath = path.join(referencesRoot, 'reference.bin');
  const refRel = path.relative(root, referencePath);
  const bindingRel = path.relative(root, capabilityPath);

  await fs.mkdir(outputRoot, { recursive: true });
  await fs.mkdir(referencesRoot, { recursive: true });
  await fs.mkdir(artifactRoot, { recursive: true });
  await fs.writeFile(referencePath, 'reference', 'utf8');

  const capability = withArtifactHash({
    schema_version: 'google_flow_capability_snapshot.v1',
    snapshot_id: 'snapshot-main',
    project_url: 'https://labs.google/fx/tools/flow',
    project_id: 'project-main',
    observed_at: '2026-08-09T00:00:00Z',
    expires_at: '2099-01-02T00:00:00Z',
    account: {
      marker: 'acct-1',
      verified: true,
    },
    extension_version: '1.0.0',
    selector_version: '1.0.0',
    offerings: [
      {
        action: 'image_generation',
        model: 'nano-banana-pro',
        mode: 'image',
        aspect_ratio: '1:1',
        duration_seconds: null,
        quantity: 1,
        displayed_credit_label: 'zero credits',
        credit_state: 'zero',
        credits_per_generation: 0,
      },
    ],
    render_eligible: false,
    review_state: 'observed',
  });
  const capabilityBytes = `${JSON.stringify(capability, null, 2)}\n`;
  await fs.writeFile(capabilityPath, capabilityBytes, 'utf8');

  const prompt = 'A cinematic hero frame with clean lighting.';

  const manifest = {
    schema_version: 'google_flow_provider_batch.v1',
    batch_id: 'batch-main',
    channel_id: 'channel-1',
    episode_id: 'episode-1',
    action: 'image_generation',
    project_url: 'https://labs.google/fx/tools/flow',
    capability_snapshot: {
        path: bindingRel,
        sha256: sha256(Buffer.from(capabilityBytes, 'utf8')),
        artifact_hash: capability.artifact_hash,
    },
    requested_settings: {
      model: 'nano-banana-pro',
      mode: 'image',
      aspect_ratio: '1:1',
      quantity: 1,
      duration_seconds: null,
    },
    items: [
      {
        item_id: 'item-1',
        ordinal: 0,
        semantic_binding: {
          type: 'shot',
          sentence: 'A hero image for a sample campaign.',
        },
        prompt,
        prompt_sha256: sha256(prompt),
        references: [
          {
            path: refRel,
            sha256: sha256(Buffer.from('reference', 'utf8')),
          },
        ],
        output_path: path.join(outputPath, 'item-1.png'),
        idempotency_key: sha256('idempotent-1'),
      },
    ],
    output_root: outputPath,
    budget_policy: {
      kind: 'zero_credit',
      expected_credits: 0,
      max_credits: 0,
      standing_policy_id: 'test-zero-credit-policy',
    },
    approval_policy: {
      state: 'standing_policy_approved',
      approval_id: null,
      expected_account_verified: true,
    },
    fallback: {
      provider: 'local',
      reason: 'manual',
    },
    status: 'planned',
    review_state: 'quarantined',
    render_eligible: false,
  };

  manifest.artifact_hash = sha256(manifest);

  await fs.writeFile(manifestPath, JSON.stringify(manifest, null, 2), 'utf8');
  return { manifestPath, manifest, outputPath };
}

async function buildHarness() {
  const projectRoot = await fs.mkdtemp(path.join(os.tmpdir(), 'flow-mcp-'));
  const queue = new DurableFlowQueue({
    runtimeRoot: path.join(projectRoot, '.codex', 'flow-runtime'),
    projectRoot,
  });
  const fixture = await createManifestFixture(projectRoot);
  const handlers = makeToolHandlers({ queue, projectRoot });
  return { projectRoot, queue, handlers, fixture };
}

test('tool registry exports only the required flow adapter tools', async () => {
  const names = MCP_TOOL_DEFINITIONS.map((tool) => tool.name).sort();
  assert.deepEqual(names, REQUIRED_TOOLS.slice().sort());
});

test('validation and enqueueing are manifest-path bound with root guards', async () => {
  const { projectRoot, queue, handlers, fixture } = await buildHarness();
  try {
    await assert.rejects(
      () => handlers.flow_capture_capabilities({ capability_path: '../outside/capability.json' }),
      /unsafe_path|escapes configured root/i,
    );

    const invalidCapture = await handlers.flow_capture_capabilities({ capability_path: fixture.manifestPath });
    assert.equal(invalidCapture.ok, false);
    assert.equal(invalidCapture.errors.length > 0, true);

    const invalidManifestPath = path.join(projectRoot, 'invalid.manifest.json');
    const invalid = { ...fixture.manifest, status: 'bad-state' };
    await fs.writeFile(invalidManifestPath, JSON.stringify(invalid, null, 2), 'utf8');
    const rejected = await handlers.flow_validate_batch({ manifest_path: invalidManifestPath });
    assert.equal(rejected.ok, false);

    const notEnqueued = await handlers.flow_enqueue_batch({ manifest_path: invalidManifestPath });
    assert.equal(notEnqueued.ok, false);
    assert.equal((await queue.status()).total, 0);
  } finally {
    await fs.rm(projectRoot, { recursive: true, force: true });
  }
});

test('validation fails closed on prompt, capability-byte, and expiry drift', async () => {
  const { projectRoot, handlers, fixture } = await buildHarness();
  try {
    const promptDrift = structuredClone(fixture.manifest);
    promptDrift.items[0].prompt = `${promptDrift.items[0].prompt} altered`;
    delete promptDrift.artifact_hash;
    promptDrift.artifact_hash = sha256(promptDrift);
    const promptPath = path.join(projectRoot, 'prompt-drift.manifest.json');
    await fs.writeFile(promptPath, `${JSON.stringify(promptDrift, null, 2)}\n`, 'utf8');
    const promptResult = await handlers.flow_validate_batch({ manifest_path: promptPath });
    assert.equal(promptResult.ok, false);
    assert.equal(promptResult.errors.some((error) => error.includes('prompt_sha256')), true);

    const capabilityPath = path.join(projectRoot, fixture.manifest.capability_snapshot.path);
    await fs.appendFile(capabilityPath, ' ', 'utf8');
    const byteResult = await handlers.flow_validate_batch({ manifest_path: fixture.manifestPath });
    assert.equal(byteResult.ok, false);
    assert.equal(byteResult.errors.some((error) => error.includes('sha256 does not match local bytes')), true);

    const expiredCapabilityCore = JSON.parse(await fs.readFile(capabilityPath, 'utf8'));
    delete expiredCapabilityCore.artifact_hash;
    expiredCapabilityCore.expires_at = '2020-01-01T00:00:00Z';
    const expiredCapability = withArtifactHash(expiredCapabilityCore);
    const expiredBytes = `${JSON.stringify(expiredCapability, null, 2)}\n`;
    await fs.writeFile(capabilityPath, expiredBytes, 'utf8');
    const expiredManifest = structuredClone(fixture.manifest);
    expiredManifest.capability_snapshot.sha256 = sha256(Buffer.from(expiredBytes, 'utf8'));
    expiredManifest.capability_snapshot.artifact_hash = expiredCapability.artifact_hash;
    delete expiredManifest.artifact_hash;
    expiredManifest.artifact_hash = sha256(expiredManifest);
    const expiredPath = path.join(projectRoot, 'expired.manifest.json');
    await fs.writeFile(expiredPath, `${JSON.stringify(expiredManifest, null, 2)}\n`, 'utf8');
    const expiredResult = await handlers.flow_validate_batch({ manifest_path: expiredPath });
    assert.equal(expiredResult.ok, false);
    assert.equal(expiredResult.errors.some((error) => error.includes('expired')), true);
  } finally {
    await fs.rm(projectRoot, { recursive: true, force: true });
  }
});

test('enqueue only persists validated manifest jobs with manifest lineage', async () => {
  const { projectRoot, handlers, queue, fixture } = await buildHarness();
  try {
    const validated = await handlers.flow_validate_batch({ manifest_path: fixture.manifestPath });
    assert.equal(validated.ok, true, JSON.stringify(validated.errors));
    const enqueued = await handlers.flow_enqueue_batch({ manifest_path: fixture.manifestPath });
    assert.equal(enqueued.ok, true, JSON.stringify(enqueued.errors));
    assert.equal(enqueued.batch_id, fixture.manifest.batch_id);
    assert.equal(enqueued.items.length, 1);
    const items = await queue.list('pending');
    assert.equal(items.length, 1);
    assert.equal(items[0].job.manifest_path, 'batch.manifest.json');
    const statusByBatch = await handlers.flow_batch_status({ batch_id: fixture.manifest.batch_id });
    assert.equal(statusByBatch.ok, true);
    assert.equal(statusByBatch.query.batch_id, fixture.manifest.batch_id);
    assert.equal(statusByBatch.jobs.length, 1);
    const byManifest = await handlers.flow_batch_status({ manifest_path: 'batch.manifest.json' });
    assert.equal(byManifest.count, 1);
    assert.equal(byManifest.jobs[0].job.batch_id, fixture.manifest.batch_id);
  } finally {
    await fs.rm(projectRoot, { recursive: true, force: true });
  }
});

test('bridge status remains explicit about candidate and pause semantics', async () => {
  const { projectRoot, handlers, fixture } = await buildHarness();
  try {
    const enqueued = await handlers.flow_enqueue_batch({ manifest_path: fixture.manifestPath });
    assert.equal(enqueued.ok, true);

    const status = await handlers.flow_bridge_status();
    assert.equal(status.provider, 'google_flow');
    assert.equal(status.candidate_semantics.candidate_state, 'pending');
    assert.equal(status.candidate?.job_id?.startsWith(`${fixture.manifest.batch_id}-`), true);

    const paused = await handlers.flow_pause_queue();
    assert.equal(paused.paused, true);

    const pausedStatus = await handlers.flow_bridge_status();
    assert.equal(pausedStatus.provider, 'google_flow');
    assert.equal(pausedStatus.candidate_semantics.candidate_state, 'paused');
    assert.equal(pausedStatus.candidate_semantics.has_candidate, true);
    await handlers.flow_resume_queue();
  } finally {
    await fs.rm(projectRoot, { recursive: true, force: true });
  }
});

test('diagnostic capture is safe to path and file-root constrained', async () => {
  const { handlers, projectRoot } = await buildHarness();
  try {
    await assert.rejects(
      () => handlers.flow_capture_diagnostic({ output_path: '../outside.json' }),
      /unsafe_path|escapes configured root/i,
    );

    const targetPath = path.join(projectRoot, 'diagnostics', 'snapshot.json');
    await fs.mkdir(path.dirname(targetPath), { recursive: true });
    const result = await handlers.flow_capture_diagnostic({ output_path: path.relative(projectRoot, targetPath) });
    assert.equal(result.wrote_file, true);
    assert.equal(path.basename(result.output_path), 'snapshot.json');
  } finally {
    await fs.rm(projectRoot, { recursive: true, force: true });
  }
});
