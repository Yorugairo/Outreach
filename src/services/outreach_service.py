from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from pathlib import Path
from typing import Any

from src.models import (
    InsightReport,
    OutreachPackage,
    ProspectRecord,
    canonical_sha256,
    utc_now_iso,
)
from src.repositories.base import InsightRepository
from src.services.opportunity_service import OpportunityService
from src.services.provenance_service import validate_evidence_ref
from src.services.client_report_service import ClientReportService
from src.services.product_strength_service import ProductStrengthService
from src.vertical_packs import resolve_vertical_pack


SERVICE_LABELS = {
    "web_development_rebuild": "Website development / rebuild",
    "profile_management_reputation": "Profile management / reputation",
    "pseo_search_architecture": "pSEO / search architecture",
    "one_trade_network_visibility": "One Trade Network visibility",
    "one_trade_network_crm_saas": "One Trade Network CRM/SaaS",
    "national_bjj_registry_visibility": "National BJJ Registry visibility",
    "national_bjj_registry_crm_saas": "National BJJ Registry CRM/SaaS",
    "website_seo_vertical_visibility": "Website + sitemap/SEO + vertical pSEO visibility",
    "vertical_plugin_embed": "Vertical plugin/embed upgrades",
    "custom_website_crm_saas": "Custom website + optional CRM/SaaS",
}


