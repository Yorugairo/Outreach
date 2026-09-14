"""R26-94: the `cutout` dock option is authorable from a shot row (P53 T7 / R26-59).

`cutout` was in DOCK_OPTS and the dock loop read `dopt.get("cutout")`, but `dock_opts` had no branch for it, so a row
carrying `{"cutout": True}` fell through to the generic option check and raised KeyError. A cutout is a person, not a
document: no card, no paper, no border. It is refused beside `press`/`stack` (the press card's `kind` would overwrite
it and the pile keys on `kind == "press"`) and beside `embed`/`fit` (the surface's projection repaints the card's
shadow, vignette and lift over the cutout's `boxShadow: none` - the ghost card edge gate 1 removed).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
import build_scene_timeline_f as B  # noqa: E402

PRESS = {"source": "THE HERALD", "phrase": {"x0": 0.1, "y0": 0.2, "x1": 0.6, "y1": 0.4}}


def test_cutout_is_a_flag_the_row_can_author():
    assert "cutout" in B.DOCK_OPTS
    assert B.dock_opts({"cutout": True}) == {"cutout": True}


@pytest.mark.parametrize("bad", ["head", 1, {"head": True}, False, None])
def test_a_cutout_that_is_not_true_is_refused_by_name(bad):
    with pytest.raises(ValueError) as e:
        B.dock_opts({"cutout": bad})
    assert "cutout must be True" in str(e.value)


@pytest.mark.parametrize("other", [
    {"press": PRESS},
    {"press": PRESS, "stack": True},
    {"stack": True},
    {"embed": "tv"},
    {"embed": "tv", "fit": "cover"},
    {"fit": "cover"},
])
def test_a_cutout_with_a_card_or_a_surface_option_is_refused_naming_the_pair(other):
    with pytest.raises(ValueError) as e:
        B.dock_opts({"cutout": True, **other})
    msg = str(e.value)
    assert any(f"cutout and {k}" in msg for k in other), msg


def test_a_row_carrying_cutout_compiles_to_a_cutout_dock():
    # the dock loop's own path: dock_opts checks the row's options, dock_entry writes cutout=bool(dopt.get("cutout"))
    dopt = B.dock_opts({"cutout": True, "arrive": "land"})
    d = B.dock_entry("head-bessent", 0, 2.0, 12.0, 0, B.DOCK_KIND_IMAGE, None,
                     dopt.get("arrive"), dopt.get("mass"), False, cutout=bool(dopt.get("cutout")))
    assert d["kind"] == B.DOCK_KIND_CUTOUT == "cutout"
    plain = B.dock_entry("ev-card", 0, 2.0, 12.0, 0, cutout=bool(B.dock_opts({}).get("cutout")))
    assert "kind" not in plain, "a document dock is byte-for-byte what it was"
