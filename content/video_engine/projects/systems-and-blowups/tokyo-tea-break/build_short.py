"""Tokyo Tea Break - the SHORT's build (stages 6-8 for `SCRIPT-90S-VO.claude.txt`, v11).

One take, one part (`vo-short/audio/scene_1.words.json` is the clock). The shot table is
AUTHORED here as rows the compiler (`build_scene_timeline_f.py`) already understands:

    (start, end, plate_id, ken_burns, [docks], exit, [species])

plate ids: ``clip:<mp4>`` = a silent @StickMike Omni clip as the world (the player seeks it to
the scene clock), ``ledger:<series>:<variant>:<emphasize>:<quiet_zone>`` = a LEDGER PAGE drawn
from `evidence/objects/<series>.series.json`. Cuts land at 0.8 of the >= 0.30 s gap before the
first word of the next beat (M13, from the reference) - the rows are anchored on PHRASES and
timed from the take, never typed.

P51 T0: the mechanism (the take's clock, the dock registrations, the audio stitch and bed
envelope, the hand-off) lives in `scripts/authoring/`; this file keeps THIS EPISODE'S FACTS -
its rows, its anchors, its crops, its cue files, its levels.

    python build_short.py            # builds build-short/ and runs the motion gate
"""
from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
SCRIPTS = REPO / "content/video_engine/scripts"
sys.path.insert(0, str(SCRIPTS))

from authoring import Project                                             # noqa: E402
from authoring import audio as A, docks as D, table as T, words as W      # noqa: E402
import gate_motion_density as MG                                          # noqa: E402  R26-50: the page's landing, one truth

SCRIPT = HERE / "SCRIPT-90S-VO.claude.txt"
TAKE = HERE / "vo-short/audio"
BUILD = HERE / os.environ.get("TOKYO_BUILD_DIR", "build-short")   # P48 T7: a cut under review builds beside the watched one (TOKYO_BUILD_DIR=build-short-p48 -> :8740), never over it
EP = Project(here=HERE, build=BUILD, take=TAKE, take_stem="scene_1", script_name=SCRIPT.name, episode_id="tokyo-tea-break")
EDIT_PAUSES = HERE / "SCRIPT-90S-VO.claude-EDIT-PAUSES.json"
CAMERA = os.environ.get("TOKYO_CAMERA", "1") == "1"   # the operator's watch, 2026-09-10 ("8742>8738"): the camera cut IS the cut; TOKYO_CAMERA=0 rebuilds the locked variant beside it   # P49 (the operator, 2026-09-10: "let's test out those camera changes"): the arrival on the ring + the pull toward the landings, in a build beside (build-short-cam, :8742)
CAM_ROW = {"keys": [], "attention": "landings"} if CAMERA else None   # the row's 8th element: the eye pulls toward a card as it lands (E59 #1; the dials are HG1's)
CLIPS = HERE / "omni-video/stills"   # the v2 set: approved stills to video (APPROVALS.json)
SERIES = ("ev-japan-holdings-v1", "ev-meta-yield-v1")


# the holdings series since 2000 (316 monthly points): the February-2026 high the script calls the peak, and the latest
def _holdings_indices() -> tuple[int, int]:
    j = json.loads((HERE / "evidence/ev-japan-holdings-v1.series.json").read_text(encoding="utf-8"))
    pts = j["series"][0]["pts"]
    peak_x = round(2026 + 1 / 12, 4)
    peak = min(range(len(pts)), key=lambda i: abs(pts[i][0] - peak_x))
    return peak, len(pts) - 1


PEAK_IDX, LAST_IDX = _holdings_indices()


def _holdings_window() -> list[float]:
    """P48 T7: the February-June window the row-2 rescale opens - a month's margin either side of the peak and the last print."""
    pts = json.loads((HERE / "evidence/ev-japan-holdings-v1.series.json").read_text(encoding="utf-8"))["series"][0]["pts"]
    return [round(float(pts[PEAK_IDX][0]) - 0.04, 3), round(float(pts[LAST_IDX][0]) + 0.04, 3)]


HOLDINGS_WINDOW = _holdings_window()
# P48 T7 (2026-09-10): the fab card's box beside the PARKED monthly bars - the band under the parked chart, above the source line
FAB_W, FAB_CX, FAB_CY = 0.58, 0.5, 0.55


def _holdings_facts() -> dict:
    """The object's own facts (peak, latest, the months): the figures the page writes come from here, never typed by hand."""
    return json.loads((HERE / "evidence/ev-japan-holdings-v1.series.json").read_text(encoding="utf-8"))["facts"]


def _bn(v: float) -> str:
    return f"${v:,.1f}B"


FACTS = _holdings_facts()
FED = json.loads((HERE / "evidence/objects/ev-fed-vs-yields-v1.series.json").read_text(encoding="utf-8"))   # the Fed page's object: its notes, its bracket indices
FED_NOTES = FED["notes"]
FED_MAY_IDX = max(range(len(FED["bars"])), key=lambda i: -FED["bars"][i]["value"]) if FED.get("bars") else 0   # the emphasised bar is the biggest SELLING month, never the first (a page with no bars emphasises nothing)


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
BED_LU = {"youtube": -20.0, "facebook": -20.0}   # a SHORT sits at -20 (E55, 2026-09-09; the -28 was the long-form calibration)
BED_SWELL_DB = 4.0   # the bed BREATHES +4 dB from a card's throw through its landing/snap (the bed blueprint rule 3; E55)
SNAP_S_BED = 0.45
TURN_BED_AT = 40.0   # the turn bed fades in under the hook bed here and runs to the end
PLATFORM = "youtube"
VO_LUFS = -17.9   # vo-short/audio/scene_1.mp3, measured 2026-09-05
BEDS = {"suno-hook-A.mp3": -13.2, "suno-hook-B.mp3": -13.0, "suno-pivot-A.mp3": -13.0, "suno-pivot-B.mp3": -13.0}   # the copies in sound/, matched to -14 then limited at -1 dBFS: MEASURED integrated LUFS (SOURCES.md), so one gain fits both variants
bed_gain = lambda f: A.bed_gain(VO_LUFS, BED_LU[PLATFORM], BEDS[f])


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
DOCK_CROP_W = 720                   # the clips' own frame width: a still-fallback card is the full width, cropped in height


