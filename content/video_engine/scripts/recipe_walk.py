"""RECIPE WALK - one timeline walk and one co-occurrence matcher, shared (P56 T4).

A recipe is an ORDERED combination of catalogue cards with offsets (E96, 2026-09-13). Two readers need the same
answer to "did these members fire together here?": the drift gate (`effects_catalog_check.py`, on a recipe's
`proof`) and the one-shot floor (`gate_one_shot_floor.py`, on a build's own timeline). Both import this module;
neither re-implements the walk.

    from recipe_walk import events, match, count, option_owner
    evts = events(json.loads(path.read_text(encoding="utf-8")), option_owner(cards))
    fires = match(evts, recipe["members"], recipe.get("window_s", 6.0), t0=recipe["proof"]["t"])

`events(timeline)` turns a compiled `scene_evidence_timeline.v1` into a flat, deterministic stream of `Event`s -
one per CARD the timeline's tokens resolve to, in the order a viewer meets them. The field reads are
`docs/research/runs/p56-recipe-seeds/derive_seeds.py`'s (P56 T2) verbatim, so the two agree:

    scenes[].world (no .kind, no .page) = a plate        -> cls world, card plate_option:world (ref = asset_id)
    scenes[].world.kind == "clip"                        -> cls world, card plate_option:clip (ref = asset_id)
    scenes[].world.ken_burns.scale                       -> cls world, card plate_option:ken (a second event)
    scenes[].world.page.{builder,variant}                -> cls world, card page_builder:<variant> (ref = builder)
    scenes[].world.page.enter                            -> cls page_enter, card page_enter:<enter> (ref = snap_from)
    scenes[].world.page.badges[] / docks[].badge_at[i]   -> cls badge, card dock_option:badge (ref = page | slide)
    scenes[].world.idle / scenes[].species[].idle        -> cls idle, card idle:<kind>
    scenes[].docks[].kind (absent = image)               -> cls dock_enter, card dock_kind:<kind>
    evidence[<slide>].species                            -> cls dock_enter, card dock_payload:<species>
    evidence[<slide>].chart discriminator                -> cls dock_enter, card chart_dock:<form>
    scenes[].docks[].{read_s,park_s}                     -> cls dock_enter, card dock_option:read + option read_s
                                                            and/or park_s (one event per field the dock carries)
    scenes[].docks[].centre                              -> cls dock_enter, card dock_option:centre
    scenes[].docks[].arrive (+ .mass)                    -> cls dock_enter, card dock_option:arrive; cls arrival,
                                                            card arrival:<arrive> + option <mass>
    evidence[<slide>].stack.items[].at / .clear_at       -> cls item / clear, card dock_payload:stack
    evidence[<slide>].chart.checklist.rows[].delay       -> cls row, card chart_dock:checklist
    scenes[].docks[].exit                                -> cls dock_exit, card None (ref = slide)
    scenes[].species[].kind + .at                        -> cls species | page_species, card species:<kind> |
                                                            page_species:<kind>; a `chart_to` adds cls chart_to,
                                                            card chart_to:<to> (the verb)
    scenes[].exit                                        -> cls exit, card exit:<base>, plus the option when the
                                                            timeline's token is a listed OPTION of that card
                                                            (Steel's `wipe_right` is `exit:wipe` + `wipe_right`)
    a world signature change                             -> cls cut, card None

`match(events, members, window_s, t0)` is the co-occurrence matcher: the members must fire IN ORDER, all inside
`window_s` from the first member, each at its own `offset_s` from the first within `OFFSET_TOL` (1.0 s; an
`offset_s` written as a range [lo, hi] widens the band to [lo - tol, hi + tol]). A member marked `optional` may be
absent (its `members_at` entry is None). `t0` pins the fire to one instant (within `ANCHOR_TOL`, 0.05 s) - what a
recipe's `proof` claims. `count` is how many distinct fires the whole timeline holds: the spike's line, a recipe
that fires once is a decoration and a recipe that fires four times is a grammar.

IN ORDER is in TIME order (the P56 review, 2026-09-13). The walk's index order is the SCENE's - a dock that outlives
its scene is clamped to that scene for the sort - so on two overlapping spans the matcher once fired `members_at
[0.0, 10.0, 9.0]`: a ladder climbing backwards. Every member must now fire at or after the previous member's own
instant (ties inside EPS allowed, so the same-instant class order still reads as order).

A member may name another RECIPE (`card: "recipe:<slug>"`): pass `recipes={id: record}` and the child's members are
spliced in where it sits, their offsets ADDED to the member's own `offset_s` (a range adds end to end), so the parent
fires exactly where the flattened list fires. The splice is recursive and stops on a cycle; a member whose recipe is
not in the registry is left alone - no event carries a recipe id, so the chain cannot fire and the drift gate says so.

Every field read is `.get` with the timeline schema's default (`scene_evidence_timeline.schema.json`: a scene's
`exit` defaults to `wipe_left`; a dock with no window is on screen for its whole scene; a species or a stack item
with no instant starts at its scene's start), so a PARTIAL or hand-written timeline walks instead of raising.

Four of those card ids (`dock_option:badge`, `plate_option:{world,clip,ken}`) are the parent's P56 ruling and are
added to the catalogue by a later slice; the walk names them now so the stream never has to be re-walked when they
land. A page's card is its ledger VARIANT (`page_builder:bars`), not `world.page.builder`: the page_builder axis is
inventoried from `ledger_page.VARIANTS` (`effects_catalog_check.SOURCES`), and Japan's bars page carries
`builder: story, variant: bars` - `page_builder:story` is no card, so the builder is the `ref`.

Stdlib only, pure functions, no repo paths, no episode facts.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

EPS = 0.005
ANCHOR_TOL = 0.05            # how near `proof.t` an anchor must fire to be THAT fire
OFFSET_TOL = 1.0             # how far a member may sit from its authored offset (seconds)
DEFAULT_WINDOW_S = 6.0       # the spike's WIN
CHART_FORMS = ("series", "bars", "shares", "checklist", "panels")
CHART_SPECIES = ("chart", "data", "tile", "table")   # an evidence payload that IS a chart surface
DEFAULT_EXIT = "wipe_left"   # scene_evidence_timeline.schema.json: `scene.exit`'s own default

# A species `kind` the catalogue carries on the page_species axis (derive_seeds.py PAGE_SPECIES_KINDS).
PAGE_SPECIES_KINDS = frozenset({"build_to", "chart_to", "retitle", "figure", "note", "bracket",
                                "span", "spread", "peel", "relight", "undraw", "cross",
                                "lit_stretch", "explode", "member"})   # P69 T47: T36's card is page_species:lit_stretch - the walk named it species:

# Same-instant order: what a viewer meets first (derive_seeds.py KIND_RANK, widened for the classes it folded).
CLS_RANK = {"cut": 0, "world": 1, "page_enter": 2, "idle": 3, "dock_enter": 5, "arrival": 6,
            "badge": 7, "species": 8, "page_species": 8, "chart_to": 8, "row": 9, "item": 10, "clear": 11,
            "dock_exit": 12, "exit": 13}
BADGE_CARD = "dock_option:badge"        # a badge has one card whether a dock or a page stamps it (P56, the parent)
PLATE_CARD = "plate_option:world"       # a bare plate world
CLIP_CARD = "plate_option:clip"         # a clip world
KEN_CARD = "plate_option:ken"           # a world that moves under the camera


@dataclass
class Event:
    """One card the timeline performs at one instant. `n` is its position in the walk (assigned after the sort)."""
    t: float
    cls: str
    card: str | None
    option: str | None = None
    scene: str = ""
    ref: str | None = None
    i: int = 0            # the scene's index
    n: int = -1

    def as_dict(self) -> dict:
        return {"t": self.t, "cls": self.cls, "card": self.card, "option": self.option,
                "scene": self.scene, "ref": self.ref, "i": self.i, "n": self.n}


@dataclass
class Fire:
    """One instance of a recipe: the members in order, each at the instant it fired (None = an absent optional)."""
    t: float
    scene: str
    members_at: list[float | None] = field(default_factory=list)
    events: list[Event | None] = field(default_factory=list)

    @property
    def t_end(self) -> float:
        times = [t for t in self.members_at if t is not None]
        return max(times) if times else self.t


# --------------------------------------------------------------------------- the walk

def load_timeline(path: Path | str) -> dict:
    """The compiled timeline as a dict (a convenience: the callers hold the paths)."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def option_owner(cards: Iterable[Mapping[str, Any]]) -> dict[str, str]:
    """{option token -> the card that lists it}, from the cards (or the generated records: both carry `options`)."""
    owner: dict[str, str] = {}
    for card in cards:
        for opt in card.get("options") or []:
            token = opt.get("token") if isinstance(opt, Mapping) else str(opt)
            if token and str(token) not in owner:
                owner[str(token)] = str(card.get("id"))
    return owner


