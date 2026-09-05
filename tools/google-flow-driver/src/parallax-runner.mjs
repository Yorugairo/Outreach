import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { ComfyClient } from './comfy-client.mjs';

const CROP_ZOOM = 1.10;

/** Pixel size of a PNG or JPEG from its header - no image library in this package. */
export function imageSize(file) {
  const b = fs.readFileSync(file);
  if (b.length > 24 && b.readUInt32BE(0) === 0x89504e47) return { width: b.readUInt32BE(16), height: b.readUInt32BE(20) };
  if (b.length > 4 && b[0] === 0xff && b[1] === 0xd8) {
    let i = 2;
    while (i + 9 < b.length) {
      if (b[i] !== 0xff) { i++; continue; }
      const marker = b[i + 1], len = b.readUInt16BE(i + 2);
      if (marker >= 0xc0 && marker <= 0xcf && ![0xc4, 0xc8, 0xcc].includes(marker)) return { height: b.readUInt16BE(i + 5), width: b.readUInt16BE(i + 7) };
      i += 2 + len;
    }
  }
  throw new Error(`imageSize: not a PNG or JPEG: ${file}`);
}

export async function generateParallaxVideo({
  inputImagePath,
  motion = 'dolly', // 'dolly', 'zoom', 'circle', 'horizontal', 'vertical', 'orbital'
  frames = 30,
  fps = 30,
  strength = 1.0,      // inert without a `feature` input (45 s45.4) - kept only because the node schema requires it
  intensity = 0.11,    // THE displacement. 45 s45.3: 0.08-0.15, ceiling 0.18; the gate holds 0.10-0.12
  reverse = false,
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

  const size = imageSize(inputImagePath);

  // 2. Select motion node type and build exact inputs per ComfyUI node schema
  let motionNodeType = 'DepthflowMotionPresetDolly';
  let motionInputs = {
    "strength": strength,
    "intensity": intensity,
    "feature_threshold": 0.0,
    "feature_param": "intensity",
    "feature_mode": "relative",
    "reverse": reverse,
    "smooth": true,
    "loop": true,
    "depth": 0.5
  };

  if (motion === 'zoom') {
    motionNodeType = 'DepthflowMotionPresetZoom';
    motionInputs = {
      "strength": strength,
      "intensity": intensity,
      "feature_threshold": 0.0,
      "feature_param": "intensity",
      "feature_mode": "relative",
      "reverse": reverse,
      "smooth": true,
      "loop": false,
      "phase": 0.0
    };
  } else if (motion === 'horizontal') {
    motionNodeType = 'DepthflowMotionPresetHorizontal';
    motionInputs = {
      "strength": strength,
      "intensity": intensity,
      "feature_threshold": 0.0,
      "feature_param": "intensity",
      "feature_mode": "relative",
      "reverse": false,
      "smooth": true,
      "loop": true,
      "phase": 0.0,
      "steady_value": 0.40
    };
  } else if (motion === 'vertical') {
    motionNodeType = 'DepthflowMotionPresetVertical';
    motionInputs = {
      "strength": strength,
      "intensity": intensity,
      "feature_threshold": 0.0,
      "feature_param": "intensity",
      "feature_mode": "relative",
      "reverse": false,
      "smooth": true,
      "loop": true,
      "phase": 0.0,
      "steady_value": 0.40
    };
  } else if (motion === 'circle') {
    motionNodeType = 'DepthflowMotionPresetCircle';
    motionInputs = {
      "strength": strength,
      "intensity": intensity,
      "feature_threshold": 0.0,
      "feature_param": "intensity",
      "feature_mode": "relative",
      "reverse": false,
      "smooth": true,
      "phase_x": 0.0,
      "phase_y": 0.0,
      "phase_z": 0.0,
      "amplitude_x": 1.0,
      "amplitude_y": 1.0,
      "amplitude_z": 0.0,
      "static_value": 0.3
    };
  } else if (motion === 'orbital') {
    motionNodeType = 'DepthflowMotionPresetOrbital';
    motionInputs = {
      "strength": strength,
      "intensity": intensity,
      "feature_threshold": 0.0,
      "feature_param": "intensity",
      "feature_mode": "relative",
      "reverse": false,
      "depth": 0.5
    };
  }

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
        "model": "depth_anything_v2_vitl_fp16.safetensors",   // ViT-Large (45 s45.3); precision per X6
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
      "inputs": motionInputs,
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
        "quality": 85,
        "ssaa": 2.0,
        "invert": 0,
        "tiling_mode": "none",   // mirror is the kaleidoscope ceiling (45 s45.3); the crop below hides the bare edges
        "edge_fix": 5
      },
      "class_type": "Depthflow"
    },
    // tiling none leaves the displaced border bare; scale the frames 1.10x and crop back to the
    // plate's size so the reveal never reaches the frame (the "1.10x crop" of 45 s45.3)
    "8": {
      "inputs": { "image": ["5", 0], "upscale_method": "lanczos", "scale_by": CROP_ZOOM },
      "class_type": "ImageScaleBy"
    },
    "9": {
      "inputs": { "image": ["8", 0], "width": size.width, "height": size.height,
                  "x": Math.round(size.width * (CROP_ZOOM - 1) / 2), "y": Math.round(size.height * (CROP_ZOOM - 1) / 2) },
      "class_type": "ImageCrop"
    },
    "6": {
      "inputs": {
        "images": ["9", 0],
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
