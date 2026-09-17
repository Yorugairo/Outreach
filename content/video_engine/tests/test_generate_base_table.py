"""THE BASE TABLE CLI (P66 T4): the base on disk, byte-identical on a re-run, and every departure NAMED.

The pins: the CLI writes the kit's own literal and `<build>/BASE-TABLE.md` (the skeleton, the act, the rule per row,
the silent beats, the signature mix beside the approved cuts' measured target) and a second run is byte-identical; a
clean build reports no departures and exits 0; an edited table exits 1 naming the row AND the field; the same edit
named in the project's PRODUCTION-LEDGER.md "Decisions taken without the operator" section in the fixed format exits 0;
a ledger without that section (or without the file) exits 1 saying so; `overrides.json` is layered through the
compiler's own `apply_overrides` and its edit is a departure too; a table NEWER than the plan is never overwritten
without `--force "<reason>"`, and the reason is recorded in BASE-TABLE.md; a plan M41 would fail is refused by name.

The bed is the Tokyo short's AUTHORED plan and take, COPIED into tmp_path - `build-short/` is the approved dir and is
never written into (memory `review-link-frozen-copy`).
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

import generate_base_table as G  # noqa: E402
from authoring import table as T  # noqa: E402

BED = ROOT / "content/video_engine/projects/systems-and-blowups/tokyo-tea-break/build-short"
LEDGER_HEAD = "## Decisions taken without the operator (for the watch)"
EXIT_FIELD = 5


@pytest.fixture()
def bed(tmp_path) -> tuple[Path, Path]:
    """A project and a build dir holding COPIES of the approved bed's plan and take - nothing of the cut's own."""
    project = tmp_path / "a-project"
    build = project / "build-base"
    build.mkdir(parents=True)
    for name in (G.PLAN_NAME, G.WORDS_NAME):
        shutil.copy2(BED / name, build / name)
    return project, build


def run(project: Path, build: Path, *args: str) -> int:
    return G.main([str(project), str(build), "--table", str(build / G.TABLE_NAME), *args])


def generate(project: Path, build: Path, *args: str) -> Path:
    assert run(project, build, *args) == 0
    return build / G.TABLE_NAME


def edit_exit(table: Path) -> tuple[int, str, str]:
    """One field of one row changed the way an agent changes it: the row's exit. -> (row number, base, final)."""
    rows = [list(r) for r in T.load_rows(table)]
    was = rows[0][EXIT_FIELD]
    now = "dip" if was != "dip" else "cut"
    rows[0][EXIT_FIELD] = now
    T.write_shot_table(table, [tuple(r) for r in rows], '"""edited by hand - the first of the two doors."""\n')
    return 1, was, now


def ledger(project: Path, body: str) -> Path:
    path = project / G.LEDGER_NAME
    path.write_text(f"# PRODUCTION LEDGER - a test bed\n\n{body}\n", encoding="utf-8")
    return path


def touch_newer(path: Path, other: Path, seconds: float = 120.0) -> None:
    st = other.stat()
    os.utime(path, (st.st_atime + seconds, st.st_mtime + seconds))


# ---------------------------------------------------------------- the base

def test_the_base_is_written_through_the_kit_and_a_re_run_is_byte_identical(bed, capsys):
    project, build = bed
    table = generate(project, build)
    doc = build / G.BASE_DOC_NAME
    first = (table.read_bytes(), doc.read_bytes())
    out = capsys.readouterr().out
    assert f"{T.SHOT_TABLE_VAR} = " in table.read_text(encoding="utf-8")
    assert "rows |" in out and "silent beats" in out
    rows = T.load_rows(table)
    assert rows and all(isinstance(r, tuple) for r in rows)
    assert run(project, build) == 0
    assert (table.read_bytes(), doc.read_bytes()) == first


