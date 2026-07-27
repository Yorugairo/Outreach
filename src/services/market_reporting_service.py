"""Immutable market snapshot and combined operator report assembly."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from src.models import InsightReport, MarketEvidenceRun
from src.repositories.base import InsightRepository


class MarketReportingService:
    REPORTABLE_STATES = {"partial", "complete"}

    def __init__(self, repository: InsightRepository) -> None:
        self.repository = repository

    def assemble(self, market_run_id: str) -> dict[str, InsightReport]:
        market_run = self.repository.get_market_evidence_run(market_run_id)
        if market_run is None:
            raise ValueError(f"market evidence run not found: {market_run_id}")
        if market_run.state not in self.REPORTABLE_STATES:
            raise ValueError("market reports require completed pilot competitor enrichment")
        run = self.repository.get_run(market_run.insight_run_id)
        if run is None or run.status != "completed":
            raise ValueError("market reports require a completed core insight run")
        seo = self.repository.get_report(run.id, "v2")
        ai = self.repository.get_report(run.id, "ai-v2") or self.repository.get_report(run.id, "ai-v1")
        if seo is None:
            raise ValueError("combined market reporting requires the existing v2 SEO report")

        predecessor = (
            self.repository.get_market_evidence_run(
                market_run.predecessor_market_run_id
            )
            if market_run.predecessor_market_run_id
            else None
        )
        market_payload = self._market_payload(
            market_run,
            predecessor=predecessor,
        )
        market_markdown = self._market_markdown(market_payload)
        market_report = InsightReport(
            insight_run_id=run.id,
            seo_target_id=run.seo_target_id,
            attempt_id=run.attempt_id,
            report_version="market-v1",
            report_status="complete" if market_run.state == "complete" else "partial",
            headline=f"Tacoma competitive opportunity evidence for {market_run.target_domain}",
            executive_summary=self._market_summary(market_payload),
            key_actions=list(market_run.recommended_gaps),
            report_payload=market_payload,
            export_json=market_payload,
            export_markdown=market_markdown,
        )
        combined_payload = self._combined_payload(market_run, seo, ai, market_payload)
        combined_markdown = self._combined_markdown(combined_payload)
        combined_report = InsightReport(
            insight_run_id=run.id,
            seo_target_id=run.seo_target_id,
            attempt_id=run.attempt_id,
            report_version="v3",
            report_status=market_report.report_status,
            headline=f"SEO, AI, and Tacoma market opportunity — {market_run.target_domain}",
            executive_summary=combined_payload["executive_summary"]["answer"],
            key_actions=list(market_run.recommended_gaps),
            report_payload=combined_payload,
            export_json=combined_payload,
            export_markdown=combined_markdown,
        )

        # Keep canonical readers convenient while also preserving immutable,
        # market-run-scoped snapshots when a later deep run supersedes a pilot.
        self.repository.save_report(market_report)
        self.repository.save_report(combined_report)
        for report in (market_report, combined_report):
            self.repository.save_market_artifact(
                run.id,
                market_run.id,
                f"reports/{report.report_version}.json",
                report.to_dict(),
            )
            if report.export_markdown:
                self.repository.save_market_artifact(
                    run.id,
                    market_run.id,
                    f"reports/{report.report_version}.md",
                    report.export_markdown.encode("utf-8"),
                )
        return {"market-v1": market_report, "v3": combined_report}

    @staticmethod
    def _market_payload(
        market_run: MarketEvidenceRun,
        *,
        predecessor: MarketEvidenceRun | None = None,
    ) -> dict[str, Any]:
        snapshot = market_run.to_dict()
        digest = hashlib.sha256(
            json.dumps(snapshot, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        ).hexdigest()
        return {
            "report_contract": "market-v1",
            "market_run_id": market_run.id,
            "market_snapshot_sha256": digest,
            "state": market_run.state,
            "phase": market_run.phase,
            "target_domain": market_run.target_domain,
            "target_entity_name": market_run.target_entity_name,
            "vertical_id": market_run.vertical_id,
            "market": market_run.market,
            "location_code": market_run.location_code,
            "language_code": market_run.language_code,
            "device": market_run.device,
            "provider": {
                "contract_version": market_run.provider_contract_version,
                "call_count": len(market_run.provider_calls),
                "call_cap": market_run.provider_call_cap,
                "actual_cost_usd": market_run.actual_provider_cost,
                "historical_predecessor_cost_usd": (
                    predecessor.actual_provider_cost if predecessor else 0.0
                ),
                "retry_cost_usd": (
                    market_run.actual_provider_cost
                    if market_run.recovery_operation == "resume_unresolved"
                    else 0.0
                ),
                "total_attributable_cost_usd": round(
                    market_run.actual_provider_cost
                    + (
                        predecessor.actual_provider_cost
                        if predecessor
                        else 0.0
                    ),
                    6,
                ),
                "clean_run_ceiling_usd": (
                    MarketReportingService._provider_ceiling(
                        market_run.provider_completeness
                    )
                ),
                "completeness": market_run.provider_completeness,
                "predecessor_market_run_id": (
                    market_run.predecessor_market_run_id
                ),
                "recovery_operation": market_run.recovery_operation,
                "calls": market_run.provider_calls,
            },
            "inventory": {
                "keyword_metrics": len(market_run.keyword_metrics),
                "organic_checks": len(market_run.organic_evidence),
                "maps_checks": len(market_run.maps_evidence),
                "approved_competitors": len(market_run.approved_competitors),
                "competitor_pages": sum(
                    int(item.get("pages_collected") or 0)
                    for item in market_run.competitor_evidence
                ),
                "screenshots": len([
                    item for item in market_run.screenshots
                    if item.get("capture_status") == "complete"
                ]),
            },
            "keyword_metrics": market_run.keyword_metrics,
            "organic_rankings": market_run.organic_evidence,
            "maps_rankings": market_run.maps_evidence,
            "search_visibility": MarketReportingService._artifact_payload(
                market_run, "search_visibility"
            ),
            "local_visibility": MarketReportingService._artifact_payload(
                market_run, "local_visibility"
            ),
            "competitor_candidates": market_run.competitor_candidates,
            "approved_competitors": market_run.approved_competitors,
            "competitor_evidence": market_run.competitor_evidence,
            "gap_matrix": market_run.gap_matrix,
            "recommended_actions": market_run.recommended_gaps,
            "screenshots": market_run.screenshots,
            "limitations": market_run.evidence_limits,
            "scoring_separation": (
                "Market and competitor evidence is an explanatory overlay and does not change "
                "the target SEO overall score or AI Readiness score."
            ),
        }

    @staticmethod
    def _artifact_payload(market_run: MarketEvidenceRun, kind: str) -> dict[str, Any] | None:
        """Return the latest immutable visibility payload attached to a run."""

        for item in reversed(market_run.artifact_refs or []):
            if isinstance(item, dict) and item.get("kind") == kind:
                payload = item.get("payload")
                if isinstance(payload, dict):
                    return payload
                # Local grid collection stores metrics alongside the artifact
                # identity when no report object is available yet.
                metrics = item.get("metrics")
                if isinstance(metrics, dict):
                    return {
                        "surface": "local_visibility" if kind == "local_visibility" else "search_visibility",
                        "version": "local-visibility.v1" if kind == "local_visibility" else "search-visibility.v2",
                        "status": "partial",
                        "metrics": metrics,
                    }
        return None

    @staticmethod
    def _provider_ceiling(completeness: dict[str, Any]) -> float | None:
        expected = completeness.get("expected") if isinstance(completeness, dict) else None
        if not isinstance(expected, dict):
            return None
        total = 0.0
        for operation, count in expected.items():
            if not isinstance(count, int) or count < 0:
                return None
            total += count * (0.10 if operation == "keyword_metrics" else 0.02)
        return round(total, 6)

    @staticmethod
    def _combined_payload(
        market_run: MarketEvidenceRun,
        seo: InsightReport,
        ai: InsightReport | None,
        market: dict[str, Any],
    ) -> dict[str, Any]:
        seo_payload = seo.report_payload
        ai_payload = ai.report_payload if ai else {}
        scorecard = seo_payload.get("scorecard") if isinstance(seo_payload.get("scorecard"), dict) else {}
        return {
            "report_contract": "v3",
            "source_versions": {
                "seo": seo.report_version,
                "ai": ai.report_version if ai else None,
                "market": "market-v1",
                "market_run_id": market_run.id,
            },
            "executive_summary": {
                "answer": MarketReportingService._combined_summary(
                    scorecard.get("overall_score"),
                    ai_payload.get("score"),
                    market,
                ),
                "seo_score": scorecard.get("overall_score"),
                "ai_readiness_score": ai_payload.get("score"),
                "ai_readiness_status": ai_payload.get("status"),
                "market_state": market_run.state,
                "market_phase": market_run.phase,
                "top_opportunities": market_run.recommended_gaps[:3],
            },
            "seo": seo_payload,
            "ai_readiness": ai_payload or {
                "status": "unknown",
                "limitations": ["AI Readiness report is unavailable for this legacy run."],
            },
            "tacoma_rankings": {
                "organic": market["organic_rankings"],
                "keyword_metrics": market["keyword_metrics"],
            },
            "search_visibility": market.get("search_visibility"),
            "local_visibility": market.get("local_visibility"),
            "local_pack_evidence": market["maps_rankings"],
            "competitor_gap_matrix": market["gap_matrix"],
            "offsite_authority": {
                "target": seo_payload.get("offsite_authority"),
                "competitors": [
                    {
                        "domain": item.get("domain"),
                        "authority": item.get("offsite_authority"),
                    }
                    for item in market["competitor_evidence"]
                ],
                "metric_disclaimer": (
                    "DataForSEO Link Rank is provider-specific evidence; it is not "
                    "Google Domain Authority or an exposed Google PageRank value."
                ),
            },
            "screenshot_comparison": market["screenshots"],
            "recommended_actions": market["recommended_actions"][:3],
            "service_fit": [
                {
                    "keyword": item.get("keyword"),
                    "service_fit": item.get("service_fit"),
                }
                for item in market["recommended_actions"][:3]
            ],
            "limitations": [
                *market["limitations"],
                {
                    "kind": "market_sample",
                    "message": (
                        "Rankings are dated Tacoma/device samples. Not observed means absent "
                        "from the returned sample, not proof of universal non-ranking."
                    ),
                },
            ],
            "market_snapshot_sha256": market["market_snapshot_sha256"],
        }

    @staticmethod
    def _market_summary(payload: dict[str, Any]) -> str:
        action_count = len(payload.get("recommended_actions", []))
        inventory = payload["inventory"]
        return (
            f"The {payload['phase']} Tacoma sample checked {inventory['organic_checks']} organic "
            f"queries and {inventory['maps_checks']} Maps queries, compared "
            f"{inventory['approved_competitors']} approved competitor(s), and produced "
            f"{action_count} evidence-backed priority action(s)."
        )

    @staticmethod
    def _combined_summary(seo_score: Any, ai_score: Any, market: dict[str, Any]) -> str:
        actions = market.get("recommended_actions", [])
        teaser = actions[0].get("observation") if actions else "No supported competitive gap was prioritized."
        return (
            f"SEO score {seo_score if seo_score is not None else 'unknown'}; "
            f"AI Readiness {ai_score if ai_score is not None else 'unknown'}; "
            f"Tacoma evidence: {teaser}"
        )

    @staticmethod
    def _market_markdown(payload: dict[str, Any]) -> str:
        lines = [
            f"# Tacoma competitive opportunity — {payload['target_domain']}",
            "",
            "## Executive summary",
            MarketReportingService._market_summary(payload),
            "",
            "## Tacoma rankings",
            f"- Organic checks: {payload['inventory']['organic_checks']}",
            f"- Keyword demand rows: {payload['inventory']['keyword_metrics']}",
            f"- Provider evidence unresolved: {sum(payload['provider'].get('completeness', {}).get('unresolved', {}).values()) if payload['provider'].get('completeness') else 'Unknown'}",
            f"- Provider cost: ${payload['provider']['actual_cost_usd']:.6f}",
        ]
        for row in payload["organic_rankings"]:
            position = row.get("target_rank")
            lines.append(f"- {row.get('keyword')}: {position if position is not None else 'not observed in sampled top 100'}")
        lines.extend(["", "## Local-pack evidence"])
        for row in payload["maps_rankings"]:
            position = row.get("target_rank")
            lines.append(f"- {row.get('keyword')}: {position if position is not None else 'not observed in returned Maps sample'}")
        if payload.get("search_visibility"):
            lines.extend(["", "## Search Visibility v2"])
            visibility = payload["search_visibility"]
            metrics = visibility.get("metrics", {}) if isinstance(visibility, dict) else {}
            lines.append(f"- Tracked coverage: {metrics.get('tracked_keyword_coverage', metrics.get('tracked_keyword_coverage_percent', 'unknown'))}%")
            lines.append(f"- Weighted visibility: {metrics.get('weighted_visibility', 'unknown')}")
        if payload.get("local_visibility"):
            lines.extend(["", "## Local Visibility grid"])
            local = payload["local_visibility"]
            metrics = local.get("metrics", {}) if isinstance(local, dict) else {}
            lines.append(f"- Grid completeness: {metrics.get('completeness_percent', 'unknown')}%")
            lines.append(f"- Top-10 coverage: {metrics.get('top_10_coverage', metrics.get('top_10_coverage_percent', 'unknown'))}%")
        lines.extend(["", "## Competitor gap matrix"])
        for row in payload["gap_matrix"]:
            classes = ", ".join(row.get("opportunity_classes", [])) or "no supported class"
            lines.append(f"- {row.get('keyword')}: {classes}")
        lines.extend(["", "## Three recommended actions"])
        for index, action in enumerate(payload["recommended_actions"][:3], start=1):
            lines.append(f"{index}. {action.get('recommended_action')} ({action.get('keyword')})")
        lines.extend([
            "",
            "## Screenshots",
        ])
        for item in payload["screenshots"]:
            lines.append(f"- {item.get('caption')} — {item.get('artifact_path') or item.get('error')}")
        lines.extend([
            "",
            "## Limitations",
            "- Market evidence does not change target SEO or AI Readiness scoring.",
            "- Positions are dated market/device observations and are not ranking guarantees.",
        ])
        for item in payload["limitations"]:
            lines.append(f"- {item.get('message') or item.get('kind')}")
        return "\n".join(lines) + "\n"

    @staticmethod
    def _combined_markdown(payload: dict[str, Any]) -> str:
        summary = payload["executive_summary"]
        lines = [
            "# Combined SEO, AI, and Tacoma opportunity report",
            "",
            "## Executive summary",
            summary["answer"],
            "",
            "## SEO",
            f"- Overall score: {summary.get('seo_score') if summary.get('seo_score') is not None else 'Unknown'}",
            "",
            "## AI Readiness",
            f"- Score: {summary.get('ai_readiness_score') if summary.get('ai_readiness_score') is not None else 'Unknown'}",
            f"- Status: {summary.get('ai_readiness_status') or 'Unknown'}",
            "",
            "## Tacoma rankings",
        ]
        for row in payload["tacoma_rankings"]["organic"]:
            position = row.get("target_rank")
            lines.append(f"- {row.get('keyword')}: {position if position is not None else 'not observed in sampled top 100'}")
        lines.extend(["", "## Local-pack evidence"])
        for row in payload["local_pack_evidence"]:
            position = row.get("target_rank")
            lines.append(f"- {row.get('keyword')}: {position if position is not None else 'not observed in returned Maps sample'}")
        lines.extend(["", "## Competitor gap matrix"])
        for row in payload["competitor_gap_matrix"]:
            lines.append(f"- {row.get('keyword')}: {', '.join(row.get('opportunity_classes', [])) or 'no supported class'}")
        lines.extend([
            "",
            "## Off-site authority",
            f"- {payload['offsite_authority']['metric_disclaimer']}",
            "",
            "## Screenshot comparison",
        ])
        for item in payload["screenshot_comparison"]:
            lines.append(f"- {item.get('caption')} — {item.get('artifact_path') or item.get('error')}")
        lines.extend(["", "## Three recommended actions"])
        for index, action in enumerate(payload["recommended_actions"], start=1):
            lines.append(f"{index}. {action.get('recommended_action')}")
        lines.extend(["", "## Service fit"])
        for item in payload["service_fit"]:
            lines.append(f"- {item.get('keyword')}: {', '.join(item.get('service_fit') or [])}")
        lines.extend(["", "## Limitations"])
        for item in payload["limitations"]:
            lines.append(f"- {item.get('message') or item.get('kind')}")
        return "\n".join(lines) + "\n"
