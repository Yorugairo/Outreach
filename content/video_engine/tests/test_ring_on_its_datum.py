"""P72 T48 / R26-367 - A RING ON A CHART CIRCLES ITS DATUM (E56; s106).

The operator, 2026-09-25, on the `chart-callout` golden: *"why is the ring completely missing the line?"* - its callout
was authored at a hand-typed STAGE point over a docked chart, never bound to a datum, so the ellipse sat 40 px above
the line (measured: centre (1382, 454), half-axes 23 x 19; the semiconductor line's datum 152 at (1391, 492)). And a
datum could not be named on a DOCKED chart at all: the engine resolved a datum only against a ledger page.

What this file holds the compiler, the engine and the probe to:

  (1) THE TARGET    `{"kind": "datum", "dock": <the row's dock index | its evidence id>, "series", "index"}` names a
                    datum on THAT docked chart - for the painted marks (callout, ring, spotlight, squiggle) and, since
                    P72 T46f (R26-373 (c)), punch / focus_zoom (render() lays the docks out before such a move reads
                    it - test_wave3_carries.py); any other kind is refused by name.
  (2) TRUTH         the dock must be on the row, on the stage at the mark's `at`, and carry a drawn chart; the series and
                    the index must exist on it - a target that resolves to nothing is refused by name (a truth rule).
  (3) THE ENGINE    resolves it against the dock's own drawn line through the dock's transform at t, and paints it
                    ABOVE the card (it annotates the card itself - E49's layer rule); a datum with no `dock` keeps the
                    page's layer, beneath the docks, and its bytes.
  (4) THE GOLDEN    `chart-callout` names `{dock: 0, series: 1, index: 152}` and its callout sits on the line.
  (5) THE PROBE     reads a docked chart's drawn lines as it reads a page's; a POINT-target callout / ring / spotlight /
                    squiggle / punch over a chart's plot, farther from every drawn line than its own reach, is M49's WARN
                    (s106 - advice, never a refusal) naming the mark, the distance in px and the nearest datum; one on
                    the line, or over no chart, is not a finding.
"""
from __future__ import annotations

import copy
import math
import re
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests/golden"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests"))

import build_scene_timeline_f as B  # noqa: E402
import build_golden_sources as G  # noqa: E402
import gate_motion_density as MG  # noqa: E402
import probe as PR  # noqa: E402
import served_player as SPL  # noqa: E402

SPECIES_DIR = ROOT / "content/video_engine/scripts/species"
BOUND = {"kind": "datum", "dock": 0, "series": 1, "index": 152}
OLD_POINT = {"kind": "point", "x": 0.72, "y": 0.42}
AID = "ev-golden-chart"
T_JUDGED = 12.0   # the golden's judged instant (build_golden_sources.JUDGED_T): the line drawn, the ring closed


# ---- (4) the golden --------------------------------------------------------------------------------------------

def test_the_golden_callout_names_its_datum_on_the_docked_chart():
    tl, _uris = G.chart_callout()
    (sp,) = tl["scenes"][0]["species"]
    assert sp["kind"] == "callout"
    assert sp["target"] == BOUND


# ---- (1) the target's grammar --------------------------------------------------------------------------------------

@pytest.mark.parametrize("kind", ["callout", B.SPECIES_RING, "spotlight", "squiggle"])
@pytest.mark.parametrize("dock", [0, AID])
def test_a_painted_mark_may_name_a_datum_on_a_dock(kind, dock):
    tgt = dict(BOUND, dock=dock)
    assert B._validate_target(kind, tgt, B.SPECIES_TARGETS[kind]) == []


@pytest.mark.parametrize("kind", ["pull_back", "build_to", "figure", "camera"])   # P72 T46f: punch / focus_zoom admitted (R26-373 (c))
def test_any_other_datum_on_a_dock_is_refused_by_name(kind):
    allowed = B.SPECIES_TARGETS.get(kind, B.TARGET_KINDS)
    errs = B._validate_target(kind, dict(BOUND), allowed)
    assert errs and any("dock" in e and kind in e for e in errs), errs


@pytest.mark.parametrize("bad", [True, -1, "", "  ", 1.5, None, [0]])
def test_a_malformed_dock_is_refused_by_name(bad):
    errs = B._validate_target("callout", dict(BOUND, dock=bad), B.SPECIES_TARGETS["callout"])
    assert errs and any("'dock'" in e for e in errs), errs


def test_a_datum_with_no_dock_is_validated_as_it_was():
    assert B._validate_target("callout", {"kind": "datum", "index": 3}, B.SPECIES_TARGETS["callout"]) == []


