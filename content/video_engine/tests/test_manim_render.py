from __future__ import annotations

import json
from pathlib import Path

import pytest

from content.video_engine.src.scenes.base import MANIM_AVAILABLE
from content.video_engine.src.services.manim_render import (
    DurationMismatchError,
    ManimRenderService,
    RenderUnit,
    group_render_units,
    load_render_profiles,
    render_smoke_skip_reason,
)


ROOT = Path(__file__).resolve().parents[3]
FIXTURE = ROOT / "content" / "video_engine" / "tests" / "fixtures" / "armbar_storyboard.json"


def _storyboard() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_continuous_scenes_group_only_when_classes_are_compatible() -> None:
    units = group_render_units(_storyboard()["scenes"])
    assert [unit.scene_ids for unit in units] == [(1, 2), (3,), (4,), (5,)]
    assert units[0].output_stem() == "seq_1-2"
    assert units[1].output_stem() == "scene_3"


def test_explicit_cut_starts_a_new_unit() -> None:
    scenes = [
        {"scene_id": 1, "manim_class": "StickFigureScene"},
        {
            "scene_id": 2,
            "manim_class": "StickFigureScene",
            "transition": {"in": "hard_cut"},
        },
        {"scene_id": 3, "manim_class": "StickFigureScene"},
    ]
    assert [unit.scene_ids for unit in group_render_units(scenes)] == [(1,), (2, 3)]


def test_renderer_writes_profile_manifest_with_relative_paths(tmp_path: Path) -> None:
    storyboard = _storyboard()
    expected: dict[str, float] = {}

    def fake_render(unit: RenderUnit, _profile: dict, output: Path, _profile_name: str) -> Path:
        duration = sum(float((scene.get("timing") or {}).get("target_s", 0.0)) for scene in unit.scenes)
        expected[str(output)] = duration
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(b"fake-mp4")
        return output

    service = ManimRenderService(
        tmp_path,
        profiles=load_render_profiles(),
        render_unit_fn=fake_render,
        duration_probe=lambda path: expected[str(path)],
    )
    manifest = service.render_storyboard(storyboard, "landscape_draft")
    assert [segment["scene_ids"] for segment in manifest["segments"]] == [
        [1, 2],
        [3],
        [4],
        [5],
    ]
    assert all(not Path(segment["path"]).is_absolute() for segment in manifest["segments"])
    manifest_path = tmp_path / "video" / "landscape_draft" / "manifest.json"
    assert json.loads(manifest_path.read_text(encoding="utf-8")) == manifest


def test_renderer_rejects_duration_drift(tmp_path: Path) -> None:
    storyboard = _storyboard()

    def fake_render(_unit, _profile, output: Path, _profile_name: str) -> Path:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(b"fake-mp4")
        return output

    service = ManimRenderService(
        tmp_path,
        render_unit_fn=fake_render,
        duration_probe=lambda _path: 99.0,
    )
    with pytest.raises(DurationMismatchError, match="scene ids"):
        service.render_storyboard(storyboard, "landscape_draft")


def test_renderer_attaches_word_timings_from_an_external_audio_directory(
    tmp_path: Path,
) -> None:
    storyboard = _storyboard()
    storyboard["scenes"] = storyboard["scenes"][:1]
    audio_dir = tmp_path / "external-audio"
    audio_dir.mkdir()
    audio_dir.joinpath("scene_1.words.json").write_text(
        json.dumps(
            {
                "scene_id": 1,
                "duration_s": 4.7,
                "words": [{"w": "leverage", "start_s": 1.25, "end_s": 2.0}],
            }
        ),
        encoding="utf-8",
    )
    observed: list[float] = []

    def fake_render(unit, _profile, output: Path, _profile_name: str) -> Path:
        observed.append(unit.scenes[0]["word_timings"][0]["start_s"])
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(b"fake-mp4")
        return output

    service = ManimRenderService(
        tmp_path / "job",
        render_unit_fn=fake_render,
        duration_probe=lambda _path: 5.0,
    )
    service.render_storyboard(
        storyboard,
        "landscape_draft",
        audio_dir=audio_dir,
    )

    assert observed == [1.25]


@pytest.mark.render_smoke
def test_render_smoke_renders_first_two_armbar_scenes_as_one_sequence(
    tmp_path: Path,
) -> None:
    reason = render_smoke_skip_reason()
    if reason:
        pytest.skip(reason)
    assert MANIM_AVAILABLE
    storyboard = _storyboard()
    storyboard["scenes"] = storyboard["scenes"][:2]
    audio_dir = tmp_path / "audio"
    audio_dir.mkdir()
    for scene in storyboard["scenes"]:
        timing = scene["timing"]
        measured_duration = float(timing["target_s"]) - float(
            timing.get("padding_s", 0.0)
        )
        audio_dir.joinpath(f"scene_{scene['scene_id']}.words.json").write_text(
            json.dumps(
                {
                    "scene_id": scene["scene_id"],
                    "duration_s": measured_duration,
                    "words": [
                        {
                            "w": "motion",
                            "start_s": 0.0,
                            "end_s": measured_duration,
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )

    manifest = ManimRenderService(tmp_path).render_storyboard(
        storyboard,
        "landscape_draft",
        audio_dir=audio_dir,
    )

    assert manifest["segments"][0]["scene_ids"] == [1, 2]
    assert tmp_path.joinpath(manifest["segments"][0]["path"]).is_file()
