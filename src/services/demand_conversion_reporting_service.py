"""Immutable demand-to-conversion report assembly.

The demand-conversion evidence record is intentionally rendered by a small
dedicated service instead of being folded into the existing SEO or opportunity
reporters.  That keeps the commercial evidence contract additive: a demand
report can be rendered for a run without rewriting any of the v1/v2/v3/v4
artifacts already attached to that run.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import date
import json
from pathlib import Path
from typing import Any, Mapping

from src.models import (
    DEMAND_CONVERSION_FORMULA_VERSION,
    DEMAND_CONVERSION_REPORT_VERSION,
    DemandConversionEvidence,
    DemandConversionReportSnapshot,
    InsightReport,
    canonical_sha256,
)
from src.repositories.base import InsightRepository
from src.services.report_validation_service import (
    DemandConversionReportValidationService,
)


class DemandConversionReportingService:
    """Render and persist mode-safe demand-conversion reports.

    ``assemble`` accepts either a persisted evidence object or its exact ID.
    The default is an internal evidence report (draft evidence is useful to an
    operator while it is being reviewed).  ``for_export=True`` routes through
    the validation service's client payload gate, which requires approved
    evidence and applies the prospect privacy filter.
    """

    REPORT_VERSION = DEMAND_CONVERSION_REPORT_VERSION
    COMBINED_VERSION = "v5"
    SCHEMA_VERSION = 1
    RENDERER_VERSION = "demand-conversion-renderer.v1"
    FORECAST_LABEL = "Forecast, not guarantee"
    FORMULA_TEXT = (
        "incremental_members = min(incremental_qualified_visits * lead_rate * "
        "booking_rate * close_rate, available_capacity); "
        "incremental_recurring_revenue = incremental_members * monthly_price"
    )

    def __init__(
        self,
        repository: InsightRepository,
        validation_service: DemandConversionReportValidationService | None = None,
    ) -> None:
        self.repository = repository
        self.validation = validation_service or DemandConversionReportValidationService(
            repository
        )

    def assemble(
        self,
        evidence: DemandConversionEvidence | str,
        *,
        mode: str | None = None,
        requested_mode: str | None = None,
        for_export: bool = False,
        include_combined: bool = True,
    ) -> dict[str, InsightReport]:
        """Assemble the demand report and, by default, the additive v5 report.

        ``mode`` is a convenience alias for ``requested_mode``.  Supplying both
        with different values is rejected rather than silently upgrading a
        prospect report into owner-verified mode.
        """

        if mode is not None and requested_mode is not None and mode != requested_mode:
            raise ValueError("mode and requested_mode must agree")
        requested = requested_mode or mode
        record = self._resolve_evidence(evidence)
        if requested is not None and requested != record.mode:
            # Keep this check local as well as in the validation service so a
            # custom validator cannot accidentally turn a prospect request into
            # an owner-verified export.
            raise ValueError("demand conversion mode cannot be changed during report/export")

        run = self._completed_run(record)
        validation_result = self.validation.validate(
            record,
            requested_mode=requested or record.mode,
            for_export=for_export,
        )
        evidence_payload = self._evidence_payload_for_report(
            record,
            requested_mode=requested or record.mode,
            for_export=for_export,
        )
        payload = self._payload(record, evidence_payload, validation_result)
        report = self._report(
            run,
            record,
            self.REPORT_VERSION,
            payload,
            self._markdown(payload),
        )
        report = self._save_report_immutably(report)
        scoped_artifacts = self._save_scoped_artifacts(run.id, record.id, report)

        # The custom snapshot is the immutable identity used by future client
        # exports.  It is persisted after the report artifact exists so the
        # referenced path is always meaningful.
        self._save_snapshot(record, report, run.id, scoped_artifacts=scoped_artifacts)

        reports: dict[str, InsightReport] = {self.REPORT_VERSION: report}
        if include_combined:
            combined_payload = self._combined_payload(run.id, record, payload)
            combined = self._report(
                run,
                record,
                self.COMBINED_VERSION,
                combined_payload,
                self._combined_markdown(combined_payload),
            )
            combined = self._save_report_immutably(combined)
            self._save_scoped_artifacts(run.id, record.id, combined)
            reports[self.COMBINED_VERSION] = combined
        return reports

    # Common service aliases make this seam usable by API/pipeline callers
    # without coupling those callers to one verb.
    build = assemble
    render = assemble
    generate = assemble
    assemble_report = assemble

    def export(
        self,
        evidence: DemandConversionEvidence | str,
        **kwargs: Any,
    ) -> dict[str, InsightReport]:
        """Assemble a client/export-safe report bundle."""

        kwargs["for_export"] = True
        return self.assemble(evidence, **kwargs)

    assemble_for_export = export

    def _resolve_evidence(
        self,
        evidence: DemandConversionEvidence | str,
    ) -> DemandConversionEvidence:
        if isinstance(evidence, DemandConversionEvidence):
            loader = getattr(self.repository, "get_demand_conversion_evidence", None)
            persisted = loader(evidence.id) if callable(loader) else None
            if persisted is None:
                raise ValueError("demand conversion evidence is not persisted")
            if canonical_sha256(persisted.to_dict()) != canonical_sha256(evidence.to_dict()):
                raise ValueError("demand conversion evidence no longer matches")
            return persisted
        loader = getattr(self.repository, "get_demand_conversion_evidence", None)
        persisted = loader(str(evidence)) if callable(loader) else None
        if persisted is None:
            raise ValueError(f"demand conversion evidence not found: {evidence}")
        return persisted

    def _completed_run(self, evidence: DemandConversionEvidence) -> Any:
        loader = getattr(self.repository, "get_run", None)
        run = loader(evidence.insight_run_id) if callable(loader) else None
        if run is None:
            raise ValueError(f"originating insight run not found: {evidence.insight_run_id}")
        if getattr(run, "status", None) != "completed":
            raise ValueError("demand conversion reports require a completed insight run")
        return run

    def _evidence_payload_for_report(
        self,
        evidence: DemandConversionEvidence,
        *,
        requested_mode: str,
        for_export: bool,
    ) -> dict[str, Any]:
        if for_export:
            # This performs the approval check and validates every evidence ref
            # again immediately before export.  It also removes owner-only
            # funnel data from a prospect payload as defense in depth.
            payload = self.validation.client_payload(
                evidence,
                requested_mode=requested_mode,
                for_export=True,
            )
        else:
            payload = evidence.to_dict()
        if requested_mode == "prospect":
            payload = self._prospect_safe_payload(payload)
        return payload

    @classmethod
    def _prospect_safe_payload(cls, payload: Mapping[str, Any]) -> dict[str, Any]:
        """Defensively remove owner-only records from legacy/hand-built data."""

        value = cls._filter_owner_records(deepcopy(dict(payload)))
        if not isinstance(value, dict):  # pragma: no cover - defensive typing guard
            return {}
        baseline = value.get("observed_inputs", {}).get("funnel_baseline")
        if isinstance(baseline, dict) and "sources" in baseline:
            value.setdefault("observed_inputs", {})["funnel_baseline"] = {
                "status": "unknown",
                "reason": "Owner aggregate measurements are unavailable in prospect mode.",
            }
        value["source_snapshots"] = [
            item
            for item in value.get("source_snapshots", [])
            if isinstance(item, dict)
            and item.get("source_class") != "owner_first_party"
        ]
        return value

    @classmethod
    def _filter_owner_records(cls, value: Any) -> Any:
        if isinstance(value, list):
            filtered = []
            for item in value:
                candidate = cls._filter_owner_records(item)
                if candidate is not None:
                    filtered.append(candidate)
            return filtered
        if isinstance(value, dict):
            if value.get("source_class") == "owner_first_party":
                return None
            result: dict[str, Any] = {}
            for key, item in value.items():
                candidate = cls._filter_owner_records(item)
                if candidate is not None:
                    result[key] = candidate
            return result
        return value

    def _payload(
        self,
        evidence: DemandConversionEvidence,
        evidence_payload: Mapping[str, Any],
        validation_result: Mapping[str, Any],
    ) -> dict[str, Any]:
        sources = [
            source
            for source in evidence_payload.get("source_snapshots", [])
            if isinstance(source, dict)
        ]
        groups = [
            group
            for group in evidence_payload.get("intent_groups", [])
            if isinstance(group, dict)
        ]
        observed_inputs = evidence_payload.get("observed_inputs", {})
        observed_inputs = observed_inputs if isinstance(observed_inputs, dict) else {}
        modeled_outputs = evidence_payload.get("modeled_outputs", {})
        modeled_outputs = modeled_outputs if isinstance(modeled_outputs, dict) else {}
        assumptions = evidence_payload.get("assumptions", [])
        assumptions = assumptions if isinstance(assumptions, list) else []
        evidence_refs = evidence_payload.get("evidence_refs", [])
        evidence_refs = evidence_refs if isinstance(evidence_refs, list) else []

        source_hashes = self._source_hashes(evidence, sources)
        hierarchy = self._evidence_hierarchy(sources, evidence.created_at)
        demand_groups = self._demand_groups(groups)
        funnel = self._funnel(observed_inputs, modeled_outputs, assumptions)
        capacity_revenue = self._capacity_revenue(
            evidence_payload.get("capacity", {}),
            evidence_payload.get("economics", {}),
            modeled_outputs,
        )
        confidence = self._confidence(
            evidence,
            observed_inputs,
            validation_result,
            len(evidence_refs),
        )
        source_age = self._source_age(sources, evidence.created_at)
        limitations = self._limitations(evidence, observed_inputs, modeled_outputs)
        what_would_change = self._what_would_change(
            evidence,
            observed_inputs,
            modeled_outputs,
            source_age,
        )
        service_fit = self._service_fit(evidence, groups)
        summary = self._executive_summary(
            evidence,
            demand_groups,
            modeled_outputs,
            confidence,
        )

        # Dict insertion order is intentional: it mirrors the operator-facing
        # report order and keeps JSON/Markdown evidence easy to scan.
        return {
            "report_contract": self.REPORT_VERSION,
            "schema_version": self.SCHEMA_VERSION,
            "mode": evidence.mode,
            "run_id": evidence.insight_run_id,
            "evidence_id": evidence.id,
            "prospect_id": evidence.prospect_id,
            "vertical_id": evidence.vertical_id,
            "market": evidence.market,
            "executive_summary": summary,
            "evidence_hierarchy": hierarchy,
            "demand_groups_and_trends": demand_groups,
            "demand_groups": demand_groups,
            "observed_vs_modeled_funnel": funnel,
            "funnel": funnel,
            "capacity_and_revenue_ranges": capacity_revenue,
            "capacity_and_revenue": capacity_revenue,
            "confidence_and_completeness": confidence,
            "confidence": confidence,
            "source_age": source_age,
            "limitations": limitations,
            "what_would_change_this": what_would_change,
            "what_would_change": what_would_change,
            "service_fit": service_fit,
            "source_hashes": source_hashes,
            "evidence_refs": deepcopy(evidence_refs),
            "validation": dict(validation_result),
            "evidence": {
                "contract_version": evidence_payload.get("contract_version"),
                "formula_version": evidence_payload.get(
                    "formula_version", DEMAND_CONVERSION_FORMULA_VERSION
                ),
                "state": evidence_payload.get("state"),
                "status": evidence_payload.get("status"),
                "completeness_percent": evidence_payload.get(
                    "completeness_percent"
                ),
                "source_snapshots": deepcopy(sources),
                "intent_groups": deepcopy(groups),
                "observed_inputs": deepcopy(observed_inputs),
                "modeled_outputs": deepcopy(modeled_outputs),
                "economics": deepcopy(evidence_payload.get("economics", {})),
                "capacity": deepcopy(evidence_payload.get("capacity", {})),
                "assumptions": deepcopy(assumptions),
                "warnings": deepcopy(evidence_payload.get("warnings", [])),
                "evidence_refs": deepcopy(evidence_refs),
            },
        }

    @staticmethod
    def _source_hashes(
        evidence: DemandConversionEvidence,
        sources: list[dict[str, Any]],
    ) -> dict[str, str]:
        hashes = {"evidence": canonical_sha256(evidence.to_dict())}
        for index, source in enumerate(sources):
            source_hash = str(source.get("source_sha256") or "")
            if source_hash:
                name = str(source.get("source_name") or "source")
                hashes[f"source:{index}:{name}"] = source_hash
        return hashes

    @classmethod
    def _evidence_hierarchy(
        cls,
        sources: list[dict[str, Any]],
        created_at: str,
    ) -> list[dict[str, Any]]:
        hierarchy: list[dict[str, Any]] = []
        for source in sorted(
            sources,
            key=lambda item: (
                int(item.get("hierarchy_level") or 99),
                str(item.get("source_name") or ""),
                str(item.get("source_sha256") or ""),
            ),
        ):
            hierarchy.append(
                {
                    "hierarchy_level": source.get("hierarchy_level"),
                    "source_class": source.get("source_class"),
                    "provenance_label": source.get("provenance_label"),
                    "source_name": source.get("source_name"),
                    "source_sha256": source.get("source_sha256"),
                    "artifact_ref": source.get("artifact_ref"),
                    "snapshot_date": source.get("snapshot_date"),
                    "source_age": cls._age(source.get("snapshot_date"), created_at),
                }
            )
        return hierarchy

    @classmethod
    def _demand_groups(cls, groups: list[dict[str, Any]]) -> dict[str, Any]:
        nonbrand = 0.0
        brand = 0.0
        trend_count = 0
        normalized: list[dict[str, Any]] = []
        for group in groups:
            occasions = group.get("monthly_search_occasions")
            if isinstance(occasions, (int, float)):
                if group.get("is_brand"):
                    brand += float(occasions)
                else:
                    nonbrand += float(occasions)
            trends = group.get("trend_evidence")
            if isinstance(trends, list):
                trend_count += len(trends)
            normalized.append(
                {
                    "group_id": group.get("group_id"),
                    "intent_family": group.get("intent_family"),
                    "representative_term": group.get("representative_term"),
                    "monthly_search_occasions": occasions,
                    "is_brand": bool(group.get("is_brand")),
                    "aggregation_rule": group.get("aggregation_rule"),
                    "provenance_label": group.get("provenance_label"),
                    "trend_evidence": deepcopy(trends or []),
                }
            )
        return {
            "semantics": "Monthly search occasions, not unique people.",
            "groups": normalized,
            "group_count": len(normalized),
            "trend_observation_count": trend_count,
            "nonbrand_monthly_search_occasions": cls._round(nonbrand),
            "brand_monthly_search_occasions_excluded_from_net_new": cls._round(brand),
        }

    @classmethod
    def _funnel(
        cls,
        observed_inputs: dict[str, Any],
        modeled_outputs: dict[str, Any],
        assumptions: list[dict[str, Any]],
    ) -> dict[str, Any]:
        observed = deepcopy(observed_inputs.get("funnel_baseline"))
        if observed is None:
            observed = {"status": "unknown", "reason": "No observed funnel baseline."}
        return {
            "semantics": "Observed measurements and modeled lift are separate evidence layers.",
            "observed": observed,
            "modeled": deepcopy(modeled_outputs),
            "assumptions": deepcopy(assumptions),
            "formula": {
                "version": DEMAND_CONVERSION_FORMULA_VERSION,
                "expression": cls.FORMULA_TEXT,
                "forecast_label": cls.FORECAST_LABEL,
            },
        }

    @classmethod
    def _capacity_revenue(
        cls,
        capacity: Any,
        economics: Any,
        modeled_outputs: dict[str, Any],
    ) -> dict[str, Any]:
        capacity_payload = deepcopy(capacity) if isinstance(capacity, dict) else {}
        economics_payload = deepcopy(economics) if isinstance(economics, dict) else {}
        bands: dict[str, Any] = {}
        for band in ("low", "base", "high"):
            output = modeled_outputs.get(band)
            bands[band] = deepcopy(output) if isinstance(output, dict) else None
        return {
            "capacity": capacity_payload,
            "economics": economics_payload,
            "ranges": bands,
            "incremental_members_range": {
                band: (value.get("incremental_members") if isinstance(value, dict) else None)
                for band, value in bands.items()
            },
            "incremental_recurring_revenue_range": {
                band: (
                    value.get("incremental_recurring_revenue")
                    if isinstance(value, dict)
                    else None
                )
                for band, value in bands.items()
            },
            "annual_run_rate_range": {
                band: (value.get("annual_run_rate") if isinstance(value, dict) else None)
                for band, value in bands.items()
            },
            "forecast_label": cls.FORECAST_LABEL,
        }

    @classmethod
    def _confidence(
        cls,
        evidence: DemandConversionEvidence,
        observed_inputs: dict[str, Any],
        validation_result: Mapping[str, Any],
        evidence_ref_count: int,
    ) -> dict[str, Any]:
        checks = observed_inputs.get("completeness_checks", [])
        checks = checks if isinstance(checks, list) else []
        known = [
            item
            for item in checks
            if isinstance(item, dict) and item.get("status") == "known"
        ]
        unknown = [
            item
            for item in checks
            if isinstance(item, dict) and item.get("status") != "known"
        ]
        return {
            "completeness_percent": evidence.completeness_percent,
            "status": evidence.status,
            "known_checks": [item.get("check_id") for item in known],
            "unknown_checks": [item.get("check_id") for item in unknown],
            "evidence_ref_count": evidence_ref_count,
            "validated_reference_count": validation_result.get(
                "resolved_reference_count", 0
            ),
            "source_count": validation_result.get("source_count", 0),
            "confidence_semantics": (
                "Completeness reflects available, context-matched evidence; it is "
                "not a probability of conversion or forecast accuracy."
            ),
        }

    @classmethod
    def _source_age(
        cls,
        sources: list[dict[str, Any]],
        created_at: str,
    ) -> list[dict[str, Any]]:
        result = []
        for source in sources:
            result.append(
                {
                    "source_name": source.get("source_name"),
                    "source_class": source.get("source_class"),
                    "snapshot_date": source.get("snapshot_date"),
                    **cls._age(source.get("snapshot_date"), created_at),
                }
            )
        return result

    @staticmethod
    def _age(snapshot_date: Any, created_at: str) -> dict[str, Any]:
        raw = str(snapshot_date or "").strip()
        as_of = str(created_at or "")[:10]
        try:
            start = date.fromisoformat(raw[:10])
            end = date.fromisoformat(as_of)
        except ValueError:
            return {"as_of": as_of or None, "age_days": None, "freshness": "unknown"}
        age = max(0, (end - start).days)
        return {
            "as_of": end.isoformat(),
            "age_days": age,
            "freshness": "current" if age <= 30 else "dated",
        }

    @classmethod
    def _limitations(
        cls,
        evidence: DemandConversionEvidence,
        observed_inputs: dict[str, Any],
        modeled_outputs: dict[str, Any],
    ) -> list[str]:
        limitations: list[str] = [str(item) for item in evidence.warnings if str(item).strip()]
        limitations.extend(
            [
                "Monthly search volume represents search occasions, not unique people.",
                "Observed funnel values describe the supplied period and do not establish causality.",
                f"Modeled outcomes use {DEMAND_CONVERSION_FORMULA_VERSION} and are scenarios, not guarantees.",
            ]
        )
        if not modeled_outputs:
            limitations.append(
                "Low/base/high outputs are suppressed until all required rates, economics, and capacity inputs are known."
            )
        baseline = observed_inputs.get("funnel_baseline")
        if not isinstance(baseline, dict) or baseline.get("status") == "unknown":
            limitations.append("An owner-authorized observed funnel baseline is unavailable.")
        if evidence.mode == "prospect":
            limitations.append(
                "Prospect mode uses public, supplied, and assumed evidence only; owner-first-party data is excluded."
            )
        return list(dict.fromkeys(limitations))

    @classmethod
    def _what_would_change(
        cls,
        evidence: DemandConversionEvidence,
        observed_inputs: dict[str, Any],
        modeled_outputs: dict[str, Any],
        source_age: list[dict[str, Any]],
    ) -> list[str]:
        changes: list[str] = []
        checks = observed_inputs.get("completeness_checks", [])
        for check in checks if isinstance(checks, list) else []:
            if isinstance(check, dict) and check.get("status") != "known":
                check_id = str(check.get("check_id") or "evidence input")
                changes.append(f"Resolve the {check_id} evidence gap.")
        if not modeled_outputs:
            changes.append("Supply reviewed low/base/high funnel rates and economics to unlock scenarios.")
        if evidence.mode == "prospect":
            changes.append(
                "An explicitly authorized, aggregate owner export could replace assumed funnel rates with observed rates."
            )
        if any(item.get("freshness") == "dated" for item in source_age):
            changes.append("Refresh dated source snapshots for the current market and planning period.")
        if not changes:
            changes.append("No unresolved evidence change was identified; continue monitoring source periods and capacity.")
        return list(dict.fromkeys(changes))

    @classmethod
    def _service_fit(
        cls,
        evidence: DemandConversionEvidence,
        groups: list[dict[str, Any]],
    ) -> dict[str, Any]:
        paths = []
        for group in groups:
            paths.append(
                {
                    "intent_family": group.get("intent_family"),
                    "representative_term": group.get("representative_term"),
                    "service_path": evidence.vertical_id,
                    "basis": "approved demand intent group",
                    "provenance_label": group.get("provenance_label"),
                }
            )
        return {
            "vertical_id": evidence.vertical_id,
            "paths": paths,
            "semantics": "Service fit is a prioritization aid from approved intent groups, not a ranking or revenue promise.",
        }

    @classmethod
    def _executive_summary(
        cls,
        evidence: DemandConversionEvidence,
        demand_groups: dict[str, Any],
        modeled_outputs: dict[str, Any],
        confidence: dict[str, Any],
    ) -> str:
        observed_state = "available" if confidence.get("known_checks") else "limited"
        modeled_state = "available" if modeled_outputs else "suppressed"
        return (
            f"{evidence.mode.replace('_', ' ').title()} evidence for {evidence.market} "
            f"contains {demand_groups.get('group_count', 0)} approved demand group(s). "
            f"Observed funnel evidence is {observed_state}; low/base/high modeled outcomes are "
            f"{modeled_state}. Completeness is {evidence.completeness_percent:g}% ({evidence.status}). "
            "Modeled outcomes are bounded scenarios, not causal findings or revenue guarantees."
        )

    @classmethod
    def _markdown(cls, payload: Mapping[str, Any]) -> str:
        lines = [
            "# Demand-to-conversion evidence report",
            "",
            "## Executive summary",
            str(payload.get("executive_summary") or "Evidence-backed demand-to-conversion snapshot."),
            "",
            "## Evidence hierarchy",
        ]
        hierarchy = payload.get("evidence_hierarchy", [])
        if hierarchy:
            for item in hierarchy:
                lines.append(
                    "- L{level} {name} ({source_class}; {provenance}) — {date}; {ref}".format(
                        level=item.get("hierarchy_level", "?"),
                        name=item.get("source_name", "source"),
                        source_class=item.get("source_class", "unknown"),
                        provenance=item.get("provenance_label", "unknown"),
                        date=item.get("snapshot_date", "date unknown"),
                        ref=item.get("artifact_ref", "artifact unknown"),
                    )
                )
        else:
            lines.append("- No source snapshots were available.")

        lines.extend(["", "## Demand groups and trends"])
        demand = payload.get("demand_groups_and_trends", {})
        lines.append(f"- Semantics: {demand.get('semantics', 'Search occasions, not unique people.')}")
        for group in demand.get("groups", []) if isinstance(demand, dict) else []:
            trend_count = len(group.get("trend_evidence", [])) if isinstance(group, dict) else 0
            lines.append(
                f"- {group.get('intent_family')}: {group.get('representative_term')} — "
                f"{group.get('monthly_search_occasions', 'unknown')} monthly search occasions; "
                f"{trend_count} trend observation(s)."
            )
        lines.extend(["", "## Observed vs modeled funnel"])
        funnel = payload.get("observed_vs_modeled_funnel", {})
        lines.append(f"- Observed baseline: {cls._compact(funnel.get('observed'))}")
        lines.append(
            f"- Formula context: {funnel.get('formula', {}).get('version', DEMAND_CONVERSION_FORMULA_VERSION)}; "
            f"{funnel.get('formula', {}).get('forecast_label', cls.FORECAST_LABEL)}."
        )
        modeled = funnel.get("modeled") if isinstance(funnel, dict) else {}
        if modeled:
            for band in ("low", "base", "high"):
                if isinstance(modeled.get(band), dict):
                    value = modeled[band]
                    lines.append(
                        f"- {band.title()}: {value.get('incremental_qualified_visits', 'unknown')} visits → "
                        f"{value.get('incremental_members', 'unknown')} members → "
                        f"{value.get('incremental_recurring_revenue', 'unknown')} recurring revenue."
                    )
        else:
            lines.append("- Modeled funnel: unknown until required inputs are supplied.")

        lines.extend(["", "## Capacity and revenue ranges"])
        ranges = payload.get("capacity_and_revenue_ranges", {})
        lines.append(f"- Capacity: {cls._compact(ranges.get('capacity'))}")
        lines.append(f"- Low/base/high members: {cls._compact(ranges.get('incremental_members_range'))}")
        lines.append(
            f"- Low/base/high recurring revenue: {cls._compact(ranges.get('incremental_recurring_revenue_range'))}"
        )
        lines.append(f"- {ranges.get('forecast_label', cls.FORECAST_LABEL)}")

        lines.extend(["", "## Confidence and completeness"])
        confidence = payload.get("confidence_and_completeness", {})
        lines.append(f"- Completeness: {confidence.get('completeness_percent', 'unknown')}% ({confidence.get('status', 'unknown')})")
        lines.append(f"- Known checks: {', '.join(confidence.get('known_checks', [])) or 'none'}")
        lines.append(f"- Unknown checks: {', '.join(confidence.get('unknown_checks', [])) or 'none'}")

        lines.extend(["", "## Source age"])
        for item in payload.get("source_age", []) or []:
            lines.append(
                f"- {item.get('source_name')}: {item.get('snapshot_date', 'unknown')} — "
                f"{item.get('age_days', 'unknown')} day(s) at {item.get('as_of', 'unknown')} ({item.get('freshness', 'unknown')})."
            )

        lines.extend(["", "## Limitations"])
        lines.extend(f"- {item}" for item in payload.get("limitations", []) or [])
        lines.extend(["", "## What would change this"])
        lines.extend(f"- {item}" for item in payload.get("what_would_change_this", []) or [])

        lines.extend(["", "## Service fit"])
        service_fit = payload.get("service_fit", {})
        for item in service_fit.get("paths", []) if isinstance(service_fit, dict) else []:
            lines.append(
                f"- {item.get('intent_family')}: {item.get('service_path')} "
                f"({item.get('basis', 'evidence-backed')})."
            )
        if not isinstance(service_fit, dict) or not service_fit.get("paths"):
            lines.append("- No approved intent group supplied a service path.")
        return "\n".join(lines) + "\n"

    @classmethod
    def _combined_markdown(cls, payload: Mapping[str, Any]) -> str:
        # Keep this renderer focused on the demand sections so an older run
        # with only v2 still receives the same report order.
        lines = [
            "# Combined demand-conversion and SEO evidence report",
            "",
            "## Executive summary",
            str(payload.get("executive_summary") or "Evidence-backed demand-to-conversion snapshot."),
            "",
            "## Evidence hierarchy",
        ]
        for item in payload.get("evidence_hierarchy", []) or []:
            lines.append(
                f"- L{item.get('hierarchy_level', '?')} {item.get('source_name', 'source')} "
                f"({item.get('provenance_label', 'unknown')}) — {item.get('artifact_ref', 'artifact unknown')}"
            )
        demand = payload.get("demand_groups_and_trends", {})
        lines.extend(["", "## Demand groups and trends"])
        lines.append(f"- {demand.get('semantics', 'Monthly search occasions, not unique people.')}")
        for group in demand.get("groups", []) if isinstance(demand, dict) else []:
            lines.append(
                f"- {group.get('intent_family')}: {group.get('representative_term')} — "
                f"{group.get('monthly_search_occasions', 'unknown')} monthly search occasions."
            )
        funnel = payload.get("observed_vs_modeled_funnel", {})
        lines.extend(["", "## Observed vs modeled funnel"])
        lines.append(f"- Observed baseline: {cls._compact(funnel.get('observed'))}")
        lines.append(f"- Formula: {funnel.get('formula', {}).get('version', DEMAND_CONVERSION_FORMULA_VERSION)} ({cls.FORECAST_LABEL}).")
        ranges = payload.get("capacity_and_revenue_ranges", {})
        lines.extend(["", "## Capacity and revenue ranges"])
        lines.append(f"- Members: {cls._compact(ranges.get('incremental_members_range'))}")
        lines.append(f"- Recurring revenue: {cls._compact(ranges.get('incremental_recurring_revenue_range'))}")
        confidence = payload.get("confidence_and_completeness", {})
        lines.extend(["", "## Confidence and completeness"])
        lines.append(f"- {confidence.get('completeness_percent', 'unknown')}% ({confidence.get('status', 'unknown')})")
        lines.extend(["", "## Source age"])
        for item in payload.get("source_age", []) or []:
            lines.append(
                f"- {item.get('source_name')}: {item.get('snapshot_date', 'unknown')} — "
                f"{item.get('age_days', 'unknown')} day(s), {item.get('freshness', 'unknown')}."
            )
        lines.extend(["", "## Limitations"])
        lines.extend(f"- {item}" for item in payload.get("limitations", []) or [])
        lines.extend(["", "## What would change this"])
        lines.extend(f"- {item}" for item in payload.get("what_would_change_this", []) or [])
        lines.extend(["", "## Service fit"])
        fit = payload.get("service_fit", {})
        for item in fit.get("paths", []) if isinstance(fit, dict) else []:
            lines.append(f"- {item.get('intent_family')}: {item.get('service_path')}")

        legacy = payload.get("legacy_report", {})
        lines.extend(["", "## Existing SEO/commercial context"])
        version = legacy.get("report_version") or "unavailable"
        lines.append(f"- Legacy report used: {version}.")
        legacy_payload = legacy.get("payload") if isinstance(legacy, dict) else {}
        if isinstance(legacy_payload, dict):
            summary = (
                legacy_payload.get("executive_summary")
                or legacy_payload.get("executive_answer")
                or legacy_payload.get("summary")
            )
            if summary:
                lines.append(f"- Legacy context summary: {cls._compact(summary)}")
        return "\n".join(lines) + "\n"

    def _legacy_payload(self, run_id: str, mode: str) -> dict[str, Any]:
        report = self.repository.get_report(run_id, "v4") or self.repository.get_report(
            run_id, "v2"
        )
        if report is None:
            return {
                "report_version": None,
                "report_contract": None,
                "payload": {},
                "status": "unknown",
                "limitations": [
                    "No legacy v4 or v2 report was available for combined context."
                ],
            }
        legacy_payload = deepcopy(report.report_payload)
        if mode == "prospect":
            legacy_payload = self._filter_owner_records(legacy_payload)
        return {
            "report_version": report.report_version,
            "report_contract": legacy_payload.get("report_contract"),
            "payload": legacy_payload,
            "status": report.report_status,
            "limitations": [],
        }

    def _combined_payload(
        self,
        run_id: str,
        evidence: DemandConversionEvidence,
        demand_payload: dict[str, Any],
    ) -> dict[str, Any]:
        payload = {
            "report_contract": self.COMBINED_VERSION,
            "schema_version": self.SCHEMA_VERSION,
            "run_id": run_id,
            "evidence_id": evidence.id,
            "mode": evidence.mode,
            "prospect_id": evidence.prospect_id,
            "vertical_id": evidence.vertical_id,
            "market": evidence.market,
            "executive_summary": demand_payload.get("executive_summary"),
            "evidence_hierarchy": deepcopy(demand_payload.get("evidence_hierarchy", [])),
            "demand_groups_and_trends": deepcopy(
                demand_payload.get("demand_groups_and_trends", {})
            ),
            "demand_groups": deepcopy(demand_payload.get("demand_groups", {})),
            "observed_vs_modeled_funnel": deepcopy(
                demand_payload.get("observed_vs_modeled_funnel", {})
            ),
            "funnel": deepcopy(demand_payload.get("funnel", {})),
            "capacity_and_revenue_ranges": deepcopy(
                demand_payload.get("capacity_and_revenue_ranges", {})
            ),
            "capacity_and_revenue": deepcopy(
                demand_payload.get("capacity_and_revenue", {})
            ),
            "confidence_and_completeness": deepcopy(
                demand_payload.get("confidence_and_completeness", {})
            ),
            "confidence": deepcopy(demand_payload.get("confidence", {})),
            "source_age": deepcopy(demand_payload.get("source_age", [])),
            "limitations": deepcopy(demand_payload.get("limitations", [])),
            "what_would_change_this": deepcopy(
                demand_payload.get("what_would_change_this", [])
            ),
            "what_would_change": deepcopy(
                demand_payload.get("what_would_change", [])
            ),
            "service_fit": deepcopy(demand_payload.get("service_fit", {})),
            "demand_conversion": deepcopy(demand_payload),
        }
        legacy = self._legacy_payload(run_id, evidence.mode)
        payload["legacy_report"] = legacy
        payload["source_versions"] = {
            "demand_conversion": DEMAND_CONVERSION_REPORT_VERSION,
            "legacy": legacy.get("report_version") or "unavailable",
        }
        # Friendly aliases make consumers that already know v2/v4 able to read
        # the additive report without a migration.  They never replace those
        # original artifacts.
        if legacy.get("report_version") == "v4":
            payload["v4"] = deepcopy(legacy.get("payload", {}))
        elif legacy.get("report_version") == "v2":
            payload["v2"] = deepcopy(legacy.get("payload", {}))
        return payload

    @classmethod
    def _report(
        cls,
        run: Any,
        evidence: DemandConversionEvidence,
        report_version: str,
        payload: dict[str, Any],
        markdown: str,
    ) -> InsightReport:
        return InsightReport(
            id=f"{evidence.id}-{report_version}",
            insight_run_id=evidence.insight_run_id,
            seo_target_id=str(
                getattr(run, "seo_target_id", None)
                or evidence.target_id
                or evidence.insight_run_id
            ),
            attempt_id=getattr(run, "attempt_id", None) or evidence.attempt_id,
            report_version=report_version,
            report_status=evidence.status,
            headline=f"Demand-to-conversion evidence — {evidence.market}",
            executive_summary=str(payload.get("executive_summary") or ""),
            key_actions=[
                {"action": item}
                for item in payload.get("what_would_change_this", [])[:3]
            ],
            report_payload=payload,
            export_json=payload,
            export_markdown=markdown,
            created_at=evidence.created_at,
            updated_at=evidence.created_at,
        )

    def _save_report_immutably(self, report: InsightReport) -> InsightReport:
        loader = getattr(self.repository, "get_report", None)
        existing = loader(report.insight_run_id, report.report_version) if callable(loader) else None
        if existing is not None:
            if existing.to_dict() != report.to_dict():
                # The canonical run report is a convenience alias.  Keep its
                # first writer intact while the evidence-scoped artifact below
                # preserves this distinct mode/version for later retrieval.
                return report
            return existing
        saver = getattr(self.repository, "save_report", None)
        if not callable(saver):
            raise ValueError("repository does not support report persistence")
        return saver(report)

    def _save_scoped_artifacts(
        self,
        run_id: str,
        evidence_id: str,
        report: InsightReport,
    ) -> bool:
        saver = getattr(self.repository, "save_opportunity_artifact", None)
        if not callable(saver):
            return False
        # The run-scoped report written by save_report is canonical.  The
        # evidence-scoped copy is an optional immutable-friendly seam for
        # repositories that expose opportunity artifact storage.
        self._assert_scoped_artifact(
            run_id,
            evidence_id,
            f"reports/{report.report_version}.json",
            report.report_payload,
        )
        saver(
            run_id,
            evidence_id,
            f"reports/{report.report_version}.json",
            report.report_payload,
        )
        if report.export_markdown:
            self._assert_scoped_artifact(
                run_id,
                evidence_id,
                f"reports/{report.report_version}.md",
                report.export_markdown.encode("utf-8"),
            )
            saver(
                run_id,
                evidence_id,
                f"reports/{report.report_version}.md",
                report.export_markdown.encode("utf-8"),
            )
        return True

    def _assert_scoped_artifact(
        self,
        run_id: str,
        evidence_id: str,
        relative_path: str,
        payload: dict[str, Any] | bytes,
    ) -> None:
        """Fail closed if a known file-backed scoped artifact was changed."""

        runs_dir = getattr(self.repository, "runs_dir", None)
        if runs_dir is None:
            files = getattr(self.repository, "_files", None)
            runs_dir = getattr(files, "runs_dir", None)
        if runs_dir is None:
            return
        path = Path(runs_dir) / str(run_id) / "opportunity" / str(evidence_id) / relative_path
        if not path.exists():
            return
        try:
            existing = (
                json.loads(path.read_text(encoding="utf-8"))
                if isinstance(payload, dict)
                else path.read_bytes()
            )
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            raise ValueError("demand conversion scoped artifacts are immutable") from exc
        if existing != payload:
            raise ValueError("demand conversion scoped artifacts are immutable")

    def _save_snapshot(
        self,
        evidence: DemandConversionEvidence,
        report: InsightReport,
        run_id: str,
        *,
        scoped_artifacts: bool,
    ) -> DemandConversionReportSnapshot:
        payload_hash = canonical_sha256(report.report_payload)
        source_hashes = report.report_payload.get("source_hashes", {})
        source_hashes = {
            str(key): str(value)
            for key, value in source_hashes.items()
            if isinstance(value, str) and value
        }
        payload_ref = (
            f"runs/{run_id}/opportunity/{evidence.id}/reports/"
            f"{self.REPORT_VERSION}.json"
            if scoped_artifacts
            else f"runs/{run_id}/reports/{self.REPORT_VERSION}.json"
        )
        markdown_ref = (
            f"runs/{run_id}/opportunity/{evidence.id}/reports/"
            f"{self.REPORT_VERSION}.md"
            if scoped_artifacts
            else f"runs/{run_id}/reports/{self.REPORT_VERSION}.md"
        )
        manifest_hash = canonical_sha256(
            {
                "report_contract": self.REPORT_VERSION,
                "payload_artifact_ref": payload_ref,
                "markdown_artifact_ref": markdown_ref,
                "payload_sha256": payload_hash,
                "source_hashes": source_hashes,
            }
        )
        lister = getattr(self.repository, "list_demand_conversion_report_snapshots", None)
        existing_records = (
            lister(
                run_id=run_id,
                demand_conversion_evidence_id=evidence.id,
                mode=evidence.mode,
            )
            if callable(lister)
            else []
        )
        for existing in existing_records:
            if existing.payload_sha256 == payload_hash:
                return existing
            raise ValueError(
                "demand conversion report snapshots are immutable for this evidence and mode"
            )
        snapshot = DemandConversionReportSnapshot(
            demand_conversion_evidence_id=evidence.id,
            run_id=run_id,
            mode=evidence.mode,
            payload_sha256=payload_hash,
            payload_artifact_ref=payload_ref,
            source_hashes=source_hashes,
            manifest_sha256=manifest_hash,
            completeness_percent=evidence.completeness_percent,
            status=evidence.status,
            created_at=evidence.created_at,
        )
        saver = getattr(self.repository, "save_demand_conversion_report_snapshot", None)
        if not callable(saver):
            raise ValueError("repository does not support demand conversion report snapshots")
        return saver(snapshot)

    @staticmethod
    def _round(value: float | int | None) -> float | int | None:
        if value is None:
            return None
        rounded = round(float(value), 4)
        return int(rounded) if rounded.is_integer() else rounded

    @staticmethod
    def _compact(value: Any) -> str:
        if value is None:
            return "unknown"
        if isinstance(value, str):
            return value
        try:
            return json.dumps(value, sort_keys=True, ensure_ascii=False)
        except TypeError:
            return str(value)
