"""P69 T50 - FORMS JUDGED BY HONESTY, NOT TYPE (E99 s100, s109 (5); BACKLOG R26-263) + A BRACKET ON A BARS PAGE (R26-272).

E99 s100 (amends E53 s1): "Area is still valid, we just have to use it when appropriate, and storytelling is the more
important thing as long as we are being truthful." An area form is TRUTHFUL when (a) every area is drawn in true
proportion to its value and (b) the figures the claim turns on are WRITTEN on the page; "the donut's and the treemap's
four-point exceptions (E53 s1 amendments) are superseded by those two tests". s109 (5): E53's form rules are DEFAULTS
that give way to the story when the honesty tests hold - "a new form is judged on its truth and its read, not refused by
type". s106: a finding is a WARN with its numbers; only UNTRUTH stays a hard refusal (a value drawn wrong, shares that do
not sum).

So, here:
  * a share page past five slices is a page - it WARNs with its count, the figures it writes and its thinnest slice;
  * a treemap may carry a SIZE claim - it WARNs, naming the cells whose figures it cannot write, unless every one is;
  * a treemap of two parts is a page (one part is not a division);
  * a `shares` object asked for as bars or a line is ROUTED to the two forms that draw it, not refused as a type;
  * the census X (`cross`) with no written share, or on a cell the page cannot name, WARNs with the crossed share and the
    cell's size - it is no longer refused;
  * the truth rules stay hard: shares that do not sum to their whole, parts past their whole, a sign in the note, a
    membership tile that carries a value, a range across zero, a broken axis in two units.

R26-272: `buildPerform` built a bracket from `st.linePts`, which a bars page never has - a `bracket` from bar 0 to bar 1
compiled and painted NOTHING. It now anchors to the bars' TOPS (the one datum rule `lpMarkDatumOn` reads for a bar) and
stands beside the bars' own sides. A line page's bracket is untouched (the `tiers-two` and page goldens pin it).

The browser rows need playwright + chromium and are skipped without them.
"""
from __future__ import annotations

import copy
import json
import re
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests/golden"))

import build_scene_timeline_f as B  # noqa: E402
import ledger_page as L  # noqa: E402
import render_baseline as RB  # noqa: E402
import build_golden_sources as G  # noqa: E402

STILL = (0, 0, 0)
FORM_WARN = "WARN form:"

# ---- the fixtures ------------------------------------------------------------------------------------------------------

# seven parts of one whole, in percent (sum 100) - the thinnest is 2.5 %
SEVEN = [("NVIDIA", 38.0), ("AMD", 17.5), ("Intel", 14.0), ("Broadcom", 11.0), ("Marvell", 9.0), ("Qualcomm", 8.0),
         ("Others", 2.5)]
FIVE = SEVEN[:4] + [("Others", 19.5)]


def _pie(parts=SEVEN, **extra) -> dict:
    """The flat pie (P48 T4): one slice emphasised, its PEEL the one figure the page writes."""
    return {"title": "Who sells the chips", "src": "fixture", "unit": "%",
            "shares": [{"label": a, "value": b} for a, b in parts], "emphasize": 0,
            "peel": {"index": 0, "value": -4.0, "value_string": "-4 pts", "label": "lost in a year"}, **extra}


def _donut(parts=SEVEN, **extra) -> dict:
    """The solid share page (T48): a donut, every slice's figure written, the angles shares of a declared whole."""
    return {"title": "Who sells the chips", "src": "fixture", "unit": "%", "total": 100, "hole": 0.5,
            "shares": [{"label": a, "value": b} for a, b in parts], "emphasize": 0, **extra}


CENSUS = [("United States", 16.8), ("Hong Kong", 8.5), ("Japan", 4.7), ("Korea", 4.5), ("Vietnam", 4.1),
          ("India", 3.4), ("Germany", 3.1), ("Netherlands", 3.0), ("Malaysia", 2.5), ("Russia", 2.4),
          ("Brazil", 2.0), ("Australia", 1.9), ("Spain", 1.3), ("Saudi Arabia", 1.2), ("Rest of world", 40.6)]


