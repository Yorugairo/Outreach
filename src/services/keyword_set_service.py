"""Versioned, factual-risk-aware keyword research intake."""

from __future__ import annotations

import csv
import hashlib
import io
import re
from collections import Counter
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Any, TextIO

from src.models import KeywordSet, KeywordSetBinding, KeywordTarget, utc_now_iso
from src.repositories.base import InsightRepository


TACOMA_BJJ_KEYWORD_SET_KEY = "national_bjj_registry.tacoma.v1"
TACOMA_LOCATION_CODE = 1027773
EXPECTED_CATEGORIES = (
    "Primary Local Core",
    "Kids & Family",
    "Beginner & Safety",
    "Specialty Programs",
    "Lineage & Authority",
    "Hyper-Local Geo",
)
EXPECTED_CATEGORY_COUNTS = {
    "Primary Local Core": 10,
    "Kids & Family": 10,
    "Beginner & Safety": 10,
    "Specialty Programs": 10,
    "Lineage & Authority": 5,
    "Hyper-Local Geo": 5,
}
PILOT_SUGGESTIONS = {
    "Primary Local Core": ("bjj tacoma", "bjj gym near me tacoma"),
    "Kids & Family": ("kids bjj tacoma", "kids martial arts eastside tacoma"),
    "Beginner & Safety": ("beginner bjj classes tacoma", "safe jiu jitsu training tacoma"),
    "Specialty Programs": ("no gi bjj tacoma", "women self defense classes tacoma"),
    "Lineage & Authority": ("nova ryu bjj tacoma", "james foster bjj lineage tacoma"),
    "Hyper-Local Geo": ("bjj portland ave tacoma wa", "eastside tacoma martial arts"),
}
REQUIRED_HEADERS = (
    "Keyword",
    "Category",
    "Search Intent",
    "Optimization Focus",
    "Target Page / Usage",
)


@dataclass(slots=True)
class KeywordImportIssue:
    row_number: int
    field: str
    message: str
    severity: str = "error"
    value: Any = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class KeywordImportPreview:
    source_sha256: str
    rows_seen: int
    keyword_targets: list[KeywordTarget]
    issues: list[KeywordImportIssue]
    category_counts: dict[str, int]

    @property
    def errors(self) -> list[KeywordImportIssue]:
        return [issue for issue in self.issues if issue.severity == "error"]

    @property
    def valid(self) -> bool:
        return bool(self.keyword_targets) and not self.errors

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_sha256": self.source_sha256,
            "rows_seen": self.rows_seen,
            "keyword_targets": [target.to_dict() for target in self.keyword_targets],
            "issues": [issue.to_dict() for issue in self.issues],
            "category_counts": dict(self.category_counts),
            "valid": self.valid,
        }


