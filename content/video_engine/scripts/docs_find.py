"""One compact line per hit across the docs retrieval layers - the query side of `build_docs_layers.py`.

The layers fixed accuracy and cut hops (round 4, `evals/RETRIEVAL-BENCHMARK-2026-09-05.md`), but tokens
rose 16 %: an `rg` on a layer returns the WHOLE JSONL record - an index record carries lead, labels and up
to a dozen body terms; a manifest record carries every heading, label and lead in the document. An agent
needs the locator and one line of context, then a `sed -n` window where it decides to read.

    python content/video_engine/scripts/docs_find.py "minimum-jerk"
    python content/video_engine/scripts/docs_find.py "hedged yield" --layer manifest --limit 4
    python content/video_engine/scripts/docs_find.py "G15b" --layer gates --json

Default `--layer all` scans manifest -> index -> topics -> gates -> animation -> craft, cheapest first, and
stops once `--limit` hits are printed. Two rules keep the cheap layer from eating the whole budget and the
research bundle from burying the doctrine, because both make the cap useless in practice:

  * each layer takes a fair share of what is left (`ceil(remaining / layers left)`, at least one), an
    unused share flows forward, and whatever the thin layers leave over goes back to the cheapest layer
    that still has hits - so a five-hit budget answers from five layers, and still spends all five;
  * inside a layer, hits under `docs/` rank before every other root - the doctrine tree is the answer, the
    `content/video_engine/sources/` research bundle is the background - and file order breaks ties.

The citation graph (`cites`) is not in `all`: it answers "what cites section Y", which is a follow-up, not a
first lookup. Ask for it with `--layer cites`. A missing layer file prints one line and never raises; the
term is compiled as a case-insensitive regex and falls back to a literal when it is not valid regex, so
`42§42.2` and `f(t) = t^2` are searchable as typed. Standard library only.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable, Sequence

SCRIPTS = Path(__file__).resolve().parent
REPO = SCRIPTS.parents[2]

MAX_LINE = 220
SNIPPET_CHARS = 100
NAME_CHARS = 80
TOPIC_SECTIONS = 6
WINDOW = 20
DEFAULT_LIMIT = 20
SEP = " — "
ELLIPSIS = "…"
DOCS_ROOT = "docs/"


# --------------------------------------------------------------------------- record helpers

def dig(record: Any, dotted: str) -> Any:
    """`dig(rec, "source.path")` - the nested value, or None if any hop is missing."""
    value = record
    for key in dotted.split("."):
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    return value


def strings(value: Any) -> list[str]:
    """Every string inside a field, whether it is a string, a list, or a list of dicts."""
    if value is None or isinstance(value, bool):
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, (int, float)):
        return [str(value)]
    if isinstance(value, (list, tuple)):
        return [text for item in value for text in strings(item)]
    if isinstance(value, dict):
        return [text for item in value.values() for text in strings(item)]
    return []


def trim(text: Any, width: int) -> str:
    """One whitespace-collapsed line, at most `width` characters, elided when it is cut."""
    flat = " ".join(str(text or "").split())
    if width <= 0 or not flat:
        return ""
    if len(flat) <= width:
        return flat
    return flat[: max(1, width - 1)].rstrip() + ELLIPSIS


def locate(path: Any, line: Any) -> str:
    """`path:line`, or just the path when the record has no line."""
    if not path:
        return "?"
    return f"{path}:{line}" if line else str(path)


# --------------------------------------------------------------------------- layer definitions

@dataclass(frozen=True)
class Layer:
    """One JSONL artifact: what to search in it, and how one of its records reads as a line."""
    name: str
    rel: str
    fields: tuple[str, ...]
    name_of: Callable[[dict], str]
    detail_of: Callable[[dict], str]
    path_of: Callable[[dict], str]
    line_of: Callable[[dict], Any] = lambda record: None
    token_fields: tuple[str, ...] = ()
    detail_only: bool = False


def first_of(record: dict, *dotted: str) -> str:
    for key in dotted:
        value = dig(record, key)
        if value not in (None, "", [], {}):
            return " ".join(strings(value))
    return ""


LAYERS: tuple[Layer, ...] = (
    Layer(
        "manifest", "docs/DOCS-MANIFEST.jsonl",
        ("title", "purpose", "defines", "headings", "labels", "leads", "key_terms"),
        name_of=lambda r: str(r.get("title") or ""),
        detail_of=lambda r: str(r.get("purpose") or ""),
        path_of=lambda r: str(r.get("path") or ""),
        detail_only=True,
    ),
    Layer(
        "index", "docs/DOCS-INDEX.jsonl", ("heading", "lead", "labels", "terms"),
        name_of=lambda r: str(r.get("heading") or ""),
        detail_of=lambda r: str(r.get("lead") or ""),
        path_of=lambda r: str(r.get("path") or ""),
        line_of=lambda r: r.get("line"),
        token_fields=("labels", "terms"),
    ),
    Layer(
        "topics", "docs/DOCS-TOPICS.jsonl", ("topic", "aliases"),
        name_of=lambda r: str(r.get("topic") or ""),
        detail_of=lambda r: "",
        path_of=lambda r: str(dig(r, "sections") and r["sections"][0].get("path") or ""),
    ),
    Layer(
        "cites", "docs/DOCS-CITATIONS.jsonl", ("ref",),
        name_of=lambda r: str(dig(r, "from.heading") or ""),
        detail_of=lambda r: str(r.get("ref") or ""),
        path_of=lambda r: str(dig(r, "from.path") or ""),
        line_of=lambda r: dig(r, "from.line"),
    ),
    Layer(
        "gates", "docs/GATES-REGISTRY.jsonl", ("id", "rule"),
        name_of=lambda r: str(r.get("id") or ""),
        detail_of=lambda r: first_of(r, "rule", "tool"),
        path_of=lambda r: str(dig(r, "source.path") or ""),
        line_of=lambda r: dig(r, "source.line"),
    ),
    Layer(
        "animation", "docs/ANIMATION-REGISTRY.jsonl", ("name", "expr", "module"),
        name_of=lambda r: str(r.get("name") or ""),
        detail_of=lambda r: first_of(r, "expr", "signature", "value"),
        path_of=lambda r: str(r.get("path") or r.get("module") or ""),
        line_of=lambda r: r.get("line"),
    ),
    Layer(
        "craft", "docs/CRAFT-MAP.jsonl", ("device", "what"),
        name_of=lambda r: str(r.get("device") or ""),
        detail_of=lambda r: str(r.get("what") or ""),
        path_of=lambda r: str(dig(r, "defined_in") and r["defined_in"][0].get("path") or ""),
        line_of=lambda r: dig(r, "defined_in") and r["defined_in"][0].get("line"),
    ),
)

BY_NAME = {layer.name: layer for layer in LAYERS}
ALL_ORDER = ("manifest", "index", "topics", "gates", "animation", "craft")
CHOICES = (*(layer.name for layer in LAYERS), "all")


# --------------------------------------------------------------------------- matching

@dataclass(frozen=True)
class Hit:
    layer: str
    path: str
    line: Any
    name: str
    snippet: str
    text: str
    sections: tuple[tuple[str, Any], ...] = ()

    def as_dict(self) -> dict:
        record = {"layer": self.layer, "path": self.path, "line": self.line,
                  "name": self.name, "snippet": self.snippet, "line_text": self.text}
        if self.sections:
            record["sections"] = [{"path": p, "line": ln} for p, ln in self.sections]
        return record


def build_pattern(term: str) -> re.Pattern[str]:
    """The term as a case-insensitive regex; a literal when it is not valid regex."""
    try:
        return re.compile(term, re.IGNORECASE)
    except re.error:
        return re.compile(re.escape(term), re.IGNORECASE)


def read_records(path: Path) -> Iterable[dict]:
    """Every well-formed JSON object in the file; a corrupt line is skipped, never raised."""
    with path.open(encoding="utf-8") as handle:
        for raw in handle:
            raw = raw.strip()
            if not raw:
                continue
            try:
                record = json.loads(raw)
            except json.JSONDecodeError:
                continue
            if isinstance(record, dict):
                yield record


def matched_field(record: dict, layer: Layer, pattern: re.Pattern[str]) -> tuple[str, str] | None:
    """The first searchable (field, string) in this record that the pattern hits, in field order."""
    for name in layer.fields:
        for text in strings(record.get(name)):
            if pattern.search(text):
                return name, text
    return None


def compose(layer: str, locator: str, name: str, snippet: str) -> str:
    """`[layer] path:line - name - snippet`, name and snippet shrunk to fit `MAX_LINE`."""
    parts = [f"[{layer}] {locator}"]
    room = MAX_LINE - len(parts[0])
    for text, width in ((name, NAME_CHARS), (snippet, SNIPPET_CHARS)):
        cut = trim(text, min(width, room - len(SEP)))
        if cut:
            parts.append(cut)
            room -= len(cut) + len(SEP)
    line = SEP.join(parts)
    return line if len(line) <= MAX_LINE else line[: MAX_LINE - 1] + ELLIPSIS


def docs_first(path: str) -> int:
    return 0 if str(path).startswith(DOCS_ROOT) else 1


def topic_hit(record: dict, layer: Layer) -> Hit:
    """A topic reads as its name, its section count, and the first few sections, docs first."""
    sections = sorted((s for s in record.get("sections") or [] if isinstance(s, dict)),
                      key=lambda s: docs_first(s.get("path", "")))
    pairs = tuple((str(s.get("path") or ""), s.get("line")) for s in sections)
    topic = layer.name_of(record)
    count = record.get("count", len(pairs))
    head = f"[{layer.name}] {topic}{SEP}{count} section{'' if count == 1 else 's'}"
    shown: list[str] = []
    for path, line in pairs[:TOPIC_SECTIONS]:
        entry = locate(path, line)
        if len(head) + len(SEP) + len(", ".join([*shown, entry])) > MAX_LINE:
            break
        shown.append(entry)
    text = head + (SEP + ", ".join(shown) if shown else "")
    return Hit(layer.name, pairs[0][0] if pairs else "", None, topic, "", text, pairs[:TOPIC_SECTIONS])


def record_hit(record: dict, layer: Layer, field_name: str, field_text: str) -> Hit:
    """One layer record as one line.

    The matched field is the context - except when it carries no context of its own: the document
    title, a bare index term, a label. Then the layer's own summary (purpose, lead, rule, formula)
    is worth more than echoing the query back at the reader."""
    name = layer.name_of(record)
    detail = layer.detail_of(record)
    thin = layer.detail_only or field_name in layer.token_fields or field_text.strip() == name.strip()
    snippet = (detail or field_text) if thin else field_text
    path, line = layer.path_of(record), layer.line_of(record)
    return Hit(layer.name, path, line, name, snippet,
               compose(layer.name, locate(path, line), name, snippet))


def scan_layer(layer: Layer, pattern: re.Pattern[str], repo: Path) -> list[Hit] | None:
    """Every hit in one layer, docs-tree paths first; None when the artifact is not built."""
    path = repo / layer.rel
    if not path.is_file():
        return None
    hits: list[Hit] = []
    for record in read_records(path):
        matched = matched_field(record, layer, pattern)
        if matched is None:
            continue
        hits.append(topic_hit(record, layer) if layer.name == "topics"
                    else record_hit(record, layer, *matched))
    return sorted(hits, key=lambda hit: docs_first(hit.path))


# --------------------------------------------------------------------------- the search

@dataclass
class Result:
    hits: list[Hit]
    missing: list[str]
    scanned: list[str]
    truncated: bool
    lines: list[str]


def share_of(remaining: int, layers_left: int) -> int:
    """This layer's slice of what is left: an even split, at least one, unused slack flows on."""
    return max(1, -(-remaining // max(1, layers_left)))


def search(term: str, layer_names: Sequence[str], repo: Path, limit: int) -> Result:
    """Scan the layers in order on a shared budget, then render them grouped, in the same order."""
    pattern = build_pattern(term)
    result = Result(hits=[], missing=[], scanned=[], truncated=False, lines=[])
    found: dict[str, list[Hit]] = {}
    taken: dict[str, int] = {}
    remaining = limit
    for position, name in enumerate(layer_names):
        if remaining <= 0:
            result.truncated = True
            break
        result.scanned.append(name)
        hits = scan_layer(BY_NAME[name], pattern, repo)
        if hits is None:
            result.missing.append(name)
            continue
        found[name] = hits
        taken[name] = min(share_of(remaining, len(layer_names) - position), remaining, len(hits))
        remaining -= taken[name]
    top_up(found, taken, result.scanned, remaining)
    render(result, found, taken)
    return result


def top_up(found: dict[str, list[Hit]], taken: dict[str, int], scanned: Sequence[str],
           remaining: int) -> None:
    """Budget a thin layer did not use goes back to the cheapest layer that still has hits."""
    for name in scanned:
        if remaining <= 0:
            return
        extra = min(remaining, len(found.get(name, ())) - taken.get(name, 0))
        if extra > 0:
            taken[name] += extra
            remaining -= extra


def render(result: Result, found: dict[str, list[Hit]], taken: dict[str, int]) -> None:
    for name in result.scanned:
        if name in result.missing:
            result.lines.append(f"[{name}] not built (run build_docs_layers.py --write)")
            continue
        kept = found[name][: taken[name]]
        result.truncated = result.truncated or len(found[name]) > len(kept)
        result.hits.extend(kept)
        result.lines.extend(hit.text for hit in kept)


def next_window(hits: Sequence[Hit]) -> str:
    """The `sed -n` window of the first index hit - the one locator worth opening next."""
    for hit in hits:
        if hit.layer == "index" and hit.path and isinstance(hit.line, int):
            return f"sed -n {max(1, hit.line - WINDOW)},{hit.line + WINDOW}p {hit.path}"
    return ""


def summary_line(result: Result) -> str:
    count = f"{len(result.hits)}{'+' if result.truncated else ''}"
    scanned = ", ".join(result.scanned) or "no layers"
    window = next_window(result.hits)
    return f"{count} hit(s) in {scanned}" + (f"; next: {window}" if window else "")


def render_json(term: str, result: Result) -> str:
    payload = {
        "query": term,
        "layers_scanned": result.scanned,
        "missing": result.missing,
        "count": len(result.hits),
        "truncated": result.truncated,
        "next": next_window(result.hits) or None,
        "hits": [hit.as_dict() for hit in result.hits],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


# --------------------------------------------------------------------------- cli

def use_utf8(*streams) -> None:
    """The layers carry em dashes and section signs; a cp1252 console must not kill the answer."""
    for stream in streams:
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError, OSError):
            pass


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("term", help="case-insensitive substring or regex")
    parser.add_argument("--layer", choices=CHOICES, default="all",
                        help="one layer, or all (default: manifest, index, topics, gates, animation, craft)")
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT,
                        help=f"most hits to print across every layer (default: {DEFAULT_LIMIT})")
    parser.add_argument("--json", action="store_true", help="the same hits as one JSON object")
    parser.add_argument("--repo", type=Path, default=REPO, help="repository root (default: this checkout)")
    args = parser.parse_args(argv)

    use_utf8(sys.stdout, sys.stderr)
    names = list(ALL_ORDER) if args.layer == "all" else [args.layer]
    result = search(args.term, names, Path(args.repo), max(0, args.limit))
    if args.json:
        print(render_json(args.term, result))
        return 0
    for line in result.lines:
        print(line)
    print(summary_line(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
