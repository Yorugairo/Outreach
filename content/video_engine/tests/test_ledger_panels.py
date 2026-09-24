"""P69 T8b (E99 s104, amended twice): THE LEDGER PAGE DRAWS PANELS, AND FOCUS IS A COMPOSABLE STATE.

A `panels` evidence object - the format `ev-tnx-two-eras-v3` carries and the card's `chart_dock:panels` draws -
compiles as a ledger PAGE of two to four plots, each with its own sub, axes and end tags, one scale by default
(E79). Before this slice it compiled to a dense-line page with 0 series. A `panel_focus` species on a word moves
every panel's box, ink and blur on one clock (the engine's `lpPanelPoses`); the compiler normalises it here.
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "content/video_engine/scripts"))

import build_scene_timeline_f as B  # noqa: E402
import ledger_page as LPG  # noqa: E402

OBJECTS = REPO / "content/video_engine/projects/systems-and-blowups/steel-and-paper/evidence/objects"
TWO_ERAS = OBJECTS / "ev-tnx-two-eras-v3.series.json"
FIXTURE = json.loads(LPG.PAGE_BOXES_FIXTURE.read_text(encoding="utf-8"))


def _two_eras() -> dict:
    return LPG.load_series(TWO_ERAS)


def _four(**page) -> dict:
    xs = [2016 + i for i in range(9)]
    mk = lambda k: [[x, round(1 + k * 0.5 + 0.1 * i, 2)] for i, x in enumerate(xs)]  # noqa: E731
    return dict({"title": "Four", "src": "synthetic", "yunit": "%",
                 "panels": [{"sub": f"P{k}", "series": [{"name": f"S{k}", "label": f"{k}%", "pts": mk(k)}]} for k in range(4)]},
                **page)


def _world(series: dict) -> dict:
    B.ASPECT = "16:9"
    return {"kind": B.SPECIES_LEDGER, "page": B.stamp_full_stage(LPG.build_spec(series, "line")),
            "ken_burns": {"scale": 0, "x": 0, "y": 0}}


# ---- the page ----------------------------------------------------------------------------------------------------
def test_a_panels_object_compiles_to_a_panels_page_not_an_empty_dense_line() -> None:
    """The Expected RED: v3 built as a dense-line page with 0 series (P69 T23)."""
    spec = LPG.build_spec(_two_eras(), "line")
    assert spec["builder"] == "panels", spec["builder"]
    panels = spec["panels"]
    assert len(panels) == 2
    assert [p["sub"] for p in panels] == ["Dot-com era - 1998-2001", "AI era - 2021-today"]
    assert all(len(p["series"]) == 1 for p in panels), [len(p["series"]) for p in panels]
    assert "panels" not in spec["axes"], "the panels are the spec's own key, never duplicated into the page's axes"


def test_E79_panels_of_one_measure_share_ONE_scale_by_default() -> None:
    """The card's own rule: min and max over every panel, the rules and ymin/ymax, 6 % air on top (ymin names the floor)."""
    doms = [p["axes"]["domain"] for p in LPG.build_spec(_two_eras(), "line")["panels"]]
    assert doms[0] == doms[1] == [0.0, pytest.approx(7.632)], doms


def test_independent_gives_each_panel_its_own_scale_and_no_warning() -> None:
    spec = LPG.build_spec(_four(independent=True), "line")
    doms = [tuple(p["axes"]["domain"]) for p in spec["panels"]]
    assert len(set(doms)) == 4, doms
    assert "warnings" not in spec


def test_a_panel_declaring_its_own_domain_keeps_it_and_the_build_WARNs_E79() -> None:
    """E99 s106: the author's domain stands; a same-unit panel off the shared scale is a WARN, never a refusal."""
    series = _four()
    series["panels"][2]["domain"] = [0, 50]
    assert LPG.validate(series, "line") == []
    spec = LPG.build_spec(series, "line")
    assert spec["panels"][2]["axes"]["domain"] == [0, 50]
    assert len(spec["warnings"]) == 1 and "panels[2]" in spec["warnings"][0] and "independent" in spec["warnings"][0]
    series["panels"][2]["independent"] = True
    assert "warnings" not in LPG.build_spec(series, "line")


def test_a_panels_page_is_two_to_four_plots_each_named() -> None:
    one = _four()
    one["panels"] = one["panels"][:1]
    assert any("at least 2" in e for e in LPG.validate(one, "line"))
    five = _four()
    five["panels"].append(copy.deepcopy(five["panels"][0]))
    assert any("ceiling is 4" in e for e in LPG.validate(five, "line"))
    nameless = _four()
    del nameless["panels"][1]["sub"]
    assert any("panels[1] has no 'sub'" in e for e in LPG.validate(nameless, "line"))


def test_each_panel_ticks_its_own_x_span_and_the_rules_are_named_on_the_panel_with_room() -> None:
    spec = LPG.build_spec(_two_eras(), "line")
    ticks = [[t[1] for t in p["axes"]["xticks"]] for p in spec["panels"]]
    assert ticks == [["1998", "1999", "2000", "2001"], ["2021", "2022", "2023", "2024", "2025", "2026"]], ticks
    assert spec["panel_rule_home"] == 1, "the AI era's right end stands under 5 %, the dot-com's at 5.1 % over the 5.5 % rule"
    assert all(len(p["axes"]["hlines"]) == 2 and all(h.get("label") for h in p["axes"]["hlines"]) for p in spec["panels"])
    assert all(p["axes"]["unit"] == "%" for p in spec["panels"]), "E28: every panel's ticks carry the unit"


def test_a_plain_panels_end_tags_are_fitted_to_its_own_margin() -> None:
    """A tag past the panel's right margin runs into the next panel or off the stage (read on the first render)."""
    spec = LPG.build_spec(_two_eras(), "line")
    assert [p["axes"]["tag_form"] for p in spec["panels"]] == ["badge", "badge"]   # the label alone: no inline badge rides it
    assert LPG.build_spec(_four(), "line")["panels"][0]["axes"]["tag_form"] == "full"


# ---- the layout law ---------------------------------------------------------------------------------------------
REGION = (58.0, 216.0, 1822.0, 656.0)
ASPECT = LPG.panel_aspect(2, REGION)


def test_one_active_panel_stands_where_a_single_chart_stands() -> None:
    (b,) = LPG.panel_layout("row", 1, REGION, ASPECT)
    assert b[0] == REGION[0] and b[1] == REGION[1] and b[3] == pytest.approx(REGION[3])


def test_a_lone_active_panel_spans_the_whole_region_T8c() -> None:
    """P69 T8c (E99 s104 amended): a standing single chart FILLS the plot region - its box is the region's full width,
    not its home slot's (T8b stood it at its slot and the single <-> row resize was a fade)."""
    (b,) = LPG.panel_layout("row", 1, REGION, ASPECT)
    assert b == pytest.approx(REGION), b
    (s,) = LPG.panel_layout("stack", 1, REGION, ASPECT)
    assert s == pytest.approx(REGION), s


