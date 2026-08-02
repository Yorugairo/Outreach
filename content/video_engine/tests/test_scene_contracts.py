from __future__ import annotations

import json
from pathlib import Path

import pytest

from content.video_engine.src.models import SCENE_CLASS_REGISTRY
from content.video_engine.src.scenes import (
    BJJActionScene,
    CombatScienceScene,
    JointLeverageScene,
    MapNetworkScene,
    StickFigureScene,
    TitleConceptCard,
)
from content.video_engine.src.scenes.base import MANIM_AVAILABLE, ThemedScene, aspect_for_layout


ROOT = Path(__file__).resolve().parents[3]
FIXTURE = ROOT / "content" / "video_engine" / "tests" / "fixtures" / "armbar_storyboard.json"


def _storyboard() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _theme(storyboard: dict) -> dict:
    return storyboard["global_settings"]["theme"]


def test_scene_classes_match_the_frozen_registry() -> None:
    assert set(SCENE_CLASS_REGISTRY) == {
        "BJJActionScene",
        "CombatScienceScene",
        "StickFigureScene",
        "TitleConceptCard",
        "JointLeverageScene",
        "MapNetworkScene",
    }
    assert BJJActionScene is not None
    assert CombatScienceScene is not None


def test_aspect_layouts_are_first_class() -> None:
    assert aspect_for_layout("landscape_draft") == "landscape"
    assert aspect_for_layout("vertical_final") == "vertical"

    spec = _storyboard()["scenes"][0]
    landscape = StickFigureScene(spec, "landscape", 5.0, _theme(_storyboard()))
    vertical = StickFigureScene(spec, "vertical", 5.0, _theme(_storyboard()))
    assert landscape.aspect == "landscape"
    assert vertical.aspect == "vertical"


def test_stick_figure_entrance_and_duration_contract() -> None:
    storyboard = _storyboard()
    scene = StickFigureScene(
        storyboard["scenes"][0],
        "landscape",
        5.0,
        _theme(storyboard),
    )
    scene.construct()
    assert scene._first_animation_start is not None
    assert scene._first_animation_start <= 0.5
    assert scene._play_timeline == pytest.approx(5.0, abs=0.05)


def test_pose_resolution_rejects_missing_assets() -> None:
    storyboard = _storyboard()
    spec = storyboard["scenes"][0].copy()
    spec["parameters"] = {"poses": ["does-not-exist"]}
    scene = StickFigureScene(spec, "landscape", 3.0, _theme(storyboard))
    with pytest.raises(FileNotFoundError, match="pose asset"):
        scene.construct()


@pytest.mark.parametrize(
    ("scene_cls", "scene_index", "duration"),
    [
        (JointLeverageScene, 3, 8.0),
        (TitleConceptCard, 4, 7.0),
    ],
)
def test_remaining_scene_classes_obey_entrance_contract(scene_cls, scene_index, duration) -> None:
    storyboard = _storyboard()
    scene = scene_cls(
        storyboard["scenes"][scene_index],
        "landscape",
        duration,
        _theme(storyboard),
    )
    scene.construct()
    assert scene._first_animation_start is not None
    assert scene._first_animation_start <= 0.5


def test_map_scene_is_deterministic_without_randomness() -> None:
    storyboard = _storyboard()
    spec = {
        "scene_id": 9,
        "parameters": {
            "nodes": ["a", "b", "c"],
            "edges": [["a", "b"], ["b", "c"]],
        },
    }
    first = MapNetworkScene(spec, "vertical", 4.0, _theme(storyboard))
    second = MapNetworkScene(spec, "vertical", 4.0, _theme(storyboard))
    first.construct()
    second.construct()
    assert first.animation_log() == second.animation_log()


@pytest.mark.render_smoke
def test_render_smoke_has_an_explicit_local_dependency_reason() -> None:
    if not MANIM_AVAILABLE:
        pytest.skip("missing local dependency: manim")
    pytest.importorskip("shutil")
