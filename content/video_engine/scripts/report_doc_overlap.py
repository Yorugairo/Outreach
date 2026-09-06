"""What a compressed doc still holds that the doc it was compressed INTO dropped - the lift list.

Operator ruling, 2026-09-05: "we compressed the docs because we didn't have a proper search system;
now that we do, we shouldn't kill everything in the compressed docs. The right way is to lift the
differences out and dedupe." A doc labelled "superseded by 29" / "record only" / "partially
superseded" was not a bad document - it was compressed, and compression drops detail. This report
makes the lift mechanical: per compressed section, is the target carrying it (DUPLICATE), carrying
some of it (PARTIAL), or carrying nothing like it (DELTA)?

    python content/video_engine/scripts/report_doc_overlap.py --write   # regenerate both artifacts
    python content/video_engine/scripts/report_doc_overlap.py --check   # exit 1 when stale (default)
    python content/video_engine/scripts/report_doc_overlap.py --pair 15=29 --pair 16=29   # add/override

    docs/DOC-OVERLAP.jsonl   one record per compressed section - the thing you `rg`
    docs/DOC-OVERLAP.md      the same, readable: DELTA first, because DELTA is the lift list

PAIRS ARE DISCOVERED, NEVER HARD-CODED. Three sources, in this order:

  (a) `AGENTS.md`: a sentence naming a doc and a marker - "Doc 16 ... is partially superseded by it
      and doc 15 ... is record only". The target is the doc the marker names outright, else the
      antecedent of "it": the first doc the enclosing list item / paragraph references and that is
      not itself being marked.
  (b) any doc whose first HEAD_LINES lines carry a marker - `superseded (by)`, `deprecated`,
      `compressed into`, `folded into`, `record only`, `see <doc>` - in a `> **STATUS:` byline or any
      other block up there. The target is resolved from the same block, by doc number against the
      docs index or by path.
  (c) `--pair <compressed>=<target>`, either side a doc number or a repo-relative path. An explicit
      pair REPLACES a discovered pair for the same compressed doc.

A marker whose named target does not resolve is reported as unresolved, never guessed; a marker that
names no target at all is counted and listed, because "STATUS: RECORD" alone is not a pair.

SCORING, all three thresholds fixed here and printed into the report:

  score_heading  1.0 when the normalised headings are equal (numbering, `Part N`, parentheticals and
                 punctuation removed), else 0.0
  score_jaccard  over the union of the two sections' labels + terms + heading tokens, taken from
                 `docs/DOCS-INDEX.jsonl` when it covers the path and computed the same way when it
                 does not (a `tmp_path` corpus has no index)
  score_body     `difflib.SequenceMatcher.ratio()` over the two section bodies as WORD lists, fenced
                 code stripped, `autojunk=False` (character-level with autojunk would junk every
                 common letter on a body this long). Computed only when score_jaccard >= JACCARD_FLOOR
                 to keep it cheap, and only when difflib's own cheap upper bound clears BODY_PARTIAL;
                 below that the upper bound is reported, which lands in the same class either way.

  DUPLICATE  heading match, or score_body >= BODY_DUPLICATE
  PARTIAL    BODY_PARTIAL <= score_body < BODY_DUPLICATE, or score_jaccard >= JACCARD_PARTIAL
  DELTA      neither - the target has nothing like it

For PARTIAL and DELTA the section's RULE lines are listed with `path:line`, because those are what
gets lifted: a numbered/bulleted item, a line carrying must / never / always / only / rule / gate, or
the lead-in of a ladder (a line ending in `:` whose next line is a list item - "Motion is authored in
this order:" is the rule; its four numbered steps are its body).

Standard library only. Deterministic (no timestamps), written with LF. Both artifacts are already
excluded from the docs-index walk by `docs/DOCS-INDEX.config.json`, so indexing them is not a risk.
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_docs_index as BDI  # noqa: E402  (the walk, the terms and the labels are defined once)

REPO = Path(__file__).resolve().parents[3]

JSONL_REL = "docs/DOC-OVERLAP.jsonl"
MD_REL = "docs/DOC-OVERLAP.md"
INDEX_REL = "docs/DOCS-INDEX.jsonl"
AGENTS_REL = "AGENTS.md"

HEAD_LINES = 30              # how far into a doc a status byline may sit
BODY_WORDS = 1200            # words of a section body compared; longer sections are truncated
JACCARD_FLOOR = 0.15         # below this the body ratio is not worth computing
JACCARD_PARTIAL = 0.40       # vocabulary overlap alone is enough for PARTIAL
BODY_PARTIAL = 0.30
BODY_DUPLICATE = 0.60
MIN_HEADING_CHARS = 3        # a one-token normalised heading is not an identity
RULE_TEXT_MAX = 160

MARKERS = (
    "superseded by", "partially superseded", "superseded",
    "compressed into", "folded into", "record only", "deprecated",
)

# --- patterns -----------------------------------------------------------------------------

DOC_MENTION = re.compile(r"\bdocs?\.?\s+(\d{1,3})\b", re.I)
BOLD_DOC = re.compile(r"\*\*(\d{1,3})(?:\s*[§s][\d.]+)?\*\*")
PATH_DOC = re.compile(r"\b(\d{1,3})-[A-Za-z0-9][A-Za-z0-9-]*\.md\b")
MD_LINK = re.compile(r"\]\(([^)\s]+\.md)(?:#[^)\s]*)?\)")
EXPLICIT_TARGET = re.compile(
    r"(?:superseded\s+by|compressed\s+into|folded\s+into|see)\s+"
    r"(?:the\s+)?(?:\*\*)?(?:docs?\.?\s+)?(\d{1,3})\b", re.I)
SENTENCE_END = re.compile(r"[.!?][)\"'’*\]]*(?:\s+|$)")
LIST_ITEM = re.compile(r"^\s{0,8}(?:[-*+]|\d+[.)])\s+\S")
BLOCK_START = re.compile(r"^\s{0,8}(?:[-*+]|\d+[.)])\s")
RULE_WORDS = re.compile(r"\b(?:must|never|always|only|rules?|gates?)\b", re.I)
HEAD_NUMBER = re.compile(r"^(?:part\s+)?\d+(?:\.\d+)*\s*[.)—–:-]*\s*", re.I)
PARENTHETICAL = re.compile(r"\([^)]*\)")
WORD = re.compile(r"[a-z0-9]+")
BODY_WORD = re.compile(r"[a-z0-9][a-z0-9_.-]*")

STOPWORDS = frozenset(
    "the and for its with that this from are was were has have had not but you your our their they "
    "them then than when what which who how why into onto over under out off all any one two each "
    "per via can may will shall does did done been being here there other more most such only very "
    "also just now new old use used using".split())


# --- small helpers ------------------------------------------------------------------------

def doc_key(rel_path: str) -> str:
    """A doc's short name: its leading number when it has one, else its file stem."""
    name = rel_path.rsplit("/", 1)[-1]
    return BDI.doc_id(rel_path) or name.rsplit(".", 1)[0]


