from __future__ import annotations

import json
from pathlib import Path

import pytest

from content.video_engine.cli import (
    PROJECT_ROOT,
    _pipeline,
    validate_art_bible_contract,
)
from content.video_engine.src.guards.storyboard_guard import guard
from content.video_engine.src.pipeline import VideoPipeline
from content.video_engine.src.repositories.file_repository import (
    FileBackedVideoJobRepository,
)
from content.video_engine.src.services.editorial_beats import (
    compile_editorial_beat_plan,
)


EPISODE = Path(
    "content/video_engine/projects/history-of-bjj/episode-1.json"
)
BRANDED_ART_BIBLE = Path(
    "content/video_engine/configs/art_bibles/"
    "combat-history-branded-literature-v1.json"
)
PROFILE_FORK_ART_BIBLE = Path(
    "content/video_engine/configs/art_bibles/"
    "combat-history-longform-cutout-fork-v1.json"
)


def _research_rubric(path: Path, research_hash: str, score: int = 4) -> Path:
    path.write_text(
        json.dumps(
            {
                "schema_version": "research_gate_rubric.v1",
                "research_hash": research_hash,
                "scores": {
                    "thesis_clarity": score,
                    "source_quality": score,
                    "contested_framing": score,
                    "claim_completeness": score,
                    "promotional_neutrality": score,
                    "rights_readiness": score,
                },
            }
        ),
        encoding="utf-8",
    )
    return path


def _visual_rubric(path: Path, art_bible_hash: str, score: int = 4) -> Path:
    path.write_text(
        json.dumps(
            {
                "schema_version": "documentary_visual_direction_rubric.v1",
                "art_bible_hash": art_bible_hash,
                "scores": {
                    "originality": score,
                    "hierarchy": score,
                    "asset_integration": score,
                    "typography": score,
                    "citation_legibility": score,
                    "audience_clarity": score,
                },
            }
        ),
        encoding="utf-8",
    )
    return path


def _asset_rubric(job_dir: Path, path: Path) -> Path:
    batch = json.loads(
        (job_dir / "asset_selection" / "stock-candidates.json").read_text(
            encoding="utf-8"
        )
    )
    review = json.loads(
        (job_dir / "asset_selection" / "review-template.json").read_text(
            encoding="utf-8"
        )
    )
    fallback_by_slot = {
        candidate["slot_id"]: candidate["candidate_id"]
        for candidate in batch["candidates"]
        if candidate["provider"] == "local"
    }
    review["approved"] = True
    review["reviewed_by"] = "test-operator"
    review["reviewed_at"] = "2026-07-30T00:00:00Z"
    for selection in review["selections"]:
        selection["candidate_id"] = fallback_by_slot[selection["slot_id"]]
    path.write_text(json.dumps(review), encoding="utf-8")
    return path


def test_public_art_bible_validator_dispatches_history_v2(
    tmp_path: Path,
) -> None:
    assert validate_art_bible_contract(BRANDED_ART_BIBLE) == []
    assert validate_art_bible_contract(PROFILE_FORK_ART_BIBLE) == []
    stale = json.loads(PROFILE_FORK_ART_BIBLE.read_text(encoding="utf-8"))
    stale["profile_derivation"]["base_profile_hash"] = "0" * 64
    stale_path = tmp_path / "stale-profile-fork.json"
    stale_path.write_text(json.dumps(stale), encoding="utf-8")

    assert any(
        "base_profile_hash does not match" in error
        for error in validate_art_bible_contract(stale_path)
    )


