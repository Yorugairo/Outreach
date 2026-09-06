"""DOCS-TOPICS + DOCS-CITATIONS - the context layer over the docs index.

`build_docs_index.py` answers "where is heading X". This answers the two questions that cost a
handful of tool calls each: "everything we hold about topic X across the corpus" and "what cites
section 42 §42.2". Both are derived from the index and from the docs' own citations - nothing is
inferred, and no output is hand-written.

Three artifacts, all generated:

  docs/DOCS-TOPICS.jsonl     one record per topic key -> every section that carries it
  docs/DOCS-CITATIONS.jsonl  one edge per reference occurrence -> the section it resolves to
  docs/DOCS-TOPICS.md        the top-N topic hubs, with "cited by" from the graph

Usage:

    python content/video_engine/scripts/build_topic_index.py --write
    python content/video_engine/scripts/build_topic_index.py --check      # exit 1 when stale
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
from bisect import bisect_right
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_docs_index as BDI  # noqa: E402  (the token vocabulary is defined once, over there)

INDEX_REL = "docs/DOCS-INDEX.jsonl"
TOPICS_REL = "docs/DOCS-TOPICS.jsonl"
CITATIONS_REL = "docs/DOCS-CITATIONS.jsonl"
HUBS_REL = "docs/DOCS-TOPICS.md"

TOP_DEFAULT = 200        # topic hubs rendered into the Markdown; the JSONL always holds them all
LEAD_MAX = 120           # the hub's lead, shorter than the index's own
SECTION_LIMIT = 12       # sections listed per hub before "and N more"
CITED_LIMIT = 6          # "cited by" entries listed per section
MIN_SECTIONS = 2         # a topic is inter-document by definition
ID_FILES = ("OPERATOR-RULINGS.md", "BACKLOG.md", "CAPABILITIES.md")   # where a bare id is defined
BODY_LEVEL = 6           # levels 1-6 are headings; level 7 is a table row, never an enclosure

# --- topic keys ----------------------------------------------------------------------------

SEPARATOR = re.compile(r"[^\w₀-₉.]+|_+")     # anything that is not a word char joins with -
DASHES = re.compile(r"-{2,}")
EDGES = re.compile(r"^[-.]+|[-.]+$")


def normalise(surface: str) -> str:
    """The topic key: casefolded, surrounding punctuation stripped, `_`/`-`/spaces collapsed to `-`.

    "Min-jerk", "min_jerk" and "  min jerk." are one key; "minimum-jerk" is a different word and
    stays a different key - the merge is surface normalisation, never synonymy."""
    key = DASHES.sub("-", SEPARATOR.sub("-", surface.strip()).casefold())
    return EDGES.sub("", key)


def heading_tokens(heading: str) -> list[str]:
    """The heading's own distinctive tokens - hyphenated, CamelCase, Greek, citations - as
    `build_docs_index` defines them. A path or a code span is not one."""
    spans = [(m.start(), m.end()) for m in BDI.CODE_SPAN.finditer(heading)]
    return [term for _, _, term in sorted(BDI.prose_terms(heading, spans))]


def surfaces_of(rec: dict) -> list[str]:
    """Every surface form one record contributes: its labels, its body terms, its heading tokens."""
    return [*rec.get("labels", []), *rec.get("terms", []), *heading_tokens(rec.get("heading", ""))]


# `build_docs_index` extracts "Flash & Hogan" from "Flash & Hogan (1985)", so the surface that
# reaches us has lost the year: a citation is a name pair, or a name with a year / "et al.".
CITATION_SURFACE = re.compile(
    rf"{BDI.NAME}\s*(?:&|and)\s*{BDI.NAME}(?:\s+(?:et al\.|{BDI.YEAR}))?"
    rf"|{BDI.NAME}\s+(?:et al\.|{BDI.YEAR})"
)


def is_citation(surface: str) -> bool:
    """"Deegan 1997", "Deegan et al.", "Flash & Hogan" - a citation is a topic even in one section."""
    return bool(CITATION_SURFACE.fullmatch(surface.strip()))


def keeps_single(surfaces: set[str]) -> bool:
    """A citation or a formula symbol survives the single-section drop; ordinary prose does not."""
    return any(is_citation(s) or BDI.is_symbol(s.strip()) for s in surfaces)


def section_of(rec: dict) -> dict:
    return {"path": rec["path"], "line": rec["line"], "heading": rec["heading"], "doc": rec["doc"]}


def collect_surfaces(records: list[dict]) -> dict[str, dict]:
    """key -> {"surfaces": set, "sections": {(path, line): section}} before singularisation."""
    out: dict[str, dict] = {}
    for rec in records:
        for surface in surfaces_of(rec):
            key = normalise(surface)
            if not key:
                continue
            entry = out.setdefault(key, {"surfaces": set(), "sections": {}})
            entry["surfaces"].add(surface.strip())
            entry["sections"].setdefault((rec["path"], rec["line"]), section_of(rec))
    return out


def singularise(collected: dict[str, dict]) -> dict[str, dict]:
    """Fold a trailing `s` into the singular, and only when the singular also occurs."""
    original = set(collected)
    merged: dict[str, dict] = {}
    for key in sorted(collected):
        target = key[:-1] if key.endswith("s") and key[:-1] in original else key
        entry = merged.setdefault(target, {"surfaces": set(), "sections": {}})
        entry["surfaces"] |= collected[key]["surfaces"]
        entry["sections"].update(collected[key]["sections"])
    return merged


def build_topics(records: list[dict]) -> list[dict]:
    """One record per topic key, count desc then key; sections by (path, line)."""
    topics: list[dict] = []
    for key, entry in singularise(collect_surfaces(records)).items():
        sections = sorted(entry["sections"].values(), key=lambda s: (s["path"].lower(), s["path"], s["line"]))
        if len(sections) < MIN_SECTIONS and not keeps_single(entry["surfaces"]):
            continue
        aliases = sorted(entry["surfaces"], key=lambda s: (s.casefold(), s))
        topics.append({"topic": key, "aliases": aliases, "sections": sections, "count": len(sections)})
    return sorted(topics, key=lambda t: (-t["count"], t["topic"]))


# --- references ----------------------------------------------------------------------------

# The forms the docs actually use. `(?<![\w:.\-])` keeps a clock ("0:03 S01") or a date from
# reading as a document number. Case-sensitive on purpose: an id is upper-case.
#
# `s` is the corpus' plain-text `§` ("46 s46.4" is "46 §46.4"), so it normalises to the same ref;
# an id may be a letter with a hyphen suffix ("G-j", "V-a"); and "docs 39 and 40" is a list, one
# edge per document, not a reference to 39 alone.
REFERENCE = re.compile(
    r"(?:[Dd]ocs?\s+)?(?<![\w:.\-])(?P<dnum>\d{1,3})(?:\s*§\s*|\s+s)(?P<dsec>[A-Za-z]?\d+(?:\.\d+)*[a-z]?)"
    r"|(?<![\w:.\-])(?P<pnum>\d{1,3})\s+Part\s+(?P<psec>\d{1,2})\b"
    r"|(?<![\w:.\-])(?P<bnum>\d{1,3})\s+(?P<bsec>[A-Z]\d{1,2}[a-z]?)(?![\w])"
    r"|[Dd]ocs?\s+(?P<many>\d{1,3}(?:(?:\s*,\s*(?:and\s+)?|\s+and\s+)\d{1,3})+)(?!\w|\.\d)"
    r"|[Dd]ocs?\s+(?P<only>\d{1,3})(?![\w.])"
    r"|§\s*(?P<bare>\d+(?:\.\d+)*[a-z]?)"
    r"|(?<![\w])(?P<ident>[EGJMSPTR]\d{1,2}[a-z]?)(?![\w])"
    r"|(?<![\w])(?P<hyid>[GVR]-[a-z])(?![\w-])"
)

LIST_NUMBER = re.compile(r"\d{1,3}")     # the document numbers inside a "docs 26, 29, 37" list


def prefix_matcher(token: str) -> re.Pattern:
    """A heading starts with the section token: "42.2 The settle", "Part 3 - ...", "M13 ...".
    "42.21" is not "42.2"."""
    parts = [re.escape(p) for p in token.split() if p]
    return re.compile(r"^\s*" + r"\s*".join(parts) + r"(?![\w.])", re.IGNORECASE)


def depth(path: str) -> int:
    return path.count("/")


def target_order(rec: dict) -> tuple:
    """The shallowest path wins, so `docs/content-video-engine/42-*.md` beats a deep source copy."""
    return (depth(rec["path"]), rec["path"].lower(), rec["path"], rec["line"])


def doc_number(rec: dict) -> int | None:
    doc = rec.get("doc")
    return int(doc) if doc and doc.isdigit() else None


class Resolver:
    """Turns one reference match into its (ref, to) edges - one, or one per document for a list.
    `to` is null when nothing in the index answers."""

    def __init__(self, records: list[dict]) -> None:
        self.records = records
        self.by_doc: dict[int, list[dict]] = {}
        for rec in records:
            number = doc_number(rec)
            if number is not None:
                self.by_doc.setdefault(number, []).append(rec)
        self.ids = [r for r in records if r["path"].rsplit("/", 1)[-1] in ID_FILES]

    @staticmethod
    def _best(candidates: list[dict]) -> dict | None:
        chosen = min(candidates, key=target_order) if candidates else None
        return None if chosen is None else {
            "path": chosen["path"], "line": chosen["line"], "heading": chosen["heading"]}

    def doc_section(self, number: int, token: str) -> dict | None:
        pattern = prefix_matcher(token)
        return self._best([r for r in self.by_doc.get(number, []) if pattern.match(r["heading"])])

    def whole_doc(self, number: int) -> dict | None:
        return self._best(self.by_doc.get(number, []))

    def bare_id(self, ident: str) -> dict | None:
        pattern = prefix_matcher(ident)
        return self._best([r for r in self.ids if pattern.match(r["heading"])])

    def bare_section(self, token: str) -> dict | None:
        """A `§42.2` with no document number resolves only when exactly one heading in the corpus
        starts with it - the resolution is the evidence, so no document is ever guessed."""
        pattern = prefix_matcher(token)
        hits = [r for r in self.records if pattern.match(r["heading"])]
        return self._best(hits) if len(hits) == 1 else None

    def edge(self, m: re.Match) -> list[tuple[str, dict | None]]:
        """The edges one match makes: one, except a multi-doc list, which makes one per document."""
        group = m.groupdict()
        if group["dnum"]:
            number, token = int(group["dnum"]), group["dsec"]
            return [(f"{number}§{token}", self.doc_section(number, token))]
        if group["pnum"]:
            number, token = int(group["pnum"]), f"Part {group['psec']}"
            return [(f"{number}§Part{group['psec']}", self.doc_section(number, token))]
        if group["bnum"]:
            number, token = int(group["bnum"]), group["bsec"]
            return [(f"{number}§{token}", self.doc_section(number, token))]
        if group["many"]:
            numbers = dict.fromkeys(int(n) for n in LIST_NUMBER.findall(group["many"]))
            return [(f"doc{number}", self.whole_doc(number)) for number in numbers]
        if group["only"]:
            number = int(group["only"])
            return [(f"doc{number}", self.whole_doc(number))]
        if group["bare"]:
            token = group["bare"]
            to = self.bare_section(token)
            doc = to and next((r["doc"] for r in self.records
                               if r["path"] == to["path"] and r["line"] == to["line"]), None)
            return [((f"{int(doc)}§{token}" if doc and doc.isdigit() else f"§{token}"), to)]
        if group["ident"]:
            return [(group["ident"], self.bare_id(group["ident"]))]
        if group["hyid"]:
            return [(group["hyid"], self.bare_id(group["hyid"]))]
        return []


def enclosures(records: list[dict]) -> dict[str, list[dict]]:
    """path -> its heading records (levels 1-6) in line order; a table row encloses nothing."""
    out: dict[str, list[dict]] = {}
    for rec in records:
        if rec["level"] <= BODY_LEVEL:
            out.setdefault(rec["path"], []).append(rec)
    for path in out:
        out[path].sort(key=lambda r: r["line"])
    return out


def enclosing(sections: list[dict], line: int, rel_path: str) -> dict:
    """The section a body line sits in; the file's preamble sits in line 0."""
    position = bisect_right([s["line"] for s in sections], line) - 1
    if position < 0:
        return {"path": rel_path, "line": 0, "heading": ""}
    found = sections[position]
    return {"path": rel_path, "line": found["line"], "heading": found["heading"]}


