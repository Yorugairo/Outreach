"""One row, one verdict (CHECK-RESPONSIBILITIES R1; PRP P34 T6).

Once `run_script_gates` has written `<script>-GATES.md` beside a script, the
opening gate owns doc 38 beats 1-4 (hook 3s, paradox 8s, greetings, "you" by
0:30, promise in 60s, hook concreteness). The audit then emits ONE INFO
pointer at the report instead of restating those rows. Without the report,
behaviour is byte-identical, and no other audit row moves either way.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / "content/video_engine/scripts"
sys.path.insert(0, str(SCRIPTS))

import audit_script_doctrine as A     # noqa: E402
import run_script_gates as RG         # noqa: E402

DEFERRED_RULES = ("doc 38 beat 1", "doc 38 beat 2", "doc 38 beat 3", "doc 38 beat 4")
POINTER = "owned by gate_opening_structure"
# Trips beats 2 (greetings), 3 (no "you" inside 0:30) and 4 (no promise) and
# the beat-1 concreteness WARN (no direct address in the hook). No "you"
# anywhere, no "threshold": the doc-35 tell row FAILs in both runs.
OPENER = "Hey guys, welcome back to the channel. "
FILLER = "The mechanism underneath moved and almost nobody on the desk looked at it. "


def _pad_to(text: str, target_s: float) -> str:
    while A.secs(A.spoken(text)) < target_s:
        text += FILLER
    return text


def _script(tmp_path: Path) -> Path:
    path = tmp_path / "TEST-VO.txt"
    path.write_text(_pad_to(OPENER, 120.0), encoding="utf-8")
    return path


def _deferred(findings) -> list[str]:
    return [f.message for f in findings if f.rule in DEFERRED_RULES]


def _pointers(findings) -> list[str]:
    return [f.message for f in findings if POINTER in f.message]


def _others(findings) -> list[tuple[str, str, str]]:
    """Every row the gate does NOT own, in emission order."""
    return [(f.level, f.rule, f.message) for f in findings
            if f.rule not in DEFERRED_RULES and POINTER not in f.message]


def _write_stub_report(script: Path) -> Path:
    report = RG.report_path(script)
    report.write_text("# stub gates report\n", encoding="utf-8")
    return report


# ---- without a report: the rows are the audit's ----------------------------

def test_without_report_the_audit_emits_the_doc38_rows(tmp_path):
    script = _script(tmp_path)
    findings, _ = A.audit(script.read_text(encoding="utf-8"), script_path=script)

    rows = _deferred(findings)
    assert any("banned opener" in m for m in rows), rows
    assert any("direct address ('you')" in m for m in rows), rows
    assert any("no dated/checkable promise" in m for m in rows), rows
    assert _pointers(findings) == []


def test_without_report_path_and_no_path_are_identical(tmp_path):
    script = _script(tmp_path)
    text = script.read_text(encoding="utf-8")

    with_path = A.audit(text, script_path=script)
    without_path = A.audit(text)

    assert with_path == without_path


# ---- with a report: the gate owns them, the audit points -------------------

def test_with_report_the_rows_are_replaced_by_one_pointer(tmp_path):
    script = _script(tmp_path)
    report = _write_stub_report(script)
    findings, _ = A.audit(script.read_text(encoding="utf-8"), script_path=script)

    assert _deferred(findings) == []
    pointers = [f for f in findings if POINTER in f.message]
    assert len(pointers) == 1, [f.message for f in findings]
    assert pointers[0].level == "INFO"
    assert pointers[0].rule == "doc 38 B1-B4"
    assert str(report) in pointers[0].message


def test_rows_the_gate_does_not_own_do_not_move(tmp_path):
    script = _script(tmp_path)
    text = script.read_text(encoding="utf-8")
    before, stats_before = A.audit(text, script_path=script)
    _write_stub_report(script)
    after, stats_after = A.audit(text, script_path=script)

    assert _others(before) == _others(after)
    tell = ("FAIL", "doc 35 rule 2")
    assert any((f.level, f.rule) == tell for f in before)
    assert any((f.level, f.rule) == tell for f in after)
    assert stats_before == stats_after     # the beat stats are still computed


# ---- main(): the path flows through and the RESULT line keeps its shape ----

def test_main_prints_the_pointer_and_keeps_the_result_line(tmp_path, monkeypatch, capsys):
    script = _script(tmp_path)
    _write_stub_report(script)
    monkeypatch.setattr(sys, "argv", ["audit_script_doctrine.py", str(script)])

    A.main()
    out = capsys.readouterr().out

    assert out.count(POINTER) == 1, out
    assert not re.search(r"\[(?:FAIL|WARN)\] doc 38 beat [1-4]", out), out
    assert re.search(r"^RESULT: \d+ FAIL, \d+ WARN$", out, re.M), out


def test_defer_opening_flag_defers_before_the_report_exists(tmp_path):
    """The runner audits first and writes the report second; it says so, and the audit points at the path it will write."""
    script = _script(tmp_path)
    assert A.gate_report(script) is None
    findings, _ = A.audit(script.read_text(encoding="utf-8"), script_path=script, defer_opening=True)
    assert _deferred(findings) == []
    pointers = [f for f in findings if POINTER in f.message]
    assert len(pointers) == 1 and str(RG.report_path(script)) in pointers[0].message
    # without a script path there is nothing to point at: the rows stay
    findings, _ = A.audit(script.read_text(encoding="utf-8"), defer_opening=True)
    assert _deferred(findings) != []
