"""Ledger page spec (P35 T2, doc 29 s9.26): the series.json -> page spec contract.

Real-file tests skip when the Steel and Paper evidence objects are not on disk.
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
import ledger_page as L  # noqa: E402

OBJECTS = ROOT / "content/video_engine/projects/systems-and-blowups/steel-and-paper/evidence/objects"
DIVERGENCE = OBJECTS / "ev-divergence-v1.series.json"
TRIM = OBJECTS / "ev-trim-proof-v1.series.json"
SCORECARD = OBJECTS / "ev-test-scorecard-v1.series.json"
needs_objects = pytest.mark.skipif(
    not (DIVERGENCE.exists() and TRIM.exists() and SCORECARD.exists()),
    reason="steel-and-paper evidence objects not on disk",
)

TRIM_VALUE_STRINGS = ["3.9", "12.4", "5.3", "10.5", "11.3", "10.9", "8.7", "13.8"]


def _race(periods: bool = True) -> dict:
    series = {
        "title": "Memory-maker share", "src": "Company filings, our count",
        "series": [
            {"name": "hynix", "values": [10, 20, 30, 40], "color": "crimson"},
            {"name": "Micron", "values": [15, 18, 25, 35], "color": "teal"},
            {"name": "Samsung", "values": [40, 35, 30, 25], "color": "cobalt"},
        ],
    }
    return {**series, "periods": ["2023", "2024", "2025", "2026"]} if periods else series


def _bars(values: list, **extra) -> dict:
    return {
        "title": "t", "src": "our source",
        "bars": [{"label": f"L{i}", "value": v, "color": "crimson"} for i, v in enumerate(values)],
        **extra,
    }


def _write(tmp_path: Path, name: str, data: dict) -> Path:
    path = tmp_path / name
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


# --- real files --------------------------------------------------------------

@needs_objects
def test_divergence_line_is_dense_line_with_series_verbatim():
    series = L.load_series(DIVERGENCE)
    assert L.validate(series, "line") == []
    spec = L.build_spec(series, "line")
    assert spec["builder"] == "dense-line" and spec["variant"] == "line"
    assert spec["series"] == series["series"] and spec["series"] is not series["series"]
    assert spec["series"][0]["pts"][0] == ["2025.6680355920603", "100.0"]   # tokens, not floats
    assert spec["source"] == series["src"] and spec["source"]
    assert spec["axes"]["log"] is True and "xticks" in spec["axes"]
    assert spec["labels"] == [s["name"] for s in series["series"]]
    assert spec["values"] == [] and spec["value_strings"] == []


@needs_objects
def test_trim_proof_bars_is_story_with_verbatim_value_strings():
    series = L.load_series(TRIM)
    assert L.validate(series, "bars") == []
    spec = L.build_spec(series, "bars", emphasize=7)
    assert spec["builder"] == "story"
    assert len(spec["values"]) == 8 and spec["values"][0] == 3.9
    assert spec["value_strings"] == TRIM_VALUE_STRINGS
    assert spec["labels"][0] == "Oct '24" and spec["colors"][5] == "teal"
    assert spec["emphasize"] == 7
    assert L.build_spec(series, "bars", emphasize=99)["emphasize"] == 7   # clamped to the last datum
    assert L.build_spec(series, "bars", emphasize=-3)["emphasize"] == 0
    assert L.build_spec(series, "bars")["emphasize"] is None


@needs_objects
def test_scorecard_checklist_is_rejected_as_unchartable(capsys):
    series = L.load_series(SCORECARD)
    errors = L.validate(series, "bars")
    assert any("no chartable values" in e for e in errors), errors
    assert L.main([str(SCORECARD), "--variant", "bars"]) == L.EXIT_INVALID
    assert "no chartable values" in capsys.readouterr().err


@needs_objects
def test_main_writes_spec_and_summary(tmp_path, capsys):
    out = tmp_path / "trim.page.json"
    assert L.main([str(TRIM), "--variant", "bars", "--emphasize", "7", "--out", str(out)]) == 0
    spec = json.loads(out.read_text(encoding="utf-8"))
    assert spec["schema_version"] == "ledger_page.v1" and spec["surface"] == "page"
    assert spec["value_strings"] == TRIM_VALUE_STRINGS and spec["quiet_zone"] == "right"
    line = capsys.readouterr().out.strip()
    assert line.startswith("story bars 8 values source=")


# --- race ----------------------------------------------------------------------

def test_race_with_periods_builds_ranked_rows():
    series = _race()
    assert L.validate(series, "race") == []
    assert L.pick_builder(series, "race") == "race"
    spec = L.build_spec(series, "race", emphasize=0)
    assert spec["periods"] == ["2023", "2024", "2025", "2026"]
    assert spec["labels"] == ["hynix", "Micron", "Samsung"]
    assert spec["values"][2] == [40.0, 35.0, 30.0, 25.0]
    assert spec["value_strings"][0] == ["10", "20", "30", "40"]
    assert spec["colors"] == ["crimson", "teal", "cobalt"]


def test_race_without_periods_is_an_error_naming_periods():
    errors = L.validate(_race(periods=False), "race")
    assert errors and all("periods" in e for e in errors), errors


def test_race_derives_periods_from_a_shared_x_grid():
    series = {"title": "t", "src": "s", "series": [
        {"name": "a", "color": "teal", "pts": [[2024, 1], [2025, 2], [2026, 3]]},
        {"name": "b", "color": "crimson", "pts": [[2024, 3], [2025, 2], [2026, 1]]},
    ]}
    assert L.validate(series, "race") == []
    spec = L.build_spec(series, "race")
    assert spec["periods"] == [2024, 2025, 2026] and spec["values"][1] == [3.0, 2.0, 1.0]


def test_race_rejects_misaligned_values():
    series = _race()
    series["series"][1] = {**series["series"][1], "values": [1, 2]}
    assert any("2 values for 4 periods" in e for e in L.validate(series, "race"))


# --- decline / progress --------------------------------------------------------

def test_decline_takes_first_and_last_as_start_and_end():
    series = _bars([88.0, 61.5, 28])
    assert L.validate(series, "decline") == []
    spec = L.build_spec(series, "decline")
    assert spec["builder"] == "decline"
    assert spec["start"] == {"label": "L0", "value": 88.0, "value_string": "88.0"}
    assert spec["end"] == {"label": "L2", "value": 28.0, "value_string": "28"}


def test_decline_from_a_single_dense_series_and_rejects_two_metrics():
    one = {"title": "t", "src": "s", "series": [
        {"name": "yield", "color": "crimson", "pts": [[i, 100 - i] for i in range(20)]}]}
    assert L.validate(one, "decline") == []
    spec = L.build_spec(one, "decline")
    assert spec["start"]["value"] == 100.0 and spec["end"]["value"] == 81.0
    two = {**one, "series": one["series"] * 2}
    assert any("exactly one metric" in e for e in L.validate(two, "decline"))
    assert any("start and an end" in e for e in L.validate(_bars([5]), "decline"))


def test_progress_out_of_range_needs_a_denominator():
    errors = L.validate(_bars([28, 140]), "progress")
    assert errors and "140" in errors[0] and "0..100" in errors[0] and "denominator" in errors[0]
    with_denominator = _bars([28, 140], denominator=200)
    assert L.validate(with_denominator, "progress") == []
    assert L.build_spec(with_denominator, "progress")["denominator"] == "200"
    assert any("outside 0..200" in e for e in L.validate(_bars([250], denominator=200), "progress"))


# --- source line, builder pick, determinism ------------------------------------

def test_missing_src_is_a_hard_failure(tmp_path, capsys):
    series = {"title": "t", "bars": [{"label": "a", "value": 1, "color": "teal"}]}
    assert any("src" in e for e in L.validate(series, "bars"))
    path = _write(tmp_path, "no-src.series.json", series)
    assert L.main([str(path), "--variant", "bars"]) == 2
    err = capsys.readouterr().err
    assert "no-src.series.json" in err and "source" in err


def test_pick_builder_matrix():
    short = {"title": "t", "src": "s", "series": [
        {"name": "a", "color": "teal", "pts": [[i, i] for i in range(6)]}]}
    long = {**short, "series": [{**short["series"][0], "pts": [[i, i] for i in range(13)]}]}
    assert L.pick_builder(short, "line") == "story"
    assert L.pick_builder(long, "line") == "dense-line"
    assert L.pick_builder({**short, "series": short["series"] * 2}, "line") == "dense-line"
    assert L.pick_builder({**_bars([1, 2]), "series": short["series"]}, "bars") == "combo"
    assert L.pick_builder(_bars([1, 2, 3]), "line") == "story"


def test_short_series_as_a_story_line_and_the_story_ceiling():
    short = {"title": "t", "src": "s", "series": [
        {"name": "a", "color": "teal", "pts": [[2024, 1.5], [2025, 2.25]]}]}
    spec = L.build_spec(short, "line")
    assert spec["builder"] == "story" and spec["labels"] == ["2024", "2025"]
    assert spec["value_strings"] == ["1.5", "2.25"] and spec["colors"] == ["teal", "teal"]
    assert any("ceiling is 12" in e for e in L.validate(_bars(list(range(13))), "bars"))


def test_combo_carries_both_story_values_and_the_series():
    series = {**_bars([1, 2]), "series": [
        {"name": "a", "color": "teal", "pts": [[0, 1], [1, 2]]}], "ylabel": "y"}
    spec = L.build_spec(series, "bars")
    assert spec["builder"] == "combo" and spec["value_strings"] == ["1", "2"]
    assert spec["series"] == series["series"] and spec["axes"] == {"ylabel": "y"}


def test_value_strings_keep_the_file_token_never_rerounded(tmp_path):
    path = tmp_path / "x.series.json"
    path.write_text('{"title":"t","src":"s","bars":[{"label":"a","value":3.90,"color":"teal"},'
                    '{"label":"b","value":0.1,"color":"teal"}]}', encoding="utf-8")
    spec = L.build_spec(L.load_series(path), "bars")
    assert spec["value_strings"] == ["3.90", "0.1"] and spec["values"] == [3.9, 0.1]
    assert L.main([str(path), "--variant", "bars"]) == 0           # default --out: beside the input
    assert json.loads((tmp_path / "x.page.json").read_text(encoding="utf-8"))["value_strings"] == ["3.90", "0.1"]


def test_build_spec_is_deterministic_and_never_mutates_the_input():
    series = _race()
    before = copy.deepcopy(series)
    assert L.build_spec(series, "race", 1, "left") == L.build_spec(series, "race", 1, "left")
    assert series == before
    with pytest.raises(ValueError):
        L.build_spec(series, "race", quiet_zone="middle")


# --- T5: the specs the race / decline / combo builders consume ------------------

RACE_FILE = OBJECTS / "ev-memory-share-race-v1.series.json"
SMH = OBJECTS / "ev-smh-drawdown-v3.series.json"


def test_placeholder_figures_never_build_a_page(tmp_path, capsys):
    series = {**_race(), "status": "SOURCES-TO-VERIFY", "placeholder": True}
    errors = L.validate(series, "race")
    assert any("placeholder" in e and "SOURCES-TO-VERIFY" in e for e in errors), errors
    path = _write(tmp_path, "ph.series.json", series)
    assert L.main([str(path), "--variant", "race"]) == L.EXIT_INVALID
    assert "placeholder" in capsys.readouterr().err
    assert L.validate({**series, "placeholder": False}, "race") == []   # only the literal true refuses


@pytest.mark.skipif(not RACE_FILE.exists(), reason="race series not on disk")
def test_memory_share_race_file_is_flagged_until_sourced():
    series = L.load_series(RACE_FILE)
    assert series["status"] == "SOURCES-TO-VERIFY" and series["placeholder"] is True
    assert "TrendForce" in series["src"] and len(series["periods"]) >= L.RACE_MIN_PERIODS
    assert any("placeholder" in e for e in L.validate(series, "race"))


def test_race_spec_rows_align_with_periods_for_the_builder():
    spec = L.build_spec(_race(), "race")
    n = len(spec["periods"])
    assert spec["builder"] == "race" and n == 4
    for values, strings in zip(spec["values"], spec["value_strings"]):
        assert len(values) == n == len(strings)
        assert all(isinstance(v, float) for v in values)
    assert spec["emphasize"] is None                       # the leader is decided by the data, per frame
    assert spec["labels"] == ["hynix", "Micron", "Samsung"]


@pytest.mark.skipif(not SMH.exists(), reason="SMH drawdown series not on disk")
def test_smh_drawdown_is_a_decline_with_verbatim_endpoints():
    series = L.load_series(SMH)
    assert L.validate(series, "decline") == []
    spec = L.build_spec(series, "decline")
    assert spec["builder"] == "decline"
    pts = series["series"][0]["pts"]
    assert spec["start"] == {"label": pts[0][0], "value": float(pts[0][1]), "value_string": pts[0][1]}
    assert spec["end"] == {"label": pts[-1][0], "value": float(pts[-1][1]), "value_string": pts[-1][1]}
    assert len(spec["values"]) == len(pts) and min(spec["values"]) < 0


def test_decline_from_bars_keeps_the_tokens_the_file_wrote(tmp_path):
    path = tmp_path / "d.series.json"
    path.write_text('{"title":"t","src":"s","bars":[{"label":"peak","value":88.0,"color":"crimson"},'
                    '{"label":"mid","value":61.50,"color":"crimson"},{"label":"floor","value":28,"color":"crimson"}]}',
                    encoding="utf-8")
    spec = L.build_spec(L.load_series(path), "decline")
    assert spec["start"]["value_string"] == "88.0" and spec["end"]["value_string"] == "28"
    assert spec["value_strings"] == ["88.0", "61.50", "28"] and spec["values"] == [88.0, 61.5, 28.0]


def test_combo_spec_carries_bars_and_the_line_tokens_for_the_builder(tmp_path):
    path = tmp_path / "c.series.json"
    path.write_text('{"title":"t","src":"s","ylabel":"$bn",'
                    '"bars":[{"label":"Q1","value":8.0,"color":"deemph"},{"label":"Q2","value":12.5,"color":"deemph"}],'
                    '"series":[{"name":"margin","color":"cobalt","pts":[[1,2.10],[2,3.4]]}]}', encoding="utf-8")
    spec = L.build_spec(L.load_series(path), "bars", emphasize=5)
    assert spec["builder"] == "combo" and spec["emphasize"] == 1        # clamped to the last bar
    assert spec["value_strings"] == ["8.0", "12.5"] and spec["labels"] == ["Q1", "Q2"]
    assert spec["series"][0]["pts"] == [[1, "2.10"], [2, "3.4"]]         # the y tokens verbatim (ints stay ints)
    assert spec["axes"] == {"ylabel": "$bn"}