def norm_heading(heading: str) -> str:
    """Lower-case, numbering / `Part N` / parentheticals / punctuation removed."""
    text = BDI.strip_emphasis(heading).replace("`", "").casefold()
    text = HEAD_NUMBER.sub("", text)
    text = PARENTHETICAL.sub(" ", text)
    text = re.sub(r"[^a-z0-9 ]+", " ", text)
    return " ".join(text.split())


def sentences(text: str) -> list[tuple[int, str]]:
    """(offset, sentence) - a boundary is `.!?` plus closers, followed by an opener or the end."""
    out: list[tuple[int, str]] = []
    start = 0
    for m in SENTENCE_END.finditer(text):
        nxt = text[m.end():m.end() + 1]
        if nxt and not (nxt.isupper() or nxt in "*\"“`[("):
            continue
        chunk = text[start:m.end()].strip()
        if chunk:
            out.append((start, chunk))
        start = m.end()
    tail = text[start:].strip()
    if tail:
        out.append((start, tail))
    return out


def has_marker(text: str) -> str:
    """The first marker the text carries, or ""."""
    low = text.casefold()
    return next((m for m in MARKERS if m in low), "")


# --- blocks: the unit a naming sentence lives in -------------------------------------------

@dataclass(frozen=True, slots=True)
class Block:
    """One list item or paragraph, flattened to a line with an offset -> line-number map."""

    text: str
    offsets: tuple[tuple[int, int], ...]      # (offset of the line in `text`, 1-based line number)

    def line_of(self, offset: int) -> int:
        line = self.offsets[0][1] if self.offsets else 1
        for start, number in self.offsets:
            if start > offset:
                break
            line = number
        return line


