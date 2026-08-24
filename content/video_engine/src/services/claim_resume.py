"""Headless claim re-entry: scan, compose free artifacts, stop at the paid gate.

This is what runs when a delivery lands — invoked by the orchestrator after
``codex exec`` returns, or by the watchdog's resume command. It performs only
**free, local** work:

1. re-run the deterministic scan (never trust a marker file);
2. render composite previews for every scan-clean, compositable asset against
   the catalogue's placeable worlds (``runtime/``-class output, like every
   preview);
3. hand off to the editor render lane when one is configured — through a
   boundary, because that lane is owned elsewhere (P16); its absence is a
   recorded skip, not an error;
4. write a pack summary under ``runtime/claim-packs/`` and register any paid
   follow-ups the claim declares in the paid-gate registry — **registered,
   never released**.

No network. No spend. Motion stays in the lanes: this module copies values,
it computes none (held by the structural motion-arithmetic test).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable, Mapping

from content.video_engine.src.services import paths as _paths
from content.video_engine.src.services.composite_preview import (
    CompositePreviewError,
    render_composite,
)
from content.video_engine.src.services.delivery_intake import DeliveryIntakeError
from content.video_engine.src.services.delivery_scan import scan_claim_delivery, summary_line
from content.video_engine.src.services.generation_claim import GenerationClaimError, load_claim

#: Asset kinds that composite onto a world for a placement check.
COMPOSITABLE = {"actor", "prop", "mechanism"}


class ClaimResumeError(Exception):
    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__("; ".join(errors))


def _catalog(project_root: Path) -> dict[str, Any]:
    path = project_root / "asset-catalog.v1.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _placeable_worlds(catalog: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [
        asset for asset in catalog.get("assets", [])
        if asset.get("kind") in {"world", "world_board"} and asset.get("placement")
    ]


def _editor_render_hook(claim: Mapping[str, Any], project_root: Path) -> dict[str, Any]:
    """The editor lane boundary. Owned by P16's ``editor_render``; absent is a skip."""

    try:
        from content.video_engine.src.services import editor_render  # noqa: PLC0415
    except ImportError:
        return {"status": "skipped", "reason": "editor render lane not installed"}
    return editor_render.render_for_claim(claim, project_root=project_root)


def resume_claim(
    claim_id: str,
    *,
    env: Mapping[str, str] | None = None,
    editor_hook: Callable[[Mapping[str, Any], Path], dict[str, Any]] = _editor_render_hook,
) -> dict[str, Any]:
    """The whole free half of the loop; returns the written pack summary."""

    try:
        claim = load_claim(claim_id, env)
    except GenerationClaimError as exc:
        raise ClaimResumeError(exc.errors)
    project_root = Path(str(claim["project_root"]))
    catalog = _catalog(project_root)

    try:
        scan = scan_claim_delivery(claim, style_families=catalog.get("style_families"))
    except DeliveryIntakeError as exc:
        raise ClaimResumeError(exc.errors)

    verdicts = {str(r["asset_id"]): str(r["status"]) for r in scan["report"]["assets"]}
    by_id = {str(a.get("asset_id")): a for a in scan["assets"]}
    worlds = _placeable_worlds(catalog)
    delivery_root = Path(scan["delivery_root"])
    preview_dir = _paths.runtime_dir(project_root, "claim-previews", claim_id, ensure=True)

    composites: list[dict[str, Any]] = []
    for asset_id, status in sorted(verdicts.items()):
        entry = by_id.get(asset_id, {})
        if status != "clean" or str(entry.get("kind")) not in COMPOSITABLE or not worlds:
            continue
        rel = str(entry.get("path") or "")
        if not rel:
            continue
        figure_path = delivery_root / rel
        try:
            result = render_composite(
                worlds[0],
                [{"asset_id": asset_id, "path": str(figure_path)}],
                project_root=project_root,
                output_dir=preview_dir,
            )
            composites.append({"asset_id": asset_id, "path": result["path"]})
        except CompositePreviewError as exc:
            composites.append({"asset_id": asset_id, "error": exc.errors})

    editor = editor_hook(claim, project_root)

    paid_followups = list(claim.get("paid_followups") or [])
    registered: list[dict[str, Any]] = []
    if paid_followups:
        from content.video_engine.src.services import paid_gate  # noqa: PLC0415

        for followup in paid_followups:
            registered.append(paid_gate.register_job(
                claim_id=claim_id,
                lane=str(followup.get("lane") or "unknown"),
                description=str(followup.get("description") or ""),
                estimated_cost_usd=float(followup.get("estimated_cost_usd") or 0.0),
                env=env,
            ))

    summary = {
        "schema_version": "claim_pack_summary.v1",
        "claim_id": claim_id,
        "scan": {key: scan[key] for key in ("counts", "conflicts", "unresolved", "style_version")},
        "line": summary_line(scan),
        "composites": composites,
        "editor": editor,
        "paid_jobs_registered": [job.get("job_id") for job in registered],
        "paid_note": "registered only — release happens at the paid gate, never here",
    }
    out_dir = _paths.runtime_dir(project_root, "claim-packs", ensure=True)
    out_path = out_dir / f"{claim_id}.summary.json"
    out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    summary["summary_path"] = str(out_path)
    return summary