def world_sig(world: Mapping[str, Any]) -> tuple:
    """What makes a scene a NEW composition (derive_seeds.world_sig)."""
    page = world.get("page")
    if page:
        return ("ledger", page.get("title"), page.get("builder"), page.get("variant"))
    if world.get("kind") == "clip":
        return ("clip", world.get("asset_id"))
    return ("plate", world.get("asset_id"))


def chart_form(block: Mapping[str, Any]) -> str | None:
    """The chart's discriminator key in an `evidence[<slide>]` block, or None."""
    chart = block.get("chart")
    if not isinstance(chart, Mapping):
        return None
    return next((form for form in CHART_FORMS if form in chart), None)


def species_card(kind: str) -> str:
    """A species kind resolves on the page_species axis when the catalogue carries it there, else on species."""
    return ("page_species:" if kind in PAGE_SPECIES_KINDS else "species:") + str(kind)


def exit_card(token: Any, options: Mapping[str, str] | None = None) -> tuple[str, str | None]:
    """(card id, option) for a scene `exit` token: `wipe_right` is `exit:wipe`'s OPTION, `suck:0.49,0.55` a timing.

    A scene that states no exit takes the timeline schema's own default (`wipe_left`) - a partial timeline still
    walks."""
    raw = str(DEFAULT_EXIT if token is None else token)
    base = raw.split(":")[0]
    owner = (options or {}).get(base)
    if owner and owner != f"exit:{base}":
        return owner, base
    card = f"exit:{base}"
    rest = raw[len(base) + 1:]
    return card, (rest if rest and (options or {}).get(rest) == card else None)


