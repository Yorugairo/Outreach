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

import contextlib
import json
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import build_scene_timeline_f as B  # noqa: E402
import ledger_page as LPG  # noqa: E402
import render_baseline as RB  # noqa: E402

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


# ---- the served player, for the claims a compile cannot make (P61 T4a/T4b) ------------------------
def _browser_ok() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _browser_ok(), reason="playwright chromium not installed")

FACE_SEL = {"shadow": ".bx-shadow", "side": ".bx-side", "cap": ".bx-cap"}
FACES_JS = """(sel) => {
  const g = (s) => [...document.querySelectorAll(s)].map((e) => e.getAttribute('transform') || '');
  const [sh, si, ca] = [g(sel.shadow), g(sel.side), g(sel.cap)];
  return ca.map((c, i) => ({ shadow: sh[i] || '', side: si[i] || '', cap: c }));
}"""


FIELD_JS = """() => {
  const f = document.querySelector('.lp-field'), fp = document.querySelector('.lp-fieldplate');
  const seeps = f ? [...f.querySelectorAll('svg > g > path')] : [];
  return { display: f ? (f.style.display || getComputedStyle(f).display) : 'absent',
           plate_opacity: fp ? (fp.style.opacity || '1') : 'absent',
           seeps: seeps.length,
           seeps_transformed: seeps.filter((e) => /rotate/.test(e.getAttribute('transform') || '')).length };
}"""


class _Player:
    """A golden SURFACE in a headless page, seekable - test_camera.py's `_Player`, scoped to what a form needs."""

    def __init__(self, surface: str):
        from playwright.sync_api import sync_playwright
        tl, uris, _t, aspect = RB.load_surface(surface)
        self.td = tempfile.TemporaryDirectory()
        html = Path(self.td.name) / f"{surface}.html"
        html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
        self.w, self.h = RB.STAGE[aspect]
        self.srv, port = RB.serve(html.parent)
        self.pw = sync_playwright().start()
        self.br = self.pw.chromium.launch(headless=True)
        self.page = self.br.new_context(viewport={"width": self.w, "height": self.h}).new_page()
        self.errs: list[str] = []
        self.page.on("pageerror", lambda e: self.errs.append(str(e)))
        self.page.goto("http://127.0.0.1:%d/%s" % (port, html.name), wait_until="networkidle", timeout=120000)
        RB.prepare_page(self.page, self.w, self.h)

    def seek(self, t: float) -> None:
        self.page.evaluate("t => { const s = document.getElementById('scrub'); s.value = t; s.dispatchEvent(new Event('input', {bubbles:true})); }", t)

    def field_state(self) -> dict:
        """P61 T4b: the page's GROUND at the instant now shown - is the procedural field standing, how opaque is
        the inked plate, and how many of the field's seeps carry a transform (i.e. are riding the drain)."""
        return self.page.evaluate(FIELD_JS)

    def faces(self) -> list[dict]:
        """One row per prism: the transform each of its three extruded faces carries at the instant now shown."""
        return self.page.evaluate(FACES_JS, FACE_SEL)

    def close(self) -> None:
        self.br.close(); self.pw.stop(); self.srv.shutdown(); self.td.cleanup()


@contextlib.contextmanager
def _player(surface: str):
    p = _Player(surface)
    try:
        yield p
        assert not p.errs, p.errs
    finally:
        p.close()


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


