"""fact_bundle.py — serialize LocationFacts into a compact, LLM-ready prompt bundle.

This is the "feed step" for a flash model. The bundle is token-light (suitable for
Gemini Flash / DeepSeek V4 Flash / Haiku) and explicitly separates:

  - `facts`     : hard, sourced data the model MAY print (academy names, counts, lineage, vocab)
  - `signals`   : derived metrics the model may use to INFORM prose but must NOT print as numbers
  - `constraints`: hard rules the model must obey (no invented facts, no raw scores)

The template writer (article_template.py) remains the deterministic fallback and the
prose-quality floor; the LLM is a renderer that operates strictly within this bundle.
"""
from __future__ import annotations

from typing import Optional

from location_facts import LocationFacts


def build_bundle(facts: LocationFacts) -> dict:
    """Return a compact, Gemini-ready bundle for one location page."""
    loc = facts.name if facts.tier == "national" else f"{facts.name}, {facts.state or ''}".strip()

    # Hard facts the model is allowed to surface
    hard = {
        "tier": facts.tier,
        "name": loc,
        "state": facts.state,
        "county": facts.county,
        "city": facts.city,
        "academy_count": facts.academy_count if facts.academy_count_verified else None,
        "lineages_present": facts.lineages_present,
        "top_academies": [
            {"name": a.name, "lineage": a.lineage, "note": a.note}
            for a in facts.top_academies if a.verified
        ],
        "top_cities": facts.top_cities,
    }

    # Derived signals: inform the prose, but the published text must stay number-free.
    ins = facts.insights or {}
    signals = {
        "quality_band": _band(ins.get("avg_registry_score")),
        "relative_to_parent": _rel(
            ins.get("avg_registry_score"),
            ins.get("state_avg") if facts.tier in ("city", "county") else ins.get("national_avg"),
        ),
        "quality_evenness": _evenness(ins.get("median_registry_score"), ins.get("avg_registry_score")),
        "elite_depth": _elite(ins.get("pct_85_plus")),
        "majority_legit": _majority(ins.get("pct_70_plus")),
        "sample_size": ins.get("sample_size"),
    }

    return {
        "tier": facts.tier,
        "location": loc,
        "facts": hard,
        "signals": {k: v for k, v in signals.items() if v is not None},
        "constraints": [
            "Write in an expert black-belt voice: concrete, honest, opinionated but never arrogant.",
            "Use ONLY the provided facts and signals. Do NOT invent academy names, counts, rankings, or quotes.",
            "Do NOT print any numeric registry scores or percentages in the prose — express quality as "
            "qualitative bands (e.g. 'a strong training market', 'above the state average', 'a deep elite tier').",
            "Mirror the section structure and H2 headings supplied by the template; fill each with natural prose.",
            "Keep it genuinely useful to a beginner choosing where to train, not marketing fluff.",
        ],
    }


# --- qualitative banding (mirrors article_template._insights_section) ---

def _band(v: Optional[float]) -> Optional[str]:
    if v is None:
        return None
    if v >= 75:
        return "strong"
    if v >= 68:
        return "solid"
    if v >= 60:
        return "moderate"
    return "developing"


def _rel(val: Optional[float], base: Optional[float]) -> Optional[str]:
    if val is None or base is None:
        return None
    if val - base >= 3:
        return "above the average"
    if val - base <= -3:
        return "below the average"
    return "in line with the average"


def _evenness(median: Optional[float], avg: Optional[float]) -> Optional[str]:
    if median is None or avg is None:
        return None
    if median < avg - 3:
        return "uneven — a few standout gyms lift the average"
    if median > avg + 3:
        return "top-heavy — median above average, reliable across the board"
    return "consistent — median tracks average"


def _elite(pct85: Optional[float]) -> Optional[str]:
    if pct85 is None:
        return None
    if pct85 >= 15:
        return "deep elite tier"
    if pct85 >= 8:
        return "real elite tier"
    return "thin elite tier"


def _majority(pct70: Optional[float]) -> Optional[str]:
    if pct70 is None:
        return None
    if pct70 >= 60:
        return "most options are legitimate"
    if pct70 >= 40:
        return "most options legitimate, some developing"
    return "mixed quality"


# ---------- Technique axis bundle ----------
def build_technique_bundle(facts, brand: str = "National BJJ Registry") -> dict:
    """Token-light feed for a technique page. Transcript is the fact source.

    Steps are passed verbatim (they ARE the facts); the model may reword but not
    add. Constraints forbid inventing steps, scores, or academy claims. Academy
    attribution is intentionally absent — it cannot be sourced from the corpus alone.
    """
    return {
        "axis": "technique",
        "name": facts.name,
        "position": facts.position,
        "belt": facts.belt,
        "category": facts.category,
        "summary": facts.summary,
        "source": "transcript" if facts.transcript_verified else "metadata",
        "steps": facts.steps,                       # verbatim, sourced
        "common_errors": facts.common_errors,
        "key_terms": facts.key_terms,
        "related": [{"name": r.name, "slug": r.slug} for r in facts.related_techniques],
        "constraints": [
            "You are a black-belt instructor writing a precise technique explainer.",
            "Rewrite the provided STEPS into clean, natural instruction. You may reword each step, "
            "but you MUST NOT add, remove, or reorder steps — the step list is fixed and sourced.",
            "Do NOT invent grips, sequences, or details not implied by the given steps.",
            "Do NOT print any numeric scores, rankings, or statistics.",
            "Do NOT name or recommend any specific academy or gym — attribution is out of scope.",
            "Voice: concrete, safety-aware, beginner-friendly but not condescending.",
        ],
    }
