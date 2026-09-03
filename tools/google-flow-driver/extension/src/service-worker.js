import { createImageRunner } from './image-runner.js';
import { createVideoRunner, FLOW_VIDEO_ACTIONS } from './video-runner.js';
import { buildCapabilitySnapshot } from './capability-capture.js';

const FLOW_STATE_KEY = 'flowDriverUiState';
const FLOW_NATIVE_HOST_NAME = 'com.outreach.flow_driver';
const HEARTBEAT_INTERVAL_MS = 8000;
const HEARTBEAT_TIMEOUT_MS = 3500;
const INITIAL_RECONNECT_MS = 1500;
const MAX_RECONNECT_MS = 30000;

const DEFAULT_STATE = Object.freeze({
  schemaVersion: 1,
  connection: {
    host: {
      connected: false,
      lastConnectedAt: null,
      lastError: null,
      reconnectAttempts: 0,
    },
    heartbeat: {
      status: 'disconnected',
      at: null,
      latencyMs: null,
      error: null,
    },
  },
  queue: {
    paused: false,
    counts: {
      pending: 0,
      active: 0,
      completed: 0,
      failed: 0,
      cancelled: 0,
    },
    activeJobId: null,
    activeManifest: null,
    lastUpdateAt: null,
  },
  panel: {
    connected: false,
    lastVisibleAt: null,
    clientId: null,
    lastHeartbeat: null,
  },
  diagnostics: {
    enabled: true,
    lastCaptureAt: null,
    lastAction: null,
    lastPayload: null,
  },
  meta: {
    extensionVersion: null,
    pluginName: 'flow-driver-shell',
  },
});

let heartbeatTimer = null;
let nativePort = null;
let reconnectTimer = null;
let reconnectDelayMs = INITIAL_RECONNECT_MS;
let nextRequestId = 0;
const pendingNativeRequests = new Map();
let flowTabId = null;
let executionPromise = null;

function nowIso() {
  return new Date().toISOString();
}

function mergeObjects(base, patch) {
  if (!patch || typeof patch !== 'object' || Array.isArray(patch)) {
    return base;
  }
  const out = { ...base };
  for (const [key, value] of Object.entries(patch)) {
    if (value && typeof value === 'object' && !Array.isArray(value)) {
      out[key] = mergeObjects(out[key] ?? {}, value);
    } else {
      out[key] = value;
    }
  }
  return out;
}

function normalizeState(rawState = {}) {
  const copy = structuredClone(rawState);
  return mergeObjects(structuredClone(DEFAULT_STATE), copy);
}

async function readState() {
  const stored = await chrome.storage.local.get(FLOW_STATE_KEY);
  return normalizeState(stored[FLOW_STATE_KEY]);
}

async function writeState(mutator) {
  const current = await readState();
  const patch = typeof mutator === 'function' ? mutator(structuredClone(current)) : mutator;
  const next = mergeObjects(current, patch);
  if (next.meta?.extensionVersion == null) {
    next.meta = { ...next.meta, extensionVersion: chrome.runtime.getManifest()?.version || null };
  }
  await chrome.storage.local.set({ [FLOW_STATE_KEY]: normalizeState(next) });
  return readState();
}

async function readManifestVersion() {
  return chrome.runtime.getManifest()?.version || null;
}

function serializeError(error) {
  if (!error) return null;
  if (error instanceof Error) {
    return {
      name: error.name,
      message: error.message,
      code: error.code,
      details: error.details || null,
      result: error.result || null,
    };
  }
  if (typeof error === 'string') return { name: 'Error', message: error };
  return {
    name: error.name || 'Error',
    message: String(error.message || error),
  };
}