# ---- P61 T4a: the prism's LEAVE breaks down, face by face ----------------------------------------
def test_the_shed_is_declared_and_runs_after_the_drain_on_the_drain_s_own_clock() -> None:
    """E99 s4. The dials are named, the faces carry three of everything, and the slot is the LAST word of the frame."""
    src = ENGINE.read_text(encoding="utf-8")
    assert "const SHED = Object.freeze({" in src
    block = src.split("const SHED = Object.freeze({", 1)[1].split("});", 1)[0]
    # one entry per face, and no two pieces of a prism share a depth in the drain, a spin or a bearing
    for dial in ("LEAD", "SPIN", "DRIFT"):
        assert f"{dial}: [" in block, f"the shed's {dial} dial is not declared"
        vals = [float(v) for v in block.split(f"{dial}: [", 1)[1].split("]", 1)[0].split(",")]
        assert len(vals) == 3 and len(set(vals)) == 3, (dial, vals)
    # the shed rides the vortex's OWN map and clock - no second geometry, no second state
    assert "const q = lpVortex(h[0], h[1], P.cChart, P.Rchart, uj);" in src
    assert "const { uc } = spiralClocks(t, a, z, pg.exit, pg.enter);" in src
    # ... and is called AFTER it, so the drain's particle cache is always measured with the faces at home
    assert src.index("lpShedPrisms(st, scene, t, pg);") > src.index("lpSpiral(st, scene, t, pg);   /* the retract")


@needs_browser
def test_each_prism_s_faces_go_their_own_way_at_the_leave() -> None:
    """The acceptance, measured: at `form-extruded-bar@proof-leave`'s own instant no two faces of one prism carry
    the same transform (the block no longer travels as one body), and the whole thing is a pure function of t -
    seeking away and back lands on the same strings, which is what makes the golden reachable by a seek."""
    t_leave = RB.PROOF_FRAMES["form-extruded-bar@proof-leave"][2]
    faces = {}
    with _player("form-extruded-bar") as p:
        p.seek(t_leave)
        faces["leave"] = p.faces()
        p.seek(6.0)
        faces["build"] = p.faces()
        p.seek(t_leave)
        faces["again"] = p.faces()
    L = faces["leave"]
    assert len(L) >= 4, L                                    # the four values the flat `thread-baseline` draws
    for i, f in enumerate(L):
        assert all(f[k] for k in ("shadow", "side", "cap")), (i, f)          # every face is IN the drain
        assert len({f["shadow"], f["side"], f["cap"]}) == 3, (i, f)          # ... and no two of them ride it the same way
    assert faces["again"] == L                               # a pure function of t: the second seek is the first
    assert all(not any(f.values()) for f in faces["build"])   # and the shed writes nothing while the drain is shut


# ---- P61 T4b: the FIELD is named on the row, and every field leaves by the soak's recede ----------
# E99 s35: *"I think they should both be first class effects. When we are trying to maintain continuity,
# connecting ideas, speaking across plates i think the cross-fade is the answer, when we are building an idea or
# introducing a new idea or looking to fill space to separate ideas, the soak is the transition."* - so the ground
# is authored by the sentence's JOB, never by the page's form, and the scribble is the opt-in back-up.
def test_the_field_is_named_on_the_row_and_the_soak_is_the_default(ep: Path) -> None:
    assert B.PAGE_FIELDS == ("soak", "plates", "scribble")
    # a page that names NO field carries no key: the engine's own default IS the soak, so the timeline is unmoved
    assert "field" not in world(ep, BARS_PAGE)["page"]
    assert world(ep, f"{BARS_PAGE};field=soak")["page"]["field"] == "soak"
    assert world(ep, f"{BARS_PAGE};field=scribble")["page"]["field"] == "scribble"   # the back-up, passed through
    # ... and naming it changes NOTHING else about the page
    named = dict(world(ep, f"{BARS_PAGE};field=soak")["page"]); named.pop("field")
    assert named == world(ep, BARS_PAGE)["page"]


def test_the_cross_fade_is_refused_by_name_when_the_page_has_no_plates(ep: Path) -> None:
    msg = refusal(ep, f"{BARS_PAGE};field=plates")
    assert "field=plates is the TWO-PLATE CROSS-FADE" in msg
    for pid in B.PAGE_FIELD_PLATES:                      # the refusal NAMES the two ids the record uses
        assert pid in msg
    assert "field=soak" in msg                            # ... and says what to do instead
    # the same page WITH the two plates takes it (the grammar asks; the build that owns the assets provides them)
    page = dict(world(ep, BARS_PAGE)["page"], plate=B.PAGE_FIELD_PLATES[0], field_plate=B.PAGE_FIELD_PLATES[1])
    assert B.page_field_spec("plates", page, "r") == "plates"
    assert B.page_field_spec("plates", None, "r") == "plates"   # the ROW's grammar is checked without a page


