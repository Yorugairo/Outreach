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


# ---------------------------------------------------------------- the project's own outro (E41 / E99 s72)
#
# *"You didn't attach the outro either."* The closing row is the PROJECT's outro row, resolved off its
# own `build_short.py` - READ with `ast`, never run (running it would write the APPROVED cut's files).

BED_SOURCE = '''"""a test bed - never run by the resolver."""
from pathlib import Path

HERE = Path(__file__).resolve().parent
(HERE / "RAN-THE-BED").write_text("the resolver executed this module", encoding="utf-8")

OUTRO = HERE / "outro/outro-v9.mov"
BRAND_LINE = HERE.parents[1] / "channel-assets/brand-line.mp3"
BRAND_GAP, BRAND_TAIL = 0.7, 1.0
OUTRO_S, OUTRO_LEAD = 6.2, 0.1


def shot_table(ws, runtime_s, t_outro):
    clip = lambda name, src=None: f"clip:{name}"
    return [(t_outro, runtime_s, clip("outro-v9.mp4", OUTRO), (0, 0, 0), [], "dip", [])]
'''


def bed_script(project: Path, source: str = BED_SOURCE) -> Path:
    project.mkdir(parents=True, exist_ok=True)
    path = project / G.OUTRO_BED
    path.write_text(source, encoding="utf-8")
    return path


def test_a_project_with_no_build_script_defines_no_outro_and_the_tail_is_unchanged(bed):
    project, build = bed
    assert G.outro_resolver(project, build) is None
    table = generate(project, build)
    assert not str(T.load_rows(table)[-1][2]).startswith("clip:outro"), "nothing is invented"


def test_the_outro_is_READ_off_the_projects_build_script_and_never_run(bed):
    project, build = bed
    bed_script(project)
    outro = G.outro_resolver(project, build)
    assert not (project / "RAN-THE-BED").exists(), "the bed is parsed with ast, never imported or run"
    assert outro["world"] == "clip:outro-v9.mp4", "the NAME the bed's own `clip(..., OUTRO)` call gives it"
    assert outro["exit"] == "dip"
    last = max(float(w.get("end", w.get("end_s", 0)) or 0) for w in G.read_words(build))
    assert outro["at"] == round(last - 0.1, 3) and outro["runtime"] > outro["at"]
    assert "read with ast" in outro["source"] and "outro-v9.mov" in outro["source"]


def test_the_bed_reader_unpacks_a_tuple_assignment_and_a_path_off_HERE(tmp_path):
    project = tmp_path / "p"
    got = G.bed_constants(bed_script(project), project, G.OUTRO_CONSTS)
    assert got["OUTRO_S"] == 6.2 and got["OUTRO_LEAD"] == 0.1 and got["BRAND_GAP"] == 0.7
    assert got["OUTRO"] == project / "outro/outro-v9.mov"
    assert got["BRAND_LINE"] == project.parents[1] / "channel-assets/brand-line.mp3"


def test_a_bed_missing_the_three_needed_constants_defines_no_outro(bed):
    project, build = bed
    bed_script(project, "OUTRO_S = 6.2\n")       # no OUTRO, no OUTRO_LEAD
    assert G.outro_resolver(project, build) is None


def test_the_generated_base_CLOSES_on_that_outro_row(bed, capsys):
    project, build = bed
    bed_script(project)
    table = generate(project, build)
    rows = T.load_rows(table)
    outro = G.outro_resolver(project, build)
    assert rows[-1][2] == "clip:outro-v9.mp4" and rows[-1][5] == "dip"
    assert (round(rows[-1][0], 2), round(rows[-1][1], 2)) == (round(outro["at"], 2), round(outro["runtime"], 2))
    assert round(rows[-2][1], 2) == round(outro["at"], 2), "the row before it ends at t_outro"
    doc = (build / G.BASE_DOC_NAME).read_text(encoding="utf-8")
    assert "the cut CLOSES on the project's own outro row" in doc and "E41" in doc


