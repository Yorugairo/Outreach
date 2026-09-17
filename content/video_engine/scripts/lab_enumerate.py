"""THE RECIPE LAB - the enumerator: the combination space as DATA, finite and closed (P65 T2, R26-176).

    python content/video_engine/scripts/lab_enumerate.py --write   # emits content/video_engine/effects/lab/candidates.jsonl
    python content/video_engine/scripts/lab_enumerate.py --check   # exits 1 when the file on disk is stale (the default)

THE RECONCILIATION, and this module's only licence: **the lab ENUMERATES CANDIDATES for the operator's judgement on
a TEST BED; it authors no episode, it fills no slot by count, and nothing it emits reaches a cut except as a `proven`
recipe or a tracked DEFAULT an author may still refuse.** `authoring/recipes.py:1-20` stands verbatim -
"NOT AN ALLOCATOR, and it cannot become one ... this module returns CANDIDATES. It names no episode, chooses
nothing by count, writes no shot table and allocates nothing - the AUTHOR binds" - and so does
`docs/content-video-engine/PIPELINE.md:33` ("Stage 7 is AUTHORED. There is no allocator"). E99 s66: the beat plan
and the script are
INTELLIGENCE work, never a tool's. E99 s68: the combination knowledge is built by presenting BATCHES and tracking
approvals AND denials - which is why this tool has NO `--n`, NO `--fill` and NO sampling. The space is CLOSED: it is
the cross product of a tracked table, and a batch is drawn from it downstream (`lab_batch.py`), never here.

Three truths are PULLED, never typed:

  1. the SHAPES and their member slots - `content/video_engine/effects/lab/beat-shapes.json`, the only place a shape
     or a slot entry is added (that file's own `description` says so and names the ceiling);
  2. the CARDS - `authoring/effects.py` over the generated `docs/EFFECTS-CATALOG.jsonl`, so no candidate can name a
     token the compiler refuses, and an option a card does not list is refused by name;
  3. the CLOCKS - `gate_motion_density.py`'s own: six constants read by name (`CLOCK_CONSTANTS` - M44's plate
     floor, M16's event gap, M12's dock clock, M11's first-light tolerance, the page's build end and `LP_BUILD_S`)
     and two LANDINGS read by calling `_page_land_offset` (`CLOCK_LANDINGS` - the spiral's and the mount's). All
     eight are recorded on every candidate, because a candidate is only ever judged on the clocks it was generated
     against (R26-168: fifteen recipes are `proven` against clocks that no longer exist).

THE LIGHT FOLLOWS THE ENTRY, AS M11 MEASURES IT (P65 T3, the first smoke batch's own finding). A page's chart does
not land at one number, and `gate_motion_density._page_land_offset` (`:1170-1188`) is the ONE place that landing is
defined: axes `LP_BUILD_S` 3.0 s, spiral `LP_SPIRAL_IN_S` 1.6 s, 0.0 for an entry that ARRIVES_BUILT, a mount
`mount_s + PAGE_BUILD_END_S - LP_ROLL_S - LP_SAVOR_S - LP_FIELD_S` (5.9 s at the player's default `mount_s`), and
`PAGE_BUILD_END_S` 7.4 s for anything else. Batch `smoke-r1` lit an `axes`-entered open at 7.4 s (the ROLLED-OUT
page's clock) and M11 read the chart as "full and unannotated", 4.4 s late. So the lab CALLS that function
(`page_land_s`) instead of re-typing its arithmetic - the mount's landing alone is four constants, and the lab and
the gate must not be able to disagree about it. A shape may declare an `entry_slot` and write its offsets against
`entry_landing` (`ENTRY_TOKEN`): a PER-CANDIDATE clock resolved from that candidate's OWN entry member
(`ENTRY_LANDINGS`). The record names the landing it was generated against - `lp_build_s` for an axes entry,
`lp_spiral_in_s` for a spiral, `mount_land_s` for a mount, 0.0 for one that arrives built, `page_build_end_s` for
anything else - which is why `clocks` is EIGHT keys and no longer six (P65 T3c widened the schema).

A candidate that violates its own shape's clocks is REFUSED BY NAME at generation - never silently skipped: the run
prints the candidate, the rule, the slots and the numbers, and writes nothing. A shape whose slot table pushes the
product past `MAX_CANDIDATES` is refused the same way, with its own product printed: a batch the operator cannot
read in one sitting is not a batch.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import re
import sys
from itertools import zip_longest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
REPO = SCRIPTS.parents[2]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import gate_motion_density as G  # noqa: E402  (the clocks are the gate's own constants, read by name)
from authoring import effects as FX  # noqa: E402  (the cards are the generated catalogue's, read through the kit)

SHAPES_REL = "content/video_engine/effects/lab/beat-shapes.json"
CANDIDATES_REL = "content/video_engine/effects/lab/candidates.jsonl"
SCHEMA_REL = "content/video_engine/configs/lab_candidate.schema.json"
BUILD_CMD = "python content/video_engine/scripts/lab_enumerate.py --write"

# THE CEILING (P65 T2). The space is expected in the LOW HUNDREDS: it is read by a human, one batch at a time, and a
# shape whose slot table pushes the product past this is refused by name rather than quietly sampled down - sampling
# is what a lab with no ceiling does instead of admitting its table grew.
MAX_CANDIDATES = 400

STATUS = "enumerated"          # the schema's first state: enumerated -> built -> survivor -> carded -> approved|denied
DIGEST_LEN = 8                 # the id's members-digest, as the schema's pattern demands
TABLE_DIGEST_LEN = 12          # beat-shapes.json's digest, carried in `source`
EPS = 1e-6

# The six clocks that are gate CONSTANTS, each the NAME of one in gate_motion_density.py - never a number here.
CLOCK_CONSTANTS = {
    "m44_plate_s": "PLATE_MIN_S",                 # M44: a world plate the eye can take in
    "m16_gap_s": "SHORT_PULSE_MAX_S",             # M16: the longest gap between visual events on a short
    "m12_dock_s": "OPENING_CHART_HOLD_MAX_S",     # M12 / E25: the chart is the proof, not the homework
    "m11_first_light_s": "ANNOTATE_TOL_S",        # M11 / E24: the species fires within this of the build landing
    "page_build_end_s": "PAGE_BUILD_END_S",       # E99 s67: the second a ROLLED-OUT page finishes BUILDING
    "lp_build_s": "LP_BUILD_S",                   # P65 T3: an `axes` entry's chart lands one BUILD in, not at 7.4
}

# The two clocks that are LANDINGS rather than constants (P65 T3c). `mount_land_s` is arithmetic over four gate
# constants and `lp_spiral_in_s` is a branch of the same function, so both are read by CALLING the gate's own
# `_page_land_offset` - the value recorded is the landing at the player's DEFAULT mount_s (LP_FIELD_S).
CLOCK_LANDINGS = {
    "lp_spiral_in_s": "spiral",   # :1183 - the page UNWINDS from its point over LP_SPIRAL_IN_S (1.6)
    "mount_land_s": "mount",      # :1178-1180 - the soak on the page's own clock, then ink -> punch -> build (5.9)
}
RULES = ("plate_min_s", "after_build_s", "gap_max_s", "dock_hold_max_s")
WINDOW = "window"              # what a rule's `until` says when it means the shape's own window

# THE ENTRY'S OWN LANDING (P65 T3, corrected in T3c). `entry_landing` is not one of the recorded clocks: it is
# resolved per candidate from that candidate's entry member. Each entry names the `enter` the COMPILED scene
# carries into M11, which is what `_page_land_offset` reads - so the landing is always the gate's own number.
ENTRY_TOKEN = "entry_landing"
ENTRY_LANDINGS: dict[str, str] = {
    # :1187-1188 - "the page is there on frame 0 and the DATA is what builds - the chart lands one build later"
    "page_enter:axes": "axes",
    # :1178-1180 - the mount is the SOAK on the page's own clock (R26-50): mount_s + PAGE_BUILD_END_S - ROLL -
    # SAVOR - FIELD, which is 5.9 s at the player's default mount_s and 5.5 s on a page carrying mount_s = 2.0.
    # T3 encoded 7.4 here on the dispatch's word; T3c takes M11's own number, so the thirty mount candidates are
    # no longer generated 1.5 s outside the tolerance they are judged by.
    "page_enter:mount": "mount",
    # :1183 - "the page UNWINDS from its point over LP_SPIRAL_IN_S" (the probe measured it mid-vortex at 0.0)
    "page_enter:spiral": "spiral",
    # :1185-1186 - ARRIVES_BUILT: the page is DRAWN on its first frame, so its chart has already landed
    "page_enter:built": "built",
    # build_scene_timeline_f.stamp_transition_pages:2197-2200 - a ledger page that follows a ledger page and
    # declares no enter "arrives on its axes, whatever the transition" (the hook's page too). The gate never sees
    # the word `stamped`: the compiler has already rewritten it to `axes` by the time M11 measures, so that is the
    # enter this asks the gate about. The `return` shape is planted between two pages (lab_build.SHAPE_BEATS).
    "page_enter:stamped": "axes",
}
# Which RECORDED clock holds that landing, by the enter the gate reads - so a candidate is judged on a clock its
# own record names. `built` lands at 0.0 and needs none; anything else is the ROLLED-OUT page's, which is
# `_page_land_offset`'s own fallback. `shape_clocks` refuses by name if the named clock and the gate ever disagree.
ENTRY_LANDING_CLOCK: dict[str, str | None] = {
    "axes": "lp_build_s",
    "spiral": "lp_spiral_in_s",
    "mount": "mount_land_s",
    "built": None,
}
DEFAULT_LANDING_CLOCK = "page_build_end_s"

_TERM = re.compile(r"^(?:(\d+)\s*\*\s*)?([a-z_][a-z0-9_]*)$")


class LabError(ValueError):
    """The space cannot be enumerated: a card the catalogue does not carry, an option it does not list, an offset
    that is not an expression over the clocks, a candidate that violates its own clocks, or a table past the
    ceiling. Every message names the shape, the slot and the numbers."""


# --------------------------------------------------------------------------- the three sources

def clocks() -> dict[str, float]:
    """The gate's own values, by name - what a candidate is generated and judged against: six constants read by
    name, and the two LANDINGS read by calling `_page_land_offset` (the spiral's, and the mount's at the default)."""
    cl = {name: round(float(getattr(G, const)), 3) for name, const in CLOCK_CONSTANTS.items()}
    cl.update({name: page_land_s(enter) for name, enter in CLOCK_LANDINGS.items()})
    return cl


def page_land_s(enter: str | None, mount_s: float | None = None) -> float:
    """The instant M11 takes as *the build landed* for a page that enters this way - `_page_land_offset`'s own
    answer (`gate_motion_density.py:1170-1188`), CALLED and never re-typed here: it is the one place the landing
    per entry is defined, and a second copy of the mount's four-constant arithmetic is a disagreement waiting."""
    page: dict[str, object] = {"enter": enter}
    if mount_s is not None:
        page["mount_s"] = float(mount_s)
    return round(float(G._page_land_offset({"world": {"page": page}})), 3)


