"""Extract PPTX slide media and context-preserving semantic crops.

The source decks used by the finance pilot are raster slide containers: each
slide points at one embedded PNG and contains no editable text or shapes. This
script keeps those bytes intact, then creates explicitly described crop
derivatives whose manifest entries retain the parent slide, parent hash,
coordinates, editorial meaning, and review state.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import posixpath
import re
import sys
import zipfile
from io import BytesIO
from pathlib import Path
from typing import Any, Iterable, Mapping
from xml.etree import ElementTree as ET

from PIL import Image, ImageDraw, ImageFont, ImageOps


SCHEMA_VERSION = "deck_asset_manifest.v1"
NS_REL = "http://schemas.openxmlformats.org/package/2006/relationships"
SLIDE_RE = re.compile(r"^ppt/slides/slide(\d+)\.xml$")
DEFAULT_PROMOTION_POLICY = "Only operator-verified context and approved rights may render."
DEFAULT_CLEANUP_POLICY = "Derived from an operator-approved non-destructive footer cleanup."


class DeckExtractionError(ValueError):
    """Raised when a PPTX cannot be mapped deterministically to slide media."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_hash(payload: Mapping[str, Any]) -> str:
    body = {key: value for key, value in payload.items() if key != "artifact_hash"}
    encoded = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return sha256_bytes(encoded)


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def slug(value: str) -> str:
    value = value.lower().replace("&", "and")
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    if not value:
        raise DeckExtractionError(f"Cannot create stable ID from empty value: {value!r}")
    return value


def load_config(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("decks"), list) or not data["decks"]:
        raise DeckExtractionError("Config must be an object with a non-empty 'decks' array.")
    return data


def _relationship_targets(zf: zipfile.ZipFile, slide_path: str) -> list[str]:
    rel_path = f"ppt/slides/_rels/{Path(slide_path).name}.rels"
    if rel_path not in zf.namelist():
        raise DeckExtractionError(f"Missing relationship file for {slide_path}: {rel_path}")
    root = ET.fromstring(zf.read(rel_path))
    targets: list[str] = []
    for relationship in root.findall(f"{{{NS_REL}}}Relationship"):
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
    slides.sort()
    if not slides:
        raise DeckExtractionError("PPTX contains no ppt/slides/slideN.xml files.")

    mapped: list[tuple[int, str]] = []
    members = set(zf.namelist())
    for number, slide_path in slides:
        targets = _relationship_targets(zf, slide_path)
        if len(targets) != 1:
            raise DeckExtractionError(
                f"{slide_path} must map to exactly one embedded media file; found {targets!r}."
            )
        if targets[0] not in members:
            raise DeckExtractionError(f"{slide_path} points to missing media member {targets[0]}.")
        mapped.append((number, targets[0]))
    return mapped


def inspect_image(data: bytes) -> tuple[int, int, str]:
    try:
        with Image.open(BytesIO(data)) as image:
            return image.width, image.height, image.mode
    except Exception as exc:  # pragma: no cover - Pillow's exception varies by codec
        raise DeckExtractionError(f"Embedded media is not a readable raster image: {exc}") from exc


def extract_variant(
    deck: Mapping[str, Any],
    *,
    variant: str,
    deck_path: Path,
    output_root: Path,
    original_media_by_slide: Mapping[int, str],
) -> tuple[list[dict[str, Any]], dict[int, dict[str, Any]]]:
    deck_id = str(deck["deck_id"])
    slide_dir = output_root / deck_id / ("slides" if variant == "original" else "slides-cleaned")
    images: list[dict[str, Any]] = []
    by_slide: dict[int, dict[str, Any]] = {}
    with zipfile.ZipFile(deck_path) as zf:
        mapped = dict(map_slide_media(zf))
        if set(mapped) != set(original_media_by_slide):
            raise DeckExtractionError(f"{deck_id} {variant} deck slide numbering differs from original.")
        if variant == "cleaned":
            for number, member in original_media_by_slide.items():
                if mapped[number] != member:
                    raise DeckExtractionError(
                        f"{deck_id} cleaned slide {number} maps to {mapped[number]!r}, expected {member!r}."
                    )
        for number in sorted(mapped):
            member = mapped[number]
            data = zf.read(member)
            width, height, mode = inspect_image(data)
            image_id = f"{deck_id}-s{number:02d}-{variant}"
            relative_path = Path(deck_id) / ("slides" if variant == "original" else "slides-cleaned") / f"slide-{number:03d}.png"
            output_path = output_root / relative_path
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(data)
            record: dict[str, Any] = {
                "image_id": image_id,
                "deck_id": deck_id,
                "slide_id": f"{deck_id}-s{number:02d}",
                "slide_number": number,
                "variant": variant,
                "pptx_member": member,
                "extracted_path": relative_path.as_posix(),
                "sha256": sha256_bytes(data),
                "width": width,
                "height": height,
                "mode": mode,
            }
            if variant == "cleaned":
                record["parent_image_id"] = f"{deck_id}-s{number:02d}-original"
            images.append(record)
            by_slide[number] = record
    return images, by_slide


