"""THE RECIPE LAB'S BATCH CARDS (P65 T4): the survivors grouped by beat shape, the seeded exploration draw, the
calibration probe, `--check`, and the server's one new item grammar.

The pins: one card per beat shape and only survivors on it; a card that validates as a `batch` record against
`build_review_queue.validate` (candidates side by side, a clip proof each, the proofs mirroring them in order); the
exploration draw is about a quarter, is SEEDED (the same seed gives the same draw, the seed is written into the
record) and is made without reference to any learner - the module names no approval-rate table at all; the calibration
probe attaches one previously approved candidate only when the log holds one older than 14 days, carrying the reason
it was judged with; `--check` passes on what `--write` wrote and fails by name on a card that drifted; and
`serve_review_queue.refuse_candidate` accepts `<card>#<candidate>` with a reason on the fixed list and refuses an
unknown candidate, a choice off approve / deny and a note that opens with no reason. Every write goes to a temp path;
no test renders video.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import build_review_queue as BRQ  # noqa: E402
import lab_batch as LB  # noqa: E402
import serve_review_queue as SRQ  # noqa: E402

BATCH = "test-r1"
SHAPES = ("plate-carries-a-card", "return")
NOW = "2026-09-17T00:00:00+00:00"


def a_run_record(shape: str, digest: str, survivor: bool = True) -> dict:
    cid = f"lab:{shape}:{digest}"
    return {"id": cid, "batch": BATCH, "shape": shape, "survivor": survivor,
            "build": f"content/video_engine/projects/x/build-lab-{BATCH}/{shape}-{digest}",
            "clip": {"t0": 10.0, "t1": 16.5}, "sheet": f"build-lab-{BATCH}/{shape}-{digest}/lab-sheet.png",
            "beat": {"n": 3, "sentence": "a Treasury page, and your phone.", "t0": 10.0, "t1": 16.5},
            "decided_by": [] if survivor else ["[FAIL] M29 a cue marking nothing at 9.51s"],
            "context": [], "at": "2026-09-17T08:00:00+00:00"}


def a_candidate_record(shape: str, digest: str) -> dict:
    return {"id": f"lab:{shape}:{digest}", "shape": shape, "status": "enumerated",
            "members": [{"card": "plate_option:ken", "offset_s": 0.0, "role": "the world plate"},
                        {"card": "dock_kind:image", "offset_s": 2.5, "role": "the evidence still"}],
            "clocks": {"m44_plate_s": 6.0}, "source": "lab_enumerate beat-shapes.json test"}


def a_lab(tmp_path: Path, runs: list[dict], judgements: list[dict] | None = None,
          extra_runs: dict[str, list[dict]] | None = None) -> dict:
    """A whole lab on a temp path: the batch's run record, the enumerated candidates, an empty queue, the log."""
    batches = tmp_path / "batches"
    batches.mkdir(exist_ok=True)
    (batches / f"{BATCH}.jsonl").write_text("".join(json.dumps(r) + "\n" for r in runs), encoding="utf-8")
    for name, recs in (extra_runs or {}).items():
        (batches / f"{name}.jsonl").write_text("".join(json.dumps(r) + "\n" for r in recs), encoding="utf-8")
    ids = {r["id"] for r in runs} | {r["id"] for recs in (extra_runs or {}).values() for r in recs}
    cands = [a_candidate_record(*cid.split(":")[1:]) for cid in sorted(ids)]
    (tmp_path / "candidates.jsonl").write_text("".join(json.dumps(c) + "\n" for c in cands), encoding="utf-8")
    queue = tmp_path / "queue.json"
    queue.write_text(json.dumps({"schema": "review_queue.v1", "as_of": "2026-09-17", "head": "abc1234",
                                 "items": []}, indent=2) + "\n", encoding="utf-8")
    log = tmp_path / "judgements.jsonl"
    if judgements is not None:
        log.write_text("".join(json.dumps(j) + "\n" for j in judgements), encoding="utf-8")
    return {"batches": batches, "candidates": tmp_path / "candidates.jsonl", "queue": queue, "judgements": log}


