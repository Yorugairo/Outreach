"""CHART CARD (R26-19 / E50, P47 T6): a ledger page rendered once at its landing to a PNG that docks as a card.

The page box is found on the pixels (the charcoal ground between the stage's black and the cream deckle); the card is the
page, not the stage; it renders from the object's own ledger_page spec through the same player. The Fed object on disk
(evidence/objects/ev-fed-vs-yields-v1.series.json, FRED, fetched with proof lines) is the input - no network in the test.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
import chart_card as CC  # noqa: E402

FED = ROOT / "content/video_engine/projects/systems-and-blowups/tokyo-tea-break/evidence/objects/ev-fed-vs-yields-v1.series.json"


def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")


def test_page_box_finds_the_charcoal_page_between_the_black_stage_and_the_cream_deckle():
    from PIL import Image
    im = Image.new("RGB", (400, 200), (0, 0, 0))
    px = im.load()
    for x in range(60, 340):
        for y in range(20, 180):
            px[x, y] = (238, 226, 200)        # the cream deckle
    for x in range(80, 320):
        for y in range(40, 160):
            px[x, y] = (30, 42, 54)           # the charcoal page
    assert CC.page_box(im) == (80, 40, 240, 120)
    assert CC.page_box(Image.new("RGB", (50, 50), (0, 0, 0))) == (0, 0, 50, 50), "no page found = the whole frame, never a crash"


def test_the_fed_object_carries_its_proof_lines_and_its_facts_are_read_not_typed():
    import json
    obj = json.loads(FED.read_text(encoding="utf-8"))
    assert obj["status"] == "REAL" and len(obj["series"]) == 3
    assert {p["series"] for p in obj["proof"]} == {"DFEDTARU", "DGS10", "MORTGAGE30US"}
    for p in obj["proof"]:
        assert p["url"].startswith("https://fred.stlouisfed.org/graph/fredgraph.csv?id=") and len(p["sha256"]) == 64
        assert (FED.parent.parent / p["path"].split("evidence/", 1)[1]).exists() or (ROOT / "content/video_engine/projects/systems-and-blowups/tokyo-tea-break" / p["path"]).exists()
    f = obj["facts"]
    fed = obj["series"][0]["pts"]
    assert all(abs(v - f["fed_target_upper"]) < 1e-9 for _x, v in fed[-5:]), "the Fed line is flat at the facts' target over its tail"
    assert f["dgs10_rise_bp_from_low"] > 0 and f["mortgage_rise_bp_from_low"] > 0, "the borrowing costs climbed - measured, not asserted"


@needs_browser
def test_the_card_is_the_page_not_the_stage(tmp_path: Path):
    out = CC.render_card(FED, tmp_path / "card.png", width=720)
    from PIL import Image
    im = Image.open(out)
    w, h = im.size
    assert w == 720 and 300 < h < 520, f"a landscape page box scaled to the dock width, not the 16:9 stage (405 tall): {im.size}"
    px = im.load()
    edges = [px[w // 2, 2], px[w // 2, h - 3], px[2, h // 2], px[w - 3, h // 2]]   # the edge midpoints (the corners are rounded and show the deckle)
    assert all(c[2] >= c[0] and 15 < c[0] < 80 for c in edges), f"the card's edges are the page's charcoal, not the stage's black or the deckle: {edges}"
