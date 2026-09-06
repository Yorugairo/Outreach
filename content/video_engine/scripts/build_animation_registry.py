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

JSONL_REL = "docs/ANIMATION-REGISTRY.jsonl"
MD_REL = "docs/ANIMATION-REGISTRY.md"
INDEX_REL = "docs/DOCS-INDEX.jsonl"
CITATIONS_REL = "docs/DOCS-CITATIONS.jsonl"
KINETICS_DIR = "content/video_engine/scripts/kinetics"
TEMPLATE_REL = "docs/content-video-engine/samples/scene-evidence-player.template.html"
TESTS_DIR = "content/video_engine/tests"
DOCS_DIR = "docs/content-video-engine"
SOURCES_DIR = "content/video_engine/sources/reference_analyses"
SCRIPTS_DIR = "content/video_engine/scripts"
RESEARCH_INDEX_REL = f"{DOCS_DIR}/RESEARCH-INDEX.md"   # research heading -> the doc section it became
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
CHAIN_ARROW = " → "      # code:line → our §section → research §section
DOCSTRING_HEAD = 3       # lines a script's own docstring may start on

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
# `closed-form` is not `closed`, and neither is the "closed form" of doc 47's seek-test note
RETIRED_WORD = re.compile(
    r"\breclassified\b|\bwithdrawn\b|\bclosed\b(?![-\w])(?!\s+form\b)|\binvented\b", re.I)
# a graduation, not a withdrawal: "**CLOSED 2026-09-04** by [48-THE-FIGURE-AND-THE-GROUND](...)"
GRADUATION = re.compile(r"\bclosed\b[^|]{0,40}?\bby\b\s*(?P<target>[^|]{0,120})", re.I)
# what makes a number ours rather than a finding
DERIVED_TAG = re.compile(r"\[DERIVED", re.I)
DERIVED_WORD = re.compile(r"\binvented\b|\breclassified\b|\bderived\b", re.I)
URL_MARK = re.compile(r"\bURL:")
BOLD_SPAN = re.compile(r"\*\*(.+?)\*\*", re.S)
CELL_LEAD = re.compile(r"^(?:~~[^~]*~~|[\s*_→>-])*")     # strikethrough titles and emphasis marks
# how the ledger writes a verdict inside a bold run: in capitals, or as a sentence of its own.
# "**closed**" emphasising the word in a sentence about the keyword is not a verdict.
VERDICT_LEAD = re.compile(r"(?:CLOSED|WITHDRAWN|RECLASSIFIED|INVENTED|DERIVED)\b"
                          r"|(?:Closed|Withdrawn|Reclassified|Invented|Derived)\s*[.:]")
DOC_LINK = re.compile(r"\]\(([A-Za-z0-9][\w.-]*\.md)\)")   # "[48-THE-FIGURE...](48-THE-FIGURE....md)"
RULE_CONSTANT = re.compile(r"^[A-Z][A-Z0-9_]*\s*=\s*[\"']")   # `SRC_G_M = "47 s2 G-m / 49 s49.2 …"`
# `07 §5.3`, ``06`` §2-4, `07 s5.3` - a reference to the RESEARCH layer, whose numbers are the `NN_`
# prefixes of the bundle, not our doc numbers. `42 §42.1` parses here too and is dropped: no research
# file is numbered 42. `42 SS42.1` is the RESEARCH-INDEX table's ASCII rendering of `§`.
RESEARCH_REF = re.compile(r"`?(?<![\w.])(?P<num>\d{1,2})`?\s*(?:§+|SS|\bs)\s*"
                          r"(?P<sec>\d+(?:\.\d+)*)(?:\s*[-–—]\s*(?P<end>\d+)\b)?")
SECTION_TOKEN = re.compile(r"^\s*(\d+(?:\.\d+)*)")
FILE_NUMBER = re.compile(r"^(\d{1,2})[_-]")

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