def run(lab: dict, *mode: str) -> int:
    return LB.main([*mode, "--batch", BATCH, "--batches-dir", str(lab["batches"]), "--candidates",
                    str(lab["candidates"]), "--judgements", str(lab["judgements"]), "--queue", str(lab["queue"]),
                    "--root", str(ROOT), "--now", NOW])


def cards_of(lab: dict) -> list[dict]:
    return [i for i in json.loads(lab["queue"].read_text(encoding="utf-8"))["items"] if i["kind"] == "batch"]


# ---------------------------------------------------------------- grouping

def test_one_card_per_beat_shape_carrying_only_the_survivors(tmp_path):
    runs = [a_run_record(SHAPES[0], "00000001"), a_run_record(SHAPES[0], "00000002"),
            a_run_record(SHAPES[1], "00000003"), a_run_record(SHAPES[1], "00000004", survivor=False)]
    lab = a_lab(tmp_path, runs)
    assert run(lab, "--write") == 0
    cards = cards_of(lab)
    assert [c["id"] for c in cards] == [f"lab-{BATCH}-{SHAPES[0]}", f"lab-{BATCH}-{SHAPES[1]}"]
    assert [[c["id"] for c in card["candidates"]] for card in cards] == [
        [f"lab:{SHAPES[0]}:00000001", f"lab:{SHAPES[0]}:00000002"], [f"lab:{SHAPES[1]}:00000003"]]
    assert all("00000004" not in json.dumps(card) for card in cards), "a candidate a gate killed never reaches a card"


def test_the_written_cards_validate_as_batch_records(tmp_path):
    lab = a_lab(tmp_path, [a_run_record(SHAPES[0], "00000001"), a_run_record(SHAPES[0], "00000002")])
    assert run(lab, "--write") == 0
    data = json.loads(lab["queue"].read_text(encoding="utf-8"))
    BRQ.validate(data["items"])
    card = data["items"][0]
    assert card["kind"] == "batch" and LB.QUESTION in card["judge"]
    assert card["proofs"] == [c["proof"] for c in card["candidates"]]
    for cand in card["candidates"]:
        assert cand["proof"]["type"] == "clip" and cand["proof"]["build"] and cand["one_line"]
        assert cand["one_line"] == "plate_option:ken +0s, dock_kind:image +2.5s"
    assert any(w["path"].endswith("lab-sheet.png") for w in card["where"])


def test_a_batch_with_no_survivor_is_refused_by_name(tmp_path, capsys):
    lab = a_lab(tmp_path, [a_run_record(SHAPES[0], "00000001", survivor=False)])
    assert run(lab, "--write") == 2
    assert "no survivor in the run record" in capsys.readouterr().err


def test_a_candidate_missing_from_the_enumerated_space_is_refused_by_name(tmp_path, capsys):
    lab = a_lab(tmp_path, [a_run_record(SHAPES[0], "00000001")])
    lab["candidates"].write_text("", encoding="utf-8")
    assert run(lab, "--write") == 2
    assert "not in content/video_engine/effects/lab/candidates.jsonl" in capsys.readouterr().err


def test_a_run_record_with_no_clip_window_is_refused_by_name(tmp_path, capsys):
    rec = a_run_record(SHAPES[0], "00000001")
    del rec["clip"]
    lab = a_lab(tmp_path, [rec])
    assert run(lab, "--write") == 2
    assert "carries no clip window" in capsys.readouterr().err


# ---------------------------------------------------------------- the exploration draw

def test_the_exploration_draw_is_about_a_quarter_and_deterministic_for_a_seed():
    ids = [f"lab:{SHAPES[0]}:0000000{n}" for n in range(8)]
    draw = LB.exploration_draw(BATCH, SHAPES[0], ids)
    assert draw["k"] == 2 and len(draw["drawn"]) == 2 and set(draw["drawn"]) <= set(ids)
    assert draw["seed"] == f"{BATCH}:{SHAPES[0]}" and draw["share"] == LB.EXPLORATION_SHARE == 0.25
    assert LB.exploration_draw(BATCH, SHAPES[0], list(reversed(ids)))["drawn"] == draw["drawn"], "the same seed draws"
    assert LB.exploration_draw("other-batch", SHAPES[0], ids)["drawn"] != draw["drawn"]
    assert LB.exploration_draw(BATCH, SHAPES[0], ids[:1])["k"] == 0, "a single candidate rounds to none"
    assert LB.exploration_draw(BATCH, SHAPES[0], ids[:2])["k"] == 1


