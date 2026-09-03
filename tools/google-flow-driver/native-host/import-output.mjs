import crypto from 'node:crypto';
import fs from 'node:fs/promises';
import path from 'node:path';

import { canonicalJson } from '../shared/contracts.mjs';
import { realpathInside, resolveInside } from '../shared/paths.mjs';

export const FLOW_OUTPUT_IMPORT_VERSION = 'flow-output-import.v1';
export const FLOW_QUARANTINE_DIRECTORY = path.join('assets', 'quarantine', 'flow');

const MEDIA_TYPES = Object.freeze({
  '.png': { mimeType: 'image/png', magic: (bytes) => bytes.length >= 8 && bytes.subarray(0, 8).equals(Buffer.from([137, 80, 78, 71, 13, 10, 26, 10])) },
  '.jpg': { mimeType: 'image/jpeg', magic: (bytes) => bytes.length >= 3 && bytes[0] === 0xff && bytes[1] === 0xd8 && bytes[2] === 0xff },
  '.jpeg': { mimeType: 'image/jpeg', magic: (bytes) => bytes.length >= 3 && bytes[0] === 0xff && bytes[1] === 0xd8 && bytes[2] === 0xff },
  '.webp': { mimeType: 'image/webp', magic: (bytes) => bytes.length >= 12 && bytes.subarray(0, 4).toString('ascii') === 'RIFF' && bytes.subarray(8, 12).toString('ascii') === 'WEBP' },
  '.gif': { mimeType: 'image/gif', magic: (bytes) => bytes.length >= 6 && ['GIF87a', 'GIF89a'].includes(bytes.subarray(0, 6).toString('ascii')) },
  '.mp4': { mimeType: 'video/mp4', magic: (bytes) => bytes.length >= 12 && bytes.subarray(4, 8).toString('ascii') === 'ftyp' },
  '.m4v': { mimeType: 'video/x-m4v', magic: (bytes) => bytes.length >= 12 && bytes.subarray(4, 8).toString('ascii') === 'ftyp' },
  '.mov': { mimeType: 'video/quicktime', magic: (bytes) => bytes.length >= 12 && bytes.subarray(4, 8).toString('ascii') === 'ftyp' },
  '.webm': { mimeType: 'video/webm', magic: (bytes) => bytes.length >= 4 && bytes.subarray(0, 4).equals(Buffer.from([0x1a, 0x45, 0xdf, 0xa3])) },
});

export class OutputImportError extends Error {
  constructor(code, message = code, details = {}) {
    super(message);
    this.name = 'OutputImportError';
    this.code = code;
    this.details = details;
  }
}

function absolute(value) {
  return path.resolve(String(value));
}

function deepFreeze(value, seen = new Set()) {
  if (!value || typeof value !== 'object' || seen.has(value)) return value;
  seen.add(value);
  for (const child of Object.values(value)) deepFreeze(child, seen);
  return Object.freeze(value);
}

async function fileHash(filePath) {
  const hash = crypto.createHash('sha256');
  const handle = await fs.open(filePath, 'r');
  try {
    for (;;) {
      const { bytesRead, buffer } = await handle.read({ buffer: Buffer.allocUnsafe(1024 * 1024), position: null });
      if (!bytesRead) break;
      hash.update(buffer.subarray(0, bytesRead));
    }
  } finally {
    await handle.close();
  }
  return hash.digest('hex');
}

export const hashFile = fileHash;

function quarantineRootFor(projectRoot, candidate) {
  return absolute(candidate || path.join(projectRoot, FLOW_QUARANTINE_DIRECTORY));
}

function destinationPathFor(projectRoot, quarantineRoot, candidate) {
  if (candidate === undefined || candidate === null || String(candidate).trim() === '') {
    throw new OutputImportError('missing_output_path', 'An output path is required');
  }
  const raw = String(candidate);
  if (path.isAbsolute(raw)) {
    try {
      return resolveInside(projectRoot, raw, 'output_path');
    } catch (error) {
      throw new OutputImportError('unsafe_quarantine_path', error.message, { cause: error });
    }
  }
  // A project-relative quarantine path is convenient in manifests; a bare
  // filename is interpreted relative to the configured quarantine root.
  let projectCandidate;
  try {
    projectCandidate = resolveInside(projectRoot, raw, 'output_path');
  } catch (error) {
    throw new OutputImportError('unsafe_quarantine_path', error.message, { cause: error });
  }
  const quarantineCandidate = resolveInside(quarantineRoot, raw, 'output_path');
  const projectRelative = path.relative(quarantineRoot, projectCandidate);
  if (projectRelative !== '..' && !projectRelative.startsWith(`..${path.sep}`) && !path.isAbsolute(projectRelative)) {
    return projectCandidate;
  }
  return quarantineCandidate;
}