# MEASURED off the clip's own frame (the ink rows, not by eye): the cup and saucer sit at x 440-570, its steam above at
# x 492-535, so the CUP's centre is x 505 - the crop is built around that, not around the counter's furniture
TEA_CROP = (375, 515, 260, 200)
STILL_DOCKS = "--still-docks" in sys.argv
STILLS_DIR = HERE / "omni-video/stills"
FAB_CROP = (0.22, 0.33)   # the band of the fab still: Mike with the clipboard, the wafer chamber (landscape, the toll gate's slot)
FAB_WAFER = (0.649, 0.501)   # the wafer's centre in the band (the warm disc's centroid)   # the pre-video-dock fallback: dock each clip's first frame instead


def dock_still(aid: str) -> str:
    """The dock asset: the CLIP itself, so the compiler makes a VIDEO dock (E44 / R26-7, video dock c0c6a17). With
    `--still-docks`: the clip's first frame cropped to the card - v2's first build, kept as the fallback."""
    name, h, y = DOCK_STILLS[aid]
    return D.dock_still(aid, CLIPS / name, BUILD, still=STILL_DOCKS, frame_crop=(DOCK_CROP_W, h, 0, y))


def dock_chart(aid: str, series: str, variant: str = "line", aspect: str | None = None) -> str:
    """This episode's chart card: the object beside the build, rendered at its landing (R26-19 / E50)."""
    return D.chart_card(aid, HERE / "evidence/objects" / f"{series}.series.json", BUILD, variant, aspect)


PLEDGE_QUOTE = "...at least 10 trillion yen ($65 billion) in support through fiscal 2030..."   # the Nikkei lede's claim, excerpted (both ellipses say so; the operator, 2026-09-10: "the read out can end at 'through fiscal 2030...'")
PLEDGE_HL = ("at", "least", "10", "trillion", "yen")     # the highlighter's phrase
PLEDGE_SYNC = {"10": "ten", "trillion": "trillion", "yen": "yen"}   # the stroke lands per-word on the NARRATOR's word
PLEDGE_ANCHOR = "ten trillion yen"


def record_dock(aid: str, ws: list[dict], t0: float) -> str:
    """The pledge record: a placeholder asset (a record is live type, never an image) and the META's `record` filled
    from the take's own word times."""
    D.record_asset(aid, BUILD)
    typed, hl, end = D.record_words(PLEDGE_QUOTE, t0, ws, PLEDGE_ANCHOR, PLEDGE_SYNC, PLEDGE_HL)
    D.meta_set(DOCK_META, aid, "record",
               {"hdr": ["Nikkei Asia", "12 November 2024"], "kicker": "Japan to roll out $65bn in support for chips, AI",
                "words": typed, "hl": hl, "end": end, "attr": "Mari Ishibashi, Nikkei staff writer",
                "src": "asia.nikkei.com · fetched 2026-09-10 · evidence/sources/nikkei-2024-11-12-japan-chips-ai-support.txt"})
    return aid


# the docked stills' evidence cards. species "deck": these are the channel's own drawn stills and never a chart, so the
# opening-minute chart gates (M11 first chart, M12 chart hold) must not read one as the chart. No badges: ruling B3 - a badge
# numeral must appear verbatim in the document behind it, and a drawn still carries no numerals.
DOCK_META = [
    {"asset": "dock-c-blue-ties-panel", "title": "Three men in blue ties", "source": "@StickMike · Money Physics", "species": "deck", "badges": []},
    {"asset": "dock-a2-counter-colder", "title": "The host at the counter", "source": "@StickMike · Money Physics", "species": "deck", "badges": []},
    {"asset": "dock-g-two-fingers", "title": "Two numbers", "source": "@StickMike · Money Physics", "species": "deck", "badges": []},
    {"asset": "dock-f-toll-gate-to-fab", "title": "The gate to the fab", "source": "@StickMike · Money Physics", "species": "deck", "badges": []},
    {"asset": "dock-i-fab-wafer", "title": "Ten trillion yen for chips", "source": "HollowStickMike · Money Physics", "species": "deck", "badges": []},
    # R26-19 / E50: the hook's own proof as a CHART card on the ring - species "chart", so M11/M12 read it as the chart it is
    {"asset": "dock-h-fed-vs-yields", "title": "The Fed hasn't moved. Your borrowing costs climbed anyway.", "source": "US Treasury TIC · FRED · Sep 2026", "species": "chart", "badges": []},
    # the pledge's evidence (2026-09-10): a RECORD dock - the Nikkei lede typed on paper, the highlighter on the phrase the sentence
    # claims; `record` is filled at build (record_dock) from the take's word times. Source: evidence/sources/nikkei-2024-11-12-japan-chips-ai-support.txt
    {"asset": "dock-k-pledge-record", "title": "Japan to roll out $65bn in support for chips, AI", "source": "Nikkei Asia · 12 Nov 2024", "species": "record", "badges": []},
    # the sixth watch: the cup from the opening scene, zoomed and still steaming, on "its tea break"
    {"asset": "dock-j-tea-cup", "title": "The tea, still going", "source": "@StickMike · Money Physics", "species": "deck", "badges": []},
]

