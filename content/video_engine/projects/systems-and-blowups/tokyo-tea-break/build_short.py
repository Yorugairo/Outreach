"""Tokyo Tea Break - the SHORT's build (stages 6-8 for `SCRIPT-90S-VO.claude.txt`, v11).

One take, one part (`vo-short/audio/scene_1.words.json` is the clock). The shot table is
AUTHORED here as rows the compiler (`build_scene_timeline_f.py`) already understands:

    (start, end, plate_id, ken_burns, [docks], exit, [species])

plate ids: ``clip:<mp4>`` = a silent @StickMike Omni clip as the world (the player seeks it to
the scene clock), ``ledger:<series>:<variant>:<emphasize>:<quiet_zone>`` = a LEDGER PAGE drawn
from `evidence/objects/<series>.series.json`. Cuts land at 0.8 of the >= 0.30 s gap before the
first word of the next beat (M13, from the reference) - the rows are anchored on PHRASES and
timed from the take, never typed.

    python build_short.py            # builds build-short/ and runs the motion gate
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
SCRIPTS = REPO / "content/video_engine/scripts"
sys.path.insert(0, str(SCRIPTS))

SCRIPT = HERE / "SCRIPT-90S-VO.claude.txt"
TAKE = HERE / "vo-short/audio"
BUILD = HERE / "build-short"
CLIPS = HERE / "omni-video/stills"   # the v2 set: approved stills to video (APPROVALS.json)
SERIES = ("ev-japan-holdings-v1", "ev-meta-yield-v1")
CUT_AT = 0.8          # M13: the cut sits at 0.8 of the gap before the next phrase
MIN_GAP = 0.30        # M13: a gap shorter than this is not a cut point

# the holdings series since 2000 (316 monthly points): the February-2026 high the script calls the peak, and the latest
def _holdings_indices() -> tuple[int, int]:
    j = json.loads((HERE / "evidence/ev-japan-holdings-v1.series.json").read_text(encoding="utf-8"))
    pts = j["series"][0]["pts"]
    peak_x = round(2026 + 1 / 12, 4)
    peak = min(range(len(pts)), key=lambda i: abs(pts[i][0] - peak_x))
    return peak, len(pts) - 1


PEAK_IDX, LAST_IDX = _holdings_indices()


def words() -> list[dict]:
    """The take's words (start_s / end_s)."""
    d = json.loads((TAKE / "scene_1.words.json").read_text(encoding="utf-8"))
    return d["words"] if isinstance(d, dict) else d


def shifted_words() -> list[dict]:
    """The words AFTER the edit pauses (build-short/timeline.json, start / end) in the take's shape."""
    tl = json.loads((BUILD / "timeline.json").read_text(encoding="utf-8"))
    return [{"w": w["w"], "start_s": w["start"], "end_s": w["end"]} for w in tl["words"]]


def phrase_start(ws: list[dict], phrase: str) -> tuple[int, float]:
    """Index and start time of the word that opens `phrase` (punctuation-insensitive)."""
    norm = lambda s: s.strip(".,:;!?\"'").lower()
    toks = [norm(x) for x in phrase.split()]
    for i in range(len(ws) - len(toks) + 1):
        if [norm(x["w"]) for x in ws[i:i + len(toks)]] == toks:
            return i, ws[i]["start_s"]
    raise SystemExit(f"phrase not in the take: {phrase!r}")


def cut_before(ws: list[dict], phrase: str) -> float:
    """The cut time before `phrase`: 0.8 of the gap after the previous word (M13)."""
    i, start = phrase_start(ws, phrase)
    if i == 0:
        return 0.0
    prev_end = ws[i - 1]["end_s"]
    gap = start - prev_end
    if gap < MIN_GAP:
        raise SystemExit(f"no cut point before {phrase!r}: gap {gap:.2f}s < {MIN_GAP}s (M13)")
    return round(prev_end + CUT_AT * gap, 2)


def word_time(ws: list[dict], phrase: str) -> float:
    return phrase_start(ws, phrase)[1]


def write_timeline(ws: list[dict], runtime_s: float) -> dict:
    """`timeline.json` in the shape the caption-page builder and the compiler read (one part)."""
    out_words = [{"w": w["w"], "start": round(w["start_s"], 3), "end": round(w["end_s"], 3), "part": 1} for w in ws]
    sents, cur = [], []
    for w in out_words:
        cur.append(w)
        if w["w"].rstrip('"”').endswith((".", "!", "?", ":")):
            sents.append({"text": " ".join(x["w"] for x in cur), "start": cur[0]["start"], "end": cur[-1]["end"], "part": 1})
            cur = []
    if cur:
        sents.append({"text": " ".join(x["w"] for x in cur), "start": cur[0]["start"], "end": cur[-1]["end"], "part": 1})
    tl = {"episode": "tokyo-tea-break", "script": SCRIPT.name, "take": "vo-short", "runtime_s": runtime_s,
          "words": out_words, "sentences": sents, "edit_pauses_applied": False}
    (BUILD / "timeline.json").write_text(json.dumps(tl, indent=1), encoding="utf-8")
    return tl


