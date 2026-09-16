"""P61 T14 - THE ALIVE PLATE UNDER THE WHOLE DEPTH STACK (a private test-bed beat, never a fixture).

E99 s55 (the operator, 2026-09-16, closing R26-133): *"i think we need both the drift painted as an
option and the alive. Maybe we need the ken burns + alive or parallax+ alive or maybe we need a
slightly smaller drift (maybe 30 px?) AND the alive water."* - and then, of the drift lane's run:
*"when you ran vace did you also run the rest of our depth stack etc?"* It had not: VACE ran over
the flat still alone. This beat is the composition that question asks for, with nothing invented:

    CAPABILITIES:143   the mask-pinned AMBIENT lane - the harbour water generated locally (SAM 2.1
                       mask + Wan 2.1 VACE 1.3B), pinned to the still outside its own mask, and
                       re-composited over the depth split's own `-far` layer so the ALIVE region is
                       the background WALL of a layered plate
    CAPABILITIES:145-6 the layered plate and its sidecar - the containers, the clerk's desk and the
                       hanging lamp, the same planes `camera-layers` reads, standing over that wall
    CAPABILITIES:147   the camera over layers - ONE authored camera, each plane at its own k
    E99 s55 / E49      the drift, PAINTED, at 30 px - the plate's own idle, shared per plane at its
                       own share of k

THE BEAT (Tokyo is the test bed; the approved cut is untouched, E45). One window of the REAL take
(`vo-short/audio/scene_1.words.json`), the REAL words, the real plate:

    "The Treasury's table shows Japan holds over a trillion dollars of our debt, and it's been
     selling since February."

The world is the Tokyo CUSTOMS DOCK - a container quay at dusk with a clerk's ledger desk near the
eye and the harbour behind it - and the harbour is alive. The light lands on the water as the
sentence names Japan (E56: a picture's focus is the light, never a ring), and the camera pushes in
a notch, slowly, as the sentence turns from the table to the selling.

THE CAMERA'S REASON, stated so the parent can judge it: this is an AUTHORED KEY (CAPABILITIES:147's
own grammar, "authored keys per scene"), tied to the sentence's turn, not to a landing. E51's law -
a push is tied to a landing - is the law for a SHIPPING cut, and a beat that goes into one owes a
card landing on that quay. What the key is here for is that a locked camera makes every plane paint
the flat composite exactly (that is the record's own claim, CAPABILITIES:147), so a locked beat
could not show the parallax at all.

NO APPROVED CUT IS TOUCHED and nothing is rendered: this directory holds the beat.

    python build_alive.py
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

BUILD = Path(__file__).resolve().parent
EPISODE = BUILD.parent
REPO = BUILD.parents[5]
SCRIPTS = REPO / "content/video_engine/scripts"
sys.path.insert(0, str(SCRIPTS))

from authoring import Project                                         # noqa: E402
from authoring import audio as A, table as T, words as W              # noqa: E402

TIMELINE_NAME = "tokyo-alive.timeline.json"
PLATE_ID = "world-tokyo-customs-dock-v1-alive"
WORDS_SRC = EPISODE / "vo-short/audio/scene_1.words.json"
AUDIO_SRC = EPISODE / "vo-short/audio/scene_1.mp3"

OPEN_PHRASE = "The Treasury's table"      # the beat opens on the cut before this phrase
LAST_WORD = "February."                   # ... and ends when the sentence ends
TAIL_S = 0.6

DRIFT_PX = 30                             # E99 s55: the named LONG-FORM amplitude
# the harbour band, in stage fractions of the 16:9 stage (the plate is cover-fitted): the water the
# ambient lane actually generated - the life mask's own box, read off the rendered stage.
WATER_BAND = {"kind": "region", "x0": 0.219, "y0": 0.450, "x1": 0.998, "y1": 0.640}


def take_window() -> tuple[float, float, list[dict]]:
    full = json.loads(WORDS_SRC.read_text(encoding="utf-8"))
    full = full["words"] if isinstance(full, dict) else full
    t0 = W.cut_before(full, OPEN_PHRASE, rule="gap")
    i = next(i for i, w in enumerate(full) if w["w"].strip() == LAST_WORD and w["start_s"] > t0)
    t1 = round(full[i]["end_s"] + TAIL_S, 2)
    ws = [{"w": w["w"], "start_s": round(w["start_s"] - t0, 3), "end_s": round(w["end_s"] - t0, 3)}
          for w in full if w["start_s"] >= t0 and w["end_s"] <= t1]
    return t0, t1, ws


def cut_take(t0: float, t1: float, ws: list[dict]) -> Path:
    """The take's own audio and word times, windowed - never re-timed, never re-recorded."""
    out = BUILD / "take"
    out.mkdir(exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(AUDIO_SRC), "-ss", f"{t0:.3f}", "-to", f"{t1:.3f}",
                    "-c:a", "libmp3lame", "-q:a", "2", str(out / "scene_1.mp3")], check=True)
    (out / "scene_1.words.json").write_text(json.dumps({"words": ws}, indent=1), encoding="utf-8")
    return out


