"""Deterministic P32 coverage baseline for current-bubble-mechanism.

This module inventories the canonical cue schedule, approved source surfaces,
and composition-approved world plates.  It deliberately does not crop,
generate, promote, or bind a visual.  Its output is a Gate-A review artifact:
every candidate remains a recommendation for an editor to accept or reject.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping, Sequence
import copy
import hashlib
import html
import json
import os
from pathlib import Path
import re
from typing import Any

from jsonschema import Draft202012Validator

from .semantic_evidence_binding import canonical_sha256, file_sha256


COVERAGE_VERSION = "full_episode_evidence_coverage.v1"
COMPILER_VERSION = "p32-full-episode-evidence-coverage-1.0"
WORLD_PLATE_KINDS = frozenset({"hero_plate", "generated_hero", "world_board", "mechanism"})
MAX_WORLD_HOLD_SECONDS = 20.0
MAX_EVIDENCE_CANDIDATES = 3
_TOKEN = re.compile(r"[a-z0-9]+")
_STOP_WORDS = frozenset(
    {
        "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "in", "into", "is", "it",
        "of", "on", "or", "that", "the", "their", "this", "to", "with", "will", "can", "not", "more",
    }
)
_REQUIRED_INPUTS = {
    "cue_sheet": "edit/word-timed-v1/finance-visual-cue-sheet.v1.json",
    "beat_plan": "edit/word-timed-v1/editorial-beat-plan.v1.json",
    "asset_map": "edit/word-timed-v1/asset-map.v1.json",
    "resolution_map": "edit/semantic-v2/remotion-semantic-resolution-map.v3.json",
    "composition_spine": "edit/semantic-v2/full-episode-composition-spine.v1.json",
    "snapshot": "edit/production-console/current-bubble.snapshot.v1.json",
    "claim_ledger": "claim-ledger.v1.json",
    "teacher_approval": "review/teacher-stamped-sheets/teacher-stamped-decks-approval.v1.json",
}


class CoverageCompilationError(ValueError):
    """Raised when a coverage input is absent, stale, or internally inconsistent."""


def _read_json(path: Path, label: str) -> dict[str, Any]:
    if not path.is_file():
        raise CoverageCompilationError(f"missing {label}: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CoverageCompilationError(f"invalid {label}: {path}") from exc
    if not isinstance(payload, dict):
        raise CoverageCompilationError(f"{label} must be a JSON object")
    return payload


def _validate_artifact_hash(payload: Mapping[str, Any], label: str) -> str:
    declared = str(payload.get("artifact_hash") or "").lower()
    if not re.fullmatch(r"[0-9a-f]{64}", declared):
        raise CoverageCompilationError(f"{label} is missing artifact_hash")
    if declared != canonical_sha256(payload):
        raise CoverageCompilationError(f"{label} artifact_hash is stale")
    return declared


def _tokenize(*values: Any) -> set[str]:
    text = " ".join(str(value or "").lower() for value in values)
    return {
        token
        for token in _TOKEN.findall(text)
        if (len(token) > 2 or token.isdigit()) and token not in _STOP_WORDS
    }


def _repo_root(project_root: Path) -> Path:
    for candidate in (project_root, *project_root.parents):
        if (candidate / "content" / "video_engine").is_dir():
            return candidate
    raise CoverageCompilationError("unable to resolve repository root from project path")


def _safe_repo_file(repo_root: Path, relative_path: str, label: str) -> Path:
    roots = (
        repo_root,
        repo_root / "content" / "video_engine",
        repo_root / "content" / "video_engine" / "projects" / "systems-and-blowups",
        repo_root / "content" / "video_engine" / "projects" / "systems-and-blowups" / "sources" / "decks",
    )
    for root in roots:
        candidate = (root / relative_path).resolve()
        try:
            candidate.relative_to(root.resolve())
        except ValueError:
            continue
        if candidate.is_file():
            return candidate
    raise CoverageCompilationError(f"missing or unsafe {label} media: {relative_path}")


def _world_library(project_root: Path, repo_root: Path, asset_map: Mapping[str, Any]) -> list[dict[str, Any]]:
    assets = asset_map.get("assets")
    if not isinstance(assets, Mapping):
        raise CoverageCompilationError("asset_map.assets must be an object")
    library: list[dict[str, Any]] = []
    for asset_id, raw in sorted(assets.items()):
        if not isinstance(raw, Mapping) or raw.get("kind") not in WORLD_PLATE_KINDS or raw.get("render_eligible") is not True:
            continue
        path = _safe_repo_file(repo_root, str(raw.get("path") or ""), f"world plate {asset_id}")
        expected = str(raw.get("sha256") or "").lower()
        if file_sha256(path) != expected:
            raise CoverageCompilationError(f"world plate {asset_id} hash mismatch")
        library.append(
            {
                "asset_id": str(asset_id),
                "kind": str(raw["kind"]),
                "path": str(raw["path"]),
                "sha256": expected,
                "source": "asset_map",
                "claim_refs": sorted(str(value) for value in raw.get("claim_refs") or []),
                "semantic_tags": sorted(str(value) for value in raw.get("semantic_tags") or []),
                "composition_approval": "mapped_render_eligible",
                "range_s": None,
            }
        )

    manifests = sorted(project_root.glob("assets/quarantine/sentence-native-wave-*/wave-*-review-manifest.v1.json"))
    for manifest_path in manifests:
        manifest = _read_json(manifest_path, f"sentence-native manifest {manifest_path.name}")
        if manifest.get("review_state") != "operator_approved_for_composition":
            continue
        accepted = manifest.get("accepted_candidates")
        if not isinstance(accepted, list):
            raise CoverageCompilationError(f"{manifest_path.name}.accepted_candidates must be a list")
        for raw in accepted:
            if not isinstance(raw, Mapping):
                raise CoverageCompilationError(f"{manifest_path.name} contains a malformed accepted candidate")
            relative_path = str(raw.get("path") or "")
            path = _safe_repo_file(repo_root, relative_path, f"sentence-native plate {raw.get('filename')}")
            expected = str(raw.get("sha256") or "").lower()
            if file_sha256(path) != expected:
                raise CoverageCompilationError(f"sentence-native plate {raw.get('filename')} hash mismatch")
            start_s, end_s = float(raw.get("start_s", -1)), float(raw.get("end_s", -1))
            if start_s < 0 or end_s <= start_s:
                raise CoverageCompilationError(f"sentence-native plate {raw.get('filename')} has invalid range")
            filename = Path(relative_path).stem
            library.append(
                {
                    "asset_id": f"sentence-native-{filename}",
                    "kind": "sentence_native_plate",
                    "path": relative_path,
                    "sha256": expected,
                    "source": "sentence_native_manifest",
                    "claim_refs": [],
                    "semantic_tags": sorted(_tokenize(raw.get("semantic_job"), raw.get("narration_excerpt"))),
                    "composition_approval": "operator_approved_for_composition",
                    "range_s": {"start": round(start_s, 3), "end": round(end_s, 3)},
                    "semantic_job": str(raw.get("semantic_job") or ""),
                    "narration_excerpt": str(raw.get("narration_excerpt") or ""),
                    "manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
                }
            )
    ids = [str(item["asset_id"]) for item in library]
    if len(ids) != len(set(ids)):
        raise CoverageCompilationError("world plate library has duplicate asset ids")
    return sorted(library, key=lambda item: str(item["asset_id"]))


def _source_surfaces(snapshot: Mapping[str, Any], project_root: Path, repo_root: Path) -> tuple[list[dict[str, Any]], dict[str, str]]:
    raw_assets = snapshot.get("assets")
    if not isinstance(raw_assets, list):
        raise CoverageCompilationError("production snapshot assets must be a list")
    surfaces: list[dict[str, Any]] = []
    for raw in raw_assets:
        if not isinstance(raw, Mapping) or raw.get("evidence_eligible") is not True:
            continue
        relative_path = str(raw.get("path") or "")
        path = _safe_repo_file(repo_root, relative_path, f"source surface {raw.get('asset_id')}")
        expected = str(raw.get("sha256") or "").lower()
        if file_sha256(path) != expected:
            raise CoverageCompilationError(f"source surface {raw.get('asset_id')} hash mismatch")
        surfaces.append(
            {
                "asset_id": str(raw.get("asset_id") or ""),
                "deck_id": str(raw.get("deck_id") or ""),
                "slide_number": raw.get("slide_number"),
                "label": str(raw.get("label") or ""),
                "what_it_is": str(raw.get("what_it_is") or ""),
                "path": relative_path,
                "sha256": expected,
                "approval_scope": str(raw.get("approval_scope") or ""),
                "context_status": str(raw.get("context_status") or ""),
                "claim_refs": sorted(str(value) for value in raw.get("claim_refs") or []),
                "cue_refs": sorted(str(value) for value in raw.get("cue_refs") or []),
                "evidence_state": "production_ready",
            }
        )
    context_hashes: dict[str, str] = {}
    deck_root = repo_root / "content" / "video_engine" / "projects" / "systems-and-blowups" / "sources" / "decks"
    for context_path in sorted(deck_root.glob("*/semantic-assets/asset-context.json")):
        context = _read_json(context_path, f"deck context {context_path.parent.parent.name}")
        deck_id = str(context.get("deck_id") or context_path.parents[1].name)
        context_hashes[f"deck_context_{deck_id}"] = _validate_artifact_hash(context, f"deck context {deck_id}")
        for raw in context.get("assets") or []:
            if not isinstance(raw, Mapping):
                raise CoverageCompilationError(f"deck context {deck_id} contains malformed asset")
            relative_path = str(raw.get("path") or "")
            path = _safe_repo_file(repo_root, relative_path, f"context crop {raw.get('asset_id')}")
            expected = str(raw.get("sha256") or "").lower()
            if file_sha256(path) != expected:
                raise CoverageCompilationError(f"context crop {raw.get('asset_id')} hash mismatch")
            crop_context = raw.get("context") if isinstance(raw.get("context"), Mapping) else {}
            surfaces.append(
                {
                    "asset_id": str(raw.get("asset_id") or ""),
                    "deck_id": str(raw.get("deck_id") or deck_id),
                    "slide_number": raw.get("slide_number"),
                    "label": str(raw.get("asset_id") or ""),
                    "what_it_is": str(crop_context.get("what_it_is") or ""),
                    "path": relative_path,
                    "sha256": expected,
                    "approval_scope": "source_context_review_only",
                    "context_status": str(crop_context.get("context_status") or "review_only"),
                    "claim_refs": sorted(str(value) for value in crop_context.get("claim_refs") or []),
                    "cue_refs": sorted(str(value) for value in crop_context.get("cue_refs") or []),
                    "evidence_state": "context_crop_review_only",
                }
            )
    if not surfaces:
        raise CoverageCompilationError("production snapshot has no approved evidence surfaces")
    ids = [str(item["asset_id"]) for item in surfaces]
    if len(ids) != len(set(ids)):
        raise CoverageCompilationError("source surface inventory has duplicate asset ids")
    return sorted(surfaces, key=lambda item: str(item["asset_id"])), context_hashes


def _scene_for_cue(cue_id: str, scenes: Sequence[Mapping[str, Any]]) -> Mapping[str, Any]:
    for scene in scenes:
        if cue_id in {str(value) for value in scene.get("cue_refs") or []}:
            return scene
    raise CoverageCompilationError(f"cue {cue_id} is not assigned to an episode scene")


def _resolution_by_cue(resolution_map: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for raw in resolution_map.get("cues") or []:
        if not isinstance(raw, Mapping):
            raise CoverageCompilationError("resolution_map.cues contains malformed entry")
        cue_id = str(raw.get("cue_id") or "")
        if not cue_id or cue_id in result:
            raise CoverageCompilationError(f"resolution map has duplicate or missing cue_id: {cue_id!r}")
        result[cue_id] = dict(raw)
    return result


def _claim_tokens(claim_refs: Sequence[str], claims_by_id: Mapping[str, Mapping[str, Any]]) -> set[str]:
    values: list[str] = []
    for claim_id in claim_refs:
        claim = claims_by_id.get(claim_id)
        if claim is None:
            raise CoverageCompilationError(f"cue references unknown claim {claim_id}")
        values.extend([str(claim.get("text") or ""), str(claim.get("qualifier") or "")])
    return _tokenize(*values)


def _rank_source_surfaces(cue: Mapping[str, Any], claim_tokens: set[str], surfaces: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    cue_tokens = _tokenize(cue.get("excerpt"))
    ranked: list[dict[str, Any]] = []
    for surface in surfaces:
        direct_cue = str(cue["cue_id"]) in set(surface.get("cue_refs") or [])
        direct_claim = bool(set(cue.get("claim_refs") or []) & set(surface.get("claim_refs") or []))
        surface_tokens = _tokenize(surface.get("label"), surface.get("what_it_is"))
        direct_overlap = sorted(cue_tokens & surface_tokens)
        contextual_overlap = sorted((claim_tokens & surface_tokens) - set(direct_overlap))
        score = (60 if direct_cue else 0) + (45 if direct_claim else 0) + min(40, len(direct_overlap) * 10) + min(10, len(contextual_overlap) * 2)
        if not direct_cue and not direct_claim and len(direct_overlap) < 2:
            continue
        ranked.append(
            {
                "asset_id": surface["asset_id"],
                "deck_id": surface["deck_id"],
                "slide_number": surface["slide_number"],
                "sha256": surface["sha256"],
                "path": surface["path"],
                "score": score,
                "match_terms": direct_overlap,
                "match_basis": "direct_cue_or_claim" if direct_cue or direct_claim else "lexical_context_only",
                "action": "review_crop_or_small_source_surface",
                "evidence_state": surface["evidence_state"],
            }
        )
    return sorted(ranked, key=lambda item: (-int(item["score"]), str(item["asset_id"])))[:MAX_EVIDENCE_CANDIDATES]


def _contiguous_segments(cues: Sequence[Mapping[str, Any]], resolution: Mapping[str, Mapping[str, Any]]) -> list[dict[str, Any]]:
    segments: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for cue in cues:
        resolved = resolution[str(cue["cue_id"])]
        asset_id = str(resolved.get("asset_id") or "")
        if not asset_id:
            raise CoverageCompilationError(f"resolution map lacks asset_id for {cue['cue_id']}")
        start_s, end_s = float(cue["start_s"]), float(cue["end_s"])
        if current and current["asset_id"] == asset_id and abs(float(current["end_s"]) - start_s) < 0.001:
            current["end_s"] = round(end_s, 3)
            current["cue_ids"].append(str(cue["cue_id"]))
            continue
        if current:
            segments.append(current)
        current = {"asset_id": asset_id, "start_s": round(start_s, 3), "end_s": round(end_s, 3), "cue_ids": [str(cue["cue_id"])]}
    if current:
        segments.append(current)
    for segment in segments:
        segment["duration_s"] = round(float(segment["end_s"]) - float(segment["start_s"]), 3)
    return segments


def _world_turns(
    segments: Sequence[Mapping[str, Any]],
    scenes: Sequence[Mapping[str, Any]],
    library: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    by_id = {str(item["asset_id"]): item for item in library}
    sentence_native = [item for item in library if item.get("source") == "sentence_native_manifest"]
    turns: list[dict[str, Any]] = []
    for segment in segments:
        if float(segment["duration_s"]) <= MAX_WORLD_HOLD_SECONDS:
            continue
        scene = _scene_for_cue(str(segment["cue_ids"][0]), scenes)
        scene_pool = [by_id[asset_id] for asset_id in scene.get("asset_ids") or [] if asset_id in by_id and asset_id != segment["asset_id"]]
        turn_at = float(segment["start_s"]) + MAX_WORLD_HOLD_SECONDS
        ordinal = 0
        while turn_at < float(segment["end_s"]) - 0.001:
            exact = [
                item
                for item in sentence_native
                if float(item["range_s"]["start"]) <= turn_at < float(item["range_s"]["end"])
            ]
            nearby = [
                item
                for item in sentence_native
                if abs(float(item["range_s"]["start"]) - turn_at) <= 10.0
            ]
            if exact or nearby:
                chosen = sorted(exact or nearby, key=lambda item: (abs(float(item["range_s"]["start"]) - turn_at), str(item["asset_id"])))[0]
                state, basis = "sentence_native_candidate", "exact_range" if exact else "nearby_causal_turn"
            elif scene_pool:
                chosen = scene_pool[ordinal % len(scene_pool)]
                state, basis = "scene_authority_candidate", "canonical_scene_asset_pool"
            else:
                chosen, state, basis = None, "new_world_art_gap", "no_existing_composition_candidate"
            turns.append(
                {
                    "turn_id": f"cadence-{segment['cue_ids'][0]}-{ordinal + 1}",
                    "scene_id": str(scene["scene_id"]),
                    "parent_asset_id": str(segment["asset_id"]),
                    "at_s": round(turn_at, 3),
                    "state": state,
                    "match_basis": basis,
                    "candidate_world_asset": None
                    if chosen is None
                    else {"asset_id": chosen["asset_id"], "sha256": chosen["sha256"], "path": chosen["path"]},
                    "requires_editorial_acceptance": True,
                }
            )
            ordinal += 1
            turn_at += MAX_WORLD_HOLD_SECONDS
    return turns


def compile_full_episode_evidence_coverage(project_root: str | Path) -> dict[str, Any]:
    """Compile a reproducible, non-mutating P32 baseline from canonical inputs."""

    project = Path(project_root).resolve()
    repo_root = _repo_root(project)
    inputs = {label: _read_json(project / relative, label) for label, relative in _REQUIRED_INPUTS.items()}
    hashes = {
        label: _validate_artifact_hash(payload, label)
        for label, payload in inputs.items()
        if label != "teacher_approval"
    }
    hashes["teacher_approval"] = hashlib.sha256((project / _REQUIRED_INPUTS["teacher_approval"]).read_bytes()).hexdigest()
    if inputs["teacher_approval"].get("status") != "approved" or inputs["teacher_approval"].get("approval_scope") != "production_visuals":
        raise CoverageCompilationError("teacher-stamped deck approval is not production_visuals approved")

    cues = inputs["cue_sheet"].get("cues")
    beats = inputs["beat_plan"].get("beats")
    scenes = inputs["snapshot"].get("scenes")
    claims = inputs["claim_ledger"].get("claims")
    if not all(isinstance(value, list) for value in (cues, beats, scenes, claims)):
        raise CoverageCompilationError("cue sheet, beat plan, snapshot scenes, and claim ledger must contain lists")
    if len(cues) != len(beats) or len(cues) != len(inputs["resolution_map"].get("cues") or []):
        raise CoverageCompilationError("cue, beat, and resolution-map counts must match")
    cue_ids = [str(cue.get("cue_id") or "") for cue in cues]
    if not all(cue_ids) or len(cue_ids) != len(set(cue_ids)):
        raise CoverageCompilationError("cue sheet has duplicate or missing cue IDs")
    if len(scenes) != 11:
        raise CoverageCompilationError(f"expected 11 scenes, found {len(scenes)}")
    claims_by_id = {str(claim.get("claim_id") or ""): claim for claim in claims if isinstance(claim, Mapping)}
    if not claims_by_id or "" in claims_by_id:
        raise CoverageCompilationError("claim ledger has malformed claim IDs")

    resolution = _resolution_by_cue(inputs["resolution_map"])
    if set(resolution) != set(cue_ids):
        raise CoverageCompilationError("resolution map cue IDs do not reconcile to canonical cue sheet")
    beat_by_id = {str(beat.get("beat_id") or ""): beat for beat in beats if isinstance(beat, Mapping)}
    world_library = _world_library(project, repo_root, inputs["asset_map"])
    source_surfaces, context_hashes = _source_surfaces(inputs["snapshot"], project, repo_root)
    hashes.update(context_hashes)
    if len(world_library) != 76:
        raise CoverageCompilationError(f"expected 76 composition-approved world plates, found {len(world_library)}")

    records: list[dict[str, Any]] = []
    seen_claims: set[str] = set()
    previous_world_asset_id: str | None = None
    for index, cue in enumerate(cues, start=1):
        if not isinstance(cue, Mapping):
            raise CoverageCompilationError("cue sheet contains malformed cue")
        cue_id = str(cue["cue_id"])
        beat_id = f"cbm-beat-{index:03d}"
        if beat_id not in beat_by_id:
            raise CoverageCompilationError(f"missing beat {beat_id} for cue {cue_id}")
        scene = _scene_for_cue(cue_id, scenes)
        claim_refs = sorted(str(value) for value in cue.get("claim_refs") or [])
        claim_tokens = _claim_tokens(claim_refs, claims_by_id)
        candidates = _rank_source_surfaces(cue, claim_tokens, source_surfaces)
        resolved = resolution[cue_id]
        new_claim_introduction = bool(set(claim_refs) - seen_claims)
        early_new_world_turn = float(cue["start_s"]) < 180.0 and str(resolved["asset_id"]) != previous_world_asset_id
        requires_source_surface = bool(cue.get("fact_surface")) or new_claim_introduction or early_new_world_turn
        if not requires_source_surface:
            status, reason = "manual_only", "no_new_source_surface_required_for_this_cue"
        elif candidates:
            status, reason = "existing_context_needed", "approved_source_surface_requires_crop_and_slot_review"
        else:
            status, reason = "source_pack_needed", "no_safe_contextual_source_surface_match"
        start_s, end_s = round(float(cue["start_s"]), 3), round(float(cue["end_s"]), 3)
        records.append(
            {
                "cue_id": cue_id,
                "beat_id": beat_id,
                "scene_id": str(scene["scene_id"]),
                "start_s": start_s,
                "end_s": end_s,
                "frame_range": {"fps": 30, "start_frame": round(start_s * 30), "end_frame": round(end_s * 30)},
                "excerpt": str(cue.get("excerpt") or ""),
                "claim_refs": claim_refs,
                "active_world_plate": {
                    "asset_id": str(resolved["asset_id"]),
                    "semantic_action": str(resolved.get("semantic_action") or ""),
                },
                "evidence_status": status,
                "evidence_reason": reason,
                "requires_source_surface": requires_source_surface,
                "candidate_evidence": candidates,
                "candidate_slot_status": "requires_reviewed_plate_profile",
                "maximum_simultaneous_evidence": 2,
                "maximum_sequential_evidence": 3,
                "requires_editorial_acceptance": True,
            }
        )
        seen_claims.update(claim_refs)
        previous_world_asset_id = str(resolved["asset_id"])

    segments = _contiguous_segments(cues, resolution)
    turns = _world_turns(segments, scenes, world_library)
    scene_summaries: list[dict[str, Any]] = []
    for scene in scenes:
        scene_id = str(scene["scene_id"])
        scene_records = [record for record in records if record["scene_id"] == scene_id]
        scene_turns = [turn for turn in turns if turn["scene_id"] == scene_id]
        status_counts: dict[str, int] = defaultdict(int)
        for record in scene_records:
            status_counts[str(record["evidence_status"])] += 1
        scene_summaries.append(
            {
                "scene_id": scene_id,
                "title": str(scene.get("title") or ""),
                "start_s": round(float(scene["start_s"]), 3),
                "end_s": round(float(scene["end_s"]), 3),
                "cue_count": len(scene_records),
                "claim_refs": sorted(str(value) for value in scene.get("claim_refs") or []),
                "existing_world_asset_ids": sorted(str(value) for value in scene.get("asset_ids") or []),
                "evidence_status_counts": dict(sorted(status_counts.items())),
                "cadence_turn_count": len(scene_turns),
                "new_world_art_gap_count": sum(turn["state"] == "new_world_art_gap" for turn in scene_turns),
            }
        )
    status_counts: dict[str, int] = defaultdict(int)
    for record in records:
        status_counts[str(record["evidence_status"])] += 1
    payload = {
        "schema_version": COVERAGE_VERSION,
        "compiler_version": COMPILER_VERSION,
        "episode_id": str(inputs["cue_sheet"].get("episode_id") or ""),
        "approval_boundary": {
            "evidence": "teacher-stamped production_visuals; no source surface is auto-inserted",
            "world_plates": "composition-approved visual-only assets; not factual evidence",
            "next_gate": "Gate A coverage-map approval before crop or generation",
        },
        "source_hashes": dict(sorted(hashes.items())),
        "summary": {
            "duration_s": float(inputs["cue_sheet"]["narration"]["duration_s"]),
            "word_count": int(inputs["cue_sheet"]["narration"]["word_count"]),
            "cue_count": len(records),
            "scene_count": len(scene_summaries),
            "evidence_asset_count": len(source_surfaces),
            "production_ready_source_surface_count": sum(item["evidence_state"] == "production_ready" for item in source_surfaces),
            "context_crop_count": sum(item["evidence_state"] == "context_crop_review_only" for item in source_surfaces),
            "composition_world_plate_count": len(world_library),
            "base_resolution_segment_count": len(segments),
            "over_twenty_second_hold_count": sum(float(segment["duration_s"]) > MAX_WORLD_HOLD_SECONDS for segment in segments),
            "cadence_turn_count": len(turns),
            "new_world_art_gap_count": sum(turn["state"] == "new_world_art_gap" for turn in turns),
            "evidence_status_counts": dict(sorted(status_counts.items())),
        },
        "scenes": scene_summaries,
        "world_plate_library": world_library,
        "approved_source_surfaces": source_surfaces,
        "resolution_segments": segments,
        "cadence_turns": turns,
        "cues": records,
        "artifact_hash": "",
    }
    payload["artifact_hash"] = canonical_sha256(payload)
    return payload


def _markdown(payload: Mapping[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# P32 Full-Episode Evidence Coverage Baseline",
        "",
        f"Artifact: `{payload['artifact_hash']}`",
        "",
        "This is a review plan only. It does not insert, crop, generate, or approve evidence.",
        "",
        "## Baseline",
        "",
        f"- {summary['scene_count']} scenes · {summary['cue_count']} cues · {summary['duration_s']:.3f} seconds",
        f"- {summary['composition_world_plate_count']} composition-approved world plates · {summary['evidence_asset_count']} deck/evidence assets ({summary['production_ready_source_surface_count']} production-ready surfaces + {summary['context_crop_count']} context crops)",
        f"- {summary['over_twenty_second_hold_count']} existing holds over 20 seconds · {summary['cadence_turn_count']} cadence turns needing editorial acceptance",
        f"- {summary['new_world_art_gap_count']} true new-world-art gaps before review",
        "",
        "## Scene Coverage",
        "",
        "| Scene | Time | Cues | Existing-context | Source-pack | Cadence turns | New-art gaps |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for scene in payload["scenes"]:
        counts = scene["evidence_status_counts"]
        lines.append(
            f"| {scene['title']} | {scene['start_s']:.3f}–{scene['end_s']:.3f} | {scene['cue_count']} | "
            f"{counts.get('existing_context_needed', 0)} | {counts.get('source_pack_needed', 0)} | "
            f"{scene['cadence_turn_count']} | {scene['new_world_art_gap_count']} |"
        )
    lines.extend(["", "## Gate A Review", "", "Approve or reject the candidate evidence and cadence turns before any crop, source-pack, or generation work.", ""])
    return "\n".join(lines)


def _relative_url(output: Path, asset: Path) -> str:
    return Path(os.path.relpath(asset, output.parent)).as_posix()


def _contact_sheet_html(payload: Mapping[str, Any], output: Path, repo_root: Path) -> str:
    worlds = {item["asset_id"]: item for item in payload["world_plate_library"]}
    sources = {item["asset_id"]: item for item in payload["approved_source_surfaces"]}
    cue_by_scene: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for cue in payload["cues"]:
        cue_by_scene[str(cue["scene_id"])].append(cue)
    sections: list[str] = []
    for scene in payload["scenes"]:
        scene_cues = cue_by_scene[scene["scene_id"]]
        world_id = next((cue["active_world_plate"]["asset_id"] for cue in scene_cues if cue["active_world_plate"]["asset_id"] in worlds), None)
        cards: list[str] = []
        if world_id:
            asset = worlds[world_id]
            image = _relative_url(output, _safe_repo_file(repo_root, str(asset["path"]), f"contact-sheet world {world_id}"))
            cards.append(f'<figure><img src="{html.escape(image)}" alt="{html.escape(world_id)}"><figcaption>World · {html.escape(world_id)}</figcaption></figure>')
        for cue in scene_cues:
            for candidate in cue["candidate_evidence"]:
                asset = sources[candidate["asset_id"]]
                image = _relative_url(output, _safe_repo_file(repo_root, str(asset["path"]), f"contact-sheet source {asset['asset_id']}"))
                cards.append(f'<figure><img src="{html.escape(image)}" alt="{html.escape(asset["label"])}"><figcaption>Candidate · {html.escape(asset["label"])}</figcaption></figure>')
                if len(cards) >= 3:
                    break
            if len(cards) >= 3:
                break
        sections.append(
            f'<section><h2>{html.escape(scene["title"])}</h2><p>{scene["start_s"]:.3f}s–{scene["end_s"]:.3f}s · '
            f'{scene["cue_count"]} cues · {scene["cadence_turn_count"]} cadence turns</p><div class="cards">{"".join(cards) or "<p>No visual candidate selected automatically.</p>"}</div></section>'
        )
    return """<!doctype html><html><head><meta charset=\"utf-8\"><title>P32 Coverage Review</title><style>
