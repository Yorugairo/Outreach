import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { execSync } from 'node:child_process';

export function sha256File(filePath) {
  if (!fs.existsSync(filePath)) return null;
  const hash = crypto.createHash('sha256');
  hash.update(fs.readFileSync(filePath));
  return hash.digest('hex');
}

export function reverseVideo(inputPath, outputPath) {
  fs.mkdirSync(path.dirname(outputPath), { recursive: true });
  const cmd = `ffmpeg -y -i "${inputPath}" -vf reverse "${outputPath}"`;
  execSync(cmd, { stdio: 'pipe' });
  return outputPath;
}

export function extractVerificationFrames(videoPath, frame0Path, frameEndPath) {
  fs.mkdirSync(path.dirname(frame0Path), { recursive: true });
  fs.mkdirSync(path.dirname(frameEndPath), { recursive: true });
  
  // Extract start frame at 0.1s
  const cmd0 = `ffmpeg -y -ss 0.1 -i "${videoPath}" -frames:v 1 "${frame0Path}"`;
  execSync(cmd0, { stdio: 'pipe' });

  // Extract end frame at -0.1s
  const cmdEnd = `ffmpeg -y -sseof -0.1 -i "${videoPath}" -frames:v 1 "${frameEndPath}"`;
  execSync(cmdEnd, { stdio: 'pipe' });

  return { frame0Path, frameEndPath };
}

export function probeVideo(videoPath) {
  const cmd = `ffprobe -v error -select_streams v:0 -show_entries stream=width,height,duration,r_frame_rate -of json "${videoPath}"`;
  const out = execSync(cmd, { stdio: 'pipe' }).toString();
  const data = JSON.parse(out);
  const stream = data.streams?.[0] || {};
  return {
    width: stream.width,
    height: stream.height,
    duration: stream.duration,
    fps: stream.r_frame_rate,
    aspect_ratio: stream.width && stream.height ? (stream.height > stream.width ? '9:16' : '16:9') : 'unknown',
  };
}

export function writeMetadata(metadataPath, payload) {
  fs.mkdirSync(path.dirname(metadataPath), { recursive: true });
  const manifest = {
    schema_version: 'google_flow_output.v1',
    created_at: new Date().toISOString(),
    ...payload,
  };
  fs.writeFileSync(metadataPath, JSON.stringify(manifest, null, 2), 'utf8');
  return metadataPath;
}
