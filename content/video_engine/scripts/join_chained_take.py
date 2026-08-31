"""Join the chained parts into episode.mp3 - with the seam DEFENDED.

The whisper gate's first real catch (2026-08-30): ElevenLabs appended a
loud vocalized tone (~-1.2 dB peak) in part one's trailing 1.7s, after
the last scripted word. A naive tail trim to last-word + 1.2s would have
carried ~1.1s of it straight into the join.

So the join is now deterministic and defensive:

  part 1 audio survives only to last_word_end + KEEP (natural decay),
  faded to silence over the KEEP window; the rest of the 1.2s settle is
  GENERATED silence. Anything the provider appends after the last word
  dies here, every take, by construction.

Timeline math is untouched: part one's contribution is exactly
last_word_end + SETTLE_S, the same offset build_timeline_f.py computes.

    python join_chained_take.py
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
EP = REPO / "content/video_engine/projects/systems-and-blowups/steel-and-paper"
TAKE = EP / "vo-f/audio"
OUT = EP / "build-f/audio"

SETTLE_S = 1.20   # doc 37 cap - must match build_timeline_f.py
KEEP = 0.35       # natural decay kept after the last word, faded out
FADE_AT = 0.10    # fade starts this long after the word ends


def dur(p: Path) -> float:
    r = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries",
                        "format=duration", "-of", "csv=p=0", str(p)],
                       capture_output=True, text=True, check=True)
    return float(r.stdout.strip())


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    w1 = json.loads((TAKE / "scene_1.words.json").read_text(encoding="utf-8"))
    we = w1["words"][-1]["end_s"]
    tail = dur(TAKE / "scene_1.mp3") - we
    print(f"part 1 last word ends {we:.3f}s; provider tail {tail:.2f}s "
          f"({'DEFENDED' if tail > KEEP else 'clean'})")

    tmp = OUT / "_join"
    tmp.mkdir(exist_ok=True)
    p1 = tmp / "p1.mp3"
    sil = tmp / "sil.mp3"
    # a take can end EXACTLY on its last word (zero provider tail) -
    # keep only the decay that exists and make up the rest in silence
    keep = min(KEEP, max(0.0, dur(TAKE / "scene_1.mp3") - we))
    fade_at = min(FADE_AT, keep)
    subprocess.run(["ffmpeg", "-y", "-v", "quiet", "-i",
                    str(TAKE / "scene_1.mp3"), "-to", f"{we + keep}"]
                   + (["-af", f"afade=t=out:st={we + fade_at}:d={max(0.01, keep - fade_at)}"]
                      if keep > 0.02 else [])
                   + ["-c:a", "libmp3lame", "-b:a", "192k", str(p1)],
                   check=True)
    subprocess.run(["ffmpeg", "-y", "-v", "quiet", "-f", "lavfi", "-i",
                    "anullsrc=r=44100:cl=mono", "-t", f"{SETTLE_S - keep}",
                    "-c:a", "libmp3lame", "-b:a", "192k", str(sil)],
                   check=True)
    lst = tmp / "concat.txt"
    lst.write_text(f"file 'p1.mp3'\nfile 'sil.mp3'\n"
                   f"file '{(TAKE / 'scene_2.mp3').resolve().as_posix()}'\n",
                   encoding="utf-8")
    out = OUT / "episode.mp3"
    subprocess.run(["ffmpeg", "-y", "-v", "quiet", "-f", "concat", "-safe",
                    "0", "-i", str(lst), "-c:a", "libmp3lame", "-b:a",
                    "192k", str(out)], check=True, cwd=tmp)

    got = dur(out)
    want = we + SETTLE_S + dur(TAKE / "scene_2.mp3")
    print(f"episode.mp3: {got:.2f}s (expected {want:.2f}s, "
          f"drift {abs(got - want) * 1000:.0f}ms)")
    if abs(got - want) > 0.15:
        print("FAIL: join drifted - do not build the timeline on this")
        return 1
    print(f"join offset {we + SETTLE_S:.3f}s - matches build_timeline_f")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
