"""P72 T53 (b) + (e) (R26-412 (b), (e); P71 T34's findings) - THE GROUP BRACKET AND THE LEVEL ACROSS TO A FAR BAR.

(b) A16 (BRAVOS-USE-WHEN: "a label covers a whole group (several bars, a diagram)"; CHN 18:18 "take decades to play out" -
    one span over the group, dashed ends reaching down to it, "Decades" over it). A bars bracket measured two bar TOPS and
    had no group form (T34: "no card spans a group of bars first..last with one label"). `form: "group"` on a BARS page:
    `from` .. `to` two bars, every bar between them inside - ONE horizontal span over the group, from the first bar's left
    edge to the last bar's right edge, clear over the group's ink (its bars and their printed values), a tick dropping
    from each end toward the group, the label centred above. Refused by name off a bars page, and on one bar.
(e) STK 2:16: the tall bar's level runs across to the low bar as a dashed line. Ours stood the span beside the far-right
    bar and its foot tick joined nothing when the low bar was two bars away (T34's ratio beat: "the span stands beside the
    150 bar from the 28 LEVEL, its foot tick joins nothing"). Now, on a bars page, when the two bars are NOT adjacent the
    far bar's level is drawn dashed from the span across to that bar's side - broken where a bar between stands through
    the level (it passes BEHIND the bars, never across their ink). Adjacent bars are untouched (the span stands beside the
    near one, the tick at its neighbour's level - R26-272's layout, to the byte).

The fixture copies H row 16's three issuance values (the dossier's C1 bars: 2020-24 a year, 2025, 2026E top of range) so
this file never reads an untracked series; the goldens read the committed series file.
"""
from __future__ import annotations

import copy
import json
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests/golden"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests"))

import build_scene_timeline_f as B  # noqa: E402
import render_baseline as RB  # noqa: E402
import build_golden_sources as G  # noqa: E402

import served_player as SP  # noqa: E402 - R26-351: the one guarded Playwright opener

STILL = (0, 0, 0)
ASPECT = "16:9"
BK_AT, BK_S = 8.0, 1.8
ISSUANCE = {"title": "The builders started borrowing",
            "sub": "Hyperscaler bond issuance, US$ billions a year - 2020-24 an average; 2026E the top of the range",
            "src": "fixture - H row 16's three bars", "unit": "$", "unit_suffix": "B",
            "bars": [{"label": "2020-24, a year", "value": 28, "color": "deemph"},
                     {"label": "2025", "value": 121, "color": "deemph"},
                     {"label": "2026E, top of range", "value": 150, "color": "crimson"}]}
RATIO = {"kind": "bracket", "at": BK_AT, "dur": BK_S, "from": 0, "to": 2, "label": "5.4x", "sub": "2026E on the 2020-24 year"}
GROUP = {"kind": "bracket", "form": "group", "at": BK_AT, "dur": BK_S, "from": 1, "to": 2, "label": "the new borrowing"}

PROBE = """() => {
  const w = [wB, wA].find(e => e.__lp && e.classList.contains('ledger')); if (!w) return null;
  const st = w.__lp, PF = st.perform || { brackets: [] };
  const bars = (st.marks || []).filter(m => m.role === 'bar').map(m => m.geom);
  const box = (el) => { if (!el) return null; const b = el.getBBox(); return [b.x, b.y, b.width, b.height]; };
  const brackets = (PF.brackets || []).map(b => ({
    x: b.x, y0: b.y0, y1: b.y1, group: !!b.group, opacity: +(b.main.g.getAttribute('opacity') || 0),
    offset: +(b.main.line.getAttribute('stroke-dashoffset') || 0), len: b.main.len, line: box(b.main.line),
    lineD: b.main.line.getAttribute('d'), label: box(b.main.label), anchor: b.main.label.getAttribute('text-anchor'),
    glyphs: b.main.lg.map(ts => +(ts.getAttribute('opacity') || 0)),
    ticks: [b.main.t0, b.main.t1].map(tk => tk ? { d: tk.getAttribute('d'), tf: tk.getAttribute('transform') || '' } : null),
    level: b.main.level ? b.main.level.getAttribute('d') || '' : null,
    levelDash: b.main.level ? b.main.level.getAttribute('stroke-dasharray') : null }));
  const vals = (st.bars || []).map(b => (b.val && b.val.style.display !== 'none') ? box(b.val) : null);
  return { bars, brackets, vals };
}"""


