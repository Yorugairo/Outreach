import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import {
  ContractError,
  assertMetadataOnly,
  isoNow,
  normalizeJob,
  sha256,
} from './contracts.mjs';
import {
  assertJobPathRoots,
  createFlowPaths,
  ensureRuntimeLayout,
  eventFilePath,
  idempotencyIndexPath,
  jobFileName,
  jobPath,
  queueControlPath,
  realpathInside,
} from './paths.mjs';

const JSON_ENCODING = 'utf8';

async function readJson(file) {
  const text = await fs.readFile(file, JSON_ENCODING);
  return JSON.parse(text);
}

/** Write JSON through a sibling temporary file, then atomically rename it. */
export async function atomicWriteJson(file, value) {
  assertMetadataOnly(value, '$json');
  await fs.mkdir(path.dirname(file), { recursive: true });
  const temporary = `${file}.${process.pid}.${crypto.randomBytes(8).toString('hex')}.tmp`;
  const body = `${JSON.stringify(value, null, 2)}\n`;
  try {
    await fs.writeFile(temporary, body, { encoding: JSON_ENCODING, flag: 'wx' });
    try {
      await fs.rename(temporary, file);
    } catch (error) {
      // POSIX rename replaces an existing file. Windows does not, so retain
      // the same temp+rename contract with a narrow replacement fallback.
      if (error?.code !== 'EEXIST' && error?.code !== 'EPERM') throw error;
      await fs.rm(file, { force: true });
      await fs.rename(temporary, file);
    }
  } finally {
    await fs.rm(temporary, { force: true }).catch(() => {});
  }
  return file;
}

async function listJsonFiles(directory) {
  const entries = await fs.readdir(directory, { withFileTypes: true }).catch((error) => {
    if (error?.code === 'ENOENT') return [];
    throw error;
  });
  return entries
    .filter((entry) => entry.isFile() && entry.name.endsWith('.json'))
    .map((entry) => entry.name)
    .sort((left, right) => left.localeCompare(right));
}

async function moveAtomic(source, destination) {
  await fs.mkdir(path.dirname(destination), { recursive: true });
  await fs.rename(source, destination);
  return destination;
}

export class DurableFlowQueue {
  constructor(options = {}) {
    this.paths = options.paths ?? createFlowPaths(options);
    this.clock = options.clock ?? (() => new Date());
    this.autoRecover = options.autoRecover !== false;
    this._ready = null;
    this._autoRecoveryStarted = false;
    this._controlTail = Promise.resolve();
  }

  async _ensureReady() {
    if (!this._ready) {
      this._ready = ensureRuntimeLayout(this.paths);
    }
    await this._ready;
    if (this.autoRecover && !this._autoRecoveryStarted) {
      this._autoRecoveryStarted = true;
      await this.recoverActive({ skipReady: true });
    }
  }

  /** Serialize pause/resume/claim decisions within one native-host process. */
  async _withControlLock(operation) {
    const previous = this._controlTail;
    let release;
    this._controlTail = new Promise((resolve) => { release = resolve; });
    await previous;
    try {
      return await operation();
    } finally {
      release();
    }
  }

  async _nextEventSequence() {
    const names = await fs.readdir(this.paths.eventsRoot, { withFileTypes: true }).catch((error) => {
      if (error?.code === 'ENOENT') return [];
      throw error;
    });
    let max = 0;
    for (const entry of names) {
      const match = /^(\d+)-/.exec(entry.name);
      if (match) max = Math.max(max, Number(match[1]));
    }
    return max + 1;
  }

