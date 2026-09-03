import crypto from 'node:crypto';

/**
 * The native host is deliberately a metadata bridge.  Media bytes belong in
 * the browser download/quarantine path and must never cross stdout.
 */
export const NATIVE_PROTOCOL_VERSION = 'flow-native.v1';
// Chrome documents asymmetric native-messaging limits: an extension may send
// up to 64 MiB to a host, while a host response must remain below 1 MiB.
export const MAX_NATIVE_REQUEST_BYTES = 64 * 1024 * 1024;
export const MAX_NATIVE_RESPONSE_BYTES = 1024 * 1024;
// Backwards-compatible alias for callers that mean host-to-extension output.
export const MAX_NATIVE_MESSAGE_BYTES = MAX_NATIVE_RESPONSE_BYTES;
export const MAX_METADATA_STRING_BYTES = 256 * 1024;

export const QUEUE_STATES = Object.freeze([
  'pending',
  'active',
  'completed',
  'failed',
  'cancelled',
]);

export const FLOW_ACTIONS = Object.freeze([
  'character_setup',
  'image_generation',
  'video_hook_generation',
  'scene_generation',
]);

export class ContractError extends Error {
  constructor(message, code = 'invalid_contract') {
    super(message);
    this.name = 'ContractError';
    this.code = code;
  }
}

function sortValue(value) {
  if (Array.isArray(value)) return value.map(sortValue);
  if (value && typeof value === 'object') {
    if (value instanceof Date) return value.toISOString();
    const sorted = {};
    for (const key of Object.keys(value).sort()) sorted[key] = sortValue(value[key]);
    return sorted;
  }
  return value;
}

/** Stable JSON used for hashes and deterministic event/request evidence. */
export function canonicalJson(value) {
  return JSON.stringify(sortValue(value));
}

export const canonicalize = canonicalJson;

export function sha256(value) {
  const input = typeof value === 'string' || Buffer.isBuffer(value)
    ? value
    : canonicalJson(value);
  return crypto.createHash('sha256').update(input).digest('hex');
}

export const hashMetadata = sha256;

export function isoNow(clock = () => new Date()) {
  const value = clock();
  const date = value instanceof Date ? value : new Date(value);
  if (Number.isNaN(date.valueOf())) throw new ContractError('clock returned an invalid date');
  return date.toISOString();
}

function isBinary(value) {
  return Buffer.isBuffer(value)
    || value instanceof Uint8Array
    || value instanceof ArrayBuffer
    || (typeof Blob !== 'undefined' && value instanceof Blob);
}

/**
 * Reject binary values and data URLs recursively.  A key such as
 * `output_path` remains valid; only payloads that carry bytes are rejected.
 */
export function assertMetadataOnly(value, path = '$') {
  if (isBinary(value)) throw new ContractError(`${path} contains binary data`, 'binary_payload');
  if (typeof value === 'string') {
    const size = Buffer.byteLength(value, 'utf8');
    if (size > MAX_METADATA_STRING_BYTES) {
      throw new ContractError(`${path} exceeds metadata string limit`, 'metadata_too_large');
    }
    if (/^data:[^,]+,/i.test(value)) {
      throw new ContractError(`${path} contains a data URL`, 'binary_payload');
    }
    return value;
  }
  if (Array.isArray(value)) {
    value.forEach((item, index) => assertMetadataOnly(item, `${path}[${index}]`));
    return value;
  }
  if (value && typeof value === 'object') {
    for (const [key, child] of Object.entries(value)) {
      if (/^(?:bytes|buffer|binary|blob|media_bytes|output_bytes)$/i.test(key)) {
        throw new ContractError(`${path}.${key} is not metadata`, 'binary_payload');
      }
      assertMetadataOnly(child, `${path}.${key}`);
    }
  }
  return value;
}

export function assertNonEmptyString(value, label) {
  if (typeof value !== 'string' || value.trim() === '') {
    throw new ContractError(`${label} must be a non-empty string`);
  }
  return value;
}

export function assertIdentifier(value, label = 'identifier') {
  assertNonEmptyString(value, label);
  if (!/^[A-Za-z0-9][A-Za-z0-9._-]{0,199}$/.test(value)) {
    throw new ContractError(`${label} contains unsafe characters`);
  }
  return value;
}

export function normalizeJob(input, { clock } = {}) {
  if (!input || typeof input !== 'object' || Array.isArray(input)) {
    throw new ContractError('job must be an object');
  }
  assertMetadataOnly(input, '$job');
  const source = structuredClone(input);
  const idempotencyKey = assertNonEmptyString(
    source.idempotency_key ?? source.idempotencyKey,
    'idempotency_key',
  );
  const jobId = source.job_id ?? source.jobId ?? `job-${sha256(idempotencyKey).slice(0, 32)}`;
  assertIdentifier(jobId, 'job_id');
  const createdAt = source.created_at ?? source.createdAt ?? isoNow(clock);
  const normalized = {
    ...source,
    job_id: jobId,
    idempotency_key: idempotencyKey,
    depends_on: source.depends_on ?? source.dependsOn ?? null,
    references: Array.isArray(source.references) ? source.references : [],
    status: source.status ?? 'pending',
    attempt: Number.isInteger(source.attempt) && source.attempt >= 0 ? source.attempt : 0,
    created_at: createdAt,
    updated_at: source.updated_at ?? createdAt,
  };
  if (!QUEUE_STATES.includes(normalized.status) && normalized.status !== 'pending') {
    throw new ContractError(`unsupported queue status: ${normalized.status}`);
  }
  return normalized;
}

export function makeNativeResponse(requestId, result, error = null) {
  assertMetadataOnly(result, '$response');
  const response = {
    protocol_version: NATIVE_PROTOCOL_VERSION,
    request_id: requestId ?? null,
    ok: !error,
  };
  if (error) {
    response.error = {
      code: String(error.code || 'native_error'),
      message: String(error.message || error),
    };
  } else {
    response.result = result ?? null;
  }
  assertMetadataOnly(response, '$response');
  return response;
}

export function isMetadataOnly(value) {
  try {
    assertMetadataOnly(value);
    return true;
  } catch {
    return false;
  }
}
