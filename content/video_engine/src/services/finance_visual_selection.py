"""Fail-closed semantic asset resolution for finance editorial cues.

This module has no provider, network, file-write, or render dependency.  It
matches explicit visual anchors and representation modes, then returns either a
deterministic resolution or a complete asset-demand record.  Similar tags are
intentionally insufficient evidence of a usable image.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Any, Mapping, Sequence


RESOLUTION_STRATEGIES = (
    "exact_asset",
    "component_composition",
    "deterministic_surface",
)
DEMAND_STRATEGIES = (
    "source_retrieval_request",
    "original_generation_request",
    "local_compositor_request",
    "script_revision_request",
)
REUSE_REASONS = {"continuation", "callback", "comparison", "evidence_hold"}


@dataclass(frozen=True, slots=True)
class SelectionResult:
    """A selected asset or a reviewable requirement for an unavailable one."""

    status: str
    strategy: str
    asset_ids: tuple[str, ...]
    demand: dict[str, Any] | None
    errors: tuple[str, ...] = ()


def _anchors(item: Mapping[str, Any]) -> set[str]:
    return {str(value) for value in item.get("capability_anchors", [])}


def _mode_compatible(asset: Mapping[str, Any], cue: Mapping[str, Any]) -> bool:
    return str(cue.get("representation_mode")) in set(asset.get("representation_modes", []))


def _claim_compatible(asset: Mapping[str, Any], cue: Mapping[str, Any]) -> bool:
    policy = asset.get("reuse_policy", {})
    if not isinstance(policy, Mapping) or not policy.get("claim_bound"):
        return True
    return set(cue.get("claim_refs", [])).issubset(set(asset.get("claim_refs", [])))


def _eligible(asset: Mapping[str, Any], *, require_promoted: bool) -> bool:
    if not require_promoted:
        return True
    return bool(asset.get("render_eligible")) and asset.get("review_state") == "approved_reusable" and asset.get("rights_state") == "approved"


def _matches(asset: Mapping[str, Any], cue: Mapping[str, Any], *, require_promoted: bool) -> bool:
    target = cue.get("semantic_target", {})
    required = set(target.get("required_visual_anchors", [])) if isinstance(target, Mapping) else set()
    prohibited = set(target.get("prohibited_implications", [])) if isinstance(target, Mapping) else set()
    return (
        _eligible(asset, require_promoted=require_promoted)
        and _mode_compatible(asset, cue)
        and required.issubset(_anchors(asset))
        and not prohibited.intersection(set(asset.get("prohibited_implications", [])))
        and _claim_compatible(asset, cue)
    )


def build_demand(cue: Mapping[str, Any], *, kind: str = "original_generation_request") -> dict[str, Any]:
    """Produce an immutable-quality request instead of selecting a near match."""

    if kind not in DEMAND_STRATEGIES:
        raise ValueError(f"unsupported demand kind: {kind}")
    target = cue.get("semantic_target", {})
    if not isinstance(target, Mapping):
        target = {}
    cue_id = str(cue.get("cue_id", "unidentified-cue"))
    return {
        "demand_id": f"demand-{cue_id}",
        "kind": kind,
        "brief": (
            f"{target.get('subject', 'Unspecified subject')} must show "
            f"{target.get('relationship', 'the stated relationship')} so the viewer understands "
            f"{target.get('viewer_takeaway', 'the narration claim')}"
        ),
        "required_visual_anchors": list(target.get("required_visual_anchors", [])),
        "prohibited_implications": list(target.get("prohibited_implications", [])),
        "depth_layers": ["foreground", "midground", "background", "negative_space"],
        "review_state": "draft",
    }


def resolve_cue(
    cue: Mapping[str, Any],
    assets: Sequence[Mapping[str, Any]],
    *,
    require_promoted: bool = False,
) -> SelectionResult:
    """Resolve only an unambiguous exact capability match, otherwise demand art."""

    candidates = [asset for asset in assets if _matches(asset, cue, require_promoted=require_promoted)]
    candidates.sort(key=lambda item: (int(item.get("resolution_tier", 99)), str(item.get("asset_id", ""))))
    if not candidates:
        return SelectionResult("unresolved", "original_generation_request", (), build_demand(cue))

    selected = candidates[0]
    return SelectionResult("resolved", "exact_asset", (str(selected["asset_id"]),), None)


def validate_reuse(
    resolution: Mapping[str, Any],
    asset_index: Mapping[str, Mapping[str, Any]],
    usage: Counter[str],
    *,
    previous_asset_ids: set[str] | None = None,
) -> list[str]:
    """Validate policy before a resolution is appended to an edit sequence."""

    errors: list[str] = []
    reason = resolution.get("reuse_reason")
    current = {str(asset_id) for asset_id in resolution.get("selected_asset_ids", [])}
    previous = previous_asset_ids or set()
    for asset_id in current:
        asset = asset_index.get(asset_id)
        if asset is None:
            errors.append(f"unknown asset {asset_id!r}")
            continue
        policy = asset.get("reuse_policy", {})
        if not isinstance(policy, Mapping):
            errors.append(f"asset {asset_id!r} is missing reuse_policy")
            continue
        next_count = usage[asset_id] + 1
        if next_count > int(policy.get("max_total_uses", 0)):
            errors.append(f"asset {asset_id!r} exceeds max_total_uses")
        if usage[asset_id] and reason not in set(policy.get("allowed_reasons", [])):
            errors.append(f"asset {asset_id!r} reuse_reason is absent or disallowed")
        if asset_id in previous and not (reason == "continuation" and policy.get("allow_adjacent_continuation")):
            errors.append(f"asset {asset_id!r} cannot repeat adjacent without permitted continuation")
        if reason is not None and reason not in REUSE_REASONS:
            errors.append(f"asset {asset_id!r} has unknown reuse_reason")
    return errors


__all__ = [
    "DEMAND_STRATEGIES",
    "RESOLUTION_STRATEGIES",
    "REUSE_REASONS",
    "SelectionResult",
    "build_demand",
    "resolve_cue",
    "validate_reuse",
]
