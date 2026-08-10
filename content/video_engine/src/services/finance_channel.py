"""Deterministic contracts for the finance/business/economics channel.

This module deliberately performs no network, provider, render, or publication
work.  It validates operator-authored artifacts and supplies deterministic
topic scoring and asset-resolution decisions.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from jsonschema import Draft7Validator, FormatChecker

from content.video_engine.src.services.finance_visual_selection import validate_reuse


CONFIG_ROOT = Path(__file__).resolve().parents[2] / "configs"
SCHEMAS = {
    "finance_channel_profile.v1": "finance_channel_profile.schema.json",
    "finance_schedule.v1": "finance_schedule.schema.json",
    "finance_episode_brief.v1": "finance_episode_brief.schema.json",
    "finance_claim_ledger.v1": "finance_claim_ledger.schema.json",
    "finance_semantic_beat_ledger.v1": "finance_semantic_beat_ledger_v1.schema.json",
    "finance_asset_demand.v1": "finance_asset_demand_v1.schema.json",
    "finance_research_resolution.v1": "finance_research_resolution_v1.schema.json",
    "finance_generation_prompt_spine.v1": "finance_generation_prompt_spine_v1.schema.json",
    "finance_layered_composition.v1": "finance_layered_composition_v1.schema.json",
    "finance_visual_cue_sheet.v1": "finance_visual_cue_sheet.schema.json",
    "finance_visual_cue_sheet.v2": "finance_visual_cue_sheet_v2.schema.json",
    "finance_visual_resolution.v1": "finance_visual_resolution_v1.schema.json",
    "finance_numeric_evidence_register.v1": "finance_numeric_evidence_register_v1.schema.json",
    "finance_market_data_packet.v1": "finance_market_data_packet_v1.schema.json",
    "finance_edit_manifest.v1": "finance_edit_manifest.schema.json",
    "finance_asset_catalog.v1": "finance_asset_catalog.schema.json",
    "finance_asset_catalog.v2": "finance_asset_catalog_v2.schema.json",
    "finance_reference_learnings.v1": "finance_reference_learnings.schema.json",
}

TOPIC_WEIGHTS = {
    "audience_contradiction": 0.18,
    "ordinary_financial_importance": 0.14,
    "primary_evidence": 0.16,
    "hidden_mechanism": 0.15,
    "visualizability": 0.10,
    "shelf_life": 0.08,
    "graph_connection": 0.07,
    "defensible_conclusion": 0.12,
}
TOPIC_PENALTIES = {"production_cost": 0.05, "editorial_risk": 0.05}


class FinanceChannelValidationError(ValueError):
    """Raised when a finance-channel artifact violates a hard contract."""

    def __init__(self, errors: Sequence[str]):
        self.errors = tuple(errors)
        super().__init__("; ".join(self.errors))


def load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def canonical_json(payload: Mapping[str, Any]) -> str:
    core = dict(payload)
    core.pop("artifact_hash", None)
    return json.dumps(core, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def canonical_sha256(payload: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def file_sha256(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def with_artifact_hash(payload: Mapping[str, Any]) -> dict[str, Any]:
    result = dict(payload)
    result["artifact_hash"] = canonical_sha256(result)
    return result


def _schema_errors(payload: Mapping[str, Any]) -> list[str]:
    version = str(payload.get("schema_version") or "")
    schema_name = SCHEMAS.get(version)
    if not schema_name:
        return [f"unsupported schema_version: {version!r}"]
    schema = load_json(CONFIG_ROOT / schema_name)
    errors = sorted(
        Draft7Validator(schema, format_checker=FormatChecker()).iter_errors(dict(payload)),
        key=lambda error: list(error.absolute_path),
    )
    return [
        f"{'.'.join(str(part) for part in error.absolute_path) or '<root>'}: {error.message}"
        for error in errors
    ]


def _hash_errors(payload: Mapping[str, Any]) -> list[str]:
    declared = str(payload.get("artifact_hash") or "")
    expected = canonical_sha256(payload)
    return [] if declared == expected else [f"artifact_hash is stale: expected {expected}"]


def validate_artifact(payload: Mapping[str, Any]) -> dict[str, Any]:
    errors = _schema_errors(payload) + _hash_errors(payload)
    version = payload.get("schema_version")
    if version == "finance_channel_profile.v1":
        errors.extend(_channel_profile_errors(payload))
    elif version == "finance_schedule.v1":
        errors.extend(_schedule_errors(payload))
    elif version == "finance_episode_brief.v1":
        errors.extend(_episode_brief_errors(payload))
    elif version == "finance_claim_ledger.v1":
        errors.extend(_claim_ledger_errors(payload))
    elif version == "finance_semantic_beat_ledger.v1":
        errors.extend(_semantic_beat_ledger_errors(payload))
    elif version == "finance_asset_demand.v1":
        errors.extend(_asset_demand_errors(payload))
    elif version == "finance_research_resolution.v1":
        errors.extend(_research_resolution_errors(payload))
    elif version == "finance_generation_prompt_spine.v1":
        errors.extend(_generation_prompt_spine_errors(payload))
    elif version == "finance_layered_composition.v1":
        errors.extend(_layered_composition_errors(payload))
    elif version == "finance_visual_cue_sheet.v1":
        errors.extend(_cue_sheet_errors(payload))
    elif version == "finance_visual_cue_sheet.v2":
        errors.extend(_cue_sheet_errors(payload))
        errors.extend(_semantic_cue_sheet_errors(payload))
    elif version == "finance_numeric_evidence_register.v1":
        errors.extend(_numeric_evidence_errors(payload))
    elif version == "finance_market_data_packet.v1":
        from content.video_engine.src.services.finance_market_data import validate_market_data_packet

        try:
            validate_market_data_packet(payload)
        except FinanceChannelValidationError as exc:
            errors.extend(exc.errors)
    elif version == "finance_visual_resolution.v1":
        errors.extend(_resolution_shape_errors(payload))
    elif version == "finance_edit_manifest.v1":
        errors.extend(_edit_manifest_errors(payload))
    if errors:
        raise FinanceChannelValidationError(errors)
    return dict(payload)


def _channel_profile_errors(payload: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    budget = payload.get("complexity_budget", {})
    if isinstance(budget, Mapping) and sum(int(budget.get(key, 0)) for key in ("reusable_percent", "evidence_percent", "bespoke_percent")) != 100:
        errors.append("complexity_budget percentages must total 100")
    worlds = set(payload.get("visual_worlds", []))
    if worlds != {"story", "mechanism", "evidence"}:
        errors.append("visual_worlds must contain story, mechanism, and evidence exactly")
    formats = {item.get("id") for item in payload.get("formats", []) if isinstance(item, Mapping)}
    if formats != {"economic_anatomy", "one_level_deeper", "current_mechanism"}:
        errors.append("formats must contain each long-form class exactly once")
    if payload.get("render_eligible") and payload.get("state") != "operator_approved":
        errors.append("render_eligible channel profile must be operator_approved")
    return errors


def _schedule_errors(payload: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    releases = [item for item in payload.get("releases", []) if isinstance(item, Mapping)]
    slot_ids = [str(item.get("slot_id")) for item in releases]
    if len(slot_ids) != len(set(slot_ids)):
        errors.append("schedule slot_id values must be unique")
    longs = {(item.get("day"), item.get("format")): item for item in releases if item.get("kind") == "long"}
    required = {
        ("Friday", "current_mechanism"),
        ("Saturday", "economic_anatomy"),
        ("Sunday", "one_level_deeper"),
    }
    if set(longs) != required:
        errors.append("long-form schedule must be Friday current, Saturday anatomy, Sunday deeper")
    friday = longs.get(("Friday", "current_mechanism"), {})
    if str(friday.get("local_time", "00:00")) < "16:00":
        errors.append("Friday current mechanism must release after U.S. market close")
    long_ids = {str(item.get("slot_id")) for item in longs.values()}
    shorts = [item for item in releases if item.get("kind") == "short"]
    if len(shorts) != 3 or any(item.get("format") != "embedded_short" for item in shorts):
        errors.append("schedule must contain exactly three embedded Shorts")
    short_parents = [str(item.get("parent_slot_id")) for item in shorts]
    if set(short_parents) != long_ids or len(short_parents) != len(set(short_parents)):
        errors.append("each Short must map one-to-one to a weekend long-form slot")
    if any(item.get("day") in {"Friday", "Saturday", "Sunday"} for item in shorts):
        errors.append("embedded Shorts must release on weekdays")
    return errors


def _episode_brief_errors(payload: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    packages = [item for item in payload.get("packages", []) if isinstance(item, Mapping)]
    promise_keys = {item.get("promise_key") for item in packages}
    families = {item.get("family") for item in packages}
    if len(promise_keys) != 1:
        errors.append("all package tests must resolve to the same episode promise")
    if families != {"contradiction", "identity", "mechanism"}:
        errors.append("packages must test contradiction, identity, and mechanism families")
    blockers = payload.get("research_blockers", [])
    if payload.get("render_eligible"):
        if payload.get("state") != "operator_approved" or payload.get("thesis_state") != "operator_approved":
            errors.append("render-eligible brief requires operator-approved state and thesis")
        if blockers:
            errors.append("render-eligible brief cannot retain research blockers")
    forbidden = _recommendation_language_errors(str(payload.get("thesis", "")))
    errors.extend(f"thesis {item}" for item in forbidden)
    return errors


def _recommendation_language_errors(text: str) -> list[str]:
    patterns = (
        r"\b(?:you should|i recommend|you must|go)\s+(?:buy|sell|short|invest)\b",
        r"\b(?:buy|sell|short)\s+(?:this|it|now|today)\b",
        r"\bput your money (?:in|into)\b",
    )
    return ["contains personalized buy/sell instruction"] if any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns) else []


def _claim_ledger_errors(payload: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("contrarian_frame"):
        if len(str(payload.get("countercase", "")).strip()) < 20:
            errors.append("contrarian ledger requires a material countercase")
        if not payload.get("failure_conditions"):
            errors.append("contrarian ledger requires failure conditions")
    claims = [item for item in payload.get("claims", []) if isinstance(item, Mapping)]
    ids = {str(item.get("claim_id")) for item in claims}
    for index, claim in enumerate(claims):
        label = f"claims[{index}]"
        classification = claim.get("classification")
        sources = [source for source in claim.get("source_locators", []) if isinstance(source, Mapping)]
        if classification in {"observed_fact", "calculation", "sourced_interpretation"}:
            if not sources:
                errors.append(f"{label} requires a source locator")
            elif not any(source.get("primary") for source in sources):
                errors.append(f"{label} requires at least one primary source")
        if classification == "market_snapshot":
            if not sources:
                errors.append(f"{label} market snapshot requires a source locator")
            if not claim.get("market_data_packet_hash"):
                errors.append(f"{label} market snapshot requires a market_data_packet_hash")
        if claim.get("temporal_kind") in {"dated", "current", "numeric"} and not claim.get("as_of"):
            errors.append(f"{label} requires an as_of date")
        if classification == "calculation" and not claim.get("calculation"):
            errors.append(f"{label} calculation requires formula, inputs, and result")
        if classification in {"channel_inference", "scenario"} and len(str(claim.get("qualifier", "")).strip()) < 8:
            errors.append(f"{label} inference/scenario requires a plain qualifier")
        for ref in claim.get("counterevidence_refs", []):
            if ref not in ids:
                errors.append(f"{label} counterevidence ref {ref!r} is unknown")
        errors.extend(f"{label} {item}" for item in _recommendation_language_errors(str(claim.get("text", ""))))
    if payload.get("research_state") in {"source_locked", "operator_approved"} and not claims:
        errors.append("source-locked ledger cannot be empty")
    return errors


def _semantic_beat_ledger_errors(payload: Mapping[str, Any]) -> list[str]:
    """Enforce the word-contiguous contract before visual resolution begins."""

    errors: list[str] = []
    timing = payload.get("timing", {})
    word_count = int(timing.get("word_count", 0)) if isinstance(timing, Mapping) else 0
    beats = [item for item in payload.get("beats", []) if isinstance(item, Mapping)]
    beat_ids = [str(item.get("beat_id", "")) for item in beats]
    if len(beat_ids) != len(set(beat_ids)):
        errors.append("semantic beat IDs must be unique")

    expected_start = 0
    for index, beat in enumerate(beats):
        label = f"beats[{index}]"
        start_word = int(beat.get("start_word_index", -1))
        end_word = int(beat.get("end_word_index", -1))
        if start_word != expected_start:
            errors.append(
                f"{label} must start at canonical word {expected_start}, got {start_word}"
            )
        if end_word < start_word:
            errors.append(f"{label} end_word_index precedes start_word_index")
        expected_start = end_word + 1
        if not beat.get("active_nouns"):
            errors.append(f"{label} requires at least one active noun")
        causal_verb = beat.get("causal_verb")
        if not isinstance(causal_verb, Mapping) or not str(causal_verb.get("surface", "")).strip():
            errors.append(f"{label} requires a causal verb bound to a canonical word")

    if expected_start != word_count:
        errors.append(
            f"semantic beats cover {expected_start} canonical words, expected {word_count}"
        )

    chapters = [item for item in payload.get("chapters", []) if isinstance(item, Mapping)]
    chapter_ids = {str(item.get("chapter_id", "")) for item in chapters}
    reviews = [
        item
        for item in payload.get("chapter_boundary_review", [])
        if isinstance(item, Mapping)
    ]
    reviewed_ids = {
        str(item.get("chapter_id", ""))
        for item in reviews
        if item.get("status") == "manually_reviewed"
    }
    if reviewed_ids != chapter_ids:
        errors.append("every chapter boundary must be manually reviewed exactly once")
    return errors


def _asset_demand_errors(payload: Mapping[str, Any]) -> list[str]:
    """Reject partial demand ledgers and convenient, unexplained reuse."""

    errors: list[str] = []
    demands = [item for item in payload.get("demands", []) if isinstance(item, Mapping)]
    beat_ids = [str(item.get("beat_id", "")) for item in demands]
    demand_ids = [str(item.get("demand_id", "")) for item in demands]
    if len(beat_ids) != len(set(beat_ids)):
        errors.append("asset demand must contain exactly one resolution path per beat")
    if len(demand_ids) != len(set(demand_ids)):
        errors.append("asset demand IDs must be unique")
    selected_usage: Counter[str] = Counter()
    strategy_counts: Counter[str] = Counter()
    for index, demand in enumerate(demands):
        label = f"demands[{index}]"
        strategy = str(demand.get("strategy", ""))
        strategy_counts[strategy] += 1
        selected = [str(item) for item in demand.get("selected_asset_ids", [])]
        surfaces = [str(item) for item in demand.get("evidence_surface_ids", [])]
        sources = [str(item) for item in demand.get("source_request_ids", [])]
        prompt_id = demand.get("prompt_id")
        for asset_id in selected:
            selected_usage[asset_id] += 1
        if strategy in {"exact_asset", "component_composition"} and not selected:
            errors.append(f"{label} {strategy} requires an explicit selected asset")
        if strategy not in {"exact_asset", "component_composition"} and selected:
            errors.append(f"{label} {strategy} cannot carry a convenient selected asset")
        if strategy == "deterministic_surface" and not (surfaces or demand.get("claim_refs")):
            errors.append(f"{label} deterministic surface requires evidence or a qualified claim")
        if strategy == "source_retrieval_request" and not sources:
            errors.append(f"{label} source retrieval requires a source request")
        if strategy == "original_generation_request" and not prompt_id:
            errors.append(f"{label} original generation requires a prompt ID")
        if strategy != "original_generation_request" and prompt_id is not None:
            errors.append(f"{label} non-generation path cannot reference a generation prompt")
        target = demand.get("semantic_target", {})
        if isinstance(target, Mapping):
            if not target.get("active_nouns") or not target.get("causal_verb"):
                errors.append(f"{label} requires active nouns and a causal verb")
    repeated = sorted(asset_id for asset_id, count in selected_usage.items() if count > 1)
    if repeated:
        errors.append(
            "asset demand cannot assign the same existing asset to multiple beats before a "
            f"reviewed reuse decision: {', '.join(repeated)}"
        )
    summary = payload.get("summary", {})
    if isinstance(summary, Mapping):
        if int(summary.get("beat_count", -1)) != len(demands):
            errors.append("asset-demand summary beat_count is stale")
        if dict(summary.get("strategy_counts", {})) != dict(sorted(strategy_counts.items())):
            errors.append("asset-demand summary strategy_counts are stale")
    expected_order = [
        "exact_asset",
        "component_composition",
        "deterministic_surface",
        "source_retrieval_request",
        "original_generation_request",
    ]
    if payload.get("resolution_order") != expected_order:
        errors.append("asset-demand resolution_order must preserve the five-tier P21 contract")
    if payload.get("render_eligible"):
        errors.append("asset-demand planning artifact cannot itself be render eligible")
    return errors


def _research_resolution_errors(payload: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    records = [item for item in payload.get("source_records", []) if isinstance(item, Mapping)]
    record_ids = [str(item.get("source_id", "")) for item in records]
    if len(record_ids) != len(set(record_ids)):
        errors.append("research source IDs must be unique")
    for index, record in enumerate(records):
        locator = {
            "source_id": str(record.get("source_id", "")).split("--", 1)[-1],
            "publisher": record.get("publisher"),
            "title": record.get("title"),
            "url": record.get("url"),
            "location": record.get("location"),
            "published_at": record.get("published_at"),
            "accessed_at": record.get("accessed_at"),
            "primary": record.get("primary"),
        }
        expected = hashlib.sha256(
            json.dumps(locator, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        ).hexdigest()
        if record.get("locator_sha256") != expected:
            errors.append(f"source_records[{index}] locator_sha256 is stale")
        if not (record.get("published_at") or record.get("accessed_at")):
            errors.append(f"source_records[{index}] requires a publication or access date")
    bindings = [item for item in payload.get("beat_bindings", []) if isinstance(item, Mapping)]
    request_ids = [str(item.get("request_id", "")) for item in bindings]
    beat_ids = [str(item.get("beat_id", "")) for item in bindings]
    if len(request_ids) != len(set(request_ids)) or len(beat_ids) != len(set(beat_ids)):
        errors.append("research manifest requires one unique request per bound beat")
    known_sources = set(record_ids)
    for index, binding in enumerate(bindings):
        unknown = set(binding.get("source_ids", [])) - known_sources
        if unknown:
            errors.append(f"beat_bindings[{index}] references unknown sources: {', '.join(sorted(unknown))}")
        if not (binding.get("source_ids") or binding.get("evidence_surface_ids") or binding.get("binding_kind") in {"channel_inference", "scenario"}):
            errors.append(f"beat_bindings[{index}] has no evidence or qualified inference path")
    return errors


def _generation_prompt_spine_errors(payload: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    prompts = [item for item in payload.get("prompts", []) if isinstance(item, Mapping)]
    prompt_ids = [str(item.get("prompt_id", "")) for item in prompts]
    beat_ids = [str(item.get("beat_id", "")) for item in prompts]
    if len(prompt_ids) != len(set(prompt_ids)) or len(beat_ids) != len(set(beat_ids)):
        errors.append("generation prompt spine requires one unique prompt per generation beat")
    banned = ("generic money rain", "giant empty parchment", "unrecognizable chart symbols")
    for index, prompt in enumerate(prompts):
        text = str(prompt.get("prompt", "")).lower()
        if any(term not in {str(item).lower() for item in prompt.get("avoid", [])} for term in banned):
            errors.append(f"prompts[{index}] must explicitly prohibit common finance visual failures")
        if not prompt.get("active_nouns") or not prompt.get("causal_verb"):
            errors.append(f"prompts[{index}] requires semantic nouns and a causal verb")
        if any(token in text for token in ("write the number", "label the chart", "include ticker text")):
            errors.append(f"prompts[{index}] attempts to generate authoritative factual text")
    if payload.get("provider_calls_authorized"):
        errors.append("prompt planning artifact cannot authorize provider calls")
    return errors


def _layered_composition_errors(payload: Mapping[str, Any], *, tolerance: float = 0.002) -> list[str]:
    errors: list[str] = []
    cues = [item for item in payload.get("cues", []) if isinstance(item, Mapping)]
    cue_ids = [str(item.get("cue_id", "")) for item in cues]
    beat_ids = [str(item.get("beat_id", "")) for item in cues]
    if len(cue_ids) != len(set(cue_ids)) or len(beat_ids) != len(set(beat_ids)):
        errors.append("layered composition requires one unique cue per semantic beat")
    expected_word = 0
    expected_time = 0.0
    role_counts: Counter[str] = Counter()
    non_evidence = 0
    non_evidence_three_plus = 0
    camera_only = 0
    camera_actions = {"camera", "camera_pan", "pan", "zoom", "push_in", "pull_out", "locked", "none"}
    for cue_index, cue in enumerate(cues):
        label = f"cues[{cue_index}]"
        word_range = cue.get("word_range", {})
        time_range = cue.get("time_range", {})
        start_word = int(word_range.get("start_index", -1))
        end_word = int(word_range.get("end_index", -1))
        start_s = float(time_range.get("start_s", -1))
        end_s = float(time_range.get("end_s", -1))
        if start_word != expected_word or end_word < start_word:
            errors.append(f"{label} word range leaves a gap or overlap")
        if abs(start_s - expected_time) > tolerance or end_s <= start_s:
            errors.append(f"{label} time range leaves a gap or overlap")
        expected_word, expected_time = end_word + 1, end_s
        layers = [item for item in cue.get("layers", []) if isinstance(item, Mapping)]
        layer_ids = [str(item.get("layer_id", "")) for item in layers]
        if len(layer_ids) != len(set(layer_ids)):
            errors.append(f"{label} layer IDs must be unique")
        roles = [str(item.get("role", "")) for item in layers]
        role_counts.update(roles)
        if roles.count("world") != 1:
            errors.append(f"{label} requires exactly one visible world layer")
        if roles.count("transition") != 1:
            errors.append(f"{label} requires exactly one transition layer")
        if "subject" not in roles or not ({"prop", "mechanism"} & set(roles)):
            errors.append(f"{label} requires subject plus prop or mechanism layers")
        if cue.get("evidence_surface_ids") and "evidence" not in roles:
            errors.append(f"{label} verified evidence surfaces require an evidence layer")
        meaningful_actions: list[str] = []
        for layer_index, layer in enumerate(layers):
            layer_label = f"{label}.layers[{layer_index}]"
            layer_words = layer.get("word_range", {})
            action_words = layer.get("action_word_range", {})
            layer_time = layer.get("time_range", {})
            action_time = layer.get("action_time_range", {})
            layer_start = int(layer_words.get("start_index", -1))
            layer_end = int(layer_words.get("end_index", -1))
            action_start = int(action_words.get("start_index", -1))
            action_end = int(action_words.get("end_index", -1))
            layer_start_s = float(layer_time.get("start_s", -1))
            layer_end_s = float(layer_time.get("end_s", -1))
            action_start_s = float(action_time.get("start_s", -1))
            action_end_s = float(action_time.get("end_s", -1))
            if layer_start < start_word or layer_end > end_word or layer_end < layer_start:
                errors.append(f"{layer_label} word range escapes its cue")
            if action_start < layer_start or action_end > layer_end or action_end < action_start:
                errors.append(f"{layer_label} action word range escapes its layer")
            if layer_start_s < start_s - tolerance or layer_end_s > end_s + tolerance or layer_end_s <= layer_start_s:
                errors.append(f"{layer_label} time range escapes its cue")
            if action_start_s < layer_start_s - tolerance or action_end_s > layer_end_s + tolerance or action_end_s <= action_start_s:
                errors.append(f"{layer_label} action time range escapes its layer")
            action = str(layer.get("action", "")).casefold()
            if layer.get("role") != "world" and action not in camera_actions:
                meaningful_actions.append(action)
        if not meaningful_actions:
            camera_only += 1
            errors.append(f"{label} is camera-only; add a subject, prop, mechanism, evidence, or transition action")
        has_evidence = "evidence" in roles
        if not has_evidence:
            non_evidence += 1
            if len([role for role in roles if role != "transition"]) >= 3:
                non_evidence_three_plus += 1
    timing = payload.get("timing", {})
    if expected_word != int(timing.get("word_count", 0)):
        errors.append("layered cues do not cover every canonical word")
    if abs(expected_time - float(timing.get("duration_s", 0))) > tolerance:
        errors.append("layered cues do not cover canonical duration")
    required_roles = {"world", "subject", "prop", "mechanism", "evidence", "transition"}
    if not required_roles.issubset(role_counts):
        errors.append("layered composition must exercise all six finance layer roles")
    ratio = 1.0 if not non_evidence else round(non_evidence_three_plus / non_evidence, 6)
    if ratio < 0.7:
        errors.append("fewer than 70% of non-evidence cues contain three meaningful layers")
    summary = payload.get("summary", {})
    if isinstance(summary, Mapping):
        expected_summary = {
            "cue_count": len(cues),
            "role_counts": dict(sorted(role_counts.items())),
            "non_evidence_cue_count": non_evidence,
            "non_evidence_three_plus_layer_count": non_evidence_three_plus,
            "non_evidence_three_plus_layer_ratio": ratio,
            "camera_only_cue_count": camera_only,
        }
        for key, value in expected_summary.items():
            if summary.get(key) != value:
                errors.append(f"layered composition summary {key} is stale")
    return errors


def _cue_sheet_errors(payload: Mapping[str, Any], *, tolerance: float = 0.002) -> list[str]:
    errors: list[str] = []
    narration = payload.get("narration", {})
    cues = [item for item in payload.get("cues", []) if isinstance(item, Mapping)]
    if not cues:
        return errors
    expected_word = 0
    expected_time = 0.0
    memberships: set[str] = set()
    for index, cue in enumerate(cues):
        label = f"cues[{index}]"
        start_word, end_word = int(cue.get("start_word", -1)), int(cue.get("end_word", -1))
        start_s, end_s = float(cue.get("start_s", -1)), float(cue.get("end_s", -1))
        if start_word != expected_word:
            errors.append(f"{label} word range leaves a gap or overlap")
        if abs(start_s - expected_time) > tolerance:
            errors.append(f"{label} time range leaves a gap or overlap")
        if end_word < start_word or end_s <= start_s:
            errors.append(f"{label} range must advance")
        events = [event for event in cue.get("micro_events", []) if isinstance(event, Mapping)]
        if end_s - start_s > 4.0 and len(events) < 2:
            errors.append(f"{label} exceeds four seconds without two timed micro-events")
        for event in events:
            at_s = float(event.get("at_s", -1))
            if at_s < start_s - tolerance or at_s > end_s + tolerance:
                errors.append(f"{label} micro-event falls outside its cue")
        memberships.update(str(item) for item in cue.get("short_membership", []))
        expected_word, expected_time = end_word + 1, end_s
    if expected_word != int(narration.get("word_count", 0)):
        errors.append("cue words do not cover the canonical narration")
    if abs(expected_time - float(narration.get("duration_s", 0))) > tolerance:
        errors.append("cue times do not cover the canonical narration")
    short_ids = {str(item.get("short_id")) for item in payload.get("short_ranges", []) if isinstance(item, Mapping)}
    if memberships - short_ids:
        errors.append("cue short_membership references an unknown short range")
    return errors


def _semantic_cue_sheet_errors(payload: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    ids: set[str] = set()
    calls: set[str] = set()
    for index, cue in enumerate(payload.get("cues", [])):
        if not isinstance(cue, Mapping):
            continue
        label = f"cues[{index}]"
        cue_id, call_id = str(cue.get("cue_id")), str(cue.get("call_cue_id"))
        if cue_id in ids:
            errors.append(f"{label} cue_id must be unique")
        if call_id in calls:
            errors.append(f"{label} call_cue_id must be unique")
        ids.add(cue_id)
        calls.add(call_id)
        target = cue.get("semantic_target", {})
        if not isinstance(target, Mapping) or not target.get("required_visual_anchors"):
            errors.append(f"{label} requires semantic visual anchors")
        if cue.get("representation_mode") == "literal_evidence" and not cue.get("claim_refs"):
            errors.append(f"{label} literal evidence requires claim_refs")
        if cue.get("evidence_surface_ids") and not cue.get("claim_refs"):
            errors.append(f"{label} evidence surfaces require claim_refs")
    return errors


def _numeric_evidence_errors(payload: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    ids: set[str] = set()
    for index, item in enumerate(payload.get("items", [])):
        if not isinstance(item, Mapping):
            continue
        surface_id = str(item.get("surface_id"))
        if surface_id in ids:
            errors.append(f"items[{index}] surface_id must be unique")
        ids.add(surface_id)
        value = item.get("display_value")
        if isinstance(value, str) and not value.strip():
            errors.append(f"items[{index}] display_value cannot be blank")
        if not str(item.get("report_locator", "")).strip():
            errors.append(f"items[{index}] requires a verified report locator")
    return errors


def _resolution_shape_errors(payload: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    ids: set[str] = set()
    cue_ids: set[str] = set()
    for index, resolution in enumerate(payload.get("resolutions", [])):
        if not isinstance(resolution, Mapping):
            continue
        label = f"resolutions[{index}]"
        resolution_id, cue_id = str(resolution.get("resolution_id")), str(resolution.get("cue_id"))
        if resolution_id in ids:
            errors.append(f"{label} resolution_id must be unique")
        if cue_id in cue_ids:
            errors.append(f"{label} cue_id must be unique")
        ids.add(resolution_id)
        cue_ids.add(cue_id)
        status = resolution.get("status")
        strategy = resolution.get("strategy")
        selected = resolution.get("selected_asset_ids", [])
        demand = resolution.get("demand")
        if status == "resolved" and (not selected or demand is not None):
            errors.append(f"{label} resolved state requires selected assets and no demand")
        if status == "unresolved" and (selected or not isinstance(demand, Mapping)):
            errors.append(f"{label} unresolved state requires a demand and no selected assets")
        if status == "unresolved" and strategy not in {"source_retrieval_request", "original_generation_request", "local_compositor_request", "script_revision_request"}:
            errors.append(f"{label} unresolved state requires a demand strategy")
        if status == "resolved" and strategy not in {"exact_asset", "component_composition", "deterministic_surface"}:
            errors.append(f"{label} resolved state requires a resolution strategy")
    if payload.get("render_eligible"):
        if payload.get("review_state") != "operator_approved":
            errors.append("render-eligible resolution manifest must be operator approved")
        if any(item.get("status") != "resolved" for item in payload.get("resolutions", []) if isinstance(item, Mapping)):
            errors.append("render-eligible resolution manifest cannot contain unresolved cues")
    return errors


def _edit_manifest_errors(payload: Mapping[str, Any]) -> list[str]:
    if payload.get("render_eligible") and payload.get("review_state") != "operator_approved":
        return ["render-eligible edit manifest must be operator approved"]
    return []


def validate_asset_catalog(payload: Mapping[str, Any], project_root: str | Path) -> dict[str, Any]:
    errors = _schema_errors(payload) + _hash_errors(payload)
    expected_order = [
        "exact_semantic_match",
        "reusable_component_composition",
        "deterministic_evidence_or_mechanism",
        "bespoke_plate",
    ]
    if payload.get("resolution_order") != expected_order:
        errors.append("asset resolution_order must preserve the four-tier contract")
    root = Path(project_root).resolve()
    for index, asset in enumerate(payload.get("assets", [])):
        if not isinstance(asset, Mapping):
            continue
        label = f"assets[{index}]"
        candidate = (root / str(asset.get("path", ""))).resolve()
        try:
            candidate.relative_to(root)
        except ValueError:
            errors.append(f"{label} path escapes project root")
            continue
        if not candidate.is_file():
            errors.append(f"{label} file does not exist")
        elif file_sha256(candidate) != asset.get("sha256"):
            errors.append(f"{label} sha256 does not match local bytes")
        if asset.get("generated") and asset.get("contains_factual_text"):
            errors.append(f"{label} generated asset cannot contain factual text")
        if asset.get("render_eligible") and (
            asset.get("review_state") != "approved_reusable" or asset.get("rights_state") != "approved"
        ):
            errors.append(f"{label} render eligibility requires visual and rights approval")
    if errors:
        raise FinanceChannelValidationError(errors)
    return dict(payload)


def validate_finance_asset_demand_package(
    demand_manifest: Mapping[str, Any],
    research_manifest: Mapping[str, Any],
    prompt_spine: Mapping[str, Any],
    repository_root: str | Path,
) -> dict[str, Any]:
    """Bind P21 demand, sources, prompts, catalog assets, and evidence hashes."""

    errors: list[str] = []
    for payload in (demand_manifest, research_manifest, prompt_spine):
        try:
            validate_artifact(payload)
        except FinanceChannelValidationError as exc:
            errors.extend(exc.errors)
    if errors:
        raise FinanceChannelValidationError(errors)

    root = Path(repository_root).resolve()
    source_payloads: dict[str, Mapping[str, Any]] = {}
    bindings = demand_manifest.get("source_bindings", {})
    if not isinstance(bindings, Mapping):
        bindings = {}
    for name, binding in bindings.items():
        if not isinstance(binding, Mapping):
            continue
        candidate = (root / str(binding.get("path", ""))).resolve()
        try:
            candidate.relative_to(root)
        except ValueError:
            errors.append(f"source binding {name!r} escapes repository root")
            continue
        if not candidate.is_file():
            errors.append(f"source binding {name!r} does not exist")
            continue
        if file_sha256(candidate) != binding.get("sha256"):
            errors.append(f"source binding {name!r} sha256 is stale")
            continue
        try:
            payload = load_json(candidate)
        except json.JSONDecodeError:
            errors.append(f"source binding {name!r} is not valid JSON")
            continue
        source_payloads[str(name)] = payload
        if binding.get("artifact_hash") and payload.get("artifact_hash") != binding.get("artifact_hash"):
            errors.append(f"source binding {name!r} artifact_hash is stale")

    outputs = demand_manifest.get("planning_outputs", {})
    expected_outputs = {
        "research_resolution": research_manifest,
        "generation_prompt_spine": prompt_spine,
    }
    if isinstance(outputs, Mapping):
        for name, expected_payload in expected_outputs.items():
            binding = outputs.get(name, {})
            if not isinstance(binding, Mapping):
                errors.append(f"planning output {name!r} is missing")
                continue
            candidate = (root / str(binding.get("path", ""))).resolve()
            try:
                candidate.relative_to(root)
            except ValueError:
                errors.append(f"planning output {name!r} escapes repository root")
                continue
            if not candidate.is_file() or file_sha256(candidate) != binding.get("sha256"):
                errors.append(f"planning output {name!r} file hash is stale")
            if expected_payload.get("artifact_hash") != binding.get("artifact_hash"):
                errors.append(f"planning output {name!r} artifact_hash is stale")

    ledger = source_payloads.get("semantic_beat_ledger", {})
    catalog = source_payloads.get("asset_catalog", {})
    numeric = source_payloads.get("numeric_evidence_register", {})
    if catalog:
        try:
            validate_artifact(catalog)
        except FinanceChannelValidationError as exc:
            errors.extend(exc.errors)
    ledger_beats = {
        str(item.get("beat_id")): item
        for item in ledger.get("beats", [])
        if isinstance(item, Mapping)
    }
    demands = {
        str(item.get("beat_id")): item
        for item in demand_manifest.get("demands", [])
        if isinstance(item, Mapping)
    }
    if set(ledger_beats) != set(demands):
        errors.append("asset demand must cover every semantic beat exactly once")

    assets = {
        str(item.get("asset_id")): item
        for item in catalog.get("assets", [])
        if isinstance(item, Mapping)
    }
    surfaces = {
        str(item.get("surface_id")): item
        for item in numeric.get("items", [])
        if isinstance(item, Mapping)
    }
    research_requests = {
        str(item.get("request_id")): item
        for item in research_manifest.get("beat_bindings", [])
        if isinstance(item, Mapping)
    }
    prompts = {
        str(item.get("prompt_id")): item
        for item in prompt_spine.get("prompts", [])
        if isinstance(item, Mapping)
    }
    referenced_prompts: set[str] = set()
    for beat_id, demand in demands.items():
        label = f"beat {beat_id!r}"
        beat = ledger_beats.get(beat_id, {})
        if demand.get("start_word_index") != beat.get("start_word_index") or demand.get("end_word_index") != beat.get("end_word_index"):
            errors.append(f"{label} word binding does not match semantic ledger")
        claim_refs = set(demand.get("claim_refs", []))
        for asset_id in demand.get("selected_asset_ids", []):
            asset = assets.get(str(asset_id))
            if asset is None:
                errors.append(f"{label} references unknown asset {asset_id!r}")
                continue
            candidate = (root / str(asset.get("path", ""))).resolve()
            try:
                candidate.relative_to(root)
            except ValueError:
                errors.append(f"{label} asset {asset_id!r} path escapes repository root")
                continue
            if not candidate.is_file() or file_sha256(candidate) != asset.get("sha256"):
                errors.append(f"{label} asset {asset_id!r} bytes or hash are stale")
            if not asset.get("render_eligible") or asset.get("review_state") != "approved_reusable" or asset.get("rights_state") != "approved":
                errors.append(f"{label} asset {asset_id!r} is not approved reusable")
            if demand.get("representation_mode") not in set(asset.get("representation_modes", [])):
                errors.append(f"{label} asset {asset_id!r} has incompatible representation mode")
            target = demand.get("semantic_target", {})
            if isinstance(target, Mapping) and not set(target.get("required_visual_anchors", [])).issubset(set(asset.get("capability_anchors", []))):
                errors.append(f"{label} asset {asset_id!r} lacks required semantic anchors")
            policy = asset.get("reuse_policy", {})
            if isinstance(policy, Mapping) and policy.get("claim_bound") and claim_refs and not claim_refs.issubset(set(asset.get("claim_refs", []))):
                errors.append(f"{label} asset {asset_id!r} is bound to unrelated claims")
        for surface_id in demand.get("evidence_surface_ids", []):
            surface = surfaces.get(str(surface_id))
            if surface is None:
                errors.append(f"{label} references unknown evidence surface {surface_id!r}")
            elif surface.get("claim_id") not in claim_refs:
                errors.append(f"{label} evidence surface {surface_id!r} is not claim-bound")
        for request_id in demand.get("source_request_ids", []):
            request = research_requests.get(str(request_id))
            if request is None or request.get("beat_id") != beat_id:
                errors.append(f"{label} references a missing or mismatched research request")
        prompt_id = demand.get("prompt_id")
        if prompt_id is not None:
            prompt = prompts.get(str(prompt_id))
            if prompt is None or prompt.get("beat_id") != beat_id:
                errors.append(f"{label} references a missing or mismatched generation prompt")
            else:
                referenced_prompts.add(str(prompt_id))
    if referenced_prompts != set(prompts):
        errors.append("prompt spine must contain exactly the prompts referenced by generation demands")

    if errors:
        raise FinanceChannelValidationError(errors)
    return {
        "status": "valid",
        "episode_id": str(demand_manifest["episode_id"]),
        "beat_count": len(demands),
        "prompt_count": len(prompts),
        "research_binding_count": len(research_requests),
    }


def validate_finance_layered_composition_package(
    composition: Mapping[str, Any],
    repository_root: str | Path,
) -> dict[str, Any]:
    """Verify T3 source hashes and exact word/action timing bindings."""

    errors: list[str] = []
    try:
        validate_artifact(composition)
    except FinanceChannelValidationError as exc:
        errors.extend(exc.errors)
    root = Path(repository_root).resolve()
    loaded: dict[str, Mapping[str, Any]] = {}
    bindings = composition.get("source_bindings", {})
    if not isinstance(bindings, Mapping):
        bindings = {}
    for name, binding in bindings.items():
        if not isinstance(binding, Mapping):
            continue
        candidate = (root / str(binding.get("path", ""))).resolve()
        try:
            candidate.relative_to(root)
        except ValueError:
            errors.append(f"layered source binding {name!r} escapes repository root")
            continue
        if not candidate.is_file() or file_sha256(candidate) != binding.get("sha256"):
            errors.append(f"layered source binding {name!r} file hash is stale")
            continue
        try:
            payload = load_json(candidate)
        except json.JSONDecodeError:
            errors.append(f"layered source binding {name!r} is not valid JSON")
            continue
        loaded[str(name)] = payload
        if binding.get("artifact_hash") and payload.get("artifact_hash") != binding.get("artifact_hash"):
            errors.append(f"layered source binding {name!r} artifact_hash is stale")
    ledger = loaded.get("semantic_beat_ledger", {})
    demand = loaded.get("asset_demand", {})
    word_payload = loaded.get("word_timing", {})
    beats = {str(item.get("beat_id")): item for item in ledger.get("beats", []) if isinstance(item, Mapping)}
    demands = {str(item.get("beat_id")): item for item in demand.get("demands", []) if isinstance(item, Mapping)}
    words = list(word_payload.get("words", [])) if isinstance(word_payload, Mapping) else []
    cues = {str(item.get("beat_id")): item for item in composition.get("cues", []) if isinstance(item, Mapping)}
    if set(cues) != set(beats) or set(cues) != set(demands):
        errors.append("layered composition, semantic ledger, and asset demand beat IDs must match")
    for beat_id, cue in cues.items():
        beat = beats.get(beat_id, {})
        asset_demand = demands.get(beat_id, {})
        label = f"layered cue {beat_id!r}"
        if cue.get("strategy") != asset_demand.get("strategy"):
            errors.append(f"{label} strategy does not match asset demand")
        if set(cue.get("evidence_surface_ids", [])) != set(asset_demand.get("evidence_surface_ids", [])):
            errors.append(f"{label} evidence surfaces do not match asset demand")
        expected_words = {"start_index": beat.get("start_word_index"), "end_index": beat.get("end_word_index")}
        if cue.get("word_range") != expected_words:
            errors.append(f"{label} word range does not match semantic ledger")
        for layer_index, layer in enumerate(cue.get("layers", [])):
            if not isinstance(layer, Mapping):
                continue
            action_range = layer.get("action_word_range", {})
            action_index = int(action_range.get("start_index", -1)) if isinstance(action_range, Mapping) else -1
            if action_index < 0 or action_index >= len(words):
                errors.append(f"{label}.layers[{layer_index}] action word does not exist")
                continue
            expected_time = {
                "start_s": words[action_index].get("start_s"),
                "end_s": words[action_index].get("end_s"),
            }
            if layer.get("action_time_range") != expected_time:
                errors.append(f"{label}.layers[{layer_index}] action time is not word-exact")
    if errors:
        raise FinanceChannelValidationError(errors)
    return {
        "status": "valid",
        "episode_id": str(composition["episode_id"]),
        "cue_count": len(cues),
        "word_count": len(words),
    }


def validate_semantic_visual_package(
    cue_sheet: Mapping[str, Any],
    resolution_manifest: Mapping[str, Any],
    asset_catalog: Mapping[str, Any],
    numeric_register: Mapping[str, Any],
    project_root: str | Path,
) -> dict[str, Any]:
    """Validate that every visual choice is explicit, compatible, and auditable.

    This is intentionally stricter than the component validators: it binds a
    concrete cue to its selected asset(s), evidence surfaces, and reuse policy.
    """

    errors: list[str] = []
    for payload in (cue_sheet, resolution_manifest, numeric_register):
        try:
            validate_artifact(payload)
        except FinanceChannelValidationError as exc:
            errors.extend(exc.errors)
    try:
        validate_asset_catalog(asset_catalog, project_root)
    except FinanceChannelValidationError as exc:
        errors.extend(exc.errors)
    if errors:
        raise FinanceChannelValidationError(errors)

    if cue_sheet.get("schema_version") != "finance_visual_cue_sheet.v2":
        errors.append("semantic package requires finance_visual_cue_sheet.v2")
    if asset_catalog.get("schema_version") != "finance_asset_catalog.v2":
        errors.append("semantic package requires finance_asset_catalog.v2")
    if cue_sheet.get("episode_id") != resolution_manifest.get("episode_id") or cue_sheet.get("episode_id") != numeric_register.get("episode_id"):
        errors.append("semantic package episode_id values must match")
    if resolution_manifest.get("cue_sheet_hash") != cue_sheet.get("artifact_hash"):
        errors.append("resolution manifest cue_sheet_hash does not match cue sheet")
    if resolution_manifest.get("asset_catalog_hash") != asset_catalog.get("artifact_hash"):
        errors.append("resolution manifest asset_catalog_hash does not match asset catalog")
    if resolution_manifest.get("numeric_evidence_register_hash") != numeric_register.get("artifact_hash"):
        errors.append("resolution manifest numeric_evidence_register_hash does not match numeric register")

    cues = {str(item.get("cue_id")): item for item in cue_sheet.get("cues", []) if isinstance(item, Mapping)}
    resolutions = {str(item.get("cue_id")): item for item in resolution_manifest.get("resolutions", []) if isinstance(item, Mapping)}
    assets = {str(item.get("asset_id")): item for item in asset_catalog.get("assets", []) if isinstance(item, Mapping)}
    surfaces = {str(item.get("surface_id")): item for item in numeric_register.get("items", []) if isinstance(item, Mapping)}
    if set(cues) != set(resolutions):
        errors.append("resolution manifest must contain exactly one resolution for every cue")

    previous_asset_ids: set[str] = set()
    usage: dict[str, int] = {}
    for cue_id, cue in cues.items():
        resolution = resolutions.get(cue_id)
        if not isinstance(resolution, Mapping):
            continue
        label = f"cue {cue_id!r}"
        if resolution.get("call_cue_id") != cue.get("call_cue_id"):
            errors.append(f"{label} resolution call_cue_id does not match")
        if resolution.get("representation_mode") != cue.get("representation_mode"):
            errors.append(f"{label} resolution representation_mode does not match")
        selected = [str(asset_id) for asset_id in resolution.get("selected_asset_ids", [])]
        target = cue.get("semantic_target", {})
        required = set(target.get("required_visual_anchors", [])) if isinstance(target, Mapping) else set()
        prohibited = set(target.get("prohibited_implications", [])) if isinstance(target, Mapping) else set()
        combined_anchors: set[str] = set()
        for asset_id in selected:
            asset = assets.get(asset_id)
            if asset is None:
                errors.append(f"{label} resolves unknown asset {asset_id!r}")
                continue
            combined_anchors.update(str(anchor) for anchor in asset.get("capability_anchors", []))
            if cue.get("representation_mode") not in set(asset.get("representation_modes", [])):
                errors.append(f"{label} asset {asset_id!r} has incompatible representation mode")
            if prohibited.intersection(set(asset.get("prohibited_implications", []))):
                errors.append(f"{label} asset {asset_id!r} carries a prohibited implication")
            policy = asset.get("reuse_policy", {})
            if isinstance(policy, Mapping) and policy.get("claim_bound") and not set(cue.get("claim_refs", [])).issubset(set(asset.get("claim_refs", []))):
                errors.append(f"{label} claim-bound asset {asset_id!r} serves an unrelated claim")
            if resolution_manifest.get("render_eligible") and not asset.get("render_eligible"):
                errors.append(f"{label} render-eligible manifest references unpromoted asset {asset_id!r}")
        if resolution.get("status") == "resolved" and not required.issubset(combined_anchors):
            errors.append(f"{label} selected assets do not satisfy required visual anchors")

        cue_surfaces = {str(surface_id) for surface_id in cue.get("evidence_surface_ids", [])}
        resolution_surfaces = {str(surface_id) for surface_id in resolution.get("evidence_surface_ids", [])}
        if cue_surfaces != resolution_surfaces:
            errors.append(f"{label} resolution evidence surfaces do not match cue")
        for surface_id in cue_surfaces:
            surface = surfaces.get(surface_id)
            if surface is None:
                errors.append(f"{label} references unknown numeric evidence surface {surface_id!r}")
            elif surface.get("claim_id") not in set(cue.get("claim_refs", [])):
                errors.append(f"{label} numeric evidence surface {surface_id!r} is not bound to a cue claim")

        policy_errors = validate_reuse(resolution, assets, Counter(usage), previous_asset_ids=previous_asset_ids)
        errors.extend(f"{label} {message}" for message in policy_errors)
        for asset_id in selected:
            usage[asset_id] = usage.get(asset_id, 0) + 1
        previous_asset_ids = set(selected)

    if errors:
        raise FinanceChannelValidationError(errors)
    return {
        "status": "valid",
        "episode_id": str(cue_sheet["episode_id"]),
        "cue_count": len(cues),
        "unresolved_count": sum(item.get("status") == "unresolved" for item in resolutions.values()),
    }


def score_topic(candidate: Mapping[str, float]) -> dict[str, Any]:
    missing = sorted((set(TOPIC_WEIGHTS) | set(TOPIC_PENALTIES)) - set(candidate))
    if missing:
        raise FinanceChannelValidationError([f"topic candidate missing: {', '.join(missing)}"])
    invalid = sorted(key for key, value in candidate.items() if key in TOPIC_WEIGHTS | TOPIC_PENALTIES and not 0 <= float(value) <= 1)
    if invalid:
        raise FinanceChannelValidationError([f"topic values outside 0..1: {', '.join(invalid)}"])
    positive = sum(float(candidate[key]) * weight for key, weight in TOPIC_WEIGHTS.items())
    penalty = sum(float(candidate[key]) * weight for key, weight in TOPIC_PENALTIES.items())
    return {
        "score": round(max(0.0, min(1.0, positive - penalty)), 4),
        "positive": round(positive, 4),
        "penalty": round(penalty, 4),
        "weights": {**TOPIC_WEIGHTS, **{key: -value for key, value in TOPIC_PENALTIES.items()}},
    }


def select_asset_strategy(available_tiers: Iterable[int]) -> int:
    tiers = sorted({int(tier) for tier in available_tiers if 1 <= int(tier) <= 4})
    if not tiers:
        raise FinanceChannelValidationError(["no viable asset-resolution tier"])
    return tiers[0]


def validate_project(project_root: str | Path, *, include_pilots: bool = False) -> dict[str, Any]:
    root = Path(project_root).resolve()
    required = {
        "channel-profile.v1.json": "finance_channel_profile.v1",
        "programming-schedule.v1.json": "finance_schedule.v1",
        "reference-learnings.v1.json": "finance_reference_learnings.v1",
        "asset-catalog.v1.json": "finance_asset_catalog.v1",
    }
    errors: list[str] = []
    validated: list[str] = []
    for relative, version in required.items():
        path = root / relative
        if not path.is_file():
            errors.append(f"missing {relative}")
            continue
        try:
            payload = load_json(path)
            if payload.get("schema_version") != version:
                errors.append(f"{relative} has wrong schema_version")
            elif version == "finance_asset_catalog.v1":
                validate_asset_catalog(payload, root)
            else:
                validate_artifact(payload)
            validated.append(relative)
        except (json.JSONDecodeError, FinanceChannelValidationError) as exc:
            errors.append(f"{relative}: {exc}")
    if include_pilots:
        brief_paths = sorted((root / "pilots").glob("*/episode-brief.v1.json"))
        ledger_paths = sorted((root / "pilots").glob("*/claim-ledger.v1.json"))
        if len(brief_paths) != 3 or len(ledger_paths) != 3:
            errors.append("project must contain exactly three pilot briefs and ledgers")
        for path in [*brief_paths, *ledger_paths]:
            try:
                validate_artifact(load_json(path))
                validated.append(path.relative_to(root).as_posix())
            except (json.JSONDecodeError, FinanceChannelValidationError) as exc:
                errors.append(f"{path.relative_to(root).as_posix()}: {exc}")
    if errors:
        raise FinanceChannelValidationError(errors)
    return {"project_root": str(root), "validated": validated, "status": "valid"}


__all__ = [
    "FinanceChannelValidationError",
    "TOPIC_PENALTIES",
    "TOPIC_WEIGHTS",
    "canonical_sha256",
    "file_sha256",
    "load_json",
    "score_topic",
    "select_asset_strategy",
    "validate_artifact",
    "validate_asset_catalog",
    "validate_finance_asset_demand_package",
    "validate_finance_layered_composition_package",
    "validate_semantic_visual_package",
    "validate_project",
    "with_artifact_hash",
]
