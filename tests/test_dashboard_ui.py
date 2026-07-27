from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from src.api.app import create_app
from src.repositories.sqlite_repository import SQLiteInsightRepository


def test_operator_dashboard_is_accessible_responsive_and_api_driven(tmp_path: Path):
    artifact_root = tmp_path / "artifacts"
    repo = SQLiteInsightRepository(tmp_path / "seo-insights.db", artifact_root=artifact_root)
    app = create_app(
        repository=repo,
        artifact_root=artifact_root,
        api_key="super-secret-value",
        environment="test",
    )

    with TestClient(app) as client:
        response = client.get("/")

    html = response.text
    assert response.status_code == 200
    assert '<a class="skip-link" href="#main-content">Skip to main content</a>' in html
    assert '<main id="main-content"' in html
    assert '<nav aria-label="Primary navigation">' in html
    assert '<form id="run-form"' in html
    assert 'Website opportunity scan' in html
    assert 'Analyze website' in html
    assert '<details class="run-options">' in html
    assert '<details id="operator-tools" class="operator-tools">' in html
    assert html.index('<form id="run-form"') < html.index('id="operator-tools"')
    assert '<details id="operator-tools" class="operator-tools" open' not in html
    assert '<form id="prospect-form"' in html
    assert 'id="market-tools"' in html
    assert 'id="opportunity-tools"' in html
    assert 'id="vertical-agentic-tools"' in html
    assert html.index('id="market-tools"') < html.index('id="opportunity-tools"')
    assert html.index('id="opportunity-tools"') < html.index('id="packages"')
    assert 'id="keyword-file"' in html
    assert 'Run 12-keyword pilot' in html
    assert 'Approve selected competitors' in html
    assert 'Deepen to approved 50-keyword set' in html
    assert 'value="v3"' in html
    assert 'value="v4"' in html
    assert 'value="v6"' in html
    assert "Demand-to-revenue opportunity case" in html
    assert "Forecast, not guarantee" in html
    assert "monthly search occasions" in html
    assert "not unique people" in html
    assert 'id="demand-file"' in html
    assert 'id="economics-capacity"' in html
    assert 'id="opportunity-assumptions"' in html
    assert "Build opportunity case" in html
    assert "Resume unresolved paid evidence" in html
    assert 'id="calibration-file"' in html
    assert '<label for="target-url">' in html
    assert '<label for="prospect-csv">' in html
    assert '<label for="api-key">' in html
    assert 'Manual outreach funnel' in html
    assert 'id="announcement" role="status" aria-live="polite"' in html
    assert '<table' in html and '<caption>' in html
    assert "operator's bounded paid-search policy" in html
    assert 'id="approve-paid"' not in html
    assert 'value="100"' in html
    assert "/ai-readiness" in html
    assert "/product-strength" in html
    assert "/agentic-analysis/preflight" in html
    assert "/agentic-evidence/preflight" in html
    assert "/owner-agentic-analysis" in html
    assert "/remediation-blueprints" in html
    assert "decision-intelligence-v1" in html
    assert "Forms, downloads, authentication, purchases, messages, and personal-data entry are prohibited." in html
    assert "/client-bundles" in html
    assert "/api/owned-measurements/csv-preview" in html
    assert "/api/demand-trends/csv-preview" in html
    assert 'id="demand-conversion-mode"' in html
    assert 'id="owner-consent-confirmed"' in html
    assert 'id="conversion-event-map-json"' in html
    assert "/demand-conversion" in html
    assert "Demand and conversion evidence" in html
    assert "Keywords and Google rankings" in html
    assert "Off-site authority" in html
    assert "DataForSEO Link Rank" in html
    assert "Google Domain Authority" in html
    assert "Organic position" in html
    assert "Overall SERP position" in html
    assert "Not observed in sampled top 100" in html
    assert "provider calls" in html
    assert "AI Readiness" in html
    assert "Technical SEO Health" in html
    assert "Conversion Readiness" in html
    assert "Observed AI Visibility" in html
    assert "Evidence Confidence, formulas, and limitations" in html
    assert "Local Visibility heatmap" in html
    assert "Run agent analysis" in html
    assert "Create client report" in html
    assert "Request GPT review" in html
    assert "Client report history" in html
    assert "Immutable aggregate owner measurement" in html
    assert "['AEO', ai.dimensions?.aeo?.score]" in html
    assert "ai.presentation_label" in html
    assert "acknowledge_partial_ai" in html
    assert 'sessionStorage' in html
    assert 'localStorage' not in html
    assert "apiFetch('/api/runs" in html or 'apiFetch(`/api/runs' in html
    assert "apiFetch('/api/prospects/csv-preview" in html
    assert "apiFetch('/api/funnel" in html
    assert "/market-evidence/pilot" in html
    assert "/competitors/approve" in html
    assert "/api/demand-evidence/csv-preview" in html
    assert "/opportunity-scenarios" in html
    assert "/api/calibration/csv-preview" in html
    assert "/pitch-pack" in html
    assert "/resume" in html
    assert "actual provider cost" in html
    assert "provider completeness" in html
    assert '@media (max-width: 760px)' in html
    assert ':focus-visible' in html
    assert 'super-secret-value' not in html
    assert 'https://fonts.googleapis.com' not in html
    repo.close()
