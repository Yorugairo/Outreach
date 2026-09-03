import fs from 'node:fs/promises';
import path from 'node:path';

import {
  ContractError,
  FLOW_ACTIONS,
  sha256,
} from '../shared/contracts.mjs';
import { realpathInside, toProjectRelative } from '../shared/paths.mjs';

const FLOW_PROVIDER = 'google_flow';
const BATCH_SCHEMA_VERSION = 'google_flow_provider_batch.v1';
const CAPABILITY_SCHEMA_VERSION = 'google_flow_capability_snapshot.v1';

function resolveProjectRoot(projectRoot) {
  return path.resolve(String(projectRoot || process.cwd()));
}

async function resolveManifestPath(projectRoot, candidate, label) {
  if (candidate === undefined || candidate === null || String(candidate).trim() === '') {
    throw new ContractError(`${label} is required`, 'missing_path');
  }
  return await realpathInside(projectRoot, candidate, label);
}

function toRelative(projectRoot, candidate, label) {
  return toProjectRelative({ projectRoot }, candidate, label);
}

function asText(value) {
  return typeof value === 'string' ? value : null;
}

function parseJson(text, pathLabel) {
  try {
    return JSON.parse(text);
  } catch (error) {
    throw new ContractError(`invalid JSON in ${pathLabel}`, 'invalid_json');
  }
}

async function readJsonAtPath(absolutePath, label) {
  try {
    return parseJson(await fs.readFile(absolutePath, 'utf8'), label);
  } catch (error) {
    if (error?.code === 'ENOENT') throw new ContractError(`${label} does not exist`, 'missing_file');
    throw error;
  }
}

function isObject(value) {
  return Boolean(value) && typeof value === 'object' && !Array.isArray(value);
}

function requireString(value, label, errors, allowNull = false) {
  if (value === undefined || value === null) {
    if (allowNull) return;
    errors.push(`${label} is required`);
    return;
  }
  if (typeof value !== 'string' || value.trim() === '') {
    errors.push(`${label} must be a non-empty string`);
    return;
  }
}

function requireObject(value, label, errors, allowNull = false) {
  if (value === undefined || value === null) {
    if (allowNull) return;
    errors.push(`${label} is required`);
    return;
  }
  if (!isObject(value)) {
    errors.push(`${label} must be an object`);
  }
}

function requireArray(value, label, errors, minLength = 0) {
  if (!Array.isArray(value)) {
    errors.push(`${label} must be an array`);
    return false;
  }
  if (value.length < minLength) {
    errors.push(`${label} must contain at least ${minLength} entries`);
    return false;
  }
  return true;
}

function requireObjectFields(value, required, label, errors) {
  for (const field of required) {
    if (value[field] === undefined) errors.push(`${label}.${field} is required`);
  }
}

async function validateArtifactBinding(value, projectRoot, label, errors, expectFile = false) {
  requireObject(value, `${label} binding`, errors);
  if (!isObject(value)) return;
  requireString(value.path, `${label}.path`, errors);
  requireString(value.sha256, `${label}.sha256`, errors);
  requireString(value.artifact_hash, `${label}.artifact_hash`, errors);
  if (value.sha256 && !/^[a-f0-9]{64}$/i.test(String(value.sha256))) {
    errors.push(`${label}.sha256 must be a 64-character hex string`);
  }
  if (value.artifact_hash && !/^[a-f0-9]{64}$/i.test(String(value.artifact_hash))) {
    errors.push(`${label}.artifact_hash must be a 64-character hex string`);
  }

  if (value.path) {
    const absolute = await resolveManifestPath(projectRoot, value.path, `${label}.path`);
    if (expectFile) {
      try {
        const stat = await fs.stat(absolute);
        if (!stat.isFile()) {
          errors.push(`${label}.path must resolve to a file`);
          return null;
        }
        const bytes = await fs.readFile(absolute);
        if (value.sha256 && sha256(bytes) !== String(value.sha256).toLowerCase()) {
          errors.push(`${label}.sha256 does not match local bytes`);
        }
        let artifact;
        try {
          artifact = parseJson(bytes.toString('utf8'), `${label}.path`);
        } catch (error) {
          errors.push(error.message);
          return null;
        }
        if (value.artifact_hash && artifact.artifact_hash !== value.artifact_hash) {
          errors.push(`${label}.artifact_hash does not match bound artifact`);
        }
        const artifactCore = { ...artifact };
        delete artifactCore.artifact_hash;
        if (artifact.artifact_hash && sha256(artifactCore) !== artifact.artifact_hash) {
          errors.push(`${label} bound artifact hash does not match its content`);
        }
        return artifact;
      } catch (error) {
        if (error?.code === 'ENOENT') {
          errors.push(`${label}.path does not exist`);
        } else {
          throw error;
        }
      }
    }
  }
  return null;
}

