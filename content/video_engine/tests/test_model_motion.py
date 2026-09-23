from __future__ import annotations

import copy
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any

import pytest

from content.video_engine.src.modeling.inspection import (
    CoordinateResidual,
    MotionInspectionError,
    inspect_motion_sample,
)
from content.video_engine.src.modeling.motion import (
    MotionContractError,
    MotionTimeline,
    RationalClock,
    SemanticTarget,
    bind_motion_targets,
)


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "modeling" / "motion" / "knockout-motion.v1.json"
SOURCE_CLOCK_PATH = Path(__file__).parent / "fixtures" / "modeling" / "motion" / "source-exchange-clock.v1.json"
PROJECT_ROOT = Path(__file__).resolve().parents[3]


def _fixture() -> dict[str, Any]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def _timeline() -> MotionTimeline:
    return MotionTimeline.from_scene(_fixture()["scene"])


def test_diagnostic_fixture_hash_and_rational_clock_are_exact() -> None:
    fixture = _fixture()
    source = PROJECT_ROOT / fixture["provenance"]["path"]
    assert hashlib.sha256(source.read_bytes()).hexdigest() == fixture["provenance"]["sha256"]

    timeline = _timeline()
    assert timeline.clock.fps == Fraction(24, 1)
    assert timeline.clock.seconds_at(Fraction(27)) == Fraction(9, 8)
    assert timeline.clock.seconds_at(Fraction(1, 2)) == Fraction(1, 48)


def test_direct_clock_construction_normalizes_exact_values_and_rejects_floats() -> None:
    clock = RationalClock(fps=24, duration_frames=96, origin_seconds=0)
    assert clock.fps == Fraction(24, 1)
    assert clock.origin_seconds == Fraction(0, 1)
    assert clock.seconds_at(Fraction(1, 2)) == Fraction(1, 48)

    ntsc_clock = RationalClock(fps=Fraction(24_000, 1_001), duration_frames=1000)
    assert ntsc_clock.seconds_at(Fraction(24)) == Fraction(1_001, 1_000)

    with pytest.raises(MotionContractError, match="exact rational"):
        RationalClock(fps=24.0, duration_frames=96)  # type: ignore[arg-type]
    with pytest.raises(MotionContractError, match="exact rational"):
        RationalClock(fps=24, duration_frames=96, origin_seconds=0.25)  # type: ignore[arg-type]


def test_events_are_points_and_contacts_are_end_exclusive_intervals() -> None:
    timeline = _timeline()

    at_contact = timeline.evaluate(Fraction(27))
    assert [event.event_id for event in at_contact.events] == ["right-straight-contact"]
    assert [contact.contact_id for contact in at_contact.contacts] == [
        "attacker-planted-foot",
        "right-hand-to-head",
    ]

    during_contact = timeline.evaluate(Fraction(55, 2))
    assert not during_contact.events
    assert [contact.contact_id for contact in during_contact.contacts] == [
        "attacker-planted-foot",
        "right-hand-to-head",
    ]

    after_contact = timeline.evaluate(Fraction(28))
    assert [event.event_id for event in after_contact.events] == ["head-recoil"]
    assert [contact.contact_id for contact in after_contact.contacts] == ["attacker-planted-foot"]

    grounded = timeline.evaluate(Fraction(85))
    assert [contact.contact_id for contact in grounded.contacts] == ["victim-on-mat"]


