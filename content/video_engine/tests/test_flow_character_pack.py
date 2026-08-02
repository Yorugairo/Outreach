from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from content.video_engine.src.services.flow_character_pack import (
    FlowCharacterPackError,
    validate_flow_character_pack,
)
from content.video_engine.src.services.producer_orchestration import (
    compile_producer_plan,
)


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "projects" / "history-of-bjj" / "episode-1-flow-character-pack.json"


def test_episode_character_pack_is_hashed_and_non_renderable() -> None:
    payload = validate_flow_character_pack(PACK)
    assert payload["provider"] == "google_flow"
    assert payload["model"] == "nano-banana-pro"
    assert len(payload["characters"]) == 4
    assert payload["render_eligible"] is False
    assert all(character["render_eligible"] is False for character in payload["characters"])


def test_character_pack_rejects_provider_leakage_and_stale_hash() -> None:
    payload = json.loads(PACK.read_text(encoding="utf-8"))
    leaked = copy.deepcopy(payload)
    leaked["characters"][0]["prompt"] += " in the style of a creator name"
    with pytest.raises(FlowCharacterPackError, match="prohibited input"):
        validate_flow_character_pack(leaked)

    stale = copy.deepcopy(payload)
    stale["characters"][0]["label"] = "changed"
    with pytest.raises(FlowCharacterPackError, match="artifact_hash"):
        validate_flow_character_pack(stale)


def test_flow_character_producers_are_opt_in() -> None:
    coverage = {
        "schema_version": "editorial_coverage.v1",
        "artifact_hash": "coverage-hash",
        "slots": [
            {
                "slot_id": "illustration-one",
                "narration_excerpt": "A learner watches the map become a journey.",
                "duration_s": 4.0,
                "semantic_purpose": "setting",
                "visual_archetype": "period_comic_block",
                "selected_visual_source": "original_illustration",
            }
        ],
    }
    plan = compile_producer_plan(
        coverage,
        art_bible_id="combat-history-longform-cutout-fork-v1",
        art_bible_hash="a" * 64,
        character_pack_id="history-episode-1-flow-cast-v1",
    )
    block = plan["blocks"][0]
    assert "google_flow_character" in {item["id"] for item in block["still_producers"]}
    assert block["motion_producers"][0]["id"] == "google_flow_ingredients_to_video"
    assert block["style_key"]["character_pack_id"] == "history-episode-1-flow-cast-v1"
