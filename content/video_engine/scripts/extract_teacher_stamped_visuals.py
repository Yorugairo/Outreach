"""Extract approved teacher-stamped deck slides as production visuals.

The approved deck record gates which source PPTX files are eligible for
render-level use. Factual-content eligibility is promoted only when the same
record carries an explicit operator evidence approval.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import posixpath
import re
import sys
import zipfile
from io import BytesIO
from pathlib import Path
from typing import Any, Iterable, Mapping
from xml.etree import ElementTree as ET

from PIL import Image, ImageDraw, ImageFont, ImageOps

NS_REL = "http://schemas.openxmlformats.org/package/2006/relationships"
SLIDE_RE = re.compile(r"^ppt/slides/slide(\d+)\.xml$")
SCHEMA_VERSION = "teacher_stamped_visuals.v1"


class TeacherStampedExtractionError(ValueError):
    """Raised when production-visual extraction cannot deterministically proceed."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_hash(payload: Mapping[str, Any]) -> str:
    body = {key: value for key, value in payload.items() if key != "artifact_hash"}
    encoded = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return sha256_bytes(encoded)


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--approval-record", type=Path, required=True, help="Path to teacher-stamped deck approval JSON.")
    parser.add_argument("--output-root", type=Path, required=True, help="Root directory for extracted production visuals.")
    parser.add_argument(
        "--source-manifest-root",
        type=Path,
        default=Path("content/video_engine/projects/systems-and-blowups/sources/decks"),
        help="Root of source deck manifests used for deterministic context.",
    )
    return parser.parse_args(argv)


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TeacherStampedExtractionError(f"Invalid JSON object at {path}")
    return data


