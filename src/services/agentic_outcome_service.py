"""Append-only recommendation outcome memory for the P12 agentic layer.

This module deliberately keeps outcome learning downstream of the immutable
run/report/package contracts.  It only joins an approved recommendation to
an approved package, reads activation history, and emits aggregate
associations.  It never mutates a link or an activation event and never
claims that a recommendation caused a funnel outcome.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict, dataclass, field
from typing import Any, Iterable, Mapping

from src.models import RecommendationOutcomeLink, utc_now_iso
from src.repositories.base import InsightRepository


OUTCOME_MEMORY_VERSION = "recommendation-outcome-memory.v1"
MIN_SENT_PACKAGES = 20
MIN_POSITIVE_REPLIES = 5
MIN_BOOKED_CALLS = 3
CALIBRATION_THRESHOLDS = {
    "sent_packages": MIN_SENT_PACKAGES,
    "positive_replies": MIN_POSITIVE_REPLIES,
    "booked_calls": MIN_BOOKED_CALLS,
}

FUNNEL_STAGES = (
    "package_approved",
    "outreach_sent",
    "positive_reply",
    "call_booked",
    "proposal_sent",
    "closed_won",
    "closed_lost",
    "correction_recorded",
)


@dataclass(slots=True)
class OutcomeAssociation:
    """One aggregate finding/service cohort.

    No prospect, package, or event identifiers are exposed here.  The
    denominator fields make small samples visible to operators and keep the
    output descriptive rather than causal.
    """

    vertical_id: str
    recommendation_id: str
    service_fit: list[str]
    denominators: dict[str, int]
    associations: dict[str, dict[str, Any]]
    calibration_eligible: bool
    calibration_blockers: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class OutcomeCalibrationSummary:
    """Immutable-in-memory aggregate summary for one vertical scope."""

    vertical_id: str
    denominators: dict[str, int]
    associations: dict[str, dict[str, Any]]
    recommendation_cohorts: list[dict[str, Any]]
    calibration_eligible: bool
    calibration_blockers: list[str]
    source_link_count: int
    invalid_link_count: int = 0
    version: str = OUTCOME_MEMORY_VERSION
    created_at: str = field(default_factory=utc_now_iso)

    @property
    def eligible(self) -> bool:
        """Compatibility spelling used by callers reading gate status."""

        return self.calibration_eligible

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["eligible"] = self.calibration_eligible
        payload["association_disclaimer"] = (
            "Descriptive association only; this history does not establish "
            "that a recommendation caused an outcome."
        )
        payload["calibration_thresholds"] = dict(CALIBRATION_THRESHOLDS)
        return payload


class RecommendationOutcomeService:
    """Bind approved recommendations and derive gated outcome memory.

    The repository is the source of truth.  This service performs no writes
    except the one immutable link creation operation; activation and review
    events are always appended through their existing services/repository
    methods and are only read here.
    """

    VERSION = OUTCOME_MEMORY_VERSION
    THRESHOLDS = CALIBRATION_THRESHOLDS

    def __init__(self, repository: InsightRepository):
        self.repository = repository

    # ------------------------------------------------------------------
    # Immutable binding
    # ------------------------------------------------------------------
    def bind_approved_recommendation(
        self,
        *,
        recommendation_id: str,
        source_snapshot_id: str,
        outreach_package_id: str,
        outreach_package_version: int | None = None,
        prospect_id: str | None = None,
        vertical_id: str | None = None,
        service_fit: Iterable[str] | None = None,
    ) -> RecommendationOutcomeLink:
        """Create (or return) an immutable recommendation/package link.

        A package must already be approved and the recommendation must be one
        of its approved findings.  Repeating the exact binding is idempotent;
        attempting to bind the same package/recommendation to different source
        or service data is rejected rather than rewriting history.
        """

        recommendation_id = self._require(recommendation_id, "recommendation_id")
        source_snapshot_id = self._require(source_snapshot_id, "source_snapshot_id")
        outreach_package_id = self._require(outreach_package_id, "outreach_package_id")
        package = self.repository.get_outreach_package(outreach_package_id)
        if package is None:
            raise ValueError(f"outreach package {outreach_package_id} not found")
        if package.state != "approved":
            raise ValueError("recommendation outcome links require an approved outreach package")

        package_version = (
            package.package_version
            if outreach_package_version is None
            else outreach_package_version
        )
        if package_version != package.package_version:
            raise ValueError("outcome link package version does not match immutable package")
        expected_prospect = package.prospect_id
        if prospect_id is not None and prospect_id != expected_prospect:
            raise ValueError("outcome link prospect does not match package")
        expected_vertical = self._vertical_from_package(package.vertical_pack_version)
        resolved_vertical = vertical_id or expected_vertical
        if not resolved_vertical:
            raise ValueError("outcome links require a resolvable vertical")
        if expected_vertical and resolved_vertical != expected_vertical:
            raise ValueError("outcome link vertical does not match package")

        package_services = tuple(sorted(set(package.recommended_service_package)))
        resolved_services = tuple(
            sorted(set(service_fit if service_fit is not None else package_services))
        )
        if not resolved_services:
            raise ValueError("outcome links require a non-empty service fit")
        if not set(resolved_services).issubset(set(package_services)):
            raise ValueError("outcome link service fit must be supported by immutable package routing")

        self._require_approved_finding(package.approved_findings, recommendation_id)
        self._validate_source_snapshot(
            source_snapshot_id,
            insight_run_id=package.insight_run_id,
        )

        existing = self._existing_link(
            recommendation_id=recommendation_id,
            outreach_package_id=outreach_package_id,
        )
        if existing is not None:
            if (
                existing.source_snapshot_id != source_snapshot_id
                or existing.outreach_package_version != package_version
                or tuple(sorted(existing.service_fit)) != resolved_services
            ):
                raise ValueError("recommendation outcome links are immutable")
            return existing

        activation_event_ids, correction_event_ids = self._current_event_ids(
            outreach_package_id=outreach_package_id,
            package_version=package_version,
            vertical_id=resolved_vertical,
        )
        link = RecommendationOutcomeLink(
            recommendation_id=recommendation_id,
            source_snapshot_id=source_snapshot_id,
            outreach_package_id=outreach_package_id,
            outreach_package_version=package_version,
            prospect_id=expected_prospect,
            vertical_id=resolved_vertical,
            service_fit=list(resolved_services),
            activation_event_ids=activation_event_ids,
            correction_event_ids=correction_event_ids,
        )
        return self.repository.save_recommendation_outcome_link(link)

    # Common spellings for API/service callers.
    create_link = bind_approved_recommendation
    link_recommendation = bind_approved_recommendation
    save_link = bind_approved_recommendation
    create_outcome_link = bind_approved_recommendation
    bind_recommendation = bind_approved_recommendation

    # ------------------------------------------------------------------
    # Aggregate summaries
    # ------------------------------------------------------------------
    def summarize(
        self,
        *,
        vertical_id: str | None = None,
        recommendation_id: str | None = None,
        service_fit: Iterable[str] | None = None,
    ) -> dict[str, Any]:
        """Return denominator-first, association-only outcome evidence."""

        links = list(
            self.repository.list_recommendation_outcome_links(
                vertical_id=vertical_id,
                recommendation_id=recommendation_id,
                limit=10000,
            )
        )
        required_services = set(service_fit or ())
        valid_links: list[RecommendationOutcomeLink] = []
        invalid_link_count = 0
        for link in links:
            if required_services and not required_services.issubset(set(link.service_fit)):
                continue
            if not self._link_scope_valid(link):
                invalid_link_count += 1
                continue
            valid_links.append(link)
        valid_links = self._latest_links(valid_links)

        resolved_vertical = vertical_id or self._single_vertical(valid_links) or "all"
        aggregate = self._aggregate_links(valid_links)
        cohorts = [
            cohort.to_dict()
            for cohort in sorted(
                self._cohorts(valid_links),
                key=lambda item: (item.recommendation_id, item.service_fit),
            )
        ]
        summary = OutcomeCalibrationSummary(
            vertical_id=resolved_vertical,
            denominators=aggregate["denominators"],
            associations=aggregate["associations"],
            recommendation_cohorts=cohorts,
            calibration_eligible=aggregate["calibration_eligible"],
            calibration_blockers=aggregate["calibration_blockers"],
            source_link_count=len(valid_links),
            invalid_link_count=invalid_link_count,
        )
        return summary.to_dict()

    summary = summarize
    summarize_vertical = summarize
    build_summary = summarize

    def append_activation_event(self, event: Any) -> Any:
        """Append a funnel/correction event through the existing service.

        Keeping this convenience method here makes the outcome layer easy to
        operate without giving it a mutable history API: ``ActivationService``
        still enforces package/version/service identity and the repository
        remains append-only.
        """

        from src.services.activation_service import ActivationService

        return ActivationService(self.repository).append_event(event)

    append_event = append_activation_event

    def attach_activation_event(
        self, *, link_id: str, event_id: str
    ) -> RecommendationOutcomeLink:
        """Create an immutable successor link containing one event reference.

        Activation events remain append-only.  The existing link is never
        edited; a successor carries the additional reference and points back
        through ``predecessor_id`` for auditability.
        """

        link = self.repository.get_recommendation_outcome_link(link_id)
        if link is None:
            raise ValueError(f"recommendation outcome link {link_id} not found")
        events = self.repository.list_activation_events(
            outreach_package_id=link.outreach_package_id,
            limit=50000,
        )
        event = next((item for item in events if item.id == event_id), None)
        if event is None:
            raise ValueError(f"activation event {event_id} not found for outcome link")
        if event.package_version != link.outreach_package_version:
            raise ValueError("activation event package version does not match outcome link")
        if event.vertical_id != link.vertical_id:
            raise ValueError("activation event vertical does not match outcome link")
        activation_ids = list(link.activation_event_ids)
        correction_ids = list(link.correction_event_ids)
        destination = correction_ids if event.stage == "correction_recorded" else activation_ids
        if event_id in destination:
            return link
        destination.append(event_id)
        successor = RecommendationOutcomeLink(
            recommendation_id=link.recommendation_id,
            source_snapshot_id=link.source_snapshot_id,
            outreach_package_id=link.outreach_package_id,
            outreach_package_version=link.outreach_package_version,
            prospect_id=link.prospect_id,
            vertical_id=link.vertical_id,
            service_fit=list(link.service_fit),
            activation_event_ids=activation_ids,
            correction_event_ids=correction_ids,
            predecessor_id=link.id,
        )
        return self.repository.save_recommendation_outcome_link(successor)

    link_event = attach_activation_event
    attach_event = attach_activation_event

    def calibration_gate(self, *, vertical_id: str) -> dict[str, Any]:
        """Return the explicit vertical gate without exposing raw records."""

        summary = self.summarize(vertical_id=vertical_id)
        return {
            "version": self.VERSION,
            "vertical_id": vertical_id,
            "eligible": bool(summary.get("calibration_eligible")),
            "thresholds": dict(CALIBRATION_THRESHOLDS),
            "denominators": {
                key: summary.get("denominators", {}).get(key, 0)
                for key in CALIBRATION_THRESHOLDS
            },
            "blockers": list(summary.get("calibration_blockers", [])),
            "outcome_adjustment_permitted": bool(summary.get("calibration_eligible")),
        }

    gate = calibration_gate

    def calibrated_outcome_rates(
        self,
        *,
        vertical_id: str,
        metric: str = "positive_reply_rate",
    ) -> dict[str, Any]:
        """Return gated rates consumable by ``RecommendationPriorityService``.

        The explicit marker is intentional: a caller cannot accidentally pass
        a small-sample mapping and make outcome history affect ordering.
        """

        summary = self.summarize(vertical_id=vertical_id)
        eligible = bool(summary.get("calibration_eligible"))
        rates: dict[str, Any] = {
            "__calibration_eligible__": eligible,
            "__calibration_version__": self.VERSION,
            "__vertical_id__": vertical_id,
            "__metric__": metric,
            "__calibration_blockers__": list(summary.get("calibration_blockers", [])),
        }
        if not eligible:
            return rates
        for cohort in summary.get("recommendation_cohorts", []):
            recommendation = str(cohort.get("recommendation_id") or "").strip()
            association = cohort.get("associations", {}).get(metric)
            if recommendation and isinstance(association, Mapping):
                rates[recommendation] = {
                    "value": association.get("value"),
                    "numerator": association.get("numerator"),
                    "denominator": association.get("denominator"),
                    "eligible": True,
                }
        return rates

    outcome_rates = calibrated_outcome_rates
    calibration_rates = calibrated_outcome_rates

    # ------------------------------------------------------------------
    # Similar-case retrieval
    # ------------------------------------------------------------------
    def similar_cases(
        self,
        *,
        vertical_id: str,
        service_fit: Iterable[str],
        recommendation_id: str,
    ) -> dict[str, Any]:
        """Retrieve only compatible aggregate history.

        Finding compatibility is intentionally exact on the stable
        recommendation identity.  The response omits prospect/package/event
        IDs, allowing it to be reused by an agent without cross-prospect
        disclosure.
        """

        requested_services = set(service_fit)
        links = self.repository.list_recommendation_outcome_links(
            vertical_id=vertical_id,
            recommendation_id=recommendation_id,
            limit=10000,
        )
        compatible = [
            link
            for link in links
            if requested_services.issubset(set(link.service_fit))
            and self._link_scope_valid(link)
        ]
        compatible = self._latest_links(compatible)
        aggregate = self._aggregate_links(compatible)
        return {
            "version": self.VERSION,
            "vertical_id": vertical_id,
            "service_fit": sorted(requested_services),
            "finding_compatibility": "exact_recommendation_id",
            "compatible_case_count": len({self._package_key(link) for link in compatible}),
            "denominators": aggregate["denominators"],
            "associations": aggregate["associations"],
            "calibration_eligible": aggregate["calibration_eligible"],
            "calibration_blockers": aggregate["calibration_blockers"],
            "aggregate_only": True,
            "association_disclaimer": (
                "Descriptive association only; similar-case history does not "
                "establish causation or guarantee an outcome."
            ),
        }

    retrieve_similar_cases = similar_cases
    find_similar_cases = similar_cases

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------
    def _existing_link(
        self, *, recommendation_id: str, outreach_package_id: str
    ) -> RecommendationOutcomeLink | None:
        links = self.repository.list_recommendation_outcome_links(
            recommendation_id=recommendation_id,
            limit=10000,
        )
        matches = [
            link for link in links if link.outreach_package_id == outreach_package_id
        ]
        return max(matches, key=lambda item: (item.created_at, item.id), default=None)

    def _link_scope_valid(self, link: RecommendationOutcomeLink) -> bool:
        package = self.repository.get_outreach_package(link.outreach_package_id)
        if package is None or package.state != "approved":
            return False
        return (
            package.package_version == link.outreach_package_version
            and package.prospect_id == link.prospect_id
            and self._vertical_from_package(package.vertical_pack_version)
            in {link.vertical_id, ""}
        )

    @staticmethod
    def _latest_links(
        links: Iterable[RecommendationOutcomeLink],
    ) -> list[RecommendationOutcomeLink]:
        """Collapse immutable successor chains to the latest binding."""

        latest: dict[tuple[str, str, int], RecommendationOutcomeLink] = {}
        for link in links:
            key = (
                link.recommendation_id,
                link.outreach_package_id,
                link.outreach_package_version,
            )
            current = latest.get(key)
            if current is None or (link.created_at, link.id) > (
                current.created_at,
                current.id,
            ):
                latest[key] = link
        return list(latest.values())

    def _validate_source_snapshot(self, snapshot_id: str, *, insight_run_id: str) -> None:
        """Resolve known P12/P10 snapshots when the repository exposes them.

        A small in-memory test repository may intentionally implement only the
        package/link methods.  In that case the immutable ID remains the
        persisted evidence reference and the package/run checks still apply.
        """

        getter_names = (
            "get_agentic_assessment_snapshot",
            "get_business_fact_ledger_snapshot",
            "get_decision_coverage_snapshot",
            "get_journey_evidence_run",
            "get_ai_representation_accuracy_snapshot",
            "get_remediation_blueprint_snapshot",
            "get_report_snapshot",
        )
        resolved = None
        for name in getter_names:
            getter = getattr(self.repository, name, None)
            if getter is None:
                continue
            try:
                candidate = getter(snapshot_id)
            except (KeyError, ValueError):
                candidate = None
            if candidate is not None:
                resolved = candidate
                break
        if resolved is None:
            return
        source_run = getattr(resolved, "run_id", None) or getattr(
            resolved, "insight_run_id", None
        )
        if source_run and source_run != insight_run_id:
            raise ValueError("outcome link source snapshot does not match package run")
        if getattr(resolved, "mode", "prospect") == "owner_verified":
            raise ValueError("prospect outcome links cannot bind owner-mode evidence")

    @staticmethod
    def _require(value: str, label: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{label} is required")
        return value.strip()

    @staticmethod
    def _vertical_from_package(version: str | None) -> str:
        return str(version or "").split(".", 1)[0].strip()

    @staticmethod
    def _require_approved_finding(
        findings: Iterable[Mapping[str, Any]], recommendation_id: str
    ) -> None:
        records = list(findings)
        if not records:
            raise ValueError("approved package has no recommendation findings")
        identities = {
            str(
                finding.get("recommendation_id")
                or finding.get("finding_id")
                or finding.get("id")
                or ""
            ).strip()
            for finding in records
            if isinstance(finding, Mapping)
        }
        if recommendation_id not in identities:
            raise ValueError("recommendation is not an approved finding on the package")

    @staticmethod
    def _single_vertical(links: Iterable[RecommendationOutcomeLink]) -> str | None:
        values = {link.vertical_id for link in links if link.vertical_id}
        return next(iter(values)) if len(values) == 1 else None

    @staticmethod
    def _package_key(link: RecommendationOutcomeLink) -> tuple[str, int]:
        return (link.outreach_package_id, link.outreach_package_version)

    def _events(self, link: RecommendationOutcomeLink) -> list[Any]:
        events = self.repository.list_activation_events(
            outreach_package_id=link.outreach_package_id,
            limit=50000,
        )
        return [
            event
            for event in events
            if event.package_version == link.outreach_package_version
            and event.vertical_id == link.vertical_id
        ]

    def _current_event_ids(
        self, *, outreach_package_id: str, package_version: int, vertical_id: str
    ) -> tuple[list[str], list[str]]:
        events = self.repository.list_activation_events(
            outreach_package_id=outreach_package_id,
            limit=50000,
        )
        selected = [
            event
            for event in events
            if event.package_version == package_version
            and event.vertical_id == vertical_id
        ]
        return (
            [event.id for event in selected if event.stage != "correction_recorded"],
            [event.id for event in selected if event.stage == "correction_recorded"],
        )

    def _aggregate_links(
        self, links: Iterable[RecommendationOutcomeLink]
    ) -> dict[str, Any]:
        packages: set[tuple[str, int]] = set()
        stage_packages: dict[str, set[tuple[str, int]]] = defaultdict(set)
        correction_events: set[str] = set()
        for link in links:
            package_key = self._package_key(link)
            # A package can carry multiple compatible findings, but each
            # stage counts once in a cohort aggregate.
            events = self._events(link)
            packages.add(package_key)
            for event in events:
                stage = str(event.stage)
                if stage not in FUNNEL_STAGES:
                    continue
                if stage == "correction_recorded":
                    correction_events.add(event.id)
                else:
                    stage_packages[stage].add(package_key)

        denominators = {
            "approved_packages": len(stage_packages["package_approved"]),
            "sent_packages": len(stage_packages["outreach_sent"]),
            "positive_replies": len(stage_packages["positive_reply"]),
            "booked_calls": len(stage_packages["call_booked"]),
            "proposals": len(stage_packages["proposal_sent"]),
            "closed_won": len(stage_packages["closed_won"]),
            "closed_lost": len(stage_packages["closed_lost"]),
            "corrections": len(correction_events),
        }
        associations = self._associations(denominators)
        eligible, blockers = self._gate(denominators)
        return {
            "denominators": denominators,
            "associations": associations,
            "calibration_eligible": eligible,
            "calibration_blockers": blockers,
        }

    def _cohorts(
        self, links: Iterable[RecommendationOutcomeLink]
    ) -> list[OutcomeAssociation]:
        grouped: dict[tuple[str, str, tuple[str, ...]], list[RecommendationOutcomeLink]] = defaultdict(list)
        for link in links:
            grouped[
                (link.vertical_id, link.recommendation_id, tuple(sorted(set(link.service_fit))))
            ].append(link)
        output: list[OutcomeAssociation] = []
        for (vertical, recommendation, services), records in grouped.items():
            aggregate = self._aggregate_links(records)
            output.append(
                OutcomeAssociation(
                    vertical_id=vertical,
                    recommendation_id=recommendation,
                    service_fit=list(services),
                    denominators=aggregate["denominators"],
                    associations=aggregate["associations"],
                    calibration_eligible=aggregate["calibration_eligible"],
                    calibration_blockers=aggregate["calibration_blockers"],
                )
            )
        return output

    @staticmethod
    def _associations(denominators: Mapping[str, int]) -> dict[str, dict[str, Any]]:
        pairs = {
            "approved_to_sent_rate": ("outreach_sent", "approved_packages"),
            "positive_reply_rate": ("positive_replies", "sent_packages"),
            "booked_call_rate": ("booked_calls", "positive_replies"),
            "proposal_rate": ("proposals", "booked_calls"),
            "closed_won_rate": ("closed_won", "proposals"),
            "correction_rate": ("corrections", "approved_packages"),
        }
        result: dict[str, dict[str, Any]] = {}
        for name, (numerator_key, denominator_key) in pairs.items():
            numerator = int(denominators.get(numerator_key, 0))
            denominator = int(denominators.get(denominator_key, 0))
            result[name] = {
                "numerator": numerator,
                "denominator": denominator,
                "value": round(numerator / denominator, 6) if denominator else None,
            }
        return result

    @staticmethod
    def _gate(denominators: Mapping[str, int]) -> tuple[bool, list[str]]:
        observed = {
            "sent_packages": int(denominators.get("sent_packages", 0)),
            "positive_replies": int(denominators.get("positive_replies", 0)),
            "booked_calls": int(denominators.get("booked_calls", 0)),
        }
        blockers = [
            f"{key} requires at least {threshold}; observed {observed[key]}"
            for key, threshold in CALIBRATION_THRESHOLDS.items()
            if observed[key] < threshold
        ]
        return not blockers, blockers


# Public aliases keep the contract discoverable under the names used in the
# P12 plan and by operator-facing callers.
OutcomeCalibrationService = RecommendationOutcomeService
RecommendationOutcomeMemoryService = RecommendationOutcomeService
AgenticOutcomeService = RecommendationOutcomeService


__all__ = [
    "OUTCOME_MEMORY_VERSION",
    "CALIBRATION_THRESHOLDS",
    "OutcomeAssociation",
    "OutcomeCalibrationSummary",
    "RecommendationOutcomeService",
    "OutcomeCalibrationService",
    "RecommendationOutcomeMemoryService",
    "AgenticOutcomeService",
]
