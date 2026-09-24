"""The capabilities retrieval layer: one compact record per CAPABILITIES.md row.

`docs/content-video-engine/CAPABILITIES.md` answers "do we have X" - but a row averages 1.3 KB and runs
to 9 KB, so a section-index hit lands on a paragraph. This reads every `| **Name** ... |` row and writes
one record per capability (name, section, line, a capped `what`, the `where` paths, a normalised
`state`, the `proof` artifacts, and the effect cards, rulings and BACKLOG ids the row mentions):

    python content/video_engine/scripts/build_capabilities_index.py --write   # regenerate both
    python content/video_engine/scripts/build_capabilities_index.py --check   # exit 1 when stale

    docs/CAPABILITIES-INDEX.jsonl   one JSON record per capability row (docs_find.py searches it first)
    docs/CAPABILITIES-INDEX.md      one line per capability, by section - the page a fresh agent reads

Row forms. A row under a `| Capability | Where | State | Proof |` header has four cells. Two
recoverable forms are parsed and FLAGGED by name and line (printed, and listed at the foot of the
.md, so the doc gets fixed): a row with an unescaped `|` in its prose (extra cells - the leading ones
are joined back into the capability cell) and the two-cell `| **NAME, STATE** (date) - prose | proof |`
form (the state is read off the name). A four-cell row under a three-column header is flagged too.
A three-cell row under the three-column Reference table is the reference form. Any other shape is a
FAILURE: printed by name with its line, and nothing is written. `--strict` turns every flagged row
into a failure. Cells split on `|` outside backticks; `\\|` is a literal pipe. Standard library only.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
REPO = SCRIPTS.parents[2]

CAP_REL = "docs/content-video-engine/CAPABILITIES.md"
JSONL_REL = "docs/CAPABILITIES-INDEX.jsonl"
MD_REL = "docs/CAPABILITIES-INDEX.md"

WHAT_MAX = 120          # characters in `what`, the ellipsis included; cut at a word
STATE_NOTE_MAX = 60     # characters in the state cell's first clause
SLUG_MAX = 60
MD_MAX_BYTES = 44_000   # the start-of-session page; raise only with a stated reason. 2026-09-23: 40_000 -> 44_000 - P69's catch-up adds 16 capability rows (~1.9 KB of one-line entries) to a page already at 39,288 bytes
ELLIPSIS = "…"
ROW_PREFIX = "| **"

# The state vocabulary: the first token in the state cell's lead wins; synonyms fold into one token.
STATE_TOKENS = (
    ("RETIRED", "RETIRED"), ("SUPERSEDED", "RETIRED"), ("STALE", "STALE"),
    ("AWAITING", "AWAITING"), ("LIVE", "LIVE"), ("SHIPPED", "LIVE"), ("STANDARDIZED", "LIVE"),
    ("STANDING", "LIVE"), ("WIRED", "WIRED"), ("LANDED", "WIRED"), ("BUILT", "BUILT"),
    ("UNWIRED", "BUILT"), ("INSTALLED", "INSTALLED"), ("PROVED", "PROVED"), ("PROVEN", "PROVED"),
    ("RULED", "RULED"), ("CLOSED", "CLOSED"), ("REFERENCE", "REFERENCE"),
)
STATE_LEAD_CHARS = 40
STATE_WORDS = "|".join(token for token, _ in STATE_TOKENS)
STATE_RE = re.compile(r"\b(" + STATE_WORDS + r")\b", re.IGNORECASE)
STATE_FOLD = dict(STATE_TOKENS)
UNKNOWN = "UNKNOWN"

# The effect-card axes of docs/EFFECTS-CATALOG.jsonl (2026-09-14); a test pins this against it.
CARD_AXES = ("recipe", "species", "kinetics", "page_species", "plate_option", "page_builder",
             "page_enter", "dock_option", "exit", "chart_to", "idle", "chart_dock", "dock_kind",
             "arrival", "caption", "dock_payload", "overflow", "page_exit", "camera")
CARD_RE = re.compile(r"(?<![\w:])(" + "|".join(sorted(CARD_AXES, key=len, reverse=True))
                     + r"):([a-z0-9][a-z0-9_]*)\b")
RULING_RE = re.compile(r"(?<![\w#])E\d{1,3}(?:\s?(?:s|§)\s?\d+(?:\.\d+)?)?(?![\w])")
BACKLOG_RE = re.compile(r"\bR26-\d+\b")
COMMIT_RE = re.compile(r"(?<![\w#-])(?=[0-9a-f]*[a-f])(?=[0-9a-f]*\d)[0-9a-f]{7,12}(?![\w-])")
TICK_RE = re.compile(r"`([^`]+)`")
BOLD_NAME_RE = re.compile(r"^\*\*(.+?)\*\*")
LINK_RE = re.compile(r"\[([^\]]*)\]\([^)]*\)")
SENTENCE_END_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\"'(*`])")
LEAD_SEP_RE = re.compile(r"^[\s—–:-]+")
TRAILING_STATE_RE = re.compile(r",\s*(" + STATE_WORDS + r")\s*$", re.IGNORECASE)
CLAUSE_RE = re.compile(r"\s[—–-]\s|;|\(|\. ")
SEPARATOR_RE = re.compile(r"\|(\s*:?-{3,}:?\s*\|)+\s*")
TERM_RE = re.compile(r"[a-z][a-z0-9_'-]{2,}")
STOPWORDS = frozenset(
    "the and for with that this from its are was not but one two all any has have been into on "
    "off out per than then them they their there when where which while who why how what our "
    "you your use can each every only also over under after before between same own more most "
    "never always does did done it's is be as at by an or of to in no so do if".split())


# --------------------------------------------------------------------------- cells and text

def split_cells(line: str) -> list[str]:
    """The row's cells: `|` outside backticks separates, `\\|` is a literal pipe."""
    body = line.strip()
    body = body[1:] if body.startswith("|") else body
    cells: list[str] = []
    current: list[str] = []
    in_tick = False
    index = 0
    while index < len(body):
        char = body[index]
        if char == "\\" and body[index + 1:index + 2] == "|":
            current.append("|")
            index += 2
            continue
        if char == "`":
            in_tick = not in_tick
        if char == "|" and not in_tick:
            cells.append("".join(current).strip())
            current = []
        else:
            current.append(char)
        index += 1
    tail = "".join(current).strip()
    if tail:
        cells.append(tail)
    return cells


