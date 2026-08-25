"""Steel and Paper — scene-evidence v8: DMP deck evidence, sharp SVG charts,
word-punch captions, clean re-synth timings."""
from __future__ import annotations

import base64
import json
import subprocess
from pathlib import Path

REPO = Path(r"C:\Users\Snipe\Downloads\Outreach Program\.claude\worktrees\sweet-villani-1c3a16")
CLAIMS = REPO / "content/video_engine/projects/systems-and-blowups/review/claims"
W1 = CLAIMS / "steel-and-paper-plates-wave-1" / "objects"
W1B = CLAIMS / "steel-and-paper-plates-wave-1b" / "objects"
DMP = Path(r"C:\Users\Snipe\Downloads\Decoding_Market_Physics_slides")
SCRATCH = Path(__file__).parent
VO = SCRATCH / "steel-and-paper-vo"
BUILD = SCRATCH / "steel-and-paper-build"
CARDS = BUILD / "evidence-cards"
TEMPLATE = REPO / "docs/content-video-engine/samples/scene-evidence-player.template.html"
VO_SCENES = ["s01-open", "s02-engine", "s03-gap", "s04-pivot",
             "s05-reflection", "s06-close", "s07-story-close"]
ZERO = "0" * 64
CREAM, CHARCOAL, COBALT, TEAL, SUNFLOWER, CORAL = (
    "#F4E6C7", "#25313C", "#1769C2", "#178C83", "#F5B72E", "#ED6A4A")


def world(name: str) -> Path:
    for root in (W1B, W1):
        if (root / f"{name}.png").exists():
            return root / f"{name}.png"
    raise FileNotFoundError(name)


def scene_offsets() -> tuple[list[float], list[float]]:
    starts, durs, off = [], [], 0.0
    for i, name in enumerate(VO_SCENES, start=1):
        d = json.loads((VO / name / f"scene_{i}.words.json").read_text(encoding="utf-8"))
        starts.append(off)
        durs.append(d["duration_s"])
        off += d["duration_s"]
    return starts, durs


# ------------------------------------------------------------- sharp charts
def svg_divergence() -> str:
    data = json.loads((SCRATCH / "divergence-data.json").read_text(encoding="utf-8"))
    semis_v, hyper_v = data["semis"], data["hyper"]
    n = len(semis_v)
    top = max(semis_v)

    def pts(vals):
        return " ".join(
            f"{120 + i * 1140 / (n - 1):.0f},{640 - (v - 90) * 470 / (top - 90):.0f}"
            for i, v in enumerate(vals))

    semis_end = semis_v[-1] - 100
    hyper_end = hyper_v[-1] - 100
    sy = 640 - (semis_v[-1] - 90) * 470 / (top - 90)
    hy = 640 - (hyper_v[-1] - 90) * 470 / (top - 90)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1376 768">
