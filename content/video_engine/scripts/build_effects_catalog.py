"""EFFECTS CATALOG - every effect the scene-evidence engine performs, one card each, generated (P55 T3).

The operator, 2026-09-13: "how would a different agent know what to call the evidence wall, what it does, etc? is it
a component or does it live as logic only?" The answer lives as DATA, one JSON file per axis under
`content/video_engine/effects/cards/` (schema `content/video_engine/configs/effect_card.schema.json`), and this tool
joins those cards to the truths they must never copy:

  1. `when` on the species / page_species / chart_to axes is PULLED from the compiler's `SPECIES_WHEN` /
     `CHART_TO_WHEN` (`build_scene_timeline_f.py`, imported read-only); a card on those axes carries `when: null`.
  2. `dials: {module, object}` names a frozen object in a `.mjs` module; its keys and literal values are READ from the
     source at build (the object parser of `build_animation_registry.py`), never written on the card; a module that
     does not exist or an object it does not declare is an error naming the card.
  3. `doctrine` cites (`29 s9.24`, `E88`, `CAPABILITIES verdict stack`, `BACKLOG R26-82`) resolve through
     `docs/DOCS-INDEX.jsonl` to a path:line (the gates-registry forms, plus the named docs below); a BACKLOG row id
     or a ruling id is found in the document's own text (`| **R26-30** |`, `## E88`); an unresolved cite keeps a null
     path rather than disappearing, and is never pointed at the document's first line.

    python content/video_engine/scripts/build_effects_catalog.py [--write | --check] [--repo <root>]

P56 T4: the same generator carries the RECIPES (`content/video_engine/effects/recipes/*.json`, schema
`content/video_engine/configs/effect_recipe.schema.json`) - a recipe is an ORDERED combination of cards with
offsets, the act it serves and the played instant that proves it (E96). Each becomes a record with
`axis: "recipe"`, LAST in `AXIS_ORDER`, and each member's `title` is PULLED from the card it names - a recipe
file never copies it. Whether the members really fire together at that instant is the drift gate's job
(`effects_catalog_check.py`, over `recipe_walk.py`'s walk of the timeline on disk).

`--write` regenerates `docs/EFFECTS-CATALOG.jsonl` (the layer `docs_find.py` searches first: id, title, aliases,
does, token) and `docs/EFFECTS-CATALOG.md`; `--check` (the default) exits 1 naming the stale artifact. Deterministic:
cards sorted by id, keys sorted, LF, no timestamps. Every card file is validated against the schema; a duplicate id
or an alias two cards share is an error, not a silent pick - a name that means several things lives in
`AMBIGUOUS_NAMES` and is an alias of none (P55 decision 2).
"""
from __future__ import annotations

import argparse
import difflib
import hashlib
import importlib
import importlib.util
import json
import re
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
REPO = SCRIPTS.parents[2]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import build_gates_registry as BGR  # noqa: E402  (the cite forms and their resolution are defined once, there)

CARDS_REL = "content/video_engine/effects/cards"
RECIPES_REL = "content/video_engine/effects/recipes"
SCHEMA_REL = "content/video_engine/configs/effect_card.schema.json"
RECIPE_SCHEMA_REL = "content/video_engine/configs/effect_recipe.schema.json"
SCRIPTS_REL = "content/video_engine/scripts"
JSONL_REL = "docs/EFFECTS-CATALOG.jsonl"
MD_REL = "docs/EFFECTS-CATALOG.md"
BUILD_CMD = "python content/video_engine/scripts/build_effects_catalog.py --write"
COMPILER = "build_scene_timeline_f"
PULLED_WHEN = {"species": "SPECIES_WHEN", "page_species": "SPECIES_WHEN", "chart_to": "CHART_TO_WHEN"}
AXIS_ORDER = ("species", "page_species", "chart_to", "page_builder", "overflow", "dock_kind", "dock_payload",
              "chart_dock", "dock_option", "plate_option", "idle", "arrival", "camera", "exit", "page_enter",
              "page_exit", "caption", "kinetics", "recipe")
