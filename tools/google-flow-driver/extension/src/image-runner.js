import {
  createMediaObserver,
  mediaIdentity,
  selectFreshMedia,
  snapshotMedia,
} from './media-observer.js';
import { downloadMedia } from './downloads.js';

export const FLOW_IMAGE_RUNNER_VERSION = 'flow-image-runner.v1';

export class ImageRunnerError extends Error {
  constructor(code, message = code, details = {}) {
    super(message);
    this.name = 'ImageRunnerError';
    this.code = code;
    this.details = details;
  }
}

function value(value) {
  return value === undefined || value === null || value === '' ? null : String(value);
}

function deepFreeze(input, seen = new Set()) {
  if (!input || typeof input !== 'object' || seen.has(input)) return input;
  seen.add(input);
  for (const child of Object.values(input)) deepFreeze(child, seen);
  return Object.freeze(input);
}

function itemId(item) {
  return value(item?.itemId ?? item?.item_id ?? item?.id);
}

function requestId(item) {
  return value(item?.requestId ?? item?.request_id ?? item?.batchItemId ?? item?.batch_item_id ?? itemId(item));
}

function providerRequestId(item) {
  return value(item?.providerRequestId ?? item?.provider_request_id);
}

function idempotencyKey(item) {
  return value(item?.idempotencyKey ?? item?.idempotency_key ?? item?.key ?? itemId(item));
}

function quantityFor(item) {
  const valueToParse = item?.settings?.quantity ?? item?.settings?.outputs ?? item?.requested_settings?.quantity ?? item?.quantity ?? 1;
  const quantity = Number(valueToParse);
  return Number.isInteger(quantity) && quantity > 0 ? quantity : 1;
}

function outputPathFor(item, index = 0, media = {}) {
  const outputs = item?.outputs ?? item?.output_paths ?? item?.outputPaths;
  if (Array.isArray(outputs)) {
    const candidate = outputs[index];
    if (typeof candidate === 'string') return candidate;
    if (candidate?.output_path || candidate?.path) return candidate.output_path ?? candidate.path;
  }
  if (item?.output_path || item?.outputPath) return item.output_path ?? item.outputPath;
  if (media?.outputPath || media?.output_path) return media.outputPath ?? media.output_path;
  return null;
}

function requestObservation(valueToInspect) {
  if (!valueToInspect || typeof valueToInspect !== 'object') return null;
  if (valueToInspect.observation) return valueToInspect.observation;
  if (valueToInspect.media) return valueToInspect;
  if (Array.isArray(valueToInspect.items)) return { media: valueToInspect };
  return null;
}

function asMediaItems(valueToInspect) {
  const observation = requestObservation(valueToInspect);
  if (!observation) return [];
  if (Array.isArray(observation.media?.items)) return observation.media.items;
  if (Array.isArray(observation.items)) return observation.items;
  if (Array.isArray(observation.media)) return observation.media;
  return [];
}

function stableJson(valueToHash) {
  if (Array.isArray(valueToHash)) return `[${valueToHash.map(stableJson).join(',')}]`;
  if (valueToHash && typeof valueToHash === 'object') {
    return `{${Object.keys(valueToHash).sort().map((key) => `${JSON.stringify(key)}:${stableJson(valueToHash[key])}`).join(',')}}`;
  }
  return JSON.stringify(valueToHash);
}

async function metadataHash(valueToHash) {
  const body = new TextEncoder().encode(stableJson(valueToHash));
  const subtle = globalThis.crypto?.subtle;
  if (!subtle) return null;
  try {
    const digest = await subtle.digest('SHA-256', body);
    return [...new Uint8Array(digest)].map((byte) => byte.toString(16).padStart(2, '0')).join('');
  } catch {
    return null;
  }
}

function skippedResult(item, existing) {
  return deepFreeze({
    schema_version: 'flow-image-item-result.v1',
    status: 'completed',
    skipped: true,
    skip_reason: 'already_completed',
    item_id: itemId(item),
    idempotency_key: idempotencyKey(item),
    existing_result: existing?.result ?? existing ?? null,
    outputs: existing?.outputs ?? existing?.result?.outputs ?? [],
    render_eligible: false,
    review_state: 'quarantined',
  });
}

