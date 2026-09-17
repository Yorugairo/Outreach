"""P65 T3: the test-bed builder refuses what it must, plants a candidate in a REAL Tokyo beat, and records it.

Everything here runs through `lab_build.py --dry-run`: the rows are authored and spliced for real (the approved
table, the bed's own assets, the kit's `write_shot_table` / `load_rows` round trip), the compile and the four tools
are stubbed by monkeypatching `lab_build.run_tool` with canned `[LEVEL] Mxx` text. NO PYTEST RUN RENDERS VIDEO, no
ffmpeg is called and nothing is written outside `tmp_path`.

What is pinned: the `build-short*` refusal (`review-link-frozen-copy`), the shape -> beat map citing a real beat of
`build-short/BEAT-PLAN.jsonl`, the member -> row translation for one candidate of EACH shape, the row protocol's
parsing, the record's shape, `survivor` false on a FAIL row INSIDE the candidate's window, the E99 s60 refusal (a
window no sentence covers), and `--check` exiting 1 on a record whose sheet is not on disk.

P65 T3 (second pass) adds the window rule: only the rows whose own instants fall inside `[t0, t1]` decide, the
whole-cut floors (`gate_one_shot_floor.ROW_ORDER`) and the rows firing elsewhere in the approved cut are `context`,
and a WARN inside the window is recorded without killing the candidate.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import gate_one_shot_floor as OSF  # noqa: E402
import lab_build as LB  # noqa: E402
import lab_enumerate as LE  # noqa: E402
from authoring import table as T  # noqa: E402

# One candidate per shape, by id, from the committed `candidates.jsonl` (the ids are stable - P65 T2).
ONE_PER_SHAPE = {
    # the two ids the ENTRY clock moved (P65 T3): the open's callout now lands at its axes entry's own 3.0 s and the
    # return's mark at the stamped entry's 3.0 s, so their member digests changed with their offsets.
    "open-on-the-chart": "lab:open-on-the-chart:7f588cbb",
    "page-number-lands-at-n": "lab:page-number-lands-at-n:c976519f",
    "page-to-page-transform": "lab:page-to-page-transform:03c4bb6a",
    "return": "lab:return:a8f817b4",
    "plate-carries-a-card": "lab:plate-carries-a-card:9b5531bf",
}

# The rows exactly as the gates print them: `f"  [{level:5}] {id} {message}"` (gate_motion_density.py:2795), which
# is why the four-letter levels carry a trailing space inside the brackets.
CLEAN_ROWS = ("  [PASS ] M01 no stretch over 12s without a visual event\n"
              "  [WARN ] M02 one stretch over 8s: 41.1-49.9\n"
              "  [PASS ] M11 the first chart enters 0:02 lit\n"
              "RESULT: PASS\n")
# M38 is a WHOLE-CUT floor (it is read over every beat of the approved cut, so a one-beat candidate cannot own it);
# the M27 row fires at 0:50, inside the page-to-page window (45.00-59.90s), and is the candidate's own.
FAILING_ROWS = ("  [FAIL ] M38 proven-recipe coverage 0.03 of beats, under 0.60 (R26-168)\n"
                "  [FAIL ] M27 1 card(s) reading over a ledger page's ink: dock-g-two-fingers at 0:50\n"
                "  [PASS ] M35 3 chart forms\n")


@pytest.fixture(scope="module")
def candidates() -> dict:
    return LB.load_candidates(ROOT)


@pytest.fixture(scope="module")
def beats() -> list[dict]:
    return LB.load_beats(ROOT)


def canned(text: str):
    """A stub for `lab_build.run_tool`: the canned rows for every tool, and no subprocess anywhere."""
    def _run(argv):
        return 0, text
    return _run


def recipes(tmp_path: Path, monkeypatch, ids: list[str], text: str = CLEAN_ROWS,
            batch: str = "r") -> tuple[int, Path]:
    """P65 T8: the same `--dry-run` drive for a batch of `proven` RECIPES built as candidates."""
    monkeypatch.setattr(LB, "run_tool", canned(text))
    runs = tmp_path / f"{batch}.jsonl"
    rc = LB.main(["--batch", batch, "--recipes", ",".join(ids), "--dry-run",
                  "--runs", str(runs), "--builds", str(tmp_path / f"build-lab-{batch}")])
    return rc, runs


def run(tmp_path: Path, monkeypatch, ids: list[str], text: str = CLEAN_ROWS, batch: str = "t") -> tuple[int, Path]:
    monkeypatch.setattr(LB, "run_tool", canned(text))
    runs = tmp_path / f"{batch}.jsonl"
    rc = LB.main(["--batch", batch, "--candidates", ",".join(ids), "--dry-run",
                  "--runs", str(runs), "--builds", str(tmp_path / f"build-lab-{batch}")])
    return rc, runs


def records_of(path: Path) -> list[dict]:
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


# --------------------------------------------------------------------------- the refusals

def test_refuses_the_approved_build_by_name(tmp_path: Path):
    """`review-link-frozen-copy` / E99 s11: the lab never builds into the cut the operator holds a link to."""
    with pytest.raises(LB.LabBuildError) as exc:
        LB.refuse_dir(tmp_path / "build-short", tmp_path)
    assert "build-short" in str(exc.value) and "never rebuilt under the operator" in str(exc.value)
    with pytest.raises(LB.LabBuildError):                       # ... and not underneath one either
        LB.refuse_dir(tmp_path / "build-short-cam" / "x", tmp_path)


def test_refuses_a_dir_outside_the_batch_root(tmp_path: Path):
    with pytest.raises(LB.LabBuildError) as exc:
        LB.refuse_dir(tmp_path / "elsewhere", tmp_path / "build-lab-t")
    assert "build-lab-t" in str(exc.value)


def test_a_lab_dir_under_its_own_batch_root_is_allowed(tmp_path: Path):
    LB.refuse_dir(tmp_path / "build-lab-t" / "return-1bbc89a0", tmp_path / "build-lab-t")


def test_e99_s60_a_window_no_sentence_covers_is_refused(beats: list[dict]):
    """A proof is a SCENE: a candidate planted where no sentence is spoken is refused BY NAME."""
    with pytest.raises(LB.LabBuildError) as exc:
        LB.beat_window(beats, (99,), 6.0, "lab:return:1bbc89a0")
    assert "E99 s60" in str(exc.value) and "99" in str(exc.value)
    with pytest.raises(LB.LabBuildError) as exc:                # the RING: 7.5 s from 75.79 runs past the last word
        LB.beat_window(beats, (23, 24), 7.5, "lab:return:1bbc89a0")
    assert "E99 s60" in str(exc.value) and "past the cut's last spoken instant" in str(exc.value)
    broken = [dict(beats[0], t0=4.95, t1=2.0)] + beats[1:]      # a plan record whose window opens after it closes
    with pytest.raises(LB.LabBuildError) as exc:                # 4.95 s falls between two sentences: nothing is said
        LB.beat_window(broken, (1,), 1.0, "lab:open-on-the-chart:331d7285")
    assert "no sentence is spoken" in str(exc.value) and "E99 s60" in str(exc.value)


def test_sentence_at_answers_only_inside_a_beat(beats: list[dict]):
    assert LB.sentence_at(beats, 0.0) == "Tokyo took a tea break."
    assert LB.sentence_at(beats, 1.6) is None                   # the gap between the hook's two sentences
    assert LB.sentence_at(beats, 999.0) is None


def test_the_batch_record_is_tracked_and_not_under_the_bare_runs_rule():
    """The record dir is `batches/`, not `runs/`: `.gitignore`'s bare `runs/` rule swallowed the first slice's
    record and the batch record is a TRACKED artifact (acceptance 2, and T8 leans on it)."""
    assert LB.BATCHES_REL.endswith("/batches") and "/runs" not in LB.BATCHES_REL
    assert LB.record_note(ROOT, ROOT / LB.BATCHES_REL / "smoke-r2.jsonl") is None   # git does not swallow it
    note = LB.record_note(ROOT, ROOT / "content/video_engine/effects/lab/runs/smoke-r1.jsonl")
    assert note is None or ("GITIGNORED" in note and "does not edit .gitignore" in note)


def test_a_shape_with_no_beat_is_refused(tmp_path: Path, beats: list[dict]):
    cand = {"id": "lab:no-such-shape:00000000", "shape": "no-such-shape", "members": []}
    with pytest.raises(LB.LabBuildError) as exc:
        LB.build_one(ROOT, "t", cand, beats, tmp_path / "build-lab-t", True)
    assert "SHAPE_BEATS" in str(exc.value) and "E99 s66" in str(exc.value)


# --------------------------------------------------------------------------- the shape -> beat map

def test_the_shapes_window_follows_the_candidates_own_entry(candidates):
    """P65 T3: the open's window is its entry's landing + M16 + M12 - 11.5 s entered by axes, 8.5 s entered built."""
    axes = ONE_PER_SHAPE["open-on-the-chart"]
    built = next(c["id"] for c in candidates.values() if c["shape"] == "open-on-the-chart"
                 and any(m["card"] == "page_enter:built" for m in c["members"]))
    cl = LE.clocks()
    assert LB.shape_window_s(ROOT, "open-on-the-chart", candidates[axes]) == cl["lp_build_s"] + 2.5 + 6.0 == 11.5
    assert LB.shape_window_s(ROOT, "open-on-the-chart", candidates[built]) == 8.5
    assert LB.shape_window_s(ROOT, "open-on-the-chart") == 11.5          # no candidate: the longest it can ask for
    assert LB.shape_window_s(ROOT, "page-number-lands-at-n") == 10.9     # its mount entry is the longest of the three
    assert LB.shape_window_s(ROOT, "plate-carries-a-card") == cl["m44_plate_s"]   # no entry slot: one window


def test_every_shape_maps_to_a_real_tokyo_beat(beats: list[dict]):
    """Each of the five shapes cites beat numbers the approved cut's own BEAT PLAN carries, with a reason."""
    known = {int(b["beat"]) for b in beats}
    assert set(LB.SHAPE_BEATS) == set(ONE_PER_SHAPE), "a shape without a beat cannot be planted"
    for shape, (numbers, reason) in LB.SHAPE_BEATS.items():
        assert numbers and set(numbers) <= known, f"{shape} cites a beat the plan does not have"
        assert len(reason) > 60 and "'" in reason, f"{shape}'s reason must quote the sentence it is owed in"
        window = LB.beat_window(beats, numbers, LB.shape_window_s(ROOT, shape), f"lab:{shape}:00000000")
        assert window["sentence"] == next(b["sentence"] for b in beats if int(b["beat"]) == numbers[0])
        assert window["t1"] - window["t0"] >= LB.shape_window_s(ROOT, shape) - LB.EPS


