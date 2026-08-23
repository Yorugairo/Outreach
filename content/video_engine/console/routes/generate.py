"""Generation request pack — compile and export, never call.

Mirrors the compile / record split ``pronunciation_dictionary`` established:
``compile_visual_prompt_pack`` builds the request and performs no network call;
the operator executes it in a browser generation session. The provider API
adapter is deferred until a provider and spend control are chosen, so nothing
in this module imports a provider client, reads an API key, or opens a socket.

The route computes no prompt of its own: ``visual_prompt_pack`` owns the fan-out
and the negative-prompt rule; this view renders the pack, offers it for copy and
for export, and states the delivery layout ``/intake`` can bind.
"""

from __future__ import annotations

import re
from pathlib import Path

from fastapi import APIRouter, Form, Query, Request
from fastapi.responses import HTMLResponse

from content.video_engine.src.services.artifact_io import write_artifact
from content.video_engine.src.services.delivery_intake import CLASS_DIMENSIONS
from content.video_engine.src.services.style_packs import StylePackError, load_registry
from content.video_engine.src.services.visual_prompt_pack import (
    DEFAULT_VARIANTS_PER_SLOT,
    VisualPromptPackError,
    compile_visual_prompt_pack,
)

router = APIRouter()

#: ``content/video_engine`` — this file is ``<engine>/console/routes/generate.py``.
_ENGINE_ROOT = Path(__file__).resolve().parents[2]

#: Exports land under a ``runtime/`` directory only, mirroring
#: ``composite_preview``'s refusal — a request pack is derived and disposable,
#: never a catalogue artifact.
EXPORT_SUBPATH = ("runtime", "generation-requests")

#: A bare filename: no separators, no traversal, nothing shell-hostile.
_SAFE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")

#: Kind delivery intake assigns an ungrouped manifest entry by default.
_DEFAULT_DELIVERY_KIND = "prop"


def _lanes() -> list[str]:
    """Lanes the registry knows. An empty list degrades to free-text entry."""

    try:
        return sorted(load_registry())
    except StylePackError:
        return []


def _error(request: Request, title: str, errors: list[str]) -> HTMLResponse:
    return request.app.state.templates.TemplateResponse(
        request=request,
        name="error.html",
        context={"title": title, "errors": errors},
        status_code=200,
    )


def _export_path(settings, name: str) -> Path:
    """Resolve the operator's filename under ``runtime/`` or refuse."""

    clean = name.strip()
    if not clean:
        raise VisualPromptPackError(["name the export file"])
    if not _SAFE_NAME.match(clean) or ".." in clean:
        raise VisualPromptPackError(
            [
                f"export name {clean!r} must be a bare filename "
                "(letters, digits, dot, dash, underscore); paths are refused"
            ]
        )
    if not clean.endswith(".json"):
        clean += ".json"

    root = settings.project_root if settings.project_root else _ENGINE_ROOT
    out = root.joinpath(*EXPORT_SUBPATH, clean).resolve()
    if "runtime" not in out.parts:
        raise VisualPromptPackError(
            [
                f"exports must live under a 'runtime' directory; got {out}. "
                "A request pack is derived and disposable, never a source artifact."
            ]
        )
    return out


def _delivery_plan(pack: dict) -> dict:
    """The folder layout ``/intake`` can scan once the batch is generated.

    ``delivery_intake`` binds by one ``*.manifest.json`` naming every file with
    its sha256, so the view states that convention rather than leaving the
    operator to reverse-engineer it from a rejection.
    """

    suffix = str(pack.get("coverage_hash") or "")[:8] or "batch"
    batch = f"{pack['lane']}-{suffix}"
    files = [
        f"{group['slot_id']}-v{index}.png"
        for group in pack["groups"]
        for index in range(int(pack["variants_per_slot"]))
    ]
    return {
        "batch": batch,
        "folder": f"review/{batch}/",
        "manifest": f"{batch}.manifest.json",
        "files": files,
        "kind": _DEFAULT_DELIVERY_KIND,
        "dimensions": sorted(CLASS_DIMENSIONS.items()),
    }


def _compiled_context(coverage: str, lane: str, variants: int) -> dict:
    """Compile the pack and everything the template shows about it."""

    pack = compile_visual_prompt_pack(coverage, lane=lane, variants_per_slot=variants)
    return {
        "pack": pack,
        "requested_generations": len(pack["groups"]) * pack["variants_per_slot"],
        "delivery": _delivery_plan(pack),
    }


@router.get("/generate", response_class=HTMLResponse)
def generate(
    request: Request,
    coverage: str | None = Query(default=None),
    lane: str = Query(default="stick_explainer"),
    variants: int = Query(default=DEFAULT_VARIANTS_PER_SLOT),
) -> HTMLResponse:
    templates = request.app.state.templates
    base = {
        "title": "Generate",
        "coverage": coverage or "",
        "lane": lane,
        "variants": variants,
        "lanes": _lanes(),
        "pack": None,
        "exported": None,
    }
    if not coverage:
        return templates.TemplateResponse(request=request, name="generate.html", context=base)

    try:
        compiled = _compiled_context(coverage, lane, variants)
    except (VisualPromptPackError, StylePackError) as exc:
        return _error(request, "Pack rejected", exc.errors)
    except ValueError as exc:
        return _error(request, "Pack rejected", [str(exc)])

    return templates.TemplateResponse(
        request=request, name="generate.html", context={**base, **compiled}
    )


@router.post("/generate/export", response_class=HTMLResponse)
def export(
    request: Request,
    coverage: str = Form(...),
    lane: str = Form(...),
    variants: int = Form(default=DEFAULT_VARIANTS_PER_SLOT),
    name: str = Form(...),
) -> HTMLResponse:
    templates = request.app.state.templates
    try:
        compiled = _compiled_context(coverage, lane, variants)
        path = _export_path(request.app.state.settings, name)
        write_artifact(path, compiled["pack"])
    except (VisualPromptPackError, StylePackError) as exc:
        return _error(request, "Export refused", exc.errors)
    except ValueError as exc:
        return _error(request, "Export refused", [str(exc)])

    return templates.TemplateResponse(
        request=request,
        name="generate.html",
        context={
            "title": "Generate",
            "coverage": coverage,
            "lane": lane,
            "variants": variants,
            "lanes": _lanes(),
            "exported": str(path),
            **compiled,
        },
    )
