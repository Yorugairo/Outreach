"""EFFECTS CATALOG DRIFT GATE - the cards may not drift from the compiler, the painters or the goldens (P55 T4).

The catalogue (`build_effects_catalog.py`) turns the cards into docs; this gate proves the cards still tell the truth.
Eight checks, each a function returning one message per failure naming the card id or the token:

  1. coverage   - every token the compiler accepts on an inventoried axis is a card's token or a listed option
  2. phantoms   - a card token the compiler does not accept fails unless `planned` + backlog, or `implicit`
  3. anchors    - `lives.path` exists and holds `lives.symbol` (its last dotted part) and every `lives.also`
  4. proof      - `proof.golden` is a pytest golden (SURFACES / FLAG_FRAMES / PROOF_FRAMES) with its PNG;
                  `proof.test` names an existing file and, with `::name`, a `def name` in it
  5. examples   - `author.example` passes the compiler's own validator for `author.check` (ast.literal_eval only)
  6. aliases    - no alias on two cards, no alias equal to another card's title (case and whitespace folded)
  7. phases     - a card whose T1 inventory row had >= 2 phases keeps >= 2 (skipped with a note when the gitignored
                  inventory directory is absent)
  8. when       - species / page_species / chart_to cards carry `when: null`; every token has a *_WHEN entry

P56 T4 adds four RECIPE checks - a recipe is an ordered combination of cards, so it can drift in ways a card cannot:

  9. members    - every member names a card id (or another recipe, acyclic); an `option` is one the card LISTS;
                  fewer than 2 members is not a combination
 10. proof      - a `proven` recipe has a proof, its `timeline` is on disk, and the members really fire in order
                  inside `window_s` at `proof.t` (`recipe_walk.py` re-walks that timeline) with `members_at` agreeing
                  within 0.05 s; the failure names the member that did not fire and the instant
 11. aliases    - a recipe's title and aliases are unique across cards AND recipes, and none is in AMBIGUOUS_NAMES
 12. count      - the authored `count` is the MATCHER's: the proof timeline is re-walked and `recipe_walk.count`
                  must agree (a mismatch names both numbers); a `proven` recipe fired at least once and one that
                  fired exactly once is reported INFO as a decoration

    python content/video_engine/scripts/effects_catalog_check.py [--repo <root>]

Exit 1 on any failure. An example the gate cannot validate without a project is listed as SKIPPED_EXAMPLE, never
passed silently. `build_effects_catalog.py --check` calls `check`, so `build_docs_layers.py` carries the gate.
"""
from __future__ import annotations

import argparse
import ast
import importlib
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
REPO = SCRIPTS.parents[2]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import build_effects_catalog as BEC  # noqa: E402
import recipe_walk as RW  # noqa: E402  (the walk and the matcher live once, there)

ENGINE_REL = "docs/content-video-engine/samples/scene-evidence-engine.mjs"
COMPILER_REL = f"{BEC.SCRIPTS_REL}/{BEC.COMPILER}.py"
GOLDEN_TEST_REL = "content/video_engine/tests/test_golden_frames.py"
FRAMES_REL = "content/video_engine/tests/golden/frames"
KINETICS_REL = "content/video_engine/scripts/kinetics"
INVENTORY_REL = "docs/research/runs/p55-effects-inventory"
MEMBERS_AT_TOL = 0.05          # how far a proof's stated instant may sit from the walk's own
UNANCHORED_FORMS = ("compiler-only", "declared-unbuilt")
PAINTED_FORMS = ("module", "inline")
INVENTORY_AXIS_FOLD = {"camera_move": "species"}   # T3 merged the camera-move rows into the species cards
IDENT_EDGE = r"(?<![A-Za-z0-9_$]){}(?![A-Za-z0-9_$])"


@dataclass(frozen=True)
class Source:
    """One key-set the compiler accepts. `attr` names the tuple/dict (`DOCK_KIND_*` collects the constants); a
    `literal` row has no tuple to read, so each of its tokens must still occur as a word in `probe`."""
    name: str
    module: str                    # "compiler" | "ledger" | "literal" | "kinetics-dir"
    attr: str | None
    axes: tuple[str, ...]
    literal: tuple[str, ...] = ()
    probe: str | None = None


