from __future__ import annotations

import io

from PIL import Image, ImageDraw

from content.video_engine.scripts.clean_pptx_watermarks import clean_png


def _png(image: Image.Image) -> bytes:
    buffer = io.BytesIO()
    image.save(buffer, format="PNG", optimize=False)
    return buffer.getvalue()


def test_clean_png_masks_footer_and_right_bottom_aligns_stamp() -> None:
    source = Image.new("RGBA", (100, 80), (245, 245, 245, 255))
    ImageDraw.Draw(source).rectangle((80, 65, 99, 79), fill=(10, 10, 10, 255))

    stamp = Image.new("RGBA", (20, 16), (0, 0, 0, 0))
    ImageDraw.Draw(stamp).rectangle((0, 0, 19, 15), fill=(225, 40, 80, 255))

    result = Image.open(
        io.BytesIO(
            clean_png(
                _png(source),
                right_px=20,
                bottom_px=16,
                stamp_data=_png(stamp),
            )
        )
    ).convert("RGBA")

    assert result.size == (100, 80)
    assert result.getpixel((99, 79)) == (225, 40, 80, 255)
    assert result.getpixel((79, 64)) == (245, 245, 245, 255)