def _census(parts=CENSUS, **extra) -> dict:
    return {"title": "China's exports, by partner", "sub": "share of goods exports, one year",
            "src": "our reading", "unit": "%", "total": 100,
            "shares": [{"label": a, "value": b} for a, b in parts], **extra}


def CENSUS_ORDER(spec: dict) -> list[dict]:   # noqa: N802 - the page's cells in the FILE's order
    return [{"label": x} for x in spec["labels"]]


def _form_warnings(spec: dict) -> list[str]:
    return [w for w in spec.get("warnings") or [] if str(w).startswith(FORM_WARN)]


# ---- the share page: the slice count is guidance, the sum is truth -----------------------------------------------------


def test_a_pie_of_seven_slices_is_a_page_and_warns_with_its_numbers():
    s = _pie()
    assert L.validate(s, "share") == [], "E99 s100: the four-point exception's slice cap is superseded by the two tests"
    w = _form_warnings(L.build_spec(s, "share"))
    assert len(w) == 1, w
    assert "7 slices" in w[0] and f"{L.SHARE_MAX_SLICES}" in w[0], w[0]
    assert "1 of 7 figures" in w[0], "the flat pie writes the peel's figure alone - the WARN counts it"
    assert "'Others'" in w[0] and "2.5%" in w[0] and "9.0 deg" in w[0], "the thinnest slice, its share and its angle"
    assert "E99 s106" in w[0]


def test_a_donut_of_seven_slices_writes_every_figure_and_names_its_thinnest_slice():
    s = _donut()
    assert L.validate(s, "share") == []
    w = _form_warnings(L.build_spec(s, "share"))
    assert len(w) == 1 and "7 of 7 figures" in w[0] and "'Others'" in w[0], w


def test_five_slices_carry_no_warning_and_their_spec_has_no_warnings_key():
    for s in (_pie(FIVE), _donut(FIVE)):
        assert L.validate(s, "share") == []
        assert "warnings" not in L.build_spec(s, "share"), "a page inside the guidance is byte-identical: no key at all"


@pytest.mark.parametrize("parts, needle", [
    (SEVEN[:-1], "unaccounted for"),                              # sums to 97.5 of 100
    (SEVEN[:-1] + [("Others", 12.5)], "cannot exceed its whole"),  # sums to 110
])
def test_shares_that_do_not_sum_to_their_whole_are_still_refused(parts, needle):
    errs = L.validate(_donut(parts), "share")
    assert any(needle in e for e in errs), errs


def test_a_negative_slice_is_still_refused():
    errs = L.validate(_pie([("A", 60.0), ("B", -10.0), ("C", 50.0)]), "share")
    assert any("cannot be negative" in e for e in errs), errs


def test_a_shares_object_asked_for_as_bars_is_routed_to_the_forms_that_draw_it():
    for variant in ("bars", "line"):
        errs = L.validate({"title": "t", "src": "s", "shares": [{"label": "a", "value": 1}, {"label": "b", "value": 2}]},
                          variant)
        assert len(errs) == 1, errs
        e = errs[0]
        assert "--variant share" in e and "--variant treemap" in e, "it names the two forms that DRAW a part-to-whole"
        assert "E99 s100" in e, "and the ruling that made the hierarchy guidance"
        assert "refused for every variant" not in e and "bottom of the perception hierarchy" not in e, \
            "a part-to-whole is not refused as a TYPE any more"


# ---- the treemap: a size claim is honest when its figures are written --------------------------------------------------


def test_a_size_claim_on_a_treemap_is_a_page():
    for text, field in (("America is bigger than the next four", "sub"), ("Who is largest?", "title"),
                        ("three times Japan's", "claim")):
        assert L.validate(_census(**{field: text}), "treemap") == [], (field, text)


def test_a_size_claim_whose_figures_are_not_all_written_warns_with_its_numbers():
    spec = L.build_spec(_census(sub="America is bigger than the next four"), "treemap")
    w = _form_warnings(spec)
    assert len(w) == 1, w
    lay = spec["layout"]
    for aspect in ("16:9", "9:16"):
        written = sum(1 for c in lay[aspect]["cells"] if c["tier"] == 2)
        assert f"{written} of 15 cells at {aspect}" in w[0], (aspect, written, w[0])
    assert "says 'bigger'" in w[0] and "page's sub" in w[0], "it quotes the claim's word and names its field"
    unwritten = [c["label"] for c in CENSUS_ORDER(spec) if any(x["label"] == c["label"] and x["tier"] < 2
                                                             for a in ("16:9", "9:16") for x in lay[a]["cells"])]
    assert unwritten and f"unwritten: {unwritten[0]}" in w[0], "it names, in the file's order, the cells it cannot write"
    assert f"and {len(unwritten) - 6} more" in w[0] if len(unwritten) > 6 else unwritten[-1] in w[0]
    assert "--variant bars" in w[0] and "E99 s100" in w[0] and "E99 s106" in w[0]