<rect width="1376" height="768" fill="{CREAM}"/>
<rect x="10" y="10" width="1356" height="748" fill="none" stroke="{CHARCOAL}" stroke-width="6"/>
<text x="54" y="92" font-family="Inter,Arial" font-size="46" font-weight="800" fill="{CHARCOAL}">THE DIVERGENCE, ON LIVE TICKERS</text>
<text x="54" y="132" font-family="Inter,Arial" font-size="26" fill="{CHARCOAL}">Semiconductor ETF vs the four biggest AI spenders, equal weight, indexed to 100.</text>
<line x1="120" y1="660" x2="1260" y2="660" stroke="{CHARCOAL}" stroke-width="3"/>
<polyline points="{pts(hyper_v)}" fill="none" stroke="{CHARCOAL}" stroke-width="5" stroke-linejoin="round"/>
<polyline points="{pts(semis_v)}" fill="none" stroke="{CORAL}" stroke-width="7" stroke-linejoin="round"/>
<text x="1268" y="{sy + 8:.0f}" font-family="Inter,Arial" font-size="36" font-weight="800" fill="{CORAL}">+{semis_end:.0f}%</text>
<text x="1268" y="{sy + 40:.0f}" font-family="Inter,Arial" font-size="22" fill="{CHARCOAL}">SMH</text>
<text x="1268" y="{hy + 8:.0f}" font-family="Inter,Arial" font-size="30" font-weight="700" fill="{CHARCOAL}">+{hyper_end:.0f}%</text>
<text x="1268" y="{hy + 38:.0f}" font-family="Inter,Arial" font-size="20" fill="{CHARCOAL}">hyperscalers</text>
<text x="54" y="726" font-family="Inter,Arial" font-size="22" fill="{TEAL}">Data: Yahoo Finance daily closes, Apr 2025 – Aug 2026 · SMH vs AMZN/MSFT/GOOGL/META</text>
</svg>"""


def svg_ai_debt() -> str:
    bars = [("'20–'23 AVG / YR", 30, TEAL), ("'24–'25 TOTAL", 150, SUNFLOWER),
            ("2026 YTD", 244, CORAL)]
    parts = []
    x = 190
    for label, val, color in bars:
        h = val * 1.75
        parts.append(
            f'<rect x="{x}" y="{620 - h}" width="240" height="{h}" fill="{color}"/>'
            f'<text x="{x + 120}" y="{600 - h}" text-anchor="middle" '
            f'font-family="Inter,Arial" font-size="44" font-weight="800" fill="{CHARCOAL}">${val}B</text>'
            f'<text x="{x + 120}" y="668" text-anchor="middle" '
            f'font-family="Inter,Arial" font-size="24" font-weight="600" fill="{CHARCOAL}">{label}</text>')
        x += 350
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1376 768">
<rect width="1376" height="768" fill="{CREAM}"/>
<rect x="10" y="10" width="1356" height="748" fill="none" stroke="{CHARCOAL}" stroke-width="6"/>
<text x="54" y="92" font-family="Inter,Arial" font-size="46" font-weight="800" fill="{CHARCOAL}">BORROWING THE BUILDOUT</text>
<text x="54" y="132" font-family="Inter,Arial" font-size="26" fill="{CHARCOAL}">Hyperscaler AI debt raised — five times the prior pace, and rising.</text>
{''.join(parts)}
<text x="54" y="726" font-family="Inter,Arial" font-size="22" fill="{TEAL}">Recreated — Bravos Research debt-issuance figures</text>
</svg>"""


E1 = (REPO / "content/video_engine/projects/systems-and-blowups/review/claims"
      / "steel-paper-evidence-agent-e1/objects")


def _svg_shell(title: str, subtitle: str, body: str, source: str) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1376 768">
<rect width="1376" height="768" fill="{CREAM}"/>
<rect x="10" y="10" width="1356" height="748" fill="none" stroke="{CHARCOAL}" stroke-width="6"/>
<text x="54" y="92" font-family="Inter,Arial" font-size="46" font-weight="800" fill="{CHARCOAL}">{title}</text>
<text x="54" y="132" font-family="Inter,Arial" font-size="26" fill="{CHARCOAL}">{subtitle}</text>
<line x1="54" y1="158" x2="1322" y2="158" stroke="{CHARCOAL}" stroke-width="3"/>
{body}
<text x="54" y="726" font-family="Inter,Arial" font-size="22" fill="{TEAL}">{source}</text>
</svg>"""


def svg_arithmetic() -> str:
    body = f"""
<text x="688" y="330" text-anchor="middle" font-family="Inter,Arial" font-size="110" font-weight="800" fill="{COBALT}">20% &#215; 50% = &#8722;10%</text>
<text x="688" y="395" text-anchor="middle" font-family="Inter,Arial" font-size="32" fill="{CHARCOAL}">one bet's drawdown, priced straight into "the market"</text>
<text x="688" y="540" text-anchor="middle" font-family="Inter,Arial" font-size="72" font-weight="800" fill="{CORAL}">490 companies</text>
<text x="688" y="595" text-anchor="middle" font-family="Inter,Arial" font-size="32" fill="{CHARCOAL}">never get a vote</text>"""
    return _svg_shell("RUN THE ARITHMETIC", "Concentration turns one drawdown into everyone's drawdown.",
                      body, "Arithmetic on Bravos' attributed concentration figure")


def svg_steel_test() -> str:
    cols = [("1", "SCARCE?", "sold out, priced up,", "fought over &#8212; or abundant", COBALT),
            ("2", "CASH OR PAPER?", "growth funded by earnings,", "or by issuance", TEAL),
            ("3", "USED TOMORROW?", "if the hype died tonight,", "does it still get used", CORAL)]
    body = ""
    for i, (num, head, l1, l2, color) in enumerate(cols):
        x = 90 + i * 420
        body += f"""
