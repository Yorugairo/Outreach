"""Focused contract tests for the local assembly wrapper."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

import build_assembly as assembly


def _manifest(tmp_path: Path, *, clips: list[dict], duration: float = 2.0, captions=None) -> Path:
    for clip in clips:
        (tmp_path / clip["path"]).write_bytes(b"video")
    path = tmp_path / "edit.json"
    path.write_text(json.dumps({"duration": duration, "clips": clips, "captions": captions or []}), encoding="utf-8")
    return path


def test_load_edit_accepts_contiguous_hard_cuts(tmp_path: Path):
    path = _manifest(
        tmp_path,
        clips=[
            {"id": "a", "path": "a.mp4", "start": 0, "duration": 1},
            {"id": "b", "path": "b.mp4", "start": 1, "duration": 1},
        ],
    )
    result = assembly.load_edit(path)
    assert [clip["end"] for clip in result["clips"]] == [1.0, 2.0]


@pytest.mark.parametrize(
    ("start", "message"),
    [(0.5, "overlap"), (-1, "start must be >= 0")],
)
def test_load_edit_rejects_non_hard_cut_spans(tmp_path: Path, start: float, message: str):
    path = _manifest(
        tmp_path,
        clips=[
            {"id": "a", "path": "a.mp4", "start": 0, "duration": 1},
            {"id": "b", "path": "b.mp4", "start": start, "duration": 1},
        ],
        duration=2,
    )
    with pytest.raises(assembly.ContractError, match=message):
        assembly.load_edit(path)


def test_caption_pages_are_seek_safe_and_word_clocked():
    pages, words = assembly._caption_pages(
        [{"at": 1.0, "until": 2.0, "text": "One two"}],
        [
            {"w": "One", "start": 1.0, "end": 1.5},
            {"w": "two", "start": 1.5, "end": 2.0},
        ],
    )
    assert pages == [{
        "s": 1.0,
        "e": 2.0,
        "t": [
            {"w": "One", "s": 1.0, "e": 1.5, "k": False},
            {"w": "two", "s": 1.5, "e": 2.0, "k": False},
        ],
    }]
    assert words[0]["start"] == 1.0 and words[-1]["end"] == 2.0


def test_caption_pages_use_sidecar_word_clock_and_keep_page_hold():
    pages, words = assembly._caption_pages(
        [
            {"at": 1.288, "until": 1.975, "text": "SEAN SHARAF"},
            {"at": 1.975, "until": 3.3, "text": "SHUTS THE LIGHTS OUT."},
        ],
        [
            {"w": "Ten", "start": 0.275, "end": 0.512},
            {"w": "seconds.", "start": 0.512, "end": 1.288},
            {"w": "Sean", "start": 1.288, "end": 1.587},
            {"w": "Sharaf", "start": 1.587, "end": 1.975},
            {"w": "shuts", "start": 1.975, "end": 2.237},
            {"w": "the", "start": 2.237, "end": 2.325},
            {"w": "lights", "start": 2.325, "end": 2.6},
            {"w": "out.", "start": 2.6, "end": 3.225},
        ],
    )
    assert pages[0]["t"][0]["s"] == 1.288
    assert pages[1]["t"][-1]["e"] == 3.225
    assert pages[1]["e"] == 3.3
    assert words[-1]["end"] == 3.225