# THE one axis -> tuple table (T1's inventoried axes). `name` is what a card option writes as `source_set`.
SOURCES: tuple[Source, ...] = (
    Source("SPECIES_KINDS", "compiler", "SPECIES_KINDS", ("species", "page_species")),
    Source("PAGE_SPECIES", "compiler", "PAGE_SPECIES", ("page_species",)),
    Source("CHART_TO_KINDS", "compiler", "CHART_TO_KINDS", ("chart_to",)),
    Source("VARIANTS", "ledger", "VARIANTS", ("page_builder",)),
    Source("UNCHARTABLE", "ledger", "UNCHARTABLE", ("page_builder",)),
    Source("DOCK_KINDS", "compiler", "DOCK_KIND_*", ("dock_kind",)),
    Source("EMBED_CARD_PAYLOADS", "compiler", "EMBED_CARD_PAYLOADS", ("dock_payload",)),
    Source("CHART_DOCK_FORMS", "literal", None, ("chart_dock",),
           ("series", "panels", "bars", "log", "checklist", "shares"), ENGINE_REL),
    Source("DOCK_OPTS", "compiler", "DOCK_OPTS", ("dock_option",)),
    Source("SCENE_EXITS", "compiler", "SCENE_EXITS", ("exit",)),
    Source("TIMED_EXITS", "compiler", "TIMED_EXITS", ("exit",)),
    Source("MELT_ENDINGS", "compiler", "MELT_ENDINGS", ("exit",)),
    Source("LEDGER_ENTERS", "compiler", "LEDGER_ENTERS", ("page_enter",)),
    Source("LEDGER_EXITS", "compiler", "LEDGER_EXITS", ("page_exit",)),
    Source("CAMERA_MOVES", "compiler", "CAMERA_MOVES", ("species",)),
    Source("CAMERA_EASES", "compiler", "CAMERA_EASES", ("camera",)),
    Source("CAMERA_ATTENTION", "compiler", "CAMERA_ATTENTION", ("camera",)),
    Source("CAMERA_ROW_KEYS", "literal", None, ("camera",), ("keys",), COMPILER_REL),
    Source("IDLE_KINDS", "compiler", "IDLE_KINDS", ("idle",)),
    Source("ARRIVALS", "compiler", "ARRIVALS", ("arrival",)),
    Source("MASSES", "compiler", "MASSES", ("arrival",)),
    Source("MORPH_SHAPES", "compiler", "MORPH_SHAPES", ("page_enter",)),
    Source("PLATE_OPTS", "compiler", "PLATE_OPTS", ("plate_option",)),
    Source("PLATE_USES", "compiler", "PLATE_USES", ("plate_option",)),
    Source("CAPTION_MODES", "literal", None, ("caption",), ("stage", "anchor"), COMPILER_REL),
    Source("CAPTION_STYLES", "literal", None, ("caption",), ("phrase",), COMPILER_REL),
    Source("CAPTION_ARRIVALS", "compiler", "CAPTION_ARRIVALS", ("caption",)),
    Source("OVERFLOW_MODES", "ledger", "OVERFLOW_MODES", ("overflow",)),
    Source("KINETICS_MODULES", "kinetics-dir", None, ("kinetics",)),
)


@dataclass
class Report:
    failures: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)   # SKIPPED_EXAMPLE: "<card id>: <why>"
    notes: list[str] = field(default_factory=list)
    info: list[str] = field(default_factory=list)      # INFO: true, and not a failure (a decoration)
    recipes: int = 0
    proven: int = 0


# --------------------------------------------------------------------------- inputs

def compiler():
    return importlib.import_module(BEC.COMPILER)


def ledger():
    return importlib.import_module("ledger_page")


def load_recipes(recipes_dir: Path) -> list[dict]:
    """Every recipe file, raw (the schema is the generator's job; this gate must see what the schema cannot)."""
    directory = Path(recipes_dir)
    if not directory.is_dir():
        return []
    return [json.loads(path.read_text(encoding="utf-8")) for path in sorted(directory.glob("*.json"))]


def load_cards(cards_dir: Path) -> list[dict]:
    """Every card from every axis file, raw (the schema is the generator's job; this gate must see duplicates)."""
    cards: list[dict] = []
    for path in sorted(Path(cards_dir).glob("*.json")):
        cards.extend(json.loads(path.read_text(encoding="utf-8"))["cards"])
    return cards