  /**
   * Every transition creates a new event file. Existing event files are never
   * opened for update or deleted, which makes the evidence stream append-only.
   */
  async appendEvent(type, job, details = {}) {
    await this._ensureReady();
    assertMetadataOnly(details, '$event.details');
    const base = {
      protocol_version: 'flow-queue.v1',
      type: String(type),
      job_id: job?.job_id ?? null,
      idempotency_key: job?.idempotency_key ?? null,
      at: isoNow(this.clock),
      ...details,
    };
    assertMetadataOnly(base, '$event');
    let sequence = await this._nextEventSequence();
    for (;;) {
      const target = eventFilePath(this.paths, sequence, type);
      try {
        const handle = await fs.open(target, 'wx');
        try {
          await handle.writeFile(`${JSON.stringify({ sequence, ...base })}\n`, JSON_ENCODING);
        } finally {
          await handle.close();
        }
        return { sequence, path: target, event: { sequence, ...base } };
      } catch (error) {
        if (error?.code !== 'EEXIST') throw error;
        sequence += 1;
      }
    }
  }

  async _findByJobId(jobId) {
    const name = jobFileName(jobId);
    for (const state of ['pending', 'active', 'completed', 'failed', 'cancelled']) {
      const candidate = jobPath(this.paths, state, jobId);
      try {
        return { state, path: candidate, job: await readJson(candidate) };
      } catch (error) {
        if (error?.code !== 'ENOENT') throw error;
      }
    }
    return null;
  }

  async _findByIdempotencyKey(idempotencyKey) {
    const indexPath = idempotencyIndexPath(this.paths, idempotencyKey);
    let index;
    try {
      index = await readJson(indexPath);
    } catch (error) {
      if (error?.code !== 'ENOENT') throw error;
    }
    if (index?.job_id) {
      const found = await this._findByJobId(index.job_id);
      if (found) return found;
    }
    // Index files are durable evidence, but a manually recovered old spool may
    // predate the index. A bounded scan keeps restart recovery backwards-safe.
    for (const state of ['pending', 'active', 'completed', 'failed', 'cancelled']) {
      const directory = this.paths.queue[state];
      for (const name of await listJsonFiles(directory)) {
        const candidate = path.join(directory, name);
        const job = await readJson(candidate);
        if (job.idempotency_key === idempotencyKey) return { state, path: candidate, job };
      }
    }
    return null;
  }

  async _assertJobRoots(job) {
    assertJobPathRoots(this.paths, job);
    for (const field of ['output_path', 'output_root', 'project_path', 'artifact_path']) {
      if (job[field] !== undefined && job[field] !== null) {
        await realpathInside(this.paths.projectRoot, job[field], field);
      }
    }
    for (const field of ['diagnostic_path', 'event_path']) {
      if (job[field] !== undefined && job[field] !== null) {
        await realpathInside(this.paths.runtimeRoot, job[field], field);
      }
    }
    for (const field of ['download_path', 'downloads_path']) {
      if (job[field] !== undefined && job[field] !== null) {
        await realpathInside(this.paths.downloadsRoot, job[field], field);
      }
    }
    return job;
  }

  /**
   * Read the durable queue control. A missing file is the initial running
   * state; malformed control metadata fails closed so claims cannot proceed
   * while an operator's pause decision is ambiguous.
   */
  async _readQueueControl() {
    const controlPath = queueControlPath(this.paths);
    try {
      const control = await readJson(controlPath);
      if (!control || typeof control !== 'object' || Array.isArray(control) || typeof control.paused !== 'boolean') {
        return { paused: true, state_error: 'invalid_queue_control' };
      }
      return control;
    } catch (error) {
      if (error?.code === 'ENOENT') return { paused: false };
      if (error instanceof SyntaxError) return { paused: true, state_error: 'invalid_queue_control' };
      throw error;
    }
  }

  async _writeQueueControl(paused, reason = null) {
    const state = {
      protocol_version: 'flow-queue.v1',
      paused: Boolean(paused),
      updated_at: isoNow(this.clock),
    };
    if (reason !== null && reason !== undefined) state.reason = String(reason);
    await atomicWriteJson(queueControlPath(this.paths), state);
    return state;
  }

