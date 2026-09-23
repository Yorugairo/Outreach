"""Semantic and artifact checks for the bounded minimal-full rough cut."""

from __future__ import annotations

import json
import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parent


def load_timeline() -> dict:
    return json.loads((ROOT / "timeline.json").read_text(encoding="utf-8"))


def load_renderer():
    spec = importlib.util.spec_from_file_location("minimal_full_renderer_test", ROOT / "render_minimal_full.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_structure_and_disclosures() -> None:
    timeline = load_timeline()
    assert timeline["status"] == "private-review-rough-cut"
    assert timeline["canvas"] == {"width": 540, "height": 960, "fps": 24, "nominal_duration_s": 20.933333, "frame_count": 503}
    ids = [segment["id"] for segment in timeline["segments"]]
    assert ids == ["hook", "news", "reaction", "follow-up", "hendo", "hendo-replay"]
    assert timeline["audio"]["insert_at_s"] == 8.766667
    assert timeline["audio"]["reaction_end_s"] == 11.066666999999999
    assert timeline["audio"]["reaction_insert"].endswith("reaction-duo.wav")
    assert "ANIMATED PARODY" in timeline["required_disclosures"]
    assert "2019 ALLEGATION" in timeline["required_disclosures"]
    assert "NO CHARGES FILED" in timeline["required_disclosures"]
    source = (ROOT / "render_minimal_full.py").read_text(encoding="utf-8")
    assert "SEAN SHARAF" in source
    assert "hair=\"bald\"" in source


def test_opening_freeze_and_caption_windows() -> None:
    renderer = load_renderer()
    assert renderer.opening_caption(0.0) == "NO CHARGES FILED."
    assert renderer.opening_caption(1.1969) == "NO CHARGES FILED."
    assert renderer.opening_caption(1.197) == "THEN SHARAF DELIVERED A"
    assert renderer.opening_caption(2.1989) == "THEN SHARAF DELIVERED A"
    assert renderer.opening_caption(2.199) == "ONE-PUNCH VERDICT."
    assert renderer.opening_caption(3.4999) == "ONE-PUNCH VERDICT."
    assert renderer.opening_caption(3.5) == ""
    assert renderer.opening_local_time(0.0) == 0.0
    assert 0.0 < renderer.opening_local_time(1.0) < 0.4
    assert abs(renderer.opening_local_time(1.197) - 0.4) < 1e-9
    assert abs(renderer.opening_local_time(2.2) - 0.4) < 1e-9
    assert abs(renderer.opening_local_time(4.1) - 1.125) < 1e-9
    assert renderer.opening_local_time(5.5) > renderer.opening_local_time(4.1)
    timeline = load_timeline()
    opening_map = timeline["geometry"]["opening"]["animation_map"]
    assert opening_map["guard_motion_s"] == [0.0, 1.197]
    assert opening_map["filed_freeze_s"] == [1.197, 2.35]


def test_winner_and_contact_geometry() -> None:
    geometry = load_timeline()["geometry"]
    opening = geometry["opening"]
    assert opening["contact"]["attacker"] == "right_fighter_right_glove"
    assert opening["contact"]["receiver"] == "left_head"
    assert opening["contact"]["passes"] is True
    assert opening["brain_launch"]["planned_time_s"] > opening["contact"]["time_s"]
    hendo = geometry["hendo_bisping"]
    assert hendo["contact"]["attacker"] == "left_henderson_right_glove"
    assert hendo["contact"]["receiver"] == "right_bisping_head"
    assert hendo["contact"]["passes"] is True
    assert hendo["fall"]["fighter"] == "right_bisping"
    assert hendo["fall"]["near_horizontal"] is True
    assert hendo["fall"]["floor_contact_passes"] is True
    assert hendo["fall"]["torso_floor_contact_passes"] is True


def test_validation_record_and_source_artifacts() -> None:
    validation = json.loads((ROOT / "validation.json").read_text(encoding="utf-8"))
    assert validation["status"] == "PASS"
    assert validation["decode"] == "PASS"
    assert all(validation["checks"].values())
    assert (ROOT / "timeline.json").is_file()
    assert (ROOT / "audio" / "audio-manifest.json").is_file()
    audio_manifest = json.loads((ROOT / "audio" / "audio-manifest.json").read_text(encoding="utf-8"))
    assert "at unity" in audio_manifest["mix_rule"]
    assert "no ducking" in audio_manifest["mix_rule"]


@pytest.mark.parametrize(
    "artifact",
    (
        "minimal-full-review-roughcut.mp4",
        "contact-sheet.png",
        "style-preview.png",
        "audio/minimal-full-review-audio.wav",
    ),
)
def test_review_only_artifact_if_generated(artifact: str) -> None:
    path = ROOT / artifact
    if not path.is_file():
        pytest.skip(f"review-only artifact has not been generated in this checkout: {artifact}")
    assert path.stat().st_size > 0, artifact
