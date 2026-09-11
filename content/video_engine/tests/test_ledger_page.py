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

TRIM_VALUE_STRINGS = ["-3.9", "-12.4", "-5.3", "-10.5", "-11.3", "10.9", "-8.7", "-13.8"]   # signed: a drop is a bar going down (E28)


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
    assert len(spec["values"]) == 8 and spec["values"][0] == -3.9
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
    lines = capsys.readouterr().out.strip().splitlines()
    assert lines[-1].startswith("story bars 8 values source=")
    assert any(l.strip().startswith("[JUDGE]") and "uneven gaps" in l for l in lines[:-1]), lines   # E28: the uneven date axis is surfaced


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


def test_badges_ride_on_the_page_synced_to_the_series_labels():
    # operator 2026-09-03: 'we need the badges back' - the dock's pills, keyed by accent, values from the series itself
    div = L.load_series(DIVERGENCE)
    spec = L.build_spec(div, "line", None, "right")
    assert spec["badges"] and all(set(b) == {"label", "value", "tag", "accent", "inline"} for b in spec["badges"])
    assert all(b["inline"] for b in spec["badges"])   # every divergence badge keys a line: a dynamic label, not a rail pill
    by_accent = {b["accent"]: b["value"] for b in spec["badges"]}
    labels = {s["color"]: str(s.get("label", "")).split()[0] for s in div["series"] if s.get("label")}
    assert by_accent["coral"] == labels["crimson"] and by_accent["teal"] == labels["teal"]   # synced, never authored twice
    extra = L.badges_for(div, [{"label": "X", "value": "stale", "tag": "t", "accent": "cobalt"}])
    assert extra[-1]["value"] == labels["cobalt"]
    assert L.build_spec(L.load_series(TRIM), "bars", 7, "right")["badges"][0]["value"] == "7 of 8"


def test_a_badge_naming_another_line_is_a_swapped_label_e28():
    # operator 2026-09-03: the +613% line was labelled MEGA-CAP TECH while its badge said MEMORY BUILDERS
    div = L.load_series(DIVERGENCE)
    assert not L.badge_key_conflicts(div)
    swapped = json.loads(json.dumps(div))
    by = {s["color"]: s for s in swapped["series"]}
    by["crimson"]["name"], by["deemph"]["name"] = by["deemph"]["name"], by["crimson"]["name"]
    errs = L.badge_key_conflicts(swapped)
    assert errs and "swapped label" in errs[0] and "MEMORY" in errs[0], errs
    assert any("swapped label" in e for e in L.validate(swapped, "line"))
    dock = [{"label": "MEMORY BUILDERS", "value": "+601%", "tag": "our layer", "accent": "coral"}]
    assert not L.badge_key_conflicts(div, dock) and L.badge_key_conflicts(swapped, dock)


def test_sign_hidden_in_a_note_is_refused_e28():
    # operator 2026-09-03: 'every bar appears to be positive at a glance, and the negative move is the tallest bar'
    series = {"title": "t", "src": "s", "bars": [{"label": "a", "value": "3.9", "note": "-4%"}, {"label": "b", "value": "10.9", "note": "+11%"}]}
    errors = L.validate(series, "bars")
    assert len(errors) == 1 and "sign lives in the note" in errors[0] and "'a'" in errors[0], errors
    signed = {**series, "bars": [{**series["bars"][0], "value": "-3.9"}, series["bars"][1]]}
    assert not L.validate(signed, "bars")
    assert not L.validate(L.load_series(TRIM), "bars")


def test_uneven_date_axis_is_a_judge_row_naming_the_selection_rule_e28():
    trim = L.load_series(TRIM)
    notes = L.review_notes(trim)
    assert len(notes) == 1 and "uneven gaps" in notes[0] and "selection rule declared" in notes[0], notes
    assert L.build_spec(trim, "bars", 7, "right")["judge"] == notes
    bare = {**trim}; bare.pop("selection")
    assert "no `selection` rule" in L.review_notes(bare)[0]
    even = {**trim, "bars": [{"label": f"{m} '25", "value": "-1"} for m in ("Jan", "Feb", "Mar", "Apr")]}
    assert L.review_notes(even) == []


def test_a_variant_without_its_own_shape_is_refused():
    # reviewer 2026-09-03: a race-shaped file asked for bars validated clean and built an empty page
    errors = L.validate(_race(), "bars")
    assert any("needs story values" in e for e in errors), errors
    assert not L.validate(_race(), "race"), L.validate(_race(), "race")


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


# --- T5 review: decline endpoints carry DISPLAY labels (doc 29 s9.22: x labels are readable) --