  async pause(reason = 'operator_requested') {
    return this._withControlLock(async () => {
      await this._ensureReady();
      const current = await this._readQueueControl();
      if (current.paused && !current.state_error) return this.status();
      await this._writeQueueControl(true, reason);
      await this.appendEvent('queue_paused', null, { paused: true, reason: String(reason) });
      return this.status();
    });
  }

  async resume(reason = 'operator_requested') {
    return this._withControlLock(async () => {
      await this._ensureReady();
      const current = await this._readQueueControl();
      if (!current.paused && !current.state_error) return this.status();
      await this._writeQueueControl(false, reason);
      await this.appendEvent('queue_resumed', null, { paused: false, reason: String(reason) });
      return this.status();
    });
  }

  // Explicit aliases make the queue API read naturally beside native methods.
  async pauseQueue(reason) {
    return this.pause(reason);
  }

  async resumeQueue(reason) {
    return this.resume(reason);
  }

  async enqueue(input) {
    await this._ensureReady();
    const job = normalizeJob(input, { clock: this.clock });
    job.status = 'pending';
    job.updated_at = isoNow(this.clock);
    await this._assertJobRoots(job);

    const sameId = await this._findByJobId(job.job_id);
    if (sameId && sameId.job.idempotency_key !== job.idempotency_key) {
      throw new ContractError(`job_id already belongs to another idempotency key: ${job.job_id}`, 'job_id_conflict');
    }
    if (sameId) {
      return { created: false, duplicate: true, state: sameId.state, job: sameId.job };
    }

    const existing = await this._findByIdempotencyKey(job.idempotency_key);
    if (existing) {
      return { created: false, duplicate: true, state: existing.state, job: existing.job };
    }

    const indexPath = idempotencyIndexPath(this.paths, job.idempotency_key);
    const index = {
      protocol_version: 'flow-queue.v1',
      idempotency_key: job.idempotency_key,
      job_id: job.job_id,
      created_at: job.created_at,
    };
    try {
      await fs.writeFile(indexPath, `${JSON.stringify(index)}\n`, { encoding: JSON_ENCODING, flag: 'wx' });
    } catch (error) {
      if (error?.code !== 'EEXIST') throw error;
      // The winning writer may be between its index and queue-file writes.
      for (let attempt = 0; attempt < 20; attempt += 1) {
        const winner = await this._findByIdempotencyKey(job.idempotency_key);
        if (winner) return { created: false, duplicate: true, state: winner.state, job: winner.job };
        await new Promise((resolve) => setTimeout(resolve, 5));
      }
      throw new ContractError('idempotency index exists without a recoverable job', 'queue_corrupt');
    }

    const destination = jobPath(this.paths, 'pending', job.job_id);
    try {
      await atomicWriteJson(destination, job);
    } catch (error) {
      await fs.rm(indexPath, { force: true }).catch(() => {});
      throw error;
    }
    await this.appendEvent('enqueued', job);
    return { created: true, duplicate: false, state: 'pending', job };
  }

