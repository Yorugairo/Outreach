"""The self-watch (P51 T3): the one-shot bar as a build artifact. The mechanical rows are filled by the tools, the O-rows
are the agent's read (TODO from the runner), a FAIL in section 1 is NOT CLEAN and exit 1, the opening's sheets exist."""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import self_watch as SW  # noqa: E402

TOKYO = ROOT / "content/video_engine/projects/systems-and-blowups/tokyo-tea-break"
BUILD = TOKYO / "build-short"

GATE_TEXT = """=== MOTION DENSITY GATE: x ===
  [PASS ] M01 no still stretch over 12s
  [FAIL ] M12 a chart dock spans a scene boundary: dock-x at 0:31
          E25: the chart is the proof, not the homework
  [WARN ] M21 1 page(s) deployed under 6s after the last data mark
  [INFO ] M25 layout not measured - run probe.py <build> --gate (writes layout-probe.json)
RESULT: 1 FAIL / 1 WARN / 14 PASS / 1 JUDGE / 3 INFO
"""


def _browser_ok() -> bool:
    try:
        from playwright.sync_api import sync_playwright  # noqa: F401
        return True
    except Exception:
        return False


needs_build = pytest.mark.skipif(not (BUILD / "player.html").is_file() or not _browser_ok(),
                                 reason="the Tokyo build-short player or the browser is not on disk")


# ---------------------------------------------------------------- the pure parts
def test_parse_gate_reads_rows_and_result():
    g = SW.parse_gate(GATE_TEXT)
    assert g["verdict"] == "FAIL" and [r["id"] for r in g["fails"]] == ["M12"] and [r["id"] for r in g["warns"]] == ["M21"]
    assert g["m25"]["level"] == "INFO" and "not measured" in g["m25"]["text"]
    assert g["result"].startswith("RESULT: 1 FAIL")
    assert SW.parse_gate("")["verdict"] == "absent"


def test_section1_fail_is_not_clean():
    g = SW.parse_gate(GATE_TEXT)
    counts = {"sentences": 3, "with_act": 2, "with_row": 1, "no_row": 1}
    rows = SW.section1(g, ["INFO 0.00-1.00 · \"x\" · TURNS · available: figure · row has: none · no row"], counts, "absent", "absent", "short")
    assert [r[0] for r in rows][:2] == ["motion gate (M01-M24)", "M25 layout"]
    assert rows[0][1] == "FAIL" and rows[1][1] == "INFO" and rows[2][1] == "INFO" and rows[3][1] == "n/a"
    assert rows[4] == ("the viewer (P36)", "absent", "absent") and rows[5][1] == "absent"
    assert SW.verdict(rows).startswith("NOT CLEAN - motion gate (M01-M24): [FAIL] M12")


def test_section1_clean_is_todo_never_clean():
    g = SW.parse_gate(GATE_TEXT.replace("[FAIL ] M12", "[PASS ] M12"))
    counts = {"sentences": 3, "with_act": 2, "with_row": 2, "no_row": 0}
    rows = SW.section1(g, [], counts, "VERDICT: PASS", "VERDICT: PASS (all gates)", "short")
    assert rows[0][1] == "WARN" and rows[4][1] == "PASS" and rows[5][1] == "PASS"
    assert SW.verdict(rows).startswith("TODO -") and "CLEAN" not in SW.verdict(rows).split(" - ")[0]


def test_long_form_lists_the_plates():
    g = SW.parse_gate(GATE_TEXT.replace("[FAIL ] M12", "[PASS ] M12"))
    counts = {"sentences": 3, "with_act": 2, "with_row": 2, "no_row": 0, "plates": 2, "plates_unnamed": 1}
    rows = SW.section1(g, ["WARN 0.00-100.00 · plate plate-a · no named use (E61: ...)"], counts, "absent", "absent", "long")
    assert rows[3][0] == "E61 plates (long)" and rows[3][1] == "WARN" and "plate-a" in rows[3][2]


def test_verdict_line_reads_the_last_verdict_or_absent(tmp_path):
    assert SW.verdict_line(tmp_path / "nope.md") == "absent"
    p = tmp_path / "x-GATES.md"
    p.write_text("# report\nVERDICT: FAIL (1 viewer)\nmore\n**VERDICT:** PASS\n", encoding="utf-8")
    assert SW.verdict_line(p) == "VERDICT: PASS"
    p.write_text("no verdict here\n", encoding="utf-8")
    assert SW.verdict_line(p) == "present, no verdict line"
    assert SW.level_of("VERDICT: FAIL (1 viewer)") == "FAIL" and SW.level_of("absent") == "absent"


def test_opening_instants_are_the_format_window():
    assert SW.opening_instants(88.8, "short", 2.0) == [round(2.0 * i, 2) for i in range(30)]
    assert len(SW.opening_instants(600.0, "long", 2.0)) == 90
    assert SW.opening_instants(10.0, "short", 2.0) == [0.0, 2.0, 4.0, 6.0, 8.0]   # a build shorter than the window


