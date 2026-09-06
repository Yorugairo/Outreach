"""The prose side of the animation registry: markdown structure, the research layer, the chain.

Split out of `build_animation_registry.py` on 2026-09-05 (the second cut, after
`animation_registry_render.py` took the Markdown face), when the citation chain, the research layer
and the ledger verdicts pushed that module past the 800-line style cap. Nothing here changed in the
move: `build_animation_registry` imports every name back, so the registry's public surface is
unchanged and `docs_find.py`, `build_docs_layers.py` and the tests keep reading it there.

The split is by what is read, not by what is built. Everything in this module reads PROSE - our
numbered docs, the research bundle, RESEARCH-INDEX.md and the ledger rows of BACKLOG /
47-FINDINGS-TO-CHECKS - and answers three questions:

  * structure - which heading a line sits under, where that section ends, which files are read
  * the research layer - `Research`, the bundle addressed as the docs address it (``07`` §5.3)
  * the chain - `code:line -> our §section -> research §section`, and what a row's verdict says

`build_animation_registry` keeps the code side: the kinetics modules, the dials, the formula
records, the status precedence and the build. Standard library only.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:                     # annotation only - importing it for real would be circular
    from build_animation_registry import Corpus

# --- what is read -------------------------------------------------------------------------

DOCS_DIR = "docs/content-video-engine"
SOURCES_DIR = "content/video_engine/sources/reference_analyses"
RESEARCH_INDEX_REL = f"{DOCS_DIR}/RESEARCH-INDEX.md"   # research heading -> the doc section it became
ROW_FILES = (f"{DOCS_DIR}/BACKLOG.md", f"{DOCS_DIR}/47-FINDINGS-TO-CHECKS.md")
EXTRA_DOCS = (f"{DOCS_DIR}/FINDING-the-animation-math-and-what-it-changes.md",
              f"{DOCS_DIR}/briefs/ANSWERS-RESEARCH-BRIEF-animation-craft.md")
DOC_NUMBERS = (29, *range(42, 54))
SOURCE_NAME = re.compile(r"animation|drawing|kinetic|academic_literature", re.I)

EXPR_MAX = 200           # the spec's cap on a formula's text
NAME_MAX = 120
CHAIN_ARROW = " → "      # code:line → our §section → research §section
DOCSTRING_HEAD = 3       # lines a script's own docstring may start on


# --- patterns -----------------------------------------------------------------------------

HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
FENCE = re.compile(r"^\s*(?:```|~~~)")
TABLE_SEP = re.compile(r"^\s*\|?\s*:?-{3,}")
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


def rel_of(root: Path, path: Path) -> str:
    return path.resolve().relative_to(Path(root).resolve()).as_posix()


# --- markdown structure -------------------------------------------------------------------

def heading_map(index: list[dict]) -> dict[str, list[dict]]:
    """path -> its heading records (levels 1-6) in line order; a table row encloses nothing."""
    out: dict[str, list[dict]] = {}
    for rec in index:
        if rec.get("level", 7) <= 6:
            out.setdefault(rec["path"], []).append(rec)
    for recs in out.values():
        recs.sort(key=lambda r: r["line"])
    return out



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


def strip_markdown(text: str) -> str:
    return truncate(text.replace("**", "").replace("~~", "").strip("| "), EXPR_MAX)


def doc_of(rel: str, section: dict | None) -> str | None:
    if section and section.get("doc"):
        return section["doc"]
    match = re.match(r"(\d{1,3})-", rel.rsplit("/", 1)[-1])
    return match.group(1) if match else None


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


# --- the research layer -------------------------------------------------------------------

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


# --- the citation chain -------------------------------------------------------------------

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


# --- what a ledger row's verdict says ------------------------------------------------------

def status_text(row: str) -> str:
    """A row's verdict text: the bolded runs that OPEN on a verdict ("**CLOSED 2026-09-05** ...",
    "**Closed.** Superseded by ..."), plus everything outside the bold runs.

    `**A6 secondary-motion ratio (0.22)**` is a title and "An invented number." is the verdict;
    `**Two-handed closed kinematic chains**` is a title that contains the word and decides nothing."""
    outside = BOLD_SPAN.sub(" | ", row)
    lead = [s for s in (m.group(1) for m in BOLD_SPAN.finditer(row))
            if VERDICT_LEAD.match(CELL_LEAD.sub("", s))]
    return " ".join(lead + [outside])


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