def test_a_size_claim_whose_every_figure_is_written_carries_no_warning():
    spec = L.build_spec(_census([("United States", 50.0), ("Hong Kong", 30.0), ("Japan", 20.0)],
                                sub="America is bigger than Hong Kong and Japan together"), "treemap")
    assert all(c["tier"] == 2 for a in ("16:9", "9:16") for c in spec["layout"][a]["cells"]), "every figure written"
    assert "warnings" not in spec, "honest by both tests: nothing to report"


def test_a_census_with_no_size_claim_is_byte_identical():
    spec = L.build_spec(_census(), "treemap")
    assert "warnings" not in spec


def test_every_treemap_cell_is_drawn_true_to_its_value():
    """s100 (a), measured: a cell's area is its value's share of the drawn whole, to a millionth of the plot."""
    spec = L.build_spec(_census(), "treemap")
    total = sum(v for _, v in CENSUS)
    for aspect in ("16:9", "9:16"):
        for c in spec["layout"][aspect]["cells"]:
            assert abs(c["fw"] * c["fh"] - c["value"] / total) < 5e-6, (aspect, c)


def test_a_two_part_treemap_is_a_page_and_one_part_is_not():
    assert L.validate(_census([("Inside", 60.0), ("Outside", 40.0)]), "treemap") == []
    errs = L.validate(_census([("All", 100.0)]), "treemap")
    assert errs and "at least 2 parts" in errs[0], errs


def test_treemap_parts_past_their_whole_are_still_refused():
    errs = L.validate(_census([("A", 70.0), ("B", 50.0)]), "treemap")
    assert any("cannot exceed its whole" in e for e in errs), errs


# ---- the census X: the written share and the named cell are honesty tests, WARNed ------------------------------------

CENSUS_PARTS = [("United States", 16.8), ("Hong Kong", 8.5), ("Japan", 4.7), ("Korea", 4.5),
                ("Vietnam", 4.1), ("India", 3.4), ("Saudi Arabia", 1.2), ("Rest of world", 58.8)]


def _census_world() -> dict:
    series = {"title": "China's exports, by partner", "src": "our reading", "unit": "%", "total": 100,
              "shares": [{"label": a, "value": b} for a, b in CENSUS_PARTS]}
    return {"kind": "ledger", "page": L.build_spec(series, "treemap", None, "right"),
            "ken_burns": {"scale": 0, "x": 0, "y": 0}}


def _cross(**extra) -> dict:
    return {"kind": "cross", "at": 9.0, "dur": 3.0, "cells": ["United States", "Japan"], **extra}


def test_a_cross_without_its_written_share_compiles_and_warns_with_the_crossed_share(tmp_path, capsys):
    sp = _cross()
    assert B.validate_species([sp], STILL, "ledger:exports:treemap") == []
    B.derive_rescale_states(_census_world(), [sp], "ledger:exports:treemap", tmp_path)
    out = capsys.readouterr().out
    warn = [ln for ln in out.splitlines() if "[WARN]" in ln and "cross" in ln]
    assert len(warn) == 1, out
    assert "21.5" in warn[0] and "of the whole" in warn[0], "the crossed share, computed from the page: 16.8 + 4.7"
    assert "E99 s100" in warn[0] and "E99 s106" in warn[0]


def test_a_cross_whose_text_carries_no_number_warns_with_the_crossed_share(tmp_path, capsys):
    sp = _cross(text="the partners that left")
    assert B.validate_species([sp], STILL, "ledger:exports:treemap") == []
    B.derive_rescale_states(_census_world(), [sp], "ledger:exports:treemap", tmp_path)
    out = capsys.readouterr().out
    assert "carries no number" in out and "21.5" in out, out