# ---------------------------------------------------------------- the Tokyo build, in a temp copy (never the watched dir)
@needs_build
def test_the_tokyo_report_is_written_with_the_sheets(tmp_path):
    project = tmp_path / "tokyo-tea-break"
    build = project / "build-short"
    build.mkdir(parents=True)
    for name in ("player.html", "timeline.json", "tokyo-short.timeline.json"):
        shutil.copy2(BUILD / name, build / name)
    shutil.copy2(TOKYO / "SHOT-TABLE-SHORT.py", project / "SHOT-TABLE-SHORT.py")   # the lint's table; no script reports -> absent
    rc = SW.main([str(build), "--project", str(project), "--script", "SCRIPT-90S.claude", "--step", "2", "--tile", "240"])
    report = (build / SW.REPORT_NAME).read_text(encoding="utf-8")
    assert rc == 0, report
    assert report.startswith("# SELF-WATCH - tokyo-tea-break - build-short - ")
    lines = report.splitlines()
    sec1 = [l for l in lines if l.startswith("| ") and " | " in l and not l.startswith("| row") and not l.startswith("| #")]
    mech = sec1[:6]
    levels = [l.split(" | ")[1] for l in mech]
    assert levels[0] in ("PASS", "WARN") and levels[1:] == ["PASS", "INFO", "n/a", "absent", "absent"], mech   # the Tokyo gate carries standing WARNs (M11, M21), never a FAIL
    assert "M25 layout | PASS" in report and "no settled card" in report
    assert "species by sentence | INFO" in report and "sentences" in report
    for k, _ in SW.O_ROWS:
        assert f"| {k} | " in report and " | TODO | " in report
    sheets = sorted((build / SW.SHEET_DIR).glob("opening*.png"))
    assert len(sheets) == 3, sheets                       # 30 tiles, 12 a sheet
    assert (build / "layout-probe.json").is_file()        # M25's input was written
    assert lines[-1].startswith("TODO - the agent reads the sheets")


@needs_build
def test_a_failing_script_gate_makes_it_not_clean(tmp_path):
    project = tmp_path / "tokyo-tea-break"
    build = project / "build-short"
    build.mkdir(parents=True)
    for name in ("player.html", "timeline.json", "tokyo-short.timeline.json"):
        shutil.copy2(BUILD / name, build / name)
    shutil.copy2(TOKYO / "SHOT-TABLE-SHORT.py", project / "SHOT-TABLE-SHORT.py")
    (project / "SCRIPT-90S.claude-GATES.md").write_text("# gates\nVERDICT: FAIL (1 viewer)\n", encoding="utf-8")
    rc = SW.main([str(build), "--project", str(project), "--script", "SCRIPT-90S.claude", "--step", "10", "--tile", "200"])
    report = (build / SW.REPORT_NAME).read_text(encoding="utf-8")
    assert rc == 1
    assert report.splitlines()[-1].startswith("NOT CLEAN - the script gates: VERDICT: FAIL")


# ---- the operator's copy (SELF-WATCH.html) ---------------------------------------------------------------------
def test_instants_in_reads_the_forms_and_skips_sizes_shares_and_durations():
    ev = ("t=10.0: the pop over the plot; t=24-32 five tiles; t=57.5 and 57.65 identical; the landing (9.1) and (48-50); "
          "the retitle at 33.2; 11.6 CSS px; 36.6% and 36.59%; reads 0.00 %; 0.4 s before; 303 px; 0:39-0:45; R26-39")
    ts = SW.instants_in(ev, 89.0, cap=40)
    assert ts == [9.0, 10.0, 24.0, 28.0, 32.0, 33.0, 39.0, 45.0, 48.0, 50.0, 57.5]   # a 6 s span has no midpoint; 8 s (24-32) does
    assert SW.instants_in("t=120", 89.0) == []                                   # past the runtime
    assert len(SW.instants_in(" ".join(f"t={t}" for t in range(0, 80, 2)), 89.0)) == SW.TILES_PER_ROW   # capped, spread


