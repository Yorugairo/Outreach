"""P72 T47 (R26-366, R26-316's build half): THE PANELS PAGE AT `longform:phone`, BUILT - where the arithmetic allows.

P72 T12 WARNed every panels page at phone (the subs at 15-35 px, the x ticks and the rule names overprinting, the y
axis thinned to one tick, the bars 4-13 px) and left the build to this slice. The phone layout, for a page the compiler
finds it HOLDS (`ledger_page.longform_panels_phone_band` -> `axes.panel_band_px`, the band in rendered px over every
panel's plot):

  - each panel's SUB at the floor (59.08 px) in its own band (F / SUB_MAX);
  - its RULE NAMES off their rules (two rules 1 % apart cannot each carry a 60 px name) and LADDERED in the band under
    the sub, one line each at the floor, highest rule first, in the rule's own ink, right-aligned in the panel;
  - the y axis at the finest nice step (<= 5 divisions) that writes TWO ticks 1.25 figures apart (E28: a stated scale);
  - the x labels thinned by the card's rule (the two ends kept, a middle label that would meet one dropped).

A page the phone layout cannot hold (four panels in two rows; the companion's 210 px under its key rail and a
three-line source) is drawn as it was, byte for byte, and keeps T12's WARN - whose tail now says why, with the numbers
(E99 s106: advice). `_longform_panel_scale` reads the region the panels are drawn in (the floor cut) and, at phone, the
band. Every other preset is the page it was.
"""
from __future__ import annotations

