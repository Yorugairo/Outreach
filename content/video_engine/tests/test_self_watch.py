"""The self-watch (P51 T3): the one-shot bar as a build artifact. The mechanical rows are filled by the tools, the O-rows
are the agent's read (TODO from the runner), a FAIL in section 1 is NOT CLEAN and exit 1, the opening's sheets exist.

P56 T7 adds the one-shot floor to section 1 (M35-M42, parsed from ONE subprocess of `gate_one_shot_floor.py` - a FAIL
there says `NOT CLEAN - the one-shot floor (M3x)`, M40/M42 never end the report, a missing gate WARNs) and the recipe
audit sheets (one png per beat that carries a proven recipe: this cut's member frames over the PROOF cut's own, the
proof read read-only and never rebuilt). The floor gate and the probes are faked here - no browser, no real cut.
"""
from __future__ import annotations

import json
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


def _small_build(tmp_path) -> Path:
    """The smallest build the bar's publish step can read: a take and a compiled timeline (P52 T16)."""
    build = tmp_path / "proj" / "build-x"
    build.mkdir(parents=True)
    (build / "timeline.json").write_text(json.dumps(
        {"episode": "demo", "script": "S.txt", "take": "vo", "runtime_s": 12.0,
         "sentences": [{"text": "One line that opens it.", "start": 0.0, "end": 2.0},
                       {"text": "Japan sold a hundred billion.", "start": 3.0, "end": 6.0}]}), encoding="utf-8")
    (build / "demo.timeline.json").write_text(json.dumps(
        {"title": "Demo Short", "subtitle": "Demo Channel · short", "episode_id": "demo", "aspect": "9:16",
         "evidence": {}, "scenes": [{"world": {"page": {"source": "US Treasury TIC · 2026-09"}}}]}),
        encoding="utf-8")
    return build


# ---- the publish package joins the bar (R26-8, P52 T16) -------------------------------------------------------------
def test_the_publish_package_is_a_section_1_row_and_lands_in_the_build(tmp_path):
    build = _small_build(tmp_path)
    row = SW.publish_row(build, build.parent)
    assert row[0] == "the publish package (R26-8)" and row[1] == "WARN"      # this build carries no dossier, no master
    assert "publish/: CHECKLIST.md" in row[2] and "not on disk:" in row[2]
    assert (build / "publish" / "CHECKLIST.md").is_file() and (build / "publish" / "DESCRIPTION-YOUTUBE.md").is_file()
    assert "Demo Short" in (build / "publish" / "DESCRIPTION-YOUTUBE.md").read_text(encoding="utf-8")


def test_the_report_lists_the_publish_row_under_the_gates(tmp_path):
    build = _small_build(tmp_path)
    rows = [("motion gate (M01-M24)", "PASS", "clean"), SW.publish_row(build, build.parent)]
    md = SW.render(build, build.parent, "S", "short", "abc", "demo.timeline.json", 12.0, "9:16", rows, [], [0.0],
                   "2026-09-12")
    sec1 = md.split("## 2.")[0]
    assert "| the publish package (R26-8) | WARN |" in sec1 and "CHECKLIST.md" in sec1


