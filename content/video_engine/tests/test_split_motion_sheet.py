from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image, ImageDraw

from content.video_engine.scripts.split_motion_sheet import split_motion_sheet


def _sheet(path: Path, *, transparent: bool = True) -> None:
    background = (0, 0, 0, 0) if transparent else (0, 255, 0, 255)
    image = Image.new("RGBA", (400, 160), background)
    draw = ImageDraw.Draw(image)
    for index in range(4):
        left = index * 100 + 25
        draw.rectangle((left, 20, left + 50, 140), fill=(20, 30, 40, 255))
    image.save(path)


def test_split_motion_sheet_writes_four_trimmed_sprites(tmp_path: Path) -> None:
    source = tmp_path / "sheet.png"
    _sheet(source)

    payload = split_motion_sheet(source, tmp_path / "sprites", prefix="learner")

    assert [item["pose"] for item in payload["sprites"]] == [
        "idle",
        "walk",
        "explain",
        "prop",
    ]
    for item in payload["sprites"]:
        path = Path(str(item["path"]))
        assert path.is_file()
        with Image.open(path) as sprite:
            assert sprite.mode == "RGBA"
            assert sprite.width < 100


def test_split_motion_sheet_rejects_nontransparent_input(tmp_path: Path) -> None:
    source = tmp_path / "opaque.png"
    _sheet(source, transparent=False)

    with pytest.raises(ValueError, match="transparent background"):
        split_motion_sheet(source, tmp_path / "sprites", prefix="learner")


def test_split_motion_sheet_can_follow_uneven_alpha_gaps(tmp_path: Path) -> None:
    source = tmp_path / "uneven.png"
    image = Image.new("RGBA", (500, 160), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    for left, right in ((10, 145), (160, 230), (255, 390), (420, 490)):
        draw.rectangle((left, 20, right, 140), fill=(20, 30, 40, 255))
    image.save(source)

    payload = split_motion_sheet(
        source,
        tmp_path / "sprites",
        prefix="prop",
        poses=("one", "two", "three", "four"),
        auto_gaps=True,
    )

    widths = [int(item["width"]) for item in payload["sprites"]]
    assert widths[0] > widths[1]
    assert widths[2] > widths[3]
