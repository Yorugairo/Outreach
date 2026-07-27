"""Deterministic target-versus-approved-competitor opportunity analysis."""

from __future__ import annotations

from typing import Any
from urllib.parse import urlsplit

from src.models import MarketEvidenceRun, PageRecord


class GapAnalysisService:
    CLASS_WEIGHT = {
        "local_pack_gap": 8,
        "near_win": 7,
        "landing_page_gap": 6,
        "conversion_gap": 5,
        "authority_gap": 4,
        "improvement": 3,
        "not_observed_sample": 2,
    }

    def analyze(
        self,
        market_run: MarketEvidenceRun,
        *,
        target_pages: list[PageRecord],
        target_authority: dict[str, Any] | None,
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
        approved_domains = {
            self._domain(str(item.get("domain") or ""))
            for item in market_run.approved_competitors
            if item.get("domain")
        }
        competitor_evidence = {
            self._domain(str(item.get("domain") or "")): item
            for item in market_run.competitor_evidence
            if item.get("domain")
        }
        target_pages_by_url = {self._url_identity(page.url): page for page in target_pages}
        snapshots: dict[str, dict[str, Any]] = {}
        for source_type, source in (
            ("organic", market_run.organic_evidence),
            ("maps", market_run.maps_evidence),
        ):
            for index, item in enumerate(source):
                keyword = str(item.get("keyword") or "").strip()
                if not keyword:
                    continue
                group = snapshots.setdefault(keyword, {"organic": None, "maps": None})
                group[source_type] = (index, item)

        rows: list[dict[str, Any]] = []
        limitations: list[dict[str, Any]] = []
        target_link_rank = self._number((target_authority or {}).get("link_rank"))
        for keyword, group in snapshots.items():
            organic_entry = group["organic"]
            maps_entry = group["maps"]
            source = organic_entry[1] if organic_entry else maps_entry[1]
            target_rank = self._rank(source.get("target_rank")) if organic_entry else None
            target_maps_rank = self._rank(maps_entry[1].get("target_rank")) if maps_entry else None
            target_url = str(source.get("target_url") or "") if organic_entry else ""
            competitor_positions = self._competitor_positions(group, approved_domains)
            classes: list[str] = []
            evidence_refs: list[dict[str, Any]] = []
            comparisons: list[dict[str, Any]] = []

            if organic_entry:
                evidence_refs.append(self._snapshot_ref(market_run, "organic_evidence", organic_entry[0], source))
                if target_rank is None:
                    classes.append("not_observed_sample")
                elif 4 <= target_rank <= 20 and any(
                    position.get("organic_rank") is not None
                    and position["organic_rank"] < target_rank
                    for position in competitor_positions
                ):
                    classes.append("near_win")
                elif 21 <= target_rank <= 100:
                    classes.append("improvement")
                if target_rank is None and any(position.get("organic_rank") for position in competitor_positions):
                    classes.append("landing_page_gap")
            if maps_entry:
                evidence_refs.append(self._snapshot_ref(market_run, "maps_evidence", maps_entry[0], maps_entry[1]))
                if target_maps_rank is None and any(position.get("maps_rank") for position in competitor_positions):
                    classes.append("local_pack_gap")

            target_page = target_pages_by_url.get(self._url_identity(target_url)) if target_url else None
            for position in competitor_positions:
                domain = str(position["domain"])
                competitor = competitor_evidence.get(domain)
                landing_url = str(position.get("organic_url") or position.get("maps_url") or "")
                competitor_page = self._find_competitor_page(competitor, landing_url)
                if competitor_page and target_page:
                    page_differences = self._page_differences(target_page, competitor_page)
                    if page_differences:
                        competitor_pages = competitor.get("pages", [])
                        competitor_page_index = competitor_pages.index(competitor_page)
                        comparison_refs = [
                            {
                                "artifact_path": str(competitor.get("artifact_path")),
                                "field": f"pages[{competitor_page_index}]",
                                "reason": "Persisted bounded competitor landing-page evidence.",
                                "observed": competitor_page,
                            },
                            {
                                "artifact_path": f"pages/{target_page.id}.json",
                                "field": "url",
                                "reason": "Persisted target page used in the comparative evidence.",
                                "observed": target_page.url,
                            },
                        ]
                        comparisons.append({
                            "domain": domain,
                            "landing_url": landing_url,
                            "differences": page_differences,
                            "evidence_refs": comparison_refs,
                        })
                    if (
                        competitor_page.get("conversion_links")
                        and not self._target_conversion_links(target_page)
                    ):
                        classes.append("conversion_gap")
                elif landing_url and competitor is not None:
                    limitations.append({
                        "kind": "competitor_landing_page_not_collected",
                        "keyword": keyword,
                        "domain": domain,
                        "message": "A competitor ranked in the sample, but its exact landing page was not present in the bounded ten-page crawl.",
                    })

                competitor_link_rank = self._number(
                    ((competitor or {}).get("offsite_authority") or {}).get("link_rank")
                )
                if (
                    target_link_rank is not None
                    and competitor_link_rank is not None
                    and competitor_link_rank >= target_link_rank + 10
                ):
                    classes.append("authority_gap")
                    authority_refs = [{
                        "artifact_path": str((competitor or {}).get("artifact_path") or f"market/{market_run.id}.json"),
                        "field": "offsite_authority.link_rank",
                        "reason": "Persisted provider-specific competitor Link Rank.",
                        "observed": competitor_link_rank,
                    }]
                    target_authority_ref = (target_authority or {}).get("evidence_ref")
                    if isinstance(target_authority_ref, dict) and target_authority_ref.get("artifact_path"):
                        authority_refs.append({
                            "artifact_path": target_authority_ref["artifact_path"],
                            "field": f"{target_authority_ref['field']}.link_rank",
                            "reason": "Persisted provider-specific target Link Rank.",
                            "observed": target_link_rank,
                        })
                    comparisons.append({
                        "domain": domain,
                        "differences": [{
                            "type": "provider_link_rank",
                            "target": target_link_rank,
                            "competitor": competitor_link_rank,
                            "provider": "DataForSEO",
                        }],
                        "evidence_refs": authority_refs,
                    })

            classes = sorted(set(classes), key=lambda value: (-self.CLASS_WEIGHT[value], value))
            for comparison in comparisons:
                if comparison.get("evidence_ref"):
                    evidence_refs.append(comparison["evidence_ref"])
                evidence_refs.extend(comparison.get("evidence_refs", []))
            why = [
                self._why_statement(comparison)
                for comparison in comparisons
                if self._why_statement(comparison)
            ]
            row = {
                "keyword": keyword,
                "category": source.get("category"),
                "search_intent": source.get("search_intent"),
                "optimization_focus": source.get("optimization_focus"),
                "target_page_usage": source.get("target_page_usage"),
                "search_volume": self._keyword_metric(market_run, keyword, "search_volume"),
                "target_organic_position": target_rank,
                "target_maps_position": target_maps_rank,
                "target_ranking_url": target_url or None,
                "competitor_positions": competitor_positions,
                "comparative_evidence": comparisons,
                "opportunity_classes": classes,
                "why_they_may_be_winning": why,
                "evidence_refs": evidence_refs,
                "limitation": (
                    None
                    if why
                    else "No causal explanation is emitted because the persisted comparative page or authority evidence is insufficient."
                ),
            }
            rows.append(row)

        rows.sort(key=lambda row: (str(row.get("category") or ""), str(row["keyword"])))
        recommendations = self._recommend(rows)
        if target_link_rank is None:
            limitations.append({
                "kind": "target_authority_unknown",
                "message": "Authority-gap classification is unknown because the target has no validated provider Link Rank snapshot.",
            })
        return rows, recommendations, self._dedupe_limits(limitations)

    def _recommend(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        ranked: list[tuple[float, dict[str, Any]]] = []
        for row in rows:
            classes = row.get("opportunity_classes") or []
            if not classes or not row.get("evidence_refs"):
                continue
            intent = str(row.get("search_intent") or "").casefold()
            commercial = 3 if any(token in intent for token in ("transactional", "commercial", "local")) else 1
            volume = self._number(row.get("search_volume")) or 0
            volume_bonus = min(volume / 1000, 2)
            class_score = max(self.CLASS_WEIGHT[item] for item in classes)
            competitor_consistency = sum(
                1
                for item in row.get("competitor_positions", [])
                if item.get("organic_rank") is not None or item.get("maps_rank") is not None
            )
            evidence_score = min(len(row.get("evidence_refs", [])), 3)
            ranked.append((
                class_score + commercial + volume_bonus + competitor_consistency + evidence_score,
                row,
            ))
        ranked.sort(key=lambda item: (-item[0], str(item[1]["keyword"])))
        recommendations: list[dict[str, Any]] = []
        used_keywords: set[str] = set()
        for score, row in ranked:
            if row["keyword"] in used_keywords:
                continue
            primary_class = row["opportunity_classes"][0]
            service_fit = self._service_fit(primary_class)
            recommendations.append({
                "keyword": row["keyword"],
                "opportunity_class": primary_class,
                "priority_score": round(score, 2),
                "observation": self._observation(row, primary_class),
                "recommended_action": self._action(row, primary_class),
                "service_fit": service_fit,
                "evidence_refs": row["evidence_refs"],
                "ranking_promise": False,
            })
            used_keywords.add(row["keyword"])
            if len(recommendations) == 3:
                break
        return recommendations

    @staticmethod
    def _competitor_positions(
        group: dict[str, Any],
        approved_domains: set[str],
    ) -> list[dict[str, Any]]:
        positions: dict[str, dict[str, Any]] = {
            domain: {
                "domain": domain,
                "organic_rank": None,
                "organic_url": None,
                "maps_rank": None,
                "maps_url": None,
            }
            for domain in approved_domains
        }
        for source_type, rank_field, url_field in (
            ("organic", "organic_rank", "organic_url"),
            ("maps", "maps_rank", "maps_url"),
        ):
            entry = group.get(source_type)
            if not entry:
                continue
            for result in entry[1].get("results", []):
                if not isinstance(result, dict):
                    continue
                url = str(result.get("url") or result.get("website") or "")
                domain = GapAnalysisService._domain(url)
                if domain not in positions:
                    continue
                rank = GapAnalysisService._rank(result.get("rank"))
                current = positions[domain][rank_field]
                if rank is not None and (current is None or rank < current):
                    positions[domain][rank_field] = rank
                    positions[domain][url_field] = url or None
        return [
            value for value in positions.values()
            if value["organic_rank"] is not None or value["maps_rank"] is not None
        ]

    @staticmethod
    def _page_differences(target: PageRecord, competitor: dict[str, Any]) -> list[dict[str, Any]]:
        differences: list[dict[str, Any]] = []
        for name, target_value, competitor_value in (
            ("title", target.title, competitor.get("title")),
            ("meta_description", target.meta_description, competitor.get("meta_description")),
            ("h1", target.h1, competitor.get("h1")),
        ):
            if bool(competitor_value) and not bool(target_value):
                differences.append({"type": f"{name}_presence", "target": target_value, "competitor": competitor_value})
        target_schema = set(target.schema_types)
        competitor_schema = set(competitor.get("schema_types") or [])
        if competitor_schema - target_schema:
            differences.append({
                "type": "structured_data",
                "target": sorted(target_schema),
                "competitor": sorted(competitor_schema),
            })
        target_words = target.word_count or 0
        competitor_words = competitor.get("word_count")
        if isinstance(competitor_words, int) and competitor_words >= target_words + 300:
            differences.append({
                "type": "content_depth",
                "target_word_count": target_words,
                "competitor_word_count": competitor_words,
            })
        return differences

    @staticmethod
    def _find_competitor_page(
        competitor: dict[str, Any] | None,
        landing_url: str,
    ) -> dict[str, Any] | None:
        if competitor is None:
            return None
        pages = competitor.get("pages") if isinstance(competitor.get("pages"), list) else []
        identity = GapAnalysisService._url_identity(landing_url)
        exact = next(
            (page for page in pages if GapAnalysisService._url_identity(str(page.get("url") or "")) == identity),
            None,
        )
        return exact

    @staticmethod
    def _target_conversion_links(page: PageRecord) -> list[str]:
        return [
            url for url in page.internal_links
            if any(token in url.casefold() for token in ("schedule", "contact", "book", "trial", "signup", "sign-up"))
        ]

    @staticmethod
    def _snapshot_ref(
        market_run: MarketEvidenceRun,
        field: str,
        index: int,
        snapshot: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "artifact_path": f"market/{market_run.id}.json",
            "field": f"{field}[{index}]",
            "reason": "Persisted dated Tacoma market SERP evidence.",
            "observed": snapshot,
        }

    @staticmethod
    def _why_statement(comparison: dict[str, Any]) -> str | None:
        differences = comparison.get("differences") or []
        labels = {
            "title_presence": "a populated title",
            "meta_description_presence": "a populated meta description",
            "h1_presence": "a populated H1",
            "structured_data": "additional observed structured-data types",
            "content_depth": "substantially more HTTP-delivered text on the compared page",
            "provider_link_rank": "a higher DataForSEO Link Rank",
        }
        observed = [labels[item["type"]] for item in differences if item.get("type") in labels]
        if not observed:
            return None
        return f"{comparison.get('domain')} has {', '.join(observed)} in the persisted comparison."

    @staticmethod
    def _service_fit(opportunity_class: str) -> list[str]:
        if opportunity_class == "conversion_gap":
            return ["vertical_plugin_embed", "custom_website_crm_saas"]
        if opportunity_class in {"local_pack_gap", "landing_page_gap", "near_win", "improvement", "authority_gap"}:
            return ["website_seo_vertical_visibility", "national_bjj_registry_visibility"]
        return ["website_seo_vertical_visibility"]

    @staticmethod
    def _observation(row: dict[str, Any], opportunity_class: str) -> str:
        organic = row.get("target_organic_position")
        maps = row.get("target_maps_position")
        if opportunity_class == "local_pack_gap":
            return f"{row['keyword']!r} did not show Nova in the sampled Maps results while an approved competitor was observed."
        if opportunity_class == "near_win":
            return f"{row['keyword']!r} was observed at organic position {organic}, behind at least one approved competitor."
        if opportunity_class == "improvement":
            return f"{row['keyword']!r} was observed at organic position {organic} in the Tacoma sample."
        if opportunity_class == "landing_page_gap":
            return f"Nova was not observed organically for {row['keyword']!r}, while an approved competitor landing page was."
        if opportunity_class == "conversion_gap":
            return f"An approved competitor landing page exposed a schedule/contact conversion route not observed on Nova’s compared page for {row['keyword']!r}."
        if opportunity_class == "authority_gap":
            return f"Provider-specific Link Rank evidence showed a materially stronger approved competitor for {row['keyword']!r}."
        return f"Nova was not observed in the bounded organic sample for {row['keyword']!r}."

    @staticmethod
    def _action(row: dict[str, Any], opportunity_class: str) -> str:
        usage = row.get("target_page_usage") or "intended landing page"
        if opportunity_class == "conversion_gap":
            return f"Add a vertical-specific schedule, trial, or contact embed to the {usage}."
        if opportunity_class == "local_pack_gap":
            return f"Align the {usage} and local entity facts with the Tacoma query intent and Registry profile."
        if opportunity_class == "authority_gap":
            return "Strengthen verifiable entity corroboration through the National BJJ Registry and consistent owned profiles."
        if opportunity_class == "near_win":
            return f"Improve the existing {usage} metadata, headings, and intent coverage around the verified near-win."
        return f"Create or improve the dedicated {usage} so the query has a clear, crawlable destination."

    @staticmethod
    def _keyword_metric(market_run: MarketEvidenceRun, keyword: str, field: str) -> Any:
        normalized = " ".join(keyword.casefold().split())
        for item in market_run.keyword_metrics:
            if " ".join(str(item.get("keyword") or "").casefold().split()) == normalized:
                return item.get(field)
        return None

    @staticmethod
    def _rank(value: Any) -> int | None:
        if isinstance(value, bool) or not isinstance(value, int | float):
            return None
        rank = int(value)
        return rank if 1 <= rank <= 100 else None

    @staticmethod
    def _number(value: Any) -> float | None:
        if isinstance(value, bool) or not isinstance(value, int | float):
            return None
        return float(value)

    @staticmethod
    def _domain(value: str) -> str:
        candidate = value.strip().casefold().rstrip(".")
        if "://" in candidate:
            candidate = (urlsplit(candidate).hostname or "").casefold().rstrip(".")
        return candidate.removeprefix("www.")

    @staticmethod
    def _url_identity(value: str) -> str:
        parsed = urlsplit(value)
        host = (parsed.hostname or "").casefold().removeprefix("www.").rstrip(".")
        path = (parsed.path or "/").rstrip("/") or "/"
        return f"{host}{path}"

    @staticmethod
    def _dedupe_limits(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        output: list[dict[str, Any]] = []
        seen: set[tuple[str, str, str]] = set()
        for item in items:
            key = (
                str(item.get("kind") or ""),
                str(item.get("keyword") or ""),
                str(item.get("domain") or ""),
            )
            if key not in seen:
                seen.add(key)
                output.append(item)
        return output