# the LEDGER PAGE's own clock, mirrored from the player's `const LP` (template :1724) exactly as the motion gate mirrors it:
# ROLL .7 + SAVOR .8 + FIELD 2.4 + PUNCH .5 + BUILD 3.0. The chart LANDS at 7.4s after the page enters and the focus action
# fires there - no highlight over the charcoal build (operator, 2026-09-04). A page cannot land a callout sooner than this.
PAGE_BUILD_END_S = 7.4
PAGE_BUILD_START_S, PAGE_BUILD_S = 4.4, 3.0   # LP: ROLL .7 + SAVOR .8 + FIELD 2.4 + PUNCH .5 -> the build beat, LP.BUILD 3.0 (P47 T2's first cap rides it)
LP_ROLL_S = 0.7      # the roll-out beat; a MOUNT replaces it (E45: the mount IS the roll-out, the savor stays) and ends where the roll would have


def shot_table(ws: list[dict], runtime_s: float, t_outro: float | None = None) -> list[tuple]:
    """The authored rows, timed from the take. V2 (E44, operator 2026-09-06 on SHOT-TABLE-V2-PROPOSAL.md): the
    holdings page ROLLS OUT ON THE HOOK and stays; the clips stop being scenes and arrive as DOCKS over it; the ring
    returns the page unwound and the host mounts on the last line. Clip b (dial and bill) has no slot in this cut.
    V3 (P47 T2/T4, SHOT-TABLE-V3-PROPOSAL part B): THE PAGE PERFORMS ON A WORD - the line builds to the February peak
    only and the coral drop draws on "watching"; the title rewrites on "The opponent"; the bracket "-$122.6B / a tenth
    of the pile" draws from the peak to June on "a hundred and twenty-two billion" and stands on the ring, re-lit on the
    second "unfunded bar tab". One thing per sentence; the callouts the bracket now says are gone."""
    clip = lambda name, src=None: f"clip:{D.seekable_clip(name, src or CLIPS / name, BUILD).as_posix()}"
    t_outro = t_outro if t_outro is not None else runtime_s
    hold = f"ledger:ev-japan-holdings-v1:line:{LAST_IDX}:right"
    at = lambda phrase: W.at(ws, phrase)
    datum = lambda i: {"kind": "datum", "index": i}
    # V2 anchors. A dock MOUNTS on a word (s9.15: a mount is a dissolve on a word), so these are word times, not cut
    # points; only the world changes that are still cuts (the promise plate, the catalyst, the ring) take cut_before.
    t_page = at("unfunded")                              # the page's own clock starts on "unfunded" (E44: the chart flexes on the hook)
    t_mount = at("left America")                         # E45 s2: the page MOUNTS over the host - the bar fades above while the cream builds beneath
    mount_hook = round(t_page + LP_ROLL_S - t_mount, 2)  #   E45: the timing does not change - the fade cuts INTO the prior scene and ends where the
                                                         #   roll-out would have ended (t_page + 0.7), so the savor, the charcoal and the graph land as before
    t_panel = at("Three men in blue ties")               # the panel docks on "Three"
    t_sixty = at("sixty-three stick figures")            # ... and swaps to the host on the joke
    t_watch = at("watching")                             # ... and retracts on "watching", leaving the page bare for the datum
    t_lender = at("our biggest lender")
    t_table = at("The Treasury's table")                 # E50: the line UN-DRAWS here - the sentence turns to the treasury number
    t_trillion = at("over a trillion")                   # ... and the peak figure writes where the line was
    t_since = at("selling since February")               # ... the June figure beside it
    t_two = at("Two numbers")
    # P52 T11 PIN: the approved cut keeps M13's 0.8-of-the-gap placement (rule="gap"); TR-13's onset rule (the cut 3 frames
    # before the next word, a dip centred on it - doc 46 s46.6) is words.py's default for every build after this one. The
    # pin is what keeps this build byte-identical; lifting it is a re-cut and needs the operator's word.
    cut = lambda phrase: W.cut_before(ws, phrase, rule="gap")
    t_promise = cut("a Treasury page")                   # the cut drops on "went:" (operator, 2026-09-05): the promise plate
    t_catalyst = cut("Since February, Japan")
    t_pledge = at("pledged")                             # the gate docks on "pledged"
    t_cut = cut("So, the second number")                 # the cream is full here and the Meta chart starts drawing
    t_second = at("went home")                           # the Meta page's mount begins under the holdings page
    t_ring = cut("The Fed still hasn't moved")
    t_relit = at("that unfunded")                        # the second "unfunded bar tab" - the callout is re-lit on it
    t_ours = at("still ours")                            # the host mounts here as the last image before the card
    t_fed_still = at("The Fed still")                    # R26-19: the Fed-vs-yields CARD is thrown here ...
    word_in = lambda phrase, word: W.word_in(ws, phrase, word)
    t_moved = word_in("still hasn't moved", "moved")     # ... and SNAPS up to become the last world on the ring's "moved" (the third watch; the hook says it first)
    t_tokyo_still = at("Tokyo is still")                 # the first side note writes here ...
    t_tea = word_in("still on its tea break", "tea")     # ... the second here, and the cup docks on it
    t_bar_tab = word_in("bar tab is still ours", "bar")  # (the ring's last line)
    t_that = word_in("that unfunded bar tab is", "that")  # the host arrives CENTRED on the Fed page for its whole last line
    # V3 words (P47 T2): the page performs on these
    # R26-50 (2026-09-11): the mount is the SOAK on the page's own clock - the build beat starts mount_s + PUNCH after the
    # scene's start, not 4.4 s after t_page; the landing is the gate's one truth (_page_land_offset), so the build_to that
    # shapes the line's arrival on the peak rides the clock the gate measures (before: 7.69 on a landing of 10.69; now 4.49 / 7.49)
    t_build = round(t_mount + MG._page_land_offset({"world": {"kind": "ledger", "page": {"enter": "mount", "mount_s": mount_hook}}}) - PAGE_BUILD_S, 2)
    t_opponent = at("The opponent")                      # the title rewrites here
    t_hundred = at("a hundred and twenty-two billion")   # the bracket draws here, its sub landing on "a tenth of the pile"
    t_prints = at("The Treasury prints")                 # E50: the line and the bracket un-draw here (the last data mark is the bracket)
    t_first = at("your first number")                    # ... and the June print writes as the FIRST NUMBER
    RETITLE = "The opponent: a balance sheet"            # one line at 68 px, like the title it replaces (a second line would sit on the sub)
    carried = lambda t0: {"kind": "retitle", "at": round(t0 - 3.0, 2), "dur": 2.4, "text": RETITLE}   # a returning page ARRIVES retitled (a species before its scene is a state)
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
            # V3 second pass (P47 T1, HG2 - judged by eye): the panel is THROWN onto the page on "Three men" (a prop with a path,
            # paper), the two fingers LAND with weight on "Two numbers" (the lift, the drop, the impact, the settle); the host
            # keeps E45's spring so the three arrivals can be compared in one watch
            # HG1 (operator, 2026-09-07): "the dock at 0:16 is useless, that's the tea clip but at that point we're not talking about tea" -
            # the tea swap on "sixty-three" is gone; the panel holds parked through the joke and retracts on "watching" (part B row 4)
            (dock_still("dock-c-blue-ties-panel"), 0, t_panel, t_watch, {"arrive": "throw", "mass": "paper"}),
            # the operator, 2026-09-10 ("two numbers could probably be parked better, now that our charts are actually a living species
            # docking over them costs more because it's space we could be using"): the chart PARKS up-left on "Two numbers" (Bravos 91)
            # and the fingers land BESIDE it in the room the park frees - measured on the P48 build: the chart svg is 800x851 at (80,374),
            # parked at 0.55 it holds x 80-520, y 374-842; the card (720x660) at 0.42 of the stage sits centred at (0.76, 0.316), clear of
            # the sub above (242-342) and the parked plot, over nothing
            (dock_still("dock-g-two-fingers"), 0, t_two, t_promise, {"arrive": "land", "mass": "metal", "centre": True, "card_aspect": 0.9167, "centre_w": 0.42, "centre_x": 0.76, "centre_y": 0.316}),
        ], "cut", [
            # V3: the build stops at the FEBRUARY PEAK ("The Fed hasn't moved, but your borrowing costs climbed anyway"); the coral
            # drop is its own stroke on "watching:", so the June datum is drawn the moment the sentence turns to the lender
            {"kind": "build_to", "at": t_build, "dur": PAGE_BUILD_S, "target": datum(PEAK_IDX)},
            {"kind": "build_to", "at": t_watch, "dur": 1.2, "target": datum(LAST_IDX)},
            {"kind": "spotlight", "at": t_lender, "dur": 1.0, "target": datum(LAST_IDX)},                                  # the June datum on "our biggest lender"
            # P48 T7 (E58; the fourth watch: "we were supposed to re-draw or morph the chart to another"): on "The Treasury's table"
            # the chart CHANGES STATE instead of un-drawing - it RESCALES to the February-June window, so the sell-off the sentence is
            # about stands at full width (five of 316 points were a ~10 px stub on the 26-year axis - the beat the 09-07 note left
            # unfinished); the two treasury figures then write on the windowed line - the peak on "over a trillion", June on "selling
            # since February" - from the object's facts, and the chart un-draws on "The opponent" (E50: the rescale restarts its
            # clock at 0:22 and the title turns to the opponent at 0:30 - its life ends at the turn; on "Two numbers" M21 read 14.1 s)
            # so the figures stand alone under the retitle and the fingers land on the bare page as designed
            {"kind": "chart_to", "at": t_table, "dur": 1.4, "to": "rescale", "window": HOLDINGS_WINDOW},
            # ... and on "Two numbers" the windowed chart PARKS up-left (the fingers take the room beside it) instead of un-drawing:
            # the chart stays legible as the sentence sets the agenda (E58: park = room for the next thing; no clock restarts)
            {"kind": "chart_to", "at": round(t_two - 0.4, 2), "dur": 0.9, "to": "park", "scale": 0.55, "anchor": "top"},
            {"kind": "figure", "at": t_trillion, "dur": 1.6, "target": datum(PEAK_IDX), "text": _bn(FACTS["peak"]), "dy": -0.7},   # P48 T7: on the windowed line the months ARE the axis (Feb '26 ... Jun '26) - the figures carry no month sub (E52)
            {"kind": "figure", "at": t_since, "dur": 1.6, "target": datum(LAST_IDX), "text": _bn(FACTS["latest"]), "color": "neg", "dy": -1.0},   # P48 T7: June is the windowed plot's floor - the figure writes ABOVE its point, clear of the line's last segment (dy +1.6 put it on the axis labels)
            # THE BEAT IS UNFINISHED AND SAYS SO (2026-09-07). E50: a chart un-draws OR BECOMES THE NEXT THING. This page
            # un-draws correctly and then becomes nothing - I redrew a piece of the SAME line (`paths: "tail"`) and labelled it,
            # which is neither. It also could not read: February-June is 5 of 316 points, 1.27 % of a 26-year axis, so the
            # redraw painted a ~10 px stub; a focus_zoom (the only magnification we have) is a ~1.1x push and does not rescue
            # it. Both are removed. The honest frame is the two treasury figures standing where the line was. The beat wants a
            # DIFFERENT chart - the Feb-Jun window, or the monthly change as signed bars - and which one is the operator's
            # call; the capability is P48 (`rescale` T2 / `recast` T4).
            {"kind": "retitle", "at": t_opponent, "dur": 2.4, "text": RETITLE},                                       # the title rewrites by the hand on "The opponent"
        ], CAM_ROW),
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
        (t_catalyst, t_second, hold + ":spiral:cut;then=ev-japan-selling-v1:bars:3;then=ev-bonds-vs-chips-10y-v1:bars:1", (0, 0, 0), [   # the second state: the month-by-month bars, June emphasised
            # E55 (operator, 2026-09-09): the toll-gate clip "was already weak because it was supposed to be a toll gate, without the
            # manufacturing plant it's just useless" - the fab (Mike at the wafer chamber, the operator's own Flow plate) takes the
            # clip's own measured place as a centred card; the LIGHT lands on the wafer at "chips" and holds to the cut (E56: never a ring on a picture)
            # the card proves its sentence and leaves at the turn ("And here's what nobody says" - E50/E25); its exit is the beat M16 counts
            # the operator, 2026-09-10 (docking over a living chart costs space): the monthly bars PARK up-left on "pledged" and the fab
            # card takes the band the park frees - 626x370 at (0.5, 0.55) = y 871-1241, above the source line (1249), over nothing
            # the pledge's EVIDENCE (2026-09-10): the record types the Nikkei lede in the band under the parked bars on "pledged", the
            # highlighter landing on "at least 10 trillion yen" as the narrator says it; on "works" the band is the plant's
            # the operator (2026-09-10): "'Tokyo has pledged ten trillion yen to chips' should summon both the fab card and the quote, they both
            # fit on screen ... put the text evidence next to the chart with the fab card docked below. We pop the card first next to the
            # chart, then on 'chips' the fab card below." The record (slot 1) stands BESIDE the parked chart, top-right, from "pledged";
            # the plant (slot 0) lands in the band below on "to chips,"; both leave at the turn ("And here's"). The burst plays top-left.
            # ... then the operator again: "pop the card centered exactly as it is, and move it and resize it to that slot on the right when we
            # pop the next card" - the record POPS at the band box it had (`read`), holds until "to chips," (`read_s`), and PARKS over 0.7 s
            # to the slot beside the parked chart as the plant lands beneath; its type scales with its width (no rewrap)
            (record_dock("dock-k-pledge-record", ws, t_pledge), 1, t_pledge, at("And here's"),
             {"centre": True, "card_aspect": 1.0, "centre_w": 0.40, "centre_x": 0.77, "centre_y": 0.335,
              "read": {"centre_w": FAB_W, "centre_x": FAB_CX, "centre_y": FAB_CY - 0.015, "card_aspect": 0.47},
              "read_s": round(at("to chips") - t_pledge, 2), "park_s": 0.7}),
            (D.dock_png("dock-i-fab-wafer", STILLS_DIR / "sig-i-fab-wafer.png", FAB_CROP, BUILD), 0, at("to chips"), at("And here's"),
             {"centre": True, "card_aspect": 0.5911, "centre_w": FAB_W, "centre_x": FAB_CX, "centre_y": FAB_CY + 0.04}),   # under the parked bars (E60): the card's top clears their labels and source
            # the fourth watch: the selling bars are no evidence dock - they are the ring page's own bars, laid against its lines (combo)
        ], "cut", [
            carried(t_catalyst),
            # the LIGHT on the wafer (E56), breathing; on "works" it GLIDES out to the whole fab ("if that works" - the plant, not the
            # wafer) and holds until the card leaves; the glide is the second beat the 4.9 s hold needed (M16)
            # two lights, two beats (the gate credits a species START, not a glide inside one): the wafer on "chips" for the 0.99 s
            # to "works"; then a second light that starts on the wafer and GLIDES out to the whole fab, held until the card leaves
            {"kind": "chart_to", "at": round(t_pledge - 0.4, 2), "dur": 0.9, "to": "park", "scale": 0.52, "anchor": "top"},   # the bars make room for the plant; 0.52 (measured 2026-09-10): the ten-year bars' feet and labels clear the card's top
            # the lights follow the plant: the wafer once the card has landed (works + the landing), the glide out to the whole fab on "beats"
            # NO light on the plant (measured 2026-09-10): the spotlight darkens the whole page, and the page above the band is where
            # the burst lands on "bonds" (E60) - the bars vanished under the vignette for the whole beat. The card lands with weight
            # and holds on its idle; "beats our bonds" belongs to the breakthrough.
            # E51 (the third watch): the punch on the peak here was tied to nothing - the page returns drawn - and is cut
            # V3: the BRACKET measures the drop from the peak to June by the hand on the number; its label is the number and
            # its sub lands on "a tenth of the pile" - the callout that said the same is gone (one thing per sentence)
            {"kind": "bracket", "at": t_hundred, "dur": 2.4, "from": PEAK_IDX, "to": LAST_IDX, "label": "−$122.6B", "sub": "a tenth of the pile", "color": "neg"},
            # E50: the bracket is the page's last data mark (49.1); on "The Treasury prints" the line and the bracket un-draw and the
            # June print writes on "your first number" - THE first number the promise named; it holds under the pledge and the
            # money-went-home line (a figure is the next thing, not the chart) until the Meta page mounts over it
            # the operator, 2026-09-10 ("showing the monthly-change on the treasury prints might make sense"): on "The Treasury prints" the
            # line RECASTS into the month-by-month bars (E58: the same data in another form - the hand-over, 316 points have no bar
            # correspondence): the line leaves by length, the sub and source rewrite, the four signed bars draw (a drop goes DOWN, blood
            # red - E28); "your first number" then writes at the JUNE bar - the print the sentence names. The bracket leaves with the line.
            {"kind": "chart_to", "at": t_prints, "dur": 1.4, "to": "recast", "state": 1},
            # E60 (the operator, 2026-09-10: "It should go into Tokyo 'beats our bonds'"): on "and if that works" the parked monthly bars
            # RECAST into the ten-year bars - bonds 1.52 % a year on a stated 0-8 % scale, chips building to the bonds' level with it -
            # and the BURST lands on "bonds": the chips bar shoots to 36.59 % while the scale rewrites to 40 % under it (Bravos's move).
            # Timed from the take (measured 2026-09-10: the hold starts at the END of the state's build, not at the bars' landing): recast on
            # "to chips," 56.85-57.35, the bars at the bonds' level 58.13, the hold from 58.55 ("beats"), the shoot 59.05-59.65 ("bonds." 58.97-59.57)
            {"kind": "chart_to", "at": at("to chips"), "dur": 0.5, "to": "recast", "state": 2},
            {"kind": "retitle", "at": at("to chips"), "dur": 1.2, "text": "Ten years, a year at a time"},   # the recast rewrites the sub and source; the title is the hand's (as row 2)
            # the operator (2026-09-10: "if they're going to leave the chart should either re-take center stage, or they might as well stay
            # til the transition"): as the two cards leave on "And here's", the chart UN-PARKS - grows back to full size from the parked
            # slot - and the burst's result holds large under "what nobody says" until the Meta page mounts over it
            {"kind": "chart_to", "at": round(at("And here's") + 0.3, 2), "dur": 0.9, "to": "park", "scale": 1.0, "anchor": "top"},
            # measured on the frame: a FIGURE at the June bar (282 px of type, written leftward) crosses the May bar's body at every dy the
            # 800 px plot allows - so the print is a NOTE in the page's quiet zone (the June bar's own -$26.4 stands in its callout)
            {"kind": "note", "at": t_first, "dur": 1.4, "text": "the June print: " + _bn(FACTS["latest"]) + " - your first number"},
        ], CAM_ROW),
        # 5 the second number: a Meta share priced at each yield, punch on the 5.5 % bar at "discounts" - as v1
        # ... the Meta page HOLDS to the snap (E50: deployed 69.2 -> 76.8, 7.6 s) and the Fed CARD is thrown onto it on "The Fed still" -
        #   the holdings page does not come back for the ring ("we bring back the old chart for no reason" - the third watch)
        (t_second, t_moved, meta, (0, 0, 0), [
            (dock_chart("dock-h-fed-vs-yields", "ev-fed-vs-yields-v1", aspect="9:16"), 0, t_fed_still, t_moved, {"arrive": "throw", "mass": "paper"}),
        ], None, [
            {"kind": "callout", "at": at("price-to-earnings multiple"), "dur": 2.0, "target": datum(0)},
            # E51 (the third watch, "the weak push-in at 1:14"): the punch on the 5.5 % bar at "discounts" zoomed on a bar that had landed
            # five seconds earlier - filler - and is cut
        ]),
        # 6 THE RING on the mechanism, not the phrase (G15b): the holdings page returns UNWOUND on "The Fed still hasn't
        #   moved" with the drop already drawn, and the -$122.6B is re-lit on the second "unfunded bar tab". exit=cut
        #   because the callout would otherwise ride the retract (M15 / E40 #5) and because the host mounts on top of it.
        # 6 THE RING (the third watch, operator 2026-09-07: "'The Fed hasn't moved. Your borrowing costs climbed anyway.' is the ring, and
        #   it's also the wrapping words. We should throw it, then immediately zoom/snap to it to bring it to the full world-stage, and
        #   that's the last scene that we land - center dock then retract the 'bar tab is still ours' video scene on that chart page").
        #   the Fed-vs-yields CARD (R26-19 - the hook's own proof, FRED, proof lines in the object; a PORTRAIT card, the page it will
        #   become) is THROWN onto the Meta page above on "The Fed still" ...
        #   6b: on "moved" the card SNAPS up to the full stage and IS the last world - the Fed page, arrived built (E51: a push tied to
        #   a landing); its side notes write as the ring is spoken (from the object's facts); the host arrives CENTRED on it for
        #   "and that unfunded bar tab is still ours" and retracts before the dip to the card.
        (t_moved, t_outro, f"ledger:ev-fed-vs-yields-v1:line:{FED_MAY_IDX}:right:{'camera' if CAMERA else 'snap'}=dock-h-fed-vs-yields:cut", (0, 0, 0), [   # P49 T5: with TOKYO_CAMERA=1 the eye goes to the thrown card on "moved" instead of the card growing
            # the sixth watch (operator: "get rid of the host and just dock a small, centered image of the cup of tea on 'its
            # tea break' that doesn't interfere with graph ... I wonder if we could even just zoom the video on it and play the
            # steaming tea cup"): the opening scene's own cup, zoomed out of that footage so the steam keeps moving, small and
            # centred in the page's free space. The host is gone from this page - it was parking over the title.
            (D.dock_zoom("dock-j-tea-cup", CLIPS / "clip-a-counter-tab-v2.mp4", TEA_CROP, BUILD), 0, t_tea, t_outro - 0.3, {"centre": True, "centre_w": 0.20, "centre_x": 0.34, "centre_y": 0.353}),   # the plot's own empty upper-left, under the % label and above the line's low start   # the gap between the source line and the caption: clear of the graph, the notes and the words
        ], "cut", [   # the SNAP is this row's own transition (no dip into it); the outro row still dips
            # the three notes write in the quiet zone over "Tokyo is still on its tea break", staggered, before the host lands over the page
            # the fourth watch: the bracket on this page drew a naked vertical span at the plot's edge - its label had no room in the
            # gutter the terminal tags now own - and read as an artifact. The +80 bp is in the notes below, in words, instead.
            # the fifth watch (operator: "bleed the chart fill to red beneath the 10 year line and the fed rate"): the GAP between
            # what the Fed charges and what America pays is the argument - it bleeds full of blood red as the ring lands
            # the fifth watch, second read ("we should circle and call out the low more, now that we have room for it"): the page
            # marks WHERE the climb started - the hand rings the February low and names it - and only then bleeds the gap that
            # grew out of it. The order is the argument: the low, then the distance from it.
            {"kind": "callout", "at": t_moved + 0.35, "dur": 2.2, "target": datum(FED["facts"]["dgs10_low_index"]), "pad": 26,
             "label": f"{FED['facts']['dgs10_low_since_move']:.2f}% - the February low"},
            # ... and the red begins AT the circled low, so the fill is exactly the distance the page just named
            {"kind": "spread", "at": t_moved + 1.5, "dur": 1.8, "from": 0, "to_rule": 0, "from_index": FED["facts"]["dgs10_low_index"], "color": "neg"},
            {"kind": "note", "at": t_tokyo_still, "dur": 1.0, "text": FED_NOTES[0]},
            {"kind": "note", "at": t_tokyo_still + 0.9, "dur": 1.0, "text": FED_NOTES[1]},
            {"kind": "note", "at": t_tokyo_still + 1.8, "dur": 1.2, "text": FED_NOTES[2]},
        ]),
        # 8 the outro: the Remotion kit's card dissolving in over the ring clip; `life` so the pulse gate credits its drift
        (t_outro, runtime_s, clip("outro-v2.mp4", OUTRO), (0, 0, 0), [], "dip", [   # E47: the card is a world change - the dip, not the dissolve
            {"kind": "life", "at": t_outro, "dur": round(runtime_s - t_outro, 2)},
        ]),
    ]


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
PRESS_GAIN = 0.08   # R26-5 / E44 s2a (P52 T13): the transient accent at a cut, halved from 0.16 [DERIVED: from the 2026-09-05 metering, halved] -
                    # the same dial as sound/SOUND-PLAN.json `transient_gain`; the V2 cut carries no press cue, so no build output changes