KEYFRAME_EVERY = 12   # frames (0.5 s at 24 fps): a seek decodes at most half a second, not the whole clip


# THE OUTRO (operator, 2026-09-05: "we have the outro built already, same as we used for the first reel - the remotion kit outro"):
# the Remotion kit lives in content/video_engine/remotion-kit/ (rescued from a session scratchpad); its render is appended
# after the last word - the card DISSOLVES in over the ring clip (which keeps playing underneath), the audio is padded to the new runtime
OUTRO = HERE / "outro/outro-v2.mov"   # 6.2 s, 1080x1920 ProRes, the DARK starfield the operator showed (2026-09-05): "It's not magic. It's mechanics." / "follow for the next teardown" / @MoneyPhysicsHQ; outro-brand is the cream re-skin, outro-yt the "subscribe" variant
# THE BRAND LINE (operator, 2026-09-05: 'might as well record it ... so we only ever have to record it once'): one ElevenLabs pickup,
# "Not a panic. Not a plot. Mechanics.", a CHANNEL asset (channel-assets/money-physics/outro/vo, 2.3 s, request VWz6F5nZII19oUXxsUYt),
# stitched BRAND_GAP after the last word so it plays under the card; the card's own text is its caption (no caption page)
BRAND_LINE = HERE.parents[2] / "channel-assets/money-physics/outro/vo/audio/brand-line-paced.mp3"   # the PACED cut (pace_brand_line.py): periods, then a savor before "Mechanics." (operator: "it reads too fast")
BRAND_GAP, BRAND_TAIL = 0.7, 1.0
OUTRO_S, OUTRO_LEAD = 6.2, 0.1   # the card's fade begins a tenth before the last word ends and DISSOLVES in (M16: the last caption pops 2.52 s before the VO ends) (operator, 2026-09-05: the wipe into a title card was 'madness')


# THE PRESS PACK (operator, 2026-09-05: "press camera clicking noises for all of the people with their phones out starting at 0:09"):
# four CC0 shutters (sound/SOURCES.md) composed into a seeded pack the length of the panel clip - clusters of two or three
# clicks, a cluster every ~1-1.6 s, the sample and its level varied per click; A dense, B sparse. One cue at the panel.
SHUTTERS = ["fs-shutter-pentax-337229.mp3", "fs-shutter-manual-521854.mp3", "fs-shutter-sony-249750.mp3", "fs-shutter-dslr-539136.mp3"]


def press_pack(window_s: float, out: Path, clusters: int, seed: int) -> Path:
    """A window of press clicks, seeded, written to out (peak -1 dBFS, then the cue gain sits it under the voice)."""
    import random
    import subprocess
    rnd = random.Random(seed)
    clicks, t = [], 0.15 + rnd.random() * 0.4
    for _ in range(clusters):
        if t > window_s - 0.6:
            break
        for k in range(rnd.choice((2, 2, 3))):
            clicks.append((round(t + k * (0.12 + rnd.random() * 0.16), 3), rnd.choice(SHUTTERS), round(0.55 + rnd.random() * 0.45, 2)))
        t += 0.9 + rnd.random() * 0.7
    inputs, parts = [], []
    for i, (at, f, g) in enumerate(clicks):
        inputs += ["-i", str(HERE / "sound" / f)]
        parts.append(f"[{i}:a]aresample=44100,aformat=channel_layouts=mono,volume={g},adelay={int(at * 1000)}|{int(at * 1000)}[c{i}]")
    fc = ";".join(parts) + ";" + "".join(f"[c{i}]" for i in range(len(clicks))) + f"amix=inputs={len(clicks)}:normalize=0,atrim=0:{window_s:.3f},alimiter=limit=0.891[out]"
    subprocess.run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", fc, "-map", "[out]", "-c:a", "libmp3lame", "-q:a", "2", str(out)], check=True)
    return out


