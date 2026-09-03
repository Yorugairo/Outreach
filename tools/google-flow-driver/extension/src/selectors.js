/**
 * Clean-room, Flow-local selector registry.
 *
 * The content script never starts with a generic `textarea`/`contenteditable`
 * lookup.  It first resolves one explicit Flow project root and every further
 * lookup is scoped to that root (or to a deliberately marked Flow overlay).
 * Selectors are intentionally boring: stable roles, labels, and data markers
 * are preferred over generated class names or DOM positions.
 */

export const FLOW_SELECTOR_VERSION = 'flow-selectors.v2';

export const FLOW_LOCAL_ROOT_SELECTORS = Object.freeze([
  '[data-flow-root="project"]',
  '[data-flow-project-root]',
  '[data-flow-root]',
  '[data-testid="flow-project-root"]',
  '[data-testid="flow-project"]',
  '[role="main"][data-app="flow"]',
  '[role="main"][aria-label*="Flow" i]',
  '[id="__next"]',
]);

/**
 * All entries are deliberately scoped after `resolveFlowRoot` succeeds.
 * `overlayRoot` is not a page-wide portal fallback; it must carry an explicit
 * Flow marker so another app's menu cannot be mistaken for Flow settings.
 */
export const SELECTOR_REGISTRY = Object.freeze({
  settingsTrigger: Object.freeze([
    '[data-flow-settings-trigger]',
    '[data-flow-control="settings"]',
    '[aria-label="Generation settings" i]',
    '[aria-label="Open generation settings" i]',
    '[role="button"][aria-label*="settings" i]',
    'button[aria-haspopup="menu"][aria-expanded]',
  ]),
  settingsMenu: Object.freeze([
    '[data-flow-settings-menu]',
    '[data-flow-menu-kind="settings"]',
    '[role="dialog"][aria-label*="generation settings" i]',
    '[role="menu"][aria-label*="generation settings" i]',
  ]),
  overlayRoot: Object.freeze([
    '[data-flow-overlay-root]',
    '[data-flow-portal="true"]',
  ]),
  openMenu: Object.freeze([
    '[data-flow-menu][data-open="true"]',
    '[data-flow-menu-kind][data-state="open"]',
    '[role="menu"][data-state="open"]',
    '[role="dialog"][data-state="open"]',
  ]),
  modeControl: Object.freeze([
    '[data-flow-control="mode"]',
    '[data-flow-setting="mode"]',
    '[role="combobox"][aria-label*="mode" i]',
    '[aria-label="Image" i][role="button"]',
    '[aria-label="Video" i][role="button"]',
  ]),
  modelControl: Object.freeze([
    '[data-flow-control="model"]',
    '[data-flow-setting="model"]',
    '[role="combobox"][aria-label*="model" i]',
    '[aria-label="Model" i][role="button"]',
  ]),
  ratioControl: Object.freeze([
    '[data-flow-control="ratio"]',
    '[data-flow-control="aspect-ratio"]',
    '[data-flow-setting="ratio"]',
    '[data-flow-setting="aspect-ratio"]',
    '[role="combobox"][aria-label*="aspect" i]',
    '[aria-label*="aspect ratio" i][role="button"]',
  ]),
  durationControl: Object.freeze([
    '[data-flow-control="duration"]',
    '[data-flow-setting="duration"]',
    '[role="combobox"][aria-label*="duration" i]',
    '[aria-label*="duration" i][role="button"]',
  ]),
  quantityControl: Object.freeze([
    '[data-flow-control="quantity"]',
    '[data-flow-control="outputs"]',
    '[data-flow-setting="quantity"]',
    '[data-flow-setting="outputs"]',
    '[role="combobox"][aria-label*="output" i]',
    '[role="combobox"][aria-label*="quantity" i]',
    '[aria-label*="output" i][role="button"]',
  ]),
  promptEditor: Object.freeze([
    '[data-flow-prompt-editor]',
    '[data-flow-editor="prompt"]',
    '[data-slate-editor="true"][contenteditable="true"][data-flow-prompt]',
    '[data-slate-editor="true"][contenteditable="true"][aria-label*="prompt" i]',
    '[role="textbox"][contenteditable="true"][aria-label*="prompt" i]',
    '[contenteditable="true"][aria-label*="prompt" i]',
    '[role="textbox"][contenteditable="true"]',
  ]),
  referenceContainer: Object.freeze([
    '[data-flow-references]',
    '[data-flow-reference-container]',
    '[aria-label="References" i][role="group"]',
    '[aria-label*="reference" i]',
    '[data-testid*="reference"]',
    '[role="group"][aria-label*="reference" i]',
  ]),
  referenceNode: Object.freeze([
    '[data-flow-reference]',
    '[data-flow-reference-id]',
    '[data-flow-reference-item]',
    '[data-testid*="reference-item"]',
    '[data-testid*="chip"]',
    '[role="listitem"][data-reference-id]',
  ]),
  referenceInput: Object.freeze([
    'input[type="file"][accept*="image"]',
    'input[type="file"]',
    '[data-flow-file-input]',
  ]),
  referenceAddButton: Object.freeze([
    '[data-flow-add-reference]',
    'button[aria-label*="Add reference" i]',
    'button[aria-label*="Ajouter une référence" i]',
    'button[aria-label*="reference" i]',
    '[data-testid*="add-reference"]',
  ]),
  submitButton: Object.freeze([
    '[data-flow-submit]',
    '[data-flow-action="submit"]',
    '[data-testid="composer-submit"]',
    '[data-testid="generate-button"]',
    '[data-testid="create-button"]',
    'button[aria-label*="Create" i]',
    'button[aria-label*="Generate" i]',
    'button[aria-label*="Créer" i]',
    'button[aria-label*="Run" i]',
    '[aria-label="Create" i][role="button"]',
    '[aria-label="Generate" i][role="button"]',
    '[aria-label="Créer" i][role="button"]',
    'button[type="submit"][data-flow-action]',
    'button[type="submit"]',
  ]),
  creditDisplay: Object.freeze([
    '[data-flow-credit]',
    '[data-flow-cost]',
    '[aria-label*="credit" i][data-flow-label]',
    '[role="status"][aria-label*="credit" i]',
  ]),
  mediaRoot: Object.freeze([
    '[data-flow-media-grid]',
    '[data-flow-output-grid]',
    '[role="grid"][aria-label*="generated" i]',
    '[role="grid"][aria-label*="output" i]',
  ]),
  mediaItem: Object.freeze([
    '[data-flow-media-item]',
    '[data-flow-generated-media]',
    '[data-flow-media-id]',
    'img[src*="media.getMediaUrlRedirect"]',
    'img[src*="googleusercontent.com"]',
    'img[src*="blob:"]',
    '[data-testid*="media"]',
    '[data-testid*="image"]',
    '[data-testid*="card"]',
    '[role="img"]',
  ]),
  failureCard: Object.freeze([
    '[data-flow-failure]',
    '[data-flow-media-item][data-status="failed"]',
    '[role="alert"][data-flow-error]',
    '[data-flow-generation-status="failed"]',
  ]),
});

