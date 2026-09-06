"""DOCS-MANIFEST - one compact entry per DOCUMENT: what is inside it, in one `rg` call.

`DOCS-INDEX` is section-level: it answers "where is the section about X". The question that
keeps costing walks of the docs tree is document-level - "do we have X at all, and which doc
holds it" - and a heading index answers that only after you already know the heading. This
folds the index into one record per file: title, purpose, what the file OWNS (`defines`), what
it only refers to (`mentions`), and its ten most frequent body terms. Two artifacts, the same
records:

    docs/DOCS-MANIFEST.jsonl   one JSON object per document
    docs/DOCS-MANIFEST.md      the same, grouped by kind, one line per document, <= 60 KB

    python content/video_engine/scripts/build_docs_manifest.py --write   # regenerate both
    python content/video_engine/scripts/build_docs_manifest.py --check   # exit 1 when stale

The input is `docs/DOCS-INDEX.jsonl` (`--index` moves it) plus the documents themselves, read
for the H1, its byline and its first paragraph. Level-7 records (CAPABILITIES / BACKLOG table
rows) fold into their file: they carry the capability names and backlog ids, which is exactly
what "do we have X" asks for. Standard library only; deterministic (sorted by path, no
timestamps) and written with LF endings.

`kind` is decided by path prefix and filename, first rule in KIND_RULES wins:

    | rule                                       | kind          |
    |--------------------------------------------|---------------|
    | docs/portable/OPERATOR-RULINGS.md           | ruling-ledger |
    | docs/content-video-engine/CAPABILITIES.md   | capabilities  |
    | docs/content-video-engine/BACKLOG.md        | backlog       |
    | docs/content-video-engine/<NN>-*.md         | doctrine      |
    | README*.md, *INDEX*.md, SKILL_ROUTER.md,    | index         |
    |   AGENT_START_HERE.md                       |               |
    | docs/content-video-engine/patterns/**       | pattern       |
    | docs/content-video-engine/briefs/**         | brief         |
    | docs/content-video-engine/prompts/**        | prompt        |
    | docs/runbooks/**, docs/harness/**,          | runbook       |
    |   *RUNBOOK*.md                              |               |
    | content/video_engine/sources/**             | source-bundle |
    | docs/research/**, FINDING-*.md,             | research      |
    |   *-REVIEW.md, *-HARVEST.md                 |               |
    | docs/portable/**, RULE-*.md, PIPELINE.md,   | doctrine      |
    |   AGENTS*.md                                |               |
    | anything else                               | other         |
"""
from __future__ import annotations

import argparse
import difflib
import fnmatch
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_docs_index import (  # noqa: E402
    HEADING, REPO, ROW_ID, ROW_LEVEL, TABLE_SEP, split_lines, strip_emphasis, truncate, unfenced,
)

INDEX_REL = "docs/DOCS-INDEX.jsonl"
JSONL_REL = "docs/DOCS-MANIFEST.jsonl"
MD_REL = "docs/DOCS-MANIFEST.md"

TITLE_MAX = 120
PURPOSE_MAX = 240
BYLINE_MAX = 160
CAPABILITY_TITLE_MAX = 60
KEY_TERM_LIMIT = 10
MENTION_LIMIT = 24
SENTENCE_MIN = 40        # below this a "sentence" is a stub ("Hand-maintained.") - read on

MD_MAX_BYTES = 60_000
# (title, purpose, key terms, defines) budgets for one Markdown line; the first rung whose whole
# file fits MD_MAX_BYTES wins, so the artifact stays cheap to grep as the docs tree grows. The
# untruncated record is always in the JSONL.
MD_LADDER = ((120, 240, 10, 12), (110, 180, 10, 10), (100, 150, 9, 9), (90, 130, 8, 8),
             (80, 120, 7, 7), (70, 110, 6, 6), (60, 90, 6, 5), (55, 70, 6, 4), (50, 60, 6, 3),
             (45, 50, 5, 3), (40, 40, 4, 2))

KINDS = ("doctrine", "ruling-ledger", "capabilities", "backlog", "pattern", "runbook", "research",
         "source-bundle", "brief", "prompt", "index", "other")
FALLBACK_KIND = "other"

