"""P56 T6: the one-shot floor (M35-M42) - the arithmetic on synthetic timelines, then the four cuts on disk.

The calibration fixture asserts the MEASURED truth, not a hope (HG1 (A), answered 2026-09-13): Japan `2` chart
forms and `0` chart-to-chart transforms as INFO rows that say `predates E96`, `docks on 0.36 of 25 beats` PASS,
`narrative : chart 1.00` PASS, `28.1 events/min` INFO and M41 WARN with no beat plan on disk; the thin one-shot
`1 / 0 / 0.00 / 0.20` with M37 and M39 FAILing and the process exiting 1; Steel `5` forms and `0.80` docks per beat;
Tokyo `2 / 0 / 0.28` (FAIL, under both 1/3 and the reference's own) `/ 1.00`. Those numbers are T2's
(`docs/research/runs/p56-recipe-seeds/measures.md`), re-derived here by the gate's own functions.

M38's exact coverage on the real builds is NOT pinned: three of the 15 proven recipes (badge-ladder,
plate-dock-wipe, held-dock-across-the-cut) carry proofs whose members are still being re-membered (T8 adds the
`dock_option:badge` and `plate_option:*` cards), so the number moves under this file. What is pinned is the row's
SHAPE: the threshold is 0.60 and the reference's own measured coverage prints beside it.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import gate_one_shot_floor as FLOOR  # noqa: E402

PROJECTS = ROOT / "content/video_engine/projects/systems-and-blowups"
JAPAN = PROJECTS / "japan-tariff-trick/build-short"
TOKYO = PROJECTS / "tokyo-tea-break/build-short.v2"
STEEL = PROJECTS / "steel-and-paper/build-f"
THIN = PROJECTS / "normal-for-which-bridge/review-v1"
REGISTRY = ROOT / "docs/GATES-REGISTRY.jsonl"

# `self_watch.parse_gate`'s own row pattern: a row this gate prints must parse there unchanged (T7 depends on it).
ROW_RE = re.compile(r"^\s*\[(PASS |FAIL |WARN |INFO |JUDGE)\]\s*(\S+)\s*(.*)$")


# ---------------------------------------------------------------- synthetic builds

def plate(sid: str, span: list, **over) -> dict:
    base = {"scene_id": sid, "span": span, "world": {"asset_id": f"plate-{sid}"}, "exit": "cut",
            "species": [], "docks": []}
    return {**base, **over}


def page(sid: str, span: list, builder: str = "story", variant: str = "bars", enter: str = "mount",
         **over) -> dict:
    world = {"kind": "ledger", "page": {"title": f"page {sid}", "builder": builder, "variant": variant,
                                        "enter": enter, **(over.pop("page", None) or {})}}
    base = {"scene_id": sid, "span": span, "world": world, "exit": "cut", "species": [], "docks": []}
    return {**base, **over}


def dock(slide: str, enter: float, exit_: float, **over) -> dict:
    return {"slide": slide, "enter": enter, "exit": exit_, **over}


def build(tmp: Path, scenes: list, beats: list, evidence: dict | None = None,
          runtime: float | None = None, plan: list | None = None) -> Path:
    """A build dir: one compiled timeline, one words `timeline.json` (the beats), optionally a beat plan."""
    tmp.mkdir(parents=True, exist_ok=True)
    end = runtime if runtime is not None else max((s["span"][1] for s in scenes), default=60.0)
    (tmp / "cut.timeline.json").write_text(json.dumps(
        {"schema_version": "scene_evidence_timeline.v1", "runtime_s": end, "scenes": scenes,
         "evidence": evidence or {}, "narration": {"words_path": "cut/timeline.json"}}), encoding="utf-8")
    (tmp / "timeline.json").write_text(json.dumps(
        {"sentences": [{"text": f"beat {i + 1}", "start": a, "end": b} for i, (a, b) in enumerate(beats)]}),
        encoding="utf-8")
    if plan is not None:
        (tmp / FLOOR.BEAT_PLAN_NAME).write_text(
            "".join(json.dumps(r) + "\n" for r in plan), encoding="utf-8")
    return tmp


def row(gates: list, rid: str):
    return next(g for g in gates if g.id == rid)


def measured(tmp: Path, scenes: list, beats: list, recipes: list | None = None, **kw) -> FLOOR.Measures:
    return FLOOR.measure(build(tmp, scenes, beats, **kw), recipes=recipes or [])


# ---------------------------------------------------------------- M35: the forms

def test_m35_counts_a_page_pair_and_a_chart_docks_own_discriminator(tmp_path: Path) -> None:
    scenes = [page("s1", [0, 10], "story", "bars"), page("s2", [10, 20], "story", "bars"),
              plate("s3", [20, 30], docks=[dock("ev-a", 20.0, 25.0)])]
    m = measured(tmp_path / "b", scenes, [(0, 10), (10, 20), (20, 30)],
                 evidence={"ev-a": {"species": "chart", "chart": {"series": [1, 2]}}})
    assert m.forms == {"series": 1, "story/bars": 2}
    assert row(FLOOR.rows(m, None, predates=False), "M35").level == "FAIL"


def test_m35_passes_on_three_distinct_forms(tmp_path: Path) -> None:
    scenes = [page("s1", [0, 10], "story", "bars"), page("s2", [10, 20], "dense-line", "line"),
              plate("s3", [20, 30], docks=[dock("ev-a", 20.0, 25.0)])]
    m = measured(tmp_path / "b", scenes, [(0, 30)],
                 evidence={"ev-a": {"species": "chart", "chart": {"shares": [1]}}})
    gate = row(FLOOR.rows(m, None, predates=False), "M35")
    assert gate.level == "PASS" and "3 chart forms" in gate.message
    assert f"the floor is {FLOOR.MIN_FORMS}" in gate.message


# ---------------------------------------------------------------- M36: the transforms

def test_m36_a_snap_from_a_dock_is_not_a_chart_to_chart(tmp_path: Path) -> None:
    scenes = [page("s1", [0, 10], enter="snap", page={"snap_from": "ev-a"}),
              page("s2", [10, 20], enter="spiral"), page("s3", [20, 30], enter="axes")]
    m = measured(tmp_path / "b", scenes, [(0, 30)])
    gate = row(FLOOR.rows(m, None, predates=False), "M36")
    assert m.chart_to == [] and gate.level == "FAIL" and "0 chart-to-chart transforms" in gate.message


def test_m36_a_morph_page_after_a_page_is_a_chart_to_chart(tmp_path: Path) -> None:
    scenes = [page("s1", [0, 10]), page("s2", [10, 20], enter="morph")]
    m = measured(tmp_path / "b", scenes, [(0, 20)])
    gate = row(FLOOR.rows(m, None, predates=False), "M36")
    assert m.chart_to == [("s2", "page enter morph after a ledger page")] and gate.level == "PASS"


def test_m36_a_morph_page_after_a_plate_is_not_one(tmp_path: Path) -> None:
    scenes = [plate("s1", [0, 10]), page("s2", [10, 20], enter="stamped")]
    assert measured(tmp_path / "b", scenes, [(0, 20)]).chart_to == []


def test_m36_counts_a_chart_to_species_by_its_verb(tmp_path: Path) -> None:
    scenes = [page("s1", [0, 10], species=[{"kind": "chart_to", "at": 4.0, "to": "rescale"}])]
    m = measured(tmp_path / "b", scenes, [(0, 10)])
    assert m.chart_to == [("s1", "species chart_to -> rescale")]
    assert row(FLOOR.rows(m, None, predates=False), "M36").level == "PASS"


# ---------------------------------------------------------------- M37: on screen, not entering

def test_m37_reads_a_held_dock_on_screen_where_the_enters_during_rule_does_not(tmp_path: Path) -> None:
    scenes = [plate("s1", [0, 30], docks=[dock("ev-a", 1.0, 25.0)])]
    m = measured(tmp_path / "b", scenes, [(0, 10), (10, 20), (20, 30)],
                 evidence={"ev-a": {"species": "photo"}})
    assert (m.dock_beats, m.enter_beats) == (3, 1)
    assert (m.docks_per_beat, m.enters_per_beat) == (1.0, 0.33)
    gate = row(FLOOR.rows(m, None), "M37")
    assert gate.level == "PASS" and "3 on screen, 1 entering" in gate.message


def test_m37_floor_rises_to_the_references_own_share(tmp_path: Path) -> None:
    cut = measured(tmp_path / "cut", [plate("s1", [0, 30], docks=[dock("ev-a", 1.0, 9.0)])],
                   [(0, 10), (10, 20), (20, 30)], evidence={"ev-a": {"species": "photo"}})
    ref = measured(tmp_path / "ref", [plate("s1", [0, 30], docks=[dock("ev-a", 1.0, 29.0)])],
                   [(0, 10), (10, 20), (20, 30)], evidence={"ev-a": {"species": "photo"}})
    assert (cut.docks_per_beat, ref.docks_per_beat) == (0.33, 1.0)
    assert row(FLOOR.rows(cut, None), "M37").level == "PASS"        # 0.33 clears E96's own 1/3
    beaten = row(FLOOR.rows(cut, ref), "M37")
    assert beaten.level == "FAIL" and "the floor is 1.00 = max(1/3, the reference's own)" in beaten.message


# ---------------------------------------------------------------- M38: the recipe coverage

PUNCH = {"id": "recipe:test-punch", "status": "proven", "window_s": 6.0, "members": [
    {"card": "plate_option:world", "offset_s": 0.0, "role": "the world arrives"},
    {"card": "species:punch", "offset_s": 1.0, "role": "the punch lands on the word"}]}


def test_m38_coverage_is_the_share_of_beats_a_fire_overlaps(tmp_path: Path) -> None:
    scenes = [plate("s1", [0, 10], species=[{"kind": "punch", "at": 1.0}]),
              plate("s2", [10, 20]), plate("s3", [20, 30])]
    m = measured(tmp_path / "b", scenes, [(0, 10), (10, 20), (20, 30)], recipes=[PUNCH])
    assert len(m.fires["recipe:test-punch"]) == 1 and m.recipe_beats == {0} and m.coverage == 0.33
    gate = row(FLOOR.rows(m, None), "M38")
    assert gate.level == "FAIL"
    assert f"the floor is {FLOOR.MIN_RECIPE_COVERAGE:.2f}" in gate.message
    assert "recipe:test-punch x1 (a decoration)" in gate.message
    # both readings in the one row (the P56 review): the floor is the spanning number, the other is printed beside it
    assert "coverage 0.33 spanning / 0.33 by the beat a fire starts in" in gate.message


def test_m38_passes_over_sixty_percent_and_names_a_recurring_recipe_without_the_decoration_note(
        tmp_path: Path) -> None:
    scenes = [plate("s1", [0, 10], species=[{"kind": "punch", "at": 1.0}]),
              plate("s2", [10, 20], species=[{"kind": "punch", "at": 11.0}]),
              plate("s3", [20, 30])]
    m = measured(tmp_path / "b", scenes, [(0, 10), (10, 20), (20, 30)], recipes=[PUNCH])
    gate = row(FLOOR.rows(m, None), "M38")
    assert m.coverage == 0.67 and gate.level == "PASS"
    assert "recipe:test-punch x2" in gate.message and "a decoration" not in gate.message


def test_m38_prints_the_references_own_coverage_beside_the_threshold(tmp_path: Path) -> None:
    thin = measured(tmp_path / "thin", [plate("s1", [0, 30])], [(0, 30)], recipes=[PUNCH])
    ref = measured(tmp_path / "ref", [plate("s1", [0, 30], species=[{"kind": "punch", "at": 1.0}])],
                   [(0, 30)], recipes=[PUNCH])
    gate = row(FLOOR.rows(thin, ref), "M38")
    assert gate.level == "FAIL" and "no proven recipe fires" in gate.message
    assert "measures 1.00" in gate.message


# ---------------------------------------------------------------- M39: narrative : chart

def test_m39_is_narrative_surfaces_over_chart_surfaces(tmp_path: Path) -> None:
    scenes = [plate("s1", [0, 10]), plate("s2", [10, 20], world={"kind": "clip", "asset_id": "c1"}),
              page("s3", [20, 30]), plate("s4", [30, 40], docks=[dock("ev-a", 31.0, 35.0)])]
    m = measured(tmp_path / "b", scenes, [(0, 40)], evidence={"ev-a": {"species": "chart"}})
    assert (m.plates, m.clips, m.pages, m.chart_docks) == (2, 1, 1, 1)
    gate = row(FLOOR.rows(m, None), "M39")
    assert m.narr_chart == 1.5 and gate.level == "PASS"
    assert "3 narrative = 2 plates + 1 clips / 2 chart = 1 pages + 1 chart docks" in gate.message


def test_m39_fails_when_the_charts_outnumber_the_narrative(tmp_path: Path) -> None:
    scenes = [plate("s1", [0, 10]), page("s2", [10, 20]), page("s3", [20, 30], variant="line")]
    m = measured(tmp_path / "b", scenes, [(0, 30)])
    gate = row(FLOOR.rows(m, None), "M39")
    assert m.narr_chart == 0.5 and gate.level == "FAIL" and "the floor is 1.00" in gate.message


# ---------------------------------------------------------------- M40 / M42: never a floor

def test_m40_is_a_judge_row_carrying_the_three_column_table(tmp_path: Path) -> None:
    m = measured(tmp_path / "b", [plate("s1", [0, 30])], [(0, 30)])
    gate = row(FLOOR.rows(m, None), "M40")
    assert gate.level == "JUDGE"
    assert "the reference is NOT on disk" in gate.message
    for name in ("distinct chart forms", "narrative : chart", "events / min", "builds : compositions"):
        assert name in gate.message
    assert "docs/agent-memory/operator/bravos-reference.md" in gate.message
    assert "6.0" in gate.message and "2.5" in gate.message


@pytest.mark.parametrize("scenes, beats", [
    ([plate("s1", [0, 30])], [(0, 30)]),                                     # 1 event in 30 s
    ([plate(f"s{i}", [i, i + 1], species=[{"kind": "punch", "at": i + 0.1}]) for i in range(40)],
     [(0, 40)]),                                                             # 80 events in 40 s
])
def test_m42_is_always_info_whatever_the_rate(tmp_path: Path, scenes: list, beats: list) -> None:
    m = measured(tmp_path / f"b{len(scenes)}", scenes, beats)
    gate = row(FLOOR.rows(m, None), "M42")
    assert gate.level == "INFO" and "never a floor" in gate.message


def test_the_registry_records_m42_as_info_only_and_m40_as_judge_only() -> None:
    records = [json.loads(l) for l in REGISTRY.read_text(encoding="utf-8").splitlines() if l.strip()]
    floor = {r["id"]: r for r in records if r["family"] == "floor"}
    assert sorted(floor) == list(FLOOR.ROW_ORDER)
    assert floor["M42"]["levels"] == ["INFO"]
    assert floor["M40"]["levels"] == ["JUDGE"]
    assert "FAIL" in floor["M37"]["levels"] and "FAIL" in floor["M39"]["levels"]


# ---------------------------------------------------------------- M41: the beat plan

def full_record(i: int, t0: float, t1: float) -> dict:
    return {"beat": i, "t0": t0, "t1": t1, "text": f"beat {i}", "acts": ["EXPLAINS"],
            "comparator": {"claim": "a claim", "compared_to": "the 2019 level", "series": "s", "source": "src"},
            "recipe": "recipe:test-punch", "why_none": "", "capabilities": ["species:punch"], "bound": {}}


def test_m41_warns_and_never_dies_when_there_is_no_plan_on_disk(tmp_path: Path) -> None:
    m = measured(tmp_path / "b", [plate("s1", [0, 30])], [(0, 10), (10, 20), (20, 30)])
    gate = row(FLOOR.rows(m, None), "M41")
    assert gate.level == "WARN" and "no beat plan on disk" in gate.message and "3 beats unplanned" in gate.message


def test_m41_passes_when_every_beat_has_a_record_with_a_comparator_and_a_recipe(tmp_path: Path) -> None:
    plan = [full_record(1, 0.0, 10.0), full_record(2, 10.0, 20.0)]
    m = measured(tmp_path / "b", [plate("s1", [0, 20])], [(0, 10), (10, 20)], plan=plan)
    gate = row(FLOOR.rows(m, None), "M41")
    assert gate.level == "PASS" and "covers all 2 beats (2 records)" in gate.message


def test_m41_names_its_three_gap_kinds(tmp_path: Path) -> None:
    missing_comparator = full_record(2, 10.0, 20.0) | {"comparator": {"claim": "c", "compared_to": " "}}
    no_recipe_no_reason = full_record(3, 20.0, 30.0) | {"recipe": None, "why_none": ""}
    m = measured(tmp_path / "b", [plate("s1", [0, 40])], [(0, 10), (10, 20), (20, 30), (30, 40)],
                 plan=[full_record(1, 0.0, 10.0), missing_comparator, no_recipe_no_reason])
    gate = row(FLOOR.rows(m, None), "M41")
    assert gate.level == "FAIL"
    assert "beat 2 compares to nothing" in gate.message
    assert "beat 3 has no recipe and no why_none" in gate.message
    assert "beat 4 has no record" in gate.message


def test_m41_reads_a_plan_numbered_from_zero_through_its_own_t0(tmp_path: Path) -> None:
    plan = [full_record(0, 0.0, 10.0), full_record(1, 10.0, 20.0)]
    m = measured(tmp_path / "b", [plate("s1", [0, 20])], [(0, 10), (10, 20)], plan=plan)
    assert row(FLOOR.rows(m, None), "M41").level == "PASS"


# ---------------------------------------------------------------- HG1 (A): the enumerated set

def test_the_predates_e96_set_is_the_four_cuts_pinned_to_their_timelines_sha256() -> None:
    assert sorted(FLOOR.PREDATES_E96) == [("japan-tariff-trick", "build-short"),
                                          ("normal-for-which-bridge", "review-v1"),
                                          ("steel-and-paper", "build-f"),
                                          ("tokyo-tea-break", "build-short.v2")]
    source = Path(FLOOR.__file__).read_text(encoding="utf-8")
    assert "ADDING A BUILD TO THIS TABLE NEEDS A RULING" in source
    for (project, build), sha in sorted(FLOOR.PREDATES_E96.items()):
        directory = PROJECTS / project / build
        if not directory.is_dir() or not list(directory.glob("*.timeline.json")):
            pytest.skip(f"no compiled timeline in {directory} (the gitignored builds are not in this checkout)")
        on_disk = hashlib.sha256(FLOOR.timeline_path(directory).read_bytes()).hexdigest()
        assert on_disk == sha, f"{project}/{build} was re-authored - the exemption needs a ruling, not a rename"


def test_a_re_authored_timeline_in_the_same_dir_stops_predating(tmp_path: Path) -> None:
    if not JAPAN.is_dir() or not list(JAPAN.glob("*.timeline.json")):
        pytest.skip("no compiled timeline in the Japan build")
    assert FLOOR.predates_e96(JAPAN) and FLOOR.predates_e96(THIN)
    copy_dir = tmp_path / "japan-tariff-trick/build-short"
    copy_dir.mkdir(parents=True)
    (copy_dir / "japan-short.timeline.json").write_bytes(FLOOR.timeline_path(JAPAN).read_bytes())
    assert FLOOR.predates_e96(copy_dir)                       # the same BYTES, wherever the copy sits
    (copy_dir / "japan-short.timeline.json").write_text('{"scenes": []}', encoding="utf-8")
    assert not FLOOR.predates_e96(copy_dir)                   # re-authored in the same dir: no exemption
    assert not FLOOR.predates_e96(tmp_path / "build-short")   # no timeline to hash at all


def test_only_m35_and_m36_go_info_on_a_predating_build(tmp_path: Path) -> None:
    m = measured(tmp_path / "b", [plate("s1", [0, 30])], [(0, 30)])
    info = {g.id for g in FLOOR.rows(m, None, predates=True) if g.level == "INFO"}
    assert info == {"M35", "M36", "M42"}                      # M42 is INFO by its own rule, always


# ---------------------------------------------------------------- the four cuts on disk

def floor_rows(build_dir: Path) -> dict:
    if not build_dir.is_dir() or not list(build_dir.glob("*.timeline.json")):
        pytest.skip(f"no compiled timeline in {build_dir} (the gitignored builds are not in this checkout)")
    gates, m, ref = FLOOR.run(build_dir)
    return {g.id: g for g in gates} | {"_m": m, "_ref": ref}


def test_japan_the_reference_reproduces_t2s_measures() -> None:
    r = floor_rows(JAPAN)
    assert r["_m"].n_beats == 25
    assert r["M35"].level == "INFO" and "2 chart forms" in r["M35"].message
    assert "predates E96 (measured 2)" in r["M35"].message
    assert r["M36"].level == "INFO" and "0 chart-to-chart transforms" in r["M36"].message
    assert "predates E96 (measured 0)" in r["M36"].message
    assert r["M37"].level == "PASS" and "docks on 0.36 of 25 beats" in r["M37"].message
    assert r["M39"].level == "PASS" and "narrative : chart 1.00" in r["M39"].message
    assert r["M42"].level == "INFO" and "28.1 events/min" in r["M42"].message
    assert r["M41"].level == "WARN" and "no beat plan on disk" in r["M41"].message


def test_japans_m38_row_carries_the_threshold_and_its_own_measured_coverage() -> None:
    r = floor_rows(JAPAN)
    assert r["M38"].level in ("PASS", "FAIL")                 # the number moves while T8 re-members three proofs
    assert "the floor is 0.60" in r["M38"].message
    assert f"the reference {r['_ref'].name} measures {r['_ref'].coverage:.2f}" in r["M38"].message
    assert (f"proven-recipe coverage {r['_m'].coverage:.2f} spanning / {r['_m'].coverage_start:.2f} "
            f"by the beat a fire starts in") in r["M38"].message


def test_tokyo_fails_the_dock_floor_under_both_readings() -> None:
    r = floor_rows(TOKYO)
    assert "2 chart forms" in r["M35"].message and "0 chart-to-chart" in r["M36"].message
    assert r["M37"].level == "FAIL" and "docks on 0.28 of 25 beats" in r["M37"].message
    assert r["M39"].level == "PASS" and "narrative : chart 1.00" in r["M39"].message


def test_steel_the_long_form_carries_five_forms_and_docks_on_four_fifths_of_its_beats() -> None:
    r = floor_rows(STEEL)
    assert "5 chart forms" in r["M35"].message and r["_m"].n_beats == 240
    assert r["M37"].level == "PASS" and "docks on 0.80 of 240 beats" in r["M37"].message
    assert "narrative : chart 2.34" in r["M39"].message


def test_the_thin_one_shot_fails_the_floors_and_exits_one() -> None:
    r = floor_rows(THIN)
    assert "1 chart forms" in r["M35"].message and "0 chart-to-chart" in r["M36"].message
    assert r["M37"].level == "FAIL" and "docks on 0.00 of 19 beats" in r["M37"].message
    assert r["M39"].level == "FAIL" and "narrative : chart 0.20" in r["M39"].message
    assert r["M38"].level == "FAIL" and "no proven recipe fires" in r["M38"].message
    assert "17.9 events/min" in r["M42"].message
    done = subprocess.run([sys.executable, str(ROOT / "content/video_engine/scripts/gate_one_shot_floor.py"),
                           str(THIN)], capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert done.returncode == 1, done.stdout + done.stderr
    # the FAIL COUNT is not pinned (M38's number moves while T8 re-members three proofs): the verdict is
    assert re.search(r"^RESULT: [1-9]\d* FAIL", done.stdout, re.M), done.stdout


def test_every_printed_row_parses_under_self_watchs_own_pattern() -> None:
    if not JAPAN.is_dir():
        pytest.skip("no compiled timeline in the Japan build")
    gates, m, ref = FLOOR.run(JAPAN)
    text = FLOOR.report_text(gates, m, ref)
    parsed = {mt.group(2) for mt in (ROW_RE.match(line) for line in text.splitlines()) if mt}
    assert parsed == set(FLOOR.ROW_ORDER)
    result = [l for l in text.splitlines() if l.startswith("RESULT:")]
    assert len(result) == 1 and re.match(r"^RESULT: \d+ FAIL / 1 WARN / \d+ PASS / 1 JUDGE / 3 INFO$", result[0])
    assert sum(int(n) for n in re.findall(r"(\d+) (?:FAIL|WARN|PASS|JUDGE|INFO)", result[0])) == len(FLOOR.ROW_ORDER)


# ---------------------------------------------------------------- the P56 review (2026-09-13)

SPANNING = {"id": "recipe:test-span", "status": "proven", "window_s": 30.0, "members": [
    {"card": "plate_option:world", "offset_s": 0.0, "role": "the world arrives"},
    {"card": "species:punch", "offset_s": [0.0, 25.0], "role": "the punch lands a beat or three later"}]}


def test_m38_prints_the_beat_a_fire_starts_in_beside_the_spanning_reading(tmp_path: Path) -> None:
    # Arrange: ONE fire, open at 0.0 and closed at 21.0 - it spans three beats and starts in the first
    m = measured(tmp_path / "b", [plate("s1", [0, 30], species=[{"kind": "punch", "at": 21.0}])],
                 [(0, 10), (10, 20), (20, 30)], recipes=[SPANNING])

    # Act
    gate = row(FLOOR.rows(m, None), "M38")

    # Assert
    assert (m.recipe_beats, m.coverage) == ({0, 1, 2}, 1.0)
    assert (m.recipe_start_beats, m.coverage_start) == ({0}, 0.33)
    assert "coverage 1.00 spanning / 0.33 by the beat a fire starts in" in gate.message
    assert gate.level == "PASS"                    # HG1/HG2 as ruled: the floor stays on the spanning number


def held_build(tmp: Path) -> FLOOR.Measures:
    """Two plates, each with a chart dock on screen and a punch: M37, M38 and M39 all clear their own numbers."""
    scenes = [plate("s1", [0, 10], species=[{"kind": "punch", "at": 1.0}], docks=[dock("ev-a", 0.0, 10.0)]),
              plate("s2", [10, 20], species=[{"kind": "punch", "at": 11.0}], docks=[dock("ev-b", 10.0, 20.0)])]
    return measured(tmp, scenes, [(0, 10), (10, 20)], recipes=[PUNCH],
                    evidence={"ev-a": {"species": "chart"}, "ev-b": {"species": "chart"}})


def test_an_unreadable_reference_warns_on_every_reference_row_and_holds_the_rules_own_number(tmp_path: Path) -> None:
    # Arrange
    m = held_build(tmp_path / "b")

    # Act
    gates = FLOOR.rows(m, None, predates=False, ref_warn="content/video_engine/projects/nope/build-x")

    # Assert
    assert {g.id for g in gates if g.level == "WARN"} == {"M37", "M38", "M39", "M41"}   # M41: no beat plan
    for rid in ("M37", "M38", "M39"):
        message = row(gates, rid).message
        assert "not readable" in message and "floor held at the rule's own number" in message
        assert row(gates, rid).level == "WARN"     # the rule's own number is cleared: WARN, never a silent PASS


def test_a_bogus_reference_still_prints_the_rows_and_a_result_line(tmp_path: Path) -> None:
    # Arrange
    built = build(tmp_path / "b", [plate("s1", [0, 30], species=[{"kind": "punch", "at": 1.0}])], [(0, 30)])

    # Act
    done = subprocess.run([sys.executable, str(ROOT / "content/video_engine/scripts/gate_one_shot_floor.py"),
                           str(built), "--reference", str(tmp_path / "nope")],
                          capture_output=True, text=True, encoding="utf-8", errors="replace")

    # Assert: the run goes on - every row prints, the three reference rows say the reference was not readable
    assert "NOT readable" in done.stdout, done.stdout + done.stderr
    assert re.search(r"^RESULT: \d+ FAIL / \d+ WARN / ", done.stdout, re.M), done.stdout
    printed = {mt.group(2): mt.group(3) for mt in (ROW_RE.match(line) for line in done.stdout.splitlines()) if mt}
    assert set(printed) == set(FLOOR.ROW_ORDER)
    for rid in ("M37", "M38", "M39"):
        assert "not readable" in printed[rid] and "the rule's own number" in printed[rid], printed[rid]


def test_a_dock_with_no_window_is_held_for_its_whole_scene(tmp_path: Path) -> None:
    # Arrange: a partial timeline - the dock states no enter and no exit, so it holds its scene [0, 9]
    m = measured(tmp_path / "b", [plate("s1", [0, 9], docks=[{"slide": "ev-a"}]), plate("s2", [9, 20])],
                 [(0, 10), (10, 20)], evidence={"ev-a": {"species": "chart"}})

    # Act / Assert
    assert m.docks == [{"scene": "s1", "slide": "ev-a", "enter": 0.0, "exit": 9.0, "chart": True}]
    assert m.dock_beats == 1 and row(FLOOR.rows(m, None, predates=False), "M37").level == "PASS"


# ---------------------------------------------------------------- the catalogue is ensured (P63 T2)

import docs_layers as DL  # noqa: E402  (the table the gate ensures the catalogue through)

BUILDER = """import json, sys
from pathlib import Path