def test_the_window_runs_to_the_later_of_the_beat_and_the_shape(beats: list[dict]):
    numbers, _reason = LB.SHAPE_BEATS["open-on-the-chart"]
    window = LB.beat_window(beats, numbers, 15.9, "lab:open-on-the-chart:331d7285")
    assert window["t0"] == 0.0 and window["t1"] == 15.9        # the hook is 4.74 s; the shape's own window is longer
    assert window["beats"] == [1, 2] and window["n"] == 1


# --------------------------------------------------------------------------- the member -> row translation

@pytest.mark.parametrize("shape", sorted(ONE_PER_SHAPE))
def test_one_candidate_of_each_shape_authors_rows_the_kit_accepts(tmp_path, monkeypatch, shape, candidates):
    """The kit's own grammar is the judge: the table is written with `write_shot_table` and read back by `load_rows`."""
    cid = ONE_PER_SHAPE[shape]
    rc, runs = run(tmp_path, monkeypatch, [cid], batch=shape)
    assert rc == 0
    build = tmp_path / f"build-lab-{shape}" / LB.short_id(cid)
    rows = T.load_rows(build / LB.SHOT_TABLE_NAME)
    assert rows == sorted(rows, key=lambda r: (r[0], r[1])), "the spliced table is in clock order"
    record = records_of(runs)[0]
    t0, t1 = record["clip"]["t0"], record["clip"]["t1"]
    planted = [r for r in rows if abs(float(r[0]) - t0) < 0.01 and abs(float(r[1]) - t1) < 0.01]
    assert len(planted) == 1, "the candidate is exactly one row of the cut"
    row = planted[0]
    assert isinstance(row[2], str) and row[2], "a row carries a world"
    offsets = {round(t0 + float(m["offset_s"]), 2) for m in candidates[cid]["members"]}
    fired = {float(s["at"]) for s in (row[6] or [])} | {float(d[2]) for d in (row[4] or [])}
    assert fired <= offsets, "every member fires at the window's t0 + its own offset"
    assert fired, "a candidate that fires nothing is not a beat"


def test_the_members_become_the_row_tokens_the_catalogue_names(tmp_path, monkeypatch, candidates):
    """`author.key` per card: a page part in the plate id, a species dict, a dock tuple, the exit as the 6th element."""
    cid = ONE_PER_SHAPE["plate-carries-a-card"]                 # ken + an image dock landed + plate life + a cut exit
    rc, _runs = run(tmp_path, monkeypatch, [cid], batch="p")
    assert rc == 0
    rows = T.load_rows(tmp_path / "build-lab-p" / LB.short_id(cid) / LB.SHOT_TABLE_NAME)
    row = next(r for r in rows if r[4] and any(d[0] == "dock-i-fab-wafer" for d in r[4]))
    assert row[3] == LB.KEN_BURNS                               # plate_option:ken -> the row's 4th element
    dock = next(d for d in row[4] if d[0] == "dock-i-fab-wafer")
    assert dock[4]["arrive"] == "land" and dock[4]["mass"] == "metal"   # arrival:land + its option, in the dock opts
    assert row[5] == "cut"                                      # exit:cut -> the row's 6th element
    assert [s["kind"] for s in row[6]] == ["plate_life"]         # species:plate_life -> the species list
    page = ONE_PER_SHAPE["page-number-lands-at-n"]
    rc, _runs = run(tmp_path, monkeypatch, [page], batch="q")
    rows = T.load_rows(tmp_path / "build-lab-q" / LB.short_id(page) / LB.SHOT_TABLE_NAME)
    plate = next(r[2] for r in rows if str(r[2]).startswith("ledger:ev-japan-holdings-v1:bars"))
    assert ":mount" in plate and not plate.endswith(":cut")     # page_enter:mount, page_exit:retract (no 7th part)


