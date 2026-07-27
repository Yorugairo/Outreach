from __future__ import annotations

import json
from pathlib import Path

from src.config import DataForSEOSettings, load_config
from src.dataforseo_client import DataForSEOClient
from src.services import search_intelligence_service as search_module
from src.services.search_intelligence_service import (
    SearchIntelligenceService,
    TargetContext,
    build_search_evidence_view,
    corroborated_external_mentions,
    validate_target_search_evidence,
)


class FakeSearchClient:
    calls: list[dict] = []

    def __init__(self, settings, artifact_dir=None):
        self.settings = settings
        self.artifact_dir = artifact_dir
        self.last_raw_artifact = None

    def collect_offsite_authority(self, target_domain):
        self.calls.append({"authority_target": target_domain})
        return {
            "status": "complete",
            "target_domain": target_domain,
            "snapshot_date": "2026-07-25",
            "source": "dataforseo_backlinks_summary_live",
            "rank_scale": "one_hundred",
            "link_rank": 12,
            "backlinks": 20,
            "referring_domains": 8,
        }

    def collect_target_search_evidence(self, context, **kwargs):
        self.calls.append({"context": context.to_dict(), "kwargs": kwargs})
        return {
            "target_domain": context.target_domain,
            "snapshot_date": "2026-07-25",
            "language_code": context.language_code,
            "device": context.device,
            "location_code": context.location_code or 2840,
            "market": context.market or "United States",
            "source": "fixture-dataforseo",
            "observed_ranking_urls": ["https://example.com/services"],
            "visibility_score": 98.0,
            "raw_artifact_refs": ["artifacts/dataforseo_raw/fixture.json"],
        }


def test_load_config_accepts_explicit_local_env_without_printing_values(tmp_path, monkeypatch):
    for key in (
        "DATAFORSEO_LOGIN",
        "DATAFORSEO_PASSWORD",
        "DATAFORSEO_DEFAULT_LOCATION_CODE",
        "DATAFORSEO_DEFAULT_LANGUAGE_CODE",
        "SEO_INSIGHTS_ALLOW_PAID_API_CALLS",
    ):
        monkeypatch.delenv(key, raising=False)
    dotenv = tmp_path / "local.env"
    dotenv.write_text(
        "DATAFORSEO_LOGIN=test-login\n"
        "DATAFORSEO_PASSWORD=test-password\n"
        "DATAFORSEO_DEFAULT_LOCATION_CODE=2840\n"
        "DATAFORSEO_DEFAULT_LANGUAGE_CODE=en\n"
        "SEO_INSIGHTS_ALLOW_PAID_API_CALLS=true\n",
        encoding="utf-8",
    )

    config = load_config(dotenv)

    assert config.dataforseo.configured is True
    assert config.dataforseo.default_location_code == 2840
    assert config.approval.allow_paid_api_calls is True


def test_search_service_blocks_configured_but_unapproved_paid_calls(monkeypatch):
    config = load_config()
    config.dataforseo = DataForSEOSettings("login", "password")
    config.approval.allow_paid_api_calls = False
    monkeypatch.setattr(search_module, "DataForSEOClient", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("must not call")))

    output = SearchIntelligenceService(config).gather(
        TargetContext("https://example.com/", "example.com", "en", "desktop", 2840, "United States")
    )

    assert output.configured is True
    assert output.approved is False
    assert "explicit operator approval" in (output.skipped_reason or "")


def test_search_service_collects_and_binds_target_context(monkeypatch, tmp_path):
    FakeSearchClient.calls = []
    config = load_config()
    config.dataforseo = DataForSEOSettings("login", "password")
    config.approval.allow_paid_api_calls = True
    monkeypatch.setattr(search_module, "DataForSEOClient", FakeSearchClient)
    context = TargetContext("https://example.com/", "example.com", "en", "desktop", 2840, "United States")

    output = SearchIntelligenceService(config, artifact_dir=str(tmp_path)).gather(context)

    assert output.configured is True
    assert output.approved is True
    assert output.requested_context == context.to_dict()
    assert output.payload["target_domain"] == "example.com"
    assert validate_target_search_evidence(output, context) == 98.0
    assert FakeSearchClient.calls[0]["authority_target"] == "example.com"
    assert FakeSearchClient.calls[1]["context"] == context.to_dict()


