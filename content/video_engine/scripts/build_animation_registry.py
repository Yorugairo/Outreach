"""One registry of every animation formula, dial and kinetics symbol - with a status column.

The operator's ask (2026-09-05): "all of the animation & maths easily searched, referenced, and
understood". The lead-line review that day showed why: the two-thirds power law is IMPLEMENTED as
the curvature stroke and nothing calls it by name; zero-slip anchoring is TRACKED in a backlog row
and unbuilt; the on-1s/on-2s cadence rule is ORPHANED - no code, no gate, no row; the
secondary-motion 0.22 ratio was RETIRED by doc 47 as an invented number.

    docs/ANIMATION-REGISTRY.jsonl   one JSON object per line - the thing you `rg`
    docs/ANIMATION-REGISTRY.md      the same, readable, grouped by module / status

    python content/video_engine/scripts/build_animation_registry.py --write   # regenerate both
    python content/video_engine/scripts/build_animation_registry.py --check   # exit 1 when stale

What is read and how a status is decided is stated once, in `RECIPE` below - it is the header of the
generated Markdown, so the artifact carries its own recipe. Reference forms (`42 s42.1`, `47 s1`)
are parsed and normalised by `build_topic_index`, so the registry cites what the citation graph
cites (`42§42.1`), resolved through `docs/DOCS-INDEX.jsonl` when the index answers.

Standard library only; deterministic (no timestamps, sorted records); written with LF endings.
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_topic_index as BTI  # noqa: E402  (reference forms + resolution are defined once, there)

JSONL_REL = "docs/ANIMATION-REGISTRY.jsonl"
MD_REL = "docs/ANIMATION-REGISTRY.md"
INDEX_REL = "docs/DOCS-INDEX.jsonl"
CITATIONS_REL = "docs/DOCS-CITATIONS.jsonl"
KINETICS_DIR = "content/video_engine/scripts/kinetics"
TEMPLATE_REL = "docs/content-video-engine/samples/scene-evidence-player.template.html"
TESTS_DIR = "content/video_engine/tests"
DOCS_DIR = "docs/content-video-engine"
SOURCES_DIR = "content/video_engine/sources/reference_analyses"
ROW_FILES = (f"{DOCS_DIR}/BACKLOG.md", f"{DOCS_DIR}/47-FINDINGS-TO-CHECKS.md")
EXTRA_DOCS = (f"{DOCS_DIR}/FINDING-the-animation-math-and-what-it-changes.md",
              f"{DOCS_DIR}/briefs/ANSWERS-RESEARCH-BRIEF-animation-craft.md")
DOC_NUMBERS = (29, *range(42, 54))
SOURCE_NAME = re.compile(r"animation|drawing|kinetic|academic_literature", re.I)

TEMPLATE_DIAL_OBJECTS = ("MARK", "SP", "LP")
TEMPLATE_DIAL_SCALARS = ("MOUNT_STEPS", "DISSOLVE_S", "LP_MOUNT_RISE", "CAP_LAST_HOLD_S")

EXPR_MAX = 200           # the spec's cap on a formula's text
SIG_MAX = 200            # the same cap on a signature, so a one-line object cannot flood the md
VALUE_MAX = 120
NAME_MAX = 120
EVIDENCE_MAX = 6         # evidence entries kept per record, sorted
CONTEXT_COMMENTS = 8     # comment lines read around a declaration for its citations

KIND_ORDER = {"code": 0, "dial": 1, "formula": 2}
STATUS_ORDER = ("implemented", "tracked", "retired", "orphaned")

# --- patterns -----------------------------------------------------------------------------

EXPORT = re.compile(r"^export\s+(?:const|function)\s+([A-Za-z_$][\w$]*)")
CONST_ANY = re.compile(r"^\s*(?:export\s+)?(?:const|let|var|function)\s")
FLAG_MENTION = re.compile(r"kinetics\.([a-z][a-z0-9_]*)")
KIN_BEGIN = re.compile(r"KINETICS:BEGIN\s+(\w+)")
KIN_END = re.compile(r"KINETICS:END")
DEFAULTS_BLOCK = re.compile(r"KINETICS_DEFAULTS\s*=\s*Object\.freeze\(\{(.*?)\}\)", re.S)
DEFAULT_KEY = re.compile(r"^\s*([a-z][a-z0-9_]*)\s*:", re.M)
OBJECT_KEY = re.compile(r"([A-Za-z_$][\w$]*)\s*:")
CONST_OBJECT = re.compile(r"=\s*(?:Object\.freeze\(\s*)?\{")
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
FENCE = re.compile(r"^\s*(?:```|~~~)")
TABLE_SEP = re.compile(r"^\s*\|?\s*:?-{3,}")
COMMENT_LINE = re.compile(r"^\s*(?:/\*|\*|//|\*/)")

# `=` plus one of these makes a line a formula: the Greek block, subscripts, and the operators the
# docs use. The spec's set, unextended - a minus-only line ("v_contact - v_surface = 0") is caught
# by the law rule instead.
MATH_SYMBOL = re.compile(r"[Ͱ-Ͽ₀-₟]|\^|√|∝|\bcoth\b|\bexp\(")
# a hyphen/slash compound is the distinctive part of a name: "two-thirds", "zero-slip", "FK/IK"
COMPOUND = re.compile(r"[A-Za-z][A-Za-z0-9]*(?:[-/][A-Za-z0-9]+)+")
# the one reference form the citation graph does not carry: a FINDING doc has no document number
FINDING_REF = re.compile(r"(?<![\w-])(FINDING-[A-Za-z][A-Za-z0-9-]*?)\s+s(\d+(?:\.\d+)*[a-z]?)(?![\w.])")
RETIRED_WORD = re.compile(r"\breclassified\b|\bwithdrawn\b|\bclosed\b(?![-\w])|\binvented\b", re.I)

# The laws the registry knows by name. Order is the naming order: the first that matches a line names
# the record. `zero-slip` and `FK/IK` are added to the spec's list because doc 48 states them as
# rules and backlog G-j tracks one of them - without them those rows have nothing to attach to.
LAWS = (
    ("two-thirds power law", ("two-thirds", "power law")),
    ("minimum-jerk", ("minimum-jerk", "min-jerk", "minJerk")),
    ("Kubelka-Munk", ("Kubelka",)),
    ("Deegan (coffee-ring)", ("Deegan",)),
    ("Euler spiral / clothoid", ("Euler spiral", "clothoid")),
    ("ARAP / polar decomposition", ("ARAP", "polar decomposition")),
    ("Flash & Hogan", ("Flash & Hogan", "Flash and Hogan")),
    ("Viviani", ("Viviani",)),
    ("Fitts", ("Fitts",)),
    ("On-1s / On-2s", ("On-1s", "On-2s", "On-3s")),
    ("zero-slip", ("zero-slip",)),
    ("FK/IK", ("FK/IK",)),
)
LAW_RE = tuple((name, re.compile("|".join(re.escape(a) for a in aliases), re.I), aliases)
               for name, aliases in LAWS)
LAW_ALIASES = {name: aliases for name, aliases in LAWS}


# --- text helpers -------------------------------------------------------------------------

CONTROL = {c: " " for c in range(32) if c not in (9, 10, 13)}


def truncate(text: str, limit: int) -> str:
    """One line, whitespace collapsed, at most `limit` characters.

    C0 control characters become spaces first: two of the bundled research files were written
    through non-raw Python strings, so `\\rho` and `\\beta` are a CR and a BACKSPACE on disk."""
    text = " ".join(str(text).translate(CONTROL).split())
    return text if len(text) <= limit else text[:limit].rstrip()


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


def read_text(root: Path, rel: str) -> str:
    path = Path(root) / rel
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def read_jsonl(root: Path, rel: str) -> list[dict]:
    return [json.loads(line) for line in read_text(root, rel).splitlines() if line.strip()]


def rel_of(root: Path, path: Path) -> str:
    return path.resolve().relative_to(Path(root).resolve()).as_posix()


def law_name(text: str) -> tuple[str, tuple[str, ...]] | None:
    """The first law named in `text`, with the aliases it is searched by."""
    for name, pattern, aliases in LAW_RE:
        if pattern.search(text):
            return name, aliases
    return None


def name_tokens(name: str) -> tuple[str, ...]:
    """What a row or a module must contain to count as naming this record.

    A law is searched by its aliases; anything else by the hyphen/slash compounds of its name
    ("Secondary-Motion" out of a heading), and failing that by the whole name - deliberately strict,
    so a common word in a heading cannot manufacture a status."""
    if name in LAW_ALIASES:
        return LAW_ALIASES[name]
    compounds = tuple(dict.fromkeys(COMPOUND.findall(name)))
    return compounds or (name,)


def mentions(text: str, tokens: tuple[str, ...]) -> bool:
    low = text.casefold()
    return any(token.casefold() in low for token in tokens)


def word_re(name: str) -> re.Pattern:
    return re.compile(r"(?<![\w$.])" + re.escape(name) + r"(?![\w$])")


# --- the corpus ---------------------------------------------------------------------------

class Corpus:
    """Every file the registry reads, loaded once, addressed by repo-relative path."""

    def __init__(self, root: Path) -> None:
        self.root = Path(root)
        self.index = read_jsonl(self.root, INDEX_REL)
        self.citations = read_jsonl(self.root, CITATIONS_REL)
        self.resolver = BTI.Resolver(self.index)
        self.headings = heading_map(self.index)
        self.modules = {rel_of(self.root, p): p.read_text(encoding="utf-8")
                        for p in sorted((self.root / KINETICS_DIR).glob("*.mjs"))}
        self.template_rel = TEMPLATE_REL
        self.template = read_text(self.root, TEMPLATE_REL)
        self.template_lines = split_lines(self.template)
        self.inlined = inlined_spans(self.template_lines)
        self.flags = default_flags(self.template)
        self.declared = declared_flag_lines(self.template_lines, self.flags, self.inlined)
        self.tests = {rel_of(self.root, p): p.read_text(encoding="utf-8", errors="replace")
                      for p in sorted((self.root / TESTS_DIR).rglob("*"))
                      if p.is_file() and p.suffix in (".py", ".mjs", ".js")
                      and "__pycache__" not in p.parts}
        self.rows = table_rows(self.root)

    def enclosing(self, rel: str, line: int) -> dict | None:
        """The heading a line sits under, from the docs index; from the file when it is unindexed."""
        recs = self.headings.get(rel) or file_headings(self.root, rel)
        found = None
        for rec in recs:
            if rec["line"] <= line:
                found = rec
            else:
                break
        return found

    def refs(self, text: str) -> list[dict]:
        """Normalised citation refs in `text`, resolved to path:line when the index answers."""
        out: list[dict] = []
        for match in BTI.REFERENCE.finditer(text):
            for ref, to in self.resolver.edge(match):
                add_cite(out, ref, f"{to['path']}:{to['line']}" if to else None)
        for match in FINDING_REF.finditer(text):
            slug, token = match.group(1), match.group(2)
            add_cite(out, f"{slug}§{token}", self.finding_section(slug, token))
        return out

    def finding_section(self, slug: str, token: str) -> str | None:
        """`FINDING-the-animation-math s1` -> that file's section 1. The docs' numbered findings head
        their sections `1.`, and the citation graph's matcher rejects a trailing dot, so the section
        is matched here: the token, then anything but a digit."""
        pattern = re.compile(r"^\s*" + re.escape(token) + r"(?:(?![\w.])|\.(?!\d))")
        hits = [r for r in self.index
                if r["path"].rsplit("/", 1)[-1].startswith(slug) and pattern.match(r["heading"])]
        best = min(hits, key=lambda r: (r["path"].count("/"), r["path"], r["line"]), default=None)
        return f"{best['path']}:{best['line']}" if best else None


def add_cite(out: list[dict], ref: str, to: str | None) -> None:
    cite = {"ref": ref, "to": to}
    if cite not in out:
        out.append(cite)


def heading_map(index: list[dict]) -> dict[str, list[dict]]:
    """path -> its heading records (levels 1-6) in line order; a table row encloses nothing."""
    out: dict[str, list[dict]] = {}
    for rec in index:
        if rec.get("level", 7) <= 6:
            out.setdefault(rec["path"], []).append(rec)
    for recs in out.values():
        recs.sort(key=lambda r: r["line"])
    return out


def default_flags(template: str) -> tuple[str, ...]:
    """The KINETICS_DEFAULTS keys - the only names a `kinetics.<flag>` may resolve to."""
    match = DEFAULTS_BLOCK.search(template)
    return tuple(DEFAULT_KEY.findall(match.group(1))) if match else ()


def declared_flag_lines(lines: list[str], flags: tuple[str, ...],
                        inlined: list[tuple[int, int]]) -> set[int]:
    """Template line indexes that only DECLARE a kinetics flag nothing reads.

    `arap_morph: false,   // 43.5B polar-decomposition morph` names a law in a comment beside a flag
    the player never passes to `kin()`. That line is a placeholder, not an implementation, and
    counting it would mark an unbuilt finding implemented."""
    live = {f for f in flags if any(f'kin("{f}")' in line
                                    for i, line in enumerate(lines) if not in_spans(i, inlined))}
    return {i for i, line in enumerate(lines)
            for key in DEFAULT_KEY.findall(line) if key in flags and key not in live}


def file_headings(root: Path, rel: str) -> list[dict]:
    """Heading records straight from a file - the fallback when the docs index does not carry it."""
    out = []
    for i, line in unfenced(split_lines(read_text(root, rel))):
        match = HEADING.match(line)
        if match:
            out.append({"path": rel, "line": i + 1, "level": len(match.group(1)),
                        "heading": truncate(match.group(2), NAME_MAX)})
    return out


def inlined_spans(lines: list[str]) -> list[tuple[int, int]]:
    """[start, end] line indexes of the template's KINETICS:BEGIN..END regions - `sync_kinetics.py`'s
    copies of the modules. A use inside them is the module using itself, not the player calling it."""
    spans, start = [], None
    for i, line in enumerate(lines):
        if start is None and KIN_BEGIN.search(line):
            start = i
        elif start is not None and KIN_END.search(line):
            spans.append((start, i))
            start = None
    if start is not None:
        spans.append((start, len(lines) - 1))
    return spans


def in_spans(index: int, spans: list[tuple[int, int]]) -> bool:
    return any(lo <= index <= hi for lo, hi in spans)


def table_rows(root: Path) -> list[tuple[str, int, str]]:
    """(path, line, text) for every Markdown table row of BACKLOG.md and 47-FINDINGS-TO-CHECKS.md.

    The docs index carries level-7 rows for BACKLOG only - 47 is not one of its row files - so both
    are parsed here the same way, from the source, and the two sets agree on BACKLOG."""
    out = []
    for rel in ROW_FILES:
        for i, line in unfenced(split_lines(read_text(root, rel))):
            if line.lstrip().startswith("|") and not TABLE_SEP.match(line):
                out.append((rel, i + 1, line))
    return out


# --- javascript object literals -------------------------------------------------------------

def skip_string(text: str, i: int) -> int:
    quote, i = text[i], i + 1
    while i < len(text):
        if text[i] == "\\":
            i += 2
            continue
        if text[i] == quote:
            return i + 1
        i += 1
    return i


def object_span(text: str, start: int) -> tuple[int, int] | None:
    """(open, close) indexes of the first `{...}` at or after `start`, braces balanced."""
    open_at = text.find("{", start)
    if open_at < 0:
        return None
    depth, i = 0, open_at
    while i < len(text):
        if text[i] in "\"'`":
            i = skip_string(text, i)
            continue
        if text.startswith("/*", i):
            end = text.find("*/", i + 2)
            i = len(text) if end < 0 else end + 2
            continue
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return open_at, i
        i += 1
    return None


def scan_to(text: str, start: int, close_at: int, stop: str) -> int:
    """Walk from `start` to `close_at`, skipping strings, block comments and nested brackets; stop
    on a `stop` character at bracket depth 0."""
    i, depth = start, 0
    while i < close_at:
        ch = text[i]
        if ch in "\"'`":
            i = skip_string(text, i)
        elif text.startswith("/*", i):
            end = text.find("*/", i + 2)
            i = close_at if end < 0 else end + 2
        elif ch in "{[(":
            depth, i = depth + 1, i + 1
        elif ch in "}])":
            depth, i = depth - 1, i + 1
        elif depth == 0 and ch in stop:
            break
        else:
            i += 1
    return i


def object_entries(text: str, open_at: int, close_at: int) -> list[tuple[str, str, int]]:
    """(key, value, offset) for every top-level `key: value` of one object literal."""
    entries, i = [], open_at + 1
    while i < close_at:
        if text[i].isspace() or text[i] == ",":
            i += 1
            continue
        if text.startswith("/*", i):                    # a note between two keys, not a value
            end = text.find("*/", i + 2)
            i = close_at if end < 0 else end + 2
            continue
        match = OBJECT_KEY.match(text, i)
        if not match:
            i = scan_to(text, i, close_at, ",")
            continue
        end = scan_to(text, match.end(), close_at, ",")
        entries.append((match.group(1), truncate(text[match.end():end], VALUE_MAX), i))
        i = end
    return entries


def constant_object(text: str, start: int) -> tuple[int, int] | None:
    """The span of a declared constant object - `= { ... }` or `= Object.freeze({ ... })`, and
    nothing else: `scaleBy = (s, a) => ({ sx, sy })` returns an object, it does not declare dials."""
    equals = text.find("=", start)
    span = object_span(text, start)
    if equals < 0 or span is None or not CONST_OBJECT.match(text, equals):
        return None
    return span


def line_of(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def offset_of(lines: list[str], index: int) -> int:
    return sum(len(line) + 1 for line in lines[:index])


# --- code records -------------------------------------------------------------------------

def header_comment(text: str) -> str:
    """The module's leading `/* ... */` block - where a module states its doc sections and its flag."""
    if not text.lstrip().startswith("/*"):
        return ""
    end = text.find("*/")
    return text[:end] if end > 0 else text