function connectNativePort() {
  if (nativePort) return;
  if (reconnectTimer) {
    clearTimeout(reconnectTimer);
    reconnectTimer = null;
  }

  try {
    nativePort = chrome.runtime.connectNative(FLOW_NATIVE_HOST_NAME);
  } catch (error) {
    nativePort = null;
    throw error;
  }

  nativePort.onMessage.addListener((rawMessage) => {
    if (!rawMessage || typeof rawMessage.request_id !== 'string') return;
    const pending = pendingNativeRequests.get(rawMessage.request_id);
    if (!pending) return;
    clearTimeout(pending.timer);
    pendingNativeRequests.delete(rawMessage.request_id);
    if (typeof rawMessage !== 'object') {
      pending.reject(new Error('invalid native response'));
      return;
    }
    pending.resolve({
      ...rawMessage,
      latencyMs: Math.max(1, Math.round(performance.now() - pending.startedAt)),
    });
  });

  nativePort.onDisconnect.addListener(() => {
    const disconnectError = new Error(chrome.runtime.lastError?.message || 'native port disconnected');
    const portRequests = [...pendingNativeRequests.entries()];
    pendingNativeRequests.clear();
    for (const [, pending] of portRequests) {
      clearTimeout(pending.timer);
      pending.reject(disconnectError);
    }
    nativePort = null;
    writeState((state) => ({
      connection: {
        host: {
          connected: false,
          lastError: serializeError(disconnectError),
          reconnectAttempts: (state.connection.host.reconnectAttempts || 0) + 1,
        },
        heartbeat: {
          status: 'disconnected',
          at: nowIso(),
          latencyMs: null,
          error: serializeError(disconnectError),
        },
      },
    })).catch(() => {});
    if (!reconnectTimer) {
      reconnectTimer = setTimeout(() => {
        reconnectTimer = null;
        reconnectDelayMs = Math.min(reconnectDelayMs * 2, MAX_RECONNECT_MS);
        try {
          connectNativePort();
        } catch (error) {
          writeState({
            connection: {
              host: {
                connected: false,
                lastError: serializeError(error),
                reconnectAttempts: 1,
              },
            },
          }).catch(() => {});
        }
      }, reconnectDelayMs);
    }
  });
  reconnectDelayMs = INITIAL_RECONNECT_MS;
}

async function sendNativeRequest(message, { timeoutMs = HEARTBEAT_TIMEOUT_MS } = {}) {
  const requestId = `${Date.now().toString(36)}_${nextRequestId++}`;
  const payload = { request_id: requestId, ...message };
  const startedAt = performance.now();

  if (!nativePort) {
    try {
      connectNativePort();
    } catch (error) {
      writeState((state) => ({
        connection: {
          host: {
            connected: false,
            lastError: serializeError(error),
            reconnectAttempts: (state.connection.host.reconnectAttempts || 0) + 1,
          },
          heartbeat: {
            status: 'disconnected',
            at: nowIso(),
            latencyMs: null,
            error: serializeError(error),
          },
        },
      })).catch(() => {});
      throw error;
    }
  }

  return await new Promise((resolve, reject) => {
    const timer = setTimeout(() => {
      const error = new Error(`native messaging request ${requestId} timed out`);
      pendingNativeRequests.delete(requestId);
      writeState((state) => ({
        connection: {
          host: {
            connected: false,
            reconnectAttempts: (state.connection.host.reconnectAttempts || 0) + 1,
            lastError: serializeError(error),
          },
          heartbeat: {
            status: 'disconnected',
            at: nowIso(),
            latencyMs: null,
            error: serializeError(error),
          },
        },
      })).catch(() => {});
      reject(error);
    }, timeoutMs);
    pendingNativeRequests.set(requestId, {
      startedAt,
      timer,
      resolve: (response) => {
        writeState((state) => ({
          connection: {
            host: {
              connected: true,
              lastError: null,
              reconnectAttempts: state.connection.host.reconnectAttempts || 0,
            },
          },
        })).catch(() => {});
        resolve(response);
      },
      reject: (error) => {
        writeState((state) => ({
          connection: {
            host: {
              connected: false,
              lastError: serializeError(error),
              reconnectAttempts: (state.connection.host.reconnectAttempts || 0) + 1,
            },
            heartbeat: {
              status: 'disconnected',
              at: nowIso(),
              latencyMs: null,
              error: serializeError(error),
            },
          },
        })).catch(() => {});
        reject(error);
      },
    });

    try {
      nativePort.postMessage(payload);
    } catch (error) {
      pendingNativeRequests.delete(requestId);
      clearTimeout(timer);
      writeState((state) => ({
        connection: {
          host: {
            connected: false,
            lastError: serializeError(error),
            reconnectAttempts: (state.connection.host.reconnectAttempts || 0) + 1,
          },
          heartbeat: {
            status: 'disconnected',
            at: nowIso(),
            latencyMs: null,
            error: serializeError(error),
          },
        },
      })).catch(() => {});
      reject(error);
    }
  });
}

