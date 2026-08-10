from __future__ import annotations

import copy
import importlib.util
from collections import Counter
from pathlib import Path

import pytest

from content.video_engine.src.services.finance_channel import (
    FinanceChannelValidationError,
    validate_artifact,
    validate_finance_asset_demand_package,
    with_artifact_hash,
)


REPO_ROOT = Path(__file__).resolve().parents[3]
PILOT_ROOT = (
    REPO_ROOT
    / "content/video_engine/projects/systems-and-blowups/pilots/current-bubble-mechanism"
)
OUTPUT_ROOT = PILOT_ROOT / "edit/sentence-native-v1"
SCRIPT_PATH = REPO_ROOT / "content/video_engine/scripts/compile_finance_asset_demand.py"


def _load_compiler():
    spec = importlib.util.spec_from_file_location("finance_asset_demand_compiler", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _checked_in_package() -> tuple[dict, dict, dict]:
    import json

    return tuple(
        json.loads((OUTPUT_ROOT / name).read_text(encoding="utf-8"))
        for name in (
            "asset-demand.v1.json",
            "research-resolution.v1.json",
            "generation-prompt-spine.v1.json",
        )
    )


def test_checked_in_t2_package_is_hash_bound_and_covers_all_202_beats() -> None:
    demand, research, prompts = _checked_in_package()
    for payload in (demand, research, prompts):
        assert validate_artifact(payload)["artifact_hash"] == payload["artifact_hash"]
    result = validate_finance_asset_demand_package(demand, research, prompts, REPO_ROOT)
    assert result == {
        "status": "valid",
        "episode_id": "systems-and-blowups:current-bubble-mechanism",
        "beat_count": 202,
        "prompt_count": 133,
        "research_binding_count": 103,
    }
    assert demand["summary"]["all_beats_have_resolution_path"] is True
    assert sum(demand["summary"]["strategy_counts"].values()) == 202


def test_compiler_is_deterministic_and_reproduces_checked_in_artifacts() -> None:
    module = _load_compiler()
    first = module.compile_asset_demand(PILOT_ROOT)
    second = module.compile_asset_demand(PILOT_ROOT)
    assert first == second
    assert first == _checked_in_package()


def test_existing_assets_are_explicit_single_use_not_convenient_repeats() -> None:
    demand, _, _ = _checked_in_package()
    selected = [
        asset_id
        for item in demand["demands"]
        for asset_id in item["selected_asset_ids"]
    ]
    assert selected
    assert all(count == 1 for count in Counter(selected).values())
    for item in demand["demands"]:
        if item["selected_asset_ids"]:
            assert "Explicit semantic profile" in item["resolution_reason"]
            assert item["reuse_reason"] is None
        elif item["strategy"] == "original_generation_request":
            assert "No exact approved catalog asset" in item["resolution_reason"]


def test_every_numeric_surface_is_verified_and_bound_to_the_same_claim() -> None:
    import json

    demand, _, _ = _checked_in_package()
    numeric = json.loads(
        (PILOT_ROOT / "edit/semantic-v2/numeric-evidence-register.v1.json").read_text(encoding="utf-8")
    )
    surfaces = {item["surface_id"]: item for item in numeric["items"]}
    for item in demand["demands"]:
        for surface_id in item["evidence_surface_ids"]:
            assert surface_id in surfaces
            assert surfaces[surface_id]["claim_id"] in item["claim_refs"]
            assert surfaces[surface_id]["report_locator"]
            assert surfaces[surface_id]["qualifier"]
            assert surfaces[surface_id]["as_of"]


def test_source_requests_have_dates_locator_hashes_and_exact_beat_bindings() -> None:
    demand, research, _ = _checked_in_package()
    records = {item["source_id"]: item for item in research["source_records"]}
    requests = {item["request_id"]: item for item in research["beat_bindings"]}
    for record in records.values():
        assert record["locator_sha256"]
        assert record["published_at"] or record["accessed_at"]
        assert record["url"] and record["location"]
    for item in demand["demands"]:
        for request_id in item["source_request_ids"]:
            assert requests[request_id]["beat_id"] == item["beat_id"]
            assert set(requests[request_id]["source_ids"]).issubset(records)


def test_generation_prompts_are_sentence_native_and_forbid_visual_failure_modes() -> None:
    demand, _, prompt_spine = _checked_in_package()
    prompts = {item["prompt_id"]: item for item in prompt_spine["prompts"]}
    generation_demands = [item for item in demand["demands"] if item["strategy"] == "original_generation_request"]
    assert set(prompts) == {item["prompt_id"] for item in generation_demands}
    for item in generation_demands:
        prompt = prompts[item["prompt_id"]]
        assert prompt["beat_id"] == item["beat_id"]
        assert prompt["narration_excerpt"] == item["excerpt"]
        assert "CURRENT NARRATION BEAT" in prompt["prompt"]
        assert "PRIOR CONTEXT FOR REFERENTS ONLY" in prompt["prompt"]
        assert "NEXT CONTEXT FOR REFERENTS ONLY" in prompt["prompt"]
        assert prompt["active_nouns"] == item["semantic_target"]["active_nouns"]
        assert prompt["causal_verb"] == item["semantic_target"]["causal_verb"]
        assert prompt["factual_text_policy"] == "no_authoritative_text_or_numbers_in_generated_pixels"
        assert {"unrecognizable chart symbols", "giant empty parchment", "generic money rain"}.issubset(prompt["avoid"])

    fragment_prompt = prompts["prompt-cbm-semantic-beat-01-004"]
    assert fragment_prompt["context_before"]
    assert fragment_prompt["context_after"]
    assert "do not collapse multiple beats" in fragment_prompt["prompt"]


def test_validators_reject_missing_beat_invented_surface_and_reused_asset() -> None:
    demand, research, prompts = _checked_in_package()

    missing = copy.deepcopy(demand)
    missing["demands"].pop()
    missing["summary"]["beat_count"] -= 1
    missing["summary"]["strategy_counts"]["original_generation_request"] -= 1
    missing = with_artifact_hash({key: value for key, value in missing.items() if key != "artifact_hash"})
    with pytest.raises(FinanceChannelValidationError, match="cover every semantic beat"):
        validate_finance_asset_demand_package(missing, research, prompts, REPO_ROOT)

    invented = copy.deepcopy(demand)
    target = next(item for item in invented["demands"] if item["strategy"] == "deterministic_surface")
    target["evidence_surface_ids"] = ["invented-return-statistic"]
    invented = with_artifact_hash({key: value for key, value in invented.items() if key != "artifact_hash"})
    with pytest.raises(FinanceChannelValidationError, match="unknown evidence surface"):
        validate_finance_asset_demand_package(invented, research, prompts, REPO_ROOT)

    reused = copy.deepcopy(demand)
    selected = next(item for item in reused["demands"] if item["selected_asset_ids"])
    second = next(item for item in reused["demands"] if item["strategy"] == "original_generation_request")
    second["strategy"] = "exact_asset"
    second["selected_asset_ids"] = list(selected["selected_asset_ids"])
    second["prompt_id"] = None
    reused["summary"]["strategy_counts"]["original_generation_request"] -= 1
    reused["summary"]["strategy_counts"]["exact_asset"] += 1
    reused = with_artifact_hash({key: value for key, value in reused.items() if key != "artifact_hash"})
    with pytest.raises(FinanceChannelValidationError, match="same existing asset"):
        validate_artifact(reused)
