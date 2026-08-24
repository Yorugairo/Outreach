"""Interactive scene board.

A thin window onto ``scene_board.build_board``: the service assembles the board
with its auto-selected defaults and exception flags; this module renders it and
records operator overrides through ``scene_selection.record_scene_selection``.
No route writes a board or review artifact directly — every recorded byte goes
through the service that owns the contract, so the console and
``cli.py record-scene-selection`` cannot drift apart.

The board is built from five artifacts. Rather than five query parameters, the
operator names a **job directory** and the artifacts are found by the
conventional filenames the pipeline already writes:

- ``director_brief.json`` and ``source_attestation.json`` (``script_ingest``)
- ``canonical_coverage.json`` or ``provisional_coverage.json`` (coverage;
  canonical wins when both exist)
- ``visual_prompt_pack.json`` (``visual_prompt_pack``)
- ``generated_visuals/candidate_batch.json`` or ``candidate_batch.json``

Operator choices are held server-side per job — the same in-memory pattern as
triage — and every change is re-recorded in full through the service, so the
review on disk always reflects the current state of the board.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping
from urllib.parse import quote

from fastapi import APIRouter, Form, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from content.video_engine.src.services.scene_board import (
    _EXCEPTION_REASONS,
    SceneBoardError,
    build_board,
    render_board_html,
)
from content.video_engine.src.services.scene_selection import (
    SceneSelectionError,
    record_scene_selection,
)

router = APIRouter()


def _editor_url() -> str | None:
    """Deep link into Studio's EditorialMotion, only while it serves."""

    from content.video_engine.console.routes.editor import studio_link
    from content.video_engine.src.services import editor_studio

    return studio_link(editor_studio.status(), "EditorialMotion")

#: Coverage candidates, most authoritative first. Canonical timing beats the
#: word-count estimate when a job carries both.
COVERAGE_FILENAMES = ("canonical_coverage.json", "provisional_coverage.json")

#: Candidate-batch locations, the run agents' path first.
BATCH_FILENAMES = ("generated_visuals/candidate_batch.json", "candidate_batch.json")

BRIEF_FILENAME = "director_brief.json"
ATTESTATION_FILENAME = "source_attestation.json"
PACK_FILENAME = "visual_prompt_pack.json"

#: Where the recorded review lands, relative to the job directory. The service
#: writes ``asset_selection_review.json`` and ``video_intents.json`` here.
SELECTION_SUBDIR = "selection"

#: The existing warning carried by ``render_board_html`` for estimated timing.
ESTIMATED_TIMING_WARNING = (
    "Timing is estimated from word count. Valid for layout and slot counting; "
    "the render clock still comes from audio."
)


def _first_existing(job: Path, names: tuple[str, ...]) -> Path | None:
    for name in names:
        candidate = job / name
        if candidate.is_file():
            return candidate
    return None


def resolve_artifacts(job: Path) -> dict[str, Path]:
    """Map the five board inputs to files under ``job``, or raise naming every gap."""

    found: dict[str, Path] = {}
    missing: list[str] = []
    for key, names in (
        ("brief", (BRIEF_FILENAME,)),
        ("attestation", (ATTESTATION_FILENAME,)),
        ("coverage", COVERAGE_FILENAMES),
        ("pack", (PACK_FILENAME,)),
        ("batch", BATCH_FILENAMES),
    ):
        path = _first_existing(job, names)
        if path is None:
            missing.append(f"{key}: expected one of {', '.join(names)}")
        else:
            found[key] = path
    if missing:
        raise SceneBoardError([f"{job}: no {entry}" for entry in missing])
    return found


def build_board_for(job: Path) -> dict[str, Any]:
    """Assemble the board from the job directory's conventional artifacts."""

    if not job.is_dir():
        raise SceneBoardError([f"job directory not found: {job}"])
    paths = resolve_artifacts(job)
    return build_board(
        coverage=paths["coverage"],
        pack=paths["pack"],
        batch=paths["batch"],
        brief=paths["brief"],
        attestation=paths["attestation"],
    )


def _store(request: Request) -> dict[str, dict[str, Any]]:
    """Server-side operator choices per job, mirroring the triage session pattern."""

    store = getattr(request.app.state, "board_selections", None)
    if store is None:
        store = {}
        request.app.state.board_selections = store
    return store


