"""THE BASE TABLE (P66 T4) - the AUTHORED beat plan compiled into the approved skeleton, as a table the agent EDITS.

    python content/video_engine/scripts/generate_base_table.py <project> <build> [--aspect 9:16]
        [--table PATH] [--force "<reason>"]
    python content/video_engine/scripts/generate_base_table.py <project> <build> --departures

E99 s68: *"the compiler outcome doesn't have to be the final solution, the agent can use it to establish the base of
the video and then modify."* **The output is a BASE, never a cut.** This CLI is the door: it reads the build's
AUTHORED `BEAT-PLAN.jsonl` (M41's schema - the intelligence work E99 s66 reserves to an agent or the operator) and the
take's own words, calls `authoring.shapes.compile`, and writes

  * the rows through `authoring.table.write_shot_table` - the same literal the compiler, the gates and the lint read;
  * `<build>/BASE-TABLE.md` - per row the skeleton chosen, the act that chose it and the rule that applied; the beats
    the plan leaves SILENT; the cut's signature mix beside `effects/skeletons/approved-mix.json`'s measured target;
    and the gaps M16 would MEASURE on the base (never filled here - `recipes.py:1-20`, `PIPELINE.md:33`).

Nothing is filled by count and no beat is invented: a plan M41 would fail is refused by name by `shapes.check_plan`.
Re-running on the same plan and the same take is byte-identical.

THE TWO DOORS the agent then modifies through (P51 T5): the shot table itself, and `<build>/overrides.json`. Every
departure from the base is a numbered decision in the project's `PRODUCTION-LEDGER.md` under "Decisions taken without
the operator (for the watch)", in the fixed format

    N. BASE DEPARTURE - row <n> <what changed>: <why>, <ruling or path:line>

and `--departures` is the reader: it re-generates the base in memory, loads the build's current table, layers the
sidecar through the compiler's own `apply_overrides`, diffs field by field, prints one line per departure (row, field,
base value, final value) and exits 1 naming any departure the ledger does not carry - a departure is documented when a
ledger row names ITS ROW NUMBER and ITS FIELD. A ledger with no such section, when there are departures, exits 1
saying so.

THE TABLE'S PATH. `<project>/SHOT-TABLE-SHORT.py` is where a project's `build_short.py` writes it and where
`table.apply_sidecar` and the compiler read it. A PRIVATE build never writes over the project's approved table
(`lab_build.py:96` writes its own inside the build): pass `--table <build>/SHOT-TABLE-SHORT.py` for one.

It names no episode: the project, the build, the aspect and every path are arguments, read off disk.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lint_species_choice as LSC  # noqa: E402  (TABLE_NAME - what a project's build writes; never re-typed here)
from authoring import shapes as SH, table as T  # noqa: E402

REPO = SH.REPO
PLAN_NAME = "BEAT-PLAN.jsonl"
WORDS_NAME = "timeline.json"                  # the take's words, as the build carries them
BASE_DOC_NAME = "BASE-TABLE.md"
TABLE_NAME = LSC.TABLE_NAME                   # "SHOT-TABLE-SHORT.py" (lint_species_choice.py:51)
OVERRIDES_NAME = T.OVERRIDES_NAME             # "overrides.json" (P51 T5), beside the build it belongs to
MIX_REL = f"{SH.SKELETON_DIR}/{SH.MIX_NAME}"
LEDGER_NAME = "PRODUCTION-LEDGER.md"
LEDGER_SECTION = "Decisions taken without the operator"
DEPARTURE_MARK = "BASE DEPARTURE"
DEPARTURE_FORM = "N. BASE DEPARTURE - row <n> <what changed>: <why>, <ruling or path:line>"
DEPARTURE_RE = re.compile(rf"^\s*(\d+)\.\s+{DEPARTURE_MARK}\s+-\s+row\s+(\d+)\s+(.+?):\s*(.+?),\s*(\S.+)$")
FIELDS = ("start", "end", "plate", "ken_burns", "docks", "exit", "species", "camera")
ASPECTS = ("16:9", "9:16")
DEFAULT_ASPECT = "9:16"                       # the shorts lane R26-171 / R26-172 bind; --aspect 16:9 for a long form
ABSENT = "<no row>"
VALUE_MAX = 160                               # how much of a field's value a departure line prints


class Refused(SystemExit):
    """The tool will not write, or the departures are not all named. The message says which, by name."""


# ---------------------------------------------------------------- the base

def rel(path: Path) -> str:
    """A repo-relative posix path - what BASE-TABLE.md prints, so the document is the same on any machine."""
    path = Path(path).resolve()
    try:
        return path.relative_to(REPO).as_posix()
    except ValueError:
        return path.as_posix()


def read_words(build: Path) -> list | None:
    """The take's words as the build carries them (`<build>/timeline.json`) - the clock every row is timed on."""
    path = build / WORDS_NAME
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8")).get("words")


