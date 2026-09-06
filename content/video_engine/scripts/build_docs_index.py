"""One flat, greppable index of every heading in `docs/` - the retrieval layer SigMap has not got.

SigMap indexes declared code symbols, so a doctrine query ("animation math min-jerk spring")
ranks a retired scene and never reaches doc 42 or 47; the agent then walks the whole docs tree.
This builds the missing index: one record per Markdown heading under `docs/`, plus the
CAPABILITIES / BACKLOG table rows (those carry capability and backlog names that never appear as
headings). Two artifacts, the same records:

    docs/DOCS-INDEX.jsonl   one JSON object per line - the thing you `rg`
    docs/DOCS-INDEX.md      the same, readable, grouped by file

    python content/video_engine/scripts/build_docs_index.py --write   # regenerate both
    python content/video_engine/scripts/build_docs_index.py --check   # exit 1 when stale (the default)

Excluded from the walk: `docs/research/runs/**` (gitignored scratch), anything under a
`node_modules`, and `docs/DOCS-INDEX.md` itself - indexing the index is a fixpoint, not an index.
Standard library only; the output is deterministic (no timestamps) and written with LF endings.
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]

DOCS_DIR = "docs"
JSONL_REL = "docs/DOCS-INDEX.jsonl"
MD_REL = "docs/DOCS-INDEX.md"
CAPABILITIES_REL = "docs/content-video-engine/CAPABILITIES.md"
BACKLOG_REL = "docs/content-video-engine/BACKLOG.md"

EXCLUDED_FILES = (MD_REL,)
EXCLUDED_PREFIXES = ("docs/research/runs/",)
EXCLUDED_PARTS = ("node_modules",)

LEAD_MAX = 160
TITLE_MAX = 120
LABEL_MAX = 60
LABEL_LIMIT = 6
LABEL_SCAN = 600
ROW_LEVEL = 7            # a table row is not a heading; it sorts after level 6 on sight

HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
FENCE = re.compile(r"^\s*(?:```|~~~)")
TABLE_SEP = re.compile(r"^\s*\|?\s*:?-{3,}")
BOLD = re.compile(r"\*\*(.+?)\*\*", re.S)
CELL_SPLIT = re.compile(r"(?<!\\)\|")
ROW_ID = re.compile(r"[A-Z][A-Za-z0-9]{0,3}(?:-[A-Za-z0-9]{1,2})?'?")
WRAPPED = re.compile(r"~~(.+)~~|\*\*(.+)\*\*", re.S)
LEAD_SEPARATORS = "—–-·:, "


# --- text helpers -------------------------------------------------------------------------

def truncate(text: str, limit: int) -> str:
    """One line, whitespace collapsed, at most `limit` characters."""
    text = " ".join(text.split())
    return text if len(text) <= limit else text[:limit].rstrip()


def strip_emphasis(text: str) -> str:
    """Drop bold/strike/italic markers; a path glob like `*.mjs` survives (no partner on the line)."""
    out = text.replace("**", "").replace("__", "").replace("~~", "")
    out = re.sub(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])", r"\1", out)
    out = re.sub(r"(?<![\w_])_([^_\n]+)_(?![\w_])", r"\1", out)
    return out


def split_lines(text: str) -> list[str]:
    return text.replace("\r\n", "\n").replace("\r", "\n").split("\n")


def unfenced(lines: list[str]):
    """(index, line) for every line outside a fenced code block."""
    fenced = False
    for i, line in enumerate(lines):
        if FENCE.match(line):
            fenced = not fenced
            continue
        if not fenced:
            yield i, line


def doc_id(rel_path: str) -> str | None:
    """The leading numeric id of a numbered doc: 42-DRAWING-KINETICS.md -> "42"."""
    m = re.match(r"(\d+)", rel_path.rsplit("/", 1)[-1])
    return m.group(1) if m else None


def record(path: str, line: int, level: int, doc: str | None, heading: str, lead: str, labels: list[str]) -> dict:
    """The record, keys in the contract's order."""
    return {"path": path, "line": line, "level": level, "doc": doc, "heading": heading, "lead": lead, "labels": labels}


# --- headings -----------------------------------------------------------------------------

def heading_positions(lines: list[str]) -> list[tuple[int, int, str]]:
    """(index, level, text) for every ATX heading outside a fenced code block."""
    out: list[tuple[int, int, str]] = []
    for i, line in unfenced(lines):
        m = HEADING.match(line)
        if m:
            out.append((i, len(m.group(1)), m.group(2).strip()))
    return out


