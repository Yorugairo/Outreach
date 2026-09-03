import {
  FLOW_SELECTOR_VERSION,
  inspectFlowUI,
  normalizeSettingValue,
  normalizeWhitespace,
  structuralDiagnostic,
} from './selectors.js';

export const FLOW_STATES = Object.freeze([
  'wrong_page',
  'project_ready',
  'settings_open',
  'settings_confirmed',
  'prompt_ready',
  'references_attached',
  'ready_to_submit',
  'submitted',
  'generating',
  'settling',
  'completed',
  'downloaded',
  'blocked',
  'failed',
  'paused_for_operator',
]);

const FLOW_PROGRESS_STATES = Object.freeze(FLOW_STATES.slice(0, 12));
const OPERATOR_STATES = Object.freeze(['blocked', 'failed', 'paused_for_operator']);

export const FLOW_TRANSITIONS = Object.freeze({
  wrong_page: Object.freeze(['project_ready']),
  project_ready: Object.freeze(['settings_open']),
  settings_open: Object.freeze(['settings_confirmed']),
  settings_confirmed: Object.freeze(['prompt_ready']),
  prompt_ready: Object.freeze(['references_attached']),
  references_attached: Object.freeze(['ready_to_submit']),
  ready_to_submit: Object.freeze(['submitted']),
  submitted: Object.freeze(['generating']),
  generating: Object.freeze(['settling']),
  settling: Object.freeze(['completed']),
  completed: Object.freeze(['downloaded']),
  downloaded: Object.freeze([]),
  blocked: Object.freeze([]),
  failed: Object.freeze([]),
  paused_for_operator: Object.freeze([]),
});

export class FlowStateTransitionError extends Error {
  constructor(from, to, code = 'invalid_transition') {
    super(`Flow UI transition ${from} -> ${to} is not allowed`);
    this.name = 'FlowStateTransitionError';
    this.code = code;
    this.from = from;
    this.to = to;
  }
}

export class FlowVerificationError extends Error {
  constructor(code, message = code, details = {}) {
    super(message);
    this.name = 'FlowVerificationError';
    this.code = code;
    this.details = details;
  }
}

function nowIso(now) {
  try {
    return new Date((typeof now === 'function' ? now() : now) || Date.now()).toISOString();
  } catch {
    return new Date().toISOString();
  }
}

function valueOrNull(value) {
  return value === undefined || value === null ? null : String(value);
}

function expectedFromRequest(expected = {}) {
  const settings = expected.settings || {};
  const references = expected.references;
  const referenceCount = Number.isInteger(expected.referenceCount)
    ? expected.referenceCount
    : Array.isArray(references)
      ? references.length
      : Number.isInteger(references)
        ? references
        : 0;
  const credit = expected.credit || {};
  return {
    mode: valueOrNull(settings.mode ?? expected.mode),
    model: valueOrNull(settings.model ?? expected.model),
    ratio: valueOrNull(settings.ratio ?? settings.aspectRatio ?? expected.ratio ?? expected.aspectRatio),
    duration: valueOrNull(settings.duration ?? expected.duration),
    quantity: valueOrNull(settings.quantity ?? settings.outputs ?? expected.quantity ?? expected.outputs),
    prompt: valueOrNull(expected.prompt ?? expected.promptText),
    // Flow may expose its own request/card identifier after submission.  That
    // provider identifier is not our internal batch item ID, so never infer it
    // from itemId/batchItemId.  When Flow does not expose one, attribution is
    // established by the serial lock plus the request-local before/after media
    // snapshot.
    requestId: valueOrNull(expected.providerRequestId ?? expected.provider_request_id),
    referenceCount,
    projectId: valueOrNull(expected.projectId ?? expected.project),
    accountVerified: expected.accountVerified === undefined ? true : Boolean(expected.accountVerified),
    credit: {
      required: expected.requireCredit !== false,
      zero: Boolean(credit.zero || expected.zeroCredit),
      cost: Number.isFinite(credit.cost) ? Number(credit.cost) : Number.isFinite(expected.cost) ? Number(expected.cost) : null,
      kind: valueOrNull(credit.kind || expected.creditKind),
    },
  };
}

