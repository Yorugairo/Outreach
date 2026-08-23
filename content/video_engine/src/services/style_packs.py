"""Video style-pack registry — one pack per art lane.

Each pack encodes the four axes the 2026-08-22 reference review found actually
distinguish lanes: character policy, background policy, caption policy, and
colour semantics — plus the renderer and the motion recipes the lane permits.

Two rules are enforced here rather than left to review:

* **Rive is rejected by name.** `.riv` is a compiled binary authored only in
  Rive's editor, so it cannot be produced programmatically. It is not one of the
  seven HyperFrames adapters and never will be a lane target.
* **Rendition level is descriptive, not restrictive.** Reference conditioning
  holds identity at any rendition, and legibility is protected by caption and
  evidence zoning rather than by flattening the artwork.

Distinct from `style_pack_library.v1`, which governs woodblock calibration packs.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Sequence

from jsonschema import Draft7Validator

from content.video_engine.src.services.artifact_io import (
    load_json,
    stamp_artifact_hash,
)

VIDEO_STYLE_PACK_VERSION = "video_style_pack.v1"

_VIDEO_ENGINE_ROOT = Path(__file__).resolve().parents[2]
_CONFIG_DIR = _VIDEO_ENGINE_ROOT / "configs"
_PACK_DIR = _CONFIG_DIR / "style_packs"

#: The seven HyperFrames runtime adapters. Rive is deliberately absent.
HYPERFRAMES_ADAPTERS = frozenset(
    {"gsap", "lottie", "three", "animejs", "css", "waapi", "typegpu"}
)

#: Lanes in build-priority order, most reachable first.
LANE_ORDER: tuple[str, ...] = (
    "expert_explainer",
    "presenter_infographic",
    "flat_cartoon_explainer",
    "stick_explainer",
    "cutout_history",
    "woodblock",
    "whiteboard",
)

_REJECTED_ADAPTERS = {
    "rive": (
        "rive is not a valid runtime adapter: .riv is a compiled binary authored "
        "only in Rive's editor and cannot be produced programmatically. Use one of "
        + ", ".join(sorted(HYPERFRAMES_ADAPTERS))
    )
}


class StylePackError(ValueError):
    """A pack failed validation, or the registry is incomplete."""

    def __init__(self, errors: Sequence[str]):
        self.errors = [str(item) for item in errors]
        super().__init__("; ".join(self.errors) or "invalid style pack")


def _schema() -> dict[str, Any]:
    return load_json(_CONFIG_DIR / "video_style_pack.schema.json", "style pack schema")


def _schema_errors(payload: Mapping[str, Any], label: str) -> list[str]:
    validator = Draft7Validator(_schema())
    return [
        label + "".join(f"[{part!r}]" for part in error.absolute_path) + f": {error.message}"
        for error in sorted(validator.iter_errors(dict(payload)), key=lambda e: list(e.absolute_path))
    ]


def _adapter_errors(payload: Mapping[str, Any], label: str) -> list[str]:
    renderer = payload.get("renderer") or {}
    adapter = renderer.get("runtime_adapter")
    if adapter is None:
        return []
    name = str(adapter).strip().casefold()
    if name in _REJECTED_ADAPTERS:
        return [f"{label}: {_REJECTED_ADAPTERS[name]}"]
    if name not in HYPERFRAMES_ADAPTERS:
        return [
            f"{label}: runtime_adapter {adapter!r} is not one of the seven HyperFrames "
            "adapters (" + ", ".join(sorted(HYPERFRAMES_ADAPTERS)) + ")"
        ]
    if renderer.get("engine") != "hyperframes":
        return [f"{label}: runtime_adapter requires engine 'hyperframes'"]
    return []


def _caption_errors(payload: Mapping[str, Any], label: str) -> list[str]:
    captions = payload.get("captions") or {}
    if captions.get("mode") == "none":
        return []
    errors: list[str] = []
    for field in ("position", "highlight"):
        if not captions.get(field):
            errors.append(f"{label}: captions.{field} is required when captions are burned in")
    if captions.get("highlight") in {"keyword", "karaoke"} and not captions.get(
        "highlight_colour"
    ):
        errors.append(f"{label}: captions.highlight_colour is required for a highlight rule")
    return errors


def validate_style_pack(
    value: Mapping[str, Any] | str | Path, *, label: str | None = None
) -> dict[str, Any]:
    """Validate one pack and stamp its artifact hash."""

    payload = dict(load_json(value, "style pack"))
    name = label or str(payload.get("lane") or "style pack")
    payload["schema_version"] = VIDEO_STYLE_PACK_VERSION
    payload.pop("artifact_hash", None)
    stamp_artifact_hash(payload)

    # Adapter first: the schema enum would otherwise reject a bad adapter with a
    # bare "not one of [...]" and swallow the actionable reason, which is the whole
    # point of rejecting Rive by name.
    adapter_errors = _adapter_errors(payload, name)
    if adapter_errors:
        raise StylePackError(adapter_errors)

    errors = _schema_errors(payload, name)
    if errors:
        raise StylePackError(errors)

    errors.extend(_caption_errors(payload, name))
    if errors:
        raise StylePackError(errors)
    return payload


def load_registry(pack_dir: str | Path | None = None) -> dict[str, dict[str, Any]]:
    """Load and validate every pack, keyed by lane."""

    root = Path(pack_dir) if pack_dir else _PACK_DIR
    if not root.is_dir():
        raise StylePackError([f"style pack directory not found: {root}"])

    packs: dict[str, dict[str, Any]] = {}
    errors: list[str] = []
    for path in sorted(root.glob("*.json")):
        try:
            pack = validate_style_pack(path, label=path.name)
        except StylePackError as exc:
            errors.extend(exc.errors)
            continue
        lane = str(pack["lane"])
        if lane in packs:
            errors.append(f"{path.name}: lane {lane!r} is already defined")
            continue
        packs[lane] = pack

    missing = [lane for lane in LANE_ORDER if lane not in packs]
    if missing:
        errors.append("registry is missing lanes: " + ", ".join(missing))
    if errors:
        raise StylePackError(errors)
    return packs


def get_pack(lane: str, pack_dir: str | Path | None = None) -> dict[str, Any]:
    packs = load_registry(pack_dir)
    if lane not in packs:
        raise StylePackError([f"unknown lane {lane!r}"])
    return packs[lane]


def registry_summary(pack_dir: str | Path | None = None) -> dict[str, Any]:
    """Ordered, board-friendly view of the registry."""

    packs = load_registry(pack_dir)
    return {
        "lane_count": len(packs),
        "lanes": [
            {
                "lane": lane,
                "label": packs[lane]["label"],
                "engine": packs[lane]["renderer"]["engine"],
                "runtime_adapter": packs[lane]["renderer"].get("runtime_adapter"),
                "character_policy": packs[lane]["character"]["policy"],
                "rendition": packs[lane]["character"].get("rendition"),
                "captions": packs[lane]["captions"]["mode"],
                "plate_kinds": packs[lane]["plate_kinds"],
                "operator_writes_on_screen_copy": packs[lane].get(
                    "operator_writes_on_screen_copy", False
                ),
                "artifact_hash": packs[lane]["artifact_hash"],
            }
            for lane in LANE_ORDER
            if lane in packs
        ],
    }