# THE BEDS (sub-threshold music, docs/research/audio/SUBTHRESHOLD_BACKGROUND_MUSIC_RESEARCH_BLUEPRINT.md s2, calibrated by ear
# 2026-09-01; operator, 2026-09-05: "-28 LU is youtube, -26 is facebook"): gain = 10^((VO_I - LU - bed_I) / 20). The ep1 Suno beds
# reused (SOURCES.md); the hook bed from 0:00, the turn bed fading in under it at 0:40 and running to the end (continuity, s5).
BED_LU = {"youtube": -28.0, "facebook": -26.0}
PLATFORM = "youtube"
VO_LUFS = -17.9   # vo-short/audio/scene_1.mp3, measured 2026-09-05
BEDS = {"suno-hook-A.mp3": -13.2, "suno-hook-B.mp3": -13.0, "suno-pivot-A.mp3": -13.0, "suno-pivot-B.mp3": -13.0}   # the copies in sound/, matched to -14 then limited at -1 dBFS: MEASURED integrated LUFS (SOURCES.md), so one gain fits both variants
bed_gain = lambda f: round(10 ** ((VO_LUFS + BED_LU[PLATFORM] - BEDS[f]) / 20), 4)


def seekable_clip(name: str, src: Path | None = None) -> Path:
    """The Flow clip re-encoded with a keyframe every KEYFRAME_EVERY frames (the originals carry ONE keyframe in 240,
    so every seek decoded from frame 0 and live playback fell behind and held - operator, 2026-09-05). Same
    frames, same length; written once into build-short/clips/ and reused while the source is unchanged."""
    import subprocess
    src, out = (src or CLIPS / name), BUILD / "clips" / name
    out.parent.mkdir(parents=True, exist_ok=True)
    if not out.exists() or out.stat().st_mtime < src.stat().st_mtime:
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(src), "-an", "-c:v", "libx264", "-profile:v", "high", "-crf", "17", "-preset", "slow",
                        "-g", str(KEYFRAME_EVERY), "-keyint_min", str(KEYFRAME_EVERY), "-sc_threshold", "0", "-bf", "0", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(out)], check=True)
    return out


# THE DOCKS (E44 / operator, 2026-09-06: "use the chart plate/ledger AND THEN DOCK the animation videos"): under v2 the page
# is the constant and the clips arrive OVER it. The VIDEO DOCK shipped 2026-09-06 (c0c6a17: a clip docks as a <video> on the
# scene clock, sharing the world clip's seek; the motion gate credits a live video dock as motion). A dock asset that resolves
# to an .mp4 becomes a video dock in the compiler (`build_scene_timeline_f.is_video_asset`), so the build registers the CLIP
# itself. The crop columns below are kept for the still fallback (`--still-docks`), which was v2's first build before the
# video dock existed: a 9:16 solo card is 800px wide at top 553 inside the mobile safe box y[280,1340] (doc 49 s49.1).
DOCK_STILLS = {                     # dock asset id -> (source clip, crop height, crop y) on the clips' own 720x1280
    "dock-c-blue-ties-panel":   ("clip-c-blue-ties-panel-v2.mp4", 540, 380),   # the panel, the desk, the boy on his phone
    "dock-a2-counter-colder":   ("clip-a2-counter-colder-v2.mp4", 660, 240),   # the host at the counter, the two cups
    "dock-g-two-fingers":       ("clip-g-two-fingers-v2.mp4", 660, 200),       # both hands, the two fingers up
    "dock-f-toll-gate-to-fab":  ("clip-f-toll-gate-to-fab-v2.mp4", 620, 190),  # the open gate, the road, the fab
}


STILL_DOCKS = "--still-docks" in sys.argv   # the pre-video-dock fallback: dock each clip's first frame instead


def dock_still(aid: str) -> str:
    """Register the dock asset with the resolver (`build_render_f.find_asset` checks STAMPED first, build_render_f.py:49).
    Default: the CLIP itself, so the compiler makes a VIDEO dock (E44 / R26-7, video dock c0c6a17). With `--still-docks`:
    the clip's first frame cropped to the card, written to build-short/docks/ - v2's first build, kept as the fallback."""
    import subprocess
    import build_render_f as R
    name, h, y = DOCK_STILLS[aid]
    src = CLIPS / name
    if not STILL_DOCKS:
        R.STAMPED[aid] = str(src)
        return aid
    out = BUILD / "docks" / f"{aid}.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    if not out.exists() or out.stat().st_mtime < src.stat().st_mtime:
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(src), "-frames:v", "1",
                        "-vf", f"crop=720:{h}:0:{y}", str(out)], check=True)
    R.STAMPED[aid] = str(out)
    return aid