// Short aliases keep the registry convenient for the content driver and make
// the versioned contract discoverable to independent fixture tests.
export const SELECTORS = SELECTOR_REGISTRY;
export const SELECTOR_VERSION = FLOW_SELECTOR_VERSION;

const SETTINGS_KEYS = Object.freeze(['mode', 'model', 'ratio', 'duration', 'quantity']);

export class SelectorResolutionError extends Error {
  constructor(code, message, details = {}) {
    super(message);
    this.name = 'SelectorResolutionError';
    this.code = code;
    this.details = details;
  }
}

function asDocument(value) {
  if (value && typeof value.querySelectorAll === 'function') return value;
  if (typeof document !== 'undefined') return document;
  return null;
}

function asElements(root, selectors) {
  if (!root || typeof root.querySelectorAll !== 'function') return [];
  const found = [];
  const seen = new Set();
  for (const selector of selectors || []) {
    let matches = [];
    try {
      matches = [...root.querySelectorAll(selector)];
    } catch {
      // A stale browser selector must not make the driver guess another node.
      continue;
    }
    for (const element of matches) {
      if (!seen.has(element)) {
        seen.add(element);
        found.push(element);
      }
    }
  }
  return found;
}

function attr(element, name) {
  if (!element || typeof element.getAttribute !== 'function') return null;
  const value = element.getAttribute(name);
  return value == null ? null : String(value);
}

