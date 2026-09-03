import path from 'node:path';
import { pathToFileURL } from 'node:url';
import {
  ContractError,
  MAX_NATIVE_REQUEST_BYTES,
  MAX_NATIVE_RESPONSE_BYTES,
  NATIVE_PROTOCOL_VERSION,
  assertMetadataOnly,
  assertNonEmptyString,
  canonicalJson,
  makeNativeResponse,
} from '../shared/contracts.mjs';
import { createQueue } from '../shared/queue.mjs';
import { importOutput } from './import-output.mjs';
import { writeCapabilitySnapshot } from './write-capability.mjs';

export class NativeProtocolError extends Error {
  constructor(message, code = 'invalid_native_message') {
    super(message);
    this.name = 'NativeProtocolError';
    this.code = code;
  }
}

/** Encode one Chrome native-messaging message (uint32 little-endian length). */
export function encodeNativeMessage(payload) {
  try {
    assertMetadataOnly(payload, '$native_payload');
  } catch (error) {
    throw new NativeProtocolError(error.message, error.code || 'binary_payload');
  }
  const body = Buffer.from(canonicalJson(payload), 'utf8');
  if (body.byteLength > MAX_NATIVE_RESPONSE_BYTES) {
    throw new NativeProtocolError('native response exceeds Chrome 1 MiB limit', 'message_too_large');
  }
  const frame = Buffer.allocUnsafe(4 + body.byteLength);
  frame.writeUInt32LE(body.byteLength, 0);
  body.copy(frame, 4);
  return frame;
}

/**
 * Decode as many complete frames as are available. The remainder is retained
 * for the next stdin chunk, making partial pipe reads safe.
 */
export function decodeNativeMessages(input) {
  const buffer = Buffer.isBuffer(input) ? input : Buffer.from(input);
  const messages = [];
  let offset = 0;
  while (buffer.byteLength - offset >= 4) {
    const length = buffer.readUInt32LE(offset);
    if (length > MAX_NATIVE_REQUEST_BYTES) {
      throw new NativeProtocolError('native request exceeds Chrome 64 MiB limit', 'message_too_large');
    }
    if (buffer.byteLength - offset - 4 < length) break;
    const body = buffer.subarray(offset + 4, offset + 4 + length);
    let parsed;
    try {
      parsed = JSON.parse(body.toString('utf8'));
    } catch {
      throw new NativeProtocolError('native message is not valid JSON', 'invalid_json');
    }
    if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) {
      throw new NativeProtocolError('native message must be a JSON object');
    }
    try {
      assertMetadataOnly(parsed, '$native_request');
    } catch (error) {
      throw new NativeProtocolError(error.message, error.code || 'binary_payload');
    }
    messages.push(parsed);
    offset += 4 + length;
  }
  return { messages, remainder: buffer.subarray(offset) };
}

export const encodeMessage = encodeNativeMessage;
export const decodeMessages = decodeNativeMessages;
export const frameNativeMessage = encodeNativeMessage;
export const parseNativeMessages = decodeNativeMessages;

