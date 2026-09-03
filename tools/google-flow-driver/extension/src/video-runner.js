import {
  createMediaObserver,
  mediaIdentity,
  selectFreshMedia,
} from './media-observer.js';
import { downloadMedia } from './downloads.js';

export const FLOW_VIDEO_RUNNER_VERSION = 'flow-video-runner.v1';
export const FLOW_VIDEO_ACTIONS = Object.freeze(['video_hook_generation', 'scene_generation']);
export const FLOW_VIDEO_FALLBACK_PROVIDER = 'remotion_hyperframes';

export class VideoRunnerError extends Error {
  constructor(code, message = code, details = {}) {
    super(message);
    this.name = 'VideoRunnerError';
    this.code = code;
    this.details = details;
  }
}

function value(input) {
  return input === undefined || input === null || input === '' ? null : String(input);
}

function number(input) {
  return typeof input === 'number' && Number.isFinite(input) ? input : Number(input);
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
  return value(item?.providerRequestId
    ?? item?.provider_request_id
    ?? item?.requestId
    ?? item?.request_id
    ?? item?.batchItemId
    ?? item?.batch_item_id
    ?? itemId(item));
}

function explicitRequestId(item) {
  return value(item?.requestId
    ?? item?.request_id
    ?? item?.batchItemId
    ?? item?.batch_item_id);
}

function providerRequestId(item) {
  return value(item?.providerRequestId ?? item?.provider_request_id);
}

function expectedMediaBinding(item) {
  const provider = providerRequestId(item);
  if (provider) return { providerRequestId: provider };
  const request = explicitRequestId(item);
  return request ? { requestId: request } : {};
}

function idempotencyKey(item) {
  return value(item?.idempotencyKey ?? item?.idempotency_key ?? item?.key ?? itemId(item));
}

function settingsFor(request) {
  const settings = request?.requested_settings ?? request?.requestedSettings ?? request?.settings ?? {};
  return {
    model: value(settings.model ?? request?.model),
    mode: value(settings.mode ?? request?.mode ?? 'video'),
    aspectRatio: value(settings.aspect_ratio ?? settings.aspectRatio ?? settings.ratio ?? request?.aspect_ratio ?? request?.aspectRatio ?? request?.ratio),
    durationSeconds: toSeconds(settings.duration_seconds ?? settings.duration ?? request?.duration_seconds ?? request?.duration),
    quantity: integer(settings.quantity ?? settings.outputs ?? request?.quantity ?? request?.outputs, 1),
  };
}

function integer(input, fallback = null) {
  const result = Number(input);
  return Number.isInteger(result) ? result : fallback;
}

function toSeconds(input) {
  if (input === undefined || input === null || input === '') return null;
  if (typeof input === 'number' && Number.isInteger(input)) return input;
  const match = String(input).trim().match(/^(\d+)\s*(?:s|sec|secs|second|seconds)?$/i);
  return match ? Number(match[1]) : null;
}

function normalizeSetting(input) {
  return String(input ?? '').trim().replace(/[×✕]/g, 'x').replace(/\s+/g, ' ').toLowerCase();
}

function normalizeObservedSettings(observation) {
  const values = observation?.settings?.values ?? observation?.settings ?? observation?.values ?? {};
  return {
    model: value(values.model ?? observation?.model),
    mode: value(values.mode ?? observation?.mode),
    aspectRatio: value(values.ratio ?? values.aspect_ratio ?? values.aspectRatio ?? observation?.aspectRatio ?? observation?.aspect_ratio),
    durationSeconds: toSeconds(values.duration ?? values.duration_seconds ?? observation?.duration ?? observation?.duration_seconds),
    quantity: integer(values.quantity ?? values.outputs ?? observation?.quantity ?? observation?.outputs),
  };
}

function rootAttribute(observation, name) {
  const root = observation?.root?.element ?? observation?.root?.root ?? observation?.root;
  return root && typeof root.getAttribute === 'function' ? root.getAttribute(name) : null;
}

function observedAccountVerified(observation) {
  if (observation?.account?.verified !== undefined) return observation.account.verified === true;
  if (observation?.accountVerified !== undefined) return observation.accountVerified === true;
  return rootAttribute(observation, 'data-flow-account-verified') === 'true';
}