def test_a_cross_that_writes_its_share_warns_nothing(tmp_path, capsys):
    sp = _cross(text="2 partners, 21.5 % of exports")
    B.derive_rescale_states(_census_world(), [sp], "ledger:exports:treemap", tmp_path)
    assert "[WARN]" not in capsys.readouterr().out


def test_a_cross_on_a_cell_the_page_cannot_name_warns_with_its_size(tmp_path, capsys):
    world = _census_world()
    sp = _cross(cells=["Saudi Arabia"], text="1 partner, 1.2 %")
    B.derive_rescale_states(world, [sp], "ledger:exports:treemap", tmp_path)   # no exception (E99 s106)
    out = capsys.readouterr().out
    warn = [ln for ln in out.splitlines() if "[WARN]" in ln and "Saudi Arabia" in ln]
    assert warn, out
    bare = [a for a, lay in world["page"]["layout"].items()
            for c in lay["cells"] if c["label"] == "Saudi Arabia" and c["tier"] < 1]
    assert bare and len(warn) == len(bare) and all(any(f"at {a} " in w for w in warn) for a in bare), (bare, warn)
    assert all(re.search(r"\d+ x \d+ px cell", w) for w in warn), "the cell's own size, against the floors"


def test_a_text_that_is_not_a_string_is_still_a_grammar_error():
    errs = B.validate_species([_cross(text=41)], STILL, "ledger:exports:treemap")
    assert errs and "text" in errs[0], errs


def test_a_cross_off_a_treemap_page_is_still_refused(tmp_path):
    """Capability, not type: only a treemap has CELLS to cross."""
    with pytest.raises(ValueError, match="land on a TREEMAP page"):
        B.derive_rescale_states({"kind": "ledger", "page": {"builder": "story", "labels": []}}, [_cross()],
                                "ledger:x:bars", tmp_path)


# ---- the truth rules stay hard -----------------------------------------------------------------------------------------


def test_the_truth_rules_stay_hard():
    base = {"title": "t", "src": "s", "unit": "%"}
    sign = dict(base, bars=[{"label": "a", "value": 5, "note": "-5%"}, {"label": "b", "value": 3}])
    assert any("E28" in e for e in L.validate(sign, "bars")), "a drop drawn as a rise is a value drawn wrong"
    across = dict(base, bars=[{"label": "a", "value": [-2, 3]}, {"label": "b", "value": 1}])
    assert any("straddles zero" in e for e in L.validate(across, "bars"))
    valued = dict(base, bars=[{"label": "a", "value": 10, "members": [{"name": "X", "value": 4}, {"name": "Y"}]}])
    assert any("carries a value" in e for e in L.validate(valued, "bars")), "an equal tile drawn for an unequal value"


def test_a_ledger_world_carries_the_form_warning_to_the_build(tmp_path):
    (tmp_path / "evidence/objects").mkdir(parents=True)
    (tmp_path / "evidence/objects/fx-seven.series.json").write_text(json.dumps(_donut()), encoding="utf-8")
    world = B.world_for_plate("ledger:fx-seven:share", STILL, tmp_path)
    assert _form_warnings(world["page"]), "the compiler's world carries it; main prints it as a [WARN] line"


def test_the_compiler_prints_a_form_warning_beside_the_membership_ones():
    src = (ROOT / "content/video_engine/scripts/build_scene_timeline_f.py").read_text(encoding="utf-8")
    lines = [ln for ln in re.split(r"\r?\n", src) if "startswith(LPG.FORM_WARN)" in ln]
    assert lines and L.FORM_WARN == FORM_WARN, "main's world loop prints the page's `WARN form:` lines"


# ---- R26-272: a bracket on a bars page anchors to the bar tops ---------------------------------------------------------

ASPECT = "16:9"
BK_AT, BK_S = 8.0, 1.6          # the page has built (its bars grow 4.4-7.4 s on a page entered at 0)
# the H row-21 wafer ratio (ev-hbm-wafer-ratio-bars-v1), its values copied so this file never reads an untracked series
WAFER = {"title": "Wafer capacity per gigabyte",
         "sub": "HBM against standard DRAM - stacking the dies takes about three times the silicon for the same gigabyte",
         "src": "Micron / SK hynix technical disclosures, via industry reporting - approximate ratio",
         "unit": "x",
         "bars": [{"label": "Standard DRAM", "value": 1, "note": "1x", "color": "deemph"},
                  {"label": "HBM (stacked dies)", "value": 3, "note": "about 3x", "color": "crimson"}]}
