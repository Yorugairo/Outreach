"""P70 T3 (was P69 T51): THE FILL GAUGE - one share of one whole fills a capsule on its word.

Harvest v2 T34 "Fill gauge / meter (a capsule filling to a share)", USE-WHEN `:483`: use it for "one share of one whole
('two-thirds', '94 %')"; don't for "comparing shares (use bars)". Bravos D40 17:24-17:40 (a capsule on a baseline rule,
the share filled in its ink). A CHART FORM - "how a page's chart is DRAWN, never what it says" - so `gauge` joins
`ledger_page.CHART_FORMS` beside `extruded_bar`, and the engine branches on `formOf(pg, "gauge")` in buildLedgerBars.

What is held here:
  1. `;form=gauge` is legal on a PROGRESS page only, refused elsewhere by name through `form_error` (one rule: the row
     and an object naming the form). `gauge:h` (the horizontal capsule) was refused by name here until P72 T6 gave M26 a
     width reader (R26-319); it is held by test_value_gate_longform now, and any OTHER setting is still refused here.
  2. One capsule, vertical: its fill rises from empty to value / ceiling on the page's own bar-grow clock, and the
     figure is written at the fill line as the fill lands - verbatim, at the s90 phone floor, in its bar's ink.
  3. The capsule's full length IS the whole, and the whole is NAMED on the page (the label of an hline at the ceiling).
     A gauge whose whole is unnamed is refused (E28).
  4. M26, THROUGH THE PROBE: the printed value and the drawn fill agree at every instant; a value past the ceiling is
     refused by the existing progress bound; and a page that printed a number its fill does not carry is FAILED by the
     same probe, so the row is proved to read the capsule and not to pass it by default.
  5. A second bar is a WARN with its numbers (s106), never a refusal; one capsule per bar.
"""
from __future__ import annotations

import contextlib
import copy
import io
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests/golden"))

import build_scene_timeline_f as B  # noqa: E402
import gate_motion_density as G  # noqa: E402
import ledger_page as LPG  # noqa: E402
import render_baseline as RB  # noqa: E402

ENGINE = ROOT / "docs/content-video-engine/samples/scene-evidence-engine.mjs"
CARDS = ROOT / "content/video_engine/effects/cards"
H_EP = ROOT / "content/video_engine/projects/systems-and-blowups/steel-and-paper"
H_OBJ = "ev-capex-ocf-94-bars-v1"                       # PIMCO Fig. 3: 94 % of operating cash flow, hline 100 named
GAUGE = f"ledger:{H_OBJ}:progress::right;form=gauge"
KEN = (0, 0, 0)
PHONE_FLOOR = 12 * 1920 / 390                           # E99 s90: 59.08 stage px
READS = "a PROGRESS page - one share of one whole, drawn as a capsule"
ORANGE = "rgb(255, 138, 76)"                            # LP_INK.crimson (#FF8A4C), the 94 bar's declared token
REST_T = 9.0                                            # the hold; mid-build is found on the page's own clock

WHOLE_OBJ = {"title": "Share of the whole", "sub": "fixture", "src": "golden fixture", "unit": "%", "domain": [0, 100],
             "hlines": [{"y": 100, "label": "the whole", "color": "deemph"}],
             "bars": [{"label": "Part", "value": 60, "color": "teal"}]}


def _obj(**over) -> dict:
    return dict(copy.deepcopy(WHOLE_OBJ), **over)


FIXTURES = {
    "g-named": _obj(),
    "g-unnamed": _obj(hlines=[]),
    "g-rule-no-label": _obj(hlines=[{"y": 100, "color": "deemph"}]),
    "g-rule-elsewhere": _obj(hlines=[{"y": 50, "label": "half", "color": "deemph"}]),
    "g-two": _obj(bars=[{"label": "Part", "value": 60, "color": "teal"}, {"label": "Other", "value": 25, "color": "crimson"}]),
    "g-over": _obj(bars=[{"label": "Part", "value": 120, "color": "teal"}]),
    "g-denominator": _obj(denominator=40, domain=None, hlines=[{"y": 40, "label": "all forty seats", "color": "deemph"}],
                          bars=[{"label": "Held", "value": 26, "color": "teal"}]),
    "g-domain": _obj(domain=[0, 120]),
    "g-segments": _obj(bars=[{"label": "Part", "value": 60, "color": "teal",
                              "segments": [{"name": "a", "value": 40}, {"name": "b", "value": 20}]}]),
}


