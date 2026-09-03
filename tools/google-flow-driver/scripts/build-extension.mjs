import { cp, mkdir, rm, readdir, stat, readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(scriptDir, '..', '..', '..');
const extensionSourceDir = path.join(repoRoot, 'tools', 'google-flow-driver', 'extension');
const buildRoot = path.join(repoRoot, '.codex', 'flow-extension-build');
const buildArchive = path.join(buildRoot, 'flow-driver-extension.zip');
const buildStaging = path.join(buildRoot, 'extension');
const manifestPath = path.join(extensionSourceDir, 'manifest.json');

function sha256Hex(data) {
  return createHash('sha256').update(data).digest('hex');
}

async function copyRecursive(from, to) {
  await mkdir(to, { recursive: true });
  const entries = await readdir(from, { withFileTypes: true });
  for (const entry of entries) {
    const sourcePath = path.join(from, entry.name);
    const destPath = path.join(to, entry.name);
    if (entry.isDirectory()) {
      await copyRecursive(sourcePath, destPath);
      continue;
    }
    await cp(sourcePath, destPath, { force: true });
  }
}

async function collectFiles(root, prefix = '') {
  const entries = await readdir(root, { withFileTypes: true });
  const out = [];
  for (const entry of entries) {
    const sourcePath = path.join(root, entry.name);
    const relName = prefix ? `${prefix}/${entry.name}` : entry.name;
    if (entry.isDirectory()) {
      out.push(...(await collectFiles(sourcePath, relName)));
      continue;
    }
    if (entry.isFile()) {
      out.push({ name: relName, fullPath: sourcePath });
    }
  }
  return out;
}

function stripModuleSyntax(source) {
  return source
    .replace(/^\s*import\s*\{[\s\S]*?\}\s*from\s*['"][^'"]+['"];\s*/gm, '')
    .replace(/\bexport\s+(?=(?:const|let|var|class|function)\b)/g, '')
    .replace(/\bexport\s*\{[^}]*\};?/g, '');
}

async function bundleContentScript() {
  const sourceRoot = path.join(extensionSourceDir, 'src');
  const parts = [];
  for (const name of ['selectors.js', 'state-machine.js', 'content-script.js']) {
    const source = await readFile(path.join(sourceRoot, name), 'utf8');
    parts.push(`// ---- ${name} ----\n${stripModuleSyntax(source)}`);
  }
  const bundle = `(() => {\n'use strict';\n${parts.join('\n\n')}\ninstallFlowContentScript();\n})();\n`;
  const target = path.join(buildStaging, 'dist', 'content-script.bundle.js');
  await mkdir(path.dirname(target), { recursive: true });
  await writeFile(target, bundle, 'utf8');
  return target;
}

function escapePsArg(value) {
  return `'${String(value).replaceAll('\'', '\'\'')}'`;
}

function createArchive() {
  const command = `Compress-Archive -Path ${escapePsArg(`${buildStaging}\\\\*`)} -DestinationPath ${escapePsArg(buildArchive)} -Force`;
  const hosts = [
    'powershell',
    'pwsh',
    `${process.env.WINDIR}\\System32\\WindowsPowerShell\\v1.0\\powershell.exe`,
  ];
  for (const host of hosts) {
    try {
      if (!host) continue;
      execFileSync(host, ['-NoProfile', '-Command', command], { stdio: 'ignore' });
      return true;
    } catch {
      // Try the next binary.
    }
  }
  return false;
}

async function main() {
  const manifestRaw = await readFile(manifestPath, 'utf8');
  JSON.parse(manifestRaw); // validate JSON shape

  await rm(buildRoot, { recursive: true, force: true });
  await mkdir(buildRoot, { recursive: true });
  await copyRecursive(extensionSourceDir, buildStaging);
  await bundleContentScript();

  const manifestHash = sha256Hex(manifestRaw);
  const files = (await collectFiles(buildStaging)).sort((a, b) => a.name.localeCompare(b.name));
  const hashLines = [];
  for (const file of files) {
    const full = file.fullPath;
    const name = file.name;
    const itemStat = await stat(full);
    if (!itemStat.isFile()) continue;
    const bytes = await readFile(full);
    hashLines.push(`${name}: ${sha256Hex(bytes)}`);
  }
  await writeFile(
    path.join(buildRoot, 'build-manifest.json'),
    JSON.stringify(
      {
        builtAt: new Date().toISOString(),
        manifestHash,
        manifestPath: path.relative(repoRoot, manifestPath).replaceAll(path.sep, '/'),
        artifact: {
          directory: path.relative(repoRoot, buildStaging).replaceAll(path.sep, '/'),
          archive: path.relative(repoRoot, buildArchive).replaceAll(path.sep, '/'),
          fileHashes: hashLines.slice(0, 25),
        },
      },
      null,
      2,
    ),
    'utf8',
  );

  const archived = createArchive();
  const archiveStat = archived ? await stat(buildArchive).catch(() => null) : null;
  const output = {
    builtAt: new Date().toISOString(),
    manifestHash,
    staging: path.relative(repoRoot, buildStaging).replaceAll(path.sep, '/'),
    archive: path.relative(repoRoot, buildArchive).replaceAll(path.sep, '/'),
    archiveBytes: archiveStat?.size ?? null,
  };
  await writeFile(path.join(buildRoot, 'build-result.json'), `${JSON.stringify(output, null, 2)}\n`, 'utf8');
  console.log(JSON.stringify(output, null, 2));
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