def dock_cards(dock: Mapping[str, Any], block: Mapping[str, Any]) -> list[tuple[str, str | None]]:
    """Every card a dock's ENTER performs, in the order the walk emits them."""
    kind = str(dock.get("kind", "image"))
    out: list[tuple[str, str | None]] = [(f"dock_kind:{kind}", None)]
    payload = block.get("species")
    if payload:
        out.append((f"dock_payload:{payload}", None))
    form = chart_form(block)
    if form:
        out.append((f"chart_dock:{form}", None))
    for field_name in ("read_s", "park_s"):
        if field_name in dock:
            out.append(("dock_option:read", field_name))
    if dock.get("centre"):
        out.append(("dock_option:centre", None))
    if dock.get("arrive"):
        out.append(("dock_option:arrive", None))
    return out


def _scene_docks(scene: Mapping[str, Any], evidence: Mapping[str, Any], add, i: int, sid: str,
                 span: tuple[float, float] = (0.0, 0.0)) -> None:
    """Every dock of one scene. A dock that states no window is on screen for its whole scene (the schema's read)."""
    for dock in scene.get("docks") or []:
        slide = dock.get("slide")
        block = evidence.get(slide) or {}
        enter = float(span[0] if dock.get("enter") is None else dock["enter"])
        leave = float(span[1] if dock.get("exit") is None else dock["exit"])
        for card, option in dock_cards(dock, block):
            add(enter, "dock_enter", card, option=option, ref=slide, i=i, scene=sid)
        if dock.get("arrive"):
            add(enter, "arrival", f"arrival:{dock['arrive']}", option=dock.get("mass"), ref=slide, i=i, scene=sid)
        for at in dock.get("badge_at") or []:
            add(at, "badge", BADGE_CARD, ref=slide, i=i, scene=sid)
        stack = block.get("stack")
        if isinstance(stack, Mapping):
            for item in stack.get("items") or []:
                if item.get("at") is not None:
                    add(item["at"], "item", "dock_payload:stack", ref=slide, i=i, scene=sid)
            if stack.get("clear_at") is not None:
                add(stack["clear_at"], "clear", "dock_payload:stack", ref=slide, i=i, scene=sid)
        chart = block.get("chart")
        checklist = chart.get("checklist") if isinstance(chart, Mapping) else None
        if isinstance(checklist, Mapping):
            for row in checklist.get("rows") or []:
                if row.get("delay") is not None:
                    add(enter + float(row["delay"]), "row", "chart_dock:checklist", ref=slide, i=i, scene=sid)
        add(leave, "dock_exit", None, ref=slide, i=i, scene=sid)


