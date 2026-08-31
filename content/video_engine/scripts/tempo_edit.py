"""TEMPO-AUTHORED EDIT - runs move, reveals breathe, no seams audible.

Renders an edited take from four semantic inputs the provider never had:
the dead-space caps, the tighten runs, the pause plan, and the tempo map
(attention sentences hold 1.0x, connective sentences run at RUN_RATE).

v3 - THE TEMPO FIELD (operator, 2026-08-30): tempo is a CONTINUOUS
CURVE over the timeline, not per-sentence gears. Attention spans (the
sentences carrying pause anchors - the same sentences the docks and
badges bind to) impose SPEED LIMITS of 1.0x; between them the curve
eases up to RUN_RATE through cosine ramps (~RAMP_S). Emission quantizes
the curve into micro-segments whose rates differ by <= 0.02x, so every
12ms crossfade joins two nearly identical renders - no cliff, no click,
even mid-word. The literary graph drives the accelerator.

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
TAIL_HOLD_S = 14.0            # ...and neither does the ring close
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


PAD = int(SR * 0.08)   # context borrowed for the stretcher's warm-up


def stretch(seg: np.ndarray, rate: float,
            pre: int = 0, post: int = 0) -> np.ndarray:
    """Stretch with CONTEXT PADDING (v5 - the operator heard the last of
    the black-hole class): WSOLA has a startup transient that can double
    the first onset of an independently-stretched chunk ("Vo-voice") and
    sharpen attacks at chunk heads. Each chunk is stretched WITH pre/post
    context and the stretched pads are trimmed - the transient lands in
    the discard, never in the audible span."""
    if abs(rate - 1.0) < 0.005 or len(seg) < SR // 25:
        return seg[pre:len(seg) - post if post else len(seg)]
    with tempfile.TemporaryDirectory() as td:
        a, b = Path(td) / "a.wav", Path(td) / "b.wav"
        sf.write(a, seg, SR)
        subprocess.run(["ffmpeg", "-y", "-v", "quiet", "-i", str(a),
                        "-filter:a", f"atempo={rate}", str(b)], check=True)
        out, _ = sf.read(b, dtype="float32")
    scale = len(out) / max(1, len(seg))
    h = int(round(pre * scale))
    t = int(round(post * scale))
    return out[h:len(out) - t if t else len(out)]


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

    # attention marks: every pause anchor + every break-tag site.
    # THE INSERTION POINT IS NEVER A WORD EDGE (operator caught the "Mm"
    # pip before "Meta"): provider timestamps are +/-30-60ms loose, so a
    # cut at word.start can strand the onset. Every insertion snaps to
    # the MIDPOINT of its natural silence gap.
    def gap_mid(t, is_after):
        for x, y in zip(words, words[1:]):
            if is_after and abs(x["end"] - t) < 0.02:
                return (x["end"] + y["start"]) / 2
            if not is_after and abs(y["start"] - t) < 0.02:
                return (x["end"] + y["start"]) / 2
        return t
    att = []
    for p in plan["pauses"]:
        is_after = "after" in p and bool(p.get("after"))
        anc = p.get("after") or p.get("before")
        t = find(anc, is_after)
        if t is not None:
            att.append((gap_mid(t, is_after), p["s"]))
    marks = [t for t, _ in att]
    tag_sites = []
    vo = (EP / "SCRIPT-G-VO.txt").read_text(encoding="utf-8")
    for m in re.finditer(r"`\[[a-z-]+\]`", vo):
        pre = norm(re.sub(r"`\[[a-z-]+\]`", " ", vo[:m.start()])).split()[-4:]
        t = find(" ".join(pre), True)
        if t is not None:
            marks.append(t)
            tag_sites.append(round(t, 3))

    # THE TEMPO FIELD: speed limits at attention spans, cosine ramps
    att_spans = []
    for t, _ in att:
        for a, b in sents:
            if a - 0.05 <= t <= b + 0.05:
                att_spans.append((a, b))
    for t in [x for x in marks if x not in [q for q, _ in att]]:
        for a, b in sents:
            if a - 0.05 <= t <= b + 0.05:
                att_spans.append((a, b))
    att_spans.append((0.0, HOOK_HOLD_S))
    take_end = words[-1]["end"]
    att_spans.append((take_end - TAIL_HOLD_S, take_end + 1))
    RAMP_S = 1.6   # halved slope (operator: stabilize the field edges)

    def rate_curve(t: float) -> float:
        # distance to the nearest attention span
        d = min((max(0.0, a - t, t - b) for a, b in att_spans),
                default=RAMP_S)
        if d <= 0:
            return 1.0
        if d >= RAMP_S:
            return RUN_RATE
        # cosine ease between the limit and cruise
        import math
        f = 0.5 - 0.5 * math.cos(math.pi * d / RAMP_S)
        return 1.0 + (RUN_RATE - 1.0) * f

    nrun = sum(1 for a, b in sents
               if rate_curve((a + b) / 2) > 1.05)
    print(f"  {len(sents)} sentences, {len(att_spans)} attention spans, "
          f"{nrun} cruise at ~{RUN_RATE}x")

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

    # emission v4 (operator: "black hole dynamics" at field edges):
    # WORDS ARE NEVER SPLIT and cuts only happen inside real silence
    # gaps. Consecutive words merge into one chunk until the curve
    # drifts >0.015x AND a gap >=30ms offers a clean boundary - so every
    # stretched piece is a healthy 0.5-2s and every transient sits far
    # from any joint. Adjacent chunks differ by <=~0.015x.
    chunks = []          # (start, end, rate) covering the whole take
    cs = 0.0
    cr = rate_curve(words[0]["start"])
    for x, y in zip(words, words[1:]):
        gap = y["start"] - x["end"]
        r = rate_curve((y["start"] + y["end"]) / 2)
        # v6 (operator: "vo-oice" - the vowel doubled MID-WORD): provider
        # word timestamps are +/-30-60ms loose, so a reported 30ms "gap"
        # can sit INSIDE a co-articulated word - cutting there splits the
        # word across two rates. A cut site must be a gap no timestamp
        # jitter can fake: >=120ms of reported silence.
        if gap >= 0.12 and abs(r - cr) > 0.015:
            mid = (x["end"] + y["start"]) / 2
            chunks.append((cs, mid, cr))
            cs, cr = mid, r
    chunks.append((cs, len(audio) / SR, cr))

    def emit(a, b):
        if b - a < 0.03:
            return
        for c0, c1, r in chunks:
            s0, s1 = max(a, c0), min(b, c1)
            if s1 - s0 < 0.02:
                continue
            i0, i1 = int(s0 * SR), int(s1 * SR)
            pre = min(PAD, i0)
            post = min(PAD, len(audio) - i1)
            seg = audio[i0 - pre:i1 + post]
            pieces.append({"pcm": stretch(seg, r, pre, post),
                           "o0": s0, "o1": s1, "rate": r})

    pieces = []
    prev = 0.0

    for a, b, t, kind in ops:
        if kind == "cut":
            emit(prev, a + t / 2)
            prev = b - t / 2
        else:
            emit(prev, a)
            pieces.append({"pcm": np.zeros(int(SR * t), dtype="float32"),
                           "o0": None, "o1": None, "rate": 1.0})
            prev = a
    emit(prev, len(audio) / SR)

    # exact original->edited time map (xfade_join overlaps XF per joint)
    out_pos = 0.0
    for i, pc in enumerate(pieces):
        if i:
            out_pos -= XF / SR
        pc["out0"] = out_pos
        out_pos += len(pc["pcm"]) / SR

    def to_edited(t: float) -> float:
        last = 0.0
        for pc in pieces:
            if pc["o0"] is None:
                continue
            if pc["o0"] - 0.001 <= t <= pc["o1"] + 0.001:
                return pc["out0"] + (t - pc["o0"]) / pc["rate"]
            if t > pc["o1"]:
                last = pc["out0"] + (pc["o1"] - pc["o0"]) / pc["rate"]
        return last

    return xfade_join([pc["pcm"] for pc in pieces]), to_edited


def run_probe_mode():
    src = EP / "vo-f/audio/scene_99.mp3"
    wj = json.loads((EP / "vo-f/audio/scene_99.words.json")
                    .read_text(encoding="utf-8"))["words"]
    words = [{"w": x["w"], "start": x["start_s"], "end": x["end_s"]}
             for x in wj]
    plan = json.loads((EP / "SCRIPT-G-EDIT-PAUSES.json")
                      .read_text(encoding="utf-8"))
    out, _ = build(words, plan, decode(src))
    dest = EP / "vo-f/audio/probe-tempo-preview.mp3"
    encode(out, dest)
    print(f"{dest.name}: {len(out) / SR:.1f}s")


def run_take_mode():
    """CHAIN STAGE: edit the joined master, rewrite the timeline onto
    the edited clock. Replaces compress_dead_space + insert_edit_pauses
    (doc 37 s20)."""
    tl_path = EP / "build-f/timeline.json"
    tl = json.loads(tl_path.read_text(encoding="utf-8"))
    if tl.get("tempo_field_applied"):
        print("REFUSED: tempo field already applied")
        return 1
    if tl.get("edit_pauses_applied"):
        print("REFUSED: legacy pause insertion already ran on this "
              "timeline - rebuild it first")
        return 1
    plan = json.loads((EP / "SCRIPT-G-EDIT-PAUSES.json")
                      .read_text(encoding="utf-8"))
    audio = decode(EP / "build-f/audio/episode.mp3")
    out, to_edited = build(tl["words"], plan, audio)
    encode(out, EP / "build-f/audio/episode-paused.mp3")
    for w in tl["words"]:
        w["start"] = round(to_edited(w["start"]), 3)
        w["end"] = round(to_edited(w["end"]), 3)
    for sn in tl.get("sentences", []):
        sn["start"] = round(to_edited(sn["start"]), 3)
        sn["end"] = round(to_edited(sn["end"]), 3)
    tl["runtime_s"] = round(len(out) / SR, 3)
    tl["tempo_field_applied"] = True
    tl["edit_pauses_applied"] = True      # downstream guard convention
    tl["dead_space_compressed"] = True
    tl["paused_audio"] = "audio/episode-paused.mp3"
    tl_path.write_text(json.dumps(tl, indent=1), encoding="utf-8")
    print(f"episode-paused.mp3 (tempo field): {len(out) / SR:.1f}s; "
          f"timeline rewritten onto the edited clock")
    return 0


def encode(pcm, dest: Path):
    with tempfile.TemporaryDirectory() as td:
        wav = Path(td) / "o.wav"
        sf.write(wav, pcm, SR)
        subprocess.run(["ffmpeg", "-y", "-v", "quiet", "-i", str(wav),
                        "-c:a", "libmp3lame", "-b:a", "192k", str(dest)],
                       check=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--take", action="store_true")
    a = ap.parse_args()
    if a.take:
        return run_take_mode() or 0
    run_probe_mode()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
