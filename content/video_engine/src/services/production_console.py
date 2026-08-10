"""Loopback-only HTTP bridge for the read-only Production Console.

The bridge is intentionally small and dependency-free at the HTTP boundary.
It serves a prebuilt console, exposes the validated snapshot and snapshot-known
media, and places only typed, allowlisted job operations onto the local render
queue.  Revision mutation endpoints are deliberately absent while Gate A is
read-only.
"""

from __future__ import annotations

import hashlib
import copy
import json
import mimetypes
import os
import re
import threading
import uuid
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any
from urllib.parse import unquote, urlsplit

from content.video_engine.src.services.local_render_queue import (
    ALLOWED_OPERATIONS,
    JobContext,
    JobNotFoundError,
    LocalRenderQueue,
    LocalRenderQueueError,
    QueueClosedError,
    QueueOverflowError,
)
from content.video_engine.src.services.production_console_snapshot import (
    ProductionConsoleSnapshotError,
    validate_production_console_snapshot,
)


LOOPBACK_HOST = "127.0.0.1"
DEFAULT_PORT = 8765
MAX_REQUEST_BODY_BYTES = 256 * 1024
MAX_MEDIA_BYTES = 256 * 1024 * 1024

_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
_SHA256_RE = re.compile(r"^[a-f0-9]{64}$")
_MEDIA_TYPES = {
    ".aac": "audio/aac",
    ".gif": "image/gif",
    ".jpeg": "image/jpeg",
    ".jpg": "image/jpeg",
    ".m4a": "audio/mp4",
    ".mp3": "audio/mpeg",
    ".mp4": "video/mp4",
    ".png": "image/png",
    ".svg": "image/svg+xml",
    ".wav": "audio/wav",
    ".webm": "video/webm",
    ".webp": "image/webp",
}
_STATIC_TYPES = {
    ".css": "text/css; charset=utf-8",
    ".html": "text/html; charset=utf-8",
    ".ico": "image/x-icon",
    ".js": "text/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".map": "application/json; charset=utf-8",
    ".svg": "image/svg+xml",
    ".txt": "text/plain; charset=utf-8",
    ".woff": "font/woff",
    ".woff2": "font/woff2",
}
_JOB_ARGUMENT_KEYS = frozenset(
    {
        "artifact_id",
        "artifact_ids",
        "fps",
        "height",
        "width",
    }
)


class ProductionConsoleError(RuntimeError):
    """Safe structured error suitable for an HTTP response."""

    def __init__(
        self,
        code: str,
        message: str,
        *,
        status: int = HTTPStatus.BAD_REQUEST,
        details: Mapping[str, Any] | None = None,
    ) -> None:
        self.code = str(code)
        self.message = str(message)
        self.status = int(status)
        self.details = dict(details or {})
        super().__init__(self.message)


@dataclass(frozen=True, slots=True)
class ProductionConsoleConfig:
    """Validated startup configuration; no host field is intentionally present."""

    project_root: Path | str
    repository_root: Path | str
    snapshot_path: Path | str
    runtime_root: Path | str
    console_dist: Path | str
    port: int = DEFAULT_PORT
    queue_capacity: int = 2

    def __post_init__(self) -> None:
        object.__setattr__(self, "project_root", Path(self.project_root).resolve())
        object.__setattr__(self, "repository_root", Path(self.repository_root).resolve())
        object.__setattr__(self, "snapshot_path", Path(self.snapshot_path).resolve())
        object.__setattr__(self, "runtime_root", Path(self.runtime_root).resolve())
        object.__setattr__(self, "console_dist", Path(self.console_dist).resolve())
        if (
            not isinstance(self.port, int)
            or isinstance(self.port, bool)
            or not 0 <= self.port <= 65535
        ):
            raise ValueError("port must be between 0 and 65535")
        if (
            not isinstance(self.queue_capacity, int)
            or isinstance(self.queue_capacity, bool)
            or self.queue_capacity < 1
        ):
            raise ValueError("queue_capacity must be positive")

    @property
    def snapshot(self) -> Path:
        """Compatibility alias for callers using the CLI option's name."""

        return self.snapshot_path