def test_source_clock_exposure_preserves_contact_and_following_head_snap() -> None:
    fixture = json.loads(SOURCE_CLOCK_PATH.read_text(encoding="utf-8"))
    source = PROJECT_ROOT / fixture["provenance"]["path"]
    assert hashlib.sha256(source.read_bytes()).hexdigest() == fixture["provenance"]["sha256"]
    timeline = MotionTimeline.from_scene(fixture["scene"])
    assert timeline.clock.fps == Fraction(30)

    # Exact source events are absent from the 24 fps midpoint samples, but
    # retained in their half-open output exposures and never shifted earlier.
    before = timeline.evaluate_output_exposure(18, 24)
    contact = timeline.evaluate_output_exposure(19, 24)
    recoil = timeline.evaluate_output_exposure(20, 24)
    assert before.exposed_events == before.exposed_contacts == ()
    assert (contact.source_start_frame, contact.source_end_frame) == (
        Fraction(95, 4), Fraction(25)
    )
    assert contact.sample.frame == Fraction(195, 8)
    assert contact.sample.events == ()
    assert [event.event_id for event in contact.exposed_events] == ["left-hook-contact"]
    assert [item.contact_id for item in contact.exposed_contacts] == ["left-hand-to-head"]
    assert [event.event_id for event in recoil.exposed_events] == ["head-snap"]
    assert recoil.exposed_contacts == ()
    assert timeline.evaluate(Fraction(24)).events[0].event_id == "left-hook-contact"

    # Arbitrary seek order and fractional output rates must not consume events.
    assert timeline.evaluate_output_exposure(19, 24) == contact
    event_ids = [
        event.event_id
        for frame in range(84)
        for event in timeline.evaluate_output_exposure(frame, 24).exposed_events
    ]
    assert event_ids == ["left-hook-contact", "head-snap"]
    assert timeline.evaluate_output_exposure(19, Fraction(24_000, 1_001)).output_fps == Fraction(24_000, 1_001)


def test_output_exposure_rejects_invalid_clock_and_partial_tail() -> None:
    timeline = _timeline()
    for frame, fps in ((-1, 24), (True, 24), (0, 0), (0, 24.0), (96, 24)):
        with pytest.raises(MotionContractError):
            timeline.evaluate_output_exposure(frame, fps)  # type: ignore[arg-type]

    source_scene = json.loads(SOURCE_CLOCK_PATH.read_text(encoding="utf-8"))["scene"]
    source_timeline = MotionTimeline.from_scene(source_scene)
    assert source_timeline.evaluate_output_exposure(83, 24).source_end_frame == 105
    with pytest.raises(MotionContractError, match="output exposure is outside"):
        source_timeline.evaluate_output_exposure(84, 24)


def test_seek_evaluation_is_order_independent_and_cubic_is_defined_smoothstep() -> None:
    timeline = _timeline()
    requested = Fraction(27, 2)
    expected = timeline.evaluate(requested)

    for frame in (Fraction(70), Fraction(27), Fraction(3), requested, Fraction(84), requested):
        sample = timeline.evaluate(frame)
        if frame == requested:
            assert sample == expected

    hand = next(channel for channel in expected.channels if channel.channel_id == "fighter-a-right-hand")
    assert hand.value == pytest.approx((0.2, 0.05, 1.2))
    assert expected.frame == requested
    assert expected.time_seconds == Fraction(9, 16)


def test_linear_channel_evaluation_and_backend_neutral_target_binding() -> None:
    timeline = _timeline()
    sample = timeline.evaluate(Fraction(31))
    head = next(channel for channel in sample.channels if channel.channel_id == "fighter-b-head")
    assert head.value == pytest.approx((0.11, 0.0, 1.66))

    # The same evaluated scene motion binds through two backend-owned semantic
    # maps; their opaque handles never enter the portable scene or fixture.
    targets_3d = {
        SemanticTarget("fighter_a", "semantic_joint", "right_hand"): object(),
        SemanticTarget("fighter_b", "semantic_joint", "head"): object(),
    }
    targets_2_5d = {
        SemanticTarget("fighter_a", "semantic_joint", "right_hand"): object(),
        SemanticTarget("fighter_b", "semantic_joint", "head"): object(),
    }
    bound_3d = bind_motion_targets(sample, targets_3d)
    bound_2_5d = bind_motion_targets(sample, targets_2_5d)

    assert (bound_3d.scene_id, bound_3d.frame, bound_3d.time_seconds) == (
        bound_2_5d.scene_id,
        bound_2_5d.frame,
        bound_2_5d.time_seconds,
    ) == (sample.scene_id, sample.frame, sample.time_seconds)
    assert bound_3d.events == bound_2_5d.events == sample.events
    assert bound_3d.contacts == bound_2_5d.contacts == sample.contacts
    assert [item.channel_id for item in bound_3d.channels] == [
        item.channel_id for item in bound_2_5d.channels
    ]
    assert [item.value for item in bound_3d.channels] == [
        item.value for item in bound_2_5d.channels
    ]
    assert all(
        left.target_handle is not right.target_handle
        for left, right in zip(bound_3d.channels, bound_2_5d.channels)
    )