@pytest.fixture(scope="module")
def ep(tmp_path_factory) -> Path:
    d = tmp_path_factory.mktemp("t3-ep")
    (d / "evidence/objects").mkdir(parents=True)
    for name, obj in FIXTURES.items():
        obj = {k: v for k, v in obj.items() if v is not None}
        (d / f"evidence/objects/{name}.series.json").write_text(json.dumps(obj), encoding="utf-8")
    return d


def world(ep_dir: Path, plate: str) -> dict:
    return B.world_for_plate(plate, KEN, ep_dir)


def refusal(ep_dir: Path, plate: str) -> str:
    with pytest.raises(ValueError) as exc:
        world(ep_dir, plate)
    return str(exc.value)


# ---- 1. the grammar and the one refusal ------------------------------------------------------------------------------
def test_the_expected_red_is_gone_gauge_is_a_chart_form() -> None:
    assert "gauge" in LPG.CHART_FORMS
    assert B.page_form_geom("gauge", "r") == {"kind": "gauge"}
    assert LPG.FORM_READS["gauge"] == READS
    assert LPG.FORM_BUILDERS["gauge"] == ("story",) and LPG.FORM_VARIANTS["gauge"] == ("progress",)


def test_the_unknown_form_message_names_all_three_forms() -> None:
    with pytest.raises(ValueError) as exc:
        B.page_form_geom("bogus", "r")
    assert "extruded_bar|tilted_line|gauge" in str(exc.value)
    assert "extruded_bar|tilted_line|gauge" in LPG.form_error("bogus", "story", "r")


def test_form_error_reads_the_variant_for_the_gauge_only() -> None:
    assert LPG.form_error("gauge", "story", "r", "progress") is None
    for variant in ("bars", None):
        msg = LPG.form_error("gauge", "story", "r", variant)
        assert READS in msg and repr(variant) in msg
    msg = LPG.form_error("gauge", "dense-line", "r", "line")
    assert READS in msg
    # the two 2.5D forms ignore the new argument - their rule is the builder's, as it was
    assert LPG.form_error("extruded_bar", "story", "r", "progress") is None
    assert LPG.form_error("extruded_bar", "story", "r") is None
    assert "form=tilted_line is a LINE page" in LPG.form_error("tilted_line", "story", "r", "progress")


def test_the_row_compiles_the_gauge_on_the_H_progress_page() -> None:
    page = world(H_EP, GAUGE)["page"]
    assert page["form"] == {"kind": "gauge", "ceiling": 100}
    assert page["variant"] == "progress" and page["builder"] == "story"
    assert page["values"] == [94.0] and page["value_strings"] == ["94"]


def test_a_gauge_on_any_other_page_is_refused_by_name_and_it_is_the_only_refusal(ep: Path) -> None:
    msg = refusal(H_EP, f"ledger:{H_OBJ}:bars::right;form=gauge")
    assert READS in msg and "'bars'" in msg
    # the same data as progress with a second bar compiles: the refusal is the BUILDER's, never the bar count's
    assert world(ep, "ledger:g-two:progress;form=gauge")["page"]["form"]["kind"] == "gauge"


def test_the_gauge_takes_no_setting_but_h() -> None:
    """P72 T6 (R26-319): `gauge:h` compiles - M26 reads its fill as a width (test_value_gate_longform holds it); any other
    setting is refused by name, and the bare form is the vertical capsule to the byte."""
    assert B.page_form_geom("gauge:h", "r") == {"kind": "gauge", "dir": "h"}
    assert B.page_form_geom("gauge", "r") == {"kind": "gauge"}
    with pytest.raises(ValueError) as exc:
        B.page_form_geom("gauge:x", "r")
    assert "takes no setting but :h" in str(exc.value)


def test_the_object_naming_the_form_is_held_to_the_same_rule() -> None:
    assert LPG.validate(dict(WHOLE_OBJ, form="gauge"), "progress") == []
    errs = LPG.validate(dict(WHOLE_OBJ, form="gauge"), "bars")
    assert any(READS in e for e in errs)
    errs = LPG.validate(dict(WHOLE_OBJ, form="gauge", hlines=[]), "progress")
    assert any("never names it" in e for e in errs)


