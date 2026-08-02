from __future__ import annotations

import json
from pathlib import Path

from content.video_engine.src.models import StageContext, VideoRun
from content.video_engine.src.services.style_board import (
    COMPOSITION_FUNCTIONS,
    STYLE_BOARD_STILL_ROLES,
    StyleBoardService,
)


def _art_direction() -> dict:
    return {
        "schema_version": "art_bible.v1",
        "art_bible": {
            "schema_version": "art_bible.v1",
            "palette": {"background": "#0B0F14", "accent": "#20D69B"},
        },
    }


def test_style_board_is_six_stills_and_deterministic(tmp_path: Path) -> None:
    first = StyleBoardService().build(_art_direction(), tmp_path / "one")
    second = StyleBoardService().build(_art_direction(), tmp_path / "two")

    assert first["schema_version"] == "style_board.v1"
    assert first["approval_granted"] is False
    assert first["provider_calls"] == 0
    assert [item["role"] for item in first["stills"]] == list(STYLE_BOARD_STILL_ROLES)
    assert first["artifact_hash"] == second["artifact_hash"]
    assert all((tmp_path / "one" / item["path"]).is_file() for item in first["stills"])
    assert first["composition_functions"] == list(COMPOSITION_FUNCTIONS)


def test_style_board_does_not_copy_study_provenance(tmp_path: Path) -> None:
    direction = _art_direction()
    direction["study_path"] = "YouTube Reference Pack/study.json"
    direction["creator_name"] = "external creator"
    result = StyleBoardService().build(direction, tmp_path / "style_board")
    rendered = (tmp_path / "style_board" / "style_board.json").read_text(encoding="utf-8")

    assert "YouTube Reference Pack" not in rendered
    assert "external creator" not in rendered
    assert result["source"] == "deterministic_style_board"


def test_run_stage_writes_review_packet_under_style_board(tmp_path: Path) -> None:
    class Repo:
        def update_run(self, run):
            return run

    run = VideoRun(source_ref="armbar")
    ctx = StageContext(repository=Repo(), configs={"art_bible": _art_direction()}, job_dir=tmp_path)
    summary = StyleBoardService().run_stage(run, ctx).summary

    assert summary["still_count"] == 6
    assert (tmp_path / "style_board" / "style_board.json").is_file()
    assert (tmp_path / "style_board" / "review-packet.json").is_file()
    packet = json.loads((tmp_path / "style_board" / "review-packet.json").read_text())
    assert packet["approval_granted"] is False
