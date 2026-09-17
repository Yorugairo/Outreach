"""The authoring kit - SHAPES: the AUTHORED beat plan in, the approved skeleton out (P66 T3).

    from authoring import shapes as SH, table as T
    plan = SH.load_plan(build / "BEAT-PLAN.jsonl")          # M41's schema, written by the AUTHOR
    rows, why = SH.compile(plan, words, SH.DEFAULTS, "9:16")
    T.write_shot_table(path, rows, header)                   # the kit's own row grammar, unchanged

THE DOCTRINE LINE, in one sentence: `authoring/recipes.py:1-20` ("NOT AN ALLOCATOR") and
`docs/content-video-engine/PIPELINE.md:33` ("Stage 7 is AUTHORED. There is no allocator") both
STAND, because this module consumes an AUTHORED beat plan - the intelligence work E99 s66 reserved
to an agent or the operator - and fills nothing by count; E99 s68 outranks the older reading of
"authored" as "every row typed by hand": the author still decides every beat, and now edits a BASE
instead of a blank page. **The output is a BASE, never a cut.** Nothing here is chosen to hit a
rate: M16's pulse is MEASURED (`event_gaps`) and never filled, because a loop that fills slots by
count answers "how many fit" instead of "which one belongs".

It never invents. A plan M41 would fail (a beat with no record, an empty `comparator.compared_to`,
a null recipe with no `why_none`) is REFUSED by name, and a hole the plan cannot fill is refused
naming the beat, the skeleton and the hole. The ONE softer case, named in `why` rather than raised:
a SECOND mark or card (`{datum_b}`, `{dock_b}`) is the skeleton's extra, not the beat's claim, so a
plan that names one gets the row without the extra - and the same for a `{dock}` on a beat whose
plan names no evidence at all. Less than the skeleton asked for is never MORE than the plan said.

THE APPROVED SHAPE, enforced BY CONSTRUCTION (E99 s67 Apply 1-6, E47, E65, R26-171/172, M44):

  * the first beat is the page ON ITS AXES drawing under the hook - the open IS the chart; the page
    MOUNTS over the hook's world instead when the plan's first beat carries a clip or plate world
    (then the hook and that page are ONE row: a page never enters twice);
  * a page whose number lands `MOUNT_AT_OR_AFTER_S` (7.0 s) or more after its entry gets
    `mount=<s>`, never `built`; every other page enters by its axes;
  * a world change exits by `dip` (E47), page to page by `suck` or `cut`, and NEVER into a mount -
    the mount is itself the transition;
  * a return uses `spiral`;
  * a dock reads then parks in the page's own room (E65) and holds to the row's own end;
  * no world plate row is shorter than `plate_hold_s` (M44 `PLATE_MIN_S`);
  * at 9:16 no `badges` rail is emitted (R26-171); the PARK is emitted in both aspects - R26-172 is
    WITHDRAWN and a park is how a page makes room for a card (`place_cards`);
  * a light is emitted ONLY on a sentence that POINTS - the plan's own `capabilities` name a datum,
    an index, a point or a region - and never before the page's chart LANDS (Apply 1-2). The landing
    is the page's own (`gate_motion_density`): `PAGE_BUILD_END_S` on a roll-out, `LP_BUILD_S` on an
    axes entry, `mount_s + PAGE_BUILD_END_S - ROLL - SAVOR - FIELD` on a mount, `LP_SPIRAL_IN_S` on
    a spiral - a flat 7.4 s would put every axes page's light four seconds past its own chart.

THE BEAT'S NAMED MOVES (P66 T3 continued, 2026-09-17). One skeleton row per authored GROUP leaves a
long group with ONE event - a read-back plan's eleven-beat opening group measured a 32 s gap on M16.
The answer is not to fill by count (there is no allocator here) and not a looser gate: THE BEAT PLAN
IS THE INTELLIGENCE (E99 s66) and it already names, per sentence, what the cut does. A plan record
MAY carry:

    "moves": [{"kind": "<a species kind, or `dock`>", "at_word": "<a phrase of THIS beat's sentence>",
               "target": {...}, "label": "...", "dur": 1.2, "asset": "dock-x", "options": {...}}]

and `compile` realises each beat's moves on its group's row, timed by `at_word` INSIDE that beat's
own `[t0, t1]` - the take is the clock (`words`), never a stopwatch, and a phrase the beat's own
sentence does not carry is refused by name. `kind` is the COMPILER's own vocabulary
(`build_scene_timeline_f.SPECIES_KINDS`) and a card's options are the compiler's own (`DOCK_OPTS`),
so a move that is legal here is legal there. `label` is written into the field that kind carries its
words in (`LABEL_FIELD`: a figure's `text`, a callout's `label`); `options` is the species' or the
card's OWN remaining fields, copied verbatim - the compiler writes them and invents none. Every rule
above still holds over a move, and a move is REFUSED rather than silently moved: a light asked for
before its page's chart lands names the beat and the rule, and so does a camera move over a Ken
Burns (s9.28 C3).

A beat with NO moves contributes nothing - and SAYS so: `why` gains one record per silent beat
(`{beat, silent, sentence, note}`), so the agent reads where the base is a base and not a cut
(E99 s68: the base the agent modifies). `event_gaps` still MEASURES whatever results.

THE POSITIONAL RULE. Twelve of the twenty-five records in an approved read-back plan carry
`act: "none of the 11 - <what it does>"`: the sentence plays none of the twelve acts
(SPECIES-BY-SENTENCE.md). Such a beat is NEVER refused - it is chosen by its SHAPE and its
POSITION, in this order:

  1. the FIRST beat is the open;
  2. a beat whose `act` or `capabilities` name a RETURN (the spiral, the ring, a callback, the page
     coming back) is the return;
  3. a beat whose world is a ledger PAGE is a page beat - the page-to-page transform when the next
     world is a page too, the held page when the plan names a dock over it, else the page whose
     number lands at N;
  4. every other beat is a narrative PLATE.

THE VARIETY RULE is counted on SKELETON IDS, not on signature words (P66 T2: the approved cuts
themselves carry consecutive signature words - Japan's throw -> snap pair reads card, card).

Nothing in this module names an episode (`authoring/__init__.py:12-15`): the plan, the words, the
defaults and the aspect all arrive as ARGUMENTS.
"""
from __future__ import annotations

import copy
import json
import re
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
REPO = Path(__file__).resolve().parents[4]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import gate_motion_density as MD  # noqa: E402  (the gates' own clocks, by name - never re-typed here)

from . import table as T, words as W  # noqa: E402

SKELETON_DIR = "content/video_engine/effects/skeletons"
MIX_NAME = "approved-mix.json"

# --- the gates' constants, imported and never re-typed -----------------------------------------
PAGE_BUILD_END_S = MD.PAGE_BUILD_END_S          # 7.4: a rolled-out page's chart lands here (M11's annotation clock)
ANNOTATE_TOL_S = MD.ANNOTATE_TOL_S              # M11 1.5: the first chart's species fires WITH its landing
ANNOTATED_KINDS = MD.ANNOTATED_KINDS            # M11: the kinds that ANNOTATE a chart's divergence (+ the build_to's cap)
CHART_HOLD_MAX_S = MD.OPENING_CHART_HOLD_MAX_S  # M12 6.0: a chart is never held as homework
PULSE_MAX_S = MD.SHORT_PULSE_MAX_S              # M16 2.5: MEASURED by `event_gaps`, never filled (no allocator)
PLATE_MIN_S = MD.PLATE_MIN_S                    # M44 6.0: no world plate row under six seconds
MOUNT_AT_OR_AFTER_S = 7.0                       # E99 s67 Apply 3; every skeleton states it as `rules.mount_at_or_after_s`

DEFAULTS: dict = {
    "page_entry": "axes",         # E99 s67 Apply 6: a page enters by its axes unless its number lands late
    "light_after_build": True,    # E99 s67 Apply 1-2: no light over the build
    "card_in_page_room": True,    # E65: a dock reads, then parks in the page's own room and stays
    "no_rails_9_16": True,        # R26-171
    "plate_hold_s": PLATE_MIN_S,  # M44
    "park_scale": 0.52,           # the park a page makes room with, measured on the approved cut:
    "park_anchor": "top",         # (the skeleton `page-parks-to-make-room-for-the-card` cites the table's own line)
}
# R26-172 ("no `chart_to park` at 9:16") is WITHDRAWN - the parent's read of base v3 beside the approved
# cut, 2026-09-17: at 56.72 / 57.52 s the APPROVED PORTRAIT cut parks its page small at the top and the
# clipping and the wafer card take the room below, while the base left the page full size and dropped both
# cards over its ink. THE PARK IS HOW A PAGE MAKES ROOM FOR A CARD (`build_short.py:314` 0.55 for the two
# fingers, `:361-367` 0.52 for the record and the fab, `:394` 1.0 - the UN-PARK as the cards leave). So no
# default strips one, no library filter hides the park skeletons, and `place_cards` MAKES one when a card
# lands on a page with no room (`park_scale` / `park_anchor` above).

ACTS = ("QUOTES", "RANKS", "COMPARES", "DIVIDES", "NAMES", "EXPLAINS",
        "TURNS", "BREAKS", "SPANS", "SETS", "RETRACTS", "COUNTS")
NO_ACT = "none of the"           # how a read-back plan says the sentence plays none of the twelve

SHAPE_OPEN = "open-on-the-chart"
SHAPE_PAGE = "page-number-lands-at-n"
SHAPE_HELD = "held-page-hosts-the-docks"
SHAPE_TRANSFORM = "page-to-page-transform"
SHAPE_PLATE = "plate-carries-a-card"
SHAPE_RETURN = "return"

RETURN_TOKENS = ("spiral", "returns", "the return", "callback", "call back", "comes back",
                 "the ring", "ring's")
POINTS_AT = ("datum", "index", "region", "point", "bracket", "spread", "peak",
             "the low", "the bar", "callout", "spotlight", "build_to", "figure")
NUMBER_WORDS = ("percent", "billion", "trillion", "million", "thousand", "hundred", "dollars",
                "half", "twice", "double", "a tenth")
LIGHT_KINDS = ("spotlight", "callout", "focus_zoom", "ring", "punch", "figure", "note")
# E99 s67 Apply 1-2 is about the LIGHT over the build - the lamp that darkens the page around a point.
# It is not about the marks that ANNOTATE the chart as it lands: a `build_to` IS the build (M11 counts
# its cap as the annotation), and a callout, a figure or a note on the number's word is the sentence's
# own mark, which the approved cuts write at the word and not a beat later (P66 T3c, the third pass).
LIGHT_AFTER_BUILD_KINDS = ("spotlight", "focus_zoom")
ENTRY_SUFFIX = re.compile(r":(axes|spiral|built|morph|(?:mount|snap|camera)=(?:[A-Za-z0-9_.-]+|\{[a-z0-9_]+\}))")
THEN_OPT = re.compile(r";then=([^;]+)")          # the page's CHAIN of other chart states (build_scene_timeline_f:112)

# --- THE CHART_TO VERBS (E99 s70 Apply 3) -------------------------------------------------------
# The three that TRAVEL to a state the plate id declares as `;then=<series>:<variant>`, the two the
# compiler DERIVES from the page's own series, and the two that name no state at all. A move whose
# state does not exist redraws nothing - the first base's six chart_to moves all came out as no-ops
# because the translation dropped the chain (the critic of 2026-09-17, mechanism 7 / table-2 row 3).
CHART_TO_TO_STATE = ("recast", "morph", "remake")
CHART_TO_DERIVED = ("rescale", "extend")
CHART_TO_NO_STATE = ("park", "compare")
CHART_TO_KINDS = CHART_TO_TO_STATE + CHART_TO_DERIVED + CHART_TO_NO_STATE
LINE_VARIANTS = ("line", "dense-line", "lines", "tiers")
BARS_VARIANTS = ("bars", "signed-bars", "breakthrough")
UNPARK_SCALE = 1.0               # CAPABILITIES.md:120 - a park to 1.0 is the UN-PARK: the chart re-takes the stage
TIME_HOLE = re.compile(r"^\{(t[01])\}([+-][0-9.]+)?$")
HOLE = re.compile(r"\{([a-z0-9_]+)\}")
DOCK_ID = re.compile(r"(?<!recipe:)\b(dock-[a-z0-9-]+)")   # `recipe:dock-...` is a RECIPE name, never a dock asset
DATUM_ID = re.compile(r"\b(?:datum|index|from_index|to_index)[ _]*(?:index )?(\d+)")
MOUNT_S = re.compile(r"mount=([0-9.]+)")
DOCK_LANE = 0                    # the dock tuple's second element: the lane a card arrives on
SPECIES_TAIL_S = 0.3             # a species with less than this left on the row has no room to read: it is dropped
MOUNT_S_DEFAULT = MD.LP_FIELD_S  # the player's own default when a spec carries no mount_s (gate_motion_density:1179)

# --- the beat's named MOVES (P66 T3 continued) --------------------------------------------------
MOVE_DOCK = "dock"               # the one move kind that is not a species: a CARD arrives over the world
MOVE_SLOT = "slot"               # a dock move's lane, the dock tuple's 2nd element - an option here, not a DOCK_OPT

# --- E65: the card's ROOM on a page (P66 T3c) ---------------------------------------------------
CARD_PLACE_KEYS = ("centre_x", "centre_y", "centre_w")   # the AUTHOR's own placement: kept verbatim (E99 s66)
CARD_ROOM_ASPECT = 1.0   # the height a room must hold per unit of card WIDTH when the card's own aspect is not
                         # known here (the asset is registered by the EPISODE at build time, never by the kit):
                         # the approved cards measure 0.59-1.00, and a row that docks a portrait CHART card
                         # names its own `card_aspect`, which this placer keeps verbatim with the rest
MOVE_KEYS = ("kind", "at_word", "target", "label", "dur", "asset", "options")
CAMERA_MOVES = ("punch", "focus_zoom", "pull_back")   # s9.28 C3: one per row, and never over a Ken Burns
LABEL_FIELD = {"figure": "text", "note": "text", "retitle": "text", "stamp": "text",
               "callout": "label", "bracket": "label", "span": "label", "chip": "label",
               "ring": "label", "peel": "label"}   # where a kind carries THE WORDS it writes on the page
DEFAULT_LABEL_FIELD = "label"
CONTINUITY_ENTRIES = ("snap", "camera", "morph")   # E99 s70: the entries that CARRY the world that was there into
                                                  # this one - the card becomes the page, the camera pushes to it, the
                                                  # object becomes the chart. They are the continuity the operator said
                                                  # was dropped, and the CLOCK never replaces one with a bare axes: an
                                                  # authored continuity entry STANDS (the plan is the intelligence, s66)
BUILT_ON_ARRIVAL = ("snap", "camera")   # the two entries whose chart is ALREADY on the page when it arrives
                                        # (`page_land_offset` reads 0.0 for both): the page snaps to a card, or the
                                        # camera does. A page the AUTHOR gave one of these is a page whose light may
                                        # land on the first word of its own sentence - and both approved cuts do it.
EPS = 0.005                      # the closed-interval slack, as the gates use it


class Refused(ValueError):
    """The plan cannot be compiled AS WRITTEN - named, never guessed around."""


# --------------------------------------------------------------------------- the library and the plan

def load_library(repo: Path | str | None = None) -> list[dict]:
    """Every skeleton file under `effects/skeletons/`, ordered by id - the order every fallback and
    every tie is resolved in, so a second compile of one plan is byte-identical to the first."""
    root = Path(repo) if repo is not None else REPO
    d = root / SKELETON_DIR
    out = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(d.glob("*.json")) if p.name != MIX_NAME]
    if not out:
        raise Refused(f"no skeleton library at {d} - P66 T2 writes it")
    return sorted(out, key=lambda s: s["id"])


def load_plan(path: Path | str) -> list[dict]:
    """`<build>/BEAT-PLAN.jsonl` as records (M41's schema). The AUTHOR wrote it; this reads it."""
    text = Path(path).read_text(encoding="utf-8")
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def check_plan(plan: list[dict]) -> None:
    """The three gaps M41 names, refused BY NAME before a single row is shaped
    (`gate_one_shot_floor.plan_gaps`; SRC_M41 - "a beat with no record, an empty
    comparator.compared_to, or a null recipe with no why_none is a gap")."""
    if not plan:
        raise Refused("M41: the beat plan is empty - the compiler's input is AUTHORED (E99 s66), never generated")
    gaps: list[str] = []
    numbers = [int(r["beat"]) for r in plan if isinstance(r.get("beat"), (int, float))]
    if len(numbers) != len(plan):
        gaps.append("a record carries no `beat` number")
    for n in range(1, (max(numbers) if numbers else 0) + 1):
        if n not in numbers:
            gaps.append(f"beat {n} has no record")
    for r in plan:
        n = r.get("beat", "?")
        if not str((r.get("comparator") or {}).get("compared_to") or "").strip():
            gaps.append(f"beat {n} compares to nothing")
        if not r.get("recipe") and not str(r.get("why_none") or "").strip():
            gaps.append(f"beat {n} has no recipe and no why_none")
        for key in ("t0", "t1", "sentence", "plate"):
            if r.get(key) in (None, ""):
                gaps.append(f"beat {n} names no {key}")
    if gaps:
        raise Refused(f"M41: the beat plan has {len(gaps)} gaps and is not compilable: "
                      + "; ".join(gaps[:12]) + (f"; +{len(gaps) - 12} more" if len(gaps) > 12 else ""))
    for r in plan:
        check_moves(r)   # the beat's NAMED moves: the kind, the phrase, the card's asset and its options