export async function readBatchManifest(manifestPath, { projectRoot }) {
  const normalizedProjectRoot = resolveProjectRoot(projectRoot);
  const absolutePath = await resolveManifestPath(normalizedProjectRoot, manifestPath, 'manifest_path');
  const payload = await readJsonAtPath(absolutePath, 'manifest_path');
  return { projectRoot: normalizedProjectRoot, manifestPath: absolutePath, manifest: payload };
}

export async function validateBatchManifest(manifest, projectRoot) {
  const errors = [];
  const normalizedRoot = resolveProjectRoot(projectRoot);
  if (!isObject(manifest)) {
    return { valid: false, errors: ['manifest must be a JSON object'], normalized: null };
  }

  requireString(manifest.schema_version, 'schema_version', errors);
  if (manifest.schema_version && manifest.schema_version !== BATCH_SCHEMA_VERSION) {
    errors.push(`schema_version must be ${BATCH_SCHEMA_VERSION}`);
  }

  requireObjectFields(manifest, [
    'batch_id',
    'channel_id',
    'episode_id',
    'action',
    'project_url',
    'capability_snapshot',
    'requested_settings',
    'items',
    'output_root',
    'budget_policy',
    'approval_policy',
    'fallback',
    'status',
    'review_state',
    'render_eligible',
    'artifact_hash',
  ], 'batch', errors);

  if (manifest.action && !FLOW_ACTIONS.includes(manifest.action)) {
    errors.push(`action must be one of ${FLOW_ACTIONS.join(', ')}`);
  }

  requireString(manifest.batch_id, 'batch_id', errors);
  requireString(manifest.channel_id, 'channel_id', errors);
  requireString(manifest.episode_id, 'episode_id', errors);
  requireString(manifest.project_url, 'project_url', errors);
  requireString(manifest.output_root, 'output_root', errors);
  requireString(manifest.artifact_hash, 'artifact_hash', errors);
  if (manifest.artifact_hash && !/^[a-f0-9]{64}$/i.test(manifest.artifact_hash)) {
    errors.push('artifact_hash must be a 64-character hex string');
  }

  if (manifest.render_eligible !== false) {
    errors.push('render_eligible must be false for this provider');
  }
  if (manifest.review_state !== 'quarantined') {
    errors.push('review_state must be quarantined');
  }
  if (!['planned', 'validated', 'queued', 'running', 'completed', 'failed', 'blocked'].includes(manifest.status)) {
    errors.push('status is not recognized');
  }

  const outputRoot = await resolveManifestPath(normalizedRoot, manifest.output_root, 'output_root');
  const capability = await validateArtifactBinding(
    manifest.capability_snapshot,
    normalizedRoot,
    'capability_snapshot',
    errors,
    true,
  );
  requireObject(manifest.requested_settings, 'requested_settings', errors);
  if (isObject(manifest.requested_settings)) {
    requireString(manifest.requested_settings.model, 'requested_settings.model', errors);
    requireString(manifest.requested_settings.mode, 'requested_settings.mode', errors);
    requireString(manifest.requested_settings.aspect_ratio, 'requested_settings.aspect_ratio', errors);
    if (!Number.isInteger(manifest.requested_settings.quantity) || manifest.requested_settings.quantity < 1) {
      errors.push('requested_settings.quantity must be a positive integer');
    }
    if (manifest.requested_settings.duration_seconds !== null
      && !Number.isInteger(manifest.requested_settings.duration_seconds)) {
      errors.push('requested_settings.duration_seconds must be an integer or null');
    }
  }

  requireObject(manifest.budget_policy, 'budget_policy', errors);
  if (isObject(manifest.budget_policy)) {
    if (!['zero_credit', 'paid'].includes(manifest.budget_policy.kind)) {
      errors.push('budget_policy.kind must be zero_credit or paid');
    }
    if (!Number.isInteger(manifest.budget_policy.expected_credits) || manifest.budget_policy.expected_credits < 0) {
      errors.push('budget_policy.expected_credits must be a non-negative integer');
    }
    if (!Number.isInteger(manifest.budget_policy.max_credits) || manifest.budget_policy.max_credits < 0) {
      errors.push('budget_policy.max_credits must be a non-negative integer');
    }
    if (manifest.budget_policy.kind === 'zero_credit') {
      if (manifest.budget_policy.expected_credits !== 0 || manifest.budget_policy.max_credits !== 0) {
        errors.push('zero-credit batches must have expected_credits=0 and max_credits=0');
      }
      requireString(manifest.budget_policy.standing_policy_id, 'budget_policy.standing_policy_id', errors);
    }
  }

  requireObject(manifest.approval_policy, 'approval_policy', errors);
  if (isObject(manifest.approval_policy)) {
    if (!['not_requested', 'standing_policy_approved', 'operator_approved'].includes(manifest.approval_policy.state)) {
      errors.push('approval_policy.state is not recognized');
    }
    if (manifest.approval_policy.approval_id !== null && !asText(manifest.approval_policy.approval_id)) {
      errors.push('approval_policy.approval_id must be a string or null');
    }
    if (manifest.approval_policy.expected_account_verified !== true && manifest.approval_policy.expected_account_verified !== false) {
      errors.push('approval_policy.expected_account_verified must be true/false');
    }
    if (manifest.budget_policy?.kind === 'zero_credit'
      && manifest.approval_policy.state !== 'standing_policy_approved') {
      errors.push('zero-credit batches require standing_policy_approved');
    }
    if (manifest.budget_policy?.kind === 'paid') {
      if (manifest.approval_policy.state !== 'operator_approved') {
        errors.push('paid batches require operator_approved');
      }
      requireString(manifest.approval_policy.approval_id, 'approval_policy.approval_id', errors);
      if (manifest.budget_policy.expected_credits > manifest.budget_policy.max_credits) {
        errors.push('paid expected_credits exceed max_credits');
      }
    }
  }

  if (capability) {
    const capabilityValidation = await validateCapabilitySnapshot(capability, normalizedRoot);
    errors.push(...capabilityValidation.errors.map((error) => `capability_snapshot: ${error}`));
    if (capability.project_url !== manifest.project_url) {
      errors.push('project_url does not match capability snapshot');
    }
    const expiresAt = Date.parse(capability.expires_at || '');
    if (!Number.isFinite(expiresAt) || expiresAt <= Date.now()) {
      errors.push('capability snapshot is expired or has invalid expires_at');
    }
    const exactOffering = Array.isArray(capability.offerings)
      ? capability.offerings.find((offering) => (
          offering.action === manifest.action
          && ['model', 'mode', 'aspect_ratio', 'duration_seconds', 'quantity']
            .every((field) => offering[field] === manifest.requested_settings?.[field])
        ))
      : null;
    if (!exactOffering) {
      errors.push('requested_settings do not match an exact capability offering');
    } else if (manifest.budget_policy?.kind === 'zero_credit' && exactOffering.credit_state !== 'zero') {
      errors.push('zero-credit batch capability does not display zero credit');
    } else if (manifest.budget_policy?.kind === 'paid') {
      const expected = Number(exactOffering.credits_per_generation) * manifest.items.length;
      if (!Number.isInteger(expected) || expected !== manifest.budget_policy.expected_credits) {
        errors.push('paid expected_credits do not match exact capability cost');
      }
    }
  }

  requireObject(manifest.fallback, 'fallback', errors);
  if (isObject(manifest.fallback)) {
    requireString(manifest.fallback.provider, 'fallback.provider', errors);
    requireString(manifest.fallback.reason, 'fallback.reason', errors);
  }

  if (!requireArray(manifest.items, 'items', errors, 1)) {
    return { valid: false, errors, normalized: null };
  }

  const itemIds = new Set();
  const itemKeys = new Set();
  for (let index = 0; index < manifest.items.length; index += 1) {
    const item = manifest.items[index];
    const label = `items[${index}]`;
    if (!isObject(item)) {
      errors.push(`${label} must be an object`);
      continue;
    }
    requireObjectFields(item, [
      'item_id',
      'ordinal',
      'semantic_binding',
      'prompt',
      'prompt_sha256',
      'references',
      'output_path',
      'idempotency_key',
    ], label, errors);

    if (item.item_id !== undefined && itemIds.has(item.item_id)) errors.push(`${label}.item_id is duplicated`);
    if (item.idempotency_key && itemKeys.has(item.idempotency_key)) errors.push(`${label}.idempotency_key is duplicated`);

    if (item.item_id) {
      if (!/^[a-z0-9-]+$/.test(String(item.item_id))) {
        errors.push(`${label}.item_id must match ^[a-z0-9-]+$`);
      }
      itemIds.add(item.item_id);
    }
    if (item.idempotency_key) {
      itemKeys.add(item.idempotency_key);
      if (!/^[a-f0-9]{64}$/i.test(String(item.idempotency_key))) {
        errors.push(`${label}.idempotency_key must be a 64-character hex string`);
      }
    }
    if (!Number.isInteger(item.ordinal)) errors.push(`${label}.ordinal must be an integer`);
    if (item.ordinal !== index) errors.push(`${label}.ordinal must preserve order`);

    requireObject(item.semantic_binding, `${label}.semantic_binding`, errors);
    requireString(item.prompt, `${label}.prompt`, errors);
    requireString(item.prompt_sha256, `${label}.prompt_sha256`, errors);
    if (item.prompt_sha256 && !/^[a-f0-9]{64}$/i.test(item.prompt_sha256)) {
      errors.push(`${label}.prompt_sha256 must be a 64-character hex string`);
    }
    if (typeof item.prompt === 'string' && item.prompt_sha256 && sha256(item.prompt) !== item.prompt_sha256) {
      errors.push(`${label}.prompt_sha256 does not match prompt`);
    }

    if (item.depends_on) {
      if (typeof item.depends_on !== 'string' || !/^[a-z0-9-]+$/.test(item.depends_on)) {
        errors.push(`${label}.depends_on must match ^[a-z0-9-]+$`);
      } else if (!itemIds.has(item.depends_on) || item.depends_on === item.item_id) {
        errors.push(`${label}.depends_on must reference an earlier item in the batch`);
      }
    }

    if (requireArray(item.references, `${label}.references`, errors)) {
      if (item.references.length > 3) {
        errors.push(`${label}.references exceeds maximum limit of 3 references`);
      }
      for (let referenceIndex = 0; referenceIndex < item.references.length; referenceIndex += 1) {
        const reference = item.references[referenceIndex];
        const referenceLabel = `${label}.references[${referenceIndex}]`;
        requireObject(reference, referenceLabel, errors);
        if (reference.from_job) {
          requireString(reference.from_job, `${referenceLabel}.from_job`, errors);
          if (reference.from_job && !itemIds.has(reference.from_job)) {
            errors.push(`${referenceLabel}.from_job must reference an earlier item in the batch`);
          }
        } else {
          requireString(reference.path, `${referenceLabel}.path`, errors);
          requireString(reference.sha256, `${referenceLabel}.sha256`, errors);
          if (reference.sha256 && !/^[a-f0-9]{64}$/i.test(reference.sha256)) {
            errors.push(`${referenceLabel}.sha256 must be a 64-character hex string`);
          }
          if (reference.path) {
            const absoluteReference = await resolveManifestPath(normalizedRoot, reference.path, `${referenceLabel}.path`);
            try {
              const stat = await fs.stat(absoluteReference);
              if (!stat.isFile()) errors.push(`${referenceLabel}.path must be a file`);
              if (stat.isFile()) {
                const bytes = await fs.readFile(absoluteReference);
                if (reference.sha256 && sha256(bytes) !== String(reference.sha256).toLowerCase()) {
                  errors.push(`${referenceLabel}.sha256 does not match local bytes`);
                }
              }
            } catch (error) {
              if (error?.code === 'ENOENT') errors.push(`${referenceLabel}.path does not exist`);
              else throw error;
            }
          }
        }
      }
    }

    if (item.output_path) {
      const absoluteOutputPath = await resolveManifestPath(normalizedRoot, item.output_path, `${label}.output_path`);
      if (path.relative(outputRoot, absoluteOutputPath).startsWith('..')) {
        errors.push(`${label}.output_path must be inside output_root`);
      }
    }
  }

  const manifestCore = { ...manifest };
  delete manifestCore.artifact_hash;
  if (manifest.artifact_hash && sha256(manifestCore) !== manifest.artifact_hash) {
    errors.push('artifact_hash does not match manifest content');
  }

  return {
    valid: errors.length === 0,
    errors,
    normalized: {
      ...manifest,
      output_root: toRelative(normalizedRoot, outputRoot, 'output_root'),
    },
  };
}

