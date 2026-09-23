import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { execFileSync } from 'node:child_process';

const OUT = path.resolve('content/video_engine/projects/martial-matters/pilots/knockout-brain-matchcut-001/production/animated-variants/flow-test');
const VIDEO = path.join(OUT, 'detailed-2d-motion-test-v1.mp4');
const FRAMES = path.join(OUT, 'contact-frames');
const JOB = path.join(OUT, 'job.json');
const RECEIPT = path.join(OUT, 'receipt.json');
const START = path.resolve('content/video_engine/projects/martial-matters/pilots/knockout-brain-matchcut-001/production/animated-variants/plates/detailed-2d-start-v2.png');
const END = path.resolve('content/video_engine/projects/martial-matters/pilots/knockout-brain-matchcut-001/production/animated-variants/plates/detailed-2d-end-v1.png');
const DOWNLOAD_NAME = 'Fighter_lands_knockout_punch_20260920183837.mp4';
const BROWSER_DOWNLOAD_ARTIFACTS = [
  'C:/Users/Snipe/AppData/Local/Temp/playwright-artifacts-b0hsWd/118f9b15-ec84-4003-9d0b-ce6db1355717',
  'C:/Users/Snipe/AppData/Local/Temp/playwright-artifacts-HNcF7e/d97fc582-1b8e-4bc2-b968-28a03fc20a6e',
];
const ASSET_ID = '784cfd9f-fa95-40d9-80e3-a6da22e93378';
const EDITOR_ID = '402ac862-8916-4b6f-9081-9a3e781a16fa';
const PROMPT = `Continuing from the starting frame, animate a fluid hand-drawn anime MMA exchange in the same wide locked camera. The bald fighter in white shorts on the RIGHT advances and lands a clean RIGHT straight punch against the dark-haired fighter on the LEFT, then the SAME bald fighter lands his LEFT hook. Each glove reaches the opponent's face before the opponent's head recoils. His hips and shoulders drive the punches and his arms complete their follow-through. The dark-haired fighter in black shorts loses balance and falls fully onto the mat while the bald fighter remains standing and stops. At second five the fallen fighter settles onto his side and the standing fighter lowers his guard, with the dark-haired fighter fully grounded and the bald fighter still standing. Preserve the entire fall and floor contact. The exchange is fast and forceful, the characters retain crisp drawn contours and consistent athletic anatomy, and the arena camera keeps both complete bodies visible. Completely silent video, no text or blood.`;

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

function extractFrame(second, target) {
  execFileSync('ffmpeg', [
    '-y', '-v', 'error', '-ss', String(second), '-i', VIDEO,
    '-frames:v', '1', '-an', '-c:v', 'png', target,
  ], { stdio: 'pipe' });
}

if (!fs.existsSync(VIDEO)) throw new Error(`Missing downloaded video: ${VIDEO}`);
if (!fs.existsSync(JOB)) throw new Error(`Missing job record: ${JOB}`);
fs.mkdirSync(FRAMES, { recursive: true });

const data = probe(VIDEO);
const videoStream = data.streams.find((s) => s.codec_type === 'video') || {};
const video = {
  path: VIDEO,
  original_download_filename: DOWNLOAD_NAME,
  sha256: sha256(VIDEO),
  size_bytes: fs.statSync(VIDEO).size,
  duration_s: Number(data.format?.duration || 0),
  format_name: data.format?.format_name || null,
  codec_name: videoStream.codec_name || null,
  width: videoStream.width || null,
  height: videoStream.height || null,
  pix_fmt: videoStream.pix_fmt || null,
  frame_rate: videoStream.r_frame_rate || null,
  audio_streams: data.streams.filter((s) => s.codec_type === 'audio').length,
  audio_note: 'Flow 720p export includes an AAC stereo stream; no audio edit or remix was performed.',
};
writeJson(path.join(OUT, 'ffprobe.json'), data);

const decode = {
  command: `ffmpeg -v error -i ${path.basename(VIDEO)} -f null -`,
  status: 'PASS',
};
execFileSync('ffmpeg', ['-v', 'error', '-i', VIDEO, '-f', 'null', '-'], { stdio: 'pipe' });
writeJson(path.join(OUT, 'decode-check.json'), decode);

const verificationFrames = [];
for (let second = 0; second < 6; second += 1) {
  const frame = path.join(FRAMES, `frame-${second}s.png`);
  extractFrame(second, frame);
  verificationFrames.push({ at_s: second, path: frame, sha256: sha256(frame) });
}

const job = JSON.parse(fs.readFileSync(JOB, 'utf8'));
const resultIdentity = {
  service_ids_seen_before_polling: job.submission?.service_ids_seen_before_polling || [],
  flow_asset_id: ASSET_ID,
  editor_id: EDITOR_ID,
  download_filename: DOWNLOAD_NAME,
  browser_download_artifacts: BROWSER_DOWNLOAD_ARTIFACTS.map((file) => ({ path: file, sha256: sha256(file), size_bytes: fs.statSync(file).size })),
  downloaded_at: new Date().toISOString(),
};
writeJson(JOB, { ...job, result_identity: resultIdentity, artifact: video });

const receipt = {
  schema: 'flow_motion_test_receipt.v2',
  status: 'ready_for_review',
  work_order: '../flow-motion-work-order-v2.md',
  project: 'knockout-brain-matchcut-001',
  generation: {
    attempt_id: job.attempt_id,
    service_ids_seen_before_polling: resultIdentity.service_ids_seen_before_polling,
    flow_asset_id: ASSET_ID,
    editor_id: EDITOR_ID,
    model: job.settings?.modelText || 'Omni 1.1 Flash',
    settings: job.settings,
    credits_spent: job.settings?.credits ?? 10,
    submitted_once: true,
    conditioning: job.conditioning,
  },
  video,
  browser_download_artifacts: resultIdentity.browser_download_artifacts,
  ffprobe: 'ffprobe.json',
  decode_check: 'decode-check.json',
  verification_frames: verificationFrames,
  prompt: PROMPT,
  source_inputs: {
    start: { path: START, sha256: sha256(START), bound: true },
    end: { path: END, sha256: sha256(END), uploaded: true, bound: false },
  },
  review_state: 'review_only_quarantine',
};
writeJson(RECEIPT, receipt);
console.log(JSON.stringify(receipt, null, 2));