def test_search_service_honors_configured_paid_call_limit(monkeypatch, tmp_path):
    FakeSearchClient.calls = []
    config = load_config()
    config.dataforseo = DataForSEOSettings("login", "password", max_paid_calls=1)
    config.approval.allow_paid_api_calls = True
    monkeypatch.setattr(search_module, "DataForSEOClient", FakeSearchClient)
    context = TargetContext("https://example.com/", "example.com", "en", "desktop", 2840, "United States")

    output = SearchIntelligenceService(config, artifact_dir=str(tmp_path)).gather(context)

    assert output.approved is True
    assert FakeSearchClient.calls == [{"authority_target": "example.com"}]
    assert output.payload["offsite_authority"]["link_rank"] == 12


def test_search_service_reserves_authority_and_one_validated_entity_mention(monkeypatch, tmp_path):
    FakeSearchClient.calls = []
    config = load_config()
    config.dataforseo = DataForSEOSettings("login", "password", max_paid_calls=6)
    config.approval.allow_paid_api_calls = True
    monkeypatch.setattr(search_module, "DataForSEOClient", FakeSearchClient)
    context = TargetContext(
        "https://example.com/",
        "example.com",
        "en",
        "desktop",
        2840,
        "United States",
        "Example Co",
        "organization_json_ld",
    )

    SearchIntelligenceService(config, artifact_dir=str(tmp_path)).gather(context)

    assert FakeSearchClient.calls[0]["authority_target"] == "example.com"
    assert FakeSearchClient.calls[1]["kwargs"]["serp_limit"] == 3
    assert FakeSearchClient.calls[1]["kwargs"]["mention_limit"] == 1
    assert FakeSearchClient.calls[1]["kwargs"]["entity_name"] == "Example Co"


def test_target_evidence_rejects_urls_outside_bound_target():
    config = load_config()
    config.dataforseo = DataForSEOSettings("login", "password")
    output = search_module.SearchIntelligenceOutput(
        configured=True,
        approved=True,
        skipped_reason=None,
        requested_context=None,
        payload={
            "target_domain": "example.com",
            "snapshot_date": "2026-07-25",
            "language_code": "en",
            "device": "desktop",
            "location_code": 2840,
            "market": "United States",
            "source": "fixture",
            "observed_ranking_urls": ["https://other.example/services"],
            "visibility_score": 50,
        },
    )

    assert validate_target_search_evidence(
        output,
        TargetContext("https://example.com/", "example.com", "en", "desktop", 2840, "United States"),
    ) is None


def test_dataforseo_client_binds_endpoint_payloads_and_persists_raw_refs(tmp_path):
    client = DataForSEOClient(DataForSEOSettings("login", "password"), artifact_dir=tmp_path)
    calls: list[tuple[str, list[dict]]] = []
    labs = {
        "tasks": [{
            "result": [{
                "items": [{
                    "keyword_data": {
                        "keyword": "example services",
                        "keyword_info": {"search_volume": 100, "cpc": 4.25},
                        "search_intent_info": {"main_intent": "commercial"},
                    }
                }]
            }]
        }]
    }
    serp = {
        "tasks": [{
            "result": [{
                "items": [{
                    "type": "organic",
                    "rank_absolute": 3,
                    "url": "https://example.com/services",
                    "title": "Example Services",
                }]
            }]
        }]
    }

    def fake_post(path, payload):
        calls.append((path, payload))
        artifact = tmp_path / f"raw-{len(calls)}.json"
        artifact.write_text(json.dumps({"path": path}), encoding="utf-8")
        client.last_raw_artifact = str(artifact)
        return labs if "keywords_for_site" in path else serp

    client.post = fake_post
    payload = client.collect_target_search_evidence(
        TargetContext("https://example.com/", "example.com", "en", "desktop", 2840, "United States"),
        location_code=2840,
        language_code="en",
        device="desktop",
        market="United States",
        keyword_limit=10,
        serp_limit=5,
    )

    assert [path for path, _ in calls] == [
        "/v3/dataforseo_labs/google/keywords_for_site/live",
        "/v3/serp/google/organic/live/advanced",
    ]
    assert calls[0][1][0]["target"] == "example.com"
    assert calls[0][1][0]["location_code"] == 2840
    assert calls[1][1][0]["keyword"] == "example services"
    assert calls[1][1][0]["device"] == "desktop"
    assert payload["observed_ranking_urls"] == ["https://example.com/services"]
    assert payload["serp_snapshots"][0]["rank"] == 3
    assert payload["visibility_score"] == 98.0
    assert payload["keywords"][0]["intent"] == "commercial"
    assert payload["keywords"][0]["cpc"] == 4.25
    assert len(payload["raw_artifact_refs"]) == 2