def test_the_draw_is_made_without_reference_to_any_learner(tmp_path):
    source = (ROOT / "content/video_engine/scripts/lab_batch.py").read_text(encoding="utf-8")
    assert "approval-rates" not in source and "approval_rates" not in source
    assert "lab_log" not in source, "the batch cards never read the learner's table (Gao et al. 2022)"
    lab = a_lab(tmp_path, [a_run_record(SHAPES[0], f"0000000{n}") for n in range(4)])
    assert run(lab, "--write") == 0
    card = cards_of(lab)[0]
    marked = [c["id"] for c in card["candidates"] if c.get("exploration")]
    assert marked == card["draw"]["drawn"] and len(marked) == 1
    assert card["draw"]["seed"] and "NO reference to any learner" in card["draw"]["why"]


# ---------------------------------------------------------------- the calibration probe

def a_judgement(candidate: str, at: str, bit: str = "approve", reason: str = "good") -> dict:
    return {"candidate": candidate, "bit": bit, "reason": reason, "proof": {"clip": "x.mp4", "t": 1.0},
            "at": at, "by": "operator", "answer_at": at}


def test_an_approval_older_than_fourteen_days_rides_along_as_a_calibration_probe(tmp_path):
    old = a_run_record(SHAPES[0], "000000aa")
    lab = a_lab(tmp_path, [a_run_record(SHAPES[0], "00000001")],
                judgements=[a_judgement(old["id"], "2026-08-01T10:00:00+00:00")],
                extra_runs={"older-r0": [old]})
    assert run(lab, "--write") == 0
    card = cards_of(lab)[0]
    probe = [c for c in card["candidates"] if c.get("calibration")]
    assert len(probe) == 1 and probe[0]["id"] == old["id"] and probe[0]["reason"] == "good"
    assert "2026-08-01" in probe[0]["label"] and "CALIBRATION PROBE" in card["judge"]
    assert card["proofs"][-1] == probe[0]["proof"], "the probe's clip is mirrored like every other candidate"
    BRQ.validate(json.loads(lab["queue"].read_text(encoding="utf-8"))["items"])


def test_an_approval_younger_than_fourteen_days_is_not_a_probe(tmp_path):
    old = a_run_record(SHAPES[0], "000000aa")
    lab = a_lab(tmp_path, [a_run_record(SHAPES[0], "00000001")],
                judgements=[a_judgement(old["id"], "2026-09-10T10:00:00+00:00")],
                extra_runs={"older-r0": [old]})
    assert run(lab, "--write") == 0
    assert not [c for c in cards_of(lab)[0]["candidates"] if c.get("calibration")]


def test_a_denial_is_never_a_calibration_probe(tmp_path):
    old = a_run_record(SHAPES[0], "000000aa")
    lab = a_lab(tmp_path, [a_run_record(SHAPES[0], "00000001")],
                judgements=[a_judgement(old["id"], "2026-08-01T10:00:00+00:00", bit="deny", reason="too-fast")],
                extra_runs={"older-r0": [old]})
    assert run(lab, "--write") == 0
    assert not [c for c in cards_of(lab)[0]["candidates"] if c.get("calibration")]


def test_the_probe_is_skipped_by_name_when_no_batch_record_carries_the_approved_candidate(tmp_path, capsys):
    lab = a_lab(tmp_path, [a_run_record(SHAPES[0], "00000001")],
                judgements=[a_judgement(f"lab:{SHAPES[0]}:000000ff", "2026-08-01T10:00:00+00:00")])
    assert run(lab, "--write") == 0
    assert "no probe attached" in capsys.readouterr().err
    assert not [c for c in cards_of(lab)[0]["candidates"] if c.get("calibration")]


def test_a_missing_judgements_file_is_simply_no_probe(tmp_path):
    lab = a_lab(tmp_path, [a_run_record(SHAPES[0], "00000001")])
    assert not lab["judgements"].exists()
    assert run(lab, "--write") == 0
    assert not [c for c in cards_of(lab)[0]["candidates"] if c.get("calibration")]