def entry_landing_s(card: str, mount_s: float | None = None) -> float:
    """That instant for this entry CARD - the landing its light follows (P65 T3), the gate's own number."""
    return page_land_s(entry_enter(card), mount_s)


def entry_enter(card: str) -> str:
    """The `enter` the compiled scene carries into M11 for this entry card - refused by name when it is unknown."""
    if card not in ENTRY_LANDINGS:
        raise LabError(f"{card!r} has no landing: M11 measures the first light from "
                       f"gate_motion_density._page_land_offset (:1170-1188), and ENTRY_LANDINGS carries "
                       f"{', '.join(sorted(ENTRY_LANDINGS))} - read the gate and add the entry there")
    return ENTRY_LANDINGS[card]


def entry_clock(card: str) -> str | None:
    """The RECORDED clock that carries this entry's landing, so a candidate is judged on a clock the record names:
    axes -> lp_build_s, spiral -> lp_spiral_in_s, mount -> mount_land_s, built -> None (it lands at 0.0),
    anything else -> page_build_end_s, the rolled-out page's own."""
    return ENTRY_LANDING_CLOCK.get(entry_enter(card), DEFAULT_LANDING_CLOCK)


def entry_slot(shape: dict) -> dict | None:
    """The shape's ENTRY slot (the one `entry_slot` names), or None when the shape has no entry at all."""
    name = shape.get("entry_slot")
    if name is None:
        return None
    slot = next((s for s in shape.get("slots") or [] if s.get("name") == name), None)
    if slot is None:
        raise LabError(f"beat-shapes.json {shape.get('id')}: entry_slot names {name!r}, which is not one of its "
                       f"slots ({', '.join(str(s.get('name')) for s in shape.get('slots') or [])})")
    if slot.get("optional"):
        raise LabError(f"beat-shapes.json {shape.get('id')}: the ENTRY slot {name!r} is never optional - every "
                       f"offset written against {ENTRY_TOKEN} is measured from it")
    return slot


