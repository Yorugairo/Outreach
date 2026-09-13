"""The extraction gate fails every way the ungated 2026-09-13 reasoning run failed, and passes an honest extract."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
import verify_reasoning_extract as V  # noqa: E402


def _setup(tmp_path, rows):
    inp = tmp_path / "in.jsonl"
    inp.write_text("\n".join(json.dumps(r) for r in [
        {"id": "aaaaaaaaaaaa", "operator": "maybe start the axis from the lowest since 2000", "agent": "Agreed, the line reads by shape."},
        {"id": "bbbbbbbbbbbb", "operator": "thanks", "agent": "Done."},
    ]) + "\n", encoding="utf-8")
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "real.md").write_text("# Real\n## The heading\ntext", encoding="utf-8")
    ext = tmp_path / "ext.jsonl"
    ext.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
    return ext, inp


GOOD_ITEM = {"kind": "item", "rid": "R-001", "title": "t", "logic": "l",
             "evidence": [{"id": "aaaaaaaaaaaa", "quote": "start the axis from the lowest since 2000"}],
             "repo_check": {"terms": ["x", "y"], "found": "partial", "anchor": "docs/real.md:The heading"},
             "home": "docs/real.md:The heading", "confidence": "high"}
GOOD = [{"kind": "coverage", "id": "aaaaaaaaaaaa", "status": "kept"},
        {"kind": "coverage", "id": "bbbbbbbbbbbb", "status": "nothing"},
        GOOD_ITEM,
        {"kind": "counts", "read": 2, "kept": 1, "nothing": 1, "recorded": 0, "items": 1}]


def test_an_honest_extract_passes(tmp_path):
    ext, inp = _setup(tmp_path, GOOD)
    assert V.verify(ext, inp, tmp_path, use_docs_find=False) == []


def test_it_fails_the_ways_the_ungated_run_failed(tmp_path):
    bad_item = {**GOOD_ITEM, "evidence": [{"id": "aaaaaaaaaaaa", "quote": "an invented sentence"}],
                "home": "docs/content-video-engine/02-VOICE-AND-NARRATION.md:Spoken"}
    rows = [GOOD[0], bad_item, {"kind": "counts", "read": 1446, "kept": 1, "nothing": 0, "recorded": 375, "items": 1}]
    ext, inp = _setup(tmp_path, rows)
    fails = " | ".join(V.verify(ext, inp, tmp_path, use_docs_find=False))
    assert "not verbatim" in fails                     # a quote not in its exchange
    assert "home path does not exist" in fails         # an invented file
    assert "no coverage row" in fails                  # skimmed: an exchange never accounted for
    assert "counts.read" in fails and "counts.recorded" in fails   # copied counts


def test_a_triage_crib_and_a_bad_recorded_anchor_fail(tmp_path):
    rows = [{"kind": "coverage", "id": "aaaaaaaaaaaa", "status": "recorded", "anchor": "docs/operator-ledger/TRIAGE-DIGEST.md:x"},
            {"kind": "coverage", "id": "bbbbbbbbbbbb", "status": "recorded", "anchor": "docs/real.md:No such heading"},
            {"kind": "counts", "read": 2, "kept": 0, "nothing": 0, "recorded": 2, "items": 0}]
    ext, inp = _setup(tmp_path, rows)
    fails = " | ".join(V.verify(ext, inp, tmp_path, use_docs_find=False))
    assert "forbidden source" in fails and "not found in docs/real.md" in fails