def test_a_box_takes_its_cells_width_and_never_more_height_than_the_panels_aspect_T8c() -> None:
    """The layout law after T8c: every active box is its cell's FULL WIDTH (the line builder re-lays its plot out at any
    width); its height is the cell's, or the panel aspect's when the cell is taller - the builder's landscape plot is a
    fixed height, so a taller cell is met at the aspect, hung from its top (T8b's case, folded in). A quad panel growing
    to the page is therefore exactly T8b's box, and portrait (`fill=False`) keeps T8b's law whole."""
    for layout, k in (("row", 2), ("row", 3), ("stack", 2), ("quad", 4), ("quad", 3), ("quad", 2), ("row", 1)):
        cells = LPG.panel_cells(layout, k, REGION)
        for (x, y, w, h), c in zip(LPG.panel_layout(layout, k, REGION, ASPECT), cells):
            assert (x, y, w) == pytest.approx(c[:3]) and h == pytest.approx(min(c[3], c[2] / ASPECT))
    quad = LPG.panel_aspect(4, REGION)
    assert LPG.panel_layout("row", 1, REGION, quad)[0][3] == pytest.approx(REGION[2] / quad), "the quad grow: T8b's box"
    assert LPG.panel_layout("row", 1, REGION, ASPECT, fill=False)[0][2] == pytest.approx(ASPECT * REGION[3]), "portrait: T8b"
    assert LPG.panel_fit((0, 0, 900, 200), 2.0) == pytest.approx((0, 0, 900, 200))
    assert LPG.panel_fit((0, 0, 300, 400), 2.0) == pytest.approx((0, 125, 300, 150))


def test_a_row_a_stack_and_a_quad_keep_every_panels_aspect_inside_the_region() -> None:
    for layout, k in (("row", 2), ("row", 3), ("stack", 2), ("quad", 4), ("quad", 3), ("quad", 2)):
        boxes = LPG.panel_layout(layout, k, REGION, ASPECT, fill=False)   # T8b's fixed-aspect law, portrait's since T8c
        assert len(boxes) == k
        for x, y, w, h in boxes:
            assert w / h == pytest.approx(ASPECT)
            assert x >= REGION[0] - 1e-6 and y >= REGION[1] - 1e-6
            assert x + w <= REGION[0] + REGION[2] + 1e-6 and y + h <= REGION[1] + REGION[3] + 1e-6
        for i, a in enumerate(boxes):   # never on each other
            for c in boxes[i + 1:]:
                assert a[0] + a[2] <= c[0] + 1e-6 or c[0] + c[2] <= a[0] + 1e-6 or a[1] + a[3] <= c[1] + 1e-6 or c[1] + c[3] <= a[1] + 1e-6
    q = LPG.panel_layout("quad", 4, REGION, ASPECT)
    assert q[0][1] == q[1][1] < q[2][1] == q[3][1] and q[0][0] == q[2][0] < q[1][0] == q[3][0], "a 2 x 2 in reading order"


def test_page_boxes_carry_every_panels_home_box_and_the_plot_covers_them() -> None:
    boxes = LPG.page_boxes(_world(_two_eras())["page"], "16:9")
    panels = boxes["panels"]
    assert len(panels) == 2 and panels[0]["box"]["x"] < panels[1]["box"]["x"]
    assert panels[0]["box"]["y"] == panels[1]["box"]["y"]
    plot = boxes["plot"]
    for p in panels:
        assert plot["x"] <= p["plot"]["x"] and plot["x"] + plot["w"] >= p["plot"]["x"] + p["plot"]["w"] - 1
    assert "tags" not in boxes, "no page-wide end-tag column: each panel's tags stand in its own box"
    assert panels[1]["box"]["x"] + panels[1]["box"]["w"] <= LPG.LAND_PHONE_SAFE_RIGHT * 1920 + 1
    assert panels[0]["box"]["y"] + panels[0]["box"]["h"] <= LPG.CAPTION_ANCHOR["16:9"][1], "the ticks clear the caption strip"


def test_the_estimate_is_the_players_panels_the_fixture_measured() -> None:
    """The layout law in Python is the engine's, line for line: the estimate of every panel's home box agrees with the
    player's own measurement (the `panels` representative in the fixture) at both aspects and full stage."""
    rep = FIXTURE["builders"]["panels"]
    for key, entry in rep.items():
        aspect = key.split("|")[0]
        page = LPG.build_spec(_two_eras(), "line")
        if key.endswith("|full_stage"):
            B.ASPECT = "16:9"
            page = B.stamp_full_stage(page)
        est = LPG.panel_boxes(page, entry["boxes"]["chart"], aspect)
        for e, m in zip(est, entry["panels"]):
            assert all(abs(e["box"][d] - m["box"][d]) <= 1 for d in "xywh"), (key, e["box"], m["box"])


# ---- the long form -----------------------------------------------------------------------------------------------
def test_the_long_form_composes_one_key_rail_for_the_page_and_each_panel_its_own_tags() -> None:
    page = _world(_two_eras())["page"]
    assert LPG.readability_error(page, "longform", "panels") is None
    assert LPG.readability_error(page, "landscape-phone", "panels") is not None
    LPG.apply_longform(page, "middle")
    assert [p["axes"]["tag_form"] for p in page["panels"]] == ["badge", "badge"]
    assert page["axes"]["key"] == [{"panel": 0, "series": 0, "name": "10-YEAR TREASURY YIELD"}], "one name, once (E53 s8)"


# ---- the compiler: the panel address and the focus states ---------------------------------------------------------
PLATE = "ledger:golden-panels:line"


def _compile(series: dict, species: list) -> list:
    world = _world(series)
    assert B.validate_species(species, (0, 0, 0), PLATE) == []
    B.derive_rescale_states(world, species, PLATE, REPO)
    return species


def test_a_focus_state_normalises_to_a_role_per_panel_and_every_dial() -> None:
    (fs,) = _compile(_four(), [{"kind": "panel_focus", "at": 9.0, "dur": 1.0, "layout": "row", "active": [1], "hidden": [3],
                                "recede": {"blur": 8}}])
    assert fs["roles"] == ["receded", "active", "receded", "hidden"]
    assert fs["recede"] == {"scale": LPG.PANEL_RECEDE["scale"], "dim": LPG.PANEL_RECEDE["dim"], "blur": 8.0}
    assert fs["boxes"] == [None] * 4 and "active" not in fs
    again = copy.deepcopy(fs)
    B.panel_focus_state(again, 4, "again")
    assert again == fs, "normalising is idempotent"


def test_roles_may_name_the_exceptions_and_free_names_a_box_per_active_panel() -> None:
    (fs,) = _compile(_four(), [{"kind": "panel_focus", "at": 9.0, "dur": 1.0, "layout": "free",
                                "roles": {"2": "receded", "3": "hidden"},
                                "boxes": {"0": [0.05, 0.2, 0.4, 0.3], "1": [0.5, 0.2, 0.4, 0.3]}}])
    assert fs["roles"] == ["active", "active", "receded", "hidden"]
    assert fs["boxes"][2] is None and fs["boxes"][0] == [0.05, 0.2, 0.4, 0.3]


@pytest.mark.parametrize("entry, why", [
    ({"layout": "row", "active": [4]}, "last panel is 3"),
    ({"layout": "row", "roles": ["hidden", "receded", "receded", "receded"]}, "no panel in focus"),
    ({"layout": "free", "active": [0], "boxes": {"1": [0.1, 0.1, 0.3, 0.3]}}, "no box"),
])
def test_a_focus_state_that_does_not_fit_the_page_is_refused_by_name(entry, why) -> None:
    with pytest.raises(ValueError, match=why):
        _compile(_four(), [dict({"kind": "panel_focus", "at": 9.0, "dur": 1.0}, **entry)])


@pytest.mark.parametrize("entry, why", [
    ({"layout": "diagonal", "active": [0]}, "layout must be one of"),
    ({"layout": "row"}, "name the ACTIVE panels"),
    ({"layout": "row", "active": [0], "recede": {"scale": 2}}, "recede.scale"),
    ({"layout": "row", "active": [0], "region": [0.5, 0.5, 0.9, 0.9]}, "region must be"),
    ({"layout": "free", "active": [0]}, "BOX per panel"),
    ({"layout": "row", "active": [0], "zoom": 2}, "unknown key"),
])
def test_the_focus_grammar_is_checked_before_the_page(entry, why) -> None:
    errs = B.validate_species([dict({"kind": "panel_focus", "at": 9.0, "dur": 1.0}, **entry)], (0, 0, 0), PLATE)
    assert any(why in e for e in errs), errs


