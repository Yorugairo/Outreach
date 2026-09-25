"""P37 T8 - G-l. The strongest evidence in the PRP: the gate FAILs the template exactly as it
shipped before T0 (the fixture below is that CSS, verbatim) and PASSes the template now."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
import gate_vertical_safe_box as V  # noqa: E402

TEMPLATE = ROOT / "docs/content-video-engine/samples/scene-evidence-player.template.html"

PRE_T0_CSS = '''
  html[data-aspect="9:16"] .dock { width: 952px; top: 690px; }
  html[data-aspect="9:16"] #dock-1 { left: 64px; }
  html[data-aspect="9:16"] #dock-2 { left: 64px; top: 1180px; }
  html[data-aspect="9:16"] #dock-1.solo { width: 952px; left: 64px; top: 690px; }
'''


def _elements(findings):
    return sorted({f.element for f in findings})


def test_the_template_as_shipped_before_t0_fails():
    findings = V.check_template_css(PRE_T0_CSS)
    assert _elements(findings) == ["#caption.quiet", "#dock-1", "#dock-2"], [f.line() for f in findings]
    text = " ".join(f.detail for f in findings)
    assert "leaves the box x(80, 880)" in text          # 64 + 952 = 1016, into the right rail
    assert "leaves the box y(280, 1340)" in text        # dock-2 from 1180 runs past the box
    assert "bottom dead zone" in text                   # no 9:16 caption rule


def test_the_template_now_passes():
    findings = V.check_template_css(TEMPLATE.read_text(encoding="utf-8"))
    assert not findings, "\n".join(f.line() for f in findings)


def test_rendered_rectangles_are_judged_the_same_way():
    ok = {"dock-1": {"x": 80, "y": 280, "right": 880, "bottom": 794}, "dock-2": {"x": 80, "y": 806, "right": 880, "bottom": 1320},
          "caption": {"x": 145, "y": 1399, "right": 935, "bottom": 1440}}
    assert V.check_rects(ok) == []
    bad = {"dock-2": {"x": 64, "y": 1180, "right": 1016, "bottom": 1780}, "caption": {"x": 145, "y": 1759, "right": 935, "bottom": 1800}}
    assert _elements(V.check_rects(bad)) == ["caption", "dock-2"]


# ---- P72 T8 / R26-206: the LANDSCAPE mode - the same tool, a 16:9 reader -------------------------------------------
# The band: doc 29 s9.15 ruling 7 (the operator, 2026-09-02: YouTube's hover-controls bar covers ~10-12 % of the frame
# in the normal and embedded player - the caption never sits lower than 120 px of the 1080p stage) and the template's
# `#caption` comment; MEASURED 2026-09-25 on the player itself (P72 T8 logs/yt-watch.json): the normal player on a
# 1366x768 screen (942x530) puts `.ytp-chrome-bottom` over the bottom 120.2 px of the 1080 stage (11.13 %); on a
# 1920x1080 screen (1344x756) 84.3 px. The controls' own inset is 17-25 px: nothing overlays the sides.

import json  # noqa: E402
import subprocess  # noqa: E402

LAND_CSS_OK = '''
  .dock { position: absolute; top: 206px; width: 864px; }
  #dock-1.solo { width: 1056px; top: 172px; }
  #dock-1.solo.side-r { left: 764px; }
  #dock-1.solo.side-l { left: 100px; }
  #dock-1 { left: 64px; } #dock-2 { left: 992px; }
  html[data-aspect="9:16"] .dock { width: 800px; top: 280px; }
  #caption { position: absolute; left: 145px; right: 145px; bottom: 120px; line-height: 1.24; font-size: 40px; }
  #caption.quiet { font-size: 33px; font-weight: 600; }
'''


def _landscape_build(tmp: Path, docks: list[dict], css: str = LAND_CSS_OK) -> Path:
    """A build dir: a compiled 16:9 timeline with one scene carrying `docks`, and a player whose CSS is `css`."""
    tmp.mkdir(parents=True, exist_ok=True)
    (tmp / "cut.timeline.json").write_text(json.dumps(
        {"aspect": "16:9", "scenes": [{"scene_id": "s01", "span": [0, 30], "docks": docks}]}), encoding="utf-8")
    (tmp / "timeline.json").write_text(json.dumps({"words": []}), encoding="utf-8")   # the words file is never read
    (tmp / "player.html").write_text(f"<html><style>{css}</style><script>const x = {{a: 1}};</script></html>",
                                     encoding="utf-8")
    return tmp


def _card(slide: str, x: float, y: float, w: float, h: float, **over) -> dict:
    return {"id": f"s01.dock.{slide}", "slide": slide, "slot": 0, "enter": 1.0, "exit": 9.0,
            "place": {"x": x, "y": y, "w": w, "h": h}, **over}


def test_the_landscape_band_is_the_measured_hover_controls_bar():
    assert (V.LAND_STAGE, V.LAND_BAND_PX) == ((1920, 1080), 120)
    assert V.LAND_CAPTION_RAIL == 145
    import ledger_page  # noqa: E402  (the anchored strip's one owner)
    x, y, w, h = ledger_page.CAPTION_ANCHOR["16:9"]
    assert (x, 1920 - (x + w), 1080 - (y + h)) == (V.LAND_CAPTION_RAIL, V.LAND_CAPTION_RAIL, V.LAND_BAND_PX)


def test_landscape_mode_names_a_placed_dock_over_the_bottom_band(tmp_path):
    build = _landscape_build(tmp_path / "b", [_card("ev-low", 900, 700, 400, 300), _card("ev-ok", 200, 300, 400, 300)])
    findings, checked = V.check_build_landscape(build)
    assert [f.element for f in findings] == ["s01 ev-low"], [f.line() for f in findings]
    fail = next(f for f in findings if f.element == "s01 ev-low")
    assert "bottom 1000" in fail.detail and "960" in fail.detail and "place" in fail.detail
    assert checked == 2


def test_landscape_mode_reads_the_read_box_and_every_move_a_dock_makes(tmp_path):
    popped = _card("ev-read", 200, 200, 400, 300, read_place={"x": 300, "y": 600, "w": 600, "h": 450})
    moved = _card("ev-move", 1400, 300, 300, 200, centre=True,
                  moves=[{"at": 5.0, "dur": 1.0, "ease": "cubic", "x": 1400.0, "y": 800.0, "w": 300.0, "rot": 0.0}])
    findings, _ = V.check_build_landscape(_landscape_build(tmp_path / "b", [popped, moved]))
    details = {f.element: f.detail for f in findings}
    assert set(details) == {"s01 ev-read", "s01 ev-move"}, details
    assert "read_place" in details["s01 ev-read"] and "bottom 1050" in details["s01 ev-read"]
    assert "move at 5.00s" in details["s01 ev-move"] and "bottom 1000" in details["s01 ev-move"]   # h keeps the aspect


def test_landscape_mode_fails_a_caption_in_the_band_or_off_its_rails(tmp_path):
    ok, _ = V.check_build_landscape(_landscape_build(tmp_path / "ok", []))
    assert ok == []
    low = LAND_CSS_OK.replace("bottom: 120px", "bottom: 38px")     # episode one's own baseline (ruling 7: "got cut off")
    wide = LAND_CSS_OK.replace("left: 145px; right: 145px", "left: 64px; right: 64px")
    for name, css in (("low", low), ("wide", wide)):
        findings, _ = V.check_build_landscape(_landscape_build(tmp_path / name, [], css=css))
        assert [f.element for f in findings] == ["#caption"], (name, [f.line() for f in findings])
        assert all(f.gate == "G-l16" for f in findings)


def test_landscape_mode_judges_the_templates_slot_docks_and_the_shipped_template_passes():
    tall = LAND_CSS_OK.replace(".dock { position: absolute; top: 206px;", ".dock { position: absolute; top: 460px;")
    findings = V.check_template_css_landscape(tall)
    assert {f.element for f in findings} == {"#dock-1", "#dock-2"}, [f.line() for f in findings]   # 460 + 555 > 960
    assert V.check_template_css_landscape(TEMPLATE.read_text(encoding="utf-8")) == []


def test_the_landscape_cli_runs_on_a_build_dir_and_the_portrait_default_is_unchanged(tmp_path):
    tool = ROOT / "content/video_engine/scripts/gate_vertical_safe_box.py"
    build = _landscape_build(tmp_path / "b", [_card("ev-low", 900, 700, 400, 300)])
    done = subprocess.run([sys.executable, str(tool), str(build), "--aspect", "16:9"],
                          capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert done.returncode == 1, done.stdout + done.stderr
    assert "FAIL G-l16 s01 ev-low" in done.stdout and "VERDICT: FAIL" in done.stdout
    assert "the lowest placed box ends at y 1000 (s01 ev-low place), -40 px above the band" in done.stdout, done.stdout
    portrait = subprocess.run([sys.executable, str(tool), str(TEMPLATE)], capture_output=True, text=True,
                              encoding="utf-8", errors="replace")
    assert portrait.returncode == 0 and "VERDICT: PASS (0 findings)" in portrait.stdout, portrait.stdout


def test_the_rendered_reader_judges_a_served_box_against_the_same_band():
    ok = {"s25 dock-h-weight-check @ 757.20s": {"x": -2, "y": 378, "right": 1115, "bottom": 916},   # H, measured
          "#caption @ 757.20s": {"x": 141, "y": 919, "right": 1778, "bottom": 960}}
    assert V.check_rects_landscape(ok) == []
    low = {"s01 ev-low @ 5.00s": {"x": 900, "y": 800, "right": 1300, "bottom": 975}}
    assert [f.element for f in V.check_rects_landscape(low)] == ["s01 ev-low @ 5.00s"]


def test_settle_instants_read_each_placed_dock_after_its_read_its_park_and_each_move():
    tl = {"scenes": [{"scene_id": "s01", "span": [0.0, 40.0], "docks": [
        _card("ev-a", 100, 100, 300, 200, enter=10.0, exit=20.0, read_s=1.2, park_s=0.7, park=True),
        _card("ev-b", 100, 100, 300, 200, enter=10.0, exit=11.0, read_place={"x": 0, "y": 0, "w": 9, "h": 9}),
        _card("ev-c", 100, 100, 300, 200, enter=10.0, exit=30.0, moves=[{"at": 20.0, "dur": 1.0, "x": 0, "y": 0, "w": 9}]),
        {"slide": "ev-slot", "enter": 1.0, "exit": 5.0}]},
        # H s03: a thrown card carried past its scene into the next page's hand-off (the snap's zoom)
        {"scene_id": "s03", "span": [49.45, 56.62], "docks": [
            _card("ev-snap", 173, 86, 653, 367, enter=55.62, exit=57.07, read_s=1.2, park=False, centre=True)]}]}
    got = V.settle_instants(tl)
    assert (12.05, "s01", "ev-a") in got                                         # read + park + the pad
    assert (11.35, "s01", "ev-c") in got and (21.15, "s01", "ev-c") in got       # no park: after its read; after its move
    assert [x for x in got if x[2] == "ev-b"] == [(10.9, "s01", "ev-b")]         # a 1 s life: both instants clip to one
    assert [x for x in got if x[2] == "ev-snap"] == [(56.52, "s03", "ev-snap")]  # inside its OWN scene, before the zoom
    assert not any(slide == "ev-slot" for _, _, slide in got)                   # a slot dock is the CSS reader's
