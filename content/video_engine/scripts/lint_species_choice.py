"""Species by sentence - the lint (P50 T1, 2026-09-11). INFO only; it never blocks a build.

The map is docs/content-video-engine/SPECIES-BY-SENTENCE.md: ten sentence ACTS (QUOTES, RANKS, COMPARES, DIVIDES, NAMES,
EXPLAINS, TURNS, BREAKS, SPANS, SETS, RETRACTS) each pointing at the species or verb a shot row should carry. This reads a
project's written shot table (`SHOT-TABLE-SHORT.py`, the `W` literal the build writes) and the build's `timeline.json`
(the take's `sentences` on the clock the docks and captions use), classifies every sentence by a keyword table - crude on
purpose, like V05 - and prints one line per sentence:

    t0-t1 · "the sentence" · ACTS · available: <built species for those acts> · row has: <what fires in the window, or none>

A sentence with an act, an available species and nothing firing is marked `· no row` (INFO, the author's eye). For a
long-form table (runtime >= LONG_FORM_S or --long) it lists every plate row with its `;use=` and WARNs one without (E61:
a plate is a landing surface, a bridge or a reset, and says which; the compiler's PLATE_OPTS learns the token with P51 T0).

    python content/video_engine/scripts/lint_species_choice.py <project dir> [--build <dir>] [--table <py>] [--words <timeline.json>] [--long]
    python content/video_engine/scripts/lint_species_choice.py --when [--md] [--write-doc | --check-doc]

`--when` prints the compiler's `when` on every kind (SPECIES_WHEN / CHART_TO_WHEN); `--write-doc` regenerates the map's
s4 block between the SPECIES_WHEN markers, `--check-doc` exits 1 when the block is stale. Exit 0 otherwise; 2 on usage.
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))   # bare-module import works from any cwd / test runner
import build_scene_timeline_f as B  # noqa: E402
from build_scene_timeline_f import PLATE_USES  # noqa: E402,F401  E61: the compiler owns the tuple; `L.PLATE_USES` still reads

ROOT = Path(__file__).resolve().parents[3]
MAP_DOC = ROOT / "docs/content-video-engine/SPECIES-BY-SENTENCE.md"
DOC_BEGIN, DOC_END = "<!-- SPECIES_WHEN:BEGIN -->", "<!-- SPECIES_WHEN:END -->"
LONG_FORM_S = 180.0          # the script gates' route: a measured clock under 3:00 is a short (E35 / G2)
TABLE_NAME = "SHOT-TABLE-SHORT.py"
DEFAULT_BUILD = "build-short"
TEXT_W = 74

# The keyword table. Crude on purpose (V05's lesson: a classifier the author can read beats one they cannot argue with).
ACT_RE = {
    "QUOTES": r"\b(said|says|saying|announced|pledg\w*|promis\w*|told|wrote|reported|according to|claim\w*|we call this|quot\w+)\b",
    "RANKS": r"\b(biggest|largest|smallest|top|highest|lowest|most|least|number one|rank\w*|the first|the second|the third)\b",
    "COMPARES": r"\b(since|over the (?:last|same|past)|monthly|month by month|a year at a time|each month|every month|climbed|fell|rose|dropped|went up|went down|selling|sold|trend\w*|decade|years?)\b",
    "DIVIDES": r"\b(share of|a tenth|a third|a quarter|half of|percent of|out of every|slice|portion|split|of the pile)\b",
    "NAMES": r"\b(cross\w*|across|through|route|border|port|strait|ship\w*|flow\w*|export\w*|import\w*|went home|brought .* home|from \w+ to \w+)\b",
    "EXPLAINS": r"\b(because|so that|which means|that's why|therefore|when you\w*|when your|works? like|mechanism|the reason|forces?|causes?|compound\w*|discounts?|we call this|funded)\b",
    "BREAKS": r"\b(beats?|dwarfs?|blows? past|breaks|breaks? (?:through|past)|off the chart|times bigger|many times|outgrows?)\b",   # `breaks` the verb only: "tea break" is a noun
    "SPANS": r"\b(between|from .+ to|the gap|distance|spread|over the period|the same months)\b",
    "SETS": r"\b(two numbers|two things|three things|two reasons|here's what|here's where|both numbers|the second number|the first number|second lever)\b",
    "RETRACTS": r"\b(none of this|didn't happen|never happened|isn't the|not the|wasn't|instead|nobody (?:explained|says|on)|not a penny|wrong|myth)\b",
}
TURNS_RE = r"\b(\d[\d,.]*|hundred|thousand|million|billion|trillion|percent|per cent|dollars?|yen|multiple)\b"
ACTS = ("QUOTES", "RANKS", "COMPARES", "DIVIDES", "NAMES", "EXPLAINS", "TURNS", "BREAKS", "SPANS", "SETS", "RETRACTS")
_ACT_RE = {k: re.compile(v, re.I) for k, v in ACT_RE.items()}
_TURNS = re.compile(TURNS_RE, re.I)

# What the map lists as BUILT for each act (SPECIES-BY-SENTENCE.md s1-s2) ...
ACT_SPECIES = {
    "QUOTES": ("record dock", "read->park"),
    "RANKS": ("bars page", "callout", "burst"),
    "COMPARES": ("line page", "build_to", "chart_to:rescale", "chart_to:extend", "figure"),
    "DIVIDES": ("share page", "peel"),
    "NAMES": ("trace",),
    "EXPLAINS": ("note", "plate use=bridge"),
    "TURNS": ("figure", "spotlight", "callout", "note"),
    "BREAKS": ("burst", "stack"),
    "SPANS": ("bracket", "spread", "relight"),
    "SETS": ("chart_to:park", "figure", "retitle"),
    "RETRACTS": ("retitle", "squiggle"),
}
# ... and what it names as pending, by task (s5), so the line says where the better species is.
ACT_PENDING = {
    "QUOTES": "press card T3", "NAMES": "vector map T5", "EXPLAINS": "chips + flow diagram T2", "DIVIDES": "treemap T6",
    "RETRACTS": "crossed-out board T2", "BREAKS": "furniture T10",
}


# ---------------------------------------------------------------- the inputs
def load_table(path: Path) -> list[tuple]:
    """The `W = [...]` literal the build writes (`SHOT-TABLE-SHORT.py`): rows of (start, end, plate, ken, docks, exit[, species[, camera]])."""
    text = path.read_text(encoding="utf-8")
    match = re.search(r"^W = (.*)$", text, re.S | re.M)
    if not match:
        raise ValueError(f"{path}: no `W = [...]` literal")
    rows = ast.literal_eval(match.group(1).strip())
    return [tuple(r) for r in rows]


def load_sentences(path: Path) -> list[dict]:
    """The build's timeline.json (`write_timeline`): `sentences` [{text, start, end}] on the take's clock."""
    data = json.loads(path.read_text(encoding="utf-8"))
    sents = data.get("sentences") or []
    if not sents:
        raise ValueError(f"{path}: no `sentences` (the build writes them from the take's words)")
    return [{"text": s["text"], "start": float(s["start"]), "end": float(s["end"])} for s in sents]


def plate_opts(plate_id: str) -> tuple[str, dict]:
    """`<plate>[;k=v...]` -> (bare, opts). The lint's own parser: it reads `;use=` (E61) before the compiler learns it."""
    bare, *parts = plate_id.split(";")
    opts: dict = {}
    for part in parts:
        if "=" in part:
            k, v = part.split("=", 1)
            opts.setdefault(k, []).append(v) if k == "then" else opts.__setitem__(k, v)
    return bare, opts