BRACKET = {"kind": "bracket", "at": BK_AT, "dur": BK_S, "from": 0, "to": 1, "label": "3x", "sub": "the silicon per gigabyte"}

PROBE = """() => {
  const w = [wB, wA].find(e => e.__lp && e.classList.contains('ledger')); if (!w) return null;
  const st = w.__lp, PF = st.perform || { brackets: [] };
  const bars = (st.marks || []).filter(m => m.role === 'bar').map(m => m.geom);
  const brackets = (PF.brackets || []).map(b => {
    const bb = b.main.line.getBBox(), lb = b.main.label.getBBox(), sb = b.main.sub ? b.main.sub.getBBox() : null;
    return { x: b.x, y0: b.y0, y1: b.y1, A: b.A, B: b.B, fits: b.fits, opacity: +(b.main.g.getAttribute('opacity') || 0),
             offset: +(b.main.line.getAttribute('stroke-dashoffset') || 0), len: b.main.len,
             glyphs: b.main.lg.map(ts => +(ts.getAttribute('opacity') || 0)), line: [bb.x, bb.y, bb.width, bb.height],
             label: [lb.x, lb.y, lb.width, lb.height], sub: sb ? [sb.x, sb.y, sb.width, sb.height] : null };
  });
  const vals = (st.bars || []).map(b => { if (!b.val) return null; const v = b.val.getBBox(); return [v.x, v.y, v.width, v.height]; });
  return { kind: st.kind, linePts: (st.linePts || []).length, bars, brackets, vals, W: (st.geom || {}).W };
}"""


def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")


def bars_timeline(tmp: Path, obj: dict, species: list[dict], aspect: str = ASPECT) -> tuple[dict, dict]:
    """A bars page as the compiler builds it (stamped full-stage on 16:9), one scene, its species."""
    (tmp / "evidence/objects").mkdir(parents=True, exist_ok=True)
    (tmp / "evidence/objects/fx-bars.series.json").write_text(json.dumps(obj), encoding="utf-8")
    plate = "ledger:fx-bars:bars"
    saved = B.ASPECT
    B.ASPECT = aspect
    try:
        world = B.world_for_plate(plate, STILL, tmp)
        B.stamp_full_stage(world["page"])
    finally:
        B.ASPECT = saved
    assert B.validate_species(species, STILL, plate) == [], "the compiler accepts the bracket on a bars page"
    scenes = [{"scene_id": "s01", "world": dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}),
               "exit": "cut", "span": [0.0, G.RUNTIME], "docks": [], "species": copy.deepcopy(species)}]
    return G._timeline("P69 T50: a bracket on bars", scenes, {}, aspect), G._base_uris()


class Served:
    def __init__(self, timeline: dict, uris: dict, aspect: str = ASPECT):
        from playwright.sync_api import sync_playwright
        self._td = tempfile.TemporaryDirectory()
        html = Path(self._td.name) / "bars.html"
        html.write_text(RB.instantiate(timeline, uris), encoding="utf-8")
        self.w, self.h = RB.STAGE[aspect]
        self._srv, port = RB.serve(html.parent)
        self._pw = sync_playwright().start()
        self._br = self._pw.chromium.launch(headless=True)
        self.page = self._br.new_context(viewport={"width": self.w, "height": self.h}).new_page()
        self.errs: list[str] = []
        self.page.on("pageerror", lambda e: self.errs.append(str(e)))
        try:
            self.page.goto("http://127.0.0.1:%d/%s" % (port, html.name), wait_until="networkidle", timeout=120000)
            RB.prepare_page(self.page, self.w, self.h)
        except Exception:
            self.close()   # a player that never mounts must not leave its loop running under the next test
            raise

    def at(self, t: float) -> dict:
        self.page.evaluate("t => { const s = document.getElementById('scrub'); s.value = t; s.dispatchEvent(new Event('input', {bubbles:true})); }", t)
        return self.page.evaluate(PROBE)

    def png(self, t: float) -> bytes:
        return RB.frame_png(self.page, t, (self.w, self.h))

    def close(self) -> None:
        self._br.close(); self._pw.stop(); self._srv.shutdown(); self._td.cleanup()


