import assert from 'node:assert/strict';
import test from 'node:test';
import {
  FLOW_STATES,
  FlowStateMachine,
  FlowStateTransitionError,
} from '../extension/src/state-machine.js';

const FLOW_LOCATION = { href: 'https://labs.google/fx/project/project-001' };

function root() {
  return {
    getAttribute(name) {
      return {
        'data-flow-project-id': 'project-001',
        'data-flow-account-verified': 'true',
      }[name] ?? null;
    },
  };
}

function observation(overrides = {}) {
  return {
    ok: true,
    page: { isFlow: true },
    root: { ok: true, element: root() },
    settings: {
      open: true,
      ambiguous: false,
      unexpectedMenus: [],
      values: {
        mode: 'image',
        model: 'Nano Banana Pro 2',
        ratio: '16:9',
        duration: '4s',
        quantity: '1',
      },
    },
    prompt: { ok: true, slate: true, text: 'A verified prompt.' },
    references: { count: 0 },
    submit: { ok: true, element: {}, enabled: true },
    credit: { known: true, zero: true, paid: false, cost: 0 },
    media: { items: [], failures: [] },
    ...overrides,
  };
}

function machine(overrides = {}) {
  return new FlowStateMachine({
    location: FLOW_LOCATION,
    expected: {
      mode: 'image',
      model: 'Nano Banana Pro 2',
      ratio: '16:9',
      duration: '4s',
      quantity: '1',
      prompt: 'A verified prompt.',
      referenceCount: 0,
      projectId: 'project-001',
      zeroCredit: true,
      ...overrides,
    },
  });
}

test('state machine enumerates the locked progress and operator states', () => {
  assert.deepEqual(FLOW_STATES, [
    'wrong_page', 'project_ready', 'settings_open', 'settings_confirmed', 'prompt_ready',
    'references_attached', 'ready_to_submit', 'submitted', 'generating', 'settling',
    'completed', 'downloaded', 'blocked', 'failed', 'paused_for_operator',
  ]);
});

test('verified serial path reaches downloaded without skipping a state', () => {
  const driver = machine();
  const closed = observation({ settings: { ...observation().settings, open: false } });
  driver.advance(closed);
  assert.equal(driver.state, 'project_ready');
  driver.advance(observation());
  assert.equal(driver.state, 'settings_open');
  driver.advance(observation());
  assert.equal(driver.state, 'settings_confirmed');
  driver.advance(observation());
  assert.equal(driver.state, 'prompt_ready');
  driver.advance(observation());
  assert.equal(driver.state, 'references_attached');
  driver.advance(observation());
  assert.equal(driver.state, 'ready_to_submit');
  assert.equal(driver.submit(() => true, observation()).ok, true);
  assert.equal(driver.state, 'submitted');
  driver.recordGenerationStatus('generating', observation());
  assert.equal(driver.state, 'generating');
  driver.recordGenerationStatus('settling', observation({ media: { items: [{ id: 'new-1', status: 'generating', settled: false }], failures: [] } }));
  assert.equal(driver.state, 'settling');
  const completed = observation({ media: { items: [{ id: 'new-1', status: 'settled', settled: true, url: 'https://cdn.example/new-1.png' }], failures: [] } });
  driver.recordGenerationStatus('completed', completed);
  assert.equal(driver.state, 'completed');
  driver.recordGenerationStatus('downloaded', completed, { downloaded: true });
  assert.equal(driver.state, 'downloaded');
  assert.deepEqual(driver.history.map((event) => event.state), [
    'wrong_page', 'project_ready', 'settings_open', 'settings_confirmed', 'prompt_ready',
    'references_attached', 'ready_to_submit', 'submitted', 'generating', 'settling',
    'completed', 'downloaded',
  ]);
});

test('invalid transitions and submit-before-ready fail closed', () => {
  const driver = machine();
  assert.throws(() => driver.transition('ready_to_submit'), FlowStateTransitionError);
  let clicked = false;
  const result = driver.submit(() => { clicked = true; }, observation());
  assert.equal(result.ok, false);
  assert.equal(driver.state, 'blocked');
  assert.equal(clicked, false);
});

