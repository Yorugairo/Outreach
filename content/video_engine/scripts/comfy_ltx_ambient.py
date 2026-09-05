"""Mask-pinned AMBIENT life on an approved still - LTX-Video 2B (distilled) on the local ComfyUI (doc 49 s49.3).
The pinning is ComfyUI's latent noise mask over a latent that IS the still on every frame: where the life mask
is 0 the sampler keeps the encoded still bit-for-bit, where it is 1 it denoises - the timestep clamp doc 49
quotes, as the engine implements it. The still is also the frame-0 guide (LTXVAddGuide) so what is generated
matches it. Seconds per run, not minutes (doc 49: ~10 s for 5 s on a 4090).

    python comfy_ltx_ambient.py --still <png> --life x0,y0,x1,y1 --prompt "..." --out <mp4> [--frames 121] [--steps 8]

Dials from doc 49: frames 8n+1 (121 @ 24 fps = 5.04 s), distilled = 8 steps / CFG 1.0 / STG off, CRF 28-32 on
the guide image (LTXVPreprocess). The job JSON is written beside the output and checked by gate_comfy_config.py.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
import urllib.request
import uuid
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comfy_vace_ambient import BASE, life_mask, png_bytes, upload  # noqa: E402

HERE = Path(__file__).resolve().parent
MODEL = "ltxv-2b-0.9.8-distilled.safetensors"
TEXT_ENCODER = "t5xxl_fp8_e4m3fn_scaled.safetensors"
GEN_W, GEN_H = 480, 864      # multiples of 32 (LTX's latent block)
FPS = 24
NEGATIVE = "low quality, worst quality, deformed, distorted, disfigured, motion smear, motion artifacts, fused fingers, bad anatomy, weird hand, ugly, blurry, jittery, flicker"


def workflow(control: str, ref: str, mask: str, prompt: str, frames: int, steps: int, cfg: float, seed: int, crf: int, denoise: float = 1.0) -> dict:
    wf = {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": MODEL}},
        "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": TEXT_ENCODER, "type": "ltxv", "device": "default"}},
        "3": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 0], "text": prompt}},
        "4": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 0], "text": NEGATIVE}},
        "5": {"class_type": "LTXVConditioning", "inputs": {"positive": ["3", 0], "negative": ["4", 0], "frame_rate": FPS}},
        "6": {"class_type": "LoadImage", "inputs": {"image": control}},
        "7": {"class_type": "RepeatImageBatch", "inputs": {"image": ["6", 0], "amount": frames}},
        "8": {"class_type": "VAEEncode", "inputs": {"pixels": ["7", 0], "vae": ["1", 2]}},               # the still on every frame
        "9": {"class_type": "LoadImage", "inputs": {"image": ref}},
        "10": {"class_type": "LTXVPreprocess", "inputs": {"image": ["9", 0], "img_compression": crf}},   # CRF 28-32 frees motion (49 s49.3)
        "11": {"class_type": "LTXVAddGuide", "inputs": {"positive": ["5", 0], "negative": ["5", 1], "vae": ["1", 2], "latent": ["8", 0], "image": ["10", 0], "frame_idx": 0, "strength": 1.0}},
        "12": {"class_type": "LoadImage", "inputs": {"image": mask}},
        "13": {"class_type": "ImageToMask", "inputs": {"image": ["12", 0], "channel": "red"}},
        "14": {"class_type": "SetLatentNoiseMask", "inputs": {"samples": ["11", 2], "mask": ["13", 0]}},   # 1 = denoise, 0 = the still, bit-for-bit
        "15": {"class_type": "ModelSamplingLTXV", "inputs": {"model": ["1", 0], "max_shift": 2.05, "base_shift": 0.95, "latent": ["14", 0]}},
        "16": {"class_type": "LTXVScheduler", "inputs": {"steps": steps, "max_shift": 2.05, "base_shift": 0.95, "stretch": True, "terminal": 0.1, "latent": ["14", 0]}},
        "17": {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "euler"}},
        "18": {"class_type": "SamplerCustom", "inputs": {"model": ["15", 0], "add_noise": True, "noise_seed": seed, "cfg": cfg, "positive": ["11", 0], "negative": ["11", 1],
                                                         "sampler": ["17", 0], "sigmas": ["16", 0], "latent_image": ["14", 0]}},
        "19": {"class_type": "LTXVCropGuides", "inputs": {"positive": ["11", 0], "negative": ["11", 1], "latent": ["18", 0]}},
        "20": {"class_type": "VAEDecode", "inputs": {"samples": ["19", 2], "vae": ["1", 2]}},
        "21": {"class_type": "CreateVideo", "inputs": {"images": ["20", 0], "fps": FPS}},
        "22": {"class_type": "SaveVideo", "inputs": {"video": ["21", 0], "filename_prefix": "ltx-ambient", "format": "mp4", "codec": "h264"}},
    }
    if denoise < 1.0:   # partial denoise: the life region starts from the still's own latent and the model ADDS to it (SplitSigmasDenoise keeps the low-sigma tail)
        wf["23"] = {"class_type": "SplitSigmasDenoise", "inputs": {"sigmas": ["16", 0], "denoise": denoise}}
        wf["18"]["inputs"]["sigmas"] = ["23", 1]
    return wf


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--still", type=Path, required=True)
    ap.add_argument("--life", required=True)
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--frames", type=int, default=121)
    ap.add_argument("--steps", type=int, default=8)
    ap.add_argument("--cfg", type=float, default=1.0)
    ap.add_argument("--crf", type=int, default=30)
    ap.add_argument("--seed", type=int, default=4242)
    ap.add_argument("--no-inpaint", dest="inpaint", action="store_false")
    ap.add_argument("--denoise", type=float, default=1.0, help="< 1: the life region keeps the still's latent and is only partly re-noised")
    ap.add_argument("--timeout", type=int, default=900)
    a = ap.parse_args()
    life = tuple(float(v) for v in a.life.split(","))
    job = {"model": MODEL, "num_frames": a.frames, "cfg": a.cfg, "steps": a.steps, "text_encoder": TEXT_ENCODER, "width": GEN_W, "height": GEN_H,
           "fps": FPS, "life": life, "prompt": a.prompt, "still": str(a.still), "seed": a.seed, "crf": a.crf, "denoise": a.denoise, "inpaint": a.inpaint, "stg": "off (distilled)"}
    job_path = a.out.with_suffix(".job.json"); a.out.parent.mkdir(parents=True, exist_ok=True)
    job_path.write_text(json.dumps(job, indent=1), encoding="utf-8")
    gate = subprocess.run([sys.executable, str(HERE / "gate_comfy_config.py"), str(job_path), "--plate-kind", "world"], capture_output=True, text=True)
    print(gate.stdout.strip().splitlines()[-1] if gate.stdout.strip() else gate.stderr)
    if gate.returncode != 0:
        print("gate_comfy_config refused the job - nothing submitted"); return 1
    still = Image.open(a.still).convert("RGB").resize((GEN_W, GEN_H), Image.LANCZOS)
    mask = life_mask((GEN_W, GEN_H), life)
    control = Image.composite(Image.new("RGB", still.size, (128, 128, 128)), still, mask.point(lambda v: 255 if v > 127 else 0)) if a.inpaint else still
    names = (upload("ltx-control.png", png_bytes(control)), upload("ltx-reference.png", png_bytes(still)), upload("ltx-life-mask.png", png_bytes(mask.convert("RGB"))))
    mask.save(a.out.with_suffix(".life-mask.png"))
    wf = workflow(*names, a.prompt, a.frames, a.steps, a.cfg, a.seed, a.crf, a.denoise)
    r = json.loads(urllib.request.urlopen(urllib.request.Request(BASE + "/prompt", data=json.dumps({"prompt": wf, "client_id": uuid.uuid4().hex}).encode(),
                                                                 headers={"Content-Type": "application/json"})).read())
    if r.get("node_errors"):
        print(json.dumps(r["node_errors"], indent=1)[:2000]); return 1
    pid = r["prompt_id"]; print("queued", pid); t0 = time.time()
    while time.time() - t0 < a.timeout:
        time.sleep(3)
        h = json.loads(urllib.request.urlopen(BASE + "/history/" + pid).read())
        if pid not in h:
            continue
        st = h[pid].get("status", {})
        if st.get("status_str") == "error":
            print(json.dumps(st.get("messages"))[:2500]); return 1
        outs = h[pid].get("outputs", {}).get("22", {})
        for f in outs.get("images") or outs.get("video") or outs.get("videos") or []:
            data = urllib.request.urlopen(BASE + f"/view?filename={f['filename']}&subfolder={f.get('subfolder', '')}&type={f['type']}").read()
            a.out.write_bytes(data); print(f"wrote {a.out} ({len(data)} bytes) in {time.time() - t0:.0f}s"); return 0
        print("finished without a file:", json.dumps(outs)[:400]); return 1
    print("timeout"); return 1


if __name__ == "__main__":
    raise SystemExit(main())