def test_t2_compatible_opaque_semantic_tokens_are_preserved_and_mapped() -> None:
    scene = _fixture()["scene"]
    scene["motion_channels"] = scene["motion_channels"][:1]
    opaque_name = "right.hand / primary"
    scene["motion_channels"][0]["semantic_target"] = opaque_name
    timeline = MotionTimeline.from_scene(scene)
    sample = timeline.evaluate(Fraction(27))
    target = SemanticTarget("fighter_a", "semantic_joint", opaque_name)
    assert sample.channels[0].target == target

    handle = object()
    bound = bind_motion_targets(sample, {target: handle})
    assert bound.channels[0].target == target
    assert bound.channels[0].target_handle is handle


def test_quaternion_channels_use_shortest_path_slerp() -> None:
    scene = _fixture()["scene"]
    scene["motion_channels"] = [
        {
            "channel_id": "fighter-a-facing",
            "binding_id": "fighter_a",
            "target_kind": "semantic_joint",
            "semantic_target": "torso",
            "value_unit": "quaternion",
            "interpolation": "linear",
            "keyframes": [
                {"frame": 0, "value": [0.0, 0.0, 0.0, 1.0]},
                {"frame": 24, "value": [0.0, 0.0, 1.0, 0.0]},
            ],
        }
    ]
    sample = MotionTimeline.from_scene(scene).evaluate(Fraction(12))
    quaternion = sample.channels[0].value
    assert quaternion == pytest.approx((0.0, 0.0, 2**-0.5, 2**-0.5))


def test_non_unit_quaternion_keys_normalize_endpoints_and_fractional_samples() -> None:
    scene = _fixture()["scene"]
    scene["motion_channels"] = [
        {
            "channel_id": "fighter-a-facing",
            "binding_id": "fighter_a",
            "target_kind": "semantic_joint",
            "semantic_target": "torso",
            "value_unit": "quaternion",
            "interpolation": "linear",
            "keyframes": [
                {"frame": 0, "value": [0.0, 0.0, 0.0, 2.0]},
                {"frame": 24, "value": [0.0, 0.0, 2.0, 0.0]},
            ],
        }
    ]
    timeline = MotionTimeline.from_scene(scene)
    start = timeline.evaluate(Fraction(0)).channels[0].value
    end = timeline.evaluate(Fraction(24)).channels[0].value
    clamped = timeline.evaluate(Fraction(30)).channels[0].value
    fractional = timeline.evaluate(Fraction(25, 2)).channels[0].value

    assert start == pytest.approx((0.0, 0.0, 0.0, 1.0))
    assert end == pytest.approx((0.0, 0.0, 1.0, 0.0))
    assert clamped == end
    assert math.hypot(*fractional) == pytest.approx(1.0)
    expected_slerp_angle = math.pi * Fraction(25, 48) / 2
    assert fractional == pytest.approx(
        (
            0.0,
            0.0,
            math.sin(float(expected_slerp_angle)),
            math.cos(float(expected_slerp_angle)),
        )
    )