function observedProjectUrl(observation) {
  return value(observation?.projectUrl ?? observation?.project_url ?? observation?.page?.projectUrl ?? rootAttribute(observation, 'data-flow-project-url'));
}

function referencesCount(observation) {
  const references = observation?.references;
  if (Number.isInteger(references?.count)) return references.count;
  if (Array.isArray(references?.nodes)) return references.nodes.length;
  if (Array.isArray(references)) return references.length;
  return null;
}

function parseDisplayedCost(credit = {}) {
  if (credit?.known === false) return { known: false, cost: null, scope: null, label: null };
  const candidates = [
    credit.batchCost,
    credit.batch_cost,
    credit.cost,
    credit.displayedCost,
    credit.displayed_cost,
    credit.credits,
    credit.observed,
    credit.label,
  ];
  for (const candidate of candidates) {
    if (typeof candidate === 'number' && Number.isFinite(candidate)) {
      return { known: true, cost: candidate, scope: credit.batchCost !== undefined || credit.batch_cost !== undefined ? 'batch' : credit.costScope || credit.cost_scope || 'job' };
    }
    if (typeof candidate !== 'string') continue;
    const text = candidate.trim();
    if (/unknown|unavailable|n\/a|\?{2,}/i.test(text)) continue;
    const match = text.match(/(?:cost|credit(?:s)?|price)?[^0-9]*(\d+(?:\.\d+)?)/i);
    if (match) {
      return {
        known: true,
        cost: Number(match[1]),
        scope: credit.costScope || credit.cost_scope || 'job',
        label: text,
      };
    }
  }
  return { known: false, cost: null, scope: null, label: null };
}

function capabilityObject(request) {
  const snapshot = request?.capability_snapshot ?? request?.capabilitySnapshot ?? request?.capability ?? null;
  if (!snapshot || typeof snapshot !== 'object') return null;
  if (Array.isArray(snapshot.offerings)) return snapshot;
  if (snapshot.offering && typeof snapshot.offering === 'object') return { ...snapshot, offerings: [snapshot.offering] };
  if (snapshot.action || snapshot.model) return { offerings: [snapshot] };
  return snapshot;
}

function capabilityOffering(request, settings) {
  const snapshot = capabilityObject(request);
  const offerings = Array.isArray(snapshot?.offerings) ? snapshot.offerings : [];
  const action = value(request?.action ?? request?.batch_action ?? 'video_hook_generation');
  const matches = offerings.filter((offering) => (
    value(offering.action) === action
    && normalizeSetting(offering.model) === normalizeSetting(settings.model)
    && normalizeSetting(offering.mode) === normalizeSetting(settings.mode)
    && normalizeSetting(offering.aspect_ratio) === normalizeSetting(settings.aspectRatio)
    && toSeconds(offering.duration_seconds) === settings.durationSeconds
    && integer(offering.quantity) === settings.quantity
  ));
  return { snapshot, offerings, matches, offering: matches.length === 1 ? matches[0] : null };
}

function approvalFor(request) {
  const policy = request?.approval_policy ?? request?.approvalPolicy ?? request?.approval ?? {};
  return {
    state: value(policy.state ?? request?.approval_state),
    approvalId: value(policy.approval_id ?? policy.approvalId ?? request?.approval_id ?? request?.approvalId),
    expectedAccountVerified: policy.expected_account_verified ?? policy.expectedAccountVerified ?? request?.expected_account_verified,
  };
}

function budgetFor(request) {
  const policy = request?.budget_policy ?? request?.budgetPolicy ?? request?.budget ?? {};
  return {
    kind: value(policy.kind ?? request?.budget_kind ?? 'paid'),
    expectedCredits: integer(policy.expected_credits ?? policy.expectedCredits ?? request?.expected_credits ?? request?.expectedCredits),
    maxCredits: integer(policy.max_credits ?? policy.maxCredits ?? request?.max_credits ?? request?.maxCredits),
  };
}

function fallbackFor(request, fallback = null) {
  const supplied = request?.fallback ?? request?.fallback_policy ?? fallback ?? {
    provider: FLOW_VIDEO_FALLBACK_PROVIDER,
    reason: 'Use deterministic Remotion/HyperFrames motion when Flow preflight or execution blocks.',
  };
  return {
    provider: value(supplied.provider),
    reason: value(supplied.reason),
  };
}