def test_history_v4_stops_at_research_then_visual_gate(tmp_path: Path) -> None:
    repository = FileBackedVideoJobRepository(tmp_path / "jobs")
    pipeline = _pipeline(repository)

    run = pipeline.start(
        EPISODE.as_posix(),
        channel="combat-science",
        targets=["landscape", "vertical"],
    )

    assert run.status == "awaiting_research_gate"
    assert run.research_gate_status == "pending"
    assert run.config_snapshot["pipeline_contract_version"] == "4.1"
    assert run.config_snapshot["storyboard_contract_version"] == "storyboard.v2.3"
    assert (
        run.config_snapshot["art_bible_id"]
        == "combat-history-longform-cutout-fork-v1"
    )
    assert run.config_snapshot["character_pack_id"] == "history-episode-1-flow-cast-v1"
    assert run.config_snapshot["character_pack_path"].endswith(
        "episode-1-flow-character-pack.json"
    )
    assert "building_technique_manifest" not in run.config_snapshot["stage_order"]
    assert not (repository.job_dir(run.id) / "beat_sheet.json").exists()

    with pytest.raises(ValueError, match="not awaiting_visual_gate"):
        pipeline.approve(run.id, "visual", rubric_path=tmp_path / "missing.json")

    rubric = _research_rubric(
        tmp_path / "research-rubric.json",
        run.config_snapshot["research_hash"],
    )
    advanced = pipeline.approve(run.id, "research", rubric_path=rubric)

    assert advanced.status == "awaiting_asset_gate", advanced.error_text
    assert advanced.research_gate_status == "approved"
    assert advanced.asset_gate_status == "pending"
    assert advanced.visual_gate_status == "pending"
    job_dir = repository.job_dir(run.id)
    assert (job_dir / "editorial_coverage.json").is_file()
    assert (job_dir / "asset_selection" / "contact-sheet.png").is_file()
    advanced = pipeline.approve(
        run.id,
        "assets",
        rubric_path=_asset_rubric(
            job_dir,
            tmp_path / "asset-rubric.json",
        ),
    )
    assert advanced.status == "awaiting_visual_gate", advanced.error_text
    assert advanced.asset_gate_status == "approved"
    assert (job_dir / "visual_treatment.v2.json").is_file()
    assert (job_dir / "storyboard.json").is_file()
    assert (job_dir / "style_board" / "style_board.json").is_file()
    style_board = json.loads(
        (job_dir / "style_board" / "style_board.json").read_text(
            encoding="utf-8"
        )
    )
    assert (
        style_board["art_bible_id"]
        == "combat-history-longform-cutout-fork-v1"
    )
    assert style_board["production_profile"]["id"] == (
        "longform-illustrated-history-v1"
    )
    assert set(style_board["literature_modes"]) == {
        "lofi_comedy",
        "historical_comic",
        "archive_evidence",
    }
    archive_still = next(
        still for still in style_board["stills"] if still["role"] == "archive"
    )
    assert archive_still["function"] == "archival_portrait"
    assert archive_still["asset_ids"] == ["archive-jigoro-kano"]
    assert archive_still["resolved_asset_count"] == 1
    storyboard = json.loads(
        (job_dir / "storyboard.json").read_text(encoding="utf-8")
    )
    assert storyboard["schema_version"] == "2.3.0"
    assert storyboard["coverage_plan_hash"]
    assert storyboard["asset_selection_hash"]
    assert all(scene["visual_beats"] for scene in storyboard["scenes"])
    assert storyboard["source"]["kind"] == "history_episode"
    assert all(
        scene["manim_class"] == "DocumentaryScene"
        for scene in storyboard["scenes"]
    )
    assert advanced.config_snapshot["storyboard_hash"]
    assert not guard(storyboard)[1]

    pipeline.configs["animatic_motion_render"] = False
    visual_rubric = _visual_rubric(
        tmp_path / "visual-rubric.json",
        advanced.config_snapshot["art_bible_hash"],
    )
    gate_a_candidate = pipeline.approve(
        run.id,
        "visual",
        rubric_path=visual_rubric,
    )
    assert gate_a_candidate.status == "awaiting_gate_a"
    assert gate_a_candidate.visual_gate_status == "approved"
    assert gate_a_candidate.gate_a_status == "pending"
    assert (job_dir / "animatic" / "review-packet.json").is_file()
    assert gate_a_candidate.config_snapshot["style_board_hash"]
    assert pipeline._visual_plan_violations(
        job_dir / "storyboard.json",
        job_dir,
    ) == []