def world_of(plate_id: str) -> dict:
    """kind (ledger | clip | plate), the object id and the `;then=` state objects of a ledger row, the plate's `use`."""
    bare, opts = plate_opts(plate_id)
    if bare.startswith(B.LEDGER_PREFIX):
        obj = bare[len(B.LEDGER_PREFIX):].split(":")[0]
        states = [t.split(":")[0] for t in opts.get("then", [])]
        return {"kind": "ledger", "object": obj, "states": states, "use": opts.get("use")}
    if bare.startswith("clip:"):
        return {"kind": "clip", "object": Path(bare[5:]).name, "states": [], "use": opts.get("use")}
    return {"kind": "plate", "object": bare, "states": [], "use": opts.get("use")}


def overflow_of(project: Path, obj: str) -> str | None:
    """`overflow` on the object (E60: burst | stack), or None."""
    p = project / "evidence/objects" / f"{obj}.series.json"
    if not p.is_file():
        return None
    try:
        mode = json.loads(p.read_text(encoding="utf-8")).get("overflow")
    except (OSError, ValueError):
        return None
    return mode if isinstance(mode, str) else None


# ---------------------------------------------------------------- the classifier
def classify(text: str) -> list[str]:
    """The acts a sentence carries, in the map's order. Crude keyword hits; a sentence may carry several."""
    out = [act for act in ACTS if act != "TURNS" and _ACT_RE[act].search(text)]
    if _TURNS.search(text):
        out.append("TURNS")
    return [a for a in ACTS if a in out]


