from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from statistics import median
from typing import Any

from src.models import OutreachActivationEvent
from src.repositories.base import InsightRepository


FUNNEL_STAGES = [
    "package_approved",
    "outreach_sent",
    "positive_reply",
    "call_booked",
    "proposal_sent",
    "closed_won",
    "closed_lost",
    "correction_recorded",
]
ALLOWED_STAGES = tuple(FUNNEL_STAGES)


class ActivationService:
    """Append activation events and derive funnel metrics from event history."""

    def __init__(self, repository: InsightRepository):
        self.repository = repository

    def append_event(self, event: OutreachActivationEvent) -> OutreachActivationEvent:
        self.validate_event(event)
        package = self.repository.get_outreach_package(event.outreach_package_id)
        if package is None:
            raise ValueError(f"outreach package {event.outreach_package_id} not found")
        if package.insight_run_id != event.insight_run_id:
            raise ValueError("activation event run does not match package")
        if package.package_version != event.package_version:
            raise ValueError("activation event package version does not match package")
        prospect = self.repository.get_prospect(package.prospect_id)
        if prospect is None:
            raise ValueError(f"prospect {package.prospect_id} not found for package")
        if event.vertical_id != prospect.vertical_id:
            raise ValueError("activation event vertical does not match package prospect")
        if set(event.service_packages) != set(package.recommended_service_package):
            raise ValueError(
                "activation event service packages do not match immutable package routing"
            )
        if event.stage in {"package_approved", "outreach_sent", "positive_reply", "call_booked", "proposal_sent", "closed_won", "closed_lost"}:
            if package.state != "approved":
                raise ValueError("funnel events require an approved package")
        return self.repository.append_activation_event(event)

    @staticmethod
    def validate_event(event: OutreachActivationEvent) -> None:
        if event.stage not in FUNNEL_STAGES:
            raise ValueError(f"invalid activation stage: {event.stage}")
        if not event.insight_run_id or not event.outreach_package_id or not event.vertical_id or not event.operator.strip():
            raise ValueError("activation events require run, package, vertical, and operator identity")
        if event.stage != "closed_won" and (event.revenue_amount is not None or event.currency is not None):
            raise ValueError("revenue and currency are only valid for closed_won events")
        if event.stage == "closed_won" and (event.revenue_amount is None or not event.currency):
            raise ValueError("closed_won requires revenue_amount and currency")

    def summarize(self, *, vertical_id: str | None = None) -> dict[str, Any]:
        events = self.repository.list_activation_events(vertical_id=vertical_id, limit=50000)
        by_vertical: dict[str, dict[str, Any]] = defaultdict(self._empty_summary)
        prospects = self.repository.list_prospects(
            vertical_id=vertical_id,
            qualification_status="qualified",
            limit=10000,
        )
        for prospect in prospects:
            by_vertical[prospect.vertical_id]["qualified_prospect_ids"].add(prospect.id)
        for event in events:
            bucket = by_vertical[event.vertical_id]
            bucket["event_count"] += 1
            bucket["stage_packages"][event.stage].add(
                (event.outreach_package_id, event.package_version)
            )
            bucket["package_ids"].add(event.outreach_package_id)
            bucket["events"].append(event)
            service_key = self._service_key(event.service_packages)
            service_bucket = bucket["service_segments"][service_key]
            service_bucket["stage_packages"][event.stage].add(
                (event.outreach_package_id, event.package_version)
            )
            if event.stage == "closed_won" and event.revenue_amount is not None:
                bucket["closed_won_revenue"] += event.revenue_amount
                service_bucket["closed_won_revenue"] += event.revenue_amount
        summaries = {}
        for key, bucket in by_vertical.items():
            stage_counts = {
                stage: len(bucket["stage_packages"].get(stage, set()))
                for stage in FUNNEL_STAGES
            }
            packages = self.repository.list_outreach_packages(limit=10000)
            vertical_packages = [
                package
                for package in packages
                if package.vertical_pack_version.startswith(f"{key}.")
            ]
            review_seconds = [
                self._elapsed_seconds(package.created_at, package.approved_at)
                for package in vertical_packages
                if package.approved_at
            ]
            approved_count = stage_counts["package_approved"]
            correction_count = stage_counts["correction_recorded"]
            estimated_paid_calls = 0
            for package in vertical_packages:
                run = self.repository.get_run(package.insight_run_id)
                if run is not None:
                    estimated_paid_calls += int(
                        run.input_payload.get("budget", {}).get(
                            "estimated_paid_api_calls", 0
                        )
                        or 0
                    )
            summaries[key] = {
                "event_count": bucket["event_count"],
                "package_count": len(bucket["package_ids"]),
                "qualified_prospect_count": len(bucket["qualified_prospect_ids"]),
                "stage_counts": stage_counts,
                "conversion_rates": self._rates(
                    stage_counts,
                    qualified_count=len(bucket["qualified_prospect_ids"]),
                ),
                "correction_rate": (
                    None if approved_count == 0 else correction_count / approved_count
                ),
                "median_review_seconds": (
                    median(review_seconds) if review_seconds else None
                ),
                "estimated_paid_api_calls": estimated_paid_calls,
                "closed_won_revenue": bucket["closed_won_revenue"],
                "service_package_segments": {
                    service_key: self._service_segment_summary(service_bucket)
                    for service_key, service_bucket in sorted(
                        bucket["service_segments"].items()
                    )
                },
                "current_state": self._aggregate_state(bucket["events"]),
            }
        return {"verticals": summaries, "total_event_count": len(events)}

    def funnel_summary(self, *, vertical_id: str | None = None) -> dict[str, Any]:
        return self.summarize(vertical_id=vertical_id)

    def derive_funnel(self, *, vertical_id: str | None = None) -> dict[str, Any]:
        return self.summarize(vertical_id=vertical_id)

    @staticmethod
    def current_state(events: list[OutreachActivationEvent]) -> dict[str, Any]:
        # Manual events can legitimately share the same timestamp on fast
        # imports.  Break those ties by funnel progression before the opaque
        # UUID so derived state is deterministic across repository backends.
        ordered = sorted(
            events,
            key=lambda item: (
                item.occurred_at,
                FUNNEL_STAGES.index(item.stage),
                item.id,
            ),
        )
        reached = {stage: any(event.stage == stage for event in ordered) for stage in FUNNEL_STAGES}
        terminal = "closed_won" if reached["closed_won"] else "closed_lost" if reached["closed_lost"] else None
        return {
            "last_stage": ordered[-1].stage if ordered else None,
            "terminal_stage": terminal,
            "reached": reached,
            "event_count": len(ordered),
        }

    @staticmethod
    def _empty_summary() -> dict[str, Any]:
        return {
            "event_count": 0,
            "package_ids": set(),
            "qualified_prospect_ids": set(),
            "stage_packages": defaultdict(set),
            "service_segments": defaultdict(ActivationService._empty_service_segment),
            "closed_won_revenue": 0.0,
            "events": [],
        }

    @staticmethod
    def _rates(
        stage_counts: dict[str, int],
        *,
        qualified_count: int = 0,
    ) -> dict[str, float | None]:
        pairs = [
            ("approved_to_sent", "package_approved", "outreach_sent"),
            ("sent_to_positive_reply", "outreach_sent", "positive_reply"),
            ("reply_to_booked_call", "positive_reply", "call_booked"),
            ("booked_call_to_proposal", "call_booked", "proposal_sent"),
            ("proposal_to_closed_won", "proposal_sent", "closed_won"),
        ]
        rates: dict[str, float | None] = {}
        for label, denominator_stage, numerator_stage in pairs:
            denominator = stage_counts.get(denominator_stage, 0)
            rates[label] = None if denominator == 0 else stage_counts.get(numerator_stage, 0) / denominator
        rates["qualified_to_approved"] = (
            None
            if qualified_count == 0
            else stage_counts.get("package_approved", 0) / qualified_count
        )
        return rates

    @staticmethod
    def _empty_service_segment() -> dict[str, Any]:
        return {
            "stage_packages": defaultdict(set),
            "closed_won_revenue": 0.0,
        }

    @staticmethod
    def _service_key(service_packages: list[str]) -> str:
        return "+".join(sorted(set(service_packages))) or "none"

    @staticmethod
    def _service_segment_summary(bucket: dict[str, Any]) -> dict[str, Any]:
        stage_counts = {
            stage: len(bucket["stage_packages"].get(stage, set()))
            for stage in FUNNEL_STAGES
        }
        approved_count = stage_counts["package_approved"]
        return {
            "stage_counts": stage_counts,
            "conversion_rates": ActivationService._rates(stage_counts),
            "correction_rate": (
                None
                if approved_count == 0
                else stage_counts["correction_recorded"] / approved_count
            ),
            "closed_won_revenue": bucket["closed_won_revenue"],
        }

    @staticmethod
    def _elapsed_seconds(started_at: str, completed_at: str | None) -> float:
        if not completed_at:
            return 0.0
        try:
            started = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
            completed = datetime.fromisoformat(completed_at.replace("Z", "+00:00"))
        except ValueError:
            return 0.0
        return max(0.0, (completed - started).total_seconds())

    @staticmethod
    def _aggregate_state(events: list[OutreachActivationEvent]) -> str | None:
        if not events:
            return None
        states = []
        for events_for_package in ActivationService._group_events(events):
            state = ActivationService.current_state(events_for_package)
            states.append(state["terminal_stage"] or state["last_stage"])
        return max((state for state in states if state), key=lambda state: FUNNEL_STAGES.index(state), default=None)

    @staticmethod
    def _group_events(events: list[OutreachActivationEvent]) -> list[list[OutreachActivationEvent]]:
        grouped: dict[tuple[str, str, int], list[OutreachActivationEvent]] = defaultdict(list)
        for event in events:
            grouped[(event.insight_run_id, event.outreach_package_id, event.package_version)].append(event)
        return list(grouped.values())