repo = Path(sys.argv[sys.argv.index("--repo") + 1])
(repo / "docs").mkdir(parents=True, exist_ok=True)
(repo / "docs/EFFECTS-CATALOG.jsonl").write_text(
    json.dumps({"id": "recipe:rebuilt", "axis": "recipe", "title": "The rebuilt recipe",
                "status": "proven", "window_s": 2.0, "members": [], "aliases": []}) + "\\n", encoding="utf-8")
(repo / "docs/EFFECTS-CATALOG.md").write_text("# catalogue", encoding="utf-8")
print("fake catalogue: written")
"""

STALE_LINE = '{"id": "recipe:stale", "axis": "recipe", "title": "The stale recipe", "status": "proven", "window_s": 2.0, "members": [], "aliases": []}'


@pytest.fixture()
def fake_repo(tmp_path: Path, monkeypatch) -> Path:
    """A miniature repo whose catalogue has a FAKE builder; `FLOOR.REPO` points at it for the test.

    The real checkout is never rebuilt by a test, and the tree the gate's other fixtures use has no
    builders in it at all - `ensure` is a no-op there by construction."""
    repo = tmp_path / "repo"
    scripts = repo / DL.SCRIPTS_REL
    scripts.mkdir(parents=True)
    (scripts / DL.SENTINEL).write_text("import sys", encoding="utf-8")   # the sentinel: ensure is live
    (scripts / "build_effects_catalog.py").write_text(BUILDER, encoding="utf-8")
    (repo / "docs").mkdir()
    (repo / FLOOR.CATALOG_REL).write_text(STALE_LINE + "\n", encoding="utf-8")
    monkeypatch.setattr(FLOOR, "REPO", repo)
    return repo


def test_a_stale_catalogue_is_rebuilt_before_the_floor_reads_it_when_it_waits(fake_repo: Path) -> None:
    """P64 T1 renamed this from `test_a_stale_catalogue_is_rebuilt_before_the_floor_reads_it`: the gate
    runs on what is on disk by default and names the staleness in its header; `--wait` is this path."""
    # Act
    rebuilt = FLOOR.ensure_catalog(fake_repo / FLOOR.CATALOG_REL, wait=True)

    # Assert: the recipes the gate goes on to read are the rebuilt ones
    assert rebuilt == ["docs-index", "effects-catalog"]          # the sentinel IS docs-index's builder
    assert [r["id"] for r in FLOOR.load_recipes(fake_repo / FLOOR.CATALOG_REL)] == ["recipe:rebuilt"]
    assert DL.stored_digest(fake_repo, FLOOR.CATALOG_LAYER)
    assert FLOOR.ensure_catalog(fake_repo / FLOOR.CATALOG_REL, wait=True) == []   # nothing moved


def test_the_default_builds_nothing_and_the_staleness_goes_in_the_report_header(fake_repo: Path) -> None:
    """The verdict depends on a current catalogue, so the reader is TOLD how current it was - and the
    gate still runs on what is there (P64 T1: nothing blocks)."""
    # Act
    rebuilt = FLOOR.ensure_catalog(fake_repo / FLOOR.CATALOG_REL)
    note = FLOOR.catalog_note(fake_repo / FLOOR.CATALOG_REL)

    # Assert
    assert rebuilt == [] and not (fake_repo / DL.CACHE_REL).exists()
    assert note == ("[layers] stale: docs-index, effects-catalog "
                    "(no refresh running - run build_docs_layers.py --refresh)")
    assert [r["id"] for r in FLOOR.load_recipes(fake_repo / FLOOR.CATALOG_REL)] == ["recipe:stale"]
    assert FLOOR.catalog_note(Path("somewhere/else.jsonl")) is None      # not this repo's artifact


def test_a_catalogue_that_is_not_this_repos_own_artifact_is_never_rebuilt(fake_repo: Path,
                                                                          tmp_path: Path) -> None:
    # Arrange: the caller's own file, outside the repo
    mine = tmp_path / "mine.jsonl"
    mine.write_text(STALE_LINE + "\n", encoding="utf-8")

    # Act
    rebuilt = FLOOR.ensure_catalog(mine, wait=True)

    # Assert
    assert rebuilt == []
    assert not (fake_repo / DL.CACHE_REL).exists()
    assert [r["id"] for r in FLOOR.load_recipes(mine)] == ["recipe:stale"]


def test_a_tree_with_no_builders_in_it_is_never_rebuilt(tmp_path: Path, monkeypatch) -> None:
    # Arrange: every other fixture in this file is such a tree
    repo = tmp_path / "bare"
    (repo / "docs").mkdir(parents=True)
    (repo / FLOOR.CATALOG_REL).write_text(STALE_LINE + "\n", encoding="utf-8")
    monkeypatch.setattr(FLOOR, "REPO", repo)

    # Act / Assert
    assert FLOOR.ensure_catalog(repo / FLOOR.CATALOG_REL, wait=True) == []
    assert not (repo / DL.CACHE_REL).exists()


def test_a_builder_that_fails_is_named_and_the_floor_still_runs(fake_repo: Path, capsys) -> None:
    # Arrange
    (fake_repo / DL.SCRIPTS_REL / "build_effects_catalog.py").write_text(
        'import sys' + "\n" + 'print("fake: the card is malformed", file=sys.stderr)' + "\n"
        + 'sys.exit(2)' + "\n", encoding="utf-8")

    # Act
    rebuilt = FLOOR.ensure_catalog(fake_repo / FLOOR.CATALOG_REL, wait=True)

    # Assert: the gate reads the catalogue as it sits, and says what happened
    assert rebuilt == []
    assert [r["id"] for r in FLOOR.load_recipes(fake_repo / FLOOR.CATALOG_REL)] == ["recipe:stale"]
    assert capsys.readouterr().err.strip().endswith(
        "[layers] effects-catalog failed to rebuild: fake: the card is malformed")
