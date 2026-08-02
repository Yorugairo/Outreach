"""Split a four-pose transparent character sheet into trimmed PNG sprites.

The image generator is asked for four evenly spaced, full-body poses on a
chroma-key background.  After chroma removal this utility turns the reviewed
sheet into deterministic, individually addressable assets.  It never infers or
generates anatomy.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image


DEFAULT_POSES = ("idle", "walk", "explain", "prop")


def split_motion_sheet(
    source: Path,
    output_dir: Path,
    *,
    prefix: str,
    poses: tuple[str, ...] = DEFAULT_POSES,
    padding: int = 24,
    auto_gaps: bool = False,
    version: str = "v1",
) -> dict[str, object]:
    if len(poses) != 4:
        raise ValueError("four-column sheets must declare exactly four asset names")
    if padding < 0:
        raise ValueError("padding cannot be negative")

    with Image.open(source) as opened:
        image = opened.convert("RGBA")
    alpha = image.getchannel("A")
    if alpha.getextrema()[0] != 0:
        raise ValueError("motion sheet must contain transparent background pixels")

    output_dir.mkdir(parents=True, exist_ok=True)
    boundaries = [0, round(image.width / 4), round(image.width / 2), round(image.width * 3 / 4), image.width]
    if auto_gaps:
        alpha_data = image.getchannel("A")
        occupied = [alpha_data.crop((x, 0, x + 1, image.height)).getbbox() is not None for x in range(image.width)]
        runs: list[tuple[int, int]] = []
        start: int | None = None
        for x, is_occupied in enumerate(occupied + [True]):
            if not is_occupied and start is None:
                start = x
            elif is_occupied and start is not None:
                if x - start >= 4:
                    runs.append((start, x))
                start = None
        inner_runs = [run for run in runs if run[0] > 0 and run[1] < image.width]
        separators: list[int] = []
        for target in boundaries[1:-1]:
            eligible = [run for run in inner_runs if (run[0] + run[1]) // 2 > (separators[-1] if separators else 0)]
            if not eligible:
                raise ValueError("could not find four separated alpha regions")
            run = min(eligible, key=lambda item: abs(((item[0] + item[1]) // 2) - target))
            separators.append((run[0] + run[1]) // 2)
        boundaries = [0, *separators, image.width]
    sprites: list[dict[str, object]] = []
    for index, pose in enumerate(poses):
        left = boundaries[index]
        right = boundaries[index + 1]
        cell = image.crop((left, 0, right, image.height))
        bbox = cell.getchannel("A").getbbox()
        if bbox is None:
            raise ValueError(f"pose {pose!r} contains no visible pixels")
        x0 = max(0, bbox[0] - padding)
        y0 = max(0, bbox[1] - padding)
        x1 = min(cell.width, bbox[2] + padding)
        y1 = min(cell.height, bbox[3] + padding)
        sprite = cell.crop((x0, y0, x1, y1))
        output = output_dir / f"{prefix}-{pose}-{version}.png"
        sprite.save(output, format="PNG", optimize=True)
        sprites.append(
            {
                "pose": pose,
                "path": output.as_posix(),
                "sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
                "width": sprite.width,
                "height": sprite.height,
            }
        )

    return {
        "schema_version": "motion_sprite_set.v1",
        "source_path": source.as_posix(),
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "prefix": prefix,
        "sprites": sprites,
        "render_eligible": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--prefix", required=True)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--padding", type=int, default=24)
    parser.add_argument("--version", default="v1")
    parser.add_argument(
        "--names",
        default=",".join(DEFAULT_POSES),
        help="comma-separated names for the four columns",
    )
    parser.add_argument(
        "--auto-gaps",
        action="store_true",
        help="split at transparent vertical gaps instead of equal-width columns",
    )
    args = parser.parse_args()

    poses = tuple(item.strip() for item in args.names.split(",") if item.strip())

    payload = split_motion_sheet(
        args.input,
        args.output_dir,
        prefix=args.prefix,
        poses=poses,
        padding=args.padding,
        auto_gaps=args.auto_gaps,
        version=args.version,
    )
    if args.manifest:
        args.manifest.parent.mkdir(parents=True, exist_ok=True)
        args.manifest.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