export function isFlowUrl(locationLike) {
  if (!locationLike) return false;
  try {
    const parsed = new URL(String(locationLike.href || locationLike), 'https://labs.google');
    return parsed.origin === 'https://labs.google' && parsed.pathname.startsWith('/fx/');
  } catch {
    return false;
  }
}

export function allowedTransition(from, to) {
  if (!FLOW_STATES.includes(from) || !FLOW_STATES.includes(to)) return false;
  if (OPERATOR_STATES.includes(to)) return true;
  return FLOW_TRANSITIONS[from]?.includes(to) || false;
}

function compactExpected(expected) {
  return Object.fromEntries(
    Object.entries(expected || {})
      .filter(([key]) => !['prompt', 'projectId'].includes(key))
      .map(([key, value]) => [key, typeof value === 'string' ? { present: Boolean(value), length: value.length } : value]),
  );
}

function settingMismatch(observation, expected) {
  const mismatches = [];
  const values = observation.settings?.values || {};
  for (const key of ['mode', 'model', 'ratio', 'duration', 'quantity']) {
    const want = expected[key];
    if (want == null || want === '') continue;
    const got = values[key];
    if (!got || normalizeSettingValue(got) !== normalizeSettingValue(want)) {
      mismatches.push({ code: `setting_${key}_mismatch`, expectedPresent: true, observedPresent: Boolean(got) });
    }
  }
  return mismatches;
}

function rootAttribute(root, name) {
  return root && typeof root.getAttribute === 'function' ? root.getAttribute(name) : null;
}

function verifyIdentity(observation, expected) {
  const mismatches = [];
  const root = observation.root?.element || observation.root?.root;
  if (!root) return [{ code: 'flow_project_root_missing' }];
  const observedProjectId = observation.root?.projectId || rootAttribute(root, 'data-flow-project-id');
  const observedAccountVerified = observation.root?.accountVerified === true
    || rootAttribute(root, 'data-flow-account-verified') === 'true';
  if (expected.projectId != null && String(observedProjectId || '') !== expected.projectId) {
    mismatches.push({ code: 'project_mismatch' });
  }
  if (expected.accountVerified && !observedAccountVerified) {
    mismatches.push({ code: 'account_not_verified' });
  }
  return mismatches;
}

function verifyCredit(observation, expected) {
  const credit = observation.credit || {};
  if (!expected.credit.required) return [];
  if (!credit.known) return [{ code: 'credit_unknown' }];
  if (expected.credit.zero && (!credit.zero || credit.cost !== 0)) return [{ code: 'credit_not_zero' }];
  if (expected.credit.cost != null && credit.cost !== expected.credit.cost) return [{ code: 'credit_cost_changed' }];
  if (expected.credit.kind === 'zero' && !credit.zero) return [{ code: 'credit_kind_changed' }];
  if (expected.credit.kind === 'paid' && !credit.paid) return [{ code: 'credit_kind_changed' }];
  return [];
}

export function mediaIdentity(item) {
  const id = String(item?.id || '');
  const url = String(item?.url || '');
  if (id && url) return `${id}|${url}`;
  return id || url;
}

function settledNewMedia(observation, beforeMedia = new Set()) {
  const items = observation.media?.items || [];
  return items.filter((item) => item.settled && mediaIdentity(item) && !beforeMedia.has(mediaIdentity(item)));
}

function attributableMedia(items, expected) {
  if (!expected.requestId) return items;
  return items.filter((item) => item.requestId && String(item.requestId) === String(expected.requestId));
}

function structuralStateDiagnostic(state, code, observation, expected) {
  return {
    ...structuralDiagnostic(observation || {}),
    schemaVersion: 'flow-state-diagnostic.v1',
    selectorVersion: FLOW_SELECTOR_VERSION,
    state,
    code,
    expected: compactExpected(expected),
  };
}

/**
 * Explicit, fail-closed state machine for one serial Flow item. It is
 * dependency-free and accepts a document-like object so fixture tests can run
 * without a browser or a DOM package.
 */
