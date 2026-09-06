"""One registry of every animation formula, dial and kinetics symbol - with a status column.

The operator's ask (2026-09-05): "all of the animation & maths easily searched, referenced, and
understood". The lead-line review that day showed why: the two-thirds power law is IMPLEMENTED as
the curvature stroke and nothing calls it by name; zero-slip anchoring is TRACKED in a backlog row
and unbuilt; the on-1s/on-2s cadence rule was ORPHANED - no code, no gate, no row - until the
triage opened one for it; the secondary-motion 0.22 ratio was RETIRED by doc 47 as invented.

    docs/ANIMATION-REGISTRY.jsonl   one JSON object per line - the thing you `rg`
    docs/ANIMATION-REGISTRY.md      the same, readable, grouped by module / status

    python content/video_engine/scripts/build_animation_registry.py --write   # regenerate both
    python content/video_engine/scripts/build_animation_registry.py --check   # exit 1 when stale

This module owns the code side - the kinetics modules, the dials, the formula records, the status
precedence and the build. The prose side it reads them against - markdown structure, the research
layer, the citation chain and the ledger verdicts - is `animation_registry_chain.py`, imported back
whole so every public name of the registry stays importable from here.

What is read and how a status is decided is stated once, in `RECIPE` (now in
`animation_registry_render.py`) - it is the header of the generated Markdown, so the artifact
carries its own recipe. Reference forms (`42 s42.1`, `47 s1`) are parsed and normalised by
`build_topic_index`, so the registry cites what the citation graph cites (`42§42.1`), resolved
through `docs/DOCS-INDEX.jsonl` when the index answers.

Two systematic misreads were corrected on 2026-09-05 (`docs/content-video-engine/TRIAGE-2026-09-05.md`
§1b and "Registry misreads corrected"):

  * a shipped law read as an orphan on the research side, because a module cites OUR numbered doc
    section and never the research file the section was extracted from. `chain_hits` walks
    `code → our section → research section` and hands the research section the module's status.
  * "Closed Kinematic Chains" is a title, not a retirement. A retirement keyword now has to sit in
    the row's status text, and `CLOSED <date> by <doc>` is a graduation - tracked, with the doc that
    graduated it as the evidence.

Every formula record also carries `provenance` - derived, sourced, or unsourced.

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
from animation_registry_render import (  # noqa: E402  (the Markdown face, split out at the 800-line cap)
    KIND_ORDER, PROVENANCE_ORDER, STATUS_ORDER, render_md)
# The prose side - markdown structure, the research layer, the citation chain and the row verdicts -
# is `animation_registry_chain`, split out at the same cap. It is imported back whole, so every
# public name of the registry is still importable from here.
from animation_registry_chain import (  # noqa: E402,F401  (re-exported: see above)
    CHAIN_ARROW, EXPR_MAX, NAME_MAX, RESEARCH_INDEX_REL, RETIRED_WORD, ROW_FILES, SOURCES_DIR,
    Research, chain_hits, chain_reach, chain_roots, doc_of, file_headings, formula_files,
    graduation_target, header_comment, header_lines, heading_map, heading_spans, norm_heading,
    prose_lines, provenance, read_text, rel_of, research_index_edges, retirement, section_matcher,
    split_lines, status_text, strip_markdown, table_rows, truncate, unfenced)

JSONL_REL = "docs/ANIMATION-REGISTRY.jsonl"
MD_REL = "docs/ANIMATION-REGISTRY.md"
INDEX_REL = "docs/DOCS-INDEX.jsonl"
CITATIONS_REL = "docs/DOCS-CITATIONS.jsonl"
KINETICS_DIR = "content/video_engine/scripts/kinetics"
TEMPLATE_REL = "docs/content-video-engine/samples/scene-evidence-player.template.html"
TESTS_DIR = "content/video_engine/tests"
SCRIPTS_DIR = "content/video_engine/scripts"

TEMPLATE_DIAL_OBJECTS = ("MARK", "SP", "LP")
TEMPLATE_DIAL_SCALARS = ("MOUNT_STEPS", "DISSOLVE_S", "LP_MOUNT_RISE", "CAP_LAST_HOLD_S")

SIG_MAX = 200            # the cap on a signature, so a one-line object cannot flood the md
VALUE_MAX = 120
EVIDENCE_MAX = 6         # evidence entries kept per record, sorted
CONTEXT_COMMENTS = 8     # comment lines read around a declaration for its citations

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
COMMENT_LINE = re.compile(r"^\s*(?:/\*|\*|//|\*/)")

# `=` plus one of these makes a line a formula: the Greek block, subscripts, and the operators the
# docs use. The spec's set, unextended - a minus-only line ("v_contact - v_surface = 0") is caught
# by the law rule instead.
MATH_SYMBOL = re.compile(r"[Ͱ-Ͽ₀-₟]|\^|√|∝|\bcoth\b|\bexp\(")
# a hyphen/slash compound is the distinctive part of a name: "two-thirds", "zero-slip", "FK/IK"
COMPOUND = re.compile(r"[A-Za-z][A-Za-z0-9]*(?:[-/][A-Za-z0-9]+)+")
# the one reference form the citation graph does not carry: a FINDING doc has no document number
FINDING_REF = re.compile(r"(?<![\w-])(FINDING-[A-Za-z][A-Za-z0-9-]*?)\s+s(\d+(?:\.\d+)*[a-z]?)(?![\w.])")

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

def read_jsonl(root: Path, rel: str) -> list[dict]:
    return [json.loads(line) for line in read_text(root, rel).splitlines() if line.strip()]


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
        self.gates = {rel_of(self.root, p): p.read_text(encoding="utf-8", errors="replace")
                      for p in sorted((self.root / SCRIPTS_DIR).glob("gate_*.py"))}
        self.rows = table_rows(self.root)
        self.research = Research(self.root, formula_files(self.root))
        self._bodies: dict[str, list[tuple[str, str, int, int]]] = {}
        self.research_index = research_index_edges(self)

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

    def spans(self, rel: str) -> list[dict]:
        """The file's headings with the line each one's section ends on - the docs index when it
        carries the file, the file itself when it does not. A level-1 heading spans the whole doc,
        which is what makes a whole-doc cite (`doc 45`) read doc 45's own source references."""
        recs = self.headings.get(rel) or file_headings(self.root, rel)
        return heading_spans(recs, len(split_lines(read_text(self.root, rel))))

    def section_text(self, rel: str, line: int) -> str:
        """The body of the section a line sits in, its own heading included."""
        lines = split_lines(read_text(self.root, rel))
        found = [s for s in self.spans(rel) if s["line"] <= line <= s["end"]]
        if not found:
            return ""
        span = max(found, key=lambda s: s["line"])
        return "\n".join(lines[span["line"] - 1:span["end"]])

    def body_edges(self, anchor: str) -> list[tuple[str, str, int, int]]:
        """The research sections our section's own body references - the `07 §5.3` in doc 42 §42.2,
        the `06` §2-4 in doc 45's sources. Cached: a doc section is read once per build."""
        if anchor not in self._bodies:
            rel, _, line = anchor.rpartition(":")
            self._bodies[anchor] = self.research.refs(self.section_text(rel, int(line)))
        return self._bodies[anchor]

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