# (matcher, pattern, kind); "path" is exact, "prefix" a directory, "glob" the whole repo-relative
# path, "name" the basename. First match wins - see the table in the module docstring.
KIND_RULES = (
    ("path", "docs/portable/OPERATOR-RULINGS.md", "ruling-ledger"),
    ("path", "docs/content-video-engine/CAPABILITIES.md", "capabilities"),
    ("path", "docs/content-video-engine/BACKLOG.md", "backlog"),
    ("glob", "docs/content-video-engine/[0-9]*-*.md", "doctrine"),
    ("name", "README*.md", "index"),
    ("name", "*INDEX*.md", "index"),
    ("name", "SKILL_ROUTER.md", "index"),
    ("name", "AGENT_START_HERE.md", "index"),
    ("prefix", "docs/content-video-engine/patterns/", "pattern"),
    ("prefix", "docs/content-video-engine/briefs/", "brief"),
    ("prefix", "docs/content-video-engine/prompts/", "prompt"),
    ("prefix", "docs/runbooks/", "runbook"),
    ("prefix", "docs/harness/", "runbook"),
    ("name", "*RUNBOOK*.md", "runbook"),
    ("prefix", "content/video_engine/sources/", "source-bundle"),
    ("prefix", "docs/research/", "research"),
    ("name", "FINDING-*.md", "research"),
    ("name", "*-REVIEW.md", "research"),
    ("name", "*-HARVEST.md", "research"),
    ("prefix", "docs/portable/", "doctrine"),
    ("name", "RULE-*.md", "doctrine"),
    ("name", "PIPELINE.md", "doctrine"),
    ("name", "AGENTS*.md", "doctrine"),
)

# --- id shapes ----------------------------------------------------------------------------
RULING_ID = re.compile(r"\b[EA]\d{1,3}\b")            # E41, A7 - owned by the rulings ledger
GATE_ID = re.compile(r"\b(?:[GMSVJ]\d\d[a-z]?|G-[a-z])\b")   # G45, M08, S12a, G-g
PLAN_ID = re.compile(r"\bP\d{1,3}\b")                 # P13, P36
ID_SHAPES = (RULING_ID, GATE_ID, PLAN_ID)

LINK = re.compile(r"\[([^\]\n]+)\]\([^)\n]*\)")
LEADING_MARKER = re.compile(r"^\s*(?:[-*+]\s+|>\s*|\d+\.\s+)+")
METADATA_KEY = re.compile(
    r"^(?:Status|Generated|Proven by|Supersedes|Superseded by|Last reviewed|Reviewed|Updated"
    r"|Date|Owner|Author|Source|Sources|Confidence|Scope)\s*:", re.I)
SENTENCE_END = re.compile(r"[.!?](?=\s|$)")
ABBREVIATIONS = frozenset({"e.g.", "i.e.", "cf.", "vs.", "etc.", "approx.", "no.", "fig.", "dr.",
                           "mr.", "ms.", "st.", "ch.", "vol.", "al."})
NESTED_NUMBER = re.compile(r"\d+\.\d+\.$")
INITIAL = re.compile(r"\b[A-Z]\.$")
OPENERS = "\"'`(“‘[*"


# --- text helpers -------------------------------------------------------------------------

def plain(text: str, limit: int) -> str:
    """One line, no links, no list/quote markers, no emphasis, at most `limit` characters."""
    return truncate(strip_emphasis(LINK.sub(r"\1", text)), limit)


def wholly_emphasised(line: str) -> bool:
    """True for a line that is entirely one bold or italic span - a subtitle, never a sentence."""
    text = line.strip()
    for mark in ("**", "*", "_"):
        span = len(mark)
        if (len(text) > 2 * span and text.startswith(mark) and text.endswith(mark)
                and mark not in text[span:-span]):
            return True
    return False


def first_sentence(text: str, limit: int = PURPOSE_MAX) -> str:
    """The first sentence of a paragraph, or the whole thing truncated when it has no end."""
    flat = " ".join(text.split())
    for m in SENTENCE_END.finditer(flat):
        head = flat[:m.end()]
        if len(head) < SENTENCE_MIN:
            continue
        last = head.split()[-1].lower()
        if last in ABBREVIATIONS or NESTED_NUMBER.search(head) or INITIAL.search(head):
            continue
        rest = flat[m.end():].lstrip()
        if rest and not (rest[0].isupper() or rest[0] in OPENERS):
            continue
        return truncate(head, limit)
    return truncate(flat, limit)


