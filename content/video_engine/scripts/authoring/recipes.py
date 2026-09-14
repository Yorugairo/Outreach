"""The authoring kit - RECIPES: name a BEAT, get the proven combination as data (P56 T5).

    from authoring import recipes as RX
    p = RX.preset("the badge ladder")      # the ordered members, their offsets, the option DEFAULTS, the dials
    p["binds"]                             # what the AUTHOR still owes, per member: the asset, the target, the label
    RX.for_act("EXPLAINS")                 # every recipe that act makes available, proven first, then by count

NOT AN ALLOCATOR, and it cannot become one (the proposer's own refusal, `lint_species_choice.py`): this module
returns CANDIDATES. It names no episode, chooses nothing by count, writes no shot table and allocates nothing -
the AUTHOR binds. A loop that fills slots by count answers "how many fit" instead of "which one belongs", and no
quality of tuning fixes that (PIPELINE.md: "Stage 7 is AUTHORED. There is no allocator"). `for_act` orders by
proven-first then count so the record is READ in the order the record earned; that ordering is not a choice.

Reads ONLY the generated layer `docs/EFFECTS-CATALOG.jsonl`, through `effects.load` - cards and recipes share one
source, so a preset can never name an effect the compiler does not accept. Nothing here opens a recipe file.

THE BINDS TABLE - what the author supplies per member, derived from the MEMBER CARD's own `axis` / `author.key` in
the catalogue (never from the recipe, which carries no episode fact and no asset):

| the member card's `author.check` (its axes) | the author supplies (`needs`) |
| --- | --- |
| `dock` (`dock_kind`, `dock_payload`) | `asset` - the dock tuple's asset id; and `data` on a `dock_payload` (the payload's own content: the `<asset>.series.json`, the record block, the stack list) |
| `dock_option` (`dock_option`) | `asset`; and `target` when the option names a PLACE on the world under the card - a reading box, a plate surface, a layer (`read`, `embed`, `behind` in the card's `author.key`) |
| `chart` (`page_builder`, `chart_dock`) | `data` (the series the page or the dock is built from) and `builder args` (the ledger id's own fields) |
| `species` (`species`, `page_species`, `chart_to`) | `target`; and `label` on a callout, a figure, a stamp or a chip (the mark carries the number as it is said, E56) |
| `plate` (`plate_option`) | `asset` - the plate the option is a suffix of |
| `exit` / `enter` (`exit`, `page_enter`, `page_exit`) | nothing - the row's own transition carries it |
| anything else (`arrival`, `camera`, `caption`, `idle`, `kinetics`, `module`, `overflow`, `none`) | nothing |
"""
from __future__ import annotations

import copy
import re
from pathlib import Path

from . import effects

CANDIDATE_REASON = "no approved cut has carried it (no proof)"
LABEL_TOKENS = ("callout", "figure", "stamp", "chip")
MEMBER_KEYS = ("card", "option", "offset_s", "role", "options", "optional", "title")
PROVEN = "proven"

# The option keys whose value is a PLACE on the world under the dock, so the author owes a target as well as an
# asset: the reading box, an embed surface, a layer to sit behind (`dock_option:read` / `:embed` / `:behind`).
PLACED_OPTION = re.compile(r"\b(read|embed|behind)\b")

# The table above, as code. Keyed on the member card's `author.check` - the catalogue's own word for which
# validator accepts it - and falling back to the card's `axis` when a card carries no author block.
# The four IMPLICIT cards P56 T8 added carry `author.check: "none"` (they have no option key of their own), so their
# needs are named by id: a badge is the author's TEXT on the rail, a world is the plate or clip asset, the Ken Burns
# push is dials only.
NEEDS_BY_CARD: dict[str, tuple[str, ...]] = {
    "dock_option:badge": ("label",),
    "plate_option:world": ("asset",),
    "plate_option:clip": ("asset",),
    "plate_option:ken": (),
}

NEEDS_BY_CHECK: dict[str, tuple[str, ...]] = {
    "dock": ("asset",),
    "dock_option": ("asset",),
    "chart": ("data", "builder args"),
    "species": ("target",),
    "plate": ("asset",),
    "exit": (),
    "enter": (),
}


