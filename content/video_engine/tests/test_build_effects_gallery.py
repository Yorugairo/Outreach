"""P55 T9: the effects gallery is one static page generated from EFFECTS-CATALOG.jsonl only.

The pins: two builds give byte-identical index.html; every card id appears as exactly one tile; a card with no golden
shows the "no proof yet" marker; the verdict stack tile lists its five phases; a resolved golden is copied beside the
page with its @proof-* strip; and no http(s) string appears outside a card's quoted example or blend text (no network).

P56 T4: the recipes get their own section - one tile each, the members in order with the proof frame of every member
whose card has one - and they never count as cards.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import build_effects_gallery as BEG  # noqa: E402

CATALOG = ROOT / BEG.CATALOG_REL
FRAMES = ROOT / BEG.FRAMES_REL
VERDICT_ID = "dock_payload:stack"


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    out = tmp_path_factory.mktemp("gallery")
    index, line = BEG.build(CATALOG, FRAMES, out)
    return index, line, index.read_text(encoding="utf-8")


def tile_of(page: str, card_id: str) -> str:
    match = re.search(rf'<article class="tile[^"]*" data-id="{re.escape(card_id)}".*?</article>', page, re.S)
    assert match, card_id
    return match.group(0)


def test_two_builds_give_identical_index_bytes(tmp_path):
    first, _ = BEG.build(CATALOG, FRAMES, tmp_path / "a")
    second, _ = BEG.build(CATALOG, FRAMES, tmp_path / "b")
    assert first.read_bytes() == second.read_bytes()


def test_every_card_id_is_exactly_one_tile(built):
    _, _, page = built
    cards = BEG.load_cards(CATALOG)
    tile_ids = re.findall(r'<article class="tile[^"]*" data-id="([^"]+)"', page)
    assert sorted(tile_ids) == sorted(c["id"] for c in cards)
    assert len(tile_ids) == len(set(tile_ids))


def test_a_card_without_a_golden_shows_the_no_proof_marker(built):
    _, _, page = built
    cards, _ = BEG.split_recipes(BEG.load_cards(CATALOG))
    bare = [c for c in cards if BEG.resolve_proof(c["proof"].get("golden"), FRAMES)[0] is None]
    assert bare, "the catalogue has no card without a golden to pin"
    for c in bare:
        assert BEG.NO_PROOF_MARKER in tile_of(page, c["id"])


def test_the_verdict_stack_tile_lists_six_phases(built):
    """Five since P61 T7; six since P61 T7c / E99 s59-s61 - the GATHER before the burst (the vertical form's)."""
    _, _, page = built
    assert len(re.findall(r'<li class="phase">', tile_of(page, VERDICT_ID))) == 6


def test_no_network_string_outside_examples_and_blends(built):
    _, _, page = built
    stripped = re.sub(r'<pre class="example">.*?</pre>', "", page, flags=re.S)
    stripped = re.sub(r'<li class="blend">.*?</li>', "", stripped, flags=re.S)
    stripped = re.sub(r'data-search="[^"]*"', "", stripped)
    assert "http://" not in stripped and "https://" not in stripped


def test_the_counts_line_names_every_status_and_the_proof_tallies(built):
    _, line, page = built
    cards, recipes = BEG.split_recipes(BEG.load_cards(CATALOG))
    assert line.startswith(f"{len(cards)} cards")
    assert f"recipes {len(recipes)}" in line
    for label in (*BEG.STATUSES, "with golden", "with test", "no proof"):
        assert label in line
    assert BEG.esc(line) in page


def test_a_resolved_golden_is_copied_with_its_proof_strip(tmp_path):
    frames = tmp_path / "frames"
    frames.mkdir()
    for stem in ("surf", "surf@proof-a", "surf@proof-b", "surf@flag-x", "other"):
        (frames / f"{stem}.png").write_bytes(b"\x89PNG" + stem.encode())
    cards = [
        {"id": "a:one", "axis": "a", "token": "one", "title": "One", "does": "d", "status": "live",
         "proof": {"golden": "surf", "test": None}, "author": {"example": "'one'", "check": "none"}},
        {"id": "a:two", "axis": "a", "token": "two", "title": "Two", "does": "d", "status": "planned",
         "proof": {"golden": "missing", "test": "t.py::x"}},
    ]
    catalog = tmp_path / "cat.jsonl"
    catalog.write_text("\n".join(json.dumps(c) for c in cards) + "\n", encoding="utf-8")
    index, line = BEG.build(catalog, frames, tmp_path / "out")
    page = index.read_text(encoding="utf-8")
    copied = sorted(p.name for p in (tmp_path / "out" / BEG.FRAMES_SUBDIR).iterdir())
    assert copied == ["surf.png", "surf@proof-a.png", "surf@proof-b.png"]
    one = tile_of(page, "a:one")
    assert 'loading="lazy"' in one and "surf%40proof-a.png" in one and BEG.NO_PROOF_MARKER not in one
    two = tile_of(page, "a:two")
    assert BEG.NO_PROOF_MARKER in two and "golden missing not found" in two
    assert "with golden 1 | with test 1 | no proof 0" in line


def test_every_recipe_is_one_tile_in_its_own_section_with_its_members_in_order(built):
    _, _, page = built
    _, recipes = BEG.split_recipes(BEG.load_cards(CATALOG))
    assert recipes, "the catalogue has no recipe to pin"
    section = re.search(r'<section class="axis" id="axis-recipe">.*?</section>', page, re.S)
    assert section, "no recipes section"
    for record in recipes:
        tile = tile_of(section.group(0), record["id"])
        offsets = re.findall(r'<li class="member"><b>([^<]+)</b> <code>([^<]+)</code>', tile)
        assert [c for _, c in offsets] == [m["card"] for m in record["members"]]
        assert record["status"] in tile and f"count {record['count']}" in tile
    assert f'recipes ({len(recipes)})' in page


def test_a_member_shows_the_proof_frame_of_the_card_it_names(built):
    _, _, page = built
    cards, recipes = BEG.split_recipes(BEG.load_cards(CATALOG))
    by_id = {c["id"]: c for c in cards}
    framed = [(r, m) for r in recipes for m in r["members"]
              if BEG.resolve_proof(((by_id.get(m["card"]) or {}).get("proof") or {}).get("golden"), FRAMES)[0]]
    assert framed, "no member of any recipe has a card with a golden"
    record, member = framed[0]
    golden = BEG.resolve_proof(by_id[member["card"]]["proof"]["golden"], FRAMES)[0]
    assert BEG.img_src(golden) in tile_of(page, record["id"])


def test_a_recipe_tile_is_not_counted_as_a_card(tmp_path):
    records = [
        {"id": "a:one", "axis": "a", "token": "one", "title": "One", "does": "d", "status": "live",
         "proof": {"golden": None, "test": None}, "author": {"example": "'one'", "check": "none"}},
        {"id": "recipe:two", "axis": "recipe", "title": "Two", "does": "d", "status": "proven", "count": 3,
         "acts": ["EXPLAINS"], "window_s": 6.0, "aliases": [], "dials": {}, "proof": None,
         "members": [{"card": "a:one", "offset_s": 0.0, "role": "r1", "title": "One"},
                     {"card": "a:nope", "offset_s": 1.0, "role": "r2", "title": None}]},
    ]
    catalog = tmp_path / "cat.jsonl"
    catalog.write_text("\n".join(json.dumps(r) for r in records) + "\n", encoding="utf-8")
    index, line = BEG.build(catalog, tmp_path / "frames", tmp_path / "out")
    page = index.read_text(encoding="utf-8")
    assert line.startswith("1 cards") and "recipes 1" in line
    tile = tile_of(page, "recipe:two")
    assert "no card of that id" in tile and "count 3 (a grammar)" in tile
    assert BEG.NO_PROOF_MARKER in tile


def test_callable_false_renders_its_why_as_a_warning(tmp_path):
    card = {"id": "a:x", "axis": "a", "token": "x", "title": "X", "does": "d", "status": "declared",
            "proof": {"golden": None, "test": None}, "callable": {"today": False, "why": "no compiler path"}}
    html_text = BEG.render_card(card, tmp_path)
    assert '<p class="warn">not callable today: no compiler path</p>' in html_text


# ---------------------------------------------------------------- the catalogue is ensured (P63 T2)

import docs_layers as DL  # noqa: E402  (the table the gallery ensures the catalogue through)

CARD = {"id": "dock_payload:stack", "axis": "dock_payload", "token": "stack", "status": "live",
        "title": "TITLE", "does": "it does the thing", "aliases": [], "phases": [],
        "lives": {"form": "inline", "path": "docs/alpha.mjs", "symbol": "drawStack"}}

BUILDER = """import json, sys
from pathlib import Path

repo = Path(sys.argv[sys.argv.index("--repo") + 1])
record = json.loads(Path(sys.argv[0]).with_name("record.json").read_text(encoding="utf-8"))
(repo / "docs").mkdir(parents=True, exist_ok=True)
(repo / "docs/EFFECTS-CATALOG.jsonl").write_text(json.dumps(record) + "\\n", encoding="utf-8")
(repo / "docs/EFFECTS-CATALOG.md").write_text("# catalogue", encoding="utf-8")
print("fake catalogue: written")
"""


@pytest.fixture()
def fake_repo(tmp_path: Path, monkeypatch) -> Path:
    """A miniature repo with a FAKE catalogue builder; `BEG.ROOT` points at it for the test.

    The gallery is build output and so is its input, so the page must never be generated from a stale
    catalogue. The real checkout is never rebuilt by a test."""
    repo = tmp_path / "repo"
    scripts = repo / DL.SCRIPTS_REL
    scripts.mkdir(parents=True)
    (scripts / DL.SENTINEL).write_text("import sys", encoding="utf-8")   # the sentinel: ensure is live
    (scripts / "build_effects_catalog.py").write_text(BUILDER, encoding="utf-8")
    (scripts / "record.json").write_text(json.dumps({**CARD, "title": "The REBUILT card"}),
                                         encoding="utf-8")
    (repo / "docs").mkdir()
    (repo / BEG.CATALOG_REL).write_text(json.dumps({**CARD, "title": "The STALE card"}) + "\n",
                                        encoding="utf-8")
    monkeypatch.setattr(BEG, "ROOT", repo)
    return repo


def test_the_page_is_generated_from_a_rebuilt_catalogue_not_a_stale_one(fake_repo: Path, tmp_path, capsys):
    # Act
    code = BEG.main(["--catalog", str(fake_repo / BEG.CATALOG_REL), "--frames", str(tmp_path / "frames"),
                     "--out", str(tmp_path / "out")])

    # Assert
    assert code == 0
    page = (tmp_path / "out/index.html").read_text(encoding="utf-8")
    assert "The REBUILT card" in page and "The STALE card" not in page
    assert DL.stored_digest(fake_repo, BEG.CATALOG_LAYER)


def test_a_catalogue_that_is_not_this_repos_own_artifact_is_never_rebuilt(fake_repo: Path, tmp_path):
    # Arrange
    mine = tmp_path / "mine.jsonl"
    mine.write_text(json.dumps(CARD) + "\n", encoding="utf-8")

    # Act / Assert
    assert BEG.ensure_catalog(mine) == []
    assert not (fake_repo / DL.CACHE_REL).exists()


def test_a_tree_with_no_builders_in_it_is_never_rebuilt(tmp_path, monkeypatch):
    # Arrange
    repo = tmp_path / "bare"
    (repo / "docs").mkdir(parents=True)
    (repo / BEG.CATALOG_REL).write_text(json.dumps(CARD) + "\n", encoding="utf-8")
    monkeypatch.setattr(BEG, "ROOT", repo)

    # Act / Assert
    assert BEG.ensure_catalog(repo / BEG.CATALOG_REL) == []
    assert not (repo / DL.CACHE_REL).exists()
