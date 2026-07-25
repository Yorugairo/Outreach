from __future__ import annotations

import json
from pathlib import Path

from src.config import DataForSEOSettings, load_config
from src.dataforseo_client import DataForSEOClient
from src.services import search_intelligence_service as search_module
from src.services.search_intelligence_service import (
    SearchIntelligenceService,
    TargetContext,
    validate_target_search_evidence,
)


class FakeSearchClient:
    calls: list[dict] = []

    def __init__(self, settings, artifact_dir=None):
        self.settings = settings
        self.artifact_dir = artifact_dir

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
    assert FakeSearchClient.calls[0]["context"] == context.to_dict()


def test_search_service_honors_configured_paid_call_limit(monkeypatch, tmp_path):
    FakeSearchClient.calls = []
    config = load_config()
    config.dataforseo = DataForSEOSettings("login", "password", max_paid_calls=1)
    config.approval.allow_paid_api_calls = True
    monkeypatch.setattr(search_module, "DataForSEOClient", FakeSearchClient)
    context = TargetContext("https://example.com/", "example.com", "en", "desktop", 2840, "United States")

    output = SearchIntelligenceService(config, artifact_dir=str(tmp_path)).gather(context)

    assert output.approved is True
    assert FakeSearchClient.calls[0]["kwargs"]["serp_limit"] == 0


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
                        "keyword_info": {"search_volume": 100},
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
    assert len(payload["raw_artifact_refs"]) == 2
