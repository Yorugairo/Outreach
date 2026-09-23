"""Synthetic adapter coverage for the Fed episode's minute segment."""
from __future__ import annotations

import importlib.util
from pathlib import Path
from types import SimpleNamespace
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
BUILDER_PATH = (
    ROOT
    / "content/video_engine/projects/systems-and-blowups/fed-liquidity-pressure/build_fed_liquidity.py"
)
SPEC = importlib.util.spec_from_file_location("fed_liquidity_minute_builder_test", BUILDER_PATH)
assert SPEC and SPEC.loader
BUILDER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = BUILDER
SPEC.loader.exec_module(BUILDER)
MINUTE_LOADED_ON_IMPORT = "minute" in BUILDER._SHOT_TABLES


MINUTE_PHRASE = (
    "The companies replacing cheap debt still need financing, even as one source "
    "of support behind the banks runs down."
)


def _minute_table(*, register_assets=None):
    def group_end_phrase(group: str) -> str:
        assert group == "M01"
        return MINUTE_PHRASE

    return SimpleNamespace(
        SEGMENT_GROUPS={"minute": ("M01",)},
        AUTHORING_STATUS="SYNTHETIC_MINUTE_TABLE",
        group_end_phrase=group_end_phrase,
        register_assets=register_assets,
    )


def _minute_words() -> list[dict[str, float | str]]:
    words = [
        {"w": token, "start_s": float(index * 3), "end_s": float(index * 3 + 1)}
        for index, token in enumerate(
            [
                "The", "companies", "replacing", "cheap", "debt", "still", "need",
                "financing,", "even", "as", "one", "source", "of", "support",
                "behind", "the", "banks", "runs",
            ]
        )
    ]
    words.extend(
        [
            {"w": "down.", "start_s": 64.0, "end_s": 64.975},
            {"w": "Next", "start_s": 65.6, "end_s": 66.4},
        ]
    )
    return words


def test_minute_uses_its_own_output_and_table_contract() -> None:
    assert BUILDER.TABLE_NAMES["minute"] == "SHOT-TABLE-MINUTE.py"
    assert BUILDER.TIMELINE_NAMES["minute"] == "fed-liquidity-minute.timeline.json"
    assert BUILDER.BUILD_NAMES["minute"] == "build-minute"
    assert "minute" in BUILDER.ASSEMBLY_SEGMENTS


def test_existing_segments_keep_the_eager_pilot_table() -> None:
    assert BUILDER._SHOT_TABLES["bed"] is BUILDER.SHOT_TABLE_PILOT
    assert BUILDER._SHOT_TABLES["unit"] is BUILDER.SHOT_TABLE_PILOT
    assert BUILDER._SHOT_TABLES["pilot"] is BUILDER.SHOT_TABLE_PILOT
    assert not MINUTE_LOADED_ON_IMPORT


def test_minute_table_is_loaded_lazily_from_episode_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    table_path = tmp_path / "SHOT-TABLE-MINUTE.py"
    table_path.write_text(
        "SEGMENT_GROUPS = {'minute': ('M01',)}\n"
        "AUTHORING_STATUS = 'SYNTHETIC'\n"
        "def group_end_phrase(group):\n"
        "    return 'Done.'\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(BUILDER, "EPISODE_ROOT", tmp_path)
    monkeypatch.delitem(BUILDER._SHOT_TABLES, "minute", raising=False)
    loaded = BUILDER._shot_table_for("minute")
    assert loaded.SEGMENT_GROUPS == {"minute": ("M01",)}
    assert loaded.AUTHORING_STATUS == "SYNTHETIC"
    assert BUILDER._SHOT_TABLES["minute"] is loaded


def test_minute_runtime_ends_on_parent_selected_sentence_and_real_tail(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(BUILDER._SHOT_TABLES, "minute", _minute_table())
    boundary = BUILDER._segment_runtime(_minute_words(), "minute", audio_duration_s=67.0)
    assert boundary.end_word_index == 18
    assert boundary.closing_phrase == MINUTE_PHRASE
    assert boundary.spoken_end_s == 64.975
    assert boundary.end_s == 65.425
    assert boundary.next_word_start_s == 65.6


def test_minute_asset_hook_is_scoped_to_minute(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[object] = []
    table = _minute_table(register_assets=lambda docks: calls.append(docks))
    monkeypatch.setitem(BUILDER._SHOT_TABLES, "minute", table)
    BUILDER._register_segment_assets("pilot", table)
    assert calls == []
    BUILDER._register_segment_assets("minute", table)
    assert calls == [BUILDER.D]


def test_minute_asset_hook_rejects_noncallable_registration(monkeypatch: pytest.MonkeyPatch) -> None:
    table = _minute_table(register_assets="not-callable")
    monkeypatch.setitem(BUILDER._SHOT_TABLES, "minute", table)
    with pytest.raises(ValueError, match="register_assets must be callable"):
        BUILDER._register_segment_assets("minute", table)
