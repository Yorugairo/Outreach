from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from content.video_engine.src.models import StageContext, StageOutput, VideoRun
from content.video_engine.src.pipeline import (
    DEFAULT_STAGES,
    VideoPipeline,
    build_default_stage_fns,
)
from content.video_engine.src.repositories.file_repository import (
    FileBackedVideoJobRepository,
)
from content.video_engine.src.services.editorial import EditorialService
from content.video_engine.src.timing import load_measured_timeline


ROOT = Path(__file__).resolve().parents[3]
ENGINE_ROOT = ROOT / "content" / "video_engine"


def _run_ffmpeg(command: list[str]) -> None:
    subprocess.run(command, check=True, capture_output=True)


def _mock_audio(job: VideoRun, ctx: StageContext) -> StageOutput:
    storyboard = json.loads(
        ctx.job_dir.joinpath("storyboard.json").read_text(encoding="utf-8")
    )
    audio_dir = ctx.job_dir / "audio"
    audio_dir.mkdir(exist_ok=True)
    measured_durations = {
        int(scene["scene_id"]): float(scene["timing"]["target_s"]) * 1.2
        for scene in storyboard["scenes"]
    }
    longest = max(measured_durations.values())
    source_audio = audio_dir / ".mock-tone.mp3"
    _run_ffmpeg(
        [
            "ffmpeg",
            "-y",
            "-f",
            "lavfi",
            "-i",
            f"sine=frequency=440:duration={longest + 0.5}",
            "-codec:a",
            "libmp3lame",
            str(source_audio),
        ]
    )
    for scene in storyboard["scenes"]:
        scene_id = int(scene["scene_id"])
        duration = measured_durations[scene_id]
        shutil.copyfile(source_audio, audio_dir / f"scene_{scene_id}.mp3")
        words = str(scene["narration_text"]).split()
        step = duration / len(words)
        audio_dir.joinpath(f"scene_{scene_id}.words.json").write_text(
            json.dumps(
                {
                    "scene_id": scene_id,
                    "duration_s": duration,
                    "words": [
                        {
                            "w": word,
                            "start_s": round(index * step, 6),
                            "end_s": round((index + 1) * step, 6),
                        }
                        for index, word in enumerate(words)
                    ],
                }
            ),
            encoding="utf-8",
        )
    return StageOutput(
        {
            "scene_count": len(storyboard["scenes"]),
            "provider": "mock",
            "cost_usd": 0.0,
        }
    )


def _mock_render(job: VideoRun, ctx: StageContext) -> StageOutput:
    del job
    storyboard = json.loads(
        ctx.job_dir.joinpath("storyboard.json").read_text(encoding="utf-8")
    )
    duration = load_measured_timeline(storyboard, ctx.job_dir / "audio").total_s
    manifests = {}
    for profile, color in (
        ("landscape_final", "blue"),
        ("vertical_final", "green"),
    ):
        profile_dir = ctx.job_dir / "video" / profile
        profile_dir.mkdir(parents=True, exist_ok=True)
        clip = profile_dir / "seq_1-11.mp4"
        _run_ffmpeg(
            [
                "ffmpeg",
                "-y",
                "-f",
                "lavfi",
                "-i",
                f"color=c={color}:s=320x180:d={duration}:r=15",
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                str(clip),
            ]
        )
        manifest = {
            "segments": [
                {
                    "path": clip.relative_to(ctx.job_dir).as_posix(),
                    "scene_ids": [
                        int(scene["scene_id"]) for scene in storyboard["scenes"]
                    ],
                    "duration_s": duration,
                }
            ]
        }
        profile_dir.joinpath("manifest.json").write_text(
            json.dumps(manifest),
            encoding="utf-8",
        )
        manifests[profile] = manifest
    return StageOutput(
        {
            "profiles": sorted(manifests),
            "manifests": manifests,
            "cost_usd": 0.0,
        }
    )


def _mock_editorial(job: VideoRun, ctx: StageContext) -> StageOutput:
    service = EditorialService()
    outputs = {}
    for profile in job.config_snapshot["selected_render_profiles"]:
        target = str(job.config_snapshot["render_profile_configs"][profile]["target"])
        source_manifest = json.loads(
            (ctx.job_dir / "video" / profile / "manifest.json").read_text(
                encoding="utf-8"
            )
        )
        segment = source_manifest["segments"][0]
        source = ctx.job_dir / segment["path"]
        output_dir = ctx.job_dir / "editorial" / target
        output_dir.mkdir(parents=True, exist_ok=True)
        output = output_dir / "editorial.mp4"
        shutil.copyfile(source, output)
        manifest = service.build_manifest(
            [
                {
                    "id": "mock-editorial",
                    "path": str(source),
                    "duration_s": segment["duration_s"],
                    "scene_ids": segment["scene_ids"],
                    "transition": "continuous",
                }
            ],
            aspect=target,
        )
        service.write_manifest(manifest, output_dir / "edit_manifest.json")
        if not (ctx.job_dir / "edit_manifest.json").exists():
            service.write_manifest(manifest, ctx.job_dir / "edit_manifest.json")
            service.write_manifest(
                manifest, ctx.job_dir / "editorial" / "edit_manifest.json"
            )
        outputs[profile] = {"output_path": str(output)}
    return StageOutput({"profiles": outputs, "cost_usd": 0.0})