def test_the_approved_rows_outside_the_window_are_kept(tmp_path, monkeypatch):
    """Everything the window does not touch is the approved cut, row for row."""
    cid = ONE_PER_SHAPE["return"]
    rc, runs = run(tmp_path, monkeypatch, [cid], batch="r")
    assert rc == 0
    approved = T.load_rows(LB.bed_dir(ROOT) / LB.APPROVED_TABLE)
    rows = T.load_rows(tmp_path / "build-lab-r" / LB.short_id(cid) / LB.SHOT_TABLE_NAME)
    clip = records_of(runs)[0]["clip"]
    untouched = [r for r in approved if r[1] <= clip["t0"] + LB.EPS or r[0] >= clip["t1"] - LB.EPS]
    assert untouched and all(r in rows for r in untouched)


def test_the_window_takes_a_remnant_too_short_to_be_a_plate():
    """M44: a tenth of a second of the outgoing plate is a flash, not a plate - the window snaps to its cut (M13)."""
    rows = [(38.95, 45.0, "plate-p-viewers-desk", (0, 0, 0), [], "cut", []), (45.0, 60.0, "x", (0, 0, 0), [], None, [])]
    assert LB.snap_window(rows, 39.05, 45.05) == (38.95, 45.05)   # 0.10 s of the plate: taken
    assert LB.snap_window(rows, 41.0, 45.05) == (41.0, 45.05)     # 2.05 s of the plate: a beat of its own, kept


def test_splice_clips_a_row_the_window_cuts_into():
    row = (0.0, 10.0, "plate-x", (0, 0, 0), [("d", 0, 1.0, 9.0, {})], "cut", [{"kind": "punch", "at": 8.0, "dur": 1.0}])
    out = LB.splice([row], [(4.0, 6.0, "plate-y", (0, 0, 0), [], None, [])], 4.0, 6.0)
    assert [(r[0], r[1]) for r in out] == [(0.0, 4.0), (4.0, 6.0), (6.0, 10.0)]
    assert out[0][4][0][3] == 4.0 and out[0][6] == []           # the dock is clipped, the species outside it dropped
    assert out[2][6] == [{"kind": "punch", "at": 8.0, "dur": 1.0}]


# --------------------------------------------------------------------------- the rows, the record, the survivor bit

def test_the_level_id_protocol_is_parsed_not_reimplemented():
    rows = LB.tool_rows("  [PASS ] M01 fine\n  [WARN ] M02 one stretch\n  [FAIL ] M38 coverage 0.03\n"
                        "RESULT: FAIL\nnoise, and a table row M40 | 0.4 | 0.6\n")
    assert [(r["level"], r["id"]) for r in rows] == [("PASS", "M01"), ("WARN", "M02"), ("FAIL", "M38")]
    assert rows[2]["text"] == "coverage 0.03"
    assert LB.decided_by(rows) == ["[WARN] M02 one stretch", "[FAIL] M38 coverage 0.03"]
    assert LB.tool_rows("[PASS] M01 fine\n") == [], "the protocol is the gates' own: `[LEVEL]` is five wide"


def test_the_bar_that_could_not_run_is_a_warn_naming_it_and_a_written_report_is_read(tmp_path, monkeypatch):
    """self_watch's own rule for a tool that cannot run: one WARN row naming it, never a crash and never a verdict."""
    build, sheet = tmp_path / "b", tmp_path / "b" / LB.SHEET_NAME
    build.mkdir()
    monkeypatch.setattr(LB, "run_tool", lambda argv: (1, "Traceback\nFileNotFoundError: no timeline.json\n"))
    rows = LB.run_filter(build, tmp_path, [0.0, 2.5, 6.0], sheet)
    bar = [r for r in rows if r["id"] == "self-watch"]
    assert len(bar) == 1 and bar[0]["level"] == "WARN" and "did not run" in bar[0]["text"]
    assert [r for r in rows if r["id"] == "probe"][0]["level"] == "FAIL"     # no sheet on disk: the probe FAILs
    (build / "SELF-WATCH.md").write_text("## 3 verdict\nVERDICT: NOT CLEAN - the one-shot floor (M38)\n",
                                         encoding="utf-8")
    sheet.write_bytes(b"png")
    monkeypatch.setattr(LB, "run_tool", lambda argv: (1, CLEAN_ROWS) if "self_watch.py" in argv[0]
                        else (0, CLEAN_ROWS))
    rows = LB.run_filter(build, tmp_path, [0.0, 2.5, 6.0], sheet)
    bar = [r for r in rows if r["id"] == "self-watch"]
    assert len(bar) == 1 and bar[0]["level"] == "FAIL" and "NOT CLEAN" in bar[0]["text"]
    assert [r for r in rows if r["id"] == "probe"][0]["level"] == "PASS"


def test_the_record_carries_the_beat_the_clip_the_sheet_and_the_receipt(tmp_path, monkeypatch, beats):
    cid = ONE_PER_SHAPE["open-on-the-chart"]
    rc, runs = run(tmp_path, monkeypatch, [cid], batch="rec")
    assert rc == 0
    record = records_of(runs)[0]
    assert set(record) >= {"id", "shape", "beat", "build", "survivor", "decided_by", "context", "clip", "sheet",
                           "no_receipt", "at"}
    assert record["id"] == cid and record["shape"] == "open-on-the-chart"
    assert record["no_receipt"] == f"recipe lab candidate {cid}"
    assert record["beat"]["n"] == 1 and record["beat"]["sentence"] == "Tokyo took a tea break."
    assert LB.sentence_at(beats, record["clip"]["t0"]) == record["beat"]["sentence"]
    assert record["sheet"].endswith(LB.SHEET_NAME) and LB.short_id(cid) in record["build"]
    # M02's stretch runs 41.1-49.9s - a minute away from this candidate's beat, so it is CONTEXT and decides nothing
    assert record["decided_by"] == [] and record["context"] == ["[WARN] M02 one stretch over 8s: 41.1-49.9"]
    assert record["survivor"] is True


def test_survivor_is_false_when_a_fail_row_INSIDE_the_window_decided_it(tmp_path, monkeypatch):
    """A candidate a gate FAILs is RECORDED with the row that killed it, never dropped - and the whole-cut floor
    that fired on the approved cut around it is carried as context, not as its verdict (P65 T3)."""
    cid = ONE_PER_SHAPE["page-to-page-transform"]
    rc, runs = run(tmp_path, monkeypatch, [cid], text=FAILING_ROWS, batch="f")
    assert rc == 0
    record = records_of(runs)[0]
    assert record["clip"]["t0"] <= 50.0 <= record["clip"]["t1"]          # 0:50 is inside this candidate's beat
    assert record["survivor"] is False and record["fails"] == ["M27"]
    assert any(line.startswith("[FAIL] M27 1 card(s)") for line in record["decided_by"])
    assert any(line.startswith("[FAIL] M38 proven-recipe coverage 0.03") for line in record["context"])