export function normalizeWhitespace(value) {
  return String(value ?? '')
    .replace(/[\u200b\ufeff]/g, '')
    .replace(/\s+/g, ' ')
    .trim();
}

export function normalizeSettingValue(value) {
  return normalizeWhitespace(value)
    .replace(/[×✕]/g, 'x')
    .replace(/\s*:\s*/g, ':')
    .toLowerCase();
}

function elementText(element) {
  return normalizeWhitespace(element?.innerText || element?.textContent || '');
}

function isHiddenByAttribute(element) {
  return element?.hidden === true || attr(element, 'hidden') !== null || attr(element, 'aria-hidden') === 'true';
}

export function isVisible(element) {
  if (!element || isHiddenByAttribute(element)) return false;
  const style = element.style;
  if (style && (style.display === 'none' || style.visibility === 'hidden')) return false;
  if (typeof globalThis.getComputedStyle === 'function') {
    try {
      const computed = globalThis.getComputedStyle(element);
      if (computed?.display === 'none' || computed?.visibility === 'hidden') return false;
    } catch {
      // Test doubles and detached nodes need not provide computed styles.
    }
  }
  return true;
}

export function isEnabled(element) {
  if (!element || isHiddenByAttribute(element)) return false;
  if (element.disabled === true) return false;
  if (attr(element, 'disabled') !== null) return false;
  if (attr(element, 'aria-disabled') === 'true') return false;
  return true;
}

function explicitRootMarker(element) {
  return Boolean(
    attr(element, 'data-flow-root') ||
      attr(element, 'data-flow-project-root') !== null ||
      attr(element, 'data-testid') === 'flow-project-root' ||
      attr(element, 'data-testid') === 'flow-project' ||
      isLiveFlowShell(element),
  );
}

function isLiveFlowShell(element) {
  if (attr(element, 'id') !== '__next') return false;
  const editors = asElements(element, [
    '[role="textbox"][contenteditable="true"]',
    '[contenteditable="true"]',
    '[data-slate-editor="true"]',
  ]);
  return editors.length >= 1;
}

function rootHasProjectMarker(element) {
  return Boolean(
    attr(element, 'data-flow-project') !== null ||
      attr(element, 'data-flow-project-id') !== null ||
      attr(element, 'data-flow-account-verified') !== null ||
      attr(element, 'data-testid')?.includes('flow-project') ||
      /project/i.test(attr(element, 'aria-label') || '') ||
      isLiveFlowShell(element),
  );
}

function uniqueElements(elements) {
  const seen = new Set();
  return elements.filter((element) => {
    if (seen.has(element)) return false;
    seen.add(element);
    return true;
  });
}

/** Resolve one explicit Flow project root. Ambiguity is a hard failure. */
export function resolveFlowRoot(inputDocument) {
  const doc = asDocument(inputDocument);
  if (!doc) {
    return { ok: false, code: 'document_unavailable', candidates: [] };
  }
  const candidates = uniqueElements(asElements(doc, FLOW_LOCAL_ROOT_SELECTORS)).filter(isVisible);
  const marked = candidates.filter(explicitRootMarker);
  const projectRoots = marked.filter(rootHasProjectMarker);
  const pool = projectRoots.length ? projectRoots : marked.length ? marked : candidates.filter(rootHasProjectMarker);
  if (pool.length === 1) {
    return { ok: true, root: pool[0], source: projectRoots.length ? 'explicit-project-root' : 'flow-landmark' };
  }
  if (pool.length > 1) {
    return {
      ok: false,
      code: 'ambiguous_flow_root',
      candidates: pool.map((element) => describeElement(element, 'flow-root')),
    };
  }
  return {
    ok: false,
    code: 'flow_root_not_found',
    candidates: candidates.map((element) => describeElement(element, 'flow-root')),
  };
}

export function getFlowRoot(inputDocument) {
  return resolveFlowRoot(inputDocument).root || null;
}

function selectorEntries(root, key) {
  const selectors = SELECTOR_REGISTRY[key];
  if (!selectors) throw new SelectorResolutionError('unknown_selector_key', `Unknown Flow selector key: ${key}`);
  return asElements(root, selectors).filter(isVisible);
}

