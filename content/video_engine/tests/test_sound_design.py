from __future__ import annotations

import json
from pathlib import Path

import pytest

from content.video_engine.src.services.sound_design import (
    SoundDesignError,
    SoundDesignService,
)


def _storyboard() -> dict:
    return {
        "scenes": [
            {
                "scene_id": 1,
                "timing": {"padding_s": 0.3},
                "parameters": {
                    "sound_cues": [
                        "movement",
                        {"cue": "contact", "phase": "contact"},
                        "aftermath",
                    ]
                },
            }
        ]
    }


def _words(root: Path) -> None:
    root.mkdir(parents=True)
    (root / "scene_1.words.json").write_text(
        json.dumps(
            {
                "scene_id": 1,
                "duration_s": 5.0,
                "words": [{"w": "move", "start_s": 0.0, "end_s": 4.8}],
            }
        ),
        encoding="utf-8",
    )


def _palette(path: Path, asset_path: str | None = None) -> None:
    path.write_text(
        json.dumps(
            {
                "schema_version": "sound_palette.v1",
                "cues": {
                    "movement": {
                        "asset_path": asset_path,
                        "gain_db": -18,
                        "phase": "anticipation",
                    },
                    "contact": {
                        "asset_path": None,
                        "gain_db": -12,
                        "phase": "contact",
                    },
                    "aftermath": {
                        "asset_path": None,
                        "gain_db": -20,
                        "phase": "recovery",
                    },
                },
            }
        ),
        encoding="utf-8",
    )


def test_sound_manifest_uses_measured_narration_clock(tmp_path: Path) -> None:
    audio = tmp_path / "audio"
    _words(audio)
    asset = tmp_path / "move.wav"
    asset.write_bytes(b"licensed-local-cue")
    palette = tmp_path / "palette.json"
    _palette(palette, asset.name)

    result = SoundDesignService(palette).build(
        _storyboard(), audio, audio / "sound_manifest.json"
    )

    assert result["narration_clock_s"] == 5.3
    assert [event["phase"] for event in result["events"]] == [
        "anticipation",
        "contact",
        "recovery",
    ]
    assert [event["at_s"] for event in result["events"]] == [0.9, 2.9, 4.0]
    assert result["available_event_count"] == 1
    assert result["music"] is None


def test_unknown_cue_fails_closed(tmp_path: Path) -> None:
    audio = tmp_path / "audio"
    _words(audio)
    palette = tmp_path / "palette.json"
    _palette(palette)
    storyboard = _storyboard()
    storyboard["scenes"][0]["parameters"]["sound_cues"] = ["unknown"]
    with pytest.raises(SoundDesignError, match="unknown sound cue"):
        SoundDesignService(palette).build(
            storyboard, audio, audio / "sound_manifest.json"
        )


def test_sound_manifest_does_not_extend_timeline(tmp_path: Path) -> None:
    audio = tmp_path / "audio"
    _words(audio)
    palette = tmp_path / "palette.json"
    _palette(palette)
    result = SoundDesignService(palette).build(
        _storyboard(), audio, audio / "sound_manifest.json"
    )
    assert max(event["at_s"] for event in result["events"]) < result["narration_clock_s"]


# ---- R26-5 / E44 s2a: Tokyo's transient gain, halved, tagged in the plan itself ----

TOKYO_SOUND_PLAN = (
    Path(__file__).resolve().parents[3]
    / "content/video_engine/projects/systems-and-blowups/tokyo-tea-break/sound/SOUND-PLAN.json"
)
TRANSIENT_GAIN = 0.08
DERIVED_TAG = "[DERIVED: from the 2026-09-05 metering, halved]"


def test_tokyo_transient_gain_is_halved_and_tagged_derived() -> None:
    """R26-5 (E44 s2a): 0.16 -> 0.08 on the hand-held dial, with its provenance in the plan's own text.
    The gain M29 (gate_motion_density) polices in the build; this is the plan that carries it.
    The dial is a top-level field on purpose: build_short.py rewrites only `cues`, so a gain written into
    a cue would not survive a build - and the V2 cut already dropped `press 3`, so no cue carries it."""
    plan = json.loads(TOKYO_SOUND_PLAN.read_text(encoding="utf-8"))
    assert plan["transient_gain"] == TRANSIENT_GAIN
    assert DERIVED_TAG in plan["transient_gain_note"]
    assert DERIVED_TAG in plan["note"] and "0.16 -> 0.08" in plan["note"]
    assert not [c for c in plan["cues"] if c.get("slot", "").startswith("press")]   # never re-added