def available(acts: list[str]) -> list[str]:
    out: list[str] = []
    for act in acts:
        for sp in ACT_SPECIES.get(act, ()):
            if sp not in out:
                out.append(sp)
    return out


def pending(acts: list[str]) -> list[str]:
    return [f"{ACT_PENDING[a]} ({a})" for a in acts if a in ACT_PENDING]


# ---------------------------------------------------------------- what the table does in a window
def _in(t, s0: float, s1: float) -> bool:
    return isinstance(t, (int, float)) and s0 <= float(t) < s1


def row_events(rows: list[tuple], s0: float, s1: float, project: Path) -> list[str]:
    """Everything the table fires inside [s0, s1): species (with the chart_to verb and its state's overflow), docks
    entering, worlds starting (with the page's overflow)."""
    out: list[str] = []
    for row in rows:
        start, end, plate = float(row[0]), float(row[1]), row[2]
        world = world_of(plate)
        if _in(start, s0, s1):
            tag = f"world {world['kind']}:{world['object']}"
            if world["kind"] == "ledger":
                mode = overflow_of(project, world["object"])
                if mode:
                    tag += f" ({mode})"
            if world["kind"] == "plate" and world["use"]:
                tag += f" use={world['use']}"
            out.append(tag)
        if end <= s0 or start >= s1:
            continue
        for dock in (row[4] or []):
            if len(dock) >= 3 and _in(dock[2], s0, s1):
                opts = dock[4] if len(dock) > 4 and isinstance(dock[4], dict) else {}
                out.append(f"dock {dock[0]}" + (" (read->park)" if opts.get("read") else "") + (" centred" if opts.get("centre") and not opts.get("read") else ""))
        for sp in (row[6] if len(row) > 6 and row[6] else []):
            if not isinstance(sp, dict) or not _in(sp.get("at"), s0, s1):
                continue
            kind = sp.get("kind")
            if kind == "chart_to":
                verb = sp.get("to")
                tag = f"chart_to:{verb}"
                if verb == "park":
                    tag += f" {sp.get('scale')}" + (" (un-park)" if sp.get("scale") == 1.0 else "")
                if verb in ("recast", "morph") and isinstance(sp.get("state"), int):
                    idx = sp["state"] - 1
                    if 0 <= idx < len(world["states"]):
                        obj = world["states"][idx]
                        mode = overflow_of(project, obj)
                        tag += f" -> {obj}" + (f" ({mode})" if mode else "")
                out.append(tag)
            else:
                out.append(kind + (" hold" if sp.get("dur") == "hold" else ""))
    return out


# ---------------------------------------------------------------- the report
def resolve_inputs(project: Path, build: str | None, table: Path | None, words: Path | None) -> tuple[Path, Path]:
    table = table or project / TABLE_NAME
    words = words or project / (build or DEFAULT_BUILD) / "timeline.json"
    if not table.is_file():
        raise FileNotFoundError(f"no shot table at {table} (the build writes {TABLE_NAME}; --table names another)")
    if not words.is_file():
        raise FileNotFoundError(f"no timeline.json at {words} (--build names the build dir; --words names the file)")
    return table, words