# ---- 3. the whole is named, and the capsule IS the whole ------------------------------------------------------------
def test_a_gauge_whose_whole_is_unnamed_is_refused(ep: Path) -> None:
    for name in ("g-unnamed", "g-rule-no-label", "g-rule-elsewhere"):
        msg = refusal(ep, f"ledger:{name}:progress;form=gauge")
        assert "never names it" in msg and "E28" in msg and "100" in msg, name
    assert world(ep, "ledger:g-named:progress;form=gauge")["page"]["form"] == {"kind": "gauge", "ceiling": 100}


def test_the_ceiling_is_the_denominator_when_one_is_given(ep: Path) -> None:
    page = world(ep, "ledger:g-denominator:progress;form=gauge")["page"]
    assert page["form"] == {"kind": "gauge", "ceiling": 40}
    assert LPG.gauge_whole(page) == "all forty seats"


def test_a_stated_scale_other_than_the_whole_is_refused(ep: Path) -> None:
    msg = refusal(ep, "ledger:g-domain:progress;form=gauge")
    assert "[0, 100]" in msg and "0..100" in msg and "capsule" in msg


def test_a_stack_on_a_gauge_is_refused_by_the_existing_rule(ep: Path) -> None:
    # a progress page never carries a stack (P69 T64's rule, before any form is read): the gauge adds no second rule
    msg = refusal(ep, "ledger:g-segments:progress;form=gauge")
    assert "carry segments: a stacked bar is a bars page's" in msg and "draws 'progress' as 'story'" in msg


# ---- 4 (compile half). the existing bound holds ----------------------------------------------------------------------
def test_a_value_past_the_ceiling_is_refused_by_the_existing_progress_bound(ep: Path) -> None:
    msg = refusal(ep, "ledger:g-over:progress;form=gauge")
    assert "progress value 120" in msg and "outside 0..100" in msg


# ---- 5. a second bar WARNs with its numbers ------------------------------------------------------------------------
def test_a_second_bar_is_a_warn_with_its_numbers_never_a_refusal(ep: Path) -> None:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        page = world(ep, "ledger:g-two:progress;form=gauge")["page"]
    out = buf.getvalue()
    assert "[WARN] P70 T3:" in out and "2 bars" in out and "'Part' 60%" in out and "'Other' 25%" in out
    assert "use bars" in out and "E99 s106" in out
    assert "warnings" not in page                        # printed, never stored: the page's bytes stay
    assert LPG.gauge_warnings(page)[0].startswith(LPG.FORM_WARN)
    assert LPG.gauge_warnings(world(H_EP, GAUGE)["page"]) == []


def test_a_page_without_the_form_carries_no_key_and_prints_nothing() -> None:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        page = world(H_EP, f"ledger:{H_OBJ}:progress::right")["page"]
    assert "form" not in page and "P70 T3" not in buf.getvalue()


# ---- the cards ------------------------------------------------------------------------------------------------------
def _card(axis: str, cid: str) -> dict:
    cards = json.loads((CARDS / f"{axis}.json").read_text(encoding="utf-8"))
    cards = cards["cards"] if isinstance(cards, dict) else cards
    return next(c for c in cards if c["id"] == cid)


def test_the_cards_name_the_gauge() -> None:
    form = _card("plate_option", "plate_option:form")
    assert "gauge" in {o["token"] for o in form["options"]} and len(form["does"]) <= 240
    prog = _card("page_builder", "page_builder:progress")
    assert prog["status"] == "wired" and "gauge" in prog["does"]


# ---- the review round (finding 7): the figure's ink against its ground; (finding 4): the gauge's own page-boxes key ----
def test_a_figure_under_the_text_floor_warns_with_its_numbers() -> None:
    page = world(H_EP, GAUGE)["page"]
    assert LPG.gauge_figure_ink(page, 0) == ("#FF8A4C", "crimson", "#25313C")   # E67's orange on the charcoal: 5.68:1, no WARN
    assert LPG.gauge_warnings(page) == []
    cream = dict(page, surface_from="plate-x")                                   # the same orange on a plate's cream surface
    (w,) = LPG.gauge_warnings(cream)
    assert w.startswith(LPG.FORM_WARN) and "1.89:1" in w and "#F4E6C7" in w and "4.5:1" in w and "E99 s106" in w


