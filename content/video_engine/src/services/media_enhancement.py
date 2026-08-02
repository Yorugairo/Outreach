"""Reviewed-media enhancement with a bounded Magnific adapter.

The feasibility slice supports image style transfer and Flux 2 Pro because
their published prices permit conservative preflight cost ceilings. It does
not treat raw prompts as the production workflow: custom references, Spaces
flows, Designer templates, and stock intake require separate reviewed
provenance contracts. Every output remains a non-renderable candidate until
an operator promotes its local hash through the asset manifest.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import shutil
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Protocol
from urllib.parse import urljoin, urlparse


PLAN_VERSION = "media_enhancement_plan.v1"
MANIFEST_VERSION = "media_enhancement_manifest.v1"
MAGNIFIC_PROVIDER = "magnific"
STYLE_TRANSFER_OPERATION = "image_style_transfer"
FLUX_2_PRO_OPERATION = "flux_2_pro"
DEFAULT_MAGNIFIC_BASE_URL = "https://api.magnific.com"
# Magnific publishes €0.10 per style-transfer operation.  The deliberately
# higher USD ceiling absorbs exchange-rate movement and billing variance.
STYLE_TRANSFER_COST_CEILING_USD = 0.15
# Public API pricing lists Flux 2 Pro at $0.036 per generation.  This ceiling is
# intentionally almost 3x higher and the adapter limits output to 1344x768.
FLUX_2_PRO_COST_CEILING_USD = 0.10
MAX_DOWNLOAD_BYTES = 50 * 1024 * 1024
PROHIBITED_PROMPT_TERMS = (
    "in the style of",
    "youtube reference pack",
    "consultant outline",
    "creator_name",
    "source_frame",
)


class MediaEnhancementError(RuntimeError):
    """A configuration, contract, provider, or artifact failure."""


class MagnificTransport(Protocol):
    """Small injectable boundary used by the real client and focused tests."""

    def create_style_transfer(self, payload: Mapping[str, Any]) -> Mapping[str, Any]:
        ...

    def get_style_transfer(self, task_id: str) -> Mapping[str, Any]:
        ...

    def create_flux_2_pro(self, payload: Mapping[str, Any]) -> Mapping[str, Any]:
        ...

    def get_flux_2_pro(self, task_id: str) -> Mapping[str, Any]:
        ...

    def download(self, url: str) -> bytes:
        ...


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _canonical_bytes(payload: Any) -> bytes:
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _contained_path(value: str | Path, root: Path, label: str) -> Path:
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = root / candidate
    resolved = candidate.resolve()
    approved_root = root.resolve()
    try:
        resolved.relative_to(approved_root)
    except ValueError as exc:
        raise MediaEnhancementError(
            f"{label} escapes the approved project root: {value}"
        ) from exc
    return resolved


def _image_base64(path: Path) -> str:
    suffix = path.suffix.casefold()
    if suffix not in {".png", ".jpg", ".jpeg", ".webp"}:
        raise MediaEnhancementError(
            f"Magnific style-transfer input must be PNG, JPEG, or WebP: {path}"
        )
    return base64.b64encode(path.read_bytes()).decode("ascii")


def _image_extension(value: bytes) -> str:
    if value.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png"
    if value.startswith(b"\xff\xd8\xff"):
        return ".jpg"
    if len(value) >= 12 and value[:4] == b"RIFF" and value[8:12] == b"WEBP":
        return ".webp"
    raise MediaEnhancementError(
        "Magnific generated asset has an unsupported image signature"
    )


def _response_data(payload: Mapping[str, Any], label: str) -> Mapping[str, Any]:
    data = payload.get("data", payload)
    if not isinstance(data, Mapping):
        raise MediaEnhancementError(f"{label} returned no object data")
    return data


def _task_status(data: Mapping[str, Any]) -> str:
    return str(data.get("status") or data.get("task_status") or "").upper()


def _task_id(data: Mapping[str, Any]) -> str:
    return str(data.get("task_id") or "").strip()


@dataclass(frozen=True, slots=True)
class MagnificSettings:
    api_key: str
    max_cost_usd: float
    max_calls: int
    paid_calls_allowed: bool
    base_url: str = DEFAULT_MAGNIFIC_BASE_URL
    timeout_s: float = 60.0
    poll_interval_s: float = 2.0
    max_poll_s: float = 180.0
    style_transfer_cost_ceiling_usd: float = STYLE_TRANSFER_COST_CEILING_USD
    flux_2_pro_cost_ceiling_usd: float = FLUX_2_PRO_COST_CEILING_USD

    @classmethod
    def from_environment(
        cls,
        *,
        max_cost_usd: float,
        max_calls: int,
        paid_calls_allowed: bool,
    ) -> "MagnificSettings":
        api_key = (os.environ.get("MAGNIFIC_API_KEY") or "").strip()
        if not api_key:
            raise MediaEnhancementError(
                "MAGNIFIC_API_KEY is required; load it from a local ignored env file"
            )
        if not paid_calls_allowed:
            raise MediaEnhancementError(
                "Magnific paid calls require the explicit --allow-paid flag"
            )
        if max_cost_usd <= 0:
            raise MediaEnhancementError("Magnific max_cost_usd must be positive")
        if max_calls < 1:
            raise MediaEnhancementError("Magnific max_calls must be positive")
        return cls(
            api_key=api_key,
            max_cost_usd=float(max_cost_usd),
            max_calls=int(max_calls),
            paid_calls_allowed=True,
            base_url=(
                os.environ.get("MAGNIFIC_BASE_URL", DEFAULT_MAGNIFIC_BASE_URL)
                or DEFAULT_MAGNIFIC_BASE_URL
            ).rstrip("/"),
            timeout_s=float(os.environ.get("MAGNIFIC_TIMEOUT_S", "60")),
            poll_interval_s=float(
                os.environ.get("MAGNIFIC_POLL_INTERVAL_S", "2")
            ),
            max_poll_s=float(os.environ.get("MAGNIFIC_MAX_POLL_S", "180")),
            style_transfer_cost_ceiling_usd=float(
                os.environ.get(
                    "MAGNIFIC_STYLE_TRANSFER_COST_CEILING_USD",
                    str(STYLE_TRANSFER_COST_CEILING_USD),
                )
            ),
            flux_2_pro_cost_ceiling_usd=float(
                os.environ.get(
                    "MAGNIFIC_FLUX_2_PRO_COST_CEILING_USD",
                    str(FLUX_2_PRO_COST_CEILING_USD),
                )
            ),
        )

    def redacted(self) -> dict[str, Any]:
        return {
            "provider": MAGNIFIC_PROVIDER,
            "base_url": self.base_url,
            "max_cost_usd": self.max_cost_usd,
            "max_calls": self.max_calls,
            "paid_calls_allowed": self.paid_calls_allowed,
            "style_transfer_cost_ceiling_usd": (
                self.style_transfer_cost_ceiling_usd
            ),
            "flux_2_pro_cost_ceiling_usd": self.flux_2_pro_cost_ceiling_usd,
        }


class MagnificHttpTransport:
    """Minimal urllib implementation that never persists the API key."""

    def __init__(self, settings: MagnificSettings) -> None:
        self.settings = settings

    def _json_request(
        self,
        method: str,
        path: str,
        payload: Mapping[str, Any] | None = None,
    ) -> Mapping[str, Any]:
        body = _canonical_bytes(payload) if payload is not None else None
        request = urllib.request.Request(
            urljoin(f"{self.settings.base_url}/", path.lstrip("/")),
            data=body,
            method=method,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "x-magnific-api-key": self.settings.api_key,
            },
        )
        try:
            with urllib.request.urlopen(
                request,
                timeout=self.settings.timeout_s,
            ) as response:
                raw = response.read()
        except urllib.error.HTTPError as exc:
            # Provider bodies can contain request details.  Return only the
            # status code at this boundary so credentials/prompts cannot leak.
            raise MediaEnhancementError(
                f"Magnific request failed with HTTP {exc.code}"
            ) from exc
        except urllib.error.URLError as exc:
            raise MediaEnhancementError("Magnific request failed") from exc
        try:
            decoded = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise MediaEnhancementError(
                "Magnific returned invalid JSON"
            ) from exc
        if not isinstance(decoded, Mapping):
            raise MediaEnhancementError("Magnific returned a non-object response")
        return decoded

    def create_style_transfer(self, payload: Mapping[str, Any]) -> Mapping[str, Any]:
        return self._json_request(
            "POST",
            "/v1/ai/image-style-transfer",
            payload,
        )

    def get_style_transfer(self, task_id: str) -> Mapping[str, Any]:
        return self._json_request(
            "GET",
            f"/v1/ai/image-style-transfer/{task_id}",
        )

    def create_flux_2_pro(self, payload: Mapping[str, Any]) -> Mapping[str, Any]:
        return self._json_request(
            "POST",
            "/v1/ai/text-to-image/flux-2-pro",
            payload,
        )

    def get_flux_2_pro(self, task_id: str) -> Mapping[str, Any]:
        return self._json_request(
            "GET",
            f"/v1/ai/text-to-image/flux-2-pro/{task_id}",
        )

    def download(self, url: str) -> bytes:
        parsed = urlparse(url)
        if parsed.scheme != "https" or not parsed.netloc:
            raise MediaEnhancementError(
                "Magnific generated asset URL must use HTTPS"
            )
        request = urllib.request.Request(url, headers={"Accept": "image/*"})
        try:
            with urllib.request.urlopen(
                request,
                timeout=self.settings.timeout_s,
            ) as response:
                content_type = str(response.headers.get("Content-Type") or "")
                if not content_type.casefold().startswith("image/"):
                    raise MediaEnhancementError(
                        "Magnific generated asset is not an image"
                    )
                raw = response.read(MAX_DOWNLOAD_BYTES + 1)
        except urllib.error.URLError as exc:
            raise MediaEnhancementError(
                "Magnific generated asset download failed"
            ) from exc
        if len(raw) > MAX_DOWNLOAD_BYTES:
            raise MediaEnhancementError(
                "Magnific generated asset exceeds the download limit"
            )
        return raw


def validate_media_enhancement_plan(
    payload: Mapping[str, Any],
    *,
    project_root: str | Path,
) -> list[dict[str, Any]]:
    if payload.get("schema_version") != PLAN_VERSION:
        raise MediaEnhancementError(
            f"media enhancement plan must use {PLAN_VERSION}"
        )
    if payload.get("provider") != MAGNIFIC_PROVIDER:
        raise MediaEnhancementError("media enhancement provider must be magnific")
    operation = str(payload.get("operation") or "")
    if operation not in {STYLE_TRANSFER_OPERATION, FLUX_2_PRO_OPERATION}:
        raise MediaEnhancementError(
            "media enhancement operation must be image_style_transfer or flux_2_pro"
        )
    raw_items = payload.get("items")
    if not isinstance(raw_items, list) or not raw_items:
        raise MediaEnhancementError("media enhancement plan requires items")

    root = Path(project_root).resolve()
    seen: set[str] = set()
    validated: list[dict[str, Any]] = []
    for index, raw_item in enumerate(raw_items):
        if not isinstance(raw_item, Mapping):
            raise MediaEnhancementError(f"plan item {index} must be an object")
        item_id = str(raw_item.get("id") or "").strip()
        if not item_id or item_id in seen:
            raise MediaEnhancementError(
                f"plan item {index} requires a unique non-empty id"
            )
        seen.add(item_id)
        source = _contained_path(
            str(raw_item.get("source_path") or ""),
            root,
            f"{item_id} source_path",
        )
        reference = _contained_path(
            str(raw_item.get("reference_path") or ""),
            root,
            f"{item_id} reference_path",
        )
        for label, path, expected in (
            ("source", source, raw_item.get("source_sha256")),
            ("reference", reference, raw_item.get("reference_sha256")),
        ):
            if not path.is_file():
                raise MediaEnhancementError(
                    f"{item_id} {label} file does not exist: {path}"
                )
            actual = _sha256_file(path)
            if str(expected or "").casefold() != actual:
                raise MediaEnhancementError(
                    f"{item_id} {label} hash is stale"
                )
        prompt = str(raw_item.get("prompt") or "").strip()
        if not prompt:
            raise MediaEnhancementError(f"{item_id} prompt is required")
        lowered = prompt.casefold()
        for term in PROHIBITED_PROMPT_TERMS:
            if term in lowered:
                raise MediaEnhancementError(
                    f"{item_id} prompt contains prohibited renderer input {term!r}"
                )
        params = dict(raw_item.get("parameters") or {})
        if operation == STYLE_TRANSFER_OPERATION:
            style_strength = int(params.get("style_strength", 35))
            structure_strength = int(params.get("structure_strength", 85))
            if not 0 <= style_strength <= 100:
                raise MediaEnhancementError(
                    f"{item_id} style_strength must be between 0 and 100"
                )
            if not 0 <= structure_strength <= 100:
                raise MediaEnhancementError(
                    f"{item_id} structure_strength must be between 0 and 100"
                )
            normalized_params = {
                "style_strength": style_strength,
                "structure_strength": structure_strength,
                "flavor": str(params.get("flavor") or "faithful"),
                "engine": str(params.get("engine") or "illusio"),
                "fixed_generation": bool(
                    params.get("fixed_generation", True)
                ),
                "is_portrait": bool(params.get("is_portrait", False)),
            }
        else:
            width = int(params.get("width", 1344))
            height = int(params.get("height", 768))
            if not 256 <= width <= 1440 or not 256 <= height <= 1440:
                raise MediaEnhancementError(
                    f"{item_id} Flux 2 Pro dimensions must be 256-1440px"
                )
            if width * height > 1_100_000:
                raise MediaEnhancementError(
                    f"{item_id} Flux 2 Pro output exceeds the 1.1MP test limit"
                )
            seed = int(params.get("seed", 1882))
            if not 0 <= seed <= 4_294_967_295:
                raise MediaEnhancementError(
                    f"{item_id} Flux 2 Pro seed is out of range"
                )
            normalized_params = {
                "width": width,
                "height": height,
                "seed": seed,
                "prompt_upsampling": False,
            }
        validated.append(
            {
                "id": item_id,
                "source": source,
                "reference": reference,
                "source_sha256": _sha256_file(source),
                "reference_sha256": _sha256_file(reference),
                "prompt": prompt,
                "parameters": normalized_params,
            }
        )
    return validated


class MediaEnhancementService:
    """Execute a reviewed plan with content-addressed caching and a hard cap."""

    def __init__(
        self,
        settings: MagnificSettings,
        *,
        transport: MagnificTransport | None = None,
        sleep_fn: Any = time.sleep,
        monotonic_fn: Any = time.monotonic,
    ) -> None:
        self.settings = settings
        self.transport = transport or MagnificHttpTransport(settings)
        self.sleep_fn = sleep_fn
        self.monotonic_fn = monotonic_fn

    def _poll(self, task_id: str, operation: str) -> Mapping[str, Any]:
        deadline = self.monotonic_fn() + self.settings.max_poll_s
        while True:
            response = (
                self.transport.get_style_transfer(task_id)
                if operation == STYLE_TRANSFER_OPERATION
                else self.transport.get_flux_2_pro(task_id)
            )
            data = _response_data(
                response,
                "Magnific task status",
            )
            status = _task_status(data)
            if status == "COMPLETED":
                return data
            if status == "FAILED":
                raise MediaEnhancementError(
                    f"Magnific style-transfer task {task_id} failed"
                )
            if status not in {"CREATED", "IN_PROGRESS"}:
                raise MediaEnhancementError(
                    f"Magnific style-transfer task {task_id} has unknown status"
                )
            if self.monotonic_fn() >= deadline:
                raise MediaEnhancementError(
                    f"Magnific style-transfer task {task_id} timed out"
                )
            self.sleep_fn(self.settings.poll_interval_s)

    def execute(
        self,
        plan: Mapping[str, Any] | str | Path,
        *,
        project_root: str | Path,
        output_dir: str | Path,
    ) -> dict[str, Any]:
        if isinstance(plan, Mapping):
            payload = dict(plan)
        else:
            try:
                payload = json.loads(Path(plan).read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                raise MediaEnhancementError(
                    f"media enhancement plan could not be read: {exc}"
                ) from exc
        if not isinstance(payload, Mapping):
            raise MediaEnhancementError(
                "media enhancement plan must be an object"
            )
        items = validate_media_enhancement_plan(
            payload,
            project_root=project_root,
        )
        if len(items) > self.settings.max_calls:
            raise MediaEnhancementError(
                f"plan requires {len(items)} calls but max_calls is "
                f"{self.settings.max_calls}"
            )
        operation = str(payload["operation"])
        cost_per_call = (
            self.settings.style_transfer_cost_ceiling_usd
            if operation == STYLE_TRANSFER_OPERATION
            else self.settings.flux_2_pro_cost_ceiling_usd
        )
        projected_cost = len(items) * cost_per_call
        if projected_cost > self.settings.max_cost_usd + 1e-9:
            raise MediaEnhancementError(
                f"projected cost ${projected_cost:.2f} exceeds approved "
                f"ceiling ${self.settings.max_cost_usd:.2f}"
            )

        root = Path(project_root).resolve()
        output = _contained_path(output_dir, root, "output_dir")
        output.mkdir(parents=True, exist_ok=True)
        cache_dir = output / ".cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        manifest_items: list[dict[str, Any]] = []
        provider_calls = 0

        for item in items:
            request_contract = {
                "provider": MAGNIFIC_PROVIDER,
                "operation": operation,
                "source_sha256": item["source_sha256"],
                "reference_sha256": item["reference_sha256"],
                "prompt": item["prompt"],
                "parameters": item["parameters"],
            }
            request_hash = _sha256_bytes(_canonical_bytes(request_contract))
            cached_candidates = [
                cache_dir / f"{request_hash}{suffix}"
                for suffix in (".png", ".jpg", ".webp")
            ]
            cache_path = next(
                (
                    candidate
                    for candidate in cached_candidates
                    if candidate.is_file() and candidate.stat().st_size > 0
                ),
                None,
            )
            cache_hit = cache_path is not None
            task_id = ""
            if cache_hit:
                assert cache_path is not None
                target_path = output / f"{item['id']}{cache_path.suffix}"
                shutil.copyfile(cache_path, target_path)
            else:
                if (
                    (provider_calls + 1)
                    * cost_per_call
                    > self.settings.max_cost_usd + 1e-9
                ):
                    raise MediaEnhancementError(
                        "Magnific cost ceiling reached before the next call"
                    )
                provider_payload = {"prompt": item["prompt"], **item["parameters"]}
                if operation == STYLE_TRANSFER_OPERATION:
                    provider_payload.update(
                        {
                            "image": _image_base64(item["source"]),
                            "reference_image": _image_base64(item["reference"]),
                        }
                    )
                    response = self.transport.create_style_transfer(
                        provider_payload
                    )
                else:
                    provider_payload.update(
                        {
                            "input_image": _image_base64(item["source"]),
                            "input_image_2": _image_base64(item["reference"]),
                        }
                    )
                    response = self.transport.create_flux_2_pro(provider_payload)
                created = _response_data(
                    response,
                    "Magnific create task",
                )
                task_id = _task_id(created)
                if not task_id:
                    raise MediaEnhancementError(
                        "Magnific create task returned no task_id"
                    )
                provider_calls += 1
                completed = (
                    created
                    if _task_status(created) == "COMPLETED"
                    else self._poll(task_id, operation)
                )
                generated = completed.get("generated")
                if (
                    not isinstance(generated, list)
                    or not generated
                    or not isinstance(generated[0], str)
                ):
                    raise MediaEnhancementError(
                        f"Magnific task {task_id} returned no generated image"
                    )
                image_bytes = self.transport.download(generated[0])
                if not image_bytes:
                    raise MediaEnhancementError(
                        f"Magnific task {task_id} returned an empty image"
                    )
                extension = _image_extension(image_bytes)
                cache_path = cache_dir / f"{request_hash}{extension}"
                target_path = output / f"{item['id']}{extension}"
                cache_path.write_bytes(image_bytes)
                target_path.write_bytes(image_bytes)

            manifest_items.append(
                {
                    "id": item["id"],
                    "request_hash": request_hash,
                    "source_sha256": item["source_sha256"],
                    "reference_sha256": item["reference_sha256"],
                    "output_path": target_path.relative_to(output).as_posix(),
                    "output_sha256": _sha256_file(target_path),
                    "cache_hit": cache_hit,
                    "task_id": task_id,
                    "cost_ceiling_usd": (
                        0.0
                        if cache_hit
                        else cost_per_call
                    ),
                    "render_eligible": False,
                    "review_status": "pending",
                    "disclosure_label": "AI-assisted illustration candidate",
                }
            )

        manifest: dict[str, Any] = {
            "schema_version": MANIFEST_VERSION,
            "provider": MAGNIFIC_PROVIDER,
            "operation": operation,
            "approval_ceiling_usd": self.settings.max_cost_usd,
            "cost_ceiling_usd": round(
                provider_calls
                * cost_per_call,
                4,
            ),
            "provider_calls": provider_calls,
            "cache_hits": len(items) - provider_calls,
            "items": manifest_items,
            "provider_settings": self.settings.redacted(),
        }
        manifest["artifact_hash"] = _sha256_bytes(_canonical_bytes(manifest))
        (output / "manifest.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return manifest


__all__ = [
    "DEFAULT_MAGNIFIC_BASE_URL",
    "FLUX_2_PRO_COST_CEILING_USD",
    "FLUX_2_PRO_OPERATION",
    "MAGNIFIC_PROVIDER",
    "MANIFEST_VERSION",
    "MediaEnhancementError",
    "MediaEnhancementService",
    "MagnificHttpTransport",
    "MagnificSettings",
    "PLAN_VERSION",
    "STYLE_TRANSFER_COST_CEILING_USD",
    "STYLE_TRANSFER_OPERATION",
    "validate_media_enhancement_plan",
]