def _meets(a: list[float], b: list[float]) -> bool:
    return a[0] < b[0] + b[2] and b[0] < a[0] + a[2] and a[1] < b[1] + b[3] and b[1] < a[1] + a[3]


@needs_browser
@pytest.mark.parametrize("aspect", ["16:9", "9:16"])
def test_a_bracket_on_a_bars_page_anchors_to_the_bar_tops(aspect):
    with tempfile.TemporaryDirectory() as td:
        timeline, uris = bars_timeline(Path(td), WAFER, [BRACKET], aspect)
    P = Served(timeline, uris, aspect)
    try:
        before = P.at(BK_AT - 0.5)
        assert before["kind"] == "story" and before["linePts"] == 0, "a bars page has no line points - the cause"
        assert len(before["brackets"]) == 1, "R26-272: the bracket on a bars page painted nothing"
        assert before["brackets"][0]["opacity"] == 0, "and it is not on the page before its word"
        s = P.at(BK_AT + BK_S + 0.4)
        bk, (b0, b1) = s["brackets"][0], s["bars"][:2]
        assert bk["A"] == [b0["cx"], b0["end"]] and bk["B"] == [b1["cx"], b1["end"]], "anchored to the two bar TOPS"
        assert abs(bk["y0"] - min(b0["end"], b1["end"])) < 1e-6 and abs(bk["y1"] - max(b0["end"], b1["end"])) < 1e-6, \
            "the span runs from one top to the other - the measured gap"
        right = max(b0["x"] + b0["w"], b1["x"] + b1["w"])
        assert bk["x"] > right, f"it stands beside the bars' own sides, off their ink: x {bk['x']} vs edge {right}"
        assert bk["opacity"] == 1 and bk["offset"] < 0.5 and all(g == 1 for g in bk["glyphs"]), "drawn whole, label written"
        for b in (b0, b1):
            rect = [b["x"], b["y"], b["w"], b["h"]]
            assert not _meets(bk["line"], rect), ("the span never draws on a bar", bk["line"], rect)
            for part in ("label", "sub"):
                assert not _meets(bk[part], rect), (f"nor its {part}", bk[part], rect)
        for v in filter(None, s["vals"]):   # the frame read (9:16): a stacked label wrote onto the bar's own "3x"
            for part in ("label", "sub"):
                assert not _meets(bk[part], v), (f"the {part} never writes on a bar's value", bk[part], v)
        assert not P.errs, P.errs
    finally:
        P.close()


@needs_browser
def test_a_bracket_on_a_line_page_is_built_where_it_always_was():
    """The fallback runs only where the line points are absent: a line page's bracket is its own (the goldens pin the
    pixels; this pins the anchors - the two data on the line)."""
    line = {"title": "t", "sub": "s", "src": "fixture", "unit": "%",
            "series": [{"name": "yield", "color": "crimson", "pts": [[2000 + i, 2 + (i % 5)] for i in range(16)]}]}
    sp = dict(BRACKET, **{"from": 3, "to": 9})
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        (tmp / "evidence/objects").mkdir(parents=True)
        (tmp / "evidence/objects/fx-line.series.json").write_text(json.dumps(line), encoding="utf-8")
        world = B.world_for_plate("ledger:fx-line:line", STILL, tmp)
    scenes = [{"scene_id": "s01", "world": dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}),
               "exit": "cut", "span": [0.0, G.RUNTIME], "docks": [], "species": [sp]}]
    P = Served(G._timeline("P69 T50: a bracket on a line", scenes, {}, ASPECT), G._base_uris())
    try:
        s = P.at(BK_AT + BK_S + 0.4)
        assert s["linePts"] == 1 and len(s["brackets"]) == 1
        bk = s["brackets"][0]
        assert bk["A"] != bk["B"] and bk["x"] > max(bk["A"][0], bk["B"][0]), "beside its two data on the line"
        assert not P.errs, P.errs
    finally:
        P.close()