def test_parse_report_reads_the_md_the_agent_filled():
    md = "\n".join([
        "# SELF-WATCH - proj - build - 2026-09-11 - short (1 min opening)",
        "player.html sha256 abc - timeline x.timeline.json - runtime 1:29 - aspect 9:16 - script S",
        "", "## 1. The gates (mechanical - a FAIL here ends the report)", "",
        "| row | verdict | detail |", "|---|---|---|",
        "| motion gate (M01-M24) | WARN | [WARN] M11 a \\| b |",
        "| M25 layout | PASS | clean |",
        "", "## 2. The opening, read", "",
        "sheets: self-watch/ opening.1.png, opening.2.png (30 tiles at 2 s steps from 0:00 to 0:58, 360 px, 12 per sheet)",
        "", "| # | check | verdict | evidence (t, what the tile shows) |", "|---|---|---|---|",
        "| O1 | the package | PASS | t=0.0-2.0: the counter |",
        "| O9 | the cards | FAIL | the burst at (59.5) |",
        "", "## 3. Verdict", "", "NOT CLEAN - O9 FAIL", "read 2026-09-11 by the agent", ""])
    rep = SW.parse_report(md)
    assert rep["title"].startswith("SELF-WATCH - proj") and rep["meta"].startswith("player.html sha256 abc")
    assert rep["gates"] == [("motion gate (M01-M24)", "WARN", "[WARN] M11 a | b"), ("M25 layout", "PASS", "clean")]
    assert rep["sheets"] == ["opening.1.png", "opening.2.png"]
    assert rep["o_rows"] == [("O1", "the package", "PASS", "t=0.0-2.0: the counter"), ("O9", "the cards", "FAIL", "the burst at (59.5)")]
    assert rep["verdict"] == "NOT CLEAN - O9 FAIL" and rep["notes"] == ["read 2026-09-11 by the agent"]


def test_write_html_without_a_probe_names_the_instants_and_inlines_the_sheets(tmp_path):
    build = tmp_path / "build"
    (build / SW.SHEET_DIR).mkdir(parents=True)
    from PIL import Image
    Image.new("RGB", (40, 70), (10, 10, 10)).save(build / SW.SHEET_DIR / "opening.1.png")
    (build / "timeline.json").write_text('{"runtime_s": 89.0}', encoding="utf-8")
    (build / "x.timeline.json").write_text('{"aspect": "9:16", "scenes": []}', encoding="utf-8")
    (build / SW.REPORT_NAME).write_text("\n".join([
        "# SELF-WATCH - proj - build - 2026-09-11 - short (1 min opening)", "meta line", "",
        "## 1. The gates", "", "| row | verdict | detail |", "|---|---|---|", "| M25 layout | PASS | clean |", "",
        "## 2. The opening, read", "",
        "sheets: self-watch/ opening.1.png (1 tiles at 2 s steps from 0:00 to 0:00, 360 px, 12 per sheet)", "",
        "| # | check | verdict | evidence (t, what the tile shows) |", "|---|---|---|---|",
        "| O8 | the captions | PASS | t=48 under the plot; t=54 above the note |",
        "| O9 | the cards | TODO | opening.1.png |",
        "", "## 3. Verdict", "", "TODO - the agent reads the sheets", ""]), encoding="utf-8")
    out = SW.write_html(build, None, "http://127.0.0.1:8738/player.html")
    html = out.read_text(encoding="utf-8")
    assert out.name == SW.HTML_NAME
    assert SW.PLAIN["O8"][0] in html and "PASS looks like:" in html and "E62" in html      # the plain question and the looks
    assert "instants named: 0:48.0, 0:54.0" in html                                          # no probe: named, not grabbed
    assert "class='verdict TODO'" in html and "data:image/png;base64," in html                # the sheet inlined
    assert "http://127.0.0.1:8738/player.html?t=" not in html                                 # no tiles without a probe
    assert "<span class='lv PASS'>PASS</span>" in html and "<span class='lv TODO'>TODO</span>" in html


@needs_build
def test_html_from_the_probe_writes_a_tile_per_instant_linked_to_the_player(tmp_path):
    build = tmp_path / "build-short"
    build.mkdir(parents=True)
    for name in ("player.html", "timeline.json", "tokyo-short.timeline.json"):
        shutil.copy2(BUILD / name, build / name)
    (build / SW.SHEET_DIR).mkdir()
    (build / SW.REPORT_NAME).write_text("\n".join([
        "# SELF-WATCH - tokyo-tea-break - build-short - 2026-09-11 - short (1 min opening)", "meta", "",
        "## 1. The gates", "", "| row | verdict | detail |", "|---|---|---|", "| M25 layout | PASS | clean |", "",
        "## 2. The opening, read", "", "sheets: self-watch/  (0 tiles)", "",
        "| # | check | verdict | evidence (t, what the tile shows) |", "|---|---|---|---|",
        "| O8 | the captions | WARN | t=38.0 the anchor caption under the fingers card at 12 CSS px |",
        "", "## 3. Verdict", "", "NOT CLEAN - O8", ""]), encoding="utf-8")
    rc = SW.main([str(build), "--html", "--player-url", "http://127.0.0.1:8738/player.html"])
    assert rc == 0
    html = (build / SW.HTML_NAME).read_text(encoding="utf-8")
    tiles = sorted((build / SW.SHEET_DIR).glob("O8-*.png"))
    assert [p.name for p in tiles] == ["O8-0038.0.png"]
    assert "href='http://127.0.0.1:8738/player.html?t=38' data-t='38'" in html and "0:38.0 · watch" in html and "SEEK_JS" not in html and "name='mp-player'" not in html and "window.open(a.href, 'mp-player')" in html
    from PIL import Image
    im = Image.open(tiles[0])
    assert im.width == SW.TILE_W["9:16"] and abs(im.height / im.width - 1920 / 1080) < 0.02
