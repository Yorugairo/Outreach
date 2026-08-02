from __future__ import annotations

import json

import pytest

from content.video_engine.src.services.generated_block_images import (
    compile_generated_block_plan,
)
from content.video_engine.src.services.history_contracts import canonical_sha256
from content.video_engine.src.services.magnific_video import validate_magnific_video_plan
from content.video_engine.src.services.plate_motion import (
    PlateMotionError,
    compile_plate_motion_plan,
    to_magnific_video_plan,
    validate_plate_motion_manifest,
    validate_plate_motion_plan,
)


def _coverage() -> dict:
    return {
        "schema_version": "editorial_coverage.v1",
        "artifact_hash": "coverage-hash",
        "slots": [
            {
                "slot_id": "history-001-a",
                "narration_excerpt": "The plate should move with the narration.",
                "function": "illustrated_reconstruction",
                "visual_archetype": "period_comic_block",
                "duration_s": 4.0,
                "motion_recipe": "parallax_push",
            }
        ],
    }


def _batch(tmp_path):
    image = tmp_path / "generated_blocks" / "001.png"
    image.parent.mkdir()
    image.write_bytes(b"generated-plate")
    plan = compile_generated_block_plan(_coverage())
    import hashlib

    digest = hashlib.sha256(image.read_bytes()).hexdigest()
    block = plan["blocks"][0]
    core = {
        "schema_version": "generated_image_block_batch.v1",
        "provider": "openai-built-in-image-generation",
        "plan_hash": plan["artifact_hash"],
        "one_generated_plate_per_block": True,
        "blocks": [
            {
                **block,
                "path": block["planned_path"],
                "sha256": digest,
                "source_kind": "ai_assisted_illustration",
                "status": "candidate",
            }
        ],
        "policy": {
            "generated_pixels_are_not_evidence": True,
            "factual_overlay_owner": "remotion",
            "provider_output_render_eligible": False,
        },
    }
    return plan, {**core, "artifact_hash": canonical_sha256(core)}


def test_compile_and_validate_plate_motion_plan(tmp_path):
    plan, batch = _batch(tmp_path)
    batch_path = tmp_path / "batch.json"
    batch_path.write_text(json.dumps(batch), encoding="utf-8")
    motion = compile_plate_motion_plan(
        batch_path,
        job_root=tmp_path,
        expected_plan=plan,
    )
    motion_path = tmp_path / "motion-plan.json"
    motion_path.write_text(json.dumps(motion), encoding="utf-8")
    validated = validate_plate_motion_plan(
        motion_path,
        job_root=tmp_path,
        expected_batch_hash=batch["artifact_hash"],
    )
    assert validated["block_count"] == 1
    assert validated["items"][0]["duration"] == "10"
    assert "camera shake" in validated["items"][0]["negative_prompt"]
    adapter_plan = to_magnific_video_plan(
        motion_path,
        job_root=tmp_path,
        expected_batch_hash=batch["artifact_hash"],
    )
    assert adapter_plan["schema_version"] == "magnific_video_plan.v1"
    assert adapter_plan["items"][0]["source_path"] == "generated_blocks/001.png"
    validated_provider = validate_magnific_video_plan(
        adapter_plan,
        project_root=tmp_path,
    )
    assert validated_provider[0]["id"] == "image-block-001-history-001-a"


def test_motion_plan_rejects_stale_batch_hash(tmp_path):
    plan, batch = _batch(tmp_path)
    batch_path = tmp_path / "batch.json"
    batch_path.write_text(json.dumps(batch), encoding="utf-8")
    motion = compile_plate_motion_plan(batch_path, job_root=tmp_path, expected_plan=plan)
    with pytest.raises(PlateMotionError) as exc_info:
        validate_plate_motion_plan(
            motion,
            job_root=tmp_path,
            expected_batch_hash="0" * 64,
        )
    assert any("source_batch_hash" in error for error in exc_info.value.errors)


def test_motion_manifest_resolves_job_local_clips(tmp_path):
    motion_dir = tmp_path / "generated_blocks" / "motion"
    motion_dir.mkdir(parents=True)
    clip = motion_dir / "image-block-001.mp4"
    clip.write_bytes(b"clip")
    manifest = {
        "schema_version": "magnific_video_manifest.v1",
        "provider": "magnific",
        "model": "kling-v2-5-pro",
        "items": [
            {
                "id": "image-block-001",
                "output_path": clip.name,
                "render_eligible": False,
            }
        ],
    }
    path = motion_dir / "manifest.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    validated = validate_plate_motion_manifest(path, job_root=tmp_path)
    assert validated["items"][0]["_resolved_path"] == clip.resolve()


def test_motion_manifest_rejects_remote_or_unsafe_clip(tmp_path):
    path = tmp_path / "manifest.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": "magnific_video_manifest.v1",
                "provider": "magnific",
                "model": "kling-v2-5-pro",
                "items": [
                    {
                        "id": "image-block-001",
                        "output_path": "https://example.com/video.mp4",
                        "render_eligible": False,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(PlateMotionError):
        validate_plate_motion_manifest(path, job_root=tmp_path)
