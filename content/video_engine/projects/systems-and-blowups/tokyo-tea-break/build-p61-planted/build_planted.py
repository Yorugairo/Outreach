"""P61 T3d - THE PLANTED MORPH ON A REAL SCENE (a private test-bed beat, never a fixture).

E99 s60 (the operator, 2026-09-16, on the golden served as a scene): "what you just showed me
makes no sense, you showed me a still frame with an ink splotch held for 6 seconds or
something...we would never do that." A proof is a SCENE - a beat a short could carry.

THE BEAT (Tokyo is the test bed; the approved cut is untouched, E45). One window of the REAL take
(vo-short/audio/scene_1.words.json, trimmed into take/ here), the REAL operator-approved plate
(omni-video/stills/approved/still-c-blue-ties-panel.png, APPROVALS.json 2026-09-05), and the REAL
series object (ev-japan-holdings-v1, 316 monthly TIC points):

    "Three men in blue ties blame the deficit, the Fed, or the vibes at Jackson Hole. On YouTube,
     it's sixty-three stick figures. Here's what nobody on that panel is watching: our biggest
     lender."                                 <- the PLANT: the sentence names the ties and the
                                                 light lands on the three of them (E56)
    | the cut (M13, the gap rule - the register the approved cut is pinned to)
    "The Treasury's table shows Japan holds over a trillion dollars of our debt, and it's been
     selling since February."                 <- the page arrives by enter=morph off the LEFT
                                                 panelist's TIE - its own silhouette, traced from
                                                 this build's last plate frame by
                                                 kinetics/contour.mjs contourSilhouette - the
                                                 ground soaks out from it (E99 s52), the chart
                                                 builds on the shape it became

NO ENGINE FILE IS TOUCHED: the engine is the one committed; this directory holds the beat.

    python build_planted.py       # pass 1 (no poly yet) -> trace_tie.py -> python build_planted.py
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

BUILD = Path(__file__).resolve().parent          # the private build IS its own episode dir: self-contained, so
EPISODE = BUILD.parent                           # nothing outside this folder is written (the take, the plate and
REPO = BUILD.parents[5]                          # the series object are READ from the episode beside it)
SCRIPTS = REPO / "content/video_engine/scripts"
sys.path.insert(0, str(SCRIPTS))

from authoring import Project                                         # noqa: E402
from authoring import audio as A, docks as D, table as T, words as W  # noqa: E402

TIMELINE_NAME = "tokyo-planted.timeline.json"
POLY_FILE = BUILD / "planted-tie.poly.json"      # written by trace_tie.py off the rendered last plate frame
PLATE_ID = "plate-c-blue-ties-panel"
PLATE_SRC = EPISODE / "omni-video/stills/approved/still-c-blue-ties-panel.png"
WORDS_SRC = EPISODE / "vo-short/audio/scene_1.words.json"
AUDIO_SRC = EPISODE / "vo-short/audio/scene_1.mp3"
SERIES = "ev-japan-holdings-v1"

PLANT = "Three men in blue ties"        # the scene opens on the cut before this phrase
TURN = "The Treasury's table"           # ... and the page takes the world on the cut before this one
LAST_WORD = "February."                 # the beat ends when the sentence the chart proves ends
TAIL_S = 1.15                           # ... plus the room the chart's build needs to stand in


# ---- the engine, EXACTLY AS COMMITTED (this lane holds no engine lock) ---------------------------
ENGINE_SRC = "docs/content-video-engine/samples/scene-evidence-engine.mjs"
PINNED = BUILD / "engine-as-committed" / "scene-evidence-engine.mjs"


def pin_engine() -> Path:
    """The engine another lane is editing in the working tree is NOT what this proof runs on. The
    committed bytes (`git show HEAD:<engine>`) are written here and every player this build writes is
    instantiated against them - the beat is the engine as it stands in the record, nothing else."""
    import hashlib
    import render_baseline as RB
    PINNED.parent.mkdir(exist_ok=True)
    out = subprocess.run(["git", "show", f"HEAD:{ENGINE_SRC}"], cwd=REPO, capture_output=True, check=True).stdout
    PINNED.write_bytes(out)
    RB.ENGINE = PINNED
    _write_split = RB.write_split
    RB.write_split = lambda bd, tl, uris, name, template=RB.TEMPLATE, engine=PINNED: _write_split(
        bd, tl, uris, name, template=template, engine=engine)
    print(f"  engine      : HEAD:{ENGINE_SRC} sha256 {hashlib.sha256(out).hexdigest()[:16]} ({len(out)} bytes) - the committed engine, not the working tree's")
    return PINNED


# ---- the window of the take this beat is cut from ------------------------------------------------
def take_window() -> tuple[float, float, list[dict]]:
    full = json.loads(WORDS_SRC.read_text(encoding="utf-8"))
    full = full["words"] if isinstance(full, dict) else full
    t0 = W.cut_before(full, PLANT, rule="gap")          # the approved cut's own placement rule (M13, the P52 T11 pin)
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


# ---- the rows -------------------------------------------------------------------------------------
# The stage boxes are READ off the rendered stage (the plate is cover-fitted 768x1376 -> 1080x1920, so
# a plate pixel is not a stage fraction); trace_tie.py prints both and this file keeps the numbers.
TIES_BAND = {"kind": "region", "x0": 0.055, "y0": 0.345, "x1": 0.905, "y1": 0.500}   # the bench: the three men and their ties
CROWD_BAND = {"kind": "region", "x0": 0.020, "y0": 0.715, "x1": 0.980, "y1": 0.985}  # the phones below - "sixty-three stick figures"


def last_index() -> int:
    pts = json.loads((BUILD / "evidence/objects" / f"{SERIES}.series.json").read_text(encoding="utf-8"))["series"][0]["pts"]
    return len(pts) - 1


def shot_table(ws: list[dict], runtime_s: float) -> list[tuple]:
    at = lambda phrase: W.at(ws, phrase)                                  # noqa: E731
    t_cut = W.cut_before(ws, TURN, rule="gap")
    page = f"ledger:{SERIES}:line:{last_index()}:right:morph:cut"         # enter=morph; :cut - the page does not retract at the end
    return [
        # 1 THE PLANT. The panel plate is the world, alive on its idle (E49 `live` = breath + drift), and the
        #   light is the picture's focus (E56): it lands on the three men as the sentence names them, and again
        #   on the crowd below when the sentence turns to it.
        (0.0, t_cut, f"{PLATE_ID};idle=live", (0, 0, 0), [], None, [
            {"kind": "spotlight", "at": at("Three men in blue ties"), "dur": "hold", "target": TIES_BAND},
            {"kind": "spotlight", "at": at("sixty-three stick figures"), "dur": "hold", "target": CROWD_BAND},
        ]),
        # 2 THE MORPH. The page takes the world on the turn to the Treasury's table and arrives by MORPH: its
        #   prop outline is the LEFT panelist's tie, traced off this build's own last plate frame
        #   (world.morph.poly, injected below from planted-tie.poly.json). The ground soaks out from the tie
        #   (E99 s52 / T3b) and the line builds along the top of the area the tie became.
        (t_cut, round(runtime_s, 2), page, (0, 0, 0), [], None, [
            # ... and the chart answers the sentence it was cut to: the ring lands on the LAST datum as the
            #     narration says "February." - a point on a chart, E56's own use, after the build has landed
            #     (M11: never over the build).
            {"kind": "callout", "at": at("February."), "dur": 1.4, "target": {"kind": "datum", "index": last_index()}},
        ]),
    ]


# ---- the planted source, injected into the compiled timeline ---------------------------------------
def inject_poly() -> bool:
    """`world.morph = {poly: [...]}` on the page's scene - the planted element's OWN traced silhouette
    (P48 T5b / R26-16). The compiler's own refusals are run over it before the player is rewritten."""
    if not POLY_FILE.exists():
        print("  morph       : no planted-tie.poly.json yet - pass 1 (run trace_tie.py, then build again)")
        return False
    import build_scene_timeline_f as C
    import render_baseline as RB
    poly = json.loads(POLY_FILE.read_text(encoding="utf-8"))["poly"]
    tl = json.loads((BUILD / TIMELINE_NAME).read_text(encoding="utf-8"))
    sc = next(s for s in tl["scenes"] if (s.get("world") or {}).get("kind") == "ledger")
    sc["world"]["morph"] = {"poly": poly}
    err = C.morph_source_error(sc["world"], f"{sc['scene_id']}: world.morph")
    if err:
        raise SystemExit(err)
    uris = json.loads((BUILD / RB.ASSETS_NAME).read_text(encoding="utf-8"))
    RB.write_split(BUILD, tl, uris, TIMELINE_NAME)
    print(f"  morph       : world.morph.poly on {sc['scene_id']} - {len(poly)} traced points (planted-tie.poly.json)")
    return True


def main() -> int:
    pin_engine()
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
    D.register(PLATE_ID, PLATE_SRC)
    (BUILD / "evidence-dock.json").write_text("[]\n", encoding="utf-8")
    rows = shot_table(ws, runtime_s)
    T.write_shot_table(BUILD / "SHOT-TABLE-PLANTED.py", rows,
                       '"""P61 T3d - AUTHORED shot table, timed from the take by build_planted.py. Do not hand-edit."""\n')
    T.print_rows(rows)
    rc = T.compile_timeline(
        BUILD, BUILD,
        timeline_name=TIMELINE_NAME,
        shot_table_file="SHOT-TABLE-PLANTED.py",
        title="Tokyo Tea Break", subtitle="Money Physics - P61 T3d test bed", episode_id="tokyo-tea-break",
        aspect="9:16",
        caption_style="phrase",
        kinetics={"analytic_spring": True, "min_jerk": True, "area_squash": True, "km_ink": False,
                  "curvature_stroke": True, "arap_morph": True})
    if rc:
        return rc
    inject_poly()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
