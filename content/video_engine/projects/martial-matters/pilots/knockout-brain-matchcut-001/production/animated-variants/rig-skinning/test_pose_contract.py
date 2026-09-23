"""Parent acceptance: measure solved geometry, never authored target labels."""
from pathlib import Path
import math
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent/'rig-foundation'))
import rig_pose as r


def test_both_actual_hands_contact_and_brain_waits():
    for t, side in ((r.RIGHT_CONTACT_T,'right'), (r.HOOK_CONTACT_T,'left')):
        p=r.evaluate_frame(t)
        gap=math.dist(p.attacker.arm(side).end,p.victim.head)-r.GLOVE_RADIUS-p.victim.head_radius
        assert abs(gap)<1., (side,gap)
    for f in range(round(r.HEAD_SNAP_T*r.FPS)):
        assert r.evaluate_frame(f/r.FPS).brain is None


def test_solved_bones_and_planted_feet():
    for p in r.evaluate_all_frames():
        for fighter in (p.attacker,p.victim):
            for chain in (*fighter.feet, fighter.arm('right'),fighter.arm('left')):
                assert abs(chain.upper_error)<1e-5
                assert abs(chain.lower_error)<1e-5
            if fighter is p.attacker or p.time_s < r.FALL_RELEASE_T:
                for chain,target in zip(fighter.feet,fighter.feet_targets):
                    assert math.dist(chain.end,target)<.1, (p.frame,fighter.name,chain.target_error)


def test_no_surface_floor_penetration_and_constant_scale():
    for p in r.evaluate_all_frames():
        for fighter in (p.attacker,p.victim):
            assert fighter.scale == 1., (p.frame,fighter.name)
            assert r.floor_receipt(fighter)['clearance_px']>=-.5, (p.frame,fighter.name,r.floor_receipt(fighter))


def test_seek_order_and_dqs_usage():
    sequential=r.evaluate_all_frames()
    for f in reversed(range(r.FRAME_COUNT)):
        assert sequential[f] == r.evaluate_frame(f/r.FPS)
    assert r.DQS is not None


def test_no_precontact_impact_graphic():
    for f in range(round(r.RIGHT_CONTACT_T*r.FPS)):
        p=r.evaluate_frame(f/r.FPS)
        assert p.right_impact == 0