  async claimNext() {
    return this._withControlLock(async () => {
      await this._ensureReady();
      if ((await this._readQueueControl()).paused) return null;
      for (const name of await listJsonFiles(this.paths.queue.pending)) {
        // Re-check before each atomic claim so a pause requested while scanning
        // cannot allow a later pending item to start.
        if ((await this._readQueueControl()).paused) return null;
        const source = path.join(this.paths.queue.pending, name);

        let candidate = null;
        try {
          candidate = await readJson(source);
        } catch {
          continue;
        }

        if (candidate.depends_on) {
          const dep = await this._findByJobId(candidate.depends_on);
          if (!dep || dep.state !== 'completed') {
            // Prerequisite job has not reached completed status yet; skip for now
            continue;
          }
          // Prerequisite job is completed; hydrate dynamic references
          const depOutput = dep.job.result?.outputs?.[0]?.import?.output_path || dep.job.output_path;
          const depSha = dep.job.result?.outputs?.[0]?.import?.sha256 || dep.job.result?.artifact_hash;
          if (depOutput && Array.isArray(candidate.references)) {
            for (const ref of candidate.references) {
              if (ref.from_job && (ref.from_job === candidate.depends_on || candidate.depends_on.endsWith(`-${ref.from_job}`))) {
                ref.path = depOutput;
                ref.sha256 = depSha || ref.sha256;
                ref.asset_id = ref.asset_id || `ref-${dep.job.item_id || 'prev'}`;
              }
            }
          }
        }

        const destination = path.join(this.paths.queue.active, name);
        try {
          await moveAtomic(source, destination);
        } catch (error) {
          if (error?.code === 'ENOENT' || error?.code === 'EEXIST') continue;
          throw error;
        }
        // A pause may have landed between the check and rename. Roll the claim
        // back before touching attempt/status so paused queues do no work.
        if ((await this._readQueueControl()).paused) {
          await moveAtomic(destination, source).catch((error) => {
            if (error?.code !== 'ENOENT' && error?.code !== 'EEXIST') throw error;
          });
          return null;
        }
        let job = await readJson(destination);
        job = {
          ...job,
          ...candidate,
          references: candidate.references,
          status: 'active',
          attempt: (Number.isInteger(job.attempt) ? job.attempt : 0) + 1,
          started_at: job.started_at ?? isoNow(this.clock),
          updated_at: isoNow(this.clock),
        };
        await this._assertJobRoots(job);
        await atomicWriteJson(destination, job);
        await this.appendEvent('claimed', job, { attempt: job.attempt });
        return job;
      }
      return null;
    });
  }

  /**
   * Requeue only terminal failed/cancelled jobs. The existing job id,
   * idempotency key, and attempt count remain unchanged; claimNext owns the
   * next attempt increment. Completed jobs are never replayed.
   */
  async retry(jobId) {
    await this._ensureReady();
    const found = await this._findByJobId(jobId);
    if (!found) throw new ContractError(`job not found: ${jobId}`, 'job_not_found');
    if (!['failed', 'cancelled'].includes(found.state)) {
      throw new ContractError(
        `job ${jobId} is ${found.state}, only failed or cancelled jobs can be retried`,
        'invalid_transition',
      );
    }

    const job = { ...found.job };
    for (const field of [
      'started_at',
      'completed_at',
      'failed_at',
      'cancellation_reason',
      'result',
      'error',
      'recovered_at',
    ]) delete job[field];
    job.status = 'pending';
    job.updated_at = isoNow(this.clock);
    await this._assertJobRoots(job);

    const destination = jobPath(this.paths, 'pending', jobId);
    await atomicWriteJson(found.path, job);
    await moveAtomic(found.path, destination);
    await this.appendEvent('retry', job, {
      previous_state: found.state,
      previous_status: found.state,
      previous_attempt: Number.isInteger(found.job.attempt) ? found.job.attempt : 0,
      attempt: Number.isInteger(job.attempt) ? job.attempt : 0,
    });
    return job;
  }

  async recoverActive(options = {}) {
    if (!options.skipReady) await this._ensureReady();
    const recovered = [];
    for (const name of await listJsonFiles(this.paths.queue.active)) {
      const source = path.join(this.paths.queue.active, name);
      const previous = await readJson(source);
      // A terminal status may have been durably written immediately before a
      // crash interrupted the directory move. Complete that move instead of
      // replaying work that already has a result.
      const terminalState = ['completed', 'failed', 'cancelled'].includes(previous.status)
        ? previous.status
        : null;
      const destination = path.join(this.paths.queue[terminalState ?? 'pending'], name);
      try {
        await moveAtomic(source, destination);
      } catch (error) {
        if (error?.code === 'ENOENT') continue;
        if (error?.code === 'EEXIST') {
          // Keep the older pending copy as the deterministic winner and record
          // the conflict; no work is silently duplicated.
          await this.appendEvent('recovery_conflict', previous);
          continue;
        }
        throw error;
      }
      if (terminalState) {
        await this.appendEvent('recovered_terminal', previous, { state: terminalState });
        recovered.push(previous);
        continue;
      }
      const job = {
        ...previous,
        status: 'pending',
        recovered_at: isoNow(this.clock),
        updated_at: isoNow(this.clock),
      };
      await atomicWriteJson(destination, job);
      await this.appendEvent('recovered', job, { previous_status: 'active' });
      recovered.push(job);
    }
    return recovered;
  }