# the docked stills' evidence cards. species "deck": these are the channel's own drawn stills and never a chart, so the
# opening-minute chart gates (M11 first chart, M12 chart hold) must not read one as the chart. No badges: ruling B3 - a badge
# numeral must appear verbatim in the document behind it, and a drawn still carries no numerals.
DOCK_META = [
    {"asset": "dock-c-blue-ties-panel", "title": "Three men in blue ties", "source": "@StickMike · Money Physics", "species": "deck", "badges": []},
    {"asset": "dock-a2-counter-colder", "title": "The host at the counter", "source": "@StickMike · Money Physics", "species": "deck", "badges": []},
    {"asset": "dock-g-two-fingers", "title": "Two numbers", "source": "@StickMike · Money Physics", "species": "deck", "badges": []},
    {"asset": "dock-f-toll-gate-to-fab", "title": "The gate to the fab", "source": "@StickMike · Money Physics", "species": "deck", "badges": []},
]

# the LEDGER PAGE's own clock, mirrored from the player's `const LP` (template :1724) exactly as the motion gate mirrors it:
# ROLL .7 + SAVOR .8 + FIELD 2.4 + PUNCH .5 + BUILD 3.0. The chart LANDS at 7.4s after the page enters and the focus action
# fires there - no highlight over the charcoal build (operator, 2026-09-04). A page cannot land a callout sooner than this.
PAGE_BUILD_END_S = 7.4
MOUNT_SKIP_S = 1.5   # ROLL 0.7 + SAVOR 0.8: a MOUNTED page (E45 s2) skips both, so its chart lands at mount end + (7.4 - 1.5)


