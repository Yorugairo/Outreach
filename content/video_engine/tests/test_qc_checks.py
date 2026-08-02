from __future__ import annotations

import json
from pathlib import Path

import pytest

from content.video_engine.src.guards.qc_checks import run_qc_checks


FIXTURE = Path(__file__).parent / "fixtures" / "armbar_storyboard.json"


def _storyboard() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _write_valid_artifacts(
    tmp_path: Path,
    *,
    measured_durations: list[float] | None = None,
) -> float:
    storyboard = _storyboard()
    durations = measured_durations or [
        float(scene["timing"]["target_s"]) for scene in storyboard["scenes"]
    ]
    (tmp_path / "audio").mkdir(parents=True)
    (tmp_path / "video" / "landscape_final").mkdir(parents=True)
    (tmp_path / "video" / "vertical_final").mkdir(parents=True)
    (tmp_path / "captions").mkdir()
    (tmp_path / "package").mkdir()
    for scene, duration in zip(storyboard["scenes"], durations):
        (tmp_path / "audio" / f"scene_{scene['scene_id']}.words.json").write_text(
            json.dumps(
                {
                    "scene_id": scene["scene_id"],
                    "duration_s": duration,
                    "words": [{"w": "word", "start_s": 0.0, "end_s": duration - 0.1}],
                }
            ),
            encoding="utf-8",
        )
    manifest = {
        "segments": [
            {
                "path": "scene.mp4",
                "scene_ids": [scene["scene_id"]],
                "duration_s": (
                    scene["timing"]["target_s"]
                    + scene["timing"].get("padding_s", 0.0)
                ),
            }
            for scene in storyboard["scenes"]
        ]
    }
    for profile in ("landscape_final", "vertical_final"):
        (tmp_path / "video" / profile / "final.mp4").write_bytes(b"placeholder-final")
        (tmp_path / "video" / profile / "manifest.json").write_text(
            json.dumps(manifest), encoding="utf-8"
        )
    for name in ("landscape_final.srt", "vertical_final.srt"):
        (tmp_path / "captions" / name).write_text("1\n00:00:00,000 --> 00:00:01,000\nword\n", encoding="utf-8")
    metadata = {
        "titles": ["Title one", "Title two"],
        "description": "Read more at https://example.test/article?utm_source=youtube&utm_medium=longform&utm_campaign=armbar",
        "tags": ["bjj"],
        "chapters": [{"start_s": 0.0, "title": "Hook"}],
        "disclosure": {"required": False, "reason": None},
        "upload_checklist": ["choose title"],
    }
    (tmp_path / "package" / "metadata.json").write_text(json.dumps(metadata), encoding="utf-8")

    return sum(
        duration + float(scene["timing"].get("padding_s", 0.0))
        for scene, duration in zip(storyboard["scenes"], durations)
    )


def _probe(expected: float):
    def probe(_path: Path) -> float:
        return expected

    return probe


def _check(result: dict, check_id: str) -> dict:
    return next(check for check in result["checks"] if check["check_id"] == check_id)


def test_complete_artifact_tree_passes_and_writes_report(tmp_path: Path) -> None:
    expected = _write_valid_artifacts(tmp_path)
    result = run_qc_checks(
        _storyboard(),
        tmp_path,
        {"measured_lufs": -14.2},
        duration_probe=_probe(expected),
    )
    assert result["overall"] == "pass"
    assert all(check["status"] == "pass" for check in result["checks"])
    report = tmp_path / "qc" / "report.json"
    assert report.exists()
    assert json.loads(report.read_text(encoding="utf-8")) == result


def test_duration_drift_over_two_percent_fails(tmp_path: Path) -> None:
    expected = _write_valid_artifacts(tmp_path)
    path = tmp_path / "video" / "landscape_final" / "manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    manifest["segments"][0]["duration_s"] += 2
    path.write_text(json.dumps(manifest), encoding="utf-8")
    result = run_qc_checks(
        _storyboard(),
        tmp_path,
        {"integrated_lufs": -14},
        duration_probe=lambda final: expected * (1.1 if final.parent.name == "landscape_final" else 1.0),
    )
    assert result["overall"] == "fail"
    assert _check(result, "duration_drift")["status"] == "fail"