def test_decimal_year_label_formats_month_and_short_year():
    assert L.decimal_year_label(2024.0027) == "Jan '24"
    assert L.decimal_year_label(2026.6489) == "Aug '26"
    assert L.decimal_year_label(2025.5) == "Jul '25"
    assert L.decimal_year_label(1999.999) == "Dec '99"
    assert L.decimal_year_label("2024.0027") == "Jan '24"          # the token as written parses too
    assert L.decimal_year_label(17.3) is None                       # not a year: no label
    assert L.decimal_year_label("peak") is None


def test_display_label_prefers_an_exact_xtick_then_labels_then_the_year():
    xticks = [[2024.04, "Jan '24"], [2026.54, "Jul '26"]]
    assert L.display_label("2024.04", 0, xticks=xticks) == "Jan '24"
    assert L.display_label("2026.54", 1, xticks=xticks) == "Jul '26"
    assert L.display_label("2024.0027", 0, xticks=xticks) == "Jan '24"        # no tick at that x: the year
    assert L.display_label("2026.6489", 1, xticks=xticks, labels=["from", "to"]) == "to"   # a labels list wins over the year
    assert L.display_label("peak", 0) == "peak"                                 # a bar label is already a display string


@pytest.mark.skipif(not SMH.exists(), reason="SMH drawdown series not on disk")
def test_smh_decline_endpoints_carry_display_labels_and_axes():
    spec = L.build_spec(L.load_series(SMH), "decline")
    assert spec["start"]["label"] == "2024.0027" and spec["end"]["label"] == "2026.6489"   # labels stay verbatim
    assert spec["display_labels"] == {"start": "Jan '24", "end": "Aug '26", "series": "CHIP STOCKS: % BELOW THEIR HIGH"}
    assert spec["axes"]["ylabel"] == "drawdown from running high" and len(spec["axes"]["xticks"]) == 6


def test_decline_from_bars_displays_the_bar_labels_and_carries_no_axes():
    spec = L.build_spec(_bars([88.0, 61.5, 28]), "decline")
    assert spec["display_labels"] == {"start": "L0", "end": "L2", "series": None}
    assert "axes" not in spec


def test_decline_display_from_a_labels_list_beats_the_decimal_year():
    series = {"title": "t", "src": "s", "labels": ["start", "mid", "end"],
              "series": [{"name": "m", "color": "crimson", "pts": [[2024.0, 3], [2025.0, 2], [2026.0, 1]]}]}
    spec = L.build_spec(series, "decline")
    assert spec["display_labels"] == {"start": "start", "end": "end", "series": "m"}
    no_list = {**series, "labels": None}
    spec2 = L.build_spec(no_list, "decline")
    assert spec2["display_labels"] == {"start": "Jan '24", "end": "Jan '26", "series": "m"}


# --- P50 T9: N-TIER PAGES (R26-24) -------------------------------------------
# N small multiples on one page: N bands, each its own y-scale and honest zero, ONE shared x.

def _tier(name: str, unit: str = "Mb", n: int = 8, base: float = 300.0, step: float = -2.0, x0: float = 2015.0) -> dict:
    return {"name": name, "unit": unit, "pts": [[x0 + 0.5 * i, base + step * i] for i in range(n)]}


def _tiers(*tiers: dict, **extra) -> dict:
    return {"title": "Two reserves, one decade", "src": "our reading", "tiers": list(tiers), **extra}


def test_two_tiers_build_two_bands_on_one_shared_x():
    series = _tiers(_tier("JAPAN"), _tier("UNITED STATES", base=695.0, step=-9.0))
    assert L.validate(series, "tiers") == []
    spec = L.build_spec(series, "tiers", None, "right")
    assert spec["builder"] == "tiers" and spec["variant"] == "tiers"
    assert spec["labels"] == ["JAPAN", "UNITED STATES"], "the tier titles ARE the series' names; the page's title stays the argument"
    assert [t["unit"] for t in spec["tiers"]] == ["Mb", "Mb"]
    assert [t["kind"] for t in spec["tiers"]] == ["line", "line"]
    assert spec["tiers"][0]["x"] == spec["tiers"][1]["x"] == [2015.0, 2018.5], "one x, and it is the page's"
    assert spec["tiers"][0]["series"][0]["pts"][0] == [2015.0, 300.0], "the points ride verbatim"


def test_the_two_band_combo_key_is_untouched_by_the_n_tier_builder():
    """`tiers: true` (a bool) is the macro-chart intake's OVERLAY key and builds exactly as it did:
    E53 s4 keeps the two apart, and so does this test - a list is the new builder, a bool is not."""
    series = {"title": "t", "src": "s", "unit": "%", "tiers": True,
              "bars": [{"label": "Jan", "value": -3.0, "x": 2025.0}, {"label": "Feb", "value": 2.0, "x": 2025.1}],
              "series": [{"name": "10-year", "color": "cobalt", "pts": [[2025.0, 4.1], [2025.1, 4.4]]}]}
    spec = L.build_spec(series, "line", None, "right")
    assert spec["builder"] == "combo" and spec["tiers"] is True
    assert "labels" in spec and spec["labels"] == ["Jan", "Feb"]


