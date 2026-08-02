"""Magnific stock discovery, review, and fail-closed asset promotion."""

from __future__ import annotations

import copy
import hashlib
import json
import os
import re
import textwrap
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Any, Mapping, Protocol

from PIL import Image, ImageDraw, ImageOps

from content.video_engine.src.models import StageContext, StageOutput, VideoRun
from content.video_engine.src.services.history_contracts import canonical_sha256
from content.video_engine.src.services.living_editorial import (
    EDITORIAL_COVERAGE_VERSION,
    compile_editorial_coverage,
    validate_editorial_coverage,
)
from content.video_engine.src.services.producer_orchestration import (
    compile_producer_plan,
    validate_producer_plan,
)


STOCK_BATCH_VERSION = "stock_candidate_batch.v1"
ASSET_SELECTION_VERSION = "asset_selection_review.v1"
REFERENCE_REGISTRY_VERSION = "provider_reference_registry.v1"
FLOW_SNAPSHOT_VERSION = "provider_flow_snapshot.v1"
MAX_PREVIEW_BYTES = 12 * 1024 * 1024
MAX_ASSET_BYTES = 80 * 1024 * 1024
STOCK_SOURCES = {"stock_photo", "stock_vector"}
REFERENCE_KINDS = {"style", "character", "element", "location", "template"}


class StockAssetError(ValueError):
    """Raised when stock provenance, review, or local bytes are unsafe."""


