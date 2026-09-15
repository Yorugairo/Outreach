"""G49 (thumbnail-text-clipping, ledger 3570a6280d20): the operator said the headline was "still
aprtially cut" and no gate could see it, because G45 and J12 read the WORDS. These fixtures are the
pixels: a 1280x720 thumbnail whose headline runs 40 px off the right edge, its sticker off the top,
and the same layout re-lined so both clear - plus the probed reader on a page's landing frame."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
import gate_thumbnail_text as T  # noqa: E402

FRAME = (1280.0, 720.0)
# the thumbnail the operator was looking at: the headline's last word past the right edge, the
# "+$6,240 TAX" sticker pushed off the top - and the by-line, which is fine
CUT = {"frame": [1280, 720], "boxes": [
    {"role": "headline", "text": "THE TARIFF TRAP", "box": [420, 96, 900, 180]},
    {"role": "sticker", "text": "+$6,240 TAX", "box": [140, -24, 300, 120]},
    {"role": "byline", "text": "Money Physics", "box": [80, 600, 320, 60]},
]}
CLEAR = {"frame": [1280, 720], "boxes": [
    {"role": "headline", "text": "THE TARIFF TRAP", "box": [200, 96, 900, 180]},
    {"role": "sticker", "text": "+$6,240 TAX", "box": [140, 24, 300, 120]},
    {"role": "byline", "text": "Money Physics", "box": [80, 600, 320, 60]},
]}


def _gate(doc, **kw):
    boxes, frame = T.boxes_from_layout(doc)
    return T.gate(boxes, frame, **kw)


def test_g49_names_every_clipped_box_and_the_px_at_display_size():
    g = _gate(CUT)
    assert g.level == "FAIL", g.message
    assert "2 of 3 text box(es) clipped" in g.message, g.message
    assert "headline:THE TARIFF TRAP" in g.message and "40 px off the right edge" in g.message, g.message
    assert "sticker:+$6,240 TAX" in g.message and "24 px off the top edge" in g.message, g.message
    # the number the operator is actually looking at: the cut measured where the thumbnail is read
    assert "10.0 px at 320 wide" in g.message, g.message
    # the box that clears every edge is not named
    assert "Money Physics" not in g.message, g.message


def test_g49_passes_the_relined_layout():
    g = _gate(CLEAR)
    assert g.level == "PASS", g.message
    assert "3 text box(es) all inside the 1280x720 frame by 0 px" in g.message, g.message


def test_g49_margin_is_the_dial_and_defaults_to_the_edge_itself():
    """Default 0 px: FAIL only when a box is ACTUALLY clipped - the complaint and nothing more. Raise the
    dial and a box merely flush with the edge is refused too."""
    assert T.MARGIN_PX == 0.0
    assert _gate(CLEAR, margin=0.0).level == "PASS"
    assert _gate(CLEAR, margin=30.0).level == "FAIL"        # the sticker sits 24 px from the top
    assert "sticker:+$6,240 TAX" in _gate(CLEAR, margin=30.0).message


def test_g49_worst_edge_first_and_a_box_outside_on_two_edges_is_named_once():
    boxes = [("corner", (-50.0, -10.0, 100.0, 40.0))]
    cuts = T.clipped(boxes, FRAME)
    assert len(cuts) == 1 and cuts[0].edge == "left" and cuts[0].px == 50.0


def test_g49_is_info_when_there_is_no_text_to_measure():
    """Measured or named, never a silent skip - M18's and M25's pattern."""
    g = _gate({"frame": [1280, 720], "boxes": []})
    assert g.level == "INFO" and "no text box to measure" in g.message, g.message


def test_g49_reads_a_pages_landing_frame_from_the_probe(tmp_path):
    """E67 s4: the chart IS the thumbnail, and probe.py --gate already wrote its boxes. The nearest
    instant to --at is the frame; the stage the probe names is the frame's size."""
    doc = {"aspect": "9:16", "instants": [
        {"t": 4.0, "page": {"title": [80, 200, 900, 90]}, "labels": []},
        {"t": 9.0, "page": {"title": [80, 200, 900, 90], "source": [80, 1880, 700, 60]},
         "labels": [{"role": "sname", "text": "10-year", "box": [700, 900, 460, 50]}]},
    ]}
    p = tmp_path / "layout-probe.json"
    p.write_text(json.dumps(doc), encoding="utf-8")
    boxes, frame, t = T.boxes_from_probe(json.loads(p.read_text(encoding="utf-8")), 9.0)
    assert t == 9.0 and frame == (1080.0, 1920.0)
    g = T.gate(boxes, frame)
    assert g.level == "FAIL", g.message
    assert "sname:10-year" in g.message and "80 px off the right edge" in g.message, g.message   # 700+460 = 1160
    assert "page.source" in g.message and "20 px off the bottom edge" in g.message, g.message    # 1880+60 = 1940
    assert "page.title" not in g.message, g.message
