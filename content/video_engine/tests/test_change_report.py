"""P51 T6 - the change report: what a human or a flash agent changed, as the agent sees it.

Two layers are proven here.

The GRAMMAR, on synthetic rows and a synthetic pair of sidecars: one line per field in row order,
the two EFFECTIVE values (the authored 0.335, not the sidecar that does not carry it), an explicit
`null` said as an edit, a word-form `at` shown as the word and the second it resolved to, and the
instants of the timeline diff attributed to the key that explains them.

The WHOLE PATH, on a Tokyo side build (skipped when there is none): three hand edits - the record's
`centre_y` down to 0.30, the species `s04.species.3`'s `at` moved onto the word "pledged", and
`s02.camera` turned off - compiled into a TEMP COPY of the build, and the report run against an
empty sidecar. The build AND the authored shot table are copied first and the compile block
re-pointed at the copies: the side builds and the episode's table are live files that the
operator's own agents rebuild, and a fixture that reads them in place is a fixture that moves.
"""
from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
import authoring.table as T  # noqa: E402
import build_scene_timeline_f as C  # noqa: E402
import change_report as CR  # noqa: E402

PROJECT = ROOT / "content/video_engine/projects/systems-and-blowups/tokyo-tea-break"
TL_NAME = "tokyo-short.timeline.json"
SOURCE = next((PROJECT / n for n in ("build-short-t6", "build-short-t0") if (PROJECT / n / TL_NAME).is_file()), None)
RECORD = "s04.dock.dock-k-pledge-record"
SPECIES = "s04.species.3"
CAMERA = "s02.camera"
# THE OPERATOR'S THREE HAND EDITS (human gate 2): a box moved, a species moved onto a word, a camera off.
EDITS = {RECORD: {"centre_y": 0.30}, SPECIES: {"at": {"word": "pledged"}}, CAMERA: None}
MAX_CROPS, CHECK_MAX = 6, 4   # the report is frames and renders: the test bounds both


def _browser_ok() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _browser_ok(), reason="playwright chromium not installed")
needs_tokyo = pytest.mark.skipif(SOURCE is None, reason=f"no Tokyo side build under {PROJECT}")


# ---- the grammar ---------------------------------------------------------------------------------------------------

def test_the_diff_line_formatter_reads_as_one_field_moving():
    """One line, one field, both values - the formatter alone, on a synthetic pair."""
    assert (CR.diff_line("s04.dock.dock-k-pledge-record.centre_y", (True, 0.335), (True, 0.30), "added")
            == "- s04.dock.dock-k-pledge-record.centre_y: 0.335 -> 0.3 [added]")
    assert (CR.diff_line("s04.species.3.at", (True, 50.3), (True, 55.31), "changed", "pledged")
            == '- s04.species.3.at: 50.3 -> 55.31 ("pledged") [changed]')
    assert (CR.diff_line("s02.camera", (True, {"keys": [], "attention": "landings"}), (True, None), "added")
            == '- s02.camera: {"keys": [], "attention": "landings"} -> null [added]')
    assert (CR.diff_line("s03.exit", (False, None), (True, "dip"), "added")
            == '- s03.exit: (unset) -> "dip" [added]')
    assert (CR.diff_line("s03.exit", (True, "dip"), (False, None), "removed")
            == '- s03.exit: "dip" -> (unset) [removed]')


def test_the_sidecar_diff_is_one_line_per_field_in_row_order():
    """Added, removed and changed, each with the value the compile actually saw - and the rows in
    the order the compiler numbers them, whatever order the sidecar's keys arrive in."""
    before_sc = {RECORD: {"centre_y": 0.32}, "s03.exit": "dip"}
    after_sc = {SPECIES: {"at": {"word": "pledged"}}, CAMERA: None, RECORD: {"centre_y": 0.30}}
    before = {f"{RECORD}.centre_y": 0.32, f"{SPECIES}.at": 50.3, CAMERA: {"keys": []}, "s03.exit": "dip"}
    after = {f"{RECORD}.centre_y": 0.30, f"{SPECIES}.at": 55.31}
    resolve = lambda d: (lambda leaf: (leaf in d, d.get(leaf)))   # noqa: E731 - the test's stand-in for the rows
    rows = CR.sidecar_diff(before_sc, after_sc, resolve(before), resolve(after))
    assert [r["line"] for r in rows] == [
        '- s02.camera: {"keys": []} -> null [added]',
        '- s03.exit: "dip" -> (unset) [removed]',
        '- s04.dock.dock-k-pledge-record.centre_y: 0.32 -> 0.3 [changed]',
        '- s04.species.3.at: 50.3 -> 55.31 ("pledged") [added]',
    ]
    assert [r["key"] for r in rows] == [CAMERA, "s03.exit", RECORD, SPECIES]
    assert [r["state"] for r in rows] == ["added", "removed", "changed", "added"]