def events(timeline: Mapping[str, Any], options: Mapping[str, str] | None = None) -> list[Event]:
    """The card stream of one compiled timeline, deterministic: scene order, then the instant (clamped to the
    scene's start - a dock that outlives its scene still belongs to it), then the same-instant class order."""
    evidence = timeline.get("evidence") or {}
    out: list[Event] = []
    starts: list[float] = []
    previous: tuple | None = None

    def add(t, cls, card, option=None, ref=None, i=0, scene="") -> None:
        out.append(Event(t=round(float(t), 3), cls=cls, card=card, option=option, scene=scene,
                         ref=None if ref is None else str(ref), i=i, n=len(out)))

    for i, scene in enumerate(timeline.get("scenes") or []):
        world = scene.get("world") or {}
        sid = str(scene.get("scene_id") or i)
        span = list(scene.get("span") or [0.0, 0.0])
        t0 = float(span[0] if span else 0.0)
        t1 = float(span[1] if len(span) > 1 else t0)
        starts.append(round(t0, 3))
        signature = world_sig(world)
        if signature != previous:
            add(t0, "cut", None, ref=signature[0], i=i, scene=sid)
        previous = signature

        page = world.get("page")
        if page:
            add(t0, "world", f"page_builder:{page.get('variant')}", ref=page.get("builder"), i=i, scene=sid)
            add(t0, "page_enter", f"page_enter:{page.get('enter') or 'mount'}", ref=page.get("snap_from"),
                i=i, scene=sid)
        else:
            add(t0, "world", CLIP_CARD if world.get("kind") == "clip" else PLATE_CARD,
                ref=world.get("asset_id"), i=i, scene=sid)
        if (world.get("ken_burns") or {}).get("scale"):
            add(t0, "world", KEN_CARD, ref=world.get("asset_id"), i=i, scene=sid)
        if world.get("idle"):
            add(t0, "idle", f"idle:{world['idle']}", i=i, scene=sid)
        for badge in page.get("badges") or [] if page else []:
            add(t0, "badge", BADGE_CARD, ref=page.get("title") or page.get("variant"), i=i, scene=sid)

        _scene_docks(scene, evidence, add, i, sid, (t0, t1))

        for sp in scene.get("species") or []:
            kind = str(sp.get("kind"))
            card = species_card(kind)
            cls = "page_species" if card.startswith("page_species:") else "species"
            at = float(t0 if sp.get("at") is None else sp["at"])
            add(at, cls, card, ref=(sp.get("target") or {}).get("kind"), i=i, scene=sid)
            if kind == "chart_to" and sp.get("to"):
                add(at, "chart_to", f"chart_to:{sp['to']}", i=i, scene=sid)
            if sp.get("idle"):
                add(at, "idle", f"idle:{sp['idle']}", i=i, scene=sid)

        card, option = exit_card(scene.get("exit"), options)
        add(t1, "exit", card, option=option, ref=scene.get("exit"), i=i, scene=sid)

    out.sort(key=lambda e: (e.i, max(e.t, starts[e.i]), CLS_RANK.get(e.cls, 99), e.n))
    for n, event in enumerate(out):
        event.n = n
    return out


# --------------------------------------------------------------------------- the matcher

def fits(event: Event, member: Mapping[str, Any]) -> bool:
    """A member names a card and may narrow it to one of that card's options; naming no option matches any."""
    if event.card != member.get("card"):
        return False
    option = member.get("option")
    return option is None or event.option == option


def offset_ends(offset: Any) -> tuple[float, float]:
    """An `offset_s` as (lo, hi): a plain number is a point, a [lo, hi] list is a range."""
    if isinstance(offset, (list, tuple)) and len(offset) == 2:
        return float(offset[0]), float(offset[1])
    value = float(offset or 0.0)
    return value, value


def band(offset: Any, tol: float = OFFSET_TOL) -> tuple[float, float]:
    """The [lo, hi] seconds-from-the-first-member a member may fire in (a range offset widens it both ways)."""
    lo, hi = offset_ends(offset)
    return lo - tol, hi + tol


def shift(offset: Any, by: Any) -> float | list[float]:
    """`offset` moved by `by`, ends added (a range offset adds to both ends) - a spliced member's new offset."""
    lo_a, hi_a = offset_ends(offset)
    lo_b, hi_b = offset_ends(by)
    lo, hi = round(lo_a + lo_b, 6), round(hi_a + hi_b, 6)
    return [lo, hi] if hi > lo else lo


