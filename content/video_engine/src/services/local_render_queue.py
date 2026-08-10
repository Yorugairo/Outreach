"""Bounded, local-only render job queue primitives.

The queue deliberately accepts operation identifiers and JSON-like arguments,
not command text.  Callers register the small set of handlers they own; a
handler may use :func:`run_typed_argv` for a fixed subprocess invocation, but
the queue never accepts or evaluates shell syntax.
"""

from __future__ import annotations

import inspect
import json
import os
import queue
import re
import subprocess
import threading
import time
import uuid
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any, TypeAlias


JOB_SCHEMA_VERSION = "local_render_job.v1"
JOB_STATES = frozenset({"queued", "running", "succeeded", "failed", "cancelled"})
TERMINAL_JOB_STATES = frozenset({"succeeded", "failed", "cancelled"})
ALLOWED_OPERATIONS = frozenset(
    {
        "validate_revision",
        "compile_revision",
        "render_preview",
        "render_diagnostic",
    }
)

_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
_SHA256_RE = re.compile(r"^[a-f0-9]{64}$")
_FORBIDDEN_ARGUMENT_KEYS = frozenset(
    {
        "argv",
        "cmd",
        "command",
        "commands",
        "patch",
        "script",
        "shell",
    }
)


class LocalRenderQueueError(RuntimeError):
    """Base error with a stable public code and safe details."""

    def __init__(
        self,
        code: str,
        message: str,
        *,
        details: Mapping[str, Any] | None = None,
    ) -> None:
        self.code = str(code)
        self.message = str(message)
        self.details = dict(details or {})
        super().__init__(self.message)


class QueueOverflowError(LocalRenderQueueError):
    """Raised when the active queue has reached its configured capacity."""

    def __init__(self) -> None:
        super().__init__(
            "QUEUE_OVERFLOW",
            "render queue capacity is full",
        )


class QueueClosedError(LocalRenderQueueError):
    """Raised when a submission is attempted after queue shutdown."""

    def __init__(self) -> None:
        super().__init__("QUEUE_CLOSED", "render queue is closed")


class JobNotFoundError(LocalRenderQueueError):
    """Raised when a job identifier is not known to the queue."""

    def __init__(self) -> None:
        super().__init__("JOB_NOT_FOUND", "render job was not found")


class OperationNotAllowedError(LocalRenderQueueError):
    """Raised when an operation is not registered by the caller."""

    def __init__(self, operation: str) -> None:
        super().__init__(
            "OPERATION_NOT_ALLOWED",
            "render operation is not allowlisted",
            details={"operation": operation},
        )


class JobCancelledError(LocalRenderQueueError):
    """Raised by a handler that observes cancellation while doing work."""

    def __init__(self) -> None:
        super().__init__("JOB_CANCELLED", "render job was cancelled")


class JobExecutionError(LocalRenderQueueError):
    """Raised when a typed local operation cannot complete."""

    def __init__(self, message: str = "render operation failed") -> None:
        # Do not preserve arbitrary subprocess/error text: it can contain a
        # machine path or an untrusted command fragment.
        super().__init__("JOB_EXECUTION_FAILED", message)


@dataclass(frozen=True, slots=True)
class JobContext:
    """Context supplied to an allowlisted handler."""

    job_id: str
    request_id: str
    revision_id: str
    operation: str
    cancel_event: threading.Event
    runtime_root: Path | None

    @property
    def cancellation_requested(self) -> bool:
        return self.cancel_event.is_set()

    def raise_if_cancelled(self) -> None:
        if self.cancellation_requested:
            raise JobCancelledError()


JobHandler: TypeAlias = Callable[
    [Mapping[str, Any], JobContext],
    Mapping[str, Any] | None,
]


@dataclass(slots=True)
class _QueuedJob:
    job: dict[str, Any]
    arguments: dict[str, Any]
    cancel_event: threading.Event
    finished: threading.Event


