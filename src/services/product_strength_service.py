"""Compose the URL-first product-strength view from immutable report evidence."""

from __future__ import annotations

from typing import Any

from src.models import ReportAlias, ReportSnapshot, canonical_sha256


class ProductStrengthService:
    CONTRACT_VERSION = "product-strength.v1"
    RENDERER_VERSION = "product-strength-composer.v1"

    def __init__(self, repository: Any) -> None:
        self.repository = repository

    def assemble(self, run_id: str) -> dict[str, Any]:
        run = self.repository.get_run(run_id)
        if run is None:
            raise ValueError(f"run {run_id} not found")
        versions = {
            "technical_seo_health": ("seo-health-v2",),
            "ai_readiness": ("ai-v3", "ai-v2", "ai-v1"),
            "conversion_readiness": ("conversion-v1",),
            "legacy_seo": ("v2", "v1"),
            "market_evidence": ("market-v1",),
            "demand_opportunity": ("opportunity-v1",),
        }
        reports: dict[str, Any] = {}
        selected_versions: dict[str, str] = {}
        for surface, candidates in versions.items():
            report = next(
                (
                    candidate
                    for version in candidates
                    if (candidate := self.repository.get_report(run_id, version))
                    is not None
                ),
                None,
            )
            if report is not None:
                reports[surface] = report
                selected_versions[surface] = report.report_version

        v2_payload = (
            reports["legacy_seo"].report_payload
            if "legacy_seo" in reports
            else {}
        )
        limitations: list[str] = []
        for surface in (
            "technical_seo_health",
            "ai_readiness",
            "conversion_readiness",
        ):
            report = reports.get(surface)
            if report is None:
                limitations.append(f"{surface.replace('_', ' ')} is unavailable for this run.")
                continue
            payload = report.report_payload
            limitations.extend(
                str(item)
                for item in payload.get("warnings", [])
                if str(item).strip()
            )
        payload = {
            "contract_version": self.CONTRACT_VERSION,
            "run_id": run.id,
            "attempt_id": run.attempt_id,
            "normalized_domain": run.requested_domain,
            "normalized_url": run.requested_url,
            "headline": f"Website opportunity report — {run.requested_domain}",
            "executive_summary": (
                "A bounded view of technical SEO health, AI readiness, "
                "conversion readiness, observed visibility, and evidence limits."
            ),
            "technical_seo_health": self._surface(reports.get("technical_seo_health")),
            "ai_readiness": self._surface(reports.get("ai_readiness")),
            "conversion_readiness": self._surface(reports.get("conversion_readiness")),
            "search_visibility": v2_payload.get(
                "search_visibility",
                {"status": "unknown", "score": None},
            ),
            "offsite_authority": v2_payload.get(
                "offsite_authority",
                {"status": "unknown", "score": None},
            ),
            "observed_ai_visibility": {
                "status": "unknown",
                "score": None,
                "completeness_percent": 0.0,
                "warning": (
                    "No approved prompt/topic observation snapshot is bound "
                    "to this run."
                ),
            },
            "market_evidence": self._surface(reports.get("market_evidence")),
            "demand_opportunity": self._surface(reports.get("demand_opportunity")),
            "selected_report_versions": selected_versions,
            "limitations": sorted(set(limitations)),
            "readiness_visibility_disclosure": (
                "AI Readiness measures site preparedness. Observed AI Visibility "
                "is separate sampled provider evidence and may remain unknown."
            ),
        }
        payload["score_stack"] = {
            "technical_seo_health": self._score(payload["technical_seo_health"]),
            "ai_readiness": self._score(payload["ai_readiness"]),
            "conversion_readiness": self._score(payload["conversion_readiness"]),
        }
        payload["evidence_confidence"] = {
            key: (
                value.get("evidence_confidence")
                if isinstance(value, dict)
                else None
            )
            for key, value in (
                ("technical_seo_health", payload["technical_seo_health"]),
                ("ai_readiness", payload["ai_readiness"]),
                ("conversion_readiness", payload["conversion_readiness"]),
            )
        }
        return payload

    def create_snapshot(self, run_id: str) -> ReportSnapshot:
        run = self.repository.get_run(run_id)
        if run is None:
            raise ValueError(f"run {run_id} not found")
        if run.status != "completed":
            raise ValueError("product-strength snapshots require a completed run")
        payload = self.assemble(run_id)
        source_snapshot_ids: dict[str, str] = {}
        source_hashes: dict[str, str] = {}
        for surface, version in payload["selected_report_versions"].items():
            report = self.repository.get_report(run_id, version)
            if report is None:
                continue
            report_payload = report.to_dict()
            digest = canonical_sha256(report_payload)
            artifact_ref = self.repository.save_report_snapshot_payload(
                run_id,
                digest,
                report_payload,
            )
            source = ReportSnapshot(
                id=f"{run.id}-{version}-{digest[:16]}",
                run_id=run.id,
                attempt_id=run.attempt_id,
                report_contract=version,
                schema_version=1,
                source_snapshot_ids={},
                source_hashes={version: digest},
                renderer_version="legacy-report-adapter.v1",
                payload_sha256=digest,
                payload_artifact_ref=artifact_ref,
                completeness_percent=self._completeness(report.report_payload),
                status=self._status(report.report_payload),
                created_at=report.created_at,
            )
            stored = self.repository.save_report_snapshot(source)
            source_snapshot_ids[surface] = stored.id
            source_hashes[surface] = digest

        digest = canonical_sha256(payload)
        artifact_ref = self.repository.save_report_snapshot_payload(
            run_id,
            digest,
            payload,
        )
        scored = [
            value
            for surface in (
                payload["technical_seo_health"],
                payload["ai_readiness"],
                payload["conversion_readiness"],
            )
            if isinstance(surface, dict)
            and isinstance(
                value := surface.get("completeness_percent"),
                (int, float),
            )
        ]
        completeness = round(sum(scored) / len(scored), 2) if scored else 0.0
        snapshot = ReportSnapshot(
            id=f"{run.id}-product-strength-{digest[:16]}",
            run_id=run.id,
            attempt_id=run.attempt_id,
            report_contract=self.CONTRACT_VERSION,
            schema_version=1,
            source_snapshot_ids=source_snapshot_ids,
            source_hashes=source_hashes,
            renderer_version=self.RENDERER_VERSION,
            payload_sha256=digest,
            payload_artifact_ref=artifact_ref,
            completeness_percent=completeness,
            status=(
                "complete"
                if all(
                    isinstance(payload[name], dict)
                    and payload[name].get("status") == "complete"
                    for name in (
                        "technical_seo_health",
                        "ai_readiness",
                        "conversion_readiness",
                    )
                )
                else "partial" if source_snapshot_ids else "limited"
            ),
            created_at=run.updated_at,
        )
        stored = self.repository.save_report_snapshot(snapshot)
        self.repository.save_report_alias(
            ReportAlias(
                id=f"{run.id}-product-strength-latest",
                run_id=run.id,
                report_contract=self.CONTRACT_VERSION,
                alias="latest",
                snapshot_id=stored.id,
            )
        )
        return stored

    @staticmethod
    def _surface(report: Any | None) -> dict[str, Any]:
        if report is None:
            return {
                "status": "unknown",
                "score": None,
                "completeness_percent": 0.0,
                "evidence_confidence": 0.0,
                "warnings": ["Evidence is unavailable for this surface."],
            }
        return dict(report.report_payload)

    @staticmethod
    def _score(payload: dict[str, Any]) -> float | int | None:
        value = payload.get("score")
        return value if isinstance(value, (int, float)) and not isinstance(value, bool) else None

    @staticmethod
    def _completeness(payload: dict[str, Any]) -> float:
        value = payload.get("completeness_percent")
        return float(value) if isinstance(value, (int, float)) else 0.0

    @classmethod
    def _status(cls, payload: dict[str, Any]) -> str:
        value = str(payload.get("status") or "limited")
        return value if value in {"complete", "partial", "limited"} else "limited"
