"""Build a woodblock-world + whiteboard-evidence blend proof.

The generated woodblock kit is the persistent story world. The whiteboard
easel and analyst are local world props; selected NotebookLM/PPTX-derived
plates enter only on the board as source-backed evidence surfaces.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from PIL import Image, ImageOps


SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))
import build_finance_whiteboard_deck_asset_proof as deck_proof  # noqa: E402


REPO = deck_proof.REPO
PILOT = deck_proof.PILOT
PROOF_ID = "finance-whiteboard-world-blend-proof-v1"
PROOF_ROOT = PILOT / PROOF_ID
ASSET_ROOT = PROOF_ROOT / "assets"
DECK_ASSET_ROOT = ASSET_ROOT / "deck"
WORLD_ASSET_ROOT = ASSET_ROOT / "world"
SOURCE_ROOT = PROOF_ROOT / "source"
REVIEW_ROOT = PROOF_ROOT / "review"
RENDER_ROOT = PROOF_ROOT / "render"

P28_MANIFEST = deck_proof.P28_MANIFEST
CANONICAL_AUDIO = deck_proof.CANONICAL_AUDIO
CANONICAL_WORDS = deck_proof.CANONICAL_WORDS
P24_NARRATION = deck_proof.P24_NARRATION
P24_LEDGER = deck_proof.P24_LEDGER
HAND_SOURCE = deck_proof.HAND_SOURCE

DURATION_S = 18.0
DELIVERY_FPS = 24
AUTHORING = {"width": 1920, "height": 1080, "fps": DELIVERY_FPS}
REVIEW = {"width": 1280, "height": 720, "fps": DELIVERY_FPS, "label": "review"}

WORLD_SOURCES = [
    {
        "asset_id": "woodblock-finance-analyst-v1",
        "source": REPO / "content/video_engine/projects/systems-and-blowups/assets/generated/cutouts/actor-institutional-analyst-v1.png",
        "path": "assets/world/finance-analyst-v1.png",
        "kind": "world_character",
        "x": 1415,
        "y": 285,
        "width": 390,
    },
    {
        "asset_id": "woodblock-whiteboard-easel-v2",
        "source": REPO / "content/video_engine/projects/systems-and-blowups/assets/generated/cutouts/whiteboard-easel-v2.png",
        "path": "assets/world/whiteboard-easel-v2.png",
        "kind": "world_evidence_surface",
        "x": 35,
        "y": 38,
        "width": 1300,
    },
]

DECK_LAYOUTS = [
    {
        "asset_id": "silicon-antidote-s02-valuation-bubble-v1",
        "filename": "valuation-bubble.png",
        "display_name": "S&P 500 valuation balloon",
        "x": 465,
        "y": 245,
        "width": 405,
        "height": 400,
        "rect": [-55, -55, 460, 455],
        "rows": 8,
        "stroke_width": 105,
        "start_s": 0.28,
        "duration_s": 0.88,
        "scene": "valuation",
    },
    {
        "asset_id": "silicon-antidote-s09-capacity-penalty-v1",
        "filename": "capacity-penalty.png",
        "display_name": "three-to-one capacity penalty",
        "x": 275,
        "y": 235,
        "width": 750,
        "height": 415,
        "rect": [-65, -65, 815, 480],
        "rows": 8,
        "stroke_width": 110,
        "start_s": 3.62,
        "duration_s": 1.25,
        "scene": "physical",
    },
    {
        "asset_id": "silicon-reality-gap-s07-hbm-stack-v1",
        "filename": "hbm-stack.png",
        "display_name": "HBM physical stack",
        "x": 965,
        "y": 405,
        "width": 190,
        "height": 178,
        "rect": [-45, -45, 235, 223],
        "rows": 7,
        "stroke_width": 78,
        "start_s": 5.28,
        "duration_s": 0.94,
        "scene": "physical",
    },
    {
        "asset_id": "silicon-antidote-s10-ram-ageddon-v1",
        "filename": "ram-ageddon.png",
        "display_name": "RAM-ageddon supply-demand shock",
        "x": 275,
        "y": 245,
        "width": 820,
        "height": 394,
        "rect": [-65, -65, 885, 459],
        "rows": 8,
        "stroke_width": 110,
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


def verify_inputs() -> dict[str, Any]:
    for path in (CANONICAL_AUDIO, CANONICAL_WORDS, P24_NARRATION, P24_LEDGER, HAND_SOURCE, P28_MANIFEST):
        require_file(path)
    for spec in WORLD_SOURCES:
        require_file(spec["source"])
    _, asset_index = deck_proof.source_asset_index()
    source_root = REPO / "content/video_engine/projects/systems-and-blowups/sources/decks"
    for spec in DECK_LAYOUTS:
        asset = asset_index.get(spec["asset_id"])
        if not asset:
            raise RuntimeError(f"P28 manifest is missing {spec['asset_id']}")
        source = source_root / asset["path"]
        require_file(source)
        if sha256(source) != asset["sha256"]:
            raise RuntimeError(f"P28 source hash mismatch for {spec['asset_id']}")
        if asset.get("render_eligible"):
            raise RuntimeError("world blend proof must not silently promote review-only deck assets")
    return {
        "p28_manifest_sha256": sha256(P28_MANIFEST),
        "audio_sha256": sha256(CANONICAL_AUDIO),
        "hand_source_sha256": sha256(HAND_SOURCE),
        "world_asset_ids": [spec["asset_id"] for spec in WORLD_SOURCES],
        "deck_asset_ids": [spec["asset_id"] for spec in DECK_LAYOUTS],
    }


def stage_world() -> list[dict[str, Any]]:
    WORLD_ASSET_ROOT.mkdir(parents=True, exist_ok=True)
    staged = []
    for spec in WORLD_SOURCES:
        destination = PROOF_ROOT / spec["path"]
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(spec["source"], destination)
        staged.append({**spec, "path": spec["path"], "sha256": sha256(destination), "source": str(spec["source"])})
    return staged


def stage_deck_assets(asset_index: dict[str, Any]) -> list[dict[str, Any]]:
    DECK_ASSET_ROOT.mkdir(parents=True, exist_ok=True)
    source_root = REPO / "content/video_engine/projects/systems-and-blowups/sources/decks"
    staged = []
    for spec in DECK_LAYOUTS:
        source_asset = asset_index[spec["asset_id"]]
        source = source_root / source_asset["path"]
        destination = DECK_ASSET_ROOT / spec["filename"]
        shutil.copy2(source, destination)
        staged.append({
            **spec,
            "path": f"assets/deck/{spec['filename']}",
            "sha256": sha256(destination),
            "source_asset_id": source_asset["asset_id"],
            "source_asset_path": source_asset["path"],
            "source_asset_sha256": source_asset["sha256"],
            "source_slide_id": source_asset["slide_id"],
            "context": source_asset["context"],
            "rights_state": source_asset["rights_state"],
            "review_state": source_asset["review_state"],
            "render_eligible": source_asset["render_eligible"],
            "asset_mode": "evidence_plate_on_world_whiteboard",
        })
    return staged


def svg_asset(art: dict[str, Any], mask_id: str, aria: str) -> str:
    return f'''<div id="art-{html.escape(art["filename"].rsplit(".", 1)[0])}" class="artblock" style="left:{art["x"]}px;top:{art["y"]}px;width:{art["width"]}px;height:{art["height"]}px">
          <svg width="{art["width"]}" height="{art["height"]}" viewBox="0 0 {art["width"]} {art["height"]}" aria-label="{html.escape(aria)}">
            <defs><mask id="{mask_id}" maskUnits="userSpaceOnUse" x="0" y="0" width="{art["width"]}" height="{art["height"]}"><rect width="{art["width"]}" height="{art["height"]}" fill="#000" /></mask></defs>
            <image href="{html.escape(art["path"])}" x="0" y="0" width="{art["width"]}" height="{art["height"]}" mask="url(#{mask_id})" />
          </svg>
        </div>'''


def html_document(arts: list[dict[str, Any]], worlds: list[dict[str, Any]]) -> str:
    lookup = {art["source_asset_id"]: art for art in arts}
    valuation = lookup["silicon-antidote-s02-valuation-bubble-v1"]
    capacity = lookup["silicon-antidote-s09-capacity-penalty-v1"]
    hbm = lookup["silicon-reality-gap-s07-hbm-stack-v1"]
    ram = lookup["silicon-antidote-s10-ram-ageddon-v1"]
    world_lookup = {item["asset_id"]: item for item in worlds}
    actor = world_lookup["woodblock-finance-analyst-v1"]
    easel = world_lookup["woodblock-whiteboard-easel-v2"]
    return f'''<!doctype html>
<html lang="en" data-resolution="landscape">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <title>Finance Whiteboard World Blend Proof</title>
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      * {{ box-sizing: border-box; }}
      html, body {{ margin:0; width:1920px; height:1080px; overflow:hidden; background:#e7d8be; }}
      @font-face {{ font-family:"WhiteboardSans"; src:local("Segoe Print"); font-style:normal; font-weight:400 800; }}
      @font-face {{ font-family:"WorldSerif"; src:local("Georgia"); font-style:normal; font-weight:400 800; }}
      body {{ color:#25252a; font-family:"WhiteboardSans", sans-serif; }}
      #stage {{ position:relative; width:1920px; height:1080px; overflow:hidden; background:#e7d8be; }}
      #world {{ position:absolute; inset:0; z-index:0; }}
      #world-plate {{ position:absolute; inset:0; width:100%; height:100%; }}
      .world-prop {{ position:absolute; z-index:3; object-fit:contain; }}
      .analyst {{ z-index:7; filter:drop-shadow(0 18px 12px rgba(50,38,22,.2)); }}
      .easel {{ z-index:4; }}
      .world-sign {{ position:absolute; z-index:9; left:100px; top:75px; padding:15px 26px 12px; color:#f5e9d0; background:#243d5e; border:5px solid #d59c41; box-shadow:7px 7px 0 #bc5a46; font:700 28px WorldSerif,serif; letter-spacing:.08em; transform:rotate(-1deg); }}
      .world-desk {{ position:absolute; z-index:2; left:0; right:0; top:925px; height:155px; background:#315c72; border-top:12px solid #b96548; box-shadow:0 -10px 0 rgba(45,42,34,.22); }}
      .world-desk::after {{ content:""; position:absolute; left:0; right:0; top:26px; height:5px; background:#e2c590; opacity:.7; }}
      .scene {{ position:absolute; inset:0; z-index:12; overflow:hidden; }}
      .scene-inner {{ position:absolute; inset:0; }}
      .artblock {{ position:absolute; opacity:0; z-index:14; background:#fffdf8; border:5px solid #f7efdf; box-shadow:0 13px 16px rgba(42,35,26,.24); mix-blend-mode:multiply; }}
      .artblock svg {{ display:block; overflow:visible; }}
      .revealPath {{ fill:none; stroke:#fff; stroke-linecap:round; stroke-linejoin:round; }}
      .hand {{ position:absolute; left:0; top:0; z-index:40; width:320px; height:480px; object-fit:contain; pointer-events:none; opacity:0; visibility:hidden; transform-origin:135px 428px; }}
      .lbl {{ position:absolute; z-index:25; white-space:nowrap; padding-right:.22em; clip-path:inset(0 calc((1 - var(--rv,0)) * 100%) 0 0); opacity:0; font-weight:700; letter-spacing:.015em; }}
      .board-kicker {{ left:310px; top:130px; color:#1e2827; background:#f7efdf; padding:3px 8px 2px; font-size:18px; line-height:1.4; letter-spacing:.2em; }}
      .board-title {{ left:310px; top:172px; font-size:50px; line-height:1.2; color:#171b1b; background:#f7efdf; padding:4px 9px 3px; }}
      .board-caption {{ left:305px; top:690px; font-size:24px; line-height:1.35; color:#171b1b; background:#f7efdf; padding:4px 8px 3px; }}
      .board-note {{ left:940px; top:315px; font-size:22px; line-height:1.35; color:#1e3e50; background:#f7efdf; padding:4px 7px 3px; transform:rotate(-2deg); }}
      .source-tag {{ position:absolute; z-index:26; left:985px; top:645px; color:#233a35; background:#f7efdf; padding:3px 6px; font-size:14px; letter-spacing:.13em; }}
      .rule {{ fill:none; stroke:#25252a; stroke-width:6; stroke-linecap:round; opacity:.5; }}
      .rule.blue {{ stroke:#6f9bb3; }}
      .rule.coral {{ stroke:#c95d52; }}
    </style>
  </head>
  <body>
    <div id="stage" data-composition-id="{PROOF_ID}" data-start="0" data-duration="18" data-width="1920" data-height="1080" data-fps="24">
      <div id="world">
        <svg id="world-plate" viewBox="0 0 1920 1080" aria-label="Warm woodblock research room">
          <defs>
            <filter id="paper-grain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".72" numOctaves="2" seed="29" result="noise"/><feColorMatrix in="noise" type="saturate" values="0" result="gray"/><feComponentTransfer in="gray"><feFuncA type="table" tableValues="0 .15"/></feComponentTransfer></filter>
            <pattern id="grain-lines" width="180" height="150" patternUnits="userSpaceOnUse" patternTransform="rotate(-4)"><path d="M-30 35 Q65 8 210 31 M-40 76 Q75 49 230 72 M-15 118 Q66 91 205 112" fill="none" stroke="#8f7358" stroke-width="2" opacity=".16"/></pattern>
          </defs>
          <rect width="1920" height="1080" fill="#e7d8be"/>
          <rect width="1920" height="1080" fill="#8b765d" filter="url(#paper-grain)" opacity=".34"/>
          <rect width="1920" height="1080" fill="url(#grain-lines)" opacity=".68"/>
          <path d="M45 205 Q360 176 660 205 T1290 200" class="rule"/>
          <path d="M56 230 L56 290 M56 230 L120 230 M1290 230 L1290 290 M1290 230 L1226 230" class="rule blue"/>
          <path d="M1410 160 Q1650 145 1875 175" class="rule coral"/>
          <path d="M1425 185 L1425 245 M1870 192 L1870 252" class="rule blue"/>
        </svg>
        <div class="world-sign">THE RESEARCH DESK</div>
        <div class="world-desk"></div>
        <img class="world-prop easel" src="{html.escape(easel["path"])}" alt="Woodblock whiteboard easel" style="left:{easel["x"]}px;top:{easel["y"]}px;width:{easel["width"]}px" />
        <img class="world-prop analyst" src="{html.escape(actor["path"])}" alt="Woodblock institutional analyst" style="left:{actor["x"]}px;top:{actor["y"]}px;width:{actor["width"]}px" />
      </div>

      <section id="scene-one" class="scene clip" data-start="0" data-duration="3" data-track-index="2">
        <div id="scene-one-inner" class="scene-inner">
          <div id="s1-kicker" class="lbl board-kicker" style="--rv:0">NOTEBOOK EVIDENCE · VALUATION</div>
          <div id="s1-title" class="lbl board-title" style="--rv:0">THE WRONG BUBBLE?</div>
          {svg_asset(valuation, "mask-valuation-bubble", "NotebookLM valuation evidence plate")}
          <div id="s1-caption" class="lbl board-caption" style="--rv:0">The market may be labeling the wrong bubble.</div>
          <div class="source-tag">S02 · SILICON ANTIDOTE</div>
        </div>
      </section>

      <section id="scene-two" class="scene clip" data-start="3" data-duration="8.4" data-track-index="3">
        <div id="scene-two-inner" class="scene-inner">
          <div id="s2-kicker" class="lbl board-kicker" style="--rv:0">NOTEBOOK EVIDENCE · PHYSICAL CONSTRAINT</div>
          <div id="s2-title" class="lbl board-title" style="--rv:0">THE PHYSICAL PENALTY.</div>
          {svg_asset(capacity, "mask-capacity-penalty", "NotebookLM capacity penalty evidence plate")}
          {svg_asset(hbm, "mask-hbm-stack", "NotebookLM HBM stack evidence plate")}
          <div id="s2-note" class="lbl board-note" style="--rv:0">THE BOARD EXPLAINS THE WORLD.</div>
          <div id="s2-caption" class="lbl board-caption" style="--rv:0">The physical constraint is underneath the market story.</div>
          <div class="source-tag">S09 + S07 · ANTI­DOTE / REALITY GAP</div>
        </div>
      </section>

      <section id="scene-three" class="scene clip" data-start="11.4" data-duration="6.6" data-track-index="4">
        <div id="scene-three-inner" class="scene-inner">
          <div id="s3-kicker" class="lbl board-kicker" style="--rv:0">NOTEBOOK EVIDENCE · CHOKE POINT</div>
          <div id="s3-title" class="lbl board-title" style="--rv:0">LOOK UNDER THE CHART.</div>
          {svg_asset(ram, "mask-ram-ageddon", "NotebookLM RAM-ageddon evidence plate")}
          <div id="s3-caption" class="lbl board-caption" style="--rv:0">But underneath the chart is a product customers cannot get enough of.</div>
          <div class="source-tag">S10 · SILICON ANTIDOTE</div>
        </div>
      </section>

      <audio id="voiceover" data-start="0" data-duration="18" data-track-index="1" src="assets/history_episode_1_master.mp3" preload="auto"></audio>
      <img id="handA" class="hand" src="assets/draw-hand-a-v1.png" alt="" aria-hidden="true" data-layout-allow-occlusion="true" />
      <img id="handB" class="hand" src="assets/draw-hand-b-v1.png" alt="" aria-hidden="true" data-layout-allow-occlusion="true" />
      <div id="handE" class="hand" aria-hidden="true" data-layout-allow-occlusion="true"></div>
    </div>

    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused:true }});
      const SVGNS = "http://www.w3.org/2000/svg";
      const handA = document.getElementById("handA"); const handB = document.getElementById("handB"); const handE = document.getElementById("handE");
      const NIB = {{ a:{{x:135,y:428}}, b:{{x:185,y:428}}, e:{{x:135,y:428}} }};
      const ARTS = {{ valuationBubble:{{x:{valuation["x"]},y:{valuation["y"]}}}, capacityPenalty:{{x:{capacity["x"]},y:{capacity["y"]}}}, hbmStack:{{x:{hbm["x"]},y:{hbm["y"]}}}, ramAgeddon:{{x:{ram["x"]},y:{ram["y"]}}} }};
      handA.style.transformOrigin = `${{NIB.a.x}}px ${{NIB.a.y}}px`; handB.style.transformOrigin = `${{NIB.b.x}}px ${{NIB.b.y}}px`; handE.style.transformOrigin = `${{NIB.e.x}}px ${{NIB.e.y}}px`;
      function serp(x0,y0,x1,y1,rows,sw) {{ const ix0=x0+sw/2, ix1=x1-sw/2, iy0=y0+sw/2, iy1=y1-sw/2, step=(iy1-iy0)/Math.max(1,rows-1); let d=`M${{ix0}} ${{Math.round(iy0)}}`; for(let i=0;i<rows;i+=1){{ d+=` H${{i%2===0?ix1:ix0}}`; if(i<rows-1)d+=` V${{Math.round(iy0+step*(i+1))}}`; }} return d; }}
      function buildGeometry(path,samples=512) {{ const length=path.getTotalLength()||6000, points=[]; for(let i=0;i<=samples;i+=1){{ const p=path.getPointAtLength(i/samples*length); points.push({{x:p.x,y:p.y}}); }} return {{length,points}}; }}
      function pointAt(g,progress) {{ const p=Math.min(1,Math.max(0,progress)), scaled=p*(g.points.length-1), index=Math.min(g.points.length-2,Math.floor(scaled)), mix=scaled-index, a=g.points[index], b=g.points[index+1]; return {{x:a.x+(b.x-a.x)*mix,y:a.y+(b.y-a.y)*mix}}; }}
      function setHandAt(g,key,progress) {{ const art=ARTS[key], point=pointAt(g,progress), ahead=pointAt(g,Math.min(1,progress+.01)), backwards=ahead.x-point.x<-.5, hand=backwards?handB:handA, nib=backwards?NIB.b:NIB.a; handA.style.opacity=0; handB.style.opacity=0; handE.style.opacity=0; hand.style.visibility="visible"; hand.style.opacity=1; hand.style.transform=`translate(${{art.x+point.x-nib.x}}px,${{art.y+point.y-nib.y}}px) rotate(${{Math.sin(progress*34)*2.2}}deg)`; }}
      function hideHands(at) {{ tl.set([handA,handB,handE],{{autoAlpha:0}},at); }}
      function prepareChunk(maskId,id,artKey,rect,rows,sw) {{ const path=document.createElementNS(SVGNS,"path"); path.setAttribute("id",id); path.setAttribute("class","revealPath"); path.setAttribute("stroke-width",sw); path.setAttribute("d",serp(...rect,rows,sw)); document.getElementById(maskId).appendChild(path); const geometry=buildGeometry(path); path.style.strokeDasharray=`${{geometry.length}}`; path.style.strokeDashoffset=`${{geometry.length}}`; return {{path,geometry,artKey}}; }}
      function draw(chunk,dur,at) {{ const {{path,geometry,artKey}}=chunk, len=geometry.length, block=path.closest(".artblock"); tl.set(block,{{autoAlpha:1}},at-.05); tl.to(path,{{strokeDashoffset:0,duration:dur,ease:"none"}},at); const proxy={{p:0}}; tl.to(proxy,{{p:1,duration:dur,ease:"none",onUpdate:()=>setHandAt(geometry,artKey,proxy.p)}},at); hideHands(at+dur+.05); }}
      function drawLbl(id,at,dur,width) {{ const el=document.querySelector(id), left=el.offsetLeft, top=el.offsetTop, fontSize=parseFloat(getComputedStyle(el).fontSize)||50, baseY=top+fontSize*.72; tl.set(id,{{autoAlpha:1,"--rv":0}},at); tl.to(id,{{"--rv":1,duration:dur,ease:"none"}},at); const proxy={{p:0}}; tl.to(proxy,{{p:1,duration:dur,ease:"none",onUpdate:()=>{{handA.style.opacity=1;handA.style.visibility="visible";handB.style.opacity=0;handB.style.visibility="hidden";handA.style.transform=`translate(${{left+proxy.p*width-NIB.a.x}}px,${{baseY+Math.sin(proxy.p*26)*fontSize*.06-NIB.a.y}}px) rotate(${{Math.sin(proxy.p*40)*1.6}}deg)`;}}}},at); hideHands(at+dur+.05); }}
      function sceneFrame(id,start,duration) {{ const inner=document.getElementById(id); if(start>0)tl.set(inner,{{autoAlpha:1}},Math.max(0,start-.12)); tl.to(inner,{{autoAlpha:0,duration:.12,ease:"none"}},start+duration-.12); tl.set(inner,{{autoAlpha:0}},start+duration); }}
      const s1=prepareChunk("mask-valuation-bubble","chunk-valuation-bubble","valuationBubble",{json.dumps(valuation["rect"])},{valuation["rows"]},{valuation["stroke_width"]});
      const s2=prepareChunk("mask-capacity-penalty","chunk-capacity-penalty","capacityPenalty",{json.dumps(capacity["rect"])},{capacity["rows"]},{capacity["stroke_width"]});
      const s2h=prepareChunk("mask-hbm-stack","chunk-hbm-stack","hbmStack",{json.dumps(hbm["rect"])},{hbm["rows"]},{hbm["stroke_width"]});
      const s3=prepareChunk("mask-ram-ageddon","chunk-ram-ageddon","ramAgeddon",{json.dumps(ram["rect"])},{ram["rows"]},{ram["stroke_width"]});
      gsap.set([document.getElementById("scene-one-inner"),document.getElementById("scene-two-inner"),document.getElementById("scene-three-inner")],{{autoAlpha:0}}); gsap.set("#scene-one-inner",{{autoAlpha:1}}); gsap.set([handA,handB,handE],{{autoAlpha:0}});
      sceneFrame("scene-one-inner",0,3); sceneFrame("scene-two-inner",3,8.4); sceneFrame("scene-three-inner",11.4,6.6);
      drawLbl("#s1-kicker",.10,.25,420); drawLbl("#s1-title",.20,.45,440); draw(s1,.88,.28); drawLbl("#s1-caption",1.78,.55,700);
      drawLbl("#s2-kicker",2.92,.25,600); drawLbl("#s2-title",3.12,.48,560); draw(s2,1.25,3.62); draw(s2h,.94,5.28); drawLbl("#s2-note",6.58,.52,500); drawLbl("#s2-caption",9.56,.58,780);
      drawLbl("#s3-kicker",11.48,.25,500); drawLbl("#s3-title",11.80,.50,560); draw(s3,1.28,11.98); drawLbl("#s3-caption",15.28,.62,850);
      window.__timelines["{PROOF_ID}"]=tl;
    </script>
  </body>
</html>
'''


def stage_project(receipts: dict[str, Any]) -> dict[str, Any]:
    for directory in (PROOF_ROOT, ASSET_ROOT, SOURCE_ROOT, REVIEW_ROOT, RENDER_ROOT):
        directory.mkdir(parents=True, exist_ok=True)
    _, asset_index = deck_proof.source_asset_index()
    worlds = stage_world()
    arts = stage_deck_assets(asset_index)
    shutil.copy2(CANONICAL_AUDIO, ASSET_ROOT / "history_episode_1_master.mp3")
    shutil.copy2(HAND_SOURCE, ASSET_ROOT / "draw-hand-a-v1.png")
    with Image.open(HAND_SOURCE) as hand:
        ImageOps.mirror(hand).save(ASSET_ROOT / "draw-hand-b-v1.png", optimize=True)
    shutil.copy2(CANONICAL_WORDS, SOURCE_ROOT / "canonical.words.json")
    shutil.copy2(P24_NARRATION, SOURCE_ROOT / "narration.locked.md")
    shutil.copy2(P24_LEDGER, SOURCE_ROOT / "claim-ledger.v1.json")
    coverage_root = REVIEW_ROOT / "coverage"
    coverage_root.mkdir(parents=True, exist_ok=True)
    chunks = []
    for art in arts:
        coverage_path = coverage_root / art["filename"]
        with Image.open(DECK_ASSET_ROOT / art["filename"]) as source:
            source.convert("RGB").resize((art["width"], art["height"]), Image.Resampling.LANCZOS).save(coverage_path, optimize=True)
        chunks.append({"image": str(coverage_path), "rect": [-art["stroke_width"], -40, art["width"] + art["stroke_width"], art["height"] + 40], "sw": art["stroke_width"]})
    write_json(REVIEW_ROOT / "chunks.json", chunks)
    REVIEW_ROOT.joinpath("contact-sheet.html").write_text(
        "<!doctype html><meta charset='utf-8'><title>World blend proof contact sheet</title>"
        "<style>body{margin:0;padding:32px;background:#e7d8be;color:#25252a;font:16px Georgia,serif}main{display:grid;grid-template-columns:repeat(2,1fr);gap:20px}figure{margin:0;background:#fffdf8;border:3px solid #243d5e;padding:12px}img{width:100%;height:260px;object-fit:contain;background:#e7d8be}figcaption{padding-top:8px;font:14px 'Segoe Print',sans-serif}</style>"
        "<main>"
        + "".join(f"<figure><img src='../assets/deck/{html.escape(art['filename'])}' alt='{html.escape(art['display_name'])}'><figcaption>{html.escape(art['source_asset_id'])} · {html.escape(art['context']['what_it_is'])}</figcaption></figure>" for art in arts)
        + "</main>\n",
        encoding="utf-8",
    )
    proof = {
        "schema_version": "finance_whiteboard_world_blend_manifest.v1",
        "proof_id": PROOF_ID,
        "renderer": "hyperframes:html-gsap",
        "duration_s": DURATION_S,
        "delivery_fps": DELIVERY_FPS,
        "authoring_profile": AUTHORING,
        "render_profile": REVIEW,
        "source_manifest": {"path": str(P28_MANIFEST.relative_to(REPO)).replace("\\", "/"), "sha256": receipts["p28_manifest_sha256"]},
        "world_assets": worlds,
        "deck_assets": arts,
        "canonical_audio": {"path": "assets/history_episode_1_master.mp3", "sha256": receipts["audio_sha256"], "duration_s": DURATION_S},
        "hand": {"a_path": "assets/draw-hand-a-v1.png", "b_path": "assets/draw-hand-b-v1.png", "source_sha256": receipts["hand_source_sha256"]},
        "composition_rule": "continuous woodblock research world with whiteboard evidence layer; no world reset between evidence plates",
        "asset_policy": "NotebookLM/PPTX crops remain review-only source evidence; generated cutouts are world props",
        "provider_calls": 0,
        "status": "inputs_staged",
    }
    write_json(SOURCE_ROOT / "asset-binding.v1.json", {"schema_version": "finance_whiteboard_world_blend_binding.v1", "proof_id": PROOF_ID, "source_receipts": receipts, "world_assets": worlds, "deck_assets": arts})
    write_json(PROOF_ROOT / "proof-manifest.v1.json", proof)
    PROOF_ROOT.joinpath("index.html").write_text(html_document(arts, worlds), encoding="utf-8")
    return proof


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
    output = RENDER_ROOT / "finance-whiteboard-world-blend-proof.mp4"
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
    write_json(REVIEW_ROOT / "watch-review-draft.v1.json", {"schema_version": "watch_review_draft.v1", "proof_id": PROOF_ID, "status": "draft", "review_required": True, "render_path": str(output.relative_to(PROOF_ROOT)).replace("\\", "/"), "checks": ["woodblock world remains stable across scenes", "whiteboard evidence layer stays inside the world", "hand reveals each deck plate", "baked source text remains legible", "P28 source IDs and hashes remain bound"]})


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--render", action="store_true")
    args = parser.parse_args()
    receipts = verify_inputs()
    manifest = stage_project(receipts)
    if args.render:
        render_project(manifest)
    print(json.dumps({"proof_root": str(PROOF_ROOT), "status": manifest.get("status", "inputs_staged"), "duration_s": DURATION_S}, indent=2))


if __name__ == "__main__":
    main()