def test_a_field_that_resolves_to_the_same_value_is_not_a_change():
    same = {f"{RECORD}.centre_y": 0.30}
    resolve = lambda d: (lambda leaf: (leaf in d, d.get(leaf)))   # noqa: E731
    assert CR.sidecar_diff({RECORD: {"centre_y": 0.30}}, {RECORD: {"centre_y": 0.30}},
                           resolve(same), resolve(same)) == []


def test_the_effective_value_is_read_off_the_rows_not_off_the_sidecar():
    """`centre_y: 0.335 -> 0.30`: the left side is the AUTHORED table's, which no sidecar carries."""
    rows = [(0.0, 10.0, "plate-x;idle=drift", (0, 0, 0),
             [("dock-k", 0, 4.0, 9.0, {"centre": True, "centre_y": 0.335})], None,
             [{"kind": "chart_to", "at": 5.0, "dur": 1.0, "to": "park", "scale": 0.5, "anchor": "top"}],
             {"keys": [], "attention": "landings"})]
    ids = C.row_ids(rows)
    assert ids == {"s01": 0}
    assert CR.effective(rows, ids, "s01.dock.dock-k.centre_y") == (True, 0.335)
    assert CR.effective(rows, ids, "s01.dock.dock-k.centre_x") == (False, None)
    assert CR.effective(rows, ids, "s01.species.0.at") == (True, 5.0)
    assert CR.effective(rows, ids, "s01.species.4.at") == (False, None)
    assert CR.effective(rows, ids, "s01.plate.idle") == (True, "drift")
    assert CR.effective(rows, ids, "s01.exit") == (False, None)
    assert CR.effective(rows, ids, "s01.camera") == (True, {"keys": [], "attention": "landings"})
    assert CR.effective(rows, ids, "s09.camera") == (False, None)


def test_the_instants_are_attributed_to_the_key_that_explains_them():
    """The determinism check's diff, read as the agent reads it: which key moved this frame."""
    changed = [(1.99, "s02 scene changed"), (38.96, "s02 span end"),
               (55.31, f"s04 dock dock-k-pledge-record enter"), (56.71, "s04 species chart_to"),
               (9.09, "s03 dock dock-c-blue-ties-panel enter")]
    by_key, other = CR.instants_by_key([CAMERA, RECORD, SPECIES], changed, {SPECIES: "chart_to"})
    assert [t for t, _w in by_key[CAMERA]] == [1.99, 38.96]
    assert [t for t, _w in by_key[RECORD]] == [55.31]
    assert [t for t, _w in by_key[SPECIES]] == [56.71]
    assert other == [(9.09, "s03 dock dock-c-blue-ties-panel enter")]


def test_every_changed_key_gets_a_crop_before_any_key_gets_a_second():
    by_key = {RECORD: [(1.0, "a"), (2.0, "b"), (3.0, "c")], CAMERA: [(4.0, "d"), (5.0, "e")],
              SPECIES: [(6.0, "f")]}
    assert [k for k, _t, _w in CR.crop_plan(by_key, 3)] == [CAMERA, RECORD, SPECIES]
    assert [t for _k, t, _w in CR.crop_plan(by_key, 5)] == [4.0, 1.0, 6.0, 5.0, 2.0]
    assert len(CR.crop_plan(by_key, 99)) == 6
    assert CR.crop_plan({}, 5) == []


def test_the_diff_ignores_the_compiles_own_bookkeeping():
    """`overrides_applied` and the words path name the sidecar and the build DIRECTORY - neither
    moves a frame, and the before build is a copy in a temp dir."""
    tl = {"runtime_s": 10.0, "scenes": [{"scene_id": "s01", "span": [0.0, 10.0]}],
          "overrides_applied": ["s04.plate"], "narration": {"canonical_hash": "abc", "words_path": "b/timeline.json"}}
    other = dict(tl, overrides_applied=[], narration={"canonical_hash": "abc", "words_path": "c/timeline.json"})
    assert CR._picture(tl) == CR._picture(other)
    assert CR._picture(tl)["narration"] == {"canonical_hash": "abc"}
    moved = dict(tl, narration={"canonical_hash": "zzz", "words_path": "b/timeline.json"})
    assert CR._picture(tl) != CR._picture(moved), "a different take IS a change"


