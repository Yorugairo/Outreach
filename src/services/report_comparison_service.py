"""Context-aware, immutable report comparisons.

The comparison service intentionally treats report payloads as untrusted,
versioned evidence.  It compares only identities that can be aligned and
returns explicit ``unknown`` entries when context is missing or incompatible.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import asdict, is_dataclass
from typing import Any
from urllib.parse import urlsplit, urlunsplit

from src.models import ReportComparisonSnapshot, ReportSnapshot, canonical_sha256


class ReportComparisonService:
    """Build ``comparison-v1`` snapshots without mutating source reports."""

    CONTRACT_VERSION = "comparison-v1"
    _DIMENSIONS = (
        "stable_checks",
        "normalized_pages",
        "keyword_set",
        "grid_points",
        "prompts",
        "agent_model",
        "agent_rubric",
    )

    def __init__(self, repository: Any | None = None) -> None:
        self.repository = repository

    def compare(
        self,
        baseline_snapshot: Any,
        current_snapshot: Any,
        baseline_payload: Any | None = None,
        current_payload: Any | None = None,
        *,
        target_id: str | None = None,
        baseline_assessment: Any | None = None,
        current_assessment: Any | None = None,
    ) -> ReportComparisonSnapshot:
        """Compare two immutable snapshots and return a write-once model.

        ``baseline_payload`` and ``current_payload`` may be report payloads,
        ``InsightReport`` instances, or envelopes containing ``report_payload``.
        A payload is optional when the caller only needs an explicit unknown
        comparison; hashes and source identities are still retained.
        """

        base_info = self._snapshot_info(baseline_snapshot, baseline_payload)
        current_info = self._snapshot_info(current_snapshot, current_payload)
        base_payload = self._payload(baseline_payload, baseline_snapshot)
        current_payload_map = self._payload(current_payload, current_snapshot)
        resolved_target = (
            str(target_id or "").strip()
            or self._target_id(base_payload)
            or self._target_id(current_payload_map)
            or base_info.get("target_id")
            or current_info.get("target_id")
            or "unknown-target"
        )

        compatibility = self._compatibility(
            base_payload,
            current_payload_map,
            baseline_assessment,
            current_assessment,
            base_info,
            current_info,
            target_id=target_id,
        )
        unknown_reasons: list[str] = []
        if not compatibility["same_target"]:
            unknown_reasons.append("Snapshots belong to different normalized targets.")
        reasons = {
            "stable_checks": "Stable check registry or formula identity differs.",
            "normalized_pages": "Page identity normalization context differs.",
            "keyword_set": "Keyword set identity or version differs.",
            "grid_points": "Local visibility grid identity differs.",
            "prompts": "Prompt/topic set identity or version differs.",
            "agent_model": "Validated agent recommendations use different model/provider identities.",
            "agent_rubric": "Validated agent recommendations use different prompt/rubric identities.",
        }
        unknown_reasons.extend(
            message for key, message in reasons.items() if compatibility.get(key) is False
        )

        dimensions = {
            "checks": self._dimension_changes(
                self._records(base_payload, "check"),
                self._records(current_payload_map, "check"),
                compatible=compatibility["stable_checks"],
            ),
            "pages": self._dimension_changes(
                self._records(base_payload, "page"),
                self._records(current_payload_map, "page"),
                compatible=compatibility["normalized_pages"],
            ),
            "keywords": self._dimension_changes(
                self._records(base_payload, "keyword"),
                self._records(current_payload_map, "keyword"),
                compatible=compatibility["keyword_set"],
            ),
            "grid_cells": self._dimension_changes(
                self._records(base_payload, "grid"),
                self._records(current_payload_map, "grid"),
                compatible=compatibility["grid_points"],
            ),
            "prompts": self._dimension_changes(
                self._records(base_payload, "prompt"),
                self._records(current_payload_map, "prompt"),
                compatible=compatibility["prompts"],
            ),
        }
        base_recs = self._recommendations(baseline_assessment, base_payload)
        current_recs = self._recommendations(current_assessment, current_payload_map)
        dimensions["recommendations"] = self._dimension_changes(
            base_recs,
            current_recs,
            compatible=compatibility["agent_model"] and compatibility["agent_rubric"],
        )
        dimensions["recommendations"]["versions"] = {
            "baseline": self._agent_identity(baseline_assessment, base_payload),
            "current": self._agent_identity(current_assessment, current_payload_map),
        }

        changes: dict[str, Any] = {
            **dimensions,
            # Stable top-level aliases keep consumers from having to know the
            # internal dimension names while retaining the detailed sections.
            "introduced": sorted({item for value in dimensions.values() if isinstance(value, Mapping) for item in value.get("introduced", [])}),
            "resolved": sorted({item for value in dimensions.values() if isinstance(value, Mapping) for item in value.get("resolved", [])}),
            "persisting": sorted({item for value in dimensions.values() if isinstance(value, Mapping) for item in value.get("persisting", [])}),
            "unknown": sorted({item for value in dimensions.values() if isinstance(value, Mapping) for item in value.get("unknown", [])}),
        }
        if all(compatibility.values()):
            numeric = self._numeric_deltas(base_payload, current_payload_map)
            if numeric:
                changes["numeric_deltas"] = numeric
        else:
            unknown_reasons.extend(
                "Numeric deltas were suppressed because one or more comparison dimensions are incompatible."
                for _ in [0]
            )
            # The model rejects numeric values whenever *any* compatibility
            # dimension is false.  Keep this key absent, not an empty claim.
            changes.pop("numeric_deltas", None)

        # De-duplicate while preserving deterministic order.
        unknown_reasons = sorted(set(reason for reason in unknown_reasons if reason))
        return ReportComparisonSnapshot(
            target_id=resolved_target,
            baseline_snapshot_id=base_info["id"],
            current_snapshot_id=current_info["id"],
            baseline_sha256=base_info["sha256"],
            current_sha256=current_info["sha256"],
            compatibility=compatibility,
            changes=changes,
            unknown_reasons=unknown_reasons,
        )

    compare_snapshots = compare
    compare_reports = compare
    diff = compare
    build = compare

    def compare_and_persist(self, *args: Any, **kwargs: Any) -> ReportComparisonSnapshot:
        snapshot = self.compare(*args, **kwargs)
        return self.persist(snapshot)

    def persist(self, snapshot: ReportComparisonSnapshot) -> ReportComparisonSnapshot:
        """Persist through an existing repository hook, if one is available.

        Comparison persistence is deliberately not emulated with ``save_report``:
        that would make a comparison mutable and violate the snapshot contract.
        """

        if self.repository is None:
            raise RuntimeError("comparison persistence requires a repository")
        saver = getattr(self.repository, "save_report_comparison_snapshot", None)
        if saver is None:
            saver = getattr(self.repository, "save_comparison_snapshot", None)
        if saver is None:
            raise RuntimeError(
                "repository does not expose save_report_comparison_snapshot; "
                "comparison-v1 cannot be persisted without a repository contract"
            )
        return saver(snapshot)

    def compare_runs(self, baseline_run_id: str, current_run_id: str) -> ReportComparisonSnapshot:
        if self.repository is None:
            raise RuntimeError("compare_runs requires a repository")
        baseline_run = self.repository.get_run(baseline_run_id)
        current_run = self.repository.get_run(current_run_id)
        if baseline_run is None:
            raise ValueError(f"run {baseline_run_id} not found")
        if current_run is None:
            raise ValueError(f"run {current_run_id} not found")
        base_snapshot = self._latest_snapshot(baseline_run_id)
        current_snapshot = self._latest_snapshot(current_run_id)
        base_report = self.repository.get_report(
            baseline_run_id,
            getattr(base_snapshot, "report_contract", "v2") if base_snapshot else "v2",
        ) or self.repository.get_report(baseline_run_id, "v1")
        current_report = self.repository.get_report(
            current_run_id,
            getattr(current_snapshot, "report_contract", "v2") if current_snapshot else "v2",
        ) or self.repository.get_report(current_run_id, "v1")
        base_payload = self._payload(base_report, None)
        current_payload = self._payload(current_report, None)
        base_snapshot = base_snapshot or self._synthetic_snapshot(baseline_run, base_report, base_payload)
        current_snapshot = current_snapshot or self._synthetic_snapshot(current_run, current_report, current_payload)
        return self.compare(
            base_snapshot,
            current_snapshot,
            base_payload,
            current_payload,
            target_id=self._run_target(baseline_run),
        )

    def _latest_snapshot(self, run_id: str) -> Any | None:
        getter = getattr(self.repository, "get_latest_report_snapshot", None)
        if getter is not None:
            return getter(run_id, "v2") or getter(run_id, "v1")
        lister = getattr(self.repository, "list_report_snapshots", None)
        if lister is None:
            return None
        rows = lister(run_id=run_id, limit=20)
        return rows[0] if rows else None

    @staticmethod
    def _synthetic_snapshot(run: Any, report: Any, payload: Mapping[str, Any]) -> dict[str, Any]:
        report_id = str(getattr(report, "id", "") or f"{getattr(run, 'id', 'run')}-report")
        return {
            "id": report_id,
            "run_id": getattr(run, "id", ""),
            "target_id": ReportComparisonService._run_target(run),
            "payload_sha256": canonical_sha256(report.to_dict() if hasattr(report, "to_dict") else payload),
        }

    @staticmethod
    def _run_target(run: Any) -> str:
        return str(getattr(run, "seo_target_id", "") or getattr(run, "requested_domain", "") or "unknown-target")

    @staticmethod
    def _as_mapping(value: Any) -> Mapping[str, Any]:
        if value is None:
            return {}
        if isinstance(value, Mapping):
            return value
        if hasattr(value, "to_dict"):
            result = value.to_dict()
            return result if isinstance(result, Mapping) else {}
        if is_dataclass(value):
            result = asdict(value)
            return result if isinstance(result, Mapping) else {}
        return {}

    @classmethod
    def _payload(cls, value: Any, fallback: Any) -> Mapping[str, Any]:
        mapping = cls._as_mapping(value)
        if not mapping:
            mapping = cls._as_mapping(fallback)
        for key in ("report_payload", "export_json", "payload"):
            candidate = mapping.get(key)
            if isinstance(candidate, Mapping):
                return candidate
        return mapping

    @classmethod
    def _snapshot_info(cls, snapshot: Any, payload: Any) -> dict[str, str]:
        mapping = cls._as_mapping(snapshot)
        payload_mapping = cls._payload(payload, snapshot)
        identity = str(mapping.get("id") or mapping.get("snapshot_id") or "").strip()
        if not identity:
            identity = f"snapshot-{canonical_sha256(payload_mapping)[:16]}"
        digest = str(mapping.get("payload_sha256") or mapping.get("sha256") or "").strip()
        if not digest:
            source_hashes = mapping.get("source_hashes")
            if isinstance(source_hashes, Mapping):
                digest = next((str(value) for value in source_hashes.values() if isinstance(value, str)), "")
        if len(digest) != 64 or any(char not in "0123456789abcdefABCDEF" for char in digest):
            digest = canonical_sha256(payload_mapping)
        return {
            "id": identity,
            "sha256": digest.lower(),
            "target_id": str(mapping.get("target_id") or mapping.get("seo_target_id") or "").strip(),
        }

    @classmethod
    def _target_id(cls, payload: Mapping[str, Any]) -> str:
        for key in ("target_id", "seo_target_id", "normalized_domain", "domain"):
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        target = payload.get("target")
        if isinstance(target, Mapping):
            return str(target.get("id") or target.get("normalized_domain") or "").strip()
        return ""

    @classmethod
    def _compatibility(
        cls,
        baseline: Mapping[str, Any],
        current: Mapping[str, Any],
        base_assessment: Any,
        current_assessment: Any,
        base_info: Mapping[str, str],
        current_info: Mapping[str, str],
        target_id: str | None = None,
    ) -> dict[str, bool]:
        base_target = cls._target_id(baseline) or base_info.get("target_id", "") or str(target_id or "")
        current_target = cls._target_id(current) or current_info.get("target_id", "") or str(target_id or "")
        checks_base = cls._records(baseline, "check")
        checks_current = cls._records(current, "check")
        check_context = cls._context_value(baseline, ("formula_version", "check_registry_version", "version"))
        current_check_context = cls._context_value(current, ("formula_version", "check_registry_version", "version"))
        pages_context = cls._context_value(baseline, ("page_identity_version",))
        current_pages_context = cls._context_value(current, ("page_identity_version",))
        return {
            "same_target": bool(
                base_target
                and current_target
                and cls._target_identity(base_target)
                == cls._target_identity(current_target)
            ),
            "stable_checks": bool(check_context == current_check_context and (not checks_base or not checks_current or set(checks_base) == set(checks_current))),
            "normalized_pages": pages_context == current_pages_context,
            "keyword_set": cls._context_compatible(baseline, current, ("keyword_set_id", "keyword_set_version", "keyword_set_key"), "keyword"),
            "grid_points": cls._context_compatible(baseline, current, ("grid_id", "grid_identity_sha256", "place_id"), "grid"),
            "prompts": cls._context_compatible(baseline, current, ("prompt_set_id", "prompt_version", "prompt_identity_sha256"), "prompt"),
            "agent_model": cls._agent_identity(base_assessment, baseline).get("model") == cls._agent_identity(current_assessment, current).get("model"),
            "agent_rubric": cls._agent_identity(base_assessment, baseline).get("rubric") == cls._agent_identity(current_assessment, current).get("rubric"),
        }

    @classmethod
    def _context_value(cls, payload: Mapping[str, Any], keys: Iterable[str]) -> str:
        for key in keys:
            value = payload.get(key)
            if value is not None and str(value).strip():
                return cls._norm(value)
        return ""

    @classmethod
    def _context_compatible(cls, baseline: Mapping[str, Any], current: Mapping[str, Any], keys: Iterable[str], dimension: str) -> bool:
        left = cls._context_value(baseline, keys)
        right = cls._context_value(current, keys)
        if left or right:
            return left == right and bool(left)
        left_records = cls._records(baseline, dimension)
        right_records = cls._records(current, dimension)
        # Versioned evidence dimensions cannot be assumed comparable merely
        # because their labels happen to match. Missing identity is unknown.
        return not left_records and not right_records

    @classmethod
    def _dimension_changes(cls, baseline: Mapping[str, Any], current: Mapping[str, Any], *, compatible: bool) -> dict[str, Any]:
        if not compatible:
            return {"introduced": [], "resolved": [], "persisting": [], "unknown": sorted(set(baseline) | set(current)), "status": "unknown"}
        introduced = sorted(set(current) - set(baseline))
        resolved = sorted(set(baseline) - set(current))
        persisting: list[str] = []
        unknown: list[str] = []
        for identity in sorted(set(baseline) & set(current)):
            left = str(baseline[identity].get("status") or baseline[identity].get("evidence_status") or "").casefold()
            right = str(current[identity].get("status") or current[identity].get("evidence_status") or "").casefold()
            if "unknown" in {left, right} or "incomplete" in {left, right}:
                unknown.append(identity)
            else:
                persisting.append(identity)
        return {"introduced": introduced, "resolved": resolved, "persisting": persisting, "unknown": unknown, "status": "complete" if not unknown else "partial"}

    @classmethod
    def _records(cls, payload: Mapping[str, Any], dimension: str) -> dict[str, dict[str, Any]]:
        records: dict[str, dict[str, Any]] = {}
        tokens = {
            "check": ("check", "checks", "checkpoint"),
            "page": ("page", "pages"),
            "keyword": ("keyword", "keywords", "demand", "terms"),
            "grid": ("grid", "cell", "heatmap", "local_visibility"),
            "prompt": ("prompt", "prompts", "topic", "topics"),
        }[dimension]

        def visit(value: Any, path: tuple[str, ...]) -> None:
            if isinstance(value, Mapping):
                lowered = {str(key).casefold(): item for key, item in value.items()}
                path_text = ".".join(path).casefold()
                active = any(token in path_text for token in tokens)
                identity: str | None = None
                if dimension == "check":
                    identity = lowered.get("check_id") or (lowered.get("id") if active and "status" in lowered else None)
                elif dimension == "page":
                    identity = lowered.get("normalized_url") or lowered.get("url") or lowered.get("page_id")
                    if identity and not active and "url" not in lowered and "normalized_url" not in lowered:
                        identity = None
                elif dimension == "keyword":
                    identity = lowered.get("normalized_keyword") or lowered.get("keyword") or lowered.get("query")
                    if identity and not active:
                        identity = None
                elif dimension == "grid":
                    identity = lowered.get("cell_id") or lowered.get("grid_cell_id")
                    if identity is None and active and "row" in lowered and "column" in lowered:
                        identity = f"{lowered.get('row')}:{lowered.get('column')}"
                elif dimension == "prompt":
                    identity = lowered.get("prompt_id") or lowered.get("topic_id") or lowered.get("prompt")
                    if identity and not active:
                        identity = None
                if identity is not None and str(identity).strip():
                    normalized = cls._identity(identity, dimension)
                    records.setdefault(normalized, dict(value))
                for key, child in value.items():
                    visit(child, (*path, str(key)))
            elif isinstance(value, (list, tuple)):
                for child in value:
                    visit(child, path)

        visit(payload, ())
        return records

    @classmethod
    def _recommendations(cls, assessment: Any, payload: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
        source = cls._as_mapping(assessment)
        findings = source.get("findings") if source else None
        validation = source.get("validation_result") if source else None
        if not isinstance(findings, list):
            agent = payload.get("agentic") or payload.get("agentic_analysis") or {}
            if isinstance(agent, Mapping):
                findings = agent.get("findings")
                validation = agent.get("validation_result")
        if not isinstance(findings, list):
            return {}
        if not isinstance(validation, Mapping) or validation.get("customer_safe") is not True:
            return {}
        result: dict[str, dict[str, Any]] = {}
        for finding in findings:
            if not isinstance(finding, Mapping) or finding.get("claim_type") != "recommendation":
                continue
            if finding.get("customer_safe") is not True:
                continue
            identity = finding.get("id") or finding.get("title") or finding.get("claim")
            if identity:
                result[cls._identity(identity, "recommendation")] = dict(finding)
        return result

    @classmethod
    def _agent_identity(cls, assessment: Any, payload: Mapping[str, Any]) -> dict[str, str]:
        source = cls._as_mapping(assessment)
        if not source:
            agent = payload.get("agentic") or payload.get("agentic_analysis") or {}
            source = agent if isinstance(agent, Mapping) else {}
        model = source.get("served_model") or source.get("requested_model") or source.get("model") or ""
        provider = source.get("served_provider") or source.get("provider") or ""
        rubric = source.get("rubric_version") or source.get("rubric") or ""
        prompt = source.get("prompt_version") or ""
        # Prompt and rubric are a single validated recommendation contract:
        # changing either invalidates recommendation deltas.
        return {"model": cls._norm(f"{provider}:{model}"), "rubric": cls._norm(f"{prompt}:{rubric}"), "prompt": cls._norm(prompt)}

    @classmethod
    def _numeric_deltas(cls, baseline: Mapping[str, Any], current: Mapping[str, Any]) -> dict[str, float]:
        keys = ("overall_score", "score", "page_count", "weighted_visibility", "median_rank", "completeness_percent")
        left = cls._numeric_values(baseline)
        right = cls._numeric_values(current)
        result: dict[str, float] = {}
        for key in keys:
            if key in left and key in right:
                result[key] = round(right[key] - left[key], 2)
        return result

    @classmethod
    def _numeric_values(cls, payload: Mapping[str, Any]) -> dict[str, float]:
        result: dict[str, float] = {}
        for key in ("overall_score", "score", "page_count", "weighted_visibility", "median_rank", "completeness_percent"):
            value = payload.get(key)
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                result[key] = float(value)
        for nested_key in ("metrics", "summary"):
            nested = payload.get(nested_key)
            if isinstance(nested, Mapping):
                for key in ("overall_score", "score", "page_count", "weighted_visibility", "median_rank", "completeness_percent"):
                    value = nested.get(key)
                    if isinstance(value, (int, float)) and not isinstance(value, bool):
                        result.setdefault(key, float(value))
        run = payload.get("run")
        if isinstance(run, Mapping) and isinstance(run.get("summary"), Mapping):
            for key in ("overall_score", "score", "page_count", "completeness_percent"):
                value = run["summary"].get(key)
                if isinstance(value, (int, float)) and not isinstance(value, bool):
                    result.setdefault(key, float(value))
        return result

    @staticmethod
    def _identity(value: Any, dimension: str) -> str:
        text = " ".join(str(value or "").casefold().split())
        if dimension == "page":
            try:
                parsed = urlsplit(text)
                if parsed.netloc:
                    path = parsed.path.rstrip("/") or "/"
                    host = parsed.netloc.casefold()
                    if host.startswith("www."):
                        host = host[4:]
                    return urlunsplit((parsed.scheme.casefold(), host, path, parsed.query, ""))
            except ValueError:
                pass
        return text

    @staticmethod
    def _norm(value: Any) -> str:
        return " ".join(str(value or "").casefold().split())

    @staticmethod
    def _target_identity(value: Any) -> str:
        text = str(value or "").strip().casefold()
        parsed = urlsplit(text if "://" in text else f"https://{text}")
        host = (parsed.hostname or "").rstrip(".").removeprefix("www.")
        return host or text.rstrip("/")


__all__ = ["ReportComparisonService"]
