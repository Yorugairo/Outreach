from __future__ import annotations

import json
from pathlib import Path

import pytest

from content.video_engine.src.services.style_packs import (
    HYPERFRAMES_ADAPTERS,
    LANE_ORDER,
    StylePackError,
    get_pack,
    load_registry,
    registry_summary,
    validate_style_pack,
)


def _pack(**overrides) -> dict:
    pack = {
        "schema_version": "video_style_pack.v1",
        "lane": "whiteboard",
        "label": "Test pack",
        "renderer": {"engine": "hyperframes", "runtime_adapter": "css"},
        "character": {
            "policy": "none",
            "identity_anchor": "single-weight marker line on white",
        },
        "background": {"policy": "plain"},
        "captions": {"mode": "none"},
        "colour_semantics": {},
        "motion_recipes": ["masked_reveal"],
        "plate_kinds": ["composed_plate"],
    }
    pack.update(overrides)
    return pack


def test_registry_defines_exactly_the_seven_lanes():
    packs = load_registry()

    assert set(packs) == set(LANE_ORDER)
    assert len(LANE_ORDER) == 7


def test_expert_explainer_is_first_in_build_priority():
    # Reordered 2026-08-22: its advantages are machine strengths, unlike a human drawing hand.
    assert LANE_ORDER[0] == "expert_explainer"


def test_every_lane_declares_the_four_distinguishing_axes():
    for lane, pack in load_registry().items():
        assert pack["character"]["policy"], lane
        assert pack["character"]["identity_anchor"], lane
        assert pack["background"]["policy"], lane
        assert pack["captions"]["mode"], lane
        assert pack["motion_recipes"], lane


def test_identity_anchor_never_relies_on_facial_features():
    anchors = " ".join(
        pack["character"]["identity_anchor"] for pack in load_registry().values()
    ).lower()

    assert "silhouette" in anchors or "colour" in anchors
    assert "facial features" not in anchors


def test_rive_is_rejected_by_name_with_the_reason():
    with pytest.raises(StylePackError) as excinfo:
        validate_style_pack(_pack(renderer={"engine": "hyperframes", "runtime_adapter": "rive"}))

    joined = " ".join(excinfo.value.errors)
    assert "rive" in joined
    assert "compiled binary" in joined


def test_adapter_outside_the_seven_is_rejected():
    with pytest.raises(StylePackError) as excinfo:
        validate_style_pack(
            _pack(renderer={"engine": "hyperframes", "runtime_adapter": "spine"})
        )

    assert any("seven HyperFrames adapters" in error for error in excinfo.value.errors)


def test_all_seven_adapters_are_accepted():
    for adapter in sorted(HYPERFRAMES_ADAPTERS):
        pack = validate_style_pack(
            _pack(renderer={"engine": "hyperframes", "runtime_adapter": adapter})
        )
        assert pack["renderer"]["runtime_adapter"] == adapter


def test_runtime_adapter_requires_the_hyperframes_engine():
    with pytest.raises(StylePackError) as excinfo:
        validate_style_pack(_pack(renderer={"engine": "remotion", "runtime_adapter": "gsap"}))

    assert any("engine 'hyperframes'" in error for error in excinfo.value.errors)


def test_unknown_lane_is_rejected():
    with pytest.raises(StylePackError):
        validate_style_pack(_pack(lane="crude_stick_comedy"))


def test_missing_identity_anchor_is_rejected():
    with pytest.raises(StylePackError) as excinfo:
        validate_style_pack(_pack(character={"policy": "none"}))

    assert any("identity_anchor" in error for error in excinfo.value.errors)


def test_burned_in_captions_require_a_position_and_highlight_rule():
    with pytest.raises(StylePackError) as excinfo:
        validate_style_pack(_pack(captions={"mode": "burned_in"}))

    joined = " ".join(excinfo.value.errors)
    assert "captions.position" in joined
    assert "captions.highlight" in joined


def test_keyword_highlight_requires_a_colour():
    with pytest.raises(StylePackError) as excinfo:
        validate_style_pack(
            _pack(captions={"mode": "burned_in", "position": "top", "highlight": "keyword"})
        )

    assert any("highlight_colour" in error for error in excinfo.value.errors)


def test_rendition_is_descriptive_and_unrestricted():
    # Retracted 2026-08-22: reference conditioning holds identity at any rendition,
    # and legibility is protected by zoning rather than by flattening the artwork.
    renditions = {
        pack["character"].get("rendition") for pack in load_registry().values()
    }

    assert "painterly" in renditions
    assert "flat" in renditions


def test_stick_explainer_defers_on_screen_copy_to_the_operator():
    assert get_pack("stick_explainer")["operator_writes_on_screen_copy"] is True
    assert get_pack("expert_explainer").get("operator_writes_on_screen_copy", False) is False


def test_every_lane_reserves_an_evidence_region():
    for lane, pack in load_registry().items():
        assert pack["background"].get("evidence_safe_region") is True, lane


def test_composed_plates_are_available_in_every_lane():
    for lane, pack in load_registry().items():
        assert "composed_plate" in pack["plate_kinds"], lane


def test_duplicate_lane_in_the_directory_is_rejected(tmp_path):
    for name in ("a.json", "b.json"):
        (tmp_path / name).write_text(json.dumps(_pack()), encoding="utf-8")

    with pytest.raises(StylePackError) as excinfo:
        load_registry(tmp_path)

    assert any("already defined" in error for error in excinfo.value.errors)


def test_incomplete_registry_names_the_missing_lanes(tmp_path):
    (tmp_path / "one.json").write_text(json.dumps(_pack()), encoding="utf-8")

    with pytest.raises(StylePackError) as excinfo:
        load_registry(tmp_path)

    assert any("missing lanes" in error and "expert_explainer" in error
               for error in excinfo.value.errors)


def test_packs_on_disk_carry_stable_hashes():
    first = registry_summary()
    second = registry_summary()

    assert [lane["artifact_hash"] for lane in first["lanes"]] == [
        lane["artifact_hash"] for lane in second["lanes"]
    ]
    assert all(len(lane["artifact_hash"]) == 64 for lane in first["lanes"])
