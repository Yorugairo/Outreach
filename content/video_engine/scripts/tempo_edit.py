"""TEMPO-AUTHORED EDIT - runs move, reveals breathe, no seams audible.

Renders an edited take from four semantic inputs the provider never had:
the dead-space caps, the tighten runs, the pause plan, and the tempo map
(attention sentences hold 1.0x, connective sentences run at RUN_RATE).

Artifact-free by construction (v2 after the operator heard clicks):
  - ALL boundaries land at inter-word GAP MIDPOINTS, never word edges
  - stretching happens on decoded PCM per span (ffmpeg atempo on wav)
  - every joint gets a 12ms crossfade, placed in near-silence
  - inserted silences ramp through the crossfade instead of gating

Usage (preview mode, probe):
    python tempo_edit.py --probe
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import tempfile
from pathlib import Path

import numpy as np
import soundfile as sf

REPO = Path(__file__).resolve().parents[3]
EP = REPO / "content/video_engine/projects/systems-and-blowups/steel-and-paper"
SR = 44100
RUN_RATE = 1.10
XF = int(SR * 0.012)          # 12ms crossfade
INTRA, INTRAT = 0.40, 0.30
INTER, INTERT = 0.65, 0.50
TAG_CAP = 1.00
HOOK_HOLD_S = 9.0             # the open never runs
ENDERS = (".", "!", "?", ":")


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9' ]", " ", s.lower())


def decode(path: Path) -> np.ndarray:
    with tempfile.TemporaryDirectory() as td:
        wav = Path(td) / "a.wav"
        subprocess.run(["ffmpeg", "-y", "-v", "quiet", "-i", str(path),
                        "-ac", "1", "-ar", str(SR), str(wav)], check=True)
        data, _ = sf.read(wav, dtype="float32")
    return data


def stretch(seg: np.ndarray, rate: float) -> np.ndarray:
    if abs(rate - 1.0) < 0.001 or len(seg) < SR // 10:
        return seg
    with tempfile.TemporaryDirectory() as td:
        a, b = Path(td) / "a.wav", Path(td) / "b.wav"
        sf.write(a, seg, SR)
        subprocess.run(["ffmpeg", "-y", "-v", "quiet", "-i", str(a),
                        "-filter:a", f"atempo={rate}", str(b)], check=True)
        out, _ = sf.read(b, dtype="float32")
    return out


def xfade_join(pieces: list[np.ndarray]) -> np.ndarray:
    pieces = [p for p in pieces if len(p)]
    out = pieces[0]
    ramp = np.linspace(0, 1, XF, dtype="float32")
    for p in pieces[1:]:
        if len(out) >= XF and len(p) >= XF:
            out = np.concatenate([
                out[:-XF],
                out[-XF:] * (1 - ramp) + p[:XF] * ramp,
                p[XF:]])
        else:
            out = np.concatenate([out, p])
    return out


def build(words, plan, audio):
    wt = [(t, x) for x in words for t in norm(x["w"]).split()]
    wtoks = [t for t, _ in wt]

    def find(txt, end):
        toks = norm(txt).split()
        n = len(toks)
        for i in range(len(wtoks) - n + 1):
            if (wtoks[i:i + n - 1] == toks[:-1]
                    and wtoks[i + n - 1].startswith(toks[-1])):
                return wt[i + n - 1][1]["end"] if end else wt[i][1]["start"]

    # sentence spans
    sents, cur = [], []
    for x in words:
        cur.append(x)
        if x["w"].rstrip("\"”").endswith(ENDERS):
            sents.append((cur[0]["start"], cur[-1]["end"]))
            cur = []
    if cur:
        sents.append((cur[0]["start"], cur[-1]["end"]))
    sent_ends = {round(b, 3) for _, b in sents}

    # attention marks: every pause anchor + every break-tag site
    att = []
    for p in plan["pauses"]:
        anc = p.get("after") or p.get("before")
        t = find(anc, "after" in p and bool(p.get("after")))
        if t is not None:
            att.append((t, p["s"]))
    marks = [t for t, _ in att]
    tag_sites = []
    vo = (EP / "SCRIPT-G-VO.txt").read_text(encoding="utf-8")
    for m in re.finditer(r"`\[[a-z-]+\]`", vo):
        pre = norm(re.sub(r"`\[[a-z-]+\]`", " ", vo[:m.start()])).split()[-4:]
        t = find(" ".join(pre), True)
        if t is not None:
            marks.append(t)
            tag_sites.append(round(t, 3))

    def sent_rate(a, b):
        if a < HOOK_HOLD_S or any(a - 0.05 <= t <= b + 0.05 for t in marks):
            return 1.0
        return RUN_RATE
    rates = [(a, b, sent_rate(a, b)) for a, b in sents]
    nrun = sum(1 for _, _, r in rates if r > 1)
    print(f"  {len(sents)} sentences: {nrun} run at {RUN_RATE}x, "
          f"{len(sents) - nrun} hold 1.0x")

    # compression + insertion ops
    runs = []
    for r in plan.get("tighten_runs", []):
        a, b = find(r["start_after"], True), find(r["end_before"], False)
        if a and b:
            runs.append({"a": a, "b": b, **r})
    ops = []
    for a, b in zip(words, words[1:]):
        g = b["start"] - a["end"]
        at = round(a["end"], 3)
        if g <= 0:
            continue
        if at in tag_sites:
            if g > TAG_CAP:
                ops.append((a["end"], b["start"], TAG_CAP, "cut"))
            continue
        cap, tgt = ((INTER, INTERT) if at in sent_ends
                    else (INTRA, INTRAT))
        for r in runs:
            if r["a"] <= at <= r["b"]:
                cap, tgt = ((r["inter_cap"], r["inter_tgt"])
                            if at in sent_ends
                            else (r["intra_cap"], r["intra_tgt"]))
        if g > cap:
            ops.append((a["end"], b["start"], tgt, "cut"))
    for t, s in att:
        ops.append((t, t, s, "ins"))
    ops.sort(key=lambda o: (o[0], o[3]))

    # rate boundaries snapped to gap midpoints
    gaps = [((x["end"] + y["start"]) / 2)
            for x, y in zip(words, words[1:]) if y["start"] > x["end"]]

    def snap(t):
        best = min(gaps, key=lambda m: abs(m - t), default=t)
        return best if abs(best - t) < 0.6 else t
    bounds = sorted({snap(a) for a, _, _ in rates}
                    | {snap(b) for _, b, _ in rates})

    def rate_of(t):
        for a, b, r in rates:
            if a - 0.05 <= t <= b + 0.05:
                return r
        return RUN_RATE

    pieces = []
    prev = 0.0

    def emit(a, b):
        if b - a < 0.03:
            return
        pts = [a] + [x for x in bounds if a < x < b] + [b]
        for s0, s1 in zip(pts, pts[1:]):
            if s1 - s0 < 0.03:
                continue
            seg = audio[int(s0 * SR):int(s1 * SR)]
            pieces.append(stretch(seg, rate_of((s0 + s1) / 2)))

    for a, b, t, kind in ops:
        if kind == "cut":
            emit(prev, a + t / 2)
            prev = b - t / 2
        else:
            emit(prev, a)
            pieces.append(np.zeros(int(SR * t), dtype="float32"))
            prev = a
    emit(prev, len(audio) / SR)
    return xfade_join(pieces)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", action="store_true")
    ap.parse_args()
    src = EP / "vo-f/audio/scene_99.mp3"
    wj = json.loads((EP / "vo-f/audio/scene_99.words.json")
                    .read_text(encoding="utf-8"))["words"]
    words = [{"w": x["w"], "start": x["start_s"], "end": x["end_s"]}
             for x in wj]
    plan = json.loads((EP / "SCRIPT-G-EDIT-PAUSES.json")
                      .read_text(encoding="utf-8"))
    audio = decode(src)
    out = build(words, plan, audio)
    dest = EP / "vo-f/audio/probe-tempo-preview.mp3"
    with tempfile.TemporaryDirectory() as td:
        wav = Path(td) / "o.wav"
        sf.write(wav, out, SR)
        subprocess.run(["ffmpeg", "-y", "-v", "quiet", "-i", str(wav),
                        "-c:a", "libmp3lame", "-b:a", "192k", str(dest)],
                       check=True)
    print(f"{dest.name}: {len(out) / SR:.1f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
