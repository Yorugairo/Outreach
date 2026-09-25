"""P72 T3: the recipes carry the rulings - E99 s84 applied to the recipe registry.

The operator ruled P65 HG2's six re-proved recipes on 2026-09-18 (E99 s84, `docs/portable/OPERATOR-RULINGS.md`): two
approved with a note each, four DENIED with the reason each. Pinned here:

- the four denied recipes read `status: denied`, `ruled_by: "E99 s84"` and the operator's words VERBATIM as
  `denied_reason` (each string is checked against the rulings file itself, so a paraphrase fails);
- the schema admits `denied` and refuses a denied recipe with no reason, and a reason on a recipe that is not denied;
- a denied recipe keeps its `proof` and `count` as the RECORD of what was ruled, and the drift gate accepts that for
  `denied` only (a candidate with a proof still FAILs); a proven recipe may never splice a denied one in;
- `effects_catalog_check` counts 11 proven, not 15, with 0 failures, and M38's reader (`gate_one_shot_floor`) takes
  the new set - the denied four are out of the coverage and still in the splice registry;
- the two approved recipes carry the operator's notes verbatim (R26-196's retitle edge beside `read-park-build-write`);
- `page_species:note` lists its `keep` option (R26-219, the card half);
- `melt-then-rewrite` (R26-116) validates against the schema, as a candidate: no approved cut plays it.

The lab's stamp clock (R26-252) is pinned in `test_lab_build.py`.
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import build_effects_catalog as BEC  # noqa: E402
import effects_catalog_check as ECC  # noqa: E402
import gate_one_shot_floor as OSF  # noqa: E402

RECIPES = ROOT / "content/video_engine/effects/recipes"
SCHEMA = ROOT / "content/video_engine/configs/effect_recipe.schema.json"
CARDS = ROOT / "content/video_engine/effects/cards"
RULINGS = ROOT / "docs/portable/OPERATOR-RULINGS.md"
S84 = "E99 s84"

# The operator's words, 2026-09-18 15:39-15:43, on `p65-hg2-the-reproved-set-and-m38` (E99 s84) - verbatim.
DENIED = {
    "card-becomes-the-chart": "off-doctrine: there is no reason to fade/dip the card growth",
    "dock-lands-page-renames": ("off-doctrine: I think we can use our choreography and awareness to better position "
                                "the cards/charts"),
    "plate-dock-wipe": (
        "off-doctrine: You literally docked and wiped then held a still frame for 30 seconds. If it's an evidence dock "
        "it should re-choreograph not to be center, if it's meant to become the plate, then it should be "
        "snapping/zooming in on the evidence layer. we're not gaining anything by wiping to a narrative plate and "
        "docking a barely legible chart over the top, especially when the chart is docked over the center of the "
        "narrative plate, not being scene aware."),
    "spotlight-held-past-the-cut": (
        "reads-as-noise: i'm not even sure what effect you're trying to show here, and i'm not sure when we would "
        "ever want to hold a spotlight past a cut except for maybe on an evidence dock that is staying past a scene."),
}
APPROVED = {
    "badge-ladder": ("good: we should prefer to land on even pills (2 or 4) to maximize real estate used, but even "
                     "numbers is fine if needed"),
    "read-park-build-write": "good",
}
RETITLE_EDGE = "`read-park-build-write`'s retitle clips at the page edge"   # BACKLOG R26-196, the T8b re-proof
PROVEN_BEFORE, PROVEN_AFTER = 15, 11


def recipe(slug: str) -> dict:
    return json.loads((RECIPES / f"{slug}.json").read_text(encoding="utf-8"))


def validator():
    import jsonschema
    return jsonschema.Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8")))


def schema_errors(rec: dict) -> list[str]:
    return [e.message for e in validator().iter_errors(rec)]


# --------------------------------------------------------------------------- the four denied (R26-237)

@pytest.mark.parametrize("slug", sorted(DENIED))
def test_a_denied_recipe_reads_denied_with_the_operators_words_and_the_ruling(slug):
    rec = recipe(slug)
    assert rec["status"] == "denied", f"{slug} still reads {rec['status']!r} - E99 s84 denied it"
    assert rec["ruled_by"] == S84
    assert rec["denied_reason"] == DENIED[slug], f"{slug}: the reason is the operator's words, verbatim"
    assert not schema_errors(rec), schema_errors(rec)


@pytest.mark.skipif(not RULINGS.is_file(), reason="the rulings file is not in this checkout")
@pytest.mark.parametrize("slug", sorted(DENIED) + sorted(APPROVED))
def test_every_quoted_reason_is_in_the_rulings_file_verbatim(slug):
    """The words are the operator's, never a paraphrase: each string is read in the s84 entry itself."""
    s84 = next(line for line in RULINGS.read_text(encoding="utf-8").splitlines() if line.startswith("**E99 s84"))
    words = {**DENIED, **APPROVED}[slug]
    assert f"`{slug}` (*\"{words}\"" in s84, f"{slug}: {words!r} is not quoted verbatim in the s84 entry"


