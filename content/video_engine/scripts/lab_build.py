"""THE RECIPE LAB - the test-bed builder and the gate + probe filter (P65 T3, R26-176).

    python content/video_engine/scripts/lab_build.py --batch smoke-r1 --candidates lab:return:0a1b2c3d,...
    python content/video_engine/scripts/lab_build.py --batch smoke-r1 --shape return
    python content/video_engine/scripts/lab_build.py --batch smoke-r1 --check

THE RECONCILIATION, and this module's only licence (`authoring/recipes.py:1-20`, `PIPELINE.md:33`): **the lab builds
CANDIDATES on a TEST BED for the operator's judgement; it authors no episode, it fills no slot by count, and nothing
it builds reaches a cut except as a `proven` recipe or a tracked DEFAULT an author may still refuse.** E99 s66: the
beat plan and the script are INTELLIGENCE work, never a tool's - so this tool never CHOOSES a beat. The shape -> beat
map below is written by hand, one entry per shape, each carrying the Tokyo sentence it is owed in and the reason.

A CANDIDATE IS A SCENE, NEVER A FIXTURE (E99 s60: *"what the operator watches must be a beat a short could carry; a
held fixture is a test, not a proof"*). So a candidate is planted INTO the approved Tokyo cut:

  1. the bed's own AUTHORED rows come from `tokyo-tea-break/build_short.py`'s `shot_table` - its take, its words, its
     assets, its docks, its series. Nothing is invented here and no figure is typed;
  2. the shape's window is read off the bed's own BEAT PLAN (`build-short/BEAT-PLAN.jsonl`, P66 T7): the sentence the
     shape is owed in, its `t0` and `t1`. A window no sentence covers is REFUSED BY NAME (E99 s60);
  3. the rows inside that window are replaced by rows written from the candidate's MEMBERS - each member's card to its
     row token by the catalogue's own `author.key` (`docs/EFFECTS-CATALOG.jsonl` through `authoring/effects.py`), each
     member's offset to `window.t0 + offset_s`, each bind filled from the BED's own assets. Every other approved row
     is kept as authored (a row the window cuts into is clipped, and the species and docks the clip drops go with it);
  4. the table is written through `authoring.table.write_shot_table` into a PRIVATE build dir and compiled with
     `no_receipt="recipe lab candidate <id>"` - the compile door's NAMED escape (P67 T2), recorded in the manifest.

THE REFUSALS (memory `review-link-frozen-copy`, E99 s11: a served build is never rebuilt under the operator):
`build-short*` by name, any dir outside the batch's own `build-lab-<batch>/`, and a dir a `serve_player.py` is
answering for (the listening ports are probed and identified by their own `player.json`; neither `serve_player.py`
nor `build_review_queue.py` keeps a port registry on disk, so identification is by content, and a port that cannot
be identified is NAMED on stdout rather than guessed at).

THE FILTER runs four tools, in this order, and RE-IMPLEMENTS NONE of them - each is a subprocess whose
`[LEVEL] Mxx text` rows are parsed with `self_watch.parse_gate`, the protocol's own reader:

    self_watch.py <build> --project <ep>      the fresh probe, FIRST (P51 T3)
    gate_motion_density.py <build>            M01-M34
    gate_one_shot_floor.py <build>            M35-M46, the whole-cut floors
    probe.py <build> <t0> <t0+M16> <t1> --sheet <build>/lab-sheet.png     the candidate's OWN instants

THE FILTER DECIDES ON THE WINDOW (P65 T3, the first smoke batch's own finding). A candidate is ONE beat spliced into
an APPROVED cut, so the rows that fire in the rest of that cut are the BED's, not the candidate's: batch `smoke-r1`
killed both of its candidates on M35 / M37 / M39 (whole-cut floors), on M28 at 0:25 and on M34 at 1:10 - none of
them inside either beat. So the DIAGNOSIS is decided ONLY by the rows whose own instants fall inside the candidate's
window `[t0, t1]`: a FAIL inside the window names the HOLE IN THE BEAT, a WARN inside the window is RECORDED, and
everything else - the one-shot floors (`gate_one_shot_floor.ROW_ORDER`, read over the whole cut by definition) and
every row whose instants land elsewhere - is carried under `context` and decides nothing. A row's instants are the
ones it PRINTS (`row_instants`: `t=` / `at 9.51s`, an `m:ss` stamp, a `41.1-49.9` span, and the span of any scene it
names off the build's own timeline); a row that prints none is whole-cut. A TOOL row (`compile`, `probe`, the bar)
always decides: a build that did not compile or render is not a candidate at all.

THE FILTER DIAGNOSES, IT NEVER KILLS (E99 s69, the operator 2026-09-17: *"they shouldn't be dismissing our
effects/recipes, they should be guiding us on how to build with them"*). Every record carries a `diagnosis`:
`buildable as-is` (no row decided), `buildable with a companion - <what the row asks for and where>` (a row fires
after the recipe's last member has LANDED, or a layout row whose fix is placement - the hole in the beat, named),
or `not on this bed - <the missing member>` (a bind this bed has not got). `survivor` stays as a DERIVED field for
the readers written against it, true for both buildable answers.

`batches/<batch>.jsonl` then carries one record per candidate: the beat it was planted in with its sentence, the
build dir, the clip window a card would show, the sheets, the `no_receipt` reason, the `diagnosis`, `decided_by`
(every FAIL / WARN row INSIDE the window, verbatim) and `context` (every one that is not). A candidate a gate FAILs
is recorded with the row it names, never dropped; a compile the door or the compiler refuses is recorded the same
way, as a `[FAIL] compile` row. The record dir is `effects/lab/batches/` and not `runs/`: `.gitignore` carries
a bare `runs/` rule that swallows any directory of that name, and the batch record is a TRACKED artifact of this
plan (acceptance 2, and T8 leans on it).

R26-168 IS VISIBLE HERE AND IS NOT WORKED AROUND: the Tokyo bed's own proven-recipe coverage is 2 fires over 25
beats, so every build made from that bed carries M38's number, candidate or not. This tool reads the row EXACTLY as
the gate prints it - since P65 T7 that is the interim WARN naming R26-168, and before it was a FAIL - and it fits no
threshold to our own work, holds no waiver list and has no opinion about which rows are the bed's (memory
`thresholds-from-the-reference`). The record shows the row; the parent reads it.

THE WHOLE-TABLE MODE (P66 HG1):

    python content/video_engine/scripts/lab_build.py --table <a shot table> --into <build dir> --label <text>

A candidate is ONE beat spliced into the approved cut; a generated BASE is a WHOLE table (`generate_base_table.py`,
P66 T4) and has no window. The mode takes that table as it stands - `authoring.table.load_rows`, never a row written
here - and builds the same bed around it: `build_short.py` imported with `TOKYO_BUILD_DIR` on the PRIVATE dir, its
OWN registration run (the take copied, the pauses applied, the outro clock, the caption pages, the dock and chart
assets its `shot_table` registers) and ITS ROWS DISCARDED. The bed registers; the given table decides.

The sound follows the landing over the WHOLE cut: `build_short.sound_cues` re-derived from the GIVEN rows, written
to `<build>/SOUND-PLAN.json` - the PRIVATE copy - and embedded into the compiled timeline. The project's
`sound/SOUND-PLAN.json` and its approved `SHOT-TABLE-SHORT.py` are the approved cut's and are NEVER written: this
mode digests both before it starts and refuses by name if either moved under it (`build_short.main` writes both, so
`main` is never called - the registration is reused, not the entry point).

Then the same four tools, over the whole cut (`probe.py --gate`, the gate's own instants, not a candidate's window),
and ONE record in `batches/<label>.jsonl`: the row count, every FAIL / WARN row verbatim, the M45 / M46 parity and
variety rows verbatim, and the sheets on disk. Nothing is judged here and no threshold is fitted - a base is offered
for a watch (E99 s38), and whatever the gates measure is the finding.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import importlib.util
import json
import os
import re
import socket
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Mapping

SCRIPTS = Path(__file__).resolve().parent
REPO = SCRIPTS.parents[2]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import gate_motion_density as GMD  # noqa: E402  (_is_bed / CUE_TOL_S / PLATE_MIN_S: the gate's own sound and
                                   #  world clocks - the lab never keeps a second opinion about a threshold)
import gate_one_shot_floor as OSF  # noqa: E402  (ROW_ORDER: the WHOLE-CUT floors, named by the gate itself)
import build_scene_timeline_f as BSTF  # noqa: E402  (scene_exit: the compiler's own hybrid exit rule, never mirrored)
import lab_enumerate as LE  # noqa: E402  (the shapes, the clocks and the offset grammar - one source, never a copy)
import ledger_page as LPG  # noqa: E402  (badges_for: a badge is the SERIES' own, never typed here)
import recipe_walk as RW  # noqa: E402  (events / match / flatten: what a FIRE is, shared with the floor gate)
import self_watch as SW  # noqa: E402  (parse_gate: the `[LEVEL] Mxx` protocol's own reader)
from authoring import table as T  # noqa: E402  (the rows go through the kit's door, never a hand-written literal)

BED_REL = "content/video_engine/projects/systems-and-blowups/tokyo-tea-break"   # the CANDIDATE lab's bed
BED_SCRIPT = "build_short.py"      # ... and the file that makes any project a bed (the whole-table mode walks to it)
BEAT_PLAN_REL = "build-short/BEAT-PLAN.jsonl"      # P66 T7: the approved cut read back, one record per sentence
APPROVED_TABLE = "SHOT-TABLE-SHORT.py"             # the approved rows, as the kit last wrote them (--dry-run reads these)
BATCHES_REL = "content/video_engine/effects/lab/batches"   # NOT `runs/`: .gitignore's bare `runs/` rule swallows
                                                          # any directory of that name, and the record is tracked
SHOT_TABLE_NAME = "SHOT-TABLE-LAB.py"              # written INSIDE the private build, never over the episode's own
TIMELINE_NAME = "tokyo-lab.timeline.json"
TIMELINE_JSON = "timeline.json"                     # the take's own words + runtime, as every bed writes it
TABLE_TIMELINE_NAME = "base.timeline.json"         # the whole-table mode's compiled timeline, beside the bed's own
CUE_PLAN_NAME = "SOUND-PLAN.json"                  # the re-derived plan, in the PRIVATE build - never the project's
PROJECT_PLAN_REL = "sound/SOUND-PLAN.json"         # the APPROVED plan `build_short.main` writes; read-only here
PROBE_GATE_NAME = "layout-probe.json"              # what `probe.py --gate` writes (probe.py:924)
SHEET_NAME = "lab-sheet.png"
BUILD_PREFIX = "build-lab-"                        # every lab build lives under <bed>/build-lab-<batch>/<short id>/
REFUSED_PREFIX = "build-short"                     # the approved cut and every watched variant beside it
SCRIPT_STEM = "SCRIPT-90S.claude"                  # the report stem self_watch reads beside the project
SW_NO_VERDICT = "present, no verdict line"         # self_watch.verdict_line's own miss (self_watch.py:149)
SERVE_PORTS = tuple(range(8730, 8750))             # serve_player's default is 8731; the watched cuts sit in this band
EPS = 0.005

# The species a member becomes, with the duration and the binds the BED itself uses on that species. Nothing here is
# a new dial: each number is one this episode's own rows carry (`build_short.shot_table`), so a candidate is judged
# on the bed's craft and not on a value the lab invented.
SPECIES_DUR_S = {"spotlight": 1.0, "callout": 2.0, "focus_zoom": 2.0, "punch": 1.6, "plate_life": 3.0,
                 "figure": 1.6, "retitle": 2.4, "relight": 1.0, "span": 2.4, "chart_to": 1.4}
KEN_BURNS = (0.04, 14, -10)      # `plate_option:ken`: the compiler's own KEN proportions (build_scene_timeline_f.KEN)
ALIVE_PLATE = "world-tokyo-customs-dock-v1-alive;idle=drift;drift=20"   # P61 T14 / E99 s63: the bed's own alive plate
DESK_REGION = {"kind": "region", "x0": 0.117, "y0": 0.39, "x1": 0.26, "y1": 0.485}   # the bed's own desk region (row 3)
SUCK_POINT = "suck:0.49,0.55"    # the bed's own suck target (build_short.py row 3)
# THE PLAYER'S OWN CLOCKS, mirrored here and nowhere else (the lab never keeps a second opinion about a dial): a
# member is only REALISED when the row gives the player the seconds its mechanism takes. Each line names its source.
CARD_FLIGHT_S = 0.45             # STOP.FLIGHT_S (player.html:1041): a thrown card's time in the air
CARD_DROP_S = 0.32               # STOP.ANTIC_S + STOP.DROP_S (player.html:1044-1048): a dropped card's fall
CARD_IN_S = 0.75                 # CARD_IN (player.html:1644): a plain dock's lift in
CARD_LEAVE_S = 0.35              # DOCK_RETRACT_S (player.html:1672): the retract has to FINISH inside the row - under
                                 # it the card is still leaving while the next row is on screen, and the parent read
                                 # exactly that on batch-r1 (2026-09-17: "the card floats on the next page's cream")
SNAP_HOLD_S = 0.45               # SNAP_S (player.html:2612): the page grows out of the card's rectangle over these
                                 # seconds and the player MEASURES that rectangle off the card's own element
                                 # (player.html:5310), so a page that snaps needs its card still in the dock list at
                                 # the page's first frames - the landed card riding the veil (E99 s69's re-read of
                                 # recipe:card-becomes-the-chart; `held-dock-across-the-cut` holds a card the same way)
ARRIVAL_LANDS_S = {"throw": CARD_FLIGHT_S, "land": CARD_DROP_S, "drop": CARD_DROP_S}
FRAME_S = 0.033                  # one frame at the reference's 30 fps (GMD.DIP_S's own measurement)
SPECIES_READ_S = 0.3             # a species is READ a moment after it fires, never on the frame it starts
BADGE_IN_S = 0.36                # LP_BADGE_IN (player.html): a pill springs in over this - a badge stamp is read
                                 # when the pill has SETTLED, and each stamp of a ladder is its own tile
BLACK_LUMA = 8.0                 # M32's own reading of near-black (`SRC_M32`: "near-black = mean luma < 8"), the
                                 # threshold the first tile of a window has to clear
# THE CAPTION LAYER OWNS ITS BAND, and a card's RAIL is never under it (the parent, 2026-09-17: "the eye sees one
# static $617 pill with META NO clipped behind the words"). The player names the strip itself:
CAPTION_TOP_PX = 1340            # `html[data-aspect="9:16"] #caption.stage.onpage` - "the caption strip y1340-1440
                                 # (G-l), never over the chart or a plate's subject" (the player's own comment)
SAFE_TOP_F = 0.12                # the Shorts chrome band at the top (GMD's SAFE_WARN_SHARE: "top 12 %, bottom 20 %")
RAIL_COLS = 2                    # `.rail { grid-template-columns: 1fr 1fr }` - a rail of pills, two to a row
RAIL_ROW_PX, RAIL_GAP_PX, RAIL_MARGIN_PX = 39, 9, 11     # `.pill` / `.rail` in the player's CSS; MEASURED on this
                                 # bed at rows y 1420 and 1468 (48 = 39 + 9) with the rail 11 px under the frame


def rail_px(n_badges: int) -> int:
    """The height a rail of `n` pills takes UNDER the card - the player's own grid, counted."""
    rows = max(1, -(-int(n_badges) // RAIL_COLS))
    return RAIL_MARGIN_PX + rows * RAIL_ROW_PX + (rows - 1) * RAIL_GAP_PX


def rail_clear_place(card_aspect: float, n_badges: int) -> dict:
    """The dock options that put a carded rail in the room BETWEEN the top chrome and the caption strip.

    A card on a PLATE gets no box from the placer (`dock_place` reads a PAGE's geometry), so it takes the player's
    default dock box and its rail lands in the caption band. Naming `centre_y` takes `centred_place`'s own first
    branch (`build_scene_timeline_f.py:4027`), which writes a box for any row: the card is sized to the room that
    is left once the top chrome and the rail's own height are taken out of it."""
    sw, sh = 1080, 1920
    top = round(SAFE_TOP_F * sh)
    room = CAPTION_TOP_PX - rail_px(n_badges) - top
    h = min(room, BSTF.CENTRE_MAX_H * sh)
    w = min(h / float(card_aspect or 1.0), BSTF.CENTRE_W * sw)
    h = w * float(card_aspect or 1.0)
    return {"centre": True, "card_aspect": round(float(card_aspect), 4),
            "centre_w": round(w / sw, 4), "centre_y": round((top + h / 2) / sh, 4)}
DOCK_TAIL_S = CARD_LEAVE_S       # a card leaves before the window does, never on its cut (E40 #5), and its retract
                                 # finishes inside the row that carries it
MIN_REMNANT_S = 0.5              # a remnant of an approved row shorter than this is a FLASH, not a plate (M44)
BRACKET_LABEL = "-$122.6B"       # the bed's own bracket label (build_short.py, the V3 bracket) - never a new figure
ARRIVAL_MASS = {"throw": "paper", "land": "metal"}   # the mass each arrival card's own `author.example` carries

# THE SHAPE -> BEAT MAP. One or two Tokyo beats per shape, BY NUMBER, with the reason. This table is INTELLIGENCE
# work (E99 s66) and is written by hand: a tool that picked the beat by a rule would be choosing a beat for a cut.
SHAPE_BEATS: dict[str, tuple[tuple[int, ...], str]] = {
    "open-on-the-chart": ((1, 2), "the cut's own OPEN - 'Tokyo took a tea break.' / 'And left America with an "
                                  "unfunded bar tab.' The approved open is a CLIP and the page only mounts 2.0 s in "
                                  "(build_short.py:285); E99 s67 says the open starts ON the chart, so this hook is "
                                  "exactly the beat the shape is owed in."),
    "page-number-lands-at-n": ((8, 9), "the beat whose page carries a NUMBER - 'The Treasury's table shows Japan "
                                       "holds over a trillion dollars of our debt, and it's been selling since "
                                       "February.' The approved cut writes the peak figure and the June print on "
                                       "this sentence (build_short.py t_trillion / t_since)."),
    "page-to-page-transform": ((14, 15), "the cut's own chart-to-chart - on 'The Treasury prints the new total "
                                         "monthly' the line RECASTS into the month-by-month bars (E58, "
                                         "build_short.py t_prints): one page becoming the next through the chart "
                                         "itself, with no cream between."),
    "return": ((14, 15), "the cut's own RETURN - on 'Since February, Japan has sold a hundred and twenty-two billion "
                         "dollars' the holdings page comes back by the SPIRAL, unwound from its point with the drop "
                         "already drawn (E40 s4, build_short.py row 4), and the sentence says what has changed. The "
                         "RING (beats 23-25) is this cut's other return and is not used: the shape's 7.5 s window "
                         "would run into the outro card."),
    "plate-carries-a-card": ((12, 13), "the cut's only NARRATIVE PLATE - 'a Treasury page, and your phone.' / 'By "
                                       "the end you'll read both numbers yourself.' (row 3, plate-p-viewers-desk), "
                                       "the one beat in this cut where a plate can be handed a card."),
}


class LabBuildError(ValueError):
    """A refusal, BY NAME: a build dir the lab may not touch, a shape with no beat, a window no sentence covers, a
    member the bed cannot bind, or a batch whose records do not match what is on disk."""


# --------------------------------------------------------------------------- the bed

def bed_dir(repo: Path, table: Path | None = None) -> Path:
    """THE BED IS THE TABLE'S OWN PROJECT (P66 T3 seventh pass, E99 s72 Apply 6).

    The candidate lab has ONE bed (`BED_REL`) and keeps it: a shape's window is read off that cut's beat
    plan and its members are bound to its own docks. The WHOLE-TABLE mode has no window and no members -
    it builds a generated BASE, and s72 Apply 6 puts the next base on the one-shot's own plan, so its bed
    must be the project the table was generated for (its take, its words, its docks, its stills). The
    project is the nearest directory above the table that carries a `build_short.py` - the same walk the
    kit's own `Project` makes, and no map of episode names anywhere."""
    if table is not None:
        for parent in [Path(table).resolve(), *Path(table).resolve().parents]:
            if (parent / BED_SCRIPT).is_file():
                return parent
        raise LabBuildError(f"{table}: no `{BED_SCRIPT}` above it - the whole-table mode builds a base on the "
                            f"project's OWN bed (its take, its words, its docks), so the table has to live under one")
    return Path(repo) / BED_REL


BED_ENV = re.compile(r"""os\.environ\.get\(\s*["']([A-Z0-9_]*BUILD_DIR)["']""")
# ... and the DIRS that script writes into, by name: the `*_BUILD_DIR` call's own default (the approved
# build of that project - `build-short` on two beds, `build-oneshot-3` on the one-shot's) and any other
# `HERE / "<dir>"` it names as an output. `refuse_by_name` refuses every one of them.
BED_OUT_ENV = re.compile(r"""os\.environ\.get\(\s*["'][A-Z0-9_]*BUILD_DIR["']\s*,\s*["']([^"']+)["']""")
BED_OUT_HERE = re.compile(r"""^\s*(?:BUILD|OUT|OUTPUT|PUBLISH)\w*\s*=\s*HERE\s*/\s*["']([^"']+)["']""", re.M)


def bed_build_env(bed: Path) -> str:
    """The environment variable the project's own build script reads its BUILD dir from - read off the
    source, never mapped by episode name. Every short's bed carries one (`<NAME>_BUILD_DIR`) exactly so a
    cut under review can build beside the watched one and never over it (P48 T7)."""
    m = BED_ENV.search((Path(bed) / BED_SCRIPT).read_text(encoding="utf-8"))
    if not m:
        raise LabBuildError(f"{Path(bed).name}/{BED_SCRIPT} reads no `*_BUILD_DIR` from the environment, so this tool "
                            f"cannot point it at a PRIVATE build dir - and it never writes into the approved one")
    return m.group(1)


def load_beats(repo: Path | str = REPO) -> list[dict]:
    """The approved cut's BEAT PLAN: one record per sentence, `beat`/`t0`/`t1`/`row`/`sentence`/`plate` (P66 T7)."""
    path = bed_dir(Path(repo)) / BEAT_PLAN_REL
    if not path.is_file():
        raise LabBuildError(f"{path} is missing - the lab plants a candidate in a SENTENCE of the approved cut "
                            f"(E99 s60), and the beat plan is where those sentences are")
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def import_bed(repo: Path, build: Path, bed: Path | None = None):
    """`build_short.py` imported with its own `*_BUILD_DIR` pointed at the PRIVATE build - the bed's own
    facts, in memory.

    The module is loaded fresh per candidate (its `BUILD`, `EP` and dock registrations are module state), and its
    `main()` is never called: `main` writes the episode's own `SHOT-TABLE-SHORT.py` and `sound/SOUND-PLAN.json`, and
    a lab build never writes into the episode dir. `bed` is the project to import (the whole-table mode hands
    the table's own; the candidate lab's is `BED_REL`)."""
    root = Path(bed) if bed is not None else bed_dir(Path(repo))
    path = root / BED_SCRIPT
    os.environ[bed_build_env(root)] = str(Path(build).resolve())
    spec = importlib.util.spec_from_file_location(f"bed_{root.name.replace('-', '_')}_{abs(hash(str(build)))}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def approved_rows(bed, dry_run: bool) -> tuple[list[tuple], list[dict], float]:
    """(the approved rows, the take's words, the runtime). The REAL path runs the bed's own authoring - the take
    copied, the pauses applied, the outro clock, the caption pages, the dock assets registered - because those
    registrations are what lets the compiler resolve this episode's cards. `--dry-run` reads the rows the kit last
    wrote (`SHOT-TABLE-SHORT.py`) and touches no audio, so a pytest run renders nothing."""
    import shutil

    from authoring import audio as A, words as W
    ws = W.take_words(bed.EP)
    if dry_run:
        rows = T.load_rows(bed.HERE / APPROVED_TABLE)
        return rows, ws, max(float(r[1]) for r in rows)
    bed.EP.mkdirs()
    # the take's own file, from the bed's own stem (a project may hold several candidate cuts of one take:
    # `Project.take_stem`, `authoring/__init__.py:34`) - never a file name this tool typed
    shutil.copy2(bed.TAKE / f"{getattr(bed, 'TAKE_STEM', None) or bed.EP.take_stem}.mp3", bed.EP.audio_master)
    W.write_timeline(bed.EP, ws, A.probe_duration(bed.EP.audio_master))
    # THE EDIT PAUSES ARE THE BED'S, NOT THIS TOOL'S (P66 T3 seventh pass): a project whose take was
    # TIGHTENED before it was recorded declares no `EDIT_PAUSES` (doc 37 s14's dead space killed by
    # `retime_take.py`) and its own `main()` writes the timeline straight off the take. Inserting pauses
    # into a take that has none would move every word the plan is clocked on.
    pauses = getattr(bed, "EDIT_PAUSES", None)
    tl = (W.apply_edit_pauses(bed.EP, pauses) if pauses is not None
          else json.loads((Path(bed.EP.build) / TIMELINE_JSON).read_text(encoding="utf-8")))
    if pauses is not None:
        ws = W.shifted_words(bed.EP)
    line_s = A.probe_duration(bed.BRAND_LINE)
    t_outro, _t_line, runtime_s = A.outro_clock(tl["runtime_s"], line_s, outro_lead=bed.OUTRO_LEAD,
                                                outro_s=bed.OUTRO_S, brand_gap=bed.BRAND_GAP,
                                                brand_tail=bed.BRAND_TAIL)
    A.stitch_brand_line(bed.BUILD / tl.get("paused_audio", "audio/episode.mp3"), bed.BRAND_LINE, bed.BRAND_GAP,
                        runtime_s)
    tl["runtime_s"] = runtime_s
    W.save_timeline(bed.EP, tl)
    T.caption_pages(bed.BUILD, char_budget=28, max_words=6)
    # THE BED REGISTERS (the mode's own promise, above): a project that keeps its plate and card
    # registrations in a `register_assets()` of its own calls it from `main()`, which this tool never
    # calls - so it is called here where the bed has one, and the compiler can resolve that project's
    # own stills. Without it the base compiles to "no plate asset found" on the bed's own plate.
    if callable(getattr(bed, "register_assets", None)):
        bed.register_assets()
    rows = bed.shot_table(ws, runtime_s, t_outro)
    (bed.BUILD / "evidence-dock.json").write_text(json.dumps(bed.DOCK_META, indent=1), encoding="utf-8")
    return rows, ws, runtime_s


# --------------------------------------------------------------------------- the window (E99 s60)

def sentence_at(beats: list[dict], t: float) -> str | None:
    """The sentence being spoken at `t`, or None when the instant falls in no beat of the plan."""
    for b in beats:
        if float(b["t0"]) - EPS <= t <= float(b["t1"]) + EPS:
            return str(b["sentence"])
    return None


def beat_window(beats: list[dict], numbers: tuple[int, ...], window_s: float, cid: str) -> dict:
    """The sentence window a shape is planted in: `{n, beats, sentence, t0, t1, row, plate}`.

    The window opens on the FIRST beat's own `t0` and runs to the later of the last beat's `t1` and the shape's own
    window - a shape is never cut short by the sentence it opens in. Three things are refused BY NAME, all of them
    the same rule (E99 s60: a proof is a scene, and a candidate's clip must be a beat a short could carry): a beat
    number the plan does not carry, a window that OPENS where no sentence is spoken, and a window whose own length
    carries it PAST the cut's last spoken instant - a clip that runs out over the outro card is not a beat."""
    by_n = {int(b["beat"]): b for b in beats}
    missing = [n for n in numbers if n not in by_n]
    if missing:
        raise LabBuildError(f"{cid}: beat(s) {', '.join(str(n) for n in missing)} are not in the approved cut's beat "
                            f"plan (it carries {min(by_n)}-{max(by_n)}) - a candidate is planted in a SENTENCE of a "
                            f"real cut, never at a bare instant (E99 s60)")
    first, last = by_n[numbers[0]], by_n[numbers[-1]]
    t0 = round(float(first["t0"]), 2)
    t1 = round(max(float(last["t1"]), t0 + window_s), 2)
    if sentence_at(beats, t0) is None:
        raise LabBuildError(f"{cid}: the window opens at {t0:.2f}s, where no sentence is spoken - a proof is a "
                            f"SCENE, and a candidate's clip must be a beat a short could carry (E99 s60)")
    spoken = max(float(b["t1"]) for b in beats)
    if t1 > spoken + EPS:
        raise LabBuildError(f"{cid}: the window {t0:.2f}-{t1:.2f}s runs past the cut's last spoken instant "
                            f"({spoken:.2f}s) - the tail is the outro card, where no sentence is spoken, and a "
                            f"candidate's clip must be a beat a short could carry (E99 s60). Map this shape to an "
                            f"earlier beat in SHAPE_BEATS")
    return {"n": int(first["beat"]), "beats": [int(n) for n in numbers], "sentence": str(first["sentence"]),
            "t0": t0, "t1": t1, "row": int(first.get("row") or 0), "plate": str(first.get("plate") or "")}


# --------------------------------------------------------------------------- the member -> row translation

def exit_kind(row: tuple) -> tuple[str, float | None]:
    """A row's own exit as (name, its declared length): `dip`, `dip:0.6`, `suck:0.49,0.55` -> ("suck", None)."""
    token = str(row[5] or "")
    name, _, rest = token.partition(":")
    try:
        return name, float(rest)
    except ValueError:
        return name, None


def veil_s(rows: list[tuple], t: float) -> float:
    """The seconds of BLACK a transition puts at the boundary `t` - the half of it that falls AFTER `t`.

    WHOSE TRANSITION IT IS, in the player's own words (the dip block, E47, operator 2026-09-06): *"DIP and BLURZOOM
    straddle the boundary, so a scene reads its OWN exit for the half after its start and the NEXT scene's exit for
    the half before its end. `exit` names the transition INTO the scene it sits on."* So the veil at a boundary
    belongs to the row that BEGINS there, not to the one that ends - which is why the first correction did not hold:
    the lab read the outgoing row's exit, and on this bed the incoming row's own (the compiler defaults a row with
    docks to a dip, E47) was the one painting the frame black.

    MEASURED on the badge-ladder rendition (2026-09-17, `probe.png` mean luma): 0.0 at 38.96 s, 13.6 at 39.00,
    45.3 at 39.10, 76.7 at 39.20 - the black clears at the half-width, 0.235 s, exactly as the ramp says."""
    for i, r in enumerate(rows):
        if i == 0 or abs(float(r[0]) - t) >= EPS:      # the cut's first row has no boundary before it, so no veil
            continue
        name, own = row_exit(rows, i)
        if name in GMD.TRANSITION_S:
            return round((own if own else GMD.TRANSITION_S[name]) / 2, 2)
    return 0.0


def row_exit(rows: list[tuple], i: int) -> tuple[str, float | None]:
    """The transition INTO row `i`, as the COMPILER resolves it - `build_scene_timeline_f.scene_exit`, called here
    rather than mirrored. An authored 6th element wins; otherwise the dip is the default wherever the world actually
    changes and the incoming page does not carry a signature enter (E47 as corrected 2026-09-12). The world change
    is read off the plate ids, which is what the row tuple carries."""
    r = rows[i]
    authored = r[5] if len(r) > 5 else None
    page = parse_ledger(str(r[2])) or {}
    changed = str(r[2]).split(";")[0] != str(rows[i - 1][2]).split(";")[0]
    return BSTF.scene_exit(authored, bool(r[4]), page.get("enter") or None, changed)


def readable_window(rows: list[tuple], t0: float, t1: float) -> tuple[float, float]:
    """The window's own READABLE bounds: after the veil the boundary at `t0` puts on the frame, and the last frame
    that is still this candidate's (`t1` is the NEXT row's first frame, and a dip takes the ones before it)."""
    # one frame PAST the veil's own half-width: the ramp reaches full picture at the half, and a frame is what the
    # measurement above has between 45.3 and 76.7 luma
    veil, out = veil_s(rows, t0), veil_s(rows, t1)
    lo = round(t0 + (veil + FRAME_S if veil else 0.0), 2)
    hi = round(t1 - (out + FRAME_S if out else FRAME_S), 2)
    return lo, max(lo, hi)


def member_lands_s(card: Any, options: Mapping | None = None) -> float:
    """The seconds between a member being AUTHORED and its mechanism being on the frame - the player's own clocks.

    A thrown card authored at 41.46 s is in the air until 41.91 s, so a frame read at 41.46 s carries an empty plate:
    the parent's "two candidates show no card inside the window at all" was the sheet reading the instant the card
    was thrown rather than the instant it landed (2026-09-17)."""
    axis, token = member_axis(card), member_token(card)
    if axis == "arrival":
        return ARRIVAL_LANDS_S.get(token, CARD_FLIGHT_S)
    if axis == "dock_option" and token == "badge":
        return BADGE_IN_S            # the pill's own spring: the stamp is at the offset, the tile a spring later
    if axis in DOCK_AXES:
        return float((options or {}).get("lands_s") or CARD_IN_S)
    if axis == "page_enter":
        # AN ARRIVAL IS READ MID-ARRIVAL: a page that SNAPS is the card's rectangle growing into the page, and the
        # only frames that carry that mechanism are the snap's own (`SNAP_S`). A page that mounts or draws its axes
        # carries no such move, so it is read where its chart LANDS (E99 s67: it builds, then holds built).
        return SNAP_HOLD_S / 2 if token in ("snap", "camera") else float(LE.clocks()["lp_build_s"])
    if axis in ("species", "page_species", "chart_to"):
        return SPECIES_READ_S
    if axis == "exit":
        # a transition is read on the last frame that still carries the outgoing world: the boundary frame itself is
        # the veil (a dip reaches full black exactly there - `build_scene_timeline_f.py:5147`)
        return -(GMD.TRANSITION_S.get(token, 0.0) / 2 + FRAME_S)
    return 0.0


def sheet_instants(members: list[tuple[float, dict]], rows: list[tuple], t0: float, t1: float) -> list[float]:
    """The instants the probe reads on a candidate: the window's first READABLE frame, every member where its own
    mechanism has LANDED, and the last frame still inside the window. Sorted, de-duplicated, clamped to the window.

    Nothing here is a judgement - it is where a member can be SEEN, which is what a sheet is for (E99 s60)."""
    lo, hi = readable_window(rows, t0, t1)
    out = [lo, hi]
    for at, m in members:
        lands = member_lands_s(str(m["card"]), m.get("options"))
        out.append(round(min(max(t0 + at + lands, lo), hi), 2))
    return sorted({round(t, 2) for t in out})


def mmss(t: float) -> str:
    return f"{int(t // 60)}:{int(t % 60):02d}"


def parse_ledger(plate: str) -> dict | None:
    """A ledger plate id into its parts: `ledger:<series>:<variant>:<emphasize>:<quiet>[:<enter>[:<exit>]][;opts]`."""
    head, _, opts = str(plate).partition(";")
    if not head.startswith("ledger:"):
        return None
    parts = head.split(":")
    return {"series": parts[1], "variant": parts[2] if len(parts) > 2 else "line",
            "emphasize": parts[3] if len(parts) > 3 else "0", "quiet": parts[4] if len(parts) > 4 else "right",
            "enter": parts[5] if len(parts) > 5 else "", "exit": parts[6] if len(parts) > 6 else "",
            "opts": opts}


def ledger_id(p: dict) -> str:
    """The parts back into a plate id - the trailing empty parts dropped, the `;opts` kept verbatim."""
    parts = ["ledger", p["series"], p["variant"], str(p["emphasize"]), p["quiet"], p["enter"], p["exit"]]
    while parts and parts[-1] == "":
        parts.pop()
    return ":".join(parts) + (";" + p["opts"] if p["opts"] else "")


def bed_page(bed, beat: dict) -> dict:
    """The page a candidate's members dress: the BEAT's own page when it has one, else the bed's holdings page."""
    page = parse_ledger(beat.get("plate") or "")
    if page is None:
        page = parse_ledger(f"ledger:ev-japan-holdings-v1:line:{bed.LAST_IDX}:right")
    return dict(page)


def bed_binds(rows: list[tuple]) -> dict:
    """The TEXT a species needs, read off the bed's OWN authored rows - the retitle line it wrote and the label its
    bracket carries. A lab candidate never types a line of an episode's copy (the kit's rule, `authoring/__init__`)."""
    marks = [s for r in rows for s in ((r[6] if len(r) > 6 else None) or []) if isinstance(s, dict)]
    return {"retitle": next((s["text"] for s in marks if s.get("kind") == "retitle" and s.get("text")), None),
            "bracket": next((s["label"] for s in marks if s.get("kind") == "bracket" and s.get("label")),
                            BRACKET_LABEL)}


def species_for(bed, kind: str, at: float, on_page: bool, binds: dict) -> dict:
    """A `species` / `page_species` member as the row dict the compiler reads (`author.key`: species[] {"kind", "at",
    "dur", ...}). Every bind is the BED's own: its datum indices, its figures, its retitle, its bracket label."""
    sp = {"kind": kind, "at": round(at, 2), "dur": SPECIES_DUR_S.get(kind, 1.4)}
    target = {"kind": "datum", "index": bed.PEAK_IDX} if on_page else dict(DESK_REGION)
    if kind in ("spotlight", "callout", "focus_zoom", "punch", "figure"):
        sp["target"] = target
    if kind == "figure":
        sp["text"] = bed._bn(bed.FACTS["peak"])      # the object's own fact, never typed (build_short._holdings_facts)
        sp["dy"] = -0.7
    elif kind == "retitle":
        if not binds.get("retitle"):
            raise LabBuildError("page_species:retitle needs the line the BED retitles with, and the approved table "
                                "carries none - a lab candidate never types an episode's copy")
        sp["text"] = binds["retitle"]
    elif kind == "relight":
        sp["ref"], sp["index"] = "figure", 0
    elif kind == "span":
        sp.update({"from": bed.PEAK_IDX, "to": bed.LAST_IDX, "label": binds["bracket"], "color": "neg"})
    return sp


def chart_to_for(bed, verb: str, at: float, page: dict, rows: "list[tuple] | tuple" = ()) -> dict:
    """A `chart_to` member: the verb, and the state or window the bed's own page can actually travel to (E58)."""
    sp = {"kind": "chart_to", "at": round(at, 2), "dur": SPECIES_DUR_S["chart_to"], "to": verb}
    if verb == "rescale":
        sp["window"] = bed.HOLDINGS_WINDOW
    elif verb == "park":
        # R26-172 is WITHDRAWN (2026-09-17): the park IS how a page makes room for a card on this stage, and the
        # approved Tokyo cut parks twice (`chart_to park` at 36.18 s scale 0.55 and at 54.91 s scale 0.52, anchor
        # top) with the card landing in the room it makes. The dials are the BED's own, read off its rows.
        own = bed_chart_to(list(rows or ()), "park")
        sp.update({k: own[k] for k in ("scale", "anchor") if k in own} if own else
                  {"scale": PARK_SCALE, "anchor": "top"})
    elif verb == "extend":
        sp["to_index"] = bed.LAST_IDX
    else:                                            # morph / recast / remake travel to a declared page STATE
        # THE STATE IS THE `;then=` CHAIN, and the verb is only realised when the page HAS the state it travels to
        # (E58; the approved cut's own rows: `...;then=ev-japan-selling-v1:bars:3;then=ev-bonds-vs-chips-10y-v1:bars:1`
        # with `chart_to state 1` and `state 2`). A `state` index the chain cannot answer is a chart_to that plays as
        # nothing on the frame - the defect class the parent named on 2026-09-17 - so the chain is EXTENDED here and
        # the index always names a state that exists.
        states = [x for x in (page.get("opts") or "").split(";") if x.startswith("then=")]
        if not states:
            page["opts"] = ";".join(x for x in [page.get("opts") or "", "then=ev-japan-selling-v1:bars:3"] if x)
            states = ["then=ev-japan-selling-v1:bars:3"]
        sp["state"] = len(states)                    # the page's own last declared state: 1 for one `then=`, 2 for two
    return sp


def dock_for(bed, kind: str, arrival: dict | None, enter: float, leave: float, ws: list[dict],
             dry_run: bool) -> tuple:
    """A `dock_kind` member as the row's dock tuple `(asset_id, slot, enter, exit, opts)` - the BED's own cards, at
    the BED's own measured placement. `--dry-run` skips the asset registration (the crops and the record are ffmpeg
    and PIL work); the row token is the asset id either way."""
    opts = {"centre": True, "card_aspect": 0.5911, "centre_w": bed.FAB_W, "centre_x": bed.FAB_CX,
            "centre_y": bed.FAB_CY + 0.04}
    if kind == "press":
        aid = "dock-k-pledge-record" if dry_run else bed.record_dock("dock-k-pledge-record", ws, enter)
        opts = {"centre": True, "card_aspect": 1.0, "centre_w": 0.40, "centre_x": 0.77, "centre_y": 0.335}
    elif kind in ("image", "cutout"):
        aid = ("dock-i-fab-wafer" if dry_run else
               bed.D.dock_png("dock-i-fab-wafer", bed.STILLS_DIR / "sig-i-fab-wafer.png", bed.FAB_CROP, bed.BUILD))
        if kind == "cutout":
            opts["cutout"] = True                    # `dock_kind:cutout`'s own author key: dock option {'cutout': True}
    else:
        raise LabBuildError(f"dock_kind:{kind} has no card in the Tokyo bed - a bind is filled from the bed's own "
                            f"assets, never invented")
    if arrival:
        opts.update(arrival)
    return (aid, 0, round(enter, 2), round(leave, 2), opts)


def check_lands(cid: str, card: str, at: float, lands: float, end: float) -> None:
    """A card whose mechanism would land OUTSIDE the row that carries it is refused BY NAME, at build time.

    The parent's read of batch-r1 (2026-09-17): "two candidates show no card inside the window at all - the arrival
    lands after t1 or never". A member the window cannot hold is not a candidate the operator can judge, and the lab
    records the refusal rather than building a beat whose mechanism happens off screen (E99 s60)."""
    if at + lands > end - CARD_LEAVE_S + EPS:
        raise LabBuildError(f"{cid}: {card} is authored at {at:.2f}s and its own mechanism lands at "
                            f"{at + lands:.2f}s, past the last instant this row can hold it "
                            f"({end - CARD_LEAVE_S:.2f}s = the row's end {end:.2f}s less the card's retract "
                            f"{CARD_LEAVE_S:.2f}s, player.html DOCK_RETRACT_S) - a member that would land outside "
                            f"the window is a refusal, never a beat with nothing in it")


def candidate_rows(bed, cand: dict, beat: dict, ws: list[dict], dry_run: bool, binds: dict) -> list[tuple]:
    """The candidate as ONE row of the cut: its members translated by the catalogue's `author.key`, its offsets laid
    on the window's own clock. Every card the shapes carry lands in exactly one place of the row tuple
    `(start, end, plate_id, ken_burns, [docks], exit, [species])`."""
    t0, t1 = float(beat["t0"]), float(beat["t1"])
    page = bed_page(bed, beat)
    plate, ken = beat.get("plate") or "", (0, 0, 0)
    docks: list[tuple] = []
    species: list[dict] = []
    row_exit: str | None = None
    arrival = next(({"arrive": str(m["card"]).split(":", 1)[1],
                     "mass": m.get("option") or ARRIVAL_MASS.get(str(m["card"]).split(":", 1)[1], "paper")}
                    for m in cand["members"] if str(m["card"]).startswith("arrival:")), None)
    on_page = parse_ledger(plate) is not None or any(
        str(m["card"]).split(":", 1)[0] in ("page_builder", "page_enter", "page_exit", "page_species", "chart_to")
        for m in cand["members"])
    dock_kind, dock_at = None, t0
    for m in cand["members"]:
        axis, token = str(m["card"]).split(":", 1)[0], str(m["card"]).split(":", 1)[1]
        at = round(t0 + float(m["offset_s"]), 2)
        if axis == "page_builder":
            page["variant"] = token
        elif axis == "page_enter":
            page["enter"] = "" if token == "stamped" else token      # `stamped` is the compiler's own: an EMPTY part
        elif axis == "page_exit":
            page["exit"] = "cut" if token == "cut" else ""           # `retract` is the default leave: no 7th part
        elif axis in ("species", "page_species"):
            species.append(species_for(bed, token, at, on_page, binds))
        elif axis == "chart_to":
            species.append(chart_to_for(bed, token, at, page))
        elif axis == "dock_kind":
            dock_kind, dock_at = token, at
        elif axis == "arrival":
            continue                                                 # read above: an arrival is the dock's own opts
        elif axis == "exit":
            row_exit = SUCK_POINT if token == "suck" else token
        elif axis == "plate_option":
            plate, ken = (ALIVE_PLATE, ken) if token == "alive" else (plate, KEN_BURNS)
        else:
            raise LabBuildError(f"{cand['id']}: the axis {axis!r} has no place in a shot row - lab_build.py binds "
                                f"the axes beat-shapes.json carries, and this one is new")
    if dock_kind is not None:
        lands = (ARRIVAL_LANDS_S.get(str(arrival["arrive"]), CARD_FLIGHT_S) if arrival else CARD_IN_S)
        check_lands(str(cand["id"]), f"dock_kind:{dock_kind}", dock_at, lands, t1)
        docks.append(dock_for(bed, dock_kind, arrival, dock_at, t1 - DOCK_TAIL_S, ws, dry_run))
    if on_page:
        plate = ledger_id(page)
    species.sort(key=lambda s: float(s["at"]))
    return [(round(t0, 2), round(t1, 2), plate, ken, docks, row_exit, species)]


# --------------------------------------------------------------------------- the splice

def clip_row(row: tuple, start: float, end: float) -> tuple:
    """An approved row the candidate's window cuts into, kept but CLIPPED - and the species and docks the clip drops
    go with it, so a mark never fires outside the row that carries it."""
    docks = [tuple(d[:2]) + (round(max(float(d[2]), start), 2), round(min(float(d[3]), end), 2)) + tuple(d[4:])
             for d in (row[4] or []) if float(d[2]) < end - EPS and float(d[3]) > start + EPS]
    species = [s for s in (row[6] if len(row) > 6 else None) or [] if start - EPS <= float(s["at"]) < end - EPS]
    return (round(start, 2), round(end, 2), row[2], row[3], docks, row[5], species) + tuple(row[7:])


def snap_window(rows: list[tuple], t0: float, t1: float) -> tuple[float, float]:
    """The window pulled out to the approved CUT it sits inside, when the remnant it would leave is a flash.

    A beat's own `t0` is a WORD's instant and an approved row starts at the CUT before it (M13: 0.8 of the gap), so
    a window planted on the word leaves a tenth of a second of the outgoing plate on screen - a sliver M44 reads as
    a plate the eye cannot take in, and a clip that opens mid-dissolve. Under `MIN_REMNANT_S` the window takes it."""
    for r in rows:
        s, e = float(r[0]), float(r[1])
        if s < t0 - EPS < e and t0 - s < MIN_REMNANT_S:
            t0 = round(s, 2)
        if s < t1 + EPS < e and e - t1 < MIN_REMNANT_S:
            t1 = round(e, 2)
    return t0, t1


def splice(rows: list[tuple], new_rows: list[tuple], t0: float, t1: float) -> list[tuple]:
    """The approved table with the candidate's window replaced. Every row outside the window is kept AS AUTHORED."""
    out: list[tuple] = []
    for r in rows:
        s, e = float(r[0]), float(r[1])
        if e <= t0 + EPS or s >= t1 - EPS:
            out.append(r)
            continue
        if s < t0 - EPS:
            out.append(clip_row(r, s, t0))
        if e > t1 + EPS:
            out.append(clip_row(r, t1, e))
    out += list(new_rows)
    out.sort(key=lambda r: (float(r[0]), float(r[1])))
    return out


# --------------------------------------------------------------------------- the refusals

def served_port(build: Path) -> int | None:
    """The port serving THIS build dir, or None. Neither `serve_player.py` nor `build_review_queue.py` records a port
    list on disk, so a listening port is identified by CONTENT: its own `/player.json` against the one in the dir."""
    manifest = Path(build) / "player.json"
    if not manifest.is_file():
        return None
    mine = manifest.read_bytes()
    for port in SERVE_PORTS:
        with socket.socket() as s:
            s.settimeout(0.05)
            if s.connect_ex(("127.0.0.1", port)) != 0:
                continue
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/player.json", timeout=1.0) as r:
                if r.read() == mine:
                    return port
        except (urllib.error.URLError, OSError, ValueError):
            print(f"  [lab] 127.0.0.1:{port} is listening and did not answer /player.json - named, not guessed at")
    return None


def bed_output_dirs(bed: Path) -> list[str]:
    """Every dir name the BED's own `build_short.py` writes into - read off the source, never mapped by
    episode name (the seventh pass' review M4).

    `build-short*` was the whole by-name guard while the lab had one bed, and the project the whole-table
    mode was generalised FOR keeps its approved cut in `build-oneshot-3`: `--into <that>` was refused by
    nothing but a `serve_player.py` happening to answer, and `check_guard` watches only the approved
    `SHOT-TABLE-SHORT.py` and `sound/SOUND-PLAN.json` - so the approved BUILD's `timeline.json` /
    `player.json` / `assets.json` would have been overwritten under the operator (E99 s11, memory
    `review-link-frozen-copy`). The dirs are the `*_BUILD_DIR` default (`bed_build_env` reads the variable
    off the same call) and any other `HERE / "<dir>"` the script writes to."""
    src = (Path(bed) / BED_SCRIPT).read_text(encoding="utf-8")
    out: list[str] = []
    for pat in (BED_OUT_ENV, BED_OUT_HERE):
        for m in pat.finditer(src):
            name = m.group(1).strip().strip("/")
            if not name or "." in name or "/" in name:
                continue          # an asset the script READS (`HERE / "outro/outro-v2.mov"`), not a dir it writes
            if name not in out:
                out.append(name)
    return out


def refuse_by_name(build: Path, bed: Path | None = None) -> None:
    """`build-short*` and, where the bed is known, every dir the BED's own script writes into - by NAME:
    the approved cut, every cut watched beside it, and the approved BUILD of any project."""
    build = Path(build)
    if build.name.startswith(REFUSED_PREFIX) or any(p.name.startswith(REFUSED_PREFIX) for p in build.parents):
        raise LabBuildError(f"{build.name}: the lab never builds into `{REFUSED_PREFIX}*` - that is the approved cut "
                            f"and the cuts watched beside it, and a served build is never rebuilt under the operator "
                            f"(memory `review-link-frozen-copy`, E99 s11)")
    if bed is None:
        return
    named = bed_output_dirs(bed)
    parts = [build.name] + [p.name for p in build.parents]
    for name in named:
        if name in parts and not build.name.startswith(BUILD_PREFIX):
            raise LabBuildError(f"{build.name}: `{name}` is a dir {Path(bed).name}/{BED_SCRIPT} writes into itself "
                                f"(its own `*_BUILD_DIR` default or an output it names), so it is the APPROVED build - "
                                f"the lab never builds into one, and a served build is never rebuilt under the operator "
                                f"(memory `review-link-frozen-copy`, E99 s11). Point `--into` at a private dir")


def refuse_if_served(build: Path) -> None:
    """A dir a `serve_player.py` is answering for: the operator is watching it, so nothing is rebuilt under them."""
    port = served_port(build)
    if port is not None:
        raise LabBuildError(f"{Path(build).name}: a serve_player.py on 127.0.0.1:{port} is answering for this build - "
                            f"a served build is never rebuilt under the operator (memory `review-link-frozen-copy`)")


def refuse_dir(build: Path, batch_root: Path) -> None:
    """The build dirs the lab may not touch - by NAME first, then by what a `serve_player.py` is answering for."""
    build = Path(build)
    refuse_by_name(build)
    if not str(build.resolve()).startswith(str(Path(batch_root).resolve())):
        raise LabBuildError(f"{build}: a lab build lives under {Path(batch_root).name}/ and nowhere else")
    refuse_if_served(build)


def record_note(repo: Path, path: Path) -> str | None:
    """The batch record is a TRACKED artifact (P65 acceptance 2, and T8 leans on it). `.gitignore`'s bare `runs/`
    rule swallowed the first slice's `runs/<batch>.jsonl`, which is why the dir is `batches/` (P65 T3, 2026-09-17);
    if git would swallow this path too, the lab says so once per batch rather than editing `.gitignore` itself."""
    r = subprocess.run(["git", "check-ignore", "-q", str(path)], cwd=str(repo), capture_output=True)
    if r.returncode != 0:
        return None
    rel = os.path.relpath(path, repo).replace("\\", "/")
    return (f"  [lab] {rel} is GITIGNORED and the batch record is a TRACKED artifact of this plan - the two lines "
            f"that re-include it are `!{BATCHES_REL}/` and `!{BATCHES_REL}/*.jsonl`, in that order (git cannot "
            f"re-include a file inside an excluded directory until the directory itself is re-included); this tool "
            f"does not edit .gitignore")


def gitignore_note(repo: Path, build: Path) -> str | None:
    """`build-lab-*` is NOT in `.gitignore` today (checked 2026-09-17). The lab writes nothing to that file - it is
    outside this slice's write set - so it says so once, with the line that would fix it."""
    r = subprocess.run(["git", "check-ignore", "-q", str(build)], cwd=str(repo), capture_output=True)
    if r.returncode == 0:
        return None
    rel = os.path.relpath(build, repo).replace("\\", "/")
    return (f"  [lab] {rel} is NOT gitignored - a lab build is a render and belongs out of git; the line is "
            f"`content/video_engine/projects/*/*/{BUILD_PREFIX}*/` (this tool does not edit .gitignore)")


# --------------------------------------------------------------------------- the tools

def run_tool(argv: list[str]) -> tuple[int, str]:
    """One tool, one subprocess, its whole output. Monkeypatched in the tests: no pytest run renders video.

    PYTHONIOENCODING is forced to utf-8 because the record keeps every row VERBATIM: on Windows a child's piped
    stdout is the locale encoding, so a row carrying the gates' own middle dot (M35's `dense-line/line·4`) would
    reach the record as a replacement character. `gate_one_shot_floor.py:1180` reconfigures its own stdout; the
    others do not, and the lab reads all four the same way."""
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    r = subprocess.run([sys.executable, *argv], capture_output=True, text=True, encoding="utf-8", errors="replace",
                       env=env)
    return r.returncode, (r.stdout or "") + "\n" + (r.stderr or "")


def tool_rows(text: str) -> list[dict]:
    """The `[LEVEL] Mxx text` rows, read with the protocol's OWN reader (`self_watch.parse_gate`)."""
    return SW.parse_gate(text)["rows"]


def run_filter(build: Path, project: Path, instants: list[float], sheet: Path | None,
               timeline_name: str = TIMELINE_NAME, gate: bool = False) -> list[dict]:
    """The four tools, in order, as rows. self_watch runs FIRST (the fresh probe); probe takes the candidate's OWN
    instants and never a bare `--sheet`. A tool that dies is one row naming it, never a crash.

    `gate=True` is the WHOLE-CUT read (P66 HG1): a base has no window, so probe runs `--gate` - the GATE's own
    instants, written to the build's `layout-probe.json` - instead of a candidate's three."""
    rows: list[dict] = []
    rc, out = run_tool([str(SCRIPTS / "self_watch.py"), str(build), "--project", str(project),
                        "--script", SCRIPT_STEM, "--timeline", timeline_name])
    rows += tool_rows(out)
    report = Path(build) / SW.REPORT_NAME
    if not report.is_file():
        # The bar could not RUN - that is a tool row, not a verdict on the candidate, and self_watch keeps the same
        # rule for a floor gate it cannot run ("a floor gate that is missing or crashes is a WARN row naming it").
        # Known cause on a lab build: `self_watch.py:746` hands the lint only the build dir's NAME and
        # `lint_species_choice.build_dir` resolves it as `<project>/<name>`, so a build NESTED under
        # `build-lab-<batch>/` is not found; the lint would also read the EPISODE's approved table either way.
        last = next((l.strip() for l in reversed(out.splitlines()) if l.strip()), "no output")
        rows.append({"level": "WARN", "id": "self-watch",
                     "text": f"the one-shot bar did not run on this build (exit {rc}, no {SW.REPORT_NAME}): "
                             f"{last[:300]}"})
    elif rc != 0:
        said = SW.verdict_line(report)
        if said == SW_NO_VERDICT:
            # self_watch writes its verdict UNDER `## 3. Verdict`, on its own line, which `verdict_line`'s
            # `^\W*verdict\b` cannot match (self_watch.py:141-149 against :439) - its OWN `parse_report`
            # (:530-553) reads it. The lab re-implements neither reader; it says which one answered.
            said = f"{SW.parse_report(report.read_text(encoding='utf-8', errors='replace')).get('verdict') or said}" \
                   f"  (read by self_watch.parse_report: verdict_line cannot match self_watch's own heading)"
        rows.append({"level": "FAIL", "id": "self-watch", "text": said[:400]})
    _rc, out = run_tool([str(SCRIPTS / "gate_motion_density.py"), str(build), "--timeline", timeline_name])
    rows += tool_rows(out)
    _rc, out = run_tool([str(SCRIPTS / "gate_one_shot_floor.py"), str(build), "--project", str(project),
                         "--timeline", timeline_name])
    rows += tool_rows(out)
    if gate:
        rc, out = run_tool([str(SCRIPTS / "probe.py"), str(build), "--gate", "--timeline", timeline_name])
        written = Path(build) / PROBE_GATE_NAME
        if rc != 0 or not written.is_file():
            last = next((l.strip() for l in reversed(out.splitlines()) if l.strip()), "no output")
            rows.append({"level": "FAIL", "id": "probe",
                         "text": f"no {PROBE_GATE_NAME} (exit {rc}): {last[:400]}"})
        else:
            rows.append({"level": "PASS", "id": "probe", "text": f"{PROBE_GATE_NAME} on the gate's own instants"})
        return rows
    rc, out = run_tool([str(SCRIPTS / "probe.py"), str(build), *[f"{t:.2f}" for t in instants],
                        "--sheet", str(sheet), "--timeline", timeline_name])
    if rc != 0 or not Path(sheet).is_file():
        last = next((l.strip() for l in reversed(out.splitlines()) if l.strip()), "no output")
        rows.append({"level": "FAIL", "id": "probe",
                     "text": f"no sheet at {Path(sheet).name} (exit {rc}): {last[:400]}"})
    else:
        rows.append({"level": "PASS", "id": "probe",
                     "text": f"{Path(sheet).name} at {', '.join(f'{t:.2f}' for t in instants)}"})
    return rows


def decided_by(rows: list[dict]) -> list[str]:
    """Every FAIL and WARN row of the list, verbatim, its level and id in front."""
    return [f"[{r['level']}] {r['id']} {r['text']}".strip() for r in rows if r["level"] in ("FAIL", "WARN")]


# --------------------------------------------------------------------------- the sound follows the landing (T8)
#
# THE SMOKE'S OWN KILL (batch smoke-r2): `[FAIL] M29 1 transient cue(s) marking nothing inside the drop window:
# landing 2 (throw, paper) at 9.51s`. The bed's cue plan is authored for the APPROVED rows, so when the lab replaces
# the rows in a window the approved cues inside that window mark landings that no longer happen, and the candidate's
# own landings carry no sound at all. The answer is neither a waiver nor a new sound file: the cues INSIDE the window
# are RE-DERIVED from the spliced rows through the path `build_short.py` itself uses - `build_short.sound_cues`
# (`:477`, the call `main` makes at `:562`) over `authoring/audio.py`'s readings (`page_transitions`, `row_arrivals`,
# `landing_contact`, `stop_dials`) - and every cue OUTSIDE the window is kept exactly as the approved plan wrote it.
# NOTHING IS INVENTED: a landing kind the bed's map has no cue for is recorded as `no cue mapped for <kind>` and M29
# says whatever it says (memory `thresholds-from-the-reference`: a lab never fits a number to our own work).
#
# WHERE IT IS WRITTEN. The compiler reads the EPISODE's `sound/SOUND-PLAN.json` (`build_scene_timeline_f.py:5486`)
# and a lab build never writes into the episode dir, so the re-derived plan goes into the PRIVATE build instead: the
# compiled timeline's own `sound` list - what `gate_motion_density._cues` reads (`:1436-1450`) - and the new
# variants' data URIs into the build's `assets.json`, which `player.html` loads through `player.json`. The URI is
# made by `build_scene_timeline_f.data_uri`, the compiler's own; neither reader is re-implemented here.

CUE_KEY = "__snd_lab_{i}_{v}__"      # the compiler's key shape (`__snd_<i>_<variant>__`), in a range of its own


def approved_cues(build: Path) -> list[dict]:
    """The cues the compiler embedded from the APPROVED `sound/SOUND-PLAN.json`, read off the private build."""
    path = Path(build) / TIMELINE_NAME
    if not path.is_file():
        return []
    return list(json.loads(path.read_text(encoding="utf-8")).get("sound") or [])


def derive_cues(bed, rows: list[tuple]) -> list[dict]:
    """The cue plan the BED's own writer makes of the SPLICED rows - `build_short.sound_cues`, the same call
    `build_short.main` makes, over `authoring/audio.py`.

    `press_pack` is stubbed for the call and only for it: that function RENDERS the two press packs into the
    EPISODE's `sound/` dir, and a lab build never writes there. The packs are already on disk and the cue only names
    them, so the plan this returns is the one the bed would write."""
    packed = getattr(bed, "press_pack", None)
    try:
        if packed is not None:
            bed.press_pack = lambda *a, **k: None
        return list(bed.sound_cues(rows))
    finally:
        if packed is not None:
            bed.press_pack = packed


def cue_at(cue: dict) -> float:
    try:
        return float(cue.get("at") or 0.0)
    except (TypeError, ValueError):
        return 0.0


def cue_in_window(cue: dict, t0: float, t1: float) -> bool:
    """A cue's own instant inside the candidate's window. A BED is continuous sub-threshold music and belongs to no
    window - the reading is the gate's own (`gate_motion_density._is_bed`), never a second opinion."""
    return not GMD._is_bed(cue) and t0 - EPS <= cue_at(cue) <= t1 + EPS


def cue_label(cue: dict) -> str:
    return f"{cue.get('slot')} at {cue_at(cue):.2f}s"


def slot_base(cue: dict) -> str:
    """A cue's slot without its ROW NUMBER: `landing 2 (throw, paper)` -> `landing (throw, paper)`. The bed numbers
    each cue by the row it came from (`build_short.sound_cues`), and a splice renumbers the rows."""
    return re.sub(r"\s*\d+\s*", " ", str(cue.get("slot") or "")).strip()


def cue_splice(approved: list[dict], derived: list[dict], t0: float,
               t1: float) -> tuple[list[dict], list[str], list[str]]:
    """(the plan the build carries, the approved cues dropped, the cues the candidate's rows derived).

    THE PLAN IS THE SPLICED ROWS' OWN, and every cue OUTSIDE the window is still the approved one: the bed's writer
    is deterministic over rows, so an untouched row derives the cue it already had, at the same instant with the same
    slot, and THAT approved object - with the variants the compiler embedded and the operator chose - is the one
    kept. A derived cue with no such twin is the candidate's: either a landing inside the window, or a landing the
    window MOVED (a clipped approved row starts later, so its throw touches down later and its sound goes with it).
    An approved cue with no twin at all marked a landing that no longer happens, and it is dropped and named.

    The BEDS ride with the approved plan untouched: they are continuous, they mark no landing, and their envelopes
    are the operator's - a candidate does not re-breathe the music of the rest of the cut."""
    beds = [c for c in approved if GMD._is_bed(c)]
    live = [c for c in approved if not GMD._is_bed(c)]
    out, added, taken = list(beds), [], set()
    for d in derived:
        if GMD._is_bed(d):
            continue
        at = cue_at(d)
        twin = next((i for i, c in enumerate(live)
                     if i not in taken and abs(cue_at(c) - at) < EPS and slot_base(c) == slot_base(d)), None)
        if twin is not None and not (t0 - EPS <= at <= t1 + EPS):
            taken.add(twin)
            out.append(live[twin])
        else:
            out.append(d)
            added.append(cue_label(d))
    dropped = [cue_label(c) for i, c in enumerate(live) if i not in taken]
    return sorted(out, key=cue_at), dropped, added


def row_landings(rows: list[tuple], t0: float, t1: float) -> list[tuple[float, str]]:
    """Every landing the candidate's OWN rows make inside the window, BY KIND: a dock that arrives with weight (its
    contact frame on the kinetics module's clock, through `audio.landing_contact`) and a page that arrives (the row's
    own start, and the entry the plate id declares). These are the instants a cue is owed at."""
    from authoring import audio as A
    dials = A.stop_dials()
    out: list[tuple[float, str]] = []
    for r in rows:
        if not (t0 - EPS <= float(r[0]) <= t1 + EPS):
            continue
        for d, opts in A.row_arrivals(r):
            out.append((round(A.landing_contact(float(d[2]), str(opts["arrive"]), dials), 2),
                        f"dock arrive={opts['arrive']}"))
        page = A.page_transitions(str(r[2]))
        if page["ledger"]:
            enter = next((k for k in ("spiral", "mount", "snap", "camera") if page[k]), "roll-out")
            out.append((round(float(r[0]), 2), f"page enter={enter}"))
    return sorted(out)


def cue_notes(cues: list[dict], landings: list[tuple[float, str]]) -> list[str]:
    """`no cue mapped for <kind>`: a landing the candidate introduces that the BED's own cue map has no sound for.

    The lab does not invent one - there is no file on disk for it and no ruling that there should be (E99 s37). It
    records the gap and lets M29 print what it prints."""
    out: list[str] = []
    for t, kind in landings:
        if any(not GMD._is_bed(c) and abs(cue_at(c) - t) <= GMD.CUE_TOL_S for c in cues):
            continue
        note = f"no cue mapped for {kind} (its landing at {t:.2f}s carries no sound)"
        if note not in out:
            out.append(note)
    return out


def embed_cues(bed, build: Path, cues: list[dict], timeline_name: str = TIMELINE_NAME) -> list[str]:
    """The plan into the PRIVATE build: the timeline's `sound` (what the gate reads) and every NEW variant's data URI
    into `assets.json` (what the player loads). A variant whose file is not in the bed's own `sound/` dir is dropped
    from that cue and NAMED - the lab never points a cue at a file that is not on disk.

    `timeline_name` is the build's OWN compiled timeline (the whole-table mode compiles `base.timeline.json`): a
    plan embedded into a timeline that is not there is a plan nobody hears, so the name is passed, never assumed."""
    import build_scene_timeline_f as C
    tl_path, assets_path = Path(build) / timeline_name, Path(build) / "assets.json"
    if not tl_path.is_file():
        return [f"no {timeline_name} on disk - the cue plan was not written"]
    assets = json.loads(assets_path.read_text(encoding="utf-8")) if assets_path.is_file() else {}
    missing: list[str] = []
    out: list[dict] = []
    for i, cue in enumerate(cues):
        variants = dict(cue.get("variants") or {})
        for v, name in list(variants.items()):
            if str(name).startswith("__snd"):        # an approved cue: the compiler embedded it already
                continue
            src = Path(bed.HERE) / "sound" / str(name)
            if not src.is_file():
                missing.append(f"{cue.get('slot')}: no sound file {name} in the bed's sound/ dir")
                variants.pop(v)
                continue
            key = CUE_KEY.format(i=i, v=v)
            assets[key] = C.data_uri(src)
            variants[v] = key
        if variants:
            out.append({**cue, "variants": variants})
    tl = json.loads(tl_path.read_text(encoding="utf-8"))
    tl["sound"] = out
    tl_path.write_text(json.dumps(tl, indent=1), encoding="utf-8")
    assets_path.write_text(json.dumps(assets), encoding="utf-8")
    return missing


def bind_embedded_cues(build: Path, plan_path: Path, timeline_name: str) -> list[str]:
    """E99 s72's second fault closed AT THE SOURCE: once the plan is embedded, every cue whose effect does not fire
    at its instant in the COMPILED timeline is dropped from the timeline's `sound` and from the private plan, and
    named. The binder (`authoring.audio.bind_cues`) chooses no sound, adds no cue and moves no gain; a slot it
    cannot judge (a bed, a press pack) survives. Runs here, after `embed_cues`, so a rebuild never re-embeds an
    unbound cue - the sixth pass bound them from the outside (`generate_base_table.py --bind-cues`) and every
    `--table` rebuild put the five back. An instant the map has no cue for stays silent (E99 s37); `cue_notes`
    already names those, so only the DROPPED cues are returned here."""
    from authoring import audio as A
    tl_path = Path(build) / timeline_name
    if not tl_path.is_file():
        return []
    tl = json.loads(tl_path.read_text(encoding="utf-8"))
    kept, dropped = A.bind_cues(list(tl.get("sound") or []), tl)
    if dropped:
        tl["sound"] = kept
        tl_path.write_text(json.dumps(tl, indent=1), encoding="utf-8")
    if Path(plan_path).is_file():
        plan = json.loads(Path(plan_path).read_text(encoding="utf-8"))
        plan_kept, plan_dropped = A.bind_cues(list(plan.get("cues") or []), tl)
        plan["cues"] = plan_kept
        plan["bound"] = (f"bound to {timeline_name} by lab_build.py after the embed (E99 s72): every cue whose "
                         f"effect does not fire at its instant is dropped; {len(plan_dropped)} dropped")
        Path(plan_path).write_text(json.dumps(plan, indent=1), encoding="utf-8")
    return [f"DROPPED {d['slot']} at {d['at']:.2f}s: {d['why']}" for d in dropped]


def resound(bed, build: Path, rows: list[tuple], t0: float, t1: float) -> dict:
    """The candidate's window re-sounded, and the record's own `sound` block: how many approved cues were kept, which
    were dropped with the landings they marked, which the candidate's rows derived, and every gap named."""
    approved = approved_cues(build)
    derived = derive_cues(bed, rows)
    cues, dropped, added = cue_splice(approved, derived, t0, t1)
    notes = cue_notes(cues, row_landings(rows, t0, t1)) + embed_cues(bed, build, cues)
    notes = [n for n in notes if n]
    return {"kept": len(approved) - len(dropped), "dropped": dropped, "added": added, "notes": notes}


# --------------------------------------------------------------------------- the recipes as candidates (P65 T8)
#
# R26-168: fifteen recipes are `proven` against clocks that no longer exist. The lab is the only machine that can
# re-prove them, so each `proven` recipe is built HERE as a candidate - its ordered members at their own `offset_s`,
# in a Tokyo window whose beat matches its `acts` - under TODAY's clocks: a six-second world (M44), a page that
# BUILDS then holds (E99 s67: an `axes` or `mount` entry, never `built`), no badge rail and no `chart_to park` at
# 9:16 (R26-171 / R26-172). NO RECIPE FILE IS EDITED by this tool (the plan's T8 says so): a member the clocks refuse
# or the bed cannot bind is DROPPED, and the record says which member and why. Promotion is T6's, after the operator.

RECIPES_REL = "content/video_engine/effects/recipes"
BED_PLATE = "plate-p-viewers-desk"       # the Tokyo cut's only narrative plate (row 3) - what a plate segment stands on
DEFAULT_ENTER = "axes"                   # E99 s67: a page BUILDS then holds built; `built` is never an entry here
PAGE_AXES = ("page_builder", "page_enter", "page_exit", "page_species", "chart_to")
PLATE_AXES = ("plate_option", "idle")
# the bed's OWN read/park dial and reading box (`build_short.py` row 4, dock-k-pledge-record) - `dock_option:read`
MIN_SPECIES_S = 0.3                      # a mark shorter than this is a flash, not a mark
READ_OPTS = {"read": {"centre_w": 0.58, "centre_x": 0.5, "centre_y": 0.535, "card_aspect": 0.47},
             "read_s": 1.41, "park_s": 0.7}

# THE ACT -> SHAPE MAP. A recipe declares the sentence ACTS it was proven under; `SHAPE_BEATS` says which Tokyo
# sentence each shape is owed in. This table is the join and it is INTELLIGENCE work like `SHAPE_BEATS` (E99 s66):
# one line per act, each carrying the reason a recipe of that act belongs in that beat. The recipe's FIRST act
# decides, so the choice is the recipe's own declaration and not a scoring rule.
ACT_SHAPES: dict[str, tuple[str, str]] = {
    "SETS": ("plate-carries-a-card", "a SETS act builds the room the argument will stand in, and Tokyo's only "
             "NARRATIVE plate (row 3, plate-p-viewers-desk) is the one beat of this cut that is a room"),
    "NAMES": ("plate-carries-a-card", "a NAMES act writes on a PICTURE rather than on a chart's axes - the same "
              "narrative plate beat, the only one where a mark has a photograph to land on"),
    "QUOTES": ("plate-carries-a-card", "a QUOTES act hands the viewer a piece of evidence, and E99 s67 says a dock "
               "is an evidence still - the beat where a plate can be handed a card"),
    "EXPLAINS": ("page-number-lands-at-n", "an EXPLAINS act is a page carrying a number - the beat the approved cut "
                 "writes the peak figure and the June print on (build_short.py t_trillion / t_since)"),
    "COMPARES": ("open-on-the-chart", "a COMPARES act sets one reading against another and E99 s67 says the open "
                 "starts ON the chart - the hook is where this cut puts a chart to be read against something"),
    "TURNS": ("return", "a TURNS act turns the argument back onto a page it has already shown - the cut's own spiral "
              "return on 'Since February, Japan has sold a hundred and twenty-two billion dollars'"),
    "RETRACTS": ("return", "a RETRACTS act takes the claim back to the page that made it - the same return beat"),
}

# THE MEMBERS THIS BUILD DROPS, each with the reason, each RECORDED (never silently skipped). The first two are
# today's 9:16 clocks; the last two are binds the Tokyo bed does not carry, and a bind is filled from the bed's own
# assets or not at all. Only the second kind is `not on this bed` (E99 s69): a member today's clocks refuse is still
# the recipe's, and the candidate around it is still buildable.
NOT_ON_BED: frozenset = frozenset({"dock_payload:stack", "chart_dock:checklist"})   # binds this BED has not got

MEMBER_DROPS: dict[str, str] = {
    # R26-171 is AMENDED (2026-09-17, the parent's read of the badge-ladder rendition under E99 s71): *the rail is
    # SCALED to the stage, never dropped - dropping it at 9:16 left the badge ladder a still card for five seconds,
    # the recipe's whole point gone.* So `dock_option:badge` is no longer a drop; it is realised (see `badge_card`).
    "dock_payload:stack": "the Tokyo bed carries no stack payload - the verdict wall is Steel's (steel-and-paper/"
                          "build-f) and this cut has no card that opens into a rail of proofs",
    "chart_dock:checklist": "the Tokyo bed carries no checklist chart card - the procedure table is Steel's, and a "
                            "bind is filled from the bed's own assets, never invented",
}


def member_axis(card: Any) -> str:
    return str(card).split(":", 1)[0]


def member_token(card: Any) -> str:
    return str(card).split(":", 1)[1] if ":" in str(card) else ""


def member_offset(m: Mapping, window_s: float) -> float:
    """A member's offset on the window's clock. A range `[lo, hi]` is the band the proven fires were measured across
    (`recipe_walk.offset_ends`); the lab takes the HIGH end when it still fits the recipe's own window - the recipe's
    BEST case under today's clocks, so a row that fires anyway is a real contradiction - and the low end otherwise."""
    lo, hi = RW.offset_ends(m.get("offset_s", 0.0))
    return round(hi if hi <= window_s + EPS else lo, 2)


def load_proven(repo: Path) -> dict[str, dict]:
    """The `proven` recipe FILES (`effects/recipes/*.json`), by id - the source, not `docs/EFFECTS-CATALOG.jsonl`,
    which is build output (P63: never hand-edited, and it can lag its sources)."""
    out: dict[str, dict] = {}
    for path in sorted((Path(repo) / RECIPES_REL).glob("*.json")):
        rec = json.loads(path.read_text(encoding="utf-8"))
        if rec.get("status") == "proven" and rec.get("id"):
            out[str(rec["id"])] = rec
    return out


def recipe_shape(rec: Mapping) -> tuple[str, str]:
    """(the shape, the reason) the recipe's FIRST mapped act chooses - and a refusal by name when none is mapped."""
    acts = [str(a) for a in (rec.get("acts") or [])]
    for act in acts:
        if act in ACT_SHAPES:
            shape, why = ACT_SHAPES[act]
            return shape, f"act {act}: {why}"
    raise LabBuildError(f"{rec.get('id')}: none of its acts {acts or '[]'} has a beat in ACT_SHAPES - which sentence "
                        f"a recipe is owed in is intelligence work (E99 s66), so the act is added to that table by "
                        f"hand or the recipe is not built")


def recipe_segments(members: list[tuple[float, dict]], rec: Mapping) -> list[dict]:
    """The recipe's members split into the WORLDS they ask for, in order: `[{at, kind}]` on the window's own clock.

    A `page_enter` opens a page and a `plate_option` / `idle` opens a plate; a mark that does not change the kind is
    not a boundary. A recipe that declares no world at 0 opens on the kind its other members imply (a page when it
    dresses a page, a plate otherwise). This is what lets M44 measure `card-becomes-the-chart`: its plate is its own
    ROW with its own seconds (1.82-5.12 s across the proven band), not a share of one long world (R26-168)."""
    marks: list[tuple[float, str]] = []
    for at, m in members:
        axis = member_axis(m["card"])
        if axis == "page_enter":
            marks.append((at, "page"))
        elif axis in PLATE_AXES:
            marks.append((at, "plate"))
    if not marks or min(t for t, _ in marks) > EPS:
        implied = "page" if any(member_axis(m["card"]) in PAGE_AXES for _at, m in members) else "plate"
        marks.append((0.0, implied))
    segs: list[dict] = []
    for at, kind in sorted(marks):
        if segs and (segs[-1]["kind"] == kind or at - segs[-1]["at"] < EPS):
            continue
        segs.append({"at": round(at, 2), "kind": kind})
    return segs


def segment_of(at: float, m: Mapping, segs: list[dict], end: float) -> int:
    """Which segment a member fires in. An `exit` member is the LEAVE of the segment that ENDS at its offset - a
    row's exit fires at the row's own end (`build_scene_timeline_f`), never in the middle of it."""
    bounds = [s["at"] for s in segs] + [end]
    if member_axis(m["card"]) == "exit":
        return min(range(len(segs)), key=lambda i: abs(bounds[i + 1] - at))
    return max(i for i in range(len(segs)) if segs[i]["at"] <= at + EPS)


PARK_SCALE = 0.52     # the approved Tokyo row's own park (54.91 s), used only when the bed's rows are not to hand


def bed_chart_to(rows: list[tuple], verb: str) -> dict | None:
    """The `chart_to <verb>` species the BED itself authored, with its own scale and anchor - never a dial invented
    here (the approved cut parks at 0.52 / anchor top, and that is what a lab park is)."""
    for r in rows:
        for s in (r[6] if len(r) > 6 else None) or []:
            if isinstance(s, dict) and s.get("kind") == "chart_to" and str(s.get("to")) == verb:
                return {k: v for k, v in s.items() if k not in ("at", "dur")}
    return None


def bed_species(rows: list[tuple], kind: str) -> dict | None:
    """The species dict the BED itself authored for this kind, if the approved table carries one - its regions, its
    densities, its paper colour, its target datum. A lab candidate never invents a dial (`authoring/__init__`)."""
    for r in rows:
        for s in (r[6] if len(r) > 6 else None) or []:
            if isinstance(s, dict) and s.get("kind") == kind:
                return {k: v for k, v in s.items() if k != "at"}
    return None


def bed_variant_page(rows: list[tuple], variant: str) -> dict | None:
    """The page the BED itself authored in this VARIANT, if the approved table carries one. `page_builder:bars` on a
    holdings LINE series would recast 316 daily points as 316 bars - a page no short could carry (E28: a chart reads
    at a glance), so the recipe's variant is filled from this cut's own bars page instead of forced onto its line."""
    for r in rows:
        page = parse_ledger(str(r[2]))
        if page is not None and page["variant"] == variant:
            return dict(page)
    for r in rows:                       # ... and the `;then=` states the bed's own pages travel to are pages too
        for part in str(r[2]).split(";")[1:]:
            if part.startswith("then="):
                page = parse_ledger("ledger:" + part.split("=", 1)[1])
                if page is not None and page["variant"] == variant:
                    return dict(page)
    return None


def recipe_species(bed, kind: str, at: float, rows: list[tuple], on_page: bool, binds: dict) -> dict:
    """A recipe member's species, the bed's own authored one when this cut carries that kind, else the lab's bind."""
    own = bed_species(rows, kind)
    if own is not None:
        return {**own, "kind": kind, "at": round(at, 2)}
    return species_for(bed, kind, at, on_page, binds)


def bed_clip(rows: list[tuple]) -> str:
    """The bed's own CLIP world, resolved (`plate_option:clip` asks for a world that is a clip, not a still)."""
    clips = [str(r[2]) for r in rows if str(r[2]).startswith("clip:")]
    if not clips:
        raise LabBuildError("plate_option:clip needs a clip world and the approved Tokyo table carries none")
    return clips[-1]


def video_dock(bed, n: int, dry_run: bool) -> str:
    """The nth video dock of the bed, by its own registration: `build_short.dock_still` makes a VIDEO dock unless
    `--still-docks` is passed (`build_short.py:157-167`), and the bed names its clips in `DOCK_STILLS`."""
    aids = sorted(bed.DOCK_STILLS)
    aid = aids[n % len(aids)]
    return aid if dry_run else bed.dock_still(aid)


DOCK_AXES = ("dock_kind", "dock_payload", "dock_option")
DOCK_RANK = {"lab_card": -1, "dock_payload": 0, "dock_kind": 1, "dock_option": 2}   # the most specific member names
# the card, and a card the LAB registered for a rail or a snap is the most specific of all: it is already the series'
# own page rendered once, and the other members on that instant only merge their options into it


LAB_CARD = "dock-lab-{series}"    # a card the LAB registers on the bed: the SERIES' own page, rendered once
CARD_ASPECT = "9:16"              # the stage the bed is authored at - the card is rendered for the stage it lands on
RAIL_CARD_ASPECT = "16:9"         # ... except a card that carries a RAIL: a portrait card is so tall on a plate row
                                  # that the player's default dock box puts its pills off the bottom of the stage


def series_obj(bed, series: str) -> dict:
    """The evidence OBJECT the bed carries for this series - the file `docks.chart_card` renders from."""
    path = Path(bed.HERE) / "evidence/objects" / f"{series}.series.json"
    if not path.is_file():
        raise LabBuildError(f"the Tokyo bed carries no evidence object for {series} ({path.name}) - a card is "
                            f"rendered from the bed's own series file, never invented")
    return json.loads(path.read_text(encoding="utf-8"))


def series_variant(obj: Mapping, want: str) -> str:
    """The variant this series file is AUTHORED for - the card is the series' own page, not the page's variant
    forced onto it. Measured on the bed: `ledger_page.py` refuses `ev-bonds-vs-chips-10y-v1 --variant line` with
    "overflow is a BARS page's device (E60); this page is 'line'" - a bars file is a bars page, and only a file with
    no bars of its own takes the variant the page row names."""
    return "bars" if obj.get("bars") else (want or "line")


def write_dock_meta(bed) -> None:
    """The PRIVATE build's `evidence-dock.json`, rewritten after the lab has registered a card of its own. The
    compiler reads it from the build dir (`build_scene_timeline_f.py:5118`); the episode's own copy is never
    touched, because `bed.BUILD` is the lab's private dir for the whole run."""
    (bed.BUILD / "evidence-dock.json").write_text(json.dumps(bed.DOCK_META, indent=1), encoding="utf-8")


def lab_chart_card(bed, series: str, variant: str, dry_run: bool, badges: bool = False,
                   aspect: str = CARD_ASPECT) -> str:
    """`authoring.docks.chart_card` of the SERIES a page row names - the card that page grows out of (the parent,
    2026-09-17: the proof cut throws the chart's own card, not an arbitrary bed still), with the series' OWN badges
    when a recipe asks for a rail. Every string is the series file's: nothing is typed here and no figure is made.

    The card's meta entry joins `DOCK_META` (title, source, species `chart`, badges) and the private
    `evidence-dock.json` is rewritten, because the badges a card carries live on the EVIDENCE record - the dock
    tuple only says WHEN each is stamped (`build_scene_timeline_f.dock_entry`: enter + 0.75 + 1.3 n)."""
    obj = series_obj(bed, series)
    # THE ASPECT IS PART OF THE ASSET'S NAME: `docks.chart_card` only re-renders when the series or the renderer is
    # newer than the card on disk, so a card first rendered portrait would stay portrait forever under one id (it
    # did, on the first landscape run - measured: the rail painted nothing because the old PNG was still there).
    aid = LAB_CARD.format(series=series) + ("" if aspect == CARD_ASPECT else "-" + aspect.replace(":", "x"))
    entry = {"asset": aid, "title": str(obj.get("title") or ""), "source": str(obj.get("source") or ""),
             "species": "chart", "badges": LPG.badges_for(obj) if badges else []}
    meta = [m for m in bed.DOCK_META if m.get("asset") != aid] + [entry]
    bed.DOCK_META[:] = meta
    if not dry_run:
        bed.dock_chart(aid, series, variant=series_variant(obj, variant), aspect=aspect)
        write_dock_meta(bed)
    return aid


def badge_series(bed, want: int) -> tuple[str, int]:
    """(the bed's own series that carries the most badges, how many) - a badge rail is a CHART's conclusions, and
    B3 is why a drawn still can never carry one: a badge numeral must appear verbatim in the document behind it."""
    best, n = "", 0
    for path in sorted((Path(bed.HERE) / "evidence/objects").glob("*.series.json")):
        obj = json.loads(path.read_text(encoding="utf-8"))
        k = len(LPG.badges_for(obj))
        if k > n:
            best, n = path.name.replace(".series.json", ""), k
        if n >= want:
            break
    return best, n


def recipe_dock(bed, card: str, at: float, leave: float, ws: list[dict], dry_run: bool, n: int) -> tuple:
    """One dock member as the row's dock tuple `(asset_id, slot, enter, exit, opts)` - the BED's own cards only."""
    axis, token = member_axis(card), member_token(card)
    if axis == "lab_card":                           # a card the LAB registered on the bed (a chart card of a series)
        # CENTRED, so the compiler places it in the band ABOVE the caption strip (`CENTRE_BAND`, the portrait
        # stage's own device): the parked card's RAIL is what the badge ladder is about, and at the default dock
        # place it lands under the captions.
        opts = {"arrive": "land", "mass": "paper", "centre": True}
        if not dry_run:
            opts["card_aspect"] = bed.D.card_aspect(token, bed.BUILD)
        return (token, 0, round(at, 2), round(leave, 2), opts)
    if axis == "dock_kind" and token == "video":
        return (video_dock(bed, n, dry_run), 0, round(at, 2), round(leave, 2),
                {"centre": True, "card_aspect": 0.5911, "centre_w": bed.FAB_W, "centre_x": bed.FAB_CX,
                 "centre_y": bed.FAB_CY + 0.04})
    if axis == "dock_kind":
        return dock_for(bed, token, None, at, leave, ws, dry_run)
    if axis == "dock_payload" and token == "chart":
        aid = ("dock-h-fed-vs-yields" if dry_run
               else bed.dock_chart("dock-h-fed-vs-yields", "ev-fed-vs-yields-v1", aspect="9:16"))
        return (aid, 0, round(at, 2), round(leave, 2), {"arrive": "throw", "mass": "paper"})
    if axis == "dock_payload" and token == "record":
        return dock_for(bed, "press", None, at, leave, ws, dry_run)
    if axis == "dock_option" and token == "read":
        # a second `dock_option:read` is a SECOND card taking the same box (`read-park-build-write`), never the same
        # asset docked twice - the bed's two readable cards are the record and the fab still, in that order
        dock = dock_for(bed, "press" if n % 2 == 0 else "image", None, at, leave, ws, dry_run)
        return dock[:4] + ({**dock[4], **READ_OPTS},)
    if axis == "dock_option" and token == "centre":
        dock = dock_for(bed, "image", None, at, leave, ws, dry_run)
        return dock[:4] + ({**dock[4], "centre": True},)
    raise LabBuildError(f"{card} has no card in the Tokyo bed - a bind is filled from the bed's own assets")


def recipe_rows(bed, rec: Mapping, beat: dict, ws: list[dict], dry_run: bool, rows: list[tuple],
                binds: dict) -> tuple[list[tuple], list[str], list[dict]]:
    """(the rows, the members dropped with their reasons, the segments). A `proven` recipe as a beat of this cut."""
    t0, t1 = float(beat["t0"]), float(beat["t1"])
    window_s = float(rec.get("window_s") or RW.DEFAULT_WINDOW_S)
    drops: list[str] = []
    members: list[tuple[float, dict]] = []
    for m in rec.get("members") or []:
        card = str(m["card"])
        reason = MEMBER_DROPS.get(card)
        at = member_offset(m, window_s)
        if reason:
            mark = NOT_ON_BED_MARK if card in NOT_ON_BED else "DROPPED - "
            drops.append(f"{card} at +{at:.2f}s {mark}{reason}")
            continue
        members.append((at, dict(m)))
    members.sort(key=lambda x: x[0])
    segs = recipe_segments(members, rec)
    end_rel = round(t1 - t0, 2)
    out: list[tuple] = []
    page = bed_page(bed, beat)
    if not any(member_axis(m["card"]) == "chart_to" for _at, m in members):
        # M23: a second chart state is BUILT TO BE MOVED TO. The beat's own page may declare states the approved row
        # recasts into; a recipe that carries no `chart_to` never travels there, so it does not inherit them.
        page["opts"] = ";".join(p for p in (page.get("opts") or "").split(";")
                                if p and not p.startswith("then="))
    for k, seg in enumerate(segs):
        s = round(t0 + seg["at"], 2)
        e = round(t0 + segs[k + 1]["at"], 2) if k + 1 < len(segs) else round(t1, 2)
        mine = [(at, m) for at, m in members if segment_of(at, m, segs, end_rel) == k]
        # R26-171 AMENDED (2026-09-17): a `dock_option:badge` member is one PILL ON THE RAIL of the card that is
        # standing - never a card of its own. The compiler stamps them on its own clock (`dock_entry`: the card's
        # enter + 0.75 + 1.3 n = +2.05, +3.35, +4.65, +5.95), which is where the recipe's own offsets come from.
        badge_ats = [at for at, m in mine if str(m["card"]) == "dock_option:badge"]
        mine = [(at, m) for at, m in mine if str(m["card"]) != "dock_option:badge"]
        docks: list[tuple] = []
        species: list[dict] = []
        ken, row_exit, world = (0, 0, 0), None, None
        dock_members: dict[float, list[str]] = {}
        page["enter"] = DEFAULT_ENTER if seg["kind"] == "page" else page.get("enter") or ""
        arrivals: list[tuple[float, dict]] = []
        for at_rel, m in mine:
            card = str(m["card"])
            axis, token = member_axis(card), member_token(card)
            at = round(t0 + at_rel, 2)
            if axis == "page_builder":
                own = bed_variant_page(rows, token)
                if own is not None:
                    page.update({k: own[k] for k in ("series", "variant", "emphasize", "quiet")})
                else:
                    page["variant"] = token
            elif axis == "page_enter":
                page["enter"] = token
            elif axis == "page_exit":
                page["exit"] = "cut" if token == "cut" else ""
            elif axis in ("species", "page_species"):
                sp = recipe_species(bed, token, at, rows, seg["kind"] == "page", binds)
                sp.update(m.get("options") or {})    # the recipe's own dials (a trace's bow, draw_s, width)
                species.append(sp)
            elif axis == "chart_to":
                species.append(chart_to_for(bed, token, at, page, rows))
            elif axis == "idle":
                world = ALIVE_PLATE
            elif axis == "plate_option":
                if token == "ken":
                    ken = KEN_BURNS
                elif token == "alive":
                    world = ALIVE_PLATE
                elif token == "clip":
                    world = bed_clip(rows)
                else:
                    world = world or BED_PLATE
            elif axis in DOCK_AXES:
                dock_members.setdefault(at, []).append(card)
                # A CARD THAT PARKS OVER A PAGE NEEDS THE ROOM THE PAGE'S PARK MAKES (R26-172 WITHDRAWN,
                # 2026-09-17): `dock_option:read` carrying the option `park_s` is the recipe's own PARK member
                # ("a second card takes the same place and parks, clearing the chart for what comes next"), and the
                # approved Tokyo cut does exactly that - `chart_to park` at 54.91 s (scale 0.52, anchor top) and
                # the card landing in the room at 56.72 s. The park is planted a park's own length AHEAD of the
                # card, so the room exists when the card arrives, never over a plot the page still fills.
                if str(m.get("option") or "") == "park_s" and seg["kind"] == "page":
                    # AT THE SEGMENT'S START, the earliest the room can open: the approved cut parks 0.4 s before
                    # its card arrives (54.91 -> 55.31), and this recipe's first card lands on the row's own first
                    # frame, so the park cannot start any sooner than the beat does.
                    species.append(chart_to_for(bed, "park", s, page, rows))
            elif axis == "arrival":
                arrivals.append((at, {"arrive": token,
                                      "mass": m.get("option") or ARRIVAL_MASS.get(token, "paper")}))
            elif axis == "exit":
                row_exit = SUCK_POINT if token == "suck" else (m.get("option") or token)
            else:
                raise LabBuildError(f"{rec.get('id')}: the axis {axis!r} has no place in a shot row")
        # ONE CARD PER OFFSET: `dock_kind:image` + `dock_payload:chart` at the same instant is one card whose
        # payload is a chart, not two cards on top of each other; the most specific member names the asset and the
        # rest merge their options into it. A card's exit is the next card's ENTER when a later one takes its box
        # (`held-page-hosts-the-docks`: "the second moving card replaces the first in the same box").
        ats = sorted(dock_members)
        if badge_ats and ats:
            # THE RAIL IS A CHART'S CONCLUSIONS (B3: a badge numeral appears verbatim in the document behind it), so
            # the card the ladder stamps is the bed's own CHART card - which is what the recipe's PROOF cut carries
            # (steel-and-paper/build-f: ev-divergence-v1 with four badges at 52.45 / 53.75 / 55.05 / 56.35).
            series, have = badge_series(bed, len(badge_ats))
            if not series:
                drops.append(f"dock_option:badge x{len(badge_ats)} {NOT_ON_BED_MARK}no series on this bed carries a "
                             f"badge of its own, and a badge numeral is the document's, never typed (B3)")
            else:
                if have < len(badge_ats):
                    drops.append(f"dock_option:badge: the ladder asks {len(badge_ats)} pills and the bed's richest "
                                 f"series ({series}) carries {have} - {have} are stamped, the rest are NOT on this "
                                 f"bed (a badge is the document's own, never typed)")
                # A LANDSCAPE card for a rail (MEASURED, 2026-09-17): the portrait card is 802 x 1473 stage px on
                # this bed and its rail falls to y 2020-2107 of a 1920 stage - off the frame entirely (hiding the
                # standing pills changes no pixel). The same page rendered 16:9 is a card whose rail lands on stage.
                badge_card = lab_chart_card(bed, series, page.get("variant") or "line", dry_run, badges=True,
                                            aspect=RAIL_CARD_ASPECT)
                dock_members[ats[0]] = [c for c in dock_members[ats[0]] if member_axis(c) != "dock_kind"]
                dock_members[ats[0]].insert(0, f"lab_card:{badge_card}")
        for j, at in enumerate(ats):
            until = round(min(ats[j + 1], e - DOCK_TAIL_S), 2) if j + 1 < len(ats) else round(e - DOCK_TAIL_S, 2)
            cards = sorted(dock_members[at], key=lambda c: DOCK_RANK.get(member_axis(c), 9))
            lands = next((ARRIVAL_LANDS_S.get(str(a["arrive"]), CARD_FLIGHT_S) for a_at, a in arrivals
                          if abs(a_at - at) < EPS), CARD_IN_S)
            check_lands(str(rec.get("id")), cards[0], at, lands, e)
            dock = recipe_dock(bed, cards[0], at, until, ws, dry_run, j)
            for extra in cards[1:]:
                dock = dock[:4] + ({**dock[4], **recipe_dock(bed, extra, at, until, ws, dry_run, j)[4]},)
            if badge_ats and j == 0 and dock[4].get("card_aspect"):
                # THE RAIL CLEARS THE CAPTION STRIP: the card is sized and placed to the room above it
                dock = dock[:4] + ({**dock[4], **rail_clear_place(dock[4]["card_aspect"], len(badge_ats))},)
            docks.append(dock)
        for at, arrival in arrivals:
            if docks:
                i = min(range(len(docks)), key=lambda j: abs(float(docks[j][2]) - at))
                docks[i] = docks[i][:4] + ({**docks[i][4], **arrival},)
            else:
                # A RECIPE THAT THROWS A CARD WITHOUT NAMING ONE, into a page that SNAPS, throws THE PAGE'S OWN
                # CHART CARD (the parent, 2026-09-17: "in the proof cut the thrown card IS the chart's own card" -
                # japan-tariff-trick throws `dock-b-holdings`, the hook page rendered as a card, and the page grows
                # out of it). `authoring.docks.chart_card` of the series the page row names is that card. It is also
                # an IMAGE card, which is what the snap needs: the player measures the rectangle off the card's
                # `img` element, and on a VIDEO card that img is the empty `#i1` placeholder (`offsetHeight` 0,
                # measured on this bed), so the rect is never recorded and the page simply appears.
                snapping = any(str(s.get("kind")) == "page" for s in segs[k + 1:])
                if snapping and page.get("series"):
                    aid = lab_chart_card(bed, str(page["series"]), page.get("variant") or "line", dry_run)
                    dock = (aid, 0, round(at, 2), round(e - DOCK_TAIL_S, 2), dict(arrival))
                else:
                    dock = dock_for(bed, "image", arrival, at, e - DOCK_TAIL_S, ws, dry_run)
                docks.append(dock)
        if seg["kind"] == "page":
            if page["enter"].startswith("snap") and "=" not in page["enter"]:
                # `snap_from` names the dock the viewer was just shown, and the PLAYER measures that dock's rectangle
                # off the card's own element (player.html:5310) at the instant the page grows out of it. A card whose
                # dock tuple ENDS on the boundary has left the dock list by the page's first frame, so the rect is
                # never taken and the page simply appears - which is what the parent read on the r1 build of
                # `card-becomes-the-chart` (2026-09-17). The card is therefore HELD ACROSS the boundary, into the
                # page's own row, for the snap's own clock: the landed card rides the veil (the member's role text),
                # exactly as `held-dock-across-the-cut` holds a card past its scene in the proof cut.
                prev = out[-1] if out and (out[-1][4] or []) else None
                # ... and it must be a card the player can MEASURE: a video card's `img` is the empty placeholder
                # (`#i1`), so `SNAP_RECT` is never filled for it and the page has no rectangle to grow from
                clips = set(getattr(bed, "DOCK_STILLS", {}) or {})
                i = next((k for k in range(len(prev[4]) - 1, -1, -1) if str(prev[4][k][0]) not in clips),
                         None) if prev is not None else None
                if prev is not None and i is not None:
                    dock = prev[4][i]
                    page["enter"] = f"snap={dock[0]}"
                    prev[4][i] = dock[:3] + (round(s + SNAP_HOLD_S, 2),) + tuple(dock[4:])
                else:
                    why = ("carries no dock" if prev is None else "carries only VIDEO cards, whose rectangle "
                           "the player cannot measure (player.html:5310)")
                    drops.append(f"page_enter:snap at +{seg['at']:.2f}s {NOT_ON_BED_MARK}no landed card stands "
                                 f"before this page for it to grow out of (the row that ends at {s:.2f}s {why}), "
                                 f"so the page is entered by `{DEFAULT_ENTER}` and the member is NOT realised - "
                                 f"the mechanism needs a still card on the veil")
                    page["enter"] = DEFAULT_ENTER
            plate = ledger_id(page)
        else:
            plate = world or bed_world_at(rows, s) or BED_PLATE
            if plate.startswith("ledger:"):
                plate = BED_PLATE
        species.sort(key=lambda x: float(x["at"]))
        clamp_species(species, e)
        out.append((s, e, plate, ken, docks, row_exit, species))
    return out, drops, segs


def clamp_species(species: list[dict], end: float) -> None:
    """A species never outlives its row, and never outlives the NEXT fire of its own kind: the bed's `dur` was
    authored for ONE long trace on a whole plate, and a recipe's ladder fires three of them 1.26 s apart
    (`trace-callout-ladder`). Held in place, the first would still be drawing when the third begins."""
    for i, sp in enumerate(species):
        at = float(sp["at"])
        nxt = next((float(o["at"]) for o in species[i + 1:] if o.get("kind") == sp.get("kind")), None)
        cap = min(end, nxt if nxt is not None else end)
        sp["dur"] = round(max(MIN_SPECIES_S, min(float(sp.get("dur") or MIN_SPECIES_S), cap - at)), 2)


def bed_world_at(rows: list[tuple], t: float) -> str:
    """The world the APPROVED cut carries at this instant - the bed's own resolved token (a clip's path, a plate's
    id), never the beat plan's abbreviation."""
    for r in rows:
        if float(r[0]) - EPS <= t < float(r[1]) + EPS:
            return str(r[2])
    return ""


# --------------------------------------------------------------------------- did it fire, and what is the verdict

LIGHT_KINDS = ("spotlight", "punch", "callout", "focus_zoom", "relight")   # the targeted species M11 counts as a light


def recipe_fires(repo: Path, build: Path, rec: Mapping, t0: float, t1: float) -> dict:
    """`recipe_walk.match` on the BUILT timeline: did the recipe's own members fire, in order, at their offsets?

    The walk and the matcher are `recipe_walk`'s - the same two the drift gate and the one-shot floor use - and the
    catalogue's option owners and recipe registry come from `gate_one_shot_floor`. Nothing is re-implemented. A miss
    is explained in the walk's own terms: which member's CARD never fired inside the window, or (when they all did)
    which one fired away from its authored offset."""
    path = Path(build) / TIMELINE_NAME
    if not path.is_file():
        return {"count": 0, "why": f"no {TIMELINE_NAME} on disk - the candidate did not compile"}
    catalog = Path(repo) / OSF.CATALOG_REL
    options = OSF.card_options(catalog) if catalog.is_file() else {}
    registry = OSF.recipe_registry(catalog) if catalog.is_file() else {}
    tl = json.loads(path.read_text(encoding="utf-8"))
    evts = RW.events(tl, options)
    window_s = float(rec.get("window_s") or RW.DEFAULT_WINDOW_S)
    # The matcher is run over the BEAT's own span, never the recipe's number alone: a sentence may run a tenth of a
    # second longer than the recipe's window, and the thing under test is the MEMBERS' offsets (each still pinned to
    # `recipe_walk.OFFSET_TOL`), not whether the Tokyo sentence happens to be shorter than the proof's scene. Both
    # numbers are recorded, so nothing about the window is hidden.
    used = round(max(window_s, t1 - t0), 2)
    members = list(rec.get("members") or [])
    fires = [f for f in RW.match(evts, members, used, recipes=registry) if t0 - EPS <= f.t <= t1 + EPS]
    out = {"count": len(fires), "window_s": window_s, "window_used_s": used,
           "whole_build": len(RW.match(evts, members, window_s, recipes=registry))}
    if fires:
        out.update({"at": round(fires[0].t, 2), "members_at": fires[0].members_at, "scene": fires[0].scene})
        return out
    out["why"] = fire_miss(evts, members, registry, used, t0, t1)
    return out


def fire_miss(evts, members, registry, window_s: float, t0: float, t1: float) -> str:
    """Why the recipe did not fire, in the walk's own terms: the member cards absent from the window, or the first
    one that fired away from its authored offset (`from X -> Y` - what an amended offset would have to say)."""
    flat = RW.flatten(members, registry)
    inside: dict[str, list[float]] = {}
    for e in evts:
        if e.card and t0 - EPS <= e.t <= t1 + EPS:
            inside.setdefault(str(e.card), []).append(round(e.t, 2))
    absent = [str(m["card"]) for m in flat if not m.get("optional") and str(m["card"]) not in inside]
    if absent:
        return (f"{', '.join(sorted(set(absent)))} never fired inside {t0:.2f}-{t1:.2f}s - the member is not on the "
                f"built timeline at all")
    for m in flat:
        want = round(t0 + RW.offset_ends(m.get("offset_s", 0.0))[0], 2)
        hits = inside.get(str(m["card"]), [])
        near = min(hits, key=lambda t: abs(t - want)) if hits else None
        if near is not None and abs(near - want) > RW.OFFSET_TOL:
            return f"{m['card']}, from {want:.2f} -> {near:.2f}"
    return (f"every member's card fired inside {t0:.2f}-{t1:.2f}s but not in order inside the recipe's own "
            f"{window_s:.1f}s window (recipe_walk.match, tol {RW.OFFSET_TOL}s)")


def row_id(row: str) -> str:
    """The gate id a recorded row carries: `[FAIL] M29 1 transient cue(s) ...` -> `M29`."""
    parts = str(row).split()
    return parts[1] if len(parts) > 1 else ""


def amend_for(row: str, members: list[tuple[float, dict]], segs: list[dict]) -> str | None:
    """The offset amendment a CLOCK row asks for, or None when no offset of this recipe can answer it.

    M44 - a world plate under six seconds: the member that CLOSES the plate (the `exit`, or the `page_enter` that
    takes the world away) has to move out to M44's floor. M11 - the first chart entering unannotated: the targeted
    species that lights the page has to come back to the page's own build landing. Those are exactly two of the
    three contradictions R26-168 names, and each is answered by moving ONE member, not by lowering a gate."""
    rid = row_id(row)
    if rid == "M44":
        plate = next((i for i, s in enumerate(segs) if s["kind"] == "plate"), None)
        if plate is None:
            return None
        end = segs[plate + 1]["at"] if plate + 1 < len(segs) else None
        closer = next((m for at, m in members
                       if end is not None and abs(at - end) < 0.5 and member_axis(m["card"]) in ("exit", "page_enter")),
                      None)
        if closer is None or end is None:
            return None
        return (f"{closer['card']}, from {end:.2f} -> {GMD.PLATE_MIN_S:.2f} (M44: a world plate the eye can take in; "
                f"the proven offset leaves {end:.2f}s)")
    if rid == "M11":
        light = next(((at, m) for at, m in members
                      if member_axis(m["card"]) in ("species", "page_species")
                      and member_token(m["card"]) in LIGHT_KINDS), None)
        if light is None:
            return None
        at, m = light
        lands = float(LE.clocks()["lp_build_s"])
        return (f"{m['card']}, from {at:.2f} -> {lands:.2f} (M11 / E99 s67: the light lands within "
                f"{GMD.ANNOTATE_TOL_S:.1f}s of the page's own build landing at {lands:.2f}s, not {at:.2f}s after it)")
    return None


# --------------------------------------------------------------------------- the lab DIAGNOSES, never kills (E99 s69)
#
# THE RULING (the operator, 2026-09-17): *"it seems like our gates don't work right. they shouldn't be dismissing our
# effects/recipes, they should be guiding us on how to build with them. if a recipe is 'short' on length, that's not a
# reason to not use it, that's a reason to slot in something else after it."* A recipe is a proven combination of a few
# seconds; the gates' clocks measure the WHOLE beat, and a beat is a recipe PLUS what follows it. So a row that fires
# after the recipe's last member has landed is a HOLE IN THE BEAT - the author's next move, named - and never a verdict
# on the recipe. Three answers, and none of them is a kill:
DIAG_AS_IS = "buildable as-is"                  # no row decided inside the window
DIAG_COMPANION = "buildable with a companion"   # a row asks for the next beat, or for a placement
DIAG_NOT_ON_BED = "not on this bed"             # a member whose bind this bed has not got
# E99 s71 (the operator, 2026-09-17): *a spotlight is never the move; when a sentence names a thing, the THING
# ARRIVES.* So the companion a hole is answered with is an ARRIVAL, never a light, and a candidate whose only event
# inside its window is a light is not a beat at all - it is a light on a still frame.
DIAG_LIGHT_ONLY = "a light is not a move - the named thing should arrive (E99 s71)"
COMPANION_MOVES = ("a badge or a pill springing with its callout, a stamped prop or icon, a docked screenshot, a "
                   "flight - the thing the sentence names, arriving (E99 s71); never a light")
LIGHT_ONLY_KINDS = frozenset({"spotlight", "relight"})     # the species that only LIGHT what is already on the frame
MOVELESS_AXES = frozenset({"idle", "plate_option", "exit", "page_exit"})   # they dress a row, they are not its move
NOT_ON_BED_MARK = "NOT ON THIS BED - "          # how a dropped member says the bed cannot carry it
LAYOUT_IDS = frozenset({"M25", "M26"})          # the layout probe's rows: their fix is PLACEMENT, never a member
TOOL_FAILS = frozenset({"compile", "probe"})    # not gate rows: a build that did not compile or render is no beat
ASK_MAX = 220                                   # the row's own ask, trimmed; the WHOLE row is in `decided_by`


def row_ask(row: str) -> str:
    """The move the gate row itself names ("add motion there (a species, a caption pop, plate life)") - the operator's
    words are the gate's job (E99 s69), so they are quoted here rather than re-written."""
    tail = str(row).rsplit(" - ", 1)[-1] if " - " in str(row) else str(row)
    return tail[:ASK_MAX].strip()


_RUN = re.compile(r"\+(\d+(?:\.\d+)?)\s*s\b")      # `0:39+5.7s` - how long the gap the row found RUNS


def row_hole(row: str, spans: dict[str, tuple[float, float]] | None = None) -> tuple[float, float] | None:
    """(where the hole opens, how long it runs) - both read off what the row PRINTS, nothing inferred.

    `row_instants` reads the four forms the gates use; the length is the `+5.7s` a gap row prints after its stamp
    (`_pulse_gate`: `0:39+5.7s`). A row that prints no instant at all is a whole-cut row and has no hole."""
    ins = row_instants(str(row), spans)
    if not ins:
        return None
    at = min(a for a, _b in ins)
    end = max(b for _a, b in ins)
    runs = [float(x) for x in _RUN.findall(str(row))]
    return at, round(max(end - at, max(runs) if runs else 0.0), 2)


def last_landing(members: list[tuple[float, dict]], t0: float) -> float | None:
    """The instant the recipe's LAST member has landed on the frame - after it, the beat is the author's to fill."""
    if not members:
        return None
    return round(max(t0 + at + member_lands_s(m["card"], m.get("options")) for at, m in members), 2)


def companion_ask(row: str, last: float | None, spans: dict[str, tuple[float, float]] | None = None) -> str:
    """What this row asks the author to BUILD, and where - never a verdict on the recipe (E99 s69).

    The hole is an interval: a row whose gap RUNS past the recipe's last landing is the beat's next move, named,
    however early it opened. A layout row is answered by PLACEMENT, whenever it fired."""
    rid = row_id(row) or "the row"
    hole = row_hole(row, spans)
    at, runs = hole if hole else (None, 0.0)
    where = f" at {mmss(at)}" if at is not None else ""
    if rid in LAYOUT_IDS:
        return f"{rid}: the card sits over the page's ink{where} - place it in the page's room ({row_ask(row)})"
    ran = f" and runs {runs:.1f} s" if runs else ""
    if last is not None and at is not None and at + runs >= last - EPS:
        return (f"{rid}: the hole opens{where}{ran}, past the recipe's last member landing at {last:.2f}s - slot "
                f"the next beat there: {COMPANION_MOVES}. The row's own words: {row_ask(row)}")
    if last is not None:
        return (f"{rid}: the row fires{where}, inside the recipe's own span (its last member lands at {last:.2f}s) - "
                f"answer it with {COMPANION_MOVES}. The row's own words: {row_ask(row)}")
    return f"{rid}: the row fires{where}{ran} - answer it with {COMPANION_MOVES}. The row's own words: {row_ask(row)}"


def only_a_light(members: "list[tuple[float, dict]] | tuple") -> bool:
    """E99 s71: is the candidate's ONLY event inside its window a light? Then the thing the sentence names never
    arrives, and no gate row has to fire for that to be the finding."""
    moves = [(member_axis(m["card"]), member_token(m["card"])) for _at, m in members
             if member_axis(m["card"]) not in MOVELESS_AXES]
    return bool(moves) and all(axis in ("species", "page_species") and token in LIGHT_ONLY_KINDS
                               for axis, token in moves)


def missing_member(record: Mapping) -> str | None:
    """The member this BED has not got, when one decided: a dropped bind, or a member the walk never saw fire."""
    for line in record.get("dropped") or []:
        if NOT_ON_BED_MARK in str(line):
            return str(line).replace(NOT_ON_BED_MARK, "")
    why = str((record.get("fires") or {}).get("why") or "")
    if "never fired" in why:
        # ... unless every member the walk missed is one TODAY'S CLOCKS dropped (a badge rail at 9:16, R26-171):
        # that is a clock refusing a member, not a bind the bed has not got, and the beat around it still builds
        cards = [c for c in MEMBER_DROPS if c in why]
        if cards and all(c not in NOT_ON_BED for c in cards):
            return None
        return why
    return None


def diagnose(record: Mapping, members: "list[tuple[float, dict]] | tuple" = (),
             spans: dict[str, tuple[float, float]] | None = None) -> str:
    """The candidate's DIAGNOSIS - one of the three, and the row and the hole it names (E99 s69). Never a kill."""
    miss = missing_member(record)
    if miss:
        return f"{DIAG_NOT_ON_BED} - {miss}"
    if only_a_light(list(members)):
        return DIAG_LIGHT_ONLY
    fails = [r for r in (record.get("decided_by") or []) if str(r).startswith("[FAIL]")]
    tool = next((r for r in fails if row_id(r) in TOOL_FAILS), None)
    if tool:           # a build that did not compile or render is not a beat this bed can show the operator at all
        return f"{DIAG_NOT_ON_BED} - {tool}"
    if not fails:
        return DIAG_AS_IS
    last = last_landing(list(members), float((record.get("clip") or {}).get("t0") or 0.0))
    return f"{DIAG_COMPANION} - {companion_ask(fails[0], last, spans)}"


def recipe_verdict(record: Mapping, members: list[tuple[float, dict]], segs: list[dict],
                   spans: dict[str, tuple[float, float]] | None = None) -> str:
    """The re-proof's own answers (P65 T8) as E99 s69 leaves them - the third IS the diagnosis, because a gate never
    dismisses a recipe:

      survives as proven          - nothing inside the window failed and the recipe fired at its own offsets
      needs an amended offset     - a clock row names an offset that has to move, or the members fired out of band
      <the diagnosis>             - `buildable with a companion - ...` / `not on this bed - ...`
    """
    rows_in = list(record.get("decided_by") or [])
    for row in rows_in:
        amend = amend_for(row, members, segs)
        if amend:
            return f"needs an amended offset: {amend}"
    fails = [r for r in rows_in if r.startswith("[FAIL]")]
    fires = record.get("fires") or {}
    if not fails and fires.get("count"):
        return "survives as proven"
    if not fails and not missing_member(record):
        why = str(fires.get("why") or "the recipe did not fire on its own built timeline")
        return f"needs an amended offset: {why}"
    return diagnose(record, members, spans)


# --------------------------------------------------------------------------- the filter decides on the WINDOW

WHOLE_CUT_IDS = frozenset(OSF.ROW_ORDER)      # M35-M46: the one-shot floors, each read over the WHOLE cut
# The one-shot BAR is a whole-cut verdict too: `NOT CLEAN - motion gate (M01-M24): [FAIL] M28 ...` aggregates the
# same gate rows the lab already reads one by one, with their own instants. So its row is recorded as context and
# never decides - `compile` and `probe` still do, because a build that did not compile or render is not a candidate.
WHOLE_CUT_TOOLS = frozenset({"self-watch"})
_GATE_ID = re.compile(r"^M\d+$")               # a gate row; anything else (compile, probe, self-watch) is a TOOL row
_CLOCK = re.compile(r"\b(\d{1,3}):([0-5]\d)\b")                    # `at 0:25 (s02)` - the gates' own stamp
_AT = re.compile(r"\b(?:t=|at\s+)(\d+(?:\.\d+)?)\s*s\b")           # `at 9.51s`, `its build lands at 3.0s`
_SPAN = re.compile(r"\b(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)\b")   # `one stretch over 8s: 41.1-49.9`
_SCENE = re.compile(r"\bs(\d{2})\b")                                # `(s02)` - the scene's own span, off the timeline


def scene_spans(build: Path) -> dict[str, tuple[float, float]]:
    """`s02` -> its own span, read off the build's timeline: a row that names a scene names its seconds."""
    path = Path(build) / TIMELINE_NAME
    if not path.is_file():
        return {}
    tl = json.loads(path.read_text(encoding="utf-8"))
    return {str(s.get("scene_id")): (float(s["span"][0]), float(s["span"][1]))
            for s in tl.get("scenes", []) if s.get("scene_id") and s.get("span")}


def row_instants(text: str, spans: dict[str, tuple[float, float]] | None = None) -> list[tuple[float, float]]:
    """Every instant a gate row PRINTS, as intervals - the four forms the gates use, and nothing inferred. A row
    that prints none of them is a whole-cut row (a count, a share, a ratio) and cannot be a candidate's own."""
    out: list[tuple[float, float]] = []
    out += [(float(int(m) * 60 + int(s)),) * 2 for m, s in _CLOCK.findall(text)]
    out += [(float(t),) * 2 for t in _AT.findall(text)]
    out += [tuple(sorted((float(a), float(b)))) for a, b in _SPAN.findall(text)]
    out += [span for n in _SCENE.findall(text) if (span := (spans or {}).get(f"s{n}"))]
    return out


def inside(a: float, b: float, t0: float, t1: float) -> bool:
    """Does an instant (a == b) or a span the row printed share time with the window? A span that merely TOUCHES
    the window at an endpoint does not: the scene before the candidate's own ends where its row begins."""
    if a == b:
        return t0 - EPS <= a <= t1 + EPS
    return b > t0 + EPS and a < t1 - EPS


def decides(row: dict, t0: float, t1: float, spans: dict[str, tuple[float, float]]) -> bool:
    """Does this row decide the candidate, or is it the CUT's? A tool row always decides (a build that did not
    compile or render is not a candidate). A gate row decides only when an instant it prints falls inside the
    candidate's beat window: the Tokyo cut around that window is the approved cut, and a ONE-BEAT change cannot own
    its whole-cut floors (M35-M46) or a defect firing a minute away."""
    rid = str(row.get("id") or "")
    if not _GATE_ID.match(rid):
        return rid not in WHOLE_CUT_TOOLS
    if rid in WHOLE_CUT_IDS:
        return False
    return any(inside(a, b, t0, t1) for a, b in row_instants(str(row.get("text") or ""), spans))


def partition(rows: list[dict], t0: float, t1: float,
              spans: dict[str, tuple[float, float]]) -> tuple[list[dict], list[dict]]:
    """(the rows that DECIDE, the rows that are CONTEXT). A FAIL inside the window kills the candidate; a WARN
    inside the window is recorded and is NOT fatal; a context row is recorded and decides nothing."""
    deciding, context = [], []
    for row in rows:
        (deciding if decides(row, t0, t1, spans) else context).append(row)
    return deciding, context


# --------------------------------------------------------------------------- the run record

def now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")


def short_id(cid: str) -> str:
    """`lab:<shape>:<digest>` -> `<shape>-<digest>`, the build dir's own name."""
    parts = str(cid).split(":")
    return f"{parts[1]}-{parts[2]}" if len(parts) >= 3 else str(cid).replace(":", "-")


def load_candidates(repo: Path) -> dict[str, dict]:
    """The enumerated space by id (`lab_enumerate.py --write` is what writes it)."""
    path = Path(repo) / LE.CANDIDATES_REL
    if not path.is_file():
        raise LabBuildError(f"{LE.CANDIDATES_REL} is missing - run {LE.BUILD_CMD}")
    out: dict[str, dict] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            record = json.loads(line)
            out[record["id"]] = record
    return out


def record_path(repo: Path, batch: str, override: str | None = None) -> Path:
    return Path(override) if override else Path(repo) / BATCHES_REL / f"{batch}.jsonl"


def write_record(path: Path, records: list[dict]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes("".join(json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n"
                             for r in records).encode("utf-8"))
    return path


def shape_window_s(repo: Path, shape: str, cand: dict | None = None) -> float:
    """The shape's own window, from `beat-shapes.json` through the enumerator's offset grammar - never typed here.

    A shape with an `entry_slot` has a window PER ENTRY (the light, the hold and the leave follow the entry's own
    build landing, P65 T3), so this resolves the CANDIDATE's own entry when it is given, and the longest window the
    shape can ask for when it is not."""
    shapes, _digest = LE.load_shapes(Path(repo) / LE.SHAPES_REL)
    table = next((s for s in shapes["shapes"] if s["id"] == shape), None)
    if table is None:
        raise LabBuildError(f"{shape!r} is not a shape in beat-shapes.json - a shape is a data change in that file")
    cl, where = LE.clocks(), f"beat-shapes.json {shape}"
    entries = LE.entry_cards(table)
    if cand is not None:
        own = LE.candidate_entry_card(table, cand.get("members") or [])
        if own is not None:
            entries = [own]
    return max(LE.resolve_offset(table.get("window_s", "0"), LE.shape_clocks(table, cl, c), where) for c in entries)


# The bed's OWN kinetics dials (`build_short.main`'s call to `table.compile_timeline`) - one copy, read by both
# compiles here, so a lab build and a base build are judged under the dials the approved cut compiled under.
BED_KINETICS = {"analytic_spring": True, "min_jerk": True, "area_squash": True, "km_ink": False,
                "curvature_stroke": True}


def compile_candidate(bed, build: Path, batch: str, no_receipt: str) -> tuple[int, str | None]:
    """The kit's compile door, with the NAMED escape (P67 T2). Returns (rc, the refusal text or None) - the door's
    and the compiler's own refusals are recorded as a row, never raised through the batch."""
    try:
        rc = T.compile_timeline(
            bed.HERE, build, timeline_name=TIMELINE_NAME,
            shot_table_file=os.path.relpath(build / SHOT_TABLE_NAME, bed.HERE),
            title="Tokyo Tea Break", subtitle=f"Money Physics - recipe lab {batch}",
            episode_id="tokyo-tea-break", aspect="9:16", caption_style="phrase",
            kinetics=dict(BED_KINETICS),
            no_receipt=no_receipt)
    except BaseException as exc:                     # SystemExit is a refusal, not a crash: it becomes the row
        return 1, f"{type(exc).__name__}: {' '.join(str(exc).split())[:600]}"
    return rc, None


# --------------------------------------------------------------------------- the side-by-side sheet (the parent, 2026-09-17)
#
# A RECORD SAYS THE MEMBERS FIRED; A SHEET SAYS THE MECHANISM IS THERE. `recipe_walk` counts TOKENS on the built
# timeline, so a card thrown, a dip and a page that simply appears count as `card-becomes-the-chart` firing once -
# and the parent read exactly that on the r1 build. So every recipe candidate is drawn beside the cut its recipe was
# PROVEN in (`proof.timeline` / `proof.members_at`, read where it lies and never rebuilt - `review-link-frozen-copy`),
# and every shape candidate is drawn against its own window's bounds. The pieces are `self_watch`'s own audit-sheet
# pieces (`recipe_sheet`, `proof_frames`); nothing here re-implements a probe or a sheet.

MEMBERS_SHEET = "lab-members.png"          # <build>/lab-members.png - the members over the proof (or over the bounds)


def proof_dir_of(rec: Mapping, repo: Path) -> Path | None:
    """The PROOF cut's build dir, off the recipe's own `proof.timeline` - None when it is not on disk."""
    proof = (rec or {}).get("proof") or {}
    rel = str(proof.get("timeline") or "")
    if not rel:
        return None
    path = Path(repo) / rel
    return path.parent if path.is_file() else None


def _mean_luma(png: bytes) -> float:
    """The tile's own mean luminance - the reading M32 makes of a frame (`near-black = mean luma < 8`)."""
    import io
    from PIL import Image
    im = Image.open(io.BytesIO(png)).convert("L")
    px = list(im.getdata())
    return sum(px) / len(px) if px else 0.0


_HIDE = "(sel) => { document.querySelectorAll(sel).forEach(e => e.style.visibility = 'hidden'); }"
_SHOW = "(sel) => { document.querySelectorAll(sel).forEach(e => e.style.visibility = ''); }"
PIXEL_DELTA = 20                 # a channel difference this size is a pixel the element actually painted


def _painted(probe, base, sel: str) -> tuple | None:
    """The box an element actually PAINTS on the frame: hide it, take the frame again, and read the bounding box of
    what changed. A layout box is not a frame - this bed's rail measured y 2020-2107 in the DOM while its pills were
    off a 1920 stage entirely, and hiding them changed no pixel (2026-09-17)."""
    import io
    from PIL import Image, ImageChops
    probe.page.evaluate(_HIDE, sel)
    other = Image.open(io.BytesIO(probe.page.screenshot())).convert("RGB")
    probe.page.evaluate(_SHOW, sel)
    diff = ImageChops.difference(base, other).convert("L").point(lambda v: 255 if v > PIXEL_DELTA else 0)
    return diff.getbbox()


def _overlap(a: tuple | None, b: tuple | None) -> int:
    """The area two painted boxes share, in stage px - 0 when either painted nothing."""
    if not a or not b:
        return 0
    w = min(a[2], b[2]) - max(a[0], b[0])
    h = min(a[3], b[3]) - max(a[1], b[1])
    return int(w * h) if w > 0 and h > 0 else 0


def _rail_read(probe, t: float) -> dict:
    """What the RAIL and the CAPTION STRIP actually paint at `t`, and how much of each other they cover.

    A rail is never under the captions (the parent, 2026-09-17), and the claim has to be the FRAME's: both boxes are
    read by hiding the element and diffing the frame, never off the DOM."""
    import io
    from PIL import Image
    probe.seek(t)
    on = int(probe.page.evaluate("() => document.querySelectorAll('.pill.on').length"))
    if not on:
        return {"on": 0, "rail": None, "caption": None, "over": 0}
    base = Image.open(io.BytesIO(probe.page.screenshot())).convert("RGB")
    rail, cap = _painted(probe, base, ".pill.on"), _painted(probe, base, "#caption")
    return {"on": on, "rail": list(rail) if rail else None, "caption": list(cap) if cap else None,
            "over": _overlap(rail, cap)}


def member_sheets(repo: Path, build: Path, rec: Mapping | None, members: list[tuple[float, dict]], beat: dict,
                  rows: list[tuple], dry_run: bool) -> dict:
    """`<build>/lab-members.png`: this build's frames at the members' own LANDINGS over the proof cut's frames at its
    `members_at` (a recipe), or over the window's own readable bounds (a shape candidate). Returns the record's
    `sheets` entry - the path, the instants of both rows, and any warning, never a raised exception: a sheet that
    could not be drawn is a NOTE on the record, not a dead batch."""
    out: dict = {"members": os.path.relpath(Path(build) / MEMBERS_SHEET, repo).replace("\\", "/"),
                 "at": [], "proof_at": [], "warn": ""}
    t0, t1 = float(beat["t0"]), float(beat["t1"])
    lo, hi = readable_window(rows, t0, t1)
    at = sheet_instants(members, rows, t0, t1)
    out.update({"at": at, "bounds": [lo, hi]})
    if dry_run:
        out["warn"] = "--dry-run: no player to read, no sheet drawn"
        return out
    pdir = proof_dir_of(rec, repo) if rec is not None else None
    proof_at = [float(t) for t in ((rec or {}).get("proof") or {}).get("members_at") or []] if rec is not None else []
    out["proof_at"] = proof_at
    try:
        import probe as P                                   # imported here: the batch's other modes need no browser
        with P.Probe(Path(build), TIMELINE_NAME) as q:
            top = [(t, q.png(t)) for t in at]
            # WHAT THE FRAME ACTUALLY CARRIES, measured in the same session the sheet is drawn in, so the record can
            # be READ against the tiles: the mean luminance of every tile (a window that opens on the veil is a
            # black first tile - M32's own reading of near-black is mean luma < 8) and the number of PILLS standing
            # (a badge ladder is a rail that grows, 1 -> 2 -> 3, not one pill held for five seconds).
            out["luma"] = [round(_mean_luma(png), 1) for _t, png in top]
            rails = [_rail_read(q, t) for t in at]
            out["pills"] = [m["on"] for m in rails]
            out["rail_boxes"] = [m["rail"] for m in rails]
            out["rail_over_caption"] = [m["over"] for m in rails]
            out["caption_boxes"] = [m["caption"] for m in rails]
            bottom = [(t, q.png(t)) for t in (lo, hi)] if pdir is None else []
        if pdir is not None:
            shots = [{"recipe": str(rec.get("id")), "proof_dir": pdir, "proof_at": proof_at}]
            frames, warns = SW.proof_frames(shots, {}, P.Probe)
            bottom = frames.get(str(rec.get("id"))) or []
            out["warn"] = "; ".join(warns)
            out["proof"] = os.path.relpath(pdir, repo).replace("\\", "/")
        labels = ("this cut's members", "the proof cut" if pdir is not None else "the window's own bounds")
        head = (f"{str((rec or {}).get('id') or beat.get('sentence') or '')} - beat {beat['n']} "
                f"{t0:.2f}-{t1:.2f}s - readable {lo:.2f}-{hi:.2f}s - {labels[0]} over {labels[1]}")
        if not bottom:
            out["warn"] = (out["warn"] + "; " if out["warn"] else "") + "no frames for the lower row"
        path = SW.recipe_sheet(top, bottom, Path(build) / MEMBERS_SHEET, SW.TILE_PX, head, labels)
        out["members"] = os.path.relpath(path, repo).replace("\\", "/") if path is not None else ""
    except (Exception, SystemExit) as exc:                   # a browser that will not start is a NOTE, never a crash
        out["warn"] = f"{type(exc).__name__}: {' '.join(str(exc).split())[:300]}"
    return out


PAGE_CARD_W = 0.55          # a card wider than this share of the stage is PAGE-SIZED: more than half the frame
GROWS = ("snap=", "camera=")   # the page enters the thrown card grows into (`ledger:...:snap=<dock>`)
ZOOMS = ("focus_zoom", "chart_to", "punch")   # ... or the move that takes it to full screen inside its own row


def throw_notes(rows: list[tuple], t0: float, t1: float) -> list[str]:
    """E99 s71 (the operator, 2026-09-17): *the throw is a signature event, and a thrown full-page card zooms or
    pushes to full screen.* A translation that throws a page-sized card and then leaves it floating over the plate
    is a defect, and it is NAMED here rather than left for the frame to show."""
    out: list[str] = []
    for i, r in enumerate(rows):
        if float(r[1]) <= t0 + EPS or float(r[0]) >= t1 - EPS:
            continue
        nxt = str(rows[i + 1][2]) if i + 1 < len(rows) else ""
        for d in r[4] or []:
            opts = d[4] if len(d) > 4 else {}
            if not (t0 - EPS <= float(d[2]) <= t1 + EPS):     # the CANDIDATE's own cards; the cut's are the cut's
                continue
            if str(opts.get("arrive") or "") != "throw" or float(opts.get("centre_w") or 0.0) < PAGE_CARD_W:
                continue
            grown = any(g + str(d[0]) in nxt for g in GROWS) or any(
                str(s.get("kind")) in ZOOMS and float(s.get("at", 0)) >= float(d[2]) for s in (r[6] or []))
            if not grown:
                out.append(f"{d[0]} is THROWN at {float(d[2]):.2f}s at {float(opts['centre_w']):.2f} of the stage "
                           f"(page-sized) and nothing takes it to full screen - E99 s71: a thrown full-page card "
                           f"zooms or pushes to full screen; this translation leaves it floating over the plate")
    return out


def build_one(repo: Path, batch: str, cand: dict, beats: list[dict], batch_root: Path, dry_run: bool) -> dict:
    """One candidate, built as a beat on the bed and filtered. Returns its run record - a refused compile is a record
    carrying the row that killed it, never a dropped candidate."""
    cid, shape = cand["id"], cand["shape"]
    rec = cand.get("recipe")
    if shape not in SHAPE_BEATS:
        raise LabBuildError(f"{cid}: the shape {shape!r} has no beat in SHAPE_BEATS - a candidate is planted in a "
                            f"sentence of the approved cut, and which sentence is intelligence work (E99 s66)")
    numbers, reason = SHAPE_BEATS[shape]
    if rec is not None:
        # A RECIPE's window is its OWN (`window_s`), widened so its LAST world is not a flash: the shortest world any
        # beat may carry is M44's six seconds, and a 0.9 s page hanging off the end of a five-second plate would be a
        # defect the lab invented rather than one the recipe has (R26-168 measures the recipe, not the harness).
        rel = recipe_segments(sorted(((member_offset(m, float(rec.get("window_s") or RW.DEFAULT_WINDOW_S)), dict(m))
                                      for m in rec.get("members") or []
                                      if str(m["card"]) not in MEMBER_DROPS), key=lambda x: x[0]), rec)
        want = max(float(rec.get("window_s") or RW.DEFAULT_WINDOW_S), rel[-1]["at"] + GMD.PLATE_MIN_S)
        beat = beat_window(beats, numbers, round(want, 2), cid)
        beat["reason"] = f"{cand['act_reason']} | the beat: {reason}"
    else:
        beat = beat_window(beats, numbers, shape_window_s(repo, shape, cand), cid)
        beat["reason"] = reason
    build = Path(batch_root) / short_id(cid)
    refuse_dir(build, batch_root)
    build.mkdir(parents=True, exist_ok=True)
    note = gitignore_note(repo, batch_root)
    if note:
        print(note)
    no_receipt = f"recipe lab candidate {cid}"
    bed = import_bed(repo, build)
    rows, ws, _runtime = approved_rows(bed, dry_run)
    beat["t0"], beat["t1"] = snap_window(rows, beat["t0"], beat["t1"])
    record = {"id": cid, "shape": shape, "batch": batch,
              "beat": {k: beat[k] for k in ("n", "beats", "sentence", "t0", "t1", "reason")},
              "build": os.path.relpath(build, repo).replace("\\", "/"),
              "clip": {"t0": beat["t0"], "t1": beat["t1"]},
              "sheet": os.path.relpath(build / SHEET_NAME, repo).replace("\\", "/"),
              "no_receipt": no_receipt, "at": now()}
    drops: list[str] = []
    segs: list[dict] = []
    members: list[tuple[float, dict]] = []
    if rec is not None:
        planted, drops, segs = recipe_rows(bed, rec, beat, ws, dry_run, rows, bed_binds(rows))
        window_s = float(rec.get("window_s") or RW.DEFAULT_WINDOW_S)
        members = sorted(((member_offset(m, window_s), dict(m)) for m in rec.get("members") or []
                          if str(m["card"]) not in MEMBER_DROPS), key=lambda x: x[0])
        record["recipe"] = str(rec.get("id"))
        record["acts"] = [str(a) for a in (rec.get("acts") or [])]
        record["dropped"] = drops
        record["segments"] = segs
    else:
        planted = candidate_rows(bed, cand, beat, ws, dry_run, bed_binds(rows))
        members = sorted(((float(m["offset_s"]), dict(m)) for m in cand.get("members") or []), key=lambda x: x[0])
    table_rows = splice(rows, planted, beat["t0"], beat["t1"])
    T.write_shot_table(build / SHOT_TABLE_NAME, table_rows,
                       f'"""P65 T3 - the recipe lab: {cid} planted in beat {beat["n"]} of the Tokyo cut '
                       f'({beat["t0"]:.2f}-{beat["t1"]:.2f}s). Written by lab_build.py; do not hand-edit."""\n')
    # THE INSTANTS ARE THE MEMBERS' OWN LANDINGS, inside the window's READABLE bounds - never the boundary frame a
    # dip paints black, never the next row's first frame, and never the instant a card was thrown (the parent's read
    # of batch-r1, 2026-09-17: a black tile, a card floating on the next page's cream, and two windows with no card
    # in them at all - all three were the sheet reading the wrong three instants).
    instants = sheet_instants(members, table_rows, beat["t0"], beat["t1"])
    record["clip"] = {"t0": readable_window(table_rows, beat["t0"], beat["t1"])[0], "t1": beat["t1"]}
    gate_rows: list[dict] = []
    if dry_run:                                      # the compile and the four tools are stubbed; the rows are canned
        _rc, out = run_tool(["--dry-run", str(build)])
        gate_rows = tool_rows(out)
    else:
        rc, refusal = compile_candidate(bed, build, batch, no_receipt)
        if refusal is not None:
            gate_rows.append({"level": "FAIL", "id": "compile", "text": refusal})
        elif rc != 0:
            gate_rows.append({"level": "FAIL", "id": "compile", "text": f"the compiler exited {rc}"})
        else:
            # THE SOUND FOLLOWS THE LANDING (T8): the cues inside the window are re-derived from the SPLICED rows
            # before any gate reads the build, so M29 is asked about the candidate's own landings and not about the
            # approved cues its rows replaced.
            record["sound"] = resound(bed, build, table_rows, beat["t0"], beat["t1"])
            for line in record["sound"]["notes"]:
                print(f"      [sound] {line}")
            gate_rows += run_filter(build, bed.HERE, instants, build / SHEET_NAME)
    spans = scene_spans(build)
    deciding, context = partition(gate_rows, beat["t0"], beat["t1"], spans)
    record["decided_by"] = decided_by(deciding)          # the rows INSIDE the candidate's own window
    record["context"] = decided_by(context)              # the whole-cut floors and the approved cut's own rows
    record["fails"] = sorted({r["id"] for r in deciding if r["level"] == "FAIL"})
    if rec is not None:
        record["fires"] = recipe_fires(repo, build, rec, beat["t0"], beat["t1"])
    # E99 s69: the filter DIAGNOSES, it never kills. `survivor` stays as a DERIVED field for the readers written
    # against it (`lab_batch.survivors`) - true for both buildable answers, false only when the bed has not got
    # the member, because a beat whose member is missing is not this bed's beat to judge.
    record["notes"] = throw_notes(table_rows, beat["t0"], beat["t1"])
    record["sheets"] = member_sheets(repo, build, rec, members, beat, table_rows, dry_run)
    record["diagnosis"] = diagnose(record, members, spans)
    record["survivor"] = not record["diagnosis"].startswith(DIAG_NOT_ON_BED)
    if rec is not None:
        record["verdict"] = recipe_verdict(record, members, segs, spans)
    return record


def recipe_candidates(repo: Path, ids: list[str]) -> dict[str, dict]:
    """The named `proven` recipes as candidate records: `{id, shape, act_reason, members, recipe}`. The shape (and
    so the Tokyo beat) is chosen by the recipe's OWN first act through `ACT_SHAPES`, and the reason is carried."""
    proven = load_proven(repo)
    wanted = sorted(proven) if ids == ["all-proven"] else ids
    unknown = [i for i in wanted if i not in proven]
    if unknown:
        raise LabBuildError(f"not a `proven` recipe file in {RECIPES_REL}: {', '.join(unknown)} - the fifteen are "
                            f"{', '.join(sorted(proven))}")
    out: dict[str, dict] = {}
    for rid in wanted:
        rec = proven[rid]
        shape, why = recipe_shape(rec)
        out[rid] = {"id": rid, "shape": shape, "act_reason": why, "members": rec.get("members") or [],
                    "recipe": rec}
    return out


def run_batch(repo: Path, batch: str, ids: list[str], dry_run: bool, runs: str | None,
              builds: str | None, known: dict[str, dict] | None = None) -> tuple[list[dict], Path]:
    beats = load_beats(repo)
    known = known if known is not None else load_candidates(repo)
    root = Path(builds) if builds else bed_dir(repo) / f"{BUILD_PREFIX}{batch}"
    records = []
    for cid in ids:
        record = build_one(repo, batch, known[cid], beats, root, dry_run)
        print(f"  {record['id']}  beat {record['beat']['n']} "
              f"{record['clip']['t0']:.2f}-{record['clip']['t1']:.2f}s  {record['diagnosis']}"
              + (f"  fails={', '.join(record['fails'])}" if record["fails"] else ""))
        sheets = record.get("sheets") or {}
        print(f"      sheet   {sheets.get('members') or 'none'}"
              + (f"  ({sheets['warn']})" if sheets.get("warn") else "")
              + f"  at {', '.join(f'{t:.2f}' for t in sheets.get('at') or [])}")
        if record.get("verdict"):
            print(f"      VERDICT {record['verdict']}")
            print(f"      fires   {json.dumps(record.get('fires') or {}, sort_keys=True)[:400]}")
            for line in record.get("dropped") or []:
                print(f"      dropped {line}")
        for line in record.get("notes") or []:
            print(f"      [E99 s71] {line}")
        for line in record["decided_by"]:
            print(f"      {line}")
        for line in record.get("context") or []:
            print(f"      (context, outside {record['clip']['t0']:.2f}-{record['clip']['t1']:.2f}s) {line}")
        records.append(record)
    path = write_record(record_path(repo, batch, runs), records)
    note = record_note(repo, path)
    if note:
        print(note)
    return records, path


DIAGNOSES = (DIAG_AS_IS, DIAG_COMPANION, DIAG_NOT_ON_BED, DIAG_LIGHT_ONLY)


def check(repo: Path, batch: str, ids: list[str], runs: str | None) -> list[str]:
    """T8 leans on this: every candidate of the batch has a record, a DIAGNOSIS in the ruling's own vocabulary, its
    member sheet and its clip window on disk. The defects come back as named lines - one per defect."""
    path = record_path(repo, batch, runs)
    if not path.is_file():
        return [f"{path} is missing - the batch has not been built"]
    records = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    bad: list[str] = []
    seen = {r.get("id") for r in records}
    for cid in ids:
        if cid not in seen:
            bad.append(f"{cid}: no record in {path.name} - a candidate a gate FAILs is RECORDED, never dropped")
    for r in records:
        cid = r.get("id", "(no id)")
        if not (Path(repo) / str(r.get("sheet") or "")).is_file():
            bad.append(f"{cid}: the sheet {r.get('sheet')} is not on disk")
        diagnosis = str(r.get("diagnosis") or "")
        if not any(diagnosis.startswith(d) for d in DIAGNOSES):
            bad.append(f"{cid}: the diagnosis {diagnosis[:60]!r} is none of {', '.join(DIAGNOSES)} - E99 s69: the "
                       f"lab DIAGNOSES, it never kills (re-run lab_build.py --batch)")
        sheets = r.get("sheets") or {}
        if not (Path(repo) / str(sheets.get("members") or "")).is_file():
            bad.append(f"{cid}: the member sheet {sheets.get('members') or '(none)'} is not on disk"
                       + (f" - {sheets.get('warn')}" if sheets.get("warn") else ""))
        timeline = Path(repo) / str(r.get("build") or "") / "timeline.json"
        if not timeline.is_file():
            bad.append(f"{cid}: the build {r.get('build')} has no timeline.json - there is no clip to show")
            continue
        runtime = float(json.loads(timeline.read_text(encoding="utf-8")).get("runtime_s") or 0.0)
        clip = r.get("clip") or {}
        if not clip or float(clip.get("t1", 0)) > runtime + EPS or float(clip.get("t0", -1)) < -EPS:
            bad.append(f"{cid}: the clip window {clip} is not inside the build's own {runtime:.2f}s runtime")
    return bad


# --------------------------------------------------------------------------- the WHOLE TABLE (P66 HG1)
#
# A generated BASE (`generate_base_table.py`, P66 T4) is a WHOLE shot table, not a beat: there is no window to splice
# into, nothing decides on a window, and the read is the whole cut's. What it still needs is exactly what a candidate
# needed - the Tokyo bed around it - and the bed is `build_short.py`, whose `main()` writes the PROJECT's own
# `SHOT-TABLE-SHORT.py` and `sound/SOUND-PLAN.json` (`:528-590`) and so can never be the entry point for a base.
#
# So the mode reuses the REGISTRATION and discards the ROWS: `approved_rows` runs the bed's own authoring for real
# (the take copied, the pauses applied, the outro clock and the brand line, the caption pages, and `shot_table`'s own
# `dock_still` / `dock_chart` / `record_dock` calls, which are what put this episode's cards in the private build),
# and then the rows it returns are dropped on the floor. The rows that compile are the GIVEN table's, read through
# `table.load_rows` - the kit's own door - and never rewritten here.
#
# THE SOUND FOLLOWS THE LANDING over the whole cut, for the same reason it does inside a window (T8): the approved
# cue plan marks the APPROVED rows' landings, and a base's landings are its own. `build_short.sound_cues` is
# re-derived from the given rows and written to the PRIVATE build, and the project's plan is read-only - digested
# before the run and checked after it, so a file the approved cut owns cannot move under a base build unnoticed.

PARITY_IDS = ("M45", "M46")        # P66 T5: parity BY MECHANISM and the signature mix - the rows HG1 is read on


def digest(path: Path) -> str | None:
    """A file's sha256, or None when it is not on disk."""
    import hashlib
    path = Path(path)
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def guarded(bed) -> dict[str, str | None]:
    """The APPROVED cut's two files this mode must not move, digested: the project's cue plan and its shot table."""
    return {rel: digest(Path(bed.HERE) / rel) for rel in (PROJECT_PLAN_REL, APPROVED_TABLE)}


def check_guard(bed, before: Mapping[str, str | None]) -> None:
    """The after half of the guard - a refusal BY NAME, never a warning printed into a scroll."""
    for rel, was in before.items():
        if digest(Path(bed.HERE) / rel) != was:
            raise LabBuildError(f"{rel} moved under this run - the whole-table mode never writes the APPROVED cut's "
                                f"files (`build_short.main` writes both, which is why it is never called)")


def write_cue_plan(bed, build: Path, rows: list[tuple], table: Path) -> tuple[Path, list[dict]]:
    """The cue plan the BED's own writer makes of the GIVEN rows, into the PRIVATE build (never the project's).

    The shape is the project plan's own - its dials kept, its `cues` replaced - because the compiler and the gates
    read a plan of that shape and this tool keeps no second opinion about one."""
    cues = derive_cues(bed, rows)
    src = Path(bed.HERE) / PROJECT_PLAN_REL
    plan = json.loads(src.read_text(encoding="utf-8")) if src.is_file() else {}
    plan["cues"] = cues
    plan["source"] = (f"re-derived by lab_build.py --table {Path(table).name} through build_short.sound_cues "
                      f"(P66 HG1); the approved {PROJECT_PLAN_REL} is untouched")
    out = Path(build) / CUE_PLAN_NAME
    out.write_text(json.dumps(plan, indent=1), encoding="utf-8")
    return out, cues


def bed_id(bed) -> tuple[str, str]:
    """`(the episode id, the title)` the BED's own module declares - never this tool's opinion. The base is
    compiled for the project the table was generated for (E99 s72 Apply 6), so the timeline carries that
    episode's id: the player, the gates and the probe all key off it."""
    ep = getattr(bed, "EP", None)
    episode = str(getattr(ep, "episode_id", "") or Path(bed.HERE).name)
    return episode, str(getattr(bed, "TITLE", "") or episode)


def compile_table(bed, build: Path, label: str, shot_table_file: str, no_receipt: str) -> tuple[int, str | None]:
    """The kit's compile door on a WHOLE table. Returns (rc, the refusal text or None), as `compile_candidate` does:
    the door's and the compiler's own refusals become a `[FAIL] compile` row in the record, never a crash."""
    episode, title = bed_id(bed)
    try:
        rc = T.compile_timeline(
            bed.HERE, build, timeline_name=TABLE_TIMELINE_NAME, shot_table_file=shot_table_file,
            title=title, subtitle=f"Money Physics - base {label}",
            episode_id=episode, aspect="9:16", caption_style="phrase",
            kinetics=dict(BED_KINETICS), no_receipt=no_receipt)
    except BaseException as exc:                     # SystemExit is a refusal, not a crash: it becomes the row
        return 1, f"{type(exc).__name__}: {' '.join(str(exc).split())[:600]}"
    return rc, None


def table_rel(bed, table: Path) -> str:
    """The table's path RELATIVE to the episode dir - what `table.compile_timeline` hands the compiler."""
    try:
        rel = os.path.relpath(Path(table).resolve(), Path(bed.HERE).resolve()).replace("\\", "/")
    except ValueError:                               # a different drive on Windows
        rel = ".."
    if rel.startswith(".."):
        raise LabBuildError(f"{table}: the compiler reads a shot table by a path RELATIVE to the episode dir "
                            f"(`table.compile_timeline`), so a base table lives under {Path(bed.HERE).name}/")
    return rel


def build_sheets(repo: Path, build: Path) -> list[str]:
    """Every sheet the tools left - the build dir's own and `self_watch`'s (`SHEET_DIR`, the opening's tiles) - plus
    the bar's report and the gate probe's JSON. These are the paths a watch card shows; none is written here."""
    build = Path(build)
    out: list[str] = []
    for where in (build, build / SW.SHEET_DIR):
        out += [os.path.relpath(p, repo).replace("\\", "/") for p in sorted(where.glob("*.png"))]
    for name in (SW.REPORT_NAME, PROBE_GATE_NAME):
        if (build / name).is_file():
            out.append(os.path.relpath(build / name, repo).replace("\\", "/"))
    return out


def build_table(repo: Path, table: Path, into: Path, label: str, dry_run: bool, runs: str | None = None) -> dict:
    """One WHOLE table built on the bed in a PRIVATE dir, gated and probed, and recorded as ONE record."""
    repo, table, into = Path(repo), Path(table), Path(into)
    if not table.is_file():
        raise LabBuildError(f"{table} is not a file - --table takes a shot table the kit wrote "
                            f"(`generate_base_table.py <project> <build> --table <path>` writes one)")
    refuse_by_name(into, bed_dir(repo, table))   # ... including the TABLE's own bed's approved build dir (M4)
    refuse_if_served(into)
    into.mkdir(parents=True, exist_ok=True)
    rows = T.load_rows(table)
    if not rows:
        raise LabBuildError(f"{table} carries no rows - a base is a whole table, and an empty one is not a cut")
    end_s = max(float(r[1]) for r in rows)
    bed = import_bed(repo, into, bed_dir(repo, table))   # the table's OWN project is the bed (E99 s72 Apply 6)
    rel = table_rel(bed, table)
    before = guarded(bed)
    no_receipt = f"P66 HG1 base: {label}"
    record: dict = {"label": label, "mode": "table", "rows": len(rows), "end_s": round(end_s, 2),
                    "table": os.path.relpath(table, repo).replace("\\", "/"),
                    "build": os.path.relpath(into, repo).replace("\\", "/"),
                    "timeline": TABLE_TIMELINE_NAME, "no_receipt": no_receipt, "at": now()}
    note = gitignore_note(repo, into)
    if note:
        print(note)
    # THE BED REGISTERS, THE GIVEN TABLE DECIDES: the take, the words, the caption pages and every dock and chart
    # asset `build_short.shot_table` registers - and then its rows are dropped (they are the APPROVED cut's).
    bed_rows, _ws, _runtime = approved_rows(bed, dry_run)
    record["bed_rows_discarded"] = len(bed_rows)
    plan_path, cues = write_cue_plan(bed, into, rows, table)
    record["sound"] = {"plan": os.path.relpath(plan_path, repo).replace("\\", "/"), "cues": len(cues), "notes": []}
    gate_rows: list[dict] = []
    if dry_run:                                      # the compile and the four tools are stubbed; the rows are canned
        _rc, out = run_tool(["--dry-run", str(into)])
        gate_rows = tool_rows(out)
    else:
        rc, refusal = compile_table(bed, into, label, rel, no_receipt)
        if refusal is not None:
            gate_rows.append({"level": "FAIL", "id": "compile", "text": refusal})
        elif rc != 0:
            gate_rows.append({"level": "FAIL", "id": "compile", "text": f"the compiler exited {rc}"})
        else:
            notes = cue_notes(cues, row_landings(rows, 0.0, end_s)) + embed_cues(bed, into, cues,
                                                                                TABLE_TIMELINE_NAME)
            notes += bind_embedded_cues(into, plan_path, TABLE_TIMELINE_NAME)   # E99 s72: bound to what fires
            record["sound"]["notes"] = [n for n in notes if n]
            for line in record["sound"]["notes"]:
                print(f"      [sound] {line}")
            gate_rows += run_filter(into, bed.HERE, [], None, TABLE_TIMELINE_NAME, gate=True)
    check_guard(bed, before)
    record["flagged"] = decided_by(gate_rows)        # every FAIL and WARN row of the whole cut, verbatim
    record["parity"] = [f"[{r['level']}] {r['id']} {r['text']}".strip()
                        for r in gate_rows if r["id"] in PARITY_IDS]
    record["fails"] = sorted({r["id"] for r in gate_rows if r["level"] == "FAIL"})
    record["warns"] = sorted({r["id"] for r in gate_rows if r["level"] == "WARN"})
    record["sheets"] = build_sheets(repo, into)
    record["clean"] = not record["fails"]
    path = write_record(record_path(repo, label, runs), [record])
    record["record"] = os.path.relpath(path, repo).replace("\\", "/")
    note = record_note(repo, path)
    if note:
        print(note)
    return record


# --------------------------------------------------------------------------- the CLI

def main(argv: list[str] | None = None) -> int:
    # The record and the console keep every gate row VERBATIM, and Tokyo's own bracket label carries a real minus
    # sign (U+2212). On Windows a redirected stdout is cp1252, so the tool reconfigures its own stream the way
    # `gate_one_shot_floor.py:1180` does rather than mangling a row it was asked to quote.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("--batch", help="the batch id - its records land in batches/<batch>.jsonl")
    ap.add_argument("--candidates", help="candidate ids, comma-separated")
    ap.add_argument("--shape", help="every candidate of one beat shape")
    ap.add_argument("--recipes", help="P65 T8 / R26-168: `proven` recipe ids (or `all-proven`) built as candidates - "
                                      "each in the Tokyo beat its own first act chooses, under today's clocks")
    ap.add_argument("--check", action="store_true",
                    help="re-read runs/<batch>.jsonl and exit 1 on a missing record, sheet or clip window")
    ap.add_argument("--dry-run", action="store_true", help="author and splice the rows; compile and render nothing")
    ap.add_argument("--repo", default=str(REPO))
    ap.add_argument("--runs", dest="runs", metavar="PATH",
                    help=f"the batch record's path (default {BATCHES_REL}/<batch>.jsonl)")
    ap.add_argument("--builds", help="the batch's build root (default <bed>/build-lab-<batch>)")
    ap.add_argument("--table", help="P66 HG1: build a WHOLE shot table (a generated BASE) on the bed - no window, "
                                    "no splice; the rows are the table's and the bed only registers")
    ap.add_argument("--into", help="--table's PRIVATE build dir (never `build-short*`, never a dir being served)")
    ap.add_argument("--label", help="--table's label - its record lands in batches/<label>.jsonl")
    a = ap.parse_args(argv)
    repo = Path(a.repo)
    try:
        if a.table:
            if not (a.into and a.label):
                raise LabBuildError("--table needs --into <a private build dir> and --label <text>: the mode builds "
                                    "ONE whole table into ONE named dir and records it under that label")
            if a.batch or a.candidates or a.shape or a.recipes or a.check:
                raise LabBuildError("--table is the WHOLE-table mode (a generated BASE, P66 HG1) and takes no "
                                    "candidates, no shape, no recipes and no --check: those are the window's")
            record = build_table(repo, Path(a.table), Path(a.into), a.label, a.dry_run, a.runs)
            print(f"  {record['label']}  {record['rows']} rows to {record['end_s']:.2f}s -> {record['build']}  "
                  f"(the bed registered and its own {record['bed_rows_discarded']} rows were discarded)")
            for line in record["parity"]:
                print(f"      {line}")
            for line in record["flagged"]:
                print(f"      {line}")
            print(f"  sheets  {', '.join(record['sheets']) or 'none on disk'}")
            print(f"  wrote {record['record']}")
            print(f"RESULT: {record['label']} {len(record['fails'])} FAIL row(s), {len(record['warns'])} WARN "
                  f"row(s) - a BASE is offered for a watch (E99 s38), never judged here")
            return 0
        if not a.batch:
            raise LabBuildError("--batch is required outside the whole-table mode (--table --into --label)")
        ids: list[str] = [c.strip() for c in (a.candidates or "").split(",") if c.strip()]
        if a.shape:
            ids += [c["id"] for c in load_candidates(repo).values() if c["shape"] == a.shape]
        known: dict[str, dict] | None = None
        if a.recipes:
            known = recipe_candidates(repo, [r.strip() for r in a.recipes.split(",") if r.strip()])
            ids += list(known)
        if a.check:
            bad = check(repo, a.batch, ids, a.runs)
            for line in bad:
                print(f"FAIL: {line}")
            print(f"RESULT: {a.batch} {'FAIL' if bad else 'PASS'} ({len(bad)} defect(s))")
            return 1 if bad else 0
        if not ids:
            raise LabBuildError("name the candidates: --candidates <id,...> or --shape <shape>. The lab never builds "
                                "the whole space in one batch - a batch the operator cannot read in one sitting is "
                                "not a batch (R26-176)")
        if known is None:
            unknown = [c for c in ids if c not in load_candidates(repo)]
            if unknown:
                raise LabBuildError(f"not in {LE.CANDIDATES_REL}: {', '.join(unknown)} - a candidate is enumerated "
                                    f"before it is built ({LE.BUILD_CMD})")
        records, path = run_batch(repo, a.batch, sorted(dict.fromkeys(ids)), a.dry_run, a.runs, a.builds, known)
        for name in (DIAG_AS_IS, DIAG_COMPANION, DIAG_NOT_ON_BED):
            n = sum(1 for r in records if str(r.get("diagnosis") or "").startswith(name))
            if n:
                print(f"  {name}: {n}")
        for verdict in ("survives as proven", "needs an amended offset"):
            n = sum(1 for r in records if str(r.get("verdict") or "").startswith(verdict))
            if n:
                print(f"  {verdict}: {n}")
        print(f"  wrote {os.path.relpath(path, repo)}")
        print(f"RESULT: {a.batch} {len(records)} candidate(s) DIAGNOSED - the lab never kills one (E99 s69)")
        return 0
    except LabBuildError as exc:
        print(f"FAIL: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
