"""THE VERIFIED RECEIPT (P67 T1): the record is read back, not taken on trust.

The receipt lives in a project's `PRODUCTION-LEDGER.md`, under the LAST `## Recall` heading, one line per citation:

    - Recall(<stage>): <path>:<line> "<verbatim span>" (<note>)
    - Recall(<stage>): docs_find 0 hits for "<term>"

Nine stages - package script voice world evidence motion sound publish rulings - each owed at least one line
(`docs/runbooks/ONE-SHOT.md` "Before step 1"). The gotcha this exists for (arXiv 2606.04990): CITATION IS NOT
GROUNDING. A `path:line` proves nothing on its own, so the verifier re-opens the file and matches the QUOTED SPAN
against that EXACT line (whitespace runs collapsed, case-sensitive, at least 12 characters), and re-runs every
`0 hits` claim through `docs_find.py --json --limit 1`. The tolerance is the exact line, never the line plus or
minus one: a one-line window doubles the false-accept surface for the short spans that are cheapest to fabricate,
and the docs layers are build output that moves. The strict check repairs itself instead - on a miss it scans the
whole file and refuses with "the span moved to <path>:<N> - cite that", which costs the author one edit.

A legacy `- Recall: ...` line (the 2026-09-08 commit-receipt form, no stage) parses with `stage=None` and is
reported UNSTAGED - never silently dropped, never counted for a stage, and never verified as a staged
citation (the pre-P67 form carries no span).

Exit 0 = the receipt verifies, 1 = refused (one block of text, no partial credit), 2 = usage.

    python content/video_engine/scripts/recall_verify.py <episode dir or ledger path> [--json]

This module names no episode and no project, and never writes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
LEDGER_NAME = "PRODUCTION-LEDGER.md"
DOCS_FIND_REL = "content/video_engine/scripts/docs_find.py"

#: The nine stages of the runbook's step 0, in its order. Each is owed at least one citation.
STAGES = ("package", "script", "voice", "world", "evidence", "motion", "sound", "publish", "rulings")
MIN_SPAN = 12

HEADING_RE = re.compile(r"^##(?!#)\s*Recall")
ANY_H2_RE = re.compile(r"^##(?!#)\s")
LINE_RE = re.compile(r"^\s*[-*]\s*Recall(?:\(\s*([A-Za-z_]+)\s*\))?\s*:\s*(.+?)\s*$")
ZERO_RE = re.compile(r"^docs_find\s+0\s+hits?\s+for\s+(?:\"([^\"]+)\"|([^\"(]+?))\s*(?:\(([^)]*)\))?\s*$", re.I)
CITE_RE = re.compile(
    r"^`?(?P<path>[^\s\"`]+?)(?::(?P<line>\d+))?`?\s*(?:\"(?P<span>[^\"]*)\")?\s*(?:\((?P<note>.*)\))?\s*$"
)


def collapse(text: str) -> str:
    """Runs of whitespace become one space; case is untouched (the match is case-sensitive)."""
    return re.sub(r"\s+", " ", text).strip()


@dataclass(frozen=True)
class Citation:
    """One `- Recall...` line of the block, parsed. `kind` is "cite" or "zero"."""

    kind: str
    stage: str | None
    raw: str
    lineno: int
    path: str | None = None
    line: int | None = None
    span: str | None = None
    term: str | None = None
    note: str | None = None

    @property
    def where(self) -> str:
        return self.path if self.line is None else f"{self.path}:{self.line}"

    @property
    def label(self) -> str:
        stage = self.stage if self.stage else "-"
        where = f'docs_find 0 hits for "{self.term}"' if self.kind == "zero" else self.where
        return f"Recall({stage}) {where}"


@dataclass
class RecallBlock:
    """The LAST `## Recall` block of a ledger: its heading, its text (for the sha) and one record per line."""

    heading: str | None = None
    heading_line: int = 0
    headings_found: int = 0
    text: str = ""
    citations: list[Citation] = field(default_factory=list)

    @property
    def found(self) -> bool:
        return self.heading is not None

    def sha256(self) -> str:
        return hashlib.sha256(self.text.encode("utf-8")).hexdigest()

    def stage_counts(self) -> dict[str, int]:
        return {s: sum(1 for c in self.citations if c.stage == s) for s in STAGES}

    def unstaged(self) -> list[Citation]:
        return [c for c in self.citations if c.stage is None]


def _parse_line(stage: str | None, body: str, raw: str, lineno: int) -> Citation:
    zero = ZERO_RE.match(body)
    if zero:
        term = (zero.group(1) or zero.group(2) or "").strip().strip("`")
        return Citation("zero", stage, raw, lineno, term=term, note=zero.group(3))
    cite = CITE_RE.match(body)
    if not cite:
        return Citation("cite", stage, raw, lineno, path=None)
    line = cite.group("line")
    return Citation(
        "cite", stage, raw, lineno,
        path=cite.group("path"),
        line=int(line) if line else None,
        span=cite.group("span"),
        note=cite.group("note"),
    )


def parse_block(text: str) -> RecallBlock:
    """The LAST `## Recall` heading's block (to the next `## ` heading or EOF), one record per `Recall` line."""
    lines = text.splitlines()
    starts = [i for i, ln in enumerate(lines) if HEADING_RE.match(ln)]
    if not starts:
        return RecallBlock()
    start = starts[-1]
    end = len(lines)
    for i in range(start + 1, len(lines)):
        if ANY_H2_RE.match(lines[i]):
            end = i
            break
    body = lines[start:end]
    block = RecallBlock(
        heading=lines[start].strip(),
        heading_line=start + 1,
        headings_found=len(starts),
        text="\n".join(body).rstrip() + "\n",
    )
    for offset, raw in enumerate(body):
        match = LINE_RE.match(raw)
        if not match:
            continue
        block.citations.append(_parse_line(match.group(1), match.group(2), raw.strip(), start + offset + 1))
    return block