# ---------------------------------------------------------------- the cues bound to what fires (E99 s72)

def cue(slot: str, at: float) -> dict:
    return {"slot": slot, "at": at, "gain": 0.12, "variants": {"A": "x.mp3"}}


def sounded(build: Path, cues: list[dict]) -> Path:
    """A BUILT build: a compiled timeline whose one page leaves on the cut, and a cue plan claiming a
    whirl over it - the base's own fault, in miniature."""
    timeline = {"scenes": [{"scene_id": "s01", "span": [0.0, 10.0], "exit": "cut", "docks": [],
                            "world": {"page": {"builder": "dense-line", "variant": "line",
                                               "enter": "spiral", "exit": "cut"}}}],
                "evidence": {}, "sound": list(cues)}
    (build / G.BASE_TIMELINE_NAME).write_text(json.dumps(timeline), encoding="utf-8")
    (build / G.CUE_PLAN_NAME).write_text(json.dumps({"note": "the bed's dials", "cues": list(cues)}),
                                         encoding="utf-8")
    return build / G.BASE_TIMELINE_NAME


def test_bind_cues_drops_the_whirl_the_frame_never_plays_and_keeps_the_spiral(bed, capsys):
    project, build = bed
    sounded(build, [cue("page enter 1 (spiral)", 0.0), cue("page retract 1 (whirl)", 7.8)])
    assert G.main([str(project), str(build), "--bind-cues"]) == 0
    out = capsys.readouterr().out
    assert "| cue | at | claims | does it fire there? |" in out, "the audit is the evidence"
    assert "DROPPED page retract 1 (whirl)" in out and "no `page retract (whirl)` fires" in out
    timeline = json.loads((build / G.BASE_TIMELINE_NAME).read_text(encoding="utf-8"))
    plan = json.loads((build / G.CUE_PLAN_NAME).read_text(encoding="utf-8"))
    assert [c["slot"] for c in timeline["sound"]] == ["page enter 1 (spiral)"]
    assert [c["slot"] for c in plan["cues"]] == ["page enter 1 (spiral)"]
    assert plan["note"] == "the bed's dials", "the bed's own dials are kept"
    assert "E99 s72" in plan["bound"]


def test_bind_cues_refuses_a_build_that_was_never_compiled(bed, capsys):
    project, build = bed
    assert G.main([str(project), str(build), "--bind-cues"]) == 1
    assert "the cues are bound to what the COMPILED timeline plays" in capsys.readouterr().err


# --- THE APPROVED CUT IS REFUSED BY NAME (the sixth pass' review, finding 1) ---------------------
# `--bind-cues` is a WRITER: it rewrites `<build>/SOUND-PLAN.json` and the compiled timeline's own
# `sound` in place. `build` is whatever the CLI is handed and `--timeline` is a free string, so
# `... tokyo-tea-break/build-short --bind-cues --timeline timeline.json` would have rewritten the
# APPROVED cut's timeline with cues dropped. The lab refuses exactly this by name
# (`lab_build.REFUSED_PREFIX`, `lab_build.refuse_by_name`); so does this door now.

APPROVED_TIMELINE = {"scenes": [{"scene_id": "s01", "span": [0.0, 10.0], "exit": "cut", "docks": [],
                                 "world": {"page": {"builder": "dense-line", "variant": "line",
                                                    "enter": "spiral", "exit": "cut"}}}],
                     "evidence": {},
                     "sound": [{"slot": "page retract 1 (whirl)", "at": 7.8, "gain": 0.12}]}


