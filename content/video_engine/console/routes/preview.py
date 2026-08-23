"""Motion preview — the console asks the render lanes, and implements nothing.

Two renderers already own motion, per the ownership table in
``19-HYPERFRAMES-LANE.md``: Remotion owns camera transforms and layer
composition (``editor/``, the ``EditorialMotion`` composition), and HyperFrames
owns motion units including ``animatic_preview`` — deterministic,
estimated-timing, and never publishable, which is exactly the right status for
a preview artifact.

A preview produced by any other engine could disagree with the delivered
video, so this module contains no camera, no easing, no timing arithmetic, and
never touches a layer's ``parallax_factor`` — the unit file carries it to the
lane untouched. A test greps this package to hold that true.

Renders run in a background thread so the console stays responsive; state is
polled, and failures surface the lane's own stderr verbatim.
"""

from __future__ import annotations

import subprocess
import sys
import threading
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Form, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse

router = APIRouter()

_REPO_ROOT = Path(__file__).resolve().parents[4]
_CLI = _REPO_ROOT / "content" / "video_engine" / "cli.py"

#: The two lane actions the console may trigger. Commands only — no behaviour.
_LANES = {
    "hyperframes": {
        "label": "HyperFrames animatic preview",
        "build": lambda unit, dry: [sys.executable, str(_CLI), "render-unit", unit]
        + (["--dry-run"] if dry else []),
        "needs_unit": True,
    },
    "remotion": {
        "label": "Remotion editor smoke",
        "build": lambda unit, dry: [sys.executable, str(_CLI), "verify-editor", "--smoke"],
        "needs_unit": False,
    },
}


def _run_command(cmd: list[str]) -> subprocess.CompletedProcess:
    """The only place a lane process starts. Tests monkeypatch this."""

    return subprocess.run(cmd, capture_output=True, text=True, cwd=_REPO_ROOT)


def _jobs(request: Request) -> dict[str, dict[str, Any]]:
    jobs = getattr(request.app.state, "motion_previews", None)
    if jobs is None:
        jobs = {}
        request.app.state.motion_previews = jobs
    return jobs


def _launch(jobs: dict[str, dict[str, Any]], key: str, cmd: list[str]) -> None:
    job = {"status": "running", "cmd": cmd, "stdout": "", "stderr": "", "returncode": None}
    jobs[key] = job

    def work() -> None:
        try:
            done = _run_command(cmd)
            job["stdout"] = done.stdout or ""
            job["stderr"] = done.stderr or ""
            job["returncode"] = done.returncode
            job["status"] = "done" if done.returncode == 0 else "failed"
        except Exception as exc:  # the lane could not even start
            job["stderr"] = f"{type(exc).__name__}: {exc}"
            job["status"] = "failed"

    threading.Thread(target=work, daemon=True).start()


@router.get("/preview/motion", response_class=HTMLResponse)
def motion(request: Request, unit: str = Query(default="")) -> HTMLResponse:
    templates = request.app.state.templates
    jobs = _jobs(request)
    key = unit or "remotion-smoke"
    return templates.TemplateResponse(
        request=request,
        name="motion.html",
        context={
            "title": "Motion preview",
            "unit": unit,
            "job": jobs.get(key),
            "lanes": {name: lane["label"] for name, lane in _LANES.items()},
            "pending": jobs.get(key, {}).get("status") == "running",
        },
    )


@router.post("/preview/motion")
def start_motion(
    request: Request,
    lane: str = Form(...),
    unit: str = Form(default=""),
    dry_run: bool = Form(default=False),
):
    templates = request.app.state.templates
    spec = _LANES.get(lane)
    if spec is None:
        return templates.TemplateResponse(
            request=request, name="error.html",
            context={"title": "Unknown lane", "errors": [f"no lane named {lane!r}"]},
            status_code=200,
        )
    if spec["needs_unit"]:
        if not unit:
            return templates.TemplateResponse(
                request=request, name="error.html",
                context={"title": "Missing unit", "errors": ["name a hyperframes unit JSON file"]},
                status_code=200,
            )
        if not Path(unit).exists():
            return templates.TemplateResponse(
                request=request, name="error.html",
                context={"title": "Unit not found", "errors": [f"no file at {unit}"]},
                status_code=200,
            )

    jobs = _jobs(request)
    key = unit or "remotion-smoke"
    if jobs.get(key, {}).get("status") == "running":
        # One render per unit at a time; the poll view shows the pending state.
        return RedirectResponse(url=f"/preview/motion?unit={unit}", status_code=303)

    _launch(jobs, key, spec["build"](unit, dry_run))
    return RedirectResponse(url=f"/preview/motion?unit={unit}", status_code=303)