# ---- (2) truth: the dock is on the row, on the stage, and carries the datum ---------------------------------------

def _row(target: dict, at: float = 10.0, kind: str = "callout") -> list[dict]:
    return [{"kind": kind, "at": at, "dur": 6.0, "target": target}]


def _docks() -> list[dict]:
    return [{"slide": "ev-card", "slot": 0, "enter": 1.0, "exit": 30.0},
            {"slide": AID, "slot": 1, "enter": 2.0, "exit": 30.0}]


def _evidence() -> dict:
    chart = {"series": [{"pts": [[i, i] for i in range(10)]}, {"pts": [[i, 2 * i] for i in range(6)]}]}
    return {"ev-card": {"species": "deck", "badges": []}, AID: {"species": "chart", "chart": chart, "badges": []}}


@pytest.mark.parametrize("dock", [1, AID])
def test_a_bound_datum_on_the_row_s_chart_dock_passes(dock):
    assert B.dock_datum_errors(_row(dict(BOUND, dock=dock, index=5)), _docks(), _evidence(), "row 1") == []


@pytest.mark.parametrize("target,needle", [
    (dict(BOUND, dock=4, index=5), "not on this row"),
    (dict(BOUND, dock="ev-elsewhere", index=5), "not on this row"),
    (dict(BOUND, dock=0, index=5), "no drawn chart"),
    (dict(BOUND, dock=1, series=2, index=5), "series 2"),
    (dict(BOUND, dock=1, series=1, index=6), "index 6"),
])
def test_a_datum_that_resolves_to_nothing_is_refused_by_name(target, needle):
    errs = B.dock_datum_errors(_row(target), _docks(), _evidence(), "row 1")
    assert len(errs) == 1 and needle in errs[0] and "row 1" in errs[0] and "callout" in errs[0], errs


@pytest.mark.parametrize("at,needle", [(1.5, "not arrived"), (30.0, "LEFT")])
def test_a_datum_on_a_dock_off_the_stage_is_refused(at, needle):
    errs = B.dock_datum_errors(_row(dict(BOUND, dock=1, index=5), at=at), _docks(), _evidence(), "row 1")
    assert len(errs) == 1 and needle in errs[0], errs


def test_a_panel_chart_names_its_panel():
    ev = _evidence()
    ev[AID]["chart"] = {"panels": [{"series": [{"pts": [[0, 1], [1, 2]]}]}, {"series": [{"pts": [[0, 1]] * 4}]}]}
    ok = B.dock_datum_errors(_row(dict(BOUND, dock=1, series=0, index=3, panel=1)), _docks(), ev, "row 1")
    bad = B.dock_datum_errors(_row(dict(BOUND, dock=1, series=0, index=3, panel=2)), _docks(), ev, "row 1")
    assert ok == [] and len(bad) == 1 and "panel 2" in bad[0], (ok, bad)


def test_a_row_with_no_dock_datum_says_nothing():
    rows = [_row(OLD_POINT), _row({"kind": "datum", "index": 3}), [], None]
    assert all(B.dock_datum_errors(r, _docks(), _evidence(), "row 1") == [] for r in rows)


@pytest.mark.parametrize("bad", [True, -1, "", 1.5, [0]])
def test_a_malformed_target_is_left_to_the_shape_check_never_a_crash(bad):
    assert B.dock_datum_errors(_row(dict(BOUND, dock=bad, index=5)), _docks(), _evidence(), "row 1") == []
    assert B.dock_datum_errors(_row(dict(BOUND, dock=1, index="5")), _docks(), _evidence(), "row 1") == []


def test_the_compiler_checks_the_row_where_its_docks_are_compiled():
    import inspect
    src = inspect.getsource(B.main)
    assert "dock_datum_errors(row_species, docks, evidence" in src


# ---- (5) the probe's reach, mirrored from the painters ------------------------------------------------------------

def _mjs_num(path: Path, key: str) -> float:
    m = re.search(rf"\b{key}:\s*([0-9.]+)", path.read_text(encoding="utf-8"))
    assert m, (path.name, key)
    return float(m.group(1))


