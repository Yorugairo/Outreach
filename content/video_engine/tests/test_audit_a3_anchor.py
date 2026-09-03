"""A3 at 10% of runtime (ruling E23): kit_spec owns the figure, the audit and
the opening gate both call it, and the audit prints the computed target -
never the 3:00 that was only the @30:00 column of the rule.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / "content/video_engine/scripts"
sys.path.insert(0, str(SCRIPTS))

import audit_script_doctrine as A     # noqa: E402
import gate_opening_structure as G    # noqa: E402
import kit_spec                       # noqa: E402

EP = ROOT / "content/video_engine/projects/systems-and-blowups/steel-and-paper"
SCRIPT = EP / "SCRIPT-G-VO.txt"
needs_ep1 = pytest.mark.skipif(not SCRIPT.exists(), reason="episode one script not on disk")

FILLER = "The mechanism underneath moved and almost nobody on the desk looked at it. "


def _pad_to(text: str, target_s: float) -> str:
    while A.secs(A.spoken(text)) < target_s:
        text += FILLER
    return text


def _clock(mmss: str) -> float:
    m, _, s = mmss.partition(":")
    return int(m) * 60 + int(s)


def _anchor_warn(findings):
    return next((f for f in findings if f.rule == "MAP sec 2" and "anchor(s)" in f.message), None)


# ---- kit_spec owns the anchor ---------------------------------------------

def test_a3_anchor_is_ten_percent_of_runtime():
    assert kit_spec.a3_anchor_s(806) == pytest.approx(80.6)
    assert kit_spec.a3_anchor_s(1800) == 180.0


def test_phase_shares_match_the_audit_geometry():
    assert kit_spec.P3_GAP_SHARE == tuple(p / 100 for p in A.P3_GAP_PCT)
    assert kit_spec.P5_REFLECTION_SHARE == tuple(p / 100 for p in A.P5_REFLECTION_PCT)


def test_unit_windows_split_p3_and_p5_contiguously():
    runtime = 806.0
    n = kit_spec.unit_count(runtime / 60)
    windows = kit_spec.unit_windows(runtime)
    assert len(windows) == 2 * n
    p3, p5 = windows[:n], windows[n:]
    assert p3[0][0] == pytest.approx(runtime * 0.17) and p3[-1][1] == pytest.approx(runtime * 0.45)
    assert p5[0][0] == pytest.approx(runtime * 0.55) and p5[-1][1] == pytest.approx(runtime * 0.87)
    for group in (p3, p5):
        assert all(lo < hi for lo, hi in group)
        for (_, a_hi), (b_lo, _) in zip(group, group[1:]):
            assert a_hi == pytest.approx(b_lo)          # contiguous, no holes


# ---- the audit prints the computed A3 -------------------------------------

def test_audit_warns_with_computed_a3_not_three_minutes():
    text = _pad_to("The safest thing you own looks like this. An iron spike. ", 806.0)
    findings, stats = A.audit(text)
    warn = _anchor_warn(findings)
    assert warn is not None, [f.message for f in findings]
    assert "A3" in warn.message and "3:00" not in warn.message, warn.message
    m = re.search(r"A3 ~(1:[12]\d)", warn.message)
    assert m, warn.message
    assert stats["a3_anchor"] == m.group(1)
    assert _clock(stats["a3_anchor"]) == pytest.approx(stats["runtime_s"] * 0.10, abs=1.0)


def test_audit_and_gate_compute_the_same_a3_for_the_same_text():
    text = _pad_to("The safest thing you own looks like this. An iron spike. ", 806.0)
    _, audit_stats = A.audit(text)
    _, gate_stats = G.run(text, None)
    # the two tools time the same text within a few chars per sentence boundary
    assert _clock(audit_stats["a3_anchor"]) == pytest.approx(_clock(gate_stats["a3_anchor"]), abs=2.0)


@needs_ep1
def test_audit_on_episode_one_targets_a3_near_one_twenty():
    findings, stats = A.audit(SCRIPT.read_text(encoding="utf-8"))
    # ~14:12 estimated -> A3 ~1:25, not 3:00. Episode one's promise line (~1:20,
    # an A1-family construction) sits inside the 45s tolerance, so the anchor
    # WARN may stay silent; the target itself is what changed.
    assert re.match(r"1:[12]\d$", stats["a3_anchor"]), stats["a3_anchor"]
    assert _clock(stats["a3_anchor"]) == pytest.approx(stats["runtime_s"] * 0.10, abs=1.0)
    assert not any("A3 ~3:00" in f.message for f in findings), [f.message for f in findings]