# --------------------------------------------------------------------------- reading one beat

def acts_of(record) -> set:
    """The acts a record names. A record that says `none of the 11 - ...` names NONE: its own prose
    may quote an act word (the classifier's BREAKS hit), and the positional rule owns that beat."""
    act = str((record or {}).get("act") or "")
    if act.strip().lower().startswith(NO_ACT):
        return set()
    return {a for a in ACTS if re.search(rf"\b{a}\b", act)}


def world_of(plate: str) -> str:
    """The KIND of world a plate id names: `page` (a ledger page), `clip`, or `plate`."""
    p = str(plate or "")
    return "page" if p.startswith("ledger:") else "clip" if p.startswith("clip:") else "plate"


def page_of(plate: str) -> str:
    """`{page}`: the series and variant a ledger plate names, with its entry suffix, its `:cut` and
    its `;options` tail stripped - `ledger:ev-x-v1:line:315:right:mount=2.0:cut` -> `ev-x-v1:line:315:right`."""
    body = str(plate).split(";", 1)[0]
    body = body[len("ledger:"):] if body.startswith("ledger:") else body
    body = ENTRY_SUFFIX.sub("", body)
    return body[:-len(":cut")] if body.endswith(":cut") else body


def plate_of(plate: str) -> str:
    """`{plate}`: the plate or clip id, with its `;options` tail stripped."""
    return str(plate).split(";", 1)[0]


# --------------------------------------------------------------------------- the page's own CHAIN of states

def states_of(plate: str) -> list[str]:
    """The `;then=<series>:<variant>[:<emphasize>]` CHAIN a plate id declares, in order.

    `build_scene_timeline_f:112`: every `then=` is another full `ledger_page.v1` spec on
    `world.page_states`, built at load and hidden until a `chart_to` reaches it. A `recast`, a
    `morph` or a `remake` names one of them as `state: <n>`; WITHOUT the chain the move redraws
    nothing and the frame never changes (E99 s70 Apply 3 - the chain IS the transition, doc 29
    Part 3 - so a transform that would render nothing is refused at compile, by name).
    """
    return [s.strip() for s in THEN_OPT.findall(str(plate or "")) if s.strip()]


def variant_of(spec: str) -> str:
    """The page VARIANT a `<series>:<variant>[:<emphasize>]` spec (or a resolved `{page}`) names."""
    parts = [p for p in str(spec or "").split(":") if p]
    return parts[1] if len(parts) > 1 else ""


def with_states(plate: str, states: list[str]) -> str:
    """The AUTHOR's `;then=` chain carried onto a resolved ledger plate.

    `page_of` strips a plate's `;options` tail to fill `{page}`, so a skeleton's template rebuilds
    the id WITHOUT the chain - which is exactly how the first base's `chart_to recast` moves came out
    as no-ops. The chain belongs to the PLAN's page and never to a skeleton (a skeleton names no
    episode, `authoring/__init__.py:12-15`), so it is carried across here.
    """
    if not states or not str(plate).startswith("ledger:"):
        return plate
    have = states_of(plate)
    return str(plate) + "".join(f";then={s}" for s in states if s not in have)


def group_states(g: dict) -> list[str]:
    """Every `;then=` state the beats of one group declare, in the order they declare them."""
    out: list[str] = []
    for b in g.get("beats") or []:
        for s in states_of(b.get("plate", "")):
            if s not in out:
                out.append(s)
    return out


def chart_to_error(sp: dict, plate: str, beat_n) -> str | None:
    """Why this `chart_to` would render NOTHING on this page - the message, or None (E99 s70 Apply 3).

    A transform is a REFUSAL, never a silent no-op: a `to` the compiler does not know; a verb that
    travels to a page state on a plate declaring no `;then=` chain (or fewer states than the move
    asks for); a pair the page's own FORM does not admit (a morph is line to line, a remake is line
    to bars); a derived verb with nothing to derive from; a `state` on a verb that has none.
    """
    to = str(sp.get("to") or "")
    where = f"beat {beat_n}: the chart_to {to or '<unnamed>'} at {sp.get('at')}"
    if not str(plate).startswith("ledger:"):
        return f"{where} - only a LEDGER PAGE has chart states, and this row's world is {plate!r}"
    if to not in CHART_TO_KINDS:
        return f"{where} - `to` is not one of {'|'.join(CHART_TO_KINDS)} (the verbs the compiler knows)"
    states, here = states_of(plate), variant_of(page_of(plate))
    if to in CHART_TO_TO_STATE:
        k = sp.get("state")
        if isinstance(k, bool) or not isinstance(k, int) or k < 1:
            return (f"{where} - a {to} travels to one of the page's OTHER chart states and names it `state: <n>` "
                    f"(n >= 1); this move names {k!r}")
        if k > len(states):
            head = str(plate).split(";", 1)[0]
            return (f"{where} - the page declares {len(states)} `;then=` state(s) and the move asks for state {k}: "
                    f"it would redraw NOTHING. Declare the chain on the plate id ({head};then=<series>:<variant>) "
                    "or drop the move - a transform that renders nothing is refused (E99 s70 Apply 3)")
        there = variant_of(states[k - 1])
        if to == "morph" and not (here in LINE_VARIANTS and there in LINE_VARIANTS):
            return (f"{where} - a morph hands ONE LINE's area to another's; this page is {here!r} and state {k} is "
                    f"{there!r} (CAPABILITIES.md:118 - the compiler refuses any other pair and points at the recast)")
        if to == "remake" and not ({here, there} & set(LINE_VARIANTS) and {here, there} & set(BARS_VARIANTS)):
            return (f"{where} - a remake is admitted on a line <-> bars pair ONLY; this page is {here!r} and state "
                    f"{k} is {there!r} (CAPABILITIES.md:119)")
        return None
    if "state" in sp:
        return f"{where} - `state` is not named on a {to}: the compiler derives it, or the verb has none"
    if to == "rescale" and not any(sp.get(k) is not None for k in ("ymin", "ymax", "window")):
        return f"{where} - a rescale names the target domain: ymin and/or ymax, and/or window [from_x, to_x]"
    if to == "extend" and len([k for k in ("to_index", "series") if sp.get(k) is not None]) != 1:
        return f"{where} - an extend names exactly one of to_index (the datum the window grows to) or series"
    if to == "compare" and not (sp.get("metric") or sp.get("comparator") or sp.get("form")):
        return (f"{where} - a compare names the quoted METRIC and the COMPARATOR it becomes (E76); a bare compare "
                "melts nothing")
    return None


def docks_of(record) -> list[str]:
    """`{dock}` / `{dock_b}`: the dock ids the plan's own `capabilities` name, in the order named."""
    text = " ".join(str(c) for c in (record or {}).get("capabilities") or [])
    out: list[str] = []
    for m in DOCK_ID.finditer(text):
        if m.group(1) not in out:
            out.append(m.group(1))
    return out


def data_of(record) -> list[int]:
    """`{datum}` / `{datum_b}`: the datum indices the `capabilities` name, then the page's own
    emphasize index (the author's mark on the plate) - never a number this module made up."""
    text = " ".join(str(c) for c in (record or {}).get("capabilities") or [])
    out: list[int] = []
    for m in DATUM_ID.finditer(text):
        if int(m.group(1)) not in out:
            out.append(int(m.group(1)))
    for part in page_of((record or {}).get("plate", "")).split(":"):
        if part.isdigit() and int(part) not in out:
            out.append(int(part))
    return out


def points(record) -> bool:
    """Does this sentence POINT? E99 s67 Apply 1: a light is punctuation, not filler - it is
    emitted only where the plan's own capabilities name a datum, an index, a point or a region."""
    text = " ".join(str(c) for c in (record or {}).get("capabilities") or []).lower()
    return any(tok in text for tok in POINTS_AT)


def names_a_number(record) -> bool:
    """Does this sentence land a NUMBER? A digit, a number word, or an act that turns on one."""
    text = str((record or {}).get("sentence") or "")
    if re.search(r"\d", text) or any(w in text.lower() for w in NUMBER_WORDS):
        return True
    return bool({"TURNS", "COUNTS", "RANKS"} & acts_of(record))


# --------------------------------------------------------------------------- the beat's named moves

_COMPILER = None


def compiler():
    """The compiler module, imported LAZILY and once - the kit's habit (`table.apply_sidecar`).

    Two vocabularies live there and are never re-typed here: `SPECIES_KINDS` (what a row's species
    list may carry) and `DOCK_OPTS` (what a card's option dict may carry). A move checked against
    them is a move the compiler will accept.
    """
    global _COMPILER
    if _COMPILER is None:
        import build_scene_timeline_f as C
        _COMPILER = C
    return _COMPILER


def move_kinds() -> tuple:
    """Every `kind` a move may name: the compiler's species kinds, and `dock` for a card."""
    return tuple(compiler().SPECIES_KINDS) + (MOVE_DOCK,)


def dock_option_keys() -> tuple:
    """Every option a `dock` move may carry: the compiler's own `DOCK_OPTS`, plus the lane."""
    return tuple(compiler().DOCK_OPTS) + (MOVE_SLOT,)


# --------------------------------------------------------------------------- the card's room on a page

_PAGER = None


def pager():
    """`ledger_page`, imported LAZILY and once - the module that BUILDS a page and reports where its
    ink lands (`page_boxes`). The placer below reads a page's geometry through that one path, which
    is the same path the compiler's own placer and `probe.py` read it through (P50 T16: one
    placement truth, measured when the fixture holds the player's numbers for this ink)."""
    global _PAGER
    if _PAGER is None:
        import ledger_page as LPG
        _PAGER = LPG
    return _PAGER


def _meets(a: dict, b: dict, pad: float = 0.0) -> bool:
    """Do these two rectangles meet, with `b` grown by `pad` on every side? (the compiler's own test)"""
    return (a["x"] < b["x"] + b["w"] + pad and a["x"] + a["w"] > b["x"] - pad
            and a["y"] < b["y"] + b["h"] + pad and a["y"] + a["h"] > b["y"] - pad)


# --- THE PARK'S OWN ROOM (E99 s70 / the parent's read of the approved cut, 2026-09-17) ----------
PARK_LEAD_S = 0.4        # the park starts before the card lands (`build_short.py:361`: `t_pledge - 0.4`)
PARK_DUR_S = 0.9         # the affine transform's own clock (`:314`, `:361`, `:394` - all 0.9)
UNPARK_LAG_S = 0.3       # ... and the page re-takes the stage after the cards leave (`:394`: `+ 0.3`)


def park_scale_at(species: list, t: float) -> float:
    """The scale the page's chart is PARKED to at `t` - 1.0 while it stands full size. The last
    `chart_to park` at or before `t` decides, and a park to 1.0 is the UN-PARK (CAPABILITIES.md:120)."""
    scale = UNPARK_SCALE
    for sp in sorted((s for s in (species or []) if s.get("kind") == "chart_to" and s.get("to") == "park"),
                     key=lambda s: float(s["at"])):
        if float(sp["at"]) <= t + EPS:
            scale = float(sp.get("scale", UNPARK_SCALE))
    return scale


def _shrink(box: dict, ox: float, oy: float, s: float) -> dict:
    """One box under an affine park of `s` about `(ox, oy)` - every mark in place, nothing re-laid out."""
    return {**box, "x": ox + (box["x"] - ox) * s, "y": oy + (box["y"] - oy) * s,
            "w": box["w"] * s, "h": box["h"] * s}


def parked_boxes(boxes: dict, scale: float) -> dict:
    """The page's boxes as a `chart_to park` DRAWS them, not as they are laid out.

    Measured on the approved cut rather than modelled here: *"the chart svg is 800x851 at (80,374),
    parked at 0.55 it holds x 80-520, y 374-842"* (the approved portrait cut's own table, at the line the
    skeleton `page-parks-to-make-room-for-the-card` cites as its `source`) - the same
    corner, the width and the height times the scale, the axis labels riding with it - and the card the
    park makes room for lands *"626x370 at (0.5, 0.55) = y 871-1241, above the source line (1249)"*
    (`:340-345`), so the title, the sub and the SOURCE LINE stay where they are. The measured
    `data_mask` is dropped: the data's own holes park with the plot and are no longer where it says.
    """
    plot = boxes.get("plot")
    if not plot or scale >= UNPARK_SCALE - EPS:
        return boxes
    ox, oy = float(plot["x"]), float(plot["y"])
    out = {k: v for k, v in boxes.items() if k != "data_mask"}
    out["plot"] = _shrink(plot, ox, oy, scale)
    axis = boxes.get("axis") or {}
    if axis:
        out["axis"] = {k: (_shrink(b, ox, oy, scale) if isinstance(b, dict) else b) for k, b in axis.items()}
    return out


def _boxes(page: dict, aspect: str, park: float = UNPARK_SCALE) -> dict:
    """One page's boxes, through the page builder's own report, as the park at this instant draws them."""
    return parked_boxes(pager().page_boxes(page, aspect), float(park))


def page_ink(page: dict, aspect: str, park: float = UNPARK_SCALE) -> list[dict]:
    """Every rectangle of a page a card may NOT settle on: its type (the title, the sub, the source
    line, the badge rail), its axis labels, and the DATA's own cells - the boxes M25 scores
    (`gate_motion_density` LAYOUT_INK + `page.data`), read from the page builder's own report."""
    boxes = _boxes(page, aspect, park)
    out = [boxes[k] for k in ("title", "sub", "source", "rail") if boxes.get(k) and boxes[k]["h"] > 0]
    out += [b for b in ((boxes.get("axis") or {}).get("x"), (boxes.get("axis") or {}).get("y")) if b]
    return out


def clear_strips(band: dict, ink: list[dict]) -> list[dict]:
    """The strips of one free band that NO line of the page's ink crosses.

    `free_bands` hands a card the title and the sub ("a card parks over the title", E45 s1) - and
    M25 scores a card on either of them as a fault, which is how the third pass' cards read over the
    page's sub. So the band is cut at every piece of ink that reaches into it, and what is left is
    room a card can settle in without covering a word."""
    cuts = sorted((max(band["y"], b["y"]), min(band["y"] + band["h"], b["y"] + b["h"]))
                  for b in ink if _meets(band, b))
    out, top = [], band["y"]
    for lo, hi in cuts + [(band["y"] + band["h"], band["y"] + band["h"])]:
        if lo - top > 0:
            out.append({"x": band["x"], "y": top, "w": band["w"], "h": lo - top})
        top = max(top, hi)
    return out


# --- THE MARKS THE ROW ITSELF WRITES (P66 T3e, the v5 critic's row 3) ---------------------------
# E65's room is the page AS IT STANDS, and what stands on a page is not only its ink: a callout
# rings a datum and writes its label beside it, a bracket spans two, a figure writes a number at its
# spot, a spread bleeds the region between two series. None of those are in the page builder's own
# report (`page_boxes` measures the PAGE, not the row), so the plot's empty rooms read as free while
# the beat's whole argument is being drawn in them. Measured on base v5 at 79.50 s: the tea-cup card
# parked INSIDE the Fed page's plot and covered the right half of the callout's own label
# *"3.97% - the February low"* - the one thing that beat exists to say (M25 FAIL, the same instant).
# So a card whose window overlaps a mark of the row's own takes no room inside the plot: the bands
# outside it, or the park that makes one, are what is left - the same ladder `make_room` already
# walks, and the same argument `bound_by_state` makes for a `chart_to` redrawing under a card.
PLOT_MARKS = ("callout", "bracket", "figure", "spread", "relight", "peel", "undraw", "span", "ring")
# ... and the QUIET ZONE is written in too: a `note` is *"a line of handwriting in the page's quiet
# zone"* (`build_scene_timeline_f.SPECIES_WHEN`), which is the band a card sent out of the plot is
# otherwise given. The first fifth-pass build measured exactly that: the cup, out of the plot, landed
# on all three of the Fed page's notes (84 %, 45 % and 100 % of them). So while a note of the row's
# own is up, the quiet-zone side is the handwriting's and the card takes another band.
QUIET_MARKS = ("note",)


def _span_of(sp: dict, t_out: float) -> tuple[float, float]:
    """One species' (start, end) as the room finder reads it. A mark with no readable end stands to
    the card's own exit: what the approved cuts write on a page STAYS written."""
    at, until, dur = float(sp.get("at", 0.0)), sp.get("until"), sp.get("dur")
    if isinstance(until, (int, float)) and not isinstance(until, bool):
        return at, float(until)
    if isinstance(dur, (int, float)) and not isinstance(dur, bool):
        return at, at + float(dur)
    return at, float(t_out)