export async function validateCapabilitySnapshot(manifest, projectRoot) {
  const errors = [];
  const normalizedRoot = resolveProjectRoot(projectRoot);
  if (!isObject(manifest)) return { valid: false, errors: ['capability snapshot must be an object'], normalized: null };

  requireString(manifest.schema_version, 'schema_version', errors);
  if (manifest.schema_version && manifest.schema_version !== CAPABILITY_SCHEMA_VERSION) {
    errors.push(`schema_version must be ${CAPABILITY_SCHEMA_VERSION}`);
  }
  requireString(manifest.snapshot_id, 'snapshot_id', errors);
  requireString(manifest.project_url, 'project_url', errors);
  if (!/^(https:\/\/)?labs\.google\/fx\//.test(manifest.project_url || '')) {
    errors.push('project_url must be a Flow URL');
  }
  requireObject(manifest.account, 'account', errors);
  if (isObject(manifest.account)) {
    requireString(manifest.account.marker, 'account.marker', errors);
    if (manifest.account.verified !== true) errors.push('account.verified must be true');
  }
  requireArray(manifest.offerings, 'offerings', errors, 1);
  if (manifest.render_eligible !== false) errors.push('render_eligible must be false');
  if (manifest.review_state !== 'observed' && manifest.review_state !== 'operator_confirmed') {
    errors.push('review_state must be observed or operator_confirmed');
  }
  requireString(manifest.artifact_hash, 'artifact_hash', errors);
  if (manifest.artifact_hash && !/^[a-f0-9]{64}$/i.test(manifest.artifact_hash)) {
    errors.push('artifact_hash must be a 64-character hex string');
  }

  if (manifest.account && manifest.offerings && Array.isArray(manifest.offerings)) {
    for (let index = 0; index < manifest.offerings.length; index += 1) {
      const offering = manifest.offerings[index];
      const label = `offerings[${index}]`;
      requireObject(offering, label, errors);
      requireString(`${offering?.action}`, `${label}.action`, errors);
      requireString(offering?.model, `${label}.model`, errors);
      requireString(offering?.mode, `${label}.mode`, errors);
      requireString(offering?.aspect_ratio, `${label}.aspect_ratio`, errors);
      if (offering?.duration_seconds !== null && !Number.isInteger(offering.duration_seconds)) {
        errors.push(`${label}.duration_seconds must be an integer or null`);
      }
      if (!Number.isInteger(offering?.quantity) || offering.quantity < 1) {
        errors.push(`${label}.quantity must be a positive integer`);
      }
      requireString(offering?.displayed_credit_label, `${label}.displayed_credit_label`, errors);
      if (!['zero', 'positive', 'unknown'].includes(offering?.credit_state)) {
        errors.push(`${label}.credit_state must be zero, positive, or unknown`);
      }
      if (offering?.credit_state !== 'unknown' && !Number.isInteger(offering?.credits_per_generation)) {
        errors.push(`${label}.credits_per_generation must be an integer`);
      }
    }
  }

  if (manifest.output_binding) {
    await validateArtifactBinding(manifest.output_binding, normalizedRoot, 'output_binding', errors, true);
  }

  return { valid: errors.length === 0, errors, normalized: manifest };
}

