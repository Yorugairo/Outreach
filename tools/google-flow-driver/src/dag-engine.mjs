import path from 'node:path';
import { FlowCdpDriver } from './cdp-driver.mjs';
import {
  reverseVideo,
  extractVerificationFrames,
  probeVideo,
  sha256File,
  writeMetadata,
} from './postprocess.mjs';

export class FlowDagEngine {
  constructor(options = {}) {
    this.driver = new FlowCdpDriver(options);
  }

  async generateVideo({
    prompt,
    references = [],
    mode = 'video',          // 'video' | 'image' - ALWAYS set; the project's last state is never trusted
    submode = 'ingredients', // 'ingredients' (reference images) | 'frames' (start/end frame)
    model = null,            // exact model label as Flow shows it, e.g. 'Omni 1.1 Flash'
    count = 1,               // outputs per generation x1..x4 - credits scale with it
    maxCredits = null,       // refuse the scene if Flow quotes more than this
    ratio = null,            // null = preserve canvas ratio; '9:16' or '16:9'
    duration = null,         // e.g. 6
    resolution = null,       // e.g. '720p'
    reverse = false,         // true = apply ffmpeg reversal for ending-frame lock
    outputPath,
    projectUrl = null,
  }) {
    if (!prompt || typeof prompt !== 'string') {
      throw new Error('prompt is required and must be a string.');
    }
    if (!outputPath) {
      throw new Error('outputPath is required.');
    }

    const targetDir = path.dirname(outputPath);
    const baseName = path.basename(outputPath, path.extname(outputPath));
    const rawPath = path.join(targetDir, `${baseName}-raw.mp4`);
    const finalVideoPath = reverse ? path.join(targetDir, `${baseName}-reversed.mp4`) : outputPath;

    // 1. Connect and ensure Flow page
    await this.driver.getFlowPage(projectUrl);

    // 2. Set the generation state and READ IT BACK - never preserve whatever the project was left on.
    const settings = await this.driver.configureSettings({ mode, submode, model, ratio, duration, resolution, count, maxCredits });

    // 3. Upload References (up to 3)
    if (references && references.length > 0) {
      await this.driver.uploadReferences(references);
    }

    // 4. Inject Prompt
    await this.driver.setPrompt(prompt);

    // 5. Submit Generation
    await this.driver.triggerGeneration();

    // 6. Wait for Generation & Download
    await this.driver.waitForGenerationAndDownload(rawPath);

    // 7. Post-Processing
    let activeVideoPath = rawPath;
    if (reverse) {
      console.log(`[FlowDagEngine] Applying FFmpeg reversal to ${rawPath} -> ${finalVideoPath}...`);
      reverseVideo(rawPath, finalVideoPath);
      activeVideoPath = finalVideoPath;
    } else if (rawPath !== outputPath) {
      // If no reversal requested and rawPath != outputPath, save directly to outputPath
      activeVideoPath = outputPath;
      import('node:fs').then(fs => fs.copyFileSync(rawPath, outputPath));
    }

    // 8. Extract verification frames
    const frame0Path = path.join(targetDir, `${baseName}_frame_0.png`);
    const frameEndPath = path.join(targetDir, `${baseName}_frame_end.png`);
    extractVerificationFrames(activeVideoPath, frame0Path, frameEndPath);

    // 9. Probe video
    const probe = probeVideo(activeVideoPath);

    // 10. Write Metadata Manifest
    const metadataPath = path.join(targetDir, `${baseName}_meta.json`);
    const metadata = {
      prompt,
      references,
      requested_ratio: ratio || 'preserved',
      detected_dimensions: `${probe.width}x${probe.height}`,
      aspect_ratio: probe.aspect_ratio,
      duration_seconds: probe.duration,
      reversed: reverse,
      files: {
        video: { path: activeVideoPath, sha256: sha256File(activeVideoPath) },
        raw_video: { path: rawPath, sha256: sha256File(rawPath) },
        frame_start: { path: frame0Path, sha256: sha256File(frame0Path) },
        frame_end: { path: frameEndPath, sha256: sha256File(frameEndPath) },
      },
    };
    writeMetadata(metadataPath, metadata);

    return {
      success: true,
      videoPath: activeVideoPath,
      rawVideoPath: rawPath,
      frame0Path,
      frameEndPath,
      metadataPath,
      probe,
    };
  }

  async generateBatch(batch = {}) {
    const {
      projectUrl = null,
      outputDir,
      scenes = [],
      ratio = null,
    } = batch;
    if (!Array.isArray(scenes) || scenes.length === 0) {
      throw new Error('scenes must be a non-empty array.');
    }
    if (!outputDir) {
      throw new Error('outputDir is required.');
    }

    const results = [];
    let previousSceneResult = null;

    for (let i = 0; i < scenes.length; i++) {
      const scene = scenes[i];
      const sceneId = scene.id || `scene_${String(i + 1).padStart(2, '0')}`;
      const sceneOutputPath = path.join(outputDir, `${sceneId}.mp4`);

      const refs = [...(scene.references || [])];

      // Auto-chaining: condition on previous scene's end frame if requested
      if (scene.chain_from_previous && previousSceneResult?.frameEndPath) {
        console.log(`[FlowDagEngine] Chaining scene ${sceneId} from previous frame: ${previousSceneResult.frameEndPath}`);
        refs.unshift(previousSceneResult.frameEndPath);
      }

      console.log(`[FlowDagEngine] Starting scene ${i + 1}/${scenes.length}: ${sceneId}`);
      const res = await this.generateVideo({
        prompt: scene.prompt,
        references: refs,
        mode: scene.mode ?? batch.mode ?? 'video',
        submode: scene.submode ?? batch.submode ?? 'ingredients',
        model: scene.model ?? batch.model ?? null,
        count: scene.count ?? batch.count ?? 1,
        maxCredits: scene.maxCredits ?? batch.maxCredits ?? null,
        ratio: scene.ratio || ratio || null,
        duration: scene.duration || null,
        resolution: scene.resolution || null,
        reverse: Boolean(scene.reverse),
        outputPath: sceneOutputPath,
        projectUrl,
      });

      results.push({ sceneId, ...res });
      previousSceneResult = res;
    }

    return {
      success: true,
      totalScenes: scenes.length,
      results,
    };
  }
}