def shot_table(ws: list[dict], runtime_s: float, t_outro: float | None = None) -> list[tuple]:
    """The authored rows, timed from the take. V2 (E44, operator 2026-09-06 on SHOT-TABLE-V2-PROPOSAL.md): the
    holdings page ROLLS OUT ON THE HOOK and stays; the clips stop being scenes and arrive as DOCKS over it; the ring
    returns the page unwound and the host mounts on the last line. Clip b (dial and bill) has no slot in this cut."""
    clip = lambda name, src=None: f"clip:{seekable_clip(name, src).as_posix()}"
    t_outro = t_outro if t_outro is not None else runtime_s
    hold = f"ledger:ev-japan-holdings-v1:line:{LAST_IDX}:right"
    at = lambda phrase: round(word_time(ws, phrase), 2)
    datum = lambda i: {"kind": "datum", "index": i}
    # V2 anchors. A dock MOUNTS on a word (s9.15: a mount is a dissolve on a word), so these are word times, not cut
    # points; only the world changes that are still cuts (the promise plate, the catalyst, the ring) take cut_before.
    t_page = at("unfunded")                              # the page's own clock starts on "unfunded" (E44: the chart flexes on the hook)
    t_mount = at("left America")                         # E45 s2: the page MOUNTS over the host - the bar fades above while the cream builds beneath
    mount_hook = round(t_page - t_mount, 2)              #   from "left America" to "unfunded"; the page's clock then runs from t_page as before
    t_panel = at("Three men in blue ties")               # the panel docks on "Three"
    t_sixty = at("sixty-three stick figures")            # ... and swaps to the host on the joke
    t_watch = at("watching")                             # ... and retracts on "watching", leaving the page bare for the datum
    t_lender = at("our biggest lender")
    t_trillion = at("over a trillion")
    t_two = at("Two numbers")
    t_promise = cut_before(ws, "a Treasury page")        # the cut drops on "went:" (operator, 2026-09-05): the promise plate
    t_catalyst = cut_before(ws, "Since February, Japan")
    t_pledge = at("pledged")                             # the gate docks on "pledged"
    t_cut = cut_before(ws, "So, the second number")      # the cream is full here and the Meta chart starts drawing
    t_second = at("went home")                           # the Meta page's mount begins under the holdings page
    t_ring = cut_before(ws, "The Fed still hasn't moved")
    t_relit = at("that unfunded")                        # the second "unfunded bar tab" - the callout is re-lit on it
    t_ours = at("still ours")                            # the host mounts here as the last image before the card
    meta = f"ledger:ev-meta-yield-v1:bars:3:right:mount={round(t_cut - t_second, 2)}:cut"   # as v1; the world it mounts over is now the page
    return [
        # 1 the hook: the counter, the steaming cup, the tab - as v1, ending where the page rolls out
        (0.0, t_mount, clip("clip-a-counter-tab-v2.mp4"), (0, 0, 0), [], None, None),
        # 2 THE PAGE ON THE HOOK (E44) and everything over it. The holdings page rolls out on "unfunded" and holds for 36s:
        #   the panel, the host and the two fingers arrive as DOCKS (operator, 2026-09-06) instead of taking the frame.
        #   exit=cut: the page never retracts here - it is SUCKED into the promise plate (row 3), and a live dock must not
        #   ride a page's exit (E40 #5). The callout cannot land on "climbed anyway" (8.0): the page's own build lands at
        #   t_page + 7.4 and the operator's ruling is no highlight over the charcoal build - so the -$122.6B lands there.
        (t_mount, t_promise, hold + f":mount={mount_hook}:cut", (0, 0, 0), [   # E45 s2: the mount, not a cut into the roll-out
            (dock_still("dock-c-blue-ties-panel"), 0, t_panel, t_sixty),
            (dock_still("dock-a2-counter-colder"), 0, t_sixty, t_watch),
            (dock_still("dock-g-two-fingers"), 0, t_two, t_promise),
        ], "cut", [
            {"kind": "callout", "at": round(t_page + PAGE_BUILD_END_S - MOUNT_SKIP_S + 0.1, 2), "dur": 2.0, "target": datum(LAST_IDX)},   # -$122.6B, at the build's landing
            {"kind": "spotlight", "at": t_lender, "dur": 2.0, "target": datum(LAST_IDX)},                                  # the June datum on "our biggest lender"
            {"kind": "callout", "at": t_trillion, "dur": 2.0, "target": datum(PEAK_IDX)},                                  # the February peak on "over a trillion"
        ]),
        # 3 the PROMISE plate: the viewer's desk, entered by SUCK - the page collapses into the black of the stick figure
        #   (operator, 2026-09-05). Unchanged from v1 except that what gets sucked away is now the page, not a clip.
        (t_promise, t_catalyst, "plate-p-viewers-desk", (0, 0, 0), [], "suck:0.49,0.55", [
            {"kind": "steam", "at": t_promise, "dur": round(t_catalyst - t_promise, 2), "target": {"kind": "region", "x0": 0.80, "y0": 0.55, "x1": 0.95, "y1": 0.60}},
            {"kind": "trace", "at": t_promise + 0.3, "dur": round(t_catalyst - t_promise - 0.3, 2), "target": {"kind": "region", "x0": 0.117, "y0": 0.39, "x1": 0.26, "y1": 0.485}},
            {"kind": "ticker", "at": t_promise + 0.2, "dur": round(t_catalyst - t_promise - 0.2, 2), "density": 0.3, "paper": "#EFE8D5", "tilt": -4,
             "col_lines": [0.602, 0.681, 0.750, 0.812], "row_lines": [0.409, 0.431, 0.454, 0.477, 0.501, 0.525, 0.548],
             "target": {"kind": "region", "x0": 0.602, "y0": 0.409, "x1": 0.812, "y1": 0.548}},
        ]),
        # 4 catalyst + the pledge: the page RETURNS by the spiral (it unwinds from its point, never drawn like new - E40 s4)
        #   and STAYS through the pledge, which docks the gate instead of cutting to it. exit=cut: the Meta page MOUNTS over
        #   this one at "went home", so there is no retract to double it, and the gate card does not ride one (E40 #5).
        (t_catalyst, t_second, hold + ":spiral:cut", (0, 0, 0), [
            (dock_still("dock-f-toll-gate-to-fab"), 0, t_pledge, t_second),
        ], "cut", [
            {"kind": "punch", "at": at("Since February, Japan"), "dur": 0.9, "target": datum(PEAK_IDX)},
            {"kind": "callout", "at": at("a tenth of"), "dur": 2.0, "target": datum(LAST_IDX)},
        ]),
        # 5 the second number: a Meta share priced at each yield, punch on the 5.5 % bar at "discounts" - as v1
        (t_second, t_ring, meta, (0, 0, 0), [], None, [
            {"kind": "callout", "at": at("price-to-earnings multiple"), "dur": 2.0, "target": datum(0)},
            {"kind": "punch", "at": at("discounts it."), "dur": 0.9, "target": datum(3)},
        ]),
        # 6 THE RING on the mechanism, not the phrase (G15b): the holdings page returns UNWOUND on "The Fed still hasn't
        #   moved" with the drop already drawn, and the -$122.6B is re-lit on the second "unfunded bar tab". exit=cut
        #   because the callout would otherwise ride the retract (M15 / E40 #5) and because the host mounts on top of it.
        (t_ring, t_ours, hold + ":spiral:cut", (0, 0, 0), [], "cut", [
            {"kind": "callout", "at": t_relit, "dur": 2.0, "target": datum(LAST_IDX)},
        ]),
        # 7 the host, mounted on "still ours" (s9.15: a mount is a dissolve on a word) - the last image before the card
        (t_ours, t_outro, clip("clip-a2-counter-colder-v2.mp4"), (0, 0, 0), [], "dissolve", None),
        # 8 the outro: the Remotion kit's card dissolving in over the ring clip; `life` so the pulse gate credits its drift
        (t_outro, runtime_s, clip("outro-v2.mp4", OUTRO), (0, 0, 0), [], "dissolve", [
            {"kind": "life", "at": t_outro, "dur": round(runtime_s - t_outro, 2)},
        ]),
    ]