def test_a_species_lands_in_the_panel_it_names_and_a_datum_target_carries_it() -> None:
    sp = _compile(_two_eras(), [
        {"kind": "build_to", "at": 5.0, "dur": 1.0, "panel": 1, "target": {"kind": "datum", "series": 0, "index": 20}},
        {"kind": "callout", "at": 8.0, "dur": 2.0, "label": "4.7%", "target": {"kind": "datum", "series": 0, "index": 141, "panel": 1}},
        {"kind": "figure", "at": 9.0, "dur": 1.0, "text": "6.5%", "target": {"kind": "datum", "index": 73}}])
    assert sp[0]["target"]["panel"] == 1 and sp[1]["target"]["panel"] == 1 and sp[2]["target"]["panel"] == 0


@pytest.mark.parametrize("sp, why", [
    ({"kind": "build_to", "at": 5.0, "dur": 1.0, "panel": 2, "target": {"kind": "datum", "index": 3}}, "past the page's last panel"),
    ({"kind": "undraw", "at": 5.0, "dur": 1.0, "panel": 0, "series": 1, "target": {"kind": "datum", "index": 0}}, "past panel 0's last series"),
    ({"kind": "chart_to", "at": 5.0, "dur": 1.0, "to": "recast", "state": 1, "panel": 0}, "ONE chart state"),
    ({"kind": "build_to", "at": 5.0, "dur": 1.0, "panel": 0, "target": {"kind": "datum", "index": 3, "panel": 1}}, "disagree"),
])
def test_an_address_the_page_cannot_draw_is_refused_by_name(sp, why) -> None:
    with pytest.raises(ValueError, match=why):
        _compile(_two_eras(), [sp])


def test_a_panel_address_or_a_focus_state_on_a_page_with_no_panels_is_refused() -> None:
    line = {"title": "one line", "src": "synthetic", "series": [{"name": "A", "pts": [[i, i] for i in range(20)]},
                                                             {"name": "B", "pts": [[i, 2 * i] for i in range(20)]}]}
    for sp, why in (({"kind": "panel_focus", "at": 5.0, "dur": 1.0, "layout": "row", "active": [0]}, "PANELS page"),
                    ({"kind": "build_to", "at": 5.0, "dur": 1.0, "panel": 0, "target": {"kind": "datum", "index": 3}}, "PANELS page")):
        with pytest.raises(ValueError, match=why):
            _compile(line, [sp])


def test_a_page_with_no_panels_compiles_the_bytes_it_always_did() -> None:
    """Byte identity at the spec: a line page is untouched by the builder, and `check_panels` writes nothing on it."""
    series = LPG.load_series(OBJECTS / "ev-tnx-two-eras-v4.series.json")
    spec = LPG.build_spec(series, "line")
    assert spec["builder"] == "dense-line" and "panels" not in spec and "panel_rule_home" not in spec
    species = [{"kind": "build_to", "at": 5.0, "dur": 1.0, "target": {"kind": "datum", "series": 1, "index": 20}}]
    before = copy.deepcopy(species)
    _compile(series, species)
    assert species == before


# ---- the player: a focus change is a pure function of t ------------------------------------------------------------
def _chromium() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


POSE_READ = """() => { const w = [...document.querySelectorAll('.world.ledger')].find((x) => x.__lp && x.__lp.panels);
  return w.__lp.panels.map((S) => [S.box.style.cssText, S.chart.style.opacity, S.chart.getAttribute('viewBox'), S.chart.style.width,
    ...S.paths.map((p) => p.p.getAttribute('stroke-dashoffset') + '|' + p.name.getAttribute('opacity'))]); }"""


MOVING = {   # what says the golden's instant is mid-move: the quad's panels scale; the resize's panel 1 is RE-LAID OUT
    "panels-quad-grow": lambda poses: any("scale(" in p[0] and "scale(1.00000)" not in p[0] for p in poses),
    "panels-resize": lambda poses: poses[0][3] not in ("", "100%") and float(poses[0][2].split()[2]) > 1.2 * float(poses[1][2].split()[2]),
    "panels-mixed-grow": lambda poses: any("scale(" in p[0] and "scale(1.00000)" not in p[0] for p in poses),   # P69 T8d
}


@pytest.mark.skipif(not _chromium(), reason="playwright chromium not installed")
@pytest.mark.parametrize("surface", sorted(MOVING))
def test_a_focus_change_is_seek_safe_forward_play_paints_what_a_cold_seek_paints(tmp_path, surface) -> None:
    """The quad golden mid-grow (u 0.50), and (P69 T8c) the resize golden mid-resize - its panel 1 a build re-laid out
    for its box's width, swapped in per width. Forward play in 0.1 s steps across the grow paints the cold seek's pixels
    exactly (the repo's own seek law: test_prop_free_placement), and a BACKWARD jump from past the grow leaves every
    panel's pose - its box, transform, ink, blur, depth, its line's dash and its tags - exactly as the cold seek wrote
    it. (The one thing a backward jump may move is Chromium's raster of a blurred layer's edge: <= 1 level of 255.)"""
    import render_baseline as RB
    from playwright.sync_api import sync_playwright
    tl, uris, t, aspect = RB.load_surface(surface)
    html = tmp_path / "p.html"
    html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
    srv, port = RB.serve(tmp_path)
    w, h = RB.STAGE[aspect]
    shots, poses = [], []
    forward = [round(t - 1.1 + 0.1 * i, 2) for i in range(11)]
    try:
        with sync_playwright() as pw:
            br = pw.chromium.launch(headless=True)
            for path in ([t], forward, [t + 6.0, t - 6.0]):
                pg = br.new_context(viewport={"width": w, "height": h}, device_scale_factor=1).new_page()
                pg.goto(f"http://127.0.0.1:{port}/{html.name}", wait_until="networkidle", timeout=120000)
                RB.prepare_page(pg, w, h)
                for x in path:
                    RB.frame_png(pg, x, (w, h))
                    pg.wait_for_timeout(100)
                shots.append(RB.frame_png(pg, t, (w, h)))
                poses.append(pg.evaluate(POSE_READ))
                pg.context.close()
            br.close()
    finally:
        srv.shutdown()
    if surface in ("panels-resize", "panels-mixed-grow") and shots[1] != shots[0]:
        # the page's rule NAMES crossfade to the panel coming into focus (T8b's `panel_rule_home`): a translucent haloed
        # <text> over the bloomed line, whose raster Chromium may round one level apart after play (the attributes are
        # identical - read on the probe). T8b's engine paints this very surface 2 levels apart; the pose law is exact.
        # P69 T8d: the growing BARS panel is a build per scale (the 196 px cap, as T8c's resize is a build per width) -
        # its box edge over the blurred panels behind rasterises <= 1 level apart after play (a 5 px strip, measured
        # `scratchpad/p69t8d/frames/seek1`); every pose, dash and ink is exact (the assertion below).
        import io
        from PIL import Image, ImageChops
        d = ImageChops.difference(*(Image.open(io.BytesIO(x)).convert("RGB") for x in shots[:2]))
        assert max(hi for _, hi in d.getextrema()) <= 1, "forward play across the resize paints another frame than the cold seek"
    else:
        assert shots[1] == shots[0], "forward play across the grow paints another frame than the cold seek"
    assert poses[1] == poses[0] and poses[2] == poses[0], "a panel's pose is not a function of t alone"
    assert MOVING[surface](poses[0]), "mid-move, the panels are moving"


