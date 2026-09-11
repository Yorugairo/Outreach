"""P37 T3 - G-d. One anchored and one unanchored transform: exactly one finding."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
import lint_template_transforms as L  # noqa: E402

FIXTURE = """
<style>
  .anchored { transform: scale(1.2); transform-origin: 50% 100%; }
  .loose    { transform: rotate(3deg); }
  #card { transform-origin: 0 100%; }
  #card.on { transform: scale(1.05); }
</style>
<script>
  el.style.transformOrigin = "50% 100%";
  el.style.transform = "scale(" + k + ")";
  other.style.transform = "rotate(" + r + "deg)";
</script>
"""


def test_exactly_the_unanchored_ones_are_reported():
    css = L.check_css(FIXTURE)
    assert [f.where for f in css] == ["css:.loose"], [f.line() for f in css]
    js = L.check_js(FIXTURE)
    assert len(js) == 1 and "rotate(" in js[0].detail, [f.line() for f in js]


def test_the_template_lands_as_info_with_a_list():
    import render_baseline as RB
    html = RB.player_text()
    findings = L.check(html)
    assert isinstance(findings, list)   # the count is the deliverable, not a threshold - INFO ladder