/** Resolve exactly one control; zero or multiple matches are never guessed. */
export function resolveUnique(root, key, { required = false } = {}) {
  const candidates = selectorEntries(root, key);
  if (candidates.length === 1) return { ok: true, key, element: candidates[0], candidates };
  if (candidates.length === 0) {
    return {
      ok: !required,
      key,
      element: null,
      candidates,
      code: required ? 'selector_missing' : 'selector_optional_missing',
    };
  }
  return {
    ok: false,
    key,
    element: null,
    candidates,
    code: 'selector_ambiguous',
  };
}

function isOpen(element) {
  if (!element) return false;
  if (attr(element, 'aria-hidden') === 'true') return false;
  if (attr(element, 'data-open') === 'false' || attr(element, 'data-state') === 'closed') return false;
  return isVisible(element);
}

function resolveExplicitOverlayRoots(doc, root) {
  return uniqueElements([
    root,
    ...asElements(root, SELECTOR_REGISTRY.overlayRoot),
    ...asElements(doc, SELECTOR_REGISTRY.overlayRoot),
  ]).filter(isVisible);
}

function selectedTab(group) {
  const selected = asElements(group, [
    '[role="tab"][aria-selected="true"]',
    '[role="tab"][data-state="active"]',
  ]);
  return selected.length === 1 ? selected[0] : null;
}

function tabLabels(group) {
  return asElements(group, ['[role="tab"]']).map((element) => normalizeSettingValue(elementText(element)));
}

function tabGroupKind(group) {
  const labels = tabLabels(group);
  if (labels.length >= 2 && labels.some((value) => /\bimage\b/.test(value)) && labels.some((value) => /\bvideo\b/.test(value))) return 'mode';
  if (labels.length >= 3 && labels.filter((value) => /(?:16:9|4:3|1:1|3:4|9:16)/.test(value)).length >= 3) return 'ratio';
  if (labels.length >= 2 && labels.every((value) => /\bx[1-4]\b/.test(value))) return 'quantity';
  if (labels.length >= 2 && labels.every((value) => /\b(?:4|6|8|10)s\b/.test(value))) return 'duration';
  return null;
}

function liveSettingsMenuSignature(menu) {
  if (attr(menu, 'role') !== 'menu' || attr(menu, 'data-state') !== 'open') return false;
  const kinds = new Set(asElements(menu, ['[role="tablist"]']).map(tabGroupKind).filter(Boolean));
  const modelButtons = asElements(menu, ['button[aria-haspopup="menu"]']);
  const text = normalizeSettingValue(elementText(menu));
  return kinds.has('mode') && kinds.has('ratio') && kinds.has('quantity') && modelButtons.length === 1 && /\bcredits?\b/.test(text);
}

function liveSettingsControl(menu, key) {
  if (!menu) return null;
  if (key === 'model') {
    const buttons = asElements(menu, ['button[aria-haspopup="menu"]']);
    return buttons.length === 1 ? buttons[0] : null;
  }
  const groups = asElements(menu, ['[role="tablist"]']).filter((group) => tabGroupKind(group) === key);
  return groups.length === 1 ? selectedTab(groups[0]) : null;
}

function canonicalControlValue(element, key) {
  const raw = normalizeWhitespace(elementText(element));
  const normalized = normalizeSettingValue(raw);
  if (key === 'mode') {
    if (/\bimage\b/.test(normalized)) return 'image';
    if (/\bvideo\b/.test(normalized)) return 'video';
  }
  if (key === 'ratio') return normalized.match(/(?:16:9|4:3|1:1|3:4|9:16)/)?.[0] || raw;
  if (key === 'duration') return normalized.match(/\b(?:4|6|8|10)s\b/)?.[0] || raw;
  if (key === 'quantity') return normalized.match(/\bx([1-4])\b/)?.[1] || raw;
  if (key === 'model') {
    return raw.replace(/arrow_drop_down/gi, '').replace(/^[^\p{L}\p{N}]+/u, '').trim();
  }
  return raw;
}

function isLiveSubmitButton(element) {
  const aria = normalizeSettingValue(attr(element, 'aria-label') || '');
  if (/(?:create|generate|créer|run)/i.test(aria)) return true;
  const text = normalizeSettingValue(elementText(element));
  return /^(?:arrow_forward|arrow_upward|send|sparkle|play_arrow)?\s*(?:create|generate|créer|run)$/i.test(text)
    || /^(?:create|generate|créer|run)$/i.test(text);
}

