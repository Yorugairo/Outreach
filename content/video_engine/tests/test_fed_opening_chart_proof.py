"""Focused authoring tests for the source-bound Fed opening proof candidates."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


PATH = (
    Path(__file__).resolve().parents[1]
    / "projects/systems-and-blowups/fed-liquidity-pressure/build_opening_chart_proof.py"
)
SPEC = importlib.util.spec_from_file_location("fed_opening_chart_proof", PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def _real_history() -> dict:
    return json.loads(MODULE.HISTORY_SOURCE.read_text(encoding="utf-8"))


def _rrp() -> dict:
    return json.loads(MODULE.RRP_SOURCE.read_text(encoding="utf-8"))


def test_actual_history_is_two_series_and_source_bound():
    history = _real_history()
    verified = MODULE.validate_history(history, MODULE.HISTORY_SOURCE)
    assert verified["status"] == "DERIVED"
    assert len(verified["series"]) == 2
    assert all(len(line["pts"]) == 159 for line in verified["series"])
    assert [line["pts"][-1][1] for line in verified["series"]] == [-2.237895, 0.07228]
    assert history["facts"]["interpolation"] is False
    assert history["facts"]["decimation"] is False


@pytest.mark.parametrize(
    "mutation",
    [
        lambda value: value.update({"status": "PLACEHOLDER"}),
        lambda value: value["facts"].update({"interpolation": True}),
        lambda value: value["facts"].update({"window_end": "2025-06-10"}),
    ],
)
def test_history_refuses_unverified_inputs(mutation):
    history = _real_history()
    mutation(history)
    with pytest.raises(ValueError):
        MODULE.validate_history(history, MODULE.HISTORY_SOURCE)


def test_prepare_copies_history_and_derives_exact_endpoint_bars(tmp_path):
    history = _real_history()
    source_bytes = MODULE.HISTORY_SOURCE.read_bytes()
    objects = MODULE.prepare_candidate_objects(tmp_path, history, _rrp(), candidate="b")

    assert MODULE.HISTORY_SOURCE.read_bytes() == source_bytes
    local_history = objects[MODULE.HISTORY_ID]
    endpoint = objects[MODULE.ENDPOINT_ID]
    assert local_history["unit"] == ""
    assert local_history["ylabel"] == MODULE.HISTORY_YLABEL
    assert "xlabel" not in local_history
    assert local_history["xticks"] == MODULE._date_ticks()
    assert all("name" not in line for line in local_history["series"])
    assert [bar["value"] for bar in endpoint["bars"]] == [line["pts"][-1][1] for line in history["series"]]
    assert endpoint["facts"]["derived_from"] == f"{MODULE.HISTORY_ID}.series.json"
    assert endpoint["domain"] == local_history["domain"]
    assert (tmp_path / "evidence/objects" / f"{MODULE.ENDPOINT_ID}.series.json").is_file()


def test_rows_are_full_stage_candidates_without_slide_boundaries():
    rows_a = MODULE.build_rows("a", 19.425)
    rows_b = MODULE.build_rows("b", 19.425)
    for rows in (rows_a, rows_b):
        assert rows[0][0] == 0.0
        assert rows[0][1] == rows[1][0]
        assert rows[-1][1] == 19.425
        assert all("slide" not in str(row[5]) for row in rows)
        assert rows[1][5] == "melt:gather:throw:2.0"
        assert ":axes:" in rows[0][2]
    assert ";then=fed-assets-reserves-history-endpoints:bars" not in rows_a[0][2]
    assert ";then=fed-assets-reserves-history-endpoints:bars" in rows_b[0][2]
    chart_to = next(spec for spec in rows_b[0][6] if spec["kind"] == "chart_to")
    assert chart_to["keyed"] is True
    assert chart_to["at"] > 6.0  # after both 3s line draws


def test_phone_profile_is_opt_in_and_end_tags_come_from_actual_points(tmp_path):
    from ledger_page import badges_for

    source = _real_history()
    source_before = json.dumps(source, sort_keys=True)
    a = MODULE.prepare_candidate_objects(tmp_path / "a", source, _rrp(), candidate="a")
    b = MODULE.prepare_candidate_objects(tmp_path / "b", source, _rrp(), candidate="b")
    history = a[MODULE.HISTORY_ID]
    assert all(obj["readability"] == "landscape-phone" for obj in a.values())
    assert all("readability" not in obj for obj in b.values())
    assert [line["pts"] for line in history["series"]] == [line["pts"] for line in source["series"]]
    assert [badge["tag"] for badge in history["badges"]] == ["−2.238T", "+0.072T"]
    assert all(badge["inline"] for badge in badges_for(history))
    assert json.dumps(source, sort_keys=True) == source_before


def test_runtime_ends_after_the_measured_opening_sentence():
    words = [
        {"w": "history.", "start_s": 0.0, "end_s": 1.0},
        {"w": "price.", "start_s": 18.25, "end_s": 18.975},
        {"w": "next", "start_s": 19.6, "end_s": 19.8},
    ]
    assert MODULE.opening_runtime(words) == 19.425


def test_runtime_rejects_a_following_word_inside_the_silence_tail():
    words = [
        {"w": "price.", "start_s": 18.25, "end_s": 18.975},
        {"w": "next", "start_s": 19.2, "end_s": 19.4},
    ]
    with pytest.raises(ValueError, match="tail|starts"):
        MODULE.opening_runtime(words)


@pytest.mark.parametrize(
    "bad_word",
    [
        {"w": "price.", "start_s": True, "end_s": 18.975},
        {"w": "price.", "start_s": float("nan"), "end_s": 18.975},
        {"w": "price.", "start_s": 18.975, "end_s": 18.25},
    ],
)
def test_runtime_rejects_malformed_target_timings(bad_word):
    with pytest.raises(ValueError, match="timing|finite|numeric"):
        MODULE.opening_runtime([bad_word, {"w": "next", "start_s": 19.6, "end_s": 19.8}])


def test_runtime_rejects_out_of_order_crossing_word():
    words = [
        {"w": "price.", "start_s": 18.25, "end_s": 18.975},
        {"w": "next", "start_s": 18.8, "end_s": 19.2},
    ]
    with pytest.raises(ValueError, match="crosses"):
        MODULE.opening_runtime(words)


def test_runtime_requires_a_following_onset_or_trustworthy_audio_duration():
    words = [{"w": "price.", "start_s": 18.25, "end_s": 18.975}]
    with pytest.raises(MODULE.SourceWaitError, match="following word onset"):
        MODULE.opening_runtime(words)
    assert MODULE.opening_runtime(words, audio_duration_s=19.8) == 19.425


def test_runtime_matches_the_real_take_boundary_without_writing_artifacts(tmp_path):
    project = MODULE.Project(
        here=tmp_path,
        build=tmp_path,
        take=MODULE.TAKE,
        take_stem=MODULE.TAKE_STEM,
        script_name="SCRIPT-VO.txt",
        episode_id="fed-opening-runtime-test",
        take_name=MODULE.TAKE.name,
    )
    words = MODULE.W.take_words(project)
    assert MODULE.opening_runtime(words) == 19.425
    assert list(tmp_path.iterdir()) == []


def test_missing_parent_source_fails_before_build(tmp_path, monkeypatch):
    missing_history = tmp_path / "missing-history.series.json"
    missing_rrp = tmp_path / "missing-rrp.series.json"
    build_root = tmp_path / "build-opening-chart-proof-v1"
    monkeypatch.setattr(MODULE, "HISTORY_SOURCE", missing_history)
    monkeypatch.setattr(MODULE, "RRP_SOURCE", missing_rrp)
    monkeypatch.setattr(MODULE, "BUILD_ROOT", build_root)
    monkeypatch.setattr(MODULE, "TAKE", tmp_path / "take")
    with pytest.raises(SystemExit, match="refusing placeholder compile"):
        MODULE.main(["--candidate", "a"])
    assert not build_root.exists()