def _coerce_value(value: Any, key: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TeacherStampedExtractionError(f"Invalid value for {key}: {value!r}")
    return value.strip()


def _evidence_approval(payload: Mapping[str, Any]) -> tuple[bool, str]:
    raw = payload.get("evidence_approval")
    if raw is None:
        return False, "source_review_only"
    if not isinstance(raw, Mapping):
        raise TeacherStampedExtractionError("evidence_approval must be an object")
    status = _coerce_value(raw.get("status"), "evidence_approval.status")
    scope = _coerce_value(raw.get("scope"), "evidence_approval.scope")
    if status == "approved" and scope != "all_factual_contents":
        raise TeacherStampedExtractionError(
            "Approved evidence scope must be 'all_factual_contents'"
        )
    if status not in {"approved", "not_approved"}:
        raise TeacherStampedExtractionError(
            f"Unsupported evidence approval status: {status!r}"
        )
    return status == "approved", scope


def read_approval_record(path: Path) -> dict[str, Any]:
    payload = load_json(path)
    status = _coerce_value(payload.get("status"), "status")
    if status != "approved":
        raise TeacherStampedExtractionError(f"Approval record status is not approved: {status!r}")

    scope = _coerce_value(payload.get("approval_scope"), "approval_scope")
    if scope != "production_visuals":
        raise TeacherStampedExtractionError(
            f"Approval scope mismatch: expected 'production_visuals', found {scope!r}"
        )
    _evidence_approval(payload)

    decks = payload.get("decks")
    if not isinstance(decks, list) or not decks:
        raise TeacherStampedExtractionError("Approval record must include a non-empty 'decks' array.")
    for deck in decks:
        if not isinstance(deck, dict):
            raise TeacherStampedExtractionError(f"Deck entry must be an object: {deck!r}")
        for key in ("deck_id", "title", "pptx", "contact_sheet"):
            if key not in deck:
                raise TeacherStampedExtractionError(f"Deck entry missing '{key}': {deck!r}")
            _coerce_value(deck[key], key)

    return payload


def _relationship_targets(zf: zipfile.ZipFile, slide_path: str) -> list[str]:
    rel_path = f"ppt/slides/_rels/{Path(slide_path).name}.rels"
    if rel_path not in zf.namelist():
        raise TeacherStampedExtractionError(f"Missing relationship file for {slide_path}: {rel_path}")
    root = ET.fromstring(zf.read(rel_path))
    targets: list[str] = []
    for relationship in root.findall(f"{{{NS_REL}}}Relationship"):
        relationship_type = relationship.attrib.get("Type", "")
        if not relationship_type.endswith("/relationships/image"):
            continue
        target = relationship.attrib.get("Target", "")
        resolved = posixpath.normpath(posixpath.join("ppt/slides", target))
        if resolved.startswith("ppt/media/"):
            targets.append(resolved)
    return targets


def map_slide_media(zf: zipfile.ZipFile) -> list[tuple[int, str]]:
    slides = []
    for name in zf.namelist():
        match = SLIDE_RE.match(name)
        if match:
            slides.append((int(match.group(1)), name))
    if not slides:
        raise TeacherStampedExtractionError("PPTX has no ppt/slides/slideN.xml entries.")
    slides.sort()

    mapped: list[tuple[int, str]] = []
    names = set(zf.namelist())
    for number, slide_path in slides:
        targets = _relationship_targets(zf, slide_path)
        if len(targets) != 1:
            raise TeacherStampedExtractionError(f"{slide_path} must map to exactly one image, found {targets!r}.")
        target = targets[0]
        if target not in names:
            raise TeacherStampedExtractionError(f"{slide_path} points to missing media member {target!r}.")
        mapped.append((number, target))
    return mapped


def png_payload(image_bytes: bytes) -> tuple[bytes, int, int, str]:
    try:
        with Image.open(BytesIO(image_bytes)) as image:
            width, height = image.size
            mode = image.mode
            png = image.convert("RGBA")
            output = BytesIO()
            png.save(output, format="PNG", optimize=False, compress_level=9)
            return output.getvalue(), width, height, mode
    except Exception as exc:
        raise TeacherStampedExtractionError(f"Embedded media is not decodable as image bytes: {exc}") from exc


def _default_context(deck_title: str, number: int) -> dict[str, Any]:
    return {
        "label": f"{deck_title} · slide {number:02d}",
        "summary": f"Teacher-stamped production visual for slide {number:02d} of {deck_title}.",
        "context_status": "review_only",
        "claim_refs": [],
        "cue_refs": [],
    }


def _read_source_context(source_manifest_root: Path, deck_id: str) -> tuple[dict[int, dict[str, Any]], dict[int, str | None]]:
    manifest_path = source_manifest_root / deck_id / "source-manifest.json"
    if not manifest_path.exists():
        return {}, {}
    source = load_json(manifest_path)
    slide_contexts: dict[int, dict[str, Any]] = {}
    source_image_ids: dict[int, str] = {}
    for entry in source.get("slides", []):
        if not isinstance(entry, dict):
            raise TeacherStampedExtractionError(f"Invalid source slide entry in {manifest_path}: {entry!r}")
        number = int(entry.get("slide_number", 0))
        if number < 1:
            raise TeacherStampedExtractionError(f"Invalid slide number in {manifest_path}: {entry!r}")
        context = entry.get("context", {})
        if not isinstance(context, dict):
            raise TeacherStampedExtractionError(f"Invalid context object in {manifest_path}: {context!r}")
        slide_contexts[number] = {
            "label": str(context.get("label", f"Slide {number:02d}")),
            "summary": str(context.get("summary", "Teacher-stamped production visual.")),
            "context_status": str(context.get("context_status", "review_only")),
            "claim_refs": list(context.get("claim_refs", [])),
            "cue_refs": list(context.get("cue_refs", [])),
        }
        source_image_id = entry.get("source_image_id")
        if source_image_id:
            source_image_ids[number] = str(source_image_id)
    return slide_contexts, source_image_ids


def make_contact_sheet(records: Iterable[Mapping[str, Any]], output_path: Path, *, title: str) -> None:
    records = list(records)
    column_width = 340
    image_height = 188
    label_height = 56
    columns = 4
    rows = max(1, (len(records) + columns - 1) // columns)
    canvas = Image.new("RGB", (columns * column_width, rows * (image_height + label_height) + 48), (246, 241, 226))
    draw = ImageDraw.Draw(canvas)
    header_font = ImageFont.load_default()
    body_font = ImageFont.load_default()

    draw.text((14, 12), title, fill=(36, 32, 28), font=header_font)
    for index, record in enumerate(records):
        column = index % columns
        row = index // columns
        x = column * column_width
        y = row * (image_height + label_height) + 44
        image_path = Path(output_path.parent) / str(record["extracted_path"])
        if image_path.exists():
            with Image.open(image_path) as source:
                preview = ImageOps.contain(source.convert("RGB"), (column_width - 14, image_height - 16))
            px = x + (column_width - preview.width) // 2
            py = y + (image_height - preview.height) // 2
            canvas.paste(preview, (px, py))
        draw.rectangle((x + 1, y + 1, x + column_width - 3, y + image_height - 1), outline=(112, 104, 89), width=1)
        label = str(record.get("slide_id", "unknown"))
        source = f"{record['deck_id']} · {int(record['slide_number']):02d}"
        draw.text((x + 8, y + image_height + 8), label[:43], fill=(25, 25, 25), font=body_font)
        draw.text((x + 8, y + image_height + 27), source[:46], fill=(78, 73, 67), font=body_font)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output_path, format="PNG", optimize=False, compress_level=9)


def extract_teacher_stamped_visuals(
    approval_record: Mapping[str, Any],
    *,
    output_root: Path,
    source_manifest_root: Path,
    approval_record_path: Path,
) -> dict[str, Any]:
    output_root = output_root.resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    status = _coerce_value(approval_record.get("status"), "status")
    if status != "approved":
        raise TeacherStampedExtractionError(f"Approval record status is not approved: {status!r}")
    scope = _coerce_value(approval_record.get("approval_scope"), "approval_scope")
    if scope != "production_visuals":
        raise TeacherStampedExtractionError(
            f"Approval scope mismatch: expected 'production_visuals', found {scope!r}"
        )
    evidence_eligible, evidence_scope = _evidence_approval(approval_record)

    seen_deck_ids: set[str] = set()
    seen_image_ids: set[str] = set()
    seen_hashes: set[str] = set()

    visuals: list[dict[str, Any]] = []
    deck_refs: list[dict[str, Any]] = []
    for deck in approval_record["decks"]:
        deck_id = _coerce_value(deck["deck_id"], "deck_id")
        _coerce_value(deck["title"], "title")
        _coerce_value(deck["contact_sheet"], "contact_sheet")
        _coerce_value(deck["pptx"], "pptx")
        if deck_id in seen_deck_ids:
            raise TeacherStampedExtractionError(f"Duplicate deck_id detected in approval record: {deck_id}")
        seen_deck_ids.add(deck_id)

    # Re-iterate with deterministic per-deck extraction.
    for deck in approval_record["decks"]:
        deck_id = _coerce_value(deck["deck_id"], "deck_id")
        title = _coerce_value(deck["title"], "title")
        contact_sheet = _coerce_value(deck["contact_sheet"], "contact_sheet")
        pptx = Path(str(deck["pptx"])).expanduser().resolve()
        if not pptx.exists():
            raise TeacherStampedExtractionError(f"PPTX path missing for deck {deck_id}: {pptx}")
        deck_sha = sha256_bytes(pptx.read_bytes())

        source_contexts, source_image_ids = _read_source_context(source_manifest_root, deck_id)
        deck_visuals: list[dict[str, Any]] = []

        with zipfile.ZipFile(pptx) as zf:
            mapped = dict(map_slide_media(zf))
            for number in sorted(mapped):
                member = mapped[number]
                image_id = f"{deck_id}-s{number:02d}-teacher-stamped"
                if image_id in seen_image_ids:
                    raise TeacherStampedExtractionError(f"Duplicate image id detected: {image_id}")
                seen_image_ids.add(image_id)

                png_data, width, height, mode = png_payload(zf.read(member))
                media_hash = sha256_bytes(png_data)
                if media_hash in seen_hashes:
                    raise TeacherStampedExtractionError(
                        f"Hash ambiguity detected for {deck_id} slide {number}: media hash {media_hash} repeats."
                    )
                seen_hashes.add(media_hash)

                slide_context = source_contexts.get(
                    number,
                    _default_context(title, number),
                )
                context_payload = {
                    **slide_context,
                    "context_status": (
                        "operator_verified"
                        if evidence_eligible
                        else slide_context.get("context_status", "review_only")
                    ),
                    "approval_scope": scope,
                    "source_image_id": source_image_ids.get(number),
                    "source_review_status": slide_context.get("context_status", "review_only"),
                    "production_scope": "production_visuals",
                    "evidence_scope": evidence_scope,
                }
                relative_path = Path(deck_id) / "slides" / f"slide-{number:03d}.png"
                output_path = output_root / relative_path
                output_path.parent.mkdir(parents=True, exist_ok=True)
                temporary = output_path.with_suffix(output_path.suffix + ".tmp")
                temporary.write_bytes(png_data)
                os.replace(temporary, output_path)

                entry = {
                    "image_id": image_id,
                    "deck_id": deck_id,
                    "slide_id": f"{deck_id}-s{number:02d}",
                    "slide_number": number,
                    "source": {
                        "pptx_name": pptx.name,
                        "pptx_member": member,
                        "pptx_sha256": deck_sha,
                    },
                    "extracted_path": relative_path.as_posix(),
                    "sha256": media_hash,
                    "width": width,
                    "height": height,
                    "mode": mode,
                    "context": context_payload,
                    "rights_state": "source_review_only",
                    "approval_scope": scope,
                    "render_eligible": scope == "production_visuals",
                    "evidence_render_eligible": evidence_eligible,
                }
                visuals.append(entry)
                deck_visuals.append(entry)

        if not deck_visuals:
            raise TeacherStampedExtractionError(f"Deck has no extractable slides: {deck_id}")

        make_contact_sheet(
            deck_visuals,
            output_root / contact_sheet,
            title=f"{title} · teacher-stamped production visuals",
        )

        deck_refs.append(
            {
                "deck_id": deck_id,
                "title": title,
                "pptx_name": pptx.name,
                "slide_count": len(deck_visuals),
                "contact_sheet": contact_sheet,
                "scope": scope,
                "evidence_scope": evidence_scope,
                "pptx_sha256": deck_sha,
                "source_manifest": str((source_manifest_root / deck_id / "source-manifest.json").as_posix()),
            }
        )

    manifest = {
        "schema_version": SCHEMA_VERSION,
        "approval_record_path": str(approval_record_path),
        "approved_at": _coerce_value(approval_record.get("approved_at"), "approved_at"),
        "status": status,
        "approval_scope": scope,
        "evidence_approval_status": "approved" if evidence_eligible else "not_granted",
        "evidence_scope": evidence_scope,
        "scope": scope,
        "decks": deck_refs,
        "visuals": visuals,
        "artifact_hash": "",
    }
    manifest["artifact_hash"] = canonical_hash(manifest)
    return manifest


def _write_default_manifest(output_root: Path, manifest: Mapping[str, Any]) -> Path:
    output_path = output_root / "teacher-stamped-production-visuals-manifest.v1.json"
    write_json(output_path, manifest)
    return output_path


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        approval_record = read_approval_record(args.approval_record)
        manifest = extract_teacher_stamped_visuals(
            approval_record,
            output_root=args.output_root,
            source_manifest_root=args.source_manifest_root,
            approval_record_path=args.approval_record,
        )
        output_manifest = _write_default_manifest(args.output_root, manifest)
        print(json.dumps({"manifest": str(output_manifest), "artifact_hash": manifest["artifact_hash"]}, indent=2))
        return 0
    except (TeacherStampedExtractionError, OSError, zipfile.BadZipFile, ET.ParseError, json.JSONDecodeError) as exc:
        print(f"extract_teacher_stamped_visuals: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
