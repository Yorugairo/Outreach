from __future__ import annotations

from src.services.agentic_outcome_service import (
    MIN_BOOKED_CALLS,
    MIN_POSITIVE_REPLIES,
    MIN_SENT_PACKAGES,
    RecommendationOutcomeService,
)
from src.services.recommendation_priority_service import RecommendationPriorityService

from tests.test_agentic_outcome_links import (
    FakeOutcomeRepository,
    _event,
    _package,
)


def _seed_link(service, repository, package, index: int):
    repository.packages[package.id] = package
    link = service.bind_approved_recommendation(
        recommendation_id="rec-trial",
        source_snapshot_id=f"decision-{index}",
        outreach_package_id=package.id,
    )
    repository.events.append(_event(package, "package_approved", event_id=f"approved-{index}"))
    repository.events.append(_event(package, "outreach_sent", event_id=f"sent-{index}"))
    return link


def test_small_sample_is_descriptive_and_cannot_produce_calibration_rates():
    repository = FakeOutcomeRepository()
    service = RecommendationOutcomeService(repository)
    package = _package()
    _seed_link(service, repository, package, 1)

    summary = service.summarize(vertical_id="national_bjj_registry")
    assert summary["denominators"]["sent_packages"] == 1
    assert summary["associations"]["positive_reply_rate"]["denominator"] == 1
    assert summary["calibration_eligible"] is False
    assert any("sent_packages" in reason for reason in summary["calibration_blockers"])
    rates = service.calibrated_outcome_rates(vertical_id="national_bjj_registry")
    assert rates["__calibration_eligible__"] is False
    assert all(not key.startswith("rec-") for key in rates)

    priority = RecommendationPriorityService().score(
        {"id": "rec-trial", "severity": "high", "confidence": "high"},
        outcome_rates=rates,
    )
    assert priority["priority_components"]["recorded_outcomes"] is None
    # A caller cannot bypass the gate with an unversioned/plain rate mapping.
    unmarked = RecommendationPriorityService().score(
        {"id": "rec-trial", "severity": "high", "confidence": "high"},
        outcome_rates={"rec-trial": 1.0},
    )
    assert unmarked["priority_components"]["recorded_outcomes"] is None


def test_gate_opens_only_after_all_vertical_sample_thresholds():
    repository = FakeOutcomeRepository()
    service = RecommendationOutcomeService(repository)
    for index in range(1, MIN_SENT_PACKAGES + 1):
        package = _package(f"package-{index}")
        # Keep each package tied to its own prospect while retaining the same
        # vertical/service/finding cohort.
        package.prospect_id = f"prospect-{index}"
        _seed_link(service, repository, package, index)
        if index <= MIN_POSITIVE_REPLIES:
            repository.events.append(_event(package, "positive_reply", event_id=f"reply-{index}"))
        if index <= MIN_BOOKED_CALLS:
            repository.events.append(_event(package, "call_booked", event_id=f"call-{index}"))
    # One factual correction is retained in history and counted separately.
    repository.events.append(_event(package, "correction_recorded", event_id="correction-1", correction=True))

    summary = service.summarize(vertical_id="national_bjj_registry")
    assert summary["calibration_eligible"] is True
    assert summary["denominators"] == {
        "approved_packages": MIN_SENT_PACKAGES,
        "sent_packages": MIN_SENT_PACKAGES,
        "positive_replies": MIN_POSITIVE_REPLIES,
        "booked_calls": MIN_BOOKED_CALLS,
        "proposals": 0,
        "closed_won": 0,
        "closed_lost": 0,
        "corrections": 1,
    }
    assert summary["associations"]["positive_reply_rate"] == {
        "numerator": MIN_POSITIVE_REPLIES,
        "denominator": MIN_SENT_PACKAGES,
        "value": 0.25,
    }

    rates = service.calibrated_outcome_rates(vertical_id="national_bjj_registry")
    assert rates["__calibration_eligible__"] is True
    assert rates["rec-trial"]["numerator"] == MIN_POSITIVE_REPLIES
    priority = RecommendationPriorityService().score(
        {"id": "rec-trial", "severity": "high", "confidence": "high"},
        outcome_rates=rates,
    )
    assert priority["priority_components"]["recorded_outcomes"] == 25.0


def test_similar_cases_are_vertical_service_finding_compatible_and_aggregate_only():
    repository = FakeOutcomeRepository()
    service = RecommendationOutcomeService(repository)
    for index in range(1, 4):
        package = _package(f"package-{index}")
        package.prospect_id = f"prospect-{index}"
        _seed_link(service, repository, package, index)

    result = service.similar_cases(
        vertical_id="national_bjj_registry",
        service_fit=["website_seo_vertical_visibility"],
        recommendation_id="rec-trial",
    )
    assert result["aggregate_only"] is True
    assert result["compatible_case_count"] == 3
    assert "prospect_id" not in result
    assert "outreach_package_id" not in result
    assert result["associations"]["positive_reply_rate"]["denominator"] == 3
    assert "causation" in result["association_disclaimer"]
