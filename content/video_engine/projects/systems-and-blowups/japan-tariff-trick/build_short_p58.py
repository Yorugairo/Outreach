"""Japan tariff trick - P58 T7 attempt 2, THE FIRST 2.5D CUT: a NEW short beside the approved one, never a rebuild (E45).

    python build_short_p58.py                                   # -> build-p58-2-5d/ (the 2.5D cut)
    P58_LAYERED=0 TARIFF_BUILD_DIR=<abs temp dir> python build_short_p58.py   # the FLAT CONTROL: change 1 omitted

It is `build_short.py` exactly - the same script, take, docks, captions, sound and kinetics - with FOUR changes and nothing else:
  1. row 5's world `plate-ship` resolves to a byte-identical COPY of its approved still inside this build
     (`build-p58-2-5d/plates/sig-d-ship-once.png`) whose `.layers.json` declares four b-sam planes. The copy is the point:
     a sidecar beside the approved still would layer the approved cut on its next build.
  2. row 6 arrives by CAMERA (`TARIFF_CHART_ARRIVAL=camera`, this build only): the P49 T5 arrival, a move with a reason.
  3. row 6's page stands at a depth: `;depth=1.15;plane=tilt:14,y` (T4, the `page-depth` golden's pair).
  4. row 8's bars page (`ev-japan-selling-v1`, the `story` builder) takes `;form=extruded_bar` (T5).
Every write `build_short.main` makes OUTSIDE the build dir is redirected or refused: the shot table is written inside the
build; the sound plan is derived and COMPARED with the approved `sound/SOUND-PLAN.json` (identical -> the compiler reads
the untouched file; different -> refuse); the evidence objects are asserted identical, never re-copied; SELF_WATCH is off
(it reads the project's own shot table).
"""
from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

BUILD_DIR = "build-p58-2-5d"
LAYERED = os.environ.get("P58_LAYERED", "1") == "1"
os.environ.setdefault("TARIFF_BUILD_DIR", BUILD_DIR)
if LAYERED and os.environ["TARIFF_BUILD_DIR"] != BUILD_DIR:
    raise SystemExit(f"FAIL: the layered cut builds {BUILD_DIR} only (TARIFF_BUILD_DIR={os.environ['TARIFF_BUILD_DIR']!r})")
if not LAYERED and not Path(os.environ["TARIFF_BUILD_DIR"]).is_absolute():
    raise SystemExit("FAIL: the flat control builds in a temp dir outside the project (an absolute TARIFF_BUILD_DIR)")
os.environ["TARIFF_CHART_ARRIVAL"] = "camera"                                        # change 2

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import build_short as B   # noqa: E402

LAYERED_STILL = HERE / BUILD_DIR / "plates" / "sig-d-ship-once.png"                 # change 1
PAGE_DEPTH = ";depth=1.15;plane=tilt:14,y"                                          # change 3
FORM = ";form=extruded_bar"                                                         # change 4
RECEIPT = "ledger:ev-tariff-receipt-v1:bars:1:right:camera=dock-g-receipt:cut;idle=live"
SELLING = "ledger:ev-japan-selling-v1:bars:2:right:mount="

_live_shot_table = B.shot_table
_live_register = B.register_assets


def shot_table(ws: list[dict], runtime_s: float, t_outro: float) -> list[tuple]:
    """The live table with changes 3 and 4; refuses if the live rows moved under it."""
    rows = [list(r) for r in _live_shot_table(ws, runtime_s, t_outro)]
    if len(rows) != 12:
        raise SystemExit(f"FAIL: the live table has {len(rows)} rows, T7b was authored on 12")
    if rows[4][2] != "plate-ship;idle=drift":
        raise SystemExit(f"FAIL: row 5's world is {rows[4][2]!r}, expected 'plate-ship;idle=drift'")
    if rows[5][2] != RECEIPT:
        raise SystemExit(f"FAIL: row 6's world is {rows[5][2]!r}, expected {RECEIPT!r}")
    if not (str(rows[7][2]).startswith(SELLING) and str(rows[7][2]).endswith(":cut;idle=live")):
        raise SystemExit(f"FAIL: row 8's world is {rows[7][2]!r}, expected the selling bars page")
    rows[5][2] = rows[5][2] + PAGE_DEPTH
    rows[7][2] = rows[7][2] + FORM
    return [tuple(r) for r in rows]


