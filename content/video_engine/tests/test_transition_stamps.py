"""The two defaults a WORLD-TAKING transition implies (P53 T2 / T6; BACKLOG R26-60, R26-66).

Measured before either was written (`measure_stage_gaps.py` on `normal-for-which-bridge/build-short-axes`): the
suck at 13.79 s and the melt at 40.51 s each left the stage with no world on it for 3.1 s, 8.9% of a 69.8 s short,
and both ran under a live sentence. An inked arrival on the page that FOLLOWS took the measured share to 0.0%.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
import build_scene_timeline_f as B  # noqa: E402


def _page_scene(sid: str, a: float, b: float, exit_id: str | None = None, **page) -> dict:
    return {"scene_id": sid, "span": [a, b], "exit": exit_id,
            "world": {"kind": "ledger", "page": {"schema_version": "ledger_page.v1", "builder": "story", **page}}}


def test_the_page_under_a_suck_is_stamped_cut():
    scenes = [_page_scene("s01", 1.0, 10.0, "suck:0.5,0.5"), _page_scene("s02", 10.0, 20.0, "cut")]
    notes = B.stamp_transition_pages(scenes)
    assert scenes[0]["world"]["page"]["exit"] == "cut", "R26-60: it must not retract itself into the suck"
    assert any("exit=cut" in n and "s01" in n for n in notes), notes


def test_the_page_after_a_melt_keeps_its_own_arrival():
    """Withdrawn 2026-09-12 (the operator): the inked arrival is for the first frame or a row that needs speed; after
    a suck or a melt the page arrives by its roll-out or its mount, so nothing is stamped on it."""
    scenes = [_page_scene("s01", 1.0, 10.0, "melt", exit="cut"), _page_scene("s02", 10.0, 20.0, "cut")]
    assert B.stamp_transition_pages(scenes) == []
    assert "enter" not in scenes[1]["world"]["page"]


def test_the_hook_opens_on_the_axes_register():
    """The operator, 2026-09-12: "hook should open on the axes register, then we immediately answer it on the ledger"."""
    scenes = [_page_scene("s01", 0.0, 10.0, "cut"), _page_scene("s02", 10.0, 20.0, "cut")]
    notes = B.stamp_transition_pages(scenes)
    assert scenes[0]["world"]["page"]["enter"] == "axes"
    assert "enter" not in scenes[1]["world"]["page"], "only the hook"
    assert any("s01" in n and "hook" in n for n in notes), notes


def test_a_hook_that_declares_its_enter_is_left_alone():
    scenes = [_page_scene("s01", 0.0, 10.0, "cut", enter="built")]
    assert B.stamp_transition_pages(scenes) == []
    assert scenes[0]["world"]["page"]["enter"] == "built"


def test_an_author_who_chose_is_not_corrected():
    scenes = [_page_scene("s01", 1.0, 10.0, "suck", exit="cut"),
              _page_scene("s02", 10.0, 20.0, "cut", enter="spiral")]
    assert B.stamp_transition_pages(scenes) == []
    assert scenes[1]["world"]["page"]["enter"] == "spiral"


def test_a_cut_and_a_dip_stamp_nothing():
    for kind in ("cut", "dip", "wipe_right", None):
        scenes = [_page_scene("s01", 1.0, 10.0, kind), _page_scene("s02", 10.0, 20.0, "cut")]
        assert B.stamp_transition_pages(scenes) == [], kind
        assert "enter" not in scenes[1]["world"]["page"], kind


def test_a_world_that_is_not_a_page_is_left_alone():
    scenes = [{"scene_id": "s01", "span": [0.0, 10.0], "exit": "suck", "world": {"asset_id": "plate-x"}},
              {"scene_id": "s02", "span": [10.0, 20.0], "exit": "cut", "world": {"asset_id": "plate-y"}}]
    assert B.stamp_transition_pages(scenes) == []
