"""STAGE ZERO: the scratch take - free audio before any credit moves.

Two engines, two jobs (operator, 2026-08-30):

  --engine chirp    Chirp 3 HD (cloud, fast) - the LISTEN. Audio in ~a
                    minute so the ear pass starts immediately.
  --engine kokoro   Kokoro-82M (local, ~2x realtime) - the EVIDENCE.
                    Word timestamps (scratch-kokoro.words.json, same
                    schema as take words), a navigable SCRATCH-INDEX.md
                    (jump to any paragraph while listening), and real
                    per-beat durations to replace the rate estimators
                    (measured 1.8% off the EL take vs the estimators'
                    ~10% spread, n=1).
  --engine both     chirp first, then kokoro.

The scratch is a PRE-SPEND instrument: it tests OUR TEXT (ear failures,
pacing, pronouns, number reads) and calibrates timing. It cannot test
ElevenLabs behavior - the 2:00 probe (doc 37 s13) still runs before any
master. Scratch timings never touch the build; the EL take is the clock.

    python scratch_take.py --engine chirp
"""
from __future__ import annotations

import argparse
import base64
import json
import re
import subprocess
import time
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
DEFAULT_EP = REPO / "content/video_engine/projects/systems-and-blowups/steel-and-paper"
DEFAULT_SCRIPT = DEFAULT_EP / "SCRIPT-G-VO.txt"
DEFAULT_OUT = DEFAULT_EP / "vo-f/scratch"
ENV_FILE = Path(r"C:\Users\Snipe\Downloads\Outreach Program\docs\local.env")
CHIRP_VOICE = "en-US-Chirp3-HD-Charon"
KOKORO_VOICE = "am_michael"
SR = 24000

SCRIPT_PATH = DEFAULT_SCRIPT
OUT = DEFAULT_OUT


def load_script() -> str:
    """The spoken text: every beat mark off, backticked or bare.

    The bare form is the one every short writes (`SCRIPT-90S-VO.txt`), and stripping only the backticked form read
    twelve marks aloud - "[ring", "[post-key" - and spent 17.0 s of an 81 s kokoro scratch on them
    (normal-for-which-bridge, 2026-09-12). Both engines read through this door so they cannot disagree again."""
    t = SCRIPT_PATH.read_text(encoding="utf-8")
    return re.sub(r"`?\[[a-z0-9_-]+\]`?", "", t)


def paragraphs(text: str) -> list[str]:
    return [" ".join(p.split()) for p in text.split("\n\n") if p.strip()]


def env_key(name: str) -> str:
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith(name):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit(f"{name} not in {ENV_FILE}")


def run_chirp(rate: float = 1.0) -> None:
    key = env_key("GEMINI_TTS_API_KEY")
    paras = [p.strip() for p in load_script().split("\n\n") if p.strip()]
    batches, cur = [], ""
    for p in paras:
        if cur and len(cur) + len(p) + 2 > 4500:
            batches.append(cur); cur = p
        else:
            cur = (cur + "\n\n" + p) if cur else p
    if cur:
        batches.append(cur)
    OUT.mkdir(parents=True, exist_ok=True)
    segs = []
    t0 = time.time()
    for i, b in enumerate(batches):
        req = urllib.request.Request(
            "https://texttospeech.googleapis.com/v1/text:synthesize",
            data=json.dumps({
                "input": {"text": b},
                "voice": {"languageCode": "en-US", "name": CHIRP_VOICE},
                "audioConfig": {"audioEncoding": "MP3",
                                "sampleRateHertz": SR,
                                "speakingRate": rate},
            }).encode(),
            headers={"Content-Type": "application/json",
                     "X-Goog-Api-Key": key})
        with urllib.request.urlopen(req, timeout=180) as r:
            audio = base64.b64decode(json.loads(r.read())["audioContent"])
        seg = OUT / f"_c{i:02d}.mp3"
        seg.write_bytes(audio)
        segs.append(seg)
        print(f"  chirp {i + 1}/{len(batches)}")
    lst = OUT / "_concat.txt"
    lst.write_text("".join(f"file '{s.name}'\n" for s in segs),
                   encoding="utf-8")
    out = OUT / "scratch-chirp.mp3"
    subprocess.run(["ffmpeg", "-y", "-v", "quiet", "-f", "concat", "-safe",
                    "0", "-i", lst.name, "-c:a", "libmp3lame", "-b:a",
                    "160k", out.name], check=True, cwd=OUT)
    for s in segs:
        s.unlink()
    lst.unlink()
    print(f"scratch-chirp.mp3 in {time.time() - t0:.0f}s "
          f"({len(batches)} calls, free tier)")


