from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft7Validator

from content.video_engine.src.models import StageContext, VideoRun
from content.video_engine.src.repositories.file_repository import FileBackedVideoJobRepository
from content.video_engine.src.services.art_direction import (
    ART_BIBLE_VERSION,
    ART_DIRECTION_VERSION,
    DEFAULT_ART_BIBLE_ID,
    REFERENCE_STUDY_VERSION,
    VISUAL_TREATMENT_VERSION,
    ArtDirectionService,
    ArtDirectionValidationError,
    VisualTreatmentService,
    canonical_sha256,
)


ENGINE_ROOT = Path(__file__).resolve().parents[1]
CONFIG_ROOT = ENGINE_ROOT / "configs"


def test_curated_study_and_art_bible_are_strict_and_hash_stable() -> None:
    service = ArtDirectionService()
    study = service.load_reference_study()
    bible = service.load_art_bible()

    assert study["schema_version"] == REFERENCE_STUDY_VERSION
    assert study["render_policy"]["renderable"] is False
    assert bible["schema_version"] == ART_BIBLE_VERSION
    assert bible["id"] == DEFAULT_ART_BIBLE_ID
    assert bible["study_ref"]["hash"] == study["artifact_hash"]
    assert bible["artifact_hash"] == canonical_sha256(bible)

    for filename, payload in (
        ("reference_study.schema.json", study),
        ("art_bible.schema.json", bible),
    ):
        schema = json.loads((CONFIG_ROOT / filename).read_text(encoding="utf-8"))
        assert list(Draft7Validator(schema).iter_errors(payload)) == []

    # Insertion order cannot change a canonical digest.
    reordered = {key: study[key] for key in reversed(list(study))}
    assert canonical_sha256(reordered) == canonical_sha256(study)


def test_study_rejects_renderable_or_media_provenance() -> None:
    service = ArtDirectionService()
    study = service.load_reference_study()

    renderable = copy.deepcopy(study)
    renderable["render_policy"]["renderable"] = True
    with pytest.raises(ArtDirectionValidationError, match="renderable"):
        service.validate_reference_study(renderable)

    source_frame = copy.deepcopy(study)
    source_frame["lessons"][0]["source_frames"] = ["frame_001.png"]
    with pytest.raises(ArtDirectionValidationError, match="source_frames|source provenance"):
        service.validate_reference_study(source_frame)


def test_renderer_contract_rejects_youtube_paths_and_imitation_language() -> None:
    service = ArtDirectionService()
    bible = service.load_art_bible()

    youtube = copy.deepcopy(bible)
    youtube["style_atoms"][0]["description"] = "Study https://youtu.be/abc123 for the look."
    youtube.pop("artifact_hash", None)
    with pytest.raises(ArtDirectionValidationError, match="prohibited source"):
        service.validate_art_bible(youtube)

    imitation = copy.deepcopy(bible)
    imitation["style_atoms"][0]["description"] = "Render in the style of a named creator."
    imitation.pop("artifact_hash", None)
    with pytest.raises(ArtDirectionValidationError, match="prohibited source"):
        service.validate_art_bible(imitation)


def test_art_direction_stage_writes_renderer_safe_identity_and_hash(tmp_path: Path) -> None:
    repository = FileBackedVideoJobRepository(tmp_path / "jobs")
    run = VideoRun(source_ref="armbar-from-guard.json")
    repository.create_run(run)
    ctx = StageContext(repository=repository, configs={}, job_dir=repository.job_dir(run.id))

    output = ArtDirectionService().run_stage(run, ctx)
    artifact = json.loads((ctx.job_dir / "art_direction.json").read_text(encoding="utf-8"))

    assert output.summary["artifact_path"] == "art_direction.json"
    assert artifact["schema_version"] == ART_DIRECTION_VERSION
    assert artifact["art_bible_id"] == DEFAULT_ART_BIBLE_ID
    assert artifact["artifact_hash"] == canonical_sha256(artifact)
    encoded = json.dumps(artifact, ensure_ascii=False).casefold()
    assert "youtube" not in encoded
    assert "source_frames" not in encoded
    assert "in the style of" not in encoded


def test_visual_treatment_compilation_is_versioned_and_deterministic() -> None:
    service = ArtDirectionService()
    treatment_service = VisualTreatmentService(service)
    plan = {
        "schema_version": "shot_plan.v1",
        "shots": [
            {
                "scene_id": 1,
                "visual_function": "wide_setup",
                "camera": {"framing": "wide_context", "anchor": "mat_center"},
            },
            {
                "scene_id": 2,
                "function": "force_diagram",
                "motion": {"phases": ["action", "contact"], "transition": "diagram_reveal"},
            },
        ],
    }

    treatment = treatment_service.compile(plan)
    treatment_again = treatment_service.compile({"shots": list(reversed(plan["shots"]))})
    assert treatment["schema_version"] == VISUAL_TREATMENT_VERSION
    assert treatment["artifact_hash"] == canonical_sha256(treatment)
    assert [shot["treatment_id"] for shot in treatment["shots"]] == [
        "treatment-shot-001",
        "treatment-shot-002",
    ]
    assert treatment["shots"][0]["function"] == "wide_setup"
    assert treatment_again["shots"][0]["function"] == "force_diagram"


def test_visual_treatment_rejects_unknown_style_atoms() -> None:
    service = ArtDirectionService()
    bible = service.load_art_bible()
    invalid = {
        "schema_version": VISUAL_TREATMENT_VERSION,
        "art_bible_id": bible["id"],
        "art_bible_hash": bible["artifact_hash"],
        "shot_plan_hash": "0" * 64,
        "shots": [
            {
                "shot_id": "1",
                "treatment_id": "treatment-shot-001",
                "function": "wide_setup",
                "purpose": "Establish body ownership",
                "composition": "wide_spatial_setup",
                "rig": "filled-cutout-v3",
                "style_atom_ids": ["not-an-atom"],
                "palette_roles": ["background"],
                "camera": {"framing": "wide", "anchor": "center"},
                "depth": {"attacker": 20, "defender": 10, "overlay": 120},
                "motion": {"phases": ["hold"], "transition": "hard_reset"},
                "overlays": [],
                "typography": {
                    "caption_font": "Inter",
                    "measurement_font": "Roboto Mono",
                },
                "signature": "invalid",
                "uniqueness_signature": "invalid",
            }
        ],
    }
    with pytest.raises(ArtDirectionValidationError, match="unknown style atoms"):
        service.validate_visual_treatment(invalid, art_bible=bible)
