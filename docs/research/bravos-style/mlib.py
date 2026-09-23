"""Pixel-measurement helpers for the Bravos long-form chart spec. Every function reads pixels only."""
import numpy as np
from PIL import Image
def load(p):
    return np.asarray(Image.open(p).convert('RGB')).astype(int)
def hx(c):
    c = [int(round(v)) for v in c]
    return '#%02X%02X%02X' % tuple(c)
def med(a, x0, y0, x1, y1):
    return np.median(a[y0:y1, x0:x1].reshape(-1, 3), axis=0)
def lum(a):
    return 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]
def runs(mask):
    out, start = [], None
    for i, m in enumerate(mask):
        if m and start is None: start = i
        if not m and start is not None: out.append((start, i - 1)); start = None
    if start is not None: out.append((start, len(mask) - 1))
    return out
def bbox(mask):
    ys, xs = np.nonzero(mask)
    if len(xs) == 0: return None
    return int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())
def save_crop(a, box, path, zoom=1):
    im = Image.fromarray(a[box[1]:box[3], box[0]:box[2]].astype('uint8'))
    if zoom != 1: im = im.resize((im.width * zoom, im.height * zoom), Image.NEAREST)
    im.save(path)
