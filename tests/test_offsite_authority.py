from __future__ import annotations

import json

from src.config import DataForSEOSettings
from src.dataforseo_client import DataForSEOClient
from src.services.offsite_authority_service import (
    OFFSITE_AUTHORITY_METRIC_LABEL,
    OFFSITE_AUTHORITY_VERSION,
    build_offsite_authority_view,
)
from src.services.search_intelligence_service import SearchIntelligenceOutput, TargetContext


def _context() -> TargetContext:
    return TargetContext(
        "https://example.com/",
        "example.com",
        "en",
        "desktop",
        2840,
        "United States",
    )


def _complete_authority() -> dict:
    return {
        "status": "complete",
        "target_domain": "example.com",
        "snapshot_date": "2026-07-25",
        "source": "dataforseo_backlinks_summary_live",
        "rank_scale": "one_hundred",
        "link_rank": 24,
        "backlinks": 120,
        "backlinks_spam_score": 7,
        "target_spam_score": 2,
        "broken_backlinks": 3,
        "broken_pages": 1,
        "referring_domains": 40,
        "referring_domains_nofollow": 10,
        "referring_main_domains": 35,
        "referring_main_domains_nofollow": 8,
        "referring_pages": 100,
        "referring_pages_nofollow": 20,
        "referring_ips": 30,
        "referring_subnets": 25,
        "provider_cost_usd": 0.02,
        "raw_artifact_ref": "raw-authority.json",
    }


def test_authority_view_is_provider_specific_and_not_a_score_dimension():
    output = SearchIntelligenceOutput(
        configured=True,
        approved=True,
        skipped_reason=None,
        payload={"offsite_authority": _complete_authority()},
    )

    view = build_offsite_authority_view(
        output,
        _context(),
        checkpoint_path="checkpoints/attempt/pulling_search_intelligence.json",
    )

    assert view["version"] == OFFSITE_AUTHORITY_VERSION
    assert view["metric_label"] == OFFSITE_AUTHORITY_METRIC_LABEL
    assert view["status"] == "complete"
    assert view["link_rank"] == 24
    assert view["referring_domains_nofollow_percent"] == 25.0
    assert view["referring_pages_nofollow_percent"] == 20.0
    assert "Google Domain Authority" in view["limitations"][0]
    assert "does not change the SEO or AI Readiness scores" in view["limitations"][1]
    assert view["evidence_ref"]["field"] == "payload.payload.offsite_authority"


def test_missing_or_mismatched_authority_is_unknown_not_zero():
    missing = SearchIntelligenceOutput(
        configured=False,
        approved=False,
        skipped_reason="not configured",
        payload={},
    )
    mismatch = SearchIntelligenceOutput(
        configured=True,
        approved=True,
        skipped_reason=None,
        payload={"offsite_authority": {**_complete_authority(), "target_domain": "other.example"}},
    )

    missing_view = build_offsite_authority_view(missing, _context())
    mismatch_view = build_offsite_authority_view(mismatch, _context())

    assert missing_view["status"] == "unknown"
    assert missing_view["link_rank"] is None
    assert mismatch_view["status"] == "unknown"
    assert mismatch_view["backlinks"] is None


def test_dataforseo_backlink_summary_request_and_normalization(tmp_path):
    client = DataForSEOClient(DataForSEOSettings("login", "password"), artifact_dir=tmp_path)
    calls: list[tuple[str, list[dict]]] = []
    response = {
        "tasks": [{
            "status_code": 20000,
            "cost": 0.02003,
            "result": [{
                "target": "example.com",
                "rank": 24,
                "backlinks": 120,
                "backlinks_spam_score": 7,
                "broken_backlinks": 3,
                "broken_pages": 1,
                "referring_domains": 40,
                "referring_domains_nofollow": 10,
                "referring_main_domains": 35,
                "referring_main_domains_nofollow": 8,
                "referring_ips": 30,
                "referring_subnets": 25,
                "referring_pages": 100,
                "referring_pages_nofollow": 20,
                "info": {"target_spam_score": 2},
            }],
        }],
    }

    def fake_post(path, payload):
        calls.append((path, payload))
        artifact = tmp_path / "authority.json"
        artifact.write_text(json.dumps(response), encoding="utf-8")
        client.last_raw_artifact = str(artifact)
        return response

    client.post = fake_post
    result = client.collect_offsite_authority("https://www.example.com/")

    assert calls[0][0] == "/v3/backlinks/summary/live"
    assert calls[0][1] == [{
        "target": "example.com",
        "include_subdomains": True,
        "exclude_internal_backlinks": True,
        "backlinks_status_type": "live",
        "internal_list_limit": 10,
        "rank_scale": "one_hundred",
    }]
    assert result["link_rank"] == 24
    assert result["referring_domains"] == 40
    assert result["provider_cost_usd"] == 0.02003
    assert result["raw_artifact_ref"].endswith("authority.json")


def test_serp_parser_uses_organic_group_rank_and_retains_absolute_position():
    results = DataForSEOClient._extract_serp_results({
        "tasks": [{"result": [{"items": [{
            "type": "organic",
            "rank_group": 13,
            "rank_absolute": 18,
            "url": "https://example.com/classes",
        }]}]}],
    })

    assert results == [{
        "rank": 13,
        "rank_group": 13,
        "rank_absolute": 18,
        "url": "https://example.com/classes",
        "title": None,
        "snippet": None,
        "type": "organic",
    }]
