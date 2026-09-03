import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import test from 'node:test';
import {
  FLOW_SELECTOR_VERSION,
  inspectFlowUI,
  resolveFlowRoot,
  resolveUnique,
} from '../extension/src/selectors.js';

/** Small HTML fixture DOM; production code uses the browser DOM directly. */
class FixtureElement {
  constructor(tagName, attributes = {}, parent = null) {
    this.tagName = tagName;
    this.nodeName = tagName;
    this.attributes = attributes;
    this.parentElement = parent;
    this.children = [];
    this.ownText = '';
    this.style = {};
    this.disabled = Object.hasOwn(attributes, 'disabled');
  }

  get textContent() {
    return `${this.ownText}${this.children.map((child) => child.textContent).join('')}`;
  }

  get innerText() {
    return this.textContent;
  }

  get hidden() {
    return Object.hasOwn(this.attributes, 'hidden');
  }

  getAttribute(name) {
    return Object.hasOwn(this.attributes, name) ? this.attributes[name] : null;
  }

  hasAttribute(name) {
    return Object.hasOwn(this.attributes, name);
  }

  querySelectorAll(selector) {
    const descendants = [];
    const walk = (node) => {
      for (const child of node.children) {
        descendants.push(child);
        walk(child);
      }
    };
    walk(this);
    return descendants.filter((node) => matchesSelector(node, selector));
  }

  querySelector(selector) {
    return this.querySelectorAll(selector)[0] || null;
  }
}

class FixtureDocument extends FixtureElement {
  constructor() {
    super('#document');
  }
}

function splitSelectors(selector) {
  const out = [];
  let current = '';
  let bracketDepth = 0;
  let quote = null;
  for (const char of selector) {
    if (quote) {
      current += char;
      if (char === quote) quote = null;
      continue;
    }
    if (char === '"' || char === "'") quote = char;
    if (char === '[') bracketDepth += 1;
    if (char === ']') bracketDepth -= 1;
    if (char === ',' && bracketDepth === 0) {
      out.push(current.trim());
      current = '';
    } else {
      current += char;
    }
  }
  if (current.trim()) out.push(current.trim());
  return out;
}

function splitDescendant(selector) {
  const out = [];
  let current = '';
  let bracketDepth = 0;
  let quote = null;
  for (const char of selector.trim()) {
    if (quote) {
      current += char;
      if (char === quote) quote = null;
      continue;
    }
    if (char === '"' || char === "'") quote = char;
    if (char === '[') bracketDepth += 1;
    if (char === ']') bracketDepth -= 1;
    if (/\s/.test(char) && bracketDepth === 0) {
      if (current.trim()) out.push(current.trim());
      current = '';
    } else current += char;
  }
  if (current.trim()) out.push(current.trim());
  return out;
}

