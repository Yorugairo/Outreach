"""Read the script doctrine's constants from the kit, not from a copy.

The same value used to live in ten places across four tiers — the numbered
docs, FULL-VIDEO-MAP, the kit binder, KNOWLEDGE-GRAPH, LLM-CONTEXT-CLASSICAL
and the phase guides — and all ten drifted independently. One owner per
value is the fix, so `SCRIPT-PATTERN-KIT.md` owns them and this module
parses them. Change the kit's tables and the linters follow.

The split that matters:

  DOCTRINE  — roster counts, phase geometry, gates. Decided by the operator,
              owned by the kit, parsed here.
  MEASURED  — speech rate. Not doctrine; a fact about a voice, measured off
              a recorded take. Lives in code with its provenance, because
              re-measuring is an experiment, not an edit to doctrine.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

KIT = (Path(__file__).resolve().parents[3]
       / "docs/content-video-engine/patterns/SCRIPT-PATTERN-KIT.md")

# --- MEASURED, not doctrine -------------------------------------------------
# Steel and Paper take: 1,231 words / 7,161 chars / 446.1s across 7 scenes
# (per-scene 160-174 wpm). Two estimators because they fail differently:
# chars/sec under-reads numerals, words/min under-reads long words.
CHARS_PER_SEC = 16.05
WORDS_PER_MIN = 165.6


@dataclass(frozen=True)
class RosterRow:
    system: str
    count: str
    placement: str


@dataclass(frozen=True)
class PhaseRow:
    name: str
    owns: str
    windows: dict[str, str]     # "@30:00" -> "0:00–1:30"

    def seconds(self, column: str) -> tuple[float, float] | None:
        span = self.windows.get(column)
        if not span:
            return None
        parts = re.split(r"[–-]", span)
        if len(parts) != 2:
            return None
        return tuple(_clock(p) for p in parts)          # type: ignore[return-value]


def _clock(text: str) -> float:
    m, _, s = text.strip().partition(":")
    return int(m) * 60 + int(s or 0)


def _tables(md: str) -> list[list[list[str]]]:
    """Every pipe table in the document, as rows of trimmed cells."""
    tables, current = [], []
    for line in md.splitlines():
        if line.lstrip().startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if not all(re.fullmatch(r":?-{2,}:?", c) for c in cells):
                current.append(cells)
        elif current:
            tables.append(current)
            current = []
    if current:
        tables.append(current)
    return tables


@lru_cache(maxsize=1)
def _kit() -> str:
    if not KIT.exists():
        raise FileNotFoundError(
            f"the kit is the source of truth for these constants and is "
            f"missing: {KIT}")
    return KIT.read_text(encoding="utf-8")


@lru_cache(maxsize=1)
def roster() -> tuple[RosterRow, ...]:
    """The duty roster — what must exist, counted (kit: 'The duty roster')."""
    for table in _tables(_kit()):
        if table and table[0][:2] == ["System", "Count"]:
            return tuple(RosterRow(*r[:3]) for r in table[1:] if len(r) >= 3)
    raise ValueError("no duty-roster table found in the kit")


@lru_cache(maxsize=1)
def phases() -> tuple[PhaseRow, ...]:
    """The six phases and their authored windows (kit: 'Geometry')."""
    for table in _tables(_kit()):
        if table and table[0][0] == "Phase" and "@30:00" in table[0]:
            header = table[0]
            rows = []
            for r in table[1:]:
                if len(r) < len(header):
                    continue
                rows.append(PhaseRow(
                    name=r[0], owns=r[1],
                    windows={h: v for h, v in zip(header[2:], r[2:])}))
            return tuple(rows)
    raise ValueError("no geometry table found in the kit")


@lru_cache(maxsize=1)
def pivot_pin() -> tuple[float, float]:
    """The midpoint pin, read from the kit's geometry prose."""
    m = re.search(r"pinned at\s*\*?\*?(\d+)[–-](\d+)%", _kit())
    if not m:
        raise ValueError("pivot pin not found in the kit's geometry section")
    return float(m.group(1)), float(m.group(2))


@lru_cache(maxsize=1)
def sentence_band() -> tuple[float, float]:
    """The score's sentence-length band (kit hard gate 2)."""
    m = re.search(r"\*\*(\d+)[–-](\d+) word\s*\n?\s*average", _kit())
    if not m:
        m = re.search(r"(\d+)[–-](\d+) word average", _kit())
    if not m:
        raise ValueError("sentence band not found in the kit's hard gates")
    return float(m.group(1)), float(m.group(2))


def unit_count(runtime_min: float) -> int:
    """P3 pattern units this runtime wants (kit geometry, elastic knob)."""
    import math
    m = re.search(r"ceil\(\(runtime_min\s*[−-]\s*(\d+)\)\s*/\s*([\d.]+)\)",
                  _kit())
    offset, divisor = (float(m.group(1)), float(m.group(2))) if m else (9.0, 2.5)
    return max(1, math.ceil((runtime_min - offset) / divisor))


def open_close_seconds() -> tuple[float, float]:
    """The absolute OPEN/CLOSE window, both pinned at every runtime."""
    m = re.search(r"OPEN is (\d+)[–-](\d+) seconds", _kit())
    return (float(m.group(1)), float(m.group(2))) if m else (60.0, 90.0)


if __name__ == "__main__":
    import sys
    # The kit is full of en-dashes and middots; a cp1252 console cannot
    # print them. Never let a display encoding fail a doctrine dump.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print(f"kit: {KIT}")
    print(f"\npivot pin      : {pivot_pin()}")
    print(f"sentence band  : {sentence_band()}")
    print(f"open/close     : {open_close_seconds()}")
    print(f"units @11.7min : {unit_count(11.7)}")
    print(f"\nphases ({len(phases())}):")
    for p in phases():
        print(f"  {p.name:<15} @30:00 {p.windows.get('@30:00')}"
              f"  -> {p.seconds('@30:00')}")
    print(f"\nroster ({len(roster())} systems):")
    for r in roster():
        print(f"  {r.system:<20} {r.count}")