# ---------------------------------------------------------------- --check

def test_check_passes_on_what_write_wrote_and_names_a_card_that_drifted(tmp_path, capsys):
    lab = a_lab(tmp_path, [a_run_record(SHAPES[0], "00000001"), a_run_record(SHAPES[1], "00000002")])
    assert run(lab, "--write") == 0
    capsys.readouterr()
    assert run(lab, "--check") == 0
    assert "2 card(s)" in capsys.readouterr().out
    data = json.loads(lab["queue"].read_text(encoding="utf-8"))
    data["items"][1]["candidates"][0]["one_line"] = "something a hand typed"
    lab["queue"].write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    assert run(lab, "--check") == 1
    assert f"STALE: lab-{BATCH}-{SHAPES[1]}" in capsys.readouterr().err


def test_write_is_idempotent_and_touches_no_other_record(tmp_path):
    lab = a_lab(tmp_path, [a_run_record(SHAPES[0], "00000001")])
    data = json.loads(lab["queue"].read_text(encoding="utf-8"))
    data["items"].append({"id": "someone-elses-card", "kind": "owed", "status": "open", "title": "not ours",
                          "ids": ["x"], "judge": "?", "where": [{"label": "l", "path": "p"}], "options": [],
                          "recommendation": "", "blocks": "", "sources": [], "ruling": "", "owed": "a proof"})
    lab["queue"].write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    assert run(lab, "--write") == 0
    first = lab["queue"].read_bytes()
    assert run(lab, "--write") == 0
    assert lab["queue"].read_bytes() == first, "the same batch written twice is the same file"
    items = json.loads(lab["queue"].read_text(encoding="utf-8"))["items"]
    assert [i["id"] for i in items] == ["someone-elses-card", f"lab-{BATCH}-{SHAPES[0]}"]


def test_the_queue_files_own_line_endings_are_kept(tmp_path):
    lab = a_lab(tmp_path, [a_run_record(SHAPES[0], "00000001")])
    lab["queue"].write_bytes(lab["queue"].read_bytes().replace(b"\n", b"\r\n"))
    assert run(lab, "--write") == 0
    raw = lab["queue"].read_bytes()
    assert b"\r\n" in raw and b"\n" not in raw.replace(b"\r\n", b"")


# ---------------------------------------------------------------- the server's one new branch

def a_batch_card() -> dict:
    cands = [{"id": f"lab:{SHAPES[0]}:0000000{n}", "label": f"c{n}", "one_line": "plate +0s",
              "proof": {"type": "clip", "label": f"c{n}", "t0": 0.0, "t1": 6.0, "build": "b", "route": "r"}}
             for n in range(2)]
    return {"id": f"lab-{BATCH}-{SHAPES[0]}", "kind": "batch", "status": "open", "options": [],
            "candidates": cands, "proofs": [c["proof"] for c in cands]}


@pytest.fixture()
def items_by_id() -> dict:
    card = a_batch_card()
    return {card["id"]: card, "r26-1-a-plain-card": {"id": "r26-1-a-plain-card", "kind": "rule", "options": ["hold"]}}


def item_of(n: int = 0) -> str:
    card = a_batch_card()
    return f'{card["id"]}{BRQ.BATCH_SEP}{card["candidates"][n]["id"]}'


def test_a_good_candidate_answer_is_accepted(items_by_id):
    body = {"item": item_of(), "choice": "approve", "note": "good: the plate holds its six seconds"}
    assert SRQ.refuse_reason(body, items_by_id) is None
    assert SRQ.refuse_reason({**body, "choice": "deny", "note": "illegible-at-9-16: the rails vanish"},
                             items_by_id) is None


