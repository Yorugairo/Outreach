#!/usr/bin/env python3
"""Gate: the research bundle was actually read, and the extraction is traceable.

A research layer is easy to commission and easy to half-use. This gate exists because
that is exactly what happened on 2026-09-04: file 08 was reviewed, 07 was spot-checked,
and 01-06 sat unread while a verdict was written on top of them. Two backlog items were
already answered in the unread files, one shipped gate was measuring the wrong thing, and
a live parallax defect had a correct diagnosis nobody had opened.

Coverage is the proof. You cannot write a disposition for a section you never opened, so
the gate demands one for every heading in every bundle document.

CHECKS
  C1 COVERAGE   every heading in every bundle doc has a row in RESEARCH-INDEX.md
  C2 TARGETS    every "EXTRACTED -> NN" names a reference doc that exists
  C3 BACKLINK   every reference doc names at least one primary it came from
  C4 CONFLICTS  the index declares a conflicts section (explicitly "none" is allowed)
  C5 ORPHANS    every reference doc is reachable from the index
  C6 STALENESS  no bundle document is newer than the index that dispositions it

Exit 0 = PASS, 1 = FAIL. Run from the repository root.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

BUNDLE = Path("content/video_engine/sources/reference_analyses/complete_research_evidence_bundle")
DOCS = Path("docs/content-video-engine")
INDEX = DOCS / "RESEARCH-INDEX.md"
REFERENCE_DOC_GLOB = "4[2-9]-*.md"
HEADING = re.compile(r"^#{2,3} ")
EXTRACT_TARGET = re.compile(r"EXTRACTED\s*->\s*(\d\d)")


def bundle_headings() -> dict[str, list[str]]:
    """Every level-2/3 heading of every bundle document, by filename."""
    out: dict[str, list[str]] = {}
    for f in sorted(list(BUNDLE.glob("*.md")) + list(BUNDLE.glob("*.txt"))):
        hs = [
            re.sub(r"^#+\s*", "", line.rstrip()).replace("|", "/").strip()
            for line in f.read_text(encoding="utf-8", errors="replace").splitlines()
            if HEADING.match(line)
        ]
        out[f.name] = hs
    return out


def index_rows(text: str) -> set[tuple[str, str]]:
    """(file, heading) pairs the index accounts for."""
    rows: set[tuple[str, str]] = set()
    current: str | None = None
    for line in text.splitlines():
        m = re.match(r"^### `([^`]+)`", line)
        if m:
            current = m.group(1)
            continue
        if current and line.startswith("|") and not line.startswith("|---"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) >= 2 and cells[0] not in ("heading",):
                rows.add((current, cells[0]))
    return rows


def fail(checks: list[str], msg: str) -> None:
    checks.append(f"FAIL  {msg}")


def main() -> int:
    if not INDEX.exists():
        print(f"FAIL  no research index at {INDEX}")
        return 1

    text = INDEX.read_text(encoding="utf-8")
    checks: list[str] = []
    headings = bundle_headings()
    rows = index_rows(text)

    # ---- C1 coverage -------------------------------------------------------
    total = missing = 0
    for fname, hs in headings.items():
        for h in hs:
            total += 1
            if (fname, h) not in rows:
                missing += 1
                if missing <= 10:
                    fail(checks, f"C1 unaccounted heading: {fname} :: {h}")
    if missing > 10:
        fail(checks, f"C1 ... and {missing - 10} more unaccounted headings")
    if not total:
        fail(checks, "C1 no bundle headings found - is the bundle path right?")

    # ---- C2 extraction targets exist ---------------------------------------
    for num in sorted(set(EXTRACT_TARGET.findall(text))):
        if not list(DOCS.glob(f"{num}-*.md")):
            fail(checks, f"C2 index extracts to doc {num} but no {num}-*.md exists")

    # ---- C3 every reference doc names a primary ----------------------------
    ref_docs = sorted(DOCS.glob(REFERENCE_DOC_GLOB))
    primaries = set(headings)
    for d in ref_docs:
        body = d.read_text(encoding="utf-8")
        if not any(p.split("_")[0] in body or p in body for p in primaries):
            fail(checks, f"C3 {d.name} cites no primary from the bundle")

    # ---- C4 conflicts declared ---------------------------------------------
    if not re.search(r"^##\s+Declared conflicts", text, re.M):
        fail(checks, "C4 index has no 'Declared conflicts' section")

    # ---- C5 no orphan reference docs ---------------------------------------
    for d in ref_docs:
        if d.name not in text:
            fail(checks, f"C5 {d.name} is not reachable from the index")

    # ---- C6 staleness ------------------------------------------------------
    idx_mtime = INDEX.stat().st_mtime
    for f in sorted(list(BUNDLE.glob("*.md")) + list(BUNDLE.glob("*.txt"))):
        if f.stat().st_mtime > idx_mtime:
            fail(checks, f"C6 {f.name} is newer than the index - re-read and re-disposition")

    # ---- report ------------------------------------------------------------
    print(f"research extraction gate: {total} headings across {len(headings)} bundle docs")
    print(f"  index rows: {len(rows)}   reference docs: {len(ref_docs)}")
    if checks:
        print()
        for c in checks:
            print(c)
        print(f"\n{len(checks)} failure(s)")
        return 1
    print("  C1 coverage OK   C2 targets OK   C3 backlinks OK")
    print("  C4 conflicts declared   C5 no orphans   C6 index current")
    print("\nPASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
