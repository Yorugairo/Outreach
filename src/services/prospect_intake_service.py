"""Deterministic prospect CSV intake with no persistence side effects."""

from __future__ import annotations

import csv
import io
import re
from dataclasses import asdict, dataclass, replace
from typing import Any, Iterable, Mapping, TextIO
from urllib.parse import urlsplit, urlunsplit

from src.models import ProspectRecord, VerticalPack
from src.vertical_packs import resolve_vertical_pack


@dataclass(slots=True)
class ProspectRowIssue:
    row_number: int
    field: str
    message: str
    value: Any = None
    severity: str = "error"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class ProspectImportPreview:
    vertical_pack_version: str
    rows_seen: int
    records: list[ProspectRecord]
    issues: list[ProspectRowIssue]

    @property
    def errors(self) -> list[ProspectRowIssue]:
        return [issue for issue in self.issues if issue.severity == "error"]

    @property
    def warnings(self) -> list[ProspectRowIssue]:
        return [issue for issue in self.issues if issue.severity == "warning"]

    @property
    def valid_prospects(self) -> list[ProspectRecord]:
        return [record for record in self.records if record.is_runnable]

    @property
    def commit_ready(self) -> list[ProspectRecord]:
        return self.valid_prospects

    def to_dict(self) -> dict[str, Any]:
        return {
            "vertical_pack_version": self.vertical_pack_version,
            "rows_seen": self.rows_seen,
            "records": [record.to_dict() for record in self.records],
            "valid_prospects": [record.to_dict() for record in self.valid_prospects],
            "issues": [issue.to_dict() for issue in self.issues],
        }


_ALIASES: dict[str, tuple[str, ...]] = {
    "business_name": ("business_name", "business", "name", "company", "academy_name"),
    "website_url": ("website_url", "website", "url", "domain", "site"),
    "category": ("category", "business_category", "type", "vertical_category"),
    "location": ("location", "city", "market", "service_area", "address"),
    "contact_route": ("contact_route", "contact", "contact_info", "email", "phone"),
    "source_provenance": ("source_provenance", "source", "source_url", "provenance", "dataset"),
}