def _default_slide_context(deck_id: str, number: int, title: str | None = None) -> dict[str, Any]:
    display_title = str(title or deck_id).replace("-", " ").title()
    return {
        "label": f"{display_title} · source plate · slide {number:02d}",
        "summary": f"Raster source plate from {display_title}, slide {number:02d}; semantic meaning pending operator review.",
        "context_status": "review_only",
        "claim_refs": [],
        "cue_refs": [],
        "review_notes": "Structural deck/slide context only. Do not promote as evidence until the operator verifies the slide meaning and claim binding.",
    }


def _context_by_slide(config: Mapping[str, Any]) -> dict[tuple[str, int], dict[str, Any]]:
    contexts: dict[tuple[str, int], dict[str, Any]] = {}
    for item in config.get("slide_context", []):
        if not isinstance(item, dict):
            raise DeckExtractionError("Each slide_context entry must be an object.")
        deck_id = str(item.get("deck_id", ""))
        number = int(item.get("slide_number", 0))
        if not deck_id or number < 1:
            raise DeckExtractionError(f"Invalid slide_context entry: {item!r}")
        contexts[(deck_id, number)] = {
            "label": str(item.get("label", f"Slide {number:02d}")),
            "summary": str(item.get("summary", "Context pending operator review.")),
            "context_status": str(item.get("context_status", "review_only")),
            "claim_refs": list(item.get("claim_refs", [])),
            "cue_refs": list(item.get("cue_refs", [])),
            **({"review_notes": str(item["review_notes"])} if "review_notes" in item else {}),
        }
    return contexts


def _box_from_recipe(recipe: Mapping[str, Any], width: int, height: int) -> tuple[list[int], list[float]]:
    if "bbox_norm" in recipe:
        raw = recipe["bbox_norm"]
        if not isinstance(raw, list) or len(raw) != 4:
            raise DeckExtractionError(f"bbox_norm must be [x, y, width, height]: {recipe!r}")
        norm = [float(v) for v in raw]
        if any(v < 0 for v in norm) or norm[2] <= 0 or norm[3] <= 0 or norm[0] + norm[2] > 1 or norm[1] + norm[3] > 1:
            raise DeckExtractionError(f"bbox_norm is out of bounds: {norm!r}")
        px = [round(norm[0] * width), round(norm[1] * height), round(norm[2] * width), round(norm[3] * height)]
    elif "bbox_px" in recipe:
        raw = recipe["bbox_px"]
        if not isinstance(raw, list) or len(raw) != 4:
            raise DeckExtractionError(f"bbox_px must be [x, y, width, height]: {recipe!r}")
        px = [int(v) for v in raw]
        if px[0] < 0 or px[1] < 0 or px[2] <= 0 or px[3] <= 0 or px[0] + px[2] > width or px[1] + px[3] > height:
            raise DeckExtractionError(f"bbox_px is out of bounds: {px!r} for {width}x{height}")
        norm = [px[0] / width, px[1] / height, px[2] / width, px[3] / height]
    else:
        raise DeckExtractionError(f"Crop recipe needs bbox_norm or bbox_px: {recipe!r}")
    if px[2] < 2 or px[3] < 2:
        raise DeckExtractionError(f"Crop is too small: {px!r}")
    return px, norm


def _crop_image(source_path: Path, recipe: Mapping[str, Any], bbox_px: list[int], output_path: Path) -> str:
    method = "rect_crop"
    polygon = recipe.get("polygon_norm")
    with Image.open(source_path) as source:
        image = source.convert("RGBA")
        x, y, width, height = bbox_px
        cropped = image.crop((x, y, x + width, y + height))
        if polygon:
            if not isinstance(polygon, list) or len(polygon) < 3:
                raise DeckExtractionError("polygon_norm must contain at least three [x, y] points.")
            points = [(float(point[0]) * image.width - x, float(point[1]) * image.height - y) for point in polygon]
            mask = Image.new("L", cropped.size, 0)
            ImageDraw.Draw(mask).polygon(points, fill=255)
            cropped.putalpha(mask)
            method = "polygon_crop"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        cropped.save(output_path, format="PNG", optimize=False, compress_level=9)
    return method