def _read_json(value: Mapping[str, Any] | str | Path, label: str) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return copy.deepcopy(dict(value))
    try:
        payload = json.loads(Path(value).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise StockAssetError(f"{label} is not valid JSON: {exc}") from exc
    if not isinstance(payload, Mapping):
        raise StockAssetError(f"{label} root must be an object")
    return dict(payload)


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _inside(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


def _contained(value: str | Path, root: Path, label: str) -> Path:
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = root / candidate
    resolved = candidate.resolve()
    if not _inside(resolved, root):
        raise StockAssetError(f"{label} escapes the job directory")
    return resolved


def _image_extension(data: bytes, content_type: str = "") -> str:
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png"
    if data.startswith(b"\xff\xd8\xff"):
        return ".jpg"
    if len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return ".webp"
    if "svg" in content_type.casefold() or data.lstrip().startswith(b"<svg"):
        return ".svg"
    raise StockAssetError("downloaded stock bytes are not PNG, JPEG, WebP, or SVG")


def _preview_dhash(data: bytes) -> int | None:
    try:
        with Image.open(BytesIO(data)) as opened:
            pixels = list(
                opened.convert("L")
                .resize((9, 8), Image.Resampling.LANCZOS)
                .get_flattened_data()
            )
    except OSError:
        return None
    value = 0
    for row in range(8):
        for column in range(8):
            left = pixels[(row * 9) + column]
            right = pixels[(row * 9) + column + 1]
            value = (value << 1) | int(left > right)
    return value


class MagnificStockTransport(Protocol):
    def search(self, term: str, *, limit: int = 8) -> list[dict[str, Any]]:
        ...

    def download_url(self, resource_id: str, resource_format: str) -> Mapping[str, Any]:
        ...

    def download_bytes(self, url: str, *, maximum: int) -> tuple[bytes, str]:
        ...


@dataclass(frozen=True, slots=True)
class MagnificStockSettings:
    api_key: str
    base_url: str = "https://api.magnific.com"
    timeout_s: float = 45.0
    account_plan: str = "unknown"
    included_downloads: bool = False
    daily_download_limit: int = 0

    @classmethod
    def from_environment(cls) -> "MagnificStockSettings":
        api_key = str(os.environ.get("MAGNIFIC_API_KEY") or "").strip()
        if not api_key:
            raise StockAssetError("MAGNIFIC_API_KEY is required for live stock search")
        return cls(
            api_key=api_key,
            base_url=str(
                os.environ.get("MAGNIFIC_BASE_URL") or "https://api.magnific.com"
            ).rstrip("/"),
            timeout_s=float(os.environ.get("MAGNIFIC_TIMEOUT_S") or 45),
            account_plan=str(os.environ.get("MAGNIFIC_ACCOUNT_PLAN") or "unknown"),
            included_downloads=str(
                os.environ.get("MAGNIFIC_STOCK_DOWNLOADS_INCLUDED") or ""
            ).casefold()
            in {"1", "true", "yes"},
            daily_download_limit=int(
                os.environ.get("MAGNIFIC_STOCK_DAILY_DOWNLOAD_LIMIT") or 0
            ),
        )


class MagnificStockHttpTransport:
    """Read/search Magnific stock and download only explicitly selected assets."""

    def __init__(self, settings: MagnificStockSettings) -> None:
        self.settings = settings

    def _json(self, path: str) -> Mapping[str, Any]:
        request = urllib.request.Request(
            f"{self.settings.base_url}{path}",
            headers={
                "Accept": "application/json",
                "x-magnific-api-key": self.settings.api_key,
            },
        )
        try:
            with urllib.request.urlopen(
                request, timeout=self.settings.timeout_s
            ) as response:
                raw = response.read()
        except urllib.error.HTTPError as exc:
            raise StockAssetError(
                f"Magnific stock request failed with HTTP {exc.code}"
            ) from exc
        except urllib.error.URLError as exc:
            raise StockAssetError("Magnific stock request failed") from exc
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise StockAssetError("Magnific stock returned invalid JSON") from exc
        if not isinstance(payload, Mapping):
            raise StockAssetError("Magnific stock returned a non-object response")
        return payload

    def search(self, term: str, *, limit: int = 8) -> list[dict[str, Any]]:
        query = urllib.parse.urlencode(
            {
                "term": term,
                "limit": max(1, min(int(limit), 20)),
                "page": 1,
                "order": "relevance",
            }
        )
        payload = self._json(f"/v1/resources?{query}")
        data = payload.get("data")
        if isinstance(data, Mapping):
            data = data.get("data") or data.get("items")
        if not isinstance(data, list):
            return []
        return [dict(item) for item in data if isinstance(item, Mapping)]

    def download_url(
        self, resource_id: str, resource_format: str
    ) -> Mapping[str, Any]:
        safe_id = urllib.parse.quote(str(resource_id), safe="")
        safe_format = urllib.parse.quote(str(resource_format), safe="")
        payload = self._json(
            f"/v1/resources/{safe_id}/download/{safe_format}"
        )
        data = payload.get("data", payload)
        if isinstance(data, list):
            data = data[0] if data else {}
        if not isinstance(data, Mapping):
            raise StockAssetError("Magnific download response has no object data")
        return dict(data)

    def download_bytes(self, url: str, *, maximum: int) -> tuple[bytes, str]:
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme != "https" or not parsed.netloc:
            raise StockAssetError("stock download URL must use HTTPS")
        request = urllib.request.Request(url, headers={"Accept": "image/*,*/*"})
        try:
            with urllib.request.urlopen(
                request, timeout=self.settings.timeout_s
            ) as response:
                content_type = str(response.headers.get("Content-Type") or "")
                data = response.read(maximum + 1)
        except urllib.error.URLError as exc:
            raise StockAssetError("stock media download failed") from exc
        if len(data) > maximum:
            raise StockAssetError("stock media download exceeds the size limit")
        return data, content_type


def _preview_url(resource: Mapping[str, Any]) -> str:
    image = resource.get("image")
    if isinstance(image, Mapping):
        source = image.get("source")
        if isinstance(source, Mapping) and source.get("url"):
            value = str(source["url"])
            return (
                "https://" + value.removeprefix("http://").removeprefix("//")
                if value.startswith(("http://", "//"))
                else value
            )
    preview = resource.get("preview")
    if isinstance(preview, Mapping) and preview.get("url"):
        value = str(preview["url"])
        return (
            "https://" + value.removeprefix("http://").removeprefix("//")
            if value.startswith(("http://", "//"))
            else value
        )
    return ""


def _media_type(resource: Mapping[str, Any]) -> str:
    image = resource.get("image")
    if isinstance(image, Mapping) and image.get("type"):
        return str(image["type"]).casefold()
    return str(resource.get("type") or "photo").casefold()


def _license_record(resource: Mapping[str, Any]) -> tuple[str, str]:
    licenses = resource.get("licenses")
    if isinstance(licenses, list) and licenses:
        first = licenses[0]
        if isinstance(first, Mapping):
            return (
                str(first.get("type") or "licensed"),
                str(first.get("url") or ""),
            )
    value = resource.get("license")
    if value:
        return ("licensed", str(value))
    return ("", "")


def _author_name(resource: Mapping[str, Any]) -> str:
    author = resource.get("author")
    if isinstance(author, Mapping):
        return str(author.get("name") or author.get("slug") or "")
    return str(author or "")


def _normalized_text(value: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", value.casefold()))


def _term_present(haystack: str, term: str) -> bool:
    normalized = _normalized_text(term)
    return bool(normalized) and f" {normalized} " in f" {haystack} "


def _resource_relevance_text(resource: Mapping[str, Any]) -> str:
    values: list[str] = []
    relevant_keys = {
        "category",
        "categories",
        "description",
        "keyword",
        "keywords",
        "name",
        "style",
        "subject",
        "tag",
        "tags",
        "title",
        "type",
    }

    def collect(value: Any, key: str = "") -> None:
        if isinstance(value, Mapping):
            for child_key, child in value.items():
                collect(child, str(child_key).casefold())
        elif isinstance(value, list):
            for child in value:
                collect(child, key)
        elif key in relevant_keys and isinstance(value, (str, int, float)):
            values.append(str(value))

    collect(resource)
    return _normalized_text(" ".join(values))


def score_stock_candidate(
    slot: Mapping[str, Any],
    resource: Mapping[str, Any],
) -> dict[str, Any]:
    """Reject category mismatches before any provider preview is downloaded."""

    haystack = _resource_relevance_text(resource)
    blocked = [
        str(term)
        for term in slot.get("blocked_terms") or []
        if _term_present(haystack, str(term))
    ]
    if blocked:
        return {
            "accepted": False,
            "score": -100,
            "matched_terms": [],
            "rejected_terms": blocked,
        }

    required = [str(term) for term in slot.get("required_terms") or []]
    matched_required = [
        term for term in required if _term_present(haystack, term)
    ]
    # Old snapshotted V4.1 artifacts did not carry relevance terms. Preserve
    # their readability; all newly compiled stock slots require a domain match.
    if required and not matched_required:
        return {
            "accepted": False,
            "score": 0,
            "matched_terms": [],
            "rejected_terms": ["missing required theme match"],
        }
    required_groups = [
        [str(term) for term in group]
        for group in slot.get("required_term_groups") or []
        if isinstance(group, list)
    ]
    missing_groups = [
        group
        for group in required_groups
        if not any(_term_present(haystack, term) for term in group)
    ]
    if missing_groups:
        return {
            "accepted": False,
            "score": 0,
            "matched_terms": matched_required,
            "rejected_terms": ["missing required archetype facet"],
        }
    concepts = [
        str(term)
        for term in slot.get("search_concepts") or []
        if _term_present(haystack, str(term))
    ]
    score = (len(matched_required) * 3) + (len(concepts) * 2)
    return {
        "accepted": True,
        "score": score,
        "matched_terms": sorted(set([*matched_required, *concepts])),
        "rejected_terms": [],
    }


def _fallback_preview(path: Path, slot: Mapping[str, Any]) -> None:
    image = Image.new("RGB", (640, 360), "#151C24")
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 12, 360), fill="#20D69B")
    draw.text((38, 34), "LOCAL FALLBACK", fill="#20D69B")
    excerpt = str(slot.get("narration_excerpt") or "")
    lines = textwrap.wrap(excerpt, width=45)[:5]
    draw.multiline_text((38, 86), "\n".join(lines), fill="#F4F7FA", spacing=8)
    draw.text(
        (38, 320),
        str(slot.get("fallback_visual_source") or "typography").upper(),
        fill="#FF8A3D",
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, format="PNG")


def _contact_sheet(
    batch: Mapping[str, Any],
    *,
    job_dir: Path,
    output_path: Path,
) -> None:
    candidates = list(batch.get("candidates") or [])
    width, height = 480, 365
    columns = 3
    rows = max(1, (len(candidates) + columns - 1) // columns)
    sheet = Image.new("RGB", (columns * width, rows * height), "#0B0F14")
    for index, candidate in enumerate(candidates):
        card = Image.new("RGB", (width, height), "#151C24")
        preview = _contained(
            str(candidate.get("preview_path") or ""),
            job_dir,
            "candidate preview",
        )
        try:
            with Image.open(preview) as opened:
                visual = ImageOps.fit(
                    opened.convert("RGB"),
                    (width, 235),
                    method=Image.Resampling.LANCZOS,
                )
            card.paste(visual, (0, 0))
        except OSError:
            pass
        draw = ImageDraw.Draw(card)
        draw.rectangle((0, 235, width, height), fill="#151C24")
        draw.text(
            (14, 246),
            (
                f"{candidate.get('visual_archetype') or 'local_fallback'} / "
                f"{candidate.get('media_type')} / "
                f"score {candidate.get('relevance_score', '-')}"
            )[:64],
            fill="#20D69B",
        )
        title_lines = textwrap.wrap(
            str(candidate.get("title") or "Untitled candidate"),
            width=64,
        )[:2]
        draw.text(
            (14, 270),
            "\n".join(title_lines),
            fill="#F4F7FA",
        )
        draw.text(
            (14, 316),
            str(candidate.get("slot_id") or "")[:62],
            fill="#C9D2DA",
        )
        draw.text(
            (14, 340),
            str(candidate.get("candidate_id") or "")[:62],
            fill="#88939D",
        )
        sheet.paste(card, ((index % columns) * width, (index // columns) * height))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output_path, format="PNG")


def write_asset_review_packet(
    batch: Mapping[str, Any],
    *,
    job_dir: str | Path,
) -> Path:
    root = Path(job_dir).resolve()
    candidates = [
        item for item in batch.get("candidates") or [] if isinstance(item, Mapping)
    ]
    remote = [item for item in candidates if item.get("provider") == "magnific"]
    entitlement: dict[str, Any] = {}
    entitlement_path = root / "asset_selection" / "entitlement.json"
    if entitlement_path.is_file():
        try:
            entitlement = _read_json(entitlement_path, "stock entitlement")
        except StockAssetError:
            entitlement = {}
    included = entitlement.get("downloads_included") is True
    unknown_cost = [
        item
        for item in remote
        if item.get("estimated_cost_usd") is None and not included
    ]
    lines = [
        "# Episode Asset Selection Gate",
        "",
        f"- Coverage hash: `{batch.get('coverage_hash')}`",
        f"- Candidate batch hash: `{batch.get('artifact_hash')}`",
        f"- Stock coverage slots: {len(batch.get('stock_slot_ids') or [])}",
        f"- Magnific candidates: {len(remote)}",
        f"- Local fallbacks: {len(candidates) - len(remote)}",
        f"- Theme mismatches rejected before preview: "
        f"{batch.get('relevance_rejection_count') or 0}",
        f"- Duplicate resources/previews rejected: "
        f"{batch.get('duplicate_rejection_count') or 0}",
        f"- Unknown-cost candidates (blocked): {len(unknown_cost)}",
        f"- Account plan: {entitlement.get('account_plan') or 'unknown'}",
        f"- Daily full-resolution download limit: "
        f"{entitlement.get('daily_download_limit') or 'unknown'}",
        "",
        "Review `contact-sheet.png`, then fill every slot in "
        "`review-template.json`. A Magnific candidate cannot pass while its "
        "cost or plan entitlement is unknown. Candidate previews remain "
        "non-renderable.",
        "",
        "Approval command:",
        "",
        "```powershell",
        "python -m content.video_engine.cli --artifact-root "
        ".context/p13-history-v4-1/jobs approve <JOB_ID> "
        "--gate assets --rubric <COMPLETED_REVIEW.json>",
        "```",
        "",
    ]
    packet = root / "asset_selection" / "review-packet.md"
    packet.write_text("\n".join(lines), encoding="utf-8")
    return packet


class StockCandidateService:
    """Build a quarantined stock contact sheet without downloading full assets."""

    def __init__(
        self,
        transport: MagnificStockTransport | None = None,
        settings: MagnificStockSettings | None = None,
    ) -> None:
        self.settings = settings
        self.transport = transport or (
            MagnificStockHttpTransport(settings) if settings is not None else None
        )

    def build_batch(
        self,
        coverage: Mapping[str, Any] | str | Path,
        *,
        job_dir: str | Path,
        live_search: bool = False,
        candidates_per_slot: int = 3,
    ) -> dict[str, Any]:
        payload = _read_json(coverage, "editorial coverage")
        coverage_errors = validate_editorial_coverage(payload)
        if coverage_errors:
            raise StockAssetError("; ".join(coverage_errors))
        root = Path(job_dir).resolve()
        preview_root = root / "asset_selection" / "previews"
        preview_root.mkdir(parents=True, exist_ok=True)
        stock_slots = [
            slot
            for slot in payload["slots"]
            if slot.get("preferred_visual_source") in STOCK_SOURCES
            and slot.get("stock_eligible", True) is True
        ]
        candidates: list[dict[str, Any]] = []
        search_call_count = 0
        preview_download_count = 0
        relevance_rejection_count = 0
        duplicate_rejection_count = 0
        used_resource_ids: set[str] = set()
        used_preview_hashes: list[int] = []
        for slot in stock_slots:
            slot_id = str(slot["slot_id"])
            query = str(slot.get("search_query") or "").strip() or " ".join(
                str(value) for value in slot["search_concepts"]
            )
            desired = (
                "vector"
                if slot["preferred_visual_source"] == "stock_vector"
                else "photo"
            )
            resources: list[dict[str, Any]] = []
            if live_search:
                if self.transport is None:
                    raise StockAssetError(
                        "live stock search requires Magnific settings"
                    )
                resources = self.transport.search(
                    query,
                    limit=20,
                )
                search_call_count += 1
            accepted = 0
            ranked: list[tuple[int, dict[str, Any], dict[str, Any]]] = []
            for resource in resources:
                relevance = score_stock_candidate(slot, resource)
                if not relevance["accepted"]:
                    relevance_rejection_count += 1
                    continue
                ranked.append((int(relevance["score"]), resource, relevance))
            ranked.sort(key=lambda item: item[0], reverse=True)
            for _, resource, relevance in ranked:
                if accepted >= candidates_per_slot:
                    break
                media_type = _media_type(resource)
                if desired == "vector" and media_type != "vector":
                    continue
                if desired == "photo" and media_type not in {"photo", "image"}:
                    continue
                resource_id = str(resource.get("id") or "").strip()
                if not resource_id:
                    continue
                if resource_id in used_resource_ids:
                    duplicate_rejection_count += 1
                    continue
                preview_url = _preview_url(resource)
                if not preview_url:
                    continue
                assert self.transport is not None
                data, content_type = self.transport.download_bytes(
                    preview_url,
                    maximum=MAX_PREVIEW_BYTES,
                )
                preview_download_count += 1
                extension = _image_extension(data, content_type)
                preview_dhash = _preview_dhash(data)
                if preview_dhash is not None and any(
                    (preview_dhash ^ prior).bit_count() <= 6
                    for prior in used_preview_hashes
                ):
                    duplicate_rejection_count += 1
                    continue
                candidate_id = f"{slot_id}-magnific-{resource_id}"
                preview_path = preview_root / f"{candidate_id}{extension}"
                preview_path.write_bytes(data)
                license_type, license_url = _license_record(resource)
                author = _author_name(resource)
                account_plan = (
                    self.settings.account_plan if self.settings is not None else "unknown"
                )
                included = bool(
                    self.settings is not None
                    and self.settings.included_downloads
                )
                candidates.append(
                    {
                        "candidate_id": candidate_id,
                        "slot_id": slot_id,
                        "provider": "magnific",
                        "resource_id": resource_id,
                        "media_type": media_type,
                        "title": str(
                            resource.get("title")
                            or resource.get("name")
                            or candidate_id
                        ),
                        "visual_archetype": str(
                            slot.get("visual_archetype") or ""
                        ),
                        "search_query": query,
                        "relevance_score": int(relevance["score"]),
                        "matched_terms": list(relevance["matched_terms"]),
                        "preview_dhash": (
                            f"{preview_dhash:016x}"
                            if preview_dhash is not None
                            else ""
                        ),
                        "creator": author,
                        "canonical_url": str(resource.get("url") or ""),
                        "preview_path": preview_path.relative_to(root).as_posix(),
                        "preview_sha256": _sha256(preview_path),
                        "license_type": license_type,
                        "license_url": license_url,
                        "plan_snapshot": account_plan,
                        "attribution_required": account_plan.casefold()
                        in {"free", "essential", "unknown"},
                        "attribution": (
                            f"{author or 'Creator'} via Magnific"
                            if author
                            else ""
                        ),
                        "estimated_cost_usd": 0.0 if included else None,
                        "alteration_allowed": True,
                        "download_format": "svg" if media_type == "vector" else "jpg",
                        "render_eligible": False,
                        "status": "pending_review",
                    }
                )
                used_resource_ids.add(resource_id)
                if preview_dhash is not None:
                    used_preview_hashes.append(preview_dhash)
                accepted += 1

            fallback_id = f"{slot_id}-local-fallback"
            fallback_path = preview_root / f"{fallback_id}.png"
            _fallback_preview(fallback_path, slot)
            candidates.append(
                {
                    "candidate_id": fallback_id,
                    "slot_id": slot_id,
                    "provider": "local",
                    "resource_id": fallback_id,
                    "media_type": str(slot["fallback_visual_source"]),
                    "title": "Use deterministic local fallback",
                    "creator": "Outreach Program",
                    "canonical_url": "",
                    "preview_path": fallback_path.relative_to(root).as_posix(),
                    "preview_sha256": _sha256(fallback_path),
                    "license_type": "original",
                    "license_url": "",
                    "plan_snapshot": "local",
                    "attribution_required": False,
                    "attribution": "",
                    "estimated_cost_usd": 0.0,
                    "alteration_allowed": True,
                    "download_format": "png",
                    "render_eligible": False,
                    "status": "pending_review",
                }
            )

        core = {
            "schema_version": STOCK_BATCH_VERSION,
            "provider": "magnific",
            "coverage_hash": payload["artifact_hash"],
            "stock_slot_ids": [str(slot["slot_id"]) for slot in stock_slots],
            "search_call_count": search_call_count,
            "preview_download_count": preview_download_count,
            "relevance_rejection_count": relevance_rejection_count,
            "duplicate_rejection_count": duplicate_rejection_count,
            "entitlement_snapshot": {
                "account_plan": (
                    self.settings.account_plan
                    if self.settings is not None
                    else "unknown"
                ),
                "downloads_included": bool(
                    self.settings is not None
                    and self.settings.included_downloads
                ),
                "daily_download_limit": int(
                    self.settings.daily_download_limit
                    if self.settings is not None
                    else 0
                ),
            },
            "candidate_count": len(candidates),
            "candidates": candidates,
        }
        batch = {**core, "artifact_hash": canonical_sha256(core)}
        errors = validate_stock_candidate_batch(batch, job_dir=root)
        if errors:
            raise StockAssetError("; ".join(errors))
        batch_path = root / "asset_selection" / "stock-candidates.json"
        _write_json(batch_path, batch)
        contact_path = root / "asset_selection" / "contact-sheet.png"
        _contact_sheet(batch, job_dir=root, output_path=contact_path)
        review = {
            "schema_version": ASSET_SELECTION_VERSION,
            "coverage_hash": payload["artifact_hash"],
            "candidate_batch_hash": batch["artifact_hash"],
            "approved": False,
            "reviewed_by": "",
            "reviewed_at": "",
            "selections": [
                {
                    "slot_id": slot_id,
                    "candidate_id": "",
                    "approved_cost_usd": 0.0,
                }
                for slot_id in batch["stock_slot_ids"]
            ],
        }
        _write_json(root / "asset_selection" / "review-template.json", review)
        write_asset_review_packet(batch, job_dir=root)
        return batch


def validate_stock_candidate_batch(
    value: Mapping[str, Any] | str | Path,
    *,
    job_dir: str | Path | None = None,
) -> list[str]:
    try:
        payload = _read_json(value, "stock candidate batch")
    except StockAssetError as exc:
        return [str(exc)]
    errors: list[str] = []
    if payload.get("schema_version") != STOCK_BATCH_VERSION:
        errors.append(f"stock batch must use {STOCK_BATCH_VERSION}")
    candidates = payload.get("candidates")
    if not isinstance(candidates, list):
        return [*errors, "stock batch candidates must be an array"]
    seen: set[str] = set()
    root = Path(job_dir).resolve() if job_dir is not None else None
    for index, candidate in enumerate(candidates):
        if not isinstance(candidate, Mapping):
            errors.append(f"candidates[{index}] must be an object")
            continue
        candidate_id = str(candidate.get("candidate_id") or "")
        if not candidate_id or candidate_id in seen:
            errors.append(f"candidates[{index}].candidate_id must be unique")
        seen.add(candidate_id)
        if candidate.get("render_eligible") is not False:
            errors.append(f"{candidate_id or index} must remain non-renderable")
        if not candidate.get("slot_id"):
            errors.append(f"{candidate_id or index} requires slot_id")
        if candidate.get("provider") == "magnific":
            if not candidate.get("resource_id"):
                errors.append(f"{candidate_id or index} requires resource_id")
            if not candidate.get("license_type") or not candidate.get("license_url"):
                errors.append(f"{candidate_id or index} requires license evidence")
        if root is not None:
            try:
                preview = _contained(
                    str(candidate.get("preview_path") or ""),
                    root,
                    f"{candidate_id} preview",
                )
            except StockAssetError as exc:
                errors.append(str(exc))
                continue
            if not preview.is_file():
                errors.append(f"{candidate_id} preview is missing")
            elif _sha256(preview) != candidate.get("preview_sha256"):
                errors.append(f"{candidate_id} preview hash is stale")
    expected = canonical_sha256(
        {key: item for key, item in payload.items() if key != "artifact_hash"}
    )
    if payload.get("artifact_hash") != expected:
        errors.append("stock batch artifact_hash does not match content")
    return errors


def validate_asset_selection(
    selection: Mapping[str, Any] | str | Path,
    batch: Mapping[str, Any] | str | Path,
    *,
    expected_coverage_hash: str = "",
) -> list[str]:
    try:
        review = _read_json(selection, "asset selection review")
        candidates_payload = _read_json(batch, "stock candidate batch")
    except StockAssetError as exc:
        return [str(exc)]
    errors: list[str] = []
    if review.get("schema_version") != ASSET_SELECTION_VERSION:
        errors.append(f"asset selection must use {ASSET_SELECTION_VERSION}")
    if review.get("approved") is not True:
        errors.append("asset selection review must set approved=true")
    if not str(review.get("reviewed_by") or "").strip():
        errors.append("asset selection review requires reviewed_by")
    coverage_hash = str(review.get("coverage_hash") or "")
    if coverage_hash != str(candidates_payload.get("coverage_hash") or ""):
        errors.append("asset selection coverage_hash does not match candidate batch")
    if expected_coverage_hash and coverage_hash != expected_coverage_hash:
        errors.append("asset selection coverage_hash is stale")
    if review.get("candidate_batch_hash") != candidates_payload.get("artifact_hash"):
        errors.append("asset selection candidate_batch_hash is stale")
    by_id = {
        str(item.get("candidate_id")): item
        for item in candidates_payload.get("candidates") or []
        if isinstance(item, Mapping)
    }
    required = set(str(value) for value in candidates_payload.get("stock_slot_ids") or [])
    entitlement = review.get("entitlement_snapshot")
    if not isinstance(entitlement, Mapping):
        entitlement = candidates_payload.get("entitlement_snapshot")
    if not isinstance(entitlement, Mapping):
        entitlement = {}
    selected_slots: set[str] = set()
    remote_selection_count = 0
    selections = review.get("selections")
    if not isinstance(selections, list):
        return [*errors, "asset selection selections must be an array"]
    for index, item in enumerate(selections):
        if not isinstance(item, Mapping):
            errors.append(f"selections[{index}] must be an object")
            continue
        slot_id = str(item.get("slot_id") or "")
        candidate_id = str(item.get("candidate_id") or "")
        if not slot_id or slot_id in selected_slots:
            errors.append(f"selections[{index}].slot_id must be unique")
        selected_slots.add(slot_id)
        candidate = by_id.get(candidate_id)
        if candidate is None or str(candidate.get("slot_id")) != slot_id:
            errors.append(f"{slot_id or index} selects an unknown candidate")
            continue
        estimated = candidate.get("estimated_cost_usd")
        approved_cost = item.get("approved_cost_usd")
        if estimated is None and entitlement.get("downloads_included") is True:
            estimated = 0.0
        if estimated is None:
            errors.append(f"{candidate_id} has unknown cost and cannot be approved")
        elif approved_cost is None or float(approved_cost) + 1e-9 < float(estimated):
            errors.append(f"{candidate_id} exceeds its approved cost")
        if candidate.get("provider") == "magnific":
            remote_selection_count += 1
            if not candidate.get("license_type") or not candidate.get("license_url"):
                errors.append(f"{candidate_id} has incomplete license evidence")
            attribution_required = (
                str(entitlement.get("account_plan") or "").casefold()
                in {"free", "essential"}
                if entitlement
                else candidate.get("attribution_required") is True
            )
            if attribution_required and not str(
                candidate.get("attribution") or ""
            ).strip():
                errors.append(f"{candidate_id} requires attribution")
    if remote_selection_count:
        if not isinstance(entitlement, Mapping):
            errors.append("remote selections require an entitlement snapshot")
        else:
            daily_limit = int(entitlement.get("daily_download_limit") or 0)
            if entitlement.get("downloads_included") is not True:
                errors.append("remote selections require verified included downloads")
            if daily_limit <= 0:
                errors.append("remote selections require a positive daily download limit")
            elif remote_selection_count > daily_limit:
                errors.append(
                    f"selection requests {remote_selection_count} downloads; "
                    f"daily limit is {daily_limit}"
                )
    if selected_slots != required:
        missing = sorted(required - selected_slots)
        extra = sorted(selected_slots - required)
        if missing:
            errors.append("asset selection is missing slots: " + ", ".join(missing))
        if extra:
            errors.append("asset selection contains unknown slots: " + ", ".join(extra))
    return errors


def bind_stock_entitlement(
    batch_path: str | Path,
    *,
    job_dir: str | Path,
    account_plan: str,
    downloads_included: bool,
    daily_download_limit: int,
) -> dict[str, Any]:
    """Rebind an unapproved preview batch to operator-confirmed plan terms."""

    root = Path(job_dir).resolve()
    path = _contained(batch_path, root, "stock candidate batch")
    batch = _read_json(path, "stock candidate batch")
    errors = validate_stock_candidate_batch(batch, job_dir=root)
    if errors:
        raise StockAssetError("; ".join(errors))
    if not account_plan.strip() or daily_download_limit <= 0:
        raise StockAssetError("plan and positive daily download limit are required")
    entitlement = {
        "schema_version": "stock_entitlement.v1",
        "account_plan": account_plan.strip().casefold(),
        "downloads_included": bool(downloads_included),
        "daily_download_limit": int(daily_download_limit),
        "confirmed_by": "operator",
    }
    entitlement["artifact_hash"] = canonical_sha256(entitlement)
    _write_json(root / "asset_selection" / "entitlement.json", entitlement)
    review_path = root / "asset_selection" / "review-template.json"
    review = _read_json(review_path, "asset selection review template")
    review["candidate_batch_hash"] = batch["artifact_hash"]
    review["entitlement_snapshot"] = {
        key: value
        for key, value in entitlement.items()
        if key not in {"schema_version", "artifact_hash"}
    }
    review["approved"] = False
    review["reviewed_by"] = ""
    review["reviewed_at"] = ""
    for selection in review.get("selections") or []:
        if isinstance(selection, dict):
            selection["candidate_id"] = ""
            selection["approved_cost_usd"] = 0.0
    _write_json(review_path, review)
    write_asset_review_packet(batch, job_dir=root)
    return entitlement


def validate_provider_reference_registry(
    value: Mapping[str, Any] | str | Path,
) -> list[str]:
    try:
        payload = _read_json(value, "provider reference registry")
    except StockAssetError as exc:
        return [str(exc)]
    errors: list[str] = []
    if payload.get("schema_version") != REFERENCE_REGISTRY_VERSION:
        errors.append(f"reference registry must use {REFERENCE_REGISTRY_VERSION}")
    references = payload.get("references")
    if not isinstance(references, list):
        return [*errors, "reference registry references must be an array"]
    seen: set[str] = set()
    for index, reference in enumerate(references):
        if not isinstance(reference, Mapping):
            errors.append(f"references[{index}] must be an object")
            continue
        identifier = str(reference.get("id") or "")
        if not identifier or identifier in seen:
            errors.append(f"references[{index}].id must be unique")
        seen.add(identifier)
        if reference.get("kind") not in REFERENCE_KINDS:
            errors.append(f"{identifier or index} has invalid reference kind")
        hashes = reference.get("input_hashes")
        if not isinstance(hashes, list) or not hashes:
            errors.append(f"{identifier or index} requires input_hashes")
        elif any(
            not isinstance(item, str)
            or len(item) != 64
            or any(char not in "0123456789abcdef" for char in item.casefold())
            for item in hashes
        ):
            errors.append(f"{identifier or index} has invalid input hashes")
        if reference.get("rights_reviewed") is not True:
            errors.append(f"{identifier or index} inputs require rights review")
        if reference.get("render_eligible") is not False:
            errors.append(f"{identifier or index} provider reference is not a render asset")
    return errors


def validate_flow_snapshot(value: Mapping[str, Any] | str | Path) -> list[str]:
    try:
        payload = _read_json(value, "provider flow snapshot")
    except StockAssetError as exc:
        return [str(exc)]
    errors: list[str] = []
    if payload.get("schema_version") != FLOW_SNAPSHOT_VERSION:
        errors.append(f"flow snapshot must use {FLOW_SNAPSHOT_VERSION}")
    if not payload.get("flow_id") or not payload.get("flow_version"):
        errors.append("flow snapshot requires flow_id and flow_version")
    if payload.get("evaluator_required") is not True:
        errors.append("flow snapshot must require an evaluator")
    cost = payload.get("cost_ceiling_usd")
    if not isinstance(cost, (int, float)) or float(cost) < 0:
        errors.append("flow snapshot requires a non-negative cost ceiling")
    if payload.get("can_approve_assets") is not False:
        errors.append("provider flows cannot approve assets")
    if payload.get("can_establish_facts") is not False:
        errors.append("provider flows cannot establish facts")
    return errors


class EditorialCoverageStage:
    def run_stage(self, job: VideoRun, ctx: StageContext) -> StageOutput:
        shot_plan = _read_json(ctx.job_dir / "shot_plan.json", "shot plan")
        coverage = compile_editorial_coverage(shot_plan)
        _write_json(ctx.job_dir / "editorial_coverage.json", coverage)
        art_bible = {}
        art_bible_path = ctx.job_dir / "art_bible.json"
        if art_bible_path.is_file():
            art_bible = _read_json(art_bible_path, "art bible")
        art_bible_hash = str(
            art_bible.get("artifact_hash")
            or canonical_sha256(art_bible)
            if art_bible
            else job.config_snapshot.get("art_bible_hash") or ""
        )
        character_pack_id = str(job.config_snapshot.get("character_pack_id") or "")
        character_pack_path = str(
            job.config_snapshot.get("character_pack_path") or ""
        )
        if character_pack_id:
            from content.video_engine.src.services.flow_character_pack import (
                FlowCharacterPackError,
                validate_flow_character_pack,
            )

            project_root = Path(
                ctx.configs.get("project_root") or Path.cwd()
            ).resolve()
            candidate = Path(character_pack_path)
            if not candidate.is_absolute():
                candidate = project_root / candidate
            try:
                candidate = candidate.resolve(strict=True)
                candidate.relative_to(project_root)
            except (OSError, RuntimeError, ValueError) as exc:
                raise StockAssetError(
                    "configured character pack path must stay inside project_root"
                ) from exc
            try:
                validate_flow_character_pack(
                    candidate,
                    expected_art_bible_hash=art_bible_hash or None,
                    expected_id=character_pack_id,
                )
            except FlowCharacterPackError as exc:
                raise StockAssetError(
                    "configured character pack failed validation: "
                    + "; ".join(exc.errors)
                ) from exc
        producer_plan = compile_producer_plan(
            coverage,
            art_bible_id=str(job.config_snapshot.get("art_bible_id") or art_bible.get("id") or ""),
            art_bible_hash=art_bible_hash,
            character_pack_id=character_pack_id,
            style_descriptor={
                "style_atom_ids": [
                    str(atom.get("id"))
                    for atom in art_bible.get("style_atoms") or []
                    if isinstance(atom, Mapping) and atom.get("id")
                ],
                "style_signature": list(art_bible.get("signature") or []),
                "visual_language": str(
                    art_bible.get("visual_language")
                    or "internal art-bible style atoms, palette roles, and composition rules"
                ),
            },
        )
        producer_errors = validate_producer_plan(
            producer_plan,
            expected_art_bible_hash=art_bible_hash or None,
            expected_coverage_hash=str(coverage["artifact_hash"]),
        )
        if producer_errors:
            raise StockAssetError("producer plan failed: " + "; ".join(producer_errors))
        _write_json(ctx.job_dir / "producer_plan.json", producer_plan)
        return StageOutput(
            {
                "artifact_path": "editorial_coverage.json",
                "coverage_hash": coverage["artifact_hash"],
                "slot_count": coverage["slot_count"],
                "producer_plan_path": "producer_plan.json",
                "producer_plan_hash": producer_plan["artifact_hash"],
                "producer_block_count": producer_plan["block_count"],
                "cost_usd": 0.0,
            }
        )


class StockCandidateStage:
    def run_stage(self, job: VideoRun, ctx: StageContext) -> StageOutput:
        del job
        live_search = bool(ctx.configs.get("stock_search_live"))
        settings = MagnificStockSettings.from_environment() if live_search else None
        batch = StockCandidateService(settings=settings).build_batch(
            ctx.job_dir / "editorial_coverage.json",
            job_dir=ctx.job_dir,
            live_search=live_search,
            candidates_per_slot=int(ctx.configs.get("stock_candidates_per_slot") or 3),
        )
        return StageOutput(
            {
                "artifact_path": "asset_selection/stock-candidates.json",
                "contact_sheet_path": "asset_selection/contact-sheet.png",
                "review_template_path": "asset_selection/review-template.json",
                "review_packet_path": "asset_selection/review-packet.md",
                "candidate_batch_hash": batch["artifact_hash"],
                "candidate_count": batch["candidate_count"],
                "stock_slot_count": len(batch["stock_slot_ids"]),
                "provider_calls": int(batch.get("search_call_count") or 0),
                "preview_download_count": int(
                    batch.get("preview_download_count") or 0
                ),
                "cost_usd": 0.0,
            }
        )


class AssetSelectionReviewStage:
    def run_stage(self, job: VideoRun, ctx: StageContext) -> StageOutput:
        del job
        root = ctx.job_dir / "asset_selection"
        batch_path = root / "stock-candidates.json"
        contact_path = root / "contact-sheet.png"
        review_path = root / "review-template.json"
        batch = _read_json(batch_path, "stock candidate batch")
        errors = validate_stock_candidate_batch(batch, job_dir=ctx.job_dir)
        if errors:
            raise StockAssetError("; ".join(errors))
        for required in (contact_path, review_path):
            if not required.is_file():
                raise StockAssetError(
                    f"asset review packet is missing {required.name}"
                )
        return StageOutput(
            {
                "candidate_batch_hash": batch["artifact_hash"],
                "contact_sheet_path": "asset_selection/contact-sheet.png",
                "review_template_path": "asset_selection/review-template.json",
                "cost_usd": 0.0,
            }
        )


def _download_href(payload: Mapping[str, Any]) -> str:
    for key in ("url", "download_url", "downloadUrl", "href"):
        value = payload.get(key)
        if isinstance(value, str) and value:
            return value
    file_record = payload.get("file")
    if isinstance(file_record, Mapping):
        return _download_href(file_record)
    raise StockAssetError("Magnific download response contains no download URL")


class AssetPromotionStage:
    """Promote only operator-selected candidates into a resolved asset domain."""

    def run_stage(self, job: VideoRun, ctx: StageContext) -> StageOutput:
        from content.video_engine.src.services.asset_resolver import (
            AssetResolverService,
        )

        root = ctx.job_dir
        selection_root = root / "asset_selection"
        coverage = _read_json(root / "editorial_coverage.json", "editorial coverage")
        batch = _read_json(
            selection_root / "stock-candidates.json", "stock candidate batch"
        )
        review = _read_json(
            selection_root / "approved-review.json", "approved asset selection"
        )
        errors = validate_asset_selection(
            review,
            batch,
            expected_coverage_hash=str(coverage.get("artifact_hash") or ""),
        )
        if errors:
            raise StockAssetError("; ".join(errors))

        original_manifest = _read_json(root / "asset_manifest.json", "asset manifest")
        promoted_assets = list(original_manifest.get("assets") or [])
        candidates = {
            str(item["candidate_id"]): item
            for item in batch.get("candidates") or []
            if isinstance(item, Mapping)
        }
        selections = {
            str(item["slot_id"]): item
            for item in review.get("selections") or []
            if isinstance(item, Mapping)
        }
        transport: MagnificStockTransport | None = None
        downloaded = 0
        review_entitlement = (
            dict(review.get("entitlement_snapshot"))
            if isinstance(review.get("entitlement_snapshot"), Mapping)
            else {}
        )
        selected_slots: list[dict[str, Any]] = []
        assets_dir = selection_root / "assets"
        assets_dir.mkdir(parents=True, exist_ok=True)

        for slot in coverage.get("slots") or []:
            current = copy.deepcopy(dict(slot))
            selected = selections.get(str(slot.get("slot_id")))
            if selected is None:
                current["selected_visual_source"] = current.get(
                    "preferred_visual_source"
                )
                current["selected_asset_ids"] = list(current.get("asset_ids") or [])
                selected_slots.append(current)
                continue
            candidate = candidates[str(selected["candidate_id"])]
            current["selected_candidate_id"] = candidate["candidate_id"]
            if candidate.get("provider") == "local":
                current["selected_visual_source"] = current[
                    "fallback_visual_source"
                ]
                current["selected_asset_ids"] = list(current.get("asset_ids") or [])
                selected_slots.append(current)
                continue

            if transport is None:
                settings = MagnificStockSettings.from_environment()
                transport = MagnificStockHttpTransport(settings)
            response = transport.download_url(
                str(candidate["resource_id"]),
                str(candidate.get("download_format") or "jpg"),
            )
            data, content_type = transport.download_bytes(
                _download_href(response),
                maximum=MAX_ASSET_BYTES,
            )
            suffix = _image_extension(data, content_type)
            asset_id = (
                "magnific-"
                + re.sub(
                    r"[^a-z0-9._-]+",
                    "-",
                    str(candidate["candidate_id"]).casefold(),
                ).strip("-")
            )
            asset_path = assets_dir / f"{asset_id}{suffix}"
            asset_path.write_bytes(data)
            promoted_assets.append(
                {
                    "id": asset_id,
                    "path": asset_path.relative_to(root).as_posix(),
                    "sha256": _sha256(asset_path),
                    "kind": "vector"
                    if candidate.get("media_type") == "vector"
                    else "photo",
                    "role": "editorial_cut_in",
                    "origin": "Magnific stock resource",
                    "title": candidate.get("title"),
                    "creator": candidate.get("creator"),
                    "source_url": candidate.get("canonical_url"),
                    "rights": {
                        "permission": "licensed",
                        "reviewed": True,
                        "reviewed_by": review.get("reviewed_by"),
                        "reviewed_at": review.get("reviewed_at"),
                        "source": "Magnific stock",
                        "source_url": candidate.get("canonical_url"),
                        "license": candidate.get("license_type"),
                        "attribution_required": (
                            str(
                                review_entitlement.get("account_plan") or ""
                            ).casefold()
                            in {"free", "essential"}
                            if review_entitlement
                            else bool(candidate.get("attribution_required"))
                        ),
                        "attribution": candidate.get("attribution") or None,
                    },
                    "alteration_policy": {
                        "allowed": bool(candidate.get("alteration_allowed"))
                    },
                    "render_eligible": True,
                }
            )
            current["selected_visual_source"] = (
                "stock_vector"
                if candidate.get("media_type") == "vector"
                else "stock_photo"
            )
            current["selected_asset_ids"] = [
                *list(current.get("asset_ids") or []),
                asset_id,
            ]
            selected_slots.append(current)
            downloaded += 1

        combined_core = {
            "schema_version": "asset_manifest.v1",
            "manifest_id": f"{job.id}-v4-1-assets",
            "job_id": job.id,
            "review": {
                "asset_selection_hash": canonical_sha256(review),
                "candidate_batch_hash": batch["artifact_hash"],
                "entitlement": review_entitlement,
            },
            "assets": promoted_assets,
        }
        # Resolver normalization is the specification of record for manifest
        # hashing, so do not predeclare a hash over the unnormalized input.
        combined = combined_core
        manifest_path = selection_root / "asset_manifest.v4_1.json"
        _write_json(manifest_path, combined)
        resolved_dir = selection_root / "resolved"
        result = AssetResolverService().resolve(
            combined,
            project_root=Path(
                ctx.configs.get("project_root") or root
            ),
            job_dir=root,
            output_dir=resolved_dir,
            job_id=job.id,
        )
        selected_core = {
            **{
                key: value
                for key, value in coverage.items()
                if key not in {"slots", "artifact_hash"}
            },
            "asset_selection_hash": canonical_sha256(review),
            "asset_manifest_hash": result["manifest_hash"],
            "slots": selected_slots,
        }
        selected_coverage = {
            **selected_core,
            "artifact_hash": canonical_sha256(selected_core),
        }
        _write_json(root / "editorial_coverage.selected.json", selected_coverage)
        return StageOutput(
            {
                "artifact_path": "editorial_coverage.selected.json",
                "resolved_assets_path": result["resolved_assets_path"],
                "credits_path": result["credits_path"],
                "coverage_hash": coverage["artifact_hash"],
                "asset_selection_hash": canonical_sha256(review),
                "asset_manifest_hash": result["manifest_hash"],
                "downloaded_asset_count": downloaded,
                "cost_usd": 0.0,
            }
        )


class AssetSelectionGateGuard:
    def validate(
        self,
        job_dir: str | Path,
        rubric: str | Path,
        expected_coverage_hash: str,
    ) -> list[str]:
        root = Path(job_dir)
        return validate_asset_selection(
            rubric,
            root / "asset_selection" / "stock-candidates.json",
            expected_coverage_hash=expected_coverage_hash,
        )


__all__ = [
    "ASSET_SELECTION_VERSION",
    "FLOW_SNAPSHOT_VERSION",
    "REFERENCE_REGISTRY_VERSION",
    "STOCK_BATCH_VERSION",
    "AssetSelectionGateGuard",
    "AssetSelectionReviewStage",
    "AssetPromotionStage",
    "EditorialCoverageStage",
    "MagnificStockHttpTransport",
    "MagnificStockSettings",
    "StockAssetError",
    "StockCandidateService",
    "StockCandidateStage",
    "score_stock_candidate",
    "validate_asset_selection",
    "bind_stock_entitlement",
    "validate_flow_snapshot",
    "validate_provider_reference_registry",
    "validate_stock_candidate_batch",
    "write_asset_review_packet",
]