STATUS_ORDER = ("live", "wired", "draft", "declared", "planned", "retired")
RECIPE_AXIS = "recipe"                      # P56: a combination, not an effect - the LAST axis
RECIPE_STATUS_ORDER = ("proven", "candidate")
DEFAULT_WINDOW_S = 6.0                      # effect_recipe.schema.json `window_s` default (the spike's WIN)

# A cite that names a document rather than a numbered section: the rest of the cite is matched against that
# document's headings (case-insensitive, contained); a row / ruling id is found in the document's text; else
# the cite is unresolved (P55 review #5: the first-heading fallback counted 23 unmatched cites as resolved).
NAMED_DOCS = {
    "CAPABILITIES": "docs/content-video-engine/CAPABILITIES.md",
    "BACKLOG": "docs/content-video-engine/BACKLOG.md",
    "SPECIES-BY-SENTENCE": "docs/content-video-engine/SPECIES-BY-SENTENCE.md",
    "MOTION-GRAMMAR": "docs/portable/MOTION-GRAMMAR.md",
    "SHORT-FORM-SHAPE": "docs/content-video-engine/patterns/SHORT-FORM-SHAPE.md",
    "TRANSITIONS-REVIEW": "docs/content-video-engine/TRANSITIONS-REVIEW-2026-09-06.md",
    "CHECK-RESPONSIBILITIES": "docs/content-video-engine/patterns/CHECK-RESPONSIBILITIES.md",
}
BACKLOG_ROW = re.compile(r"^R\d{2}-\d+$")
RULING_ID = re.compile(r"^E\d+$")
MEMORY_REL = "docs/agent-memory/operator/%s.md"

# P55 decision 2: a name that means several things is an alias of NONE. Each entry: the name -> the cards whose
# records used it (empty when doctrine named it ambiguous before any card claimed it). The Markdown lists, beside
# them, every card whose token or title contains the name - what `effects_card.py` prints for it.
AMBIGUOUS_NAMES: dict[str, tuple[str, ...]] = {
    "push": (), "peel": (), "mount": (), "vortex": (), "hold": (), "snap": (),
    "push hand-off": ("dock_option:stack", "species:push"),
    "still life": ("species:steam", "species:ticker"),
    "the vector map world": ("species:arc", "species:light", "species:stamp"),
    "build-on: the page performs on a word": ("page_species:bracket", "page_species:build_to",
                                              "page_species:relight", "page_species:retitle"),
    "the treemap page with x marks": ("page_builder:treemap", "page_species:cross"),
    "the breakthrough bars - two mechanics": ("overflow:burst", "overflow:stack"),
    "the idle, wired": ("idle:breath", "idle:drift", "idle:figure", "idle:live", "idle:none", "idle:pulse",
                        "kinetics:idle", "plate_option:idle"),
    "nothing ever goes truly still": ("idle:breath", "idle:drift", "idle:figure", "idle:live", "idle:pulse"),
    "stop-action mechanics: throw and land with weight": ("arrival:land", "arrival:throw", "kinetics:stopaction"),
}


class CatalogError(ValueError):
    """The cards cannot be built into a catalogue: a schema violation, a duplicate id, a shared alias or a missing
    dials module / object."""


# --------------------------------------------------------------------------- inputs

