from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft7Validator

from content.video_engine.src.models import (
    SCENE_CLASS_REGISTRY,
    STORYBOARD_CONTRACT_VERSION,
    VIDEO_PIPELINE_CONTRACT_VERSION,
)


ROOT = Path(__file__).resolve().parents[3]
ENGINE_ROOT = ROOT / "content" / "video_engine"


def test_runtime_schema_is_verbatim_spec_copy() -> None:
    assert (
        ENGINE_ROOT.joinpath("configs/storyboard.schema.json").read_text(encoding="utf-8")
        == ROOT.joinpath("docs/content-video-engine/storyboard.schema.json").read_text(
            encoding="utf-8"
        )
    )


def test_armbar_fixture_validates_against_storyboard_contract() -> None:
    schema = json.loads(
        ENGINE_ROOT.joinpath("configs/storyboard.schema.json").read_text(encoding="utf-8")
    )
    storyboard = json.loads(
        ENGINE_ROOT.joinpath("tests/fixtures/armbar_storyboard.json").read_text(
            encoding="utf-8"
        )
    )

    assert list(Draft7Validator(schema).iter_errors(storyboard)) == []


def test_render_profiles_match_the_documented_ladder() -> None:
    profiles = json.loads(
        ENGINE_ROOT.joinpath("configs/render_profiles.json").read_text(encoding="utf-8")
    )

    assert (profiles["landscape_draft"]["width"], profiles["landscape_draft"]["fps"]) == (
        854,
        15,
    )
    assert (
        profiles["landscape_final"]["width"],
        profiles["landscape_final"]["height"],
        profiles["landscape_final"]["fps"],
    ) == (1920, 1080, 60)
    assert (
        profiles["vertical_final"]["width"],
        profiles["vertical_final"]["height"],
        profiles["vertical_final"]["fps"],
    ) == (1080, 1920, 30)


def test_contract_versions_and_scene_registry_are_frozen() -> None:
    assert STORYBOARD_CONTRACT_VERSION == "storyboard.v2.1"
    assert VIDEO_PIPELINE_CONTRACT_VERSION == 3
    assert set(SCENE_CLASS_REGISTRY) == {
        "BJJActionScene",
        "CombatScienceScene",
        "StickFigureScene",
        "TitleConceptCard",
        "JointLeverageScene",
        "MapNetworkScene",
    }


def test_combat_science_channel_enables_only_the_armbar_v3_pilot() -> None:
    channel = json.loads(
        ENGINE_ROOT.joinpath("configs/channels/combat-science.json").read_text(
            encoding="utf-8"
        )
    )

    assert channel["art_bible_id"] == "combat-science-technical-cinematic-v1"
    assert channel["visual_v3_pilot_slugs"] == ["armbar-from-guard"]
    assert channel["theme"]["background_color"] == "#0B0F14"
    assert channel["theme"]["measurement_font"] == "Roboto Mono"
