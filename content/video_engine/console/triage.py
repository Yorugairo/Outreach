"""Triage session state — decisions held server-side until commit.

Decisions live in memory, keyed by delivery root. They are reversible until the
operator commits, and nothing here touches the catalogue: this module records
intent, and ``asset_catalog.register_assets`` is the only thing that ever acts
on it.

Policy, small enough to test exhaustively:

* a **clean** asset carries a default decision of ``promote`` — exception-first
  review means the operator only has to touch what is flagged;
* a **flag** asset has no default; it requires an explicit decision;
* a **fail** asset may be rejected or skipped, never promoted — a failing guard
  is not an aesthetic judgement to overrule from a keyboard.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

PROMOTE = "promote"
REJECT = "reject"
SKIP = "skip"

_DECISIONS = {PROMOTE, REJECT, SKIP}


class TriageError(ValueError):
    """A decision that the triage policy does not allow."""

    def __init__(self, errors: list[str]):
        self.errors = [str(item) for item in errors]
        super().__init__("; ".join(self.errors) or "invalid triage decision")


def default_decision(status: str) -> str | None:
    """Clean assets default to promotion; anything else needs a human."""

    return PROMOTE if status == "clean" else None


def validate_decision(status: str, decision: str) -> None:
    if decision not in _DECISIONS:
        raise TriageError([f"unknown decision {decision!r}; expected one of {sorted(_DECISIONS)}"])
    if status == "fail" and decision == PROMOTE:
        raise TriageError([
            "a failed asset cannot be promoted from triage; the failing check "
            "must be fixed and the delivery rescanned"
        ])


@dataclass
class TriageSession:
    """One delivery under review."""

    delivery_root: str
    report: dict[str, Any]
    decisions: dict[str, str] = field(default_factory=dict)

    def status_of(self, asset_id: str) -> str:
        for row in self.report["assets"]:
            if row["asset_id"] == asset_id:
                return str(row["status"])
        raise TriageError([f"{asset_id!r} is not in this delivery"])

    def decide(self, asset_id: str, decision: str) -> None:
        validate_decision(self.status_of(asset_id), decision)
        self.decisions[asset_id] = decision

    def clear(self, asset_id: str) -> None:
        self.decisions.pop(asset_id, None)

    def effective(self, asset_id: str) -> str | None:
        """The operator's decision, or the status default."""

        if asset_id in self.decisions:
            return self.decisions[asset_id]
        return default_decision(self.status_of(asset_id))

    def is_explicit(self, asset_id: str) -> bool:
        return asset_id in self.decisions

    def summary(self) -> dict[str, Any]:
        rows = self.report["assets"]
        effective = {str(r["asset_id"]): self.effective(str(r["asset_id"])) for r in rows}
        undecided = [
            aid for aid, decision in effective.items() if decision is None
        ]
        return {
            "total": len(rows),
            "promote": sum(1 for d in effective.values() if d == PROMOTE),
            "reject": sum(1 for d in effective.values() if d == REJECT),
            "skip": sum(1 for d in effective.values() if d == SKIP),
            "undecided": undecided,
            "explicit": sorted(self.decisions),
        }


class TriageStore:
    """In-memory sessions, keyed by delivery root. Localhost, one operator."""

    def __init__(self) -> None:
        self._sessions: dict[str, TriageSession] = {}

    def start(self, delivery_root: str, report: Mapping[str, Any]) -> TriageSession:
        session = TriageSession(delivery_root=delivery_root, report=dict(report))
        self._sessions[delivery_root] = session
        return session

    def get(self, delivery_root: str) -> TriageSession | None:
        return self._sessions.get(delivery_root)

    def drop(self, delivery_root: str) -> None:
        self._sessions.pop(delivery_root, None)
