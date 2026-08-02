from __future__ import annotations

import json
from pathlib import Path

import pytest

from content.video_engine.src.models import StageContext, VideoRun
from content.video_engine.src.repositories.file_repository import FileBackedVideoJobRepository
from content.video_engine.src.services.shot_plan import (
    SHOT_PLAN_VERSION,
    ShotPlanService,
    ShotPlanValidationError,
)


def _manifest() -> dict:
    return {
        "schema_version": "technique_visual_manifest.v1",
        "slug": "armbar-from-guard",
        "style_preset": "flat_vector_bjj",
        "rights": {"permission": "internal", "source": "fixture", "reviewed": True},
        "cast": {
            "attacker": {"id": "attacker", "color": "blue"},
            "defender": {"id": "defender", "color": "black"},
        },
        "actions": [
            {
                "id": "wrist-control",
                "state_from": "closed_guard",
                "action": "two_on_one_wrist_control",
                "state_to": "wrist_frame",
                "contact": "attacker_wrist",
                "motion_path": "linear",
                "reviewed": True,
                "reference_refs": [],
                "overlays": ["wrist_lock"],
            }
        ],
    }


def _beats() -> dict:
    return {
        "source_slug": "armbar-from-guard",
        "beats": [
            {
                "act": "develop",
                "narration_text": "Grip the wrist with both hands.",
                "visual_type": "bjj_action",
                "manim_class": "BJJActionScene",
                "action_id": "wrist-control",
                "function": "contact_closeup",
                "transition": {"in": "continuous", "motif": "cast:attacker"},
            },
            {
                "act": "cta",
                "narration_text": "Learn it properly.",
                "visual_type": "title_card",
                "manim_class": "TitleConceptCard",
            },
        ],
    }


def test_compile_emits_deterministic_instructional_recipe_and_provenance() -> None:
    plan = ShotPlanService().compile(_beats(), _manifest())

    assert plan["schema_version"] == SHOT_PLAN_VERSION
    shot = plan["shots"][0]
    assert shot["function"] == "contact_closeup"
    assert shot["visual_type"] == "bjj_action"
    assert shot["cast"]["attacker"]["color"] == "blue"
    assert shot["state_from"] == "closed_guard"
    assert shot["action"] == "two_on_one_wrist_control"
    assert shot["state_to"] == "wrist_frame"
    assert shot["camera"] == {
        "framing": "grip_closeup",
        "move": "push_in",
        "focus": "contact",
    }
    assert shot["motion"]["path"] == "linear"
    assert shot["motion"]["phases"] == ["anticipation", "action", "contact", "recovery"]
    assert shot["overlays"] == ["wrist_lock"]
    assert shot["sound_cues"] == ["movement", "contact", "aftermath"]
    assert shot["provenance"]["manifest_slug"] == "armbar-from-guard"
    assert plan["shots"][1]["visual_type"] == "title_card"


def test_unresolved_instructional_beat_fails_closed() -> None:
    beats = _beats()
    beats["beats"][0]["action_id"] = "not-reviewed"
    with pytest.raises(ShotPlanValidationError, match="unresolved reviewed action"):
        ShotPlanService().compile(beats, _manifest())


def test_incomplete_action_reports_each_mechanic_error() -> None:
    manifest = _manifest()
    manifest["actions"][0].pop("contact")
    manifest["actions"][0].pop("motion_path")
    manifest["actions"][0]["reviewed"] = False

    with pytest.raises(ShotPlanValidationError) as raised:
        ShotPlanService().compile(_beats(), manifest)

    detail = " ".join(raised.value.errors)
    assert "missing contact" in detail
    assert "missing motion_path" in detail
    assert "reviewed action state is required" in detail


def test_run_stage_writes_shot_plan_artifact(tmp_path: Path) -> None:
    repository = FileBackedVideoJobRepository(tmp_path / "jobs")
    run = VideoRun(source_ref="armbar-from-guard.json")
    repository.create_run(run)
    context = StageContext(repository=repository, configs={}, job_dir=repository.job_dir(run.id))
    context.job_dir.joinpath("beat_sheet.json").write_text(
        json.dumps(_beats()), encoding="utf-8"
    )
    context.job_dir.joinpath("technique_manifest.json").write_text(
        json.dumps(_manifest()), encoding="utf-8"
    )

    output = ShotPlanService().run_stage(run, context)

    assert output.summary["shot_count"] == 2
    artifact = json.loads((context.job_dir / "shot_plan.json").read_text(encoding="utf-8"))
    assert artifact["schema_version"] == SHOT_PLAN_VERSION
    assert artifact["shots"][0]["beat_index"] == 0