def test_history_v4_gate_a_rejects_storyboard_hash_drift(
    tmp_path: Path,
) -> None:
    repository = FileBackedVideoJobRepository(tmp_path / "jobs")
    pipeline = _pipeline(repository)
    run = pipeline.start(
        EPISODE.as_posix(),
        channel="combat-science",
    )
    run = pipeline.approve(
        run.id,
        "research",
        rubric_path=_research_rubric(
            tmp_path / "research-rubric.json",
            run.config_snapshot["research_hash"],
        ),
    )
    run = pipeline.approve(
        run.id,
        "assets",
        rubric_path=_asset_rubric(
            repository.job_dir(run.id),
            tmp_path / "asset-rubric.json",
        ),
    )
    pipeline.configs["animatic_motion_render"] = False
    run = pipeline.approve(
        run.id,
        "visual",
        rubric_path=_visual_rubric(
            tmp_path / "visual-rubric.json",
            run.config_snapshot["art_bible_hash"],
        ),
    )
    assert run.status == "awaiting_gate_a"

    storyboard_path = repository.job_dir(run.id) / "storyboard.json"
    storyboard = json.loads(storyboard_path.read_text(encoding="utf-8"))
    storyboard["packaging"]["titles"][0] = "Unreviewed replacement title"
    storyboard_path.write_text(
        json.dumps(storyboard, indent=2) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(Exception) as exc_info:
        pipeline.approve(run.id, "a")
    assert "storyboard hash does not match" in str(exc_info.value)


def test_history_v4_gate_a_rejects_style_board_hash_drift(
    tmp_path: Path,
) -> None:
    repository = FileBackedVideoJobRepository(tmp_path / "jobs")
    pipeline = _pipeline(repository)
    run = pipeline.start(
        EPISODE.as_posix(),
        channel="combat-science",
    )
    run = pipeline.approve(
        run.id,
        "research",
        rubric_path=_research_rubric(
            tmp_path / "research-rubric.json",
            run.config_snapshot["research_hash"],
        ),
    )
    run = pipeline.approve(
        run.id,
        "assets",
        rubric_path=_asset_rubric(
            repository.job_dir(run.id),
            tmp_path / "asset-rubric.json",
        ),
    )
    pipeline.configs["animatic_motion_render"] = False
    run = pipeline.approve(
        run.id,
        "visual",
        rubric_path=_visual_rubric(
            tmp_path / "visual-rubric.json",
            run.config_snapshot["art_bible_hash"],
        ),
    )
    assert run.status == "awaiting_gate_a"

    board_path = (
        repository.job_dir(run.id) / "style_board" / "style_board.json"
    )
    board = json.loads(board_path.read_text(encoding="utf-8"))
    board["stills"][0]["role"] = "archive"
    board_path.write_text(
        json.dumps(board, indent=2) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(Exception) as exc_info:
        pipeline.approve(run.id, "a")
    assert "style board integrity failed" in str(exc_info.value)


def test_history_v4_research_rubric_is_hash_bound(tmp_path: Path) -> None:
    repository = FileBackedVideoJobRepository(tmp_path / "jobs")
    run = _pipeline(repository).start(
        EPISODE.as_posix(),
        channel="combat-science",
    )
    stale = _research_rubric(
        tmp_path / "stale.json",
        "0" * 64,
    )
    with pytest.raises(Exception) as exc_info:
        _pipeline(repository).approve(run.id, "research", rubric_path=stale)
    assert "does not match" in str(exc_info.value)


def test_gate_a_requires_documentary_treatment_artifact(tmp_path: Path) -> None:
    storyboard = {
        "schema_version": "2.3.0",
        "source": {"kind": "history_episode"},
    }
    storyboard_path = tmp_path / "storyboard.json"
    storyboard_path.write_text(json.dumps(storyboard), encoding="utf-8")

    assert VideoPipeline._visual_plan_violations(
        storyboard_path,
        tmp_path,
    ) == [
        "documentary visual QC: visual_treatment.v2.json is required "
        "before Gate A"
    ]


def test_gate_a_rejects_tampered_editorial_beat_plan(
    tmp_path: Path,
) -> None:
    job_dir = tmp_path / "job"
    animatic = job_dir / "animatic"
    animatic.mkdir(parents=True)
    storyboard = {
        "schema_version": "2.2.0",
        "source": {"kind": "history_episode"},
        "scenes": [
            {
                "scene_id": 1,
                "chapter_id": "chapter-one",
                "narration_text": "A supported sentence.",
                "visual_function": "document_quote_closeup",
                "claim_refs": ["claim-one"],
                "citation_refs": ["citation-one"],
                "asset_ids": [],
                "timing": {"target_s": 3.0},
                "transition": {"in": "hard_cut", "motif": "document"},
            }
        ],
    }
    (job_dir / "storyboard.json").write_text(
        json.dumps(storyboard),
        encoding="utf-8",
    )
    plan = compile_editorial_beat_plan(storyboard)
    plan["beats"][0]["duration_s"] = 20
    (animatic / "editorial-beat-plan.json").write_text(
        json.dumps(plan),
        encoding="utf-8",
    )
    for name in ("motion-preview.mp4", "shot-strip.png", "contact.png"):
        (animatic / name).write_bytes(b"fixture")
    (animatic / "review-packet.json").write_text(
        json.dumps(
            {
                "renderer": "editorial_ffmpeg",
                "preview_path": "animatic/motion-preview.mp4",
                "shot_strip_path": "animatic/shot-strip.png",
                "editorial_beat_plan_path": (
                    "animatic/editorial-beat-plan.json"
                ),
                "motion_contact_sheet_path": "animatic/contact.png",
                "editorial_beat_count": 1,
            }
        ),
        encoding="utf-8",
    )

    violations = VideoPipeline._animatic_violations(job_dir)

    assert any("artifact_hash" in item for item in violations)
    assert any("12-second" in item for item in violations)


def test_checked_in_history_inputs_validate() -> None:
    from content.video_engine.src.services.asset_resolver import (
        validate_asset_manifest,
    )
    from content.video_engine.src.services.history_contracts import (
        HistoryContractService,
    )

    service = HistoryContractService(root=PROJECT_ROOT)
    episode = service.validate_history_episode(PROJECT_ROOT / EPISODE)
    research = service.validate_research_packet(
        PROJECT_ROOT
        / "content/video_engine/projects/history-of-bjj/episode-1-research-packet.json"
    )
    assets = validate_asset_manifest(
        PROJECT_ROOT
        / "content/video_engine/projects/history-of-bjj/episode-1-asset-manifest.v2.json",
        project_root=PROJECT_ROOT,
        check_files=True,
    )

    assert episode["research_packet"]["hash"] == research["artifact_hash"]
    assert episode["asset_manifest"]["hash"] == assets["artifact_hash"]
    assert episode["target_duration_s"] == 600
    assert len([item for item in episode["outputs"] if item["format"] == "vertical"]) == 2
    assert len(
        [
            item
            for item in episode["outputs"]
            if item["format"] == "chapter_subvideo"
        ]
    ) == len(episode["chapters"])