def _session(store: Mapping[str, dict[str, Any]], job: Path) -> dict[str, Any]:
    return store.get(str(job), {"choices": {}, "last_record": None, "reviewed_by": ""})


def order_slots(board: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Flagged first, builder order preserved within each band.

    The same partition ``render_board_html`` applies; the console must not
    invent a different ordering.
    """

    rows = [dict(row) for row in board.get("slots") or []]
    flagged = [row for row in rows if row.get("exceptions")]
    clean = [row for row in rows if not row.get("exceptions")]
    return flagged + clean


def _error(request: Request, title: str, errors: list[str]) -> HTMLResponse:
    return request.app.state.templates.TemplateResponse(
        request=request,
        name="error.html",
        context={"title": title, "errors": errors},
        status_code=200,
    )


@router.get("/board", response_class=HTMLResponse)
def board(request: Request, job: str | None = Query(default=None)) -> HTMLResponse:
    templates = request.app.state.templates
    if not job:
        return templates.TemplateResponse(
            request=request,
            name="board.html",
            context={"title": "Board", "board": None, "job": "", "editor_url": _editor_url()},
        )

    job_dir = Path(job).expanduser()
    try:
        payload = build_board_for(job_dir)
    except (SceneBoardError, ValueError) as exc:
        errors = getattr(exc, "errors", None) or [str(exc)]
        return _error(request, "Board unavailable", list(errors))

    session = _session(_store(request), job_dir)
    return templates.TemplateResponse(
        request=request,
        name="board.html",
        context={
            "title": "Board",
            "editor_url": _editor_url(),
            "job": str(job_dir),
            "job_q": quote(str(job_dir)),
            "board": payload,
            "slots": order_slots(payload),
            "choices": session["choices"],
            "last_record": session["last_record"],
            "reviewed_by": session["reviewed_by"] or "console-operator",
            "reasons": _EXCEPTION_REASONS,
            "timing_warning": ESTIMATED_TIMING_WARNING,
        },
    )


@router.get("/board/static", response_class=HTMLResponse)
def board_static(request: Request, job: str = Query(...)) -> HTMLResponse:
    """The unchanged ``render_board_html`` page, for offline sharing.

    Byte-identical to what ``cli.py render-scene-board`` writes as
    ``board/index.html``; candidate images resolve when the page is saved next
    to the job's ``assets/`` directory.
    """

    try:
        payload = build_board_for(Path(job).expanduser())
    except (SceneBoardError, ValueError) as exc:
        errors = getattr(exc, "errors", None) or [str(exc)]
        return _error(request, "Board unavailable", list(errors))
    return HTMLResponse(render_board_html(payload))


@router.post("/board/select")
def select(
    request: Request,
    job: str = Form(...),
    slot_id: str = Form(...),
    candidate_id: str = Form(...),
    reviewed_by: str = Form(...),
):
    """Record one changed selection through the ``scene_selection`` service.

    The full operator payload — every choice held for this job — is
    re-reconciled against the board and re-recorded, so a bad choice is
    rejected by the service before anything is written and the review on disk
    never lags the screen.
    """

    job_dir = Path(job).expanduser()
    try:
        payload = build_board_for(job_dir)
    except (SceneBoardError, ValueError) as exc:
        errors = getattr(exc, "errors", None) or [str(exc)]
        return _error(request, "Board unavailable", list(errors))

    store = _store(request)
    session = _session(store, job_dir)
    # Immutable update: the held choices are only replaced after the service
    # accepts and records them.
    attempted = {**session["choices"], slot_id: candidate_id}
    operator_payload = {
        "schema_version": "scene_board_selection.v1",
        "selections": [
            {"slot_id": sid, "candidate_id": cid} for sid, cid in sorted(attempted.items())
        ],
    }

    try:
        summary = record_scene_selection(
            board=payload,
            output_dir=job_dir / SELECTION_SUBDIR,
            reviewed_by=reviewed_by,
            operator_payload=operator_payload,
        )
    except SceneSelectionError as exc:
        return _error(request, "Selection rejected", exc.errors)

    store[str(job_dir)] = {
        "choices": attempted,
        "last_record": summary,
        "reviewed_by": reviewed_by,
    }
    return RedirectResponse(
        url=f"/board?job={quote(str(job_dir))}#slot-{quote(slot_id)}", status_code=303
    )