def resolve_ledger(target: Path) -> Path:
    """An episode dir or the ledger path itself."""
    target = Path(target)
    return target / LEDGER_NAME if target.is_dir() else target


def docs_find_hits(repo: Path, term: str) -> list[dict]:
    """Re-run a zero-hit claim through docs_find as a SUBPROCESS (a stale layer is the query side's problem)."""
    script = Path(repo) / DOCS_FIND_REL
    if not script.exists():
        raise RuntimeError(f"{DOCS_FIND_REL} is not in this repo")
    out = subprocess.run(
        [sys.executable, str(script), term, "--json", "--limit", "1"],
        cwd=str(repo), capture_output=True, text=True, timeout=300,
    )
    if out.returncode != 0:
        raise RuntimeError(f"docs_find exited {out.returncode}: {collapse(out.stderr)[:200]}")
    try:
        return list(json.loads(out.stdout).get("hits") or [])
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"docs_find printed no JSON: {exc}") from exc


def _resolve_cited(repo: Path, rel: str) -> Path | None:
    """The cited path inside the repo, or None when it points outside it."""
    if Path(rel).is_absolute() or rel.startswith(("/", "\\")):
        return None
    candidate = (Path(repo) / rel).resolve()
    try:
        candidate.relative_to(Path(repo).resolve())
    except ValueError:
        return None
    return candidate


def _check_span(citation: Citation, lines: list[str]) -> str | None:
    """The span on the EXACT cited line, or the refusal - naming where the span actually is."""
    want = collapse(citation.span)
    if len(want) < MIN_SPAN:
        return (f'the span is {len(want)} characters; a span is at least {MIN_SPAN} '
                f'("{citation.span}") - quote more of the line')
    if want in collapse(lines[citation.line - 1]):
        return None
    moved = [i + 1 for i, ln in enumerate(lines) if want in collapse(ln)]
    head = f'line {citation.line} does not carry the span "{citation.span}"'
    if moved:
        return f"{head}; the span moved to {citation.path}:{moved[0]} - cite that"
    return (f"{head}; it is nowhere in {citation.path}. "
            f'Line {citation.line} reads: "{collapse(lines[citation.line - 1])[:90]}"')


def _check_citation(repo: Path, citation: Citation) -> str | None:
    """One citation, re-read off disk. Returns the reason it is refused, or None."""
    grammar = 'the grammar is `<path>:<line> "<verbatim span>" (<note>)`'
    if not citation.path:
        return f"the line names no path - {grammar}"
    resolved = _resolve_cited(repo, citation.path)
    if resolved is None:
        return f"the path is outside the repo: {citation.path}"
    if not resolved.is_file():
        return f"no such file in the repo: {citation.path}"
    if citation.line is None:
        return f"the citation names no line - {grammar}"
    lines = resolved.read_text(encoding="utf-8", errors="replace").splitlines()
    if citation.line > len(lines) or citation.line < 1:
        return f"line {citation.line} is past the end of the file ({len(lines)} lines)"
    if citation.span is None:
        return f"the citation carries no quoted span - read line {citation.line} back and quote it"
    return _check_span(citation, lines)