export class FlowStateMachine {
  constructor({ document: inputDocument, location, expected = {}, inspector = inspectFlowUI, now = Date.now } = {}) {
    this.document = inputDocument || (typeof document !== 'undefined' ? document : null);
    this.location = location || (typeof globalThis.location !== 'undefined' ? globalThis.location : null);
    this.inspector = inspector;
    this.now = now;
    this.expected = expectedFromRequest(expected);
    this.state = 'wrong_page';
    this.history = [];
    this.lastObservation = null;
    this.lastDiagnostic = null;
    this.beforeMedia = new Set();
    this._record('wrong_page', 'initial', null);
  }

  setExpected(expected = {}) {
    this.expected = expectedFromRequest({ ...this.expected, ...expected, settings: { ...this.expected, ...(expected.settings || {}) } });
    return this.expected;
  }

  reset(expected = {}) {
    this.expected = expectedFromRequest(expected);
    this.state = 'wrong_page';
    this.history = [];
    this.lastObservation = null;
    this.lastDiagnostic = null;
    this.beforeMedia = new Set();
    this._record('wrong_page', 'reset', null);
    return this.state;
  }

  inspect(observation = null) {
    if (observation) {
      this.lastObservation = observation;
      return observation;
    }
    try {
      this.lastObservation = this.inspector(this.document, { location: this.location });
    } catch {
      this.lastObservation = { ok: false, page: { isFlow: isFlowUrl(this.location) }, root: { ok: false, code: 'selector_inspection_failed' } };
    }
    return this.lastObservation;
  }

  _record(state, code, observation) {
    this.history.push({ state, code, at: nowIso(this.now), diagnostic: observation ? structuralStateDiagnostic(state, code, observation, this.expected) : null });
  }

  transition(next, { code = 'verified', observation = this.lastObservation } = {}) {
    if (!allowedTransition(this.state, next)) throw new FlowStateTransitionError(this.state, next);
    this.state = next;
    this.lastDiagnostic = observation ? structuralStateDiagnostic(next, code, observation, this.expected) : { state: next, code };
    this._record(next, code, observation);
    return this.state;
  }

  _operatorTransition(next, code, observation) {
    if (!OPERATOR_STATES.includes(next)) throw new FlowStateTransitionError(this.state, next);
    this.state = next;
    this.lastDiagnostic = structuralStateDiagnostic(next, code, observation || this.lastObservation || {}, this.expected);
    this._record(next, code, observation || this.lastObservation || {});
    return this.state;
  }

  verifyReadyToSubmit(observation = this.inspect()) {
    const failures = [];
    if (!isFlowUrl(this.location) && observation.page?.isFlow !== true) failures.push({ code: 'wrong_page' });
    if (!observation.ok || !observation.root?.ok) failures.push({ code: observation.root?.code || 'flow_root_not_found' });
    failures.push(...verifyIdentity(observation, this.expected));
    if (observation.settings?.ambiguous || (observation.settings?.unexpectedMenus?.length || 0) > 0) {
      failures.push({ code: 'unexpected_menu_or_ambiguous_settings' });
    }
    failures.push(...settingMismatch(observation, this.expected));
    const prompt = observation.prompt || {};
    if (!prompt.ok || !prompt.slate) failures.push({ code: 'slate_prompt_not_ready' });
    if (this.expected.prompt != null && normalizeWhitespace(prompt.text) !== normalizeWhitespace(this.expected.prompt)) {
      failures.push({ code: 'prompt_readback_mismatch' });
    }
    if (observation.references?.count !== this.expected.referenceCount) {
      failures.push({ code: 'reference_count_mismatch' });
    }
    if (!observation.submit?.ok || !observation.submit?.element) failures.push({ code: 'submit_selector_unresolved' });
    if (!observation.submit?.enabled) failures.push({ code: 'submit_disabled' });
    failures.push(...verifyCredit(observation, this.expected));
    return {
      ok: failures.length === 0,
      failures,
      observation,
      diagnostic: structuralStateDiagnostic(this.state, failures[0]?.code || 'ready_to_submit', observation, this.expected),
    };
  }

  canSubmit(observation = this.inspect()) {
    return this.verifyReadyToSubmit(observation);
  }

