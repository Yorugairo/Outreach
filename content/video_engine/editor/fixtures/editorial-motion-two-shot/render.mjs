import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { spawnSync } from "node:child_process";

const fixtureDir = path.dirname(fileURLToPath(import.meta.url));
const editorDir = path.resolve(fixtureDir, "..", "..");
const runtimeDir = path.resolve(editorDir, "..", "runtime");
const outputDir = path.join(runtimeDir, "jobs", "p16-fixture");
const outputPath = path.join(outputDir, "editorial-motion-two-shot.mp4");
const propsPath = path.join(fixtureDir, "props.json");
const publicDir = path.join(fixtureDir, "public");

const requiredFiles = [
  propsPath,
  path.join(publicDir, "assets", "establish.svg"),
  path.join(publicDir, "assets", "detail.svg"),
  path.join(publicDir, "audio", "canonical-fixture.wav"),
];
for (const file of requiredFiles) {
  if (!fs.statSync(file, { throwIfNoEntry: false })?.isFile()) {
    throw new Error(`editorial-motion fixture file is missing: ${file}`);
  }
}

fs.mkdirSync(outputDir, { recursive: true });
const args = [
  "--no-install",
  "remotion",
  "render",
  "src/index.tsx",
  "EditorialMotion",
  `--props=${propsPath}`,
  `--public-dir=${publicDir}`,
  "--codec=h264",
  outputPath,
];
const npx = process.platform === "win32" ? process.execPath : "npx";
const npxArgs = process.platform === "win32"
  ? [
      path.resolve(path.dirname(process.execPath), "node_modules", "npm", "bin", "npx-cli.js"),
      ...args,
    ]
  : args;
const result = spawnSync(npx, npxArgs, {
  cwd: editorDir,
  stdio: "inherit",
  windowsHide: true,
});
if (result.error) throw result.error;
if (result.status !== 0) {
  process.exit(result.status ?? 1);
}
console.log(`EditorialMotion fixture rendered to ${outputPath}`);
