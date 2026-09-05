"""Pace the recorded brand line from its own word clock (operator, 2026-09-05: "it reads too fast, edit it so that we
have pauses, like half savors / periods instead of commas": "Not a panic. Not a plot. / Mechanics.").

The recording is cut at the midpoint of each word gap and the three strokes are re-joined with room the take itself
gives a period (the Tokyo take's period gaps run 0.07-0.60 s, p75 0.44): PAUSE_1 after "panic." at the top of that range,
PAUSE_2 before "Mechanics." a savor beat, longer - the third stroke stands alone. 8 ms fades at every cut so nothing
clicks. Writes brand-line-paced.mp3 + .words.json (the shifted clock) beside the take; every short stitches THAT.

    python pace_brand_line.py            # rebuilds vo/audio/brand-line-paced.mp3 from vo/audio/scene_1.mp3
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "vo/audio/scene_1.mp3"
WORDS = HERE / "vo/audio/scene_1.words.json"
OUT = HERE / "vo/audio/brand-line-paced.mp3"
OUT_WORDS = HERE / "vo/audio/brand-line-paced.words.json"
PAUSES = {"panic.": 0.5, "plot.": 0.8}   # seconds of room AFTER the word: a period's worth, then a savor beat
FADE = 0.008


def main() -> int:
    words = json.load(open(WORDS, encoding="utf-8"))["words"]
    key = lambda w: str(w.get("w", w.get("word", "")))
    s_of = lambda w: float(w.get("start", w.get("start_s")))
    e_of = lambda w: float(w.get("end", w.get("end_s")))
    total = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(SRC)],
                                 capture_output=True, text=True).stdout)
    # segments: [0, cut1], [cut1, cut2], [cut2, end] - each cut at the midpoint of the gap after a paused word
    cuts = []
    for a, b in zip(words, words[1:]):
        if key(a) in PAUSES:
            cuts.append((round((e_of(a) + s_of(b)) / 2, 3), PAUSES[key(a)]))
    bounds = [0.0] + [c for c, _ in cuts] + [total]
    segs = list(zip(bounds, bounds[1:]))
    parts, inputs, n = [], [], 0
    for i, (a, b) in enumerate(segs):
        inputs += ["-i", str(SRC)]
        parts.append(f"[{n}:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d={FADE},afade=t=out:st={max(0.0, b - a - FADE)}:d={FADE},aresample=44100,aformat=channel_layouts=mono[s{i}]")
        n += 1
        if i < len(cuts):
            inputs += ["-f", "lavfi", "-t", str(cuts[i][1]), "-i", "anullsrc=r=44100:cl=mono"]
            parts.append(f"[{n}:a]aresample=44100,aformat=channel_layouts=mono[p{i}]")
            n += 1
    chain = "".join(f"[s{i}][p{i}]" if i < len(cuts) else f"[s{i}]" for i in range(len(segs)))
    fc = ";".join(parts) + f";{chain}concat=n={n}:v=0:a=1[out]"
    subprocess.run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", fc, "-map", "[out]", "-c:a", "libmp3lame", "-q:a", "2", str(OUT)], check=True)
    # the shifted word clock: every word after a cut moves by the pauses inserted before it
    shifted, shift = [], 0.0
    for w in words:
        t0 = s_of(w)
        offs = sum(p for c, p in cuts if c <= t0)
        shifted.append({"w": key(w), "start": round(t0 + offs, 3), "end": round(e_of(w) + offs, 3)})
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(OUT)], capture_output=True, text=True).stdout)
    OUT_WORDS.write_text(json.dumps({"source": SRC.name, "pauses_after": PAUSES, "cuts": cuts, "duration_s": round(dur, 3), "words": shifted}, indent=1), encoding="utf-8")
    print(f"{OUT.name}: {dur:.2f}s; cuts {cuts}; words {[(w['w'], w['start'], w['end']) for w in shifted]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
