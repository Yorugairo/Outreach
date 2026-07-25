from __future__ import annotations

import base64
import json
import time
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path
from typing import Any

from src.config import DataForSEOSettings


class DataForSEOClient:
    def __init__(self, settings: DataForSEOSettings, artifact_dir: str | Path | None = None):
        settings.require_credentials()
        self.settings = settings
        self.artifact_dir = Path(artifact_dir) if artifact_dir else Path("artifacts") / "dataforseo_raw"
        self.artifact_dir.mkdir(parents=True, exist_ok=True)
        self.last_raw_artifact: str | None = None

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
                    self.last_raw_artifact = self._persist_raw(path, parsed)
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

    def _persist_raw(self, path: str, payload: dict[str, Any]) -> str:
        timestamp = int(time.time() * 1000)
        safe_name = path.strip("/").replace("/", "__") or "root"
        out_path = self.artifact_dir / f"{timestamp}_{safe_name}.json"
        suffix = 1
        while out_path.exists():
            out_path = self.artifact_dir / f"{timestamp}_{suffix}_{safe_name}.json"
            suffix += 1
        out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return str(out_path)

    def get(self, path: str) -> dict[str, Any]:
        return self._request("GET", path)

    def post(self, path: str, payload: dict[str, Any] | list[dict[str, Any]]) -> dict[str, Any]:
        return self._request("POST", path, payload)

    def get_errors_reference(self) -> dict[str, Any]:
        return self.get("/v3/appendix/errors")

    def post_dataforseo_labs_locations(self) -> dict[str, Any]:
        return self.post("/v3/dataforseo_labs/google/locations_and_languages", [])

    def collect_target_search_evidence(
        self,
        target_context: Any,
        *,
        location_code: int,
        language_code: str,
        device: str,
        market: str,
        keyword_limit: int = 10,
        serp_limit: int = 5,
    ) -> dict[str, Any]:
        target_domain = self._normalize_domain(str(target_context.target_domain))
        labs_response = self.post(
            "/v3/dataforseo_labs/google/keywords_for_site/live",
            [
                {
                    "target": target_domain,
                    "location_code": location_code,
                    "language_code": language_code,
                    "include_serp_info": False,
                    "limit": keyword_limit,
                }
            ],
        )
        raw_refs = [self.last_raw_artifact] if self.last_raw_artifact else []
        keywords = self._extract_keywords(labs_response)[:keyword_limit]
        serp_snapshots: list[dict[str, Any]] = []
        observed_ranking_urls: list[str] = []
        ranks: list[int] = []
        for keyword_entry in keywords[:serp_limit]:
            keyword = keyword_entry["keyword"]
            serp_response = self.post(
                "/v3/serp/google/organic/live/advanced",
                [
                    {
                        "keyword": keyword,
                        "location_code": location_code,
                        "language_code": language_code,
                        "device": device,
                        "os": "windows",
                        "depth": 100,
                    }
                ],
            )
            if self.last_raw_artifact:
                raw_refs.append(self.last_raw_artifact)
            results = self._extract_serp_results(serp_response)
            target_results = [
                result
                for result in results
                if self._url_in_domain(result.get("url"), target_domain)
            ]
            rank = min(
                (int(result["rank"]) for result in target_results if result.get("rank") is not None),
                default=None,
            )
            if rank is not None:
                ranks.append(rank)
                for result in target_results:
                    result_url = result.get("url")
                    if result_url and result_url not in observed_ranking_urls:
                        observed_ranking_urls.append(result_url)
            serp_snapshots.append(
                {
                    "keyword": keyword,
                    "rank": rank,
                    "results": results,
                }
            )
        visibility_score = round(
            sum(max(0, 101 - rank) for rank in ranks) / len(ranks),
            2,
        ) if ranks else 0.0
        return {
            "target_domain": target_domain,
            "snapshot_date": date.today().isoformat(),
            "language_code": language_code,
            "device": device,
            "location_code": location_code,
            "market": market,
            "source": "dataforseo_labs_google_keywords_for_site + dataforseo_serp_google_organic_live_advanced",
            "keywords": keywords,
            "serp_snapshots": serp_snapshots,
            "observed_ranking_urls": observed_ranking_urls,
            "visibility_score": visibility_score,
            "raw_artifact_refs": raw_refs,
        }

    @staticmethod
    def _extract_keywords(response: dict[str, Any]) -> list[dict[str, Any]]:
        items = DataForSEOClient._result_items(response)
        output: list[dict[str, Any]] = []
        for item in items:
            data = item.get("keyword_data") or item
            keyword = data.get("keyword")
            if not isinstance(keyword, str) or not keyword.strip():
                continue
            info = data.get("keyword_info") or {}
            output.append(
                {
                    "keyword": keyword.strip(),
                    "search_volume": info.get("search_volume"),
                    "competition": info.get("competition"),
                }
            )
        return output

    @staticmethod
    def _extract_serp_results(response: dict[str, Any]) -> list[dict[str, Any]]:
        output: list[dict[str, Any]] = []
        for item in DataForSEOClient._result_items(response):
            url = item.get("url")
            if not isinstance(url, str) or not url.strip():
                continue
            rank = item.get("rank_absolute") or item.get("rank_group")
            output.append(
                {
                    "rank": int(rank) if isinstance(rank, int | float) else None,
                    "url": url.strip(),
                    "title": item.get("title"),
                    "type": item.get("type"),
                }
            )
        return output

    @staticmethod
    def _result_items(response: dict[str, Any]) -> list[dict[str, Any]]:
        tasks = response.get("tasks")
        if not isinstance(tasks, list) or not tasks:
            return []
        result = tasks[0].get("result") if isinstance(tasks[0], dict) else None
        if not isinstance(result, list) or not result:
            return []
        items = result[0].get("items") if isinstance(result[0], dict) else None
        return items if isinstance(items, list) else []

    @staticmethod
    def _normalize_domain(value: str) -> str:
        value = value.strip().casefold().rstrip(".")
        if "://" in value:
            from urllib.parse import urlsplit

            value = (urlsplit(value).hostname or "").casefold().rstrip(".")
        return value.removeprefix("www.")

    @staticmethod
    def _url_in_domain(url: Any, target_domain: str) -> bool:
        if not isinstance(url, str):
            return False
        from urllib.parse import urlsplit

        host = DataForSEOClient._normalize_domain(urlsplit(url).hostname or "")
        return host == target_domain or host.endswith(f".{target_domain}")