def load_cards(repo: Path) -> list[dict]:
    """Every card from every axis file, schema-validated, sorted by id."""
    import jsonschema

    schema = json.loads((repo / SCHEMA_REL).read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    cards: list[dict] = []
    for path in sorted((repo / CARDS_REL).glob("*.json")):
        doc = json.loads(path.read_text(encoding="utf-8"))
        errors = sorted(validator.iter_errors(doc), key=lambda e: [str(p) for p in e.absolute_path])
        if errors:
            where = "/".join(str(p) for p in errors[0].absolute_path)
            raise CatalogError(f"{path.name}: {where}: {errors[0].message[:200]}")
        if path.stem != doc["axis"] or any(c["axis"] != doc["axis"] for c in doc["cards"]):
            raise CatalogError(f"{path.name}: every card must sit in the file named for its axis")
        cards.extend(doc["cards"])
    check_unique(cards)
    return sorted(cards, key=lambda c: c["id"])


def check_unique(cards: list[dict]) -> None:
    """A duplicate id, an id that is not <axis>:<token>, an ambiguous alias or a shared alias is an error."""
    seen_ids: set[str] = set()
    owner: dict[str, str] = {}
    for card in cards:
        if card["id"] != f"{card['axis']}:{card['token']}":
            raise CatalogError(f"{card['id']}: id must be <axis>:<token>")
        if card["id"] in seen_ids:
            raise CatalogError(f"{card['id']}: duplicate card id")
        seen_ids.add(card["id"])
        for alias in card["aliases"]:
            key = alias["name"].strip().lower()
            if key in AMBIGUOUS_NAMES:
                raise CatalogError(f"{card['id']}: alias {alias['name']!r} is in AMBIGUOUS_NAMES (decision 2)")
            if key in owner and owner[key] != card["id"]:
                raise CatalogError(f"alias {alias['name']!r} is shared by {owner[key]} and {card['id']}")
            owner[key] = card["id"]


def load_recipes(repo: Path) -> list[dict]:
    """Every recipe file, schema-validated, sorted by id (P56 T1: one file per recipe - the merge-collision unit).

    An absent directory is not an error: the catalogue is the cards' until the first recipe lands."""
    import jsonschema

    directory = Path(repo) / RECIPES_REL
    if not directory.is_dir():
        return []
    schema = json.loads((Path(repo) / RECIPE_SCHEMA_REL).read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    recipes: list[dict] = []
    for path in sorted(directory.glob("*.json")):
        doc = json.loads(path.read_text(encoding="utf-8"))
        errors = sorted(validator.iter_errors(doc), key=lambda e: [str(p) for p in e.absolute_path])
        if errors:
            where = "/".join(str(p) for p in errors[0].absolute_path) or "<recipe>"
            raise CatalogError(f"{path.name}: {where}: {errors[0].message[:200]}")
        if doc["id"] != f"recipe:{path.stem}":
            raise CatalogError(f"{doc['id']}: a recipe lives in the file named for its slug, not {path.name}")
        recipes.append(doc)
    check_recipes_unique(recipes)
    return sorted(recipes, key=lambda r: r["id"])


def check_recipes_unique(recipes: list[dict]) -> None:
    """A duplicate recipe id, an ambiguous alias or an alias two recipes share is an error (decision 2 again)."""
    seen: set[str] = set()
    owner: dict[str, str] = {}
    for recipe in recipes:
        if recipe["id"] in seen:
            raise CatalogError(f"{recipe['id']}: duplicate recipe id")
        seen.add(recipe["id"])
        for alias in recipe["aliases"]:
            key = alias["name"].strip().lower()
            if key in AMBIGUOUS_NAMES:
                raise CatalogError(f"{recipe['id']}: alias {alias['name']!r} is in AMBIGUOUS_NAMES (decision 2)")
            if key in owner and owner[key] != recipe["id"]:
                raise CatalogError(f"alias {alias['name']!r} is shared by {owner[key]} and {recipe['id']}")
            owner[key] = recipe["id"]


def _load_compiler_file(path: Path):
    """Execute another checkout's compiler under a unique module name; the import cache is left as it was."""
    name = f"_effects_catalog_{COMPILER}_{hashlib.sha1(str(path).encode('utf-8')).hexdigest()[:12]}"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise CatalogError(f"cannot load the compiler at {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    sys.path.insert(0, str(path.parent))
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.remove(str(path.parent))
        sys.modules.pop(name, None)
    return module


def compiler_when(repo: Path) -> dict[str, dict[str, str]]:
    """SPECIES_WHEN / CHART_TO_WHEN from the compiler, read-only: `<repo>`'s own copy when it has one, else this one's."""
    path = Path(repo) / SCRIPTS_REL / f"{COMPILER}.py"
    if path.is_file() and path.resolve() != (SCRIPTS / f"{COMPILER}.py").resolve():
        module = _load_compiler_file(path.resolve())
    else:
        module = importlib.import_module(COMPILER)
    return {name: dict(getattr(module, name)) for name in sorted(set(PULLED_WHEN.values()))}


# --------------------------------------------------------------------------- joins

def _heading_containing(rows: list[dict], words: str) -> dict | None:
    needle = re.sub(r"\([^)]*\)", "", words).strip().lower()
    if not needle:
        return None
    return next((r for r in rows if needle in r["heading"].lower()), None)


def _id_line(repo: Path | None, rel: str, ident: str) -> int | None:
    """The 1-based line of a BACKLOG row (`| **R26-30 ...** |`) or a ruling heading (`## E88`) in the document."""
    path = Path(repo) / rel if repo is not None else None
    if path is None or not path.is_file():
        return None
    lead = r"^\|\s*\*\*" if BACKLOG_ROW.match(ident) else r"^#+\s+"
    pattern = re.compile(lead + re.escape(ident) + r"(?!\d)")
    lines = path.read_text(encoding="utf-8").splitlines()
    return next((n for n, line in enumerate(lines, 1) if pattern.match(line)), None)


def _named_doc_cite(ref: str, rel: str, rest: str, index: list[dict], repo: Path | None) -> dict:
    words = rest.split()
    ident = words[0] if words else ""
    if BACKLOG_ROW.match(ident) or RULING_ID.match(ident):
        line = _id_line(repo, rel, ident)
        return {"ref": ref, "path": rel if line else None, "line": line}
    hit = _heading_containing([r for r in index if r["path"] == rel], rest)
    return {"ref": ref, "path": hit["path"] if hit else None, "line": hit["line"] if hit else None}


def resolve_cite(ref: str, index: list[dict], repo: Path | None = None) -> dict:
    """{ref, path, line} for one doctrine cite; path and line stay None when nothing answers it (never line 1)."""
    head, _, rest = ref.partition(" ")
    if BACKLOG_ROW.match(head):
        head, rest = "BACKLOG", ref
    if head in NAMED_DOCS:
        return _named_doc_cite(ref, NAMED_DOCS[head], rest, index, repo)
    if head == "memory" and rest:
        rows = [r for r in index if r["path"] == MEMORY_REL % rest.strip()]
        return {"ref": ref, "path": rows[0]["path"] if rows else None, "line": rows[0]["line"] if rows else None}
    match = BGR.CITE_RE.match(ref)
    if match:
        path, line, emit = BGR._resolve(match, index)
        if emit and path:
            return {"ref": ref, "path": path, "line": line}
    return {"ref": ref, "path": None, "line": None}


def dial_values(repo: Path, dials: dict | None, card_id: str = "?") -> dict[str, str] | None:
    """The frozen object's top-level keys and literal values, read from the module source; None when the card names
    no dials. A module that does not exist, or an object it does not declare, is a CatalogError naming the card."""
    if not dials:
        return None
    import build_animation_registry as BAR  # the object-literal parser, defined once there

    path = Path(repo) / dials["module"]
    if not path.is_file():
        raise CatalogError(f"{card_id}: dials module {dials['module']!r} does not exist")
    text = path.read_text(encoding="utf-8")
    decl = re.search(r"(?:export\s+)?const\s+" + re.escape(dials["object"]) + r"\s*=", text)
    span = BAR.constant_object(text, decl.start()) if decl else None
    if not span:
        raise CatalogError(f"{card_id}: dials object {dials['object']!r} is not a frozen object in {dials['module']}")
    return {key: " ".join(value.split()) for key, value, _ in BAR.object_entries(text, *span)}


def record_of(card: dict, when: dict, index: list[dict], repo: Path) -> dict:
    """The card, plus the pulled `when`, the resolved `doctrine` and the module's `dials_values`."""
    record = dict(card)
    table = PULLED_WHEN.get(card["axis"])
    if table:
        record["when"] = when.get(table, {}).get(card["token"])
        record["when_source"] = f"{SCRIPTS_REL}/{COMPILER}.py {table}"
    record["doctrine"] = [resolve_cite(ref, index, repo) for ref in card.get("doctrine", [])]
    record["dials_values"] = dial_values(repo, card.get("dials"), card["id"])
    return record


MEMBER_KEYS = ("card", "option", "offset_s", "role", "options", "optional")


def recipe_record_of(recipe: dict, titles: dict[str, str], index: list[dict], repo: Path) -> dict:
    """One recipe as a catalogue record: `axis: recipe`, the ordered members with the TITLE pulled from the card
    each names (never stored in the recipe file), and its cites resolved exactly as a card's."""
    members = []
    for member in recipe["members"]:
        row = {key: member.get(key) for key in MEMBER_KEYS}
        row["title"] = titles.get(member["card"])
        members.append(row)
    return {
        "axis": RECIPE_AXIS,
        "id": recipe["id"],
        "title": recipe["title"],
        "aliases": recipe["aliases"],
        "acts": recipe["acts"],
        "members": members,
        "window_s": float(recipe.get("window_s", DEFAULT_WINDOW_S)),
        "dials": recipe.get("dials") or {},
        "dials_source": recipe.get("dials_source"),
        "does": recipe["does"],
        "doctrine": [resolve_cite(ref, index, repo) for ref in recipe.get("doctrine", [])],
        "status": recipe["status"],
        "proof": recipe.get("proof"),
        "source": recipe["source"],
        "count": recipe["count"],
        "backlog": recipe.get("backlog") or [],
        **({"use_when": recipe["use_when"]} if recipe.get("use_when") else {}),
    }


def cards_of(records: list[dict]) -> list[dict]:
    return [r for r in records if r["axis"] != RECIPE_AXIS]


def recipes_of(records: list[dict]) -> list[dict]:
    return [r for r in records if r["axis"] == RECIPE_AXIS]


def build(repo: Path = REPO, when: dict | None = None) -> list[dict]:
    """Every catalogue record: the cards sorted by id, then the recipes sorted by id (the recipe axis is last, so
    the cards' records and their order never move when a recipe lands). `when` injects the compiler's WHEN dicts."""
    repo = Path(repo)
    cards = load_cards(repo)
    pulled = when if when is not None else compiler_when(repo)
    index = BGR.load_docs_index(repo)
    records = [record_of(card, pulled, index, repo) for card in cards]
    recipes = load_recipes(repo)
    titles = {r["id"]: r["title"] for r in records}
    titles.update({r["id"]: r["title"] for r in recipes})
    return records + [recipe_record_of(r, titles, index, repo) for r in recipes]


# --------------------------------------------------------------------------- the Markdown face

def _flat(text) -> str:
    return " ".join(str(text).split())


def _cite_text(cite: dict) -> str:
    return f"{cite['ref']} -> " + (f"{cite['path']}:{cite['line']}" if cite["path"] else "unresolved")


def _phase_lines(record: dict) -> list[str]:
    lines = []
    for n, phase in enumerate(record.get("phases") or [], 1):
        dials = phase.get("dials") or {}
        dial = ("; dials: " + ", ".join(f"`{k}`={_flat(v)}" for k, v in dials.items())) if dials else ""
        lines.append(f"  {n}. **{phase['name']}** - {phase['does']} (trigger: {phase['trigger']}{dial})")
    return lines


def _lives_text(lives: dict) -> str:
    parts = [lives["form"], f"`{lives['path']}`" if lives.get("path") else "no path",
             f"symbol `{lives['symbol']}`" if lives.get("symbol") else "no symbol"]
    if lives.get("also"):
        parts.append("also " + ", ".join(f"`{s}`" for s in lives["also"]))
    text = " - ".join(parts)
    return text + (f" - {lives['note']}" if lives.get("note") else "")


def _proof_text(proof: dict) -> str:
    first = proof.get("first_use")
    use = f"{first.get('project')} {first.get('build')} t={first.get('t')}" if first else "none"
    return f"golden {proof.get('golden') or 'none'} - test {proof.get('test') or 'none'} - first use {use}"


def _head_lines(record: dict) -> list[str]:
    author = record["author"]
    when = record.get("when")
    return [f"### {record['title']}", "", f"- **id** `{record['id']}` - **does** {record['does']}",
            f"- **when** {when} ({record.get('when_source') or 'no source'})" if when else "- **when** none",
            f"- **example** `{author['example']}` ({author.get('example_source') or 'authored'}; key: "
            f"{author['key'] or 'none'}; check: {author['check']})"]


def card_block(record: dict) -> list[str]:
    lines = _head_lines(record)
    if record.get("phases"):
        lines += ["- **phases**", *_phase_lines(record)]
    for blend in record.get("blends") or []:
        lines.append(f"- **blend** {blend['source']} -> {blend['became']} ({blend.get('tie') or 'untied'}; "
                     f"{blend.get('record') or 'no record'})")
    if record.get("options"):
        lines.append("- **options** " + "; ".join(
            f"`{o['token']}` {o['means']}" + (f" ({o['source_set']})" if o.get("source_set") else "")
            for o in record["options"]))
    lines.append(f"- **lives** {_lives_text(record['lives'])}")
    if record.get("dials_values") is not None:
        values = ", ".join(f"`{k}`={v}" for k, v in record["dials_values"].items())
        lines.append(f"- **dials** `{record['dials']['object']}` in `{record['dials']['module']}`: {values}")
    backlog = f" (backlog {', '.join(record['backlog'])})" if record.get("backlog") else ""
    implicit = " (implicit: no token of its own)" if record.get("implicit") else ""
    callable_ = record["callable"]
    lines += [f"- **status** {record['status']}{backlog}{implicit} - **callable** "
              f"{'yes' if callable_['today'] else 'no'}" + (f": {callable_['why']}" if callable_.get("why") else ""),
              f"- **proof** {_proof_text(record['proof'])}"]
    if record.get("doctrine"):
        lines.append("- **doctrine** " + "; ".join(_cite_text(c) for c in record["doctrine"]))
    if record["aliases"]:
        lines.append("- **aliases** " + "; ".join(f"\"{a['name']}\" ({a['source']})" for a in record["aliases"]))
    return lines + [""]


def _offset_text(offset) -> str:
    """`+2.05s`, or `+2.05..6.65s` when the seed fired at a range of offsets."""
    if isinstance(offset, (list, tuple)):
        return f"+{float(offset[0]):g}..{float(offset[1]):g}s"
    return f"+{float(offset or 0.0):g}s"


def member_line(member: dict) -> str:
    card = member["card"] + (f" + {member['option']}" if member.get("option") else "")
    title = f" ({member['title']})" if member.get("title") else " (no card of that id)"
    defaults = (" - defaults " + ", ".join(f"`{k}`={_flat(v)}" for k, v in (member.get("options") or {}).items())
                if member.get("options") else "")
    return (f"  - {_offset_text(member['offset_s'])} -> `{card}`{title} - {member['role']}{defaults}"
            + (" - optional" if member.get("optional") else ""))


def _count_says(count: int) -> str:
    return "a decoration" if count == 1 else ("unfired" if count < 1 else "a grammar")


def recipe_block(record: dict) -> list[str]:
    lines = [f"### {record['title']}", "", f"- **id** `{record['id']}` - **does** {record['does']}",
             f"- **acts** {', '.join(record['acts'])} - **window** {record['window_s']:g}s",
             "- **members**", *[member_line(m) for m in record["members"]]]
    if record.get("dials"):
        lines.append("- **dials** " + ", ".join(f"`{k}`={_flat(v)}" for k, v in record["dials"].items())
                     + f" ({record.get('dials_source') or 'no source'})")
    proof = record.get("proof")
    if proof:
        at = ", ".join("-" if t is None else f"{float(t):g}" for t in proof.get("members_at") or [])
        lines.append(f"- **proof** {proof['project']} / {proof['build']} @ {float(proof['t']):g}s - members at "
                     f"{at} - `{proof['timeline']}`")
    lines.append(f"- **status** {record['status']} - **count** {record['count']} ({_count_says(record['count'])})"
                 f" - **source** {record['source']}")
    if record.get("doctrine"):
        lines.append("- **doctrine** " + "; ".join(_cite_text(c) for c in record["doctrine"]))
    if record.get("use_when"):
        uw = record["use_when"]
        lines.append(f"- **use when** {uw['act']} - {uw['moment']} - {uw['shape']}: {uw['use']}. **not** {uw['dont']}")
    if record["aliases"]:
        lines.append("- **aliases** " + "; ".join(f"\"{a['name']}\" ({a['source']})" for a in record["aliases"]))
    return lines + [""]


def recipe_count_table(recipes: list[dict]) -> list[str]:
    lines = ["| status | recipes | members | fires (sum of count) |", "|---|---|---|---|"]
    for status in RECIPE_STATUS_ORDER:
        rows = [r for r in recipes if r["status"] == status]
        lines.append(f"| {status} | {len(rows)} | {sum(len(r['members']) for r in rows)} | "
                     f"{sum(r['count'] for r in rows)} |")
    return lines


def recipes_section(recipes: list[dict]) -> list[str]:
    """The Recipes section: the count table, then one block per recipe (P56 T4). Empty until a recipe lands."""
    if not recipes:
        return []
    body = ["## Recipes", "",
            "A recipe is the unit of AUTHORING (E96): ordered card ids with offsets, the act it serves, the dials as",
            "measured and the played instant that proves it. `proven` means the members fire inside `window_s` at that",
            "instant in the timeline named below - `effects_catalog_check.py` re-walks it. A recipe that fires once is",
            "a decoration; one that fires four times is a grammar.", "",
            *recipe_count_table(recipes), ""]
    for record in recipes:
        body += recipe_block(record)
    return body


def count_table(records: list[dict]) -> list[str]:
    axes = [a for a in AXIS_ORDER if any(r["axis"] == a for r in records)]
    lines = ["| axis | cards | options | " + " | ".join(STATUS_ORDER) + " |",
             "|---|---|---|" + "---|" * len(STATUS_ORDER)]
    for axis in axes:
        rows = [r for r in records if r["axis"] == axis]
        counts = " | ".join(str(sum(1 for r in rows if r["status"] == s)) for s in STATUS_ORDER)
        lines.append(f"| {axis} | {len(rows)} | {sum(len(r.get('options') or []) for r in rows)} | {counts} |")
    return lines


def ambiguous_lines(records: list[dict]) -> list[str]:
    lines = []
    for name in sorted(AMBIGUOUS_NAMES):
        claimed = AMBIGUOUS_NAMES[name]
        live = [r["id"] for r in records if name in r["token"].lower() or name in r["title"].lower()]
        said = f"used by {', '.join(claimed)}; dropped from each" if claimed else "named ambiguous by decision 2"
        lines.append(f"- \"{name}\" - {said} - cards whose token or title contains it: {', '.join(live) or 'none'}")
    return lines


def _md_head(records: list[dict], recipes: list[dict] | None = None) -> list[str]:
    return [
        "# EFFECTS-CATALOG - every effect the engine performs, one card each",
        "",
        f"Generated by `{BUILD_CMD}` from `{CARDS_REL}/*.json` (schema `{SCHEMA_REL}`). Do not hand-edit it:",
        "`--check` fails when it drifts from the cards, the compiler's `SPECIES_WHEN` / `CHART_TO_WHEN` (pulled into",
        "`when` on the species, page_species and chart_to axes), the module dial objects or `docs/DOCS-INDEX.jsonl`.",
        "",
        "The recipe - one call:",
        "",
        "```bash",
        'python content/video_engine/scripts/effects_card.py "<name>"',
        f'rg -i "<name>" {MD_REL}',
        "```",
        "",
        "Each card is: title - id - does - when - the example - phases as a numbered list - blends - options -",
        "lives (module | inline | compiler-only | declared-unbuilt, the path and the one symbol) - dials read from the",
        "module - status and callable - proof - doctrine cites resolved to path:line - aliases. A token that is only a",
        "parameter of an effect is an option on its card, never a card.",
        "",
        f"{len(records)} cards, {sum(len(r.get('options') or []) for r in records)} options, "
        f"{len({r['axis'] for r in records})} axes."
        + (f" {len(recipes)} recipes ({sum(1 for r in recipes if r['status'] == 'proven')} proven)."
           if recipes else ""),
        "",
        *count_table(records),
        "",
    ]


def render_md(records: list[dict]) -> str:
    cards, recipes = cards_of(records), recipes_of(records)
    body: list[str] = []
    for axis in AXIS_ORDER:
        rows = [r for r in cards if r["axis"] == axis]
        if rows:
            body += [f"## {axis}", ""]
            for record in rows:
                body += card_block(record)
    body += recipes_section(recipes)
    unproven = [r for r in cards if not r["proof"].get("golden") and not r["proof"].get("test")]
    body += ["## Ambiguous names", "", *ambiguous_lines(cards), "",
             "## No proof yet", "",
             *[f"- `{r['id']}` - {r['title']} ({r['status']})" for r in unproven], ""]
    return "\n".join(_md_head(cards, recipes) + body)


def render_jsonl(records: list[dict]) -> str:
    return "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in records)


# --------------------------------------------------------------------------- write / check

def rendered(repo: Path = REPO, when: dict | None = None) -> dict[str, str]:
    records = build(repo, when)
    return {JSONL_REL: render_jsonl(records), MD_REL: render_md(records)}


def write(repo: Path = REPO, when: dict | None = None) -> dict[str, str]:
    texts = rendered(repo, when)
    for rel, text in texts.items():
        path = Path(repo) / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text.encode("utf-8"))
    return texts


def check(repo: Path = REPO, when: dict | None = None) -> list[str]:
    """One entry per stale artifact: "<path> (+added/-removed lines)". Empty = in sync."""
    problems: list[str] = []
    for rel, want in rendered(repo, when).items():
        path = Path(repo) / rel
        if not path.is_file():
            problems.append(f"{rel} (missing)")
            continue
        have = path.read_bytes().decode("utf-8")
        if have == want:
            continue
        diff = list(difflib.ndiff(have.splitlines(), want.splitlines()))
        added = sum(1 for d in diff if d.startswith("+ "))
        removed = sum(1 for d in diff if d.startswith("- "))
        problems.append(f"{rel} (+{added}/-{removed} lines)")
    return problems


def summary(records: list[dict]) -> str:
    cites = [c for r in records for c in r["doctrine"]]
    cards, recipes = cards_of(records), recipes_of(records)
    said = (f" {len(recipes)} recipes ({sum(1 for r in recipes if r['status'] == 'proven')} proven),"
            if recipes else "")
    return (f"{len(cards)} cards, {sum(len(r.get('options') or []) for r in cards)} options,{said} "
            f"{sum(1 for c in cites if c['path'])}/{len(cites)} cites resolved")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true", help="exit 1 when either artifact is stale (default)")
    ap.add_argument("--write", action="store_true", help="regenerate both artifacts")
    ap.add_argument("--repo", type=Path, default=REPO, help="repository root (default: this checkout)")
    args = ap.parse_args(argv)
    root = args.repo.resolve()
    try:
        if args.write:
            write(root)
            print(f"build_effects_catalog: wrote {JSONL_REL} + {MD_REL}")
        stale = check(root)
    except CatalogError as exc:
        print(f"build_effects_catalog: INVALID - {exc}")
        return 1
    if stale:
        print("build_effects_catalog: STALE - " + "; ".join(stale) + " - run --write")
        return 1
    if not args.write:   # P55 T4: the drift gate rides --check, so build_docs_layers.py carries it
        import effects_catalog_check as ECC

        drift = ECC.check(root)
        if drift:
            print("build_effects_catalog: DRIFT - " + "; ".join(drift))
            return 1
    print(f"build_effects_catalog: in sync ({summary(build(root))})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
