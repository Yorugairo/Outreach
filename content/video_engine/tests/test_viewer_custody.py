from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / "content/video_engine/scripts"
sys.path.insert(0, str(SCRIPTS))

import script_review_contract as C  # noqa: E402
import viewer_run as R  # noqa: E402
import viewer_windows as W  # noqa: E402


def test_viewer_runner_rejects_legacy_or_stale_windows_before_a_call(tmp_path):
    script = tmp_path / "SCRIPT-VO.txt"
    script.write_text("One complete sentence.", encoding="utf-8")
    windows = tmp_path / "SCRIPT-VIEWER-WINDOWS.json"
    windows.write_text(json.dumps({"schema_version": W.SCHEMA_VERSION, "windows": []}), encoding="utf-8")
    with pytest.raises(SystemExit, match="stale or lacks script custody"):
        R.load_windows(script, windows)


def test_generated_windows_have_current_dual_hash_custody(tmp_path):
    script = tmp_path / "SCRIPT-VO.txt"
    text = "[rehook] One complete sentence."
    script.write_text(text, encoding="utf-8")
    doc = W.build_document(script, text)
    windows = tmp_path / "SCRIPT-VIEWER-WINDOWS.json"
    W.write_windows(doc, windows)
    loaded = R.load_windows(script, windows)
    assert loaded["script_hash"] == C.spoken_hash(text)
    assert loaded["annotated_script_hash"] == C.annotated_hash(text)


def test_tag_only_edit_invalidates_viewer_windows_even_when_audio_is_reusable(tmp_path):
    script = tmp_path / "SCRIPT-VO.txt"
    script.write_text("One complete sentence.", encoding="utf-8")
    windows = tmp_path / "SCRIPT-VIEWER-WINDOWS.json"
    W.write_windows(W.build_document(script, script.read_text(encoding="utf-8")), windows)
    script.write_text("[rehook] One complete sentence.", encoding="utf-8")
    with pytest.raises(SystemExit, match="stale or lacks script custody"):
        R.load_windows(script, windows)