function liveComposerSettingsTrigger(root) {
  const candidates = asElements(root, ['button[aria-haspopup="menu"][aria-expanded]'])
    .filter((element) => /\bx[1-4]\b/.test(normalizeSettingValue(elementText(element))));
  const matches = [];
  for (const candidate of candidates) {
    let ancestor = candidate.parentElement;
    for (let depth = 0; ancestor && depth < 8; depth += 1, ancestor = ancestor.parentElement) {
      const editors = asElements(ancestor, SELECTOR_REGISTRY.promptEditor);
      const submitters = asElements(ancestor, ['button']).filter(isLiveSubmitButton);
      if (editors.length === 1 && submitters.length === 1) {
        matches.push(candidate);
        break;
      }
    }
  }
  const unique = uniqueElements(matches);
  return unique.length === 1 ? unique[0] : null;
}

function findInRoots(roots, key, options = {}) {
  const candidates = uniqueElements(roots.flatMap((candidateRoot) => selectorEntries(candidateRoot, key)));
  if (candidates.length === 1) return { ok: true, key, element: candidates[0], candidates };
  if (candidates.length === 0) {
    return { ok: !options.required, key, element: null, candidates, code: options.required ? 'selector_missing' : 'selector_optional_missing' };
  }
  return { ok: false, key, element: null, candidates, code: 'selector_ambiguous' };
}

export function resolveSettings(root, inputDocument) {
  const doc = asDocument(inputDocument) || root;
  const roots = resolveExplicitOverlayRoots(doc, root);
  const declaredMenus = uniqueElements(roots.flatMap((candidateRoot) => selectorEntries(candidateRoot, 'settingsMenu')));
  const livePortalMenus = asElements(doc, ['[role="menu"][data-state="open"]']).filter(liveSettingsMenuSignature);
  const menuCandidates = uniqueElements([...declaredMenus, ...livePortalMenus]);
  const menuResult = menuCandidates.length === 1
    ? { ok: true, key: 'settingsMenu', element: menuCandidates[0], candidates: menuCandidates }
    : menuCandidates.length === 0
      ? { ok: true, key: 'settingsMenu', element: null, candidates: [], code: 'selector_optional_missing' }
      : { ok: false, key: 'settingsMenu', element: null, candidates: menuCandidates, code: 'selector_ambiguous' };
  const openMenus = uniqueElements([
    ...roots.flatMap((candidateRoot) => asElements(candidateRoot, SELECTOR_REGISTRY.openMenu)),
    ...asElements(doc, ['[role="menu"][data-state="open"]', '[role="dialog"][data-state="open"]']),
  ]).filter(isOpen);
  const expectedMenu = menuResult.element && isOpen(menuResult.element) ? menuResult.element : null;
  const unexpectedMenus = openMenus.filter((menu) => menu !== expectedMenu && !menuResult.candidates.includes(menu));
  return {
    menu: expectedMenu,
    menuResult,
    open: Boolean(expectedMenu),
    unexpectedMenus,
    ambiguous: menuResult.code === 'selector_ambiguous' || unexpectedMenus.length > 0,
  };
}

function readAttributeValue(element) {
  for (const name of ['data-value', 'data-selected-value', 'aria-valuetext', 'value']) {
    const value = attr(element, name);
    if (value) return normalizeWhitespace(value);
  }
  const selected = asElements(element, [
    '[aria-selected="true"]',
    '[data-selected="true"]',
    '[data-flow-selected="true"]',
  ]);
  if (selected.length === 1) return elementText(selected[0]);
  return elementText(element);
}

export function readControlValue(element) {
  return readAttributeValue(element);
}

function readCredit(element) {
  const raw = readAttributeValue(element);
  const lower = raw.toLowerCase();
  const costAttribute = attr(element, 'data-cost') || attr(element, 'data-credit-cost');
  const costRaw = costAttribute || raw.match(/(\d+(?:\.\d+)?)\s*credits?/i)?.[1] || raw.match(/(?:cost|credit(?:s)?)[^0-9]*(\d+(?:\.\d+)?)/i)?.[1] || null;
  const cost = costRaw == null ? null : Number(costRaw);
  const zero = cost === 0 || /free|zero\s*credit|0\s*credit/i.test(raw);
  const paid = cost != null && cost > 0;
  return { observed: raw || null, cost: Number.isFinite(cost) ? cost : null, zero, paid, known: zero || paid };
}

