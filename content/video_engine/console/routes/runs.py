"""Runs and status view — strictly read-only.

Jobs live on disk under ``runtime/jobs/`` and are owned by
``FileBackedVideoJobRepository``. This module reads through that repository so the
console and ``cli.py status`` see byte-identical state; it never parses ``job.json``
itself and never writes.

**Read-only is structural, not a promise.** The router exposes ``GET`` only, and the
directory is probed with ``exists()`` before the repository is constructed —
``FileBackedVideoJobRepository.__init__`` calls ``mkdir``, so an absent runs
directory must never reach it. Rendering the runs page creates nothing.

**The exception vocabulary is derived, not persisted.** Nothing in the engine ever
writes ``degraded``: run status is one of ``queued``, ``running``,
``awaiting_*``, ``failed``, ``packaged``, ``published``, and a stage event is one
of ``running``, ``completed``, ``failed``, ``awaiting_approval``. This module maps
that recorded state onto the plan's three-way ``fail`` / ``flag`` / ``clean``
encoding and states the mapping in one place. It is a presentation classification
over recorded facts, not a new guard — no verdict here can contradict a service,
because no service owns this question yet.

The flagged-first ordering mirrors ``scene_board.render_board_html``, which
partitions ``flagged + clean`` at the view layer and preserves the builder's order
within each group. The same shape is used here over the repository's recency order.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from content.video_engine.src.services import paths as _paths
from content.video_engine.src.models import VideoRun, VideoStageEvent
from content.video_engine.src.repositories.file_repository import (
    FileBackedVideoJobRepository,
)

router = APIRouter()

#: ``content/video_engine`` — this file is ``<engine>/console/routes/runs.py``.
_ENGINE_ROOT = Path(__file__).resolve().parents[2]

#: Where the pipeline writes jobs, relative to a project root.
RUNS_SUBPATH = _paths.RUNS_SUBPATH

#: Fallback when no project root is configured. Must equal
#: ``cli.DEFAULT_ARTIFACT_ROOT``; a test asserts the two have not drifted.
DEFAULT_RUNS_DIR = _ENGINE_ROOT.joinpath(*RUNS_SUBPATH)

#: Stage-event status meaning the stage recorded a failure.
EVENT_FAILED = "failed"
#: Stage-event status meaning the stage stopped and is waiting on a human.
EVENT_AWAITING_APPROVAL = "awaiting_approval"
#: Run status meaning the pipeline gave up.
RUN_FAILED = "failed"
#: Prefix of every run status that parks a run on a human gate.
RUN_AWAITING_PREFIX = "awaiting_"

#: The five gate fields on ``VideoRun``, and the only value that clears one.
GATE_FIELDS = (
    "research_gate_status",
    "asset_gate_status",
    "visual_gate_status",
    "gate_a_status",
    "gate_b_status",
)
GATE_APPROVED = "approved"

SEVERITY_FAIL = "fail"
SEVERITY_FLAG = "flag"
SEVERITY_CLEAN = "clean"

#: Ordering rank. Exceptions first, worst first — the scene board's rule.
SEVERITY_ORDER = (SEVERITY_FAIL, SEVERITY_FLAG, SEVERITY_CLEAN)

#: Reasons that make a job a hard failure rather than something merely parked.
FAIL_REASONS = frozenset({"run_failed", "run_error_text", "stage_failed"})

#: Status is never colour alone: the chip class carries the glyph and colour, the
#: label carries text that survives greyscale.
SEVERITY_CHIP = {
    SEVERITY_FAIL: "chip-fail",
    SEVERITY_FLAG: "chip-flag",
    SEVERITY_CLEAN: "chip-clean",
}
SEVERITY_LABEL = {
    SEVERITY_FAIL: "FAIL",
    SEVERITY_FLAG: "FLAG",
    SEVERITY_CLEAN: "OK",
}


def resolve_runs_dir(settings: Any) -> Path:
    """Where this console reads jobs from.

    Injectable in three ways, most explicit first:

    1. ``settings.runs_dir`` — honoured if ``ConsoleSettings`` carries one. It does
       not today; reading it through ``getattr`` means adding the field later
       takes effect here with no change to this module.
    2. ``settings.project_root`` — the configured project's ``runtime/jobs``.
    3. ``DEFAULT_RUNS_DIR`` — the engine's own runtime directory, which is where
       the CLI writes when it is given no artifact root.

    Never raises and never creates anything. An unconfigured console still
    resolves to a real path, so the view can render an empty state rather than a
    configuration error.
    """

    configured = getattr(settings, "runs_dir", None)
    if configured:
        return Path(configured).expanduser()

    project_root = getattr(settings, "project_root", None)
    if project_root is not None:
        return Path(project_root).expanduser().joinpath(*RUNS_SUBPATH)

    return DEFAULT_RUNS_DIR


def pending_gates(run: VideoRun) -> list[str]:
    """Gates still holding this run. The console displays them and never moves one."""

    return [
        field.removesuffix("_status")
        for field in GATE_FIELDS
        if getattr(run, field, None) != GATE_APPROVED
    ]


def exception_reasons(run: VideoRun, events: list[VideoStageEvent]) -> list[str]:
    """Why this job needs an operator, in the scene board's sorted-set shape."""

    reasons: set[str] = set()

    if run.status == RUN_FAILED:
        reasons.add("run_failed")
    if run.error_text:
        reasons.add("run_error_text")
    if str(run.status).startswith(RUN_AWAITING_PREFIX):
        reasons.add("awaiting_gate")

    for event in events:
        if event.status == EVENT_FAILED:
            reasons.add("stage_failed")
        elif event.status == EVENT_AWAITING_APPROVAL:
            reasons.add("awaiting_approval")

    return sorted(reasons)


