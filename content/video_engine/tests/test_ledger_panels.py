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
    if surface == "panels-resize" and shots[1] != shots[0]:
        # the page's rule NAMES crossfade to the panel coming into focus (T8b's `panel_rule_home`): a translucent haloed
        # <text> over the bloomed line, whose raster Chromium may round one level apart after play (the attributes are
        # identical - read on the probe). T8b's engine paints this very surface 2 levels apart; the pose law is exact.
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