def _utc_now() -> str:
    return (
        datetime.now(timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )


def _safe_id(value: Any, label: str) -> str:
    if not isinstance(value, str) or not _ID_RE.fullmatch(value):
        raise LocalRenderQueueError(
            "INVALID_JOB_REQUEST",
            f"{label} must be a safe identifier",
        )
    return value


def _json_copy(value: Any) -> Any:
    try:
        return json.loads(json.dumps(value, ensure_ascii=False))
    except (TypeError, ValueError, OverflowError) as exc:
        raise LocalRenderQueueError(
            "INVALID_JOB_REQUEST",
            "job arguments must be JSON values",
        ) from exc


def _reject_forbidden_keys(value: Any) -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            if str(key).casefold() in _FORBIDDEN_ARGUMENT_KEYS:
                raise LocalRenderQueueError(
                    "INVALID_JOB_REQUEST",
                    "job arguments contain an unsupported command field",
                )
            _reject_forbidden_keys(item)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for item in value:
            _reject_forbidden_keys(item)


def _validate_relative_artifact_path(value: Any) -> str:
    if not isinstance(value, str) or not value or "\x00" in value:
        raise JobExecutionError("render operation returned an invalid artifact")
    if PureWindowsPath(value).is_absolute() or PurePosixPath(value).is_absolute():
        raise JobExecutionError("render operation returned an invalid artifact")
    normalized = value.replace("\\", "/")
    parts = PurePosixPath(normalized).parts
    if not parts or any(part in {"", ".", ".."} for part in parts):
        raise JobExecutionError("render operation returned an invalid artifact")
    if ":" in parts[0]:
        raise JobExecutionError("render operation returned an invalid artifact")
    return "/".join(parts)


def _validate_handler_result(result: Mapping[str, Any] | None) -> list[dict[str, str]]:
    if result is None:
        return []
    if not isinstance(result, Mapping):
        raise JobExecutionError("render operation returned an invalid result")
    artifacts = result.get("artifacts", [])
    if not isinstance(artifacts, Sequence) or isinstance(artifacts, (str, bytes, bytearray)):
        raise JobExecutionError("render operation returned an invalid result")
    validated: list[dict[str, str]] = []
    for artifact in artifacts:
        if not isinstance(artifact, Mapping):
            raise JobExecutionError("render operation returned an invalid artifact")
        if set(artifact) != {"artifact_id", "path", "sha256"}:
            raise JobExecutionError("render operation returned an invalid artifact")
        artifact_id = artifact.get("artifact_id")
        if not isinstance(artifact_id, str) or not _ID_RE.fullmatch(artifact_id):
            raise JobExecutionError("render operation returned an invalid artifact")
        path = _validate_relative_artifact_path(artifact.get("path"))
        sha256 = artifact.get("sha256")
        if not isinstance(sha256, str) or not _SHA256_RE.fullmatch(sha256):
            raise JobExecutionError("render operation returned an invalid artifact")
        validated.append(
            {
                "artifact_id": artifact_id,
                "path": path,
                "sha256": sha256,
            }
        )
    return validated


def _call_handler(handler: Callable[..., Any], arguments: Mapping[str, Any], context: JobContext) -> Any:
    """Call the documented two-argument handler, with one-argument test support."""

    try:
        signature = inspect.signature(handler)
    except (TypeError, ValueError):
        return handler(arguments, context)
    positional = [
        parameter
        for parameter in signature.parameters.values()
        if parameter.kind
        in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
    ]
    accepts_varargs = any(
        parameter.kind == inspect.Parameter.VAR_POSITIONAL
        for parameter in signature.parameters.values()
    )
    if accepts_varargs or len(positional) >= 2:
        return handler(arguments, context)
    return handler(arguments)


def run_typed_argv(
    argv: Sequence[str],
    *,
    cwd: str | Path | None = None,
    cancel_event: threading.Event | None = None,
    timeout_s: float | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run a caller-owned argument vector without a shell.

    This helper is intentionally strict and is not exposed as an HTTP
    operation.  The bridge's handlers construct the vector from fixed
    operation definitions; callers cannot submit it through the API.
    """

    if isinstance(argv, (str, bytes, bytearray)):
        raise JobExecutionError("typed subprocess arguments are required")
    values = list(argv)
    if not values or any(not isinstance(item, str) or "\x00" in item for item in values):
        raise JobExecutionError("typed subprocess arguments are required")
    if timeout_s is not None and (not isinstance(timeout_s, (int, float)) or timeout_s <= 0):
        raise JobExecutionError("subprocess timeout is invalid")

    process = subprocess.Popen(
        values,
        cwd=str(cwd) if cwd is not None else None,
        shell=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    started = time.monotonic()
    while True:
        return_code = process.poll()
        if return_code is not None:
            break
        if cancel_event is not None and cancel_event.is_set():
            process.terminate()
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
            raise JobCancelledError()
        if timeout_s is not None and time.monotonic() - started >= float(timeout_s):
            process.terminate()
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
            raise JobExecutionError("render operation timed out")
        time.sleep(0.02)

    completed = subprocess.CompletedProcess(values, return_code)
    if return_code != 0:
        raise JobExecutionError()
    return completed


class LocalRenderQueue:
    """A bounded FIFO queue with exactly one worker thread.

    ``max_pending`` is the total active capacity, including the running job.
    Completed jobs remain readable until the queue is closed, but do not count
    toward that capacity.
    """

    def __init__(
        self,
        handlers: Mapping[str, Callable[..., Any]],
        *,
        max_pending: int = 2,
        runtime_root: str | Path | None = None,
        start_worker: bool = True,
    ) -> None:
        if not isinstance(max_pending, int) or isinstance(max_pending, bool) or max_pending < 1:
            raise ValueError("max_pending must be a positive integer")
        normalized_handlers = dict(handlers)
        if not normalized_handlers:
            raise ValueError("at least one allowlisted render handler is required")
        invalid = set(normalized_handlers) - ALLOWED_OPERATIONS
        if invalid:
            raise ValueError("render handlers contain unsupported operations")
        if any(not callable(handler) for handler in normalized_handlers.values()):
            raise ValueError("render handlers must be callable")

        self.max_pending = max_pending
        self.handlers = normalized_handlers
        self.runtime_root = Path(runtime_root).resolve() if runtime_root is not None else None
        self._job_directory: Path | None = None
        if self.runtime_root is not None:
            self.runtime_root.mkdir(parents=True, exist_ok=True)
            self._job_directory = self.runtime_root / "jobs"
            self._job_directory.mkdir(parents=True, exist_ok=True)

        self._items: queue.Queue[_QueuedJob | None] = queue.Queue(maxsize=max_pending)
        self._jobs: dict[str, _QueuedJob] = {}
        self._lock = threading.RLock()
        self._closed = False
        self._worker = threading.Thread(
            target=self._worker_loop,
            name="local-render-queue-worker",
            daemon=True,
        )
        if start_worker:
            self._worker.start()

    @property
    def worker_count(self) -> int:
        return 1

    @property
    def is_closed(self) -> bool:
        with self._lock:
            return self._closed

    def _active_count(self) -> int:
        return sum(
            item.job["state"] in {"queued", "running"}
            for item in self._jobs.values()
        )

    def _persist(self, item: _QueuedJob) -> None:
        if self._job_directory is None:
            return
        destination = self._job_directory / f"{item.job['job_id']}.json"
        temporary = destination.with_name(f".{destination.name}.{uuid.uuid4().hex}.tmp")
        try:
            temporary.write_text(
                json.dumps(item.job, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
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
                "render job could not be persisted",
            ) from exc

    def _new_job(
        self,
        *,
        operation: str,
        revision_id: str,
        request_id: str,
        arguments: dict[str, Any],
    ) -> _QueuedJob:
        now = _utc_now()
        job = {
            "schema_version": JOB_SCHEMA_VERSION,
            "job_id": f"job-{uuid.uuid4().hex}",
            "request_id": request_id,
            "revision_id": revision_id,
            "operation": operation,
            "state": "queued",
            "created_at": now,
            "updated_at": now,
            "artifacts": [],
            "error": None,
        }
        return _QueuedJob(job, arguments, threading.Event(), threading.Event())

    def submit(
        self,
        operation: str,
        *,
        revision_id: str,
        request_id: str | None = None,
        arguments: Mapping[str, Any] | None = None,
        args: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Enqueue one allowlisted operation and return its typed job record."""

        if arguments is not None and args is not None:
            raise LocalRenderQueueError(
                "INVALID_JOB_REQUEST",
                "job arguments were supplied twice",
            )
        selected_arguments = arguments if arguments is not None else args
        if selected_arguments is None:
            selected_arguments = {}
        if not isinstance(selected_arguments, Mapping):
            raise LocalRenderQueueError(
                "INVALID_JOB_REQUEST",
                "job arguments must be an object",
            )
        if not isinstance(operation, str) or operation not in ALLOWED_OPERATIONS:
            raise OperationNotAllowedError(str(operation))
        if operation not in self.handlers:
            raise OperationNotAllowedError(operation)
        revision = _safe_id(revision_id, "revision_id")
        request = _safe_id(request_id or f"request-{uuid.uuid4().hex}", "request_id")
        copied_arguments = _json_copy(dict(selected_arguments))
        _reject_forbidden_keys(copied_arguments)

        item = self._new_job(
            operation=operation,
            revision_id=revision,
            request_id=request,
            arguments=copied_arguments,
        )
        with self._lock:
            if self._closed:
                raise QueueClosedError()
            if self._active_count() >= self.max_pending:
                raise QueueOverflowError()
            self._jobs[item.job["job_id"]] = item
            try:
                self._items.put_nowait(item)
                self._persist(item)
            except queue.Full as exc:
                self._jobs.pop(item.job["job_id"], None)
                raise QueueOverflowError() from exc
            except Exception:
                self._jobs.pop(item.job["job_id"], None)
                raise
        return self.get(item.job["job_id"])

    enqueue = submit

    def get(self, job_id: str) -> dict[str, Any]:
        with self._lock:
            item = self._jobs.get(job_id)
            if item is None:
                raise JobNotFoundError()
            return dict(item.job)

    get_job = get

    def cancel(self, job_id: str) -> dict[str, Any]:
        with self._lock:
            item = self._jobs.get(job_id)
            if item is None:
                raise JobNotFoundError()
            if item.job["state"] in TERMINAL_JOB_STATES:
                return dict(item.job)
            item.cancel_event.set()
            item.job["state"] = "cancelled"
            item.job["updated_at"] = _utc_now()
            self._persist(item)
            if item.job["state"] == "cancelled":
                item.finished.set()
            return dict(item.job)

    cancel_job = cancel

    def wait(self, job_id: str, timeout: float | None = None) -> dict[str, Any]:
        with self._lock:
            item = self._jobs.get(job_id)
            if item is None:
                raise JobNotFoundError()
            finished = item.finished
        if not finished.wait(timeout):
            raise TimeoutError("render job did not finish before timeout")
        return self.get(job_id)

    def stats(self) -> dict[str, int]:
        with self._lock:
            counts = {state: 0 for state in JOB_STATES}
            for item in self._jobs.values():
                counts[item.job["state"]] += 1
            return {"capacity": self.max_pending, **counts}

    def _mark_running(self, item: _QueuedJob) -> bool:
        with self._lock:
            if item.job["state"] != "queued":
                item.finished.set()
                return False
            item.job["state"] = "running"
            item.job["updated_at"] = _utc_now()
            self._persist(item)
            return True

    def _finish(
        self,
        item: _QueuedJob,
        *,
        state: str,
        artifacts: list[dict[str, str]] | None = None,
        error: Mapping[str, Any] | None = None,
    ) -> None:
        with self._lock:
            if item.job["state"] == "cancelled" and state != "cancelled":
                item.finished.set()
                return
            item.job["state"] = state
            item.job["updated_at"] = _utc_now()
            item.job["artifacts"] = list(artifacts or [])
            item.job["error"] = dict(error) if error is not None else None
            self._persist(item)
            item.finished.set()

    def _worker_loop(self) -> None:
        while True:
            item = self._items.get()
            if item is None:
                self._items.task_done()
                return
            try:
                if not self._mark_running(item):
                    continue
                context = JobContext(
                    job_id=item.job["job_id"],
                    request_id=item.job["request_id"],
                    revision_id=item.job["revision_id"],
                    operation=item.job["operation"],
                    cancel_event=item.cancel_event,
                    runtime_root=self.runtime_root,
                )
                context.raise_if_cancelled()
                result = _call_handler(
                    self.handlers[item.job["operation"]],
                    item.arguments,
                    context,
                )
                context.raise_if_cancelled()
                artifacts = _validate_handler_result(result)
                self._finish(item, state="succeeded", artifacts=artifacts)
            except JobCancelledError as exc:
                self._finish(
                    item,
                    state="cancelled",
                    error={
                        "code": exc.code,
                        "message": exc.message,
                        "details": {},
                        "request_id": item.job["request_id"],
                    },
                )
            except LocalRenderQueueError as exc:
                self._finish(
                    item,
                    state="failed",
                    error={
                        "code": exc.code,
                        "message": exc.message,
                        "details": dict(exc.details),
                        "request_id": item.job["request_id"],
                    },
                )
            except Exception:
                self._finish(
                    item,
                    state="failed",
                    error={
                        "code": "JOB_FAILED",
                        "message": "render operation failed",
                        "details": {},
                        "request_id": item.job["request_id"],
                    },
                )
            finally:
                self._items.task_done()

    def close(self, *, wait: bool = True) -> None:
        with self._lock:
            if self._closed:
                return
            self._closed = True
            for item in self._jobs.values():
                if item.job["state"] in {"queued", "running"}:
                    item.cancel_event.set()
                    item.job["state"] = "cancelled"
                    item.job["updated_at"] = _utc_now()
                    self._persist(item)
                    item.finished.set()
        if self._worker.is_alive():
            self._items.put(None)
            if wait:
                self._worker.join(timeout=5)

    shutdown = close

    def __enter__(self) -> "LocalRenderQueue":
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()


__all__ = [
    "ALLOWED_OPERATIONS",
    "JOB_SCHEMA_VERSION",
    "JOB_STATES",
    "JobCancelledError",
    "JobContext",
    "JobExecutionError",
    "JobNotFoundError",
    "LocalRenderQueue",
    "LocalRenderQueueError",
    "OperationNotAllowedError",
    "QueueClosedError",
    "QueueOverflowError",
    "run_typed_argv",
]
