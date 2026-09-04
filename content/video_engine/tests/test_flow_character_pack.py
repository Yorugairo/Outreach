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
FINANCE_PACK = ROOT / "projects" / "systems-and-blowups" / "finance-host-flow-character-pack.v1.json"
SHEET_STANDARD_VIEWS = {"front", "profile", "three_quarter", "back", "expression_sheet", "pose_sheet"}
# 53 §53.10: the stick variant keeps what survives at 5 % of the pixels and nothing else.
STICK_SURVIVORS = ("loc", "glasses", "goatee", "indigo", "copper")
STICK_DROPPED = ("lapel", "floral", "textile", "pocket square", "paper", "woodblock")


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


# ---------------------------------------------------------------- A0 (2026-09-04)
# The finance pack had never validated: its role was not in its own schema's enum and no
# test loaded it. These are the gates that stop that recurring.


def test_finance_pack_validates_and_meets_the_model_sheet_standard() -> None:
    payload = validate_flow_character_pack(FINANCE_PACK)
    by_id = {character["id"]: character for character in payload["characters"]}
    assert {"finance-host-v1", "finance-host-stick-v1"} <= set(by_id)
    for character in by_id.values():
        assert SHEET_STANDARD_VIEWS <= set(character["reference_views"]), character["id"]
        assert len(character["expressions"]) == 5, character["id"]
        assert len(character["poses"]) == 5, character["id"]
        assert character["render_eligible"] is False
    assert by_id["finance-host-v1"]["variant"] == "retention"
    assert by_id["finance-host-stick-v1"]["variant"] == "acquisition"
    assert by_id["finance-host-stick-v1"]["variant_of"] == "finance-host-v1"
    # the two rows are the rig's slot enumeration, so they must agree across variants
    assert by_id["finance-host-v1"]["expressions"] == by_id["finance-host-stick-v1"]["expressions"]
    assert by_id["finance-host-v1"]["poses"] == by_id["finance-host-stick-v1"]["poses"]


def test_stick_variant_carries_only_what_survives_simplification() -> None:
    payload = validate_flow_character_pack(FINANCE_PACK)
    stick = next(c for c in payload["characters"] if c["id"] == "finance-host-stick-v1")
    prompt = stick["prompt"].casefold()
    missing = [term for term in STICK_SURVIVORS if term not in prompt]
    carried = [term for term in STICK_DROPPED if term in prompt]
    assert not missing, f"stick prompt lost identity features: {missing}"
    assert not carried, f"stick prompt carries retention-lane detail: {carried}"


def test_host_prompt_is_the_colour_cartoon_not_the_paper_toy() -> None:
    """Operator, 2026-09-04: the paper-toy assets are rejected; only the host identity is good."""
    payload = validate_flow_character_pack(FINANCE_PACK)
    host = next(c for c in payload["characters"] if c["id"] == "finance-host-v1")
    prompt = host["prompt"].casefold()
    for term in ("crinkle", "puppet", "hand-cut", "cut-out", "paper-craft"):
        assert term not in prompt, f"host prompt still describes the paper-toy medium: {term!r}"
    for term in ("indigo", "copper", "glasses", "goatee", "loc"):
        assert term in prompt
    # the recognised Flow directive (operator, 2026-09-04; in eight shipped Tokyo _meta.json prompts)
    assert "light application of woodblock print and vox newspaper with rich anime colors" in prompt


def test_declared_sheets_must_be_enumerated_and_variants_must_point_home() -> None:
    payload = json.loads(FINANCE_PACK.read_text(encoding="utf-8"))

    unenumerated = copy.deepcopy(payload)
    del unenumerated["characters"][0]["expressions"]
    unenumerated.pop("artifact_hash")
    with pytest.raises(FlowCharacterPackError, match="enumerates no expressions"):
        validate_flow_character_pack(unenumerated)

    orphan = copy.deepcopy(payload)
    orphan["characters"][1]["variant_of"] = "nobody-v1"
    orphan.pop("artifact_hash")
    with pytest.raises(FlowCharacterPackError, match="not another character in this pack"):
        validate_flow_character_pack(orphan)

    headless = copy.deepcopy(payload)
    del headless["characters"][1]["variant_of"]
    headless.pop("artifact_hash")
    with pytest.raises(FlowCharacterPackError, match="names no variant_of"):
        validate_flow_character_pack(headless)
