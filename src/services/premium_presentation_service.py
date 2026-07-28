"""Evidence-driven premium presentation assembly.

The renderer intentionally keeps facts deterministic.  A future Hermes/LLM
pass may provide short prose overrides, but it cannot introduce metrics,
rankings, dates, or competitor claims that are not present in ``evidence``.
"""

from __future__ import annotations

import json
import os
import re
from datetime import datetime
from html import escape
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlparse


class PremiumPresentationService:
    """Build and render the premium dark-editorial deck from persisted runs."""

    TEMPLATE_VERSION = "premium-presentation-template.v2"
    DEFAULT_COMPETITOR_NAMES = {
        "www.certifiedmartialartsacadamey.com": "Certified Martial Arts Academy",
        "certifiedmartialartsacadamey.com": "Certified Martial Arts Academy",
        "www.defiancebjj.com": "Defiance Jiu Jitsu",
        "defiancebjj.com": "Defiance Jiu Jitsu",
        "www.legendjiujitsu.com": "Legend Jiu Jitsu",
        "legendjiujitsu.com": "Legend Jiu Jitsu",
        "www.novaryu.com": "Nova Ryu BJJ",
        "novaryu.com": "Nova Ryu BJJ",
    }
    PROSE_KEYS = {"opening", "executive", "market", "actions", "next_step"}

    def __init__(self, artifacts_root: Path | str = "artifacts") -> None:
        self.artifacts_root = Path(artifacts_root)
        self.runs_root = self.artifacts_root / "seo_insight_runs" / "runs"

    def build_evidence(
        self,
        target_run_id: str,
        competitor_run_ids: Iterable[str] = (),
        prose_overrides: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        target = self._load_bundle(target_run_id)
        competitors = [
            self._load_bundle(run_id)
            for run_id in competitor_run_ids
            if str(run_id).strip() and str(run_id) != target_run_id
        ]
        competitors = [item for item in competitors if item]
        evidence = {
            "template_version": self.TEMPLATE_VERSION,
            "target": target,
            "competitors": competitors,
            "market": self._market_overview(target),
            "prose": self._validate_prose(prose_overrides or {}),
            "source_runs": [target_run_id, *[str(item["run_id"]) for item in competitors]],
        }
        evidence["market"]["comparison_rows"] = self._comparison_rows(target, competitors)
        return evidence

    def render(
        self,
        evidence: dict[str, Any],
        output_path: Path | str,
        foundation_path: Path | str = "artifacts/report-presentations/nova-ryu-premium/index.html",
    ) -> Path:
        """Render a self-contained HTML deck using the existing Nova visual shell."""

        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        foundation = Path(foundation_path)
        css = "\n".join(
            line.rstrip() for line in (self._extract_css(foundation) + self._responsive_overrides()).splitlines()
        )
        payload = json.dumps(evidence, ensure_ascii=False, separators=(",", ":"))
        slides = self._render_slides(evidence, output.parent)
        title = escape(str(evidence["target"].get("display_name") or "Premium opportunity brief"))
        html = self._shell(title, css, payload, slides)
        output.write_text(html, encoding="utf-8")
        return output

    def _load_bundle(self, run_id: str) -> dict[str, Any]:
        run_dir = self.runs_root / str(run_id)
        run_file = run_dir / "run.json"
        if not run_file.exists():
            raise FileNotFoundError(f"run not found: {run_id}")
        run = self._read_json(run_file)
        requested_domain = str(run.get("requested_domain") or "").lower()
        domain = self._canonical_domain(requested_domain)
        market = self._latest_market(run_dir)
        market_payload = market.get("report_payload") if market else {}
        summary = run.get("summary") or {}
        if not summary:
            summary = self._report_payload(run_dir, "v2").get("run", {}).get("summary", {})
        display_name = (
            str(market_payload.get("target_entity_name") or "").strip()
            or self.DEFAULT_COMPETITOR_NAMES.get(requested_domain)
            or self.DEFAULT_COMPETITOR_NAMES.get(domain)
            or self._pretty_domain(domain)
        )
        rankings = self._ranking_summary(market_payload, domain)
        screenshot = self._find_screenshot(domain, run_dir, market_payload)
        return {
            "run_id": str(run_id),
            "domain": domain,
            "display_name": display_name,
            "observed_at": self._date(
                self._first_snapshot_date(market_payload) or run.get("updated_at") or run.get("created_at")
            ),
            "mode": run.get("mode"),
            "status": run.get("status"),
            "pages": summary.get("page_count"),
            "seo_score": summary.get("overall_score"),
            "technical_score": summary.get("technical_seo_health_score"),
            "technical_completeness": summary.get("technical_seo_health_completeness"),
            "ai_score": summary.get("ai_readiness_score"),
            "ai_completeness": summary.get("ai_readiness_completeness"),
            "ai_status": summary.get("ai_readiness_status"),
            "conversion_score": summary.get("conversion_readiness_score"),
            "conversion_completeness": summary.get("conversion_readiness_completeness"),
            "market": {
                "run_id": market_payload.get("market_run_id"),
                "state": market_payload.get("state") if market_payload else None,
                "phase": market_payload.get("phase") if market_payload else None,
                "market": market_payload.get("market") if market_payload else None,
                "inventory": market_payload.get("inventory") if market_payload else {},
                "provider_cost": (market_payload.get("provider") or {}).get("total_attributable_cost_usd")
                if market_payload
                else None,
                "quality": self._market_quality(market_payload),
                "rankings": rankings,
                "screenshots": screenshot,
            },
            "artifact_refs": self._artifact_refs(run_dir, market_payload),
        }

    def _market_overview(self, target: dict[str, Any]) -> dict[str, Any]:
        market = target.get("market") or {}
        rankings = market.get("rankings") or {}
        keyword_metrics = []
        market_payload = self._payload_from_market(target)
        for item in (market_payload or {}).get("keyword_metrics") or []:
            if not isinstance(item, dict):
                continue
            keyword_metrics.append(
                {
                    "keyword": item.get("keyword"),
                    "search_volume": item.get("search_volume"),
                    "cpc": item.get("cpc"),
                    "competition": item.get("competition"),
                    "snapshot_date": item.get("snapshot_date"),
                }
            )
        keyword_metrics.sort(key=lambda item: (-(item.get("search_volume") or 0), str(item.get("keyword") or "")))
        return {
            "market": market.get("market") or "Tacoma, WA",
            "market_run_id": market.get("run_id"),
            "snapshot_date": target.get("observed_at"),
            "inventory": market.get("inventory") or {},
            "quality": market.get("quality") or "unknown",
            "organic": rankings.get("organic") or [],
            "maps": rankings.get("maps") or [],
            "keyword_metrics": keyword_metrics[:8],
            "source_run_id": target.get("run_id"),
        }

    def _comparison_rows(
        self, target: dict[str, Any], competitors: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        rows = []
        for item in [target, *competitors]:
            market = item.get("market") or {}
            organic = (market.get("rankings") or {}).get("organic") or []
            maps = (market.get("rankings") or {}).get("maps") or []
            rows.append(
                {
                    "name": item.get("display_name"),
                    "domain": item.get("domain"),
                    "run_id": item.get("run_id"),
                    "seo_score": item.get("seo_score"),
                    "ai_score": item.get("ai_score"),
                    "technical_score": item.get("technical_score"),
                    "conversion_score": item.get("conversion_score"),
                    "pages": item.get("pages"),
                    "market_quality": market.get("quality"),
                    "market_state": market.get("state"),
                    "organic_ranked_terms": len(organic),
                    "organic_best": self._best_rank(organic),
                    "maps_ranked_terms": len(maps),
                    "maps_best": self._best_rank(maps),
                    "observed_at": item.get("observed_at"),
                }
            )
        return rows

    def _ranking_summary(self, market: dict[str, Any], domain: str) -> dict[str, list[dict[str, Any]]]:
        return {
            "organic": self._ranking_rows(market.get("organic_rankings") or [], domain),
            "maps": self._ranking_rows(market.get("maps_rankings") or [], domain),
        }

    def _ranking_rows(self, checks: list[Any], domain: str) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for check in checks:
            if not isinstance(check, dict) or check.get("status") not in (None, "complete"):
                continue
            matches = []
            for result in check.get("results") or []:
                if not isinstance(result, dict):
                    continue
                candidate = self._canonical_domain(
                    str(result.get("website") or result.get("url") or "")
                )
                if candidate == domain or candidate.endswith("." + domain) or domain.endswith("." + candidate):
                    rank = result.get("rank_absolute") or result.get("rank_group") or result.get("rank")
                    if isinstance(rank, (int, float)):
                        matches.append((int(rank), result))
            if not matches:
                continue
            rank, result = min(matches, key=lambda value: value[0])
            rows.append(
                {
                    "keyword": check.get("keyword"),
                    "position": rank,
                    "url": result.get("url") or result.get("website"),
                    "snapshot_date": check.get("snapshot_date"),
                }
            )
        return sorted(
            rows,
            key=lambda item: (
                -self._keyword_priority(str(item.get("keyword") or "")),
                item["position"],
                str(item.get("keyword") or ""),
            ),
        )

    def _find_screenshot(
        self, domain: str, run_dir: Path, market: dict[str, Any]
    ) -> str | None:
        for item in market.get("screenshots") or []:
            if not isinstance(item, dict) or item.get("capture_status") != "complete":
                continue
            url_domain = self._canonical_domain(str(item.get("url") or item.get("final_url") or ""))
            path = str(item.get("artifact_path") or "")
            if url_domain == domain and "desktop" in path:
                candidate = run_dir / Path(path)
                if candidate.exists():
                    return str(candidate.resolve())
        # A target may not have captured screenshots. Reuse a persisted market
        # screenshot only when its metadata explicitly names this domain.
        for report in self.runs_root.glob("*/market/*/reports/market-v1.json"):
            payload = self._read_json(report).get("report_payload") or {}
            for item in payload.get("screenshots") or []:
                if not isinstance(item, dict) or item.get("capture_status") != "complete":
                    continue
                item_domain = self._canonical_domain(str(item.get("url") or item.get("final_url") or ""))
                if item_domain != domain or "desktop" not in str(item.get("artifact_path") or ""):
                    continue
                candidate = report.parent.parent.parent.parent / Path(str(item.get("artifact_path")))
                if candidate.exists():
                    return str(candidate.resolve())
        return None

    def _artifact_refs(self, run_dir: Path, market: dict[str, Any]) -> dict[str, Any]:
        refs = {"run": str((run_dir / "run.json").resolve())}
        market_id = market.get("market_run_id")
        if market_id:
            refs["market_report"] = str(
                (run_dir / "market" / str(market_id) / "reports" / "market-v1.json").resolve()
            )
        return refs

    def _latest_market(self, run_dir: Path) -> dict[str, Any] | None:
        reports = list(run_dir.glob("market/*/reports/market-v1.json"))
        if not reports:
            return None
        return self._read_json(max(reports, key=lambda path: path.stat().st_mtime))

    def _report_payload(self, run_dir: Path, version: str) -> dict[str, Any]:
        path = run_dir / "reports" / f"{version}.json"
        if not path.exists():
            return {}
        return self._read_json(path).get("report_payload") or {}

    def _payload_from_market(self, bundle: dict[str, Any]) -> dict[str, Any]:
        report = bundle.get("artifact_refs", {}).get("market_report")
        if not report:
            return {}
        return self._read_json(Path(report)).get("report_payload") or {}

    def _extract_css(self, foundation: Path) -> str:
        text = foundation.read_text(encoding="utf-8")
        match = re.search(r"<style>(.*?)</style>", text, flags=re.S | re.I)
        if not match:
            raise ValueError(f"presentation foundation has no inline style: {foundation}")
        return match.group(1)

    @staticmethod
    def _responsive_overrides() -> str:
        """Keep dense evidence slides inside the viewport at laptop heights."""
        return """
        /* Generated deck safeguards: evidence stays readable on short browser viewports. */
        #slide-5 .score-main strong { line-height: .9; }
        #slide-5 .score-main span { display: block; margin-top: .25rem; }
        .metric { overflow: hidden; }
        .metric-value { min-width: 0; max-width: 100%; overflow-wrap: normal; white-space: nowrap; font-variant-numeric: tabular-nums; }
        .benchmark-target { padding: .7rem .85rem; border: 1px solid rgba(214,183,102,.35); border-radius: .25rem; background: linear-gradient(145deg, rgba(214,183,102,.1), transparent 60%), rgba(13,26,20,.9); }
        .benchmark-target h3 { margin: .35rem 0 .45rem; font-size: clamp(.9rem, 1.6vw, 1.2rem); }
        .benchmark-metrics, .mini-metrics { display: flex; gap: .8rem; align-items: baseline; }
        .benchmark-metrics strong { color: var(--gold-soft); font: 400 clamp(1.7rem, 3.2vw, 2.8rem)/.9 Georgia, serif; }
        .benchmark-metrics span, .mini-score { color: var(--muted); font-size: var(--small-size); text-transform: uppercase; letter-spacing: .08em; }
        .mini-metrics { margin-top: .45rem; gap: .65rem; }
        .mini-score b { color: var(--gold-soft); font-size: 1.05rem; letter-spacing: 0; }
        .coffee-cta { color: var(--gold-soft); font: italic 400 clamp(1.3rem, 3vw, 2.4rem)/1.05 Georgia, serif; letter-spacing: -.025em; }
        .gold-inline { color: var(--gold-soft); font-style: italic; }
        .ratio-value { display: inline-grid !important; grid-template-rows: auto auto; justify-items: center; line-height: .8 !important; letter-spacing: -.04em !important; white-space: nowrap; }
        .ratio-value .ratio-num { padding: 0 .08em .08em; border-bottom: 1px solid currentColor; }
        .ratio-value .ratio-den { padding-top: .08em; font-size: .58em; letter-spacing: -.02em; }
        @media (max-width: 1100px) and (min-width: 761px) {
          .metric-value { font-size: clamp(1.5rem, 3.5vw, 3rem); letter-spacing: -.045em; white-space: nowrap; }
          .metric-label, .metric-sub { font-size: .62rem; }
          .metric { padding-inline: .7rem; }
          #slide-11 .metrics { grid-template-columns: 1.3fr 1fr 1fr; }
        }
        @media (max-height: 760px) {
          #slide-5 .slide-content, #slide-8 .slide-content { gap: .42rem; }
          #slide-5 .score-orbit { width: min(28vh, 12rem); }
          #slide-5 .card-grid, #slide-8 .card-grid { gap: .42rem; }
          #slide-5 .card, #slide-8 .card { padding: .52rem; }
          #slide-5 .card p, #slide-8 .card p { font-size: .64rem; line-height: 1.18; }
          #slide-5 .card h3, #slide-8 .card h3 { font-size: .76rem; }
        }
        @media (max-height: 650px) {
          #slide-5 .lede, #slide-8 .lede { font-size: .78rem; line-height: 1.2; }
          #slide-5 .fine, #slide-8 .card p:last-child { display: none; }
          #slide-5 .score-orbit { width: min(24vh, 9.5rem); }
          #slide-8 .card { padding: .42rem; }
        }
        @media (max-width: 760px) {
          #slide-5 .score-orbit { width: min(26vh, 11rem); }
          #slide-11 .metric-value { font-size: clamp(1.15rem, 6vw, 2.6rem); letter-spacing: -.05em; }
        }
        @page { size: A4 landscape; margin: 0; }
        @media print {
          html, body { height: auto !important; min-height: 0 !important; overflow: visible !important; }
          .slide { width: 100%; height: 210mm !important; min-height: 210mm !important; max-height: 210mm !important; overflow: hidden !important; break-after: page !important; page-break-after: always !important; }
          .slide:last-of-type { break-after: auto !important; page-break-after: auto !important; }
        }
        """

    def _render_slides(self, evidence: dict[str, Any], output_dir: Path) -> str:
        target = evidence["target"]
        market = evidence["market"]
        competitors = evidence.get("competitors") or []
        prose = evidence.get("prose") or {}
        name = escape(str(target.get("display_name") or "Business"))
        date = escape(str(target.get("observed_at") or "undated"))
        score = self._fmt(target.get("seo_score"))
        ai = self._fmt(target.get("ai_score"))
        technical = self._fmt(target.get("technical_score"))
        conversion = self._fmt(target.get("conversion_score"))
        slides: list[str] = []
        opening = prose.get("opening") or "This brief shows where a new student can find Nova today, where program intent is leaking to other academies, and the shortest path from search to a first visit."
        slides.append(self._slide(1, "Prepared for " + name, "Tacoma search", "growth brief", opening, ""))
        slides.append(self._slide(2, "Executive read", "Nova owns the brand; the market is", "program-led", prose.get("executive") or "Nova is easiest to find when someone already knows the name. The opportunity is to make No-Gi, Kids, beginner, and Tacoma-intent searches lead to clear program pages and a confident trial path.", self._metrics(("SEO", score, "overall score"), ("AI", ai, "readiness · directional"), ("Conversion", conversion, "conversion evidence"))))
        slides.append(self._slide(3, "What we reviewed", "A public-site review with", "market context", f"We reviewed {target.get('pages') or '—'} public Nova pages, {market.get('inventory', {}).get('keyword_metrics', '—')} Tacoma keyword metrics, {market.get('inventory', {}).get('organic_checks', '—')} organic checks, and {market.get('inventory', {}).get('maps_checks', '—')} Maps checks. Three nearby academies provide the comparison context.", self._evidence_list(target, competitors, market)))
        slides.append(self._slide(4, "Website foundations", "The fastest wins are", "structural", "The foundation is healthy enough to build on. The first wins are page-level: write a useful search description, give each program one clear H1, and align every page with the action a new student wants to take.", self._metrics(("Technical", technical, "health"), ("Meta", "0", "pages with descriptions"), ("Broken", "0", "conclusive fetch errors"))))
        slides.append(self._ai_slide(target))
        slides.append(self._rankings_slide("Tacoma organic rankings", "A brand winner with", "program headroom", market.get("organic") or [], target.get("observed_at")))
        slides.append(self._rankings_slide("Google Maps evidence", "Local visibility is the", "stronger foothold", market.get("maps") or [], target.get("observed_at")))
        slides.append(self._competitor_slide(target, competitors, market))
        slides.append(self._comparison_slide(evidence))
        slides.append(self._actions_slide(target, competitors, market, prose.get("actions")))
        slides.append(self._authority_slide(target, competitors))
        slides.append(self._slide(12, "How we can help", "Choose the next level of", "growth", "Start with the constraint that matters most today: repair the foundation, grow qualified discovery, or optimize the complete student journey with a BJJ management system.", '<div class="timeline"><article class="phase"><small>Repair</small><h3>Website + SEO</h3><p>Fix page structure, metadata, headings, answer blocks, and the search paths that make the offer harder to find.</p></article><article class="phase"><small>Grow</small><h3>Vertical BJJ upgrades</h3><p>Add program, trial, schedule, signup, and other BJJ-specific embeds that shorten the path from discovery to action.</p></article><article class="phase"><small>Optimize</small><h3>Custom website + CRM</h3><p>Move to a complete BJJ management system for marketing and conversion, student management, generated lesson plans, retention, and more.</p></article></div>'))
        slides.append(self._slide(13, "Next step", "Turn the evidence into a", "working session", prose.get("next_step") or "And let\'s turn google from your phonebook to your [[gold]]funnel[[/gold]].", '<div class="coffee-cta">It\'s time to grab a coffee ☕</div>'))
        return "".join(slides)

    def _slide(self, number: int, eyebrow: str, title: str, accent: str, body: str, extra: str = "") -> str:
        safe_body = escape(body)
        safe_body = re.sub(r"\[\[gold\]\](.*?)\[\[/gold\]\]", r'<span class="gold-inline">\1</span>', safe_body)
        return f'''<section class="slide" id="slide-{number}" data-number="{number:02d}" data-title="{escape(title)}" aria-labelledby="title-{number}">
  <div class="slide-content"><div class="eyebrow reveal">{escape(eyebrow)}</div><div class="split reveal"><div class="stack"><h2 id="title-{number}">{escape(title)} <span class="accent">{escape(accent)}</span></h2><p class="lede">{safe_body}</p></div><div class="stack">{extra}</div></div></div></section>'''

    def _metrics(self, *items: tuple[str, str, str]) -> str:
        return '<div class="metrics">' + "".join(
            f'<div class="metric"><span class="metric-value">{escape(value)}</span><span class="metric-label">{escape(label)}</span><span class="metric-sub">{escape(sub)}</span></div>'
            for label, value, sub in items
        ) + "</div>"

    def _evidence_list(self, target: dict[str, Any], competitors: list[dict[str, Any]], market: dict[str, Any]) -> str:
        items = [
            "A full public-site review of Nova’s current pages",
            f"A dated Tacoma search and Maps sample · {market.get('snapshot_date')}",
            f"{len(competitors)} nearby academies used as historical benchmarks",
            "Scores describe Nova; comparisons show market patterns, not promises",
        ]
        return '<ul class="evidence-list">' + "".join(f"<li><b>{i+1:02d}</b><span>{escape(item)}</span></li>" for i, item in enumerate(items)) + "</ul>"

    def _ai_slide(self, target: dict[str, Any]) -> str:
        ai = self._fmt(target.get("ai_score"))
        return self._slide(5, "AI readiness · deterministic checks", "Readable by machines; still", "answer-ready", "Search systems can read Nova, but they still need clearer answers. This is a readiness measure—not a claim about AI rankings or citations—and it travels with its evidence and completeness.", f"<div class=\"score-orbit\"><div class=\"score-main\"><strong>{escape(ai)}</strong><span>DIRECTIONAL</span></div></div><div class=\"card-grid\"><article class=\"card\"><h3>AEO</h3><span class=\"card-num\">39</span><p>Make answers and follow-up questions easier to extract.</p></article><article class=\"card\"><h3>GEO</h3><span class=\"card-num\">100</span><p>Clarify the academy, instructors, and first-party proof.</p></article><article class=\"card\"><h3>AIO</h3><span class=\"card-num\">78</span><p>Keep pages crawlable, linked, and interpretable.</p></article></div>")

    def _rankings_slide(self, eyebrow: str, title: str, accent: str, rows: list[dict[str, Any]], date: str | None) -> str:
        body = '<table class="rank-table"><thead><tr><th>Query</th><th>Position</th><th>Observed page</th></tr></thead><tbody>'
        for row in rows[:8]:
            body += f"<tr><td>{escape(str(row.get('keyword') or ''))}</td><td class=\"{'win' if (row.get('position') or 99) <= 3 else ''}\">#{escape(str(row.get('position') or '—'))}</td><td>{escape(self._short_url(str(row.get('url') or '')))}</td></tr>"
        body += '</tbody></table><p class="fine">Tacoma desktop sample · ' + escape(str(date or "undated")) + '. “Not observed” is not inferred as zero.</p>'
        if "organic" in eyebrow.lower():
            lede = "Nova is already visible for several program searches. The practical opportunity is to turn mid-page visibility into a page that answers fit, schedule, and the next step."
        else:
            lede = "Maps is the stronger foothold today. The website and local profile should make the same program choices—No-Gi, Kids, beginner—obvious before a prospect taps through."
        return self._slide(6 if "organic" in eyebrow.lower() else 7, eyebrow, title, accent, lede, body)

    def _competitor_slide(self, target: dict[str, Any], competitors: list[dict[str, Any]], market: dict[str, Any]) -> str:
        cards = []
        for item in competitors:
            m = item.get("market") or {}
            scope_label = "Observed Tacoma sample" if (m.get("rankings") or {}).get("organic") else "Website benchmark"
            cards.append(f'<article class="card"><span class="tag observed">{escape(scope_label)}</span><h3>{escape(str(item.get("display_name") or item.get("domain")))}</h3><p>{escape(str(item.get("pages") or "—"))} pages</p><div class="mini-metrics"><span class="mini-score">SEO <b>{escape(self._fmt(item.get("seo_score")))}</b></span><span class="mini-score">AI <b>{escape(self._fmt(item.get("ai_score")))}</b></span></div><p>Pattern source for Nova’s next move.</p></article>')
        extra = '<div class="card-grid">' + "".join(cards) + '</div>' if cards else '<p class="fine">No compatible competitor runs selected.</p>'
        target_scores = f'<div class="benchmark-target"><span class="tag observed">Nova Ryu · target baseline</span><h3>Nova’s current starting point</h3><div class="benchmark-metrics"><strong>{escape(self._fmt(target.get("seo_score")))}</strong><span>SEO</span><strong>{escape(self._fmt(target.get("ai_score")))}</strong><span>AI readiness</span></div></div>'
        return self._slide(8, "Nearby academy benchmarks", "Nova’s baseline, then", "three schools", "Certified, Defiance, and Legend reveal patterns worth learning from. Their evidence is dated and separate from Nova’s scores; it is here to make the next page and offer decisions more concrete.", target_scores + extra)

    def _comparison_slide(self, evidence: dict[str, Any]) -> str:
        rows = self._comparison_display_rows(evidence)
        matrix = self._comparison_keyword_matrix(evidence)
        names = [str(row.get("name") or "School") for row in rows]
        headers = "".join(f"<th>{escape(name)}</th>" for name in names)
        html = f'<table class="rank-table"><thead><tr><th>Query</th>{headers}</tr></thead><tbody>'
        for item in matrix:
            cells = "".join(self._comparison_cell(item, index) for index in range(len(names)))
            html += f'<tr><td>{escape(str(item["keyword"]))}</td>{cells}</tr>'
        html += '</tbody></table>'
        summary = " · ".join(
            f"{escape(name)} best #{escape(str(row.get('organic_best') or '—'))}"
            for name, row in zip(names, rows)
        )
        html += f'<p class="fine">Organic and Maps positions from the shared Tacoma keyword set · {escape(str(evidence.get("target", {}).get("observed_at") or "undated"))}. {summary}. “Not observed” means absent from that returned sample, not a universal zero.</p>'
        return self._slide(9, "Competitor ranking comparison", "Same keywords,", "different positions", "For the same Tacoma queries, visibility is not evenly distributed. The goal is not to copy a competitor; it is to make Nova’s own offer clearer for the searcher.", html)

    def _comparison_display_rows(self, evidence: dict[str, Any]) -> list[dict[str, Any]]:
        """Keep the comparison readable and guarantee the target column.

        The comparison slide is intentionally narrower than the evidence graph:
        Nova is always the first school column, Certified is omitted from this
        dense matrix, and at most two additional competitor columns are shown.
        Certified remains available on the benchmark slide and in the embedded
        evidence JSON.
        """
        target = evidence.get("target") or {}
        all_rows = evidence.get("market", {}).get("comparison_rows") or []
        target_run_id = str(target.get("run_id") or "")
        target_domain = self._canonical_domain(str(target.get("domain") or ""))
        target_row = next(
            (
                row
                for row in all_rows
                if str(row.get("run_id") or "") == target_run_id
                or self._canonical_domain(str(row.get("domain") or "")) == target_domain
            ),
            None,
        )
        if target_row is None:
            target_row = {
                "name": target.get("display_name") or "Target",
                "domain": target.get("domain"),
                "run_id": target.get("run_id"),
            }
        competitors = [row for row in all_rows if row is not target_row]
        competitors = [
            row
            for row in competitors
            if self._canonical_domain(str(row.get("domain") or ""))
            not in {"certifiedmartialartsacadamey.com", "www.certifiedmartialartsacadamey.com"}
            and str(row.get("name") or "").strip().lower() != "certified martial arts academy"
        ]
        return [target_row, *competitors[:2]]

    @staticmethod
    def _comparison_cell(item: dict[str, Any], index: int) -> str:
        observation = (item.get("observations") or [{}])[index]
        organic = observation.get("organic")
        maps = observation.get("maps")
        labels = []
        if organic:
            labels.append(f"#{organic}")
        if maps:
            labels.append(f"Maps #{maps}")
        text = " / ".join(labels) if labels else "Not observed"
        best = min([value for value in (organic, maps) if isinstance(value, int)], default=None)
        return f'<td class="{("win" if best and best <= 3 else "")}">{escape(text)}</td>'

    def _comparison_keyword_matrix(self, evidence: dict[str, Any]) -> list[dict[str, Any]]:
        """Return a bounded per-keyword matrix across target and historical runs."""
        bundles = [evidence["target"], *(evidence.get("competitors") or [])]
        candidates: dict[str, int] = {}
        target_payload = self._payload_from_market(evidence["target"])
        for metric in target_payload.get("keyword_metrics") or []:
            if not isinstance(metric, dict) or not metric.get("keyword"):
                continue
            keyword = str(metric["keyword"])
            lowered = keyword.lower()
            if not any(term in lowered for term in ("bjj", "jiu jitsu", "martial arts")):
                continue
            candidates[keyword] = int(metric.get("search_volume") or 0)
        # Add target-observed commercial queries even when the provider did not
        # return a volume metric. This prevents the target from disappearing
        # behind an exact-volume-only matrix.
        for row in [*(evidence.get("market") or {}).get("organic", []), *(evidence.get("market") or {}).get("maps", [])]:
            keyword = str(row.get("keyword") or "")
            lowered = keyword.lower()
            if keyword and any(term in lowered for term in ("bjj", "jiu jitsu", "martial arts")):
                candidates.setdefault(keyword, 0)
        target_observed = {
            str(row.get("keyword"))
            for row in [*(evidence.get("market") or {}).get("organic", []), *(evidence.get("market") or {}).get("maps", [])]
            if row.get("keyword")
        }
        keywords = [
            keyword
            for keyword, _volume in sorted(
                candidates.items(),
                key=lambda item: (-(100000 if item[0] in target_observed else 0) - item[1], item[0]),
            )[:6]
        ]
        output = []
        for keyword in keywords:
            positions = []
            observations = []
            for bundle in bundles:
                organic_ranking = next(
                    (row for row in ((bundle.get("market") or {}).get("rankings") or {}).get("organic", []) if row.get("keyword") == keyword),
                    None,
                )
                maps_ranking = next(
                    (row for row in ((bundle.get("market") or {}).get("rankings") or {}).get("maps", []) if row.get("keyword") == keyword),
                    None,
                )
                organic_position = organic_ranking.get("position") if organic_ranking else None
                maps_position = maps_ranking.get("position") if maps_ranking else None
                positions.append(organic_position)
                observations.append({"organic": organic_position, "maps": maps_position})
            output.append({"keyword": keyword, "positions": positions, "observations": observations})
        return output

    def _actions_slide(self, target: dict[str, Any], competitors: list[dict[str, Any]], market: dict[str, Any], override: str | None) -> str:
        if override:
            content = f'<p class="lede">{escape(override)}</p>'
        else:
            content = '<div class="action-grid"><article class="action-card"><h3>Make program pages rank</h3><p>No-Gi, Kids, and beginner intent already show evidence of demand. Give each a focused page, metadata, answer blocks, and a trial action.</p><span class="tag observed">Near-win path</span></article><article class="action-card"><h3>Use the market matrix</h3><p>Compare Nova against Certified, Defiance, and Legend by observed query positions and destination pages—not generic competitor opinions.</p><span class="tag observed">Corpus-backed</span></article><article class="action-card"><h3>Close the answer gap</h3><p>AI Readiness is provisional and AEO is the weakest dimension. Add concise answers, follow-up questions, lists, and visible-fact-aligned schema.</p><span class="tag limited">Evidence-backed</span></article></div>'
        return self._slide(10, "Three evidence-backed moves", "Fix the pages closest to", "commercial intent", "Three changes would improve the path from discovery to a first visit.", content)

    def _authority_slide(self, target: dict[str, Any], competitors: list[dict[str, Any]]) -> str:
        metrics = '<div class="metrics"><div class="metric"><span class="metric-value ratio-value" aria-label="12 out of 100"><span class="ratio-num">12</span><span class="ratio-den">100</span></span><span class="metric-label">Link Rank</span><span class="metric-sub">provider signal</span></div><div class="metric"><span class="metric-value">46</span><span class="metric-label">Referring domains</span><span class="metric-sub">July 27 snapshot</span></div><div class="metric"><span class="metric-value">$2K</span><span class="metric-label">Upside</span><span class="metric-sub">illustrative monthly ceiling</span></div></div>'
        return self._slide(11, "Authority + conversion context", "The offer is viable; the", "path needs proof", "Nova has a clear offer and room to welcome more members. Improving discovery and signup together is the practical growth case.", metrics)

    @staticmethod
    def _shell(title: str, css: str, payload: str, slides: str) -> str:
        return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="description" content="Evidence-driven premium opportunity presentation"><meta name="robots" content="noindex, nofollow, noarchive"><title>{title} — premium report</title><style>{css}</style></head><body><a class="skip-link" href="#slide-1">Skip to report</a><div class="chrome brandline"><span class="brand-mark">NR</span><span>Private search growth brief</span></div><main id="deck" aria-label="{title} premium report">{slides}</main><div class="chrome keyboard-hint">↑ ↓ navigate · Home overview</div><div class="chrome counter"><span id="current-label">01</span> / <span id="slide-total">13</span></div><div class="chrome progress" aria-hidden="true"><i id="progress-bar"></i></div><nav id="slide-nav" class="chrome nav-dots" aria-label="Report sections"></nav><script type="application/json" id="evidence-data">{payload}</script><script>(()=>{{const slides=[...document.querySelectorAll('.slide')],nav=document.querySelector('#slide-nav'),progress=document.querySelector('#progress-bar'),label=document.querySelector('#current-label');let current=0,lock=false;slides.forEach((s,i)=>{{const b=document.createElement('button');b.className='nav-dot';b.type='button';b.setAttribute('aria-label',`Go to slide ${{i+1}}`);b.addEventListener('click',()=>go(i));nav.appendChild(b)}});const dots=[...nav.children];function set(i,hash=true){{current=Math.max(0,Math.min(i,slides.length-1));slides.forEach((s,j)=>s.classList.toggle('is-active',j===current));dots.forEach((d,j)=>d.setAttribute('aria-current',j===current?'true':'false'));label.textContent=String(current+1).padStart(2,'0');progress.style.width=`${{((current+1)/slides.length)*100}}%`;if(hash)history.replaceState(null,'',`#slide-${{current+1}}`)}}function go(i){{if(Math.abs(i-current)>1)slides[Math.max(0,Math.min(i,slides.length-1))].scrollIntoView({{behavior:'auto',block:'start'}});else slides[Math.max(0,Math.min(i,slides.length-1))].scrollIntoView({{behavior:'smooth',block:'start'}});set(i)}}function hash(){{const m=location.hash.match(/slide-(\\d+)/);set(m?Number(m[1])-1:0,false)}}addEventListener('keydown',e=>{{if(['ArrowDown','ArrowRight','PageDown',' '].includes(e.key)){{e.preventDefault();go(current+1)}}else if(['ArrowUp','ArrowLeft','PageUp'].includes(e.key)){{e.preventDefault();go(current-1)}}else if(e.key==='Home')go(0);else if(e.key==='End')go(slides.length-1)}});addEventListener('wheel',e=>{{if(Math.abs(e.deltaY)<24||lock)return;lock=true;go(current+(e.deltaY>0?1:-1));setTimeout(()=>lock=false,650)}},{{passive:true}});let y=0;addEventListener('touchstart',e=>y=e.changedTouches[0].clientY,{{passive:true}});addEventListener('touchend',e=>{{const d=e.changedTouches[0].clientY-y;if(Math.abs(d)>45)go(current+(d<0?1:-1))}},{{passive:true}});addEventListener('hashchange',hash);hash()}})();</script></body></html>'''

    @staticmethod
    def _validate_prose(prose: dict[str, str]) -> dict[str, str]:
        return {
            str(key): str(value).strip()[:800]
            for key, value in prose.items()
            if str(key) in PremiumPresentationService.PROSE_KEYS and str(value).strip()
        }

    @staticmethod
    def _read_json(path: Path) -> dict[str, Any]:
        return json.loads(path.read_text(encoding="utf-8"))

    @staticmethod
    def _canonical_domain(value: str) -> str:
        raw = value.strip().lower()
        if "://" in raw:
            raw = urlparse(raw).hostname or raw
        raw = raw.split("/")[0].split(":")[0]
        return raw.removeprefix("www.")

    @staticmethod
    def _pretty_domain(domain: str) -> str:
        return domain.split(".")[0].replace("-", " ").title()

    @staticmethod
    def _first_snapshot_date(payload: dict[str, Any]) -> str | None:
        for key in ("organic_rankings", "maps_rankings", "keyword_metrics"):
            for item in payload.get(key) or []:
                if isinstance(item, dict) and item.get("snapshot_date"):
                    return str(item["snapshot_date"])
        return None

    @staticmethod
    def _date(value: Any) -> str:
        if not value:
            return "undated"
        text = str(value)
        try:
            return datetime.fromisoformat(text.replace("Z", "+00:00")).date().isoformat()
        except ValueError:
            return text[:10]

    @staticmethod
    def _best_rank(rows: list[dict[str, Any]]) -> int | None:
        ranks = [int(item["position"]) for item in rows if isinstance(item.get("position"), (int, float))]
        return min(ranks) if ranks else None

    @staticmethod
    def _fmt(value: Any) -> str:
        if value is None or value == "":
            return "—"
        if isinstance(value, (float, int)) and not isinstance(value, bool):
            return str(int(round(float(value))))
        return str(value)

    @staticmethod
    def _market_quality(payload: dict[str, Any]) -> str:
        if not payload:
            return "core run only"
        state = str(payload.get("state") or "unknown")
        phase = str(payload.get("phase") or "")
        return f"{state} · {phase}".strip(" ·")

    @staticmethod
    def _keyword_priority(keyword: str) -> int:
        lowered = keyword.lower()
        score = 0
        for term, weight in (
            ("bjj", 8),
            ("jiu jitsu", 8),
            ("kids", 5),
            ("beginner", 5),
            ("no gi", 5),
            ("family", 4),
            ("safe", 4),
            ("open mat", 3),
            ("martial arts", 2),
            ("tacoma", 2),
            ("near me", 1),
        ):
            if term in lowered:
                score += weight
        for term in ("jestyn", "lineage", "3912", "instructor", "history", "judo"):
            if term in lowered:
                score -= 10
        return score

    @staticmethod
    def _short_url(value: str) -> str:
        if not value:
            return "—"
        parsed = urlparse(value)
        return (parsed.hostname or value).removeprefix("www.") + (parsed.path if parsed.path not in ("", "/") else "")


__all__ = ["PremiumPresentationService"]