function assertQuarantinePath(quarantineRoot, candidate) {
  const relative = path.relative(quarantineRoot, candidate);
  if (relative === '..' || relative.startsWith(`..${path.sep}`) || path.isAbsolute(relative)) {
    throw new OutputImportError('unsafe_quarantine_path', 'Output must remain inside the project Flow quarantine root');
  }
  return candidate;
}

async function assertRegularFile(filePath, label) {
  let info;
  try { info = await fs.lstat(filePath); } catch (error) {
    if (error?.code === 'ENOENT') throw new OutputImportError('missing_output', `${label} does not exist`);
    throw error;
  }
  if (info.isSymbolicLink()) throw new OutputImportError('symlink_output', `${label} may not be a symbolic link`);
  if (!info.isFile()) throw new OutputImportError('not_a_file', `${label} must be a regular file`);
  if (info.size <= 0) throw new OutputImportError('empty_output', `${label} is empty`);
  return info;
}

function detectMediaType(filePath, bytes) {
  const extension = path.extname(filePath).toLowerCase();
  const type = MEDIA_TYPES[extension];
  if (!type) throw new OutputImportError('unsupported_media_type', `Flow media extension is not supported: ${extension || '(none)'}`);
  if (!type.magic(bytes)) throw new OutputImportError('invalid_media_bytes', `Flow output does not match its ${extension} media signature`);
  return { extension, ...type };
}

/** Validate a downloaded Flow image or video without writing it. */
export async function validateOutputFile(sourcePath, { allowUnknownFormat = false } = {}) {
  const info = await assertRegularFile(sourcePath, 'downloaded output');
  const bytes = await fs.readFile(sourcePath);
  let type;
  try {
    type = detectMediaType(sourcePath, bytes);
  } catch (error) {
    if (!allowUnknownFormat) throw error;
    type = { extension: path.extname(sourcePath).toLowerCase() || null, mimeType: 'application/octet-stream' };
  }
  return {
    path: sourcePath,
    bytes: info.size,
    sha256: crypto.createHash('sha256').update(bytes).digest('hex'),
    mimeType: type.mimeType,
    extension: type.extension,
  };
}

async function writeImmutableReceipt(receiptPath, result) {
  const absoluteReceipt = receiptPath;
  await fs.mkdir(path.dirname(absoluteReceipt), { recursive: true });
  const body = `${JSON.stringify(result, null, 2)}\n`;
  try {
    await fs.writeFile(absoluteReceipt, body, { encoding: 'utf8', flag: 'wx' });
  } catch (error) {
    if (error?.code !== 'EEXIST') throw error;
    const existing = await fs.readFile(absoluteReceipt, 'utf8');
    if (existing !== body) throw new OutputImportError('receipt_conflict', 'An immutable output receipt already exists with different content');
  }
  return absoluteReceipt;
}

function artifactHash(result) {
  const body = { ...result };
  delete body.artifact_hash;
  delete body.artifactHash;
  return crypto.createHash('sha256').update(canonicalJson(body), 'utf8').digest('hex');
}

/**
 * Validate and copy a Chrome download into the project Flow quarantine.
 * Existing identical destinations are reused; a different destination is a
 * hard conflict so a retry/restart can never silently overwrite evidence.
 */
