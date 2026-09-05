"""P40 T2: synthetic sequences with known answers - a static pair gives zero motion energy,
a translating block gives a centroid shift equal to its translation."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts/metrics"))
import frame_metrics as FM  # noqa: E402


def _frame(path: Path, block_x: int | None, size=(480, 180)) -> None:
    im = Image.new("L", size, 20)
    if block_x is not None:
        im.paste(220, (block_x, 60, block_x + 40, 100))
    im.save(path)


def test_static_pair_has_zero_motion_energy(tmp_path: Path):
    _frame(tmp_path / "f0.png", 100); _frame(tmp_path / "f1.png", 100)
    rows = FM.sequence_metrics(sorted(tmp_path.glob("*.png")))
    assert rows[0]["motion_energy"] == 0.0 and rows[0]["change_centroid"] is None


def test_translating_block_moves_the_change_centroid_by_its_translation(tmp_path: Path):
    # block at x=100 then x=200: the |diff| is two blocks, so the centroid sits between them
    _frame(tmp_path / "f0.png", 100); _frame(tmp_path / "f1.png", 200); _frame(tmp_path / "f2.png", 300)
    rows = FM.sequence_metrics(sorted(tmp_path.glob("*.png")))
    c1, c2 = rows[0]["change_centroid"], rows[1]["change_centroid"]
    assert rows[0]["motion_energy"] > 0
    assert abs(c1[0] - (170 / 480)) < 0.02          # between x=100..140 and x=200..240 -> centre 170 (as a fraction of width)
    assert abs((c2[0] - c1[0]) - (100 / 480)) < 0.02  # the centroid moved by the translation (the 300..340 block must fit the frame)
    assert abs(c1[1] - (80 / 180)) < 0.02             # rows 60..100 -> centre 80


def test_window_summary_reports_still_share(tmp_path: Path):
    for i in range(6):
        _frame(tmp_path / f"f{i}.png", 100 if i < 4 else 100 + 20 * (i - 3))
    rows = FM.sequence_metrics(sorted(tmp_path.glob("*.png")))
    w = FM.window_summary(rows, fps=1.0, edges=[0, 3, 6])
    assert w[0]["still_share"] == 1.0 and w[1]["still_share"] < 1.0