def merge_punct(words: list[dict]) -> list[dict]:
    """A stop is part of the word it closes, not a word of its own.

    Kokoro tokenises "once ." as two tokens; a take's words.json carries "once." on one. Every consumer of this
    file (the caption pages, `split_sentences`, a shot table's phrase anchors) reads the take's shape, so the
    scratch has to be the take's shape - the docstring already promises it.  (normal-for-which-bridge, 2026-09-12)"""
    out: list[dict] = []
    for w in words:
        if out and w["w"] and all(c in ".,;:!?\u2014-\"')" for c in w["w"]):
            out[-1]["w"] += w["w"]
            out[-1]["end_s"] = w["end_s"]
            continue
        out.append(dict(w))
    return out


def run_kokoro() -> None:
    import numpy as np
    import soundfile as sf
    from kokoro import KPipeline
    text = load_script()
    paras = paragraphs(text)
    OUT.mkdir(parents=True, exist_ok=True)
    pipe = KPipeline(lang_code="a")
    t0 = time.time()
    wavs, words, index = [], [], []
    offset = 0.0
    for pi, para in enumerate(paras):
        index.append({"para": pi + 1, "at": round(offset, 2),
                      "head": para[:70]})
        for r in pipe(para, voice=KOKORO_VOICE):
            for tok in (r.tokens or []):
                if tok.start_ts is None:
                    continue
                words.append({"w": tok.text,
                              "start_s": round(tok.start_ts + offset, 3),
                              "end_s": round((tok.end_ts or tok.start_ts)
                                             + offset, 3)})
            wavs.append(r.audio.numpy() if hasattr(r.audio, "numpy")
                        else np.asarray(r.audio))
            offset += len(wavs[-1]) / SR
        # paragraph breath: 0.25s inserted + the engine's own settle
        # lands near the compressor's 0.50s inter-sentence target, so the
        # scratch PREDICTS post-compression pacing (operator: the 0.5s
        # version made the pause after "holding you." a beat too long)
        wavs.append(np.zeros(int(SR * 0.25), dtype=np.float32))
        offset += 0.25
    words = merge_punct(words)
    wav = np.concatenate(wavs)
    sf.write(OUT / "scratch-kokoro.wav", wav, SR)
    subprocess.run(["ffmpeg", "-y", "-v", "quiet", "-i",
                    str(OUT / "scratch-kokoro.wav"), "-c:a", "libmp3lame",
                    "-b:a", "160k", str(OUT / "scratch-kokoro.mp3")],
                   check=True)
    (OUT / "scratch-kokoro.wav").unlink()
    dur = len(wav) / SR
    (OUT / "scratch-kokoro.words.json").write_text(
        json.dumps({"engine": "kokoro-82M", "voice": KOKORO_VOICE,
                    "duration_s": round(dur, 2), "words": words},
                   indent=1), encoding="utf-8")
    # navigable ear-pass index + estimator comparison
    n = len(load_script())
    lines = [f"# SCRATCH INDEX - jump points for the ear pass",
             f"",
             f"kokoro {dur / 60:.1f} min for {n:,} chars "
             f"-> {n / dur:.2f} chars/s actual "
             f"(estimators assume 16.05 c/s / 165.6 wpm)",
             ""]
    lines += [f"- {e['at'] // 60:02.0f}:{e['at'] % 60:04.1f}  "
              f"P{e['para']:02d}  {e['head']}" for e in index]
    (OUT / "SCRATCH-INDEX.md").write_text("\n".join(lines) + "\n",
                                          encoding="utf-8")
    print(f"scratch-kokoro.mp3 {dur / 60:.1f} min in "
          f"{time.time() - t0:.0f}s ({dur / (time.time() - t0):.1f}x rt); "
          f"words + index written")


def main() -> int:
    global SCRIPT_PATH, OUT
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine", choices=["chirp", "kokoro", "both"],
                    default="both")
    ap.add_argument("--script", type=Path, default=None,
                    help="Path to script text file")
    ap.add_argument("--out", type=Path, default=None,
                    help="Output directory for scratch audio")
    ap.add_argument("--rate", type=float, default=1.0,
                    help="Speaking rate multiplier (e.g. 1.07 for ~170 WPM)")
    a = ap.parse_args()

    if a.script:
        SCRIPT_PATH = a.script
    if a.out:
        OUT = a.out
    elif a.script:
        OUT = a.script.parent / "scratch"

    if a.engine in ("chirp", "both"):
        run_chirp(rate=a.rate)
    if a.engine in ("kokoro", "both"):
        run_kokoro()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
