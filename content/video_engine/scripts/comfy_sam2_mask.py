"""An OBJECT mask from an approved still with SAM 2 on the local ComfyUI (operator Option C, 2026-09-05): the
cup, the saucer, the table - whatever must not move - as a PNG mask for the mask-pinned ambient lane
(comfy_vace_ambient.py) and for measuring where a still-life species may live.

    python comfy_sam2_mask.py --still <png> --positive x,y[;x,y...] [--negative x,y[;x,y...]] --out <png> [--grow 6]

Points are pixels on the still. The mask is white on the object, black elsewhere, grown by --grow px.
"""
from __future__ import annotations

import argparse
import json
import time
import urllib.request
import uuid
from pathlib import Path

BASE = "http://127.0.0.1:8188"
SAM_MODEL = "sam2.1_hiera_small.safetensors"


def upload(name: str, png: bytes) -> str:
    boundary = "----sam" + uuid.uuid4().hex
    body = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"image\"; filename=\"{name}\"\r\n"
            f"Content-Type: image/png\r\n\r\n").encode() + png + \
           f"\r\n--{boundary}\r\nContent-Disposition: form-data; name=\"overwrite\"\r\n\r\ntrue\r\n--{boundary}--\r\n".encode()
    req = urllib.request.Request(BASE + "/upload/image", data=body, headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    return json.loads(urllib.request.urlopen(req).read())["name"]


def points(spec: str | None) -> str:
    """'x,y;x,y' -> the SAM 2 node's coordinate string: a JSON list of {"x", "y"}."""
    if not spec:
        return "[]"
    return json.dumps([{"x": int(p.split(",")[0]), "y": int(p.split(",")[1])} for p in spec.split(";") if p.strip()])


def workflow(still: str, pos: str, neg: str, grow: int) -> dict:
    return {
        "1": {"class_type": "LoadImage", "inputs": {"image": still}},
        "2": {"class_type": "DownloadAndLoadSAM2Model", "inputs": {"model": SAM_MODEL, "segmentor": "single_image", "device": "cuda", "precision": "fp16"}},
        "3": {"class_type": "PrimitiveString", "inputs": {"value": pos}},
        "4": {"class_type": "PrimitiveString", "inputs": {"value": neg}},
        "5": {"class_type": "Sam2Segmentation", "inputs": {"sam2_model": ["2", 0], "image": ["1", 0], "keep_model_loaded": False,
                                                          "coordinates_positive": ["3", 0], "coordinates_negative": ["4", 0], "individual_objects": False}},
        "6": {"class_type": "GrowMask", "inputs": {"mask": ["5", 0], "expand": grow, "tapered_corners": True}},
        "7": {"class_type": "MaskToImage", "inputs": {"mask": ["6", 0]}},
        "8": {"class_type": "SaveImage", "inputs": {"images": ["7", 0], "filename_prefix": "sam2-mask"}},
    }


def run(still: Path, positive: str, negative: str | None, out: Path, grow: int = 6, timeout: int = 600) -> Path:
    name = upload(f"sam2-{still.stem}.png", still.read_bytes())
    wf = workflow(name, points(positive), points(negative), grow)
    r = json.loads(urllib.request.urlopen(urllib.request.Request(BASE + "/prompt", data=json.dumps({"prompt": wf, "client_id": uuid.uuid4().hex}).encode(),
                                                                 headers={"Content-Type": "application/json"})).read())
    if r.get("node_errors"):
        raise SystemExit(json.dumps(r["node_errors"], indent=1)[:1500])
    pid = r["prompt_id"]; t0 = time.time()
    while time.time() - t0 < timeout:
        time.sleep(2)
        h = json.loads(urllib.request.urlopen(BASE + "/history/" + pid).read())
        if pid not in h:
            continue
        st = h[pid].get("status", {})
        if st.get("status_str") == "error":
            raise SystemExit(json.dumps(st.get("messages"))[:1500])
        for im in h[pid].get("outputs", {}).get("8", {}).get("images", []):
            data = urllib.request.urlopen(BASE + f"/view?filename={im['filename']}&subfolder={im.get('subfolder', '')}&type={im['type']}").read()
            out.parent.mkdir(parents=True, exist_ok=True); out.write_bytes(data)
            return out
        raise SystemExit("finished without a mask")
    raise SystemExit("timeout")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--still", type=Path, required=True)
    ap.add_argument("--positive", required=True, help="points ON the object: x,y;x,y")
    ap.add_argument("--negative", default=None, help="points OFF the object: x,y;x,y")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--grow", type=int, default=6)
    a = ap.parse_args()
    p = run(a.still, a.positive, a.negative, a.out, a.grow)
    print(f"wrote {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
