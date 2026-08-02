"""Bounded Magnific Nano Banana 2 image-generation adapter."""

from __future__ import annotations

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

from .media_enhancement import PROHIBITED_PROMPT_TERMS


PLAN_VERSION = "magnific_image_plan.v1"
MANIFEST_VERSION = "magnific_image_manifest.v1"
MAGNIFIC_PROVIDER = "magnific"
NANO_BANANA_2_MODEL = "nano-banana-pro-flash"
DEFAULT_MAGNIFIC_BASE_URL = "https://api.magnific.com"
MAX_IMAGE_DOWNLOAD_BYTES = 50 * 1024 * 1024
PROMPT_MAX_CHARS = 3000
ASPECT_RATIOS = {
    "1:1",
    "2:3",
    "3:2",
    "4:3",
    "3:4",
    "5:4",
    "4:5",
    "16:9",
    "9:16",
    "21:9",
}
RESOLUTIONS = {"1K", "2K", "4K", "low", "medium", "high"}


class MagnificImageError(RuntimeError):
    """A configuration, contract, provider, or artifact failure."""


class MagnificImageTransport(Protocol):
    def create_nano_banana_2(self, payload: Mapping[str, Any]) -> Mapping[str, Any]:
        ...

    def get_nano_banana_2(self, task_id: str) -> Mapping[str, Any]:
        ...

    def download_image(self, url: str) -> bytes:
        ...


def _canonical_bytes(payload: Any) -> bytes:
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _contained_path(value: str | Path, root: Path, label: str) -> Path:
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = root / candidate
    resolved = candidate.resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError as exc:
        raise MagnificImageError(
            f"{label} escapes the approved project root: {value}"
        ) from exc
    return resolved


def _response_data(payload: Mapping[str, Any], label: str) -> Mapping[str, Any]:
    data = payload.get("data", payload)
    if not isinstance(data, Mapping):
        raise MagnificImageError(f"{label} returned no object data")
    return data


def _task_id(data: Mapping[str, Any]) -> str:
    return str(data.get("task_id") or "").strip()


def _task_status(data: Mapping[str, Any]) -> str:
    return str(data.get("status") or data.get("task_status") or "").upper()


def _image_url(data: Mapping[str, Any]) -> str:
    generated = data.get("generated")
    if isinstance(generated, list) and generated:
        return str(generated[0] or "").strip()
    return str(data.get("image_url") or "").strip()


def _image_extension(value: bytes) -> str:
    if value.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png"
    if value.startswith(b"\xff\xd8\xff"):
        return ".jpg"
    if len(value) >= 12 and value[:4] == b"RIFF" and value[8:12] == b"WEBP":
        return ".webp"
    raise MagnificImageError("Magnific returned an unsupported image signature")


@dataclass(frozen=True, slots=True)
class MagnificImageSettings:
    api_key: str
    max_cost_usd: float
    max_calls: int
    paid_calls_allowed: bool
    base_url: str = DEFAULT_MAGNIFIC_BASE_URL
    timeout_s: float = 60.0
    poll_interval_s: float = 2.0
    max_poll_s: float = 300.0
    cost_ceiling_usd: float = 14.0

    @classmethod
    def from_environment(
        cls,
        *,
        max_cost_usd: float,
        max_calls: int,
        paid_calls_allowed: bool,
    ) -> "MagnificImageSettings":
        api_key = (os.environ.get("MAGNIFIC_API_KEY") or "").strip()
        if not api_key:
            raise MagnificImageError(
                "MAGNIFIC_API_KEY is required; load it from a local ignored env file"
            )
        if not paid_calls_allowed:
            raise MagnificImageError(
                "Magnific image calls require the explicit --allow-paid flag"
            )
        if max_cost_usd <= 0 or max_calls < 1:
            raise MagnificImageError(
                "Magnific image max_cost_usd and max_calls must be positive"
            )
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
            max_poll_s=float(
                os.environ.get("MAGNIFIC_IMAGE_MAX_POLL_S", "300")
            ),
            cost_ceiling_usd=float(
                os.environ.get("MAGNIFIC_IMAGE_COST_CEILING_USD", "14")
            ),
        )

    def redacted(self) -> dict[str, Any]:
        return {
            "provider": MAGNIFIC_PROVIDER,
            "model": NANO_BANANA_2_MODEL,
            "base_url": self.base_url,
            "max_cost_usd": self.max_cost_usd,
            "max_calls": self.max_calls,
            "paid_calls_allowed": self.paid_calls_allowed,
            "cost_ceiling_usd": self.cost_ceiling_usd,
            "pricing_status": "provider_plan_or_api_pricing_not_verified",
        }