def heading_spans(recs: list[dict], total: int) -> list[dict]:
    """Heading records with `end` - the last line of the section, which runs to the next heading of
    the same or a higher level. A subsection is inside its parent's span, so a reference to
    "3.1 Closed-Form Physics" reaches the three damping regimes stated under it."""
    out = [dict(rec) for rec in sorted(recs, key=lambda r: r["line"])]
    for i, rec in enumerate(out):
        later = [o["line"] - 1 for o in out[i + 1:] if o.get("level", 7) <= rec.get("level", 7)]
        rec["end"] = later[0] if later else total
    return out


def section_matcher(token: str) -> re.Pattern:
    """A heading that IS section `token`: the token, then anything but a digit. The research files
    number their headings "4. Engine 3: …" and "4.1 Mechanics Under the Hood", so the trailing dot of
    an outline number has to be allowed where a decimal digit does not - `4.1` is not `4`."""
    return re.compile(r"^\s*" + re.escape(token) + r"(?:(?![\w.])|\.(?!\d))")


def norm_heading(text: str) -> str:
    """A heading as a RESEARCH-INDEX row writes it: no emphasis, no backticks, no trailing colon."""
    text = truncate(text.replace("**", "").replace("~~", "").replace("`", ""), NAME_MAX)
    return text.strip().rstrip(":").casefold()


class Research:
    """The research layer: `content/video_engine/sources/reference_analyses/**`, addressed the way
    the docs address it - by the `NN_` number of the bundle file (``07`` §5.3) or by a heading a
    RESEARCH-INDEX row names verbatim.

    Three of the scanned files are held twice on disk, a bundle copy and a top-level copy, so one
    research section lives at two paths. The copies are byte-identical; a chain that reaches one
    reaches its twin at the same line, which is why the orphan list showed everything twice."""

    def __init__(self, root: Path, files: list[str]) -> None:
        self.paths = [rel for rel in files if rel.startswith(SOURCES_DIR)]
        texts = {rel: read_text(root, rel) for rel in self.paths}
        self.sections = {rel: heading_spans(file_headings(root, rel), len(split_lines(texts[rel])))
                         for rel in self.paths}
        same: dict[str, list[str]] = {}
        for rel in self.paths:
            same.setdefault(texts[rel], []).append(rel)
        self.twins = {rel: same[texts[rel]] for rel in self.paths}
        self.by_number: dict[int, list[str]] = {}
        for rel in self.paths:
            match = FILE_NUMBER.match(rel.rsplit("/", 1)[-1])
            if match:
                self.by_number.setdefault(int(match.group(1)), []).append(rel)

    def label(self, rel: str, rec: dict) -> str:
        """`07§1.2` - the reference form the chain evidence is written in."""
        match = FILE_NUMBER.match(rel.rsplit("/", 1)[-1])
        number = match.group(1) if match else rel.rsplit("/", 1)[-1][:12]
        token = SECTION_TOKEN.match(rec["heading"])
        return f"{number}§{token.group(1) if token else truncate(rec['heading'], 40)}"

    def _reach(self, rel: str, rec: dict) -> list[tuple[str, str, int, int]]:
        label = self.label(rel, rec)
        return [(label, twin, rec["line"], rec["end"]) for twin in self.twins[rel]]

    def section(self, number: int, token: str) -> list[tuple[str, str, int, int]]:
        """(label, path, start, end) for every section a ``07`` §5.3-style reference names."""
        pattern = section_matcher(token)
        return [hit for rel in self.by_number.get(number, [])
                for rec in self.sections[rel] if pattern.match(rec["heading"])
                for hit in self._reach(rel, rec)]

    def heading(self, rel: str, text: str) -> list[tuple[str, str, int, int]]:
        """The same, for a heading a RESEARCH-INDEX row names verbatim in one named file."""
        want = norm_heading(text)
        return [hit for rec in self.sections.get(rel, [])
                if norm_heading(rec["heading"]) == want for hit in self._reach(rel, rec)]

    def refs(self, text: str) -> list[tuple[str, str, int, int]]:
        """Every research section referenced in a stretch of prose. A number no research file
        carries is not a research reference - that is what keeps `42 §42.1` out."""
        out: list[tuple[str, str, int, int]] = []
        for match in RESEARCH_REF.finditer(text):
            number, token = int(match.group("num")), match.group("sec")
            tokens = [token]
            if match.group("end") and token.isdigit():      # `06` §2-4 is 2, 3 and 4
                tokens = [str(n) for n in range(int(token), int(match.group("end")) + 1)]
            for hit in (h for t in tokens for h in self.section(number, t)):
                if hit not in out:
                    out.append(hit)
        return out

    def file_of(self, name: str) -> str | None:
        """The scanned path a RESEARCH-INDEX file heading names (`` `07_academic_...md` ``)."""
        base = norm_heading(name).split(" — ")[0].strip()
        hits = [rel for rel in self.paths if rel.rsplit("/", 1)[-1].casefold() == base]
        return hits[0] if hits else None


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