def test_a_package_that_cannot_be_written_warns_and_never_ends_the_watch(tmp_path):
    empty = tmp_path / "no-build"
    empty.mkdir()
    row = SW.publish_row(empty, empty)
    assert row[1] == "WARN" and row[2].startswith("not written: ")
    g = SW.parse_gate(GATE_TEXT.replace("[FAIL ] M12", "[PASS ] M12"))
    rows = SW.section1(g, [], {"sentences": 1, "with_act": 1, "with_row": 1, "no_row": 0}, "VERDICT: PASS",
                       "VERDICT: PASS", "short") + [row]
    assert SW.verdict(rows).startswith("TODO -")                             # a missing description is not a FAIL


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
    assert rc in (0, 1), report            # 1 = NOT CLEAN on the frozen build's standing motion-gate FAILs (below)
    assert report.startswith("# SELF-WATCH - tokyo-tea-break - build-short - ")
    lines = report.splitlines()
    sec1 = [l for l in lines if l.startswith("| ") and " | " in l and not l.startswith("| row") and not l.startswith("| #")]
    mech = sec1[:6]
    levels = [l.split(" | ")[1] for l in mech]
    # the frozen build-short carries the gate's STANDING verdicts - WARNs (M21) and, since M27/M28 (2026-09-11) and M29
    # (P52 T13), FAILs (M11, M27, M28, M29) - a frozen copy is never rebuilt (E-rule), so the row reads its level and the
    # report is still written; re-baselined 2026-09-12 (P52 T16)
    assert levels[0] in ("PASS", "WARN", "FAIL") and levels[1:] == ["PASS", "INFO", "n/a", "absent", "absent"], mech
    # P52 T16; P56 T7 (2026-09-13) put the floor rows M35-M42 between the six mechanical rows and publish, so the row is found
    # by name, not by index
    assert "the publish package (R26-8) | " in report and any(line.startswith("| the publish package") for line in sec1)
    assert (build / "publish" / "CHECKLIST.md").is_file()
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
    last = report.splitlines()[-1]
    assert last.startswith("NOT CLEAN - ") and "the script gates: VERDICT: FAIL" in report, last   # the motion gate's standing
    #   FAILs on the frozen build (M11, M27, M28, M29) may be named first; the script gates' FAIL is still in the verdict line


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


# ---- the one-shot floor rides section 1 (P56 T7) --------------------------------------------------------------------
FLOOR_TEXT = """=== ONE-SHOT FLOOR: build-x ===
              timeline: cut.timeline.json (89.00 s, 7 docks)
  [INFO ] M35 2 chart forms (line, bars) - the floor is 3; predates E96 (measured 2)
          docs/portable/OPERATOR-RULINGS.md E96
  [FAIL ] M37 docks on 0.28 of 25 beats (7 on screen, 5 entering) - the floor is 0.33
          docs/portable/OPERATOR-RULINGS.md E96
  [FAIL ] M38 coverage 0.44 of 25 beats - the floor is 0.60
          docs/portable/OPERATOR-RULINGS.md E96
  [JUDGE] M40 parity: this cut | japan-tariff-trick/build-short measured at run time | Bravos quoted
          | distinct chart forms |         2 |         2 | ~6
          | events / min         |      18.2 |      28.1 | 6.0
  [INFO ] M42 18.2 events/min (27 = 12 + 15 over 89.00 s) - reported, never a floor
          docs/portable/OPERATOR-RULINGS.md E96
RESULT: 2 FAIL / 0 WARN / 0 PASS / 1 JUDGE / 2 INFO
"""


def _stub_floor(monkeypatch, tmp_path, body: str = FLOOR_TEXT, rc: int = 1) -> None:
    """A stub `gate_one_shot_floor.py`: the bar shells out to it exactly as it does to the motion gate."""
    stub = tmp_path / "stub_floor.py"
    stub.write_text("import sys\nsys.stdout.reconfigure(encoding='utf-8')\n"
                    f"print({body!r})\nraise SystemExit({rc})\n", encoding="utf-8")
    monkeypatch.setattr(SW, "FLOOR", stub, raising=True)


def test_run_floor_parses_the_gates_own_rows_and_recomputes_nothing(tmp_path, monkeypatch):
    _stub_floor(monkeypatch, tmp_path)
    rows = SW.run_floor(tmp_path)
    assert [r["id"] for r in rows] == ["M35", "M37", "M38", "M40", "M42"]       # the M40 table lines are not rows
    assert [r["level"] for r in rows] == ["INFO", "FAIL", "FAIL", "JUDGE", "INFO"]
    assert rows[0]["text"].startswith("2 chart forms (line, bars)") and "predates E96" in rows[0]["text"]
    assert rows[3]["text"].startswith("parity: this cut |") and "distinct chart forms" not in rows[3]["text"]


