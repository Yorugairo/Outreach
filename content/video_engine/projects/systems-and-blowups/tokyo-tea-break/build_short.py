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


def seekable_clip(name: str) -> Path:
    """The Flow clip re-encoded with a keyframe every KEYFRAME_EVERY frames (the originals carry ONE keyframe in 240,
    so every seek decoded from frame 0 and live playback fell behind and held - operator, 2026-09-05). Same
    frames, same length; written once into build-short/clips/ and reused while the source is unchanged."""
    import subprocess
    src, out = CLIPS / name, BUILD / "clips" / name
    out.parent.mkdir(parents=True, exist_ok=True)
    if not out.exists() or out.stat().st_mtime < src.stat().st_mtime:
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(src), "-an", "-c:v", "libx264", "-profile:v", "high", "-crf", "17", "-preset", "slow",
                        "-g", str(KEYFRAME_EVERY), "-keyint_min", str(KEYFRAME_EVERY), "-sc_threshold", "0", "-bf", "0", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(out)], check=True)
    return out


def shot_table(ws: list[dict], runtime_s: float) -> list[tuple]:
    """The authored rows (SHOT-TABLE-90S.claude.md, the short section), timed from the take."""
    clip = lambda name: f"clip:{seekable_clip(name).as_posix()}"
    hold = f"ledger:ev-japan-holdings-v1:line:{LAST_IDX}:right"
    meta = "ledger:ev-meta-yield-v1:bars:3:right::cut"   # exit=cut: the punch on "discounts it." is the last beat of the row - no retract under it (E40 #5)
    t_stakes = cut_before(ws, "The Fed hasn't moved")
    t_panel = cut_before(ws, "Three men in blue ties")
    t_lender = cut_before(ws, "Here's what nobody on that panel")
    t_opponent = cut_before(ws, "The opponent isn't the Fed")
    t_promise = cut_before(ws, "a Treasury page")      # the cut drops on "went:" (operator, 2026-09-05): the promise plate
    t_catalyst = cut_before(ws, "Since February, Japan")
    t_pledge = cut_before(ws, "Tokyo has pledged")
    t_second = cut_before(ws, "So, the second number")
    t_ring = cut_before(ws, "The Fed still hasn't moved")
    at = lambda phrase: round(word_time(ws, phrase), 2)
    datum = lambda i: {"kind": "datum", "index": i}
    return [
        # 1 the hook: the counter, the steaming cup, the tab
        (0.0, t_stakes, clip("clip-a-counter-tab-v2.mp4"), (0, 0, 0), [], None, None),
        # 2 stakes: the dial that does not turn, the bill that grows
        (t_stakes, t_panel, clip("clip-b-dial-and-bill-v2.mp4"), (0, 0, 0), [], None, None),
        # 3 archetype: the panel pointing three ways, the crowd on phones (the sixty-three). Mike walks in from the RIGHT,
        #   so the wipe comes from the right (operator, 2026-09-05: the wipe follows the side the character enters from)
        (t_panel, t_lender, clip("clip-c-blue-ties-panel-v2.mp4"), (0, 0, 0), [], "wipe_right", None),
        # 4 THE FIRST PROOF (M11, 8-20 s): the holdings page rolls out under "our biggest lender" - spotlit
        #   on the latest print as it enters; the peak called out at "since February"; a focus on the
        #   slide at "the auction sets your price"; the page leaves before the opponent line (< 20 s, M05)
        (t_lender, t_opponent, hold, (0, 0, 0), [], None, [
            {"kind": "spotlight", "at": round(t_lender + 8.4, 2), "dur": 2.0, "target": datum(LAST_IDX)},   # after the build completes (+8.2 s): no highlight over the charcoal build (operator, 2026-09-04)
            {"kind": "callout", "at": at("selling since February"), "dur": 2.0, "target": datum(PEAK_IDX)},
            # (no focus on "the auction sets": the row ends in the retract, and nothing rides a spiral out - E40 #5;
            #  the vortex IS the picture for "walks")
        ]),
        # 5 opponent + desire/map: two fingers at "Two numbers"
        (t_opponent, t_promise, clip("clip-g-two-fingers-v2.mp4"), (0, 0, 0), [], None, None),
        # 5b the PROMISE plate (operator, 2026-09-05: a narrative plate from "a Treasury page, and your phone" through
        #    "read both numbers yourself"): the viewer's desk - a stick figure at a laptop of numbers, a phone with one
        #    falling red line, a mug. An approved still (E40: the still is the asset); its life is the template's
        #    enters by SUCK (operator, 2026-09-05: near-instant, everything pulled into one point in the black of the stick figure)
        (t_promise, t_catalyst, "plate-p-viewers-desk", (0, 0, 0), [], "suck:0.49,0.55", [
            # regions measured on the approved still (fractions of the frame): the mug's rim, the phone's screen, the laptop's grid
            {"kind": "steam", "at": t_promise, "dur": round(t_catalyst - t_promise, 2), "target": {"kind": "region", "x0": 0.80, "y0": 0.55, "x1": 0.95, "y1": 0.60}},
            {"kind": "trace", "at": t_promise + 0.3, "dur": round(t_catalyst - t_promise - 0.3, 2), "target": {"kind": "region", "x0": 0.117, "y0": 0.39, "x1": 0.26, "y1": 0.485}},
            # the four columns of the grid the head does not cover
            {"kind": "ticker", "at": t_promise + 0.2, "dur": round(t_catalyst - t_promise - 0.2, 2), "density": 0.3, "paper": "#EFE8D5", "tilt": -4,
             # the drawn grid's own lines, measured on the 1080 render (the three columns clear of the head, six rows)
             "col_lines": [0.602, 0.681, 0.750, 0.812], "row_lines": [0.409, 0.431, 0.454, 0.477, 0.501, 0.525, 0.548],
             "target": {"kind": "region", "x0": 0.602, "y0": 0.409, "x1": 0.812, "y1": 0.548}},
        ]),
        # 6 catalyst + loop + foreshadow: the page RETURNS (enter=spiral: it unwinds from its point, never drawn like new)
        (t_catalyst, t_pledge, hold + ":spiral", (0, 0, 0), [], None, [
            {"kind": "punch", "at": at("Since February, Japan"), "dur": 0.9, "target": datum(PEAK_IDX)},
            {"kind": "callout", "at": at("a tenth of"), "dur": 2.0, "target": datum(LAST_IDX)},
            # (no spotlight at "that print is": it ran into the retract - E40 #5)
        ]),
        # 7 the pledge + the read: past the open toll gate toward the fab
        (t_pledge, t_second, clip("clip-f-toll-gate-to-fab-v2.mp4"), (0, 0, 0), [], None, None),
        # 8 the second number: a Meta share priced at each yield, punch on the 5.5 % bar at "discounts"
        (t_second, t_ring, meta, (0, 0, 0), [], None, [
            {"kind": "callout", "at": at("price-to-earnings multiple"), "dur": 2.0, "target": datum(0)},
            {"kind": "punch", "at": at("discounts it."), "dur": 0.9, "target": datum(3)},
        ]),
        # 9 the ring: the same counter, colder; StickMike lifts the tab
        (t_ring, runtime_s, clip("clip-a2-counter-colder-v2.mp4"), (0, 0, 0), [], None, None),
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
    runtime_s = json.loads((BUILD / "timeline.json").read_text(encoding="utf-8"))["runtime_s"]
    (BUILD / "evidence-dock.json").write_text("[]", encoding="utf-8")   # the short docks nothing; its proof is pages
    (HERE / "evidence/objects").mkdir(exist_ok=True)
    for s in SERIES:
        shutil.copy2(HERE / "evidence" / f"{s}.series.json", HERE / "evidence/objects" / f"{s}.series.json")

    import build_caption_pages as CP
    CP.BUILD = BUILD
    CP.main()

    rows = shot_table(ws, runtime_s)
    # the page-enter cue (M11: a sound hit within 1.5 s of the first chart): the page roll-out foley at
    # every ledger entry, on the episode clock, beside the page-relative page_cues (P35 T9)
    plan_path = HERE / "sound/SOUND-PLAN.json"
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    # operator, 2026-09-05: the page-roll "tear" at a fifth of its level (0.9 -> 0.18); a spiral - in or out - and the suck are a WHOOSH
    ROLL, WHOOSH = "fs-page-roll-464302.mp3", "fs-whoosh-2-743004.mp3"
    RETRACT_S = 2.0   # LP_RETRACT.COLOURS + CHARCOAL (template): the spiral out starts here before the row ends
    cues = []
    for i, r in enumerate(rows):
        if r[2].startswith("ledger:"):
            spiral_in, cut = ":spiral" in r[2], r[2].endswith(":cut")
            cues.append({"slot": f"page enter {i + 1}" + (" (spiral)" if spiral_in else ""), "at": round(r[0], 2), "gain": 0.5 if spiral_in else 0.18, "fade_in": 0.0,
                         "variants": {"A": WHOOSH if spiral_in else ROLL}})
            if not cut:
                cues.append({"slot": f"page retract {i + 1}", "at": round(r[1] - RETRACT_S, 2), "gain": 0.5, "fade_in": 0.0, "variants": {"A": WHOOSH}})
        elif isinstance(r[5], str) and r[5].startswith("suck"):
            cues.append({"slot": f"suck {i + 1}", "at": round(r[0], 2), "gain": 0.4, "fade_in": 0.0, "variants": {"A": WHOOSH}})
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
    C.KINETICS = {"analytic_spring": True, "min_jerk": True,   # the timing module (FINDING-the-animation-math s2/s3): closed-form springs on the pops, minimum-jerk on the wipe and the suck
                  "area_squash": True}                        # P43 T4: the badge pops stretch along their travel from the spring's own velocity (42 s42.3)
    # P43 T2 curvature_stroke and T3 km_ink are landed flag-off; they turn on here after the operator rules on the before/after strips (human gates)
    return C.main()


if __name__ == "__main__":
    raise SystemExit(main())