def quiet_live(species: list, t_in: float, t_out: float) -> list[str]:
    """The row's own handwriting in the page's QUIET ZONE while a card is on screen (`QUIET_MARKS`)."""
    return [f"{sp.get('kind')} at {_span_of(sp, t_out)[0]:.2f}s" for sp in species or []
            if str(sp.get("kind")) in QUIET_MARKS
            and _span_of(sp, t_out)[1] > t_in + EPS and _span_of(sp, t_out)[0] < t_out - EPS]


def marks_live(species: list, t_in: float, t_out: float) -> list[str]:
    """The row's own marks standing over the plot while a card is on screen, named for the `why`.

    A mark with no readable end stands to the card's own exit: what the approved cuts write on a
    page's chart STAYS written (a callout's label, a bracket, a figure, a spread's fill)."""
    out: list[str] = []
    for sp in species or []:
        if str(sp.get("kind")) not in PLOT_MARKS:
            continue
        at, until, dur = float(sp.get("at", 0.0)), sp.get("until"), sp.get("dur")
        if isinstance(until, (int, float)) and not isinstance(until, bool):
            end = float(until)
        elif isinstance(dur, (int, float)) and not isinstance(dur, bool):
            end = at + float(dur)
        else:
            end = float(t_out)
        if end > t_in + EPS and at < t_out - EPS:
            out.append(f"{sp.get('kind')} at {at:.2f}s")
    return out


def rooms_of(page: dict, aspect: str, park: float = UNPARK_SCALE, marked: bool = False,
             quiet_taken: bool = False) -> list[dict]:
    """Every rectangle on this page a card may settle in, largest first: the plot's own empty rooms
    (E65's `mask_rooms`, read off the page's measured mask) and the strips of the bands outside the
    plot that carry no ink (`clear_strips`). One list, one order, no episode named.

    Under a PARK the mask's rooms are gone (the data's holes shrank with the plot) and the room is the
    band the park freed - which is what the approved cut puts its cards in (`build_short.py:340-345`).

    `marked` says the row is writing MARKS of its own inside the plot while the card is up
    (`marks_live`): the plot's holes are not room then, and only the bands outside it are offered.
    `quiet_taken` says the row is writing in the page's QUIET ZONE (`quiet_live`): that side's band is
    the handwriting's, and no card is offered it."""
    C = compiler()
    boxes = _boxes(page, aspect, park)
    if not boxes.get("plot"):
        return []
    ink = page_ink(page, aspect, park)
    out = [] if marked else list(C.mask_rooms(boxes))
    quiet = str(boxes.get("quiet_zone") or "") if quiet_taken else ""
    for band in C.free_bands(boxes):
        if quiet and str(band.get("band") or "") == quiet:
            continue
        out += clear_strips(band, ink)
    return sorted(out, key=lambda r: -(r["w"] * r["h"]))


def card_rooms(page: dict, aspect: str, n: int, park: float = UNPARK_SCALE, marked: bool = False,
               quiet_taken: bool = False) -> list[dict]:
    """`n` boxes a card can settle in on this page, none of them sharing a pixel with another or
    with the page's ink - E65's own rooms, largest first, at the quiet-zone end.

    E65: the card takes a room of the page's own. (E65 also said *"parking is not a way to make room
    for a card on 9:16"* - R26-172, WITHDRAWN 2026-09-17 on the approved cut's own 56.72 s frame: the
    page parks and the cards take the room below. `park` is the second answer, not the first: a page
    with a room of its own still uses it.) The rooms are the rectangles the DATA's ink does not touch
    (`build_scene_timeline_f.mask_rooms`, read off the page's measured mask), and the card takes the
    end of its room the plate's own `quiet_zone` token names (`right` / `left`). Fewer than `n` boxes
    come back when the page has not got the room - the caller leaves those cards to the compiler's
    placer and says so. `marked` drops the plot's own holes: while the row writes marks inside the
    plot the room is a band outside it (`rooms_of`). Pure: the page spec is never mutated."""
    C = compiler()
    boxes = _boxes(page, aspect, park)
    if not boxes.get("plot"):
        return []
    stage, pad = boxes["stage"], C.DOCK_PLACE_PAD
    want = round(C.DOCK_ON_PAGE_W * stage["w"])
    floor = C.PLACE_FLOOR_H.get(aspect, C.PLACE_FLOOR_H["16:9"])
    quiet, ink = boxes.get("quiet_zone"), page_ink(page, aspect, park)
    out: list[dict] = []
    for room in rooms_of(page, aspect, park, marked, quiet_taken):
        if len(out) >= n:
            break
        room_h = room["h"] - 2 * pad
        w = min(float(want), room["w"] - 2 * pad)
        if w * CARD_ROOM_ASPECT > room_h:
            w = room_h / CARD_ROOM_ASPECT                # the card gives its SCALE before its place (E65) - so the
        h = min(float(C.dock_card_h(int(w))), room_h)    # room holds it even if the asset is a square one, and a
                                                         # room that cannot hold THAT is refused below, not filled
                                                         # with a wide flat card the asset may be twice the height of
        if w < C.DOCK_ON_PAGE_MIN_W or h < floor:        # under the floor a card has stopped being evidence
            continue
        x = room["x"] + pad if quiet == "left" else room["x"] + room["w"] - pad - w
        # the card sits at the HEAD of its room: the box is the compiler's own 16:9 estimate, and a taller
        # asset (the kit cannot read one - it is registered by the episode at build time) grows DOWN into the
        # room's own empty space rather than out of it
        box = {"x": round(x), "y": round(room["y"] + pad), "w": round(w), "h": round(h)}
        if any(_meets(box, other) for other in ink + out):
            continue
        out.append(box)
    return out


def room_options(box: dict, aspect: str) -> dict:
    """One room as the dock options that PLACE a card in it: the compiler's own centred placement,
    authored. No `read` is written with it, and that is the point - *"a centred card with no `read`
    has no pop at all"* (`build_scene_timeline_f`:5304), so the card lands in the page's room and
    never flashes at the solo card's 800 px over the page's ink first (E63, M25)."""
    sw, sh = pager().STAGE_PX[aspect]
    return {"centre": True,
            "centre_w": round(box["w"] / sw, 4),
            "centre_x": round((box["x"] + box["w"] / 2) / sw, 4),
            "centre_y": round((box["y"] + box["h"] / 2) / sh, 4)}


def placed(options) -> bool:
    """Does this dock's options carry the AUTHOR's own placement? Then it is kept verbatim."""
    return any(k in (options or {}) for k in CARD_PLACE_KEYS)


def _slots(free: list) -> list[int]:
    """The room INDEX each card takes: the first one no card live at the same instant already holds,
    so two cards over one page never share a rectangle."""
    slots: list[int] = []
    for i, d in enumerate(free):
        taken = {slots[j] for j, o in enumerate(free[:i]) if float(o[3]) > float(d[2]) and float(o[2]) < float(d[3])}
        slots.append(next(k for k in range(len(free)) if k not in taken))
    return slots


def make_room(card: list, species: list, t1: float, d: dict, notes: list) -> float:
    """THE PARK THAT MAKES THE ROOM - emitted onto the row, and the scale it parks the page to.

    The approved cut's own answer to a card with nowhere to go: *"the monthly bars PARK up-left on
    'pledged' and the fab card takes the band the park frees"* (the park 0.4 s before the card, at
    `scale` / `anchor: top`), and when the cards leave the page UN-PARKS - *"the chart UN-PARKS - grows
    back to full size from the parked slot"* (a park to 1.0, 0.3 s after the card's exit). Both are
    transcribed from the approved cut's own rows, which the skeletons
    `page-parks-to-make-room-for-the-card` and `page-unparks-and-retakes-the-stage` cite as their
    `source`; never invented here. R26-172, which used to strip them in portrait, is WITHDRAWN."""
    scale, anchor = float(d.get("park_scale", 0.52)), str(d.get("park_anchor", "top"))
    at = round(max(float(card[2]) - PARK_LEAD_S, 0.0), 2)
    species.append({"kind": "chart_to", "at": at, "dur": PARK_DUR_S, "to": "park", "scale": scale, "anchor": anchor})
    notes.append(f"the page PARKS to {scale} at {at:.2f}s to make the room `{card[0]}` lands in: the page had no room "
                 "of its own clear of its ink, and a card is never dropped over a page's ink (the approved cut's own "
                 "move, transcribed in `page-parks-to-make-room-for-the-card`; R26-172 WITHDRAWN)")
    out = round(float(card[3]) + UNPARK_LAG_S, 2)
    if out < t1 - EPS:
        species.append({"kind": "chart_to", "at": out, "dur": PARK_DUR_S, "to": "park",
                        "scale": UNPARK_SCALE, "anchor": anchor})
        notes.append(f"the page UN-PARKS at {out:.2f}s, as the card leaves: the chart re-takes the stage rather than "
                     "standing small under nothing (`build_short.py:394`; CAPABILITIES.md:120)")
    return scale


def place_cards(docks: list, page: dict | None, aspect: str, notes: list,
                species: list | None = None, t1: float | None = None, defaults: dict | None = None) -> list:
    """Every card on one page row, placed in the page's own room - and never two of them in one box.

    A card the plan placed itself (`centre_x` / `centre_y` / `centre_w`) is untouched. Every other card
    on a LEDGER page takes a room of its own: the rooms are ordered by size, and a card is given the
    first room no card LIVE AT THE SAME INSTANT already holds.

    The rooms are read AS THE PAGE STANDS AT THAT INSTANT - under a `chart_to park` the room is the band
    the park freed (`parked_boxes`). When a card lands on a page that stands full size and has no room
    for it, the page PARKS to make one (`make_room`) instead of the card sitting on the page's ink or
    losing its box to the stage's centre - the approved cut's own move at 56.7 s.

    The page as it stands includes THE MARKS THIS ROW WRITES (`marks_live`): while a callout, a
    bracket, a figure or a spread of the card's own row is up, the plot's holes are not room and the
    card takes a band outside the plot - or the page parks (P66 T3e; base v5 at 79.50 s)."""
    if page is None or not docks:
        return docks
    free = [d for d in docks if not placed(d[4])]
    if not free:
        return docks
    d = {**DEFAULTS, **(defaults or {})}
    slots = _slots(free)
    parks = {i: park_scale_at(species or [], float(card[2])) for i, card in enumerate(free)}
    # ... and the row's OWN marks decide whether the plot's holes are room at all (P66 T3e)
    marks = {i: marks_live(species or [], float(card[2]), float(card[3])) for i, card in enumerate(free)}
    quiet = {i: quiet_live(species or [], float(card[2]), float(card[3])) for i, card in enumerate(free)}
    keys = {i: (parks[i], bool(marks[i]), bool(quiet[i])) for i in range(len(free))}
    rooms: dict[tuple, list[dict]] = {}
    for key in sorted(set(keys.values())):
        n = max([k for i, k in enumerate(slots) if keys[i] == key] or [0]) + 1
        rooms[key] = card_rooms(page, aspect, n, park=key[0], marked=key[1], quiet_taken=key[2])
    for i, (card, k) in enumerate(zip(free, slots)):
        scale, marked, quiet_taken = keys[i]
        no_room = k >= len(rooms[keys[i]])
        if no_room and species is not None and t1 is not None and scale >= UNPARK_SCALE - EPS:
            scale = make_room(card, species, float(t1), d, notes)
            parks[i] = scale
            keys[i] = (scale, marked, quiet_taken)
            rooms.setdefault(keys[i], card_rooms(page, aspect, max(slots) + 1, park=scale, marked=marked,
                                                 quiet_taken=quiet_taken))
        if quiet[i]:
            notes.append(f"{card[0]} takes no room in the page's quiet zone: this row writes there while the card is "
                         f"up ({', '.join(quiet[i])}) - a note is a line of handwriting in the quiet zone "
                         "(`build_scene_timeline_f.SPECIES_WHEN`), and the fifth pass' first build landed the card on "
                         "all three of them")
        if marks[i]:
            notes.append(f"{card[0]} takes no room inside the plot: this row writes its own marks over it while the "
                         f"card is up ({', '.join(marks[i])}) - a callout's label, a bracket, a figure or a spread "
                         "is not in the page's measured ink, and E65's room is the page AS IT STANDS (base v5 at "
                         "79.50s: the card covered the callout's own label)")
        if k < len(rooms[keys[i]]):
            room = rooms[keys[i]][k]
            popped = [key for key in ("read", "read_s", "park_s") if key in card[4]]
            card[4] = {**{key: v for key, v in card[4].items() if key not in popped},
                       **room_options(room, aspect)}
            if popped:
                notes.append(f"{card[0]} drops its {', '.join(popped)}: a card given a room of the page's own lands "
                             "IN it - the read-then-park pop would put it at the stage's centre over the page's ink "
                             "first, which is what M25 and E63 score (`room_options`: a centred card with no `read` "
                             "has no pop at all)")
            notes.append(f"{card[0]} takes the page's own room "
                         f"{'x'.join(str(room[v]) for v in ('w', 'h'))} at "
                         f"({room['x']}, {room['y']})"
                         + (f", the band the park to {scale} frees" if scale < UNPARK_SCALE - EPS else "")
                         + " (E65)")
        elif card[4].get("centre"):
            card[4] = {key: v for key, v in card[4].items() if key != "centre"}
            notes.append(f"{card[0]} loses its bare `centre`: the page has no {k + 1}th room clear of its ink, not "
                         "even parked, and a centred card with no box of its own reads at the stage's centre, over "
                         "the page (E65)")
        else:
            notes.append(f"{card[0]} keeps the compiler's own placer: the page has no {k + 1}th room clear of its "
                         "ink for a card, not even parked (E65's ladder decides it at compile time)")
    return docks


# --- E67: THE CHART'S INKS ARE ELECTRIC; THE CHART IS THE THUMBNAIL -----------------------------
# (CAPABILITIES.md:34; OPERATOR-RULINGS.md:2176, the operator 2026-09-12: *"we need to use bolder
# primary, high-contrast line colors for our default the chart instead of gray. that way our charts
# can become our thumbnails ... the Teal and a Claude orange would work."*)
#
# WHERE A PAGE'S INKS ARE DECIDED - measured before this was written, not recalled. NOT here, and not
# on the shot row. A page's ink is a TOKEN named in the EPISODE's own series file
# (`evidence/objects/<object>.series.json`: `series[].color`, `bars[].color`, `colors[]`), carried
# onto the page spec verbatim by `build_scene_timeline_f.ledger_world`, and resolved to a hex by the
# PLAYER's one table (`scene-evidence-engine.mjs` LP_INK: crimson `#FF8A4C` - the Claude orange sits
# in the crimson slot so every object file stays valid - teal `#34F5C5`, cobalt `#4FC3FF`, amber
# `#F5B72E`). A series that declares NO colour takes the electric cycle by index (LP_CYCLE, E67
# Apply 3) or, alone, its own sign colour - and never grey. There is no `ink=` plate option: the
# compiler cannot choose a page's ink from the table, and rewriting a bed's series file to fix a base
# is not a compiler's business (E99 s11 - an approved cut's own files are never moved under it).
#
# So the base emits E67's inks BY DEFAULT wherever the plan's series names none (the engine's cycle
# IS the default), and where a series names its own the row's `why` says which - and WARNS when that
# set predates E67: a raw hex or an unknown token the electric table cannot resolve, or a page whose
# every series is `deemph` (E67 Apply 3: grey is never a default, it is an author's de-emphasis).
E67_CYCLE = ("teal", "crimson", "cobalt", "amber")   # LP_CYCLE's own order - what an undeclared series takes
E67_DEEMPH = "deemph"
E67_SIGN = ("var(--lp-neg)", "var(--lp-pos)")       # the SIGN colours on the field (E67, CAPABILITIES.md:34:
# `#3DDC84` up / `#FF4D4D` down, E28 standing) - authored exactly this way, resolved by the engine's own `lpVarHex`
# beside LP_INK (`PS_PAL = { ...LP_INK, neg: "var(--lp-neg)", pos: "var(--lp-pos)" }`), and what a LONE series takes
# when it declares nothing. They are E67's, not the old palette, so they are never WARNed as predating it.
E67_TOKENS = E67_CYCLE + (E67_DEEMPH,) + E67_SIGN
E67_CITE = "E67, CAPABILITIES.md:34 (the chart is the thumbnail)"
INK_LISTS = ("series", "bars", "shares")             # the page-spec lists whose items may name a colour


def page_inks(page: dict) -> list[str]:
    """Every ink TOKEN a `ledger_page.v1` spec declares, in the order the page reads them."""
    out = [str(c) for c in (page.get("colors") or []) if c]
    for name in INK_LISTS:
        for item in page.get(name) or []:
            if isinstance(item, dict) and item.get("color"):
                out.append(str(item["color"]))
    return out


