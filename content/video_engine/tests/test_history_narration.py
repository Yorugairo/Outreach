from __future__ import annotations

import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from content.video_engine.src.services.higgsfield_explainer import (
    compile_audio_aligned_higgsfield_blocks,
)
from content.video_engine.src.services.history_contracts import canonical_sha256
from content.video_engine.src.services.history_narration import (
    HistoryNarrationError,
    compile_history_narration,
    resolve_canonical_elevenlabs_audio,
    validate_canonical_audio,
    validate_history_narration,
)


def _storyboard() -> dict:
    return {
        "job_id": "history-episode-1",
        "channel": {"series": "history-of-bjj"},
        "research_hash": "research-hash",
        "scenes": [
            {
                "scene_id": 1,
                "chapter_id": "chapter-one",
                "narration_text": "Canonical narration comes from the storyboard.",
                "claim_refs": ["claim-one"],
                "citation_refs": ["citation-one"],
                "visual_beats": [
                    {"narration_excerpt": "THIS VISUAL CUE MUST NEVER BE SPOKEN"}
                ],
            }
        ],
    }


def test_history_narration_uses_canonical_scene_text_not_visual_cues(tmp_path: Path) -> None:
    storyboard = _storyboard()
    source = {
        "status": "research_gate_revision",
        "target_duration_s": 600,
        "segments": [
            {
                "segment_id": "scene-one-expanded",
                "scene_id": 1,
                "chapter_id": "chapter-one",
                "claim_refs": ["claim-one"],
                "citation_refs": ["citation-one"],
                "text": "Canonical narration comes from the storyboard. This is an approved expansion.",
            }
        ],
    }
    compiled = compile_history_narration(storyboard, source=source)
    assert "THIS VISUAL CUE" not in compiled["full_text"]
    assert compiled["total_words"] == 11
    assert compiled["source_kind"] == "research_gate_revision"
    assert validate_history_narration(compiled)["artifact_hash"] == compiled["artifact_hash"]


def test_history_narration_rejects_stale_text(tmp_path: Path) -> None:
    compiled = compile_history_narration(_storyboard())
    compiled["full_text"] = "stale"
    with pytest.raises(HistoryNarrationError, match="full_text"):
        validate_history_narration(compiled)


def test_canonical_audio_is_one_take_then_sliced(tmp_path: Path) -> None:
    narration = compile_history_narration(_storyboard())

    class FakeSynth:
        def __init__(self) -> None:
            self.calls = 0

        def synthesize_scene(self, scene_id, text, *, voice_id, settings, audio_dir, cache_dir, config):
            self.calls += 1
            audio_dir.mkdir(parents=True, exist_ok=True)
            audio = audio_dir / f"scene_{scene_id}.mp3"
            words = audio_dir / f"scene_{scene_id}.words.json"
            audio.write_bytes(b"canonical-audio")
            words.write_text(
                json.dumps(
                    {
                        "duration_s": 15.0,
                        "words": [
                            {"w": "Canonical", "start_s": 0.0, "end_s": 0.5},
                            {"w": "narration", "start_s": 10.0, "end_s": 10.5},
                        ],
                    }
                ),
                encoding="utf-8",
            )
            return SimpleNamespace(
                audio_path=audio,
                words_path=words,
                duration_s=15.0,
                cache_hit=False,
                cost_usd=0.01,
            )

    def segmenter(source_audio, windows, output_dir):
        output_dir.mkdir(parents=True, exist_ok=True)
        paths = []
        for index, _window in enumerate(windows, start=1):
            target = output_dir / f"audio_block_{index:03d}.mp3"
            target.write_bytes(source_audio.read_bytes())
            paths.append(target)
        return paths

    fake = FakeSynth()
    manifest = resolve_canonical_elevenlabs_audio(
        narration,
        job_root=tmp_path,
        storyboard_hash="storyboard-hash",
        voice_id="voice",
        allow_synthesis=True,
        synthesizer=fake,
        synthesis_config=SimpleNamespace(voice_id="voice"),
        segmenter=segmenter,
    )
    assert fake.calls == 1
    assert manifest["status"] == "ready"
    assert manifest["duration_s"] == 15.0
    assert len(manifest["blocks"]) == 2
    assert validate_canonical_audio(
        manifest,
        job_root=tmp_path,
        expected_narration_hash=narration["narration_hash"],
        expected_storyboard_hash="storyboard-hash",
        expected_voice_id="voice",
    )["artifact_hash"] == manifest["artifact_hash"]