def test_the_schema_admits_denied_and_refuses_it_without_the_reason_or_the_ruling():
    rec = recipe("plate-dock-wipe")
    assert not schema_errors(rec)
    for key in ("denied_reason", "ruled_by"):
        bare = {k: v for k, v in rec.items() if k != key}
        assert schema_errors(bare), f"a denied recipe with no {key} passed the schema"
    proven = recipe("badge-ladder")
    assert not schema_errors(proven)
    assert schema_errors(dict(proven, denied_reason="off-doctrine: a reason on a recipe nobody denied")), (
        "a denied_reason on a proven recipe passed the schema")
    assert schema_errors(dict(recipe("prop-stamped-onto-its-page"), denied_reason="off-doctrine: not denied")), (
        "a denied_reason on a candidate passed the schema")


def test_a_denied_recipe_keeps_its_proof_and_count_as_the_record_and_only_a_denied_one():
    """The coordinator's ruling (P72 T3): keep history. `check_recipe_proof` / `check_recipe_count` accept a proof
    and a count on status `denied` only - a candidate that carries either still FAILs, by name."""
    cards = ECC.load_cards(CARDS)
    denied = dict(recipe("card-becomes-the-chart"), status="denied", ruled_by=S84,
                  denied_reason=DENIED["card-becomes-the-chart"])   # the check's own law, apart from the file's edit
    assert denied.get("proof") and denied.get("count") == 2, "the denied record keeps its proof and its count"
    assert ECC.check_recipe_proof([denied], ROOT, cards) == []
    failures, info = ECC.check_recipe_count([denied])
    assert failures == [] and info == [], "a denied recipe is neither a failure nor a decoration"
    candidate = dict(copy.deepcopy(denied), status="candidate")
    for key in ("denied_reason", "ruled_by"):
        candidate.pop(key, None)
    assert any("a candidate carries a proof" in f for f in ECC.check_recipe_proof([candidate], ROOT, cards))
    assert any("a candidate that fired 2 time(s)" in f for f in ECC.check_recipe_count([candidate])[0])


def test_a_proven_recipe_never_splices_a_denied_one_in():
    """A proven recipe that names a denied one as a member would carry the denied choreography into M38's coverage
    through `recipe_walk.flatten` - the drift gate refuses it by name."""
    recipes = ECC.load_recipes(RECIPES)
    cards = ECC.load_cards(CARDS)
    parent = copy.deepcopy(recipe("badge-ladder"))
    parent["members"][1] = {"card": "recipe:plate-dock-wipe", "offset_s": 2.05, "role": "a denied recipe spliced in"}
    failures = ECC.check_recipe_members([parent] + [r for r in recipes if r["id"] != parent["id"]], cards)
    assert any("recipe:badge-ladder" in f and "recipe:plate-dock-wipe" in f and "denied" in f for f in failures), failures


# --------------------------------------------------------------------------- the counts and the floor's reader

@pytest.fixture(scope="module")
def report():
    return ECC.run(ROOT)


def test_the_drift_gate_counts_eleven_proven_and_no_failures(report):
    assert report.failures == [], report.failures
    assert report.proven == PROVEN_AFTER, f"{report.proven} proven - the four denied are {PROVEN_BEFORE} - 4"
    for slug in DENIED:
        assert not any(f"recipe:{slug} " in line for line in report.info), "a denied recipe is no decoration"