def natural_key(value: str) -> tuple:
    """Sort ids the way they read: E9 before E11, letters before numbers."""
    m = re.match(r"([^\d]*)(\d*)", value)
    prefix, digits = (m.group(1), m.group(2)) if m else (value, "")
    return (prefix.casefold(), int(digits) if digits else -1, value)


def natural_sorted(values) -> list[str]:
    return sorted(set(values), key=natural_key)


# --- the document itself: title, byline, purpose -------------------------------------------

def paragraphs(lines: list[str], start: int, end: int) -> list[list[str]]:
    """Blank-line separated prose blocks in [start, end): no fences, tables, rules or headings."""
    blocks: list[list[str]] = []
    current: list[str] = []
    for _, line in unfenced(lines[start:end]):
        stripped = line.strip()
        skip = (not stripped or TABLE_SEP.match(line) or stripped.startswith(("|", "<!--"))
                or HEADING.match(line))
        if skip:
            if current:
                blocks.append(current)
                current = []
            continue
        current.append(stripped)
    if current:
        blocks.append(current)
    return blocks


def is_byline(block: list[str]) -> bool:
    """A byline block: a wholly italic/bold subtitle, or a `Status:` / `Generated:` metadata run -
    including the `> **STATUS: RECORD.**` callout, which 19 docs share verbatim and which says
    nothing about what is inside any of them."""
    head = block[0]
    stamped = strip_emphasis(LEADING_MARKER.sub("", head))
    return bool(wholly_emphasised(head) or METADATA_KEY.match(stamped))


def block_text(block: list[str]) -> str:
    return " ".join(LEADING_MARKER.sub("", line) for line in block)


def h1_position(lines: list[str]) -> tuple[int, int, str] | None:
    """(line index, level, text) of the first level-1 heading, or None."""
    for i, line in unfenced(lines):
        m = HEADING.match(line)
        if m and len(m.group(1)) == 1:
            return (i, 1, m.group(2).strip())
    return None


def next_heading(lines: list[str], after: int) -> int:
    for i, line in unfenced(lines):
        if i > after and HEADING.match(line):
            return i
    return len(lines)


def first_h2(lines: list[str]) -> str:
    for _, line in unfenced(lines):
        m = HEADING.match(line)
        if m and len(m.group(1)) == 2:
            return m.group(2).strip()
    return ""


def document_head(rel_path: str, text: str) -> tuple[str, str, str | None]:
    """(title, purpose, byline) read from the file. Purpose is the H1's lead paragraph, else the
    first non-heading non-byline paragraph anywhere, else the first H2."""
    lines = split_lines(text)
    h1 = h1_position(lines)
    title = plain(h1[2], TITLE_MAX) if h1 else rel_path.rsplit("/", 1)[-1]
    byline: str | None = None
    lead_blocks = paragraphs(lines, h1[0] + 1, next_heading(lines, h1[0])) if h1 else []
    for block in lead_blocks:
        if is_byline(block):
            byline = byline or plain(block_text(block), BYLINE_MAX)
            continue
        return (title, first_sentence(plain(block_text(block), PURPOSE_MAX * 2)), byline)
    for block in paragraphs(lines, 0, len(lines)):
        if is_byline(block):
            continue
        return (title, first_sentence(plain(block_text(block), PURPOSE_MAX * 2)), byline)
    return (title, plain(first_h2(lines), PURPOSE_MAX), byline)


# --- kind ----------------------------------------------------------------------------------

def classify(rel_path: str) -> str:
    """The first KIND_RULES match, else `other` (which the report must list, never hide)."""
    name = rel_path.rsplit("/", 1)[-1]
    for matcher, pattern, kind in KIND_RULES:
        hit = {
            "path": rel_path == pattern,
            "prefix": rel_path.startswith(pattern),
            "glob": fnmatch.fnmatchcase(rel_path, pattern),
            "name": fnmatch.fnmatchcase(name, pattern),
        }[matcher]
        if hit:
            return kind
    return FALLBACK_KIND


# --- what a document owns, and what it only refers to --------------------------------------

def ids_in(texts, patterns=ID_SHAPES) -> list[str]:
    return [m.group(0) for text in texts for p in patterns for m in p.finditer(text)]


