import importlib.util
import json
from pathlib import Path
import sys
from PIL import Image


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "build_finance_whiteboard_code_drawn_proof.py"
SPEC = importlib.util.spec_from_file_location("build_finance_whiteboard_code_drawn_proof", SCRIPT_PATH)
assert SPEC and SPEC.loader
builder = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = builder
SPEC.loader.exec_module(builder)


def test_verified_p24_inputs_and_hand_receipt():
    receipts = builder.verify_source_inputs()
    assert receipts["source_window"] == {
        "start_s": 0.0,
        "end_s": 18.0,
        "duration_s": 18.0,
        "word_start_index": 0,
        "word_end_index": 50,
    }
    assert receipts["hand_source_sha256"]


def test_composition_uses_isolated_artblocks_and_whiteboard_contract():
    html = (builder.PROOF_ROOT / "index.html").read_text(encoding="utf-8")
    package = json.loads((builder.PROOF_ROOT / "package.json").read_text(encoding="utf-8"))
    assert all("hyperframes@0.7.104" in command for command in package["scripts"].values())
    assert 'window.__timelines["finance-whiteboard-code-drawn-proof-v1"] = tl;' in html
    assert html.count('class="artblock"') == 9
    assert html.count("<image href=\"assets/art/") == 9
    assert 'id="s1-topic"' in html and 'id="s2-topic"' in html and 'id="s3-topic"' in html
    assert "maskUnits=\"userSpaceOnUse\"" in html
    assert "function drawLbl" in html
    assert "function prepareChunk" in html
    assert "Math.random" not in html
    assert "Date.now" not in html
    assert "fetch(" not in html
    assert "valuation-paradox.png" not in html
    assert ".pdf" not in html.lower()
    assert 'draw(s1Tag, 0.42, 0.92)' in html
    assert 'draw(s1Arrow, 0.38, 1.43)' in html
    assert 'draw(s2Capacity, 0.45, 4.06)' in html
    assert 'draw(s2Price, 1.18, 5.05)' in html
    assert 'draw(s2Factories, 0.95, 8.50)' in html
    assert 'draw(s3Lock, 1.18, 13.78)' in html


def test_staged_art_manifest_and_audit_inputs():
    manifest = json.loads((builder.PROOF_ROOT / "proof-manifest.v1.json").read_text(encoding="utf-8"))
    assert manifest["proof_id"] == "finance-whiteboard-code-drawn-proof-v1"
    assert manifest["provider_calls"] == 0
    assert manifest["pdf_assets"] == []
    assert len(manifest["art"]) == 9
    assert manifest["hand"]["b_path"] == "assets/draw-hand-b-v1.png"
    assert manifest["word_map"]["timing_source"] == "verified P24 Whisper word receipt"
    assert (builder.PROOF_ROOT / "review/chunks.json").is_file()
    assert (builder.PROOF_ROOT / "review/contact-sheet.html").is_file()
    assert (builder.PROOF_ROOT / "review/coverage").is_dir()
    for art in manifest["art"]:
        art_path = builder.PROOF_ROOT / art["path"]
        assert art_path.is_file()
        with Image.open(art_path) as image:
            assert image.mode == "RGBA"
            assert image.getpixel((0, 0))[3] == 0


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