  /**
   * Narrow fast path for an already-approved zero-credit image request.
   * Flow's settings popover is persistent and may coexist with unrelated
   * menus, so image execution verifies only identity, exact prompt readback,
   * reference count, and the main composer submit control. Paid/video work
   * continues to use verifyReadyToSubmit().
   */
  verifyBoundedZeroCreditImage(observation = this.inspect()) {
    const failures = [];
    if (!isFlowUrl(this.location) && observation.page?.isFlow !== true) failures.push({ code: 'wrong_page' });
    if (!observation.root?.ok) failures.push({ code: observation.root?.code || 'flow_root_not_found' });
    failures.push(...verifyIdentity(observation, this.expected));
    const prompt = observation.prompt || {};
    if (!prompt.ok || !prompt.slate) failures.push({ code: 'slate_prompt_not_ready' });
    if (this.expected.prompt != null && normalizeWhitespace(prompt.text) !== normalizeWhitespace(this.expected.prompt)) {
      failures.push({ code: 'prompt_readback_mismatch' });
    }
    if (observation.references?.count !== this.expected.referenceCount) failures.push({ code: 'reference_count_mismatch' });
    if (!observation.submit?.ok || !observation.submit?.element) failures.push({ code: 'submit_selector_unresolved' });
    if (!observation.submit?.enabled) failures.push({ code: 'submit_disabled' });
    return {
      ok: failures.length === 0,
      failures,
      observation,
      diagnostic: structuralStateDiagnostic(this.state, failures[0]?.code || 'bounded_zero_credit_image_ready', observation, this.expected),
    };
  }

  armBoundedZeroCreditImage(observation = this.inspect()) {
    this.lastObservation = observation;
    const ready = this.verifyBoundedZeroCreditImage(observation);
    if (!ready.ok) {
      this._operatorTransition('blocked', ready.failures[0]?.code || 'bounded_image_not_ready', observation);
      return { ok: false, state: this.state, failures: ready.failures, diagnostic: this.lastDiagnostic };
    }
    this.state = 'ready_to_submit';
    this.lastDiagnostic = structuralStateDiagnostic(this.state, 'bounded_zero_credit_image_ready', observation, this.expected);
    this._record(this.state, 'bounded_zero_credit_image_ready', observation);
    return { ok: true, state: this.state, diagnostic: this.lastDiagnostic };
  }

  submitBoundedZeroCreditImage(submitter, observation = this.inspect()) {
    const ready = this.verifyBoundedZeroCreditImage(observation);
    if (!ready.ok) {
      this._operatorTransition('blocked', ready.failures[0]?.code || 'bounded_image_submit_failed', observation);
      return { ok: false, state: this.state, failures: ready.failures, diagnostic: this.lastDiagnostic };
    }
    this.captureBeforeMedia(observation);
    try {
      const result = typeof submitter === 'function' ? submitter(observation.submit.element) : undefined;
      if (result === false) throw new FlowVerificationError('submit_action_failed');
    } catch {
      this._operatorTransition('failed', 'submit_action_failed', observation);
      return { ok: false, state: this.state, diagnostic: this.lastDiagnostic };
    }
    this.state = 'submitted';
    this.lastObservation = observation;
    this.lastDiagnostic = structuralStateDiagnostic(this.state, 'bounded_zero_credit_image_submitted', observation, this.expected);
    this._record(this.state, 'bounded_zero_credit_image_submitted', observation);
    return { ok: true, state: this.state, beforeMedia: [...this.beforeMedia] };
  }

