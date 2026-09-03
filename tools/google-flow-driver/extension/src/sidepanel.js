const POLL_MS = 3000;
const STATE_STORAGE_REFRESH_MS = 2000;

const el = {
  connectionStatus: document.getElementById('connectionStatus'),
  connectionDetails: document.getElementById('connectionDetails'),
  heartbeatLog: document.getElementById('heartbeatLog'),
  queuePending: document.getElementById('queuePending'),
  queueActive: document.getElementById('queueActive'),
  queueCompleted: document.getElementById('queueCompleted'),
  queueFailed: document.getElementById('queueFailed'),
  queueCancelled: document.getElementById('queueCancelled'),
  activeJob: document.getElementById('activeJob'),
  pauseStatus: document.getElementById('pauseStatus'),
  pauseBtn: document.getElementById('pauseBtn'),
  retryJobId: document.getElementById('retryJobId'),
  retryBtn: document.getElementById('retryBtn'),
  diagnosticBtn: document.getElementById('diagnosticBtn'),
  refreshBtn: document.getElementById('refreshBtn'),
  diagnosticOutput: document.getElementById('diagnosticOutput'),
  accountMarker: document.getElementById('accountMarker'),
  capabilityPath: document.getElementById('capabilityPath'),
  accountConfirmed: document.getElementById('accountConfirmed'),
  capabilityBtn: document.getElementById('capabilityBtn'),
  capabilityStatus: document.getElementById('capabilityStatus'),
  version: document.getElementById('extensionVersion'),
};

const clientId = crypto.randomUUID();
let lastState = null;
let timer = null;

function sendToServiceWorker(message) {
  return new Promise((resolve, reject) => {
    chrome.runtime.sendMessage({ ...message, clientId }, (response) => {
      if (chrome.runtime.lastError) {
        reject(new Error(chrome.runtime.lastError.message));
        return;
      }
      if (!response) {
        reject(new Error('empty response'));
        return;
      }
      if (!response.ok) {
        reject(new Error(response.error?.message || response.error || 'service worker returned error'));
        return;
      }
      resolve(response);
    });
  });
}

function formatHeartbeat(heartbeat) {
  if (!heartbeat || !heartbeat.at) return 'not yet available';
  if (heartbeat.status === 'connected') {
    return `connected ${new Date(heartbeat.at).toLocaleTimeString()} (${heartbeat.latencyMs ?? '?'} ms)`;
  }
  return `disconnected at ${new Date(heartbeat.at).toLocaleTimeString()}`;
}

function setConnectionVisual(heartbeat) {
  if (!heartbeat) {
    el.connectionStatus.textContent = 'Disconnected';
    el.connectionStatus.className = 'status status-offline';
    return;
  }
  if (heartbeat.status === 'connected') {
    el.connectionStatus.textContent = 'Connected';
    el.connectionStatus.className = 'status status-ok';
  } else {
    el.connectionStatus.textContent = 'Disconnected';
    el.connectionStatus.className = 'status status-offline';
  }
  el.connectionDetails.textContent = heartbeat.error?.message || formatHeartbeat(heartbeat);
}

function renderQueue(state) {
  const counts = state?.queue?.counts || {};
  el.queuePending.textContent = String(counts.pending ?? '-');
  el.queueActive.textContent = String(counts.active ?? '-');
  el.queueCompleted.textContent = String(counts.completed ?? '-');
  el.queueFailed.textContent = String(counts.failed ?? '-');
  el.queueCancelled.textContent = String(counts.cancelled ?? '-');
  el.activeJob.textContent = `Active item: ${state?.queue?.activeJobId || 'none'}`;
  el.pauseStatus.textContent = state?.queue?.paused ? 'Paused' : 'Running';
  el.pauseBtn.textContent = state?.queue?.paused ? 'Resume' : 'Pause';
}

async function refresh() {
  const response = await sendToServiceWorker({ type: 'FLOW_DRIVER_REFRESH' });
  const state = response.state || {};
  lastState = state;
  setConnectionVisual(state.connection?.heartbeat);
  renderQueue(state);
  el.heartbeatLog.textContent = formatHeartbeat(state.connection?.heartbeat);
  el.version.textContent = `v${state.meta?.extensionVersion || 'dev'}`;
}

async function performTogglePause() {
  const paused = !lastState?.queue?.paused;
  await sendToServiceWorker({ type: 'FLOW_DRIVER_PAUSE_QUEUE', paused });
  await refresh();
}

async function performRetry() {
  const jobId = el.retryJobId.value.trim();
  if (!jobId) throw new Error('Enter a failed or cancelled job ID.');
  el.retryBtn.disabled = true;
  try {
    await sendToServiceWorker({ type: 'FLOW_DRIVER_RETRY_ITEM', jobId });
    el.retryJobId.value = '';
    await refresh();
  } finally {
    el.retryBtn.disabled = false;
  }
}

async function performDiagnostic() {
  el.diagnosticBtn.disabled = true;
  try {
    const response = await sendToServiceWorker({ type: 'FLOW_DRIVER_CAPTURE_DIAGNOSTIC' });
    el.diagnosticOutput.textContent = JSON.stringify(response.state
      ? {
        capturedAt: response.state.diagnostics?.lastCaptureAt,
        heartbeat: response.state.connection?.heartbeat,
        queue: response.state.queue,
      }
      : response.diagnostic, null, 2);
  } finally {
    el.diagnosticBtn.disabled = false;
  }
}

async function performCapabilityCapture() {
  if (!el.accountConfirmed.checked) throw new Error('Confirm the intended Flow account and project first.');
  el.capabilityBtn.disabled = true;
  try {
    const response = await sendToServiceWorker({
      type: 'FLOW_DRIVER_CAPTURE_CAPABILITY',
      accountMarker: el.accountMarker.value.trim(),
      outputPath: el.capabilityPath.value.trim(),
      operatorConfirmedAccount: true,
    });
    el.capabilityStatus.textContent = `Captured: ${response.capability.output_path}`;
  } finally {
    el.capabilityBtn.disabled = false;
  }
}

async function requestStateOrHandleError(handler) {
  try {
    await handler();
  } catch (error) {
    el.connectionDetails.textContent = error.message || String(error);
  }
}

function startHeartbeat() {
  if (timer) return;
  timer = setInterval(() => {
    requestStateOrHandleError(() => refresh());
  }, POLL_MS);
}

window.addEventListener('beforeunload', () => {
  clearInterval(timer);
  sendToServiceWorker({ type: 'FLOW_DRIVER_PANEL_CLOSE' }).catch(() => {});
});

window.addEventListener('pagehide', () => {
  clearInterval(timer);
  sendToServiceWorker({ type: 'FLOW_DRIVER_PANEL_CLOSE' }).catch(() => {});
});

el.pauseBtn.addEventListener('click', () => requestStateOrHandleError(performTogglePause));
el.refreshBtn.addEventListener('click', () => requestStateOrHandleError(refresh));
el.retryBtn.addEventListener('click', () => requestStateOrHandleError(performRetry));
el.diagnosticBtn.addEventListener('click', () => requestStateOrHandleError(performDiagnostic));
el.capabilityBtn.addEventListener('click', () => requestStateOrHandleError(performCapabilityCapture));

sendToServiceWorker({ type: 'FLOW_DRIVER_PANEL_OPEN' })
  .then(() => refresh())
  .catch((error) => {
    el.connectionDetails.textContent = error.message || String(error);
  })
  .finally(() => {
    startHeartbeat();
  });
