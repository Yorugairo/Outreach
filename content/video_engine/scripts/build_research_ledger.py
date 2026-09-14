"""The research ingestion gate: every run under `docs/research/runs/`, and what cites it.

A Gemini research run lands on disk gitignored. Nothing made it join the work: six of the runs
measured 2026-09-13 were cited by nothing at all, so the reading was paid for and never spent.
This layer makes that visible and checkable - the orphan list, the way the animation registry
lists a formula nothing implements.

    A run is **landed** only when a BACKLOG row or a plan slice cites its path;
    **referenced** when only a doc cites it; **orphan** when nothing does.

The run's own files are gitignored, so only the directory name, the file count and the newest
file's date are read - never the contents. A citation is the literal run path
(`docs/research/runs/<name>`) in a BACKLOG row, a `.claude/PRPs/plans/*.md` slice or any doc
under `docs/`; the generated layers are skipped (an index echoing a doc's line is not a
citation) and so is anything inside the runs tree (a run citing itself is not ingestion).

The second half is the parked-row trigger: a parked BACKLOG row may name what re-surfaces it
(`trigger:` ...). They are extracted read-only into a table, so a parked thing has a stated
condition instead of being forgotten - R26-61's rig was parked on a ruling whose reason has
since changed.

    python content/video_engine/scripts/build_research_ledger.py --write   # regenerate both
    python content/video_engine/scripts/build_research_ledger.py --check   # exit 1 when stale

Standard library only; both artifacts are written LF, sorted, with no timestamp, so two runs
over the same tree are byte-identical.
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
from datetime import datetime
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
REPO = SCRIPTS.parents[2]

RUNS_REL = "docs/research/runs"
BACKLOG_REL = "docs/content-video-engine/BACKLOG.md"
PLANS_REL = ".claude/PRPs/plans"
DOCS_REL = "docs"
INDEX_CONFIG_REL = "docs/DOCS-INDEX.config.json"
JSONL_REL = "docs/RESEARCH-LEDGER.jsonl"
MD_REL = "docs/RESEARCH-LEDGER.md"

RULE = ('a run is landed only when a backlog row or a plan slice cites it - E96-era ruling, '
        'the operator 2026-09-13: "a process that immediately ingests the gemini research and '
        'adds to backlog or exploration"')

STATUS_ORDER = ("orphan", "referenced", "landed")   # the orphans first, everywhere
TRIGGER_MARK = "trigger:"
TRIGGER_MAX = 200
CITED_SHOWN = 3


# --- the tree -------------------------------------------------------------------------------

def generated_docs(root: Path) -> set[str]:
    """The docs-layer artifacts, which echo the docs and must never count as a citation.

    Taken from `DOCS-INDEX.config.json`'s exclude list - its plain (glob-free) entries ARE the
    generated files - so a new layer is skipped here the moment it excludes itself there. The
    index's own output is added on top: it is not in its own exclude list, and counting it would
    both invent citations and re-stale this ledger every time the index's line numbers move."""
    out = {JSONL_REL, MD_REL}
    config = Path(root) / INDEX_CONFIG_REL
    if not config.is_file():
        return out
    try:
        data = json.loads(config.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError, OSError):
        return out
    for entry in data.get("exclude", []):
        if isinstance(entry, str) and "*" not in entry:
            out.add(entry.strip("/"))
    output = data.get("output")
    if isinstance(output, str):
        out |= {f"{output}.jsonl", f"{output}.md"}
    return out