def header_lines(text: str) -> int:
    """How many lines the module's leading comment block occupies."""
    head = header_comment(text)
    return len(split_lines(head)) if head else 0


def flag_for(text: str, corpus: Corpus) -> str | None:
    """The `kinetics.<flag>` a comment names, when it is a real KINETICS_DEFAULTS key."""
    for flag in FLAG_MENTION.findall(text):
        if not corpus.flags or flag in corpus.flags:
            return flag
    return None


def comment_context(lines: list[str], index: int) -> str:
    """The contiguous comment block above a declaration, plus the comment lines right below it."""
    out, i = [], index - 1
    while i >= 0 and len(out) < CONTEXT_COMMENTS and COMMENT_LINE.match(lines[i]):
        out.append(lines[i])
        i -= 1
    j = index + 1
    while j < len(lines) and len(out) < 2 * CONTEXT_COMMENTS and COMMENT_LINE.match(lines[j]):
        out.append(lines[j])
        j += 1
    return "\n".join(out)


def code_records(corpus: Corpus) -> list[dict]:
    """One record per exported symbol of every kinetics module, plus one per exported object key."""
    out: list[dict] = []
    for rel, text in corpus.modules.items():
        lines = split_lines(text)
        head = header_comment(text)
        cites, module_flag = corpus.refs(head), flag_for(head, corpus)
        for i, line in enumerate(lines):
            match = EXPORT.match(line)
            if not match:
                continue
            name = match.group(1)
            flag = flag_for(comment_context(lines, i) + "\n" + line, corpus) or module_flag
            out.append(code_record(corpus, name, rel, i + 1, truncate(line, SIG_MAX), flag, cites))
            out += key_records(corpus, name, rel, text, lines, i, flag, cites)
    return out