async function dispatch(request, queue, options = {}) {
  if (!request || typeof request !== 'object' || Array.isArray(request)) {
    throw new NativeProtocolError('request must be an object');
  }
  const method = assertNonEmptyString(request.method, 'method');
  const params = request.params && typeof request.params === 'object' ? request.params : {};
  switch (method) {
    case 'ping':
      return { protocol_version: NATIVE_PROTOCOL_VERSION, pong: true };
    case 'status':
    case 'queue_status':
      return queue.status();
    case 'pause_queue':
    case 'pause':
      return queue.pause(params.reason);
    case 'resume_queue':
    case 'resume':
      return queue.resume(params.reason);
    case 'recover':
    case 'recover_active':
      return { recovered: await queue.recoverActive() };
    case 'enqueue': {
      const job = params.job && typeof params.job === 'object' ? params.job : params;
      return queue.enqueue(job);
    }
    case 'claim':
    case 'claim_next':
      return { job: await queue.claimNext() };
    case 'complete':
      return { job: await queue.complete(assertNonEmptyString(params.job_id, 'job_id'), params.result ?? {}) };
    case 'fail':
      return { job: await queue.fail(assertNonEmptyString(params.job_id, 'job_id'), params.error ?? {}) };
    case 'cancel':
    case 'cancel_job':
      return { job: await queue.cancel(assertNonEmptyString(params.job_id, 'job_id'), params.reason) };
    case 'retry_job':
    case 'retry':
      return {
        job: await queue.retry(assertNonEmptyString(params.job_id ?? params.jobId, 'job_id')),
      };
    case 'import_output':
      return importOutput({
        sourcePath: assertNonEmptyString(params.source_path ?? params.sourcePath, 'source_path'),
        outputPath: assertNonEmptyString(params.output_path ?? params.outputPath, 'output_path'),
        projectRoot: options.projectRoot ?? queue.paths.projectRoot,
        downloadsRoot: options.downloadsRoot ?? queue.paths.downloadsRoot,
        quarantineRoot: options.quarantineRoot,
        itemId: params.item_id ?? params.itemId ?? null,
        requestId: params.request_id ?? params.requestId ?? null,
        providerMediaId: params.provider_media_id ?? params.providerMediaId ?? null,
        downloadId: params.download_id ?? params.downloadId ?? null,
        resultPath: params.result_path ?? params.resultPath ?? null,
      });
    case 'write_capability_snapshot':
      return writeCapabilitySnapshot({
        projectRoot: options.projectRoot ?? queue.paths.projectRoot,
        outputPath: assertNonEmptyString(params.output_path ?? params.outputPath, 'output_path'),
        snapshot: params.snapshot,
      });
    case 'get':
    case 'get_job':
      return queue.get(assertNonEmptyString(params.job_id, 'job_id'));
    case 'list':
      return { jobs: await queue.list(params.state ?? null) };
    default:
      throw new NativeProtocolError(`unsupported method: ${method}`, 'unsupported_method');
  }
}

export async function handleNativeRequest(request, queue, options = {}) {
  try {
    const result = await dispatch(request, queue, options);
    return makeNativeResponse(request.request_id ?? request.id ?? null, result);
  } catch (error) {
    return makeNativeResponse(
      request?.request_id ?? request?.id ?? null,
      null,
      error instanceof Error ? error : new Error(String(error)),
    );
  }
}

/** Start a stdio Chrome native host. stdout is reserved for framed JSON. */
export function startNativeHost({
  stdin = process.stdin,
  stdout = process.stdout,
  stderr = process.stderr,
  queue = null,
  projectRoot = process.env.FLOW_PROJECT_ROOT ?? process.cwd(),
  runtimeRoot = process.env.FLOW_RUNTIME_ROOT,
  downloadsRoot = process.env.FLOW_DOWNLOADS_ROOT,
  quarantineRoot = null,
} = {}) {
  const durableQueue = queue ?? createQueue({ projectRoot, runtimeRoot, downloadsRoot });
  const hostOptions = {
    projectRoot: durableQueue.paths.projectRoot,
    downloadsRoot: downloadsRoot ?? durableQueue.paths.downloadsRoot,
    quarantineRoot,
  };
  let remainder = Buffer.alloc(0);
  let serial = Promise.resolve();
  const onData = (chunk) => {
    serial = serial.then(async () => {
      let decoded;
      try {
        decoded = decodeNativeMessages(Buffer.concat([remainder, Buffer.from(chunk)]));
        remainder = decoded.remainder;
      } catch (error) {
        remainder = Buffer.alloc(0);
        const response = makeNativeResponse(null, null, error);
        stdout.write(encodeNativeMessage(response));
        return;
      }
      for (const request of decoded.messages) {
        const response = await handleNativeRequest(request, durableQueue, hostOptions);
        stdout.write(encodeNativeMessage(response));
      }
    }).catch((error) => {
      stderr.write(`[flow-driver] native request failed: ${error.message}\n`);
    });
  };
  stdin.on('data', onData);
  stdin.on('end', () => {
    if (remainder.byteLength > 0) stderr.write('[flow-driver] truncated native message\n');
  });
  return { queue: durableQueue, stop: () => stdin.off('data', onData) };
}

const invokedPath = process.argv[1] ? pathToFileURL(path.resolve(process.argv[1])).href : null;
if (invokedPath === import.meta.url) startNativeHost();