RESIZE_READ = """() => { const s = document.getElementById('stage').getBoundingClientRect();
  const w = [...document.querySelectorAll('.world.ledger')].find((x) => x.__lp && x.__lp.panels);
  const R = (e) => { const r = e.getBoundingClientRect(); return [r.x - s.x, r.y - s.y, r.width, r.height]; };
  return w.__lp.panels.map((S) => { const lab = S.marks.find((m) => m.role === 'ylabel'), tick = S.marks.find((m) => m.role === 'tick' && m.geom.v === lab.geom.v);
    return { ground: R(S.chart.querySelector('.lp-pground')), plot: R(S.chart.querySelector('line.ax')), op: +(S.box.style.opacity || 1),
             lab: R(lab.el), labFs: parseFloat(getComputedStyle(lab.el).fontSize) * S.chart.getScreenCTM().d,
             grid: tick ? R(tick.el) : null, tag: R(S.paths[0].name) }; }); }"""


@pytest.mark.skipif(not _chromium(), reason="playwright chromium not installed")
def test_a_standing_chart_fills_the_region_and_RESIZES_into_its_slot_with_its_words_at_their_size_T8c(tmp_path) -> None:
    """P69 T8c. The golden `panels-resize`: panel 1 stands ALONE over the whole region, SHRINKS into its row slot on the
    word while panel 2 builds in beside it, and - on the leave - panel 2 GROWS back over the whole region. Every frame
    the plot is re-projected to its box's CURRENT width (mid-resize it is between the two), and the words are the
    same size throughout (a tick label's rendered size, its place on its own gridline, the end tag past the plot's
    end): E28, text never stretched."""
    import render_baseline as RB
    from playwright.sync_api import sync_playwright
    tl, uris, t_mid, aspect = RB.load_surface("panels-resize")
    html = tmp_path / "p.html"
    html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
    srv, port = RB.serve(tmp_path)
    w, h = RB.STAGE[aspect]
    reads = {}
    try:
        with sync_playwright() as pw:
            br = pw.chromium.launch(headless=True)
            pg = br.new_context(viewport={"width": w, "height": h}, device_scale_factor=1).new_page()
            pg.goto(f"http://127.0.0.1:{port}/{html.name}", wait_until="networkidle", timeout=120000)
            RB.prepare_page(pg, w, h)
            for tag, x in (("standing", 8.5), ("mid", t_mid), ("both", 12.0), ("survivor", 18.0)):
                RB.frame_png(pg, x, (w, h))
                reads[tag] = pg.evaluate(RESIZE_READ)
            br.close()
    finally:
        srv.shutdown()
    alone, mid, both, surv = (reads[k] for k in ("standing", "mid", "both", "survivor"))
    region_l, region_r = both[0]["ground"][0], both[1]["ground"][0] + both[1]["ground"][2]
    for who, p in (("standing panel 1", alone[0]), ("survivor panel 2", surv[1])):
        assert abs(p["ground"][0] - region_l) <= 1.5 and abs(p["ground"][0] + p["ground"][2] - region_r) <= 1.5, (who, p["ground"], region_l, region_r)
    full, slot, now = alone[0]["plot"][2], both[0]["plot"][2], mid[0]["plot"][2]
    assert full > 1.8 * slot, (full, slot)
    assert slot + 0.2 * (full - slot) < now < full - 0.2 * (full - slot), ("the plot re-projects mid-resize", slot, now, full)
    for p in (alone[0], mid[0], both[0], both[1], surv[1]):
        assert p["labFs"] == pytest.approx(alone[0]["labFs"], abs=0.05), "a tick label keeps its size"
        assert p["lab"][3] == pytest.approx(alone[0]["lab"][3], abs=0.6), "... its rendered height too"
        assert p["grid"] is None or abs(p["lab"][1] + p["lab"][3] / 2 - p["grid"][1]) < p["lab"][3], "... and stands on its gridline"
        assert p["tag"][0] >= p["plot"][0] + p["plot"][2] - 1, "the end tag stands past the plot's end"


# ---- P69 T8d (E99 s104 amended x2): A PANEL MAY BE BARS, AND A BAR MAY CARRY A RANGE -------------------------------
# Row 21 carries four charts, two of them bars (the wafer ratio; `ev-dram-contract-v1`). T8b's panels drew lines only
# ("has no line series"). A panel names its `builder` (line by default | bars); a bars panel keeps the bars rules (the
# 196 px bar, a value on its bar, the zero baseline, the unit as written). A bar's value may be a RANGE `[lo, hi]`: the
# bar stands at lo, a lighter band runs lo -> hi, and the page prints the range as the source states it - never a
# midpoint (the row-21 agent found `ev-dram-contract-v1` printing 57.5, a number no source states).
DASH = "–"
WAFER = [{"label": "Standard DRAM", "value": 1, "color": "deemph"},       # copied from ev-hbm-wafer-ratio-bars-v1
         {"label": "HBM (stacked dies)", "value": 3, "color": "crimson"}]
DRAM = [{"label": "Conventional DRAM", "value": ["+55", "60"], "color": "deemph"},   # ev-dram-contract-v1's note "+55-60%"
        {"label": "Server DRAM", "value": "+60", "color": "deemph"},                 # restated as the range it is
        {"label": "Consumer DRAM", "value": "+89", "color": "crimson"}]


def _mixed(**page) -> dict:
    """Two line panels and two bars panels - row 21's shape (a line, the wafer bars, a line, the contract bars)."""
    lines = _four()["panels"]
    return dict({"title": "Mixed", "src": "synthetic", "yunit": "%",
                 "panels": [lines[0], {"sub": "Wafer per gigabyte", "builder": "bars", "unit": "x", "bars": copy.deepcopy(WAFER)},
                            lines[2], {"sub": "Contract prices", "builder": "bars", "unit": "%", "independent": True,
                                       "bars": copy.deepcopy(DRAM)}]}, **page)


def _bars_page(bars: list, **page) -> dict:
    return dict({"title": "Memory contract prices", "src": "synthetic", "unit": "%", "bars": copy.deepcopy(bars)}, **page)


def test_a_bars_panel_compiles_as_a_bars_plot_on_a_panels_page_T8d() -> None:
    """The Expected RED: T8b refused a panel with no line series."""
    series = _mixed()
    assert LPG.validate(series, "line") == []
    spec = LPG.build_spec(series, "line")
    assert spec["builder"] == "panels" and [p.get("builder", "line") for p in spec["panels"]] == ["line", "bars", "line", "bars"]
    wafer = spec["panels"][1]
    assert wafer["labels"] == ["Standard DRAM", "HBM (stacked dies)"] and wafer["values"] == [1.0, 3.0]
    assert wafer["value_strings"] == ["1", "3"] and wafer["colors"] == ["deemph", "crimson"]
    assert wafer["unit"] == "x" and wafer["axes"]["unit"] == "x", "a bars panel's values carry ITS unit"
    assert "series" not in wafer and "tag_form" not in wafer["axes"], "a bars panel has no lines and no end tags"
    assert [p["sub"] for p in spec["panels"]] == spec["labels"]


