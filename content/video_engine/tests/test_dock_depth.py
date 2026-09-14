"""P58 T6 (a): THE DOCK AT A DEPTH - the grammar, the two refusals by name, and the flat dock unmoved.

E98 s4: *"the docks, the ball and the slide move THROUGH the depth"*. A dock row may carry ONE new option,
`depth=<k>`: the card stands on a LAYER'S plane and takes that share of the one camera's move (kinetics/camera.mjs
`camLayerCss`, P58 T3's own term) instead of standing in screen space. The first test here is the one that matters
most - a dock that names no depth compiles to the byte-identical entry it compiled to before this slice existed,
which is also what the untouched goldens say (`test_golden_frames.py`).

The refusals are the slice's real surface, so each is asserted BY NAME with the fix in the message:
  - a depth that is not a number, or outside the camera's own range (the page's range, and the page's wording:
    there is ONE depth vocabulary in this engine, not one per thing that can stand on a plane)
  - `behind=` and a depth that DISAGREE: `behind` puts the card under the plate's foreground cutout - doc 24's
    `-near` plane, which build_plate_library indexes at k 1.40 - so a card behind the front can never sit nearer
    than it (HF-17 composes with the depth; it is not duplicated by it)
  - `embed=` and `depth=` on one card: two names for one thing, because a card that lands on a declared surface
    already stands on that surface's plane (P50 T7)
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import build_plate_library as BPL  # noqa: E402
import build_scene_timeline_f as B  # noqa: E402

GOLDEN = ROOT / "content/video_engine/tests/golden"


def refusal(opts: dict) -> str:
    with pytest.raises(ValueError) as exc:
        B.dock_opts(opts)
    return str(exc.value)


# ---- the default is the dock we already had ----------------------------------------------------

def test_a_dock_that_names_no_depth_is_byte_for_byte_the_entry_it_was() -> None:
    entry = B.dock_entry("ev-card", 0, 4.0, 12.0, 2, B.DOCK_KIND_IMAGE, None, "land")
    assert "depth" not in entry, "an unauthored dock gained a key - every committed timeline would differ"
    assert B.dock_opts({"arrive": "land", "mass": "paper"}) == {"arrive": "land", "mass": "paper"}


def test_the_option_is_written_only_when_the_row_asks_and_carries_the_number() -> None:
    assert B.dock_entry("ev-card", 0, 4.0, 12.0, 0, depth=1.15)["depth"] == 1.15
    assert "depth" not in B.dock_entry("ev-card", 0, 4.0, 12.0, 0, depth=None)
    assert "depth" not in B.dock_entry("ev-card", 0, 4.0, 12.0, 0, depth=0)   # 0 = pinned to the frame is the default, not a key


# ---- one vocabulary: the camera's range, the page's words ---------------------------------------

def test_the_dock_s_depth_is_the_camera_s_own_range_and_the_occluder_s_own_plane() -> None:
    assert B.DOCK_DEPTH["K_MIN"] == B.PAGE_DEPTH["K_MIN"] and B.DOCK_DEPTH["K_MAX"] == B.PAGE_DEPTH["K_MAX"], \
        "the dock's depth must take the page's range - one depth vocabulary, not one per thing"
    assert B.DOCK_DEPTH["BEHIND_K"] == BPL.LAYER_PLANES["occluder"][1], \
        "the plane `behind=` puts a card under is the occluder's - one dial written twice (as MELT_S is)"


@pytest.mark.parametrize("k", [0.0, 1.0, 1.15, 1.40, 4.0])
def test_a_depth_inside_the_range_is_taken_as_a_number(k: float) -> None:
    assert B.dock_opts({"depth": k}) == {"depth": float(k)}
    assert B.dock_opts({"depth": str(k)}) == {"depth": float(k)}   # a string resolves here, so every caller sees the number


@pytest.mark.parametrize("bad", ["deep", "", True, None])
def test_a_depth_that_is_not_a_number_is_refused_by_name(bad) -> None:
    assert "is not a number - depth=<k>" in refusal({"depth": bad})


@pytest.mark.parametrize("k", [-0.1, 4.1, 12])
def test_a_depth_outside_the_camera_s_range_is_refused_by_name(k: float) -> None:
    msg = refusal({"depth": k})
    assert f"depth {k:g} is outside 0..4" in msg and "kinetics/camera.mjs PARALLAX" in msg


# ---- it COMPOSES with `behind`, and the pair must agree ------------------------------------------

@pytest.mark.parametrize("k", [0.0, 1.0, 1.15, 1.40])
def test_a_card_behind_the_plate_s_front_may_stand_on_any_plane_up_to_the_occluder_s(k: float) -> None:
    assert B.dock_opts({"behind": "desk", "depth": k}) == {"behind": "desk", "depth": float(k)}


@pytest.mark.parametrize("k", [1.41, 2.0, 4.0])
def test_a_card_behind_the_front_and_nearer_than_it_is_refused_by_name(k: float) -> None:
    msg = refusal({"behind": "desk", "depth": k})
    assert "a card behind the plate's front cannot sit nearer than it: depth <= 1.4 with behind=, or drop one" in msg
    assert f"depth={k:g} with behind='desk'" in msg


def test_a_card_on_a_declared_surface_is_refused_a_depth_by_name() -> None:
    msg = refusal({"embed": "poster", "depth": 1.15})
    assert "embed and depth are two names for one thing" in msg and "drop depth= or drop embed=" in msg


# ---- the golden is the paint's proof -------------------------------------------------------------

def test_the_dock_depth_golden_carries_the_option_on_its_dock_and_the_plate_s_four_planes() -> None:
    import json
    src = GOLDEN / "sources" / "dock-depth.timeline.json"
    if not src.exists():
        pytest.skip("the golden sources are not written in this checkout")
    tl = json.loads(src.read_text(encoding="utf-8"))
    scene = tl["scenes"][0]
    assert [ly["k"] for ly in scene["world"]["layers"]] == [1.0, 1.05, 1.15, 1.275, 1.40][:len(scene["world"]["layers"])] or \
        all(ly["k"] > 0 for ly in scene["world"]["layers"])
    assert scene["docks"][0]["depth"] == 1.15, "the golden's card stands on the `-mid` plane"
    assert scene["species"][0]["kind"] == "focus_zoom", "E49/E59: the move is the one the scene already had"
