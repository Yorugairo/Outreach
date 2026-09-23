import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { pathToFileURL } from 'node:url';

const ROOT = path.resolve(process.cwd());
const OUT = path.resolve('content/video_engine/projects/martial-matters/pilots/knockout-brain-matchcut-001/production/animated-variants/flow-test');
const PROJECT_URL = 'https://flow.google.com/project/440edc03-c44a-4ff8-bd71-d22a29866386';
const START = path.resolve('content/video_engine/projects/martial-matters/pilots/knockout-brain-matchcut-001/production/animated-variants/plates/detailed-2d-start-v2.png');
const END = path.resolve('content/video_engine/projects/martial-matters/pilots/knockout-brain-matchcut-001/production/animated-variants/plates/detailed-2d-end-v1.png');
const VIDEO = path.join(OUT, 'detailed-2d-flow-test-original.mp4');
const FRAMES = path.join(OUT, 'contact-frames');
const JOB = path.join(OUT, 'job.json');
const RECEIPT = path.join(OUT, 'receipt.json');
const PROMPT = `Continuing from the starting frame, animate a fluid hand-drawn anime MMA exchange in the same wide locked camera. The bald fighter in white shorts on the RIGHT advances and lands a clean RIGHT straight punch against the dark-haired fighter on the LEFT, then the SAME bald fighter lands his LEFT hook. Each glove reaches the opponent's face before the opponent's head recoils. His hips and shoulders drive the punches and his arms complete their follow-through. The dark-haired fighter in black shorts loses balance and falls fully onto the mat while the bald fighter remains standing and stops. At second five the fallen fighter settles onto his side and the standing fighter lowers his guard, with the dark-haired fighter fully grounded and the bald fighter still standing. Preserve the entire fall and floor contact. The exchange is fast and forceful, the characters retain crisp drawn contours and consistent athletic anatomy, and the arena camera keeps both complete bodies visible. Completely silent video, no text or blood.`;

const { FlowCdpDriver } = await import(pathToFileURL(path.join(ROOT, 'tools/google-flow-driver/src/cdp-driver.mjs')).href);

function writeJson(file, value) {
  fs.writeFileSync(file, JSON.stringify(value, null, 2) + '\n', 'utf8');
}

function sha256(file) {
  return crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
}

function probe(file) {
  return JSON.parse(execFileSync('ffprobe', [
    '-v', 'error', '-print_format', 'json', '-show_streams', '-show_format', file,
  ], { encoding: 'utf8' }));
}

function probeSummary(file) {
  const data = probe(file);
  const stream = data.streams?.find((s) => s.codec_type === 'video') || data.streams?.[0] || {};
  return {
    duration_s: Number(data.format?.duration || 0),
    size_bytes: Number(data.format?.size || fs.statSync(file).size),
    format_name: data.format?.format_name || null,
    codec_name: stream.codec_name || null,
    width: stream.width || null,
    height: stream.height || null,
    pix_fmt: stream.pix_fmt || null,
    frame_rate: stream.r_frame_rate || null,
  };
}

function extractFrame(second, target) {
  execFileSync('ffmpeg', [
    '-y', '-v', 'error', '-ss', String(second), '-i', VIDEO,
    '-frames:v', '1', '-an', '-c:v', 'png', target,
  ], { stdio: 'pipe' });
}

function idsFrom(value) {
  const text = typeof value === 'string' ? value : JSON.stringify(value || {});
  return [...new Set(text.match(/[0-9a-f]{8}-[0-9a-f-]{27,}/gi) || [])];
}

fs.mkdirSync(OUT, { recursive: true });
fs.mkdirSync(FRAMES, { recursive: true });
for (const file of [START, END]) {
  if (!fs.existsSync(file)) throw new Error(`Missing work-order input: ${file}`);
}

const attemptId = crypto.randomUUID();
const driver = new FlowCdpDriver({ port: 9223, idleTimeoutMs: 12 * 60 * 1000 });
let page;
const network = [];
const requestListener = (req) => {
  const u = req.url();
  if (!/flow|googleapis|generat|creation|media/i.test(u)) return;
  try {
    const parsed = new URL(u);
    network.push({ kind: 'request', method: req.method(), origin: parsed.origin, pathname: parsed.pathname, ids: idsFrom(parsed.pathname) });
  } catch {}
};
const responseListener = (res) => {
  const u = res.url();
  if (!/flow|googleapis|generat|creation|media/i.test(u)) return;
  try {
    const parsed = new URL(u);
    network.push({ kind: 'response', status: res.status(), origin: parsed.origin, pathname: parsed.pathname, ids: idsFrom(parsed.pathname) });
  } catch {}
};

