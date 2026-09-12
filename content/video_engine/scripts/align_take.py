"""ALIGN A TAKE: local Whisper word-timestamps for an engine that ships none.

E70 (docs/portable/VOICE-PACK.md, OPERATOR-RULINGS.md): Chirp does not ship
on YouTube and does fine on Facebook, so a one-shot renders BOTH takes for
the data. Kokoro carries its own word timestamps out of the pipeline
(scratch_take.py:run_kokoro); Chirp carries none, so a Chirp clock has to be
ALIGNED after the fact. Whisper runs LOCALLY - never a cloud STT call, never
a paid API, per the operator's standing constraint (see MEMORY.md
"Local Whisper, no paid STT"). This tool is that local aligner.

Output schema matches a take's own words.json exactly (scratch_take.py
run_kokoro, ~line 170-173; consumed by authoring/words.py:take_words):
    {"engine": str, "voice": str, "duration_s": float,
     "words": [{"w": str, "start_s": float, "end_s": float}, ...]}

A stop belongs to its word ("once." is ONE token, not "once" + "."):
reused from scratch_take.merge_punct rather than re-implemented (the
docstring there already promises this is every consumer's shape).

Usage:
    align_take.py <audio> --out <words.json> [--script <txt>]
                  [--model small.en] [--engine <name>]

THE LIMIT, measured on the day it was written (2026-09-12): free-form ASR is
not an authoring clock. On the same audio, faster-whisper `small.en` returned
141 words where kokoro's own tokenizer had 155, and the last word's end lagged
by 0.84 s. A shot table anchors its rows on PHRASES (`authoring/words.at`), so
a clock missing one word in eleven cannot carry them. Use this clock to LISTEN
and to time beats; before authoring against a Chirp take, align to the SCRIPT
(forced alignment) rather than to whatever the recogniser heard.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from scratch_take import merge_punct  # noqa: E402  (local import, see sys.path above)


def _load_whisper():
    try:
        from faster_whisper import WhisperModel
    except ImportError as e:
        raise SystemExit(
            "align_take.py needs faster-whisper for local word-level "
            "timestamps and it is not installed in this interpreter. "
            "Install it with: pip install faster-whisper "
            "(no cloud STT call is ever made by this tool)."
        ) from e
    return WhisperModel


def transcribe(audio_path: Path, model_name: str) -> tuple[list[dict], float]:
    """Run local faster-whisper with word_timestamps=True; return
    (words, duration_s) in the take schema's word shape (pre-merge_punct)."""
    WhisperModel = _load_whisper()
    model = WhisperModel(model_name, device="cpu", compute_type="int8")
    segments, info = model.transcribe(
        str(audio_path), word_timestamps=True, beam_size=5,
    )
    words: list[dict] = []
    duration_s = 0.0
    for seg in segments:
        for w in seg.words or []:
            words.append({
                "w": w.word.strip(),
                "start_s": round(w.start, 3),
                "end_s": round(w.end, 3),
            })
            duration_s = max(duration_s, w.end)
    return words, round(duration_s, 2)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("audio", type=Path, help="mp3/wav of the take")
    ap.add_argument("--out", type=Path, required=True,
                     help="words.json to write")
    ap.add_argument("--script", type=Path, default=None,
                     help="the take's own script text, for a word-count check")
    ap.add_argument("--model", default="small.en",
                     help="faster-whisper model name (default small.en)")
    ap.add_argument("--engine", default=None,
                     help="engine name to record (default: the audio stem)")
    args = ap.parse_args()

    if not args.audio.exists():
        raise SystemExit(f"audio not found: {args.audio}")

    words, duration_s = transcribe(args.audio, args.model)
    words = merge_punct(words)

    engine = args.engine or args.audio.stem
    if args.script is not None:
        engine = f"{engine}-aligned"

    payload = {
        "engine": engine,
        "voice": "aligned/faster-whisper",
        "duration_s": duration_s,
        "words": words,
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=1), encoding="utf-8")

    n_aligned = len(words)
    print(f"{args.out} written: {n_aligned} words, "
          f"duration_s={duration_s}")

    if args.script is not None:
        script_text = args.script.read_text(encoding="utf-8")
        n_script = len(script_text.split())
        print(f"script word count: {n_script}  |  aligned word count: "
              f"{n_aligned}  |  delta: {n_aligned - n_script}")


if __name__ == "__main__":
    main()
