import fs from 'node:fs/promises';
import path from 'node:path';

import { ContractError, assertMetadataOnly, canonicalJson, sha256 } from '../shared/contracts.mjs';
import { realpathInside } from '../shared/paths.mjs';

export async function writeCapabilitySnapshot({ projectRoot, outputPath, snapshot } = {}) {
  if (!snapshot || typeof snapshot !== 'object' || Array.isArray(snapshot)) {
    throw new ContractError('capability snapshot must be an object');
  }
  assertMetadataOnly(snapshot, '$capability_snapshot');
  if (snapshot.schema_version !== 'google_flow_capability_snapshot.v1') {
    throw new ContractError('unsupported capability snapshot schema');
  }
  const core = { ...snapshot };
  delete core.artifact_hash;
  if (snapshot.artifact_hash !== sha256(core)) throw new ContractError('capability artifact_hash is stale');
  const destination = await realpathInside(projectRoot, outputPath, 'capability output_path');
  if (path.extname(destination).toLowerCase() !== '.json') throw new ContractError('capability output must be JSON');
  await fs.mkdir(path.dirname(destination), { recursive: true });
  const body = `${JSON.stringify(snapshot, null, 2)}\n`;
  const existing = await fs.readFile(destination, 'utf8').catch((error) => {
    if (error?.code === 'ENOENT') return null;
    throw error;
  });
  if (existing !== null) {
    if (canonicalJson(JSON.parse(existing)) === canonicalJson(snapshot)) {
      return { output_path: path.relative(projectRoot, destination).split(path.sep).join('/'), artifact_hash: snapshot.artifact_hash, existing: true };
    }
    throw new ContractError('capability destination already exists with different content', 'immutable_conflict');
  }
  const temporary = `${destination}.${process.pid}.${Date.now()}.tmp`;
  try {
    await fs.writeFile(temporary, body, { encoding: 'utf8', flag: 'wx' });
    await fs.rename(temporary, destination);
  } finally {
    await fs.unlink(temporary).catch(() => {});
  }
  return {
    output_path: path.relative(projectRoot, destination).split(path.sep).join('/'),
    artifact_hash: snapshot.artifact_hash,
    existing: false,
  };
}