def rel_of(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def run_dirs(root: Path) -> list[Path]:
    runs = Path(root) / RUNS_REL
    if not runs.is_dir():
        return []
    return sorted((p for p in runs.iterdir() if p.is_dir()), key=lambda p: p.name)


def run_files(run: Path) -> list[Path]:
    return sorted(p for p in run.rglob("*") if p.is_file())


def newest_date(files: list[Path]) -> str:
    """The newest file's date (local, YYYY-MM-DD) - the only date a gitignored run offers."""
    stamps = []
    for path in files:
        try:
            stamps.append(path.stat().st_mtime)
        except OSError:
            continue
    if not stamps:
        return ""
    return datetime.fromtimestamp(max(stamps)).strftime("%Y-%m-%d")


# --- the citations --------------------------------------------------------------------------

def source_files(root: Path) -> list[tuple[str, str]]:
    """(kind, relative path) for every file that can cite a run: the BACKLOG, the plan slices,
    then every doc - generated layers and the runs tree itself excluded."""
    root = Path(root)
    skip = generated_docs(root)
    out: list[tuple[str, str]] = []

    backlog = root / BACKLOG_REL
    if backlog.is_file():
        out.append(("backlog", BACKLOG_REL))

    plans = root / PLANS_REL
    if plans.is_dir():
        out += [("plan", rel_of(root, p)) for p in sorted(plans.glob("*.md"))]

    docs = root / DOCS_REL
    if docs.is_dir():
        for path in sorted(docs.rglob("*.md")):
            rel = rel_of(root, path)
            if rel == BACKLOG_REL or rel in skip or rel.startswith(RUNS_REL + "/"):
                continue
            out.append(("doc", rel))
    return out


def citation_re(name: str) -> re.Pattern[str]:
    """The run's own path - `docs/research/runs/<name>` not followed by more name characters,
    so `weight_mass` never matches `weight_mass_two`."""
    return re.compile(re.escape(f"{RUNS_REL}/{name}") + r"(?![\w.-])")


def scan(root: Path, names: list[str]) -> dict[str, list[dict]]:
    """{run name: [{kind, path, line}, ...]} over every source file, read once."""
    patterns = {name: citation_re(name) for name in names}
    hits: dict[str, list[dict]] = {name: [] for name in names}
    for kind, rel in source_files(root):
        try:
            text = (Path(root) / rel).read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for number, line in enumerate(text.splitlines(), start=1):
            if RUNS_REL not in line:
                continue
            for name, pattern in patterns.items():
                if pattern.search(line):
                    hits[name].append({"kind": kind, "path": rel, "line": number})
    return hits


def status_of(cites: list[dict]) -> str:
    if any(c["kind"] in ("backlog", "plan") for c in cites):
        return "landed"
    return "referenced" if cites else "orphan"


# --- the parked-row triggers ------------------------------------------------------------------

def row_id(cell: str) -> str:
    """The BACKLOG row's id, stripped of its markdown (`**R26-61**`, `~~D3~~`)."""
    return cell.replace("*", "").replace("~", "").replace("`", "").strip()


def trigger_text(cell: str) -> str:
    """What the row says re-surfaces it: the text after `trigger:`, to the sentence end."""
    after = cell.split(TRIGGER_MARK, 1)[1]
    after = after.lstrip("`* ").strip()
    cut = after.find(". ", 10)
    if cut != -1:
        after = after[:cut + 1]
    if len(after) > TRIGGER_MAX:
        after = after[:TRIGGER_MAX].rstrip() + "..."
    return after.strip()


def trigger_rows(root: Path) -> list[dict]:
    """Every BACKLOG table row carrying a `trigger:`, in file order. Read-only - the BACKLOG is
    never rewritten by this tool."""
    backlog = Path(root) / BACKLOG_REL
    if not backlog.is_file():
        return []
    rows = []
    for number, line in enumerate(backlog.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.strip()
        if not stripped.startswith("|") or TRIGGER_MARK not in stripped:
            continue
        cells = stripped.strip("|").split("|")
        if len(cells) < 2:
            continue
        body = "|".join(cells[1:])
        if TRIGGER_MARK not in body:
            continue
        rows.append({"row": row_id(cells[0]), "line": number, "trigger": trigger_text(body)})
    return rows


# --- build / render ---------------------------------------------------------------------------

def build(root: Path = REPO) -> list[dict]:
    """One record per run directory, sorted by name. The one entry point for callers."""
    root = Path(root)
    runs = run_dirs(root)
    hits = scan(root, [run.name for run in runs])
    records = []
    for run in runs:
        files = run_files(run)
        cites = hits[run.name]
        records.append({
            "name": run.name,
            "date": newest_date(files),
            "files": len(files),
            "cited_by": [{"path": c["path"], "line": c["line"]} for c in cites],
            "status": status_of(cites),
        })
    return records


def counts(records: list[dict]) -> dict[str, int]:
    return {s: sum(1 for r in records if r["status"] == s) for s in STATUS_ORDER}


def md_cell(text: str) -> str:
    return text.replace("|", r"\|").replace("\n", " ").strip()


def cited_cell(record: dict) -> str:
    cites = record["cited_by"]
    if not cites:
        return "**nothing cites it**"
    shown = ", ".join(f"`{c['path']}:{c['line']}`" for c in cites[:CITED_SHOWN])
    extra = len(cites) - CITED_SHOWN
    return shown + (f", +{extra} more" if extra > 0 else "")


def md_order(record: dict) -> tuple:
    return (STATUS_ORDER.index(record["status"]), record["name"])


def render_md(records: list[dict], triggers: list[dict]) -> str:
    tally = counts(records)
    lines = [
        "# Research ledger - every run, and what cites it",
        "",
        f"> **{RULE}**",
        "",
        "Generated by `content/video_engine/scripts/build_research_ledger.py --write` (a layer of",
        "`build_docs_layers.py`); never edit by hand. The runs' contents are gitignored - only the",
        "directory name, the file count and the newest file's date are read.",
        "",
        f"**{len(records)} runs: {tally['landed']} landed, {tally['referenced']} referenced, "
        f"{tally['orphan']} orphan.** Orphans first: each is research paid for and not spent - "
        "triage it into a BACKLOG row or an explicit retirement.",
        "",
        "| run | date | files | status | cited by |",
        "|---|---|---|---|---|",
    ]
    for record in sorted(records, key=md_order):
        status = record["status"]
        mark = f"**{status}**" if status == "orphan" else status
        lines.append(f"| `{md_cell(record['name'])}` | {record['date'] or '-'} | {record['files']} "
                     f"| {mark} | {md_cell(cited_cell(record))} |")
    lines += [
        "",
        "## Parked rows with a trigger",
        "",
        "Read-only extraction of every BACKLOG row carrying `trigger:` - what a parked row is",
        "waiting for. When a reference exercises the parked thing, the trigger has fired.",
        "",
        "| row | backlog line | trigger |",
        "|---|---|---|",
    ]
    if not triggers:
        lines.append("| - | - | no parked row states a trigger |")
    for row in triggers:
        lines.append(f"| `{md_cell(row['row'])}` | {row['line']} | {md_cell(row['trigger'])} |")
    lines.append("")
    return "\n".join(lines)


def render_jsonl(records: list[dict]) -> str:
    return "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records)


def rendered(root: Path = REPO) -> dict[str, str]:
    records = build(root)
    return {JSONL_REL: render_jsonl(records),
            MD_REL: render_md(records, trigger_rows(root))}


def write(root: Path = REPO) -> list[dict]:
    """Regenerate both artifacts (LF). Returns the records written."""
    for rel, text in rendered(root).items():
        path = Path(root) / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text.encode("utf-8"))
    return build(root)


def check(root: Path = REPO) -> list[str]:
    """One entry per stale artifact: "<path> (+added/-removed lines)". Empty means in sync."""
    problems = []
    for rel, want in rendered(root).items():
        path = Path(root) / rel
        if not path.is_file():
            problems.append(f"{rel} (missing)")
            continue
        have = path.read_text(encoding="utf-8")
        if have == want:
            continue
        diff = list(difflib.ndiff(have.splitlines(), want.splitlines()))
        added = sum(1 for d in diff if d.startswith("+ "))
        removed = sum(1 for d in diff if d.startswith("- "))
        problems.append(f"{rel} (+{added}/-{removed} lines)")
    return problems


def summary(records: list[dict], triggers: list[dict]) -> str:
    tally = counts(records)
    status = ", ".join(f"{tally[s]} {s}" for s in STATUS_ORDER)
    return f"{len(records)} runs ({status}; {len(triggers)} parked rows with a trigger)"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true",
                    help="exit 1 when either artifact is stale (default)")
    ap.add_argument("--write", action="store_true", help="regenerate both artifacts")
    ap.add_argument("--repo", type=Path, default=REPO,
                    help="repository root (default: this checkout)")
    a = ap.parse_args(argv)
    root = a.repo.resolve()
    if a.write:
        print(f"build_research_ledger: {summary(write(root), trigger_rows(root))} "
              f"-> {JSONL_REL} + {MD_REL}")
    problems = check(root)
    if problems:
        print("build_research_ledger: STALE - " + "; ".join(problems) + " - run --write")
        return 1
    print(f"build_research_ledger: in sync ({summary(build(root), trigger_rows(root))})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
