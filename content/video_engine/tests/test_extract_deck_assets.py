from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

import pytest
from jsonschema import Draft7Validator
from PIL import Image

from content.video_engine.scripts.extract_deck_assets import (
    DeckExtractionError,
    build_manifest,
    canonical_hash,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_ROOT = ROOT


def _png_bytes(color: tuple[int, int, int, int], label: str) -> bytes:
    image = Image.new("RGBA", (32, 24), color)
    image.putpixel((0, 0), (len(label), 1, 2, 255))
    from io import BytesIO

    buffer = BytesIO()
    image.save(buffer, format="PNG", optimize=False, compress_level=9)
    return buffer.getvalue()


def _write_deck(path: Path, *, slide_count: int = 2, ambiguous: bool = False) -> dict[int, bytes]:
    media: dict[int, bytes] = {number: _png_bytes((number * 20, 100, 150, 255), f"slide-{number}") for number in range(1, slide_count + 1)}
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as deck:
        for number, data in media.items():
            deck.writestr(f"ppt/media/image{number}.png", data)
            targets = f'<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="../media/image{number}.png"/>'
            if ambiguous and number == 1:
                deck.writestr("ppt/media/image-extra.png", data)
                targets += '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="../media/image-extra.png"/>'
            deck.writestr(
                f"ppt/slides/_rels/slide{number}.xml.rels",
                f'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">{targets}</Relationships>',
            )
            deck.writestr(f"ppt/slides/slide{number}.xml", "<p:sld xmlns:p=\"http://schemas.openxmlformats.org/presentationml/2006/main\"/>")
    return media


def _config(source: Path, output: Path, *, cleaned: Path | None = None, verified: bool = False) -> dict:
    deck = {
        "deck_id": "fixture-deck",
        "title": "Fixture Deck",
        "source_path": str(source),
        "source_family": "test-fixture",
        "rights_state": "approved" if verified else "source_review_only",
    }
    if cleaned:
        deck["cleaned_path"] = str(cleaned)
        deck["cleanup_approved"] = verified
    payload = {
        "manifest_id": "fixture-deck-manifest",
        "project_id": "systems-and-blowups",
        "decks": [deck],
        "slide_context": [
            {
                "deck_id": "fixture-deck",
                "slide_number": 1,
                "label": "Fixture mechanism",
                "summary": "A source slide used to test context retention.",
                "context_status": "operator_verified" if verified else "review_only",
                "claim_refs": ["claim-fixture"],
                "cue_refs": ["cue-fixture"],
            }
        ],
        "crops": [
            {
                "asset_id": "fixture-mechanism-crop-v1",
                "deck_id": "fixture-deck",
                "slide_number": 1,
                "source_variant": "cleaned" if cleaned else "original",
                "bbox_norm": [0.0, 0.0, 0.5, 0.5],
                "what_it_is": "A bounded test crop from the fixture mechanism slide.",
                "visual_role": "mechanism",
                "representation_mode": "accurate_mechanism",
                "factual_text": False,
                "claim_refs": ["claim-fixture"],
                "cue_refs": ["cue-fixture"],
                "not_what_it_means": ["It is not a complete source slide."],
                "context_status": "operator_verified" if verified else "review_only",
                "rights_state": "approved" if verified else "source_review_only",
                "review_state": "approved_reusable" if verified else "review_only",
                "render_eligible": True,
            }
        ],
    }
    output.mkdir(parents=True, exist_ok=True)
    return {"config": output / "config.json", "payload": payload}


def _write_config(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_exact_slide_media_and_context_are_preserved(tmp_path: Path) -> None:
    source = tmp_path / "fixture.pptx"
    media = _write_deck(source)
    config = _config(source, tmp_path / "run")
    config_path = tmp_path / "config.json"
    payload = config["payload"]
    _write_config(config_path, payload)
    manifest = build_manifest(payload, config["config"].parent)

    assert len(manifest["slides"]) == 2
    assert len(manifest["source_images"]) == 2
    assert len(manifest["assets"]) == 1
    first = manifest["source_images"][0]
    assert first["sha256"] == hashlib.sha256(media[1]).hexdigest()
    assert first["selection_label"] == "Fixture Deck · S01 · Fixture mechanism"
    assert first["context"]["summary"] == "A source slide used to test context retention."
    assert (config["config"].parent / first["extracted_path"]).read_bytes() == media[1]
    crop = manifest["assets"][0]
    assert crop["parent_source_image_id"] == "fixture-deck-s01-original"
    assert crop["extraction"]["bbox_px"] == [0, 0, 16, 12]
    assert crop["context"]["what_it_is"].startswith("A bounded test crop")
    assert crop["render_eligible"] is False
    assert (config["config"].parent / "fixture-deck" / "review" / "slide-contact-sheet.png").exists()
    assert (config["config"].parent / "fixture-deck" / "review" / "semantic-contact-sheet.png").exists()
    index = (config["config"].parent / "asset-selection-index.md").read_text(encoding="utf-8")
    assert "Fixture mechanism" in index
    assert "fixture-deck/slides/slide-001.png" in index


def test_cleaned_variant_is_linked_to_original_and_verified_context_can_render(tmp_path: Path) -> None:
    source = tmp_path / "fixture.pptx"
    cleaned = tmp_path / "fixture.no-watermark.pptx"
    _write_deck(source)
    _write_deck(cleaned)
    config = _config(source, tmp_path / "run", cleaned=cleaned, verified=True)
    full_payload = config["payload"]
    full_payload["crops"][0]["asset_id"] = "fixture-cleaned-crop-v1"
    full_payload["crops"][0]["what_it_is"] = "A verified crop from the cleaned source slide."
    full_payload["crops"][0]["visual_role"] = "evidence"
    full_payload["crops"][0]["representation_mode"] = "literal_evidence"
    full_payload["crops"][0]["factual_text"] = True
    manifest = build_manifest(full_payload, tmp_path / "run")
    assert len(manifest["source_images"]) == 2
    assert len(manifest["cleaned_images"]) == 2
    assert manifest["assets"][0]["source_variant"] == "cleaned"
    assert manifest["assets"][0]["render_eligible"] is True
    assert manifest["cleaned_images"][0]["parent_image_id"] == "fixture-deck-s01-original"


def test_repeated_extraction_has_stable_manifest_and_crop_hash(tmp_path: Path) -> None:
    source = tmp_path / "fixture.pptx"
    _write_deck(source)
    base = _config(source, tmp_path / "run-a")["payload"]
    first = build_manifest(base, tmp_path / "run-a")
    second = build_manifest(base, tmp_path / "run-b")
    assert first["artifact_hash"] == second["artifact_hash"]
    assert first["assets"][0]["sha256"] == second["assets"][0]["sha256"]
    assert canonical_hash(first) == first["artifact_hash"]


def test_ambiguous_media_mapping_fails_closed(tmp_path: Path) -> None:
    source = tmp_path / "ambiguous.pptx"
    _write_deck(source, ambiguous=True)
    payload = _config(source, tmp_path / "run")["payload"]
    with pytest.raises(DeckExtractionError, match="exactly one embedded media"):
        build_manifest(payload, tmp_path / "run")


def test_schema_and_template_validate() -> None:
    schema = json.loads((SCRIPT_ROOT / "configs" / "deck_asset_manifest.v1.schema.json").read_text(encoding="utf-8"))
    template = json.loads((SCRIPT_ROOT / "templates" / "deck_asset_manifest.v1.json").read_text(encoding="utf-8"))
    assert list(Draft7Validator(schema).iter_errors(template)) == []
