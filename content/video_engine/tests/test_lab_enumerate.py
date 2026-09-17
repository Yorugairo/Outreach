"""P65 T2: the enumerated space is FINITE, CLOSED and byte-stable - and every way it can go wrong is refused by name.

The committed `candidates.jsonl` is the cross product of `beat-shapes.json` and nothing else: its count equals the
product computed from the slot tables here (no sampling, no `--n`, no `--fill`), every member resolves to a card the
catalogue carries (with an option that card lists), every record validates against `lab_candidates.v1`, and the
eight clocks on every record ARE `gate_motion_density.py`'s own - six constants, and the spiral's and the mount's
LANDINGS, which are `_page_land_offset`'s.

Each refusal is proved on a tmp copy of the table, the way `test_effects_catalog_drift.py` proves the drift gate: a
plate under M44's six seconds, a light before the page has built, a gap past M16's 2.5 s, a slot table past
MAX_CANDIDATES, a card the catalogue does not carry and an option it does not list. Nothing here renders anything.

P65 T3 adds the ENTRY's own clock: a shape that declares `entry_slot` places its light, its hold and its leave
against the instant M11 itself measures the first light from for THAT entry, and T3c makes that instant the gate's
own - `gate_motion_density._page_land_offset` is CALLED, never re-typed. So the four entry kinds (axes 3.0,
spiral 1.6, mount 5.9, built 0.0) are pinned against the gate's own function, against the clocks the record names
(`lp_build_s`, `lp_spiral_in_s`, `mount_land_s`) and against the emitted candidates.
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


def land(enter: str | None, mount_s: float | None = None) -> float:
    """THE JUDGE of every landing in this file: `gate_motion_density._page_land_offset` (:1170-1188) itself, called
    on a page that enters this way - never a number typed here and never the lab's own arithmetic."""
    page: dict = {"enter": enter}
    if mount_s is not None:
        page["mount_s"] = mount_s
    return round(G._page_land_offset({"world": {"page": page}}), 3)


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
            assert rule["clock"] in LE.CLOCK_CONSTANTS or rule["clock"] == LE.ENTRY_TOKEN
            if rule["clock"] == LE.ENTRY_TOKEN or LE.ENTRY_TOKEN in str(rule.get("from") or ""):
                assert shape.get("entry_slot"), f"{shape['id']} measures from the entry and declares no entry_slot"


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
        "lp_build_s": round(G.LP_BUILD_S, 3),
        # the two LANDINGS (P65 T3c): not constants, but the gate's own function, at the player's default mount_s
        "lp_spiral_in_s": land("spiral"),
        "mount_land_s": land("mount"),
    }
    assert LE.clocks() == want
    for record in emitted:
        assert record["clocks"] == want, record["id"]


# --------------------------------------------------------------------------- the light follows the ENTRY (T3)

# the slot each shape lights its ENTRY's landing with (the light / the mark), and the entry slot it follows
LIGHT_SLOT = {"page-number-lands-at-n": "light", "open-on-the-chart": "first_move", "return": "mark"}


def test_the_entry_landings_are_the_ones_m11_measures() -> None:
    """Each entry's landing IS `gate_motion_density._page_land_offset` (:1170-1188) - the gate is the judge, and
    the lab holds no second copy of its arithmetic (P65 T3c)."""
    assert LE.entry_landing_s("page_enter:axes") == land("axes") == round(G.LP_BUILD_S, 3) == 3.0    # :1187-1188
    assert LE.entry_landing_s("page_enter:spiral") == land("spiral") == round(G.LP_SPIRAL_IN_S, 3) == 1.6  # :1183
    assert LE.entry_landing_s("page_enter:built") == land("built") == 0.0                            # :1185-1186
    # :1178-1180 - the mount's landing is mount_s + PAGE_BUILD_END_S - ROLL - SAVOR - FIELD: 5.9 s at the player's
    # default mount_s, 5.5 s on a page carrying mount_s = 2.0. T3 encoded 7.4 here and the thirty mount candidates
    # would have been judged 1.5 s outside M11's tolerance; T3c takes the gate's own number.
    assert LE.entry_landing_s("page_enter:mount") == land("mount") == 5.9
    assert LE.entry_landing_s("page_enter:mount", 2.0) == land("mount", 2.0) == 5.5
    # the compiler stamps a page that follows a page onto its AXES (build_scene_timeline_f.py:2197-2200), and the
    # `return` shape is planted between two pages - so `stamped` lands one BUILD in, like `axes`.
    assert LE.entry_landing_s("page_enter:stamped") == land("axes") == 3.0