def test_armbar_v3_builds_original_style_board_before_any_provider_call(
    tmp_path: Path,
) -> None:
    repository = FileBackedVideoJobRepository(tmp_path / "jobs")
    channel = json.loads(
        ENGINE_ROOT.joinpath("configs/channels/combat-science.json").read_text(
            encoding="utf-8"
        )
    )
    pipeline = VideoPipeline(
        repository,
        configs={
            "project_root": ROOT,
            "video_engine_root": ENGINE_ROOT,
            "channel_configs": {"combat-science": channel},
            "render_profiles": json.loads(
                ENGINE_ROOT.joinpath("configs/render_profiles.json").read_text(
                    encoding="utf-8"
                )
            ),
        },
        stage_fns=build_default_stage_fns(),
    )

    run = pipeline.start(
        "content/bjj-registry/corpus/armbar-from-guard.json",
        targets=["landscape"],
    )
    job_dir = repository.job_dir(run.id)

    assert run.status == "awaiting_visual_gate"
    assert run.visual_gate_status == "pending"
    assert "synthesizing_audio" not in run.summary["stages"]
    storyboard = json.loads(
        job_dir.joinpath("storyboard.json").read_text(encoding="utf-8")
    )
    treatment = json.loads(
        job_dir.joinpath("visual_treatment.json").read_text(encoding="utf-8")
    )
    board = json.loads(
        job_dir.joinpath("style_board/style_board.json").read_text(
            encoding="utf-8"
        )
    )
    assert storyboard["schema_version"] == "2.1.0"
    assert all(
        scene["manim_class"] != "BJJActionScene"
        for scene in storyboard["scenes"]
        if scene["visual_type"] == "bjj_action"
    )
    assert {item["composition"] for item in treatment["shots"]} >= {
        "result_hero",
        "wide_spatial_setup",
        "contact_macro_context_inset",
        "mechanic_transition",
        "wrong_right_matched_split",
        "living_geometry_reveal",
        "held_recognition_frame",
        "cta_card",
    }
    assert sum(item.get("living_diagram") is True for item in treatment["shots"]) >= 2
    assert len(board["stills"]) == 6
    assert board["provider_calls"] == 0
    assert board["approval_granted"] is False


@pytest.mark.integration
def test_armbar_pipeline_reaches_packaged_with_mocked_provider_and_render(
    tmp_path: Path,
) -> None:
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        pytest.skip("ffmpeg and ffprobe are required for integration assembly")
    repository = FileBackedVideoJobRepository(tmp_path / "jobs")
    stage_fns = build_default_stage_fns()
    stage_fns["synthesizing_audio"] = _mock_audio
    stage_fns["rendering_scenes"] = _mock_render
    stage_fns["editing_picture"] = _mock_editorial
    pipeline = VideoPipeline(
        repository,
        configs={
            "project_root": ROOT,
            "video_engine_root": ENGINE_ROOT,
            "render_profiles": json.loads(
                ENGINE_ROOT.joinpath("configs/render_profiles.json").read_text(
                    encoding="utf-8"
                )
            ),
            "article_url_template": (
                "https://nationalbjjregistry.com/techniques/{position}/{slug}"
            ),
            "registry_url": "https://nationalbjjregistry.com",
            "animatic_motion_render": False,
        },
        stage_fns=stage_fns,
    )

    run = pipeline.start(
        "content/bjj-registry/corpus/armbar-from-guard.json"
    )
    assert run.status == "awaiting_gate_a"
    assert repository.job_dir(run.id).joinpath("storyboard.json").exists()

    run = pipeline.approve(run.id, "a")
    assert run.status == "awaiting_gate_b"
    storyboard = json.loads(
        repository.job_dir(run.id).joinpath("storyboard.json").read_text(
            encoding="utf-8"
        )
    )
    target_duration = sum(
        float(scene["timing"]["target_s"])
        + float(scene["timing"].get("padding_s", 0.0))
        for scene in storyboard["scenes"]
    )
    measured_timeline = load_measured_timeline(
        storyboard,
        repository.job_dir(run.id) / "audio",
    )
    assert abs(measured_timeline.total_s - target_duration) / target_duration >= 0.1
    qc_report = json.loads(
        repository.job_dir(run.id).joinpath("qc/report.json").read_text(
            encoding="utf-8"
        )
    )
    assert qc_report["overall"] == "pass"
    duration_check = next(
        check
        for check in qc_report["checks"]
        if check["check_id"] == "duration_drift"
    )
    assert "measured_audio=" in duration_check["detail"]
    assert (
        run.summary["stages"]["packaging"]["duration_s"]
        == pytest.approx(measured_timeline.total_s, abs=0.0005)
    )

    run = pipeline.approve(run.id, "b")
    assert run.status == "packaged"
    completed = [
        event.stage_name
        for event in repository.list_stage_events(run.id)
        if event.status == "completed"
    ]
    assert completed == DEFAULT_STAGES
    for path in (
        "video/landscape_final/final.mp4",
        "video/vertical_final/final.mp4",
        "captions/landscape.srt",
        "captions/vertical.srt",
        "package/metadata.json",
        "package/embed_payload.json",
        "qc/report.json",
    ):
        assert repository.job_dir(run.id).joinpath(path).is_file(), path
