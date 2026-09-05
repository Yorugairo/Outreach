"""Mask-pinned AMBIENT life on an approved still - Wan 2.1 VACE 1.3B on the local ComfyUI (doc 49 s49.2 / s49.3,
operator Option C, 2026-09-05): the still is the control video for every frame, a LIFE mask (1 = generate) covers
only the air the effect lives in, everything else is 0 = frozen bit-for-bit to the still. SAM 2 makes the object
mask (comfy_sam2_mask.py); this script takes the still, the life region, and a prompt, and returns an mp4.

    python comfy_vace_ambient.py --still <png> --life x0,y0,x1,y1 --prompt "..." --out <mp4> [--frames 81] [--cfg 4.0]

Dials from doc 49 (never fitted here): frames 4k+1, steps 25, CFG <= 4.5, shift 3.0 at 480p, scaled fp8 UMT5,
unquantized VAE. The job JSON is written beside the output and checked by gate_comfy_config.py before submission.
"""
from __future__ import annotations

import argparse
import io
import json
import subprocess
import sys
import time
import urllib.request
import uuid
from pathlib import Path

from PIL import Image, ImageFilter

HERE = Path(__file__).resolve().parent
BASE = "http://127.0.0.1:8188"
MODEL = "wan2.1_vace_1.3B_fp16.safetensors"
TEXT_ENCODER = "umt5_xxl_fp8_e4m3fn_scaled.safetensors"
VAE = "wan_2.1_vae.safetensors"
GEN_W, GEN_H = 480, 864          # VACE 1.3B's 480p class, portrait, multiples of 16 (the 768x1376 still is 0.558)
FPS = 16
NEGATIVE = ("bright colors, overexposed, static, blurred details, subtitles, style, works, paintings, images, "
            "static, overall gray, worst quality, low quality, JPEG compression residue, ugly, incomplete, "
            "extra fingers, poorly drawn hands, poorly drawn faces, deformed, disfigured, malformed limbs, "
            "fused fingers, still picture, messy background, three legs, many people in the background, walking backwards")


