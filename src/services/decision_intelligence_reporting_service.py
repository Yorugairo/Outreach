"""Immutable, mode-safe P12 decision-intelligence and combined v6 reports."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from src.models import (
    COMBINED_REPORT_V6_VERSION,
    DECISION_INTELLIGENCE_REPORT_VERSION,
    InsightReport,
    ReportAlias,
    ReportSnapshot,
    canonical_sha256,
)
from src.repositories.base import InsightRepository


class DecisionIntelligenceReportingService:
    REPORT_VERSION = DECISION_INTELLIGENCE_REPORT_VERSION
    COMBINED_VERSION = COMBINED_REPORT_V6_VERSION
    RENDERER_VERSION = "decision-intelligence-renderer.v1"

    def __init__(self, repository: InsightRepository) -> None:
        self.repository = repository

    def assemble(
        self,
        run_id: str,
        *,
        mode: str = "prospect",
        for_export: bool = False,
        include_combined: bool = True,
    ) -> dict[str, InsightReport]:
        if mode not in {"prospect", "owner_verified"}:
            raise ValueError("decision-intelligence mode must be prospect or owner_verified")
        run = self.repository.get_run(run_id)
        if run is None:
            raise ValueError(f"run {run_id} not found")
        if run.status != "completed":
            raise ValueError("decision-intelligence reports require a completed insight run")
        prospect = self._qualified_prospect(run.requested_domain)
        selected = self._select_snapshots(run_id, mode=mode, for_export=for_export)
        payload = self._payload(
            run=run,
            prospect=prospect,
            selected=selected,
            mode=mode,
            for_export=for_export,
        )
        report = self._persist_report(
            run=run,
            version=self.REPORT_VERSION,
            payload=payload,
            headline=f"Decision intelligence — {run.requested_domain}",
            markdown=self._markdown(payload),
        )
        reports = {self.REPORT_VERSION: report}
        if include_combined:
            combined_payload = self._combined_payload(run_id, payload, mode=mode)
            combined = self._persist_report(
                run=run,
                version=self.COMBINED_VERSION,
                payload=combined_payload,
                headline=f"Website opportunity report — {run.requested_domain}",
                markdown=self._combined_markdown(combined_payload),
            )
            reports[self.COMBINED_VERSION] = combined
        self._save_snapshot(run, payload, selected)
        return reports

    def _qualified_prospect(self, domain: str) -> Any:
        normalized = domain.casefold().removeprefix("www.")
        prospects = [
            item
            for item in self.repository.list_prospects(
                qualification_status="qualified",
                limit=10_000,
            )
            if item.normalized_domain.casefold().removeprefix("www.") == normalized
        ]
        if not prospects:
            raise ValueError("decision intelligence requires a qualified prospect")
        prospects.sort(key=lambda item: (item.updated_at, item.id), reverse=True)
        return prospects[0]

    def _select_snapshots(
        self,
        run_id: str,
        *,
        mode: str,
        for_export: bool,
    ) -> dict[str, Any]:
        # The public target evidence is shared by both views. Owner mode adds a
        # private diagnostic; prospect mode never queries it.
        shared_mode = "prospect"
        ledgers = self.repository.list_business_fact_ledger_snapshots(
            run_id=run_id,
            mode=shared_mode,
            limit=100,
        )
        decisions = self.repository.list_decision_coverage_snapshots(
            run_id=run_id,
            mode=shared_mode,
            limit=100,
        )
        journeys = self.repository.list_journey_evidence_runs(
            run_id=run_id,
            mode=shared_mode,
            limit=1000,
        )
        representations = self.repository.list_ai_representation_accuracy_snapshots(
            run_id=run_id,
            mode=shared_mode,
            limit=100,
        )
        blueprints = self.repository.list_remediation_blueprint_snapshots(
            run_id=run_id,
            mode=mode,
            limit=100,
        )
        if mode == "owner_verified" and not blueprints:
            blueprints = self.repository.list_remediation_blueprint_snapshots(
                run_id=run_id,
                mode="prospect",
                limit=100,
            )
        owner = (
            self.repository.list_owner_diagnostic_snapshots(run_id=run_id, limit=100)
            if mode == "owner_verified"
            else []
        )
        selected = {
            "fact_ledger": ledgers[0] if ledgers else None,
            "decision_coverage": decisions[0] if decisions else None,
            "journeys": self._latest_by(journeys, "task_id"),
            "representation_accuracy": representations[0] if representations else None,
            "owner_diagnostic": owner[0] if owner else None,
            "remediation_blueprint": blueprints[0] if blueprints else None,
        }
        if mode == "prospect" and selected["owner_diagnostic"] is not None:
            raise ValueError("prospect decision intelligence cannot consume owner evidence")
        if for_export:
            required = ("fact_ledger", "decision_coverage")
            missing = [key for key in required if selected[key] is None]
            if missing:
                raise ValueError(
                    f"decision-intelligence export lacks required snapshots: {sorted(missing)}"
                )
            unapproved = [
                self._snapshot_key(kind, snapshot)
                for kind, value in selected.items()
                for snapshot in (value.values() if isinstance(value, dict) else [value])
                if snapshot is not None and not self._approved(kind, snapshot)
            ]
            if unapproved:
                raise ValueError(
                    "decision-intelligence export requires review approval: "
                    + ", ".join(sorted(unapproved))
                )
        return selected

    @staticmethod
    def _latest_by(records: list[Any], field: str) -> dict[str, Any]:
        selected: dict[str, Any] = {}
        for record in records:
            key = str(getattr(record, field, "") or "")
            if key and key not in selected:
                selected[key] = record
        return selected

    def _approved(self, kind: str, snapshot: Any) -> bool:
        work_item = self.repository.get_agentic_work_item(snapshot.work_item_id)
        if work_item is None or work_item.execution_mode in {"shadow", "review"}:
            return False
        if getattr(snapshot, "review_state", None) == "approved":
            return True
        return self.repository.get_agentic_evidence_review_state(snapshot.id) == "approved"

    def _payload(
        self,
        *,
        run: Any,
        prospect: Any,
        selected: dict[str, Any],
        mode: str,
        for_export: bool,
    ) -> dict[str, Any]:
        ledger = selected["fact_ledger"]
        decision = selected["decision_coverage"]
        journeys = list(selected["journeys"].values())
        representation = selected["representation_accuracy"]
        owner = selected["owner_diagnostic"]
        blueprint = selected["remediation_blueprint"]
        required_journey_kinds = {
            "offer_discovery",
            "decision_resolution",
            "ready_to_convert_cta",
        }
        observed_journey_kinds = {
            self._journey_kind(item.task_id) for item in journeys
        }
        required = {
            "business_truth": ledger is not None,
            "decision_coverage": decision is not None,
            "three_target_journeys": required_journey_kinds.issubset(
                observed_journey_kinds
            ),
        }
        completeness = round(sum(required.values()) / len(required) * 100, 2)
        status = "complete" if completeness == 100 else ("partial" if completeness else "limited")
        limitations: list[str] = []
        if not required["business_truth"]:
            limitations.append("Business fact extraction is not yet available.")
        if not required["decision_coverage"]:
            limitations.append("Buyer decision coverage is not yet available.")
        if not required["three_target_journeys"]:
            missing = required_journey_kinds - observed_journey_kinds
            limitations.append(
                "Target journey evidence is incomplete: " + ", ".join(sorted(missing))
            )
        for snapshot in [ledger, decision, representation, owner, blueprint, *journeys]:
            if snapshot is not None:
                limitations.extend(getattr(snapshot, "limitations", []) or [])

        snapshot_ids, snapshot_hashes = self._snapshot_identity(selected)
        decision_rows = deepcopy(decision.coverage) if decision is not None else []
        facts = [
            deepcopy(item)
            for item in (ledger.facts if ledger is not None else [])
            if item.get("sensitivity_class") == "public"
        ]
        teaser = self._verified_teaser(decision_rows, journeys)
        recommendations = self._recommendations(blueprint, decision)
        payload: dict[str, Any] = {
            "report_contract": self.REPORT_VERSION,
            "schema_version": 1,
            "run_id": run.id,
            "attempt_id": run.attempt_id,
            "prospect_id": prospect.id,
            "vertical_id": prospect.vertical_id,
            "mode": mode,
            "status": status,
            "completeness_percent": completeness,
            "executive_summary": (
                "This report tests whether a prospective customer can understand the offer, "
                "resolve key decisions, and reach a clear next step. It is evidence and "
                "labeled inference—not a ranking, traffic, conversion, or revenue score."
            ),
            "outreach_teaser": teaser,
            "business_truth": {
                "snapshot_id": ledger.id if ledger else None,
                "review_state": self._review_state("fact_ledger", ledger),
                "facts": facts,
                "conflicts": deepcopy(ledger.conflicts) if ledger else [],
            },
            "decision_coverage": {
                "snapshot_id": decision.id if decision else None,
                "review_state": self._review_state("decision_coverage", decision),
                "completeness_percent": (
                    decision.completeness_percent if decision else 0.0
                ),
                "questions": decision_rows,
            },
            "journeys": [
                {
                    "snapshot_id": item.id,
                    "task_id": item.task_id,
                    "task_kind": self._journey_kind(item.task_id),
                    "viewport": item.viewport,
                    "result_status": item.result_status,
                    "oracle_results": deepcopy(item.oracle_results),
                    "blockers": deepcopy(item.blockers),
                    "screenshot_refs": list(item.screenshot_refs),
                    "review_state": self._review_state("journey", item),
                }
                for item in journeys
            ],
            "representation_accuracy": (
                {
                    "snapshot_id": representation.id,
                    "review_state": self._review_state(
                        "representation_accuracy", representation
                    ),
                    "completeness_percent": representation.completeness_percent,
                    "claims": deepcopy(representation.claims),
                }
                if representation
                else {
                    "snapshot_id": None,
                    "status": "unknown",
                    "limitation": "No approved AI-response sample was supplied.",
                }
            ),
            "recommendations": recommendations,
            "limitations": list(dict.fromkeys(limitations)),
            "source_snapshot_ids": snapshot_ids,
            "source_hashes": snapshot_hashes,
            "customer_export": for_export,
            "disclaimer": (
                "Agentic evidence does not change deterministic SEO, AI Readiness, "
                "visibility, demand, conversion, or revenue calculations."
            ),
        }
        if mode == "owner_verified":
            payload["owner_diagnostic"] = (
                {
                    "snapshot_id": owner.id,
                    "privacy_scope": owner.privacy_scope,
                    "observations": deepcopy(owner.observations),
                    "hypotheses": deepcopy(owner.hypotheses),
                    "review_state": self._review_state("owner_diagnostic", owner),
                }
                if owner
                else {
                    "snapshot_id": None,
                    "status": "unknown",
                    "limitation": "No consented owner diagnostic is available.",
                }
            )
        return payload

    def _combined_payload(
        self,
        run_id: str,
        decision_payload: dict[str, Any],
        *,
        mode: str,
    ) -> dict[str, Any]:
        foundation = None
        for version in ("v5", "v4", "v3", "v2"):
            report = self.repository.get_report(run_id, version)
            if report is None:
                continue
            candidate_mode = report.report_payload.get("mode")
            if version == "v5" and candidate_mode not in {None, mode}:
                continue
            foundation = {
                "report_version": version,
                "payload": deepcopy(report.report_payload),
            }
            break
        return {
            "report_contract": self.COMBINED_VERSION,
            "schema_version": 1,
            "run_id": run_id,
            "mode": mode,
            "executive_summary": decision_payload["executive_summary"],
            "foundation": foundation
            or {
                "report_version": None,
                "status": "unknown",
                "limitation": "No compatible deterministic combined report is available.",
            },
            "decision_intelligence": deepcopy(decision_payload),
            "source_versions": {
                "decision_intelligence": self.REPORT_VERSION,
                "foundation": foundation["report_version"] if foundation else "unavailable",
            },
            "limitations": deepcopy(decision_payload["limitations"]),
        }

    def _persist_report(
        self,
        *,
        run: Any,
        version: str,
        payload: dict[str, Any],
        headline: str,
        markdown: str,
    ) -> InsightReport:
        digest = canonical_sha256(payload)
        report = InsightReport(
            id=f"{run.id}-{version}-{digest[:16]}",
            insight_run_id=run.id,
            seo_target_id=str(run.seo_target_id or run.id),
            report_version=version,
            attempt_id=run.attempt_id,
            report_status=str(payload.get("status") or "complete"),
            headline=headline,
            executive_summary=str(payload.get("executive_summary") or ""),
            key_actions=deepcopy(payload.get("recommendations", []))[:3],
            report_payload=payload,
            export_json=payload,
            export_markdown=markdown,
            created_at=run.updated_at,
            updated_at=run.updated_at,
        )
        existing = self.repository.get_report(run.id, version)
        if existing is None:
            return self.repository.save_report(report)
        if canonical_sha256(existing.report_payload) == digest:
            return existing
        return report

    def _save_snapshot(
        self,
        run: Any,
        payload: dict[str, Any],
        selected: dict[str, Any],
    ) -> ReportSnapshot:
        digest = canonical_sha256(payload)
        artifact_ref = self.repository.save_report_snapshot_payload(run.id, digest, payload)
        snapshot_ids, snapshot_hashes = self._snapshot_identity(selected)
        snapshot = ReportSnapshot(
            id=f"{run.id}-{self.REPORT_VERSION}-{digest[:16]}",
            run_id=run.id,
            attempt_id=run.attempt_id,
            report_contract=self.REPORT_VERSION,
            schema_version=1,
            source_snapshot_ids=snapshot_ids,
            source_hashes=snapshot_hashes,
            renderer_version=self.RENDERER_VERSION,
            payload_sha256=digest,
            payload_artifact_ref=artifact_ref,
            completeness_percent=float(payload["completeness_percent"]),
            status=str(payload["status"]),
            created_at=run.updated_at,
        )
        stored = self.repository.save_report_snapshot(snapshot)
        self.repository.save_report_alias(
            ReportAlias(
                id=f"{run.id}-{self.REPORT_VERSION}-latest",
                run_id=run.id,
                report_contract=self.REPORT_VERSION,
                alias="latest",
                snapshot_id=stored.id,
            )
        )
        return stored

    @staticmethod
    def _snapshot_identity(selected: dict[str, Any]) -> tuple[dict[str, str], dict[str, str]]:
        ids: dict[str, str] = {}
        hashes: dict[str, str] = {}
        for kind, value in selected.items():
            values = value.items() if isinstance(value, dict) else [(kind, value)]
            for suffix, snapshot in values:
                if snapshot is None:
                    continue
                key = f"{kind}:{suffix}" if isinstance(value, dict) else kind
                digest = getattr(snapshot, "content_sha256", None) or canonical_sha256(
                    snapshot.to_dict()
                )
                ids[key] = snapshot.id
                hashes[key] = digest
        return ids, hashes

    def _review_state(self, kind: str, snapshot: Any | None) -> str:
        if snapshot is None:
            return "unavailable"
        model_state = getattr(snapshot, "review_state", None)
        if model_state == "approved":
            return "approved"
        return self.repository.get_agentic_evidence_review_state(snapshot.id)

    @staticmethod
    def _journey_kind(task_id: str) -> str:
        normalized = task_id.casefold().replace("_", "-")
        if "offer-discovery" in normalized or normalized.endswith("offer"):
            return "offer_discovery"
        if "decision-resolution" in normalized or normalized.endswith("decision"):
            return "decision_resolution"
        if "ready-to-convert" in normalized or "cta" in normalized:
            return "ready_to_convert_cta"
        return "other"

    @staticmethod
    def _verified_teaser(
        coverage: list[dict[str, Any]],
        journeys: list[Any],
    ) -> dict[str, Any] | None:
        for result in coverage:
            if result.get("status") in {"answered", "partial", "ambiguous", "contradicted"}:
                refs = result.get("evidence_refs") or []
                if refs:
                    return {
                        "kind": "decision_evidence",
                        "text": (
                            f"We reviewed how the site answers “{result.get('question_id')}” "
                            f"and found the current evidence is {result.get('status')}."
                        ),
                        "evidence_refs": deepcopy(refs),
                    }
        for journey in journeys:
            if journey.blockers:
                return {
                    "kind": "journey_blocker",
                    "text": "A ready-to-act visitor encounters a verified path blocker.",
                    "evidence_refs": [
                        {
                            "artifact_ref": f"journey_evidence_runs/{journey.id}.json",
                            "reference_kind": "persisted_field",
                            "field_path": "blockers",
                            "snapshot_id": journey.id,
                        }
                    ],
                }
        return None

    @staticmethod
    def _recommendations(blueprint: Any | None, decision: Any | None) -> list[dict[str, Any]]:
        if blueprint is not None:
            raw = blueprint.blueprint.get("recommendations", [])
            if isinstance(raw, list):
                grounded = [
                    deepcopy(item)
                    for item in raw
                    if isinstance(item, dict) and item.get("evidence_refs")
                ]
                if grounded:
                    return grounded[:3]
        if decision is None:
            return []
        recommendations: list[dict[str, Any]] = []
        for index, result in enumerate(decision.coverage):
            if result.get("status") not in {"missing", "partial", "ambiguous", "contradicted"}:
                continue
            recommendations.append(
                {
                    "recommendation_id": f"decision-{result.get('question_id')}",
                    "title": f"Clarify {str(result.get('question_id')).replace('_', ' ')}",
                    "action": "Add a concise, visible answer and a direct next step.",
                    "service_fit": ["website_seo_vertical_visibility"],
                    "evidence_refs": [
                        {
                            "artifact_ref": f"decision_coverage/{decision.id}.json",
                            "reference_kind": "persisted_field",
                            "field_path": f"coverage.{index}.status",
                            "snapshot_id": decision.id,
                        }
                    ],
                }
            )
            if len(recommendations) == 3:
                break
        return recommendations

    @staticmethod
    def _snapshot_key(kind: str, snapshot: Any) -> str:
        return f"{kind}:{snapshot.id}"

    @staticmethod
    def _markdown(payload: dict[str, Any]) -> str:
        lines = [
            "# Decision intelligence",
            "",
            payload["executive_summary"],
            "",
            f"- Evidence completeness: {payload['completeness_percent']}% ({payload['status']})",
            f"- Mode: {payload['mode']}",
            "",
            "## Buyer questions",
        ]
        for item in payload["decision_coverage"]["questions"]:
            lines.append(
                f"- {str(item.get('question_id')).replace('_', ' ').title()}: "
                f"{item.get('status')}"
            )
        lines.extend(["", "## Customer journeys"])
        for item in payload["journeys"]:
            lines.append(
                f"- {item['task_kind'].replace('_', ' ').title()} "
                f"({item['viewport']}): {item['result_status']}"
            )
        if payload["recommendations"]:
            lines.extend(["", "## Recommended next steps"])
            lines.extend(
                f"- **{item.get('title')}** — {item.get('action')}"
                for item in payload["recommendations"]
            )
        if payload["limitations"]:
            lines.extend(["", "## Evidence limits"])
            lines.extend(f"- {item}" for item in payload["limitations"])
        lines.extend(["", payload["disclaimer"]])
        return "\n".join(lines) + "\n"

    @classmethod
    def _combined_markdown(cls, payload: dict[str, Any]) -> str:
        foundation = payload["foundation"]
        lines = [
            "# Website opportunity report",
            "",
            payload["executive_summary"],
            "",
            f"- Deterministic foundation: {foundation.get('report_version') or 'unavailable'}",
            f"- Decision layer: {cls.REPORT_VERSION}",
            "",
            cls._markdown(payload["decision_intelligence"]),
        ]
        return "\n".join(lines)
