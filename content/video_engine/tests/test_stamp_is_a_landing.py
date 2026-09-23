"""P69 T2 (R26-247, the gate): a STAMP is a landing to the motion gate, at its contact.

The stamp arrival (kinetics/stopaction.mjs STAMP_ARRIVAL, E99 s87) came in with no change to any reader, so the
motion gate saw a stamped dock as a bare dock: `_arrival_events` gave it no event, `_landings` put its contact on
its enter (`+ 0.0`), and M20 had no row for it. The contact is the CLAMPED scale spring's crossing time `tc` - the
instant the mark reaches its own size and the overshoot clamp ends the spring (stopaction.mjs:305-313) - mirrored
here as `STAMP_CONTACT_S` and pinned against the module's own `STAMP_ARRIVAL.LAND`, never a hardcoded copy.

Four readers take it, STAMPS ONLY: M01-M03/M07 (an event), M20 (a row), E51 / M22 (an anchor a push ties to) and
M29 (a dock landing that licenses a transient cue). Throw and land keep every reader's own value, byte for byte
(0.46 in `_landings`, STOP_FLIGHT_S / STOP_LAND_S in `_arrivals`).

P69 T4 (the camera; E51): the camera mirror (`_attention_moves`, `camera_state_at`) moved WITH the player - a
landings-attention scene pulls toward a stamp from its contact, and the gate's state agrees with the player's
`camAttentionState` at the same instants (section 4).
"""
from __future__ import annotations

import json
import math
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import gate_motion_density as G  # noqa: E402
from test_gate_motion_density import _by_id, _drop_window_build, _with_dock  # noqa: E402

STOP_MJS = ROOT / "content/video_engine/scripts/kinetics/stopaction.mjs"
CAM_MJS = ROOT / "content/video_engine/scripts/kinetics/camera.mjs"
NODE = shutil.which("node") or shutil.which("node.exe")
needs_node = pytest.mark.skipif(NODE is None, reason="node is not on PATH")
TC_TOL = 1e-4          # the acceptance: the mirror agrees with the module's closed form to within this
ENTER = 9.2158         # a stamp's enter: its contact falls at 9.37 s, clear of the fixture's caption-page starts (every 1.5 s)


def _node(expr: str):
    """Evaluate one expression against stopaction.mjs (and camera.mjs's attention law) and return its JSON."""
    src = (f"import {{ STAMP_ARRIVAL, STAMP_LAND }} from {json.dumps(STOP_MJS.as_uri())};\n"
           f"import {{ ATTN, camAttentionState }} from {json.dumps(CAM_MJS.as_uri())};\n"
           f"console.log(JSON.stringify(({expr})));\n")
    out = subprocess.run([NODE, "--input-type=module", "-e", src], capture_output=True, text=True, cwd=str(ROOT))
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout.strip().splitlines()[-1])


def _tc(g: dict) -> float:
    """stopaction.mjs:308-312, the closed form: the first instant a 0 -> 1 step response of the mass-spring-damper
    reaches 1 - wd t = pi - atan(wd / (z w))."""
    z = g["c"] / (2 * math.sqrt(g["k"] * g["m"]))
    w = math.sqrt(g["k"] / g["m"])
    wd = w * math.sqrt(1 - z * z) if z < 1 else 0.0
    return (math.pi - math.atan2(wd, z * w)) / wd if wd > 0 else math.inf


def _stamp_scene(arrive="stamp", enter=ENTER, species=None) -> dict:
    return {"scene_id": "s01", "world": {"kind": "clip"}, "span": [0.0, 30.0], "species": species or [],
            "docks": [{"slide": "fed", "enter": enter, "exit": enter + 6.0, "arrive": arrive, "mass": "ink"}]}


# ---- 1. THE CONTACT IS THE MODULE'S tc, MIRRORED AND PINNED -------------------------------------

@needs_node
def test_stamp_contact_is_the_clamped_scale_springs_tc_read_from_the_module():
    land = _node("STAMP_ARRIVAL.LAND")
    tc = _tc(land)
    assert abs(tc - _node("STAMP_LAND.tc")) < 1e-9, "the closed form here is the module's own"
    assert abs(G.STAMP_CONTACT_S - tc) <= TC_TOL, f"STAMP_CONTACT_S {G.STAMP_CONTACT_S} vs the module's tc {tc:.6f}"
    assert 0.15 < tc < 0.16, f"tc {tc:.6f}: the scale spring (m 0.9, k 220, c 14) crosses 1 at ~0.1542 s"


