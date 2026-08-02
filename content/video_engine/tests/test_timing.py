from __future__ import annotations

import json
from pathlib import Path

import pytest

from content.video_engine.src.timing import (
    TimingArtifactError,
    load_measured_timeline,
)


def _storyboard() -> dict:
    return {
        "scenes": [
            {"scene_id": 1, "timing": {"target_s": 5.0, "padding_s": 0.3}},
            {"scene_id": 2, "timing": {"target_s": 5.0, "padding_s": 0.2}},
        ]
    }


def _write_words(audio_dir: Path, scene_id: int, duration: float) -> None:
    audio_dir.mkdir(parents=True, exist_ok=True)
    audio_dir.joinpath(f"scene_{scene_id}.words.json").write_text(
        json.dumps(
            {
                "scene_id": scene_id,
                "duration_s": duration,
                "words": [{"w": "measured", "start_s": 0.0, "end_s": duration}],
            }
        ),
        encoding="utf-8",
    )


def test_timeline_uses_measured_words_and_storyboard_padding_in_order(
    tmp_path: Path,
) -> None:
    storyboard = _storyboard()
    _write_words(tmp_path, 1, 6.0)  # 20% over target_s, intentionally.
    _write_words(tmp_path, 2, 3.0)  # 40% under target_s, intentionally.

    timeline = load_measured_timeline(storyboard, tmp_path)

    assert [scene.scene_id for scene in timeline] == [1, 2]
    assert timeline[0].duration_s == pytest.approx(6.0)
    assert timeline[0].start_s == pytest.approx(0.0)
    assert timeline[0].end_s == pytest.approx(6.3)
    assert timeline[1].start_s == pytest.approx(6.3)
    assert timeline[1].end_s == pytest.approx(9.5)
    assert timeline.total_s == pytest.approx(9.5)


@pytest.mark.parametrize(
    ("payload", "match"),
    [
        ({"scene_id": 1, "duration_s": 0, "words": [{"w": "x", "start_s": 0, "end_s": 0}]}, "duration_s must be positive"),
        ({"scene_id": 1, "duration_s": "nan", "words": [{"w": "x", "start_s": 0, "end_s": 1}]}, "duration_s must be finite"),
        ({"scene_id": 1, "duration_s": 1, "words": [{"w": "x", "start_s": 0, "end_s": 2}]}, "exceeds duration_s"),
        ({"scene_id": 1, "duration_s": 1, "words": []}, "non-empty words array"),
    ],
)
def test_timeline_rejects_malformed_scene_artifacts(
    tmp_path: Path,
    payload: dict,
    match: str,
) -> None:
    storyboard = _storyboard()
    _write_words(tmp_path, 2, 3.0)
    tmp_path.joinpath("scene_1.words.json").write_text(
        json.dumps(payload),
        encoding="utf-8",
    )

    with pytest.raises(TimingArtifactError, match=rf"scene 1.*{match}"):
        load_measured_timeline(storyboard, tmp_path)


def test_timeline_missing_artifact_names_scene(tmp_path: Path) -> None:
    with pytest.raises(TimingArtifactError, match="scene 1.*missing word-timing"):
        load_measured_timeline(_storyboard(), tmp_path)


def test_timeline_accepts_zero_length_provider_word_alignment(tmp_path: Path) -> None:
    storyboard = _storyboard()
    _write_words(tmp_path, 2, 1.0)
    tmp_path.joinpath("scene_1.words.json").write_text(
        json.dumps(
            {
                "scene_id": 1,
                "duration_s": 1.0,
                "words": [{"w": "tap", "start_s": 0.5, "end_s": 0.5}],
            }
        ),
        encoding="utf-8",
    )

    assert load_measured_timeline(storyboard, tmp_path).total_s == pytest.approx(2.5)


def test_timeline_rejects_unexpected_and_duplicate_artifacts(tmp_path: Path) -> None:
    storyboard = _storyboard()
    _write_words(tmp_path, 1, 1.0)
    _write_words(tmp_path, 2, 1.0)
    _write_words(tmp_path, 3, 1.0)
    with pytest.raises(TimingArtifactError, match="scene 3.*unexpected"):
        load_measured_timeline(storyboard, tmp_path)

    # Distinct filenames can still identify the same scene; both must fail
    # closed instead of making filesystem order part of the clock contract.
    tmp_path.joinpath("scene_3.words.json").unlink()
    tmp_path.joinpath("scene_01.words.json").write_text(
        tmp_path.joinpath("scene_1.words.json").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    with pytest.raises(TimingArtifactError, match="scene 1.*duplicate"):
        load_measured_timeline(storyboard, tmp_path)
