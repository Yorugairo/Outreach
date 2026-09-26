"""R26-380 (a) - A PORTRAIT BARS PAGE KEEPS ROOM FOR A NAME'S SECOND LINE (P72 T51b, 2026-09-26).

P72 T15 measured every bar's name as the player draws it and WARNed (R26-270) where one ran into the page's foot: at
9:16 the gauge representative's two-line "Capex, next / two years" stood 12 px into its source line, and T15's own
long-name page ("Hyperscaler / capital spending") did the same, and so did P71 T25's projected representative ("2026 /
consensus", 12 px into its source; measured by this slice). The cause was the engine's: `buildLedgerBars` laid the
portrait plot's floor (the chart's height less 70) for ONE line of names - their baseline 52 under the floor, the
chart's own foot 18 under that - and `lpWrapBarLabel` then broke a wide name onto a second line 1.15 of its size lower,
off the chart and into the source.

THE LAW. The names are measured BEFORE the plot is laid, on the wrap's own rule (a space, and wider than the slot it
will be wrapped to); a portrait row with a two-line name raises its floor by that line, and the plot is a line shorter.
A row of one-line names keeps the floor it always had; the landscape and long-form floors are not touched (their
goldens pin them).
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests"))

import build_scene_timeline_f as B  # noqa: E402
import ledger_page as LPG  # noqa: E402
import measure_page_boxes as M  # noqa: E402
import served_player as SP  # noqa: E402 - R26-351: the one guarded Playwright opener

PORTRAIT_FOOT = 70          # buildLedgerBars: the portrait plot's floor is the chart's height less this
NAME_LINE = 1.15 * 40       # LPBAR_LINE_H x the portrait name's 40 px: the second line's room
LONG = {"title": "Two long names on capped bars", "sub": "Synthetic bars for the name-room test",
        "src": "Synthetic series for the name-room test; not a figure about the world", "unit": "%",
        "bars": [{"label": "Hyperscaler capital spending", "value": 62, "color": "crimson"},
                 {"label": "Everything else in the index", "value": 38, "color": "deemph"}]}
SHORT = dict(LONG, title="Two short names on capped bars",
             bars=[{"label": "Hyperscalers", "value": 62, "color": "crimson"}, {"label": "Others", "value": 38, "color": "deemph"}])


def _page(which: str) -> dict:
    if which in ("gauge", "projected"):
        return M.representative(M.STORY_GAUGE if which == "gauge" else M.STORY_PROJECTED)
    return LPG.build_spec(LONG if which == "long" else SHORT, "bars", None, "right")


def _drawn(page: dict) -> dict:
    import render_baseline as RB
    w, h = RB.STAGE["9:16"]
    td = tempfile.TemporaryDirectory()
    html = Path(td.name) / "names.html"
    tl = M._timeline(page, "9:16")
    html.write_text(RB.instantiate(tl, {"__audio__": M._silence(), **B.longform_assets(tl)}), encoding="utf-8")
    with SP.served(html, w, h, cleanup=td.cleanup) as (pg, errs):
        RB.frame_png(pg, M.MEASURE_T, (w, h))
        dom = pg.evaluate(M.READ_BOXES)
    assert not errs, errs
    return dom


def _meets(a: dict, b: dict) -> bool:
    return min(a["x"] + a["w"], b["x"] + b["w"]) > max(a["x"], b["x"]) and min(a["y"] + a["h"], b["y"] + b["h"]) > max(a["y"], b["y"])


@pytest.fixture(scope="module")
def reads() -> dict:
    return {k: _drawn(_page(k)) for k in ("gauge", "projected", "long", "short")}


@pytest.mark.parametrize("which", ["gauge", "projected", "long"])
def test_a_two_line_name_stands_clear_of_the_source_and_the_caption(reads, which):
    page, dom = _page(which), reads[which]
    names = [dict(M._box(n), lines=n["lines"]) for n in dom[LPG.BAR_NAMES_KEY]]
    assert any(n["lines"] == 2 for n in names), f"{which}: the page must carry a two-line name to test: {names}"
    boxes = dict(LPG.page_boxes(page, "9:16"), source=M._box(dom["source"]), **{LPG.BAR_NAMES_KEY: names})
    for n in names:
        assert not _meets(n, boxes["source"]), f"{which}: {n} runs into the source line {boxes['source']}"
        assert not _meets(n, boxes["caption_anchor"]), f"{which}: {n} runs into the caption band {boxes['caption_anchor']}"
    assert LPG.bar_name_findings(boxes) == [], "R26-270's WARN has nothing left to say"


@pytest.mark.parametrize("which,lift", [("short", 0.0), ("long", NAME_LINE), ("gauge", NAME_LINE), ("projected", NAME_LINE)])
def test_the_floor_rises_by_one_name_line_only_when_a_name_wraps(reads, which, lift):
    dom = reads[which]
    chart, plot = M._box(dom["chart"]), M._box(dom["plot"])
    lines = [n["lines"] for n in dom[LPG.BAR_NAMES_KEY]]
    assert (max(lines) == 2) == (lift > 0), (which, lines)
    floor = chart["y"] + chart["h"] - PORTRAIT_FOOT - lift
    assert abs(plot["y"] + plot["h"] - floor) <= 1.0, (which, plot, chart, lift)