def test_stamp_contact_carries_its_derived_tag():
    src = (ROOT / "content/video_engine/scripts/gate_motion_density.py").read_text(encoding="utf-8")
    line = next((ln for ln in src.splitlines() if ln.startswith("STAMP_CONTACT_S")), "")
    assert "[DERIVED: stopaction.mjs STAMP_LAND.tc]" in line, line


# ---- 2. THE FOUR READERS SEE A STAMP AT enter + STAMP_CONTACT_S ---------------------------------

def test_a_stamp_dock_is_an_arrival_and_its_contact_is_an_event_m01_m03_m07():
    contact = ENTER + G.STAMP_CONTACT_S
    assert G._arrivals([_stamp_scene()]) == [(ENTER, "fed", "stamp", contact)]
    assert G._arrival_events([_stamp_scene()]) == [round(contact, 2)]


def test_the_stamp_contact_reaches_the_frame_event_list_that_m01_m03_m07_count():
    contact = round(ENTER + G.STAMP_CONTACT_S, 2)
    tl, docks, mp = _drop_window_build(cue_at=20.0)
    bare = G.analyse(_with_dock(tl, enter=ENTER, arrive=None), docks, mp)["events"]
    tl, docks, mp = _drop_window_build(cue_at=20.0)
    stamped = G.analyse(_with_dock(tl, enter=ENTER, arrive="stamp"), docks, mp)["events"]
    assert contact not in bare and contact in stamped, (contact, sorted(set(stamped) - set(bare)))


def test_m20_carries_a_row_for_the_stamp_at_its_contact():
    g = G._cadence_gate([_stamp_scene()])
    assert g is not None and g.id == "M20" and g.level == "INFO", g
    assert "1 arrival(s)" in g.message, g.message
    assert f"fed stamp (ink) - contact {G.STAMP_CONTACT_S:.2f}s after its enter, at {ENTER + G.STAMP_CONTACT_S:.2f}s" in g.message, g.message


def test_m20_names_an_unmassed_stamp_ink_the_engines_own_default():
    sc = _stamp_scene()
    del sc["docks"][0]["mass"]
    assert "fed stamp (ink)" in G._cadence_gate([sc]).message


def test_a_stamp_is_an_e51_landing_at_its_contact():
    lands = G._landings(_stamp_scene())
    assert lands == [(ENTER + G.STAMP_CONTACT_S, "dock fed stamp")], lands


def test_m22_ties_a_push_to_the_stamps_contact_not_to_its_enter():
    # the push sits 1.47 s after the contact: inside (at - 1.5, at + 0.3) of the contact, 0.03 s before the enter's reach
    at = ENTER + G.STAMP_CONTACT_S + 1.47
    push = [{"kind": "punch", "at": at, "dur": 0.6}]
    assert G._untied_pushes([_stamp_scene(species=push)]) == []
    assert G._untied_pushes([_stamp_scene(arrive=None, species=push)]) == [("s01", "punch", round(at, 2))]


def test_m29_pairs_a_transient_with_a_stamps_contact():
    tl, docks, mp = _drop_window_build(cue_at=9.0)                  # no page lands within 1.5 s of 9.0 s ...
    _with_dock(tl, enter=9.0 - G.STAMP_CONTACT_S, arrive="stamp")    # ... the stamp's contact does, at 9.00 s
    g = _by_id(G.run(tl, docks, mp)[0])
    assert g["M29"].level == "PASS", g["M29"]
    assert "with s02 dock paper stamp lands at 9.00s" in g["M29"].message, g["M29"]


# ---- 3. THROW AND LAND ARE UNTOUCHED, BYTE FOR BYTE ----------------------------------------------

def test_throw_and_land_keep_every_readers_own_value():
    assert (G.STOP_FLIGHT_S, G.STOP_LAND_S) == (0.45, 0.32)
    throw, land = _stamp_scene(arrive="throw"), _stamp_scene(arrive="land")
    assert G._landings(throw) == [(ENTER + 0.46, "dock fed throw")]          # the 0.46 in _landings, as it was
    assert G._landings(land) == [(ENTER + 0.32, "dock fed land")]
    assert G._arrivals([throw, land]) == [(ENTER, "fed", "throw", ENTER + G.STOP_FLIGHT_S),
                                          (ENTER, "fed", "land", ENTER + G.STOP_LAND_S)]
    msg = G._cadence_gate([throw, land]).message
    assert msg == "2 arrival(s): fed throw ~2479 px/s -> on 1s; fed land (ink) - weight sold 0.32s before the impact", msg


