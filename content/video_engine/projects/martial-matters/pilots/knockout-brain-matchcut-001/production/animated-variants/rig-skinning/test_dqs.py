import math
import pytest
from dqs import encode, blend, apply, dot, skin_mesh


def test_rigid_motion_and_identity():
    assert apply(encode(0, 0, 0), (3, 4)) == pytest.approx((3, 4))
    assert apply(encode(2, 3, math.pi/2), (1, 0)) == pytest.approx((2, 4))


def test_rotation_about_joint():
    # Rest joint (2,0) remains fixed under a 90-degree rotation.
    q = encode(2, -2, math.pi/2)
    assert apply(q, (2, 0)) == pytest.approx((2, 0))
    assert apply(q, (3, 0)) == pytest.approx((2, 1))


def test_half_turn_preserves_single_blended_rigid_transform():
    q = blend({'a': encode(0,0,0), 'b': encode(0,0,math.pi)}, {'a': .5, 'b': .5})
    p = apply(q, (1, 0))
    assert p == pytest.approx((0, 1))
    assert dot(q[0], q[0]) == pytest.approx(1)
    assert dot(q[0], q[1]) == pytest.approx(0)


def test_antipodal_encoding_and_weight_order():
    q = encode(1,2,.7)
    minus = tuple(tuple(-v for v in part) for part in q)
    transforms = {'a': q, 'b': minus}
    x = blend(transforms, {'a': .5, 'b': .5})
    y = blend(transforms, {'b': .5, 'a': .5})
    assert apply(x, (4,5)) == pytest.approx(apply(q, (4,5)))
    assert x == y


def test_weights_and_bind_identity():
    points = [(0,0), (1,0), (0,1)]
    weights = [{'a': 2, 'b': 3}]*3
    assert skin_mesh(points, {'a': encode(0,0,0), 'b': encode(0,0,0)}, weights) == points
    for invalid in ({}, {'a': 0}, {'a': -1, 'b': 2}, {'a': float('nan')}):
        with pytest.raises(ValueError):
            blend({'a': encode(0,0,0)}, invalid)


def test_spatially_varying_weights_do_not_guarantee_area():
    # Different rigid transformations at each vertex can change triangle area.
    p = skin_mesh([(0,0),(1,0),(0,1)],
                  {'a': encode(0,0,0), 'b': encode(1,0,0)},
                  [{'a':1},{'b':1},{'a':1}])
    area = abs((p[1][0]-p[0][0])*(p[2][1]-p[0][1])-(p[2][0]-p[0][0])*(p[1][1]-p[0][1]))/2
    assert area == pytest.approx(1.)  # rest area was 0.5


def test_malformed_transforms_and_dimensions():
    for transforms in ({}, {'a': None}, {'a': ((1,0), (0,0))},
                       {'a': ((2,0,0,0),(0,0,0,0))}):
        with pytest.raises(ValueError):
            blend(transforms, {'a':1})
    with pytest.raises(ValueError):
        apply(encode(0,0,0), (1,2,3))


def test_authored_rotation_continuity_around_half_turn():
    # No forced angle wrapping: a single transform passes smoothly through pi.
    before = apply(blend({'a':encode(0,0,math.pi-1e-5)}, {'a':1}), (1,0))
    after = apply(blend({'a':encode(0,0,math.pi+1e-5)}, {'a':1}), (1,0))
    assert math.dist(before,after) < 3e-5