def test_ranking_query_selection_balances_relevance_demand_and_commercial_intent():
    keywords = [
        {"keyword": "provider first", "search_volume": 10, "intent": "informational"},
        {"keyword": "highest demand", "search_volume": 5000, "intent": "informational"},
        {"keyword": "commercial winner", "search_volume": 900, "intent": "commercial"},
        {"keyword": "other commercial", "search_volume": 20, "intent": "commercial"},
    ]

    selected = DataForSEOClient._select_ranking_keywords(keywords, 3)

    assert [item["keyword"] for item in selected] == [
        "provider first",
        "highest demand",
        "commercial winner",
    ]


def test_sampled_top_100_non_observation_is_valid_zero_visibility(tmp_path):
    client = DataForSEOClient(DataForSEOSettings("login", "password"), artifact_dir=tmp_path)
    labs = {
        "tasks": [{"result": [{"items": [{
            "keyword_data": {
                "keyword": "bjj academy near me",
                "keyword_info": {"search_volume": 90},
                "search_intent_info": {"main_intent": "commercial"},
            }
        }]}]}]
    }
    competitor_serp = {
        "tasks": [{"result": [{"items": [{
            "type": "organic",
            "rank_absolute": 1,
            "url": "https://competitor.example/programs",
            "title": "Competitor Academy",
        }]}]}]
    }

    def fake_post(path, payload):
        artifact = tmp_path / f"raw-{len(list(tmp_path.glob('raw-*.json'))) + 1}.json"
        artifact.write_text("{}", encoding="utf-8")
        client.last_raw_artifact = str(artifact)
        return labs if "keywords_for_site" in path else competitor_serp

    client.post = fake_post
    context = TargetContext("https://example.com/", "example.com", "en", "desktop", 2840, "United States")
    payload = client.collect_target_search_evidence(
        context,
        location_code=2840,
        language_code="en",
        device="desktop",
        market="United States",
        serp_limit=1,
    )
    output = search_module.SearchIntelligenceOutput(
        configured=True,
        approved=True,
        skipped_reason=None,
        requested_context=context.to_dict(),
        payload=payload,
    )
    view = build_search_evidence_view(
        output,
        context,
        checkpoint_path="checkpoints/attempt-1/pulling_search_intelligence.json",
    )

    assert validate_target_search_evidence(output, context) == 0.0
    assert view["status"] == "complete"
    assert view["ranking_checks"] == 1
    assert view["ranked_count"] == 0
    assert view["not_observed_count"] == 1
    assert view["keywords"][0]["opportunity_band"] == "not_observed_top_100"
    assert view["keywords"][0]["observed_url"] is None
    assert view["serp_landscape"][0]["results"][0]["domain"] == "competitor.example"