function semanticId(request) {
  const binding = request?.semantic_binding ?? request?.semanticBinding;
  return value(request?.sentence_id ?? request?.sentenceId ?? binding?.sentence_id ?? binding?.sentenceId);
}

function capabilityFresh(snapshot, asOf = new Date()) {
  if (!snapshot?.expires_at && !snapshot?.expiresAt) return null;
  const expires = new Date(snapshot.expires_at ?? snapshot.expiresAt);
  const now = asOf instanceof Date ? asOf : new Date(asOf);
  if (Number.isNaN(expires.valueOf()) || Number.isNaN(now.valueOf())) return false;
  return now <= expires;
}

function preflightFailure(code, message, details = {}) {
  return { code, message, ...details };
}

/**
 * Fail-closed paid-video preflight. This function is pure: it never opens the
 * Flow UI, submits a request, or spends credits.
 */
export function validateVideoPreflight(request = {}, observation = {}, { asOf = new Date(), fallback = null } = {}) {
  const failures = [];
  const settings = settingsFor(request);
  const observed = normalizeObservedSettings(observation);
  const budget = budgetFor(request);
  const approval = approvalFor(request);
  const fallbackRecord = fallbackFor(request, fallback);
  const action = value(request.action ?? request.batch_action ?? 'video_hook_generation');
  const references = Array.isArray(request.references) ? request.references : [];
  const capability = capabilityOffering(request, settings);
  const creditObservation = observation.credit ?? observation.credits ?? observation;
  const displayed = parseDisplayedCost(creditObservation);

  if (!FLOW_VIDEO_ACTIONS.includes(action)) failures.push(preflightFailure('video_action_required', 'Paid runner accepts only authored video actions'));
  if (!itemId(request)) failures.push(preflightFailure('item_id_required', 'A manifest-bound video item_id is required'));
  if (!idempotencyKey(request)) failures.push(preflightFailure('idempotency_key_required', 'A manifest-bound idempotency key is required'));
  if (!semanticId(request)) failures.push(preflightFailure('semantic_binding_required', 'A sentence/beat semantic binding is required'));
  if (!settings.model || !settings.mode || !settings.aspectRatio || !Number.isInteger(settings.durationSeconds) || !Number.isInteger(settings.quantity)) {
    failures.push(preflightFailure('requested_settings_incomplete', 'Video model, mode, aspect ratio, duration, and quantity are required'));
  }
  if (settings.mode && normalizeSetting(settings.mode) !== 'video') failures.push(preflightFailure('video_mode_required', 'Paid runner requires video mode'));

  for (const key of ['model', 'mode', 'aspectRatio']) {
    const requestedValue = settings[key];
    const observedValue = observed[key];
    if (requestedValue && observedValue && normalizeSetting(requestedValue) !== normalizeSetting(observedValue)) {
      failures.push(preflightFailure(`setting_${key}_mismatch`, `${key} changed between preflight and submit`, { expectedPresent: true, observedPresent: true }));
    } else if (requestedValue && !observedValue) {
      failures.push(preflightFailure(`setting_${key}_unknown`, `${key} is not observable in the current Flow UI`));
    }
  }
  if (Number.isInteger(settings.durationSeconds) && observed.durationSeconds !== settings.durationSeconds) failures.push(preflightFailure('duration_mismatch', 'Video duration changed or is not observable'));
  if (Number.isInteger(settings.quantity) && observed.quantity !== settings.quantity) failures.push(preflightFailure('quantity_mismatch', 'Video quantity changed or is not observable'));

  const expectedReferences = references.length;
  const observedReferences = referencesCount(observation);
  if (observedReferences === null || observedReferences !== expectedReferences) failures.push(preflightFailure('reference_count_mismatch', 'Reference count does not match the validated manifest'));
  for (const [index, reference] of references.entries()) {
    if (!reference || !value(reference.path) || !/^[a-f0-9]{64}$/i.test(String(reference.sha256 || ''))) {
      failures.push(preflightFailure('reference_binding_invalid', `Reference ${index} is not path/hash bound`));
    }
  }

  if (!capability.snapshot) failures.push(preflightFailure('capability_snapshot_required', 'Current capability snapshot is required before paid video submission'));
  const freshness = capabilityFresh(capability.snapshot, asOf);
  if (freshness === false) failures.push(preflightFailure('capability_snapshot_stale', 'Capability snapshot is expired'));
  if (capability.offerings.length && !capability.offering) failures.push(preflightFailure('capability_settings_mismatch', 'Requested model/settings do not match one exact current capability offering'));
  if (capability.offering?.credit_state !== 'positive' || !Number.isInteger(capability.offering?.credits_per_generation) || capability.offering.credits_per_generation <= 0) {
    failures.push(preflightFailure('paid_cost_unknown', 'Positive exact displayed video cost is required'));
  }

  const perGeneration = capability.offering?.credits_per_generation ?? (displayed.known && displayed.scope !== 'batch' ? displayed.cost : null);
  const expectedCredits = budget.expectedCredits ?? (Number.isInteger(perGeneration) ? perGeneration * settings.quantity : null);
  const maxCredits = budget.maxCredits;
  if (budget.kind !== 'paid') failures.push(preflightFailure('paid_budget_required', 'Paid video requires a paid budget policy'));
  if (!Number.isInteger(expectedCredits) || expectedCredits <= 0) failures.push(preflightFailure('expected_credit_cost_required', 'Exact positive expected credits are required'));
  if (!Number.isInteger(maxCredits) || maxCredits <= 0) failures.push(preflightFailure('credit_ceiling_required', 'A positive max-credit ceiling is required'));
  if (Number.isInteger(expectedCredits) && Number.isInteger(maxCredits) && maxCredits < expectedCredits) failures.push(preflightFailure('credit_ceiling_exceeded', 'Batch credit ceiling is below the exact expected cost'));
  if (Number.isInteger(perGeneration) && Number.isInteger(expectedCredits) && expectedCredits !== perGeneration * settings.quantity) failures.push(preflightFailure('expected_credit_mismatch', 'Expected credits do not match exact model/duration/quantity cost'));
  if (!displayed.known) failures.push(preflightFailure('displayed_cost_unknown', 'Current Flow displayed cost is unknown'));
  else if (displayed.scope === 'batch' && Number.isInteger(expectedCredits) && displayed.cost !== expectedCredits) failures.push(preflightFailure('displayed_cost_mismatch', 'Displayed batch cost differs from approved ceiling')); 
  else if (displayed.scope !== 'batch' && Number.isInteger(perGeneration) && displayed.cost !== perGeneration) failures.push(preflightFailure('displayed_cost_mismatch', 'Displayed per-job cost differs from the capability snapshot'));

  if (approval.state !== 'operator_approved' && approval.state !== 'executed') failures.push(preflightFailure('operator_approval_required', 'Paid video requires named operator approval'));
  if (!approval.approvalId) failures.push(preflightFailure('approval_id_required', 'Paid video requires an explicit approval ID'));
  if (approval.expectedAccountVerified !== true || !observedAccountVerified(observation)) failures.push(preflightFailure('account_not_verified', 'Expected Flow account is not verified'));
  const expectedProject = value(request.project_url ?? request.projectUrl);
  const observedProject = observedProjectUrl(observation);
  if (expectedProject && observedProject && expectedProject !== observedProject) failures.push(preflightFailure('project_mismatch', 'Flow project changed during preflight'));
  if (!fallbackRecord.provider || fallbackRecord.provider !== FLOW_VIDEO_FALLBACK_PROVIDER || !fallbackRecord.reason || fallbackRecord.reason.length < 12) failures.push(preflightFailure('deterministic_fallback_required', 'Remotion/HyperFrames fallback must remain declared'));

  return deepFreeze({
    schema_version: 'google-flow-video-preflight.v1',
    ok: failures.length === 0,
    code: failures[0]?.code ?? 'paid_video_preflight_verified',
    failures,
    action,
    item_id: itemId(request),
    semantic_binding_id: semanticId(request),
    settings,
    observed_settings: observed,
    references: { expected: expectedReferences, observed: observedReferences },
    capability: {
      snapshot_id: value(capability.snapshot?.snapshot_id ?? capability.snapshot?.snapshotId),
      offering: capability.offering ? {
        model: capability.offering.model,
        mode: capability.offering.mode,
        aspect_ratio: capability.offering.aspect_ratio,
        duration_seconds: capability.offering.duration_seconds,
        quantity: capability.offering.quantity,
        displayed_credit_label: capability.offering.displayed_credit_label,
        credit_state: capability.offering.credit_state,
        credits_per_generation: capability.offering.credits_per_generation,
      } : null,
    },
    displayed_cost: displayed,
    credits: { per_generation: perGeneration, expected: expectedCredits, max: maxCredits },
    approval: { state: approval.state, approval_id: approval.approvalId, expected_account_verified: approval.expectedAccountVerified === true },
    fallback: fallbackRecord,
  });
}

