"""Deterministic scan of a claim's delivery — the gate that cannot be persuaded.

Wraps ``delivery_intake``'s verdict layer for the claim loop: load the
delivery, scan every asset (hashes, dimensions, alpha rim, style family,
promotion guards), and cross-check the generating agent's ``approvals.json``
against the arithmetic. An asset the agent approved but the scan fails is a
**conflict** — the exact case the operator (or an escalation judge) should
see first.

No writes, no model, no tokens. Everything here is re-runnable.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from content.video_engine.src.services.delivery_intake import (
    DeliveryIntakeError,
    load_delivery,
    scan_delivery,
)

APPROVALS_FILENAME = "approvals.json"


def read_approvals(delivery_root: str | Path) -> dict[str, Any] | None:
    """The agent's completion signal, if present. Its word is data, not truth."""

    path = Path(delivery_root) / APPROVALS_FILENAME
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise DeliveryIntakeError([f"{APPROVALS_FILENAME} is unreadable: {exc}"])


def scan_claim_delivery(
    claim: Mapping[str, Any],
    *,
    style_families: Mapping[str, Sequence[str]] | None = None,
) -> dict[str, Any]:
    """Scan a claim's delivery and reconcile it with the agent's approvals."""

    delivery_root = Path(str(claim["delivery_dir"]))
    loaded = load_delivery(delivery_root)
    report = scan_delivery(
        loaded["assets"], delivery_root=delivery_root, style_families=style_families,
    )
    approvals = read_approvals(delivery_root)

    verdicts = {str(row["asset_id"]): str(row["status"]) for row in report["assets"]}
    approved = set(map(str, (approvals or {}).get("approved") or []))
    unresolved = [str(u) for u in (approvals or {}).get("unresolved") or []]
    conflicts = sorted(
        asset_id for asset_id, status in verdicts.items()
        if status == "fail" and asset_id in approved
    )
    counts = {
        "fail": sum(1 for s in verdicts.values() if s == "fail"),
        "flag": sum(1 for s in verdicts.values() if s == "flag"),
        "clean": sum(1 for s in verdicts.values() if s == "clean"),
    }
    return {
        "claim_id": claim.get("claim_id"),
        "delivery_root": str(delivery_root),
        "style_version": loaded.get("style_version"),
        "counts": counts,
        "conflicts": conflicts,
        "unresolved": unresolved,
        "has_approvals": approvals is not None,
        "assets": loaded["assets"],
        "report": report,
    }


def summary_line(summary: Mapping[str, Any]) -> str:
    """One line for a toast or a Telegram message."""

    counts = summary["counts"]
    parts = [
        f"claim {summary.get('claim_id')}:",
        f"{counts['clean']} clean, {counts['flag']} flagged, {counts['fail']} failed",
    ]
    if summary.get("conflicts"):
        parts.append(f"CONFLICTS: {', '.join(summary['conflicts'])}")
    if summary.get("unresolved"):
        parts.append(f"unresolved: {len(summary['unresolved'])}")
    return " ".join(parts)
