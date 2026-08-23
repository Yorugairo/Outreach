"""Catalogue read views.

The route computes nothing. ``asset_catalog.load_catalog`` validates, applies the
scale and depth-plane guards, and raises ``AssetCatalogError`` carrying its own
messages — the view renders those messages verbatim so the console and the CLI
report a bad catalogue identically.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from content.video_engine.src.services.asset_catalog import (
    AssetCatalogError,
    load_catalog,
)

router = APIRouter()

#: Assets the render lane may use. Anything else is provisional by definition.
_PROMOTED_REVIEW_STATE = "approved_reusable"


def _summarise(assets: list[dict[str, Any]]) -> dict[str, Any]:
    """Counts the operator needs before reading a single row."""

    promoted = [a for a in assets if a.get("render_eligible") is True]
    layered = [a for a in assets if a.get("layers")]
    return {
        "total": len(assets),
        "render_eligible": len(promoted),
        "review_only": len(assets) - len(promoted),
        "layered": len(layered),
        "style_versions": sorted({str(a.get("style_version")) for a in assets if a.get("style_version")}),
    }


@router.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    return catalog(request)


@router.get("/catalog", response_class=HTMLResponse)
def catalog(request: Request) -> HTMLResponse:
    templates = request.app.state.templates
    settings = request.app.state.settings

    if not settings.is_configured:
        return templates.TemplateResponse(
            request=request,
            name="empty.html",
            context={"title": "No catalogue configured"},
            status_code=200,
        )

    if not settings.catalog_path.exists():
        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={
                "title": "Catalogue not found",
                "errors": [f"No file at {settings.catalog_path}"],
            },
            status_code=200,
        )

    try:
        payload = load_catalog(settings.catalog_path)
    except AssetCatalogError as exc:
        # The service's own errors, verbatim. The console never restates a guard.
        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={"title": "Catalogue rejected", "errors": exc.errors},
            status_code=200,
        )

    assets = list(payload.get("assets") or [])
    return templates.TemplateResponse(
        request=request,
        name="catalog.html",
        context={
            "title": "Catalogue",
            "catalog_path": str(settings.catalog_path),
            "channel_id": payload.get("channel_id"),
            "style_families": payload.get("style_families") or {},
            "summary": _summarise(assets),
            "assets": assets,
        },
    )