  /**
   * Commit a bounded zero-credit image request that was just armed against a
   * verified Slate prompt and the live main Create control.  Flow keeps its
   * settings popover mounted, and a second full selector pass between arm and
   * click can observe a transient app shell instead of the already-verified
   * composer.  This method intentionally reuses that exact armed observation;
   * it is not available to paid or video work.
   */
  submitArmedBoundedZeroCreditImage(submitter, { captureMedia = true } = {}) {
    const observation = this.lastObservation;
    if (this.state !== 'ready_to_submit' || !observation?.submit?.element || !observation.submit?.enabled) {
      this._operatorTransition('blocked', 'bounded_image_not_armed', observation || this.inspect());
      return { ok: false, state: this.state, diagnostic: this.lastDiagnostic };
    }
    // A trusted out-of-page click (CDP) is dispatched before this commit, so the
    // pre-click media snapshot is taken by the caller.  Re-capturing here would
    // fold a card Flow created in response to that click into `beforeMedia` and
    // permanently hide the only evidence that a generation started.
    if (captureMedia) this.captureBeforeMedia(observation);
    try {
      const result = typeof submitter === 'function' ? submitter(observation.submit.element) : undefined;
      if (result === false) throw new FlowVerificationError('submit_action_failed');
    } catch {
      this._operatorTransition('failed', 'submit_action_failed', observation);
      return { ok: false, state: this.state, diagnostic: this.lastDiagnostic };
    }
    this.state = 'submitted';
    this.lastDiagnostic = structuralStateDiagnostic(this.state, 'bounded_zero_credit_image_submitted', observation, this.expected);
    this._record(this.state, 'bounded_zero_credit_image_submitted', observation);
    return { ok: true, state: this.state, beforeMedia: [...this.beforeMedia] };
  }

  captureBeforeMedia(observation = this.inspect()) {
    this.beforeMedia = new Set((observation.media?.items || []).map(mediaIdentity).filter(Boolean));
    return [...this.beforeMedia];
  }

  /** Advance one verified edge; no action is inferred for a missing control. */
  advance(observation = this.inspect(), { strict = false } = {}) {
    this.lastObservation = observation;
    if (!isFlowUrl(this.location) && observation.page?.isFlow !== true) {
      if (this.state !== 'wrong_page') this._operatorTransition('blocked', 'wrong_page', observation);
      return { state: this.state, progressed: false, code: 'wrong_page' };
    }
    if (!observation.ok || !observation.root?.ok) {
      if (this.state !== 'wrong_page') this._operatorTransition('blocked', observation.root?.code || 'flow_root_not_found', observation);
      return { state: this.state, progressed: false, code: observation.root?.code || 'flow_root_not_found' };
    }
    if (observation.settings?.ambiguous || (observation.settings?.unexpectedMenus?.length || 0) > 0) {
      this._operatorTransition('blocked', 'unexpected_menu_or_ambiguous_settings', observation);
      return { state: this.state, progressed: false, code: 'unexpected_menu_or_ambiguous_settings' };
    }

    switch (this.state) {
      case 'wrong_page':
        this.transition('project_ready', { code: 'flow_project_verified', observation });
        break;
      case 'project_ready':
        if (observation.settings?.open) this.transition('settings_open', { code: 'settings_menu_open', observation });
        else return { state: this.state, progressed: false, code: 'settings_not_open' };
        break;
      case 'settings_open': {
        const mismatches = [...verifyIdentity(observation, this.expected), ...settingMismatch(observation, this.expected)];
        if (mismatches.length) {
          if (strict && mismatches.some((item) => item.code === 'account_not_verified' || item.code === 'project_mismatch')) {
            this._operatorTransition('blocked', mismatches[0].code, observation);
          }
          return { state: this.state, progressed: false, code: mismatches[0].code, failures: mismatches };
        }
        this.transition('settings_confirmed', { code: 'settings_verified', observation });
        break;
      }
      case 'settings_confirmed': {
        const prompt = observation.prompt || {};
        if (!prompt.ok || !prompt.slate) return { state: this.state, progressed: false, code: 'slate_prompt_missing' };
        if (this.expected.prompt != null && normalizeWhitespace(prompt.text) !== normalizeWhitespace(this.expected.prompt)) {
          if (strict && prompt.text) this._operatorTransition('blocked', 'prompt_readback_mismatch', observation);
          return { state: this.state, progressed: false, code: 'prompt_readback_pending' };
        }
        this.transition('prompt_ready', { code: 'slate_prompt_verified', observation });
        break;
      }
      case 'prompt_ready':
        if (observation.references?.count !== this.expected.referenceCount) return { state: this.state, progressed: false, code: 'reference_count_pending' };
        this.transition('references_attached', { code: 'references_verified', observation });
        break;
      case 'references_attached': {
        const ready = this.verifyReadyToSubmit(observation);
        if (!ready.ok) {
          const hardFailure = ready.failures.some((item) => /ambiguous|unexpected|disabled|unknown|changed|unresolved|wrong_page/.test(item.code));
          if (hardFailure || strict) this._operatorTransition('blocked', ready.failures[0].code, observation);
          return { state: this.state, progressed: false, code: ready.failures[0]?.code || 'submit_not_ready', failures: ready.failures };
        }
        this.transition('ready_to_submit', { code: 'submit_preflight_verified', observation });
        break;
      }
      default:
        return { state: this.state, progressed: false, code: 'no_automatic_transition' };
    }
    return { state: this.state, progressed: true, code: 'verified_transition' };
  }

