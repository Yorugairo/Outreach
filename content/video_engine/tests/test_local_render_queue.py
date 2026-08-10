from __future__ import annotations

import json
import threading
import time
from pathlib import Path

import pytest

from content.video_engine.src.services.local_render_queue import (
    JobCancelledError,
    LocalRenderQueue,
    OperationNotAllowedError,
    QueueOverflowError,
)


def _wait_for_started(event: threading.Event) -> None:
    assert event.wait(2), "queue worker did not start the test job"


def test_queue_is_single_worker_bounded_and_cancellable(tmp_path: Path) -> None:
    started = threading.Event()
    release = threading.Event()

    def blocking_handler(_arguments, context):
        started.set()
        while not release.wait(0.01):
            if context.cancellation_requested:
                raise JobCancelledError()
        return None

    render_queue = LocalRenderQueue(
        {"render_preview": blocking_handler},
        max_pending=1,
        runtime_root=tmp_path,
    )
    try:
        first = render_queue.submit(
            "render_preview",
            revision_id="revision-001",
            request_id="request-001",
        )
        _wait_for_started(started)
        assert render_queue.worker_count == 1

        with pytest.raises(QueueOverflowError):
            render_queue.submit(
                "render_preview",
                revision_id="revision-002",
                request_id="request-002",
            )

        cancelled = render_queue.cancel(first["job_id"])
        assert cancelled["state"] == "cancelled"
        release.set()
        assert render_queue.wait(first["job_id"], timeout=2)["state"] == "cancelled"
    finally:
        release.set()
        render_queue.close()


def test_queued_job_can_be_cancelled_without_running(tmp_path: Path) -> None:
    started = threading.Event()
    release = threading.Event()

    def blocking_handler(_arguments, context):
        started.set()
        while not release.wait(0.01):
            context.raise_if_cancelled()

    render_queue = LocalRenderQueue(
        {"render_preview": blocking_handler},
        max_pending=2,
        runtime_root=tmp_path,
    )
    try:
        running = render_queue.submit("render_preview", revision_id="revision-001")
        _wait_for_started(started)
        queued = render_queue.submit("render_preview", revision_id="revision-002")
        assert queued["state"] == "queued"
        assert render_queue.cancel(queued["job_id"])["state"] == "cancelled"
        release.set()
        assert render_queue.wait(running["job_id"], timeout=2)["state"] == "succeeded"
        assert render_queue.get(queued["job_id"])["state"] == "cancelled"
    finally:
        release.set()
        render_queue.close()


def test_success_and_failure_are_persisted_as_structured_jobs(tmp_path: Path) -> None:
    def success_handler(_arguments, _context):
        return {
            "artifacts": [
                {
                    "artifact_id": "preview",
                    "path": "results/preview.mp4",
                    "sha256": "a" * 64,
                }
            ]
        }

    def failure_handler(_arguments, _context):
        raise RuntimeError("do not disclose this path: C:/private")

    render_queue = LocalRenderQueue(
        {
            "render_preview": success_handler,
            "render_diagnostic": failure_handler,
        },
        max_pending=2,
        runtime_root=tmp_path,
    )
    try:
        succeeded = render_queue.submit("render_preview", revision_id="revision-001")
        failed = render_queue.submit("render_diagnostic", revision_id="revision-002")
        assert render_queue.wait(succeeded["job_id"], timeout=2)["state"] == "succeeded"
        failed_job = render_queue.wait(failed["job_id"], timeout=2)
        assert failed_job["state"] == "failed"
        assert failed_job["error"]["code"] == "JOB_FAILED"
        assert "C:/private" not in json.dumps(failed_job)
        for job_id in (succeeded["job_id"], failed["job_id"]):
            persisted = tmp_path / "jobs" / f"{job_id}.json"
            assert persisted.is_file()
            assert json.loads(persisted.read_text(encoding="utf-8"))["job_id"] == job_id
    finally:
        render_queue.close()


def test_unregistered_operation_and_command_arguments_fail_closed(tmp_path: Path) -> None:
    render_queue = LocalRenderQueue(
        {"render_preview": lambda _arguments, _context: None},
        runtime_root=tmp_path,
    )
    try:
        with pytest.raises(OperationNotAllowedError):
            render_queue.submit("run_shell", revision_id="revision-001")
        with pytest.raises(Exception, match="unsupported command field"):
            render_queue.submit(
                "render_preview",
                revision_id="revision-001",
                arguments={"command": "whoami"},
            )
    finally:
        render_queue.close()
