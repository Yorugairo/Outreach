"""P55 T3: the effects catalogue is generated from the cards, and never copies what it can pull.

The pins: two writes are byte-identical and `--check` passes; editing one card's `does` makes `--check` exit 1; a card
on the `species` axis shows the compiler's SPECIES_WHEN text (injected in the synthetic tree, imported over the real
one); a doctrine cite resolves through DOCS-INDEX while an unresolved cite keeps a null path; dial values are read
from the module's frozen object; a shared alias is refused; the verdict stack keeps all five phases; and every card
file on disk validates against the schema.

P56 T4: the same generator carries the RECIPES. Its pins: a recipe becomes a record on the LAST axis with each
member's title PULLED from the card it names; the card records and their order do not move when a recipe lands;
editing a member's role makes `--check` exit 1; a recipe file that breaks its schema is a CatalogError naming the
file; and every committed recipe validates and resolves. P56 T9 pins the coverage claim: every `wired` card
in the GENERATED layer is a member of some recipe, the kinetics modules excepted (named in a role, never a
member), and a candidate carries no proof and a zero count.
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import jsonschema
import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import build_effects_catalog as BEC  # noqa: E402

CARDS_DIR = ROOT / BEC.CARDS_REL
WHEN = {"SPECIES_WHEN": {"trace": "the sentence NAMES places and flows (injected)"}, "CHART_TO_WHEN": {}}
RULINGS_ROW = {"path": "docs/portable/OPERATOR-RULINGS.md", "line": 1419, "level": 2, "doc": None,
               "heading": "E47 — The dip through black", "lead": "", "labels": [], "terms": []}


def card(axis: str, token: str, **over) -> dict:
    base = {
        "id": f"{axis}:{token}", "axis": axis, "token": token, "title": f"The {token} {axis} card",
        "aliases": [], "does": f"The {token} effect lands on its beat.", "when": None,
        "author": {"key": "a key", "example": f"'{token}'", "check": "none"},
        "lives": {"form": "module", "path": "content/video_engine/scripts/kinetics/w.mjs", "symbol": "W"},
        "doctrine": [], "status": "wired", "proof": {"golden": None, "test": None},
        "callable": {"today": True, "why": None},
    }
    return {**base, **over}


def recipe(slug: str, **over) -> dict:
    base = {
        "schema_version": "effect_recipes.v1", "id": f"recipe:{slug}", "title": f"The {slug} recipe",
        "aliases": [], "acts": ["EXPLAINS"],
        "members": [{"card": "species:trace", "offset_s": 0.0, "role": "the trace hops the map first"},
                    {"card": "exit:dip", "offset_s": 1.5, "role": "the world dips once the hops land"}],
        "does": "The trace hops, then the world dips on the last hop.", "status": "candidate",
        "source": "recipes_r1 s4", "count": 0,
    }
    return {**base, **over}


def write_recipe(repo: Path, doc: dict) -> Path:
    """One recipe file in the tmp tree, beside a copy of the real recipe schema."""
    schema = repo / BEC.RECIPE_SCHEMA_REL
    if not schema.is_file():
        schema.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(ROOT / BEC.RECIPE_SCHEMA_REL, schema)
    path = repo / BEC.RECIPES_REL / f"{doc['id'].split(':', 1)[1]}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    return path


def write_cards(repo: Path, axis: str, cards: list[dict]) -> Path:
    path = repo / BEC.CARDS_REL / f"{axis}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    doc = {"schema_version": "effect_cards.v1", "axis": axis, "cards": cards}
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    return path


@pytest.fixture()
def tree(tmp_path: Path) -> Path:
    """A synthetic repo: the real schema, a species card, an exit card with two cites, a module with dials."""
    schema = tmp_path / BEC.SCHEMA_REL
    schema.parent.mkdir(parents=True)
    shutil.copy(ROOT / BEC.SCHEMA_REL, schema)
    write_cards(tmp_path, "species", [card("species", "trace",
                                           dials={"module": "content/video_engine/scripts/kinetics/w.mjs",
                                                  "object": "W"})])
    write_cards(tmp_path, "exit", [card("exit", "dip", when="the world changes",
                                        doctrine=["E47 s1", "compiler SCENE EXITS comment"])])
    module = tmp_path / "content/video_engine/scripts/kinetics/w.mjs"
    module.parent.mkdir(parents=True, exist_ok=True)
    module.write_text('export const W = Object.freeze({ DIP_S: 0.47, EASE: "linear" });\n', encoding="utf-8")
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs/DOCS-INDEX.jsonl").write_text(json.dumps(RULINGS_ROW, ensure_ascii=False) + "\n",
                                                    encoding="utf-8")
    return tmp_path


def by_id(records: list[dict]) -> dict[str, dict]:
    return {r["id"]: r for r in records}


def test_two_writes_are_byte_identical_and_check_passes(tree):
    # Act
    first = {rel: (tree / rel).read_bytes() for rel in BEC.write(tree, WHEN)}
    second = {rel: (tree / rel).read_bytes() for rel in BEC.write(tree, WHEN)}

    # Assert
    assert first == second
    assert BEC.check(tree, WHEN) == []
    assert all(b"\r\n" not in text for text in first.values())


def test_editing_one_card_does_makes_check_exit_1_naming_the_artifact(tree, monkeypatch, capsys):
    # Arrange
    monkeypatch.setattr(BEC, "compiler_when", lambda repo: WHEN)
    assert BEC.main(["--write", "--repo", str(tree)]) == 0
    path = tree / BEC.CARDS_REL / "exit.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    doc["cards"][0]["does"] = "The dip now does something else entirely."
    path.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    capsys.readouterr()

    # Act
    code = BEC.main(["--check", "--repo", str(tree)])

    # Assert
    out = capsys.readouterr().out.strip().splitlines()
    assert code == 1
    assert len(out) == 1 and out[0].startswith("build_effects_catalog: STALE - docs/EFFECTS-CATALOG")


def test_a_species_card_shows_the_compilers_when_text(tree):
    # Act
    record = by_id(BEC.build(tree, WHEN))["species:trace"]

    # Assert: pulled, never copied - the card on disk carries null
    assert record["when"] == WHEN["SPECIES_WHEN"]["trace"]
    assert record["when_source"].endswith("build_scene_timeline_f.py SPECIES_WHEN")
    assert by_id(BEC.build(tree, WHEN))["exit:dip"]["when"] == "the world changes"


def test_a_cite_resolves_through_the_index_and_an_unresolved_cite_keeps_a_null_path(tree):
    # Act
    doctrine = by_id(BEC.build(tree, WHEN))["exit:dip"]["doctrine"]

    # Assert
    assert doctrine[0] == {"ref": "E47 s1", "path": "docs/portable/OPERATOR-RULINGS.md", "line": 1419}
    assert doctrine[1] == {"ref": "compiler SCENE EXITS comment", "path": None, "line": None}


def test_dial_values_are_read_from_the_modules_frozen_object(tree):
    # Act
    record = by_id(BEC.build(tree, WHEN))["species:trace"]

    # Assert
    assert record["dials_values"] == {"DIP_S": "0.47", "EASE": '"linear"'}
    assert by_id(BEC.build(tree, WHEN))["exit:dip"]["dials_values"] is None


BACKLOG_REL = "docs/content-video-engine/BACKLOG.md"
BACKLOG_TEXT = ("# BACKLOG\n\n## Open rows\n\n| id | row |\n|---|---|\n| **R26-3** | a shorter id |\n"
                "| **R26-30 CLOSED 2026-09-11** | SHIPPED as break_cadence |\n")


def test_a_backlog_row_id_resolves_to_the_rows_real_line_and_a_cite_with_no_match_stays_unresolved(tree):
    # Arrange: the index knows only the BACKLOG title heading (line 1); the rows live on lines 7 and 8
    backlog = tree / BACKLOG_REL
    backlog.parent.mkdir(parents=True, exist_ok=True)
    backlog.write_text(BACKLOG_TEXT, encoding="utf-8")
    title_row = {**RULINGS_ROW, "path": BACKLOG_REL, "line": 1, "level": 1, "heading": "BACKLOG"}
    with (tree / "docs/DOCS-INDEX.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(title_row) + "\n")
    write_cards(tree, "exit", [card("exit", "dip", doctrine=["BACKLOG R26-30", "R26-3", "BACKLOG R26-31",
                                                             "BACKLOG no such section"])])

    # Act
    records = BEC.build(tree, WHEN)
    doctrine = by_id(records)["exit:dip"]["doctrine"]

    # Assert: only a real match counts; the document's first heading is never a fallback
    assert doctrine[0] == {"ref": "BACKLOG R26-30", "path": BACKLOG_REL, "line": 8}
    assert doctrine[1] == {"ref": "R26-3", "path": BACKLOG_REL, "line": 7}
    assert doctrine[2] == {"ref": "BACKLOG R26-31", "path": None, "line": None}
    assert doctrine[3] == {"ref": "BACKLOG no such section", "path": None, "line": None}
    assert BEC.summary(records).endswith("2/4 cites resolved")


def test_a_dials_module_that_does_not_exist_makes_check_exit_1_naming_the_card(tree, monkeypatch, capsys):
    # Arrange
    monkeypatch.setattr(BEC, "compiler_when", lambda repo: WHEN)
    write_cards(tree, "species", [card("species", "trace", dials={"module": "missing/nowhere.mjs", "object": "X"})])

    # Act
    code = BEC.main(["--check", "--repo", str(tree)])

    # Assert
    out = capsys.readouterr().out
    assert code == 1
    assert "species:trace" in out and "missing/nowhere.mjs" in out


def test_a_dials_object_not_exported_by_the_module_is_an_error_naming_the_card(tree):
    # Arrange
    write_cards(tree, "species", [card("species", "trace", dials={
        "module": "content/video_engine/scripts/kinetics/w.mjs", "object": "RENAMED"})])

    # Act / Assert
    with pytest.raises(BEC.CatalogError, match="species:trace.*RENAMED"):
        BEC.build(tree, WHEN)


def test_the_compiler_when_comes_from_the_repo_argument_not_the_import_cache(tree):
    # Arrange: this checkout's compiler is already imported; the tmp repo's compiler says something else
    import build_scene_timeline_f  # noqa: F401
    compiler = tree / BEC.SCRIPTS_REL / f"{BEC.COMPILER}.py"
    compiler.parent.mkdir(parents=True, exist_ok=True)
    compiler.write_text('SPECIES_WHEN = {"trace": "the tmp repo says so"}\nCHART_TO_WHEN = {}\n', encoding="utf-8")

    # Act
    record = by_id(BEC.build(tree))["species:trace"]

    # Assert
    assert record["when"] == "the tmp repo says so"


def test_an_alias_two_cards_share_is_refused_not_kept_on_one(tree):
    # Arrange
    alias = [{"name": "the veil", "source": "operator 2026-09-13"}]
    write_cards(tree, "exit", [card("exit", "dip", aliases=alias), card("exit", "cut", aliases=alias)])

    # Act / Assert
    with pytest.raises(BEC.CatalogError, match="the veil"):
        BEC.build(tree, WHEN)


# --------------------------------------------------------------------------- the recipes (P56 T4)

def test_a_recipe_becomes_a_record_on_the_last_axis_with_its_member_titles_pulled(tree):
    # Arrange
    write_recipe(tree, recipe("trace-then-dip"))

    # Act
    records = BEC.build(tree, WHEN)
    record = by_id(records)["recipe:trace-then-dip"]

    # Assert: the axis is last, and each member's title comes from the CARD, never from the recipe file
    assert BEC.AXIS_ORDER[-1] == "recipe"
    assert [r["id"] for r in records][-1] == "recipe:trace-then-dip"
    assert record["axis"] == "recipe" and record["window_s"] == 6.0
    assert [m["title"] for m in record["members"]] == ["The trace species card", "The dip exit card"]
    assert [m["card"] for m in record["members"]] == ["species:trace", "exit:dip"]
    assert record["proof"] is None and record["count"] == 0


def test_the_card_records_do_not_move_when_a_recipe_lands(tree):
    # Arrange
    before = (tree / BEC.JSONL_REL).read_bytes() if (tree / BEC.JSONL_REL).is_file() else b""
    BEC.write(tree, WHEN)
    cards_only = (tree / BEC.JSONL_REL).read_bytes()
    write_recipe(tree, recipe("trace-then-dip"))

    # Act
    BEC.write(tree, WHEN)
    with_recipe = (tree / BEC.JSONL_REL).read_bytes()

    # Assert: the recipe is APPENDED; every card line is byte-identical
    assert before == b""
    assert with_recipe.startswith(cards_only)
    assert with_recipe[len(cards_only):].startswith(b'{"acts": ["EXPLAINS"], "aliases": [], "axis": "recipe"')


def test_two_writes_with_a_recipe_are_byte_identical_and_check_passes(tree):
    # Arrange
    write_recipe(tree, recipe("trace-then-dip"))

    # Act
    first = {rel: (tree / rel).read_bytes() for rel in BEC.write(tree, WHEN)}
    second = {rel: (tree / rel).read_bytes() for rel in BEC.write(tree, WHEN)}

    # Assert
    assert first == second
    assert BEC.check(tree, WHEN) == []
    assert "## Recipes" in first[BEC.MD_REL].decode("utf-8")


def test_editing_a_members_role_makes_check_exit_1_naming_the_artifact(tree, monkeypatch, capsys):
    # Arrange
    monkeypatch.setattr(BEC, "compiler_when", lambda repo: WHEN)
    path = write_recipe(tree, recipe("trace-then-dip"))
    assert BEC.main(["--write", "--repo", str(tree)]) == 0
    doc = json.loads(path.read_text(encoding="utf-8"))
    doc["members"][1]["role"] = "the world now does something else entirely"
    path.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    capsys.readouterr()

    # Act
    code = BEC.main(["--check", "--repo", str(tree)])

    # Assert
    out = capsys.readouterr().out.strip().splitlines()
    assert code == 1
    assert out[0].startswith("build_effects_catalog: STALE - docs/EFFECTS-CATALOG")


def test_a_recipe_that_breaks_its_schema_is_an_error_naming_the_file(tree):
    # Arrange: one member is not a combination
    write_recipe(tree, recipe("lonely", members=[{"card": "species:trace", "offset_s": 0.0, "role": "alone here"}]))

    # Act / Assert
    with pytest.raises(BEC.CatalogError, match="lonely.json"):
        BEC.build(tree, WHEN)


def test_a_recipe_in_the_wrong_file_is_an_error(tree):
    # Arrange
    doc = recipe("trace-then-dip")
    path = write_recipe(tree, doc)
    path.rename(path.with_name("renamed.json"))

    # Act / Assert
    with pytest.raises(BEC.CatalogError, match="recipe:trace-then-dip"):
        BEC.build(tree, WHEN)


def test_an_alias_two_recipes_share_is_refused(tree):
    # Arrange
    alias = [{"name": "the hop and the veil", "source": "operator 2026-09-13"}]
    write_recipe(tree, recipe("trace-then-dip", aliases=alias))
    write_recipe(tree, recipe("dip-then-trace", aliases=alias))

    # Act / Assert
    with pytest.raises(BEC.CatalogError, match="the hop and the veil"):
        BEC.build(tree, WHEN)


# --------------------------------------------------------------------------- the committed cards

def test_every_card_file_validates_against_the_schema_and_sits_in_its_axis_file():
    # Arrange
    validator = jsonschema.Draft202012Validator(json.loads((ROOT / BEC.SCHEMA_REL).read_text(encoding="utf-8")))
    files = sorted(CARDS_DIR.glob("*.json"))

    # Act
    docs = {path.stem: json.loads(path.read_text(encoding="utf-8")) for path in files}

    # Assert
    assert files
    for stem, doc in docs.items():
        assert [e.message for e in validator.iter_errors(doc)] == [], stem
        assert doc["axis"] == stem and all(c["axis"] == stem for c in doc["cards"])


def test_the_verdict_stack_keeps_all_five_phases_and_the_gather():
    # Act
    doc = json.loads((CARDS_DIR / "dock_payload.json").read_text(encoding="utf-8"))
    stack = next(c for c in doc["cards"] if c["id"] == "dock_payload:stack")

    # Assert: the operator's correction - enter one at a time, focus, recede to the mosaic, idle, burst
    assert stack["title"] == "The verdict stack"
    # P61 T7c / E99 s59-s61: the GATHER before the burst (the vertical form's; the full frame keeps the reference)
    assert [p["name"] for p in stack["phases"]] == ["enter", "focus", "recede", "idle", "gather", "burst"]
    assert "evidence wall" in [a["name"] for a in stack["aliases"]]
    assert stack["phases"][0]["dials"]["translateZ_from_px"] == "-700"


def test_every_recipe_file_validates_and_lands_in_the_catalogue():
    # Arrange
    files = sorted((ROOT / BEC.RECIPES_REL).glob("*.json"))

    # Act
    recipes = BEC.load_recipes(ROOT)

    # Assert
    assert files and len(recipes) == len(files)
    assert {r["id"] for r in recipes} == {f"recipe:{p.stem}" for p in files}  # a mapping, not a sort order:
    # `badge-ladder-embedded.json` sorts before `badge-ladder.json` while its id sorts after (P56 T9)
    records = BEC.recipes_of(BEC.build(ROOT))
    assert [r["id"] for r in records] == [r["id"] for r in recipes]
    assert all(m["title"] or m["card"].startswith("recipe:") for r in records for m in r["members"])


def test_every_wired_card_is_in_a_recipe():
    """P56 T9: compositions are discoverable, but a new card is not a fabricated recipe.

    The count is taken from the GENERATED layer, not from recipes_r1 s4 - s4 is the input, the layer is the claim.
    The kinetics modules are the one exclusion, with their own reason: their `does` says "the viewer sees it only
    through the effects that call it", so a recipe names them in the ROLE of the member they parameterise.
    """
    # Arrange
    records = BEC.build(ROOT)
    cards = [r for r in records if r["axis"] != "recipe"]
    recipes = BEC.recipes_of(records)
    in_a_recipe = {m["card"] for r in recipes for m in r["members"]}
    roles = " | ".join(m["role"] for r in recipes for m in r["members"])

    # Act
    wired = [c["id"] for c in cards if c["status"] == "wired"]
    excluded = sorted(i for i in wired if i.startswith("kinetics:"))
    uncovered = sorted(i for i in wired if i not in in_a_recipe and i not in excluded)

    # These source-bound options and the paper handoff are callable and tested individually,
    # but no source-bound combination has earned a recipe yet. Keep the exception exact:
    # a newly uncomposed wired card still fails this test. P69 T26d's authored prop place and moves
    # (dock_option:place / dock_option:moves, 5c6871c) are tested alone in test_prop_free_placement.py; no committed
    # beat plays them yet, so they wait here rather than in an invented recipe. P69 T8b's panel focus
    # (page_species:panel_focus) is tested alone in test_ledger_panels.py until row 21 plays it. P69 T36's lit stretch
    # (page_species:lit_stretch) is tested alone in test_lit_stretch.py until a recipe composes it (T44's epoch walk).
    assert uncovered == ["dock_option:moves", "dock_option:place", "page_enter:surface", "page_species:lit_stretch",
                         "page_species:panel_focus",
                         "plate_option:bar_style",
                         "plate_option:build", "plate_option:domain", "plate_option:readability",
                         "plate_option:room"], uncovered
    assert excluded == ["kinetics:arap", "kinetics:camera", "kinetics:chartxf", "kinetics:clothoid", "kinetics:contour",
                        "kinetics:ease", "kinetics:homography", "kinetics:ink", "kinetics:labelfit",
                        "kinetics:morph_a", "kinetics:page_surface", "kinetics:spring", "kinetics:squash",
                        "kinetics:stagger", "kinetics:stroke", "kinetics:transitions"]
    # ... and each excluded module stays reachable: it is named in the role of the member it parameterises
    # Labelfit and page_surface are new helper laws, not proven recipe members.
    assert [i for i in excluded if i not in roles and i not in ("kinetics:labelfit", "kinetics:page_surface")] == []
    assert [i for i in excluded if i in in_a_recipe] == [], "a kinetics module is never a member of its own"


def test_a_candidate_recipe_carries_no_proof_and_a_zero_count():
    # Arrange / Act
    candidates = [r for r in BEC.load_recipes(ROOT) if r["status"] == "candidate"]

    # Assert: the candidate rule (P56 T9) - the seed's shape, none of the seed's evidence
    assert candidates
    for recipe in candidates:
        assert "proof" not in recipe and recipe["count"] == 0, recipe["id"]
        # A candidate can also come from a measured private proof (P69 T35), still
        # without an approved-cut count or an in-recipe proof claim.
        assert any(marker in recipe["source"] for marker in
                   ("recipes_r1 s4", "golden", "projects/_proofs/")), recipe["id"]
        assert len(recipe["members"]) >= 2, recipe["id"]


def test_the_real_species_cards_carry_the_compilers_when():
    # Arrange
    import build_scene_timeline_f as B

    # Act
    records = [r for r in BEC.build(ROOT) if r["axis"] in ("species", "page_species")]

    # Assert
    assert records
    assert all(r["when"] == B.SPECIES_WHEN[r["token"]] for r in records)