# --- status -------------------------------------------------------------------------------

def apply_status(records: list[dict], corpus: Corpus) -> None:
    """`status` + `status_evidence` on every code and formula record, `provenance` on the formulas.

    Precedence is implemented > retired > tracked > orphaned: code that exists is implemented
    whatever a row says, and a row calling something invented outranks a row that merely names it."""
    code = [r for r in records if r["kind"] == "code"]
    for rec in code:
        set_status(rec, *code_status(rec, corpus))
    chains = chain_reach(corpus, code)
    for rec in (r for r in records if r["kind"] == "formula"):
        anchor, tokens = rec["_anchor"], name_tokens(rec["name"])
        rows = naming_rows(corpus, tokens, own=(rec["path"], rec["line"]))
        strong, chain = chain_hits(chains, rec)
        set_status(rec, *formula_status(rec, corpus, code, rows, strong, chain))
        rec["provenance"] = provenance(rec, corpus, anchor, rows, chain)


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


def formula_status(rec: dict, corpus: Corpus, code: list[dict], rows: list[tuple[str, int, str]],
                   strong: list[str], chain: list[str]) -> tuple[str, list[str]]:
    anchor = rec.pop("_anchor")
    evidence = [f"{c['module']}:{c['line']}" for c in code
                if anchor and any(cite["to"] == anchor for cite in c["cites"])]
    evidence += token_hits(corpus, name_tokens(rec["name"]))
    if evidence:
        return "implemented", evidence
    status, row_evidence = row_status(corpus, rows)
    # a module chain outranks a row that tracks the research - the math ships, and the row saying so
    # is the triage of a citation orphan, not a gap. A row calling it invented still outranks both.
    if strong and status != "retired":
        return "implemented", strong
    cited = [f"{e['from']['path']}:{e['from']['line']}" for e in corpus.citations
             if anchor and e["from"]["path"] in ROW_FILES and e.get("to")
             and f"{e['to']['path']}:{e['to']['line']}" == anchor]
    if status == "orphaned":
        # a gate chain speaks only here, where nothing else does: a check is not a build
        if chain:
            return "implemented", chain
        if cited:
            return "tracked", cited
    return status, row_evidence + (cited if status == "tracked" else [])


def naming_rows(corpus: Corpus, tokens: tuple[str, ...],
                own: tuple[str, int] | None = None) -> list[tuple[str, int, str]]:
    """The BACKLOG and doc-47 rows that name these tokens.

    A formula that IS such a row is its own row: doc 47's DESIGNED-OUT table states the formula and
    tracks it in the same line, and no token match can see that."""
    return [row for row in corpus.rows
            if mentions(row[2], tokens) or (own and (row[0], row[1]) == own)]


def row_status(corpus: Corpus, rows: list[tuple[str, int, str]]) -> tuple[str, list[str]]:
    """What those rows say: retired, tracked (with what graduated it), or nothing.

    A retirement is a verdict in the row's status text. "**Two-handed closed kinematic chains**" is a
    title that happens to contain the word - it retires nothing, and the row's actual verdict
    (`BACKLOG.md:431`) is "deferred with a trigger"."""
    verdicts = [(row, retirement(row[2])) for row in rows]
    retired = [row for row, kind in verdicts if kind == "retired"]
    if retired:
        return "retired", [f"{p}:{n}" for p, n, _ in retired]
    if rows:
        graduated = [t for row, kind in verdicts if kind == "graduated"
                     for t in graduation_target(corpus, row[0], row[2])]
        return "tracked", [f"{p}:{n}" for p, n, _ in rows] + graduated
    return "orphaned", []


# --- naming evidence ----------------------------------------------------------------------

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
    prov = ", ".join(f"{sum(1 for r in records if r.get('provenance') == p)} {p}"
                     for p in PROVENANCE_ORDER)
    return f"{len(records)} records ({kinds}; {status}; {prov})"


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