def test_the_record_names_the_clock_each_entrys_landing_came_from(emitted: list[dict]) -> None:
    """A candidate is judged on the clocks its RECORD carries (R26-168), so every entry's landing is one of them:
    axes -> lp_build_s, spiral -> lp_spiral_in_s, mount -> mount_land_s, built -> 0.0 (it arrives drawn)."""
    cl = LE.clocks()
    assert cl["lp_spiral_in_s"] == land("spiral") and cl["mount_land_s"] == land("mount")
    assert {"lp_spiral_in_s", "mount_land_s"} <= set(emitted[0]["clocks"])
    for card, clock in (("page_enter:axes", "lp_build_s"), ("page_enter:spiral", "lp_spiral_in_s"),
                        ("page_enter:mount", "mount_land_s"), ("page_enter:stamped", "lp_build_s")):
        assert LE.entry_clock(card) == clock
        assert cl[clock] == LE.entry_landing_s(card)
    assert LE.entry_clock("page_enter:built") is None and LE.entry_landing_s("page_enter:built") == 0.0


def test_an_entry_card_with_no_landing_is_refused_by_name() -> None:
    with pytest.raises(LE.LabError) as exc:
        LE.entry_landing_s("page_enter:morph")
    assert "_page_land_offset" in str(exc.value) and "ENTRY_LANDINGS" in str(exc.value)


def test_the_light_follows_the_entrys_own_build_clock(table: dict, emitted: list[dict]) -> None:
    """One candidate per ENTRY KIND, of each shape that has an entry: its light sits AT that entry's landing."""
    seen: set[str] = set()
    for shape in table["shapes"]:
        slot_name = LIGHT_SLOT.get(shape["id"])
        if slot_name is None:
            assert "entry_slot" not in shape, f"{shape['id']} has an entry slot and no light following it"
            continue
        light_cards = {m["card"] for m in slot_of(table, shape["id"], slot_name)["members"]}
        for entry in slot_of(table, shape["id"], shape["entry_slot"])["members"]:
            card = entry["card"]
            want = land("axes" if card == "page_enter:stamped" else card.split(":")[-1])
            lit = [r for r in emitted if r["shape"] == shape["id"]
                   and any(m["card"] == card and m["offset_s"] == 0.0 for m in r["members"])
                   and any(m["card"] in light_cards and m["offset_s"] == want for m in r["members"])]
            assert lit, f"{shape['id']}: no candidate lights {card} at its own landing {want:.2f}s"
            seen.add(card)
            for record in emitted:                       # and no candidate of the shape lights before that landing
                if record["shape"] != shape["id"] or not any(m["card"] == card for m in record["members"]):
                    continue
                early = [m for m in record["members"] if m["card"] in light_cards and m["offset_s"] < want - 1e-6]
                assert not early, f"{record['id']} lights at {early[0]['offset_s']}s, before {card} has built"
    assert seen == {"page_enter:axes", "page_enter:mount", "page_enter:spiral", "page_enter:built",
                    "page_enter:stamped"}, "every entry kind the table carries is proved"


def test_a_shape_that_measures_from_the_entry_without_one_is_refused_by_name(tmp_path: Path) -> None:
    """`entry_landing` is a clock only where an `entry_slot` says which member it is measured from."""
    path = shapes_copy(tmp_path, lambda d: shape_of(d, "page-to-page-transform")["clocks"]
                       .append({"rule": "after_build_s", "clock": "entry_landing", "slot": "light",
                                "after": "from_page", "note": "a rule with no entry to measure from"}))
    with pytest.raises(LE.LabError) as exc:
        LE.build(ROOT, shapes=path)
    assert "entry_landing" in str(exc.value) and "entry_slot" in str(exc.value)


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
    said = str(exc.value)
    assert "BEFORE the page has built" in said
    # the clock the light is judged against is the ENTRY's own landing, not one number for every page (P65 T3)
    assert f"entry_landing = {land('axes'):.2f}s" in said and f"entry_landing = {land('mount'):.2f}s" in said


def test_a_gap_over_m16s_two_and_a_half_seconds_is_refused_by_name(tmp_path: Path) -> None:
    path = shapes_copy(tmp_path, lambda d: slot_of(d, "plate-carries-a-card", "life")
                       .__setitem__("offsets_s", ["m44_plate_s"]))
    with pytest.raises(LE.LabError) as exc:
        LE.build(ROOT, shapes=path)
    assert "3.50s of screen with no event" in str(exc.value) and "m16_gap_s = 2.50s" in str(exc.value)


def test_a_dock_held_past_m12_is_refused_by_name(tmp_path: Path) -> None:
    path = shapes_copy(tmp_path, lambda d: shape_of(d, "open-on-the-chart")
                       .__setitem__("window_s", "entry_landing + m16_gap_s + 2 * m12_dock_s"))
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