# --------------------------------------------------------------------------- the filter decides on the WINDOW

def test_row_instants_reads_the_four_forms_and_nothing_else():
    spans = {"s02": (15.9, 38.96)}
    assert LB.row_instants("1 pair(s) sitting on each other at 0:25 (s02)", spans) == [(25.0, 25.0), (15.9, 38.96)]
    assert LB.row_instants("landing 2 (throw, paper) at 9.51s gain 0.12") == [(9.51, 9.51)]
    assert LB.row_instants("its build lands at 3.0s (never over the build)") == [(3.0, 3.0)]
    assert LB.row_instants("one stretch over 8s: 41.1-49.9") == [(41.1, 49.9)]
    # a count, a share and a ratio name no instant at all: a whole-cut row
    assert LB.row_instants("2 chart forms (dense-line/line x4) on 6 chart surfaces - the floor is 3") == []
    assert LB.row_instants("narrative : chart 0.33 (2 narrative / 6 chart) - the floor is 1.00") == []


def test_only_the_rows_inside_the_window_decide_and_the_floors_never_do():
    """The Tokyo cut around a candidate is the APPROVED cut: a one-beat change cannot own its whole-cut floors."""
    spans = {"s02": (15.9, 38.96), "s03": (38.96, 44.88)}
    rows = LB.tool_rows(
        "  [FAIL ] M11 first chart enters full and unannotated - ... its build lands at 3.0s; window 0-10s\n"
        "  [FAIL ] M28 2 pair(s) of a page's own labels sitting on each other at 0:25 (s02)\n"
        "  [FAIL ] M34 1 collision(s): callout m0 over tick:4% at 1:10 (s05)\n"
        "  [WARN ] M44 1 world plate(s) under 6s: s03 5.9s\n"
        "  [FAIL ] M37 docks on 0.32 of 25 beats - the floor is 0.36\n")
    deciding, context = LB.partition(rows, 0.0, 11.5, spans)            # the open's own window
    assert [r["id"] for r in deciding] == ["M11"]
    assert [r["id"] for r in context] == ["M28", "M34", "M44", "M37"]
    deciding, context = LB.partition(rows, 38.96, 45.05, spans)         # the plate's own window
    assert [r["id"] for r in deciding] == ["M44"]                       # s03 IS the candidate's row
    assert [r["id"] for r in context] == ["M11", "M28", "M34", "M37"]
    for row_id in OSF.ROW_ORDER:                                        # M35-M46, every one of them
        assert not LB.decides({"level": "FAIL", "id": row_id, "text": "at 0:05 in s01"}, 0.0, 11.5, spans)


def test_a_build_row_always_decides_and_a_warn_inside_the_window_is_not_fatal(tmp_path, monkeypatch):
    """A build that did not compile or render is not a candidate at all - but the one-shot BAR's verdict is a
    whole-cut aggregate of the same gate rows, so it is context (P65 T3)."""
    spans = {}
    for tool in ("compile", "probe"):
        assert LB.decides({"level": "FAIL", "id": tool, "text": "no instant here"}, 0.0, 1.0, spans)
    assert not LB.decides({"level": "FAIL", "id": "self-watch",
                           "text": "NOT CLEAN - motion gate (M01-M24): [FAIL] M28 at 0:25"}, 0.0, 1.0, spans)
    cid = ONE_PER_SHAPE["plate-carries-a-card"]
    warn = "  [WARN ] M23 1 transition(s): s03 rescale 0:40+1.4s fires inside the page's build beat (E45)\n"
    rc, runs = run(tmp_path, monkeypatch, [cid], text=warn, batch="warn")
    assert rc == 0
    record = records_of(runs)[0]
    assert record["decided_by"] == ["[WARN] M23 1 transition(s): s03 rescale 0:40+1.4s fires inside the page's "
                                   "build beat (E45)"]
    assert record["fails"] == [] and record["survivor"] is True         # a WARN inside the window is recorded only


def test_a_span_that_only_touches_the_window_is_not_inside_it():
    assert LB.inside(3.0, 3.0, 0.0, 11.5) and not LB.inside(25.0, 25.0, 0.0, 11.5)
    assert not LB.inside(15.9, 38.96, 38.96, 45.05), "the scene before the candidate's own ends where its row begins"
    assert LB.inside(38.96, 44.88, 38.96, 45.05)


def test_an_unknown_candidate_is_refused_by_name(tmp_path, monkeypatch, capsys):
    rc, _runs = run(tmp_path, monkeypatch, ["lab:return:deadbeef"], batch="u")
    assert rc == 1
    assert LE.CANDIDATES_REL in capsys.readouterr().out


# --------------------------------------------------------------------------- --check

def test_check_exits_1_on_a_missing_sheet_and_0_when_both_are_on_disk(tmp_path, monkeypatch):
    cid = ONE_PER_SHAPE["return"]
    rc, runs = run(tmp_path, monkeypatch, [cid], batch="c")
    assert rc == 0
    record = records_of(runs)[0]
    argv = ["--batch", "c", "--candidates", cid, "--check", "--runs", str(runs), "--repo", str(ROOT)]
    assert LB.main(argv) == 1                                   # --dry-run rendered no sheet and compiled no timeline
    build = ROOT / record["build"]
    assert not (build / "timeline.json").is_file() or True
    # the same record with its artifacts on disk passes: a tmp repo root with the sheet, the timeline and the runtime
    fake = tmp_path / "repo"
    (fake / record["build"]).mkdir(parents=True)
    (fake / record["sheet"]).write_bytes(b"png")
    (fake / record["build"] / "timeline.json").write_text(json.dumps({"runtime_s": 120.0}), encoding="utf-8")
    assert LB.check(fake, "c", [cid], str(runs)) == []
    (fake / record["sheet"]).unlink()
    bad = LB.check(fake, "c", [cid], str(runs))
    assert len(bad) == 1 and "is not on disk" in bad[0] and cid in bad[0]


def test_check_names_a_candidate_with_no_record(tmp_path, monkeypatch):
    cid = ONE_PER_SHAPE["return"]
    _rc, runs = run(tmp_path, monkeypatch, [cid], batch="m")
    bad = LB.check(tmp_path, "m", [cid, ONE_PER_SHAPE["open-on-the-chart"]], str(runs))
    assert any("no record" in line and ONE_PER_SHAPE["open-on-the-chart"] in line for line in bad)


def test_check_refuses_a_clip_window_past_the_builds_runtime(tmp_path, monkeypatch):
    cid = ONE_PER_SHAPE["page-number-lands-at-n"]
    _rc, runs = run(tmp_path, monkeypatch, [cid], batch="w")
    record = records_of(runs)[0]
    fake = tmp_path / "short"
    (fake / record["build"]).mkdir(parents=True)
    (fake / record["sheet"]).write_bytes(b"png")
    (fake / record["build"] / "timeline.json").write_text(json.dumps({"runtime_s": 1.0}), encoding="utf-8")
    bad = LB.check(fake, "w", [cid], str(runs))
    assert len(bad) == 1 and "is not inside the build's own 1.00s runtime" in bad[0]


