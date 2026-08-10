from __future__ import annotations

import json
import zipfile
from pathlib import Path
from typing import Any
from io import BytesIO

from PIL import Image
import pytest

from content.video_engine.scripts.extract_teacher_stamped_visuals import (
    TeacherStampedExtractionError,
    extract_teacher_stamped_visuals,
)


def _png_bytes(color: tuple[int, int, int, int], *, width: int = 32, height: int = 24) -> bytes:
    image = Image.new("RGBA", (width, height), color)
    buffer = BytesIO()
    image.save(buffer, format="PNG", optimize=False, compress_level=9)
    return buffer.getvalue()


def _write_fixture_pptx(path: Path, *, slide_count: int, shared_media: bool = False) -> dict[int, bytes]:
    media: dict[int, bytes] = {}
    for number in range(1, slide_count + 1):
        source = _png_bytes((20 * number, 40 + number, 60 + number, 255), width=16, height=12)
        media[number] = source if not shared_media else _png_bytes((30, 30, 30, 255), width=16, height=12)
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for number, payload in media.items():
            archive.writestr(f"ppt/media/image{number}.png", payload)
            archive.writestr(
                f"ppt/slides/_rels/slide{number}.xml.rels",
                (
                    "<Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\">"
                    f"<Relationship Id=\"rId1\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/image\""
                    ' Target="../media/image'
                    f"{number}.png\"/></Relationships>"
                ),
            )
            archive.writestr(f"ppt/slides/slide{number}.xml", "<p:sld xmlns:p=\"http://schemas.openxmlformats.org/presentationml/2006/main\"/>")
    return media


