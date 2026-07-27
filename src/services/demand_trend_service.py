"""CSV-first market-trend intake for the demand-conversion evidence layer.

The service deliberately stops at a reviewable, immutable ``DemandTrendSnapshot``
value.  It does not write to a repository.  Google Trends values are relative
indices (0--100), while Keyword Planner/operator values are supplied monthly
search-occasion estimates; neither source is a people or conversion count.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import re
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Any, Iterable, Mapping, TextIO

from src.models import DemandTrendSnapshot, KeywordSet, canonical_sha256, utc_now_iso
from src.services.demand_evidence_service import DemandEvidenceService


MAX_TREND_CSV_BYTES = 5 * 1024 * 1024
MAX_TREND_CSV_ROWS = 10_000
MAX_TREND_CSV_COLUMNS = 100
MAX_MONTHLY_SEARCHES = 1_000_000_000.0

SUPPORTED_SOURCES = {
    "google_trends_csv",
    "keyword_planner_csv",
    "operator_csv",
}
SOURCE_ALIASES = {
    "google_trends": "google_trends_csv",
    "google_trends_export": "google_trends_csv",
    "trends": "google_trends_csv",
    "trends_csv": "google_trends_csv",
    "keyword_planner": "keyword_planner_csv",
    "keyword_planner_export": "keyword_planner_csv",
    "keywordplanner": "keyword_planner_csv",
    "planner": "keyword_planner_csv",
    "operator": "operator_csv",
}

_FORMULA_RE = re.compile(r"^[=+\-@]")
_UNIQUE_PERSON_CLAIM_RE = re.compile(
    r"\bunique\s+(?:people|person|searchers|searcher|users|user|persons|individuals)\b",
    re.IGNORECASE,
)
_PII_HEADER_RE = re.compile(
    r"(?:e[-_ ]?mail|phone|mobile|first[ _-]?name|last[ _-]?name|full[ _-]?name|"
    r"contact|street[ _-]?address|postal[ _-]?address|customer|lead[ _-]?id|"
    r"user[ _-]?id|person|(?:^|[_\s-])name(?:$|[_\s-]))",
    re.IGNORECASE,
)
_SECRET_KEY_RE = re.compile(
    r"(?:api[_-]?key|authorization|cookie|credential|oauth|password|"
    r"refresh[_-]?token|secret|private[_-]?key)",
    re.IGNORECASE,
)
_DATE_HEADER_ALIASES = {
    "week",
    "month",
    "date",
    "time",
    "period",
    "day",
}
_PERIOD_RE = re.compile(r"^(?:\d{4}(?:-\d{2})?(?:-\d{2})?|\d{4}/\d{2}(?:/\d{2})?)$")


@dataclass(slots=True)
class DemandTrendImportIssue:
    """One safe-parser issue, retaining source row and field provenance."""

    row_number: int
    field: str
    message: str
    severity: str = "error"
    value: Any = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class DemandTrendGroup(dict[str, Any]):
    """Mapping group with attribute access for operator/test compatibility."""

    def __getattr__(self, name: str) -> Any:
        try:
            return self[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    def to_dict(self) -> dict[str, Any]:
        return dict(self)


@dataclass(slots=True)
class DemandTrendPreview:
    """Commit-ready trend terms plus context and operator-review issues."""

    source_sha256: str
    source: str
    rows_seen: int
    terms: list[dict[str, Any]]
    issues: list[DemandTrendImportIssue]
    prospect_id: str = ""
    vertical_id: str = ""
    market: str = ""
    period_start: str = ""
    period_end: str = ""
    location_code: int | None = None
    context: dict[str, Any] | None = None
    artifact_ref: str = ""
    groups: list[DemandTrendGroup] | None = None

    def __post_init__(self) -> None:
        if self.context is None:
            self.context = {}
        if self.groups is None:
            self.groups = []

    @property
    def rows(self) -> list[dict[str, Any]]:
        """Compatibility alias for import callers that call terms rows."""
        return self.terms

    @property
    def source_hash(self) -> str:
        return self.source_sha256

    @property
    def trend_terms(self) -> list[dict[str, Any]]:
        return self.terms

    @property
    def errors(self) -> list[DemandTrendImportIssue]:
        return [issue for issue in self.issues if issue.severity == "error"]

    @property
    def warnings(self) -> list[DemandTrendImportIssue]:
        return [issue for issue in self.issues if issue.severity == "warning"]

    @property
    def valid(self) -> bool:
        return bool(self.terms) and not self.errors

    @property
    def context_sha256(self) -> str | None:
        return str((self.context or {}).get("context_sha256") or "") or None

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_sha256": self.source_sha256,
            "source": self.source,
            "rows_seen": self.rows_seen,
            "terms": list(self.terms),
            "rows": list(self.terms),
            "groups": [group.to_dict() if hasattr(group, "to_dict") else dict(group) for group in (self.groups or [])],
            "issues": [issue.to_dict() for issue in self.issues],
            "prospect_id": self.prospect_id,
            "vertical_id": self.vertical_id,
            "market": self.market,
            "period_start": self.period_start,
            "period_end": self.period_end,
            "location_code": self.location_code,
            "context": dict(self.context or {}),
            "artifact_ref": self.artifact_ref,
            "valid": self.valid,
        }

    def to_snapshot(self, **kwargs: Any) -> DemandTrendSnapshot:
        """Materialize this preview through the non-persisting service seam."""
        return DemandTrendService().commit(self, **kwargs)


class DemandTrendService:
    """Preview and build demand-trend snapshots without persistence side effects."""

    def __init__(self, repository: Any | None = None) -> None:
        # The repository parameter is accepted for parity with the other
        # import services, but this T3 service intentionally never saves a
        # snapshot.  Parent-owned persistence can consume the returned model.
        self.repository = repository
        self._demand_service = DemandEvidenceService()

    def preview_csv(
        self,
        csv_input: str | bytes | TextIO,
        *,
        source: str = "operator_csv",
        prospect_id: str = "",
        vertical_id: str = "",
        market: str = "",
        period_start: str = "",
        period_end: str = "",
        location_code: int | None = None,
        context: Mapping[str, Any] | None = None,
        timeframe: Mapping[str, Any] | None = None,
        artifact_ref: str | None = None,
        keyword_set: KeywordSet | None = None,
        brand_terms: Iterable[str] = (),
        aggregation_rule: str = "max_close_variant",
        operator_approved: bool = False,
        operator: str | None = None,
    ) -> DemandTrendPreview:
        """Parse a bounded Trends/Planner/operator CSV without executing cells.

        The preview retains invalid rows as issues and keeps valid rows where
        possible.  ``commit`` later enforces the required snapshot context.
        ``aggregation_rule`` is recorded even while the snapshot remains in
        draft/review; it is never silently treated as operator approval.
        """
        raw_context = context
        context_input = dict(context) if isinstance(context, Mapping) else {}
        context_timeframe = context_input.get("timeframe")
        explicit_context_checks = (
            ("prospect_id", prospect_id, context_input.get("prospect_id")),
            ("vertical_id", vertical_id, context_input.get("vertical_id")),
            ("market", market, context_input.get("market") or context_input.get("location") or context_input.get("geo")),
        )
        context_mismatch_fields = {
            field
            for field, explicit, supplied in explicit_context_checks
            if str(explicit or "").strip() and str(supplied or "").strip() and str(explicit).strip() != str(supplied).strip()
        }
        if isinstance(context_timeframe, Mapping):
            context_start = context_timeframe.get("period_start") or context_timeframe.get("start")
            context_end = context_timeframe.get("period_end") or context_timeframe.get("end")
            if str(period_start or "").strip() and str(context_start or "").strip() and str(period_start).strip() != str(context_start).strip():
                context_mismatch_fields.add("period_start")
            if str(period_end or "").strip() and str(context_end or "").strip() and str(period_end).strip() != str(context_end).strip():
                context_mismatch_fields.add("period_end")
        if isinstance(context_timeframe, Mapping):
            period_start = period_start or str(context_timeframe.get("period_start") or context_timeframe.get("start") or "")
            period_end = period_end or str(context_timeframe.get("period_end") or context_timeframe.get("end") or "")
        prospect_id = prospect_id or str(context_input.get("prospect_id") or "")
        vertical_id = vertical_id or str(context_input.get("vertical_id") or "")
        market = market or str(context_input.get("market") or context_input.get("location") or context_input.get("geo") or "")
        if location_code is None and context_input.get("location_code") is not None:
            try:
                location_code = int(context_input["location_code"])
            except (TypeError, ValueError):
                pass
        if timeframe is not None:
            if not isinstance(timeframe, Mapping):
                raise ValueError("timeframe must be an object")
            supplied_start = timeframe.get("period_start") or timeframe.get("start")
            supplied_end = timeframe.get("period_end") or timeframe.get("end")
            if str(period_start or "").strip() and str(supplied_start or "").strip() and str(period_start).strip() != str(supplied_start).strip():
                context_mismatch_fields.add("period_start")
            if str(period_end or "").strip() and str(supplied_end or "").strip() and str(period_end).strip() != str(supplied_end).strip():
                context_mismatch_fields.add("period_end")
            period_start = period_start or str(timeframe.get("period_start") or timeframe.get("start") or "")
            period_end = period_end or str(timeframe.get("period_end") or timeframe.get("end") or "")
        brand_terms = tuple(brand_terms or ())
        if not vertical_id and keyword_set is not None:
            vertical_id = keyword_set.vertical_id
        if location_code is None and keyword_set is not None:
            location_code = keyword_set.location_code
        normalized_source = self._normalize_source(source)
        text = self._read_text(csv_input)
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        issues: list[DemandTrendImportIssue] = []
        if "timeframe" in context_input and not isinstance(context_input.get("timeframe"), Mapping):
            issues.append(DemandTrendImportIssue(1, "timeframe", "timeframe must be an object"))
        issues.extend(
            DemandTrendImportIssue(1, field, f"{field} does not match supplied context")
            for field in sorted(context_mismatch_fields)
        )
        base_context = context_input
        issues.extend(self._context_issues(raw_context if raw_context is not None else base_context))
        self._required_context_issues(
            issues,
            prospect_id=prospect_id,
            vertical_id=vertical_id,
            location_code=location_code,
        )
        if keyword_set is not None and location_code is not None and location_code != keyword_set.location_code:
            issues.append(DemandTrendImportIssue(1, "location_code", "trend location_code does not match keyword set context"))
        if keyword_set is not None and vertical_id and vertical_id != keyword_set.vertical_id:
            issues.append(DemandTrendImportIssue(1, "vertical_id", "trend vertical does not match keyword set context"))
        if keyword_set is not None and market and market.casefold().strip() != keyword_set.market.casefold().strip():
            issues.append(DemandTrendImportIssue(1, "market", "trend market does not match keyword set context"))
        if not self._safe_artifact_ref(artifact_ref or f"demand_trends/{digest}.csv"):
            issues.append(DemandTrendImportIssue(1, "artifact_ref", "artifact reference must be a relative safe path"))
        if _UNIQUE_PERSON_CLAIM_RE.search(text):
            issues.append(
                DemandTrendImportIssue(
                    1,
                    "csv",
                    "keyword observations cannot be represented as unique-person counts",
                )
            )
        if not text.strip():
            issues.append(DemandTrendImportIssue(1, "csv", "CSV is empty"))
            return self._preview(
                digest,
                normalized_source,
                0,
                [],
                issues,
                prospect_id,
                vertical_id,
                market,
                period_start,
                period_end,
                location_code,
                base_context,
                artifact_ref,
                [],
            )
        if "\x00" in text:
            issues.append(DemandTrendImportIssue(1, "csv", "CSV contains a NUL byte"))
            return self._preview(
                digest,
                normalized_source,
                0,
                [],
                issues,
                prospect_id,
                vertical_id,
                market,
                period_start,
                period_end,
                location_code,
                base_context,
                artifact_ref,
                [],
            )

        if normalized_source == "google_trends_csv":
            rows_seen, terms, groups, metadata = self._parse_google_trends(
                text,
                issues,
                keyword_set=keyword_set,
                brand_terms=brand_terms,
            )
            # Trends exports often include market and date range metadata.  It
            # is useful as a fallback, but explicit request context always wins.
            if not market:
                market = self._metadata_value(metadata, "market", "location", "geo", "country")
            if not period_start or not period_end:
                inferred_start, inferred_end = self._period_bounds_from_terms(terms)
                period_start = period_start or inferred_start
                period_end = period_end or inferred_end
            if not market:
                issues.append(DemandTrendImportIssue(1, "market", "market context is required"))
            if not period_start or not period_end:
                issues.append(DemandTrendImportIssue(1, "period", "period_start and period_end are required"))
            base_context.update(metadata)
        else:
            rows_seen, terms, groups = self._parse_planner_rows(
                text,
                issues,
                source=normalized_source,
                market=market,
                snapshot_period=self._snapshot_period(period_start, period_end),
                location_code=location_code,
                keyword_set=keyword_set,
                brand_terms=brand_terms,
                aggregation_rule=aggregation_rule,
                operator_approved=operator_approved,
            )
            inferred_market, inferred_period = self._planner_context(terms)
            if not market and inferred_market:
                market = inferred_market
            if not market and keyword_set is not None:
                market = str(keyword_set.market or "").strip()
            if (not period_start or not period_end) and inferred_period:
                period_start = period_start or inferred_period
                period_end = period_end or inferred_period
            if not market:
                issues.append(DemandTrendImportIssue(1, "market", "market context is required"))
            if not period_start or not period_end:
                issues.append(DemandTrendImportIssue(1, "period", "period_start and period_end are required"))
            for term in terms:
                term_market = str(term.get("market") or "").strip()
                if market and term_market not in {"", "unknown", market}:
                    issues.append(
                        DemandTrendImportIssue(
                            int(term.get("source_row") or 1),
                            "Market",
                            "row market does not match trend context",
                            value=term_market,
                        )
                    )
                term_period = str(term.get("snapshot_period") or "").strip()
                if period_start and period_end and period_start == period_end and term_period not in {"", "unspecified", period_start}:
                    issues.append(
                        DemandTrendImportIssue(
                            int(term.get("source_row") or 1),
                            "Snapshot Period",
                            "row snapshot period does not match trend timeframe",
                            value=term_period,
                        )
                    )

        if period_start and period_end and period_end < period_start:
            issues.append(DemandTrendImportIssue(1, "period", "period_end cannot precede period_start"))
        if aggregation_rule not in {"provider_grouped", "max_close_variant", "sum_distinct_intents"}:
            issues.append(DemandTrendImportIssue(1, "aggregation_rule", f"unsupported aggregation rule: {aggregation_rule}"))
        if aggregation_rule == "sum_distinct_intents" and not operator_approved:
            # Keep the rows visible but make the unsafe arithmetic gate clear.
            issues.append(
                DemandTrendImportIssue(
                    1,
                    "aggregation_rule",
                    "sum_distinct_intents requires explicit operator approval",
                    severity="warning",
                )
            )
        if operator_approved and not str(operator or "").strip():
            issues.append(DemandTrendImportIssue(1, "operator", "operator approval requires an operator identity"))
        for group in groups:
            group["reviewer"] = str(operator).strip() if operator_approved and str(operator or "").strip() else None

        provenance = "observed" if normalized_source == "google_trends_csv" else "supplied"
        semantics = (
            "relative interest index from Google Trends (0-100), directional only; not absolute volume"
            if normalized_source == "google_trends_csv"
            else "monthly search occasions from a supplied planner/operator estimate; close variants may overlap"
        )
        context_payload = self._build_context(
            base_context,
            digest=digest,
            source=normalized_source,
            prospect_id=prospect_id,
            vertical_id=vertical_id,
            market=market,
            period_start=period_start,
            period_end=period_end,
            location_code=location_code,
            metric_semantics=semantics,
            aggregation_rule=aggregation_rule,
            operator_approved=operator_approved,
            operator=operator,
            provenance=provenance,
        )
        context_payload["artifact_ref"] = artifact_ref or f"demand_trends/{digest}.csv"
        if keyword_set is not None:
            context_payload["keyword_set_id"] = keyword_set.id
            context_payload["keyword_set_source_sha256"] = keyword_set.source_sha256
        context_payload["intent_groups"] = [
            group.to_dict() if hasattr(group, "to_dict") else dict(group)
            for group in groups
        ]
        context_payload["context_sha256"] = self._context_hash(context_payload)
        return self._preview(
            digest,
            normalized_source,
            rows_seen,
            terms,
            issues,
            prospect_id,
            vertical_id,
            market,
            period_start,
            period_end,
            location_code,
            context_payload,
            artifact_ref,
            groups,
        )

    def commit(
        self,
        preview: DemandTrendPreview,
        *,
        prospect_id: str | None = None,
        vertical_id: str | None = None,
        market: str | None = None,
        period_start: str | None = None,
        period_end: str | None = None,
        location_code: int | None = None,
        source: str | None = None,
        artifact_ref: str | None = None,
        context: Mapping[str, Any] | None = None,
        operator_approved: bool | None = None,
        operator: str | None = None,
    ) -> DemandTrendSnapshot:
        """Build a model-valid snapshot; never save it to a repository."""
        if not preview.valid:
            raise ValueError("demand trend preview contains errors or no terms")
        values = {
            "prospect_id": prospect_id if prospect_id is not None else preview.prospect_id,
            "vertical_id": vertical_id if vertical_id is not None else preview.vertical_id,
            "market": market if market is not None else preview.market,
            "period_start": period_start if period_start is not None else preview.period_start,
            "period_end": period_end if period_end is not None else preview.period_end,
            "location_code": location_code if location_code is not None else preview.location_code,
            "source": source if source is not None else preview.source,
            "artifact_ref": artifact_ref if artifact_ref is not None else preview.artifact_ref,
        }
        for field in ("prospect_id", "vertical_id", "market", "period_start", "period_end"):
            supplied = locals()[field]
            original = getattr(preview, field)
            if supplied is not None and str(supplied).strip() != str(original).strip():
                raise ValueError(f"demand trend {field} cannot change between preview and commit")
        if location_code is not None and preview.location_code is not None and location_code != preview.location_code:
            raise ValueError("demand trend location_code cannot change between preview and commit")
        if any(not str(values[key] or "").strip() for key in ("prospect_id", "vertical_id", "market", "period_start", "period_end")):
            raise ValueError("demand trend commit requires prospect, vertical, market, and timeframe context")
        if values["period_end"] < values["period_start"]:
            raise ValueError("period_end cannot precede period_start")
        normalized_source = self._normalize_source(str(values["source"]))
        if normalized_source != preview.source:
            raise ValueError("demand trend source cannot change between preview and commit")
        if not self._safe_artifact_ref(str(values["artifact_ref"] or "")):
            raise ValueError("demand trend artifact reference must be a relative safe path")
        if context is not None:
            if not isinstance(context, Mapping):
                raise ValueError("demand trend context must be an object")
            supplied_context = dict(context)
            context_issues = self._context_issues(supplied_context)
            if context_issues:
                raise ValueError("demand trend context contains prohibited PII or credentials")
            for field in ("prospect_id", "vertical_id", "market"):
                if field in supplied_context and str(supplied_context[field]).strip() != str(values[field]).strip():
                    raise ValueError(f"demand trend context {field} does not match snapshot context")
            if "source" in supplied_context and self._normalize_source(str(supplied_context["source"])) != preview.source:
                raise ValueError("demand trend context source does not match snapshot context")
            if "source_sha256" in supplied_context and str(supplied_context["source_sha256"]).strip() != preview.source_sha256:
                raise ValueError("demand trend context source hash does not match snapshot context")
            if "context_sha256" in supplied_context and str(supplied_context["context_sha256"]).strip() != self._context_hash(supplied_context):
                raise ValueError("demand trend context hash is invalid")
            timeframe = supplied_context.get("timeframe")
            if isinstance(timeframe, Mapping):
                if "period_start" in timeframe and str(timeframe["period_start"]).strip() != str(values["period_start"]).strip():
                    raise ValueError("demand trend context period_start does not match snapshot context")
                if "period_end" in timeframe and str(timeframe["period_end"]).strip() != str(values["period_end"]).strip():
                    raise ValueError("demand trend context period_end does not match snapshot context")
        resolved_context = dict(preview.context or {})
        resolved_context.update(dict(context or {}))
        resolved_context["location_code"] = values["location_code"]
        resolved_context["artifact_ref"] = str(values["artifact_ref"]).strip()
        resolved_context["source"] = preview.source
        resolved_context["source_sha256"] = preview.source_sha256
        approved = bool(
            resolved_context.get("operator_approved")
            if operator_approved is None
            else operator_approved
        )
        approver = str(operator or resolved_context.get("operator") or "").strip() or None
        if resolved_context.get("aggregation_rule") == "sum_distinct_intents" and not approved:
            raise ValueError("sum_distinct_intents requires explicit operator approval before commit")
        if approved and not approver:
            raise ValueError("operator approval requires an operator identity")
        resolved_context["operator_approved"] = approved
        if approver:
            resolved_context["operator"] = approver
        resolved_context["aggregation_status"] = "approved" if approved else "requires_operator_review"
        # Preserve the preview source hash as the immutable source identity;
        # changing context creates a different context hash, not a new source.
        resolved_context["context_sha256"] = self._context_hash(resolved_context)
        state = "approved" if approved else "draft"
        approved_at = utc_now_iso() if approved else None
        snapshot_terms: list[dict[str, Any]] = []
        for original_term in preview.terms:
            term = dict(original_term)
            evidence_ref = dict(term.get("evidence_ref") or {})
            evidence_ref["artifact_ref"] = str(values["artifact_ref"]).strip()
            term["evidence_ref"] = evidence_ref
            snapshot_terms.append(term)
        return DemandTrendSnapshot(
            prospect_id=str(values["prospect_id"]).strip(),
            vertical_id=str(values["vertical_id"]).strip(),
            market=str(values["market"]).strip(),
            source=normalized_source,
            period_start=str(values["period_start"]).strip(),
            period_end=str(values["period_end"]).strip(),
            source_sha256=preview.source_sha256,
            terms=snapshot_terms,
            artifact_ref=str(values["artifact_ref"]).strip(),
            location_code=values["location_code"],
            context=resolved_context,
            state=state,
            approved_by=approver if approved else None,
            approved_at=approved_at,
        )

    def review(self, snapshot: DemandTrendSnapshot, *, reviewer: str) -> DemandTrendSnapshot:
        if snapshot.state not in {"draft", "review"}:
            raise ValueError("only draft or review demand trends may be reviewed")
        if not str(reviewer or "").strip():
            raise ValueError("demand trend review requires an operator")
        context = dict(snapshot.context)
        context["reviewer"] = str(reviewer).strip()
        context["context_sha256"] = self._context_hash(context)
        return replace(
            snapshot,
            id=self._new_id(),
            version=snapshot.version + 1,
            predecessor_id=snapshot.id,
            state="review",
            approved_by=None,
            approved_at=None,
            context=context,
        )

    review_snapshot = review
    correct = review
    review_terms = review

    def approve(self, snapshot: DemandTrendSnapshot, *, operator: str) -> DemandTrendSnapshot:
        if snapshot.state not in {"draft", "review"}:
            raise ValueError("only draft or review demand trends may be approved")
        if not str(operator or "").strip():
            raise ValueError("demand trend approval requires an operator")
        context = dict(snapshot.context)
        groups = [dict(group) for group in context.get("intent_groups", []) if isinstance(group, Mapping)]
        for group in groups:
            if group.get("aggregation_status") != "not_applicable_relative":
                group["status"] = "approved"
                group["aggregation_status"] = "approved"
            group["reviewer"] = str(operator).strip()
        if groups:
            context["intent_groups"] = groups
        context.update({"operator": str(operator).strip(), "operator_approved": True, "aggregation_status": "approved"})
        context["context_sha256"] = self._context_hash(context)
        return replace(
            snapshot,
            id=self._new_id(),
            version=snapshot.version + 1,
            predecessor_id=snapshot.id,
            state="approved",
            approved_by=str(operator).strip(),
            approved_at=utc_now_iso(),
            context=context,
        )

    approve_snapshot = approve

    def supersede(
        self,
        snapshot: DemandTrendSnapshot,
        *,
        successor: DemandTrendSnapshot | None = None,
        successor_id: str | None = None,
    ) -> DemandTrendSnapshot:
        if successor is None and successor_id and self.repository is not None:
            getter = getattr(self.repository, "get_demand_trend_snapshot", None)
            if callable(getter):
                successor = getter(successor_id)
        if successor is None:
            raise ValueError("a demand trend successor is required")
        if successor.predecessor_id != snapshot.id:
            raise ValueError("demand trend successor must reference its predecessor")
        if successor.id == snapshot.id or successor.version <= snapshot.version:
            raise ValueError("demand trend successor must have a new version")
        return successor

    # Import-service compatibility spellings.
    preview_import = preview_csv
    commit_preview = commit
    commit_import = commit
    parse_csv = preview_csv
    build_snapshot = commit

    def import_csv(self, csv_input: str | bytes | TextIO, **kwargs: Any) -> DemandTrendSnapshot:
        return self.commit(self.preview_csv(csv_input, **kwargs))

    def preview_google_trends_csv(self, csv_input: str | bytes | TextIO, **kwargs: Any) -> DemandTrendPreview:
        kwargs["source"] = "google_trends_csv"
        return self.preview_csv(csv_input, **kwargs)

    def preview_keyword_planner_csv(self, csv_input: str | bytes | TextIO, **kwargs: Any) -> DemandTrendPreview:
        kwargs["source"] = "keyword_planner_csv"
        return self.preview_csv(csv_input, **kwargs)

    preview_trends_csv = preview_google_trends_csv
    preview_planner_csv = preview_keyword_planner_csv

    def group_terms(
        self,
        terms: Iterable[Mapping[str, Any]],
        *,
        relative: bool = False,
        aggregation_rule: str = "max_close_variant",
        operator_approved: bool = False,
    ) -> list[DemandTrendGroup]:
        return self._term_groups(
            [dict(term) for term in terms],
            relative=relative,
            aggregation_rule=aggregation_rule,
            operator_approved=operator_approved,
        )

    cluster_terms = group_terms
    cluster_intent_families = group_terms

    def _parse_google_trends(
        self,
        text: str,
        issues: list[DemandTrendImportIssue],
        *,
        keyword_set: KeywordSet | None,
        brand_terms: Iterable[str],
    ) -> tuple[int, list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
        try:
            table = list(csv.reader(io.StringIO(text, newline="")))
        except csv.Error as exc:
            issues.append(DemandTrendImportIssue(1, "csv", f"invalid CSV: {exc}"))
            return 0, [], [], {}
        if not table:
            issues.append(DemandTrendImportIssue(1, "header", "CSV header is required"))
            return 0, [], [], {}
        for index, row in enumerate(table, start=1):
            if len(row) > MAX_TREND_CSV_COLUMNS:
                issues.append(DemandTrendImportIssue(index, "header", f"CSV exceeds {MAX_TREND_CSV_COLUMNS} columns"))
                break
            for cell in row:
                if _FORMULA_RE.match(str(cell or "").strip()):
                    issues.append(DemandTrendImportIssue(index, "csv_cell", "formula-like CSV cells are not accepted"))
                    break

        metadata: dict[str, Any] = {}
        header_index = self._find_trends_header(table)
        if header_index is None:
            # A row-per-term Trends file is accepted when a normal header is
            # present but no Week/Month column was emitted.
            header_index = self._find_term_header(table)
        if header_index is None:
            issues.append(DemandTrendImportIssue(1, "header", "Google Trends CSV header is required"))
            return len(table) - 1, [], [], metadata
        for row in table[:header_index]:
            if len(row) == 1 and ":" in row[0]:
                key, value = row[0].split(":", 1)
                metadata[self._header_norm(key)] = self._clean(value)
            elif len(row) >= 2 and str(row[0]).strip().endswith(":"):
                metadata[self._header_norm(row[0][:-1])] = self._clean(row[1])
        headers = [self._clean(value) for value in table[header_index]]
        if any(_PII_HEADER_RE.search(header) for header in headers):
            issues.append(DemandTrendImportIssue(header_index + 1, "header", "PII columns are not accepted"))
        if any(_SECRET_KEY_RE.search(header) for header in headers):
            issues.append(DemandTrendImportIssue(header_index + 1, "header", "credential columns are not accepted"))
        normalized_headers = [self._header_norm(header) for header in headers]
        date_column = 0
        if normalized_headers and normalized_headers[0] not in _DATE_HEADER_ALIASES:
            explicit_date = next((index for index, value in enumerate(normalized_headers) if value in _DATE_HEADER_ALIASES), None)
            if explicit_date is not None:
                date_column = explicit_date
        seen_term_headers: set[str] = set()
        for column, header in enumerate(normalized_headers):
            if column == date_column or header in {"", "is_partial", "ispartial", "partial"}:
                continue
            if header in seen_term_headers:
                issues.append(DemandTrendImportIssue(header_index + 1, headers[column], "duplicate trend term column"))
            seen_term_headers.add(header)
        relative_column = self._first_header_index(normalized_headers, {"relative_interest", "relative_index", "interest", "value", "search_interest"})
        keyword_column = self._first_header_index(normalized_headers, {"keyword", "search_term", "query", "term"})
        row_style = keyword_column is not None and relative_column is not None
        observations: dict[str, list[tuple[str, float]]] = {}
        rows_seen = 0
        for row_number, raw in enumerate(table[header_index + 1 :], start=header_index + 2):
            rows_seen += 1
            if rows_seen > MAX_TREND_CSV_ROWS:
                issues.append(DemandTrendImportIssue(row_number, "csv", f"CSV exceeds {MAX_TREND_CSV_ROWS} rows"))
                break
            values = [self._clean(value) for value in raw]
            if not any(values):
                continue
            period = values[date_column] if date_column < len(values) else ""
            if row_style:
                keyword = values[keyword_column] if keyword_column is not None and keyword_column < len(values) else ""
                raw_value = values[relative_column] if relative_column is not None and relative_column < len(values) else ""
                if not keyword:
                    issues.append(DemandTrendImportIssue(row_number, "Keyword", "keyword is required"))
                    continue
                parsed = self._parse_relative(raw_value)
                if parsed is None:
                    issues.append(DemandTrendImportIssue(row_number, headers[relative_column or 0], "relative interest must be a finite number from 0 to 100", value=raw_value))
                    continue
                observations.setdefault(keyword, []).append((period or str(rows_seen), parsed))
                continue
            for column, keyword in enumerate(headers):
                if column == date_column or not keyword or self._header_norm(keyword) in {"is_partial", "ispartial", "partial"}:
                    continue
                raw_value = values[column] if column < len(values) else ""
                if not raw_value:
                    continue
                parsed = self._parse_relative(raw_value)
                if parsed is None:
                    issues.append(DemandTrendImportIssue(row_number, keyword, "relative interest must be a finite number from 0 to 100", value=raw_value))
                    continue
                observations.setdefault(keyword, []).append((period or str(rows_seen), parsed))
        terms = self._trend_terms(observations, keyword_set=keyword_set, brand_terms=brand_terms)
        if keyword_set is not None:
            for term in terms:
                if term.get("review_status") == "needs_review" and "not_in_keyword_set" in term.get("review_reasons", []):
                    issues.append(
                        DemandTrendImportIssue(
                            1,
                            "Keyword",
                            "keyword is not present in the bound keyword set; retained for review",
                            severity="warning",
                            value=term.get("keyword"),
                        )
                    )
        groups = self._term_groups(terms, relative=True)
        return rows_seen, terms, groups, metadata

    def _parse_planner_rows(
        self,
        text: str,
        issues: list[DemandTrendImportIssue],
        *,
        source: str,
        market: str,
        snapshot_period: str,
        location_code: int | None,
        keyword_set: KeywordSet | None,
        brand_terms: Iterable[str],
        aggregation_rule: str,
        operator_approved: bool,
    ) -> tuple[int, list[dict[str, Any]], list[dict[str, Any]]]:
        # DemandEvidenceService intentionally rejects ``sum_distinct_intents``
        # at preview time.  Trend previews still need to expose those rows so
        # an operator can explicitly approve the rule; parse with the safe
        # max-close-variant rule and retain the requested rule in the trend
        # group/context metadata.
        parser_aggregation_rule = (
            "max_close_variant" if aggregation_rule == "sum_distinct_intents" else aggregation_rule
        )
        try:
            first_row = next(csv.reader(io.StringIO(text, newline="")), [])
            if any(_FORMULA_RE.match(self._clean(header)) for header in first_row):
                issues.append(DemandTrendImportIssue(1, "header", "formula-like CSV headers are not accepted"))
            if any(_PII_HEADER_RE.search(self._clean(header)) for header in first_row):
                issues.append(DemandTrendImportIssue(1, "header", "PII columns are not accepted"))
            if any(_SECRET_KEY_RE.search(self._clean(header)) for header in first_row):
                issues.append(DemandTrendImportIssue(1, "header", "credential columns are not accepted"))
            preview = self._demand_service.preview_csv(
                text,
                market=market,
                source=source,
                snapshot_period=snapshot_period,
                location_code=location_code,
                keyword_set=keyword_set,
                brand_terms=tuple(brand_terms),
                aggregation_rule=parser_aggregation_rule,
            )
        except (TypeError, ValueError) as exc:
            issues.append(DemandTrendImportIssue(1, "csv", str(exc)))
            return 0, [], []
        for issue in preview.issues:
            issues.append(DemandTrendImportIssue(issue.row_number, issue.field, issue.message, issue.severity, issue.value))
        terms: list[dict[str, Any]] = []
        for row in preview.demand_rows:
            ref = dict(row.evidence_ref or {})
            family = str(ref.get("intent_family") or self._family_for_keyword(row.keyword, keyword_set=keyword_set, brand=row.brand_demand))
            signature = str(ref.get("close_variant_signature") or DemandEvidenceService.close_variant_signature(row.keyword))
            target = self._target_for_keyword(keyword_set, row.normalized_keyword)
            review_status = target.review_status if target is not None else "approved"
            term_id = self._term_id(preview.source_sha256 if hasattr(preview, "source_sha256") else "", row.keyword, family)
            terms.append(
                {
                    "term_id": term_id,
                    "keyword": row.keyword,
                    "normalized_keyword": row.normalized_keyword,
                    "intent_family": family,
                    "close_variant_signature": signature,
                    "provenance_label": "supplied",
                    "source_class": "approved_market",
                    "review_status": review_status,
                    "review_reasons": list(target.review_reasons) if target is not None else [],
                    "supported": bool(row.supported),
                    "brand_demand": bool(row.brand_demand),
                    "metrics": {
                        "monthly_searches": float(row.monthly_searches or 0),
                        "monthly_search_occasions": float(row.monthly_searches or 0),
                    },
                    "semantics": "monthly search occasions; planner close variants are not de-duplicated people",
                    "source_row": row.source_row,
                    "snapshot_period": row.snapshot_period,
                    "market": row.market,
                }
            )
        # Recompute deterministic term IDs from the actual source hash later in
        # ``_preview``; the local value is replaced there.
        for term in terms:
            term["term_id"] = self._term_id("", str(term["keyword"]), str(term["intent_family"]))
        groups = self._term_groups(
            terms,
            relative=False,
            aggregation_rule=aggregation_rule,
            operator_approved=operator_approved,
        )
        return preview.rows_seen, terms, groups

    def _trend_terms(
        self,
        observations: Mapping[str, list[tuple[str, float]]],
        *,
        keyword_set: KeywordSet | None,
        brand_terms: Iterable[str],
    ) -> list[dict[str, Any]]:
        terms: list[dict[str, Any]] = []
        for keyword in sorted(observations, key=lambda value: (DemandEvidenceService.normalize_keyword(value), value)):
            samples = sorted(observations[keyword], key=lambda item: (str(item[0]), float(item[1])))
            values = [float(value) for _, value in samples]
            mean = sum(values) / len(values)
            first_period, first = samples[0]
            last_period, last = samples[-1]
            minimum = min(values)
            maximum = max(values)
            slope = (last - first) / max(1, len(values) - 1)
            direction = "rising" if slope > 1 else "falling" if slope < -1 else "stable"
            target = self._target_for_keyword(keyword_set, DemandEvidenceService.normalize_keyword(keyword))
            category = target.category if target is not None else "Uncategorized"
            intent = target.search_intent if target is not None else "unknown"
            target_page = target.target_page_usage if target is not None else "unknown"
            brand = self._is_brand(keyword, category, intent, brand_terms, target)
            family = DemandEvidenceService.intent_family_key(
                category=category,
                search_intent=intent,
                target_page=target_page,
                brand=brand,
            )
            review_status = target.review_status if target is not None else ("needs_review" if keyword_set is not None else "approved")
            review_reasons = list(target.review_reasons) if target is not None else (["not_in_keyword_set"] if keyword_set is not None else [])
            terms.append(
                {
                    "keyword": keyword,
                    "normalized_keyword": DemandEvidenceService.normalize_keyword(keyword),
                    "intent_family": family,
                    "close_variant_signature": DemandEvidenceService.close_variant_signature(keyword),
                    "provenance_label": "observed",
                    "source_class": "approved_market",
                    "review_status": review_status,
                    "review_reasons": review_reasons,
                    "supported": review_status == "approved",
                    "brand_demand": brand,
                    "metrics": {
                        "relative_interest": round(mean, 6),
                        "relative_interest_min": round(minimum, 6),
                        "relative_interest_max": round(maximum, 6),
                        "relative_interest_first": round(first, 6),
                        "relative_interest_last": round(last, 6),
                        "observations": len(values),
                        "trend_slope_abs": round(abs(slope), 6),
                        "seasonality_amplitude": round(maximum - minimum, 6),
                        "seasonality_index": round((maximum - minimum) / mean, 6) if mean else 0.0,
                    },
                    "relative_semantics": "relative interest index from Google Trends, scaled 0-100; directional only",
                    "trend_direction": direction,
                    "trend": direction,
                    "seasonality": {
                        "peak_period": max(samples, key=lambda item: (item[1], item[0]))[0],
                        "trough_period": min(samples, key=lambda item: (item[1], item[0]))[0],
                        "sample_period_start": first_period,
                        "sample_period_end": last_period,
                    },
                    "source_observations": [
                        {"period": period, "relative_interest": value} for period, value in samples
                    ],
                }
            )
        return terms

    def _term_groups(
        self,
        terms: list[dict[str, Any]],
        *,
        relative: bool,
        aggregation_rule: str = "max_close_variant",
        operator_approved: bool = False,
    ) -> list[dict[str, Any]]:
        buckets: dict[tuple[str, bool, str], list[dict[str, Any]]] = {}
        for term in terms:
            if not term.get("supported", True):
                continue
            key = (
                str(term.get("intent_family") or "unknown"),
                bool(term.get("brand_demand")),
                str(term.get("close_variant_signature") or ""),
            )
            buckets.setdefault(key, []).append(term)
        groups: list[dict[str, Any]] = []
        for (family, is_brand, signature), members in sorted(buckets.items()):
            ordered = sorted(
                members,
                key=lambda term: (
                    -float(term.get("metrics", {}).get("relative_interest" if relative else "monthly_searches", 0) or 0),
                    str(term.get("normalized_keyword") or term.get("keyword") or ""),
                ),
            )
            representative = ordered[0]
            stable_group_id = "trend-group-" + hashlib.sha256(
                "|".join(
                    (
                        family,
                        signature,
                        ",".join(str(term.get("normalized_keyword") or term.get("keyword") or "") for term in ordered),
                    )
                ).encode("utf-8")
            ).hexdigest()[:24]
            groups.append(
                DemandTrendGroup(
                    {
                    "id": stable_group_id,
                    "group_id": stable_group_id,
                    "intent_family": family,
                    "close_variant_signature": signature,
                    # Keep keywords until ``_preview`` assigns source-hash
                    # based term IDs; this makes group references stable and
                    # avoids carrying provisional IDs.
                    "included_terms": [str(term.get("keyword")) for term in ordered[:1]],
                    "excluded_duplicate_terms": [str(term.get("keyword")) for term in ordered[1:]],
                    "representative_term": representative.get("keyword"),
                    "is_brand": is_brand,
                    "aggregation_rule": "relative_index_summary" if relative else aggregation_rule,
                    "aggregation_status": (
                        "not_applicable_relative"
                        if relative
                        else "approved" if operator_approved else "requires_operator_review"
                    ),
                    "status": "approved" if (operator_approved and not relative) else "draft",
                    "approved_monthly_search_occasions": (
                        None
                        if relative
                        else (
                            sum(float(term.get("metrics", {}).get("monthly_searches", 0) or 0) for term in ordered)
                            if aggregation_rule == "sum_distinct_intents" and operator_approved
                            else max(float(term.get("metrics", {}).get("monthly_searches", 0) or 0) for term in ordered)
                        )
                    ),
                    "claim_limit": "directional market evidence; not a people count",
                    "rationale": "deterministic intent-family and close-variant clustering",
                    }
                )
            )
        return groups

    @staticmethod
    def _preview(
        digest: str,
        source: str,
        rows_seen: int,
        terms: list[dict[str, Any]],
        issues: list[DemandTrendImportIssue],
        prospect_id: str,
        vertical_id: str,
        market: str,
        period_start: str,
        period_end: str,
        location_code: int | None,
        context: Mapping[str, Any],
        artifact_ref: str | None,
        groups: list[dict[str, Any]],
    ) -> DemandTrendPreview:
        resolved_artifact = artifact_ref or f"demand_trends/{digest}.csv"
        terms.sort(key=lambda term: (str(term.get("normalized_keyword") or term.get("keyword") or ""), str(term.get("keyword") or "")))
        for term in terms:
            term["source_sha256"] = digest
            term["evidence_ref"] = {
                "source_sha256": digest,
                "artifact_ref": resolved_artifact,
                "source_row": term.get("source_row"),
            }
            term["term_id"] = DemandTrendService._term_id(digest, str(term.get("keyword") or ""), str(term.get("intent_family") or ""))
        # Rewrite group references after deterministic term IDs are known.
        by_keyword = {str(term.get("keyword")): str(term.get("term_id")) for term in terms}
        for group in groups:
            for key in ("included_terms", "excluded_duplicate_terms"):
                group[key] = [by_keyword.get(value, value) for value in group.get(key, [])]
            group["included_keyword_ids"] = list(group.get("included_terms", []))
            group["excluded_duplicate_ids"] = list(group.get("excluded_duplicate_terms", []))
        return DemandTrendPreview(
            source_sha256=digest,
            source=source,
            rows_seen=rows_seen,
            terms=terms,
            issues=issues,
            prospect_id=str(prospect_id or "").strip(),
            vertical_id=str(vertical_id or "").strip(),
            market=str(market or "").strip(),
            period_start=str(period_start or "").strip(),
            period_end=str(period_end or "").strip(),
            location_code=location_code,
            context=dict(context),
            artifact_ref=resolved_artifact,
            groups=groups,
        )

    @staticmethod
    def _target_for_keyword(keyword_set: KeywordSet | None, normalized_keyword: str) -> Any | None:
        if keyword_set is None:
            return None
        target_map = {target.normalized_keyword: target for target in keyword_set.targets()}
        return target_map.get(DemandEvidenceService.normalize_keyword(normalized_keyword))

    def _family_for_keyword(self, keyword: str, *, keyword_set: KeywordSet | None, brand: bool) -> str:
        target = self._target_for_keyword(keyword_set, DemandEvidenceService.normalize_keyword(keyword))
        return DemandEvidenceService.intent_family_key(
            category=target.category if target is not None else "Uncategorized",
            search_intent=target.search_intent if target is not None else "unknown",
            target_page=target.target_page_usage if target is not None else "unknown",
            brand=brand,
        )

    @staticmethod
    def _is_brand(keyword: str, category: str, intent: str, brand_terms: Iterable[str], target: Any | None) -> bool:
        if target is not None and str(target.category).casefold() in {"brand", "lineage & authority"}:
            return True
        normalized = DemandEvidenceService.normalize_keyword(keyword)
        known = {DemandEvidenceService.normalize_keyword(value) for value in brand_terms if str(value).strip()}
        text = f"{keyword} {category} {intent}".casefold()
        return normalized in known or bool(re.search(r"\b(brand|lineage|authority)\b", text))

    @staticmethod
    def _planner_context(terms: list[dict[str, Any]]) -> tuple[str, str]:
        markets = sorted({str(term.get("market")) for term in terms if str(term.get("market")) not in {"", "unknown"}})
        periods = sorted({str(term.get("snapshot_period")) for term in terms if str(term.get("snapshot_period")) not in {"", "unspecified"}})
        return (markets[0] if len(markets) == 1 else "", periods[0] if len(periods) == 1 else "")

    @staticmethod
    def _period_bounds_from_terms(terms: list[dict[str, Any]]) -> tuple[str, str]:
        periods: list[str] = []
        for term in terms:
            for item in term.get("source_observations", []):
                value = str(item.get("period") or "").strip()
                if value:
                    periods.append(value)
            value = str(term.get("snapshot_period") or "").strip()
            if value and value not in {"unspecified", "unknown"}:
                periods.append(value)
        return (min(periods), max(periods)) if periods else ("", "")

    @staticmethod
    def _metadata_value(metadata: Mapping[str, Any], *keys: str) -> str:
        normalized = {re.sub(r"[^a-z0-9]+", "_", str(key).casefold()).strip("_"): value for key, value in metadata.items()}
        for key in keys:
            value = str(normalized.get(key, "") or "").strip()
            if value:
                return value
        return ""

    @classmethod
    def _find_trends_header(cls, table: list[list[str]]) -> int | None:
        for index, row in enumerate(table):
            if not row:
                continue
            first = cls._header_norm(row[0])
            if first in _DATE_HEADER_ALIASES and len(row) >= 2:
                return index
        return None

    @classmethod
    def _find_term_header(cls, table: list[list[str]]) -> int | None:
        for index, row in enumerate(table):
            normalized = {cls._header_norm(value) for value in row}
            if normalized & {"keyword", "search_term", "query", "term"} and normalized & {"relative_interest", "relative_index", "interest", "value", "search_interest"}:
                return index
        return None

    @staticmethod
    def _first_header_index(headers: list[str], candidates: set[str]) -> int | None:
        return next((index for index, header in enumerate(headers) if header in candidates), None)

    @staticmethod
    def _header_norm(value: Any) -> str:
        return re.sub(r"[^a-z0-9]+", "_", str(value or "").casefold()).strip("_")

    @staticmethod
    def _clean(value: Any) -> str:
        return " ".join(str(value or "").replace("\ufeff", "").split())

    @classmethod
    def _parse_relative(cls, value: str) -> float | None:
        cleaned = cls._clean(value).replace(",", "")
        if not cleaned:
            return None
        if cleaned.casefold() in {"<1", "less than 1"}:
            return 0.0
        if _FORMULA_RE.match(cleaned):
            return None
        try:
            number = float(cleaned)
        except ValueError:
            return None
        if not math.isfinite(number) or number < 0 or number > 100:
            return None
        return number

    @staticmethod
    def _snapshot_period(period_start: str, period_end: str) -> str:
        if period_start and period_end and period_start == period_end:
            return period_start
        return period_start or period_end or ""

    @classmethod
    def _normalize_source(cls, source: str) -> str:
        normalized = str(source or "").casefold().strip().replace("-", "_").replace(" ", "_")
        normalized = SOURCE_ALIASES.get(normalized, normalized)
        if normalized not in SUPPORTED_SOURCES:
            raise ValueError(f"unsupported demand trend source: {source}")
        return normalized

    @classmethod
    def _read_text(cls, csv_input: str | bytes | TextIO) -> str:
        if isinstance(csv_input, Path):
            raise ValueError("CSV paths are not accepted; upload CSV content")
        if isinstance(csv_input, bytes):
            if len(csv_input) > MAX_TREND_CSV_BYTES:
                raise ValueError(f"CSV exceeds {MAX_TREND_CSV_BYTES} bytes")
            try:
                text = csv_input.decode("utf-8-sig")
            except UnicodeDecodeError as exc:
                raise ValueError("CSV must be UTF-8") from exc
        elif isinstance(csv_input, str):
            if "\n" not in csv_input and "\r" not in csv_input and ("/" in csv_input or "\\" in csv_input):
                raise ValueError("CSV paths are not accepted; upload CSV content")
            text = csv_input.lstrip("\ufeff")
        else:
            text = csv_input.read().lstrip("\ufeff")
        if len(text.encode("utf-8")) > MAX_TREND_CSV_BYTES:
            raise ValueError(f"CSV exceeds {MAX_TREND_CSV_BYTES} bytes")
        return text

    @classmethod
    def _context_issues(cls, context: Mapping[str, Any]) -> list[DemandTrendImportIssue]:
        issues: list[DemandTrendImportIssue] = []
        if not isinstance(context, Mapping):
            return [DemandTrendImportIssue(1, "context", "context must be an object")]
        if _UNIQUE_PERSON_CLAIM_RE.search(json.dumps(dict(context), default=str)):
            issues.append(
                DemandTrendImportIssue(
                    1,
                    "context",
                    "keyword observations cannot be represented as unique-person counts",
                )
            )

        def inspect(payload: Mapping[str, Any], prefix: str = "") -> None:
            for key, value in payload.items():
                field = f"{prefix}.{key}" if prefix else str(key)
                normalized = str(key).casefold().replace("-", "_")
                if _PII_HEADER_RE.search(normalized):
                    issues.append(DemandTrendImportIssue(1, field, "PII context fields are not accepted"))
                elif _SECRET_KEY_RE.search(normalized):
                    issues.append(DemandTrendImportIssue(1, field, "credential context fields are not accepted"))
                if isinstance(value, Mapping):
                    inspect(value, field)
                elif isinstance(value, list):
                    for index, item in enumerate(value):
                        if isinstance(item, Mapping):
                            inspect(item, f"{field}[{index}]")
                elif isinstance(value, (bytes, bytearray)):
                    issues.append(DemandTrendImportIssue(1, field, "binary credential values are not accepted"))

        inspect(context)
        return issues

    @staticmethod
    def _required_context_issues(
        issues: list[DemandTrendImportIssue],
        *,
        prospect_id: str,
        vertical_id: str,
        location_code: int | None,
    ) -> None:
        for field, value in (("prospect_id", prospect_id), ("vertical_id", vertical_id)):
            if not str(value or "").strip():
                issues.append(DemandTrendImportIssue(1, field, f"{field} is required"))
        if location_code is not None and (not isinstance(location_code, int) or location_code <= 0):
            issues.append(DemandTrendImportIssue(1, "location_code", "location_code must be a positive integer"))

    @staticmethod
    def _build_context(
        context: Mapping[str, Any],
        *,
        digest: str,
        source: str,
        prospect_id: str,
        vertical_id: str,
        market: str,
        period_start: str,
        period_end: str,
        location_code: int | None,
        metric_semantics: str,
        aggregation_rule: str,
        operator_approved: bool,
        operator: str | None,
        provenance: str,
    ) -> dict[str, Any]:
        payload = dict(context)
        payload.update(
            {
                "prospect_id": str(prospect_id or "").strip(),
                "vertical_id": str(vertical_id or "").strip(),
                "market": str(market or "").strip(),
                "location_code": location_code,
                "source": source,
                "source_sha256": digest,
                "source_hash": digest,
                "timeframe": {"period_start": str(period_start or "").strip(), "period_end": str(period_end or "").strip()},
                "metric_semantics": metric_semantics,
                "provenance_label": provenance,
                "source_class": "approved_market",
                "aggregation_rule": aggregation_rule,
                "aggregation_status": "approved" if operator_approved else "requires_operator_review",
                "operator_approved": bool(operator_approved),
            }
        )
        if str(operator or "").strip():
            payload["operator"] = str(operator).strip()
        payload["context_sha256"] = DemandTrendService._context_hash(payload)
        return payload

    @staticmethod
    def _context_hash(context: Mapping[str, Any]) -> str:
        clean = {key: value for key, value in context.items() if key != "context_sha256"}
        return canonical_sha256(clean)

    @staticmethod
    def _safe_artifact_ref(value: str) -> bool:
        candidate = str(value or "").strip().replace("\\", "/")
        if not candidate or candidate.startswith("/") or re.match(r"^[a-zA-Z]:", candidate):
            return False
        if any(part in {"", ".", ".."} for part in candidate.split("/")):
            return False
        return not any(ord(char) < 32 for char in candidate)

    @staticmethod
    def _term_id(source_hash: str, keyword: str, family: str) -> str:
        return "term-" + hashlib.sha256(
            f"{source_hash}|{DemandEvidenceService.normalize_keyword(keyword)}|{family}".encode("utf-8")
        ).hexdigest()[:24]

    @staticmethod
    def _new_id() -> str:
        from uuid import uuid4

        return str(uuid4())


# Compatibility spelling used by operator/import integrations.
DemandTrendImportService = DemandTrendService
DemandTrendIssue = DemandTrendImportIssue
TrendImportIssue = DemandTrendImportIssue
DemandTrendPreviewIssue = DemandTrendImportIssue
TrendImportPreview = DemandTrendPreview
DemandTrendImportPreview = DemandTrendPreview
TrendGroup = DemandTrendGroup
MAX_CSV_BYTES = MAX_TREND_CSV_BYTES
MAX_CSV_ROWS = MAX_TREND_CSV_ROWS
MAX_CSV_COLUMNS = MAX_TREND_CSV_COLUMNS