def entry_cards(shape: dict) -> list[str | None]:
    """The entry cards a candidate of this shape can carry - `[None]` when the shape declares no entry slot."""
    slot = entry_slot(shape)
    if slot is None:
        return [None]
    return [str(m["card"]) for m in slot.get("members") or []]


def shape_clocks(shape: dict, cl: dict[str, float], card: str | None) -> dict[str, float]:
    """The clocks ONE candidate is resolved against: the recorded ones, plus its own entry's landing, which is the
    GATE's (`entry_landing_s`). The clock the record names for that entry must hold the same number - when it does
    not, the candidate would be judged on a clock its record does not carry, and that is refused by name."""
    if card is None:
        return dict(cl)
    land, clock = entry_landing_s(card), entry_clock(card)
    named = 0.0 if clock is None else float(cl[clock])
    if abs(named - land) > EPS:
        raise LabError(f"{card!r} lands at {land:.2f}s (gate_motion_density._page_land_offset) but the record would "
                       f"name {clock} = {named:.2f}s - a candidate is only ever judged on the clocks its record "
                       f"carries (R26-168): add the landing to CLOCK_LANDINGS and name it in ENTRY_LANDING_CLOCK")
    return {**cl, ENTRY_TOKEN: land}


def candidate_entry_card(shape: dict, members: list[dict]) -> str | None:
    """The entry card a candidate carries (lab_build reads its window through this), or None."""
    slot = entry_slot(shape)
    if slot is None:
        return None
    known = {str(m["card"]) for m in slot.get("members") or []}
    return next((str(m["card"]) for m in members if str(m["card"]) in known), None)