def page_resolver(project: Path):
    """`pages(<a resolved ledger plate id>) -> that page's `ledger_page.v1` spec` for `shapes.compile`.

    It is the COMPILER's own reader (`build_scene_timeline_f.ledger_world`: the series file under
    `<project>/evidence/objects/`, built into the spec the player draws), so the base places a card
    by the geometry the page will actually have - one placement truth (P50 T16), read here through
    the same door. The kit names no episode; the project is this CLI's own argument."""
    def pages(plate: str):
        C = SH.compiler()
        return (C.ledger_world(C.split_plate_opts(str(plate))[0], (0, 0, 0), project) or {}).get("page")
    return pages


CLIP_DIRS = ("clips", "omni-video/stills", "comfy-video", ".")   # where an episode keeps the clips a plan names


def world_resolver(project: Path, build: Path):
    """The kit's WORLD resolver: the id the plan names -> the id the BUILD can open.

    A read-back plan names the hook's world as the cut recorded it (`clip:clip-a-counter-tab-v2.mp4`),
    and `build_scene_timeline_f` opens a `clip:<path>` relative to the EPISODE (`:3619-3623`). Where a
    clip lives is the episode's business, not the kit's, so the lookup is here: the build's own
    `clips/` first (that is where the seekable copy the cut used is written), then the project's, and
    the id is written back RELATIVE TO THE PROJECT so the table stays portable. An id the project does
    not carry is handed back unchanged - the build then names the file it cannot find, which is the
    honest failure."""
    def worlds(plate: str) -> str:
        pid = str(plate)
        if not pid.startswith("clip:"):
            return pid
        name = pid[len("clip:"):].split(";", 1)[0]
        for root in (build, project):
            for where in CLIP_DIRS:
                p = (root / where / Path(name).name)
                if p.is_file():
                    return "clip:" + p.resolve().relative_to(project.resolve()).as_posix()
        return pid
    return worlds


def compile_base(build: Path, aspect: str, project: Path | None = None) -> tuple[list[tuple], list[dict]]:
    """The build's AUTHORED plan as the approved skeleton. Refusals keep `shapes`' own words.

    With `project`, every card on a page is placed by that page's OWN geometry (`page_resolver`) and
    every world the plan names is resolved to a file this build can open (`world_resolver`); without
    it the compiler's placer decides at compile time and each row's `why` says so."""
    plan = build / PLAN_NAME
    if not plan.is_file():
        raise Refused(f"FAIL: no {PLAN_NAME} in {rel(build)} - the compiler's INPUT is AUTHORED (E99 s66, M41); "
                      "this tool never writes one")
    try:
        return SH.compile(SH.load_plan(plan), read_words(build), SH.DEFAULTS, aspect,
                          pages=page_resolver(project) if project is not None else None,
                          worlds=world_resolver(project, build) if project is not None else None)
    except SH.Refused as exc:
        raise Refused(f"FAIL: {rel(plan)}: {exc}") from None


def table_text(rows: list[tuple], head: str) -> bytes:
    """The literal `table.write_shot_table` would write - built by the kit itself, never re-formatted here."""
    with tempfile.TemporaryDirectory() as tmp:
        return T.write_shot_table(Path(tmp) / TABLE_NAME, rows, head).read_bytes()


def header(build: Path, aspect: str) -> str:
    """The prefix above the rows: what wrote them, from what, and the two doors that change them."""
    return ('"""GENERATED BASE - `generate_base_table.py` from '
            f'`{rel(build / PLAN_NAME)}` (the AUTHORED beat plan, M41) and the take\'s own words, at {aspect}.\n\n'
            "E99 s68: a BASE, never a cut. Edit these rows, or layer `overrides.json` beside the build - and name\n"
            f'every departure in the project\'s {LEDGER_NAME} ("{LEDGER_SECTION}"), in the fixed format\n'
            f"`{DEPARTURE_FORM}`. `generate_base_table.py <project> <build> --departures` reads them back.\n"
            '"""\n')


def signature_mix(why: list[dict]) -> dict:
    """The base's own signature mix: one signature per ROW, as `approved-mix.json` counts one per scene."""
    counts: dict[str, int] = {}
    for w in SH.rows_why(why):
        counts[w["signature"]] = counts.get(w["signature"], 0) + 1
    return counts