def upload(name: str, png: bytes) -> str:
    boundary = "----vace" + uuid.uuid4().hex
    body = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"image\"; filename=\"{name}\"\r\n"
            f"Content-Type: image/png\r\n\r\n").encode() + png + \
           f"\r\n--{boundary}\r\nContent-Disposition: form-data; name=\"overwrite\"\r\n\r\ntrue\r\n--{boundary}--\r\n".encode()
    req = urllib.request.Request(BASE + "/upload/image", data=body, headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    return json.loads(urllib.request.urlopen(req).read())["name"]


def png_bytes(im: Image.Image) -> bytes:
    b = io.BytesIO(); im.save(b, "PNG"); return b.getvalue()


def life_mask(size: tuple[int, int], life: tuple[float, float, float, float], blur_px: int = 4) -> Image.Image:
    """1 (white) where the effect may generate, 0 elsewhere; edges snapped to the 32 px latent block and blurred (49 s49.3)."""
    w, h = size
    m = Image.new("L", size, 0)
    x0, y0, x1, y1 = (round(life[0] * w / 32) * 32, round(life[1] * h / 32) * 32, round(life[2] * w / 32) * 32, round(life[3] * h / 32) * 32)
    m.paste(255, (max(0, x0), max(0, y0), min(w, x1), min(h, y1)))
    return m.filter(ImageFilter.GaussianBlur(blur_px))


def workflow(still: str, mask: str, prompt: str, frames: int, cfg: float, steps: int, seed: int, shift: float) -> dict:
    return {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": MODEL, "weight_dtype": "default"}},
        "2": {"class_type": "ModelSamplingSD3", "inputs": {"model": ["1", 0], "shift": shift}},
        "3": {"class_type": "CLIPLoader", "inputs": {"clip_name": TEXT_ENCODER, "type": "wan", "device": "default"}},
        "4": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["3", 0], "text": prompt}},
        "5": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["3", 0], "text": NEGATIVE}},
        "6": {"class_type": "VAELoader", "inputs": {"vae_name": VAE}},
        "7": {"class_type": "LoadImage", "inputs": {"image": still}},
        "8": {"class_type": "RepeatImageBatch", "inputs": {"image": ["7", 0], "amount": frames}},
        "9": {"class_type": "LoadImage", "inputs": {"image": mask}},
        "10": {"class_type": "RepeatImageBatch", "inputs": {"image": ["9", 0], "amount": frames}},
        "11": {"class_type": "ImageToMask", "inputs": {"image": ["10", 0], "channel": "red"}},
        "12": {"class_type": "WanVaceToVideo", "inputs": {"positive": ["4", 0], "negative": ["5", 0], "vae": ["6", 0], "width": GEN_W, "height": GEN_H,
                                                          "length": frames, "batch_size": 1, "strength": 1.0,
                                                          "control_video": ["8", 0], "control_masks": ["11", 0], "reference_image": ["7", 0]}},
        "13": {"class_type": "KSampler", "inputs": {"model": ["2", 0], "seed": seed, "steps": steps, "cfg": cfg, "sampler_name": "uni_pc",
                                                    "scheduler": "simple", "denoise": 1.0, "positive": ["12", 0], "negative": ["12", 1], "latent_image": ["12", 2]}},
        "14": {"class_type": "TrimVideoLatent", "inputs": {"samples": ["13", 0], "trim_amount": ["12", 3]}},
        "15": {"class_type": "VAEDecode", "inputs": {"samples": ["14", 0], "vae": ["6", 0]}},
        "16": {"class_type": "CreateVideo", "inputs": {"images": ["15", 0], "fps": FPS}},
        "17": {"class_type": "SaveVideo", "inputs": {"video": ["16", 0], "filename_prefix": "vace-ambient", "format": "mp4", "codec": "h264"}},
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--still", type=Path, required=True)
    ap.add_argument("--life", required=True, help="x0,y0,x1,y1 as fractions of the frame: where the effect may generate")
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--frames", type=int, default=81)
    ap.add_argument("--cfg", type=float, default=4.0)
    ap.add_argument("--steps", type=int, default=25)
    ap.add_argument("--shift", type=float, default=3.0)
    ap.add_argument("--seed", type=int, default=4242)
    ap.add_argument("--timeout", type=int, default=1800)
    ap.add_argument("--no-inpaint", dest="inpaint", action="store_false", help="leave the life region's pixels in the control video (the model then tends to keep them)")
    a = ap.parse_args()
    life = tuple(float(v) for v in a.life.split(","))
    job = {"model": MODEL, "num_frames": a.frames, "cfg": a.cfg, "steps": a.steps, "shift": a.shift, "text_encoder": TEXT_ENCODER, "vae": VAE,
           "width": GEN_W, "height": GEN_H, "fps": FPS, "life": life, "prompt": a.prompt, "still": str(a.still), "seed": a.seed}
    job_path = a.out.with_suffix(".job.json"); a.out.parent.mkdir(parents=True, exist_ok=True)
    job_path.write_text(json.dumps(job, indent=1), encoding="utf-8")
    gate = subprocess.run([sys.executable, str(HERE / "gate_comfy_config.py"), str(job_path), "--plate-kind", "world"], capture_output=True, text=True)
    print(gate.stdout.strip().splitlines()[-1] if gate.stdout.strip() else gate.stderr)
    if gate.returncode != 0:
        print("gate_comfy_config refused the job - nothing submitted"); return 1
    still = Image.open(a.still).convert("RGB").resize((GEN_W, GEN_H), Image.LANCZOS)
    mask = life_mask((GEN_W, GEN_H), life)
    # the CONTROL video is the still with the life region greyed out (VACE's inpaint convention: reactive pixels
    # at 0.5 must be re-imagined - left as the still, the model keeps them and generates nothing; run 1 proved it);
    # the REFERENCE image stays the whole still, so what is re-imagined matches it
    control = Image.composite(Image.new("RGB", still.size, (128, 128, 128)), still, mask.point(lambda v: 255 if v > 127 else 0)) if a.inpaint else still
    still_name = upload("vace-control.png", png_bytes(control)); mask_name = upload("vace-life-mask.png", png_bytes(mask.convert("RGB")))
    ref_name = upload("vace-reference.png", png_bytes(still))
    mask.save(a.out.with_suffix(".life-mask.png"))
    wf = workflow(still_name, mask_name, a.prompt, a.frames, a.cfg, a.steps, a.seed, a.shift)
    wf["18"] = {"class_type": "LoadImage", "inputs": {"image": ref_name}}
    wf["12"]["inputs"]["reference_image"] = ["18", 0]
    r = json.loads(urllib.request.urlopen(urllib.request.Request(BASE + "/prompt", data=json.dumps({"prompt": wf, "client_id": uuid.uuid4().hex}).encode(),
                                                                 headers={"Content-Type": "application/json"})).read())
    if r.get("node_errors"):
        print(json.dumps(r["node_errors"], indent=1)[:2000]); return 1
    pid = r["prompt_id"]; print("queued", pid); t0 = time.time()
    while time.time() - t0 < a.timeout:
        time.sleep(5)
        h = json.loads(urllib.request.urlopen(BASE + "/history/" + pid).read())
        if pid not in h:
            continue
        st = h[pid].get("status", {})
        if st.get("status_str") == "error":
            print(json.dumps(st.get("messages"))[:2500]); return 1
        outs = h[pid].get("outputs", {}).get("17", {})
        files = outs.get("images") or outs.get("video") or outs.get("videos") or []
        for f in files:
            data = urllib.request.urlopen(BASE + f"/view?filename={f['filename']}&subfolder={f.get('subfolder', '')}&type={f['type']}").read()
            a.out.write_bytes(data); print(f"wrote {a.out} ({len(data)} bytes) in {time.time() - t0:.0f}s"); return 0
        print("finished without a file:", json.dumps(outs)[:400]); return 1
    print("timeout"); return 1


if __name__ == "__main__":
    raise SystemExit(main())
