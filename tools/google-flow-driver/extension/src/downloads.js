/**
 * Small wrapper around chrome.downloads.  Flow output is downloaded by the
 * browser (never by navigating the page), and every wait is keyed by the ID
 * returned from that exact download() call.  We never scan all downloads for a
 * filename, which avoids stale/duplicate output association.
 */

export const FLOW_DOWNLOADS_VERSION = 'flow-downloads.v1';

export class DownloadAssociationError extends Error {
  constructor(code, message = code, details = {}) {
    super(message);
    this.name = 'DownloadAssociationError';
    this.code = code;
    this.details = details;
  }
}

function deepFreeze(value, seen = new Set()) {
  if (!value || typeof value !== 'object' || seen.has(value)) return value;
  seen.add(value);
  for (const child of Object.values(value)) deepFreeze(child, seen);
  return Object.freeze(value);
}

function asPromiseCall(target, method, args = []) {
  const fn = target?.[method];
  if (typeof fn !== 'function') {
    return Promise.reject(new DownloadAssociationError('downloads_api_missing', `chrome.downloads.${method} is unavailable`));
  }
  return new Promise((resolve, reject) => {
    let settled = false;
    const finish = (error, result) => {
      if (settled) return;
      settled = true;
      if (error) reject(error);
      else resolve(result);
    };
    const callback = (result) => {
      const runtimeError = globalThis.chrome?.runtime?.lastError;
      if (runtimeError) finish(new DownloadAssociationError('downloads_api_error', runtimeError.message || String(runtimeError)));
      else finish(null, result);
    };
    try {
      const returned = fn.call(target, ...args, callback);
      if (returned && typeof returned.then === 'function') returned.then((result) => finish(null, result), finish);
      else if (returned !== undefined) finish(null, returned);
    } catch (error) {
      finish(error instanceof Error ? error : new DownloadAssociationError('downloads_api_error', String(error)));
    }
  });
}

function normalizeUrl(url) {
  if (typeof url !== 'string' || url.trim() === '') {
    throw new DownloadAssociationError('missing_media_url', 'A media URL is required for download');
  }
  const raw = url.trim();
  let parsed;
  try { parsed = new URL(raw); } catch { throw new DownloadAssociationError('invalid_media_url', 'Media URL is not valid'); }
  if (!['https:', 'http:', 'blob:'].includes(parsed.protocol)) {
    throw new DownloadAssociationError('unsafe_media_url', `Media URL protocol is not allowed: ${parsed.protocol}`);
  }
  return raw;
}

function normalizeFilename(filename, fallback = 'flow-output.png') {
  const candidate = String(filename || fallback).trim();
  if (!candidate || candidate === '.' || candidate === '..') throw new DownloadAssociationError('invalid_download_filename');
  if (/^[a-zA-Z]:[\\/]/.test(candidate) || candidate.startsWith('/') || candidate.startsWith('\\')) {
    throw new DownloadAssociationError('unsafe_download_filename', 'Download filename must be relative');
  }
  const parts = candidate.replaceAll('\\', '/').split('/');
  if (parts.some((part) => !part || part === '.' || part === '..')) {
    throw new DownloadAssociationError('unsafe_download_filename', 'Download filename may not escape its download root');
  }
  return parts.join('/');
}

function normalizeRecord(value, fallback = {}) {
  const record = Array.isArray(value) ? value[0] : value;
  if (!record || typeof record !== 'object') return null;
  const state = record.state?.current ?? record.state ?? null;
  const error = record.error?.current ?? record.error ?? null;
  return {
    id: record.id ?? fallback.downloadId,
    filename: record.filename ?? fallback.filename ?? null,
    url: record.url ?? fallback.url ?? null,
    state: typeof state === 'string' ? state : null,
    error: error == null ? null : String(error),
    bytesReceived: Number.isFinite(record.bytesReceived) ? record.bytesReceived : null,
    totalBytes: Number.isFinite(record.totalBytes) ? record.totalBytes : null,
  };
}

function downloadEventCurrent(change, key) {
  const value = change?.[key];
  return value && typeof value === 'object' && Object.hasOwn(value, 'current') ? value.current : value;
}

