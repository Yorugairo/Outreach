"""RE-TIME A TAKE - kill the dead space, then change the tempo; the words re-timed exactly, never re-aligned.

The record: doc 37 s14 (operator, 2026-08-30) - "kill the dead space, THEN add the breaks": intra-sentence gaps above
0.40 s tighten to 0.30 s, inter-sentence gaps above 0.65 s tighten to 0.50 s (`compress_dead_space.py` does it on the
long-form JOINED take through the episode timeline; this tool does the same caps on a single scene take + its words file).
E34: we deliver near 180 WPM. A tempo change is `atempo` (pitch-preserving, WSOLA) on the compressed take; a word's
timing scales by exactly 1/tempo, so the words file stays the clock without a second Whisper pass (the cuts are inside
silences and never touch a word). The original take and words are never modified; the output is a new stem.

    python retime_take.py <take.mp3> [--gaps] [--tempo 1.06] [--out <stem>]

Prints the accounting (gaps found, seconds removed, the new pace) and verifies the written file's duration against the
prediction. Whisper-gate the result if the tempo is large (verify_take_whisper.py --audio <stem>.mp3 --script ...).
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

INTRA_CAP, INTRA_TGT = 0.40, 0.30
INTER_CAP, INTER_TGT = 0.65, 0.50
SENT_END = (".", "?", "!", ":", ";")
JOIN_FADE_S = 0.004   # a 4 ms ramp on each side of a cut so a join inside a silence cannot click


def probe(path: Path) -> tuple[float, int, int]:
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries",
                          "stream=sample_rate,channels:format=duration", "-of", "json", str(path)],
                         capture_output=True, text=True, check=True).stdout
    j = json.loads(out)
    st = j["streams"][0]
    return float(j["format"]["duration"]), int(st["sample_rate"]), int(st["channels"])


def decode(path: Path, sr: int, ch: int) -> np.ndarray:
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-f", "s16le", "-ac", str(ch), "-ar", str(sr), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.int16).reshape(-1, ch)


def encode(pcm: np.ndarray, sr: int, ch: int, out: Path, tempo: float | None) -> None:
    af = ["-af", f"atempo={tempo}"] if tempo and abs(tempo - 1.0) > 1e-6 else []
    codec = ["-c:a", "libmp3lame", "-q:a", "2"] if out.suffix.lower() == ".mp3" else []
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "s16le", "-ac", str(ch), "-ar", str(sr), "-i", "-", *af, *codec, str(out)],
                   input=pcm.astype(np.int16).tobytes(), check=True)


def cut_gaps(words: list[dict], pcm: np.ndarray, sr: int) -> tuple[list[dict], np.ndarray, list[tuple]]:
    """Remove the middle of every gap over its cap so what remains is the target; return the shifted words, the audio, the log."""
    cuts = []   # (t_from, t_to) in original time, ascending
    for a, b in zip(words, words[1:]):
        g = b["start_s"] - a["end_s"]
        if g <= 0:
            continue
        sent = a["w"].strip().endswith(SENT_END)
        cap, tgt = (INTER_CAP, INTER_TGT) if sent else (INTRA_CAP, INTRA_TGT)
        if g > cap:
            cuts.append((round(a["end_s"] + tgt / 2, 4), round(b["start_s"] - tgt / 2, 4), a["w"], b["w"], sent, g))
    keep, pos = [], 0.0
    for c in cuts:
        keep.append((pos, c[0])); pos = c[1]
    keep.append((pos, len(pcm) / sr))
    fade = max(1, int(JOIN_FADE_S * sr))
    parts = []
    for i, (t0, t1) in enumerate(keep):
        seg = pcm[int(round(t0 * sr)):int(round(t1 * sr))].astype(np.float32)
        if len(seg) == 0:
            continue
        if i > 0 and len(seg) > fade:
            seg[:fade] *= np.linspace(0, 1, fade)[:, None]
        if i < len(keep) - 1 and len(seg) > fade:
            seg[-fade:] *= np.linspace(1, 0, fade)[:, None]
        parts.append(seg)
    audio = np.concatenate(parts) if parts else pcm.astype(np.float32)
    # shift the words: every word after a cut moves up by the cut's length
    out, removed = [], 0.0
    ci = 0
    for w in words:
        while ci < len(cuts) and cuts[ci][1] <= w["start_s"] + 1e-6:
            removed += cuts[ci][1] - cuts[ci][0]; ci += 1
        out.append({**w, "start_s": round(w["start_s"] - removed, 3), "end_s": round(w["end_s"] - removed, 3)})
    return out, audio, cuts


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("take", type=Path)
    ap.add_argument("--gaps", action="store_true", help="doc 37 s14 caps: intra >0.40 -> 0.30, inter >0.65 -> 0.50")
    ap.add_argument("--tempo", type=float, default=1.0, help="atempo factor (1.06 = six percent faster)")
    ap.add_argument("--out", type=str, default=None, help="output stem (default <take>-retimed)")
    a = ap.parse_args()
    take = a.take
    words_p = take.with_suffix(".words.json")
    meta = json.loads(words_p.read_text(encoding="utf-8"))
    words = meta["words"]
    dur, sr, ch = probe(take)
    pcm = decode(take, sr, ch)
    n0, span0 = len(words), words[-1]["end_s"] - words[0]["start_s"]
    print(f"take {take.name}: {dur:.2f}s, {sr} Hz x{ch}, {n0} words, {n0 / (span0 / 60):.1f} WPM over the words' span")
    cuts = []
    if a.gaps:
        words, pcm, cuts = cut_gaps(words, pcm, sr)
        removed = sum(c[1] - c[0] for c in cuts)
        print(f"gaps: {len(cuts)} over the caps, {removed:.2f}s removed "
              f"({sum(1 for c in cuts if c[4])} sentence settles -> {INTER_TGT}s, {sum(1 for c in cuts if not c[4])} mid-sentence -> {INTRA_TGT}s)")
        for c in cuts:
            print(f"   {c[0]:6.2f}  '{c[2]}' -> '{c[3]}'  {c[5]:.2f}s -> {INTER_TGT if c[4] else INTRA_TGT}s")
    if abs(a.tempo - 1.0) > 1e-6:
        words = [{**w, "start_s": round(w["start_s"] / a.tempo, 3), "end_s": round(w["end_s"] / a.tempo, 3)} for w in words]
    stem = a.out or f"{take.stem}-retimed"
    out = take.with_name(f"{stem}{take.suffix}")
    encode(pcm, sr, ch, out, a.tempo if abs(a.tempo - 1.0) > 1e-6 else None)
    dur1, _, _ = probe(out)
    predicted = (len(pcm) / sr) / a.tempo
    span1 = words[-1]["end_s"] - words[0]["start_s"]
    out_meta = {**meta, "duration_s": round(dur1, 3), "take": out.name,
                "engine": f"{meta.get('engine', '?')} | retime_take: " + (f"gaps doc37 caps ({len(cuts)} cut, {sum(c[1]-c[0] for c in cuts):.2f}s); " if a.gaps else "") + f"atempo {a.tempo}",
                "retimed_from": take.name, "words": words}
    out.with_suffix(".words.json").write_text(json.dumps(out_meta, indent=1, ensure_ascii=False), encoding="utf-8")
    ok = abs(dur1 - predicted) < 0.08 and words[-1]["end_s"] <= dur1 + 0.02
    print(f"wrote {out.name}: {dur1:.2f}s (predicted {predicted:.2f}s), {len(words)} words, {len(words) / (span1 / 60):.1f} WPM; "
          f"{dur - dur1:.2f}s shorter than the take  {'OK' if ok else 'MISMATCH'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