async function pollHostStatus() {
  const startedAt = nowIso();
  const state = await readState();
  try {
    const status = await sendNativeRequest({ method: 'status', params: { includeEvents: true } });
    if (!status.ok) {
      const error = new Error(status.error?.message || 'native host status failed');
      error.code = status.error?.code;
      throw error;
    }
    const next = {
      connection: {
        host: {
          connected: true,
          lastConnectedAt: status.ok ? (state.connection.host.lastConnectedAt || startedAt) : state.connection.host.lastConnectedAt,
          lastError: null,
          reconnectAttempts: status.ok ? 0 : state.connection.host.reconnectAttempts,
        },
        heartbeat: {
          status: 'connected',
          at: status.now || startedAt,
          latencyMs: status.latencyMs || null,
          error: null,
        },
      },
      queue: {
        paused: status.result?.paused === true,
        counts: status.result?.counts || state.queue.counts,
        activeJobId: status.result?.active_job_id || status.result?.active_jobId || state.queue.activeJobId,
        activeManifest: status.result?.active_manifest || state.queue.activeManifest,
        lastUpdateAt: status.now || nowIso(),
      },
    };
    const written = await writeState(mergeObjects(next, { queue: { lastUpdateAt: startedAt } }));
    void scheduleExecution();
    return written;
  } catch (error) {
    const payload = serializeError(error);
    const next = {
      connection: {
        host: {
          connected: false,
          lastError: payload,
          reconnectAttempts: state.connection.host.reconnectAttempts + 1,
        },
        heartbeat: {
          status: 'disconnected',
          at: nowIso(),
          latencyMs: null,
          error: payload,
        },
      },
    };
    return writeState(next);
  }
}

async function sendFlowMessage(type, payload = {}) {
  if (!Number.isInteger(flowTabId)) throw new Error('No verified Flow content tab is connected');
  try {
    return await chrome.tabs.sendMessage(flowTabId, { type, ...payload });
  } catch (error) {
    flowTabId = null;
    throw error;
  }
}

function uiRequestFor(job) {
  const settings = job.requested_settings || {};
  const budget = job.budget_policy || {};
  return {
    ...job,
    itemId: job.item_id,
    providerRequestId: job.provider_request_id,
    settings: {
      model: settings.model,
      mode: settings.mode,
      aspectRatio: settings.aspect_ratio,
      duration: settings.duration_seconds,
      quantity: settings.quantity,
    },
    zeroCredit: budget.kind === 'zero_credit',
    credit: {
      zero: budget.kind === 'zero_credit',
      kind: budget.kind,
      cost: budget.kind === 'paid' ? budget.expected_credits : 0,
    },
    accountVerified: job.approval_policy?.expected_account_verified === true,
  };
}

function isBoundedZeroCreditImage(job) {
  const settings = job.requested_settings || {};
  const budget = job.budget_policy || {};
  return job.action === 'image_generation'
    && String(settings.mode || '').toLowerCase() === 'image'
    && budget.kind === 'zero_credit'
    && Number(budget.expected_credits) === 0
    && Number(budget.max_credits) === 0
    && job.approval_policy?.state === 'standing_policy_approved';
}