@pytest.fixture(scope="module")
def catalog(tmp_path_factory) -> Path:
    """The catalogue exactly as `build_effects_catalog --write` renders it, into a private file."""
    path = tmp_path_factory.mktemp("catalog") / "EFFECTS-CATALOG.jsonl"
    path.write_text(BEC.render_jsonl(BEC.build(ROOT)), encoding="utf-8")
    return path


def test_m38_reads_the_new_proven_set_and_the_splice_registry_keeps_every_recipe(catalog):
    proven = {r["id"] for r in OSF.load_recipes(catalog)}
    assert len(proven) == PROVEN_AFTER
    registry = OSF.recipe_registry(catalog)
    for slug in DENIED:
        assert f"recipe:{slug}" not in proven, f"M38 still credits the denied recipe {slug}"
        assert registry[f"recipe:{slug}"]["status"] == "denied", "the registry keeps the record, marked"
    for slug in APPROVED:
        assert f"recipe:{slug}" in proven


JAPAN = ROOT / "content/video_engine/projects/systems-and-blowups/japan-tariff-trick"


@pytest.mark.skipif(not (JAPAN / "build-short/japan-short.timeline.json").is_file(),
                    reason="the approved Japan cut's compiled timeline is gitignored build output")
def test_the_approved_japan_cut_reads_its_lower_coverage_and_its_mechanisms_unchanged(catalog):
    """The coordinator's ruling (a): the frozen cut is unchanged (E45); only what its floor reads changes. M38 on the
    approved Japan cut is 0.76 (19 of 25 beats) with the fifteen, 0.48 (12 of 25) with the eleven; M45 reads the beat
    plan, not the recipes, and stays 7 present / 0 absent. The drop is P72-HG1 item 8's, before M38 can FAIL."""
    m = OSF.measure(JAPAN / "build-short", JAPAN, OSF.load_recipes(catalog), registry=OSF.recipe_registry(catalog))
    assert (len(m.recipe_beats), len(m.beats)) == (12, 25)
    for slug in ("card-becomes-the-chart", "dock-lands-page-renames", "spotlight-held-past-the-cut"):
        assert f"recipe:{slug}" not in m.fires or not m.fires[f"recipe:{slug}"]


# --------------------------------------------------------------------------- the two approved (R26-196)

@pytest.mark.parametrize("slug", sorted(APPROVED))
def test_an_approved_recipe_carries_the_operators_note_verbatim(slug):
    rec = recipe(slug)
    assert rec["status"] == "proven" and rec["ruled_by"] == S84
    notes = {n["note"]: n["source"] for n in rec["use_notes"]}
    assert APPROVED[slug] in notes and notes[APPROVED[slug]].startswith(S84)
    assert not schema_errors(rec), schema_errors(rec)


def test_read_park_build_write_carries_the_retitle_edge_beside_the_approval():
    notes = {n["note"]: n["source"] for n in recipe("read-park-build-write")["use_notes"]}
    assert notes.get(RETITLE_EDGE, "").startswith("BACKLOG R26-196")


# --------------------------------------------------------------------------- the note's keep (R26-219) and the melt (R26-116)

def test_the_note_card_lists_its_keep_option():
    cards = json.loads((CARDS / "page_species.json").read_text(encoding="utf-8"))["cards"]
    note = next(c for c in cards if c["id"] == "page_species:note")
    keep = [o for o in note["options"] if o["token"] == "keep"]
    assert len(keep) == 1 and "R26-219" in keep[0]["means"] and "keep: true" in keep[0]["means"]


def test_melt_then_rewrite_validates_as_a_candidate_on_the_compare_streak():
    rec = recipe("melt-then-rewrite")
    assert not schema_errors(rec), schema_errors(rec)
    assert rec["id"] == "recipe:melt-then-rewrite" and rec["status"] == "candidate" and rec["count"] == 0
    assert "proof" not in rec, "a candidate carries no proof - the golden is named in `source`"
    cards = [m["card"] for m in rec["members"]]
    assert cards[0] == "page_species:figure" and "chart_to:compare" in cards
    compare = next(m for m in rec["members"] if m["card"] == "chart_to:compare")
    assert compare.get("option") == "streak", "the melt that RE-WRITES is the streak form (P57 T12b)"
    assert "compare-streak" in rec["source"] and "R26-116" in " ".join(rec.get("backlog") or [])