def load_shapes(path: Path) -> tuple[dict, str]:
    """(the table, its digest). LF-normalised before hashing, so a CRLF checkout enumerates the same space."""
    text = Path(path).read_bytes().decode("utf-8").replace("\r\n", "\n")
    table = json.loads(text)
    if not (table.get("shapes") or []):
        raise LabError(f"{Path(path).name}: the table names no shapes - a shape is a data change in that file")
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:TABLE_DIGEST_LEN]
    return table, digest


def load_cards(repo: Path) -> dict[str, dict]:
    """The generated catalogue's cards by id - the only source a member may be drawn from."""
    return {c["id"]: c for c in FX.load(repo) if not FX.is_recipe(c)}


# --------------------------------------------------------------------------- the offset grammar

def resolve_offset(expr, cl: dict[str, float], where: str) -> float:
    """`0`, `m16_gap_s`, `2 * m16_gap_s`, `page_build_end_s + m16_gap_s` - whole steps of the clocks, nothing else."""
    text = " ".join(str(expr).split())
    tokens = [t for t in re.split(r"\s*([+-])\s*", text) if t.strip() != ""]
    if not tokens:
        raise LabError(f"{where}: an empty offset expression")
    total, sign, want_term = 0.0, 1.0, True
    for token in tokens:
        if token in "+-":
            if want_term:
                raise LabError(f"{where}: {expr!r} is not an offset - a sign with no term after it")
            sign, want_term = (1.0 if token == "+" else -1.0), True
            continue
        if not want_term:
            raise LabError(f"{where}: {expr!r} is not an offset - two terms with no sign between them")
        total += sign * _term(token, cl, where, expr)
        want_term = False
    if want_term:
        raise LabError(f"{where}: {expr!r} is not an offset - it ends on a sign")
    return round(total, 3)


