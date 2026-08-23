from __future__ import annotations

import json
from pathlib import Path

import pytest

from content.video_engine.src.services.composed_plate import (
    ComposedPlateError,
    compose_and_write,
    is_composed,
    plate_kind,
    render_plate_svg,
    validate_composed_plate,
)
from content.video_engine.src.services.visual_prompt_pack import (
    VisualPromptPackError,
    compile_visual_prompt_pack,
)


def _plate(**overrides) -> dict:
    plate = {
        "schema_version": "composed_plate.v1",
        "plate_id": "yr-growth",
        "lane": "expert_explainer",
        "layout": "figure_board",
        "title": "Rent roll",
        "content": {
            "rows": [
                {"label": "YR 1", "value": "$55,000", "direction": "up", "tone": "positive"},
                {"label": "YR 2", "value": "$61,000", "direction": "up", "tone": "positive"},
            ]
        },
    }
    plate.update(overrides)
    return plate


def _stack(total: float = 86000.0) -> dict:
    return _plate(
        plate_id="total-in",
        layout="arithmetic_stack",
        content={
            "operands": [
                {"label": "$50K", "amount": 50000.0},
                {"label": "$36K", "amount": 36000.0, "tone": "negative"},
            ],
            "total": {"label": "$86K TOTAL IN.", "amount": total},
        },
    )


def test_figure_board_renders_real_type_not_pixels():
    svg = render_plate_svg(validate_composed_plate(_plate()))

    assert svg.startswith("<svg")
    assert "$55,000" in svg
    assert "YR 1" in svg


def test_render_is_byte_identical_across_runs():
    plate = validate_composed_plate(_plate())

    assert render_plate_svg(plate) == render_plate_svg(plate)


def test_arithmetic_that_reconciles_is_accepted():
    validated = validate_composed_plate(_stack())

    assert validated["content"]["total"]["amount"] == pytest.approx(86000.0)


def test_arithmetic_that_does_not_add_up_is_refused_not_drawn():
    with pytest.raises(ComposedPlateError) as excinfo:
        validate_composed_plate(_stack(total=90000.0))

    joined = " ".join(excinfo.value.errors)
    assert "does not reconcile" in joined
    assert "worse than no plate" in joined


def test_comparison_pair_renders_both_sides():
    plate = validate_composed_plate(
        _plate(
            plate_id="bond-compare",
            layout="comparison_pair",
            content={
                "pair": [
                    {"label": "old issue", "value": "3% BOND", "tone": "negative"},
                    {"label": "new issue", "value": "5% BOND", "tone": "positive"},
                ]
            },
        )
    )
    svg = render_plate_svg(plate)

    assert "3% BOND" in svg
    assert "5% BOND" in svg


def test_stat_row_renders_each_tile():
    plate = validate_composed_plate(
        _plate(
            plate_id="stats",
            layout="stat_row",
            content={
                "stats": [
                    {"value": "44.3", "caption": "figures per 1000 words"},
                    {"value": "19x", "caption": "views per subscriber"},
                ]
            },
        )
    )
    svg = render_plate_svg(plate)

    assert "44.3" in svg
    assert "views per subscriber" in svg


def test_layout_without_its_required_content_is_rejected():
    with pytest.raises(ComposedPlateError) as excinfo:
        validate_composed_plate(_plate(layout="comparison_pair"))

    assert any("requires content.pair" in error for error in excinfo.value.errors)


def test_lane_palette_drives_the_ground_colour():
    expert = render_plate_svg(validate_composed_plate(_plate(lane="expert_explainer")))
    whiteboard = render_plate_svg(
        validate_composed_plate(_plate(lane="whiteboard", plate_id="wb"))
    )

    assert "#F4E6C7" in expert
    assert "#FFFFFF" in whiteboard


def test_markup_escapes_operator_supplied_text():
    plate = validate_composed_plate(
        _plate(title='Rent & "roll" <b>', plate_id="escaped")
    )
    svg = render_plate_svg(plate)

    assert "<b>" not in svg
    assert "&amp;" in svg


def test_compose_and_write_costs_nothing_and_emits_svg(tmp_path):
    summary = compose_and_write(_plate(), output_dir=tmp_path / "job")

    assert summary["generation_cost_usd"] == 0.0
    assert Path(summary["svg_path"]).read_text(encoding="utf-8").startswith("<svg")
    assert json.loads(Path(summary["artifact_path"]).read_text(encoding="utf-8"))["plate_id"]


def test_plate_kind_defaults_to_generated_so_existing_coverage_is_unchanged():
    assert plate_kind({"slot_id": "s1"}) == "generated_plate"
    assert is_composed({"slot_id": "s1"}) is False
    assert is_composed({"slot_id": "s1", "plate_kind": "composed_plate"}) is True


def test_unknown_plate_kind_is_rejected():
    with pytest.raises(ComposedPlateError) as excinfo:
        plate_kind({"slot_id": "s1", "plate_kind": "hand_drawn"})

    assert any("hand_drawn" in error for error in excinfo.value.errors)


def _coverage(*kinds: str) -> dict:
    return {
        "schema_version": "editorial_coverage.v1",
        "artifact_hash": "a" * 64,
        "timing_basis": "estimated",
        "slots": [
            {
                "slot_id": f"s{index}",
                "narration_excerpt": f"line {index}",
                "visual_archetype": "typography_explainer",
                "motion_recipe": "detail_punch",
                "duration_s": 4.0,
                "plate_kind": kind,
            }
            for index, kind in enumerate(kinds)
        ],
    }


def test_composed_slots_are_excluded_from_the_generation_budget():
    coverage = _coverage("generated_plate", "composed_plate", "generated_plate")

    pack = compile_visual_prompt_pack(coverage, lane="expert_explainer")

    assert len(pack["groups"]) == 2
    assert pack["composed_slot_count"] == 1
    assert {group["slot_id"] for group in pack["groups"]} == {"s0", "s2"}


def test_an_all_composed_coverage_needs_no_prompt_pack():
    with pytest.raises(VisualPromptPackError) as excinfo:
        compile_visual_prompt_pack(_coverage("composed_plate"), lane="expert_explainer")

    assert any("no prompt pack is required" in error for error in excinfo.value.errors)