export async function flowCaptureCapabilities(queue, { capability_path }, { projectRoot }) {
  if (typeof capability_path !== 'string' || capability_path.trim() === '') {
    throw new ContractError('capability_path is required for capture', 'missing_path');
  }
  const normalizedRoot = resolveProjectRoot(projectRoot);
  const absolutePath = await resolveManifestPath(normalizedRoot, capability_path, 'capability_path');
  const payload = await readJsonAtPath(absolutePath, 'capability_path');
  const validation = await validateCapabilitySnapshot(payload, normalizedRoot);
  if (!validation.valid) {
    return {
      provider: FLOW_PROVIDER,
      ok: false,
      errors: validation.errors,
      capability_path: toRelative(normalizedRoot, absolutePath, 'capability_path'),
    };
  }
  return {
    provider: FLOW_PROVIDER,
    ok: true,
    capability_path: toRelative(normalizedRoot, absolutePath, 'capability_path'),
    snapshot_id: validation.normalized.snapshot_id,
    project_url: validation.normalized.project_url,
    account: validation.normalized.account,
  };
}

export async function flowValidateBatch(queue, { manifest_path }, { projectRoot }) {
  if (typeof manifest_path !== 'string' || manifest_path.trim() === '') {
    throw new ContractError('manifest_path is required', 'missing_path');
  }
  const { manifest, manifestPath, projectRoot: normalizedRoot } = await readBatchManifest(manifest_path, { projectRoot });
  const validation = await validateBatchManifest(manifest, normalizedRoot);
  return {
    provider: FLOW_PROVIDER,
    ok: validation.valid,
    manifest_path: toRelative(normalizedRoot, manifestPath, 'manifest_path'),
    errors: validation.errors,
    item_count: validation.normalized?.items?.length || 0,
  };
}

