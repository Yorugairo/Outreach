"""Placement preview — does a figure sit correctly in a world?

This renderer answers exactly one question: **size, zone and baseline**. It is
not a render preview and must never be presented as one. Camera motion, parallax
and every other render-lane behaviour belong to Remotion and HyperFrames, which
already own them; producing motion here with a different engine would let a
preview disagree with the delivered video.

The episode-1 intake is why this exists. Three defects — figures at the wrong
scale, figures standing on furniture, and a world whose furniture committed it to
a different figure height — were all invisible in an isolated thumbnail and
obvious the moment an asset sat in a real frame.

Output is deterministic and lands under ``runtime/``. A preview is never a
catalogue asset.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Sequence

from PIL import Image

from content.video_engine.src.services.paths import is_runtime_path
from content.video_engine.src.services.asset_catalog import DEPTH_LAYERS

#: Preview frames are rendered at delivery resolution so measurements transfer.
FRAME_WIDTH = 1920
FRAME_HEIGHT = 1080

#: Stamped on every result. The console labels frames with this so a placement
#: check is never mistaken for a look at the finished shot.
PREVIEW_KIND = "placement_check"
PREVIEW_ANSWERS = "size, zone and baseline only"

#: Depth planes, back to front. Imported rather than restated: ``asset_catalog``
#: owns this vocabulary, and a second copy here would silently disagree the day a
#: plane is added there.
_PLANE_ORDER = DEPTH_LAYERS
_CAST_AFTER = "actor_or_machine"
_CAST_AFTER_INDEX = _PLANE_ORDER.index(_CAST_AFTER)

#: Gap between figures sharing a frame, as a fraction of frame width.
_FIGURE_GAP = 0.02


def _fit_to_frame(im: Image.Image) -> Image.Image:
    """Scale a plate to the frame without distorting it.

    The library ships worlds at 1536x1024 (3:2) while delivery is 16:9. Stretching
    one to the other applies a 1.185x horizontal scale to the *world* while the
    composited figure keeps its own aspect — so the figure reads ~18% narrow
    against the furniture, in the one frame whose entire purpose is judging figure
    size against furniture.

    Scale to cover, anchored to the bottom edge. The floor is load-bearing —
    ``baseline_y`` puts feet on it — so overflow is cropped from the top, which is
    wall.
    """

    if im.size == (FRAME_WIDTH, FRAME_HEIGHT):
        return im
    scale = max(FRAME_WIDTH / im.width, FRAME_HEIGHT / im.height)
    scaled = im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)
    left = (scaled.width - FRAME_WIDTH) // 2
    top = scaled.height - FRAME_HEIGHT  # bottom-anchored
    return scaled.crop((left, top, left + FRAME_WIDTH, top + FRAME_HEIGHT))


class CompositePreviewError(ValueError):
    """The requested frame cannot be composed as asked."""

    def __init__(self, errors: Sequence[str]):
        self.errors = [str(item) for item in errors]
        super().__init__("; ".join(self.errors) or "cannot compose preview")


def measure_cutout(path: str | Path) -> tuple[int, int]:
    """Trimmed width and height of a cutout, ignoring transparent margin."""

    with Image.open(path) as im:
        rgba = im.convert("RGBA")
        box = rgba.getchannel("A").getbbox()
    if box is None:
        return (0, 0)
    return (box[2] - box[0], box[3] - box[1])


def _placement_errors(world: Mapping[str, Any]) -> list[str]:
    placement = world.get("placement")
    if not placement:
        return [
            f"{world.get('asset_id')}: no 'placement' block, so there is nothing to "
            "say where a figure may stand. Declare figure_zone, baseline_y and "
            "figure_height rather than guessing."
        ]
    missing = [k for k in ("figure_zone", "baseline_y", "figure_height") if not placement.get(k)]
    if missing:
        return [f"{world.get('asset_id')}: placement is missing {', '.join(missing)}"]
    return []


def plan_composite(
    world: Mapping[str, Any],
    figures: Sequence[Mapping[str, Any]],
    *,
    figure_height: float | None = None,
    project_root: str | Path | None = None,
) -> dict[str, Any]:
    """Resolve geometry without touching pixels.

    Separated from rendering because every placement rule is arithmetic, and
    arithmetic is worth testing without images. A figure may carry a
    ``trimmed_size`` and skip disk entirely; otherwise its ``path`` is measured,
    resolved against ``project_root`` when one is given.
    """

    errors = _placement_errors(world)
    if errors:
        raise CompositePreviewError(errors)

    # Plane validity is arithmetic on names, so it belongs here rather than at
    # render time — the console plans far more often than it renders.
    if world.get("layers"):
        _ordered_planes(world)

    placement = world["placement"]
    height = float(figure_height if figure_height is not None else placement["figure_height"])
    max_figures = int(placement.get("max_figures") or 1)

    if len(figures) > max_figures:
        raise CompositePreviewError([
            f"{world.get('asset_id')}: {len(figures)} figures requested but the world "
            f"declares max_figures {max_figures}. A world holds only as many figures "
            "as its clear floor fits."
        ])

    x0, x1 = (float(v) for v in placement["figure_zone"])
    # round, not truncate: (1.0 - 0.55) * 1920 is 863.999... in binary float,
    # and reporting an 863px zone for a 864px one is a lie in an error message.
    zone_px = round((x1 - x0) * FRAME_WIDTH)
    # round, like zone_px above. int() and round() disagree for 40 of 100 figure
    # heights, and measuring the zone one way and the figure another puts both
    # sides of the same comparison on different rulers.
    height_px = round(FRAME_HEIGHT * height)
    bottom_px = round(FRAME_HEIGHT * float(placement["baseline_y"]))

    widths: list[int] = []
    for figure in figures:
        size = figure.get("trimmed_size")
        if size is None:
            rel = str(figure.get("path"))
            path = Path(rel) if project_root is None else Path(project_root) / rel
            if not path.exists():
                root_note = project_root if project_root is not None else Path.cwd()
                raise CompositePreviewError([
                    f"{figure.get('asset_id')}: no file at {rel!r} relative to {root_note}"
                ])
            size = measure_cutout(path)
        w, h = size
        if h <= 0:
            raise CompositePreviewError([
                f"{figure.get('asset_id')}: cutout measures {w}x{h}; it is fully "
                "transparent, so there is nothing to place."
            ])
        widths.append(round(w * height_px / h))

    if height_px > bottom_px:
        raise CompositePreviewError([
            f"{world.get('asset_id')}: a figure at figure_height {height:.2f} is "
            f"{height_px}px tall but its feet sit at {bottom_px}px, so {height_px - bottom_px}px "
            "would be cut off above the frame. Lower figure_height or raise baseline_y."
        ])

    gap_px = round(FRAME_WIDTH * _FIGURE_GAP)
    total_px = sum(widths) + gap_px * max(0, len(widths) - 1)
    if total_px > zone_px:
        breakdown = " + ".join(f"{w}px" for w in widths)
        raise CompositePreviewError([
            f"{world.get('asset_id')}: {len(figures)} figures at figure_height "
            f"{height:.2f} need {breakdown} plus {gap_px}px gap = {total_px}px, "
            f"but the clear zone is {zone_px}px. Lower the figure height, use fewer "
            "figures, or use a world with a wider clear zone."
        ])

    # Centre the group in the zone; nearest figure last so it draws in front.
    start = x0 * FRAME_WIDTH + (zone_px - total_px) / 2
    placed: list[dict[str, Any]] = []
    cursor = start
    for figure, width in zip(figures, widths):
        placed.append({
            "asset_id": figure.get("asset_id"),
            "left_px": int(cursor),
            "bottom_px": bottom_px,
            "width_px": width,
            "height_px": height_px,
        })
        cursor += width + gap_px

    return {
        "preview_kind": PREVIEW_KIND,
        "answers": PREVIEW_ANSWERS,
        "world_id": world.get("asset_id"),
        "figure_height": height,
        "zone_px": zone_px,
        "used_px": total_px,
        "figures": placed,
    }


def _resolve(project_root: Path, rel: str, label: str) -> Path:
    path = (project_root / rel).resolve()
    if not path.exists():
        # Name the root as well as the relative part: resolving against the wrong
        # root is the failure this reports, and the root is the half you need.
        raise CompositePreviewError([
            f"{label}: no file at {rel!r} relative to project root {project_root}"
        ])
    return path


def _ordered_planes(world: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    """Sort planes back to front, refusing anything unorderable.

    Sorting an unknown name to the back of the list would put a typo'd plane in
    front of every real one, silently. ``asset_catalog`` rejects unknown planes on
    the catalogue path; this path takes a raw mapping and never loads the
    catalogue, so it has to reject them itself.
    """

    layers = list(world.get("layers") or [])
    names = [str(layer.get("depth_layer")) for layer in layers]

    unknown = [n for n in names if n not in _PLANE_ORDER]
    if unknown:
        raise CompositePreviewError([
            f"{world.get('asset_id')}: plane(s) {', '.join(repr(n) for n in unknown)} "
            "are not declared depth layers; expected one of " + ", ".join(_PLANE_ORDER)
        ])
    duplicated = sorted({n for n in names if names.count(n) > 1})
    if duplicated:
        raise CompositePreviewError([
            f"{world.get('asset_id')}: depth layer(s) {', '.join(repr(n) for n in duplicated)} "
            "declared more than once; plane order would depend on input order."
        ])
    return sorted(layers, key=lambda layer: _PLANE_ORDER.index(str(layer.get("depth_layer"))))


def _load_planes(world: Mapping[str, Any], project_root: Path) -> list[tuple[str, Image.Image]]:
    planes: list[tuple[str, Image.Image]] = []
    sizes: dict[str, tuple[int, int]] = {}
    for layer in _ordered_planes(world):
        rel = str(layer.get("path"))
        path = _resolve(project_root, rel, f"{world.get('asset_id')} plane {layer.get('depth_layer')}")
        im = Image.open(path).convert("RGBA")
        sizes[rel] = im.size
        planes.append((str(layer.get("depth_layer")), im))

    distinct = set(sizes.values())
    if len(distinct) > 1:
        shown = ", ".join(f"{rel} {w}x{h}" for rel, (w, h) in sorted(sizes.items()))
        raise CompositePreviewError([
            f"{world.get('asset_id')}: depth planes differ in size ({shown}). "
            "Planes that do not register cannot be composited; regenerate them in "
            "one pass at identical dimensions."
        ])
    return planes


def render_composite(
    world: Mapping[str, Any],
    figures: Sequence[Mapping[str, Any]],
    *,
    project_root: str | Path,
    output_dir: str | Path,
    figure_height: float | None = None,
) -> dict[str, Any]:
    """Compose a placement frame and write it under ``runtime/``."""

    root = Path(project_root)

    # Resolve every figure up front: planning measures cutouts, so an unresolved
    # path would surface as a Pillow FileNotFoundError instead of our own error.
    resolved: list[dict[str, Any]] = []
    for figure in figures:
        path = _resolve(root, str(figure.get("path")), str(figure.get("asset_id")))
        resolved.append({**figure, "path": str(path)})

    plan = plan_composite(world, resolved, figure_height=figure_height)

    frame = Image.new("RGBA", (FRAME_WIDTH, FRAME_HEIGHT), (0, 0, 0, 255))
    planes = _load_planes(world, root) if world.get("layers") else []

    if planes:
        # Split by declared depth, not by list position. Falling back to "last
        # plane" put the cast in front of foreground_cutout whenever a world
        # declared no actor_or_machine plane — a shape the catalogue guards allow,
        # since only building_or_environment is required.
        behind = [
            plane for plane in planes
            if _PLANE_ORDER.index(plane[0]) <= _CAST_AFTER_INDEX
        ]
        in_front = [
            plane for plane in planes
            if _PLANE_ORDER.index(plane[0]) > _CAST_AFTER_INDEX
        ]
    else:
        path = _resolve(root, str(world.get("path")), f"{world.get('asset_id')} plate")
        behind = [("building_or_environment", Image.open(path).convert("RGBA"))]
        in_front = []

    for _, im in behind:
        frame.alpha_composite(_fit_to_frame(im))

    for figure, placed in zip(resolved, plan["figures"]):
        cut = Image.open(figure["path"]).convert("RGBA")
        box = cut.getchannel("A").getbbox()
        if box is not None:
            cut = cut.crop(box)
        cut = cut.resize((placed["width_px"], placed["height_px"]), Image.LANCZOS)
        frame.alpha_composite(cut, (placed["left_px"], placed["bottom_px"] - placed["height_px"]))

    for _, im in in_front:
        frame.alpha_composite(_fit_to_frame(im))

    out_dir = Path(output_dir)
    # A preview is a scratch artifact, never an asset. Enforcing the location here
    # rather than trusting the caller keeps a preview frame out of the asset tree,
    # where it could be mistaken for something the catalogue owns. The rule is
    # the path contract's runtime-class check; only the error stays local.
    if not is_runtime_path(out_dir):
        raise CompositePreviewError([
            f"preview output must live under a 'runtime' directory; got {out_dir}. "
            "Previews are scratch artifacts and are never catalogue assets."
        ])
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = "-".join([str(world.get("asset_id"))] + [str(f.get("asset_id")) for f in figures])
    # Four digits via round(): int() collapses 0.28/0.29 and 0.56/0.57 to one
    # filename, so a second render at a different height silently overwrote the
    # first and the console showed the wrong geometry under the right label.
    out_path = out_dir / f"{stem}-h{round(plan['figure_height'] * 1000):04d}.png"
    # Deterministic bytes: no timestamp chunk, fixed encoder settings.
    frame.convert("RGB").save(out_path, format="PNG", optimize=False, compress_level=6)

    return {
        **plan,
        "path": str(out_path),
        "plane_count": len(planes),
        "frame_size": [FRAME_WIDTH, FRAME_HEIGHT],
    }