def _coverage_and_batch(tmp_path: Path) -> tuple[dict, dict]:
    slots = []
    blocks = []
    for index in range(4):
        slot_id = f"slot-{index + 1}"
        slots.append(
            {
                "slot_id": slot_id,
                "duration_s": 10.0,
                "narration_excerpt": f"visual cue {index}",
                "function": "artifact_cold_open",
                "semantic_purpose": "evidence",
                "motion_recipe": "detail_punch",
                "micro_events": [],
                "claim_refs": ["claim-one"],
                "citation_refs": ["citation-one"],
                "asset_ids": [f"asset-{index + 1}"],
            }
        )
        image = tmp_path / "generated" / f"{index + 1:03d}.png"
        image.parent.mkdir(parents=True, exist_ok=True)
        image.write_bytes(f"plate-{index}".encode())
        blocks.append(
            {
                "block_id": f"plate-{index + 1}",
                "order": index + 1,
                "coverage_slot_ids": [slot_id],
                "path": str(image.relative_to(tmp_path)).replace("\\", "/"),
                "sha256": hashlib.sha256(image.read_bytes()).hexdigest(),
                "render_eligible": False,
                "evidence_eligible": False,
                "contains_factual_text": False,
                "source_kind": "ai_assisted_illustration",
                "disclosure_label": "AI-assisted illustration / reconstruction",
                "prompt": "original illustrated plate; no words",
            }
        )
    coverage = {"schema_version": "editorial_coverage.v1", "slots": slots, "artifact_hash": ""}
    coverage["artifact_hash"] = canonical_sha256({key: value for key, value in coverage.items() if key != "artifact_hash"})
    batch = {
        "schema_version": "generated_image_block_batch.v1",
        "provider": "fixture",
        "plan_hash": "fixture",
        "one_generated_plate_per_block": True,
        "blocks": blocks,
        "policy": {"generated_pixels_are_not_evidence": True},
        "artifact_hash": "",
    }
    batch["artifact_hash"] = canonical_sha256({key: value for key, value in batch.items() if key != "artifact_hash"})
    return coverage, batch


def test_audio_aligned_blocks_use_audio_words_and_cover_every_plate(tmp_path: Path) -> None:
    coverage, batch = _coverage_and_batch(tmp_path)
    narration = {
        "schema_version": "history_narration.v1",
        "episode_id": "history-of-bjj:history-episode-1",
        "source_storyboard_hash": "0" * 64,
        "research_hash": "research-hash",
        "source_kind": "test",
        "target_duration_s": 20.0,
        "segments": [
            {
                "segment_id": "s1",
                "scene_id": 1,
                "chapter_id": "chapter-one",
                "claim_refs": ["claim-one"],
                "citation_refs": ["citation-one"],
                "text": "Canonical first block. Canonical second block.",
                "word_count": 6,
                "char_count": 46,
            }
        ],
        "full_text": "Canonical first block. Canonical second block.",
        "total_words": 6,
        "total_chars": 46,
        "narration_hash": "",
        "policy": {},
        "artifact_hash": "",
    }
    from content.video_engine.src.services.history_narration import _narration_hash

    narration["narration_hash"] = _narration_hash(narration["full_text"])
    narration["artifact_hash"] = canonical_sha256({key: value for key, value in narration.items() if key != "artifact_hash"})
    audio_paths = []
    audio_blocks = []
    for index in range(2):
        path = tmp_path / "audio" / f"block-{index + 1}.mp3"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(f"audio-{index}".encode())
        audio_paths.append(path)
        audio_blocks.append(
            {
                "audio_block_id": f"audio-block-{index + 1:03d}",
                "order": index + 1,
                "start_s": index * 10.0,
                "end_s": (index + 1) * 10.0,
                "audio_path": str(path.relative_to(tmp_path)).replace("\\", "/"),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "duration_s": 10.0,
                "word_timings": (
                    [{"w": "Canonical", "start_s": 0.0, "end_s": 0.5}]
                    if index == 0
                    else [{"w": "second", "start_s": 0.0, "end_s": 0.5}]
                ),
            }
        )
    audio = {
        "schema_version": "elevenlabs_canonical_audio.v1",
        "status": "ready",
        "provider": "elevenlabs",
        "episode_id": narration["episode_id"],
        "narration_hash": narration["narration_hash"],
        "storyboard_hash": "storyboard-hash",
        "voice_id": "voice",
        "audio_path": audio_blocks[0]["audio_path"],
        "audio_sha256": audio_blocks[0]["sha256"],
        "words_path": audio_blocks[0]["audio_path"],
        "duration_s": 20.0,
        "blocks": audio_blocks,
        "policy": {},
        "artifact_hash": "",
    }
    audio["artifact_hash"] = canonical_sha256({key: value for key, value in audio.items() if key != "artifact_hash"})
    plan = compile_audio_aligned_higgsfield_blocks(
        coverage,
        batch,
        narration,
        audio,
        job_root=tmp_path,
        storyboard_hash="storyboard-hash",
    )
    assert plan["block_count"] == 2
    assert plan["coverage_slot_count"] == 4
    assert plan["blocks"][0]["narration_excerpt"] == "Canonical"
    assert "visual cue" not in plan["blocks"][0]["narration_excerpt"]