def test_a_gauge_page_has_its_own_page_boxes_key_and_no_other_page_moves() -> None:
    gauge = world(H_EP, GAUGE)["page"]
    flat = world(H_EP, f"ledger:{H_OBJ}:progress::right")["page"]
    bars = world(H_EP, f"ledger:{H_OBJ}:bars::right")["page"]
    assert LPG.page_ink_key(gauge) != LPG.page_ink_key(flat)      # the capsule's plot is not the bars' plot
    # the flat page's key is the key it had before this slice: the same ink as the bars page of the same object
    # (builder story, the same title, sub, source and zone), so every fixture entry measured before still answers
    assert LPG.page_ink_key(flat) == LPG.page_ink_key(bars)
    import measure_page_boxes as M
    rep = M.representative(M.STORY_GAUGE)
    assert rep["form"] == {"kind": "gauge", "ceiling": 100} and LPG.page_ink_key(rep) == LPG.page_ink_key(gauge)


# ---- the served player ------------------------------------------------------------------------------------------------
def _browser_ok() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _browser_ok(), reason="playwright chromium not installed")


def _timeline(plate: str, ep_dir: Path, mutate=None) -> tuple[dict, dict]:
    import build_golden_sources as GS
    saved = B.ASPECT
    B.ASPECT = "16:9"
    try:
        w = world(ep_dir, plate)
    finally:
        B.ASPECT = saved
    if mutate:
        mutate(w["page"])
    scenes = [{"scene_id": "s01", "world": dict(w, ken_burns={"scale": 0, "x": 0, "y": 0}), "exit": "cut",
               "span": [0.0, GS.RUNTIME], "docks": [], "species": []}]
    tl = GS._timeline("P70 T3 gauge", scenes, {}, "16:9")
    return tl, dict(GS._base_uris(), **B.longform_assets(tl))


READ = r"""() => {
  const w = document.getElementById('wB'); const S = w && w.__lp; if (!S || !S.gauge) return null;
  const box = (el) => { const b = el.getBBox(); return [b.x, b.y, b.width, b.height]; };
  const op = (el) => { let o = 1; for (let e = el; e && e.getAttribute; e = e.parentElement) {
    const a = e.getAttribute('opacity'); if (a != null) o *= +a; const s = getComputedStyle(e).opacity; if (s !== '') o *= +s; } return o; };
  return { stagePx: S.stagePx, top: S.gauge.top, base: S.gauge.base, ceiling: S.gauge.ceiling,
    caps: S.gauge.caps.map((c) => ({ box: box(c.track), d: c.track.getAttribute('d') })),
    bars: S.bars.map((b) => { const m = /scaleY\(([-0-9.e]+)\)/.exec(b.bar.style.transform || ''), k = m ? +m[1] : 1;
      return { h: +b.bar.getAttribute('height') * k, v: b.v, parentClip: b.bar.parentElement.getAttribute('clip-path'),
               val: b.val.textContent, vop: op(b.val), vfill: getComputedStyle(b.val).fill,
               vsize: parseFloat(getComputedStyle(b.val).fontSize), vbox: box(b.val), foot: !!b.foot }; }),
    callout: !!S.callout,
    capsScreen: S.gauge.caps.map((c) => { const r = c.track.getBoundingClientRect(), g = document.getElementById('stage').getBoundingClientRect();
      return [r.x - g.x, r.y - g.y, r.width, r.height]; }),   /* stage px: the frame is clipped to the stage */
    ceilRules: [...S.chart.querySelectorAll('line.grid, line.hrule')].filter((l) => Math.abs(+l.getAttribute('y1') - S.gauge.top) < 0.6)
      .map((l) => ({ x1: +l.getAttribute('x1'), x2: +l.getAttribute('x2'), w: l.getBoundingClientRect().width,
                     shown: getComputedStyle(l).display !== 'none' })),
    whole: [...S.chart.querySelectorAll('text.sname')].map((t) => ({ text: t.textContent, box: box(t), op: op(t),
                                                                       anchor: t.getAttribute('text-anchor') })),
    hatch: !!S.chart.querySelector('g.lp-bar-hatch'), feet: S.chart.querySelectorAll('rect.lp-bar-foot').length };
}"""


