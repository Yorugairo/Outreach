"""Editor controls: Studio state, start/stop, deep links, headless renders.

Thin over ``editor_studio`` (lifecycle) and ``editor_render`` (headless lane).
Routes compute nothing: state comes from the service, links from one tested
helper, and a status GET constructs and writes nothing.

Deep links: verified against the installed pin (4.0.502), not assumed —
``@remotion/studio/dist/helpers/url-state.js`` routes the SPA by
``window.location.pathname``, so ``http://127.0.0.1:<port>/<CompositionId>``
selects a composition. Props-in-URL has no evidence in the pin and is not
offered.
"""

from __future__ import annotations

import threading
from typing import Any, Mapping

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from content.video_engine.src.services import editor_studio
from content.video_engine.src.services.editor_studio import EditorStudioError

router = APIRouter()


def studio_link(state: Mapping[str, Any], composition_id: str) -> str | None:
    """The deepest supported Studio URL, or None while not serving.

    Link construction lives here and only here — templates receive finished
    URLs. The composition path is the verified 4.0.502 scheme; an empty id
    degrades to the Studio root.
    """

    if state.get("state") != "serving" or not state.get("url"):
        return None
    composition = str(composition_id or "").strip("/")
    return f"{state['url']}/{composition}" if composition else str(state["url"])


def _view(request: Request, status_code: int = 200) -> HTMLResponse:
    state = editor_studio.status()
    renders = getattr(request.app.state, "editor_renders", {})
    return request.app.state.templates.TemplateResponse(
        request=request,
        name="editor.html",
        context={
            "title": "Editor",
            "studio": state,
            "studio_root": studio_link(state, ""),
            "renders": dict(renders),
        },
        status_code=status_code,
    )


@router.get("/editor", response_class=HTMLResponse)
def editor(request: Request) -> HTMLResponse:
    return _view(request)


@router.post("/editor/start", response_class=HTMLResponse)
def start(request: Request) -> HTMLResponse:
    try:
        editor_studio.start()
    except EditorStudioError as exc:
        return request.app.state.templates.TemplateResponse(
            request=request, name="error.html",
            context={"title": "Studio start failed", "errors": exc.errors},
            status_code=200,
        )
    return RedirectResponse(url="/editor", status_code=303)


@router.post("/editor/stop", response_class=HTMLResponse)
def stop(request: Request) -> HTMLResponse:
    try:
        editor_studio.stop()
    except EditorStudioError as exc:
        return request.app.state.templates.TemplateResponse(
            request=request, name="error.html",
            context={"title": "Studio stop failed", "errors": exc.errors},
            status_code=200,
        )
    return RedirectResponse(url="/editor", status_code=303)


@router.post("/editor/render", response_class=HTMLResponse)
def render(request: Request, composition: str = Form(...), props_path: str = Form(default="")) -> HTMLResponse:
    """Operator-triggered headless render; threaded pending state (preview.py pattern)."""

    from content.video_engine.src.services import editor_render

    if not hasattr(request.app.state, "editor_renders"):
        request.app.state.editor_renders = {}
    jobs = request.app.state.editor_renders
    jobs[composition] = {"status": "running"}

    def _run() -> None:
        try:
            result = editor_render.render_headless(composition, props_path or None)
            jobs[composition] = {"status": "done", **result}
        except editor_render.EditorRenderError as exc:
            jobs[composition] = {"status": "failed", "errors": exc.errors}

    threading.Thread(target=_run, daemon=True).start()
    return RedirectResponse(url="/editor", status_code=303)
