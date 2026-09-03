import path from 'node:path';
import fs from 'node:fs/promises';
import crypto from 'node:crypto';
import { ContractError, assertIdentifier } from './contracts.mjs';

export const RUNTIME_DIRECTORY_NAMES = Object.freeze([
  'queue/pending',
  'queue/active',
  'queue/completed',
  'queue/failed',
  'queue/cancelled',
  'queue/index',
  'events',
  'downloads',
  'diagnostics',
]);

function absolute(value) {
  return path.resolve(String(value));
}

/**
 * Lexically constrain a path to a configured root.  This is intentionally
 * synchronous so callers can validate request metadata before any filesystem
 * mutation.  Existing symlinks are checked by `realpathInside` when a file is
 * opened or imported by a later stage.
 */
export function resolveInside(root, candidate, label = 'path') {
  if (candidate === undefined || candidate === null || candidate === '') {
    throw new ContractError(`${label} is required`, 'unsafe_path');
  }
  const rootPath = absolute(root);
  const candidatePath = absolute(path.isAbsolute(String(candidate))
    ? String(candidate)
    : path.join(rootPath, String(candidate)));
  const relative = path.relative(rootPath, candidatePath);
  if (relative === '..' || relative.startsWith(`..${path.sep}`) || path.isAbsolute(relative)) {
    throw new ContractError(`${label} escapes configured root`, 'unsafe_path');
  }
  return candidatePath;
}

export const resolveSafePath = resolveInside;

export async function realpathInside(root, candidate, label = 'path') {
  const lexical = resolveInside(root, candidate, label);
  const rootReal = await fs.realpath(root).catch(() => absolute(root));
  // Resolve the nearest existing ancestor so a symlinked directory cannot
  // smuggle a future output path outside its configured root.
  let probe = lexical;
  const suffix = [];
  while (true) {
    try {
      await fs.lstat(probe);
      break;
    } catch (error) {
      if (error?.code !== 'ENOENT') throw error;
      const parent = path.dirname(probe);
      if (parent === probe) break;
      suffix.unshift(path.basename(probe));
      probe = parent;
    }
  }
  const candidateReal = path.join(await fs.realpath(probe).catch(() => probe), ...suffix);
  return resolveInside(rootReal, candidateReal, label);
}

export function createFlowPaths(options = {}) {
  const runtimeRoot = absolute(
    options.runtimeRoot
      ?? process.env.FLOW_RUNTIME_ROOT
      ?? path.join(process.cwd(), '.codex', 'flow-runtime'),
  );
  const downloadsRoot = absolute(options.downloadsRoot ?? path.join(runtimeRoot, 'downloads'));
  const projectRoot = absolute(options.projectRoot ?? process.cwd());
  const queueRoot = path.join(runtimeRoot, 'queue');
  const queue = Object.fromEntries(
    ['pending', 'active', 'completed', 'failed', 'cancelled', 'index']
      .map((name) => [name, path.join(queueRoot, name)]),
  );
  return Object.freeze({
    runtimeRoot,
    queueRoot,
    queue,
    eventsRoot: path.join(runtimeRoot, 'events'),
    downloadsRoot,
    diagnosticsRoot: path.join(runtimeRoot, 'diagnostics'),
    projectRoot,
  });
}

export async function ensureRuntimeLayout(paths) {
  const directories = [
    paths.runtimeRoot,
    paths.queueRoot,
    ...Object.values(paths.queue),
    paths.eventsRoot,
    paths.downloadsRoot,
    paths.diagnosticsRoot,
  ];
  await Promise.all(directories.map((directory) => fs.mkdir(directory, { recursive: true })));
  return paths;
}

export const ensureQueueLayout = ensureRuntimeLayout;

/**
 * Durable queue controls live inside the runtime root so pause/resume survives
 * native-host restarts without depending on process memory.
 */
export function queueControlPath(paths) {
  return resolveInside(paths.runtimeRoot, path.join('queue', 'control.json'), 'queue control path');
}

// Keep descriptive aliases for callers that refer to the persisted control as
// queue state or pause state. All aliases resolve to the same canonical file.
export const queueStatePath = queueControlPath;
export const pauseStatePath = queueControlPath;

export function jobFileName(jobId) {
  assertIdentifier(jobId, 'job_id');
  return `${jobId}.json`;
}

export function jobPath(paths, state, jobId) {
  if (!Object.prototype.hasOwnProperty.call(paths.queue, state)) {
    throw new ContractError(`unknown queue state: ${state}`);
  }
  return resolveInside(paths.queue[state], jobFileName(jobId), `${state} job path`);
}

export function idempotencyIndexPath(paths, idempotencyKey) {
  const safeKey = String(idempotencyKey);
  // A digest avoids putting caller-controlled text in a filename and preserves
  // uniqueness for arbitrarily long idempotency keys.
  const digest = crypto.createHash('sha256').update(safeKey, 'utf8').digest('hex');
  const name = `${digest}.json`;
  return resolveInside(paths.queue.index, name, 'idempotency index path');
}

export function eventFilePath(paths, sequence, type = 'event') {
  if (!Number.isSafeInteger(sequence) || sequence < 1) {
    throw new ContractError('event sequence must be a positive integer');
  }
  const safeType = String(type).replace(/[^a-z0-9._-]/gi, '_').slice(0, 80) || 'event';
  return resolveInside(paths.eventsRoot, `${String(sequence).padStart(12, '0')}-${safeType}.json`, 'event path');
}

export function assertJobPathRoots(paths, job) {
  const projectFields = ['output_path', 'output_root', 'project_path', 'artifact_path'];
  for (const field of projectFields) {
    if (job[field] !== undefined && job[field] !== null) resolveInside(paths.projectRoot, job[field], field);
  }
  const runtimeFields = ['diagnostic_path', 'event_path'];
  for (const field of runtimeFields) {
    if (job[field] !== undefined && job[field] !== null) resolveInside(paths.runtimeRoot, job[field], field);
  }
  const downloadFields = ['download_path', 'downloads_path'];
  for (const field of downloadFields) {
    if (job[field] !== undefined && job[field] !== null) resolveInside(paths.downloadsRoot, job[field], field);
  }
  return job;
}

export function toProjectRelative(paths, candidate, label = 'project path') {
  const resolved = resolveInside(paths.projectRoot, candidate, label);
  return path.relative(paths.projectRoot, resolved).split(path.sep).join('/');
}