def _default_reuse_policy() -> dict[str, Any]:
    return {
        "scope": "source_only",
        "max_total_uses": 1,
        "min_nonadjacent_gap": 0,
        "allowed_reasons": ["evidence_hold"],
        "claim_bound": False,
    }


def create_assets(
    config: Mapping[str, Any],
    *,
    output_root: Path,
    source_images: Mapping[str, dict[str, Any]],
    source_paths: Mapping[str, Path],
) -> list[dict[str, Any]]:
    assets: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    decks_by_id = {str(item["deck_id"]): item for item in config["decks"]}
    for recipe in config.get("crops", []):
        if not isinstance(recipe, dict):
            raise DeckExtractionError("Each crop recipe must be an object.")
        asset_id = slug(str(recipe.get("asset_id", "")))
        if asset_id in seen_ids:
            raise DeckExtractionError(f"Duplicate crop asset_id: {asset_id}")
        seen_ids.add(asset_id)
        deck_id = slug(str(recipe.get("deck_id", "")))
        number = int(recipe.get("slide_number", 0))
        if deck_id not in decks_by_id or number < 1:
            raise DeckExtractionError(f"Crop references unknown deck/slide: {recipe!r}")
        variant = str(recipe.get("source_variant", "original"))
        image_id = f"{deck_id}-s{number:02d}-{variant}"
        if image_id not in source_images or image_id not in source_paths:
            raise DeckExtractionError(f"Crop references unavailable source image {image_id}.")
        source_record = source_images[image_id]
        bbox_px, bbox_norm = _box_from_recipe(recipe, int(source_record["width"]), int(source_record["height"]))
        output_relative = Path(deck_id) / "semantic-assets" / "assets" / f"{asset_id}.png"
        output_path = output_root / output_relative
        method = _crop_image(source_paths[image_id], recipe, bbox_px, output_path)
        data = output_path.read_bytes()
        context = {
            "what_it_is": str(recipe.get("what_it_is", "Context pending operator review.")),
            "visual_role": str(recipe.get("visual_role", "reference")),
            "representation_mode": str(recipe.get("representation_mode", "declared_metaphor")),
            "factual_text": bool(recipe.get("factual_text", False)),
            "claim_refs": list(recipe.get("claim_refs", [])),
            "cue_refs": list(recipe.get("cue_refs", [])),
            "not_what_it_means": list(recipe.get("not_what_it_means", [])),
            "context_status": str(recipe.get("context_status", "review_only")),
            "reuse_policy": dict(recipe.get("reuse_policy", _default_reuse_policy())),
        }
        rights_state = str(recipe.get("rights_state", decks_by_id[deck_id].get("rights_state", "source_review_only")))
        review_state = str(recipe.get("review_state", "review_only"))
        render_eligible = bool(
            recipe.get("render_eligible", False)
            and rights_state == "approved"
            and review_state == "approved_reusable"
            and context["context_status"] == "operator_verified"
        )
        assets.append(
            {
                "asset_id": asset_id,
                "kind": "semantic_crop",
                "path": output_relative.as_posix(),
                "sha256": sha256_bytes(data),
                "deck_id": deck_id,
                "slide_id": f"{deck_id}-s{number:02d}",
                "slide_number": number,
                "parent_source_image_id": image_id,
                "source_variant": variant,
                "extraction": {
                    "method": method,
                    "bbox_px": bbox_px,
                    "bbox_norm": bbox_norm,
                    "polygon_norm": recipe.get("polygon_norm"),
                    "mask_path": None,
                    "source_sha256": str(source_record["sha256"]),
                },
                "context": context,
                "rights_state": rights_state,
                "review_state": review_state,
                "render_eligible": render_eligible,
            }
        )
    return assets


def _font(size: int) -> ImageFont.ImageFont:
    try:
        return ImageFont.truetype("arial.ttf", size)
    except OSError:
        return ImageFont.load_default()


