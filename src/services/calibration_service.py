"""Aggregate-only acquisition calibration and immutable forecast learning."""

from __future__ import annotations

import csv
import hashlib
import io
import re
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Any, TextIO

from src.models import (
    AcquisitionCalibrationRecord,
    BusinessEconomicsProfile,
    DemandEvidenceSet,
    OpportunityScenario,
    new_id,
    utc_now_iso,
)
from src.repositories.base import InsightRepository
from src.services.opportunity_model_service import OpportunityModelService


MAX_CALIBRATION_BYTES = 1024 * 1024
MAX_CALIBRATION_ROWS = 120
MAX_CALIBRATION_COLUMNS = 30
PII_HEADER_RE = re.compile(
    r"(?:^|[_\s-])(name|email|phone|address|customer|lead_id|user_id)(?:$|[_\s-])",
    re.IGNORECASE,
)
FORMULA_RE = re.compile(r"^[=+\-@]")


@dataclass(slots=True)
class CalibrationIssue:
    row_number: int
    field: str
    message: str
    value: Any = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class CalibrationPreview:
    source_sha256: str
    rows_seen: int
    records: list[AcquisitionCalibrationRecord]
    issues: list[CalibrationIssue]

    @property
    def valid(self) -> bool:
        return bool(self.records) and not self.issues

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_sha256": self.source_sha256,
            "rows_seen": self.rows_seen,
            "records": [record.to_dict() for record in self.records],
            "issues": [issue.to_dict() for issue in self.issues],
            "valid": self.valid,
        }