<circle cx="{x + 60}" cy="270" r="52" fill="{color}"/>
<text x="{x + 60}" y="292" text-anchor="middle" font-family="Inter,Arial" font-size="60" font-weight="800" fill="{CREAM}">{num}</text>
<text x="{x + 60}" y="400" text-anchor="middle" font-family="Inter,Arial" font-size="40" font-weight="800" fill="{CHARCOAL}">{head}</text>
<text x="{x + 60}" y="450" text-anchor="middle" font-family="Inter,Arial" font-size="25" fill="{CHARCOAL}">{l1}</text>
<text x="{x + 60}" y="483" text-anchor="middle" font-family="Inter,Arial" font-size="25" fill="{CHARCOAL}">{l2}</text>"""
    body += f"""
<text x="688" y="610" text-anchor="middle" font-family="Inter,Arial" font-size="30" font-weight="700" fill="{CHARCOAL}">Steel answers scarce, cash, used. Paper answers abundant, issued, believed.</text>"""
    return _svg_shell("THE STEEL TEST", "Thirty seconds a holding. Run your top five tonight.",
                      body, "Steel and Paper &#183; the calculable take-home")


def svg_tripwires() -> str:
    body = f"""
<text x="100" y="300" font-family="Inter,Arial" font-size="76" font-weight="800" fill="{COBALT}">Fed above 5.5%</text>
<text x="100" y="352" font-family="Inter,Arial" font-size="30" fill="{CHARCOAL}">Bravos' flip condition &#8212; write it down</text>
<text x="100" y="510" font-family="Inter,Arial" font-size="76" font-weight="800" fill="{CORAL}">Memory: 2 quarters</text>
<text x="100" y="562" font-family="Inter,Arial" font-size="30" fill="{CHARCOAL}">contract prices falling while the buildout holds &#8212; ours, on camera</text>"""
    return _svg_shell("TWO TRIPWIRES, ON RECORD", "Both flip conditions, stated before they trigger.",
                      body, "Bravos Research + this channel's standing tell")


def b(label, value, tag, accent):
    return {"label": label, "value": value, "tag": tag, "accent": accent,
            "verbatim_in_document": True}