def _check_zero(repo: Path, citation: Citation) -> tuple[str | None, str | None]:
    """A zero-hit claim, re-run. Returns (refusal, note) - a broken docs_find is named, never a free pass."""
    if not citation.term:
        return 'the claim names no term - `docs_find 0 hits for "<term>"`', None
    try:
        hits = docs_find_hits(repo, citation.term)
    except Exception as exc:  # plumbing, not a claim: named on its own line, never silently accepted
        return None, f"UNCHECKED {citation.label} - docs_find could not be re-run ({exc})"
    if not hits:
        return None, None
    hit = hits[0]
    where = f"{hit.get('path')}:{hit.get('line')}"
    name = hit.get("name") or collapse(str(hit.get("snippet") or ""))[:70]
    return f"the record answers with a hit: {where} - {name}", None


def _stage_refusals(block: RecallBlock) -> list[str]:
    """A stage owed a citation and given none; and a stage name that is not one of the nine."""
    out = []
    counts = block.stage_counts()
    for stage in STAGES:
        if counts[stage] == 0:
            out.append(f'REFUSED stage "{stage}" - no citation at all: add '
                       f'`- Recall({stage}): <path>:<line> "<verbatim span>" (<note>)`, '
                       f'or `- Recall({stage}): docs_find 0 hits for "<term>"`')
    for citation in block.citations:
        if citation.stage is not None and citation.stage not in STAGES:
            out.append(f'REFUSED (ledger line {citation.lineno}) unknown stage "{citation.stage}" - '
                       f"the stages are: {' '.join(STAGES)}")
    return out


def verify(repo: Path, ledger: Path) -> tuple[bool, list[str]]:
    """Re-read every citation of the ledger's last `## Recall` block. Returns (ok, the report lines)."""
    repo = Path(repo)
    path = resolve_ledger(ledger)
    try:
        rel = path.resolve().relative_to(repo.resolve()).as_posix()
    except ValueError:
        rel = path.as_posix()
    lines = [f"Recall receipt: {rel}"]
    if not path.is_file():
        lines.append(f"REFUSED - no ledger at {rel}: the receipt lives in the project's {LEDGER_NAME}")
        return False, lines
    block = parse_block(path.read_text(encoding="utf-8", errors="replace"))
    if not block.found:
        lines.append(f"REFUSED - {rel} carries no `## Recall` heading: the receipt's nine stages "
                     f"({' '.join(STAGES)}) live under one")
        return False, lines
    which = "" if block.headings_found == 1 else f" (the last of {block.headings_found} `## Recall` headings)"
    lines.append(f'Read: "{block.heading}" at line {block.heading_line}{which} - '
                 f"{len(block.citations)} Recall line(s), sha256 {block.sha256()[:12]}")

    refusals: list[str] = []
    notes: list[str] = []
    for citation in block.citations:
        if citation.stage is None:
            continue  # UNSTAGED: reported below, never verified as a staged line and never dropped
        if citation.kind == "zero":
            why, note = _check_zero(repo, citation)
            if note:
                notes.append(note)
        else:
            why = _check_citation(repo, citation)
        if why:
            refusals.append(f"REFUSED {citation.label} - {why}")
    for citation in block.unstaged():
        notes.append(f"UNSTAGED (ledger line {citation.lineno}) {citation.raw} - no stage: rewrite it as "
                     f'`- Recall(<stage>): <path>:<line> "<verbatim span>" (<note>)`')
    refusals.extend(_stage_refusals(block))

    lines.extend(notes)
    lines.extend(refusals)
    if refusals:
        lines.append(f"REFUSED - {len(refusals)} problem(s) in the receipt; no partial credit.")
        return False, lines
    counts = block.stage_counts()
    for stage in STAGES:
        lines.append(f"  {stage}: {counts[stage]} citation(s) verified")
    verified = len(block.citations) - len(block.unstaged())
    lines.append(f"PASS - {verified} citation(s) verified across {len(STAGES)} stages.")
    return True, lines


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Re-read a project's `## Recall` receipt off disk, line by line.")
    parser.add_argument("target", help="the episode dir or the ledger path")
    parser.add_argument("--json", action="store_true", dest="as_json", help="the same report as one JSON object")
    parser.add_argument("--repo", default=str(REPO), help="repository root (default: this checkout)")
    args = parser.parse_args(argv)
    ok, lines = verify(Path(args.repo), Path(args.target))
    if args.as_json:
        print(json.dumps({"ok": ok, "target": str(args.target), "lines": lines,
                          "refusals": [ln for ln in lines if ln.startswith("REFUSED")]}, indent=2))
    else:
        print("\n".join(lines))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
