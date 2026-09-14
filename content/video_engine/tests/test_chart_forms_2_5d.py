"""P58 T5: THE TWO CHART FORMS IN 2.5D - the grammar, every refusal by name, and the flat page unmoved.

E98 s3: *"bars with extrusion, a line on a tilted plane - the flat page stays the default"*. A page row may carry
ONE new option - `;form=extruded_bar` or `;form=tilted_line[:<deg>]` - and nothing else. A form is how the page's
marks are DRAWN, never what the page says: the spec, the scale, the value capsule, the axis rule and every label
stay the flat page's, which is why the first test here is the one that matters most - a page that names no form
compiles to the byte-identical world it compiled to before this slice existed, and the untouched goldens
(`test_golden_frames.py`) say the same about its pixels.

The refusals are the slice's real surface, so each is asserted BY NAME with the fix in the message:
  - a form no builder here draws (`form=bogus`)
  - a form THIS page's builder cannot draw - a prism on a line page, a tilted plane on a bars page. The rule is
    `ledger_page.form_error`'s, so the compiler and an object file that names a form are held to ONE rule
  - a setting on the form that has none (`form=extruded_bar:3` - its depth and its light are engine dials)
  - a tilt that is not a number, and a tilt past the edge-on limit
  - a tilt whose projected plane is narrower than EMBED_MIN_W of the stage: the SAME "cannot be read on a phone"
    floor `plane=` is refused by (P58 T4) - one law and one floor, not two
  - `form=` on a PLATE row: a plate is a picture and declares its own planes in its sidecar (P58 T2)
  - `form=` beside `plane=`: one plane per page (T4's option turns the whole page; a form draws the chart on its
    own plane)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import build_scene_timeline_f as B  # noqa: E402
import ledger_page as LPG  # noqa: E402

ENGINE = ROOT / "docs/content-video-engine/samples/scene-evidence-engine.mjs"
FRAMES = ROOT / "content/video_engine/tests/golden/frames"
KEN = (0, 0, 0)
BARS_ID, LINE_ID = "t5-bars", "t5-line"
BARS_PAGE, LINE_PAGE = f"ledger:{BARS_ID}:bars", f"ledger:{LINE_ID}:line"
BARS_OBJ = {
    "title": "Where the four lines end", "sub": "index at the last point", "src": "golden fixture", "unit": "",
    "bars": [{"label": "Memory", "value": 712.5, "color": "crimson"}, {"label": "Chips", "value": 204.6, "color": "teal"},
             {"label": "Mega-cap", "value": 120.8, "color": "cobalt"}, {"label": "S&P 500", "value": -21.5}],
}
LINE_OBJ = {
    "title": "Four lines", "sub": "index, 100 = Aug '25", "src": "golden fixture", "unit": "",
    "series": [{"name": "A", "color": "teal", "pts": [[2025.0 + i / 12, 100 + i * 3] for i in range(24)]},
               {"name": "B", "color": "crimson", "pts": [[2025.0 + i / 12, 100 - i] for i in range(24)]}],
}


@pytest.fixture(scope="module")
def ep(tmp_path_factory) -> Path:
    """A one-episode fixture holding both objects, so neither test depends on an episode on disk."""
    d = tmp_path_factory.mktemp("t5-ep")
    (d / "evidence/objects").mkdir(parents=True)
    (d / f"evidence/objects/{BARS_ID}.series.json").write_text(json.dumps(BARS_OBJ), encoding="utf-8")
    (d / f"evidence/objects/{LINE_ID}.series.json").write_text(json.dumps(LINE_OBJ), encoding="utf-8")
    return d


def world(ep: Path, plate_id: str) -> dict:
    return B.world_for_plate(plate_id, KEN, ep)


def refusal(ep: Path, plate_id: str) -> str:
    with pytest.raises(ValueError) as exc:
        world(ep, plate_id)
    return str(exc.value)


# ---- the flat page is the default, and it did not move -------------------------------------------
def test_a_page_that_names_no_form_is_byte_identical(ep: Path) -> None:
    for page_id in (BARS_PAGE, LINE_PAGE):
        w = world(ep, page_id)
        assert "form" not in w["page"]
        assert w == world(ep, page_id)                                   # the compile is a pure function of the row
        assert w["page"] == world(ep, f"{page_id};idle=breath")["page"]   # another option changes the page not at all


def test_the_two_builders_are_the_ones_the_forms_name(ep: Path) -> None:
    assert world(ep, BARS_PAGE)["page"]["builder"] == "story"        # LPG.FORM_BUILDERS["extruded_bar"]
    assert world(ep, LINE_PAGE)["page"]["builder"] == "dense-line"   # LPG.FORM_BUILDERS["tilted_line"]


# ---- the grammar ---------------------------------------------------------------------------------
def test_extruded_bar_is_the_whole_option(ep: Path) -> None:
    page = world(ep, f"{BARS_PAGE};form=extruded_bar")["page"]
    assert page["form"] == {"kind": "extruded_bar"}                  # no geometry: its depth and its light are engine dials
    assert page["values"] == world(ep, BARS_PAGE)["page"]["values"]   # and the page it is drawn from is untouched


def test_tilted_line_carries_the_plane_the_compiler_resolved(ep: Path) -> None:
    form = world(ep, f"{LINE_PAGE};form=tilted_line")["page"]["form"]
    assert form["kind"] == "tilted_line" and form["deg"] == LPG.TILT_DEG and form["axis"] == "y"
    assert len(form["quad"]) == 4 and all(len(c) == 2 for c in form["quad"])
    assert all(0.0 <= v <= 1.0 for c in form["quad"] for v in c)      # fractions of the page's own box, as every embed quad is
    # the plane turns about the page's VERTICAL axis: the far (right) edge is the shorter one
    (tlx, tly), (trx, try_), (brx, bry), (blx, bly) = form["quad"]
    assert (bry - try_) < (bly - tly)


def test_a_tilt_may_be_named_on_the_row(ep: Path) -> None:
    form = world(ep, f"{LINE_PAGE};form=tilted_line:30")["page"]["form"]
    assert form["deg"] == 30.0
    assert form["quad"] != world(ep, f"{LINE_PAGE};form=tilted_line")["page"]["form"]["quad"]


def test_at_zero_degrees_the_plane_is_the_page_itself() -> None:
    quad = B.page_form_geom("tilted_line:0", "t")["quad"]
    assert quad == [[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]]   # the identity: a plane that is not tilted changes no pixel


# ---- the refusals, by name -----------------------------------------------------------------------
def test_an_unknown_form_is_refused_by_name(ep: Path) -> None:
    msg = refusal(ep, f"{BARS_PAGE};form=bogus")
    assert "form 'bogus' is not one of extruded_bar|tilted_line" in msg


def test_a_form_this_builder_cannot_draw_is_refused_by_name(ep: Path) -> None:
    prism_on_a_line = refusal(ep, f"{LINE_PAGE};form=extruded_bar")
    assert "form=extruded_bar is a BARS page" in prism_on_a_line and "'dense-line'" in prism_on_a_line
    tilt_on_bars = refusal(ep, f"{BARS_PAGE};form=tilted_line")
    assert "form=tilted_line is a LINE page" in tilt_on_bars and "'story'" in tilt_on_bars


def test_the_prism_takes_no_setting(ep: Path) -> None:
    assert "takes no setting" in refusal(ep, f"{BARS_PAGE};form=extruded_bar:3")


def test_a_tilt_that_is_not_a_number_or_is_edge_on_is_refused(ep: Path) -> None:
    assert "is not a number of degrees" in refusal(ep, f"{LINE_PAGE};form=tilted_line:x")
    past = refusal(ep, f"{LINE_PAGE};form=tilted_line:95")
    assert "past the 89 deg limit" in past and "edge-on" in past


def test_a_plane_too_narrow_to_read_is_refused_by_the_embed_floor(ep: Path) -> None:
    msg = refusal(ep, f"{LINE_PAGE};form=tilted_line:88")
    assert "cannot be read on a phone" in msg and "the line's plane" in msg   # P58 T4's own floor, one law


def test_form_is_a_page_option_not_a_plate_one(ep: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(B, "_world_for_bare_plate",
                        lambda *a, **k: {"asset_id": "plate-x", "sha256": "0" * 64,
                                         "ken_burns": {"scale": 0, "x": 0, "y": 0}})
    msg = refusal(ep, "plate-x;form=extruded_bar")
    assert "form= is a LEDGER PAGE option" in msg and "<plate>.layers.json" in msg


def test_one_plane_per_page(ep: Path) -> None:
    for spec in ("form=tilted_line", "form=extruded_bar"):
        msg = refusal(ep, f"{LINE_PAGE if 'tilted' in spec else BARS_PAGE};plane=tilt:10,y;{spec}")
        assert "two surfaces - ONE plane per page" in msg


# ---- one rule, read twice: the compiler's row and an object that names a form ---------------------
def test_the_object_that_names_a_form_is_held_to_the_same_rule() -> None:
    assert LPG.form_error("extruded_bar", "story", "r") is None
    assert LPG.validate(dict(BARS_OBJ, form="extruded_bar"), "bars") == []
    errs = LPG.validate(dict(BARS_OBJ, form="tilted_line"), "bars")
    assert any("form=tilted_line is a LINE page" in e for e in errs)


# ---- the painters: what the engine does, and what it must not do ----------------------------------
def test_the_engine_dials_are_named_and_the_forms_are_gated() -> None:
    src = ENGINE.read_text(encoding="utf-8")
    for dial in ("LIGHT_DEG", "D_PX", "D_SHARE", "CLEAR_PX", "CAP_LIGHT", "SIDE_LIGHT", "SHADOW_A", "SHADOW_K"):
        assert f"{dial}:" in src, f"the extrusion's {dial} dial is not declared"
    assert 'formOf(pg, "extruded_bar")' in src and 'formOf(pg, "tilted_line")' in src   # both opt-in, off the page's own key
    assert "const tiltProject = (quad, box)" in src and "planeMatrix(quad.map(" in src  # ONE projective path (kinetics/homography.mjs)
    # the prism is built BEFORE the face, so SVG paint order puts it behind - which is what keeps every label still
    assert src.index("extrudeFaces(st, { x, bw, base, h, neg, P") < src.index('const bar = lpEl("rect", "bar" + (neg ? " neg" : " pos") + (i === st.emph')


def test_a_negative_bar_extrudes_the_way_its_value_goes() -> None:
    """E28/E53: sign is geometry. The depth vector's y is mirrored with the bar, so no extruded ink crosses zero."""
    src = ENGINE.read_text(encoding="utf-8")
    assert "return [D * Math.sin(th), (neg ? 1 : -1) * D * Math.cos(th)];" in src


# ---- the goldens (human gate 3 reads a pair) ------------------------------------------------------
def test_each_form_has_its_three_frames_beside_a_flat_golden_of_the_same_data() -> None:
    sys.path.insert(0, str(ROOT / "content/video_engine/tests/golden"))
    import render_baseline as RB
    from build_golden_sources import FRAME_T, SURFACES
    for name, flat in (("form-extruded-bar", "thread-baseline"), ("form-tilted-line", "ledger-page-mid-build")):
        assert name in SURFACES and name in FRAME_T
        assert (FRAMES / f"{name}.png").exists()
        for phase in ("build", "leave"):
            assert f"{name}@proof-{phase}" in RB.PROOF_FRAMES
            assert (FRAMES / f"{name}@proof-{phase}.png").exists()
        assert (FRAMES / f"{flat}.png").exists(), "the flat page of the same data is the pair the operator reads"