export async function flowPreflightBatch(queue, { manifest_path }, { projectRoot }) {
  const validation = await flowValidateBatch(queue, { manifest_path }, { projectRoot });
  if (!validation.ok) return validation;
  const status = await queue.status();
  const running = !status.paused;
  return {
    ...validation,
    preflight: {
      can_enqueue: running,
      queued: status.total,
      paused: status.paused,
      runtime_root: status.runtime_root,
    },
    ok: validation.ok && running,
    errors: validation.ok && !running ? ['queue is paused'] : validation.errors,
  };
}

function normalizeJob(manifest, item, jobIdFallback, manifestPath) {
  return {
    job_id: `${manifest.batch_id}-${item.item_id || jobIdFallback}`,
    idempotency_key: item.idempotency_key,
    depends_on: item.depends_on ? `${manifest.batch_id}-${item.depends_on}` : null,
    batch_id: manifest.batch_id,
    channel_id: manifest.channel_id,
    episode_id: manifest.episode_id,
    action: manifest.action,
    project_url: manifest.project_url,
    item_id: item.item_id,
    ordinal: item.ordinal,
    semantic_binding: item.semantic_binding,
    prompt: item.prompt,
    prompt_sha256: item.prompt_sha256,
    references: item.references || [],
    output_root: manifest.output_root,
    output_path: item.output_path,
    requested_settings: manifest.requested_settings,
    budget_policy: manifest.budget_policy,
    approval_policy: manifest.approval_policy,
    fallback: manifest.fallback,
    provider: FLOW_PROVIDER,
    manifest_path: manifestPath ?? null,
  };
}