export async function importOutput({
  sourcePath,
  downloadPath,
  outputPath,
  destinationPath,
  projectRoot,
  quarantineRoot,
  downloadsRoot,
  downloadRoot,
  itemId = null,
  requestId = null,
  providerMediaId = null,
  downloadId = null,
  resultPath = null,
  allowUnknownFormat = false,
  clock = () => new Date(),
} = {}) {
  const sourceCandidate = sourcePath ?? downloadPath;
  if (!sourceCandidate) throw new OutputImportError('missing_source_path', 'A downloaded output path is required');
  if (!projectRoot) throw new OutputImportError('missing_project_root', 'projectRoot is required');
  if (!downloadsRoot && !downloadRoot) throw new OutputImportError('missing_download_root', 'downloadsRoot is required');

  const normalizedProjectRoot = absolute(projectRoot);
  const normalizedDownloadsRoot = absolute(downloadsRoot ?? downloadRoot);
  const normalizedQuarantineRoot = quarantineRootFor(normalizedProjectRoot, quarantineRoot);
  try {
    // Validate the configured quarantine root before creating it; a caller may
    // not redirect imports through an arbitrary absolute directory or symlink.
    resolveInside(normalizedProjectRoot, normalizedQuarantineRoot, 'quarantine_root');
    await realpathInside(normalizedProjectRoot, normalizedQuarantineRoot, 'quarantine_root');
  } catch (error) {
    throw new OutputImportError('unsafe_quarantine_path', error.message, { cause: error });
  }
  await fs.mkdir(normalizedQuarantineRoot, { recursive: true });

  // Check the lexical source entry before realpath resolution.  Otherwise a
  // symlink inside the downloads root would resolve to a regular target and
  // lose its provenance at the import boundary.
  let lexicalSource;
  try {
    lexicalSource = resolveInside(normalizedDownloadsRoot, sourceCandidate, 'source_path');
  } catch (error) {
    throw new OutputImportError('unsafe_source_path', error.message, { cause: error });
  }
  const lexicalInfo = await fs.lstat(lexicalSource).catch((error) => {
    if (error?.code === 'ENOENT') throw new OutputImportError('missing_output', 'downloaded output does not exist');
    throw error;
  });
  if (lexicalInfo.isSymbolicLink()) throw new OutputImportError('symlink_output', 'Downloaded output may not be a symbolic link');

  const source = await realpathInside(normalizedDownloadsRoot, sourceCandidate, 'source_path');
  const destination = destinationPathFor(normalizedProjectRoot, normalizedQuarantineRoot, outputPath ?? destinationPath);
  assertQuarantinePath(normalizedQuarantineRoot, destination);
  await assertRegularFile(source, 'downloaded output');
  await realpathInside(normalizedDownloadsRoot, source, 'source_path');
  await realpathInside(normalizedProjectRoot, destination, 'output_path');

  const validation = await validateOutputFile(source, { allowUnknownFormat });
  const existing = await fs.lstat(destination).catch((error) => {
    if (error?.code === 'ENOENT') return null;
    throw error;
  });
  if (existing?.isSymbolicLink()) throw new OutputImportError('symlink_output', 'Destination may not be a symbolic link');
  if (existing && !existing.isFile()) throw new OutputImportError('destination_not_file');

  let reused = false;
  if (existing) {
    const existingHash = await fileHash(destination);
    if (existingHash !== validation.sha256) {
      throw new OutputImportError('destination_conflict', 'Immutable quarantine destination already contains different bytes', {
        destination,
        existingSha256: existingHash,
        sourceSha256: validation.sha256,
      });
    }
    reused = true;
  } else {
    await fs.mkdir(path.dirname(destination), { recursive: true });
    const temporary = `${destination}.${process.pid}.${crypto.randomBytes(8).toString('hex')}.tmp`;
    try {
      await fs.copyFile(source, temporary, crypto.constants.COPYFILE_EXCL);
      await fs.rename(temporary, destination);
    } catch (error) {
      await fs.rm(temporary, { force: true }).catch(() => {});
      if (error?.code !== 'EEXIST') throw error;
      const existingHash = await fileHash(destination);
      if (existingHash !== validation.sha256) throw new OutputImportError('destination_conflict', 'Concurrent import produced different bytes');
      reused = true;
    }
    await assertRegularFile(destination, 'quarantined output');
  }

  const importedAt = (() => {
    try { return new Date(typeof clock === 'function' ? clock() : clock).toISOString(); }
    catch { return new Date().toISOString(); }
  })();
  const result = {
    schema_version: FLOW_OUTPUT_IMPORT_VERSION,
    item_id: itemId == null ? null : String(itemId),
    request_id: requestId == null ? null : String(requestId),
    provider_media_id: providerMediaId == null ? null : String(providerMediaId),
    download_id: downloadId == null ? null : downloadId,
    source_path: source,
    output_path: destination,
    project_relative_path: path.relative(normalizedProjectRoot, destination).split(path.sep).join('/'),
    size_bytes: validation.bytes,
    sha256: validation.sha256,
    output_sha256: validation.sha256,
    mime_type: validation.mimeType,
    content_type: validation.mimeType,
    imported_at: importedAt,
    reused,
    review_state: 'quarantined',
    render_eligible: false,
  };
  result.artifact_hash = artifactHash(result);
  const frozen = deepFreeze(result);
  if (resultPath) {
    const receipt = await realpathInside(normalizedQuarantineRoot, resultPath, 'result_path');
    await writeImmutableReceipt(receipt, frozen);
  }
  return frozen;
}

export const validateAndImportOutput = importOutput;
export const importDownloadedOutput = importOutput;
export const importDownloadedFile = importOutput;
export const hashAndImportOutput = importOutput;