def ink_note(page: dict | None) -> str | None:
    """What this page's INKS are, for the row's `why` - and a WARN when they predate E67."""
    if not page:
        return None
    declared = page_inks(page)
    if not declared:
        return ("this page's series declare no ink, so it takes E67's ELECTRIC cycle by index "
                f"({', '.join(E67_CYCLE)} - crimson is the Claude orange #FF8A4C) or, alone, its own "
                f"sign colour; grey is never a default ({E67_CITE})")
    old = sorted({c for c in declared if c not in E67_TOKENS})
    if old:
        return (f"WARN this page's series predates E67 - its inks are the old palette ({', '.join(old)}): "
                f"E67's field set is {', '.join(E67_CYCLE)}, measured against the charcoal #25313C, and a "
                "token the player's LP_INK table cannot resolve is drawn as written. The series file is the "
                f"EPISODE's, not the compiler's, so it is named here and never rewritten ({E67_CITE}; E99 s11)")
    if all(c == E67_DEEMPH for c in declared):
        return (f"WARN every series on this page is `{E67_DEEMPH}` - grey is never a default, it is an "
                f"explicit de-emphasis an author writes (E67 Apply 3; {E67_CITE})")
    return (f"this page's series name their own E67 inks ({', '.join(declared)}) and the electric table "
            f"resolves them; the cycle a page that declares none would take opens on {E67_CYCLE[0]} ({E67_CITE})")


CHART_STATE_KINDS = ("chart_to",)   # the species that REDRAW a page's chart UNDER a card


def bound_by_state(docks: list, species: list, notes: list) -> list:
    """A card parks in the page's room AS THE PAGE STANDS - so it leaves when the chart is redrawn.

    E65 places a card in the rectangle the page's DATA does not touch. A `chart_to` (rescale, recast,
    park) draws a different chart in the same plot, and the room the card was given is then wherever
    the new line goes: the third pass measured exactly that - the panel card parked in the holdings
    page's empty room at 0:09 and read over the RESCALED line from 0:22 to 0:38, nine of M25's
    twenty-nine faults. The card keeps the row's end when the change comes before it could read and
    park (leaving would make it a flash), and the row's `why` names that risk instead."""
    C = compiler()
    states = sorted(float(s["at"]) for s in species if s.get("kind") in CHART_STATE_KINDS)
    # ... and while the page is PARKED the card's room is the band the park freed, OUTSIDE the plot:
    # the chart redraws inside its parked box and the room is untouched, so only the next park (or the
    # un-park) changes it. The approved cut holds its two cards straight through a recast and lands the
    # un-park as they leave (`page-unparks-and-retakes-the-stage`).
    parks = sorted(float(s["at"]) for s in species
                   if s.get("kind") == "chart_to" and s.get("to") == "park")
    for d in docks:
        t_in, t_out = float(d[2]), float(d[3])
        mine = parks if park_scale_at(species, t_in) < UNPARK_SCALE - EPS else states
        nxt = next((t for t in mine if t > t_in + EPS), None)
        if nxt is None or nxt >= t_out - EPS:
            continue
        opts = d[4] or {}
        need = float(opts.get("read_s") or C.DOCK_READ_S) + float(opts.get("park_s") or C.DOCK_PARK_S)
        if nxt - t_in < need:
            notes.append(f"{d[0]} holds past the chart's own state change at {nxt:.2f}s: it lands at {t_in:.2f}s and "
                         f"needs {need:.2f}s to read and park - the room it sits in is the page BEFORE that change")
            continue
        d[3] = round(nxt, 2)
        notes.append(f"{d[0]} leaves at the chart's state change ({nxt:.2f}s) and not at the row's end ({t_out:.2f}s): "
                     "its room is the page's empty room as the page STANDS, and a chart_to redraws the ink under it (E65)")
    return docks


def moves_of(record) -> list[dict]:
    """The moves a plan record names, in the order the author wrote them. An absent or empty list
    is a SILENT beat - it contributes nothing, and `compile` says so in `why`."""
    return [m for m in ((record or {}).get("moves") or [])]


def check_moves(record) -> None:
    """One record's moves, refused BY NAME - the kind, the phrase, the card's asset, the options.

    The phrase is checked against the beat's OWN sentence here (a plan is readable without a take);
    `compile` then resolves it on the take's words inside the beat's window, and refuses there when
    the take does not carry it where the sentence says.
    """
    n = record.get("beat", "?")
    kinds, opts = move_kinds(), dock_option_keys()
    for m in moves_of(record):
        if not isinstance(m, dict):
            raise Refused(f"beat {n}: a move is an object {{{', '.join(MOVE_KEYS)}}}, not {m!r}")
        kind = m.get("kind")
        if kind not in kinds:
            raise Refused(f"beat {n}: the move kind {kind!r} is not one the compiler carries - "
                          f"{MOVE_DOCK}, or one of {'|'.join(sorted(k for k in kinds if k != MOVE_DOCK))}")
        phrase = str(m.get("at_word") or "").strip()
        if not phrase:
            raise Refused(f"beat {n}: the {kind} move names no `at_word` - a move lands on a WORD of its own "
                          "sentence, never on a stopwatch (authoring/words.py)")
        if not _phrase_in(str(record.get("sentence") or ""), phrase):
            raise Refused(f"beat {n}: {phrase!r} is not a phrase of that beat's own sentence "
                          f"({str(record.get('sentence') or '')!r}) - a move belongs to the sentence it punctuates")
        for key in ("target", "options"):
            if m.get(key) is not None and not isinstance(m[key], dict):
                raise Refused(f"beat {n}: the {kind} move's `{key}` is an object, not {m[key]!r}")
        if m.get("dur") is not None and not isinstance(m["dur"], (int, float)) and m["dur"] != "hold":
            raise Refused(f"beat {n}: the {kind} move's `dur` is seconds or \"hold\", not {m['dur']!r}")
        if kind == MOVE_DOCK:
            if not str(m.get("asset") or "").strip():
                raise Refused(f"beat {n}: a {MOVE_DOCK} move names no `asset` - the card is the project's "
                              "registered evidence still, and the compiler never invents one")
            bad = [k for k in (m.get("options") or {}) if k not in opts]
            if bad:
                raise Refused(f"beat {n}: the {MOVE_DOCK} move's option(s) {', '.join(sorted(bad))} are not "
                              f"the compiler's ({'|'.join(opts)})")
        elif m.get("asset") is not None:
            raise Refused(f"beat {n}: the {kind} move names an `asset` - only a {MOVE_DOCK} move carries one")


def _phrase_in(sentence: str, phrase: str) -> bool:
    """Is `phrase` a run of words of `sentence`? The kit's own normaliser, so a phrase reads here
    exactly as `words.at` reads it (punctuation-insensitive, case-insensitive)."""
    toks = [W._norm(x) for x in str(phrase).split()]
    said = [W._norm(x) for x in str(sentence).split()]
    return bool(toks) and any(said[i:i + len(toks)] == toks for i in range(len(said) - len(toks) + 1))


def word_at(ws: list[dict], phrase: str, t0: float, t1: float) -> float | None:
    """The instant `phrase` OPENS inside `[t0, t1)` - the beat's own window, so a one-word anchor is
    unambiguous within the sentence it belongs to (`words.at` searches the whole take). None when
    the take does not carry the phrase there. The window is HALF-OPEN on purpose: a word that opens
    exactly on the next beat's start belongs to that beat, and no instant is claimed by two."""
    toks = [W._norm(x) for x in str(phrase).split()]
    if not toks or not ws:
        return None
    for i, w in enumerate(ws):
        if not (t0 - EPS <= float(w["start_s"]) < t1):
            continue
        if [W._norm(x["w"]) for x in ws[i:i + len(toks)]] == toks:
            return round(float(w["start_s"]), 2)
    return None


# --------------------------------------------------------------------------- the groups

def groups(plan: list[dict]) -> list[dict]:
    """The plan's beats as ROWS-to-be: consecutive beats that share a world are one row.

    The grouping is the AUTHOR's, read two ways and never invented: the record's own `row` when
    every record carries one, else a run of consecutive beats naming the same `plate`. A page never
    enters twice, so when the hook's world is a clip or a plate and the very next group is a page,
    the hook is ABSORBED into that page's row - the page mounts over the hook's world on its last
    word (E99 s67 Apply 6), which is the open the approved cuts play.
    """
    keyed = [r.get("row") for r in plan]
    use_row = all(k is not None for k in keyed)
    out: list[dict] = []
    for i, r in enumerate(plan):
        key = keyed[i] if use_row else plate_of(r.get("plate", ""))
        if out and out[-1]["key"] == key:
            out[-1]["beats"].append(r)
        else:
            out.append({"key": key, "beats": [r]})
    if len(out) > 1 and world_of(out[0]["beats"][0]["plate"]) != "page" \
            and world_of(out[1]["beats"][0]["plate"]) == "page":
        # the hook's world is NOT absorbed away: it is kept, and the page mounts OVER it (E99 s67
        # Apply 6, the approved open - `build_short.py:281-285`). A mount with no world under it is
        # bare cream where the hook should be, which is what base v3 played at 0.20 s.
        out[1]["under_beats"] = list(out[0]["beats"])
        out[1]["beats"] = out[0]["beats"] + out[1]["beats"]
        out[1]["open_mounts"] = True
        out = out[1:]
    for g in out:
        g["t0"] = float(g["beats"][0]["t0"])
        g["t1"] = float(g["beats"][-1]["t1"])
        g["plate"] = g["beats"][-1]["plate"] if g.get("open_mounts") else g["beats"][0]["plate"]
        g["world"] = world_of(g["plate"])
        seen: list[str] = []
        for b in g["beats"]:
            seen += [x for x in docks_of(b) if x not in seen]
        g["docks"] = seen
        g["act"] = next((b.get("act") for b in g["beats"] if acts_of(b)), g["beats"][0].get("act", ""))
    return out


def first_light_move(g: dict, ws) -> float | None:
    """The instant the group's first LIGHT move lands, on the take's own words - or None when the
    plan names none. The CLOCK reads the plan's moves too: a page whose first light is already
    spoken while an axes build would still be drawing cannot enter on its axes (see `_entry`)."""
    out = [t for b in g["beats"] for m in moves_of(b) if m.get("kind") in LIGHT_KINDS
           for t in [word_at(ws, str(m.get("at_word") or ""), float(b["t0"]), float(b["t1"]))] if t is not None]
    return min(out) if out else None


def _is_return(g: dict) -> bool:
    text = " ".join(str(b.get("act", "")) + " " + " ".join(str(c) for c in b.get("capabilities") or [])
                    for b in g["beats"]).lower()
    return any(tok in text for tok in RETURN_TOKENS)


def shape_of(g: dict, index: int, nxt: dict | None, seen: tuple = ()) -> tuple[str, str]:
    """The beat shape this group plays, and the rule that says so - the POSITIONAL rule above, which
    is what carries a beat whose sentence plays none of the twelve acts. `seen` is the pages already
    on screen: a page the cut has never shown cannot RETURN (a spiral unwinds a page from its own
    point), so a beat that talks like a return over a new page is an ordinary page beat."""
    if index == 0:
        return SHAPE_OPEN, ("the page mounts the hook's world on its last word - the open IS the chart (E99 s67 Apply 6)"
                            if g.get("open_mounts") else "the page on the hook, on its axes (E99 s67 Apply 6)")
    if _is_return(g) and g["world"] == "page" and page_of(g["plate"]) in seen:
        return SHAPE_RETURN, "the spiral because the beat returns (the plan names the return, and the page has been here)"
    if g["world"] != "page":
        return SHAPE_PLATE, "a narrative plate: the world is not a page, so the plate carries the card"
    if nxt is not None and nxt["world"] == "page":
        return SHAPE_TRANSFORM, "page to page: the next world is a page too, so this page transforms into it"
    if g["docks"]:
        return SHAPE_HELD, "the page holds while its evidence arrives over it (the plan names a dock)"
    return SHAPE_PAGE, "a page beat: the page enters and its number lands on it"


# --------------------------------------------------------------------------- the chooser

def main_row(skeleton: dict) -> dict:
    """The skeleton's OWN row - the world the beat is about.

    A skeleton whose page mounts over the hook's world declares that world FIRST, because the approved
    open is TWO rows and that is the order the table writes them in
    (the approved open's own pair: the hook's clip from frame 0 to the mount word, then the page with
    `mount=<s>` over it - `open-page-mounts-the-world` cites the table's line as its `source`). So the
    beat's own row is the LAST, and every skeleton with one row is unchanged by this reading."""
    return skeleton["rows"][-1]


def under_rows(skeleton: dict) -> list[dict]:
    """The row(s) this skeleton's own row arrives OVER - the hook's world under the page that mounts.
    Empty for every skeleton whose shape is one world."""
    return list(skeleton["rows"][:-1])


def entry_of(skeleton: dict) -> str | None:
    """The entry a skeleton's own row declares: axes / mount / spiral / snap / built / camera,
    or None for a skeleton whose world is a plate."""
    m = ENTRY_SUFFIX.search(str(main_row(skeleton)["plate"]).split(";", 1)[0])
    return m.group(1).split("=", 1)[0] if m else None


def entry_token_in(plate: str) -> str | None:
    """The WHOLE entry token a resolved plate declares - `mount=2.0`, `camera=dock-x`, `axes` - where
    `entry_in` gives only its head. The author's own token is what `set_entry` writes back."""
    m = ENTRY_SUFFIX.search(str(plate).split(";", 1)[0])
    return m.group(1) if m else None


def entry_in(plate: str) -> str | None:
    """The entry a resolved ledger plate declares (`axes`, `mount`, `spiral`, `snap`, `camera`)."""
    m = ENTRY_SUFFIX.search(str(plate).split(";", 1)[0])
    return m.group(1).split("=", 1)[0] if m else None


def set_entry(plate: str, entry: str, mount_s: float) -> tuple[str, bool]:
    """The page's entry, written onto a resolved plate id - and whether it MOVED.

    The entry is the compiler's, never the skeleton's: the skeleton owns the choreography over the
    page (its docks, its lights, its exit), the approved shape owns how the page arrives (E99 s67
    Apply 3 and 6 - the mount when the number lands late, the axes otherwise, never `built`).
    """
    head, sep, tail = str(plate).partition(";")
    token = f"mount={round(mount_s, 2)}" if entry == "mount" else entry
    m = ENTRY_SUFFIX.search(head)
    if m and m.group(1) == token:
        return plate, False
    head = (head[:m.start()] + ":" + token + head[m.end():] if m else
            head[:-len(":cut")] + ":" + token + ":cut" if head.endswith(":cut") else head + ":" + token)
    return head + sep + tail, True


def _needs(skeleton: dict, hole: str) -> bool:
    return hole in json.dumps(skeleton["rows"])


# THE MECHANISM A SIGNATURE DEMANDS (E99 s70 Apply 2). The library now carries a skeleton for every
# word of the rebuilt vocabulary, and a skeleton that plays a mechanism the beat's PLAN does not name
# would be an invention - so a demanding skeleton is a candidate only where the plan names its move,
# and where it does it is PREFERRED (rung 0). The plan is the intelligence (E99 s66); the library
# only offers the shape.
SIGNATURE_ENTRY = {"snap": "snap", "throw-then-zoom": "snap", "throw-then-push": "camera",
                   "object-becomes-chart": "morph"}
SIGNATURE_CHART_TO = {"recast": "recast", "rescale": "rescale", "morph": "morph", "remake": "remake",
                      "melt": "compare", "park": "park", "unpark": "park"}
SIGNATURE_EXIT = {"door": "door"}


def _chart_to_moves(g: dict) -> list[dict]:
    """Every `chart_to` the beats of one group NAME, as the plan wrote them."""
    out: list[dict] = []
    for b in g.get("beats") or []:
        for mv in moves_of(b):
            if str(mv.get("kind")) == "chart_to":
                out.append({**(mv.get("options") or {}), "kind": "chart_to"})
    return out


def signature_named(g: dict, skeleton: dict) -> bool | None:
    """Does the GROUP's own plan name the mechanism this skeleton's signature IS?

    `True` the plan names it, `False` the plan does not (the skeleton is not offered), `None` the
    signature demands nothing of the plan (every arrival and every transition word: axes, mount,
    spiral, suck, cut, dip, card, hold - the shape alone decides those).
    """
    sig = str(skeleton["signature"])
    if sig in SIGNATURE_ENTRY:
        head = str(entry_token_in(g.get("plate", ""))).split("=", 1)[0]
        if head != SIGNATURE_ENTRY[sig]:
            return False
        if sig == "throw-then-zoom":
            return any(str(mv.get("kind")) == MOVE_DOCK and (mv.get("options") or {}).get("arrive") == "throw"
                       for b in g.get("beats") or [] for mv in moves_of(b)) or bool(g.get("thrown_before"))
        if sig == "throw-then-push":
            return True
        return True
    if sig in SIGNATURE_CHART_TO:
        want = SIGNATURE_CHART_TO[sig]
        for sp in _chart_to_moves(g):
            if str(sp.get("to")) != want:
                continue
            if sig == "unpark" and float(sp.get("scale", 0.72) or 0.72) != UNPARK_SCALE:
                continue
            if sig == "park" and float(sp.get("scale", 0.72) or 0.72) == UNPARK_SCALE:
                continue
            return True
        return False
    if sig in SIGNATURE_EXIT:
        # THE EVIDENCE DOOR opens a card that landed FLAT (E98 s7): the page before this one has to
        # have arrived by a snap or the camera, and this world has to be the thing behind it.
        return bool(g.get("prev_entry") in ("snap", "camera") and g.get("world") != "page")
    return None


