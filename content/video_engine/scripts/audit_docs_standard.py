"""Does every section in `docs/` meet the retrieval standard? Measure it, do not assert it.

GEMINI.md "Research intake" states the standard a written doc has to meet to be retrievable: the
heading names the concept in the words it is searched by, the section opens with a line that says
what it is, and the body carries the vocabulary a `rg` lands on. `docs/DOCS-INDEX.jsonl`
(`build_docs_index.py`) already carries exactly those three fields per heading - `heading`, `lead`,
`labels`/`terms` - so the standard is measurable, and a docs pass can have a gate instead of an
opinion.

Per heading (table rows, level 7, are not headings and are skipped):

    lead_ok    the section's first real line is >= LEAD_MIN chars, OR the heading is exempt
    termed     the section carries bold labels or body terms - something to `rg` for
    generic    the heading, after stripping numbering ("42.6", "3.", "§"), is a filing word
               ("Overview", "Notes", "Details") that names no concept

A lead exemption is read from the source file, not guessed: a section that opens on a table, a
fenced block, a sub-heading, a long list item, or (for the H1) an italic byline is doing its job
without a prose lead. So is a short line that hands straight to structure - a lead-in ending in
`:`, or an `Operator, 2026-09-05:` attribution - when the next real line is a list item, a quote,
a table row or a fence: the structure under it is the section. The per-doc score weights them
0.5 / 0.35 / 0.15.

    python content/video_engine/scripts/audit_docs_standard.py                  # write the report
    python content/video_engine/scripts/audit_docs_standard.py --only docs/research
    python content/video_engine/scripts/audit_docs_standard.py --min-score 70   # exit 1 below it

`--min-score` gates process docs (everything outside `docs/research/**`); research reports are
reported but never block, because a research pass writes them before the index is rebuilt. Standard
library only; the report is deterministic (no timestamps) and written with LF endings.
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]

INDEX_REL = "docs/DOCS-INDEX.jsonl"
REPORT_REL = "docs/DOCS-STANDARD.md"
RESEARCH_PREFIX = "docs/research/"

ROW_LEVEL = 7            # a table row is not a heading (build_docs_index.ROW_LEVEL)
LEAD_MIN = 40            # a lead shorter than this says nothing a query can land on
LOWEST_N = 20
W_LEAD, W_TERMS, W_SPECIFIC = 0.5, 0.35, 0.15

# Filing words: they name a slot in a document, never a concept. `Sources`, `Checklist` and
# `Changelog` are NOT here - they are legitimate structural sections with a fixed contract.
GENERIC = frozenset({
    "overview", "introduction", "summary", "notes", "background", "context", "details", "misc",
    "other", "todo", "appendix", "references", "contents", "status", "next steps",
    "open questions", "see also", "purpose", "scope", "rules", "examples", "example",
    "questions", "links",
})

NUMBERING = re.compile(r"^[\s§#]*\d+(?:\.\d+)*[.)]?\s+|^[\s§#]*\d+(?:\.\d+)*[.)]\s*|^\s*§\s*")
TRAILING = re.compile(r"[\s:.?!,;]+$")
FENCE = re.compile(r"^(?:```|~~~)")
BULLET = re.compile(r"^(?:[-*+]|\d+[.)])\s+")
ITALIC = re.compile(r"^\*[^\s*].*[^\s*]\*$")
# "Operator, 2026-09-05:", "Operator rulings, 2026-08-29." - who said it and when, not a lead
ATTRIBUTION = re.compile(r"^\**[A-Z][^,\n]{0,40},\s*\d{4}(?:-\d{2}){0,2}\s*\**[:.]?\**$")


# --- heading judgements -------------------------------------------------------------------

def normalized(heading: str) -> str:
    """The heading as the generic test sees it: no numbering, no emphasis, no trailing colon."""
    text = heading.replace("`", "").replace("**", "").replace("*", "").replace("_", " ")
    text = NUMBERING.sub("", text, count=1)
    return TRAILING.sub("", text.strip()).casefold()


def is_generic(heading: str) -> bool:
    return normalized(heading) in GENERIC


def next_nonempty_at(lines: list[str], line_no: int) -> tuple[int, str] | None:
    """(0-based index, stripped text) of the first non-blank line after the 1-based `line_no`."""
    for offset, line in enumerate(lines[line_no:], start=line_no):
        if line.strip():
            return (offset, line.strip())
    return None


def next_nonempty(lines: list[str], line_no: int) -> str | None:
    """The first non-blank line after the 1-based heading line, stripped; None at end of file."""
    found = next_nonempty_at(lines, line_no)
    return found[1] if found else None


def opens_structure(line: str) -> bool:
    """A list item, a quote, a table row or a fence - the section's body is the structure."""
    return bool(BULLET.match(line) or line.startswith((">", "|")) or FENCE.match(line))