def test_a_floor_fail_is_not_clean_and_names_the_first_id_then_the_rest(tmp_path, monkeypatch):
    _stub_floor(monkeypatch, tmp_path)
    g = SW.parse_gate(GATE_TEXT.replace("[FAIL ] M12", "[PASS ] M12"))
    counts = {"sentences": 3, "with_act": 2, "with_row": 2, "no_row": 0}
    rows = SW.section1(g, [], counts, "VERDICT: PASS", "VERDICT: PASS", "short", SW.run_floor(tmp_path))
    assert [n for n, _lv, _d in rows][6:] == [f"the one-shot floor ({i})" for i in ("M35", "M37", "M38", "M40", "M42")]
    v = SW.verdict(rows)
    assert v.startswith("NOT CLEAN - the one-shot floor (M37): docks on 0.28 of 25 beats")
    assert v.endswith("also under the floor: M38") and SW.floor_id("the one-shot floor (M37)") == "M37"


def test_the_floors_judge_and_info_rows_never_end_the_report(tmp_path, monkeypatch):
    judged = "\n".join(l for l in FLOOR_TEXT.splitlines() if "] M37" not in l and "] M38" not in l)
    _stub_floor(monkeypatch, tmp_path, judged + "\n", rc=0)
    g = SW.parse_gate(GATE_TEXT.replace("[FAIL ] M12", "[PASS ] M12"))
    floor = SW.run_floor(tmp_path)
    rows = SW.section1(g, [], {"sentences": 1, "with_act": 1, "with_row": 1, "no_row": 0}, "VERDICT: PASS",
                       "VERDICT: PASS", "short", floor)
    assert [r["level"] for r in floor] == ["INFO", "JUDGE", "INFO"]
    assert SW.verdict(rows).startswith("TODO - the agent reads the sheets and fills O1-O11")


def test_a_missing_or_crashing_floor_gate_is_one_warn_row_naming_it(tmp_path, monkeypatch):
    monkeypatch.setattr(SW, "FLOOR", tmp_path / "nope.py", raising=True)
    rows = SW.run_floor(tmp_path)
    assert len(rows) == 1 and rows[0]["level"] == "WARN" and rows[0]["id"] == "M35-M42"
    assert "the floor gate is not on disk (nope.py)" in rows[0]["text"]
    crash = tmp_path / "crash.py"
    crash.write_text("raise SystemExit('no *.timeline.json in build-x')\n", encoding="utf-8")
    monkeypatch.setattr(SW, "FLOOR", crash, raising=True)
    rows = SW.run_floor(tmp_path)
    assert rows[0]["level"] == "WARN" and "printed no row (exit 1)" in rows[0]["text"]
    assert "no *.timeline.json" in rows[0]["text"]
    g = SW.parse_gate(GATE_TEXT.replace("[FAIL ] M12", "[PASS ] M12"))
    rows = SW.section1(g, [], {"sentences": 1, "with_act": 1, "with_row": 1, "no_row": 0}, "VERDICT: PASS",
                       "VERDICT: PASS", "short", rows)
    assert rows[6][0] == "the one-shot floor (M35-M42)" and SW.verdict(rows).startswith("TODO -")


# ---- the recipe audit sheets (P56 T7, O11) -------------------------------------------------------------------------
PUNCH = {"id": "recipe:test-punch", "axis": "recipe", "status": "proven", "window_s": 6.0, "members": [
    {"card": "plate_option:world", "offset_s": 0.0, "role": "the world arrives"},
    {"card": "species:punch", "offset_s": 1.0, "role": "the punch lands on the word"}]}


