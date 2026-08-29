"""Create a non-destructive PPTX copy with the lower-right footer replaced.

The supplied Gemini Notebook decks contain one full-slide PNG per slide, so the
footer is baked into the image rather than represented by an editable shape.
This utility keeps the source deck unchanged, masks the footer patch, and adds
the approved Teacher Mini stamp to every embedded slide PNG.
"""

from __future__ import annotations

import argparse
import io
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageStat


VIDEO_ENGINE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STAMP_PATH = (
    VIDEO_ENGINE_ROOT
    / "projects"
    / "systems-and-blowups"
    / "assets"
    / "generated"
    / "host"
    / "teacher-stamp-watermark-fit-character-v5-forward-gaze.png"
)


def clean_png(
    data: bytes,
    right_px: int,
    bottom_px: int,
    stamp_data: bytes | None = None,
) -> bytes:
    with Image.open(io.BytesIO(data)) as source:
        image = source.convert("RGBA")
    width, height = image.size
    x0 = max(0, width - right_px)
    y0 = max(0, height - bottom_px)

    # The footer sits on the light slide background. Use a nearby clean sample
    # rather than hard-coding pure white for decks with a slightly warm page.
    sample_left = max(0, x0 - 80)
    sample_top = max(0, y0 - 20)
    sample = image.convert("RGB").crop((sample_left, sample_top, x0, y0))
    median = ImageStat.Stat(sample).median
    fill = (*[int(value) for value in median], 255)
    ImageDraw.Draw(image).rectangle((x0, y0, width, height), fill=fill)

    if stamp_data is not None:
        with Image.open(io.BytesIO(stamp_data)) as stamp_source:
            stamp = stamp_source.convert("RGBA")
        if stamp.width > width or stamp.height > height:
            raise ValueError(
                f"stamp ({stamp.size}) cannot fit slide image ({image.size})"
            )
        image.alpha_composite(stamp, (width - stamp.width, height - stamp.height))

    output = io.BytesIO()
    image.save(output, format="PNG", optimize=True)
    return output.getvalue()


def clean_deck(
    source: Path,
    target: Path,
    right_px: int,
    bottom_px: int,
    stamp_data: bytes | None = None,
) -> int:
    if source.resolve() == target.resolve():
        raise ValueError("target must differ from source")
    target.parent.mkdir(parents=True, exist_ok=True)
    cleaned = 0
    with zipfile.ZipFile(source, "r") as source_zip, zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as target_zip:
        for info in source_zip.infolist():
            data = source_zip.read(info.filename)
            if info.filename.startswith("ppt/media/") and info.filename.lower().endswith(".png"):
                data = clean_png(data, right_px, bottom_px, stamp_data)
                cleaned += 1
            target_zip.writestr(info, data)
    return cleaned


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("target", type=Path)
    parser.add_argument("--right-px", type=int, default=120)
    parser.add_argument("--bottom-px", type=int, default=31)
    parser.add_argument("--stamp", type=Path, default=DEFAULT_STAMP_PATH)
    args = parser.parse_args()
    stamp_data = args.stamp.read_bytes()
    count = clean_deck(
        args.source,
        args.target,
        args.right_px,
        args.bottom_px,
        stamp_data,
    )
    print(
        f"wrote {args.target} ({count} embedded PNGs cleaned and stamped; "
        f"stamp={args.stamp})"
    )


if __name__ == "__main__":
    main()