def test_the_probe_s_reach_is_the_painters_own():
    assert PR.MARK_REACH["callout"] == (_mjs_num(SPECIES_DIR / "callout.mjs", "RX_PAD"),
                                        _mjs_num(SPECIES_DIR / "callout.mjs", "RY_PAD"))
    ring = SPECIES_DIR / "ring.mjs"
    assert PR.MARK_REACH["ring"] == (max(_mjs_num(ring, "MIN_RX"), _mjs_num(ring, "RX_PAD")),
                                     max(_mjs_num(ring, "MIN_RY"), _mjs_num(ring, "RY_PAD")))
    spot = SPECIES_DIR / "spotlight.mjs"
    r = _mjs_num(spot, "W_MIN") / 2 + _mjs_num(spot, "PAD")
    assert PR.MARK_REACH["spotlight"] == (r, r)
    assert set(PR.MARK_REACH) == set(PR.REACH_MARK_KINDS)


def test_mark_reach_scales_with_a_pad():
    assert PR.mark_reach({"kind": "callout", "pad": 10}) == (PR.MARK_REACH["callout"][0] + 10,
                                                             PR.MARK_REACH["callout"][1] + 10)


# ---- (5) M49: the gate row, pure -----------------------------------------------------------------------------------

def _reading(dist: float, norm: float, at: float = 10.0, t: float = 12.0) -> dict:
    return {"kind": "callout", "scene": "s01", "at": at, "t": t, "chart": f"dock {AID}", "dist_px": dist, "norm": norm,
            "series": 1, "datum": 152, "reach": [22.0, 18.0], "centre": [1382.4, 453.6]}


def test_m49_warns_a_mark_off_every_line_by_name_distance_and_datum():
    g = MG._mark_reach_gate({"instants": [{"t": 12.0, "mreach": [_reading(39.6, 2.2)]}]})
    assert g.id == "M49" and g.level == "WARN", g
    assert "callout" in g.message and "40 px" in g.message and "series 1" in g.message and "datum 152" in g.message, g.message


def test_m49_passes_a_mark_that_reaches_its_line_at_any_instant_of_its_window():
    doc = {"instants": [{"t": 10.1, "mreach": [_reading(39.6, 2.2, t=10.1)]}, {"t": 12.0, "mreach": [_reading(3.0, 0.2)]}]}
    g = MG._mark_reach_gate(doc)
    assert g.level == "PASS", g


def test_m49_is_silent_with_no_point_mark_over_a_chart():
    assert MG._mark_reach_gate({"instants": [{"t": 1.0}]}) is None
    assert MG._mark_reach_gate(None) is None and MG._mark_reach_gate("stale") is None


def test_m49_never_fails():
    g = MG._mark_reach_gate({"instants": [{"t": 12.0, "mreach": [_reading(900.0, 50.0)]}]})
    assert g.level == "WARN"


# ---- (3) + (4) + (5) in the browser ----------------------------------------------------------------------------------

READ_CO = r"""() => {
  const sb = document.getElementById('stage').getBoundingClientRect(), k = 1920 / Math.max(1, sb.width);
  const co = [...document.querySelectorAll('#species .co, #species-under .co')].map((e) => { const r = e.getBoundingClientRect();
    return { layer: e.ownerSVGElement.id, cx: (r.left - sb.left + r.width / 2) * k, cy: (r.top - sb.top + r.height / 2) * k,
             rx: r.width * k / 2, ry: r.height * k / 2 }; });
  const p = document.querySelector('.chartbox path[data-si="1"]'); let datum = null;
  if (p) { const n = (p.getAttribute('d').match(/-?\d+(\.\d+)?/g) || []).map(Number);
    const q = new DOMPoint(n[2 * 152], n[2 * 152 + 1]).matrixTransform(p.getScreenCTM());
    datum = [(q.x - sb.left) * k, (q.y - sb.top) * k]; }
  return { co, datum };
}"""


class _Surface:
    def __init__(self, tl: dict, uris: dict):
        import render_baseline as RB
        self._td = tempfile.TemporaryDirectory()
        html = Path(self._td.name) / "p.html"
        html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
        self.tl = tl
        self.page, self.errs, self._close = SPL.open_served(html, 1920, 1080, cleanup=self._td.cleanup)

    def seek(self, t: float) -> None:
        for _ in range(2):
            self.page.evaluate("t => { const s = document.getElementById('scrub'); s.value = t; "
                               "s.dispatchEvent(new Event('input', {bubbles:true})); }", t)

    def close(self) -> None:
        self._close()


def _golden(target: dict | None = None) -> tuple[dict, dict]:
    tl, uris = G.chart_callout()
    tl = copy.deepcopy(tl)
    if target is not None:
        tl["scenes"][0]["species"][0]["target"] = target
    return tl, uris