/** Wait for one specific Chrome download ID to finish. */
export async function waitForDownloadCompletion({
  chrome: chromeApi = globalThis.chrome,
  downloadId,
  filename = null,
  url = null,
  timeoutMs = 120000,
  pollIntervalMs = 250,
  signal = null,
} = {}) {
  if (!Number.isInteger(downloadId) && typeof downloadId !== 'string') {
    throw new DownloadAssociationError('invalid_download_id', 'Chrome did not return a download ID');
  }
  const downloads = chromeApi?.downloads;
  if (!downloads) throw new DownloadAssociationError('downloads_api_missing');
  const startedAt = Date.now();
  let timer = null;
  let pollTimer = null;
  let listener = null;
  let settled = false;

  const cleanup = () => {
    if (timer) clearTimeout(timer);
    if (pollTimer) clearTimeout(pollTimer);
    if (listener && typeof downloads.onChanged?.removeListener === 'function') {
      downloads.onChanged.removeListener(listener);
    }
    timer = null;
    pollTimer = null;
    listener = null;
  };

  const readRecord = async () => {
    const response = await asPromiseCall(downloads, 'search', [{ id: downloadId }]);
    return normalizeRecord(response, { downloadId, filename, url });
  };

  return await new Promise((resolve, reject) => {
    const finish = (error, record) => {
      if (settled) return;
      settled = true;
      cleanup();
      if (error) reject(error);
      else resolve(record);
    };

    const inspect = async (eventRecord = null) => {
      try {
        const record = eventRecord || await readRecord();
        if (!record) return;
        if (String(record.id) !== String(downloadId)) return;
        if (record.state === 'complete') {
          finish(null, record);
          return;
        }
        if (record.state === 'interrupted' || record.error) {
          finish(new DownloadAssociationError('download_interrupted', record.error || 'Chrome download was interrupted', { record }));
          return;
        }
        if (Date.now() - startedAt >= timeoutMs) {
          finish(new DownloadAssociationError('download_timeout', 'Chrome download did not complete before timeout', { record }));
          return;
        }
        pollTimer = setTimeout(() => { pollTimer = null; void inspect(); }, Math.max(0, pollIntervalMs));
      } catch (error) {
        finish(error instanceof DownloadAssociationError ? error : new DownloadAssociationError('downloads_api_error', String(error)));
      }
    };

    listener = (change) => {
      if (!change || String(change.id) !== String(downloadId)) return;
      const state = downloadEventCurrent(change, 'state');
      const error = downloadEventCurrent(change, 'error');
      const record = { id: downloadId, filename, url, state, error };
      if (state === 'complete' || state === 'interrupted' || error) void inspect(record);
    };
    if (typeof downloads.onChanged?.addListener === 'function') downloads.onChanged.addListener(listener);
    timer = setTimeout(() => finish(new DownloadAssociationError('download_timeout', 'Chrome download did not complete before timeout', { downloadId })), timeoutMs);
    if (signal) {
      if (signal.aborted) {
        finish(new DownloadAssociationError('aborted', 'Download wait was aborted'));
        return;
      }
      signal.addEventListener?.('abort', () => finish(new DownloadAssociationError('aborted', 'Download wait was aborted')), { once: true });
    }
    void inspect();
  });
}

function fallbackFilename(item = {}) {
  const id = String(item.itemId ?? item.item_id ?? 'flow-output').replace(/[^A-Za-z0-9._-]/g, '_');
  const url = item.url || item.mediaUrl || '';
  let extension = 'png';
  try {
    const path = new URL(url).pathname;
    const match = path.match(/\.([A-Za-z0-9]{2,5})$/);
    if (match) extension = match[1].toLowerCase();
  } catch {
    // Keep the image default when the provider URL has no filename.
  }
  if (!['png', 'jpg', 'jpeg', 'webp', 'gif'].includes(extension)) extension = 'png';
  return `${id}.${extension}`;
}

/** Start and wait for a browser-managed download, preserving item lineage. */
export async function downloadMedia({
  chrome: chromeApi = globalThis.chrome,
  url,
  media = {},
  item = {},
  itemId = item.itemId ?? item.item_id,
  requestId = item.requestId ?? item.request_id ?? itemId,
  filename = item.downloadFilename ?? item.download_filename ?? media.filename ?? fallbackFilename({ ...media, itemId }),
  timeoutMs = 120000,
  pollIntervalMs = 250,
  signal = null,
} = {}) {
  const normalizedUrl = normalizeUrl(url ?? media.url ?? media.downloadUrl ?? media.download_url);
  const normalizedFilename = normalizeFilename(filename);
  const downloads = chromeApi?.downloads;
  if (!downloads) throw new DownloadAssociationError('downloads_api_missing');
  const downloadId = await asPromiseCall(downloads, 'download', [{
    url: normalizedUrl,
    filename: normalizedFilename,
    conflictAction: 'uniquify',
    saveAs: false,
  }]);
  const numericOrStringId = Number.isInteger(downloadId) || typeof downloadId === 'string' ? downloadId : downloadId?.id;
  if (!Number.isInteger(numericOrStringId) && typeof numericOrStringId !== 'string') {
    throw new DownloadAssociationError('invalid_download_id', 'chrome.downloads.download returned no ID');
  }
  const record = await waitForDownloadCompletion({
    chrome: chromeApi,
    downloadId: numericOrStringId,
    filename: normalizedFilename,
    url: normalizedUrl,
    timeoutMs,
    pollIntervalMs,
    signal,
  });
  const result = {
    schemaVersion: FLOW_DOWNLOADS_VERSION,
    downloadId: numericOrStringId,
    download_id: numericOrStringId,
    itemId: itemId == null ? null : String(itemId),
    item_id: itemId == null ? null : String(itemId),
    requestId: requestId == null ? null : String(requestId),
    request_id: requestId == null ? null : String(requestId),
    url: normalizedUrl,
    requestedFilename: normalizedFilename,
    filename: record.filename || normalizedFilename,
    state: record.state,
    bytesReceived: record.bytesReceived,
    totalBytes: record.totalBytes,
    completedAt: new Date().toISOString(),
  };
  return deepFreeze(result);
}

export function createDownloadManager({ chrome: chromeApi = globalThis.chrome, ...defaults } = {}) {
  const active = new Map();
  return {
    active,
    async download(options = {}) {
      const result = await downloadMedia({ chrome: chromeApi, ...defaults, ...options });
      active.set(String(result.downloadId), result);
      return result;
    },
    async wait(options = {}) {
      return waitForDownloadCompletion({ chrome: chromeApi, ...defaults, ...options });
    },
    get(downloadId) { return active.get(String(downloadId)) || null; },
  };
}

export const requestChromeDownload = downloadMedia;
export const downloadFlowMedia = downloadMedia;
export const waitForDownload = waitForDownloadCompletion;
export const downloadWithChrome = downloadMedia;
export const startAndWaitForDownload = downloadMedia;