def test_a_bars_panel_stands_on_zero_and_its_unit_group_shares_one_scale_E79_T8d() -> None:
    """E79: panels of one measure share one scale; a bars scale holds its zero (E28), with the bars page's own air (the
    engine's 14 %) away from it; a bars panel in another unit - or `independent` - stands on its own scale."""
    spec = LPG.build_spec(_mixed(), "line")
    wafer, dram = spec["panels"][1]["axes"]["domain"], spec["panels"][3]["axes"]["domain"]
    assert wafer == [0.0, pytest.approx(3 * 1.14)], wafer
    assert dram == [0.0, pytest.approx(89 * 1.14)], "the range's hi and the tallest bar both inside, zero at the floor"
    assert spec["panels"][0]["axes"]["domain"] == spec["panels"][2]["axes"]["domain"] != dram, "the % lines share theirs"
    two = _mixed()
    two["panels"][1] = dict(two["panels"][3], sub="Second", independent=False)
    two["panels"][3]["independent"] = False
    spec2 = LPG.build_spec(two, "line")
    doms = [p["axes"]["domain"] for p in spec2["panels"]]
    assert doms[1] == doms[3] == doms[0] == doms[2], "one unit ('%'), one scale - bars and lines of one measure (E79)"
    assert doms[1][0] == 0.0, "a group holding a bar keeps the zero"
    assert "warnings" not in spec2


def test_the_page_rules_are_the_lines_own_a_bars_panel_takes_only_its_own_T8d() -> None:
    series = _mixed(hlines=[{"y": 3, "label": "a rule"}])
    series["panels"][1]["hlines"] = [{"y": 2, "label": "twice", "color": "deemph"}]
    spec = LPG.build_spec(series, "line")
    assert [h["label"] for h in spec["panels"][0]["axes"]["hlines"]] == ["a rule"]
    assert [h["label"] for h in spec["panels"][1]["axes"]["hlines"]] == ["twice"], "its own comparator rule, verbatim"
    assert "hlines" not in spec["panels"][3]["axes"], "a page rule in another measure is not drawn across bars"


@pytest.mark.parametrize("mutate, why", [
    (lambda s: s["panels"][1].update(builder="pie"), "builder 'pie' is not one of line|bars"),
    (lambda s: s["panels"][1].update(bars=[]), "has no bars"),
    (lambda s: s["panels"][1].update(series=[{"name": "A", "pts": [[0, 1], [1, 2]]}]), "draws bars, not lines"),
    (lambda s: s["panels"][1].update(overflow="burst", domain=[0, 2]), "overflow"),
    (lambda s: s["panels"][1]["bars"][0].update(value="lots"), "is not numeric"),
    (lambda s: s["panels"][1]["bars"][0].pop("label"), "has no label"),
    (lambda s: s["panels"][0].update(bars=copy.deepcopy(WAFER)), "a line panel"),
])
def test_a_bars_panel_that_is_not_a_bars_chart_is_refused_by_name_T8d(mutate, why) -> None:
    series = _mixed()
    mutate(series)
    errs = LPG.validate(series, "line")
    assert any(why in e for e in errs), errs


# ---- the RANGE ---------------------------------------------------------------------------------------------------
def test_a_range_bar_stands_at_lo_and_prints_the_range_as_the_source_states_it_T8d() -> None:
    for spec, where in ((LPG.build_spec(_bars_page(DRAM), "bars"), "a bars page"),
                        (LPG.build_spec(_mixed(), "line")["panels"][3], "a bars panel")):
        assert spec["values"][0] == 55.0, (where, "the bar is drawn to what every source guarantees - its lo")
        assert spec["value_strings"][0] == "+55" + DASH + "60", (where, "the range as stated, never a midpoint")
        assert spec["ranges"] == [[55.0, 60.0], None, None], where
        assert 57.5 not in spec["values"], where
    assert LPG.validate(_bars_page(DRAM), "bars") == []


@pytest.mark.parametrize("bars, page, why", [
    ([{"label": "A", "value": [60, 55]}], {}, "runs backwards"),
    ([{"label": "A", "value": [55, 60]}], {"unit": None}, "has no unit"),
    ([{"label": "A", "value": [-5, 10]}], {}, "straddles zero"),
    ([{"label": "A", "value": [55]}], {}, "a RANGE is [lo, hi]"),
    ([{"label": "A", "value": [55, "sixty"]}], {}, "a RANGE is [lo, hi]"),
    ([{"label": "A", "value": [55, 60]}, {"label": "B", "value": 200}], {"overflow": "burst", "domain": [0, 100]}, "breakthrough"),
])
def test_a_range_that_is_not_honest_is_refused_by_name_T8d(bars, page, why) -> None:
    series = _bars_page(bars, **page)
    if series.get("unit") is None:
        series.pop("unit")
    errs = LPG.validate(series, "bars")
    assert any(why in e for e in errs), errs


def test_a_range_off_a_bars_chart_is_refused_T8d() -> None:
    """A range is a BAR's: a race, a decline or a progress page draws a value as a point in time or a share."""
    errs = LPG.validate(_bars_page([{"label": "A", "value": [1, 2]}, {"label": "B", "value": 3}]), "decline")
    assert any("a range is a BARS chart's" in e for e in errs), errs


def test_a_bars_page_with_no_range_compiles_the_page_it_always_did_T8d() -> None:
    """Byte identity at the spec: no `ranges` key, the tokens verbatim, the numbers the numbers."""
    spec = LPG.build_spec(_bars_page(WAFER, unit="x"), "bars")
    assert "ranges" not in spec
    assert spec["values"] == [1.0, 3.0] and spec["value_strings"] == ["1", "3"]
    eras = LPG.build_spec(_two_eras(), "line")
    assert "ranges" not in eras and all("builder" not in p for p in eras["panels"])


# ---- species on a bars panel ---------------------------------------------------------------------------------------
def _cmp(at: float = 22.0) -> dict:
    return {"kind": "chart_to", "at": at, "dur": 2.4, "to": "compare", "form": "melt", "then": "splash", "hold": "metric",
            "panel": 1, "metric": {"value": 3, "text": "3x", "label": "HBM against standard DRAM"},
            "comparator": {"value": 3, "text": "3 wafers", "label": "for the gigabytes 1 wafer of DRAM makes"},
            "inputs": {"hbm": 3, "dram": 1}, "derive": "hbm / dram", "source": "[DERIVED: synthetic, hbm / dram]"}


def test_a_figure_a_compare_a_callout_and_a_ring_land_on_a_bars_panel_T8d() -> None:
    sp = _compile(_mixed(), [
        {"kind": "figure", "at": 20.0, "dur": 1.2, "panel": 1, "text": "3x", "target": {"kind": "datum", "index": 1}},
        _cmp(),
        {"kind": "callout", "at": 25.0, "dur": 2.0, "label": "+89%", "target": {"kind": "datum", "index": 2, "panel": 3}},
        {"kind": "ring", "at": 27.0, "dur": 2.0, "form": "dashed", "target": {"kind": "datum", "index": 0, "panel": 3}}])
    assert [s.get("panel", (s.get("target") or {}).get("panel")) for s in sp] == [1, 1, 3, 3]
    assert sp[0]["target"]["panel"] == 1


@pytest.mark.parametrize("sp, why", [
    ({"kind": "build_to", "at": 5.0, "dur": 1.0, "panel": 1, "target": {"kind": "datum", "index": 1}}, "draws on a LINE"),
    ({"kind": "undraw", "at": 5.0, "dur": 1.0, "panel": 3, "target": {"kind": "datum", "index": 0}}, "draws on a LINE"),
    ({"kind": "lit_stretch", "at": 5.0, "dur": 1.0, "panel": 1, "from": 0, "to": 1}, "draws on a LINE"),
    ({"kind": "chart_to", "at": 5.0, "dur": 1.0, "to": "recast", "state": 1, "panel": 1}, "ONE chart state"),
    ({"kind": "figure", "at": 5.0, "dur": 1.0, "panel": 1, "text": "4x", "target": {"kind": "datum", "index": 2}}, "past panel 1's last bar"),
])
def test_a_species_a_bars_panel_cannot_draw_is_refused_by_name_T8d(sp, why) -> None:
    with pytest.raises(ValueError, match=why):
        _compile(_mixed(), [sp])


