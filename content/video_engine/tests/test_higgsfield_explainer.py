from __future__ import annotations

import hashlib
import json
from types import SimpleNamespace

import pytest

from content.video_engine.src.services.higgsfield_explainer import (
    HiggsfieldExplainerError,
    compile_higgsfield_blocks,
    compile_higgsfield_job_manifest,
    preflight_higgsfield_models,
    record_higgsfield_output,
    record_higgsfield_task,
    resolve_elevenlabs_audio,
    validate_elevenlabs_block_audio_manifest,
    validate_higgsfield_blocks,
)
from content.video_engine.src.services.history_contracts import canonical_sha256


def _fixture(tmp_path):
    slots = []
    blocks = []
    for index in range(138):
        slot_id = f"history-{index + 1:03d}"
        slots.append(
            {
                "slot_id": slot_id,
                "narration_excerpt": f"The historical sentence {index + 1} establishes context.",
                "function": "illustrated_reconstruction" if index % 3 else "artifact_cold_open",
                "semantic_purpose": "evidence",
                "duration_s": 4.0,
                "motion_recipe": "detail_punch",
                "micro_events": [{"at_s": 0.0, "action": "establish", "recipe": "detail_punch"}],
                "claim_refs": [f"claim-{index + 1}"],
                "citation_refs": [f"citation-{index + 1}"],
                "asset_ids": [f"asset-{index + 1}"],
            }
        )
        image = tmp_path / "generated_blocks" / f"{index + 1:03d}.png"
        image.parent.mkdir(parents=True, exist_ok=True)
        image.write_bytes(f"plate-{index}".encode())
        blocks.append(
            {
                "block_id": f"image-block-{index + 1:03d}",
                "order": index + 1,
                "coverage_slot_ids": [slot_id],
                "narration_excerpt": slots[-1]["narration_excerpt"],
                "function": slots[-1]["function"],
                "visual_archetype": "period_comic_block",
                "visual_source": "period_scene",
                "duration_s": 4.0,
                "motion_recipe": "detail_punch",
                "path": f"generated_blocks/{index + 1:03d}.png",
                "sha256": hashlib.sha256(image.read_bytes()).hexdigest(),
                "source_kind": "ai_assisted_illustration",
                "status": "candidate",
                "render_eligible": False,
                "evidence_eligible": False,
                "contains_factual_text": False,
                "disclosure_label": "AI-assisted illustration / reconstruction",
                "prompt": "original illustrated plate; do not place any words",
            }
        )
    coverage = {"schema_version": "editorial_coverage.v1", "slots": slots}
    coverage["artifact_hash"] = canonical_sha256(coverage)
    batch = {
        "schema_version": "generated_image_block_batch.v1",
        "provider": "local-fixture",
        "plan_hash": "fixture-plan",
        "one_generated_plate_per_block": True,
        "blocks": blocks,
        "policy": {"generated_pixels_are_not_evidence": True},
    }
    batch["artifact_hash"] = canonical_sha256(batch)
    coverage_path = tmp_path / "editorial_coverage.json"
    batch_path = tmp_path / "generated_blocks" / "batch.json"
    coverage_path.write_text(json.dumps(coverage), encoding="utf-8")
    batch_path.write_text(json.dumps(batch), encoding="utf-8")
    return coverage_path, batch_path


def test_compiler_reduces_138_beats_to_60_and_preserves_coverage(tmp_path):
    coverage, batch = _fixture(tmp_path)
    plan = compile_higgsfield_blocks(coverage, batch, job_root=tmp_path)
    assert plan["coverage_slot_count"] == 138
    assert plan["block_count"] == 60
    assert len(plan["blocks"]) == 60
    assert len({slot for block in plan["blocks"] for slot in block["coverage_slot_ids"]}) == 138
    assert all(block["provider_duration_s"] == 10.0 for block in plan["blocks"])
    assert all(block["audio"]["generate_audio"] is False for block in plan["blocks"])
    assert plan["timeline_duration_s"] == 552.0


def test_block_validator_rejects_stale_plate(tmp_path):
    coverage, batch = _fixture(tmp_path)
    plan = compile_higgsfield_blocks(coverage, batch, job_root=tmp_path)
    plan["blocks"][0]["plate"]["sha256"] = "0" * 64
    plan["artifact_hash"] = canonical_sha256({key: value for key, value in plan.items() if key != "artifact_hash"})
    with pytest.raises(HiggsfieldExplainerError, match="plate.sha256 is stale"):
        validate_higgsfield_blocks(plan, job_root=tmp_path)