def test_the_base_doc_names_the_skeleton_the_act_the_rule_the_silent_beats_and_the_mix(bed):
    project, build = bed
    generate(project, build)
    text = (build / G.BASE_DOC_NAME).read_text(encoding="utf-8")
    rows, why = G.compile_base(build, G.DEFAULT_ASPECT)
    for w in G.SH.rows_why(why):
        assert f"`{w['skeleton']}`" in text and f"`{w['signature']}`" in text
        assert w["rule"].split(";")[0] in text
    silent = G.SH.silent_why(why)
    assert f"## The beats the plan leaves silent ({len(silent)})" in text
    for w in silent:
        assert f"- beat {w['beat']}: {w['sentence']}" in text
    approved = G.approved_mix()
    assert G.MIX_REL in text and str(approved["max_share"]["value"]) in text
    for sig, n in G.signature_mix(why).items():
        assert f"| `{sig}` | {n} |" in text
    assert f"{len(G.SH.event_gaps(rows))} gaps over {G.SH.PULSE_MAX_S} s" in text


def test_a_plan_m41_would_fail_is_refused_by_name(bed, capsys):
    project, build = bed
    records = [json.loads(line) for line in (build / G.PLAN_NAME).read_text(encoding="utf-8").splitlines() if line.strip()]
    records[3]["comparator"] = {"compared_to": ""}
    (build / G.PLAN_NAME).write_text("\n".join(json.dumps(r) for r in records) + "\n", encoding="utf-8")
    assert run(project, build) == 1
    err = capsys.readouterr().err
    assert "M41" in err and f"beat {records[3]['beat']} compares to nothing" in err
    assert not (build / G.TABLE_NAME).exists() and not (build / G.BASE_DOC_NAME).exists()


# ---------------------------------------------------------------- the newer table, and --force

def test_a_table_newer_than_the_plan_is_not_overwritten_without_a_named_reason(bed, capsys):
    project, build = bed
    table = generate(project, build)
    capsys.readouterr()
    edit_exit(table)
    touch_newer(table, build / G.PLAN_NAME)
    edited = table.read_bytes()
    assert run(project, build) == 1
    assert "is NEWER than" in capsys.readouterr().err
    assert table.read_bytes() == edited, "the edit is still there - nothing was written"


def test_force_overwrites_it_and_records_the_reason_in_the_base_doc(bed, capsys):
    project, build = bed
    table = generate(project, build)
    base = table.read_bytes()
    edit_exit(table)
    touch_newer(table, build / G.PLAN_NAME)
    reason = "the plan's beat 3 was rewritten; the hand edit is superseded"
    assert run(project, build, "--force", reason) == 0
    assert table.read_bytes() == base
    assert reason in (build / G.BASE_DOC_NAME).read_text(encoding="utf-8")


def test_an_empty_force_reason_is_refused(bed, capsys):
    project, build = bed
    generate(project, build)
    assert run(project, build, "--force", "  ") == 1
    assert "--force takes a REASON" in capsys.readouterr().err


# ---------------------------------------------------------------- --departures

def test_a_clean_build_has_no_departures(bed, capsys):
    project, build = bed
    generate(project, build)
    capsys.readouterr()
    assert G.main([str(project), str(build), "--departures"]) == 0
    out = capsys.readouterr().out
    assert "0 departures" in out and "CLEAN" in out


def test_an_undocumented_departure_exits_1_naming_the_row_and_the_field(bed, capsys):
    project, build = bed
    table = generate(project, build)
    n, was, now = edit_exit(table)
    ledger(project, f"{LEDGER_HEAD}\n\n1. THE VOICE: the scratch take is the clock, E70 (docs/portable/OPERATOR-RULINGS.md)")
    capsys.readouterr()
    assert G.main([str(project), str(build), "--departures"]) == 1
    out = capsys.readouterr().out
    assert f"row {n} exit: base {was!r} -> final {now!r}" in out
    assert f"UNNAMED: row {n} exit" in out and "1 of 1 departures are unnamed" in out


