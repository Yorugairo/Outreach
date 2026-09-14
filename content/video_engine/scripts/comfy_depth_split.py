"""Route (b) of P58 T1: ONE flat plate -> FOUR depth layers, the disocclusion inpainted.

    python comfy_depth_split.py --plate <png> --out <dir> [--model vitl_fp16|vits_fp16] [--bands 4]
                               [--seed 0] [--sigma 2.0] [--edges a,b,c] [--depth <png>]

The graph is nodes 1-3 of `workflows/2_5d_parallax_inpaint.json` ONLY -
`LoadImage -> DownloadAndLoadDepthAnythingV2Model -> DepthAnything_V2 -> SaveImage`. DepthFlow and
`CreateVideo` (nodes 4-6) are NEVER called: E32 retired the GLSL mesh warp as a motion source; we want
the depth MAP and a split, never the warp (doc 45 s45.1 "Why our parallax melted").

THE SPLIT RECIPE (doc 45 s45.5, doc 24 :156-185)
- Depth Anything v2 emits RELATIVE inverse depth: bright = NEAR. Bands ascend toward the viewer, so
  band 0 is the farthest. The four bands take doc 24's roles back to front: `far` (opaque,
  building_or_environment, k=1.00), `mid` (furniture/actor ground, k=1.15), `subject` (k=1.15) and
  `near` (the one foreground occluder, k=1.40).
- Layer 0 (`far`) is COMPLETE and opaque: every pixel a nearer band owns is a hole, inpainted.
- A middle layer i keeps its own band plus an R_grow margin of inpainted content eaten out of the
  nearer bands, so a camera push cannot tear along its silhouette:
      alpha_i = dilate(band_i, R_grow) & (band_i | union(band_j, j > i))
  with `R_grow = ceil(2 * sigma) + 12 px` (doc 45 s45.5).
- The nearest layer is never inpainted - nothing occludes it.
- Every inpainted region is colour-matched mu/sigma to its own ring in L*a*b* (doc 45 s45.5).

THE INPAINTER: `INPAINT_LoadInpaintModel -> INPAINT_InpaintWithModel` with `big-lama.pt` when the
weight is on disk and the node accepts it; otherwise `cv2.inpaint(..., INPAINT_TELEA)`. The split json
always records which one ran under `"inpainter"` - the slice must SAY which.

Deterministic: the same plate and the same flags give byte-identical layer PNGs.
"""
from __future__ import annotations

import argparse
import io
import json
import math
import threading
import time
import urllib.request
import uuid
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

BASE = "http://127.0.0.1:8188"
MODELS = {
    "vits_fp16": "depth_anything_v2_vits_fp16.safetensors",
    "vitb_fp16": "depth_anything_v2_vitb_fp16.safetensors",
    "vitl_fp16": "depth_anything_v2_vitl_fp16.safetensors",
}
# doc 24 :166-171, back to front. `board` is an empty display surface a generated plate has no way to
# emit, so the split's four roles are far / mid / subject / near, with the board's 1.05 unused here.
ROLES = ("far", "mid", "subject", "near")
PARALLAX = {"far": 1.00, "mid": 1.15, "subject": 1.15, "near": 1.40}
LAMA_WEIGHT = "big-lama.pt"
SAM_MODEL = "sam2.1_hiera_small.safetensors"


# ---------------------------------------------------------------- pure geometry


def band_edges(depth: np.ndarray, n: int = 4) -> list[float]:
    """n+1 STRICTLY monotone edges over `depth` by quantile, so every pixel lands in exactly one band.

    Band i is `edges[i] <= d < edges[i+1]`, the last band closing on the max. Quantiles that collide
    (a flat plate, a posterised depth map) are nudged apart so the edges stay monotone and no band
    silently swallows another.
    """
    if n < 2:
        raise ValueError("a split needs at least 2 bands")
    d = np.asarray(depth, dtype=np.float64).ravel()
    lo, hi = float(d.min()), float(d.max())
    if hi <= lo:
        hi = lo + 1.0
    qs = [float(np.quantile(d, i / n)) for i in range(1, n)]
    edges = [lo] + qs + [hi]
    eps = (hi - lo) * 1e-6
    for i in range(1, len(edges)):
        if edges[i] <= edges[i - 1]:
            edges[i] = edges[i - 1] + eps
    edges[-1] = max(edges[-1], edges[-2] + eps)
    return edges