def test_provider_task_failures_are_partial_evidence_not_negative_observations():
    context = TargetContext("https://example.com/", "example.com", "en", "desktop", 2840, "United States")
    output = search_module.SearchIntelligenceOutput(
        configured=True,
        approved=True,
        skipped_reason=None,
        requested_context=context.to_dict(),
        payload={
            "target_domain": "example.com",
            "snapshot_date": "2026-07-25",
            "language_code": "en",
            "device": "desktop",
            "location_code": 2840,
            "market": "United States",
            "source": "fixture",
            "keywords": [{"keyword": "example service", "search_volume": 100}],
            "serp_snapshots": [{"keyword": "example service", "rank": 5, "results": [
                {"rank": 5, "url": "https://example.com/service", "title": "Example"}
            ]}],
            "observed_ranking_urls": ["https://example.com/service"],
            "visibility_score": 96.0,
            "mention_queries": ['"Example" -site:example.com'],
            "external_mentions": [],
            "provider_errors": [{
                "operation": "external_mention_serp",
                "query": '"Example" -site:example.com',
                "status_code": 40101,
                "status_message": "Internal SE Server Error.",
            }],
            "raw_artifact_refs": ["keyword.json", "rank.json", "mention.json"],
        },
    )

    view = build_search_evidence_view(output, context)

    assert view["status"] == "partial"
    assert view["visibility_score"] == 96.0
    assert view["not_observed_count"] == 0
    assert "failed" in view["limitations"][0]


def test_keyword_only_provider_evidence_is_limited_and_never_a_zero_score():
    context = TargetContext(
        "https://example.com/",
        "example.com",
        "en",
        "desktop",
        2840,
        "United States",
    )
    output = search_module.SearchIntelligenceOutput(
        configured=True,
        approved=True,
        skipped_reason=None,
        requested_context=context.to_dict(),
        payload={
            "target_domain": "example.com",
            "snapshot_date": "2026-07-25",
            "language_code": "en",
            "device": "desktop",
            "location_code": 2840,
            "market": "United States",
            "source": "fixture",
            "keywords": [{"keyword": "example service", "search_volume": 100}],
            "serp_snapshots": [],
            "observed_ranking_urls": [],
            "visibility_score": None,
            "provider_errors": [{
                "operation": "organic_serp",
                "query": "example service",
                "status_message": "Provider budget exhausted.",
            }],
        },
    )

    view = build_search_evidence_view(output, context)

    assert validate_target_search_evidence(output, context) is None
    assert view["status"] == "limited"
    assert view["evidence_state"] == "keyword_only"
    assert view["visibility_score"] is None
    assert view["ranking_checks"] == 0
    assert view["keyword_count"] == 1
    assert "no Google organic SERP queries" in view["limitations"][0]


def test_dataforseo_mentions_use_serp_results_without_fetching_third_party_pages(tmp_path):
    client = DataForSEOClient(DataForSEOSettings("login", "password"), artifact_dir=tmp_path)
    calls: list[tuple[str, list[dict]]] = []
    labs = {
        "tasks": [{"result": [{"items": [{
            "keyword_data": {
                "keyword": "plumbing service",
                "keyword_info": {"search_volume": 50},
            }
        }]}]}]
    }
    mention_serp = {
        "tasks": [{"result": [{"items": [{
            "type": "organic",
            "rank_absolute": 2,
            "url": "https://industry.example/directory",
            "title": "Example Co plumbing service directory profile",
            "description": "Details about Example Co.",
        }]}]}]
    }

    def fake_post(path, payload):
        calls.append((path, payload))
        artifact = tmp_path / f"mention-{len(calls)}.json"
        artifact.write_text("{}", encoding="utf-8")
        client.last_raw_artifact = str(artifact)
        return labs if "keywords_for_site" in path else mention_serp

    client.post = fake_post
    payload = client.collect_target_search_evidence(
        TargetContext("https://example.com/", "example.com", "en", "desktop", 2840),
        location_code=2840,
        language_code="en",
        device="desktop",
        market="United States",
        keyword_limit=10,
        serp_limit=0,
        entity_name="Example Co",
        mention_limit=2,
    )

    assert len(calls) == 3
    assert all(path.startswith("/v3/") for path, _ in calls)
    assert len(payload["external_mentions"]) == 2
    assert all(item["exact_name_match"] is True for item in payload["external_mentions"])
    assert all(item["topic_match"] is True for item in payload["external_mentions"])


