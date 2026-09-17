"""THE BASE TABLE (P66 T4) - the AUTHORED beat plan compiled into the approved skeleton, as a table the agent EDITS.

    python content/video_engine/scripts/generate_base_table.py <project> <build> [--aspect 9:16]
        [--table PATH] [--force "<reason>"]
    python content/video_engine/scripts/generate_base_table.py <project> <build> --departures
    python content/video_engine/scripts/generate_base_table.py <project> <build> --bind-cues

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

THE CUT'S CLOSE (E41 / E99 s72). Where the project defines an outro - the Remotion-kit card and the brand line
stitched under it - the base's closing row IS that row: `outro_resolver` READS the project's own `build_short.py`
with `ast` (never runs it) for `OUTRO`, `OUTRO_S`, `OUTRO_LEAD` and the brand line's dials, clocks them through
`authoring.audio.outro_clock` off the take's last word, and `shapes.close_the_cut` writes the clip from `t_outro`
to the runtime with its `life` and the dip into it - the row before it ending at `t_outro`. The `why` names the
outro row, where its values came from, and the brand line's instant (which is stitched into the take, not a row).

THE CUE PLAN (E99 s72). `--bind-cues` binds a BUILT build's cues to what its compiled timeline actually plays
(`authoring.audio.bind_cues`): the audit cue by cue, then the plan and the timeline's `sound` with every cue whose
effect does not fire at its instant DROPPED and named. It runs after the build because the bed's cue plan is
written from the rows before anything is compiled, and a row token is not what the frame plays.

It names no episode: the project, the build, the aspect and every path are arguments, read off disk.
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import lint_species_choice as LSC  # noqa: E402  (TABLE_NAME - what a project's build writes; never re-typed here)
from authoring import audio as A, shapes as SH, table as T  # noqa: E402

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
EPS_RUNTIME = 0.02                            # two runtimes this close are the same runtime (a rounding, not a disagreement)


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


def read_runtime(build: Path) -> float | None:
    """The build's own runtime (`timeline.json` `runtime_s`) - the compiler HOLDS the last row to it with its idle
    (`shapes.close_the_cut`), so no frame after the last row is frozen (the v5 critic: 82.72-88.82 s pixel-identical)."""
    path = build / WORDS_NAME
    if not path.is_file():
        return None
    value = json.loads(path.read_text(encoding="utf-8")).get("runtime_s")
    return float(value) if value else None


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
    worlds = world_resolver(project, build) if project is not None else None
    try:
        return SH.compile(SH.load_plan(plan), read_words(build), SH.DEFAULTS, aspect, runtime=read_runtime(build),
                          pages=page_resolver(project) if project is not None else None, worlds=worlds,
                          outro=outro_resolver(project, build, worlds) if project is not None else None,
                          last_word_end=last_word_end(build))
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


# ---------------------------------------------------------------- the project's own outro (E41 / E99 s72)
#
# The operator, on the generated base v7: *"You didn't attach the outro either."* E41 (2026-09-05): the
# brand line *"Not a panic. Not a plot. Mechanics."* is a CHANNEL ASSET, recorded once and STITCHED under
# the Remotion-kit outro card - so the closing row is the PROJECT's outro clip, not the last page held to
# the runtime. The kit names no episode, so the values are resolved HERE, off the project's own
# `build_short.py` - and READ, never run: the module is parsed with `ast` and its module-level literals are
# evaluated by hand. Importing it would execute an episode's build-time paths and side effects, and running
# `main()` would write the APPROVED cut's own files (`lab_build.py:260` refuses to for the same reason).
OUTRO_BED = "build_short.py"          # where a project keeps the values its own outro row is built from
OUTRO_CONSTS = ("OUTRO", "OUTRO_S", "OUTRO_LEAD", "BRAND_LINE", "BRAND_GAP", "BRAND_TAIL")
OUTRO_NEEDED = ("OUTRO", "OUTRO_S", "OUTRO_LEAD")     # without these three there is no outro row to write
OUTRO_CLIP_FN = "clip"                                # the bed's own `clip(<name>, OUTRO)` helper
OUTRO_SUFFIX = ".mp4"                                 # what `docks.seekable_clip` writes into <build>/clips/


def _const(node, project: Path):
    """One module-level literal of a bed: a number, a string, or a path built off `HERE` (the project).

    The two path shapes a bed writes are `HERE / "<rel>"` and `HERE.parents[<n>] / "<rel>"`; anything
    else returns None and the caller names what it could not read rather than guessing at it."""
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Name) and node.id == "HERE":
        return project
    if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Attribute) \
            and node.value.attr == "parents" and isinstance(node.value.value, ast.Name) \
            and node.value.value.id == "HERE" and isinstance(node.slice, ast.Constant):
        try:
            return project.parents[int(node.slice.value)]
        except (IndexError, TypeError, ValueError):
            return None      # a depth this project does not have, or a subscript that is not an int:
            # unreadable, like anything else this hand evaluator does not understand, and the caller
            # NAMES what it could not read rather than dying on a bed it only meant to parse
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        left, right = _const(node.left, project), _const(node.right, project)
        if isinstance(left, Path) and isinstance(right, str):
            return left / right
    return None


def bed_constants(bed: Path, project: Path, names: tuple[str, ...]) -> dict:
    """The named module-level constants of a bed, READ with `ast` - `a, b = 1, 2` unpacked as the
    module writes it. A name the reader cannot evaluate is simply absent from the result."""
    tree = ast.parse(bed.read_text(encoding="utf-8"), filename=str(bed))
    out: dict = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            pairs = (zip(target.elts, node.value.elts)
                     if isinstance(target, ast.Tuple) and isinstance(node.value, ast.Tuple)
                     else [(target, node.value)])
            for name, value in pairs:
                if isinstance(name, ast.Name) and name.id in names:
                    got = _const(value, project)
                    if got is not None:
                        out[name.id] = got
    return out


def outro_clip_name(bed: Path, fallback: Path) -> str:
    """The NAME the bed's outro row gives its clip - read off its own `clip("<name>", OUTRO)` call, so
    the base points at the file the build already wrote (`docks.seekable_clip` writes it into
    `<build>/clips/`). Absent, the source's own stem at `.mp4`, which is what that helper would make."""
    for node in ast.walk(ast.parse(bed.read_text(encoding="utf-8"), filename=str(bed))):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == OUTRO_CLIP_FN
                and len(node.args) > 1 and isinstance(node.args[0], ast.Constant)
                and isinstance(node.args[1], ast.Name) and node.args[1].id == "OUTRO"):
            return str(node.args[0].value)
    return Path(fallback).with_suffix(OUTRO_SUFFIX).name


