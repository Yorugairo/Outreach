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
EP = REPO / "content/video_engine/projects/systems-and-blowups/steel-and-paper"
OUT = EP / "vo-f/scratch"
ENV_FILE = Path(r"C:\Users\Snipe\Downloads\Outreach Program\docs\local.env")
CHIRP_VOICE = "en-US-Chirp3-HD-Charon"
KOKORO_VOICE = "am_michael"
SR = 24000


def load_script() -> str:
    t = (EP / "SCRIPT-G-VO.txt").read_text(encoding="utf-8")
    return re.sub(r"`\[[a-z-]+\]`", "", t)


def paragraphs(text: str) -> list[str]:
    return [" ".join(p.split()) for p in text.split("\n\n") if p.strip()]


def env_key(name: str) -> str:
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith(name):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit(f"{name} not in {ENV_FILE}")


def run_chirp() -> None:
    key = env_key("GEMINI_TTS_API_KEY")
    paras = paragraphs(load_script())
    # batch paragraphs into <4500-byte requests (API cap 5000)
    batches, cur = [], ""
    for p in paras:
        if cur and len((cur + "\n\n" + p).encode()) > 4500:
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
                                "sampleRateHertz": SR},
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
                    "0", "-i", str(lst), "-c:a", "libmp3lame", "-b:a",
                    "160k", str(out)], check=True, cwd=OUT)
    for s in segs:
        s.unlink()
    lst.unlink()
    print(f"scratch-chirp.mp3 in {time.time() - t0:.0f}s "
          f"({len(batches)} calls, free tier)")


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
        # paragraph breath in the scratch render
        wavs.append(np.zeros(int(SR * 0.5), dtype=np.float32))
        offset += 0.5
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
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine", choices=["chirp", "kokoro", "both"],
                    default="both")
    a = ap.parse_args()
    if a.engine in ("chirp", "both"):
        run_chirp()
    if a.engine in ("kokoro", "both"):
        run_kokoro()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