def main() -> int:
    ws = words()
    BUILD.mkdir(exist_ok=True)
    (BUILD / "audio").mkdir(exist_ok=True)
    shutil.copy2(TAKE / "scene_1.mp3", BUILD / "audio/episode.mp3")
    import subprocess
    runtime_s = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                      str(BUILD / "audio/episode.mp3")], capture_output=True, text=True).stdout or 0)
    write_timeline(ws, runtime_s)
    # the OWED room at the four cut points (doc 37: silence over the settle lives in the editor's timeline)
    import insert_edit_pauses as IP
    IP.EP, IP.BUILD, IP.PLAN_FILE = HERE, BUILD, HERE / "SCRIPT-90S-VO.claude-EDIT-PAUSES.json"
    sys.argv = [sys.argv[0], "--skip-tighten-check"]      # the take is raw on purpose: the gaps are the cut points
    if IP.main() != 0:
        raise SystemExit("edit pauses failed")
    ws = shifted_words()
    tl_built = json.loads((BUILD / "timeline.json").read_text(encoding="utf-8"))
    runtime_s = tl_built["runtime_s"]
    # the outro extends the runtime past the VO: pad the (paused) audio with silence so the player plays to the end
    t_vo_end = runtime_s
    t_outro = round(t_vo_end - OUTRO_LEAD, 3)
    line_s = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(BRAND_LINE)], capture_output=True, text=True).stdout or 0)
    t_line = round(t_vo_end + BRAND_GAP, 3)
    runtime_s = round(max(t_outro + OUTRO_S, t_line + line_s + BRAND_TAIL), 3)
    audio = BUILD / tl_built.get("paused_audio", "audio/episode.mp3")
    stitched = audio.with_name(audio.stem + "-stitched.mp3")
    # the take, BRAND_GAP of silence, the brand line, then silence to the runtime - one stream, the take's own sample rate
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(audio), "-f", "lavfi", "-t", str(BRAND_GAP), "-i", "anullsrc=r=44100:cl=mono", "-i", str(BRAND_LINE),
                    "-filter_complex", f"[0:a]aresample=44100,aformat=channel_layouts=mono[a];[1:a]aresample=44100,aformat=channel_layouts=mono[g];[2:a]aresample=44100,aformat=channel_layouts=mono[l];[a][g][l]concat=n=3:v=0:a=1,apad=whole_dur={runtime_s}[out]",
                    "-map", "[out]", "-c:a", "libmp3lame", "-q:a", "2", str(stitched)], check=True)
    stitched.replace(audio)
    print(f"  brand line  : {line_s:.2f}s at {t_line:.2f}s (gap {BRAND_GAP}s after the last word); card at {t_outro:.2f}s; runtime {runtime_s:.2f}s")
    tl_built["runtime_s"] = runtime_s
    (BUILD / "timeline.json").write_text(json.dumps(tl_built, indent=1), encoding="utf-8")
    # v2: the short DOES dock - the clips arrive over the page as stills (E44 / operator, 2026-09-06). The cards carry an
    # authored title, source and species; the pages are still the proof.
    (BUILD / "evidence-dock.json").write_text(json.dumps(DOCK_META, indent=1), encoding="utf-8")
    (HERE / "evidence/objects").mkdir(exist_ok=True)
    for s in SERIES:
        shutil.copy2(HERE / "evidence" / f"{s}.series.json", HERE / "evidence/objects" / f"{s}.series.json")

    import build_caption_pages as CP
    CP.BUILD = BUILD
    CP.CHAR_BUDGET, CP.MAX_WORDS = 28, 6   # a page holds a phrase of 3-6 words on TWO lines at most: the portrait strip is 800 px at 64 px type = 25-28 chars a line; measured 2026-09-05 - 46 chars / 7 words wrapped half the pages to 3-5 lines
    CP.main()

    rows = shot_table(ws, runtime_s, t_outro)
    # the page-enter cue (M11: a sound hit within 1.5 s of the first chart): the page roll-out foley at
    # every ledger entry, on the episode clock, beside the page-relative page_cues (P35 T9)
    plan_path = HERE / "sound/SOUND-PLAN.json"
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    # THE SOUND MAP (operator, 2026-09-05, second pass: "page retract 4 and page enter 9 are the only sound effects i hear"):
    # fs-whoosh-2 is -26.9 LUFS, 13 dB under every other file - every cue on it was inaudible. The VO is -17.9 LUFS; each accent
    # sits 1-4 LU under it. The map: a roll-in page enters on the page-roll at a fifth (the "tear", 80% quieter - earlier ruling);
    # a MOUNT entry has no page turn at all; a page that leaves by the drain: a LIGHT FLIP (whoosh-1, the short swish) if it will
    # come back, a WHIRL (whoosh-4, the long sweep, timed to end on the cut) if it arrived by spiral; a spiral IN is a WHOOSH
    # (whoosh-3); the SUCK is the tear (the page-roll - "if there's not a good one, the tear actually makes some sense")
    # THIRD PASS (operator, 2026-09-05: "that whoosh sound is too mechanical, it sounds like a jet almost, ours should sound like a
    # whirl / whirlpool / spinning / spiralling ... the sounds should still be background sounds, ~8-10 dB below"): WATER - the spiral
    # in and the drain are basin swirls, the suck is a whirlpool, the flip a quiet page turn (CC0, sound/SOURCES.md); every accent
    # file is -14 LUFS, so ACCENT = 0.22 puts it ~9 dB under the -17.9 LUFS voice. The review strip carries the alternates (B/C/D).
    ROLL, FLIP, SWIRL_IN, SWIRL_OUT, WHIRLPOOL = "fs-page-roll-464302.mp3", "fs-pageturn-484968.mp3", "fs-swirl-in-478722.mp3", "fs-swirl-out-478683.mp3", "fs-whirlpool-537920.mp3"
    SLURP, SLURP2, AIR1, AIR3, AIR4 = "fs-slurp-735164.mp3", "fs-slurp2-583716.mp3", "fs-whoosh-1-706679.mp3", "fs-whoosh-3-648729.mp3", "fs-whoosh-4-648732.mp3"
    # FOURTH PASS (operator, 2026-09-05: "page enter 7 spiral (B) is the way, and it can probably be used for suck 6 also ... stretch/warp
    # the sound to match the transition - the distortion would work in our favour"): whoosh-3 WARPED to each transition's clock by
    # sound/warp_sound.py (a time-varying resample on the min-jerk curve: pitch and speed glide together, tape-style) - accelerating
    # into the suck (0.55 s), decelerating out of the spiral (1.6 s), accelerating into the drain (2.2 s, ending on the cut)
    W_SUCK, W_SPIRAL, W_DRAIN = "fs-whoosh-3-suck.mp3", "fs-whoosh-3-spiral-in.mp3", "fs-whoosh-3-drain.mp3"
    # FIFTH PASS (E44, operator 2026-09-06 on SHOT-TABLE-V2-PROPOSAL.md): under v2 the pages are the CONSTANT and the sound
    # should not announce them - every page accent comes down from 0.22 to 0.12 (~14.5 dB under the -17.9 LUFS voice, the
    # level the operator set for the press pack on 2026-09-05), and the roll-out enter comes down from 0.18 to the same 0.12.
    ACCENT, RETRACT_S, WHIRL_S = 0.12, 2.0, 2.2   # the drain starts RETRACT_S before the row ends; the out-swirl and the drain warp run 2.2 s, timed to end on the cut
    ENTER_GAIN = 0.12                             # a roll-out page enter (was 0.18)
    cues = []
    for i, r in enumerate(rows):
        if r[2].startswith("ledger:"):
            spiral_in, mount_in, cut = ":spiral" in r[2], ":mount" in r[2], r[2].endswith(":cut")
            if spiral_in:
                cues.append({"slot": f"page enter {i + 1} (spiral)", "at": round(r[0], 2), "gain": ACCENT, "fade_in": 0.0, "variants": {"A": W_SPIRAL, "B": AIR3, "C": SWIRL_IN}})
            elif not mount_in:
                cues.append({"slot": f"page enter {i + 1}", "at": round(r[0], 2), "gain": ENTER_GAIN, "fade_in": 0.0, "variants": {"A": ROLL}})
            if not cut:
                if spiral_in:
                    cues.append({"slot": f"page retract {i + 1} (whirl)", "at": round(r[1] - WHIRL_S, 2), "gain": ACCENT, "fade_in": 0.0, "variants": {"A": SWIRL_OUT, "B": W_DRAIN, "C": AIR4}})
                else:
                    cues.append({"slot": f"page retract {i + 1} (flip)", "at": round(r[1] - RETRACT_S, 2), "gain": ACCENT, "fade_in": 0.0, "variants": {"A": FLIP, "B": AIR1}})
        elif isinstance(r[5], str) and r[5].startswith("suck"):
            cues.append({"slot": f"suck {i + 1}", "at": round(r[0], 2), "gain": ACCENT, "fade_in": 0.0, "variants": {"A": W_SUCK, "B": AIR3, "C": WHIRLPOOL, "D": ROLL}})
        if "clip-c-blue-ties-panel" in r[2]:   # the press: phones out for the whole panel clip
            win = round(r[1] - r[0], 3)
            press_pack(win, HERE / "sound/press-pack-A.mp3", clusters=12, seed=0xC1A55)
            press_pack(win, HERE / "sound/press-pack-B.mp3", clusters=6, seed=0xC1A56)
            cues.append({"slot": f"press {i + 1}", "at": round(r[0], 2), "gain": 0.16, "fade_in": 0.0, "variants": {"A": "press-pack-A.mp3", "B": "press-pack-B.mp3"},
                         "note": "the pack meters -16.6 LUFS; 0.16 puts the clicks ~14.5 dB under the voice (operator, 2026-09-05: 14-15 dB under)"})
    # the beds, sub-threshold and continuous: the hook bed from 0, the turn bed fading in under it at 0:40 to the end
    cues.append({"slot": "hook bed", "at": 0.0, "gain": bed_gain("suno-hook-B.mp3"), "fade_in": 1.5, "variants": {"A": "suno-hook-B.mp3", "B": "suno-hook-A.mp3"},
                 "note": f"{PLATFORM} {BED_LU[PLATFORM]:+.0f} LU under the VO ({VO_LUFS} LUFS); B at {bed_gain('suno-hook-A.mp3')}"})
    cues.append({"slot": "turn bed", "at": 40.0, "gain": bed_gain("suno-pivot-A.mp3"), "fade_in": 3.0, "variants": {"A": "suno-pivot-A.mp3", "B": "suno-pivot-B.mp3"},
                 "note": f"{PLATFORM} {BED_LU[PLATFORM]:+.0f} LU under the VO; B at {bed_gain('suno-pivot-B.mp3')}"})
    plan["cues"] = cues
    plan_path.write_text(json.dumps(plan, indent=1), encoding="utf-8")
    (HERE / "SHOT-TABLE-SHORT.py").write_text(
        '"""Tokyo short - AUTHORED shot table, timed from the take by build_short.py. Do not hand-edit; edit build_short.shot_table."""\n'
        "W = " + repr(rows).replace("), (", "),\n     (") + "\n", encoding="utf-8")
    for r in rows:
        print(f"  {r[0]:6.2f}-{r[1]:6.2f}  {r[2].split('/')[-1] if r[2].startswith('clip:') else r[2]}"
              + (f"  species {[s['kind'] for s in r[6]]}" if r[6] else ""))

    import build_scene_timeline_f as C
    C.EP, C.BUILD = HERE, BUILD
    C.TIMELINE_NAME = "tokyo-short.timeline.json"
    C.SHOT_TABLE_FILE = "SHOT-TABLE-SHORT.py"
    C.TITLE, C.SUBTITLE, C.EPISODE_ID = "Tokyo Tea Break", "Money Physics · short", "tokyo-tea-break"
    C.ASPECT = "9:16"
    C.CAPTION_STYLE = "phrase"   # shorts read their captions (operator, 2026-09-05): the page lands as one phrase, only k-words punctuated
    C.KINETICS = {"analytic_spring": True, "min_jerk": True,   # the timing module (FINDING-the-animation-math s2/s3): closed-form springs on the pops, minimum-jerk on the wipe and the suck
                  "area_squash": True,                        # P43 T4: the badge pops stretch along their travel from the spring's own velocity (42 s42.3)
                  "km_ink": False}                            # P43 T3: OFF (operator, 2026-09-05, after six rounds in motion: "our original applications were better, with the ink pooling/blotchiness ... turn ink off"); K-M stays for ink over ink, the soak goes to a plate reveal (BACKLOG)
    C.KINETICS["curvature_stroke"] = True                     # P43 T2: the HAND on every drawn path - the operator ruled from the side-by-side clip (2026-09-05: "curvature stroke should be on")
    return C.main()


if __name__ == "__main__":
    raise SystemExit(main())