function asError(error, fallbackCode = 'image_runner_failed') {
  if (error instanceof ImageRunnerError) return error;
  const code = value(error?.code) || fallbackCode;
  return new ImageRunnerError(code, error?.message || String(error), { cause: error });
}

/**
 * Execute Flow image items serially. The active lock is intentionally local to
 * this executor: a second submit cannot happen while the first item is still
 * settling/downloading/importing.
 */
export class SerialImageRunner {
  constructor({
    driver = null,
    contentDriver = null,
    observer = null,
    downloader = null,
    importer = null,
    queue = null,
    completedItems = null,
    completedStore = null,
    findCompleted = null,
    clock = () => new Date(),
    timeoutMs = 300000,
    pollIntervalMs = 100,
    stabilityPolls = 2,
    onProgress = null,
  } = {}) {
    this.driver = driver || contentDriver;
    if (!this.driver) throw new ImageRunnerError('driver_required', 'A Flow content driver is required');
    this.downloader = downloader || { download: (options) => downloadMedia(options) };
    this.importer = importer;
    this.queue = queue;
    this.completedItems = completedItems || new Map();
    this.completedStore = completedStore;
    this.findCompleted = findCompleted;
    this.clock = clock;
    this.timeoutMs = timeoutMs;
    this.pollIntervalMs = pollIntervalMs;
    this.stabilityPolls = stabilityPolls;
    this.onProgress = onProgress;
    this._active = null;
    this._observer = observer || createMediaObserver({
      clock,
      pollIntervalMs,
      stabilityPolls,
      snapshot: () => this._snapshot(),
    });
  }

  get activeRequest() {
    return this._active;
  }

  _snapshot() {
    if (typeof this.driver.snapshot === 'function') return this.driver.snapshot();
    if (typeof this.driver.inspect === 'function') return this.driver.inspect();
    if (typeof this.driver.observe === 'function') return this.driver.observe();
    return { media: { items: [], failures: [] } };
  }

  _emit(event, payload = {}) {
    try { this.onProgress?.({ schema_version: FLOW_IMAGE_RUNNER_VERSION, event, ...payload }); }
    catch { /* progress callbacks cannot change execution truth */ }
  }

  async _lookupCompleted(item) {
    const key = idempotencyKey(item);
    const id = itemId(item);
    if (item?.status === 'completed' || item?.completed_at || item?.completedAt) return item;
    if (this.completedItems instanceof Set) {
      if (this.completedItems.has(key) || this.completedItems.has(id)) return { idempotency_key: key, item_id: id };
    } else if (this.completedItems && typeof this.completedItems === 'object') {
      const found = this.completedItems[key] ?? this.completedItems[id];
      if (found) return found;
    }
    if (typeof this.findCompleted === 'function') {
      const found = await this.findCompleted(item);
      if (found) return found;
    }
    if (this.completedStore?.get) {
      const found = await this.completedStore.get(key ?? id);
      if (found) return found;
    }
    return null;
  }

  async _prepare(item) {
    if (typeof this.driver.prepare !== 'function') throw new ImageRunnerError('prepare_unavailable');
    const result = await this.driver.prepare(item, { strict: true });
    if (!result?.ok || (result.state && !['ready_to_submit', 'submitted'].includes(result.state))) {
      throw new ImageRunnerError('prepare_failed', 'Flow item failed verified preflight', { result });
    }
    return result;
  }

  async _submit() {
    if (typeof this.driver.submit !== 'function') throw new ImageRunnerError('submit_unavailable');
    const result = await this.driver.submit();
    if (!result?.ok) throw new ImageRunnerError('submit_failed', 'Flow submit did not succeed', { result });
    return result;
  }

  async _waitForMedia(item, generationResult = null) {
    const expected = { providerRequestId: providerRequestId(item) };
    const resultObservation = requestObservation(generationResult);
    if (resultObservation) {
      const selected = selectFreshMedia(this._observer.before, resultObservation, expected);
      if (selected.settled.length) {
        return {
          ok: true,
          item: selected.settled[0],
          items: selected.settled,
          before: this._observer.before,
          after: selected.after,
          diff: selected,
          source: 'generation_result',
        };
      }
    }
    if (typeof this._observer.waitForStableNewMedia === 'function') {
      return this._observer.waitForStableNewMedia({
        getSnapshot: () => this._snapshot(),
        expected,
        timeoutMs: item.timeoutMs ?? this.timeoutMs,
        pollInterval: item.pollIntervalMs ?? this.pollIntervalMs,
        requiredPolls: item.stabilityPolls ?? this.stabilityPolls,
      });
    }
    throw new ImageRunnerError('media_observer_unavailable');
  }

