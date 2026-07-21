"""llm_guard.py — post-write guardrail for LLM-rendered articles.

The LLM operates on a fact bundle; the guard ensures it didn't smuggle in:
  - unsourced academy names (names not present in the bundle's verified top_academies)
  - unexplained raw numeric scores (e.g. '71.4', '85+', 'score of 70')
Hard counts from the bundle (e.g. '58 academies') ARE allowed because they are sourced.

It returns (ok, reason). On ok=False the caller should fall back to the template writer.
"""
from __future__ import annotations

import re
from typing import Optional

# A raw registry-style score looks like a number possibly with decimals, optionally
# followed by '+', attached to 'score'/'registry'/'85+'/'70+'. We flag score-percent language.
_SCORE_HINT = re.compile(
    r"\b(score[d]?\s*(of|is|at)?\s*\d)|(\d{2,3}\s*\+)|(registry score[:\s]+\d)",
    re.IGNORECASE,
)
_NUMBER = re.compile(r"\b\d{2,3}(?:\.\d+)?\b")


def guard(bundle: dict, prose: str) -> tuple[bool, Optional[str]]:
    """Return (passed, reason_or_None)."""
    if not prose or not prose.strip():
        return False, "empty prose"

    # Strip markdown headings — they are structural, not invented facts
    body = "\n".join(
        ln for ln in prose.splitlines() if not ln.strip().startswith("## ")
    )

    # 1) No raw registry-score language
    if _SCORE_HINT.search(body):
        return False, "prose contains raw score/percent language (numbers must stay qualitative)"

    # 2) Any 2-3 digit number must be sourced/explainable
    allowed_numbers = set()
    facts = bundle.get("facts", {})
    if facts.get("academy_count"):
        allowed_numbers.add(str(facts["academy_count"]))
    years = set(re.findall(r"\b(1[89]\d\d|20\d\d)\b", body))
    for m in _NUMBER.finditer(body):
        num = m.group(0)
        if num in allowed_numbers or num in years:
            continue
        return False, f"unsourced numeric value '{num}' in prose"

    # 3) No academy/gym name outside the verified bundle (allowlist from bundle + commons)
    allow = set()
    loc = (bundle.get("location") or "").lower()
    for tok in re.split(r"[\s,]+", loc):
        if tok:
            allow.add(tok)
    for lin in facts.get("lineages_present", []) or []:
        allow.add(lin.lower())
    for a in facts.get("top_academies", []) or []:
        if a.get("name"):
            allow.add(a["name"].lower())
    allow |= {"brazilian jiu-jitsu", "united states", "national bjj registry", "jiu jitsu",
              "no gi", "gi", "bjj"}
    for name in re.findall(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b", body):
        low = name.lower()
        if any(k and k in low for k in allow):
            continue
        if low in allow:
            continue
        return False, f"possible unsourced proper noun '{name}' in prose"

    return True, None


def guard_technique(bundle: dict, prose: str) -> tuple[bool, Optional[str]]:
    """Guard for technique pages: the LLM may reword steps but not invent them.

    Rule: every numbered step in `prose` must share a meaningful token with at
    least one source step from the bundle (provenance). Also blocks raw scores
    and forbids step-count inflation beyond the source list.
    """
    if not prose or not prose.strip():
        return False, "empty prose"
    body = "\n".join(ln for ln in prose.splitlines() if not ln.strip().startswith("## "))
    if _SCORE_HINT.search(body):
        return False, "prose contains raw score/percent language"

    src_steps = bundle.get("steps", [])
    # Tokenize source steps into keyword sets (content words only)
    stop = {"the", "a", "an", "and", "or", "to", "your", "you", "of", "in", "on", "with",
            "then", "now", "next", "keep", "make", "get", "up", "down", "into", "it", "that", "this"}
    src_tokens = [set(w for w in re.findall(r"[a-z]{4,}", s.lower()) if w not in stop)
                  for s in src_steps]

    # Extract numbered steps from prose
    rendered = re.findall(r"^\s*\d+[\.\)]\s*(.+)$", prose, flags=re.MULTILINE)
    if rendered and src_steps:
        if len(rendered) > len(src_steps) + 1:
            return False, f"step inflation: {len(rendered)} rendered vs {len(src_steps)} sourced"
        for step in rendered:
            toks = set(w for w in re.findall(r"[a-z]{4,}", step.lower()) if w not in stop)
            if not toks:
                continue
            matched = any(toks & st for st in src_tokens)
            if not matched:
                return False, f"unsourced step content: '{step[:60]}…'"
    return True, None
