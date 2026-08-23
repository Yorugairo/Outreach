"""Asset resolver and the accretion loop.

The catalogue already declares the right policy in `resolution_order`: try an
exact semantic match, then a reusable component composition, then deterministic
evidence, and only then generate a bespoke plate. Nothing executed it. This does.

The economic point is the last tier. Every slot that falls through to
``bespoke_plate`` is a generation the library could not cover, and the gap report
listing those slots **is** the generation worklist. Each asset it produces is
registered back, so coverage rises and per-episode generation falls — episode 1
buys the index-fund vocabulary, episode 5 buys housing, and later episodes mostly
resolve against what already exists.

One guard is load-bearing: assets carry a ``style_version`` and an episode may not
mix art directions. A sparse actor composited over a dense world does not read as
one picture, and the defect is invisible until it is on screen. Version strings
alone are too blunt a proxy for that — one coherent cast can be generated across
two of them — so a catalogue may declare ``style_families`` grouping versions
known to composite. The guard compares families and falls back to the version
string when none are declared.
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

from jsonschema import Draft7Validator

from content.video_engine.src.services.artifact_io import (
    load_json,
    stamp_artifact_hash,
    write_artifact,
)

ASSET_CATALOG_SCHEMA = "asset_catalog.schema.json"
GAP_REPORT_VERSION = "asset_gap_report.v1"

_VIDEO_ENGINE_ROOT = Path(__file__).resolve().parents[2]
_CONFIG_DIR = _VIDEO_ENGINE_ROOT / "configs"

BESPOKE_TIER = "bespoke_plate"
_TIER_INDEX = {
    "exact_semantic_match": 1,
    "reusable_component_composition": 2,
    "deterministic_evidence_or_mechanism": 3,
    BESPOKE_TIER: 4,
}
_EVIDENCE_KINDS = {"mechanism", "world_board"}
#: Episodes a catalogue asset may go unused before it is a pruning candidate.
_STALE_AFTER_EPISODES = 6


class AssetCatalogError(ValueError):
    """The catalogue is invalid, or a resolution would be unsafe."""

    def __init__(self, errors: Sequence[str]):
        self.errors = [str(item) for item in errors]
        super().__init__("; ".join(self.errors) or "invalid asset catalog")


def _schema_errors(payload: Mapping[str, Any]) -> list[str]:
    schema = load_json(_CONFIG_DIR / ASSET_CATALOG_SCHEMA, "asset catalog schema")
    validator = Draft7Validator(schema)
    return [
        "catalog" + "".join(f"[{part!r}]" for part in error.absolute_path) + f": {error.message}"
        for error in sorted(validator.iter_errors(dict(payload)), key=lambda e: list(e.absolute_path))
    ]


def load_catalog(value: Mapping[str, Any] | str | Path) -> dict[str, Any]:
    """Validate a catalogue and reject duplicate asset ids."""

    payload = dict(load_json(value, "asset catalog"))
    errors = _schema_errors(payload)
    if errors:
        raise AssetCatalogError(errors)

    seen: set[str] = set()
    for asset in payload.get("assets") or []:
        asset_id = str(asset.get("asset_id"))
        if asset_id in seen:
            errors.append(f"asset_id {asset_id!r} is defined more than once")
        seen.add(asset_id)
    errors.extend(_scale_errors(payload.get("assets") or []))
    errors.extend(_layer_errors(payload.get("assets") or []))
    if errors:
        raise AssetCatalogError(errors)
    return payload


#: Height of a standing adult, in metres. The constant every world is scaled to.
ADULT_HEIGHT_M = 1.75
#: Depth planes a 2.5D world may declare, back to front. Matches the style
#: profile's ``depth_layers``, so a layered plate binds straight into the
#: composite recipe and the renderer's bounded parallax.
DEPTH_LAYERS = (
    "building_or_environment",
    "evidence_safe_region",
    "actor_or_machine",
    "foreground_cutout",
)
_BACKGROUND_LAYER = DEPTH_LAYERS[0]


def _layer_errors(assets: Sequence[Mapping[str, Any]]) -> list[str]:
    """A 2.5D world declares separated planes; a flat plate declares none.

    Parallax has nothing to move on a single flattened image. Where a world does
    ship as layers, the planes must be nameable depth layers in back-to-front
    order and must include a background, or the renderer cannot decide what sits
    behind the cast.
    """

    errors: list[str] = []
    for asset in assets:
        layers = asset.get("layers")
        if not layers:
            continue
        asset_id = asset.get("asset_id")
        named = [str(layer.get("depth_layer")) for layer in layers]

        unknown = [name for name in named if name not in DEPTH_LAYERS]
        if unknown:
            errors.append(
                f"{asset_id}: layer(s) {', '.join(repr(u) for u in unknown)} are not "
                "declared depth layers; expected one of " + ", ".join(DEPTH_LAYERS)
            )
        if _BACKGROUND_LAYER not in named:
            errors.append(
                f"{asset_id}: a layered world needs a {_BACKGROUND_LAYER!r} plane; "
                "without one there is nothing behind the cast"
            )

        order = [DEPTH_LAYERS.index(name) for name in named if name in DEPTH_LAYERS]
        if order != sorted(order):
            errors.append(
                f"{asset_id}: layers must be declared back to front, "
                f"got {' -> '.join(named)}"
            )
        if len(set(named)) != len(named):
            errors.append(f"{asset_id}: a depth layer is declared more than once")
    return errors


#: How far a world's implied figure height may sit from its declared one.
_SCALE_TOLERANCE = 0.15


def _scale_errors(assets: Sequence[Mapping[str, Any]]) -> list[str]:
    """Reject a world plate whose furniture is drawn at the wrong human scale.

    Figure size is not a compositing choice — it is set by the furniture already
    in the plate. The episode-1 interiors were drawn as close-up rooms whose chair
    and sofa backs occupy 0.45 of the frame, putting a correctly-scaled adult at
    ~0.92 of frame height. Composited at the 0.50 standard the cast reads as dolls
    beside furniture built for giants, and no compositor setting can fix it.

    A world may declare the drawn height of one real object; the implied figure
    height follows by arithmetic and is checked against what the world claims.
    """

    errors: list[str] = []
    for asset in assets:
        ref = asset.get("scale_reference")
        placement = asset.get("placement") or {}
        if not ref or not placement.get("figure_height"):
            continue

        real_m = float(ref.get("real_height_m") or 0)
        drawn = float(ref.get("drawn_height") or 0)
        if real_m <= 0 or drawn <= 0:
            errors.append(
                f"{asset.get('asset_id')}: scale_reference needs a positive "
                "'real_height_m' and 'drawn_height'"
            )
            continue

        implied = drawn * (ADULT_HEIGHT_M / real_m)
        declared = float(placement["figure_height"])
        if abs(implied - declared) > _SCALE_TOLERANCE * declared:
            errors.append(
                f"{asset.get('asset_id')}: {ref.get('object')!r} is drawn at "
                f"{drawn:.2f} of frame height, which puts a {ADULT_HEIGHT_M}m adult "
                f"at {implied:.2f} — but the plate declares figure_height "
                f"{declared:.2f}. Regenerate the world at the declared scale; "
                "shrinking the figures instead makes them read as dolls."
            )
    return errors


def _slot_terms(slot: Mapping[str, Any]) -> set[str]:
    """Everything about a slot that could match a semantic tag."""

    terms: set[str] = set()
    for key in ("visual_intent", "narration_excerpt", "semantic_purpose", "visual_archetype"):
        value = slot.get(key)
        if value:
            terms.update(str(value).casefold().replace("_", " ").split())
    for tag in slot.get("semantic_tags") or []:
        # Both forms: an asset tag is matched by its hyphen-split parts, so a
        # slot tag added only whole could never match the identical asset tag
        # ("bar-comparison" needs "bar" and "comparison" to be present).
        folded = str(tag).casefold()
        terms.add(folded)
        terms.update(folded.replace("-", " ").split())
    return terms


def _tag_overlap(asset: Mapping[str, Any], terms: set[str]) -> int:
    hits = 0
    for tag in asset.get("semantic_tags") or []:
        parts = str(tag).casefold().replace("-", " ").split()
        if parts and all(part in terms for part in parts):
            hits += 1
    return hits


def _eligible(asset: Mapping[str, Any], *, for_render: bool) -> bool:
    """Preview may use anything; render may not use un-promoted assets."""

    if not for_render:
        return True
    return asset.get("render_eligible") is True


def _candidates_at_tier(
    assets: Sequence[Mapping[str, Any]],
    *,
    tier: str,
    terms: set[str],
    for_render: bool,
) -> list[tuple[int, Mapping[str, Any]]]:
    index = _TIER_INDEX[tier]
    scored: list[tuple[int, Mapping[str, Any]]] = []
    for asset in assets:
        if int(asset.get("resolution_tier") or 4) != index:
            continue
        if not _eligible(asset, for_render=for_render):
            continue
        if tier == "deterministic_evidence_or_mechanism" and asset.get("kind") not in _EVIDENCE_KINDS:
            continue
        overlap = _tag_overlap(asset, terms)
        if overlap:
            scored.append((overlap, asset))
    # Deterministic order: strongest overlap, then asset_id.
    scored.sort(key=lambda pair: (-pair[0], str(pair[1].get("asset_id"))))
    return scored


def resolve_slot(
    slot: Mapping[str, Any],
    catalog: Mapping[str, Any],
    *,
    for_render: bool = False,
) -> dict[str, Any]:
    """Walk the declared cascade in order and return the first match."""

    assets = list(catalog.get("assets") or [])
    terms = _slot_terms(slot)

    # Strength first, cascade second. The cascade expresses a preference between
    # candidates that match the slot equally well; it is not licence for a
    # one-word coincidence at an early tier to pre-empt a genuine match at a
    # later one. A host pose tagged "comparison" must not win a slot that a
    # mechanism matches on "comparison" *and* "bar-comparison".
    best_tier: str | None = None
    best_asset: Mapping[str, Any] | None = None
    best_overlap = 0

    for tier in catalog.get("resolution_order") or []:
        if tier == BESPOKE_TIER:
            break
        scored = _candidates_at_tier(assets, tier=tier, terms=terms, for_render=for_render)
        if not scored:
            continue
        overlap, asset = scored[0]
        if overlap > best_overlap:
            best_overlap, best_asset, best_tier = overlap, asset, tier

    if best_asset is not None:
        return {
            "slot_id": slot.get("slot_id"),
            "asset_id": best_asset.get("asset_id"),
            "resolved_tier": best_tier,
            "style_version": best_asset.get("style_version"),
            "sha256": best_asset.get("sha256"),
        }

    return {
        "slot_id": slot.get("slot_id"),
        "asset_id": None,
        "resolved_tier": BESPOKE_TIER,
        "style_version": None,
        "sha256": None,
    }


def _style_errors(
    resolutions: Sequence[Mapping[str, Any]],
    *,
    families: Mapping[str, Sequence[str]] | None = None,
) -> list[str]:
    """Reject an episode that mixes art directions.

    Exact version equality is too crude on its own. The episode-1 library shipped
    a single cast whose host and civilians carried different version strings, and
    they composite cleanly on a shared world — the guard would have blocked a
    frame that visibly reads as one picture. A catalogue may therefore group
    versions into families that are known to composite; the guard compares
    families and falls back to the version string when none are declared.
    """

    versions = sorted({r["style_version"] for r in resolutions if r.get("style_version")})
    if len(versions) <= 1:
        return []

    if families:
        by_version = {
            version: family
            for family, members in families.items()
            for version in members
        }
        # An undeclared version is its own family rather than a silent pass.
        groups = sorted({by_version.get(version, version) for version in versions})
        if len(groups) <= 1:
            return []
        return [
            "episode mixes style families " + " and ".join(repr(g) for g in groups)
            + " (versions " + ", ".join(repr(v) for v in versions) + ")"
            + "; assets from different art directions do not read as one picture"
        ]

    return [
        "episode mixes style versions " + " and ".join(repr(v) for v in versions)
        + "; assets from different art directions do not read as one picture."
        + " Declare a 'style_families' group in the catalogue if these are known"
        + " to composite together"
    ]


def _pruning_candidates(
    catalog: Mapping[str, Any], *, episode_number: int | None
) -> list[dict[str, Any]]:
    if episode_number is None:
        return []
    stale: list[dict[str, Any]] = []
    for asset in catalog.get("assets") or []:
        last = asset.get("last_used_episode")
        if last is None:
            continue
        if episode_number - int(last) >= _STALE_AFTER_EPISODES:
            stale.append(
                {
                    "asset_id": asset.get("asset_id"),
                    "last_used_episode": int(last),
                    "episodes_idle": episode_number - int(last),
                }
            )
    stale.sort(key=lambda entry: str(entry["asset_id"]))
    return stale


def resolve_episode_assets(
    coverage: Mapping[str, Any] | str | Path,
    catalog: Mapping[str, Any] | str | Path,
    *,
    for_render: bool = False,
    episode_number: int | None = None,
) -> dict[str, Any]:
    """Resolve every slot and emit the gap report that drives generation."""

    catalog_payload = load_catalog(catalog)
    coverage_payload = load_json(coverage, "coverage")
    slots = list(coverage_payload.get("slots") or [])
    if not slots:
        raise AssetCatalogError(["coverage contains no slots"])

    resolutions = [
        resolve_slot(slot, catalog_payload, for_render=for_render) for slot in slots
    ]
    errors = _style_errors(
        resolutions, families=catalog_payload.get("style_families")
    )
    if errors:
        raise AssetCatalogError(errors)

    gaps = [
        {
            "slot_id": slot.get("slot_id"),
            "visual_intent": slot.get("visual_intent"),
            "visual_archetype": slot.get("visual_archetype"),
            "narration_excerpt": slot.get("narration_excerpt"),
        }
        for slot, resolution in zip(slots, resolutions)
        if resolution["resolved_tier"] == BESPOKE_TIER
    ]
    tier_counts = Counter(resolution["resolved_tier"] for resolution in resolutions)

    payload = {
        "schema_version": GAP_REPORT_VERSION,
        "coverage_hash": coverage_payload.get("artifact_hash"),
        "episode_number": episode_number,
        "for_render": for_render,
        "slot_count": len(slots),
        "resolved_count": len(slots) - len(gaps),
        "coverage_ratio": round((len(slots) - len(gaps)) / len(slots), 4),
        "tier_counts": dict(sorted(tier_counts.items())),
        "style_version": next(
            (r["style_version"] for r in resolutions if r.get("style_version")), None
        ),
        "resolutions": resolutions,
        "gaps": gaps,
        "pruning_candidates": _pruning_candidates(
            catalog_payload, episode_number=episode_number
        ),
    }
    return stamp_artifact_hash(payload)


def register_assets(
    catalog: Mapping[str, Any] | str | Path,
    new_assets: Sequence[Mapping[str, Any]],
    *,
    output_path: str | Path,
) -> dict[str, Any]:
    """Fold newly generated assets back into the catalogue.

    This is the accretion step: what the gap report asked for becomes permanent
    library coverage, so the next episode resolves more and generates less.
    """

    payload = load_catalog(catalog)
    existing = {str(asset.get("asset_id")) for asset in payload.get("assets") or []}
    errors: list[str] = []
    added: list[str] = []

    for index, asset in enumerate(new_assets):
        asset_id = str(asset.get("asset_id") or "")
        if not asset_id:
            errors.append(f"new_assets[{index}].asset_id is required")
            continue
        if asset_id in existing:
            errors.append(f"asset_id {asset_id!r} is already in the catalogue")
            continue
        if not asset.get("style_version"):
            errors.append(f"{asset_id}: style_version is required")
            continue
        payload["assets"].append(dict(asset))
        existing.add(asset_id)
        added.append(asset_id)

    if errors:
        raise AssetCatalogError(errors)

    schema_errors = _schema_errors(payload)
    if schema_errors:
        raise AssetCatalogError(schema_errors)

    path = write_artifact(Path(output_path), stamp_artifact_hash(payload))
    return {
        "catalog_path": str(path),
        "added": added,
        "asset_count": len(payload["assets"]),
    }