def report(project: Path, build: str | None = None, table: Path | None = None, words: Path | None = None,
           long: bool = False) -> tuple[list[str], dict]:
    table, words = resolve_inputs(project, build, table, words)
    rows, sents = load_table(table), load_sentences(words)
    runtime = max(float(r[1]) for r in rows) if rows else 0.0
    lines = [f"species by sentence · {project.name} · {table.name} + {words.relative_to(project).as_posix()} · {len(sents)} sentences · {len(rows)} rows · {runtime:.1f} s"]
    counts = {"sentences": len(sents), "with_act": 0, "with_row": 0, "no_row": 0, "plates": 0, "plates_unnamed": 0}
    for s in sents:
        acts = classify(s["text"])
        avail, pend, has = available(acts), pending(acts), row_events(rows, s["start"], s["end"], project)
        text = s["text"] if len(s["text"]) <= TEXT_W else s["text"][:TEXT_W - 1] + "…"
        fired = [e for e in has if not e.startswith("world ")]   # a world starting is context, not a species row
        no_row = bool(acts) and bool(avail) and not fired
        counts["with_act"] += bool(acts)
        counts["with_row"] += bool(has)
        counts["no_row"] += no_row
        line = (f"INFO {s['start']:6.2f}-{s['end']:6.2f} · \"{text}\" · {'+'.join(acts) or 'bridge'}"
                f" · available: {', '.join(avail) or '-'}" + (f" (pending: {'; '.join(pend)})" if pend else "")
                + f" · row has: {', '.join(has) or 'none'}" + (" · no row" if no_row else ""))
        lines.append(line)
    lines.append(f"INFO {counts['sentences']} sentences · {counts['with_act']} carry an act · {counts['with_row']} have a row firing"
                 f" · {counts['no_row']} have an available species and no row")
    if long or runtime >= LONG_FORM_S:
        lines.append(f"INFO long form ({runtime:.0f} s): E61 - every plate names its use (;use={'|'.join(PLATE_USES)})")
        for row in rows:
            world = world_of(row[2])
            if world["kind"] != "plate":
                continue
            counts["plates"] += 1
            if world["use"] in PLATE_USES:
                lines.append(f"INFO {float(row[0]):6.2f}-{float(row[1]):6.2f} · plate {world['object']} · use={world['use']}")
            else:
                counts["plates_unnamed"] += 1
                lines.append(f"WARN {float(row[0]):6.2f}-{float(row[1]):6.2f} · plate {world['object']} · no named use"
                             f" (E61: a plate is a landing surface, a bridge or a reset, and says which)")
    return lines, counts


# ---------------------------------------------------------------- the compiler's `when`
def render_when_md() -> str:
    out = ["| kind | when (the sentence that calls for it) |", "|---|---|"]
    for kind in B.SPECIES_KINDS:
        out.append(f"| `{kind}` | {B.SPECIES_WHEN[kind]} |")
    for verb in B.CHART_TO_KINDS:
        out.append(f"| `chart_to` -> `{verb}` | {B.CHART_TO_WHEN[verb]} |")
    return "\n".join(out) + "\n"


def doc_block(text: str) -> tuple[int, int]:
    a, b = text.index(DOC_BEGIN) + len(DOC_BEGIN), text.index(DOC_END)
    return a, b


def sync_doc(write: bool) -> bool:
    """True when the map's s4 block equals the compiler's rendering (after writing, when asked)."""
    text = MAP_DOC.read_text(encoding="utf-8")
    a, b = doc_block(text)
    want = "\n" + render_when_md()
    if text[a:b] == want:
        return True
    if write:
        MAP_DOC.write_text(text[:a] + want + text[b:], encoding="utf-8")
        return True
    return False


# ---------------------------------------------------------------- CLI
def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("project", nargs="?", type=Path, help="the project dir (SHOT-TABLE-SHORT.py + <build>/timeline.json)")
    ap.add_argument("--build", default=None, help=f"the build dir under the project (default {DEFAULT_BUILD})")
    ap.add_argument("--table", type=Path, default=None)
    ap.add_argument("--words", type=Path, default=None, help="a timeline.json with `sentences`")
    ap.add_argument("--long", action="store_true", help="apply E61's plate-use check regardless of runtime")
    ap.add_argument("--when", action="store_true", help="print the compiler's `when` on every kind")
    ap.add_argument("--md", action="store_true", help="with --when: as a Markdown table")
    ap.add_argument("--write-doc", action="store_true", help="regenerate SPECIES-BY-SENTENCE.md s4 from the compiler")
    ap.add_argument("--check-doc", action="store_true", help="exit 1 when SPECIES-BY-SENTENCE.md s4 is stale")
    args = ap.parse_args(argv)
    if args.write_doc or args.check_doc:
        ok = sync_doc(write=args.write_doc)
        print(f"{MAP_DOC.name}: SPECIES_WHEN block {'written' if args.write_doc else ('in sync' if ok else 'STALE - run --write-doc')}")
        return 0 if ok else 1
    if args.when:
        if args.md:
            print(render_when_md(), end="")
        else:
            for kind in B.SPECIES_KINDS:
                print(f"{kind:12s} {B.SPECIES_WHEN[kind]}")
            for verb in B.CHART_TO_KINDS:
                print(f"chart_to:{verb:8s} {B.CHART_TO_WHEN[verb]}")
        return 0
    if args.project is None:
        ap.print_usage()
        return 2
    try:
        lines, _ = report(args.project, args.build, args.table, args.words, args.long)
    except (FileNotFoundError, ValueError) as exc:
        print(f"lint_species_choice: {exc}", file=sys.stderr)
        return 2
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