PANEL_CLIP = "clip-c-blue-ties-panel"         # the press: phones out for the whole panel clip


def sound_cues(rows: list[tuple]) -> list[dict]:
    """This episode's cue map over the kit's transition and arrival readings: which file plays where, and how loud."""
    STOP = A.stop_dials()                     # FLIGHT_S / ANTIC_S / DROP_S from the kinetics module: the landing cue's clock
    cues: list[dict] = []
    for i, r in enumerate(rows):
        page = A.page_transitions(r[2])
        if page["ledger"]:
            if page["spiral"]:
                cues.append({"slot": f"page enter {i + 1} (spiral)", "at": round(r[0], 2), "gain": ACCENT, "fade_in": 0.0, "variants": {"A": W_SPIRAL, "B": AIR3, "C": SWIRL_IN}})
            elif not page["mount"]:
                cues.append({"slot": f"page enter {i + 1}", "at": round(r[0], 2), "gain": ENTER_GAIN, "fade_in": 0.0, "variants": {"A": ROLL}})
            if not page["cut"]:
                if page["spiral"]:
                    cues.append({"slot": f"page retract {i + 1} (whirl)", "at": round(r[1] - WHIRL_S, 2), "gain": ACCENT, "fade_in": 0.0, "variants": {"A": SWIRL_OUT, "B": W_DRAIN, "C": AIR4}})
                else:
                    cues.append({"slot": f"page retract {i + 1} (flip)", "at": round(r[1] - RETRACT_S, 2), "gain": ACCENT, "fade_in": 0.0, "variants": {"A": FLIP, "B": AIR1}})
        elif isinstance(r[5], str) and r[5].startswith("suck"):
            cues.append({"slot": f"suck {i + 1}", "at": round(r[0], 2), "gain": ACCENT, "fade_in": 0.0, "variants": {"A": W_SUCK, "B": AIR3, "C": WHIRLPOOL, "D": ROLL}})
        if PANEL_CLIP in r[2]:
            win = round(r[1] - r[0], 3)
            press_pack(win, HERE / "sound/press-pack-A.mp3", clusters=12, seed=0xC1A55)
            press_pack(win, HERE / "sound/press-pack-B.mp3", clusters=6, seed=0xC1A56)
            cues.append({"slot": f"press {i + 1}", "at": round(r[0], 2), "gain": PRESS_GAIN, "fade_in": 0.0, "variants": {"A": "press-pack-A.mp3", "B": "press-pack-B.mp3"},
                         "note": "the pack meters -16.6 LUFS; 0.16 puts the clicks ~14.5 dB under the voice (operator, 2026-09-05: 14-15 dB under)"})
        # THE LANDING CUE (P47 T1 follow-up, the weight report Q5 - source on file: Williams pp. 263, 309-311): the sound lands ON the
        # contact frame or one frame early, never two ahead. The contact is the dock's enter + the module's own flight (a throw)
        # or anticipation + drop (a land), read from stopaction.mjs so the cue cannot drift from the motion. The file: the quiet
        # page turn (documented, -19.1 LUFS) for both until the ear says; fs-riserhit-754771.mp3 sits in the folder with NO line in
        # sound/SOURCES.md and is not used. The report's "+6 to +12 dB" for a hit is a doctrine line, not our measurement - the gain
        # stays at ACCENT for the second watch.
        for d, opts in A.row_arrivals(r):
            arr = opts["arrive"]
            contact = A.landing_contact(d[2], arr, STOP)
            cues.append({"slot": f"landing {i + 1} ({arr}, {opts.get('mass', 'paper')})", "at": round(contact - 1 / 24, 2), "gain": ACCENT, "fade_in": 0.0,
                         "variants": {"A": FLIP, "B": "fs-page-stroke-447925.mp3"},
                         "note": f"contact at {contact:.2f}s, the cue one frame early (the report Q5: 0 to -1 frame); a documented hit file for metal is still to find"})
    # the beds, sub-threshold and continuous: the hook bed from 0, the turn bed fading in under it at 0:40 to the end
    # the bed's ENVELOPE (dB against its own gain), keyed to every thrown card: up over the 0.3 s before the throw, held through the
    # landing (and the snap when the card becomes the page), down over 0.8 s - the player and the render apply it as a pure function of t
    # NOTE the snap key is `:snap=` ALONE: this cut's ring arrives by `:camera=` under TOKYO_CAMERA=1, and its swell has always
    # fallen back to the throw + 1.2 s. Widening the key would move the bed under an approved cut, so it stays as shipped.
    env = A.bed_envelope(rows, BED_SWELL_DB, SNAP_S_BED, fallback_end=lambda d: float(d[2]) + 1.2, snap_keys=(":snap=",))
    hook_env = [k for k in env if k[0] < TURN_BED_AT]
    turn_env = [[round(k[0] - TURN_BED_AT, 2), k[1]] for k in env if k[0] >= TURN_BED_AT]
    cues.append({"slot": "hook bed", "at": 0.0, "gain": bed_gain("suno-hook-B.mp3"), "fade_in": 1.5, "env": hook_env, "variants": {"A": "suno-hook-B.mp3", "B": "suno-hook-A.mp3"},
                 "note": f"{PLATFORM} {BED_LU[PLATFORM]:+.0f} LU under the VO ({VO_LUFS} LUFS); B at {bed_gain('suno-hook-A.mp3')}"})
    cues.append({"slot": "turn bed", "at": TURN_BED_AT, "gain": bed_gain("suno-pivot-A.mp3"), "fade_in": 3.0, "env": [[round(k[0] + TURN_BED_AT, 2), k[1]] for k in turn_env], "variants": {"A": "suno-pivot-A.mp3", "B": "suno-pivot-B.mp3"},
                 "note": f"{PLATFORM} {BED_LU[PLATFORM]:+.0f} LU under the VO; B at {bed_gain('suno-pivot-B.mp3')}"})
    return cues


