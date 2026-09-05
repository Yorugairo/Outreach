"""P37 T5 - V-a. Recorded model replies only; the verdict logic and both diagnoses are pinned."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
import judge_muted_caption as J  # noqa: E402

CLAIM = "the memory makers rose 613% while the market rose 21%"


def test_a_frame_the_model_reads_passes():
    v = J.judge(CLAIM, {"claim_read": "memory chip makers rose about 613%, far more than the market's 21%", "confidence": 0.9, "describes_only_scenery": False})
    assert v.verdict == "PASS" and v.diagnosis == "none" and v.overlap >= 2


def test_scenery_only_is_diagnosed_as_scenery():
    v = J.judge(CLAIM, {"claim_read": "", "confidence": 0.2, "describes_only_scenery": True})
    assert (v.verdict, v.diagnosis) == ("FAIL", "scenery")


def test_an_unresolved_claim_is_diagnosed_as_over_dense():
    v = J.judge(CLAIM, {"claim_read": "several lines go up on a dark chart with many labels", "confidence": 0.3, "describes_only_scenery": False})
    assert (v.verdict, v.diagnosis) == ("FAIL", "over-dense")


def test_cli_replays_recorded_responses_and_exits_by_verdict(tmp_path: Path):
    prior, test = tmp_path / "prior.png", tmp_path / "frame.png"
    prior.write_bytes(b"x"); test.write_bytes(b"x")
    rec = tmp_path / "rec.json"
    rec.write_text(json.dumps({"frame.png": {"claim_read": "", "confidence": 0.1, "describes_only_scenery": True}}), encoding="utf-8")
    r = subprocess.run([sys.executable, str(ROOT / "content/video_engine/scripts/judge_muted_caption.py"), "--prior", str(prior), "--test", str(test),
                        "--claim", CLAIM, "--responses", str(rec)], capture_output=True, text=True)
    assert r.returncode == 1 and '"diagnosis": "scenery"' in r.stdout