def blocks_of(lines: list[str], limit: int | None = None) -> list[Block]:
    """Paragraphs, split again at every list-item start; blockquote markers dropped."""
    groups: list[list[tuple[int, str]]] = []
    current: list[tuple[int, str]] = []
    for i, line in BDI.unfenced(lines[:limit] if limit else lines):
        text = re.sub(r"^\s*>\s?", "", line).rstrip()
        if not text.strip():
            current = []
            continue
        if not current or BLOCK_START.match(line):
            current = []
            groups.append(current)
        current.append((i + 1, text.strip()))
    out: list[Block] = []
    for group in groups:
        if not group:
            continue
        text_parts: list[str] = []
        offsets: list[tuple[int, int]] = []
        cursor = 0
        for number, text in group:
            offsets.append((cursor, number))
            text_parts.append(text)
            cursor += len(text) + 1
        out.append(Block(" ".join(text_parts), tuple(offsets)))
    return out


# --- resolving a doc reference -------------------------------------------------------------

def doc_number_map(paths: list[str]) -> dict[str, list[str]]:
    """{doc number: [path, ...]} - a list because two files may share a number (40- twice)."""
    out: dict[str, list[str]] = {}
    for rel_path in paths:
        number = BDI.doc_id(rel_path)
        if number:
            out.setdefault(number, []).append(rel_path)
    return {k: sorted(v) for k, v in out.items()}


def references(text: str) -> list[tuple[int, str]]:
    """(offset, reference) for every doc reference in reading order: link, path, **N**, "doc N"."""
    found = [(m.start(), m.group(1)) for m in MD_LINK.finditer(text)]
    found += [(m.start(), m.group(0)) for m in PATH_DOC.finditer(text)]
    found += [(m.start(), m.group(1)) for m in BOLD_DOC.finditer(text)]
    found += [(m.start(), m.group(1)) for m in DOC_MENTION.finditer(text)]
    return sorted(found)


class Resolver:
    """A doc reference - number, bare filename or link - to a repo-relative path."""

    def __init__(self, paths: list[str]) -> None:
        self.paths = set(paths)
        self.numbers = doc_number_map(paths)
        self.by_name: dict[str, list[str]] = {}
        for rel_path in paths:
            self.by_name.setdefault(rel_path.rsplit("/", 1)[-1].casefold(), []).append(rel_path)

    def resolve(self, reference: str, source: str = "") -> str | None:
        """The path a reference names, or None. `source` is the referring doc, for a relative link."""
        reference = reference.strip().strip("`")
        if reference.endswith(".md"):
            if source and not reference.startswith("docs/"):
                candidate = (Path(source).parent / reference).as_posix()
                candidate = Path(candidate).resolve().as_posix() if ".." in candidate else candidate
                for option in (candidate, re.sub(r"[^/]+/\.\./", "", (Path(source).parent / reference).as_posix())):
                    if option in self.paths:
                        return option
            if reference in self.paths:
                return reference
            names = self.by_name.get(reference.rsplit("/", 1)[-1].casefold(), [])
            return names[0] if len(names) == 1 else None
        number = re.sub(r"\D", "", reference)
        options = self.numbers.get(number, [])
        return options[0] if options else None


# --- pairs ----------------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class Pair:
    compressed: str
    target: str
    source: str          # "<path>:<line>" of the sentence that named it, or "--pair"
    sentence: str


@dataclass(frozen=True, slots=True)
class Unresolved:
    path: str
    line: int
    sentence: str
    reason: str


def _explicit_target(text: str, exclude: set[str], resolver: Resolver,
                     source_path: str) -> tuple[str | None, str | None]:
    """(path, reference) for a target the marker names outright: "superseded by **37 §8**"."""
    for m in EXPLICIT_TARGET.finditer(text):
        reference = m.group(1)
        if reference not in exclude:
            return resolver.resolve(reference, source_path), reference
    return None, None


def _antecedent_target(block: Block, exclude: set[str], resolver: Resolver,
                       source_path: str) -> tuple[str | None, str | None]:
    """The antecedent of "it": the first doc the enclosing block references that is neither the
    referring doc nor a doc being marked."""
    for _, reference in references(block.text):
        resolved = resolver.resolve(reference, source_path)
        if resolved and doc_key(resolved) not in exclude and resolved != source_path:
            return resolved, reference
    return None, None