def flatten(members: Sequence[Mapping[str, Any]], recipes: Mapping[str, Mapping[str, Any]] | None = None,
            _trail: tuple[str, ...] = ()) -> list[dict]:
    """The member list with every `recipe:` member replaced by that recipe's own members (offsets added).

    The matcher only ever sees CARDS. A child's offsets are written from the child's own first member, which sits at
    the parent member's `offset_s`, so the two add. An optional parent member makes every spliced member optional.
    A member naming a recipe the registry does not hold - or one already on the trail (a cycle the drift gate's
    `_recipe_cycles` fails) - is left exactly as it is: nothing can match it, so the chain dies instead of hanging.
    """
    out: list[dict] = []
    for member in members:
        card = str(member.get("card") or "")
        child = (recipes or {}).get(card) if card.startswith("recipe:") else None
        if child is None or card in _trail:
            out.append(dict(member))
            continue
        for spliced in flatten(child.get("members") or [], recipes, (*_trail, card)):
            grown = dict(spliced)
            grown["offset_s"] = shift(spliced.get("offset_s"), member.get("offset_s"))
            if member.get("optional"):
                grown["optional"] = True
            out.append(grown)
    return out


def candidates(evts: Sequence[Event], member: Mapping[str, Any], after: int, t0: float,
               window_s: float = DEFAULT_WINDOW_S, tol: float = OFFSET_TOL,
               t_prev: float | None = None) -> list[int]:
    """The indices of every event that could BE this member here - the gate names the member with none.

    `t_prev` is the instant the PREVIOUS member fired: a member never fires before it (the walk's index order is the
    scene's, not the clock's, so index order alone let a fire run backwards - the P56 review)."""
    lo, hi = band(member.get("offset_s"), tol)
    out: list[int] = []
    for j in range(after + 1, len(evts)):
        dt = evts[j].t - t0
        if dt < -EPS or dt > window_s + EPS or dt < lo - EPS or dt > hi + EPS:
            continue
        if t_prev is not None and evts[j].t < float(t_prev) - EPS:
            continue
        if fits(evts[j], member):
            out.append(j)
    return out


def _chain(evts: Sequence[Event], members: Sequence[Mapping[str, Any]], k: int, after: int, t0: float,
           window_s: float, tol: float, t_prev: float) -> list[Event | None] | None:
    """The members from index `k` on, matched after event index `after` AND after the instant `t_prev`; None when one
    of them cannot fire. An absent optional member moves neither the index nor the clock."""
    if k >= len(members):
        return []
    member = members[k]
    for j in candidates(evts, member, after, t0, window_s, tol, t_prev):
        rest = _chain(evts, members, k + 1, j, t0, window_s, tol, evts[j].t)
        if rest is not None:
            return [evts[j], *rest]
    if member.get("optional"):
        rest = _chain(evts, members, k + 1, after, t0, window_s, tol, t_prev)
        if rest is not None:
            return [None, *rest]
    return None


def match(evts: Sequence[Event], members: Sequence[Mapping[str, Any]], window_s: float = DEFAULT_WINDOW_S,
          t0: float | None = None, offset_tol: float = OFFSET_TOL,
          recipes: Mapping[str, Mapping[str, Any]] | None = None) -> list[Fire]:
    """Every fire of an ordered member list: in TIME order, inside `window_s`, each within `offset_tol` of its offset.

    `t0` keeps only the fire whose FIRST member lands there (ANCHOR_TOL) - what a `proof` claims. An `optional`
    member that did not fire holds None in `members_at`. `recipes` is the {id: record} registry a `recipe:` member is
    spliced from (`flatten`). One fire per anchor: `_chain` returns the first chain that satisfies every member, and
    the anchors are distinct events, so no fire can repeat (the P56 review retired a dedupe that never fired)."""
    if not members:
        return []
    flat = flatten(members, recipes)
    fires: list[Fire] = []
    for anchor in evts:
        if not fits(anchor, flat[0]):
            continue
        if t0 is not None and abs(anchor.t - float(t0)) > ANCHOR_TOL:
            continue
        rest = _chain(evts, flat, 1, anchor.n, anchor.t, float(window_s), float(offset_tol), anchor.t)
        if rest is None:
            continue
        chain: list[Event | None] = [anchor, *rest]
        fires.append(Fire(t=anchor.t, scene=anchor.scene,
                          members_at=[None if e is None else e.t for e in chain], events=chain))
    return fires


def count(evts: Sequence[Event], members: Sequence[Mapping[str, Any]], window_s: float = DEFAULT_WINDOW_S,
          offset_tol: float = OFFSET_TOL, recipes: Mapping[str, Mapping[str, Any]] | None = None) -> int:
    """How many times the ordered set fires in the whole timeline (a decoration fires once; a grammar recurs)."""
    return len(match(evts, members, window_s, None, offset_tol, recipes))