async function replaceFlowPromptWithTrustedInput(prompt) {
  if (!Number.isInteger(flowTabId)) throw new Error('No verified Flow content tab is connected');
  const focused = await sendFlowMessage('FLOW_UI_FOCUS_PROMPT');
  if (!focused?.ok) throw new Error(focused?.code || 'prompt_focus_failed');
  const target = { tabId: flowTabId };
  let attached = false;
  try {
    await chrome.debugger.attach(target, '1.3');
    attached = true;
    await chrome.debugger.sendCommand(target, 'Input.dispatchKeyEvent', {
      type: 'rawKeyDown', key: 'a', code: 'KeyA', windowsVirtualKeyCode: 65, nativeVirtualKeyCode: 65, modifiers: 2,
    });
    await chrome.debugger.sendCommand(target, 'Input.dispatchKeyEvent', {
      type: 'keyUp', key: 'a', code: 'KeyA', windowsVirtualKeyCode: 65, nativeVirtualKeyCode: 65, modifiers: 2,
    });
    await chrome.debugger.sendCommand(target, 'Input.insertText', { text: String(prompt || '') });
  } finally {
    if (attached) await chrome.debugger.detach(target).catch(() => {});
  }
}

/**
 * Dispatch a trusted left click at a viewport point in the Flow tab.
 *
 * Flow ignores synthetic in-page input: the same class of `element.click()`
 * that the content script can produce was never accepted as a submission, in
 * the same way synthetic `beforeinput`/`input` were never accepted as prompt
 * entry. Chrome synthesizes the full trusted pointer/mouse/click sequence from
 * these CDP events, so `isTrusted` is true and Flow's handler runs.
 *
 * Coordinates are CSS pixels in the main-frame layout viewport (the basis of
 * `getBoundingClientRect`); no devicePixelRatio scaling is applied.
 */
async function dispatchTrustedClickAt(point) {
  if (!Number.isInteger(flowTabId)) throw new Error('No verified Flow content tab is connected');
  if (!Number.isFinite(point?.x) || !Number.isFinite(point?.y)) throw new Error('trusted_click_point_invalid');
  // A background tab can be throttled and some apps gate on visibility; make
  // the already-open Flow tab active without creating any new tab or window.
  try { await chrome.tabs.update(flowTabId, { active: true }); } catch { /* non-fatal */ }
  const target = { tabId: flowTabId };
  const base = { x: point.x, y: point.y, button: 'left', buttons: 1, clickCount: 1, pointerType: 'mouse' };
  let attached = false;
  try {
    await chrome.debugger.attach(target, '1.3');
    attached = true;
    await chrome.debugger.sendCommand(target, 'Input.dispatchMouseEvent', { ...base, type: 'mouseMoved', buttons: 0 });
    await chrome.debugger.sendCommand(target, 'Input.dispatchMouseEvent', { ...base, type: 'mousePressed' });
    await chrome.debugger.sendCommand(target, 'Input.dispatchMouseEvent', { ...base, type: 'mouseReleased', buttons: 0 });
  } finally {
    if (attached) await chrome.debugger.detach(target).catch(() => {});
  }
  return { dispatched: true, point: { x: point.x, y: point.y } };
}

async function dispatchTrustedKeyboardSubmit() {
  if (!Number.isInteger(flowTabId)) throw new Error('No verified Flow content tab is connected');
  try { await chrome.tabs.update(flowTabId, { active: true }); } catch { /* non-fatal */ }
  const target = { tabId: flowTabId };
  let attached = false;
  try {
    await chrome.debugger.attach(target, '1.3');
    attached = true;
    await chrome.debugger.sendCommand(target, 'Input.dispatchKeyEvent', {
      type: 'rawKeyDown',
      key: 'Enter',
      code: 'Enter',
      windowsVirtualKeyCode: 13,
      nativeVirtualKeyCode: 13,
      modifiers: 2, // Control / Cmd
    });
    await chrome.debugger.sendCommand(target, 'Input.dispatchKeyEvent', {
      type: 'keyUp',
      key: 'Enter',
      code: 'Enter',
      windowsVirtualKeyCode: 13,
      nativeVirtualKeyCode: 13,
      modifiers: 2,
    });
  } finally {
    if (attached) await chrome.debugger.detach(target).catch(() => {});
  }
  return { dispatched: true, submitMethod: 'trusted_keyboard_enter' };
}

