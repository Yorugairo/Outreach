from __future__ import annotations

import glob
import json
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from src.models import (
    AcquisitionCalibrationRecord,
    BusinessEconomicsProfile,
    ConversionEventMap,
    DemandConversionEvidence,
    DemandConversionReportSnapshot,
    DemandEvidenceSet,
    DemandTrendSnapshot,
    DiscoveredAsset,
    InsightReport,
    InsightRun,
    KeywordSet,
    KeywordSetBinding,
    MarketEvidenceRun,
    OutreachActivationEvent,
    OutreachPackage,
    OpportunityScenario,
    PageRecord,
    ProspectRecord,
    ReportAlias,
    ReportSnapshot,
    ReportComparisonSnapshot,
    ClientReportBundle,
    SiteEvidencePack,
    AgenticAnalysisJob,
    AgentCallRecord,
    AgenticAssessmentSnapshot,
    AgenticAssessmentReviewEvent,
    VerticalAgenticPack,
    AgenticWorkItem,
    AgenticToolStep,
    BusinessFactLedgerSnapshot,
    DecisionCoverageSnapshot,
    JourneyEvidenceRun,
    AIRepresentationAccuracySnapshot,
    OwnerDiagnosticSnapshot,
    RemediationBlueprintSnapshot,
    RecommendationOutcomeLink,
    AgenticEvidenceReviewEvent,
    AGENTIC_WORK_ITEM_STATES,
    derive_agentic_review_state,
    RunStageEvent,
    SEOTarget,
    StageCheckpoint,
    VerticalPack,
    OwnedMeasurementSnapshot,
)


