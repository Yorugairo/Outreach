---
name: comfy-local-models-layout
description: "Comfy Desktop runs ComfyUI-Installs/ComfyUI/ComfyUI (models folders EMPTY); the operator's weights live in Comfy-Desktop/ComfyUI-Shared/models and must be HARDLINKED into the install; what is on disk (Wan 2.1 T2V 1.3B, VACE 1.3B, LTX 2B 0.9.8 distilled, both text encoders, Wan VAE, SAM 2) and what the ambient lane proved"
metadata: 
  node_type: memory
  type: project
  originSessionId: 45114c3b-258a-4ca8-9aaf-b674a804cc7e
  modified: 2026-09-05T11:17:43.318Z
---

**Layout (2026-09-05).** The running server (`127.0.0.1:8188`) is `C:\Users\Snipe\AppData\Local\Comfy-Desktop\ComfyUI-Installs\ComfyUI\ComfyUI\main.py`. Its own `models/*` folders hold only placeholders, so every loader listed `[]`. The operator's weights are in `C:\Users\Snipe\AppData\Local\Comfy-Desktop\ComfyUI-Shared\models\...` and are NOT linked (no `extra_model_paths.yaml`). Fix that worked without a restart: `New-Item -ItemType HardLink` from the install's folder to the shared file (same volume); the loaders rescan on request.

**On disk after the day:** `wan2.1_t2v_1.3B_fp16` (text-to-video only, no image input), `wan2.1_vace_1.3B_fp16` (downloaded: the masked image-to-video), `ltxv-2b-0.9.8-distilled` (downloaded; the 0.9.6 name on the hub is `ltxv-2b-0.9.6-distilled-04-25`, a wrong name returns a 15-byte "Entry not found" file), `umt5_xxl_fp8_e4m3fn_scaled`, `t5xxl_fp8_e4m3fn_scaled`, `wan_2.1_vae`; SAM 2 fetches on demand (`DownloadAndLoadSAM2Model`). No 14B anything: the 4070 has 12 GB.

**Why it matters / how to apply:** the mask-pinned ambient lane (`comfy_sam2_mask.py`, `comfy_vace_ambient.py`, `comfy_ltx_ambient.py`) is LIVE and the PIN is proven (four runs, the cup within compression noise). Neither 1-2B model draws thin steam in a small dark region - VACE rebuilds the room, LTX invents a desk. Use the lane for ambient life that fills its region; a thin bright element stays a drawn species. Speeds: VACE ~8 min / 81 portrait frames at 480p; LTX distilled 12-18 s / 121 frames. SAM 2 coordinates are a JSON list of `{"x","y"}`. See [flow-stills-first-image-to-video](flow-stills-first-image-to-video.md), [install-permission](install-permission.md).
