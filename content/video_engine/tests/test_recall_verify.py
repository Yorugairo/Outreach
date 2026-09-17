"""THE VERIFIED RECEIPT (P67 T1): every pin is a way the receipt could be typed instead of read.

The pins: a good nine-stage block passes; a stage with no line is refused BY NAME; the tolerance is the EXACT
line (a span one line off is refused and the message names the line the span is really on); a span under twelve
characters is refused; a span that moved anywhere in the file is reported "moved to <path>:<N> - cite that"; a
span that is nowhere in the file says so and prints the line it read; a legacy `- Recall:` line parses with
stage=None and is reported UNSTAGED, never dropped; a ledger carrying two `## Recall` headings is verified on
the LAST one and the report names which heading it read; a `0 hits` claim the record answers is refused with the
first hit printed (the subprocess is monkeypatched - the live index is not a unit-test dependency) and one it
does not answer passes; the CLI exits 0 and 1. Every write goes to tmp_path; the module itself writes nothing.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import recall_verify as RV  # noqa: E402

DOC_LINES = [
    "# The doctrine page",                                          # 1
    "",                                                             # 2
    "The package answers the thumbnail in the first sentence.",      # 3
    "The script's spine is the full video map.",                     # 4
    "The voice pack holds the calibration pair.",                    # 5
    "A world is a place the camera can stand in.",                   # 6
    "Evidence is a chart that proves one sentence.",                 # 7
    "Motion is an event every two and a half seconds.",              # 8
    "Sound   is a bed at   minus twenty loudness units.",            # 9 (whitespace runs, on purpose)
    "Publishing is the package first, the cut second.",              # 10
    "The rulings outrank my recollection every time.",               # 11
]

GOOD = [
    ("package", 3, "answers the thumbnail"),
    ("script", 4, "spine is the full video map"),
    ("voice", 5, "holds the calibration pair"),
    ("world", 6, "the camera can stand in"),
    ("evidence", 7, "proves one sentence"),
    ("motion", 8, "every two and a half seconds"),
    ("sound", 9, "minus twenty loudness units"),
    ("publish", 10, "the package first"),
    ("rulings", 11, "outrank my recollection"),
]

DOC_REL = "docs/doctrine.md"


def cite(stage: str, line: int, span: str, note: str = "why it was read") -> str:
    return f'- Recall({stage}): {DOC_REL}:{line} "{span}" ({note})'


def ledger_text(rows: list[str], heading: str = "## Recall", after: str = "") -> str:
    body = "\n".join(rows)
    return (f"# PRODUCTION LEDGER - a fixture project\n\nSome prose before the block.\n\n"
            f"{heading}\n{body}\n\n## Decisions taken\n1. a decision.\n{after}")


def good_rows() -> list[str]:
    return [cite(stage, line, span) for stage, line, span in GOOD]


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    (tmp_path / "docs").mkdir()
    (tmp_path / DOC_REL).write_text("\n".join(DOC_LINES) + "\n", encoding="utf-8")
    (tmp_path / "proj").mkdir()
    return tmp_path


def write_ledger(repo: Path, rows: list[str], **kw) -> Path:
    path = repo / "proj" / RV.LEDGER_NAME
    path.write_text(ledger_text(rows, **kw), encoding="utf-8")
    return path


def test_the_nine_stages_are_the_runbooks_order():
    assert RV.STAGES == ("package", "script", "voice", "world", "evidence", "motion", "sound", "publish", "rulings")


def test_a_good_nine_stage_block_verifies(repo: Path):
    write_ledger(repo, good_rows())
    ok, lines = RV.verify(repo, repo / "proj")
    report = "\n".join(lines)
    assert ok, report
    assert "PASS - 9 citation(s) verified across 9 stages." in lines[-1]
    for stage in RV.STAGES:
        assert f"  {stage}: 1 citation(s) verified" in lines, report


def test_the_episode_dir_and_the_ledger_path_are_the_same_target(repo: Path):
    path = write_ledger(repo, good_rows())
    assert RV.verify(repo, path)[0] and RV.verify(repo, repo / "proj")[0]


def test_a_missing_stage_is_refused_by_name(repo: Path):
    write_ledger(repo, [r for r in good_rows() if "Recall(sound)" not in r])
    ok, lines = RV.verify(repo, repo / "proj")
    report = "\n".join(lines)
    assert not ok
    assert 'REFUSED stage "sound" - no citation at all' in report
    assert "Recall(sound): <path>:<line>" in report, "the refusal carries the repair"
    assert 'REFUSED stage "motion"' not in report, "only the stage that is missing is named"


def test_the_exact_line_tolerance_a_span_one_line_off_is_refused_and_the_real_line_named(repo: Path):
    """The tolerance is the EXACT line, never the line plus or minus one (P67 Execution Path)."""
    rows = [r for r in good_rows() if "Recall(voice)" not in r]
    rows.append(cite("voice", 4, "holds the calibration pair"))  # the span lives on line 5
    write_ledger(repo, rows)
    ok, lines = RV.verify(repo, repo / "proj")
    report = "\n".join(lines)
    assert not ok, report
    assert "line 4 does not carry the span" in report
    assert f"the span moved to {DOC_REL}:5 - cite that" in report


def test_a_span_that_moved_across_the_file_is_reported_where_it_went(repo: Path):
    rows = [r for r in good_rows() if "Recall(rulings)" not in r]
    rows.append(cite("rulings", 3, "outrank my recollection"))  # really on line 11
    write_ledger(repo, rows)
    ok, lines = RV.verify(repo, repo / "proj")
    assert not ok
    assert f"the span moved to {DOC_REL}:11 - cite that" in "\n".join(lines)


def test_a_span_nowhere_in_the_file_says_so_and_prints_the_line_it_read(repo: Path):
    rows = [r for r in good_rows() if "Recall(world)" not in r]
    rows.append(cite("world", 6, "a sentence nobody ever wrote here"))
    write_ledger(repo, rows)
    ok, lines = RV.verify(repo, repo / "proj")
    report = "\n".join(lines)
    assert not ok
    assert f"it is nowhere in {DOC_REL}" in report
    assert "A world is a place the camera can stand in." in report


def test_a_span_under_twelve_characters_is_refused(repo: Path):
    rows = [r for r in good_rows() if "Recall(motion)" not in r]
    rows.append(cite("motion", 8, "an event"))
    write_ledger(repo, rows)
    ok, lines = RV.verify(repo, repo / "proj")
    report = "\n".join(lines)
    assert not ok
    assert "the span is 8 characters; a span is at least 12" in report


def test_whitespace_runs_collapse_but_the_case_does_not(repo: Path):
    rows = [r for r in good_rows() if "Recall(sound)" not in r]
    rows.append(cite("sound", 9, "Sound    is a bed"))  # line 9 has runs of spaces; the case matches
    write_ledger(repo, rows)
    assert RV.verify(repo, repo / "proj")[0]
    rows[-1] = cite("sound", 9, "SOUND is a bed at minus")
    write_ledger(repo, rows)
    ok, lines = RV.verify(repo, repo / "proj")
    assert not ok and "does not carry the span" in "\n".join(lines)


def test_a_path_that_is_absent_and_a_path_outside_the_repo_are_each_refused(repo: Path):
    rows = [r for r in good_rows() if "Recall(world)" not in r]
    rows.append('- Recall(world): docs/gone.md:3 "a span long enough to count" (absent)')
    rows.append('- Recall(world): ../outside.md:3 "a span long enough to count" (outside)')
    write_ledger(repo, rows)
    ok, lines = RV.verify(repo, repo / "proj")
    report = "\n".join(lines)
    assert not ok
    assert "no such file in the repo: docs/gone.md" in report
    assert "the path is outside the repo: ../outside.md" in report


def test_a_line_past_the_end_of_the_file_is_refused_with_the_files_length(repo: Path):
    rows = [r for r in good_rows() if "Recall(evidence)" not in r]
    rows.append(cite("evidence", 400, "proves one sentence"))
    write_ledger(repo, rows)
    ok, lines = RV.verify(repo, repo / "proj")
    assert not ok
    assert "line 400 is past the end of the file (11 lines)" in "\n".join(lines)


def test_a_legacy_recall_line_parses_unstaged_and_is_never_dropped(repo: Path):
    legacy = f"- Recall: {DOC_REL}:3 (the 2026-09-08 commit-receipt form, no stage)"
    block = RV.parse_block(ledger_text(good_rows() + [legacy]))
    assert len(block.citations) == 10
    assert [c.stage for c in block.unstaged()] == [None]
    write_ledger(repo, good_rows() + [legacy])
    ok, lines = RV.verify(repo, repo / "proj")
    report = "\n".join(lines)
    assert ok, report
    assert "UNSTAGED" in report and legacy in report
    assert "PASS - 9 citation(s) verified" in report, "an unstaged line is reported, never counted for a stage"


def test_the_last_recall_block_is_the_one_read_and_the_report_names_it(repo: Path):
    """The calibration case appends a dated block below the original; the last block is the receipt."""
    original = "## Recall (RECALL-RECEIPT: the record outranks my recollection)\n" \
               f"- Recall: {DOC_REL}:3 (what that pass actually read)\n\n## Decisions taken\n1. a decision.\n\n"
    path = repo / "proj" / RV.LEDGER_NAME
    path.write_text(original + "## Recall (verified, P67)\n" + "\n".join(good_rows()) + "\n", encoding="utf-8")
    ok, lines = RV.verify(repo, path)
    report = "\n".join(lines)
    assert ok, report
    assert '"## Recall (verified, P67)"' in report
    assert "the last of 2 `## Recall` headings" in report


def test_a_zero_hit_claim_the_record_answers_is_refused_with_the_first_hit(repo: Path, monkeypatch):
    hit = {"layer": "capabilities", "path": "docs/content-video-engine/CAPABILITIES.md", "line": 272,
           "name": "The recall receipt", "snippet": "LIVE - ..."}
    monkeypatch.setattr(RV, "docs_find_hits", lambda _repo, _term: [hit])
    rows = [r for r in good_rows() if "Recall(publish)" not in r]
    rows.append('- Recall(publish): docs_find 0 hits for "the recall receipt"')
    write_ledger(repo, rows)
    ok, lines = RV.verify(repo, repo / "proj")
    report = "\n".join(lines)
    assert not ok
    assert 'Recall(publish) docs_find 0 hits for "the recall receipt"' in report
    assert "the record answers with a hit: docs/content-video-engine/CAPABILITIES.md:272 - The recall receipt" in report


def test_a_zero_hit_claim_the_record_does_not_answer_passes(repo: Path, monkeypatch):
    seen = []
    monkeypatch.setattr(RV, "docs_find_hits", lambda _repo, term: seen.append(term) or [])
    rows = [r for r in good_rows() if "Recall(publish)" not in r]
    rows.append('- Recall(publish): docs_find 0 hits for "zzqqxx not a thing"')
    write_ledger(repo, rows)
    ok, lines = RV.verify(repo, repo / "proj")
    assert ok, "\n".join(lines)
    assert seen == ["zzqqxx not a thing"], "the claim is re-run through docs_find with the term as written"


def test_a_docs_find_that_cannot_run_is_named_unchecked_and_never_a_silent_pass(repo: Path, monkeypatch):
    def boom(_repo, _term):
        raise RuntimeError("docs_find exited 2")

    monkeypatch.setattr(RV, "docs_find_hits", boom)
    rows = [r for r in good_rows() if "Recall(publish)" not in r]
    rows.append('- Recall(publish): docs_find 0 hits for "a term"')
    write_ledger(repo, rows)
    ok, lines = RV.verify(repo, repo / "proj")
    assert ok
    assert any(ln.startswith("UNCHECKED") and "docs_find exited 2" in ln for ln in lines)


def test_a_ledger_with_no_recall_heading_and_a_missing_ledger_are_each_refused(repo: Path):
    (repo / "proj" / RV.LEDGER_NAME).write_text("# A ledger with no receipt\n\n## Decisions\n", encoding="utf-8")
    ok, lines = RV.verify(repo, repo / "proj")
    assert not ok and "carries no `## Recall` heading" in "\n".join(lines)
    ok, lines = RV.verify(repo, repo / "nowhere")
    assert not ok and "no ledger at" in "\n".join(lines)


def test_an_unknown_stage_name_is_refused_and_the_nine_are_printed(repo: Path):
    write_ledger(repo, good_rows() + [cite("packaging", 3, "answers the thumbnail")])
    ok, lines = RV.verify(repo, repo / "proj")
    report = "\n".join(lines)
    assert not ok
    assert 'unknown stage "packaging"' in report and "package script voice" in report


def test_the_cli_exits_0_on_a_good_receipt_and_1_on_a_refusal(repo: Path, capsys):
    write_ledger(repo, good_rows())
    assert RV.main([str(repo / "proj"), "--repo", str(repo)]) == 0
    assert "PASS - 9 citation(s) verified" in capsys.readouterr().out
    write_ledger(repo, [r for r in good_rows() if "Recall(voice)" not in r])
    assert RV.main([str(repo / "proj"), "--repo", str(repo)]) == 1
    assert 'REFUSED stage "voice"' in capsys.readouterr().out


def test_the_cli_json_carries_the_verdict_and_the_refusals(repo: Path, capsys):
    write_ledger(repo, [r for r in good_rows() if "Recall(world)" not in r])
    assert RV.main([str(repo / "proj"), "--json", "--repo", str(repo)]) == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is False
    assert any('stage "world"' in ln for ln in payload["refusals"])


def test_the_module_names_no_episode_and_no_project(repo: Path):
    """The authoring kit's rule: a mechanism holds no episode fact."""
    source = (ROOT / "content/video_engine/scripts/recall_verify.py").read_text(encoding="utf-8")
    for forbidden in ("projects/", "systems-and-blowups", "money-physics", "build-oneshot"):
        assert forbidden not in source


def test_the_verifier_writes_nothing(repo: Path):
    write_ledger(repo, good_rows())
    before = {p: p.stat().st_mtime_ns for p in sorted(repo.rglob("*")) if p.is_file()}
    assert RV.verify(repo, repo / "proj")[0]
    after = {p: p.stat().st_mtime_ns for p in sorted(repo.rglob("*")) if p.is_file()}
    assert before == after