export async function flowEnqueueBatch(queue, { manifest_path }, { projectRoot }) {
  if (typeof manifest_path !== 'string' || manifest_path.trim() === '') {
    throw new ContractError('manifest_path is required', 'missing_path');
  }
  const { manifest, manifestPath, projectRoot: normalizedRoot } = await readBatchManifest(manifest_path, { projectRoot });
  const normalizedManifestPath = toRelative(normalizedRoot, manifestPath, 'manifest_path');
  const validation = await validateBatchManifest(manifest, normalizedRoot);
  if (!validation.valid) {
    return {
      provider: FLOW_PROVIDER,
      ok: false,
      errors: validation.errors,
      manifest_path: toRelative(normalizedRoot, manifestPath, 'manifest_path'),
      items: [],
    };
  }

  const preflight = await flowPreflightBatch(queue, { manifest_path }, { projectRoot });
  if (!preflight.preflight.can_enqueue) {
    return {
      provider: FLOW_PROVIDER,
      ok: false,
      errors: preflight.errors,
      manifest_path: toRelative(normalizedRoot, manifestPath, 'manifest_path'),
      items: [],
    };
  }

  const results = [];
  for (const item of validation.normalized.items || []) {
    const job = normalizeJob(validation.normalized, item, item.item_id, normalizedManifestPath);
    const enqueued = await queue.enqueue(job);
    results.push({
      item_id: item.item_id,
      job_id: job.job_id,
      created: enqueued.created,
      duplicate: enqueued.duplicate,
      state: enqueued.state,
    });
  }

  return {
    provider: FLOW_PROVIDER,
    ok: true,
      manifest_path: normalizedManifestPath,
      batch_id: validation.normalized.batch_id,
      items: results,
    };
}