test('bounded zero-credit image path ignores persistent settings menus but requires prompt and main submit', () => {
  const driver = machine();
  const persistentMenu = observation({
    settings: { ...observation().settings, open: false, ambiguous: true, unexpectedMenus: [{}] },
    credit: { known: false, zero: false, paid: false, cost: null },
  });
  const armed = driver.armBoundedZeroCreditImage(persistentMenu);
  assert.equal(armed.ok, true);
  assert.equal(driver.state, 'ready_to_submit');
  let clicked = false;
  const submitted = driver.submitArmedBoundedZeroCreditImage(() => { clicked = true; });
  assert.equal(submitted.ok, true);
  assert.equal(clicked, true);
  assert.equal(driver.state, 'submitted');

  const wrongPrompt = machine();
  const blocked = wrongPrompt.armBoundedZeroCreditImage(observation({
    prompt: { ok: true, slate: true, text: 'stale prompt' },
  }));
  assert.equal(blocked.ok, false);
  assert.equal(wrongPrompt.state, 'blocked');
  assert.equal(wrongPrompt.diagnostic().code, 'prompt_readback_mismatch');
});

test('unexpected menus, ambiguous controls, disabled submit, and unknown credit block before submit', () => {
  const driver = machine();
  driver.advance(observation({ settings: { ...observation().settings, open: false } }));
  const blocked = driver.advance(observation({ settings: { ...observation().settings, ambiguous: true } }));
  assert.equal(blocked.state, 'blocked');
  assert.equal(driver.diagnostic().code, 'unexpected_menu_or_ambiguous_settings');

  const disabled = machine();
  disabled.advance(observation({ settings: { ...observation().settings, open: false } }));
  disabled.advance(observation());
  disabled.advance(observation());
  disabled.advance(observation());
  disabled.advance(observation());
  const result = disabled.advance(observation({ submit: { ok: true, element: {}, enabled: false } }), { strict: true });
  assert.equal(result.state, 'blocked');
  assert.equal(disabled.diagnostic().code, 'submit_disabled');
});

test('generation failure and operator pause are terminal review paths', () => {
  const failure = machine();
  const failed = failure.recordGenerationStatus('failed', observation({ media: { items: [], failures: [{ status: 'failed' }] } }));
  assert.equal(failed.ok, false);
  assert.equal(failure.state, 'failed');
  const paused = machine();
  assert.equal(paused.pause().state, 'paused_for_operator');
});

test('state diagnostics redact prompt, account, project, and media values', () => {
  const driver = machine({ prompt: 'account-secret prompt text', projectId: 'private-project' });
  const diagnostic = JSON.stringify(driver.block('prompt_readback_mismatch', observation({ prompt: { ok: true, slate: true, text: 'account-secret prompt text' } })));
  assert.doesNotMatch(diagnostic, /account-secret|private-project|verified prompt/);
  assert.match(diagnostic, /flow-state-diagnostic\.v1/);
  assert.equal(driver.state, 'blocked');
});

test('live identity metadata verifies the project and authenticated profile without fixture-only attributes', () => {
  const driver = machine();
  const live = observation({
    root: {
      ok: true,
      element: { getAttribute() { return null; } },
      projectId: 'project-001',
      accountVerified: true,
    },
  });
  assert.equal(driver.verifyReadyToSubmit(live).failures.some((item) => /project_mismatch|account_not_verified/.test(item.code)), false);
});

test('completed media must be new and settled before completion', () => {
  const driver = machine();
  driver.advance(observation({ settings: { ...observation().settings, open: false } }));
  driver.advance(observation());
  driver.advance(observation());
  driver.advance(observation());
  driver.advance(observation());
  driver.advance(observation());
  driver.submit(() => true, observation({ media: { items: [{ id: 'existing', settled: true }], failures: [] } }));
  driver.recordGenerationStatus('generating', observation({ media: { items: [{ id: 'existing', settled: true }], failures: [] } }));
  driver.recordGenerationStatus('settling', observation({ media: { items: [{ id: 'existing', settled: true }], failures: [] } }));
  assert.equal(driver.state, 'settling');
  driver.recordGenerationStatus('completed', observation({ media: { items: [{ id: 'existing', settled: true }, { id: 'new', settled: true }], failures: [] } }));
  assert.equal(driver.state, 'completed');
});