/**
 * Submit the armed bounded zero-credit image with trusted input.
 *
 * Order matters: measure (which also snapshots pre-click media) -> trusted
 * click (with keyboard fallback if occluded) -> commit.
 */
async function submitBoundedZeroCreditImageWithTrustedClick() {
  const measured = await sendFlowMessage('FLOW_UI_MEASURE_SUBMIT');
  let clickInfo = null;
  if (measured?.ok && measured.point) {
    clickInfo = await dispatchTrustedClickAt(measured.point);
  } else {
    // If point measurement fails (e.g. popover occlusion), dispatch trusted Ctrl+Enter
    clickInfo = await dispatchTrustedKeyboardSubmit();
  }
  const committed = await sendFlowMessage('FLOW_UI_COMMIT_SUBMIT');
  return {
    ...committed,
    ok: committed?.ok === true,
    trustedClick: { ...clickInfo, control: measured?.control || { role: 'keyboard_submit' } },
  };
}

function makeContentDriver(job) {
  const request = uiRequestFor(job);
  return {
    snapshot: async () => {
      const response = await sendFlowMessage('FLOW_UI_SNAPSHOT');
      if (!response?.ok) throw new Error(response?.code || 'Flow snapshot failed');
      return response.observation;
    },
    prepare: async () => {
      if (!isBoundedZeroCreditImage(job)) return sendFlowMessage('FLOW_UI_PREPARE', { request });
      await replaceFlowPromptWithTrustedInput(request.prompt ?? request.promptText);
      return sendFlowMessage('FLOW_UI_ARM_BOUNDED_IMAGE', { request });
    },
    submit: async () => (isBoundedZeroCreditImage(job)
      ? submitBoundedZeroCreditImageWithTrustedClick()
      : sendFlowMessage('FLOW_UI_SUBMIT')),
    waitForGeneration: async (options = {}) => sendFlowMessage('FLOW_UI_WAIT_GENERATION', options),
  };
}

async function importDownloadedOutput(context) {
  const response = await sendNativeRequest({
    method: 'import_output',
    params: {
      source_path: context.sourcePath,
      output_path: context.outputPath,
      item_id: context.itemId,
      request_id: context.requestId,
      provider_media_id: context.providerMediaId,
      download_id: context.downloadId,
    },
  }, { timeoutMs: 120000 });
  if (!response.ok) throw new Error(response.error?.message || 'Native output import failed');
  return response.result;
}

async function executeOnePendingJob() {
  if (!Number.isInteger(flowTabId)) return null;
  const claim = await sendNativeRequest({ method: 'claim_next', params: {} });
  if (!claim.ok) throw new Error(claim.error?.message || 'Queue claim failed');
  const job = claim.result?.job;
  if (!job) return null;
  const isVideoJob = FLOW_VIDEO_ACTIONS.includes(job.action || job.batch_action);
  const runner = (isVideoJob ? createVideoRunner : createImageRunner)({
    driver: makeContentDriver(job),
    importer: importDownloadedOutput,
    onProgress: (progress) => {
      void writeState({
        diagnostics: {
          lastAction: progress.event,
          lastPayload: {
            event: progress.event,
            item_id: progress.item_id || null,
            media_id: progress.media_id || null,
          },
        },
      });
    },
  });
  try {
    const result = await runner.run(job);
    const completed = await sendNativeRequest({
      method: 'complete',
      params: { job_id: job.job_id, result },
    }, { timeoutMs: 120000 });
    if (!completed.ok) throw new Error(completed.error?.message || 'Queue completion failed');
    return result;
  } catch (error) {
    await sendNativeRequest({
      method: 'fail',
      params: {
        job_id: job.job_id,
        error: {
          code: error?.code || 'flow_execution_failed',
          message: error?.message || String(error),
          credits: error?.credits || error?.result?.credits || null,
          result: error?.result || error?.details?.result || error?.details || null,
        },
      },
    }).catch(() => {});
    throw error;
  }
}