try {
  page = await driver.getFlowPage(PROJECT_URL);
  page.on('request', requestListener);
  page.on('response', responseListener);

  const settings = await driver.configureSettings({
    mode: 'video',
    submode: 'frames',
    model: 'Omni 1.1 Flash',
    ratio: '9:16',
    duration: 6,
    resolution: '720p',
    count: 1,
    maxCredits: 10,
  });
  // v2 deliberately conditions on the confirmed Start image only. setPrompt clears the
  // existing mention chip, so reattach the already-uploaded start asset; End stays empty.
  await driver.setPrompt(PROMPT);
  await driver.uploadReferences([START]);

  const composer = await page.evaluate(() => ({
    text: (document.querySelector("div[contenteditable='true']")?.innerText || '').replace(/\s+/g, ' ').trim(),
    chips: Array.from(document.querySelectorAll("div[contenteditable='true'] .mention-chip")).map((el) => el.innerText.trim()),
    frameTriggers: Array.from(document.querySelectorAll('.frame-trigger, .empty-chip, .chip-container')).map((el) => ({ text: el.innerText.trim(), hasImg: Boolean(el.querySelector('img')) })),
  }));
  const source = {
    start: { path: START, sha256: sha256(START), bound: true },
    end: { path: END, sha256: sha256(END), uploaded: true, bound: false },
  };
  const conditioning = {
    start_frame: 'detailed-2d-start-v2.png',
    end_frame: null,
    end_frame_policy: 'deliberately_unbound_per_flow_motion_work_order_v2',
  };
  const preSubmitCanvas = await page.evaluate(() => ({
    url: location.href,
    title: document.title,
    videoSrcs: Array.from(document.querySelectorAll('video')).map((v) => v.src || v.getAttribute('src')).filter(Boolean),
    pending: Array.from(document.querySelectorAll('flow-pending-tile')).map((el) => ({ text: el.innerText, attrs: Array.from(el.attributes).map((a) => [a.name, a.value]) })),
  }));
  const preSubmit = { attempt_id: attemptId, project_url: PROJECT_URL, settings, prompt: PROMPT, source, conditioning, composer, pre_submit_canvas: preSubmitCanvas, prepared_at: new Date().toISOString() };
  writeJson(JOB, preSubmit);

  await driver.triggerGeneration();
  await page.waitForTimeout(1500);
  const postSubmitCanvas = await page.evaluate(() => ({
    url: location.href,
    title: document.title,
    pending: Array.from(document.querySelectorAll('flow-pending-tile, [data-generation-id], [data-job-id], [data-id]')).map((el) => ({ tag: el.tagName, text: (el.innerText || '').slice(0, 300), attrs: Array.from(el.attributes).map((a) => [a.name, a.value]) })).slice(0, 20),
    bodyText: (document.body.innerText || '').slice(0, 1200),
  }));
  const serviceIds = [...new Set([...idsFrom(network), ...idsFrom(postSubmitCanvas)])];
  const submission = {
    attempt_id: attemptId,
    submitted_at: new Date().toISOString(),
    acknowledged_before_polling: true,
    service_ids_seen_before_polling: serviceIds,
    network_records_before_polling: network,
    post_submit_canvas: postSubmitCanvas,
  };
  writeJson(JOB, { ...preSubmit, submission });

  await driver.waitForGenerationAndDownload(VIDEO, 420000, 'video', { excludeFiles: [START, END], count: 1 });
  page.removeListener('request', requestListener);
  page.removeListener('response', responseListener);

  const videoProbe = probeSummary(VIDEO);
  const decode = { command: `ffmpeg -v error -i ${path.basename(VIDEO)} -f null -`, status: 'PASS' };
  execFileSync('ffmpeg', ['-v', 'error', '-i', VIDEO, '-f', 'null', '-'], { stdio: 'pipe' });
  for (let second = 0; second < 6; second += 1) {
    extractFrame(second, path.join(FRAMES, `frame-${second}s.png`));
  }
  const receipt = {
    schema: 'flow_motion_test_receipt.v2',
    status: 'ready_for_review',
    work_order: '../flow-motion-work-order-v2.md',
    project: 'knockout-brain-matchcut-001',
    generation: {
      attempt_id: attemptId,
      service_ids_seen_before_polling: submission.service_ids_seen_before_polling,
      model: settings.modelText,
      settings,
      credits_spent: settings.credits,
      submitted_once: true,
      conditioning,
    },
    video: {
      path: VIDEO,
      sha256: sha256(VIDEO),
      ffprobe: 'ffprobe.json',
      decode_check: 'decode-check.json',
      ...videoProbe,
    },
    verification_frames: Array.from({ length: 6 }, (_, second) => ({
      at_s: second,
      path: path.join(FRAMES, `frame-${second}s.png`),
      sha256: sha256(path.join(FRAMES, `frame-${second}s.png`)),
    })),
    prompt: PROMPT,
    source_inputs: source,
    conditioning,
    review_state: 'review_only_quarantine',
  };
  writeJson(path.join(OUT, 'ffprobe.json'), probe(VIDEO));
  writeJson(path.join(OUT, 'decode-check.json'), decode);
  writeJson(RECEIPT, receipt);
  console.log(JSON.stringify(receipt, null, 2));
} catch (error) {
  const failed = { schema: 'flow_motion_test_failure.v1', attempt_id: attemptId, failed_at: new Date().toISOString(), error: String(error?.stack || error), network_records: network };
  writeJson(path.join(OUT, 'failure.json'), failed);
  console.error(JSON.stringify(failed, null, 2));
  process.exitCode = 1;
} finally {
  await driver.disconnect().catch(() => {});
}