def key_records(corpus: Corpus, owner: str, rel: str, text: str, lines: list[str], index: int,
                flag: str | None, cites: list[dict]) -> list[dict]:
    """A record per key of an exported constant object: `INK.S1`, `SPRING.MP`, `SOAK_STEP.FPS`."""
    span = constant_object(text, offset_of(lines, index))
    if span is None or line_of(text, span[0]) > index + 2:
        return []
    out = []
    for key, value, offset in object_entries(text, *span):
        name = f"{owner}.{key}"
        out.append(code_record(corpus, name, rel, line_of(text, offset),
                               truncate(f"{name} = {value}", SIG_MAX), flag, cites, usage=key))
    return out


def code_record(corpus: Corpus, name: str, rel: str, line: int, signature: str,
                flag: str | None, cites: list[dict], usage: str | None = None) -> dict:
    """A key is used through its object (`P.COVERAGE`), so a key record is searched by its bare key."""
    sites = template_sites(corpus, usage or name, flag)
    return {"kind": "code", "name": name, "module": rel, "line": line, "signature": signature,
            "flag": flag, "template_sites": len(sites), "tests": test_files(corpus, usage or name),
            "cites": cites, "_sites": sites, "_usage": usage or name}


def template_sites(corpus: Corpus, name: str, flag: str | None) -> list[int]:
    """Template lines (1-based) reading `kin("<flag>")` or using the name outside its declaration,
    the inlined KINETICS regions excluded."""
    word, kin = word_re(name), (f'kin("{flag}")' if flag else None)
    out = []
    for i, line in enumerate(corpus.template_lines):
        if in_spans(i, corpus.inlined):
            continue
        if (kin and kin in line) or (word.search(line) and not CONST_ANY.match(line)):
            out.append(i + 1)
    return out