async function recoverFlowTabBinding() {
  if (Number.isInteger(flowTabId)) {
    try {
      const tab = await chrome.tabs.get(flowTabId);
      if (tab?.url?.includes('labs.google/fx/')) return flowTabId;
    } catch {
      flowTabId = null;
    }
  }
  const tabs = await chrome.tabs.query({ url: ['https://labs.google/fx/*'] });
  if (!tabs || tabs.length === 0) return null;
  const activeTab = tabs.find((t) => t.active);
  if (activeTab && (await bindFlowTab(activeTab.id))) {
    return flowTabId;
  }
  for (const tab of tabs) {
    if (await bindFlowTab(tab.id)) {
      return flowTabId;
    }
  }
  return null;
}

async function bindFlowTab(tabId) {
  if (!Number.isInteger(tabId)) return null;
  try {
    const response = await chrome.tabs.sendMessage(tabId, { type: 'FLOW_UI_SNAPSHOT' });
    if (!response?.ok || response.observation?.page?.isFlow !== true) return null;
    flowTabId = tabId;
    return flowTabId;
  } catch {
    return null;
  }
}

function scheduleExecution() {
  if (executionPromise) return executionPromise;
  let ranJob = false;
  executionPromise = recoverFlowTabBinding()
    .then((tabId) => (Number.isInteger(tabId) ? executeOnePendingJob() : null))
    .then((result) => {
      ranJob = Boolean(result);
      return result;
    })
    .catch((error) => writeState({
      diagnostics: {
        lastCaptureAt: nowIso(),
        lastAction: 'execution_failed',
        lastPayload: serializeError(error),
      },
    }))
    .finally(() => {
      executionPromise = null;
      if (ranJob) setTimeout(() => void scheduleExecution(), 250);
    });
  return executionPromise;
}

function startHeartbeatLoop() {
  if (heartbeatTimer) return;
  heartbeatTimer = setInterval(() => {
    void pollHostStatus().catch(() => {});
  }, HEARTBEAT_INTERVAL_MS);
}

function stopHeartbeatLoop() {
  if (!heartbeatTimer) return;
  clearInterval(heartbeatTimer);
  heartbeatTimer = null;
}

async function updatePanelState(clientId, connected) {
  if (connected) {
    return writeState({
      panel: {
        connected,
        clientId,
        lastVisibleAt: nowIso(),
      },
    });
  }
  return writeState({
    panel: {
      connected: false,
      lastVisibleAt: nowIso(),
    },
  });
}

