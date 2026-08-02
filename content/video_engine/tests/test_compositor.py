from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

import content.video_engine.src.services.compositor as compositor_module
from content.video_engine.src.models import StageContext, StageOutput, VideoRun
from content.video_engine.src.repositories.file_repository import (
    FileBackedVideoJobRepository,
)
from content.video_engine.src.services.captions import (
    CaptionService,
    ffmpeg_subtitle_filter,
    group_words,
    write_srt,
)
from content.video_engine.src.services.compositor import (
    CompositorService,
    build_video_filter,
)


def _storyboard() -> dict:
    return {
        "global_settings": {"targets": ["landscape"]},
        "scenes": [
            {
                "scene_id": 1,
                "act": "hook",
                "timing": {"target_s": 1.0, "padding_s": 0.0},
                "transition": {"in": "continuous"},
            },
            {
                "scene_id": 2,
                "act": "payoff",
                "timing": {"target_s": 1.0, "padding_s": 0.0},
                "transition": {"in": "crossfade"},
            },
        ],
    }


def _write_measured_inputs(tmp_path: Path, durations: list[float]) -> None:
    audio_dir = tmp_path / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    for scene_id, duration in enumerate(durations, start=1):
        audio_dir.joinpath(f"scene_{scene_id}.mp3").write_bytes(b"audio")
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


def test_caption_grouping_respects_word_limit_and_timing_gaps() -> None:
    words = [
        {"w": "Your", "start_s": 0.0, "end_s": 0.1},
        {"w": "hips", "start_s": 0.11, "end_s": 0.2},
        {"w": "are", "start_s": 0.21, "end_s": 0.3},
        {"w": "the", "start_s": 0.5, "end_s": 0.6},
        {"w": "fulcrum", "start_s": 0.61, "end_s": 0.8},
    ]

    cues = group_words(words, max_words=3, offset_s=2.0)

    assert [cue.text for cue in cues] == ["Your hips are", "the fulcrum"]
    assert cues[0].start_s == 2.0
    assert cues[1].start_s == 2.5


def test_srt_writer_and_windows_filter_escaping(tmp_path: Path) -> None:
    cues = group_words(
        [{"w": "Armbar", "start_s": 0.0, "end_s": 0.75}],
        max_words=3,
    )
    path = write_srt(cues, tmp_path / "captions.srt")

    assert "00:00:00,000 --> 00:00:00,750" in path.read_text(encoding="utf-8")
    filter_value = ffmpeg_subtitle_filter(path)
    assert "subtitles=filename=" in filter_value
    assert "MarginV=220" in filter_value


def test_caption_service_uses_three_words_vertical_and_seven_landscape(
    tmp_path: Path,
) -> None:
    storyboard = _storyboard()
    words_dir = tmp_path / "audio"
    words_dir.mkdir()
    for scene in storyboard["scenes"]:
        words_dir.joinpath(f"scene_{scene['scene_id']}.words.json").write_text(
            json.dumps(
                {
                    "scene_id": scene["scene_id"],
                    "duration_s": 1.0,
                    "words": [
                        {"w": word, "start_s": index * 0.1, "end_s": index * 0.1 + 0.09}
                        for index, word in enumerate(
                            ["one", "two", "three", "four", "five", "six"]
                        )
                    ],
                }
            ),
            encoding="utf-8",
        )

    service = CaptionService()
    vertical = service.build_cues(storyboard, words_dir, target="vertical")
    landscape = service.build_cues(storyboard, words_dir, target="landscape")

    assert max(len(cue.text.split()) for cue in vertical) <= 3
    assert max(len(cue.text.split()) for cue in landscape) <= 7


def test_video_filter_honors_crossfade_boundary() -> None:
    manifest = [
        {"path": "scene_1.mp4", "scene_ids": [1], "duration_s": 1.0},
        {"path": "scene_2.mp4", "scene_ids": [2], "duration_s": 1.0},
    ]

    graph, label = build_video_filter(_storyboard(), manifest)

    assert "tpad=stop_mode=clone:stop_duration=0.300000" in graph
    assert "settb=AVTB[v0pad]" in graph
    assert "[v1]settb=AVTB[v1tb]" in graph
    assert "xfade=transition=fade:duration=0.300000:offset=1.000000" in graph
    assert label == "join1"