@dataclass(frozen=True, slots=True)
class MediaPayload:
    body: bytes
    content_type: str
    asset_id: str


def _safe_identifier(value: Any, label: str) -> str:
    if not isinstance(value, str) or not _ID_RE.fullmatch(value):
        raise ProductionConsoleError(
            "INVALID_REQUEST",
            f"{label} must be a safe identifier",
        )
    return value


def _safe_relative(value: Any) -> str:
    """Return a slash-normalized relative path or raise without path detail."""

    if not isinstance(value, str) or not value or "\x00" in value:
        raise ProductionConsoleError("UNSAFE_PATH", "configured path is not allowed")
    normalized = value.replace("\\", "/")
    if normalized.startswith("/") or PureWindowsPath(value).is_absolute():
        raise ProductionConsoleError("UNSAFE_PATH", "configured path is not allowed")
    parts = PurePosixPath(normalized).parts
    if not parts or any(part in {"", ".", ".."} for part in parts):
        raise ProductionConsoleError("UNSAFE_PATH", "configured path is not allowed")
    if ":" in parts[0]:
        raise ProductionConsoleError("UNSAFE_PATH", "configured path is not allowed")
    return "/".join(parts)


def _inside(candidate: Path, root: Path) -> bool:
    try:
        candidate.resolve().relative_to(root.resolve())
    except (OSError, ValueError):
        return False
    return True


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_request_id(value: Any) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value or len(value) > 128:
        return None
    if any(ord(character) < 0x20 or ord(character) == 0x7F for character in value):
        return None
    return value


def _artifact_result(artifact_id: str, path: Path, root: Path) -> dict[str, str]:
    if not _inside(path, root) or not path.is_file():
        raise ProductionConsoleError("ARTIFACT_NOT_FOUND", "requested artifact was not found")
    relative = path.resolve().relative_to(root.resolve()).as_posix()
    return {
        "artifact_id": artifact_id,
        "path": relative,
        "sha256": _sha256_file(path),
    }


