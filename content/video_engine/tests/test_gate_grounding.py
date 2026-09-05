"""P37 T7 - G-i / G-j / G-k on the INFO-then-FAIL ladder: INFO while nothing is declared,
FAIL the moment a declaration is wrong, PASS when it is right."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
import gate_grounding as G  # noqa: E402

TEMPLATE = (ROOT / "docs/content-video-engine/samples/scene-evidence-player.template.html").read_text(encoding="utf-8")


def _scene(**kw) -> dict:
    return {"scene_id": "s01", "world": {"asset_id": "w"}, "span": [0, 10], "species": [], **kw}


def _by_id(gates):
    return {g.id: g for g in gates}


def test_nothing_declared_lands_as_info_not_pass():
    g = _by_id(G.run({"scenes": [_scene()]}))
    assert g["G-i"].level == "INFO" and g["G-k"].level == "INFO" and g["G-j"].level == "INFO"


def test_eye_height_off_the_horizon_fails_and_on_it_passes():
    pit = _scene(world={"asset_id": "w", "horizon": 0.42}, species=[{"kind": "plate_life", "at": 1, "dur": 3, "cutouts": [{"asset": "cut-host", "x": 0.3, "y": 0.9, "w": 0.2, "eye_y": 0.55}]}])
    assert _by_id(G.run({"scenes": [pit]}))["G-i"].level == "FAIL"
    pit["species"][0]["cutouts"][0]["eye_y"] = 0.43
    assert _by_id(G.run({"scenes": [pit]}))["G-i"].level == "PASS"


def test_the_template_anchors_sprites_at_the_feet_and_a_screen_tween_fails():
    walk = _scene(species=[{"kind": "plate_life", "at": 1, "dur": 3, "cutouts": [{"asset": "cut-host", "x": 0.3, "y": 0.9, "w": 0.2, "tween": "floor"}]}])
    assert _by_id(G.run({"scenes": [walk]}, TEMPLATE))["G-j"].level == "PASS"
    walk["species"][0]["cutouts"][0]["tween"] = "screen"
    assert _by_id(G.run({"scenes": [walk]}, TEMPLATE))["G-j"].level == "FAIL"
    assert _by_id(G.run({"scenes": [walk]}, "#plife img { position: absolute; }"))["G-j"].level == "FAIL"


def test_contact_without_a_solver_fails():
    grab = _scene(species=[{"kind": "plate_life", "at": 1, "dur": 3, "contact": True, "cutouts": []}])
    assert _by_id(G.run({"scenes": [grab]}))["G-k"].level == "FAIL"
    grab["species"][0]["solver"] = "ik"
    assert _by_id(G.run({"scenes": [grab]}))["G-k"].level == "PASS"