def test_a_bars_panel_on_a_portrait_page_is_refused_by_name_T8d(monkeypatch) -> None:
    """The portrait bars builder lays out a whole 9:16 page in stage px; a stacked panel cannot hold it (read on the
    frames: its ticks and values overprint) - refused, never drawn wrong. A 9:16 page of LINE panels stands as T8b built it."""
    world = _world(_mixed())
    monkeypatch.setattr(B, "ASPECT", "9:16")
    with pytest.raises(ValueError, match="a BARS panel is drawn on a 16:9 page"):
        B.check_panels(world, [])
    B.check_panels({"kind": B.SPECIES_LEDGER, "page": LPG.build_spec(_four(), "line")}, [])   # line panels: T8b's page


# ---- the boxes ---------------------------------------------------------------------------------------------------
def test_a_mixed_pages_ink_says_which_panels_are_bars_and_a_line_page_keeps_its_key_T8d() -> None:
    line4 = LPG.build_spec(_four(), "line")
    mixed = LPG.build_spec(_mixed(title="Four"), "line")
    assert LPG.page_ink_key(line4) != LPG.page_ink_key(mixed), "a bars panel's plot is not a line panel's"
    boxes = LPG.page_boxes(_world(_mixed())["page"], "16:9")
    line_p, bars_p = boxes["panels"][0]["plot"], boxes["panels"][1]["plot"]
    assert bars_p["y"] > line_p["y"], "a bars plot's top is the bars builder's (90 units), under a line plot's (40)"
    for p in boxes["panels"]:
        b = p["box"]
        assert b["x"] <= p["plot"]["x"] and p["plot"]["x"] + p["plot"]["w"] <= b["x"] + b["w"] + 1


def test_the_mixed_representative_is_measured_and_the_estimate_agrees_on_every_panel_box_T8d() -> None:
    import measure_page_boxes as M
    name = LPG.PANELS + LPG.REPRESENTATIVE_SEP + "bars"
    assert name in M.BUILDERS and name in FIXTURE["builders"]
    rep = M.representative(name)
    assert [p.get("builder", "line") for p in rep["panels"]].count("bars") == 2
    for key, entry in FIXTURE["builders"][name].items():
        aspect = key.split("|")[0]
        page = copy.deepcopy(rep)
        if key.endswith("|full_stage"):
            B.ASPECT = "16:9"
            page = B.stamp_full_stage(page)
        got = LPG.page_boxes(page, aspect)
        assert got["measured"] is True, key
        est = LPG.panel_boxes(page, entry["boxes"]["chart"], aspect)
        for e, m in zip(est, entry["panels"]):
            assert all(abs(e["box"][d] - m["box"][d]) <= 1 for d in "xywh"), (key, e["box"], m["box"])


def test_the_long_form_fits_the_line_panels_tags_and_leaves_the_bars_panels_alone_T8d() -> None:
    page = _world(_mixed())["page"]
    LPG.apply_longform(page, "middle")
    assert [("tag_form" in p["axes"]) for p in page["panels"]] == [True, False, True, False]
    assert all(k["panel"] in (0, 2) for k in page["axes"].get("key") or [])


# ---- the player: a bars panel keeps the bars rules, and the range is drawn true -------------------------------------
BARS_READ = """() => { const s = document.getElementById('stage').getBoundingClientRect();
  const w = [...document.querySelectorAll('.world.ledger')].find((x) => x.__lp);
  const R = (e) => { const r = e.getBoundingClientRect(); return [r.x - s.x, r.y - s.y, r.width, r.height]; };
  const read = (S) => S.kind !== 'story' ? null : ({ axis: R(S.chart.querySelector('line.ax')),
    bars: S.bars.map((b) => ({ bar: R(b.bar), val: R(b.val), text: b.val.textContent, op: +(b.val.getAttribute('opacity') || 0),
                              band: b.band ? R(b.band) : null })) });
  return w.__lp.panels ? w.__lp.panels.map(read) : [read(w.__lp)]; }"""


def _read_bars(tmp_path, surface: str, times: list[float]) -> dict:
    import render_baseline as RB
    from playwright.sync_api import sync_playwright
    tl, uris, _t, aspect = RB.load_surface(surface)
    html = tmp_path / "p.html"
    html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
    srv, port = RB.serve(tmp_path)
    w, h = RB.STAGE[aspect]
    out = {}
    try:
        with sync_playwright() as pw:
            br = pw.chromium.launch(headless=True)
            pg = br.new_context(viewport={"width": w, "height": h}, device_scale_factor=1).new_page()
            pg.goto(f"http://127.0.0.1:{port}/{html.name}", wait_until="networkidle", timeout=120000)
            RB.prepare_page(pg, w, h)
            for x in times:
                RB.frame_png(pg, x, (w, h))
                out[x] = pg.evaluate(BARS_READ)
            br.close()
    finally:
        srv.shutdown()
    return out


def _bars_rules(panel: dict, texts: list[str]) -> None:
    base = panel["axis"][1] + panel["axis"][3] / 2
    assert [b["text"] for b in panel["bars"]] == texts, "each bar's value, written with its unit"
    for b in panel["bars"]:
        x, y, bw, bh = b["bar"]
        assert bw <= 196.5, ("E99 s96: a bar is at most Bravos's 196 px on the stage", bw)
        assert abs(y + bh - base) <= 1.5, ("the bar stands on the zero line", y + bh, base)
        top = b["band"][1] if b["band"] else y
        assert b["op"] >= 0.99 and b["val"][1] + b["val"][3] <= top + 1, ("the value is written over its bar", b["val"], top)
        assert abs((b["val"][0] + b["val"][2] / 2) - (x + bw / 2)) <= 1.5, "... centred on it"


@pytest.mark.skipif(not _chromium(), reason="playwright chromium not installed")
def test_a_bars_panel_keeps_the_bars_rules_at_home_and_grown_to_the_page_T8d(tmp_path) -> None:
    """The golden `panels-mixed-grow`: in the quad and once the wafer bars have grown over the page, every bar is at most
    196 px on the stage, stands on its zero line, and carries its value centred over it with its unit; the grown panel is
    the same chart LARGER (its bars wider apart, its words bigger), never its bars stretched."""
    reads = _read_bars(tmp_path, "panels-mixed-grow", [16.9, 19.5])
    home, grown = reads[16.9], reads[19.5]
    assert home[0] is None and home[2] is None, "the line panels are lines"
    for panel in (home[1], grown[1]):
        _bars_rules(panel, ["1x", "3x"])
    _bars_rules(home[3], ["+55\u201360%", "+60%", "+89%"])
    pitch = lambda p: p["bars"][1]["bar"][0] - p["bars"][0]["bar"][0]  # noqa: E731
    assert pitch(home[1]) <= pitch(grown[1]) <= 196 / 0.44 + 1, "the grown panel spreads its bars to the capped pitch (LPBAR)"
    assert grown[1]["bars"][0]["bar"][2] == pytest.approx(home[1]["bars"][0]["bar"][2], abs=1.5), "... at the SAME 196 px"
    assert grown[1]["bars"][0]["val"][3] > 1.6 * home[1]["bars"][0]["val"][3], "... and its words grow with it (T8b's grow)"


