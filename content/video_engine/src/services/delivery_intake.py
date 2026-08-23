"""Delivery intake — every check the episode-1 review ran by hand, as one pass.

The v2 batch arrived with three defects that nothing caught until a human read
the JSON and composited a frame: every asset self-promoted to render
eligibility, nineteen assets registered at a tier the resolver cannot reach for
their kind, and two interiors whose furniture implied a 0.92 adult against a
declared 0.50. This service exists so that class of defect is caught by the
first scan, not the third review.

Division of labour: ``asset_measurement`` measures and holds no opinions;
``asset_catalog`` owns the guards; **this module is the verdict layer**. It
combines both into one report per asset, every verdict carrying the measured
value and the expected one, because "FAIL" without numbers sends the operator
back to a shell.

The service performs no writes. Promotion is the operator's, through
``register_assets``, later.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from PIL import Image

from content.video_engine.src.services.asset_catalog import (
    _layer_errors,
    _scale_errors,
    _TIER_INDEX,
)
from content.video_engine.src.services.asset_measurement import measure_asset

FAIL = "fail"
FLAG = "flag"
CLEAN = "clean"

_SEVERITY = {FAIL: 0, FLAG: 1, CLEAN: 2}

#: Dimensions each asset class is generated at. A mismatch is a flag, not a
#: fail — the in-scene mechanism plates legitimately ship at world size.
CLASS_DIMENSIONS: dict[str, tuple[int, int]] = {
    "actor": (1024, 1536),
    "prop": (1024, 1024),
    "mechanism": (1024, 1024),
    "world": (1536, 1024),
    "world_board": (1536, 1024),
    "cast_board": (1024, 1536),
}

#: Kinds delivered as transparent cutouts. Worlds are opaque plates (their
#: non-``far`` planes carry alpha, but the flat plate does not).
_CUTOUT_KINDS = {"actor", "prop", "mechanism", "cast_board"}

#: Kind-to-tier convention the resolver depends on. Tier 3 is restricted to
#: mechanism and world_board, so an actor registered there is invisible to the
#: resolver and every actor slot falls through to a paid bespoke generation.
KIND_TIER = {
    "actor": 2,
    "prop": 2,
    "world": 2,
    "world_board": 2,
    "cast_board": 2,
    "mechanism": 3,
}

#: Fields product code must never set. Promotion is an operator action.
_PROMOTION_FIELDS = {
    "rights_state": "approved",
    "review_state": "approved_reusable",
    "render_eligible": True,
}

#: A partially-transparent edge brighter than this reads as a matte halo cut
#: from a light ground; it will ring on any darker world.
_HALO_EDGE_LUMA = 170.0


class DeliveryIntakeError(ValueError):
    """The delivery cannot be scanned as described."""

    def __init__(self, errors: Sequence[str]):
        self.errors = [str(item) for item in errors]
        super().__init__("; ".join(self.errors) or "cannot scan delivery")


#: Review-manifest plane names mapped onto the catalogue's depth vocabulary.
_MANIFEST_DEPTHS = {
    "far": "building_or_environment",
    "board": "evidence_safe_region",
    "mid": "actor_or_machine",
    "near": "foreground_cutout",
}


def _kind_for(asset_id: str, group: str) -> str:
    if group == "worlds":
        return "world_board"
    if asset_id.startswith("mechanism-"):
        return "mechanism"
    return "prop"


def load_delivery(delivery_root: str | Path) -> dict[str, Any]:
    """Find a review manifest in a delivery folder and normalise its entries.

    Review manifests are written by the generating agent in its own shape —
    grouped lists, short plane names — and this is the one place that shape is
    translated into catalogue-shaped assets. Keeping the translation in the
    service means the route and the CLI cannot drift on it.
    """

    root = Path(delivery_root)
    if not root.is_dir():
        raise DeliveryIntakeError([f"delivery root {root} is not a directory"])
    manifests = sorted(root.glob("*.manifest.json"))
    if not manifests:
        raise DeliveryIntakeError([f"no *.manifest.json in {root}"])
    if len(manifests) > 1:
        names = ", ".join(m.name for m in manifests)
        raise DeliveryIntakeError([f"multiple manifests in {root}: {names}; name one"])

    payload = json.loads(manifests[0].read_text(encoding="utf-8"))
    style_version = payload.get("style_family")
    assets: list[dict[str, Any]] = []
    for group in ("worlds", "finance_objects", "mechanism_plates", "assets"):
        for entry in payload.get(group) or []:
            asset = dict(entry)
            asset_id = str(asset.get("asset_id") or "")
            kind = asset.get("kind") or _kind_for(asset_id, group)
            asset.setdefault("kind", kind)
            asset.setdefault("style_version", style_version)
            asset.setdefault("resolution_tier", KIND_TIER.get(str(kind)))
            layers = asset.get("layers")
            if layers:
                mapped = []
                for layer in layers:
                    plane = dict(layer)
                    depth = plane.pop("depth", None)
                    if depth is not None and "depth_layer" not in plane:
                        plane["depth_layer"] = _MANIFEST_DEPTHS.get(str(depth), str(depth))
                    mapped.append(plane)
                asset["layers"] = mapped
                if not asset.get("path"):
                    far = next(
                        (l for l in mapped if l.get("depth_layer") == "building_or_environment"),
                        mapped[0],
                    )
                    asset["path"] = far.get("path")
                    asset.setdefault("sha256", far.get("sha256"))
            assets.append(asset)

    if not assets:
        raise DeliveryIntakeError([f"{manifests[0].name} declares no assets"])
    return {
        "manifest_path": str(manifests[0]),
        "style_version": style_version,
        "assets": assets,
    }


def _plane_digest_checks(asset: Mapping[str, Any], root: Path) -> list[dict[str, Any]]:
    """Verify every declared plane digest, not only the primary path."""

    checks: list[dict[str, Any]] = []
    for layer in asset.get("layers") or []:
        rel, declared = str(layer.get("path") or ""), str(layer.get("sha256") or "")
        if not rel or not declared:
            continue
        name = f"plane:{layer.get('depth_layer')}"
        path = root / rel
        if not path.exists():
            checks.append(_check(name, FAIL, f"no file at {rel!r}", "file present"))
            continue
        got = hashlib.sha256(path.read_bytes()).hexdigest()
        status = CLEAN if got == declared else FAIL
        checks.append(_check(name, status, got[:16], declared[:16]))
    return checks


def _check(name: str, status: str, measured: Any, expected: Any, note: str = "") -> dict[str, Any]:
    return {
        "check": name,
        "status": status,
        "measured": measured,
        "expected": expected,
        "note": note,
    }


def _digest_check(asset: Mapping[str, Any], root: Path) -> tuple[dict[str, Any], Path | None]:
    rel = str(asset.get("path") or "")
    path = (root / rel).resolve()
    if not rel:
        return _check("digest", FAIL, "no path declared", "a path and sha256"), None
    # A manifest is untrusted input; a path that climbs out of the delivery
    # folder is refused before anything reads it.
    try:
        path.relative_to(root.resolve())
    except ValueError:
        return _check(
            "digest", FAIL, rel, "a path inside the delivery folder",
            "path escapes the delivery root",
        ), None
    if not path.exists():
        return _check("digest", FAIL, f"no file at {rel!r}", "file present"), None
    got = hashlib.sha256(path.read_bytes()).hexdigest()
    declared = str(asset.get("sha256") or "")
    if not declared:
        return _check("digest", FAIL, "no sha256 declared", "a declared digest"), path
    if got != declared:
        return _check(
            "digest", FAIL, got[:16], declared[:16],
            "bytes on disk do not match the declared digest",
        ), path
    return _check("digest", CLEAN, got[:16], declared[:16]), path


def _dimension_check(asset: Mapping[str, Any], size: tuple[int, int]) -> dict[str, Any]:
    kind = str(asset.get("kind") or "")
    expected = CLASS_DIMENSIONS.get(kind)
    if expected is None:
        return _check("dimensions", FLAG, f"{size[0]}x{size[1]}", "unknown class", f"no contract for kind {kind!r}")
    if size != expected:
        return _check(
            "dimensions", FLAG, f"{size[0]}x{size[1]}", f"{expected[0]}x{expected[1]}",
            "outside the class contract; acceptable only if deliberate",
        )
    return _check("dimensions", CLEAN, f"{size[0]}x{size[1]}", f"{expected[0]}x{expected[1]}")


def _alpha_checks(asset: Mapping[str, Any], report: Mapping[str, Any]) -> list[dict[str, Any]]:
    kind = str(asset.get("kind") or "")
    alpha = report["alpha"]
    checks: list[dict[str, Any]] = []

    if kind in _CUTOUT_KINDS:
        if not alpha["has_alpha"]:
            checks.append(_check("alpha", FAIL, "no alpha channel", "transparent cutout"))
        else:
            checks.append(_check("alpha", CLEAN, "alpha present", "transparent cutout"))
            edge = alpha.get("edge_mean_rgb")
            if edge is not None:
                luma = 0.299 * edge[0] + 0.587 * edge[1] + 0.114 * edge[2]
                if luma > _HALO_EDGE_LUMA:
                    checks.append(_check(
                        "halo", FLAG, f"edge mean luma {luma:.0f}", f"<= {_HALO_EDGE_LUMA:.0f}",
                        "bright matte edge; will ring on darker grounds",
                    ))
                else:
                    checks.append(_check("halo", CLEAN, f"edge mean luma {luma:.0f}", f"<= {_HALO_EDGE_LUMA:.0f}"))
    else:
        checks.append(_check(
            "alpha", CLEAN if not alpha["has_alpha"] else FLAG,
            "alpha present" if alpha["has_alpha"] else "opaque",
            "opaque plate",
            "" if not alpha["has_alpha"] else "a flat world plate should be opaque",
        ))
    return checks


def _promotion_check(asset: Mapping[str, Any]) -> dict[str, Any]:
    claimed = [
        f"{field}={asset.get(field)!r}"
        for field, promoted in _PROMOTION_FIELDS.items()
        if asset.get(field) == promoted
    ]
    if claimed:
        return _check(
            "promotion", FAIL, ", ".join(claimed), "review_only on arrival",
            "promotion is an operator action; product code never sets it",
        )
    return _check("promotion", CLEAN, "review_only", "review_only on arrival")


def _tier_check(asset: Mapping[str, Any]) -> dict[str, Any]:
    kind = str(asset.get("kind") or "")
    tier = asset.get("resolution_tier")
    expected = KIND_TIER.get(kind)
    if expected is None or tier is None:
        return _check("tier", FLAG, repr(tier), repr(expected), f"no tier convention for kind {kind!r}")
    if int(tier) == 3 and kind not in {"mechanism", "world_board"}:
        return _check(
            "tier", FAIL, f"tier {tier}", f"tier {expected}",
            f"tier 3 is restricted by kind; a {kind} there is invisible to the "
            "resolver and every slot falls through to bespoke generation",
        )
    if int(tier) != expected:
        return _check("tier", FLAG, f"tier {tier}", f"tier {expected}", "outside the catalogue convention")
    return _check("tier", CLEAN, f"tier {tier}", f"tier {expected}")


def _guard_checks(asset: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Run the catalogue's own guards on the single asset, verbatim."""

    checks: list[dict[str, Any]] = []
    for name, guard in (("scale", _scale_errors), ("layers", _layer_errors)):
        errors = guard([asset])
        if errors:
            checks.extend(_check(name, FAIL, error, "the guard passing") for error in errors)
        else:
            checks.append(_check(name, CLEAN, "guard passed", "the guard passing"))
    return checks