def band_masks(depth: np.ndarray, edges: list[float]) -> list[np.ndarray]:
    """Boolean masks back to front. Their union is the whole frame and they never overlap."""
    d = np.asarray(depth, dtype=np.float64)
    out = []
    for i in range(len(edges) - 1):
        last = i == len(edges) - 2
        m = (d >= edges[i]) & ((d <= edges[i + 1]) if last else (d < edges[i + 1]))
        out.append(m)
    covered = np.zeros(d.shape, dtype=bool)
    for m in out:
        covered |= m
    out[-1] |= ~covered  # anything the float comparisons dropped belongs to the nearest band
    return out


def compose_masks(depth: np.ndarray, occluder: np.ndarray | None = None,
                  subject: np.ndarray | None = None) -> tuple[list[np.ndarray], list[float], list[str]]:
    """The four band masks back to front, with a named OBJECT overriding the quantiles (variant b-prime).

    An object that straddles a quantile edge is the split's one real defect: the dock's hanging lamp
    landed in three bands, the apartment's roof ridge rode the near band away from its own wall. Doc 45
    s45.5 names SAM 2.1 for exactly this. So a SAM mask is not a hint - it is law: every pixel of the
    occluder mask goes WHOLE into `near`, every pixel of the subject mask (minus the occluder) goes
    WHOLE into `subject`, and the depth quantiles then decide only the REMAINDER, over the roles that
    are left. No object can straddle a band it was named out of.

    Returns (masks back to front, the remainder's edges, the roles the quantiles were free to use).
    """
    shape = np.asarray(depth).shape
    occ = np.zeros(shape, dtype=bool) if occluder is None else np.asarray(occluder, dtype=bool)
    sub = np.zeros(shape, dtype=bool) if subject is None else (np.asarray(subject, dtype=bool) & ~occ)
    override = {}
    if occ.any():
        override["near"] = occ
    if sub.any():
        override["subject"] = sub
    remainder = ~(occ | sub)
    free_roles = [r for r in ROLES if r not in override]
    if not remainder.any() or len(free_roles) < 2:
        raise ValueError("the masks left no remainder for the depth quantiles to band")

    edges = band_edges(depth[remainder], len(free_roles))
    free = [m & remainder for m in band_masks(depth, edges)]
    covered = np.zeros(shape, dtype=bool)
    for m in free:
        covered |= m
    free[-1] |= remainder & ~covered  # a remainder pixel the float edges dropped joins the nearest free band

    masks, i = [], 0
    for role in ROLES:
        if role in override:
            masks.append(override[role])
        else:
            masks.append(free[i])
            i += 1
    return masks, edges, free_roles


def grow_radius(sigma: float) -> int:
    """doc 45 s45.5: `R_grow = ceil(2 * sigma_optical) + 12 px`."""
    return int(math.ceil(2.0 * float(sigma))) + 12


def dilate(mask: np.ndarray, radius: int) -> np.ndarray:
    if radius <= 0:
        return np.array(mask, dtype=bool, copy=True)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * radius + 1, 2 * radius + 1))
    return cv2.dilate(mask.astype(np.uint8), k, iterations=1).astype(bool)


def layer_alpha_and_hole(masks: list[np.ndarray], i: int, sigma: float) -> tuple[np.ndarray, np.ndarray]:
    """(alpha, hole) for layer `i`: what the layer covers, and which of that is invented.

    The far layer is opaque everywhere and every nearer pixel is a hole. A middle layer keeps its own
    band plus an R_grow margin taken out of the nearer bands. The nearest layer has no hole.
    """
    nearer = np.zeros(masks[0].shape, dtype=bool)
    for m in masks[i + 1:]:
        nearer |= m
    if i == 0:
        return np.ones(masks[0].shape, dtype=bool), nearer
    if i == len(masks) - 1:
        return np.array(masks[i], dtype=bool, copy=True), np.zeros(masks[0].shape, dtype=bool)
    grown = dilate(masks[i], grow_radius(sigma))
    return masks[i] | (grown & nearer), (grown & nearer)