async function handlePanelRequest(message) {
  if (!message || typeof message.type !== 'string') return { ok: false, error: 'invalid message' };
  switch (message.type) {
    case 'FLOW_DRIVER_GET_STATE':
      await pollHostStatus();
      void scheduleExecution();
      return { ok: true, state: await readState() };
    case 'FLOW_DRIVER_REFRESH': {
      const state = await pollHostStatus();
      void scheduleExecution();
      return { ok: true, state };
    }
    case 'FLOW_DRIVER_PANEL_OPEN': {
      const clientId = message.clientId || crypto.randomUUID();
      await updatePanelState(clientId, true);
      const state = await readState();
      return { ok: true, state, clientId };
    }
    case 'FLOW_DRIVER_PANEL_CLOSE':
      await updatePanelState(null, false);
      return { ok: true, state: await readState() };
    case 'FLOW_DRIVER_PAUSE_QUEUE': {
      const method = message.paused ? 'pause_queue' : 'resume_queue';
      const response = await sendNativeRequest({ method, params: { reason: 'sidepanel_operator' } });
      if (!response.ok) throw new Error(response.error?.message || `${method} failed`);
      return { ok: true, state: await pollHostStatus() };
    }
    case 'FLOW_DRIVER_RETRY_ITEM':
    case 'FLOW_DRIVER_RETRY_ACTIVE': {
      if (typeof message.jobId !== 'string' || message.jobId.trim() === '') {
        return { ok: false, error: 'jobId is required to retry a failed or cancelled item' };
      }
      const response = await sendNativeRequest({ method: 'retry_job', params: { job_id: message.jobId.trim() } });
      if (!response.ok) throw new Error(response.error?.message || 'retry_job failed');
      return { ok: true, state: await pollHostStatus() };
    }
    case 'FLOW_DRIVER_CAPTURE_DIAGNOSTIC': {
      const capturedAt = nowIso();
      const state = await pollHostStatus();
      const diagnostic = {
        capturedAt,
        queue: state.queue,
        heartbeat: state.connection.heartbeat,
        nativeConnected: state.connection.host.connected,
        manifest: await readManifestVersion(),
      };
      await writeState({
        diagnostics: {
          lastCaptureAt: capturedAt,
          lastAction: 'capture_diagnostic',
          lastPayload: diagnostic,
        },
      });
      return { ok: true, diagnostic };
    }
    case 'FLOW_DRIVER_CAPTURE_CAPABILITY': {
      if (!Number.isInteger(flowTabId)) return { ok: false, error: 'No verified Flow content tab is connected' };
      const accountMarker = typeof message.accountMarker === 'string' ? message.accountMarker.trim() : '';
      const outputPath = typeof message.outputPath === 'string' ? message.outputPath.trim() : '';
      if (!accountMarker) return { ok: false, error: 'A non-secret account marker is required' };
      if (!outputPath) return { ok: false, error: 'A project-relative capability output path is required' };
      const response = await sendFlowMessage('FLOW_UI_SNAPSHOT');
      if (!response?.ok || !response.observation) throw new Error(response?.code || 'Flow snapshot failed');
      const snapshot = await buildCapabilitySnapshot({
        observation: response.observation,
        accountMarker,
        operatorConfirmedAccount: message.operatorConfirmedAccount === true,
        extensionVersion: chrome.runtime.getManifest()?.version || 'dev',
      });
      const written = await sendNativeRequest({
        method: 'write_capability_snapshot',
        params: { output_path: outputPath, snapshot },
      });
      if (!written.ok) throw new Error(written.error?.message || 'Capability snapshot write failed');
      await writeState({ diagnostics: { lastCaptureAt: nowIso(), lastAction: 'capture_capability', lastPayload: written.result } });
      return { ok: true, capability: written.result };
    }
    default:
      return { ok: false, error: `unknown message type: ${message.type}` };
  }
}

chrome.runtime.onInstalled.addListener(async () => {
  await writeState({
    meta: {
      pluginName: 'flow-driver-shell',
      extensionVersion: chrome.runtime.getManifest()?.version || null,
    },
  });
  await pollHostStatus().catch(() => {});
  chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: true }).catch(() => {});
  startHeartbeatLoop();
});

chrome.runtime.onStartup.addListener(() => {
  writeState((state) => ({
    ...state,
    panel: {
      ...state.panel,
      connected: false,
    },
    queue: {
      ...state.queue,
      activeJobId: null,
    },
  })).catch(() => {});
  chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: true }).catch(() => {});
  startHeartbeatLoop();
});

chrome.runtime.onSuspend.addListener(() => {
  stopHeartbeatLoop();
});

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message?.type === 'FLOW_DRIVER_CONTENT_READY') {
    if (Number.isInteger(sender?.tab?.id)) flowTabId = sender.tab.id;
    void scheduleExecution();
    sendResponse({ ok: Number.isInteger(flowTabId) });
    return false;
  }
  handlePanelRequest(message)
    .then((response) => sendResponse(response))
    .catch((error) => sendResponse({ ok: false, error: serializeError(error) }))
    .finally(() => {});
  return true;
});

// Extension reloads can outlive a content script's one-time ready message.
// A completed Flow navigation provides a second, background-only bind point;
// it never activates, opens, or navigates a tab.
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status !== 'complete' || !String(tab?.url || '').startsWith('https://labs.google/fx/')) return;
  void bindFlowTab(tabId).then((boundTabId) => {
    if (Number.isInteger(boundTabId)) void scheduleExecution();
  });
});

startHeartbeatLoop();