  async _waitGeneration(item) {
    if (typeof this.driver.waitForGeneration !== 'function') return null;
    const result = await this.driver.waitForGeneration({
      timeoutMs: item.timeoutMs ?? this.timeoutMs,
      pollIntervalMs: item.pollIntervalMs ?? this.pollIntervalMs,
    });
    if (result?.ok === false || ['failed', 'blocked', 'paused_for_operator'].includes(result?.state)) {
      throw new ImageRunnerError(result?.code || 'generation_failed', 'Flow generation did not complete', { result });
    }
    return result;
  }

  async _download(media, item, ordinal) {
    const options = {
      media,
      item,
      itemId: itemId(item),
      requestId: requestId(item),
      url: media?.url ?? media?.downloadUrl ?? media?.download_url,
      filename: media?.filename ?? item?.download_filename ?? item?.downloadFilename,
      timeoutMs: item.timeoutMs ?? this.timeoutMs,
      pollIntervalMs: item.pollIntervalMs ?? this.pollIntervalMs,
      ordinal,
    };
    if (typeof this.downloader === 'function') return this.downloader(options);
    if (typeof this.downloader.downloadMedia === 'function') return this.downloader.downloadMedia(options);
    if (typeof this.downloader.download === 'function') return this.downloader.download(options);
    throw new ImageRunnerError('downloader_unavailable');
  }

  async _import(download, media, item, ordinal) {
    if (!this.importer) throw new ImageRunnerError('output_importer_required', 'Downloaded Flow output must be imported into quarantine');
    const context = {
      sourcePath: download?.path ?? download?.filePath ?? download?.file_path ?? download?.filename ?? download?.downloadPath,
      downloadPath: download?.path ?? download?.filePath ?? download?.file_path ?? download?.downloadPath,
      outputPath: outputPathFor(item, ordinal, media),
      itemId: itemId(item),
      requestId: requestId(item),
      providerMediaId: media?.providerMediaId ?? media?.id ?? null,
      downloadId: download?.downloadId ?? download?.id ?? null,
      item,
      media,
      download,
    };
    if (typeof this.importer === 'function') return this.importer(context);
    if (typeof this.importer.importOutput === 'function') return this.importer.importOutput(context);
    if (typeof this.importer.importDownloadedOutput === 'function') return this.importer.importDownloadedOutput(context);
    throw new ImageRunnerError('output_importer_unavailable');
  }

