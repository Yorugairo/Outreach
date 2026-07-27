from __future__ import annotations

import pytest

from src.models import OutreachActivationEvent, RecommendationOutcomeLink
from src.services.agentic_outcome_service import RecommendationOutcomeService


class FakeOutcomeRepository:
    def __init__(self) -> None:
        self.packages = {}
        self.links: list[RecommendationOutcomeLink] = []
        self.events: list[OutreachActivationEvent] = []

    def get_outreach_package(self, package_id):
        return self.packages.get(package_id)

    def save_recommendation_outcome_link(self, link):
        for existing in self.links:
            if existing.id == link.id and existing.to_dict() != link.to_dict():
                raise ValueError("recommendation outcome links are immutable")
        self.links.append(link)
        return link

    def get_recommendation_outcome_link(self, link_id):
        return next((item for item in self.links if item.id == link_id), None)

    def list_recommendation_outcome_links(
        self, *, prospect_id=None, vertical_id=None, recommendation_id=None, limit=1000
    ):
        records = self.links
        if prospect_id is not None:
            records = [item for item in records if item.prospect_id == prospect_id]
        if vertical_id is not None:
            records = [item for item in records if item.vertical_id == vertical_id]
        if recommendation_id is not None:
            records = [item for item in records if item.recommendation_id == recommendation_id]
        return records[:limit]

    def list_activation_events(self, *, insight_run_id=None, outreach_package_id=None, vertical_id=None, limit=5000):
        records = self.events
        if insight_run_id is not None:
            records = [item for item in records if item.insight_run_id == insight_run_id]
        if outreach_package_id is not None:
            records = [item for item in records if item.outreach_package_id == outreach_package_id]
        if vertical_id is not None:
            records = [item for item in records if item.vertical_id == vertical_id]
        return records[:limit]


def _package(package_id: str = "package-1"):
    return type(
        "Package",
        (),
        {
            "id": package_id,
            "state": "approved",
            "package_version": 1,
            "prospect_id": f"prospect-{package_id}",
            "vertical_pack_version": "national_bjj_registry.v1",
            "insight_run_id": "run-1",
            "recommended_service_package": ["website_seo_vertical_visibility"],
            "approved_findings": [{"id": "rec-trial"}],
        },
    )()


def _event(package, stage: str, *, event_id: str, correction: bool = False):
    return OutreachActivationEvent(
        id=event_id,
        insight_run_id=package.insight_run_id,
        outreach_package_id=package.id,
        package_version=package.package_version,
        stage=stage,
        vertical_id="national_bjj_registry",
        operator="operator",
        service_packages=package.recommended_service_package,
        reason_code="wrong_finding" if correction else None,
    )


def test_link_requires_approved_package_and_is_idempotent() -> None:
    repository = FakeOutcomeRepository()
    package = _package()
    repository.packages[package.id] = package
    service = RecommendationOutcomeService(repository)

    link = service.bind_approved_recommendation(
        recommendation_id="rec-trial",
        source_snapshot_id="decision-snapshot-1",
        outreach_package_id=package.id,
        outreach_package_version=1,
    )
    assert link.prospect_id == package.prospect_id
    assert service.create_link(
        recommendation_id="rec-trial",
        source_snapshot_id="decision-snapshot-1",
        outreach_package_id=package.id,
        outreach_package_version=1,
    ).id == link.id

    with pytest.raises(ValueError, match="immutable"):
        service.bind_approved_recommendation(
            recommendation_id="rec-trial",
            source_snapshot_id="different-snapshot",
            outreach_package_id=package.id,
            outreach_package_version=1,
        )

    package.state = "needs_review"
    with pytest.raises(ValueError, match="approved"):
        service.bind_approved_recommendation(
            recommendation_id="rec-trial",
            source_snapshot_id="another-snapshot",
            outreach_package_id=package.id,
            outreach_package_version=1,
        )


def test_link_rejects_unapproved_recommendation_and_owner_evidence() -> None:
    repository = FakeOutcomeRepository()
    package = _package()
    repository.packages[package.id] = package
    service = RecommendationOutcomeService(repository)

    with pytest.raises(ValueError, match="approved finding"):
        service.bind_approved_recommendation(
            recommendation_id="rec-not-approved",
            source_snapshot_id="snapshot-1",
            outreach_package_id=package.id,
        )

    class OwnerRepository(FakeOutcomeRepository):
        def get_business_fact_ledger_snapshot(self, snapshot_id):
            return type("Snapshot", (), {"run_id": "run-1", "mode": "owner_verified"})()

    owner_repository = OwnerRepository()
    owner_repository.packages[package.id] = package
    with pytest.raises(ValueError, match="owner-mode"):
        RecommendationOutcomeService(owner_repository).bind_approved_recommendation(
            recommendation_id="rec-trial",
            source_snapshot_id="owner-snapshot",
            outreach_package_id=package.id,
        )


def test_event_references_use_immutable_successor_links() -> None:
    repository = FakeOutcomeRepository()
    package = _package()
    repository.packages[package.id] = package
    service = RecommendationOutcomeService(repository)
    link = service.bind_approved_recommendation(
        recommendation_id="rec-trial",
        source_snapshot_id="decision-snapshot-1",
        outreach_package_id=package.id,
    )
    event = _event(package, "outreach_sent", event_id="sent-1")
    repository.events.append(event)

    successor = service.attach_activation_event(link_id=link.id, event_id=event.id)
    assert successor.id != link.id
    assert successor.predecessor_id == link.id
    assert link.activation_event_ids == []
    assert successor.activation_event_ids == [event.id]
    # Re-attaching the same event is idempotent and does not create another
    # mutable history update.
    assert service.attach_activation_event(link_id=successor.id, event_id=event.id).id == successor.id