export function readSlateEditorText(element) {
  if (!element) return '';
  let source = element;
  try {
    const clone = element.cloneNode?.(true);
    if (clone?.querySelectorAll) {
      for (const placeholder of clone.querySelectorAll('[data-slate-placeholder="true"]')) placeholder.remove?.();
      source = clone;
    }
  } catch {
    source = element;
  }
  return normalizeWhitespace(source.innerText || source.textContent || '');
}

function resolvePrompt(root) {
  const result = resolveUnique(root, 'promptEditor', { required: true });
  if (!result.ok || !result.element) return { ...result, slate: false, text: '' };
  const element = result.element;
  const slate = attr(element, 'data-slate-editor') === 'true' || attr(element, 'data-flow-editor') === 'prompt';
  const text = readSlateEditorText(element);
  return { ...result, slate, text, textLength: text.length };
}

function resolveReferences(root) {
  const container = resolveUnique(root, 'referenceContainer');
  const referenceRoots = container.element ? [container.element] : [root];
  let nodes = uniqueElements(referenceRoots.flatMap((referenceRoot) => selectorEntries(referenceRoot, 'referenceNode')));
  if (!nodes.length && container.element) {
    // A fixture/live build may expose only the explicit count on the container.
    const declared = Number(attr(container.element, 'data-reference-count'));
    if (Number.isInteger(declared) && declared >= 0) nodes = Array.from({ length: declared }, () => container.element);
  }
  return { container, nodes, count: nodes.length };
}

function mediaId(element, index) {
  return attr(element, 'data-flow-media-id') || attr(element, 'data-media-id') || `media-${index + 1}`;
}

function mediaStatus(element) {
  const status = attr(element, 'data-status') || attr(element, 'data-flow-generation-status');
  if (status) return normalizeSettingValue(status);
  if (attr(element, 'aria-busy') === 'true') return 'generating';
  return 'settled';
}

function mediaUrl(element) {
  const direct = attr(element, 'data-media-url') || attr(element, 'src');
  if (direct) return direct;
  const child = asElements(element, ['img[src]', 'video[src]', 'source[src]'])[0];
  return child ? attr(child, 'src') : null;
}

function mediaRequestId(element) {
  return attr(element, 'data-flow-request-id') || attr(element, 'data-request-id') || attr(element, 'data-flow-item-id') || null;
}

function resolveMedia(root) {
  const mediaRoot = resolveUnique(root, 'mediaRoot');
  const roots = mediaRoot.element ? [mediaRoot.element] : [root];
  const items = uniqueElements(roots.flatMap((candidateRoot) => selectorEntries(candidateRoot, 'mediaItem')));
  const failures = uniqueElements(roots.flatMap((candidateRoot) => selectorEntries(candidateRoot, 'failureCard')));
  return {
    root: mediaRoot,
    items: items.map((element, index) => ({
      element,
      id: mediaId(element, index),
      requestId: mediaRequestId(element),
      status: mediaStatus(element),
      url: mediaUrl(element),
      settled: mediaStatus(element) === 'settled' || mediaStatus(element) === 'completed',
    })),
    failures: failures.map((element) => ({ element, status: 'failed' })),
  };
}

function resolveControls(root, settingsMenu = null) {
  const controls = {};
  for (const key of ['settingsTrigger', ...SETTINGS_KEYS.map((name) => `${name}Control`)]) {
    let result = resolveUnique(root, key, { required: false });
    if (key === 'settingsTrigger' && (!result.ok || !result.element)) {
      const liveTrigger = liveComposerSettingsTrigger(root);
      if (liveTrigger) {
        result = { ok: true, key, element: liveTrigger, candidates: [liveTrigger], source: 'live-composer-summary' };
      }
    }
    const settingName = key.endsWith('Control') ? key.slice(0, -'Control'.length) : null;
    if (settingName && (!result.element || !result.ok)) {
      const liveElement = liveSettingsControl(settingsMenu, settingName);
      if (liveElement) result = { ok: true, key, element: liveElement, candidates: [liveElement], source: 'live-settings-menu' };
    }
    controls[key] = {
      ...result,
      value: result.element ? canonicalControlValue(result.element, settingName) : null,
      enabled: result.element ? isEnabled(result.element) : false,
    };
  }
  return controls;
}

