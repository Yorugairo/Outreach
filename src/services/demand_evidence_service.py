"""Operator demand evidence intake and conservative de-duplication.

The service is deliberately deterministic.  A keyword-tool row is a search
occasion, not a person, and rows only enter arithmetic through a reviewed
``DemandGroup``.  The repository is optional for previews, but commits and
state transitions use the repository's immutable demand-evidence contract.
"""

from __future__ import annotations

import csv
import hashlib
import io
import math
import re
from collections import defaultdict
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Any, Iterable, Mapping, TextIO

from src.models import DemandEvidenceRow, DemandEvidenceSet, DemandGroup, KeywordSet, utc_now_iso
from src.repositories.base import InsightRepository


MAX_CSV_BYTES = 5 * 1024 * 1024
MAX_CSV_ROWS = 10_000
MAX_CSV_COLUMNS = 100
MAX_MONTHLY_SEARCHES = 1_000_000_000.0

_PII_HEADER_RE = re.compile(
    r"(?:e[-_ ]?mail|phone|mobile|first[ _-]?name|last[ _-]?name|full[ _-]?name|"
    r"contact|street[ _-]?address|postal[ _-]?address|customer|lead[ _-]?id|user[ _-]?id|"
    r"(?:^|[_\s-])name(?:$|[_\s-]))",
    re.IGNORECASE,
)
_FORMULA_RE = re.compile(r"^[=+\-@]")
_UNIQUE_PERSON_CLAIM_RE = re.compile(
    r"\bunique\s+(?:people|person|searchers|searcher|users|user|persons|individuals)\b",
    re.IGNORECASE,
)


@dataclass(slots=True)
class DemandImportIssue:
    row_number: int
    field: str
    message: str
    severity: str = "error"
    value: Any = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class DemandEvidencePreview:
    source_sha256: str
    rows_seen: int
    demand_rows: list[DemandEvidenceRow]
    groups: list[DemandGroup]
    issues: list[DemandImportIssue]
    source: str = "operator_csv"
    market: str = ""
    snapshot_period: str = ""
    location_code: int | None = None

    @property
    def rows(self) -> list[DemandEvidenceRow]:
        """Compatibility alias for callers using the model field name."""
        return self.demand_rows

    @property
    def errors(self) -> list[DemandImportIssue]:
        return [issue for issue in self.issues if issue.severity == "error"]

    @property
    def valid(self) -> bool:
        return bool(self.demand_rows) and not self.errors

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_sha256": self.source_sha256,
            "rows_seen": self.rows_seen,
            "demand_rows": [row.to_dict() for row in self.demand_rows],
            "rows": [row.to_dict() for row in self.demand_rows],
            "groups": [group.to_dict() for group in self.groups],
            "issues": [issue.to_dict() for issue in self.issues],
            "source": self.source,
            "market": self.market,
            "snapshot_period": self.snapshot_period,
            "location_code": self.location_code,
            "valid": self.valid,
        }