def _cut(dir_: Path, scenes: list, beats: list) -> Path:
    """A build dir the walk can read: one compiled timeline and the words `timeline.json` (the beats)."""
    dir_.mkdir(parents=True, exist_ok=True)
    (dir_ / "cut.timeline.json").write_text(json.dumps(
        {"schema_version": "scene_evidence_timeline.v1", "runtime_s": 30.0, "scenes": scenes, "evidence": {}}),
        encoding="utf-8")
    (dir_ / "timeline.json").write_text(json.dumps(
        {"runtime_s": 30.0, "sentences": [{"text": f"beat {i + 1}", "start": a, "end": b}
                                          for i, (a, b) in enumerate(beats)]}), encoding="utf-8")
    return dir_


def _plate(sid: str, span: list, at: float | None = None) -> dict:
    return {"scene_id": sid, "span": span, "world": {"asset_id": f"plate-{sid}"}, "exit": "cut", "docks": [],
            "species": ([{"kind": "punch", "at": at}] if at is not None else [])}


def _catalog(path: Path, proof_timeline: str, members_at=(4.0, 5.0)) -> Path:
    """A one-record effects catalogue: the recipe, `proven`, with its proof on (or off) disk. The proof path is
    ABSOLUTE here - `proof_dir` reads a repo-relative one against the repo root, which a tmp dir is not under."""
    record = {**PUNCH, "proof": {"project": "proj", "build": "proof", "scene": "s1", "t": members_at[0],
                                 "members_at": list(members_at), "timeline": proof_timeline}}
    path.write_text(json.dumps(record) + "\n", encoding="utf-8")
    return path


def _builds(tmp_path, proof_on_disk: bool = True):
    """This cut (a punch in beat 1 and in beat 2) and the PROOF cut (a punch at 4.0), plus the catalogue."""
    build = _cut(tmp_path / "proj" / "build-x",
                 [_plate("s1", [0, 10], at=1.0), _plate("s2", [10, 20], at=11.0), _plate("s3", [20, 30])],
                 [(0, 10), (10, 20), (20, 30)])
    proof = _cut(tmp_path / "proj" / "proof", [_plate("s1", [0, 10], at=5.0)], [(0, 10)])
    tl = (proof / "cut.timeline.json") if proof_on_disk else (proof / "absent.timeline.json")
    return build, proof, _catalog(tmp_path / "EFFECTS-CATALOG.jsonl", str(tl))


class _FakeProbe:
    """A probe with no browser: one small solid frame per instant, and the build it was opened on (read-only)."""
    opened: list = []

    def __init__(self, build, timeline_name=None, html_name="player.html"):
        self.build = Path(build)
        self.seen: list = []
        _FakeProbe.opened.append(self.build)

    def png(self, t: float) -> bytes:
        import io
        from PIL import Image
        self.seen.append(round(float(t), 2))
        buf = io.BytesIO()
        Image.new("RGB", (108, 192), (20, 30, 40)).save(buf, "PNG")
        return buf.getvalue()

    def __enter__(self):
        return self

    def __exit__(self, *_exc):
        return False


def test_the_shots_are_one_per_beat_per_recipe_with_this_cuts_and_the_proofs_instants(tmp_path):
    build, proof, cat = _builds(tmp_path)
    shots, misses = SW.recipe_shots(build, catalog=cat)
    assert misses == [] and [s["png"] for s in shots] == ["beat01-test-punch.png", "beat02-test-punch.png"]
    assert [s["beat"] for s in shots] == [1, 2] and [s["at"] for s in shots] == [[0.0, 1.0], [10.0, 11.0]]
    assert all(s["proof_at"] == [4.0, 5.0] and Path(s["proof_dir"]) == proof for s in shots)
    assert all(s["proof_name"] == "proj/proof" for s in shots)
    assert SW.beat_of([{"start": 0.0, "end": 10.0}, {"start": 10.0, "end": 20.0}], 11.0) == 2