/**
 * Return a complete Flow UI observation. Raw prompt/account labels are kept in
 * the observation for verification only; call `structuralDiagnostic` for a
 * safe diagnostic payload.
 */
export function inspectFlowUI(inputDocument, { location } = {}) {
  const doc = asDocument(inputDocument);
  const rootResult = resolveFlowRoot(doc);
  if (!rootResult.ok) {
    return {
      ok: false,
      selectorVersion: FLOW_SELECTOR_VERSION,
      root: rootResult,
      controls: {},
      settings: { open: false, unexpectedMenus: [], ambiguous: false },
      prompt: { ok: false, slate: false, text: '' },
      references: { count: 0, nodes: [] },
      submit: { ok: false, element: null, enabled: false },
      credit: { known: false, zero: false, paid: false, cost: null, observed: null },
      media: { items: [], failures: [] },
      page: pageShape(location),
      diagnostic: structuralDiagnostic({ root: rootResult, page: pageShape(location) }),
    };
  }

  const root = rootResult.root;
  const settings = resolveSettings(root, doc);
  const controls = resolveControls(root, settings.menu);
  const prompt = resolvePrompt(root);
  const references = resolveReferences(root);
  let submitResult = resolveUnique(root, 'submitButton', { required: false });
  if (!submitResult.element) {
    const semanticSubmit = asElements(root, ['button']).filter(isLiveSubmitButton);
    if (semanticSubmit.length === 1) submitResult = { ok: true, key: 'submitButton', element: semanticSubmit[0], candidates: semanticSubmit, source: 'semantic-button' };
    else if (semanticSubmit.length > 1) submitResult = { ok: false, key: 'submitButton', element: null, candidates: semanticSubmit, code: 'selector_ambiguous' };
  }
  let creditResult = resolveUnique(root, 'creditDisplay', { required: false });
  if (!creditResult.element && settings.menu) {
    const credits = asElements(settings.menu, ['a']).filter((element) => /^\d+(?:\.\d+)?\s+credits?$/i.test(normalizeWhitespace(elementText(element))));
    if (credits.length === 1) creditResult = { ok: true, key: 'creditDisplay', element: credits[0], candidates: credits, source: 'live-settings-menu' };
    else if (credits.length > 1) creditResult = { ok: false, key: 'creditDisplay', element: null, candidates: credits, code: 'selector_ambiguous' };
  }
  const credit = creditResult.element ? readCredit(creditResult.element) : { known: false, zero: false, paid: false, cost: null, observed: null };
  const media = resolveMedia(root);
  const page = pageShape(location);
  return {
    ok: true,
    selectorVersion: FLOW_SELECTOR_VERSION,
    root: { ...rootResult, element: root },
    controls,
    settings: {
      ...settings,
      values: Object.fromEntries(SETTINGS_KEYS.map((name) => [name, controls[`${name}Control`]?.value || null])),
    },
    prompt,
    references,
    submit: {
      ...submitResult,
      enabled: Boolean(submitResult.element && isEnabled(submitResult.element)),
    },
    credit,
    media,
    page,
    diagnostic: structuralDiagnostic({ root: rootResult, controls, settings, prompt, references, submit: submitResult, credit, media, page }),
  };
}

export const resolveFlowSelectors = inspectFlowUI;

function pageShape(location) {
  if (!location) return { flowOrigin: null, pathDepth: null, isFlow: null };
  let parsed;
  try {
    parsed = new URL(String(location.href || location), 'https://labs.google');
  } catch {
    return { flowOrigin: null, pathDepth: null, isFlow: false };
  }
  return {
    flowOrigin: parsed.origin === 'https://labs.google' ? 'labs.google' : 'other',
    pathDepth: parsed.pathname.split('/').filter(Boolean).length,
    isFlow: parsed.origin === 'https://labs.google' && parsed.pathname.startsWith('/fx/'),
  };
}