def _needs_states(skeleton: dict) -> int:
    """The highest `chart_to` state index this skeleton's own rows travel to (0 = none)."""
    out = 0
    for row in skeleton["rows"]:
        for sp in row.get("species") or []:
            if str(sp.get("kind")) == "chart_to":
                k = (sp.get("options") or {}).get("state")
                if isinstance(k, int) and not isinstance(k, bool):
                    out = max(out, k)
    return out


def usable_library(lib: list[dict], aspect: str) -> list[dict]:
    """The skeletons this ASPECT may be offered - every one of them, in both aspects.

    R26-172 kept the park and the un-park out of portrait until the parent read the approved cut's own
    56.72 s frame: the page parks small at the top and the cards take the room below. The ruling is
    WITHDRAWN and the two skeletons are offered in portrait exactly as they are in landscape."""
    return list(lib)


def choose(beat, history: list, library: list[dict]) -> tuple[dict, str]:
    """The skeleton this beat gets, and the rung of the fallback that chose it.

    `beat` is a mapping carrying `shape` and `act` (a plan record, or one of `groups`' groups, which
    also carry `entry` and `docks`). `history` is the skeleton ids already emitted, in order.

    Candidates are the skeletons whose `shape` matches and whose `acts` include the beat's act - by
    SHAPE ALONE when the sentence plays none of the twelve. THE VARIETY RULE: the previous beat's
    skeleton id is refused (ids, not signature words - P66 T2). The fallback order, in full:

      1. the shape's skeletons whose acts carry this beat's act, whose entry the CLOCK allows and
         whose docks the plan can fill - minus the previous skeleton - first by id;
      2. the same, without the ACT filter (same shape, any act);
      3. the same, without the dock filter either;
      4. the shape's first skeleton by id, even when it repeats - the approved shape outranks
         variety, and `why` says which rung was used.
    """
    shape = beat.get("shape")
    pool = [s for s in library if s["shape"] == shape]
    if not pool:
        raise Refused(f"beat {beat.get('beat', '?')}: no skeleton in the library carries the shape {shape!r}")
    entry = beat.get("entry")
    clocked = [s for s in pool if entry_of(s) == entry] if entry else list(pool)
    clocked = clocked or list(pool)
    have = len(beat.get("docks") or []) + (1 if beat.get("entry_card") else 0)
    fillable = [s for s in clocked
                if (have >= 1 or not _needs(s, "{dock}")) and (have >= 2 or not _needs(s, "{dock_b}"))]
    # E99 s70 Apply 3: a skeleton that travels to a page state the plan's plate never declared would
    # redraw nothing, so it is never offered; and a skeleton whose signature IS a mechanism the plan
    # does not name would be an invention.
    states = len(beat.get("states") or [])
    fillable = [s for s in fillable if _needs_states(s) <= states and signature_named(beat, s) is not False]
    clocked = [s for s in clocked if _needs_states(s) <= states and signature_named(beat, s) is not False]
    acts = beat.get("acts") if beat.get("acts") is not None else acts_of(beat)
    by_act = [s for s in fillable if acts & set(s["acts"])] if acts else []
    named = [s for s in by_act if signature_named(beat, s)] or [s for s in fillable if signature_named(beat, s)]
    prev = history[-1] if history else None
    for rung, cands in ((0, named), (1, by_act), (2, fillable), (3, clocked)):
        fresh = [s for s in cands if s["id"] != prev]
        if fresh:
            return fresh[0], ("rung 0 (the plan itself names this beat's mechanism)" if rung == 0 else f"rung {rung}")
    return pool[0], "rung 4 (the only skeleton left for this shape - the shape outranks variety)"


# --------------------------------------------------------------------------- resolving one skeleton

def page_land_offset(entry: str | None, mount_s: float) -> float:
    """Seconds from a page's ENTRY to its chart LANDING - `gate_motion_density._page_land_offset`'s
    own arithmetic, by name: the flat `PAGE_BUILD_END_S` is the ROLL-OUT's landing only."""
    if entry == "mount":
        return round(mount_s + PAGE_BUILD_END_S - MD.LP_ROLL_S - MD.LP_SAVOR_S - MD.LP_FIELD_S, 2)
    if entry == "spiral":
        return MD.LP_SPIRAL_IN_S
    if entry in ("axes", "morph"):
        # E99 s70 / CAPABILITIES.md:121: an `enter=morph` page is on screen from frame 0 as the
        # traced silhouette it grew out of, and it is the DATA that builds - the axes entry's clock
        return MD.LP_BUILD_S
    if entry in ("built", "snap", "camera"):
        return 0.0
    return PAGE_BUILD_END_S


def _time(value, t0: float, t1: float) -> float:
    """A time hole (`{t0}`, `{t1}-3.0`) or a literal second, on this row's own window."""
    if isinstance(value, (int, float)):
        return round(float(value), 2)
    m = TIME_HOLE.match(str(value).strip())
    if not m:
        raise Refused(f"{value!r} is not a time: a second, or {{t0}} / {{t1}} with an offset")
    return round((t0 if m.group(1) == "t0" else t1) + (float(m.group(2)) if m.group(2) else 0.0), 2)


def _text(template: str, fills: dict, beat, skeleton) -> str:
    """A template string with its holes filled - or a refusal naming the beat, the skeleton and the
    hole. The module never invents a page, a plate, a dock or a datum."""
    def sub(m):
        key = m.group(1)
        if fills.get(key) in (None, ""):
            raise Refused(f"beat {beat.get('beat', '?')}: the skeleton {skeleton['id']!r} needs {{{key}}} and the "
                          f"plan names none - the compiler never invents one (the plan is the author's: E99 s66)")
        return str(fills[key])
    return HOLE.sub(sub, str(template))


def _dock_tuple(spec, fills, beat, skeleton, t0, t1, defaults) -> tuple | None:
    """One dock of the row's 5th element: `(id, lane, in, out, options)`. E65: the card reads, then
    parks in the page's OWN room and holds to the row's end. A dock the plan names no asset for is
    DROPPED, never invented - the caller records it in `why`."""
    spec = {"id": spec} if isinstance(spec, str) else dict(spec)
    holes = [h for h in HOLE.findall(str(spec["id"])) if h.startswith("dock")]
    if any(fills.get(h) in (None, "") for h in holes):
        return None
    t_in = _time(spec.get("at", "{t0}"), t0, t1)
    options = dict(spec.get("options") or {})
    for key in ("read_s", "park_s"):
        if spec.get(key) is not None:
            options[key] = spec[key]
    t_out = t1 if defaults.get("card_in_page_room", True) else round(
        t_in + float(spec.get("read_s") or 0) + float(spec.get("park_s") or 0) + CHART_HOLD_MAX_S, 2)
    return (_text(spec["id"], fills, beat, skeleton), DOCK_LANE, t_in, round(min(t_out, t1), 2), options)


def _species(spec, fills, beat, skeleton, t0, t1, land, defaults) -> tuple[dict | None, str | None]:
    """One species of the row's 7th element - or (None, the reason it was dropped).

    E99 s67 Apply 1-2: a light is emitted only where the sentence POINTS, and never before the
    page's own chart lands. A `build_to` IS the build: it is placed to END on the landing.
    """
    out = {"kind": spec["kind"], "at": _time(spec.get("at", "{t0}"), t0, t1)}
    target = dict(spec.get("target") or {})
    holes = [h for v in target.values() for h in HOLE.findall(str(v))]
    if holes:
        if not points(beat):
            return None, f"no light on beat {beat.get('beat', '?')}: the sentence points at nothing (E99 s67 Apply 1)"
        # a SECOND mark (`{datum_b}`) is the skeleton's extra, not the beat's claim: when the plan
        # names one datum the extra species is DROPPED, and only a missing FIRST mark is a refusal
        extra = [h for h in holes if h.endswith("_b") and fills.get(h) in (None, "")]
        if extra:
            return None, (f"the {out['kind']} on beat {beat.get('beat', '?')} wanted a second mark "
                          f"({', '.join('{%s}' % h for h in extra)}) and the plan names one: dropped, never invented")
        target = {k: (int(_text(str(v), fills, beat, skeleton)) if HOLE.search(str(v)) else v)
                  for k, v in target.items()}
    dur = spec.get("dur")
    if isinstance(dur, (int, float)):
        out["dur"] = round(float(dur), 2)
    elif dur is not None:
        out["dur"] = dur
    if target:
        out["target"] = target
    for k, v in (spec.get("options") or {}).items():
        out[k] = _time(v, t0, t1) if isinstance(v, str) and TIME_HOLE.match(v) else v
    if land is not None and out["kind"] == "build_to" and isinstance(out.get("dur"), float):
        out["at"] = round(max(t0, t0 + land - out["dur"]), 2)
    elif land is not None and out["kind"] in LIGHT_AFTER_BUILD_KINDS and defaults.get("light_after_build", True):
        out["at"] = round(max(out["at"], t0 + land), 2)
    if out["at"] >= t1 - SPECIES_TAIL_S:
        return None, (f"the {out['kind']} on beat {beat.get('beat', '?')} has no room left on this row after the "
                      f"page's chart lands: dropped rather than fired over the build (E99 s67 Apply 2)")
    return out, None


def hold_room(sp: dict, species: list, docks: list, t1: float) -> float:
    """The seconds a HELD species has before the next event on its row - the compiler's own clock for
    a `dur: "hold"` (`build_scene_timeline_f`:5158-5175: held until the next species' `at`, a card
    ARRIVING counted as an event, or the row's end, and `until` when the row named one)."""
    ats = sorted([float(x["at"]) for x in species if isinstance(x.get("at"), (int, float))]
                 + [float(d[2]) for d in (docks or [])])
    end = next((a for a in ats if a > float(sp["at"]) + 1e-6), float(t1))
    if isinstance(sp.get("until"), (int, float)) and not isinstance(sp.get("until"), bool):
        end = min(end, float(sp["until"]))
    return round(end - float(sp["at"]), 2)


def flashes(sp: dict, species: list, docks: list, t1: float) -> bool:
    """Would the compiler DROP this species as a flash? A held light with less than its `HOLD_MIN_S`
    of room before the next event is dropped there, so a base that emits one is describing a cut
    that will not have it (found by the third pass: the open's held spotlight, 0.64 s before the
    build, was dropped at compile time and M11 read the chart as unannotated)."""
    return sp.get("dur") == "hold" and hold_room(sp, species, docks, t1) < compiler().HOLD_MIN_S


def annotate_first_chart(species: list, docks: list, t0: float, t1: float, land: float, notes: list) -> None:
    """M11 on the cut's FIRST chart: it never stands full and unannotated.

    The gate's own reading (`gate_motion_density._first_chart_gate`): the page is annotated when one
    of `ANNOTATED_KINDS` fires inside [the landing, the landing + `ANNOTATE_TOL_S`], **or** when a
    `build_to`'s CAP lands within that tolerance of it - *"the line ends ON the datum and the nib
    rests there ... which points at the divergence harder than a ring drawn around it"* (P47 T2). So
    the BUILD is the annotation, and the row's own first build_to is placed to END on the landing
    rather than a beat after its word; a plan that names no build has its first mark pulled back into
    the window instead. E99 s67 Apply 6: the open is one of the few places a chart may stand fully
    drawn - and it is still annotated inside M11's 1.5 s. Mutates in place and records what it did."""
    lo, hi = round(t0 + land, 2), round(t0 + land + ANNOTATE_TOL_S, 2)
    if any(s["kind"] in ANNOTATED_KINDS and lo - EPS <= float(s["at"]) <= hi + EPS
           and not flashes(s, species, docks, t1) for s in species):
        return
    build = next((s for s in species if s["kind"] == "build_to" and isinstance(s.get("dur"), (int, float))), None)
    if build is not None:
        was, dur = float(build["at"]), float(build["dur"])
        if abs(was + dur - lo) <= ANNOTATE_TOL_S + EPS:
            return
        build["at"] = round(max(t0, lo - dur), 2)
        notes.append(f"the first chart's BUILD is placed to END on the page's landing at {lo:.2f}s and not "
                     f"{dur:.1f}s after its own word at {was:.2f}s - the build IS the annotation M11 counts "
                     "(P47 T2: the line ends on the datum), and the open never stands full and unannotated")
        return
    mark = next((s for s in species if s["kind"] in ANNOTATED_KINDS), None)
    if mark is not None:
        was = float(mark["at"])
        mark["at"] = round(min(max(was, lo), hi), 2)
        if abs(was - float(mark["at"])) > EPS:
            notes.append(f"the open's {mark['kind']} moves from {was:.2f}s to {mark['at']:.2f}s: the plan names no "
                         f"build on the first chart, so its own first mark lands inside M11's {ANNOTATE_TOL_S:.1f}s "
                         f"after the page's landing at {lo:.2f}s (E99 s67 Apply 6)")
        return
    notes.append(f"M11 UNANSWERED: the plan names neither a build nor a mark on the first chart (landing {lo:.2f}s) "
                 "- the open's skeleton carries no annotation to place and the compiler invents no datum")


def drop_flashes(species: list, docks: list, t1: float, notes: list) -> list:
    """The held species the compiler would drop as flashes, dropped HERE - so the base's rows say
    what the cut will actually carry (`build_scene_timeline_f`:5174, HOLD_MIN_S)."""
    kept = [s for s in species if not flashes(s, species, docks, t1)]
    for s in species:
        if s not in kept:
            notes.append(f"the held {s['kind']} at {float(s['at']):.2f}s is dropped: "
                         f"{hold_room(s, species, docks, t1):.2f}s of room before the next event, under the "
                         f"compiler's {compiler().HOLD_MIN_S:.1f}s - a held light with no room is a flash")
    return kept


def _aspect_clean(row_docks: list, row_species: list, aspect: str, defaults: dict) -> tuple[list, list, list]:
    """R26-171: at 9:16 no `badges` rail leaves this module. The park does (R26-172 WITHDRAWN)."""
    notes: list[str] = []
    if str(aspect) != "9:16":
        return row_docks, row_species, notes
    if defaults.get("no_rails_9_16", True):
        for d in row_docks:
            if "badges" in d[4]:
                d[4].pop("badges")
                notes.append("the badges rail is not emitted at 9:16 (R26-171)")
    return row_docks, row_species, notes


# --------------------------------------------------------------------------- the windows

def _windows(gs: list[dict], ws: list | None, exits: list[str], hold_s: float,
             arrivals: list | None = None) -> list[tuple]:
    """Each row's (start, end): the take's own cut point before the group's first sentence
    (`words.cut_before`, M13), the rows contiguous, the first row on frame 0.

    A page that arrives BY A CARD (`snap=` / `camera=`) arrives when that card has been READ, not when
    its own first sentence starts - `arrivals[i]`, measured in `_arrivals` off the card's own word.

    M44: a world-plate row shorter than `hold_s` takes the seconds it is missing from the PREVIOUS
    row's tail when that row can spare them, and from the next row's head when it cannot - the beat
    moves, never the words (the gate-fit ruling).
    """
    starts = [0.0]
    for i, g in enumerate(gs[1:], start=1):
        t = round(float(g["t0"]), 2)
        if ws:
            try:
                t = W.cut_before(ws, " ".join(str(g["beats"][0]["sentence"]).split()[:4]), exit=exits[i - 1])
            except SystemExit:
                pass
        starts.append(round(t, 2))
    for i, a in enumerate(arrivals or []):
        if i and a is not None and starts[i - 1] + EPS < round(float(a), 2) < starts[i] - EPS:
            starts[i] = round(float(a), 2)
    ends = starts[1:] + [round(float(gs[-1]["t1"]), 2)]
    for i, g in enumerate(gs):
        if g["world"] == "page" or ends[i] - starts[i] >= hold_s:
            continue
        need = round(hold_s - (ends[i] - starts[i]), 2)
        room = round(starts[i] - starts[i - 1] - hold_s, 2) if i else -1.0
        if room >= need:
            starts[i] = round(starts[i] - need, 2)
            ends[i - 1] = starts[i]
        else:
            ends[i] = round(ends[i] + need, 2)
            if i + 1 < len(starts):
                starts[i + 1] = ends[i]
    return list(zip(starts, ends))


def _exit(g: dict, nxt: dict | None, skeleton: dict, next_entry: str | None) -> tuple[str, str]:
    """How this world LEAVES, and the rule that says so (E47; the plan's Acceptance 2)."""
    if nxt is None:
        return "cut", "the cut is the last word"
    if next_entry == "mount":
        return "cut", "a cut, never into a mount - the mount IS the transition"
    if g["world"] == "page" and nxt["world"] == "page":
        skeleton_exit = str(main_row(skeleton)["exit"])
        return ((skeleton_exit, "page to page: the suck, with no cream between them")
                if skeleton_exit.startswith("suck") else ("cut", "page to page: a straight cut"))
    if g["world"] != nxt["world"] or plate_of(g["plate"]) != plate_of(nxt["plate"]):
        skeleton_exit = str(main_row(skeleton)["exit"])
        if skeleton_exit.split(":")[0] == "door" and g.get("prev_entry") in ("snap", "camera"):
            # E98 s7 / CAPABILITIES.md:38: the page before this one landed FLAT as a card, so it can
            # swing open on its hinge onto this world instead of dipping to it - the transition that
            # carries continuity rather than cutting it (E99 s70).
            return skeleton_exit, "the door, because the page before this one landed flat as a card (E98 s7)"
        return "dip", "the dip because the world changes (E47)"
    return "cut", "a cut inside one world"