class MagnificImageHttpTransport:
    def __init__(self, settings: MagnificImageSettings) -> None:
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
            with urllib.request.urlopen(request, timeout=self.settings.timeout_s) as response:
                raw = response.read()
        except urllib.error.HTTPError as exc:
            raise MagnificImageError(
                f"Magnific image request failed with HTTP {exc.code}"
            ) from exc
        except urllib.error.URLError as exc:
            raise MagnificImageError("Magnific image request failed") from exc
        try:
            decoded = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise MagnificImageError("Magnific image API returned invalid JSON") from exc
        if not isinstance(decoded, Mapping):
            raise MagnificImageError("Magnific image API returned a non-object response")
        return decoded

    def create_nano_banana_2(self, payload: Mapping[str, Any]) -> Mapping[str, Any]:
        return self._json_request(
            "POST",
            f"/v1/ai/text-to-image/{NANO_BANANA_2_MODEL}",
            payload,
        )

    def get_nano_banana_2(self, task_id: str) -> Mapping[str, Any]:
        return self._json_request(
            "GET",
            f"/v1/ai/text-to-image/{NANO_BANANA_2_MODEL}/{task_id}",
        )

    def download_image(self, url: str) -> bytes:
        parsed = urlparse(url)
        if parsed.scheme != "https" or not parsed.netloc:
            raise MagnificImageError("Magnific image URL must use HTTPS")
        request = urllib.request.Request(url, headers={"Accept": "image/*"})
        try:
            with urllib.request.urlopen(request, timeout=self.settings.timeout_s) as response:
                content_type = str(response.headers.get("Content-Type") or "")
                if content_type and not content_type.casefold().startswith("image/"):
                    raise MagnificImageError("Magnific generated asset is not an image")
                raw = response.read(MAX_IMAGE_DOWNLOAD_BYTES + 1)
        except urllib.error.URLError as exc:
            raise MagnificImageError("Magnific generated image download failed") from exc
        if len(raw) > MAX_IMAGE_DOWNLOAD_BYTES:
            raise MagnificImageError("Magnific generated image exceeds the download limit")
        return raw


def validate_magnific_image_plan(
    payload: Mapping[str, Any],
) -> list[dict[str, Any]]:
    if payload.get("schema_version") != PLAN_VERSION:
        raise MagnificImageError(f"image plan must use {PLAN_VERSION}")
    if payload.get("provider") != MAGNIFIC_PROVIDER:
        raise MagnificImageError("image plan provider must be magnific")
    if payload.get("model") != NANO_BANANA_2_MODEL:
        raise MagnificImageError(f"image plan model must be {NANO_BANANA_2_MODEL}")
    raw_items = payload.get("items")
    if not isinstance(raw_items, list) or not raw_items:
        raise MagnificImageError("image plan requires items")
    seen: set[str] = set()
    validated: list[dict[str, Any]] = []
    for index, raw_item in enumerate(raw_items):
        if not isinstance(raw_item, Mapping):
            raise MagnificImageError(f"image plan item {index} must be an object")
        item_id = str(raw_item.get("id") or "").strip()
        if not item_id or item_id in seen:
            raise MagnificImageError(
                f"image plan item {index} requires a unique non-empty id"
            )
        seen.add(item_id)
        prompt = str(raw_item.get("prompt") or "").strip()
        if not 2 <= len(prompt) <= PROMPT_MAX_CHARS:
            raise MagnificImageError(
                f"{item_id} prompt must be 2-{PROMPT_MAX_CHARS} characters"
            )
        lowered = prompt.casefold()
        for term in PROHIBITED_PROMPT_TERMS:
            if term in lowered:
                raise MagnificImageError(
                    f"{item_id} prompt contains prohibited renderer input {term!r}"
                )
        aspect_ratio = str(raw_item.get("aspect_ratio") or "16:9")
        if aspect_ratio not in ASPECT_RATIOS:
            raise MagnificImageError(f"{item_id} aspect_ratio is unsupported")
        resolution = str(raw_item.get("resolution") or "1K")
        if resolution not in RESOLUTIONS:
            raise MagnificImageError(f"{item_id} resolution is unsupported")
        validated.append(
            {
                "id": item_id,
                "prompt": prompt,
                "aspect_ratio": aspect_ratio,
                "resolution": resolution,
                "use_google_search_tool": bool(
                    raw_item.get("use_google_search_tool", False)
                ),
            }
        )
    return validated