def test_run_stage_uses_snapshotted_custom_profile(tmp_path: Path) -> None:
    repository = FileBackedVideoJobRepository(tmp_path / "jobs")
    run = VideoRun(
        source_ref="source.json",
        input_payload={"targets": ["cinema_final"]},
        config_snapshot={"selected_render_profiles": ["cinema_final"]},
    )
    repository.create_run(run)
    context = StageContext(
        repository=repository,
        configs={},
        job_dir=repository.job_dir(run.id),
    )
    context.job_dir.joinpath("storyboard.json").write_text(
        json.dumps(_storyboard()),
        encoding="utf-8",
    )
    selected: list[str] = []
    service = CompositorService()

    def assemble(storyboard, manifest_path, audio_dir, output_path, **kwargs):
        del storyboard, audio_dir, output_path, kwargs
        selected.append(manifest_path.parent.name)
        return StageOutput({"measured_lufs": -14.0})

    service.assemble_profile = assemble  # type: ignore[method-assign]
    output = service.run_stage(run, context)

    assert selected == ["cinema_final"]
    assert list(output.summary["profiles"]) == ["cinema_final"]


def test_compositor_uses_measured_timeline_when_target_estimates_differ(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    storyboard = _storyboard()
    _write_measured_inputs(tmp_path, [2.0, 0.5])  # target_s is 1.0 for both scenes.
    profile_dir = tmp_path / "video" / "landscape_final"
    profile_dir.mkdir(parents=True)
    manifest = profile_dir / "manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "segments": [
                    {"path": "scene_1.mp4", "scene_ids": [1], "duration_s": 2.3},
                    {"path": "scene_2.mp4", "scene_ids": [2], "duration_s": 0.8},
                ]
            }
        ),
        encoding="utf-8",
    )

    commands: list[list[str]] = []

    def runner(command, **kwargs):
        del kwargs
        command = list(command)
        commands.append(command)
        if command[-1] != "-":
            output = Path(command[-1])
            if output.suffix in {".mp4", ".wav"}:
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_bytes(b"placeholder")
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    service = compositor_module.CompositorService(runner=runner)
    loudness_paths: list[Path] = []

    def measure_loudness(path: Path) -> dict[str, str]:
        loudness_paths.append(path)
        return {
            "input_i": {
                1: "-20",
                2: "-15.5",
                3: "-14.2",
            }[len(loudness_paths)],
            "input_lra": "1",
            "input_tp": "-1",
            "input_thresh": "-24",
            "target_offset": "0",
        }

    service._measure_loudness = measure_loudness

    def normalize(_input: Path, output: Path, _measured: dict[str, str]) -> dict[str, str]:
        output.write_bytes(b"final")
        return {"output_i": "-1"}

    service._normalize_loudness = normalize
    monkeypatch.setattr(
        compositor_module,
        "probe_duration",
        lambda _path, runner=None: 2.5,  # measured 2 + 0.5; target total is 2.
    )

    output = service.assemble_profile(
        storyboard,
        manifest,
        tmp_path / "audio",
        profile_dir / "final.mp4",
    )

    assert output.summary["expected_duration_s"] == pytest.approx(2.5)
    assert output.summary["duration_s"] == pytest.approx(2.5)
    assert output.summary["measured_lufs"] == pytest.approx(-14.2)
    assert output.summary["loudness_correction_db"] == pytest.approx(1.5)
    assert len(loudness_paths) == 3
    filter_commands = [" ".join(command) for command in commands]
    assert any("atrim=duration=2.000000" in command for command in filter_commands)
    assert any("atrim=duration=0.500000" in command for command in filter_commands)
    assert any("volume=1.500000dB" in command for command in filter_commands)