EVIDENCE = {
    "svg-divergence": {"title": "The Divergence, Live", "kind": "svg", "src": svg_divergence,
        "source": "Yahoo Finance daily closes · Apr 2025 – Aug 2026",
        "badges": [b("SEMIS (SMH) SINCE APR '25", "+158%", "YAHOO FINANCE", "coral"),
                    b("HYPERSCALER BASKET", "+46%", "SAME WINDOW", "sunflower")]},
    "svg-ai-debt": {"title": "Borrowing the Buildout", "kind": "svg", "src": svg_ai_debt,
        "source": "Recreated — Bravos Research debt figures",
        "badges": [b("AI DEBT '24–'25", "$150B", "5× PRIOR PACE", "sunflower"),
                    b("2026 YTD", "$244B", "AND RISING", "coral")]},
    "bravos-frame-railway": {"title": "Railway Stocks — Bravos Research", "kind": "dmp",
        "src": E1 / "evclip-railway-stocks-clean.png",
        "source": "Bravos Research video frame · verified clean-draw (evidence agent)",
        "badges": [b("RAILWAY STOCKS", "+100%", "IN 3 YEARS · 1843–1846", "sunflower")]},
    "bravos-frame-fed": {"title": "The Rate Trigger — Bravos Research", "kind": "dmp",  # era-correct frame @634s (pills + 2000 marker as focus)
        "src": BUILD / "evclip-fed-trigger-v2.png",
        "source": "Bravos Research video frame · verified clean-draw (evidence agent)",
        "badges": [b("FED, 1999", "4.5%", "", "sunflower"),
                    b("FED, 2000 — THE POP", "6.5%", "", "coral")]},
    "bravos-frame-uber": {"title": "The Uber Burn — Bravos Research", "kind": "dmp",
        "src": E1 / "evclip-uber-burn-clean.png",
        "source": "Bravos Research video frame · verified clean-draw (evidence agent)",
        "badges": []},
    "evchart-spy-rsp": {"title": "Cap-Weight vs Equal-Weight, Live", "kind": "dmp",
        "src": E1 / "evchart-concentration-ratio.png",
        "source": "Yahoo Finance, SPY/RSP, 2020-01-01 to 2026-08-24 (evidence agent)",
        "badges": [b("SPY vs EQUAL WEIGHT", "122.9", "INDEXED TO 100 - SINCE 2020", "coral")]},
    "card-index-arithmetic": {"title": "Run The Arithmetic", "kind": "svg",
        "src": svg_arithmetic,
        "source": "Arithmetic on the attributed figure",
        "badges": [b("'THE MARKET' TAKES", "−10%", "BEFORE A VOTE", "coral")]},
    "card-steel-test": {"title": "The Steel Test", "kind": "svg",
        "src": svg_steel_test,
        "source": "The calculable take-home", "badges": []},
    "card-tripwires": {"title": "Two Tripwires, On Record", "kind": "svg",
        "src": svg_tripwires,
        "source": "Both flip conditions, on record",
        "badges": [b("BRAVOS' LINE", "5.5%", "FED FUNDS", "cobalt"),
                    b("OUR LINE — MEMORY PRICES", "2 QTRS", "DOWN, CAPEX HOLDS", "coral")]},
    "dmp-s01": {"title": "Mechanics, Not Hype", "kind": "dmp",
        "src": DMP / "decoding-market-physics-s01.png",
        "source": "Decoding Market Physics · slide 01", "badges": []},
    "dmp-s02": {"title": "Index Physics, One Level Deeper", "kind": "dmp",
        "src": DMP / "decoding-market-physics-s02.png",
        "source": "Decoding Market Physics · slide 02", "badges": []},
    "dmp-s03": {"title": "Structural Digestion", "kind": "dmp",
        "src": DMP / "decoding-market-physics-s03.png",
        "source": "Decoding Market Physics · slide 03",
        "badges": [b("AFTER A 10X RUN", "50%", "ROUTINE DIGESTION", "cobalt")]},
    "dmp-s04": {"title": "8% of GDP, Physically Constrained", "kind": "dmp",
        "src": DMP / "decoding-market-physics-s04.png",
        "source": "Decoding Market Physics · slide 04",
        "badges": [b("HISTORIC PEAK LINE", "7%", "RAIL + INTERNET", "sunflower"),
                    b("AI TODAY", "8%", "OF US GDP", "coral")]},
    "dmp-s05": {"title": "Sold Out Through 2027", "kind": "dmp",
        "src": DMP / "decoding-market-physics-s05.png",
        "source": "Decoding Market Physics · slide 05",
        "badges": [b("HBM CAPACITY COMMITTED", "100%", "THROUGH 2027", "coral"),
                    b("OPERATING PROFIT", "$77B", "", "teal")]},
    "dmp-s06": {"title": "A Fifth of the Index", "kind": "dmp",
        "src": DMP / "decoding-market-physics-s06.png",
        "source": "Decoding Market Physics · slide 06",
        "badges": [b("TECH INFRA TODAY", "20%", "OF THE S&P 500", "coral"),
                    b("HISTORIC NORM", "2% to 4%", "", "teal")]},
    "dmp-s09": {"title": "Inelastic Markets", "kind": "dmp",
        "src": DMP / "decoding-market-physics-s09.png",
        "source": "Decoding Market Physics · slide 09",
        "badges": [b("EACH $1 OF OUTFLOW", "$5", "OF VALUE DESTROYED", "coral")]},
    "dmp-s11": {"title": "Mechanical Limits", "kind": "dmp",
        "src": DMP / "decoding-market-physics-s11.png",
        "source": "Decoding Market Physics · slide 11", "badges": []},
}