  submit(submitter, observation = this.inspect()) {
    if (this.state !== 'ready_to_submit') {
      this._operatorTransition('blocked', 'submit_called_before_ready', observation);
      return { ok: false, state: this.state, diagnostic: this.lastDiagnostic };
    }
    const ready = this.verifyReadyToSubmit(observation);
    if (!ready.ok) {
      this._operatorTransition('blocked', ready.failures[0]?.code || 'submit_preflight_failed', observation);
      return { ok: false, state: this.state, failures: ready.failures, diagnostic: this.lastDiagnostic };
    }
    this.captureBeforeMedia(observation);
    try {
      const result = typeof submitter === 'function' ? submitter(observation.submit.element) : undefined;
      if (result === false) throw new FlowVerificationError('submit_action_failed');
    } catch (error) {
      this._operatorTransition('failed', 'submit_action_failed', observation);
      return { ok: false, state: this.state, diagnostic: this.lastDiagnostic };
    }
    this.transition('submitted', { code: 'submit_clicked', observation });
    return { ok: true, state: this.state, beforeMedia: [...this.beforeMedia] };
  }

  recordGenerationStatus(status, observation = this.inspect(), { downloaded = false } = {}) {
    this.lastObservation = observation;
    const normalized = normalizeSettingValue(status);
    if (normalized === 'failed' || (observation.media?.failures?.length || 0) > 0) {
      this._operatorTransition('failed', 'generation_failed', observation);
      return { ok: false, state: this.state, code: 'generation_failed', diagnostic: this.lastDiagnostic };
    }
    if (normalized === 'paused' || normalized === 'paused_for_operator') {
      this._operatorTransition('paused_for_operator', 'operator_pause', observation);
      return { ok: true, state: this.state, code: 'operator_pause' };
    }
    if (this.state === 'submitted' && normalized === 'generating') {
      this.transition('generating', { code: 'generation_started', observation });
    } else if (this.state === 'generating' && (normalized === 'settling' || normalized === 'completed')) {
      this.transition('settling', { code: 'new_media_observed', observation });
    }
    const newMedia = attributableMedia(settledNewMedia(observation, this.beforeMedia), this.expected);
    if (this.state === 'settling' && (normalized === 'completed' || newMedia.length > 0) && newMedia.length > 0) {
      this.transition('completed', { code: 'new_media_settled', observation });
    }
    if (this.state === 'completed' && (downloaded || normalized === 'downloaded')) {
      this.transition('downloaded', { code: 'download_verified', observation });
    }
    return { ok: true, state: this.state, newMediaCount: newMedia.length };
  }

  block(code = 'operator_review_required', observation = this.inspect()) {
    this._operatorTransition('blocked', code, observation);
    return this.lastDiagnostic;
  }

  fail(code = 'flow_driver_failed', observation = this.inspect()) {
    this._operatorTransition('failed', code, observation);
    return this.lastDiagnostic;
  }

  pause(observation = this.inspect()) {
    this._operatorTransition('paused_for_operator', 'operator_pause', observation);
    return this.lastDiagnostic;
  }

  diagnostic() {
    return this.lastDiagnostic || structuralStateDiagnostic(this.state, 'no_diagnostic', this.lastObservation || {}, this.expected);
  }
}

export function createFlowStateMachine(options) {
  return new FlowStateMachine(options);
}