class DemandEvidenceService:
    """Preview, commit, review, approve, and correct demand evidence."""

    _ALIASES: dict[str, set[str]] = {
        "keyword": {"keyword", "keyword idea", "term", "search keyword", "search term", "query"},
        "monthly_searches": {
            "avg monthly searches", "average monthly searches", "monthly searches",
            "avg monthly search", "average monthly search", "search volume", "volume",
        },
        "category": {"category", "keyword category", "ad group"},
        "search_intent": {"search intent", "intent", "intent family"},
        "target_page": {"target page usage", "target page", "landing page", "page"},
        "match_semantics": {"match semantics", "match type", "keyword match type"},
        "brand": {"brand", "brand demand", "brand/non brand", "brand non brand"},
        "supported": {"supported", "eligible", "approved"},
        "market": {"market", "location", "geo", "target location"},
        "snapshot_period": {"snapshot period", "period", "month", "date"},
        "target_id": {"keyword set target id", "target id", "keyword target id"},
        "grouped_volume": {"provider grouped volume", "grouped volume", "group volume"},
    }

    # These substitutions are intentionally small.  They make reordered
    # phrases and the common BJJ spelling variants resolve to one stable
    # close-variant signature without pretending that every related phrase is
    # the same search intent.  Category, intent, target-page, and brand
    # boundaries remain the primary grouping keys below.
    _CLOSE_VARIANT_PHRASES: tuple[tuple[tuple[str, ...], str], ...] = (
        (("brazilian", "jiu", "jitsu"), "bjj"),
        (("jiu", "jitsu"), "bjj"),
        (("jiu-jitsu",), "bjj"),
        (("jiujitsu",), "bjj"),
    )
    _CLOSE_VARIANT_STOPWORDS = {
        "a", "an", "the", "for", "in", "of", "to", "near", "me",
        "class", "classes", "lesson", "lessons", "training", "program",
        "programs", "gym", "academy", "school",
    }

    def __init__(self, repository: InsightRepository | None = None) -> None:
        self.repository = repository

    def preview_csv(
        self,
        csv_input: str | bytes | TextIO,
        *,
        market: str = "",
        source: str = "operator_csv",
        snapshot_period: str = "",
        location_code: int | None = None,
        keyword_set: KeywordSet | None = None,
        brand_terms: list[str] | tuple[str, ...] = (),
        aggregation_rule: str = "max_close_variant",
    ) -> DemandEvidencePreview:
        """Parse a bounded Keyword Planner-style export without executing cells."""
        if aggregation_rule not in {"provider_grouped", "max_close_variant", "sum_distinct_intents"}:
            raise ValueError(f"unsupported demand aggregation rule: {aggregation_rule}")
        if aggregation_rule == "sum_distinct_intents":
            raise ValueError("sum_distinct_intents requires explicit operator review; preview with max_close_variant first")
        text = self._read_text(csv_input)
        source_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
        issues: list[DemandImportIssue] = []
        if _UNIQUE_PERSON_CLAIM_RE.search(text):
            issues.append(
                DemandImportIssue(
                    1,
                    "csv",
                    "keyword observations cannot be represented as unique-person counts",
                )
            )
        if not text.strip():
            return DemandEvidencePreview(source_hash, 0, [], [], [DemandImportIssue(1, "csv", "CSV is empty")], source, market, snapshot_period, location_code)
        if "\x00" in text:
            return DemandEvidencePreview(source_hash, 0, [], [], [DemandImportIssue(1, "csv", "CSV contains a NUL byte")], source, market, snapshot_period, location_code)

        try:
            reader = csv.DictReader(io.StringIO(text, newline=""))
            headers = reader.fieldnames or []
        except csv.Error as exc:
            return DemandEvidencePreview(source_hash, 0, [], [], [DemandImportIssue(1, "csv", f"invalid CSV: {exc}")], source, market, snapshot_period, location_code)
        if not headers:
            return DemandEvidencePreview(source_hash, 0, [], [], [DemandImportIssue(1, "header", "CSV header is required")], source, market, snapshot_period, location_code)
        if len(headers) > MAX_CSV_COLUMNS:
            issues.append(DemandImportIssue(1, "header", f"CSV exceeds {MAX_CSV_COLUMNS} columns"))
        pii_headers = [header for header in headers if _PII_HEADER_RE.search(str(header or ""))]
        if pii_headers:
            issues.append(DemandImportIssue(1, "header", "PII columns are not accepted", value=pii_headers))
        canonical = self._canonical_headers(headers, issues)
        if "keyword" not in canonical:
            issues.append(DemandImportIssue(1, "Keyword", "missing required keyword column"))
        if "monthly_searches" not in canonical:
            issues.append(DemandImportIssue(1, "Avg. monthly searches", "missing required monthly-searches column"))
        # Continue parsing when an unsafe optional column is present so the
        # operator receives row-level errors as well as the PII header error.
        # Missing required columns, however, make row parsing meaningless.
        if any(
            issue.row_number == 1
            and issue.field in {"Keyword", "Avg. monthly searches"}
            and issue.severity == "error"
            for issue in issues
        ):
            return DemandEvidencePreview(source_hash, 0, [], [], issues, source, market, snapshot_period, location_code)

        targets_by_keyword: dict[str, Any] = {}
        if keyword_set is not None:
            targets_by_keyword = {target.normalized_keyword: target for target in keyword_set.targets()}
        known_brand_terms = {self.normalize_keyword(term) for term in brand_terms if str(term).strip()}
        rows: list[DemandEvidenceRow] = []
        seen: set[str] = set()
        rows_seen = 0
        for row_number, raw in enumerate(reader, start=2):
            rows_seen += 1
            if rows_seen > MAX_CSV_ROWS:
                issues.append(DemandImportIssue(row_number, "csv", f"CSV exceeds {MAX_CSV_ROWS} rows"))
                break
            row = {key: self._clean(raw.get(header, "")) for key, header in canonical.items()}
            raw_values = [self._clean(value) for value in raw.values() if value is not None]
            keyword = row.get("keyword", "")
            normalized = self.normalize_keyword(keyword)
            if not keyword:
                issues.append(DemandImportIssue(row_number, "Keyword", "keyword is required"))
                continue
            if normalized in seen:
                issues.append(DemandImportIssue(row_number, "Keyword", "duplicate normalized keyword", value=keyword))
                continue
            seen.add(normalized)
            formula_fields = [field for field, value in row.items() if value and _FORMULA_RE.match(value)]
            if any(_FORMULA_RE.match(value) for value in raw_values):
                formula_fields.append("csv_cell")
            if formula_fields:
                issues.append(DemandImportIssue(row_number, ",".join(formula_fields), "formula-like CSV cells are not accepted"))
                continue
            volume_field = "monthly_searches"
            volume_raw = row.get("monthly_searches", "")
            if aggregation_rule == "provider_grouped" and row.get("grouped_volume"):
                volume_field = "grouped_volume"
                volume_raw = row.get("grouped_volume", "")
            try:
                volume = self._parse_volume(volume_raw)
            except ValueError as exc:
                issues.append(DemandImportIssue(row_number, volume_field, str(exc), value=volume_raw))
                continue
            target = targets_by_keyword.get(normalized)
            category = row.get("category") or (target.category if target else "Uncategorized")
            intent = row.get("search_intent") or (target.search_intent if target else "unknown")
            target_page = row.get("target_page") or (target.target_page_usage if target else "unknown")
            row_market = row.get("market") or market or "unknown"
            row_period = row.get("snapshot_period") or snapshot_period or "unspecified"
            semantics = row.get("match_semantics") or "close_variants"
            target_id = row.get("target_id") or (target.id if target else None)
            if keyword_set is not None and target is None:
                issues.append(DemandImportIssue(row_number, "Keyword", "keyword is not present in the bound keyword set", value=keyword))
                continue
            if target_id and keyword_set is not None and target is not None and target.id != target_id:
                issues.append(DemandImportIssue(row_number, "Keyword Set Target ID", "target id does not match keyword", value=target_id))
                continue
            supported = self._parse_bool(row.get("supported"), default=True)
            if target is not None and target.review_status != "approved":
                # A factual-risk keyword remains operator-reviewable, but it
                # must not enter demand arithmetic until the target itself is
                # approved.  Preserve the row for the review surface and mark
                # it unsupported so grouping excludes it safely.
                supported = False
                issues.append(
                    DemandImportIssue(
                        row_number,
                        "Keyword",
                        "keyword target requires factual review; excluded from demand groups",
                        severity="warning",
                        value={"keyword": keyword, "review_reasons": list(target.review_reasons)},
                    )
                )
            brand = self._parse_bool(row.get("brand"), default=False)
            if not brand:
                text_for_brand = f"{category} {intent} {keyword}".casefold()
                is_nonbrand = bool(re.search(r"\bnon[- ]?brand\b", text_for_brand))
                brand = not is_nonbrand and (
                    "brand" in text_for_brand
                    or "lineage" in text_for_brand
                    or "authority" in text_for_brand
                    or normalized in known_brand_terms
                )
            evidence_ref = {
                "source": source,
                "source_sha256": source_hash,
                "csv_row": row_number,
                "category": category,
                "search_intent": intent,
                "target_page_usage": target_page,
                "intent_family": self.intent_family_key(
                    category=category,
                    search_intent=intent,
                    target_page=target_page,
                    brand=brand,
                ),
                "close_variant_signature": self.close_variant_signature(keyword),
            }
            rows.append(DemandEvidenceRow(
                keyword=keyword,
                normalized_keyword=normalized,
                keyword_set_target_id=target_id,
                market=row_market,
                source=source,
                snapshot_period=row_period,
                match_semantics=semantics,
                location_code=location_code,
                monthly_searches=volume,
                source_row=row_number,
                evidence_ref=evidence_ref,
                brand_demand=brand,
                supported=supported,
            ))
        groups = self.group_rows(rows, aggregation_rule=aggregation_rule)
        return DemandEvidencePreview(source_hash, rows_seen, rows, groups, issues, source, market, snapshot_period, location_code)

    def group_rows(self, rows: list[DemandEvidenceRow], *, aggregation_rule: str = "max_close_variant") -> list[DemandGroup]:
        if aggregation_rule not in {"provider_grouped", "max_close_variant", "sum_distinct_intents"}:
            raise ValueError(f"unsupported demand aggregation rule: {aggregation_rule}")
        buckets: dict[tuple[str, str, str, bool], list[DemandEvidenceRow]] = defaultdict(list)
        for row in rows:
            if not row.supported or row.monthly_searches is None:
                continue
            ref = row.evidence_ref or {}
            category = self.normalize_keyword(str(ref.get("category", "uncategorized")))
            intent = self.normalize_keyword(str(ref.get("search_intent", "unknown")))
            page = self.normalize_keyword(str(ref.get("target_page_usage", "unknown")))
            buckets[(category, intent, page, row.brand_demand)].append(row)
        groups: list[DemandGroup] = []
        for key in sorted(buckets):
            category, intent, page, is_brand = key
            candidates = sorted(
                buckets[key],
                key=lambda row: (
                    -float(row.monthly_searches or 0),
                    row.normalized_keyword,
                    row.source_row if row.source_row is not None else 10**9,
                    row.id,
                ),
            )
            representative = candidates[0]
            # A group claims one representative row for arithmetic.  The
            # remaining close variants are explicitly recorded as excluded
            # duplicates; DemandGroup requires these sets to be disjoint.
            included = [representative.id]
            excluded = [row.id for row in candidates[1:]]
            if aggregation_rule == "provider_grouped":
                approved_volume = float(representative.monthly_searches or 0)
            elif aggregation_rule == "sum_distinct_intents":
                # Model validation still requires operator approval for this rule.
                approved_volume = sum(float(row.monthly_searches or 0) for row in candidates)
            else:
                approved_volume = float(representative.monthly_searches or 0)
            group_key = "|".join(
                (
                    category,
                    intent,
                    page,
                    "brand" if is_brand else "non_brand",
                    aggregation_rule,
                    ",".join(sorted(row.normalized_keyword for row in candidates)),
                )
            )
            groups.append(DemandGroup(
                intent_family=f"{category}|{intent}|{page}",
                included_keyword_ids=included,
                excluded_duplicate_ids=excluded,
                representative_term=representative.keyword,
                aggregation_rule=aggregation_rule,
                approved_monthly_search_occasions=approved_volume,
                id="group-" + hashlib.sha256(group_key.encode("utf-8")).hexdigest()[:24],
                rationale="deterministic category/intent/target-page grouping",
                is_brand=is_brand,
            ))
        return groups

    def commit(
        self,
        preview: DemandEvidencePreview,
        *,
        prospect_id: str,
        keyword_set_id: str,
        vertical_id: str | None = None,
        market: str | None = None,
        location_code: int | None = None,
        source: str | None = None,
        snapshot_period: str | None = None,
    ) -> DemandEvidenceSet:
        if not preview.valid:
            raise ValueError("demand CSV preview contains errors or no rows")
        self._validate_binding(prospect_id, keyword_set_id, vertical_id=vertical_id)
        keyword_set = self.repository.get_keyword_set(keyword_set_id) if self.repository is not None else None
        resolved_vertical = vertical_id or (keyword_set.vertical_id if keyword_set is not None else "unknown")
        evidence = DemandEvidenceSet(
            prospect_id=prospect_id,
            keyword_set_id=keyword_set_id,
            vertical_id=resolved_vertical,
            market=market or preview.market or (keyword_set.market if keyword_set is not None else "unknown"),
            source_sha256=preview.source_sha256,
            rows=[row.to_dict() for row in preview.demand_rows],
            groups=[group.to_dict() for group in preview.groups],
            location_code=location_code if location_code is not None else preview.location_code,
            source=source or preview.source,
            snapshot_period=snapshot_period or preview.snapshot_period or "unspecified",
        )
        return self.repository.save_demand_evidence_set(evidence) if self.repository is not None else evidence

    def review_groups(
        self,
        evidence: DemandEvidenceSet,
        *,
        reviewer: str,
        group_updates: Mapping[str, Mapping[str, Any]] | list[Mapping[str, Any]] | None = None,
    ) -> DemandEvidenceSet:
        if evidence.state not in {"draft", "review"}:
            raise ValueError("only draft or review demand evidence may be reviewed")
        if not reviewer.strip():
            raise ValueError("demand review requires an operator")
        updates: dict[str, Mapping[str, Any]] = {}
        if isinstance(group_updates, Mapping):
            updates = {str(key): value for key, value in group_updates.items()}
        elif group_updates is not None:
            updates = {str(item.get("id")): item for item in group_updates if item.get("id")}
        groups: list[DemandGroup] = []
        for payload in evidence.groups:
            group = DemandGroup(**payload)
            update = updates.get(group.id)
            if update:
                allowed = {key: value for key, value in update.items() if key not in {"id"}}
                group = replace(group, **allowed)
            if group.status == "approved" and not group.reviewer:
                group = replace(group, reviewer=reviewer.strip())
            groups.append(group)
        successor = replace(
            evidence,
            id=self._new_id(),
            version=evidence.version + 1,
            predecessor_id=evidence.id,
            groups=[group.to_dict() for group in groups],
            state="review",
            approved_by=None,
            approved_at=None,
        )
        return self.repository.save_demand_evidence_set(successor) if self.repository is not None else successor

    review = review_groups

    def approve(self, evidence: DemandEvidenceSet, *, operator: str) -> DemandEvidenceSet:
        if evidence.state not in {"draft", "review"}:
            raise ValueError("only draft or review demand evidence may be approved")
        if not operator.strip() or not evidence.groups:
            raise ValueError("approved demand evidence requires reviewed groups and an operator")
        groups = [DemandGroup(**payload) for payload in evidence.groups]
        if any(group.status != "approved" for group in groups):
            raise ValueError("all demand groups must be approved before evidence approval")
        approved = replace(
            evidence,
            id=self._new_id(),
            version=evidence.version + 1,
            predecessor_id=evidence.id,
            state="approved",
            approved_by=operator.strip(),
            approved_at=utc_now_iso(),
        )
        return self.repository.save_demand_evidence_set(approved) if self.repository is not None else approved

    def correct(
        self,
        evidence: DemandEvidenceSet,
        *,
        reviewer: str,
        group_updates: Mapping[str, Mapping[str, Any]] | list[Mapping[str, Any]] | None = None,
    ) -> DemandEvidenceSet:
        """Create an immutable successor for operator corrections."""
        return self.review_groups(evidence, reviewer=reviewer, group_updates=group_updates)

    def create_successor(self, evidence: DemandEvidenceSet, *, reviewer: str, groups: list[DemandGroup]) -> DemandEvidenceSet:
        return self.correct(evidence, reviewer=reviewer, group_updates={group.id: group.to_dict() for group in groups})

    def supersede(
        self,
        evidence: DemandEvidenceSet,
        *,
        successor: DemandEvidenceSet | None = None,
        successor_id: str | None = None,
    ) -> DemandEvidenceSet:
        """Validate/return an immutable successor created by ``correct``.

        Repositories intentionally do not rewrite the predecessor.  This
        helper therefore only validates attribution and persists a supplied
        successor when needed.
        """
        if successor is None and successor_id and self.repository is not None:
            successor = self.repository.get_demand_evidence_set(successor_id)
        if successor is None:
            raise ValueError("a demand-evidence successor is required")
        if successor.predecessor_id != evidence.id:
            raise ValueError("demand successor must reference its predecessor")
        if successor.id == evidence.id or successor.version <= evidence.version:
            raise ValueError("demand successor must have a new version")
        return successor

    def validate_binding(
        self,
        *,
        prospect_id: str,
        keyword_set_id: str,
        vertical_id: str | None = None,
    ) -> None:
        self._validate_binding(prospect_id, keyword_set_id, vertical_id=vertical_id)

    def cluster_intent_families(
        self,
        rows: Iterable[DemandEvidenceRow],
        *,
        aggregation_rule: str = "max_close_variant",
    ) -> list[DemandGroup]:
        """Return deterministic reviewed units for trend/planner consumers.

        This named seam keeps the existing ``group_rows`` behavior intact for
        demand evidence callers while making the intent-family contract
        explicit to additive trend ingestion.  Rows with the same approved
        category/intent/page/brand boundary are one family; close-variant
        rows are represented once using the maximum observed occasion count.
        """
        return self.group_rows(list(rows), aggregation_rule=aggregation_rule)

    # Compatibility names used by operator/import integrations.
    group_intent_families = cluster_intent_families
    cluster_rows = cluster_intent_families

    @classmethod
    def intent_family_key(
        cls,
        category: str,
        search_intent: str,
        target_page: str,
        brand: bool = False,
        include_brand: bool = False,
    ) -> str:
        """Build a stable, human-readable family boundary key."""
        base = "|".join(
            (
                cls.normalize_keyword(category) or "uncategorized",
                cls.normalize_keyword(search_intent) or "unknown",
                cls.normalize_keyword(target_page) or "unknown",
            )
        )
        # Existing demand artifacts use the three-part family key.  Callers
        # that need a brand-qualified key can opt in without changing that
        # contract; ``is_brand`` remains an independent group field.
        return f"{base}|{'brand' if brand else 'non_brand'}" if include_brand else base

    @classmethod
    def close_variant_signature(cls, value: str) -> str:
        """Normalize reordered/common-synonym phrases for deterministic review.

        The signature is evidence metadata only; it never creates an estimate
        by itself.  Arithmetic still occurs through one ``DemandGroup`` per
        category/intent/page/brand family.
        """
        normalized = cls.normalize_keyword(value)
        if not normalized:
            return ""
        tokens = re.findall(r"[a-z0-9]+", normalized.replace("-", " "))
        # Apply longer phrases first so ``brazilian jiu jitsu`` is not reduced
        # to a partially transformed token sequence.
        index = 0
        replaced: list[str] = []
        phrases = sorted(cls._CLOSE_VARIANT_PHRASES, key=lambda item: -len(item[0]))
        while index < len(tokens):
            replacement: str | None = None
            consumed = 0
            for phrase, value_for_phrase in phrases:
                if tuple(tokens[index : index + len(phrase)]) == phrase:
                    replacement = value_for_phrase
                    consumed = len(phrase)
                    break
            if replacement is not None:
                replaced.append(replacement)
                index += consumed
            else:
                replaced.append(tokens[index])
                index += 1
        filtered = [token for token in replaced if token not in cls._CLOSE_VARIANT_STOPWORDS]
        # Preserve meaningful ``no gi``/similar modifiers while making token
        # order deterministic for close variants.
        return " ".join(sorted(filtered))

    def _validate_binding(self, prospect_id: str, keyword_set_id: str, *, vertical_id: str | None) -> None:
        if not prospect_id.strip() or not keyword_set_id.strip():
            raise ValueError("demand evidence requires prospect and keyword-set identities")
        if self.repository is None:
            return
        prospect = self.repository.get_prospect(prospect_id)
        keyword_set = self.repository.get_keyword_set(keyword_set_id)
        if prospect is None:
            raise ValueError("demand evidence prospect does not exist")
        if keyword_set is None or keyword_set.state != "approved":
            raise ValueError("demand evidence requires an approved keyword set")
        if vertical_id and keyword_set.vertical_id != vertical_id:
            raise ValueError("demand evidence vertical does not match keyword set")
        if prospect.vertical_id and prospect.vertical_id != keyword_set.vertical_id:
            raise ValueError("demand evidence vertical does not match prospect")
        bindings = self.repository.list_keyword_set_bindings(keyword_set_id=keyword_set_id, prospect_id=prospect_id, state="active")
        if not bindings:
            raise ValueError("demand evidence requires an active prospect/keyword-set binding")

    @staticmethod
    def normalize_keyword(value: str) -> str:
        return " ".join(str(value).casefold().split())

    @staticmethod
    def _clean(value: Any) -> str:
        return " ".join(str(value or "").replace("\ufeff", "").split())

    @classmethod
    def _canonical_headers(cls, headers: list[str], issues: list[DemandImportIssue]) -> dict[str, str]:
        canonical: dict[str, str] = {}
        for header in headers:
            normalized = cls.normalize_keyword(re.sub(r"[^a-z0-9]+", " ", str(header).casefold()))
            match = next((name for name, aliases in cls._ALIASES.items() if normalized in aliases or normalized == name.replace("_", " ")), None)
            if match is None:
                continue
            if match in canonical:
                issues.append(DemandImportIssue(1, str(header), f"duplicate {match} column"))
                continue
            canonical[match] = header
        return canonical

    @staticmethod
    def _parse_volume(value: str) -> float:
        cleaned = value.replace(",", "").strip()
        if not cleaned or cleaned in {"-", "—", "n/a", "na", "none"}:
            raise ValueError("monthly search volume is required")
        try:
            number = float(cleaned)
        except ValueError as exc:
            raise ValueError("monthly search volume must be numeric") from exc
        if not math.isfinite(number) or number < 0:
            raise ValueError("monthly search volume must be a finite non-negative number")
        if number > MAX_MONTHLY_SEARCHES:
            raise ValueError("monthly search volume exceeds the safe maximum")
        return number

    @staticmethod
    def _parse_bool(value: str | None, *, default: bool) -> bool:
        if not value:
            return default
        lowered = value.casefold().strip()
        if lowered in {"true", "yes", "y", "1", "brand", "supported", "approved"}:
            return True
        if lowered in {"false", "no", "n", "0", "non-brand", "nonbrand", "unsupported", "rejected"}:
            return False
        return default

    @staticmethod
    def _read_text(csv_input: str | bytes | TextIO) -> str:
        if isinstance(csv_input, Path):
            raise ValueError("CSV paths are not accepted; upload CSV content")
        if isinstance(csv_input, bytes):
            if len(csv_input) > MAX_CSV_BYTES:
                raise ValueError(f"CSV exceeds {MAX_CSV_BYTES} bytes")
            try:
                return csv_input.decode("utf-8-sig")
            except UnicodeDecodeError as exc:
                raise ValueError("CSV must be UTF-8") from exc
        if isinstance(csv_input, str):
            if "\n" not in csv_input and "\r" not in csv_input and ("/" in csv_input or "\\" in csv_input):
                raise ValueError("CSV paths are not accepted; upload CSV content")
            text = csv_input.lstrip("\ufeff")
        else:
            text = csv_input.read().lstrip("\ufeff")
        if len(text.encode("utf-8")) > MAX_CSV_BYTES:
            raise ValueError(f"CSV exceeds {MAX_CSV_BYTES} bytes")
        return text

    @staticmethod
    def _new_id() -> str:
        # Keep UUID generation in one place while avoiding a mutable model copy.
        from uuid import uuid4

        return str(uuid4())


# Short name retained for integrations that mirror the service module name.
DemandEvidenceIntakeService = DemandEvidenceService