def _write_source_manifest(path: Path, deck_id: str, *, slide_count: int = 2) -> None:
    slides: list[dict[str, Any]] = []
    for number in range(1, slide_count + 1):
        slides.append(
            {
                "slide_id": f"{deck_id}-s{number:02d}",
                "deck_id": deck_id,
                "slide_number": number,
                "slide_label": f"Fixture Slide {number:02d}",
                "source_image_id": f"{deck_id}-s{number:02d}-original",
                "context": {
                    "label": f"Fixture slide {number:02d}",
                    "summary": f"Fixture source context for slide {number:02d}.",
                    "context_status": "review_only",
                    "claim_refs": [f"claim-{number}"],
                    "cue_refs": [f"cue-{number}"],
                },
            }
        )
    manifest = {
        "schema_version": "deck_asset_manifest.v1",
        "manifest_id": "fixture-manifest",
        "decks": [deck_id],
        "slides": slides,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def _approval_record(
    path: Path,
    *,
    deck_id: str,
    pptx: Path,
    contact_sheet: str,
    scope: str = "production_visuals",
    status: str = "approved",
    evidence_approved: bool = False,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "schema_version": "teacher_stamped_deck_approval.v1",
        "approved_at": "2026-08-10",
        "approval_scope": scope,
        "status": status,
        "decks": [
            {
                "deck_id": deck_id,
                "title": "Fixture Deck",
                "pptx": str(pptx),
                "contact_sheet": contact_sheet,
            }
        ],
        "note": "fixture",
    }
    if evidence_approved:
        payload["evidence_approval"] = {
            "status": "approved",
            "scope": "all_factual_contents",
            "approved_at": "2026-08-10",
            "basis": "operator_attestation",
        }
    path.write_text(json.dumps(payload), encoding="utf-8")
    return payload


def test_extract_teacher_stamped_visuals_success(tmp_path: Path) -> None:
    deck_id = "fixture-deck"
    pptx = tmp_path / "fixture.teacher-stamped.pptx"
    _write_fixture_pptx(pptx, slide_count=2)
    source_root = tmp_path / "sources" / "decks"
    _write_source_manifest(source_root / deck_id / "source-manifest.json", deck_id)

    approval_path = tmp_path / "approval.json"
    approval = _approval_record(
        approval_path,
        deck_id=deck_id,
        pptx=pptx,
        contact_sheet="fixture-teacher-stamped-slides.png",
        evidence_approved=True,
    )
    output = tmp_path / "outputs"
    manifest = extract_teacher_stamped_visuals(
        approval,
        output_root=output,
        source_manifest_root=source_root,
        approval_record_path=approval_path,
    )

    assert manifest["approval_scope"] == "production_visuals"
    assert manifest["decks"][0]["slide_count"] == 2
    assert manifest["decks"][0]["contact_sheet"] == "fixture-teacher-stamped-slides.png"
    assert manifest["visuals"][0]["approval_scope"] == "production_visuals"
    assert manifest["evidence_approval_status"] == "approved"
    assert manifest["visuals"][0]["evidence_render_eligible"] is True
    assert manifest["visuals"][0]["context"]["evidence_scope"] == "all_factual_contents"
    assert manifest["visuals"][0]["context"]["context_status"] == "operator_verified"
    assert manifest["visuals"][0]["render_eligible"] is True
    assert (output / manifest["decks"][0]["contact_sheet"]).exists()
    first = manifest["visuals"][0]
    assert (output / first["extracted_path"]).exists()
    assert first["context"]["label"].startswith("Fixture")


def test_visual_approval_alone_does_not_promote_factual_contents(tmp_path: Path) -> None:
    deck_id = "visual-only-deck"
    pptx = tmp_path / "visual-only.teacher-stamped.pptx"
    _write_fixture_pptx(pptx, slide_count=1)
    approval_path = tmp_path / "approval.json"
    approval = _approval_record(
        approval_path,
        deck_id=deck_id,
        pptx=pptx,
        contact_sheet="visual-only.png",
    )

    manifest = extract_teacher_stamped_visuals(
        approval,
        output_root=tmp_path / "outputs",
        source_manifest_root=tmp_path / "sources",
        approval_record_path=approval_path,
    )

    assert manifest["evidence_approval_status"] == "not_granted"
    assert manifest["visuals"][0]["evidence_render_eligible"] is False
    assert manifest["visuals"][0]["context"]["evidence_scope"] == "source_review_only"


def test_missing_approval_scope_fails() -> None:
    with pytest.raises(TeacherStampedExtractionError, match="Approval scope mismatch"):
        extract_teacher_stamped_visuals(
            {
                "schema_version": "teacher_stamped_deck_approval.v1",
                "approved_at": "2026-08-10",
                "approval_scope": "evidence",
                "status": "approved",
                "decks": [{"deck_id": "x", "title": "X", "pptx": "x", "contact_sheet": "x.png"}],
            },
            output_root=Path("does-not-matter"),
            source_manifest_root=Path("does-not-matter"),
            approval_record_path=Path("does-not-matter/approval.json"),
        )


def test_approved_evidence_requires_full_content_scope() -> None:
    with pytest.raises(TeacherStampedExtractionError, match="all_factual_contents"):
        extract_teacher_stamped_visuals(
            {
                "schema_version": "teacher_stamped_deck_approval.v1",
                "approved_at": "2026-08-10",
                "approval_scope": "production_visuals",
                "status": "approved",
                "evidence_approval": {"status": "approved", "scope": "selected_claims"},
                "decks": [{"deck_id": "x", "title": "X", "pptx": "x", "contact_sheet": "x.png"}],
            },
            output_root=Path("does-not-matter"),
            source_manifest_root=Path("does-not-matter"),
            approval_record_path=Path("does-not-matter/approval.json"),
        )


def test_duplicate_slide_image_hash_is_rejected(tmp_path: Path) -> None:
    deck_id = "fixture-hash"
    pptx = tmp_path / "fixture.teacher-stamped.pptx"
    _write_fixture_pptx(pptx, slide_count=2, shared_media=True)
    approval_path = tmp_path / "approval.json"
    approval = _approval_record(
        approval_path,
        deck_id=deck_id,
        pptx=pptx,
        contact_sheet="fixture-teacher-stamped-slides.png",
    )

    with pytest.raises(TeacherStampedExtractionError, match="Hash ambiguity"):
        extract_teacher_stamped_visuals(
            approval,
            output_root=tmp_path / "outputs",
            source_manifest_root=tmp_path / "sources",
            approval_record_path=approval_path,
        )


def test_duplicate_deck_id_is_rejected(tmp_path: Path) -> None:
    approval_path = tmp_path / "approval.json"
    approval_path.write_text(
        json.dumps(
            {
                "schema_version": "teacher_stamped_deck_approval.v1",
                "approved_at": "2026-08-10",
                "approval_scope": "production_visuals",
                "status": "approved",
                "decks": [
                    {"deck_id": "same", "title": "One", "pptx": "a", "contact_sheet": "a.png"},
                    {"deck_id": "same", "title": "Two", "pptx": "b", "contact_sheet": "b.png"},
                ],
            }
        ),
        encoding="utf-8",
    )
    approval = json.loads(approval_path.read_text(encoding="utf-8"))

    with pytest.raises(TeacherStampedExtractionError, match="Duplicate deck_id"):
        extract_teacher_stamped_visuals(
            approval,
            output_root=tmp_path / "outputs",
            source_manifest_root=tmp_path / "sources",
            approval_record_path=approval_path,
        )
