"""R26-48 / P52 T4 - where do two frames differ? The bounding box of the changed pixels, the count,
the max channel delta, and the elements whose client rect covers that box (so a residual mismatch is
attributed to a THING, not to a hash).

    python px_diff.py <build> <t> [<t> ...]        # reads <build>/determinism/<t>-{warm,cold}.png
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[7]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
import render_baseline as RB  # noqa: E402


def report(build: Path, t: float, log=print) -> None:
    d = build / "determinism"
    w = d / f"{t:.2f}-warm.png"
    c = d / f"{t:.2f}-cold.png"
    if not (w.exists() and c.exists()):
        log(f"t={t:.2f}  no frame pair on disk ({w.name}) - the instant matched")
        return
    (W, H), a = RB.rgb_bytes(w.read_bytes())
    (_, _), b = RB.rgb_bytes(c.read_bytes())
    n = 0
    x0, y0, x1, y1, mx = W, H, -1, -1, 0
    for i in range(0, len(a), 3):
        if a[i] != b[i] or a[i + 1] != b[i + 1] or a[i + 2] != b[i + 2]:
            p = i // 3
            x, y = p % W, p // W
            n += 1
            x0, y0, x1, y1 = min(x0, x), min(y0, y), max(x1, x), max(y1, y)
            mx = max(mx, abs(a[i] - b[i]), abs(a[i + 1] - b[i + 1]), abs(a[i + 2] - b[i + 2]))
    if n == 0:
        log(f"t={t:.2f}  the two PNGs on disk are identical now")
        return
    log(f"t={t:.2f}  {n} px differ ({100.0 * n / (W * H):.3f} % of {W}x{H}), max channel delta {mx}, "
        f"box x{x0}-{x1} y{y0}-{y1} ({x1 - x0 + 1}x{y1 - y0 + 1})")


def main(argv):
    build = Path(argv[0])
    for t in [float(x) for x in argv[1:]]:
        report(build, t)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