def _on_a_thread(fn):
    """Run a SECOND player on a thread of its own: Playwright's sync API allows one running loop per thread and the
    module-scoped `h_gauge` owns this one (test_probe.py's own rule)."""
    import threading
    out: dict = {}

    def run() -> None:
        try:
            out["v"] = fn()
        except BaseException as e:        # noqa: BLE001 - re-raised on the calling thread below
            out["err"] = e

    th = threading.Thread(target=run)
    th.start()
    th.join()
    if "err" in out:
        raise out["err"]
    return out["v"]


def _once(tmp: Path, plate: str, ep_dir: Path, fn, mutate=None):
    """Build one timeline, serve it, run ``fn(player)`` and close - on a thread of its own."""
    def run():
        tl, uris = _timeline(plate, ep_dir, mutate)
        pl = Player(tmp, tl, uris)
        try:
            return fn(pl)
        finally:
            pl.close()
    return _on_a_thread(run)


FLAT = r"""() => {
  const w = document.getElementById('wB'); const S = w && w.__lp; if (!S) return null;
  const b = S.bars[0], m = /scaleY\(([-0-9.e]+)\)/.exec(b.bar.style.transform || ''), k = m ? +m[1] : 1;
  return { gauge: S.gauge || null, n_gauge_els: S.chart.querySelectorAll('.lp-gauge, .lp-gauge-rule').length,
           parentIsChart: b.bar.parentElement === S.chart, ticks: S.chart.querySelectorAll('text.lab[text-anchor="end"]').length,
           share: +b.bar.getAttribute('height') * k / (S.scale.my(0) - S.scale.my(100)),
           vanchor: b.val.getAttribute('text-anchor') };
}"""


class Player:
    """A split build of one timeline, served, and its probe (the gate's own reader)."""

    def __init__(self, tmp: Path, tl: dict, uris: dict):
        import probe as P
        self.P = P
        RB.write_split(tmp, tl, uris, "gauge.timeline.json")
        self.p = P.Probe(tmp, "gauge.timeline.json")

    def read(self, t: float) -> dict:
        self.p.seek(t)
        return self.p.page.evaluate(READ)

    def close(self) -> None:
        self.p.close()


@pytest.fixture(scope="module")
def h_gauge(tmp_path_factory):
    tl, uris = _timeline(GAUGE, H_EP)
    pl = Player(tmp_path_factory.mktemp("gauge-h"), tl, uris)
    try:
        yield pl
    finally:
        pl.close()


def _fill_share(d: dict, i: int = 0) -> float:
    return d["bars"][i]["h"] / (d["base"] - d["top"])


@needs_browser
def test_one_vertical_capsule_its_full_length_is_the_whole(h_gauge) -> None:
    d = h_gauge.read(REST_T)
    assert d is not None, "the page carries no gauge state"
    assert len(d["caps"]) == 1 and d["ceiling"] == 100
    x, y, w, h = d["caps"][0]["box"]
    assert abs(y - d["top"]) < 0.51 and abs(y + h - d["base"]) < 0.51     # the capsule runs zero -> the ceiling
    assert h > 2.5 * w                                                   # vertical
    assert d["bars"][0]["parentClip"], "the fill is not cut to the capsule"
    assert not d["callout"]                                              # no counting pill: the figure is the fill's


BUILD_TS = [0.0] + [round(3.8 + 0.1 * k, 2) for k in range(0, 25)] + [REST_T]


@pytest.fixture(scope="module")
def flat_progress(tmp_path_factory) -> dict:
    """The SAME object as the flat progress page (no form): its state at every build instant, read once."""
    def run(pl):
        out = {}
        for t in BUILD_TS:
            pl.p.seek(t)
            out[t] = pl.p.page.evaluate(FLAT)
        return out
    return _once(tmp_path_factory.mktemp("flat"), f"ledger:{H_OBJ}:progress::right", H_EP, run)


@needs_browser
def test_the_flat_progress_page_takes_no_gauge_branch(flat_progress) -> None:
    """The form is opt-in, observed: without `;form=gauge` the page builds no capsule, keeps its bar on the chart, prints
    the bars page's own six-division scale and writes its value centred over the bar - today's page."""
    d = flat_progress[REST_T]
    assert d["gauge"] is None and d["n_gauge_els"] == 0 and d["parentIsChart"]
    assert d["ticks"] > 2 and d["vanchor"] == "middle"


