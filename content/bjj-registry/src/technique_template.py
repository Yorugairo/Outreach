"""technique_template.py — deterministic article + JSON-LD for technique pages (axis 2).

Reuses the same conventions as article_template.py: deterministic, never fabricate,
structure controlled here, prose swappable via the LLM writer. The transcript is the
fact source — rendered steps must trace to it. Renders a HowTo JSON-LD (rich-result
eligible) so technique pages get a real SEO leg up over location pages.

The LLM render mode (build_technique_llm) follows the same guard pattern: the model
may rewrite step phrasing but must not invent steps; llm_guard checks step provenance.
"""
from __future__ import annotations

import json
import re
from typing import Optional

from technique_facts import TechniqueFacts


def build_article(facts: TechniqueFacts, brand: str = "National BJJ Registry") -> dict:
    crumbs = facts.breadcrumb()
    crumb_md = " > ".join(f"[{label}](/{slug})" for label, slug in crumbs)
    h1 = ("How to " + facts.name) + (f" from {facts.position.title()}" if facts.position else "")

    body = [f"*Part of the {brand}.*", "", crumb_md, "", f"# {h1}", ""]
    if facts.summary:
        body.append(f"> {facts.summary}")
        body.append("")

    # Position / level context
    ctx = []
    if facts.position:
        ctx.append(f"**Position:** {facts.position.title()}")
    if facts.belt and facts.belt != "all levels":
        ctx.append(f"**Level:** {facts.belt.title()} belt and up")
    if facts.category:
        ctx.append(f"**Type:** {facts.category.title()}")
    if ctx:
        body.append(" | ".join(ctx))
        body.append("")

    # Step-by-step (transcript-sourced)
    body.append("## Step-by-Step Breakdown")
    body.append("")
    if facts.steps:
        for i, s in enumerate(facts.steps, 1):
            body.append(f"{i}. {s}")
    else:
        body.append("_A step-by-step breakdown is being finalized from the instructional transcript. "
                    "Check back or visit a registered academy to learn this live._")
    body.append("")

    # Common errors
    if facts.common_errors:
        body.append("## Common Mistakes to Avoid")
        body.append("")
        for e in facts.common_errors:
            body.append(f"- {e}")
        body.append("")

    # Key terms
    if facts.key_terms:
        body.append("## Key Terms")
        body.append("")
        body.append(", ".join(f"**{t}**" for t in facts.key_terms[:12]))
        body.append("")

    # Related
    if facts.related_techniques:
        body.append("## Related Techniques")
        body.append("")
        body.append(", ".join(f"[{r.name}](/{r.slug})" for r in facts.related_techniques))
        body.append("")

    body.append("---")
    body.append("")
    body.append(f"*Instructional content on the {brand} is derived from published technique transcripts. "
                "Always train under a qualified instructor — details matter and a live coach will correct what "
                "a page cannot.*")

    markdown = "\n".join(body)

    jsonld = _howto_jsonld(facts, h1, brand)
    return {
        "axis": "technique", "slug": facts.slug, "title_tag": facts.title_tag(brand),
        "meta_description": facts.meta_description(), "h1": h1,
        "markdown": markdown, "jsonld": jsonld,
        "verified": facts.transcript_verified,
    }


def _howto_jsonld(facts: TechniqueFacts, h1: str, brand: str) -> dict:
    """HowTo schema — eligible for Google rich results on technique pages."""
    steps = []
    for i, s in enumerate(facts.steps, 1):
        steps.append({"@type": "HowToStep", "position": i, "text": s})
    data = {
        "@context": "https://schema.org",
        "@type": "HowTo",
        "name": h1,
        "description": facts.summary or h1,
        "totalTime": "PT15M" if facts.belt and facts.belt == "white" else "PT10M",
    }
    if steps:
        data["step"] = steps
    if facts.key_terms:
        data["tool"] = [{"@type": "HowToTool", "name": t} for t in facts.key_terms[:6]]
    return data


# ---------- LLM render mode (mirrors article_template.build_article_llm) ----------
def build_technique_llm(facts: TechniqueFacts, brand: str = "National BJJ Registry", cfg=None) -> dict:
    """LLM rewrites step *phrasing* only; steps are sourced from the transcript.

    The model may reword a step but cannot add steps. llm_guard enforces provenance:
    every rendered step must be a paraphrase of a transcript-sourced step.
    """
    from fact_bundle import build_technique_bundle
    from llm_writer import render_sections
    from llm_guard import guard_technique
    bundle = build_technique_bundle(facts, brand)
    prose = render_sections(bundle, ["Step-by-Step Breakdown", "Common Mistakes to Avoid"], cfg=cfg)
    if not prose:
        raise RuntimeError("llm_writer returned no prose")
    ok, reason = guard_technique(bundle, prose)
    if not ok:
        raise RuntimeError(f"llm_guard rejected technique output: {reason}")
    # Splice: keep deterministic structure, swap step/errors bodies from LLM prose.
    from article_template import _parse_llm_sections  # reuse parser
    blocks = _parse_llm_sections(prose)
    new = dict(facts)
    if "Step-by-Step Breakdown" in blocks:
        new_steps = [ln.strip(f"{i}. ") for i, ln in enumerate(blocks["Step-by-Step Breakdown"].splitlines(), 1)
                     if ln.strip()]
        if new_steps:
            facts.steps = new_steps
    return build_article(facts, brand=brand)
