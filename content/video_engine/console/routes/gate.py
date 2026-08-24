"""The paid gate's console surface — the only write route about money.

Kept out of ``runs.py`` deliberately: the runs view holds a structural
read-only invariant (P15), and a release button is precisely the kind of
control that must not creep into a monitoring surface. Machine-channel
release lives here; the Telegram channel lives in the watchdog package.
"""

from __future__ import annotations

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

router = APIRouter()


@router.post("/gate/release", response_class=HTMLResponse)
def release(request: Request, job_id: str = Form(...)) -> HTMLResponse:
    """Machine-channel release: the on-machine half of the dual-mode gate."""

    from content.video_engine.src.services.paid_gate import PaidGateError, release_job

    try:
        release_job(job_id, channel="machine")
    except PaidGateError as exc:
        return request.app.state.templates.TemplateResponse(
            request=request, name="error.html",
            context={"title": "Release refused", "errors": exc.errors}, status_code=200,
        )
    return RedirectResponse(url="/runs", status_code=303)
