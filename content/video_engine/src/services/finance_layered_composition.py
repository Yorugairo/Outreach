"""Sentence-native layered composition planning for finance explainers.

This service produces a pre-render contract. It does not claim that planned
trace cuts, generated plates, source documents, or deterministic surfaces
already exist. Every meaningful layer carries an exact canonical word and time
range so the renderer can schedule the action independently of camera motion.
"""

from __future__ import annotations

from collections import Counter
from typing import Any, Mapping, Sequence

from content.video_engine.src.services.finance_channel import with_artifact_hash


def _layer(
    *,
    beat: Mapping[str, Any],
    words: Sequence[Mapping[str, Any]],
    role: str,
    source_kind: str,
    source_ref: str,
    z_index: int,
    action: str,
    action_word_index: int,
    state: str,
) -> dict[str, Any]:
    start_word = int(beat["start_word_index"])
    end_word = int(beat["end_word_index"])
    action_word_index = max(start_word, min(end_word, int(action_word_index)))
    return {
        "layer_id": f"{beat['beat_id']}-{role}-{z_index:02d}",
        "role": role,
        "source_kind": source_kind,
        "source_ref": source_ref,
        "z_index": z_index,
        "word_range": {"start_index": start_word, "end_index": end_word},
        "time_range": {"start_s": float(beat["start_s"]), "end_s": float(beat["end_s"])},
        "action_word_range": {"start_index": action_word_index, "end_index": action_word_index},
        "action_time_range": {
            "start_s": float(words[action_word_index]["start_s"]),
            "end_s": float(words[action_word_index]["end_s"]),
        },
        "action": action,
        "state": state,
    }


def _semantic_sources(demand: Mapping[str, Any]) -> tuple[dict[str, str], dict[str, str], dict[str, str]]:
    strategy = str(demand["strategy"])
    beat_id = str(demand["beat_id"])
    selected = [str(item) for item in demand.get("selected_asset_ids", [])]
    prompt_id = str(demand.get("prompt_id") or "")
    source_requests = [str(item) for item in demand.get("source_request_ids", [])]
    if strategy == "original_generation_request":
        return (
            {"kind": "planned_generation", "ref": f"{prompt_id}#background", "state": "planned_generation"},
            {"kind": "planned_generation", "ref": f"{prompt_id}#midground", "state": "planned_generation"},
            {"kind": "planned_generation", "ref": f"{prompt_id}#foreground", "state": "planned_generation"},
        )
    if strategy == "exact_asset":
        asset_id = selected[0]
        return (
            {"kind": "planned_trace_cut", "ref": f"{asset_id}#background", "state": "planned_trace_cut"},
            {"kind": "planned_trace_cut", "ref": f"{asset_id}#midground", "state": "planned_trace_cut"},
            {"kind": "planned_trace_cut", "ref": f"{asset_id}#foreground", "state": "planned_trace_cut"},
        )
    if strategy == "component_composition":
        return (
            {"kind": "local_primitive", "ref": "local:finance-paper-world", "state": "local_primitive"},
            {"kind": "local_primitive", "ref": f"local:finance-actor:{beat_id}", "state": "local_primitive"},
            {"kind": "existing_asset", "ref": selected[0], "state": "approved_existing"},
        )
    if strategy == "deterministic_surface":
        return (
            {"kind": "local_primitive", "ref": "local:finance-evidence-world", "state": "local_primitive"},
            {"kind": "local_primitive", "ref": f"local:finance-analyst:{beat_id}", "state": "local_primitive"},
            {"kind": "deterministic_surface", "ref": f"deterministic:mechanism:{beat_id}", "state": "planned_deterministic"},
        )
    request = source_requests[0]
    return (
        {"kind": "local_primitive", "ref": "local:source-desk-world", "state": "local_primitive"},
        {"kind": "source_retrieval", "ref": f"{request}#document", "state": "pending_source"},
        {"kind": "local_primitive", "ref": f"local:source-callout:{beat_id}", "state": "local_primitive"},
    )


