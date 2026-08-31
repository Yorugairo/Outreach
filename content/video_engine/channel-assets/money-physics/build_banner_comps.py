"""Money Physics — banner + avatar concept comps (review page)."""
from __future__ import annotations

import base64
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps

REPO = Path(r"C:\Users\Snipe\Downloads\Outreach Program\.claude\worktrees\sweet-villani-1c3a16")
CLAIMS = REPO / "content/video_engine/projects/systems-and-blowups/review/claims"
HOST_BOARD = CLAIMS / "finance-host-evidence-exp-2/objects/host-presents-board-v1.png"
HOST_DESK = CLAIMS / "finance-host-in-world-exp-1/objects/host-trade-desk-v1.png"
BUILD = Path(__file__).parent / "steel-and-paper-build"

CREAM, CHARCOAL, COBALT, TEAL, SUNFLOWER, CORAL = (
    "#F4E6C7", "#25313C", "#1769C2", "#178C83", "#F5B72E", "#ED6A4A")


def b64(path: Path, width: int = 1100) -> str:
    im = Image.open(path).convert("RGB")
    if im.width > width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    tmp = BUILD / "_tmp.jpg"
    im.save(tmp, quality=82)
    data = base64.b64encode(tmp.read_bytes()).decode()
    tmp.unlink()
    return f"data:image/jpeg;base64,{data}"


def host_bust_b64() -> str:
    im = Image.open(HOST_DESK).convert("RGB")
    bust = im.crop((260, 60, 900, 700)).resize((420, 420), Image.LANCZOS)
    mask = Image.new("L", (420, 420), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, 420, 420), fill=255)
    circ = ImageOps.fit(bust, (420, 420))
    out = Image.new("RGB", (420, 420), CHARCOAL)
    out.paste(circ, (0, 0), mask)
    tmp = BUILD / "_bust.png"
    out.save(tmp)
    data = base64.b64encode(tmp.read_bytes()).decode()
    tmp.unlink()
    return f"data:image/png;base64,{data}"