def file_edges(rel_path: str, text: str, sections: list[dict], resolver: Resolver) -> list[dict]:
    """One edge per reference occurrence outside a fenced code block; a multi-doc list, one per
    document it names."""
    out: list[dict] = []
    for i, line in BDI.unfenced(BDI.split_lines(text)):
        for m in REFERENCE.finditer(line):
            for ref, to in resolver.edge(m):
                out.append({"from": enclosing(sections, i + 1, rel_path), "ref": ref, "to": to})
    return out


def build_edges(records: list[dict], repo_root: Path) -> list[dict]:
    """The citation graph over every indexed source file, sorted by (from.path, from.line, ref)."""
    resolver = Resolver(records)
    sections = enclosures(records)
    out: list[dict] = []
    for rel_path in sorted({r["path"] for r in records}):
        path = Path(repo_root) / rel_path
        if not path.is_file():                       # an index record whose file moved: not an error
            continue
        out += file_edges(rel_path, path.read_text(encoding="utf-8"), sections.get(rel_path, []), resolver)
    return sorted(out, key=lambda e: (e["from"]["path"].lower(), e["from"]["path"],
                                      e["from"]["line"], e["ref"]))


def build(records: list[dict], repo_root: Path) -> tuple[list[dict], list[dict]]:
    """(topics, edges) - the whole contract, from index records plus the files they point at."""
    return build_topics(records), build_edges(records, repo_root)