def defines_of(kind: str, headings: list[str], h2s: list[str], rows: list[str]) -> list[str]:
    """The ids and names this file OWNS: rulings from the ledger's H2s, gate and plan ids from
    its own headings and table rows, capability names, backlog ids."""
    owned: list[str] = []
    if kind == "ruling-ledger":
        owned += ids_in(h2s, (RULING_ID,))
    owned += ids_in(headings + rows, (GATE_ID, PLAN_ID))
    if kind == "capabilities":
        owned += [truncate(row, CAPABILITY_TITLE_MAX) for row in rows]
    if kind == "backlog":
        owned += [row.split(" ", 1)[0] for row in rows
                  if row and ROW_ID.fullmatch(row.split(" ", 1)[0])]
    return natural_sorted(t for t in owned if t)


def mentions_of(records: list[dict], defines: set[str]) -> list[str]:
    """Ids of the same shapes carried by this file's terms, labels and leads but owned elsewhere."""
    texts = [t for r in records for t in [*r["terms"], *r["labels"], r["lead"]] if t]
    return natural_sorted(i for i in ids_in(texts) if i not in defines)[:MENTION_LIMIT]


def key_terms_of(records: list[dict]) -> list[str]:
    """The most frequent distinct terms and labels, by count then first appearance. A phrase
    ending in `:` is a lead-in ("Why:", "Where it applies:"), not vocabulary."""
    counts: Counter[str] = Counter()
    first: dict[str, tuple[int, str]] = {}
    for record in records:
        for value in [*record["labels"], *record["terms"]]:
            value = value.strip()
            if not value or value.endswith(":"):
                continue
            key = value.casefold()
            counts[key] += 1
            first.setdefault(key, (len(first), value))
    ranked = sorted(counts, key=lambda k: (-counts[k], first[k][0]))
    return [first[k][1] for k in ranked[:KEY_TERM_LIMIT]]


# --- the manifest ---------------------------------------------------------------------------

def group_by_path(records: list[dict]) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = {}
    for record in records:
        grouped.setdefault(record["path"], []).append(record)
    return grouped


def read_text(repo_root: Path, rel_path: str) -> str:
    path = Path(repo_root) / rel_path
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def build(records: list[dict], repo_root: Path = REPO) -> list[dict]:
    """One record per indexed document, sorted by path. Level-7 rows fold into their file."""
    grouped = group_by_path(records)
    out: list[dict] = []
    for rel_path in sorted(grouped, key=lambda p: (p.lower(), p)):
        file_records = grouped[rel_path]
        sections = [r for r in file_records if r["level"] <= 6]
        rows = [r["heading"] for r in file_records if r["level"] == ROW_LEVEL]
        headings = [r["heading"] for r in sections]
        h2s = [r["heading"] for r in sections if r["level"] == 2]
        kind = classify(rel_path)
        title, purpose, byline = document_head(rel_path, read_text(repo_root, rel_path))
        defines = defines_of(kind, headings, h2s, rows)
        out.append({
            "path": rel_path,
            "doc": file_records[0]["doc"],
            "title": title,
            "kind": kind,
            "purpose": purpose,
            "sections": len(sections),
            "defines": defines,
            "mentions": mentions_of(file_records, set(defines)),
            "key_terms": key_terms_of(file_records),
            "byline": byline,
        })
    return out


def load_index(path: Path) -> list[dict]:
    """The index records, validated enough that a wrong `--index` fails loudly."""
    if not Path(path).is_file():
        raise ValueError(f"{Path(path).as_posix()} not found - run build_docs_index.py --write")
    records = []
    for n, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        record = json.loads(line)
        missing = [k for k in ("path", "level", "heading", "lead", "labels", "terms", "doc")
                   if k not in record]
        if missing:
            raise ValueError(f"{Path(path).as_posix()}:{n}: record is missing {', '.join(missing)}")
        records.append(record)
    if not records:
        raise ValueError(f"{Path(path).as_posix()}: no records")
    return records


# --- rendering -------------------------------------------------------------------------------

def render_jsonl(entries: list[dict]) -> str:
    return "".join(json.dumps(e, ensure_ascii=False) + "\n" for e in entries)