# windows: (scene_idx0, rel_start, rel_end|None=end, plate, kb, docks)
# dock: (evidence_id, slot, rel_enter, rel_exit, [rel_badge_at])
WINDOWS = [
    (0, 0.0, 10.0, "world-spike-desk-v1", (0.05, 14, -8), []),
    (0, 10.0, 40.0, "world-two-rooms-divergence-v1", (0.06, -18, 6),
     [("svg-divergence", 0, 13.5, 25.0, [16.0, 19.0])]),
    (0, 40.0, None, "world-workbench-triad-v1", (0.07, 10, 10), []),
    (1, 0.0, 35.0, "world-viaduct-train-rain-v1", (0.06, -14, -8),
     [("bravos-frame-railway", 0, 5.0, 15.0, [7.5, 10.0]),
      ("dmp-s04", 1, 21.0, 32.0, [23.5, 26.0])]),
    (1, 35.0, None, "world-two-rooms-divergence-v1", (0.05, 16, -6),
     [("bravos-frame-fed", 0, 39.0, 48.0, [42.0]),
      ("dmp-s01", 1, 56.0, 66.0, [])]),
    (2, 0.0, 33.0, "world-exhibition-hall-morning-v1", (0.07, -10, 12),
     [("bravos-frame-uber", 0, 4.5, 14.0, [7.5])]),
    (2, 33.0, None, "world-viaduct-train-rain-v1", (0.05, 12, 8),
     [("dmp-s03", 0, 38.0, 48.0, [40.5, 43.0])]),
    (3, 0.0, 30.0, "world-certificate-wall-v1", (0.06, -16, -10),
     [("dmp-s06", 0, 10.0, 22.0, [12.5, 15.5])]),
    (3, 30.0, None, "world-modern-certificate-v1", (0.06, 8, -12),
     [("card-index-arithmetic", 0, 33.0, 42.0, [35.5]),
      ("evchart-spy-rsp", 1, 43.0, 49.5, [45.0])]),
    (4, 0.0, 27.0, "world-molten-pour-v1", (0.04, -8, -6),
     [("dmp-s11", 0, 17.0, 25.0, [])]),
    (4, 27.0, 62.0, "world-circuit-terrain-v1", (0.06, 14, 6),
     [("dmp-s05", 0, 31.0, 43.0, [33.5, 36.5]),
      ("svg-ai-debt", 1, 48.0, 60.0, [50.5, 53.5])]),
    (4, 62.0, 100.0, "world-workbench-triad-v1", (0.05, -12, 8),
     [("card-steel-test", 0, 72.0, 85.0, [])]),
    (4, 100.0, None, "world-circuit-terrain-v1", (0.05, 10, -10),
     [("card-tripwires", 0, 107.0, 118.0, [109.5, 112.5]),
      ("dmp-s09", 1, 122.0, 133.0, [124.5])]),
    (5, 0.0, 24.6, "world-spike-certificate-ring-v2", (0.05, -10, 6), []),
    (5, 24.6, 44.6, "world-bankrupt-club-v1", (0.06, 12, -8),
     [("dmp-s02", 0, 28.0, 38.0, [])]),
    (5, 44.6, None, "world-spike-certificate-ring-v2", (0.04, -6, -6), []),
    (6, 0.0, None, "world-spike-rest-v2", (0.02, 0, 0), []),
]

CAPTION_JS_OLD = """    let line = null;
    for (const c of TL.captions) { if (t >= c.at && t < c.until) { line = c; break; } }
    cap.textContent = line ? line.text : "";
    const quiet = active.length > 0;
    cap.style.fontSize = quiet ? "33px" : "40px";
    cap.style.fontWeight = quiet ? "600" : "700";
    cap.style.opacity = line
      ? Math.min(clamp01((t - line.at) / 0.22), clamp01((line.until - t) / 0.18))
      : 0;"""

CAPTION_JS_NEW = """    let line = null, li = -1;
    for (let i = 0; i < TL.captions.length; i++) {
      const c = TL.captions[i];
      if (t >= c.at && t < c.until) { line = c; li = i; break; }
    }
    if (li !== cap._li) {
      cap._li = li;
      cap.innerHTML = line
        ? line.words.map(w => `<span class="cw${/\\d/.test(w.w) ? " num" : ""}" data-at="${w.at}">${w.w}</span>`).join(" ")
        : "";
    }
    if (line) {
      for (const s of cap.children) s.classList.toggle("on", t >= parseFloat(s.dataset.at) - 0.02);
    }
    const quiet = active.length > 0;
    cap.style.fontSize = quiet ? "33px" : "40px";
    cap.style.fontWeight = quiet ? "600" : "700";
    cap.style.opacity = line ? clamp01((line.until - t) / 0.18) : 0;"""