def test_files(corpus: Corpus, name: str) -> list[str]:
    word = word_re(name)
    return [rel for rel, text in corpus.tests.items() if word.search(text)]


# --- dial records -------------------------------------------------------------------------

def dial_records(corpus: Corpus) -> list[dict]:
    """The tunable constants: kinetics constant objects, and the template's dial objects/scalars."""
    out: list[dict] = []
    for rel, text in corpus.modules.items():
        lines = split_lines(text)
        for i, line in enumerate(lines):
            match = EXPORT.match(line)
            if match:
                out += object_dials(corpus, match.group(1), rel, text, lines, i)
    out += template_dials(corpus)
    return out


def object_dials(corpus: Corpus, owner: str, rel: str, text: str, lines: list[str],
                 index: int) -> list[dict]:
    span = constant_object(text, offset_of(lines, index))
    if span is None or line_of(text, span[0]) > index + 2:
        return []
    # the dial's own note first, then the module's header: a dial is cited by the note beside it
    # ("the dials - 42 s42.5") AND by the section the module implements
    cites = corpus.refs(comment_context(lines, index) + "\n" + lines[index])
    for cite in corpus.refs(header_comment(text)):
        if cite not in cites:
            cites.append(cite)
    return [{"kind": "dial", "name": f"{owner}.{key}", "value": value, "path": rel,
             "line": line_of(text, offset), "cites": cites}
            for key, value, offset in object_entries(text, *span)]