def test_three_tiers_build_three_bands_and_page_boxes_reports_them():
    series = _tiers(_tier("A"), _tier("B", base=40.0), _tier("C", base=9.0, step=-0.2))
    assert L.validate(series, "tiers") == []
    spec = L.build_spec(series, "tiers", None, "right")
    assert len(spec["tiers"]) == 3
    for aspect in ("16:9", "9:16"):
        boxes = L.page_boxes(spec, aspect)
        bands = boxes["bands"]
        assert len(bands) == 3, aspect
        assert bands[0]["y"] == boxes["plot"]["y"], "the first band starts at the plot's top"
        assert bands[2]["y"] + bands[2]["h"] <= boxes["plot"]["y"] + boxes["plot"]["h"] + 1
        assert bands[0]["h"] == bands[1]["h"] == bands[2]["h"], "equal bands: shape is read against shape"
        gutter = bands[1]["y"] - (bands[0]["y"] + bands[0]["h"])
        assert abs(gutter - L.TIER_GAP * bands[0]["h"]) <= 1, (aspect, gutter)


def test_tiers_on_different_x_ranges_are_refused_naming_both():
    series = _tiers(_tier("A"), _tier("B", x0=1990.0))
    errs = L.validate(series, "tiers")
    assert len(errs) == 1 and "share ONE x" in errs[0], errs
    assert "1990..1993.5" in errs[0] and "2015..2018.5" in errs[0], errs


def test_a_tier_without_a_unit_is_refused_by_name():
    series = _tiers(_tier("JAPAN"), _tier("UNITED STATES", unit=""))
    errs = L.validate(series, "tiers")
    assert len(errs) == 1 and "'UNITED STATES'" in errs[0] and "no 'unit'" in errs[0], errs


def test_five_tiers_are_refused_and_the_message_names_the_ceiling_and_why():
    series = _tiers(*[_tier(f"T{i}") for i in range(5)])
    errs = L.validate(series, "tiers")
    assert errs and errs[0].startswith("5 tiers: the ceiling is 4"), errs
    assert "9:16" in errs[0] and "quarter" in errs[0], "the refusal says WHY four is the ceiling"
    assert L.validate(_tiers(_tier("A")), "tiers")[0].startswith("a tiers page needs 'tiers'")


def test_a_tiers_page_carries_the_pages_own_axes_for_the_one_shared_x():
    series = _tiers(_tier("A"), _tier("B"), xticks=[[2015, "2015"], [2018, "2018"]])
    spec = L.build_spec(series, "tiers", None, "right")
    assert spec["axes"]["xticks"] == [[2015, "2015"], [2018, "2018"]], "the x is shared, so its ticks are the page's"


# --- P50 T6: THE CENSUS PAGE (E53 s1's second amendment) ---------------------

CENSUS = [("United States", 16.8), ("Hong Kong", 8.5), ("Japan", 4.7), ("Korea", 4.5), ("Vietnam", 4.1),
          ("India", 3.4), ("Germany", 3.1), ("Netherlands", 3.0), ("Malaysia", 2.5), ("Russia", 2.4),
          ("Brazil", 2.0), ("Australia", 1.9), ("Spain", 1.3), ("Saudi Arabia", 1.2), ("Rest of world", 40.6)]


def _census(**extra) -> dict:
    return {"title": "China's exports, by partner", "sub": "share of goods exports, one year",
            "src": "our reading", "unit": "%", "total": 100,
            "shares": [{"label": a, "value": b} for a, b in CENSUS], **extra}