def plain(text: str) -> str:
    """Markdown stripped to one whitespace-collapsed line."""
    text = LINK_RE.sub(r"\1", text)
    text = text.replace("**", "").replace("`", "")
    return " ".join(text.split())


def cap_words(text: str, width: int) -> str:
    """At most `width` characters, cut at a word boundary with an ellipsis, never mid-word."""
    if len(text) <= width:
        return text
    head = text[: width - len(ELLIPSIS) + 1]       # one spare char: a space there ends a word
    cut = head.rsplit(" ", 1)[0] if " " in head else ""
    cut = cut.rstrip(" ,;:—–-(")
    return (cut + ELLIPSIS) if cut else ""


def unique(items) -> list[str]:
    return list(dict.fromkeys(items))


def ticks(text: str) -> list[str]:
    return unique(t.strip() for t in TICK_RE.findall(text) if t.strip())


def slug(name: str) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    if len(base) > SLUG_MAX:
        base = base[:SLUG_MAX].rsplit("-", 1)[0]
    return base or "capability"


def strip_parenthetical(text: str) -> str:
    """Drop one leading balanced `( ... )` (a date, a commit) and the separator after it."""
    if not text.startswith("("):
        return text
    depth = 0
    for index, char in enumerate(text):
        depth += (char == "(") - (char == ")")
        if depth == 0:
            return LEAD_SEP_RE.sub("", text[index + 1:])
    return text


def first_sentence(capability_cell: str, bold: str) -> str:
    """The capability cell after its bold name: the first sentence, markdown stripped, capped."""
    rest = capability_cell[len(bold) + 4:]
    rest = rest.split("**Use when:**", 1)[0]
    text = plain(strip_parenthetical(LEAD_SEP_RE.sub("", rest)))
    text = SENTENCE_END_RE.split(text, 1)[0] if text else ""
    return cap_words(text.rstrip(), WHAT_MAX)


def read_state(cell: str) -> tuple[str, str]:
    """(token, first clause) of a state cell."""
    text = plain(cell)
    match = STATE_RE.search(text[:STATE_LEAD_CHARS])
    token = STATE_FOLD[match.group(1).upper()] if match else UNKNOWN
    clause = CLAUSE_RE.split(text, 1)[0].strip(" ,")
    return token, cap_words(clause, STATE_NOTE_MAX)


# --------------------------------------------------------------------------- parsing

@dataclass
class Parsed:
    records: list[dict] = field(default_factory=list)
    failures: list[str] = field(default_factory=list)
    flagged: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class Cells:
    """A row's cells assigned to the four columns, and the form it was read in."""
    form: str
    capability: str
    where: str
    state: str
    proof: str
    what: str