def test_words_coverage_and_caption_presence_fail_closed(tmp_path: Path) -> None:
    expected = _write_valid_artifacts(tmp_path)
    (tmp_path / "audio" / "scene_3.words.json").unlink()
    (tmp_path / "captions" / "vertical_final.srt").unlink()
    result = run_qc_checks(
        _storyboard(), tmp_path, {"loudness_lufs": -14}, duration_probe=_probe(expected)
    )
    assert _check(result, "words_coverage")["status"] == "fail"
    assert _check(result, "captions")["status"] == "fail"


def test_loudness_and_metadata_fields_are_required(tmp_path: Path) -> None:
    expected = _write_valid_artifacts(tmp_path)
    (tmp_path / "package" / "metadata.json").write_text(json.dumps({"titles": []}), encoding="utf-8")
    result = run_qc_checks(
        _storyboard(), tmp_path, {"measured_lufs": -10}, duration_probe=_probe(expected)
    )
    assert _check(result, "loudness")["status"] == "fail"
    assert _check(result, "metadata")["status"] == "fail"


def test_loudness_check_ignores_target_fields(tmp_path: Path) -> None:
    expected = _write_valid_artifacts(tmp_path)
    result = run_qc_checks(
        _storyboard(),
        tmp_path,
        {
            "measured_lufs": -14.2,
            "loudness_target_lufs": -14.0,
            "profiles": {
                "landscape_final": {"loudness_target_lufs": -14.0},
                "vertical_final": {"loudness_target_lufs": -14.0},
            },
        },
        duration_probe=_probe(expected),
    )
    loudness = _check(result, "loudness")
    assert loudness["status"] == "pass"
    assert loudness["detail"] == "measured -14.2 LUFS"


def test_silent_gap_over_500ms_is_reported(tmp_path: Path) -> None:
    expected = _write_valid_artifacts(tmp_path)
    path = tmp_path / "audio" / "scene_1.words.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    duration = data["duration_s"]
    data["words"] = [
        {"w": "first", "start_s": 0.0, "end_s": 0.4},
        {"w": "second", "start_s": 1.1, "end_s": 1.2},
    ]
    data["duration_s"] = duration
    path.write_text(json.dumps(data), encoding="utf-8")
    result = run_qc_checks(
        _storyboard(), tmp_path, {"measured_lufs": -14}, duration_probe=_probe(expected)
    )
    assert result["overall"] == "fail"
    assert _check(result, "silent_gaps")["status"] == "fail"


def test_duration_qc_passes_all_selected_profiles_on_measured_timeline(
    tmp_path: Path,
) -> None:
    storyboard = _storyboard()
    target_durations = [float(scene["timing"]["target_s"]) for scene in storyboard["scenes"]]
    measured_durations = [duration * 1.2 for duration in target_durations]
    expected = _write_valid_artifacts(tmp_path, measured_durations=measured_durations)
    summary = {
        "measured_lufs": -14,
        "profiles": {"landscape_final": {}, "vertical_final": {}},
    }
    probed: list[str] = []

    def probe(final_path: Path) -> float:
        probed.append(final_path.parent.name)
        return expected

    result = run_qc_checks(storyboard, tmp_path, summary, duration_probe=probe)
    duration_check = _check(result, "duration_drift")
    assert duration_check["status"] == "pass"
    assert "measured_audio=" in duration_check["detail"]
    assert probed == ["landscape_final", "vertical_final"]


def test_duration_qc_fails_when_selected_final_is_missing(tmp_path: Path) -> None:
    expected = _write_valid_artifacts(tmp_path)
    (tmp_path / "video" / "vertical_final" / "final.mp4").unlink()
    result = run_qc_checks(
        _storyboard(),
        tmp_path,
        {"profiles": {"landscape_final": {}, "vertical_final": {}}},
        duration_probe=_probe(expected),
    )
    duration_check = _check(result, "duration_drift")
    assert duration_check["status"] == "fail"
    assert "vertical_final" in duration_check["detail"]
    assert "missing" in duration_check["detail"]


def test_duration_qc_fails_when_selected_final_is_unprobeable(tmp_path: Path) -> None:
    expected = _write_valid_artifacts(tmp_path)

    def probe(final_path: Path) -> float:
        if final_path.parent.name == "vertical_final":
            raise OSError("ffprobe failed")
        return expected

    result = run_qc_checks(
        _storyboard(),
        tmp_path,
        {"profiles": {"landscape_final": {}, "vertical_final": {}}},
        duration_probe=probe,
    )
    duration_check = _check(result, "duration_drift")
    assert duration_check["status"] == "fail"
    assert "vertical_final" in duration_check["detail"]
    assert "unprobeable" in duration_check["detail"]