class ProspectIntakeService:
    """Parse and qualify curated CSV rows for a selected vertical pack.

    The service intentionally does not persist. A caller may pass the returned
    ``valid_prospects`` to a repository after operator review.
    """

    def __init__(self, packs: Mapping[str, VerticalPack] | None = None) -> None:
        self._packs = dict(packs or {})

    def preview_csv(
        self,
        csv_input: str | bytes | TextIO,
        vertical_pack: str | VerticalPack = "one_trade_network.v1",
    ) -> ProspectImportPreview:
        pack = self._resolve_pack(vertical_pack)
        text = self._read_text(csv_input)
        reader = csv.DictReader(io.StringIO(text))
        if not reader.fieldnames:
            return ProspectImportPreview(pack.pack_id, 0, [], [ProspectRowIssue(1, "header", "CSV header is required")])

        headers = {self._header_key(name): name for name in reader.fieldnames if name}
        records: list[ProspectRecord] = []
        issues: list[ProspectRowIssue] = []
        seen: set[tuple[str, str]] = set()
        rows_seen = 0
        for row_number, row in enumerate(reader, start=2):
            rows_seen += 1
            if None in row:
                issues.append(ProspectRowIssue(row_number, "row", "row contains more values than the CSV header"))
            values = self._canonical_row(row, headers)
            record = self._record_from_row(values, pack, row_number)
            qualified, row_issues = self.qualify(record, pack, row_number=row_number)
            issues.extend(row_issues)
            identity = (pack.vertical_id, qualified.normalized_domain)
            if qualified.normalized_domain and identity in seen:
                issues.append(
                    ProspectRowIssue(
                        row_number,
                        "website_url",
                        "duplicate website for this vertical; first row retained",
                        value=qualified.normalized_domain,
                    )
                )
                continue
            if qualified.normalized_domain:
                seen.add(identity)
            records.append(qualified)
        return ProspectImportPreview(pack.pack_id, rows_seen, records, issues)

    # Explicit aliases make the small service convenient to use from CLI/API slices.
    parse_csv = preview_csv
    preview = preview_csv

    def commit_csv(
        self,
        csv_input: str | bytes | TextIO,
        vertical_pack: str | VerticalPack = "one_trade_network.v1",
    ) -> list[ProspectRecord]:
        return self.preview_csv(csv_input, vertical_pack).valid_prospects

    def deduplicate(self, records: Iterable[ProspectRecord]) -> list[ProspectRecord]:
        """Keep the first normalized domain per vertical, preserving input order."""

        result: list[ProspectRecord] = []
        seen: set[tuple[str, str]] = set()
        for record in records:
            key = (record.vertical_id or record.vertical_pack_version.split(".", 1)[0], record.normalized_domain)
            if not key[1] or key in seen:
                continue
            seen.add(key)
            result.append(record)
        return result

    def qualify(
        self,
        record: ProspectRecord,
        vertical_pack: str | VerticalPack,
        *,
        row_number: int = 0,
    ) -> tuple[ProspectRecord, list[ProspectRowIssue]]:
        pack = self._resolve_pack(vertical_pack)
        reasons: list[str] = []
        issues: list[ProspectRowIssue] = []
        normalized_url, normalized_domain = self.normalize_website(record.website_url)
        if not normalized_url:
            reasons.append("website_url is missing or invalid")
            issues.append(ProspectRowIssue(row_number, "website_url", reasons[-1], record.website_url))

        for field_name in pack.required_fields:
            value = getattr(record, field_name, "")
            if not isinstance(value, str) or not value.strip():
                reason = f"{field_name} is required"
                if reason not in reasons:
                    reasons.append(reason)
                    issues.append(ProspectRowIssue(row_number, field_name, reason, value))

        category = self.normalize_category(record.category)
        allowed = {self.normalize_category(item) for item in pack.allowed_business_categories}
        status = "qualified"
        if category and category not in allowed:
            status = str(pack.qualification_rules.get("unknown_category_status", "needs_review"))
            reason = f"category {record.category!r} is not in the vertical pack"
            reasons.append(reason)
            issues.append(ProspectRowIssue(row_number, "category", reason, record.category, "warning"))
        if reasons and any(issue.severity == "error" for issue in issues):
            status = "rejected"
        updated = replace(
            record,
            website_url=normalized_url or record.website_url.strip(),
            normalized_domain=normalized_domain,
            category=category,
            vertical_id=pack.vertical_id,
            vertical_pack_version=pack.pack_id,
            qualification_status=status,
            rejection_reasons=reasons,
        )
        return updated, issues

    @staticmethod
    def normalize_website(value: str | None) -> tuple[str, str]:
        if not isinstance(value, str) or not value.strip():
            return "", ""
        candidate = value.strip()
        if "://" not in candidate:
            candidate = f"https://{candidate}"
        try:
            parsed = urlsplit(candidate)
        except ValueError:
            return "", ""
        hostname = parsed.hostname
        if parsed.scheme.lower() not in {"http", "https"} or not hostname or "." not in hostname:
            return "", ""
        domain = hostname.rstrip(".").lower()
        if domain.startswith("www."):
            domain = domain[4:]
        path = parsed.path or "/"
        normalized_url = urlunsplit((parsed.scheme.lower(), domain, path, parsed.query, ""))
        return normalized_url, domain

    @staticmethod
    def normalize_category(value: str | None) -> str:
        if not isinstance(value, str):
            return ""
        return re.sub(r"\s+", " ", value.strip().lower().replace("&", "and")).strip()

    def _resolve_pack(self, value: str | VerticalPack) -> VerticalPack:
        if isinstance(value, VerticalPack):
            return value
        if value in self._packs:
            return self._packs[value]
        return resolve_vertical_pack(value)

    @staticmethod
    def _read_text(csv_input: str | bytes | TextIO) -> str:
        if isinstance(csv_input, bytes):
            return csv_input.decode("utf-8-sig")
        if isinstance(csv_input, str):
            return csv_input
        return csv_input.read()

    @classmethod
    def _header_key(cls, value: str) -> str:
        return re.sub(r"[^a-z0-9]+", "_", value.strip().lower()).strip("_")

    @classmethod
    def _canonical_row(cls, row: Mapping[str | None, Any], headers: Mapping[str, str]) -> dict[str, str]:
        normalized = {cls._header_key(str(key)): (str(value).strip() if value is not None else "") for key, value in row.items() if key is not None}
        result: dict[str, str] = {}
        for field_name, aliases in _ALIASES.items():
            for alias in aliases:
                if alias in normalized:
                    result[field_name] = normalized[alias]
                    break
            result.setdefault(field_name, "")
        return result

    @staticmethod
    def _record_from_row(values: Mapping[str, str], pack: VerticalPack, row_number: int) -> ProspectRecord:
        return ProspectRecord(
            business_name=values.get("business_name", ""),
            website_url=values.get("website_url", ""),
            category=values.get("category", ""),
            location=values.get("location", ""),
            contact_route=values.get("contact_route", ""),
            source_provenance=values.get("source_provenance", ""),
            vertical_id=pack.vertical_id,
            vertical_pack_version=pack.pack_id,
            metadata={"source_row": row_number},
        )

