"""Money Physics banner — strip-first layout (v3).

Everything that matters lives INSIDE the YouTube channel-page crop
(1546x423 centered in 2560x1440, y 508..931):
  lockup (left) | host face + presenting hand (center) | triad on board (right)
Full-bleed desktop view reveals the rest of the host below the strip.
Stage background sampled from the plate (#F6D8A1) so there is no seam.
"""
from __future__ import annotations

import base64
from pathlib import Path

from PIL import Image

REPO = Path(r"C:\Users\Snipe\Downloads\Outreach Program\.claude\worktrees\sweet-villani-1c3a16")
HOST_BOARD = (REPO / "content/video_engine/projects/systems-and-blowups/review/claims"
              / "finance-host-evidence-exp-2/objects/host-presents-board-v1.png")
BUILD = Path(__file__).parent / "steel-and-paper-build"

CREAM_PLATE = "#F6D8A1"          # sampled from the plate background
CHARCOAL, COBALT, TEAL, CORAL = "#25313C", "#1769C2", "#178C83", "#ED6A4A"

# Plate geometry (1536x1024 source): face box ~(300..560, 60..330),
# gesturing hand ~(770..950, 440..570). Display height 1000px (s=0.977).
PLATE_H = 1000          # px on stage
PLATE_LEFT = 700        # face center x ≈ 700 + 430*0.977 ≈ 1120  (in strip)
PLATE_TOP = 400         # face center y ≈ 400 + 195*0.977 ≈ 590   (in strip)
                        # hand center  y ≈ 400 + 505*0.977 ≈ 893  (in strip)


def b64(path: Path, width: int = 1600) -> str:
    im = Image.open(path).convert("RGB")
    if im.width > width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    tmp = BUILD / "_tmp.jpg"
    im.save(tmp, quality=88)
    data = base64.b64encode(tmp.read_bytes()).decode()
    tmp.unlink()
    return f"data:image/jpeg;base64,{data}"


def page(scale: float, show_safe: bool) -> str:
    safe = ""
    if show_safe:
        safe = ('<div style="position:absolute;left:507px;top:508px;width:1546px;height:423px;'
                'outline:2px dashed rgba(37,49,60,.4);z-index:9;pointer-events:none;"></div>')
    return f"""<!doctype html><html><head><meta charset="utf-8">
<title>Money Physics banner</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@700;800;900&display=swap">
<style>
  html,body {{ margin:0; padding:0; background:{CREAM_PLATE}; }}
  #stage {{ width:2560px; height:1440px; position:relative; overflow:hidden;
            background:{CREAM_PLATE}; font-family:Inter,Arial,sans-serif;
            transform:scale({scale}); transform-origin:top left; }}
  img.plate {{ position:absolute; left:{PLATE_LEFT}px; top:{PLATE_TOP}px;
               height:{PLATE_H}px; }}
  .lockup {{ position:absolute; left:545px; top:560px; width:430px; z-index:5; }}
  .lockup .nm {{ font-weight:900; font-size:64px; color:{CHARCOAL}; line-height:1.02; }}
  .lockup .nm b {{ color:{COBALT}; }}
  .lockup .line {{ font-weight:900; font-size:30px; color:{CHARCOAL}; margin-top:16px;
                   line-height:1.16; }}
  .lockup .line em {{ font-style:normal; color:{CORAL}; }}
  .board {{ position:absolute; left:1380px; top:600px; width:640px;
            text-align:center; z-index:5; }}
  .board .triad {{ white-space:nowrap; font-weight:900; font-size:64px; color:{CHARCOAL}; }}
  .board .triad .chip {{ background:{COBALT}; color:#F4E6C7; padding:0 16px; }}
  .board .sub {{ font-weight:700; font-size:27px; color:{TEAL}; margin-top:14px;
                 letter-spacing:.05em; }}
</style></head><body>
<div id="stage">
  <img class="plate" src="{b64(HOST_BOARD)}">
  {safe}
  <div class="lockup">
    <div class="nm">MONEY<br><b>PHYSICS</b></div>
    <div class="line">The market isn't magic.<br>It's <em>mechanics</em>.</div>
  </div>
  <div class="board">
    <div class="triad">Risk. <span class="chip">Reward.</span> Time.</div>
    <div class="sub">how markets actually move</div>
  </div>
</div>
</body></html>"""


(BUILD / "money-physics-banner-preview.html").write_text(page(0.5, True), encoding="utf-8")
(BUILD / "money-physics-banner-export.html").write_text(page(1.0, False), encoding="utf-8")
print("written")