class FileBackedInsightRepository:
    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.targets_dir = self.root / "targets"
        self.runs_dir = self.root / "runs"
        self.vertical_packs_dir = self.root / "vertical_packs"
        self.prospects_dir = self.root / "prospects"
        self.keyword_sets_dir = self.root / "keyword_sets"
        self.keyword_set_bindings_dir = self.root / "keyword_set_bindings"
        self.activation_events_dir = self.root / "activation_events"
        self.demand_evidence_sets_dir = self.root / "demand_evidence_sets"
        self.economics_profiles_dir = self.root / "economics_profiles"
        self.opportunity_scenarios_dir = self.root / "opportunity_scenarios"
        self.calibration_records_dir = self.root / "calibration_records"
        self.owned_measurements_dir = self.root / "owned_measurements"
        self.demand_trends_dir = self.root / "demand_trends"
        self.conversion_event_maps_dir = self.root / "conversion_event_maps"
        self.demand_conversion_evidence_dir = self.root / "demand_conversion_evidence"
        self.demand_conversion_reports_dir = self.root / "demand_conversion_reports"
        self.report_snapshots_dir = self.root / "report_snapshots"
        self.report_comparisons_dir = self.root / "report_comparisons"
        self.report_aliases_dir = self.root / "report_aliases"
        self.client_bundles_dir = self.root / "bundles"
        self.evidence_packs_dir = self.root / "evidence_packs"
        self.agentic_jobs_dir = self.root / "agentic_jobs"
        self.agent_calls_dir = self.root / "agent_calls"
        self.agentic_assessments_dir = self.root / "agentic_assessments"
        self.agentic_review_events_dir = self.root / "agentic_review_events"
        self.vertical_agentic_packs_dir = self.root / "vertical_agentic_packs"
        self.agentic_work_items_dir = self.root / "agentic_work_items"
        self.agentic_tool_steps_dir = self.root / "agentic_tool_steps"
        self.business_fact_ledgers_dir = self.root / "business_fact_ledgers"
        self.decision_coverage_dir = self.root / "decision_coverage"
        self.journey_evidence_runs_dir = self.root / "journey_evidence_runs"
        self.ai_representation_accuracy_dir = self.root / "ai_representation_accuracy"
        self.owner_diagnostics_dir = self.root / "owner_diagnostics"
        self.remediation_blueprints_dir = self.root / "remediation_blueprints"
        self.recommendation_outcome_links_dir = self.root / "recommendation_outcome_links"
        self.agentic_evidence_review_events_dir = self.root / "agentic_evidence_review_events"
        self.targets_dir.mkdir(parents=True, exist_ok=True)
        self.runs_dir.mkdir(parents=True, exist_ok=True)
        self.vertical_packs_dir.mkdir(parents=True, exist_ok=True)
        self.prospects_dir.mkdir(parents=True, exist_ok=True)
        self.keyword_sets_dir.mkdir(parents=True, exist_ok=True)
        self.keyword_set_bindings_dir.mkdir(parents=True, exist_ok=True)
        self.activation_events_dir.mkdir(parents=True, exist_ok=True)
        self.demand_evidence_sets_dir.mkdir(parents=True, exist_ok=True)
        self.economics_profiles_dir.mkdir(parents=True, exist_ok=True)
        self.opportunity_scenarios_dir.mkdir(parents=True, exist_ok=True)
        self.calibration_records_dir.mkdir(parents=True, exist_ok=True)
        self.owned_measurements_dir.mkdir(parents=True, exist_ok=True)
        self.demand_trends_dir.mkdir(parents=True, exist_ok=True)
        self.conversion_event_maps_dir.mkdir(parents=True, exist_ok=True)
        self.demand_conversion_evidence_dir.mkdir(parents=True, exist_ok=True)
        self.demand_conversion_reports_dir.mkdir(parents=True, exist_ok=True)
        self.report_snapshots_dir.mkdir(parents=True, exist_ok=True)
        self.report_comparisons_dir.mkdir(parents=True, exist_ok=True)
        self.report_aliases_dir.mkdir(parents=True, exist_ok=True)
        self.client_bundles_dir.mkdir(parents=True, exist_ok=True)
        self.evidence_packs_dir.mkdir(parents=True, exist_ok=True)
        self.agentic_jobs_dir.mkdir(parents=True, exist_ok=True)
        self.agent_calls_dir.mkdir(parents=True, exist_ok=True)
        self.agentic_assessments_dir.mkdir(parents=True, exist_ok=True)
        self.agentic_review_events_dir.mkdir(parents=True, exist_ok=True)
        self.vertical_agentic_packs_dir.mkdir(parents=True, exist_ok=True)
        self.agentic_work_items_dir.mkdir(parents=True, exist_ok=True)
        self.agentic_tool_steps_dir.mkdir(parents=True, exist_ok=True)
        self.business_fact_ledgers_dir.mkdir(parents=True, exist_ok=True)
        self.decision_coverage_dir.mkdir(parents=True, exist_ok=True)
        self.journey_evidence_runs_dir.mkdir(parents=True, exist_ok=True)
        self.ai_representation_accuracy_dir.mkdir(parents=True, exist_ok=True)
        self.owner_diagnostics_dir.mkdir(parents=True, exist_ok=True)
        self.remediation_blueprints_dir.mkdir(parents=True, exist_ok=True)
        self.recommendation_outcome_links_dir.mkdir(parents=True, exist_ok=True)
        self.agentic_evidence_review_events_dir.mkdir(parents=True, exist_ok=True)

    def upsert_target(self, target: SEOTarget) -> SEOTarget:
        path = self.targets_dir / f"{target.id}.json"
        path.write_text(json.dumps(target.to_dict(), indent=2), encoding="utf-8")
        return target

    def create_run(self, run: InsightRun) -> InsightRun:
        run_dir = self._run_dir(run.id)
        for subdir in ["events", "assets", "pages", "reports"]:
            (run_dir / subdir).mkdir(parents=True, exist_ok=True)
        self._write_json(run_dir / "run.json", run.to_dict())
        return run

    def update_run(self, run: InsightRun) -> InsightRun:
        self._write_json(self._run_dir(run.id) / "run.json", run.to_dict())
        return run

    def append_stage_event(self, event: RunStageEvent) -> RunStageEvent:
        safe_stamp = self._safe_filename(event.created_at)
        safe_stage = self._safe_filename(event.stage_name)
        safe_status = self._safe_filename(event.status)
        if event.artifact_path:
            relative = Path(event.artifact_path)
            if relative.is_absolute() or ".." in relative.parts:
                raise ValueError("stage event artifact_path must be a safe run-relative path")
            path = self._run_dir(event.insight_run_id) / relative
        else:
            path = self._run_dir(event.insight_run_id) / "events" / f"{safe_stamp}_{safe_stage}_{safe_status}.json"
        self._write_json(path, event.to_dict())
        return event

    def save_discovered_asset(self, asset: DiscoveredAsset) -> DiscoveredAsset:
        path = self._run_dir(asset.insight_run_id) / "assets" / f"{asset.id}.json"
        self._write_json(path, asset.to_dict())
        return asset

    def save_page_record(self, page: PageRecord) -> PageRecord:
        path = self._run_dir(page.insight_run_id) / "pages" / f"{page.id}.json"
        self._write_json(path, page.to_dict())
        return page

    def list_page_records(self, run_id: str) -> list[PageRecord]:
        return [
            PageRecord(**self._read_json(path))
            for path in sorted((self._run_dir(run_id) / "pages").glob("*.json"))
        ]

    def save_report(self, report: InsightReport) -> InsightReport:
        run_dir = self._run_dir(report.insight_run_id)
        self._write_json(run_dir / "reports" / f"{report.report_version}.json", report.to_dict())
        if report.export_markdown:
            (run_dir / "reports" / f"{report.report_version}.md").write_text(report.export_markdown, encoding="utf-8")
        return report

    def save_report_snapshot_payload(
        self, run_id: str, payload_sha256: str, payload: dict
    ) -> str:
        from src.models import canonical_sha256

        if canonical_sha256(payload) != payload_sha256:
            raise ValueError("report snapshot payload hash does not match content")
        run_dir = self._run_dir(run_id)
        if not (run_dir / "run.json").is_file():
            raise ValueError(f"run {run_id} does not exist")
        path = run_dir / "snapshots" / f"{payload_sha256}.json"
        if path.exists():
            existing = self._read_json(path)
            if existing != payload:
                raise ValueError("report snapshot payloads are immutable")
        else:
            self._write_json(path, payload)
        return f"runs/{run_id}/snapshots/{payload_sha256}.json"

    def save_report_snapshot(self, snapshot: ReportSnapshot) -> ReportSnapshot:
        path = self.report_snapshots_dir / f"{self._safe_identity(snapshot.id)}.json"
        return self._save_immutable(path, snapshot, ReportSnapshot)

    def get_report_snapshot(self, snapshot_id: str) -> ReportSnapshot | None:
        path = self.report_snapshots_dir / f"{self._safe_identity(snapshot_id)}.json"
        if not path.exists():
            return None
        snapshot = ReportSnapshot(**self._read_json(path))
        if snapshot.id != snapshot_id:
            raise ValueError("report snapshot identity does not match requested loader scope")
        return snapshot

    def list_report_snapshots(
        self,
        *,
        run_id: str | None = None,
        report_contract: str | None = None,
        limit: int = 1000,
    ) -> list[ReportSnapshot]:
        snapshots = [ReportSnapshot(**self._read_json(path)) for path in self.report_snapshots_dir.glob("*.json")]
        if run_id is not None:
            snapshots = [snapshot for snapshot in snapshots if snapshot.run_id == run_id]
        if report_contract is not None:
            snapshots = [snapshot for snapshot in snapshots if snapshot.report_contract == report_contract]
        snapshots.sort(key=lambda snapshot: (snapshot.created_at, snapshot.id), reverse=True)
        return snapshots[: max(1, min(int(limit), 10000))]

    def get_latest_report_snapshot(
        self, run_id: str, report_contract: str, alias: str = "latest"
    ) -> ReportSnapshot | None:
        pointer = self.get_report_alias(run_id, report_contract, alias)
        if pointer is not None:
            return self.get_report_snapshot(pointer.snapshot_id)
        history = self.list_report_snapshot_history(run_id, report_contract, limit=1)
        return history[0] if history else None

    def list_report_snapshot_history(
        self, run_id: str, report_contract: str, limit: int = 1000
    ) -> list[ReportSnapshot]:
        return self.list_report_snapshots(run_id=run_id, report_contract=report_contract, limit=limit)

    # Short names used by report-serving callers.
    latest_report_snapshot = get_latest_report_snapshot
    list_report_history = list_report_snapshot_history

    def save_report_comparison_snapshot(
        self, snapshot: ReportComparisonSnapshot
    ) -> ReportComparisonSnapshot:
        path = self.report_comparisons_dir / f"{self._safe_identity(snapshot.id)}.json"
        return self._save_immutable(path, snapshot, ReportComparisonSnapshot)

    def get_report_comparison_snapshot(
        self, snapshot_id: str
    ) -> ReportComparisonSnapshot | None:
        path = self.report_comparisons_dir / f"{self._safe_identity(snapshot_id)}.json"
        if not path.exists():
            return None
        snapshot = ReportComparisonSnapshot(**self._read_json(path))
        if snapshot.id != snapshot_id:
            raise ValueError("report comparison identity does not match requested loader scope")
        return snapshot

    def list_report_comparison_snapshots(
        self,
        *,
        target_id: str | None = None,
        baseline_snapshot_id: str | None = None,
        current_snapshot_id: str | None = None,
        limit: int = 1000,
    ) -> list[ReportComparisonSnapshot]:
        snapshots = [
            ReportComparisonSnapshot(**self._read_json(path))
            for path in self.report_comparisons_dir.glob("*.json")
        ]
        for field_name, value in (
            ("target_id", target_id),
            ("baseline_snapshot_id", baseline_snapshot_id),
            ("current_snapshot_id", current_snapshot_id),
        ):
            if value is not None:
                snapshots = [
                    snapshot
                    for snapshot in snapshots
                    if getattr(snapshot, field_name) == value
                ]
        snapshots.sort(key=lambda snapshot: (snapshot.created_at, snapshot.id), reverse=True)
        return snapshots[: max(1, min(int(limit), 10000))]

    save_comparison_snapshot = save_report_comparison_snapshot
    get_comparison_snapshot = get_report_comparison_snapshot
    list_comparison_snapshots = list_report_comparison_snapshots

    def save_report_alias(self, alias: ReportAlias) -> ReportAlias:
        snapshot = self.get_report_snapshot(alias.snapshot_id)
        if snapshot is None:
            raise ValueError(f"report snapshot {alias.snapshot_id} does not exist")
        if (snapshot.run_id, snapshot.report_contract) != (alias.run_id, alias.report_contract):
            raise ValueError("report alias scope does not match snapshot")
        path = self._report_alias_path(alias.run_id, alias.report_contract, alias.alias)
        self._write_json(path, alias.to_dict())
        return alias

    def get_report_alias(self, run_id: str, report_contract: str, alias: str) -> ReportAlias | None:
        path = self._report_alias_path(run_id, report_contract, alias)
        if not path.exists():
            return None
        record = ReportAlias(**self._read_json(path))
        if (record.run_id, record.report_contract, record.alias) != (run_id, report_contract, alias):
            raise ValueError("report alias identity does not match requested loader scope")
        return record

    def list_report_aliases(
        self,
        *,
        run_id: str | None = None,
        report_contract: str | None = None,
        limit: int = 1000,
    ) -> list[ReportAlias]:
        aliases: list[ReportAlias] = []
        for path in self.report_aliases_dir.glob("*/*/*.json"):
            aliases.append(ReportAlias(**self._read_json(path)))
        if run_id is not None:
            aliases = [record for record in aliases if record.run_id == run_id]
        if report_contract is not None:
            aliases = [record for record in aliases if record.report_contract == report_contract]
        aliases.sort(key=lambda record: (record.updated_at, record.id), reverse=True)
        return aliases[: max(1, min(int(limit), 10000))]

    def save_client_report_bundle(self, bundle: ClientReportBundle) -> ClientReportBundle:
        snapshot = self.get_report_snapshot(bundle.report_snapshot_id)
        if snapshot is None:
            raise ValueError(f"report snapshot {bundle.report_snapshot_id} does not exist")
        if snapshot.run_id != bundle.run_id:
            raise ValueError("client bundle scope does not match snapshot")
        path = self.client_bundles_dir / f"{self._safe_identity(bundle.id)}.json"
        return self._save_immutable(path, bundle, ClientReportBundle)

    def get_client_report_bundle(self, bundle_id: str) -> ClientReportBundle | None:
        path = self.client_bundles_dir / f"{self._safe_identity(bundle_id)}.json"
        if not path.exists():
            return None
        bundle = ClientReportBundle(**self._read_json(path))
        if bundle.id != bundle_id:
            raise ValueError("client bundle identity does not match requested loader scope")
        return bundle

    def list_client_report_bundles(
        self,
        *,
        run_id: str | None = None,
        report_snapshot_id: str | None = None,
        limit: int = 1000,
    ) -> list[ClientReportBundle]:
        bundles = [ClientReportBundle(**self._read_json(path)) for path in self.client_bundles_dir.glob("*.json")]
        if run_id is not None:
            bundles = [bundle for bundle in bundles if bundle.run_id == run_id]
        if report_snapshot_id is not None:
            bundles = [bundle for bundle in bundles if bundle.report_snapshot_id == report_snapshot_id]
        bundles.sort(key=lambda bundle: (bundle.created_at, bundle.id), reverse=True)
        return bundles[: max(1, min(int(limit), 10000))]

    save_report_bundle = save_client_report_bundle
    get_report_bundle = get_client_report_bundle
    list_report_bundles = list_client_report_bundles
    save_snapshot = save_report_snapshot
    get_snapshot = get_report_snapshot
    list_snapshots = list_report_snapshots
    get_latest_snapshot = get_latest_report_snapshot
    list_snapshot_history = list_report_snapshot_history
    get_report_snapshot_history = list_report_snapshot_history
    save_alias = save_report_alias
    get_alias = get_report_alias
    list_aliases = list_report_aliases
    save_bundle = save_client_report_bundle
    get_bundle = get_client_report_bundle
    list_bundles = list_client_report_bundles

    def save_site_evidence_pack(self, pack: SiteEvidencePack) -> SiteEvidencePack:
        path = self.evidence_packs_dir / f"{self._safe_identity(pack.id)}.json"
        return self._save_immutable(path, pack, SiteEvidencePack)

    def get_site_evidence_pack(self, pack_id: str) -> SiteEvidencePack | None:
        path = self.evidence_packs_dir / f"{self._safe_identity(pack_id)}.json"
        if not path.exists():
            return None
        pack = SiteEvidencePack(**self._read_json(path))
        if pack.id != pack_id:
            raise ValueError("site evidence pack identity does not match requested loader scope")
        return pack

    def list_site_evidence_packs(
        self, *, run_id: str | None = None, limit: int = 1000
    ) -> list[SiteEvidencePack]:
        packs = [SiteEvidencePack(**self._read_json(path)) for path in self.evidence_packs_dir.glob("*.json")]
        if run_id is not None:
            packs = [pack for pack in packs if pack.run_id == run_id]
        packs.sort(key=lambda pack: (pack.created_at, pack.id), reverse=True)
        return packs[: max(1, min(int(limit), 10000))]

    def save_agentic_analysis_job(self, job: AgenticAnalysisJob) -> AgenticAnalysisJob:
        existing_by_key = self.get_agentic_job_by_idempotency_key(job.idempotency_key)
        if existing_by_key is not None and existing_by_key.id != job.id:
            raise ValueError("agentic job idempotency key already exists")
        path = self.agentic_jobs_dir / f"{self._safe_identity(job.id)}.json"
        if path.exists():
            existing = AgenticAnalysisJob(**self._read_json(path))
            if existing.to_dict() == job.to_dict():
                return existing
            raise ValueError("agentic analysis jobs require update_agentic_analysis_job for changes")
        self._write_json(path, job.to_dict())
        return job

    def update_agentic_analysis_job(self, job: AgenticAnalysisJob) -> AgenticAnalysisJob:
        path = self.agentic_jobs_dir / f"{self._safe_identity(job.id)}.json"
        if not path.exists():
            raise ValueError(f"agentic job {job.id} not found")
        existing = AgenticAnalysisJob(**self._read_json(path))
        if existing.idempotency_key != job.idempotency_key or existing.evidence_pack_id != job.evidence_pack_id:
            raise ValueError("agentic job identity fields are immutable")
        self._write_json(path, job.to_dict())
        return job

    def get_agentic_analysis_job(self, job_id: str) -> AgenticAnalysisJob | None:
        path = self.agentic_jobs_dir / f"{self._safe_identity(job_id)}.json"
        if not path.exists():
            return None
        job = AgenticAnalysisJob(**self._read_json(path))
        if job.id != job_id:
            raise ValueError("agentic job identity does not match requested loader scope")
        return job

    def get_agentic_job_by_idempotency_key(self, idempotency_key: str) -> AgenticAnalysisJob | None:
        for path in self.agentic_jobs_dir.glob("*.json"):
            job = AgenticAnalysisJob(**self._read_json(path))
            if job.idempotency_key == idempotency_key:
                return job
        return None

    def list_agentic_analysis_jobs(
        self, *, evidence_pack_id: str | None = None, state: str | None = None, limit: int = 1000
    ) -> list[AgenticAnalysisJob]:
        jobs = [AgenticAnalysisJob(**self._read_json(path)) for path in self.agentic_jobs_dir.glob("*.json")]
        if evidence_pack_id is not None:
            jobs = [job for job in jobs if job.evidence_pack_id == evidence_pack_id]
        if state is not None:
            jobs = [job for job in jobs if job.state == state]
        jobs.sort(key=lambda job: (job.updated_at, job.id), reverse=True)
        return jobs[: max(1, min(int(limit), 10000))]

    def append_agent_call_record(self, call: AgentCallRecord) -> AgentCallRecord:
        if self.get_agentic_analysis_job(call.job_id) is None:
            raise ValueError(f"agentic job {call.job_id} does not exist")
        path = self.agent_calls_dir / f"{self._safe_identity(call.id)}.json"
        payload = call.to_dict()
        if path.exists():
            existing = self._agent_call_from_payload(self._read_json(path))
            if existing.to_dict() == payload:
                return existing
            raise ValueError("agent call records are append-only")
        self._write_json(path, payload)
        return call

    def get_agent_call_record(self, call_id: str) -> AgentCallRecord | None:
        path = self.agent_calls_dir / f"{self._safe_identity(call_id)}.json"
        if not path.exists():
            return None
        call = self._agent_call_from_payload(self._read_json(path))
        if call.id != call_id:
            raise ValueError("agent call identity does not match requested loader scope")
        return call

    def list_agent_call_records(
        self, *, job_id: str | None = None, limit: int = 5000
    ) -> list[AgentCallRecord]:
        calls = [self._agent_call_from_payload(self._read_json(path)) for path in self.agent_calls_dir.glob("*.json")]
        if job_id is not None:
            calls = [call for call in calls if call.job_id == job_id]
        calls.sort(key=lambda call: (call.started_at, call.id))
        return calls[: max(1, min(int(limit), 50000))]

    def save_agentic_assessment_snapshot(self, assessment: AgenticAssessmentSnapshot) -> AgenticAssessmentSnapshot:
        job = self.get_agentic_analysis_job(assessment.job_id)
        if job is None:
            raise ValueError(f"agentic job {assessment.job_id} does not exist")
        if assessment.evidence_pack_id != job.evidence_pack_id:
            raise ValueError("assessment evidence pack does not match job")
        path = self.agentic_assessments_dir / f"{self._safe_identity(assessment.id)}.json"
        return self._save_immutable(path, assessment, AgenticAssessmentSnapshot)

    def get_agentic_assessment_snapshot(self, assessment_id: str) -> AgenticAssessmentSnapshot | None:
        path = self.agentic_assessments_dir / f"{self._safe_identity(assessment_id)}.json"
        if not path.exists():
            return None
        assessment = AgenticAssessmentSnapshot(**self._read_json(path))
        if assessment.id != assessment_id:
            raise ValueError("agentic assessment identity does not match requested loader scope")
        return assessment

    def list_agentic_assessment_snapshots(
        self, *, job_id: str | None = None, evidence_pack_id: str | None = None,
        predecessor_id: str | None = None, limit: int = 1000,
    ) -> list[AgenticAssessmentSnapshot]:
        assessments = [
            AgenticAssessmentSnapshot(**self._read_json(path))
            for path in self.agentic_assessments_dir.glob("*.json")
        ]
        for field_name, value in (("job_id", job_id), ("evidence_pack_id", evidence_pack_id), ("predecessor_id", predecessor_id)):
            if value is not None:
                assessments = [assessment for assessment in assessments if getattr(assessment, field_name) == value]
        assessments.sort(key=lambda assessment: (assessment.created_at, assessment.id), reverse=True)
        return assessments[: max(1, min(int(limit), 10000))]

    def append_agentic_assessment_review_event(
        self, event: AgenticAssessmentReviewEvent
    ) -> AgenticAssessmentReviewEvent:
        if self.get_agentic_assessment_snapshot(event.assessment_id) is None:
            raise ValueError(f"assessment {event.assessment_id} does not exist")
        path = self.agentic_review_events_dir / f"{self._safe_identity(event.id)}.json"
        if path.exists():
            existing = AgenticAssessmentReviewEvent(**self._read_json(path))
            if existing.to_dict() == event.to_dict():
                return existing
            raise ValueError("assessment review events are append-only")
        self._write_json(path, event.to_dict())
        return event

    def list_agentic_assessment_review_events(
        self, assessment_id: str, limit: int = 5000
    ) -> list[AgenticAssessmentReviewEvent]:
        events = [
            AgenticAssessmentReviewEvent(**self._read_json(path))
            for path in self.agentic_review_events_dir.glob("*.json")
        ]
        events = [event for event in events if event.assessment_id == assessment_id]
        events.sort(key=lambda event: (event.created_at, event.id))
        return events[: max(1, min(int(limit), 50000))]

    def get_agentic_assessment_review_state(self, assessment_id: str) -> str:
        return derive_agentic_review_state(self.list_agentic_assessment_review_events(assessment_id))

    # ------------------------------------------------------------------
    # P12 vertical agentic evidence and durable work queue
    # ------------------------------------------------------------------
    def save_vertical_agentic_pack(self, pack: VerticalAgenticPack) -> VerticalAgenticPack:
        path = self.vertical_agentic_packs_dir / f"{self._safe_identity(pack.id)}.json"
        return self._save_immutable(path, pack, VerticalAgenticPack)

    def get_vertical_agentic_pack(self, pack_id: str) -> VerticalAgenticPack | None:
        path = self.vertical_agentic_packs_dir / f"{self._safe_identity(pack_id)}.json"
        if path.exists():
            pack = VerticalAgenticPack(**self._read_json(path))
            if pack.id != pack_id:
                raise ValueError("vertical agentic pack identity does not match requested loader scope")
            return pack
        matches = self.list_vertical_agentic_packs(version=pack_id, limit=2)
        if len(matches) > 1:  # pragma: no cover - protected by repository uniqueness
            raise ValueError("vertical agentic pack version is not unique")
        return matches[0] if matches else None

    def list_vertical_agentic_packs(
        self, *, vertical_id: str | None = None, version: str | None = None,
        state: str | None = None, limit: int = 1000,
    ) -> list[VerticalAgenticPack]:
        records = [
            VerticalAgenticPack(**self._read_json(path))
            for path in self.vertical_agentic_packs_dir.glob("*.json")
        ]
        records = self._filter_records(records, vertical_id=vertical_id, version=version, state=state)
        records.sort(key=lambda item: (item.created_at, item.id), reverse=True)
        return records[: max(1, min(int(limit), 10000))]

    def save_agentic_work_item(self, item: AgenticWorkItem) -> AgenticWorkItem:
        existing_by_key = self.get_agentic_work_item_by_idempotency_key(item.idempotency_key)
        if existing_by_key is not None and existing_by_key.id != item.id:
            raise ValueError("agentic work-item idempotency key already exists")
        path = self.agentic_work_items_dir / f"{self._safe_identity(item.id)}.json"
        if path.exists():
            existing = AgenticWorkItem(**self._read_json(path))
            if existing.to_dict() == item.to_dict():
                return existing
            raise ValueError("agentic work items require update_agentic_work_item for changes")
        self._write_json(path, item.to_dict())
        return item

    def update_agentic_work_item(self, item: AgenticWorkItem) -> AgenticWorkItem:
        path = self.agentic_work_items_dir / f"{self._safe_identity(item.id)}.json"
        if not path.exists():
            raise ValueError(f"agentic work item {item.id} not found")
        existing = AgenticWorkItem(**self._read_json(path))
        immutable = (
            "id", "run_id", "attempt_id", "evidence_pack_id", "vertical_pack_version",
            "work_kind", "mode", "source_sha256", "idempotency_key", "requested_runtime",
            "requested_provider", "requested_model", "prompt_version", "rubric_version",
            "schema_version", "budget_class", "consent_id",
        )
        if any(getattr(existing, field) != getattr(item, field) for field in immutable):
            raise ValueError("agentic work-item identity fields are immutable")
        self._write_json(path, item.to_dict())
        return item

    def get_agentic_work_item(self, item_id: str) -> AgenticWorkItem | None:
        path = self.agentic_work_items_dir / f"{self._safe_identity(item_id)}.json"
        if not path.exists():
            return None
        item = AgenticWorkItem(**self._read_json(path))
        if item.id != item_id:
            raise ValueError("agentic work-item identity does not match requested loader scope")
        return item

    def get_agentic_work_item_by_idempotency_key(self, idempotency_key: str) -> AgenticWorkItem | None:
        for path in self.agentic_work_items_dir.glob("*.json"):
            item = AgenticWorkItem(**self._read_json(path))
            if item.idempotency_key == idempotency_key:
                return item
        return None

    def list_agentic_work_items(
        self, *, run_id: str | None = None, state: str | None = None,
        work_kind: str | None = None, mode: str | None = None,
        limit: int = 1000,
    ) -> list[AgenticWorkItem]:
        records = [
            AgenticWorkItem(**self._read_json(path))
            for path in self.agentic_work_items_dir.glob("*.json")
        ]
        records = self._filter_records(
            records, run_id=run_id, state=state, work_kind=work_kind, mode=mode
        )
        records.sort(key=lambda item: (item.updated_at, item.id))
        return records[: max(1, min(int(limit), 10000))]

    def lease_agentic_work_item(
        self, item_id: str, owner: str, *, lease_seconds: int = 90
    ) -> AgenticWorkItem:
        if not owner or not owner.strip():
            raise ValueError("agentic work-item leases require an owner")
        if lease_seconds < 1:
            raise ValueError("agentic work-item lease duration must be positive")
        item = self.get_agentic_work_item(item_id)
        if item is None:
            raise ValueError(f"agentic work item {item_id} not found")
        now = datetime.now(timezone.utc)
        if item.lease_expires_at:
            try:
                expires = datetime.fromisoformat(item.lease_expires_at)
            except ValueError:
                expires = now
            if expires > now and item.lease_owner not in {None, owner}:
                raise ValueError("agentic work-item lease is held by another owner")
        if item.state in {"complete", "partial", "failed", "superseded"}:
            raise ValueError(f"cannot lease terminal agentic work item: {item.state}")
        updated = replace(
            item,
            state="leased",
            lease_owner=owner.strip(),
            lease_expires_at=(now + timedelta(seconds=lease_seconds)).isoformat(),
            attempt_count=item.attempt_count + 1,
            updated_at=now.isoformat(),
        )
        return self.update_agentic_work_item(updated)

    def append_agentic_tool_step(self, step: AgenticToolStep) -> AgenticToolStep:
        if self.get_agentic_work_item(step.work_item_id) is None:
            raise ValueError(f"agentic work item {step.work_item_id} does not exist")
        path = self.agentic_tool_steps_dir / f"{self._safe_identity(step.id)}.json"
        if path.exists():
            existing = AgenticToolStep(**self._read_json(path))
            if existing.to_dict() == step.to_dict():
                return existing
            raise ValueError("agentic tool steps are append-only")
        self._write_json(path, step.to_dict())
        return step

    def get_agentic_tool_step(self, step_id: str) -> AgenticToolStep | None:
        path = self.agentic_tool_steps_dir / f"{self._safe_identity(step_id)}.json"
        if not path.exists():
            return None
        step = AgenticToolStep(**self._read_json(path))
        if step.id != step_id:
            raise ValueError("agentic tool-step identity does not match requested loader scope")
        return step

    def list_agentic_tool_steps(
        self, *, work_item_id: str | None = None, limit: int = 5000
    ) -> list[AgenticToolStep]:
        records = [
            AgenticToolStep(**self._read_json(path))
            for path in self.agentic_tool_steps_dir.glob("*.json")
        ]
        records = self._filter_records(records, work_item_id=work_item_id)
        records.sort(key=lambda item: (item.work_item_id, item.sequence, item.created_at, item.id))
        return records[: max(1, min(int(limit), 50000))]

    def save_business_fact_ledger_snapshot(self, snapshot: BusinessFactLedgerSnapshot) -> BusinessFactLedgerSnapshot:
        return self._save_agentic_snapshot(
            self.business_fact_ledgers_dir, snapshot, BusinessFactLedgerSnapshot
        )

    def get_business_fact_ledger_snapshot(self, snapshot_id: str) -> BusinessFactLedgerSnapshot | None:
        return self._get_agentic_snapshot(self.business_fact_ledgers_dir, snapshot_id, BusinessFactLedgerSnapshot)

    def list_business_fact_ledger_snapshots(
        self, *, run_id: str | None = None, work_item_id: str | None = None,
        mode: str | None = None, limit: int = 1000,
    ) -> list[BusinessFactLedgerSnapshot]:
        return self._list_agentic_snapshots(
            self.business_fact_ledgers_dir, BusinessFactLedgerSnapshot,
            run_id=run_id, work_item_id=work_item_id, mode=mode, limit=limit,
        )

    def save_decision_coverage_snapshot(self, snapshot: DecisionCoverageSnapshot) -> DecisionCoverageSnapshot:
        return self._save_agentic_snapshot(self.decision_coverage_dir, snapshot, DecisionCoverageSnapshot)

    def get_decision_coverage_snapshot(self, snapshot_id: str) -> DecisionCoverageSnapshot | None:
        return self._get_agentic_snapshot(self.decision_coverage_dir, snapshot_id, DecisionCoverageSnapshot)

    def list_decision_coverage_snapshots(
        self, *, run_id: str | None = None, work_item_id: str | None = None,
        mode: str | None = None, limit: int = 1000,
    ) -> list[DecisionCoverageSnapshot]:
        return self._list_agentic_snapshots(
            self.decision_coverage_dir, DecisionCoverageSnapshot,
            run_id=run_id, work_item_id=work_item_id, mode=mode, limit=limit,
        )

    def save_journey_evidence_run(self, evidence: JourneyEvidenceRun) -> JourneyEvidenceRun:
        return self._save_agentic_snapshot(self.journey_evidence_runs_dir, evidence, JourneyEvidenceRun)

    def get_journey_evidence_run(self, evidence_id: str) -> JourneyEvidenceRun | None:
        return self._get_agentic_snapshot(self.journey_evidence_runs_dir, evidence_id, JourneyEvidenceRun)

    def list_journey_evidence_runs(
        self, *, run_id: str | None = None, work_item_id: str | None = None,
        mode: str | None = None, limit: int = 1000,
    ) -> list[JourneyEvidenceRun]:
        return self._list_agentic_snapshots(
            self.journey_evidence_runs_dir, JourneyEvidenceRun,
            run_id=run_id, work_item_id=work_item_id, mode=mode, limit=limit,
        )

    def save_ai_representation_accuracy_snapshot(self, snapshot: AIRepresentationAccuracySnapshot) -> AIRepresentationAccuracySnapshot:
        return self._save_agentic_snapshot(
            self.ai_representation_accuracy_dir, snapshot, AIRepresentationAccuracySnapshot
        )

    def get_ai_representation_accuracy_snapshot(self, snapshot_id: str) -> AIRepresentationAccuracySnapshot | None:
        return self._get_agentic_snapshot(self.ai_representation_accuracy_dir, snapshot_id, AIRepresentationAccuracySnapshot)

    def list_ai_representation_accuracy_snapshots(
        self, *, run_id: str | None = None, work_item_id: str | None = None,
        mode: str | None = None, limit: int = 1000,
    ) -> list[AIRepresentationAccuracySnapshot]:
        return self._list_agentic_snapshots(
            self.ai_representation_accuracy_dir, AIRepresentationAccuracySnapshot,
            run_id=run_id, work_item_id=work_item_id, mode=mode, limit=limit,
        )

    def save_owner_diagnostic_snapshot(self, snapshot: OwnerDiagnosticSnapshot) -> OwnerDiagnosticSnapshot:
        return self._save_agentic_snapshot(self.owner_diagnostics_dir, snapshot, OwnerDiagnosticSnapshot)

    def get_owner_diagnostic_snapshot(self, snapshot_id: str) -> OwnerDiagnosticSnapshot | None:
        return self._get_agentic_snapshot(self.owner_diagnostics_dir, snapshot_id, OwnerDiagnosticSnapshot)

    def list_owner_diagnostic_snapshots(
        self, *, run_id: str | None = None, prospect_id: str | None = None,
        limit: int = 1000,
    ) -> list[OwnerDiagnosticSnapshot]:
        return self._list_agentic_snapshots(
            self.owner_diagnostics_dir, OwnerDiagnosticSnapshot,
            run_id=run_id, prospect_id=prospect_id, limit=limit,
        )

    def save_remediation_blueprint_snapshot(self, snapshot: RemediationBlueprintSnapshot) -> RemediationBlueprintSnapshot:
        return self._save_agentic_snapshot(self.remediation_blueprints_dir, snapshot, RemediationBlueprintSnapshot)

    def get_remediation_blueprint_snapshot(self, snapshot_id: str) -> RemediationBlueprintSnapshot | None:
        return self._get_agentic_snapshot(self.remediation_blueprints_dir, snapshot_id, RemediationBlueprintSnapshot)

    def list_remediation_blueprint_snapshots(
        self, *, run_id: str | None = None, work_item_id: str | None = None,
        mode: str | None = None, limit: int = 1000,
    ) -> list[RemediationBlueprintSnapshot]:
        return self._list_agentic_snapshots(
            self.remediation_blueprints_dir, RemediationBlueprintSnapshot,
            run_id=run_id, work_item_id=work_item_id, mode=mode, limit=limit,
        )

    def save_recommendation_outcome_link(self, link: RecommendationOutcomeLink) -> RecommendationOutcomeLink:
        path = self.recommendation_outcome_links_dir / f"{self._safe_identity(link.id)}.json"
        return self._save_immutable(path, link, RecommendationOutcomeLink)

    def get_recommendation_outcome_link(self, link_id: str) -> RecommendationOutcomeLink | None:
        path = self.recommendation_outcome_links_dir / f"{self._safe_identity(link_id)}.json"
        if not path.exists():
            return None
        link = RecommendationOutcomeLink(**self._read_json(path))
        if link.id != link_id:
            raise ValueError("recommendation outcome identity does not match requested loader scope")
        return link

    def list_recommendation_outcome_links(
        self, *, prospect_id: str | None = None, vertical_id: str | None = None,
        recommendation_id: str | None = None, limit: int = 1000,
    ) -> list[RecommendationOutcomeLink]:
        records = [
            RecommendationOutcomeLink(**self._read_json(path))
            for path in self.recommendation_outcome_links_dir.glob("*.json")
        ]
        records = self._filter_records(
            records, prospect_id=prospect_id, vertical_id=vertical_id,
            recommendation_id=recommendation_id,
        )
        records.sort(key=lambda item: (item.created_at, item.id), reverse=True)
        return records[: max(1, min(int(limit), 10000))]

    def append_agentic_evidence_review_event(self, event: AgenticEvidenceReviewEvent) -> AgenticEvidenceReviewEvent:
        if not self._agentic_snapshot_exists(event.snapshot_id, event.snapshot_type):
            raise ValueError(f"agentic evidence snapshot {event.snapshot_id} does not exist")
        path = self.agentic_evidence_review_events_dir / f"{self._safe_identity(event.id)}.json"
        if path.exists():
            existing = AgenticEvidenceReviewEvent(**self._read_json(path))
            if existing.to_dict() == event.to_dict():
                return existing
            raise ValueError("agentic evidence review events are append-only")
        self._write_json(path, event.to_dict())
        return event

    def list_agentic_evidence_review_events(
        self, snapshot_id: str, *, limit: int = 5000
    ) -> list[AgenticEvidenceReviewEvent]:
        records = [
            AgenticEvidenceReviewEvent(**self._read_json(path))
            for path in self.agentic_evidence_review_events_dir.glob("*.json")
            if self._read_json(path).get("snapshot_id") == snapshot_id
        ]
        records.sort(key=lambda item: (item.created_at, item.id))
        return records[: max(1, min(int(limit), 50000))]

    def get_agentic_evidence_review_state(self, snapshot_id: str) -> str:
        state = "unreviewed"
        for event in self.list_agentic_evidence_review_events(snapshot_id):
            if event.event_type in {"review_requested", "correction_recorded"}:
                state = "needs_review"
            elif event.event_type == "approved":
                state = "approved"
            elif event.event_type == "rejected":
                state = "rejected"
        return state

    def _save_agentic_snapshot(self, directory: Path, record: Any, model: type[Any]) -> Any:
        work_item_id = getattr(record, "work_item_id", None)
        if work_item_id and self.get_agentic_work_item(work_item_id) is None:
            raise ValueError(f"agentic work item {work_item_id} does not exist")
        return self._save_immutable(directory / f"{self._safe_identity(record.id)}.json", record, model)

    def _get_agentic_snapshot(self, directory: Path, snapshot_id: str, model: type[Any]) -> Any | None:
        path = directory / f"{self._safe_identity(snapshot_id)}.json"
        if not path.exists():
            return None
        record = model(**self._read_json(path))
        if record.id != snapshot_id:
            raise ValueError("agentic evidence identity does not match requested loader scope")
        return record

    def _list_agentic_snapshots(
        self, directory: Path, model: type[Any], *, limit: int = 1000, **filters: Any
    ) -> list[Any]:
        records = [model(**self._read_json(path)) for path in directory.glob("*.json")]
        records = self._filter_records(records, **filters)
        records.sort(key=lambda item: (item.created_at, item.id), reverse=True)
        return records[: max(1, min(int(limit), 10000))]

    def _agentic_snapshot_exists(self, snapshot_id: str, snapshot_type: str) -> bool:
        key = snapshot_type.casefold().replace("-", "_")
        mapping = {
            "vertical_agentic_pack": (self.vertical_agentic_packs_dir, VerticalAgenticPack),
            "vertical_agentic_pack_snapshot": (self.vertical_agentic_packs_dir, VerticalAgenticPack),
            "business_fact_ledger": (self.business_fact_ledgers_dir, BusinessFactLedgerSnapshot),
            "business_fact_ledger_snapshot": (self.business_fact_ledgers_dir, BusinessFactLedgerSnapshot),
            "decision_coverage": (self.decision_coverage_dir, DecisionCoverageSnapshot),
            "decision_coverage_snapshot": (self.decision_coverage_dir, DecisionCoverageSnapshot),
            "journey_evidence": (self.journey_evidence_runs_dir, JourneyEvidenceRun),
            "journey_evidence_run": (self.journey_evidence_runs_dir, JourneyEvidenceRun),
            "ai_representation_accuracy": (self.ai_representation_accuracy_dir, AIRepresentationAccuracySnapshot),
            "ai_representation_accuracy_snapshot": (self.ai_representation_accuracy_dir, AIRepresentationAccuracySnapshot),
            "owner_diagnostic": (self.owner_diagnostics_dir, OwnerDiagnosticSnapshot),
            "owner_diagnostic_snapshot": (self.owner_diagnostics_dir, OwnerDiagnosticSnapshot),
            "remediation_blueprint": (self.remediation_blueprints_dir, RemediationBlueprintSnapshot),
            "remediation_blueprint_snapshot": (self.remediation_blueprints_dir, RemediationBlueprintSnapshot),
        }
        target = mapping.get(key)
        if target is None:
            return False
        return self._get_agentic_snapshot(target[0], snapshot_id, target[1]) is not None

    save_evidence_pack = save_site_evidence_pack
    get_evidence_pack = get_site_evidence_pack
    list_evidence_packs = list_site_evidence_packs
    save_agentic_job = save_agentic_analysis_job
    update_agentic_job = update_agentic_analysis_job
    get_agentic_job = get_agentic_analysis_job
    list_agentic_jobs = list_agentic_analysis_jobs
    append_agent_call = append_agent_call_record
    save_agent_call_record = append_agent_call_record
    list_agent_calls = list_agent_call_records
    get_agent_call_records = list_agent_call_records
    save_assessment = save_agentic_assessment_snapshot
    save_agentic_assessment = save_agentic_assessment_snapshot
    get_assessment = get_agentic_assessment_snapshot
    list_assessments = list_agentic_assessment_snapshots
    append_review_event = append_agentic_assessment_review_event
    append_assessment_review_event = append_agentic_assessment_review_event
    get_review_state = get_agentic_assessment_review_state
    save_agentic_pack = save_vertical_agentic_pack
    get_agentic_pack = get_vertical_agentic_pack
    list_agentic_packs = list_vertical_agentic_packs
    save_work_item = save_agentic_work_item
    update_work_item = update_agentic_work_item
    get_work_item = get_agentic_work_item
    list_work_items = list_agentic_work_items
    lease_work_item = lease_agentic_work_item
    append_tool_step = append_agentic_tool_step
    save_agentic_tool_step = append_agentic_tool_step
    save_fact_ledger = save_business_fact_ledger_snapshot
    save_business_fact_ledger = save_business_fact_ledger_snapshot
    get_business_fact_ledger = get_business_fact_ledger_snapshot
    list_business_fact_ledgers = list_business_fact_ledger_snapshots
    get_fact_ledger = get_business_fact_ledger_snapshot
    list_fact_ledgers = list_business_fact_ledger_snapshots
    save_decision_coverage = save_decision_coverage_snapshot
    get_decision_coverage = get_decision_coverage_snapshot
    list_decision_coverages = list_decision_coverage_snapshots
    save_journey_evidence = save_journey_evidence_run
    get_journey_evidence = get_journey_evidence_run
    list_journey_evidence = list_journey_evidence_runs
    save_ai_representation = save_ai_representation_accuracy_snapshot
    get_ai_representation = get_ai_representation_accuracy_snapshot
    list_ai_representations = list_ai_representation_accuracy_snapshots
    save_owner_diagnostic = save_owner_diagnostic_snapshot
    get_owner_diagnostic = get_owner_diagnostic_snapshot
    list_owner_diagnostics = list_owner_diagnostic_snapshots
    save_remediation_blueprint = save_remediation_blueprint_snapshot
    get_remediation_blueprint = get_remediation_blueprint_snapshot
    list_remediation_blueprints = list_remediation_blueprint_snapshots
    save_outcome_link = save_recommendation_outcome_link
    get_outcome_link = get_recommendation_outcome_link
    list_outcome_links = list_recommendation_outcome_links
    append_evidence_review_event = append_agentic_evidence_review_event
    save_agentic_evidence_review_event = append_agentic_evidence_review_event
    list_evidence_review_events = list_agentic_evidence_review_events
    get_evidence_review_state = get_agentic_evidence_review_state

    def save_checkpoint(self, checkpoint: StageCheckpoint) -> StageCheckpoint:
        path = self._checkpoint_path(checkpoint.insight_run_id, checkpoint.attempt_id, checkpoint.stage_name)
        self._write_json(path, checkpoint.to_dict())
        return checkpoint

    def get_run(self, run_id: str) -> "InsightRun | None":
        path = self._run_dir(run_id) / "run.json"
        if not path.exists():
            return None
        return InsightRun(**self._read_json(path))

    def list_runs(self, limit: int = 20) -> list["InsightRun"]:
        runs: list[InsightRun] = []
        for run_dir in sorted(self.runs_dir.glob("*/"), reverse=True):
            path = run_dir / "run.json"
            if path.exists():
                runs.append(InsightRun(**self._read_json(path)))
            if len(runs) >= limit:
                break
        return runs

    def list_stage_events(self, run_id: str) -> list["RunStageEvent"]:
        events: list[RunStageEvent] = []
        for path in sorted((self._run_dir(run_id) / "events").glob("*.json")):
            events.append(RunStageEvent(**self._read_json(path)))
        return events

    def get_report(self, run_id: str, report_version: str) -> "InsightReport | None":
        path = self._run_dir(run_id) / "reports" / f"{report_version}.json"
        if not path.exists():
            return None
        return InsightReport(**self._read_json(path))

    def get_checkpoint(self, run_id: str, attempt_id: str, stage_name: str) -> StageCheckpoint | None:
        path = self._checkpoint_path(run_id, attempt_id, stage_name)
        if not path.exists():
            return None
        payload = self._read_json(path)
        checkpoint = StageCheckpoint(**payload)
        if checkpoint.insight_run_id != run_id or checkpoint.attempt_id != attempt_id or checkpoint.stage_name != stage_name:
            raise ValueError("checkpoint identity does not match requested loader scope")
        return checkpoint

    def save_vertical_pack(self, pack: VerticalPack) -> VerticalPack:
        path = self.vertical_packs_dir / f"{self._safe_identity(pack.pack_id)}.json"
        if path.exists():
            existing = VerticalPack(**self._read_json(path))
            if existing.to_dict() != pack.to_dict():
                raise ValueError(f"vertical pack {pack.pack_id} is immutable")
            return existing
        self._write_json(path, pack.to_dict())
        return pack

    def get_vertical_pack(self, pack_id: str) -> VerticalPack | None:
        path = self.vertical_packs_dir / f"{self._safe_identity(pack_id)}.json"
        if not path.exists():
            return None
        pack = VerticalPack(**self._read_json(path))
        if pack.pack_id != pack_id:
            raise ValueError("vertical pack identity does not match requested loader scope")
        return pack

    def list_vertical_packs(self) -> list[VerticalPack]:
        return [VerticalPack(**self._read_json(path)) for path in sorted(self.vertical_packs_dir.glob("*.json"))]

    def save_prospect(self, prospect: ProspectRecord) -> ProspectRecord:
        path = self.prospects_dir / f"{self._safe_identity(prospect.id)}.json"
        for candidate_path in self.prospects_dir.glob("*.json"):
            if candidate_path == path:
                continue
            candidate = ProspectRecord(**self._read_json(candidate_path))
            if (
                candidate.vertical_id == prospect.vertical_id
                and candidate.normalized_domain == prospect.normalized_domain
            ):
                raise ValueError("prospect already exists for vertical and normalized domain")
        self._write_json(path, prospect.to_dict())
        return prospect

    def get_prospect(self, prospect_id: str) -> ProspectRecord | None:
        path = self.prospects_dir / f"{self._safe_identity(prospect_id)}.json"
        if not path.exists():
            return None
        prospect = ProspectRecord(**self._read_json(path))
        if prospect.id != prospect_id:
            raise ValueError("prospect identity does not match requested loader scope")
        return prospect

    def list_prospects(
        self,
        *,
        vertical_id: str | None = None,
        qualification_status: str | None = None,
        limit: int = 1000,
    ) -> list[ProspectRecord]:
        records = [ProspectRecord(**self._read_json(path)) for path in sorted(self.prospects_dir.glob("*.json"))]
        if vertical_id is not None:
            records = [record for record in records if record.vertical_id == vertical_id]
        if qualification_status is not None:
            records = [record for record in records if record.qualification_status == qualification_status]
        return records[: max(1, min(int(limit), 10000))]

    def save_keyword_set(self, keyword_set: KeywordSet) -> KeywordSet:
        path = self.keyword_sets_dir / f"{self._safe_identity(keyword_set.id)}.json"
        if path.exists():
            existing = KeywordSet(**self._read_json(path))
            if existing.to_dict() == keyword_set.to_dict():
                return existing
            allowed_supersession = (
                existing.state == "approved"
                and keyword_set.state == "superseded"
                and existing.id == keyword_set.id
                and existing.keyword_set_key == keyword_set.keyword_set_key
                and keyword_set.superseded_by_id
            )
            if existing.state in {"approved", "superseded"} and not allowed_supersession:
                raise ValueError("approved and superseded keyword sets are immutable")
        for candidate_path in self.keyword_sets_dir.glob("*.json"):
            if candidate_path == path:
                continue
            candidate = KeywordSet(**self._read_json(candidate_path))
            if candidate.keyword_set_key == keyword_set.keyword_set_key:
                raise ValueError(f"keyword set version already exists: {keyword_set.keyword_set_key}")
        self._write_json(path, keyword_set.to_dict())
        return keyword_set

    def get_keyword_set(self, keyword_set_id: str) -> KeywordSet | None:
        path = self.keyword_sets_dir / f"{self._safe_identity(keyword_set_id)}.json"
        if not path.exists():
            return None
        keyword_set = KeywordSet(**self._read_json(path))
        if keyword_set.id != keyword_set_id:
            raise ValueError("keyword set identity does not match requested loader scope")
        return keyword_set

    def list_keyword_sets(
        self,
        *,
        vertical_id: str | None = None,
        normalized_domain: str | None = None,
        state: str | None = None,
        limit: int = 1000,
    ) -> list[KeywordSet]:
        records = [KeywordSet(**self._read_json(path)) for path in self.keyword_sets_dir.glob("*.json")]
        if vertical_id is not None:
            records = [record for record in records if record.vertical_id == vertical_id]
        if normalized_domain is not None:
            records = [record for record in records if record.normalized_domain == normalized_domain]
        if state is not None:
            records = [record for record in records if record.state == state]
        records.sort(key=lambda record: (record.updated_at, record.id), reverse=True)
        return records[: max(1, min(int(limit), 10000))]

    def save_keyword_set_binding(self, binding: KeywordSetBinding) -> KeywordSetBinding:
        path = self.keyword_set_bindings_dir / f"{self._safe_identity(binding.id)}.json"
        if path.exists():
            existing = KeywordSetBinding(**self._read_json(path))
            if existing.to_dict() != binding.to_dict():
                raise ValueError("keyword-set bindings are immutable")
            return existing
        for candidate_path in self.keyword_set_bindings_dir.glob("*.json"):
            candidate = KeywordSetBinding(**self._read_json(candidate_path))
            if (
                candidate.state == "active"
                and candidate.normalized_domain == binding.normalized_domain
                and candidate.vertical_id == binding.vertical_id
            ):
                if candidate.keyword_set_id == binding.keyword_set_id and candidate.prospect_id == binding.prospect_id:
                    return candidate
                raise ValueError("domain already has an active keyword-set binding for this vertical")
        self._write_json(path, binding.to_dict())
        return binding

    def list_keyword_set_bindings(
        self,
        *,
        keyword_set_id: str | None = None,
        normalized_domain: str | None = None,
        prospect_id: str | None = None,
        state: str | None = "active",
        limit: int = 1000,
    ) -> list[KeywordSetBinding]:
        records = [
            KeywordSetBinding(**self._read_json(path))
            for path in self.keyword_set_bindings_dir.glob("*.json")
        ]
        for field_name, value in (
            ("keyword_set_id", keyword_set_id),
            ("normalized_domain", normalized_domain),
            ("prospect_id", prospect_id),
            ("state", state),
        ):
            if value is not None:
                records = [record for record in records if getattr(record, field_name) == value]
        records.sort(key=lambda record: (record.created_at, record.id), reverse=True)
        return records[: max(1, min(int(limit), 10000))]

    def save_market_evidence_run(self, market_run: MarketEvidenceRun) -> MarketEvidenceRun:
        path = self._market_run_path(market_run.insight_run_id, market_run.id)
        if path.exists():
            existing = MarketEvidenceRun(**self._read_json(path))
            if existing.to_dict() == market_run.to_dict():
                return existing
            if existing.state in {"complete", "failed", "superseded"}:
                raise ValueError("terminal market evidence runs are immutable")
        self._write_json(path, market_run.to_dict())
        return market_run

    def get_market_evidence_run(self, market_run_id: str) -> MarketEvidenceRun | None:
        safe_id = self._safe_identity(market_run_id)
        for path in self.runs_dir.glob(f"*/market/{safe_id}.json"):
            market_run = MarketEvidenceRun(**self._read_json(path))
            if market_run.id != market_run_id:
                raise ValueError("market evidence identity does not match requested loader scope")
            return market_run
        return None

    def list_market_evidence_runs(
        self,
        *,
        insight_run_id: str | None = None,
        state: str | None = None,
        limit: int = 1000,
    ) -> list[MarketEvidenceRun]:
        pattern = f"{self._safe_identity(insight_run_id)}/market/*.json" if insight_run_id else "*/market/*.json"
        records = [MarketEvidenceRun(**self._read_json(path)) for path in self.runs_dir.glob(pattern)]
        if state is not None:
            records = [record for record in records if record.state == state]
        records.sort(key=lambda record: (record.updated_at, record.id), reverse=True)
        return records[: max(1, min(int(limit), 10000))]

    def save_market_artifact(
        self,
        insight_run_id: str,
        market_run_id: str,
        relative_path: str,
        payload: dict | bytes,
    ) -> str:
        relative = Path(relative_path)
        if relative.is_absolute() or not relative.parts or ".." in relative.parts:
            raise ValueError("market artifact path must be safe and relative")
        safe_run = self._safe_identity(insight_run_id)
        safe_market = self._safe_identity(market_run_id)
        path = self.runs_dir / safe_run / "market" / safe_market / relative
        resolved_root = (self.runs_dir / safe_run / "market" / safe_market).resolve()
        resolved_path = path.resolve()
        if resolved_path != resolved_root and resolved_root not in resolved_path.parents:
            raise ValueError("market artifact path escaped its run scope")
        if isinstance(payload, bytes):
            path.parent.mkdir(parents=True, exist_ok=True)
            temporary = path.with_name(f".{path.name}.tmp")
            temporary.write_bytes(payload)
            temporary.replace(path)
        elif isinstance(payload, dict):
            self._write_json(path, payload)
        else:
            raise TypeError("market artifacts must be JSON objects or bytes")
        return str(path)

    def save_opportunity_artifact(
        self,
        insight_run_id: str,
        scenario_id: str,
        relative_path: str,
        payload: dict | bytes,
    ) -> str:
        relative = Path(relative_path)
        if relative.is_absolute() or not relative.parts or ".." in relative.parts:
            raise ValueError("opportunity artifact path must be safe and relative")
        safe_run = self._safe_identity(insight_run_id)
        safe_scenario = self._safe_identity(scenario_id)
        root = self.runs_dir / safe_run / "opportunity" / safe_scenario
        path = root / relative
        resolved_root = root.resolve()
        resolved_path = path.resolve()
        if resolved_path != resolved_root and resolved_root not in resolved_path.parents:
            raise ValueError("opportunity artifact path escaped its run scope")
        if isinstance(payload, bytes):
            path.parent.mkdir(parents=True, exist_ok=True)
            temporary = path.with_name(f".{path.name}.tmp")
            temporary.write_bytes(payload)
            temporary.replace(path)
        elif isinstance(payload, dict):
            self._write_json(path, payload)
        else:
            raise TypeError("opportunity artifacts must be JSON objects or bytes")
        return str(path)

    def save_outreach_package(self, package: OutreachPackage) -> OutreachPackage:
        if not package.insight_run_id:
            raise ValueError("outreach package requires insight_run_id")
        path = self._package_json_path(package)
        if path.exists():
            existing = OutreachPackage(**self._read_json(path))
            if existing.to_dict() != package.to_dict() and existing.state in {"approved", "superseded"}:
                raise ValueError("approved outreach packages are immutable")
            if existing.to_dict() == package.to_dict():
                return existing
        for candidate_path in self.runs_dir.glob("*/outreach/*.json"):
            if candidate_path == path:
                continue
            candidate = OutreachPackage(**self._read_json(candidate_path))
            if (
                candidate.insight_run_id == package.insight_run_id
                and candidate.prospect_id == package.prospect_id
                and candidate.report_version == package.report_version
                and candidate.package_version == package.package_version
            ):
                raise ValueError("outreach package version already exists")
        self._write_json(path, package.to_dict())
        outreach_dir = path.parent
        if package.state == "approved" and package.email_body:
            (outreach_dir / f"{self._safe_identity(package.id)}.txt").write_text(package.email_body, encoding="utf-8")
        if package.state == "approved" and package.evidence_brief:
            (outreach_dir / f"{self._safe_identity(package.id)}.md").write_text(package.evidence_brief, encoding="utf-8")
        return package

    def get_outreach_package(self, package_id: str) -> OutreachPackage | None:
        safe_id = self._safe_identity(package_id)
        for path in self.runs_dir.glob(f"*/outreach/{safe_id}.json"):
            package = OutreachPackage(**self._read_json(path))
            if package.id != package_id:
                raise ValueError("outreach package identity does not match requested loader scope")
            return package
        return None

    def list_outreach_packages(
        self,
        *,
        prospect_id: str | None = None,
        insight_run_id: str | None = None,
        state: str | None = None,
        limit: int = 1000,
    ) -> list[OutreachPackage]:
        packages = [OutreachPackage(**self._read_json(path)) for path in self.runs_dir.glob("*/outreach/*.json")]
        if prospect_id is not None:
            packages = [package for package in packages if package.prospect_id == prospect_id]
        if insight_run_id is not None:
            packages = [package for package in packages if package.insight_run_id == insight_run_id]
        if state is not None:
            packages = [package for package in packages if package.state == state]
        packages.sort(key=lambda package: (package.updated_at, package.id), reverse=True)
        return packages[: max(1, min(int(limit), 10000))]

    def append_activation_event(self, event: OutreachActivationEvent) -> OutreachActivationEvent:
        path = self.activation_events_dir / f"{self._safe_identity(event.id)}.json"
        if path.exists():
            existing = OutreachActivationEvent(**self._read_json(path))
            if existing.to_dict() != event.to_dict():
                raise ValueError("activation events are append-only")
            return existing
        self._write_json(path, event.to_dict())
        return event

    def list_activation_events(
        self,
        *,
        insight_run_id: str | None = None,
        outreach_package_id: str | None = None,
        vertical_id: str | None = None,
        limit: int = 5000,
    ) -> list[OutreachActivationEvent]:
        events = [OutreachActivationEvent(**self._read_json(path)) for path in sorted(self.activation_events_dir.glob("*.json"))]
        if insight_run_id is not None:
            events = [event for event in events if event.insight_run_id == insight_run_id]
        if outreach_package_id is not None:
            events = [event for event in events if event.outreach_package_id == outreach_package_id]
        if vertical_id is not None:
            events = [event for event in events if event.vertical_id == vertical_id]
        return events[: max(1, min(int(limit), 50000))]

    def save_demand_evidence_set(self, evidence: DemandEvidenceSet) -> DemandEvidenceSet:
        path = self.demand_evidence_sets_dir / f"{self._safe_identity(evidence.id)}.json"
        return self._save_immutable(path, evidence, DemandEvidenceSet)

    def get_demand_evidence_set(self, evidence_id: str) -> DemandEvidenceSet | None:
        path = self.demand_evidence_sets_dir / f"{self._safe_identity(evidence_id)}.json"
        if not path.exists():
            return None
        evidence = DemandEvidenceSet(**self._read_json(path))
        if evidence.id != evidence_id:
            raise ValueError("demand evidence identity does not match requested loader scope")
        return evidence

    def list_demand_evidence_sets(
        self,
        *,
        prospect_id: str | None = None,
        keyword_set_id: str | None = None,
        state: str | None = None,
        predecessor_id: str | None = None,
        superseded_by_id: str | None = None,
        limit: int = 1000,
    ) -> list[DemandEvidenceSet]:
        records = [DemandEvidenceSet(**self._read_json(path)) for path in self.demand_evidence_sets_dir.glob("*.json")]
        records = self._filter_records(records, prospect_id=prospect_id, keyword_set_id=keyword_set_id,
                                       state=state, predecessor_id=predecessor_id,
                                       superseded_by_id=superseded_by_id)
        records.sort(key=lambda record: (record.created_at, record.id), reverse=True)
        return records[: max(1, min(int(limit), 10000))]

    save_demand_evidence = save_demand_evidence_set
    get_demand_evidence = get_demand_evidence_set
    list_demand_evidence = list_demand_evidence_sets

    def save_business_economics_profile(self, profile: BusinessEconomicsProfile) -> BusinessEconomicsProfile:
        path = self.economics_profiles_dir / f"{self._safe_identity(profile.id)}.json"
        return self._save_immutable(path, profile, BusinessEconomicsProfile)

    save_economics_profile = save_business_economics_profile

    def get_business_economics_profile(self, profile_id: str) -> BusinessEconomicsProfile | None:
        path = self.economics_profiles_dir / f"{self._safe_identity(profile_id)}.json"
        if not path.exists():
            return None
        profile = BusinessEconomicsProfile(**self._read_json(path))
        if profile.id != profile_id:
            raise ValueError("economics profile identity does not match requested loader scope")
        return profile

    get_economics_profile = get_business_economics_profile

    def list_business_economics_profiles(
        self,
        *,
        prospect_id: str | None = None,
        vertical_id: str | None = None,
        state: str | None = None,
        predecessor_id: str | None = None,
        superseded_by_id: str | None = None,
        limit: int = 1000,
    ) -> list[BusinessEconomicsProfile]:
        records = [BusinessEconomicsProfile(**self._read_json(path)) for path in self.economics_profiles_dir.glob("*.json")]
        records = self._filter_records(records, prospect_id=prospect_id, vertical_id=vertical_id,
                                       state=state, predecessor_id=predecessor_id,
                                       superseded_by_id=superseded_by_id)
        records.sort(key=lambda record: (record.created_at, record.id), reverse=True)
        return records[: max(1, min(int(limit), 10000))]

    list_economics_profiles = list_business_economics_profiles

    def save_opportunity_scenario(self, scenario: OpportunityScenario) -> OpportunityScenario:
        path = self.opportunity_scenarios_dir / f"{self._safe_identity(scenario.id)}.json"
        return self._save_immutable(path, scenario, OpportunityScenario)

    def get_opportunity_scenario(self, scenario_id: str) -> OpportunityScenario | None:
        path = self.opportunity_scenarios_dir / f"{self._safe_identity(scenario_id)}.json"
        if not path.exists():
            return None
        payload = self._read_json(path)
        payload.pop("forecast_label", None)
        scenario = OpportunityScenario(**payload)
        if scenario.id != scenario_id:
            raise ValueError("opportunity scenario identity does not match requested loader scope")
        return scenario

    def list_opportunity_scenarios(
        self,
        *,
        insight_run_id: str | None = None,
        prospect_id: str | None = None,
        state: str | None = None,
        predecessor_id: str | None = None,
        calibrated_from_id: str | None = None,
        limit: int = 1000,
    ) -> list[OpportunityScenario]:
        records = []
        for path in self.opportunity_scenarios_dir.glob("*.json"):
            payload = self._read_json(path)
            payload.pop("forecast_label", None)
            records.append(OpportunityScenario(**payload))
        records = self._filter_records(records, insight_run_id=insight_run_id, prospect_id=prospect_id,
                                       state=state, predecessor_id=predecessor_id,
                                       calibrated_from_id=calibrated_from_id)
        records.sort(key=lambda record: (record.created_at, record.id), reverse=True)
        return records[: max(1, min(int(limit), 10000))]

    save_opportunity = save_opportunity_scenario
    get_opportunity = get_opportunity_scenario
    list_opportunities = list_opportunity_scenarios

    def save_acquisition_calibration_record(self, record: AcquisitionCalibrationRecord) -> AcquisitionCalibrationRecord:
        path = self.calibration_records_dir / f"{self._safe_identity(record.id)}.json"
        return self._save_immutable(path, record, AcquisitionCalibrationRecord)

    def get_acquisition_calibration_record(self, record_id: str) -> AcquisitionCalibrationRecord | None:
        path = self.calibration_records_dir / f"{self._safe_identity(record_id)}.json"
        if not path.exists():
            return None
        record = AcquisitionCalibrationRecord(**self._read_json(path))
        if record.id != record_id:
            raise ValueError("calibration record identity does not match requested loader scope")
        return record

    def list_acquisition_calibration_records(
        self,
        *,
        prospect_id: str | None = None,
        vertical_id: str | None = None,
        market: str | None = None,
        limit: int = 1000,
    ) -> list[AcquisitionCalibrationRecord]:
        records = [AcquisitionCalibrationRecord(**self._read_json(path)) for path in self.calibration_records_dir.glob("*.json")]
        records = self._filter_records(records, prospect_id=prospect_id, vertical_id=vertical_id, market=market)
        records.sort(key=lambda record: (record.period_end, record.created_at, record.id), reverse=True)
        return records[: max(1, min(int(limit), 10000))]

    save_calibration_record = save_acquisition_calibration_record
    get_calibration_record = get_acquisition_calibration_record
    list_calibration_records = list_acquisition_calibration_records
    save_acquisition_calibration = save_acquisition_calibration_record
    get_acquisition_calibration = get_acquisition_calibration_record
    list_acquisition_calibrations = list_acquisition_calibration_records

    def save_owned_measurement_snapshot(self, snapshot: OwnedMeasurementSnapshot) -> OwnedMeasurementSnapshot:
        path = self.owned_measurements_dir / f"{self._safe_identity(snapshot.id)}.json"
        return self._save_immutable(path, snapshot, OwnedMeasurementSnapshot)

    def get_owned_measurement_snapshot(self, snapshot_id: str) -> OwnedMeasurementSnapshot | None:
        path = self.owned_measurements_dir / f"{self._safe_identity(snapshot_id)}.json"
        if not path.exists():
            return None
        snapshot = OwnedMeasurementSnapshot(**self._read_json(path))
        if snapshot.id != snapshot_id:
            raise ValueError("owned measurement identity does not match requested loader scope")
        return snapshot

    def list_owned_measurement_snapshots(
        self,
        *,
        prospect_id: str | None = None,
        vertical_id: str | None = None,
        source: str | None = None,
        predecessor_id: str | None = None,
        limit: int = 1000,
    ) -> list[OwnedMeasurementSnapshot]:
        records = [
            OwnedMeasurementSnapshot(**self._read_json(path))
            for path in self.owned_measurements_dir.glob("*.json")
        ]
        records = self._filter_records(
            records,
            prospect_id=prospect_id,
            vertical_id=vertical_id,
            source=source,
            predecessor_id=predecessor_id,
        )
        records.sort(key=lambda record: (record.period_end, record.created_at, record.id), reverse=True)
        return records[: max(1, min(int(limit), 10000))]

    save_owned_measurement = save_owned_measurement_snapshot
    get_owned_measurement = get_owned_measurement_snapshot
    list_owned_measurements = list_owned_measurement_snapshots

    def save_demand_trend_snapshot(
        self, snapshot: DemandTrendSnapshot
    ) -> DemandTrendSnapshot:
        path = self.demand_trends_dir / f"{self._safe_identity(snapshot.id)}.json"
        return self._save_immutable(path, snapshot, DemandTrendSnapshot)

    def get_demand_trend_snapshot(
        self, snapshot_id: str
    ) -> DemandTrendSnapshot | None:
        path = self.demand_trends_dir / f"{self._safe_identity(snapshot_id)}.json"
        if not path.exists():
            return None
        snapshot = DemandTrendSnapshot(**self._read_json(path))
        if snapshot.id != snapshot_id:
            raise ValueError("demand trend identity does not match requested loader scope")
        return snapshot

    def list_demand_trend_snapshots(
        self,
        *,
        prospect_id: str | None = None,
        vertical_id: str | None = None,
        market: str | None = None,
        source: str | None = None,
        state: str | None = None,
        predecessor_id: str | None = None,
        limit: int = 1000,
    ) -> list[DemandTrendSnapshot]:
        records = [
            DemandTrendSnapshot(**self._read_json(path))
            for path in self.demand_trends_dir.glob("*.json")
        ]
        records = self._filter_records(
            records,
            prospect_id=prospect_id,
            vertical_id=vertical_id,
            market=market,
            source=source,
            state=state,
            predecessor_id=predecessor_id,
        )
        records.sort(key=lambda record: (record.created_at, record.id), reverse=True)
        return records[: max(1, min(int(limit), 10000))]

    save_demand_trend = save_demand_trend_snapshot
    get_demand_trend = get_demand_trend_snapshot
    list_demand_trends = list_demand_trend_snapshots

    def save_conversion_event_map(
        self, event_map: ConversionEventMap
    ) -> ConversionEventMap:
        path = self.conversion_event_maps_dir / (
            f"{self._safe_identity(event_map.id)}.json"
        )
        return self._save_immutable(path, event_map, ConversionEventMap)

    def get_conversion_event_map(
        self, event_map_id: str
    ) -> ConversionEventMap | None:
        path = self.conversion_event_maps_dir / (
            f"{self._safe_identity(event_map_id)}.json"
        )
        if not path.exists():
            return None
        event_map = ConversionEventMap(**self._read_json(path))
        if event_map.id != event_map_id:
            raise ValueError(
                "conversion event map identity does not match requested loader scope"
            )
        return event_map

    def list_conversion_event_maps(
        self,
        *,
        prospect_id: str | None = None,
        vertical_id: str | None = None,
        state: str | None = None,
        predecessor_id: str | None = None,
        limit: int = 1000,
    ) -> list[ConversionEventMap]:
        records = [
            ConversionEventMap(**self._read_json(path))
            for path in self.conversion_event_maps_dir.glob("*.json")
        ]
        records = self._filter_records(
            records,
            prospect_id=prospect_id,
            vertical_id=vertical_id,
            state=state,
            predecessor_id=predecessor_id,
        )
        records.sort(key=lambda record: (record.created_at, record.id), reverse=True)
        return records[: max(1, min(int(limit), 10000))]

    save_event_map = save_conversion_event_map
    get_event_map = get_conversion_event_map
    list_event_maps = list_conversion_event_maps

    def save_demand_conversion_evidence(
        self, evidence: DemandConversionEvidence
    ) -> DemandConversionEvidence:
        path = self.demand_conversion_evidence_dir / (
            f"{self._safe_identity(evidence.id)}.json"
        )
        return self._save_immutable(path, evidence, DemandConversionEvidence)

    def get_demand_conversion_evidence(
        self, evidence_id: str
    ) -> DemandConversionEvidence | None:
        path = self.demand_conversion_evidence_dir / (
            f"{self._safe_identity(evidence_id)}.json"
        )
        if not path.exists():
            return None
        evidence = DemandConversionEvidence(**self._read_json(path))
        if evidence.id != evidence_id:
            raise ValueError(
                "demand conversion identity does not match requested loader scope"
            )
        return evidence

    def list_demand_conversion_evidence(
        self,
        *,
        insight_run_id: str | None = None,
        prospect_id: str | None = None,
        vertical_id: str | None = None,
        mode: str | None = None,
        state: str | None = None,
        predecessor_id: str | None = None,
        limit: int = 1000,
    ) -> list[DemandConversionEvidence]:
        records = [
            DemandConversionEvidence(**self._read_json(path))
            for path in self.demand_conversion_evidence_dir.glob("*.json")
        ]
        records = self._filter_records(
            records,
            insight_run_id=insight_run_id,
            prospect_id=prospect_id,
            vertical_id=vertical_id,
            mode=mode,
            state=state,
            predecessor_id=predecessor_id,
        )
        records.sort(key=lambda record: (record.created_at, record.id), reverse=True)
        return records[: max(1, min(int(limit), 10000))]

    save_demand_conversion = save_demand_conversion_evidence
    get_demand_conversion = get_demand_conversion_evidence
    list_demand_conversions = list_demand_conversion_evidence

    def save_demand_conversion_report_snapshot(
        self, snapshot: DemandConversionReportSnapshot
    ) -> DemandConversionReportSnapshot:
        path = self.demand_conversion_reports_dir / (
            f"{self._safe_identity(snapshot.id)}.json"
        )
        return self._save_immutable(
            path,
            snapshot,
            DemandConversionReportSnapshot,
        )

    def get_demand_conversion_report_snapshot(
        self, snapshot_id: str
    ) -> DemandConversionReportSnapshot | None:
        path = self.demand_conversion_reports_dir / (
            f"{self._safe_identity(snapshot_id)}.json"
        )
        if not path.exists():
            return None
        snapshot = DemandConversionReportSnapshot(**self._read_json(path))
        if snapshot.id != snapshot_id:
            raise ValueError(
                "demand conversion report identity does not match requested loader scope"
            )
        return snapshot

    def list_demand_conversion_report_snapshots(
        self,
        *,
        run_id: str | None = None,
        demand_conversion_evidence_id: str | None = None,
        mode: str | None = None,
        limit: int = 1000,
    ) -> list[DemandConversionReportSnapshot]:
        records = [
            DemandConversionReportSnapshot(**self._read_json(path))
            for path in self.demand_conversion_reports_dir.glob("*.json")
        ]
        records = self._filter_records(
            records,
            run_id=run_id,
            demand_conversion_evidence_id=demand_conversion_evidence_id,
            mode=mode,
        )
        records.sort(key=lambda record: (record.created_at, record.id), reverse=True)
        return records[: max(1, min(int(limit), 10000))]

    @staticmethod
    def _filter_records(records: list[Any], **filters: Any) -> list[Any]:
        return [record for record in records if all(value is None or getattr(record, field) == value
                                                    for field, value in filters.items())]

    def _save_immutable(self, path: Path, record: Any, model: type[Any]) -> Any:
        payload = record.to_dict()
        if path.exists():
            existing_payload = self._read_json(path)
            existing_payload.pop("forecast_label", None)
            existing = model(**existing_payload)
            if existing.to_dict() == payload:
                return existing
            raise ValueError(f"{model.__name__} records are immutable")
        self._write_json(path, payload)
        return record

    @staticmethod
    def _agent_call_from_payload(payload: dict[str, Any]) -> AgentCallRecord:
        payload = dict(payload)
        # AgentCallRecord.to_dict exposes this derived convenience property;
        # it is not a constructor field.
        payload.pop("routing_diverged", None)
        return AgentCallRecord(**payload)

    def _run_dir(self, run_id: str) -> Path:
        return self.runs_dir / run_id

    def _package_json_path(self, package: OutreachPackage) -> Path:
        safe_run = self._safe_identity(package.insight_run_id)
        return self.runs_dir / safe_run / "outreach" / f"{self._safe_identity(package.id)}.json"

    def _market_run_path(self, run_id: str, market_run_id: str) -> Path:
        safe_run = self._safe_identity(run_id)
        safe_market = self._safe_identity(market_run_id)
        return self.runs_dir / safe_run / "market" / f"{safe_market}.json"

    def _checkpoint_path(self, run_id: str, attempt_id: str, stage_name: str) -> Path:
        safe_attempt = self._safe_filename(attempt_id)
        safe_stage = self._safe_filename(stage_name)
        if safe_attempt != attempt_id or safe_stage != stage_name:
            raise ValueError("checkpoint identity contains unsafe path characters")
        return self._run_dir(run_id) / "checkpoints" / safe_attempt / f"{safe_stage}.json"

    def _report_alias_path(self, run_id: str, report_contract: str, alias: str) -> Path:
        return (
            self.report_aliases_dir
            / self._safe_identity(run_id)
            / self._safe_identity(report_contract)
            / f"{self._safe_identity(alias)}.json"
        )

    @staticmethod
    def _read_json(path: Path) -> dict:
        import json
        return json.loads(path.read_text(encoding="utf-8"))

    @staticmethod
    def _write_json(path: Path, payload: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_name(f".{path.name}.tmp")
        temporary.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        temporary.replace(path)

    @staticmethod
    def _safe_filename(value: str | None) -> str:
        if not value:
            return "unknown"
        safe = value
        for char in ['<', '>', ':', '"', '/', '\\', '|', '?', '*']:
            safe = safe.replace(char, '-')
        return safe

    @classmethod
    def _safe_identity(cls, value: str) -> str:
        safe = cls._safe_filename(value)
        if not value or safe != value or safe in {".", ".."}:
            raise ValueError("identity contains unsafe path characters")
        return safe