def shot_table(ws: list[dict], runtime_s: float) -> list[tuple]:
    at = lambda phrase: W.at(ws, phrase)                                  # noqa: E731
    push_at = at("selling since")
    # THE ROW. The plate id carries E49's idle and E99 s55's amplitude: `;idle=drift;drift=30`. Its LAYERS
    # come from its own sidecar (P58 T2) - the compiler reads them, the background one is the alive clip.
    camera = {"attention": "locked",
              "keys": [{"t": 0.0, "zoom": 1.0, "look": [0.5, 0.5]},
                       {"t": round(push_at, 2), "zoom": 1.0, "look": [0.5, 0.5]},
                       {"t": round(min(push_at + 2.0, runtime_s - 0.2), 2), "zoom": 1.14,
                        "look": [0.60, 0.53], "ease": "cubic"}]}
    return [
        (0.0, round(runtime_s, 2), f"{PLATE_ID};idle=drift;drift={DRIFT_PX}", (0, 0, 0), [], None,
         [{"kind": "spotlight", "at": at("Japan holds"), "dur": "hold", "target": WATER_BAND}],
         camera),
    ]


def main() -> int:
    t0, t1, wsrc = take_window()
    take = cut_take(t0, t1, wsrc)
    ep = Project(here=BUILD, build=BUILD, take=take, take_stem="scene_1",
                 script_name="SCRIPT-90S-VO.claude.txt", episode_id="tokyo-tea-break")
    ws = W.take_words(ep)
    ep.mkdirs()
    shutil.copy2(take / "scene_1.mp3", ep.audio_master)
    runtime_s = A.probe_duration(ep.audio_master)
    W.write_timeline(ep, ws, runtime_s)
    print(f"  take        : {t0:.2f}-{t1:.2f}s of the Tokyo take ({runtime_s:.2f}s, {len(ws)} words)")
    T.caption_pages(BUILD, char_budget=28, max_words=6)
    (BUILD / "evidence-dock.json").write_text("[]\n", encoding="utf-8")
    rows = shot_table(ws, runtime_s)
    T.write_shot_table(BUILD / "SHOT-TABLE-ALIVE.py", rows,
                       '"""P61 T14 - AUTHORED shot table, timed from the take by build_alive.py. Do not hand-edit."""\n')
    T.print_rows(rows)
    return T.compile_timeline(
        BUILD, BUILD,
        timeline_name=TIMELINE_NAME,
        shot_table_file="SHOT-TABLE-ALIVE.py",
        title="Tokyo Tea Break", subtitle="Money Physics - P61 T14 test bed (the alive plate)",
        episode_id="tokyo-tea-break",
        aspect="16:9",
        caption_style="phrase",
        kinetics={"analytic_spring": True, "min_jerk": True, "curvature_stroke": True,
                  "plate_idle_paints": True})


if __name__ == "__main__":
    raise SystemExit(main())