def hands_to_structure(lines: list[str], lead_index: int, lead: str) -> bool:
    """A short lead that is only a hand-off: a lead-in ending in `:`, or a `<Name>, <date>:`
    attribution, whose next real line is the structure it announced."""
    if not (lead.rstrip("*").endswith(":") or ATTRIBUTION.match(lead)):
        return False
    nxt = next_nonempty(lines, lead_index + 1)
    return bool(nxt and opens_structure(nxt))


def lead_exempt(lines: list[str], line_no: int, level: int) -> bool:
    """A section that opens on structure, not prose, owes no lead line."""
    found = next_nonempty_at(lines, line_no)
    if found is None:
        return False
    index, nxt = found
    if nxt.startswith("|") or FENCE.match(nxt) or nxt.startswith("#"):
        return True
    if BULLET.match(nxt) and len(nxt) >= LEAD_MIN:
        return True
    if level == 1 and ITALIC.match(nxt):
        return True
    return hands_to_structure(lines, index, nxt)


def has_terms(rec: dict) -> bool:
    return bool(rec.get("labels")) or bool(rec.get("terms"))


def score_of(headings: int, lead_ok: int, termed: int, generic: int) -> int:
    """The weighted per-doc score, 0-100."""
    if headings <= 0:
        return 0
    return round(100 * (W_LEAD * lead_ok / headings
                        + W_TERMS * termed / headings
                        + W_SPECIFIC * (1 - generic / headings)))


# --- the audit ----------------------------------------------------------------------------

def source_lines(repo_root: Path, rel_path: str, cache: dict[str, list[str]]) -> list[str]:
    """The doc's lines, cached. A doc the index names but the tree has not got reads as empty,
    which makes every exemption fail closed (the heading is reported, not silently passed)."""
    if rel_path not in cache:
        path = Path(repo_root) / rel_path
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            text = ""
        cache[rel_path] = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    return cache[rel_path]


def group_of(rel_path: str) -> str:
    return "research" if rel_path.startswith(RESEARCH_PREFIX) else "process"


def audit_doc(repo_root: Path, rel_path: str, recs: list[dict],
              cache: dict[str, list[str]]) -> tuple[dict, list[dict], list[dict]]:
    """(doc summary, missing leads, generic headings) for one file."""
    lines = source_lines(repo_root, rel_path, cache)
    lead_ok = termed = generic = 0
    missing: list[dict] = []
    filing: list[dict] = []
    for rec in recs:
        entry = {"path": rel_path, "line": rec["line"], "heading": rec["heading"]}
        if len(rec.get("lead") or "") >= LEAD_MIN or lead_exempt(lines, rec["line"], rec["level"]):
            lead_ok += 1
        else:
            missing.append(entry)
        termed += 1 if has_terms(rec) else 0
        if is_generic(rec["heading"]):
            generic += 1
            filing.append(entry)
    doc = {"path": rel_path, "group": group_of(rel_path), "headings": len(recs),
           "lead_ok": lead_ok, "termed": termed, "generic": generic,
           "score": score_of(len(recs), lead_ok, termed, generic)}
    return doc, missing, filing


def summarize(docs: list[dict]) -> dict:
    """Files, headings, the three counts, their percentages and the median score."""
    headings = sum(d["headings"] for d in docs)
    lead_ok = sum(d["lead_ok"] for d in docs)
    termed = sum(d["termed"] for d in docs)
    return {
        "files": len(docs),
        "headings": headings,
        "lead_ok": lead_ok,
        "termed": termed,
        "generic": sum(d["generic"] for d in docs),
        "lead_pct": 100.0 * lead_ok / headings if headings else 0.0,
        "termed_pct": 100.0 * termed / headings if headings else 0.0,
        "median_score": float(statistics.median(d["score"] for d in docs)) if docs else 0.0,
    }


def audit(records: list[dict], repo_root: Path = REPO) -> dict:
    """Measure every indexed heading. Docs sorted by path, issues by (path, line)."""
    heads = [r for r in records if r.get("level") != ROW_LEVEL]
    by_path: dict[str, list[dict]] = {}
    for rec in heads:
        by_path.setdefault(rec["path"], []).append(rec)
    cache: dict[str, list[str]] = {}
    docs: list[dict] = []
    missing: list[dict] = []
    filing: list[dict] = []
    for rel_path in sorted(by_path):
        recs = sorted(by_path[rel_path], key=lambda r: r["line"])
        doc, doc_missing, doc_filing = audit_doc(repo_root, rel_path, recs, cache)
        docs.append(doc)
        missing += doc_missing
        filing += doc_filing
    return {
        "docs": docs,
        "groups": {"research": summarize([d for d in docs if d["group"] == "research"]),
                   "process": summarize([d for d in docs if d["group"] == "process"]),
                   "all": summarize(docs)},
        "missing_leads": sorted(missing, key=lambda e: (e["path"], e["line"])),
        "generic_headings": sorted(filing, key=lambda e: (e["path"], e["line"])),
    }


def lowest(docs: list[dict], count: int = LOWEST_N) -> list[dict]:
    return sorted(docs, key=lambda d: (d["score"], d["path"]))[:count]


def below(docs: list[dict], min_score: int, group: str = "process") -> list[dict]:
    return [d for d in docs if d["group"] == group and d["score"] < min_score]