export function preflightVideoBatch(input = {}, observation = {}, options = {}) {
  if (input && typeof input === 'object' && (input.request || input.observation)) {
    return validateVideoPreflight(input.request ?? {}, input.observation ?? {}, input.options ?? options);
  }
  return validateVideoPreflight(input, observation, options);
}
export const validatePaidVideoPreflight = validateVideoPreflight;

function mediaObservation(valueToInspect) {
  if (!valueToInspect || typeof valueToInspect !== 'object') return null;
  if (valueToInspect.observation) return valueToInspect.observation;
  if (valueToInspect.media) return valueToInspect;
  if (Array.isArray(valueToInspect.items)) return { media: valueToInspect };
  return null;
}

function outputPathFor(item, index, media) {
  const outputs = item?.outputs ?? item?.output_paths ?? item?.outputPaths;
  const candidate = Array.isArray(outputs) ? outputs[index] : null;
  if (typeof candidate === 'string') return candidate;
  if (candidate?.output_path || candidate?.path) return candidate.output_path ?? candidate.path;
  return item?.output_path ?? item?.outputPath ?? media?.output_path ?? media?.outputPath ?? null;
}

function stableJson(input) {
  if (Array.isArray(input)) return `[${input.map(stableJson).join(',')}]`;
  if (input && typeof input === 'object') return `{${Object.keys(input).sort().map((key) => `${JSON.stringify(key)}:${stableJson(input[key])}`).join(',')}}`;
  return JSON.stringify(input);
}

