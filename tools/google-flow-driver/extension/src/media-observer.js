/**
 * Flow media observation for one serial request.
 *
 * The page can contain media from earlier prompts and the generated card is
 * often inserted before its URL/status settles.  This module deliberately
 * keeps a request-local before snapshot, compares stable provider identities,
 * and requires the same new item to be observed in consecutive settled polls.
 * It does not inspect or transport media bytes.
 */

export const FLOW_MEDIA_OBSERVER_VERSION = 'flow-media-observer.v1';

export class MediaObservationError extends Error {
  constructor(code, message = code, details = {}) {
    super(message);
    this.name = 'MediaObservationError';
    this.code = code;
    this.details = details;
  }
}

function value(value) {
  return value === undefined || value === null || value === '' ? null : String(value);
}

function asMediaSource(source) {
  if (source && source.media && typeof source.media === 'object') return source.media;
  return source;
}

function asArray(value) {
  if (Array.isArray(value)) return value;
  if (value && typeof value === 'object') return [value];
  return [];
}

function providerId(item) {
  return value(
    item?.providerMediaId
      ?? item?.provider_media_id
      ?? item?.mediaId
      ?? item?.media_id
      ?? item?.id
      ?? item?.media?.id,
  );
}

function mediaUrl(item) {
  return value(item?.url ?? item?.mediaUrl ?? item?.media_url ?? item?.src ?? item?.href);
}

function requestId(item) {
  return value(item?.requestId ?? item?.request_id ?? item?.flowRequestId ?? item?.flow_request_id);
}

function statusFor(item) {
  const raw = value(item?.status ?? item?.state ?? item?.generationStatus ?? item?.generation_status);
  if (raw) return raw.toLowerCase();
  if (item?.settled === true) return 'settled';
  if (item?.ariaBusy === true) return 'generating';
  return 'settled';
}

export function isSettledMedia(item) {
  const status = statusFor(item);
  return item?.settled === true
    || ['settled', 'completed', 'complete', 'ready', 'downloadable'].includes(status);
}

/**
 * Prefer a provider/card ID over a URL.  URLs can be assigned after the card
 * is inserted, while a provider ID remains stable across that settling step.
 */
export function mediaIdentity(item) {
  const id = providerId(item);
  if (id) return `id:${id}`;
  const url = mediaUrl(item);
  if (url) return `url:${url}`;
  return '';
}

export function mediaFingerprint(item) {
  return JSON.stringify({
    identity: mediaIdentity(item),
    id: providerId(item),
    requestId: requestId(item),
    url: mediaUrl(item),
    status: statusFor(item),
    settled: isSettledMedia(item),
  });
}

function normalizeItem(item, index) {
  const id = providerId(item);
  const url = mediaUrl(item);
  const request = requestId(item);
  const status = statusFor(item);
  const normalized = {
    id,
    providerMediaId: id,
    requestId: request,
    url,
    status,
    settled: isSettledMedia(item),
    ordinal: Number.isInteger(item?.ordinal) ? item.ordinal : index,
  };
  if (item?.mimeType || item?.mime_type) normalized.mimeType = value(item.mimeType ?? item.mime_type);
  if (item?.filename) normalized.filename = value(item.filename);
  if (item?.downloadUrl || item?.download_url) normalized.downloadUrl = value(item.downloadUrl ?? item.download_url);
  return normalized;
}

function normalizeFailure(failure, index) {
  if (!failure || typeof failure !== 'object') return { index, status: 'failed' };
  return {
    index,
    id: providerId(failure),
    requestId: requestId(failure),
    status: value(failure.status ?? failure.state) || 'failed',
  };
}

