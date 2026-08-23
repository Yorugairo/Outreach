"""Delivery intake views.

The route scans nothing itself: ``delivery_intake`` finds the manifest,
normalises it, and produces the verdicts; the view renders them. Service errors
reach the operator verbatim.
"""

from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import quote

from fastapi import APIRouter, Form, Query, Request
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse

from content.video_engine.console.triage import PROMOTE, REJECT, SKIP, TriageError, TriageStore
from content.video_engine.src.services.asset_catalog import (
    AssetCatalogError,
    register_assets,
)
from content.video_engine.src.services.composite_preview import (
    CompositePreviewError,
    render_composite,
)
from content.video_engine.src.services.delivery_intake import (
    DeliveryIntakeError,
    load_delivery,
    scan_delivery,
)

router = APIRouter()

#: Kinds whose default stage view is a composited frame, not a bare thumbnail.
_COMPOSITABLE = {"actor", "prop", "mechanism", "cast_board"}

_ENGINE_RUNTIME = Path(__file__).resolve().parents[2] / "runtime" / "console-previews"


def _store(request: Request) -> TriageStore:
    store = getattr(request.app.state, "triage", None)
    if store is None:
        store = TriageStore()
        request.app.state.triage = store
    return store


def _families(settings) -> dict | None:
    if settings.is_configured and settings.catalog_path.exists():
        return json.loads(settings.catalog_path.read_text(encoding="utf-8")).get("style_families")
    return None


def _catalog_worlds(settings) -> list[dict]:
    """Worlds a triage stage can composite against: placed, and present on disk."""

    if not (settings.is_configured and settings.catalog_path.exists() and settings.project_root):
        return []
    payload = json.loads(settings.catalog_path.read_text(encoding="utf-8"))
    worlds = []
    for asset in payload.get("assets") or []:
        if asset.get("kind") in {"world", "world_board"} and asset.get("placement"):
            if (settings.project_root / str(asset.get("path"))).exists():
                worlds.append(asset)
    return worlds


def _delivery_asset(session, asset_id: str) -> dict:
    for row in session.report["assets"]:
        if row["asset_id"] == asset_id:
            return row
    raise DeliveryIntakeError([f"{asset_id!r} is not in this delivery"])


@router.get("/intake", response_class=HTMLResponse)
def intake(request: Request, delivery: str | None = Query(default=None)) -> HTMLResponse:
    templates = request.app.state.templates
    settings = request.app.state.settings

    if not delivery:
        return templates.TemplateResponse(
            request=request,
            name="intake.html",
            context={"title": "Intake", "report": None, "delivery": ""},
        )

    try:
        loaded = load_delivery(delivery)
        # Families come from the catalogue when one is configured; a scan
        # without a catalogue still works, with the style check family-blind.
        families = _families(settings)
        report = scan_delivery(
            loaded["assets"],
            delivery_root=Path(delivery),
            style_families=families,
        )
    except DeliveryIntakeError as exc:
        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={"title": "Delivery rejected", "errors": exc.errors},
            status_code=200,
        )

    return templates.TemplateResponse(
        request=request,
        name="intake.html",
        context={
            "title": "Intake",
            "delivery": delivery,
            "manifest": loaded["manifest_path"],
            "style_version": loaded["style_version"],
            "report": report,
        },
    )


def _triage_session(request: Request, delivery: str):
    """Reuse the session for this delivery, or scan and start one."""

    store = _store(request)
    session = store.get(delivery)
    if session is None:
        loaded = load_delivery(delivery)
        report = scan_delivery(
            loaded["assets"],
            delivery_root=Path(delivery),
            style_families=_families(request.app.state.settings),
        )
        # Keep the normalised entries beside the verdicts; the stage needs paths.
        by_id = {str(a.get("asset_id")): a for a in loaded["assets"]}
        for row in report["assets"]:
            row["entry"] = by_id.get(str(row["asset_id"]), {})
        session = store.start(delivery, report)
    return session


def _triage_url(delivery: str, asset_id: str, mode: str, world: int) -> str:
    return (
        f"/intake/triage?delivery={quote(delivery)}&asset={quote(asset_id)}"
        f"&mode={mode}&world={world}"
    )


