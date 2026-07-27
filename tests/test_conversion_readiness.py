from __future__ import annotations

from email.message import Message

from src.fetchers.http_client import SafeHTTPResponse
from src.fetchers.page_fetcher import PageFetcher
from src.models import PageRecord
from src.services.conversion_readiness_service import ConversionReadinessService
from src.services.page_analysis_service import PageAnalysisOutput


def _page(evidence: dict, *, page_class: str = "homepage") -> PageRecord:
    return PageRecord(
        insight_run_id="run-1",
        seo_target_id="target-1",
        url="https://example.com/",
        page_class=page_class,
        fetch_status="fetched",
        http_status=200,
        ai_evidence=evidence,
    )


def _evidence(**overrides):
    evidence = {
        "conversion_evidence_version": "conversion-dom-evidence.v1",
        "offer_signals": ["classes", "program"],
        "cta_links": [{"href": "/trial", "text": "Sign up for a free trial", "kind": "cta"}],
        "schedule_signals": ["schedule"],
        "pricing_signals": ["membership"],
        "eligibility_signals": ["beginner", "adult"],
        "forms": [{"action": "https://example.com/signup", "field_count": 1, "submit_control_count": 1}],
        "phone_numbers": ["555-123-4567"],
        "email_addresses": [],
        "contact_signals": ["call"],
        "trust_signals": ["reviews", "certified"],
        "mobile_viewport": True,
    }
    evidence.update(overrides)
    return evidence


def _check(result, check_id):
    return next(check for check in result.checks if check["check_id"] == check_id)


def test_bjj_conversion_checks_are_vertical_aware_and_deterministic():
    pages = PageAnalysisOutput(pages=[_page(_evidence())])
    first = ConversionReadinessService().build(pages, "national_bjj_registry.v1")
    second = ConversionReadinessService().build(pages, "national_bjj_registry.v1")

    assert first.to_dict() == second.to_dict()
    assert first.version == "conversion-readiness.v1"
    assert first.score == 100
    assert first.status == "complete"
    assert _check(first, "signup_or_lead_capture")["status"] == "measured"
    assert first.metrics["forms_submitted"] is False
    assert first.metrics["funnel_performance_observed"] is False


def test_trade_checks_use_quote_and_service_area_evidence():
    evidence = _evidence(
        offer_signals=["service", "repair"],
        cta_links=[{"href": "/quote", "text": "Request a quote", "kind": "cta"}],
        schedule_signals=["appointment"],
        pricing_signals=["estimate"],
        eligibility_signals=["service area", "licensed"],
        forms=[{"action": "/contact", "field_count": 2, "submit_control_count": 1}],
        trust_signals=["licensed", "insured"],
    )
    result = ConversionReadinessService().build(
        [_page(evidence)], "one_trade_network.v1"
    )
    assert result.score == 100
    assert _check(result, "offer_clarity")["status"] == "measured"
    assert _check(result, "contact_route")["status"] == "measured"


def test_missing_dom_contract_is_unknown_not_a_failure_or_zero_score():
    result = ConversionReadinessService().build(
        PageAnalysisOutput(pages=[_page({})]), "national_bjj_registry"
    )
    assert result.score is None
    assert result.status == "unknown"
    assert all(check["status"] == "unknown" for check in result.checks)
    assert all(check["score"] is None for check in result.checks)
    assert "lead quality" in " ".join(result.warnings).lower()


def test_known_absence_is_a_site_path_issue_but_does_not_claim_funnel_performance():
    result = ConversionReadinessService().build(
        [_page(_evidence(cta_links=[], forms=[], phone_numbers=[], contact_signals=[], trust_signals=[]))],
        "one_trade_network",
    )
    assert _check(result, "next_action")["status"] == "failed"
    assert _check(result, "contact_route")["status"] == "failed"
    rendered = str(result.to_dict()).lower()
    assert "conversion rate" not in rendered
    assert "revenue guarantee" not in rendered


def test_page_fetcher_adds_bounded_conversion_dom_evidence_without_submission():
    body = b"""
    <html><head><meta name='viewport' content='width=device-width'></head><body>
      <h1>Emergency plumbing repair</h1>
      <a href='/quote'>Request a quote</a>
      <form action='/contact' method='post'><input name='email'><button>Send request</button></form>
      <p>Call 555-123-4567. Licensed and insured with 20 years of reviews.</p>
    </body></html>
    """

    class StubHTTP:
        def fetch(self, url, *, allowed_hosts=None):
            headers = Message()
            headers["content-type"] = "text/html"
            return SafeHTTPResponse(
                requested_url=url,
                final_url=url,
                status=200,
                headers=headers,
                body=body,
            )

    evidence = PageFetcher(http_client=StubHTTP()).fetch(
        "https://example.com/", allowed_host="example.com"
    ).ai_evidence
    assert evidence["conversion_evidence_version"] == "conversion-dom-evidence.v1"
    assert evidence["cta_links"][0]["href"] == "https://example.com/quote"
    assert evidence["form_count"] == 1
    assert evidence["forms"][0]["field_count"] == 1
    assert evidence["forms"][0]["submit_control_count"] == 1
    assert evidence["mobile_viewport"] is True