@pytest.mark.parametrize("body, reason", [
    ({"item": item_of(), "choice": "approve", "note": "it just works"}, "opens with a reason from the list"),
    ({"item": item_of(), "choice": "approve", "note": "brilliant: a reason of my own"},
     "opens with a reason from the list"),
    ({"item": item_of(), "choice": "approve", "note": None}, "opens with a reason from the list"),
    ({"item": item_of(), "choice": "hold", "note": "good: x"}, "invalid choice 'hold'"),
    ({"item": f"lab-{BATCH}-{SHAPES[0]}#lab:{SHAPES[0]}:deadbeef", "choice": "deny", "note": "too-fast: x"},
     "unknown candidate"),
    ({"item": "r26-1-a-plain-card#lab:x:00000000", "choice": "deny", "note": "too-fast: x"}, "unknown batch"),
    ({"item": "no-such-card#lab:x:00000000", "choice": "deny", "note": "too-fast: x"}, "unknown batch"),
])
def test_a_bad_candidate_answer_is_refused_by_name(items_by_id, body, reason):
    refusal = SRQ.refuse_reason(body, items_by_id)
    assert refusal and reason in refusal


def test_a_candidate_note_over_the_maximum_is_still_refused(items_by_id):
    body = {"item": item_of(), "choice": "approve", "note": "good: " + "x" * SRQ.NOTE_MAX}
    assert "over NOTE_MAX" in SRQ.refuse_reason(body, items_by_id)


def test_the_plain_card_grammar_is_untouched(items_by_id):
    assert SRQ.refuse_reason({"item": "r26-1-a-plain-card", "choice": "hold", "note": ""}, items_by_id) is None
    assert "invalid choice" in SRQ.refuse_reason({"item": "r26-1-a-plain-card", "choice": "approve", "note": ""},
                                                 items_by_id)


def test_every_reason_the_page_offers_is_accepted_by_the_server(items_by_id):
    for reason in BRQ.REASONS:
        body = {"item": item_of(1), "choice": "approve" if reason == "good" else "deny", "note": f"{reason}: why"}
        assert SRQ.refuse_reason(body, items_by_id) is None, reason


# ---------------------------------------------------------------- HG2: the fifteen re-proved (P65 T8)

REPROOF = "reproof-r1"
REPROOF_RECORD = ROOT / "content/video_engine/effects/lab/batches" / f"{REPROOF}.jsonl"
HG2_OWED = {"id": LB.HG2_CARD_ID, "status": "open", "kind": "owed", "ids": ["P65 HG2"], "title": "P65 HG2 - owed",
            "judge": "the re-proof run has not built yet", "where": [{"label": "the plan", "path": "x.md"}],
            "proofs": [], "options": [], "recommendation": "", "blocks": "P65 T6", "sources": ["the plan"],
            "ruling": "", "was_kind": "", "owed": "the re-proof run P65 T8 is building now"}


def a_queue_holding_the_owed_row(tmp_path: Path) -> Path:
    queue = tmp_path / "queue-hg2.json"
    queue.write_text(json.dumps({"schema": "review_queue.v1", "as_of": "2026-09-17", "head": "abc1234",
                                 "items": [dict(HG2_OWED)]}, indent=2) + "\n", encoding="utf-8")
    return queue


def run_hg2(queue: Path, *mode: str) -> int:
    return LB.main([*mode, "--batch", REPROOF, "--hg2", "--record", str(REPROOF_RECORD),
                    "--queue", str(queue), "--root", str(ROOT)])


def reproof_records() -> list[dict]:
    return LB.read_jsonl(REPROOF_RECORD)


def hg2_of(queue: Path) -> dict:
    items = json.loads(queue.read_text(encoding="utf-8"))["items"]
    assert len(items) == 1, "the flip replaces the owed row in place; it never appends a second one"
    return items[0]


def test_hg2_flips_the_owed_row_in_place_to_a_batch(tmp_path):
    queue = a_queue_holding_the_owed_row(tmp_path)
    assert run_hg2(queue, "--write") == 0
    card = hg2_of(queue)
    assert card["id"] == LB.HG2_CARD_ID and card["kind"] == "batch" and card["was_kind"] == "owed"
    assert card["owed"] == "" and card["status"] == "open"
    assert LB.HG2_QUESTION in card["judge"] and card["options"] == LB.HG2_OPTIONS
    assert "0.60" in card["recommendation"] and "R26-168" in card["blocks"]


def test_hg2_cards_only_the_recipes_still_standing(tmp_path):
    queue = a_queue_holding_the_owed_row(tmp_path)
    assert run_hg2(queue, "--write") == 0
    card = hg2_of(queue)
    standing = [r for r in reproof_records() if LB.verdict_class(r) in ("proven", "amended")]
    assert [c["id"] for c in card["candidates"]] == [r["id"] for r in standing]
    assert [c["label"] for c in card["candidates"]] == [r["recipe"] for r in standing]
    assert [c["one_line"] for c in card["candidates"]] == [r["verdict"] for r in standing]