async function metadataHash(input) {
  if (!globalThis.crypto?.subtle) return null;
  try {
    const digest = await globalThis.crypto.subtle.digest('SHA-256', new TextEncoder().encode(stableJson(input)));
    return [...new Uint8Array(digest)].map((byte) => byte.toString(16).padStart(2, '0')).join('');
  } catch {
    return null;
  }
}

function actualCreditValue(valueToInspect) {
  if (typeof valueToInspect === 'number' && Number.isFinite(valueToInspect)) return valueToInspect;
  if (!valueToInspect || typeof valueToInspect !== 'object') return null;
  for (const key of ['actual_credits', 'actualCredits', 'spent_credits', 'spentCredits', 'credits']) {
    if (typeof valueToInspect[key] === 'number' && Number.isFinite(valueToInspect[key])) return valueToInspect[key];
  }
  return null;
}

function idempotentCompleted(item, completedItems) {
  if (item?.status === 'completed' || item?.completed_at || item?.completedAt) return item;
  const key = idempotencyKey(item);
  const id = itemId(item);
  if (completedItems instanceof Set) return completedItems.has(key) || completedItems.has(id) ? { item_id: id, idempotency_key: key } : null;
  if (completedItems && typeof completedItems === 'object') return completedItems[key] ?? completedItems[id] ?? null;
  return null;
}

function errorFor(error, fallback = 'video_runner_failed') {
  if (error instanceof VideoRunnerError) return error;
  return new VideoRunnerError(value(error?.code) || fallback, error?.message || String(error), { cause: error });
}

function skippedResult(item, existing, fallback) {
  return deepFreeze({
    schema_version: 'flow-video-item-result.v1',
    status: 'completed',
    skipped: true,
    skip_reason: 'already_completed',
    item_id: itemId(item),
    idempotency_key: idempotencyKey(item),
    existing_result: existing?.result ?? existing ?? null,
    outputs: existing?.outputs ?? existing?.result?.outputs ?? [],
    fallback,
    render_eligible: false,
    review_state: 'quarantined',
  });
}