class CalibrationService:
    HEADER_ALIASES = {
        "period_start": {"period_start", "start_date", "date_start"},
        "period_end": {"period_end", "end_date", "date_end"},
        "source": {"source", "platform", "data_source"},
        "impressions": {"impressions"},
        "clicks": {"clicks", "sessions", "visits"},
        "total_users": {"total_users", "users", "unique_users"},
        "signups_or_leads": {"signups_or_leads", "signups", "leads"},
        "attended_or_appointments": {
            "attended_or_appointments",
            "attended_trials",
            "appointments",
        },
        "new_customers": {"new_customers", "members", "won_jobs", "customers"},
        "spend": {"spend", "cost", "ad_spend"},
    }

    def __init__(self, repository: InsightRepository | None = None) -> None:
        self.repository = repository

    def preview_csv(
        self,
        csv_input: str | bytes | TextIO,
        *,
        prospect_id: str,
        vertical_id: str,
        market: str,
    ) -> CalibrationPreview:
        text = self._read_text(csv_input)
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        reader = csv.DictReader(io.StringIO(text))
        issues: list[CalibrationIssue] = []
        if not reader.fieldnames:
            return CalibrationPreview(
                digest,
                0,
                [],
                [CalibrationIssue(1, "header", "CSV header is required")],
            )
        if len(reader.fieldnames) > MAX_CALIBRATION_COLUMNS:
            issues.append(
                CalibrationIssue(
                    1,
                    "header",
                    f"CSV exceeds {MAX_CALIBRATION_COLUMNS} columns",
                )
            )
        pii = [
            header
            for header in reader.fieldnames
            if PII_HEADER_RE.search(str(header or ""))
        ]
        if pii:
            issues.append(
                CalibrationIssue(
                    1,
                    "header",
                    "PII columns are not accepted",
                    pii,
                )
            )
        header_map = self._header_map(reader.fieldnames)
        missing = [
            field
            for field in ("period_start", "period_end", "source")
            if field not in header_map
        ]
        if missing:
            issues.append(
                CalibrationIssue(
                    1,
                    "header",
                    f"missing required columns: {', '.join(missing)}",
                )
            )

        records: list[AcquisitionCalibrationRecord] = []
        rows_seen = 0
        for row_number, raw in enumerate(reader, start=2):
            rows_seen += 1
            if rows_seen > MAX_CALIBRATION_ROWS:
                issues.append(
                    CalibrationIssue(
                        row_number,
                        "csv",
                        f"CSV exceeds {MAX_CALIBRATION_ROWS} rows",
                    )
                )
                break
            values = {
                key: str(raw.get(source_header) or "").strip()
                for key, source_header in header_map.items()
            }
            formula_field = next(
                (
                    key
                    for key, value in values.items()
                    if FORMULA_RE.match(value)
                ),
                None,
            )
            if formula_field:
                issues.append(
                    CalibrationIssue(
                        row_number,
                        formula_field,
                        "spreadsheet formulas are not accepted",
                    )
                )
                continue
            try:
                aggregates = {
                    field: self._optional_number(values.get(field, ""))
                    for field in (
                        "impressions",
                        "clicks",
                        "total_users",
                        "signups_or_leads",
                        "attended_or_appointments",
                        "new_customers",
                        "spend",
                    )
                }
                self._validate_funnel(aggregates)
                record = AcquisitionCalibrationRecord(
                    prospect_id=prospect_id,
                    vertical_id=vertical_id,
                    market=market,
                    source=values.get("source", ""),
                    period_start=values.get("period_start", ""),
                    period_end=values.get("period_end", ""),
                    artifact_ref={
                        "source_sha256": digest,
                        "source_row": row_number,
                    },
                    **aggregates,
                )
            except ValueError as exc:
                issues.append(
                    CalibrationIssue(
                        row_number,
                        "row",
                        str(exc),
                    )
                )
                continue
            records.append(record)
        return CalibrationPreview(digest, rows_seen, records, issues)

    def commit(
        self,
        preview: CalibrationPreview,
    ) -> list[AcquisitionCalibrationRecord]:
        if not preview.valid:
            raise ValueError("calibration preview contains errors")
        if self.repository is None:
            return list(preview.records)
        return [
            self.repository.save_acquisition_calibration_record(record)
            for record in preview.records
        ]

    @staticmethod
    def observed_metrics(
        record: AcquisitionCalibrationRecord,
        *,
        capacity_headroom: float | None = None,
    ) -> dict[str, float | None]:
        visits = record.clicks if record.clicks is not None else record.total_users
        return {
            "sessions_per_user": CalibrationService._divide(
                record.clicks,
                record.total_users,
            ),
            "visit_to_signup": CalibrationService._divide(
                record.signups_or_leads,
                visits,
            ),
            "attendance_rate": CalibrationService._divide(
                record.attended_or_appointments,
                record.signups_or_leads,
            ),
            "close_rate": CalibrationService._divide(
                record.new_customers,
                record.attended_or_appointments,
            ),
            "cost_per_signup": CalibrationService._divide(
                record.spend,
                record.signups_or_leads,
            ),
            "cost_per_customer": CalibrationService._divide(
                record.spend,
                record.new_customers,
            ),
            "capacity_fill_rate": CalibrationService._divide(
                record.new_customers,
                capacity_headroom,
            ),
        }

    def calibrate_scenario(
        self,
        scenario_id: str,
        calibration_id: str,
    ) -> OpportunityScenario:
        if self.repository is None:
            raise ValueError("forecast calibration requires a repository")
        original = self.repository.get_opportunity_scenario(scenario_id)
        if original is None:
            raise ValueError(f"opportunity scenario not found: {scenario_id}")
        calibration = self.repository.get_acquisition_calibration_record(
            calibration_id
        )
        if calibration is None:
            raise ValueError(f"calibration record not found: {calibration_id}")
        if calibration.prospect_id != original.prospect_id:
            raise ValueError("calibration and scenario prospects do not match")
        economics = self.repository.get_business_economics_profile(
            original.economics_profile_id
        )
        if economics is None:
            raise ValueError("scenario economics profile is missing")
        demand = (
            self.repository.get_demand_evidence_set(
                original.demand_evidence_set_id
            )
            if original.demand_evidence_set_id
            else None
        )
        metrics = self.observed_metrics(
            calibration,
            capacity_headroom=economics.capacity_headroom,
        )
        assumptions = {
            band: {
                name: dict(entry)
                for name, entry in values.items()
            }
            for band, values in original.assumptions.items()
        }
        mapping = {
            "visit_to_signup_rate": metrics["visit_to_signup"],
            "signup_to_attended_rate": metrics["attendance_rate"],
            "attended_to_customer_rate": metrics["close_rate"],
        }
        for name, value in mapping.items():
            if value is not None:
                assumptions["base"][name] = {
                    "value": value,
                    "provenance": "aggregate_calibration",
                    "reviewed": True,
                }
        recalculated = OpportunityModelService().create_scenario(
            insight_run_id=original.insight_run_id,
            prospect_id=original.prospect_id,
            economics=economics,
            demand=demand,
            assumptions=assumptions,
        )
        successor = replace(
            recalculated,
            id=new_id(),
            predecessor_id=original.id,
            calibrated_from_id=calibration.id,
            evidence_refs=[
                *recalculated.evidence_refs,
                {
                    "kind": "acquisition_calibration_record",
                    "record_id": calibration.id,
                    "version": calibration.version,
                    "artifact_ref": calibration.artifact_ref,
                },
            ],
            sensitivity={
                **recalculated.sensitivity,
                "observed_calibration": metrics,
            },
            created_at=utc_now_iso(),
        )
        return self.repository.save_opportunity_scenario(successor)

    @classmethod
    def _header_map(cls, headers: list[str]) -> dict[str, str]:
        normalized = {
            re.sub(r"[^a-z0-9]+", "_", header.casefold()).strip("_"): header
            for header in headers
        }
        mapping: dict[str, str] = {}
        for canonical, aliases in cls.HEADER_ALIASES.items():
            for alias in aliases:
                if alias in normalized:
                    mapping[canonical] = normalized[alias]
                    break
        return mapping

    @staticmethod
    def _optional_number(value: str) -> float | None:
        if not value:
            return None
        number = float(value.replace(",", "").replace("$", ""))
        if number < 0:
            raise ValueError("aggregate values cannot be negative")
        return number

    @staticmethod
    def _validate_funnel(values: dict[str, float | None]) -> None:
        stages = (
            values.get("signups_or_leads"),
            values.get("attended_or_appointments"),
            values.get("new_customers"),
        )
        for earlier, later in zip(stages, stages[1:]):
            if earlier is not None and later is not None and later > earlier:
                raise ValueError(
                    "downstream funnel counts cannot exceed the prior stage"
                )

    @staticmethod
    def _divide(
        numerator: float | None,
        denominator: float | None,
    ) -> float | None:
        if numerator is None or denominator is None or denominator <= 0:
            return None
        return round(numerator / denominator, 6)

    @staticmethod
    def _read_text(csv_input: str | bytes | TextIO) -> str:
        if isinstance(csv_input, Path):
            raise ValueError("filesystem paths are not accepted as calibration uploads")
        if isinstance(csv_input, bytes):
            if len(csv_input) > MAX_CALIBRATION_BYTES:
                raise ValueError("calibration CSV exceeds size limit")
            text = csv_input.decode("utf-8-sig")
        elif isinstance(csv_input, str):
            text = csv_input.lstrip("\ufeff")
        else:
            text = csv_input.read().lstrip("\ufeff")
        if len(text.encode("utf-8")) > MAX_CALIBRATION_BYTES:
            raise ValueError("calibration CSV exceeds size limit")
        return text