function matchesSimple(element, selector) {
  if (!selector || selector === '*') return true;
  if (selector.includes(':not(')) return false;
  const tag = selector.match(/^([a-zA-Z][\w-]*)/);
  if (tag && element.tagName.toLowerCase() !== tag[1].toLowerCase()) return false;
  const attrs = [...selector.matchAll(/\[([\w:-]+)(?:\s*([*^$~]?=)\s*(?:"([^"]*)"|'([^']*)'|([^\]\s]+)))?\s*(i)?\]/g)];
  for (const [, name, operator, doubleValue, singleValue, bareValue] of attrs) {
    const actual = element.getAttribute(name);
    if (actual == null) return false;
    if (!operator) continue;
    const expected = doubleValue ?? singleValue ?? bareValue ?? '';
    const left = operator === '*=' || operator === '^=' || operator === '$=' ? String(actual).toLowerCase() : String(actual);
    const right = operator === '*=' || operator === '^=' || operator === '$=' ? String(expected).toLowerCase() : String(expected);
    if (operator === '=' && left !== right) return false;
    if (operator === '*=' && !left.includes(right)) return false;
    if (operator === '^=' && !left.startsWith(right)) return false;
    if (operator === '$=' && !left.endsWith(right)) return false;
    if (operator === '~=' && !left.split(/\s+/).includes(right)) return false;
  }
  return true;
}

function matchesSelector(element, selector) {
  return splitSelectors(selector).some((alternative) => {
    const parts = splitDescendant(alternative);
    if (!parts.length || !matchesSimple(element, parts.at(-1))) return false;
    let ancestor = element.parentElement;
    for (let index = parts.length - 2; index >= 0; index -= 1) {
      while (ancestor && !matchesSimple(ancestor, parts[index])) ancestor = ancestor.parentElement;
      if (!ancestor) return false;
      ancestor = ancestor.parentElement;
    }
    return true;
  });
}

function parseFixture(html) {
  const document = new FixtureDocument();
  const stack = [document];
  const tokenPattern = /<!--[\s\S]*?-->|<![^>]*>|<\/?([a-zA-Z][\w-]*)([^>]*)>/g;
  let cursor = 0;
  for (const match of html.matchAll(tokenPattern)) {
    const text = html.slice(cursor, match.index);
    if (text.trim()) stack.at(-1).ownText += text;
    cursor = match.index + match[0].length;
    if (match[0].startsWith('<!--') || match[0].startsWith('<!')) continue;
    const closing = match[0].startsWith('</');
    if (closing) {
      if (stack.length > 1) stack.pop();
      continue;
    }
    const element = new FixtureElement(match[1], {}, stack.at(-1));
    const attributes = match[2] || '';
    for (const attrMatch of attributes.matchAll(/([:\w-]+)(?:\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+)))?/g)) {
      element.attributes[attrMatch[1]] = attrMatch[2] ?? attrMatch[3] ?? attrMatch[4] ?? '';
    }
    element.disabled = Object.hasOwn(element.attributes, 'disabled');
    stack.at(-1).children.push(element);
    if (!/\/\s*>$/.test(match[0]) && !['img', 'input', 'br', 'hr', 'meta', 'link'].includes(match[1].toLowerCase())) stack.push(element);
  }
  return document;
}

const fixtureRoot = process.cwd().endsWith(path.join('tools', 'google-flow-driver'))
  ? path.resolve(process.cwd(), 'tests/fixtures/flow-ui')
  : path.resolve(process.cwd(), 'tools/google-flow-driver/tests/fixtures/flow-ui');
const flowLocation = { href: 'https://labs.google/fx/project/project-001' };

async function fixture(name) {
  return parseFixture(await fs.readFile(path.join(fixtureRoot, name), 'utf8'));
}

test('selector registry resolves one Flow-local project and all requested settings', async () => {
  const document = await fixture('ready-project.html');
  const root = resolveFlowRoot(document);
  assert.equal(root.ok, true);
  const observation = inspectFlowUI(document, { location: flowLocation });
  assert.equal(observation.selectorVersion, FLOW_SELECTOR_VERSION);
  assert.equal(observation.ok, true);
  assert.equal(observation.settings.open, true);
  assert.deepEqual(observation.settings.values, {
    mode: 'image',
    model: 'Nano Banana Pro 2',
    ratio: '16:9',
    duration: '4s',
    quantity: '3',
  });
  assert.equal(observation.prompt.slate, true);
  assert.equal(observation.references.count, 2);
  assert.equal(observation.submit.enabled, true);
  assert.equal(observation.credit.zero, true);
});

test('live Flow Next shell and portaled settings popover resolve structurally', async () => {
  const document = await fixture('live-settings-popover.html');
  const root = resolveFlowRoot(document);
  assert.equal(root.ok, true);
  assert.equal(root.source, 'explicit-project-root');
  const observation = inspectFlowUI(document, {
    location: { href: 'https://labs.google/fx/tools/flow/project/finance-project-001' },
  });
  assert.equal(observation.ok, true);
  assert.equal(observation.settings.open, true);
  assert.equal(observation.settings.ambiguous, false);
  assert.deepEqual(observation.settings.values, {
    mode: 'image',
    model: 'Nano Banana Pro',
    ratio: '16:9',
    duration: null,
    quantity: '1',
  });
  assert.equal(observation.prompt.ok, true);
  assert.equal(observation.submit.enabled, true);
  assert.equal(observation.credit.known, true);
  assert.equal(observation.credit.zero, true);
  assert.equal(observation.credit.cost, 0);
});

test('settings interception is surfaced instead of selecting a global menu', async () => {
  const observation = inspectFlowUI(await fixture('settings-interception.html'), { location: flowLocation });
  assert.equal(observation.settings.ambiguous, true);
  assert.equal(observation.settings.unexpectedMenus.length, 1);
  assert.equal(observation.diagnostic.settings.unexpectedMenuCount, 1);
  assert.doesNotMatch(JSON.stringify(observation.diagnostic), /Asset picker|Unrelated/);
});

test('video settings expose exact model, ratio, duration, and quantity values', async () => {
  const observation = inspectFlowUI(await fixture('settings-video.html'), { location: flowLocation });
  assert.deepEqual(observation.settings.values, {
    mode: 'video',
    model: 'Veo 3',
    ratio: '9:16',
    duration: '8s',
    quantity: '2',
  });
  assert.equal(observation.credit.paid, true);
  assert.equal(observation.credit.cost, 4);
});

test('Slate readback, reference count, and disabled submit are observable independently', async () => {
  const prompt = inspectFlowUI(await fixture('slate-prompt.html'), { location: flowLocation });
  assert.equal(prompt.prompt.slate, true);
  assert.equal(prompt.prompt.text, 'Slate readback text');
  assert.equal(prompt.references.count, 3);
  const disabled = inspectFlowUI(await fixture('disabled-submit.html'), { location: flowLocation });
  assert.equal(disabled.submit.enabled, false);
  assert.ok(disabled.submit.element, 'disabled controls remain observable for the preflight diagnostic');
});

test('generation, failure, and completed media use explicit Flow media markers', async () => {
  const generating = inspectFlowUI(await fixture('generating.html'), { location: flowLocation });
  assert.deepEqual(generating.media.items.map((item) => item.status), ['generating']);
  const failed = inspectFlowUI(await fixture('failure.html'), { location: flowLocation });
  assert.equal(failed.media.failures.length, 1);
  const completed = inspectFlowUI(await fixture('completed-media.html'), { location: flowLocation });
  assert.deepEqual(completed.media.items.map((item) => item.id), ['new-001', 'new-002']);
  assert.equal(completed.media.items.every((item) => item.settled), true);
});

test('selector drift fails closed and diagnostics contain structure only', async () => {
  const document = await fixture('selector-drift.html');
  const observation = inspectFlowUI(document, { location: flowLocation });
  assert.equal(observation.ok, true);
  assert.equal(observation.controls.modelControl.candidates.length, 0);
  assert.equal(observation.prompt.ok, false);
  const diagnostic = JSON.stringify(observation.diagnostic);
  assert.doesNotMatch(diagnostic, /Selector drift text|project-001|Nano Banana/);
  assert.match(diagnostic, /flow-structural-diagnostic\.v1/);
});

test('ambiguous matching controls never resolve to the first candidate', async () => {
  const document = await fixture('ready-project.html');
  const root = resolveFlowRoot(document).root;
  const first = root.querySelector('[data-flow-control="model"]');
  const duplicate = new FixtureElement('button', { 'data-flow-control': 'model', 'data-value': 'Other model' }, root);
  root.children.push(duplicate);
  const result = resolveUnique(root, 'modelControl', { required: true });
  assert.equal(result.ok, false);
  assert.equal(result.code, 'selector_ambiguous');
  assert.equal(result.candidates.includes(first), true);
});