def last_word_end(build: Path) -> float | None:
    """The take's LAST WORD - the instant the outro clock is measured from (`build_short.main`:
    `t_vo_end` is the timeline's runtime BEFORE the outro extends it)."""
    words = read_words(build) or []
    ends = [float(w.get("end", w.get("end_s", 0)) or 0) for w in words]
    return round(max(ends), 3) if ends else None


def outro_resolver(project: Path, build: Path, worlds=None) -> dict | None:
    """The project's OWN outro as `shapes.close_the_cut` takes it, or None when it defines none.

    `{world, at, runtime, exit, brand_line_at, source}` - the same values `build_short.main` computes,
    through the same kit function (`authoring.audio.outro_clock`), off the same constants. The runtime
    the BUILD already carries wins when the two disagree, because the take on disk is padded to it."""
    bed = project / OUTRO_BED
    if not bed.is_file():
        return None
    try:
        got = bed_constants(bed, project, OUTRO_CONSTS)
    except SyntaxError as exc:
        raise Refused(f"FAIL: {rel(bed)} cannot be parsed for its outro constants ({exc})") from None
    if any(k not in got for k in OUTRO_NEEDED):
        return None
    t_vo_end = last_word_end(build)
    if t_vo_end is None:
        return None
    brand = got.get("BRAND_LINE")
    line_s, line_note = 0.0, None
    if isinstance(brand, Path) and brand.is_file():
        try:
            line_s = A.probe_duration(brand)
        except (OSError, ValueError) as exc:
            # no ffprobe on PATH (`FileNotFoundError`), a probe that died (`OSError`), or a stream that
            # reports no duration (`float("N/A")`). The brand line is a CHANNEL asset and its length only
            # moves the runtime the clock proposes - the build's own runtime stands over that anyway - so
            # the tool reads it as 0.0, SAYS so in the source, and never crashes the base on it.
            line_s, line_note = 0.0, f"brand line duration unreadable: {exc}"
    gap, tail = float(got.get("BRAND_GAP") or 0.0), float(got.get("BRAND_TAIL") or 0.0)
    at, t_line, runtime = A.outro_clock(t_vo_end, line_s, outro_lead=float(got["OUTRO_LEAD"]),
                                        outro_s=float(got["OUTRO_S"]), brand_gap=gap, brand_tail=tail)
    built = read_runtime(build)
    source = (f"`{rel(bed)}` read with ast (OUTRO {rel(Path(got['OUTRO']))}, OUTRO_S {got['OUTRO_S']}, "
              f"OUTRO_LEAD {got['OUTRO_LEAD']}), clocked by `authoring.audio.outro_clock` off the take's "
              f"last word at {t_vo_end:.2f}s")
    if line_note:
        source += f"; {line_note}"
    if built is not None and abs(float(built) - runtime) > EPS_RUNTIME:
        source += (f"; the BUILD's own runtime ({float(built):.2f}s) stands over the clock's "
                   f"({runtime:.2f}s) - the take on disk is padded to it")
        runtime = round(float(built), 2)
    world = f"clip:{outro_clip_name(bed, Path(got['OUTRO']))}"
    return {"world": str(worlds(world)) if worlds else world, "at": at, "runtime": runtime,
            "exit": SH.OUTRO_EXIT, "brand_line_at": t_line if line_s else None, "source": source}