def test_hg2_names_every_casualty_in_the_judge_text_and_cards_none_of_them(tmp_path):
    queue = a_queue_holding_the_owed_row(tmp_path)
    assert run_hg2(queue, "--write") == 0
    card = hg2_of(queue)
    gone = [r for r in reproof_records() if LB.verdict_class(r) == "unreachable"]
    carded = json.dumps(card["candidates"])
    for rec in gone:
        assert rec["recipe"] in card["judge"], f"{rec['recipe']} is retired without being named"
        assert LB.killing_row(rec) in card["judge"], f"{rec['recipe']} is named without the row that killed it"
        assert rec["recipe"] not in carded, "a casualty's build carries the killing row, not a beat (E99 s60)"
    assert str(len(gone)) in card["judge"]


def test_hg2_carries_no_exploration_draw_and_no_calibration_probe(tmp_path):
    queue = a_queue_holding_the_owed_row(tmp_path)
    assert run_hg2(queue, "--write") == 0
    card = hg2_of(queue)
    assert "draw" not in card
    assert not any(c.get("exploration") or c.get("calibration") for c in card["candidates"])
    assert "NO exploration draw and NO calibration probe" in card["judge"]


def test_the_hg2_card_validates_as_a_batch_record_with_its_proofs_mirroring(tmp_path):
    queue = a_queue_holding_the_owed_row(tmp_path)
    assert run_hg2(queue, "--write") == 0
    card = hg2_of(queue)
    BRQ.validate_batch(card["id"], card)
    BRQ.validate(json.loads(queue.read_text(encoding="utf-8"))["items"])
    assert card["proofs"] == [c["proof"] for c in card["candidates"]]
    for cand in card["candidates"]:
        assert cand["proof"]["type"] == "clip" and cand["proof"]["build"].endswith(cand["id"].replace(":", "-"))
        assert cand["proof"]["label"].startswith(cand["label"])


def test_hg2_check_passes_on_what_it_wrote_and_fails_on_a_drifted_card(tmp_path, capsys):
    queue = a_queue_holding_the_owed_row(tmp_path)
    assert run_hg2(queue, "--write") == 0
    assert run_hg2(queue, "--check") == 0
    data = json.loads(queue.read_text(encoding="utf-8"))
    data["items"][0]["candidates"].pop()
    queue.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    assert run_hg2(queue, "--check") == 1
    assert LB.HG2_CARD_ID in capsys.readouterr().err


def test_a_verdict_the_run_record_does_not_use_is_refused_by_name(tmp_path):
    with pytest.raises(LB.BatchError, match="the verdict is none of"):
        LB.verdict_class({"id": "recipe:x", "verdict": "looks fine to me"})


def test_the_card_reads_the_diagnosis_vocabulary_and_the_word_it_replaced():
    """E99 s69: the lab DIAGNOSES, so a record's third answer is a diagnosis - and this module is a READER of
    records on disk, so batch reproof-r1's retired word still reads. Nothing is re-decided here."""
    assert LB.verdict_class({"id": "r", "diagnosis": "buildable as-is"}) == "as-is"
    said = {"id": "r", "verdict": "buildable with a companion - M16: the hole opens at 0:39 and runs 5.7 s, past "
                                 "the recipe's last member landing at 41.76s - slot the next beat there"}
    assert LB.verdict_class(said) == "companion"
    assert LB.killing_row(said).startswith("M16: the hole opens at 0:39")
    assert LB.verdict_class({"id": "r", "diagnosis": "not on this bed - dock_payload:stack"}) == "not on this bed"
    assert LB.verdict_class({"id": "r", "diagnosis": "a light is not a move - the named thing should arrive "
                                                     "(E99 s71)"}) == "light-only"
    assert LB.verdict_class({"id": "r", "verdict": "unreachable under the clocks: [FAIL] M05"}) == "unreachable"
    assert "companion" in LB.STANDING and "unreachable" not in LB.STANDING
