"""THE RECIPE LAB'S APPROVAL LOG AND ITS LEARNER (P65 T5).

The pins: the operator's real answers on the HG2 card derive to judgements that validate against
`lab_judgement.schema.json` - six live candidates, the bit and the reason category each, the clip and the instant -
and re-running derives the same bytes (a later answer for the same candidate supersedes the earlier, which is kept);
an off-list reason, an unknown candidate and a candidate with no clip are each REFUSED BY NAME and nothing is
written; a feature seen once is pulled toward the prior instead of printing 1.00 or 0.00; the reason categories are
carried per feature and never collapsed into the rate; and NO ranking or head-to-head preference model is computed
anywhere in the module (the source is grepped). Every write in this file goes to a temp root; the repo's own
answers are only ever READ.
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

import lab_log as LL  # noqa: E402

HG2 = "p65-hg2-the-reproved-set-and-m38"
THE_SIX = {
    "recipe:badge-ladder": ("approve", "good"),
    "recipe:read-park-build-write": ("approve", "good"),
    "recipe:spotlight-held-past-the-cut": ("deny", "reads-as-noise"),
    "recipe:plate-dock-wipe": ("deny", "off-doctrine"),
    "recipe:dock-lands-page-renames": ("deny", "off-doctrine"),
    "recipe:card-becomes-the-chart": ("deny", "off-doctrine"),
}
CARD = "lab-batch-t5-plate-carries-a-card"
BATCH = "t5-r1"
A = "lab:plate-carries-a-card:aaaaaaaa"
B = "lab:plate-carries-a-card:bbbbbbbb"


# ---------------------------------------------------------------- a temp lab


def a_run(cid: str, clip: bool = True) -> dict:
    rec = {"id": cid, "batch": BATCH, "shape": "plate-carries-a-card", "survivor": True,
           "beat": {"n": 3, "sentence": "a Treasury page, and your phone.", "t0": 10.0, "t1": 16.5},
           "at": "2026-09-17T08:00:00+00:00"}
    if clip:
        rec["build"] = f"content/video_engine/projects/x/build-lab-{BATCH}/{cid.rsplit(':', 1)[-1]}"
        rec["clip"] = {"t0": 10.0, "t1": 16.5}
    return rec


def a_candidate(cid: str) -> dict:
    """Two candidates of the same shape that differ in ONE member, so the table carries n=2 and n=1 cells both."""
    own = "arrival:throw" if cid == A else "exit:wipe"
    return {"id": cid, "shape": "plate-carries-a-card", "status": "enumerated",
            "members": [{"card": "plate_option:ken", "offset_s": 0.0, "role": "the world plate"},
                        {"card": "dock_kind:image", "offset_s": 2.5, "role": "the evidence still"},
                        {"card": own, "offset_s": 4.0, "role": "the member only this candidate carries"}],
            "clocks": {"m44_plate_s": 6.0}, "source": "lab_enumerate test"}


def a_card(ids: tuple[str, ...], clip: bool = True) -> dict:
    cands = []
    for cid in ids:
        proof = {"type": "clip", "label": cid, "route": "test"}
        if clip:
            proof |= {"t0": 10.0, "t1": 16.5,
                      "build": f"content/video_engine/projects/x/build-lab-{BATCH}/{cid.rsplit(':', 1)[-1]}"}
        cands.append({"id": cid, "label": cid, "one_line": "a beat", "proof": proof})
    return {"id": CARD, "kind": "batch", "status": "open", "title": "a test batch",
            "where": [{"label": "the run record",
                       "path": f"content/video_engine/effects/lab/batches/{BATCH}.jsonl"}],
            "candidates": cands}


def a_lab(tmp_path: Path, answers: list[dict], ids: tuple[str, ...] = (A, B), clip: bool = True) -> Path:
    root = tmp_path / "root"
    (root / "content/video_engine/configs").mkdir(parents=True)
    (root / "content/video_engine/effects/lab/batches").mkdir(parents=True)
    (root / "docs/content-video-engine").mkdir(parents=True)
    shutil.copy(ROOT / LL.SCHEMA_REL, root / LL.SCHEMA_REL)
    (root / LL.QUEUE_REL).write_text(json.dumps({"schema": "review_queue.v1", "items": [a_card(ids, clip)]}),
                                     encoding="utf-8")
    (root / LL.BATCHES_REL / f"{BATCH}.jsonl").write_text(
        "".join(json.dumps(a_run(cid, clip)) + "\n" for cid in ids), encoding="utf-8")
    (root / LL.CANDIDATES_REL).write_text("".join(json.dumps(a_candidate(cid)) + "\n" for cid in ids),
                                          encoding="utf-8")
    (root / LL.ANSWERS_REL).write_text("".join(json.dumps(a) + "\n" for a in answers), encoding="utf-8")
    return root


def an_answer(cid: str, choice: str, note: str, at: str) -> dict:
    return {"item": f"{CARD}#{cid}", "choice": choice, "note": note, "at": at, "by": "operator"}


# ---------------------------------------------------------------- the real six


def test_the_operators_six_answers_derive_to_six_live_judgements_that_validate():
    records, refusals = LL.derive(ROOT)
    assert refusals == []
    LL.validate(records, LL.load_schema(ROOT))          # the schema is the contract, every record
    live = [r for r in records if not r.get("superseded")]
    assert {r["candidate"]: (r["bit"], r["reason"]) for r in live} == THE_SIX
    assert len(live) == 6
    for rec in live:
        assert rec["by"] == "operator"
        assert rec["proof"]["clip"] and rec["proof"]["t"] >= 0
        assert rec["answer_at"].startswith("2026-09-17T")


def test_the_proof_is_the_cards_clip_at_its_t0_when_the_note_names_no_instant():
    records, _ = LL.derive(ROOT)
    badge = next(r for r in records if r["candidate"] == "recipe:badge-ladder")
    assert badge["proof"]["clip"].endswith("build-lab-reproof-r2/recipe-badge-ladder")
    assert badge["proof"]["t"] == 39.22                 # the clip's own t0 - the note names no second
    assert badge["note"].startswith("we should prefer to land on even pills")


def test_a_later_answer_supersedes_the_earlier_and_the_earlier_is_kept():
    records, _ = LL.derive(ROOT)
    wipe = [r for r in records if r["candidate"] == "recipe:plate-dock-wipe"]
    assert len(wipe) == 2
    early, late = sorted(wipe, key=lambda r: r["answer_at"])
    assert early["superseded"] is True and early["reason"] == "too-slow"
    assert "superseded" not in late and late["reason"] == "off-doctrine"


# ---------------------------------------------------------------- the instant a note names


@pytest.mark.parametrize("note,expected", [
    ("the light crosses at 12.5 s", 12.5),
    ("the card lands at 0:14 and the page holds", 14.0),
    ("held a still frame for 30 seconds", 10.0),      # a duration is not an instant; the clip's t0 stands
    ("nothing about time at all", 10.0),
    ("at 99.0 s - outside the clip", 10.0),
])
def test_the_instant_is_the_second_the_note_names_inside_the_clip(note, expected):
    assert LL.instant(note, 10.0, 16.5) == expected


# ---------------------------------------------------------------- refusals, by name


def test_an_off_list_reason_is_refused_by_name(tmp_path, capsys):
    root = a_lab(tmp_path, [an_answer(A, "deny", "meh: I do not like it", "2026-09-17T12:00:00-07:00")])
    assert LL.main(["--write", "--root", str(root)]) == 2
    out = capsys.readouterr().out
    assert "'meh'" in out and A in out and "not one of the nine reasons" in out
    assert not (root / LL.JUDGEMENTS_REL).exists()      # a refusal writes nothing


def test_an_unknown_candidate_is_refused_by_name(tmp_path, capsys):
    ghost = "lab:plate-carries-a-card:cccccccc"
    root = a_lab(tmp_path, [an_answer(ghost, "approve", "good: ", "2026-09-17T12:00:00-07:00")])
    assert LL.main(["--write", "--root", str(root)]) == 2
    out = capsys.readouterr().out
    assert f"unknown candidate '{ghost}'" in out and CARD in out


def test_a_candidate_with_no_clip_is_refused_by_name(tmp_path, capsys):
    root = a_lab(tmp_path, [an_answer(A, "approve", "good: ", "2026-09-17T12:00:00-07:00")], clip=False)
    assert LL.main(["--write", "--root", str(root)]) == 2
    out = capsys.readouterr().out
    assert A in out and "no clip proof" in out


# ---------------------------------------------------------------- idempotence


def test_a_second_write_is_byte_identical(tmp_path):
    root = a_lab(tmp_path, [an_answer(A, "approve", "good: it reads", "2026-09-17T12:00:00-07:00"),
                            an_answer(B, "deny", "too-fast: gone before I read it", "2026-09-17T12:05:00-07:00"),
                            an_answer(B, "deny", "off-doctrine: a dip into a mount", "2026-09-17T12:09:00-07:00")])
    assert LL.main(["--write", "--root", str(root)]) == 0
    first = (root / LL.JUDGEMENTS_REL).read_bytes()
    assert LL.main(["--write", "--root", str(root)]) == 0
    assert (root / LL.JUDGEMENTS_REL).read_bytes() == first
    assert LL.main(["--check", "--root", str(root)]) == 0
    assert first.decode("utf-8").count("\n") == 3       # three answers, three records, one of them superseded


# ---------------------------------------------------------------- the learner


def test_a_single_observation_cell_is_pulled_toward_the_prior_and_never_prints_1_or_0(tmp_path):
    root = a_lab(tmp_path, [an_answer(A, "approve", "good: it reads", "2026-09-17T12:00:00-07:00"),
                            an_answer(B, "approve", "good: it reads", "2026-09-17T12:05:00-07:00")])
    records, refusals = LL.derive(root)
    assert refusals == []
    data = LL.table(root, records)
    singles = [row for row in data["features"] if row["n"] == 1]
    assert singles, "the two candidates differ in no feature - the fixture must carry one"
    for row in singles:
        assert row["raw_rate"] == 1.0
        assert 0.0 < row["rate"] < 1.0
    every = [row for row in data["features"] if row["n"] == 2]
    assert every and all(row["rate"] < 1.0 for row in every)
    assert LL.shrunk(1, 1, data["prior"]["rate"]) < 1.0
    assert LL.shrunk(0, 1, data["prior"]["rate"]) > 0.0


def test_the_prior_is_named_with_its_numbers_and_the_count_is_behind_every_cell():
    records, _ = LL.derive(ROOT)
    data = LL.table(ROOT, records)
    p = data["prior"]
    assert p["family"] == "Beta" and p["strength"] == LL.PRIOR_STRENGTH
    assert p["a"] == pytest.approx(LL.PRIOR_STRENGTH * p["rate"], abs=1e-3)
    assert p["b"] == pytest.approx(LL.PRIOR_STRENGTH * (1 - p["rate"]), abs=1e-3)
    assert p["a"] + p["b"] == pytest.approx(LL.PRIOR_STRENGTH, abs=1e-3)
    assert data["judgements"]["live"] == 6
    for row in data["features"]:
        assert row["n"] == row["approve"] + row["deny"] >= 1
        assert row["kind"] in LL.FEATURE_KINDS
        assert row["rate"] == pytest.approx(LL.shrunk(row["approve"], row["n"], p["rate"]), abs=1e-3)
    md = LL.table_md(data)
    assert f"Beta(a={p['a']}, b={p['b']})" in md
    assert "arXiv 2411.04991" in md and "Gao et al. 2022" in md


def test_the_reasons_are_carried_per_feature_and_never_collapsed_into_the_rate():
    records, _ = LL.derive(ROOT)
    data = LL.table(ROOT, records)
    for row in data["features"]:
        assert row["reasons"], f"{row['feature']} carries no reason"
        assert sum(row["reasons"].values()) == row["n"]
        assert set(row["reasons"]) <= set(LL.BRQ.REASONS)
    spot = next(r for r in data["features"] if r["feature"] == "member:species:spotlight")
    assert spot["reasons"] == {"reads-as-noise": 1}     # the WHY survives beside the rate
    md = LL.table_md(data)
    assert "reads-as-noise x1" in md and "reasons (carried, never collapsed)" in md


def test_the_three_feature_kinds_are_the_shape_the_members_and_the_clock():
    records, _ = LL.derive(ROOT)
    data = LL.table(ROOT, records)
    kinds = {row["kind"] for row in data["features"]}
    assert kinds == {"shape", "member", "clock"}
    names = {row["feature"] for row in data["features"]}
    assert "shape:plate-carries-a-card" in names
    assert "member:dock_option:badge" in names
    assert any(n.startswith("clock:") for n in names)


def test_no_ranking_and_no_head_to_head_model_is_computed_anywhere_in_the_module():
    source = (ROOT / "content/video_engine/scripts/lab_log.py").read_text(encoding="utf-8").lower()
    for banned in ("bradley", "pairwise", "elo"):
        assert banned not in source, f"lab_log.py names {banned!r} - the learner is a table (E99 s68 Q5 = B)"
    for banned in ("logistic", "softmax", "argsort", "rank("):
        assert banned not in source, f"lab_log.py computes {banned!r} - no ranking model until the hundreds"