@needs_browser
def test_the_fill_rises_on_the_bar_clock_the_flat_pages_own(h_gauge, flat_progress) -> None:
    """Finding 8: not just 'a' clock - at every instant the capsule's fill stands at exactly the share the flat progress
    page's bar stands at (the same page, the same scale 0..100, T85's lpPaintChart grow unedited)."""
    shares = [(t, _fill_share(h_gauge.read(t))) for t in BUILD_TS]
    for t, s in shares:
        assert abs(s - flat_progress[t]["share"]) < 1e-6, (t, s, flat_progress[t]["share"])
    vals = [s for _t, s in shares]
    assert vals[0] < 0.02                                                # empty at the page's first frame
    assert all(b >= a - 1e-6 for a, b in zip(vals, vals[1:]))           # it only rises
    assert any(0.1 < s < 0.85 for s in vals)                             # ... through the middle, on a clock
    assert abs(vals[-1] - 0.94) < 0.004                                  # value / ceiling at rest


@needs_browser
def test_the_figure_is_written_at_the_fill_line_as_the_fill_lands(h_gauge) -> None:
    d = h_gauge.read(REST_T)
    b = d["bars"][0]
    assert b["val"] == "94%" and b["vop"] > 0.99                          # value_strings verbatim, with the unit
    assert b["vsize"] * d["stagePx"] >= PHONE_FLOOR - 0.01               # at the s90 phone floor at least
    assert b["vfill"] == ORANGE                                          # in its bar's ink
    vx, vy, vw, vh = b["vbox"]
    cx, _cy, cw, _ch = d["caps"][0]["box"]
    assert vx >= cx + cw                                                 # beside the capsule, never over it
    fill_line = d["base"] - b["h"]
    assert abs((vy + vh / 2) - fill_line) < 0.2 * vh                     # centred on the fill line
    mids = [h_gauge.read(round(3.8 + 0.1 * k, 2)) for k in range(0, 25)]
    mid = next(m for m in mids if 0.3 < _fill_share(m) < 0.8)            # the fill mid-rise
    assert mid["bars"][0]["vop"] < 0.01                                  # not before the fill lands


@needs_browser
def test_the_ceiling_rules_are_stubs_at_the_capsules_edges(h_gauge) -> None:
    """The frame read: the 100 tick and the whole's dashed rule end AT the capsule's edges - nothing crosses its rounded
    top - and each stub is at least probe.py's 4 px rule floor (M26's pairing; the M26 tests read through it)."""
    d = h_gauge.read(REST_T)
    x, _y, w, _h = d["caps"][0]["box"]
    rules = d["ceilRules"]
    assert len(rules) == 4 and all(r["shown"] for r in rules)          # 2 grid stubs + 2 hrule stubs
    for r in rules:
        lo, hi = min(r["x1"], r["x2"]), max(r["x1"], r["x2"])
        assert hi <= x + 0.05 or lo >= x + w - 0.05, r                   # outside the capsule's x range
        assert r["w"] >= 4, r                                            # stage px


