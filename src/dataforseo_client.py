from __future__ import annotations

import base64
import json
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from src.config import DataForSEOSettings


class DataForSEOClient:
    def __init__(self, settings: DataForSEOSettings, artifact_dir: str | Path | None = None):
        settings.require_credentials()
        self.settings = settings
        self.artifact_dir = Path(artifact_dir) if artifact_dir else Path("artifacts") / "dataforseo_raw"
        self.artifact_dir.mkdir(parents=True, exist_ok=True)

    def _headers(self) -> dict[str, str]:
        token = base64.b64encode(
            f"{self.settings.login}:{self.settings.password}".encode("utf-8")
        ).decode("ascii")
        return {
            "Authorization": f"Basic {token}",
            "Content-Type": "application/json",
            "User-Agent": "OutreachProgram/0.1",
        }

    def _request(self, method: str, path: str, payload: dict[str, Any] | list[dict[str, Any]] | None = None) -> dict[str, Any]:
        url = f"{self.settings.api_base.rstrip('/')}/{path.lstrip('/')}"
        data = None
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")

        attempts = 3
        last_error: Exception | None = None
        for attempt in range(1, attempts + 1):
            req = urllib.request.Request(url, data=data, headers=self._headers(), method=method.upper())
            try:
                with urllib.request.urlopen(req, timeout=self.settings.timeout_seconds) as response:
                    body = response.read().decode("utf-8", "ignore")
                    parsed = json.loads(body)
                    self._persist_raw(path, parsed)
                    return parsed
            except urllib.error.HTTPError as exc:
                detail = exc.read().decode("utf-8", "ignore")
                last_error = RuntimeError(f"DataForSEO HTTP {exc.code}: {detail[:1000]}")
            except urllib.error.URLError as exc:
                last_error = RuntimeError(f"DataForSEO request failed: {exc}")
            except json.JSONDecodeError as exc:
                last_error = RuntimeError(f"Failed to parse DataForSEO JSON response: {exc}")

            if attempt < attempts:
                time.sleep(attempt)

        raise last_error or RuntimeError("Unknown DataForSEO request failure")

    def _persist_raw(self, path: str, payload: dict[str, Any]) -> None:
        timestamp = int(time.time())
        safe_name = path.strip("/").replace("/", "__") or "root"
        out_path = self.artifact_dir / f"{timestamp}_{safe_name}.json"
        out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def get(self, path: str) -> dict[str, Any]:
        return self._request("GET", path)

    def post(self, path: str, payload: dict[str, Any] | list[dict[str, Any]]) -> dict[str, Any]:
        return self._request("POST", path, payload)

    def get_errors_reference(self) -> dict[str, Any]:
        return self.get("/v3/appendix/errors")

    def post_dataforseo_labs_locations(self) -> dict[str, Any]:
        return self.post("/v3/dataforseo_labs/google/locations_and_languages", [])
