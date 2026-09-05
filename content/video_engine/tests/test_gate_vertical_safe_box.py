"""P37 T8 - G-l. The strongest evidence in the PRP: the gate FAILs the template exactly as it
shipped before T0 (the fixture below is that CSS, verbatim) and PASSes the template now."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
import gate_vertical_safe_box as V  # noqa: E402

TEMPLATE = ROOT / "docs/content-video-engine/samples/scene-evidence-player.template.html"

PRE_T0_CSS = '''
  html[data-aspect="9:16"] .dock { width: 952px; top: 690px; }
  html[data-aspect="9:16"] #dock-1 { left: 64px; }
  html[data-aspect="9:16"] #dock-2 { left: 64px; top: 1180px; }
  html[data-aspect="9:16"] #dock-1.solo { width: 952px; left: 64px; top: 690px; }
'''


def _elements(findings):
    return sorted({f.element for f in findings})


def test_the_template_as_shipped_before_t0_fails():
    findings = V.check_template_css(PRE_T0_CSS)
    assert _elements(findings) == ["#caption.quiet", "#dock-1", "#dock-2"], [f.line() for f in findings]
    text = " ".join(f.detail for f in findings)
    assert "leaves the box x(80, 880)" in text          # 64 + 952 = 1016, into the right rail
    assert "leaves the box y(280, 1340)" in text        # dock-2 from 1180 runs past the box
    assert "bottom dead zone" in text                   # no 9:16 caption rule


def test_the_template_now_passes():
    findings = V.check_template_css(TEMPLATE.read_text(encoding="utf-8"))
    assert not findings, "\n".join(f.line() for f in findings)


def test_rendered_rectangles_are_judged_the_same_way():
    ok = {"dock-1": {"x": 80, "y": 280, "right": 880, "bottom": 794}, "dock-2": {"x": 80, "y": 806, "right": 880, "bottom": 1320},
          "caption": {"x": 145, "y": 1399, "right": 935, "bottom": 1440}}
    assert V.check_rects(ok) == []
    bad = {"dock-2": {"x": 64, "y": 1180, "right": 1016, "bottom": 1780}, "caption": {"x": 145, "y": 1759, "right": 935, "bottom": 1800}}
    assert _elements(V.check_rects(bad)) == ["caption", "dock-2"]