def approved_mix() -> dict:
    """`effects/skeletons/approved-mix.json` - MEASURED on the approved cuts (P66 T2), never typed."""
    path = REPO / MIX_REL
    if not path.is_file():
        raise Refused(f"FAIL: no {MIX_REL} - P66 T2 writes it")
    return json.loads(path.read_text(encoding="utf-8"))


def share(count: int, total: int) -> str:
    return f"{count / total:.2f}" if total else "-"


def md_rows(rows: list[tuple], why: list[dict]) -> list[str]:
    """One markdown row per emitted row: the window, the world, and WHY this skeleton (the act, the rule)."""
    out = ["| row | window | world | skeleton | signature | the act that chose it | the rule that applied |",
           "|---|---|---|---|---|---|---|"]
    for n, (row, w) in enumerate(zip(rows, SH.rows_why(why)), start=1):
        docks = len(row[4] or []) if len(row) > 4 else 0
        species = len(row[T.ROW_SPECIES] or []) if len(row) > T.ROW_SPECIES else 0
        out.append(f"| {n} | {row[0]:.2f}-{row[1]:.2f} s | `{row[2]}` ({docks} cards, {species} species) "
                   f"| `{w['skeleton']}` | `{w['signature']}` | beat {w['beat']}: {w['act'] or '-'} | {w['rule']} |")
    return out


def md_mix(mix: dict, approved: dict) -> list[str]:
    """The base's mix beside the approved shorts' measured target (M46's input, never its verdict)."""
    target = approved.get("target") or {}
    counts, shares = target.get("counts") or {}, target.get("shares") or {}
    total, t_total = sum(mix.values()), int(target.get("scenes") or 0)
    out = [f"The base's signature mix ({total} rows) beside the three approved cuts' MEASURED target "
           f"(`{MIX_REL}`, {t_total} scenes; the maximum share one signature reaches inside one approved cut: "
           f"{(approved.get('max_share') or {}).get('value')}).", "",
           "| signature | this base | share | approved | its share |", "|---|---|---|---|---|"]
    for sig in approved.get("signatures") or sorted({*mix, *counts}):
        n, m = mix.get(sig, 0), counts.get(sig, 0)
        out.append(f"| `{sig}` | {n} | {share(n, total)} | {m} | {shares.get(sig, 0):.2f} |")
    return out


def base_doc(project: Path, build: Path, table: Path, rows: list[tuple], why: list[dict],
             aspect: str, forced: str | None) -> str:
    """`<build>/BASE-TABLE.md` - deterministic (no clock in it), so a re-run is byte-identical."""
    silent = SH.silent_why(why)
    gaps = SH.event_gaps(rows)
    lines = [f"# BASE TABLE - {build.name}", "",
             f"Generated by `content/video_engine/scripts/generate_base_table.py {rel(project)} {rel(build)}"
             f" --aspect {aspect}` from [`{PLAN_NAME}`]({PLAN_NAME}) (AUTHORED, M41) and the take's words "
             f"([`{WORDS_NAME}`]({WORDS_NAME})); the rows are written to `{rel(table)}`.", "",
             "**E99 s68: this is a BASE, never a cut.** The author edits these rows (or layers "
             f"`{OVERRIDES_NAME}` beside the build) and names every departure in the project's `{LEDGER_NAME}` "
             f'under "{LEDGER_SECTION}", in the fixed format `{DEPARTURE_FORM}`. '
             "`generate_base_table.py <project> <build> --departures` reads them back.", ""]
    if forced:
        lines += ["**--force**: the table on disk was newer than the plan and was overwritten anyway. "
                  f"The reason given: *{forced}*", ""]
    lines += ["## The rows, and why each skeleton", ""] + md_rows(rows, why) + [""]
    lines += [f"## The beats the plan leaves silent ({len(silent)})", ""]
    if silent:
        lines += ["No move is named for these sentences - the base carries the held world under them. The author's to "
                  "add or to leave (E99 s68); nothing here is filled by count.", ""]
        lines += [f"- beat {w['beat']}: {w['sentence']}" for w in silent] + [""]
    else:
        lines += ["Every beat of the plan names at least one move.", ""]
    lines += ["## The signature mix", ""] + md_mix(signature_mix(why), approved_mix()) + [""]
    lines += [f"## What M16 would MEASURE on the base ({len(gaps)} gaps over {SH.PULSE_MAX_S} s)", "",
              "`shapes.event_gaps` MEASURES; it never fills - a compiler that adds an event to close a gap is an "
              "allocator (`authoring/recipes.py:1-20`, `PIPELINE.md:33`). A gap here is the plan's own silence.", ""]
    lines += ([f"- after {a:.2f} s: {g:.2f} s" for a, g in gaps] if gaps else ["None."]) + [""]
    return "\n".join(lines)