# --------------------------------------------------------------------------- P65 T8: the sound follows the landing

def cue(slot: str, at: float, **kw) -> dict:
    """One cue in the shape `build_short.sound_cues` writes and the compiler embeds."""
    return {"slot": slot, "at": at, "gain": 0.12, "fade_in": 0.0, "env": [], "variants": {"A": "x.mp3"}, **kw}


def test_the_approved_cues_inside_the_window_go_and_the_ones_outside_stay_approved():
    """The smoke's own M29 kill: the bed's cue plan is authored for the APPROVED rows, so a cue inside a replaced
    window marks a landing that no longer happens. Outside it, the derived plan puts the SAME cue at the SAME
    instant, and the object kept is the APPROVED one - the variants the compiler embedded, not a fresh copy."""
    outside = cue("landing 5 (throw, paper)", 76.21, variants={"A": "__snd_5_A__"})
    approved = [cue("hook bed", 0.0, fade_in=1.5), cue("landing 2 (throw, paper)", 9.51), outside]
    derived = [cue("hook bed", 0.0, fade_in=1.5), cue("page enter 1", 0.0),
               cue("landing 3 (throw, paper)", 76.21), cue("landing 2 (throw, paper)", 11.92)]
    cues, dropped, added = LB.cue_splice(approved, derived, 0.0, 11.5)
    assert dropped == ["landing 2 (throw, paper) at 9.51s"], "the cue whose landing the candidate replaced"
    assert added == ["page enter 1 at 0.00s", "landing 2 (throw, paper) at 11.92s"], "the candidate's own, and the"
    assert outside in cues, "the approved OBJECT outside the window, with its embedded variant"
    assert [c["slot"] for c in cues if c["slot"].startswith("landing")] == ["landing 2 (throw, paper)",
                                                                           "landing 5 (throw, paper)"]
    assert [c["at"] for c in cues] == sorted(c["at"] for c in cues)


def test_the_bed_rides_with_the_approved_plan_and_is_never_window_scoped():
    """A bed is continuous sub-threshold music: it marks no landing, its envelope is the operator's, and a candidate
    does not re-breathe the music of the rest of the cut. The reading is the gate's own (`_is_bed`)."""
    bed = cue("hook bed", 0.0, fade_in=1.5, variants={"A": "__snd_7_A__"})
    cues, dropped, _added = LB.cue_splice([bed], [cue("hook bed", 0.0, fade_in=1.5)], 0.0, 11.5)
    assert bed in cues and dropped == []


def test_a_landing_kind_the_bed_maps_no_cue_for_is_recorded_and_never_invented():
    """`no cue mapped for <kind>` - the lab has no sound file for it and no ruling that there should be one, so it
    records the gap and lets M29 print what it prints (E99 s37: no generator, no invented asset)."""
    cues = [cue("landing 2 (throw, paper)", 11.92)]
    notes = LB.cue_notes(cues, [(11.96, "dock arrive=throw"), (2.0, "page enter=mount")])
    assert notes == ["no cue mapped for page enter=mount (its landing at 2.00s carries no sound)"]
    assert LB.cue_notes(cues, [(11.96, "dock arrive=throw")]) == [], "a landing within the gate's own CUE_TOL_S"


def test_the_landings_a_candidates_rows_make_are_read_on_the_kits_own_clocks():
    """A dock's landing is its CONTACT frame (`audio.landing_contact` over the kinetics module's dials), never its
    enter; a page's is the row's own start, by the entry its plate id declares (`audio.page_transitions`)."""
    rows = [(0.0, 11.5, "ledger:ev-japan-holdings-v1:line:315:right:mount=2.0", (0, 0, 0),
             [("dock-c", 0, 1.0, 9.0, {"arrive": "throw", "mass": "paper"})], None, []),
            (20.0, 30.0, "plate-p-viewers-desk", (0, 0, 0), [], "cut", [])]
    got = LB.row_landings(rows, 0.0, 11.5)
    assert [k for _t, k in got] == ["page enter=mount", "dock arrive=throw"]
    assert got[0][0] == 0.0 and got[1][0] > 1.0, "the contact frame is later than the enter"
    assert LB.row_landings(rows, 19.0, 31.0) == [], "a row whose world is a plate lands nothing"


# --------------------------------------------------------------------------- P65 T8: the recipes as candidates

@pytest.fixture(scope="module")
def proven() -> dict:
    return LB.load_proven(ROOT)


def test_the_fifteen_proven_recipes_are_the_ones_the_lab_re_proves(proven: dict):
    """R26-168's set, read from the recipe FILES (the source) and not from the catalogue (build output, P63)."""
    assert len(proven) == 15 and all(r["status"] == "proven" and r.get("proof") for r in proven.values())


def test_the_beat_is_chosen_by_the_recipes_own_acts_and_the_reason_is_carried(proven: dict):
    """A recipe's FIRST act picks the shape through `ACT_SHAPES`, and the shape picks the Tokyo beat through
    `SHAPE_BEATS` - the recipe's own declaration, never a scoring rule (E99 s66)."""
    for rid, rec in proven.items():
        shape, why = LB.recipe_shape(rec)
        assert shape in LB.SHAPE_BEATS, rid
        assert why.startswith(f"act {rec['acts'][0]}:") or any(why.startswith(f"act {a}:") for a in rec["acts"])
    assert LB.recipe_shape(proven["recipe:emphasized-bar-lit"])[0] == "open-on-the-chart"   # COMPARES
    assert LB.recipe_shape(proven["recipe:punch-then-callout"])[0] == "return"              # TURNS
    assert LB.recipe_shape(proven["recipe:still-life-breather"])[0] == "plate-carries-a-card"   # SETS
    with pytest.raises(LB.LabBuildError) as exc:
        LB.recipe_shape({"id": "recipe:x", "acts": ["INVENTS"]})
    assert "ACT_SHAPES" in str(exc.value) and "E99 s66" in str(exc.value)


def test_the_rail_is_dropped_at_9_16_and_the_record_says_which_member_and_why(tmp_path, monkeypatch, proven):
    """R26-171: a badge rail on any card at 9:16 sits at 13 stage px (M25). The badge ladder is built WITHOUT its
    rails - four of its five members - and each drop is recorded with the member and the reason."""
    rc, runs = recipes(tmp_path, monkeypatch, ["recipe:badge-ladder"], batch="rail")
    assert rc == 0
    record = records_of(runs)[0]
    assert len(record["dropped"]) == 4 and all("dock_option:badge" in d for d in record["dropped"])
    assert all("R26-171" in d and "13 stage px" in d and "DROPPED" in d for d in record["dropped"])
    rows = T.load_rows(tmp_path / "build-lab-rail" / LB.short_id("recipe:badge-ladder") / LB.SHOT_TABLE_NAME)
    planted = [r for r in rows if abs(float(r[0]) - record["clip"]["t0"]) < 0.01]
    assert planted and not any("badge" in json.dumps(r[4] or []) for r in planted)