class KeywordSetService:
    """Preview, version, approve, bind, and deterministically sample keyword sets."""

    def __init__(self, repository: InsightRepository | None = None) -> None:
        self.repository = repository

    def preview_csv(self, csv_input: str | bytes | TextIO) -> KeywordImportPreview:
        text = self._read_text(csv_input)
        source_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
        reader = csv.DictReader(io.StringIO(text))
        issues: list[KeywordImportIssue] = []
        if not reader.fieldnames:
            return KeywordImportPreview(source_hash, 0, [], [KeywordImportIssue(1, "header", "CSV header is required")], {})
        missing = [header for header in REQUIRED_HEADERS if header not in reader.fieldnames]
        if missing:
            issues.append(KeywordImportIssue(1, "header", f"missing required columns: {', '.join(missing)}"))
            return KeywordImportPreview(source_hash, 0, [], issues, {})

        targets: list[KeywordTarget] = []
        seen: set[str] = set()
        rows_seen = 0
        for row_number, row in enumerate(reader, start=2):
            rows_seen += 1
            values = {key: " ".join(str(row.get(key) or "").split()) for key in REQUIRED_HEADERS}
            keyword = values["Keyword"]
            normalized = self.normalize_keyword(keyword)
            if not all(values.values()):
                missing_fields = [key for key, value in values.items() if not value]
                issues.append(
                    KeywordImportIssue(
                        row_number,
                        ",".join(missing_fields),
                        "keyword rows require every source field",
                    )
                )
                continue
            if normalized in seen:
                issues.append(KeywordImportIssue(row_number, "Keyword", "duplicate normalized keyword", value=keyword))
                continue
            seen.add(normalized)
            reasons = self._review_reasons(values)
            target = KeywordTarget(
                keyword=keyword,
                category=values["Category"],
                search_intent=values["Search Intent"],
                optimization_focus=values["Optimization Focus"],
                target_page_usage=values["Target Page / Usage"],
                review_status="needs_review" if reasons else "approved",
                review_reasons=reasons,
                source_row=row_number,
                local_intent=self._is_local_intent(values),
            )
            targets.append(target)

        counts = dict(Counter(target.category for target in targets))
        unexpected = sorted(set(counts) - set(EXPECTED_CATEGORIES))
        for category in unexpected:
            issues.append(KeywordImportIssue(1, "Category", f"unsupported category: {category}", value=category))
        return KeywordImportPreview(source_hash, rows_seen, targets, issues, counts)

    def commit(
        self,
        preview: KeywordImportPreview,
        *,
        vertical_id: str,
        market: str,
        market_slug: str,
        location_code: int,
        version: str,
        normalized_domain: str | None = None,
        scope_type: str = "vertical",
        scope_id: str | None = None,
        source_provenance: str = "csv_import",
    ) -> KeywordSet:
        if not preview.valid:
            raise ValueError("keyword CSV preview contains errors")
        keyword_set = KeywordSet(
            vertical_id=vertical_id,
            market=market,
            market_slug=market_slug,
            location_code=location_code,
            version=version,
            source_sha256=preview.source_sha256,
            keyword_targets=[target.to_dict() for target in preview.keyword_targets],
            normalized_domain=normalized_domain,
            scope_type=scope_type,
            scope_id=scope_id,
            source_provenance=source_provenance,
        )
        if self.repository is not None:
            return self.repository.save_keyword_set(keyword_set)
        return keyword_set

    def seed_tacoma_bjj(
        self,
        *,
        normalized_domain: str = "novaryu.com",
        source_path: str | Path | None = None,
    ) -> KeywordSet:
        path = Path(source_path) if source_path else Path(__file__).resolve().parents[1] / "data" / "national_bjj_registry_tacoma_v1.csv"
        preview = self.preview_csv(path.read_text(encoding="utf-8-sig"))
        if preview.rows_seen != 50 or preview.category_counts != EXPECTED_CATEGORY_COUNTS:
            raise ValueError("Tacoma BJJ seed must contain the reviewed 50-keyword category distribution")
        return self.commit(
            preview,
            vertical_id="national_bjj_registry",
            market="Tacoma, WA",
            market_slug="tacoma",
            location_code=TACOMA_LOCATION_CODE,
            version="v1",
            normalized_domain=normalized_domain,
            scope_type="domain",
            scope_id=normalized_domain,
            source_provenance="bundled:national_bjj_registry_tacoma_v1.csv",
        )

    def review_targets(
        self,
        keyword_set: KeywordSet,
        *,
        approved_keywords: list[str] | None = None,
        rejected_keywords: list[str] | None = None,
    ) -> KeywordSet:
        if keyword_set.state != "draft":
            raise ValueError("only draft keyword sets may be reviewed")
        approved = {self.normalize_keyword(value) for value in approved_keywords or []}
        rejected = {self.normalize_keyword(value) for value in rejected_keywords or []}
        if approved & rejected:
            raise ValueError("a keyword cannot be both approved and rejected")
        updated_targets: list[dict[str, Any]] = []
        for target in keyword_set.targets():
            normalized = target.normalized_keyword
            if normalized in approved:
                target.review_status = "approved"
                target.review_reasons = []
            elif normalized in rejected:
                target.review_status = "rejected"
            updated_targets.append(target.to_dict())
        return replace(keyword_set, keyword_targets=updated_targets, updated_at=utc_now_iso())

    def approve(self, keyword_set: KeywordSet, *, operator: str) -> KeywordSet:
        if keyword_set.state != "draft":
            raise ValueError("only draft keyword sets may be approved")
        if not operator.strip():
            raise ValueError("keyword set approval requires an operator")
        approved = replace(
            keyword_set,
            state="approved",
            approved_by=operator.strip(),
            approved_at=utc_now_iso(),
            updated_at=utc_now_iso(),
        )
        if self.repository is not None:
            return self.repository.save_keyword_set(approved)
        return approved

    def supersede(self, keyword_set: KeywordSet, *, successor_id: str) -> KeywordSet:
        if keyword_set.state != "approved":
            raise ValueError("only approved keyword sets may be superseded")
        if not successor_id.strip() or successor_id == keyword_set.id:
            raise ValueError("supersession requires a distinct successor keyword set")
        if self.repository is not None:
            successor = self.repository.get_keyword_set(successor_id)
            if successor is None or successor.state != "approved":
                raise ValueError("successor keyword set must exist and be approved")
            if successor.vertical_id != keyword_set.vertical_id:
                raise ValueError("successor keyword set must use the same vertical")
        superseded = replace(
            keyword_set,
            state="superseded",
            superseded_by_id=successor_id,
            updated_at=utc_now_iso(),
        )
        if self.repository is not None:
            return self.repository.save_keyword_set(superseded)
        return superseded

    def resolve_for_domain(self, normalized_domain: str) -> KeywordSet | None:
        if self.repository is None:
            raise ValueError("domain resolution requires a repository")
        domain = normalized_domain.casefold().removeprefix("www.")
        bindings = self.repository.list_keyword_set_bindings(
            normalized_domain=domain,
            state="active",
            limit=10,
        )
        for binding in bindings:
            keyword_set = self.repository.get_keyword_set(binding.keyword_set_id)
            if keyword_set is not None and keyword_set.state == "approved":
                return keyword_set
        records = self.repository.list_keyword_sets(normalized_domain=domain, state="approved")
        return records[0] if records else None

    def bind(
        self,
        keyword_set: KeywordSet,
        *,
        normalized_domain: str,
        operator: str,
        prospect_id: str | None = None,
    ) -> KeywordSetBinding:
        if self.repository is None:
            raise ValueError("keyword-set binding requires a repository")
        if keyword_set.state != "approved":
            raise ValueError("only approved keyword sets may be bound")
        domain = normalized_domain.strip().casefold().removeprefix("www.")
        if not domain or "." not in domain:
            raise ValueError("keyword-set binding requires a normalized domain")
        return self.repository.save_keyword_set_binding(KeywordSetBinding(
            keyword_set_id=keyword_set.id,
            vertical_id=keyword_set.vertical_id,
            normalized_domain=domain,
            prospect_id=prospect_id,
            operator=operator.strip(),
        ))

    def select_pilot(self, keyword_set: KeywordSet) -> list[KeywordTarget]:
        if keyword_set.state != "approved":
            raise ValueError("pilot selection requires an approved keyword set")
        selected: list[KeywordTarget] = []
        targets = keyword_set.targets()
        for category in EXPECTED_CATEGORIES:
            approved = [target for target in targets if target.category == category and target.review_status == "approved"]
            if len(approved) < 2:
                raise ValueError(f"category {category} has fewer than two approved keywords")
            by_keyword = {target.normalized_keyword: target for target in approved}
            category_selection: list[KeywordTarget] = []
            for suggestion in PILOT_SUGGESTIONS[category]:
                candidate = by_keyword.get(self.normalize_keyword(suggestion))
                if candidate is not None and candidate not in category_selection:
                    category_selection.append(candidate)
            for candidate in approved:
                if len(category_selection) >= 2:
                    break
                if candidate not in category_selection:
                    category_selection.append(candidate)
            for candidate in category_selection[:2]:
                candidate.pilot_selected = True
                selected.append(candidate)
        if len(selected) != 12:
            raise AssertionError("pilot selection must contain exactly 12 approved keywords")
        return selected

    @staticmethod
    def normalize_keyword(value: str) -> str:
        return " ".join(value.casefold().split())

    @staticmethod
    def _read_text(csv_input: str | bytes | TextIO) -> str:
        if isinstance(csv_input, bytes):
            return csv_input.decode("utf-8-sig")
        if isinstance(csv_input, str):
            return csv_input.lstrip("\ufeff")
        return csv_input.read().lstrip("\ufeff")

    @classmethod
    def _review_reasons(cls, values: dict[str, str]) -> list[str]:
        text = " ".join(
            (
                values["Keyword"],
                values["Search Intent"],
                values["Optimization Focus"],
                values["Target Page / Usage"],
            )
        ).casefold()
        reasons: list[str] = []
        if re.search(r"\b(judo|boxing|no[- ]?gi|open mat|women self defense|ninja cubs)\b", text):
            reasons.append("unsupported_program_claim")
        if re.search(r"\b(nurse practitioner|sports medicine|black belt)\b", text):
            reasons.append("credential_claim")
        if re.search(r"\b(james foster|jestyn cummings|foster bjj)\b", text):
            reasons.append("person_or_lineage_claim")
        if "3912 e portland ave" in text:
            reasons.append("exact_address_claim")
        if "lineage" in text:
            reasons.append("lineage_claim")
        return sorted(set(reasons))

    @staticmethod
    def _is_local_intent(values: dict[str, str]) -> bool:
        keyword = values["Keyword"].casefold()
        intent = values["Search Intent"].casefold()
        return (
            "local" in intent
            or "near me" in keyword
            or "portland ave" in keyword
            or "eastside tacoma" in keyword
            or bool(re.search(r"\b\d{3,}\b", keyword))
        )
