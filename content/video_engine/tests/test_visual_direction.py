from __future__ import annotations

from pathlib import Path

from content.video_engine.src.guards.visual_direction import (
    validate_visual_approval,
)
from content.video_engine.src.services.style_board import StyleBoardService


def _rubric(art_bible_hash: str, score: float = 4) -> dict:
    return {
        "schema_version": "visual_direction.v1",
        "art_bible_hash": art_bible_hash,
        "scores": {
            "originality": score,
            "hierarchy": score,
            "body_ownership": score,
            "typography": score,
            "diagram_integration": score,
            "audience_clarity": score,
        },
    }


def test_visual_direction_requires_six_scores_at_current_art_bible_hash(tmp_path: Path) -> None:
    board = StyleBoardService().build({}, tmp_path / "style_board")
    assert validate_visual_approval(tmp_path, _rubric(board["art_bible_hash"]), board["art_bible_hash"]) == []


def test_visual_direction_rejects_low_score_and_stale_hash(tmp_path: Path) -> None:
    board = StyleBoardService().build({}, tmp_path / "style_board")
    errors = validate_visual_approval(
        tmp_path,
        _rubric("0" * 64, score=3),
        board["art_bible_hash"],
    )

    assert any("does not match current" in error for error in errors)
    assert any("below the 4/5 threshold" in error for error in errors)


def test_visual_direction_rejects_missing_dimension(tmp_path: Path) -> None:
    board = StyleBoardService().build({}, tmp_path / "style_board")
    rubric = _rubric(board["art_bible_hash"])
    del rubric["scores"]["typography"]

    errors = validate_visual_approval(tmp_path, rubric, board["art_bible_hash"])

    assert any("six rubric dimensions" in error for error in errors)