  async _execute(item) {
    const beforeInput = await this._snapshot();
    if (typeof this._observer.begin === 'function') this._observer.begin(beforeInput);
    this._emit('before_snapshot', { item_id: itemId(item), snapshot: this._observer.before });

    const prepared = await this._prepare(item);
    this._emit('prepared', { item_id: itemId(item), state: prepared.state });
    await this._submit();
    this._emit('submitted', { item_id: itemId(item) });
    const generation = await this._waitGeneration(item);
    const stable = await this._waitForMedia(item, generation);
    const quantity = quantityFor(item);
    const mediaItems = (stable.items || [stable.item]).filter(Boolean).slice(0, quantity);
    if (!mediaItems.length) throw new ImageRunnerError('fresh_media_missing', 'No new settled media was associated with the active item', { stable });
    if (mediaItems.length < quantity) {
      throw new ImageRunnerError('output_quantity_mismatch', `Expected ${quantity} new media item(s), observed ${mediaItems.length}`, { stable });
    }

    const outputs = [];
    for (let index = 0; index < mediaItems.length; index += 1) {
      const media = mediaItems[index];
      this._emit('media_settled', { item_id: itemId(item), media_id: mediaIdentity(media), ordinal: index });
      const download = await this._download(media, item, index);
      const imported = await this._import(download, media, item, index);
      outputs.push(deepFreeze({ ordinal: index, media, download, import: imported }));
      this._emit('output_imported', { item_id: itemId(item), ordinal: index, output: imported });
    }
    // Keep the content driver's explicit UI state machine in sync with the
    // browser download/import boundary when one is attached.
    try {
      const finalObservation = await this._snapshot();
      this.driver.machine?.recordGenerationStatus?.('downloaded', finalObservation, { downloaded: true });
    } catch {
      // Result/import truth is already durable; a diagnostic-only state update
      // must not rewrite a completed output.
    }
    const resultBase = {
      schema_version: 'flow-image-item-result.v1',
      runner_version: FLOW_IMAGE_RUNNER_VERSION,
      status: 'completed',
      skipped: false,
      item_id: itemId(item),
      idempotency_key: idempotencyKey(item),
      request_id: requestId(item),
      batch_id: value(item?.batch_id ?? item?.batchId),
      outputs,
      items: outputs,
      output_count: outputs.length,
      before_media: this._observer.before.items,
      render_eligible: false,
      review_state: 'quarantined',
      completed_at: new Date(typeof this.clock === 'function' ? this.clock() : this.clock).toISOString(),
    };
    resultBase.artifact_hash = await metadataHash(resultBase);
    const result = deepFreeze(resultBase);
    this.completedItems?.set?.(idempotencyKey(item), result);
    this.completedItems?.set?.(itemId(item), result);
    await this.completedStore?.set?.(idempotencyKey(item), result);
    return result;
  }

  async run(item) {
    if (!item || typeof item !== 'object') throw new ImageRunnerError('invalid_item');
    const key = idempotencyKey(item);
    const existing = await this._lookupCompleted(item);
    if (existing) return skippedResult(item, existing);
    if (this._active) {
      throw new ImageRunnerError('active_request_exists', 'Only one Flow image request may be active at a time', {
        activeItemId: itemId(this._active),
      });
    }
    this._active = item;
    const isZeroCredit = item.budget_policy?.kind === 'zero_credit' || item.budget_policy?.expected_credits === 0;
    const maxAttempts = isZeroCredit ? 3 : 1;
    let lastError = null;
    try {
      for (let attempt = 1; attempt <= maxAttempts; attempt += 1) {
        try {
          return await this._execute(item);
        } catch (error) {
          lastError = asError(error);
          if (attempt < maxAttempts && !['active_request_exists', 'invalid_item'].includes(lastError.code)) {
            this._emit('retry_attempt', { item_id: itemId(item), attempt, error: lastError.code });
            await new Promise((resolve) => setTimeout(resolve, attempt * 1200));
            continue;
          }
          throw lastError;
        }
      }
    } catch (error) {
      const normalized = asError(error);
      this._emit('failed', { item_id: itemId(item), code: normalized.code });
      throw normalized;
    } finally {
      this._active = null;
    }
  }

  async runItem(item) {
    return this.run(item);
  }

  async runBatch(items = []) {
    if (!Array.isArray(items)) throw new ImageRunnerError('items_must_be_array');
    const results = [];
    for (const item of items) results.push(await this.run(item));
    return deepFreeze({
      schema_version: 'flow-image-batch-execution.v1',
      status: 'completed',
      results,
      completed_count: results.filter((result) => result.status === 'completed').length,
      skipped_count: results.filter((result) => result.skipped).length,
    });
  }

  async resume(items = []) {
    return this.runBatch(items);
  }

  async runNext(queue = this.queue) {
    if (!queue?.claimNext) throw new ImageRunnerError('queue_unavailable');
    const job = await queue.claimNext();
    if (!job) return null;
    try {
      const result = await this.run(job);
      await queue.complete(job.job_id, result);
      return result;
    } catch (error) {
      const normalized = asError(error);
      await queue.fail(job.job_id, { code: normalized.code, message: normalized.message });
      throw normalized;
    }
  }
}

export function createImageRunner(options) {
  return new SerialImageRunner(options);
}

export async function runImageBatch(items, options = {}) {
  return createImageRunner(options).runBatch(items);
}

export const ImageRunner = SerialImageRunner;
export const SerialImageExecutor = SerialImageRunner;
export const runSerialImageBatch = runImageBatch;
export const executeImageBatch = runImageBatch;