@pytest.mark.parametrize("where", ["build-short", "build-short-t11", "build-short/candidates/fast"])
def test_bind_cues_refuses_an_approved_or_watched_build_by_name_and_writes_nothing(bed, capsys, where):
    import lab_build as LB
    project, _build = bed
    assert where.split("/")[0].startswith(LB.REFUSED_PREFIX), "the dirs the lab itself refuses"
    approved = project / where
    approved.mkdir(parents=True, exist_ok=True)
    tl = approved / "timeline.json"
    tl.write_text(json.dumps(APPROVED_TIMELINE, indent=1), encoding="utf-8")
    before = tl.read_bytes()
    assert G.main([str(project), str(approved), "--bind-cues", "--timeline", "timeline.json"]) == 1
    err = capsys.readouterr().err
    assert LB.REFUSED_PREFIX in err and "the approved cut and every watched variant beside it" in err, err
    assert tl.read_bytes() == before, "the approved cut's timeline is byte-identical"
    assert not (approved / G.CUE_PLAN_NAME).exists(), "and nothing else was written beside it"


def test_bind_cues_still_binds_a_private_build(bed, capsys):
    """The guard is by NAME - a private build dir is bound exactly as before."""
    project, build = bed
    sounded(build, [cue("page enter 1 (spiral)", 0.0), cue("page retract 1 (whirl)", 7.8)])
    assert G.main([str(project), str(build), "--bind-cues"]) == 0
    assert "DROPPED page retract 1 (whirl)" in capsys.readouterr().out


# --- THE BED READER NEVER TRACEBACKS (the sixth pass' review, finding 6) -------------------------

@pytest.mark.parametrize("subscript, name", [("99", "an index past the project's own parents"),
                                             ('"one"', "a subscript that is not an int")])
def test_a_path_the_reader_cannot_evaluate_is_absent_not_a_traceback(tmp_path, subscript, name):
    project = tmp_path / "p"
    src = BED_SOURCE.replace("HERE.parents[1]", f"HERE.parents[{subscript}]")
    got = G.bed_constants(bed_script(project, src), project, G.OUTRO_CONSTS)
    assert "BRAND_LINE" not in got, f"{name}: the caller names what it could not read"
    assert got["OUTRO_S"] == 6.2 and got["OUTRO"] == project / "outro/outro-v9.mov", "the rest still reads"


def test_a_bed_whose_brand_line_cannot_be_read_still_resolves_its_outro(bed, tmp_path):
    project, build = bed
    src = BED_SOURCE.replace("HERE.parents[1]", "HERE.parents[99]")
    bed_script(project, src)
    outro = G.outro_resolver(project, build)
    assert outro is not None and outro["brand_line_at"] is None


# --- A MISSING ffprobe IS NOT A CRASH (the sixth pass' review, finding 7) ------------------------

@pytest.mark.parametrize("exc", [FileNotFoundError(2, "No such file or directory: 'ffprobe'"),
                                 OSError("ffprobe died"), ValueError("could not convert string to float: 'N/A'")])
def test_an_unreadable_brand_line_duration_reads_as_zero_and_is_named_in_the_source(bed, monkeypatch, exc):
    project, build = bed
    bed_script(project, BED_SOURCE.replace('HERE.parents[1] / "channel-assets/brand-line.mp3"',
                                           'HERE / "brand-line.mp3"'))
    (project / "brand-line.mp3").write_bytes(b"not audio, and ffprobe is not here either")

    def boom(_path):
        raise exc

    monkeypatch.setattr(G.A, "probe_duration", boom)
    outro = G.outro_resolver(project, build)
    assert outro is not None, "a duration the tool cannot read is 0.0, never a crash"
    assert "brand line duration unreadable" in outro["source"] and str(exc) in outro["source"], outro["source"]
    assert outro["brand_line_at"] is None, "no line was measured, so none is claimed"


def test_the_kit_and_the_cli_carry_ONE_runtime_tolerance():
    """`shapes.OUTRO_RUNTIME_EPS` and `EPS_RUNTIME` are one dial written twice (as DIP_S is) - the
    resolver reconciles the clock and the build with it, and `check_outro` refuses past it."""
    from authoring import shapes as SH
    assert SH.OUTRO_RUNTIME_EPS == G.EPS_RUNTIME