def _term(token: str, cl: dict[str, float], where: str, expr) -> float:
    match = _TERM.match(token)
    if match:
        name = match.group(2)
        if name not in cl:
            raise LabError(f"{where}: {expr!r} names {name!r}, which is not one of the clocks "
                           f"({', '.join(sorted(cl))}) - the clocks come from gate_motion_density.py, never from here")
        return int(match.group(1) or 1) * cl[name]
    try:
        return float(token)
    except ValueError:
        raise LabError(f"{where}: {expr!r} is not an offset expression - a term is a number, a clock name, "
                       f"or <int> * <clock name>") from None


# --------------------------------------------------------------------------- the slot table

def slot_choices(shape: dict, slot: dict, cards: dict[str, dict], cl: dict[str, float],
                 only: str | None = None) -> list[dict | None]:
    """Every member this slot can carry (a card x its offsets), plus None when the slot is optional.

    Each entry is resolved against the CATALOGUE here, at generation: an id it does not carry, an axis the slot does
    not accept and an option the card does not list are each refused by name. `only` is the ENTRY slot's own card:
    a shape's table is built once PER ENTRY, because every `entry_landing` offset is measured from that member."""
    where = f"beat-shapes.json {shape['id']}/{slot.get('name')}"
    axes = tuple(slot.get("axes") or ())
    if not axes:
        raise LabError(f"{where}: the slot names no axes")
    role = str(slot.get("role") or "").strip()
    if not role:
        raise LabError(f"{where}: the slot carries no role - a member says what it DOES in the combination")
    offsets = slot.get("offsets_s")
    if not isinstance(offsets, list) or not offsets:
        raise LabError(f"{where}: `offsets_s` must be a non-empty list of offset expressions")
    choices: list[dict | None] = []
    for entry in slot.get("members") or []:
        card_id = entry.get("card")
        if only is not None and card_id != only:
            continue
        card = cards.get(card_id)
        if card is None:
            raise LabError(f"{where}: {card_id!r} is not a card in {FX.CATALOG_REL} - a member is drawn from the "
                           f"catalogue, so no candidate can name a token the compiler refuses")
        if card.get("axis") not in axes:
            raise LabError(f"{where}: {card_id} is on axis {card.get('axis')!r} and the slot accepts "
                           f"{', '.join(axes)}")
        option = entry.get("option")
        if option is not None:
            tokens = [str(o.get("token")) for o in (card.get("options") or [])]
            if option not in tokens:
                raise LabError(f"{where}: {card_id} does not list the option {option!r} "
                               f"(it lists {', '.join(tokens) if tokens else 'none'})")
        for expr in offsets:
            member = {"card": card_id, "offset_s": resolve_offset(expr, cl, where), "role": role}
            if option is not None:
                member["option"] = option
            choices.append(member)
    if not choices:
        raise LabError(f"{where}: the slot lists no members")
    if slot.get("optional"):
        choices.append(None)
    return choices


def slot_table(shape: dict, cards: dict[str, dict], cl: dict[str, float],
               entry_card: str | None = None) -> list[tuple[str, list[dict | None]]]:
    """(slot name, its choices) in table order - the shape's cross product for ONE entry, and nothing else."""
    slots = shape.get("slots") or []
    if not slots:
        raise LabError(f"beat-shapes.json {shape['id']}: the shape carries no slots")
    names = [str(s.get("name") or "") for s in slots]
    if len(set(names)) != len(names) or "" in names:
        raise LabError(f"beat-shapes.json {shape['id']}: every slot needs its own name ({', '.join(names)})")
    entry_name = (entry_slot(shape) or {}).get("name") if entry_card else None
    return [(str(s["name"]),
             slot_choices(shape, s, cards, cl, only=entry_card if s["name"] == entry_name else None))
            for s in slots]


