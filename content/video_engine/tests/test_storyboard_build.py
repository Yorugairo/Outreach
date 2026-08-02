from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import Draft7Validator

from content.video_engine.src.models import StageContext, VideoRun
from content.video_engine.src.guards.storyboard_guard import guard
from content.video_engine.src.repositories.file_repository import (
    FileBackedVideoJobRepository,
)
from content.video_engine.src.services.ingest import IngestService
from content.video_engine.src.services.script_transform import ScriptTransformService
from content.video_engine.src.services.shot_plan import ShotPlanService
from content.video_engine.src.services.storyboard_build import StoryboardBuildService
from content.video_engine.src.services.technique_manifest import TechniqueManifestService


ROOT = Path(__file__).resolve().parents[3]
ENGINE_ROOT = ROOT / "content" / "video_engine"


def test_corpus_path_builds_schema_valid_storyboard_without_provider_calls(
    tmp_path: Path,
) -> None:
    repository = FileBackedVideoJobRepository(tmp_path / "jobs")
    run = VideoRun(
        source_ref="content/bjj-registry/corpus/armbar-from-guard.json",
        input_payload={
            "channel": "combat-science",
            "targets": ["landscape", "vertical"],
        },
    )
    repository.create_run(run)
    context = StageContext(
        repository=repository,
        configs={
            "project_root": ROOT,
            "video_engine_root": ENGINE_ROOT,
        },
        job_dir=repository.job_dir(run.id),
    )

    ingest = IngestService().run_stage(run, context)
    TechniqueManifestService().run_stage(run, context)
    transform = ScriptTransformService().run_stage(run, context)
    ShotPlanService().run_stage(run, context)
    built = StoryboardBuildService().run_stage(run, context)

    assert ingest.summary["cost_usd"] == 0.0
    assert transform.summary["mode"] == "deterministic_corpus"
    assert built.summary["scene_count"] >= 5
    storyboard = json.loads(
        context.job_dir.joinpath("storyboard.json").read_text(encoding="utf-8")
    )
    schema = json.loads(
        ENGINE_ROOT.joinpath("configs/storyboard.schema.json").read_text(encoding="utf-8")
    )
    assert list(Draft7Validator(schema).iter_errors(storyboard)) == []
    assert storyboard["scenes"][0]["act"] == "hook"
    assert storyboard["scenes"][-1]["act"] == "cta"
    assert any(scene["act"] == "develop" for scene in storyboard["scenes"])
    assert any(scene["act"] == "payoff" for scene in storyboard["scenes"])
    assert storyboard["scenes"][0]["manim_class"] == "BJJActionScene"
    assert storyboard["scenes"][0]["visual_function"] == "result_preview"
    assert guard(storyboard) == (True, [])


def test_ingest_rejects_source_outside_project_root(tmp_path: Path) -> None:
    repository = FileBackedVideoJobRepository(tmp_path / "jobs")
    outside = tmp_path / "outside.json"
    outside.write_text(json.dumps({"transcript": "step"}), encoding="utf-8")
    run = VideoRun(source_ref=str(outside))
    repository.create_run(run)
    context = StageContext(
        repository=repository,
        configs={"project_root": ROOT},
        job_dir=repository.job_dir(run.id),
    )

    try:
        IngestService().run_stage(run, context)
    except ValueError as exc:
        assert "project root" in str(exc)
    else:
        raise AssertionError("source traversal must fail")


def test_ingest_rejects_corpus_record_that_fails_canonical_schema(
    tmp_path: Path,
) -> None:
    source = tmp_path / "incomplete.json"
    source.write_text(
        json.dumps({"slug": "incomplete", "transcript": "Control the wrist."}),
        encoding="utf-8",
    )
    repository = FileBackedVideoJobRepository(tmp_path / "jobs")
    run = VideoRun(source_ref="incomplete.json")
    repository.create_run(run)
    context = StageContext(
        repository=repository,
        configs={
            "project_root": tmp_path,
            "corpus_schema": (
                ROOT
                / "content"
                / "bjj-registry"
                / "schemas"
                / "technique-corpus.schema.json"
            ),
        },
        job_dir=repository.job_dir(run.id),
    )

    with pytest.raises(ValueError, match="failed canonical validation"):
        IngestService().run_stage(run, context)