def test_any_other_arrival_is_still_no_arrival_and_lands_on_its_enter():
    for arr in (None, "pop", "spring"):
        assert G._arrivals([_stamp_scene(arrive=arr)]) == []
        assert G._cadence_gate([_stamp_scene(arrive=arr)]) is None
        assert G._landings(_stamp_scene(arrive=arr)) == [(ENTER, f"dock fed {arr or 'spring'}")]


# ---- 4. THE CAMERA MIRROR PULLS TOWARD A STAMP FROM ITS CONTACT, AS THE PLAYER DOES (T4) --------------------------

PLACE = {"x": 140, "y": 600, "w": 800, "h": 450}
SW, SH = 1080, 1920


def _attn_scene(arrive="stamp", attention="landings") -> dict:
    sc = _stamp_scene(arrive=arrive)
    sc["camera"] = {"keys": [], "attention": attention}
    sc["docks"][0]["place"] = dict(PLACE)
    return sc


def test_the_camera_mirror_ties_a_stamps_pull_to_its_contact():
    contact = ENTER + G.STAMP_CONTACT_S
    assert G._attention_moves(_attn_scene()) == [(contact, contact + G.ATTN_IN, "fed")]
    assert G._attention_moves(_attn_scene(attention="locked")) == [], "locked: the reference's default, nothing moves"


def test_camera_state_at_is_identity_before_a_stamps_contact_and_the_full_pull_after():
    sc, contact = _attn_scene(), ENTER + G.STAMP_CONTACT_S
    assert G.camera_state_at(sc, contact - 0.05, SW, SH, None)["s"] == 1.0, "still between the enter and the contact"
    assert abs(G.camera_state_at(sc, contact + G.ATTN_IN / 2, SW, SH, None)["s"] - (1 + (G.ATTN_SCALE - 1) / 2)) < 1e-9
    on = G.camera_state_at(sc, contact + G.ATTN_IN, SW, SH, None)
    assert abs(on["s"] - G.ATTN_SCALE) < 1e-12 and on["look"] == (540.0, 825.0) and on["at"] == on["look"], on


@needs_node
def test_the_gate_and_the_player_read_one_camera_at_the_same_instants():
    """The player's contact (STAMP_LAND.tc) against the gate's (STAMP_CONTACT_S, 4 dp): one zoom at every instant
    across the pull, the hold and the release - to within what 4 dp of tc can move a 0.5 s inout ramp."""
    sc = _attn_scene()
    ts = [ENTER + dt for dt in (0.1, 0.16, 0.25, 0.4, 0.7, 3.0, 5.5, 5.8, 6.1)]
    d = {"arrive": "stamp", "enter": ENTER, "exit": ENTER + 6.0, "place": PLACE}
    player = _node(f"{json.dumps(ts)}.map((t) => (camAttentionState([{json.dumps(d)}], t, "
                   "(x) => +x.enter + STAMP_LAND.tc, ATTN) || { s: 1 }).s)")
    gate = [G.camera_state_at(sc, t, SW, SH, None)["s"] for t in ts]
    assert all(abs(a - b) < 1e-4 for a, b in zip(player, gate)), list(zip(ts, player, gate))
    assert player[0] == 1 and gate[0] == 1.0 and max(gate) > 1.05, "identity before the contact; the pull after it"


def test_the_camera_mirror_keeps_throw_and_land_on_their_own_contacts():
    for arr, lag in (("throw", G.STOP_FLIGHT_S), ("land", G.STOP_ANTIC_S + G.STOP_DROP_S)):
        tc = ENTER + lag
        assert G._attention_moves(_attn_scene(arrive=arr)) == [(tc, tc + G.ATTN_IN, "fed")], arr
        assert G.camera_state_at(_attn_scene(arrive=arr), tc - 0.01, SW, SH, None)["s"] == 1.0, arr
        assert G.camera_state_at(_attn_scene(arrive=arr), tc + G.ATTN_IN, SW, SH, None)["s"] == 1 + (G.ATTN_SCALE - 1) * 1.0, arr
    for arr in (None, "pop", "spring"):
        assert G._attention_moves(_attn_scene(arrive=arr)) == [], arr
        assert G.camera_state_at(_attn_scene(arrive=arr), ENTER + 3.0, SW, SH, None)["s"] == 1.0, arr