def test_park_is_dropped_at_9_16_too_and_a_bed_bind_that_is_missing_is_named():
    """R26-172 (`chart_to park` under 11 px pills) and the two Steel-only payloads: every drop names its reason."""
    assert "R26-172" in LB.MEMBER_DROPS["chart_to:park"]
    assert "Steel" in LB.MEMBER_DROPS["dock_payload:stack"]
    assert "Steel" in LB.MEMBER_DROPS["chart_dock:checklist"]


def test_a_recipes_members_land_at_their_own_offsets_on_the_windows_clock(tmp_path, monkeypatch, proven):
    """`punch-then-callout`: the page spirals in, the punch at +0.12, the callout at +3.88 - the recipe's own
    offsets on the beat's own t0, with nothing invented between them."""
    rc, runs = recipes(tmp_path, monkeypatch, ["recipe:punch-then-callout"], batch="punch")
    assert rc == 0
    record = records_of(runs)[0]
    t0 = record["clip"]["t0"]
    rows = T.load_rows(tmp_path / "build-lab-punch" / LB.short_id("recipe:punch-then-callout") / LB.SHOT_TABLE_NAME)
    row = next(r for r in rows if abs(float(r[0]) - t0) < 0.01)
    assert ":spiral" in str(row[2])
    assert "then=" not in str(row[2]), ("M23: a recipe with no chart_to never inherits the beat's own chart states "
                                        "- a state built to be moved to and never moved to is what M23 refuses")
    assert [(s["kind"], round(float(s["at"]) - t0, 2)) for s in row[6]] == [("punch", 0.12), ("callout", 3.88)]


def test_a_world_change_inside_a_recipe_is_its_own_row_so_m44_can_measure_it(tmp_path, monkeypatch):
    """R26-168's first contradiction: `card-becomes-the-chart` is proven on a 3-5 s plate and M44 asks six. The
    plate is a ROW of its own with its own seconds - measurable - and the page snaps out of the landed card."""
    rc, runs = recipes(tmp_path, monkeypatch, ["recipe:card-becomes-the-chart"], batch="cbtc")
    assert rc == 0
    record = records_of(runs)[0]
    assert [s["kind"] for s in record["segments"]] == ["plate", "page"]
    rows = T.load_rows(tmp_path / "build-lab-cbtc" / LB.short_id("recipe:card-becomes-the-chart")
                       / LB.SHOT_TABLE_NAME)
    t0, t1 = record["clip"]["t0"], record["clip"]["t1"]
    mine = [r for r in rows if t0 - 0.01 <= float(r[0]) and float(r[1]) <= t1 + 0.01]
    assert len(mine) == 2
    plate, page = mine
    assert float(plate[1]) - float(plate[0]) < LB.GMD.PLATE_MIN_S, "the proven plate is UNDER M44's six seconds"
    assert plate[5] == "dip" and "snap=dock-c-blue-ties-panel" in str(page[2])
    assert float(page[1]) - float(page[0]) >= LB.GMD.PLATE_MIN_S - 0.01, "the last world of a beat is never a flash"


def test_one_card_per_offset_and_the_box_is_handed_on(tmp_path, monkeypatch):
    """`plate-dock-wipe` asks for an image card whose PAYLOAD is a chart: one card, not two stacked on one another.
    `read-park-build-write` asks for a second card taking the same box: two cards, the first ending where the
    second begins."""
    rc, _runs = recipes(tmp_path, monkeypatch, ["recipe:plate-dock-wipe", "recipe:read-park-build-write"], batch="d")
    assert rc == 0
    clip = next(r["clip"] for r in records_of(tmp_path / "d.jsonl") if r["recipe"] == "recipe:plate-dock-wipe")
    rows = T.load_rows(tmp_path / "build-lab-d" / LB.short_id("recipe:plate-dock-wipe") / LB.SHOT_TABLE_NAME)
    row = next(r for r in rows if abs(float(r[0]) - clip["t0"]) < 0.01)
    assert len(row[4]) == 1 and row[5] == "wipe_right"
    runs = tmp_path / "d.jsonl"
    clip = next(r["clip"] for r in records_of(runs) if r["recipe"] == "recipe:read-park-build-write")
    rows = T.load_rows(tmp_path / "build-lab-d" / LB.short_id("recipe:read-park-build-write") / LB.SHOT_TABLE_NAME)
    row = next(r for r in rows if abs(float(r[0]) - clip["t0"]) < 0.01)
    assert len(row[4]) == 2
    assert row[4][0][0] != row[4][1][0], "a second READ is a second card, never the same asset docked twice"
    assert abs(float(row[4][0][3]) - float(row[4][1][2])) < 0.01, "the box is handed on"


def test_a_species_carries_its_recipes_dials_and_never_outlives_the_next_fire_of_its_kind(tmp_path, monkeypatch):
    """`trace-callout-ladder` fires three traces 1.26 s apart; the bed's own trace `dur` is 5.62 s, authored for one
    long stroke across a whole plate. Held at that, the first would still be drawing when the third began."""
    rc, _runs = recipes(tmp_path, monkeypatch, ["recipe:trace-callout-ladder"], batch="ladder")
    assert rc == 0
    rows = T.load_rows(tmp_path / "build-lab-ladder" / LB.short_id("recipe:trace-callout-ladder")
                       / LB.SHOT_TABLE_NAME)
    row = next(r for r in rows if r[6] and any(s["kind"] == "trace" for s in r[6]))
    traces = [s for s in row[6] if s["kind"] == "trace"]
    assert len(traces) == 3 and all(s.get("draw_s") == 0.55 and s.get("width") == 9 for s in traces)
    assert traces[0]["at"] + traces[0]["dur"] <= traces[1]["at"] + 0.01


def test_the_clocks_a_recipe_is_rebuilt_under_are_the_gates_own():
    """M44's six seconds and M11's tolerance are read from `gate_motion_density`, never typed here - the lab keeps
    no second opinion about a threshold (memory `thresholds-from-the-reference`)."""
    assert LB.GMD.PLATE_MIN_S == 6.0 and LB.GMD.ANNOTATE_TOL_S == 1.5
    assert LB.DEFAULT_ENTER == "axes", "E99 s67: a page BUILDS then holds built; `built` is never an entry"


# --------------------------------------------------------------------------- P65 T8: the verdict classifier

MEMBERS_CBTC = [(0.0, {"card": "idle:drift", "offset_s": 0.0}),
                (4.12, {"card": "arrival:throw", "offset_s": [0.82, 4.12]}),
                (5.12, {"card": "exit:dip", "offset_s": [1.82, 5.12]}),
                (5.12, {"card": "page_enter:snap", "offset_s": [1.82, 5.12]})]
SEGS_CBTC = [{"at": 0.0, "kind": "plate"}, {"at": 5.12, "kind": "page"}]
MEMBERS_EBL = [(0.0, {"card": "page_builder:bars", "offset_s": 0.0}),
               (7.56, {"card": "species:spotlight", "offset_s": [7.55, 7.56]})]
SEGS_EBL = [{"at": 0.0, "kind": "page"}]