def bars_timeline(tmp: Path, species: list[dict], obj: dict = ISSUANCE, aspect: str = ASPECT) -> tuple[dict, dict]:
    (tmp / "evidence/objects").mkdir(parents=True, exist_ok=True)
    (tmp / "evidence/objects/fx-bars.series.json").write_text(json.dumps(obj), encoding="utf-8")
    plate = "ledger:fx-bars:bars"
    saved = B.ASPECT
    B.ASPECT = aspect
    try:
        world = B.world_for_plate(plate, STILL, tmp)
        B.stamp_full_stage(world["page"])
        assert B.validate_species(copy.deepcopy(species), STILL, plate) == []
        B.check_brace(world["page"], copy.deepcopy(species), aspect)
    finally:
        B.ASPECT = saved
    scenes = [{"scene_id": "s01", "world": dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}),
               "exit": "cut", "span": [0.0, G.RUNTIME], "docks": [], "species": copy.deepcopy(species)}]
    return G._timeline("P72 T53: the group bracket and the level", scenes, {}, aspect), G._base_uris()


class Served:
    def __init__(self, timeline: dict, uris: dict, aspect: str = ASPECT):
        self._td = tempfile.TemporaryDirectory()
        html = Path(self._td.name) / "bars.html"
        html.write_text(RB.instantiate(timeline, uris), encoding="utf-8")
        self.w, self.h = RB.STAGE[aspect]
        self.page, self.errs, self._close = SP.open_served(html, self.w, self.h, cleanup=self._td.cleanup)

    def at(self, t: float) -> dict:
        self.page.evaluate("t => { const s = document.getElementById('scrub'); s.value = t; s.dispatchEvent(new Event('input', {bubbles:true})); }", t)
        return self.page.evaluate(PROBE)

    def close(self) -> None:
        self._close()


def _meets(a, b) -> bool:
    return a[0] < b[0] + b[2] and b[0] < a[0] + a[2] and a[1] < b[1] + b[3] and b[1] < a[1] + a[3]


def _segments(d: str) -> list[tuple[float, float, float]]:
    """(x0, x1, y) per 'M x y L x y' pair of a level path."""
    nums = [float(v) for v in d.replace("M", " ").replace("L", " ").split()]
    return [(min(nums[k], nums[k + 2]), max(nums[k], nums[k + 2]), nums[k + 1]) for k in range(0, len(nums), 4)]


# ---- the compiler: the group form, refused by name where it cannot stand -----------------------------------------------

def test_the_group_form_is_a_bracket_form_and_its_ends_are_two_bars():
    assert "group" in B.BRACKET_FORMS
    assert B.validate_species([dict(GROUP)], STILL, "ledger:x:bars") == []
    errs = B.validate_species([dict(GROUP, to=1)], STILL, "ledger:x:bars")
    assert any("group" in e and "two bars" in e for e in errs), errs
    errs = B.validate_species([dict(GROUP, bar=1)], STILL, "ledger:x:bars")
    assert any("'bar'" in e for e in errs), ("a brace's key on a group is refused by name", errs)


def test_a_group_off_a_bars_page_is_refused_by_name():
    line = {"variant": "line", "series": [{"pts": [[0, 1], [1, 2]]}]}
    with pytest.raises(ValueError, match="group"):
        B.check_brace(line, [dict(GROUP)], ASPECT)
    bars = {"variant": "bars", "values": [28, 121, 150], "labels": ["a", "b", "c"]}
    with pytest.raises(ValueError, match="bar 5"):
        B.check_brace(bars, [dict(GROUP, to=5)], ASPECT)
    assert B.check_brace(bars, [dict(GROUP)], ASPECT) == []


