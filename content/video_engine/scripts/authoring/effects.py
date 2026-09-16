"""The authoring kit - EFFECTS: name an effect, get its catalogue card (P55 T8).

    from authoring import effects as FX
    FX.card("evidence wall")["id"]    # 'dock_payload:stack'
    FX.find("stack")                  # every card carrying that token - a list, never a guess
    FX.card("badge ladder")["id"]     # 'recipe:badge-ladder' - a RECIPE resolves the same way (P56 T4)

Reads ONLY the generated layer `docs/EFFECTS-CATALOG.jsonl`, so every reader shares one source; the card
files are the generator's input and are never opened here. An ambiguous name resolves to a LIST (P55
decision 2): `card()` refuses it and names every candidate. Nothing in this module names an episode.

The layer also carries the RECIPES (`axis: "recipe"`, P56 T4): a record with no `token` and no `lives`. The
tiers key on what a record HAS, so a recipe resolves by id, title or alias, and an exact card token still
wins over a recipe whose title merely contains the word (the catalogue's retrieval budget, P56 risks).

The layer is BUILD OUTPUT (P63): `load()` ensures it before it reads it, so a card edited since the last
build is in the card this returns and no agent runs a builder by hand. `load(..., ensure=False)` reads the
file as it sits; a tree with no builders in it (every test fixture) is never rebuilt. The check costs a
0.44 s digest of the catalogue's inputs, and a caller resolves a dozen names in a row (`card()` loads for
each), so it runs ONCE PER PROCESS per repository - a CLI, a build or a test session pays it once. A process
that outlives an edit to the cards asks for another pass with `ensure_catalog(repo, force=True)`.
"""
from __future__ import annotations

import difflib
import json
import re
import sys
from pathlib import Path

CATALOG_REL = "docs/EFFECTS-CATALOG.jsonl"
CATALOG_LAYER = "effects-catalog"      # docs_layers' name for the builder that writes CATALOG_REL
RECIPE_AXIS = "recipe"
SCRIPTS = Path(__file__).resolve().parents[1]
REPO = Path(__file__).resolve().parents[4]
SUGGESTIONS = 3
_ENSURED: set[str] = set()             # the repositories this process has already ensured the catalogue in

if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import docs_layers as DL  # noqa: E402  (the layer table, the digest and the rebuild live there, P63 T1)

_SEPARATORS = re.compile(r"[\s\-]+")
_ARTICLE = re.compile(r"^(?:the|a|an)\s+")


def normalise(name: str) -> str:
    """Case, whitespace, hyphens and a leading article never change a name:
    'Blur-Zoom' == 'blur zoom' == 'blurzoom', 'The test card' == 'test card'."""
    spaced = " ".join(str(name).lower().split())
    return _SEPARATORS.sub("", _ARTICLE.sub("", spaced))


def ensure_catalog(repo: Path, *, force: bool = False) -> list[str]:
    """Rebuild the catalogue (and its upstream) iff their inputs moved; return what was rebuilt.

    Once per process per repository unless `force`. A no-op on a tree with no builders - a fixture. A
    builder that fails is NAMED on stderr and the catalogue is read as it sits: a broken card in
    someone else's lane must not take this reader down with it."""
    key = str(Path(repo).resolve())
    if key in _ENSURED and not force:
        return []
    try:
        rebuilt = DL.ensure([CATALOG_LAYER], repo)
    except DL.LayerError as exc:
        print(f"[layers] {exc.layer} failed to rebuild: {exc.detail}", file=sys.stderr)
        return []
    _ENSURED.add(key)
    return rebuilt


def load(repo: Path | str | None = None, *, ensure: bool = True) -> list[dict]:
    """Every record of the generated catalogue, in file order - ensured first (P63)."""
    repo = Path(repo or REPO)
    if ensure:
        ensure_catalog(repo)
    path = repo / CATALOG_REL
    if not path.is_file():
        raise FileNotFoundError(f"{path} is missing - run build_effects_catalog.py --write")
    lines = path.read_text(encoding="utf-8").splitlines()
    return [json.loads(line) for line in lines if line.strip()]


def is_recipe(record: dict) -> bool:
    """A combination of cards, not an effect (P56): no token, no lives, an ordered `members` list."""
    return record.get("axis") == RECIPE_AXIS


def alias_names(card: dict) -> list[str]:
    """The alias names (records carry `{name, source}` objects)."""
    return [a["name"] if isinstance(a, dict) else str(a) for a in card.get("aliases") or []]


def _names(card: dict) -> list[str]:
    return [card.get("title") or ""] + alias_names(card)


def _tiers(raw: str, key: str):
    """The match tiers in order; the first tier with any hit wins. Every tier tolerates a record with no
    `token` and no `lives` (a recipe): it reads what the record has, never what a card would have."""
    yield lambda c: str(c.get("id") or "").lower() == raw
    yield lambda c: bool(c.get("token")) and normalise(c["token"]) == key
    yield lambda c: key in {normalise(n) for n in _names(c)}
    yield lambda c: any(key in normalise(t) for t in _names(c) + [c.get("does") or ""])


def find(name: str, repo: Path | str | None = None, *, cards: list[dict] | None = None) -> list[dict]:
    """Exact id, then exact token on any axis (EVERY card with it), then title/alias equality, then a
    substring of title, alias or does. An empty name finds nothing."""
    key = normalise(name)
    if not key:
        return []
    pool = load(repo) if cards is None else cards
    raw = " ".join(str(name).split()).lower()
    for matches in _tiers(raw, key):
        hits = [c for c in pool if matches(c)]
        if hits:
            return hits
    return []


def suggest(name: str, cards: list[dict], n: int = SUGGESTIONS) -> list[dict]:
    """The `n` cards whose titles are nearest the name (difflib), nearest first."""
    by_title: dict[str, dict] = {}
    for c in cards:
        by_title.setdefault((c.get("title") or c["id"]).lower(), c)
    near = difflib.get_close_matches(str(name).lower(), list(by_title), n=n, cutoff=0.0)
    return [by_title[t] for t in near]


def _listing(cards: list[dict]) -> str:
    return "\n".join(f"  - {c['id']} - {c.get('title')}" for c in cards)


def card(name: str, repo: Path | str | None = None) -> dict:
    """Exactly one card, or LookupError naming the candidates (ambiguous) or the nearest titles (unknown)."""
    pool = load(repo)
    hits = find(name, cards=pool)
    if len(hits) == 1:
        return hits[0]
    if hits:
        raise LookupError(f"{name!r} is ambiguous: {len(hits)} cards match - name one id:\n{_listing(hits)}")
    raise LookupError(f"{name!r} is unknown; the nearest titles:\n{_listing(suggest(name, pool))}")