def _style_check(asset: Mapping[str, Any], families: Mapping[str, Sequence[str]] | None) -> dict[str, Any]:
    version = asset.get("style_version")
    if not version:
        return _check("style", FAIL, "none declared", "a style_version", "required for the mixing guard")
    if families:
        known = {v for members in families.values() for v in members}
        if str(version) not in known:
            return _check(
                "style", FLAG, str(version), "a declared family",
                "version belongs to no style family; it will refuse to mix with anything",
            )
    return _check("style", CLEAN, str(version), "a style_version")


def _measurement_checks(report: Mapping[str, Any]) -> list[dict[str, Any]]:
    detail = report["internal_detail"]
    checks = [_check(
        "internal_detail",
        CLEAN if detail["fraction"] is not None else FLAG,
        f"{detail['fraction']:.1%}" if detail["fraction"] is not None else "unmeasurable",
        "informational",
    )]
    checks.append(_check("occupancy", CLEAN, f"{report['frame_occupancy']:.1%}", "informational"))
    return checks


def scan_delivery(
    assets: Sequence[Mapping[str, Any]],
    *,
    delivery_root: str | Path,
    style_families: Mapping[str, Sequence[str]] | None = None,
) -> dict[str, Any]:
    """Scan a delivered batch and emit one verdict per asset. No writes."""

    if not assets:
        raise DeliveryIntakeError(["the delivery contains no assets"])
    root = Path(delivery_root)
    if not root.is_dir():
        raise DeliveryIntakeError([f"delivery root {root} is not a directory"])

    rows: list[dict[str, Any]] = []
    for asset in assets:
        checks: list[dict[str, Any]] = []
        digest, path = _digest_check(asset, root)
        checks.append(digest)

        if path is not None:
            try:
                with Image.open(path) as im:
                    size = im.size
                report = measure_asset(path)
            except Exception as exc:  # Pillow raises several types for bad files
                checks.append(_check(
                    "image", FAIL, f"{type(exc).__name__}: {exc}", "a readable image",
                ))
            else:
                checks.append(_dimension_check(asset, size))
                checks.extend(_alpha_checks(asset, report))
                checks.extend(_measurement_checks(report))

        checks.extend(_plane_digest_checks(asset, root))
        checks.append(_promotion_check(asset))
        checks.append(_tier_check(asset))
        checks.extend(_guard_checks(asset))
        checks.append(_style_check(asset, style_families))

        worst = min((c["status"] for c in checks), key=_SEVERITY.__getitem__)
        rows.append({
            "asset_id": asset.get("asset_id"),
            "kind": asset.get("kind"),
            "status": worst,
            "checks": checks,
        })

    rows.sort(key=lambda row: (_SEVERITY[row["status"]], str(row["asset_id"])))
    counts = {status: sum(1 for r in rows if r["status"] == status) for status in (FAIL, FLAG, CLEAN)}
    return {
        "report_kind": "delivery_verdicts",
        "asset_count": len(rows),
        "counts": counts,
        "assets": rows,
    }