@pytest.mark.skipif(not _chromium(), reason="playwright chromium not installed")
def test_a_range_bar_stands_at_its_near_end_and_its_band_runs_to_the_far_one_in_true_proportion_T8d(tmp_path) -> None:
    """The golden `bars-range`: the bar is drawn to +55 and the band from there to +60 on the page's own scale (E99 s100:
    true proportion), the value "+55–60%" written over the band's far end - and while the bars grow the band rides its
    bar (the same zero, the same clock), so no frame draws a height the page does not print."""
    reads = _read_bars(tmp_path, "bars-range", [6.2, 9.0])
    (mid,), (done,) = reads[6.2], reads[9.0]
    _bars_rules(done, ["+55\u201360%", "+60%", "+89%"])
    base = done["axis"][1] + done["axis"][3] / 2
    rng, full = done["bars"][0], done["bars"][1]
    bar_top, band_top = rng["bar"][1], rng["band"][1]
    assert band_top < bar_top, "the band stands over its bar"
    assert (base - bar_top) / (base - band_top) == pytest.approx(55 / 60, abs=0.01), "lo : hi on the page's own scale"
    assert band_top == pytest.approx(full["bar"][1], abs=1.5), "the band's far end IS 60 - the +60% bar's own top"
    assert rng["band"][0] == pytest.approx(rng["bar"][0], abs=0.5) and rng["band"][2] == pytest.approx(rng["bar"][2], abs=0.5)
    m = mid["bars"][0]
    assert m["band"][1] < m["bar"][1] and (base - m["bar"][1]) / (base - m["band"][1]) == pytest.approx(55 / 60, abs=0.02), (
        "mid-build the band grows WITH its bar")


# ---- P69 T8e (1): THE ROW PATH - the compiler's own keys reach the validator ------------------------------------------
# Row 21 (T29) found it: `main()` writes `id` (P51 T5, `species_row_id`) on EVERY species - and `held` on one whose
# `dur` is "hold" - BEFORE `validate_species`, and `panel_focus`'s closed key list refused its `id`: every compiled
# `panel_focus` FAILed "unknown key(s) ['id']". The goldens and the tests above call `validate_species` with no ids, so
# they never saw it. These run the compiler's own `main()` on a one-row bed, as a door does, and stop it where the row's
# species have been validated and normalised (`derive_rescale_states`, which runs `check_panels`).
class _PastTheSpecies(Exception):
    """Raised once the row path has validated and normalised the row's species - the test needs nothing after."""


def _row_path(tmp_path, monkeypatch, species: list, series: Path = TWO_ERAS) -> list:
    import shutil
    ep, build = tmp_path / "ep", tmp_path / "ep" / "build"
    (ep / "evidence/objects").mkdir(parents=True)
    (build / "audio").mkdir(parents=True)
    shutil.copy2(series, ep / "evidence/objects" / "ev-row-path.series.json")
    (build / "audio/episode.mp3").write_bytes(b"")
    (build / "timeline.json").write_text(json.dumps({"runtime_s": 30.0, "words": []}), encoding="utf-8")
    (build / "caption-pages.json").write_text("[]", encoding="utf-8")
    row = (0.0, 30.0, "ledger:ev-row-path:line", (0, 0, 0), [], None, species)
    (ep / "SHOT-ROW-PATH.py").write_text("W = " + repr([row]) + "\n", encoding="utf-8")
    seen: dict = {}
    real = B.derive_rescale_states

    def stop(world, row_species, plate, ep_dir, **kw):
        real(world, row_species, plate, ep_dir, **kw)
        seen["species"] = row_species
        raise _PastTheSpecies

    for name, value in (("BUILD", build), ("EP", ep), ("SHOT_TABLE_FILE", "SHOT-ROW-PATH.py"), ("ASPECT", "16:9"),
                        ("derive_rescale_states", stop)):
        monkeypatch.setattr(B, name, value)
    with pytest.raises(_PastTheSpecies):
        B.main()
    return seen["species"]


def test_a_panel_focus_compiles_through_the_row_path_with_the_compilers_own_id_T8e(tmp_path, monkeypatch) -> None:
    """The Expected RED (row 21's blocker): SystemExit "panel_focus: unknown key(s) ['id']"."""
    sp = _row_path(tmp_path, monkeypatch, [
        {"kind": "panel_focus", "at": 0.0, "dur": 0.05, "layout": "row", "active": [0], "hidden": [1]},
        {"kind": "panel_focus", "at": 12.0, "dur": 1.2, "layout": "row", "active": [0, 1]}])
    focus = [e for e in sp if e["kind"] == "panel_focus"]
    assert [e["id"] for e in focus] == ["s01.species.0", "s01.species.1"], "the P51 T5 key rides every species"
    assert [e["roles"] for e in focus] == [["active", "hidden"], ["active", "active"]], "... normalised by check_panels"


def test_a_held_closed_key_species_compiles_through_the_row_path_T8e(tmp_path, monkeypatch) -> None:
    """The audit's second key: `dur: "hold"` makes the hold pass write `held` - a lit stretch (a closed key list) held
    until the next event on its row keeps the record, and the row compiles."""
    sp = _row_path(tmp_path, monkeypatch, [
        {"kind": "lit_stretch", "at": 12.0, "dur": "hold", "panel": 1, "from": 10, "to": 60},
        {"kind": "retitle", "at": 14.0, "dur": 1.0, "text": "the next event"}])
    light = next(e for e in sp if e["kind"] == "lit_stretch")
    assert light["held"] is True and light["dur"] == 2.0 and light["id"] == "s01.species.0"


@pytest.mark.parametrize("entry", [
    {"kind": "panel_focus", "at": 9.0, "dur": 1.0, "layout": "row", "active": [0]},
    {"kind": "lit_stretch", "at": 9.0, "dur": 1.0, "from": 10, "to": 60},
    {"kind": "freeze", "at": 9.0, "dur": 0.7, "target": {"kind": "datum", "index": 20}},
    {"kind": "member", "at": 9.0, "dur": 0.5, "tile": 0},
], ids=lambda e: e["kind"])
def test_no_closed_key_species_refuses_a_key_the_row_path_writes_T8e(entry) -> None:
    """Every species with a CLOSED key list, audited: the row path's own keys (`B.ROW_PATH_KEYS`) are never an
    unknown key. The other species validate their fields and ignore the rest; `leave_*` is written only on the
    page-bound species, which are open."""
    assert set(B.ROW_PATH_KEYS) == {"id", "held"}
    stamped = dict(entry, id="s01.species.0", held=True)
    errs = B._validate_entry(stamped)
    assert not [e for e in errs if "'id'" in e or "'held'" in e or "unknown key" in e], errs
    assert set(B.PAGE_BOUND_SPECIES).isdisjoint({"panel_focus", "lit_stretch", "freeze", "member"})


