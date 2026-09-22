"""R26-230: explicit full-stage bands keep the page re-stageable."""
from __future__ import annotations

import copy
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import ledger_page as LPG  # noqa: E402
import measure_page_boxes as M  # noqa: E402


def _inside(inner: dict, outer: dict, *, tolerance: int = 1) -> bool:
    return (inner["x"] >= outer["x"] - tolerance
            and inner["y"] >= outer["y"] - tolerance
            and inner["x"] + inner["w"] <= outer["x"] + outer["w"] + tolerance
            and inner["y"] + inner["h"] <= outer["y"] + outer["h"] + tolerance)


def _data_payload(page: dict) -> dict:
    return {key: copy.deepcopy(page.get(key))
            for key in ("labels", "values", "value_strings", "colors", "series", "periods",
                        "start", "end", "display_labels", "denominator", "axes")
            if key in page}


def test_full_stage_bands_are_derived_from_existing_geometry_constants_only():
    page = M.representative("dense-line")
    full = LPG.page_boxes(dict(page, full_stage=True), "16:9")
    bands = full[LPG.FULL_STAGE_BANDS_KEY]
    stage_w, stage_h = LPG.STAGE_PX["16:9"]
    safe_x, _safe_y, safe_w, _safe_h = LPG.SAFE_BOX["16:9"]
    caption_top = LPG.CAPTION_ANCHOR["16:9"][1]
    evidence_top = round(LPG.LAND_FULL["Y"] * stage_h)

    assert bands["top"] == {"x": 0, "y": 0, "w": stage_w, "h": evidence_top}
    assert bands["bottom"] == {"x": 0, "y": caption_top, "w": stage_w, "h": stage_h - caption_top}
    assert bands["evidence_safe"] == {"x": safe_x, "y": evidence_top, "w": safe_w,
                                       "h": caption_top - evidence_top}

    assert LPG.FULL_STAGE_BANDS_KEY not in LPG.page_boxes(page, "16:9")
    assert LPG.FULL_STAGE_BANDS_KEY not in LPG.page_boxes(dict(page, full_stage=True), "9:16")


@pytest.mark.parametrize("builder", ("dense-line", "story"))
def test_representative_full_stage_plot_and_ink_respect_the_named_bands(builder: str):
    page = M.representative(builder)
    boxes = LPG.page_boxes(dict(page, full_stage=True), "16:9")
    bands = boxes[LPG.FULL_STAGE_BANDS_KEY]

    assert _inside(boxes["plot"], bands["evidence_safe"]), (builder, boxes["plot"], bands)
    assert boxes["title"]["y"] + boxes["title"]["h"] <= bands["top"]["y"] + bands["top"]["h"]
    assert boxes["sub"]["y"] + boxes["sub"]["h"] <= bands["top"]["y"] + bands["top"]["h"]
    assert boxes["source"]["y"] >= bands["bottom"]["y"]


@pytest.mark.parametrize("builder", ("dense-line", "story"))
def test_restage_keeps_data_values_and_portrait_plot_inside_doc49_safe_box(builder: str):
    page = M.representative(builder)
    stamped = dict(page, full_stage=True)
    before = copy.deepcopy(stamped)
    landscape = LPG.page_boxes(stamped, "16:9")
    portrait = LPG.page_boxes(stamped, "9:16")

    assert stamped == before
    assert _data_payload(stamped) == _data_payload(page)
    assert LPG.page_ink_key(stamped) == LPG.page_ink_key(page)
    safe = portrait["safe"]
    assert _inside(portrait["plot"], safe), (builder, portrait["plot"], safe)
    assert LPG.FULL_STAGE_BANDS_KEY not in portrait
    assert landscape["aspect"] == "16:9"


def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            browser.close()
        return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")


@needs_browser
@pytest.mark.parametrize("builder", ("dense-line", "story"))
def test_browser_representatives_keep_measured_plot_inside_full_stage_evidence_band(builder: str):
    """Use the current player measurement when Chromium is available, not only the Python mirror."""
    measured = M.measure(builder, "16:9", full_stage=True)
    actual = measured["boxes"]
    bands = LPG.page_boxes(measured["page"], "16:9")[LPG.FULL_STAGE_BANDS_KEY]

    assert _inside(actual["plot"], bands["evidence_safe"]), (builder, actual["plot"], bands)
    assert actual["title"]["y"] + actual["title"]["h"] <= bands["top"]["y"] + bands["top"]["h"]
    assert actual["sub"]["y"] + actual["sub"]["h"] <= bands["top"]["y"] + bands["top"]["h"]
    assert actual["source"]["y"] >= bands["bottom"]["y"]