def test_a_documented_departure_exits_0(bed, capsys):
    project, build = bed
    table = generate(project, build)
    n, was, now = edit_exit(table)
    ledger(project, f"{LEDGER_HEAD}\n\n1. BASE DEPARTURE - row {n} the exit becomes a {now}: the world changes at that "
                    "boundary and a world change is a dip, E47 (docs/portable/OPERATOR-RULINGS.md)")
    capsys.readouterr()
    assert G.main([str(project), str(build), "--departures"]) == 0
    out = capsys.readouterr().out
    assert "1 departures" in out and "OK: all 1 departures are named" in out


def test_a_departure_named_on_another_row_does_not_cover_this_one(bed, capsys):
    project, build = bed
    table = generate(project, build)
    n, _, now = edit_exit(table)
    ledger(project, f"{LEDGER_HEAD}\n\n1. BASE DEPARTURE - row {n + 1} the exit becomes a {now}: the wrong row, "
                    "E47 (docs/portable/OPERATOR-RULINGS.md)")
    capsys.readouterr()
    assert G.main([str(project), str(build), "--departures"]) == 1
    assert f"UNNAMED: row {n} exit" in capsys.readouterr().out


def test_a_ledger_row_in_the_wrong_form_is_named_and_does_not_cover_the_departure(bed, capsys):
    project, build = bed
    table = generate(project, build)
    n, _, now = edit_exit(table)
    ledger(project, f"{LEDGER_HEAD}\n\n1. BASE DEPARTURE row {n} the exit becomes a {now} because the world changes")
    capsys.readouterr()
    assert G.main([str(project), str(build), "--departures"]) == 1
    out = capsys.readouterr().out
    assert "not in the fixed format" in out and f"UNNAMED: row {n} exit" in out


def test_a_ledger_without_the_section_exits_1_saying_so(bed, capsys):
    project, build = bed
    table = generate(project, build)
    edit_exit(table)
    ledger(project, "## The loop (dated)\n\n- 2026-09-17: the take, the plan, the base")
    capsys.readouterr()
    assert G.main([str(project), str(build), "--departures"]) == 1
    assert f'has no "{G.LEDGER_SECTION}" section' in capsys.readouterr().err


def test_no_ledger_at_all_exits_1_saying_so(bed, capsys):
    project, build = bed
    table = generate(project, build)
    edit_exit(table)
    capsys.readouterr()
    assert G.main([str(project), str(build), "--departures"]) == 1
    err = capsys.readouterr().err
    assert G.LEDGER_NAME in err and G.LEDGER_SECTION in err


def test_the_sidecar_is_layered_and_its_edit_is_a_departure_too(bed, capsys):
    """P51 T5's second door: `overrides.json` never touches the table, so only the layered rows show the change."""
    project, build = bed
    table = generate(project, build)
    import build_scene_timeline_f as C
    was = T.load_rows(table)[0][EXIT_FIELD]
    now = "dip" if was != "dip" else "cut"
    (build / G.OVERRIDES_NAME).write_text(json.dumps({f"{C.scene_row_id(0)}.exit": now}), encoding="utf-8")
    untouched = table.read_bytes()
    capsys.readouterr()
    assert G.main([str(project), str(build), "--departures"]) == 1
    out = capsys.readouterr().out
    assert f"row 1 exit: base {was!r} -> final {now!r}" in out
    assert table.read_bytes() == untouched, "--departures never rewrites the table (apply_sidecar does; this does not)"
    ledger(project, f"{LEDGER_HEAD}\n\n1. BASE DEPARTURE - row 1 the exit becomes a {now} through the sidecar: the "
                    "world changes there, E47 (docs/portable/OPERATOR-RULINGS.md)")
    capsys.readouterr()
    assert G.main([str(project), str(build), "--departures"]) == 0


def test_a_row_the_final_table_dropped_is_a_departure(bed, capsys):
    project, build = bed
    table = generate(project, build)
    rows = T.load_rows(table)
    T.write_shot_table(table, list(rows[:-1]), '"""edited by hand: the last row was cut."""\n')
    capsys.readouterr()
    assert G.main([str(project), str(build), "--departures"]) == 1
    out = capsys.readouterr().out
    assert f"row {len(rows)} row: base " in out and G.ABSENT in out
