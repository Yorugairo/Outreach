"""P37 T5 - V-a on the Codex lane. Recorded replies only; the verdict logic, both diagnoses,
the batch prompt's image order and the variadic-`-i` command shape are pinned. No codex run."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
import judge_muted_caption as J  # noqa: E402

CLAIM = "the memory makers rose 613% while the market rose 21%"


def test_a_frame_the_judge_reads_passes():
    v = J.judge(CLAIM, {"claim_read": "memory chip makers rose about 613%, far more than the market's 21%", "confidence": 0.9, "describes_only_scenery": False}, "s03")
    assert v.verdict == "PASS" and v.diagnosis == "none" and v.overlap >= 2 and v.scene == "s03"


def test_scenery_only_is_diagnosed_as_scenery():
    v = J.judge(CLAIM, {"claim_read": "", "confidence": 0.2, "describes_only_scenery": True})
    assert (v.verdict, v.diagnosis) == ("FAIL", "scenery")


def test_an_unresolved_claim_is_diagnosed_as_over_dense():
    v = J.judge(CLAIM, {"claim_read": "several lines go up on a dark chart with many labels", "confidence": 0.3, "describes_only_scenery": False})
    assert (v.verdict, v.diagnosis) == ("FAIL", "over-dense")


def test_batch_prompt_lists_every_frame_in_order_and_asks_for_one_array():
    manifest = [{"scene": "s01", "prior": "a/p1.png", "test": "a/t1.png", "claim": "x"}, {"scene": "s02", "prior": "a/p2.png", "test": "a/t2.png", "claim": "y"}]
    p = J.batch_prompt(manifest)
    assert p.index("1. PRIOR for scene s01: p1.png") < p.index("2. TEST  for scene s01: t1.png") < p.index("3. PRIOR for scene s02: p2.png") < p.index("4. TEST  for scene s02: t2.png")
    assert "ONLY a JSON array" in p


def test_codex_command_puts_every_image_before_the_non_variadic_flags(tmp_path: Path):
    cmd = J.codex_cmd("codex", tmp_path, "PROMPT", [Path("p1.png"), Path("t1.png"), Path("p2.png"), Path("t2.png")], tmp_path / "last.txt")
    i = cmd.index("-i")
    assert cmd[i + 1: i + 5] == ["p1.png", "t1.png", "p2.png", "t2.png"] and cmd[i + 5] == "-c"   # -c closes the variadic list
    assert cmd[-1] == "PROMPT" and "--approve-for-me" in cmd and "--skip-git-repo-check" in cmd


def test_cli_replays_a_manifest_and_exits_by_verdict(tmp_path: Path):
    for n in ("p1.png", "t1.png", "p2.png", "t2.png"):
        (tmp_path / n).write_bytes(b"x")
    manifest = tmp_path / "m.json"
    manifest.write_text(json.dumps([{"scene": "s01", "prior": str(tmp_path / "p1.png"), "test": str(tmp_path / "t1.png"), "claim": CLAIM},
                                    {"scene": "s02", "prior": str(tmp_path / "p2.png"), "test": str(tmp_path / "t2.png"), "claim": CLAIM}]), encoding="utf-8")
    rec = tmp_path / "rec.json"
    rec.write_text(json.dumps({"t1.png": {"claim_read": "memory makers rose 613% versus the market's 21%", "confidence": 0.9, "describes_only_scenery": False},
                               "t2.png": {"claim_read": "", "confidence": 0.1, "describes_only_scenery": True}}), encoding="utf-8")
    out = tmp_path / "report.json"
    r = subprocess.run([sys.executable, str(ROOT / "content/video_engine/scripts/judge_muted_caption.py"), str(manifest), "--responses", str(rec), "--out", str(out)],
                       capture_output=True, text=True)
    report = json.loads(out.read_text(encoding="utf-8"))
    assert r.returncode == 1 and report["counts"] == {"PASS": 1, "FAIL": 1} and report["diagnoses"]["scenery"] == 1
    assert [s["scene"] for s in report["scenes"]] == ["s01", "s02"]
