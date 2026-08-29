import importlib.util
import json
from pathlib import Path
import sys


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "build_finance_whiteboard_world_blend_proof.py"
SPEC = importlib.util.spec_from_file_location("build_finance_whiteboard_world_blend_proof", SCRIPT_PATH)
assert SPEC and SPEC.loader
builder = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = builder
SPEC.loader.exec_module(builder)


def test_world_and_evidence_inputs_are_hash_bound():
    receipts = builder.verify_inputs()
    assert receipts["world_asset_ids"] == [spec["asset_id"] for spec in builder.WORLD_SOURCES]
    assert receipts["deck_asset_ids"] == [spec["asset_id"] for spec in builder.DECK_LAYOUTS]
    assert receipts["p28_manifest_sha256"]


def test_world_blend_composition_contract():
    html = (builder.PROOF_ROOT / "index.html").read_text(encoding="utf-8")
    manifest = json.loads((builder.PROOF_ROOT / "proof-manifest.v1.json").read_text(encoding="utf-8"))
    assert manifest["proof_id"] == "finance-whiteboard-world-blend-proof-v1"
    assert manifest["composition_rule"].startswith("continuous woodblock research world")
    assert len(manifest["world_assets"]) == 2
    assert len(manifest["deck_assets"]) == 4
    assert "assets/world/whiteboard-easel-v2.png" in html
    assert "assets/world/finance-analyst-v1.png" in html
    assert "assets/deck/capacity-penalty.png" in html
    assert "assets/deck/ram-ageddon.png" in html
    assert html.count("maskUnits=\"userSpaceOnUse\"") == 4
    assert "function setHandAt" in html
    assert "function prepareChunk" in html
    assert "Math.random" not in html
    assert "Date.now" not in html


def test_review_render_contract():
    manifest = json.loads((builder.PROOF_ROOT / "proof-manifest.v1.json").read_text(encoding="utf-8"))
    assert manifest["status"] == "review_render_complete"
    render = manifest["render"]
    render_path = builder.PROOF_ROOT / render["path"]
    assert render_path.is_file()
    video_stream = next(stream for stream in render["ffprobe"]["streams"] if stream["codec_type"] == "video")
    assert video_stream["width"] == 1280
    assert video_stream["height"] == 720
    assert video_stream["r_frame_rate"] == "24/1"
    assert abs(float(render["ffprobe"]["format"]["duration"]) - 18.0) < 0.1