def make_contact_sheet(records: Iterable[Mapping[str, Any]], output_path: Path, base_root: Path, *, title: str) -> None:
    records = list(records)
    tile_width, image_height, label_height = 320, 180, 58
    columns = 4
    rows = max(1, (len(records) + columns - 1) // columns)
    canvas = Image.new("RGB", (columns * tile_width, rows * (image_height + label_height) + 42), (243, 239, 230))
    draw = ImageDraw.Draw(canvas)
    draw.text((12, 10), title, fill=(30, 30, 30), font=_font(22))
    for index, record in enumerate(records):
        column = index % columns
        row = index // columns
        x = column * tile_width
        y = row * (image_height + label_height) + 42
        image_path = base_root / str(record["path"] if "path" in record else record["extracted_path"])
        if image_path.exists():
            with Image.open(image_path) as source:
                preview = ImageOps.contain(source.convert("RGB"), (tile_width - 12, image_height - 12))
            px = x + (tile_width - preview.width) // 2
            py = y + (image_height - preview.height) // 2
            canvas.paste(preview, (px, py))
        draw.rectangle((x, y, x + tile_width - 1, y + image_height - 1), outline=(120, 112, 100), width=1)
        label = str(record.get("selection_label", record.get("asset_id", record.get("image_id", "unknown"))))
        source = f"{record.get('deck_id', '')} / s{int(record.get('slide_number', 0)):02d}"
        status = str(record.get("review_state", record.get("variant", "source")))
        draw.text((x + 6, y + image_height + 5), label[:48], fill=(20, 20, 20), font=_font(13))
        draw.text((x + 6, y + image_height + 23), f"{source} · {status}", fill=(80, 75, 68), font=_font(11))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output_path, format="PNG", optimize=False, compress_level=9)


