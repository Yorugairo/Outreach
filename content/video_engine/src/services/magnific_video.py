"""Bounded Magnific image-to-video adapter.

This adapter deliberately uses Magnific's server-to-server API key rather than
browser cookies.  It is a provider test boundary: generated videos are cached
and recorded as non-renderable candidates until an operator reviews them.
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

from .media_enhancement import PROHIBITED_PROMPT_TERMS


PLAN_VERSION = "magnific_video_plan.v1"
MANIFEST_VERSION = "magnific_video_manifest.v1"
MAGNIFIC_PROVIDER = "magnific"
KLING_2_5_PRO_MODEL = "kling-v2-5-pro"
DEFAULT_MAGNIFIC_BASE_URL = "https://api.magnific.com"
MAX_IMAGE_BYTES = 10 * 1024 * 1024
MAX_VIDEO_DOWNLOAD_BYTES = 250 * 1024 * 1024
PROMPT_MAX_CHARS = 2500


class MagnificVideoError(RuntimeError):
    """A configuration, contract, provider, or artifact failure."""


class MagnificVideoTransport(Protocol):
    """Injectable HTTP boundary used by the real client and tests."""

    def create_kling_2_5(self, payload: Mapping[str, Any]) -> Mapping[str, Any]:
        ...

    def get_kling_2_5(self, task_id: str) -> Mapping[str, Any]:
        ...

    def download_video(self, url: str) -> bytes:
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
    approved_root = root.resolve()
    try:
        resolved.relative_to(approved_root)
    except ValueError as exc:
        raise MagnificVideoError(
            f"{label} escapes the approved project root: {value}"
        ) from exc
    return resolved


def _response_data(payload: Mapping[str, Any], label: str) -> Mapping[str, Any]:
    data = payload.get("data", payload)
    if not isinstance(data, Mapping):
        raise MagnificVideoError(f"{label} returned no object data")
    return data


def _task_id(data: Mapping[str, Any]) -> str:
    return str(data.get("task_id") or "").strip()


def _task_status(data: Mapping[str, Any]) -> str:
    return str(data.get("status") or data.get("task_status") or "").upper()


def _video_url(data: Mapping[str, Any]) -> str:
    generated = data.get("generated")
    if isinstance(generated, list) and generated:
        value = str(generated[0] or "").strip()
        if value:
            return value
    for candidate in (
        data.get("video_url"),
        data.get("url"),
        (data.get("result") or {}).get("video_url")
        if isinstance(data.get("result"), Mapping)
        else None,
        (data.get("output") or {}).get("video_url")
        if isinstance(data.get("output"), Mapping)
        else None,
    ):
        value = str(candidate or "").strip()
        if value:
            return value
    return ""


def _video_extension(value: bytes) -> str:
    if len(value) >= 12 and value[4:8] == b"ftyp":
        return ".mp4"
    if value.startswith(b"\x1a\x45\xdf\xa3"):
        return ".webm"
    if value.startswith(b"RIFF") and value[8:12] == b"AVI ":
        return ".avi"
    raise MagnificVideoError("Magnific returned an unsupported video signature")


@dataclass(frozen=True, slots=True)
class MagnificVideoSettings:
    api_key: str
    max_cost_usd: float
    max_calls: int
    paid_calls_allowed: bool
    base_url: str = DEFAULT_MAGNIFIC_BASE_URL
    timeout_s: float = 60.0
    poll_interval_s: float = 2.0
    max_poll_s: float = 600.0
    cost_ceiling_usd: float = 14.0

    @classmethod
    def from_environment(
        cls,
        *,
        max_cost_usd: float,
        max_calls: int,
        paid_calls_allowed: bool,
    ) -> "MagnificVideoSettings":
        api_key = (os.environ.get("MAGNIFIC_API_KEY") or "").strip()
        if not api_key:
            raise MagnificVideoError(
                "MAGNIFIC_API_KEY is required; load it from a local ignored env file"
            )
        if not paid_calls_allowed:
            raise MagnificVideoError(
                "Magnific video calls require the explicit --allow-paid flag"
            )
        if max_cost_usd <= 0:
            raise MagnificVideoError("Magnific max_cost_usd must be positive")
        if max_calls < 1:
            raise MagnificVideoError("Magnific max_calls must be positive")
        cost_ceiling = float(
            os.environ.get("MAGNIFIC_VIDEO_COST_CEILING_USD", "14")
        )
        if cost_ceiling <= 0:
            raise MagnificVideoError(
                "MAGNIFIC_VIDEO_COST_CEILING_USD must be positive"
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
                os.environ.get("MAGNIFIC_VIDEO_MAX_POLL_S", "600")
            ),
            cost_ceiling_usd=cost_ceiling,
        )

    def redacted(self) -> dict[str, Any]:
        return {
            "provider": MAGNIFIC_PROVIDER,
            "model": KLING_2_5_PRO_MODEL,
            "base_url": self.base_url,
            "max_cost_usd": self.max_cost_usd,
            "max_calls": self.max_calls,
            "paid_calls_allowed": self.paid_calls_allowed,
            "cost_ceiling_usd": self.cost_ceiling_usd,
            "pricing_status": "provider_plan_or_api_pricing_not_verified",
        }


class MagnificVideoHttpTransport:
    """Minimal urllib transport that never persists the API key."""

    def __init__(self, settings: MagnificVideoSettings) -> None:
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
            raise MagnificVideoError(
                f"Magnific video request failed with HTTP {exc.code}"
            ) from exc
        except urllib.error.URLError as exc:
            raise MagnificVideoError("Magnific video request failed") from exc
        try:
            decoded = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise MagnificVideoError(
                "Magnific video API returned invalid JSON"
            ) from exc
        if not isinstance(decoded, Mapping):
            raise MagnificVideoError(
                "Magnific video API returned a non-object response"
            )
        return decoded

    def create_kling_2_5(self, payload: Mapping[str, Any]) -> Mapping[str, Any]:
        return self._json_request(
            "POST",
            f"/v1/ai/image-to-video/{KLING_2_5_PRO_MODEL}",
            payload,
        )

    def get_kling_2_5(self, task_id: str) -> Mapping[str, Any]:
        return self._json_request(
            "GET",
            f"/v1/ai/image-to-video/{KLING_2_5_PRO_MODEL}/{task_id}",
        )

    def download_video(self, url: str) -> bytes:
        parsed = urlparse(url)
        if parsed.scheme != "https" or not parsed.netloc:
            raise MagnificVideoError("Magnific video URL must use HTTPS")
        request = urllib.request.Request(url, headers={"Accept": "video/*"})
        try:
            with urllib.request.urlopen(
                request,
                timeout=self.settings.timeout_s,
            ) as response:
                content_type = str(response.headers.get("Content-Type") or "")
                if content_type and not content_type.casefold().startswith("video/"):
                    raise MagnificVideoError(
                        "Magnific generated asset is not a video"
                    )
                raw = response.read(MAX_VIDEO_DOWNLOAD_BYTES + 1)
        except urllib.error.URLError as exc:
            raise MagnificVideoError(
                "Magnific generated video download failed"
            ) from exc
        if len(raw) > MAX_VIDEO_DOWNLOAD_BYTES:
            raise MagnificVideoError(
                "Magnific generated video exceeds the download limit"
            )
        return raw


def validate_magnific_video_plan(
    payload: Mapping[str, Any],
    *,
    project_root: str | Path,
) -> list[dict[str, Any]]:
    """Validate a local-image Kling 2.5 plan before any provider call."""

    if payload.get("schema_version") != PLAN_VERSION:
        raise MagnificVideoError(f"video plan must use {PLAN_VERSION}")
    if payload.get("provider") != MAGNIFIC_PROVIDER:
        raise MagnificVideoError("video plan provider must be magnific")
    if payload.get("model") != KLING_2_5_PRO_MODEL:
        raise MagnificVideoError(
            f"video plan model must be {KLING_2_5_PRO_MODEL}"
        )
    raw_items = payload.get("items")
    if not isinstance(raw_items, list) or not raw_items:
        raise MagnificVideoError("video plan requires items")

    root = Path(project_root).resolve()
    seen: set[str] = set()
    validated: list[dict[str, Any]] = []
    for index, raw_item in enumerate(raw_items):
        if not isinstance(raw_item, Mapping):
            raise MagnificVideoError(f"video plan item {index} must be an object")
        item_id = str(raw_item.get("id") or "").strip()
        if not item_id or item_id in seen:
            raise MagnificVideoError(
                f"video plan item {index} requires a unique non-empty id"
            )
        seen.add(item_id)
        source = _contained_path(
            str(raw_item.get("source_path") or ""),
            root,
            f"{item_id} source_path",
        )
        if not source.is_file():
            raise MagnificVideoError(f"{item_id} source file does not exist")
        if source.stat().st_size > MAX_IMAGE_BYTES:
            raise MagnificVideoError(f"{item_id} source image exceeds 10MB")
        if source.suffix.casefold() not in {".png", ".jpg", ".jpeg", ".webp"}:
            raise MagnificVideoError(
                f"{item_id} source must be PNG, JPEG, or WebP"
            )
        actual_hash = _sha256_file(source)
        if str(raw_item.get("source_sha256") or "").casefold() != actual_hash:
            raise MagnificVideoError(f"{item_id} source hash is stale")

        prompt = str(raw_item.get("prompt") or "").strip()
        negative_prompt = str(raw_item.get("negative_prompt") or "").strip()
        for label, value in (("prompt", prompt), ("negative_prompt", negative_prompt)):
            if len(value) > PROMPT_MAX_CHARS:
                raise MagnificVideoError(
                    f"{item_id} {label} exceeds {PROMPT_MAX_CHARS} characters"
                )
            lowered = value.casefold()
            for term in PROHIBITED_PROMPT_TERMS:
                if term in lowered:
                    raise MagnificVideoError(
                        f"{item_id} {label} contains prohibited renderer input {term!r}"
                    )
        if not prompt:
            raise MagnificVideoError(f"{item_id} prompt is required")

        resume_task_id = str(raw_item.get("task_id") or "").strip()
        if resume_task_id and not (
            len(resume_task_id) <= 200
            and all(character.isalnum() or character in "-_" for character in resume_task_id)
        ):
            raise MagnificVideoError(f"{item_id} task_id is invalid")

        duration = str(raw_item.get("duration") or "5")
        if duration not in {"5", "10"}:
            raise MagnificVideoError(f"{item_id} duration must be 5 or 10 seconds")
        cfg_scale = float(raw_item.get("cfg_scale", 0.5))
        if not 0 <= cfg_scale <= 1:
            raise MagnificVideoError(f"{item_id} cfg_scale must be between 0 and 1")
        validated.append(
            {
                "id": item_id,
                "source": source,
                "source_sha256": actual_hash,
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "duration": duration,
                "cfg_scale": cfg_scale,
                "resume_task_id": resume_task_id,
            }
        )
    return validated


class MagnificVideoService:
    """Execute a bounded provider test with content-addressed caching."""

    def __init__(
        self,
        settings: MagnificVideoSettings,
        *,
        transport: MagnificVideoTransport | None = None,
        sleep_fn: Any = time.sleep,
        monotonic_fn: Any = time.monotonic,
    ) -> None:
        self.settings = settings
        self.transport = transport or MagnificVideoHttpTransport(settings)
        self.sleep_fn = sleep_fn
        self.monotonic_fn = monotonic_fn

    def _poll(self, task_id: str) -> Mapping[str, Any]:
        deadline = self.monotonic_fn() + self.settings.max_poll_s
        while True:
            response = self.transport.get_kling_2_5(task_id)
            data = _response_data(response, "Magnific video task status")
            status = _task_status(data)
            if status in {"COMPLETED", "SUCCEEDED", "SUCCESS"}:
                return data
            if status in {"FAILED", "ERROR", "CANCELED", "CANCELLED"}:
                raise MagnificVideoError(
                    f"Magnific Kling 2.5 task {task_id} failed with status {status}"
                )
            if status not in {
                "CREATED",
                "QUEUED",
                "PROCESSING",
                "IN_PROGRESS",
                "RUNNING",
            }:
                raise MagnificVideoError(
                    f"Magnific Kling 2.5 task {task_id} has unknown status"
                )
            if self.monotonic_fn() >= deadline:
                raise MagnificVideoError(
                    f"Magnific Kling 2.5 task {task_id} timed out"
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
                raise MagnificVideoError(f"video plan could not be read: {exc}") from exc
        if not isinstance(payload, Mapping):
            raise MagnificVideoError("video plan must be an object")
        items = validate_magnific_video_plan(payload, project_root=project_root)
        if len(items) > self.settings.max_calls:
            raise MagnificVideoError(
                f"video plan requires {len(items)} calls but max_calls is {self.settings.max_calls}"
            )
        projected_cost = len(items) * self.settings.cost_ceiling_usd
        if projected_cost > self.settings.max_cost_usd + 1e-9:
            raise MagnificVideoError(
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
                "model": KLING_2_5_PRO_MODEL,
                "source_sha256": item["source_sha256"],
                "prompt": item["prompt"],
                "negative_prompt": item["negative_prompt"],
                "duration": item["duration"],
                "cfg_scale": item["cfg_scale"],
            }
            request_hash = _sha256_bytes(_canonical_bytes(request_contract))
            cached_candidates = [
                cache_dir / f"{request_hash}{suffix}"
                for suffix in (".mp4", ".webm", ".avi")
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
                    (provider_calls + 1) * self.settings.cost_ceiling_usd
                    > self.settings.max_cost_usd + 1e-9
                ):
                    raise MagnificVideoError(
                        "Magnific video cost ceiling reached before the next call"
                    )
                if item["resume_task_id"]:
                    task_id = item["resume_task_id"]
                    completed = self._poll(task_id)
                else:
                    provider_payload = {
                        "image": base64.b64encode(item["source"].read_bytes()).decode(
                            "ascii"
                        ),
                        "prompt": item["prompt"],
                        "negative_prompt": item["negative_prompt"],
                        "duration": item["duration"],
                        "cfg_scale": item["cfg_scale"],
                    }
                    response = self.transport.create_kling_2_5(provider_payload)
                    created = _response_data(response, "Magnific create video task")
                    task_id = _task_id(created)
                    if not task_id:
                        raise MagnificVideoError(
                            "Magnific create video task returned no task_id"
                        )
                    provider_calls += 1
                    completed = (
                        created
                        if _video_url(created)
                        and _task_status(created)
                        in {"COMPLETED", "SUCCEEDED", "SUCCESS"}
                        else self._poll(task_id)
                    )
                video_url = _video_url(completed)
                if not video_url:
                    raise MagnificVideoError(
                        f"Magnific task {task_id} returned no video_url"
                    )
                video_bytes = self.transport.download_video(video_url)
                if not video_bytes:
                    raise MagnificVideoError(
                        f"Magnific task {task_id} returned an empty video"
                    )
                extension = _video_extension(video_bytes)
                cache_path = cache_dir / f"{request_hash}{extension}"
                target_path = output / f"{item['id']}{extension}"
                cache_path.write_bytes(video_bytes)
                target_path.write_bytes(video_bytes)

            manifest_items.append(
                {
                    "id": item["id"],
                    "model": KLING_2_5_PRO_MODEL,
                    "request_hash": request_hash,
                    "source_sha256": item["source_sha256"],
                    "output_path": target_path.relative_to(output).as_posix(),
                    "output_sha256": _sha256_file(target_path),
                    "cache_hit": cache_hit,
                    "task_id": task_id,
                    "cost_ceiling_usd": (
                        0.0
                        if cache_hit or item["resume_task_id"]
                        else self.settings.cost_ceiling_usd
                    ),
                    "render_eligible": False,
                    "review_status": "pending",
                    "disclosure_label": "AI-generated motion test candidate",
                }
            )

        manifest: dict[str, Any] = {
            "schema_version": MANIFEST_VERSION,
            "provider": MAGNIFIC_PROVIDER,
            "model": KLING_2_5_PRO_MODEL,
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
    "KLING_2_5_PRO_MODEL",
    "MAGNIFIC_PROVIDER",
    "MANIFEST_VERSION",
    "MagnificVideoError",
    "MagnificVideoHttpTransport",
    "MagnificVideoService",
    "MagnificVideoSettings",
    "PLAN_VERSION",
    "validate_magnific_video_plan",
]