def source_tokens(source: Source, repo: Path = REPO) -> tuple[list[str], list[str]]:
    """(tokens, problems) for one table row, read at call time (so a monkeypatched tuple is seen)."""
    if source.module == "kinetics-dir":
        return sorted(p.stem for p in (Path(repo) / KINETICS_REL).glob("*.mjs")), []
    if source.module == "literal":
        text = (Path(repo) / source.probe).read_text(encoding="utf-8")
        missing = [t for t in source.literal if not re.search(IDENT_EDGE.format(re.escape(t)), text)]
        return list(source.literal), [f"table {source.name}: {t!r} no longer occurs in {source.probe}" for t in missing]
    module = compiler() if source.module == "compiler" else ledger()
    if source.attr.endswith("*"):
        prefix = source.attr[:-1]
        return sorted(str(getattr(module, n)) for n in dir(module) if n.startswith(prefix)), []
    return [str(t) for t in getattr(module, source.attr)], []


def _cards_on(cards: list[dict], axes: tuple[str, ...]) -> set[str]:
    return {c["token"] for c in cards if c["axis"] in axes}


def _options_for(cards: list[dict], source: Source) -> set[str]:
    """Option tokens that answer for this source: its own `source_set`, or an unlabelled option on its axes."""
    found: set[str] = set()
    for card in cards:
        for opt in card.get("options") or []:
            if opt.get("source_set") == source.name or (opt.get("source_set") is None and card["axis"] in source.axes):
                found.add(opt["token"])
    return found


# --------------------------------------------------------------------------- 1. coverage / 2. phantoms

def check_coverage(cards: list[dict], repo: Path = REPO) -> list[str]:
    failures: list[str] = []
    for source in SOURCES:
        tokens, problems = source_tokens(source, repo)
        failures += problems
        known = _cards_on(cards, source.axes) | _options_for(cards, source)
        failures += [f"coverage: {source.name} token {t!r} has no card on {'/'.join(source.axes)} and is no card's "
                     f"option" for t in tokens if t not in known]
    return failures


def check_phantoms(cards: list[dict], repo: Path = REPO) -> list[str]:
    accepted: dict[str, set[str]] = {}
    for source in SOURCES:
        tokens, _ = source_tokens(source, repo)
        for axis in source.axes:
            accepted.setdefault(axis, set()).update(tokens)
    failures: list[str] = []
    for card in cards:
        if card.get("implicit") or card["token"] in accepted.get(card["axis"], set()):
            continue
        if card.get("status") == "planned" and card.get("backlog"):
            continue
        failures.append(f"phantom: {card['id']}: token {card['token']!r} is not accepted by the compiler on "
                        f"{card['axis']} (only `planned` with a backlog row, or `implicit`, may say so)")
    return failures


# --------------------------------------------------------------------------- 3. anchors / 4. proof

def check_anchors(cards: list[dict], repo: Path = REPO) -> list[str]:
    failures: list[str] = []
    for card in cards:
        lives = card["lives"]
        if not lives.get("path"):
            if lives["form"] not in UNANCHORED_FORMS:
                failures.append(f"anchor: {card['id']}: lives.path is null for form {lives['form']!r}")
            continue
        path = Path(repo) / lives["path"]
        if not path.is_file():
            failures.append(f"anchor: {card['id']}: lives.path {lives['path']} does not exist")
            continue
        if not lives.get("symbol") and lives["form"] in PAINTED_FORMS:
            failures.append(f"anchor: {card['id']}: form {lives['form']!r} names no lives.symbol")
        text = path.read_text(encoding="utf-8")
        idents = ([lives["symbol"].split(".")[-1]] if lives.get("symbol") else []) + list(lives.get("also") or [])
        failures += [f"anchor: {card['id']}: {ident!r} not found in {lives['path']}" for ident in idents
                     if not re.search(IDENT_EDGE.format(re.escape(ident)), text)]
    return failures


def golden_names(repo: Path = REPO) -> set[str]:
    """pytest's SURFACES (read with ast - importing the test launches Chromium) + render_baseline's named frames."""
    tree = ast.parse((Path(repo) / GOLDEN_TEST_REL).read_text(encoding="utf-8"))
    surfaces: list[str] = []
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == "SURFACES" for t in node.targets):
            surfaces = list(ast.literal_eval(node.value))
    rb = importlib.import_module("render_baseline")
    return set(surfaces) | set(rb.FLAG_FRAMES) | set(rb.PROOF_FRAMES)