@router.get("/intake/triage", response_class=HTMLResponse)
def triage(
    request: Request,
    delivery: str = Query(...),
    asset: str | None = Query(default=None),
    mode: str = Query(default="composite"),
    world: int = Query(default=0),
) -> HTMLResponse:
    templates = request.app.state.templates
    try:
        session = _triage_session(request, delivery)
    except DeliveryIntakeError as exc:
        return templates.TemplateResponse(
            request=request, name="error.html",
            context={"title": "Delivery rejected", "errors": exc.errors}, status_code=200,
        )

    rows = session.report["assets"]
    ids = [str(r["asset_id"]) for r in rows]
    selected = asset if asset in ids else (ids[0] if ids else None)
    index = ids.index(selected) if selected else 0
    current = rows[index] if rows else None

    worlds = _catalog_worlds(request.app.state.settings)
    compositable = bool(current) and current.get("kind") in _COMPOSITABLE and bool(worlds)
    effective_mode = mode if compositable else "isolated"

    view = {
        "delivery": delivery,
        "rows": [
            {
                **row,
                "decision": session.decisions.get(str(row["asset_id"])),
                "effective": session.effective(str(row["asset_id"])),
                "explicit": session.is_explicit(str(row["asset_id"])),
                "url": _triage_url(delivery, str(row["asset_id"]), mode, world),
            }
            for row in rows
        ],
        "selected": selected,
        "current": current,
        "mode": effective_mode,
        "compositable": compositable,
        "world_index": world % len(worlds) if worlds else 0,
        "world_count": len(worlds),
        "world_id": worlds[world % len(worlds)]["asset_id"] if worlds else None,
        "prev_url": _triage_url(delivery, ids[index - 1], mode, world) if ids else "",
        "next_url": _triage_url(delivery, ids[(index + 1) % len(ids)], mode, world) if ids else "",
        "toggle_url": _triage_url(
            delivery, selected or "", "isolated" if effective_mode == "composite" else "composite", world
        ),
        "cycle_url": _triage_url(delivery, selected or "", mode, world + 1),
        "summary": session.summary(),
    }
    return templates.TemplateResponse(
        request=request, name="triage.html", context={"title": "Triage", **view},
    )


@router.post("/intake/decide")
def decide(
    request: Request,
    delivery: str = Form(...),
    asset_id: str = Form(...),
    decision: str = Form(...),
    next_url: str = Form(default=""),
):
    session = _store(request).get(delivery)
    if session is None:
        return RedirectResponse(url=f"/intake/triage?delivery={quote(delivery)}", status_code=303)
    try:
        session.decide(asset_id, decision)
    except TriageError as exc:
        return request.app.state.templates.TemplateResponse(
            request=request, name="error.html",
            context={"title": "Decision refused", "errors": exc.errors}, status_code=200,
        )
    # A decision auto-advances: the redirect lands on the next asset.
    target = next_url if next_url.startswith("/intake/triage") else f"/intake/triage?delivery={quote(delivery)}"
    return RedirectResponse(url=target, status_code=303)


@router.post("/intake/undo")
def undo(
    request: Request,
    delivery: str = Form(...),
    asset_id: str = Form(...),
    return_url: str = Form(default=""),
):
    session = _store(request).get(delivery)
    if session is not None:
        session.clear(asset_id)
    target = return_url if return_url.startswith("/intake/triage") else f"/intake/triage?delivery={quote(delivery)}"
    return RedirectResponse(url=target, status_code=303)


@router.get("/intake/stage.png")
def stage(
    request: Request,
    delivery: str = Query(...),
    asset: str = Query(...),
    mode: str = Query(default="composite"),
    world: int = Query(default=0),
):
    """The stage image: composited by default, isolated on request.

    Placement frames only — camera motion belongs to the render lanes (T10).
    """

    session = _store(request).get(delivery)
    if session is None:
        return HTMLResponse("no triage session", status_code=404)
    row = _delivery_asset(session, asset)
    entry = row.get("entry") or {}
    root = Path(delivery)

    asset_path = (root / str(entry.get("path") or "")).resolve()
    # Never serve a file outside the delivery the operator named.
    if not str(asset_path).startswith(str(root.resolve())):
        return HTMLResponse("path escapes the delivery root", status_code=400)
    if not asset_path.exists():
        return HTMLResponse(f"no file at {entry.get('path')!r}", status_code=404)

    settings = request.app.state.settings
    worlds = _catalog_worlds(settings)
    if mode == "composite" and row.get("kind") in _COMPOSITABLE and worlds:
        chosen = worlds[world % len(worlds)]
        try:
            result = render_composite(
                chosen,
                [{"asset_id": asset, "path": str(asset_path)}],
                project_root=settings.project_root,
                output_dir=_ENGINE_RUNTIME,
            )
            return FileResponse(result["path"], media_type="image/png")
        except CompositePreviewError:
            pass  # fall through to the isolated view rather than a broken stage
    return FileResponse(asset_path, media_type="image/png")


def _project_relative(settings, delivery: str, rel: str) -> str:
    """Translate a delivery-relative path into a project-relative one.

    The catalogue binds assets by path relative to the project root; the
    delivery declares them relative to its own folder. Files are not moved —
    the delivery folder lives inside the project, and the catalogue points at
    it where it stands.
    """

    absolute = (Path(delivery) / rel).resolve()
    root = settings.project_root.resolve()
    try:
        return absolute.relative_to(root).as_posix()
    except ValueError:
        raise DeliveryIntakeError([
            f"{rel!r} resolves outside the project root {root}; the catalogue "
            "cannot bind a file it cannot reach by relative path"
        ])


