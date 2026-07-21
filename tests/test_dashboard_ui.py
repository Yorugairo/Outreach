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
    assert '<label for="target-url">' in html
    assert '<label for="api-key">' in html
    assert 'id="announcement" role="status" aria-live="polite"' in html
    assert '<table' in html and '<caption>' in html
    assert 'Approve paid enrichment' in html
    assert 'sessionStorage' in html
    assert 'localStorage' not in html
    assert "apiFetch('/api/runs" in html or 'apiFetch(`/api/runs' in html
    assert '@media (max-width: 760px)' in html
    assert ':focus-visible' in html
    assert 'super-secret-value' not in html
    assert 'https://fonts.googleapis.com' not in html
    repo.close()