def check_proof(cards: list[dict], repo: Path = REPO, names: set[str] | None = None) -> list[str]:
    names = golden_names(repo) if names is None else names
    failures: list[str] = []
    for card in cards:
        proof = card.get("proof") or {}
        golden = proof.get("golden")
        if golden and golden not in names:
            failures.append(f"proof: {card['id']}: golden {golden!r} is not in pytest SURFACES / FLAG_FRAMES / "
                            f"PROOF_FRAMES (an unchecked golden is no golden, decision 7)")
        elif golden and not (Path(repo) / FRAMES_REL / f"{golden}.png").is_file():
            failures.append(f"proof: {card['id']}: golden {golden!r} has no frame {FRAMES_REL}/{golden}.png")
        if proof.get("test"):
            failures += _test_problems(card["id"], proof["test"], Path(repo))
    return failures


def _test_problems(card_id: str, ref: str, repo: Path) -> list[str]:
    rel, _, name = ref.partition("::")
    path = repo / rel
    if not path.is_file():
        return [f"proof: {card_id}: test file {rel} does not exist"]
    if name and not re.search(rf"^\s*(?:async\s+)?def\s+{re.escape(name)}\s*\(", path.read_text(encoding="utf-8"), re.M):
        return [f"proof: {card_id}: no `def {name}` in {rel}"]
    return []


# --------------------------------------------------------------------------- 5. examples

def _ledger_parts(plate_id: str) -> tuple:
    B = compiler()
    return B.parse_ledger_id(B.split_plate_opts(plate_id)[0])


def _dock_tuple(row) -> dict:
    if not (isinstance(row, tuple) and len(row) in (4, 5) and isinstance(row[0], str)
            and all(isinstance(x, (int, float)) for x in row[1:4]) and row[2] < row[3]):
        raise ValueError(f"not a dock tuple (asset, slot, enter, exit[, opts]): {row!r}")
    return compiler().dock_opts(row[4] if len(row) == 5 else None)


class NeedsContext(Exception):
    """The validator needs a project row the gate cannot build: the example becomes a SKIPPED_EXAMPLE entry."""


def _ex_species(card: dict, value) -> list[str]:
    if not isinstance(value, dict):
        return ["a species example must be one species dict"]
    B = compiler()
    if value.get("dur") == "hold":
        raise NeedsContext("dur 'hold' is resolved against the row's next event inside the build loop")
    key = "to" if card["axis"] == "chart_to" else "kind"
    plate = ("ledger:x:line" if card["axis"] in ("page_species", "chart_to")
             else "vecmap" if value.get("kind") in B.VECMAP_SPECIES else "plate-x")
    errs = list(B.validate_species([value], (0, 0, 0), plate))
    return errs + ([f"{key} {value.get(key)!r} is not the card's token"] if value.get(key) != card["token"] else [])


def _ex_exit(card: dict, value) -> list[str]:
    if isinstance(value, tuple) and len(value) >= 6:
        value = value[5]
    if not isinstance(value, str):
        return ["an exit example is the exit string or a shot row carrying it"]
    name, _ = compiler().parse_exit(value)
    return [] if name.split(":")[0] == card["token"] else [f"exit {value!r} is not the card's token"]


def _ex_enter(card: dict, value) -> list[str]:
    if not isinstance(value, str):
        return ["an enter example is a ledger plate id"]
    enter, exit_ = _ledger_parts(value)[4:6]
    if card.get("implicit"):
        return []
    have = (enter or "").split("=")[0] if card["axis"] == "page_enter" else exit_
    return [] if have == card["token"] else [f"{card['axis']} {have!r} in {value!r} is not the card's token"]


def _ex_dock(card: dict, value) -> list[str]:
    opts = _dock_tuple(value) if isinstance(value, tuple) else compiler().dock_opts(value)
    if card["axis"] == "dock_option" and card["token"] not in opts:
        return [f"dock option {card['token']!r} is not in the example"]
    if card["axis"] == "arrival" and opts.get("arrive", "spring") != card["token"]:
        return [f"arrive {opts.get('arrive')!r} is not the card's token"]
    return []


def _ex_camera(card: dict, value) -> list[str]:
    return list(compiler().validate_camera(value, "plate-x"))