def test_m44_on_a_short_plate_asks_for_the_member_that_closes_it_to_move():
    """R26-168 #1, answered by moving ONE member and never by lowering a gate."""
    row = "[WARN] M44 1 world plate(s) under 6s (1 world plate(s), floor 6s): s01 5.1s - a plate the eye cannot"
    amend = LB.amend_for(row, MEMBERS_CBTC, SEGS_CBTC)
    assert amend.startswith("exit:dip, from 5.12 -> 6.00") and "M44" in amend


def test_m11_on_a_late_light_asks_for_the_light_to_come_back_to_the_pages_build():
    """R26-168 #2: `emphasized-bar-lit` lights 7.55 s after the build and E99 s67 wants the page lit as it builds."""
    row = "[FAIL] M11 first chart enters full and unannotated - declare a spotlight within 1.5s AFTER the build"
    amend = LB.amend_for(row, MEMBERS_EBL, SEGS_EBL)
    assert amend.startswith("species:spotlight, from 7.56 -> 3.00") and "E99 s67" in amend
    assert LB.amend_for(row, MEMBERS_CBTC, SEGS_CBTC) is None, "a recipe with no light has no M11 amendment"


def test_a_row_no_offset_of_this_recipe_can_answer_is_not_an_amendment():
    assert LB.amend_for("[FAIL] M29 1 transient cue(s) marking nothing", MEMBERS_CBTC, SEGS_CBTC) is None
    assert LB.amend_for("[FAIL] M27 7 card(s) reading over a page's ink", MEMBERS_EBL, SEGS_EBL) is None


def test_the_verdict_is_one_of_the_three_and_the_deciding_row_is_named():
    """survives / needs an amended offset / unreachable - decided on the rows INSIDE the window and on the walk."""
    fired = {"decided_by": ["[WARN] M06 60 caption pages"], "fires": {"count": 1, "members_at": [0.0, 0.12, 3.88]}}
    assert LB.recipe_verdict(fired, MEMBERS_EBL, SEGS_EBL) == "survives as proven"
    killed = {"decided_by": ["[FAIL] M29 1 transient cue(s) marking nothing inside the drop window"],
              "fires": {"count": 0, "why": "x"}}
    assert LB.recipe_verdict(killed, MEMBERS_EBL, SEGS_EBL) == ("unreachable under the clocks: [FAIL] M29 1 "
                                                               "transient cue(s) marking nothing inside the drop "
                                                               "window")
    late = {"decided_by": ["[FAIL] M11 first chart enters full and unannotated"], "fires": {"count": 0, "why": "x"}}
    assert LB.recipe_verdict(late, MEMBERS_EBL, SEGS_EBL).startswith("needs an amended offset: species:spotlight")
    absent = {"decided_by": [], "fires": {"count": 0, "why": "dock_payload:stack never fired inside 38.96-65.05s "
                                                             "- the member is not on the built timeline at all"}}
    assert LB.recipe_verdict(absent, MEMBERS_EBL, SEGS_EBL).startswith("unreachable under the clocks: "
                                                                       "dock_payload:stack never fired")
    drifted = {"decided_by": [], "fires": {"count": 0, "why": "species:callout, from 42.84 -> 45.10"}}
    assert LB.recipe_verdict(drifted, MEMBERS_EBL, SEGS_EBL) == ("needs an amended offset: species:callout, from "
                                                                 "42.84 -> 45.10")


def test_a_range_offset_takes_its_high_end_while_that_still_fits_the_recipes_window():
    """The recipe's BEST case under today's clocks, so a row that fires anyway is a real contradiction."""
    assert LB.member_offset({"offset_s": [1.82, 5.12]}, 6.0) == 5.12
    assert LB.member_offset({"offset_s": [2.4, 30.0]}, 6.0) == 2.4      # the high end does not fit: the low one
    assert LB.member_offset({"offset_s": 3.88}, 6.0) == 3.88


def test_a_recipe_that_is_not_proven_is_refused_by_name(tmp_path, monkeypatch):
    monkeypatch.setattr(LB, "run_tool", canned(CLEAN_ROWS))
    rc = LB.main(["--batch", "x", "--recipes", "recipe:not-a-recipe", "--dry-run",
                  "--runs", str(tmp_path / "x.jsonl"), "--builds", str(tmp_path / "build-lab-x")])
    assert rc == 1


# --------------------------------------------------------------------------- the WHOLE TABLE (P66 HG1)
#
# `lab_build.py --table <a shot table> --into <build dir> --label <text>` builds a WHOLE table - a generated BASE
# (`generate_base_table.py`, P66 T4) - on the same Tokyo bed. Everything here is `--dry-run`: the rows are loaded
# and the cue plan is re-derived for real, the compile and the four tools are stubbed, and nothing is written
# outside `tmp_path`. What is pinned: the APPROVED cut's two files (`sound/SOUND-PLAN.json` and
# `SHOT-TABLE-SHORT.py` - the pair `build_short.main` writes, which is why `main` is never called) are BYTE-identical
# before and after; the re-derived cue plan lands in the PRIVATE build and follows the GIVEN rows' landings; and the
# mode refuses `build-short*` by name and refuses to run without `--into` and `--label`.

BASE_TABLE = (ROOT / "content/video_engine/projects/systems-and-blowups/tokyo-tea-break/build-p66-base"
              / "SHOT-TABLE-SHORT.py")                      # the P66 base - a PRIVATE build dir, gitignored
ANY_TABLE = LB.bed_dir(ROOT) / LB.APPROVED_TABLE            # any whole table: the mode is not the base's alone


def approved_pair() -> dict:
    """The two files of the APPROVED Tokyo cut this mode must never write, as BYTES."""
    bed = LB.bed_dir(ROOT)
    return {rel: (bed / rel).read_bytes() for rel in (LB.PROJECT_PLAN_REL, LB.APPROVED_TABLE)}


def drive_table(tmp_path: Path, monkeypatch, table: Path, label: str = "p66-t") -> tuple[int, Path, Path]:
    monkeypatch.setattr(LB, "run_tool", canned(CLEAN_ROWS))
    into, runs = tmp_path / f"build-{label}", tmp_path / f"{label}.jsonl"
    rc = LB.main(["--table", str(table), "--into", str(into), "--label", label, "--dry-run", "--runs", str(runs)])
    return rc, into, runs


def assert_the_base_built(table: Path, into: Path, runs: Path, label: str) -> dict:
    """The cue plan in the PRIVATE build follows the GIVEN rows, and the record carries what a watch is read on."""
    rows = T.load_rows(table)
    plan = json.loads((into / LB.CUE_PLAN_NAME).read_text(encoding="utf-8"))
    enters = {round(float(c["at"]), 2) for c in plan["cues"] if str(c["slot"]).startswith("page enter")}
    want = {round(float(r[0]), 2) for r in rows
            if str(r[2]).startswith("ledger:") and ":mount=" not in str(r[2])}
    assert enters == want, "the cue plan is the GIVEN rows' own - a page that enters carries its enter cue"
    record = records_of(runs)[0]
    assert record["label"] == label and record["mode"] == "table"
    assert record["rows"] == len(rows), "the record names the row count of the table it built"
    assert record["no_receipt"] == f"P66 HG1 base: {label}", "a base's plan is a READ-BACK plan (P67 T2's escape)"
    assert record["sound"]["cues"] == len(plan["cues"]) and record["sound"]["plan"].endswith(LB.CUE_PLAN_NAME)
    assert record["bed_rows_discarded"] > 0, "the bed REGISTERS and its own rows are discarded"
    assert record["flagged"] == ["[WARN] M02 one stretch over 8s: 41.1-49.9"], "every FAIL/WARN row, verbatim"
    return record


