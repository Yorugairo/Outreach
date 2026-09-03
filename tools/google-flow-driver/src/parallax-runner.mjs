import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { ComfyClient } from './comfy-client.mjs';

export async function generateParallaxVideo({
  inputImagePath,
  motion = 'dolly', // 'dolly', 'zoom', 'circle', 'horizontal', 'vertical', 'orbital'
  frames = 30,
  fps = 30,
  strength = 1.0,
  outputVideoPath,
  serverUrl = 'http://127.0.0.1:8188'
}) {
  const client = new ComfyClient(serverUrl);
  const healthy = await client.isHealthy();
  if (!healthy) {
    throw new Error(`ComfyUI is not reachable at ${serverUrl}`);
  }

  // 1. Copy image to ComfyUI input folder
  const comfyInputDir = 'C:\\Users\\Snipe\\AppData\\Local\\Comfy-Desktop\\ComfyUI-Installs\\ComfyUI\\ComfyUI\\input';
  fs.mkdirSync(comfyInputDir, { recursive: true });

  const ext = path.extname(inputImagePath);
  const baseName = `input_${Date.now()}_${crypto.randomBytes(4).toString('hex')}${ext}`;
  const destInputPath = path.join(comfyInputDir, baseName);
  fs.copyFileSync(inputImagePath, destInputPath);

  // 2. Select motion node type
  let motionNodeType = 'DepthflowMotionPresetDolly';
  if (motion === 'zoom') motionNodeType = 'DepthflowMotionPresetZoom';
  else if (motion === 'circle') motionNodeType = 'DepthflowMotionPresetCircle';
  else if (motion === 'horizontal') motionNodeType = 'DepthflowMotionPresetHorizontal';
  else if (motion === 'vertical') motionNodeType = 'DepthflowMotionPresetVertical';
  else if (motion === 'orbital') motionNodeType = 'DepthflowMotionPresetOrbital';

  // 3. Construct ComfyUI prompt graph
  const prefix = `Parallax_${motion}_${Date.now()}`;
  const promptGraph = {
    "1": {
      "inputs": {
        "image": baseName,
        "upload": "image"
      },
      "class_type": "LoadImage"
    },
    "2": {
      "inputs": {
        "model": "depth_anything_v2_vits_fp16.safetensors",
        "precision": "fp16"
      },
      "class_type": "DownloadAndLoadDepthAnythingV2Model"
    },
    "3": {
      "inputs": {
        "da_model": ["2", 0],
        "images": ["1", 0]
      },
      "class_type": "DepthAnything_V2"
    },
    "4": {
      "inputs": {
        "strength": strength,
        "intensity": 1.0,
        "feature_threshold": 0.0,
        "feature_param": "intensity",
        "feature_mode": "relative",
        "reverse": false,
        "smooth": true,
        "loop": true,
        "depth": 0.5
      },
      "class_type": motionNodeType
    },
    "5": {
      "inputs": {
        "image": ["1", 0],
        "depth_map": ["3", 0],
        "motion": ["4", 0],
        "animation_speed": 1.0,
        "input_fps": fps,
        "output_fps": fps,
        "num_frames": frames,
        "quality": 75,
        "ssaa": 1.0,
        "invert": 0,
        "tiling_mode": "mirror",
        "edge_fix": 5
      },
      "class_type": "Depthflow"
    },
    "6": {
      "inputs": {
        "images": ["5", 0],
        "fps": fps,
        "bit_depth": "auto",
        "color_space": "sRGB"
      },
      "class_type": "CreateVideo"
    },
    "7": {
      "inputs": {
        "video": ["6", 0],
        "filename_prefix": prefix,
        "format": "mp4"
      },
      "class_type": "SaveVideo"
    }
  };

  console.log(`[Parallax] Submitting 2.5D parallax job (${motion}, ${frames} frames) to ComfyUI...`);
  const { promptId, clientId } = await client.queuePrompt(promptGraph);
  console.log(`[Parallax] Job queued with prompt ID: ${promptId}`);

  console.log('[Parallax] Waiting for GPU processing to complete...');
  const result = await client.waitForCompletion(promptId, clientId, 180000);

  // 4. Locate video in outputs
  const outputs = result.outputs || {};
  let videoMeta = null;

  for (const nodeId of Object.keys(outputs)) {
    const nodeOutput = outputs[nodeId];
    if (nodeOutput.videos && nodeOutput.videos.length > 0) {
      videoMeta = nodeOutput.videos[0];
      break;
    }
    if (nodeOutput.gifs && nodeOutput.gifs.length > 0) {
      videoMeta = nodeOutput.gifs[0];
      break;
    }
    if (nodeOutput.images && nodeOutput.images.length > 0 && nodeOutput.images[0].filename.endsWith('.mp4')) {
      videoMeta = nodeOutput.images[0];
      break;
    }
  }

  if (!videoMeta) {
    // Check output directory directly for matching prefix
    const comfyOutputDir = 'C:\\Users\\Snipe\\AppData\\Local\\Comfy-Desktop\\ComfyUI-Installs\\ComfyUI\\ComfyUI\\output';
    const files = fs.readdirSync(comfyOutputDir).filter(f => f.startsWith(prefix) && (f.endsWith('.mp4') || f.endsWith('.webm')));
    if (files.length > 0) {
      videoMeta = { filename: files[0], subfolder: '', type: 'output' };
    }
  }

  if (!videoMeta) {
    throw new Error(`Execution completed, but no video file output found for prefix ${prefix}`);
  }

  const finalOutput = outputVideoPath || path.join(process.cwd(), 'output', `${prefix}.mp4`);
  await client.downloadOutput(videoMeta.filename, videoMeta.subfolder || '', videoMeta.type || 'output', finalOutput);

  console.log(`[Parallax] Parallax video successfully saved to: ${finalOutput}`);
  return {
    promptId,
    videoPath: finalOutput,
    filename: videoMeta.filename,
    motion,
    frames,
    fps
  };
}
