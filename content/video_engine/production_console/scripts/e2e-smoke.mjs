import {createServer} from 'node:http';
import {readFile} from 'node:fs/promises';
import {extname, resolve} from 'node:path';
import {chromium} from 'playwright-core';

const hash = (character) => character.repeat(64);
const snapshot = {
  schema_version: 'production_console_snapshot.v1', snapshot_id: 'e2e-v1', project_id: 'e2e', composition_id: 'ProductionEvidence',
  base_artifact_hashes: {flow: hash('a')}, artifact_hash: hash('b'), degraded_inputs: [], reviews: [],
  scenes: [{scene_id: 'scene-1', title: 'Valuation paradox', start_s: 0, end_s: 5, cue_refs: ['cue-1'], claim_refs: [], asset_ids: [], review_state: 'unreviewed'}],
  words: [{word_id: 'word-1', text: 'Market', start_s: 0, end_s: .2}],
  assets: [{asset_id: 'visual-1', label: 'Bubble comparison', sha256: hash('c'), source_kind: 'production_visual', approval_scope: 'production_visuals', evidence_eligible: false, rights_state: 'operator_authorized', context_status: 'review_only', deck_id: 'fixture-deck', slide_number: 1, width: 1376, height: 768, what_it_is: 'Browser smoke fixture.', claim_refs: [], cue_refs: []}],
};
const svg = Buffer.from(`<svg xmlns="http://www.w3.org/2000/svg" width="1376" height="768"><rect width="100%" height="100%" fill="#f2eee4"/><text x="80" y="150" font-size="72">Gate A production visual</text></svg>`);
const mime = {'.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.svg': 'image/svg+xml'};
const server = createServer(async (request, response) => {
  try {
    if (request.url === '/api/health') return void response.end(JSON.stringify({status: 'ready'}));
    if (request.url === '/api/snapshot') return void response.end(JSON.stringify(snapshot));
    if (request.url === '/media/visual-1') { response.setHeader('Content-Type', 'image/svg+xml'); return void response.end(svg); }
    const rawPath = request.url === '/' ? '/index.html' : request.url?.split('?')[0] ?? '/index.html';
    const file = resolve('dist', `.${rawPath}`);
    const body = await readFile(file);
    response.setHeader('Content-Type', mime[extname(file)] ?? 'application/octet-stream');
    response.end(body);
  } catch {
    response.statusCode = 404;
    response.end('not found');
  }
});

await new Promise((resolveReady) => server.listen(0, '127.0.0.1', resolveReady));
const address = server.address();
if (!address || typeof address === 'string') throw new Error('Smoke server failed to bind.');
const chrome = process.env.CHROME_PATH ?? 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const browser = await chromium.launch({headless: true, executablePath: chrome});
try {
  const page = await browser.newPage({viewport: {width: 1600, height: 1050}});
  await page.goto(`http://127.0.0.1:${address.port}`, {waitUntil: 'networkidle'});
  await page.getByText('Production Console', {exact: true}).waitFor();
  if (!(await page.getByText('Approved visual', {exact: true}).isVisible())) throw new Error('Production approval is not visible.');
  if (!(await page.getByText('Claim support', {exact: true}).isVisible())) throw new Error('Claim-support boundary is not visible.');
  if (!(await page.getByText('Not granted', {exact: true}).isVisible())) throw new Error('Negative claim-support state is not visible.');
  if (await page.getByRole('button', {name: 'Save immutable revision'}).isEnabled()) throw new Error('Gate A mutation control is enabled.');
  if (process.env.E2E_SCREENSHOT) await page.screenshot({path: process.env.E2E_SCREENSHOT, fullPage: true});
  console.log('Gate A browser smoke: PASS');
} finally {
  await browser.close();
  server.close();
}