def compile_finance_layered_composition(
    *,
    semantic_ledger: Mapping[str, Any],
    asset_demand: Mapping[str, Any],
    word_timings: Mapping[str, Any],
    source_bindings: Mapping[str, Any],
) -> dict[str, Any]:
    """Compile one independently timed layered recipe per semantic beat."""

    words = list(word_timings.get("words", []))
    if len(words) != int(semantic_ledger.get("timing", {}).get("word_count", 0)):
        raise ValueError("word timing count does not match the semantic ledger")
    demand_index = {str(item["beat_id"]): item for item in asset_demand.get("demands", [])}
    cues: list[dict[str, Any]] = []
    role_counts: Counter[str] = Counter()
    beats = list(semantic_ledger.get("beats", []))
    for index, beat in enumerate(beats):
        beat_id = str(beat["beat_id"])
        demand = demand_index.get(beat_id)
        if demand is None:
            raise ValueError(f"missing asset demand for {beat_id}")
        causal_word = int(beat["causal_verb"]["word_index"])
        start_word = int(beat["start_word_index"])
        end_word = int(beat["end_word_index"])
        verb = str(beat["causal_verb"]["lemma"])
        world_source, subject_source, relationship_source = _semantic_sources(demand)
        relationship_role = (
            "prop" if demand.get("representation_mode") == "declared_metaphor" else "mechanism"
        )
        layers = [
            _layer(
                beat=beat, words=words, role="world", source_kind=world_source["kind"],
                source_ref=world_source["ref"], z_index=0, action="present_from_first_frame",
                action_word_index=start_word, state=world_source["state"],
            ),
            _layer(
                beat=beat, words=words, role="subject", source_kind=subject_source["kind"],
                source_ref=subject_source["ref"], z_index=4, action=f"subject_{verb}",
                action_word_index=causal_word, state=subject_source["state"],
            ),
            _layer(
                beat=beat, words=words, role=relationship_role, source_kind=relationship_source["kind"],
                source_ref=relationship_source["ref"], z_index=6,
                action=f"{relationship_role}_{verb}_relationship", action_word_index=causal_word,
                state=relationship_source["state"],
            ),
        ]
        for surface_offset, surface_id in enumerate(demand.get("evidence_surface_ids", [])):
            layers.append(
                _layer(
                    beat=beat, words=words, role="evidence", source_kind="deterministic_surface",
                    source_ref=f"evidence:{surface_id}", z_index=8 + surface_offset,
                    action="evidence_reveal_after_spoken_claim", action_word_index=causal_word,
                    state="planned_deterministic",
                )
            )
        if demand.get("strategy") == "source_retrieval_request":
            request_id = str(demand["source_request_ids"][0])
            layers.append(
                _layer(
                    beat=beat, words=words, role="evidence", source_kind="source_retrieval",
                    source_ref=f"{request_id}#locator-callout", z_index=8,
                    action="evidence_locator_reveal", action_word_index=causal_word,
                    state="pending_source",
                )
            )
        next_chapter = index + 1 < len(beats) and beats[index + 1]["chapter_id"] != beat["chapter_id"]
        transition_kind = (
            "paper_wipe" if next_chapter else "match_cut" if beat["visual_job"]["kind"] == "transform" else "hard_cut"
        )
        layers.append(
            _layer(
                beat=beat, words=words, role="transition", source_kind="local_primitive",
                source_ref=f"transition:{transition_kind}", z_index=20,
                action=f"{transition_kind}_on_semantic_boundary", action_word_index=end_word,
                state="local_primitive",
            )
        )
        role_counts.update(str(layer["role"]) for layer in layers)
        cues.append({
            "cue_id": f"finance-layered-{beat_id}",
            "beat_id": beat_id,
            "chapter_id": str(beat["chapter_id"]),
            "word_range": {"start_index": start_word, "end_index": end_word},
            "time_range": {"start_s": float(beat["start_s"]), "end_s": float(beat["end_s"])},
            "excerpt": str(beat["excerpt"]),
            "visual_job": str(beat["visual_job"]["kind"]),
            "strategy": str(demand["strategy"]),
            "evidence_surface_ids": list(demand.get("evidence_surface_ids", [])),
            "camera": "locked_support_only",
            "layers": layers,
            "transition_out": transition_kind,
        })

    non_evidence = [cue for cue in cues if not any(layer["role"] == "evidence" for layer in cue["layers"])]
    three_plus = [cue for cue in non_evidence if len([layer for layer in cue["layers"] if layer["role"] != "transition"]) >= 3]
    ratio = 1.0 if not non_evidence else round(len(three_plus) / len(non_evidence), 6)
    return with_artifact_hash({
        "schema_version": "finance_layered_composition.v1",
        "episode_id": str(semantic_ledger["episode_id"]),
        "source_bindings": dict(source_bindings),
        "timing": {
            "word_count": len(words),
            "duration_s": float(semantic_ledger["timing"]["duration_s"]),
            "fps": 24,
            "paper_motion_fps": 12,
        },
        "summary": {
            "cue_count": len(cues),
            "role_counts": dict(sorted(role_counts.items())),
            "non_evidence_cue_count": len(non_evidence),
            "non_evidence_three_plus_layer_count": len(three_plus),
            "non_evidence_three_plus_layer_ratio": ratio,
            "camera_only_cue_count": 0,
        },
        "cues": cues,
        "review_state": "draft",
        "render_eligible": False,
    })


__all__ = ["compile_finance_layered_composition"]