def assign(cells: list[str], bold: str, name: str, header_cols: int) -> tuple[Cells | None, str]:
    """(the cells in columns, the name) - or (None, the problem) for a shape no form reads."""
    if header_cols == 3 and len(cells) == 3:
        return Cells("reference", cells[0], cells[1], "REFERENCE", "",
                     cap_words(plain(cells[2]), WHAT_MAX)), name
    if len(cells) >= 4:
        form = "four" if len(cells) == 4 and header_cols == 4 else (
            "extra-pipes" if len(cells) > 4 else f"four-under-{header_cols}-columns")
        capability = " | ".join(cells[:-3])
        return Cells(form, capability, cells[-3], cells[-2], cells[-1],
                     first_sentence(capability, bold)), name
    if len(cells) == 2 and header_cols == 4:
        trailing = TRAILING_STATE_RE.search(name)
        state = trailing.group(1) if trailing else (STATE_RE.findall(name) or [UNKNOWN])[-1]
        name = TRAILING_STATE_RE.sub("", name) if trailing else name
        return Cells("two-cell", cells[0], cells[1], state, cells[1],
                     first_sentence(cells[0], bold)), name
    return None, f"{len(cells)} cells under a {header_cols}-column header"


def record_for(line_no: int, section: str, cells: list[str], header_cols: int) -> tuple[dict | None, str]:
    """(record, problem): the record of one `| **` row, or None and why it cannot be read."""
    name_match = BOLD_NAME_RE.match(cells[0]) if cells else None
    if not name_match:
        return None, "the first cell has no bold name"
    bold = name_match.group(1)
    columns, name_or_problem = assign(cells, bold, plain(bold), header_cols)
    if columns is None:
        return None, name_or_problem
    whole = " | ".join(cells)
    token, note = read_state(columns.state)
    trailing = TRAILING_STATE_RE.search(name_or_problem)       # "Gate X, WIRED": the state column says it
    if trailing and STATE_FOLD[trailing.group(1).upper()] == token:
        name_or_problem = TRAILING_STATE_RE.sub("", name_or_problem)
    commits = COMMIT_RE.findall(whole if columns.form == "two-cell" else columns.proof)
    return {
        "id": slug(name_or_problem), "name": name_or_problem, "section": section, "line": line_no,
        "what": columns.what, "where": ticks(columns.where), "state": token, "state_note": note,
        "proof": unique([*ticks(columns.proof), *commits]),
        "cards": unique(f"{axis}:{token_}" for axis, token_ in CARD_RE.findall(whole)),
        "rulings": unique(" ".join(r.split()) for r in RULING_RE.findall(whole)),
        "backlog": unique(BACKLOG_RE.findall(whole)),
        "form": columns.form,
        "terms": terms_of(whole),
    }, ""


def terms_of(text: str) -> list[str]:
    """The row's distinct words (3+ letters, no stopwords): the prose a capped `what` leaves out, so
    a term said only deep in a row ("the suck") still finds it. docs_find searches this field last."""
    words = TERM_RE.findall(plain(text).lower())
    return unique(word.strip("'-_") for word in words if word.strip("'-_") not in STOPWORDS)


def row_label(cells: list[str]) -> str:
    match = BOLD_NAME_RE.match(cells[0]) if cells else None
    return plain(match.group(1)) if match else plain(cells[0] if cells else "?")[:60]


def parse(text: str) -> Parsed:
    """Every `| **` row of the doc as one record, a failure, or a flagged record - never dropped."""
    parsed = Parsed()
    section, header_cols = "", 4
    lines = text.split("\n")
    seen: dict[str, int] = {}
    for index, line in enumerate(lines):
        if line.startswith("## "):
            section = plain(line[3:])
            continue
        following = lines[index + 1] if index + 1 < len(lines) else ""
        if line.startswith("|") and SEPARATOR_RE.fullmatch(following.strip()):
            header_cols = len(split_cells(line))
            continue
        if not line.startswith(ROW_PREFIX):
            continue
        cells = split_cells(line)
        record, problem = record_for(index + 1, section, cells, header_cols)
        if record is None:
            parsed.failures.append(f"line {index + 1}: {row_label(cells)} - {problem}")
            continue
        seen[record["id"]] = seen.get(record["id"], 0) + 1
        if seen[record["id"]] > 1:
            record["id"] = f"{record['id']}-{seen[record['id']]}"
        if record["form"] != "four":
            parsed.flagged.append(f"line {index + 1}: {record['name']} - {record['form']} "
                                  f"({len(cells)} cells)")
        parsed.records.append(record)
    return parsed


# --------------------------------------------------------------------------- rendering

def md_line(record: dict) -> str:
    """`- name - STATE - what (CAPABILITIES.md:line)`; docs_find.py --capabilities prints the same."""
    what = f" - {record['what']}" if record["what"] else ""
    return f"- {record['name']} - {record['state']}{what} (CAPABILITIES.md:{record['line']})"


