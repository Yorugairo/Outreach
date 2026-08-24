"""Generation request pack — compile and export, never call.

Mirrors the compile / record split ``pronunciation_dictionary`` established:
``compile_visual_prompt_pack`` builds the request and performs no network call.
The provider question is settled by P17: generation runs on the operator's
subscription agents via **claims** — a compiled pack opens a claim whose work
order the agent follows, delivering into a review-class folder for /intake.
No provider client, no API key, no socket in this module; the paid gate exists
elsewhere and only ever for audio/video, never images.

The route computes no prompt of its own: ``visual_prompt_pack`` owns the fan-out
and the negative-prompt rule; this view renders the pack, offers it for copy and
for export, and states the delivery layout ``/intake`` can bind.
"""

from __future__ import annotations

import re
from pathlib import Path

from fastapi import APIRouter, Form, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from content.video_engine.src.services import paths as _paths
from content.video_engine.src.services.artifact_io import write_artifact
from content.video_engine.src.services.generation_claim import (
    GenerationClaimError,
    close_claim,
    list_claims,
    load_claim,
    open_claim,
    render_work_order,
)
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
#: never a catalogue artifact. The subpath literal is owned by the path
#: contract; this is a re-export for callers and tests.
EXPORT_SUBPATH = _paths.EXPORT_SUBPATH

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
        "claims": list_claims(),
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


def _slot_id(text: str) -> str:
    """A pack slot id as a claim asset id: lowercase kebab, nothing else."""

    import re as _re

    return _re.sub(r"[^a-z0-9-]+", "-", str(text).lower()).strip("-")


@router.post("/generate/claims/open", response_class=HTMLResponse)
def claim_open(
    request: Request,
    claim_id: str = Form(...),
    style_family: str = Form(...),
    coverage: str = Form(default=""),
    lane: str = Form(default=""),
    variants: int = Form(default=DEFAULT_VARIANTS_PER_SLOT),
    slots_json: str = Form(default=""),
    reference_images: str = Form(default=""),
) -> HTMLResponse:
    """Open a claim from a compiled pack, or from explicit slots.

    The route computes no prompt of its own: pack slots carry prompts composed
    by ``visual_prompt_pack``; explicit slots carry the operator's.
    """

    settings = request.app.state.settings
    if not settings.project_root:
        return _error(request, "Claim refused", [
            "no project root configured; set VIDEO_ENGINE_PROJECT_ROOT"
        ])
    try:
        if coverage:
            pack = compile_visual_prompt_pack(coverage, lane=lane, variants_per_slot=variants)
            slots = [
                {
                    "asset_id": _slot_id(group["slot_id"]),
                    "kind": _DEFAULT_DELIVERY_KIND,
                    "prompt": group["prompt"],
                    "semantic": group.get("visual_intent") or group.get("narration_excerpt") or "",
                }
                for group in pack["groups"]
            ]
        elif slots_json.strip():
            import json as _json

            slots = _json.loads(slots_json)
        else:
            return _error(request, "Claim refused", [
                "give a coverage artifact to compile, or explicit slots JSON"
            ])
        references = [line.strip() for line in reference_images.splitlines() if line.strip()]
        claim = open_claim(
            settings.project_root,
            claim_id=claim_id.strip(),
            style_family=style_family.strip(),
            slots=slots,
            reference_images=references,
        )
    except (GenerationClaimError, VisualPromptPackError, StylePackError) as exc:
        return _error(request, "Claim refused", exc.errors)
    except ValueError as exc:
        return _error(request, "Claim refused", [str(exc)])
    return RedirectResponse(url=f"/generate/claims/{claim['claim_id']}", status_code=303)


@router.get("/generate/claims/{claim_id}", response_class=HTMLResponse)
def claim_view(request: Request, claim_id: str) -> HTMLResponse:
    try:
        claim = load_claim(claim_id)
    except GenerationClaimError as exc:
        return _error(request, "No such claim", exc.errors)
    return request.app.state.templates.TemplateResponse(
        request=request,
        name="claim.html",
        context={
            "title": f"Claim {claim_id}",
            "claim": claim,
            "work_order": render_work_order(claim),
        },
    )


@router.post("/generate/claims/close", response_class=HTMLResponse)
def claim_close(request: Request, claim_id: str = Form(...)) -> HTMLResponse:
    try:
        close_claim(claim_id)
    except GenerationClaimError as exc:
        return _error(request, "Close refused", exc.errors)
    return RedirectResponse(url="/generate", status_code=303)
