import importlib.util
import json
from pathlib import Path
import sys


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "build_finance_whiteboard_asset_proof.py"
SPEC = importlib.util.spec_from_file_location("build_finance_whiteboard_asset_proof", SCRIPT_PATH)
assert SPEC and SPEC.loader
builder = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = builder
SPEC.loader.exec_module(builder)


def test_source_receipts_match_the_approved_inputs():
    receipts = builder.verify_source_inputs()

    assert receipts["pdf_hashes"] == builder.EXPECTED_PDF_HASHES
    assert receipts["source_window"]["start_s"] == 0.0
    assert receipts["source_window"]["end_s"] == 18.0
    assert receipts["source_window"]["duration_s"] == 18.0
    assert receipts["source_window"]["word_start_index"] == 0
    assert receipts["source_window"]["word_end_index"] > 0


def test_source_cards_keep_pdf_locator_and_timing_contract():
    binding_path = builder.PROOF_ROOT / "source-binding.v1.json"
    binding = json.loads(binding_path.read_text(encoding="utf-8"))

    assert len(binding["cards"]) == 3
    assert [card["id"] for card in binding["cards"]] == [
        "valuation-paradox",
        "capacity-penalty",
        "physical-antidote",
    ]
    assert [(card["start_s"], card["end_s"]) for card in binding["cards"]] == [
        (0.0, 2.4),
        (2.4, 11.6),
        (11.6, 18.0),
    ]
    assert all(card["source_pdf_sha256"] in builder.EXPECTED_PDF_HASHES.values() for card in binding["cards"])
    assert all(card["source_locator"] and card["text_owner"] == "supplied source card" for card in binding["cards"])


def test_hyperframes_composition_is_deterministic_and_face_readable():
    html = (builder.PROOF_ROOT / "index.html").read_text(encoding="utf-8")
    package = json.loads((builder.PROOF_ROOT / "package.json").read_text(encoding="utf-8"))

    assert all("hyperframes@0.7.104" in command for command in package["scripts"].values())
    assert 'window.__timelines["finance-whiteboard-asset-blend-proof-v1"] = tl;' in html
    assert 'data-start="2.4" data-duration="9.2" data-track-index="3"' in html
    assert 'data-start="11.6" data-duration="6.4" data-track-index="4"' in html
    assert 'assets/draw-hand-a-v1.png' in html
    assert 'class="reveal-path"' in html
    assert 'id="draw-hand"' in html
    assert 'function buildGeometry(path, samples = 512)' in html
    assert 'function setHandAt(geometry, progress)' in html
    assert 'drawCard("card-one", "reveal-one"' in html
    assert "Math.random" not in html
    assert "Date.now" not in html
    assert "fetch(" not in html


def test_review_manifest_is_a_real_delivery_artifact():
    manifest = json.loads((builder.PROOF_ROOT / "proof-manifest.v1.json").read_text(encoding="utf-8"))
    render = manifest["render"]
    render_path = builder.PROOF_ROOT / render["path"]

    assert manifest["status"] == "review_render_complete"
    assert render["path"] == "render/finance-whiteboard-asset-blend-proof.mp4"
    assert render["authoring_path"] == "render/hf-authoring.mp4"
    assert manifest["hand"]["path"] == "assets/draw-hand-a-v1.png"
    assert manifest["hand"]["nib"]["display_px"] == {"x": 135, "y": 428}
    assert render_path.is_file()
    video_stream = next(stream for stream in render["ffprobe"]["streams"] if stream["codec_type"] == "video")
    assert video_stream["width"] == 1280
    assert video_stream["height"] == 720
    assert abs(float(render["ffprobe"]["format"]["duration"]) - 18.0) < 0.1
