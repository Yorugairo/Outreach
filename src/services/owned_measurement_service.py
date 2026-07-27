"""Owner-authorized, aggregate-only measurement intake.

CSV is the required baseline path.  This module deliberately keeps live
connectors behind a disabled-by-default, read-only adapter boundary: connector
implementations return aggregate rows and never receive or return credentials.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Protocol, TextIO

from src.models import AcquisitionCalibrationRecord, OwnedMeasurementSnapshot, new_id
from src.repositories.base import InsightRepository
from src.services.calibration_service import CalibrationService


MAX_OWNED_MEASUREMENT_BYTES = 2 * 1024 * 1024
MAX_OWNED_MEASUREMENT_ROWS = 500
MAX_OWNED_MEASUREMENT_COLUMNS = 60
_FORMULA_RE = re.compile(r"^[=+\-@]")
_PII_HEADER_RE = re.compile(
    r"(?:email|e[-_ ]?mail|phone|mobile|first[-_ ]?name|last[-_ ]?name|full[-_ ]?name|"
    r"(?:^|[_\s-])name(?:$|[_\s-])|contact|address|customer[-_ ]+(?:id|name|email)|lead[-_ ]+id|user[-_ ]+id|person)",
    re.IGNORECASE,
)
_PII_VALUE_RE = re.compile(
    r"(?:\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b|"
    r"(?<!\d)(?:\+?1[\s().-]?)?(?:\d[\s().-]?){10,}(?!\d))",
    re.IGNORECASE,
)
_SECRET_VALUE_RE = re.compile(
    r"(?:api[_-]?key|authorization|cookie|credential|oauth|password|refresh[_-]?token|"
    r"access[_-]?token|bearer|token|secret)\s*=",
    re.IGNORECASE,
)
_SECRET_KEY_RE = re.compile(
    r"(?:api[_-]?key|authorization|cookie|credential|oauth|password|refresh[_-]?token|"
    r"access[_-]?token|bearer|token|secret)",
    re.IGNORECASE,
)

SUPPORTED_SOURCES = {"gsc_csv", "gbp_csv", "ga4_csv", "crm_csv", "ai_performance_csv"}
SOURCE_ALIASES = {
    "gsc": "gsc_csv", "search_console": "gsc_csv", "search_console_csv": "gsc_csv",
    "google_search_console": "gsc_csv", "google_search_console_performance": "gsc_csv",
    "gsc_export": "gsc_csv", "gsc_query": "gsc_csv", "gsc_query_csv": "gsc_csv",
    "gbp": "gbp_csv", "google_business_profile": "gbp_csv", "gbp_performance": "gbp_csv",
    "gbp_performance_csv": "gbp_csv", "google_business_profile_csv": "gbp_csv",
    "google_business_profile_performance": "gbp_csv",
    "ga4": "ga4_csv", "analytics": "ga4_csv", "google_analytics": "ga4_csv",
    "ga4_events": "ga4_csv", "ga4_events_csv": "ga4_csv", "ga4_aggregate": "ga4_csv",
    "ga4_aggregate_csv": "ga4_csv", "google_analytics_csv": "ga4_csv",
    "crm": "crm_csv", "crm_outcomes": "crm_csv", "crm_outcomes_csv": "crm_csv",
    "crm_aggregate": "crm_csv", "crm_aggregate_csv": "crm_csv",
    "booking": "crm_csv", "booking_csv": "crm_csv", "bookings": "crm_csv", "bookings_csv": "crm_csv",
    "ai_performance": "ai_performance_csv", "ai": "ai_performance_csv",
}

_METRIC_ALIASES: dict[str, set[str]] = {
    "impressions": {"impressions", "impression", "views", "search_impressions"},
    "clicks": {"clicks", "click", "website_clicks", "link_clicks"},
    "sessions": {"sessions", "session", "visits", "website_visits"},
    "users": {"users", "user", "total_users", "unique_users", "active_users"},
    "signups": {"signups", "signup", "registrations", "conversions", "leads", "lead_count", "qualified_leads"},
    "appointments": {"appointments", "appointment", "attended_trials", "trials", "meetings", "bookings", "booking_count"},
    "customers": {"customers", "customer_count", "new_customers", "members", "won_jobs", "won_customers"},
    "spend": {"spend", "cost", "ad_spend", "advertising_spend"},
    "revenue": {
        "revenue", "purchase_revenue", "purchaserevenue", "sales", "total_revenue", "totalrevenue",
        "booking_revenue", "bookingrevenue",
    },
    "ctr": {"ctr", "click_through_rate"},
    "position": {"position", "average_position", "averageposition", "avg_position", "rank"},
    # Source-specific aggregate measures remain in ``metrics`` even when a
    # funnel baseline does not use them directly.
    "event_count": {"event_count", "eventcount", "events", "event_total", "eventtotal", "count"},
    "key_events": {"key_events", "keyevents", "key_event_count", "keyeventcount", "conversions_count"},
    "event_value": {"event_value", "eventvalue", "conversion_value", "conversionvalue"},
    "calls": {"calls", "call_clicks", "phone_calls"},
    "direction_requests": {
        "direction_requests", "directionrequests", "directions", "directions_requests", "directionsrequests",
    },
    "messages": {"messages", "message_actions", "message_clicks"},
    "profile_views": {"profile_views", "business_profile_views"},
    "photo_views": {"photo_views", "photos_views"},
    "food_orders": {"food_orders", "food_order_actions"},
}
_PERIOD_ALIASES = {
    "period_start": {"period_start", "start_date", "date_start", "from", "date"},
    "period_end": {"period_end", "end_date", "date_end", "to"},
}
# These are dimensions, identifiers, and export metadata—not metric columns.
# They are deliberately aggregate-safe: query/page/event labels are allowed,
# while raw identity fields (email, phone, names, booking records) are not.
_CONTEXT_HEADERS = {
    "market", "location", "country", "device", "search_type", "property", "property_id",
    "site_url", "location_id", "profile_id", "provider", "prompt_set", "channel", "pipeline",
    "workspace", "source", "prospect_id", "vertical_id", "target_id", "normalized_domain",
    "query", "search_query", "search_term", "page", "page_url", "landing_page", "landing_page_url",
    "event", "event_name", "event_names", "funnel_stage", "event_stage", "conversion_event",
    "action", "action_type", "service_type", "listing_type", "stage", "outcome", "pipeline_stage",
    "lead_source", "category", "metric", "dimension", "url", "location_name", "property_name",
    "currency", "timezone", "language", "lead_status", "booking_status", "customer_status", "page_type",
    "event_map_id", "event_map_version",
    "snapshot_date", "retrieval_date", "retrieved_at", "exported_at", "as_of", "data_date",
    "freshness_date", "data_updated_at", "last_updated", "source_snapshot_date", "freshness_status",
    "freshness_age_days", "data_age_days", "source_sha256",
}
_FRESHNESS_HEADERS = {
    "snapshot_date", "retrieval_date", "retrieved_at", "exported_at", "as_of", "data_date",
    "freshness_date", "data_updated_at", "last_updated", "source_snapshot_date", "freshness_status",
    "freshness_age_days", "data_age_days",
}
_BOUND_CONTEXT_HEADERS = {
    "market", "location", "country", "device", "search_type", "property", "property_id",
    "site_url", "location_id", "profile_id", "provider", "prompt_set", "channel", "pipeline",
    "workspace", "prospect_id", "vertical_id", "target_id", "normalized_domain",
}
_SINGLE_SCOPE_DIMENSIONS = {
    "market", "location", "country", "property", "property_id", "site_url", "location_id", "profile_id",
    "prospect_id", "vertical_id", "target_id", "normalized_domain",
}
_ROW_CONTEXT_DIMENSIONS = {
    "query", "search_query", "search_term", "page", "page_url", "landing_page", "landing_page_url",
    "event", "event_name", "event_names", "funnel_stage", "event_stage", "conversion_event",
    "action", "action_type", "service_type", "listing_type", "stage", "outcome", "pipeline_stage",
    "lead_source", "category", "metric", "dimension", "url", "location_name", "property_name",
    "currency", "timezone", "language", "lead_status", "booking_status", "customer_status", "page_type",
}
_PII_SENSITIVE_DIMENSIONS = {"query", "search_query", "search_term", "page_url", "landing_page_url", "url"}
_VOLATILE_CONTEXT_DIMENSIONS = {
    "provenance", "source_sha256", "source_row", "data_freshness", "owner_consent", "owner_verified",
    "event_map_id", "event_map_version", "source", "provider",
}


class OwnedMeasurementConnector(Protocol):
    """Read-only connector shape; no credential or mutation methods exist."""

    source: str

    def read_aggregate(
        self,
        *,
        prospect_id: str,
        period_start: str,
        period_end: str,
        context: Mapping[str, Any],
    ) -> Iterable[Mapping[str, Any]]: ...


ReadOnlyOwnedMeasurementConnector = OwnedMeasurementConnector


class ConnectorDisabledError(PermissionError):
    pass


class ConnectorApprovalError(PermissionError):
    pass


@dataclass(slots=True)
class OwnedMeasurementIssue:
    row_number: int
    field: str
    message: str
    value: Any = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class OwnedMeasurementPreview:
    source_sha256: str
    source: str
    rows_seen: int
    snapshots: list[OwnedMeasurementSnapshot]
    issues: list[OwnedMeasurementIssue]

    @property
    def records(self) -> list[OwnedMeasurementSnapshot]:
        return self.snapshots

    @property
    def valid(self) -> bool:
        return bool(self.snapshots) and not self.issues

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_sha256": self.source_sha256,
            "source": self.source,
            "rows_seen": self.rows_seen,
            "snapshots": [snapshot.to_dict() for snapshot in self.snapshots],
            "records": [snapshot.to_dict() for snapshot in self.snapshots],
            "issues": [issue.to_dict() for issue in self.issues],
            "valid": self.valid,
        }


class OwnedMeasurementService:
    """Validate, persist, aggregate, and calibrate owner measurements."""

    def __init__(
        self,
        repository: InsightRepository | None = None,
        *,
        connectors_enabled: bool = False,
        connectors: Mapping[str, OwnedMeasurementConnector] | None = None,
    ) -> None:
        self.repository = repository
        self.connectors_enabled = connectors_enabled
        self._connectors = dict(connectors or {})

    def preview_csv(
        self,
        csv_input: str | bytes | TextIO,
        *,
        prospect_id: str,
        vertical_id: str,
        source: str,
        context: Mapping[str, Any] | None = None,
        artifact_ref: str | None = None,
        period_start: str | None = None,
        period_end: str | None = None,
        owner_verified: bool = False,
        require_owner_consent: bool = False,
        owner_consent: Mapping[str, Any] | None = None,
        data_freshness: Mapping[str, Any] | None = None,
        event_map_id: str | None = None,
        event_map_version: str | None = None,
    ) -> OwnedMeasurementPreview:
        normalized_source = self._normalize_source(source)
        text = self._read_text(csv_input)
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        issues: list[OwnedMeasurementIssue] = []
        snapshots: list[OwnedMeasurementSnapshot] = []
        if context is not None and not isinstance(context, Mapping):
            issues.append(OwnedMeasurementIssue(1, "context", "measurement context must be an object"))
            base_context: dict[str, Any] = {}
        else:
            base_context = dict(context or {})
        if owner_consent is not None:
            if "owner_consent" in base_context and base_context["owner_consent"] != owner_consent:
                issues.append(OwnedMeasurementIssue(1, "owner_consent", "owner consent metadata does not match supplied context"))
            base_context["owner_consent"] = (
                dict(owner_consent) if isinstance(owner_consent, Mapping) else owner_consent
            )
        if data_freshness is not None:
            if "data_freshness" in base_context and base_context["data_freshness"] != data_freshness:
                issues.append(OwnedMeasurementIssue(1, "data_freshness", "freshness metadata does not match supplied context"))
            base_context["data_freshness"] = (
                dict(data_freshness) if isinstance(data_freshness, Mapping) else data_freshness
            )
        if event_map_id is not None:
            if not str(event_map_id).strip():
                issues.append(OwnedMeasurementIssue(1, "event_map_id", "event map ID cannot be empty"))
            if "event_map_id" in base_context and base_context["event_map_id"] != event_map_id:
                issues.append(OwnedMeasurementIssue(1, "event_map_id", "event map ID does not match supplied context"))
            base_context["event_map_id"] = str(event_map_id)
        if event_map_version is not None:
            if not str(event_map_version).strip():
                issues.append(OwnedMeasurementIssue(1, "event_map_version", "event map version cannot be empty"))
            if "event_map_version" in base_context and base_context["event_map_version"] != event_map_version:
                issues.append(OwnedMeasurementIssue(1, "event_map_version", "event map version does not match supplied context"))
            base_context["event_map_version"] = str(event_map_version)
        if owner_verified:
            base_context["owner_verified"] = True
        for identity_key, expected_value in (
            ("prospect_id", prospect_id),
            ("vertical_id", vertical_id),
            ("source", normalized_source),
        ):
            supplied_value = base_context.get(identity_key)
            if supplied_value is None:
                continue
            supplied_text = str(supplied_value).strip()
            if identity_key == "source":
                supplied_text = SOURCE_ALIASES.get(
                    supplied_text.casefold().replace("-", "_").replace(" ", "_"), supplied_text
                )
            if supplied_text != expected_value:
                issues.append(
                    OwnedMeasurementIssue(
                        1,
                        identity_key,
                        f"measurement {identity_key} does not match the import scope",
                    )
                )
        supplied_hash = base_context.get("source_sha256")
        if supplied_hash is not None and str(supplied_hash).strip() != digest:
            issues.append(
                OwnedMeasurementIssue(
                    1,
                    "source_sha256",
                    "measurement source hash does not match uploaded content",
                )
            )
        issues.extend(self._validate_context(base_context))
        if owner_verified or require_owner_consent:
            issues.extend(self._validate_owner_consent(base_context.get("owner_consent")))
        issues.extend(self._validate_freshness(base_context.get("data_freshness")))
        reader = csv.DictReader(io.StringIO(text))
        if not reader.fieldnames:
            issues.append(OwnedMeasurementIssue(1, "header", "CSV header is required"))
            return OwnedMeasurementPreview(digest, normalized_source, 0, [], issues)
        if len(reader.fieldnames) > MAX_OWNED_MEASUREMENT_COLUMNS:
            issues.append(OwnedMeasurementIssue(1, "header", f"CSV exceeds {MAX_OWNED_MEASUREMENT_COLUMNS} columns"))
        pii_headers = [
            header for header in reader.fieldnames
            if self._normalize_header(header) not in _CONTEXT_HEADERS
            and _PII_HEADER_RE.search(str(header or ""))
        ]
        if pii_headers:
            issues.append(OwnedMeasurementIssue(1, "header", "PII columns are not accepted", pii_headers))
        secret_headers = [header for header in reader.fieldnames if _SECRET_KEY_RE.search(str(header or ""))]
        if secret_headers:
            issues.append(OwnedMeasurementIssue(1, "header", "credential columns are not accepted", secret_headers))
        unsafe_headers = bool(pii_headers or secret_headers)
        header_map = self._header_map(reader.fieldnames)
        has_bound_context = any(
            key in base_context and base_context[key] is not None and base_context[key] != ""
            for key in _BOUND_CONTEXT_HEADERS
        )
        if not has_bound_context and not any(
            self._normalize_header(header) in _BOUND_CONTEXT_HEADERS for header in reader.fieldnames
        ):
            issues.append(OwnedMeasurementIssue(1, "context", "measurement context is required"))
        rows_seen = 0
        seen_payloads: set[str] = set()
        scope_values: dict[str, str] = {}
        for row_number, raw in enumerate(reader, start=2):
            rows_seen += 1
            if rows_seen > MAX_OWNED_MEASUREMENT_ROWS:
                issues.append(OwnedMeasurementIssue(row_number, "csv", f"CSV exceeds {MAX_OWNED_MEASUREMENT_ROWS} rows"))
                break
            values = {key: str(raw.get(header) or "").strip() for key, header in header_map.items()}
            formula_field = next((key for key, value in raw.items() if _FORMULA_RE.match(str(value or "").strip())), None)
            if formula_field:
                issues.append(OwnedMeasurementIssue(row_number, formula_field, "spreadsheet formulas are not accepted"))
                continue
            row_context = dict(base_context)
            metrics: dict[str, float | int | None] = {}
            try:
                start = values.get("period_start") or period_start or ""
                end = values.get("period_end") or period_end or start
                if not start or not end:
                    raise ValueError("period_start and period_end are required")
                if period_start and start != period_start:
                    raise ValueError("CSV period_start does not match the supplied period")
                if period_end and end != period_end:
                    raise ValueError("CSV period_end does not match the supplied period")
                for key, value in values.items():
                    if key in {"period_start", "period_end"} or not value:
                        continue
                    if key in _METRIC_KEYS:
                        metric_key = key
                        # GBP calls its profile impressions simply "views";
                        # keep that source-specific measure distinct from
                        # Search Console impressions.
                        if (
                            normalized_source == "gbp_csv"
                            and key == "impressions"
                            and self._normalize_header(header_map.get(key, "")) == "views"
                        ):
                            metric_key = "profile_views"
                        metrics[metric_key] = self._number(value)
                    elif key in _CONTEXT_HEADERS:
                        self._assign_row_context(
                            row_context,
                            base_context,
                            key,
                            value,
                            prospect_id=prospect_id,
                            vertical_id=vertical_id,
                            source=normalized_source,
                            source_sha256=digest,
                        )
                # Unmapped numeric columns are aggregate metrics; textual columns
                # become explicit context dimensions rather than being discarded.
                mapped_headers = set(header_map.values())
                for header, value in raw.items():
                    normalized = self._normalize_header(header)
                    if not value or header in mapped_headers:
                        continue
                    if normalized in _CONTEXT_HEADERS:
                        self._assign_row_context(
                            row_context,
                            base_context,
                            normalized,
                            str(value).strip(),
                            prospect_id=prospect_id,
                            vertical_id=vertical_id,
                            source=normalized_source,
                            source_sha256=digest,
                        )
                    elif _SECRET_KEY_RE.search(str(header or "")):
                        raise ValueError("credential columns are not accepted")
                    elif (
                        normalized not in _CONTEXT_HEADERS
                        and _PII_HEADER_RE.search(str(header or ""))
                    ):
                        continue
                    else:
                        metrics[normalized] = self._number(str(value).strip())
                # Some GBP/CRM exports use a long form (``metric,value``)
                # instead of one column per aggregate.  Preserve ``value``
                # while also exposing the canonical source metric.
                metric_label = row_context.get("metric") or row_context.get("dimension")
                if metric_label and "value" in metrics:
                    canonical_metric = self._canonical_metric_name(str(metric_label))
                    if canonical_metric:
                        metrics.setdefault(canonical_metric, metrics["value"])
                if not metrics:
                    raise ValueError("at least one aggregate metric is required")
                if unsafe_headers:
                    raise ValueError("PII or credential columns are not accepted")
                for dimension in _SINGLE_SCOPE_DIMENSIONS:
                    current_value = row_context.get(dimension)
                    if current_value is None or current_value == "":
                        continue
                    current_text = str(current_value)
                    if dimension in {"market", "location"}:
                        for location_key in ("market", "location"):
                            existing_location = scope_values.get(location_key)
                            if existing_location is not None and existing_location != current_text:
                                raise ValueError("CSV rows have incompatible context for market/location")
                    previous_text = scope_values.setdefault(dimension, current_text)
                    if previous_text != current_text:
                        raise ValueError(f"CSV rows have incompatible context for {dimension}")
                freshness = self._row_freshness(row_context)
                if freshness:
                    row_context["data_freshness"] = freshness
                    freshness_issues = self._validate_freshness(freshness, row_number=row_number)
                    if freshness_issues:
                        raise ValueError(freshness_issues[0].message)
                provenance = {
                    "import_method": "csv",
                    "source_sha256": digest,
                    "source_row": row_number,
                }
                row_context["provenance"] = provenance
                row_context["source_sha256"] = digest
                row_context["source_row"] = row_number
                ref = artifact_ref or f"owned-measurements/{digest}.csv"
                if not isinstance(ref, str) or not ref.strip():
                    raise ValueError("artifact_ref is required")
                stable_context = self._stable_context(row_context)
                stable_payload = {
                    "source": normalized_source,
                    "prospect_id": prospect_id,
                    "vertical_id": vertical_id,
                    "period_start": start,
                    "period_end": end,
                    "source_sha256": digest,
                    "context": stable_context,
                    "metrics": metrics,
                }
                duplicate_key = json.dumps(stable_payload, sort_keys=True, separators=(",", ":"))
                if duplicate_key in seen_payloads:
                    raise ValueError("duplicate owned measurement snapshot")
                seen_payloads.add(duplicate_key)
                payload_id = hashlib.sha256(duplicate_key.encode("utf-8")).hexdigest()
                snapshots.append(OwnedMeasurementSnapshot(
                    id=f"owned-{payload_id[:32]}", prospect_id=prospect_id, vertical_id=vertical_id,
                    source=normalized_source, period_start=start, period_end=end,
                    source_sha256=digest, context=row_context, metrics=metrics,
                    artifact_ref=f"{ref}#row={row_number}",
                ))
            except (TypeError, ValueError) as exc:
                issues.append(OwnedMeasurementIssue(row_number, "row", str(exc)))
        return OwnedMeasurementPreview(digest, normalized_source, rows_seen, snapshots, issues)

    def commit(self, preview: OwnedMeasurementPreview) -> list[OwnedMeasurementSnapshot]:
        if not preview.valid:
            raise ValueError("owned measurement preview contains errors")
        if self.repository is None:
            return list(preview.snapshots)
        committed: list[OwnedMeasurementSnapshot] = []
        for snapshot in preview.snapshots:
            # A repeated preview has a fresh model ``created_at`` but the same
            # content-derived identity.  Reuse the persisted immutable version
            # when its semantic payload matches instead of attempting a mutable
            # overwrite through the repository.
            existing = self.repository.get_owned_measurement_snapshot(snapshot.id)
            if existing is not None:
                if self._semantic_payload(existing) != self._semantic_payload(snapshot):
                    raise ValueError("owned measurement snapshot is immutable")
                committed.append(existing)
                continue
            committed.append(self.repository.save_owned_measurement_snapshot(snapshot))
        return committed

    def import_csv(self, csv_input: str | bytes | TextIO, **kwargs: Any) -> list[OwnedMeasurementSnapshot]:
        return self.commit(self.preview_csv(csv_input, **kwargs))

    preview_import = preview_csv
    commit_import = commit
    commit_preview = commit
    import_aggregate_csv = import_csv

    def list_snapshots(self, **filters: Any) -> list[OwnedMeasurementSnapshot]:
        if self.repository is None:
            return []
        return self.repository.list_owned_measurement_snapshots(**filters)

    def derive_funnel_baseline(
        self,
        snapshots: Iterable[OwnedMeasurementSnapshot] | None = None,
        *,
        snapshot_ids: Iterable[str] | None = None,
        prospect_id: str | None = None,
        vertical_id: str | None = None,
        context: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        if snapshots is None and snapshot_ids is not None:
            snapshots = self._resolve_snapshots(snapshot_ids)
        if snapshots is None:
            snapshots = self.list_snapshots(prospect_id=prospect_id, vertical_id=vertical_id)
        records = list(snapshots)
        if not records:
            raise ValueError("at least one owned measurement snapshot is required")
        observed_prospects = {record.prospect_id for record in records}
        observed_verticals = {record.vertical_id for record in records}
        if len(observed_prospects) != 1:
            raise ValueError("owned measurement snapshots must share a prospect")
        if len(observed_verticals) != 1:
            raise ValueError("owned measurement snapshots must share a vertical")
        if prospect_id and any(record.prospect_id != prospect_id for record in records):
            raise ValueError("owned measurement snapshots must share a prospect")
        if vertical_id and any(record.vertical_id != vertical_id for record in records):
            raise ValueError("owned measurement snapshots must share a vertical")
        if context:
            records = [record for record in records if all(record.context.get(k) == v for k, v in context.items())]
            if not records:
                raise ValueError("no owned measurement snapshots match the requested context")
        self._validate_compatible_contexts(records)
        shared_context = self._shared_context(records)
        metrics = self._aggregate_metrics(records)
        observed = self._observed_rates(metrics)
        baseline = {
            "contract_version": "owned-measurement.v1",
            "prospect_id": records[0].prospect_id,
            "vertical_id": records[0].vertical_id,
            "period_start": min(record.period_start for record in records),
            "period_end": max(record.period_end for record in records),
            "sources": sorted({record.source for record in records}),
            "snapshot_ids": [record.id for record in records],
            "source_sha256s": sorted({record.source_sha256 for record in records}),
            "metrics": metrics,
            "observed_metrics": observed,
            "context": shared_context,
        }
        baseline.update(metrics)
        baseline.update(observed)
        return baseline

    derive_baseline = derive_funnel_baseline
    aggregate_baseline = derive_funnel_baseline

    def create_calibration_record(
        self, snapshots: Iterable[OwnedMeasurementSnapshot | str], *, market: str | None = None
    ) -> AcquisitionCalibrationRecord:
        baseline = self.derive_funnel_baseline(self._resolve_snapshots(snapshots))
        metrics = baseline["metrics"]
        record = AcquisitionCalibrationRecord(
            id=new_id(), prospect_id=baseline["prospect_id"], vertical_id=baseline["vertical_id"],
            market=market or str(baseline["context"].get("market") or baseline["context"].get("location") or "owner-provided"),
            source="owned_measurement",
            period_start=baseline["period_start"], period_end=baseline["period_end"],
            impressions=metrics.get("impressions"), clicks=metrics.get("clicks"),
            total_users=metrics.get("total_users"), signups_or_leads=metrics.get("signups_or_leads"),
            attended_or_appointments=metrics.get("attended_or_appointments"),
            new_customers=metrics.get("new_customers"), spend=metrics.get("spend"),
            artifact_ref={"kind": "owned_measurement_baseline", "snapshot_ids": baseline["snapshot_ids"], "source_sha256s": baseline["source_sha256s"]},
        )
        return self.repository.save_acquisition_calibration_record(record) if self.repository else record

    def calibrate_scenario(
        self,
        scenario_id: str,
        snapshots: Iterable[OwnedMeasurementSnapshot | str] | None = None,
        *,
        snapshot_ids: Iterable[str] | None = None,
        market: str | None = None,
    ):
        if self.repository is None:
            raise ValueError("forecast calibration requires a repository")
        selected = snapshots if snapshots is not None else snapshot_ids
        if selected is None:
            raise ValueError("at least one owned measurement snapshot is required")
        calibration = self.create_calibration_record(selected, market=market)
        return CalibrationService(self.repository).calibrate_scenario(scenario_id, calibration.id)

    create_calibrated_successor = calibrate_scenario
    calibrate_opportunity = calibrate_scenario

    def _resolve_snapshots(self, snapshots: Iterable[OwnedMeasurementSnapshot | str]) -> list[OwnedMeasurementSnapshot]:
        resolved: list[OwnedMeasurementSnapshot] = []
        for snapshot in snapshots:
            if isinstance(snapshot, OwnedMeasurementSnapshot):
                resolved.append(snapshot)
                continue
            if self.repository is None:
                raise ValueError("snapshot IDs require a repository")
            loaded = self.repository.get_owned_measurement_snapshot(str(snapshot))
            if loaded is None:
                raise ValueError(f"owned measurement snapshot not found: {snapshot}")
            resolved.append(loaded)
        return resolved

    def collect_live(
        self, source: str, *, prospect_id: str, period_start: str, period_end: str,
        context: Mapping[str, Any], operator_approved: bool = False,
    ) -> OwnedMeasurementPreview:
        normalized_source = self._normalize_source(source)
        if not self.connectors_enabled:
            raise ConnectorDisabledError("live owned measurement connectors are disabled by default")
        if not operator_approved:
            raise ConnectorApprovalError("live connectors require explicit operator approval")
        context_issues = self._validate_context(context)
        if context_issues:
            raise ValueError("connector context contains prohibited credential or PII fields")
        connector = self._connectors.get(normalized_source)
        if connector is None:
            raise ValueError(f"no connector registered for {normalized_source}")
        if any(callable(getattr(connector, name, None)) for name in ("write", "update", "delete", "push", "mutate")):
            raise ValueError("owned measurement connectors must be read-only")
        reader = getattr(connector, "read_aggregate", None)
        if reader is None:
            reader = getattr(connector, "fetch_aggregate", None) or getattr(connector, "collect_aggregate", None)
        if not callable(reader):
            raise ValueError("owned measurement connectors must expose a read aggregate method")
        rows = reader(
            prospect_id=prospect_id, period_start=period_start, period_end=period_end, context=dict(context)
        )
        fields: set[str] = set()
        materialized = [dict(row) for row in rows]
        for row in materialized:
            fields.update(row)
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=sorted(fields))
        writer.writeheader()
        writer.writerows(materialized)
        return self.preview_csv(output.getvalue(), prospect_id=prospect_id, vertical_id=str(context.get("vertical_id") or "unknown"), source=normalized_source, context=context, period_start=period_start, period_end=period_end)

    @staticmethod
    def _normalize_source(source: str) -> str:
        normalized = str(source).casefold().strip().replace("-", "_").replace(" ", "_")
        normalized = SOURCE_ALIASES.get(normalized, normalized)
        if normalized not in SUPPORTED_SOURCES:
            raise ValueError(f"unsupported owned measurement source: {source}")
        return normalized

    @staticmethod
    def _normalize_header(header: str) -> str:
        text = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", str(header or ""))
        return re.sub(r"[^a-z0-9]+", "_", text.casefold()).strip("_")

    @classmethod
    def _header_map(cls, headers: list[str]) -> dict[str, str]:
        normalized = {cls._normalize_header(header): header for header in headers}
        mapping: dict[str, str] = {}
        for canonical, aliases in _PERIOD_ALIASES.items():
            for alias in sorted(aliases, key=lambda item: (item != canonical, item)):
                if alias in normalized:
                    mapping[canonical] = normalized[alias]
                    break
        for canonical, aliases in _METRIC_ALIASES.items():
            for alias in sorted(aliases, key=lambda item: (item != canonical, item)):
                if alias in normalized:
                    mapping[canonical] = normalized[alias]
                    break
        for header in headers:
            normalized_header = cls._normalize_header(header)
            if normalized_header in _CONTEXT_HEADERS:
                mapping[normalized_header] = header
        return mapping

    @classmethod
    def _assign_row_context(
        cls,
        row_context: dict[str, Any],
        base_context: Mapping[str, Any],
        key: str,
        value: str,
        *,
        prospect_id: str,
        vertical_id: str,
        source: str,
        source_sha256: str,
    ) -> None:
        """Add a CSV dimension while enforcing the caller's identity scope."""

        normalized_key = cls._normalize_header(key)
        normalized_value = str(value).strip()
        if normalized_key in _PII_SENSITIVE_DIMENSIONS:
            if _PII_VALUE_RE.search(normalized_value):
                raise ValueError("PII context values are not accepted")
            if _SECRET_VALUE_RE.search(normalized_value):
                raise ValueError("credential context values are not accepted")
        if normalized_key == "source" and normalized_value:
            source_name = normalized_value.casefold().replace("-", "_").replace(" ", "_")
            source_alias = SOURCE_ALIASES.get(source_name, source_name)
            if source_alias and source_alias != source:
                if source_alias in SUPPORTED_SOURCES:
                    raise ValueError("CSV source does not match the import source")
        if normalized_key == "prospect_id" and normalized_value != prospect_id:
            raise ValueError("CSV prospect does not match the import prospect")
        if normalized_key == "vertical_id" and normalized_value != vertical_id:
            raise ValueError("CSV vertical does not match the import vertical")
        if normalized_key == "source_sha256" and normalized_value != source_sha256:
            raise ValueError("CSV source hash does not match uploaded content")

        expected = base_context.get(normalized_key)
        if expected is not None and str(expected).strip() != normalized_value:
            raise ValueError(f"CSV context does not match supplied context for {normalized_key}")
        if normalized_key in _FRESHNESS_HEADERS:
            expected_freshness = base_context.get("data_freshness")
            if isinstance(expected_freshness, Mapping):
                expected_value = expected_freshness.get(normalized_key)
                if expected_value is not None and str(expected_value).strip() != normalized_value:
                    raise ValueError(f"CSV freshness does not match supplied context for {normalized_key}")
        row_context[normalized_key] = normalized_value

    @staticmethod
    def _stable_context(context: Mapping[str, Any]) -> dict[str, Any]:
        """Drop row bookkeeping so identity/deduplication is source-stable."""

        return {
            str(key): value
            for key, value in context.items()
            if key not in {"provenance", "source_row"}
        }

    @staticmethod
    def _canonical_metric_name(label: str) -> str | None:
        normalized = re.sub(r"[^a-z0-9]+", "_", label.casefold()).strip("_")
        for canonical, aliases in _METRIC_ALIASES.items():
            if normalized == canonical or normalized in aliases:
                return canonical
        return None

    @staticmethod
    def _semantic_payload(snapshot: OwnedMeasurementSnapshot) -> dict[str, Any]:
        payload = snapshot.to_dict()
        payload.pop("created_at", None)
        return payload

    @staticmethod
    def _row_freshness(context: Mapping[str, Any]) -> dict[str, Any]:
        freshness = context.get("data_freshness")
        output = dict(freshness) if isinstance(freshness, Mapping) else {}
        for key in _FRESHNESS_HEADERS:
            if key in context and context[key] is not None and context[key] != "":
                output.setdefault(key, context[key])
        return output

    @staticmethod
    def _validate_owner_consent(
        consent: Any,
        *,
        row_number: int = 1,
    ) -> list[OwnedMeasurementIssue]:
        if not isinstance(consent, Mapping):
            return [OwnedMeasurementIssue(row_number, "owner_consent", "confirmed owner consent metadata is required")]
        confirmed = consent.get("confirmed")
        if confirmed is not True:
            return [OwnedMeasurementIssue(row_number, "owner_consent.confirmed", "owner consent must be confirmed")]
        missing = [
            key
            for key in ("operator", "confirmed_at")
            if not isinstance(consent.get(key), str) or not consent.get(key).strip()
        ]
        if missing:
            return [OwnedMeasurementIssue(row_number, "owner_consent", f"owner consent requires {', '.join(missing)}")]
        return []

    @staticmethod
    def _validate_freshness(
        freshness: Any,
        *,
        row_number: int = 1,
    ) -> list[OwnedMeasurementIssue]:
        if freshness is None:
            return []
        if not isinstance(freshness, Mapping):
            return [OwnedMeasurementIssue(row_number, "data_freshness", "freshness metadata must be an object")]
        status = str(freshness.get("status") or freshness.get("freshness_status") or "").strip().casefold()
        if status not in {"", "fresh", "stale", "unknown", "partial"}:
            return [OwnedMeasurementIssue(row_number, "data_freshness.status", "unsupported freshness status")]
        if status == "stale":
            return [OwnedMeasurementIssue(row_number, "data_freshness.status", "owner measurement snapshot is stale")]
        age_days = freshness.get("age_days")
        if age_days is None:
            age_days = freshness.get("freshness_age_days", freshness.get("data_age_days"))
        if age_days is not None:
            try:
                age = float(age_days)
            except (TypeError, ValueError):
                return [OwnedMeasurementIssue(row_number, "data_freshness.age_days", "freshness age must be numeric")]
            if age < 0:
                return [OwnedMeasurementIssue(row_number, "data_freshness.age_days", "freshness age cannot be negative")]
        date_fields = [
            key for key in {
                "snapshot_date", "retrieval_date", "retrieved_at", "exported_at", "as_of", "data_date",
                "freshness_date", "data_updated_at", "last_updated", "source_snapshot_date",
            }
            if freshness.get(key) is not None and freshness.get(key) != ""
        ]
        if not date_fields and status == "fresh":
            return [OwnedMeasurementIssue(row_number, "data_freshness", "freshness metadata requires a snapshot date")]
        return []

    @staticmethod
    def _validate_context(context: Mapping[str, Any]) -> list[OwnedMeasurementIssue]:
        issues: list[OwnedMeasurementIssue] = []
        if not isinstance(context, Mapping):
            return [OwnedMeasurementIssue(1, "context", "measurement context must be an object")]

        def inspect(payload: Any, prefix: str = "") -> None:
            if isinstance(payload, Mapping):
                for key, value in payload.items():
                    field = f"{prefix}.{key}" if prefix else str(key)
                    normalized = str(key).casefold().replace("-", "_")
                    if normalized not in _CONTEXT_HEADERS and _PII_HEADER_RE.search(normalized):
                        issues.append(OwnedMeasurementIssue(1, field, "PII context fields are not accepted"))
                    elif _SECRET_KEY_RE.search(normalized):
                        issues.append(OwnedMeasurementIssue(1, field, "credential context fields are not accepted"))
                    elif (
                        normalized in _PII_SENSITIVE_DIMENSIONS
                        and isinstance(value, str)
                        and _PII_VALUE_RE.search(value)
                    ):
                        issues.append(OwnedMeasurementIssue(1, field, "PII context values are not accepted"))
                    elif (
                        normalized in _PII_SENSITIVE_DIMENSIONS
                        and isinstance(value, str)
                        and _SECRET_VALUE_RE.search(value)
                    ):
                        issues.append(OwnedMeasurementIssue(1, field, "credential context values are not accepted"))
                    inspect(value, field)
            elif isinstance(payload, (list, tuple)):
                for index, value in enumerate(payload):
                    inspect(value, f"{prefix}[{index}]")
            elif isinstance(payload, (bytes, bytearray)):
                issues.append(OwnedMeasurementIssue(1, prefix, "binary credential values are not accepted"))

        inspect(context)
        return issues

    @staticmethod
    def _number(value: str) -> float:
        if _FORMULA_RE.match(value):
            raise ValueError("spreadsheet formulas are not accepted")
        try:
            number = float(value.replace(",", "").replace("$", "").replace("%", "").strip())
        except ValueError as exc:
            raise ValueError("aggregate value is not numeric") from exc
        if not math.isfinite(number):
            raise ValueError("aggregate value must be finite")
        if number < 0:
            raise ValueError("aggregate values cannot be negative")
        return int(number) if number.is_integer() else number

    @staticmethod
    def _read_text(csv_input: str | bytes | TextIO) -> str:
        if isinstance(csv_input, Path):
            raise ValueError("filesystem paths are not accepted as owned measurement uploads")
        if isinstance(csv_input, bytes):
            if len(csv_input) > MAX_OWNED_MEASUREMENT_BYTES:
                raise ValueError("owned measurement CSV exceeds size limit")
            text = csv_input.decode("utf-8-sig")
        elif isinstance(csv_input, str):
            text = csv_input.lstrip("\ufeff")
        else:
            text = csv_input.read().lstrip("\ufeff")
        if len(text.encode("utf-8")) > MAX_OWNED_MEASUREMENT_BYTES:
            raise ValueError("owned measurement CSV exceeds size limit")
        return text

    @staticmethod
    def _aggregate_metrics(records: list[OwnedMeasurementSnapshot]) -> dict[str, float | None]:
        def total(keys: tuple[str, ...]) -> float | None:
            values = []
            for record in records:
                value = next((record.metrics[key] for key in keys if key in record.metrics and record.metrics[key] is not None), None)
                if value is not None:
                    values.append(float(value))
            return int(sum(values)) if values and sum(values).is_integer() else (sum(values) if values else None)
        def source_total(source_names: set[str], keys: tuple[str, ...]) -> float | None:
            selected = [record for record in records if record.source in source_names]
            return total_from(selected, keys)

        def total_from(selected: list[OwnedMeasurementSnapshot], keys: tuple[str, ...]) -> float | None:
            values = []
            for record in selected:
                value = next((record.metrics[key] for key in keys if key in record.metrics and record.metrics[key] is not None), None)
                if value is not None:
                    values.append(float(value))
            return int(sum(values)) if values and sum(values).is_integer() else (sum(values) if values else None)

        # Keep semantically equivalent source measures from being counted twice:
        # GA4 sessions represent site visits even when GSC clicks are present;
        # CRM leads represent the downstream lead stage even when GA4 signups
        # are also exported.  Each stage falls back to the next source only when
        # its preferred aggregate is unavailable.
        site_clicks = source_total({"ga4_csv"}, ("sessions", "clicks"))
        if site_clicks is None:
            site_clicks = source_total({"gbp_csv"}, ("sessions", "clicks"))
        if site_clicks is None:
            site_clicks = source_total({"gsc_csv"}, ("clicks",))
        leads = source_total({"crm_csv"}, ("signups", "leads"))
        if leads is None:
            leads = source_total({"ga4_csv"}, ("signups",))
        def first_non_none(*values: float | None) -> float | None:
            return next((value for value in values if value is not None), None)
        return {
            "impressions": total(("impressions",)),
            "clicks": site_clicks,
            "total_users": first_non_none(source_total({"ga4_csv"}, ("users", "total_users")), total(("users", "total_users"))),
            "signups_or_leads": leads,
            "attended_or_appointments": first_non_none(source_total({"crm_csv"}, ("appointments", "attended_or_appointments")), total(("appointments", "attended_or_appointments"))),
            "new_customers": first_non_none(source_total({"crm_csv"}, ("customers", "new_customers")), total(("customers", "new_customers"))),
            "spend": total(("spend",)),
        }

    @staticmethod
    def _validate_compatible_contexts(records: list[OwnedMeasurementSnapshot]) -> None:
        dimensions = set().union(*(record.context for record in records))
        dimensions -= _VOLATILE_CONTEXT_DIMENSIONS
        dimensions -= _ROW_CONTEXT_DIMENSIONS
        dimensions -= _FRESHNESS_HEADERS
        for dimension in dimensions:
            values = {json.dumps(record.context.get(dimension), sort_keys=True) for record in records if dimension in record.context}
            if len(values) > 1:
                raise ValueError(f"owned measurement context is incompatible for {dimension}")

    @staticmethod
    def _shared_context(records: list[OwnedMeasurementSnapshot]) -> dict[str, Any]:
        excluded = _VOLATILE_CONTEXT_DIMENSIONS | _ROW_CONTEXT_DIMENSIONS | _FRESHNESS_HEADERS
        shared: dict[str, Any] = {}
        dimensions = set().union(*(record.context for record in records)) - excluded
        for dimension in sorted(dimensions):
            values = [record.context[dimension] for record in records if dimension in record.context]
            if len(values) == len(records) and all(value == values[0] for value in values):
                shared[dimension] = values[0]
        return shared

    @staticmethod
    def _observed_rates(metrics: Mapping[str, float | None]) -> dict[str, float | None]:
        def divide(numerator: float | None, denominator: float | None) -> float | None:
            if numerator is None or denominator is None or denominator <= 0:
                return None
            return round(numerator / denominator, 6)
        visits = metrics.get("clicks") if metrics.get("clicks") is not None else metrics.get("total_users")
        return {
            "sessions_per_user": divide(metrics.get("clicks"), metrics.get("total_users")),
            "visit_to_signup": divide(metrics.get("signups_or_leads"), visits),
            "attendance_rate": divide(metrics.get("attended_or_appointments"), metrics.get("signups_or_leads")),
            "close_rate": divide(metrics.get("new_customers"), metrics.get("attended_or_appointments")),
            "cost_per_signup": divide(metrics.get("spend"), metrics.get("signups_or_leads")),
            "cost_per_customer": divide(metrics.get("spend"), metrics.get("new_customers")),
        }


_METRIC_KEYS = {key for aliases in _METRIC_ALIASES.values() for key in aliases} | set(_METRIC_ALIASES)


# Compatibility spelling used by a few operator integrations.
OwnedMeasurementImportService = OwnedMeasurementService