def test_audio_resolution_is_pending_without_matching_episode_audio(tmp_path):
    coverage, batch = _fixture(tmp_path)
    plan = compile_higgsfield_blocks(coverage, batch, job_root=tmp_path)
    manifest = resolve_elevenlabs_audio(
        plan,
        job_root=tmp_path,
        storyboard_hash="episode-storyboard",
        voice_id="custom-voice",
    )
    assert manifest["status"] == "awaiting_audio"
    assert len(manifest["missing_block_ids"]) == 60
    assert manifest["items"] == []


def test_opt_in_synthesis_writes_one_timed_artifact_per_block(tmp_path):
    coverage, batch = _fixture(tmp_path)
    plan = compile_higgsfield_blocks(coverage, batch, job_root=tmp_path)

    class FakeSynth:
        def __init__(self):
            self.calls = 0

        def synthesize_scene(self, scene_id, narration, *, voice_id, settings, audio_dir, cache_dir, config):
            self.calls += 1
            audio_dir.mkdir(parents=True, exist_ok=True)
            cache_dir.mkdir(parents=True, exist_ok=True)
            audio = audio_dir / f"scene_{scene_id}.mp3"
            words = audio_dir / f"scene_{scene_id}.words.json"
            audio.write_bytes(f"audio-{scene_id}".encode())
            words.write_text(json.dumps({"words": [{"w": narration, "start": 0.0, "end": 1.0}]}), encoding="utf-8")
            return SimpleNamespace(audio_path=audio, words_path=words, duration_s=10.0, cache_hit=False, cost_usd=0.01)

    fake = FakeSynth()
    manifest = resolve_elevenlabs_audio(
        plan,
        job_root=tmp_path,
        storyboard_hash="episode-storyboard",
        voice_id="custom-voice",
        allow_synthesis=True,
        synthesizer=fake,
        synthesis_config=SimpleNamespace(voice_id="custom-voice"),
    )
    assert fake.calls == 60
    assert manifest["status"] == "ready"
    assert len(manifest["items"]) == 60
    validated = validate_elevenlabs_block_audio_manifest(
        manifest,
        job_root=tmp_path,
        block_plan=plan,
        expected_voice_id="custom-voice",
        expected_storyboard_hash="episode-storyboard",
    )
    assert validated["artifact_hash"] == manifest["artifact_hash"]


def test_model_preflight_falls_back_when_seedance_lacks_ten_seconds():
    result = preflight_higgsfield_models(
        {
            "seedance_2_0": {
                "supports_audio_references": True,
                "audio_reference_limit": 3,
                "requires_visual_reference": True,
                "durations_s": [5],
                "live_contract_confirmed": True,
            },
            "wan2_6": {
                "supports_audio_references": True,
                "audio_reference_limit": 3,
                "requires_visual_reference": True,
                "durations_s": [5, 10],
                "live_contract_confirmed": True,
            },
        }
    )
    assert result["selected_model"] == "wan2_6"
    assert result["generate_audio"] is False


def test_job_manifest_is_quarantined_and_running_task_cannot_duplicate(tmp_path):
    coverage, batch = _fixture(tmp_path)
    plan = compile_higgsfield_blocks(coverage, batch, job_root=tmp_path)
    audio = resolve_elevenlabs_audio(plan, job_root=tmp_path)
    job = compile_higgsfield_job_manifest(plan, audio, job_root=tmp_path)
    assert job["status"] == "awaiting_audio"
    assert all(item["render_eligible"] is False for item in job["items"])
    updated = record_higgsfield_task(
        job,
        job_root=tmp_path,
        block_id=job["items"][0]["block_id"],
        task_id="task-1",
        status="running",
    )
    with pytest.raises(HiggsfieldExplainerError, match="already has a running task"):
        record_higgsfield_task(
            updated,
            job_root=tmp_path,
            block_id=job["items"][0]["block_id"],
            task_id="task-2",
            status="running",
        )


def test_provider_output_is_hashed_but_remains_quarantined(tmp_path):
    coverage, batch = _fixture(tmp_path)
    plan = compile_higgsfield_blocks(coverage, batch, job_root=tmp_path)
    audio = resolve_elevenlabs_audio(plan, job_root=tmp_path)
    job = compile_higgsfield_job_manifest(plan, audio, job_root=tmp_path)
    output = tmp_path / "provider" / "proof.mp4"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(b"proof")
    updated = record_higgsfield_output(
        job,
        job_root=tmp_path,
        block_id=job["items"][0]["block_id"],
        output_path=output,
    )
    item = updated["items"][0]
    assert item["status"] == "complete"
    assert item["provider_output_sha256"]
    assert item["render_eligible"] is False