def _target_from(text: str, block: Block, exclude: set[str], resolver: Resolver,
                 source_path: str) -> tuple[str | None, str | None]:
    """Explicit in `text`, else the block's antecedent."""
    target, reference = _explicit_target(text, exclude, resolver, source_path)
    if target or reference:
        return target, reference
    return _antecedent_target(block, exclude, resolver, source_path)


def pairs_from_agents(root: Path, resolver: Resolver) -> tuple[list[Pair], list[Unresolved]]:
    """(a) `AGENTS.md` sentences: "Doc 16 ... is partially superseded by it and doc 15 ... is
    record only". Every "doc N" whose slice of the sentence carries a marker is a compressed doc."""
    path = root / AGENTS_REL
    if not path.is_file():
        return [], []
    lines = BDI.split_lines(path.read_text(encoding="utf-8"))
    found: list[Pair] = []
    unresolved: list[Unresolved] = []
    for block in blocks_of(lines):
        for offset, sentence in sentences(block.text):
            mentions = list(DOC_MENTION.finditer(sentence))
            if not mentions or not has_marker(sentence):
                continue
            marked = {m.group(1) for m in mentions}
            for n, m in enumerate(mentions):
                end = mentions[n + 1].start() if n + 1 < len(mentions) else len(sentence)
                slice_text = sentence[m.start():end]
                if not has_marker(slice_text):
                    continue
                compressed = resolver.resolve(m.group(1), AGENTS_REL)
                line = block.line_of(offset + m.start())
                if not compressed:
                    unresolved.append(Unresolved(AGENTS_REL, line, sentence,
                                                 f"doc {m.group(1)} names no file in the corpus"))
                    continue
                target, reference = _target_from(slice_text, block, marked, resolver, AGENTS_REL)
                if not target:
                    unresolved.append(Unresolved(
                        AGENTS_REL, line, sentence,
                        f"doc {m.group(1)}: target {reference or 'unnamed'} does not resolve"))
                    continue
                found.append(Pair(compressed, target, f"{AGENTS_REL}:{line}", sentence))
    return found, unresolved


def pairs_from_bylines(root: Path, rel_paths: list[str],
                       resolver: Resolver) -> tuple[list[Pair], list[Unresolved], list[Unresolved]]:
    """(b) a marker in the first HEAD_LINES lines of a doc. Returns (pairs, unresolved, untargeted)."""
    found: list[Pair] = []
    unresolved: list[Unresolved] = []
    untargeted: list[Unresolved] = []
    for rel_path in rel_paths:
        lines = BDI.split_lines((root / rel_path).read_text(encoding="utf-8"))
        self_key = doc_key(rel_path)
        for block in blocks_of(lines, HEAD_LINES):
            if not has_marker(block.text):
                continue
            marked = [(block.line_of(offset), sentence) for offset, sentence in sentences(block.text)
                      if has_marker(sentence)]
            hit: Pair | None = None
            note: Unresolved | None = None
            # the naming sentence is the one that names the target; only when no sentence does is
            # the block's antecedent used, and then the first marker sentence is the evidence.
            for named in (True, False):
                for line, sentence in marked:
                    target, reference = (_explicit_target(sentence, {self_key}, resolver, rel_path)
                                         if named else
                                         _antecedent_target(block, {self_key}, resolver, rel_path))
                    if target and target != rel_path:
                        hit = Pair(rel_path, target, f"{rel_path}:{line}", sentence)
                        break
                    if reference and note is None:
                        note = Unresolved(rel_path, line, sentence,
                                          f"target {reference} does not resolve to a file in the corpus")
                if hit:
                    break
            if note is None and marked and not hit:
                line, sentence = marked[0]
                note = Unresolved(rel_path, line, sentence,
                                  f"marker \"{has_marker(sentence)}\" names no target")
            if hit:
                found.append(hit)
            elif note and "does not resolve" in note.reason:
                unresolved.append(note)
            elif note:
                untargeted.append(note)
    return found, unresolved, untargeted