export async function flowBatchStatus(queue, { job_id, batch_id, manifest_path } = {}, { projectRoot }) {
  if (job_id) {
    const found = await queue.get(String(job_id));
    return {
      provider: FLOW_PROVIDER,
      ok: Boolean(found),
      query: { job_id },
      job: found || null,
    };
  }

  if (batch_id) {
    const allJobs = await queue.list();
    const jobs = allJobs.filter((entry) => entry.job?.batch_id === String(batch_id));
    return {
      provider: FLOW_PROVIDER,
      ok: true,
      query: { batch_id: String(batch_id) },
      count: jobs.length,
      jobs,
    };
  }

  if (manifest_path) {
    const normalizedRoot = resolveProjectRoot(projectRoot);
    const normalizedManifestPath = toRelative(
      normalizedRoot,
      await resolveManifestPath(normalizedRoot, manifest_path, 'manifest_path'),
      'manifest_path',
    );
    const allJobs = await queue.list();
    const jobs = allJobs.filter((entry) => entry.job?.manifest_path === normalizedManifestPath);
    return {
      provider: FLOW_PROVIDER,
      ok: true,
      query: { manifest_path: normalizedManifestPath },
      count: jobs.length,
      jobs,
    };
  }

  const status = await queue.status();
  return {
    provider: FLOW_PROVIDER,
    ok: true,
    query: { all: true },
    status,
  };
}

export async function flowPauseQueue(queue) {
  const result = await queue.pause('mcp_pause');
  return {
    provider: FLOW_PROVIDER,
    paused: true,
    queue: result,
  };
}

export async function flowResumeQueue(queue) {
  const result = await queue.resume('mcp_resume');
  return {
    provider: FLOW_PROVIDER,
    paused: false,
    queue: result,
  };
}

export async function flowRetryItem(queue, { job_id }) {
  if (!job_id) throw new ContractError('job_id is required', 'missing_job_id');
  const result = await queue.retry(String(job_id));
  return {
    provider: FLOW_PROVIDER,
    ok: true,
    job: result,
  };
}

export async function flowCancelJob(queue, { job_id, reason }) {
  if (!job_id) throw new ContractError('job_id is required', 'missing_job_id');
  const result = await queue.cancel(String(job_id), reason || 'operator_cancelled');
  return {
    provider: FLOW_PROVIDER,
    ok: true,
    job: result,
  };
}

export async function flowCaptureDiagnostic(queue, { output_path }, { projectRoot }) {
  const status = await queue.status();
  const activeJobs = await queue.list('active');
  const pendingJobs = await queue.list('pending');
  const candidate = activeJobs[0]?.job ? activeJobs[0].job : pendingJobs[0]?.job || null;
  const payload = {
    provider: FLOW_PROVIDER,
    captured_at: new Date().toISOString(),
    queue_status: {
      paused: status.paused,
      counts: status.counts,
      total: status.total,
    },
    candidate_state: activeJobs[0]?.job ? 'active' : pendingJobs[0]?.job ? 'pending' : 'idle',
    candidate_job: candidate ? {
      job_id: candidate.job_id,
      batch_id: candidate.batch_id,
      item_id: candidate.item_id || null,
      action: candidate.action || null,
      output_path: candidate.output_path || null,
      status: candidate.status || null,
      idempotency_key: candidate.idempotency_key || null,
    } : null,
    runtime_root: status.runtime_root,
  };

  if (output_path) {
    const normalizedRoot = resolveProjectRoot(projectRoot);
    const absoluteOutput = await resolveManifestPath(normalizedRoot, output_path, 'output_path');
    await fs.writeFile(absoluteOutput, `${JSON.stringify(payload, null, 2)}\n`, 'utf8');
    return {
      ...payload,
      output_path: toRelative(normalizedRoot, absoluteOutput, 'output_path'),
      wrote_file: true,
    };
  }

  return {
    ...payload,
    wrote_file: false,
  };
}

export async function flowBridgeStatus(queue) {
  const status = await queue.status();
  const activeJobs = await queue.list('active');
  const pendingJobs = await queue.list('pending');
  const active = activeJobs[0] || null;
  const candidate = pendingJobs[0] || null;
  return {
    provider: FLOW_PROVIDER,
    runtime_root: status.runtime_root,
    paused: status.paused,
    candidate: candidate
      ? {
          job_id: candidate.job.job_id,
          batch_id: candidate.job.batch_id,
          item_id: candidate.job.item_id,
          action: candidate.job.action,
          state: candidate.state,
        }
      : null,
    active: active
      ? {
          job_id: active.job.job_id,
          batch_id: active.job.batch_id,
          item_id: active.job.item_id,
          action: active.job.action,
          attempt: active.job.attempt,
          state: active.state,
        }
      : null,
    candidate_semantics: {
      has_candidate: Boolean(active || candidate),
      candidate_state: status.paused ? 'paused' : (active ? 'active' : candidate ? 'pending' : 'none'),
      queue_paused: status.paused,
    },
    counts: status.counts,
    event_count: status.event_count,
  };
}