def main() -> int:
    ws = W.take_words(EP)
    EP.mkdirs()
    shutil.copy2(TAKE / "scene_1.mp3", EP.audio_master)
    W.write_timeline(EP, ws, A.probe_duration(EP.audio_master))
    # the OWED room at the four cut points (doc 37: silence over the settle lives in the editor's timeline)
    tl_built = W.apply_edit_pauses(EP, EDIT_PAUSES)
    ws = W.shifted_words(EP)
    # the outro extends the runtime past the VO: pad the (paused) audio with silence so the player plays to the end
    t_vo_end = tl_built["runtime_s"]
    line_s = A.probe_duration(BRAND_LINE)
    t_outro, t_line, runtime_s = A.outro_clock(t_vo_end, line_s, outro_lead=OUTRO_LEAD, outro_s=OUTRO_S, brand_gap=BRAND_GAP, brand_tail=BRAND_TAIL)
    audio = BUILD / tl_built.get("paused_audio", "audio/episode.mp3")
    A.stitch_brand_line(audio, BRAND_LINE, BRAND_GAP, runtime_s)
    print(f"  brand line  : {line_s:.2f}s at {t_line:.2f}s (gap {BRAND_GAP}s after the last word); card at {t_outro:.2f}s; runtime {runtime_s:.2f}s")
    tl_built["runtime_s"] = runtime_s
    W.save_timeline(EP, tl_built)
    # v2: the short DOES dock - the clips arrive over the page as stills (E44 / operator, 2026-09-06). The cards carry an
    # authored title, source and species; the pages are still the proof.
    (HERE / "evidence/objects").mkdir(exist_ok=True)
    for s in SERIES:
        shutil.copy2(HERE / "evidence" / f"{s}.series.json", HERE / "evidence/objects" / f"{s}.series.json")

    # a page holds a phrase of 3-6 words on TWO lines at most: the portrait strip is 800 px at 64 px type = 25-28 chars a
    # line; measured 2026-09-05 - 46 chars / 7 words wrapped half the pages to 3-5 lines
    T.caption_pages(BUILD, char_budget=28, max_words=6)

    rows = shot_table(ws, runtime_s, t_outro)
    # written AFTER the rows: record_dock fills a META entry's `record` (the typed words) while the rows are built (2026-09-10)
    (BUILD / "evidence-dock.json").write_text(json.dumps(DOCK_META, indent=1), encoding="utf-8")
    # the page-enter cue (M11: a sound hit within 1.5 s of the first chart): the page roll-out foley at
    # every ledger entry, on the episode clock, beside the page-relative page_cues (P35 T9)
    plan_path = HERE / "sound/SOUND-PLAN.json"
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    plan["cues"] = sound_cues(rows)
    plan_path.write_text(json.dumps(plan, indent=1), encoding="utf-8")
    T.write_shot_table(HERE / "SHOT-TABLE-SHORT.py", rows,
                       '"""Tokyo short - AUTHORED shot table, timed from the take by build_short.py. Do not hand-edit; edit build_short.shot_table."""\n')
    T.print_rows(rows)

    rc = T.compile_timeline(
        HERE, BUILD,
        timeline_name="tokyo-short.timeline.json",
        shot_table_file="SHOT-TABLE-SHORT.py",
        title="Tokyo Tea Break", subtitle="Money Physics · short", episode_id="tokyo-tea-break",
        aspect="9:16",
        caption_style="phrase",   # shorts read their captions (operator, 2026-09-05): the page lands as one phrase, only k-words punctuated
        # the timing module (FINDING-the-animation-math s2/s3): closed-form springs on the pops, minimum-jerk on the wipe and
        # the suck; area_squash (P43 T4) stretches a badge pop along its travel from the spring's own velocity (42 s42.3);
        # km_ink OFF (P43 T3, operator 2026-09-05 after six rounds: "our original applications were better ... turn ink off");
        # curvature_stroke ON - the HAND on every drawn path (P43 T2, ruled from the side-by-side clip)
        kinetics={"analytic_spring": True, "min_jerk": True, "area_squash": True, "km_ink": False, "curvature_stroke": True})
    if os.environ.get("SELF_WATCH", "1") == "1":   # P51 T3: the one-shot bar runs LAST - the probe (M25's input), the gate, the lint, the verdicts, the opening's sheets -> SELF-WATCH.md; SELF_WATCH=0 skips it
        import self_watch as SW
        rc = rc or SW.main([str(BUILD), "--project", str(HERE), "--script", "SCRIPT-90S.claude"])
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