def explicit_pairs(specs: list[str], resolver: Resolver) -> tuple[list[Pair], list[Unresolved]]:
    """(c) `--pair <compressed>=<target>`, either side a doc number or a repo-relative path."""
    found: list[Pair] = []
    unresolved: list[Unresolved] = []
    for spec in specs:
        if "=" not in spec:
            unresolved.append(Unresolved("--pair", 0, spec, "expected <compressed>=<target>"))
            continue
        left, right = (part.strip() for part in spec.split("=", 1))
        compressed, target = resolver.resolve(left), resolver.resolve(right)
        if not compressed or not target:
            missing = ", ".join(x for x, ok in ((left, compressed), (right, target)) if not ok)
            unresolved.append(Unresolved("--pair", 0, spec, f"{missing} does not resolve"))
            continue
        found.append(Pair(compressed, target, "--pair", spec))
    return found, unresolved


def merge_pairs(discovered: list[Pair], explicit: list[Pair]) -> tuple[Pair, ...]:
    """Discovered pairs deduplicated on (compressed, target); an explicit pair replaces every
    discovered pair for the same compressed doc."""
    kept: dict[tuple[str, str], Pair] = {}
    for pair in discovered:
        kept.setdefault((pair.compressed, pair.target), pair)
    for pair in explicit:
        for key in [k for k in kept if k[0] == pair.compressed]:
            del kept[key]
        kept[(pair.compressed, pair.target)] = pair
    return tuple(sorted(kept.values(), key=lambda p: (p.compressed.lower(), p.target.lower())))


# --- sections ---------------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class Section:
    path: str
    line: int                       # 1-based heading line
    heading: str
    norm: str
    tokens: frozenset[str]
    words: tuple[str, ...]
    start: int                      # 0-based first body line
    end: int                        # 0-based end of body, exclusive


def token_set(heading: str, labels: list[str], terms: list[str]) -> frozenset[str]:
    """Heading tokens + label tokens + terms (whole, and split into words)."""
    out: set[str] = set()
    for phrase in [norm_heading(heading), *(norm_heading(label) for label in labels)]:
        out |= {w for w in phrase.split() if len(w) >= 3 and w not in STOPWORDS}
    for term in terms:
        key = term.casefold().strip()
        if key:
            out.add(key)
        out |= {w for w in WORD.findall(key) if len(w) >= 3 and w not in STOPWORDS}
    return frozenset(out)


def body_words(lines: list[str], start: int, end: int) -> tuple[str, ...]:
    """The section body as words, fenced code stripped, capped at BODY_WORDS."""
    out: list[str] = []
    for _, line in BDI.unfenced(lines[start:end]):
        out += BODY_WORD.findall(BDI.strip_emphasis(line).casefold())
        if len(out) >= BODY_WORDS:
            return tuple(out[:BODY_WORDS])
    return tuple(out)


def sections_of(rel_path: str, lines: list[str], records: list[dict]) -> list[Section]:
    """One Section per heading, in file order. `records` are that file's docs-index records."""
    heads = BDI.heading_positions(lines)
    by_line = {r["line"]: r for r in records}
    out: list[Section] = []
    for n, (i, _level, heading) in enumerate(heads):
        end = heads[n + 1][0] if n + 1 < len(heads) else len(lines)
        record = by_line.get(i + 1, {})
        labels = record.get("labels") or BDI.labels_of(lines, i + 1, end)
        terms = record.get("terms") or BDI.terms_of(lines, i + 1, end, heading, labels)
        out.append(Section(rel_path, i + 1, heading, norm_heading(heading),
                           token_set(heading, labels, terms), body_words(lines, i + 1, end),
                           i + 1, end))
    return out


# --- rules ------------------------------------------------------------------------------------

def rules_of(rel_path: str, lines: list[str], section: Section) -> list[dict]:
    """The lines that get lifted: a list item, a modal line, or the lead-in of a ladder."""
    body = [(i, re.sub(r"^(\s*)>\s?", r"\1", line))
            for i, line in BDI.unfenced(lines[section.start:section.end])]
    out: list[dict] = []
    for n, (offset, line) in enumerate(body):
        text = line.strip()
        if not text or BDI.HEADING.match(line) or BDI.TABLE_SEP.match(line):
            continue
        is_rule = bool(LIST_ITEM.match(line)) or bool(RULE_WORDS.search(text))
        if not is_rule and text.endswith(":"):
            nxt = next((l for _, l in body[n + 1:] if l.strip()), "")
            is_rule = bool(LIST_ITEM.match(nxt))
        if is_rule:
            out.append({"line": section.start + offset + 1,
                        "text": BDI.truncate(BDI.strip_emphasis(text), RULE_TEXT_MAX)})
    return out