  async _transition(jobId, targetState, details = {}) {
    await this._ensureReady();
    const found = await this._findByJobId(jobId);
    if (!found) throw new ContractError(`job not found: ${jobId}`, 'job_not_found');
    if (found.state !== 'active') {
      if (found.state === targetState) return found.job;
      throw new ContractError(`job ${jobId} is ${found.state}, expected active`, 'invalid_transition');
    }
    assertMetadataOnly(details, '$transition.details');
    const job = {
      ...found.job,
      ...details,
      status: targetState,
      updated_at: isoNow(this.clock),
    };
    await this._assertJobRoots(job);
    await atomicWriteJson(found.path, job);
    const destination = jobPath(this.paths, targetState, jobId);
    await moveAtomic(found.path, destination);
    await this.appendEvent(targetState, job);
    return job;
  }

  async complete(jobId, result = {}) {
    assertMetadataOnly(result, '$result');
    return this._transition(jobId, 'completed', { result, completed_at: isoNow(this.clock) });
  }

  async fail(jobId, error = {}) {
    assertMetadataOnly(error, '$error');
    return this._transition(jobId, 'failed', { error, failed_at: isoNow(this.clock) });
  }

  async cancel(jobId, reason = 'operator_cancelled') {
    return this._transition(jobId, 'cancelled', { cancellation_reason: String(reason) });
  }

  async get(jobId) {
    await this._ensureReady();
    return this._findByJobId(jobId);
  }

  async list(state = null) {
    await this._ensureReady();
    const states = state ? [state] : ['pending', 'active', 'completed', 'failed', 'cancelled'];
    const jobs = [];
    for (const current of states) {
      if (!Object.prototype.hasOwnProperty.call(this.paths.queue, current)) {
        throw new ContractError(`unknown queue state: ${current}`);
      }
      for (const name of await listJsonFiles(this.paths.queue[current])) {
        jobs.push({ state: current, path: path.join(this.paths.queue[current], name), job: await readJson(path.join(this.paths.queue[current], name)) });
      }
    }
    return jobs.sort((left, right) => `${left.state}/${left.job.job_id}`.localeCompare(`${right.state}/${right.job.job_id}`));
  }

  async status() {
    await this._ensureReady();
    const control = await this._readQueueControl();
    const entries = await this.list();
    const counts = Object.fromEntries(['pending', 'active', 'completed', 'failed', 'cancelled'].map((state) => [state, 0]));
    for (const entry of entries) counts[entry.state] += 1;
    return {
      protocol_version: 'flow-queue.v1',
      runtime_root: this.paths.runtimeRoot,
      paused: control.paused === true,
      counts,
      total: entries.length,
      event_count: (await fs.readdir(this.paths.eventsRoot)).filter((name) => name.endsWith('.json')).length,
    };
  }
}

export function createQueue(options = {}) {
  return new DurableFlowQueue(options);
}

export const FlowQueue = DurableFlowQueue;
export const FileQueue = DurableFlowQueue;
export const createFlowQueue = createQueue;

export async function enqueueJob(queue, job) {
  return queue.enqueue(job);
}

export async function claimNextJob(queue) {
  return queue.claimNext();
}

export async function completeJob(queue, jobId, result) {
  return queue.complete(jobId, result);
}

export async function recoverActiveJobs(queue) {
  return queue.recoverActive();
}

export async function pauseQueue(queue, reason) {
  return queue.pause(reason);
}

export async function resumeQueue(queue, reason) {
  return queue.resume(reason);
}

export async function retryJob(queue, jobId) {
  return queue.retry(jobId);
}

export { readJson };