def shape_count(shape: dict, cards: dict[str, dict], cl: dict[str, float]) -> tuple[int, str]:
    """(the shape's whole product, summed over its entries; the slot counts as text) - the ceiling's own number."""
    total, said = 0, []
    for card in entry_cards(shape):
        table = slot_table(shape, cards, shape_clocks(shape, cl, card), entry_card=card)
        total += math.prod(len(choices) for _, choices in table)
        said.append(product_text(table) + (f" [{str(card).split(':')[-1]}]" if card else ""))
    return total, "; ".join(said)


def product_text(table: list[tuple[str, list]]) -> str:
    return " x ".join(f"{name}={len(choices)}" for name, choices in table)


# --------------------------------------------------------------------------- the clocks that bind a shape

def _instant(name, placed: dict[str, dict | None], window: float, shape_id: str, rule: dict) -> float | None:
    """A rule's `until` / `after`: the shape's window, or a slot's offset (None when an optional slot is absent)."""
    if name == WINDOW:
        return window
    if name not in placed:
        raise LabError(f"beat-shapes.json {shape_id}: rule {rule.get('rule')!r} names the slot {name!r}, "
                       f"which the shape does not have ({', '.join(placed)})")
    member = placed[name]
    return None if member is None else float(member["offset_s"])


def clock_refusals(shape: dict, placed: dict[str, dict | None], cl: dict[str, float], cid: str) -> list[str]:
    """Every way this candidate breaks its own shape's clocks, each named with its numbers. Empty = it obeys them."""
    shape_id = shape["id"]
    where = f"beat-shapes.json {shape_id}"
    window = resolve_offset(shape.get("window_s", "0"), cl, where)
    events = sorted(float(m["offset_s"]) for m in placed.values() if m)
    said = "/".join(f"{name}={m['card']}" + (f":{m['option']}" if m and m.get("option") else "")
                    for name, m in placed.items() if m)
    head = f"{cid} ({said})"
    out: list[str] = []
    for rule in shape.get("clocks") or []:
        kind = rule.get("rule")
        if kind not in RULES:
            raise LabError(f"{where}: unknown clock rule {kind!r} - the rules are {', '.join(RULES)}")
        clock = rule.get("clock")
        if clock not in cl:
            raise LabError(f"{where}: rule {kind!r} names the clock {clock!r}, which is not one of "
                           f"{', '.join(sorted(cl))}"
                           + (f" - {ENTRY_TOKEN} is a clock only in a shape that declares an `entry_slot`"
                              if clock == ENTRY_TOKEN else ""))
        value = cl[clock]
        if kind in ("plate_min_s", "dock_hold_max_s"):
            start = _instant(rule.get("slot"), placed, window, shape_id, rule)
            end = _instant(rule.get("until", WINDOW), placed, window, shape_id, rule)
            if start is None or end is None:
                continue
            held = round(end - start, 3)
            if kind == "plate_min_s" and held < value - EPS:
                out.append(f"{head}: {rule.get('slot')} holds {held:.2f}s (to {rule.get('until')}), under M44's "
                           f"{clock} = {value:.2f}s - a plate the eye cannot take in")
            if kind == "dock_hold_max_s" and held > value + EPS:
                out.append(f"{head}: {rule.get('slot')} is held {held:.2f}s (to {rule.get('until')}), past M12's "
                           f"{clock} = {value:.2f}s - the chart is the proof, not the homework")
        elif kind == "after_build_s":
            light = _instant(rule.get("slot"), placed, window, shape_id, rule)
            page = _instant(rule.get("after"), placed, window, shape_id, rule)
            if light is None or page is None:
                continue
            tolerance = rule.get("tolerance")
            if tolerance is not None and tolerance not in cl:
                raise LabError(f"{where}: rule {kind!r} names the tolerance {tolerance!r}, which is not a clock")
            after = round(light - page, 3)
            slack = cl[tolerance] if tolerance else 0.0
            if after < value - EPS:
                out.append(f"{head}: {rule.get('slot')} lands {after:.2f}s after {rule.get('after')}, BEFORE the "
                           f"page has built ({clock} = {value:.2f}s) - the light lands after the build, never on "
                           f"arrival and never over it (E99 s67)")
            elif after > value + slack + EPS:
                out.append(f"{head}: {rule.get('slot')} lands {after:.2f}s after {rule.get('after')}, outside M11's "
                           f"{value:.2f}s + {slack:.2f}s window on the build's landing")
        elif kind == "gap_max_s":
            points = list(events)
            start = rule.get("from")
            if start is not None:
                t0 = resolve_offset(start, cl, where)
                points = sorted([t for t in events if t >= t0 - EPS] + [t0])
            for a, b in zip(points, points[1:]):
                if b - a > value + EPS:
                    out.append(f"{head}: {b - a:.2f}s of screen with no event ({a:.2f}s -> {b:.2f}s), past M16's "
                               f"{clock} = {value:.2f}s - the pulse is a floor on motion")
                    break
    return out