# --- matching -----------------------------------------------------------------------------------

def jaccard(left: frozenset[str], right: frozenset[str]) -> float:
    if not left or not right:
        return 0.0
    union = len(left | right)
    return len(left & right) / union if union else 0.0


def body_ratio(left: tuple[str, ...], right: tuple[str, ...]) -> float:
    """SequenceMatcher over word lists. Below BODY_PARTIAL difflib's cheap upper bound is
    returned instead of the exact ratio - the class is the same either way."""
    if not left or not right:
        return 0.0
    matcher = difflib.SequenceMatcher(None, left, right, autojunk=False)
    upper = matcher.real_quick_ratio()
    if upper < BODY_PARTIAL:
        return round(upper, 3)
    upper = matcher.quick_ratio()
    if upper < BODY_PARTIAL:
        return round(upper, 3)
    return round(matcher.ratio(), 3)


def classify(score_heading: float, score_jaccard: float, score_body: float) -> str:
    if score_heading == 1.0 or score_body >= BODY_DUPLICATE:
        return "DUPLICATE"
    if score_body >= BODY_PARTIAL or score_jaccard >= JACCARD_PARTIAL:
        return "PARTIAL"
    return "DELTA"


def best_match(section: Section, targets: list[Section]) -> tuple[Section | None, float, float, float]:
    """The target section that best carries this one, with its three scores."""
    best: tuple[float, float, float, int, Section | None] = (0.0, 0.0, 0.0, 0, None)
    for target in targets:
        heading = 1.0 if (section.norm and section.norm == target.norm
                          and len(section.norm) >= MIN_HEADING_CHARS) else 0.0
        overlap = round(jaccard(section.tokens, target.tokens), 3)
        body = body_ratio(section.words, target.words) if overlap >= JACCARD_FLOOR else 0.0
        candidate = (heading, body, overlap, -target.line, target)
        if candidate[:4] > best[:4]:
            best = candidate
    heading, body, overlap, _, target = best
    if target is None or (heading == 0.0 and body == 0.0 and overlap == 0.0):
        return None, 0.0, 0.0, 0.0
    return target, heading, overlap, body


# --- the report -----------------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class Report:
    pairs: tuple[Pair, ...]
    records: tuple[dict, ...]
    unresolved: tuple[Unresolved, ...]
    untargeted: tuple[Unresolved, ...]