def template_dials(corpus: Corpus) -> list[dict]:
    """MARK / SP / LP and the four named scalars, skipping the inlined kinetics copies."""
    out, text, lines = [], corpus.template, corpus.template_lines
    for i, line in enumerate(lines):
        if in_spans(i, corpus.inlined) or not CONST_ANY.match(line):
            continue
        for owner in TEMPLATE_DIAL_OBJECTS:
            if re.match(r"\s*(?:const|let|var)\s+" + owner + r"\s*=", line):
                out += object_dials(corpus, owner, corpus.template_rel, text, lines, i)
        for name in TEMPLATE_DIAL_SCALARS:
            match = re.search(r"(?<![\w$.])" + name + r"\s*=\s*([^,;\n]+)", line)
            if match and not any(d["name"] == name for d in out):
                out.append({"kind": "dial", "name": name,
                            "value": truncate(match.group(1), VALUE_MAX),
                            "path": corpus.template_rel, "line": i + 1,
                            "cites": corpus.refs(comment_context(lines, i) + "\n" + line)})
    return out


# --- formula records ----------------------------------------------------------------------

def formula_files(root: Path) -> list[str]:
    """The doc set, sorted: 29 and 42-53, the animation-math finding, the craft brief, and every
    reference_analyses file whose NAME carries ANIMATION / DRAWING / KINETIC / academic_literature."""
    out: list[str] = []
    docs = Path(root) / DOCS_DIR
    for number in DOC_NUMBERS:
        out += [rel_of(root, p) for p in sorted(docs.glob(f"{number}-*.md"))]
    out += [rel for rel in EXTRA_DOCS if (Path(root) / rel).is_file()]
    sources = Path(root) / SOURCES_DIR
    if sources.is_dir():
        out += sorted(rel_of(root, p) for p in sources.rglob("*.md") if SOURCE_NAME.search(p.name))
    return list(dict.fromkeys(out))


