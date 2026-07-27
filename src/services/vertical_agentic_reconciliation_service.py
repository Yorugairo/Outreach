"""Qualified-prospect to reviewed-agentic-pack reconciliation."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from src.vertical_agentic_packs import (
    AgenticPackResolution,
    reconcile_vertical_agentic_pack,
)


class VerticalAgenticReconciliationService:
    """Resolve pack/version and expose an idempotent eligibility decision."""

    def resolve(
        self,
        prospect: Any | None = None,
        *,
        vertical_pack_version: str | None = None,
        qualified: bool | None = None,
        operator_enabled: bool = True,
        require_approved: bool = True,
    ) -> AgenticPackResolution:
        pack_value = vertical_pack_version
        if pack_value is None and prospect is not None:
            if isinstance(prospect, Mapping):
                pack_value = prospect.get("vertical_pack_version") or prospect.get("vertical_id")
                if qualified is None:
                    qualified = prospect.get("qualification_status") == "qualified"
            else:
                pack_value = getattr(prospect, "vertical_pack_version", None) or getattr(prospect, "vertical_id", None)
                if qualified is None:
                    qualified = getattr(prospect, "qualification_status", None) == "qualified"
        return reconcile_vertical_agentic_pack(
            pack_value,
            qualified=True if qualified is None else bool(qualified),
            operator_enabled=operator_enabled,
            require_approved=require_approved,
        )

    reconcile = resolve


__all__ = ["VerticalAgenticReconciliationService"]