def test_squarify_areas_are_proportional_and_the_cells_sit_near_three_by_two():
    areas = [v / sum(v for _, v in CENSUS) * (900.0 * 600.0) for _, v in sorted(CENSUS, key=lambda kv: -kv[1])]
    cells = L.squarify(areas, 0.0, 0.0, 900.0, 600.0)
    assert len(cells) == len(areas)
    for area, cell in zip(areas, cells):
        assert abs(cell["w"] * cell["h"] - area) <= 1e-6 * area, (area, cell)
    assert abs(sum(c["w"] * c["h"] for c in cells) - 900.0 * 600.0) <= 1e-6 * 900 * 600
    for c in cells:
        assert c["x"] >= -1e-9 and c["y"] >= -1e-9
        assert c["x"] + c["w"] <= 900.0 + 1e-6 and c["y"] + c["h"] <= 600.0 + 1e-6
    ratios = sorted(c["w"] / c["h"] for c in cells)
    median = ratios[len(ratios) // 2]
    assert 1.0 <= median <= 2.4, f"the layout is tuned toward {L.TREEMAP_ASPECT}:1, never 1:1 - median {median}"
    # ... and tuning toward 3:2 really does move it off the square (the paper's own target)
    square = sorted(c["w"] / c["h"] for c in L.squarify(areas, 0.0, 0.0, 900.0, 600.0, target=1.0))
    assert square[len(square) // 2] < median


def test_the_label_tiers_are_the_research_floors_two_lines_one_line_none():
    assert L.label_tier(240, 160, "United States", "16.8")["tier"] == 2
    assert L.label_tier(240, 160, "United States", "16.8")["value_font"] >= L.TREEMAP_VALUE_FONT
    one = L.label_tier(120, 44, "Japan", "4.7")   # over 80 x 36, under 110 x 64: one stacked line
    assert one["tier"] == 1 and one["value_font"] == 0.0 and one["font"] >= L.TREEMAP_LABEL_FONT[0]
    assert L.label_tier(70, 40, "Japan", "4.7")["tier"] == 0, "nothing under 80 x 36 px carries text"
    assert L.label_tier(240, 30, "Japan", "4.7")["tier"] == 0, "... in either dimension"
    long_name = L.label_tier(100, 44, "Saudi Arabia", "1.2")
    assert long_name["tier"] == 0, "a name too long for its cell at 18 px is not shrunk below the floor - it is not written"


def test_a_treemap_page_lays_out_both_aspects_and_counts_what_it_could_not_name():
    series = _census()
    assert L.validate(series, "treemap") == []
    spec = L.build_spec(series, "treemap", None, "right")
    assert spec["builder"] == "treemap" and spec["total"] == 100
    assert set(spec["layout"]) == {"16:9", "9:16"}
    for aspect, lay in spec["layout"].items():
        cells = lay["cells"]
        assert len(cells) == len(CENSUS), aspect
        assert [c["label"] for c in cells][:2] == ["Rest of world", "United States"], "layout order: the biggest cell first"
        assert abs(sum(c["fw"] * c["fh"] for c in cells) - 1.0) <= 1e-3, aspect
        assert cells[0]["share"] == 0.406 and cells[1]["tier"] >= 1
        unnamed = sum(1 for c in cells if c["tier"] == 0)
        assert lay["unnamed"] == unnamed
        assert lay["legend"] == (f"and {unnamed} others" if unnamed else "")
        assert all(c["value_font"] >= L.TREEMAP_VALUE_FONT for c in cells if c["tier"] == 2), aspect


def test_a_size_claim_on_a_census_page_is_refused_and_points_at_the_bars_page():
    for text, field in (("America is bigger than the next four", "sub"), ("Who is largest?", "title"),
                        ("three times Japan's", "claim")):
        errs = L.validate(_census(**{field: text}), "treemap")
        assert errs and "SIZE CLAIM takes its BAR" in errs[0], (field, errs)
        assert "--variant bars" in errs[0], "the refusal names the page that CAN carry it (E53 s1)"
        assert field in errs[0]
    assert L.validate(_census(sub="the census of a whole year"), "treemap") == []


def test_a_census_needs_three_parts_and_positive_ones():
    errs = L.validate({"title": "t", "src": "s", "shares": [{"label": "a", "value": 1}, {"label": "b", "value": 2}]}, "treemap")
    assert errs and "at least 3 parts" in errs[0] and "--variant share" in errs[0], errs
    bad = _census()
    bad["shares"][2] = {"label": "Japan", "value": -4.7}
    assert any("not a positive number" in e for e in L.validate(bad, "treemap")), L.validate(bad, "treemap")


def test_check_infers_the_variant_from_the_files_own_shape_and_writes_nothing(tmp_path, capsys):
    path = _write(tmp_path, "ev-census.series.json", _census())
    assert L.main([str(path), "--check"]) == 0
    out = capsys.readouterr().out
    assert out.startswith("OK ev-census.series.json: treemap treemap 15 cells"), out
    assert not list(tmp_path.glob("*.page.json")), "a check writes nothing"
    tiers = _write(tmp_path, "ev-two.series.json", _tiers(_tier("A"), _tier("B")))
    assert L.main([str(tiers), "--check"]) == 0
    assert "tiers tiers 2 tiers sharing x" in capsys.readouterr().out
    assert L.infer_variant({"bars": [{"label": "a", "value": 1}]}) is None, "a bars file's variant is the sentence's call, never a guess"
    assert L.main([str(_write(tmp_path, "ev-bars.series.json", _bars([1, 2]))), "--check"]) == L.EXIT_INVALID