def test_compositor_drift_is_measured_timeline_drift_not_target_drift(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    storyboard = _storyboard()
    _write_measured_inputs(tmp_path, [2.0, 0.5])
    profile_dir = tmp_path / "video" / "landscape_final"
    profile_dir.mkdir(parents=True)
    manifest = profile_dir / "manifest.json"
    manifest.write_text(
        json.dumps(
            {"segments": [{"path": "scene_1.mp4", "scene_ids": [1], "duration_s": 2.0}, {"path": "scene_2.mp4", "scene_ids": [2], "duration_s": 0.5}]}
        ),
        encoding="utf-8",
    )

    def runner(command, **kwargs):
        del kwargs
        command = list(command)
        if command[-1] != "-" and Path(command[-1]).suffix in {".mp4", ".wav"}:
            output = Path(command[-1])
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(b"placeholder")
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    service = compositor_module.CompositorService(runner=runner)
    service._measure_loudness = lambda _path: {
        "input_i": "-14",
        "input_lra": "1",
        "input_tp": "-1",
        "input_thresh": "-24",
        "target_offset": "0",
    }
    def normalize(_input, output, _measured):
        output.write_bytes(b"final")
        return {"output_i": "-14"}

    service._normalize_loudness = normalize
    monkeypatch.setattr(compositor_module, "probe_duration", lambda _path, runner=None: 3.0)

    with pytest.raises(ValueError, match="measured audio timeline"):
        service.assemble_profile(
            storyboard,
            manifest,
            tmp_path / "audio",
            profile_dir / "final.mp4",
        )


def test_compositor_schedules_available_sound_events_without_extending_clock(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    storyboard = _storyboard()
    _write_measured_inputs(tmp_path, [1.0, 1.0])
    profile_dir = tmp_path / "video" / "landscape_final"
    profile_dir.mkdir(parents=True)
    manifest = profile_dir / "manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "segments": [
                    {"path": "scene_1.mp4", "scene_ids": [1], "duration_s": 1.0},
                    {"path": "scene_2.mp4", "scene_ids": [2], "duration_s": 1.0},
                ]
            }
        ),
        encoding="utf-8",
    )
    cue = tmp_path / "contact.wav"
    cue.write_bytes(b"cue")
    sound_manifest = tmp_path / "audio" / "sound_manifest.json"
    sound_manifest.write_text(
        json.dumps(
            {
                "events": [
                    {
                        "cue": "contact",
                        "at_s": 0.75,
                        "gain_db": -12,
                        "asset_path": str(cue),
                        "available": True,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    commands: list[list[str]] = []

    def runner(command, **kwargs):
        del kwargs
        command = list(command)
        commands.append(command)
        if command[-1] != "-" and Path(command[-1]).suffix in {".mp4", ".wav"}:
            Path(command[-1]).write_bytes(b"output")
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    service = CompositorService(runner=runner)
    service._measure_loudness = lambda _path: {
        "input_i": "-14",
        "input_lra": "1",
        "input_tp": "-1",
        "input_thresh": "-24",
        "target_offset": "0",
    }
    service._normalize_loudness = lambda _input, output, _measured: (
        output.write_bytes(b"final") or {"output_i": "-14"}
    )
    monkeypatch.setattr(compositor_module, "probe_duration", lambda _path, runner=None: 2.0)

    output = service.assemble_profile(
        storyboard,
        manifest,
        tmp_path / "audio",
        profile_dir / "final.mp4",
        sound_manifest_path=sound_manifest,
    )

    mix_commands = [
        " ".join(command)
        for command in commands
        if "-filter_complex" in command and "adelay=" in " ".join(command)
    ]
    assert mix_commands
    assert "adelay=delays=750:all=1" in mix_commands[0]
    assert "volume=-12.000000dB" in mix_commands[0]
    assert output.summary["sound_event_count"] == 1
    assert output.summary["expected_duration_s"] == 2.0


@pytest.mark.assembly
def test_ffmpeg_assembly_produces_normalized_final(tmp_path: Path) -> None:
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        pytest.skip("ffmpeg and ffprobe are required for assembly smoke")
    storyboard = _storyboard()
    profile_dir = tmp_path / "video" / "landscape_final"
    audio_dir = tmp_path / "audio"
    profile_dir.mkdir(parents=True)
    audio_dir.mkdir()
    segments = []
    colors = ["blue", "green"]
    for scene, color in zip(storyboard["scenes"], colors):
        scene_id = scene["scene_id"]
        video = profile_dir / f"scene_{scene_id}.mp4"
        audio = audio_dir / f"scene_{scene_id}.mp3"
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-f",
                "lavfi",
                "-i",
                f"color=c={color}:s=320x180:d=1:r=15",
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                str(video),
            ],
            check=True,
            capture_output=True,
        )
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-f",
                "lavfi",
                "-i",
                "sine=frequency=440:duration=1",
                "-codec:a",
                "libmp3lame",
                str(audio),
            ],
            check=True,
            capture_output=True,
        )
        audio_dir.joinpath(f"scene_{scene_id}.words.json").write_text(
            json.dumps(
                {
                    "scene_id": scene_id,
                    "duration_s": 1.0,
                    "words": [{"w": "test", "start_s": 0.0, "end_s": 0.8}],
                }
            ),
            encoding="utf-8",
        )
        segments.append(
            {"path": video.name, "scene_ids": [scene_id], "duration_s": 1.0}
        )
    manifest = profile_dir / "manifest.json"
    manifest.write_text(json.dumps({"segments": segments}), encoding="utf-8")

    output = CompositorService().assemble_profile(
        storyboard,
        manifest,
        audio_dir,
        profile_dir / "final.mp4",
    )

    assert profile_dir.joinpath("final.mp4").exists()
    assert abs(float(output.summary["measured_lufs"]) - -14.0) <= 1.0
