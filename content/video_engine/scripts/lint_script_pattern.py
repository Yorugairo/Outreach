"""Mechanical QC lints for kit-pattern scripts.

Gates (kit hard-gate tier): sentence-length stats, passive scan, fragment
stacks, CTA budget, pause-mark ration + unknown marks, stage-direction
tautology, ring check. Positional rehooks are reported as stats (their
timing can only be judged against a runtime, which plain text lacks).

Exit code 0 = clean (warnings allowed), 1 = one or more failures.
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

ALLOWED_MARKS = frozenset({"pre-key", "post-key", "verify"})
# Measured from the Steel and Paper take: 1,231 words / 446.1s across seven
# scenes (per-scene range 160-174). The old 150.0 was a generic estimate and
# ran 9.4% slow, which INFLATED the minute count and quietly loosened the
# marks-per-minute gate below.
WORDS_PER_MINUTE = 165.6
MAX_MARKS_PER_MINUTE = 3.5
SENTENCE_MEAN_RANGE = (8.0, 20.0)
PASSIVE_RATIO_MAX = 0.15
FRAGMENT_WORDS = 5
FRAGMENT_RUN_MAX = 3
CTA_MAX = 2
TAUTOLOGY_OVERLAP_MAX = 0.6
MIN_DIRECTION_TOKENS = 4
MIN_TOKEN_LEN = 4

CTA_PATTERNS = (
    r"\bsubscribe\b",
    r"\blike button\b",
    r"\bhit (?:the )?like\b",
    r"\bin the comments\b",
    r"\bcomments? below\b",
    r"\bshare this\b",
    r"\bsmash\b",
)
TRIPLE_ASK = re.compile(r"like,?\s+comment,?\s+and\s+subscribe", re.IGNORECASE)
REHOOK_PATTERNS = (
    r"but here'?s where",
    r"here'?s where it gets",
    r"this is where most people",
    r"what nobody",
    r"fast-?forward",
    r"but the real question",
)
STOPWORDS = frozenset(
    """the and that this with from into over under while when where what
    which their there here they them then than your yours you his her its
    have has had been being will would could should about after before
    every single same tonight today never always people story video"""
    .split()
)

_ANNOTATION = re.compile(r"\*\(.*?\)\*", re.DOTALL)
_MARK = re.compile(r"\[([a-z][a-z-]*)\](?!\()")
_WORD = re.compile(r"[A-Za-z']+")


@dataclass(frozen=True)
class Finding:
    code: str
    message: str


@dataclass(frozen=True)
class LintReport:
    failures: tuple[Finding, ...]
    warnings: tuple[Finding, ...]
    stats: dict = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return not self.failures


def _is_structural(line: str) -> bool:
    stripped = line.strip()
    return stripped.startswith(("#", "|", ">", "---", "```", "==="))


def parse_script(text: str) -> tuple[list[tuple[str, str]], list[str]]:
    """Split into (direction, following-paragraph) pairs and narration paragraphs."""
    cleaned = _ANNOTATION.sub("", text)
    paragraphs: list[str] = []
    pairs: list[tuple[str, str]] = []
    pending_direction = ""
    current: list[str] = []
    in_direction = False

    def flush() -> None:
        nonlocal pending_direction
        if not current:
            return
        paragraph = " ".join(current)
        paragraphs.append(paragraph)
        if pending_direction:
            pairs.append((pending_direction, paragraph))
            pending_direction = ""
        current.clear()

    for line in cleaned.splitlines():
        stripped = line.strip()
        if in_direction:
            pending_direction += " " + stripped.strip("*[]")
            in_direction = not stripped.endswith("]**")
        elif not stripped:
            flush()
        elif stripped.startswith("**["):
            flush()
            pending_direction = stripped.strip("*[]")
            in_direction = not stripped.endswith("]**")
        elif not _is_structural(stripped):
            current.append(stripped)
    flush()
    return pairs, paragraphs


def _strip_marks(text: str) -> str:
    return _MARK.sub("", text.replace("`", ""))


def _sentences(narration: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", _strip_marks(narration))
    return [part for part in parts if _WORD.search(part)]


def _content_tokens(text: str) -> set[str]:
    words = (word.lower().strip("'") for word in _WORD.findall(text))
    return {w for w in words if len(w) >= MIN_TOKEN_LEN and w not in STOPWORDS}


def _check_sentences(sentences: list[str]) -> tuple[list[Finding], dict]:
    counts = [len(_WORD.findall(s)) for s in sentences]
    if not counts:
        return [Finding("EMPTY", "no narration sentences found")], {}
    mean = sum(counts) / len(counts)
    findings = []
    low, high = SENTENCE_MEAN_RANGE
    if not low <= mean <= high:
        findings.append(
            Finding("SENTENCE_MEAN", f"mean sentence length {mean:.1f} outside {low}-{high}")
        )
    run = longest_run = 0
    for count in counts:
        run = run + 1 if count < FRAGMENT_WORDS else 0
        longest_run = max(longest_run, run)
    if longest_run > FRAGMENT_RUN_MAX:
        findings.append(
            Finding("FRAGMENT_STACK", f"{longest_run} consecutive fragments (<{FRAGMENT_WORDS} words)")
        )
    return findings, {"sentence_mean": round(mean, 1), "sentence_count": len(counts)}


def _check_passive(sentences: list[str]) -> list[Finding]:
    passive = re.compile(r"\b(?:is|are|was|were|be|been|being)\s+\w+ed\b", re.IGNORECASE)
    hits = sum(1 for s in sentences if passive.search(s))
    ratio = hits / len(sentences) if sentences else 0.0
    if ratio > PASSIVE_RATIO_MAX:
        return [Finding("PASSIVE_RATIO", f"passive voice in {hits}/{len(sentences)} sentences")]
    return []


def _check_ctas(narration: str) -> list[Finding]:
    findings = []
    if TRIPLE_ASK.search(narration):
        findings.append(Finding("CTA_TRIPLE", "'like, comment, and subscribe' is three asks"))
    hits = sum(len(re.findall(p, narration, re.IGNORECASE)) for p in CTA_PATTERNS)
    if hits > CTA_MAX:
        findings.append(Finding("CTA_COUNT", f"{hits} CTA constructions (budget {CTA_MAX})"))
    return findings


def _check_marks(narration: str, word_count: int) -> list[Finding]:
    findings = []
    marks = _MARK.findall(narration.replace("`", ""))
    unknown = sorted({m for m in marks if m not in ALLOWED_MARKS})
    if unknown:
        findings.append(Finding("UNKNOWN_MARK", f"unrecognized marks: {', '.join(unknown)}"))
    pauses = sum(1 for m in marks if m in ("pre-key", "post-key"))
    minutes = max(word_count / WORDS_PER_MINUTE, 0.1)
    if pauses / minutes > MAX_MARKS_PER_MINUTE:
        findings.append(
            Finding("PAUSE_RATION", f"{pauses} pause marks in ~{minutes:.1f} min exceeds ration")
        )
    return findings


def _check_tautology(pairs: list[tuple[str, str]]) -> list[Finding]:
    findings = []
    for direction, paragraph in pairs:
        direction_tokens = _content_tokens(direction)
        if len(direction_tokens) < MIN_DIRECTION_TOKENS:
            continue
        overlap = len(direction_tokens & _content_tokens(paragraph)) / len(direction_tokens)
        if overlap > TAUTOLOGY_OVERLAP_MAX:
            findings.append(
                Finding("TAUTOLOGY", f"narration captions its visual ({overlap:.0%}): '{direction[:60]}'")
            )
    return findings


def _check_ring(paragraphs: list[str]) -> list[Finding]:
    if len(paragraphs) < 2:
        return []
    shared = _content_tokens(paragraphs[0]) & _content_tokens(paragraphs[-1])
    if not shared:
        return [Finding("RING", "no opening token recurs in the close")]
    return []


def _rehook_positions(narration: str) -> list[int]:
    words_total = len(_WORD.findall(narration)) or 1
    positions = []
    for pattern in REHOOK_PATTERNS:
        for match in re.finditer(pattern, narration, re.IGNORECASE):
            words_before = len(_WORD.findall(narration[: match.start()]))
            positions.append(round(100 * words_before / words_total))
    return sorted(positions)


def lint_script(text: str) -> LintReport:
    pairs, paragraphs = parse_script(text)
    narration = "\n".join(paragraphs)
    sentences = _sentences(narration)
    word_count = len(_WORD.findall(_strip_marks(narration)))

    sentence_findings, stats = _check_sentences(sentences)
    failures = [
        *sentence_findings,
        *_check_passive(sentences),
        *_check_ctas(narration),
        *_check_marks(narration, word_count),
        *_check_tautology(pairs),
        *_check_ring(paragraphs),
    ]
    positions = _rehook_positions(narration)
    warnings = [] if positions else [Finding("REHOOK", "no rehook-family construction found")]
    stats = {**stats, "word_count": word_count, "rehook_positions_pct": positions}
    return LintReport(tuple(failures), tuple(warnings), stats)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("script", help="path to the script markdown/text file")
    args = parser.parse_args(argv)

    try:
        text = Path(args.script).read_text(encoding="utf-8")
    except OSError as error:
        print(f"ERROR: cannot read {args.script}: {error}")
        return 1

    report = lint_script(text)
    for finding in report.failures:
        print(f"FAIL {finding.code}: {finding.message}")
    for finding in report.warnings:
        print(f"WARN {finding.code}: {finding.message}")
    print(f"stats: {report.stats}")
    print("RESULT: " + ("clean" if report.ok else f"{len(report.failures)} failure(s)"))
    return 0 if report.ok else 1


if __name__ == "__main__":
    sys.exit(main())