# ---- the whole path, on the Tokyo side build -------------------------------------------------------------------------

def _private_copy(dest: Path) -> tuple[Path, Path]:
    """A private build and a FROZEN copy of the authored shot table, with the compile block
    re-pointed at both - so nothing this test compiles can be rewritten under it, and nothing it
    writes lands in the project."""
    block = CR.compile_block(SOURCE)
    ep = (SOURCE / block["episode_dir"]).resolve()
    frozen = dest / "SHOT-TABLE-SHORT.py"
    shutil.copy2(ep / block["shot_table_file"], frozen)
    build = CR.copy_build(SOURCE, dest / "build")
    manifest = json.loads((build / "player.json").read_text(encoding="utf-8"))
    manifest["compile"]["episode_dir"] = os.path.relpath(ep, build).replace("\\", "/")
    manifest["compile"]["shot_table_file"] = os.path.relpath(frozen, ep).replace("\\", "/")
    (build / "player.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    return build, frozen


@pytest.fixture(scope="module")
def three_edits(tmp_path_factory):
    """The operator's three hand edits compiled into a temp COPY of the side build, and the report
    run twice against an empty sidecar (the second run proves the text is a function of the inputs)."""
    quiet = lambda *_a, **_k: None    # noqa: E731
    work = tmp_path_factory.mktemp("change-report")
    build, frozen = _private_copy(work)
    rows = T.load_rows(frozen)
    authored = {leaf: CR.effective(rows, C.row_ids(rows), leaf)
                for leaf in (f"{RECORD}.centre_y", f"{SPECIES}.at", CAMERA)}
    seen = {"table": frozen.read_bytes(), "timeline": (SOURCE / TL_NAME).read_bytes()}
    after = CR.compiled_with(build, EDITS, work / "after", log=quiet)
    empty = work / "empty-sidecar.json"
    empty.write_text("{}", encoding="utf-8")
    runs = [CR.run(after, "against", empty, max_crops=MAX_CROPS, check_max=CHECK_MAX, log=quiet) for _ in range(2)]
    yield {"after": after, "first": runs[0], "second": runs[1], "seen": seen,
           "frozen": frozen, "authored": authored,
           "timeline": json.loads((after / TL_NAME).read_text(encoding="utf-8"))}


@needs_tokyo
@needs_browser
def test_the_three_hand_edits_are_three_diff_lines_in_row_order(three_edits):
    """One line per field, in the order the compiler numbers the rows, each carrying the AUTHORED
    value on its left - read off the frozen table, which no sidecar carries."""
    rep, authored = three_edits["first"], three_edits["authored"]
    assert [d["key"] for d in rep["diff"]] == [CAMERA, RECORD, SPECIES]
    lines = [d["line"] for d in rep["diff"]]
    assert lines[0] == CR.diff_line(CAMERA, authored[CAMERA], (True, None), "added"), lines[0]
    assert lines[0].endswith('-> null [added]') and '"attention"' in lines[0]
    assert lines[1] == (f"- {RECORD}.centre_y: {json.dumps(authored[f'{RECORD}.centre_y'][1])} "
                        f"-> 0.3 [added]"), lines[1]
    assert authored[f"{RECORD}.centre_y"][1] != 0.30, "an edit that changes nothing proves nothing"
    assert rep["path"] == three_edits["after"] / CR.REPORT_NAME
    assert rep["path"].read_text(encoding="utf-8") == rep["text"]


@needs_tokyo
@needs_browser
def test_the_word_form_is_shown_as_the_word_and_the_second_it_resolved_to(three_edits):
    """`at` named by its phrase: the line carries the word AND the second the take says it, and
    that second is the one the compiled species now fires on."""
    rep, authored = three_edits["first"], three_edits["authored"]
    line = next(d["line"] for d in rep["diff"] if d["key"] == SPECIES)
    moved = next(sp for s in three_edits["timeline"]["scenes"] for sp in s.get("species") or []
                 if sp.get("id") == SPECIES)
    assert line == (f"- {SPECIES}.at: {json.dumps(authored[f'{SPECIES}.at'][1])} "
                    f'-> {json.dumps(moved["at"])} ("pledged") [added]'), line
    assert moved["at"] == pytest.approx(55.31, abs=0.02), "the take says \"pledged\" at 55.306"


@needs_tokyo
@needs_browser
def test_every_key_names_the_instants_it_touches_and_carries_a_crop_pair(three_edits):
    rep, after = three_edits["first"], three_edits["after"]
    by_key, _other = CR.instants_by_key([d["key"] for d in rep["diff"]], rep["instants"],
                                        CR.species_kinds(three_edits["timeline"]))
    assert {RECORD, SPECIES, CAMERA} == set(by_key)
    card = next(d for s in three_edits["timeline"]["scenes"] for d in s.get("docks") or [] if d.get("id") == RECORD)
    assert [t for t, _w in by_key[RECORD]] == [card["enter"], card["exit"]], by_key[RECORD]
    assert all(by_key[k] for k in by_key), by_key
    assert {c["key"] for c in rep["crops"]} == {RECORD, SPECIES, CAMERA}
    for c in rep["crops"]:
        for name in ("before", "after", "pair"):
            p = after / CR.CROP_DIR / c["files"][name]
            assert p.is_file() and p.stat().st_size > 0, p
        assert f"{CR.CROP_DIR}/{c['files']['pair']}" in rep["text"]
    # the card's crop is the CARD's box, not the whole frame, and the two frames differ at its exit
    exit_crop = next(c for c in rep["crops"] if c["key"] == RECORD and c["t"] == pytest.approx(card["exit"]))
    assert exit_crop["box"] != [0, 0, 1080, 1920], exit_crop["box"]
    pair = [(after / CR.CROP_DIR / exit_crop["files"][n]).read_bytes() for n in ("before", "after")]
    assert pair[0] != pair[1], "the record moved up the stage: the two crops cannot be the same"


@needs_tokyo
@needs_browser
def test_the_gate_delta_lists_the_rows_that_moved(three_edits):
    """The camera off is a gate reading: M24 counts the pointing species on moving-camera scenes."""
    rep = three_edits["first"]
    assert rep["gate_delta"], "three edits that move five instants move a gate row"
    m24 = next((r for r in rep["gate_delta"] if r.startswith("M24:")), None)
    assert m24 and "3 pointing species" in m24 and "after: 0 pointing species" in m24, rep["gate_delta"]
    assert "## 3. The gate delta (M01-M26, before -> after)" in rep["text"]
    assert "row(s) unchanged." in rep["text"], "the rows that did not move are counted, not listed"


@needs_tokyo
@needs_browser
def test_the_determinism_check_states_its_verdict_at_the_changed_instants(three_edits):
    rep = three_edits["first"]
    section = rep["text"].split("## 4.")[1].split("## 5.")[0]
    assert "| t | why | warm vs cold |" in section
    assert f"verdict: {rep['determinism']}" in section
    assert rep["determinism"].startswith("ok") or rep["determinism"].startswith("mismatch at"), rep["determinism"]


@needs_tokyo
@needs_browser
def test_the_verdict_line_counts_the_fields_the_rows_and_the_instants(three_edits):
    rep = three_edits["first"]
    assert rep["verdict"].startswith(
        f"3 field(s) changed on 3 row(s); {len(rep['instants'])} instant(s); "), rep["verdict"]
    assert len(rep["instants"]) >= 5, rep["instants"]
    assert "gate delta: M" in rep["verdict"] and "determinism: " in rep["verdict"]
    assert rep["text"].rstrip().endswith(rep["verdict"])


@needs_tokyo
@needs_browser
def test_the_report_is_a_function_of_its_inputs(three_edits):
    """The same build, the same sidecar, the same text - the date in the header is the only clock."""
    assert three_edits["second"]["text"] == three_edits["first"]["text"]


@needs_tokyo
@needs_browser
def test_the_report_never_writes_to_the_table_it_reads_or_to_the_build_it_copied(three_edits):
    """`authoring.table.apply_sidecar` rewrites the shot table with the effective rows - which is
    right in a build and wrong in a report ABOUT one, so the report holds it off. Two compiles ran
    over this table (the after and the report's own before) and it has not moved a byte."""
    assert three_edits["frozen"].read_bytes() == three_edits["seen"]["table"]
    assert (SOURCE / TL_NAME).read_bytes() == three_edits["seen"]["timeline"]
    assert (three_edits["after"] / CR.REPORT_NAME).is_file(), "the report goes to the build it is about"
