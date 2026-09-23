"""Focused tests for the isolated v2 adapter."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import build_assembly_v2 as assembly


def test_adapter_uses_distinct_v2_paths_and_episode_id():
    assert assembly.BASE.BUILD == assembly.HERE / "build"
    assert assembly.BASE.SHOT_TABLE == assembly.HERE / "SHOT-TABLE.py"
    assert assembly.BASE.DEFAULT_EDIT == assembly.PROJECT / "production" / "edit-v2.json"
    assert assembly.BASE.DEFAULT_AUDIO == assembly.PROJECT / "production" / "audio" / "master-v2.wav"
    assert assembly.BASE.EPISODE_ID == "knockout-brain-matchcut-001-v2"
    assert assembly.OUTPUT_NAME == "knockout-brain-matchcut-001-v2.mp4"


def test_help_and_root_discovery_work_from_repository_root():
    result = subprocess.run(
        [sys.executable, str(Path(assembly.__file__).resolve()), "--help"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert "--compile" in result.stdout
    assert str(assembly.PROJECT / "production" / "edit-v2.json") not in result.stderr