def load_index(root: Path) -> dict[str, list[dict]]:
    """The docs-index records grouped by path, when the index exists."""
    path = root / INDEX_REL
    if not path.is_file():
        return {}
    out: dict[str, list[dict]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            record = json.loads(line)
            out.setdefault(record["path"], []).append(record)
    return out


def build(repo_root: Path | str = REPO, pairs: list[str] | None = None) -> Report:
    """Discover the pairs, classify every compressed section, and return the whole report."""
    root = Path(repo_root)
    config = BDI.load_config(root)
    # this tool's own artifacts are never discovery input: DOC-OVERLAP.md quotes every naming
    # sentence it found, so reading it back would pair a doc with itself on its own report.
    rel_paths = [rel for rel in (p.relative_to(root).as_posix() for p in BDI.doc_files(root, config))
                 if rel not in (JSONL_REL, MD_REL)]
    resolver = Resolver(rel_paths)
    index = load_index(root)

    from_agents, unresolved = pairs_from_agents(root, resolver)
    from_bylines, byline_unresolved, untargeted = pairs_from_bylines(root, rel_paths, resolver)
    from_flags, flag_unresolved = explicit_pairs(list(pairs or []), resolver)
    merged = merge_pairs(from_agents + from_bylines, from_flags)
    unresolved += byline_unresolved + flag_unresolved

    cache: dict[str, tuple[list[str], list[Section]]] = {}

    def load(rel_path: str) -> tuple[list[str], list[Section]]:
        if rel_path not in cache:
            lines = BDI.split_lines((root / rel_path).read_text(encoding="utf-8"))
            cache[rel_path] = (lines, sections_of(rel_path, lines, index.get(rel_path, [])))
        return cache[rel_path]

    records: list[dict] = []
    for pair in merged:
        lines, compressed = load(pair.compressed)
        _, targets = load(pair.target)
        for section in compressed:
            match, heading, overlap, body = best_match(section, targets)
            kind = classify(heading, overlap, body)
            records.append({
                "pair": f"{pair.compressed} -> {pair.target}",
                "path": section.path,
                "line": section.line,
                "heading": section.heading,
                "class": kind,
                "best_target": None if match is None else {
                    "path": match.path, "line": match.line, "heading": match.heading,
                    "score_heading": heading, "score_jaccard": overlap, "score_body": body,
                },
                "rules": [] if kind == "DUPLICATE" else rules_of(pair.compressed, lines, section),
            })
    return Report(merged, tuple(records),
                  tuple(sorted(unresolved, key=lambda u: (u.path.lower(), u.line))),
                  tuple(sorted(untargeted, key=lambda u: (u.path.lower(), u.line))))


# --- rendering -------------------------------------------------------------------------------------

CLASSES = (("DELTA", "nothing like it in the target — THIS IS THE LIFT LIST"),
           ("PARTIAL", "the target carries some of it — check what it dropped"),
           ("DUPLICATE", "the target carries it — dedupe, point at the target"))


def render_jsonl(report: Report) -> str:
    return "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in report.records)


def _row(record: dict) -> str:
    target = record["best_target"]
    if target is None:
        where, scores = "no target section scores above zero", "h 0.00 / j 0.00 / b 0.00"
    else:
        where = f"`{target['path']}:{target['line']}` {target['heading']}"
        scores = (f"h {target['score_heading']:.2f} / j {target['score_jaccard']:.2f} "
                  f"/ b {target['score_body']:.2f}")
    return (f"- `{record['path']}:{record['line']}` — {record['heading']} — {where} — "
            f"{scores} — {len(record['rules'])} rule{'' if len(record['rules']) == 1 else 's'}")


def render_md(report: Report) -> str:
    out = [
        "# DOC-OVERLAP — what the compressed docs still hold that the target dropped",
        "",
        "Generated by `python content/video_engine/scripts/report_doc_overlap.py --write`. Do not",
        "hand-edit it: `--check` fails when it drifts from the docs. Pairs are DISCOVERED — from an",
        "`AGENTS.md` sentence, from a doc's own status byline, or from `--pair` — never hard-coded.",
        "",
        "Operator ruling, 2026-09-05: *\"we compressed the docs because we didn't have a proper search",
        "system; now that we do, we shouldn't kill everything in the compressed docs. The right way is",
        "to lift the differences out and dedupe.\"* **DELTA is the lift list.**",
        "",
        "A row is a bullet, not a table row, because the rule lines nest under it. The fields are in",
        "one order: `path:line` — heading — best target `path:line` — scores — rule count. The rules",
        "under a DELTA / PARTIAL row are what gets lifted: a numbered or bulleted item, a line carrying",
        "must / never / always / only / rule / gate, or the lead-in of a ladder.",
        "",
        f"Thresholds: `score_heading` 1.0 on equal normalised headings (>= {MIN_HEADING_CHARS} chars);",
        f"`score_jaccard` over labels + terms + heading tokens; `score_body` = word-level",
        f"`difflib.SequenceMatcher.ratio()` over the section bodies (fences stripped, first",
        f"{BODY_WORDS} words), computed only when `score_jaccard` >= {JACCARD_FLOOR:.2f}.",
        f"DUPLICATE = heading match or body >= {BODY_DUPLICATE:.2f}; PARTIAL = body >= {BODY_PARTIAL:.2f}",
        f"or jaccard >= {JACCARD_PARTIAL:.2f}; DELTA = neither.",
        "",
    ]
    counts = {name: sum(1 for r in report.records if r["class"] == name) for name, _ in CLASSES}
    out += [
        f"{len(report.pairs)} pair(s), {len(report.records)} compressed section(s): "
        f"{counts['DUPLICATE']} duplicate / {counts['PARTIAL']} partial / {counts['DELTA']} delta.",
        "",
    ]
    for pair in report.pairs:
        rows = [r for r in report.records if r["pair"] == f"{pair.compressed} -> {pair.target}"]
        per = {name: [r for r in rows if r["class"] == name] for name, _ in CLASSES}
        out += [
            f"## {pair.compressed} → {pair.target}",
            "",
            f"{len(rows)} sections: {len(per['DUPLICATE'])} duplicate / {len(per['PARTIAL'])} partial"
            f" / {len(per['DELTA'])} delta. Named by `{pair.source}`:",
            "",
            f"> {pair.sentence}",
            "",
        ]
        for name, gloss in CLASSES:
            out += [f"### {name} — {gloss}", ""]
            if not per[name]:
                out += ["_none._", ""]
                continue
            for record in per[name]:
                out.append(_row(record))
                for rule in record["rules"]:
                    out.append(f"    - `:{rule['line']}` {rule['text']}")
            out.append("")
    if report.unresolved:
        out += ["## Unresolved — a marker naming a target that is not in the corpus", ""]
        out += [f"- `{u.path}:{u.line}` — {u.reason} — {u.sentence}" for u in report.unresolved]
        out.append("")
    if report.untargeted:
        out += ["## Markers naming no target — recorded, not paired", ""]
        out += [f"- `{u.path}:{u.line}` — {u.reason} — {u.sentence}" for u in report.untargeted]
        out.append("")
    return "\n".join(out).rstrip("\n") + "\n"


def rendered(root: Path, pairs: list[str] | None = None) -> tuple[Report, dict[str, str]]:
    report = build(root, pairs)
    return report, {JSONL_REL: render_jsonl(report), MD_REL: render_md(report)}


def write(root: Path | str = REPO, pairs: list[str] | None = None) -> Report:
    """Regenerate both artifacts (LF)."""
    root = Path(root)
    report, texts = rendered(root, pairs)
    for rel_path, text in texts.items():
        path = root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text.encode("utf-8"))
    return report


