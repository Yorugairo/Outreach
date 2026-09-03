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
# Mean of two independent takes, same voice/settings/seed:
#   take 1 (Script C era): 1,231w / 7,161ch / 446.1s -> 165.6 wpm, 16.05 cps
#   take 2 (Script F):     2,134w / 12,020ch / 727.0s -> 176.1 wpm, 16.53 cps
# The 6% spread is real and probably break-tag density: take 2 carries
# 1.50 tags/1k against take 1's heavier ration, so it spends less time in
# scripted silence. Two points is too thin to fit that as a term, so the
# mean is used and the spread is why the dual-estimator disagreement check
# exists. Both takes came in FASTER than the constants predicted, meaning
# runtime estimates run long — the safe direction for a cap or a 3s gate.
CHARS_PER_SEC = 16.29
WORDS_PER_MIN = 170.9


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


# --- positional anchors and unit geometry -----------------------------------
# P2.md "Positional anchor A3 + foreshadow F2 (~10% of runtime; 3:00 @30min)";
# MAP s4 QC; kit roster "A3 ~10%". Ruling E23 (2026-09-02): 10% of runtime is
# the anchor for BOTH the audit and the opening gate; 3:00 is the @30:00
# column of that rule, not a constant.
A3_RUNTIME_SHARE = 0.10
# FULL-VIDEO-MAP sec 1 scaling law, as the audit's phase geometry carries it
# (audit_script_doctrine P3_GAP_PCT / P5_REFLECTION_PCT): between the pinned
# OPEN and CLOSE, every phase is a share of runtime. P3 GAP 17-45%; P5
# REFLECTION 55-87%. Replicated here (not imported) because the audit imports
# this module.
P3_GAP_SHARE = (0.17, 0.45)
P5_REFLECTION_SHARE = (0.55, 0.87)


def a3_anchor_s(runtime_s: float) -> float:
    """Rehook anchor A3, in seconds, for a script of this runtime.

    P2.md: "A3 at ~10% of runtime; 3:00 @30min". 806s -> 80.6s; 1800s -> 180s.
    """
    return runtime_s * A3_RUNTIME_SHARE


def _split(lo: float, hi: float, n: int) -> list[tuple[float, float]]:
    """A span cut into n contiguous equal windows."""
    step = (hi - lo) / n
    return [(lo + i * step, lo + (i + 1) * step) for i in range(n)]


def unit_windows(runtime_s: float) -> list[tuple[float, float]]:
    """The per-unit windows a script of this runtime must rehook out of.

    P3.md u5 ("Rehook out", one per unit) and MAP s9 / kit roster ("1/unit"):
    the P3 GAP span is cut into `unit_count(runtime_min)` equal windows, and
    the P5 REFLECTION span the same way. The first `unit_count` tuples are
    P3, the rest P5; windows are contiguous inside each phase span.
    """
    n = unit_count(runtime_s / 60)
    p3 = _split(runtime_s * P3_GAP_SHARE[0], runtime_s * P3_GAP_SHARE[1], n)
    p5 = _split(runtime_s * P5_REFLECTION_SHARE[0],
                runtime_s * P5_REFLECTION_SHARE[1], n)
    return p3 + p5


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
