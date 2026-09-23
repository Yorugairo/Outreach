"""Planar skinning using unit dual quaternions embedded in three dimensions.

Weights are supplied, not solved by BBW. Blended transforms are rigid at each
vertex; a spatially varying deformation need not preserve mesh area.
"""
import math


def mul(a, b):
    w, x, y, z = a
    v, i, j, k = b
    return (w*v-x*i-y*j-z*k, w*i+x*v+y*k-z*j,
            w*j-x*k+y*v+z*i, w*k+x*j-y*i+z*v)


def conj(q):
    return (q[0], -q[1], -q[2], -q[3])


def dot(a, b):
    return sum(x*y for x, y in zip(a, b))


def encode(tx, ty, angle):
    if not all(math.isfinite(v) for v in (tx, ty, angle)):
        raise ValueError('finite transform required')
    real = (math.cos(angle/2), 0., 0., math.sin(angle/2))
    dual = tuple(v*.5 for v in mul((0., tx, ty, 0.), real))
    return real, dual


def blend(transforms, weights):
    """Blend {bone: (real, dual)} with sign alignment and Study normalization.

    The highest-weight bone (lexical tie break) fixes the quaternion hemisphere.
    Exact half-turn ambiguities follow its authored quaternion representation.
    """
    if not weights or any(not math.isfinite(v) or v < 0 for v in weights.values()):
        raise ValueError('finite nonnegative weights required')
    total = sum(weights.values())
    if not math.isfinite(total) or total <= 0:
        raise ValueError('positive weight sum required')
    names = sorted(n for n in weights if weights[n] > 0)
    for name in names:
        if name not in transforms:
            raise ValueError(f'missing transform: {name}')
        pair = transforms[name]
        if not isinstance(pair, (tuple, list)) or len(pair) != 2:
            raise ValueError('quaternion pair required')
        r, d = pair
        if any(not isinstance(q, (tuple, list)) or len(q) != 4 for q in (r,d)):
            raise ValueError('two four-component quaternions required')
        if not all(isinstance(v, (int,float)) and math.isfinite(v) for v in (*r,*d)):
            raise ValueError('finite quaternion pair required')
    anchor = min(names, key=lambda n: (-weights[n], n))
    reference = transforms[anchor][0]
    real, dual = [0.]*4, [0.]*4
    for name in names:
        r, d = transforms[name]
        if abs(dot(r, r)-1) > 1e-6 or abs(dot(r, d)) > 1e-6:
            raise ValueError('input must be a unit rigid dual quaternion')
        factor = weights[name]/total * (-1 if dot(reference, r) < 0 else 1)
        for i in range(4):
            real[i] += factor*r[i]
            dual[i] += factor*d[i]
    norm = math.sqrt(dot(real, real))
    if norm < 1e-12:
        raise ValueError('degenerate rotation blend')
    real = tuple(v/norm for v in real)
    dual = tuple(v/norm for v in dual)
    projection = dot(real, dual)
    dual = tuple(d-projection*r for r, d in zip(real, dual))
    return real, dual


def apply(transform, point):
    if len(point) != 2 or not all(math.isfinite(v) for v in point):
        raise ValueError('finite planar point required')
    r, d = transform
    rotated = mul(mul(r, (0., point[0], point[1], 0.)), conj(r))
    translated = mul(d, conj(r))
    return (rotated[1]+2*translated[1], rotated[2]+2*translated[2])


def skin_mesh(points, transforms, weights):
    """Transform rest-space vertices; transforms include inverse bind poses."""
    if len(points) != len(weights):
        raise ValueError('one influence map per vertex required')
    return [apply(blend(transforms, w), p) for p, w in zip(points, weights)]