def _ex_chart(card: dict, value) -> list[str]:
    if isinstance(value, tuple):
        _dock_tuple(value)
        return []
    if not isinstance(value, str):
        return ["a chart example is a ledger plate id or a dock tuple"]
    variant = _ledger_parts(value)[1]
    L = ledger()
    if card["token"] not in L.VARIANTS and card["token"] not in L.UNCHARTABLE:
        return [f"{card['token']!r} is neither a ledger VARIANT nor UNCHARTABLE"]
    return [f"variant {variant!r} is not the card's token"] if card["token"] in L.VARIANTS and variant != card["token"] else []


def _ex_plate(card: dict, value) -> list[str]:
    if not isinstance(value, str):
        return ["a plate example is a plate id with its options"]
    _, opts = compiler().split_plate_opts(value)
    if card["axis"] == "idle":
        return [] if opts.get("idle") == card["token"] else [f"idle={card['token']} is not in {value!r}"]
    return [] if card["token"] in opts else [f"{card['token']}= is not in {value!r}"]


def _ex_overflow(card: dict, value) -> list[str]:
    modes = ledger().OVERFLOW_MODES
    mode = value.get("overflow") if isinstance(value, dict) else None
    if mode not in modes:
        return [f"overflow {mode!r} is not one of {'|'.join(modes)}"]
    return [] if mode == card["token"] else [f"overflow {mode!r} is not the card's token"]


EXAMPLE_VALIDATORS = {"species": _ex_species, "exit": _ex_exit, "enter": _ex_enter, "dock": _ex_dock,
                      "dock_option": _ex_dock, "arrival": _ex_dock, "camera": _ex_camera, "chart": _ex_chart,
                      "plate": _ex_plate, "idle": _ex_plate, "overflow": _ex_overflow}
UNVALIDATED = {"caption": "no compiler validator - a build_short.py keyword"}
NOT_EXAMPLES = ("none", "module")


def check_examples(cards: list[dict]) -> tuple[list[str], list[str]]:
    """(failures, SKIPPED_EXAMPLE entries)."""
    failures: list[str] = []
    skipped: list[str] = []
    for card in cards:
        kind, example = card["author"]["check"], card["author"]["example"]
        if kind in NOT_EXAMPLES:
            continue
        if kind in UNVALIDATED:
            skipped.append(f"{card['id']}: {UNVALIDATED[kind]}")
            continue
        if card.get("status") == "planned":
            skipped.append(f"{card['id']}: planned ({', '.join(card.get('backlog') or [])}) - no compiler token yet")
            continue
        try:
            value = ast.literal_eval(example)
        except (ValueError, SyntaxError):
            skipped.append(f"{card['id']}: not a Python literal (a builder expression or a cut fragment) -{example[:60]!r}")
            continue
        try:
            errs = EXAMPLE_VALIDATORS[kind](card, value)
        except NeedsContext as why:
            skipped.append(f"{card['id']}: {why}")
            continue
        except (ValueError, TypeError, KeyError) as exc:
            errs = [str(exc)]
        failures += [f"example: {card['id']}: {e}" for e in errs]
    return failures, skipped


# --------------------------------------------------------------------------- 6. aliases / 7. phases / 8. when

def _fold(name: str) -> str:
    return " ".join(str(name).split()).casefold()


def check_aliases(cards: list[dict]) -> list[str]:
    owners: dict[str, list[str]] = {}
    for card in cards:
        for alias in card.get("aliases") or []:
            ids = owners.setdefault(_fold(alias["name"]), [])
            if card["id"] not in ids:
                ids.append(card["id"])
    titles = {_fold(c["title"]): c["id"] for c in cards}
    failures = [f"alias: {name!r} is on {' and '.join(sorted(ids))}" for name, ids in sorted(owners.items())
                if len(ids) > 1]
    failures += [f"alias: {name!r} on {cid} is the title of {titles[name]}" for name, ids in sorted(owners.items())
                 for cid in ids if name in titles and titles[name] != cid]
    return failures


def check_phases(cards: list[dict], inventory_dir: Path) -> tuple[list[str], list[str]]:
    """(failures, notes)."""
    files = sorted(Path(inventory_dir).glob("inventory-*.jsonl")) if Path(inventory_dir).is_dir() else []
    if not files:
        return [], [f"phases: skipped - no T1 inventory under {inventory_dir} (gitignored)"]
    by_id = {c["id"]: c for c in cards}
    failures: list[str] = []
    for path in files:
        for line in path.read_text(encoding="utf-8").splitlines():
            row = json.loads(line) if line.strip() else {}
            card = by_id.get(f"{INVENTORY_AXIS_FOLD.get(row.get('axis'), row.get('axis'))}:{row.get('token')}")
            had = len(row.get("phases") or [])
            if card and had >= 2 and len(card.get("phases") or []) < 2:
                failures.append(f"phases: {card['id']}: its inventory row carried {had} phases, the card "
                                f"{len(card.get('phases') or [])} (composite effects keep every phase)")
    return failures, []