def formula_records(corpus: Corpus) -> list[dict]:
    out: list[dict] = []
    for rel in formula_files(corpus.root):
        out += file_formulas(corpus, rel, read_text(corpus.root, rel))
    return out


def file_formulas(corpus: Corpus, rel: str, text: str) -> list[dict]:
    """Display-math blocks, symbol-bearing `=` lines, and law-naming lines - one record each."""
    out, block, block_at = [], None, 0
    for i, line in unfenced(split_lines(text)):
        if block is not None:
            block.append(line)
            if "$$" in line:
                out.append(formula(corpus, rel, block_at + 1, " ".join(block)))
                block = None
            continue
        count = line.count("$$")
        if count == 1:
            block, block_at = [line], i
        elif count >= 2 or ("=" in line and MATH_SYMBOL.search(line)) or law_name(line):
            out.append(formula(corpus, rel, i + 1, line))
    if block is not None:                       # an unterminated `$$` is still evidence of a formula
        out.append(formula(corpus, rel, block_at + 1, " ".join(block)))
    return out


def formula(corpus: Corpus, rel: str, line: int, expr: str) -> dict:
    section = corpus.enclosing(rel, line)
    heading = section["heading"] if section else ""
    expr = strip_markdown(expr.replace("$$", ""))
    named = law_name(expr) or law_name(heading)
    name = named[0] if named else truncate(strip_markdown(heading) or expr, NAME_MAX)
    return {"kind": "formula", "name": name, "expr": truncate(expr, EXPR_MAX), "path": rel,
            "line": line, "section": truncate(heading, NAME_MAX) or None,
            "doc": doc_of(rel, section),
            "_anchor": f"{rel}:{section['line']}" if section else None}


def strip_markdown(text: str) -> str:
    return truncate(text.replace("**", "").replace("~~", "").strip("| "), EXPR_MAX)


def doc_of(rel: str, section: dict | None) -> str | None:
    if section and section.get("doc"):
        return section["doc"]
    match = re.match(r"(\d{1,3})-", rel.rsplit("/", 1)[-1])
    return match.group(1) if match else None


# --- status -------------------------------------------------------------------------------

def apply_status(records: list[dict], corpus: Corpus) -> None:
    """`status` + `status_evidence` on every code and formula record.

    Precedence is implemented > retired > tracked > orphaned: code that exists is implemented
    whatever a row says, and a row calling something invented outranks a row that merely names it."""
    code = [r for r in records if r["kind"] == "code"]
    for rec in code:
        set_status(rec, *code_status(rec, corpus))
    for rec in (r for r in records if r["kind"] == "formula"):
        set_status(rec, *formula_status(rec, corpus, code))


def set_status(rec: dict, status: str, evidence: list[str]) -> None:
    rec["status"] = status
    rec["status_evidence"] = sorted(dict.fromkeys(evidence))[:EVIDENCE_MAX]


def code_status(rec: dict, corpus: Corpus) -> tuple[str, list[str]]:
    """Implemented when the player calls it, a test names it, or another kinetics line uses it."""
    sites, usage = rec.pop("_sites"), rec.pop("_usage")
    evidence = [f"{corpus.template_rel}:{n}" for n in sites[:3]]
    evidence += [f"{rel}:{first_line(corpus.tests[rel], usage)}" for rel in rec["tests"]]
    evidence += module_uses(corpus, usage, rec["module"], rec["line"])
    if evidence:
        return "implemented", evidence
    return row_status(corpus, (rec["name"], usage))


def module_uses(corpus: Corpus, name: str, own_module: str, own_line: int) -> list[str]:
    """Kinetics lines that USE the name: not its own declaration, not a comment, and not a module
    header - a header that explains a symbol is prose, not a call site."""
    word, out = word_re(name), []
    for rel, text in corpus.modules.items():
        head = header_lines(text)
        for i, line in enumerate(split_lines(text)):
            if i < head or (rel == own_module and i + 1 == own_line):
                continue
            if word.search(line) and not COMMENT_LINE.match(line):
                out.append(f"{rel}:{i + 1}")
    return out[:3]


