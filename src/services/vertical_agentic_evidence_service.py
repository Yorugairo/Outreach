"""P12 preflight, idempotent work creation, retry, and evidence aggregation."""

from __future__ import annotations

from dataclasses import replace
from typing import Any

from src.config import AgenticAnalysisSettings
from src.models import AgenticWorkItem, SiteEvidencePack, canonical_sha256, utc_now_iso
from src.repositories.base import InsightRepository
from src.services.vertical_agentic_reconciliation_service import (
    VerticalAgenticReconciliationService,
)


class VerticalAgenticEvidenceService:
    AUTOMATIC_WORK_BUDGETS = {
        "business_fact_ledger": 0.05,
        "decision_coverage": 0.05,
        "target_journey": 0.05,
    }
    AUTOMATIC_TOTAL_COST_USD = 0.25
    PREMIUM_TOTAL_COST_USD = 0.75

    def __init__(
        self,
        repository: InsightRepository,
        *,
        settings: AgenticAnalysisSettings,
    ) -> None:
        self.repository = repository
        self.settings = settings
        self.reconciliation = VerticalAgenticReconciliationService()

    def preflight(
        self,
        run_id: str,
        *,
        evidence_pack: SiteEvidencePack | None = None,
        execution_mode: str = "automatic",
    ) -> dict[str, Any]:
        if execution_mode not in {"automatic", "shadow", "review", "premium"}:
            raise ValueError("unsupported P12 execution mode")
        run = self.repository.get_run(run_id)
        if run is None:
            raise ValueError(f"run {run_id} not found")
        prospect = self._prospect_for_domain(run.requested_domain)
        if prospect is None:
            return self._unavailable(
                run_id,
                execution_mode,
                "No qualified prospect matches the run domain.",
            )
        resolution = self.reconciliation.resolve(
            prospect,
            operator_enabled=self.settings.operator_approved,
        )
        if not resolution.eligible or resolution.pack is None:
            return self._unavailable(
                run_id,
                execution_mode,
                resolution.reason or "No approved vertical agentic pack is available.",
            )
        if run.status != "completed":
            return self._unavailable(
                run_id,
                execution_mode,
                "The deterministic InsightRun is not complete.",
            )
        if execution_mode == "automatic" and not self.settings.available:
            return self._unavailable(
                run_id,
                execution_mode,
                "Automatic work requires enabled runtime, operator approval, and P10 promotion.",
            )
        if execution_mode in {"shadow", "review", "premium"} and not (
            self.settings.enabled and self.settings.operator_approved
        ):
            return self._unavailable(
                run_id,
                execution_mode,
                "Explicit agentic work requires an enabled, operator-approved runtime.",
            )
        if evidence_pack is None:
            return self._unavailable(
                run_id,
                execution_mode,
                "A persisted scoped SiteEvidencePack is required.",
            )
        if evidence_pack.run_id != run_id:
            raise ValueError("agentic evidence pack does not belong to the run")
        existing = self.repository.list_agentic_work_items(run_id=run_id, limit=10_000)
        return {
            "available": True,
            "run_id": run_id,
            "prospect_id": prospect.id,
            "vertical_id": prospect.vertical_id,
            "vertical_agentic_pack_version": resolution.pack.version,
            "execution_mode": execution_mode,
            "customer_export_eligible": execution_mode in {"automatic", "premium"},
            "automatic_work": [
                "business_fact_ledger",
                "decision_coverage",
                "offer_discovery",
                "decision_resolution",
                "ready_to_convert_cta",
            ],
            "planned_work_items": 5,
            "max_inference_cost_usd": self.AUTOMATIC_TOTAL_COST_USD,
            "premium_aggregate_ceiling_usd": self.PREMIUM_TOTAL_COST_USD,
            "provider_calls": 0,
            "provider_cost_usd": 0.0,
            "existing_work_item_ids": [item.id for item in existing],
            "runtime": {
                "runtime": self.settings.runtime,
                "provider": self.settings.provider,
                "model": self.settings.model,
                "promotion_approved": self.settings.promotion_approved,
            },
        }

    def enqueue_defaults(
        self,
        evidence_pack: SiteEvidencePack,
        *,
        execution_mode: str = "automatic",
    ) -> list[AgenticWorkItem]:
        preflight = self.preflight(
            evidence_pack.run_id,
            evidence_pack=evidence_pack,
            execution_mode=execution_mode,
        )
        if not preflight["available"]:
            raise ValueError(str(preflight["unavailable_reason"]))
        pack = self.repository.get_vertical_agentic_pack(
            str(preflight["vertical_agentic_pack_version"])
        )
        if pack is None:
            raise ValueError("resolved vertical agentic pack is not persisted")
        definitions = [
            ("business_fact_ledger", None, 0),
            ("decision_coverage", None, 0),
            *[
                ("target_journey", str(task["task_id"]), 30)
                for task in pack.journey_tasks
            ],
        ]
        items = [
            self._enqueue(
                evidence_pack=evidence_pack,
                work_kind=kind,
                execution_mode=execution_mode,
                budget_class="automatic",
                max_cost_usd=0.05,
                task_id=task_id,
                max_browser_actions=max_browser_actions,
                host_policy_version=(
                    pack.action_host_policy_version if kind == "target_journey" else None
                ),
                source_snapshot_ids=[],
                consent_id=None,
            )
            for kind, task_id, max_browser_actions in definitions
        ]
        if sum(item.max_cost_usd for item in items) > self.AUTOMATIC_TOTAL_COST_USD + 0.000001:
            raise ValueError("automatic work exceeds the aggregate inference ceiling")
        return items

    def enqueue_optional(
        self,
        evidence_pack: SiteEvidencePack,
        *,
        work_kind: str,
        source_snapshot_ids: list[str],
        execution_mode: str = "premium",
        consent_id: str | None = None,
        task_id: str | None = None,
        host_policy_version: str | None = None,
        max_cost_usd: float = 0.25,
    ) -> AgenticWorkItem:
        if work_kind not in {
            "competitor_journey",
            "ai_representation_accuracy",
            "owner_diagnostic",
            "remediation_blueprint",
        }:
            raise ValueError("unsupported optional agentic work kind")
        preflight = self.preflight(
            evidence_pack.run_id,
            evidence_pack=evidence_pack,
            execution_mode=execution_mode,
        )
        if not preflight["available"]:
            raise ValueError(str(preflight["unavailable_reason"]))
        existing = self.repository.list_agentic_work_items(
            run_id=evidence_pack.run_id,
            limit=10_000,
        )
        committed = sum(
            item.max_cost_usd
            for item in existing
            if item.budget_class == "premium"
            and item.state not in {"failed", "superseded"}
        )
        if committed + max_cost_usd > self.PREMIUM_TOTAL_COST_USD + 0.000001:
            raise ValueError("premium work would exceed the $0.75 aggregate inference ceiling")
        return self._enqueue(
            evidence_pack=evidence_pack,
            work_kind=work_kind,
            execution_mode=execution_mode,
            budget_class="premium",
            max_cost_usd=max_cost_usd,
            task_id=task_id,
            max_browser_actions=30 if "journey" in work_kind else 0,
            host_policy_version=host_policy_version,
            source_snapshot_ids=source_snapshot_ids,
            consent_id=consent_id,
        )

    def retry(self, work_item_id: str) -> AgenticWorkItem:
        item = self.repository.get_agentic_work_item(work_item_id)
        if item is None:
            raise ValueError(f"agentic work item {work_item_id} not found")
        if item.state != "failed" or item.error_class != "transient":
            raise ValueError("only transient failed agentic work may be retried")
        if item.attempt_count > item.retry_limit:
            raise ValueError("agentic work retry limit is exhausted")
        return self.repository.update_agentic_work_item(
            replace(
                item,
                state="queued",
                error_class=None,
                error_text=None,
                lease_owner=None,
                lease_expires_at=None,
                completed_at=None,
                updated_at=utc_now_iso(),
            )
        )

    def evidence(self, run_id: str, *, mode: str = "prospect") -> dict[str, Any]:
        if mode not in {"prospect", "owner_verified"}:
            raise ValueError("unsupported agentic evidence mode")
        return {
            "run_id": run_id,
            "mode": mode,
            "work_items": [
                item.to_dict()
                for item in self.repository.list_agentic_work_items(
                    run_id=run_id,
                    mode=mode,
                    limit=10_000,
                )
            ],
            "business_fact_ledgers": [
                item.to_dict()
                for item in self.repository.list_business_fact_ledger_snapshots(
                    run_id=run_id,
                    mode=mode,
                    limit=1000,
                )
            ],
            "decision_coverage": [
                item.to_dict()
                for item in self.repository.list_decision_coverage_snapshots(
                    run_id=run_id,
                    mode=mode,
                    limit=1000,
                )
            ],
            "journeys": [
                item.to_dict()
                for item in self.repository.list_journey_evidence_runs(
                    run_id=run_id,
                    mode=mode,
                    limit=1000,
                )
            ],
            "representation_accuracy": [
                item.to_dict()
                for item in self.repository.list_ai_representation_accuracy_snapshots(
                    run_id=run_id,
                    mode=mode,
                    limit=1000,
                )
            ],
            "owner_diagnostics": (
                [
                    item.to_dict()
                    for item in self.repository.list_owner_diagnostic_snapshots(
                        run_id=run_id,
                        limit=1000,
                    )
                ]
                if mode == "owner_verified"
                else []
            ),
            "remediation_blueprints": [
                item.to_dict()
                for item in self.repository.list_remediation_blueprint_snapshots(
                    run_id=run_id,
                    mode=mode,
                    limit=1000,
                )
            ],
        }

    def _enqueue(
        self,
        *,
        evidence_pack: SiteEvidencePack,
        work_kind: str,
        execution_mode: str,
        budget_class: str,
        max_cost_usd: float,
        task_id: str | None,
        max_browser_actions: int,
        host_policy_version: str | None,
        source_snapshot_ids: list[str],
        consent_id: str | None,
    ) -> AgenticWorkItem:
        pack_resolution = self.reconciliation.resolve(
            vertical_pack_version=evidence_pack.vertical_pack_version,
            qualified=True,
            operator_enabled=True,
        )
        if not pack_resolution.eligible or pack_resolution.pack is None:
            raise ValueError(pack_resolution.reason)
        agentic_pack_version = pack_resolution.pack.version
        identity = canonical_sha256(
            {
                "evidence_pack_sha256": evidence_pack.content_sha256,
                "vertical_pack_version": agentic_pack_version,
                "work_kind": work_kind,
                "task_id": task_id,
                "source_snapshot_ids": source_snapshot_ids,
                "execution_mode": execution_mode,
                "prompt_version": "vertical-agentic.prompt.v1",
                "rubric_version": "vertical-agentic.rubric.v1",
                "schema_version": "vertical-agentic-evidence.v1",
                "requested_runtime": self.settings.runtime,
                "requested_provider": self.settings.provider,
                "requested_model": self.settings.model,
            }
        )
        existing = self.repository.get_agentic_work_item_by_idempotency_key(identity)
        if existing is not None:
            return existing
        item = AgenticWorkItem(
            run_id=evidence_pack.run_id,
            attempt_id=evidence_pack.attempt_id,
            evidence_pack_id=evidence_pack.id,
            vertical_pack_version=agentic_pack_version,
            work_kind=work_kind,
            mode="owner_verified" if work_kind == "owner_diagnostic" else "prospect",
            consent_id=consent_id,
            source_sha256=evidence_pack.content_sha256 or evidence_pack.compute_hash(),
            idempotency_key=identity,
            requested_runtime=self.settings.runtime,
            requested_provider=self.settings.provider,
            requested_model=self.settings.model,
            prompt_version="vertical-agentic.prompt.v1",
            rubric_version="vertical-agentic.rubric.v1",
            schema_version="vertical-agentic-evidence.v1",
            budget_class=budget_class,
            execution_mode=execution_mode,
            task_id=task_id,
            source_snapshot_ids=list(source_snapshot_ids),
            host_policy_version=host_policy_version,
            max_model_decisions=12,
            max_browser_actions=max_browser_actions,
            max_cost_usd=max_cost_usd,
            max_output_tokens=2_000,
            timeout_seconds=90,
            retry_limit=2,
        )
        return self.repository.save_agentic_work_item(item)

    def _prospect_for_domain(self, domain: str) -> Any | None:
        normalized = domain.casefold().removeprefix("www.")
        matches = [
            item
            for item in self.repository.list_prospects(
                qualification_status="qualified",
                limit=10_000,
            )
            if item.normalized_domain.casefold().removeprefix("www.") == normalized
        ]
        matches.sort(key=lambda item: (item.updated_at, item.id), reverse=True)
        return matches[0] if matches else None

    @classmethod
    def _unavailable(
        cls,
        run_id: str,
        execution_mode: str,
        reason: str,
    ) -> dict[str, Any]:
        return {
            "available": False,
            "run_id": run_id,
            "execution_mode": execution_mode,
            "unavailable_reason": reason,
            "planned_work_items": 0,
            "max_inference_cost_usd": cls.AUTOMATIC_TOTAL_COST_USD,
            "premium_aggregate_ceiling_usd": cls.PREMIUM_TOTAL_COST_USD,
            "provider_calls": 0,
            "provider_cost_usd": 0.0,
        }
