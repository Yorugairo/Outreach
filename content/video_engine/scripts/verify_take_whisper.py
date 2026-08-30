"""The WHISPER GATE - transcribe what was actually said, diff it against
the script.

ElevenLabs alignment maps the INTENDED text onto the waveform - it cannot
tell you the model vocalized something that was never a word (the 0:08
"thumb" from a mangled break tag). Whisper transcribes the waveform with
no knowledge of the script, so the diff catches exactly that class:

  INSERTED   spoken but not in the script (vocalized tags, stutters)
  DELETED    scripted but never spoken (dropped lines)
  REPLACED   substitutions (misreads; whisper noise below threshold ok)

Runs AFTER record, BEFORE build_timeline_f.py:

    python verify_take_whisper.py            # gate all recorded parts
    python verify_take_whisper.py --model small.en

FAIL on any insertion run of >=1 non-noise word, or WER > 5%.
"""
from __future__ import annotations

import argparse
import difflib
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
EP = REPO / "content/video_engine/projects/systems-and-blowups/steel-and-paper"
VO_DIR = EP / "vo-f/audio"

# whisper hears these at seams without any defect behind them
NOISE = {"the", "a", "and", "uh", "um", "mm", "hm", "oh", "ah"}
WER_CAP = 0.05


def norm_tokens(text: str) -> list[str]:
    text = re.sub(r"`?\[[a-z-]+\]`?", " ", text)      # pause marks
    text = re.sub(r"<[^>]+>", " ", text)               # any literal tags
    text = text.lower().replace("&", " and ")
    text = re.sub(r"[^a-z0-9' ]", " ", text)
    return text.split()


def transcribe(model, path: Path) -> list[str]:
    segs, _ = model.transcribe(str(path), language="en", beam_size=5,
                               vad_filter=False)
    return norm_tokens(" ".join(s.text for s in segs))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="base.en")
    args = ap.parse_args()

    import json as _json
    man = EP / "vo-f/chained-take.json"
    pairs = []
    if man.exists():
        for prt in _json.loads(man.read_text(encoding="utf-8"))["parts"]:
            audio = Path(prt["audio"])
            text = EP / f"SCRIPT-G-VO-part{prt['part']}.txt"
            if audio.exists() and text.exists():
                pairs.append((audio, text))
    if not pairs:
        print("no recorded audio found under build-f/audio - record first")
        return 1

    from faster_whisper import WhisperModel
    print(f"loading whisper {args.model} (cpu, int8)...")
    model = WhisperModel(args.model, device="cpu", compute_type="int8")

    fails = []
    for audio, text in pairs:
        expect = norm_tokens(text.read_text(encoding="utf-8"))
        heard = transcribe(model, audio)
        sm = difflib.SequenceMatcher(a=expect, b=heard, autojunk=False)
        errs = 0
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag == "equal":
                continue
            errs += max(i2 - i1, j2 - j1)
            exp, got = " ".join(expect[i1:i2]), " ".join(heard[j1:j2])
            if tag == "insert" and all(w in NOISE for w in heard[j1:j2]):
                continue                       # seam noise, not a defect
            ctx = " ".join(expect[max(0, i1 - 4):i1])
            label = {"insert": "INSERTED", "delete": "DELETED",
                     "replace": "REPLACED"}[tag]
            line = (f"  {label:9s} after '...{ctx}': "
                    f"script={exp!r} heard={got!r}")
            # substitutions are usually whisper mishearing numerals/names;
            # flag them, FAIL only insertions and deletions
            if tag in ("insert", "delete"):
                fails.append(f"{audio.name}: {line.strip()}")
            print(line)
        wer = errs / max(1, len(expect))
        verdict = "OK" if wer <= WER_CAP else "HIGH"
        print(f"{audio.name}: {len(heard)} words heard vs {len(expect)} "
              f"scripted - WER {wer:.1%} [{verdict}]")
        if wer > WER_CAP:
            fails.append(f"{audio.name}: WER {wer:.1%} exceeds {WER_CAP:.0%}")

    print()
    if fails:
        print("WHISPER GATE: FAIL")
        for f in fails:
            print(" ", f)
        return 1
    print("WHISPER GATE: CLEAN - what was said is what was written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
