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
    python scratch_take.py --engine kokoro --rate 1.12 --wpm 170-180
    python scratch_take.py --measure vo-h/scratch/scratch-kokoro.words.json --wpm 170-180

A TAKE'S RATE IS MEASURED, NEVER ASSUMED (E99 s82, R26-227): `--rate 1.075` was asked for ~175 wpm and measured 166. Every
kokoro take (and `--measure` on any words file) prints its words, its SPOKEN seconds (first word's start to last word's
end), the measured wpm and the ask; with `--wpm LO-HI` (or one number, +/- ASK_TOL_WPM) a take outside the band exits 2
and is re-taken until it measures so. A chirp take has no word clock: its line is words over the FILE's seconds, said so.
"""
from __future__ import annotations

import argparse
import base64
import json
import re
import subprocess
import time
import urllib.request
from dataclasses import dataclass
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
ASK_TOL_WPM = 5.0          # `--wpm 175` asks for 170-180 (E99 s82: "a scratch at 170-180 wpm is re-taken until it measures so")
EXIT_OUTSIDE = 2           # the measured rate is outside the asked band (or there is nothing to measure)


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


def run_chirp(rate: float = 1.0, ask: tuple[float, float] | None = None) -> int:
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
    # no word clock from chirp: the script's words over the FILE's seconds (edge silence included - the line says so)
    return report_rate(Rate(count_words(load_script()), probe_seconds(out), "file"), ask)


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


def run_kokoro(rate: float = 1.0, ask: tuple[float, float] | None = None) -> int:
    """E99 s81: `--rate` reaches Kokoro too (KPipeline's `speed`); before 2026-09-18 the flag was accepted and ignored on this branch.
    R26-227: returns `rate_exit` of the measured take against `ask` (EXIT_OUTSIDE when it misses the band)."""
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
        for r in pipe(para, voice=KOKORO_VOICE, speed=rate):
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
        json.dumps({"engine": "kokoro-82M", "voice": KOKORO_VOICE, "rate": rate,
                    "duration_s": round(dur, 2), "words": words},
                   indent=1), encoding="utf-8")
    # navigable ear-pass index + estimator comparison
    n = len(load_script())
    lines = [f"# SCRATCH INDEX - jump points for the ear pass",
             f"",
             f"kokoro {dur / 60:.1f} min for {n:,} chars "
             f"-> {n / dur:.2f} chars/s actual "
             f"(estimators assume 16.05 c/s / 165.6 wpm)",
             f"",
             rate_line(measure(words), ask),   # R26-227: the measure against the ask, never the estimator's
             ""]
    lines += [f"- {e['at'] // 60:02.0f}:{e['at'] % 60:04.1f}  "
              f"P{e['para']:02d}  {e['head']}" for e in index]
    (OUT / "SCRATCH-INDEX.md").write_text("\n".join(lines) + "\n",
                                          encoding="utf-8")
    print(f"scratch-kokoro.mp3 {dur / 60:.1f} min in "
          f"{time.time() - t0:.0f}s ({dur / (time.time() - t0):.1f}x rt); "
          f"words + index written")
    return report_rate(measure(words), ask)


# ---------------------------------------------------------------- the measured rate (R26-227, E99 s82)
@dataclass(frozen=True)
class Rate:
    """A take's measured rate: `words` over `spoken_s` seconds; `clock` says which seconds ("spoken" or "file")."""

    words: int
    spoken_s: float
    clock: str = "spoken"

    @property
    def wpm(self) -> float:
        return 60.0 * self.words / self.spoken_s if self.spoken_s > 0 else 0.0


def is_word(token: str) -> bool:
    """A spoken word carries a letter or a digit; a bare stop or dash is not one."""
    return any(c.isalnum() for c in token)


def count_words(text: str) -> int:
    return sum(1 for t in text.split() if is_word(t))


START_KEYS, END_KEYS = ("start_s", "start", "s"), ("end_s", "end", "e")   # a scratch / a take's words.json, a build
                                                                           # timeline.json, a test's word clock


def _clock(word: dict, keys: tuple[str, ...]) -> float | None:
    return next((float(word[k]) for k in keys if word.get(k) is not None), None)


def measure(words: list[dict]) -> Rate:
    """Words over SPOKEN seconds: the first timed word's start to the last one's end (lead-in and tail silence are not
    speech). Tokens with no letter or digit are not counted. Reads any of the word clocks the tools write."""
    timed = [w for w in words if is_word(str(w.get("w", ""))) and _clock(w, START_KEYS) is not None]
    if not timed:
        return Rate(0, 0.0)
    last = timed[-1]
    end = _clock(last, END_KEYS)
    span = (end if end is not None else _clock(last, START_KEYS)) - _clock(timed[0], START_KEYS)
    return Rate(len(timed), max(span, 0.0))


def load_words(path: Path) -> list[dict]:
    """A words file: the scratch's / a take's `{"words": [...]}` or a bare list of `{w, start_s, end_s}`."""
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    return list(d.get("words") or []) if isinstance(d, dict) else list(d)


def probe_seconds(path: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
                          "default=noprint_wrappers=1:nokey=1", str(path)], capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def parse_ask(text: str) -> tuple[float, float]:
    """`--wpm 170-180` -> (170, 180); `--wpm 175` -> 175 +/- ASK_TOL_WPM. Anything else is refused by name."""
    try:
        nums = [float(x) for x in str(text).strip().split("-")]
    except ValueError:
        nums = []
    if len(nums) == 1 and nums[0] > 0:
        return (nums[0] - ASK_TOL_WPM, nums[0] + ASK_TOL_WPM)
    if len(nums) == 2 and 0 < nums[0] <= nums[1]:
        return (nums[0], nums[1])
    raise ValueError(f"--wpm {text!r} is not an ask: give a band LO-HI (e.g. 170-180) or one rate (e.g. 175, "
                     f"+/- {ASK_TOL_WPM:g})")


def rate_line(rate: Rate, ask: tuple[float, float] | None) -> str:
    """ONE line: the words, the seconds (and which clock), the measured wpm, and the ask with the verdict."""
    head = f"rate: {rate.words:,} words / {rate.spoken_s:.1f} s {rate.clock} = {rate.wpm:.1f} wpm"
    if ask is None:
        return f"{head} (no ask - pass --wpm LO-HI to hold the take to one)"
    band = f"ask {ask[0]:g}-{ask[1]:g} wpm"
    if ask[0] <= rate.wpm <= ask[1]:
        return f"{head}, {band}: inside"
    return f"{head}, {band}: OUTSIDE - re-take (E99 s82: a take's rate is measured, never assumed)"


def rate_exit(rate: Rate, ask: tuple[float, float] | None) -> int:
    """EXIT_OUTSIDE when an ask is given and the take misses it (or has nothing to measure), else 0."""
    if ask is None:
        return 0
    if rate.words == 0 or rate.spoken_s <= 0:
        return EXIT_OUTSIDE
    return 0 if ask[0] <= rate.wpm <= ask[1] else EXIT_OUTSIDE


def report_rate(rate: Rate, ask: tuple[float, float] | None) -> int:
    if rate.words == 0:
        print("rate: no timed words to measure - the take carries no word clock")
    else:
        print(rate_line(rate, ask))
    return rate_exit(rate, ask)


def main(argv: list[str] | None = None) -> int:
    global SCRIPT_PATH, OUT
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine", choices=["chirp", "kokoro", "both"],
                    default="both")
    ap.add_argument("--script", type=Path, default=None,
                    help="Path to script text file")
    ap.add_argument("--out", type=Path, default=None,
                    help="Output directory for scratch audio")
    ap.add_argument("--rate", type=float, default=1.0,
                    help="Speaking rate multiplier - a DIAL, not a rate: the take's wpm is measured (R26-227)")
    ap.add_argument("--wpm", default=None, metavar="LO-HI",
                    help="the ask: the band the measured wpm must land in (170-180, or 175 for +/- 5); outside it exits 2")
    ap.add_argument("--measure", type=Path, default=None, metavar="WORDS_JSON",
                    help="synthesize nothing: measure a words file already on disk against --wpm")
    a = ap.parse_args(argv)
    try:
        ask = parse_ask(a.wpm) if a.wpm is not None else None
    except ValueError as exc:
        ap.error(str(exc))
    if a.measure is not None:
        return report_rate(measure(load_words(a.measure)), ask)

    if a.script:
        SCRIPT_PATH = a.script
    if a.out:
        OUT = a.out
    elif a.script:
        OUT = a.script.parent / "scratch"

    codes = []
    if a.engine in ("chirp", "both"):
        codes.append(run_chirp(rate=a.rate, ask=ask))
    if a.engine in ("kokoro", "both"):
        codes.append(run_kokoro(rate=a.rate, ask=ask))
    return max(codes or [0])


if __name__ == "__main__":
    raise SystemExit(main())
