"""Deterministic semantic evidence binding for the P31 production editor.

The compiler turns already-reviewed cue, beat, claim, world-plate, motion,
and deck-crop metadata into an inspectable recommendation.  It never fetches,
generates, promotes, or writes an asset.  A candidate must pass every local
path, byte-hash, review, rights, and approval gate before it can be scored.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
import copy
import hashlib
import json
import math
from pathlib import Path, PurePosixPath, PureWindowsPath
import re
import unicodedata
from typing import Any
from urllib.parse import urlsplit

from jsonschema import Draft202012Validator


PLATE_LAYOUT_PROFILE_VERSION = "plate_layout_profile.v1"
PLATE_LAYOUT_PROFILES_VERSION = "plate_layout_profiles.v1"
SEMANTIC_EVIDENCE_BINDING_VERSION = "semantic_evidence_binding.v1"
COMPILER_VERSION = "p31-semantic-evidence-binding-1.0"

_CONFIG_ROOT = Path(__file__).resolve().parents[2] / "configs"
_PROFILE_SCHEMA = _CONFIG_ROOT / "plate_layout_profile.v1.schema.json"
_PROFILE_CONFIG = _CONFIG_ROOT / "plate_layout_profiles.v1.json"
_BINDING_SCHEMA = _CONFIG_ROOT / "semantic_evidence_binding.v1.schema.json"
_HEX64 = re.compile(r"^[a-f0-9]{64}$")
_SAFE_ID = re.compile(r"^[a-z0-9]+(?:[._-][a-z0-9]+)*$")
_REMOTE_SCHEME = re.compile(r"^(?:https?|data|blob|ftp|file):", re.IGNORECASE)
_MISSING_HASH = "0" * 64

DEFAULT_THRESHOLDS = {"min_score": 55.0, "min_lead_margin": 10.0}

# The weights are deliberately named and kept small enough to audit in a
# candidate ledger.  Exact structured references dominate fuzzy text overlap.
SCORE_WEIGHTS = {
    "exact_cue_reference": 26.0,
    "exact_claim_reference": 24.0,
    "claim_relationship": 10.0,
    "evidence_role_compatibility": 10.0,
    "concept_overlap": 18.0,
    "world_plate_compatibility": 4.0,
    "slot_compatibility": 4.0,
    "readability": 4.0,
}

STOP_WORDS = frozenset(
    {
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "be",
        "by",
        "for",
        "from",
        "has",
        "have",
        "in",
        "into",
        "is",
        "it",
        "of",
        "on",
        "or",
        "that",
        "the",
        "their",
        "this",
        "to",
        "with",
    }
)

# These are controlled finance concepts, not an embedding model.  Every
# source token remains in the feature set while its broader concept is added.
CONTROLLED_CONCEPTS = {
    "memory": frozenset(
        {"memory", "hbm", "dram", "nand", "ram", "semiconductor", "chip", "chips", "die", "dies"}
    ),
    "capacity": frozenset(
        {"capacity", "supply", "volume", "output", "production", "fab", "fabs", "wafer", "wafers"}
    ),
    "constraint": frozenset(
        {"constraint", "constrained", "bottleneck", "chokepoint", "shortage", "scarce", "limited"}
    ),
    "valuation": frozenset(
        {"valuation", "valuations", "price", "prices", "multiple", "multiples", "cape", "bubble", "return"}
    ),
    "comparison": frozenset(
        {"compare", "comparison", "versus", "vs", "ratio", "trade", "relative", "balance"}
    ),
    "manufacturing": frozenset(
        {"manufacturing", "manufacture", "fabrication", "factory", "station", "etch", "backgrinding", "tsv", "package", "packaging"}
    ),
    "commitment": frozenset(
        {"contract", "contracts", "commitment", "commitments", "customer", "customers", "agreement", "agreements", "take", "pay"}
    ),
    "timeline": frozenset(
        {"time", "years", "slow", "long", "generation", "generations", "build", "built", "respond"}
    ),
}
_TOKEN_TO_CONCEPT = {
    token: concept for concept, tokens in CONTROLLED_CONCEPTS.items() for token in tokens
}

_ROLE_ALIASES = {
    "explanation": {"mechanism", "evidence"},
    "mechanism": {"mechanism", "evidence", "comparison"},
    "evidence": {"evidence", "metric", "comparison", "source_quote"},
    "comparison": {"comparison", "metric", "evidence"},
    "metric": {"metric", "evidence", "comparison"},
    "timeline": {"timeline", "mechanism", "evidence"},
    "transition": {"evidence", "mechanism"},
}

_FEATURE_KEYS = frozenset(
    {
        "excerpt",
        "text",
        "title",
        "summary",
        "description",
        "what_it_is",
        "visual_role",
        "representation_mode",
        "state_type",
        "visual_world",
        "viewer_understanding",
        "subject",
        "relationship",
        "purpose",
        "entry_action",
        "exit_transition",
        "subject_action",
        "information_reveal",
        "visual_intent",
        "kind",
        "label",
        "slide_label",
        "deck_title",
        "slide_title",
        "qualifier",
        "classification",
        "active_nouns",
        "causal_verb",
        "required_visual_actions",
        "semantic_tags",
        "capability_anchors",
        "not_what_it_means",
    }
)
_NON_SEMANTIC_KEYS = frozenset(
    {
        "artifact_hash",
        "sha256",
        "source_sha256",
        "source_asset_sha256",
        "path",
        "source",
        "source_asset_path",
        "asset_id",
        "id",
        "cue_id",
        "claim_id",
        "claim_refs",
        "cue_refs",
        "deck_id",
        "slide_id",
        "slide_number",
        "review_state",
        "context_status",
        "rights_state",
        "render_eligible",
        "status",
        "review_scope",
        "reuse_policy",
        "extraction",
        "bbox_norm",
        "bbox_px",
        "focal_point",
        "start_s",
        "end_s",
        "start_frame",
        "end_frame",
        "start_word",
        "end_word",
        "word_range",
        "micro_events",
        "source_locators",
        "counterevidence_refs",
    }
)


class SemanticEvidenceBindingError(ValueError):
    """Raised for an invalid profile or malformed immutable source contract."""

    def __init__(self, errors: str | Sequence[str]):
        self.errors = (errors,) if isinstance(errors, str) else tuple(errors)
        super().__init__("; ".join(self.errors))


def canonical_json(value: Any) -> str:
    """Serialize a value using the repository's deterministic JSON rules."""

    if isinstance(value, Mapping):
        value = {key: item for key, item in value.items() if key != "artifact_hash"}
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def file_sha256(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SemanticEvidenceBindingError(f"cannot read JSON artifact {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise SemanticEvidenceBindingError(f"JSON artifact must be an object: {path}")
    return value


def _schema_errors(value: Mapping[str, Any], schema_path: Path) -> list[str]:
    schema = _read_json(schema_path)
    errors = sorted(
        Draft202012Validator(schema).iter_errors(dict(value)),
        key=lambda error: list(error.absolute_path),
    )
    return [
        f"{'/'.join(str(part) for part in error.absolute_path) or '<root>'}: {error.message}"
        for error in errors[:16]
    ]


def _require_hash(value: Any, label: str) -> str:
    text = str(value or "").casefold()
    if not _HEX64.fullmatch(text):
        raise SemanticEvidenceBindingError(f"{label} must be a lowercase SHA-256 hash")
    return text


def _rect(value: Mapping[str, Any]) -> tuple[float, float, float, float]:
    return (
        float(value["x"]),
        float(value["y"]),
        float(value["width"]),
        float(value["height"]),
    )


def _rect_overlap(left: Mapping[str, Any], right: Mapping[str, Any]) -> bool:
    lx, ly, lw, lh = _rect(left)
    rx, ry, rw, rh = _rect(right)
    return lx < rx + rw and rx < lx + lw and ly < ry + rh and ry < ly + lh


def validate_plate_layout_profile(profile: Mapping[str, Any]) -> dict[str, Any]:
    """Validate one profile, its normalized geometry, and its content hash."""

    value = copy.deepcopy(dict(profile))
    errors = _schema_errors(value, _PROFILE_SCHEMA)
    if not errors:
        expected_hash = canonical_sha256(value)
        if value.get("artifact_hash") != expected_hash:
            errors.append("artifact_hash is stale")
        anchor_ids = {str(item["anchor_id"]) for item in value["annotation_anchors"]}
        slot_ids = [str(item["slot_id"]) for item in value["evidence_slots"]]
        if len(slot_ids) != len(set(slot_ids)):
            errors.append("evidence_slots must have unique slot_id values")
        for slot in value["evidence_slots"]:
            if slot["annotation_anchor_id"] not in anchor_ids:
                errors.append(f"slot {slot['slot_id']!r} references an unknown annotation anchor")
            if not slot["safe"]:
                errors.append(f"slot {slot['slot_id']!r} is not marked safe")
            if slot["max_width"] > slot["rect"]["width"] or slot["max_height"] > slot["rect"]["height"]:
                errors.append(f"slot {slot['slot_id']!r} exceeds its normalized rectangle")
            if any(_rect_overlap(slot["rect"], region["rect"]) for region in value["protected_regions"]):
                errors.append(f"slot {slot['slot_id']!r} overlaps a protected region")
            if any(_rect_overlap(slot["rect"], region["rect"]) for region in value["caption_safe_regions"]):
                errors.append(f"slot {slot['slot_id']!r} overlaps a caption-safe region")
        if value["status"] == "reviewed" and not value["evidence_slots"]:
            errors.append("reviewed profiles require at least one evidence slot")
        if value["status"] == "reviewed" and value["world_asset_sha256"] is None:
            errors.append("reviewed profiles require a world_asset_sha256")
    if errors:
        raise SemanticEvidenceBindingError(errors)
    return value


def load_plate_layout_profiles(path: str | Path | None = None) -> dict[str, dict[str, Any]]:
    """Load and validate the reviewed profile collection used by the compiler."""

    config_path = Path(path) if path is not None else _PROFILE_CONFIG
    config = _read_json(config_path)
    errors = _schema_errors(config, _CONFIG_ROOT / "plate_layout_profiles.v1.schema.json")
    if not errors:
        expected_hash = canonical_sha256(config)
        if config.get("artifact_hash") != expected_hash:
            errors.append("plate profile collection artifact_hash is stale")
    profiles: dict[str, dict[str, Any]] = {}
    for index, raw_profile in enumerate(config.get("profiles", [])):
        try:
            profile = validate_plate_layout_profile(raw_profile)
        except SemanticEvidenceBindingError as exc:
            errors.extend(f"profiles[{index}]: {error}" for error in exc.errors)
            continue
        profile_id = profile["profile_id"]
        if profile_id in profiles:
            errors.append(f"duplicate profile_id: {profile_id!r}")
        profiles[profile_id] = profile
    if config.get("default_profile_id") not in profiles:
        errors.append("default_profile_id does not reference a profile")
    if errors:
        raise SemanticEvidenceBindingError(errors)
    return profiles


# Short alias used by callers that name the collection as "plate profiles".
load_plate_profiles = load_plate_layout_profiles


def _safe_id(value: Any, fallback: str) -> str:
    text = str(value or "").strip().casefold()
    return text if _SAFE_ID.fullmatch(text) else fallback


def _hash_bound(value: Any, label: str, errors: list[str]) -> str:
    if value is None:
        return canonical_sha256({})
    if isinstance(value, Mapping) and value.get("artifact_hash") is not None:
        declared = str(value.get("artifact_hash") or "").casefold()
        expected = canonical_sha256(value)
        if declared != expected:
            errors.append(f"{label}_artifact_hash_mismatch")
        return declared if _HEX64.fullmatch(declared) else expected
    return canonical_sha256(value)


def _normalise_text(value: str) -> list[str]:
    text = unicodedata.normalize("NFKC", value).casefold()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return [token for token in text.split() if len(token) > 1 and token not in STOP_WORDS]


def _semantic_strings(value: Any, *, key: str | None = None) -> list[str]:
    if isinstance(value, str):
        if key in _NON_SEMANTIC_KEYS:
            return []
        return [value]
    if isinstance(value, Mapping):
        strings: list[str] = []
        for child_key, child in value.items():
            if child_key in _NON_SEMANTIC_KEYS:
                continue
            if child_key not in _FEATURE_KEYS and not isinstance(child, (Mapping, list, tuple)):
                continue
            strings.extend(_semantic_strings(child, key=child_key))
        return strings
    if isinstance(value, (list, tuple)):
        strings = []
        for child in value:
            strings.extend(_semantic_strings(child, key=key))
        return strings
    return []


def _features(*values: Any) -> dict[str, list[str]]:
    tokens = {token for value in values for text in _semantic_strings(value) for token in _normalise_text(text)}
    concepts = set(tokens)
    for token in tokens:
        concept = _TOKEN_TO_CONCEPT.get(token)
        if concept:
            concepts.add(concept)
    return {"tokens": sorted(tokens), "concepts": sorted(concepts)}


def _feature_sets(features: Mapping[str, Sequence[str]]) -> tuple[set[str], set[str]]:
    return set(features.get("tokens", [])), set(features.get("concepts", []))


def _claim_list(claim: Any, claim_refs: Sequence[str]) -> list[Mapping[str, Any]]:
    if claim is None:
        return []
    if isinstance(claim, Mapping):
        if isinstance(claim.get("claims"), list):
            candidates = [item for item in claim["claims"] if isinstance(item, Mapping)]
        else:
            candidates = [claim]
    elif isinstance(claim, Sequence) and not isinstance(claim, (str, bytes, bytearray)):
        candidates = [item for item in claim if isinstance(item, Mapping)]
    else:
        return []
    if not claim_refs:
        return candidates
    selected = [item for item in candidates if str(item.get("claim_id") or "") in set(claim_refs)]
    return selected or candidates


def _motion_shot(motion_plan: Any, cue_id: str, beat_ids: set[str]) -> Mapping[str, Any]:
    if not isinstance(motion_plan, Mapping):
        return {}
    shots = motion_plan.get("shots")
    if not isinstance(shots, list):
        return motion_plan
    for shot in shots:
        if not isinstance(shot, Mapping):
            continue
        if cue_id and cue_id in set(shot.get("cue_refs", [])):
            return shot
        if beat_ids.intersection(set(shot.get("parent_beat_ids", []))):
            return shot
    return {}


def _context_and_asset(raw: Mapping[str, Any], parent: Mapping[str, Any] | None = None) -> dict[str, Any]:
    value = copy.deepcopy(dict(raw))
    context = value.get("context")
    if not isinstance(context, Mapping):
        context = {}
    value["_context"] = dict(context)
    if parent:
        value["_deck_context_hash"] = parent.get("artifact_hash")
        value["_deck_title"] = parent.get("title") or parent.get("deck_title")
        value["_deck_id"] = value.get("deck_id") or parent.get("deck_id")
        value["_slide_label"] = value.get("slide_label") or parent.get("slide_label")
    return value


def _iter_deck_assets(deck_contexts: Any) -> tuple[list[dict[str, Any]], list[str]]:
    """Flatten asset-context documents while retaining stale-container errors."""

    assets: list[dict[str, Any]] = []
    errors: list[str] = []

    def add_container(container: Mapping[str, Any]) -> None:
        if container.get("artifact_hash") is not None and container.get("artifact_hash") != canonical_sha256(container):
            container_id = container.get("deck_id") or container.get("manifest_id") or "unknown"
            errors.append(f"deck_context_artifact_hash_mismatch:{container_id}")
        raw_assets = container.get("assets")
        if not isinstance(raw_assets, list):
            errors.append("deck_context_assets_missing")
            return
        for raw_asset in raw_assets:
            if isinstance(raw_asset, Mapping):
                assets.append(_context_and_asset(raw_asset, container))

    if isinstance(deck_contexts, Mapping):
        if isinstance(deck_contexts.get("assets"), list):
            add_container(deck_contexts)
        elif isinstance(deck_contexts.get("deck_contexts"), list):
            for container in deck_contexts["deck_contexts"]:
                if isinstance(container, Mapping):
                    add_container(container)
        else:
            for asset_id, raw_asset in deck_contexts.items():
                if isinstance(raw_asset, Mapping):
                    value = _context_and_asset(raw_asset)
                    value.setdefault("asset_id", asset_id)
                    assets.append(value)
    elif isinstance(deck_contexts, Sequence) and not isinstance(deck_contexts, (str, bytes, bytearray)):
        for item in deck_contexts:
            if not isinstance(item, Mapping):
                errors.append("deck_context_item_not_object")
            elif isinstance(item.get("assets"), list):
                add_container(item)
            else:
                assets.append(_context_and_asset(item))
    return assets, errors


def _resolve_local_path(raw: Any, root: Path | None, label: str) -> tuple[Path | None, str | None]:
    text = str(raw or "").strip()
    if not text:
        return None, f"{label}_path_missing"
    if _REMOTE_SCHEME.match(text) or urlsplit(text).scheme and urlsplit(text).netloc:
        return None, f"{label}_path_not_local"
    if PureWindowsPath(text).is_absolute() or PurePosixPath(text).is_absolute():
        return None, f"{label}_path_must_be_relative"
    parts = PureWindowsPath(text).parts
    if any(part in {"", ".", ".."} for part in parts):
        return None, f"{label}_path_escape"
    if root is None:
        return None, f"{label}_root_missing"
    root_path = root.resolve()
    candidate = (root_path / Path(*parts)).resolve()
    try:
        candidate.relative_to(root_path)
    except ValueError:
        return None, f"{label}_path_escape"
    if not candidate.is_file():
        return None, f"{label}_file_missing"
    return candidate, None


def _approval_record(approval_ledger: Any, asset_id: str) -> Mapping[str, Any] | None:
    if approval_ledger is None:
        return None
    if isinstance(approval_ledger, Mapping):
        for key in ("approvals", "assets", "records"):
            records = approval_ledger.get(key)
            if isinstance(records, list):
                for record in records:
                    if isinstance(record, Mapping) and str(record.get("asset_id") or "") == asset_id:
                        return record
            elif isinstance(records, Mapping) and isinstance(records.get(asset_id), Mapping):
                return records[asset_id]
        record = approval_ledger.get(asset_id)
        return record if isinstance(record, Mapping) else None
    if isinstance(approval_ledger, Sequence) and not isinstance(approval_ledger, (str, bytes, bytearray)):
        for record in approval_ledger:
            if isinstance(record, Mapping) and str(record.get("asset_id") or "") == asset_id:
                return record
    return None


def _candidate_identity(asset: Mapping[str, Any]) -> dict[str, Any]:
    context = asset.get("_context", {})
    if not isinstance(context, Mapping):
        context = {}
    declared_hash = str(asset.get("sha256") or "").casefold()
    source_hash = str(
        asset.get("source_asset_sha256")
        or asset.get("source_sha256")
        or (asset.get("extraction") or {}).get("source_sha256")
        or ""
    ).casefold()
    return {
        "asset_id": str(asset.get("asset_id") or "unknown-asset"),
        "deck_id": str(asset.get("deck_id") or asset.get("_deck_id") or "unknown-deck"),
        "slide_id": str(asset.get("slide_id") or "unknown-slide"),
        "slide_number": asset.get("slide_number") if isinstance(asset.get("slide_number"), int) else None,
        "path": str(asset.get("path") or "<missing-path>"),
        "sha256": declared_hash if _HEX64.fullmatch(declared_hash) else _MISSING_HASH,
        "source_sha256": source_hash if _HEX64.fullmatch(source_hash) else None,
        "context": context,
    }


def _candidate_rejections(
    asset: Mapping[str, Any],
    *,
    asset_root: Path | None,
    approval_ledger: Any,
    used_asset_counts: Counter[str],
    previous_asset_id: str | None,
    reuse_reason: str | None,
    source_errors: Sequence[str],
) -> tuple[dict[str, Any], list[str]]:
    identity = _candidate_identity(asset)
    context = identity["context"]
    reasons: list[str] = []
    asset_id = identity["asset_id"]
    declared_hash = str(asset.get("sha256") or "").casefold()
    if not _HEX64.fullmatch(declared_hash):
        reasons.append("asset_hash_invalid")
    path, path_error = _resolve_local_path(asset.get("path"), asset_root, "asset")
    if path_error:
        reasons.append(path_error)
    elif path is not None and file_sha256(path) != declared_hash:
        reasons.append("asset_hash_mismatch")
    if source_errors:
        reasons.extend(error for error in source_errors if error.startswith("deck_context_artifact_hash_mismatch"))
    if asset.get("kind") not in {None, "semantic_crop"}:
        reasons.append("asset_kind_not_semantic_crop")
    if asset.get("render_eligible") is not True:
        reasons.append("render_not_eligible")
    if asset.get("review_state") not in {"approved_reusable", "approved"}:
        reasons.append("review_not_approved_reusable")
    if asset.get("rights_state") != "approved":
        reasons.append("rights_not_approved")
    if context.get("context_status") != "operator_verified":
        reasons.append("semantic_context_not_operator_verified")
    nested_approval = asset.get("approval")
    if isinstance(nested_approval, Mapping):
        status = str(nested_approval.get("status") or nested_approval.get("state") or "").casefold()
        if status not in {"approved", "operator_approved", "approved_reusable"}:
            reasons.append("approval_not_granted")
        approval_hash = str(nested_approval.get("sha256") or "").casefold()
        if approval_hash and approval_hash != declared_hash:
            reasons.append("approval_hash_mismatch")
    if approval_ledger is not None:
        record = _approval_record(approval_ledger, asset_id)
        if record is None:
            reasons.append("approval_record_missing")
        else:
            status = str(record.get("status") or record.get("state") or "").casefold()
            if status not in {"approved", "operator_approved", "approved_reusable"}:
                reasons.append("approval_not_granted")
            approval_hash = str(record.get("sha256") or record.get("asset_sha256") or "").casefold()
            if approval_hash != declared_hash:
                reasons.append("approval_hash_mismatch")
    policy = context.get("reuse_policy", {})
    if not isinstance(policy, Mapping):
        policy = {}
    count = used_asset_counts.get(asset_id, 0)
    max_uses = policy.get("max_total_uses")
    if max_uses is not None and count >= int(max_uses):
        reasons.append("reuse_limit_exceeded")
    if count and reuse_reason not in set(policy.get("allowed_reasons", [])):
        reasons.append("reuse_reason_not_allowed")
    if previous_asset_id and previous_asset_id == asset_id:
        if not (reuse_reason == "continuation" and policy.get("allow_adjacent_continuation")):
            reasons.append("adjacent_reuse_not_allowed")
    return identity, sorted(set(reasons))


def _expected_roles(cue: Mapping[str, Any], motion: Mapping[str, Any]) -> set[str]:
    roles: set[str] = set()
    for value in (
        cue.get("state_type"),
        cue.get("visual_world"),
        cue.get("visual_intent"),
        motion.get("visual_intent"),
    ):
        if value:
            text = str(value).casefold()
            roles.add(text)
            roles.update(_ROLE_ALIASES.get(text, set()))
    target = cue.get("semantic_target")
    if isinstance(target, Mapping):
        relationship = str(target.get("relationship") or "").casefold()
        for word in ("compare", "ratio", "versus", "relative"):
            if word in relationship:
                roles.add("comparison")
        for word in ("time", "slow", "years", "sequence"):
            if word in relationship:
                roles.add("timeline")
    if not roles:
        roles.update({"mechanism", "evidence"})
    return roles


def _breakdown(points: float, matched: Sequence[str], details: str) -> dict[str, Any]:
    return {"points": round(float(points), 2), "matched": sorted(set(matched)), "details": details}


def _score_candidate(
    identity: Mapping[str, Any],
    asset: Mapping[str, Any],
    *,
    cue: Mapping[str, Any],
    claim_refs: set[str],
    claim_relationship_refs: set[str],
    query_features: Mapping[str, Mapping[str, Sequence[str]]],
    world: Mapping[str, Any],
    world_features: Mapping[str, Sequence[str]],
    motion: Mapping[str, Any],
    slot: Mapping[str, Any],
    used_asset_counts: Counter[str],
    previous_asset_id: str | None,
    reuse_reason: str | None,
) -> dict[str, Any]:
    context = identity["context"]
    asset_id = identity["asset_id"]
    candidate_cue_refs = {str(value) for value in context.get("cue_refs", [])}
    candidate_claim_refs = {str(value) for value in context.get("claim_refs", [])}
    cue_id = str(cue.get("cue_id") or "")
    cue_matches = [cue_id] if cue_id and cue_id in candidate_cue_refs else []
    exact_cue_points = SCORE_WEIGHTS["exact_cue_reference"] if cue_matches else 0.0
    claim_matches = sorted(claim_refs.intersection(candidate_claim_refs))
    exact_claim_points = SCORE_WEIGHTS["exact_claim_reference"] * (
        len(claim_matches) / max(1, len(claim_refs))
    )
    related_refs = {
        str(value)
        for key in ("related_claim_refs", "claim_relationship_refs", "claim_refs")
        for value in (context.get(key, []) if isinstance(context.get(key, []), list) else [])
    }
    relation_matches = sorted(claim_relationship_refs.intersection(related_refs) - set(claim_matches))
    relationship_points = SCORE_WEIGHTS["claim_relationship"] if relation_matches else 0.0
    expected_roles = _expected_roles(cue, motion)
    candidate_role = str(context.get("visual_role") or asset.get("visual_role") or "").casefold()
    role_matches = sorted({candidate_role}.intersection(expected_roles))
    role_points = SCORE_WEIGHTS["evidence_role_compatibility"] if role_matches else (
        SCORE_WEIGHTS["evidence_role_compatibility"] / 2 if candidate_role == "evidence" else 0.0
    )
    query_concepts = set(query_features["all"].get("concepts", []))
    candidate_features = _features(asset, context, {"deck_title": asset.get("_deck_title"), "slide_label": asset.get("_slide_label")})
    candidate_concepts = set(candidate_features["concepts"])
    concept_matches = sorted(query_concepts.intersection(candidate_concepts))
    concept_ratio = len(concept_matches) / max(1, min(len(query_concepts), 12))
    concept_points = SCORE_WEIGHTS["concept_overlap"] * min(1.0, concept_ratio)
    world_id = str(world.get("asset_id") or world.get("id") or "")
    compatible_worlds = {str(value) for value in asset.get("compatible_world_asset_ids", [])}
    world_matches = sorted({world_id}.intersection(compatible_worlds)) if world_id else []
    world_concept_matches = sorted(set(world_features.get("concepts", [])).intersection(candidate_concepts))
    world_points = SCORE_WEIGHTS["world_plate_compatibility"] if world_matches else (
        SCORE_WEIGHTS["world_plate_compatibility"] / 2 if world_concept_matches else 0.0
    )
    slot_roles = {str(value) for value in slot.get("semantic_roles", [])}
    slot_matches = sorted({candidate_role}.intersection(slot_roles))
    source_slot = str(asset.get("source_slot") or context.get("source_slot") or "")
    slot_points = SCORE_WEIGHTS["slot_compatibility"] if slot_matches else 0.0
    if source_slot and source_slot == str(slot.get("slot_id")):
        slot_points = SCORE_WEIGHTS["slot_compatibility"]
        slot_matches.append("source_slot")
    reuse_count = used_asset_counts.get(asset_id, 0)
    reuse_points = -2.0 if reuse_count else 0.0
    reuse_matches = ["previous_use"] if reuse_count else []
    adjacency_points = -4.0 if previous_asset_id and previous_asset_id == asset_id else 0.0
    adjacency_matches = ["adjacent_asset"] if adjacency_points else []
    bbox = (asset.get("extraction") or {}).get("bbox_norm")
    readability_points = 0.0
    readability_detail = "normalized crop bounds unavailable"
    if isinstance(bbox, list) and len(bbox) == 4 and float(bbox[2]) > 0 and float(bbox[3]) > 0:
        crop_ratio = float(bbox[2]) / float(bbox[3])
        slot_rect = slot["rect"]
        slot_ratio = float(slot_rect["width"]) / float(slot_rect["height"])
        similarity = min(crop_ratio / slot_ratio, slot_ratio / crop_ratio)
        readability_points = SCORE_WEIGHTS["readability"] * max(0.0, min(1.0, similarity))
        readability_detail = f"aspect_similarity={similarity:.3f}"
    clutter_value = asset.get("clutter_risk", context.get("clutter_risk", 0.0))
    try:
        clutter_value = max(0.0, min(1.0, float(clutter_value)))
    except (TypeError, ValueError):
        clutter_value = 0.0
    clutter_points = -8.0 * clutter_value
    details = {
        "exact_cue_reference": _breakdown(exact_cue_points, cue_matches, "exact cue reference" if cue_matches else "no exact cue reference"),
        "exact_claim_reference": _breakdown(exact_claim_points, claim_matches, f"{len(claim_matches)}/{max(1, len(claim_refs))} claim references"),
        "claim_relationship": _breakdown(relationship_points, relation_matches, "related claim reference" if relation_matches else "no inherited claim relationship"),
        "evidence_role_compatibility": _breakdown(role_points, role_matches, f"candidate role={candidate_role or 'unknown'}"),
        "concept_overlap": _breakdown(concept_points, concept_matches, f"{len(concept_matches)} normalized concepts overlap"),
        "world_plate_compatibility": _breakdown(world_points, world_matches or world_concept_matches, "world id/concept compatibility" if world_points else "no world compatibility"),
        "slot_compatibility": _breakdown(slot_points, slot_matches, f"slot={slot.get('slot_id')}"),
        "reuse_policy": _breakdown(reuse_points, reuse_matches, "asset has prior use" if reuse_count else "no prior use"),
        "adjacency": _breakdown(adjacency_points, adjacency_matches, "adjacent reuse" if adjacency_points else "no adjacent reuse"),
        "readability": _breakdown(readability_points, [], readability_detail),
        "clutter": _breakdown(clutter_points, [], f"clutter_risk={clutter_value:.3f}"),
    }
    total = round(sum(item["points"] for item in details.values()), 2)
    details["total"] = total
    return {"score_breakdown": details, "total_score": total}


def _profile_index(profiles: Any) -> tuple[dict[str, dict[str, Any]], str]:
    if profiles is None:
        loaded = load_plate_layout_profiles()
        return loaded, "generic-off-center-v1"
    default_id = "generic-off-center-v1"
    if isinstance(profiles, Mapping) and isinstance(profiles.get("profiles"), list):
        default_id = str(profiles.get("default_profile_id") or default_id)
        raw_profiles = profiles["profiles"]
    elif isinstance(profiles, Mapping):
        raw_profiles = list(profiles.values())
    elif isinstance(profiles, Sequence) and not isinstance(profiles, (str, bytes, bytearray)):
        raw_profiles = list(profiles)
    else:
        raise SemanticEvidenceBindingError("profiles must be a profile collection")
    index: dict[str, dict[str, Any]] = {}
    errors: list[str] = []
    for raw_profile in raw_profiles:
        if not isinstance(raw_profile, Mapping):
            errors.append("profile is not an object")
            continue
        try:
            profile = validate_plate_layout_profile(raw_profile)
        except SemanticEvidenceBindingError as exc:
            errors.extend(exc.errors)
            continue
        index[profile["profile_id"]] = profile
    if errors:
        raise SemanticEvidenceBindingError(errors)
    return index, default_id


def _resolve_profile(
    world: Mapping[str, Any],
    *,
    profiles: Any,
    explicit_profile: Mapping[str, Any] | str | None,
) -> tuple[dict[str, Any] | None, list[str]]:
    errors: list[str] = []
    if explicit_profile is not None:
        if isinstance(explicit_profile, Mapping):
            try:
                return validate_plate_layout_profile(explicit_profile), errors
            except SemanticEvidenceBindingError as exc:
                return None, list(exc.errors)
        profile_id = str(explicit_profile)
        try:
            index, _ = _profile_index(profiles)
        except SemanticEvidenceBindingError as exc:
            return None, list(exc.errors)
        profile = index.get(profile_id)
        return (profile, errors) if profile else (None, [f"profile_not_found:{profile_id}"])
    try:
        index, default_id = _profile_index(profiles)
    except SemanticEvidenceBindingError as exc:
        return None, list(exc.errors)
    world_id = str(world.get("asset_id") or world.get("id") or "")
    candidates = [
        profile
        for profile in index.values()
        if profile.get("world_asset_id") in {world_id, world_id.removeprefix("world-")}
    ]
    if candidates:
        return sorted(candidates, key=lambda item: str(item["profile_id"]))[0], errors
    return index.get(default_id), errors


def _world_errors(
    world: Mapping[str, Any],
    profile: Mapping[str, Any] | None,
    *,
    world_root: Path | None,
) -> list[str]:
    errors: list[str] = []
    world_hash = str(world.get("sha256") or world.get("hash") or "").casefold()
    if not _HEX64.fullmatch(world_hash):
        errors.append("world_asset_hash_invalid")
    if profile and profile.get("status") == "reviewed":
        expected = str(profile.get("world_asset_sha256") or "").casefold()
        if world_hash != expected:
            errors.append("world_asset_hash_mismatch")
    raw_path = world.get("path") or world.get("source_path")
    if raw_path:
        path, path_error = _resolve_local_path(raw_path, world_root, "world_asset")
        if path_error:
            errors.append(path_error)
        elif path is not None and file_sha256(path) != world_hash:
            errors.append("world_asset_hash_mismatch")
    return sorted(set(errors))


def _select_slot(
    profile: Mapping[str, Any] | None,
    *,
    occupied_slot_ids: set[str],
    occupied_regions: Sequence[Mapping[str, Any]],
    active_evidence_count: int,
) -> tuple[Mapping[str, Any] | None, list[str]]:
    if profile is None:
        return None, ["profile_unavailable"]
    if active_evidence_count >= int(profile["limits"]["max_evidence_images"]):
        return None, ["evidence_clutter_budget_exhausted"]
    available = sorted(profile.get("evidence_slots", []), key=lambda item: (int(item["order"]), str(item["slot_id"])))
    if not available:
        return None, ["no_configured_evidence_slot"]
    reasons: list[str] = []
    caption_regions = profile.get("caption_safe_regions", [])
    for slot in available:
        slot_id = str(slot["slot_id"])
        if slot_id in occupied_slot_ids:
            reasons.append(f"slot_occupied:{slot_id}")
            continue
        if not slot.get("safe"):
            reasons.append(f"slot_not_safe:{slot_id}")
            continue
        if any(_rect_overlap(slot["rect"], region["rect"]) for region in profile.get("protected_regions", [])):
            reasons.append(f"slot_overlaps_protected_region:{slot_id}")
            continue
        if any(_rect_overlap(slot["rect"], region) for region in occupied_regions):
            reasons.append(f"slot_overlaps_active_region:{slot_id}")
            continue
        if any(_rect_overlap(slot["rect"], region["rect"]) for region in caption_regions):
            reasons.append(f"slot_overlaps_caption_zone:{slot_id}")
            continue
        return slot, reasons
    return None, reasons or ["no_reviewed_safe_slot"]


def _frame_range(cue: Mapping[str, Any], snapshot: Mapping[str, Any] | None) -> dict[str, int]:
    profile = snapshot.get("project_profile", {}) if isinstance(snapshot, Mapping) else {}
    fps = float(profile.get("fps") or snapshot.get("fps") if isinstance(snapshot, Mapping) else 30)
    fps = fps if fps > 0 else 30.0
    if isinstance(cue.get("start_frame"), int) and isinstance(cue.get("end_frame"), int):
        start = int(cue["start_frame"])
        end = int(cue["end_frame"])
    else:
        start = math.floor(float(cue.get("start_s") or 0.0) * fps)
        end = math.ceil(float(cue.get("end_s") or 0.0) * fps)
    return {"start_frame": max(0, start), "end_frame": max(start + 1, end)}


def _proposed_binding(
    candidate: Mapping[str, Any],
    slot: Mapping[str, Any],
    profile: Mapping[str, Any],
    *,
    cue: Mapping[str, Any],
    snapshot: Mapping[str, Any] | None,
) -> dict[str, Any] | None:
    anchors = {str(item["anchor_id"]): item for item in profile.get("annotation_anchors", [])}
    anchor = anchors.get(str(slot.get("annotation_anchor_id")))
    if not anchor:
        return None
    caption = next(
        (region for region in profile.get("caption_safe_regions", []) if not _rect_overlap(slot["rect"], region["rect"])),
        None,
    )
    if caption is None:
        return None
    return {
        "asset_id": candidate["asset_id"],
        "asset_sha256": candidate["sha256"],
        "slot_id": slot["slot_id"],
        "slot_rect": copy.deepcopy(slot["rect"]),
        "caption_zone": {"region_id": caption["region_id"], "rect": copy.deepcopy(caption["rect"])},
        "annotation_anchor": copy.deepcopy(anchor["point"]),
        "source_marker": copy.deepcopy(slot["source_marker"]),
        "frame_range": _frame_range(cue, snapshot),
    }


def compile_semantic_evidence_binding(
    cue: Mapping[str, Any],
    beat: Mapping[str, Any] | None = None,
    claim: Mapping[str, Any] | Sequence[Mapping[str, Any]] | None = None,
    world: Mapping[str, Any] | None = None,
    deck_contexts: Any = (),
    *,
    project_id: str = "unidentified-project",
    snapshot: Mapping[str, Any] | None = None,
    motion_plan: Mapping[str, Any] | None = None,
    plate_profile: Mapping[str, Any] | str | None = None,
    profiles: Any = None,
    asset_root: str | Path | None = None,
    world_root: str | Path | None = None,
    approval_ledger: Any = None,
    thresholds: Mapping[str, float] | None = None,
    occupied_slot_ids: Sequence[str] = (),
    occupied_regions: Sequence[Mapping[str, Any]] = (),
    used_asset_ids: Sequence[str] | Mapping[str, int] = (),
    previous_asset_id: str | None = None,
    reuse_reason: str | None = None,
    active_evidence_count: int = 0,
    fps: int | None = None,
    **aliases: Any,
) -> dict[str, Any]:
    """Compile one immutable semantic evidence binding ledger.

    Positional arguments mirror the current cue/beat/claim/world/deck source
    order.  The small alias set keeps the service usable by callers that name
    the world ``world_plate`` or the catalog ``asset_contexts``.
    """

    if world is None:
        world = aliases.pop("world_plate", None)
    if not deck_contexts:
        deck_contexts = aliases.pop("asset_contexts", aliases.pop("deck_assets", deck_contexts))
    if aliases:
        unknown = ", ".join(sorted(aliases))
        raise SemanticEvidenceBindingError(f"unsupported compiler arguments: {unknown}")
    if not isinstance(cue, Mapping):
        raise SemanticEvidenceBindingError("cue must be an object")
    if not isinstance(beat, Mapping):
        beat = {}
    if not isinstance(world, Mapping):
        world = {}
    if not isinstance(snapshot, Mapping):
        snapshot = {}
    if not isinstance(motion_plan, Mapping):
        motion_plan = {}
    cue_id = _safe_id(cue.get("cue_id"), "unknown-cue")
    beat_ids = {str(value) for value in beat.get("beat_ids", beat.get("beat_refs", []))}
    if beat.get("beat_id"):
        beat_ids.add(str(beat["beat_id"]))
    claim_refs = {str(value) for value in cue.get("claim_refs", [])}
    claim_refs.update(str(value) for value in beat.get("claim_refs", []))
    claims = _claim_list(claim, sorted(claim_refs))
    claim_relationship_refs = {
        str(value)
        for item in claims
        for key in ("related_claim_refs", "counterevidence_refs", "relationship_refs")
        for value in (item.get(key, []) if isinstance(item.get(key, []), list) else [])
    }
    motion = _motion_shot(motion_plan, cue_id, beat_ids)
    query_features = {
        "cue": _features(
            {
                "excerpt": cue.get("excerpt"),
                "state_type": cue.get("state_type"),
                "visual_world": cue.get("visual_world"),
                "representation_mode": cue.get("representation_mode"),
                "entry_action": cue.get("entry_action"),
                "exit_transition": cue.get("exit_transition"),
                "semantic_target": cue.get("semantic_target"),
            }
        ),
        "beat": _features(beat),
        "claim": _features(claims),
        "world": _features(world),
        "motion": _features(motion),
    }
    query_features["all"] = _features(query_features["cue"], query_features["beat"], query_features["claim"], query_features["world"], query_features["motion"])
    source_errors: list[str] = []
    source_hashes = {
        "snapshot": _hash_bound(snapshot, "snapshot", source_errors),
        "cue": _hash_bound(cue, "cue", source_errors),
        "beat": _hash_bound(beat, "beat", source_errors),
        "claim": _hash_bound(claim if claim is not None else {}, "claim", source_errors),
        "motion_plan": _hash_bound(motion_plan, "motion_plan", source_errors),
    }
    resolved_profile, profile_errors = _resolve_profile(
        world,
        profiles=profiles,
        explicit_profile=plate_profile,
    )
    source_errors.extend(profile_errors)
    profile_hash = resolved_profile.get("artifact_hash") if resolved_profile else _MISSING_HASH
    source_hashes["plate_profile"] = profile_hash if _HEX64.fullmatch(str(profile_hash or "")) else _MISSING_HASH
    assets, catalog_errors = _iter_deck_assets(deck_contexts)
    source_errors.extend(catalog_errors)
    if isinstance(deck_contexts, Sequence) and not isinstance(deck_contexts, (str, bytes, bytearray, Mapping)):
        # A bare sequence is a catalog view rather than a hash-bound source
        # document.  Sort its immutable asset identities so caller ordering
        # cannot change a recommendation artifact.
        catalog_for_hash = sorted(assets, key=lambda item: str(item.get("asset_id") or ""))
        source_hashes["asset_catalog"] = canonical_sha256(catalog_for_hash)
    else:
        source_hashes["asset_catalog"] = _hash_bound(deck_contexts, "asset_catalog", source_errors)
    approval_for_hash = approval_ledger if approval_ledger is not None else {}
    if isinstance(approval_for_hash, Sequence) and not isinstance(approval_for_hash, (str, bytes, bytearray, Mapping)):
        approval_for_hash = sorted(
            approval_for_hash,
            key=lambda item: str(item.get("asset_id") or "") if isinstance(item, Mapping) else str(item),
        )
    source_hashes["approval"] = _hash_bound(approval_for_hash, "approval", source_errors)
    asset_root_path = Path(asset_root).resolve() if asset_root is not None else None
    world_root_path = Path(world_root).resolve() if world_root is not None else asset_root_path
    world_errors = _world_errors(world, resolved_profile, world_root=world_root_path)
    source_errors.extend(world_errors)
    occupied = {str(value) for value in occupied_slot_ids}
    occupied.update(str(value) for value in world.get("occupied_slot_ids", []) if isinstance(world.get("occupied_slot_ids", []), list))
    active_regions = list(occupied_regions)
    if isinstance(world.get("occupied_regions"), list):
        active_regions.extend(region for region in world["occupied_regions"] if isinstance(region, Mapping))
    active_count = max(int(active_evidence_count), int(world.get("active_evidence_count") or 0))
    slot, slot_reasons = _select_slot(
        resolved_profile,
        occupied_slot_ids=occupied,
        occupied_regions=active_regions,
        active_evidence_count=active_count,
    )
    used_counts = Counter()
    if isinstance(used_asset_ids, Mapping):
        used_counts.update({str(key): int(value) for key, value in used_asset_ids.items()})
    else:
        used_counts.update(str(value) for value in used_asset_ids)
    eligible: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    for asset in assets:
        identity, reasons = _candidate_rejections(
            asset,
            asset_root=asset_root_path,
            approval_ledger=approval_ledger,
            used_asset_counts=used_counts,
            previous_asset_id=previous_asset_id,
            reuse_reason=reuse_reason,
            source_errors=source_errors,
        )
        if reasons:
            rejected.append(
                {
                    "asset_id": identity["asset_id"],
                    "deck_id": identity["deck_id"],
                    "slide_id": identity["slide_id"],
                    "path": identity["path"],
                    "sha256": identity["sha256"],
                    "rejection_reasons": reasons,
                }
            )
            continue
        if slot is None:
            rejected.append(
                {
                    "asset_id": identity["asset_id"],
                    "deck_id": identity["deck_id"],
                    "slide_id": identity["slide_id"],
                    "path": identity["path"],
                    "sha256": identity["sha256"],
                    "rejection_reasons": ["no_safe_slot_available"],
                }
            )
            continue
        scored = _score_candidate(
            identity,
            asset,
            cue=cue,
            claim_refs=claim_refs,
            claim_relationship_refs=claim_relationship_refs,
            query_features=query_features,
            world=world,
            world_features=query_features["world"],
            motion=motion,
            slot=slot,
            used_asset_counts=used_counts,
            previous_asset_id=previous_asset_id,
            reuse_reason=reuse_reason,
        )
        eligible.append(
            {
                "asset_id": identity["asset_id"],
                "deck_id": identity["deck_id"],
                "slide_id": identity["slide_id"],
                "slide_number": identity["slide_number"],
                "path": identity["path"],
                "sha256": identity["sha256"],
                "source_sha256": identity["source_sha256"],
                "rank": 0,
                "total_score": scored["total_score"],
                "lead_margin": 0.0,
                "score_breakdown": scored["score_breakdown"],
                "rejection_reasons": [],
            }
        )
    eligible.sort(key=lambda item: (-float(item["total_score"]), str(item["asset_id"])))
    for index, candidate in enumerate(eligible, start=1):
        candidate["rank"] = index
    if eligible:
        runner_score = float(eligible[1]["total_score"]) if len(eligible) > 1 else 0.0
        top_margin = round(float(eligible[0]["total_score"]) - runner_score, 2) if len(eligible) > 1 else round(float(eligible[0]["total_score"]), 2)
        eligible[0]["lead_margin"] = top_margin
    for index, candidate in enumerate(eligible[1:], start=1):
        candidate["lead_margin"] = round(float(candidate["total_score"]) - float(eligible[index - 1]["total_score"]), 2)
    configured_thresholds = dict(DEFAULT_THRESHOLDS)
    if thresholds is not None:
        for key in configured_thresholds:
            if key in thresholds:
                configured_thresholds[key] = float(thresholds[key])
    proposed: dict[str, Any] | None = None
    state = "unmatched"
    reason = "no_eligible_candidates"
    if source_errors or world_errors:
        state = "manual_only"
        reason = "input_hash_mismatch" if any("hash" in error or "artifact" in error for error in source_errors) else "input_contract_error"
    elif resolved_profile is None:
        state = "manual_only"
        reason = "profile_unavailable"
    elif resolved_profile.get("status") != "reviewed":
        state = "manual_only"
        reason = "generic_profile_requires_manual_review" if resolved_profile.get("status") == "manual_only" else "profile_not_reviewed"
    elif slot is None:
        state = "manual_only"
        reason = "no_reviewed_safe_slot"
    elif not eligible:
        state = "unmatched"
        reason = "no_eligible_candidates"
    else:
        top_score = float(eligible[0]["total_score"])
        lead_margin = float(eligible[0]["lead_margin"])
        if top_score < configured_thresholds["min_score"]:
            reason = "score_below_threshold"
        elif len(eligible) > 1 and lead_margin < configured_thresholds["min_lead_margin"]:
            reason = "ambiguous_lead_margin"
        else:
            proposed = _proposed_binding(eligible[0], slot, resolved_profile, cue=cue, snapshot=snapshot)
            if proposed is None:
                state = "manual_only"
                reason = "proposed_geometry_incomplete"
            else:
                state = "recommended"
                reason = "top_candidate_passed_thresholds"
    if state == "manual_only" and slot_reasons:
        source_errors.extend(reason for reason in slot_reasons if reason not in source_errors)
    world_asset_id = str(world.get("asset_id") or world.get("id") or "unknown-world")
    world_hash = str(world.get("sha256") or world.get("hash") or "").casefold()
    binding = {
        "schema_version": SEMANTIC_EVIDENCE_BINDING_VERSION,
        "binding_id": f"semantic-binding-{_safe_id(project_id, 'project')}-{_safe_id(snapshot.get('snapshot_id'), 'snapshot')}-{cue_id}",
        "project_id": str(project_id),
        "snapshot_id": str(snapshot.get("snapshot_id") or "unbound-snapshot"),
        "cue_id": cue_id,
        "beat_ids": sorted(_safe_id(value, "unknown-beat") for value in beat_ids),
        "claim_refs": sorted(claim_refs),
        "world_plate": {
            "asset_id": world_asset_id,
            "sha256": world_hash if _HEX64.fullmatch(world_hash) else _MISSING_HASH,
            "profile_id": _safe_id(resolved_profile.get("profile_id") if resolved_profile else None, "unavailable-profile"),
            "profile_status": resolved_profile.get("status") if resolved_profile else "unavailable",
        },
        "source_hashes": source_hashes,
        "normalized_features": {key: query_features[key] for key in ("cue", "beat", "claim", "world", "motion")},
        "thresholds": configured_thresholds,
        "eligible_candidates": eligible,
        "rejected_candidates": sorted(rejected, key=lambda item: (str(item["asset_id"]), str(item["path"]))),
        "recommendation_state": state,
        "recommendation_reason": reason,
        "proposed_binding": proposed,
        "accepted_binding": None,
        "binding_errors": sorted(set(source_errors)),
        "compiler_version": COMPILER_VERSION,
    }
    binding["artifact_hash"] = canonical_sha256(binding)
    return binding


def rank_semantic_evidence_candidates(*args: Any, **kwargs: Any) -> dict[str, Any]:
    """Compatibility-oriented name for the same deterministic compiler."""

    return compile_semantic_evidence_binding(*args, **kwargs)


class SemanticEvidenceBindingCompiler:
    """Small state-free adapter for callers that prefer an object service."""

    def __init__(self, *, profiles: Any = None, asset_root: str | Path | None = None, world_root: str | Path | None = None):
        self.profiles = profiles
        self.asset_root = asset_root
        self.world_root = world_root

    def compile(self, cue: Mapping[str, Any], **kwargs: Any) -> dict[str, Any]:
        kwargs.setdefault("profiles", self.profiles)
        kwargs.setdefault("asset_root", self.asset_root)
        kwargs.setdefault("world_root", self.world_root)
        return compile_semantic_evidence_binding(cue, **kwargs)


__all__ = [
    "COMPILER_VERSION",
    "DEFAULT_THRESHOLDS",
    "PLATE_LAYOUT_PROFILE_VERSION",
    "PLATE_LAYOUT_PROFILES_VERSION",
    "SCORE_WEIGHTS",
    "SEMANTIC_EVIDENCE_BINDING_VERSION",
    "SemanticEvidenceBindingCompiler",
    "SemanticEvidenceBindingError",
    "canonical_json",
    "canonical_sha256",
    "compile_semantic_evidence_binding",
    "file_sha256",
    "load_plate_layout_profiles",
    "load_plate_profiles",
    "rank_semantic_evidence_candidates",
    "validate_plate_layout_profile",
]
