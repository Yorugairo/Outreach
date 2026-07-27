from src.fetchers.http_client import SafeHTTPClient
from src.repositories.file_repository import FileBackedInsightRepository
from src.services.screenshot_service import ScreenshotCaptureService


def test_screenshot_rejects_private_resolution_before_browser_launch(tmp_path):
    client = SafeHTTPClient(
        resolver=lambda host, port: [(None, None, None, None, ("127.0.0.1", port))]
    )
    service = ScreenshotCaptureService(
        FileBackedInsightRepository(tmp_path),
        http_client=client,
    )
    result = service.capture(
        insight_run_id="run",
        market_run_id="market",
        url="https://competitor.example",
        viewport_name="desktop",
        caption="Evidence only.",
        artifact_name="blocked.png",
    )
    assert result["capture_status"] == "failed"
    assert "private or reserved" in result["error"]
    assert result["artifact_path"] is None


def test_market_artifact_cannot_escape_run_scope(tmp_path):
    repository = FileBackedInsightRepository(tmp_path)
    try:
        repository.save_market_artifact("run", "market", "../escape.json", {"unsafe": True})
    except ValueError as exc:
        assert "safe and relative" in str(exc)
    else:
        raise AssertionError("unsafe market artifact path was accepted")
