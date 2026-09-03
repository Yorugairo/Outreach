import assert from 'node:assert/strict';
import test from 'node:test';

import {
  isBoundedZeroCreditImageRequest,
  readFlowPromptText,
  toPortableObservation,
} from '../extension/src/content-script.js';

test('only approved zero-credit image work uses the bounded composer path', () => {
  const request = {
    action: 'image_generation',
    requested_settings: { mode: 'image' },
    budget_policy: { kind: 'zero_credit', expected_credits: 0, max_credits: 0 },
    approval_policy: { state: 'standing_policy_approved' },
  };
  assert.equal(isBoundedZeroCreditImageRequest(request), true);
  assert.equal(isBoundedZeroCreditImageRequest({ ...request, action: 'video_generation' }), false);
  assert.equal(isBoundedZeroCreditImageRequest({ ...request, budget_policy: { kind: 'paid', expected_credits: 10, max_credits: 10 } }), false);
  assert.equal(isBoundedZeroCreditImageRequest({ ...request, approval_policy: { state: 'operator_review_required' } }), false);
});

test('Slate prompt readback excludes its visible placeholder text', () => {
  const placeholder = { remove() { this.removed = true; }, removed: false };
  const clone = {
    innerText: 'What do you want to create?\nFLOW INPUT TEST',
    querySelectorAll() {
      return [{ remove() { clone.innerText = 'FLOW INPUT TEST'; placeholder.remove(); } }];
    },
  };
  const editor = { cloneNode() { return clone; } };
  assert.equal(readFlowPromptText(editor), 'FLOW INPUT TEST');
  assert.equal(placeholder.removed, true);
});

test('content bridge strips DOM nodes, prompt text, and account labels', () => {
  const rootElement = {
    getAttribute(name) {
      return {
        'data-flow-project-id': 'project-001',
        'data-flow-account-verified': 'true',
      }[name] ?? null;
    },
  };
  const element = { nodeType: 1, secret: 'not-cloneable' };
  const portable = toPortableObservation({
    ok: true,
    selectorVersion: 'flow-selectors.v1',
    root: { ok: true, element: rootElement },
    settings: { open: true, values: { mode: 'image', model: 'Nano Banana Pro 2', ratio: '16:9', duration: null, quantity: '2' } },
    prompt: { ok: true, slate: true, text: 'private prompt body', textLength: 19, element },
    references: { count: 0, nodes: [element] },
    submit: { ok: true, enabled: true, element },
    credit: { known: true, zero: true, paid: false, cost: 0, observed: '0 credits', element },
    media: { items: [{ id: 'media-1', requestId: null, status: 'settled', url: 'https://cdn.example/one.png', settled: true, element }], failures: [] },
    page: { isFlow: true },
  }, 'https://labs.google/fx/tools/flow/project/project-001?session=secret-token#private-state');

  assert.equal(portable.root.projectId, 'project-001');
  assert.equal(portable.root.accountVerified, true);
  assert.equal(portable.prompt.textLength, 19);
  assert.equal(Object.hasOwn(portable.prompt, 'text'), false);
  assert.equal(portable.media.items[0].id, 'media-1');
  assert.equal(portable.page.url, 'https://labs.google/fx/tools/flow/project/project-001');
  const serialized = JSON.stringify(portable);
  assert.doesNotMatch(serialized, /private prompt body|not-cloneable|secret-token|private-state/);
  assert.doesNotMatch(serialized, /"element"/);
});

test('content bridge derives a project id from the redacted Flow project URL', () => {
  const rootElement = { getAttribute() { return null; } };
  const portable = toPortableObservation({
    ok: true,
    selectorVersion: 'flow-selectors.v2',
    root: { ok: true, element: rootElement },
    settings: { open: true, values: {} },
    prompt: {}, references: {}, submit: {}, credit: {}, media: {}, page: {},
  }, 'https://labs.google/fx/tools/flow/project/finance-project-001?token=secret#private');
  assert.equal(portable.root.projectId, 'finance-project-001');
  assert.equal(portable.page.url, 'https://labs.google/fx/tools/flow/project/finance-project-001');
  assert.doesNotMatch(JSON.stringify(portable), /token=secret|#private/);
});