def check_when(cards: list[dict]) -> list[str]:
    B = compiler()
    failures = [f"when: {c['id']}: carries its own `when` - the {c['axis']} axis pulls it from "
                f"{BEC.PULLED_WHEN[c['axis']]}" for c in cards
                if c["axis"] in BEC.PULLED_WHEN and c.get("when") is not None]
    for kinds, table in (("SPECIES_KINDS", "SPECIES_WHEN"), ("CHART_TO_KINDS", "CHART_TO_WHEN")):
        failures += [f"when: {kinds} token {t!r} has no {table} entry" for t in getattr(B, kinds)
                     if t not in getattr(B, table)]
    return failures


# --------------------------------------------------------------------------- 9-12. the recipes (P56 T4)

def _recipe_cycles(recipes: list[dict]) -> list[str]:
    """A recipe may name another recipe as a member; the graph must be acyclic (the matcher would not terminate)."""
    graph = {r.get("id"): [m.get("card") for m in r.get("members") or []
                           if str(m.get("card") or "").startswith("recipe:")] for r in recipes}
    found: list[str] = []
    state: dict[str, str] = {}

    def visit(node: str, trail: list[str]) -> None:
        if state.get(node) == "done":
            return
        if state.get(node) == "open":
            said = f"recipe: {node}: the recipe graph has a cycle ({' -> '.join([*trail, node])})"
            if said not in found:
                found.append(said)
            return
        state[node] = "open"
        for nxt in graph.get(node, []):
            if nxt in graph:
                visit(nxt, [*trail, node])
        state[node] = "done"

    for rid in sorted(k for k in graph if k):
        visit(rid, [])
    return found


def check_recipe_members(recipes: list[dict], cards: list[dict]) -> list[str]:
    """Every member is a card (with a listed option) or another recipe; a combination has at least two of them.

    The FIRST member is the anchor: every other offset is measured from it, so its own `offset_s` is 0 (or a range
    that opens at 0). A first member written at +0.5 s silently moved every other member (the P56 review)."""
    by_id = {c["id"]: c for c in cards}
    recipe_ids = {r.get("id") for r in recipes}
    failures: list[str] = []
    for recipe in recipes:
        rid = recipe.get("id")
        members = recipe.get("members") or []
        if len(members) < 2:
            failures.append(f"recipe: {rid}: {len(members)} member(s) - a recipe is a COMBINATION (2 or more)")
        if members and abs(RW.offset_ends(members[0].get("offset_s"))[0]) > RW.EPS:
            failures.append(f"recipe: {rid}: member 1 sits at +{members[0].get('offset_s')}s - the first member IS "
                            f"the anchor every other offset is measured from, so its offset is 0")
        for n, member in enumerate(members, 1):
            card_id = member.get("card")
            if card_id in recipe_ids and card_id != rid:
                continue
            card = by_id.get(card_id)
            if card is None:
                failures.append(f"recipe: {rid}: member {n} names {card_id!r} - neither a card id nor a recipe id")
                continue
            option = member.get("option")
            listed = [o["token"] for o in card.get("options") or []]
            if option is not None and option not in listed:
                failures.append(f"recipe: {rid}: member {n} names option {option!r}, which {card_id} does not list "
                                f"({', '.join(listed) if listed else 'it lists none'})")
    return failures + _recipe_cycles(recipes)


def recipe_registry(recipes: list[dict]) -> dict[str, dict]:
    """{id -> record} for every recipe, so a `recipe:` member can be spliced before the walk (`recipe_walk.flatten`)."""
    return {str(r.get("id")): r for r in recipes if r.get("id")}


def _walker(repo: Path, cards: list[dict]):
    """One cached walk per proof timeline: `walk(rel)` is its event stream, or None when the file is not on disk."""
    options = RW.option_owner(cards)
    walks: dict[str, list | None] = {}

    def walk(rel: str) -> list | None:
        if rel not in walks:
            path = Path(repo) / rel
            walks[rel] = RW.events(RW.load_timeline(path), options) if path.is_file() else None
        return walks[rel]

    return walk


