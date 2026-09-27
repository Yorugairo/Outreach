"""The agenda beat both ways on one bed (P72 T42, R26-229 (a) beside (b)) - a PRIVATE build, never the committed door.

The operator, E99 s82 amended again (g): "A PARK IS ~20 % with a camera pan, or the operator's alternative shape: the
chart MELTS to a ball and is TOSSED off, the list centres". The committed door (`../build_episode_h.py`) carries (b)
- on "One test" the page melts to a ball that splashes onto the three-notch slate and the three questions land on its
face. This module builds the SAME bed twice from ONE source - the door's own `shot_table`, the same take, the same
engine - and changes only the agenda beat:

  (b)  `form-b/`  the door's rows 1-6 as committed (the melt, the slate, the list centred on it);
  (a)  `./`       the page row runs on to the host's dip; on "One test" the chart PARKS ~20 % keeping its left
                  (PARK_A_SCALE, the operator's number), the numbered agenda lands in the room the park frees, one
                  row on each of the words (b)'s rows fire on, and the camera PANS onto the list as the sentence
                  names it ("three questions") - one move, then still (E59 reason 2; s79 (3): the camera where the
                  sentence names the thing, never a pan on nothing).

The door is imported, never edited: `build_episode_h.py` is byte-identical before and after (the run asserts it, and
asserts `build-h/` untouched, beside the door's own read-only wall). The bed ends where row 7 opens (the dip into the
studio, HOST_FROM_PHRASE), so both forms carry the beat to its door and nothing after it.

Run from the repo root:  python content/video_engine/projects/systems-and-blowups/steel-and-paper/build-h-agenda-a/build_agenda_beds.py
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent            # build-h-agenda-a/ (form (a) builds here)
EPISODE = HERE.parent                              # steel-and-paper/
DOOR = EPISODE / "build_episode_h.py"
FORM_B_DIR = "form-b"                               # form (b) builds into build-h-agenda-a/form-b/

# ---- form (a)'s dials, each the operator's word or a measurement on this build's own frames (BUILD-NOTES-AGENDA.md)
PARK_A_SCALE = 0.80           # "you could have probably shrunk 20% and been fine" (E99 s82 amended again)
PARK_A_ANCHOR = "left"        # the chart keeps its left (the y ticks and the title stay where the eye left them)
PARK_A_LEAD_S = 0.5           # the park opens this far before "One test" (the prior park form's own lead, 2ca4b0f^)
PARK_A_S = 0.9                # ... and takes this long (the same)
# the room the 0.80 park frees, measured on the parked page (probe at 42.9 s): see BUILD-NOTES-AGENDA.md
AGENDA_A_BOX = {"kind": "region", "x0": 0.745, "y0": 0.20, "x1": 0.95, "y1": 0.62}
PAN_LEAD_S = 0.25             # the pan opens this far before "three questions" (the park has settled by then)
PAN_S = 1.6                   # ... and lands as the second row fires ("thirty"), then holds - one move, then still
PAN_ZOOM = 1.06               # E99 s80 (3): "a zoom under ~1.06 is not a move" - the smallest move that is one
PAN_FRAME_X0 = 80.0           # stage px: the pushed frame's left edge. At 1.06 the frame is 1811 px wide, so it can travel
                              # 0..109 px inside the stage (the page's own cream margin is past x 1900): 80 px moves the
                              # frame's centre 55 px TOWARD the list while the push closes on it - "pan the frame a bit"
PAN_CHROME = "fit"            # the page's chrome (title, sub, source, ticks) stays whole in the pushed frame - the camera
                              # relation P69 T26f built for this (E99 s108); the title starts at x 54, so without it any
                              # frame that moves toward the list crops the title (s80 (2): fully in or fully out)
STAGE_W, STAGE_H = 1920.0, 1080.0


def load_door(build_dir: str):
    """The committed door as a module, pointed at a private build dir (its own STEEL_H_BUILD_DIR door)."""
    os.environ["STEEL_H_BUILD_DIR"] = build_dir
    name = "door_h_" + build_dir.replace("/", "_").replace("-", "_")
    spec = importlib.util.spec_from_file_location(name, DOOR)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bed_rows(m, ws_all: list, bed_end: float) -> list:
    """The door's own table, cut to the bed: rows that open before the host's dip, nothing re-timed."""
    rows = m.shot_table(ws_all, bed_end + 1000.0, bed_end + 999.0)   # the outro's clock is past the bed; unused
    bed = [r for r in rows if r[0] < bed_end - 1e-6]
    if not bed or abs(bed[-1][1] - bed_end) > 0.01:
        raise SystemExit("FAIL: the door's bed rows do not end on the host's dip (%.2f): %r"
                         % (bed_end, [(r[0], r[1]) for r in bed]))
    return bed


def form_a(m, ws_all: list, rows: list) -> list:
    """(a): the page row runs to the host's dip; the chart parks ~20 %, the agenda lands in its room, the camera pans.
    The slate row (the melt's) is gone - its three agenda rows move onto the page on the same words."""
    page, slate = rows[0], rows[1]
    if not str(slate[2]).startswith(m.SLATE_PLATE.split(";")[0]) or not str(page[2]).startswith("ledger:"):
        raise SystemExit("FAIL: the door's rows 1-6 are not (page, slate) - the (b) form this bed compares against moved")
    agenda_b = [s for s in slate[6] if s.get("kind") == "agenda"]
    if len(agenda_b) != 1:
        raise SystemExit("FAIL: the slate row carries %d agendas, not one" % len(agenda_b))
    t_test = m.T.at(ws_all, "One test")
    t_three_q = m.T.at(ws_all, "three questions")
    t_thirty = m.T.at(ws_all, "thirty seconds")
    agenda = dict(agenda_b[0], target=AGENDA_A_BOX)   # the same rows, the same words, the same hold - only the room
    species = list(page[6]) + [
        {"kind": "chart_to", "at": round(t_test - PARK_A_LEAD_S, 2), "dur": PARK_A_S, "to": "park",
         "scale": PARK_A_SCALE, "anchor": PARK_A_ANCHOR},
        agenda,
    ]
    look = [round((AGENDA_A_BOX["x0"] + AGENDA_A_BOX["x1"]) / 2, 4), round((AGENDA_A_BOX["y0"] + AGENDA_A_BOX["y1"]) / 2, 4)]
    cam = dict(page[7], chrome=PAN_CHROME)
    # the frame [x0, x0 + W/s] x [y0, y0 + H/s] with the list's centre at `look`: at = s * (look - frame origin)
    y0 = (STAGE_H - STAGE_H / PAN_ZOOM) / 2
    at = [round(PAN_ZOOM * (look[0] * STAGE_W - PAN_FRAME_X0) / STAGE_W, 4),
          round(PAN_ZOOM * (look[1] * STAGE_H - y0) / STAGE_H, 4)]
    t_pan = round(t_three_q - PAN_LEAD_S, 2)
    t_land = round(max(t_pan + PAN_S, t_thirty), 2)
    cam["keys"] = list(cam["keys"]) + [
        {"t": t_pan, "zoom": 1.0, "look": look, "ease": "inout"},
        {"t": t_land, "zoom": PAN_ZOOM, "look": look, "at": at, "ease": "inout"},
    ]
    return [(page[0], slate[1], page[2], page[3], page[4], page[5], species, cam)] + list(rows[2:])


def build(form: str) -> dict:
    build_dir = "build-h-agenda-a" if form == "a" else "build-h-agenda-a/" + FORM_B_DIR
    m = load_door(build_dir)
    read_only = m._read_only_state()
    m.BUILD.mkdir(parents=True, exist_ok=True)
    m.EP.mkdirs()
    ws_all = m.W.take_words(m.EP)
    bed_end = m.W.cut_before(ws_all, m.HOST_FROM_PHRASE, exit="dip")   # row 7's door - the beat's own end
    ws = [w for w in ws_all if w["start_s"] < bed_end]
    m._take_audio(bed_end)
    m.W.write_timeline(m.EP, ws, bed_end)
    m.T.caption_pages(m.BUILD, char_budget=m.CAPTION_BUDGET, max_words=m.CAPTION_MAX_WORDS)
    m.D.dock_still(m.CERT_CARD, m.CERT_PLATE, m.BUILD, still=True, frame_crop=m.CERT_CROP)
    rows = bed_rows(m, ws_all, bed_end)
    if form == "a":
        rows = form_a(m, ws_all, rows)
    used = {d[0] for r in rows for d in r[4]}
    meta = [d for d in m.DOCK_META if d["asset"] in used]
    (m.BUILD / "evidence-dock.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    table = m.BUILD / m.TABLE_NAME
    m.T.write_shot_table(table, rows, '"""Steel and Paper H - the agenda bed, form (%s), GENERATED by '
                         'build-h-agenda-a/build_agenda_beds.py (P72 T42). Do not hand-edit."""\n' % form)
    m.T.print_rows(rows, show_docks=True)
    import recall_verify as RV   # the receipt is the DOOR's `## Recall` block (the door's own redirect, R26-197)
    inner = RV.resolve_ledger
    RV.resolve_ledger = lambda target: DOOR if Path(target).resolve() == EPISODE else inner(target)
    rc = m.T.compile_timeline(
        EPISODE, m.BUILD, timeline_name=m.TIMELINE_NAME, shot_table_file=os.path.relpath(table, EPISODE),
        title=m.TITLE, subtitle=m.SUBTITLE, episode_id=m.EPISODE_ID, aspect=m.ASPECT, caption_style=m.CAPTION_STYLE,
        kinetics={"analytic_spring": True, "min_jerk": True, "area_squash": True, "km_ink": False,
                  "curvature_stroke": True, "plate_idle_paints": False})   # the door's own kinetics, verbatim
    RV.resolve_ledger = inner
    if rc:
        raise SystemExit("FAIL: form (%s) did not compile (rc %d)" % (form, rc))
    cues = m.sound_cues(rows, ws)
    plan = m.BUILD / "SOUND-PLAN.json"
    plan.write_text(json.dumps({"note": "derived by build_agenda_beds.py (P72 T42) from the door's sound_cues",
                                "cues": cues}, indent=1), encoding="utf-8")
    for note in m.LB.embed_cues(m, m.BUILD, cues, m.TIMELINE_NAME):
        print("  [sound] " + note)
    for note in m.LB.bind_embedded_cues(m.BUILD, plan, m.TIMELINE_NAME):
        print("  [sound] " + note)
    report, n_fail = m.MG.write_report(m.BUILD, m.TIMELINE_NAME)
    print("  form (%s)    : %s - bed 0.00-%.2fs, %d rows, motion gate %s %d FAIL"
          % (form, m.BUILD, bed_end, len(rows), report.name, n_fail))
    m._assert_read_only(read_only)
    return {"form": form, "build": str(m.BUILD), "bed_end": bed_end, "rows": len(rows), "gate_fail": n_fail}


def main() -> int:
    door_before = _sha(DOOR)
    build_h = EPISODE / "build-h"
    listing = lambda: sorted((p.relative_to(build_h).as_posix(), p.stat().st_size, p.stat().st_mtime_ns)
                             for p in build_h.rglob("*") if p.is_file()) if build_h.is_dir() else []
    shot_md = EPISODE / "SHOT-TABLE-H.md"
    md_before = _sha(shot_md) if shot_md.is_file() else "absent"
    h_before = listing()
    out = [build("b"), build("a")]
    if _sha(DOOR) != door_before:
        raise SystemExit("FAIL: the committed door moved")
    if listing() != h_before:
        raise SystemExit("FAIL: build-h/ moved - this module writes only build-h-agenda-a/")
    if (_sha(shot_md) if shot_md.is_file() else "absent") != md_before:
        raise SystemExit("FAIL: SHOT-TABLE-H.md moved - the door's read file is the door's")
    (HERE / "BEDS.json").write_text(json.dumps({"door_sha256": door_before, "forms": out}, indent=1), encoding="utf-8")
    print("  door        : build_episode_h.py sha256 %s - unchanged; build-h/ and SHOT-TABLE-H.md unchanged"
          % door_before[:16])
    return 0


if __name__ == "__main__":
    sys.exit(main())