def write_base(project: Path, build: Path, table: Path, aspect: str,
               force: str | None) -> tuple[list[tuple], list[dict]]:
    """The base on disk: the table literal and `BASE-TABLE.md`. Refuses a table NEWER than the plan whose bytes
    differ from the base - that is an edit, and an edit is never overwritten without a named reason."""
    rows, why = compile_base(build, aspect, project)
    text = table_text(rows, header(build, aspect))
    plan = build / PLAN_NAME
    if table.is_file() and table.stat().st_mtime > plan.stat().st_mtime and table.read_bytes() != text:
        if not force:
            raise Refused(f"FAIL: {rel(table)} is NEWER than {rel(plan)} and differs from the base - it has been "
                          "edited (the two doors: the table and the sidecar). Re-generating would drop that work. "
                          'Pass --force "<reason>" to overwrite anyway; the reason is written into '
                          f"{BASE_DOC_NAME}.")
    table.parent.mkdir(parents=True, exist_ok=True)
    table.write_bytes(text)
    doc = build / BASE_DOC_NAME
    doc.write_text(base_doc(project, build, table, rows, why, aspect, force), encoding="utf-8")
    return rows, why


# ---------------------------------------------------------------- the departures

def final_table_path(project: Path, build: Path, explicit: Path | None) -> Path:
    """The table the build actually compiles: `--table`, else the one INSIDE the build (a private build writes its
    own), else the project's - which is where a project's `build_short.py` writes it."""
    if explicit is not None:
        return explicit
    inside = build / TABLE_NAME
    return inside if inside.is_file() else project / TABLE_NAME


def final_rows(project: Path, build: Path, table: Path, aspect: str) -> list[tuple]:
    """The build's rows AS COMPILED: the table's literal with `overrides.json` layered over it - the compiler's own
    `apply_overrides` (the reading half of `table.apply_sidecar`: nothing is written here)."""
    if not table.is_file():
        raise Refused(f"FAIL: no table at {rel(table)} - generate the base first, or name it with --table")
    rows = T.load_rows(table)
    sidecar = build / OVERRIDES_NAME
    if not sidecar.is_file():
        return rows
    import build_scene_timeline_f as C
    overrides = json.loads(sidecar.read_text(encoding="utf-8"))
    if not isinstance(overrides, dict):
        raise Refused(f"FAIL: {rel(sidecar)}: the sidecar is a JSON object keyed by row id and field")
    try:
        return C.apply_overrides(rows, overrides, words=read_words(build), aspect=aspect)
    except ValueError as exc:
        raise Refused(f"FAIL: {rel(sidecar)}: {exc}") from None


def show(value: object) -> str:
    text = repr(value)
    return text if len(text) <= VALUE_MAX else text[:VALUE_MAX - 3] + "..."


def field_value(row, i: int):
    return row[i] if row is not None and len(row) > i else None


def departures(base: list[tuple], final: list[tuple]) -> list[dict]:
    """Every field of every row where the build's table differs from the base - `{row, field, base, final}`,
    in row then field order (the shape `change_report.py` reports a change in: the pair, at the place it touches)."""
    out: list[dict] = []
    for n in range(max(len(base), len(final))):
        b = base[n] if n < len(base) else None
        f = final[n] if n < len(final) else None
        if b is None or f is None:
            out.append({"row": n + 1, "field": "row", "base": ABSENT if b is None else show(b),
                        "final": ABSENT if f is None else show(f)})
            continue
        for i, name in enumerate(FIELDS):
            bv, fv = field_value(b, i), field_value(f, i)
            if bv != fv:
                out.append({"row": n + 1, "field": name, "base": show(bv), "final": show(fv)})
    return out


def ledger_section(project: Path) -> list[str]:
    """The lines of the ledger's "Decisions taken without the operator" section, or a refusal naming what is missing."""
    path = project / LEDGER_NAME
    if not path.is_file():
        raise Refused(f"FAIL: no {rel(path)} - a departure from the base is a decision taken without the operator "
                      f'and is written there, under "{LEDGER_SECTION}", as `{DEPARTURE_FORM}`')
    out, inside = [], False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("#"):
            inside = LEDGER_SECTION.lower() in line.lower()
            continue
        if inside:
            out.append(line)
    if not out:
        raise Refused(f'FAIL: {rel(path)} has no "{LEDGER_SECTION}" section - a departure from the base is written '
                      f"there as `{DEPARTURE_FORM}`")
    return out