def md_line(entry: dict, title_max: int, purpose_max: int, term_max: int, define_max: int) -> str:
    defines = entry["defines"][:define_max]
    extra = len(entry["defines"]) - len(defines)
    if extra:
        defines = defines + [f"+{extra} more"]
    return (f"- {entry['path']} — {truncate(entry['title'], title_max)}"
            f" — {truncate(entry['purpose'], purpose_max)}"
            f" — defines: {'; '.join(defines) if defines else '—'}"
            f" — terms: {'; '.join(entry['key_terms'][:term_max]) or '—'}")


def render_md(entries: list[dict], budgets: tuple[int, int, int, int] | None = None) -> str:
    """Grouped by kind, one line per document. Budgets shrink until the file fits MD_MAX_BYTES."""
    if budgets is None:
        for rung in MD_LADDER:
            text = render_md(entries, rung)
            if len(text.encode("utf-8")) <= MD_MAX_BYTES:
                return text
        return render_md(entries, MD_LADDER[-1])
    kinds = [k for k in KINDS if any(e["kind"] == k for e in entries)]
    head = [
        "# DOCS-MANIFEST — what is inside each document, one line each",
        "",
        "Generated by `python content/video_engine/scripts/build_docs_manifest.py --write`. Do",
        "not hand-edit it: `--check` fails when it drifts from the docs.",
        "",
        'The recipe — one call answers "do we have X":',
        "",
        "```bash",
        'rg -i "<what you think we might have>" docs/DOCS-MANIFEST.md   # one hit per document',
        'rg -i "<term>" docs/DOCS-INDEX.jsonl                           # then the section inside it',
        "```",
        "",
        "`defines` is what a document OWNS — ruling ids from the ledger, gate and plan ids from",
        "its own headings, capability names, backlog ids. `terms` are its most frequent body",
        "terms. Purpose, terms and defines are truncated here to keep the file cheap to grep;",
        "the whole record, plus `mentions` and `byline`, is in `DOCS-MANIFEST.jsonl`.",
        "",
        f"{len(entries)} documents across {len(kinds)} kinds.",
        "",
    ]
    body: list[str] = []
    for kind in kinds:
        body += [f"## {kind}", ""]
        body += [md_line(e, *budgets) for e in entries if e["kind"] == kind]
        body.append("")
    return "\n".join(head + body)


def rendered(repo_root: Path = REPO, index_rel: str = INDEX_REL) -> dict[str, str]:
    """{relative path: wanted text} for both artifacts."""
    entries = build(load_index(Path(repo_root) / index_rel), Path(repo_root))
    return {JSONL_REL: render_jsonl(entries), MD_REL: render_md(entries)}


def write(repo_root: Path = REPO, index_rel: str = INDEX_REL) -> int:
    """Regenerate both artifacts (LF). Returns the number of documents."""
    texts = rendered(repo_root, index_rel)
    for rel_path, text in texts.items():
        path = Path(repo_root) / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text.encode("utf-8"))
    return len(texts[JSONL_REL].splitlines())


def check(repo_root: Path = REPO, index_rel: str = INDEX_REL) -> list[str]:
    """One entry per stale artifact: "<path> (+added/-removed lines)". Empty means in sync."""
    problems: list[str] = []
    for rel_path, want in rendered(repo_root, index_rel).items():
        path = Path(repo_root) / rel_path
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
    ap.add_argument("--index", default=INDEX_REL, metavar="PATH",
                    help=f"the docs index to fold (default: {INDEX_REL})")
    ap.add_argument("--repo", type=Path, default=REPO, help="repository root (default: this checkout)")
    a = ap.parse_args(argv)
    root = a.repo.resolve()
    index_rel = str(a.index).replace("\\", "/")
    try:
        if a.write:
            documents = write(root, index_rel)
            print(f"build_docs_manifest: {documents} document(s) -> {JSONL_REL} + {MD_REL}")
        problems = check(root, index_rel)
    except (OSError, ValueError, json.JSONDecodeError) as exc:   # a bad index is not staleness
        print(f"build_docs_manifest: INDEX ERROR - {exc}")
        return 2
    if problems:
        print("build_docs_manifest: STALE - " + "; ".join(problems) + " - run --write")
        return 1
    entries = build(load_index(root / index_rel), root)
    size = len(render_md(entries).encode("utf-8"))
    print(f"build_docs_manifest: in sync ({len(entries)} documents, {size} bytes of Markdown)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