def severity_for(reasons: list[str]) -> str:
    """``fail`` beats ``flag`` beats ``clean``. A job is only clean with no reasons."""

    if not reasons:
        return SEVERITY_CLEAN
    if FAIL_REASONS.intersection(reasons):
        return SEVERITY_FAIL
    return SEVERITY_FLAG


def stage_failures(events: list[VideoStageEvent]) -> list[dict[str, Any]]:
    """Every failed stage event, carrying its own recorded text.

    ``error_text`` is passed through untouched. A failure with no recorded text is
    reported as having none rather than being given an invented message.
    """

    return [
        {
            "stage_name": event.stage_name,
            "status": event.status,
            "error_text": event.error_text,
            "created_at": event.created_at,
        }
        for event in events
        if event.status == EVENT_FAILED
    ]


def build_job_view(run: VideoRun, events: list[VideoStageEvent]) -> dict[str, Any]:
    """One immutable row of the runs table. Pure: reads nothing, writes nothing."""

    reasons = exception_reasons(run, events)
    severity = severity_for(reasons)
    latest = events[-1] if events else None

    return {
        "id": run.id,
        "source_ref": run.source_ref,
        "status": run.status,
        "current_stage": run.current_stage,
        "latest_event_stage": latest.stage_name if latest is not None else None,
        "latest_event_status": latest.status if latest is not None else None,
        "event_count": len(events),
        "updated_at": run.updated_at,
        "pending_gates": pending_gates(run),
        "exceptions": reasons,
        "failures": stage_failures(events),
        "run_error_text": run.error_text,
        "severity": severity,
        "chip_class": SEVERITY_CHIP[severity],
        "chip_label": SEVERITY_LABEL[severity],
    }


def order_jobs(jobs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Exception-first, stable within each band.

    A partition rather than a sort, matching ``scene_board.render_board_html``:
    the repository's recency order survives inside every band.
    """

    return [job for band in SEVERITY_ORDER for job in jobs if job["severity"] == band]


def summarise(jobs: list[dict[str, Any]]) -> dict[str, Any]:
    """Counts the operator needs before reading a single row."""

    return {
        "total": len(jobs),
        "failed": sum(1 for job in jobs if job["severity"] == SEVERITY_FAIL),
        "flagged": sum(1 for job in jobs if job["severity"] == SEVERITY_FLAG),
        "clean": sum(1 for job in jobs if job["severity"] == SEVERITY_CLEAN),
        "events": sum(job["event_count"] for job in jobs),
    }


def load_job_views(runs_dir: Path) -> list[dict[str, Any]]:
    """Read every job through the repository that owns the on-disk format.

    The caller guarantees ``runs_dir`` exists, so the repository's ``mkdir`` is a
    no-op and this stays a pure read.
    """

    repository = FileBackedVideoJobRepository(runs_dir)
    return [
        build_job_view(run, repository.list_stage_events(run.id))
        for run in repository.list_runs()
    ]


def _editor_url() -> str | None:
    """Deep link into Studio, only while it serves (read-only probe)."""

    from content.video_engine.console.routes.editor import studio_link
    from content.video_engine.src.services import editor_studio

    return studio_link(editor_studio.status(), "EditorialMotion")


def _paid_jobs() -> list[dict]:
    """Pending paid work waiting at the gate; releasing is a POST, never a GET."""

    from content.video_engine.src.services.paid_gate import list_jobs

    return list_jobs()


@router.get("/runs", response_class=HTMLResponse)
def runs(request: Request) -> HTMLResponse:
    templates = request.app.state.templates
    runs_dir = resolve_runs_dir(request.app.state.settings)

    if not runs_dir.is_dir():
        # Absent is not an error: a project that has never been run has no jobs.
        return templates.TemplateResponse(
            request=request,
            name="runs.html",
            context={"title": "Runs", "runs_dir": str(runs_dir), "jobs": [],
                     "summary": None, "paid_jobs": _paid_jobs(),
                     "editor_url": _editor_url()},
        )

    try:
        jobs = load_job_views(runs_dir)
    except (OSError, TypeError, ValueError) as exc:
        # VideoRun(**payload) is strict, so a malformed job.json raises TypeError
        # and bad JSON raises ValueError. Report what was raised, not a traceback.
        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={
                "title": "Jobs unreadable",
                "errors": [f"{runs_dir}: {exc}"],
            },
            status_code=200,
        )

    return templates.TemplateResponse(
        request=request,
        name="runs.html",
        context={
            "title": "Runs",
            "runs_dir": str(runs_dir),
            "jobs": order_jobs(jobs),
            "summary": summarise(jobs),
            "paid_jobs": _paid_jobs(),
            "editor_url": _editor_url(),
        },
    )