CAPTION_CSS = """
  .cw { display: inline-block; opacity: 0; transform: translateY(12px) scale(1.14);
        transition: opacity .15s ease-out, transform .22s cubic-bezier(.22,.9,.3,1); }
  .cw.on { opacity: 1; transform: none; }
  .cw.num { color: var(--sunflower); }
"""


def build_captions() -> list[dict]:
    caps, offset = [], 0.0
    for i, name in enumerate(VO_SCENES, start=1):
        data = json.loads((VO / name / f"scene_{i}.words.json").read_text(encoding="utf-8"))
        words = data["words"]
        for g in range(0, len(words), 4):
            grp = words[g:g + 4]
            caps.append({
                "at": round(offset + grp[0]["start_s"], 2),
                "until": round(offset + grp[-1]["end_s"] + 0.12, 2),
                "text": " ".join(w["w"] for w in grp),
                "words": [{"w": w["w"], "at": round(offset + w["start_s"], 2)} for w in grp],
            })
        offset += data["duration_s"]
    return caps


def main() -> int:
    starts, durs = scene_offsets()
    total = starts[-1] + durs[-1]
    scenes = []
    for wi, (si, rs, re_, plate, (ks, kx, ky), docks) in enumerate(WINDOWS, start=1):
        a = starts[si] + rs
        z = starts[si] + (re_ if re_ is not None else durs[si])
        scenes.append({
            "scene_id": f"p{wi:02d}",
            "world": {"asset_id": plate, "sha256": ZERO,
                       "ken_burns": {"scale": ks, "x": kx, "y": ky}},
            "exit": "wipe_left", "span": [round(a, 2), round(z, 2)],
            "docks": [{"slide": ev, "slot": slot,
                        "enter": round(starts[si] + en, 2),
                        "exit": round(starts[si] + ex, 2),
                        "badge_at": [round(starts[si] + t, 2) for t in bat]}
                       for ev, slot, en, ex, bat in docks],
        })
    evidence = {eid: {"title": s["title"],
                       "document": {"path": eid, "sha256": ZERO},
                       "source": s["source"], "badges": s["badges"], "match_score": 1.0}
                for eid, s in EVIDENCE.items()}
    tl = {"schema_version": "scene_evidence_timeline.v1",
          "episode_id": "steel-and-paper-scene-evidence-v8",
          "project_id": "systems-and-blowups",
          "narration": {"canonical_hash": ZERO, "words_path": "steel-and-paper/vo"},
          "captions": build_captions(), "evidence": evidence, "scenes": scenes}

    from PIL import Image
    uris: dict[str, str] = {}

    def enc_img(key: str, src: Path, width: int, q: int) -> None:
        im = Image.open(src).convert("RGB")
        if im.width > width:
            im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
        tmp = BUILD / f"_enc_{key}.jpg"
        im.save(tmp, quality=q, optimize=True)
        uris[key] = "data:image/jpeg;base64," + base64.b64encode(tmp.read_bytes()).decode()
        tmp.unlink()

    for plate in {w[3] for w in WINDOWS}:
        enc_img(plate, world(plate), 1150, 58)
    for eid, spec in EVIDENCE.items():
        if spec["kind"] == "svg":
            svg = spec["src"]()
            uris[eid] = "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()
        else:
            enc_img(eid, spec["src"], 900 if spec["kind"] == "dmp" else 760, 78)

    m4a = BUILD / "narration.m4a"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i",
                    str(VO / "steel-and-paper-full-vo.mp3"),
                    "-ac", "1", "-ar", "32000", "-c:a", "aac", "-b:a", "40k",
                    str(m4a)], check=True, capture_output=True)
    uris["__audio__"] = "data:audio/mp4;base64," + base64.b64encode(m4a.read_bytes()).decode()

    mins, secs = divmod(round(total), 60)
    clock = f"{mins}:{secs:02d}"
    html = TEMPLATE.read_text(encoding="utf-8")
    # finance-niche dock scale +20% (operator, 2026-08-25): charts must read
    # sleeker pills (operator, 2026-08-25): one-baseline badges, document fills the card
    html = html.replace(
        ".dock-head { margin-bottom: 9px; }",
        ".dock-head { margin-bottom: 6px; }")
    html = html.replace(
        ".dock-title { font-size: 25px;",
        ".dock-title { font-size: 21px;")
    html = html.replace(
        ".rail { display: grid; grid-template-columns: 1fr 1fr; gap: 9px; margin-top: 11px; }",
        ".rail { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; margin-top: 7px; }")
    html = html.replace(
        ".pill { background: rgba(37,49,60,.94); border-radius: 7px; padding: 8px 11px; display: flex; flex-direction: column;",
        ".pill { background: rgba(37,49,60,.92); border-radius: 6px; padding: 7px 11px; display: flex; flex-direction: row; align-items: baseline; gap: 8px; white-space: nowrap; overflow: hidden;")
    html = html.replace(
        ".pill-label { font-size: 13px; font-weight: 700; letter-spacing: .08em; color: #9fb4c4; }",
        ".pill-label { font-size: 12px; font-weight: 700; letter-spacing: .06em; color: #9fb4c4; }")
    html = html.replace(
        ".pill-row { display: flex; align-items: baseline; gap: 9px; margin-top: 3px; }",
        ".pill-row { display: flex; align-items: baseline; gap: 7px; margin-top: 0; }")
    html = html.replace(
        ".pill-num { font-size: 29px;",
        ".pill-num { font-size: 25px;")
    html = html.replace(
        ".pill-tag { font-size: 13px;",
        ".pill-tag { font-size: 12px;")

    html = html.replace(
        "position: absolute; top: 226px; width: 720px;",
        "position: absolute; top: 186px; width: 864px;")
    html = html.replace("#dock-1.solo { width: 880px; top: 196px; }",
                         "#dock-1.solo { width: 1056px; top: 156px; }")
    html = html.replace("#dock-1.solo.side-r { left: 940px; }",
                         "#dock-1.solo.side-r { left: 820px; }")
    html = html.replace("#dock-1 { left: 136px; } #dock-2 { left: 1064px; }",
                         "#dock-1 { left: 70px; } #dock-2 { left: 990px; }")

    html = html.replace("Current Bubble v4", "Steel and Paper — scene-evidence v8")
    html = html.replace(
        "<b>Current Bubble &mdash; five minute v4</b> &middot; scene-evidence lane &middot; generated from timeline.v4.json",
        "<b>Steel and Paper</b> &middot; scene-evidence lane &middot; review build v8")
    html = html.replace('max="300"', f'max="{total:.2f}"')
    html = html.replace("const DUR = 300;", f"const DUR = {total:.2f};")
    html = html.replace("0:00 / 5:00", f"0:00 / {clock}")
    html = html.replace("/ 5:00`", f"/ {clock}`")
    assert CAPTION_JS_OLD in html, "caption JS anchor missing"
    html = html.replace(CAPTION_JS_OLD, CAPTION_JS_NEW)
    html = html.replace("  #bar {", CAPTION_CSS + "\n  #bar {")
    html = html.replace("{{TIMELINE}}", json.dumps(tl))
    html = html.replace("{{URIS}}", json.dumps(uris))
    out = BUILD / "steel-and-paper-scene-evidence-v8.html"
    out.write_text(html, encoding="utf-8")

    docks = [d for sc in scenes for d in sc["docks"]]
    spans = sorted((d["enter"], d["exit"]) for d in docks)
    cursor = worst = 0.0
    for a, z in spans:
        worst = max(worst, a - cursor)
        cursor = max(cursor, z)
    worst = max(worst, total - cursor)
    print(f"total={total:.1f}s scenes={len(scenes)} docks={len(docks)} "
          f"captions={len(tl['captions'])} badged={sum(1 for e in evidence.values() if e['badges'])}")
    print(f"longest bare plate: {worst:.1f}s")
    print(f"payload {sum(len(v) for v in uris.values()) / 1024 / 1024:.1f} MB")
    print("out:", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