# --- rendering -----------------------------------------------------------------------------

def render_jsonl(rows: list[dict]) -> str:
    return "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows)


def cited_by(edges: list[dict]) -> dict[tuple[str, int], list[str]]:
    """(path, line) -> the distinct "path:line" of the sections citing it; self-mentions are not
    citations."""
    out: dict[tuple[str, int], set[tuple[str, int]]] = {}
    for edge in edges:
        to = edge["to"]
        if not to:
            continue
        source = (edge["from"]["path"], edge["from"]["line"])
        if source == (to["path"], to["line"]):
            continue
        out.setdefault((to["path"], to["line"]), set()).add(source)
    return {key: [f"{path}:{line}" for path, line in sorted(value, key=lambda s: (s[0].lower(), s))]
            for key, value in out.items()}


def render_hubs(topics: list[dict], edges: list[dict], records: list[dict], top: int) -> str:
    leads = {(r["path"], r["line"]): r.get("lead", "") for r in records}
    citations = cited_by(edges)
    shown = topics[:top]
    head = [
        "# DOCS-TOPICS - everything the corpus holds about a topic, and who cites it",
        "",
        "Generated by `python content/video_engine/scripts/build_topic_index.py --write` from",
        f"`{INDEX_REL}` and the docs' own citations. Do not hand-edit it: `--check` fails when it",
        "drifts.",
        "",
        "The recipe - one call per question:",
        "",
        "```bash",
        f"rg -i '\"topic\": \"settle' {TOPICS_REL}      # every section that holds a topic",
        f"rg '\"ref\": \"42§42.2\"' {CITATIONS_REL}      # every section that cites 42 §42.2",
        "```",
        "",
        "A topic key is casefolded, `_`/`-`/space-collapsed, singularised only when the singular",
        "also occurs; `aliases` are the surface forms merged into it. A key held by a single",
        "section is dropped unless it is a citation or a formula symbol. An edge's `ref` is the",
        "reference as normalised (`42§42.2` - which `46 s46.4` also writes - `29§Part3`, `doc47`,",
        "`E38`, `M13`, `G-j`); a list (`docs 39 and 40`) makes one edge per document, and `to` is",
        "null when nothing in the index answers it.",
        "",
        f"{len(topics)} topics, {len(edges)} citation edges. The {len(shown)} largest topics follow,",
        f"at most {SECTION_LIMIT} sections each - the JSONL holds every one.",
        "",
    ]
    body: list[str] = []
    for topic in shown:
        body += [f"## {topic['topic']} ({topic['count']})", ""]
        for section in topic["sections"][:SECTION_LIMIT]:
            lead = BDI.truncate(leads.get((section["path"], section["line"]), ""), LEAD_MAX)
            line = f"- {section['path']}:{section['line']} — {section['heading']}"
            if lead:
                line += f" — {lead}"
            body.append(line)
            sources = citations.get((section["path"], section["line"]), [])
            if sources:
                more = "" if len(sources) <= CITED_LIMIT else f", +{len(sources) - CITED_LIMIT} more"
                body.append("  cited by: " + ", ".join(sources[:CITED_LIMIT]) + more)
        if topic["count"] > SECTION_LIMIT:
            body.append(f"- … {topic['count'] - SECTION_LIMIT} more in `{TOPICS_REL}`")
        body.append("")
    return "\n".join(head + body)