import copy
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
for p in (REPO / "content/video_engine/scripts", REPO / "content/video_engine/tests/golden",
          REPO / "content/video_engine/tests"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import build_golden_sources as G  # noqa: E402
import ledger_page as LPG  # noqa: E402

FLOOR = 12 * 1920 / 390        # E99 s90: 59.08 stage px (test_longform_profile.PHONE_FLOOR)
FIT_WARN = "WARN fit:"
BAND_KEY = "panel_band_px"
ENGINE = REPO / "docs/content-video-engine/samples/scene-evidence-engine.mjs"
LEAD = 1.21 - 1.1              # Inter's line box (ascent + descent) less the long form's leading: two lines' boxes meet this
                               # many ems at LINE_H 1.1 (the page's own multi-line sub does the same) - their ink never does


def _panels_page(series: dict, preset: str | None) -> dict:
    import build_scene_timeline_f as BST
    saved = BST.ASPECT
    BST.ASPECT = "16:9"
    try:
        page = BST.stamp_full_stage(LPG.build_spec(series, "line", None, "right"))
    finally:
        BST.ASPECT = saved
    if preset:
        LPG.apply_longform(page, preset)
    return page


def _fit(page: dict) -> list[str]:
    return [w for w in page.get("warnings") or [] if str(w).startswith(FIT_WARN)]


TWO_ERAS = lambda: LPG.load_series(G.PANELS_V3)  # noqa: E731
CANNOT = {"quad": G._panels_four, "mixed": G._panels_mixed, "companion": G.companion_series}


# ---- the compiler: which page holds, and the band it stamps ----------------------------------------------------------
def test_the_two_era_page_holds_at_phone_and_is_no_longer_warned() -> None:
    page = _panels_page(TWO_ERAS(), "phone")
    assert _fit(page) == [], _fit(page)
    band = page["axes"][BAND_KEY]
    # the sub band (the floor over SUB_MAX) and two rule names one floor line each (LINE_H)
    assert band == pytest.approx(FLOOR / 0.8 + 2 * 1.1 * FLOOR, abs=0.01), band


@pytest.mark.parametrize("name", sorted(CANNOT))
def test_a_page_the_phone_layout_cannot_hold_keeps_the_warn_and_takes_no_band(name) -> None:
    page = _panels_page(CANNOT[name](), "phone")
    (w,) = _fit(page)
    assert BAND_KEY not in page["axes"], page["axes"].get(BAND_KEY)
    assert "P72 T47's phone layout" in w and "R26-316's build is its own slice" not in w, w


def test_the_companion_warn_says_why_the_phone_layout_does_not_hold() -> None:
    (w,) = _fit(_panels_page(G.companion_series(), "phone"))
    assert w.startswith("WARN fit: a panels page at readability=longform:phone gets a 210 px region and a panel needs "
                        "~327 px"), w
    tail = w.split(" - it renders as drawn (E99 s106: advice; ", 1)[1]
    assert tail.startswith("P72 T47's phone layout - the subs at the floor, the rule names laddered, two y ticks - "
                           "does not hold it: "), tail
    # the companion's 210 px leave its line panel no plot that writes two ticks, and its bars panel bars under a tick
    assert tail.endswith("panel 0 writes no two y ticks 77 px apart on its 30 px plot; panel 1's bars get no plot "
                         "under the band)"), tail


@pytest.mark.parametrize("preset", [None, "middle", "bravos"])
def test_every_other_preset_takes_no_band(preset) -> None:
    for series in (TWO_ERAS(), G.companion_series(), G._panels_mixed(), G._panels_four()):
        page = _panels_page(series, preset)
        assert BAND_KEY not in (page.get("axes") or {}), preset
        assert _fit(page) == [], preset


def test_the_band_is_the_compilers_an_authored_one_never_survives() -> None:
    """s106: a key the slice adds is refused by name when malformed - this one is never authored: every fit recomputes
    it and pops a stale or malformed value (a page the layout does not hold, any other preset)."""
    for series, preset in ((G.companion_series(), "phone"), (TWO_ERAS(), "middle")):
        page = _panels_page(series, None)
        page.setdefault("axes", {})[BAND_KEY] = "tall"
        LPG.apply_longform(page, preset)
        assert BAND_KEY not in page["axes"], (preset, page["axes"].get(BAND_KEY))
    page = _panels_page(TWO_ERAS(), "phone")
    page["axes"][BAND_KEY] = -1
    LPG.apply_longform(page, "phone")
    assert page["axes"][BAND_KEY] == pytest.approx(FLOOR / 0.8 + 2 * 1.1 * FLOOR, abs=0.01)
    assert len(_fit(page)) == 0


def test_the_panel_scale_reads_the_region_the_panels_are_drawn_in() -> None:
    """R26-366 (T12's finding): `_longform_panel_scale` read the chart box WITHOUT the floor cut - 0.888 px a unit on
    the two-era page at phone where its panels draw at 0.771. It reads the floor cut region now, and at phone the band:
    (475 - band) / 560."""
    page = _panels_page(TWO_ERAS(), "phone")
    band = page["axes"][BAND_KEY]
    assert LPG._longform_panel_scale(page) == pytest.approx((475.0 - band) / 560, abs=2e-3)
    assert LPG._longform_panel_scale(_panels_page(TWO_ERAS(), "middle")) == pytest.approx(656.0 / 616, abs=2e-3)
    assert LPG._longform_panel_scale(_panels_page(G.companion_series(), "phone")) == pytest.approx(210.0 / 616, abs=2e-3)


def test_the_phone_divisions_write_two_ticks_a_label_apart() -> None:
    """The two-era domain (0-7.632 %) on its phone plot: one division (the base) is a nice step of 10 - only "0%" -
    two are a step of 5, 0 % and 5 % 101 px apart (>= 1.25 x 61.4)."""
    divs = LPG.longform_phone_divs(154.4, 0.0, 7.632, 61.4)
    assert divs and LPG._panel_nice_step(7.632 / divs) == 5, divs   # 0 % and 5 %: the most divisions a step of 5 is
    assert LPG._panel_nice_step(7.632 / 1) == 10                     # the base's one division: "0%" alone
    assert LPG.longform_phone_divs(60.0, 0.0, 7.632, 61.4) is None   # no two ticks a label apart: the page does not hold


# ---- the engine: the page as drawn -----------------------------------------------------------------------------------
READ = """() => { const s = document.getElementById('stage').getBoundingClientRect();
  const w = [...document.querySelectorAll('.world.ledger')].find((x) => x.__lp && x.__lp.panels);
  const R = (e) => { const r = e.getBoundingClientRect(); return [r.x - s.x, r.y - s.y, r.width, r.height]; };
  const op = (e) => { let n = e, o = 1; while (n && n !== document.body) { const cs = getComputedStyle(n);
    if (cs.display === 'none' || cs.visibility === 'hidden') return 0; o *= +(cs.opacity || 1);
    const a = n.getAttribute && n.getAttribute('opacity'); if (a != null && a !== '') o *= +a; n = n.parentElement; } return o; };
  return w.__lp.panels.map((S) => ({ box: R(S.box), chart: R(S.chart), op: op(S.box), vb: S.chart.getAttribute('viewBox'),
    plot: S.lfPanelEl ? R(S.lfPanelEl) : null,
    ylabs: (S.marks || []).filter((m) => m.role === 'ylabel' && m.el && m.el.isConnected).map((m) => m.el.textContent),
    xlabs: (S.marks || []).filter((m) => m.role === 'xtick' && m.el && m.el.isConnected).map((m) => m.el.textContent),
    rules: (S.hlines || []).filter((h) => h.lab).map((h) => ({ t: h.lab.textContent, box: R(h.lab), op: op(h.lab), fill: h.lab.style.fill,
      col: h.col, px: parseFloat(getComputedStyle(h.lab).fontSize) * (h.lab.getScreenCTM() ? Math.hypot(h.lab.getScreenCTM().a, h.lab.getScreenCTM().b) : 1) })),
    words: [...S.chart.querySelectorAll('text')].filter((e) => e.textContent.trim() && op(e) > 0.05).map((e) => { const m = e.getScreenCTM();
      return { t: e.textContent.trim().slice(0, 40), box: R(e), px: parseFloat(getComputedStyle(e).fontSize) * (m ? Math.hypot(m.a, m.b) : 1),
               cls: e.getAttribute('class') || '' }; }) })); }"""
SEEK = "t => { const s = document.getElementById('scrub'); s.value = t; s.dispatchEvent(new Event('input', {bubbles:true})); }"


def _timeline(series: dict, preset: str, species: list[dict]) -> tuple[dict, dict]:
    import build_scene_timeline_f as BST
    saved = BST.ASPECT
    BST.ASPECT = "16:9"
    try:
        page = BST.stamp_full_stage(LPG.build_spec(series, "line", None, "right"))
        LPG.apply_longform(page, preset)
        world = {"kind": "ledger", "page": page, "ken_burns": {"scale": 0, "x": 0, "y": 0}}
        BST.derive_rescale_states(world, species, "ledger:golden-panels:line", REPO)
    finally:
        BST.ASPECT = saved
    scenes = [{"scene_id": "s01", "world": world, "exit": "cut", "span": [0.0, G.RUNTIME], "docks": [], "species": species}]
    tl = G._timeline("panels at " + preset, scenes, {}, "16:9")
    return tl, dict(G._base_uris(), **BST.longform_assets(tl))


def _resize_species() -> list[dict]:
    return [{"kind": "panel_focus", "at": 0.0, "dur": 0.05, "layout": "row", "active": [0], "hidden": [1]},
            {"kind": "panel_focus", "at": G.PANELS_RESIZE_AT, "dur": G.PANELS_RESIZE_DUR, "layout": "row", "active": [0, 1]},
            {"kind": "panel_focus", "at": G.PANELS_LEAVE_AT, "dur": G.PANELS_RESIZE_DUR, "layout": "row", "active": [1], "hidden": [0]}]


HELD, RESIZE_T = 12.0, (9.6, 12.9, 16.6)


@pytest.fixture(scope="module")
def drawn(tmp_path_factory) -> dict:
    """{(page, preset): {t: every panel's read}} - the two-era page held, and the resize golden's page at its instants."""
    import render_baseline as RB
    import served_player as SPL
    out = {}
    for name, species, times in (("two-eras", [], (HELD,)), ("resize", _resize_species(), RESIZE_T)):
        for preset in ("phone", "middle"):
            tl, uris = _timeline(TWO_ERAS(), preset, species)
            tmp = tmp_path_factory.mktemp(f"{name}-{preset}")
            html = tmp / "p.html"
            html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
            try:
                with SPL.served(html, 1920, 1080) as (pg, errs):
                    reads = {}
                    for x in times:
                        pg.evaluate(SEEK, x)
                        reads[x] = pg.evaluate(READ)
                    reads["errs"] = list(errs)
            except Exception as e:   # no chromium on this machine
                pytest.skip(f"playwright chromium unavailable: {e}")
            out[(name, preset)] = reads
    return out


def _meet(a, b, fa, fb) -> bool:
    """Two words' boxes overprint: they cross in x, and in y by more than the leading lets two lines' boxes meet."""
    x = min(a[0] + a[2], b[0] + b[2]) - max(a[0], b[0])
    y = min(a[1] + a[3], b[1] + b[3]) - max(a[1], b[1])
    return x > 0.5 and y > LEAD * max(fa, fb) + 0.5


def _phone_reads(drawn):
    return [(k, t, r) for k, reads in drawn.items() if k[1] == "phone" for t, r in reads.items() if t != "errs"]


def test_no_page_error(drawn) -> None:
    assert all(not reads["errs"] for reads in drawn.values()), {k: v["errs"] for k, v in drawn.items()}


def test_every_word_on_a_phone_panel_holds_the_floor(drawn) -> None:
    for k, t, read in _phone_reads(drawn):
        for i, panel in enumerate(read):
            if panel["op"] < 0.05:
                continue
            small = [(w["t"], round(w["px"], 2)) for w in panel["words"] if w["px"] < FLOOR - 0.01]
            assert not small, (k, t, i, small)


def test_no_two_words_on_a_phone_panel_overprint(drawn) -> None:
    for k, t, read in _phone_reads(drawn):
        for i, panel in enumerate(read):
            if panel["op"] < 0.05:
                continue
            ws = panel["words"]
            hits = [(a["t"], b["t"]) for j, a in enumerate(ws) for b in ws[j + 1:] if _meet(a["box"], b["box"], a["px"], b["px"])]
            assert not hits, (k, t, i, hits)


def test_every_word_stays_inside_its_panel(drawn) -> None:
    for k, t, read in _phone_reads(drawn):
        for i, panel in enumerate(read):
            if panel["op"] < 0.999:
                continue
            bx = panel["chart"]   # the drawn svg (a re-laid-out build is wider than its home box)
            out = [w["t"] for w in panel["words"] if w["box"][0] < bx[0] - 1 or w["box"][0] + w["box"][2] > bx[0] + bx[2] + 1
                   or w["box"][1] < bx[1] - 1 or w["box"][1] + w["box"][3] > bx[1] + bx[3] + 1]
            assert not out, (k, t, i, out)


def test_the_y_axis_states_its_scale_with_two_ticks(drawn) -> None:
    for k, t, read in _phone_reads(drawn):
        for i, panel in enumerate(read):
            assert len(panel["ylabs"]) >= 2, (k, t, i, panel["ylabs"])
    held = drawn[("two-eras", "phone")][HELD]
    assert [p["ylabs"] for p in held] == [["0%", "5%"], ["0%", "5%"]], [p["ylabs"] for p in held]


def test_the_x_axis_keeps_its_span(drawn) -> None:
    """The card's rule: the first and the last label are always written (E28 - a time axis says where it starts and
    ends); a middle label that would meet a kept one is dropped."""
    held = drawn[("two-eras", "phone")][HELD]
    for panel, (first, last) in zip(held, (("1998", "2001"), ("2021", "2026"))):
        assert panel["xlabs"][0] == first and panel["xlabs"][-1] == last, panel["xlabs"]


def test_the_rule_names_stand_in_the_band_in_their_rules_order_and_ink(drawn) -> None:
    held = drawn[("two-eras", "phone")][HELD]
    shown = [p for p in held if any(r["op"] > 0.5 for r in p["rules"])]
    assert shown, "a panel names its rules at the held instant"
    for p in shown:
        names = sorted(p["rules"], key=lambda r: r["box"][1])
        assert [r["t"] for r in names] == ["Fed funds peak, 2000 - 6.5%", "their tripwire - 5.5%"], names
        assert all(r["box"][1] + r["box"][3] <= p["plot"][1] + 1 for r in names), (names, p["plot"])   # over the plot
        assert all(r["px"] >= FLOOR - 0.01 for r in names), names


def test_every_other_preset_draws_the_panel_as_it_did(drawn) -> None:
    """At `middle` the page takes no band: its panels' viewBox is today's (a sub band of 56 units)."""
    for (name, preset), reads in drawn.items():
        if preset != "middle":
            continue
        for t, read in reads.items():
            if t == "errs":
                continue
            for panel in read:
                assert panel["vb"].split()[1] == "-56", (name, t, panel["vb"])


def test_the_engine_reads_the_band_only_at_phone() -> None:
    src = ENGINE.read_text(encoding="utf-8")
    assert "panel_band_px" in src
    line = next(ln for ln in src.splitlines() if "panel_band_px" in ln and "lpLongformPhoneOf" in ln)
    assert "lpLongformPhoneOf(pg)" in line, line
