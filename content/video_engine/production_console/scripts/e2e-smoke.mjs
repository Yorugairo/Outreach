import {createServer} from 'node:http';
import {readFile} from 'node:fs/promises';
import {extname, resolve} from 'node:path';
import {chromium} from 'playwright-core';

const hash = (character) => character.repeat(64);
const digest = hash('a');
const asset = {asset_id: 'visual-1', label: 'Bubble comparison', sha256: digest, source_kind: 'production_visual', approval_scope: 'production_visuals', evidence_eligible: true, rights_state: 'operator_authorized', context_status: 'operator_verified', deck_id: 'fixture-deck', slide_number: 1, width: 1376, height: 768, what_it_is: 'Browser proof fixture.', claim_refs: [], cue_refs: []};
const track = (track_id, kind, order, editable, items = []) => ({track_id, kind, order, editable, label: kind.replace('_', ' '), items});
const snapshot = {
  schema_version: 'production_console_snapshot.v2', snapshot_id: 'e2e-v2', project_id: 'e2e', composition_id: 'ProductionTimeline',
  project_profile: {profile_id: 'landscape', fps: 30, width: 1920, height: 1080, duration_s: 10, duration_frames: 300, audio: {audio_id: 'canonical-narration', sha256: digest, duration_s: 10, status: 'missing'}, audio_trim: {start_s: 0, end_s: 10, start_frame: 0, end_frame: 300}},
  base_artifact_hashes: {flow: digest}, artifact_hash: hash('b'), degraded_inputs: [], reviews: [],
  scenes: [{scene_id: 'scene-1', title: 'Valuation paradox', start_s: 0, end_s: 10, start_frame: 0, end_frame: 300, cue_refs: ['cue-1'], claim_refs: [], asset_ids: [], review_state: 'unreviewed'}],
  cues: [{cue_id: 'cue-1', start_word: 0, end_word: 0, start_s: 0, end_s: 10, start_frame: 0, end_frame: 300, excerpt: 'Market', state_type: 'hook', visual_world: 'whiteboard'}],
  words: [{word_id: 'word-1', text: 'Market', start_s: 0, end_s: .2, start_frame: 0, end_frame: 6}],
  tracks: [
    track('track-scenes', 'scenes', 0, false, [{item_id: 'scene-item-1', item_type: 'scene', start_frame: 0, end_frame: 300, locked: false, locked_fields: [], scene_id: 'scene-1'}]),
    track('track-cues', 'cues', 1, false, [{item_id: 'cue-item-1', item_type: 'cue', start_frame: 0, end_frame: 300, locked: false, locked_fields: [], cue_id: 'cue-1', scene_id: 'scene-1'}]),
    track('track-captions', 'captions', 2, true, [{item_id: 'caption-1', item_type: 'caption', start_frame: 0, end_frame: 300, locked: false, locked_fields: ['text', 'word_timing'], text: 'Market', start_word: 0, end_word: 0}]),
    track('track-overlays', 'overlays', 3, true), track('track-teacher_stamp', 'teacher_stamp', 4, false), track('track-evidence', 'evidence', 5, true), track('track-world_plates', 'world_plates', 6, true), track('track-narration', 'narration', 7, false),
  ],
  assets: [asset], approved_assets: [asset], locks: {narration: true, transcript: true, word_timing: true}, waveform: {audio_sha256: digest, cache_key: digest, sample_count: 4, peaks: [.2, .7, .4, .8], status: 'derived'},
  component_catalog: {schema_version: 'editor_component_catalog.v1', catalog_id: 'catalog', catalog_version: '1.0.0', remotion_version: '4.0.502', components: [{component_id: 'fade-in', label: 'Fade In', kind: 'remotion_bit', adapter_id: 'fade-in', source: 'remotion_bits', version: '0.2.0', deterministic: true, allowed_prop_keys: ['text'], preset_ids: ['fade-in-default']}], presets: [{preset_id: 'fade-in-default', component_id: 'fade-in', label: 'Fade In default', props: {style_id: 'default'}}], catalog_hash: digest, artifact_hash: digest}, component_catalog_hash: digest,
  plate_layout_profiles: {schema_version: 'plate_layout_profiles.v1', default_profile_id: 'generic-manual-only', profiles: [], artifact_hash: digest}, semantic_evidence_bindings: [],
};
const svg = Buffer.from(`<svg xmlns="http://www.w3.org/2000/svg" width="1376" height="768"><rect width="100%" height="100%" fill="#f2eee4"/><text x="80" y="150" font-size="72">P30 approved evidence</text></svg>`);
const mime = {'.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.svg': 'image/svg+xml'};
let savedRevision = null;
const server = createServer(async (request, response) => {
  try {
    if (request.url === '/api/health') return void response.end(JSON.stringify({status: 'ready'}));
    if (request.url === '/api/editor/snapshot') return void response.end(JSON.stringify(snapshot));
    if (request.url === '/api/editor/revisions/validate' || request.url === '/api/editor/revisions') {
      const chunks = [];
      for await (const chunk of request) chunks.push(chunk);
      savedRevision = JSON.parse(Buffer.concat(chunks).toString('utf8'));
      return void response.end(JSON.stringify({ok: true, data: request.url.endsWith('validate') ? {valid: true, revision_id: savedRevision.revision_id, artifact_hash: savedRevision.artifact_hash} : {revision_id: savedRevision.revision_id, artifact_hash: savedRevision.artifact_hash}}));
    }
    if (request.url === '/media/visual-1') {response.setHeader('Content-Type', 'image/svg+xml'); return void response.end(svg);}
    const rawPath = request.url === '/' ? '/index.html' : request.url?.split('?')[0] ?? '/index.html';
    const file = resolve('dist', `.${rawPath}`);
    const body = await readFile(file);
    response.setHeader('Content-Type', mime[extname(file)] ?? 'application/octet-stream');
    response.end(body);
  } catch {response.statusCode = 404; response.end('not found');}
});

await new Promise((ready) => server.listen(0, '127.0.0.1', ready));
const address = server.address();
if (!address || typeof address === 'string') throw new Error('Smoke server failed to bind.');
const chrome = process.env.CHROME_PATH ?? 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const browser = await chromium.launch({headless: true, executablePath: chrome});
try {
  const page = await browser.newPage({viewport: {width: 1800, height: 1200}});
  await page.goto(`http://127.0.0.1:${address.port}`, {waitUntil: 'networkidle'});
  await page.getByText('Interactive Production Editor', {exact: true}).waitFor();
  await page.getByText('Bubble comparison', {exact: true}).click();
  await page.getByRole('button', {name: 'Create'}).click();
  await page.getByText('Overlay text', {exact: true}).click();
  const xField = page.getByRole('spinbutton', {name: 'X', exact: true});
  await xField.fill('0.15');
  await page.getByRole('button', {name: '◇ opacity'}).click();
  await page.getByRole('button', {name: 'Save immutable revision'}).click();
  await page.getByText(/Saved revision-/).waitFor();
  if (!savedRevision?.operations?.some((operation) => operation.op === 'insert_item')) throw new Error('Revision did not contain inserted items.');
  await page.reload({waitUntil: 'networkidle'});
  await page.getByText('Interactive Production Editor', {exact: true}).waitFor();
  if (!(await page.getByText('Edit this on-screen text', {exact: true}).count())) throw new Error('Local draft did not recover after reload.');
  if (process.env.E2E_SCREENSHOT) await page.screenshot({path: process.env.E2E_SCREENSHOT, fullPage: true});
  console.log('P31 timeline/canvas/save/reload browser proof: PASS');
} finally {await browser.close(); server.close();}
