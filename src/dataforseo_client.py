from __future__ import annotations

import base64
import json
import re
import time
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path
from typing import Any

from src.config import DataForSEOSettings


class DataForSEOProviderError(RuntimeError):
    """Sanitized transport failure with enough structure for retry policy."""

    def __init__(
        self,
        message: str,
        *,
        http_status: int | None = None,
        response_excerpt: str | None = None,
    ) -> None:
        super().__init__(message)
        self.http_status = http_status
        self.response_excerpt = response_excerpt


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
                last_error = DataForSEOProviderError(
                    f"DataForSEO HTTP {exc.code}",
                    http_status=exc.code,
                    response_excerpt=detail[:1000],
                )
                if exc.code in {401, 402, 403}:
                    break
            except urllib.error.URLError as exc:
                last_error = DataForSEOProviderError(
                    f"DataForSEO request failed: {exc}",
                )
            except json.JSONDecodeError as exc:
                last_error = DataForSEOProviderError(
                    f"Failed to parse DataForSEO JSON response: {exc}",
                )

            if attempt < attempts:
                time.sleep(attempt)

        raise last_error or RuntimeError("Unknown DataForSEO request failure")

    def account_readiness(self) -> dict[str, Any]:
        """Local readiness only; never exposes or validates credential values."""

        return {
            "provider": "dataforseo",
            "configured": self.settings.configured,
            "status": "configured" if self.settings.configured else "credentials_missing",
            "network_check_performed": False,
            "billing_check_performed": False,
        }

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

    def collect_offsite_authority(self, target_domain: str) -> dict[str, Any]:
        """Collect one target-bound backlink summary without inventing a Google metric."""
        normalized_domain = self._normalize_domain(target_domain)
        response = self.post(
            "/v3/backlinks/summary/live",
            [
                {
                    "target": normalized_domain,
                    "include_subdomains": True,
                    "exclude_internal_backlinks": True,
                    "backlinks_status_type": "live",
                    "internal_list_limit": 10,
                    "rank_scale": "one_hundred",
                }
            ],
        )
        raw_artifact_ref = self.last_raw_artifact
        task_error = self._task_error(response)
        if task_error:
            return {
                "status": "unknown",
                "target_domain": normalized_domain,
                "snapshot_date": date.today().isoformat(),
                "source": "dataforseo_backlinks_summary_live",
                "rank_scale": "one_hundred",
                "provider_error": {
                    **task_error,
                    "raw_artifact_ref": raw_artifact_ref,
                },
                "raw_artifact_ref": raw_artifact_ref,
            }
        task = response.get("tasks", [{}])[0]
        results = task.get("result") if isinstance(task, dict) else None
        result = results[0] if isinstance(results, list) and results and isinstance(results[0], dict) else None
        if result is None:
            return {
                "status": "unknown",
                "target_domain": normalized_domain,
                "snapshot_date": date.today().isoformat(),
                "source": "dataforseo_backlinks_summary_live",
                "rank_scale": "one_hundred",
                "provider_error": {
                    "status_code": None,
                    "status_message": "Provider response contained no backlink summary result.",
                    "raw_artifact_ref": raw_artifact_ref,
                },
                "raw_artifact_ref": raw_artifact_ref,
            }
        info = result.get("info") if isinstance(result.get("info"), dict) else {}
        return {
            "status": "complete",
            "target_domain": normalized_domain,
            "snapshot_date": date.today().isoformat(),
            "source": "dataforseo_backlinks_summary_live",
            "rank_scale": "one_hundred",
            "link_rank": result.get("rank"),
            "backlinks": result.get("backlinks"),
            "backlinks_spam_score": result.get("backlinks_spam_score"),
            "target_spam_score": info.get("target_spam_score"),
            "broken_backlinks": result.get("broken_backlinks"),
            "broken_pages": result.get("broken_pages"),
            "referring_domains": result.get("referring_domains"),
            "referring_domains_nofollow": result.get("referring_domains_nofollow"),
            "referring_main_domains": result.get("referring_main_domains"),
            "referring_main_domains_nofollow": result.get("referring_main_domains_nofollow"),
            "referring_pages": result.get("referring_pages"),
            "referring_pages_nofollow": result.get("referring_pages_nofollow"),
            "referring_ips": result.get("referring_ips"),
            "referring_subnets": result.get("referring_subnets"),
            "first_seen": result.get("first_seen"),
            "lost_date": result.get("lost_date"),
            "top_referring_tlds": result.get("referring_links_tld") or {},
            "provider_cost_usd": task.get("cost") if isinstance(task, dict) else None,
            "raw_artifact_ref": raw_artifact_ref,
        }

    def collect_keyword_metrics(
        self,
        keywords: list[str],
        *,
        location_code: int,
        language_code: str,
    ) -> dict[str, Any]:
        """Enrich an operator-supplied set in one Google Ads request."""
        if not keywords or len(keywords) > 1000:
            raise ValueError("keyword metrics require between 1 and 1000 keywords")
        response = self.post(
            "/v3/keywords_data/google_ads/search_volume/live",
            [{
                "keywords": keywords,
                "location_code": location_code,
                "language_code": language_code,
                "include_adult_keywords": False,
            }],
        )
        raw_artifact_ref = self.last_raw_artifact
        task_error = self._task_error(response)
        if task_error:
            return {
                "status": "unknown",
                "source": "dataforseo_keywords_data_google_ads_search_volume_live",
                "snapshot_date": date.today().isoformat(),
                "location_code": location_code,
                "language_code": language_code,
                "items": [],
                "provider_error": task_error,
                "provider_cost_usd": self._task_cost(response),
                "raw_artifact_ref": raw_artifact_ref,
            }
        items: list[dict[str, Any]] = []
        for item in self._result_items(response):
            keyword = item.get("keyword")
            if not isinstance(keyword, str) or not keyword.strip():
                continue
            items.append({
                "keyword": keyword.strip(),
                "search_volume": item.get("search_volume"),
                "cpc": item.get("cpc"),
                "competition": item.get("competition"),
                "competition_index": item.get("competition_index"),
                "monthly_searches": item.get("monthly_searches") if isinstance(item.get("monthly_searches"), list) else [],
            })
        return {
            "status": "complete",
            "source": "dataforseo_keywords_data_google_ads_search_volume_live",
            "snapshot_date": date.today().isoformat(),
            "location_code": location_code,
            "language_code": language_code,
            "items": items,
            "provider_cost_usd": self._task_cost(response),
            "raw_artifact_ref": raw_artifact_ref,
        }

    def collect_organic_serp(
        self,
        keyword: str,
        *,
        location_code: int,
        language_code: str,
        device: str = "desktop",
        depth: int = 100,
    ) -> dict[str, Any]:
        response = self.post(
            "/v3/serp/google/organic/live/advanced",
            [{
                "keyword": keyword,
                "location_code": location_code,
                "language_code": language_code,
                "device": device,
                "os": "windows",
                "depth": max(10, min(int(depth), 100)),
            }],
        )
        error = self._task_error(response)
        return {
            "status": "unknown" if error else "complete",
            "keyword": keyword,
            "source": "dataforseo_serp_google_organic_live_advanced",
            "snapshot_date": date.today().isoformat(),
            "location_code": location_code,
            "language_code": language_code,
            "device": device,
            "results": [] if error else self._extract_serp_results(response),
            "provider_error": error,
            "provider_cost_usd": self._task_cost(response),
            "raw_artifact_ref": self.last_raw_artifact,
        }

    def collect_maps_serp(
        self,
        keyword: str,
        *,
        location_code: int,
        language_code: str,
        device: str = "desktop",
        depth: int = 20,
        latitude: float | None = None,
        longitude: float | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "keyword": keyword,
            "location_code": location_code,
            "language_code": language_code,
            "device": device,
            "os": "windows",
            "depth": max(10, min(int(depth), 100)),
        }
        if latitude is not None or longitude is not None:
            if latitude is None or longitude is None:
                raise ValueError("Maps coordinate binding requires both latitude and longitude")
            if not -90 <= float(latitude) <= 90 or not -180 <= float(longitude) <= 180:
                raise ValueError("Maps coordinates are outside valid latitude/longitude bounds")
            # DataForSEO accepts a coordinate string for point-in-area SERPs;
            # retaining the location code keeps market identity explicit.
            payload["location_coordinate"] = f"{float(latitude):.7f},{float(longitude):.7f}"
        response = self.post(
            "/v3/serp/google/maps/live/advanced",
            [payload],
        )
        error = self._task_error(response)
        results: list[dict[str, Any]] = []
        if not error:
            for item in self._result_items(response):
                rank_group = item.get("rank_group")
                rank_absolute = item.get("rank_absolute")
                rating = item.get("rating") if isinstance(item.get("rating"), dict) else {}
                results.append({
                    "rank": int(rank_group or rank_absolute) if isinstance(rank_group or rank_absolute, int | float) else None,
                    "rank_group": int(rank_group) if isinstance(rank_group, int | float) else None,
                    "rank_absolute": int(rank_absolute) if isinstance(rank_absolute, int | float) else None,
                    "title": item.get("title"),
                    "place_id": item.get("place_id"),
                    "url": item.get("url"),
                    "website": item.get("domain") or item.get("website"),
                    "address": item.get("address"),
                    "phone": item.get("phone"),
                    "rating": rating.get("value") if rating else item.get("rating"),
                    "reviews_count": rating.get("votes_count") if rating else item.get("reviews_count"),
                    "category": item.get("category"),
                    "type": item.get("type"),
                })
        return {
            "status": "unknown" if error else "complete",
            "keyword": keyword,
            "source": "dataforseo_serp_google_maps_live_advanced",
            "snapshot_date": date.today().isoformat(),
            "location_code": location_code,
            "language_code": language_code,
            "device": device,
            "latitude": latitude,
            "longitude": longitude,
            "location_coordinate": payload.get("location_coordinate"),
            "results": results,
            "provider_error": error,
            "provider_cost_usd": self._task_cost(response),
            "raw_artifact_ref": self.last_raw_artifact,
        }

    def collect_maps_serp_at_coordinate(
        self,
        keyword: str,
        *,
        latitude: float,
        longitude: float,
        location_code: int,
        language_code: str,
        device: str = "desktop",
        depth: int = 20,
    ) -> dict[str, Any]:
        """Coordinate-bound Maps sample used by local visibility grids."""

        return self.collect_maps_serp(
            keyword,
            location_code=location_code,
            language_code=language_code,
            device=device,
            depth=depth,
            latitude=latitude,
            longitude=longitude,
        )

    def collect_ai_overview(
        self,
        prompt: str,
        *,
        location_code: int,
        language_code: str,
        device: str = "desktop",
        market: str | None = None,
        topic_id: str | None = None,
        topic_set_id: str | None = None,
        depth: int = 10,
    ) -> dict[str, Any]:
        """Collect one Google AI Overview observation for an approved prompt.

        This adapter only normalizes the provider envelope.  Attribution is
        intentionally performed by ``AIVisibilityService`` so provider output
        cannot alter deterministic readiness scores.
        """

        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("AI visibility prompts must be non-empty")
        response = self.post(
            "/v3/serp/google/ai_overview/live/advanced",
            [{
                "keyword": prompt.strip(),
                "location_code": location_code,
                "language_code": language_code,
                "device": device,
                "os": "windows",
                "depth": max(10, min(int(depth), 100)),
            }],
        )
        error = self._task_error(response)
        items = [] if error else self._result_items(response)
        return {
            "status": "unknown" if error else "complete",
            "prompt": prompt.strip(),
            "topic_id": topic_id,
            "prompt_topic_set_id": topic_set_id,
            "market": market,
            "location_code": location_code,
            "language_code": language_code,
            "device": device,
            "snapshot_date": date.today().isoformat(),
            "items": items,
            "results": items,
            "provider_error": error,
            "provider_cost_usd": self._task_cost(response),
            "raw_artifact_ref": self.last_raw_artifact,
        }

    # Descriptive aliases keep provider fakes and future DataForSEO endpoint
    # naming changes from leaking into the service contract.
    collect_ai_visibility = collect_ai_overview
    collect_ai_serp = collect_ai_overview

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
        entity_name: str | None = None,
        mention_limit: int = 0,
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
        labs_error = self._task_error(labs_response)
        if labs_error:
            raise RuntimeError(
                f"DataForSEO keyword discovery failed: {labs_error['status_code']} {labs_error['status_message']}"
            )
        keywords = self._extract_keywords(labs_response)[:keyword_limit]
        ranking_keywords = self._select_ranking_keywords(keywords, serp_limit)
        serp_snapshots: list[dict[str, Any]] = []
        observed_ranking_urls: list[str] = []
        provider_errors: list[dict[str, Any]] = []
        for keyword_entry in ranking_keywords:
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
            task_error = self._task_error(serp_response)
            if task_error:
                provider_errors.append(
                    {
                        "operation": "ranking_serp",
                        "query": keyword,
                        **task_error,
                        "raw_artifact_ref": self.last_raw_artifact,
                    }
                )
                continue
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
            ranked_target = min(
                target_results,
                key=lambda result: int(result.get("rank") or 10_000),
                default=None,
            )
            rank_absolute = (
                ranked_target.get("rank_absolute")
                if isinstance(ranked_target, dict)
                else None
            )
            if rank is not None:
                for result in target_results:
                    result_url = result.get("url")
                    if result_url and result_url not in observed_ranking_urls:
                        observed_ranking_urls.append(result_url)
            serp_snapshots.append(
                {
                    "keyword": keyword,
                    "rank": rank,
                    "rank_absolute": rank_absolute,
                    "results": results,
                }
            )
        # Every checked query belongs in the denominator. A target result that
        # was not observed in the returned top 100 is evidence of zero sampled
        # visibility, not an unknown query and not proof of universal absence.
        visibility_score = round(
            sum(max(0, 101 - (snapshot["rank"] or 101)) for snapshot in serp_snapshots)
            / len(serp_snapshots),
            2,
        ) if serp_snapshots else None
        external_mentions: list[dict[str, Any]] = []
        mention_candidates: list[dict[str, Any]] = []
        mention_queries: list[str] = []
        if entity_name and mention_limit > 0:
            topic = max(
                keywords,
                key=lambda item: float(item.get("search_volume") or 0),
                default={},
            ).get("keyword")
            topic_terms = self._topic_terms(keywords)
            candidates = [f'"{entity_name}" -site:{target_domain}']
            if topic:
                candidates.append(f'"{entity_name}" "{topic}" -site:{target_domain}')
            for query in candidates[:mention_limit]:
                mention_queries.append(query)
                response = self.post(
                    "/v3/serp/google/organic/live/advanced",
                    [{
                        "keyword": query,
                        "location_code": location_code,
                        "language_code": language_code,
                        "device": device,
                        "os": "windows",
                        "depth": 20,
                    }],
                )
                if self.last_raw_artifact:
                    raw_refs.append(self.last_raw_artifact)
                mention_artifact = self.last_raw_artifact
                task_error = self._task_error(response)
                if task_error:
                    provider_errors.append(
                        {
                            "operation": "external_mention_serp",
                            "query": query,
                            **task_error,
                            "raw_artifact_ref": mention_artifact,
                        }
                    )
                    continue
                for result in self._extract_serp_results(response):
                    if self._url_in_domain(result.get("url"), target_domain):
                        continue
                    haystack = f"{result.get('title') or ''} {result.get('snippet') or ''}".casefold()
                    if entity_name.casefold() not in haystack:
                        continue
                    result_url = str(result.get("url") or "")
                    candidate = {
                        **result,
                        "domain": self._normalize_domain(result_url),
                        "query": query,
                        "snapshot_date": date.today().isoformat(),
                        "market": market,
                        "source": "dataforseo_serp_google_organic_live_advanced",
                        "exact_name_match": True,
                        "topic_match": self._text_matches_topic(haystack, topic_terms),
                        "raw_artifact_ref": mention_artifact,
                    }
                    mention_candidates.append(candidate)
                    if candidate["topic_match"]:
                        external_mentions.append(candidate)
        else:
            topic_terms = self._topic_terms(keywords)
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
            "entity_name": entity_name,
            "mention_queries": mention_queries,
            "external_mentions": external_mentions,
            "mention_candidates": mention_candidates,
            "topic_terms": topic_terms,
            "provider_errors": provider_errors,
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
            intent = data.get("search_intent_info") or {}
            properties = data.get("keyword_properties") or {}
            output.append(
                {
                    "keyword": keyword.strip(),
                    "search_volume": info.get("search_volume"),
                    "competition": info.get("competition"),
                    "competition_level": info.get("competition_level"),
                    "cpc": info.get("cpc"),
                    "intent": intent.get("main_intent"),
                    "core_keyword": properties.get("core_keyword"),
                }
            )
        return output

    @staticmethod
    def _select_ranking_keywords(
        keywords: list[dict[str, Any]],
        limit: int,
    ) -> list[dict[str, Any]]:
        """Balance provider relevance, demand, and commercial intent."""
        if limit <= 0 or not keywords:
            return []
        selected: list[dict[str, Any]] = []

        def add(item: dict[str, Any] | None) -> None:
            if item is not None and item not in selected and len(selected) < limit:
                selected.append(item)

        add(keywords[0])
        add(max(keywords, key=lambda item: float(item.get("search_volume") or 0)))
        commercial = [
            item
            for item in keywords
            if str(item.get("intent") or "").casefold() in {"commercial", "transactional"}
        ]
        add(max(commercial, key=lambda item: float(item.get("search_volume") or 0), default=None))
        for item in keywords:
            add(item)
        return selected

    @staticmethod
    def _extract_serp_results(response: dict[str, Any]) -> list[dict[str, Any]]:
        output: list[dict[str, Any]] = []
        for item in DataForSEOClient._result_items(response):
            url = item.get("url")
            if not isinstance(url, str) or not url.strip():
                continue
            rank_group = item.get("rank_group")
            rank_absolute = item.get("rank_absolute")
            # Organic group position is the customer-facing Google ranking.
            # Absolute position includes non-organic SERP features and remains
            # secondary evidence.
            rank = rank_group if rank_group is not None else rank_absolute
            output.append(
                {
                    "rank": int(rank) if isinstance(rank, int | float) else None,
                    "rank_group": int(rank_group) if isinstance(rank_group, int | float) else None,
                    "rank_absolute": int(rank_absolute) if isinstance(rank_absolute, int | float) else None,
                    "url": url.strip(),
                    "title": item.get("title"),
                    "snippet": item.get("description"),
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
    def _task_error(response: dict[str, Any]) -> dict[str, Any] | None:
        tasks = response.get("tasks")
        if not isinstance(tasks, list) or not tasks or not isinstance(tasks[0], dict):
            return {
                "status_code": response.get("status_code"),
                "status_message": response.get("status_message") or "Provider response contained no task.",
            }
        task = tasks[0]
        status_code = task.get("status_code")
        if status_code == 20000 or (
            status_code is None and isinstance(task.get("result"), list)
        ):
            return None
        return {
            "status_code": status_code,
            "status_message": task.get("status_message") or "Provider task failed.",
        }

    @staticmethod
    def _task_cost(response: dict[str, Any]) -> float:
        tasks = response.get("tasks")
        if not isinstance(tasks, list) or not tasks or not isinstance(tasks[0], dict):
            return 0.0
        value = tasks[0].get("cost")
        if isinstance(value, bool) or not isinstance(value, int | float):
            return 0.0
        return max(0.0, float(value))

    @staticmethod
    def _topic_terms(keywords: list[dict[str, Any]]) -> list[str]:
        stopwords = {
            "academy", "classes", "class", "faq", "instructor", "near", "the",
            "and", "for", "from", "with", "stops", "shoplifter", "tactics",
        }
        terms: set[str] = set()
        for item in keywords:
            values = (item.get("keyword"), item.get("core_keyword"))
            for value in values:
                for token in re.findall(r"[a-z0-9]+", str(value or "").casefold()):
                    if len(token) >= 3 and token not in stopwords:
                        terms.add(token)
        return sorted(terms)

    @staticmethod
    def _text_matches_topic(text: str, topic_terms: list[str]) -> bool:
        tokens = set(re.findall(r"[a-z0-9]+", text.casefold()))
        return bool(tokens.intersection(topic_terms))

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