class ProductionConsoleService:
    """Business rules behind the loopback HTTP handler."""

    def __init__(
        self,
        project_root: ProductionConsoleConfig | str | Path,
        repository_root: str | Path | None = None,
        snapshot: str | Path | None = None,
        runtime_root: str | Path | None = None,
        console_dist: str | Path | None = None,
        *,
        snapshot_path: str | Path | None = None,
        port: int = DEFAULT_PORT,
        queue_capacity: int = 2,
        render_queue: LocalRenderQueue | None = None,
    ) -> None:
        if isinstance(project_root, ProductionConsoleConfig):
            if any(
                value is not None
                for value in (repository_root, snapshot, runtime_root, console_dist, snapshot_path)
            ):
                raise TypeError("a config cannot be combined with individual startup paths")
            config = project_root
        else:
            selected_snapshot = snapshot_path if snapshot_path is not None else snapshot
            if (
                repository_root is None
                or selected_snapshot is None
                or runtime_root is None
                or console_dist is None
            ):
                raise TypeError(
                    "project_root, repository_root, snapshot, runtime_root, and console_dist are required"
                )
            config = ProductionConsoleConfig(
                project_root=project_root,
                repository_root=repository_root,
                snapshot_path=selected_snapshot,
                runtime_root=runtime_root,
                console_dist=console_dist,
                port=port,
                queue_capacity=queue_capacity,
            )
        self.config = config
        self._validate_startup_roots()
        self._queue_owned = render_queue is None
        self.queue = render_queue or LocalRenderQueue(
            self._job_handlers(),
            max_pending=config.queue_capacity,
            runtime_root=config.runtime_root,
        )

    def _validate_startup_roots(self) -> None:
        if not self.config.project_root.is_dir() or not self.config.repository_root.is_dir():
            raise ProductionConsoleError(
                "INVALID_CONFIGURATION",
                "configured content roots are unavailable",
                status=HTTPStatus.INTERNAL_SERVER_ERROR,
            )
        if not self.config.snapshot_path.is_file():
            raise ProductionConsoleError(
                "INVALID_CONFIGURATION",
                "configured snapshot is unavailable",
                status=HTTPStatus.INTERNAL_SERVER_ERROR,
            )
        if not self.config.console_dist.is_dir():
            raise ProductionConsoleError(
                "INVALID_CONFIGURATION",
                "configured console dist is unavailable",
                status=HTTPStatus.INTERNAL_SERVER_ERROR,
            )
        if not _inside(self.config.snapshot_path, self.config.project_root) and not _inside(
            self.config.snapshot_path, self.config.repository_root
        ):
            raise ProductionConsoleError(
                "INVALID_CONFIGURATION",
                "configured snapshot is outside the allowed roots",
                status=HTTPStatus.INTERNAL_SERVER_ERROR,
            )
        self.config.runtime_root.mkdir(parents=True, exist_ok=True)

    def close(self) -> None:
        if self._queue_owned:
            self.queue.close()

    shutdown = close

    def _load_snapshot(self) -> dict[str, Any]:
        try:
            payload = json.loads(self.config.snapshot_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise ProductionConsoleError(
                "SNAPSHOT_UNAVAILABLE",
                "console snapshot is unavailable",
                status=HTTPStatus.SERVICE_UNAVAILABLE,
            ) from exc
        if not isinstance(payload, Mapping):
            raise ProductionConsoleError(
                "SNAPSHOT_INVALID",
                "console snapshot is invalid",
                status=HTTPStatus.SERVICE_UNAVAILABLE,
            )
        try:
            validated = validate_production_console_snapshot(payload)
            self._validate_snapshot_paths(validated)
        except (ProductionConsoleSnapshotError, ProductionConsoleError) as exc:
            raise ProductionConsoleError(
                "SNAPSHOT_INVALID",
                "console snapshot is invalid or stale",
                status=HTTPStatus.CONFLICT,
            ) from exc
        return validated

    def _validate_snapshot_paths(self, snapshot: Mapping[str, Any]) -> None:
        for artifact in snapshot.get("artifacts", []):
            path = _safe_relative(artifact.get("path"))
            if artifact.get("status") == "available":
                candidate = (self.config.project_root / path).resolve()
                if not _inside(candidate, self.config.project_root) or not candidate.is_file():
                    raise ProductionConsoleError("SNAPSHOT_STALE", "snapshot artifact is stale")
                expected = str(artifact.get("sha256") or "")
                if not _SHA256_RE.fullmatch(expected) or _sha256_file(candidate) != expected:
                    raise ProductionConsoleError("SNAPSHOT_STALE", "snapshot artifact is stale")
        for review in snapshot.get("reviews", []):
            _safe_relative(review.get("artifact_path"))
        for asset in snapshot.get("assets", []):
            _safe_relative(asset.get("path"))
            if asset.get("path_root") not in {"project", "repository"}:
                raise ProductionConsoleError("SNAPSHOT_INVALID", "snapshot asset root is invalid")

    def health(self) -> dict[str, Any]:
        snapshot = self._load_snapshot()
        return {
            "schema_version": "production_console_health.v1",
            "status": "ok",
            "bridge": "production_console",
            "loopback_only": True,
            "snapshot_id": snapshot["snapshot_id"],
            "queue": self.queue.stats(),
        }

    def snapshot(self) -> dict[str, Any]:
        return self._load_snapshot()

    def public_snapshot(self) -> dict[str, Any]:
        """Return browser-safe context with filesystem routing fields removed."""

        snapshot = copy.deepcopy(self._load_snapshot())
        for artifact in snapshot.get("artifacts", []):
            artifact.pop("path", None)
        for asset in snapshot.get("assets", []):
            asset.pop("path", None)
            asset.pop("path_root", None)
        for review in snapshot.get("reviews", []):
            review.pop("artifact_path", None)
        return snapshot

    def public_assets(self) -> list[dict[str, Any]]:
        return list(self.public_snapshot().get("assets", []))

    def public_reviews(self) -> list[dict[str, Any]]:
        return list(self.public_snapshot().get("reviews", []))

    @staticmethod
    def public_revisions() -> list[dict[str, Any]]:
        # Gate A has no immutable revision artifacts yet. Returning a typed
        # empty collection is preferable to inventing browser-local state.
        return []

    @staticmethod
    def _asset_map(snapshot: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
        return {
            str(asset.get("asset_id")): asset
            for asset in snapshot.get("assets", [])
            if isinstance(asset, Mapping) and asset.get("asset_id")
        }

    @staticmethod
    def _artifact_map(snapshot: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
        return {
            str(artifact.get("artifact_id")): artifact
            for artifact in snapshot.get("artifacts", [])
            if isinstance(artifact, Mapping) and artifact.get("artifact_id")
        }

    def _resolve_asset(self, asset_id: str, *, snapshot: Mapping[str, Any] | None = None) -> tuple[Path, Mapping[str, Any]]:
        selected_snapshot = snapshot or self._load_snapshot()
        assets = self._asset_map(selected_snapshot)
        asset = assets.get(asset_id)
        if asset is None:
            raise ProductionConsoleError(
                "ASSET_NOT_FOUND",
                "snapshot asset was not found",
                status=HTTPStatus.NOT_FOUND,
            )
        path_root = asset.get("path_root")
        root = {
            "project": self.config.project_root,
            "repository": self.config.repository_root,
        }.get(path_root)
        if root is None:
            raise ProductionConsoleError("UNSAFE_PATH", "asset path is not allowed")
        relative = _safe_relative(asset.get("path"))
        candidate = (root / relative).resolve()
        if not _inside(candidate, root) or not candidate.is_file():
            raise ProductionConsoleError("ASSET_NOT_FOUND", "snapshot asset was not found")
        try:
            body = candidate.read_bytes()
        except OSError as exc:
            raise ProductionConsoleError("ASSET_UNAVAILABLE", "snapshot asset is unavailable") from exc
        if len(body) > MAX_MEDIA_BYTES:
            raise ProductionConsoleError("ASSET_TOO_LARGE", "snapshot asset is too large")
        expected = str(asset.get("sha256") or "")
        if not _SHA256_RE.fullmatch(expected) or _sha256_bytes(body) != expected:
            raise ProductionConsoleError(
                "ASSET_HASH_MISMATCH",
                "snapshot asset hash does not match",
                status=HTTPStatus.CONFLICT,
            )
        return candidate, asset

    def media(self, asset_id: str) -> MediaPayload:
        asset = _safe_identifier(asset_id, "asset_id")
        path, _record = self._resolve_asset(asset)
        content_type = _MEDIA_TYPES.get(path.suffix.casefold())
        if content_type is None:
            raise ProductionConsoleError(
                "MEDIA_TYPE_NOT_ALLOWED",
                "snapshot asset media type is not allowed",
                status=HTTPStatus.UNSUPPORTED_MEDIA_TYPE,
            )
        try:
            body = path.read_bytes()
        except OSError as exc:
            raise ProductionConsoleError("ASSET_UNAVAILABLE", "snapshot asset is unavailable") from exc
        return MediaPayload(body=body, content_type=content_type, asset_id=asset)

    def _resolve_job_artifact(
        self,
        artifact_id: str,
        revision_id: str,
        *,
        snapshot: Mapping[str, Any],
    ) -> tuple[Path, Path]:
        artifact = self._artifact_map(snapshot).get(artifact_id)
        if artifact is not None:
            relative = _safe_relative(artifact.get("path"))
            path = (self.config.project_root / relative).resolve()
            if (
                artifact.get("status") != "available"
                or not _inside(path, self.config.project_root)
                or not path.is_file()
                or _sha256_file(path) != artifact.get("sha256")
            ):
                raise ProductionConsoleError("ARTIFACT_STALE", "requested artifact is stale")
            return path, self.config.project_root
        asset_map = self._asset_map(snapshot)
        if artifact_id in asset_map:
            path, _ = self._resolve_asset(artifact_id, snapshot=snapshot)
            root = self.config.project_root if asset_map[artifact_id]["path_root"] == "project" else self.config.repository_root
            return path, root

        # Runtime artifacts are addressed by a safe ID, never by an HTTP path.
        # The revision directory is fixed by the bridge and remains contained
        # by the configured runtime root.
        candidate = (self.config.runtime_root / revision_id / artifact_id).resolve()
        if not _inside(candidate, self.config.runtime_root) or not candidate.is_file():
            raise ProductionConsoleError("ARTIFACT_NOT_FOUND", "requested artifact was not found")
        return candidate, self.config.runtime_root

    def _write_operation_receipt(
        self,
        context: JobContext,
        *,
        artifact_ids: Sequence[str],
    ) -> Mapping[str, Any]:
        destination_root = self.config.runtime_root / "results"
        destination_root.mkdir(parents=True, exist_ok=True)
        destination = destination_root / f"{context.job_id}.json"
        payload = {
            "schema_version": "production_console_job_result.v1",
            "job_id": context.job_id,
            "revision_id": context.revision_id,
            "operation": context.operation,
            "artifact_ids": list(artifact_ids),
            "provider_calls": 0,
            "publish_calls": 0,
        }
        temporary = destination.with_name(f".{destination.name}.{uuid.uuid4().hex}.tmp")
        try:
            temporary.write_text(
                json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
                encoding="utf-8",
            )
            os.replace(temporary, destination)
        except OSError as exc:
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                pass
            raise LocalRenderQueueError(
                "JOB_PERSISTENCE_FAILED",
                "render job result could not be persisted",
            ) from exc
        return {
            "artifacts": [
                _artifact_result(
                    "job-result",
                    destination,
                    self.config.runtime_root,
                )
            ]
        }

    def _run_allowlisted_operation(
        self,
        operation: str,
        arguments: Mapping[str, Any],
        context: JobContext,
    ) -> Mapping[str, Any]:
        snapshot = self._load_snapshot()
        raw_ids = arguments.get("artifact_ids", [])
        if "artifact_id" in arguments:
            raw_ids = [*raw_ids, arguments["artifact_id"]]
        artifact_ids = list(dict.fromkeys(raw_ids))
        for artifact_id in artifact_ids:
            context.raise_if_cancelled()
            safe_id = _safe_identifier(artifact_id, "artifact_id")
            self._resolve_job_artifact(safe_id, context.revision_id, snapshot=snapshot)
        return self._write_operation_receipt(context, artifact_ids=artifact_ids)

    def _job_handlers(self) -> dict[str, Any]:
        return {
            operation: lambda arguments, context, operation=operation: self._run_allowlisted_operation(
                operation,
                arguments,
                context,
            )
            for operation in ALLOWED_OPERATIONS
        }

    def _validate_job_arguments(self, arguments: Any) -> dict[str, Any]:
        if arguments is None:
            return {}
        if not isinstance(arguments, Mapping):
            raise ProductionConsoleError("INVALID_REQUEST", "job arguments must be an object")
        unknown = set(arguments) - _JOB_ARGUMENT_KEYS
        if unknown:
            raise ProductionConsoleError(
                "INVALID_REQUEST",
                "job arguments contain an unsupported field",
            )
        normalized: dict[str, Any] = {}
        if "artifact_id" in arguments:
            normalized["artifact_id"] = _safe_identifier(arguments["artifact_id"], "artifact_id")
        if "artifact_ids" in arguments:
            values = arguments["artifact_ids"]
            if not isinstance(values, Sequence) or isinstance(values, (str, bytes, bytearray)):
                raise ProductionConsoleError("INVALID_REQUEST", "artifact_ids must be an array")
            if len(values) > 64:
                raise ProductionConsoleError("INVALID_REQUEST", "too many artifact IDs")
            normalized["artifact_ids"] = [
                _safe_identifier(value, "artifact_id") for value in values
            ]
        for key, lower, upper in (
            ("width", 16, 4096),
            ("height", 16, 4096),
            ("fps", 1, 120),
        ):
            if key in arguments:
                value = arguments[key]
                if isinstance(value, bool) or not isinstance(value, int) or not lower <= value <= upper:
                    raise ProductionConsoleError("INVALID_REQUEST", f"{key} is outside the allowed range")
                normalized[key] = value
        return normalized

    def submit_job(self, request: Mapping[str, Any]) -> dict[str, Any]:
        if not isinstance(request, Mapping):
            raise ProductionConsoleError("INVALID_REQUEST", "job request must be an object")
        allowed = {"operation", "revision_id", "request_id", "arguments"}
        if set(request) - allowed:
            raise ProductionConsoleError(
                "INVALID_REQUEST",
                "job request contains an unsupported field",
            )
        operation = request.get("operation")
        if not isinstance(operation, str) or operation not in ALLOWED_OPERATIONS:
            raise ProductionConsoleError(
                "OPERATION_NOT_ALLOWED",
                "render operation is not allowlisted",
                details={"allowed_operations": sorted(ALLOWED_OPERATIONS)},
            )
        revision_id = _safe_identifier(request.get("revision_id"), "revision_id")
        request_id = request.get("request_id")
        if request_id is not None:
            request_id = _safe_identifier(request_id, "request_id")
        arguments = self._validate_job_arguments(request.get("arguments"))
        try:
            return self.queue.submit(
                operation,
                revision_id=revision_id,
                request_id=request_id,
                arguments=arguments,
            )
        except QueueOverflowError as exc:
            raise ProductionConsoleError(
                exc.code,
                exc.message,
                status=HTTPStatus.TOO_MANY_REQUESTS,
            ) from exc
        except QueueClosedError as exc:
            raise ProductionConsoleError(
                exc.code,
                exc.message,
                status=HTTPStatus.SERVICE_UNAVAILABLE,
            ) from exc
        except LocalRenderQueueError as exc:
            raise ProductionConsoleError(exc.code, exc.message, details=exc.details) from exc

    def get_job(self, job_id: str) -> dict[str, Any]:
        safe_id = _safe_identifier(job_id, "job_id")
        try:
            return self.queue.get(safe_id)
        except JobNotFoundError as exc:
            raise ProductionConsoleError(
                exc.code,
                exc.message,
                status=HTTPStatus.NOT_FOUND,
            ) from exc

    def cancel_job(self, job_id: str) -> dict[str, Any]:
        safe_id = _safe_identifier(job_id, "job_id")
        try:
            return self.queue.cancel(safe_id)
        except JobNotFoundError as exc:
            raise ProductionConsoleError(
                exc.code,
                exc.message,
                status=HTTPStatus.NOT_FOUND,
            ) from exc

    def static(self, request_path: str) -> tuple[bytes, str]:
        decoded = unquote(request_path)
        if decoded == "/":
            relative = "index.html"
        else:
            relative = decoded.lstrip("/")
        try:
            safe_relative = _safe_relative(relative)
        except ProductionConsoleError:
            raise ProductionConsoleError(
                "STATIC_NOT_FOUND",
                "console asset was not found",
                status=HTTPStatus.NOT_FOUND,
            )
        candidate = (self.config.console_dist / safe_relative).resolve()
        if not _inside(candidate, self.config.console_dist) or not candidate.is_file():
            # Client-side routes can still resolve to the built app shell, but
            # never allow a path-shaped request to escape the static root.
            if "." not in Path(safe_relative).name:
                candidate = (self.config.console_dist / "index.html").resolve()
            if not _inside(candidate, self.config.console_dist) or not candidate.is_file():
                raise ProductionConsoleError(
                    "STATIC_NOT_FOUND",
                    "console asset was not found",
                    status=HTTPStatus.NOT_FOUND,
                )
        try:
            body = candidate.read_bytes()
        except OSError as exc:
            raise ProductionConsoleError(
                "STATIC_UNAVAILABLE",
                "console asset is unavailable",
                status=HTTPStatus.NOT_FOUND,
            ) from exc
        content_type = _STATIC_TYPES.get(candidate.suffix.casefold())
        if content_type is None:
            content_type = mimetypes.guess_type(candidate.name)[0] or "application/octet-stream"
        return body, content_type


class _ConsoleHTTPServer(ThreadingHTTPServer):
    allow_reuse_address = True
    daemon_threads = True

    def __init__(self, service: ProductionConsoleService, port: int) -> None:
        self.console_service = service
        # The literal constant is intentional: no caller or CLI argument can
        # turn this server into a LAN/public listener.
        super().__init__((LOOPBACK_HOST, port), _ConsoleRequestHandler)


class _ConsoleRequestHandler(BaseHTTPRequestHandler):
    server: _ConsoleHTTPServer
    protocol_version = "HTTP/1.1"

    def log_message(self, _format: str, *_args: Any) -> None:
        # Avoid the default logger, which echoes the full request target.
        return

    @property
    def service(self) -> ProductionConsoleService:
        return self.server.console_service

    def _request_id(self) -> str:
        supplied = _safe_request_id(self.headers.get("X-Request-ID"))
        return supplied or f"request-{uuid.uuid4().hex}"

    def _send_json(self, status: int, payload: Mapping[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def _success(self, data: Any, *, status: int = HTTPStatus.OK) -> None:
        self._send_json(
            status,
            {
                "schema_version": "production_console_response.v1",
                "ok": True,
                "data": data,
                "request_id": self._request_id_value,
            },
        )

    def _failure(self, error: ProductionConsoleError, *, request_id: str | None = None) -> None:
        safe_details = dict(error.details)
        self._send_json(
            error.status,
            {
                "schema_version": "production_console_error.v1",
                "ok": False,
                "error": {
                    "code": error.code,
                    "message": error.message,
                    "details": safe_details,
                    "request_id": request_id or self._request_id_value,
                },
            },
        )

    def _not_found(self, request_id: str) -> None:
        self._failure(
            ProductionConsoleError(
                "NOT_FOUND",
                "console route was not found",
                status=HTTPStatus.NOT_FOUND,
            ),
            request_id=request_id,
        )

    def _read_json_body(self) -> dict[str, Any]:
        raw_length = self.headers.get("Content-Length")
        try:
            length = int(raw_length or "-1")
        except ValueError as exc:
            raise ProductionConsoleError("INVALID_REQUEST", "request body length is invalid") from exc
        if length < 0 or length > MAX_REQUEST_BODY_BYTES:
            raise ProductionConsoleError("REQUEST_TOO_LARGE", "request body is too large", status=HTTPStatus.REQUEST_ENTITY_TOO_LARGE)
        try:
            raw = self.rfile.read(length)
            payload = json.loads(raw.decode("utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise ProductionConsoleError("INVALID_REQUEST", "request body must be JSON") from exc
        if not isinstance(payload, dict):
            raise ProductionConsoleError("INVALID_REQUEST", "request body must be an object")
        return payload

    def _begin_request(self) -> None:
        self._request_id_value = self._request_id()
        if self.client_address and self.client_address[0] != LOOPBACK_HOST:
            raise ProductionConsoleError(
                "LOOPBACK_ONLY",
                "console bridge accepts loopback connections only",
                status=HTTPStatus.FORBIDDEN,
            )

    def do_GET(self) -> None:  # noqa: N802 - stdlib handler API
        try:
            self._begin_request()
            path = unquote(urlsplit(self.path).path)
            if path == "/api/health":
                self._success(self.service.health())
                return
            if path == "/api/snapshot":
                self._success(self.service.public_snapshot())
                return
            if path == "/api/assets":
                self._success(self.service.public_assets())
                return
            if path == "/api/reviews":
                self._success(self.service.public_reviews())
                return
            if path == "/api/revisions":
                self._success(self.service.public_revisions())
                return
            segments = [segment for segment in path.split("/") if segment]
            if len(segments) == 3 and segments[:2] == ["api", "jobs"]:
                self._success(self.service.get_job(segments[2]))
                return
            if len(segments) == 2 and segments[0] == "media":
                media = self.service.media(segments[1])
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", media.content_type)
                self.send_header("Content-Length", str(len(media.body)))
                self.send_header("Cache-Control", "no-store")
                self.send_header("X-Content-Type-Options", "nosniff")
                self.end_headers()
                self.wfile.write(media.body)
                return
            if path.startswith("/api/") or path.startswith("/media/"):
                self._not_found(self._request_id_value)
                return
            body, content_type = self.service.static(path)
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(body)
        except ProductionConsoleError as exc:
            self._failure(exc, request_id=getattr(self, "_request_id_value", None))
        except Exception:
            self._failure(
                ProductionConsoleError(
                    "INTERNAL_ERROR",
                    "console request failed",
                    status=HTTPStatus.INTERNAL_SERVER_ERROR,
                ),
                request_id=getattr(self, "_request_id_value", None),
            )

    def do_POST(self) -> None:  # noqa: N802 - stdlib handler API
        try:
            self._begin_request()
            path = unquote(urlsplit(self.path).path)
            if path != "/api/jobs":
                self._not_found(self._request_id_value)
                return
            request = self._read_json_body()
            job = self.service.submit_job(request)
            self._success(job, status=HTTPStatus.ACCEPTED)
        except ProductionConsoleError as exc:
            self._failure(exc, request_id=getattr(self, "_request_id_value", None))
        except Exception:
            self._failure(
                ProductionConsoleError(
                    "INTERNAL_ERROR",
                    "console request failed",
                    status=HTTPStatus.INTERNAL_SERVER_ERROR,
                ),
                request_id=getattr(self, "_request_id_value", None),
            )

    def do_DELETE(self) -> None:  # noqa: N802 - stdlib handler API
        try:
            self._begin_request()
            path = unquote(urlsplit(self.path).path)
            segments = [segment for segment in path.split("/") if segment]
            if len(segments) != 3 or segments[:2] != ["api", "jobs"]:
                self._not_found(self._request_id_value)
                return
            self._success(self.service.cancel_job(segments[2]))
        except ProductionConsoleError as exc:
            self._failure(exc, request_id=getattr(self, "_request_id_value", None))
        except Exception:
            self._failure(
                ProductionConsoleError(
                    "INTERNAL_ERROR",
                    "console request failed",
                    status=HTTPStatus.INTERNAL_SERVER_ERROR,
                ),
                request_id=getattr(self, "_request_id_value", None),
            )


def create_production_console_server(
    service: ProductionConsoleService,
    *,
    port: int | None = None,
) -> ThreadingHTTPServer:
    """Create a server bound exactly to IPv4 loopback."""

    selected_port = service.config.port if port is None else port
    if not isinstance(selected_port, int) or isinstance(selected_port, bool) or not 0 <= selected_port <= 65535:
        raise ValueError("port must be between 0 and 65535")
    return _ConsoleHTTPServer(service, selected_port)


def serve_production_console(
    *,
    project_root: str | Path,
    repository_root: str | Path,
    snapshot: str | Path | None = None,
    snapshot_path: str | Path | None = None,
    runtime_root: str | Path,
    console_dist: str | Path,
    port: int = DEFAULT_PORT,
    queue_capacity: int = 2,
) -> None:
    """Run the blocking CLI server on loopback until interrupted."""

    selected_snapshot = snapshot_path if snapshot_path is not None else snapshot
    if selected_snapshot is None:
        raise TypeError("snapshot is required")
    service = ProductionConsoleService(
        project_root,
        repository_root,
        selected_snapshot,
        runtime_root,
        console_dist,
        port=port,
        queue_capacity=queue_capacity,
    )
    server = create_production_console_server(service)
    try:
        print(
            json.dumps(
                {
                    "status": "listening",
                    "host": LOOPBACK_HOST,
                    "port": int(server.server_address[1]),
                },
                sort_keys=True,
            ),
            flush=True,
        )
        server.serve_forever()
    finally:
        server.server_close()
        service.close()


ProductionConsoleBridge = ProductionConsoleService
ProductionConsoleServer = _ConsoleHTTPServer


__all__ = [
    "ALLOWED_OPERATIONS",
    "DEFAULT_PORT",
    "LOOPBACK_HOST",
    "MediaPayload",
    "ProductionConsoleBridge",
    "ProductionConsoleConfig",
    "ProductionConsoleError",
    "ProductionConsoleServer",
    "ProductionConsoleService",
    "create_production_console_server",
    "serve_production_console",
]