# ---------------------------------------------------------------- the cues bound to what fires (E99 s72)
#
# The operator, on the generated base v7: *"Sound effects are way off, we're playing spiral and whirls when
# there's no spiral or whirl effect."* The bed's cue map keys every page cue on the ROW TOKEN, and a token
# is not what the frame plays (`authoring.audio.bind_cues` carries the whole finding). The cue plan a
# private build gets is written from the rows BEFORE anything is compiled (`lab_build.write_cue_plan`), so
# the binding has to run AFTER the compile, against the compiled timeline - which is this mode:
#
#     generate_base_table.py <project> <build> --bind-cues [--timeline base.timeline.json]
#
# It prints the audit cue by cue (what it claims, whether that effect fires there), then keeps only the
# bound cues in BOTH places a build carries them - `<build>/SOUND-PLAN.json` (the plan) and the compiled
# timeline's own `sound` list (what the player and `gate_motion_density` read) - and names every firing
# effect the map leaves silent. It ADDS no cue and chooses no file: dropping needs no sound on disk, and
# inventing one is refused by E99 s37.
CUE_PLAN_NAME = "SOUND-PLAN.json"          # `lab_build.CUE_PLAN_NAME` - the PRIVATE plan, never the project's
BASE_TIMELINE_NAME = "base.timeline.json"  # `lab_build.TABLE_TIMELINE_NAME` - what the whole-table mode compiles


def cue_audit(cues: list[dict], timeline: dict) -> list[str]:
    """The audit as a markdown table: one row per cue - its instant, what it claims fires, and what the
    COMPILED timeline actually plays there. This is the evidence; the drop is its consequence.

    Read off `audio.bind_report`, the SAME nearest-first, consume-once pairing the binder applies, so the
    table can never print a YES for a cue the binder then drops (two arrivals of one kind inside the
    tolerance take a cue each, and a third cue on them is the one left over)."""
    out = ["| cue | at | claims | does it fire there? |", "|---|---|---|---|"]
    for r in A.bind_report(cues, timeline)["cues"]:
        key, at, got = r["key"], r["at"], r["fire"]
        if key is None:
            out.append(f"| `{r['cue'].get('slot')}` | {at:.2f} | - (a bed or an unmapped slot) | kept - not this "
                       "binder's to judge |")
            continue
        claim = f"{key['kind']} ({key['what']})" + (f", {key['mass']}" if key.get("mass") else "")
        verdict = (f"YES - {got['kind']} ({got['what']}) at {got['at']:.2f}s on {got['scene']}" if got
                   else f"NO - {r['why']}")
        out.append(f"| `{r['cue'].get('slot')}` | {at:.2f} | {claim} | {verdict} |")
    return out