def lead_of(lines: list[str], start: int, end: int) -> str:
    """The section's first real line: not empty, not a table separator, not inside a fence."""
    for _, line in unfenced(lines[start:end]):
        stripped = line.strip()
        if not stripped or TABLE_SEP.match(line):
            continue
        return truncate(strip_emphasis(stripped), LEAD_MAX)
    return ""


def labels_of(lines: list[str], start: int, end: int) -> list[str]:
    """Up to LABEL_LIMIT distinct **bold** phrases from the head of the section body."""
    body = "\n".join(lines[start:end])[:LABEL_SCAN]
    labels: list[str] = []
    for raw in BOLD.findall(body):
        label = truncate(strip_emphasis(raw), LABEL_MAX)
        if label and label not in labels:
            labels.append(label)
        if len(labels) == LABEL_LIMIT:
            break
    return labels


# --- table rows (CAPABILITIES, BACKLOG) ---------------------------------------------------

def cells_of(line: str) -> list[str]:
    r"""The cells of a Markdown table row, or [] when the line is not one. `\|` stays a pipe."""
    if not line.lstrip().startswith("|"):
        return []
    parts = CELL_SPLIT.split(line.strip())
    if parts and not parts[0].strip():
        parts = parts[1:]
    if parts and not parts[-1].strip():
        parts = parts[:-1]
    return [p.replace("\\|", "|").strip() for p in parts]


def split_title(cell: str) -> tuple[str, str]:
    """(title, remainder): the leading **bold** or ~~struck~~ phrase, else the first bold anywhere,
    else the whole cell."""
    for pattern in (r"^\*\*(.+?)\*\*", r"^~~(.+?)~~"):
        m = re.match(pattern, cell, re.S)
        if m:
            return truncate(strip_emphasis(m.group(1)), TITLE_MAX), cell[m.end():]
    m = BOLD.search(cell)
    if m:
        return truncate(strip_emphasis(m.group(1)), TITLE_MAX), cell[m.end():]
    return truncate(strip_emphasis(cell), TITLE_MAX), ""


def clean_lead(text: str) -> str:
    return truncate(strip_emphasis(text).strip().lstrip(LEAD_SEPARATORS), LEAD_MAX)


def row_id(cell: str) -> str:
    """The backlog id of a first cell - bare, **bold**, ~~struck~~ or both - else ""."""
    text = cell.strip()
    for _ in range(2):
        m = WRAPPED.fullmatch(text)
        if not m:
            break
        text = (m.group(1) or m.group(2)).strip()
    return text if ROW_ID.fullmatch(text) else ""


def capability_rows(rel_path: str, lines: list[str], doc: str | None) -> list[dict]:
    """Every CAPABILITIES row: the bold title of the first cell is the name, the rest is the lead."""
    out: list[dict] = []
    for i, line in unfenced(lines):
        cells = cells_of(line)
        if not cells or not cells[0].startswith("**"):
            continue
        title, rest = split_title(cells[0])
        if title:
            out.append(record(rel_path, i + 1, ROW_LEVEL, doc, title, clean_lead(rest), []))
    return out


def backlog_rows(rel_path: str, lines: list[str], doc: str | None) -> list[dict]:
    """Every BACKLOG row with an id first cell: the heading is "<id> <title of cell 2>". When cell 2
    has nothing after its title the decision columns are the lead - that is where a struck row's
    substance lives."""
    out: list[dict] = []
    for i, line in unfenced(lines):
        cells = cells_of(line)
        if len(cells) < 2:
            continue
        rid = row_id(cells[0])
        if not rid:
            continue
        title, rest = split_title(cells[1])
        lead = clean_lead(rest) or clean_lead(" · ".join(c for c in cells[2:] if c.strip()))
        out.append(record(rel_path, i + 1, ROW_LEVEL, doc, f"{rid} {title}".strip(), lead, []))
    return out


# --- the index ----------------------------------------------------------------------------

def file_records(rel_path: str, text: str) -> list[dict]:
    """Every record a single Markdown file contributes."""
    lines = split_lines(text)
    heads = heading_positions(lines)
    doc = doc_id(rel_path)
    out: list[dict] = []
    for n, (i, level, heading) in enumerate(heads):
        end = heads[n + 1][0] if n + 1 < len(heads) else len(lines)
        out.append(record(rel_path, i + 1, level, doc, heading, lead_of(lines, i + 1, end), labels_of(lines, i + 1, end)))
    if rel_path == CAPABILITIES_REL:
        out += capability_rows(rel_path, lines, doc)
    elif rel_path == BACKLOG_REL:
        out += backlog_rows(rel_path, lines, doc)
    return out


