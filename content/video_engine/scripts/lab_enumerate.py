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
  3. the CLOCKS - `gate_motion_density.py`'s own constants (`CLOCK_CONSTANTS` below): M44's plate floor, M16's event
     gap, M12's dock clock, M11's first-light tolerance and the page's build end. They are recorded on every
     candidate, because a candidate is only ever judged on the clocks it was generated against (R26-168: fifteen
     recipes are `proven` against clocks that no longer exist).

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

# The five clocks, each the NAME of a constant in gate_motion_density.py - never a number written here.
CLOCK_CONSTANTS = {
    "m44_plate_s": "PLATE_MIN_S",                 # M44: a world plate the eye can take in
    "m16_gap_s": "SHORT_PULSE_MAX_S",             # M16: the longest gap between visual events on a short
    "m12_dock_s": "OPENING_CHART_HOLD_MAX_S",     # M12 / E25: the chart is the proof, not the homework
    "m11_first_light_s": "ANNOTATE_TOL_S",        # M11 / E24: the species fires within this of the build landing
    "page_build_end_s": "PAGE_BUILD_END_S",       # E99 s67: the second the page finishes BUILDING and holds built
}
RULES = ("plate_min_s", "after_build_s", "gap_max_s", "dock_hold_max_s")
WINDOW = "window"              # what a rule's `until` says when it means the shape's own window

_TERM = re.compile(r"^(?:(\d+)\s*\*\s*)?([a-z_][a-z0-9_]*)$")


class LabError(ValueError):
    """The space cannot be enumerated: a card the catalogue does not carry, an option it does not list, an offset
    that is not an expression over the clocks, a candidate that violates its own clocks, or a table past the
    ceiling. Every message names the shape, the slot and the numbers."""


# --------------------------------------------------------------------------- the three sources

def clocks() -> dict[str, float]:
    """The five gate constants, by name - the value a candidate is generated and judged against."""
    return {name: round(float(getattr(G, const)), 3) for name, const in CLOCK_CONSTANTS.items()}


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

def slot_choices(shape: dict, slot: dict, cards: dict[str, dict], cl: dict[str, float]) -> list[dict | None]:
    """Every member this slot can carry (a card x its offsets), plus None when the slot is optional.

    Each entry is resolved against the CATALOGUE here, at generation: an id it does not carry, an axis the slot does
    not accept and an option the card does not list are each refused by name."""
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


def slot_table(shape: dict, cards: dict[str, dict], cl: dict[str, float]) -> list[tuple[str, list[dict | None]]]:
    """(slot name, its choices) in table order - the shape's own cross product, and nothing else."""
    slots = shape.get("slots") or []
    if not slots:
        raise LabError(f"beat-shapes.json {shape['id']}: the shape carries no slots")
    names = [str(s.get("name") or "") for s in slots]
    if len(set(names)) != len(names) or "" in names:
        raise LabError(f"beat-shapes.json {shape['id']}: every slot needs its own name ({', '.join(names)})")
    return [(str(s["name"]), slot_choices(shape, s, cards, cl)) for s in slots]


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
                           f"{', '.join(sorted(cl))}")
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
                     ) -> tuple[list[dict], list[str], list[tuple[str, list]]]:
    """(the shape's candidates, the clock refusals they earned, its slot table)."""
    table = slot_table(shape, cards, cl)
    names = [name for name, _ in table]
    records, refusals = [], []
    for combination in itertools.product(*[choices for _, choices in table]):
        placed = dict(zip(names, combination))
        seated = [(i, dict(m)) for i, m in enumerate(combination) if m]      # the slot's own order, then its offset
        members = [m for _, m in sorted(seated, key=lambda seat: (float(seat[1]["offset_s"]), seat[0]))]
        cid = f"lab:{shape['id']}:{member_digest(members)}"
        bad = clock_refusals(shape, placed, cl, cid)
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
    return records, refusals, table


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
        slots = slot_table(shape, cards, cl)
        count = math.prod(len(choices) for _, choices in slots)
        if total + count > MAX_CANDIDATES:
            raise LabError(f"{shape['id']} pushes the space past MAX_CANDIDATES ({MAX_CANDIDATES}): that shape "
                           f"alone is {count} ({product_text(slots)}), {total + count} in all - shrink its slot "
                           f"table to the members the shape can actually carry, or raise the ceiling on purpose "
                           f"(a batch the operator cannot read in one sitting is not a batch)")
        total += count
        rows, bad, _ = shape_candidates(shape, cards, cl, table_digest)
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