# --- the report ---------------------------------------------------------------------------

GROUP_LABEL = {"research": "Research (`docs/research/**`)",
               "process": "Process (everything else)",
               "all": "All docs"}


def summary_row(name: str, s: dict) -> str:
    return (f"| {GROUP_LABEL[name]} | {s['files']} | {s['headings']} | {s['lead_pct']:.1f}% | "
            f"{s['termed_pct']:.1f}% | {s['generic']} | {s['median_score']:.1f} |")


def issue_lines(entries: list[dict], empty: str) -> list[str]:
    if not entries:
        return [empty]
    return [f"- `{e['path']}:{e['line']}` {e['heading']}" for e in entries]


def render(result: dict, only: str | None = None) -> str:
    """The report. Deterministic: no timestamps, no counts of anything not in `result`."""
    scope = f"`{only}`" if only else "`docs/`"
    out = [
        f"# DOCS-STANDARD - how much of {scope} is retrievable",
        "",
        "Generated by `content/video_engine/scripts/audit_docs_standard.py` from",
        f"`{INDEX_REL}`; rebuild the index first (`build_docs_index.py --write`), then rerun.",
        "Every section is scored on the three things a query needs: a lead line that says what the",
        "section is (0.5), body vocabulary to land on (0.35), and a heading that names a concept",
        "rather than a filing slot (0.15). Sections that open on a table, a fenced block, a",
        "sub-heading, a long list item, or an H1 byline are exempt from the lead check, and so is",
        "a short lead-in (`...:`) or a `<Name>, <date>:` attribution whose next real line is a list",
        "item, a quote, a table row or a fence.",
        "",
        "## Summary",
        "",
        "| Group | Files | Headings | Lead % | Termed % | Generic | Median score |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for name in ("research", "process", "all"):
        out.append(summary_row(name, result["groups"][name]))
    out += ["", f"## The {LOWEST_N} lowest-scoring docs", "",
            "| Score | Doc | Headings | Leads | Termed | Generic |", "|---:|---|---:|---:|---:|---:|"]
    for d in lowest(result["docs"]):
        out.append(f"| {d['score']} | `{d['path']}` | {d['headings']} | "
                   f"{d['lead_ok']}/{d['headings']} | {d['termed']}/{d['headings']} | "
                   f"{d['generic']} |")
    out += ["", "## Appendix A - sections missing a lead line", "",
            f"Non-exempt sections whose first real line is under {LEAD_MIN} characters "
            f"({len(result['missing_leads'])}).", ""]
    out += issue_lines(result["missing_leads"], "- none")
    out += ["", "## Appendix B - generic headings", "",
            f"Headings that name a filing slot, not a concept ({len(result['generic_headings'])}).",
            ""]
    out += issue_lines(result["generic_headings"], "- none")
    out.append("")
    return "\n".join(out)


# --- CLI ----------------------------------------------------------------------------------

def load_records(path: Path, only: str | None = None) -> list[dict]:
    records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if only:
        prefix = only.replace("\\", "/")
        records = [r for r in records if r["path"].startswith(prefix)]
    return records


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--index", default=INDEX_REL, help=f"docs index JSONL (default {INDEX_REL})")
    parser.add_argument("--report", default=REPORT_REL, help=f"report path (default {REPORT_REL})")
    parser.add_argument("--only", default=None, help="restrict to paths under this prefix")
    parser.add_argument("--min-score", type=int, default=None,
                        help="exit 1 when a process doc scores below this")
    parser.add_argument("--root", default=str(REPO), help="repository root (default: this repo)")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = Path(args.root)
    index_path = Path(args.index) if Path(args.index).is_absolute() else root / args.index
    if not index_path.is_file():
        print(f"audit_docs_standard: index not found at {index_path} - "
              f"run build_docs_index.py --write first", file=sys.stderr)
        return 2
    records = load_records(index_path, args.only)
    if not records:
        print(f"audit_docs_standard: no records in {index_path}"
              + (f" under {args.only}" if args.only else ""), file=sys.stderr)
        return 2
    result = audit(records, root)
    report_path = Path(args.report) if Path(args.report).is_absolute() else root / args.report
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_bytes(render(result, args.only).encode("utf-8"))

    every = result["groups"]["all"]
    process = result["groups"]["process"]
    print(f"audit_docs_standard: {every['files']} file(s), {every['headings']} heading(s); "
          f"lead {every['lead_pct']:.1f}%, termed {every['termed_pct']:.1f}%, "
          f"{every['generic']} generic heading(s); process median {process['median_score']:.1f} "
          f"-> {report_path}")
    if args.min_score is None:
        return 0
    failures = below(result["docs"], args.min_score)
    for doc in sorted(failures, key=lambda d: (d["score"], d["path"])):
        print(f"audit_docs_standard: {doc['path']} scores {doc['score']} "
              f"(< {args.min_score})", file=sys.stderr)
    if failures:
        print(f"audit_docs_standard: {len(failures)} process doc(s) below "
              f"--min-score {args.min_score}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