body{margin:0;background:#111b20;color:#f7efe1;font:16px/1.45 system-ui,sans-serif;padding:32px}h1{margin-top:0}section{border-top:1px solid #59666b;padding:22px 0}.cards{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}figure{margin:0;background:#213139;padding:8px;border-radius:8px}img{width:100%;display:block;border-radius:4px;aspect-ratio:16/9;object-fit:cover}figcaption{padding:8px 4px 2px}@media(max-width:700px){.cards{grid-template-columns:repeat(2,minmax(0,1fr))}}
</style></head><body><h1>P32 Coverage Review</h1><p>World plate first; deck surfaces are candidates for small, sequential evidence slots only.</p>""" + "".join(sections) + "</body></html>"


def write_full_episode_evidence_coverage(project_root: str | Path, output_dir: str | Path | None = None) -> dict[str, Path]:
    """Write immutable derived Gate-A artifacts and return their paths."""

    project = Path(project_root).resolve()
    repo_root = _repo_root(project)
    output = Path(output_dir).resolve() if output_dir else project / "edit/evidence-coverage-v1"
    output.mkdir(parents=True, exist_ok=True)
    payload = compile_full_episode_evidence_coverage(project)
    coverage_path = output / "full-episode-evidence-coverage.v1.json"
    markdown_path = output / "coverage-summary.md"
    hash_path = output / "source-hash-report.v1.json"
    contact_sheet_path = output / "scene-contact-sheets.html"
    coverage_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(_markdown(payload), encoding="utf-8")
    hash_path.write_text(json.dumps({"schema_version": "p32_source_hash_report.v1", "coverage_artifact_hash": payload["artifact_hash"], "source_hashes": payload["source_hashes"]}, indent=2) + "\n", encoding="utf-8")
    contact_sheet_path.write_text(_contact_sheet_html(payload, contact_sheet_path, repo_root), encoding="utf-8")
    return {"coverage": coverage_path, "summary": markdown_path, "hash_report": hash_path, "contact_sheet": contact_sheet_path}


def validate_full_episode_evidence_coverage(payload: Mapping[str, Any]) -> list[str]:
    """Return stable validation errors for a compiled coverage artifact."""

    config_root = Path(__file__).resolve().parents[2] / "configs"
    schema = _read_json(config_root / "full_episode_evidence_coverage.v1.schema.json", "coverage schema")
    errors = [error.message for error in Draft202012Validator(schema).iter_errors(payload)]
    if payload.get("artifact_hash") != canonical_sha256(payload):
        errors.append("artifact_hash is stale")
    return sorted(errors)


__all__ = [
    "COMPILER_VERSION",
    "COVERAGE_VERSION",
    "CoverageCompilationError",
    "compile_full_episode_evidence_coverage",
    "validate_full_episode_evidence_coverage",
    "write_full_episode_evidence_coverage",
]
