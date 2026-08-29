"""Compile the Current Bubble Mechanism pilot into a word-timed review package.

The canonical ElevenLabs timing file is the only production clock.  This
script creates deterministic evidence cards, a finance cue sheet, a validated
editorial-motion plan, an edit manifest, and a staged Remotion revision.  It
does not call an image or video provider and it never mutates the canonical
audio artifacts.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from jsonschema import Draft7Validator

from content.video_engine.src.guards.editorial_motion_qc import run_editorial_motion_qc
from content.video_engine.src.services.editorial_motion import (
    validate_editorial_motion_plan,
    validate_editorial_pacing_recipe,
)
from content.video_engine.src.services.history_contracts import canonical_sha256


EPISODE_ID = "current-bubble-mechanism"
CHANNEL_ID = "systems-and-blowups"
HASH_RE = re.compile(r"^[a-f0-9]{64}$")
WORD_END_RE = re.compile(r"[.!?][\"')\]]*$")
CLAUSE_END_RE = re.compile(r"[,;:][\"')\]]*$")


@dataclass(frozen=True)
class Chapter:
    index: int
    segment_id: str
    title: str
    start_word: int
    end_word: int
    claim_refs: tuple[str, ...]


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain an object")
    return payload


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _hashed(core: Mapping[str, Any]) -> dict[str, Any]:
    payload = dict(core)
    payload["artifact_hash"] = canonical_sha256(payload)
    return payload


def _normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.casefold())


def _schema_validate(engine_root: Path, payload: Mapping[str, Any], schema_name: str) -> None:
    schema = _read_json(engine_root / "configs" / schema_name)
    errors = sorted(Draft7Validator(schema).iter_errors(payload), key=lambda item: list(item.path))
    if errors:
        rendered = "; ".join(
            f"{'.'.join(str(part) for part in error.path) or '$'}: {error.message}"
            for error in errors
        )
        raise ValueError(f"{schema_name} validation failed: {rendered}")


def _find_phrase(words: Sequence[Mapping[str, Any]], phrase: str, cursor: int) -> int:
    needle = [_normalize(token) for token in re.findall(r"\S+", phrase) if _normalize(token)]
    if not needle:
        raise ValueError("chapter phrase is empty")
    haystack = [_normalize(str(item["w"])) for item in words]
    for size in range(min(10, len(needle)), 3, -1):
        target = needle[:size]
        for index in range(cursor, len(haystack) - size + 1):
            if haystack[index : index + size] == target:
                return index
    raise ValueError(f"unable to locate narration phrase after word {cursor}: {phrase[:100]!r}")


def _build_chapters(
    narration: Mapping[str, Any],
    words: Sequence[Mapping[str, Any]],
) -> list[Chapter]:
    chapter_titles = (
        "The Wrong Bubble",
        "What a Bubble Actually Is",
        "Memory Is a Physical Constraint",
        "Buyers Reserved the Ovens",
        "Markets Are Repricing Technical Power",
        "The Index Can Fail Both Jobs",
        "Too Concentrated, Too Diluted",
        "Retirement Math Is Not Generational-Wealth Math",
        "Separate Upside from Defense",
        "The Strongest Countercase",
        "Find the Cable",
    )
    chapter_claims = [
        ("memory-bottleneck-not-bubble-inference", "sp500-hidden-bubble-risk-inference"),
        ("memory-bottleneck-not-bubble-inference", "sp500-hidden-bubble-risk-inference"),
        ("memory-architecture-dependency", "hbm-capacity-trade-ratio", "samsung-hbm4-growth", "sk-hynix-demand-exceeds-supply"),
        ("micron-strategic-customer-agreements", "memory-bottleneck-not-bubble-inference"),
        ("korea-italy-listed-market-comparison", "korea-technology-intensity", "cross-exchange-comparability-limit"),
        ("sp500-top-ten-concentration", "index-fund-asset-scale", "sp500-hidden-bubble-risk-inference"),
        ("sp500-top-ten-concentration", "sp500-hidden-bubble-risk-inference"),
        ("generational-wealth-return-hurdle", "sp500-trailing-return-snapshot", "sp500-market-leaders-comparison"),
        ("concentrated-defensive-barbell-hypothesis", "sp500-market-leaders-comparison"),
        ("memory-countercase", "sp500-countercase", "equal-weight-long-tail-countercase", "korea-conglomerate-concentration-risk"),
        ("memory-bottleneck-not-bubble-inference", "sp500-hidden-bubble-risk-inference", "concentrated-defensive-barbell-hypothesis"),
    ]
    starts: list[int] = []
    cursor = 0
    segments = list(narration.get("segments") or [])
    for index, segment in enumerate(segments):
        start = 0 if index == 0 else _find_phrase(words, str(segment["text"]), cursor)
        starts.append(start)
        cursor = start + 1
    chapters: list[Chapter] = []
    for index, segment in enumerate(segments):
        segment_id = str(segment["segment_id"])
        chapters.append(
            Chapter(
                index=index,
                segment_id=segment_id,
                title=chapter_titles[index],
                start_word=starts[index],
                end_word=(starts[index + 1] - 1 if index + 1 < len(starts) else len(words) - 1),
                claim_refs=chapter_claims[index],
            )
        )
    return chapters


def _boundary_end_s(words: Sequence[Mapping[str, Any]], end_word: int, audio_duration: float) -> float:
    if end_word + 1 < len(words):
        return float(words[end_word + 1]["start_s"])
    return audio_duration


def _split_chapter(
    chapter: Chapter,
    words: Sequence[Mapping[str, Any]],
    audio_duration: float,
) -> list[tuple[int, int]]:
    ranges: list[tuple[int, int]] = []
    cursor = chapter.start_word
    target_pattern = (3.05, 3.45, 3.8, 3.25)
    local_index = 0
    while cursor <= chapter.end_word:
        start_s = float(words[cursor]["start_s"])
        if cursor == chapter.end_word:
            ranges.append((cursor, cursor))
            break
        candidates: list[tuple[float, int]] = []
        target = target_pattern[local_index % len(target_pattern)]
        for end_word in range(cursor, chapter.end_word + 1):
            duration = _boundary_end_s(words, end_word, audio_duration) - start_s
            if duration < 2.15:
                continue
            if duration > 5.35:
                break
            token = str(words[end_word]["w"])
            punctuation_penalty = 0.0 if WORD_END_RE.search(token) else 0.28 if CLAUSE_END_RE.search(token) else 0.72
            candidates.append((abs(duration - target) + punctuation_penalty, end_word))
        if not candidates:
            end_word = cursor
            while end_word < chapter.end_word and _boundary_end_s(words, end_word, audio_duration) - start_s < 5.0:
                end_word += 1
            end_word = max(cursor, end_word - 1)
        else:
            end_word = min(candidates)[1]
        remaining = _boundary_end_s(words, chapter.end_word, audio_duration) - _boundary_end_s(words, end_word, audio_duration)
        current_duration = _boundary_end_s(words, end_word, audio_duration) - start_s
        if 0 < remaining < 1.35 and current_duration + remaining <= 5.5:
            end_word = chapter.end_word
        ranges.append((cursor, end_word))
        cursor = end_word + 1
        local_index += 1
    return ranges


def _svg_shell(title: str, kicker: str, body: str, footer: str) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080" viewBox="0 0 1920 1080">
  <defs>
    <filter id="paper"><feTurbulence baseFrequency="0.7" numOctaves="3" seed="19" result="noise"/><feColorMatrix in="noise" type="saturate" values="0"/><feComponentTransfer><feFuncA type="table" tableValues="0 0.13"/></feComponentTransfer></filter>
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dx="0" dy="18" stdDeviation="14" flood-color="#18222b" flood-opacity="0.22"/></filter>
    <pattern id="grid" width="64" height="64" patternUnits="userSpaceOnUse"><path d="M64 0H0V64" fill="none" stroke="#143a52" stroke-opacity="0.09" stroke-width="2"/></pattern>
    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0 0L10 5L0 10Z" fill="#d3a329"/></marker>
  </defs>
  <rect width="1920" height="1080" fill="#f4ead7"/>
  <rect width="1920" height="1080" fill="url(#grid)"/>
  <rect width="1920" height="1080" filter="url(#paper)" opacity="0.7"/>
  <rect x="64" y="54" width="1792" height="972" rx="34" fill="none" stroke="#173d58" stroke-width="8"/>
  <path d="M96 190H1824" stroke="#d19b2a" stroke-width="6"/>
  <text x="110" y="112" font-family="Inter,Arial,sans-serif" font-size="28" font-weight="800" letter-spacing="5" fill="#bb4934">{html.escape(kicker.upper())}</text>
  <text x="110" y="172" font-family="Inter,Arial,sans-serif" font-size="54" font-weight="900" fill="#172934">{html.escape(title)}</text>
  {body}
  <rect x="94" y="952" width="1732" height="54" rx="12" fill="#173d58"/>
  <text x="120" y="987" font-family="Roboto Mono,Consolas,monospace" font-size="21" fill="#f7eddb">{html.escape(footer)}</text>
</svg>'''


def _evidence_svgs(evidence_dir: Path) -> dict[str, dict[str, Any]]:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    cards: dict[str, tuple[str, str, str, str, dict[str, Any], str]] = {}
    cards["evidence-memory-contracts-v1"] = (
        "Buyers Are Reserving the Ovens",
        "Commitment evidence",
        '''<g filter="url(#shadow)">
  <rect x="130" y="250" width="500" height="590" rx="30" fill="#0f6674"/>
  <text x="190" y="430" font-family="Inter,Arial" font-size="210" font-weight="900" fill="#f6d36b">16</text>
  <text x="190" y="490" font-family="Inter,Arial" font-size="34" font-weight="800" fill="#fff6df">STRATEGIC AGREEMENTS</text>
  <rect x="700" y="250" width="500" height="590" rx="30" fill="#d36a4a"/>
  <text x="755" y="430" font-family="Inter,Arial" font-size="210" font-weight="900" fill="#fff6df">5</text>
  <text x="755" y="490" font-family="Inter,Arial" font-size="34" font-weight="800" fill="#fff6df">YEARS, TYPICALLY</text>
  <rect x="1270" y="250" width="500" height="590" rx="30" fill="#173d58"/>
  <text x="1325" y="402" font-family="Inter,Arial" font-size="115" font-weight="900" fill="#f6d36b">20%</text>
  <text x="1325" y="455" font-family="Inter,Arial" font-size="30" font-weight="800" fill="#fff6df">DRAM VOLUME</text>
  <text x="1325" y="610" font-family="Inter,Arial" font-size="115" font-weight="900" fill="#f6d36b">⅓</text>
  <text x="1325" y="663" font-family="Inter,Arial" font-size="30" font-weight="800" fill="#fff6df">NAND VOLUME</text>
</g>
<text x="960" y="905" text-anchor="middle" font-family="Inter,Arial" font-size="31" font-weight="700" fill="#172934">Take-or-pay signals buyer commitment. It does not guarantee revenue or returns.</text>''',
        "Micron Technology · Fiscal Q3 2026 prepared remarks · pp. 1–2 · as of 2026-06-24",
        {"agreements": 16, "typical_years": 5, "dram_share": 0.20, "nand_share": 1 / 3},
        "2026-06-24",
    )
    cards["evidence-sp500-concentration-v1"] = (
        "Diversification on the Label",
        "Concentration evidence",
        '''<g transform="translate(100 210)">
  <circle cx="400" cy="360" r="260" fill="none" stroke="#d7c8ad" stroke-width="116"/>
  <circle cx="400" cy="360" r="260" fill="none" stroke="#d05b42" stroke-width="116" stroke-dasharray="653 981" transform="rotate(-90 400 360)"/>
  <text x="400" y="345" text-anchor="middle" font-family="Inter,Arial" font-size="150" font-weight="900" fill="#172934">~40%</text>
  <text x="400" y="415" text-anchor="middle" font-family="Inter,Arial" font-size="34" font-weight="800" fill="#b94c38">TOP TEN WEIGHT</text>
</g>
<g filter="url(#shadow)">
  <rect x="940" y="280" width="720" height="160" rx="28" fill="#173d58"/>
  <text x="1000" y="352" font-family="Inter,Arial" font-size="44" font-weight="900" fill="#f6d36b">BENEFIT REMOVED</text>
  <text x="1000" y="405" font-family="Inter,Arial" font-size="29" fill="#fff6df">The largest holdings dominate the outcome.</text>
  <rect x="940" y="495" width="720" height="160" rx="28" fill="#0f6674"/>
  <text x="1000" y="567" font-family="Inter,Arial" font-size="44" font-weight="900" fill="#f6d36b">DRAG RETAINED</text>
  <text x="1000" y="620" font-family="Inter,Arial" font-size="29" fill="#fff6df">The long tail still absorbs part of each dollar.</text>
</g>
<text x="1300" y="755" text-anchor="middle" font-family="Inter,Arial" font-size="28" font-weight="700" fill="#172934">Concentration alone does not prove overvaluation.</text>''',
        "S&P Dow Jones Indices + Vanguard · In the Shadows of Giants · mid-2025 snapshot",
        {"top_ten_weight": 0.40, "observation": "almost"},
        "2025-06-30",
    )
    cards["evidence-index-inclusion-gate-v1"] = (
        "The Index Has an Entry Gate—not a Quality Ranking",
        "S&P 500 inclusion mechanics",
        '''<g transform="translate(135 250)" filter="url(#shadow)">
  <g font-family="Inter,Arial" font-size="34" font-weight="900" text-anchor="middle"><rect x="0" y="70" width="360" height="180" rx="28" fill="#173d58"/><text x="180" y="175" fill="#fff6df">SIZE</text><rect x="0" y="295" width="360" height="180" rx="28" fill="#0f6674"/><text x="180" y="400" fill="#fff6df">LIQUIDITY</text><rect x="0" y="520" width="360" height="180" rx="28" fill="#d36a4a"/><text x="180" y="625" fill="#fff6df">PROFITABILITY</text></g>
  <path d="M410 385H760" stroke="#d3a329" stroke-width="24" marker-end="url(#arrow)"/>
  <rect x="790" y="120" width="710" height="510" rx="38" fill="#173d58"/><text x="1145" y="255" text-anchor="middle" font-family="Inter,Arial" font-size="58" font-weight="900" fill="#f5c34f">ADMITTED</text><text x="1145" y="350" text-anchor="middle" font-family="Inter,Arial" font-size="36" fill="#fff6df">After entry, the standard index</text><text x="1145" y="405" text-anchor="middle" font-family="Inter,Arial" font-size="36" fill="#fff6df">does not continuously rank firms</text><text x="1145" y="460" text-anchor="middle" font-family="Inter,Arial" font-size="36" fill="#fff6df">by cash flow or return on capital.</text><text x="1145" y="565" text-anchor="middle" font-family="Inter,Arial" font-size="42" font-weight="900" fill="#95d4d2">GATE ≠ OPTIMIZER</text>
</g>''',
        "S&P Dow Jones Indices · S&P U.S. Indices Methodology · inclusion rules",
        {"criteria": ["size", "liquidity", "profitability"], "post_entry_weighting": "float_adjusted_market_cap"},
        "2026-08-08",
    )
    cards["evidence-float-weighting-v1"] = (
        "Every New Dollar Follows Float-Adjusted Market Value",
        "Automatic allocation",
        '''<g transform="translate(120 270)" filter="url(#shadow)">
  <rect x="0" y="40" width="430" height="520" rx="38" fill="#173d58"/><text x="215" y="145" text-anchor="middle" font-family="Inter,Arial" font-size="46" font-weight="900" fill="#fff6df">NEW CONTRIBUTION</text><text x="215" y="350" text-anchor="middle" font-family="Inter,Arial" font-size="132" font-weight="900" fill="#f5c34f">$1</text>
  <path d="M480 300H770" stroke="#d3a329" stroke-width="24" marker-end="url(#arrow)"/>
  <g font-family="Inter,Arial" font-weight="900" text-anchor="middle"><rect x="800" y="0" width="690" height="170" rx="28" fill="#0f6674"/><text x="1145" y="100" font-size="44" fill="#fff6df">LARGER FLOAT VALUE → MORE CENTS</text><rect x="800" y="220" width="520" height="150" rx="28" fill="#173d58"/><text x="1060" y="312" font-size="38" fill="#fff6df">MEDIUM VALUE → FEWER</text><rect x="800" y="420" width="390" height="130" rx="28" fill="#786a58"/><text x="995" y="502" font-size="34" fill="#fff6df">SMALLER → FEWEST</text></g>
</g>''',
        "S&P Dow Jones Indices · float-adjusted market-cap weighting methodology",
        {"weighting": "float_adjusted_market_cap", "classification": "methodology"},
        "2026-08-08",
    )
    cards["evidence-automatic-business-mix-v1"] = (
        "The Rule Buys Every Qualifier Automatically",
        "What the same contribution owns",
        '''<g transform="translate(125 260)" filter="url(#shadow)">
  <path d="M790 40V180M790 180H245M790 180H1335M245 180V300M790 180V300M1335 180V300" fill="none" stroke="#d3a329" stroke-width="20"/>
  <ellipse cx="790" cy="45" rx="300" ry="80" fill="#173d58"/><text x="790" y="62" text-anchor="middle" font-family="Inter,Arial" font-size="43" font-weight="900" fill="#fff6df">ONE AUTOMATIC CONTRIBUTION</text>
  <g font-family="Inter,Arial" text-anchor="middle"><rect x="0" y="300" width="490" height="360" rx="34" fill="#0f6674"/><text x="245" y="420" font-size="46" font-weight="900" fill="#fff6df">COMPOUNDER</text><text x="245" y="500" font-size="29" fill="#fff6df">high reinvestment runway</text><rect x="545" y="300" width="490" height="360" rx="34" fill="#173d58"/><text x="790" y="420" font-size="46" font-weight="900" fill="#fff6df">INCUMBENT</text><text x="790" y="500" font-size="29" fill="#fff6df">mature but still large</text><rect x="1090" y="300" width="490" height="360" rx="34" fill="#786a58"/><text x="1335" y="420" font-size="46" font-weight="900" fill="#fff6df">QUALIFIER</text><text x="1335" y="500" font-size="29" fill="#fff6df">large enough to remain</text></g>
</g>''',
        "Episode mechanism illustration · not a claim that any named company lacks quality",
        {"classification": "channel_illustration", "allocation": "automatic_after_inclusion"},
        "2026-08-08",
    )
    cards["evidence-diworsification-plateau-v1"] = (
        "More Names Eventually Add Less Independent Protection",
        "Diminishing diversification benefit",
        '''<g transform="translate(145 255)" filter="url(#shadow)">
  <path d="M80 650V40M80 650H1580" stroke="#173d58" stroke-width="12"/>
  <path d="M100 600C260 300 470 175 710 145S1140 125 1530 120" fill="none" stroke="#0f6674" stroke-width="26"/>
  <path d="M100 610C430 560 800 485 1530 300" fill="none" stroke="#d36a4a" stroke-width="18" stroke-dasharray="26 18"/>
  <line x1="760" y1="80" x2="760" y2="650" stroke="#d3a329" stroke-width="12" stroke-dasharray="18 16"/>
  <text x="420" y="105" text-anchor="middle" font-family="Inter,Arial" font-size="40" font-weight="900" fill="#0f6674">USEFUL DIVERSIFICATION</text><text x="1145" y="195" text-anchor="middle" font-family="Inter,Arial" font-size="40" font-weight="900" fill="#173d58">BENEFIT FLATTENS</text><text x="1170" y="385" text-anchor="middle" font-family="Inter,Arial" font-size="36" font-weight="900" fill="#b94c38">CAPITAL ALLOCATION CONTINUES</text><text x="830" y="730" font-family="Inter,Arial" font-size="34" font-weight="900" fill="#172934">NUMBER OF HOLDINGS →</text>
</g>''',
        "Conceptual mechanism · no universal holding-count threshold is claimed",
        {"classification": "conceptual_model", "threshold": "not_specified"},
        "2026-08-08",
    )
    cards["evidence-index-tail-absorption-v1"] = (
        "The Long Tail Still Receives Most of the Remaining Dollar",
        "Concentration plus dilution",
        '''<g transform="translate(140 280)" filter="url(#shadow)">
  <rect x="0" y="120" width="1580" height="280" rx="42" fill="#d7c8ad"/>
  <rect x="0" y="120" width="620" height="280" rx="42" fill="#d36a4a"/>
  <text x="310" y="250" text-anchor="middle" font-family="Inter,Arial" font-size="86" font-weight="900" fill="#fff6df">~40%</text><text x="310" y="330" text-anchor="middle" font-family="Inter,Arial" font-size="34" font-weight="900" fill="#fff6df">TOP TEN</text>
  <text x="1100" y="250" text-anchor="middle" font-family="Inter,Arial" font-size="86" font-weight="900" fill="#172934">~60%</text><text x="1100" y="330" text-anchor="middle" font-family="Inter,Arial" font-size="34" font-weight="900" fill="#172934">REMAINING INDEX</text>
  <path d="M310 445V650M1100 445V650" stroke="#173d58" stroke-width="18"/>
  <text x="310" y="725" text-anchor="middle" font-family="Inter,Arial" font-size="36" font-weight="900" fill="#b94c38">CONCENTRATED OUTCOME</text><text x="1100" y="700" text-anchor="middle" font-family="Inter,Arial" font-size="34" font-weight="900" fill="#173d58">CAPITAL STILL ABSORBED</text><text x="1100" y="745" text-anchor="middle" font-family="Inter,Arial" font-size="30" fill="#172934">independent defense is not guaranteed</text>
</g>''',
        "S&P DJI top-ten weight snapshot + channel inference · approximately mid-2025",
        {"top_ten_weight": 0.40, "remaining_weight": 0.60, "observation": "approximate"},
        "2025-06-30",
    )
    cards["evidence-korea-italy-v1"] = (
        "Listed Markets Are Repricing Technical Power",
        "Cross-market comparison",
        '''<g transform="translate(180 270)" filter="url(#shadow)">
  <rect x="0" y="0" width="680" height="530" rx="34" fill="#173d58"/>
  <rect x="120" y="160" width="170" height="300" rx="18" fill="#19a5b7"/>
  <rect x="390" y="351" width="170" height="109" rx="18" fill="#d76b4e"/>
  <text x="205" y="130" text-anchor="middle" font-family="Inter,Arial" font-size="60" font-weight="900" fill="#fff6df">€3.21T</text>
  <text x="475" y="321" text-anchor="middle" font-family="Inter,Arial" font-size="60" font-weight="900" fill="#fff6df">€1.16T</text>
  <text x="205" y="505" text-anchor="middle" font-family="Inter,Arial" font-size="36" font-weight="900" fill="#fff6df">KOREA</text>
  <text x="475" y="505" text-anchor="middle" font-family="Inter,Arial" font-size="36" font-weight="900" fill="#fff6df">MILAN</text>
  <circle cx="900" cy="265" r="220" fill="#f0c45b"/>
  <text x="900" y="245" text-anchor="middle" font-family="Inter,Arial" font-size="120" font-weight="900" fill="#173d58">2.77×</text>
  <text x="900" y="310" text-anchor="middle" font-family="Inter,Arial" font-size="29" font-weight="900" fill="#173d58">LISTED-MARKET SCALE</text>
  <text x="900" y="415" text-anchor="middle" font-family="Inter,Arial" font-size="27" fill="#172934">Not GDP. Not culture. Not perfectly</text>
  <text x="900" y="453" text-anchor="middle" font-family="Inter,Arial" font-size="27" fill="#172934">harmonized exchange universes.</text>
</g>''',
        "KRX + Borsa Italiana + ECB conversion · as of 2026-07-27 · comparison is approximate",
        {"korea_eur_trillion": 3.21, "milan_eur_trillion": 1.1578, "multiple": 2.77},
        "2026-07-27",
    )
    cards["evidence-return-hurdle-v1"] = (
        "Retirement Math Is Not Generational-Wealth Math",
        "Illustrative compound-growth hurdle",
        '''<g transform="translate(145 255)">
  <line x1="0" y1="570" x2="1620" y2="570" stroke="#173d58" stroke-width="8"/>
  <rect x="80" y="530" width="220" height="40" rx="12" fill="#6f8390"/>
  <rect x="450" y="414" width="220" height="156" rx="12" fill="#0f6674"/>
  <rect x="820" y="220" width="220" height="350" rx="12" fill="#d36a4a"/>
  <rect x="1190" y="0" width="220" height="570" rx="12" fill="#d3a329"/>
  <text x="190" y="505" text-anchor="middle" font-family="Inter,Arial" font-size="48" font-weight="900" fill="#172934">$25K</text>
  <text x="560" y="388" text-anchor="middle" font-family="Inter,Arial" font-size="48" font-weight="900" fill="#172934">$271K</text>
  <text x="930" y="194" text-anchor="middle" font-family="Inter,Arial" font-size="48" font-weight="900" fill="#172934">~$600K</text>
  <text x="1300" y="-26" text-anchor="middle" font-family="Inter,Arial" font-size="48" font-weight="900" fill="#172934">$1.0M</text>
  <text x="190" y="625" text-anchor="middle" font-family="Inter,Arial" font-size="30" font-weight="800" fill="#172934">START</text>
  <text x="560" y="625" text-anchor="middle" font-family="Inter,Arial" font-size="30" font-weight="800" fill="#172934">10.0%</text>
  <text x="930" y="625" text-anchor="middle" font-family="Inter,Arial" font-size="30" font-weight="800" fill="#172934">13.58%</text>
  <text x="1300" y="625" text-anchor="middle" font-family="Inter,Arial" font-size="30" font-weight="800" fill="#172934">15.88%</text>
</g>
<text x="960" y="925" text-anchor="middle" font-family="Inter,Arial" font-size="27" font-weight="700" fill="#172934">25 years · no added contributions · before taxes, fees, dividends, and inflation</text>''',
        "SEC compound-interest method + S&P DJI 10-year price-return snapshot · illustrative, not a forecast",
        {"start": 25000, "years": 25, "rates": [0.10, 0.1358, 0.1588]},
        "2026-06-30",
    )
    cards["evidence-market-leaders-v1"] = (
        "A Smaller Quality Basket Can Change Returns",
        "Back-tested comparison",
        '''<g transform="translate(120 245)" filter="url(#shadow)">
  <rect x="0" y="0" width="760" height="560" rx="36" fill="#173d58"/>
  <text x="60" y="105" font-family="Inter,Arial" font-size="40" font-weight="800" fill="#fff6df">S&amp;P 500</text>
  <text x="700" y="105" text-anchor="end" font-family="Inter,Arial" font-size="70" font-weight="900" fill="#d7c8ad">13.58%</text>
  <rect x="60" y="150" width="510" height="62" rx="18" fill="#d7c8ad"/>
  <path d="M60 275H700" stroke="#f4ead7" stroke-opacity="0.32" stroke-width="4"/>
  <text x="60" y="355" font-family="Inter,Arial" font-size="38" font-weight="800" fill="#fff6df">MARKET LEADERS</text>
  <text x="700" y="445" text-anchor="end" font-family="Inter,Arial" font-size="82" font-weight="900" fill="#f5c34f">16.01%</text>
  <rect x="60" y="475" width="610" height="62" rx="18" fill="#f5c34f"/>
  <path d="M850 30H1570V530H850Z" fill="#fff6df" stroke="#d36a4a" stroke-width="8"/>
  <text x="1210" y="125" text-anchor="middle" font-family="Inter,Arial" font-size="44" font-weight="900" fill="#b94c38">THE LIMIT</text>
  <text x="1210" y="205" text-anchor="middle" font-family="Inter,Arial" font-size="29" fill="#172934">The index launched in late 2024.</text>
  <text x="1210" y="255" text-anchor="middle" font-family="Inter,Arial" font-size="29" fill="#172934">Most of the ten-year record is</text>
  <text x="1210" y="310" text-anchor="middle" font-family="Inter,Arial" font-size="28" font-weight="800" fill="#172934">HYPOTHETICAL BACK-TESTING.</text>
  <text x="1210" y="380" text-anchor="middle" font-family="Inter,Arial" font-size="26" fill="#172934">It also had a deeper</text>
  <text x="1210" y="420" text-anchor="middle" font-family="Inter,Arial" font-size="26" fill="#172934">full-period drawdown.</text>
</g>''',
        "S&P Dow Jones Indices · 10-year annualized price return · as of 2026-06-30",
        {"sp500_price_return": 0.1358, "market_leaders_price_return": 0.1601, "history": "mostly_backtested"},
        "2026-06-30",
    )
    cards["evidence-index-scale-v1"] = (
        "The Default Machine Is Enormous",
        "Index-fund scale",
        '''<g filter="url(#shadow)">
  <circle cx="590" cy="535" r="300" fill="#173d58"/>
  <text x="590" y="510" text-anchor="middle" font-family="Inter,Arial" font-size="155" font-weight="900" fill="#f5c34f">$19.1T</text>
  <text x="590" y="585" text-anchor="middle" font-family="Inter,Arial" font-size="34" font-weight="800" fill="#fff6df">INDEX MUTUAL FUNDS + ETFs</text>
  <rect x="1020" y="265" width="670" height="240" rx="34" fill="#0f6674"/>
  <text x="1080" y="400" font-family="Inter,Arial" font-size="118" font-weight="900" fill="#fff6df">52%</text>
  <text x="1380" y="385" font-family="Inter,Arial" font-size="34" font-weight="800" fill="#fff6df">OF LONG-TERM</text>
  <text x="1380" y="430" font-family="Inter,Arial" font-size="34" font-weight="800" fill="#fff6df">FUND ASSETS</text>
  <rect x="1020" y="570" width="670" height="220" rx="34" fill="#d36a4a"/>
  <text x="1080" y="700" font-family="Inter,Arial" font-size="105" font-weight="900" fill="#fff6df">~19%</text>
  <text x="1425" y="665" font-family="Inter,Arial" font-size="31" font-weight="800" fill="#fff6df">OF U.S. STOCK VALUE</text>
  <text x="1425" y="713" font-family="Inter,Arial" font-size="25" fill="#fff6df">domestic equity index funds</text>
</g>
<text x="960" y="890" text-anchor="middle" font-family="Inter,Arial" font-size="29" font-weight="700" fill="#172934">Large does not mean all-owning or all-price-setting.</text>''',
        "Investment Company Institute · 2026 Fact Book · year-end 2025",
        {"index_assets_usd_trillion": 19.1, "long_term_fund_share": 0.52, "us_stock_value_share": 0.19},
        "2025-12-31",
    )
    cards["evidence-wealth-target-path-v1"] = (
        "$25,000 Has a Specific Hill to Climb",
        "Target path",
        '''<g transform="translate(125 250)" filter="url(#shadow)">
  <path d="M90 610H360V485H650V345H940V185H1230V30H1530" fill="none" stroke="#173d58" stroke-width="42" stroke-linejoin="round"/>
  <circle cx="90" cy="610" r="58" fill="#0f6674"/><text x="90" y="625" text-anchor="middle" font-family="Inter,Arial" font-size="38" font-weight="900" fill="#fff6df">$25K</text>
  <circle cx="1530" cy="30" r="78" fill="#d3a329"/><text x="1530" y="45" text-anchor="middle" font-family="Inter,Arial" font-size="38" font-weight="900" fill="#172934">$1M</text>
  <path d="M118 575L1470 68" stroke="#d36a4a" stroke-width="12" stroke-dasharray="26 18"/>
  <text x="870" y="690" text-anchor="middle" font-family="Inter,Arial" font-size="54" font-weight="900" fill="#172934">25 YEARS · NO ADDED CONTRIBUTIONS</text>
  <text x="870" y="770" text-anchor="middle" font-family="Inter,Arial" font-size="84" font-weight="900" fill="#b94c38">15.88% / YEAR REQUIRED</text>
</g>''',
        "SEC compound-interest method · illustrative hurdle · not a forecast",
        {"start": 25000, "target": 1000000, "years": 25, "required_rate": 0.1588},
        "2026-06-30",
    )
    cards["evidence-return-ten-percent-v1"] = (
        "The Familiar 10% Path Stops Short",
        "Compound-growth comparison",
        '''<g transform="translate(145 265)" filter="url(#shadow)">
  <rect x="0" y="0" width="520" height="600" rx="34" fill="#173d58"/>
  <text x="260" y="130" text-anchor="middle" font-family="Inter,Arial" font-size="72" font-weight="900" fill="#f5c34f">10.0%</text>
  <text x="260" y="190" text-anchor="middle" font-family="Inter,Arial" font-size="30" fill="#fff6df">ANNUAL GROWTH</text>
  <path d="M90 480C180 450 250 390 330 315S430 175 470 120" fill="none" stroke="#95d4d2" stroke-width="18"/>
  <text x="260" y="555" text-anchor="middle" font-family="Inter,Arial" font-size="62" font-weight="900" fill="#fff6df">≈ $271K</text>
  <path d="M610 300H1040" stroke="#d36a4a" stroke-width="22" stroke-dasharray="28 20"/>
  <text x="825" y="265" text-anchor="middle" font-family="Inter,Arial" font-size="34" font-weight="800" fill="#b94c38">THE GAP REMAINS</text>
  <circle cx="1375" cy="300" r="230" fill="#d3a329"/><text x="1375" y="325" text-anchor="middle" font-family="Inter,Arial" font-size="110" font-weight="900" fill="#172934">$1M</text>
</g>''',
        "SEC compound-interest method · $25,000 for 25 years · no contributions",
        {"start": 25000, "years": 25, "rate": 0.10, "result_rounded": 271000},
        "2026-06-30",
    )
    cards["evidence-return-comparison-v1"] = (
        "A Strong Decade Still Misses the Target",
        "10% versus 13.58%",
        '''<g transform="translate(150 250)" filter="url(#shadow)">
  <rect x="0" y="260" width="390" height="330" rx="28" fill="#0f6674"/><text x="195" y="350" text-anchor="middle" font-family="Inter,Arial" font-size="60" font-weight="900" fill="#fff6df">10.0%</text><text x="195" y="520" text-anchor="middle" font-family="Inter,Arial" font-size="72" font-weight="900" fill="#f5c34f">$271K</text>
  <rect x="520" y="80" width="450" height="510" rx="28" fill="#173d58"/><text x="745" y="175" text-anchor="middle" font-family="Inter,Arial" font-size="60" font-weight="900" fill="#fff6df">13.58%</text><text x="745" y="520" text-anchor="middle" font-family="Inter,Arial" font-size="72" font-weight="900" fill="#f5c34f">~$600K</text>
  <rect x="1100" y="0" width="470" height="590" rx="28" fill="#d3a329"/><text x="1335" y="105" text-anchor="middle" font-family="Inter,Arial" font-size="60" font-weight="900" fill="#172934">15.88%</text><text x="1335" y="520" text-anchor="middle" font-family="Inter,Arial" font-size="76" font-weight="900" fill="#172934">$1.0M</text>
  <text x="785" y="700" text-anchor="middle" font-family="Inter,Arial" font-size="36" font-weight="800" fill="#172934">SAME $25K · SAME 25 YEARS · DIFFERENT COMPOUNDING PATH</text>
</g>''',
        "SEC method + S&P DJI ten-year price return ending 2026-06-30 · counterfactual only",
        {"start": 25000, "years": 25, "rates": [0.10, 0.1358, 0.1588]},
        "2026-06-30",
    )
    cards["evidence-wealth-levers-v1"] = (
        "The Gap Can Close Through Different Levers",
        "Objective design",
        '''<g transform="translate(130 255)" filter="url(#shadow)">
  <circle cx="820" cy="90" r="90" fill="#173d58"/><text x="820" y="105" text-anchor="middle" font-family="Inter,Arial" font-size="42" font-weight="900" fill="#fff6df">GAP</text>
  <path d="M820 180V300M820 300H190M820 300H1450" fill="none" stroke="#d3a329" stroke-width="18"/>
  <g font-family="Inter,Arial" font-size="31" font-weight="900" text-anchor="middle"><rect x="40" y="360" width="290" height="210" rx="28" fill="#0f6674"/><text x="185" y="475" fill="#fff6df">MORE TIME</text><rect x="360" y="360" width="290" height="210" rx="28" fill="#173d58"/><text x="505" y="475" fill="#fff6df">MORE SAVING</text><rect x="680" y="360" width="290" height="210" rx="28" fill="#d36a4a"/><text x="825" y="455" fill="#fff6df">BUSINESS</text><text x="825" y="495" fill="#fff6df">OWNERSHIP</text><rect x="1000" y="360" width="290" height="210" rx="28" fill="#786a58"/><text x="1145" y="475" fill="#fff6df">MORE RISK</text><rect x="1320" y="360" width="290" height="210" rx="28" fill="#d3a329"/><text x="1465" y="455" fill="#172934">EXCEPTIONAL</text><text x="1465" y="495" fill="#172934">RETURNS</text></g>
</g>''',
        "Channel framework · alternatives are risks and tradeoffs, not recommendations",
        {"classification": "channel_inference"},
        "2026-08-08",
    )
    cards["evidence-portfolio-jobs-v1"] = (
        "One Basket Is Being Asked to Do Two Jobs",
        "Portfolio mechanism",
        '''<g transform="translate(140 245)" filter="url(#shadow)">
  <path d="M780 80V245M780 245L380 390M780 245L1180 390" fill="none" stroke="#d3a329" stroke-width="22"/>
  <ellipse cx="780" cy="75" rx="250" ry="75" fill="#173d58"/><text x="780" y="92" text-anchor="middle" font-family="Inter,Arial" font-size="42" font-weight="900" fill="#fff6df">ONE INDEX BASKET</text>
  <rect x="80" y="390" width="600" height="320" rx="34" fill="#0f6674"/><text x="380" y="500" text-anchor="middle" font-family="Inter,Arial" font-size="55" font-weight="900" fill="#fff6df">UPSIDE</text><text x="380" y="565" text-anchor="middle" font-family="Inter,Arial" font-size="27" fill="#fff6df">productive leaders · bottlenecks</text><path d="M190 645L310 560L420 610L575 470" fill="none" stroke="#f5c34f" stroke-width="16"/>
  <rect x="880" y="390" width="600" height="320" rx="34" fill="#173d58"/><text x="1180" y="500" text-anchor="middle" font-family="Inter,Arial" font-size="55" font-weight="900" fill="#fff6df">DEFENSE</text><text x="1180" y="565" text-anchor="middle" font-family="Inter,Arial" font-size="27" fill="#fff6df">independent recession · inflation · stress</text><path d="M1040 650V530H1320V650" fill="none" stroke="#95d4d2" stroke-width="20"/>
</g>''',
        "Channel portfolio-design framework · not personalized investment advice",
        {"classification": "channel_inference"},
        "2026-08-08",
    )
    cards["evidence-market-leaders-basket-v1"] = (
        "A Fifty-Company Quality Filter",
        "Market Leaders methodology",
        '''<g transform="translate(130 245)" filter="url(#shadow)">
  <g fill="#d7c8ad">''' + ''.join(f'<rect x="{(i % 10) * 74}" y="{(i // 10) * 74}" width="54" height="54" rx="9"/>' for i in range(50)) + '''</g>
  <path d="M805 175H1040" stroke="#d3a329" stroke-width="22" marker-end="url(#arrow)"/>
  <g font-family="Inter,Arial" font-size="27" font-weight="900"><rect x="1030" y="0" width="480" height="150" rx="26" fill="#173d58"/><text x="1270" y="88" text-anchor="middle" fill="#fff6df">FREE-CASH-FLOW MARGIN</text><rect x="1030" y="205" width="480" height="150" rx="26" fill="#0f6674"/><text x="1270" y="293" text-anchor="middle" fill="#fff6df">RETURN ON CAPITAL</text><rect x="1030" y="410" width="480" height="150" rx="26" fill="#d36a4a"/><text x="1270" y="498" text-anchor="middle" fill="#fff6df">MARKET SHARE</text></g>
  <text x="370" y="520" text-anchor="middle" font-family="Inter,Arial" font-size="46" font-weight="900" fill="#172934">ROUGHLY 50 COMPANIES</text>
</g>''',
        "S&P Dow Jones Indices · Market Leaders methodology · as of 2026-06-30",
        {"constituents_approx": 50, "screens": ["free_cash_flow_margin", "roic", "market_share"]},
        "2026-06-30",
    )
    cards["evidence-market-leaders-backtest-v1"] = (
        "Most of the Ten-Year Line Was Simulated",
        "Back-test limitation",
        '''<g transform="translate(140 285)" filter="url(#shadow)">
  <line x1="70" y1="270" x2="1570" y2="270" stroke="#173d58" stroke-width="24"/>
  <line x1="70" y1="270" x2="1290" y2="270" stroke="#d36a4a" stroke-width="34" stroke-dasharray="26 18"/>
  <line x1="1290" y1="270" x2="1570" y2="270" stroke="#0f6674" stroke-width="34"/>
  <text x="650" y="190" text-anchor="middle" font-family="Inter,Arial" font-size="58" font-weight="900" fill="#b94c38">HYPOTHETICAL BACK-TEST</text>
  <text x="1430" y="190" text-anchor="middle" font-family="Inter,Arial" font-size="58" font-weight="900" fill="#0f6674">LIVE</text>
  <text x="1290" y="375" text-anchor="middle" font-family="Inter,Arial" font-size="40" font-weight="900" fill="#172934">LAUNCHED LATE 2024</text>
  <text x="820" y="560" text-anchor="middle" font-family="Inter,Arial" font-size="42" font-weight="800" fill="#172934">A BACK-TEST IS EVIDENCE OF A RULE · NOT A CLEAN TRACK RECORD</text>
</g>''',
        "S&P Dow Jones Indices · Market Leaders brochure · launch date and back-tested history",
        {"launch": "late_2024", "history": "mostly_backtested"},
        "2026-06-30",
    )
    cards["evidence-market-leaders-drawdown-v1"] = (
        "Better Full-Period Returns Did Not Remove Drawdown",
        "Risk caveat",
        '''<g transform="translate(150 260)" filter="url(#shadow)">
  <rect x="0" y="0" width="1570" height="590" rx="34" fill="#173d58"/>
  <path d="M90 160L260 130L430 180L590 145L760 420L930 255L1100 230L1270 160L1480 110" fill="none" stroke="#f5c34f" stroke-width="18"/>
  <path d="M90 210L260 185L430 230L590 205L760 355L930 285L1100 255L1270 205L1480 170" fill="none" stroke="#95d4d2" stroke-width="18"/>
  <line x1="760" y1="95" x2="760" y2="485" stroke="#d36a4a" stroke-width="8" stroke-dasharray="18 14"/>
  <text x="760" y="535" text-anchor="middle" font-family="Inter,Arial" font-size="38" font-weight="900" fill="#fff6df">DEEPER MAXIMUM DRAWDOWN</text>
  <text x="130" y="85" font-family="Inter,Arial" font-size="28" fill="#f5c34f">MARKET LEADERS</text><text x="470" y="85" font-family="Inter,Arial" font-size="28" fill="#95d4d2">S&amp;P 500</text>
</g>''',
        "S&P Dow Jones Indices · Market Leaders brochure · illustrated full-period drawdown comparison",
        {"comparison": "market_leaders_deeper_max_drawdown"},
        "2026-06-30",
    )
    cards["evidence-concentrated-selection-risk-v1"] = (
        "Concentration Replaces Dilution With Selection Risk",
        "Counterargument",
        '''<g transform="translate(150 250)" filter="url(#shadow)">
  <circle cx="780" cy="100" r="100" fill="#d3a329"/><text x="780" y="115" text-anchor="middle" font-family="Inter,Arial" font-size="38" font-weight="900" fill="#172934">TOP STOCK</text>
  <path d="M780 200V300M780 300H180M780 300H1380" fill="none" stroke="#173d58" stroke-width="18"/>
  <g font-family="Inter,Arial" font-size="30" font-weight="900" text-anchor="middle"><rect x="30" y="370" width="330" height="220" rx="28" fill="#d36a4a"/><text x="195" y="490" fill="#fff6df">ACCOUNTING</text><rect x="390" y="370" width="330" height="220" rx="28" fill="#173d58"/><text x="555" y="490" fill="#fff6df">REGULATION</text><rect x="750" y="370" width="330" height="220" rx="28" fill="#0f6674"/><text x="915" y="490" fill="#fff6df">TECH SHIFT</text><rect x="1110" y="370" width="330" height="220" rx="28" fill="#786a58"/><text x="1275" y="490" fill="#fff6df">VALUATION</text></g>
  <text x="780" y="700" text-anchor="middle" font-family="Inter,Arial" font-size="42" font-weight="900" fill="#172934">ONE FAILURE CAN ERASE YEARS OF EXCESS RETURN</text>
</g>''',
        "Episode countercase · qualitative risk map",
        {"classification": "sourced_interpretation"},
        "2026-08-08",
    )
    cards["evidence-defensive-sleeve-risk-v1"] = (
        "Defensive Assets Do Not Promise Defense",
        "Correlation risk",
        '''<g transform="translate(130 260)" filter="url(#shadow)">
  <g font-family="Inter,Arial" font-size="34" font-weight="900" text-anchor="middle"><circle cx="190" cy="150" r="130" fill="#173d58"/><text x="190" y="165" fill="#fff6df">BONDS</text><circle cx="570" cy="150" r="130" fill="#d3a329"/><text x="570" y="165" fill="#172934">GOLD</text><circle cx="950" cy="150" r="130" fill="#0f6674"/><text x="950" y="165" fill="#fff6df">CASH</text><circle cx="1330" cy="150" r="130" fill="#786a58"/><text x="1330" y="145" fill="#fff6df">SOVEREIGN</text><text x="1330" y="185" fill="#fff6df">RISK</text></g>
  <path d="M190 280L760 560M570 280L760 560M950 280L760 560M1330 280L760 560" stroke="#d36a4a" stroke-width="18"/>
  <circle cx="760" cy="590" r="130" fill="#b94c38"/><text x="760" y="580" text-anchor="middle" font-family="Inter,Arial" font-size="34" font-weight="900" fill="#fff6df">STRESS</text><text x="760" y="625" text-anchor="middle" font-family="Inter,Arial" font-size="28" fill="#fff6df">CORRELATIONS MOVE</text>
</g>''',
        "Episode countercase · defensive assets may fail together under stress",
        {"classification": "sourced_interpretation"},
        "2026-08-08",
    )
    cards["evidence-equal-weight-countercase-v1"] = (
        "Sometimes the Reserves Become the Starters",
        "Equal-weight countercase",
        '''<g transform="translate(140 250)" filter="url(#shadow)">
  <rect x="0" y="0" width="1580" height="620" rx="34" fill="#173d58"/>
  <g fill="#d7c8ad">''' + ''.join(f'<circle cx="{90 + (i % 12) * 125}" cy="{120 + (i // 12) * 145}" r="38"/>' for i in range(36)) + '''</g>
  <g fill="#f5c34f"><circle cx="90" cy="120" r="54"/><circle cx="215" cy="120" r="54"/><circle cx="340" cy="120" r="54"/></g>
  <path d="M210 515C430 420 680 560 870 410S1230 260 1480 130" fill="none" stroke="#95d4d2" stroke-width="18"/>
  <text x="790" y="585" text-anchor="middle" font-family="Inter,Arial" font-size="35" font-weight="900" fill="#fff6df">EQUAL WEIGHT OUTPERFORMED OVER ITS LIVE HISTORY SINCE 2003</text>
</g>''',
        "S&P Dow Jones Indices · Equal Weight FAQ and February 2026 factor dashboard",
        {"live_history_start": 2003, "recent_period": "lagged_mega_cap_cycle"},
        "2026-02-28",
    )
    cards["evidence-bounded-conclusion-v1"] = (
        "The Claim Is Narrower Than the Thumbnail",
        "Bounded conclusion",
        '''<g transform="translate(145 250)" filter="url(#shadow)">
  <rect x="0" y="0" width="700" height="610" rx="34" fill="#0f6674"/><text x="350" y="110" text-anchor="middle" font-family="Inter,Arial" font-size="48" font-weight="900" fill="#fff6df">SUPPORTED</text><text x="70" y="220" font-family="Inter,Arial" font-size="31" fill="#fff6df">• Memory demand is physically constrained</text><text x="70" y="285" font-family="Inter,Arial" font-size="31" fill="#fff6df">• Indexing solves broad participation</text><text x="70" y="350" font-family="Inter,Arial" font-size="31" fill="#fff6df">• Product design should match objective</text>
  <rect x="850" y="0" width="700" height="610" rx="34" fill="#173d58"/><text x="1200" y="110" text-anchor="middle" font-family="Inter,Arial" font-size="48" font-weight="900" fill="#fff6df">NOT CLAIMED</text><text x="920" y="220" font-family="Inter,Arial" font-size="31" fill="#fff6df">• Memory stocks cannot fall</text><text x="920" y="285" font-family="Inter,Arial" font-size="31" fill="#fff6df">• Index investors should sell</text><text x="920" y="350" font-family="Inter,Arial" font-size="31" fill="#fff6df">• One model portfolio fits everyone</text>
  <path d="M775 70V560" stroke="#d3a329" stroke-width="18"/>
</g>''',
        "Episode thesis and countercase · educational framework, not investment advice",
        {"classification": "bounded_conclusion"},
        "2026-08-08",
    )

    result: dict[str, dict[str, Any]] = {}
    for asset_id, (title, kicker, body, footer, dataset, as_of) in cards.items():
        path = evidence_dir / f"{asset_id}.svg"
        path.write_text(_svg_shell(title, kicker, body, footer), encoding="utf-8")
        result[asset_id] = {
            "path": path,
            "dataset": dataset,
            "dataset_sha256": canonical_sha256(dataset),
            "as_of": as_of,
        }
    return result


def _asset_record(
    *,
    asset_id: str,
    path: Path,
    root: Path,
    kind: str,
    provider_output: bool = False,
    evidence_eligible: bool = False,
) -> dict[str, Any]:
    return {
        "id": asset_id,
        "path": path.resolve().relative_to(root.resolve()).as_posix(),
        "sha256": _sha256(path),
        "kind": kind,
        "render_eligible": True,
        "provider_output": provider_output,
        "human_promoted": True,
        "evidence_eligible": evidence_eligible,
        "review_scope": "internal_review_only",
    }


def _build_asset_map(
    repo_root: Path,
    finance_root: Path,
    evidence: Mapping[str, Mapping[str, Any]],
    semantic_catalog: Mapping[str, Any],
) -> dict[str, Any]:
    catalog = _read_json(finance_root / "asset-catalog.v1.json")
    keep = {
        "actor-worker-household-v2",
        "actor-founder-v2",
        "mechanism-index-basket-v2",
        "mechanism-balance-ledger-v1",
        "mechanism-ownership-tree-v1",
        "mechanism-economic-elevator-v1",
        "whiteboard-easel-v2",
        "whiteboard-world-v2",
        "story-neighborhood-v1",
    }
    records: dict[str, dict[str, Any]] = {}
    for raw in catalog["assets"]:
        asset_id = str(raw["asset_id"])
        if asset_id not in keep:
            continue
        path = finance_root / str(raw["path"])
        records[asset_id] = _asset_record(
            asset_id=asset_id,
            path=path,
            root=finance_root,
            kind=str(raw["kind"]),
        )
    for raw in semantic_catalog["assets"]:
        if raw.get("render_eligible") is not True:
            continue
        asset_id = str(raw["asset_id"])
        path = repo_root / str(raw["path"])
        if not path.is_file():
            raise FileNotFoundError(f"semantic asset is missing: {asset_id} -> {path}")
        records[asset_id] = _asset_record(
            asset_id=asset_id,
            path=path,
            root=finance_root,
            kind=str(raw["kind"]),
            provider_output=bool(raw.get("generated")),
            evidence_eligible=bool(raw.get("contains_factual_text")),
        )
    hero_dir = finance_root / "pilots" / EPISODE_ID / "assets" / "hero"
    hero_names = {
        "hero-wrong-bubble-v1": "hero-wrong-bubble-v1.png",
        "hero-hbm-bandwidth-v1": "hero-hbm-bandwidth-v1.png",
        "hero-fab-constraint-v1": "hero-fab-constraint-v1.png",
        "hero-contract-ovens-v1": "hero-contract-ovens-v1.png",
        "hero-korea-italy-v1": "hero-korea-italy-v1.png",
        "hero-sp500-double-failure-v1": "hero-sp500-double-failure-v1.png",
        "hero-barbell-v1": "hero-barbell-v1.png",
        "hero-countercase-v1": "hero-countercase-v1.png",
    }
    for asset_id, name in hero_names.items():
        records[asset_id] = _asset_record(
            asset_id=asset_id,
            path=hero_dir / name,
            root=finance_root,
            kind="generated_hero",
            provider_output=True,
        )
    for asset_id, item in evidence.items():
        records[asset_id] = _asset_record(
            asset_id=asset_id,
            path=Path(item["path"]),
            root=finance_root,
            kind="deterministic_evidence",
            evidence_eligible=True,
        )
    return _hashed(
        {
            "schema_version": "editorial_asset_map.v1",
            "episode_id": EPISODE_ID,
            "review_scope": "internal_review_only",
            "assets": records,
        }
    )


def _claim_refs(chapter: Chapter, excerpt: str) -> list[str]:
    lower = excerpt.casefold()
    preferred: list[str] = []
    if chapter.index == 8 and any(
        token in lower
        for token in ("market leaders", "about 16 percent", "13.6 percent", "measured volatility", "late 2024")
    ):
        preferred.append("sp500-market-leaders-comparison")
    keyword_map = [
        (("16 strategic", "take-or-pay", "one-third of its nand", "strategic agreement"), "micron-strategic-customer-agreements"),
        (("korea", "milan", "italy", "krx"), "korea-italy-listed-market-comparison"),
        (("top ten", "forty percent", "40 percent", "concentrat"), "sp500-top-ten-concentration"),
        (("19.1", "index funds", "fund assets"), "index-fund-asset-scale"),
        (("25,000", "twenty-five thousand", "one million", "15.9", "13.6", "return hurdle"), "generational-wealth-return-hurdle"),
        (("market leaders", "about 16 percent", "16.01", "back-test"), "sp500-market-leaders-comparison"),
        (("hbm", "memory", "bandwidth", "accelerator"), "memory-architecture-dependency"),
        (("supply", "capacity", "wafer", "fab"), "hbm-capacity-trade-ratio"),
        (("barbell", "defensive", "sovereign", "gold"), "concentrated-defensive-barbell-hypothesis"),
        (("equal weight", "long tail"), "equal-weight-long-tail-countercase"),
    ]
    for keywords, claim_id in keyword_map:
        if any(keyword in lower for keyword in keywords):
            preferred.append(claim_id)
    for claim_id in chapter.claim_refs:
        if claim_id not in preferred:
            preferred.append(claim_id)
    return preferred[:3]


SEMANTIC_CUE_OVERRIDES: tuple[tuple[range, str, str], ...] = (
    (range(25, 27), "wrong-bubble-elevators-v2", "ELEVATOR MECHANISMS COMPARE"),
    (range(135, 138), "shared-cause-automatic-allocation-v1", "SHARED CAUSES STAY VISIBLE"),
    (range(138, 141), "evidence-index-inclusion-gate-v1", "ENTRY GATE OPENS"),
    (range(141, 144), "evidence-float-weighting-v1", "DOLLAR FOLLOWS FLOAT VALUE"),
    (range(144, 147), "evidence-automatic-business-mix-v1", "AUTOMATIC MIX BRANCHES"),
    (range(147, 150), "evidence-diworsification-plateau-v1", "INDEPENDENT BENEFIT FLATTENS"),
    (range(150, 154), "index-roster-diworsification-v1", "STARS AND RESERVES SHARE THE ROSTER"),
    (range(154, 158), "evidence-portfolio-jobs-v1", "ONE BASKET SPLITS INTO TWO JOBS"),
    (range(158, 161), "evidence-sp500-concentration-v1", "TOP TEN DOMINATE THE OUTCOME"),
    (range(161, 163), "evidence-index-tail-absorption-v1", "THE LONG TAIL ABSORBS THE REST"),
    (range(163, 166), "index-roster-diworsification-v1", "ROSTER COST RETURNS"),
    (range(166, 169), "evidence-portfolio-jobs-v1", "UPSIDE AND DEFENSE SEPARATE"),
    (range(27, 28), "belief-versus-support-v2", "IDENTICAL PRICE PATHS SPLIT BY CAUSE"),
    (range(28, 29), "safe-default-inspection-v1", "INSPECTION MOVES BELOW THE LABEL"),
    (range(29, 30), "memory-three-supports-v1", "MEMORY CABLE BRAIDS"),
    (range(30, 33), "index-fund-weighted-inflows-v2", "INDEX WEIGHTS AND FLOWS OPEN"),
    (range(169, 173), "evidence-portfolio-jobs-v1", "DEFINE THE PRODUCT'S JOB"),
    (range(173, 177), "evidence-wealth-target-path-v1", "TARGET PATH OPENS"),
    (range(177, 181), "evidence-return-ten-percent-v1", "TEN-PERCENT PATH STOPS SHORT"),
    (range(181, 189), "evidence-return-comparison-v1", "RETURN PATHS SEPARATE"),
    (range(189, 192), "evidence-wealth-levers-v1", "WEALTH LEVERS BRANCH"),
    (range(192, 198), "evidence-index-scale-v1", "INDEX MACHINE SCALES"),
    (range(198, 206), "evidence-portfolio-jobs-v1", "ONE BASKET SPLITS INTO TWO JOBS"),
    (range(206, 212), "two-sleeve-barbell-v1", "DEFENSIVE SLEEVE SEPARATES"),
    (range(212, 216), "evidence-market-leaders-basket-v1", "FIFTY-COMPANY FILTER OPENS"),
    (range(216, 219), "evidence-market-leaders-v1", "RETURNS COMPARE"),
    (range(219, 222), "evidence-market-leaders-backtest-v1", "LIVE WINDOW SEPARATES FROM BACKTEST"),
    (range(222, 225), "evidence-market-leaders-drawdown-v1", "DRAWDOWN DEEPENS"),
    (range(225, 231), "evidence-portfolio-jobs-v1", "QUALITY BASKET AND DEFENSE SEPARATE"),
    (range(231, 236), "evidence-defensive-sleeve-risk-v1", "COSTS AND TRACKING RISK ACCUMULATE"),
    (range(236, 242), "evidence-concentrated-selection-risk-v1", "COMPANY RISK BRANCHES"),
    (range(242, 246), "evidence-defensive-sleeve-risk-v1", "DEFENSIVE CORRELATIONS CONVERGE"),
    (range(246, 254), "evidence-equal-weight-countercase-v1", "INDEX RESERVES ROTATE FORWARD"),
    (range(254, 259), "memory-three-failure-points-v1", "MEMORY FAILURE POINTS OPEN"),
    (range(259, 262), "belief-versus-support-v2", "REAL TECHNOLOGY SEPARATES FROM PRICE PAID"),
    (range(262, 264), "evidence-bounded-conclusion-v1", "THESIS NARROWS TO ITS BOUNDS"),
    (range(284, 286), "wrong-bubble-elevators-v2", "FINAL ELEVATOR CALLBACK"),
    (range(286, 288), "memory-three-supports-v1", "MEMORY CABLE RESOLVES"),
    (range(288, 290), "index-fund-weighted-inflows-v2", "INDEX MACHINE REOPENS"),
    (range(290, 291), "evidence-bounded-conclusion-v1", "TWO JOBS CLOSE THE LOOP"),
)


def _resolve_visual(cue_number: int, semantic_state: Mapping[str, Any]) -> tuple[str, str]:
    """Resolve a cue from the approved semantic map plus explicit review fixes.

    No keyword search or modulo rotation is permitted.  Overrides are bound to
    canonical cue numbers, which in turn are bound to exact narration words.
    """

    for cue_range, asset_id, action in SEMANTIC_CUE_OVERRIDES:
        if cue_number in cue_range:
            return asset_id, action
    asset_id = str(semantic_state.get("asset_id") or "")
    if not asset_id:
        raise ValueError(f"semantic cue {cue_number} has no resolved asset")
    return asset_id, str(semantic_state.get("semantic_action") or "LOCKED SEMANTIC HOLD")


def _full_layer(asset_id: str, action: str) -> dict[str, Any]:
    return {"asset_id": asset_id, "role": "world", "z_index": 0, "action": action}


def _composition_layers(asset_id: str, local_index: int) -> list[dict[str, Any]]:
    # Semantic-v2 assets are authored full-frame plates.  Do not shrink them
    # into a generic whiteboard or decorate them with unrelated cast stickers.
    return [_full_layer(asset_id, "locked")]


def _overlay_text(chapter: Chapter, local_index: int, excerpt: str) -> str | None:
    if local_index == 0:
        return chapter.title.upper()
    lower = excerpt.casefold()
    phrases = [
        ("bubble", "PRICE MOVE ≠ BUBBLE MECHANISM"),
        ("memory wall", "THE BOTTLENECK MOVED"),
        ("take-or-pay", "BUYERS COMMITTED BEFORE DELIVERY"),
        ("concentrated", "THE BENEFIT DISAPPEARS"),
        ("diluted", "THE DRAG REMAINS"),
        ("diworsification", "MORE NAMES. NOT NECESSARILY MORE PROTECTION."),
        ("15.9", "THE HURDLE IS HIGHER THAN THE DEFAULT"),
        ("separate jobs", "UPSIDE AND DEFENSE ARE DIFFERENT JOBS"),
        ("look under the elevator", "LOOK UNDER THE ELEVATOR"),
        ("find the cable", "FIND THE CABLE"),
    ]
    for token, text in phrases:
        if token in lower:
            return text
    return None


def _source_label(claim: Mapping[str, Any]) -> str:
    locators = list(claim.get("source_locators") or [])
    if not locators:
        return str(claim.get("claim_id") or "")
    first = locators[0]
    publisher = str(first.get("publisher") or first.get("title") or "Source")
    as_of = str(claim.get("as_of") or first.get("published_at") or "undated")
    return f"{publisher} · {as_of} · {claim.get('claim_id')}"


def _camera(kind: str, duration: float, direction: str) -> dict[str, Any]:
    if kind == "locked" or duration < 1.0:
        return {
            "kind": "locked",
            "amount": 0.0,
            "easing": "smoothstep",
            "direction": "toward_focal_point",
            "hold_in_s": round(duration, 6),
            "move_s": 0.0,
            "hold_out_s": 0.0,
        }
    hold_in = min(0.22, duration * 0.12)
    hold_out = min(0.38, duration * 0.18)
    return {
        "kind": kind,
        "amount": 0.018 if kind != "lateral_reveal" else 0.014,
        "easing": "smoothstep",
        "direction": direction,
        "hold_in_s": round(hold_in, 6),
        "move_s": round(duration - hold_in - hold_out, 6),
        "hold_out_s": round(hold_out, 6),
    }


def _build_outputs(
    *,
    repo_root: Path,
    finance_root: Path,
    pilot_root: Path,
    engine_root: Path,
) -> dict[str, Path]:
    narration_path = pilot_root / "audio" / "current-bubble-mechanism-narration-master.v1.json"
    audio_manifest_path = pilot_root / "audio" / "canonical-audio.v1.json"
    words_path = pilot_root / "audio" / "canonical" / "history_episode_1_master.words.json"
    audio_path = pilot_root / "audio" / "canonical" / "history_episode_1_master.mp3"
    brief_path = pilot_root / "episode-brief.v1.json"
    ledger_path = pilot_root / "claim-ledger.v1.json"
    narration = _read_json(narration_path)
    audio_manifest = _read_json(audio_manifest_path)
    word_payload = _read_json(words_path)
    brief = _read_json(brief_path)
    ledger = _read_json(ledger_path)
    words = list(word_payload["words"])
    audio_duration = float(audio_manifest["duration_s"])
    if _sha256(audio_path) != str(audio_manifest["audio_sha256"]):
        raise ValueError("canonical audio hash is stale")
    if str(audio_manifest["narration_hash"]) != str(narration["narration_hash"]):
        raise ValueError("canonical narration and audio hashes differ")
    if float(words[-1]["end_s"]) != audio_duration:
        raise ValueError("word timing does not end at the audio duration")

    edit_root = pilot_root / "edit" / "word-timed-v1"
    semantic_root = pilot_root / "edit" / "semantic-v2"
    semantic_catalog = _read_json(semantic_root / "asset-catalog.v2.json")
    semantic_cue_map = _read_json(semantic_root / "dense-visual-cue-map.v1.json")
    operator_research_path = Path(
        "C:/Users/Snipe/Downloads/Outreach Program/docs/research/"
        "The Decadal Realignment of Global Semiconductors - memory.md"
    )
    if not operator_research_path.is_file():
        raise FileNotFoundError(f"operator research packet is missing: {operator_research_path}")
    market_data_path = semantic_root / "market-data-yfinance-trailing-2026-08-07.v1.json"
    if not market_data_path.is_file():
        raise FileNotFoundError(f"dated yfinance packet is missing: {market_data_path}")
    semantic_states = {
        str(item["cue_id"]): item for item in semantic_cue_map.get("states", [])
    }
    evidence = _evidence_svgs(edit_root / "evidence")
    asset_map = _build_asset_map(repo_root, finance_root, evidence, semantic_catalog)
    asset_map_path = edit_root / "asset-map.v1.json"
    _write_json(asset_map_path, asset_map)
    chapters = _build_chapters(narration, words)
    claims = {str(item["claim_id"]): item for item in ledger["claims"]}

    pacing_recipe = _hashed(
        {
            "schema_version": "editorial_pacing_recipe.v1",
            "id": "finance-causal-paper-theatre-v1",
            "preferred_shot_duration_s": [2.15, 4.6],
            "maximum_shot_duration_s": 5.5,
            "max_consecutive_same_scale": 2,
            "max_consecutive_moving_shots": 2,
            "max_information_surfaces": 0,
            "max_non_evidence_prop_layers": 600,
            "motion_density": "moderate",
            "transition_policy": "motivated_only",
            "chapter_reset_policy": "paper_reset",
            "provider_motion_policy": "shot_level_exception_only",
            "reference_policy": "abstract_structure_only",
        }
    )
    pacing_recipe = validate_editorial_pacing_recipe(pacing_recipe)
    pacing_path = edit_root / "pacing-recipe.v1.json"
    _write_json(pacing_path, pacing_recipe)

    overlays: dict[str, dict[str, Any]] = {}
    cues: list[dict[str, Any]] = []
    shots: list[dict[str, Any]] = []
    beat_records: list[dict[str, Any]] = []
    manifest_assets: list[dict[str, Any]] = []
    shot_counter = 0
    scales = ("wide", "medium", "close", "medium_detail", "insert", "medium")
    cameras = ("push_settle", "locked", "lateral_reveal", "push_settle", "locked")
    directions = ("toward_focal_point", "right", "left", "toward_focal_point")
    chapter_bundle_hashes: list[str] = []
    chapter_bundles: list[dict[str, Any]] = []
    short_start = chapters[6].start_word
    short_end = chapters[6].end_word

    for chapter in chapters:
        bundle = _hashed(
            {
                "schema_version": "scene_bundle.v1",
                "id": f"finance-scene-{chapter.index + 1:02d}",
                "episode_id": EPISODE_ID,
                "chapter": chapter.segment_id,
            }
        )
        chapter_bundles.append(bundle)
        chapter_bundle_hashes.append(bundle["artifact_hash"])
        ranges = _split_chapter(chapter, words, audio_duration)
        for local_index, (start_word, end_word) in enumerate(ranges):
            shot_counter += 1
            start_s = float(words[start_word]["start_s"])
            end_s = _boundary_end_s(words, end_word, audio_duration)
            duration = round(end_s - start_s, 6)
            excerpt = " ".join(str(words[index]["w"]) for index in range(start_word, end_word + 1))
            cue_id = f"cbm-cue-{shot_counter:03d}"
            beat_id = f"cbm-beat-{shot_counter:03d}"
            semantic_state = semantic_states.get(cue_id)
            if semantic_state is None:
                raise ValueError(f"missing semantic-v2 resolution for {cue_id}")
            if _normalize(str(semantic_state.get("excerpt") or "")) != _normalize(excerpt):
                raise ValueError(f"semantic-v2 narration drift for {cue_id}")
            asset_id, semantic_action = _resolve_visual(shot_counter, semantic_state)
            if asset_id not in asset_map["assets"]:
                raise ValueError(f"resolved asset is not registered: {cue_id} -> {asset_id}")
            layers = _composition_layers(asset_id, local_index)
            used_ids = [str(layer["asset_id"]) for layer in layers]
            claim_refs = _claim_refs(chapter, excerpt)
            is_evidence = asset_id.startswith("evidence-")
            is_story = asset_id == "story-neighborhood-v1" or asset_id.startswith("hero-")
            state_type = "evidence" if is_evidence else "narrative" if is_story else "mechanism"
            visual_world = "evidence" if is_evidence else "story" if is_story else "mechanism"
            overlay_ids: list[str] = []
            # The full-frame plates and deterministic evidence cards already
            # carry their authored visual hierarchy.  Generic action chips
            # obscured those surfaces and repeated the narration without
            # explaining it, so only specifically authored numeric/mechanism
            # overlays are permitted below.
            headline = None
            if headline:
                overlay_id = f"overlay-headline-{shot_counter:03d}"
                overlays[overlay_id] = {
                    "kind": "text",
                    "text": headline,
                    "position": "top",
                    "from_s": 0.14,
                    "duration_s": max(0.5, duration - 0.28),
                    "style": {
                        "color": "#fff6df",
                        "background": "rgba(7,26,44,0.76)",
                        "borderLeft": "none",
                        "borderRadius": "6px",
                        "fontSize": 30,
                        "letterSpacing": 0.6,
                        "right": "auto",
                        "maxWidth": "54%",
                    },
                }
                overlay_ids.append(overlay_id)
            if claim_refs:
                citation_id = f"citation-{shot_counter:03d}"
                overlays[citation_id] = {
                    "kind": "citation",
                    "citation_id": claim_refs[0],
                    "text": _source_label(claims[claim_refs[0]]),
                    "position": "rail",
                    "from_s": min(0.7, duration * 0.2),
                    "duration_s": max(0.3, duration - min(0.7, duration * 0.2)),
                }
                overlay_ids.append(citation_id)
            if shot_counter in {2, 3}:
                return_cards = (
                    ("MU", "+685.7%", "7.4%"),
                    ("KOSPI", "+93.9%", "39.6%"),
                    ("S&P 500", "+22.4%", "72.4%"),
                )
                for card_index, (label, value, left) in enumerate(return_cards):
                    overlay_id = f"overlay-return-{shot_counter:03d}-{card_index + 1}"
                    overlays[overlay_id] = {
                        "kind": "text",
                        "text": f"{label}\n{value}",
                        "position": "top",
                        "from_s": 0.12 + card_index * 0.18,
                        "duration_s": max(0.5, duration - 0.28 - card_index * 0.18),
                        "style": {
                            "left": left,
                            "right": "auto",
                            "top": "77%",
                            "width": "20%",
                            "padding": "0",
                            "background": "transparent",
                            "borderLeft": "none",
                            "color": "#fff6df",
                            "fontSize": 28,
                            "fontWeight": 900,
                            "lineHeight": 1.05,
                            "textAlign": "center",
                            "whiteSpace": "pre-line",
                            "textShadow": "0 2px 3px rgba(0,0,0,0.52)",
                        },
                    }
                    overlay_ids.append(overlay_id)
            if shot_counter in {57, 58}:
                overlay_id = f"overlay-hbm-trade-ratio-{shot_counter:03d}"
                overlays[overlay_id] = {
                    "kind": "text",
                    "text": "1 HBM wafer allocation\n→ 2–3× less standard-DRAM bit output",
                    "position": "top",
                    "from_s": 0.22,
                    "duration_s": max(0.5, duration - 0.44),
                    "style": {
                        "left": "55%",
                        "right": "auto",
                        "top": "12%",
                        "width": "37%",
                        "padding": "13px 17px",
                        "background": "rgba(7,26,44,0.82)",
                        "borderLeft": "none",
                        "borderRadius": "8px",
                        "color": "#fff6df",
                        "fontSize": 27,
                        "fontWeight": 850,
                        "lineHeight": 1.12,
                        "whiteSpace": "pre-line",
                    },
                }
                overlay_ids.append(overlay_id)
            entry_action = "paper reveal" if local_index == 0 else "hard semantic cut"
            micro_action = (
                "deterministic chart resolves the spoken number"
                if is_evidence
                else "foreground actor or mechanism completes its authored move"
                if len(layers) > 1
                else "bounded camera settles on the causal object"
            )
            short_membership = ["short-sp500-double-failure"] if chapter.index == 6 else []
            cues.append(
                {
                    "cue_id": cue_id,
                    "start_word": start_word,
                    "end_word": end_word,
                    "start_s": round(start_s, 6),
                    "end_s": round(end_s, 6),
                    "excerpt": excerpt,
                    "claim_refs": claim_refs,
                    "state_type": state_type,
                    "visual_world": visual_world,
                    "entry_action": entry_action,
                    "micro_events": [
                        {"at_s": round(min(duration * 0.28, 0.9), 3), "action": micro_action},
                        {"at_s": round(max(duration * 0.68, duration - 1.25), 3), "action": "prepare the causal match into the next state"},
                    ],
                    "exit_transition": "hard cut on the next semantic phrase",
                    "fact_surface": asset_id if is_evidence else None,
                    "short_membership": short_membership,
                }
            )
            beat_records.append(
                {"beat_id": beat_id, "narration_excerpt": excerpt, "claim_refs": claim_refs}
            )
            camera_kind = cameras[shot_counter % len(cameras)]
            camera = _camera(camera_kind, duration, directions[shot_counter % len(directions)])
            purpose = (
                "hook"
                if shot_counter <= 4
                else "chapter_reset"
                if local_index == 0
                else "reveal"
                if is_evidence
                else "explain"
            )
            match_cut_motifs = {
                173: "wealth_path",
                177: "wealth_path",
                181: "wealth_path",
                189: "wealth_path",
                212: "quality_basket",
                216: "quality_basket",
                219: "quality_basket",
                222: "quality_basket",
                225: "quality_basket",
                236: "risk_branches",
                242: "risk_branches",
                246: "risk_branches",
                254: "risk_branches",
                259: "price_versus_cause",
                262: "price_versus_cause",
            }
            if shot_counter in match_cut_motifs:
                transition_in = {
                    "kind": "match_cut",
                    "reason": "shared causal object changes state on the spoken turn",
                    "duration_s": 0.0,
                    "motif_id": match_cut_motifs[shot_counter],
                }
            elif local_index == 0 and shot_counter > 1:
                transition_in = {
                    "kind": "paper_wipe",
                    "reason": "foreground paper edge marks a new causal chapter over the visible world",
                    "duration_s": 0.28,
                }
            else:
                transition_in = {"kind": "hard_cut", "reason": "spoken semantic turn", "duration_s": 0.0}
            shot = {
                "shot_id": f"finance-shot-{shot_counter:03d}",
                "parent_beat_ids": [beat_id],
                "parent_scene_bundle_id": str(bundle["id"]),
                "start_s": round(start_s, 6),
                "duration_s": duration,
                "word_range": {"start_index": start_word, "end_index": end_word},
                "narration_excerpt": excerpt,
                "visual_intent": "evidence" if is_evidence else "explanation" if not is_story else "scenic",
                "required_visual_actions": [
                    {
                        "kind": "list_item_popout" if is_evidence else "character_action" if len(layers) > 1 else "object_cutaway",
                        "subject": asset_id,
                    }
                ],
                "purpose": purpose,
                "shot_scale": scales[shot_counter % len(scales)],
                "focal_point": {"x": 0.48 if local_index % 2 == 0 else 0.57, "y": 0.47},
                "layers": layers,
                "subject_action": semantic_action.casefold().replace(" ", "_"),
                "ambient_actions": [],
                "information_reveal": "none",
                "camera": camera,
                "transition_in": transition_in,
                "transition_out": {"kind": "hard_cut", "reason": "next spoken claim", "duration_s": 0.0},
                "audio_bridge": "continuous_narration",
                "provider_motion": {"requirement": "none", "fallback": "local_layer_motion"},
                "overlay_ids": overlay_ids,
                "uniqueness_signature": f"finance-{shot_counter:03d}-{asset_id}-{scales[shot_counter % len(scales)]}-{camera_kind}",
            }
            shots.append(shot)
            for used_id in used_ids:
                manifest_assets.append(
                    {
                        "cue_id": cue_id,
                        "asset_id": used_id,
                        "sha256": str(asset_map["assets"][used_id]["sha256"]),
                    }
                )

    semantic_resolution = _hashed(
        {
            "schema_version": "semantic_resolution_map.v3",
            "episode_id": EPISODE_ID,
            "canonical_dense_map_hash": str(semantic_cue_map.get("artifact_hash") or ""),
            "research_inputs": [
                {
                    "kind": "operator_verified_research",
                    "path": "C:/Users/Snipe/Downloads/Outreach Program/docs/research/The Decadal Realignment of Global Semiconductors - memory.md",
                    "use": "mechanism corroboration; on-screen values remain claim-ledger bound",
                },
                {
                    "kind": "dated_market_data",
                    "path": "edit/semantic-v2/market-data-yfinance-trailing-2026-08-07.v1.json",
                    "use": "timely return comparisons",
                },
            ],
            "cues": [
                {
                    "cue_id": cue["cue_id"],
                    "start_word": cue["start_word"],
                    "end_word": cue["end_word"],
                    "start_s": cue["start_s"],
                    "end_s": cue["end_s"],
                    "asset_id": shots[index]["layers"][0]["asset_id"],
                    "semantic_action": (
                        _resolve_visual(index + 1, semantic_states[cue["cue_id"]])[1]
                    ),
                    "claim_refs": cue["claim_refs"],
                }
                for index, cue in enumerate(cues)
            ],
        }
    )
    _write_json(semantic_root / "remotion-semantic-resolution-map.v3.json", semantic_resolution)
    research_supplement = _hashed(
        {
            "schema_version": "finance_research_evidence_supplement.v1",
            "episode_id": EPISODE_ID,
            "inputs": [
                {
                    "kind": "operator_verified_research",
                    "path": operator_research_path.as_posix(),
                    "sha256": _sha256(operator_research_path),
                },
                {
                    "kind": "yfinance_adjusted_close_packet",
                    "path": market_data_path.relative_to(pilot_root).as_posix(),
                    "sha256": _sha256(market_data_path),
                    "as_of": "2026-08-07",
                },
            ],
            "visual_claims": [
                {
                    "id": "hbm-wafer-bit-output-tradeoff",
                    "display": "1 HBM wafer allocation → 2–3× less standard-DRAM bit output",
                    "source_input": operator_research_path.as_posix(),
                    "locator": "High-Bandwidth Memory and the Standard DRAM Deficit / The Cannibalization Mechanics of Advanced Wafers",
                    "cue_ids": ["cbm-cue-057", "cbm-cue-058"],
                    "classification": "operator_verified_research",
                },
                {
                    "id": "timely-trailing-return-comparison",
                    "display": "MU +685.7% · KOSPI +93.9% · S&P 500 +22.4%",
                    "source_input": market_data_path.relative_to(pilot_root).as_posix(),
                    "locator": "one-year adjusted-close windows ending 2026-08-07",
                    "cue_ids": ["cbm-cue-002", "cbm-cue-003"],
                    "classification": "dated_calculation",
                },
            ],
        }
    )
    research_supplement_path = semantic_root / "research-evidence-supplement.v1.json"
    _write_json(research_supplement_path, research_supplement)

    # start_s in the rendering plan is relative to the first selected word.
    for shot in shots:
        shot["start_s"] = round(float(shot["start_s"]) - float(words[0]["start_s"]), 6)
    beat_plan = _hashed(
        {
            "schema_version": "editorial_beat_plan.v1",
            "episode_id": EPISODE_ID,
            "duration_s": audio_duration,
            "beat_count": len(beat_records),
            "beats": beat_records,
        }
    )
    flow_graph = _hashed(
        {
            "schema_version": "scene_flow_graph.v1",
            "id": "current-bubble-causal-flow-v1",
            "episode_id": EPISODE_ID,
            "nodes": [str(bundle["id"]) for bundle in chapter_bundles],
            "edges": [
                {"from": str(chapter_bundles[index]["id"]), "to": str(chapter_bundles[index + 1]["id"])}
                for index in range(len(chapter_bundles) - 1)
            ],
        }
    )
    plan = _hashed(
        {
            "schema_version": "editorial_motion_plan.v1",
            "source_storyboard_hash": str(narration["source_storyboard_hash"]),
            "source_beat_plan_hash": str(beat_plan["artifact_hash"]),
            "scene_bundle_hashes": chapter_bundle_hashes,
            "scene_flow_graph_hash": str(flow_graph["artifact_hash"]),
            "asset_map_hash": str(asset_map["artifact_hash"]),
            "audio_manifest_hash": canonical_sha256(audio_manifest),
            "pacing_recipe_hash": str(pacing_recipe["artifact_hash"]),
            "duration_s": audio_duration,
            "source_start_s": float(words[0]["start_s"]),
            "shots": shots,
            "provider_calls": 0,
            "revision_only": True,
        }
    )
    plan = validate_editorial_motion_plan(plan, known_asset_ids=set(asset_map["assets"]))
    plan_path = edit_root / "editorial-motion-plan.v1.json"
    _write_json(plan_path, plan)
    _write_json(edit_root / "editorial-beat-plan.v1.json", beat_plan)
    _write_json(edit_root / "scene-flow-graph.v1.json", flow_graph)
    _write_json(edit_root / "scene-bundles.v1.json", {"bundles": chapter_bundles})
    _write_json(edit_root / "overlay-map.v1.json", overlays)

    words_sha = _sha256(words_path)
    cue_sheet = _hashed(
        {
            "schema_version": "finance_visual_cue_sheet.v1",
            "episode_id": EPISODE_ID,
            "narration": {
                "audio_sha256": str(audio_manifest["audio_sha256"]),
                "words_sha256": words_sha,
                "word_count": len(words),
                "duration_s": audio_duration,
            },
            "caption_safe_band": {"top": 0.88, "bottom": 0.985},
            "short_ranges": [
                {
                    "short_id": "short-sp500-double-failure",
                    "start_word": short_start,
                    "end_word": short_end,
                    "start_s": float(words[short_start]["start_s"]),
                    "end_s": _boundary_end_s(words, short_end, audio_duration),
                }
            ],
            "cues": cues,
        }
    )
    _schema_validate(engine_root, cue_sheet, "finance_visual_cue_sheet.schema.json")
    cue_path = edit_root / "finance-visual-cue-sheet.v1.json"
    _write_json(cue_path, cue_sheet)

    chart_claims = {
        "evidence-memory-contracts-v1": ["micron-strategic-customer-agreements"],
        "evidence-sp500-concentration-v1": ["sp500-top-ten-concentration"],
        "evidence-index-inclusion-gate-v1": ["sp500-top-ten-concentration"],
        "evidence-float-weighting-v1": ["sp500-top-ten-concentration", "index-fund-asset-scale"],
        "evidence-automatic-business-mix-v1": ["sp500-hidden-bubble-risk-inference"],
        "evidence-diworsification-plateau-v1": ["sp500-hidden-bubble-risk-inference"],
        "evidence-index-tail-absorption-v1": ["sp500-top-ten-concentration", "sp500-hidden-bubble-risk-inference"],
        "evidence-korea-italy-v1": ["korea-italy-listed-market-comparison"],
        "evidence-return-hurdle-v1": ["generational-wealth-return-hurdle", "sp500-trailing-return-snapshot"],
        "evidence-market-leaders-v1": ["sp500-market-leaders-comparison"],
        "evidence-index-scale-v1": ["index-fund-asset-scale"],
        "evidence-wealth-target-path-v1": ["generational-wealth-return-hurdle"],
        "evidence-return-ten-percent-v1": ["generational-wealth-return-hurdle"],
        "evidence-return-comparison-v1": ["generational-wealth-return-hurdle", "sp500-trailing-return-snapshot"],
        "evidence-wealth-levers-v1": ["generational-wealth-return-hurdle"],
        "evidence-portfolio-jobs-v1": ["sp500-hidden-bubble-risk-inference", "concentrated-defensive-barbell-hypothesis"],
        "evidence-market-leaders-basket-v1": ["sp500-market-leaders-comparison"],
        "evidence-market-leaders-backtest-v1": ["sp500-market-leaders-comparison"],
        "evidence-market-leaders-drawdown-v1": ["sp500-market-leaders-comparison"],
        "evidence-concentrated-selection-risk-v1": ["sp500-countercase"],
        "evidence-defensive-sleeve-risk-v1": ["concentrated-defensive-barbell-hypothesis", "sp500-countercase"],
        "evidence-equal-weight-countercase-v1": ["equal-weight-long-tail-countercase"],
        "evidence-bounded-conclusion-v1": ["memory-countercase", "sp500-countercase"],
    }
    edit_manifest = _hashed(
        {
            "schema_version": "finance_edit_manifest.v1",
            "episode_id": EPISODE_ID,
            "brief_hash": str(brief["artifact_hash"]),
            "claim_ledger_hash": str(ledger["artifact_hash"]),
            "research_supplement_hash": str(research_supplement["artifact_hash"]),
            "audio_sha256": str(audio_manifest["audio_sha256"]),
            "words_sha256": words_sha,
            "cue_sheet_hash": str(cue_sheet["artifact_hash"]),
            "assets": manifest_assets,
            "charts": [
                {
                    "chart_id": asset_id,
                    "dataset_sha256": str(item["dataset_sha256"]),
                    "claim_refs": chart_claims[asset_id],
                    "as_of": str(item["as_of"]),
                }
                for asset_id, item in evidence.items()
            ],
            "motion_presets": [
                "money-transfer",
                "ownership-reveal",
                "balance-sheet-open",
                "index-expand",
                "distribution-split",
                "risk-transfer",
                "evidence-lock",
            ],
            "review_state": "draft",
            "render_eligible": True,
        }
    )
    _schema_validate(engine_root, edit_manifest, "finance_edit_manifest.schema.json")
    edit_manifest_path = edit_root / "finance-edit-manifest.v1.json"
    _write_json(edit_manifest_path, edit_manifest)

    revision_dir = pilot_root / "animatic" / "revisions" / "full-review-v1"
    qc = run_editorial_motion_qc(
        plan,
        pacing_recipe=pacing_recipe,
        asset_map=asset_map,
        asset_root=finance_root,
        revision_dir=revision_dir,
        job_dir=pilot_root,
        check_files=True,
    )
    if qc["overall"] != "pass":
        failures = [item["detail"] for item in qc["checks"] if item["status"] == "fail"]
        raise ValueError("editorial QC failed: " + "; ".join(failures))
    revision_dir.mkdir(parents=True, exist_ok=True)
    public_assets = revision_dir / "public" / "assets"
    public_audio = revision_dir / "public" / "audio"
    public_assets.mkdir(parents=True, exist_ok=True)
    public_audio.mkdir(parents=True, exist_ok=True)
    renderer_assets: dict[str, str] = {}
    used_asset_ids = sorted({str(layer["asset_id"]) for shot in shots for layer in shot["layers"]})
    for asset_id in used_asset_ids:
        record = asset_map["assets"][asset_id]
        source = finance_root / str(record["path"])
        suffix = source.suffix.casefold()
        destination = public_assets / f"{asset_id}{suffix}"
        shutil.copy2(source, destination)
        renderer_assets[asset_id] = destination.relative_to(revision_dir / "public").as_posix()
    audio_destination = public_audio / "canonical.mp3"
    shutil.copy2(audio_path, audio_destination)
    props = {
        "plan": plan,
        "asset_map": renderer_assets,
        "canonical_audio": {
            "path": audio_destination.relative_to(revision_dir / "public").as_posix(),
            "start_s": 0,
            "volume": 1,
        },
        "overlay_map": overlays,
        "caption_policy": "burned_in",
        "citation_policy": "credits_only",
        "diagnostic": False,
        "render_profile": {"width": 1920, "height": 1080, "fps": 24, "label": "review-1080p-12-on-24"},
    }
    props_path = revision_dir / "remotion-props.json"
    _write_json(props_path, props)
    proof_props_path = revision_dir / "remotion-props-proof.json"
    _write_json(
        proof_props_path,
        {
            **props,
            "render_profile": {"width": 960, "height": 540, "fps": 24, "label": "proof-540p-12-on-24"},
        },
    )
    review_props_path = revision_dir / "remotion-props-review.json"
    _write_json(
        review_props_path,
        {
            **props,
            "render_profile": {"width": 1280, "height": 720, "fps": 24, "label": "review-720p-12-on-24"},
        },
    )
    master_props_path = revision_dir / "remotion-props-master.json"
    _write_json(
        master_props_path,
        {
            **props,
            "render_profile": {"width": 1920, "height": 1080, "fps": 24, "label": "master-1080p-12-on-24"},
        },
    )
    _write_json(revision_dir / "structural-qc.json", qc)
    _write_json(revision_dir / "editorial-motion-plan.json", plan)
    _write_json(revision_dir / "asset-map.json", asset_map)
    _write_json(revision_dir / "pacing-recipe.json", pacing_recipe)
    _write_json(revision_dir / "finance-visual-cue-sheet.json", cue_sheet)
    _write_json(revision_dir / "finance-edit-manifest.json", edit_manifest)
    summary = _hashed(
        {
            "schema_version": "finance_video_build.v1",
            "episode_id": EPISODE_ID,
            "duration_s": audio_duration,
            "word_count": len(words),
            "cue_count": len(cues),
            "shot_count": len(shots),
            "chapter_count": len(chapters),
            "asset_count": len(used_asset_ids),
            "evidence_card_count": len(evidence),
            "short_range": cue_sheet["short_ranges"][0],
            "audio_sha256": str(audio_manifest["audio_sha256"]),
            "words_sha256": words_sha,
            "plan_hash": str(plan["artifact_hash"]),
            "cue_sheet_hash": str(cue_sheet["artifact_hash"]),
            "edit_manifest_hash": str(edit_manifest["artifact_hash"]),
            "semantic_resolution_hash": str(semantic_resolution["artifact_hash"]),
            "research_supplement_hash": str(research_supplement["artifact_hash"]),
            "qc_overall": str(qc["overall"]),
            "review_output": (revision_dir / "current-bubble-mechanism-review-master.mp4").as_posix(),
        }
    )
    summary_path = revision_dir / "build-summary.json"
    _write_json(summary_path, summary)
    return {
        "revision_dir": revision_dir,
        "props": props_path,
        "proof_props": proof_props_path,
        "review_props": review_props_path,
        "master_props": master_props_path,
        "plan": plan_path,
        "cue_sheet": cue_path,
        "edit_manifest": edit_manifest_path,
        "semantic_resolution": semantic_root / "remotion-semantic-resolution-map.v3.json",
        "research_supplement": research_supplement_path,
        "summary": summary_path,
    }


def _verify_render(revision_dir: Path) -> Path:
    video_path = revision_dir / "current-bubble-mechanism-review-master.mp4"
    if not video_path.is_file():
        raise ValueError(f"review render is missing: {video_path}")
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration,size:stream=index,codec_type,codec_name,width,height,r_frame_rate,sample_rate,channels",
            "-of",
            "json",
            str(video_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    media = json.loads(result.stdout)
    summary = _read_json(revision_dir / "build-summary.json")
    duration = float(media["format"]["duration"])
    expected_duration = float(summary["duration_s"])
    if abs(duration - expected_duration) > 0.15:
        raise ValueError(
            f"render duration {duration:.3f}s does not match canonical audio {expected_duration:.3f}s"
        )
    video_streams = [item for item in media.get("streams", []) if item.get("codec_type") == "video"]
    audio_streams = [item for item in media.get("streams", []) if item.get("codec_type") == "audio"]
    if len(video_streams) != 1 or not audio_streams:
        raise ValueError("render must contain one video stream and at least one audio stream")
    verification = _hashed(
        {
            "schema_version": "finance_render_verification.v1",
            "episode_id": EPISODE_ID,
            "render_path": video_path.as_posix(),
            "render_sha256": _sha256(video_path),
            "size_bytes": video_path.stat().st_size,
            "duration_s": duration,
            "canonical_audio_duration_s": expected_duration,
            "video": video_streams[0],
            "audio": audio_streams[0],
            "plan_hash": str(summary["plan_hash"]),
            "cue_sheet_hash": str(summary["cue_sheet_hash"]),
            "audio_sha256": str(summary["audio_sha256"]),
            "status": "verified",
        }
    )
    verification_path = revision_dir / "render-verification.json"
    _write_json(verification_path, verification)
    return verification_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--verify-render",
        action="store_true",
        help="Verify the existing complete review MP4 after compiling the package.",
    )
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    engine_root = repo_root / "content" / "video_engine"
    finance_root = engine_root / "projects" / CHANNEL_ID
    pilot_root = finance_root / "pilots" / EPISODE_ID
    outputs = _build_outputs(
        repo_root=repo_root,
        finance_root=finance_root,
        pilot_root=pilot_root,
        engine_root=engine_root,
    )
    if args.verify_render:
        outputs["render_verification"] = _verify_render(outputs["revision_dir"])
    print(json.dumps({key: value.as_posix() for key, value in outputs.items()}, indent=2))


if __name__ == "__main__":
    main()