def formula_status(rec: dict, corpus: Corpus, code: list[dict]) -> tuple[str, list[str]]:
    anchor, tokens = rec.pop("_anchor"), name_tokens(rec["name"])
    evidence = [f"{c['module']}:{c['line']}" for c in code
                if anchor and any(cite["to"] == anchor for cite in c["cites"])]
    evidence += token_hits(corpus, tokens)
    if evidence:
        return "implemented", evidence
    status, row_evidence = row_status(corpus, tokens, own=(rec["path"], rec["line"]))
    cited = [f"{e['from']['path']}:{e['from']['line']}" for e in corpus.citations
             if anchor and e["from"]["path"] in ROW_FILES and e.get("to")
             and f"{e['to']['path']}:{e['to']['line']}" == anchor]
    if status == "orphaned" and cited:
        return "tracked", cited
    return status, row_evidence + (cited if status == "tracked" else [])


def row_status(corpus: Corpus, tokens: tuple[str, ...],
               own: tuple[str, int] | None = None) -> tuple[str, list[str]]:
    """What the BACKLOG and doc-47 rows naming these tokens say: retired, tracked, or nothing.

    A formula that IS such a row is its own row: doc 47's DESIGNED-OUT table states the formula and
    tracks it in the same line, and no token match can see that."""
    rows = [row for row in corpus.rows
            if mentions(row[2], tokens) or (own and (row[0], row[1]) == own)]
    retired = [row for row in rows if RETIRED_WORD.search(row[2])]
    if retired:
        return "retired", [f"{p}:{n}" for p, n, _ in retired]
    if rows:
        return "tracked", [f"{p}:{n}" for p, n, _ in rows]
    return "orphaned", []


def token_hits(corpus: Corpus, tokens: tuple[str, ...]) -> list[str]:
    """Kinetics and template lines naming the formula - the modules first, so the module that
    implements a law is the evidence and the template's inlined copy of it is not."""
    out = []
    for rel, text in list(corpus.modules.items()) + [(corpus.template_rel, corpus.template)]:
        for i, line in enumerate(split_lines(text)):
            if mentions(line, tokens) and not (rel == corpus.template_rel and i in corpus.declared):
                out.append(f"{rel}:{i + 1}")
    return out[:3]


def first_line(text: str, name: str) -> int:
    word = word_re(name)
    for i, line in enumerate(split_lines(text)):
        if word.search(line):
            return i + 1
    return 1


# --- build / render -----------------------------------------------------------------------

def build(repo_root: Path = REPO) -> list[dict]:
    """Every record, sorted by (kind, name, path, line). The one entry point for callers."""
    corpus = Corpus(Path(repo_root))
    records = code_records(corpus) + dial_records(corpus) + formula_records(corpus)
    apply_status(records, corpus)
    return sorted(records, key=sort_key)


def location(rec: dict) -> str:
    return rec.get("path") or rec.get("module") or ""


def sort_key(rec: dict) -> tuple:
    return (KIND_ORDER[rec["kind"]], rec["name"].casefold(), rec["name"],
            location(rec), rec.get("line", 0))


def render_jsonl(records: list[dict]) -> str:
    return "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records)


def cite_text(cites: list[dict]) -> str:
    return ", ".join(c["ref"] + (f" -> {c['to']}" if c["to"] else "") for c in cites)


def evidence_md(rec: dict) -> str:
    return " — " + ", ".join(rec["status_evidence"]) if rec["status_evidence"] else " — (no evidence)"


def code_md(records: list[dict]) -> list[str]:
    out = ["## Code (kinetics)", ""]
    code = [r for r in records if r["kind"] == "code"]
    for module in sorted({r["module"] for r in code}):
        out += [f"### `{module}`", ""]
        for rec in [r for r in code if r["module"] == module]:
            flag = f"flag `{rec['flag']}`" if rec["flag"] else "no flag"
            facts = f"{flag} · {rec['template_sites']} template site(s) · {len(rec['tests'])} test(s)"
            out.append(f"- **{rec['name']}** — `{rec['signature']}` — {rec['module']}:{rec['line']}"
                       f" — {facts} — {rec['status']}{evidence_md(rec)}")
        out.append("")
    return out


def dial_md(records: list[dict]) -> list[str]:
    out = ["## Dials", ""]
    dials = [r for r in records if r["kind"] == "dial"]
    for path in sorted({r["path"] for r in dials}):
        out += [f"### `{path}`", ""]
        for rec in [r for r in dials if r["path"] == path]:
            cites = f" — {cite_text(rec['cites'])}" if rec["cites"] else ""
            out.append(f"- **{rec['name']}** — `{rec['value']}` — {rec['path']}:{rec['line']}{cites}")
        out.append("")
    return out