# ---- P69 T8e (4): THE KEY RAIL FOLLOWS THE FOCUSED PANEL ---------------------------------------------------------------
# Row 21 (T29): the page's one key rail ("SHARE PRICE / OPERATING PROFIT") stood over the wafer bars once they had grown
# over the line - a key for a chart that is not the one in focus. A key pill names a line of ONE panel (and every panel
# whose line shares its name and colour, E53 s8): it stands while such a panel is ACTIVE, and leaves with it on the
# focus's own clock; a bars panel keys nothing, so with only bars in focus the rail is empty.
def _row21_shape() -> dict:
    """Row 21's SHAPE (a line panel of two named lines, then two bars panels) - synthetic, not figures about the world."""
    xs = [2025.6 + i / 52 for i in range(52)]
    return {"title": "One line, then two bars", "sub": "Synthetic panels for the key rail; not figures about the world",
            "src": "Synthetic series", "yunit": "%", "independent": True,
            "xticks": [[2025.75, "Oct"], [2026.04, "Jan"], [2026.29, "Apr"], [2026.54, "Jul"]],
            "panels": [
                {"sub": "A line and its partner", "series": [
                    {"name": "SHARE PRICE", "label": "+548%", "color": "crimson",
                     "pts": [[round(x, 3), round(100 + 9 * i + (i // 30) * 12 * (i - 30), 1)] for i, x in enumerate(xs)]},
                    {"name": "OPERATING PROFIT", "label": "+230%", "color": "teal",
                     "pts": [[round(x, 3), round(100 + 4 * i, 1)] for i, x in enumerate(xs)]}]},
                {"sub": "Bars, one unit", "builder": LPG.PANEL_BARS, "unit": "x",
                 "bars": [{"label": "One", "value": 1, "color": "deemph"}, {"label": "Three", "value": 3, "color": "crimson"}]},
                {"sub": "Bars with a range", "builder": LPG.PANEL_BARS, "unit": "%",
                 "bars": [{"label": "Low", "value": ["+55", "60"], "color": "deemph"}, {"label": "High", "value": "+89", "color": "crimson"}]}]}


def _longform_panels(series: dict) -> dict:
    B.ASPECT = "16:9"
    return LPG.apply_longform(B.stamp_full_stage(LPG.build_spec(series, "line", None, "right")), "middle")


def _focus_states(n: int, states: list) -> list:
    out = []
    for at, dur, fs in states:
        e = dict(fs, kind="panel_focus", at=at, dur=dur)
        B.panel_focus_state(e, n, "test")
        out.append(e)
    return out


def _play_page(tmp_path, page: dict, species: list, times: list, read: str, camera: dict | None = None) -> dict:
    """One scene of `page` (0-40 s) with `species` (and a row `camera`), played forward through `times`: {t: read(t)}."""
    import measure_page_boxes as MP
    import render_baseline as RB
    from playwright.sync_api import sync_playwright
    tl = MP._timeline(page, "16:9")
    tl["runtime_s"] = 40.0
    sc = tl["scenes"][0]
    sc["span"], sc["species"] = [0.0, 40.0], species
    if camera is not None:
        sc["camera"] = camera
        tl["kinetics"] = dict(tl.get("kinetics") or {}, camera=True)
    uris = {"__audio__": MP._silence(), **B.longform_assets(tl)}
    html = tmp_path / "p.html"
    html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
    srv, port = RB.serve(tmp_path)
    w, h = RB.STAGE["16:9"]
    out = {}
    try:
        with sync_playwright() as pw:
            br = pw.chromium.launch(headless=True)
            pg = br.new_context(viewport={"width": w, "height": h}, device_scale_factor=1).new_page()
            pg.goto(f"http://127.0.0.1:{port}/{html.name}", wait_until="networkidle", timeout=120000)
            RB.prepare_page(pg, w, h)
            for x in times:
                RB.frame_png(pg, x, (w, h))
                out[x] = pg.evaluate(read, x)
            br.close()
    finally:
        srv.shutdown()
    return out


KEY_READ = """() => { const w = document.getElementById('wB');   /* the measured world (measure_page_boxes' READ_BOXES) */
  return [...w.querySelectorAll('.lp-kpill')].map((e) => [e.textContent, +getComputedStyle(e).opacity]); }"""
LINE_ALONE = {"layout": "row", "active": [0], "hidden": [1, 2]}
BARS_BESIDE = {"layout": "row", "active": [0, 1], "hidden": [2]}
BARS_GROWN = {"layout": "row", "active": [1], "hidden": [2]}
LINE_BACK = {"layout": "row", "active": [0], "hidden": [2]}


def test_the_row21_shape_keys_the_line_panel_only_T8e() -> None:
    page = _longform_panels(_row21_shape())
    assert [(k["panel"], k["name"]) for k in page["axes"]["key"]] == [(0, "SHARE PRICE"), (0, "OPERATING PROFIT")]


@pytest.mark.skipif(not _chromium(), reason="playwright chromium not installed")
def test_the_key_rail_follows_the_focused_panel_and_a_bars_panel_hides_it_T8e(tmp_path) -> None:
    """The line alone (its key landed), the bars BESIDE it (the line still active: its key stays), the bars GROWN over
    it (the line receded: the key has gone with it), the line back (its key back). Mid-move the key crossfades on the
    focus's own clock - it has let go by the move's end, never before its word."""
    fs = _focus_states(3, [(0.0, 0.05, LINE_ALONE), (22.0, 1.2, BARS_BESIDE), (23.2, 1.2, BARS_GROWN),
                           (30.0, 1.2, LINE_BACK)])
    got = _play_page(tmp_path, _longform_panels(_row21_shape()), fs, [21.5, 23.0, 23.5, 26.0, 32.0], KEY_READ)
    ink = {t: [op for _name, op in pills] for t, pills in got.items()}
    assert [name for name, _ in got[21.5]] == ["SHARE PRICE", "OPERATING PROFIT"]
    assert ink[21.5] == [1.0, 1.0], "the line alone: its key has landed"
    assert ink[23.0] == [1.0, 1.0], "the bars beside the line: the line is still in focus, and so is its key"
    assert all(0.0 < v < 1.0 for v in ink[23.5]) or all(v == 1.0 for v in ink[23.5]), ink[23.5]
    assert ink[26.0] == [0.0, 0.0], "the bars grown over the receded line: the line's key has gone with it"
    assert ink[32.0] == [1.0, 1.0], "the line back in focus: its key back"


@pytest.mark.skipif(not _chromium(), reason="playwright chromium not installed")
def test_a_key_shared_by_two_panels_stays_while_either_is_in_focus_and_no_focus_paints_the_key_as_before_T8e(tmp_path) -> None:
    """The two-era page keys its one name once, on panel 0 (E53 s8) - panel 1's line carries the same name, so the key
    stays when panel 1 alone is in focus. A page with no focus state paints its key exactly as before."""
    page = _longform_panels(_two_eras())
    assert [k["panel"] for k in page["axes"]["key"]] == [0]
    fs = _focus_states(2, [(20.0, 1.2, {"layout": "row", "active": [1]})])
    with_focus = _play_page(tmp_path, page, fs, [19.0, 25.0], KEY_READ)
    assert [op for _n, op in with_focus[25.0]] == [1.0], "panel 1 carries the keyed name: the key stays"
    plain = _play_page(tmp_path, page, [], [19.0, 25.0], KEY_READ)
    assert plain[25.0] == with_focus[19.0] == plain[19.0]


# ---- P69 T8e (2): the measurer, in the player ---------------------------------------------------------------------------
@pytest.mark.skipif(not _chromium(), reason="playwright chromium not installed")
def test_a_panels_page_is_measured_standing_in_its_first_focus_state_T8e() -> None:
    """Row 21's shape measured as it stands from its first frame - the line ALONE across the region, the two bars panels
    hidden: the plot is the line panel's (on the stage), the hidden panels are named hidden and give the plot nothing.
    Measured in its home layout (every panel side by side, a layout no frame draws) the same page's plot is the three."""
    import measure_page_boxes as MP
    page = _longform_panels(_row21_shape())
    (fs,) = _focus_states(3, [(0.0, 0.05, LINE_ALONE)])
    home, first = MP.measure(LPG.PANELS, "16:9", page), MP.measure(LPG.PANELS, "16:9", page, focus=fs)
    assert first[LPG.PANELS_KEY][1] == {"hidden": True} == first[LPG.PANELS_KEY][2]
    line = first[LPG.PANELS_KEY][0]
    assert first["boxes"]["plot"] == line["plot"], "the one shown panel IS the plot"
    p = first["boxes"]["plot"]
    assert p["x"] >= 0 and p["x"] + p["w"] <= 1920 and p["w"] <= line["box"]["w"] + 2, (p, line["box"])
    assert line["box"]["w"] > 1.5 * home[LPG.PANELS_KEY][0]["box"]["w"], "the line alone spans the region (T8c)"
    assert len(home[LPG.PANELS_KEY]) == 3 and all("box" in q for q in home[LPG.PANELS_KEY]), "no focus: every panel, as before"
    assert "1" in "".join(first["data_mask"]), first["data_mask"]