# --- artifacts -----------------------------------------------------------------------------

def load_records(repo_root: Path, index_rel: str = INDEX_REL) -> list[dict]:
    path = Path(repo_root) / index_rel
    if not path.is_file():
        raise FileNotFoundError(f"{index_rel} is missing - run build_docs_index.py --write first")
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def rendered(repo_root: Path, index_rel: str = INDEX_REL, top: int = TOP_DEFAULT) -> dict[str, str]:
    """{relative path: wanted text} for all three artifacts."""
    records = load_records(repo_root, index_rel)
    topics, edges = build(records, Path(repo_root))
    return {
        TOPICS_REL: render_jsonl(topics),
        CITATIONS_REL: render_jsonl(edges),
        HUBS_REL: render_hubs(topics, edges, records, top),
    }


def write(repo_root: Path, index_rel: str = INDEX_REL, top: int = TOP_DEFAULT) -> tuple[int, int]:
    """Regenerate all three artifacts (LF). Returns (topics, edges)."""
    texts = rendered(repo_root, index_rel, top)
    for rel_path, text in texts.items():
        path = Path(repo_root) / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text.encode("utf-8"))
    return texts[TOPICS_REL].count("\n"), texts[CITATIONS_REL].count("\n")


def check(repo_root: Path, index_rel: str = INDEX_REL, top: int = TOP_DEFAULT) -> list[str]:
    """One entry per stale artifact: "<path> (+added/-removed lines)". Empty means in sync."""
    problems: list[str] = []
    for rel_path, want in rendered(repo_root, index_rel, top).items():
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
    ap.add_argument("--check", action="store_true", help="exit 1 when any artifact is stale (default)")
    ap.add_argument("--write", action="store_true", help="regenerate all three artifacts")
    ap.add_argument("--repo", type=Path, default=REPO, help="repository root (default: this checkout)")
    ap.add_argument("--index", default=INDEX_REL, help=f"docs index to read (default: {INDEX_REL})")
    ap.add_argument("--top", type=int, default=TOP_DEFAULT,
                    help=f"topic hubs rendered into {HUBS_REL} (default: {TOP_DEFAULT})")
    a = ap.parse_args(argv)
    root = a.repo.resolve()
    try:
        if a.write:
            topics, edges = write(root, a.index, a.top)
            print(f"build_topic_index: {topics} topic(s), {edges} citation edge(s) -> "
                  f"{TOPICS_REL} + {CITATIONS_REL} + {HUBS_REL}")
        problems = check(root, a.index, a.top)
    except (OSError, ValueError) as exc:                   # a missing/broken index is not staleness
        print(f"build_topic_index: INDEX ERROR - {exc}")
        return 2
    if problems:
        print("build_topic_index: STALE - " + "; ".join(problems) + " - run --write")
        return 1
    print("build_topic_index: in sync")
    return 0


if __name__ == "__main__":
    sys.exit(main())