def test_market_provider_endpoints_bind_tacoma_and_normalize_costs(tmp_path):
    client = DataForSEOClient(DataForSEOSettings("login", "password"), artifact_dir=tmp_path)
    calls = []
    metrics = {
        "tasks": [{
            "cost": 0.05,
            "result": [{"items": [{
                "keyword": "bjj tacoma",
                "search_volume": 320,
                "cpc": 4.5,
                "competition": 0.7,
                "competition_index": 71,
            }]}],
        }]
    }
    organic = {
        "tasks": [{
            "cost": 0.002,
            "result": [{"items": [{
                "type": "organic",
                "rank_group": 3,
                "rank_absolute": 5,
                "url": "https://novaryu.com/program",
                "title": "Nova Ryu",
            }]}],
        }]
    }
    maps = {
        "tasks": [{
            "cost": 0.004,
            "result": [{"items": [{
                "type": "maps_search",
                "rank_group": 2,
                "rank_absolute": 2,
                "title": "Nova Ryu",
                "place_id": "place-nova",
                "domain": "https://novaryu.com",
                "address": "Tacoma, WA",
                "rating": {"value": 4.9, "votes_count": 42},
            }]}],
        }]
    }

    def fake_post(path, payload):
        calls.append((path, payload))
        artifact = tmp_path / f"market-{len(calls)}.json"
        artifact.write_text("{}", encoding="utf-8")
        client.last_raw_artifact = str(artifact)
        if "search_volume" in path:
            return metrics
        if "/maps/" in path:
            return maps
        return organic

    client.post = fake_post
    metric_result = client.collect_keyword_metrics(
        ["bjj tacoma"],
        location_code=1027773,
        language_code="en",
    )
    organic_result = client.collect_organic_serp(
        "bjj tacoma",
        location_code=1027773,
        language_code="en",
        device="desktop",
    )
    maps_result = client.collect_maps_serp(
        "bjj tacoma",
        location_code=1027773,
        language_code="en",
        device="desktop",
    )

    assert [path for path, _ in calls] == [
        "/v3/keywords_data/google_ads/search_volume/live",
        "/v3/serp/google/organic/live/advanced",
        "/v3/serp/google/maps/live/advanced",
    ]
    assert all(payload[0]["location_code"] == 1027773 for _, payload in calls)
    assert calls[0][1][0]["keywords"] == ["bjj tacoma"]
    assert metric_result["items"][0]["search_volume"] == 320
    assert metric_result["provider_cost_usd"] == 0.05
    assert organic_result["results"][0]["rank"] == 3
    assert organic_result["results"][0]["rank_absolute"] == 5
    assert maps_result["results"][0]["place_id"] == "place-nova"
    assert maps_result["results"][0]["rating"] == 4.9
    assert maps_result["results"][0]["reviews_count"] == 42
    assert maps_result["provider_cost_usd"] == 0.004


def test_external_corroboration_excludes_ambiguous_exact_name_results():
    output = search_module.SearchIntelligenceOutput(
        configured=True,
        approved=True,
        skipped_reason=None,
        payload={
            "keywords": [
                {"keyword": "bjj academy"},
                {"keyword": "mma classes"},
            ],
            "external_mentions": [
                {
                    "title": "Nova Ryu BJJ",
                    "snippet": "Martial arts academy",
                    "exact_name_match": True,
                },
                {
                    "title": "  NOVA RYU BJJ ",
                    "snippet": "Second result for the same academy",
                    "exact_name_match": True,
                },
                {
                    "title": "NovaRyu - World of Warcraft character",
                    "snippet": "Gaming profile",
                    "exact_name_match": True,
                },
            ],
        },
    )

    corroborated = corroborated_external_mentions(output)

    assert [item["title"] for item in corroborated] == ["Nova Ryu BJJ"]
