"""G-b / G-c / G-e / G-m / G-n - the comfy and parallax configuration gate (P37 T2, T8).

Reads a ComfyUI job description - today the parallax runner's literal dials, or a Wan/LTX
job JSON - and FAILs anything doc 45 / doc 49 settled. It never edits the runner; a
verdict is final (CHECK-RESPONSIBILITIES, mechanical kind).

    python gate_comfy_config.py tools/google-flow-driver/src/parallax-runner.mjs
    python gate_comfy_config.py job.json --plate-kind world
    python gate_comfy_config.py tools/google-flow-driver/src/parallax-runner.mjs --plate-kind actor   # FAILs: G-b

Every finding names the rule and the source it enforces, the way gate_motion_density's
Gate does; the last line is VERDICT: PASS|FAIL and the exit code follows it.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

# the rulings each check enforces
SRC_G_B = "47 s2 G-b / 45 s45.2 - the viability matrix: parallax is for WORLD plates; actor, prop and evidence plates and any plate carrying text are excluded"
SRC_G_C = "47 s2 G-c / 45 s45.3-45.4 - the dials: intensity 0.10-0.12 (strength is inert without a feature), tiling none, ssaa >= 1.5, quality >= 80, ViT-Large depth"
SRC_G_E = "47 s2 G-e / 45 s45.3 - tiling_mode mirror is the kaleidoscope ceiling"
SRC_G_M = "47 s2 G-m / 49 s49.2 - frame laws: Wan T = 4k+1, LTX N = 8n+1"
SRC_G_N = "47 s2 G-n / 49 s49.2-49.3 - Wan I2V CFG <= 4.5, LTX CFG <= 4.5, no unscaled FP8 text encoder, no quantized Wan VAE"

INTENSITY = (0.10, 0.12)
SSAA_MIN = 1.5
QUALITY_MIN = 80
CFG_MAX = 4.5
PARALLAX_PLATE_KINDS = {"world"}


@dataclass(frozen=True)
class Finding:
    rule: str
    detail: str
    src: str

    def line(self) -> str:
        return f"FAIL {self.rule}: {self.detail}\n     {self.src}"


def _nums(pattern: str, text: str) -> list[float]:
    return [float(v) for v in re.findall(pattern, text)]


def check_runner(text: str) -> list[Finding]:
    """The parallax runner's literal dials, read as text - the six presets and the Depthflow node."""
    out: list[Finding] = []
    bad = [v for v in _nums(r'"intensity":\s*([0-9.]+)', text) if not (INTENSITY[0] <= v <= INTENSITY[1])]
    if bad:
        out.append(Finding("G-c intensity", f"{len(bad)} preset(s) outside {INTENSITY}: {sorted(set(bad))} (1.0 is 7-12x the range; this is the displacement, not `strength`)", SRC_G_C))
    for m in re.findall(r'"tiling_mode":\s*"([a-z]+)"', text):
        if m != "none":
            out.append(Finding("G-e tiling_mode", f'"{m}" - only "none" (with the 1.10x crop) avoids the kaleidoscope ceiling', SRC_G_E))
    for v in _nums(r'"ssaa":\s*([0-9.]+)', text):
        if v < SSAA_MIN:
            out.append(Finding("G-c ssaa", f"{v} < {SSAA_MIN} - edge crawl on thin silhouettes", SRC_G_C))
    for v in _nums(r'"quality":\s*([0-9.]+)', text):
        if v < QUALITY_MIN:
            out.append(Finding("G-c quality", f"{v:g} < {QUALITY_MIN} - compression around displacement vectors", SRC_G_C))
    for m in re.findall(r'"model":\s*"(depth_anything[^"]+)"', text):
        if "vitl" not in m:
            out.append(Finding("G-c model", f"{m} - ViT-Small blurs depth boundaries; take ViT-Large (precision per X6)", SRC_G_C))
    return out


def check_job(job: dict) -> list[Finding]:
    """A Wan / LTX job JSON: frame law and conditioning limits. Keys read leniently."""
    out: list[Finding] = []
    model = str(job.get("model", "")).lower()
    frames = job.get("num_frames") or job.get("frames") or job.get("length")
    if frames is not None:
        n = int(frames)
        if "wan" in model and (n - 1) % 4:
            out.append(Finding("G-m frames", f"Wan num_frames {n} is not 4k+1", SRC_G_M))
        if "ltx" in model and (n - 1) % 8:
            out.append(Finding("G-m frames", f"LTX num_frames {n} is not 8n+1", SRC_G_M))
    cfg = job.get("cfg") or job.get("guidance") or job.get("cfg_scale")
    if cfg is not None and float(cfg) > CFG_MAX and ("wan" in model or "ltx" in model):
        out.append(Finding("G-n cfg", f"CFG {cfg} > {CFG_MAX}", SRC_G_N))
    te = str(job.get("text_encoder", "")).lower()
    if "fp8" in te and "scaled" not in te:
        out.append(Finding("G-n text encoder", f"unscaled FP8 text encoder: {te}", SRC_G_N))
    vae = str(job.get("vae", "")).lower()
    if "wan" in model and any(q in vae for q in ("fp8", "int8", "q4", "q8", "gguf")):
        out.append(Finding("G-n vae", f"quantized Wan VAE: {vae}", SRC_G_N))
    return out


def check_plate(plate_kind: str | None, has_text: bool) -> list[Finding]:
    out: list[Finding] = []
    if plate_kind and plate_kind not in PARALLAX_PLATE_KINDS:
        out.append(Finding("G-b plate kind", f"parallax on a {plate_kind!r} plate - the matrix allows {sorted(PARALLAX_PLATE_KINDS)} only", SRC_G_B))
    if has_text:
        out.append(Finding("G-b text", "the plate carries text - displacement warps letterforms; parallax is excluded", SRC_G_B))
    return out


def run(target: Path, plate_kind: str | None = None, has_text: bool = False) -> list[Finding]:
    text = target.read_text(encoding="utf-8")
    findings = check_plate(plate_kind, has_text)
    if target.suffix == ".json":
        findings += check_job(json.loads(text))
    else:
        findings += check_runner(text)
    return findings


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("target", help="parallax-runner.mjs, or a Wan/LTX job JSON")
    ap.add_argument("--plate-kind", choices=["world", "actor", "prop", "evidence"])
    ap.add_argument("--has-text", action="store_true")
    args = ap.parse_args()
    findings = run(Path(args.target), args.plate_kind, args.has_text)
    for f in findings:
        print(f.line())
    print(f"VERDICT: {'FAIL' if findings else 'PASS'} ({len(findings)} finding{'s' if len(findings) != 1 else ''}) - {args.target}")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
