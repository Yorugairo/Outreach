import {
  FLOW_SELECTOR_VERSION,
  inspectFlowUI,
  normalizeSettingValue,
  normalizeWhitespace,
  readSlateEditorText,
  resolveFlowRoot,
  resolveSettings,
  resolveUnique,
} from './selectors.js';
import { FlowStateMachine, isFlowUrl, mediaIdentity } from './state-machine.js';

export const FLOW_CONTENT_SCRIPT_VERSION = 'flow-content.v1';

export function isBoundedZeroCreditImageRequest(request = {}) {
  const settings = request.requested_settings || request.settings || request;
  const budget = request.budget_policy || {};
  const approval = request.approval_policy || {};
  return request.action === 'image_generation'
    && normalizeSettingValue(settings.mode) === 'image'
    && budget.kind === 'zero_credit'
    && Number(budget.expected_credits) === 0
    && Number(budget.max_credits) === 0
    && approval.state === 'standing_policy_approved';
}

function redactPageUrl(value) {
  try {
    const parsed = new URL(String(value || ''), 'https://labs.google');
    return `${parsed.origin}${parsed.pathname}`;
  } catch {
    return null;
  }
}

function projectIdFromPageUrl(value) {
  try {
    const parsed = new URL(String(value || ''), 'https://labs.google');
    const match = parsed.pathname.match(/\/project\/([^/?#]+)/i);
    return match?.[1] ? decodeURIComponent(match[1]) : null;
  } catch {
    return null;
  }
}

function attribute(element, name) {
  try { return element?.getAttribute?.(name) ?? null; }
  catch { return null; }
}

/**
 * Chrome messages cannot structured-clone DOM nodes. Browser actions remain
 * inside this content script; only the metadata needed by the serial executor
 * and capability recorder crosses into the service worker. Prompt text and
 * account UI labels are intentionally omitted.
 */
export function toPortableObservation(observation = {}, locationLike = null) {
  const rootElement = observation.root?.element || observation.root?.root || null;
  let href = null;
  try { href = redactPageUrl(locationLike?.href || locationLike || ''); }
  catch { href = null; }
  return {
    ok: observation.ok === true,
    selectorVersion: observation.selectorVersion || FLOW_SELECTOR_VERSION,
    root: {
      ok: observation.root?.ok === true,
      projectId: attribute(rootElement, 'data-flow-project-id') || attribute(rootElement, 'data-project-id') || projectIdFromPageUrl(locationLike?.href || locationLike),
      accountVerified: attribute(rootElement, 'data-flow-account-verified') === 'true',
    },
    settings: {
      open: observation.settings?.open === true,
      ambiguous: observation.settings?.ambiguous === true,
      unexpectedMenuCount: observation.settings?.unexpectedMenus?.length || 0,
      values: { ...(observation.settings?.values || {}) },
    },
    prompt: {
      ok: observation.prompt?.ok === true,
      slate: observation.prompt?.slate === true,
      textLength: Number(observation.prompt?.textLength || 0),
    },
    references: { count: Number(observation.references?.count || 0) },
    submit: { ok: observation.submit?.ok === true, enabled: observation.submit?.enabled === true },
    credit: {
      known: observation.credit?.known === true,
      zero: observation.credit?.zero === true,
      paid: observation.credit?.paid === true,
      cost: Number.isFinite(observation.credit?.cost) ? observation.credit.cost : null,
      observed: observation.credit?.observed || null,
    },
    media: {
      items: (observation.media?.items || []).map((item) => ({
        id: item.id || null,
        requestId: item.requestId || null,
        status: item.status || null,
        url: item.url || null,
        settled: item.settled === true,
      })),
      failures: (observation.media?.failures || []).map((failure) => ({ status: failure.status || 'failed' })),
    },
    page: { ...(observation.page || {}), url: href || null },
  };
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function eventCtor(target, constructorName, eventType, init = {}) {
  const ownerWindow = target?.ownerDocument?.defaultView || globalThis.window;
  const Ctor = ownerWindow?.[constructorName] || globalThis[constructorName];
  try {
    return Ctor ? new Ctor(eventType, init) : new Event(eventType, { bubbles: true, cancelable: true });
  } catch {
    try {
      return new Event(eventType, { bubbles: true, cancelable: true });
    } catch {
      return { type: eventType, ...init };
    }
  }
}

export function readFlowPromptText(editor) {
  return readSlateEditorText(editor);
}

function editorText(editor) {
  return readFlowPromptText(editor);
}

function dispatchPromptInput(editor, text) {
  if (!editor || typeof editor.dispatchEvent !== 'function') return false;
  if (typeof editor.focus === 'function') editor.focus();
  const ownerDocument = editor.ownerDocument || (typeof document !== 'undefined' ? document : null);
  try {
    const selection = ownerDocument?.defaultView?.getSelection?.() || globalThis.getSelection?.();
    const range = ownerDocument?.createRange?.();
    if (selection && range) {
      range.selectNodeContents(editor);
      selection.removeAllRanges();
      selection.addRange(range);
    }
  } catch {
    // Selection APIs are optional in fixture documents.
  }
  try {
    if (typeof ownerDocument?.execCommand === 'function'
      && ownerDocument.execCommand('insertText', false, text) === true) {
      editor.dispatchEvent(eventCtor(editor, 'Event', 'input', { bubbles: true, composed: true }));
      editor.dispatchEvent(eventCtor(editor, 'Event', 'change', { bubbles: true, composed: true }));
      return true;
    }
  } catch {
    // Fixture documents and future browsers may not expose execCommand.
  }
  const before = eventCtor(editor, 'InputEvent', 'beforeinput', {
    bubbles: true,
    cancelable: true,
    composed: true,
    inputType: 'insertText',
    data: text,
  });
  const input = eventCtor(editor, 'InputEvent', 'input', {
    bubbles: true,
    composed: true,
    inputType: 'insertText',
    data: text,
  });
  editor.dispatchEvent(before);
  editor.dispatchEvent(input);
  editor.dispatchEvent(eventCtor(editor, 'Event', 'change', { bubbles: true, composed: true }));
  return true;
}

function optionText(element) {
  const raw = element?.getAttribute?.('data-value') || element?.getAttribute?.('aria-label') || element?.innerText || element?.textContent || '';
  return normalizeSettingValue(raw);
}

function exactOptionMatch(root, expected) {
  if (!root || typeof root.querySelectorAll !== 'function') return [];
  const options = [];
  const seen = new Set();
  for (const selector of [
    '[data-flow-option]',
    '[data-flow-setting-option]',
    '[role="option"]',
    '[role="menuitemradio"]',
    '[role="menuitem"]',
    '[role="tab"]',
  ]) {
    let found = [];
    try {
      found = [...root.querySelectorAll(selector)];
    } catch {
      continue;
    }
    for (const element of found) {
      if (seen.has(element)) continue;
      seen.add(element);
      const actual = optionText(element);
      const wanted = normalizeSettingValue(expected);
      const exact = actual === wanted;
      const semantic =
        ((wanted === 'image' || wanted === 'video') && new RegExp(`\\b${wanted}\\b`).test(actual)) ||
        (/^(?:16:9|4:3|1:1|3:4|9:16)$/.test(wanted) && actual.includes(wanted)) ||
        (/^[1-4]$/.test(wanted) && new RegExp(`\\bx${wanted}\\b`).test(actual)) ||
        (/^(?:4|6|8|10)s$/.test(wanted) && new RegExp(`\\b${wanted}\\b`).test(actual));
      if (exact || semantic) options.push(element);
    }
  }
  return options;
}

function clickElement(element) {
  if (!element || typeof element.click !== 'function') return false;
  element.click();
  return true;
}

/**
 * Resolve the live viewport centre of a control for trusted CDP mouse input.
 *
 * `Input.dispatchMouseEvent` takes CSS pixels relative to the main-frame layout
 * viewport, which is the same basis as `getBoundingClientRect()`; no
 * devicePixelRatio scaling is applied.  The visual viewport offsets are
 * reported for diagnostics only (pinch-zoom) and deliberately not added to the
 * point.
 *
 * Returns `null` when the control is missing, has no area, or is scrolled
 * outside the viewport, because an off-viewport coordinate would dispatch a
 * trusted click at whatever happens to occupy that position instead.
 */
export function elementViewportPoint(element, view = globalThis) {
  const rect = typeof element?.getBoundingClientRect === 'function'
    ? element.getBoundingClientRect()
    : null;
  if (!rect || !(rect.width > 0) || !(rect.height > 0)) return null;
  const x = rect.left + rect.width / 2;
  const y = rect.top + rect.height / 2;
  const width = Number(view?.innerWidth) || 0;
  const height = Number(view?.innerHeight) || 0;
  if (width && height && (x < 0 || y < 0 || x > width || y > height)) return null;
  const visual = view?.visualViewport;
  return {
    x: Math.round(x * 100) / 100,
    y: Math.round(y * 100) / 100,
    rect: {
      left: Math.round(rect.left * 100) / 100,
      top: Math.round(rect.top * 100) / 100,
      width: Math.round(rect.width * 100) / 100,
      height: Math.round(rect.height * 100) / 100,
    },
    devicePixelRatio: Number(view?.devicePixelRatio) || 1,
    visualViewport: visual
      ? { offsetLeft: Number(visual.offsetLeft) || 0, offsetTop: Number(visual.offsetTop) || 0, scale: Number(visual.scale) || 1 }
      : null,
  };
}

/**
 * Structural, redacted description of a control. Never includes prompt text,
 * account labels, or full node markup.
 */
export function describeControl(element) {
  if (!element) return null;
  const attr = (name) => (typeof element.getAttribute === 'function' ? element.getAttribute(name) : null);
  return {
    tag: String(element.tagName || '').toLowerCase() || null,
    role: attr('role'),
    type: attr('type'),
    ariaLabel: attr('aria-label'),
    ariaDisabled: attr('aria-disabled'),
    disabled: element.disabled === true,
    dataTestId: attr('data-testid') || attr('data-test-id'),
  };
}

/**
 * True when the point resolves to the control itself or a descendant of it.
 * Guards the case the handoff called out: Flow's settings popover stays mounted
 * and can cover the composer arrow, in which case a trusted click at the
 * arrow's centre would land on the popover.
 */
export function pointHitsElement(element, point, doc) {
  const from = doc?.elementFromPoint?.(point?.x, point?.y);
  if (!from) return { ok: false, code: 'point_not_hittable' };
  let node = from;
  while (node) {
    if (node === element) return { ok: true, code: 'point_hits_target' };
    node = node.parentElement || null;
  }
  return { ok: false, code: 'point_obscured', occluder: describeControl(from) };
}

function requestValue(settings, key) {
  if (!settings) return null;
  return settings[key] ?? (key === 'ratio' ? settings.aspectRatio : key === 'quantity' ? settings.outputs : null);
}

/**
 * Build a browser-bound driver. No listener is installed until
 * `installFlowContentScript` is called; importing this module is safe in Node
 * fixture tests and does not touch a live tab.
 */
export function createFlowContentDriver({
  document: inputDocument,
  location,
  chrome: chromeApi,
  expected = {},
  inspector = inspectFlowUI,
  machine,
  pollIntervalMs = 300,
} = {}) {
  const doc = inputDocument || (typeof document !== 'undefined' ? document : null);
  const pageLocation = location || (typeof globalThis.location !== 'undefined' ? globalThis.location : null);
  const stateMachine = machine || new FlowStateMachine({ document: doc, location: pageLocation, expected, inspector });
  stateMachine.setExpected(expected);
  let disposed = false;
  let generationObserver = null;
  let generationTimer = null;
  let confirmedSettings = null;
  let confirmedCredit = null;
  let boundedZeroCreditImageReady = false;

  const snapshot = () => {
    const observation = stateMachine.inspect();
    const projectId = projectIdFromPageUrl(pageLocation?.href || pageLocation);
    let authenticatedProfileCount = 0;
    try {
      authenticatedProfileCount = doc?.querySelectorAll?.('img[alt="User profile image"]')?.length || 0;
    } catch {
      authenticatedProfileCount = 0;
    }
    if (observation?.root?.ok) {
      // Live Flow does not expose the fixture-only data attributes. Preserve
      // equivalent evidence as observation metadata: an exact project URL and
      // one authenticated Google profile affordance in the accessible shell.
      observation.root.projectId = observation.root.projectId || projectId;
      observation.root.accountVerified = observation.root.accountVerified === true
        || (Boolean(projectId) && authenticatedProfileCount === 1);
    }
    if (!observation?.settings?.open && confirmedSettings) {
      observation.settings.values = {
        ...confirmedSettings,
        ...(observation.settings.values || {}),
      };
      for (const [key, value] of Object.entries(confirmedSettings)) {
        if (!observation.settings.values[key]) observation.settings.values[key] = value;
      }
    }
    if (!observation?.settings?.open && !observation?.credit?.known && confirmedCredit) {
      observation.credit = { ...confirmedCredit };
    }
    return observation;
  };

  async function waitUntil(predicate, timeoutMs = 2500) {
    const started = Date.now();
    while (Date.now() - started <= timeoutMs) {
      const value = snapshot();
      if (predicate(value)) return value;
      await sleep(pollIntervalMs);
    }
    return snapshot();
  }

  async function openSettings() {
    const current = snapshot();
    if (current.settings?.ambiguous || (current.settings?.unexpectedMenus?.length || 0) > 0) {
      return { ok: false, code: 'unexpected_menu_or_ambiguous_settings', diagnostic: stateMachine.block('unexpected_menu_or_ambiguous_settings', current) };
    }
    if (current.settings?.open) return { ok: true, observation: current };
    const rootResult = resolveFlowRoot(doc);
    if (!rootResult.ok) return { ok: false, code: rootResult.code, diagnostic: stateMachine.block(rootResult.code, current) };
    const trigger = current.controls?.settingsTrigger?.element
      ? current.controls.settingsTrigger
      : resolveUnique(rootResult.root, 'settingsTrigger', { required: true });
    if (!trigger.ok || !trigger.element) {
      return { ok: false, code: trigger.code || 'settings_trigger_unresolved', diagnostic: stateMachine.block(trigger.code || 'settings_trigger_unresolved', current) };
    }
    clickElement(trigger.element);
    const opened = await waitUntil((observation) => observation.settings?.open, 2500);
    if (!opened.settings?.open) {
      return { ok: false, code: 'settings_did_not_open', diagnostic: stateMachine.block('settings_did_not_open', opened) };
    }
    return { ok: true, observation: opened };
  }

  async function selectSetting(key, expectedValue) {
    if (expectedValue == null || expectedValue === '') return { ok: true, skipped: true };
    const observation = snapshot();
    const rootResult = observation.root?.ok ? observation.root : resolveFlowRoot(doc);
    if (!rootResult?.ok) return { ok: false, code: 'flow_root_not_found' };
    const controlKey = `${key}Control`;
    const observedControl = observation.controls?.[controlKey];
    const control = observedControl?.element ? observedControl : resolveUnique(rootResult.root, controlKey, { required: true });
    if (!control.ok || !control.element) return { ok: false, code: control.code || `${key}_control_unresolved` };
    const currentValue = normalizeSettingValue(observation.settings?.values?.[key] || optionText(control.element));
    if (currentValue === normalizeSettingValue(expectedValue)) return { ok: true, alreadySelected: true };
    if (!clickElement(control.element)) return { ok: false, code: `${key}_control_not_clickable` };
    const settings = resolveSettings(rootResult.root, doc);
    const roots = [settings.menu, ...settings.menuResult.candidates, ...[...doc?.querySelectorAll?.('[data-flow-overlay-root], [data-flow-portal="true"]') || []]].filter(Boolean);
    const options = [];
    const seen = new Set();
    for (const optionRoot of roots) {
      for (const option of exactOptionMatch(optionRoot, expectedValue)) {
        if (!seen.has(option)) {
          seen.add(option);
          options.push(option);
        }
      }
    }
    if (options.length !== 1) {
      return { ok: false, code: options.length ? `${key}_option_ambiguous` : `${key}_option_missing` };
    }
    clickElement(options[0]);
    const after = await waitUntil((next) => normalizeSettingValue(next.settings?.values?.[key] || '') === normalizeSettingValue(expectedValue), 2000);
    if (normalizeSettingValue(after.settings?.values?.[key] || '') !== normalizeSettingValue(expectedValue)) {
      return { ok: false, code: `${key}_readback_mismatch` };
    }
    return { ok: true, observation: after };
  }

  async function applySettings(request = expected) {
    const settings = request.settings || request;
    for (const key of ['mode', 'model', 'ratio', 'duration', 'quantity']) {
      const value = requestValue(settings, key);
      if (value == null || value === '') continue;
      const result = await selectSetting(key, value);
      if (!result.ok) return result;
    }
    const observation = snapshot();
    confirmedSettings = { ...(observation.settings?.values || {}) };
    confirmedCredit = observation.credit?.known ? { ...observation.credit } : null;
    return { ok: true, observation };
  }

  async function closeSettings() {
    const current = snapshot();
    if (!current.settings?.open) return { ok: true, alreadyClosed: true, observation: current };
    try {
      doc?.dispatchEvent?.(eventCtor(doc, 'KeyboardEvent', 'keydown', {
        key: 'Escape', code: 'Escape', bubbles: true, cancelable: true,
      }));
      doc?.dispatchEvent?.(eventCtor(doc, 'KeyboardEvent', 'keyup', {
        key: 'Escape', code: 'Escape', bubbles: true, cancelable: true,
      }));
    } catch {
      // The verified trigger fallback below handles documents without keyboard events.
    }
    let closed = await waitUntil((observation) => !observation.settings?.open, 1200);
    if (closed.settings?.open) {
      const rootResult = resolveFlowRoot(doc);
      const trigger = rootResult.ok ? resolveUnique(rootResult.root, 'settingsTrigger') : null;
      const observedTrigger = current.controls?.settingsTrigger?.element;
      const target = observedTrigger || trigger?.element || null;
      if (target) clickElement(target);
      closed = await waitUntil((observation) => !observation.settings?.open, 1800);
    }
    if (closed.settings?.open) {
      return { ok: false, code: 'settings_did_not_close', diagnostic: stateMachine.block('settings_did_not_close', closed) };
    }
    return { ok: true, observation: closed };
  }

  async function fillPrompt(prompt = expected.prompt ?? expected.promptText) {
    if (prompt == null) return { ok: true, skipped: true };
    const observation = snapshot();
    const rootResult = observation.root?.ok ? observation.root : resolveFlowRoot(doc);
    if (!rootResult?.ok) return { ok: false, code: 'flow_root_not_found' };
    const editor = resolveUnique(rootResult.root, 'promptEditor', { required: true });
    if (!editor.ok || !editor.element) return { ok: false, code: editor.code || 'prompt_editor_unresolved' };
    dispatchPromptInput(editor.element, String(prompt));
    // Slate owns its value. We only accept the operation after readback; no
    // raw `.value`/`.textContent` assignment is used as a shortcut.
    const after = await waitUntil((next) => normalizeWhitespace(next.prompt?.text || '') === normalizeWhitespace(prompt), 2500);
    if (normalizeWhitespace(after.prompt?.text || '') !== normalizeWhitespace(prompt)) {
      return { ok: false, code: 'prompt_readback_mismatch', diagnostic: stateMachine.block('prompt_readback_mismatch', after) };
    }
    return { ok: true, observation: after };
  }

  async function waitForHydratedComposer(timeoutMs = 8000) {
    return waitUntil((observation) => (
      observation.root?.ok === true
      && observation.prompt?.ok === true
      && observation.prompt?.slate === true
    ), timeoutMs);
  }

  async function focusPrompt() {
    // Flow's content script can arrive before the client has hydrated its
    // project root.  Do not treat that transient state as selector drift.
    // The bounded image lane waits only for the real Slate composer; paid
    // lanes retain their existing full state-machine validation.
    const observation = await waitForHydratedComposer();
    const rootResult = observation.root?.ok ? observation.root : resolveFlowRoot(doc);
    if (!rootResult?.ok) return { ok: false, code: 'flow_root_not_found' };
    const editor = resolveUnique(rootResult.root, 'promptEditor', { required: true });
    if (!editor.ok || !editor.element) return { ok: false, code: editor.code || 'prompt_editor_unresolved' };
    editor.element.focus?.();
    try {
      const selection = doc?.defaultView?.getSelection?.() || globalThis.getSelection?.();
      const range = doc?.createRange?.();
      if (selection && range) {
        range.selectNodeContents(editor.element);
        selection.removeAllRanges();
        selection.addRange(range);
      }
    } catch {
      return { ok: false, code: 'prompt_selection_failed' };
    }
    return { ok: true };
  }

  async function armBoundedZeroCreditImage(request = expected) {
    stateMachine.reset(request);
    boundedZeroCreditImageReady = false;
    if (!isBoundedZeroCreditImageRequest(request)) return { ok: false, code: 'bounded_image_not_eligible' };
    const observation = await waitForHydratedComposer();
    const armed = stateMachine.armBoundedZeroCreditImage(observation);
    boundedZeroCreditImageReady = armed.ok === true;
    return { ...armed, observation, diagnostic: stateMachine.diagnostic() };
  }

  async function prepare(request = expected, { strict = true } = {}) {
    stateMachine.reset(request);
    boundedZeroCreditImageReady = false;
    if (!isFlowUrl(pageLocation)) {
      const observation = snapshot();
      return { ok: false, state: stateMachine.block('wrong_page', observation), diagnostic: stateMachine.diagnostic() };
    }
    if (isBoundedZeroCreditImageRequest(request)) {
      const prompt = await fillPrompt(request.prompt ?? request.promptText);
      if (!prompt.ok) {
        return { ok: false, state: stateMachine.state, code: prompt.code, diagnostic: prompt.diagnostic || stateMachine.diagnostic() };
      }
      const observation = prompt.observation || snapshot();
      const armed = await armBoundedZeroCreditImage(request);
      boundedZeroCreditImageReady = armed.ok === true;
      return {
        ...armed,
        observation,
        diagnostic: stateMachine.diagnostic(),
      };
    }
    let observation = snapshot();
    let result = stateMachine.advance(observation, { strict });
    if (stateMachine.state === 'blocked' || stateMachine.state === 'failed') return { ok: false, state: stateMachine.state, diagnostic: stateMachine.diagnostic() };
    if (stateMachine.state === 'project_ready') {
      const opened = await openSettings();
      if (!opened.ok) return { ok: false, state: stateMachine.state, code: opened.code, diagnostic: opened.diagnostic || stateMachine.diagnostic() };
      observation = opened.observation;
      result = stateMachine.advance(observation, { strict });
    }
    if (stateMachine.state === 'settings_open') {
      const applied = await applySettings(request);
      if (!applied.ok) return { ok: false, state: stateMachine.block(applied.code, snapshot()), code: applied.code, diagnostic: stateMachine.diagnostic() };
      observation = applied.observation || snapshot();
      result = stateMachine.advance(observation, { strict });
      if (stateMachine.state === 'settings_confirmed') {
        const closed = await closeSettings();
        if (!closed.ok) return { ok: false, state: stateMachine.state, code: closed.code, diagnostic: closed.diagnostic || stateMachine.diagnostic() };
        observation = closed.observation || snapshot();
      }
    }
    if (stateMachine.state === 'settings_confirmed') {
      const prompt = await fillPrompt(request.prompt ?? request.promptText);
      if (!prompt.ok) return { ok: false, state: stateMachine.state, code: prompt.code, diagnostic: prompt.diagnostic || stateMachine.diagnostic() };
      observation = prompt.observation || snapshot();
      result = stateMachine.advance(observation, { strict });
    }
    if (stateMachine.state === 'prompt_ready') {
      observation = snapshot();
      result = stateMachine.advance(observation, { strict });
    }
    if (stateMachine.state === 'references_attached') {
      observation = snapshot();
      result = stateMachine.advance(observation, { strict });
    }
    return {
      ok: stateMachine.state === 'ready_to_submit',
      state: stateMachine.state,
      result,
      observation: stateMachine.lastObservation,
      diagnostic: stateMachine.diagnostic(),
    };
  }

  async function submit() {
    const observation = snapshot();
    const result = boundedZeroCreditImageReady
      // The arm step already verified the exact Slate value and the visible
      // main Create arrow. Commit that same button rather than running a
      // second selector pass against Flow's still-mounted settings UI.
      ? stateMachine.submitArmedBoundedZeroCreditImage((button) => clickElement(button))
      : stateMachine.submit((button) => clickElement(button), observation);
    return { ...result, diagnostic: stateMachine.diagnostic() };
  }

  /**
   * Locate the armed Create control for a trusted out-of-page click.
   *
   * Does not click and does not advance the state machine.  It captures the
   * pre-click media snapshot, because the only proof a generation started is a
   * media card that is absent here and present afterwards.
   */
  async function measureSubmitTarget() {
    const observation = stateMachine.lastObservation;
    const button = observation?.submit?.element;
    if (stateMachine.state !== 'ready_to_submit' || !button || observation.submit?.enabled !== true) {
      return { ok: false, code: 'bounded_image_not_armed', state: stateMachine.state };
    }
    if (typeof button.scrollIntoView === 'function') {
      try { button.scrollIntoView({ block: 'center', inline: 'center' }); } catch { /* non-fatal */ }
    }
    const point = elementViewportPoint(button, doc?.defaultView || globalThis);
    if (!point) return { ok: false, code: 'submit_point_unresolved', state: stateMachine.state };
    const hit = pointHitsElement(button, point, doc);
    if (!hit.ok) return { ok: false, code: hit.code, state: stateMachine.state, occluder: hit.occluder, point };
    stateMachine.captureBeforeMedia(observation);
    return {
      ok: true,
      state: stateMachine.state,
      point,
      control: describeControl(button),
      beforeMedia: [...stateMachine.beforeMedia],
    };
  }

  /**
   * Record that a trusted click was dispatched at the measured point.  The
   * click already happened out-of-page, so no submitter runs and the pre-click
   * media snapshot taken by `measureSubmitTarget` is preserved.
   */
  async function commitTrustedSubmit() {
    const result = stateMachine.submitArmedBoundedZeroCreditImage(() => true, { captureMedia: false });
    return { ...result, submitPath: 'trusted_cdp_click', diagnostic: stateMachine.diagnostic() };
  }

  function stopGenerationWait() {
    if (generationObserver?.disconnect) generationObserver.disconnect();
    generationObserver = null;
    if (generationTimer) clearInterval(generationTimer);
    generationTimer = null;
  }

  async function waitForGeneration({ timeoutMs = 300000, ackTimeoutMs = 60000, onComplete, onFailure } = {}) {
    stopGenerationWait();
    const started = Date.now();
    return await new Promise((resolve) => {
      let settled = false;
      const finish = (result) => {
        if (settled) return;
        settled = true;
        stopGenerationWait();
        resolve(result);
      };
      const check = () => {
        const observation = snapshot();
        if (observation.media?.failures?.length) {
          const result = stateMachine.recordGenerationStatus('failed', observation);
          onFailure?.(result);
          finish({ ...result, diagnostic: stateMachine.diagnostic() });
          return;
        }
        const media = observation.media?.items || [];
        const freshGenerating = media.some((item) => (
          item.status === 'generating'
          && !stateMachine.beforeMedia.has(mediaIdentity(item))
        ));
        // A clicked arrow is only a submission attempt. Do not call it
        // "generating" until Flow itself exposes a fresh busy media card.
        if (stateMachine.state === 'submitted' && freshGenerating) {
          stateMachine.recordGenerationStatus('generating', observation);
        }
        const freshSettled = media.some((item) => item.settled && !stateMachine.beforeMedia.has(mediaIdentity(item)));
        if (freshSettled) {
          const result = stateMachine.recordGenerationStatus('completed', observation);
          if (stateMachine.state === 'completed') {
            onComplete?.(result);
            finish({ ...result, diagnostic: stateMachine.diagnostic() });
          }
          return;
        }
        const elapsed = Date.now() - started;
        // Distinguish "Flow never acknowledged the click" from "generation
        // started but did not finish". The first is an input-acceptance
        // defect; the second is a slow or failed render. Collapsing both into
        // generation_timeout is what made the earlier failures unreadable.
        const acknowledged = stateMachine.state !== 'submitted'
          || freshGenerating
          || media.some((item) => !stateMachine.beforeMedia.has(mediaIdentity(item)));
        if (!acknowledged && ackTimeoutMs > 0 && elapsed >= ackTimeoutMs) {
          const result = stateMachine.fail('no_flow_ack', observation);
          onFailure?.(result);
          finish({
            ok: false,
            state: stateMachine.state,
            code: 'no_flow_ack',
            detail: 'No Flow-owned generation signal after a trusted submit click',
            elapsedMs: elapsed,
            diagnostic: result,
          });
          return;
        }
        if (elapsed >= timeoutMs) {
          const result = stateMachine.fail('generation_timeout', observation);
          onFailure?.(result);
          finish({ ok: false, state: stateMachine.state, code: 'generation_timeout', diagnostic: result });
        }
      };
      generationTimer = setInterval(check, pollIntervalMs);
      const Observer = doc?.defaultView?.MutationObserver || globalThis.MutationObserver;
      if (Observer && doc?.body) {
        generationObserver = new Observer(check);
        generationObserver.observe(doc.body, { childList: true, subtree: true, attributes: true });
      }
      check();
    });
  }

  function dispose() {
    disposed = true;
    stopGenerationWait();
  }

  async function handleMessage(message) {
    if (disposed || !message || typeof message.type !== 'string') return { ok: false, code: 'invalid_message' };
    switch (message.type) {
      case 'FLOW_UI_SNAPSHOT':
        return { ok: true, state: stateMachine.state, observation: toPortableObservation(snapshot(), pageLocation), diagnostic: stateMachine.diagnostic() };
      case 'FLOW_UI_PREPARE': {
        const result = await prepare(message.request || message, { strict: true });
        return { ...result, observation: result.observation ? toPortableObservation(result.observation, pageLocation) : undefined };
      }
      case 'FLOW_UI_FOCUS_PROMPT':
        return focusPrompt();
      case 'FLOW_UI_ARM_BOUNDED_IMAGE': {
        const result = await armBoundedZeroCreditImage(message.request || message);
        return { ...result, observation: result.observation ? toPortableObservation(result.observation, pageLocation) : undefined };
      }
      case 'FLOW_UI_MEASURE_SUBMIT':
        return measureSubmitTarget();
      case 'FLOW_UI_COMMIT_SUBMIT':
        return commitTrustedSubmit();
      case 'FLOW_UI_SUBMIT':
        return submit();
      case 'FLOW_UI_WAIT_GENERATION':
        return waitForGeneration(message);
      case 'FLOW_UI_PAUSE':
        return { ok: true, state: stateMachine.pause(), diagnostic: stateMachine.diagnostic() };
      case 'FLOW_UI_STOP':
        dispose();
        return { ok: true, state: stateMachine.state };
      default:
        return { ok: false, code: 'unknown_message_type' };
    }
  }

  return {
    version: FLOW_CONTENT_SCRIPT_VERSION,
    selectorVersion: FLOW_SELECTOR_VERSION,
    machine: stateMachine,
    snapshot,
    openSettings,
    selectSetting,
    applySettings,
    closeSettings,
    fillPrompt,
    focusPrompt,
    armBoundedZeroCreditImage,
    prepare,
    submit,
    measureSubmitTarget,
    commitTrustedSubmit,
    waitForGeneration,
    stopGenerationWait,
    handleMessage,
    dispose,
  };
}

export function installFlowContentScript(options = {}) {
  const chromeApi = options.chrome || globalThis.chrome;
  const driver = createFlowContentDriver(options);
  const listener = (message, sender, sendResponse) => {
    if (sender?.id && chromeApi?.runtime?.id && sender.id !== chromeApi.runtime.id) return undefined;
    driver.handleMessage(message).then(sendResponse).catch(() => sendResponse({ ok: false, code: 'content_script_error' }));
    return true;
  };
  chromeApi?.runtime?.onMessage?.addListener?.(listener);
  const announceReady = (attempt = 0) => {
    try {
      const ready = chromeApi?.runtime?.sendMessage?.({
        type: 'FLOW_DRIVER_CONTENT_READY',
        selectorVersion: FLOW_SELECTOR_VERSION,
      });
      Promise.resolve(ready)
        .then((response) => {
          if (response?.ok || attempt >= 5) return;
          setTimeout(() => announceReady(attempt + 1), 750);
        })
        .catch(() => {
          if (attempt < 5) setTimeout(() => announceReady(attempt + 1), 750);
        });
    } catch {
      if (attempt < 5) setTimeout(() => announceReady(attempt + 1), 750);
    }
  };
  // MV3 workers can be cold during a reload. Retrying this lightweight
  // handshake binds the already-open Flow page without opening or focusing
  // any extension UI.
  announceReady();
  return driver;
}

// A content-script bundle may call this explicitly; there is intentionally no
// import-time listener registration so Node tests and build tooling stay safe.