def test_a_recipe_whose_proof_cut_is_not_on_disk_warns_and_draws_no_sheet(tmp_path):
    build, _proof, cat = _builds(tmp_path, proof_on_disk=False)
    shots, misses = SW.recipe_shots(build, catalog=cat)
    assert shots == [] and len(misses) == 1
    assert misses[0].startswith("recipe:test-punch: the proof cut is not on disk") and "absent.timeline.json" in misses[0]
    row = SW.recipe_row([], shots, misses)
    assert row[0] == "the recipe audit sheets (O11)" and row[1] == "WARN" and "not on disk" in row[2]
    assert SW.verdict([row]).startswith("TODO -")                 # a missing proof never ends the watch


def test_the_sheet_writer_writes_one_png_per_fire_with_both_rows(tmp_path):
    build, proof, cat = _builds(tmp_path)
    shots, misses = SW.recipe_shots(build, catalog=cat)
    p = _FakeProbe(build)
    here, ahead, warns = SW.recipe_frames(p, shots, build)
    assert warns == [] and ahead == {} and p.seen == [0.0, 1.0, 10.0, 11.0]     # the proof cut is another build
    _FakeProbe.opened = []
    ahead, warns = SW.proof_frames(shots, ahead, open_probe=_FakeProbe)
    assert warns == [] and list(ahead) == ["recipe:test-punch"] and len(ahead["recipe:test-punch"]) == 2
    assert _FakeProbe.opened == [proof]                                         # ONE read-only session on the proof
    paths, warns = SW.write_recipe_sheets(build, shots, here, ahead, tile=60)
    assert warns == [] and [x.name for x in paths] == ["beat01-test-punch.png", "beat02-test-punch.png"]
    assert all(x.parent == build / SW.SHEET_DIR / SW.RECIPE_DIR and x.is_file() for x in paths)
    from PIL import Image
    im = Image.open(paths[0])
    assert im.width == 2 * 60 and im.height > 2 * round(60 * 192 / 108)         # two rows of two frames, labelled
    row = SW.recipe_row(paths, shots, warns)
    assert row[1] == "INFO" and "2 sheet(s) in self-watch/recipes/ over 2 beat(s)" in row[2]
    assert "beat01-test-punch.png" in row[2] and "O11" in SW.PLAIN
    assert "the members in order, at their offsets" in dict(SW.O_ROWS)["O11"]


def test_a_proof_cut_that_cannot_be_probed_warns_and_the_sheet_is_skipped(tmp_path):
    build, proof, cat = _builds(tmp_path)
    shots, _misses = SW.recipe_shots(build, catalog=cat)
    here, ahead, _w = SW.recipe_frames(_FakeProbe(build), shots, build)

    def _boom(_dir, *a, **kw):
        raise RuntimeError("no player.html in proof - build the episode first")

    ahead, warns = SW.proof_frames(shots, ahead, open_probe=_boom)
    assert ahead == {} and len(warns) == 1 and warns[0].startswith("the proof cut proof could not be read: RuntimeError")
    paths, w2 = SW.write_recipe_sheets(build, shots, here, ahead, tile=60)
    assert paths == [] and len(w2) == 2 and "no frames for the proof cut proj/proof" in w2[0]
    assert SW.recipe_row(paths, shots, warns + w2)[1] == "WARN"


def test_a_cut_with_no_recipe_and_a_build_with_no_timeline_never_crash(tmp_path):
    build = _cut(tmp_path / "proj" / "bare", [_plate("s1", [0, 10])], [(0, 10)])
    cat = _catalog(tmp_path / "EFFECTS-CATALOG.jsonl", str(tmp_path / "proj" / "bare" / "cut.timeline.json"))
    shots, misses = SW.recipe_shots(build, catalog=cat)
    assert shots == [] and misses == []                                 # nothing fires: no sheet, no warning
    row = SW.recipe_row([], shots, misses)
    assert row[1] == "INFO" and row[2] == "no sheet: no proven recipe fires in this cut"
    assert SW.write_recipe_sheets(build, [], {}, {}) == ([], [])
    shots, misses = SW.recipe_shots(tmp_path / "proj" / "nothing-here", catalog=cat)
    assert shots == [] and misses and misses[0].startswith("the fires could not be walked: SystemExit")