/** Serial, approval-bound Flow video executor. */
export class SerialVideoRunner {
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
    creditReader = null,
    readCredits = null,
    creditRecorder = null,
    recordCredits = null,
    fallback = null,
    clock = () => new Date(),
    timeoutMs = 600000,
    pollIntervalMs = 100,
    stabilityPolls = 2,
    onProgress = null,
  } = {}) {
    this.driver = driver || contentDriver;
    if (!this.driver) throw new VideoRunnerError('driver_required', 'A Flow content driver is required');
    this.downloader = downloader || { download: (options) => downloadMedia(options) };
    this.importer = importer;
    this.queue = queue;
    this.completedItems = completedItems || new Map();
    this.completedStore = completedStore;
    this.findCompleted = findCompleted;
    this.creditReader = creditReader || readCredits;
    this.creditRecorder = creditRecorder || recordCredits;
    this.fallback = fallback;
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

  get activeRequest() { return this._active; }

  _snapshot() {
    if (typeof this.driver.snapshot === 'function') return this.driver.snapshot();
    if (typeof this.driver.inspect === 'function') return this.driver.inspect();
    return { media: { items: [], failures: [] } };
  }

  _emit(event, payload = {}) {
    try { this.onProgress?.({ schema_version: FLOW_VIDEO_RUNNER_VERSION, event, ...payload }); } catch { /* evidence callbacks are advisory */ }
  }

  async _lookupCompleted(item) {
    const local = idempotentCompleted(item, this.completedItems);
    if (local) return local;
    if (typeof this.findCompleted === 'function') {
      const found = await this.findCompleted(item);
      if (found) return found;
    }
    if (this.completedStore?.get) return this.completedStore.get(idempotencyKey(item));
    return null;
  }

  async _readCredits(request, stage) {
    const reader = this.creditReader || this.driver.readCredits || this.driver.getActualCredits;
    if (typeof reader !== 'function') return { stage, value: null, observed: false };
    try {
      const result = await reader(request, { stage });
      return { stage, value: actualCreditValue(result), observed: true, raw: result };
    } catch (error) {
      return { stage, value: null, observed: false, error: value(error?.message || error) };
    }
  }

  async _recordCredits(event) {
    const recorder = this.creditRecorder;
    if (typeof recorder === 'function') return recorder(event);
    if (recorder?.record) return recorder.record(event);
    if (recorder?.append) return recorder.append(event);
    return null;
  }

  _resultBase(item, state, preflight, credits, outputs = [], errorCode = null, errorMessage = null) {
    const fallback = fallbackFor(item, this.fallback);
    const result = {
      schema_version: 'flow-video-item-result.v1',
      runner_version: FLOW_VIDEO_RUNNER_VERSION,
      status: state,
      skipped: false,
      item_id: itemId(item),
      idempotency_key: idempotencyKey(item),
      batch_id: value(item?.batch_id ?? item?.batchId),
      outputs,
      output_count: outputs.length,
      credits,
      preflight,
      fallback,
      render_eligible: false,
      review_state: 'quarantined',
      quarantine: { state: 'quarantined', review_state: 'pending', render_eligible: false },
      error_code: errorCode,
      error_message: errorMessage,
      completed_at: state === 'completed' ? new Date(this.clock()).toISOString() : null,
    };
    return result;
  }

  async _waitForMedia(item, generation = null) {
    const expected = expectedMediaBinding(item);
    const observation = mediaObservation(generation);
    if (observation) {
      const selected = selectFreshMedia(this._observer.before, observation, expected);
      if (selected.settled.length) return { ...selected, item: selected.settled[0], items: selected.settled, source: 'generation_result' };
    }
    if (typeof this._observer.waitForStableNewMedia !== 'function') throw new VideoRunnerError('media_observer_unavailable');
    return this._observer.waitForStableNewMedia({
      getSnapshot: () => this._snapshot(),
      expected,
      timeoutMs: item.timeoutMs ?? this.timeoutMs,
      pollInterval: item.pollIntervalMs ?? this.pollIntervalMs,
      requiredPolls: item.stabilityPolls ?? this.stabilityPolls,
    });
  }

  async _download(media, item, ordinal) {
    const options = {
      media,
      item,
      itemId: itemId(item),
      requestId: requestId(item),
      url: media?.url ?? media?.downloadUrl ?? media?.download_url,
      filename: media?.filename ?? item?.download_filename ?? item?.downloadFilename ?? `${itemId(item) || 'flow-video'}-${ordinal + 1}.mp4`,
      timeoutMs: item.timeoutMs ?? this.timeoutMs,
      pollIntervalMs: item.pollIntervalMs ?? this.pollIntervalMs,
    };
    if (typeof this.downloader === 'function') return this.downloader(options);
    if (typeof this.downloader.downloadMedia === 'function') return this.downloader.downloadMedia(options);
    if (typeof this.downloader.download === 'function') return this.downloader.download(options);
    throw new VideoRunnerError('downloader_unavailable');
  }

  async _import(download, media, item, ordinal) {
    if (!this.importer) throw new VideoRunnerError('output_importer_required', 'Video output must be imported into quarantine');
    const context = {
      sourcePath: download?.path ?? download?.filePath ?? download?.file_path ?? download?.downloadPath,
      downloadPath: download?.path ?? download?.filePath ?? download?.file_path ?? download?.downloadPath,
      outputPath: outputPathFor(item, ordinal, media),
      itemId: itemId(item),
      requestId: requestId(item),
      providerMediaId: media?.providerMediaId ?? media?.id ?? null,
      downloadId: download?.downloadId ?? download?.download_id ?? download?.id ?? null,
      item,
      media,
      download,
    };
    if (typeof this.importer === 'function') return this.importer(context);
    if (typeof this.importer.importOutput === 'function') return this.importer.importOutput(context);
    if (typeof this.importer.importDownloadedOutput === 'function') return this.importer.importDownloadedOutput(context);
    throw new VideoRunnerError('output_importer_unavailable');
  }

  async _execute(item) {
    const firstObservation = await this._snapshot();
    const firstPreflight = validateVideoPreflight(item, firstObservation, { fallback: this.fallback, asOf: this.clock() });
    if (!firstPreflight.ok) throw new VideoRunnerError('video_preflight_blocked', 'Paid video preflight failed before submit', { preflight: firstPreflight });
    if (typeof this._observer.begin === 'function') this._observer.begin(firstObservation);
    this._emit('preflight_verified', { item_id: itemId(item), credits: firstPreflight.credits });

    if (typeof this.driver.prepare !== 'function') throw new VideoRunnerError('prepare_unavailable');
    const prepared = await this.driver.prepare(item, { strict: true });
    if (!prepared?.ok) throw new VideoRunnerError('prepare_failed', 'Flow video settings did not reach submit-ready state', { prepared });

    const finalObservation = await this._snapshot();
    const preflight = validateVideoPreflight(item, finalObservation, { fallback: this.fallback, asOf: this.clock() });
    if (!preflight.ok) throw new VideoRunnerError('video_preflight_changed', 'Paid video preflight changed before submit', { preflight });

    const creditsBefore = await this._readCredits(item, 'before_submit');
    let submitted = false;
    let submitAttempted = false;
    let generation = null;
    try {
      if (typeof this.driver.submit !== 'function') throw new VideoRunnerError('submit_unavailable');
      // A click may consume credits even when the provider rejects it or the
      // driver throws before returning a success result. Mark the attempt
      // before invoking the browser action so failed-attempt accounting is
      // never relabeled as unspent.
      submitAttempted = true;
      const submission = await this.driver.submit();
      if (!submission?.ok) throw new VideoRunnerError('submit_failed', 'Flow video submit did not succeed', { submission });
      submitted = true;
      this._emit('submitted', { item_id: itemId(item), approval_id: preflight.approval.approval_id });
      if (typeof this.driver.waitForGeneration === 'function') {
        generation = await this.driver.waitForGeneration({ timeoutMs: item.timeoutMs ?? this.timeoutMs, pollIntervalMs: item.pollIntervalMs ?? this.pollIntervalMs });
        if (generation?.ok === false || ['failed', 'blocked', 'paused_for_operator'].includes(generation?.state)) throw new VideoRunnerError(generation?.code || 'generation_failed', 'Flow video generation failed', { generation });
      }
      const stable = await this._waitForMedia(item, generation);
      const quantity = settingsFor(item).quantity;
      const mediaItems = (stable.items || [stable.item]).filter(Boolean).slice(0, quantity);
      if (mediaItems.length < quantity) throw new VideoRunnerError('output_quantity_mismatch', 'Flow produced fewer video outputs than approved', { expected: quantity, observed: mediaItems.length });
      const outputs = [];
      for (let ordinal = 0; ordinal < mediaItems.length; ordinal += 1) {
        const media = mediaItems[ordinal];
        const download = await this._download(media, item, ordinal);
        const imported = await this._import(download, media, item, ordinal);
        outputs.push(deepFreeze({ ordinal, media, download, import: imported }));
      }
      const creditsAfter = await this._readCredits(item, 'after_success');
      const delta = creditsBefore.value !== null && creditsAfter.value !== null ? Math.max(0, creditsAfter.value - creditsBefore.value) : actualCreditValue(generation);
      const credits = { estimated: preflight.credits.expected, actual: delta, unknown: delta === null, failed_attempt_credits: 0 };
      const creditEvent = { schema_version: 'flow-video-credit-event.v1', item_id: itemId(item), approval_id: preflight.approval.approval_id, outcome: 'completed', credits_before: creditsBefore.value, credits_after: creditsAfter.value, actual_credits: delta, failed_attempt_credits: 0 };
      await this._recordCredits(creditEvent);
      const base = this._resultBase(item, 'completed', preflight, credits, outputs);
      base.artifact_hash = await metadataHash(base);
      const result = deepFreeze(base);
      this.completedItems?.set?.(idempotencyKey(item), result);
      this.completedItems?.set?.(itemId(item), result);
      await this.completedStore?.set?.(idempotencyKey(item), result);
      return result;
    } catch (error) {
      const normalized = errorFor(error);
      const creditsAfter = submitAttempted ? await this._readCredits(item, 'after_failure') : { value: null, observed: false };
      const delta = submitAttempted && creditsBefore.value !== null && creditsAfter.value !== null ? Math.max(0, creditsAfter.value - creditsBefore.value) : submitAttempted ? actualCreditValue(generation) : null;
      const failedAttemptCredits = delta ?? 0;
      const credits = { estimated: firstPreflight.credits.expected, actual: delta, unknown: submitAttempted && delta === null, failed_attempt_credits: failedAttemptCredits };
      const creditEvent = { schema_version: 'flow-video-credit-event.v1', item_id: itemId(item), approval_id: firstPreflight.approval.approval_id, outcome: 'failed', credits_before: creditsBefore.value, credits_after: creditsAfter.value, actual_credits: delta, failed_attempt_credits: failedAttemptCredits, error_code: normalized.code };
      if (submitAttempted) await this._recordCredits(creditEvent);
      const result = this._resultBase(item, submitAttempted ? 'failed' : 'blocked', firstPreflight, credits, [], normalized.code, normalized.message);
      result.artifact_hash = await metadataHash(result);
      normalized.result = deepFreeze(result);
      normalized.credits = credits;
      throw normalized;
    }
  }

  async run(item) {
    if (!item || typeof item !== 'object') throw new VideoRunnerError('invalid_item');
    const existing = await this._lookupCompleted(item);
    const fallback = fallbackFor(item, this.fallback);
    if (existing) return skippedResult(item, existing, fallback);
    if (this._active) throw new VideoRunnerError('active_request_exists', 'Only one Flow video request may be active at a time', { activeItemId: itemId(this._active) });
    this._active = item;
    try {
      return await this._execute(item);
    } catch (error) {
      const normalized = errorFor(error);
      this._emit('failed', { item_id: itemId(item), code: normalized.code, result: normalized.result ?? null });
      throw normalized;
    } finally {
      this._active = null;
    }
  }

  async runItem(item) { return this.run(item); }

  async runBatch(items = []) {
    if (!Array.isArray(items)) throw new VideoRunnerError('items_must_be_array');
    const results = [];
    for (const item of items) results.push(await this.run(item));
    return deepFreeze({ schema_version: 'flow-video-batch-execution.v1', status: 'completed', results });
  }

  async runNext(queue = this.queue) {
    if (!queue?.claimNext) throw new VideoRunnerError('queue_unavailable');
    const job = await queue.claimNext();
    if (!job) return null;
    try {
      const result = await this.run(job);
      await queue.complete(job.job_id, result);
      return result;
    } catch (error) {
      const normalized = errorFor(error);
      await queue.fail(job.job_id, { code: normalized.code, message: normalized.message, credits: normalized.credits ?? null });
      throw normalized;
    }
  }
}

export function createVideoRunner(options) { return new SerialVideoRunner(options); }
export async function runVideoBatch(items, options = {}) { return createVideoRunner(options).runBatch(items); }
export const VideoRunner = SerialVideoRunner;
export const PaidVideoRunner = SerialVideoRunner;
export const runPaidVideoBatch = runVideoBatch;
