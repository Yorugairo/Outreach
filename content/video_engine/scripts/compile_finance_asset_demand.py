"""Compile P21 beat-native finance asset demand without provider calls.

The compiler is intentionally conservative. Existing assets are selected only
through an explicit semantic profile and only once. A missing exact match is
recorded as deterministic evidence, source retrieval, or a distinct generation
brief; it is never replaced by a visually convenient neighboring plate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Mapping

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from content.video_engine.src.services.finance_channel import (
    file_sha256,
    validate_finance_asset_demand_package,
    with_artifact_hash,
)


DEFAULT_PILOT = (
    REPO_ROOT
    / "content/video_engine/projects/systems-and-blowups/pilots/current-bubble-mechanism"
)
OUTPUT_DIR = "edit/sentence-native-v1"
SEMANTIC_DIR = "edit/semantic-v2"
RESOLUTION_ORDER = [
    "exact_asset",
    "component_composition",
    "deterministic_surface",
    "source_retrieval_request",
    "original_generation_request",
]


# Each profile is a human-readable assertion that the catalog asset depicts the
# requested relationship. Regex/tag similarity alone is never sufficient.
EXACT_PROFILES: tuple[dict[str, Any], ...] = (
    {"phrase": r"labeling the wrong bubble", "asset_id": "wrong-bubble-elevators-v2", "strategy": "exact_asset"},
    {"phrase": r"not .?a price went up a lot", "asset_id": "bubble-mechanism-diagnostic-v1", "strategy": "component_composition"},
    {"phrase": r"stacked working memory placed beside", "asset_id": "hbm-adjacent-accelerator-v1", "strategy": "exact_asset"},
    {"phrase": r"pressure-rated fuel system", "asset_id": "accelerator-memory-bandwidth-gate-v1", "strategy": "exact_asset"},
    {"phrase": r"fixed number of ovens", "asset_id": "fixed-oven-capacity-wedding-cake-v1", "strategy": "exact_asset"},
    {"phrase": r"reserving oven time", "asset_id": "buyer-reservation-rail-v1", "strategy": "exact_asset"},
    {"phrase": r"strategic chokepoints", "asset_id": "strategic-chokepoint-network-v1", "strategy": "exact_asset"},
    {"phrase": r"future public-company cash flows", "asset_id": "capitalizes-industrial-cashflows-v1", "strategy": "exact_asset"},
    {"phrase": r"pipeline and reservoir", "asset_id": "hbm-pipeline-and-reservoir-v1", "strategy": "exact_asset"},
    {"phrase": r"open the other elevator", "asset_id": "safe-default-inspection-v1", "strategy": "exact_asset"},
    {"phrase": r"same causal weather system", "asset_id": "shared-cause-automatic-allocation-v1", "strategy": "exact_asset"},
    {"phrase": r"basketball roster", "asset_id": "index-roster-diworsification-v1", "strategy": "exact_asset"},
    {"phrase": r"twenty-five thousand dollars and wants one million", "asset_id": "return-hurdle-calculation-card-v1", "strategy": "component_composition"},
    {"phrase": r"design is a barbell", "asset_id": "two-sleeve-barbell-v1", "strategy": "exact_asset"},
    {"phrase": r"Market Leaders index", "asset_id": "market-leaders-qualified-comparison-card-v1", "strategy": "component_composition"},
    {"phrase": r"three failure points", "asset_id": "memory-three-failure-points-v1", "strategy": "exact_asset"},
    {"phrase": r"market-cap-weighted machine", "asset_id": "index-fund-weighted-inflows-v2", "strategy": "exact_asset"},
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _repo_path(path: Path) -> str:
    return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()


def _binding(path: Path, payload: Mapping[str, Any] | None = None) -> dict[str, str]:
    result = {"path": _repo_path(path), "sha256": file_sha256(path)}
    if payload is not None:
        result["artifact_hash"] = str(payload["artifact_hash"])
    return result


def _locator_hash(locator: Mapping[str, Any]) -> str:
    raw = json.dumps(dict(locator), sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _artifact_file_sha(payload: Mapping[str, Any]) -> str:
    raw = json.dumps(dict(payload), indent=2, ensure_ascii=False) + "\n"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _slug(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return normalized or "subject"


def _surface_ids(beat: Mapping[str, Any], numeric: Mapping[str, Any]) -> list[str]:
    text = str(beat["excerpt"]).lower()
    claims = set(beat.get("claim_refs", []))
    available = {
        str(item["surface_id"]): item
        for item in numeric.get("items", [])
        if item.get("claim_id") in claims
    }
    selected: list[str] = []
    if "sp500-top-ten-weight-2025" in available and any(term in text for term in ("forty percent", "ten largest", "ten companies", "concentrated")):
        selected.append("sp500-top-ten-weight-2025")
    if "generational-wealth-return-hurdle" in available and any(term in text for term in ("one million", "15.9 percent", "fifteen point nine")):
        selected.append("generational-wealth-return-hurdle")
    if "ten-percent-compound-example" in available and any(term in text for term in ("ten percent", "271,000", "271000")):
        selected.append("ten-percent-compound-example")
    if "sp500-ten-year-price-gain-compound-example" in available and any(term in text for term in ("600,000", "600000", "13.6 percent")):
        selected.append("sp500-ten-year-price-gain-compound-example")
    if "market-leaders-ten-year-price-return-2026-06-30" in available and any(term in text for term in ("16 percent", "sixteen percent", "annualized price return")):
        selected.extend([
            "market-leaders-ten-year-price-return-2026-06-30",
            "sp500-ten-year-price-return-2026-06-30",
        ])
    if "micron-trailing-return-2026-08-07" in available and "micron" in text and "return" in text:
        selected.extend([
            "micron-trailing-return-2026-08-07",
            "kospi-trailing-return-2026-08-07",
            "sp500-trailing-return-2026-08-07",
        ])
    return list(dict.fromkeys(item for item in selected if item in available))


def _source_records(claim_ledger: Mapping[str, Any]) -> tuple[list[dict[str, Any]], dict[str, list[str]], dict[str, dict[str, Any]]]:
    records: list[dict[str, Any]] = []
    by_claim: dict[str, list[str]] = {}
    claims: dict[str, dict[str, Any]] = {}
    for claim in claim_ledger.get("claims", []):
        claim_id = str(claim["claim_id"])
        claims[claim_id] = dict(claim)
        ids: list[str] = []
        for locator in claim.get("source_locators", []):
            record_id = f"{claim_id}--{locator['source_id']}"
            ids.append(record_id)
            records.append({
                "source_id": record_id,
                "claim_id": claim_id,
                "publisher": str(locator["publisher"]),
                "title": str(locator["title"]),
                "url": str(locator["url"]),
                "location": str(locator["location"]),
                "published_at": locator.get("published_at"),
                "accessed_at": locator.get("accessed_at"),
                "primary": bool(locator.get("primary")),
                "locator_sha256": _locator_hash(locator),
            })
        by_claim[claim_id] = ids
    return records, by_claim, claims


def _research_binding(
    beat: Mapping[str, Any],
    source_ids_by_claim: Mapping[str, list[str]],
    claim_index: Mapping[str, Mapping[str, Any]],
    surface_ids: list[str],
) -> dict[str, Any] | None:
    claim_refs = [str(item) for item in beat.get("claim_refs", [])]
    if not claim_refs:
        return None
    source_ids = [source_id for claim_id in claim_refs for source_id in source_ids_by_claim.get(claim_id, [])]
    as_of_dates = list(dict.fromkeys(claim_index[claim_id].get("as_of") for claim_id in claim_refs if claim_id in claim_index))
    classes = {str(claim_index[claim_id].get("classification")) for claim_id in claim_refs if claim_id in claim_index}
    if surface_ids:
        kind = "verified_calculation"
    elif source_ids:
        kind = "primary_source"
    elif "scenario" in classes:
        kind = "scenario"
    else:
        kind = "channel_inference"
    return {
        "request_id": f"research-{beat['beat_id']}",
        "beat_id": str(beat["beat_id"]),
        "claim_refs": claim_refs,
        "source_ids": list(dict.fromkeys(source_ids)),
        "evidence_surface_ids": surface_ids,
        "as_of_dates": as_of_dates,
        "binding_kind": kind,
        "status": "locator_bound",
    }


def _semantic_target(beat: Mapping[str, Any], selected_asset: Mapping[str, Any] | None) -> dict[str, Any]:
    nouns = list(dict.fromkeys(str(item["canonical"]) for item in beat["active_nouns"]))
    verb = str(beat["causal_verb"]["lemma"])
    if selected_asset is not None:
        anchors = list(selected_asset["capability_anchors"])
        prohibited = list(selected_asset.get("prohibited_implications", []))
    else:
        anchors = [f"recognizable-{_slug(noun)}" for noun in nouns[:3]]
        anchors.append(f"visible-{_slug(verb)}-relationship")
        prohibited = [
            "unlabeled-abstract-symbol",
            "unrelated-finance-decoration",
            "authoritative-text-or-number-in-generated-pixels",
        ]
    return {
        "active_nouns": nouns,
        "causal_verb": verb,
        "viewer_understanding": str(beat["viewer_understanding"]),
        "required_visual_anchors": list(dict.fromkeys(anchors)),
        "prohibited_implications": list(dict.fromkeys(prohibited or ["unsupported-causal-claim"])),
    }


def _representation_mode(beat: Mapping[str, Any]) -> str:
    if beat.get("needs_deterministic_fact_surface"):
        return "literal_evidence"
    text = str(beat["excerpt"]).lower()
    if any(term in text for term in ("hbm", "capacity", "contracts", "index", "weights", "cash flow", "rebalanc")):
        return "accurate_mechanism"
    return "declared_metaphor"


def _find_profile(beat: Mapping[str, Any], asset_index: Mapping[str, Mapping[str, Any]], used: set[str]) -> tuple[dict[str, Any], Mapping[str, Any]] | None:
    text = str(beat["excerpt"])
    claims = set(beat.get("claim_refs", []))
    for profile in EXACT_PROFILES:
        asset_id = str(profile["asset_id"])
        if asset_id in used or not re.search(str(profile["phrase"]), text, flags=re.IGNORECASE):
            continue
        asset = asset_index.get(asset_id)
        if asset is None or not asset.get("render_eligible") or asset.get("review_state") != "approved_reusable":
            continue
        if asset.get("reuse_policy", {}).get("claim_bound") and claims and not claims.issubset(set(asset.get("claim_refs", []))):
            continue
        return profile, asset
    return None


def _prompt(
    beat: Mapping[str, Any],
    target: Mapping[str, Any],
    *,
    context_before: str | None,
    context_after: str | None,
) -> dict[str, Any]:
    nouns = list(target["active_nouns"])
    noun_phrase = ", ".join(noun.replace("-", " ") for noun in nouns)
    verb = str(target["causal_verb"]).replace("-", " ")
    understanding = str(target["viewer_understanding"])
    prompt_id = f"prompt-{beat['beat_id']}"
    return {
        "prompt_id": prompt_id,
        "beat_id": str(beat["beat_id"]),
        "narration_excerpt": str(beat["excerpt"]),
        "context_before": context_before,
        "context_after": context_after,
        "semantic_job": (
            f"Show {noun_phrase} performing a visible {verb} relationship so {understanding}. "
            "Use adjacent narration only to resolve pronouns or incomplete compound clauses; do not merge neighboring beats."
        ),
        "active_nouns": nouns,
        "causal_verb": str(target["causal_verb"]),
        "prompt": (
            "Create one bright, premium editorial finance illustration in a handcrafted crinkle-cut woodblock paper style. "
            f"CURRENT NARRATION BEAT: {beat['excerpt']} "
            f"PRIOR CONTEXT FOR REFERENTS ONLY: {context_before or '[none]'} "
            f"NEXT CONTEXT FOR REFERENTS ONLY: {context_after or '[none]'} "
            "Illustrate only the current beat. Use adjacent context only to resolve referents, and do not collapse multiple beats into one plate. "
            f"The unmistakable subjects are {noun_phrase}; stage them so the causal action {verb} is visually legible. "
            f"The viewer must understand this idea without a caption: {understanding} "
            "Use friendly but adult proportions, recognizable economic objects, purposeful depth, clean silhouettes, and one dominant reading order. "
            "Leave only a modest quiet lower-edge or side pocket for deterministic compositor labels. Include no words, numerals, tickers, logos, or charts with invented values."
        ),
        "composition": "One dominant causal tableau, asymmetric editorial balance, full visual field, and a clearly separated action path between subjects.",
        "depth_plan": {
            "foreground": "one nearest prop or actor edge that motivates the causal action",
            "midground": "complete principal actors and economic objects with hands, feet, and contact shadows intact",
            "background": "specific business, market, industrial, or household context supporting this beat only",
            "negative_space": "a restrained local compositor pocket, never an empty third of the frame",
        },
        "negative_space": "Reserve at most a small local pocket; the illustration otherwise remains visually complete.",
        "avoid": [
            "authoritative text", "numbers in generated pixels", "ticker-like gibberish", "unrecognizable chart symbols",
            "generic money rain", "decorative flowers", "random office B-roll", "repeated elevator imagery",
            "giant empty parchment", "cards inside cards", "babyish clip art", "false causal implication",
        ],
        "factual_text_policy": "no_authoritative_text_or_numbers_in_generated_pixels",
        "review_state": "draft",
    }


def compile_asset_demand(pilot_root: Path = DEFAULT_PILOT) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    pilot_root = pilot_root.resolve()
    output_dir = pilot_root / OUTPUT_DIR
    semantic_dir = pilot_root / SEMANTIC_DIR
    ledger_path = output_dir / "semantic-beat-ledger.v1.json"
    catalog_path = semantic_dir / "asset-catalog.v2.json"
    claim_path = pilot_root / "claim-ledger.v1.json"
    numeric_path = semantic_dir / "numeric-evidence-register.v1.json"
    supplement_path = semantic_dir / "research-evidence-supplement.v1.json"

    ledger, catalog, claims = _load(ledger_path), _load(catalog_path), _load(claim_path)
    numeric, supplement = _load(numeric_path), _load(supplement_path)
    asset_index = {str(item["asset_id"]): item for item in catalog["assets"]}
    numeric_index = {str(item["surface_id"]): item for item in numeric["items"]}
    records, source_ids_by_claim, claim_index = _source_records(claims)

    research_bindings: list[dict[str, Any]] = []
    prompts: list[dict[str, Any]] = []
    demands: list[dict[str, Any]] = []
    used_assets: set[str] = set()

    ledger_beats = list(ledger["beats"])
    for beat_index, beat in enumerate(ledger_beats):
        surface_ids = _surface_ids(beat, numeric)
        research = _research_binding(beat, source_ids_by_claim, claim_index, surface_ids)
        if research is not None:
            research_bindings.append(research)
        matched = _find_profile(beat, asset_index, used_assets)
        selected_asset: Mapping[str, Any] | None = None
        selected_asset_ids: list[str] = []
        prompt_id: str | None = None
        if matched is not None:
            profile, selected_asset = matched
            asset_id = str(selected_asset["asset_id"])
            used_assets.add(asset_id)
            selected_asset_ids = [asset_id]
            strategy = str(profile["strategy"])
            status = "existing_approved" if strategy == "exact_asset" else "planned_pending_review"
            reason = (
                f"Explicit semantic profile {profile['phrase']!r} binds this beat to {asset_id}; "
                "the asset is approved, claim-compatible, and has not been assigned to another beat."
            )
            representation = str(selected_asset["representation_modes"][0])
        elif surface_ids:
            strategy, status, representation = "deterministic_surface", "planned_pending_review", "literal_evidence"
            reason = "Verified evidence surfaces match the spoken claim and will be constructed locally from bound values, dates, locators, and qualifiers."
        elif beat.get("needs_deterministic_fact_surface") and research and research["source_ids"]:
            strategy, status, representation = "source_retrieval_request", "planned_pending_review", "literal_evidence"
            reason = "This factual beat has source locators but no approved local evidence surface; retrieve the cited source rather than substitute unrelated imagery."
        elif beat.get("needs_deterministic_fact_surface") and beat.get("claim_refs"):
            strategy, status, representation = "deterministic_surface", "planned_pending_review", "literal_evidence"
            reason = "This qualified inference or scenario requires a local claim-and-qualifier surface; no unsupported number or source facsimile may be invented."
        else:
            strategy, status, representation = "original_generation_request", "planned_pending_review", _representation_mode(beat)
            reason = "No exact approved catalog asset depicts this sentence's nouns and causal action; generate a new beat-specific illustration rather than reuse a near match."

        target = _semantic_target(beat, selected_asset)
        if strategy == "original_generation_request":
            context_before = str(ledger_beats[beat_index - 1]["excerpt"]) if beat_index > 0 else None
            context_after = str(ledger_beats[beat_index + 1]["excerpt"]) if beat_index + 1 < len(ledger_beats) else None
            prompt = _prompt(
                beat,
                target,
                context_before=context_before,
                context_after=context_after,
            )
            prompts.append(prompt)
            prompt_id = str(prompt["prompt_id"])
        request_ids = [str(research["request_id"])] if research is not None else []
        demands.append({
            "demand_id": f"asset-demand-{beat['beat_id']}",
            "beat_id": str(beat["beat_id"]),
            "chapter_id": str(beat["chapter_id"]),
            "start_word_index": int(beat["start_word_index"]),
            "end_word_index": int(beat["end_word_index"]),
            "start_s": float(beat["start_s"]),
            "end_s": float(beat["end_s"]),
            "excerpt": str(beat["excerpt"]),
            "claim_refs": list(beat.get("claim_refs", [])),
            "semantic_target": target,
            "representation_mode": representation,
            "strategy": strategy,
            "resolution_reason": reason,
            "selected_asset_ids": selected_asset_ids,
            "reuse_reason": None,
            "evidence_surface_ids": surface_ids,
            "source_request_ids": request_ids,
            "prompt_id": prompt_id,
            "status": status,
        })

    research_manifest = with_artifact_hash({
        "schema_version": "finance_research_resolution.v1",
        "episode_id": str(ledger["episode_id"]),
        "source_bindings": [
            {"kind": "claim_ledger", **_binding(claim_path, claims)},
            {"kind": "numeric_evidence_register", **_binding(numeric_path, numeric)},
            {"kind": "research_evidence_supplement", **_binding(supplement_path, supplement)},
        ],
        "source_records": records,
        "beat_bindings": research_bindings,
        "review_state": "draft",
    })
    prompt_spine = with_artifact_hash({
        "schema_version": "finance_generation_prompt_spine.v1",
        "episode_id": str(ledger["episode_id"]),
        "asset_demand_path": _repo_path(output_dir / "asset-demand.v1.json"),
        "style_contract": {
            "material": "handcrafted crinkle-cut woodblock paper with trace-cut actors and economic objects",
            "tone": "bright, friendly, adult editorial finance illustration",
            "resolution": "1920x1080",
            "depth_layers": ["foreground", "midground", "background", "negative_space"],
            "factual_text_policy": "no_authoritative_text_or_numbers_in_generated_pixels",
            "safe_area_policy": "keep principal hands, faces, causal objects, and evidence docks clear of the lower caption band",
        },
        "prompts": prompts,
        "review_state": "draft",
        "provider_calls_authorized": False,
    })
    strategy_counts = dict(sorted(Counter(item["strategy"] for item in demands).items()))
    demand_manifest = with_artifact_hash({
        "schema_version": "finance_asset_demand.v1",
        "episode_id": str(ledger["episode_id"]),
        "source_bindings": {
            "semantic_beat_ledger": _binding(ledger_path, ledger),
            "asset_catalog": _binding(catalog_path, catalog),
            "claim_ledger": _binding(claim_path),
            "numeric_evidence_register": _binding(numeric_path, numeric),
            "research_evidence_supplement": _binding(supplement_path, supplement),
        },
        "planning_outputs": {
            "research_resolution": {"path": _repo_path(output_dir / "research-resolution.v1.json"), "sha256": _artifact_file_sha(research_manifest), "artifact_hash": research_manifest["artifact_hash"]},
            "generation_prompt_spine": {"path": _repo_path(output_dir / "generation-prompt-spine.v1.json"), "sha256": _artifact_file_sha(prompt_spine), "artifact_hash": prompt_spine["artifact_hash"]},
        },
        "resolution_order": RESOLUTION_ORDER,
        "summary": {
            "beat_count": len(demands),
            "strategy_counts": strategy_counts,
            "all_beats_have_resolution_path": True,
            "unapproved_asset_count": sum(item["status"] != "existing_approved" for item in demands),
        },
        "demands": demands,
        "review_state": "draft",
        "render_eligible": False,
    })
    return demand_manifest, research_manifest, prompt_spine


def write_package(pilot_root: Path = DEFAULT_PILOT) -> tuple[Path, Path, Path]:
    demand, research, prompts = compile_asset_demand(pilot_root)
    output_dir = pilot_root.resolve() / OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    research_path = output_dir / "research-resolution.v1.json"
    prompt_path = output_dir / "generation-prompt-spine.v1.json"
    research_path.write_text(json.dumps(research, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    prompt_path.write_text(json.dumps(prompts, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    demand_path = output_dir / "asset-demand.v1.json"
    demand_path.write_text(json.dumps(demand, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    validate_finance_asset_demand_package(demand, research, prompts, REPO_ROOT)
    return demand_path, research_path, prompt_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot-root", type=Path, default=DEFAULT_PILOT)
    args = parser.parse_args()
    paths = write_package(args.pilot_root)
    for path in paths:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