@needs_browser
def test_the_empty_part_reads_at_bravos_tone(h_gauge) -> None:
    """TRACK_A: the capsule's empty part against the ground at Bravos D40's measured 1.741:1 (rgb 60,65,76 on 20,24,30),
    read off the rendered frame - the track just under the capsule's top, the ground at the same height, 2.5 capsules left."""
    from io import BytesIO

    from PIL import Image
    d = h_gauge.read(REST_T)
    im = Image.open(BytesIO(h_gauge.p.png(REST_T))).convert("RGB")
    sx, sy, sw, sh = d["capsScreen"][0]
    y = int(sy + 0.03 * sh)                                               # inside the 6 % the fill leaves
    def med(x0: int) -> tuple:
        px = sorted((im.getpixel((x, y + dy)) for x in range(x0 - 3, x0 + 4) for dy in (-1, 0, 1)), key=sum)
        return px[len(px) // 2]
    def lum(c):
        ch = [v / 255 for v in c]
        ch = [v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4 for v in ch]
        return 0.2126 * ch[0] + 0.7152 * ch[1] + 0.0722 * ch[2]
    track, ground = med(int(sx + sw / 2)), med(int(sx - 2.5 * sw))   # the ground clear of the "100%" label
    a, b = lum(track), lum(ground)
    ratio = (max(a, b) + 0.05) / (min(a, b) + 0.05)
    assert 1.70 <= ratio <= 1.85, (track, ground, ratio)


@needs_browser
def test_the_whole_is_named_over_the_capsule(h_gauge) -> None:
    d = h_gauge.read(REST_T)
    names = [w for w in d["whole"] if w["text"] == "every dollar from operations"]
    assert names and names[0]["op"] > 0.99 and names[0]["anchor"] == "middle"
    x, y, w, h = names[0]["box"]
    cx, cy, cw, _ch = d["caps"][0]["box"]
    assert y + h <= cy + 1 and abs((x + w / 2) - (cx + cw / 2)) < 1.0


@needs_browser
def test_m26_through_the_probe_the_printed_value_and_the_fill_agree_at_every_instant(h_gauge) -> None:
    instants = [(round(0.1 * k, 2), "build") for k in range(0, 81)] + [(REST_T, "hold")]   # the build lands ~5.9 s
    doc = h_gauge.P.probe_doc(h_gauge.p.build, "gauge.timeline.json", h_gauge.p, instants)
    fails, read, worst = G._value_faults(doc)
    landed = [i for i in doc["instants"] if (((i.get("page") or {}).get("bars") or {}).get("b") or [{}])[0].get("v")]
    assert fails == [] and read == len(landed) >= 10, (fails, read, len(landed))
    assert worst[0] < 0.01
    gate = G._values_gate(doc)
    assert gate.level == "PASS", gate.message


@needs_browser
def test_m26_fails_a_gauge_that_prints_a_number_its_fill_does_not_carry(tmp_path: Path) -> None:
    def lie(page: dict) -> None:
        page["value_strings"] = ["80"]
    doc = _once(tmp_path / "lie", GAUGE, H_EP,
                lambda pl: pl.P.probe_doc(pl.p.build, "gauge.timeline.json", pl.p, [(REST_T, "hold")]), lie)
    gate = G._values_gate(doc)
    assert gate.level == "FAIL" and "prints 80%" in gate.message, gate.message


@needs_browser
def test_it_composes_with_longform_and_soft(tmp_path: Path) -> None:
    def run(pl):
        return pl.read(REST_T), pl.P.probe_doc(pl.p.build, "gauge.timeline.json", pl.p, [(REST_T, "hold")])
    # H row 12's own options (`idle=live;readability=longform`) plus the soft bars: the page's life on, the long form's
    # sheet (which paints no gridline) and the shoulders - M26 must still read the fill against the printed scale
    d, doc = _once(tmp_path / "lf-soft", GAUGE + ";idle=live;readability=longform;bar_style=soft", H_EP, run)
    assert G._values_gate(doc).level == "PASS", G._values_gate(doc).message   # M26 reads the long form's gauge too
    b = d["bars"][0]
    assert b["vsize"] * d["stagePx"] >= PHONE_FLOOR - 0.01 and b["val"] == "94%"
    assert abs(_fill_share(d) - 0.94) < 0.004
    r = 14 / d["stagePx"]                                                # LPBAR_SOFT.SHOULDER_PX in chart units
    rr = f"{round(r, 2):g}"                                              # lpShoulderPath writes +v.toFixed(2)
    assert f"A{rr} {rr}" in d["caps"][0]["d"]                            # the capsule's ends take the shoulder
    assert d["hatch"] and d["feet"] == 0                                 # the hatch follows; no square foot pokes out


@needs_browser
def test_a_second_bar_draws_one_capsule_per_bar(ep: Path, tmp_path: Path) -> None:
    d = _once(tmp_path / "two", "ledger:g-two:progress;form=gauge", ep, lambda pl: pl.read(REST_T))
    assert len(d["caps"]) == 2
    assert abs(_fill_share(d, 0) - 0.60) < 0.004 and abs(_fill_share(d, 1) - 0.25) < 0.004
    # review finding 2 (s9.23b): a figure never meets ANY capsule - its own or its neighbour's
    for b in d["bars"]:
        vx, vy, vw, vh = b["vbox"]
        for c in d["caps"]:
            cx, cy, cw, ch = c["box"]
            assert vx + vw <= cx or vx >= cx + cw or vy + vh <= cy or vy >= cy + ch, (b["val"], b["vbox"], c["box"])