class MagnificImageService:
    def __init__(
        self,
        settings: MagnificImageSettings,
        *,
        transport: MagnificImageTransport | None = None,
        sleep_fn: Any = time.sleep,
        monotonic_fn: Any = time.monotonic,
    ) -> None:
        self.settings = settings
        self.transport = transport or MagnificImageHttpTransport(settings)
        self.sleep_fn = sleep_fn
        self.monotonic_fn = monotonic_fn

    def _poll(self, task_id: str) -> Mapping[str, Any]:
        deadline = self.monotonic_fn() + self.settings.max_poll_s
        while True:
            data = _response_data(
                self.transport.get_nano_banana_2(task_id),
                "Magnific image task status",
            )
            status = _task_status(data)
            if status in {"COMPLETED", "SUCCEEDED", "SUCCESS"}:
                return data
            if status in {"FAILED", "ERROR", "CANCELED", "CANCELLED"}:
                raise MagnificImageError(
                    f"Magnific Nano Banana 2 task {task_id} failed with status {status}"
                )
            if status not in {
                "CREATED",
                "QUEUED",
                "PROCESSING",
                "IN_PROGRESS",
                "RUNNING",
            }:
                raise MagnificImageError(
                    f"Magnific Nano Banana 2 task {task_id} has unknown status"
                )
            if self.monotonic_fn() >= deadline:
                raise MagnificImageError(
                    f"Magnific Nano Banana 2 task {task_id} timed out"
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
                raise MagnificImageError(f"image plan could not be read: {exc}") from exc
        if not isinstance(payload, Mapping):
            raise MagnificImageError("image plan must be an object")
        items = validate_magnific_image_plan(payload)
        if len(items) > self.settings.max_calls:
            raise MagnificImageError(
                f"image plan requires {len(items)} calls but max_calls is {self.settings.max_calls}"
            )
        projected_cost = len(items) * self.settings.cost_ceiling_usd
        if projected_cost > self.settings.max_cost_usd + 1e-9:
            raise MagnificImageError(
                f"projected cost ceiling ${projected_cost:.2f} exceeds approved ceiling "
                f"${self.settings.max_cost_usd:.2f}"
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
                "model": NANO_BANANA_2_MODEL,
                "prompt": item["prompt"],
                "aspect_ratio": item["aspect_ratio"],
                "resolution": item["resolution"],
                "use_google_search_tool": item["use_google_search_tool"],
            }
            request_hash = _sha256_bytes(_canonical_bytes(request_contract))
            cache_path = next(
                (
                    candidate
                    for candidate in (
                        cache_dir / f"{request_hash}.png",
                        cache_dir / f"{request_hash}.jpg",
                        cache_dir / f"{request_hash}.webp",
                    )
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
                    (provider_calls + 1) * self.settings.cost_ceiling_usd
                    > self.settings.max_cost_usd + 1e-9
                ):
                    raise MagnificImageError(
                        "Magnific image cost ceiling reached before the next call"
                    )
                response = self.transport.create_nano_banana_2(
                    {
                        "prompt": item["prompt"],
                        "aspect_ratio": item["aspect_ratio"],
                        "resolution": item["resolution"],
                        "use_google_search_tool": item["use_google_search_tool"],
                    }
                )
                created = _response_data(response, "Magnific create image task")
                task_id = _task_id(created)
                if not task_id:
                    raise MagnificImageError(
                        "Magnific create image task returned no task_id"
                    )
                provider_calls += 1
                completed = (
                    created
                    if _image_url(created)
                    and _task_status(created) in {"COMPLETED", "SUCCEEDED", "SUCCESS"}
                    else self._poll(task_id)
                )
                image_url = _image_url(completed)
                if not image_url:
                    raise MagnificImageError(
                        f"Magnific task {task_id} returned no generated image"
                    )
                image_bytes = self.transport.download_image(image_url)
                if not image_bytes:
                    raise MagnificImageError(
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
                    "model": NANO_BANANA_2_MODEL,
                    "request_hash": request_hash,
                    "output_path": target_path.relative_to(output).as_posix(),
                    "output_sha256": _sha256_file(target_path),
                    "cache_hit": cache_hit,
                    "task_id": task_id,
                    "cost_ceiling_usd": (
                        0.0 if cache_hit else self.settings.cost_ceiling_usd
                    ),
                    "render_eligible": False,
                    "review_status": "pending",
                    "disclosure_label": "AI-generated learner plate candidate",
                }
            )

        manifest: dict[str, Any] = {
            "schema_version": MANIFEST_VERSION,
            "provider": MAGNIFIC_PROVIDER,
            "model": NANO_BANANA_2_MODEL,
            "approval_ceiling_usd": self.settings.max_cost_usd,
            "cost_ceiling_usd": round(
                provider_calls * self.settings.cost_ceiling_usd,
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
    "MAGNIFIC_PROVIDER",
    "MANIFEST_VERSION",
    "MagnificImageError",
    "MagnificImageHttpTransport",
    "MagnificImageService",
    "MagnificImageSettings",
    "NANO_BANANA_2_MODEL",
    "PLAN_VERSION",
    "validate_magnific_image_plan",
]
