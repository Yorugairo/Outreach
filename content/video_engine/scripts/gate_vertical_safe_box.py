"""G-l - the vertical safe-box gate (P37 T8): on a 9:16 stage every dock, and the anchored
caption, must sit inside x[80,880] y[280,1340] / the caption strip y[1340,1440].

Two readers, one rule:
  * static  - the template's `html[data-aspect="9:16"]` CSS (fast, runs anywhere, and FAILs the
              template as it shipped before P37 T0, which is this gate's fixture)
  * rendered - a built player's actual dock/caption rectangles at t (needs playwright; run by
              the tests and by hand on a Tokyo build)

    python gate_vertical_safe_box.py docs/content-video-engine/samples/scene-evidence-player.template.html
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

SAFE_X = (80, 880)
SAFE_Y = (280, 1340)
CAPTION_STRIP = (1340, 1440)
STAGE_H = 1920
# a dock's height at 800px wide: frame 430 + rail 39 + chrome 45 (measured, P37 T0). Scales with width.
DOCK_H_PER_W = 514 / 800
SRC_G_L = "47 s2 G-l / 49 s49.1, 50: platform chrome covers the top 280, bottom 480 and right 200 px of a 1080x1920 short"


@dataclass(frozen=True)
class Finding:
    element: str
    detail: str

    def line(self) -> str:
        return f"FAIL G-l {self.element}: {self.detail}\n     {SRC_G_L}"


def _px(rule: str, prop: str) -> float | None:
    m = re.search(rf"(?<![\w-]){prop}:\s*(-?[0-9.]+)px", rule)
    return float(m.group(1)) if m else None


def _rules(css: str, selector_regex: str) -> list[str]:
    return [m.group(1) for m in re.finditer(r'html\[data-aspect="9:16"\]\s*' + selector_regex + r"\s*\{([^}]*)\}", css)]


def check_template_css(css: str) -> list[Finding]:
    """The 9:16 overrides, read as text. Width/left from the .dock and #dock-N rules; height derived."""
    out: list[Finding] = []
    dock = " ".join(_rules(css, r"\.dock"))
    width, top = _px(dock, "width"), _px(dock, "top")
    if width is None or top is None:
        return [Finding("dock", "no html[data-aspect=\"9:16\"] .dock rule with width and top")]
    height = width * DOCK_H_PER_W
    for name in ("#dock-1", "#dock-2"):
        own = " ".join(_rules(css, re.escape(name) + r"(?![.\w-])"))
        left = _px(own, "left")
        t = _px(own, "top") if _px(own, "top") is not None else top
        if left is None:
            out.append(Finding(name, "no 9:16 left rule")); continue
        if left < SAFE_X[0] or left + width > SAFE_X[1]:
            out.append(Finding(name, f"x {left:.0f}-{left + width:.0f} leaves the box x{SAFE_X}"))
        if t < SAFE_Y[0] or t + height > SAFE_Y[1]:
            out.append(Finding(name, f"y {t:.0f}-{t + height:.0f} (height {height:.0f} at {width:.0f} wide) leaves the box y{SAFE_Y}"))
    cap = " ".join(_rules(css, r"#caption\.quiet"))
    bottom = _px(cap, "bottom")
    if bottom is None:
        out.append(Finding("#caption.quiet", "no 9:16 bottom rule - the caption inherits the 16:9 offset and lands in the bottom dead zone"))
    elif not (STAGE_H - CAPTION_STRIP[1] <= bottom <= STAGE_H - CAPTION_STRIP[0]):
        out.append(Finding("#caption.quiet", f"bottom {bottom:.0f}px puts the caption outside the strip y{CAPTION_STRIP}"))
    return out


def check_rects(rects: dict[str, dict]) -> list[Finding]:
    """Rendered rectangles {id: {x, y, right, bottom}} on the 1080x1920 stage."""
    out: list[Finding] = []
    for name, r in rects.items():
        if name.startswith("dock"):
            if r["x"] < SAFE_X[0] or r["right"] > SAFE_X[1]:
                out.append(Finding(name, f"x {r['x']:.0f}-{r['right']:.0f} leaves x{SAFE_X}"))
            if r["y"] < SAFE_Y[0] or r["bottom"] > SAFE_Y[1]:
                out.append(Finding(name, f"y {r['y']:.0f}-{r['bottom']:.0f} leaves y{SAFE_Y}"))
        elif name == "caption":
            if r["y"] < CAPTION_STRIP[0] - 1 or r["bottom"] > CAPTION_STRIP[1] + 1:
                out.append(Finding(name, f"y {r['y']:.0f}-{r['bottom']:.0f} is not in the strip y{CAPTION_STRIP}"))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("template", help="the player template (or a built player) to read the 9:16 CSS from")
    args = ap.parse_args()
    findings = check_template_css(Path(args.template).read_text(encoding="utf-8"))
    for f in findings:
        print(f.line())
    print(f"VERDICT: {'FAIL' if findings else 'PASS'} ({len(findings)} finding{'s' if len(findings) != 1 else ''}) - {args.template}")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