def retirement(row: str) -> str | None:
    """"retired", "graduated", or None for one row.

    The keyword has to be the verdict, so it is read outside the row's bolded titles - except where a
    bold run BEGINS with it ("**CLOSED 2026-09-05** - ...", "**WITHDRAWN 2026-09-04 ...**"), which is
    exactly how a status is written here. `CLOSED <date> by <doc>` is a graduation: X10 closed because
    doc 48 was written, and the question became a written standard rather than being withdrawn."""
    if not RETIRED_WORD.search(status_text(row)):
        return None
    return "graduated" if GRADUATION.search(row.replace("**", "")) else "retired"


def graduation_target(corpus: Corpus, rel: str, row: str) -> list[str]:
    """The doc a graduation names, resolved - a graduation must carry what closed it as evidence.
    The target is written either as a reference (`by 48 §48.1`) or as a link to the doc itself."""
    match = GRADUATION.search(row.replace("**", ""))
    target = truncate(match.group("target"), NAME_MAX) if match else ""
    links = [f"{rel.rsplit('/', 1)[0]}/{m.group(1)}:1" for m in DOC_LINK.finditer(target)]
    out = links + [cite["to"] for cite in corpus.refs(target) if cite["to"]]
    return out[:1] or ([f"CLOSED by {truncate(target, 60).strip(' *_-—.')}"] if target.strip() else [])


def provenance(rec: dict, corpus: Corpus, anchor: str | None,
               rows: list[tuple[str, int, str]], chain: list[str]) -> str:
    """Where the figure came from: derived (ours, computed), sourced (a research file or a URL is
    behind it), or unsourced - stated with nothing behind it."""
    body = corpus.section_text(rec["path"], rec["line"])
    if DERIVED_TAG.search(body) or any(DERIVED_WORD.search(status_text(row)) for _, _, row in rows):
        return "derived"
    reaches = chain or rec["path"].startswith(SOURCES_DIR) or URL_MARK.search(body)
    if reaches or (anchor and (corpus.body_edges(anchor) or corpus.research_index.get(anchor))):
        return "sourced"
    return "unsourced"


def status_text(row: str) -> str:
    """A row's verdict text: the bolded runs that OPEN on a verdict ("**CLOSED 2026-09-05** ...",
    "**Closed.** Superseded by ..."), plus everything outside the bold runs.

    `**A6 secondary-motion ratio (0.22)**` is a title and "An invented number." is the verdict;
    `**Two-handed closed kinematic chains**` is a title that contains the word and decides nothing."""
    outside = BOLD_SPAN.sub(" | ", row)
    lead = [s for s in (m.group(1) for m in BOLD_SPAN.finditer(row))
            if VERDICT_LEAD.match(CELL_LEAD.sub("", s))]
    return " ".join(lead + [outside])


# --- the citation chain ---------------------------------------------------------------------

