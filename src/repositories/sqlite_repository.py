from __future__ import annotations

import json
import sqlite3
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
    derive_agentic_review_state,
    RunStageEvent,
    SEOTarget,
    StageCheckpoint,
    VerticalPack,
    OwnedMeasurementSnapshot,
)
from src.repositories.file_repository import FileBackedInsightRepository


class SQLiteInsightRepository:
    """SQLite source of truth with a file artifact mirror.

    SQLite runs in WAL mode with foreign keys and busy timeouts enabled on every
    connection. The JSON payload columns retain forward-compatible domain objects,
    while indexed columns support operational run queries.
    """

    MIGRATIONS_DIR = Path(__file__).resolve().parent / "migrations"

    def __init__(self, database_path: str | Path, artifact_root: str | Path):
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self.artifact_root = Path(artifact_root)
        self._files = FileBackedInsightRepository(self.artifact_root)
        self._migrate()

    def upsert_target(self, target: SEOTarget) -> SEOTarget:
        payload = target.to_dict()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO seo_targets (id, normalized_domain, updated_at, payload_json)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    normalized_domain = excluded.normalized_domain,
                    updated_at = excluded.updated_at,
                    payload_json = excluded.payload_json
                """,
                (target.id, target.normalized_domain, target.updated_at, self._encode(payload)),
            )
        self._files.upsert_target(target)
        return target

    def create_run(self, run: InsightRun) -> InsightRun:
        payload = run.to_dict()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO insight_runs (
                    id, seo_target_id, requested_domain, status, current_stage,
                    created_at, updated_at, payload_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run.id,
                    run.seo_target_id,
                    run.requested_domain,
                    run.status,
                    run.current_stage,
                    run.created_at,
                    run.updated_at,
                    self._encode(payload),
                ),
            )
        self._files.create_run(run)
        return run

    def update_run(self, run: InsightRun) -> InsightRun:
        payload = run.to_dict()
        with self._connect() as connection:
            cursor = connection.execute(
                """
                UPDATE insight_runs
                SET status = ?, current_stage = ?, updated_at = ?, payload_json = ?
                WHERE id = ?
                """,
                (run.status, run.current_stage, run.updated_at, self._encode(payload), run.id),
            )
            if cursor.rowcount != 1:
                raise ValueError(f"run {run.id} not found")
        self._files.update_run(run)
        return run

    def append_stage_event(self, event: RunStageEvent) -> RunStageEvent:
        payload = event.to_dict()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO run_stage_events (
                    id, insight_run_id, stage_name, status, created_at, payload_json
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    event.id,
                    event.insight_run_id,
                    event.stage_name,
                    event.status,
                    event.created_at,
                    self._encode(payload),
                ),
            )
        self._files.append_stage_event(event)
        return event

    def save_discovered_asset(self, asset: DiscoveredAsset) -> DiscoveredAsset:
        payload = asset.to_dict()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO discovered_assets (id, insight_run_id, asset_type, url, payload_json)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET payload_json = excluded.payload_json
                """,
                (asset.id, asset.insight_run_id, asset.asset_type, asset.url, self._encode(payload)),
            )
        self._files.save_discovered_asset(asset)
        return asset

    def save_page_record(self, page: PageRecord) -> PageRecord:
        payload = page.to_dict()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO page_records (id, insight_run_id, url, payload_json)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET url = excluded.url, payload_json = excluded.payload_json
                """,
                (page.id, page.insight_run_id, page.url, self._encode(payload)),
            )
        self._files.save_page_record(page)
        return page

    def list_page_records(self, run_id: str) -> list[PageRecord]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT payload_json FROM page_records WHERE insight_run_id = ? ORDER BY url, id",
                (run_id,),
            ).fetchall()
        return [PageRecord(**self._decode(row[0])) for row in rows]

    def save_report(self, report: InsightReport) -> InsightReport:
        payload = report.to_dict()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO insight_reports (
                    id, insight_run_id, report_version, updated_at, payload_json
                ) VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(insight_run_id, report_version) DO UPDATE SET
                    id = excluded.id,
                    updated_at = excluded.updated_at,
                    payload_json = excluded.payload_json
                """,
                (
                    report.id,
                    report.insight_run_id,
                    report.report_version,
                    report.updated_at,
                    self._encode(payload),
                ),
            )
        self._files.save_report(report)
        return report

    def save_report_snapshot_payload(
        self, run_id: str, payload_sha256: str, payload: dict
    ) -> str:
        if self.get_run(run_id) is None:
            raise ValueError(f"run {run_id} does not exist")
        return self._files.save_report_snapshot_payload(
            run_id,
            payload_sha256,
            payload,
        )

    def save_report_snapshot(self, snapshot: ReportSnapshot) -> ReportSnapshot:
        self._save_immutable_payload(
            "report_snapshots",
            snapshot.id,
            snapshot.to_dict(),
            {
                "run_id": snapshot.run_id,
                "attempt_id": snapshot.attempt_id,
                "report_contract": snapshot.report_contract,
                "schema_version": snapshot.schema_version,
                "payload_sha256": snapshot.payload_sha256,
                "manifest_sha256": snapshot.manifest_sha256,
                "created_at": snapshot.created_at,
            },
            ReportSnapshot,
        )
        self._files.save_report_snapshot(snapshot)
        return snapshot

    def get_report_snapshot(self, snapshot_id: str) -> ReportSnapshot | None:
        payload = self._get_payload("report_snapshots", snapshot_id)
        if payload is None:
            return None
        snapshot = ReportSnapshot(**payload)
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
        rows = self._list_payload(
            "report_snapshots",
            [("run_id", run_id), ("report_contract", report_contract)],
            "created_at",
            limit,
        )
        return [ReportSnapshot(**row) for row in rows]

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

    latest_report_snapshot = get_latest_report_snapshot
    list_report_history = list_report_snapshot_history

    def save_report_comparison_snapshot(
        self, snapshot: ReportComparisonSnapshot
    ) -> ReportComparisonSnapshot:
        self._save_immutable_payload(
            "report_comparison_snapshots",
            snapshot.id,
            snapshot.to_dict(),
            {
                "target_id": snapshot.target_id,
                "baseline_snapshot_id": snapshot.baseline_snapshot_id,
                "current_snapshot_id": snapshot.current_snapshot_id,
                "created_at": snapshot.created_at,
            },
            ReportComparisonSnapshot,
        )
        self._files.save_report_comparison_snapshot(snapshot)
        return snapshot

    def get_report_comparison_snapshot(
        self, snapshot_id: str
    ) -> ReportComparisonSnapshot | None:
        payload = self._get_payload("report_comparison_snapshots", snapshot_id)
        return ReportComparisonSnapshot(**payload) if payload else None

    def list_report_comparison_snapshots(
        self,
        *,
        target_id: str | None = None,
        baseline_snapshot_id: str | None = None,
        current_snapshot_id: str | None = None,
        limit: int = 1000,
    ) -> list[ReportComparisonSnapshot]:
        rows = self._list_payload(
            "report_comparison_snapshots",
            [
                ("target_id", target_id),
                ("baseline_snapshot_id", baseline_snapshot_id),
                ("current_snapshot_id", current_snapshot_id),
            ],
            "created_at",
            limit,
        )
        return [ReportComparisonSnapshot(**row) for row in rows]

    save_comparison_snapshot = save_report_comparison_snapshot
    get_comparison_snapshot = get_report_comparison_snapshot
    list_comparison_snapshots = list_report_comparison_snapshots

    def save_report_alias(self, alias: ReportAlias) -> ReportAlias:
        snapshot = self.get_report_snapshot(alias.snapshot_id)
        if snapshot is None:
            raise ValueError(f"report snapshot {alias.snapshot_id} does not exist")
        if (snapshot.run_id, snapshot.report_contract) != (alias.run_id, alias.report_contract):
            raise ValueError("report alias scope does not match snapshot")
        payload = alias.to_dict()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO report_aliases (
                    id, run_id, report_contract, alias, snapshot_id, updated_at, payload_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(run_id, report_contract, alias) DO UPDATE SET
                    id = excluded.id,
                    snapshot_id = excluded.snapshot_id,
                    updated_at = excluded.updated_at,
                    payload_json = excluded.payload_json
                """,
                (
                    alias.id,
                    alias.run_id,
                    alias.report_contract,
                    alias.alias,
                    alias.snapshot_id,
                    alias.updated_at,
                    self._encode(payload),
                ),
            )
        self._files.save_report_alias(alias)
        return alias

    def get_report_alias(self, run_id: str, report_contract: str, alias: str) -> ReportAlias | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT payload_json FROM report_aliases
                WHERE run_id = ? AND report_contract = ? AND alias = ?
                """,
                (run_id, report_contract, alias),
            ).fetchone()
        if row is None:
            return None
        record = ReportAlias(**self._decode(row[0]))
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
        rows = self._list_payload(
            "report_aliases",
            [("run_id", run_id), ("report_contract", report_contract)],
            "updated_at",
            limit,
        )
        return [ReportAlias(**row) for row in rows]

    def save_client_report_bundle(self, bundle: ClientReportBundle) -> ClientReportBundle:
        snapshot = self.get_report_snapshot(bundle.report_snapshot_id)
        if snapshot is None:
            raise ValueError(f"report snapshot {bundle.report_snapshot_id} does not exist")
        if snapshot.run_id != bundle.run_id:
            raise ValueError("client bundle scope does not match snapshot")
        self._save_immutable_payload(
            "client_report_bundles",
            bundle.id,
            bundle.to_dict(),
            {
                "report_snapshot_id": bundle.report_snapshot_id,
                "run_id": bundle.run_id,
                "manifest_sha256": bundle.manifest_sha256,
                "status": bundle.status,
                "created_at": bundle.created_at,
            },
            ClientReportBundle,
        )
        self._files.save_client_report_bundle(bundle)
        return bundle

    def get_client_report_bundle(self, bundle_id: str) -> ClientReportBundle | None:
        payload = self._get_payload("client_report_bundles", bundle_id)
        if payload is None:
            return None
        bundle = ClientReportBundle(**payload)
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
        rows = self._list_payload(
            "client_report_bundles",
            [("run_id", run_id), ("report_snapshot_id", report_snapshot_id)],
            "created_at",
            limit,
        )
        return [ClientReportBundle(**row) for row in rows]

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
        self._save_immutable_payload(
            "site_evidence_packs", pack.id, pack.to_dict(),
            {"run_id": pack.run_id, "attempt_id": pack.attempt_id,
             "content_sha256": pack.content_sha256, "created_at": pack.created_at},
            SiteEvidencePack,
        )
        self._files.save_site_evidence_pack(pack)
        return pack

    def get_site_evidence_pack(self, pack_id: str) -> SiteEvidencePack | None:
        payload = self._get_payload("site_evidence_packs", pack_id)
        if payload is None:
            return None
        pack = SiteEvidencePack(**payload)
        if pack.id != pack_id:
            raise ValueError("site evidence pack identity does not match requested loader scope")
        return pack

    def list_site_evidence_packs(
        self, *, run_id: str | None = None, limit: int = 1000
    ) -> list[SiteEvidencePack]:
        rows = self._list_payload("site_evidence_packs", [("run_id", run_id)], "created_at", limit)
        return [SiteEvidencePack(**row) for row in rows]

    def save_agentic_analysis_job(self, job: AgenticAnalysisJob) -> AgenticAnalysisJob:
        existing_by_key = self.get_agentic_job_by_idempotency_key(job.idempotency_key)
        if existing_by_key is not None and existing_by_key.id != job.id:
            raise ValueError("agentic job idempotency key already exists")
        payload = job.to_dict()
        with self._connect() as connection:
            row = connection.execute(
                "SELECT payload_json FROM agentic_analysis_jobs WHERE id = ?", (job.id,)
            ).fetchone()
            if row is not None:
                existing = AgenticAnalysisJob(**self._decode(row[0]))
                if existing.to_dict() == payload:
                    return existing
                raise ValueError("agentic analysis jobs require update_agentic_analysis_job for changes")
            connection.execute(
                """
                INSERT INTO agentic_analysis_jobs (
                    id, evidence_pack_id, idempotency_key, state, updated_at, created_at, payload_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (job.id, job.evidence_pack_id, job.idempotency_key, job.state,
                 job.updated_at, job.created_at, self._encode(payload)),
            )
        self._files.save_agentic_analysis_job(job)
        return job

    def update_agentic_analysis_job(self, job: AgenticAnalysisJob) -> AgenticAnalysisJob:
        payload = job.to_dict()
        with self._connect() as connection:
            row = connection.execute(
                "SELECT payload_json FROM agentic_analysis_jobs WHERE id = ?", (job.id,)
            ).fetchone()
            if row is None:
                raise ValueError(f"agentic job {job.id} not found")
            existing = AgenticAnalysisJob(**self._decode(row[0]))
            if existing.idempotency_key != job.idempotency_key or existing.evidence_pack_id != job.evidence_pack_id:
                raise ValueError("agentic job identity fields are immutable")
            connection.execute(
                "UPDATE agentic_analysis_jobs SET state = ?, updated_at = ?, payload_json = ? WHERE id = ?",
                (job.state, job.updated_at, self._encode(payload), job.id),
            )
        self._files.update_agentic_analysis_job(job)
        return job

    def get_agentic_analysis_job(self, job_id: str) -> AgenticAnalysisJob | None:
        payload = self._get_payload("agentic_analysis_jobs", job_id)
        if payload is None:
            return None
        job = AgenticAnalysisJob(**payload)
        if job.id != job_id:
            raise ValueError("agentic job identity does not match requested loader scope")
        return job

    def get_agentic_job_by_idempotency_key(self, idempotency_key: str) -> AgenticAnalysisJob | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT payload_json FROM agentic_analysis_jobs WHERE idempotency_key = ?",
                (idempotency_key,),
            ).fetchone()
        return AgenticAnalysisJob(**self._decode(row[0])) if row else None

    def list_agentic_analysis_jobs(
        self, *, evidence_pack_id: str | None = None, state: str | None = None, limit: int = 1000
    ) -> list[AgenticAnalysisJob]:
        rows = self._list_payload(
            "agentic_analysis_jobs", [("evidence_pack_id", evidence_pack_id), ("state", state)], "updated_at", limit
        )
        return [AgenticAnalysisJob(**row) for row in rows]

    def append_agent_call_record(self, call: AgentCallRecord) -> AgentCallRecord:
        if self.get_agentic_analysis_job(call.job_id) is None:
            raise ValueError(f"agentic job {call.job_id} does not exist")
        payload = call.to_dict()
        stored_payload = dict(payload)
        stored_payload.pop("routing_diverged", None)
        with self._connect() as connection:
            row = connection.execute(
                "SELECT payload_json FROM agent_call_records WHERE id = ?", (call.id,)
            ).fetchone()
            if row is not None:
                existing = self._agent_call_from_payload(self._decode(row[0]))
                if existing.to_dict() == payload:
                    return existing
                raise ValueError("agent call records are append-only")
            connection.execute(
                "INSERT INTO agent_call_records (id, job_id, attempt, status, started_at, payload_json) VALUES (?, ?, ?, ?, ?, ?)",
                (call.id, call.job_id, call.attempt, call.status, call.started_at, self._encode(stored_payload)),
            )
        self._files.append_agent_call_record(call)
        return call

    def get_agent_call_record(self, call_id: str) -> AgentCallRecord | None:
        payload = self._get_payload("agent_call_records", call_id)
        return self._agent_call_from_payload(payload) if payload else None

    def list_agent_call_records(
        self, *, job_id: str | None = None, limit: int = 5000
    ) -> list[AgentCallRecord]:
        rows = self._list_payload("agent_call_records", [("job_id", job_id)], "started_at", limit)
        return [self._agent_call_from_payload(row) for row in rows]

    def save_agentic_assessment_snapshot(self, assessment: AgenticAssessmentSnapshot) -> AgenticAssessmentSnapshot:
        job = self.get_agentic_analysis_job(assessment.job_id)
        if job is None:
            raise ValueError(f"agentic job {assessment.job_id} does not exist")
        if assessment.evidence_pack_id != job.evidence_pack_id:
            raise ValueError("assessment evidence pack does not match job")
        self._save_immutable_payload(
            "agentic_assessment_snapshots", assessment.id, assessment.to_dict(),
            {"job_id": assessment.job_id, "evidence_pack_id": assessment.evidence_pack_id,
             "predecessor_id": assessment.predecessor_id, "created_at": assessment.created_at},
            AgenticAssessmentSnapshot,
        )
        self._files.save_agentic_assessment_snapshot(assessment)
        return assessment

    def get_agentic_assessment_snapshot(self, assessment_id: str) -> AgenticAssessmentSnapshot | None:
        payload = self._get_payload("agentic_assessment_snapshots", assessment_id)
        return AgenticAssessmentSnapshot(**payload) if payload else None

    def list_agentic_assessment_snapshots(
        self, *, job_id: str | None = None, evidence_pack_id: str | None = None,
        predecessor_id: str | None = None, limit: int = 1000,
    ) -> list[AgenticAssessmentSnapshot]:
        rows = self._list_payload(
            "agentic_assessment_snapshots",
            [("job_id", job_id), ("evidence_pack_id", evidence_pack_id), ("predecessor_id", predecessor_id)],
            "created_at", limit,
        )
        return [AgenticAssessmentSnapshot(**row) for row in rows]

    def append_agentic_assessment_review_event(
        self, event: AgenticAssessmentReviewEvent
    ) -> AgenticAssessmentReviewEvent:
        if self.get_agentic_assessment_snapshot(event.assessment_id) is None:
            raise ValueError(f"assessment {event.assessment_id} does not exist")
        payload = event.to_dict()
        with self._connect() as connection:
            row = connection.execute(
                "SELECT payload_json FROM agentic_assessment_review_events WHERE id = ?", (event.id,)
            ).fetchone()
            if row is not None:
                existing = AgenticAssessmentReviewEvent(**self._decode(row[0]))
                if existing.to_dict() == payload:
                    return existing
                raise ValueError("assessment review events are append-only")
            connection.execute(
                "INSERT INTO agentic_assessment_review_events (id, assessment_id, created_at, payload_json) VALUES (?, ?, ?, ?)",
                (event.id, event.assessment_id, event.created_at, self._encode(payload)),
            )
        self._files.append_agentic_assessment_review_event(event)
        return event

    def list_agentic_assessment_review_events(
        self, assessment_id: str, limit: int = 5000
    ) -> list[AgenticAssessmentReviewEvent]:
        rows = self._list_payload(
            "agentic_assessment_review_events", [("assessment_id", assessment_id)], "created_at", limit
        )
        return [AgenticAssessmentReviewEvent(**row) for row in rows]

    def get_agentic_assessment_review_state(self, assessment_id: str) -> str:
        return derive_agentic_review_state(self.list_agentic_assessment_review_events(assessment_id))

    # ------------------------------------------------------------------
    # P12 vertical agentic evidence and durable work queue
    # ------------------------------------------------------------------
    def save_vertical_agentic_pack(self, pack: VerticalAgenticPack) -> VerticalAgenticPack:
        payload = pack.to_dict()
        with self._connect() as connection:
            row = connection.execute(
                "SELECT payload_json FROM vertical_agentic_packs WHERE id = ?", (pack.id,)
            ).fetchone()
            if row is not None:
                existing = VerticalAgenticPack(**self._decode(row[0]))
                if existing.to_dict() == payload:
                    return existing
                raise ValueError("vertical agentic packs are immutable")
            conflict = connection.execute(
                "SELECT id FROM vertical_agentic_packs WHERE vertical_id = ? AND version = ? AND id <> ?",
                (pack.vertical_id, pack.version, pack.id),
            ).fetchone()
            if conflict is not None:
                raise ValueError("vertical agentic pack version already exists")
            connection.execute(
                "INSERT INTO vertical_agentic_packs (id, vertical_id, version, state, created_at, payload_json) VALUES (?, ?, ?, ?, ?, ?)",
                (pack.id, pack.vertical_id, pack.version, pack.state, pack.created_at, self._encode(payload)),
            )
        self._files.save_vertical_agentic_pack(pack)
        return pack

    def get_vertical_agentic_pack(self, pack_id: str) -> VerticalAgenticPack | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT payload_json FROM vertical_agentic_packs WHERE id = ?", (pack_id,)
            ).fetchone()
            if row is None:
                row = connection.execute(
                    "SELECT payload_json FROM vertical_agentic_packs WHERE version = ?",
                    (pack_id,),
                ).fetchone()
        return VerticalAgenticPack(**self._decode(row[0])) if row else None

    def list_vertical_agentic_packs(
        self, *, vertical_id: str | None = None, version: str | None = None,
        state: str | None = None, limit: int = 1000,
    ) -> list[VerticalAgenticPack]:
        rows = self._list_payload(
            "vertical_agentic_packs",
            [("vertical_id", vertical_id), ("version", version), ("state", state)],
            "created_at", limit,
        )
        return [VerticalAgenticPack(**row) for row in rows]

    def save_agentic_work_item(self, item: AgenticWorkItem) -> AgenticWorkItem:
        payload = item.to_dict()
        with self._connect() as connection:
            existing_key = connection.execute(
                "SELECT payload_json FROM agentic_work_items WHERE idempotency_key = ?",
                (item.idempotency_key,),
            ).fetchone()
            if existing_key is not None:
                existing = AgenticWorkItem(**self._decode(existing_key[0]))
                if existing.id != item.id:
                    raise ValueError("agentic work-item idempotency key already exists")
                if existing.to_dict() == payload:
                    return existing
                raise ValueError("agentic work items require update_agentic_work_item for changes")
            row = connection.execute(
                "SELECT payload_json FROM agentic_work_items WHERE id = ?", (item.id,)
            ).fetchone()
            if row is not None:
                existing = AgenticWorkItem(**self._decode(row[0]))
                if existing.to_dict() == payload:
                    return existing
                raise ValueError("agentic work items require update_agentic_work_item for changes")
            connection.execute(
                "INSERT INTO agentic_work_items (id, run_id, attempt_id, evidence_pack_id, idempotency_key, work_kind, mode, state, updated_at, created_at, payload_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    item.id, item.run_id, item.attempt_id, item.evidence_pack_id,
                    item.idempotency_key, item.work_kind, item.mode, item.state,
                    item.updated_at, item.created_at, self._encode(payload),
                ),
            )
        self._files.save_agentic_work_item(item)
        return item

    def update_agentic_work_item(self, item: AgenticWorkItem) -> AgenticWorkItem:
        payload = item.to_dict()
        with self._connect() as connection:
            row = connection.execute(
                "SELECT payload_json FROM agentic_work_items WHERE id = ?", (item.id,)
            ).fetchone()
            if row is None:
                raise ValueError(f"agentic work item {item.id} not found")
            existing = AgenticWorkItem(**self._decode(row[0]))
            immutable = (
                "id", "run_id", "attempt_id", "evidence_pack_id", "vertical_pack_version",
                "work_kind", "mode", "source_sha256", "idempotency_key", "requested_runtime",
                "requested_provider", "requested_model", "prompt_version", "rubric_version",
                "schema_version", "budget_class", "consent_id",
            )
            if any(getattr(existing, field) != getattr(item, field) for field in immutable):
                raise ValueError("agentic work-item identity fields are immutable")
            connection.execute(
                "UPDATE agentic_work_items SET state = ?, updated_at = ?, payload_json = ? WHERE id = ?",
                (item.state, item.updated_at, self._encode(payload), item.id),
            )
        self._files.update_agentic_work_item(item)
        return item

    def get_agentic_work_item(self, item_id: str) -> AgenticWorkItem | None:
        row = self._get_payload("agentic_work_items", item_id)
        return AgenticWorkItem(**row) if row else None

    def get_agentic_work_item_by_idempotency_key(self, idempotency_key: str) -> AgenticWorkItem | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT payload_json FROM agentic_work_items WHERE idempotency_key = ?",
                (idempotency_key,),
            ).fetchone()
        return AgenticWorkItem(**self._decode(row[0])) if row else None

    def list_agentic_work_items(
        self, *, run_id: str | None = None, state: str | None = None,
        work_kind: str | None = None, mode: str | None = None,
        limit: int = 1000,
    ) -> list[AgenticWorkItem]:
        rows = self._list_payload(
            "agentic_work_items",
            [("run_id", run_id), ("state", state), ("work_kind", work_kind), ("mode", mode)],
            "updated_at", limit,
        )
        return [AgenticWorkItem(**row) for row in rows]

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
        payload = step.to_dict()
        with self._connect() as connection:
            row = connection.execute(
                "SELECT payload_json FROM agentic_tool_steps WHERE id = ?", (step.id,)
            ).fetchone()
            if row is not None:
                existing = AgenticToolStep(**self._decode(row[0]))
                if existing.to_dict() == payload:
                    return existing
                raise ValueError("agentic tool steps are append-only")
            duplicate_sequence = connection.execute(
                "SELECT payload_json FROM agentic_tool_steps WHERE work_item_id = ? AND sequence = ?",
                (step.work_item_id, step.sequence),
            ).fetchone()
            if duplicate_sequence is not None:
                existing = AgenticToolStep(**self._decode(duplicate_sequence[0]))
                if existing.to_dict() == payload:
                    return existing
                raise ValueError("agentic tool-step sequence is append-only")
            connection.execute(
                "INSERT INTO agentic_tool_steps (id, work_item_id, sequence, action_kind, policy_decision, created_at, payload_json) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (step.id, step.work_item_id, step.sequence, step.action_kind, step.policy_decision, step.created_at, self._encode(payload)),
            )
        self._files.append_agentic_tool_step(step)
        return step

    def get_agentic_tool_step(self, step_id: str) -> AgenticToolStep | None:
        row = self._get_payload("agentic_tool_steps", step_id)
        return AgenticToolStep(**row) if row else None

    def list_agentic_tool_steps(
        self, *, work_item_id: str | None = None, limit: int = 5000
    ) -> list[AgenticToolStep]:
        rows = self._list_payload(
            "agentic_tool_steps", [("work_item_id", work_item_id)], "created_at", limit
        )
        records = [AgenticToolStep(**row) for row in rows]
        records.sort(key=lambda item: (item.work_item_id, item.sequence, item.created_at, item.id))
        return records[: max(1, min(int(limit), 50000))]

    def _save_p12_snapshot(self, snapshot: Any, table: str, snapshot_type: str) -> Any:
        work_item_id = getattr(snapshot, "work_item_id", None)
        if work_item_id and self.get_agentic_work_item(work_item_id) is None:
            raise ValueError(f"agentic work item {work_item_id} does not exist")
        payload = snapshot.to_dict()
        columns = {
            "snapshot_type": snapshot_type,
            "run_id": getattr(snapshot, "run_id", None),
            "work_item_id": work_item_id,
            "mode": getattr(snapshot, "mode", None),
            "prospect_id": getattr(snapshot, "prospect_id", None),
            "created_at": snapshot.created_at,
        }
        # All P12 snapshots share one additive table. The table is immutable
        # by id, while model-specific readers reconstruct the typed payload.
        self._save_immutable_payload(
            "vertical_agentic_snapshots", snapshot.id, payload, columns, type(snapshot)
        )
        self._files._save_agentic_snapshot(
            getattr(self._files, {
                "business_fact_ledger": "business_fact_ledgers_dir",
                "decision_coverage": "decision_coverage_dir",
                "journey_evidence": "journey_evidence_runs_dir",
                "ai_representation_accuracy": "ai_representation_accuracy_dir",
                "owner_diagnostic": "owner_diagnostics_dir",
                "remediation_blueprint": "remediation_blueprints_dir",
            }.get(snapshot_type, "vertical_agentic_packs_dir")),
            snapshot,
            type(snapshot),
        )
        return snapshot

    def _get_p12_snapshot(self, snapshot_id: str, model: type[Any]) -> Any | None:
        row = self._get_payload("vertical_agentic_snapshots", snapshot_id)
        return model(**row) if row else None

    def _list_p12_snapshots(self, model: type[Any], *, snapshot_type: str, limit: int = 1000, **filters: Any) -> list[Any]:
        query_filters = [("snapshot_type", snapshot_type)]
        query_filters.extend((name, value) for name, value in filters.items() if value is not None)
        rows = self._list_payload("vertical_agentic_snapshots", query_filters, "created_at", limit)
        return [model(**row) for row in rows]

    def save_business_fact_ledger_snapshot(self, snapshot: BusinessFactLedgerSnapshot) -> BusinessFactLedgerSnapshot:
        return self._save_p12_snapshot(snapshot, "vertical_agentic_snapshots", "business_fact_ledger")

    def get_business_fact_ledger_snapshot(self, snapshot_id: str) -> BusinessFactLedgerSnapshot | None:
        return self._get_p12_snapshot(snapshot_id, BusinessFactLedgerSnapshot)

    def list_business_fact_ledger_snapshots(self, *, run_id: str | None = None, work_item_id: str | None = None, mode: str | None = None, limit: int = 1000) -> list[BusinessFactLedgerSnapshot]:
        return self._list_p12_snapshots(BusinessFactLedgerSnapshot, snapshot_type="business_fact_ledger", run_id=run_id, work_item_id=work_item_id, mode=mode, limit=limit)

    def save_decision_coverage_snapshot(self, snapshot: DecisionCoverageSnapshot) -> DecisionCoverageSnapshot:
        return self._save_p12_snapshot(snapshot, "vertical_agentic_snapshots", "decision_coverage")

    def get_decision_coverage_snapshot(self, snapshot_id: str) -> DecisionCoverageSnapshot | None:
        return self._get_p12_snapshot(snapshot_id, DecisionCoverageSnapshot)

    def list_decision_coverage_snapshots(self, *, run_id: str | None = None, work_item_id: str | None = None, mode: str | None = None, limit: int = 1000) -> list[DecisionCoverageSnapshot]:
        return self._list_p12_snapshots(DecisionCoverageSnapshot, snapshot_type="decision_coverage", run_id=run_id, work_item_id=work_item_id, mode=mode, limit=limit)

    def save_journey_evidence_run(self, evidence: JourneyEvidenceRun) -> JourneyEvidenceRun:
        return self._save_p12_snapshot(evidence, "vertical_agentic_snapshots", "journey_evidence")

    def get_journey_evidence_run(self, evidence_id: str) -> JourneyEvidenceRun | None:
        return self._get_p12_snapshot(evidence_id, JourneyEvidenceRun)

    def list_journey_evidence_runs(self, *, run_id: str | None = None, work_item_id: str | None = None, mode: str | None = None, limit: int = 1000) -> list[JourneyEvidenceRun]:
        return self._list_p12_snapshots(JourneyEvidenceRun, snapshot_type="journey_evidence", run_id=run_id, work_item_id=work_item_id, mode=mode, limit=limit)

    def save_ai_representation_accuracy_snapshot(self, snapshot: AIRepresentationAccuracySnapshot) -> AIRepresentationAccuracySnapshot:
        return self._save_p12_snapshot(snapshot, "vertical_agentic_snapshots", "ai_representation_accuracy")

    def get_ai_representation_accuracy_snapshot(self, snapshot_id: str) -> AIRepresentationAccuracySnapshot | None:
        return self._get_p12_snapshot(snapshot_id, AIRepresentationAccuracySnapshot)

    def list_ai_representation_accuracy_snapshots(self, *, run_id: str | None = None, work_item_id: str | None = None, mode: str | None = None, limit: int = 1000) -> list[AIRepresentationAccuracySnapshot]:
        return self._list_p12_snapshots(AIRepresentationAccuracySnapshot, snapshot_type="ai_representation_accuracy", run_id=run_id, work_item_id=work_item_id, mode=mode, limit=limit)

    def save_owner_diagnostic_snapshot(self, snapshot: OwnerDiagnosticSnapshot) -> OwnerDiagnosticSnapshot:
        return self._save_p12_snapshot(snapshot, "vertical_agentic_snapshots", "owner_diagnostic")

    def get_owner_diagnostic_snapshot(self, snapshot_id: str) -> OwnerDiagnosticSnapshot | None:
        return self._get_p12_snapshot(snapshot_id, OwnerDiagnosticSnapshot)

    def list_owner_diagnostic_snapshots(self, *, run_id: str | None = None, prospect_id: str | None = None, limit: int = 1000) -> list[OwnerDiagnosticSnapshot]:
        return self._list_p12_snapshots(OwnerDiagnosticSnapshot, snapshot_type="owner_diagnostic", run_id=run_id, prospect_id=prospect_id, limit=limit)

    def save_remediation_blueprint_snapshot(self, snapshot: RemediationBlueprintSnapshot) -> RemediationBlueprintSnapshot:
        return self._save_p12_snapshot(snapshot, "vertical_agentic_snapshots", "remediation_blueprint")

    def get_remediation_blueprint_snapshot(self, snapshot_id: str) -> RemediationBlueprintSnapshot | None:
        return self._get_p12_snapshot(snapshot_id, RemediationBlueprintSnapshot)

    def list_remediation_blueprint_snapshots(self, *, run_id: str | None = None, work_item_id: str | None = None, mode: str | None = None, limit: int = 1000) -> list[RemediationBlueprintSnapshot]:
        return self._list_p12_snapshots(RemediationBlueprintSnapshot, snapshot_type="remediation_blueprint", run_id=run_id, work_item_id=work_item_id, mode=mode, limit=limit)

    def save_recommendation_outcome_link(self, link: RecommendationOutcomeLink) -> RecommendationOutcomeLink:
        self._save_immutable_payload(
            "recommendation_outcome_links", link.id, link.to_dict(),
            {"recommendation_id": link.recommendation_id, "source_snapshot_id": link.source_snapshot_id,
             "outreach_package_id": link.outreach_package_id, "prospect_id": link.prospect_id,
             "vertical_id": link.vertical_id, "created_at": link.created_at},
            RecommendationOutcomeLink,
        )
        self._files.save_recommendation_outcome_link(link)
        return link

    def get_recommendation_outcome_link(self, link_id: str) -> RecommendationOutcomeLink | None:
        row = self._get_payload("recommendation_outcome_links", link_id)
        return RecommendationOutcomeLink(**row) if row else None

    def list_recommendation_outcome_links(self, *, prospect_id: str | None = None, vertical_id: str | None = None, recommendation_id: str | None = None, limit: int = 1000) -> list[RecommendationOutcomeLink]:
        rows = self._list_payload(
            "recommendation_outcome_links",
            [("prospect_id", prospect_id), ("vertical_id", vertical_id), ("recommendation_id", recommendation_id)],
            "created_at", limit,
        )
        return [RecommendationOutcomeLink(**row) for row in rows]

    def append_agentic_evidence_review_event(self, event: AgenticEvidenceReviewEvent) -> AgenticEvidenceReviewEvent:
        payload = event.to_dict()
        if self._get_p12_snapshot(event.snapshot_id, {
            "business_fact_ledger": BusinessFactLedgerSnapshot,
            "decision_coverage": DecisionCoverageSnapshot,
            "journey_evidence": JourneyEvidenceRun,
            "ai_representation_accuracy": AIRepresentationAccuracySnapshot,
            "owner_diagnostic": OwnerDiagnosticSnapshot,
            "remediation_blueprint": RemediationBlueprintSnapshot,
        }.get(event.snapshot_type.casefold().replace("-", "_"), BusinessFactLedgerSnapshot)) is None:
            raise ValueError(f"agentic evidence snapshot {event.snapshot_id} does not exist")
        with self._connect() as connection:
            row = connection.execute(
                "SELECT payload_json FROM agentic_evidence_review_events WHERE id = ?", (event.id,)
            ).fetchone()
            if row is not None:
                existing = AgenticEvidenceReviewEvent(**self._decode(row[0]))
                if existing.to_dict() == payload:
                    return existing
                raise ValueError("agentic evidence review events are append-only")
            connection.execute(
                "INSERT INTO agentic_evidence_review_events (id, snapshot_id, snapshot_type, event_type, created_at, payload_json) VALUES (?, ?, ?, ?, ?, ?)",
                (event.id, event.snapshot_id, event.snapshot_type, event.event_type, event.created_at, self._encode(payload)),
            )
        self._files.append_agentic_evidence_review_event(event)
        return event

    def list_agentic_evidence_review_events(self, snapshot_id: str, *, limit: int = 5000) -> list[AgenticEvidenceReviewEvent]:
        rows = self._list_payload("agentic_evidence_review_events", [("snapshot_id", snapshot_id)], "created_at", limit)
        return [AgenticEvidenceReviewEvent(**row) for row in rows]

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

    @staticmethod
    def _agent_call_from_payload(payload: dict[str, Any]) -> AgentCallRecord:
        payload = dict(payload)
        payload.pop("routing_diverged", None)
        return AgentCallRecord(**payload)

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
        payload = checkpoint.to_dict()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO stage_checkpoints (
                    id, insight_run_id, attempt_id, stage_name, payload_type,
                    schema_version, content_sha256, created_at, payload_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(insight_run_id, attempt_id, stage_name) DO UPDATE SET
                    id = excluded.id,
                    payload_type = excluded.payload_type,
                    schema_version = excluded.schema_version,
                    content_sha256 = excluded.content_sha256,
                    created_at = excluded.created_at,
                    payload_json = excluded.payload_json
                """,
                (
                    checkpoint.id,
                    checkpoint.insight_run_id,
                    checkpoint.attempt_id,
                    checkpoint.stage_name,
                    checkpoint.payload_type,
                    checkpoint.schema_version,
                    checkpoint.content_sha256,
                    checkpoint.created_at,
                    self._encode(checkpoint.payload),
                ),
            )
        self._files.save_checkpoint(checkpoint)
        return checkpoint

    def get_run(self, run_id: str) -> InsightRun | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT payload_json FROM insight_runs WHERE id = ?", (run_id,)
            ).fetchone()
        return InsightRun(**self._decode(row[0])) if row else None

    def list_runs(self, limit: int = 20) -> list[InsightRun]:
        safe_limit = max(1, min(int(limit), 1000))
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT payload_json FROM insight_runs ORDER BY updated_at DESC, id DESC LIMIT ?",
                (safe_limit,),
            ).fetchall()
        return [InsightRun(**self._decode(row[0])) for row in rows]

    def list_stage_events(self, run_id: str) -> list[RunStageEvent]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT payload_json FROM run_stage_events
                WHERE insight_run_id = ?
                ORDER BY created_at, id
                """,
                (run_id,),
            ).fetchall()
        return [RunStageEvent(**self._decode(row[0])) for row in rows]

    def get_report(self, run_id: str, report_version: str) -> InsightReport | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT payload_json FROM insight_reports
                WHERE insight_run_id = ? AND report_version = ?
                """,
                (run_id, report_version),
            ).fetchone()
        return InsightReport(**self._decode(row[0])) if row else None

    def get_checkpoint(self, run_id: str, attempt_id: str, stage_name: str) -> StageCheckpoint | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT id, insight_run_id, attempt_id, stage_name, payload_type,
                       schema_version, content_sha256, created_at, payload_json
                FROM stage_checkpoints
                WHERE insight_run_id = ? AND attempt_id = ? AND stage_name = ?
                """,
                (run_id, attempt_id, stage_name),
            ).fetchone()
        if row is None:
            return None
        return StageCheckpoint(
            id=row[0],
            insight_run_id=row[1],
            attempt_id=row[2],
            stage_name=row[3],
            payload_type=row[4],
            schema_version=row[5],
            content_sha256=row[6],
            created_at=row[7],
            payload=self._decode(row[8]),
        )

    def save_vertical_pack(self, pack: VerticalPack) -> VerticalPack:
        payload = pack.to_dict()
        with self._connect() as connection:
            row = connection.execute(
                "SELECT payload_json FROM vertical_packs WHERE pack_id = ?", (pack.pack_id,)
            ).fetchone()
            if row is not None:
                existing = VerticalPack(**self._decode(row[0]))
                if existing.to_dict() != payload:
                    raise ValueError(f"vertical pack {pack.pack_id} is immutable")
                return existing
            connection.execute(
                "INSERT INTO vertical_packs (pack_id, vertical_id, version, payload_json) VALUES (?, ?, ?, ?)",
                (pack.pack_id, pack.vertical_id, pack.version, self._encode(payload)),
            )
        self._files.save_vertical_pack(pack)
        return pack

    def get_vertical_pack(self, pack_id: str) -> VerticalPack | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT payload_json FROM vertical_packs WHERE pack_id = ?", (pack_id,)
            ).fetchone()
        return VerticalPack(**self._decode(row[0])) if row else None

    def list_vertical_packs(self) -> list[VerticalPack]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT payload_json FROM vertical_packs ORDER BY vertical_id, version, pack_id"
            ).fetchall()
        return [VerticalPack(**self._decode(row[0])) for row in rows]

    def save_prospect(self, prospect: ProspectRecord) -> ProspectRecord:
        payload = prospect.to_dict()
        with self._connect() as connection:
            duplicate = connection.execute(
                """
                SELECT id FROM prospects
                WHERE vertical_id = ? AND normalized_domain = ? AND id <> ?
                """,
                (prospect.vertical_id, prospect.normalized_domain, prospect.id),
            ).fetchone()
            if duplicate is not None:
                raise ValueError("prospect already exists for vertical and normalized domain")
            connection.execute(
                """
                INSERT INTO prospects (
                    id, vertical_id, vertical_pack_version, normalized_domain,
                    qualification_status, updated_at, payload_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    vertical_id = excluded.vertical_id,
                    vertical_pack_version = excluded.vertical_pack_version,
                    normalized_domain = excluded.normalized_domain,
                    qualification_status = excluded.qualification_status,
                    updated_at = excluded.updated_at,
                    payload_json = excluded.payload_json
                """,
                (
                    prospect.id,
                    prospect.vertical_id,
                    prospect.vertical_pack_version,
                    prospect.normalized_domain,
                    prospect.qualification_status,
                    prospect.updated_at,
                    self._encode(payload),
                ),
            )
        self._files.save_prospect(prospect)
        return prospect

    def get_prospect(self, prospect_id: str) -> ProspectRecord | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT payload_json FROM prospects WHERE id = ?", (prospect_id,)
            ).fetchone()
        return ProspectRecord(**self._decode(row[0])) if row else None

    def list_prospects(
        self,
        *,
        vertical_id: str | None = None,
        qualification_status: str | None = None,
        limit: int = 1000,
    ) -> list[ProspectRecord]:
        clauses: list[str] = []
        args: list[Any] = []
        if vertical_id is not None:
            clauses.append("vertical_id = ?")
            args.append(vertical_id)
        if qualification_status is not None:
            clauses.append("qualification_status = ?")
            args.append(qualification_status)
        args.append(max(1, min(int(limit), 10000)))
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        with self._connect() as connection:
            rows = connection.execute(
                f"SELECT payload_json FROM prospects {where} ORDER BY updated_at DESC, id DESC LIMIT ?", args
            ).fetchall()
        return [ProspectRecord(**self._decode(row[0])) for row in rows]

    def save_keyword_set(self, keyword_set: KeywordSet) -> KeywordSet:
        payload = keyword_set.to_dict()
        with self._connect() as connection:
            row = connection.execute(
                "SELECT payload_json FROM keyword_sets WHERE id = ?", (keyword_set.id,)
            ).fetchone()
            if row is not None:
                existing = KeywordSet(**self._decode(row[0]))
                if existing.to_dict() == payload:
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
            conflict = connection.execute(
                "SELECT id FROM keyword_sets WHERE keyword_set_key = ? AND id <> ?",
                (keyword_set.keyword_set_key, keyword_set.id),
            ).fetchone()
            if conflict is not None:
                raise ValueError(f"keyword set version already exists: {keyword_set.keyword_set_key}")
            connection.execute(
                """
                INSERT INTO keyword_sets (
                    id, keyword_set_key, vertical_id, normalized_domain,
                    state, updated_at, payload_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    keyword_set_key = excluded.keyword_set_key,
                    vertical_id = excluded.vertical_id,
                    normalized_domain = excluded.normalized_domain,
                    state = excluded.state,
                    updated_at = excluded.updated_at,
                    payload_json = excluded.payload_json
                """,
                (
                    keyword_set.id,
                    keyword_set.keyword_set_key,
                    keyword_set.vertical_id,
                    keyword_set.normalized_domain,
                    keyword_set.state,
                    keyword_set.updated_at,
                    self._encode(payload),
                ),
            )
        self._files.save_keyword_set(keyword_set)
        return keyword_set

    def get_keyword_set(self, keyword_set_id: str) -> KeywordSet | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT payload_json FROM keyword_sets WHERE id = ?", (keyword_set_id,)
            ).fetchone()
        return KeywordSet(**self._decode(row[0])) if row else None

    def list_keyword_sets(
        self,
        *,
        vertical_id: str | None = None,
        normalized_domain: str | None = None,
        state: str | None = None,
        limit: int = 1000,
    ) -> list[KeywordSet]:
        clauses: list[str] = []
        args: list[Any] = []
        for field_name, value in (
            ("vertical_id", vertical_id),
            ("normalized_domain", normalized_domain),
            ("state", state),
        ):
            if value is not None:
                clauses.append(f"{field_name} = ?")
                args.append(value)
        args.append(max(1, min(int(limit), 10000)))
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        with self._connect() as connection:
            rows = connection.execute(
                f"SELECT payload_json FROM keyword_sets {where} ORDER BY updated_at DESC, id DESC LIMIT ?",
                args,
            ).fetchall()
        return [KeywordSet(**self._decode(row[0])) for row in rows]

    def save_keyword_set_binding(self, binding: KeywordSetBinding) -> KeywordSetBinding:
        payload = binding.to_dict()
        with self._connect() as connection:
            row = connection.execute(
                "SELECT payload_json FROM keyword_set_bindings WHERE id = ?", (binding.id,)
            ).fetchone()
            if row is not None:
                existing = KeywordSetBinding(**self._decode(row[0]))
                if existing.to_dict() != payload:
                    raise ValueError("keyword-set bindings are immutable")
                return existing
            duplicate = connection.execute(
                """
                SELECT payload_json FROM keyword_set_bindings
                WHERE vertical_id = ? AND normalized_domain = ? AND state = 'active'
                """,
                (binding.vertical_id, binding.normalized_domain),
            ).fetchone()
            if duplicate is not None:
                existing = KeywordSetBinding(**self._decode(duplicate[0]))
                if existing.keyword_set_id == binding.keyword_set_id and existing.prospect_id == binding.prospect_id:
                    return existing
                raise ValueError("domain already has an active keyword-set binding for this vertical")
            connection.execute(
                """
                INSERT INTO keyword_set_bindings (
                    id, keyword_set_id, vertical_id, normalized_domain,
                    prospect_id, state, created_at, payload_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    binding.id,
                    binding.keyword_set_id,
                    binding.vertical_id,
                    binding.normalized_domain,
                    binding.prospect_id,
                    binding.state,
                    binding.created_at,
                    self._encode(payload),
                ),
            )
        self._files.save_keyword_set_binding(binding)
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
        clauses: list[str] = []
        args: list[Any] = []
        for field_name, value in (
            ("keyword_set_id", keyword_set_id),
            ("normalized_domain", normalized_domain),
            ("prospect_id", prospect_id),
            ("state", state),
        ):
            if value is not None:
                clauses.append(f"{field_name} = ?")
                args.append(value)
        args.append(max(1, min(int(limit), 10000)))
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        with self._connect() as connection:
            rows = connection.execute(
                f"SELECT payload_json FROM keyword_set_bindings {where} ORDER BY created_at DESC, id DESC LIMIT ?",
                args,
            ).fetchall()
        return [KeywordSetBinding(**self._decode(row[0])) for row in rows]

    def save_market_evidence_run(self, market_run: MarketEvidenceRun) -> MarketEvidenceRun:
        payload = market_run.to_dict()
        with self._connect() as connection:
            row = connection.execute(
                "SELECT payload_json FROM market_evidence_runs WHERE id = ?", (market_run.id,)
            ).fetchone()
            if row is not None:
                existing = MarketEvidenceRun(**self._decode(row[0]))
                if existing.to_dict() == payload:
                    return existing
                if existing.state in {"complete", "failed", "superseded"}:
                    raise ValueError("terminal market evidence runs are immutable")
            connection.execute(
                """
                INSERT INTO market_evidence_runs (
                    id, insight_run_id, keyword_set_id, state, updated_at, payload_json
                ) VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    insight_run_id = excluded.insight_run_id,
                    keyword_set_id = excluded.keyword_set_id,
                    state = excluded.state,
                    updated_at = excluded.updated_at,
                    payload_json = excluded.payload_json
                """,
                (
                    market_run.id,
                    market_run.insight_run_id,
                    market_run.keyword_set_id,
                    market_run.state,
                    market_run.updated_at,
                    self._encode(payload),
                ),
            )
        self._files.save_market_evidence_run(market_run)
        return market_run

    def get_market_evidence_run(self, market_run_id: str) -> MarketEvidenceRun | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT payload_json FROM market_evidence_runs WHERE id = ?", (market_run_id,)
            ).fetchone()
        return MarketEvidenceRun(**self._decode(row[0])) if row else None

    def list_market_evidence_runs(
        self,
        *,
        insight_run_id: str | None = None,
        state: str | None = None,
        limit: int = 1000,
    ) -> list[MarketEvidenceRun]:
        clauses: list[str] = []
        args: list[Any] = []
        if insight_run_id is not None:
            clauses.append("insight_run_id = ?")
            args.append(insight_run_id)
        if state is not None:
            clauses.append("state = ?")
            args.append(state)
        args.append(max(1, min(int(limit), 10000)))
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        with self._connect() as connection:
            rows = connection.execute(
                f"SELECT payload_json FROM market_evidence_runs {where} ORDER BY updated_at DESC, id DESC LIMIT ?",
                args,
            ).fetchall()
        return [MarketEvidenceRun(**self._decode(row[0])) for row in rows]

    def save_market_artifact(
        self,
        insight_run_id: str,
        market_run_id: str,
        relative_path: str,
        payload: dict | bytes,
    ) -> str:
        return self._files.save_market_artifact(
            insight_run_id,
            market_run_id,
            relative_path,
            payload,
        )

    def save_opportunity_artifact(
        self,
        insight_run_id: str,
        scenario_id: str,
        relative_path: str,
        payload: dict | bytes,
    ) -> str:
        return self._files.save_opportunity_artifact(
            insight_run_id,
            scenario_id,
            relative_path,
            payload,
        )

    def save_outreach_package(self, package: OutreachPackage) -> OutreachPackage:
        payload = package.to_dict()
        with self._connect() as connection:
            row = connection.execute(
                "SELECT payload_json FROM outreach_packages WHERE id = ?", (package.id,)
            ).fetchone()
            if row is not None:
                existing = OutreachPackage(**self._decode(row[0]))
                if existing.to_dict() == payload:
                    return existing
                if existing.state in {"approved", "superseded"}:
                    raise ValueError("approved outreach packages are immutable")
            conflict = connection.execute(
                """
                SELECT id FROM outreach_packages
                WHERE insight_run_id = ? AND prospect_id = ? AND report_version = ?
                  AND package_version = ? AND id <> ?
                """,
                (
                    package.insight_run_id,
                    package.prospect_id,
                    package.report_version,
                    package.package_version,
                    package.id,
                ),
            ).fetchone()
            if conflict is not None:
                raise ValueError("outreach package version already exists")
            connection.execute(
                """
                INSERT INTO outreach_packages (
                    id, insight_run_id, prospect_id, report_version,
                    package_version, state, updated_at, payload_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    insight_run_id = excluded.insight_run_id,
                    prospect_id = excluded.prospect_id,
                    report_version = excluded.report_version,
                    package_version = excluded.package_version,
                    state = excluded.state,
                    updated_at = excluded.updated_at,
                    payload_json = excluded.payload_json
                """,
                (
                    package.id,
                    package.insight_run_id,
                    package.prospect_id,
                    package.report_version,
                    package.package_version,
                    package.state,
                    package.updated_at,
                    self._encode(payload),
                ),
            )
        self._files.save_outreach_package(package)
        return package

    def get_outreach_package(self, package_id: str) -> OutreachPackage | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT payload_json FROM outreach_packages WHERE id = ?", (package_id,)
            ).fetchone()
        return OutreachPackage(**self._decode(row[0])) if row else None

    def list_outreach_packages(
        self,
        *,
        prospect_id: str | None = None,
        insight_run_id: str | None = None,
        state: str | None = None,
        limit: int = 1000,
    ) -> list[OutreachPackage]:
        clauses: list[str] = []
        args: list[Any] = []
        for field_name, value in (("prospect_id", prospect_id), ("insight_run_id", insight_run_id), ("state", state)):
            if value is not None:
                clauses.append(f"{field_name} = ?")
                args.append(value)
        args.append(max(1, min(int(limit), 10000)))
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        with self._connect() as connection:
            rows = connection.execute(
                f"SELECT payload_json FROM outreach_packages {where} ORDER BY updated_at DESC, id DESC LIMIT ?", args
            ).fetchall()
        return [OutreachPackage(**self._decode(row[0])) for row in rows]

    def append_activation_event(self, event: OutreachActivationEvent) -> OutreachActivationEvent:
        payload = event.to_dict()
        with self._connect() as connection:
            row = connection.execute(
                "SELECT payload_json FROM outreach_activation_events WHERE id = ?", (event.id,)
            ).fetchone()
            if row is not None:
                existing = OutreachActivationEvent(**self._decode(row[0]))
                if existing.to_dict() != payload:
                    raise ValueError("activation events are append-only")
                return existing
            connection.execute(
                """
                INSERT INTO outreach_activation_events (
                    id, insight_run_id, outreach_package_id, package_version,
                    stage, vertical_id, occurred_at, payload_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event.id,
                    event.insight_run_id,
                    event.outreach_package_id,
                    event.package_version,
                    event.stage,
                    event.vertical_id,
                    event.occurred_at,
                    self._encode(payload),
                ),
            )
        self._files.append_activation_event(event)
        return event

    def list_activation_events(
        self,
        *,
        insight_run_id: str | None = None,
        outreach_package_id: str | None = None,
        vertical_id: str | None = None,
        limit: int = 5000,
    ) -> list[OutreachActivationEvent]:
        clauses: list[str] = []
        args: list[Any] = []
        for field_name, value in (("insight_run_id", insight_run_id), ("outreach_package_id", outreach_package_id), ("vertical_id", vertical_id)):
            if value is not None:
                clauses.append(f"{field_name} = ?")
                args.append(value)
        args.append(max(1, min(int(limit), 50000)))
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        with self._connect() as connection:
            rows = connection.execute(
                f"SELECT payload_json FROM outreach_activation_events {where} ORDER BY occurred_at, id LIMIT ?", args
            ).fetchall()
        return [OutreachActivationEvent(**self._decode(row[0])) for row in rows]

    def save_demand_evidence_set(self, evidence: DemandEvidenceSet) -> DemandEvidenceSet:
        payload = evidence.to_dict()
        self._save_immutable_payload(
            "demand_evidence_sets", evidence.id, payload,
            {"prospect_id": evidence.prospect_id, "keyword_set_id": evidence.keyword_set_id,
             "vertical_id": evidence.vertical_id, "state": evidence.state,
             "version": evidence.version, "predecessor_id": evidence.predecessor_id,
             "superseded_by_id": evidence.superseded_by_id,
             "created_at": evidence.created_at},
            DemandEvidenceSet,
        )
        self._files.save_demand_evidence_set(evidence)
        return evidence

    def get_demand_evidence_set(self, evidence_id: str) -> DemandEvidenceSet | None:
        row = self._get_payload("demand_evidence_sets", evidence_id)
        return DemandEvidenceSet(**row) if row else None

    def list_demand_evidence_sets(self, *, prospect_id: str | None = None, keyword_set_id: str | None = None,
                                  state: str | None = None, predecessor_id: str | None = None,
                                  superseded_by_id: str | None = None,
                                  limit: int = 1000) -> list[DemandEvidenceSet]:
        rows = self._list_payload("demand_evidence_sets", [
            ("prospect_id", prospect_id), ("keyword_set_id", keyword_set_id),
            ("state", state), ("predecessor_id", predecessor_id), ("superseded_by_id", superseded_by_id),
        ], "created_at", limit)
        return [DemandEvidenceSet(**row) for row in rows]

    save_demand_evidence = save_demand_evidence_set
    get_demand_evidence = get_demand_evidence_set
    list_demand_evidence = list_demand_evidence_sets

    def save_business_economics_profile(self, profile: BusinessEconomicsProfile) -> BusinessEconomicsProfile:
        self._save_immutable_payload(
            "business_economics_profiles", profile.id, profile.to_dict(),
             {"prospect_id": profile.prospect_id, "vertical_id": profile.vertical_id,
             "state": profile.state, "version": profile.version,
             "predecessor_id": profile.predecessor_id,
             "superseded_by_id": profile.superseded_by_id, "created_at": profile.created_at},
            BusinessEconomicsProfile,
        )
        self._files.save_business_economics_profile(profile)
        return profile

    save_economics_profile = save_business_economics_profile

    def get_business_economics_profile(self, profile_id: str) -> BusinessEconomicsProfile | None:
        row = self._get_payload("business_economics_profiles", profile_id)
        return BusinessEconomicsProfile(**row) if row else None

    get_economics_profile = get_business_economics_profile

    def list_business_economics_profiles(self, *, prospect_id: str | None = None, vertical_id: str | None = None,
                                         state: str | None = None, predecessor_id: str | None = None,
                                         superseded_by_id: str | None = None,
                                         limit: int = 1000) -> list[BusinessEconomicsProfile]:
        rows = self._list_payload("business_economics_profiles", [
            ("prospect_id", prospect_id), ("vertical_id", vertical_id),
            ("state", state), ("predecessor_id", predecessor_id), ("superseded_by_id", superseded_by_id),
        ], "created_at", limit)
        return [BusinessEconomicsProfile(**row) for row in rows]

    list_economics_profiles = list_business_economics_profiles

    def save_opportunity_scenario(self, scenario: OpportunityScenario) -> OpportunityScenario:
        self._save_immutable_payload(
            "opportunity_scenarios", scenario.id, scenario.to_dict(),
            {"insight_run_id": scenario.insight_run_id, "prospect_id": scenario.prospect_id,
             "state": scenario.state, "status": scenario.status,
             "predecessor_id": scenario.predecessor_id,
             "calibrated_from_id": scenario.calibrated_from_id, "created_at": scenario.created_at},
            OpportunityScenario,
        )
        self._files.save_opportunity_scenario(scenario)
        return scenario

    def get_opportunity_scenario(self, scenario_id: str) -> OpportunityScenario | None:
        row = self._get_payload("opportunity_scenarios", scenario_id)
        if row:
            row.pop("forecast_label", None)
        return OpportunityScenario(**row) if row else None

    def list_opportunity_scenarios(self, *, insight_run_id: str | None = None, prospect_id: str | None = None,
                                   state: str | None = None, predecessor_id: str | None = None,
                                   calibrated_from_id: str | None = None, limit: int = 1000) -> list[OpportunityScenario]:
        rows = self._list_payload("opportunity_scenarios", [
            ("insight_run_id", insight_run_id), ("prospect_id", prospect_id),
            ("state", state), ("predecessor_id", predecessor_id),
            ("calibrated_from_id", calibrated_from_id),
        ], "created_at", limit)
        scenarios = []
        for row in rows:
            row.pop("forecast_label", None)
            scenarios.append(OpportunityScenario(**row))
        return scenarios

    save_opportunity = save_opportunity_scenario
    get_opportunity = get_opportunity_scenario
    list_opportunities = list_opportunity_scenarios

    def save_acquisition_calibration_record(self, record: AcquisitionCalibrationRecord) -> AcquisitionCalibrationRecord:
        self._save_immutable_payload(
            "acquisition_calibration_records", record.id, record.to_dict(),
            {"prospect_id": record.prospect_id, "vertical_id": record.vertical_id,
             "market": record.market, "version": record.version,
             "period_end": record.period_end, "created_at": record.created_at},
            AcquisitionCalibrationRecord,
        )
        self._files.save_acquisition_calibration_record(record)
        return record

    def get_acquisition_calibration_record(self, record_id: str) -> AcquisitionCalibrationRecord | None:
        row = self._get_payload("acquisition_calibration_records", record_id)
        return AcquisitionCalibrationRecord(**row) if row else None

    def list_acquisition_calibration_records(self, *, prospect_id: str | None = None,
                                              vertical_id: str | None = None, market: str | None = None,
                                              limit: int = 1000) -> list[AcquisitionCalibrationRecord]:
        rows = self._list_payload("acquisition_calibration_records", [
            ("prospect_id", prospect_id), ("vertical_id", vertical_id), ("market", market),
        ], "period_end", limit)
        return [AcquisitionCalibrationRecord(**row) for row in rows]

    save_calibration_record = save_acquisition_calibration_record
    get_calibration_record = get_acquisition_calibration_record
    list_calibration_records = list_acquisition_calibration_records
    save_acquisition_calibration = save_acquisition_calibration_record
    get_acquisition_calibration = get_acquisition_calibration_record
    list_acquisition_calibrations = list_acquisition_calibration_records

    def save_owned_measurement_snapshot(self, snapshot: OwnedMeasurementSnapshot) -> OwnedMeasurementSnapshot:
        self._save_immutable_payload(
            "owned_measurement_snapshots",
            snapshot.id,
            snapshot.to_dict(),
            {
                "prospect_id": snapshot.prospect_id,
                "vertical_id": snapshot.vertical_id,
                "source": snapshot.source,
                "period_start": snapshot.period_start,
                "period_end": snapshot.period_end,
                "predecessor_id": snapshot.predecessor_id,
                "created_at": snapshot.created_at,
            },
            OwnedMeasurementSnapshot,
        )
        self._files.save_owned_measurement_snapshot(snapshot)
        return snapshot

    def get_owned_measurement_snapshot(self, snapshot_id: str) -> OwnedMeasurementSnapshot | None:
        row = self._get_payload("owned_measurement_snapshots", snapshot_id)
        return OwnedMeasurementSnapshot(**row) if row else None

    def list_owned_measurement_snapshots(
        self,
        *,
        prospect_id: str | None = None,
        vertical_id: str | None = None,
        source: str | None = None,
        predecessor_id: str | None = None,
        limit: int = 1000,
    ) -> list[OwnedMeasurementSnapshot]:
        rows = self._list_payload(
            "owned_measurement_snapshots",
            [
                ("prospect_id", prospect_id),
                ("vertical_id", vertical_id),
                ("source", source),
                ("predecessor_id", predecessor_id),
            ],
            "period_end",
            limit,
        )
        return [OwnedMeasurementSnapshot(**row) for row in rows]

    save_owned_measurement = save_owned_measurement_snapshot
    get_owned_measurement = get_owned_measurement_snapshot
    list_owned_measurements = list_owned_measurement_snapshots

    def save_demand_trend_snapshot(
        self, snapshot: DemandTrendSnapshot
    ) -> DemandTrendSnapshot:
        self._save_immutable_payload(
            "demand_trend_snapshots",
            snapshot.id,
            snapshot.to_dict(),
            {
                "prospect_id": snapshot.prospect_id,
                "vertical_id": snapshot.vertical_id,
                "market": snapshot.market,
                "source": snapshot.source,
                "state": snapshot.state,
                "version": snapshot.version,
                "predecessor_id": snapshot.predecessor_id,
                "superseded_by_id": snapshot.superseded_by_id,
                "created_at": snapshot.created_at,
            },
            DemandTrendSnapshot,
        )
        self._files.save_demand_trend_snapshot(snapshot)
        return snapshot

    def get_demand_trend_snapshot(
        self, snapshot_id: str
    ) -> DemandTrendSnapshot | None:
        row = self._get_payload("demand_trend_snapshots", snapshot_id)
        return DemandTrendSnapshot(**row) if row else None

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
        rows = self._list_payload(
            "demand_trend_snapshots",
            [
                ("prospect_id", prospect_id),
                ("vertical_id", vertical_id),
                ("market", market),
                ("source", source),
                ("state", state),
                ("predecessor_id", predecessor_id),
            ],
            "created_at",
            limit,
        )
        return [DemandTrendSnapshot(**row) for row in rows]

    save_demand_trend = save_demand_trend_snapshot
    get_demand_trend = get_demand_trend_snapshot
    list_demand_trends = list_demand_trend_snapshots

    def save_conversion_event_map(
        self, event_map: ConversionEventMap
    ) -> ConversionEventMap:
        self._save_immutable_payload(
            "conversion_event_maps",
            event_map.id,
            event_map.to_dict(),
            {
                "prospect_id": event_map.prospect_id,
                "vertical_id": event_map.vertical_id,
                "state": event_map.state,
                "version": event_map.version,
                "predecessor_id": event_map.predecessor_id,
                "superseded_by_id": event_map.superseded_by_id,
                "created_at": event_map.created_at,
            },
            ConversionEventMap,
        )
        self._files.save_conversion_event_map(event_map)
        return event_map

    def get_conversion_event_map(
        self, event_map_id: str
    ) -> ConversionEventMap | None:
        row = self._get_payload("conversion_event_maps", event_map_id)
        return ConversionEventMap(**row) if row else None

    def list_conversion_event_maps(
        self,
        *,
        prospect_id: str | None = None,
        vertical_id: str | None = None,
        state: str | None = None,
        predecessor_id: str | None = None,
        limit: int = 1000,
    ) -> list[ConversionEventMap]:
        rows = self._list_payload(
            "conversion_event_maps",
            [
                ("prospect_id", prospect_id),
                ("vertical_id", vertical_id),
                ("state", state),
                ("predecessor_id", predecessor_id),
            ],
            "created_at",
            limit,
        )
        return [ConversionEventMap(**row) for row in rows]

    save_event_map = save_conversion_event_map
    get_event_map = get_conversion_event_map
    list_event_maps = list_conversion_event_maps

    def save_demand_conversion_evidence(
        self, evidence: DemandConversionEvidence
    ) -> DemandConversionEvidence:
        self._save_immutable_payload(
            "demand_conversion_evidence",
            evidence.id,
            evidence.to_dict(),
            {
                "insight_run_id": evidence.insight_run_id,
                "prospect_id": evidence.prospect_id,
                "vertical_id": evidence.vertical_id,
                "mode": evidence.mode,
                "market": evidence.market,
                "status": evidence.status,
                "state": evidence.state,
                "predecessor_id": evidence.predecessor_id,
                "created_at": evidence.created_at,
            },
            DemandConversionEvidence,
        )
        self._files.save_demand_conversion_evidence(evidence)
        return evidence

    def get_demand_conversion_evidence(
        self, evidence_id: str
    ) -> DemandConversionEvidence | None:
        row = self._get_payload("demand_conversion_evidence", evidence_id)
        return DemandConversionEvidence(**row) if row else None

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
        rows = self._list_payload(
            "demand_conversion_evidence",
            [
                ("insight_run_id", insight_run_id),
                ("prospect_id", prospect_id),
                ("vertical_id", vertical_id),
                ("mode", mode),
                ("state", state),
                ("predecessor_id", predecessor_id),
            ],
            "created_at",
            limit,
        )
        return [DemandConversionEvidence(**row) for row in rows]

    save_demand_conversion = save_demand_conversion_evidence
    get_demand_conversion = get_demand_conversion_evidence
    list_demand_conversions = list_demand_conversion_evidence

    def save_demand_conversion_report_snapshot(
        self, snapshot: DemandConversionReportSnapshot
    ) -> DemandConversionReportSnapshot:
        self._save_immutable_payload(
            "demand_conversion_report_snapshots",
            snapshot.id,
            snapshot.to_dict(),
            {
                "demand_conversion_evidence_id": (
                    snapshot.demand_conversion_evidence_id
                ),
                "run_id": snapshot.run_id,
                "mode": snapshot.mode,
                "status": snapshot.status,
                "created_at": snapshot.created_at,
            },
            DemandConversionReportSnapshot,
        )
        self._files.save_demand_conversion_report_snapshot(snapshot)
        return snapshot

    def get_demand_conversion_report_snapshot(
        self, snapshot_id: str
    ) -> DemandConversionReportSnapshot | None:
        row = self._get_payload(
            "demand_conversion_report_snapshots",
            snapshot_id,
        )
        return DemandConversionReportSnapshot(**row) if row else None

    def list_demand_conversion_report_snapshots(
        self,
        *,
        run_id: str | None = None,
        demand_conversion_evidence_id: str | None = None,
        mode: str | None = None,
        limit: int = 1000,
    ) -> list[DemandConversionReportSnapshot]:
        rows = self._list_payload(
            "demand_conversion_report_snapshots",
            [
                ("run_id", run_id),
                (
                    "demand_conversion_evidence_id",
                    demand_conversion_evidence_id,
                ),
                ("mode", mode),
            ],
            "created_at",
            limit,
        )
        return [DemandConversionReportSnapshot(**row) for row in rows]

    def _get_payload(self, table: str, record_id: str) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute(f"SELECT payload_json FROM {table} WHERE id = ?", (record_id,)).fetchone()
        return self._decode(row[0]) if row else None

    def _list_payload(self, table: str, filters: list[tuple[str, Any]], order_column: str, limit: int) -> list[dict[str, Any]]:
        clauses: list[str] = []
        args: list[Any] = []
        for field_name, value in filters:
            if value is not None:
                clauses.append(f"{field_name} = ?")
                args.append(value)
        args.append(max(1, min(int(limit), 10000)))
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        with self._connect() as connection:
            rows = connection.execute(
                f"SELECT payload_json FROM {table} {where} ORDER BY {order_column} DESC, id DESC LIMIT ?", args
            ).fetchall()
        return [self._decode(row[0]) for row in rows]

    def _save_immutable_payload(self, table: str, record_id: str, payload: dict[str, Any], columns: dict[str, Any], model: type[Any]) -> None:
        with self._connect() as connection:
            row = connection.execute(f"SELECT payload_json FROM {table} WHERE id = ?", (record_id,)).fetchone()
            if row is not None:
                existing_payload = self._decode(row[0])
                existing_payload.pop("forecast_label", None)
                existing = model(**existing_payload)
                if existing.to_dict() == payload:
                    return
                raise ValueError(f"{model.__name__} records are immutable")
            values = {"id": record_id, "payload_json": self._encode(payload), **columns}
            names = ", ".join(values)
            placeholders = ", ".join("?" for _ in values)
            connection.execute(
                f"INSERT INTO {table} ({names}) VALUES ({placeholders})",
                tuple(values.values()),
            )

    def health(self) -> dict[str, Any]:
        with self._connect() as connection:
            connection.execute("SELECT 1").fetchone()
            journal_mode = str(connection.execute("PRAGMA journal_mode").fetchone()[0]).lower()
            foreign_keys = bool(connection.execute("PRAGMA foreign_keys").fetchone()[0])
            migration_count = int(connection.execute("SELECT COUNT(*) FROM schema_migrations").fetchone()[0])
        return {
            "status": "ok",
            "backend": "sqlite",
            "database_path": str(self.database_path),
            "journal_mode": journal_mode,
            "foreign_keys": foreign_keys,
            "migration_count": migration_count,
        }

    def close(self) -> None:
        """Connections are short-lived per operation; retained for repository parity."""

    def _migrate(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version TEXT PRIMARY KEY,
                    applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            applied = {
                row[0]
                for row in connection.execute("SELECT version FROM schema_migrations").fetchall()
            }
            for migration_path in sorted(self.MIGRATIONS_DIR.glob("*.sql")):
                version = migration_path.stem
                if version in applied:
                    continue
                connection.executescript(migration_path.read_text(encoding="utf-8"))
                connection.execute(
                    "INSERT INTO schema_migrations (version) VALUES (?)", (version,)
                )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path, timeout=30.0)
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA journal_mode = WAL")
        connection.execute("PRAGMA busy_timeout = 30000")
        return connection

    @staticmethod
    def _encode(payload: dict[str, Any]) -> str:
        return json.dumps(payload, separators=(",", ":"), ensure_ascii=False)

    @staticmethod
    def _decode(payload: str) -> dict[str, Any]:
        return json.loads(payload)
