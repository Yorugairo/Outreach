"""P37 T2: the comfy/parallax config gate FAILs the runner as it shipped, naming all five
defects; PASSes the corrected runner; enforces the frame laws, the CFG ceiling and the
plate-kind matrix. The pre-fix runner is a fixture here so the gate keeps proving it can
catch what shipped."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import gate_comfy_config as G  # noqa: E402

RUNNER = ROOT / "tools/google-flow-driver/src/parallax-runner.mjs"

# the dials exactly as parallax-runner.mjs carried them on 2026-09-04 before P37 T9
SHIPPED_RUNNER = '''
  let motionInputs = { "strength": strength, "intensity": 1.0, "feature_param": "intensity" };
  motionInputs = { "strength": strength, "intensity": 1.0, "loop": false };
  "2": { "inputs": { "model": "depth_anything_v2_vits_fp16.safetensors", "precision": "fp16" } },
  "5": { "inputs": { "quality": 75, "ssaa": 1.0, "invert": 0, "tiling_mode": "mirror", "edge_fix": 5 } },
'''


def _rules(findings: list[G.Finding]) -> set[str]:
    return {f.rule for f in findings}


def test_the_shipped_runner_fails_on_all_five_defects() -> None:
    rules = _rules(G.check_runner(SHIPPED_RUNNER))
    assert rules == {"G-c intensity", "G-e tiling_mode", "G-c ssaa", "G-c quality", "G-c model"}, rules


def test_the_committed_runner_passes() -> None:
    findings = G.run(RUNNER)
    assert not findings, "\n".join(f.line() for f in findings)


def test_frame_laws_and_cfg_ceiling(tmp_path: Path) -> None:
    def job(**kw) -> list[str]:
        p = tmp_path / "job.json"; p.write_text(json.dumps(kw), encoding="utf-8")
        return sorted(_rules(G.run(p)))
    assert job(model="wan2.1-i2v", num_frames=81, cfg=4.0) == []
    assert job(model="wan2.1-i2v", num_frames=80) == ["G-m frames"]
    assert job(model="ltx-video", num_frames=121) == []
    assert job(model="ltx-video", num_frames=120) == ["G-m frames"]
    assert job(model="wan2.1-i2v", num_frames=81, cfg=6.0) == ["G-n cfg"]
    assert job(model="wan2.1-i2v", num_frames=81, text_encoder="umt5_fp8") == ["G-n text encoder"]
    assert job(model="wan2.1-i2v", num_frames=81, text_encoder="umt5_fp8_scaled") == []
    assert job(model="wan2.1-i2v", num_frames=81, vae="wan_vae_fp8") == ["G-n vae"]


def test_plate_kind_matrix() -> None:
    assert G.check_plate("world", False) == []
    assert _rules(G.check_plate("actor", False)) == {"G-b plate kind"}
    assert _rules(G.check_plate("evidence", True)) == {"G-b plate kind", "G-b text"}