def chain_roots(corpus: Corpus, code: list[dict]) -> list[tuple[str, list[dict], bool]]:
    """(where, cites, strong) for everything a chain may start from.

    A kinetics module is a STRONG root: its header states the doc sections whose math it ships, so it
    outranks a row that merely tracks the research those sections came from. A gate script is a weak
    root: it states the doc sections it enforces, which makes it evidence where there is none - the
    LTX `8n+1` frame law is a shipped gate - but a check is not a build, so it never overturns a row.
    That is the difference between the frame law (nothing else speaks) and zero-slip anchoring (a gate
    checks a proxy, the rows track it, and nothing binds the ground)."""
    roots = []
    shipped = {rec["module"] for rec in code if rec["status"] == "implemented"}
    for rel in sorted(shipped):
        head = split_lines(corpus.modules[rel])[:header_lines(corpus.modules[rel])]
        for i, line in enumerate(head):          # the header line the citation is written on
            cites = corpus.refs(line)
            if cites:
                roots.append((f"{rel}:{i + 1}", cites, True))
    for rel, text in corpus.gates.items():
        for i, line in prose_lines(split_lines(text)):
            cites = corpus.refs(line)
            if cites:
                roots.append((f"{rel}:{i + 1}", cites, False))
    return roots


def prose_lines(lines: list[str]):
    """(index, line) for a Python script's docstring, comments and rule constants - where a script
    states what it enforces. Its code is not prose and cannot cite."""
    doc, quote = False, None
    for i, line in enumerate(lines):
        stripped = line.strip()
        if doc:
            yield i, line
            if quote in stripped:
                doc = False
            continue
        if i < DOCSTRING_HEAD and stripped[:3] in ('"""', "'''"):
            quote = stripped[:3]
            doc = stripped.count(quote) < 2       # a one-line docstring opens and closes here
            yield i, line
        elif stripped.startswith("#") or RULE_CONSTANT.match(stripped):
            yield i, line


def chain_reach(corpus: Corpus, code: list[dict]) -> dict[str, list[tuple[int, int, str, bool]]]:
    """research path -> (start, end, chain, strong) for every research section our shipped code
    reaches through one of our own doc sections. The chain is written the way it is read:
    `…/stroke.mjs:5 → 42§42.1 → 07§1.2`."""
    out: dict[str, list[tuple[int, int, str, bool]]] = {}
    for where, cites, strong in chain_roots(corpus, code):
        for cite in cites:
            anchor = cite["to"]
            if not anchor:
                continue
            reached = corpus.body_edges(anchor) + corpus.research_index.get(anchor, [])
            for label, path, start, end in reached:
                chain = CHAIN_ARROW.join([where, cite["ref"], label])
                out.setdefault(path, []).append((start, end, chain, strong))
    return out


def chain_hits(chains: dict[str, list[tuple[int, int, str, bool]]],
               rec: dict) -> tuple[list[str], list[str]]:
    """(strong, all) chains that reach this record - a section covers the subsections under it."""
    hits = [(chain, strong) for start, end, chain, strong in chains.get(rec["path"], [])
            if start <= rec["line"] <= end]
    return sorted({c for c, strong in hits if strong}), sorted({c for c, _ in hits})


def research_index_edges(corpus: Corpus) -> dict[str, list[tuple[str, str, int, int]]]:
    """our-section anchor -> the research sections extracted into it, out of RESEARCH-INDEX.md.

    That file is one table per research file (`### \\`07_academic_...md\\` - 26 headings`), one row per
    heading, and the disposition names where it went: `| 1.2 Kinematic Arc-Length Reparameterization
    for SVG & Canvas | EXTRACTED -> 42 SS42.1 |`. It is the only place that says which research
    section became which of our sections, and its `SS` spelling is invisible to the citation graph."""
    out: dict[str, list[tuple[str, str, int, int]]] = {}
    research_rel = None
    for _, line in unfenced(split_lines(read_text(corpus.root, RESEARCH_INDEX_REL))):
        heading = HEADING.match(line)
        if heading:
            research_rel = corpus.research.file_of(heading.group(2))
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if research_rel is None or not line.lstrip().startswith("|") or len(cells) != 2:
            continue
        if TABLE_SEP.match(line):
            continue
        reached = corpus.research.heading(research_rel, cells[0])
        for cite in corpus.refs(cells[1].replace("SS", "§")):
            if not cite["to"]:
                continue
            edges = out.setdefault(cite["to"], [])
            edges += [r for r in reached if r not in edges]
    return out


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