def lab_match(rgb: np.ndarray, region: np.ndarray, ring: np.ndarray) -> np.ndarray:
    """Normalise the region's mu/sigma to the ring's, per channel, in L*a*b* (doc 45 s45.5).

    Returns a NEW RGB uint8 array; the input is never mutated.
    """
    out = np.array(rgb, dtype=np.uint8, copy=True)
    if not region.any() or not ring.any():
        return out
    lab = cv2.cvtColor(out, cv2.COLOR_RGB2LAB).astype(np.float64)
    for c in range(3):
        src, dst = lab[..., c][region], lab[..., c][ring]
        s_sd = float(src.std())
        scale = float(np.clip((float(dst.std()) / s_sd) if s_sd > 1e-6 else 1.0, 0.5, 2.0))
        lab[..., c][region] = (src - src.mean()) * scale + float(dst.mean())
    return cv2.cvtColor(np.clip(lab, 0, 255).astype(np.uint8), cv2.COLOR_LAB2RGB)


def ring_of(region: np.ndarray, width: int) -> np.ndarray:
    """The band of real pixels hugging `region` - the reference the fill is matched to."""
    return dilate(region, max(1, width)) & ~region


def read_depth_png(path: Path) -> tuple[np.ndarray, int]:
    """A depth PNG as float64 in [0,1], plus the bit depth it carried."""
    im = Image.open(path)
    bits = 16 if im.mode in ("I;16", "I;16B", "I", "I;16L") else 8
    arr = np.asarray(im if bits == 16 else im.convert("L"), dtype=np.float64)
    if arr.ndim == 3:
        arr = arr[..., 0]
    return arr / (65535.0 if bits == 16 else 255.0), bits


# ---------------------------------------------------------------- the server


def _post(path: str, payload: dict) -> dict:
    req = urllib.request.Request(BASE + path, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=60).read())