class OutreachService:
    """Create, review, and export human-approved outreach packages."""

    def __init__(self, repository: InsightRepository, *, artifact_root: str | Path):
        self.repository = repository
        self.artifact_root = Path(artifact_root)
        self.opportunities = OpportunityService()

    def create_package(
        self,
        *,
        insight_run_id: str,
        prospect_id: str,
        report_version: str = "v2",
        vertical_pack_version: str | None = None,
        report_snapshot_id: str | None = None,
        client_report_bundle_id: str | None = None,
        agentic_assessment_id: str | None = None,
    ) -> OutreachPackage:
        run = self.repository.get_run(insight_run_id)
        if run is None:
            raise ValueError(f"run {insight_run_id} not found")
        if run.status != "completed":
            raise ValueError("outreach packages require a completed insight run")
        prospect = self._prospect_or_raise(prospect_id)
        if not prospect.is_runnable:
            raise ValueError("outreach packages require a qualified prospect")
        if run.requested_domain.casefold() != prospect.normalized_domain.casefold():
            raise ValueError("insight run target does not match prospect domain")
        pack = resolve_vertical_pack(vertical_pack_version or prospect.vertical_pack_version)
        if prospect.vertical_id and prospect.vertical_id != pack.vertical_id:
            raise ValueError("prospect vertical does not match requested vertical pack")
        report = self.repository.get_report(insight_run_id, report_version)
        if report is None:
            raise ValueError(f"report {report_version} not found")
        source_report = (
            self.repository.get_report(insight_run_id, "v2")
            if report_version in {"v3", "v4", "v6"}
            else report
        )
        if source_report is None:
            raise ValueError("v3 outreach packages require the source v2 SEO report")
        self.opportunities.validate_report(source_report)
        ai_report = (
            self.repository.get_report(insight_run_id, "ai-v3")
            or self.repository.get_report(insight_run_id, "ai-v2")
            or self.repository.get_report(insight_run_id, "ai-v1")
        )
        ai_snapshot = self._ai_snapshot(ai_report)
        findings = self.opportunities.normalize_findings(source_report)
        self._validate_finding_evidence(source_report, findings)

        issues = [item for item in findings if item.get("finding_type") == "prospect_issue"]
        evidence_limits = [item for item in findings if item.get("finding_type") == "evidence_limit"]
        coverage = self.opportunities.assess(source_report, pack, prospect)
        self._validate_refs(source_report, coverage.evidence_refs)
        conversation_offers = list(pack.service_taxonomy.get("commercial_packages", []))
        market_payload: dict[str, Any] = {}
        market_report: InsightReport | None = None
        market_findings: list[dict[str, Any]] = []
        market_refs: list[dict[str, Any]] = []
        screenshot_refs: list[dict[str, Any]] = []
        market_run_id: str | None = None
        market_snapshot_sha256: str | None = None
        if report_version in {"v3", "v4"}:
            market_report = self.repository.get_report(insight_run_id, "market-v1")
            if market_report is None and report_version == "v3":
                raise ValueError("v3 outreach packages require a market-v1 report")
            if market_report is not None:
                market_payload = market_report.report_payload
                market_run_id = str(market_payload.get("market_run_id") or "")
                market_snapshot_sha256 = str(market_payload.get("market_snapshot_sha256") or "")
                if not market_run_id or not market_snapshot_sha256:
                    raise ValueError("market report is missing immutable snapshot identity")
                market_findings = self._market_findings(market_payload)
                for finding in market_findings:
                    market_refs.extend(finding.get("evidence_refs", []))
                screenshot_refs = [
                    {
                        "artifact_path": item.get("artifact_path"),
                        "sha256": item.get("sha256"),
                        "url": item.get("url"),
                        "caption": item.get("caption"),
                    }
                    for item in market_payload.get("screenshots", [])
                    if isinstance(item, dict) and item.get("capture_status") == "complete"
                ]
                self._validate_refs(source_report, market_refs)
                issues = [*market_findings, *issues]

        opportunity_payload: dict[str, Any] = {}
        opportunity_report_version: str | None = None
        opportunity_scenario_id: str | None = None
        opportunity_snapshot_sha256: str | None = None
        opportunity_evidence_refs: list[dict[str, Any]] = []
        if report_version == "v4":
            opportunity_report = self.repository.get_report(
                insight_run_id,
                "opportunity-v1",
            )
            if opportunity_report is None:
                raise ValueError("v4 outreach packages require opportunity-v1")
            opportunity_payload = opportunity_report.report_payload
            opportunity_report_version = opportunity_report.report_version
            opportunity_scenario_id = str(
                opportunity_payload.get("scenario_id") or ""
            )
            opportunity_snapshot_sha256 = str(
                opportunity_payload.get("scenario_snapshot_sha256") or ""
            )
            if not opportunity_scenario_id or not opportunity_snapshot_sha256:
                raise ValueError("opportunity report is missing immutable scenario identity")
            scenario = self.repository.get_opportunity_scenario(
                opportunity_scenario_id
            )
            if scenario is None:
                raise ValueError("opportunity scenario is missing")
            opportunity_evidence_refs = list(scenario.evidence_refs)

        decision_report_version: str | None = None
        agentic_snapshot_ids: dict[str, str] = {}
        agentic_snapshot_hashes: dict[str, str] = {}
        decision_payload: dict[str, Any] = {}
        if report_version == "v6":
            decision_report = self.repository.get_report(
                insight_run_id,
                "decision-intelligence-v1",
            )
            if decision_report is None:
                raise ValueError("v6 outreach packages require decision-intelligence-v1")
            decision_payload = decision_report.report_payload
            if decision_payload.get("mode") != "prospect":
                raise ValueError("outreach cannot consume owner-mode decision intelligence")
            agentic_snapshot_ids = dict(
                decision_payload.get("source_snapshot_ids") or {}
            )
            agentic_snapshot_hashes = dict(
                decision_payload.get("source_hashes") or {}
            )
            self._validate_agentic_snapshot_bindings(
                insight_run_id,
                agentic_snapshot_ids,
                agentic_snapshot_hashes,
                require_approved=False,
            )
            decision_report_version = decision_report.report_version

        top_issue = market_findings[0] if market_findings else self._top_issue(issues)
        version = self._next_package_version(insight_run_id, prospect_id, report_version)
        product_snapshot = (
            self.repository.get_report_snapshot(report_snapshot_id)
            if report_snapshot_id
            else ProductStrengthService(self.repository).create_snapshot(insight_run_id)
        )
        if product_snapshot is None or product_snapshot.run_id != insight_run_id:
            raise ValueError("outreach report snapshot does not belong to the insight run")
        if product_snapshot.report_contract != ProductStrengthService.CONTRACT_VERSION:
            raise ValueError("outreach packages require a product-strength snapshot")
        if client_report_bundle_id:
            bundle = self.repository.get_client_report_bundle(client_report_bundle_id)
            if (
                bundle is None
                or bundle.run_id != insight_run_id
                or bundle.report_snapshot_id != product_snapshot.id
            ):
                raise ValueError("client report bundle does not match the product-strength snapshot")
            ClientReportService(
                self.repository,
                artifact_root=self.artifact_root,
                output_root=self.artifact_root,
            ).validate(bundle)
        if agentic_assessment_id:
            assessment = self.repository.get_agentic_assessment_snapshot(
                agentic_assessment_id
            )
            if assessment is None:
                raise ValueError("agentic assessment is missing")
            pack = self.repository.get_site_evidence_pack(assessment.evidence_pack_id)
            if pack is None or pack.run_id != insight_run_id:
                raise ValueError("agentic assessment does not belong to the insight run")
            if self.repository.get_agentic_assessment_review_state(assessment.id) != "approved":
                raise ValueError("agentic assessment requires operator approval before outreach")
        package = OutreachPackage(
            insight_run_id=insight_run_id,
            prospect_id=prospect_id,
            vertical_pack_version=pack.pack_id,
            report_version=report_version,
            package_version=version,
            state="needs_review",
            approved_findings=issues,
            executive_answer=self._executive_answer(source_report, top_issue),
            what_we_found=self._what_we_found(top_issue, coverage.to_dict()),
            why_it_matters=self._why_it_matters(top_issue),
            what_we_would_fix=self._conversation_next_step(pack.display_name, conversation_offers),
            confidence=str(top_issue.get("confidence", "low")) if top_issue else "low",
            effort=str(top_issue.get("effort", "discovery_required")) if top_issue else "discovery_required",
            recommended_service_package=conversation_offers,
            subject_line=self._subject(prospect, top_issue),
            email_body=self._email_body(
                prospect,
                top_issue,
                pack.display_name,
                conversation_offers,
            ),
            evidence_brief=self._evidence_brief(
                prospect,
                source_report,
                issues,
                evidence_limits,
                coverage.to_dict(),
                pack.display_name,
                conversation_offers,
                ai_snapshot,
                market_payload,
                opportunity_payload,
            )
            + self._decision_evidence_brief(decision_payload),
            evidence_limits=evidence_limits + [
                {
                    "finding_type": "evidence_limit",
                    "category": "coverage_gate",
                    "title": "Internal coverage-signal limit",
                    "observation": limit,
                    "evidence_family": "service_coverage",
                    "evidence_refs": list(coverage.evidence_refs),
                }
                for limit in coverage.evidence_limits
            ],
            ai_report_version=ai_report.report_version if ai_report else None,
            ai_score_snapshot=ai_snapshot,
            market_report_version=market_report.report_version if market_report else None,
            market_evidence_run_id=market_run_id,
            market_snapshot_sha256=market_snapshot_sha256,
            market_evidence_refs=market_refs,
            screenshot_refs=screenshot_refs,
            opportunity_report_version=opportunity_report_version,
            opportunity_scenario_id=opportunity_scenario_id,
            opportunity_snapshot_sha256=opportunity_snapshot_sha256,
            opportunity_evidence_refs=opportunity_evidence_refs,
            report_snapshot_id=product_snapshot.id,
            report_snapshot_sha256=product_snapshot.payload_sha256,
            client_report_bundle_id=client_report_bundle_id,
            agentic_assessment_id=agentic_assessment_id,
            decision_intelligence_report_version=decision_report_version,
            agentic_snapshot_ids=agentic_snapshot_ids,
            agentic_snapshot_hashes=agentic_snapshot_hashes,
        )
        return self.repository.save_outreach_package(package)

    def approve_package(
        self,
        package_id: str,
        *,
        operator: str = "operator",
        acknowledge_partial_ai: bool = False,
    ) -> OutreachPackage:
        package = self._package_or_raise(package_id)
        if package.state in {"approved", "superseded"}:
            return package
        if package.state == "rejected":
            raise ValueError("rejected outreach packages cannot be approved")
        if not operator.strip():
            raise ValueError("package approval requires an operator")
        if not package.approved_findings:
            raise ValueError(
                "outreach package has no supported prospect issue and cannot be approved"
            )
        claim_eligible = package.ai_score_snapshot.get("customer_claim_eligible")
        if claim_eligible is False and not acknowledge_partial_ai:
            raise ValueError(
                "partial AI readiness evidence requires explicit operator acknowledgement"
            )
        self._validate_package_run(package)
        if package.decision_intelligence_report_version:
            self._validate_agentic_snapshot_bindings(
                package.insight_run_id,
                package.agentic_snapshot_ids,
                package.agentic_snapshot_hashes,
                require_approved=True,
            )
        if package.opportunity_scenario_id:
            scenario = self.repository.get_opportunity_scenario(
                package.opportunity_scenario_id
            )
            if scenario is None or scenario.state != "approved":
                raise ValueError(
                    "pitch package approval requires an approved opportunity scenario"
                )
        approved_at = utc_now_iso()
        approved = replace(
            package,
            state="approved",
            approved_by=operator.strip(),
            approved_at=approved_at,
            ai_evidence_acknowledged=bool(
                acknowledge_partial_ai or claim_eligible is not False
            ),
            updated_at=approved_at,
        )
        return self.repository.save_outreach_package(approved)

    def reject_package(self, package_id: str, *, reason_code: str | None = None) -> OutreachPackage:
        package = self._package_or_raise(package_id)
        if package.state in {"approved", "superseded"}:
            raise ValueError("approved outreach packages cannot be rejected")
        metadata_limit = {
            "finding_type": "evidence_limit",
            "category": "operator_review",
            "title": "Package rejected",
            "observation": reason_code or "operator rejected package",
            "evidence_family": "answer_readiness",
            "evidence_refs": [],
        }
        rejected = replace(package, state="rejected", evidence_limits=[*package.evidence_limits, metadata_limit], updated_at=utc_now_iso())
        return self.repository.save_outreach_package(rejected)

    def export_package(self, package_id: str) -> dict[str, Any]:
        package = self._package_or_raise(package_id)
        if package.state != "approved":
            raise ValueError("only approved outreach packages can be exported")
        # Re-check the independent artifacts at export time; an approved
        # package must never outlive the evidence it cites.
        self._validate_package_run(package)
        return {
            "plaintext": package.email_body,
            "markdown": package.evidence_brief,
            "json": package.to_dict(),
        }

    def _validate_package_run(self, package: OutreachPackage) -> None:
        run = self.repository.get_run(package.insight_run_id)
        report = self.repository.get_report(package.insight_run_id, package.report_version)
        if run is None or run.status != "completed" or report is None:
            raise ValueError("approved packages require a valid completed run and report")
        if package.ai_report_version:
            ai_report = self.repository.get_report(package.insight_run_id, package.ai_report_version)
            if ai_report is None:
                raise ValueError("referenced AI readiness report is missing")
            current_snapshot = self._ai_snapshot(ai_report)
            if any(
                current_snapshot.get(key) != value
                for key, value in package.ai_score_snapshot.items()
            ):
                raise ValueError("AI readiness score snapshot no longer matches its immutable report")
            if (
                package.ai_score_snapshot.get("customer_claim_eligible") is False
                and package.state == "approved"
                and not package.ai_evidence_acknowledged
            ):
                raise ValueError("approved partial AI evidence lacks operator acknowledgement")
        source_report = (
            self.repository.get_report(package.insight_run_id, "v2")
            if package.report_version in {"v3", "v4", "v6"}
            else report
        )
        if source_report is None:
            raise ValueError("referenced source v2 report is missing")
        self._validate_finding_evidence(source_report, package.approved_findings)
        for limit in package.evidence_limits:
            self._validate_refs(source_report, limit.get("evidence_refs", []))
        if package.market_evidence_run_id:
            self._validate_market_snapshot(package, source_report)
        if package.opportunity_scenario_id:
            self._validate_opportunity_snapshot(package)
        self._validate_product_strength_snapshot(package)
        if package.client_report_bundle_id:
            bundle = self.repository.get_client_report_bundle(
                package.client_report_bundle_id
            )
            if bundle is None:
                raise ValueError("referenced client report bundle is missing")
            if bundle.report_snapshot_id != package.report_snapshot_id:
                raise ValueError("client report bundle no longer matches the outreach snapshot")
            ClientReportService(
                self.repository,
                artifact_root=self.artifact_root,
                output_root=self.artifact_root,
            ).validate(bundle)
        if package.agentic_assessment_id:
            assessment = self.repository.get_agentic_assessment_snapshot(
                package.agentic_assessment_id
            )
            if assessment is None:
                raise ValueError("referenced agentic assessment is missing")
            if self.repository.get_agentic_assessment_review_state(assessment.id) != "approved":
                raise ValueError("referenced agentic assessment is not operator-approved")
            if assessment.validation_result.get("customer_safe") is not True:
                raise ValueError("referenced agentic assessment is not customer-safe")
        if package.decision_intelligence_report_version:
            decision_report = self.repository.get_report(
                package.insight_run_id,
                package.decision_intelligence_report_version,
            )
            if decision_report is None:
                raise ValueError("referenced decision-intelligence report is missing")
            if decision_report.report_payload.get("mode") != "prospect":
                raise ValueError("outreach cannot expose owner-mode decision intelligence")
            self._validate_agentic_snapshot_bindings(
                package.insight_run_id,
                package.agentic_snapshot_ids,
                package.agentic_snapshot_hashes,
                require_approved=package.state == "approved",
            )

    def _validate_finding_evidence(self, report: InsightReport, findings: list[dict[str, Any]]) -> None:
        for finding in findings:
            refs = finding.get("evidence_refs", [])
            if not refs:
                raise ValueError("commercial findings require evidence references")
            self._validate_refs(report, refs)

    def _validate_agentic_snapshot_bindings(
        self,
        run_id: str,
        snapshot_ids: dict[str, str],
        snapshot_hashes: dict[str, str],
        *,
        require_approved: bool,
    ) -> None:
        if not snapshot_ids or set(snapshot_ids) != set(snapshot_hashes):
            raise ValueError("decision intelligence has incomplete snapshot bindings")
        for key, snapshot_id in snapshot_ids.items():
            kind = key.split(":", 1)[0]
            loaders = {
                "fact_ledger": self.repository.get_business_fact_ledger_snapshot,
                "decision_coverage": self.repository.get_decision_coverage_snapshot,
                "journeys": self.repository.get_journey_evidence_run,
                "representation_accuracy": (
                    self.repository.get_ai_representation_accuracy_snapshot
                ),
                "owner_diagnostic": self.repository.get_owner_diagnostic_snapshot,
                "remediation_blueprint": (
                    self.repository.get_remediation_blueprint_snapshot
                ),
            }
            loader = loaders.get(kind)
            snapshot = loader(snapshot_id) if loader else None
            if snapshot is None or getattr(snapshot, "run_id", None) != run_id:
                raise ValueError(f"agentic snapshot is missing or run-mismatched: {key}")
            digest = getattr(snapshot, "content_sha256", None) or canonical_sha256(
                snapshot.to_dict()
            )
            if digest != snapshot_hashes[key]:
                raise ValueError(f"agentic snapshot hash no longer matches: {key}")
            work_item = self.repository.get_agentic_work_item(snapshot.work_item_id)
            if work_item is None or work_item.run_id != run_id:
                raise ValueError(f"agentic snapshot work item is missing: {key}")
            if require_approved:
                if work_item.execution_mode in {"shadow", "review"}:
                    raise ValueError("shadow/review agentic evidence cannot enter outreach")
                review_state = getattr(snapshot, "review_state", None)
                if review_state != "approved":
                    review_state = self.repository.get_agentic_evidence_review_state(
                        snapshot.id
                    )
                if review_state != "approved":
                    raise ValueError(f"agentic snapshot is not operator-approved: {key}")

    @staticmethod
    def _decision_evidence_brief(payload: dict[str, Any]) -> str:
        if not payload:
            return ""
        lines = [
            "",
            "## Customer decision evidence",
            (
                "- This layer tests whether a visitor can understand the offer, "
                "resolve key questions, and reach a next step. It does not change "
                "SEO, AI Readiness, traffic, conversion, or revenue scores."
            ),
        ]
        teaser = payload.get("outreach_teaser")
        if isinstance(teaser, dict) and teaser.get("text"):
            lines.append(f"- Verified teaser: {teaser['text']}")
        for journey in payload.get("journeys", []):
            if isinstance(journey, dict):
                lines.append(
                    f"- {str(journey.get('task_kind')).replace('_', ' ').title()}: "
                    f"{journey.get('result_status')} ({journey.get('viewport')})"
                )
        for item in payload.get("recommendations", [])[:3]:
            if isinstance(item, dict):
                lines.append(f"- {item.get('title')}: {item.get('action')}")
        for limitation in payload.get("limitations", []):
            lines.append(f"- Evidence limit: {limitation}")
        return "\n".join(lines) + "\n"

    def _validate_product_strength_snapshot(self, package: OutreachPackage) -> None:
        if not package.report_snapshot_id and not package.report_snapshot_sha256:
            # Legacy packages predate product-strength snapshots and remain
            # readable/exportable under their original evidence contract.
            return
        if not package.report_snapshot_id or not package.report_snapshot_sha256:
            raise ValueError("outreach package is missing its product-strength snapshot")
        snapshot = self.repository.get_report_snapshot(package.report_snapshot_id)
        if snapshot is None:
            raise ValueError("referenced product-strength snapshot is missing")
        if (
            snapshot.run_id != package.insight_run_id
            or snapshot.report_contract != ProductStrengthService.CONTRACT_VERSION
            or snapshot.payload_sha256 != package.report_snapshot_sha256
        ):
            raise ValueError("product-strength snapshot identity no longer matches")
        path = self.artifact_root / Path(*snapshot.payload_artifact_ref.split("/"))
        root = self.artifact_root.resolve()
        path = path.resolve()
        try:
            path.relative_to(root)
        except ValueError as exc:
            raise ValueError("product-strength snapshot escapes the artifact root") from exc
        if not path.is_file():
            raise ValueError("product-strength snapshot payload is missing")
        payload = json.loads(path.read_text(encoding="utf-8"))
        from src.models import canonical_sha256

        if canonical_sha256(payload) != snapshot.payload_sha256:
            raise ValueError("product-strength snapshot payload hash no longer matches")
        for source_name, source_id in snapshot.source_snapshot_ids.items():
            source = self.repository.get_report_snapshot(source_id)
            if source is None:
                raise ValueError(f"product-strength source snapshot is missing: {source_name}")
            if source.payload_sha256 != snapshot.source_hashes.get(source_name):
                raise ValueError(f"product-strength source hash mismatch: {source_name}")
            source_path = (
                self.artifact_root
                / Path(*source.payload_artifact_ref.split("/"))
            ).resolve()
            try:
                source_path.relative_to(root)
            except ValueError as exc:
                raise ValueError(
                    f"product-strength source escapes the artifact root: {source_name}"
                ) from exc
            if not source_path.is_file():
                raise ValueError(
                    f"product-strength source payload is missing: {source_name}"
                )
            source_payload = json.loads(source_path.read_text(encoding="utf-8"))
            if canonical_sha256(source_payload) != source.payload_sha256:
                raise ValueError(
                    f"product-strength source payload hash mismatch: {source_name}"
                )

    def _validate_refs(self, report: InsightReport, refs: Any) -> None:
        run_dir = self.artifact_root / "runs" / report.insight_run_id
        for ref in refs or []:
            validate_evidence_ref(run_dir, ref, expected_attempt_id=report.attempt_id)

    def _validate_market_snapshot(self, package: OutreachPackage, source_report: InsightReport) -> None:
        market_run = self.repository.get_market_evidence_run(str(package.market_evidence_run_id))
        market_report = self.repository.get_report(
            package.insight_run_id,
            str(package.market_report_version or "market-v1"),
        )
        if market_run is None or market_run.state not in {"partial", "complete"} or market_report is None:
            raise ValueError("referenced market evidence is missing or not reportable")
        current_hash = hashlib.sha256(
            json.dumps(
                market_run.to_dict(),
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            ).encode("utf-8")
        ).hexdigest()
        if current_hash != package.market_snapshot_sha256:
            raise ValueError("market evidence snapshot no longer matches its immutable report")
        if market_report.report_payload.get("market_snapshot_sha256") != current_hash:
            raise ValueError("market report snapshot hash is inconsistent")
        self._validate_refs(source_report, package.market_evidence_refs)
        run_dir = (self.artifact_root / "runs" / package.insight_run_id).resolve()
        screenshots_by_path = {
            item.get("artifact_path"): item
            for item in market_run.screenshots
            if isinstance(item, dict) and item.get("capture_status") == "complete"
        }
        for ref in package.screenshot_refs:
            raw_path = ref.get("artifact_path")
            expected_hash = ref.get("sha256")
            if not isinstance(raw_path, str) or not isinstance(expected_hash, str):
                raise ValueError("screenshot references require artifact path and SHA-256")
            if raw_path not in screenshots_by_path:
                raise ValueError("screenshot reference is not present in the market snapshot")
            path = (run_dir / raw_path).resolve()
            try:
                path.relative_to(run_dir)
            except ValueError as exc:
                raise ValueError("screenshot reference escapes the run boundary") from exc
            if path.suffix.casefold() != ".png" or not path.is_file():
                raise ValueError("referenced screenshot artifact is missing")
            if hashlib.sha256(path.read_bytes()).hexdigest() != expected_hash:
                raise ValueError("referenced screenshot hash does not match the PNG artifact")

    def _validate_opportunity_snapshot(
        self,
        package: OutreachPackage,
    ) -> None:
        from src.services.opportunity_reporting_service import (
            OpportunityReportingService,
        )

        scenario = self.repository.get_opportunity_scenario(
            str(package.opportunity_scenario_id)
        )
        report = self.repository.get_report(
            package.insight_run_id,
            str(package.opportunity_report_version or "opportunity-v1"),
        )
        if scenario is None or report is None:
            raise ValueError("referenced opportunity evidence is missing")
        if package.state == "approved" and scenario.state != "approved":
            raise ValueError(
                "approved pitch packages require an approved opportunity scenario"
            )
        digest = OpportunityReportingService.scenario_snapshot_sha256(scenario)
        if digest != package.opportunity_snapshot_sha256:
            raise ValueError("opportunity scenario snapshot no longer matches")
        if (
            report.report_payload.get("scenario_id") != scenario.id
            or report.report_payload.get("scenario_snapshot_sha256") != digest
        ):
            raise ValueError("opportunity report snapshot is inconsistent")
        if package.opportunity_evidence_refs != scenario.evidence_refs:
            raise ValueError("opportunity evidence references no longer match")
        economics = self.repository.get_business_economics_profile(
            scenario.economics_profile_id
        )
        if (
            economics is None
            or economics.version != scenario.economics_profile_version
        ):
            raise ValueError("referenced economics profile is missing or mismatched")
        if scenario.demand_evidence_set_id:
            demand = self.repository.get_demand_evidence_set(
                scenario.demand_evidence_set_id
            )
            if (
                demand is None
                or demand.version != scenario.demand_evidence_version
            ):
                raise ValueError("referenced demand evidence is missing or mismatched")
        if scenario.calibrated_from_id and (
            self.repository.get_acquisition_calibration_record(
                scenario.calibrated_from_id
            )
            is None
        ):
            raise ValueError("referenced calibration evidence is missing")

    def _prospect_or_raise(self, prospect_id: str) -> ProspectRecord:
        prospect = self.repository.get_prospect(prospect_id)
        if prospect is None:
            raise ValueError(f"prospect {prospect_id} not found")
        return prospect

    def _package_or_raise(self, package_id: str) -> OutreachPackage:
        package = self.repository.get_outreach_package(package_id)
        if package is None:
            raise ValueError(f"outreach package {package_id} not found")
        return package

    def _next_package_version(self, run_id: str, prospect_id: str, report_version: str) -> int:
        existing = self.repository.list_outreach_packages(
            insight_run_id=run_id,
            prospect_id=prospect_id,
            limit=1000,
        )
        versions = [item.package_version for item in existing if item.report_version == report_version]
        return max(versions, default=0) + 1

    @staticmethod
    def _coverage_finding(coverage: dict[str, Any]) -> dict[str, Any]:
        """Return an internal coverage observation, never a client pSEO offer."""

        missing_services = list(coverage.get("missing_services", []))
        missing_locations = list(coverage.get("missing_locations", []))
        gap_parts = []
        if missing_services:
            gap_parts.append(f"services: {', '.join(missing_services)}")
        if missing_locations:
            gap_parts.append(f"locations: {', '.join(missing_locations)}")
        return {
            "id": "finding-internal-coverage-signal",
            "finding_type": "prospect_issue",
            "category": "systematic_coverage_gap",
            "title": "Supported service/location coverage gap",
            "observation": (
                "The validated page inventory does not cover the expected "
                + "; ".join(gap_parts)
                + "."
            ),
            "impact": (
                "The site has fewer dedicated, indexable surfaces for the "
                "target-specific demand demonstrated by the search evidence."
            ),
            "recommended_action": (
                "Use this as internal context for the outreach conversation; do "
                "not present it as an offer to build client pSEO."
            ),
            "severity": "medium",
            "effort": "large",
            "confidence": "high",
            "recommended_services": [],
            "service_fit_reason": (
                "Coverage evidence supports an observation only. Delivery uses "
                "the owned vertical pSEO property; it is not client pSEO construction."
            ),
            "evidence_refs": list(coverage.get("evidence_refs", [])),
            "evidence_family": "service_coverage",
        }

    @staticmethod
    def _recommended_services(issues: list[dict[str, Any]]) -> list[str]:
        result: list[str] = []
        for issue in issues:
            for service in issue.get("recommended_services", []):
                if service in SERVICE_LABELS and service not in result:
                    result.append(service)
        return result

    @staticmethod
    def _top_issue(issues: list[dict[str, Any]]) -> dict[str, Any] | None:
        ranks = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
        return min(issues, key=lambda item: (ranks.get(str(item.get("severity")), 9), str(item.get("category"))), default=None)

    @staticmethod
    def _executive_answer(report: InsightReport, top_issue: dict[str, Any] | None) -> str:
        if top_issue:
            return str(report.executive_summary or top_issue.get("observation") or "Evidence-backed website opportunity identified.")
        return "The run produced reviewable evidence, but no supported website issue is approved yet."

    @staticmethod
    def _what_we_found(top_issue: dict[str, Any] | None, coverage: dict[str, Any]) -> str:
        if top_issue:
            return str(top_issue.get("observation", "A supported website issue was observed."))
        if coverage.get("coverage_gap"):
            return "A service/location coverage gap was detected, pending supporting service-route evidence."
        return "No prospect defect is supported by the current evidence."

    @staticmethod
    def _why_it_matters(top_issue: dict[str, Any] | None) -> str:
        if top_issue:
            return str(top_issue.get("impact", "This can reduce search clarity or conversion confidence."))
        return "Unsupported or incomplete evidence should be resolved before making a sales claim."

    @staticmethod
    def _conversation_next_step(platform_name: str, offers: list[str]) -> str:
        offer_text = ", ".join(SERVICE_LABELS[item] for item in offers)
        return (
            "Walk through the persisted evidence, answer questions, and determine "
            f"which {platform_name} path fits: {offer_text}."
        )

    @staticmethod
    def _subject(prospect: ProspectRecord, top_issue: dict[str, Any] | None) -> str:
        if top_issue:
            return f"{prospect.business_name}: search evidence worth reviewing"
        return f"{prospect.business_name}: quick search presence review"

    @staticmethod
    def _email_body(
        prospect: ProspectRecord,
        top_issue: dict[str, Any] | None,
        platform_name: str,
        offers: list[str],
    ) -> str:
        offer_text = ", ".join(SERVICE_LABELS[item] for item in offers)
        issue_text = str(top_issue.get("observation")) if top_issue else "I found a few evidence limits worth resolving before making firm recommendations."
        return (
            f"Hi {prospect.business_name} team,\n\n"
            f"I took a quick evidence-based look at {prospect.website_url} and noticed this: {issue_text}\n\n"
            "I can send the short evidence brief if it would be useful—no generic score pitch or made-up revenue estimate.\n\n"
            f"We operate {platform_name}. Our options include {offer_text}. If the brief is relevant, would a quick conversation be useful?\n"
        )

    @staticmethod
    def _evidence_brief(
        prospect: ProspectRecord,
        report: InsightReport,
        issues: list[dict[str, Any]],
        limits: list[dict[str, Any]],
        coverage: dict[str, Any],
        platform_name: str,
        offers: list[str],
        ai_snapshot: dict[str, Any],
        market_payload: dict[str, Any] | None = None,
        opportunity_payload: dict[str, Any] | None = None,
    ) -> str:
        lines = [
            f"# Outreach evidence brief — {prospect.business_name}",
            "",
            f"- Prospect: {prospect.business_name}",
            f"- Website: {prospect.website_url}",
            f"- Run: {report.insight_run_id}",
            f"- Report: {report.report_version}",
            f"- Owned platform: {platform_name}",
            f"- Conversation paths: {', '.join(SERVICE_LABELS[item] for item in offers)}",
        ]
        if ai_snapshot:
            lines.extend(
                [
                    (
                        f"- AI Readiness: {ai_snapshot.get('score')}/100 "
                        f"({ai_snapshot.get('presentation_label')})"
                    ),
                    f"- AI formula: {ai_snapshot.get('score_version')} (40% AEO, 35% GEO, 25% AIO)",
                    f"- AI evidence completeness: {ai_snapshot.get('completeness_percent')}% ({ai_snapshot.get('status')})",
                    (
                        "- AI breakdown: "
                        f"AEO {ai_snapshot.get('aeo')}, "
                        f"GEO {ai_snapshot.get('geo')}, "
                        f"AIO {ai_snapshot.get('aio')}"
                    ),
                    "- AI Readiness measures technical/content readiness; it does not prove citation or ranking.",
                ]
            )
        search_view = report.report_payload.get("search_visibility", {})
        if isinstance(search_view, dict):
            lines.extend(
                [
                    "",
                    "## Keywords and Google rankings",
                    f"- Evidence status: {search_view.get('status', 'unknown')}",
                    f"- Search visibility: {search_view.get('visibility_score') if search_view.get('visibility_score') is not None else 'Unknown'}",
                    (
                        f"- Sample: {search_view.get('market') or 'Unknown market'}, "
                        f"{search_view.get('device') or 'Unknown device'}, "
                        f"{search_view.get('snapshot_date') or 'no snapshot date'}"
                    ),
                    (
                        f"- Queries checked: {search_view.get('ranking_checks', 0)}; "
                        f"observed rankings: {search_view.get('ranked_count', 0)}; "
                        f"not observed in sampled top 100: {search_view.get('not_observed_count', 0)}"
                    ),
                ]
            )
            for row in search_view.get("keywords", [])[:5]:
                if not isinstance(row, dict):
                    continue
                position = (
                    row.get("observed_rank")
                    if row.get("observed_rank") is not None
                    else "not observed in sampled top 100" if row.get("checked") else "not checked"
                )
                lines.append(
                    f"- {row.get('keyword')}: position {position}; "
                    f"volume {row.get('search_volume') if row.get('search_volume') is not None else 'unknown'}; "
                    f"{row.get('opportunity_label')}"
                )
            for limitation in search_view.get("limitations", []):
                lines.append(f"- Evidence limit: {limitation}")
        authority = report.report_payload.get("offsite_authority", {})
        if isinstance(authority, dict):
            lines.extend(
                [
                    "",
                    "## Off-site authority",
                    f"- Evidence status: {authority.get('status', 'unknown')}",
                    (
                        f"- DataForSEO Link Rank: {authority.get('link_rank')}/100"
                        if authority.get("link_rank") is not None
                        else "- DataForSEO Link Rank: Unknown"
                    ),
                    f"- Backlinks: {authority.get('backlinks') if authority.get('backlinks') is not None else 'Unknown'}",
                    f"- Referring domains: {authority.get('referring_domains') if authority.get('referring_domains') is not None else 'Unknown'}",
                    f"- Referring main domains: {authority.get('referring_main_domains') if authority.get('referring_main_domains') is not None else 'Unknown'}",
                    "- This is provider-specific link evidence, not Google Domain Authority or an exposed Google PageRank value.",
                ]
            )
            for limitation in authority.get("limitations", []):
                lines.append(f"- Evidence limit: {limitation}")
        market = market_payload or {}
        if market:
            lines.extend(
                [
                    "",
                    "## Tacoma competitive opportunities",
                    f"- Market phase: {market.get('phase')}",
                    f"- Organic checks: {(market.get('inventory') or {}).get('organic_checks', 0)}",
                    f"- Maps checks: {(market.get('inventory') or {}).get('maps_checks', 0)}",
                    f"- Approved competitors: {(market.get('inventory') or {}).get('approved_competitors', 0)}",
                    "- Competitor evidence is an explanatory overlay and does not change the SEO or AI scores.",
                ]
            )
            for action in market.get("recommended_actions", [])[:3]:
                lines.extend(
                    [
                        f"### {action.get('keyword')}",
                        f"- Verified gap: {action.get('observation')}",
                        f"- Recommended next step: {action.get('recommended_action')}",
                        f"- Service fit: {', '.join(action.get('service_fit') or [])}",
                    ]
                )
                for ref in action.get("evidence_refs", []):
                    lines.append(f"  - `{ref.get('artifact_path')}` → `{ref.get('field')}`")
            complete_screenshots = [
                item for item in market.get("screenshots", [])
                if isinstance(item, dict) and item.get("capture_status") == "complete"
            ]
            if complete_screenshots:
                lines.append("### Screenshot evidence")
                for item in complete_screenshots:
                    lines.append(f"- {item.get('caption')} — `{item.get('artifact_path')}`")
        opportunity = opportunity_payload or {}
        if opportunity:
            potential = opportunity.get("potential_if_assumptions_hold", {})
            capacity = potential.get("capacity_ceiling") or {}
            lines.extend(
                [
                    "",
                    "## Modeled commercial opportunity",
                    "- Forecast, not guarantee.",
                    "- Search demand is modeled as search occasions, not unique people.",
                    (
                        "- Capacity ceiling: "
                        f"{capacity.get('active_customers')} customers; "
                        f"${capacity.get('mrr', 0):,.0f} MRR; "
                        f"${capacity.get('annual_run_rate', 0):,.0f} annual run-rate."
                    ),
                ]
            )
            for band, output in potential.get("low_base_high", {}).items():
                lines.append(
                    f"- {band.title()}: {output.get('modeled_unique_prospects')} "
                    f"modeled unique prospects; "
                    f"{output.get('capacity_adjusted_active_customers')} "
                    f"capacity-adjusted customers; "
                    f"${output.get('first_year_ramp_revenue', 0):,.0f} "
                    "first-year ramp revenue."
                )
            lines.append("### Assumptions to confirm")
            for item in opportunity.get("what_we_need_to_confirm", []):
                lines.append(f"- {item}")
        lines.extend(
            [
                "",
            "## Approved findings",
            ]
        )
        if not issues:
            lines.append("No prospect issue is approved from the current evidence.")
        for issue in issues:
            services = ", ".join(SERVICE_LABELS[item] for item in issue.get("recommended_services", []) if item in SERVICE_LABELS) or "None"
            lines.extend(
                [
                    f"### {issue.get('title', 'Finding')}",
                    f"- Evidence family: {issue.get('evidence_family', 'technical_seo')}",
                    f"- Observation: {issue.get('observation', '')}",
                    f"- Technical remediation context: {services}",
                    f"- Confidence: {issue.get('confidence', 'low')}",
                ]
            )
            for ref in issue.get("evidence_refs", []):
                lines.append(f"  - `{ref.get('artifact_path')}` → `{ref.get('field')}`")
        lines.extend(
            [
                "",
                "## Internal coverage signal",
                "- This is research context. Any pSEO leverage comes from our owned vertical property, not a client pSEO build.",
                f"- Evidence gate passed: {coverage.get('pseo_eligible')}",
                f"- Demand valid: {coverage.get('demand_valid')}",
                f"- Crawl sufficient: {coverage.get('crawl_sufficient')}",
                f"- Coverage gap: {coverage.get('coverage_gap')}",
                "",
                "## Evidence limits",
            ]
        )
        if not limits and not coverage.get("evidence_limits"):
            lines.append("No evidence limits were emitted.")
        for limit in limits:
            lines.append(f"- {limit.get('category')}: {limit.get('observation')}")
        for limit in coverage.get("evidence_limits", []):
            lines.append(f"- coverage_gate: {limit}")
        return "\n".join(lines) + "\n"

    @staticmethod
    def _market_findings(market_payload: dict[str, Any]) -> list[dict[str, Any]]:
        findings: list[dict[str, Any]] = []
        severity_by_class = {
            "local_pack_gap": "high",
            "near_win": "high",
            "landing_page_gap": "medium",
            "conversion_gap": "medium",
            "authority_gap": "medium",
            "improvement": "medium",
            "not_observed_sample": "low",
        }
        for index, action in enumerate(market_payload.get("recommended_actions", [])[:3], start=1):
            if not isinstance(action, dict) or not action.get("evidence_refs"):
                continue
            opportunity_class = str(action.get("opportunity_class") or "not_observed_sample")
            service_fit = [
                service for service in action.get("service_fit", [])
                if service in SERVICE_LABELS
            ]
            findings.append({
                "id": f"market-gap-{index}",
                "finding_type": "prospect_issue",
                "category": opportunity_class,
                "title": f"Tacoma opportunity: {action.get('keyword')}",
                "observation": str(action.get("observation") or ""),
                "impact": (
                    "The dated Tacoma sample shows a concrete search or conversion opportunity "
                    "worth reviewing; it is not a ranking guarantee."
                ),
                "recommended_action": str(action.get("recommended_action") or ""),
                "severity": severity_by_class.get(opportunity_class, "medium"),
                "effort": "medium",
                "confidence": "high",
                "recommended_services": service_fit,
                "service_fit_reason": (
                    "The recommendation fits website/SEO, Registry visibility, embed, or "
                    "website/CRM conversation paths without offering client-owned pSEO."
                ),
                "evidence_refs": list(action.get("evidence_refs", [])),
                "evidence_family": (
                    "local_entity"
                    if opportunity_class in {"local_pack_gap", "authority_gap"}
                    else "service_coverage"
                ),
            })
        return findings

    @staticmethod
    def _ai_snapshot(report: InsightReport | None) -> dict[str, Any]:
        if report is None:
            return {}
        payload = report.report_payload
        dimensions = payload.get("dimensions", {})
        return {
            "score": payload.get("score"),
            "score_version": payload.get("score_version"),
            "completeness_percent": payload.get("completeness_percent"),
            "status": payload.get("status"),
            "presentation_label": payload.get("presentation_label") or (
                payload.get("band")
                if payload.get("status") == "complete"
                else f"Provisional — {payload.get('band')}"
            ),
            "customer_claim_eligible": payload.get(
                "customer_claim_eligible",
                payload.get("status") == "complete",
            ),
            "aeo": dimensions.get("aeo", {}).get("score"),
            "geo": dimensions.get("geo", {}).get("score"),
            "aio": dimensions.get("aio", {}).get("score"),
        }
