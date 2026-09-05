import fs from 'node:fs';
import path from 'node:path';
import { FlowDagEngine } from '../src/dag-engine.mjs';

const batchFile = process.argv[2];
if (!batchFile) {
  console.error('Usage: node run-batch.mjs <path-to-batch.json>');
  process.exit(1);
}

const resolvedPath = path.isAbsolute(batchFile) ? batchFile : path.resolve(process.cwd(), batchFile);
if (!fs.existsSync(resolvedPath)) {
  console.error('Batch file not found: ' + resolvedPath);
  process.exit(1);
}

console.log('[run-batch] Loading batch specification: ' + resolvedPath);
const batch = JSON.parse(fs.readFileSync(resolvedPath, 'utf8'));

const engine = new FlowDagEngine();
console.log('[run-batch] Dispatching ' + (batch.scenes ? batch.scenes.length : 0) + ' scene(s) to FlowDagEngine...');

try {
  const result = await engine.generateBatch(batch);
  console.log('[run-batch] Batch completed successfully:');
  console.log(JSON.stringify(result, null, 2));
  if (engine.driver) await engine.driver.disconnect();
  process.exit(0);
} catch (err) {
  console.error('[run-batch] Generation failed:', err.message);
  if (engine.driver) await engine.driver.disconnect().catch(() => {});
  process.exit(1);
}