def formula_line(rec: dict) -> str:
    return f"- **{rec['name']}** — {rec['expr']} — {rec['path']}:{rec['line']}{evidence_md(rec)}"


def formula_md(records: list[dict]) -> list[str]:
    formulas = [r for r in records if r["kind"] == "formula"]
    out = ["## Formulas and laws", ""]
    for status in STATUS_ORDER:
        rows = [r for r in formulas if r["status"] == status]
        out += [f"### {status} ({len(rows)})", ""] + [formula_line(r) for r in rows] + [""]
    orphans = [r for r in formulas if r["status"] == "orphaned"]
    out += [f"## Orphaned ({len(orphans)})", "",
            "Stated in the docs, implemented nowhere, tracked by no BACKLOG or doc-47 row, retired by",
            "nobody. This is the list to triage. Note that",
            "`content/video_engine/sources/reference_analyses/complete_research_evidence_bundle/`",
            "holds byte-identical copies of three of the scanned research files, so a research orphan",
            "usually appears twice, once per path.", ""]
    return out + [formula_line(r) for r in orphans] + [""]


RECIPE = """# Animation registry — every formula, dial and kinetics symbol, with its status

Generated by `python content/video_engine/scripts/build_animation_registry.py --write`. Never
hand-edited: the recipe below is the whole of it, and `--check` fails when this file drifts from it.

**{code} code · {dial} dial · {formula} formula records — {status}.**

**Read** — code: `content/video_engine/scripts/kinetics/*.mjs` (every `export const|function`, plus
every key of an exported constant object). Dials: those same constant objects, and the player
template's `MARK` / `SP` / `LP` / `MOUNT_STEPS` / `DISSOLVE_S` / `LP_MOUNT_RISE` / `CAP_LAST_HOLD_S`.
Formulas: `docs/content-video-engine/{{29,42..53}}-*.md`, `FINDING-the-animation-math-*.md`,
`briefs/ANSWERS-RESEARCH-BRIEF-animation-craft.md`, and the `reference_analyses` files named
ANIMATION / DRAWING / KINETIC / academic_literature — every `$$` block, every `=` line carrying a
mathematical symbol, every line naming a law.

**Status** — precedence implemented > retired > tracked > orphaned.
*implemented*: a kinetics module cites the formula's section, or the name is written in a module or
the template (code: the player calls it, a test names it, or another kinetics line uses it).
*retired*: a BACKLOG or doc-47 row naming it says reclassified / withdrawn / closed / invented
(`closed-form` is not `closed`). *tracked*: such a row names it, or cites its section in
`docs/DOCS-CITATIONS.jsonl`. *orphaned*: none of those — stated and unattached.

**Named heuristics** — the template's `KINETICS:BEGIN..END` regions are `sync_kinetics.py`'s copies
of the modules, so uses inside them are not template use sites; a law is matched by its aliases and
anything else by the hyphen/slash compounds of its name (`Secondary-Motion`, `zero-slip`), never by
a common word; `zero-slip` and `FK/IK` were added to the law list because doc 48 states them as
rules; a kinetics constant key appears twice on purpose — as code surface (flag, sites, tests) and
as a dial (with its value).
"""


def render_md(records: list[dict]) -> str:
    counts = {kind: sum(1 for r in records if r["kind"] == kind) for kind in KIND_ORDER}
    status = ", ".join(f"{sum(1 for r in records if r.get('status') == s)} {s}"
                       for s in STATUS_ORDER)
    head = RECIPE.format(status=status, **counts)
    return "\n".join([head] + code_md(records) + dial_md(records) + formula_md(records)) + "\n"


def rendered(root: Path = REPO) -> dict[str, str]:
    records = build(root)
    return {JSONL_REL: render_jsonl(records), MD_REL: render_md(records)}


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


def summary(records: list[dict]) -> str:
    kinds = ", ".join(f"{sum(1 for r in records if r['kind'] == k)} {k}" for k in KIND_ORDER)
    status = ", ".join(f"{sum(1 for r in records if r.get('status') == s)} {s}"
                       for s in STATUS_ORDER)
    return f"{len(records)} records ({kinds}; {status})"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true",
                    help="exit 1 when either artifact is stale (default)")
    ap.add_argument("--write", action="store_true", help="regenerate both artifacts")
    ap.add_argument("--repo", type=Path, default=REPO, help="repository root (default: this checkout)")
    a = ap.parse_args(argv)
    root = a.repo.resolve()
    if a.write:
        print(f"build_animation_registry: {summary(write(root))} -> {JSONL_REL} + {MD_REL}")
    problems = check(root)
    if problems:
        print("build_animation_registry: STALE - " + "; ".join(problems) + " - run --write")
        return 1
    print(f"build_animation_registry: in sync ({summary(build(root))})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
