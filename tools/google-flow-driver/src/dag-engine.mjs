import path from 'node:path';
import { FlowCdpDriver } from './cdp-driver.mjs';
import fs from 'node:fs';
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
    const isImage = mode === 'image';
    const rawExt = isImage ? '.png' : '.mp4';
    const rawPath = path.join(targetDir, `${baseName}-raw${rawExt}`);
    const finalOutputPath = isImage ? (outputPath.endsWith('.png') ? outputPath : `${outputPath}.png`) : (reverse ? path.join(targetDir, `${baseName}-reversed.mp4`) : outputPath);

    // 1. Connect and ensure Flow page
    await this.driver.getFlowPage(projectUrl);

    // 2. Set the generation state and READ IT BACK - never preserve whatever the project was left on.
    const settings = await this.driver.configureSettings({ mode, submode, model, ratio, duration, resolution, count, maxCredits });

    // 3. Resolve references (partition disk files vs named project characters)
    const fileUploads = [];
    const characterMentions = [];
    if (references && references.length > 0) {
      const availableCharacters = await this.driver.listProjectCharacters();
      for (const ref of references) {
        if (typeof ref === 'string' && fs.existsSync(ref)) {
          fileUploads.push(ref);
        } else if (typeof ref === 'string') {
          const cleanName = ref.replace(/^@/, '').trim();
          const matched = availableCharacters.find(c => c.toLowerCase() === cleanName.toLowerCase());
          if (matched) {
            characterMentions.push(matched);
          } else {
            throw new Error(`Character "${ref}" not found in active Flow project. Available characters: [${availableCharacters.join(', ')}]`);
          }
        }
      }
    }

    // 4. Inject the prompt with native character chips (this clears the composer first)
    await this.driver.setPrompt(prompt, { characters: characterMentions });

    // 5. Then attach file references - on the new Flow they land as chips in the composer,
    //    so they must come after the clear, never before it.
    if (fileUploads.length > 0) {
      await this.driver.uploadReferences(fileUploads);
    }

    // 6. Submit Generation
    await this.driver.triggerGeneration();

    // 7. Wait for Generation & Download
    await this.driver.waitForGenerationAndDownload(rawPath, 420000, mode, { excludeFiles: fileUploads });

    // 7. Post-Processing
    let activePath = rawPath;
    if (isImage) {
      if (rawPath !== finalOutputPath) {
        fs.copyFileSync(rawPath, finalOutputPath);
        activePath = finalOutputPath;
      }
      const metadataPath = path.join(targetDir, `${baseName}_meta.json`);
      const metadata = {
        prompt,
        references,
        settings: settings ?? null,
        requested_ratio: ratio || '9:16',
        mode: 'image',
        files: {
          image: { path: activePath, sha256: sha256File(activePath) },
          raw_image: { path: rawPath, sha256: sha256File(rawPath) },
        },
      };
      writeMetadata(metadataPath, metadata);
      return {
        success: true,
        mode: 'image',
        imagePath: activePath,
        rawPath,
        metadataPath,
        settings,
      };
    }

    if (reverse) {
      console.log(`[FlowDagEngine] Applying FFmpeg reversal to ${rawPath} -> ${finalOutputPath}...`);
      reverseVideo(rawPath, finalOutputPath);
      activePath = finalOutputPath;
    } else if (rawPath !== finalOutputPath) {
      activePath = finalOutputPath;
      fs.copyFileSync(rawPath, finalOutputPath);
    }

    // 8. Extract verification frames
    const frame0Path = path.join(targetDir, `${baseName}_frame_0.png`);
    const frameEndPath = path.join(targetDir, `${baseName}_frame_end.png`);
    let probe = null;
    let verificationError = null;
    try {
      extractVerificationFrames(activePath, frame0Path, frameEndPath);
      probe = probeVideo(activePath);
    } catch (err) {
      verificationError = String(err?.message || err).split(/\r?\n/)[0];
      console.warn(`[FlowDagEngine] verification step failed (video kept): ${verificationError}`);
    }

    // 10. Write Metadata Manifest
    const metadataPath = path.join(targetDir, `${baseName}_meta.json`);
    const metadata = {
      prompt,
      references,
      settings: settings ?? null,
      requested_ratio: ratio || 'preserved',
      detected_dimensions: probe ? `${probe.width}x${probe.height}` : null,
      aspect_ratio: probe?.aspect_ratio ?? null,
      duration_seconds: probe?.duration ?? null,
      verification_error: verificationError,
      reversed: reverse,
      files: {
        video: { path: activePath, sha256: sha256File(activePath) },
        raw_video: { path: rawPath, sha256: sha256File(rawPath) },
        frame_start: { path: frame0Path, sha256: sha256File(frame0Path) },
        frame_end: { path: frameEndPath, sha256: sha256File(frameEndPath) },
      },
    };
    writeMetadata(metadataPath, metadata);

    return {
      success: true,
      videoPath: activePath,
      rawVideoPath: rawPath,
      frame0Path,
      frameEndPath,
      metadataPath,
      probe,
    };
  }

  async generateImage({
    prompt,
    references = [],
    ratio = '9:16',
    outputPath,
    projectUrl = null,
  }) {
    return await this.generateVideo({
      prompt,
      references,
      mode: 'image',
      model: 'Nano Banana Pro',
      ratio,
      count: 1,
      outputPath,
      projectUrl,
    });
  }

  async getProjectDetails(projectUrl = null) {
    if (projectUrl) await this.driver.getFlowPage(projectUrl);
    return await this.driver.getProjectDetails();
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