def write_selection_index(manifest: Mapping[str, Any], output_root: Path) -> None:
    """Write a human-readable asset picker without changing evidence status."""
    lines = [
        "# Deck asset selection index",
        "",
        f"Manifest: `{manifest['manifest_id']}`",
        "",
        "This index maps every extracted slide to its original and cleaned PNG paths. "
        "Source plates and semantic crops remain review-only until the manifest gates are cleared.",
        "",
    ]
    for deck in manifest["source_decks"]:
        deck_id = str(deck["deck_id"])
        title = str(deck["title"])
        lines.extend([f"## {title} (`{deck_id}`)", ""])
        slides = [slide for slide in manifest["slides"] if slide["deck_id"] == deck_id]
        original_by_slide = {record["slide_number"]: record for record in manifest["source_images"] if record["deck_id"] == deck_id}
        cleaned_by_slide = {record["slide_number"]: record for record in manifest["cleaned_images"] if record["deck_id"] == deck_id}
        for slide in slides:
            number = int(slide["slide_number"])
            context = slide["context"]
            original = original_by_slide[number]
            cleaned = cleaned_by_slide.get(number)
            lines.extend(
                [
                    f"### S{number:02d} · {slide['slide_label']}",
                    f"{context['summary']}",
                    f"- Original: [{original['extracted_path']}]({original['extracted_path']})",
                    f"- Cleaned: [{cleaned['extracted_path']}]({cleaned['extracted_path']})" if cleaned else "- Cleaned: not extracted",
                    f"- Context status: `{context['context_status']}`",
                    "",
                ]
            )
        assets = [asset for asset in manifest["assets"] if asset["deck_id"] == deck_id]
        if assets:
            lines.extend(["### Semantic crops", ""])
            for asset in assets:
                context = asset["context"]
                lines.extend(
                    [
                        f"- `{asset['asset_id']}` · S{int(asset['slide_number']):02d} · {context['visual_role']} · `{asset['review_state']}`",
                        f"  - What it is: {context['what_it_is']}",
                        f"  - Path: [{asset['path']}]({asset['path']})",
                        f"  - Source parent: `{asset['parent_source_image_id']}` ({asset['source_variant']})",
                        f"  - Render eligible: `{asset['render_eligible']}`",
                    ]
                )
            lines.append("")
    (output_root / "asset-selection-index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_manifest(config: Mapping[str, Any], output_root: Path) -> dict[str, Any]:
    source_images: list[dict[str, Any]] = []
    cleaned_source_images: list[dict[str, Any]] = []
    source_image_lookup: dict[str, dict[str, Any]] = {}
    source_paths: dict[str, Path] = {}
    source_decks: list[dict[str, Any]] = []
    slides: list[dict[str, Any]] = []
    context_map = _context_by_slide(config)

    for deck in config["decks"]:
        deck_id = slug(str(deck["deck_id"]))
        source_path = Path(str(deck["source_path"])).resolve()
        if not source_path.exists():
            raise DeckExtractionError(f"Source deck does not exist: {source_path}")
        original_sha = sha256_bytes(source_path.read_bytes())
        with zipfile.ZipFile(source_path) as zf:
            original_media_by_slide = dict(map_slide_media(zf))
        original_images, original_by_slide = extract_variant(
            deck,
            variant="original",
            deck_path=source_path,
            output_root=output_root,
            original_media_by_slide=original_media_by_slide,
        )
        deck_title = str(deck.get("title", deck_id))
        for record in original_images:
            context = context_map.get((deck_id, int(record["slide_number"])), _default_slide_context(deck_id, int(record["slide_number"]), deck_title))
            record["selection_label"] = f"{deck_title} · S{int(record['slide_number']):02d} · {context['label']}"
            record["context"] = context
        for record in original_images:
            source_images.append(record)
            source_image_lookup[record["image_id"]] = record
            source_paths[record["image_id"]] = output_root / record["extracted_path"]

        cleaned_path_raw = deck.get("cleaned_path")
        cleaned_variant_images: list[dict[str, Any]] = []
        cleaned_by_slide: dict[int, dict[str, Any]] = {}
        cleaned_sha: str | None = None
        if cleaned_path_raw:
            cleaned_path = Path(str(cleaned_path_raw)).resolve()
            if not cleaned_path.exists():
                raise DeckExtractionError(f"Cleaned deck does not exist: {cleaned_path}")
            cleaned_sha = sha256_bytes(cleaned_path.read_bytes())
            cleaned_variant_images, cleaned_by_slide = extract_variant(
                deck,
                variant="cleaned",
                deck_path=cleaned_path,
                output_root=output_root,
                original_media_by_slide=original_media_by_slide,
            )
            for record in cleaned_variant_images:
                context = context_map.get((deck_id, int(record["slide_number"])), _default_slide_context(deck_id, int(record["slide_number"]), deck_title))
                record["selection_label"] = f"{deck_title} · S{int(record['slide_number']):02d} · {context['label']}"
                record["context"] = context
            for record in cleaned_variant_images:
                cleaned_source_images.append(record)
                source_image_lookup[record["image_id"]] = record
                source_paths[record["image_id"]] = output_root / record["extracted_path"]

        source_family = str(deck.get("source_family", "operator-supplied-research-deck"))
        source_decks.append(
            {
                "deck_id": deck_id,
                "title": str(deck.get("title", deck_id)),
                "source_path": str(source_path),
                "source_sha256": original_sha,
                "source_family": source_family,
                "rights_state": str(deck.get("rights_state", "source_review_only")),
                "cleanup": {
                    "requested": bool(cleaned_path_raw),
                    "input_path": str(Path(str(cleaned_path_raw)).resolve()) if cleaned_path_raw else None,
                    "original_sha256": original_sha if cleaned_path_raw else None,
                    "cleaned_sha256": cleaned_sha,
                    "policy": str(deck.get("cleanup_policy", DEFAULT_CLEANUP_POLICY if cleaned_path_raw else "No derivative cleanup requested.")),
                    "approved": bool(deck.get("cleanup_approved", False)),
                },
            }
        )
        for number in sorted(original_by_slide):
            context = context_map.get((deck_id, number), _default_slide_context(deck_id, number, deck_title))
            slides.append(
                {
                    "slide_id": f"{deck_id}-s{number:02d}",
                    "deck_id": deck_id,
                    "slide_number": number,
                    "slide_label": str(context["label"]),
                    "source_image_id": f"{deck_id}-s{number:02d}-original",
                    "context": context,
                }
            )

    assets = create_assets(config, output_root=output_root, source_images=source_image_lookup, source_paths=source_paths)
    by_deck_assets: dict[str, list[dict[str, Any]]] = {str(deck["deck_id"]): [] for deck in config["decks"]}
    for asset in assets:
        by_deck_assets[asset["deck_id"]].append(asset)

    source_preview_images = [record for record in source_images if record["variant"] == "original"]
    semantic_records = assets
    for deck in source_decks:
        deck_id = deck["deck_id"]
        deck_root = output_root / deck_id
        deck_review = deck_root / "review"
        slide_records = [record for record in slides if record["deck_id"] == deck_id]
        slide_images = [record for record in source_preview_images if record["deck_id"] == deck_id]
        make_contact_sheet(slide_images, deck_review / "slide-contact-sheet.png", output_root, title=f"{deck['title']} · source slides")
        make_contact_sheet(by_deck_assets[deck_id], deck_review / "semantic-contact-sheet.png", output_root, title=f"{deck['title']} · semantic crops")
        context_payload = {
            "schema_version": "deck_asset_context.v1",
            "deck_id": deck_id,
            "assets": by_deck_assets[deck_id],
        }
        context_payload["artifact_hash"] = canonical_hash(context_payload)
        write_json(deck_root / "semantic-assets" / "asset-context.json", context_payload)
        coverage = {
            "schema_version": "deck_asset_coverage.v1",
            "deck_id": deck_id,
            "slide_count": len(slide_records),
            "source_image_count": len(slide_images),
            "semantic_asset_count": len(by_deck_assets[deck_id]),
            "render_eligible_count": sum(1 for asset in by_deck_assets[deck_id] if asset["render_eligible"]),
            "status": "needs_human_review",
            "checks": {
                "source_slides_present": len(slide_records) == len(slide_images),
                "semantic_context_complete": all(asset["context"]["what_it_is"] for asset in by_deck_assets[deck_id]),
                "render_eligibility_gated": all(not asset["render_eligible"] or (asset["rights_state"] == "approved" and asset["review_state"] == "approved_reusable" and asset["context"]["context_status"] == "operator_verified") for asset in by_deck_assets[deck_id]),
            },
            "human_gates": {"H1": False, "H2": False, "H3": False, "H4": False},
            "artifact_hash": "",
        }
        coverage["artifact_hash"] = canonical_hash(coverage)
        write_json(deck_review / "coverage-report.json", coverage)

        deck_manifest = {
            "schema_version": SCHEMA_VERSION,
            "manifest_id": f"{config.get('manifest_id', 'deck-asset-manifest')}-{deck_id}",
            "project_id": str(config.get("project_id", "systems-and-blowups")),
            "source_decks": [deck],
            "slides": slide_records,
            "source_images": [record for record in source_images if record["deck_id"] == deck_id],
            "cleaned_images": [record for record in cleaned_source_images if record["deck_id"] == deck_id],
            "assets": by_deck_assets[deck_id],
            "review": {
                "slide_contact_sheet": f"{deck_id}/review/slide-contact-sheet.png",
                "semantic_contact_sheet": f"{deck_id}/review/semantic-contact-sheet.png",
                "coverage_report": f"{deck_id}/review/coverage-report.json",
                "promotion_policy": str(config.get("promotion_policy", DEFAULT_PROMOTION_POLICY)),
            },
            "artifact_hash": "",
        }
        deck_manifest["artifact_hash"] = canonical_hash(deck_manifest)
        write_json(deck_root / "source-manifest.json", deck_manifest)

    manifest: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "manifest_id": str(config.get("manifest_id", "deck-asset-manifest")),
        "project_id": str(config.get("project_id", "systems-and-blowups")),
        "source_decks": source_decks,
        "slides": slides,
        "source_images": source_images,
        "cleaned_images": cleaned_source_images,
        "assets": assets,
        "review": {
            "slide_contact_sheet": "<deck_id>/review/slide-contact-sheet.png",
            "semantic_contact_sheet": "<deck_id>/review/semantic-contact-sheet.png",
            "coverage_report": "<deck_id>/review/coverage-report.json",
            "selection_index": "asset-selection-index.md",
            "promotion_policy": str(config.get("promotion_policy", DEFAULT_PROMOTION_POLICY)),
        },
        "artifact_hash": "",
    }
    manifest["artifact_hash"] = canonical_hash(manifest)
    write_json(output_root / "deck-asset-manifest.json", manifest)
    write_selection_index(manifest, output_root)
    return manifest


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True, help="JSON deck source and crop recipe config")
    parser.add_argument("--output-root", type=Path, required=True, help="Output directory for source and derived assets")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        config = load_config(args.config)
        output_root = args.output_root.resolve()
        output_root.mkdir(parents=True, exist_ok=True)
        manifest = build_manifest(config, output_root)
        print(json.dumps({"manifest": str(output_root / "deck-asset-manifest.json"), "artifact_hash": manifest["artifact_hash"], "slides": len(manifest["slides"]), "source_images": len(manifest["source_images"]), "cleaned_images": len(manifest["cleaned_images"]), "assets": len(manifest["assets"])}, indent=2))
        return 0
    except (DeckExtractionError, OSError, zipfile.BadZipFile, ET.ParseError) as exc:
        print(f"extract_deck_assets: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
