import importlib.util
import json
from pathlib import Path
import sys


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "build_finance_whiteboard_deck_asset_proof.py"
SPEC = importlib.util.spec_from_file_location("build_finance_whiteboard_deck_asset_proof", SCRIPT_PATH)
assert SPEC and SPEC.loader
builder = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = builder
SPEC.loader.exec_module(builder)


def test_selected_assets_bind_to_p28_manifest():
    receipts = builder.verify_source_inputs()
    assert receipts["asset_count"] == 4
    assert receipts["selected_asset_ids"] == [spec["asset_id"] for spec in builder.ASSET_SPECS]
    manifest = json.loads(builder.P28_MANIFEST.read_text(encoding="utf-8"))
    source_ids = {asset["asset_id"] for asset in manifest["assets"]}
    assert set(receipts["selected_asset_ids"]) <= source_ids


def test_proof_preserves_baked_text_and_hand_reveal_contract():
    html = (builder.PROOF_ROOT / "index.html").read_text(encoding="utf-8")
    proof = json.loads((builder.PROOF_ROOT / "proof-manifest.v1.json").read_text(encoding="utf-8"))
    assert proof["proof_id"] == "finance-whiteboard-deck-asset-proof-v1"
    assert proof["asset_policy"].startswith("deck crops are review-only")
    assert len(proof["art"]) == 4
    assert "The Three-to-One Capacity Penalty" not in html
    assert "assets/deck/capacity-penalty.png" in html
    assert "assets/deck/ram-ageddon.png" in html
    assert html.count("maskUnits=\"userSpaceOnUse\"") == 4
    assert "function setHandAt" in html
    assert "function prepareChunk" in html
    assert "function drawLbl" in html
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