# --------------------------------------------------------------------------- the candidates

def member_digest(members: list[dict]) -> str:
    """The first 8 hex of the sha256 of the SORTED member tuple (card, option, offset) - the role is prose and is
    not part of a combination's identity, so rewording a slot never moves an id."""
    tup = sorted(f"{m['card']}|{m.get('option', '')}|{float(m['offset_s']):.3f}" for m in members)
    return hashlib.sha256(";".join(tup).encode("utf-8")).hexdigest()[:DIGEST_LEN]


def shape_candidates(shape: dict, cards: dict[str, dict], cl: dict[str, float], table_digest: str,
                     ) -> tuple[list[dict], list[str]]:
    """(the shape's candidates, the clock refusals they earned) - one cross product PER ENTRY, because a shape with
    an `entry_slot` places its light, its hold and its leave against that entry's own build landing (P65 T3)."""
    records, refusals = [], []
    for entry_card in entry_cards(shape):
        cl_c = shape_clocks(shape, cl, entry_card)
        table = slot_table(shape, cards, cl_c, entry_card=entry_card)
        names = [name for name, _ in table]
        for combination in itertools.product(*[choices for _, choices in table]):
            placed = dict(zip(names, combination))
            seated = [(i, dict(m)) for i, m in enumerate(combination) if m]  # the slot's order, then its offset
            members = [m for _, m in sorted(seated, key=lambda seat: (float(seat[1]["offset_s"]), seat[0]))]
            cid = f"lab:{shape['id']}:{member_digest(members)}"
            bad = clock_refusals(shape, placed, cl_c, cid)
            if bad:
                refusals += bad
                continue
            records.append({
                "id": cid,
                "shape": shape["id"],
                "members": members,
                "clocks": dict(cl),
                "status": STATUS,
                "source": f"lab_enumerate beat-shapes.json {table_digest} {shape['id']}",
            })
    return records, refusals