def _page_datum_with_a_dock() -> tuple[dict, dict]:
    """The ledger-page golden with a card docked over it and a callout on the PAGE's datum 3: the page's layer."""
    page_tl, page_uris = G.ledger_page_mid_build()
    ctl, curis = G.chart_callout()
    tl = copy.deepcopy(page_tl)
    tl["evidence"] = dict(tl.get("evidence") or {}, **ctl["evidence"])
    sc = tl["scenes"][0]
    sc["docks"] = copy.deepcopy(ctl["scenes"][0]["docks"])
    sc["species"] = [{"kind": "callout", "at": 10.0, "dur": 6.0, "target": {"kind": "datum", "index": 3}}]
    return tl, dict(page_uris, **{AID: curis[AID]})


CARD_POINT = {"kind": "point", "x": 0.45, "y": 0.40}   # over the page's plot, clear of its lines, where the slot-0 card stands


def _page_point(card: bool) -> tuple[dict, dict]:
    """The ledger-page golden with a point callout over its plot - on a PICTURE card parked there, or on the bare page.
    A light or a ring on a card annotates the card (E56: a picture's focus is its light), never the page beneath."""
    tl, uris = G.ledger_page_mid_build()
    tl = copy.deepcopy(tl)
    sc = tl["scenes"][0]
    sc["species"] = [{"kind": "callout", "at": 10.0, "dur": 6.0, "target": CARD_POINT}]
    if not card:
        return tl, uris
    pair, puris = G._dock_pair(None)
    tl["evidence"] = dict(tl.get("evidence") or {}, **{"ev-golden-card-a": pair["evidence"]["ev-golden-card-a"]})
    sc["docks"] = [copy.deepcopy(pair["scenes"][0]["docks"][0])]
    return tl, dict(uris, **{"ev-golden-card-a": puris["ev-golden-card-a"]})


@pytest.fixture(scope="module")
def drawn():
    out = {}
    for name, (tl, uris) in {"bound": _golden(), "point": _golden(OLD_POINT),
                             "far": _golden({"kind": "point", "x": 0.1, "y": 0.1}),
                             "page": _page_datum_with_a_dock(),
                             "on_card": _page_point(True), "on_page": _page_point(False)}.items():
        s = _Surface(tl, uris)
        try:
            s.seek(T_JUDGED)
            out[name] = {"dom": s.page.evaluate(READ_CO), "errs": list(s.errs),
                         "reach": PR.mark_reach_read(s.page, T_JUDGED, s.tl)}
        finally:
            s.close()
    return out


def test_the_bound_golden_s_callout_sits_on_its_datum_above_the_card(drawn):
    d = drawn["bound"]["dom"]
    assert drawn["bound"]["errs"] == []
    assert len(d["co"]) == 1, d
    co, (dx, dy) = d["co"][0], d["datum"]
    assert co["layer"] == "species", co   # the card IS the chart: the mark annotates it, on the top layer
    norm = math.hypot((co["cx"] - dx) / co["rx"], (co["cy"] - dy) / co["ry"])
    assert norm <= 0.25, (co, d["datum"], norm)   # its centre on the datum (within its own radius, and far inside it)


def test_a_datum_on_the_page_s_chart_keeps_the_layer_beneath_the_card(drawn):
    d = drawn["page"]["dom"]
    assert [c["layer"] for c in d["co"]] == ["species-under"], d


def test_the_probe_reads_the_old_point_as_a_miss_naming_its_datum(drawn):
    (r,) = drawn["point"]["reach"]
    assert r["kind"] == "callout" and r["chart"] == f"dock {AID}", r
    assert 35.0 <= r["dist_px"] <= 45.0 and r["norm"] > 1.0, r
    assert r["series"] == 1 and abs(r["datum"] - 152) <= 3, r


def test_the_probe_does_not_read_a_bound_datum_or_a_mark_over_no_chart(drawn):
    assert drawn["bound"]["reach"] == []   # a datum target is on its datum by construction: only a POINT is judged
    assert drawn["far"]["reach"] == []     # (0.1, 0.1) is over no chart's plot


def test_a_mark_on_a_card_over_the_page_is_the_card_s_not_the_page_s(drawn):
    assert drawn["on_card"]["reach"] == [], drawn["on_card"]["reach"]   # it annotates the picture (E56)
    (r,) = drawn["on_page"]["reach"]                                    # ... and the same point on the bare page is read
    assert r["chart"] == "page" and r["kind"] == "callout" and r["series"] is not None and r["datum"] is not None, r
    assert r["norm"] > 1.0, r                                           # ... as the miss it is: off every line