def test_antipodal_quaternion_keys_take_the_shortest_equivalent_path() -> None:
    scene = _fixture()["scene"]
    scene["motion_channels"] = [
        {
            "channel_id": "fighter-a-facing",
            "binding_id": "fighter_a",
            "target_kind": "semantic_joint",
            "semantic_target": "torso",
            "value_unit": "quaternion",
            "interpolation": "linear",
            "keyframes": [
                {"frame": 0, "value": [0.0, 0.0, 0.0, 2.0]},
                {"frame": 24, "value": [0.0, 0.0, 0.0, -3.0]},
            ],
        }
    ]
    timeline = MotionTimeline.from_scene(scene)

    assert timeline.evaluate(Fraction(12)).channels[0].value == pytest.approx(
        (0.0, 0.0, 0.0, 1.0)
    )


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (lambda scene: scene["fps"].update(denominator=0), "fps"),
        (lambda scene: scene["contacts"][0].update(end_frame=27), "contact interval"),
        (lambda scene: scene["motion_channels"][0]["keyframes"][1].update(frame=0), "strictly increasing"),
    ],
)
def test_invalid_clock_intervals_and_key_order_fail_closed(
    mutation: Any, message: str
) -> None:
    scene = copy.deepcopy(_fixture()["scene"])
    mutation(scene)
    with pytest.raises(MotionContractError, match=message):
        MotionTimeline.from_scene(scene)


def test_out_of_range_seek_and_unmapped_semantic_target_fail_closed() -> None:
    timeline = _timeline()
    with pytest.raises(MotionContractError, match="outside the scene frame range"):
        timeline.evaluate(Fraction(96))
    with pytest.raises(MotionContractError, match="exact rational frame"):
        timeline.evaluate(27.5)  # type: ignore[arg-type]

    sample = timeline.evaluate(Fraction(27))
    with pytest.raises(MotionContractError, match="unmapped semantic target"):
        bind_motion_targets(sample, {})


def test_coordinate_residuals_keep_world_screen_and_layer_units_separate() -> None:
    sample = _timeline().evaluate(Fraction(27))
    hand = SemanticTarget("fighter_a", "semantic_joint", "right_hand")
    residuals = (
        CoordinateResidual(
            target=hand,
            frame=Fraction(27),
            coordinate_space="world_3d",
            coordinate_frame_id="scene-world-xyz",
            unit="m",
            components=(0.03, 0.04, 0.0),
        ),
        CoordinateResidual(
            target=hand,
            frame=Fraction(27),
            coordinate_space="projected_screen",
            coordinate_frame_id="render-pixel-xy",
            unit="px",
            components=(3.0, 4.0),
        ),
        CoordinateResidual(
            target=hand,
            frame=Fraction(27),
            coordinate_space="layer_depth",
            coordinate_frame_id="back-to-front-factor",
            unit="dimensionless",
            components=(0.02,),
        ),
    )

    inspection = inspect_motion_sample(sample, residuals)
    assert len(inspection.residual_groups) == 3
    by_space = {group.coordinate_space: group for group in inspection.residual_groups}
    assert by_space["world_3d"].unit == "m"
    assert by_space["world_3d"].maximum_magnitude == pytest.approx(0.05)
    assert by_space["projected_screen"].unit == "px"
    assert by_space["projected_screen"].maximum_magnitude == pytest.approx(5.0)
    assert by_space["layer_depth"].unit == "dimensionless"
    assert by_space["layer_depth"].maximum_magnitude == pytest.approx(0.02)


def test_coordinate_residual_mismatch_and_wrong_sample_frame_are_rejected() -> None:
    target = SemanticTarget("fighter_a", "semantic_joint", "right_hand")
    with pytest.raises(MotionInspectionError, match="unit"):
        CoordinateResidual(
            target=target,
            frame=Fraction(27),
            coordinate_space="world_3d",
            coordinate_frame_id="scene-world-xyz",
            unit="px",
            components=(1.0, 2.0, 3.0),
        )

    sample = _timeline().evaluate(Fraction(27))
    residual = CoordinateResidual(
        target=target,
        frame=Fraction(28),
        coordinate_space="world_3d",
        coordinate_frame_id="scene-world-xyz",
        unit="m",
        components=(0.0, 0.0, 0.0),
    )
    with pytest.raises(MotionInspectionError, match="must match sample frame"):
        inspect_motion_sample(sample, (residual,))