# --------------------------------------------------------------------------- the cut's TAIL (P66 T3e)
# The v5 critic, reading the base at 83.00 s and 88.50 s: *"the frames are pixel-identical - the Fed
# page frozen, no caption after 'still ours.', no species, no idle (6.1 s)"*. The last row's window
# ends on the take's LAST WORD and the compiled scene runs to the build's runtime - the timeline
# compiler gives the last row `tl["runtime_s"]` for its end whatever the table says
# (`build_scene_timeline_f.py:5162`) - so every second between them plays a still page. The approved
# cut does not: it ends on an OUTRO CLIP row over exactly those seconds (`build_short.py:443-446`,
# `t_outro` from `authoring.audio.outro_clock`: the card dissolves in over the ring with `life`
# declared for the clip's own seconds, and the row before it ends at `t_outro`, not at the last word).
# The base's answer, in the order the AUTHOR's own record decides it - the mirror of the open, which
# keeps the world the hook is spoken over because the plan names it:
#   1. the plan names a closing world (its last beat's plate is a world of its own, as the open's
#      first beat names the hook's) - it compiles as a row like any other, and the `why` names it;
#   2. the caller hands the build's own `runtime` - the last row is HELD to it and carries its idle,
#      so the table says what the timeline will actually play;
#   3. neither - the `why` hands the tail back by name: THE OUTRO IS THE AUTHOR'S. The compiler will
#      not invent a world (no clip is in the plan, and the kit names no episode's file), and a base
#      that silently ends on a frozen page is what this note exists to stop.
IDLE_OPT = ";idle="        # the plate id's own idle option, as the compiler writes it (`build_scene_timeline_f.py:87`)
CLOSE_IDLE = "live"        # E49 - what a world held past its last word carries: breath + drift, never a still
OUTRO_IS_THE_AUTHORS = ("the outro is the author's - the approved cut ends on its outro clip "
                        "(`build_short.py:443-446`: the outro row from `t_outro` to the runtime, `life` "
                        "declared for the clip's own seconds, the dip into it)")


# THE OUTRO ATTACHED (E99 s72, BACKLOG R26-187). The operator's second read of the base: *"You didn't
# attach the outro either."* E41 (2026-09-05): the brand line *"Not a panic. Not a plot. Mechanics."* is a
# CHANNEL ASSET, recorded once and STITCHED under the Remotion-kit outro card - a script never writes the
# triad. So when the project defines an outro the base's closing row IS that row: the caller resolves the
# project's own values (`generate_base_table.outro_resolver` reads them off `build_short.py` without
# running it) and hands them here, and the compiler writes exactly what the approved cut writes -
# the clip from `t_outro` to the runtime, `life` declared for the clip's own seconds so the pulse gate
# credits its drift, the DIP into it (E47: the card is a world change), and the row BEFORE it ending at
# `t_outro` rather than at the take's last word. The brand line is not a row - it is stitched into the
# take (`audio.stitch_brand_line`, `brand_gap` after the last word) - so its instant is RECORDED in `why`
# and nothing on the table pretends to play it.
OUTRO_EXIT = "dip"          # `build_short.py:443`: E47 - the outro card is a world change, so the dip
OUTRO_LIFE = "life"         # ... and the clip's own drift is declared, so M05 credits it
OUTRO_SIGNATURE = {"dip": "dip", "suck": "suck"}     # `approved-mix.json` method rung 9: the scene's own exit token
OUTRO_SKELETON = "the project's own outro row"
OUTRO_REQUIRED = ("world", "at", "runtime")
OUTRO_LEAD_MAX_S = MD.DIP_S       # the MOST an outro card may begin before the take's last word: the DIP's own
# length, the world change into it (E47; `gate_motion_density.DIP_S`, measured on the reference's 35 dips). The
# approved cut starts the card `OUTRO_LEAD` 0.1 s early and DISSOLVES it in over the ring (`audio.outro_clock`),
# which is inside that; anything earlier is not a lead, it is the card playing OVER words still being spoken.
OUTRO_RUNTIME_EPS = 0.02          # two runtimes this close are ONE runtime (a rounding, not a disagreement) - the
# same number as `generate_base_table.EPS_RUNTIME`, which is what `outro_resolver` reconciles the clock and the
# build with before it ever reaches here; `test_generate_base_table.py` pins the two together.


def check_outro(outro: dict, runtime: float | None = None, last_word_end: float | None = None) -> None:
    """The three things an outro must name, or a refusal BY NAME: the world (the clip the project
    keeps), the instant it starts, and the runtime it plays to. Nothing is defaulted - an outro the
    caller could not resolve is no outro, and the tail goes back to the author in words.

    With the caller's own `runtime` the two must be the SAME runtime: the take on disk is padded to
    the build's, so a closing row that plays to a different number is a base that ends where nothing
    ends. With the take's `last_word_end` the card may not begin more than `OUTRO_LEAD_MAX_S` before
    it - an outro resolved at 5 s under a 40 s take would silently cut 33 s of SPOKEN take off the
    table, which is a refusal, never a trim (E99 s11: the compiler never quietly moves a cut)."""
    missing = [k for k in OUTRO_REQUIRED if outro.get(k) in (None, "")]
    if missing:
        raise Refused(f"the outro names no {', '.join(missing)} - the closing row is the PROJECT's own "
                      "(`build_short.py:443-446`), and the kit names no episode's file")
    if float(outro["runtime"]) <= float(outro["at"]) + EPS:
        raise Refused(f"the outro's runtime ({float(outro['runtime']):.2f}s) is not past its start "
                      f"({float(outro['at']):.2f}s)")
    if runtime is not None and abs(float(outro["runtime"]) - float(runtime)) > OUTRO_RUNTIME_EPS:
        raise Refused(f"the outro plays to {float(outro['runtime']):.2f}s and the build's own runtime is "
                      f"{float(runtime):.2f}s - the take on disk is padded to the BUILD's runtime, so the "
                      "closing row cannot end anywhere else (`generate_base_table.outro_resolver` takes "
                      "the build's when the clock disagrees)")
    if last_word_end is not None and float(outro["at"]) < float(last_word_end) - OUTRO_LEAD_MAX_S - EPS:
        raise Refused(f"the outro starts at {float(outro['at']):.2f}s and the take's last word ends at "
                      f"{float(last_word_end):.2f}s - the card would play over {float(last_word_end) - float(outro['at']):.2f}s "
                      f"of SPOKEN take. It dissolves in at most {OUTRO_LEAD_MAX_S:.2f}s early (the dip's own "
                      "length, `gate_motion_density.DIP_S`; the approved cut's lead is 0.1s)")


def outro_row(outro: dict) -> tuple:
    """The project's outro AS A ROW - the approved cut's own shape (`build_short.py:443-446`)."""
    t0, t1 = round(float(outro["at"]), 2), round(float(outro["runtime"]), 2)
    return (t0, t1, str(outro["world"]), (0, 0, 0), [], str(outro.get("exit") or OUTRO_EXIT),
            [{"kind": OUTRO_LIFE, "at": t0, "dur": round(t1 - t0, 2)}])


def outro_why(outro: dict, rec: dict) -> dict:
    """The outro row's own `why`: the row it is, where its values came from, and the brand line's
    instant - the one thing the table cannot carry (E41: the line is stitched into the take)."""
    t0, t1 = round(float(outro["at"]), 2), round(float(outro["runtime"]), 2)
    exit_ = str(outro.get("exit") or OUTRO_EXIT)
    line = outro.get("brand_line_at")
    rule = (f"the cut CLOSES on the project's own outro row - `{outro['world']}` from {t0:.2f}s to "
            f"{t1:.2f}s, `{OUTRO_LIFE}` declared for its {round(t1 - t0, 2):.2f}s and the `{exit_}` into it "
            f"(E47: the card is a world change), the row before it ending at {t0:.2f}s and not at the "
            f"take's last word. Source: {outro.get('source') or 'the caller'}")
    rule += (f". The BRAND LINE is stitched into the take at {float(line):.2f}s, under the card "
             "(E41, `authoring.audio.stitch_brand_line`) - a channel asset recorded once, never a row "
             "and never a script line" if line is not None else
             ". No brand line was resolved - E41 stitches one under the card when the channel has it")
    return {"beat": rec.get("beat"), "group": rec.get("group"), "skeleton": OUTRO_SKELETON,
            "act": None, "rule": rule, "signature": OUTRO_SIGNATURE.get(exit_, "cut"), "outro": True}


def with_idle(plate: str, kind: str = CLOSE_IDLE) -> tuple[str, bool]:
    """`(the plate id carrying an idle, whether one was added)` - E49: nothing ever goes truly still."""
    return ((plate, False) if IDLE_OPT in str(plate)
            else (f"{plate}{IDLE_OPT}{kind}", True))


def close_the_cut(rows: list[tuple], why: list[dict], runtime: float | None = None,
                  outro: dict | None = None, last_word_end: float | None = None) -> list[tuple]:
    """The cut's LAST row, read against the runtime the build will play - and named in `why`.

    Nothing is invented: the OUTRO row is emitted only where the caller resolved the project's own
    (E41 / E99 s72), a closing world only where the plan names one, the hold only where the caller
    names a runtime, and otherwise the tail is handed back to the author in words. The rows are
    given back (the last one replaced when it is held or trimmed to the outro's start)."""
    recs = rows_why(why)
    if not rows or not recs:
        return rows
    last, rec = list(rows[-1]), recs[-1]
    end = round(float(last[1]), 2)
    if outro:
        check_outro(outro, runtime, last_word_end)
        t0 = round(float(outro["at"]), 2)
        if t0 <= float(last[0]) + EPS:
            raise Refused(f"the outro starts at {t0:.2f}s, at or before the last row's own start "
                          f"({float(last[0]):.2f}s) - the closing row cannot swallow the beat before it")
        if abs(t0 - end) > EPS:
            last[1] = t0
            rows[-1] = tuple(last)
            rec["rule"] += (f"; this row ends at the OUTRO's start ({t0:.2f}s) rather than at {end:.2f}s - "
                            "the approved cut's last page row ends on `t_outro` (`build_short.py:443`)")
        rows.append(outro_row(outro))
        why.append(outro_why(outro, rec))
        return rows
    if world_of(str(last[2])) != "page":
        rec["rule"] += (f"; the cut ends on the closing world the plan's last beat names, held to {end:.2f}s - "
                        "a world of its own carries the seconds after the last word, which is what the approved "
                        "cuts' outro row is for")
        return rows
    if runtime is not None and round(float(runtime), 2) > end + EPS:
        plate, added = with_idle(str(last[2]))
        last[1], last[2] = round(float(runtime), 2), plate
        rows[-1] = tuple(last)
        rec["rule"] += (f"; the last row is HELD to the build's own runtime ({float(runtime):.2f}s) from the take's "
                        f"last word at {end:.2f}s"
                        + (f", and carries an idle (`{IDLE_OPT}{CLOSE_IDLE}`, E49)" if added else " at its own idle")
                        + f" - the timeline gives the last row the runtime for its end whatever the table says "
                          f"(`build_scene_timeline_f.py:5162`), so a row that stops at the last word leaves "
                          f"{round(float(runtime) - end, 2):.2f}s of frozen world no row admits to. "
                        + OUTRO_IS_THE_AUTHORS)
        return rows
    rec["rule"] += (f"; the row ends on the take's last word at {end:.2f}s and the compiled scene runs to the "
                    "build's runtime, so whatever the build's runtime is past that instant plays THIS world (the "
                    "timeline gives the last row the runtime for its end - `build_scene_timeline_f.py:5162`). No "
                    "runtime was handed to the compiler and the plan names no closing world, so the base cannot "
                    "hold the row to it: " + OUTRO_IS_THE_AUTHORS)
    return rows


# --------------------------------------------------------------------------- the compiler

def compile(plan, words=None, defaults: dict | None = None, aspect: str = "16:9",
            library: list[dict] | None = None, pages=None, worlds=None,
            runtime: float | None = None, outro: dict | None = None,
            last_word_end: float | None = None) -> tuple[list[tuple], list[dict]]:
    """The AUTHORED beat plan as the approved skeleton: `(rows, why)`.

    `rows` are the kit's own tuples - what `table.write_shot_table` takes and `table.load_rows`
    reads back. `why` carries ONE record per row: `{beat, skeleton, act, rule, signature, group}` - the
    skeleton chosen, the act (or the shape) that chose it, the rule that applied, and the index of the
    GROUP the row came from (a group is a run of beats over one world, and it plays TWO rows where the
    page mounts over the hook's own world - the approved open).

    `plan` is the records (or the path to `BEAT-PLAN.jsonl`), `words` the take's words (either the
    aligner's `start_s` / `end_s` or `timeline.json`'s `start` / `end`), `defaults` the six
    documented keys of `DEFAULTS`, `aspect` `"16:9"` or `"9:16"`.

    `pages` is the caller's PAGE RESOLVER - `pages(<a resolved ledger plate id>) -> the
    `ledger_page.v1` spec, or None`. The kit names no episode, and a page's ink lives in the
    episode's own `evidence/objects/`, so the CLI hands the resolver in (`generate_base_table.py`).
    With it, every card on a page is placed in the page's OWN room, off its ink (E65, `place_cards`);
    without it the compiler's placer decides at compile time and the row's `why` says so.

    `runtime` is the build's own runtime (the take's `timeline.json` `runtime_s`) when the caller
    has one. The cut plays PAST the last word - the outro's seconds - and the timeline gives the last
    row the runtime for its end whatever the table says, so with it the last row is held to the
    runtime and the table says what will play; without it the tail is named in `why` and handed back
    to the author (`close_the_cut`).

    `outro` is the PROJECT's own outro row, resolved by the caller (`generate_base_table.outro_resolver`):
    `{world, at, runtime, exit?, brand_line_at?, source?}`. With it the cut CLOSES on that row - the clip
    from `t_outro` to the runtime with its `life`, the dip into it, the row before it ending at `t_outro`
    (E41 / E99 s72, `build_short.py:443-446`); without it the tail is the runtime hold or the author's.

    `last_word_end` is the instant the take's last word ENDS - the one an outro is clocked off
    (`audio.outro_clock`). The caller may hand its own (`generate_base_table` already computes it);
    otherwise it is read from `words`. An outro that starts more than the dip before it is REFUSED,
    never trimmed: it would be playing a card over words still being spoken (`check_outro`).

    `worlds` is the caller's WORLD resolver - `worlds(<a plate or clip id>) -> the id the table should
    carry`. The plan names the hook's world as the cut recorded it (`clip:<name>`), and where that file
    lives is the EPISODE's business, not the kit's, so the CLI hands the resolver in
    (`generate_base_table.world_resolver`). Without it the plan's own id is written through unchanged.
    """
    plan = load_plan(plan) if isinstance(plan, (str, Path)) else list(plan)
    check_plan(plan)
    lib = usable_library(library if library is not None else load_library(), aspect)
    d = {**DEFAULTS, **(defaults or {})}
    ws = _norm_words(words)
    gs = groups(plan)
    picks = _pick(gs, lib, d, ws)
    spans = _windows(gs, ws, [p["exit"] for p in picks], float(d.get("plate_hold_s", PLATE_MIN_S)),
                     _arrivals(gs, ws))
    rows, why = [], []
    for i, (g, pick, (t0, t1)) in enumerate(zip(gs, picks, spans)):
        made = _group_rows(g, pick, t0, t1, d, aspect, first=i == 0, ws=ws, pages=pages, worlds=worlds)
        rows.extend(r for r, _ in made)
        why.extend({**w, "group": i} for _, w in made)
        why.extend(silent_record(b) for b in g["beats"] if is_silent(b))
    floats = chart_cards_that_float(rows)
    if floats:
        raise Refused("a thrown chart card floats over the world: " + "; ".join(floats))
    orphans = camera_entries_with_no_card(rows)
    if orphans:
        raise Refused("a page arrives by a card no row carries: " + "; ".join(orphans))
    if last_word_end is None and ws:
        last_word_end = max(float(w["end_s"]) for w in ws)
    rows = close_the_cut(rows, why, runtime, outro, last_word_end)
    if ws:
        T.hold_until(rows, ws)
    return rows, why