def test_an_unknown_field_is_refused_by_name(ep: Path) -> None:
    assert "field='bogus' is not one of soak|plates|scribble" in refusal(ep, f"{BARS_PAGE};field=bogus")


def test_field_is_a_page_option_not_a_plate_one(ep: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(B, "_world_for_bare_plate",
                        lambda *a, **k: {"asset_id": "plate-x", "sha256": "0" * 64,
                                         "ken_burns": {"scale": 0, "x": 0, "y": 0}})
    assert "field= is a LEDGER PAGE option" in refusal(ep, "plate-x;field=soak")


def test_the_two_form_goldens_carry_the_two_first_class_fields() -> None:
    """The operator's division, pinned on the two surfaces he reads: the bar page INTRODUCES four values (soak),
    the line page SPEAKS ACROSS the flat page of the same series (the cross-fade). Neither is the scribble."""
    bars = json.loads((RB.SOURCES / "form-extruded-bar.timeline.json").read_text(encoding="utf-8"))
    line = json.loads((RB.SOURCES / "form-tilted-line.timeline.json").read_text(encoding="utf-8"))
    bp, lp = bars["scenes"][0]["world"]["page"], line["scenes"][0]["world"]["page"]
    assert bp["field"] == "soak" and "plate" not in bp
    assert lp.get("field") is None and lp["plate"] and lp["field_plate"] and lp["board"]
    line_uris = json.loads((RB.SOURCES / "form-tilted-line.uris.json").read_text(encoding="utf-8"))
    for pid in (lp["plate"], lp["field_plate"]):
        assert line_uris.get(pid, "").startswith("data:image/"), pid


def test_the_recede_is_one_mechanism_on_the_drains_own_clock() -> None:
    src = ENGINE.read_text(encoding="utf-8")
    assert "const lpPlateRecede = (st, scene, t, pg) => {" in src
    assert "if (!st.fieldPlate || !st.field) return;" in src                 # a page with no inked plate takes none of it
    assert 'st.field.style.display = (uc > 0 || uf > 0) ? "" : "none";' in src   # ... and nothing is written while the drain is shut
    # it runs BEFORE the drain, which measures the field's box the first frame it is on
    assert src.index("lpPlateRecede(st, scene, t, pg);") < src.index("lpSpiral(st, scene, t, pg);   /* the retract")


@needs_browser
def test_a_cross_fade_page_leaves_by_the_soaks_recede() -> None:
    """The acceptance, measured (E99 s35: *"the leave-soak is much better than the two plate leave"*): at the
    recede instant the inked plate has gone AND the seeps stand in its place, each carrying a vortex transform -
    not a page that faded to cream. And a held page shows none of it: the field is hidden until the drain opens."""
    t_recede = RB.PROOF_FRAMES["form-tilted-line@proof-recede"][2]
    with _player("form-tilted-line") as p:
        p.seek(9.0)
        held = p.field_state()
        p.seek(t_recede)
        gone = p.field_state()
        p.seek(9.0)
        again = p.field_state()
    assert held["display"] == "none" and float(held["plate_opacity"]) > 0.99   # the plate IS the ground while it holds
    assert held["seeps_transformed"] == 0
    assert gone["display"] != "none"                                          # the field stands in the drain
    assert float(gone["plate_opacity"]) < 0.01                                # the inked plate has gone
    assert gone["seeps"] >= 6 and gone["seeps_transformed"] == gone["seeps"]   # every seep is riding the vortex
    assert again == held                                                      # a pure function of t


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