def refuse_by_name(build: Path) -> None:
    """`build-short*`, by NAME - the same guard the sibling writer carries (`lab_build.refuse_by_name`,
    `lab_build.py:683`), in the same words and off the same constant.

    `--bind-cues` REWRITES a timeline and a cue plan in place, and `build` is whatever the CLI is handed:
    pointed at the episode's `build-short/` with `--timeline timeline.json` it would drop cues out of the
    APPROVED cut. Nothing is read and nothing is written before this."""
    from lab_build import REFUSED_PREFIX        # the one place the name lives (`lab_build.py:138`)
    build = Path(build)
    if build.name.startswith(REFUSED_PREFIX) or any(q.name.startswith(REFUSED_PREFIX) for q in build.parents):
        raise Refused(f"FAIL: {build.name}: this tool never binds cues inside `{REFUSED_PREFIX}*` - that is the "
                      f"approved cut and every watched variant beside it, and a served build is never rewritten "
                      f"under the operator (memory `review-link-frozen-copy`, E99 s11). Bind the PRIVATE build "
                      f"the lab compiled (`lab_build.py --table ... --into ...`)")


def bind_build_cues(build: Path, timeline_name: str) -> int:
    """The build's cues bound to its compiled timeline, in the plan AND in the timeline. Exit 0."""
    refuse_by_name(build)
    tl_path = build / timeline_name
    if not tl_path.is_file():
        raise Refused(f"FAIL: no {rel(tl_path)} - the cues are bound to what the COMPILED timeline plays, "
                      "so the build is compiled first (`lab_build.py --table ... --into ...`)")
    timeline = json.loads(tl_path.read_text(encoding="utf-8"))
    plan_path = build / CUE_PLAN_NAME
    plan = json.loads(plan_path.read_text(encoding="utf-8")) if plan_path.is_file() else None
    embedded = list(timeline.get("sound") or [])
    source = (plan or {}).get("cues") if plan else embedded
    print("\n".join(cue_audit(list(source or []), timeline)))
    kept_tl, dropped_tl = A.bind_cues(embedded, timeline)
    timeline["sound"] = kept_tl
    tl_path.write_text(json.dumps(timeline, indent=1), encoding="utf-8")
    dropped = dropped_tl
    if plan is not None:
        kept, dropped = A.bind_cues(list(plan.get("cues") or []), timeline)
        plan["cues"] = kept
        plan["bound"] = (f"bound to {timeline_name} by generate_base_table.py --bind-cues (E99 s72): every cue "
                         f"whose effect does not fire at its instant is dropped; {len(dropped)} dropped")
        plan_path.write_text(json.dumps(plan, indent=1), encoding="utf-8")
    print(f"\n{rel(tl_path)}: {len(embedded)} cues -> {len(kept_tl)} bound ({len(dropped_tl)} dropped)")
    for d in dropped:
        print(f"  DROPPED {d['slot']} at {d['at']:.2f}s: {d['why']}")
    for note in A.unsounded(kept_tl, timeline):
        print(f"  [sound] {note}")
    if plan is not None:
        print(f"{rel(plan_path)}: {len(plan['cues'])} cues kept")
    return 0


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
    ap.add_argument("--bind-cues", action="store_true",
                    help="write no table: bind the BUILT build's cues to what its compiled timeline plays "
                         "(E99 s72) - the audit, then the plan and the timeline with the unbound cues dropped")
    ap.add_argument("--timeline", default=BASE_TIMELINE_NAME,
                    help=f"--bind-cues' compiled timeline inside the build (default {BASE_TIMELINE_NAME})")
    return ap.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    project, build = args.project.resolve(), args.build.resolve()
    if args.force is not None and not args.force.strip():
        print("FAIL: --force takes a REASON - it is written into BASE-TABLE.md and stays with the cut", file=sys.stderr)
        return 1
    try:
        if args.bind_cues:
            return bind_build_cues(build, args.timeline)
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
