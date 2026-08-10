"""Compile the current-bubble episode into sentence/idea-native semantic beats.

This compiler is intentionally upstream of asset selection and rendering.  It
binds every canonical ElevenLabs word exactly once, names the spoken actors and
action, and records the visual understanding that later P21 slices must serve.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from content.video_engine.src.services.finance_channel import (  # noqa: E402
    file_sha256,
    validate_artifact,
    with_artifact_hash,
)


DEFAULT_PILOT_ROOT = (
    REPO_ROOT
    / "content"
    / "video_engine"
    / "projects"
    / "systems-and-blowups"
    / "pilots"
    / "current-bubble-mechanism"
)
DEFAULT_OUTPUT = (
    DEFAULT_PILOT_ROOT
    / "edit"
    / "sentence-native-v1"
    / "semantic-beat-ledger.v1.json"
)
MAX_COMPOUND_DURATION_S = 8.0


@dataclass(frozen=True, slots=True)
class Chapter:
    index: int
    chapter_id: str
    title: str
    start_word: int
    end_word: int
    claim_scope_refs: tuple[str, ...]


CHAPTER_TITLES = (
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

CHAPTER_CLAIMS: tuple[tuple[str, ...], ...] = (
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
)

# Longest phrases win.  These are semantic anchors, not an asset resolver.
NOUN_PHRASES: tuple[tuple[str, str], ...] = (
    ("s&p 500 index fund", "s&p-500-index-fund"),
    ("s&p 500", "s&p-500"),
    ("high-bandwidth memory", "high-bandwidth-memory"),
    ("strategic customer agreements", "strategic-customer-agreements"),
    ("listed equity markets", "listed-equity-markets"),
    ("float-adjusted market value", "float-adjusted-market-value"),
    ("return on invested capital", "return-on-invested-capital"),
    ("free cash flow", "free-cash-flow"),
    ("market leaders index", "market-leaders-index"),
    ("equal-weight index", "equal-weight-index"),
    ("defensive assets", "defensive-assets"),
    ("take-or-pay agreements", "take-or-pay-agreements"),
    ("packaging capacity", "packaging-capacity"),
    ("clean-room space", "clean-room-space"),
    ("research and development", "research-and-development"),
    ("market capitalization", "market-capitalization"),
    ("automatic contributions", "automatic-contributions"),
    ("contribution", "contribution"),
    ("compounder", "compounder"),
    ("incumbent", "incumbent"),
    ("economic cause", "economic-cause"),
    ("index mutual funds", "index-mutual-funds"),
    ("generational wealth", "generational-wealth"),
    ("strategic bottlenecks", "strategic-bottlenecks"),
    ("sovereign risk", "sovereign-risk"),
    ("long tail", "long-tail"),
    ("memory trade", "memory-trade"),
    ("physical bottleneck", "physical-bottleneck"),
    ("ai memory stocks", "ai-memory-stocks"),
    ("ai accelerator", "ai-accelerator"),
    ("fuel system", "fuel-system"),
    ("supply capacity", "supply-capacity"),
    ("commodity memory cycle", "commodity-memory-cycle"),
    ("capital markets", "capital-markets"),
    ("south korea", "south-korea"),
    ("korea exchange", "korea-exchange"),
    ("european central bank", "european-central-bank"),
    ("public equity market", "public-equity-market"),
    ("digital age", "digital-age"),
    ("index fund", "index-fund"),
    ("index funds", "index-funds"),
    ("active managers", "active-managers"),
    ("automatic demand", "automatic-demand"),
    ("basket of leaders", "leader-basket"),
    ("defensive sleeve", "defensive-sleeve"),
    ("quality-screened basket", "quality-screened-basket"),
    ("company risk", "company-risk"),
    ("memory", "memory"),
    ("hbm", "hbm"),
    ("gpu", "gpu"),
    ("processor", "processor"),
    ("data", "data"),
    ("market", "market"),
    ("bubble", "bubble"),
    ("price", "price"),
    ("cash flow", "cash-flow"),
    ("scarcity", "scarcity"),
    ("elevator", "elevator"),
    ("elevators", "elevators"),
    ("steel cable", "steel-cable"),
    ("demand", "demand"),
    ("capacity", "capacity"),
    ("contracts", "contracts"),
    ("diversification", "diversification"),
    ("concentration", "concentration"),
    ("wafer", "wafer"),
    ("wafers", "wafers"),
    ("equipment", "equipment"),
    ("engineers", "engineers"),
    ("dies", "dies"),
    ("stacks", "stacks"),
    ("bakery", "bakery"),
    ("ovens", "ovens"),
    ("cakes", "cakes"),
    ("dram", "dram"),
    ("nand", "nand"),
    ("micron", "micron"),
    ("samsung", "samsung"),
    ("sk hynix", "sk-hynix"),
    ("customers", "customers"),
    ("buyers", "buyers"),
    ("suppliers", "suppliers"),
    ("margins", "margins"),
    ("revenue", "revenue"),
    ("chokepoints", "chokepoints"),
    ("chips", "chips"),
    ("semiconductor", "semiconductor"),
    ("robotics", "robotics"),
    ("countries", "countries"),
    ("korea", "korea"),
    ("italy", "italy"),
    ("investors", "investors"),
    ("companies", "companies"),
    ("basket", "basket"),
    ("portfolio", "portfolio"),
    ("stocks", "stocks"),
    ("bonds", "bonds"),
    ("gold", "gold"),
    ("cash", "cash"),
    ("taxes", "taxes"),
    ("drawdown", "drawdown"),
    ("volatility", "volatility"),
    ("risk", "risk"),
    ("internet", "internet"),
    ("railroads", "railroads"),
)

VERB_LEMMAS: Mapping[str, str] = {
    "absorbs": "absorb", "add": "add", "adds": "add", "aligned": "align", "associate": "associate",
    "allocates": "allocate", "apply": "apply", "applies": "apply", "ask": "ask",
    "become": "become", "becomes": "become", "began": "begin", "binds": "bind",
    "bought": "buy", "build": "build", "buys": "buy", "buying": "buy",
    "capitalize": "capitalize", "capitalized": "capitalize", "change": "change",
    "changes": "change", "collapse": "collapse", "commit": "commit", "committing": "commit",
    "compares": "compare", "compete": "compete", "competes": "compete", "concentrated": "concentrate",
    "consume": "consume", "consumes": "consume", "control": "control", "correct": "correct",
    "cover": "cover", "covers": "cover", "create": "create", "created": "create",
    "define": "define", "delay": "delay", "depends": "depend", "destroy": "destroy", "destroyed": "destroy",
    "dilute": "dilute", "diluted": "dilute", "drive": "drive", "driven": "drive",
    "earns": "earn", "exceeded": "exceed", "expand": "expand", "expands": "expand",
    "fail": "fail", "fails": "fail", "feeds": "feed", "fill": "fill", "find": "find", "held": "hold",
    "forms": "form", "guarantee": "guarantee", "grew": "grow", "grow": "grow",
    "grows": "grow", "heals": "heal", "ignore": "ignore", "improve": "improve",
    "imagine": "imagine", "invest": "invest", "jumped": "jump", "labeling": "label", "lagged": "lag",
    "limit": "limit", "limits": "limit", "look": "look", "looks": "look",
    "make": "make", "made": "make", "makes": "make", "manufacturing": "manufacture", "matter": "matter",
    "moved": "move", "occupies": "occupy", "open": "open", "opens": "open",
    "outperformed": "outperform", "pay": "pay", "paying": "pay", "pressure": "pressure",
    "pressuring": "pressure", "produces": "produce", "producing": "produce",
    "pulls": "pull", "raise": "raise", "rebalancing": "rebalance", "reduce": "reduce",
    "reduces": "reduce", "reorganizing": "reorganize", "repriced": "reprice",
    "rebalance": "rebalance", "represented": "represent", "repeated": "repeat", "replace": "replace", "reported": "report", "represent": "represent",
    "run": "run", "runs": "run", "reserve": "reserve", "reserving": "reserve", "respond": "respond", "rising": "rise",
    "rises": "rise", "separate": "separate", "separates": "separate", "show": "show",
    "says": "say", "share": "share", "showed": "show", "shows": "show", "signing": "sign", "solves": "solve", "start": "start",
    "spreads": "spread", "starving": "starve", "starts": "start", "stopped": "stop",
    "attract": "attract", "take": "take", "takes": "take", "test": "test", "tests": "test", "trade": "trade",
    "traded": "trade", "triple": "triple", "turn": "turn", "turns": "turn",
    "use": "use", "uses": "use", "want": "want", "wants": "want", "weaken": "weaken", "weakens": "weaken", "weights": "weight",
    "win": "win", "works": "work", "worth": "value",
}
AUXILIARY_LEMMAS: Mapping[str, str] = {
    "am": "be", "are": "be", "be": "be", "been": "be", "being": "be",
    "can": "enable", "could": "enable", "did": "do", "do": "do", "does": "do",
    "had": "have", "has": "have", "have": "have", "is": "be", "may": "allow",
    "cannot": "prevent", "might": "allow", "must": "require", "need": "need", "needs": "need",
    "should": "recommend", "was": "be", "were": "be", "will": "be", "would": "be",
}
STOPWORDS = {
    "a", "about", "after", "again", "all", "also", "an", "and", "another", "any",
    "as", "at", "because", "before", "both", "but", "by", "each", "enough", "even",
    "every", "for", "from", "here", "how", "if", "in", "inside", "into", "it", "its",
    "more", "most", "neither", "no", "not", "now", "of", "on", "one", "only", "or",
    "other", "out", "over", "right", "same", "so", "some", "still", "than", "that",
    "the", "their", "them", "then", "there", "these", "they", "this", "those", "through",
    "to", "too", "under", "up", "very", "what", "when", "where", "whether", "which",
    "while", "who", "why", "with", "without", "you", "your",
}
CONJUNCTIONS = {"although", "and", "because", "but", "so", "then", "while", "yet"}

CLAIM_KEYWORDS: tuple[tuple[tuple[str, ...], str], ...] = (
    (("hbm", "bandwidth", "accelerator", "gpu"), "memory-architecture-dependency"),
    (("wafer", "clean-room", "fab", "capacity", "trade ratio", "non-hbm"), "hbm-capacity-trade-ratio"),
    (("sixteen strategic", "16 strategic", "take-or-pay", "one-third of its nand", "five years"), "micron-strategic-customer-agreements"),
    (("hbm4", "triple in 2026", "samsung"), "samsung-hbm4-growth"),
    (("sk hynix", "demand exceeded supply"), "sk-hynix-demand-exceeds-supply"),
    (("top ten", "forty percent", "40 percent", "concentrat"), "sp500-top-ten-concentration"),
    (("19.1 trillion", "majority of long-term fund assets"), "index-fund-asset-scale"),
    (("25,000", "twenty-five thousand", "one million", "15.9 percent", "271,000", "600,000"), "generational-wealth-return-hurdle"),
    (("13.6 percent", "ten years ending june 2026"), "sp500-trailing-return-snapshot"),
    (("market leaders", "late 2024", "about 16 percent", "back-tested", "maximum drawdown"), "sp500-market-leaders-comparison"),
    (("equal-weight", "equal weight", "since 2003", "long tail"), "equal-weight-long-tail-countercase"),
    (("korea", "italy", "milan", "5,370 trillion", "3.2 trillion euros", "1.16 trillion euros"), "korea-italy-listed-market-comparison"),
    (("five percent of gdp", "oecd", "research and development", "semiconductor exports"), "korea-technology-intensity"),
    (("different exchange", "listed equity", "not a gdp comparison"), "cross-exchange-comparability-limit"),
    (("barbell", "defensive sleeve", "sovereign bills", "gold", "explicit protection"), "concentrated-defensive-barbell-hypothesis"),
    (("failure points", "new capacity", "more efficient ai", "giant buyers", "real demand does not prevent"), "memory-countercase"),
    (("yesterday’s winners", "tomorrow’s", "catastrophic company risk", "index also heals"), "sp500-countercase"),
    (("memory", "bottleneck", "shortage", "cable"), "memory-bottleneck-not-bubble-inference"),
    (("s&p 500", "safe index", "index trade", "diworsification", "diversification"), "sp500-hidden-bubble-risk-inference"),
)

FACTUAL_CLASSES = {"observed_fact", "calculation", "market_snapshot", "sourced_interpretation"}


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _normalize(token: str) -> str:
    return re.sub(r"[^a-z0-9]", "", token.casefold())


def _repo_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def _binding(path: Path) -> dict[str, str]:
    return {"path": _repo_path(path), "sha256": file_sha256(path)}


def _find_phrase(words: Sequence[Mapping[str, Any]], phrase: str, cursor: int) -> int:
    needle = [_normalize(token) for token in re.findall(r"\S+", phrase) if _normalize(token)]
    haystack = [_normalize(str(item["w"])) for item in words]
    for size in range(min(10, len(needle)), 3, -1):
        target = needle[:size]
        for index in range(cursor, len(haystack) - size + 1):
            if haystack[index : index + size] == target:
                return index
    raise ValueError(f"unable to locate chapter phrase after word {cursor}: {phrase[:90]!r}")


def _build_chapters(narration: Mapping[str, Any], words: Sequence[Mapping[str, Any]]) -> list[Chapter]:
    segments = list(narration.get("segments") or [])
    if len(segments) != len(CHAPTER_TITLES):
        raise ValueError(f"expected {len(CHAPTER_TITLES)} narration segments, got {len(segments)}")
    starts: list[int] = []
    cursor = 0
    for index, segment in enumerate(segments):
        start = 0 if index == 0 else _find_phrase(words, str(segment["text"]), cursor)
        starts.append(start)
        cursor = start + 1
    return [
        Chapter(
            index=index,
            chapter_id=str(segment["segment_id"]),
            title=CHAPTER_TITLES[index],
            start_word=starts[index],
            end_word=starts[index + 1] - 1 if index + 1 < len(starts) else len(words) - 1,
            claim_scope_refs=CHAPTER_CLAIMS[index],
        )
        for index, segment in enumerate(segments)
    ]


def _boundary_end_s(words: Sequence[Mapping[str, Any]], end_word: int, duration_s: float) -> float:
    return float(words[end_word + 1]["start_s"]) if end_word + 1 < len(words) else duration_s


def _find_verb(words: Sequence[Mapping[str, Any]], start: int, end: int) -> dict[str, Any] | None:
    normalized = [_normalize(str(words[index]["w"])) for index in range(start, end + 1)]
    for mapping in (VERB_LEMMAS, AUXILIARY_LEMMAS):
        for offset, token in enumerate(normalized):
            if token in mapping:
                index = start + offset
                return {"surface": str(words[index]["w"]), "lemma": mapping[token], "word_index": index}
    return None


def _sentence_ranges(chapter: Chapter, words: Sequence[Mapping[str, Any]]) -> list[tuple[int, int]]:
    ranges: list[tuple[int, int]] = []
    start = chapter.start_word
    for index in range(chapter.start_word, chapter.end_word + 1):
        raw = str(words[index]["w"])
        abbreviation = raw.casefold() in {"u.s.", "u.k.", "inc.", "vs.", "e.g.", "i.e."}
        if not abbreviation and re.search(r"[.!?][\"'”’)]*$", raw):
            ranges.append((start, index))
            start = index + 1
    if start <= chapter.end_word:
        ranges.append((start, chapter.end_word))
    return ranges


def _candidate_split(
    words: Sequence[Mapping[str, Any]], start: int, end: int, duration_s: float
) -> tuple[int, str] | None:
    if _boundary_end_s(words, end, duration_s) - float(words[start]["start_s"]) <= MAX_COMPOUND_DURATION_S:
        return None
    midpoint = (start + end) / 2
    candidates: list[tuple[float, int, str]] = []
    for index in range(start + 3, end - 2):
        raw = str(words[index]["w"])
        token = _normalize(raw)
        punctuation = ";" if ";" in raw else ":" if ":" in raw else "—" if "—" in raw else None
        conjunction = token if token in CONJUNCTIONS else None
        if not punctuation and not conjunction:
            continue
        if _find_verb(words, start, index) is None or _find_verb(words, index + 1, end) is None:
            continue
        priority = 0 if punctuation else 1
        rationale = (
            f"compound sentence split after {punctuation} because both clauses contain independent actions"
            if punctuation
            else f"compound sentence split at {conjunction!r} because both clauses contain independent actions"
        )
        candidates.append((priority * 1000 + abs(index - midpoint), index, rationale))
    if not candidates:
        return None
    _, index, rationale = min(candidates)
    return index, rationale


def _split_compound(
    words: Sequence[Mapping[str, Any]], start: int, end: int, duration_s: float
) -> list[tuple[int, int, str | None]]:
    candidate = _candidate_split(words, start, end, duration_s)
    if candidate is None:
        return [(start, end, None)]
    split_at, rationale = candidate
    left = _split_compound(words, start, split_at, duration_s)
    right = _split_compound(words, split_at + 1, end, duration_s)
    if left:
        left[-1] = (left[-1][0], left[-1][1], rationale)
    return left + right


def _coalesce_verbless(
    ranges: list[tuple[int, int, str | None]], words: Sequence[Mapping[str, Any]]
) -> list[tuple[int, int, str | None]]:
    result: list[tuple[int, int, str | None]] = []
    for start, end, rationale in ranges:
        if _find_verb(words, start, end) is not None:
            result.append((start, end, rationale))
        elif result:
            prior_start, _, prior_reason = result[-1]
            result[-1] = (
                prior_start,
                end,
                prior_reason or "verbless rhetorical fragment retained with its governing sentence",
            )
        elif ranges:
            # The first fragment is carried forward and merged on the next pass.
            result.append((start, end, "opening rhetorical fragment awaits its governing action"))
    if len(result) > 1 and _find_verb(words, result[0][0], result[0][1]) is None:
        first, second = result[0], result[1]
        result[1] = (first[0], second[1], first[2])
        result.pop(0)
    return result


def _phrase_tokens(phrase: str) -> list[str]:
    return [_normalize(token) for token in re.findall(r"\S+", phrase) if _normalize(token)]


def _active_nouns(words: Sequence[Mapping[str, Any]], start: int, end: int) -> list[dict[str, Any]]:
    tokens = [_normalize(str(words[index]["w"])) for index in range(start, end + 1)]
    matches: list[tuple[int, int, str]] = []
    for phrase, canonical in sorted(NOUN_PHRASES, key=lambda item: len(_phrase_tokens(item[0])), reverse=True):
        needle = _phrase_tokens(phrase)
        if not needle:
            continue
        for offset in range(0, len(tokens) - len(needle) + 1):
            if tokens[offset : offset + len(needle)] == needle:
                matches.append((start + offset, start + offset + len(needle) - 1, canonical))
                break
    selected: list[tuple[int, int, str]] = []
    occupied: set[int] = set()
    for noun_start, noun_end, canonical in matches:
        span = set(range(noun_start, noun_end + 1))
        if span & occupied:
            continue
        selected.append((noun_start, noun_end, canonical))
        occupied.update(span)
        if len(selected) == 3:
            break
    if not selected:
        candidates = []
        verbs = set(VERB_LEMMAS) | set(AUXILIARY_LEMMAS)
        for index in range(start, end + 1):
            token = _normalize(str(words[index]["w"]))
            if (
                len(token) >= 4
                and token not in STOPWORDS
                and token not in verbs
                and not token.isdigit()
                and not token.endswith("ly")
            ):
                candidates.append((len(token), index, token))
        if not candidates:
            raise ValueError(f"beat {start}-{end} has no active noun candidate")
        _, index, token = max(candidates)
        selected.append((index, index, token))
    return [
        {
            "surface": " ".join(str(words[index]["w"]) for index in range(noun_start, noun_end + 1)),
            "canonical": canonical,
            "start_word_index": noun_start,
            "end_word_index": noun_end,
        }
        for noun_start, noun_end, canonical in sorted(selected)
    ]


def _claim_refs(excerpt: str, valid_claim_ids: set[str]) -> list[str]:
    lower = excerpt.casefold()
    refs = [claim_id for keywords, claim_id in CLAIM_KEYWORDS if any(keyword in lower for keyword in keywords)]
    return list(dict.fromkeys(ref for ref in refs if ref in valid_claim_ids))


def _viewer_understanding(excerpt: str) -> str:
    cleaned = re.sub(r"^(?:And|But|Now|So|Meanwhile|Translation|Plain English)[:,]?\s+", "", excerpt).strip()
    if not cleaned:
        cleaned = excerpt.strip()
    return f"The viewer should understand that {cleaned[0].lower() + cleaned[1:]}"


def _visual_job(verb: Mapping[str, Any], nouns: Sequence[Mapping[str, Any]]) -> dict[str, str]:
    lemma = str(verb["lemma"])
    if lemma in {"compare", "differ", "outperform", "lag"}:
        kind = "compare"
    elif lemma in {"bind", "constrain", "limit", "occupy", "pressure", "reserve", "starve"}:
        kind = "constrain"
    elif lemma in {"absorb", "allocate", "buy", "capitalize", "pay", "rebalance", "spread", "weight"}:
        kind = "transfer"
    elif lemma in {"become", "change", "collapse", "expand", "grow", "reorganize", "reprice", "rise", "separate", "triple", "turn"}:
        kind = "transform"
    elif lemma in {"find", "look", "open", "show"}:
        kind = "reveal"
    elif lemma in {"destroy", "fail", "reduce", "weaken"}:
        kind = "countercase"
    else:
        kind = "establish"
    noun_labels = [str(item["canonical"]).replace("-", " ") for item in nouns[:2]]
    relationship = " and ".join(noun_labels)
    return {
        "kind": kind,
        "description": f"Show {relationship} performing the narrated action '{lemma}' as one legible causal state.",
    }


def compile_semantic_beat_ledger(
    pilot_root: Path = DEFAULT_PILOT_ROOT,
    *,
    reviewed_boundaries: bool = False,
) -> dict[str, Any]:
    pilot_root = pilot_root.resolve()
    narration_path = pilot_root / "audio" / "current-bubble-mechanism-narration-master.v1.json"
    words_path = pilot_root / "audio" / "canonical" / "history_episode_1_master.words.json"
    script_path = pilot_root / "script-draft.v1.md"
    claims_path = pilot_root / "claim-ledger.v1.json"

    narration = _read_json(narration_path)
    timing_payload = _read_json(words_path)
    words = list(timing_payload.get("words") or [])
    claims_payload = _read_json(claims_path)
    claims = {
        str(item["claim_id"]): item
        for item in claims_payload.get("claims", [])
        if isinstance(item, Mapping) and item.get("claim_id")
    }
    if not words:
        raise ValueError("canonical word timing is empty")
    if narration.get("source_script_sha256") != file_sha256(script_path):
        raise ValueError("canonical narration manifest points to a stale script")
    duration_s = float(timing_payload["duration_s"])
    if abs(float(words[-1]["end_s"]) - duration_s) > 0.002:
        raise ValueError("canonical duration does not match the last timed word")
    for index, word in enumerate(words):
        if float(word["end_s"]) < float(word["start_s"]):
            raise ValueError(f"canonical word {index} has negative duration")
        if index and float(word["start_s"]) < float(words[index - 1]["start_s"]):
            raise ValueError(f"canonical word {index} starts before its predecessor")

    chapters = _build_chapters(narration, words)
    chapter_rows: list[dict[str, Any]] = []
    beats: list[dict[str, Any]] = []
    reviews: list[dict[str, Any]] = []
    for chapter in chapters:
        chapter_rows.append(
            {
                "chapter_id": chapter.chapter_id,
                "chapter_index": chapter.index,
                "title": chapter.title,
                "start_word_index": chapter.start_word,
                "end_word_index": chapter.end_word,
                "start_s": round(float(words[chapter.start_word]["start_s"]), 6),
                "end_s": round(_boundary_end_s(words, chapter.end_word, duration_s), 6),
                "claim_scope_refs": list(chapter.claim_scope_refs),
            }
        )
        raw_ranges: list[tuple[int, int, str | None]] = []
        for sentence_start, sentence_end in _sentence_ranges(chapter, words):
            raw_ranges.extend(_split_compound(words, sentence_start, sentence_end, duration_s))
        ranges = _coalesce_verbless(raw_ranges, words)
        for local_index, (start, end, split_rationale) in enumerate(ranges, start=1):
            excerpt = " ".join(str(words[index]["w"]) for index in range(start, end + 1))
            verb = _find_verb(words, start, end)
            if verb is None:
                raise ValueError(f"beat {start}-{end} remains verbless after coalescing: {excerpt!r}")
            nouns = _active_nouns(words, start, end)
            refs = _claim_refs(excerpt, set(claims))
            factual = any(str(claims[ref].get("classification")) in FACTUAL_CLASSES for ref in refs)
            terminal = bool(re.search(r"[.!?][\"'”’)]*$", str(words[end]["w"])))
            boundary_kind = "compound_clause" if split_rationale and "compound sentence split" in split_rationale else "sentence_terminal" if terminal else "chapter_end"
            beats.append(
                {
                    "beat_id": f"cbm-semantic-beat-{chapter.index + 1:02d}-{local_index:03d}",
                    "chapter_id": chapter.chapter_id,
                    "chapter_index": chapter.index,
                    "local_index": local_index,
                    "start_word_index": start,
                    "end_word_index": end,
                    "start_s": round(float(words[start]["start_s"]), 6),
                    "end_s": round(_boundary_end_s(words, end, duration_s), 6),
                    "excerpt": excerpt,
                    "boundary_kind": boundary_kind,
                    "split_rationale": split_rationale,
                    "active_nouns": nouns,
                    "causal_verb": verb,
                    "claim_refs": refs,
                    "viewer_understanding": _viewer_understanding(excerpt),
                    "visual_job": _visual_job(verb, nouns),
                    "needs_deterministic_fact_surface": factual,
                }
            )
        reviews.append(
            {
                "chapter_id": chapter.chapter_id,
                "start_word_index": chapter.start_word,
                "end_word_index": chapter.end_word,
                "start_excerpt": " ".join(str(item["w"]) for item in words[chapter.start_word : min(chapter.start_word + 12, chapter.end_word + 1)]),
                "end_excerpt": " ".join(str(item["w"]) for item in words[max(chapter.start_word, chapter.end_word - 11) : chapter.end_word + 1]),
                "status": "manually_reviewed" if reviewed_boundaries else "pending",
                "notes": (
                    "Anchor and adjacent canonical word ranges manually matched to the narration segment."
                    if reviewed_boundaries
                    else "Pending operator-side inspection of the anchor and adjacent canonical word ranges."
                ),
            }
        )

    word_sequence = " ".join(str(item["w"]) for item in words)
    payload = with_artifact_hash(
        {
            "schema_version": "finance_semantic_beat_ledger.v1",
            "episode_id": str(narration["episode_id"]),
            "source_bindings": {
                "narration_manifest": _binding(narration_path),
                "word_timing": _binding(words_path),
                "script": _binding(script_path),
                "claim_ledger": _binding(claims_path),
            },
            "timing": {
                "word_count": len(words),
                "duration_s": round(duration_s, 6),
                "first_word_start_s": round(float(words[0]["start_s"]), 6),
                "last_word_end_s": round(float(words[-1]["end_s"]), 6),
                "canonical_word_sequence_sha256": hashlib.sha256(word_sequence.encode("utf-8")).hexdigest(),
            },
            "chapters": chapter_rows,
            "beats": beats,
            "chapter_boundary_review": reviews,
        }
    )
    if reviewed_boundaries:
        validate_artifact(payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot-root", type=Path, default=DEFAULT_PILOT_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--reviewed-boundaries",
        action="store_true",
        help="Assert that the printed chapter boundary excerpts were manually inspected.",
    )
    args = parser.parse_args()
    payload = compile_semantic_beat_ledger(
        args.pilot_root,
        reviewed_boundaries=args.reviewed_boundaries,
    )
    for review in payload["chapter_boundary_review"]:
        print(
            f"{review['chapter_id']} | {review['start_word_index']}-{review['end_word_index']} | "
            f"{review['start_excerpt']} ... {review['end_excerpt']}"
        )
    if not args.reviewed_boundaries:
        print("Boundary review is pending; rerun with --reviewed-boundaries after inspection.")
        return 2
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {output}")
    print(f"beats={len(payload['beats'])} words={payload['timing']['word_count']} hash={payload['artifact_hash']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
