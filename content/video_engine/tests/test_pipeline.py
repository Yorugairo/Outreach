from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from content.video_engine.cli import load_video_environment, main
from content.video_engine.src.models import StageOutput, VideoRun, VideoStageEvent
from content.video_engine.src.pipeline import (
    DEFAULT_STAGES,
    V3_STAGES,
    VideoPipeline,
    VideoPipelineGateApprovalError,
)
from content.video_engine.src.repositories.file_repository import (
    FileBackedVideoJobRepository,
)


def _pipeline(tmp_path: Path, **kwargs) -> tuple[VideoPipeline, FileBackedVideoJobRepository]:
    repository = FileBackedVideoJobRepository(tmp_path / "jobs")
    return VideoPipeline(repository, **kwargs), repository


def _write_animatic_evidence(job_dir: Path) -> None:
    animatic = job_dir / "animatic"
    animatic.mkdir(parents=True, exist_ok=True)
    (animatic / "preview.mp4").write_bytes(b"preview")
    (animatic / "shot-strip.png").write_bytes(b"strip")
    (animatic / "review-packet.json").write_text(
        json.dumps(
            {
                "preview_path": "animatic/preview.mp4",
                "shot_strip_path": "animatic/shot-strip.png",
                "approval_granted": False,
            }
        ),
        encoding="utf-8",
    )