def _gap(evts: list, recipe: dict, window_s: float, t0: float, registry: dict | None = None) -> str:
    """Which member did not fire, and where the walk got to - the failure must name it."""
    members = RW.flatten(recipe.get("members") or [], registry)
    anchors = [e for e in evts if RW.fits(e, members[0]) and abs(e.t - float(t0)) <= RW.ANCHOR_TOL]
    if not anchors:
        return f"member 1 ({members[0].get('card')}) does not fire at {t0}"
    after, t_prev = anchors[0].n, anchors[0].t
    for n, member in enumerate(members[1:], 2):
        found = RW.candidates(evts, member, after, anchors[0].t, window_s, RW.OFFSET_TOL, t_prev)
        if found:
            after, t_prev = found[0], evts[found[0]].t
            continue
        if member.get("optional"):
            continue
        return (f"member {n} ({member.get('card')}{' + ' + member['option'] if member.get('option') else ''} "
                f"at +{member.get('offset_s')}s) does not fire inside {window_s:g}s of {t0}")
    return f"the members do not fire in order inside {window_s:g}s of {t0}"


def check_recipe_proof(recipes: list[dict], repo: Path, cards: list[dict], walk=None) -> list[str]:
    """A `proven` recipe's proof is REAL: the timeline is on disk and the matcher finds the members at that instant."""
    walk = walk or _walker(Path(repo), cards)
    registry = recipe_registry(recipes)
    failures: list[str] = []
    for recipe in recipes:
        rid = recipe.get("id")
        proof = recipe.get("proof")
        if recipe.get("status") != "proven":
            if proof:
                failures.append(f"recipe: {rid}: a candidate carries a proof - it is proven, or the proof goes")
            continue
        if not proof:
            failures.append(f"recipe: {rid}: proven with no proof - name the cut and the instant that played it")
            continue
        rel = str(proof.get("timeline") or "")
        evts = walk(rel)
        if evts is None:
            failures.append(f"recipe: {rid}: proof timeline {rel!r} is not on disk")
            continue
        window = float(recipe.get("window_s", RW.DEFAULT_WINDOW_S))
        fires = RW.match(evts, recipe["members"], window, t0=proof.get("t"), recipes=registry)
        if not fires:
            failures.append(f"recipe: {rid}: {_gap(evts, recipe, window, proof.get('t'), registry)} "
                            f"in {rel} (the proof claims it does)")
            continue
        walked, said = fires[0].members_at, list(proof.get("members_at") or [])
        if len(walked) != len(said):
            failures.append(f"recipe: {rid}: proof.members_at has {len(said)} instant(s), the recipe {len(walked)} "
                            f"member(s) - the walk fired at {walked}")
            continue
        drift = [f"member {n}: the walk says {a}, the proof {b}" for n, (a, b) in enumerate(zip(walked, said), 1)
                 if (a is None) != (b is None) or (a is not None and abs(a - b) > MEMBERS_AT_TOL)]
        if drift:
            failures.append(f"recipe: {rid}: proof.members_at disagrees with the walk of {rel} - " + "; ".join(drift))
    return failures


def check_recipe_aliases(cards: list[dict], recipes: list[dict]) -> list[str]:
    """A recipe's title and aliases are its own: no card's, no other recipe's, and never an AMBIGUOUS_NAME."""
    owners: dict[str, list[str]] = {}

    def claim(name: str, owner: str) -> None:
        ids = owners.setdefault(_fold(name), [])
        if owner not in ids:
            ids.append(owner)

    for card in cards:
        claim(card["title"], card["id"])
        for alias in card.get("aliases") or []:
            claim(alias["name"], card["id"])
    failures: list[str] = []
    for recipe in recipes:
        rid = recipe.get("id")
        for name in [recipe.get("title") or ""] + [a["name"] for a in recipe.get("aliases") or []]:
            key = _fold(name)
            if key in BEC.AMBIGUOUS_NAMES:
                failures.append(f"recipe alias: {name!r} on {rid} is in AMBIGUOUS_NAMES (decision 2)")
            held = [o for o in owners.get(key, []) if o != rid]
            if held:
                failures.append(f"recipe alias: {name!r} on {rid} already belongs to {' and '.join(sorted(held))}")
            claim(name, rid)
    return failures


