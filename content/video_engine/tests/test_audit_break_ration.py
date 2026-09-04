"""doc 37 sec 1: the break ration counts the marks that become TTS breaks - nothing else.

Beat tags ([archetype], [payoff], [ring], ...) are authoring metadata, stripped before
synthesis by beat_tags.strip_beat_tags; they never reach the voice and cannot cause the
audible speed-ups the ration exists to prevent. Only DELIVERY marks ([pre-key],
[post-key], [verify]) compile into <break> tags.

Until 2026-09-03 the audit counted every bracket mark, so a well-annotated 90-second
short failed by arithmetic (11 tags in 1.5k chars = 7/1k) while Script G slid under
the 3.0 cap at 2.8/1k on length alone. A gate that fails the better-annotated script
is measuring annotation, not delivery.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import audit_script_doctrine as A  # noqa: E402

FILLER = "The customs monitor prints the number every month and nobody on cable reads it. "


def _ration_findings(text: str):
    findings, stats = A.audit(text)
    return [f for f in findings if "break ration" in f.message], stats


def test_beat_tags_do_not_count_as_breaks():
    # 12 beat tags + ONE post-key in ~600 chars: dense annotation, one real break
    tags = ["[archetype]", "[stakes]", "[payoff]", "[rehook]", "[promise]", "[ring]",
            "[opponent]", "[loop-close]", "[tricolon]", "[reflect]", "[new]", "[concede]"]
    text = "Your costs jumped anyway. [post-key] " + " ".join(f"{t} {FILLER}" for t in tags)
    fails, stats = _ration_findings(text)
    assert not fails, f"beat tags were counted as TTS breaks: {[f.message for f in fails]}"
    assert stats["break_ration"] < A.BREAK_RATION_MAX


def test_delivery_marks_still_count():
    # 5 post-keys in ~600 chars is a real speed-up hazard and must still FAIL
    text = " ".join(f"[post-key] {FILLER}" for _ in range(5))
    fails, stats = _ration_findings(text)
    assert fails, "five delivery breaks in 600 chars should fail the ration"
    assert stats["break_ration"] > A.BREAK_RATION_MAX


def test_unknown_marks_are_still_refused():
    # the unknown-mark check stays over ALL marks - an unknown mark is spoken by the recorder
    findings, _ = A.audit("[tell] The variable is the hedge cost. " + FILLER)
    assert any("unknown marks" in f.message for f in findings)
