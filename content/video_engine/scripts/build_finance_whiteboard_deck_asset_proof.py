"""Build a deck-asset whiteboard proof for the finance pilot.

This proof treats selected PPTX-derived crops as intentional evidence plates.
Their source text remains baked into the plate; HyperFrames controls the
whiteboard reveal, hand tracking, and scene timing around them.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from PIL import Image, ImageOps


REPO = Path(__file__).resolve().parents[3]
PILOT = REPO / "content/video_engine/projects/systems-and-blowups/pilots/current-bubble-mechanism"
PROOF_ID = "finance-whiteboard-deck-asset-proof-v1"
PROOF_ROOT = PILOT / PROOF_ID
ASSET_ROOT = PROOF_ROOT / "assets"
DECK_ASSET_ROOT = ASSET_ROOT / "deck"
SOURCE_ROOT = PROOF_ROOT / "source"
REVIEW_ROOT = PROOF_ROOT / "review"
RENDER_ROOT = PROOF_ROOT / "render"

P28_MANIFEST = PILOT.parent.parent / "sources/decks/deck-asset-manifest.json"
CANONICAL_AUDIO = PILOT / "audio/canonical/history_episode_1_master.mp3"
CANONICAL_WORDS = PILOT / "finance-whiteboard-code-drawn-proof-v1/source/canonical.words.json"
P24_NARRATION = PILOT / "finance-stealth-wealth-proof-v1/source/narration.locked.md"
P24_LEDGER = PILOT / "finance-stealth-wealth-proof-v1/source/claim-ledger.v1.json"
HAND_SOURCE = PILOT / "finance-whiteboard-asset-blend-proof-v1/assets/draw-hand-a-v1.png"

DURATION_S = 18.0
DELIVERY_FPS = 24
AUTHORING = {"width": 1920, "height": 1080, "fps": DELIVERY_FPS}
REVIEW = {"width": 1280, "height": 720, "fps": DELIVERY_FPS, "label": "review"}

ASSET_SPECS: list[dict[str, Any]] = [
    {
        "asset_id": "silicon-antidote-s02-valuation-bubble-v1",
        "filename": "valuation-bubble.png",
        "display_name": "S&P 500 valuation balloon",
        "x": 580,
        "y": 255,
        "width": 760,
        "height": 750,
        "rect": [-80, -80, 840, 830],
        "rows": 8,
        "stroke_width": 165,
        "start_s": 0.28,
        "duration_s": 0.88,
        "scene": "valuation",
    },
    {
        "asset_id": "silicon-antidote-s09-capacity-penalty-v1",
        "filename": "capacity-penalty.png",
        "display_name": "three-to-one capacity penalty",
        "x": 115,
        "y": 300,
        "width": 1120,
        "height": 620,
        "rect": [-80, -80, 1200, 700],
        "rows": 8,
        "stroke_width": 170,
        "start_s": 3.62,
        "duration_s": 1.25,
        "scene": "physical",
    },
    {
        "asset_id": "silicon-reality-gap-s07-hbm-stack-v1",
        "filename": "hbm-stack.png",
        "display_name": "HBM physical stack",
        "x": 1350,
        "y": 385,
        "width": 470,
        "height": 440,
        "rect": [-75, -75, 545, 515],
        "rows": 7,
        "stroke_width": 145,
        "start_s": 5.28,
        "duration_s": 0.94,
        "scene": "physical",
    },
    {
        "asset_id": "silicon-antidote-s10-ram-ageddon-v1",
        "filename": "ram-ageddon.png",
        "display_name": "RAM-ageddon supply-demand shock",
        "x": 230,
        "y": 285,
        "width": 1460,
        "height": 700,
        "rect": [-85, -85, 1550, 785],
        "rows": 8,
        "stroke_width": 175,
        "start_s": 11.98,
        "duration_s": 1.28,
        "scene": "choke-point",
    },
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def require_file(path: Path) -> None:
    if not path.is_file():
        raise FileNotFoundError(path)


def source_asset_index() -> tuple[dict[str, Any], dict[str, Any]]:
    require_file(P28_MANIFEST)
    manifest = json.loads(P28_MANIFEST.read_text(encoding="utf-8"))
    index = {asset["asset_id"]: asset for asset in manifest.get("assets", [])}
    missing = [spec["asset_id"] for spec in ASSET_SPECS if spec["asset_id"] not in index]
    if missing:
        raise RuntimeError(f"P28 manifest is missing selected asset IDs: {missing}")
    return manifest, index


def verify_source_inputs() -> dict[str, Any]:
    for path in (CANONICAL_AUDIO, CANONICAL_WORDS, P24_NARRATION, P24_LEDGER, HAND_SOURCE):
        require_file(path)
    manifest, index = source_asset_index()
    for spec in ASSET_SPECS:
        asset = index[spec["asset_id"]]
        source = REPO / "content/video_engine/projects/systems-and-blowups/sources/decks" / asset["path"]
        require_file(source)
        if sha256(source) != asset["sha256"]:
            raise RuntimeError(f"source asset hash mismatch for {spec['asset_id']}")
        if asset.get("render_eligible"):
            raise RuntimeError("review-only demo must not silently promote a source asset")
    return {
        "p28_manifest_sha256": sha256(P28_MANIFEST),
        "audio_sha256": sha256(CANONICAL_AUDIO),
        "hand_source_sha256": sha256(HAND_SOURCE),
        "selected_asset_ids": [spec["asset_id"] for spec in ASSET_SPECS],
        "asset_count": len(ASSET_SPECS),
        "source_manifest_id": manifest.get("manifest_id"),
    }


def stage_assets(source_receipts: dict[str, Any], asset_index: dict[str, Any]) -> list[dict[str, Any]]:
    DECK_ASSET_ROOT.mkdir(parents=True, exist_ok=True)
    staged: list[dict[str, Any]] = []
    source_root = REPO / "content/video_engine/projects/systems-and-blowups/sources/decks"
    for spec in ASSET_SPECS:
        source_asset = asset_index[spec["asset_id"]]
        source = source_root / source_asset["path"]
        destination = DECK_ASSET_ROOT / spec["filename"]
        shutil.copy2(source, destination)
        staged.append(
            {
                **spec,
                "path": f"assets/deck/{spec['filename']}",
                "sha256": sha256(destination),
                "source_asset_id": spec["asset_id"],
                "source_asset_path": source_asset["path"],
                "source_asset_sha256": source_asset["sha256"],
                "source_slide_id": source_asset["slide_id"],
                "context": source_asset["context"],
                "rights_state": source_asset["rights_state"],
                "review_state": source_asset["review_state"],
                "render_eligible": source_asset["render_eligible"],
                "asset_mode": "evidence_plate_with_baked_text",
            }
        )
    return staged


def html_document(arts: list[dict[str, Any]]) -> str:
    art_lookup = {art["source_asset_id"]: art for art in arts}

    def svg_asset(asset_id: str, mask_id: str, aria: str) -> str:
        art = art_lookup[asset_id]
        return f'''<div id="art-{html.escape(art["filename"].rsplit(".", 1)[0])}" class="artblock" style="left:{art["x"]}px;top:{art["y"]}px;width:{art["width"]}px;height:{art["height"]}px">
            <svg width="{art["width"]}" height="{art["height"]}" viewBox="0 0 {art["width"]} {art["height"]}" aria-label="{html.escape(aria)}">
              <defs><mask id="{mask_id}" maskUnits="userSpaceOnUse" x="0" y="0" width="{art["width"]}" height="{art["height"]}"><rect width="{art["width"]}" height="{art["height"]}" fill="#000" /></mask></defs>
              <image href="{html.escape(art["path"])}" x="0" y="0" width="{art["width"]}" height="{art["height"]}" mask="url(#{mask_id})" />
            </svg>
          </div>'''

    valuation = art_lookup["silicon-antidote-s02-valuation-bubble-v1"]
    capacity = art_lookup["silicon-antidote-s09-capacity-penalty-v1"]
    hbm = art_lookup["silicon-reality-gap-s07-hbm-stack-v1"]
    ram = art_lookup["silicon-antidote-s10-ram-ageddon-v1"]
    return f'''<!doctype html>
<html lang="en" data-resolution="landscape">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <title>Finance Whiteboard Deck Asset Blend Proof</title>
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      * {{ box-sizing: border-box; }}
      html, body {{ margin: 0; width: 1920px; height: 1080px; overflow: hidden; background: #f4eee1; }}
      @font-face {{ font-family: "WhiteboardSans"; src: local("Segoe Print"); font-style: normal; font-weight: 400 800; }}
      body {{ color: #252525; font-family: "WhiteboardSans", sans-serif; }}
      #stage {{ position: relative; width: 1920px; height: 1080px; overflow: hidden; background: #f4eee1; }}
      .plate, .scene {{ position: absolute; inset: 0; width: 100%; height: 100%; }}
      .plate {{ z-index: 0; }}
      .scene {{ z-index: 2; overflow: hidden; }}
      .scene-inner {{ position: absolute; inset: 0; }}
      .artblock {{ position: absolute; opacity: 0; mix-blend-mode: multiply; filter: drop-shadow(0 12px 12px rgba(53, 44, 31, .13)); }}
      .artblock svg {{ display: block; overflow: visible; }}
      .revealPath {{ fill: none; stroke: #fff; stroke-linecap: round; stroke-linejoin: round; }}
      .hand {{ position: absolute; left: 0; top: 0; z-index: 30; width: 320px; height: 480px; object-fit: contain; pointer-events: none; opacity: 0; visibility: hidden; transform-origin: 135px 428px; }}
      .lbl {{ position: absolute; z-index: 12; white-space: nowrap; padding-right: .22em; clip-path: inset(0 calc((1 - var(--rv, 0)) * 100%) 0 0); opacity: 0; font-weight: 700; letter-spacing: .015em; }}
      .topic {{ left: 94px; top: 92px; font-size: 68px; line-height: 1; color: #252525; letter-spacing: .02em; }}
      .kicker {{ left: 98px; top: 34px; font-size: 20px; line-height: 1; color: #4f5e5a; letter-spacing: .2em; }}
      .caption {{ left: 94px; bottom: 57px; font-size: 27px; line-height: 1; color: #252525; letter-spacing: .02em; }}
      .note {{ font-size: 31px; line-height: 1.05; color: #315b75; }}
      .source-note {{ position: absolute; left: 1515px; top: 1003px; z-index: 14; font-size: 16px; color: #4f5e5a; letter-spacing: .12em; }}
      .rule {{ fill: none; stroke: #252525; stroke-width: 6; stroke-linecap: round; stroke-linejoin: round; opacity: .42; }}
      .rule.coral {{ stroke: #c95d52; opacity: .9; }}
      .rule.blue {{ stroke: #709ab2; opacity: .85; }}
      .rule.green {{ stroke: #5c9b79; opacity: .85; }}
    </style>
  </head>
  <body>
    <div id="stage" data-composition-id="{PROOF_ID}" data-start="0" data-duration="18" data-width="1920" data-height="1080" data-fps="24">
      <svg id="plate" class="plate clip" data-start="0" data-duration="18" data-track-index="0" viewBox="0 0 1920 1080" aria-label="Warm woodblock whiteboard plate">
        <defs>
          <filter id="paper-grain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".78" numOctaves="2" seed="27" result="noise" /><feColorMatrix in="noise" type="saturate" values="0" result="gray" /><feComponentTransfer in="gray"><feFuncA type="table" tableValues="0 .18" /></feComponentTransfer></filter>
          <pattern id="woodblock-lines" width="160" height="160" patternUnits="userSpaceOnUse" patternTransform="rotate(-5)"><path d="M-30 34 Q55 5 190 28 M-40 72 Q74 44 210 68 M-18 112 Q65 86 182 110 M-36 148 Q60 130 210 150" fill="none" stroke="#8e806c" stroke-width="2" opacity=".16" /></pattern>
        </defs>
        <rect width="1920" height="1080" fill="#f4eee1" />
        <rect width="1920" height="1080" fill="#8b806f" filter="url(#paper-grain)" opacity=".34" />
        <rect width="1920" height="1080" fill="url(#woodblock-lines)" opacity=".54" />
        <path d="M68 84 Q310 54 544 79 M1370 79 Q1645 51 1854 83 M75 1004 Q320 1032 557 1008 M1372 1010 Q1637 1035 1850 1005" class="rule" />
        <path d="M74 100 L74 184 M74 100 L160 100 M1848 100 L1848 184 M1848 100 L1762 100 M74 980 L74 896 M74 980 L160 980 M1848 980 L1848 896 M1848 980 L1762 980" class="rule blue" />
        <path d="M93 270 Q520 252 960 270 T1824 266" class="rule coral" />
        <path d="M96 891 Q522 910 960 892 T1820 894" class="rule green" />
      </svg>

      <section id="scene-one" class="scene clip" data-start="0" data-duration="3" data-track-index="2">
        <div id="scene-one-inner" class="scene-inner">
          <div id="s1-kicker" class="lbl kicker" style="left:98px;top:34px;--rv:0">WHITEBOARD STUDY · VALUATION</div>
          <div id="s1-topic" class="lbl topic" style="--rv:0">THE WRONG BUBBLE?</div>
          {svg_asset(valuation["source_asset_id"], "mask-valuation-bubble", "S&P 500 valuation balloon")}
          <div id="s1-caption" class="lbl caption" style="--rv:0">The market may be labeling the wrong bubble.</div>
        </div>
      </section>

      <section id="scene-two" class="scene clip" data-start="3" data-duration="8.4" data-track-index="3">
        <div id="scene-two-inner" class="scene-inner">
          <div id="s2-kicker" class="lbl kicker" style="--rv:0">WHITEBOARD STUDY · PHYSICAL CONSTRAINT</div>
          <div id="s2-topic" class="lbl topic" style="--rv:0">THE PHYSICAL PENALTY.</div>
          {svg_asset(capacity["source_asset_id"], "mask-capacity-penalty", "Three-to-one HBM capacity penalty")}
          {svg_asset(hbm["source_asset_id"], "mask-hbm-stack", "HBM physical stack")}
          <div id="s2-note" class="lbl note" style="left:1230px;top:842px;font-size:27px;--rv:0">MORE STACKING. MORE CONSTRAINT.</div>
          <div id="s2-caption" class="lbl caption" style="--rv:0">The numbers look vertical. The physical constraint is real.</div>
        </div>
      </section>

      <section id="scene-three" class="scene clip" data-start="11.4" data-duration="6.6" data-track-index="4">
        <div id="scene-three-inner" class="scene-inner">
          <div id="s3-kicker" class="lbl kicker" style="--rv:0">WHITEBOARD STUDY · THE CHOKE POINT</div>
          <div id="s3-topic" class="lbl topic" style="--rv:0">LOOK UNDER THE CHART.</div>
          {svg_asset(ram["source_asset_id"], "mask-ram-ageddon", "RAM-ageddon supply and demand shock")}
          <div id="s3-caption" class="lbl caption" style="--rv:0">But underneath the chart is a product customers cannot get enough of.</div>
        </div>
      </section>

      <div class="source-note">SOURCE PLATES · SILICON ANTIDOTE / REALITY GAP</div>
      <audio id="voiceover" data-start="0" data-duration="18" data-track-index="1" src="assets/history_episode_1_master.mp3" preload="auto"></audio>
      <img id="handA" class="hand" src="assets/draw-hand-a-v1.png" alt="" aria-hidden="true" data-layout-allow-occlusion="true" />
      <img id="handB" class="hand" src="assets/draw-hand-b-v1.png" alt="" aria-hidden="true" data-layout-allow-occlusion="true" />
      <div id="handE" class="hand" aria-hidden="true" data-layout-allow-occlusion="true"></div>
    </div>

    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});
      const SVGNS = "http://www.w3.org/2000/svg";
      const handA = document.getElementById("handA");
      const handB = document.getElementById("handB");
      const handE = document.getElementById("handE");
      const NIB = {{ a: {{ x: 135, y: 428 }}, b: {{ x: 185, y: 428 }}, e: {{ x: 135, y: 428 }} }};
      const ARTS = {{
        valuationBubble: {{ x: {valuation["x"]}, y: {valuation["y"]}, k: 1 }},
        capacityPenalty: {{ x: {capacity["x"]}, y: {capacity["y"]}, k: 1 }},
        hbmStack: {{ x: {hbm["x"]}, y: {hbm["y"]}, k: 1 }},
        ramAgeddon: {{ x: {ram["x"]}, y: {ram["y"]}, k: 1 }},
      }};
      handA.style.transformOrigin = `${{NIB.a.x}}px ${{NIB.a.y}}px`;
      handB.style.transformOrigin = `${{NIB.b.x}}px ${{NIB.b.y}}px`;
      handE.style.transformOrigin = `${{NIB.e.x}}px ${{NIB.e.y}}px`;

      function serp(x0, y0, x1, y1, rows, sw) {{
        const ix0 = x0 + sw / 2; const ix1 = x1 - sw / 2;
        const iy0 = y0 + sw / 2; const iy1 = y1 - sw / 2;
        const step = (iy1 - iy0) / Math.max(1, rows - 1);
        let d = `M${{ix0}} ${{Math.round(iy0)}}`;
        for (let i = 0; i < rows; i += 1) {{ d += ` H${{i % 2 === 0 ? ix1 : ix0}}`; if (i < rows - 1) d += ` V${{Math.round(iy0 + step * (i + 1))}}`; }}
        return d;
      }}
      function buildGeometry(path, samples = 512) {{
        const length = path.getTotalLength() || 6000; const points = [];
        for (let i = 0; i <= samples; i += 1) {{ const point = path.getPointAtLength((i / samples) * length); points.push({{ x: point.x, y: point.y }}); }}
        return {{ length, points }};
      }}
      function pointAt(geometry, progress) {{
        const p = Math.min(1, Math.max(0, progress)); const scaled = p * (geometry.points.length - 1); const index = Math.min(geometry.points.length - 2, Math.floor(scaled)); const mix = scaled - index; const a = geometry.points[index]; const b = geometry.points[index + 1];
        return {{ x: a.x + (b.x - a.x) * mix, y: a.y + (b.y - a.y) * mix }};
      }}
      function setHandAt(geometry, artKey, progress) {{
        const art = ARTS[artKey]; const point = pointAt(geometry, progress); handA.style.opacity = 0; handB.style.opacity = 0; handE.style.opacity = 0;
        const ahead = pointAt(geometry, Math.min(1, progress + 0.01)); const backwards = ahead.x - point.x < -0.5; const hand = backwards ? handB : handA; const nib = backwards ? NIB.b : NIB.a;
        hand.style.visibility = "visible"; hand.style.opacity = 1; const jitter = Math.sin(progress * 34) * 2.2; hand.style.transform = `translate(${{art.x + point.x - nib.x}}px, ${{art.y + point.y - nib.y}}px) rotate(${{jitter}}deg)`;
      }}
      function hideHands(at) {{ tl.set([handA, handB, handE], {{ autoAlpha: 0 }}, at); }}
      function prepareChunk(maskId, id, artKey, rect, rows, sw) {{
        const path = document.createElementNS(SVGNS, "path"); path.setAttribute("id", id); path.setAttribute("class", "revealPath"); path.setAttribute("stroke-width", sw); path.setAttribute("d", serp(...rect, rows, sw)); document.getElementById(maskId).appendChild(path);
        const geometry = buildGeometry(path); path.style.strokeDasharray = `${{geometry.length}}`; path.style.strokeDashoffset = `${{geometry.length}}`; return {{ path, geometry, artKey }};
      }}
      function draw(chunkData, dur, at) {{
        const {{ path, geometry, artKey }} = chunkData; const len = geometry.length; const artblock = path.closest(".artblock"); tl.set(artblock, {{ autoAlpha: 1 }}, at - 0.05); tl.to(path, {{ strokeDashoffset: 0, duration: dur, ease: "none" }}, at); const proxy = {{ p: 0 }}; tl.to(proxy, {{ p: 1, duration: dur, ease: "none", onUpdate: () => setHandAt(geometry, artKey, proxy.p) }}, at); hideHands(at + dur + 0.05);
      }}
      function drawLbl(id, at, dur, width) {{
        const element = document.querySelector(id); const left = element.offsetLeft; const top = element.offsetTop; const fontSize = parseFloat(getComputedStyle(element).fontSize) || 70; const baseY = top + fontSize * 0.72;
        tl.set(id, {{ autoAlpha: 1, "--rv": 0 }}, at); tl.to(id, {{ "--rv": 1, duration: dur, ease: "none" }}, at); const proxy = {{ p: 0 }}; tl.to(proxy, {{ p: 1, duration: dur, ease: "none", onUpdate: () => {{ handA.style.opacity = 1; handA.style.visibility = "visible"; handB.style.opacity = 0; handB.style.visibility = "hidden"; const jitter = Math.sin(proxy.p * 40) * 1.6; const wobble = Math.sin(proxy.p * 26) * fontSize * 0.06; handA.style.transform = `translate(${{left + proxy.p * width - NIB.a.x}}px, ${{baseY + wobble - NIB.a.y}}px) rotate(${{jitter}}deg)`; }} }}, at); hideHands(at + dur + 0.05);
      }}
      function sceneFrame(innerId, start, duration) {{ const inner = document.getElementById(innerId); if (start > 0) tl.set(inner, {{ autoAlpha: 1 }}, Math.max(0, start - 0.12)); tl.to(inner, {{ autoAlpha: 0, duration: 0.12, ease: "none" }}, start + duration - 0.12); tl.set(inner, {{ autoAlpha: 0 }}, start + duration); }}

      const s1Valuation = prepareChunk("mask-valuation-bubble", "chunk-valuation-bubble", "valuationBubble", {json.dumps(valuation["rect"])}, {valuation["rows"]}, {valuation["stroke_width"]});
      const s2Capacity = prepareChunk("mask-capacity-penalty", "chunk-capacity-penalty", "capacityPenalty", {json.dumps(capacity["rect"])}, {capacity["rows"]}, {capacity["stroke_width"]});
      const s2Hbm = prepareChunk("mask-hbm-stack", "chunk-hbm-stack", "hbmStack", {json.dumps(hbm["rect"])}, {hbm["rows"]}, {hbm["stroke_width"]});
      const s3Ram = prepareChunk("mask-ram-ageddon", "chunk-ram-ageddon", "ramAgeddon", {json.dumps(ram["rect"])}, {ram["rows"]}, {ram["stroke_width"]});
      gsap.set([document.getElementById("scene-one-inner"), document.getElementById("scene-two-inner"), document.getElementById("scene-three-inner")], {{ autoAlpha: 0 }});
      gsap.set("#scene-one-inner", {{ autoAlpha: 1 }}); gsap.set([handA, handB, handE], {{ autoAlpha: 0 }});
      sceneFrame("scene-one-inner", 0, 3); sceneFrame("scene-two-inner", 3, 8.4); sceneFrame("scene-three-inner", 11.4, 6.6);

      drawLbl("#s1-kicker", 0.10, 0.28, 520); drawLbl("#s1-topic", 0.20, 0.55, 500); draw(s1Valuation, 0.88, 0.28); drawLbl("#s1-caption", 1.78, 0.55, 860);
      drawLbl("#s2-kicker", 2.92, 0.28, 520); drawLbl("#s2-topic", 3.12, 0.58, 620); draw(s2Capacity, 1.25, 3.62); draw(s2Hbm, 0.94, 5.28); drawLbl("#s2-note", 6.58, 0.52, 510); drawLbl("#s2-caption", 9.56, 0.60, 1120);
      drawLbl("#s3-kicker", 11.48, 0.28, 520); drawLbl("#s3-topic", 11.80, 0.62, 650); draw(s3Ram, 1.28, 11.98); drawLbl("#s3-caption", 15.28, 0.62, 1180);

      window.__timelines["{PROOF_ID}"] = tl;
    </script>
  </body>
</html>
'''


def stage_project(source_receipts: dict[str, Any]) -> dict[str, Any]:
    for directory in (PROOF_ROOT, SOURCE_ROOT, REVIEW_ROOT, RENDER_ROOT):
        directory.mkdir(parents=True, exist_ok=True)
    ASSET_ROOT.mkdir(parents=True, exist_ok=True)
    manifest, asset_index = source_asset_index()
    shutil.copy2(CANONICAL_AUDIO, ASSET_ROOT / "history_episode_1_master.mp3")
    shutil.copy2(HAND_SOURCE, ASSET_ROOT / "draw-hand-a-v1.png")
    with Image.open(HAND_SOURCE) as hand:
        ImageOps.mirror(hand).save(ASSET_ROOT / "draw-hand-b-v1.png", optimize=True)
    shutil.copy2(CANONICAL_WORDS, SOURCE_ROOT / "canonical.words.json")
    shutil.copy2(P24_NARRATION, SOURCE_ROOT / "narration.locked.md")
    shutil.copy2(P24_LEDGER, SOURCE_ROOT / "claim-ledger.v1.json")
    arts = stage_assets(source_receipts, asset_index)
    coverage_root = REVIEW_ROOT / "coverage"
    coverage_root.mkdir(parents=True, exist_ok=True)
    chunks = []
    for art in arts:
        coverage_path = coverage_root / art["filename"]
        with Image.open(DECK_ASSET_ROOT / art["filename"]) as source:
            source.convert("RGB").resize((art["width"], art["height"]), Image.Resampling.LANCZOS).save(coverage_path, optimize=True)
        chunks.append({
            "image": str(coverage_path),
            "rect": [-art["stroke_width"], -40, art["width"] + art["stroke_width"], art["height"] + 40],
            "sw": art["stroke_width"],
        })
    write_json(REVIEW_ROOT / "chunks.json", chunks)
    REVIEW_ROOT.joinpath("contact-sheet.html").write_text(
        "<!doctype html><meta charset='utf-8'><title>P28 deck asset proof contact sheet</title>"
        "<style>body{margin:0;padding:32px;background:#f5efe2;color:#252525;font:16px Georgia,serif}main{display:grid;grid-template-columns:repeat(2,1fr);gap:20px}figure{margin:0;background:#fffdf8;border:2px solid #252525;padding:12px}img{width:100%;height:280px;object-fit:contain;background:#f4eee1}figcaption{padding-top:8px;font:14px 'Segoe Print',sans-serif}</style>"
        + "<main>"
        + "".join(f"<figure><img src='../assets/deck/{html.escape(art['filename'])}' alt='{html.escape(art['display_name'])}'><figcaption>{html.escape(art['source_asset_id'])} · {html.escape(art['context']['what_it_is'])}</figcaption></figure>" for art in arts)
        + "</main>\n",
        encoding="utf-8",
    )
    proof_manifest = {
        "schema_version": "finance_whiteboard_deck_asset_manifest.v1",
        "proof_id": PROOF_ID,
        "renderer": "hyperframes:html-gsap",
        "duration_s": DURATION_S,
        "delivery_fps": DELIVERY_FPS,
        "authoring_profile": AUTHORING,
        "render_profile": REVIEW,
        "source_manifest": {"path": str(P28_MANIFEST.relative_to(REPO)).replace("\\", "/"), "sha256": source_receipts["p28_manifest_sha256"]},
        "canonical_audio": {"path": "assets/history_episode_1_master.mp3", "duration_s": DURATION_S, "sha256": source_receipts["audio_sha256"]},
        "hand": {"a_path": "assets/draw-hand-a-v1.png", "b_path": "assets/draw-hand-b-v1.png", "source_sha256": source_receipts["hand_source_sha256"], "nib": {"a": {"x": 135, "y": 428}, "b": {"x": 185, "y": 428}}},
        "art": arts,
        "provider_calls": 0,
        "pdf_assets": [],
        "asset_policy": "deck crops are review-only evidence plates with baked source text; not promoted reusable components",
        "status": "inputs_staged",
    }
    write_json(SOURCE_ROOT / "asset-binding.v1.json", {"schema_version": "finance_whiteboard_deck_asset_binding.v1", "proof_id": PROOF_ID, "source_manifest": source_receipts, "selected_assets": arts, "context_policy": "retain baked text and source context"})
    write_json(PROOF_ROOT / "proof-manifest.v1.json", proof_manifest)
    PROOF_ROOT.joinpath("index.html").write_text(html_document(arts), encoding="utf-8")
    return proof_manifest


def command(*args: str, cwd: Path | None = None) -> None:
    subprocess.run(list(args), cwd=cwd, check=True)


def render_project(manifest: dict[str, Any]) -> None:
    coverage = Path("C:/Users/Snipe/.codex/skills/whiteboard-explainer/scripts/coverage-check.py")
    command(sys.executable, str(coverage), str(REVIEW_ROOT / "chunks.json"))
    npx = shutil.which("npx")
    if not npx:
        raise RuntimeError("npx is required for HyperFrames rendering")
    command(npx, "--yes", "hyperframes@0.7.104", "check", cwd=PROOF_ROOT)
    authoring_output = RENDER_ROOT / "hf-authoring.mp4"
    output = RENDER_ROOT / "finance-whiteboard-deck-asset-proof.mp4"
    command(npx, "--yes", "hyperframes@0.7.104", "render", "-o", str(authoring_output), cwd=PROOF_ROOT)
    ffprobe = shutil.which("ffprobe")
    ffmpeg = shutil.which("ffmpeg")
    if not ffprobe or not ffmpeg:
        raise RuntimeError("ffprobe and ffmpeg are required for the review packet")
    command(ffmpeg, "-y", "-i", str(authoring_output), "-vf", "scale=1280:720:flags=lanczos", "-map", "0:v:0", "-map", "0:a?", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(output))
    probe = subprocess.run([ffprobe, "-v", "error", "-show_streams", "-show_format", "-of", "json", str(output)], check=True, capture_output=True, text=True)
    metadata = json.loads(probe.stdout)
    boundaries = REVIEW_ROOT / "boundaries"
    boundaries.mkdir(parents=True, exist_ok=True)
    for index, timestamp in enumerate((0.0, 0.5, 2.9, 3.1, 4.2, 5.3, 7.0, 10.8, 11.5, 12.5, 15.8, 17.9)):
        target = boundaries / f"boundary-{index + 1:02d}-{timestamp:05.1f}s.png"
        command(ffmpeg, "-y", "-ss", f"{timestamp:.3f}", "-i", str(output), "-frames:v", "1", "-update", "1", str(target))
    manifest["status"] = "review_render_complete"
    manifest["render"] = {"path": str(output.relative_to(PROOF_ROOT)).replace("\\", "/"), "authoring_path": str(authoring_output.relative_to(PROOF_ROOT)).replace("\\", "/"), "sha256": sha256(output), "ffprobe": metadata, "boundary_dir": str(boundaries.relative_to(PROOF_ROOT)).replace("\\", "/")}
    write_json(PROOF_ROOT / "proof-manifest.v1.json", manifest)
    write_json(REVIEW_ROOT / "watch-review-draft.v1.json", {"schema_version": "watch_review_draft.v1", "proof_id": PROOF_ID, "status": "draft", "review_required": True, "render_path": str(output.relative_to(PROOF_ROOT)).replace("\\", "/"), "checks": ["baked source text remains legible", "hand rides every active asset reveal", "plate remains stable with no camera drift", "selected asset IDs resolve to the P28 manifest", "deck crops are treated as evidence plates rather than promoted reusable components"]})


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--render", action="store_true", help="run HyperFrames check/render and create audit artifacts")
    args = parser.parse_args()
    receipts = verify_source_inputs()
    manifest = stage_project(receipts)
    if args.render:
        render_project(manifest)
    print(json.dumps({"proof_root": str(PROOF_ROOT), "status": manifest.get("status", "inputs_staged"), "duration_s": DURATION_S}, indent=2))


if __name__ == "__main__":
    main()