# ---- the player -----------------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("aspect", ["16:9", "9:16"])
def test_the_group_bracket_spans_its_bars_under_one_label(aspect):
    with tempfile.TemporaryDirectory() as td:
        timeline, uris = bars_timeline(Path(td), [GROUP], aspect=aspect)
    P = Served(timeline, uris, aspect)
    try:
        before = P.at(BK_AT - 0.5)
        assert len(before["brackets"]) == 1, "the group bracket is built on a bars page"
        assert before["brackets"][0]["opacity"] == 0, "and not on the page before its word"
        s = P.at(BK_AT + BK_S + 0.4)
        bk, bars = s["brackets"][0], s["bars"]
        assert bk["group"], "built as the group form"
        g1, g2 = bars[1], bars[2]
        x0, x1 = min(g1["x"], g2["x"]), max(g1["x"] + g1["w"], g2["x"] + g2["w"])
        L = bk["line"]
        assert abs(L[0] - x0) < 1.0 and abs(L[0] + L[2] - x1) < 1.0, ("ONE span from the first bar's left edge to the last's right", L, x0, x1)
        assert L[3] < 1.0, "a horizontal span"
        assert not _meets(L, [bars[0]["x"], bars[0]["y"], bars[0]["w"], bars[0]["h"]]), "a bar outside the group is not under it"
        ink = [[b["x"], b["y"], b["w"], b["h"]] for b in (g1, g2)] + [v for v in s["vals"][1:3] if v]
        top = min(r[1] for r in ink)
        assert L[1] < top, ("the span stands clear OVER the group's ink - its bars and their printed values", L, top)
        lab = bk["label"]
        assert bk["anchor"] == "middle" and abs(lab[0] + lab[2] / 2 - (x0 + x1) / 2) < 2.0, "the label centred over the group"
        assert lab[1] + lab[3] <= L[1] + 1.0, ("the label stands above the span", lab, L)
        for r in ink:
            assert not _meets(lab, r), ("the label never writes on the group's ink", lab, r)
        assert bk["opacity"] == 1 and bk["offset"] < 0.5 and all(g == 1 for g in bk["glyphs"]), "drawn whole, written whole"
        for tk in bk["ticks"]:
            assert tk and "scale(1 1" in tk["tf"].replace(".0000", ""), ("each end's tick dropped whole", tk)
        assert not P.errs, P.errs
    finally:
        P.close()


def test_the_group_draws_on_the_brackets_clock():
    with tempfile.TemporaryDirectory() as td:
        timeline, uris = bars_timeline(Path(td), [GROUP])
    P = Served(timeline, uris)
    try:
        mid = P.at(BK_AT + BK_S * 0.25)["brackets"][0]
        assert 0 < mid["offset"] < mid["len"], ("the span draws by length on its word", mid["offset"], mid["len"])
        assert all(g == 0 for g in mid["glyphs"]), "the label waits for the span"
        assert not P.errs, P.errs
    finally:
        P.close()


@pytest.mark.parametrize("aspect", ["16:9", "9:16"])
def test_the_far_bars_level_runs_across_to_it_behind_the_bars_between(aspect):
    with tempfile.TemporaryDirectory() as td:
        timeline, uris = bars_timeline(Path(td), [RATIO], aspect=aspect)
    P = Served(timeline, uris, aspect)
    try:
        s = P.at(BK_AT + BK_S + 0.4)
        bk, bars = s["brackets"][0], s["bars"]
        assert bk["level"], "R26-412 (e): the far bar's level is drawn - the foot tick joined nothing"
        assert bk["levelDash"], "dashed, as STK 2:16 draws it"
        segs = _segments(bk["level"])
        b0 = bars[0]
        y_far = b0["end"]
        assert all(abs(y - y_far) < 0.6 for _, _, y in segs), ("the level runs at the far bar's top", segs, y_far)
        assert max(x1 for _, x1, _ in segs) >= bk["x"] - 1.0, "it starts at the span"
        near = b0["x"] + b0["w"]
        assert abs(min(x0 for x0, _, _ in segs) - near) < 8.0, ("and reaches the far bar's own side", segs, near)
        for b in bars[1:]:
            rect = [b["x"], b["y"], b["w"], b["h"]]
            for x0, x1, y in segs:
                assert not _meets([x0, y - 0.5, x1 - x0, 1.0], rect), ("the level passes BEHIND a bar between, never across its ink", (x0, x1), rect)
        assert not P.errs, P.errs
    finally:
        P.close()


def test_the_level_waits_for_the_span_and_adjacent_bars_draw_none():
    with tempfile.TemporaryDirectory() as td:
        timeline, uris = bars_timeline(Path(td), [RATIO, dict(RATIO, at=BK_AT + 4, **{"from": 1, "to": 2, "label": "1.2x", "sub": ""})])
    P = Served(timeline, uris)
    try:
        early = P.at(BK_AT + BK_S * 0.3)["brackets"][0]
        assert not early["level"], "the level waits until the span has drawn"
        s = P.at(BK_AT + 4 + BK_S + 0.4)
        assert s["brackets"][0]["level"], "the far level holds"
        assert not s["brackets"][1]["level"], "adjacent bars: the tick meets its neighbour's level - no line (R26-272's layout)"
        assert not P.errs, P.errs
    finally:
        P.close()
