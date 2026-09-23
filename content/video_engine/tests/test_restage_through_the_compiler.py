"""P69 T7 / R26-230 (c): the SAME ledger row, compiled through `build_scene_timeline_f` at 16:9 and at 9:16.

test_fed_full_stage_bands.py checks the Python mirror (`page_boxes` on a hand-stamped page). This test drives the
compiler's own row door instead: `ledger_world` reads a `ledger:` plate id off an inline series file, builds the
page, and stamps it through `stamp_full_stage`, which reads the module-global `ASPECT`. So the global is pinned
and restored around each compile (`test_the_stamp_arrival.py:_golden_page`); an ASPECT leak once broke the suite.

Characterization only (plan: Expected RED none): a failure here is the finding and keeps R26-230 open.
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import build_scene_timeline_f as B  # noqa: E402
import ledger_page as LPG  # noqa: E402

SERIES_ID = "restage-fixture"
PLATE_ID = f"ledger:{SERIES_ID}:line"
KEN = (1.0, 0.0, 0.0)
DATA_KEYS = ("labels", "values", "value_strings", "colors", "series", "periods",
             "start", "end", "display_labels", "denominator", "axes", "log", "builder")


def _series() -> dict:
    """A small dense-line file: two series (so `pick_builder` returns dense-line), twelve monthly points."""
    xs = [2025.0 + m / 12 for m in range(12)]
    up = [100, 104, 109, 113, 121, 126, 134, 139, 147, 152, 161, 170]
    down = [100, 98, 97, 95, 96, 93, 91, 90, 88, 89, 86, 84]
    return {"title": "Two lines from one start", "sub": "100 = Jan 2025", "src": "Fixture - test only",
            "ylabel": "index - 100 = Jan 2025", "xticks": 4,
            "series": [{"label": "+70%", "name": "THE CLIMBER", "color": "crimson", "pts": [list(p) for p in zip(xs, up)]},
                       {"label": "-16%", "name": "THE SLIDER", "color": "cobalt", "pts": [list(p) for p in zip(xs, down)]}]}


@pytest.fixture()
def ep_dir(tmp_path: Path) -> Path:
    objects = tmp_path / "evidence/objects"
    objects.mkdir(parents=True)
    (objects / f"{SERIES_ID}.series.json").write_text(json.dumps(_series()), encoding="utf-8")
    return tmp_path


def _compile_row(ep_dir: Path, aspect: str) -> dict:
    """ONE ledger row's world, compiled with the compiler's ASPECT pinned, then restored."""
    _aspect, B.ASPECT = B.ASPECT, aspect
    try:
        return B.ledger_world(PLATE_ID, KEN, ep_dir)
    finally:
        B.ASPECT = _aspect


def _inside(inner: dict, outer: dict) -> bool:
    return (inner["x"] >= outer["x"] and inner["y"] >= outer["y"]
            and inner["x"] + inner["w"] <= outer["x"] + outer["w"]
            and inner["y"] + inner["h"] <= outer["y"] + outer["h"])


def _safe_box(aspect: str) -> dict:
    x, y, w, h = LPG.SAFE_BOX[aspect]
    return {"x": x, "y": y, "w": w, "h": h}


def _data_payload(page: dict) -> dict:
    return {k: copy.deepcopy(page[k]) for k in DATA_KEYS if k in page}


def test_the_fixture_compiles_as_a_dense_line_page_at_both_aspects(ep_dir: Path):
    for aspect in ("16:9", "9:16"):
        world = _compile_row(ep_dir, aspect)
        assert world["kind"] == B.SPECIES_LEDGER
        assert world["page"]["builder"] == "dense-line", aspect


def test_the_aspect_global_is_restored_after_each_compile(ep_dir: Path):
    before = B.ASPECT
    _compile_row(ep_dir, "9:16")
    assert B.ASPECT == before
    _compile_row(ep_dir, "16:9")
    assert B.ASPECT == before


def test_the_16x9_row_is_stamped_full_stage_and_the_9x16_row_is_not(ep_dir: Path):
    land = _compile_row(ep_dir, "16:9")
    port = _compile_row(ep_dir, "9:16")
    assert B.page_is_full_stage(land, "16:9")
    assert land["page"]["caption"] == "anchor"
    assert "full_stage" not in port["page"] and "caption" not in port["page"]
    assert not B.page_is_full_stage(port, "9:16")


def test_the_landscape_plot_sits_inside_the_full_stage_evidence_band(ep_dir: Path):
    boxes = LPG.page_boxes(_compile_row(ep_dir, "16:9")["page"], "16:9")
    bands = boxes[LPG.FULL_STAGE_BANDS_KEY]
    assert _inside(boxes["plot"], bands["evidence_safe"]), (boxes["plot"], bands["evidence_safe"])


def test_the_portrait_plot_sits_inside_doc49s_safe_box(ep_dir: Path):
    boxes = LPG.page_boxes(_compile_row(ep_dir, "9:16")["page"], "9:16")
    safe = _safe_box("9:16")
    assert boxes["safe"] == safe
    assert _inside(boxes["plot"], safe), (boxes["plot"], safe)
    assert LPG.FULL_STAGE_BANDS_KEY not in boxes


def test_the_data_payload_is_identical_across_the_two_aspects(ep_dir: Path):
    land = _compile_row(ep_dir, "16:9")["page"]
    port = _compile_row(ep_dir, "9:16")["page"]
    assert _data_payload(land), "the payload keys must exist, or the comparison is vacuous"
    assert "series" in _data_payload(land)
    assert _data_payload(land) == _data_payload(port)
    stripped = {k: v for k, v in land.items() if k not in ("full_stage", "caption")}
    assert stripped == port, "the stamp adds only `full_stage` and `caption`; nothing else in the page moves"