def upload(name: str, png: bytes) -> str:
    boundary = "----split" + uuid.uuid4().hex
    body = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"image\"; filename=\"{name}\"\r\n"
            f"Content-Type: image/png\r\n\r\n").encode() + png + \
           f"\r\n--{boundary}\r\nContent-Disposition: form-data; name=\"overwrite\"\r\n\r\ntrue\r\n--{boundary}--\r\n".encode()
    req = urllib.request.Request(BASE + "/upload/image", data=body,
                                 headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    return json.loads(urllib.request.urlopen(req, timeout=180).read())["name"]


def _await(pid: str, node: str, timeout: int = 900) -> list[bytes]:
    t0 = time.time()
    while time.time() - t0 < timeout:
        time.sleep(1.5)
        h = json.loads(urllib.request.urlopen(BASE + "/history/" + pid, timeout=30).read())
        if pid not in h:
            continue
        st = h[pid].get("status", {})
        if st.get("status_str") == "error":
            raise RuntimeError(json.dumps(st.get("messages"))[:1200])
        outs = h[pid].get("outputs", {}).get(node, {}).get("images", [])
        if outs:
            return [urllib.request.urlopen(
                BASE + f"/view?filename={im['filename']}&subfolder={im.get('subfolder', '')}&type={im['type']}",
                timeout=180).read() for im in outs]
        if st.get("status_str") == "success":
            raise RuntimeError("finished with no image on node " + node)
    raise RuntimeError("timeout waiting for node " + node)


def queue(wf: dict, node: str) -> list[bytes]:
    r = _post("/prompt", {"prompt": wf, "client_id": uuid.uuid4().hex})
    if r.get("node_errors"):
        raise RuntimeError(json.dumps(r["node_errors"])[:1200])
    return _await(r["prompt_id"], node)


def vram_free() -> int:
    try:
        s = json.loads(urllib.request.urlopen(BASE + "/system_stats", timeout=10).read())
        return int(s["devices"][0]["vram_free"])
    except Exception:
        return -1


class VramWatch:
    """Samples free VRAM while the graph runs, so the cost table carries a PEAK and not just an end state.

    The before/after pair alone reads as ~60 MB because Comfy frees the model the moment it is done.
    """

    def __init__(self, period: float = 0.25) -> None:
        self.period, self.min_free, self._stop = period, -1, False
        self._thread: threading.Thread | None = None

    def start(self) -> "VramWatch":
        self.min_free = vram_free()

        def loop() -> None:
            while not self._stop:
                f = vram_free()
                if f > 0 and (self.min_free < 0 or f < self.min_free):
                    self.min_free = f
                time.sleep(self.period)

        self._thread = threading.Thread(target=loop, daemon=True)
        self._thread.start()
        return self

    def stop(self) -> int:
        self._stop = True
        if self._thread is not None:
            self._thread.join(timeout=2.0)
        return self.min_free


def depth_workflow(image: str, model: str) -> dict:
    return {
        "1": {"class_type": "LoadImage", "inputs": {"image": image}},
        "2": {"class_type": "DownloadAndLoadDepthAnythingV2Model", "inputs": {"model": model, "precision": "fp16"}},
        "3": {"class_type": "DepthAnything_V2", "inputs": {"da_model": ["2", 0], "images": ["1", 0]}},
        "9": {"class_type": "SaveImage", "inputs": {"images": ["3", 0], "filename_prefix": "p58-depth"}},
    }


def lama_workflow(image: str, mask: str, seed: int) -> dict:
    return {
        "1": {"class_type": "LoadImage", "inputs": {"image": image}},
        "2": {"class_type": "LoadImage", "inputs": {"image": mask}},
        "3": {"class_type": "ImageToMask", "inputs": {"image": ["2", 0], "channel": "red"}},
        "4": {"class_type": "INPAINT_LoadInpaintModel", "inputs": {"model_name": LAMA_WEIGHT}},
        "5": {"class_type": "INPAINT_InpaintWithModel",
              "inputs": {"inpaint_model": ["4", 0], "image": ["1", 0], "mask": ["3", 0], "seed": seed}},
        "9": {"class_type": "SaveImage", "inputs": {"images": ["5", 0], "filename_prefix": "p58-lama"}},
    }


def sam_points(spec: str) -> str:
    """'x,y;x,y' -> the SAM 2 node's coordinate string (comfy_sam2_mask.py's form, reused verbatim)."""
    return json.dumps([{"x": int(p.split(",")[0]), "y": int(p.split(",")[1])} for p in spec.split(";") if p.strip()])


def sam_workflow(image: str, positive: str, grow: int) -> dict:
    return {
        "1": {"class_type": "LoadImage", "inputs": {"image": image}},
        "2": {"class_type": "DownloadAndLoadSAM2Model",
              "inputs": {"model": SAM_MODEL, "segmentor": "single_image", "device": "cuda", "precision": "fp16"}},
        "3": {"class_type": "PrimitiveString", "inputs": {"value": positive}},
        # `coordinates_negative` is OMITTED, not empty. It is an optional input, and Sam2Segmentation
        # stacks whatever it is handed onto the positive array - "[]" gives a 1-d array and "" a 0-d one,
        # and both raise "all the input arrays must have same number of dimensions". Only absence works.
        "5": {"class_type": "Sam2Segmentation",
              "inputs": {"sam2_model": ["2", 0], "image": ["1", 0], "keep_model_loaded": False,
                         "coordinates_positive": ["3", 0], "individual_objects": False}},
        "6": {"class_type": "GrowMask", "inputs": {"mask": ["5", 0], "expand": grow, "tapered_corners": True}},
        "7": {"class_type": "MaskToImage", "inputs": {"mask": ["6", 0]}},
        "9": {"class_type": "SaveImage", "inputs": {"images": ["7", 0], "filename_prefix": "p58-sam"}},
    }


def sam_mask(plate: Path, spec: str, grow: int, size: tuple[int, int]) -> np.ndarray:
    """A boolean mask of the named object, from SAM 2.1 on the local Comfy (doc 45 s45.5 step 1)."""
    name = upload(f"p58-sam-{plate.stem}.png", plate.read_bytes())
    png = queue(sam_workflow(name, sam_points(spec), grow), "9")[0]
    im = Image.open(io.BytesIO(png)).convert("L")
    if im.size != size:
        im = im.resize(size, Image.NEAREST)
    return np.asarray(im, dtype=np.uint8) > 127


def lama_available() -> bool:
    try:
        o = json.loads(urllib.request.urlopen(BASE + "/object_info/INPAINT_LoadInpaintModel", timeout=15).read())
        return LAMA_WEIGHT in o["INPAINT_LoadInpaintModel"]["input"]["required"]["model_name"][1]["options"]
    except Exception:
        return False


def _png_bytes(im: Image.Image) -> bytes:
    buf = io.BytesIO()
    im.save(buf, format="PNG", optimize=False)
    return buf.getvalue()


def depth_from_server(plate: Path, model_key: str) -> tuple[np.ndarray, int, str]:
    """The depth map as float64 in [0,1], its bit depth, and the model file that produced it."""
    model = MODELS[model_key]
    name = upload(f"p58-{plate.stem}.png", plate.read_bytes())
    png = queue(depth_workflow(name, model), "9")[0]
    im = Image.open(io.BytesIO(png))
    bits = 16 if im.mode in ("I;16", "I;16B", "I", "I;16L") else 8
    arr = np.asarray(im if bits == 16 else im.convert("L"), dtype=np.float64)
    if arr.ndim == 3:
        arr = arr[..., 0]
    return arr / (65535.0 if bits == 16 else 255.0), bits, model


def lama_inpaint(rgb: np.ndarray, hole: np.ndarray, seed: int, tag: str) -> np.ndarray:
    """One LaMa pass on the server. Raises on any failure so the caller can fall back to Telea."""
    img_name = upload(f"p58-lama-img-{tag}.png", _png_bytes(Image.fromarray(rgb)))
    m = np.repeat((hole.astype(np.uint8) * 255)[..., None], 3, axis=2)
    mask_name = upload(f"p58-lama-mask-{tag}.png", _png_bytes(Image.fromarray(m)))
    out = queue(lama_workflow(img_name, mask_name, seed), "9")[0]
    got = np.asarray(Image.open(io.BytesIO(out)).convert("RGB"), dtype=np.uint8)
    if got.shape != rgb.shape:
        got = np.asarray(Image.fromarray(got).resize((rgb.shape[1], rgb.shape[0]), Image.LANCZOS), dtype=np.uint8)
    return got


def telea_inpaint(rgb: np.ndarray, hole: np.ndarray) -> np.ndarray:
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    filled = cv2.inpaint(bgr, hole.astype(np.uint8) * 255, 5, cv2.INPAINT_TELEA)
    return cv2.cvtColor(filled, cv2.COLOR_BGR2RGB)


# ---------------------------------------------------------------- the split


def split(plate: Path, out_dir: Path, *, model_key: str = "vitl_fp16", bands: int = 4, seed: int = 0,
          sigma: float = 2.0, edges_override: list[float] | None = None, depth_png: Path | None = None,
          inpainter: str = "auto", occluder_points: str | None = None, subject_points: str | None = None,
          grow: int = 6, occluder_mask: np.ndarray | None = None,
          subject_mask: np.ndarray | None = None) -> dict:
    t_start = time.time()
    rgb = np.asarray(Image.open(plate).convert("RGB"), dtype=np.uint8)
    h, w = rgb.shape[:2]
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = plate.stem

    serverless = depth_png is not None
    watch = VramWatch() if not serverless else None
    vram_before = -1 if serverless else vram_free()
    if watch is not None:
        watch.start()
    if serverless:
        depth, bits = read_depth_png(depth_png)  # type: ignore[arg-type]
        model_file, t_depth = f"supplied:{depth_png.name}", 0.0  # type: ignore[union-attr]
    else:
        t0 = time.time()
        depth, bits, model_file = depth_from_server(plate, model_key)
        t_depth = time.time() - t0
    if depth.shape != (h, w):
        depth = np.asarray(Image.fromarray((depth * 255).astype(np.uint8)).resize((w, h), Image.BILINEAR),
                           dtype=np.float64) / 255.0

    occ = occluder_mask if occluder_mask is not None else (
        sam_mask(plate, occluder_points, grow, (w, h)) if occluder_points else None)
    sub = subject_mask if subject_mask is not None else (
        sam_mask(plate, subject_points, grow, (w, h)) if subject_points else None)

    if occ is not None or sub is not None:
        if bands != 4:
            raise SystemExit("a SAM override needs the four doc-24 roles (--bands 4)")
        masks, edges, free_roles = compose_masks(depth, occ, sub)
        roles = list(ROLES)
    else:
        free_roles = list(ROLES) if bands == 4 else [f"band{i}" for i in range(bands)]
        edges = list(edges_override) if edges_override else band_edges(depth, bands)
        if len(edges) != bands + 1:
            raise SystemExit(f"--edges needs {bands + 1} values, got {len(edges)}")
        masks = band_masks(depth, edges)
        roles = list(free_roles)

    Image.fromarray((np.clip(depth, 0, 1) * 65535).astype(np.uint16)).save(out_dir / f"{stem}-depth.png")

    used = inpainter
    if inpainter == "auto":
        used = "lama" if lama_available() else "telea-fallback"
    t_paint = 0.0
    layers: list[dict] = []
    notes: list[str] = []
    for i, role in enumerate(roles):
        alpha, hole = layer_alpha_and_hole(masks, i, sigma)
        body = rgb
        if hole.any():
            t0 = time.time()
            if used == "lama":
                try:
                    body = lama_inpaint(rgb, hole, seed, f"{stem}-{role}")
                except Exception as exc:  # the slice must SAY which inpainter ran
                    notes.append(f"lama failed on {role}: {str(exc)[:200]} - fell back to telea")
                    used = "telea-fallback"
                    body = telea_inpaint(rgb, hole)
            else:
                body = telea_inpaint(rgb, hole)
            t_paint += time.time() - t0
            body = lab_match(body, hole, ring_of(hole, grow_radius(sigma)))
            body = np.where(hole[..., None], body, rgb)
        rgba = np.dstack([body, np.where(alpha, 255, 0).astype(np.uint8)])
        Image.fromarray(rgba, mode="RGBA").save(out_dir / f"{stem}-{role}.png")
        j = free_roles.index(role) if role in free_roles else -1
        layers.append({
            "role": role, "path": f"{stem}-{role}.png", "parallax_factor": PARALLAX.get(role, 1.0),
            "source": "quantile" if j >= 0 else "sam2.1-mask",
            "depth_band": [round(edges[j], 6), round(edges[j + 1], 6)] if j >= 0 else None,
            "band_share": round(float(masks[i].mean()), 6),
            "alpha_share": round(float(alpha.mean()), 6),
            "hole_share": round(float(hole.mean()), 6),
            "opaque": bool(alpha.all()),
        })

    min_free = watch.stop() if watch is not None else -1
    vram_after = -1 if serverless else vram_free()
    meta = {
        "plate": str(plate).replace("\\", "/"), "stem": stem, "size": [w, h],
        "model": model_file, "depth_bits": bits, "seed": seed, "sigma": sigma,
        "grow_px": grow_radius(sigma), "bands": bands, "edges": [round(e, 6) for e in edges],
        "quantile_roles": free_roles, "sam": {"model": SAM_MODEL, "grow": grow,
                                              "occluder_points": occluder_points, "subject_points": subject_points}
        if (occ is not None or sub is not None) else None,
        "inpainter": used, "notes": notes, "layers": layers,
        "timings_s": {"depth": round(t_depth, 2), "inpaint": round(t_paint, 2),
                      "wall_clock": round(time.time() - t_start, 2)},
        "vram_free_bytes": {"before": vram_before, "after": vram_after, "min_free_during": min_free,
                            "peak_used": (vram_before - min_free) if vram_before > 0 and min_free > 0 else -1},
    }
    (out_dir / f"{stem}.split.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return meta


def main() -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("--plate", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--model", default="vitl_fp16", choices=sorted(MODELS))
    ap.add_argument("--bands", type=int, default=4)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--sigma", type=float, default=2.0)
    ap.add_argument("--edges", default=None, help="hand thresholds, comma separated (bands+1 values)")
    ap.add_argument("--depth", type=Path, default=None, help="a depth PNG, skipping the server")
    ap.add_argument("--inpainter", default="auto", choices=["auto", "lama", "telea-fallback"])
    ap.add_argument("--occluder", default=None, help="SAM 2.1 points ON the near occluder: x,y;x,y (b-prime)")
    ap.add_argument("--subject", default=None, help="SAM 2.1 points ON the subject: x,y;x,y (b-prime)")
    ap.add_argument("--grow", type=int, default=6, help="SAM mask growth in px")
    a = ap.parse_args()
    edges = [float(x) for x in a.edges.split(",")] if a.edges else None
    meta = split(a.plate, a.out, model_key=a.model, bands=a.bands, seed=a.seed, sigma=a.sigma,
                 edges_override=edges, depth_png=a.depth, inpainter=a.inpainter,
                 occluder_points=a.occluder, subject_points=a.subject, grow=a.grow)
    print(f"{meta['stem']}: inpainter={meta['inpainter']} bits={meta['depth_bits']} "
          f"quantile_roles={meta['quantile_roles']} edges={meta['edges']} "
          f"wall={meta['timings_s']['wall_clock']}s -> {a.out}")
    for lay in meta["layers"]:
        print(f"  {lay['role']:<8} {lay['source']:<13} band={lay['depth_band']} share={lay['band_share']:.3f} "
              f"alpha={lay['alpha_share']:.3f} hole={lay['hole_share']:.3f} opaque={lay['opaque']}")
    for n in notes_of(meta):
        print("  note:", n)
    return 0


def notes_of(meta: dict) -> list[str]:
    return list(meta.get("notes") or [])


if __name__ == "__main__":
    raise SystemExit(main())