def register_assets() -> None:
    """The live registration, then row 5's plate re-pointed at the layered copy (change 1)."""
    _live_register()
    if LAYERED:
        approved = B.STILLS / f"{B.PLATE_FILES['plate-ship'][B.ARM]}.png"
        if LAYERED_STILL.read_bytes() != approved.read_bytes():
            raise SystemExit(f"FAIL: {LAYERED_STILL} is not a byte-identical copy of {approved}")
        B.D.register("plate-ship", LAYERED_STILL)


def main() -> int:
    """`build_short.main`, with every write outside the build redirected or refused (see the module docstring)."""
    EP, BUILD, HERE_B = B.EP, B.BUILD, B.HERE
    ws = B.W.take_words(EP)
    EP.mkdirs()
    shutil.copy2(B.TAKE / f"{B.TAKE_STEM}.mp3", EP.audio_master)
    t_vo_end = round(B.A.probe_duration(EP.audio_master), 3)
    line_s = B.A.probe_duration(B.BRAND_LINE)
    t_outro, t_line, runtime_s = B.A.outro_clock(t_vo_end, line_s, outro_lead=B.OUTRO_LEAD, outro_s=B.OUTRO_S,
                                                 brand_gap=B.BRAND_GAP, brand_tail=B.BRAND_TAIL)
    B.A.stitch_brand_line(EP.audio_master, B.BRAND_LINE, B.BRAND_GAP, runtime_s)
    B.W.write_timeline(EP, ws, runtime_s)
    print(f"  P58 T7b layered={LAYERED}; arm {B.ARM}; take {t_vo_end:.2f}s; runtime {runtime_s:.2f}s; build {BUILD}")

    (BUILD / "evidence-dock.json").write_text(json.dumps(B.DOCK_META, indent=1), encoding="utf-8")
    for s in B.SERIES:   # the approved build's copy step, asserted instead of re-run: nothing outside the build is written
        src, dst = HERE_B / "evidence" / f"{s}.series.json", HERE_B / "evidence/objects" / f"{s}.series.json"
        if src.read_bytes() != dst.read_bytes():
            raise SystemExit(f"FAIL: evidence/objects/{s}.series.json differs from its source - run build_short.py's copy, not this")
    register_assets()
    B.T.caption_pages(BUILD, char_budget=28, max_words=6)

    rows = shot_table(ws, runtime_s, t_outro)
    B.T.hold_until(rows, ws)
    approved_plan = json.loads((HERE_B / "sound/SOUND-PLAN.json").read_text(encoding="utf-8"))
    plan = dict(approved_plan, cues=B.sound_cues(rows))
    (BUILD / "sound").mkdir(exist_ok=True)
    (BUILD / "sound/SOUND-PLAN.derived.json").write_text(json.dumps(plan, indent=1), encoding="utf-8")
    if plan["cues"] != approved_plan.get("cues"):
        raise SystemExit("FAIL: this build's derived cues differ from the approved sound/SOUND-PLAN.json - the compiler "
                         f"would embed the approved ones; compare {BUILD / 'sound/SOUND-PLAN.derived.json'}")
    print(f"  sound plan: {len(plan['cues'])} derived cues IDENTICAL to the approved sound/SOUND-PLAN.json (not rewritten)")
    B.T.write_shot_table(BUILD / "SHOT-TABLE-SHORT.py", rows,
                         '"""Japan tariff trick short - P58 T7b 2.5D cut, GENERATED by build_short_p58.py. Do not hand-edit."""\n'
                         f"# arm: {B.ARM}; layered: {LAYERED}\n")
    B.T.print_rows(rows, show_docks=True)
    return B.T.compile_timeline(
        HERE_B, BUILD,
        timeline_name="japan-short.timeline.json",
        shot_table_file=os.path.relpath(BUILD / "SHOT-TABLE-SHORT.py", HERE_B),
        title="How Japan Tricked Trump", subtitle="Money Physics - short", episode_id="japan-tariff-trick",
        aspect="9:16", caption_style="phrase",
        kinetics={"analytic_spring": True, "min_jerk": True, "area_squash": True, "km_ink": False, "curvature_stroke": True},
        render=True)


if __name__ == "__main__":
    raise SystemExit(main())