def _arrivals(gs: list[dict], ws) -> list:
    """When each group's page ARRIVES, for the groups that arrive BY A CARD - else None.

    E99 s70 / CAPABILITIES.md:76 and :84: a `snap=<dock>` or `camera=<dock>` page is the card that was
    thrown a moment ago, grown or pushed to the stage. The approved cut throws the Fed card on
    *"The Fed still"* and lands the page on *"moved"* - `t_fed_still` / `t_moved`,
    the two words the approved cut's own table names (the skeleton `card-thrown-then-the-camera-pushes`
    cites its rows) - 1.11 s apart on that take, which is the
    card's own READ clock (`DOCK_READ_S`), not the next sentence's first word. Base v3 started that row
    at the next beat instead, so the camera's 0.45 s arrival (`build_scene_timeline_f.CAMERA_ARRIVAL_S`)
    was still in flight at 77.80 s: the parent read it as a blurred page with no card.
    """
    C = compiler()
    out: list = []
    for i, g in enumerate(gs):
        card = str(g.get("entry_card") or "")
        prev = gs[i - 1] if i else None
        if not card or prev is None or not ws:
            out.append(None)
            continue
        when = [t for b in prev["beats"] for mv in moves_of(b)
                if str(mv.get("kind")) == MOVE_DOCK and str(mv.get("asset")) == card
                for t in [word_at(ws, str(mv.get("at_word") or ""), float(b["t0"]), float(b["t1"]))]
                if t is not None
                for t in [t + float((mv.get("options") or {}).get("read_s") or C.DOCK_READ_S)]]
        out.append(round(min(when), 2) if when else None)
    return out


def camera_entries_with_no_card(rows: list[tuple]) -> list[str]:
    """Every `camera=<dock>` / `snap=<dock>` page whose card NO row carries - one message each.

    The parent's read of base v3 at 77.80 s: *"the base is a blurred page and no card"*. The entry is a
    read-back token and the compiler emitted it whatever the rows held, so a page could arrive by a
    card that was never thrown - a camera pushing to nothing. The approved cut always carries it: the
    card is thrown on the row BEFORE and lives to that row's end (`build_short.py:403-420`), and the
    timeline then holds it through the arrival (`build_scene_timeline_f.extend_camera_cards`). So the
    card is owed on this row or on the one before it, live at this row's start."""
    out: list[str] = []
    for n, r in enumerate(rows):
        head, _, card = str(entry_token_in(str(r[2])) or "").partition("=")
        if head not in BUILT_ON_ARRIVAL or not card:
            continue
        mine = [x for x in (r[4] or []) if str(x[0]) == card]
        before = [x for x in (rows[n - 1][4] or []) if str(x[0]) == card
                  and float(x[3]) >= float(r[0]) - EPS] if n else []
        if mine or before:
            continue
        out.append(f"row {n + 1}: `{page_of(str(r[2]))}` arrives by `{head}={card}` at {float(r[0]):.2f}s and no row "
                   f"carries `{card}` - the camera pushes to a card that was never thrown, which renders as a page "
                   "mid-transition and nothing else (E99 s70/s71). Throw the card on the beat before (the approved "
                   "cut does: the card lands on one sentence and the page arrives on the next word), or give the "
                   "page an entry of its own (`axes`, `mount`, `spiral`).")
    return out


def _group_rows(g: dict, pick: dict, t0: float, t1: float, d: dict, aspect: str, first: bool,
                ws=None, pages=None, worlds=None) -> list[tuple]:
    """One group as the row(s) it plays, each with its own `why` record.

    Two rows where the page MOUNTS over the hook's world, because that is what the approved open is -
    the clip from frame 0 to the mount word, then the page mounting over it
    (the approved open's own pair). One row for everything else."""
    page_row = lambda a: (_row(g, pick, a, t1, d, aspect, first, ws=ws, pages=pages, worlds=worlds),
                          {"beat": int(g["beats"][0]["beat"]), "skeleton": pick["skeleton"]["id"],
                           "act": str(g["act"] or ""), "rule": "; ".join([pick["rule"], *pick["notes"]]),
                           "signature": pick["skeleton"]["signature"]})
    if not g.get("open_mounts"):
        return [page_row(t0)]
    at = mount_word_at(g, t0, t1)
    world = _world_row(g, pick, (under_rows(pick["skeleton"]) or [WORLD_ROW])[-1], t0, at, d, ws, worlds)
    made = page_row(at)
    made[1]["beat"] = int(g["beats"][len(g.get("under_beats") or [])]["beat"])
    return [world, made]


# The hook's world as a row, for an open whose own skeleton does not declare one: the plan's plate,
# still, no cards, and NO exit - the page's arrival is the transition (E45; `build_short.py:281-282`).
WORLD_ROW = {"start": "{t0}", "end": "{t1}", "plate": "{plate}", "ken": [0, 0, 0], "docks": [],
             "exit": None, "species": []}


MOUNT_WORLD_MIN_S = 1.0   # the hook's world gets a second of its own before the cream rises over it


def mount_word_at(g: dict, t0: float, t1: float) -> float:
    """When the page MOUNTS over the hook's world - the hook's LAST sentence.

    Two hook sentences or more: the LAST one - one approved cut mounts on the opening words of its last
    hook sentence, and its two rows split exactly there. ONE hook sentence: its last word - the other
    approved open mounts on the hook's final word, with the card it snaps from thrown a second before
    it. (Both tables are cited by the open skeletons' own `source`.) Never closer than
    `MOUNT_WORLD_MIN_S` to frame 0: a world with no seconds of its own is the bare cream this rule
    exists to end."""
    under = g.get("under_beats") or []
    rest = g["beats"][len(under):]
    page_t0 = float(rest[0]["t0"]) if rest else t1
    if not under:
        return round(t0, 2)
    at = float(under[-1]["t0"]) if len(under) > 1 else float(under[-1]["t1"])
    return round(min(max(at, t0 + MOUNT_WORLD_MIN_S), page_t0), 2)


def _world_row(g: dict, pick: dict, tpl: dict, t0: float, t1: float, d: dict, ws, worlds) -> tuple:
    """The hook's OWN world, held under the page that mounts over it - the approved open's first row.

    E99 s67 Apply 6 as the approved cuts play it: the hook is a world (a clip, a plate) and the page
    RISES OVER IT on the hook's last sentence. Base v3 absorbed the hook into the page's row and
    played bare cream at 0.20 s where the approved cut plays the tea-break counter; a mount with no
    world under it is a refusal. The row carries NO exit: the mount IS the transition (E45)."""
    beats = g.get("under_beats") or g["beats"][:1]
    beat = beats[0]
    # the plan's own id, options and all: the hook's world is the world the CUT was spoken over and
    # its idle (`;idle=drift;drift=35`) is part of it - a plate that stops drifting is a still (E49)
    plate = _text(tpl["plate"], {"plate": str(beat["plate"]), "page": ""}, beat, pick["skeleton"])
    plate = str(worlds(plate)) if worlds else plate
    ken = tuple(tpl["ken"]) if isinstance(tpl["ken"], list) else tpl["ken"]
    notes, species, docks = [], [], []
    for b in beats:
        for mv in moves_of(b):
            made, why = _move(mv, b, ws, t0, t1, ken, None, d)
            if made is None:
                notes.append(why)
            elif mv.get("kind") == MOVE_DOCK:
                docks.append(tuple(made))
            else:
                species.append(made)
    species.sort(key=lambda x: (float(x["at"]), str(x["kind"])))
    if round(t1 - t0, 2) + 1e-9 < float(d.get("plate_hold_s", PLATE_MIN_S)):
        notes.append(f"the hook's world holds {t1 - t0:.2f}s, under M44's six seconds - which is what both approved "
                     "opens do (the hook is spoken over it and the page mounts on the hook's last sentence); the gate "
                     "WARNs on a short plate and FAILs one that carries a card, and the author's answer is a longer "
                     "hook, not a later mount")
    rule = ("the hook's own world holds under the page that mounts over it at " + f"{t1:.2f}s"
            + " - the open keeps the world the hook is spoken over and the cream rises on the hook's last "
              "sentence (E99 s67 Apply 6, the approved opens' own first row). A mount with no world "
              "under it is bare cream, which is what base v3 played at 0.20s")
    if notes:
        rule += "; " + "; ".join(notes)
    return ((t0, t1, plate, ken, docks, tpl.get("exit"), species or None),
            {"beat": int(beat["beat"]), "skeleton": pick["skeleton"]["id"], "act": str(beat.get("act") or ""),
             "rule": rule, "signature": "hold"})


def plain_recasts(species: list) -> list[float]:
    """Every `chart_to recast` the author left un-keyed made PLAIN, and the instants, for the row's `why`.

    E99 s67 Apply 2: *"every page BUILDS with the effects and then holds built ... there should be 0 reason
    why you cant build the chart using the effects"*. A recast's plain form is the hand-over - the standing
    chart leaves by length and the named state draws on ITS OWN BUILD ENVELOPE (`effects/cards/chart_to.json`,
    phase "target builds") - and that is what the approved portrait cut's own table writes, and plays:
    measured at 52.00 s on the approved build, one bar growing; on base v3, all four standing. `keyed: false`
    is the grammar's own word for it (`build_scene_timeline_f.py:388`: *"false / absent is the hand-over"*).
    An author who NAMES a key keeps it - a keyed recast is the same data travelling (E64), not a build.
    """
    out = []
    for sp in species:
        if sp.get("kind") == "chart_to" and sp.get("to") == "recast" and "keyed" not in sp:
            sp["keyed"] = False
            out.append(round(float(sp["at"]), 2))
    return out


CARD_SLOT = re.compile(r"^dock-[a-z0-9]+-(.+)$")


def chart_cards_that_float(rows: list[tuple]) -> list[str]:
    """Every thrown FULL CHART CARD that nothing takes to the stage - one message each.

    E99 s71 (the operator, on the first base's 76.3 s frame: a portrait chart page thrown as a card,
    bleeding off the top and the bottom of the frame and over the caption): a thrown full-page card
    must then ZOOM (`:snap=<dock>`) or the camera must PUSH to it (`:camera=<dock>`) - it never
    floats over the plate. E99 s67 Apply 5 is the other half: a DOCK is an evidence still, never a
    chart page thrown on the open.

    Which cards are chart cards is DERIVED, never guessed - the kit names no episode: a dock whose
    name after its slot letter appears inside a LEDGER page id this cut carries is that page's own
    card (`dock-<slot>-<name>` against `ledger:ev-<name>-v1:<variant>:...`).
    """
    pages = [str(r[2]) for r in rows if str(r[2]).startswith("ledger:")]
    taken = {str(entry_token_in(p) or "").split("=", 1)[1]
             for p in pages if str(entry_token_in(p) or "").split("=", 1)[0] in BUILT_ON_ARRIVAL}
    out: list[str] = []
    for n, r in enumerate(rows, 1):
        for dock in r[4] or []:
            asset, opts = str(dock[0]), (dock[4] if len(dock) > 4 else {}) or {}
            m = CARD_SLOT.match(asset)
            if not m or asset in taken or str(opts.get("arrive")) != "throw":
                continue
            page = next((p for p in pages if m.group(1) in p), None)
            if page is None:
                continue
            out.append(f"row {n}: `{asset}` is the FULL CHART CARD of {page_of(page)} thrown onto the world at "
                       f"{float(dock[2]):.2f}s and nothing takes it to the stage - a thrown chart card ZOOMS "
                       f"(`:snap={asset}`) or the camera PUSHES to it (`:camera={asset}`) on the page it becomes, "
                       "never floats over the world (E99 s71). Name the entry on that page's own plate in the plan, "
                       "or dock an evidence still instead (E99 s67 Apply 5).")
    return out


SILENT_NOTE = "the plan names no move for this sentence - the author's to add or to leave"
LIGHT_ONLY_NOTE = (
    "the plan names only a LIGHT on this sentence, and a light is never the move (E99 s71, the operator: a spotlight "
    "is never the move - when a sentence names a thing, the THING ARRIVES): a badge or pill springing with its "
    "callout, a stamped prop or icon, a docked screenshot, a flight. The move this act asks for is in "
    "docs/content-video-engine/SPECIES-BY-SENTENCE.md under the act below, and in the capability's own `Use when:` "
    "line (docs/content-video-engine/CAPABILITIES.md)")
# The species that only PUNCTUATE what is already on screen - they darken, ring, or push the eye at
# a thing, and none of them is a thing arriving. A beat whose whole plan is one of these is silent.
LIGHT_ONLY_KINDS = ("spotlight", "callout", "focus_zoom", "ring", "relight", "punch", "pull_back", "vignette")


def is_silent(beat) -> bool:
    """Does the plan leave this beat with nothing the viewer can NAME? (E99 s71.)

    A beat with no moves is silent, and so is a beat whose every move is a light: the light is
    punctuation on a move that is not there yet. Naming it is not a refusal - the author may have
    meant the sentence to play under a held world - it is written into `why` because a base nobody
    can see the holes in is read as a cut (E99 s68).
    """
    moves = moves_of(beat)
    return not moves or all(str(m.get("kind")) in LIGHT_ONLY_KINDS for m in moves)


def silent_record(beat) -> dict:
    """A beat the plan leaves SILENT, named in `why` so the agent sees where to modify (E99 s68)."""
    moves = moves_of(beat)
    lights = [str(m.get("kind")) for m in moves]
    note = SILENT_NOTE if not moves else (
        LIGHT_ONLY_NOTE + f" - this beat carries {', '.join(lights)} and nothing else; its act is "
        f"{str(beat.get('act') or 'unnamed')!r}")
    return {"beat": int(beat["beat"]), "silent": True, "lights_only": bool(moves),
            "sentence": str(beat.get("sentence") or ""), "note": note}


def rows_why(why: list[dict]) -> list[dict]:
    """The ROW records of `why` - one per emitted row, in row order."""
    return [w for w in why if not w.get("silent")]


def silent_why(why: list[dict]) -> list[dict]:
    """The SILENT-beat records of `why`, in beat order - what the plan left the base nothing to do."""
    return [w for w in why if w.get("silent")]


def _norm_words(words) -> list[dict] | None:
    """The take's words in `words.py`'s shape, from either the aligner's or `timeline.json`'s."""
    if not words:
        return None
    ws = words.get("words") if isinstance(words, dict) else words
    return [{"w": w["w"], "start_s": float(w.get("start_s", w.get("start"))),
             "end_s": float(w.get("end_s", w.get("end")))} for w in ws]


def _pick(gs: list[dict], lib: list[dict], d: dict, ws=None) -> list[dict]:
    """The skeleton, the entry and the exit each group gets - decided before any window is timed,
    because the exit decides where the boundary before the NEXT row lands (M13)."""
    picks: list[dict] = []
    history: list[str] = []
    seen_pages: list[str] = []
    for i, g in enumerate(gs):
        nxt = gs[i + 1] if i + 1 < len(gs) else None
        shape, rule = shape_of(g, i, nxt, tuple(seen_pages))
        if g["world"] == "page":
            seen_pages.append(page_of(g["plate"]))
        g["shape"], g["acts"] = shape, acts_of({"act": g["act"]})
        g["states"] = group_states(g)                       # the `;then=` chain this page declares
        g["prev_entry"] = gs[i - 1].get("entry") if i else None
        g["thrown_before"] = bool(i and any(str(mv.get("kind")) == MOVE_DOCK
                                            and (mv.get("options") or {}).get("arrive") == "throw"
                                            for b in gs[i - 1]["beats"] for mv in moves_of(b)))
        g["entry"], g["entry_token"], entry_rule = _entry(g, shape, d, ws)
        # THE CARD THE PAGE CAME OUT OF (E99 s70 / s71). A `snap=<dock>` or `camera=<dock>` entry
        # names the card on the plate id itself, not in the beat's `capabilities` - so it is the
        # group's `{dock}` where the plan names no other, and it is never docked AGAIN onto the page
        # it became.
        tok = str(g.get("entry_token") or "")
        g["entry_card"] = tok.split("=", 1)[1] if "=" in tok and tok.split("=", 1)[0] in BUILT_ON_ARRIVAL else None
        skeleton, rung = choose(g, history, lib)
        history.append(skeleton["id"])
        picks.append({"skeleton": skeleton, "notes": [],
                      "rule": "; ".join(x for x in (rule, entry_rule, rung) if x)})
    for i, g in enumerate(gs):
        # the card the NEXT page grows out of: it is thrown on THIS row and the page after it becomes
        # it (`snap=` / `camera=`), so this row never gives it a room of its own (E99 s71)
        g["next_entry_card"] = gs[i + 1].get("entry_card") if i + 1 < len(gs) else None
    for i, pick in enumerate(picks):
        nxt = gs[i + 1] if i + 1 < len(gs) else None
        next_entry = entry_of(picks[i + 1]["skeleton"]) if nxt is not None else None
        pick["exit"], exit_rule = _exit(gs[i], nxt, pick["skeleton"], next_entry)
        pick["rule"] += "; " + exit_rule
    return picks