HTML = f"""<!doctype html><html><head><meta charset="utf-8">
<title>Money Physics — banner + logo comps</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@500;700;800;900&display=swap">
<style>
  body {{ background:#0a1620; color:{CREAM}; font-family:Inter,Arial,sans-serif; margin:0; padding:28px; }}
  h1 {{ font-size:15px; letter-spacing:.14em; text-transform:uppercase; color:#7d95a6; }}
  h2 {{ font-size:13px; letter-spacing:.1em; text-transform:uppercase; color:{SUNFLOWER}; margin:34px 0 10px; }}
  .banner {{ width:1280px; height:720px; position:relative; overflow:hidden; border:1px solid #14293a; }}
  .safe {{ position:absolute; left:50%; top:50%; width:773px; height:212px; transform:translate(-50%,-50%);
           outline:1px dashed rgba(244,230,199,.35); pointer-events:none; z-index:9; }}
  .safe span {{ position:absolute; right:4px; bottom:2px; font-size:10px; color:rgba(244,230,199,.5); }}
  .grain {{ position:absolute; inset:0; opacity:.05; pointer-events:none;
    background-image:repeating-linear-gradient(0deg, #000 0 1px, transparent 1px 3px); }}

  /* A — the triad */
  .a {{ background:{CREAM}; }}
  .a .inner {{ position:absolute; left:50%; top:50%; transform:translate(-50%,-50%); text-align:center; }}
  .a .name {{ font-weight:800; font-size:26px; letter-spacing:.42em; color:{CHARCOAL}; margin-bottom:18px; }}
  .a .name b {{ color:{COBALT}; }}
  .a .triad {{ white-space:nowrap; font-weight:900; font-size:64px; color:{CHARCOAL}; letter-spacing:-0.01em; }}
  .a .triad .chip {{ background:{COBALT}; color:{CREAM}; padding:0 18px; }}
  .a .tag {{ margin-top:20px; font-weight:700; font-size:22px; color:{TEAL}; letter-spacing:.06em; }}

  /* B — the presenter */
  .b {{ background:{CREAM}; }}
  .b img.plate {{ position:absolute; right:-7%; top:50%; transform:translateY(-50%); height:100%; }}
  .b .board-lockup {{ position:absolute; right:5.5%; top:26%; width:380px; text-align:center; }}
  .b .board-lockup .nm {{ font-weight:900; font-size:48px; color:{CHARCOAL}; line-height:1.02; }}
  .b .board-lockup .nm b {{ color:{COBALT}; }}
  .b .board-lockup .sub {{ font-weight:700; font-size:19px; color:{TEAL}; margin-top:10px; letter-spacing:.05em; }}
  .b .left {{ position:absolute; left:3.5%; top:50%; transform:translateY(-50%); max-width:255px; }}
  .b .left .kicker {{ font-weight:700; font-size:15px; letter-spacing:.3em; color:{TEAL}; }}
  .b .left .line {{ font-weight:900; font-size:30px; color:{CHARCOAL}; margin-top:10px; line-height:1.12; }}
  .b .left .line em {{ font-style:normal; color:{CORAL}; }}

  /* C — the formula */
  .c {{ background:{CHARCOAL}; }}
  .c .inner {{ position:absolute; left:50%; top:50%; transform:translate(-50%,-50%); text-align:center; }}
  .c .nm {{ font-weight:900; font-size:92px; color:{CREAM}; letter-spacing:.02em; }}
  .c .nm b {{ color:{SUNFLOWER}; }}
  .c .formula {{ margin-top:16px; font-weight:700; font-size:30px; color:#9fb3c2; letter-spacing:.08em; }}
  .c .formula b {{ color:{TEAL}; }} .c .formula i {{ font-style:normal; color:{CORAL}; }}
  .c .rule {{ width:340px; height:6px; background:{SUNFLOWER}; margin:22px auto 0; }}

  .avatars {{ display:flex; gap:26px; align-items:center; }}
  .av {{ width:200px; height:200px; border-radius:50%; position:relative; overflow:hidden;
         display:flex; align-items:center; justify-content:center; border:3px solid #14293a; }}
  .av1 {{ background:{CHARCOAL}; }}
  .av1 .mp {{ font-weight:900; font-size:86px; color:{CREAM}; letter-spacing:-.04em; }}
  .av1 .mp b {{ color:{SUNFLOWER}; }}
  .av1 .orbit {{ position:absolute; inset:14px; border:3px solid {COBALT}; border-radius:50%;
                 clip-path:polygon(0 0, 100% 0, 100% 38%, 0 38%); transform:rotate(-24deg); }}
  .av2 {{ background:{CREAM}; }}
  .av3 img {{ width:100%; height:100%; object-fit:cover; }}
  .cap {{ font-size:12px; color:#7d95a6; margin-top:6px; text-align:center; }}
</style></head><body>
<h1>MONEY PHYSICS — banner directions (shown at 50%; export 2560×1440) · dashed box = YouTube safe zone</h1>

<h2>A · THE TRIAD — minimal newsprint (BizMoney / "Discipline. Growth. Peace." lineage)</h2>
<div class="banner a"><div class="grain"></div><div class="safe"><span>safe zone</span></div>
  <div class="inner">
    <div class="name">MONEY <b>PHYSICS</b></div>
    <div class="triad">Risk. <span class="chip">Reward.</span> Time.</div>
    <div class="tag">Every rule is the same three dials. Build our world.</div>
  </div>
</div>

<h2>B · THE PRESENTER — host presents the channel (Alicia lineage, diegetic board)</h2>
<div class="banner b"><div class="safe"><span>safe zone</span></div>
  <img class="plate" src="{b64(HOST_BOARD)}">
  <div class="board-lockup"><div class="nm">MONEY<br><b>PHYSICS</b></div>
    <div class="sub">how markets actually move</div></div>
  <div class="left">
    <div class="kicker">NEW EVERY WEEK</div>
    <div class="line">The market isn't magic.<br>It's <em>mechanics</em>.</div>
  </div>
</div>

<h2>C · THE FORMULA — dark physics identity</h2>
<div class="banner c"><div class="safe"><span>safe zone</span></div>
  <div class="inner">
    <div class="nm">MONEY <b>PHYSICS</b></div>
    <div class="formula"><b>risk</b> × <i>time</i> → reward</div>
    <div class="rule"></div>
  </div>
</div>

<h2>Avatar marks (200px shown; export 800px)</h2>
<div class="avatars">
  <div>
    <div class="av av1"><div class="orbit"></div><div class="mp">M<b>P</b></div></div>
    <div class="cap">1 · MP + orbit arc (physics)</div>
  </div>
  <div>
    <div class="av av2"><svg width="200" height="200" viewBox="0 0 200 200">
      <circle cx="100" cy="100" r="86" fill="none" stroke="{CHARCOAL}" stroke-width="9"/>
      <g stroke-width="8" stroke-linecap="round" fill="none">
        <path d="M55 122 A26 26 0 1 1 81 122" stroke="{COBALT}"/>
        <line x1="68" y1="122" x2="80" y2="102" stroke="{COBALT}"/>
        <path d="M87 122 A26 26 0 1 1 113 122" stroke="{SUNFLOWER}"/>
        <line x1="100" y1="122" x2="100" y2="98" stroke="{SUNFLOWER}"/>
        <path d="M119 122 A26 26 0 1 1 145 122" stroke="{CORAL}"/>
        <line x1="132" y1="122" x2="144" y2="110" stroke="{CORAL}"/>
      </g>
      <text x="100" y="158" text-anchor="middle" font-family="Inter,Arial" font-weight="800"
            font-size="17" fill="{CHARCOAL}" letter-spacing="2">MONEY PHYSICS</text>
    </svg></div>
    <div class="cap">2 · three dials (risk · reward · time)</div>
  </div>
  <div>
    <div class="av av3"><img src="{host_bust_b64()}"></div>
    <div class="cap">3 · host bust (from approved plate)</div>
  </div>
</div>
</body></html>"""

out = BUILD / "money-physics-brand-comps.html"
out.write_text(HTML, encoding="utf-8")
print("out:", out)
