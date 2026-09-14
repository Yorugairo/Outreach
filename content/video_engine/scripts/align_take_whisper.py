"""Word-time a take that has no alignment (a Chirp scratch take, a pickup) with LOCAL faster-whisper.

ElevenLabs takes arrive with their own alignment; Chirp / Kokoro-less takes do not. This writes the SCRIPT's
own words (punctuation kept, tags dropped) with the waveform's timings, in the take shape every builder reads
(`vo-short/audio/scene_1.words.json`: {"scene_id", "duration_s", "words": [{"w", "start_s", "end_s"}]}).

    python align_take_whisper.py <script.txt> <take.mp3> <out.words.json> [--model small.en]

Whisper normalises numerals ("$122 billion" for "a hundred and twenty-two billion dollars"), so the two token
streams are aligned by difflib; an unmatched script run takes the span the waveform gives that gap, split by
character length. Local only (memory: no paid STT). Prints the matched share and the gaps >= 0.30 s (M13 cut points).
"""
from __future__ import annotations

import difflib
import json
import re
import sys
from pathlib import Path


def norm(tok: str) -> str:
    t = tok.lower().replace("’", "'")
    t = re.sub(r"[^a-z0-9'$%]+", "", t)
    return t


def script_tokens(text: str) -> list[str]:
    text = re.sub(r"\[[a-z-]+\]", " ", text)
    return [t for t in text.split() if norm(t)]


def align(script: list[str], heard: list[dict]) -> list[dict]:
    a = [norm(t) for t in script]
    b = [norm(w["w"]) for w in heard]
    sm = difflib.SequenceMatcher(a=a, b=b, autojunk=False)
    out: list[dict | None] = [None] * len(script)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            for k in range(i2 - i1):
                out[i1 + k] = {"w": script[i1 + k], "start_s": heard[j1 + k]["start_s"], "end_s": heard[j1 + k]["end_s"]}
    matched = sum(1 for o in out if o)
    # fill unmatched runs: the span is prev matched end -> next matched start, unless the heard tokens in the gap bound it tighter
    i = 0
    while i < len(out):
        if out[i]:
            i += 1
            continue
        j = i
        while j < len(out) and not out[j]:
            j += 1
        t0 = out[i - 1]["end_s"] if i > 0 else 0.0
        t1 = out[j]["start_s"] if j < len(out) else heard[-1]["end_s"]
        # heard tokens inside (t0, t1) give the voiced span of the gap
        inside = [w for w in heard if w["start_s"] >= t0 - 1e-6 and w["end_s"] <= t1 + 1e-6]
        if inside:
            t0, t1 = min(t0 if i == 0 else inside[0]["start_s"], inside[0]["start_s"]), inside[-1]["end_s"]
        lens = [max(1, len(norm(script[k]))) for k in range(i, j)]
        tot, t = sum(lens), t0
        for k, L in zip(range(i, j), lens):
            d = (t1 - t0) * L / tot
            out[k] = {"w": script[k], "start_s": round(t, 3), "end_s": round(t + d, 3), "interp": True}
            t += d
        i = j
    return out, matched


def main() -> int:
    argv = [x for x in sys.argv[1:] if not x.startswith("--")]
    model = next((x.split("=", 1)[1] for x in sys.argv[1:] if x.startswith("--model=")), "small.en")
    script_path, take, out_path = Path(argv[0]), Path(argv[1]), Path(argv[2])
    from faster_whisper import WhisperModel
    m = WhisperModel(model, device="cpu", compute_type="int8")
    segs, info = m.transcribe(str(take), word_timestamps=True, beam_size=5)
    heard = [{"w": w.word.strip(), "start_s": round(w.start, 3), "end_s": round(w.end, 3)} for s in segs for w in (s.words or [])]
    script = script_tokens(script_path.read_text(encoding="utf-8"))
    words, matched = align(script, heard)
    for w in words:
        w["start_s"], w["end_s"] = round(w["start_s"], 3), round(w["end_s"], 3)
    doc = {"scene_id": 1, "duration_s": round(info.duration, 3), "engine": f"faster-whisper {model} (local) aligned to {script_path.name}",
           "take": take.name, "words": words}
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(doc, indent=1), encoding="utf-8")
    gaps = [(words[k - 1]["w"], words[k]["w"], round(words[k]["start_s"] - words[k - 1]["end_s"], 2), words[k]["start_s"])
            for k in range(1, len(words)) if words[k]["start_s"] - words[k - 1]["end_s"] >= 0.30]
    print(f"{out_path}: {len(words)} script words, {matched} matched verbatim ({100 * matched / len(words):.0f}%), {len(heard)} heard, {info.duration:.2f}s")
    print("gaps >= 0.30s (cut points):", ", ".join(f"{a}|{b} {g}s@{t:.2f}" for a, b, g, t in gaps))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
