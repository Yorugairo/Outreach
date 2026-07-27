from __future__ import annotations

import pytest

from src.repositories.file_repository import FileBackedInsightRepository
from src.services.screenshot_service import ScreenshotCaptureService


def test_screenshot_contract_is_bounded_and_non_scoring(tmp_path):
    service = ScreenshotCaptureService(
        FileBackedInsightRepository(tmp_path),
        timeout_ms=1,
    )
    assert service.timeout_ms == 1_000
    failed = service._failure(
        "https://example.test",
        "mobile",
        "Visual context only.",
        "browser unavailable",
    )
    assert failed["viewport"] == {
        "name": "mobile",
        **ScreenshotCaptureService.MOBILE_VIEWPORT,
    }
    assert failed["participates_in_scoring"] is False
    assert failed["artifact_path"] is None

    with pytest.raises(ValueError, match="desktop or mobile"):
        service.capture(
            insight_run_id="run-1",
            market_run_id="market-1",
            url="https://example.test",
            viewport_name="tablet",
            caption="Invalid viewport.",
            artifact_name="invalid.png",
        )
