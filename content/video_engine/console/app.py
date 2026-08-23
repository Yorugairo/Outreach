"""Local operator console.

A thin window onto artifacts that already live on disk. Every guard belongs to a
service in ``content/video_engine/src/services``; routes call a service, get a
structured result, and render it. A rule enforced only in a template is a bug,
because the CLI would not enforce it.

Binds to loopback and reads nothing from the network.
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from content.video_engine.console.routes import board as board_routes
from content.video_engine.console.routes import catalog as catalog_routes
from content.video_engine.console.routes import generate as generate_routes
from content.video_engine.console.routes import intake as intake_routes
from content.video_engine.console.routes import preview as preview_routes
from content.video_engine.console.routes import runs as runs_routes
from content.video_engine.console.settings import ConsoleSettings, load_settings

_CONSOLE_ROOT = Path(__file__).resolve().parent
TEMPLATE_DIR = _CONSOLE_ROOT / "templates"
STATIC_DIR = _CONSOLE_ROOT / "static"

#: Loopback only. This console has no authentication because it is never exposed.
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765


def create_app(settings: ConsoleSettings | None = None) -> FastAPI:
    """Build the console application.

    Accepts settings so tests can point at a fixture catalogue without touching
    the environment.
    """

    app = FastAPI(title="Video Engine Console", docs_url=None, redoc_url=None)
    app.state.settings = settings if settings is not None else load_settings()
    app.state.templates = Jinja2Templates(directory=str(TEMPLATE_DIR))

    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
    app.include_router(catalog_routes.router)
    app.include_router(board_routes.router)
    app.include_router(intake_routes.router)
    app.include_router(generate_routes.router)
    app.include_router(preview_routes.router)
    app.include_router(runs_routes.router)

    @app.exception_handler(404)
    async def not_found(request: Request, exc: object) -> HTMLResponse:  # noqa: ARG001
        return app.state.templates.TemplateResponse(
            request=request,
            name="error.html",
            context={
                "title": "Not found",
                "errors": [f"No route for {request.url.path}"],
            },
            status_code=404,
        )

    return app