/** Create a metadata-only media snapshot from a selector observation or list. */
export function snapshotMedia(source, { clock = () => new Date() } = {}) {
  const media = asMediaSource(source) || {};
  const items = asArray(media.items ?? media.outputs ?? media.media ?? source).map(normalizeItem);
  const failures = asArray(media.failures ?? media.errors).map(normalizeFailure);
  let capturedAt;
  try {
    const now = typeof clock === 'function' ? clock() : clock;
    capturedAt = new Date(now || Date.now()).toISOString();
  } catch {
    capturedAt = new Date().toISOString();
  }
  return {
    schemaVersion: FLOW_MEDIA_OBSERVER_VERSION,
    capturedAt,
    items,
    failures,
  };
}

function itemMap(snapshot) {
  const map = new Map();
  for (const item of snapshotMedia(snapshot).items) {
    const key = mediaIdentity(item);
    if (key && !map.has(key)) map.set(key, item);
  }
  return map;
}

/** Compare two snapshots using stable provider/card identity. */
export function diffMediaSnapshots(before, after) {
  const beforeSnapshot = snapshotMedia(before);
  const afterSnapshot = snapshotMedia(after);
  const beforeMap = itemMap(beforeSnapshot);
  const afterMap = itemMap(afterSnapshot);
  const duplicateKeys = [];
  const seenAfter = new Set();
  for (const item of afterSnapshot.items) {
    const key = mediaIdentity(item);
    if (!key) continue;
    if (seenAfter.has(key)) duplicateKeys.push(key);
    seenAfter.add(key);
  }
  const added = [];
  const removed = [];
  const unchanged = [];
  for (const [key, item] of afterMap) {
    if (beforeMap.has(key)) unchanged.push(item);
    else added.push(item);
  }
  for (const [key, item] of beforeMap) {
    if (!afterMap.has(key)) removed.push(item);
  }
  return {
    schemaVersion: FLOW_MEDIA_OBSERVER_VERSION,
    before: beforeSnapshot,
    after: afterSnapshot,
    added,
    removed,
    unchanged,
    duplicateKeys,
    ambiguous: duplicateKeys.length > 0,
    failures: afterSnapshot.failures,
  };
}

function matchesExpected(item, expected = {}) {
  const expectedRequestId = value(expected.providerRequestId ?? expected.provider_request_id ?? expected.requestId ?? expected.request_id);
  if (expectedRequestId && requestId(item) !== expectedRequestId) return false;
  const expectedMediaId = value(expected.providerMediaId ?? expected.provider_media_id ?? expected.mediaId ?? expected.media_id);
  if (expectedMediaId && providerId(item) !== expectedMediaId) return false;
  return true;
}

/**
 * Return only settled media created after `before`.  A requested item with an
 * explicit Flow request ID must carry that ID; an unbound card is ambiguous.
 */
export function selectFreshMedia(before, after, expected = {}) {
  const diff = diffMediaSnapshots(before, after);
  if (diff.ambiguous) {
    return {
      ...diff,
      candidates: [],
      settled: [],
      ok: false,
      code: 'media_identity_ambiguous',
    };
  }
  const attributable = diff.added.filter((item) => matchesExpected(item, expected));
  const settled = attributable.filter(isSettledMedia);
  return {
    ...diff,
    candidates: attributable,
    settled,
    ok: settled.length > 0,
    code: settled.length ? 'fresh_media_settled' : diff.failures.length ? 'generation_failed' : 'fresh_media_pending',
  };
}