def check(root: Path | str = REPO, pairs: list[str] | None = None) -> list[str]:
    """One entry per stale artifact: "<path> (+added/-removed lines)". Empty means in sync."""
    root = Path(root)
    _, texts = rendered(root, pairs)
    problems: list[str] = []
    for rel_path, want in texts.items():
        path = root / rel_path
        if not path.is_file():
            problems.append(f"{rel_path} (missing)")
            continue
        have = path.read_text(encoding="utf-8")
        if have == want:
            continue
        diff = list(difflib.ndiff(have.splitlines(), want.splitlines()))
        problems.append(f"{rel_path} (+{sum(1 for d in diff if d.startswith('+ '))}"
                        f"/-{sum(1 for d in diff if d.startswith('- '))} lines)")
    return problems


def print_evidence(report: Report) -> None:
    """The pairs with the sentence that named each - the evidence, printed on every run."""
    for pair in report.pairs:
        print(f"report_doc_overlap: PAIR {doc_key(pair.compressed)} -> {doc_key(pair.target)}  "
              f"{pair.compressed} -> {pair.target}")
        print(f"    named by {pair.source}: {pair.sentence}")
    for entry in report.unresolved:
        print(f"report_doc_overlap: UNRESOLVED {entry.path}:{entry.line} - {entry.reason}")
    if report.untargeted:
        print(f"report_doc_overlap: {len(report.untargeted)} marker(s) name no target "
              f"({', '.join(sorted({u.path for u in report.untargeted}))})")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true", help="exit 1 when either artifact is stale (default)")
    ap.add_argument("--write", action="store_true", help="regenerate both artifacts")
    ap.add_argument("--repo", type=Path, default=REPO, help="repository root (default: this checkout)")
    ap.add_argument("--pair", action="append", metavar="COMPRESSED=TARGET", default=[],
                    help="add or override a pair; either side a doc number or a repo-relative path")
    a = ap.parse_args(argv)
    root = a.repo.resolve()
    try:
        report = write(root, a.pair) if a.write else build(root, a.pair)
    except (OSError, ValueError) as exc:
        print(f"report_doc_overlap: ERROR - {exc}")
        return 2
    print_evidence(report)
    counts = {name: sum(1 for r in report.records if r["class"] == name) for name, _ in CLASSES}
    print(f"report_doc_overlap: {len(report.pairs)} pair(s), {len(report.records)} section(s) - "
          f"{counts['DUPLICATE']} duplicate / {counts['PARTIAL']} partial / {counts['DELTA']} delta "
          f"({sum(len(r['rules']) for r in report.records if r['class'] == 'DELTA')} DELTA rule lines)")
    problems = check(root, a.pair)
    if problems:
        print("report_doc_overlap: STALE - " + "; ".join(problems) + " - run --write")
        return 1
    print(f"report_doc_overlap: in sync ({JSONL_REL} + {MD_REL})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