def is_excluded(rel_path: str, parts: tuple[str, ...]) -> bool:
    return (
        rel_path in EXCLUDED_FILES
        or any(rel_path.startswith(prefix) for prefix in EXCLUDED_PREFIXES)
        or any(part in EXCLUDED_PARTS for part in parts)
    )


def doc_files(root: Path) -> list[Path]:
    """Every indexable `docs/**/*.md`, sorted case-insensitively for determinism."""
    base = root / DOCS_DIR
    if not base.is_dir():
        return []
    kept = [p for p in base.rglob("*.md") if not is_excluded(p.relative_to(root).as_posix(), p.parts)]
    return sorted(kept, key=lambda p: (p.relative_to(root).as_posix().lower(), p.relative_to(root).as_posix()))


def build_index(root: Path = REPO) -> list[dict]:
    """Every record, sorted by (path, line)."""
    out: list[dict] = []
    for path in doc_files(root):
        rel_path = path.relative_to(root).as_posix()
        out += file_records(rel_path, path.read_text(encoding="utf-8"))
    return sorted(out, key=lambda r: (r["path"].lower(), r["path"], r["line"]))


def render_jsonl(records: list[dict]) -> str:
    return "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records)


def render_md(records: list[dict]) -> str:
    files = sorted({r["path"] for r in records}, key=lambda p: (p.lower(), p))
    head = [
        "# DOCS-INDEX - every heading in `docs/`, flat and greppable",
        "",
        "Generated by `python content/video_engine/scripts/build_docs_index.py --write`. Do not",
        "hand-edit it: `--check` fails when it drifts from the docs.",
        "",
        "The recipe - two calls, no tree walk:",
        "",
        "```bash",
        'rg -i "<term>" docs/DOCS-INDEX.jsonl     # find the section',
        'rg -n "<heading>" <path>                 # jump to it in the file',
        "```",
        "",
        "Levels 1-6 are Markdown heading depth; level 7 is a table row (CAPABILITIES, BACKLOG).",
        "A `{...}` tail lists the section's bold phrases.",
        "",
        f"{len(records)} records across {len(files)} files.",
        "",
    ]
    body: list[str] = []
    for path in files:
        body += [f"## {path}", ""]
        for r in (x for x in records if x["path"] == path):
            line = f"- L{r['line']} [{r['level']}] {r['heading']}"
            if r["lead"]:
                line += f" — {r['lead']}"
            if r["labels"]:
                line += " {" + "; ".join(r["labels"]) + "}"
            body.append(line)
        body.append("")
    return "\n".join(head + body)


def rendered(root: Path = REPO) -> dict[str, str]:
    """{relative path: wanted text} for both artifacts."""
    records = build_index(root)
    return {JSONL_REL: render_jsonl(records), MD_REL: render_md(records)}


def write(root: Path = REPO) -> tuple[int, int]:
    """Regenerate both artifacts (LF). Returns (records, files)."""
    records = build_index(root)
    for rel_path, text in {JSONL_REL: render_jsonl(records), MD_REL: render_md(records)}.items():
        path = root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text.encode("utf-8"))
    return len(records), len({r["path"] for r in records})


def check(root: Path = REPO) -> list[str]:
    """One entry per stale artifact: "<path> (+added/-removed lines)". Empty means in sync."""
    problems: list[str] = []
    for rel_path, want in rendered(root).items():
        path = root / rel_path
        if not path.is_file():
            problems.append(f"{rel_path} (missing)")
            continue
        have = path.read_text(encoding="utf-8")
        if have == want:
            continue
        diff = list(difflib.ndiff(have.splitlines(), want.splitlines()))
        added = sum(1 for d in diff if d.startswith("+ "))
        removed = sum(1 for d in diff if d.startswith("- "))
        problems.append(f"{rel_path} (+{added}/-{removed} lines)")
    return problems


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true", help="exit 1 when either artifact is stale (default)")
    ap.add_argument("--write", action="store_true", help="regenerate both artifacts")
    ap.add_argument("--root", type=Path, default=REPO, help="repository root")
    a = ap.parse_args(argv)
    root = a.root.resolve()
    if a.write:
        records, files = write(root)
        print(f"build_docs_index: {records} record(s) from {files} file(s) -> {JSONL_REL} + {MD_REL}")
    problems = check(root)
    if problems:
        print("build_docs_index: STALE - " + "; ".join(problems) + " - run --write")
        return 1
    index = build_index(root)
    print(f"build_docs_index: in sync ({len(index)} records, {len({r['path'] for r in index})} files)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