def ledger_entries(project: Path) -> tuple[list[dict], list[str]]:
    """The section's `BASE DEPARTURE` rows as `{row, what}`, and every row that carries the mark in the wrong form."""
    entries, malformed = [], []
    for line in ledger_section(project):
        if DEPARTURE_MARK not in line:
            continue
        m = DEPARTURE_RE.match(line)
        if m is None:
            malformed.append(line.strip())
            continue
        entries.append({"row": int(m.group(2)), "what": m.group(3), "why": m.group(4), "cite": m.group(5)})
    return entries, malformed


def documented(dep: dict, entries: list[dict]) -> bool:
    """A departure is named when a ledger row names ITS ROW NUMBER and ITS FIELD (the `<what changed>` half)."""
    word = re.compile(rf"\b{re.escape(dep['field'])}\b", re.IGNORECASE)
    return any(e["row"] == dep["row"] and word.search(e["what"]) for e in entries)


def report_departures(project: Path, build: Path, table: Path, aspect: str) -> int:
    """One line per departure, then the verdict: 1 when any is unnamed (or the ledger cannot answer), else 0."""
    base, _ = compile_base(build, aspect, project)
    final = final_rows(project, build, table, aspect)
    found = departures(base, final)
    print(f"{rel(table)} vs the base generated from {rel(build / PLAN_NAME)}: {len(found)} departures "
          f"({len(base)} base rows, {len(final)} final rows)")
    for d in found:
        print(f"  row {d['row']} {d['field']}: base {d['base']} -> final {d['final']}")
    if not found:
        print(f"CLEAN: the build's table IS the base - nothing to name in {LEDGER_NAME}.")
        return 0
    entries, malformed = ledger_entries(project)
    for line in malformed:
        print(f"  ledger row not in the fixed format `{DEPARTURE_FORM}`: {line}")
    unnamed = [d for d in found if not documented(d, entries)]
    for d in unnamed:
        print(f"UNNAMED: row {d['row']} {d['field']} is not in {rel(project / LEDGER_NAME)} "
              f'"{LEDGER_SECTION}" - add `{DEPARTURE_FORM}`')
    if unnamed or malformed:
        print(f"FAIL: {len(unnamed)} of {len(found)} departures are unnamed"
              + (f" and {len(malformed)} ledger rows are malformed" if malformed else ""))
        return 1
    print(f"OK: all {len(found)} departures are named in {rel(project / LEDGER_NAME)} "
          f"({len(entries)} {DEPARTURE_MARK} rows).")
    return 0


# ---------------------------------------------------------------- the CLI

def parse_args(argv: list[str] | None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("project", type=Path, help="the episode directory (its PRODUCTION-LEDGER.md and its table)")
    ap.add_argument("build", type=Path, help="the build directory (its BEAT-PLAN.jsonl, its take, its BASE-TABLE.md)")
    ap.add_argument("--aspect", choices=ASPECTS, default=DEFAULT_ASPECT)
    ap.add_argument("--table", type=Path, default=None,
                    help=f"the table to write / read (default: <project>/{TABLE_NAME}; a PRIVATE build names its own)")
    ap.add_argument("--force", metavar="REASON", default=None,
                    help="overwrite a table newer than the plan; the REASON is recorded in BASE-TABLE.md")
    ap.add_argument("--departures", action="store_true",
                    help="write nothing: diff the build's table (and its sidecar) against the base, read the ledger")
    return ap.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    project, build = args.project.resolve(), args.build.resolve()
    if args.force is not None and not args.force.strip():
        print("FAIL: --force takes a REASON - it is written into BASE-TABLE.md and stays with the cut", file=sys.stderr)
        return 1
    try:
        if args.departures:
            return report_departures(project, build, final_table_path(project, build, args.table), args.aspect)
        table = args.table if args.table is not None else project / TABLE_NAME
        rows, why = write_base(project, build, table.resolve(), args.aspect, args.force)
    except Refused as exc:
        print(str(exc), file=sys.stderr)
        return 1
    mix = ", ".join(f"{k} {v}" for k, v in sorted(signature_mix(why).items()))
    print(rel(table))
    print(rel(build / BASE_DOC_NAME))
    print(f"{len(rows)} rows | {len(SH.silent_why(why))} silent beats | mix: {mix} | "
          f"{len(SH.event_gaps(rows))} gaps over {SH.PULSE_MAX_S} s (MEASURED, never filled)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