def load(repo: Path | str | None = None) -> list[dict]:
    """Every RECIPE record of the generated catalogue, in file order (the cards are dropped here)."""
    return [r for r in effects.load(repo) if effects.is_recipe(r)]


def _records(repo: Path | str | None, records: list[dict] | None) -> list[dict]:
    return effects.load(repo) if records is None else records


def _split(records: list[dict]) -> tuple[list[dict], dict[str, dict]]:
    """(the recipes in file order, the cards by id) - one pass over the layer, for a caller holding it already."""
    recipes = [r for r in records if effects.is_recipe(r)]
    cards = {c["id"]: c for c in records if not effects.is_recipe(c)}
    return recipes, cards


def _listing(records: list[dict]) -> str:
    return "\n".join(f"  - {r['id']} - {r.get('title')}" for r in records)


def needs_of(card: dict | None, member: dict) -> list[str]:
    """What the author must supply for one member, read off its CARD (the binds table in this module's header).

    A member naming a card the catalogue does not carry is not silently dropped: the need says so, because a
    recipe whose member does not resolve is the drift gate's failure, not the author's."""
    if card is None:
        return [f"{member.get('card')} is not in the catalogue - run build_effects_catalog.py --write"]
    author = card.get("author") or {}
    check = author.get("check") or card.get("axis") or ""
    if check == "none" and card.get("id") in NEEDS_BY_CARD:      # the implicit cards: no validator, needs named by id
        return list(NEEDS_BY_CARD[card["id"]])
    needs = list(NEEDS_BY_CHECK.get(check, ()))
    if check == "dock" and card.get("axis") == "dock_payload":
        needs.append("data")
    if check == "dock_option" and PLACED_OPTION.search(author.get("key") or ""):
        needs.append("target")
    if check == "species" and card.get("token") in LABEL_TOKENS:
        needs.append("label")
    return needs


def _member(raw: dict) -> dict:
    """One member as DATA the author may edit: every value a copy, so a preset can never write back into the
    loaded record (the option defaults are handed over, not lent)."""
    return {k: copy.deepcopy(raw.get(k)) for k in MEMBER_KEYS}


def _preset(recipe: dict, cards: dict[str, dict]) -> dict:
    members = [_member(m) for m in recipe.get("members") or []]
    return {
        "id": recipe["id"],
        "title": recipe.get("title"),
        "acts": list(recipe.get("acts") or []),
        "status": recipe.get("status"),
        "window_s": recipe.get("window_s"),
        "members": members,
        "dials": copy.deepcopy(recipe.get("dials") or {}),
        "binds": [{"member": i, "card": m["card"], "needs": needs_of(cards.get(m["card"]), m)}
                  for i, m in enumerate(members)],
        "proof": copy.deepcopy(recipe.get("proof")),
        "count": recipe.get("count"),
        "candidate_reason": None if recipe.get("status") == PROVEN else CANDIDATE_REASON,
    }


def preset(name: str, repo: Path | str | None = None, *, records: list[dict] | None = None) -> dict:
    """Exactly one recipe as the author's data, or LookupError naming the candidates (ambiguous) or the nearest
    titles (unknown). Resolution is `effects.find`'s tiers over the RECIPES only: an exact id, then title or alias
    equality, then a substring of the title, an alias or `does` (no recipe carries a token, so that tier is void)."""
    recipes, cards = _split(_records(repo, records))
    hits = effects.find(name, cards=recipes)
    if len(hits) == 1:
        return _preset(hits[0], cards)
    if hits:
        raise LookupError(f"{name!r} is ambiguous: {len(hits)} recipes match - name one id:\n{_listing(hits)}")
    raise LookupError(f"{name!r} is not a recipe; the nearest titles:\n{_listing(effects.suggest(name, recipes))}")


def for_act(act: str, repo: Path | str | None = None, *, records: list[dict] | None = None) -> list[dict]:
    """Every recipe whose `acts` carry this act, as presets: proven first, then by `count` descending, then id.
    A list of CANDIDATES for the author to bind or delete - the order is the record's, never a recommendation."""
    recipes, cards = _split(_records(repo, records))
    hits = [r for r in recipes if act in (r.get("acts") or [])]
    hits.sort(key=lambda r: (r.get("status") != PROVEN, -(r.get("count") or 0), r["id"]))
    return [_preset(r, cards) for r in hits]