export const MCP_TOOL_DEFINITIONS = [
  {
    name: 'flow_bridge_status',
    description: 'Read bridge queue status including active/candidate/paused state.',
    inputSchema: { type: 'object', properties: {}, additionalProperties: false },
  },
  {
    name: 'flow_capture_capabilities',
    description: 'Capture and validate a Google Flow capability snapshot file.',
    inputSchema: {
      type: 'object',
      properties: {
        capability_path: {
          type: 'string',
          description: 'Absolute or project-relative path to the capability snapshot JSON.',
        },
      },
      required: ['capability_path'],
      additionalProperties: false,
    },
  },
  {
    name: 'flow_validate_batch',
    description: 'Validate a Google Flow batch manifest without queue mutation.',
    inputSchema: {
      type: 'object',
      properties: {
        manifest_path: {
          type: 'string',
          description: 'Absolute or project-relative path to a validated batch manifest.',
        },
      },
      required: ['manifest_path'],
      additionalProperties: false,
    },
  },
  {
    name: 'flow_preflight_batch',
    description: 'Check batch manifest, queue state, and enqueue readiness.',
    inputSchema: {
      type: 'object',
      properties: {
        manifest_path: {
          type: 'string',
        },
      },
      required: ['manifest_path'],
      additionalProperties: false,
    },
  },
  {
    name: 'flow_enqueue_batch',
    description: 'Enqueue a validated batch manifest to the durable queue.',
    inputSchema: {
      type: 'object',
      properties: {
        manifest_path: {
          type: 'string',
          description: 'Absolute or project-relative path to the validated batch manifest.',
        },
      },
      required: ['manifest_path'],
      additionalProperties: false,
    },
  },
  {
    name: 'flow_batch_status',
    description: 'Inspect one queued job, a batch, or all queue jobs.',
    inputSchema: {
      type: 'object',
      properties: {
        job_id: { type: 'string' },
        batch_id: { type: 'string' },
        manifest_path: { type: 'string' },
      },
      additionalProperties: false,
    },
  },
  {
    name: 'flow_pause_queue',
    description: 'Pause the durable queue.',
    inputSchema: { type: 'object', properties: {}, additionalProperties: false },
  },
  {
    name: 'flow_resume_queue',
    description: 'Resume the durable queue.',
    inputSchema: { type: 'object', properties: {}, additionalProperties: false },
  },
  {
    name: 'flow_retry_item',
    description: 'Retry a failed or cancelled queue item by job id.',
    inputSchema: {
      type: 'object',
      properties: { job_id: { type: 'string' } },
      required: ['job_id'],
      additionalProperties: false,
    },
  },
  {
    name: 'flow_cancel_job',
    description: 'Cancel a pending or active queue job by job id.',
    inputSchema: {
      type: 'object',
      properties: {
        job_id: { type: 'string' },
        reason: { type: 'string' },
      },
      required: ['job_id'],
      additionalProperties: false,
    },
  },
  {
    name: 'flow_capture_diagnostic',
    description: 'Capture a redacted MCP-facing diagnostic snapshot.',
    inputSchema: {
      type: 'object',
      properties: { output_path: { type: 'string' } },
      additionalProperties: false,
    },
  },
];

export function makeToolHandlers({ queue, projectRoot }) {
  return {
    flow_bridge_status: (args = {}) => flowBridgeStatus(queue, args, { projectRoot }),
    flow_capture_capabilities: (args = {}) => flowCaptureCapabilities(queue, args, { projectRoot }),
    flow_validate_batch: (args = {}) => flowValidateBatch(queue, args, { projectRoot }),
    flow_preflight_batch: (args = {}) => flowPreflightBatch(queue, args, { projectRoot }),
    flow_enqueue_batch: (args = {}) => flowEnqueueBatch(queue, args, { projectRoot }),
    flow_batch_status: (args = {}) => flowBatchStatus(queue, args, { projectRoot }),
    flow_pause_queue: (args = {}) => flowPauseQueue(queue, args),
    flow_resume_queue: (args = {}) => flowResumeQueue(queue, args),
    flow_retry_item: (args = {}) => flowRetryItem(queue, args),
    flow_cancel_job: (args = {}) => flowCancelJob(queue, args),
    flow_capture_diagnostic: (args = {}) => flowCaptureDiagnostic(queue, args, { projectRoot }),
  };
}