function labelKind(value) {
  const text = normalizeSettingValue(value);
  if (!text) return null;
  if (/setting|model|ratio|aspect|duration|output|quantity|mode/.test(text)) return 'setting';
  if (/prompt|description|create|generate/.test(text)) return 'prompt-action';
  if (/reference|asset|image|video|media/.test(text)) return 'media';
  if (/credit|cost|free|quota/.test(text)) return 'billing';
  if (/project|account|workspace/.test(text)) return 'identity';
  return 'other';
}

/** A structure-only element summary. It intentionally omits text, values, ids, and URLs. */
export function describeElement(element, role = null) {
  if (!element) return null;
  const attrs = [];
  for (const name of ['data-flow-root', 'data-flow-project-root', 'data-flow-control', 'data-flow-setting', 'data-flow-menu-kind', 'data-flow-media-item', 'data-flow-failure', 'role', 'aria-expanded', 'aria-selected', 'aria-disabled', 'disabled']) {
    if (attr(element, name) !== null) attrs.push(name);
  }
  const aria = attr(element, 'aria-label');
  return {
    role,
    tag: String(element.tagName || element.nodeName || 'unknown').toLowerCase(),
    attrs: attrs.sort(),
    labelKind: labelKind(aria),
    childCount: Array.isArray(element.children) ? element.children.length : Number(element.children?.length || 0),
    textLength: elementText(element).length,
    visible: isVisible(element),
    enabled: isEnabled(element),
  };
}

function candidateStructure(value, role) {
  if (!value) return null;
  const candidates = value.candidates || [];
  return {
    key: value.key || role,
    ok: Boolean(value.ok),
    code: value.code || null,
    candidateCount: candidates.length,
    candidates: candidates.slice(0, 8).map((element) => describeElement(element, role)),
  };
}

/**
 * Build a redacted diagnostic. This is safe to persist/send to the native
 * host: prompt text, account/project values, media URLs, and arbitrary labels
 * are represented only by structure and lengths.
 */
export function structuralDiagnostic(observation = {}) {
  const controls = observation.controls || {};
  const controlSummary = Object.fromEntries(
    Object.entries(controls).map(([key, value]) => [key, candidateStructure(value, key)]),
  );
  const settings = observation.settings || {};
  const prompt = observation.prompt || {};
  const references = observation.references || {};
  const submit = observation.submit || {};
  const credit = observation.credit || {};
  const media = observation.media || {};
  return {
    schemaVersion: 'flow-structural-diagnostic.v1',
    selectorVersion: FLOW_SELECTOR_VERSION,
    page: observation.page || null,
    root: observation.root?.ok
      ? { ok: true, source: observation.root.source || null, element: describeElement(observation.root.root || observation.root.element, 'flow-root') }
      : { ok: false, code: observation.root?.code || 'flow_root_not_found', candidateCount: observation.root?.candidates?.length || 0 },
    controls: controlSummary,
    settings: {
      open: Boolean(settings.open),
      ambiguous: Boolean(settings.ambiguous),
      unexpectedMenuCount: settings.unexpectedMenus?.length || 0,
      valuesPresent: Object.fromEntries(Object.entries(settings.values || {}).map(([key, value]) => [key, Boolean(value)])),
    },
    prompt: {
      present: Boolean(prompt.element || prompt.ok),
      slate: Boolean(prompt.slate),
      textLength: Number(prompt.textLength || String(prompt.text || '').length || 0),
    },
    references: { count: Number(references.count || 0), container: candidateStructure(references.container, 'reference-container') },
    submit: {
      present: Boolean(submit.element || submit.ok),
      enabled: Boolean(submit.enabled),
      code: submit.code || null,
      candidateCount: submit.candidates?.length || 0,
    },
    credit: {
      present: Boolean(credit.known || credit.observed),
      known: Boolean(credit.known),
      zero: Boolean(credit.zero),
      paid: Boolean(credit.paid),
      hasNumericCost: Number.isFinite(credit.cost),
    },
    media: {
      itemCount: media.items?.length || 0,
      failureCount: media.failures?.length || 0,
      statuses: [...new Set((media.items || []).map((item) => item.status).filter(Boolean))].sort(),
    },
  };
}

export function describeSelectorFailure(result) {
  if (!result || result.ok) return null;
  return {
    key: result.key || null,
    code: result.code || 'selector_resolution_failed',
    candidateCount: result.candidates?.length || 0,
    candidates: (result.candidates || []).slice(0, 8).map((element) => describeElement(element, result.key || null)),
  };
}
