"""MICRO-REPAIR: excise a sub-word defect from a take, free.

Operator doctrine (2026-08-30): provider micro-stutters (doubled
plosives, repeated glides) are EDITED OUT, not re-rendered - the editor
owns time. A repair is a PCM excision, the word timeline shifted to
match, and a before/after clip for the ear.

Joint style (operator-corrected same day): cuts land in closure
silence, so the joint is a BUTT SPLICE snapped to the nearest
zero-crossing on each side - NO crossfade. A fade across the joint
multiplies the surviving consonant's attack toward zero and the ear
hears the next word arrive quiet ("it" after "built"). Zero-cross
snapping alone is what prevents the click.

    python repair_microcut.py scene_1 23.946 23.966
"""
import json, subprocess, sys, tempfile, shutil
from pathlib import Path
import numpy as np, soundfile as sf

REPO = Path(__file__).resolve().parents[3]
EP = REPO / "content/video_engine/projects/systems-and-blowups/steel-and-paper"
ZC_SPAN = 200  # samples (~4.5ms) searched around each edge for a zero-crossing


def snap_zero_cross(d: np.ndarray, idx: int) -> int:
    lo, hi = max(1, idx - ZC_SPAN), min(len(d) - 1, idx + ZC_SPAN)
    best, bd = idx, ZC_SPAN + 1
    for i in range(lo, hi):
        if d[i - 1] <= 0 <= d[i] or d[i - 1] >= 0 >= d[i]:
            if abs(i - idx) < bd:
                best, bd = i, abs(i - idx)
    return best


def main() -> int:
    scene, a, b = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
    src = EP / f"vo-f/audio/{scene}.mp3"
    wj = EP / f"vo-f/audio/{scene}.words.json"
    bak = src.with_suffix(".mp3.prerepair")
    if not bak.exists():
        shutil.copy(src, bak)
    with tempfile.TemporaryDirectory() as td:
        wav = Path(td) / "x.wav"
        subprocess.run(["ffmpeg", "-y", "-v", "quiet", "-i", str(src),
                        "-ac", "1", "-ar", "44100", str(wav)], check=True)
        d, sr = sf.read(wav, dtype="float32")
        i0 = snap_zero_cross(d, int(a * sr))
        i1 = snap_zero_cross(d, int(b * sr))
        joined = np.concatenate([d[:i0], d[i1:]])
        out = Path(td) / "o.wav"
        sf.write(out, joined, sr)
        subprocess.run(["ffmpeg", "-y", "-v", "quiet", "-i", str(out),
                        "-c:a", "libmp3lame", "-b:a", "192k", str(src)],
                       check=True)
        cut = (i1 - i0) / sr
    payload = json.loads(wj.read_text(encoding="utf-8"))
    for w in payload["words"]:
        if w["start_s"] >= b:
            w["start_s"] = round(w["start_s"] - cut, 3)
            w["end_s"] = round(w["end_s"] - cut, 3)
        elif w["end_s"] > a:
            w["end_s"] = round(max(w["start_s"], w["end_s"] - cut), 3)
    payload["duration_s"] = round(payload["duration_s"] - cut, 3)
    payload["micro_repairs"] = payload.get("micro_repairs", []) + [
        {"cut": [a, b], "joint": "zero-cross butt",
         "note": "operator-directed micro-repair"}]
    wj.write_text(json.dumps(payload), encoding="utf-8")
    print(f"excised {cut*1000:.0f}ms at {i0/44100:.3f}s from {scene} "
          f"(zero-cross butt joint, backup: {bak.name}); words shifted")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