def _entry(g: dict, shape: str, d: dict, ws=None) -> tuple:
    """The entry the CLOCK demands of a page - `(its head, the whole token, the rule in words)`.

    The mount when the beat's number lands `MOUNT_AT_OR_AFTER_S` or more after the page's entry, the
    axes otherwise (never `built`); the clock outranks the variety rule - the approved shape is not
    traded for variety.

    ONE thing outranks the clock, and it is the plan (E99 s66): when the AUTHOR's own plate declares
    an entry whose chart is already on the page as it arrives (`BUILT_ON_ARRIVAL`) and the plan's
    first LIGHT move is spoken before the clock's entry would have finished drawing, the author's
    entry stands. The alternative is a light over a build, and the compiler will not fire one (E99
    s67 Apply 2) and will not move the author's beat either - so it stops manufacturing the conflict.
    """
    if g["world"] != "page":
        return None, None, ""
    entry, rule = _clock_entry(g, shape, d)
    declared = entry_token_in(g["plate"])
    head = str(declared).split("=", 1)[0]
    if head in CONTINUITY_ENTRIES:
        # E99 s70 (the operator: "you dropped most of the continuity building transitions like
        # morphs, transformation, and 'the door'"): the snap, the camera arrival and the object
        # that becomes the chart CARRY the previous world into this one. The clock decides between
        # a mount and an axes entry - it never overwrites a continuity transition the author wrote.
        return head, declared, (f"the page arrives by the author's own `{declared}`: a continuity entry carries the "
                                f"world that was there into this one and the clock never replaces it (E99 s70; the "
                                f"clock alone would have written {entry})")
    light = first_light_move(g, ws) if ws else None
    if light is not None and head in BUILT_ON_ARRIVAL:
        land = page_land_offset(entry, _mount_s(g["plate"]))
        if light < float(g["t0"]) + land - EPS:
            return (str(declared).split("=", 1)[0], declared,
                    f"the page arrives by the author's own `{declared}` and not by {entry}: the plan's first light "
                    f"lands at +{light - float(g['t0']):.1f}s, before a {entry} build would have finished at "
                    f"+{land:.1f}s (E99 s66 - the plan is the intelligence; the compiler neither fires a light over "
                    "a build nor moves the author's beat)")
    return entry, entry, rule


def _clock_entry(g: dict, shape: str, d: dict) -> tuple[str, str]:
    """The entry the clock alone would write, and why."""
    if shape == SHAPE_RETURN:
        return "spiral", "the spiral because the beat returns"
    if g.get("open_mounts"):
        return "mount", "the mount because the hook's world is not a page (the page mounts over it)"
    late = next((round(float(b["t0"]) - g["t0"], 2) for b in g["beats"] if names_a_number(b)), None)
    if late is not None and late >= MOUNT_AT_OR_AFTER_S:
        return "mount", f"the mount because the number lands at +{late:.1f}s, never built (E99 s67 Apply 3)"
    return str(d.get("page_entry", "axes")), (
        f"the axes because the number lands at +{late:.1f}s" if late is not None
        else "the axes because no number lands on this page (E99 s67 Apply 6)")


def _page_spec(plate: str, pages, notes: list) -> dict | None:
    """The `ledger_page.v1` spec behind a resolved ledger plate, through the CALLER's own resolver -
    or None when the caller handed none (the kit never opens an episode's evidence itself) or when
    the page cannot be read, which is a note on the row and never a refusal: a base whose cards keep
    the compiler's placer is still a base."""
    if pages is None or not str(plate).startswith("ledger:"):
        return None
    try:
        page = pages(plate)
    except (ValueError, OSError, KeyError, TypeError) as exc:
        notes.append(f"the page's own geometry could not be read ({exc}) - its cards keep the compiler's placer")
        return None
    if not isinstance(page, dict) or not page:
        notes.append("the page resolver names no page for this plate - its cards keep the compiler's placer")
        return None
    return page


def _row(g: dict, pick: dict, t0: float, t1: float, d: dict, aspect: str, first: bool,
         ws: list[dict] | None = None, pages=None, worlds=None) -> tuple:
    """One skeleton's template row, resolved onto one group's window - then the group's beats' own
    NAMED MOVES realised on it, each timed on the word it belongs to."""
    skeleton, beat, notes = pick["skeleton"], g["beats"][0], pick["notes"]
    tpl = copy.deepcopy(main_row(skeleton))
    cards = list(g["docks"]) or ([g["entry_card"]] if g.get("entry_card") else [])
    fills = {"page": page_of(g["plate"]) if g["world"] == "page" else "",
             "plate": plate_of(g["plate"]), "mount_s": _mount_s(g["plate"]),
             **{k: v for k, v in zip(("dock", "dock_b"), cards)},
             **{k: v for k, v in zip(("datum", "datum_b"), _data(g))}}
    plate = _text(tpl["plate"], fills, beat, skeleton)
    if worlds and not plate.startswith("ledger:"):
        plate = str(worlds(plate))          # the episode's own file for the world the plan names
    if plate.startswith("ledger:") and g.get("entry"):
        plate, moved = set_entry(plate, g.get("entry_token") or g["entry"], float(fills["mount_s"]))
        if moved:
            notes.append(f"the skeleton's own entry gives way to the clock's: {g['entry']} "
                         "(the approved shape is enforced on the page, not left to the skeleton)")
    # E99 s70 Apply 3: the page's own CHAIN of states travels with it. `{page}` is the plate id with
    # its `;options` tail stripped, so without this the skeleton rebuilds the page WITHOUT the
    # `;then=` states its own `chart_to` moves travel to - and every one of them renders nothing.
    chain = group_states(g)
    if chain and plate.startswith("ledger:"):
        plate = with_states(plate, chain)
        notes.append("the page's own `;then=` chain travels with it (" + ", ".join(chain) +
                     "): a chart_to that reaches a state the plate never declared redraws nothing (E99 s70 Apply 3)")
    land = page_land_offset(entry_in(plate), float(fills["mount_s"])) if plate.startswith("ledger:") else None
    docks = []
    for spec in tpl.get("docks") or []:
        dock = _dock_tuple(spec, fills, beat, skeleton, t0, t1, d)
        if dock and str(dock[0]) == str(g.get("entry_card") or ""):
            notes.append(f"no card on this row: `{dock[0]}` is the card this page GREW OUT OF, and a page never "
                         "docks the card it became (E99 s71)")
            continue
        (docks.append(list(dock)) if dock else
         notes.append("no card on this row: the plan names no dock for the beat (evidence is never invented)"))
    species = []
    for spec in tpl.get("species") or []:
        # a light lands on the SENTENCE it points with, so it is judged against the beat that is
        # speaking at that instant - not against the row's first beat (E99 s67 Apply 1)
        on = _beat_at(g, _time(spec.get("at", "{t0}"), t0, t1))
        out, why = _species(spec, {**fills, **_datum_fills(on, g)}, on, skeleton, t0, t1, land, d)
        (species.append(out) if out else notes.append(why))
    ken = tuple(tpl["ken"]) if isinstance(tpl["ken"], list) else tpl["ken"]
    # THE BEAT'S NAMED MOVES, after the skeleton's own: the plan is the intelligence, and it already
    # says what this sentence does. The skeleton gives the row its SHAPE; the moves give it its beats.
    made_docks: list = []
    for b in g["beats"]:
        for mv in moves_of(b):
            made, why = _move(mv, b, ws, t0, t1, ken, land, d)
            if made is None:
                notes.append(why)
            elif mv.get("kind") == MOVE_DOCK:
                made_docks.append(list(made))
            else:
                species.append(made)
    # the SAME card twice on one row is not two cards: where the plan lands a card the skeleton also
    # filled from the group's capabilities, the plan's own wins - it carries the word and the options
    # ... and the same for a TRANSFORM: where the plan's own beats name a `chart_to`, the skeleton's
    # template one is the shape's suggestion of a move the author has already made, on their own word
    if any(str(sp.get("kind")) == "chart_to" for sp in species[len(tpl.get("species") or []):]):
        keep = [sp for i, sp in enumerate(species)
                if not (i < len(tpl.get("species") or []) and str(sp.get("kind")) == "chart_to")]
        if len(keep) != len(species):
            notes.append("the plan's own chart_to replaces the skeleton's: the beat names the transform and the "
                         "word it lands on (E99 s66 - the plan is the intelligence)")
        species = keep
    named = {str(x[0]) for x in made_docks}
    kept = [x for x in docks if str(x[0]) not in named]
    if len(kept) != len(docks):
        notes.append(f"the plan's own card on {', '.join(sorted(named & {str(x[0]) for x in docks}))} replaces the "
                     "skeleton's fill of the same asset (the beat named the word it lands on)")
    docks = kept + made_docks
    for sp in species:   # E99 s70 Apply 3: a transform that would render nothing is refused, by name
        if str(sp.get("kind")) != "chart_to":
            continue
        err = chart_to_error(sp, plate, _beat_at(g, float(sp["at"])).get("beat", "?"))
        if err:
            raise Refused(err)
    docks, species, aspect_notes = _aspect_clean(docks, species, aspect, d)
    notes.extend(aspect_notes)
    plain = plain_recasts(species)
    if plain:
        notes.append("the recast(s) at " + ", ".join(f"{t:.2f}s" for t in plain) + " carry the approved table's own "
                     "PLAIN hand-over (`keyed: false`, the grammar's word for it - build_scene_timeline_f.py:388): "
                     "the standing chart leaves by length and the arriving state DRAWS ON ITS OWN BUILD ENVELOPE "
                     "(effects/cards/chart_to.json, phase \"target builds\"), which is E99 s67 Apply 2 - a chart "
                     "never lands fully built - and what the approved cut plays (`build_short.py:386`, read at "
                     "52.00s: one bar growing, not four standing)")
    docks.sort(key=lambda x: (float(x[2]), str(x[0])))
    species.sort(key=lambda x: (float(x["at"]), str(x["kind"])))
    # E65: every card that did not place itself takes a room of the PAGE's own, and never a room a
    # card beside it already holds (the third pass: four of the five cards read at the stage's centre,
    # over the page's ink, because a bare `centre: True` is a stage placement and not a page one)
    if land is not None:
        docks = bound_by_state(docks, species, notes)   # E65: the room is the page as it stands ...
    becomes = str(g.get("next_entry_card") or "")
    thrown = [x for x in docks if str(x[0]) == becomes]
    if thrown:
        notes.append(f"`{becomes}` keeps the throw the plan gave it and takes no room of this page's: it is the card "
                     "the NEXT world grows out of - the camera pushes to it, or it snaps up, on the row after this "
                     "one (E99 s71; CAPABILITIES.md:76 and :84; `build_short.py:403-420`)")
    page = _page_spec(plate, pages, notes)               # the page's own geometry - and its own INKS (E67)
    ink = ink_note(page)
    if ink:
        notes.append(ink)
    docks = place_cards([x for x in docks if str(x[0]) != becomes],   # ... and then it is given -
                        page, aspect, notes,
                        species, t1, d) + thrown        # ... and the page PARKS when it has none to give
    for sp in species:                                  # the parks the placer just made are checked like the rest
        if str(sp.get("kind")) == "chart_to":
            err = chart_to_error(sp, plate, _beat_at(g, float(sp["at"])).get("beat", "?"))
            if err:
                raise Refused(err)
    species.sort(key=lambda x: (float(x["at"]), str(x["kind"])))
    if first and land is not None:
        annotate_first_chart(species, docks, t0, t1, land, notes)   # M11: the open is annotated as it lands
    species = drop_flashes(species, docks, t1, notes)               # ... and the base says what the cut will carry
    if g["world"] != "page" and round(t1 - t0, 2) + 1e-9 < float(d.get("plate_hold_s", PLATE_MIN_S)):
        notes.append("the plate could not reach its six seconds (M44)")
    docks.sort(key=lambda x: (float(x[2]), str(x[0])))
    species.sort(key=lambda x: (float(x["at"]), str(x["kind"])))
    return (t0, t1, plate, ken, [tuple(x) for x in docks], pick["exit"], species)


def _move(mv: dict, beat, ws, t0: float, t1: float, ken, land, d: dict) -> tuple:
    """One named move as what it is on the row - `(a species dict or a dock list, None)`, or
    `(None, the reason it was dropped)`.

    REFUSED, never silently moved (the move is the AUTHOR's): a phrase the take does not carry
    inside the beat's own window; a light asked for before the page's chart lands (E99 s67
    Apply 1-2); a camera move over a Ken Burns (s9.28 C3). DROPPED with its reason in `why`: a move
    whose word falls outside the row the beat ended up on - the window is the compiler's (M13, M44),
    so the author is told rather than refused.
    """
    kind, n = mv["kind"], beat.get("beat", "?")
    if ws is None:
        raise Refused(f"beat {n}: the {kind} move lands on {mv['at_word']!r} and this compile has no take - "
                      "a move is timed on the WORD it belongs to (the take is the clock), never from a stopwatch")
    t = word_at(ws, str(mv["at_word"]), float(beat["t0"]), float(beat["t1"]))
    if t is None:
        raise Refused(f"beat {n}: the take carries no {mv['at_word']!r} inside that beat's own window "
                      f"({float(beat['t0']):.2f}-{float(beat['t1']):.2f}s) - a move names a phrase of its own "
                      "sentence, and the compiler will not hunt for it elsewhere in the take")
    if kind in CAMERA_MOVES and ken and ken[0]:
        raise Refused(f"beat {n}: a {kind} over Ken Burns scale {ken[0]} - a camera move and a Ken Burns never "
                      "share a window (s9.28 C3); the move or the skeleton's ken has to give")
    if land is not None and kind in LIGHT_AFTER_BUILD_KINDS and d.get("light_after_build", True) and t < t0 + land - EPS:
        raise Refused(f"beat {n}: the {kind} on {mv['at_word']!r} fires at {t:.2f}s, before this page's own chart "
                      f"lands at {t0 + land:.2f}s - a light is punctuation, not a cover for the build (E99 s67 "
                      "Apply 1-2). The compiler refuses it rather than move the author's beat.")
    if not (t0 - EPS <= t < t1 - SPECIES_TAIL_S):
        return None, (f"the {kind} on beat {n} ({mv['at_word']!r}, {t:.2f}s) falls outside the row its beat "
                      f"landed on ({t0:.2f}-{t1:.2f}s): dropped, never re-timed")
    if kind == MOVE_DOCK:
        options = dict(mv.get("options") or {})
        lane = options.pop(MOVE_SLOT, DOCK_LANE)
        out = t1 if d.get("card_in_page_room", True) else round(
            t + float(options.get("read_s") or 0) + float(options.get("park_s") or 0) + CHART_HOLD_MAX_S, 2)
        return [str(mv["asset"]), lane, t, round(min(out, t1), 2), options], None
    sp: dict = {"kind": kind, "at": t}
    if mv.get("dur") is not None:
        sp["dur"] = round(float(mv["dur"]), 2) if isinstance(mv["dur"], (int, float)) else mv["dur"]
    if mv.get("target"):
        sp["target"] = copy.deepcopy(mv["target"])
    if mv.get("label") is not None:
        sp[LABEL_FIELD.get(kind, DEFAULT_LABEL_FIELD)] = mv["label"]
    for k, v in (mv.get("options") or {}).items():
        sp[k] = copy.deepcopy(v)
    return sp, None


def _beat_at(g: dict, t: float):
    """The beat that is SPEAKING at `t` - the row's own first beat when the instant sits outside
    every beat's window (a species placed before the first word of the row)."""
    return next((b for b in g["beats"] if float(b["t0"]) <= t < float(b["t1"])),
                next((b for b in g["beats"] if float(b["t0"]) >= t), g["beats"][0]))


def _datum_fills(beat, g: dict) -> dict:
    """`{datum}` / `{datum_b}` for one beat: the indices that beat's own capabilities name, and the
    group's marks behind them - the author's, never the compiler's."""
    data = data_of(beat) + [i for i in _data(g) if i not in data_of(beat)]
    return {k: v for k, v in zip(("datum", "datum_b"), data)}


def _mount_s(plate: str) -> float:
    """`{mount_s}`: the soak the AUTHOR's own plate names, else the player's own default
    (`gate_motion_density` LP_FIELD_S, the value the player uses when a spec carries none)."""
    m = MOUNT_S.search(str(plate))
    return float(m.group(1)) if m else MOUNT_S_DEFAULT


def _data(g: dict) -> list[int]:
    out: list[int] = []
    for b in g["beats"]:
        out += [i for i in data_of(b) if i not in out]
    return out


# --------------------------------------------------------------------------- what is MEASURED, never filled

def event_gaps(rows: list[tuple]) -> list[tuple]:
    """Every gap over M16's `PULSE_MAX_S` between two events on the emitted rows, as
    `(after_s, gap_s)` - MEASURED for the author to read, never FILLED. A compiler that adds an
    event to close a gap is an allocator (`recipes.py:1-20`; PIPELINE.md:33), and this one is not.
    """
    ts: list[float] = []
    for r in rows:
        ts += [float(r[0]), float(r[1])]        # a row's own boundaries are events: the world arrives, the world leaves
        ts += [float(dk[2]) for dk in (r[4] or [])]
        ts += [float(s["at"]) for s in ((r[6] if len(r) > 6 else None) or [])]
    ts = sorted({round(t, 2) for t in ts})
    return [(a, round(b - a, 2)) for a, b in zip(ts, ts[1:]) if b - a > PULSE_MAX_S]
