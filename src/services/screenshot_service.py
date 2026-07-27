"""Bounded browser screenshots with target-host navigation enforcement."""

from __future__ import annotations

import re
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from src.fetchers.http_client import SafeHTTPClient
from src.repositories.base import InsightRepository


class ScreenshotCaptureService:
    DESKTOP_VIEWPORT = {"width": 1440, "height": 900}
    MOBILE_VIEWPORT = {"width": 390, "height": 844}

    def __init__(
        self,
        repository: InsightRepository,
        *,
        timeout_ms: int = 15_000,
        http_client: SafeHTTPClient | None = None,
    ) -> None:
        self.repository = repository
        self.timeout_ms = max(1_000, min(int(timeout_ms), 60_000))
        self.http_client = http_client or SafeHTTPClient()

    def health(self) -> dict[str, Any]:
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            return {
                "status": "unavailable",
                "playwright_installed": False,
                "chromium_installed": False,
                "message": "Install requirements and run `python -m playwright install chromium`.",
            }
        try:
            with sync_playwright() as playwright:
                executable = Path(playwright.chromium.executable_path)
                installed = executable.exists()
                return {
                    "status": "ok" if installed else "degraded",
                    "playwright_installed": True,
                    "chromium_installed": installed,
                    "chromium_executable": str(executable),
                    "message": None if installed else "Run `python -m playwright install chromium`.",
                }
        except Exception as exc:
            return {
                "status": "unavailable",
                "playwright_installed": True,
                "chromium_installed": False,
                "message": f"{type(exc).__name__}: {str(exc)[:240]}",
            }

    def capture(
        self,
        *,
        insight_run_id: str,
        market_run_id: str,
        url: str,
        viewport_name: str,
        caption: str,
        artifact_name: str,
    ) -> dict[str, Any]:
        if viewport_name not in {"desktop", "mobile"}:
            raise ValueError("screenshot viewport must be desktop or mobile")
        allowed_host = (urlsplit(url).hostname or "").casefold().rstrip(".").removeprefix("www.")
        if not allowed_host:
            raise ValueError("screenshot URL requires a host")
        try:
            self.http_client.validate_destination(url, allowed_hosts={allowed_host})
        except Exception as exc:
            return self._failure(url, viewport_name, caption, f"navigation rejected: {type(exc).__name__}: {exc}")
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            return self._failure(url, viewport_name, caption, "Playwright is not installed.")

        viewport = self.DESKTOP_VIEWPORT if viewport_name == "desktop" else self.MOBILE_VIEWPORT
        safe_name = re.sub(r"[^a-zA-Z0-9_.-]+", "-", artifact_name).strip(".-") or "capture"
        if not safe_name.casefold().endswith(".png"):
            safe_name = f"{safe_name}.png"
        timestamp = datetime.now(timezone.utc).isoformat()
        browser = None
        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(headless=True)
                context = browser.new_context(
                    viewport=viewport,
                    device_scale_factor=1,
                    ignore_https_errors=False,
                )
                page = context.new_page()

                def route_request(route) -> None:
                    request = route.request
                    if request.is_navigation_request() and request.frame == page.main_frame:
                        destination = request.url
                        host = (urlsplit(destination).hostname or "").casefold().rstrip(".").removeprefix("www.")
                        if host != allowed_host and not host.endswith(f".{allowed_host}"):
                            route.abort("blockedbyclient")
                            return
                    route.continue_()

                context.route("**/*", route_request)
                response = page.goto(url, wait_until="domcontentloaded", timeout=self.timeout_ms)
                final_url = page.url
                self.http_client.validate_destination(final_url, allowed_hosts={allowed_host})
                png = page.screenshot(type="png", full_page=True, animations="disabled")
                status = response.status if response is not None else None
                context.close()
                browser.close()
                browser = None
            self.repository.save_market_artifact(
                insight_run_id,
                market_run_id,
                f"screenshots/{safe_name}",
                png,
            )
            return {
                "capture_status": "complete",
                "url": url,
                "final_url": final_url,
                "http_status": status,
                "viewport": {"name": viewport_name, **viewport},
                "captured_at": timestamp,
                "artifact_path": f"market/{market_run_id}/screenshots/{safe_name}",
                "sha256": hashlib.sha256(png).hexdigest(),
                "caption": caption,
                "source": "playwright_chromium",
                "participates_in_scoring": False,
            }
        except Exception as exc:
            if browser is not None:
                try:
                    browser.close()
                except Exception:
                    pass
            return self._failure(
                url,
                viewport_name,
                caption,
                f"{type(exc).__name__}: {str(exc)[:400]}",
                captured_at=timestamp,
            )

    @classmethod
    def _failure(
        cls,
        url: str,
        viewport_name: str,
        caption: str,
        message: str,
        *,
        captured_at: str | None = None,
    ) -> dict[str, Any]:
        viewport = cls.DESKTOP_VIEWPORT if viewport_name == "desktop" else cls.MOBILE_VIEWPORT
        return {
            "capture_status": "failed",
            "url": url,
            "final_url": None,
            "http_status": None,
            "viewport": {"name": viewport_name, **viewport},
            "captured_at": captured_at or datetime.now(timezone.utc).isoformat(),
            "artifact_path": None,
            "caption": caption,
            "source": "playwright_chromium",
            "participates_in_scoring": False,
            "error": message,
        }