def render_md(parsed: Parsed) -> str:
    tally: dict[str, int] = {}
    for record in parsed.records:
        tally[record["state"]] = tally.get(record["state"], 0) + 1
    states = ", ".join(f"{n} {s}" for s, n in sorted(tally.items(), key=lambda kv: (-kv[1], kv[0])))
    lines = [
        "# Capabilities index - one line per capability",
        "",
        f"Generated from `{CAP_REL}` by `content/video_engine/scripts/build_capabilities_index.py`",
        "`--write`; never edit by hand. Each line: `name - STATE - what (CAPABILITIES.md:line)`; read the",
        "full row with `sed -n <line>p`. Search: `docs_find.py \"<term>\"` (capabilities first); list:",
        "`docs_find.py --capabilities [--state LIVE] [--section <text>]`.",
        "",
        f"**{len(parsed.records)} capabilities: {states}.**",
    ]
    section = None
    for record in parsed.records:
        if record["section"] != section:
            section = record["section"]
            lines += ["", f"## {section}", ""]
        lines.append(md_line(record))
    if parsed.flagged:
        lines += ["", "## Rows the doc should fix", ""]
        lines += [f"- {flag}" for flag in parsed.flagged]
    lines.append("")
    return "\n".join(lines)


def render_jsonl(records: list[dict]) -> str:
    return "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records)


def build(root: Path = REPO) -> Parsed:
    return parse((Path(root) / CAP_REL).read_text(encoding="utf-8"))


def problems_of(parsed: Parsed, strict: bool) -> list[str]:
    """What stops a write: unparsable rows, flagged rows under --strict, an oversized page."""
    problems = [*parsed.failures, *(parsed.flagged if strict else [])]
    size = len(render_md(parsed).encode("utf-8"))
    if size > MD_MAX_BYTES:
        problems.append(f"{MD_REL} is {size} bytes, over MD_MAX_BYTES {MD_MAX_BYTES}")
    return problems


def rendered(parsed: Parsed) -> dict[str, str]:
    return {JSONL_REL: render_jsonl(parsed.records), MD_REL: render_md(parsed)}


def write(root: Path, parsed: Parsed) -> None:
    for rel, text in rendered(parsed).items():
        path = Path(root) / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text.encode("utf-8"))


def first_difference(have: str, want: str) -> str:
    """The first record (or .md line) that differs, named."""
    have_lines, want_lines = have.splitlines(), want.splitlines()
    for index in range(max(len(have_lines), len(want_lines))):
        old = have_lines[index] if index < len(have_lines) else None
        new = want_lines[index] if index < len(want_lines) else None
        if old == new:
            continue
        try:
            record = json.loads(new or old or "{}")
        except json.JSONDecodeError:
            return f"line {index + 1}: {(new or old or '')[:80]}"
        return f"record {index + 1} ({record.get('id')}, CAPABILITIES.md:{record.get('line')})"
    return "trailing bytes"


def check(root: Path, parsed: Parsed) -> list[str]:
    """One entry per stale artifact, naming its first differing record. Empty means in sync."""
    stale = []
    for rel, want in rendered(parsed).items():
        path = Path(root) / rel
        if not path.is_file():
            stale.append(f"{rel} (missing)")
            continue
        have = path.read_bytes().decode("utf-8")
        if have != want:
            stale.append(f"{rel} differs at {first_difference(have, want)}")
    return stale


def use_utf8() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError, OSError):
            pass


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true", help="exit 1 when either artifact is stale (default)")
    ap.add_argument("--write", action="store_true", help="regenerate both artifacts, then re-check")
    ap.add_argument("--strict", action="store_true", help="a flagged (recovered) row is a failure too")
    ap.add_argument("--repo", type=Path, default=REPO, help="repository root (default: this checkout)")
    a = ap.parse_args(argv)
    use_utf8()
    root = a.repo.resolve()
    parsed = build(root)
    for flag in parsed.flagged:
        print(f"build_capabilities_index: FLAGGED {flag}")
    problems = problems_of(parsed, a.strict)
    for problem in problems:
        print(f"build_capabilities_index: FAILURE {problem}")
    summary = f"{len(parsed.records)} records, {len(parsed.flagged)} flagged, {len(parsed.failures)} failed"
    if a.write:
        if problems:
            print(f"build_capabilities_index: FAILED - nothing written ({summary})")
            return 1
        write(root, parsed)
        print(f"build_capabilities_index: wrote {summary} -> {JSONL_REL} + {MD_REL}")
    stale = check(root, parsed)
    if stale:
        print("build_capabilities_index: STALE - " + "; ".join(stale) + " - run --write")
        return 1
    if problems:
        print(f"build_capabilities_index: FAILED ({summary})")
        return 1
    print(f"build_capabilities_index: in sync ({summary})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