export function createMediaObserver({
  snapshot = null,
  clock = () => new Date(),
  stabilityPolls = 2,
  pollIntervalMs = 100,
} = {}) {
  let before = snapshotMedia({ items: [] }, { clock });
  let last = before;
  let disposed = false;

  const capture = (input = null) => {
    if (disposed) throw new MediaObservationError('observer_disposed');
    const result = snapshotMedia(input ?? (typeof snapshot === 'function' ? snapshot() : { items: [] }), { clock });
    last = result;
    return result;
  };

  const begin = (input = null) => {
    before = capture(input);
    return before;
  };

  const observe = (input = null, expected = {}) => {
    const after = capture(input);
    return selectFreshMedia(before, after, expected);
  };

  const waitForStable = async ({
    getSnapshot = null,
    expected = {},
    timeoutMs = 300000,
    pollInterval = pollIntervalMs,
    requiredPolls = stabilityPolls,
    signal = null,
  } = {}) => {
    const startedAt = Date.now();
    const pollsNeeded = Math.max(1, Number.isInteger(requiredPolls) ? requiredPolls : 1);
    let stableKey = null;
    let stableFingerprint = null;
    let stableCount = 0;
    let latest = last;
    for (;;) {
      if (disposed) throw new MediaObservationError('observer_disposed');
      if (signal?.aborted) throw new MediaObservationError('aborted');
      const input = typeof getSnapshot === 'function'
        ? await getSnapshot()
        : typeof snapshot === 'function'
          ? await snapshot()
          : latest;
      const result = observe(input, expected);
      latest = result.after;
      if (result.failures.length) {
        throw new MediaObservationError('generation_failed', 'Flow reported a generation failure', { result });
      }
      if (result.ambiguous) {
        throw new MediaObservationError('media_identity_ambiguous', 'Flow exposed duplicate media identities', { result });
      }
      const candidate = result.settled[0];
      if (candidate) {
        const key = mediaIdentity(candidate);
        const fingerprint = mediaFingerprint(candidate);
        if (key === stableKey && fingerprint === stableFingerprint) stableCount += 1;
        else {
          stableKey = key;
          stableFingerprint = fingerprint;
          stableCount = 1;
        }
        if (stableCount >= pollsNeeded) {
          const output = {
            schemaVersion: FLOW_MEDIA_OBSERVER_VERSION,
            ok: true,
            item: candidate,
            media: candidate,
            items: result.settled,
            before,
            after: result.after,
            diff: result,
            polls: stableCount,
            elapsedMs: Date.now() - startedAt,
          };
          return output;
        }
      } else {
        stableKey = null;
        stableFingerprint = null;
        stableCount = 0;
      }
      if (Date.now() - startedAt >= timeoutMs) {
        throw new MediaObservationError('media_timeout', 'No stable new Flow media arrived before timeout', {
          before,
          after: latest,
          lastResult: result,
        });
      }
      await new Promise((resolve) => setTimeout(resolve, Math.max(0, pollInterval)));
    }
  };

  return {
    get before() { return before; },
    get last() { return last; },
    capture,
    snapshot: capture,
    begin,
    start: begin,
    observe,
    diff: (after, expected = {}) => observe(after, expected),
    waitForStable,
    waitForStableNewMedia: waitForStable,
    findFresh: (after, expected = {}) => selectFreshMedia(before, after, expected),
    findStableNewMedia: (after, expected = {}) => selectFreshMedia(before, after, expected),
    dispose() { disposed = true; },
  };
}

export const MediaObserver = createMediaObserver;
export async function waitForStableNewMedia(beforeOrOptions, getSnapshot, options = {}) {
  // Support both `(before, getSnapshot, options)` and the ergonomic single
  // options object used by browser callers.
  if (beforeOrOptions && typeof beforeOrOptions === 'object'
    && (Object.hasOwn(beforeOrOptions, 'before') || Object.hasOwn(beforeOrOptions, 'getSnapshot'))
    && getSnapshot === undefined) {
    const input = beforeOrOptions;
    const observer = createMediaObserver(input);
    observer.begin(input.before ?? { items: [] });
    return observer.waitForStable(input);
  }
  const observer = createMediaObserver(options);
  observer.begin(beforeOrOptions);
  return observer.waitForStable({ ...options, getSnapshot });
}

// Descriptive aliases keep the contract easy to discover for callers that use
// "capture"/"wait" terminology instead of the shorter internal names.
export const captureMediaSnapshot = snapshotMedia;
export const compareMediaSnapshots = diffMediaSnapshots;
export const findFreshMedia = selectFreshMedia;
export const waitForNewStableMedia = waitForStableNewMedia;