def test_video_environment_loads_dotenv_without_overriding_process_values(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    dotenv = tmp_path / ".env"
    dotenv.write_text(
        "ELEVENLABS_API_KEY=file-key\n"
        "ELEVENLABS_VOICE_ID=file-voice\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("ELEVENLABS_API_KEY", "process-key")
    monkeypatch.delenv("ELEVENLABS_VOICE_ID", raising=False)

    load_video_environment(dotenv)

    assert os.environ["ELEVENLABS_API_KEY"] == "process-key"
    assert os.environ["ELEVENLABS_VOICE_ID"] == "file-voice"


def test_cli_loads_video_environment_at_startup(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[bool] = []
    monkeypatch.setattr(
        "content.video_engine.cli.load_video_environment",
        lambda: calls.append(True),
    )

    result = main(["--artifact-root", str(tmp_path / "jobs"), "status"])

    assert result == 0
    assert calls == [True]


def test_run_parks_at_both_human_gates_and_persists_ordered_events(
    tmp_path: Path,
) -> None:
    pipeline, repository = _pipeline(tmp_path)

    run = pipeline.start("content/bjj-registry/corpus/armbar-from-guard.json")

    assert run.status == "awaiting_gate_a"
    assert repository.job_dir(run.id).joinpath("job.json").exists()
    for directory in ("events", "audio", "video", "captions", "package", "qc"):
        assert repository.job_dir(run.id).joinpath(directory).is_dir()
    _write_animatic_evidence(repository.job_dir(run.id))

    pipeline, repository = _pipeline(
        tmp_path,
        storyboard_validator=lambda _path: (True, []),
        stage_fns={},
    )
    run = repository.load_run(run.id)
    assert run is not None
    run = pipeline.approve(run.id, "a")
    assert run.status == "awaiting_gate_b"

    run = pipeline.approve(run.id, "b")
    assert run.status == "packaged"
    assert run.current_stage == "completed"

    completed = [
        event.stage_name
        for event in repository.list_stage_events(run.id)
        if event.status == "completed"
    ]
    assert completed == DEFAULT_STAGES
    assert all(
        "cost_usd" in event.output_summary and "wall_time_s" in event.output_summary
        for event in repository.list_stage_events(run.id)
        if event.status == "completed"
    )
    names = [path.name for path in repository.job_dir(run.id).joinpath("events").glob("*.json")]
    assert names == sorted(names)
    assert names[0].startswith("0001_")


def test_resume_retries_the_first_non_completed_stage(tmp_path: Path) -> None:
    attempts = 0

    def fail_once(job, ctx):
        del job, ctx
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise RuntimeError("transient local failure")
        return StageOutput({"retried": True})

    pipeline, repository = _pipeline(
        tmp_path,
        stage_fns={"ingesting_source": fail_once},
    )
    run = pipeline.start("source.json")
    assert run.status == "failed"
    assert run.current_stage == "ingesting_source"

    run = pipeline.resume(run.id)

    assert attempts == 2
    assert run.status == "awaiting_gate_a"
    completed = [
        event.stage_name
        for event in repository.list_stage_events(run.id)
        if event.status == "completed"
    ]
    assert completed[:3] == DEFAULT_STAGES[:3]


def test_resume_does_not_cross_an_unapproved_gate(tmp_path: Path) -> None:
    pipeline, _repository = _pipeline(tmp_path)
    run = pipeline.start("source.json")

    resumed = pipeline.resume(run.id)

    assert resumed.status == "awaiting_gate_a"
    assert resumed.gate_a_status == "pending"


def test_armbar_v3_parks_at_visual_gate_before_animatic(
    tmp_path: Path,
) -> None:
    pipeline, repository = _pipeline(
        tmp_path,
        configs={
            "visual_v3_pilot_slugs": ["armbar-from-guard"],
            "art_bible_id": "combat-science-technical-cinematic-v1",
        },
    )

    run = pipeline.start(
        "content/bjj-registry/corpus/armbar-from-guard.json"
    )

    assert run.status == "awaiting_visual_gate"
    assert run.visual_gate_status == "pending"
    assert run.config_snapshot["pipeline_contract_version"] == 3
    assert run.config_snapshot["stage_order"] == V3_STAGES
    completed = [
        event.stage_name
        for event in repository.list_stage_events(run.id)
        if event.status == "completed"
    ]
    assert completed == V3_STAGES[: V3_STAGES.index("awaiting_visual_direction_approval")]
    assert "rendering_animatic" not in completed


def test_visual_gate_requires_rubric_and_resumes_to_gate_a(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pipeline, repository = _pipeline(
        tmp_path,
        configs={
            "visual_v3_pilot_slugs": ["armbar-from-guard"],
            "art_bible_id": "combat-science-technical-cinematic-v1",
        },
    )
    run = pipeline.start(
        "content/bjj-registry/corpus/armbar-from-guard.json"
    )

    with pytest.raises(VideoPipelineGateApprovalError, match="requires --rubric"):
        pipeline.approve(run.id, "visual")

    rubric = tmp_path / "rubric.json"
    rubric.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(
        pipeline,
        "_visual_direction_violations",
        lambda *_args, **_kwargs: [],
    )

    run = pipeline.approve(run.id, "visual", rubric_path=rubric)

    assert run.status == "awaiting_gate_a"
    assert run.visual_gate_status == "approved"
    assert repository.job_dir(run.id).joinpath("job.json").is_file()


def test_approve_rejects_the_wrong_gate(tmp_path: Path) -> None:
    pipeline, _repository = _pipeline(tmp_path)
    run = pipeline.start("source.json")

    with pytest.raises(ValueError, match="not awaiting_gate_b"):
        pipeline.approve(run.id, "b")


def test_approve_gate_a_revalidates_storyboard_and_blocks_invalid_runs(
    tmp_path: Path,
) -> None:
    def invalid_guard(_: Path) -> tuple[bool, list[str]]:
        return False, ["hook scene must be first", "invalid scene ordering"]

    pipeline, repository = _pipeline(
        tmp_path,
        storyboard_validator=invalid_guard,
    )
    run = repository.create_run(
        VideoRun(source_ref="source.json", status="awaiting_gate_a")
    )
    expected = repository.load_run(run.id)
    expected_events = repository.list_stage_events(run.id)
    with pytest.raises(VideoPipelineGateApprovalError) as exc_info:
        pipeline.approve(run.id, "a")

    assert exc_info.value.violations == ["hook scene must be first", "invalid scene ordering"]
    actual = repository.load_run(run.id)
    assert actual is not None
    assert actual.to_dict() == expected.to_dict()
    assert repository.list_stage_events(run.id) == expected_events


def test_gate_a_requires_animatic_evidence_for_visual_v2_runs(
    tmp_path: Path,
) -> None:
    pipeline, repository = _pipeline(
        tmp_path,
        storyboard_validator=lambda _path: (True, []),
    )
    run = repository.create_run(
        VideoRun(
            source_ref="source.json",
            status="awaiting_gate_a",
            config_snapshot={"pipeline_contract_version": 2},
        )
    )

    with pytest.raises(VideoPipelineGateApprovalError) as exc_info:
        pipeline.approve(run.id, "a")

    assert any("animatic review packet" in item for item in exc_info.value.violations)
    persisted = repository.load_run(run.id)
    assert persisted is not None
    assert persisted.gate_a_status == "pending"


def test_cli_gate_a_approval_prints_violations_for_invalid_storyboard(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    artifact_root = tmp_path / "jobs"
    repository = FileBackedVideoJobRepository(artifact_root)
    run = repository.create_run(VideoRun(source_ref="source.json", status="awaiting_gate_a"))

    result = main(
        [
            "--artifact-root",
            str(artifact_root),
            "approve",
            run.id,
            "--gate",
            "a",
        ]
    )

    payload = json.loads(capsys.readouterr().out)
    assert result == 1
    assert payload["valid"] is False
    assert isinstance(payload["errors"], list)
    assert payload["errors"]


def test_cli_status_prints_cost_and_wall_time_table(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    artifact_root = tmp_path / "jobs"
    repository = FileBackedVideoJobRepository(artifact_root)
    run = repository.create_run(VideoRun(source_ref="source.json", status="running"))
    repository.append_stage_event(
        VideoStageEvent(
            video_run_id=run.id,
            stage_name="ingesting_source",
            status="completed",
            output_summary={"cost_usd": 0.125, "wall_time_s": 1.5},
        )
    )

    result = main(
        [
            "--artifact-root",
            str(artifact_root),
            "status",
            run.id,
        ]
    )

    output = capsys.readouterr().out
    assert result == 0
    assert "COST_USD" in output
    assert "WALL_TIME_S" in output
    assert "ingesting_source" in output
    assert "0.1250" in output
    assert "1.500" in output


def test_pipeline_snapshots_selected_render_profile_configuration(
    tmp_path: Path,
) -> None:
    profiles = {
        "cinema_final": {
            "target": "landscape",
            "width": 2048,
            "height": 858,
            "fps": 24,
        }
    }
    pipeline, _repository = _pipeline(
        tmp_path,
        configs={"render_profiles": profiles},
    )

    run = pipeline.start("source.json", targets=["cinema_final"])

    assert run.config_snapshot["selected_render_profiles"] == ["cinema_final"]
    assert run.config_snapshot["render_profile_configs"] == profiles