def validate(records: list[dict], repo: Path) -> None:
    """Every emitted record against `lab_candidates.v1` - the boundary, checked before anything is written."""
    import jsonschema

    schema = json.loads((Path(repo) / SCHEMA_REL).read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    for record in records:
        errors = sorted(validator.iter_errors(record), key=lambda e: [str(p) for p in e.absolute_path])
        if errors:
            where = "/".join(str(p) for p in errors[0].absolute_path) or "(record)"
            raise LabError(f"{record.get('id')}: {where}: {errors[0].message[:200]} - it is not a "
                           f"{schema.get('$id')} record")


def build(repo: Path | str = REPO, shapes: Path | str | None = None) -> list[dict]:
    """The whole space, sorted by id. Raises LabError naming every refusal rather than writing a thinned space."""
    repo = Path(repo)
    table, table_digest = load_shapes(Path(shapes) if shapes else repo / SHAPES_REL)
    cl = clocks()
    cards = load_cards(repo)
    records: list[dict] = []
    refusals: list[str] = []
    total = 0
    for shape in table["shapes"]:
        if not re.fullmatch(r"[a-z0-9-]+", str(shape.get("id") or "")):
            raise LabError(f"beat-shapes.json: {shape.get('id')!r} is not a shape slug ([a-z0-9-]+) - the "
                           f"candidate id is lab:<shape>:<digest>")
        count, said = shape_count(shape, cards, cl)
        if total + count > MAX_CANDIDATES:
            raise LabError(f"{shape['id']} pushes the space past MAX_CANDIDATES ({MAX_CANDIDATES}): that shape "
                           f"alone is {count} ({said}), {total + count} in all - shrink its slot "
                           f"table to the members the shape can actually carry, or raise the ceiling on purpose "
                           f"(a batch the operator cannot read in one sitting is not a batch)")
        total += count
        rows, bad = shape_candidates(shape, cards, cl, table_digest)
        refusals += bad
        records += rows
    if refusals:
        raise LabError(f"{len(refusals)} candidate(s) violate their own shape's clocks and are refused by name "
                       f"(fix beat-shapes.json - the table is wrong, not the gates):\n  - " + "\n  - ".join(refusals))
    ids = [r["id"] for r in records]
    if len(set(ids)) != len(ids):
        dupes = sorted({i for i in ids if ids.count(i) > 1})
        raise LabError(f"two candidates share an id: {', '.join(dupes[:6])} - a member digest collided or a slot "
                       f"table lists the same member twice")
    records.sort(key=lambda r: r["id"])
    validate(records, repo)
    return records


# --------------------------------------------------------------------------- the artifact

def render(records: list[dict]) -> str:
    """One record per line, sorted keys, LF, a trailing newline - byte-identical on a re-run."""
    return "".join(json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n" for r in records)


def write(repo: Path | str = REPO) -> list[dict]:
    records = build(repo)
    path = Path(repo) / CANDIDATES_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(render(records).encode("utf-8"))
    return records


def check(repo: Path | str = REPO) -> str | None:
    """None when the file on disk IS a fresh enumeration; otherwise the first differing line, named."""
    want = render(build(repo))
    path = Path(repo) / CANDIDATES_REL
    if not path.is_file():
        return f"{CANDIDATES_REL} is missing - run {BUILD_CMD}"
    have = path.read_bytes().decode("utf-8")
    if have == want:
        return None
    mine, fresh = have.splitlines(), want.splitlines()
    for n, (a, b) in enumerate(zip_longest(mine, fresh, fillvalue=""), start=1):
        if a != b:
            return (f"{CANDIDATES_REL} is stale at line {n} ({len(mine)} record(s) on disk, {len(fresh)} fresh)\n"
                    f"  on disk: {a if a else '(no line)'}\n"
                    f"  fresh:   {b if b else '(no line)'}\n"
                    f"  run {BUILD_CMD}")
    return f"{CANDIDATES_REL} differs only in its line endings - run {BUILD_CMD}"


def summary(records: list[dict]) -> str:
    per: dict[str, int] = {}
    for record in records:
        per[record["shape"]] = per.get(record["shape"], 0) + 1
    said = ", ".join(f"{shape} {n}" for shape, n in sorted(per.items()))
    return f"{len(records)} candidates over {len(per)} shapes (ceiling {MAX_CANDIDATES}): {said}"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--write", action="store_true", help="emit candidates.jsonl from the beat-shapes table")
    ap.add_argument("--check", action="store_true", help="exit 1 when candidates.jsonl is stale (the default)")
    ap.add_argument("--repo", type=Path, default=REPO, help="repository root (default: this checkout)")
    args = ap.parse_args(argv)
    root = args.repo.resolve()
    try:
        if args.write:
            print(f"lab_enumerate: wrote {CANDIDATES_REL} - {summary(write(root))}")
        stale = check(root)
    except LabError as exc:
        print(f"lab_enumerate: REFUSED - {exc}")
        return 1
    if stale:
        print(f"lab_enumerate: STALE - {stale}")
        return 1
    if not args.write:
        print(f"lab_enumerate: in sync ({summary(build(root))})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