def _commit_plan(request: Request, delivery: str):
    """Everything the commit dialog shows and the confirm route acts on."""

    session = _store(request).get(delivery)
    if session is None:
        raise DeliveryIntakeError([
            "no triage session for this delivery; triage it before committing"
        ])
    settings = request.app.state.settings
    if not (settings.is_configured and settings.project_root):
        raise DeliveryIntakeError([
            "no catalogue configured; the console cannot commit without one"
        ])

    rows = session.report["assets"]
    promote, reject, skip, undecided, failing = [], [], [], [], []
    for row in rows:
        asset_id = str(row["asset_id"])
        decision = session.effective(asset_id)
        if decision == PROMOTE:
            promote.append(row)
            if row["status"] == "fail":
                failing.append(asset_id)
        elif decision == REJECT:
            reject.append(row)
        elif decision == SKIP:
            skip.append(row)
        else:
            undecided.append(asset_id)
    if failing:
        raise DeliveryIntakeError([
            f"{aid}: has a failing check and cannot be promoted" for aid in failing
        ])

    entries = []
    for row in promote:
        entry = dict(row.get("entry") or {})
        asset_id = str(row["asset_id"])
        tags = entry.get("semantic_tags")
        if not tags:
            semantic = str(entry.get("semantic") or "")
            tags = [w.strip(",.") for w in semantic.split() if len(w) > 3][:8] or [str(row.get("kind"))]
        layers = entry.get("layers")
        catalogue_entry = {
            "asset_id": asset_id,
            "path": _project_relative(settings, delivery, str(entry.get("path"))),
            "sha256": entry.get("sha256"),
            "kind": row.get("kind"),
            "style_version": entry.get("style_version"),
            "semantic_tags": tags,
            "visual_worlds": entry.get("visual_worlds") or ["story"],
            "identity_lenses": entry.get("identity_lenses") or [],
            "resolution_tier": entry.get("resolution_tier"),
            "generated": True,
            "contains_factual_text": bool(entry.get("contains_factual_text", False)),
            # Promotion fields — set here and only here, on the operator's
            # explicit confirm of a dialog that names every asset and field.
            "rights_state": "approved",
            "review_state": "approved_reusable",
            "render_eligible": True,
        }
        if entry.get("placement"):
            catalogue_entry["placement"] = entry["placement"]
        if entry.get("scale_reference"):
            catalogue_entry["scale_reference"] = entry["scale_reference"]
        if layers:
            catalogue_entry["layers"] = [
                {
                    "depth_layer": layer.get("depth_layer"),
                    "path": _project_relative(settings, delivery, str(layer.get("path"))),
                    "sha256": layer.get("sha256"),
                    **({"parallax_factor": layer["parallax_factor"]} if "parallax_factor" in layer else {}),
                }
                for layer in layers
            ]
        entries.append(catalogue_entry)

    return session, {
        "promote": promote,
        "reject": reject,
        "skip": skip,
        "undecided": undecided,
        "entries": entries,
        "bulk_clean": [
            str(r["asset_id"]) for r in promote
            if not session.is_explicit(str(r["asset_id"]))
        ],
    }


@router.get("/intake/commit", response_class=HTMLResponse)
def commit_dialog(request: Request, delivery: str = Query(...)) -> HTMLResponse:
    templates = request.app.state.templates
    try:
        _, plan = _commit_plan(request, delivery)
    except DeliveryIntakeError as exc:
        return templates.TemplateResponse(
            request=request, name="error.html",
            context={"title": "Cannot commit", "errors": exc.errors}, status_code=200,
        )
    return templates.TemplateResponse(
        request=request, name="commit.html",
        context={"title": "Commit", "delivery": delivery, **plan},
    )


@router.post("/intake/commit")
def commit_confirm(request: Request, delivery: str = Form(...)) -> HTMLResponse:
    templates = request.app.state.templates
    settings = request.app.state.settings
    try:
        session, plan = _commit_plan(request, delivery)
        if not plan["entries"]:
            raise DeliveryIntakeError(["nothing is marked for promotion; nothing to write"])
        result = register_assets(
            settings.catalog_path,
            plan["entries"],
            output_path=settings.catalog_path,
        )
    except (DeliveryIntakeError, AssetCatalogError) as exc:
        return templates.TemplateResponse(
            request=request, name="error.html",
            context={"title": "Commit refused", "errors": exc.errors}, status_code=200,
        )
    _store(request).drop(delivery)
    return templates.TemplateResponse(
        request=request, name="committed.html",
        context={
            "title": "Committed",
            "delivery": delivery,
            "added": result["added"],
            "asset_count": result["asset_count"],
            "rejected": [str(r["asset_id"]) for r in plan["reject"]],
            "skipped": [str(r["asset_id"]) for r in plan["skip"]],
        },
    )