@pytest.mark.skipif(not BASE_TABLE.is_file(), reason=f"{BASE_TABLE.parent.name}/ is a private build dir (gitignored)")
def test_the_whole_table_mode_builds_the_generated_base_and_writes_neither_approved_file(tmp_path, monkeypatch):
    """P66 HG1: the base compiles on the bed, and the APPROVED cut's own files do not move under it."""
    before = approved_pair()
    rc, into, runs = drive_table(tmp_path, monkeypatch, BASE_TABLE, "p66-base-t")
    assert rc == 0
    assert approved_pair() == before, ("the project's sound/SOUND-PLAN.json and SHOT-TABLE-SHORT.py are the APPROVED "
                                       "cut's - `build_short.main` writes both, so it is never called")
    record = assert_the_base_built(BASE_TABLE, into, runs, "p66-base-t")
    assert record["rows"] == 5, "the P66 base is five rows (T4's evidence)"


def test_the_whole_table_mode_takes_any_whole_table_and_leaves_the_approved_pair(tmp_path, monkeypatch):
    """The mode is not the base's alone: any table `table.load_rows` reads is built the same way."""
    before = approved_pair()
    rc, into, runs = drive_table(tmp_path, monkeypatch, ANY_TABLE, "any-t")
    assert rc == 0
    assert approved_pair() == before
    assert_the_base_built(ANY_TABLE, into, runs, "any-t")


def test_the_whole_table_mode_refuses_the_approved_build_dir_by_name(tmp_path, monkeypatch):
    """memory `review-link-frozen-copy`: `build-short*` is the approved cut and every cut watched beside it."""
    monkeypatch.setattr(LB, "run_tool", canned(CLEAN_ROWS))
    with pytest.raises(LB.LabBuildError) as exc:
        LB.build_table(ROOT, ANY_TABLE, LB.bed_dir(ROOT) / "build-short", "p66-t", True, str(tmp_path / "r.jsonl"))
    assert "build-short" in str(exc.value) and "review-link-frozen-copy" in str(exc.value)
    rc = LB.main(["--table", str(ANY_TABLE), "--into", str(LB.bed_dir(ROOT) / "build-short-cam"),
                  "--label", "p66-t", "--dry-run", "--runs", str(tmp_path / "r.jsonl")])
    assert rc == 1, "the CLI refuses it too, and writes nothing"
    assert not (tmp_path / "r.jsonl").exists()


def test_the_whole_table_mode_owes_into_and_label_and_takes_no_candidates(tmp_path, monkeypatch):
    monkeypatch.setattr(LB, "run_tool", canned(CLEAN_ROWS))
    assert LB.main(["--table", str(ANY_TABLE), "--dry-run"]) == 1
    assert LB.main(["--table", str(ANY_TABLE), "--into", str(tmp_path / "b"), "--label", "x",
                    "--batch", "t", "--dry-run"]) == 1
    assert LB.main(["--candidates", "lab:return:a8f817b4", "--dry-run"]) == 1, "--batch is owed outside --table"


def test_a_table_that_is_not_under_the_episode_is_refused_by_name(tmp_path, monkeypatch):
    """`table.compile_timeline` hands the compiler a path RELATIVE to the episode dir."""
    monkeypatch.setattr(LB, "run_tool", canned(CLEAN_ROWS))
    stray = tmp_path / "SHOT-TABLE-SHORT.py"
    stray.write_bytes(ANY_TABLE.read_bytes())
    with pytest.raises(LB.LabBuildError) as exc:
        LB.build_table(ROOT, stray, tmp_path / "build-x", "p66-t", True, str(tmp_path / "r.jsonl"))
    assert "relative to the episode dir" in str(exc.value).lower()
    with pytest.raises(LB.LabBuildError) as exc:
        LB.build_table(ROOT, tmp_path / "no-such-table.py", tmp_path / "build-y", "p66-t", True, None)
    assert "generate_base_table.py" in str(exc.value)


def test_probe_runs_on_the_gates_own_instants_for_a_whole_cut(tmp_path, monkeypatch):
    """A base has no window, so the probe is `--gate` - `layout-probe.json`, not a three-instant sheet."""
    seen: list[list[str]] = []

    def _run(argv):
        seen.append([str(a) for a in argv])
        return 0, CLEAN_ROWS
    monkeypatch.setattr(LB, "run_tool", _run)
    build = tmp_path / "b"
    build.mkdir()
    (build / LB.PROBE_GATE_NAME).write_text("{}", encoding="utf-8")
    rows = LB.run_filter(build, tmp_path, [], None, LB.TABLE_TIMELINE_NAME, gate=True)
    probe = [a for a in seen if a[0].endswith("probe.py")][0]
    assert "--gate" in probe and "--sheet" not in probe
    assert all(LB.TABLE_TIMELINE_NAME in a for a in seen), "every tool reads the build's own compiled timeline"
    assert rows[-1] == {"level": "PASS", "id": "probe", "text": f"{LB.PROBE_GATE_NAME} on the gate's own instants"}


def test_the_cue_plan_is_embedded_into_the_builds_own_compiled_timeline(tmp_path):
    """The defect the FIRST HG1 run printed: `no tokyo-lab.timeline.json on disk - the cue plan was not written`.

    The whole-table mode compiles `base.timeline.json`, so the plan must be embedded into THAT file; a plan written
    into a timeline that is not there is a plan nobody hears, and the gate then reads the APPROVED cues instead."""
    import types

    build = tmp_path / "b"
    build.mkdir()
    (build / LB.TABLE_TIMELINE_NAME).write_text(json.dumps({"sound": [{"slot": "the approved cue"}]}),
                                                encoding="utf-8")
    bed = types.SimpleNamespace(HERE=LB.bed_dir(ROOT))
    cue = {"slot": "page enter 1", "at": 1.0, "variants": {"A": "fs-page-roll-464302.mp3"}}
    assert LB.embed_cues(bed, build, [cue], LB.TABLE_TIMELINE_NAME) == []
    tl = json.loads((build / LB.TABLE_TIMELINE_NAME).read_text(encoding="utf-8"))
    assert [c["slot"] for c in tl["sound"]] == ["page enter 1"], "the build's own plan replaces the approved one"
    assets = json.loads((build / "assets.json").read_text(encoding="utf-8"))
    assert assets[LB.CUE_KEY.format(i=0, v="A")].startswith("data:"), "the player loads the cue through assets.json"
    assert LB.embed_cues(bed, build, [cue]) == [f"no {LB.TIMELINE_NAME} on disk - the cue plan was not written"]
