"""P65 T2: the enumerated space is FINITE, CLOSED and byte-stable - and every way it can go wrong is refused by name.

The committed `candidates.jsonl` is the cross product of `beat-shapes.json` and nothing else: its count equals the
product computed from the slot tables here (no sampling, no `--n`, no `--fill`), every member resolves to a card the
catalogue carries (with an option that card lists), every record validates against `lab_candidates.v1`, and the five
clocks on every record ARE `gate_motion_density.py`'s own constants.

Each refusal is proved on a tmp copy of the table, the way `test_effects_catalog_drift.py` proves the drift gate: a
plate under M44's six seconds, a light before the page has built, a gap past M16's 2.5 s, a slot table past
MAX_CANDIDATES, a card the catalogue does not carry and an option it does not list. Nothing here renders anything.
"""
from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import gate_motion_density as G  # noqa: E402
import lab_enumerate as LE  # noqa: E402
from authoring import effects as FX  # noqa: E402

SHAPE_IDS = ("plate-carries-a-card", "page-number-lands-at-n", "page-to-page-transform", "return",
             "open-on-the-chart")


# --------------------------------------------------------------------------- fixtures

@pytest.fixture(scope="module")
def table() -> dict:
    return json.loads((ROOT / LE.SHAPES_REL).read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def emitted() -> list[dict]:
    lines = (ROOT / LE.CANDIDATES_REL).read_bytes().decode("utf-8").splitlines()
    return [json.loads(line) for line in lines if line.strip()]


@pytest.fixture(scope="module")
def cards() -> dict[str, dict]:
    return LE.load_cards(ROOT)


@pytest.fixture()
def lab_repo(tmp_path: Path) -> Path:
    """The three files the enumerator reads, copied into a tmp root - the committed artifacts are never touched."""
    repo = tmp_path / "repo"
    for rel in (LE.SHAPES_REL, LE.SCHEMA_REL, FX.CATALOG_REL):
        (repo / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / rel, repo / rel)
    return repo


def shapes_copy(tmp_path: Path, mutate) -> Path:
    """A tmp beat-shapes.json with one thing broken on purpose."""
    doc = json.loads((ROOT / LE.SHAPES_REL).read_text(encoding="utf-8"))
    mutate(doc)
    path = tmp_path / "beat-shapes.json"
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    return path


def shape_of(doc: dict, shape_id: str) -> dict:
    return next(s for s in doc["shapes"] if s["id"] == shape_id)


def slot_of(doc: dict, shape_id: str, slot_name: str) -> dict:
    return next(s for s in shape_of(doc, shape_id)["slots"] if s["name"] == slot_name)


def product_of(shape: dict) -> int:
    """The shape's cross product read straight off the table: cards x offsets per slot, +1 when the slot is optional."""
    total = 1
    for slot in shape["slots"]:
        total *= len(slot["members"]) * len(slot["offsets_s"]) + (1 if slot.get("optional") else 0)
    return total


# --------------------------------------------------------------------------- the table and the space

def test_the_table_carries_the_five_shapes_and_names_its_ceiling(table: dict) -> None:
    assert [s["id"] for s in table["shapes"]] == list(SHAPE_IDS)
    assert str(LE.MAX_CANDIDATES) in table["ceiling"] and "MAX_CANDIDATES" in table["ceiling"]
    assert "data change" in table["description"].lower()
    for shape in table["shapes"]:
        assert shape["does"].strip(), f"{shape['id']} has no one-line `does`"
        assert shape["clocks"], f"{shape['id']} names no clock that binds it"
        for rule in shape["clocks"]:
            assert rule["rule"] in LE.RULES
            assert rule["clock"] in LE.CLOCK_CONSTANTS


def test_the_count_is_the_product_of_the_slot_tables_and_under_the_ceiling(table: dict, emitted: list[dict]) -> None:
    per_shape: dict[str, int] = {}
    for record in emitted:
        per_shape[record["shape"]] = per_shape.get(record["shape"], 0) + 1
    want = {s["id"]: product_of(s) for s in table["shapes"]}
    assert per_shape == want                       # no sampling, no thinning: the WHOLE cross product
    assert len(emitted) == sum(want.values())
    assert len(emitted) <= LE.MAX_CANDIDATES


def test_the_tool_has_no_n_no_fill_and_no_sampling() -> None:
    source = (ROOT / "content/video_engine/scripts/lab_enumerate.py").read_text(encoding="utf-8")
    body = source.split('"""', 2)[-1]              # the prose may SAY "sampling"; the code may not DO it
    assert re.search(r"^\s*(import random|from random)", body, re.M) is None
    for drawn in (".sample(", ".choice(", ".shuffle(", "randint"):
        assert drawn not in body
    for flag in ("--n", "--fill"):
        with pytest.raises(SystemExit):
            LE.main([flag, "3"])


def test_the_docstring_carries_the_reconciliation_with_its_cites() -> None:
    doc = LE.__doc__ or ""
    assert "NOT AN ALLOCATOR" in doc and "recipes.py:1-20" in doc
    assert "PIPELINE.md:33" in doc and "There is no allocator" in doc
    assert "authors no episode" in doc and "E99 s66" in doc and "E99 s68" in doc


# --------------------------------------------------------------------------- every record

def test_every_member_resolves_to_a_card_or_a_listed_option(emitted: list[dict], cards: dict[str, dict]) -> None:
    for record in emitted:
        assert record["members"], record["id"]
        assert record["members"][0]["offset_s"] == 0.0, record["id"]
        for member in record["members"]:
            card = cards.get(member["card"])
            assert card is not None, f"{record['id']} names {member['card']}, which is not in {FX.CATALOG_REL}"
            assert member["role"].strip()
            if "option" in member:
                tokens = [o["token"] for o in (card.get("options") or [])]
                assert member["option"] in tokens, f"{record['id']}: {card['id']} does not list {member['option']}"


def test_every_record_validates_against_lab_candidates_v1(emitted: list[dict]) -> None:
    import jsonschema

    schema = json.loads((ROOT / LE.SCHEMA_REL).read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    for record in emitted:
        assert list(validator.iter_errors(record)) == [], record["id"]
        assert record["status"] == "enumerated"
        assert record["source"].startswith("lab_enumerate beat-shapes.json ")
        assert record["id"].startswith(f"lab:{record['shape']}:")
    assert len({r["id"] for r in emitted}) == len(emitted)


def test_the_clocks_on_every_record_are_the_gate_constants(emitted: list[dict]) -> None:
    want = {
        "m44_plate_s": G.PLATE_MIN_S,
        "m16_gap_s": G.SHORT_PULSE_MAX_S,
        "m12_dock_s": G.OPENING_CHART_HOLD_MAX_S,
        "m11_first_light_s": G.ANNOTATE_TOL_S,
        "page_build_end_s": round(G.PAGE_BUILD_END_S, 3),
    }
    assert LE.clocks() == want
    for record in emitted:
        assert record["clocks"] == want, record["id"]


# --------------------------------------------------------------------------- the refusals

def test_a_plate_under_m44s_six_seconds_is_refused_by_name(tmp_path: Path) -> None:
    path = shapes_copy(tmp_path, lambda d: slot_of(d, "plate-carries-a-card", "exit")
                       .__setitem__("offsets_s", ["m16_gap_s"]))
    with pytest.raises(LE.LabError) as exc:
        LE.build(ROOT, shapes=path)
    assert "plate holds 2.50s" in str(exc.value) and "m44_plate_s = 6.00s" in str(exc.value)
    assert "lab:plate-carries-a-card:" in str(exc.value)


def test_a_light_before_the_build_ends_is_refused_by_name(tmp_path: Path) -> None:
    path = shapes_copy(tmp_path, lambda d: slot_of(d, "page-number-lands-at-n", "light")
                       .__setitem__("offsets_s", ["m16_gap_s"]))
    with pytest.raises(LE.LabError) as exc:
        LE.build(ROOT, shapes=path)
    assert "BEFORE the page has built" in str(exc.value) and "page_build_end_s = 7.40s" in str(exc.value)


def test_a_gap_over_m16s_two_and_a_half_seconds_is_refused_by_name(tmp_path: Path) -> None:
    path = shapes_copy(tmp_path, lambda d: slot_of(d, "plate-carries-a-card", "life")
                       .__setitem__("offsets_s", ["m44_plate_s"]))
    with pytest.raises(LE.LabError) as exc:
        LE.build(ROOT, shapes=path)
    assert "3.50s of screen with no event" in str(exc.value) and "m16_gap_s = 2.50s" in str(exc.value)


def test_a_dock_held_past_m12_is_refused_by_name(tmp_path: Path) -> None:
    path = shapes_copy(tmp_path, lambda d: shape_of(d, "open-on-the-chart")
                       .__setitem__("window_s", "page_build_end_s + m16_gap_s + 2 * m12_dock_s"))
    with pytest.raises(LE.LabError) as exc:
        LE.build(ROOT, shapes=path)
    assert "is held 12.00s" in str(exc.value) and "m12_dock_s = 6.00s" in str(exc.value)


def test_a_slot_table_past_the_ceiling_is_refused_naming_the_shape_and_the_product(tmp_path: Path,
                                                                                   cards: dict[str, dict]) -> None:
    species = sorted(c["id"] for c in cards.values() if c["axis"] == "species")
    pages = sorted(c["id"] for c in cards.values() if c["axis"] == "page_species")

    def blow_up(doc: dict) -> None:
        slot_of(doc, "return", "mark")["members"] = [{"card": cid} for cid in pages]
        slot_of(doc, "return", "light")["members"] = [{"card": cid} for cid in species]

    path = shapes_copy(tmp_path, blow_up)
    with pytest.raises(LE.LabError) as exc:
        LE.build(ROOT, shapes=path)
    said = str(exc.value)
    assert "return pushes the space past MAX_CANDIDATES" in said and str(LE.MAX_CANDIDATES) in said
    assert f"alone is {2 * len(pages) * len(species) * 2}" in said and "mark=" in said and "light=" in said


def test_a_member_the_catalogue_does_not_carry_is_refused_by_name(tmp_path: Path) -> None:
    path = shapes_copy(tmp_path, lambda d: slot_of(d, "return", "light")["members"]
                       .append({"card": "species:limelight"}))
    with pytest.raises(LE.LabError) as exc:
        LE.build(ROOT, shapes=path)
    assert "'species:limelight' is not a card" in str(exc.value) and "return/light" in str(exc.value)


def test_an_option_the_card_does_not_list_is_refused_by_name(tmp_path: Path) -> None:
    path = shapes_copy(tmp_path, lambda d: slot_of(d, "plate-carries-a-card", "arrival")["members"]
                       .append({"card": "arrival:throw", "option": "granite"}))
    with pytest.raises(LE.LabError) as exc:
        LE.build(ROOT, shapes=path)
    assert "does not list the option 'granite'" in str(exc.value)


def test_an_offset_that_is_not_a_clock_expression_is_refused_by_name(tmp_path: Path) -> None:
    path = shapes_copy(tmp_path, lambda d: slot_of(d, "return", "mark")
                       .__setitem__("offsets_s", ["m16_gap_s + about_a_beat"]))
    with pytest.raises(LE.LabError) as exc:
        LE.build(ROOT, shapes=path)
    assert "'about_a_beat', which is not one of the clocks" in str(exc.value)


# --------------------------------------------------------------------------- the artifact

def test_the_write_is_byte_identical_on_a_re_run(lab_repo: Path) -> None:
    first = LE.write(lab_repo)
    once = (lab_repo / LE.CANDIDATES_REL).read_bytes()
    LE.write(lab_repo)
    twice = (lab_repo / LE.CANDIDATES_REL).read_bytes()
    assert once == twice
    assert b"\r\n" not in once and once.endswith(b"\n")
    assert [r["id"] for r in first] == sorted(r["id"] for r in first)
    assert once == (ROOT / LE.CANDIDATES_REL).read_bytes()       # the committed file IS a fresh enumeration
    assert LE.check(lab_repo) is None


def test_check_exits_1_on_a_stale_file_and_prints_the_first_differing_line(lab_repo: Path, capsys) -> None:
    LE.write(lab_repo)
    path = lab_repo / LE.CANDIDATES_REL
    lines = path.read_bytes().decode("utf-8").splitlines()
    record = json.loads(lines[2])
    record["status"] = "survivor"                                 # a hand-edit, the thing --check exists to catch
    lines[2] = json.dumps(record, sort_keys=True, ensure_ascii=False)
    path.write_bytes(("\n".join(lines) + "\n").encode("utf-8"))

    assert LE.main(["--check", "--repo", str(lab_repo)]) == 1
    said = capsys.readouterr().out
    assert "STALE" in said and "line 3" in said and '"status": "survivor"' in said
    assert LE.BUILD_CMD in said


def test_check_names_a_missing_file(lab_repo: Path) -> None:
    assert "is missing" in (LE.check(lab_repo) or "")
    assert LE.main(["--check", "--repo", str(lab_repo)]) == 1