def check_recipe_count(recipes: list[dict], repo: Path | None = None, cards: list[dict] | None = None,
                       walk=None) -> tuple[list[str], list[str]]:
    """(failures, INFO). A proven recipe fired; one that fired ONCE is a decoration - said, not failed (HG2).

    With a `repo` the authored number is not taken on trust: the proof timeline is RE-WALKED and `recipe_walk.count`
    is the one definition of count (the P56 review - the shape check passed a `count` no walk could reproduce). A
    mismatch names both numbers. Without a `repo` only the shape is read (the unit tests' own use)."""
    walk = walk or (_walker(Path(repo), cards or []) if repo is not None else None)
    registry = recipe_registry(recipes)
    failures: list[str] = []
    info: list[str] = []
    for recipe in recipes:
        rid, count = recipe.get("id"), recipe.get("count")
        if recipe.get("status") == "proven":
            walked = _walked_count(recipe, registry, walk)
            if walked is not None and walked != count:
                failures.append(f"recipe: {rid}: count says {count!r}, the walk of "
                                f"{(recipe.get('proof') or {}).get('timeline')} fires it {walked} time(s) - one "
                                f"definition of count: the matcher's")
            if not isinstance(count, int) or count < 1:
                failures.append(f"recipe: {rid}: proven with count {count!r} - a proven recipe fired at least once")
            elif count == 1:
                where = (recipe.get("proof") or {}).get("project") or "its proof cut"
                info.append(f"count: {rid} fired once in {where} - a decoration, not yet a grammar")
        elif count:
            failures.append(f"recipe: {rid}: a candidate that fired {count} time(s) is proven - name its proof")
    return failures, info


def _walked_count(recipe: dict, registry: dict, walk) -> int | None:
    """How many times this recipe fires in its own proof timeline, or None when there is nothing to walk."""
    rel = str((recipe.get("proof") or {}).get("timeline") or "")
    members = recipe.get("members") or []
    if walk is None or not rel or len(members) < 2:
        return None
    evts = walk(rel)
    if evts is None:
        return None
    return RW.count(evts, members, float(recipe.get("window_s", RW.DEFAULT_WINDOW_S)), recipes=registry)


# --------------------------------------------------------------------------- run / CLI

def run(repo: Path = REPO, cards_dir: Path | None = None, inventory_dir: Path | None = None,
        recipes_dir: Path | None = None) -> Report:
    repo = Path(repo)
    cards = load_cards(cards_dir or repo / BEC.CARDS_REL)
    recipes = load_recipes(recipes_dir or repo / BEC.RECIPES_REL)
    report = Report(recipes=len(recipes), proven=sum(1 for r in recipes if r.get("status") == "proven"))
    report.failures += check_coverage(cards, repo) + check_phantoms(cards, repo)
    report.failures += check_anchors(cards, repo) + check_proof(cards, repo)
    failures, report.skipped = check_examples(cards)
    report.failures += failures + check_aliases(cards)
    failures, report.notes = check_phases(cards, inventory_dir or repo / INVENTORY_REL)
    report.failures += failures + check_when(cards)
    walk = _walker(repo, cards)
    report.failures += check_recipe_members(recipes, cards) + check_recipe_proof(recipes, repo, cards, walk)
    report.failures += check_recipe_aliases(cards, recipes)
    failures, report.info = check_recipe_count(recipes, repo, cards, walk)
    report.failures += failures
    return report


def check(repo: Path = REPO, cards_dir: Path | None = None, inventory_dir: Path | None = None,
          recipes_dir: Path | None = None) -> list[str]:
    """One message per failure, each naming the card id, the token or the recipe id. Empty = they tell the truth."""
    return run(repo, cards_dir, inventory_dir, recipes_dir).failures


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--repo", type=Path, default=REPO, help="repository root (default: this checkout)")
    args = ap.parse_args(argv)
    report = run(args.repo.resolve())
    for note in report.notes:
        print(f"effects_catalog_check: note - {note}")
    for entry in report.skipped:
        print(f"effects_catalog_check: SKIPPED_EXAMPLE {entry}")
    for entry in report.info:
        print(f"effects_catalog_check: INFO {entry}")
    for failure in report.failures:
        print(f"effects_catalog_check: FAIL {failure}")
    print(f"effects_catalog_check: {len(report.failures)} failure(s), {len(report.skipped)} example(s) skipped, "
          f"{report.recipes} recipe(s) ({report.proven} proven, {len(report.info)} decoration(s))")
    return 1 if report.failures else 0


if __name__ == "__main__":
    sys.exit(main())
