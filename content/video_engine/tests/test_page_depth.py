"""P58 T4: THE LEDGER PAGE AS A CARD AT A DEPTH - the grammar, every refusal by name, and the flat page unmoved.

E98 s3: *"the ledger page is a card at a depth ... the flat page stays the default reading form"*. A page row may
carry two new options and nothing else - `;depth=<k>` (the share of the ONE camera's move the page takes, the
parallax factor kinetics/camera.mjs already implements) and `;plane=tilt:<deg>[,<axis>]|quad:<8 numbers>` (the
surface it is drawn on, four corners in the same TL TR BR BL stage fractions the ART-embed grammar authors, and
projected by the SAME homography). Both are opt-in. The first test here is the one that matters most: a page that
names neither compiles to the byte-identical world it compiled to before this slice existed - which is also what
the untouched goldens say (`test_golden_frames.py`).

The refusals are the slice's real surface, so each one is asserted BY NAME with the fix in the message:
  - `depth` outside the camera's own range, or not a number at all
  - `plane` that is neither form, an unknown tilt axis, a tilt past the edge-on limit
  - a tilt whose projected page is narrower than EMBED_MIN_W of the stage - the SAME "cannot be read on a phone"
    floor the embed grammar refuses a too-small surface with (one law, not two)
  - a quad that is not a quad (off the stage, wound the wrong way) - `embed_quad_error`'s own law
  - either option on a PLATE: a plate declares its depth planes in its own sidecar (P58 T2), never on a row
  - `throw=depth` and a real `depth=` on one page: two names for one thing (P58 open decision 6)
  - B1, unchanged: a chart never lands on a plate's painted surface
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import build_scene_timeline_f as B  # noqa: E402

EP = ROOT / "content/video_engine/projects/systems-and-blowups/steel-and-paper"
SERIES_ID = "ev-divergence-v1"
PAGE = f"ledger:{SERIES_ID}:line"
KEN = (0, 0, 0)

needs_series = pytest.mark.skipif(not (EP / f"evidence/objects/{SERIES_ID}.series.json").exists(),
                                  reason="the steel-and-paper evidence objects are not on disk")


def world(plate_id: str) -> dict:
    return B.world_for_plate(plate_id, KEN, EP)


def refusal(plate_id: str) -> str:
    with pytest.raises(ValueError) as exc:
        world(plate_id)
    return str(exc.value)


# ---- the flat page is the default, and it did not move -------------------------------------------
@needs_series
def test_a_page_that_names_neither_option_is_byte_identical() -> None:
    w = world(PAGE)
    assert "depth" not in w["page"] and "plane" not in w["page"]
    assert w == world(PAGE)                      # the compile is a pure function of the row
    assert w["page"] == world(f"{PAGE};idle=breath")["page"]   # another option changes the page not at all
    assert world(f"{PAGE};idle=breath")["idle"] == "breath"    # ... it rides the world, as it always did


def test_the_flat_page_is_the_plane_at_zero_degrees() -> None:
    assert B.page_plane_quad(0, "y") == [[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]]
    assert B.page_plane_quad(0, "x") == [[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]]


# ---- the grammar ---------------------------------------------------------------------------------
@needs_series
def test_depth_lands_on_the_page_as_the_cameras_own_factor() -> None:
    assert world(f"{PAGE};depth=1.15")["page"]["depth"] == 1.15
    assert world(f"{PAGE};depth=0")["page"]["depth"] == 0.0        # pinned to the frame: the range's floor is a value, not a refusal
    assert world(f"{PAGE};depth=4")["page"]["depth"] == 4.0


@needs_series
def test_a_tilt_resolves_four_corners_in_tl_tr_br_bl_order() -> None:
    plane = world(f"{PAGE};plane=tilt:14,y")["page"]["plane"]
    assert plane["kind"] == "tilt" and plane["deg"] == 14.0 and plane["axis"] == "y"
    tl, tr, br, bl = plane["quad"]
    assert tl[0] < tr[0] and bl[0] < br[0]                          # TL TR BR BL, the way an embed quad is read
    assert (br[1] - tr[1]) < (bl[1] - tl[1])                        # turned about its VERTICAL axis: the far (right) edge is the shorter one - the ruled lines converge to the right
    assert B.page_plane_quad(-14, "y")[0][0] > B.page_plane_quad(14, "y")[0][0]   # the other way round, the near edge is on the right


@needs_series
def test_a_tilt_about_x_lies_the_page_back() -> None:
    quad = world(f"{PAGE};plane=tilt:20,x")["page"]["plane"]["quad"]
    tl, tr, br, bl = quad
    assert (br[0] - bl[0]) < (tr[0] - tl[0])                        # a positive tilt about the HORIZONTAL axis lays the page's foot away: the bottom edge is the far, shorter one
    assert (br[0] - bl[0]) == pytest.approx(B.page_plane_quad(20, "x")[2][0] - B.page_plane_quad(20, "x")[3][0])


@needs_series
def test_a_quad_takes_the_corners_the_embed_grammar_takes() -> None:
    plane = world(f"{PAGE};plane=quad:0.08,0.06,0.9,0.14,0.9,0.86,0.08,0.94")["page"]["plane"]
    assert plane == {"kind": "quad", "quad": [[0.08, 0.06], [0.9, 0.14], [0.9, 0.86], [0.08, 0.94]]}


@needs_series
def test_both_options_ride_one_page_together() -> None:
    page = world(f"{PAGE};plane=tilt:14,y;depth=1.15;card=yes")["page"]
    assert page["depth"] == 1.15 and page["plane"]["kind"] == "tilt" and page["card"] is True


# ---- every refusal, by name ----------------------------------------------------------------------
@needs_series
def test_a_depth_outside_the_cameras_range_is_refused_by_name() -> None:
    msg = refusal(f"{PAGE};depth=5")
    assert "depth 5 is outside 0..4" in msg and "PARALLAX" in msg
    assert "not a number" in refusal(f"{PAGE};depth=near")


@needs_series
def test_a_plane_that_is_neither_form_is_refused_by_name() -> None:
    msg = refusal(f"{PAGE};plane=lean:14")
    assert "is not tilt:<deg>[,<axis>] or quad:" in msg
    assert "is not one of y|x" in refusal(f"{PAGE};plane=tilt:14,z")
    assert "is not a number of degrees" in refusal(f"{PAGE};plane=tilt:sideways")
    assert "past the 89 deg limit" in refusal(f"{PAGE};plane=tilt:95,y")
    assert "is not eight numbers" in refusal(f"{PAGE};plane=quad:0.1,0.1,0.9,0.1")


@needs_series
def test_a_tilt_that_cannot_be_read_on_a_phone_is_refused_with_the_embed_grammars_own_message() -> None:
    msg = refusal(f"{PAGE};plane=tilt:80,y")
    assert "cannot be read on a phone" in msg and f"under the {B.EMBED_MIN_W:.0%} floor" in msg
    assert "the page's plane (plane=tilt:80,y)" in msg


def test_the_floor_is_the_embed_grammars_floor_and_it_bites_where_the_page_stops_reading() -> None:
    def width(deg: float) -> float:
        q = B.page_plane_quad(deg, "y")
        return ((q[1][0] - q[0][0]) + (q[2][0] - q[3][0])) / 2
    assert width(0) == pytest.approx(1.0)
    assert width(14) > B.EMBED_MIN_W > width(80)
    assert width(14) > width(40) > width(60)                        # the further it turns, the narrower it reads


@needs_series
def test_a_quad_that_is_not_a_quad_is_refused_by_the_embed_grammars_own_law() -> None:
    assert "corner off the stage" in refusal(f"{PAGE};plane=quad:-0.1,0,0.9,0.1,0.9,0.9,0.1,1")
    assert "not a convex quad" in refusal(f"{PAGE};plane=quad:0.1,0.1,0.9,0.9,0.9,0.1,0.1,0.9")


def test_either_option_on_a_plate_is_refused_by_name(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(B, "_world_for_bare_plate",
                        lambda *a, **k: {"asset_id": "plate-x", "sha256": "0" * 64,
                                         "ken_burns": {"scale": 0, "x": 0, "y": 0}})
    for opt in ("depth=1.2", "plane=tilt:14,y"):
        msg = refusal(f"plate-x;{opt}")
        assert "is a LEDGER PAGE option" in msg and "<plate>.layers.json" in msg


@needs_series
def test_the_growth_illusion_and_a_real_depth_are_refused_together() -> None:
    thrown = f"ledger:{SERIES_ID}:line:0:right:throw=depth"
    assert world(thrown)["page"]["throw_grow"] == "depth"           # the illusion is untouched: P58 keeps both names
    assert world(f"ledger:{SERIES_ID}:line:0:right:throw=snap;depth=1.15")["page"]["depth"] == 1.15
    msg = refusal(f"{thrown};depth=1.15")
    assert "two names for one thing" in msg and "throw=snap" in msg


def test_a_chart_still_never_lands_on_a_plates_surface() -> None:
    # B1, unchanged by this slice: the page is a card at a depth in OUR space, never a card on THEIR wall.
    assert B.EMBED_REFUSED_SPECIES == ("chart",)
    msg = B.embed_error({"asset_id": "plate-x"}, {"poster": {}}, "poster", "s01", species="chart")
    assert "the argument's own charts never embed" in msg
    msg = B.embed_error({"kind": B.SPECIES_LEDGER, "page": {}}, {"poster": {}}, "poster", "s01")
    assert "a chart page never embeds" in msg


# ---- what the player is handed -------------------------------------------------------------------
@needs_series
def test_the_planes_quad_is_the_only_geometry_the_timeline_carries() -> None:
    """The compiler owns the tilt's geometry (as it owns the role -> k table); the player consumes a quad, so
    kinetics/homography.mjs keeps ONE projective path and the engine has no second one to drift from."""
    plane = world(f"{PAGE};plane=tilt:14,y")["page"]["plane"]
    assert set(plane) == {"kind", "deg", "axis", "quad"}
    assert all(0.0 <= v <= 1.0 for p in plane["quad"] for v in p)
    assert B.page_plane_error(plane, "s01") is None
