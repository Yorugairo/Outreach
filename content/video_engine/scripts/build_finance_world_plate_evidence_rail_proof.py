"""Build a proof using the canonical woodblock world plates as the stage.

The world plate owns the frame. One source-backed deck crop enters at a time
through an existing negative-space callout zone or a restrained fab inset.
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

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))
import build_finance_whiteboard_deck_asset_proof as deck_proof  # noqa: E402


REPO = deck_proof.REPO
PILOT = deck_proof.PILOT
PROOF_ID = "finance-world-plate-evidence-rail-proof-v1"
PROOF_ROOT = PILOT / PROOF_ID
ASSET_ROOT = PROOF_ROOT / "assets"
WORLD_ROOT = ASSET_ROOT / "world"
DECK_ROOT = ASSET_ROOT / "deck"
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
FPS = 24

WORLD_SOURCES = [
    {
        "asset_id": "world-memory-skepticism-v2",
        "source": PILOT / "edit/hyperframes-opening-v1/assets/memory-skepticism-v2.png",
        "path": "assets/world/memory-skepticism-v2.png",
        "role": "memory world plate with three reserved evidence callouts",
    },
    {
        "asset_id": "world-hero-fab-constraint-v1",
        "source": PILOT / "assets/hero/hero-fab-constraint-v1.png",
        "path": "assets/world/hero-fab-constraint-v1.png",
        "role": "hero fabrication world plate with open peripheral space",
    },
]

DECK_LAYOUTS = [
    {
        "asset_id": "silicon-antidote-s02-valuation-bubble-v1",
        "filename": "valuation-bubble.png",
        "display_name": "S&P 500 valuation balloon",
        "x": 120,
        "y": 570,
        "width": 330,
        "height": 325,
        "rect": [-55, -55, 385, 380],
        "rows": 8,
        "stroke_width": 100,
        "start_s": 0.35,
        "duration_s": 0.82,
        "scene": "memory-rail",
        "source_slot": "teal-callout",
    },
    {
        "asset_id": "silicon-antidote-s09-capacity-penalty-v1",
        "filename": "capacity-penalty.png",
        "display_name": "three-to-one capacity penalty",
        "x": 675,
        "y": 625,
        "width": 510,
        "height": 282,
        "rect": [-65, -60, 575, 342],
        "rows": 8,
        "stroke_width": 100,
        "start_s": 4.12,
        "duration_s": 1.05,
        "scene": "memory-rail",
        "source_slot": "navy-callout",
    },
    {
        "asset_id": "silicon-antidote-s10-ram-ageddon-v1",
        "filename": "ram-ageddon.png",
        "display_name": "RAM-ageddon supply-demand shock",
        "x": 1225,
        "y": 640,
        "width": 450,
        "height": 216,
        "rect": [-65, -60, 515, 276],
        "rows": 8,
        "stroke_width": 100,
        "start_s": 7.1,
        "duration_s": 1.1,
        "scene": "memory-rail",
        "source_slot": "orange-callout",
    },
    {
        "asset_id": "silicon-reality-gap-s07-hbm-stack-v1",
        "filename": "hbm-stack.png",
        "display_name": "HBM physical stack",
        "x": 1265,
        "y": 560,
        "width": 370,
        "height": 346,
        "rect": [-50, -50, 420, 396],
        "rows": 7,
        "stroke_width": 90,
        "start_s": 12.02,
        "duration_s": 1.05,
        "scene": "fab-inset",
        "source_slot": "fab-lower-right-inset",
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
    for path in (P28_MANIFEST, CANONICAL_AUDIO, CANONICAL_WORDS, P24_NARRATION, P24_LEDGER, HAND_SOURCE):
        require_file(path)
    for spec in WORLD_SOURCES:
        require_file(spec["source"])
    manifest, index = deck_proof.source_asset_index()
    source_root = REPO / "content/video_engine/projects/systems-and-blowups/sources/decks"
    for spec in DECK_LAYOUTS:
        asset = index.get(spec["asset_id"])
        if not asset:
            raise RuntimeError(f"missing P28 asset {spec['asset_id']}")
        source = source_root / asset["path"]
        require_file(source)
        if sha256(source) != asset["sha256"]:
            raise RuntimeError(f"P28 source hash mismatch for {spec['asset_id']}")
        if asset.get("render_eligible"):
            raise RuntimeError("review-only deck asset was unexpectedly promoted")
    return {
        "p28_manifest_sha256": sha256(P28_MANIFEST),
        "source_manifest_id": manifest.get("manifest_id"),
        "audio_sha256": sha256(CANONICAL_AUDIO),
        "hand_source_sha256": sha256(HAND_SOURCE),
        "world_asset_ids": [item["asset_id"] for item in WORLD_SOURCES],
        "deck_asset_ids": [item["asset_id"] for item in DECK_LAYOUTS],
    }


def stage_assets(index: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    WORLD_ROOT.mkdir(parents=True, exist_ok=True)
    DECK_ROOT.mkdir(parents=True, exist_ok=True)
    worlds: list[dict[str, Any]] = []
    for spec in WORLD_SOURCES:
        destination = PROOF_ROOT / spec["path"]
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(spec["source"], destination)
        worlds.append({**spec, "sha256": sha256(destination), "source": str(spec["source"])})
    source_root = REPO / "content/video_engine/projects/systems-and-blowups/sources/decks"
    decks: list[dict[str, Any]] = []
    for spec in DECK_LAYOUTS:
        source_asset = index[spec["asset_id"]]
        source = source_root / source_asset["path"]
        destination = DECK_ROOT / spec["filename"]
        shutil.copy2(source, destination)
        decks.append({
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
            "asset_mode": "source_evidence_in_reserved_world_slot",
        })
    return worlds, decks


def evidence_svg(art: dict[str, Any], mask_id: str, aria: str) -> str:
    return f'''<div id="art-{html.escape(art["filename"].rsplit(".", 1)[0])}" class="artblock" style="left:{art["x"]}px;top:{art["y"]}px;width:{art["width"]}px;height:{art["height"]}px">
          <svg width="{art["width"]}" height="{art["height"]}" viewBox="0 0 {art["width"]} {art["height"]}" aria-label="{html.escape(aria)}">
            <defs><mask id="{mask_id}" maskUnits="userSpaceOnUse" x="0" y="0" width="{art["width"]}" height="{art["height"]}"><rect width="{art["width"]}" height="{art["height"]}" fill="#000" /></mask></defs>
            <image href="{html.escape(art["path"])}" x="0" y="0" width="{art["width"]}" height="{art["height"]}" mask="url(#{mask_id})" />
          </svg>
        </div>'''


def html_document(worlds: list[dict[str, Any]], decks: list[dict[str, Any]]) -> str:
    world = {item["asset_id"]: item for item in worlds}
    art = {item["source_asset_id"]: item for item in decks}
    valuation = art["silicon-antidote-s02-valuation-bubble-v1"]
    capacity = art["silicon-antidote-s09-capacity-penalty-v1"]
    ram = art["silicon-antidote-s10-ram-ageddon-v1"]
    hbm = art["silicon-reality-gap-s07-hbm-stack-v1"]
    return f'''<!doctype html>
<html lang="en" data-resolution="landscape">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <title>Finance World Plate Evidence Rail Proof</title>
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      * {{ box-sizing:border-box; }}
      html,body {{ margin:0; width:1920px; height:1080px; overflow:hidden; background:#0b2135; }}
      @font-face {{ font-family:"WhiteboardSans"; src:local("Segoe Print"); font-style:normal; font-weight:400 800; }}
      body {{ color:#f4ead3; font-family:"WhiteboardSans",sans-serif; }}
      #stage {{ position:relative; width:1920px; height:1080px; overflow:hidden; background:#0b2135; }}
      .world {{ position:absolute; inset:0; z-index:0; opacity:0; }}
      .world img {{ display:block; width:1920px; height:1080px; object-fit:cover; }}
      .world-vignette {{ position:absolute; inset:0; pointer-events:none; background:linear-gradient(90deg,rgba(4,17,29,.22),transparent 28%,transparent 72%,rgba(4,17,29,.18)); }}
      .scene {{ position:absolute; inset:0; z-index:10; overflow:hidden; }}
      .scene-inner {{ position:absolute; inset:0; }}
      .artblock {{ position:absolute; opacity:0; z-index:18; background:#fffdf8; border:6px solid #f7efdf; box-shadow:0 16px 20px rgba(0,0,0,.28); mix-blend-mode:multiply; }}
      .artblock svg {{ display:block; overflow:visible; }}
      .revealPath {{ fill:none; stroke:#fff; stroke-linecap:round; stroke-linejoin:round; }}
      .hand {{ position:absolute; left:0; top:0; z-index:40; width:320px; height:480px; object-fit:contain; pointer-events:none; opacity:0; visibility:hidden; transform-origin:135px 428px; }}
      .lbl {{ position:absolute; z-index:26; white-space:nowrap; padding-right:.22em; clip-path:inset(0 calc((1 - var(--rv,0)) * 100%) 0 0); opacity:0; font-weight:700; letter-spacing:.015em; }}
      .chapter {{ left:90px; top:70px; font-size:32px; line-height:1.25; background:#092239; color:#f4ead3; padding:8px 16px 6px; border:4px solid #d3993d; box-shadow:7px 7px 0 #b95643; }}
      .caption {{ left:100px; top:880px; max-width:1070px; font-size:27px; line-height:1.35; color:#1b2427; background:#f4ead3; padding:5px 11px 4px; border:3px solid #0a2135; }}
      .source-tag {{ position:absolute; z-index:30; font-size:16px; line-height:1.25; letter-spacing:.12em; color:#f4ead3; background:#0a2135; padding:5px 9px 4px; border:2px solid #d3993d; }}
      .memory-tag {{ left:125px; top:535px; }}
      .capacity-tag {{ left:700px; top:595px; }}
      .ram-tag {{ left:1260px; top:610px; }}
      .fab-tag {{ left:1275px; top:520px; }}
      .leader {{ fill:none; stroke:#f4ead3; stroke-width:8; stroke-linecap:round; stroke-linejoin:round; opacity:.95; }}
      .leader-dot {{ fill:#d3993d; stroke:#0a2135; stroke-width:5; }}
    </style>
  </head>
  <body>
    <div id="stage" data-composition-id="{PROOF_ID}" data-start="0" data-duration="18" data-width="1920" data-height="1080" data-fps="24">
      <div id="world-memory" class="world clip" data-start="0" data-duration="9.8"><img src="{world['world-memory-skepticism-v2']['path']}" alt="Memory skepticism woodblock world plate" /><div class="world-vignette"></div></div>
      <div id="world-fab" class="world clip" data-start="9.8" data-duration="8.2"><img src="{world['world-hero-fab-constraint-v1']['path']}" alt="Fabrication constraint woodblock world plate" /><div class="world-vignette"></div></div>

      <section id="memory-scene" class="scene clip" data-start="0" data-duration="9.8" data-track-index="2">
        <div id="memory-inner" class="scene-inner">
          <div id="m-chapter" class="lbl chapter" style="--rv:0">MEMORY SKEPTICISM</div>
          <path id="memory-leader" class="leader" d="M650 410 C520 480 380 555 285 635" />
          <circle class="leader-dot" cx="650" cy="410" r="12" />
          {evidence_svg(valuation, "mask-valuation", "S&P 500 valuation source evidence")}
          {evidence_svg(capacity, "mask-capacity", "Three-to-one capacity penalty source evidence")}
          {evidence_svg(ram, "mask-ram", "RAM-ageddon source evidence")}
          <div id="m-caption" class="lbl caption" style="--rv:0">The world tells the story. The evidence fills one callout at a time.</div>
          <div class="source-tag memory-tag">S02 · CAPE EVIDENCE</div>
          <div class="source-tag capacity-tag">S09 · CAPACITY EVIDENCE</div>
          <div class="source-tag ram-tag">S10 · SUPPLY SHOCK</div>
        </div>
      </section>

      <section id="fab-scene" class="scene clip" data-start="9.8" data-duration="8.2" data-track-index="3">
        <div id="fab-inner" class="scene-inner">
          <div id="f-chapter" class="lbl chapter" style="--rv:0">THE FAB IS THE CHOKE POINT</div>
          <path id="fab-leader" class="leader" d="M1030 590 C1160 600 1240 650 1305 700" />
          <circle class="leader-dot" cx="1030" cy="590" r="12" />
          {evidence_svg(hbm, "mask-hbm", "HBM stack source evidence inset")}
          <div id="f-caption" class="lbl caption" style="--rv:0">The evidence is an inset. The factory remains the world.</div>
          <div class="source-tag fab-tag">S07 · HBM STRUCTURE</div>
        </div>
      </section>

      <audio id="voiceover" data-start="0" data-duration="18" data-track-index="1" src="assets/history_episode_1_master.mp3" preload="auto"></audio>
      <img id="handA" class="hand" src="assets/draw-hand-a-v1.png" alt="" aria-hidden="true" data-layout-allow-occlusion="true" />
      <img id="handB" class="hand" src="assets/draw-hand-b-v1.png" alt="" aria-hidden="true" data-layout-allow-occlusion="true" />
      <div id="handE" class="hand" aria-hidden="true" data-layout-allow-occlusion="true"></div>
    </div>

    <script>
      window.__timelines = window.__timelines || {{}};
      const tl=gsap.timeline({{paused:true}}), SVGNS="http://www.w3.org/2000/svg";
      const handA=document.getElementById("handA"), handB=document.getElementById("handB"), handE=document.getElementById("handE");
      const NIB={{a:{{x:135,y:428}},b:{{x:185,y:428}},e:{{x:135,y:428}}}};
      const ARTS={{ valuation:{{x:{valuation["x"]},y:{valuation["y"]}}}, capacity:{{x:{capacity["x"]},y:{capacity["y"]}}}, ram:{{x:{ram["x"]},y:{ram["y"]}}}, hbm:{{x:{hbm["x"]},y:{hbm["y"]}}} }};
      handA.style.transformOrigin=`${{NIB.a.x}}px ${{NIB.a.y}}px`; handB.style.transformOrigin=`${{NIB.b.x}}px ${{NIB.b.y}}px`; handE.style.transformOrigin=`${{NIB.e.x}}px ${{NIB.e.y}}px`;
      function serp(x0,y0,x1,y1,rows,sw){{const ix0=x0+sw/2,ix1=x1-sw/2,iy0=y0+sw/2,iy1=y1-sw/2,step=(iy1-iy0)/Math.max(1,rows-1);let d=`M${{ix0}} ${{Math.round(iy0)}}`;for(let i=0;i<rows;i+=1){{d+=` H${{i%2===0?ix1:ix0}}`;if(i<rows-1)d+=` V${{Math.round(iy0+step*(i+1))}}`;}}return d;}}
      function geometry(path,samples=512){{const length=path.getTotalLength()||6000,points=[];for(let i=0;i<=samples;i+=1){{const p=path.getPointAtLength(i/samples*length);points.push({{x:p.x,y:p.y}});}}return{{length,points}};}}
      function pointAt(g,progress){{const p=Math.min(1,Math.max(0,progress)),scaled=p*(g.points.length-1),index=Math.min(g.points.length-2,Math.floor(scaled)),mix=scaled-index,a=g.points[index],b=g.points[index+1];return{{x:a.x+(b.x-a.x)*mix,y:a.y+(b.y-a.y)*mix}};}}
      function handAt(g,key,progress){{const art=ARTS[key],point=pointAt(g,progress),ahead=pointAt(g,Math.min(1,progress+.01)),backwards=ahead.x-point.x<-.5,hand=backwards?handB:handA,nib=backwards?NIB.b:NIB.a;handA.style.opacity=0;handB.style.opacity=0;handE.style.opacity=0;hand.style.visibility="visible";hand.style.opacity=1;hand.style.transform=`translate(${{art.x+point.x-nib.x}}px,${{art.y+point.y-nib.y}}px) rotate(${{Math.sin(progress*34)*2.2}}deg)`;}}
      function hideHands(at){{tl.set([handA,handB,handE],{{autoAlpha:0}},at);}}
      function prepare(maskId,id,key,rect,rows,sw){{const path=document.createElementNS(SVGNS,"path");path.setAttribute("id",id);path.setAttribute("class","revealPath");path.setAttribute("stroke-width",sw);path.setAttribute("d",serp(...rect,rows,sw));document.getElementById(maskId).appendChild(path);const g=geometry(path);path.style.strokeDasharray=`${{g.length}}`;path.style.strokeDashoffset=`${{g.length}}`;return{{path,geometry:g,key}};}}
      function draw(chunk,dur,at){{const{{path,geometry,key}}=chunk,block=path.closest(".artblock");tl.set(block,{{autoAlpha:1}},at-.05);tl.to(path,{{strokeDashoffset:0,duration:dur,ease:"none"}},at);const proxy={{p:0}};tl.to(proxy,{{p:1,duration:dur,ease:"none",onUpdate:()=>handAt(geometry,key,proxy.p)}},at);hideHands(at+dur+.05);}}
      function write(id,at,dur,width){{const el=document.querySelector(id),left=el.offsetLeft,top=el.offsetTop,fontSize=parseFloat(getComputedStyle(el).fontSize)||30,baseY=top+fontSize*.72;tl.set(id,{{autoAlpha:1,"--rv":0}},at);tl.to(id,{{"--rv":1,duration:dur,ease:"none"}},at);const proxy={{p:0}};tl.to(proxy,{{p:1,duration:dur,ease:"none",onUpdate:()=>{{handA.style.opacity=1;handA.style.visibility="visible";handB.style.opacity=0;handB.style.visibility="hidden";handA.style.transform=`translate(${{left+proxy.p*width-NIB.a.x}}px,${{baseY-NIB.a.y}}px) rotate(${{Math.sin(proxy.p*40)*1.5}}deg)`;}}}},at);hideHands(at+dur+.05);}}
      function frame(id,start,duration){{const inner=document.getElementById(id);tl.set(inner,{{autoAlpha:0}},0);tl.set(inner,{{autoAlpha:1}},start);tl.set(inner,{{autoAlpha:0}},start+duration);}}
      gsap.set([document.getElementById("world-memory"),document.getElementById("world-fab")],{{autoAlpha:0}});tl.set("#world-memory",{{autoAlpha:1}},0);tl.set("#world-fab",{{autoAlpha:1}},9.8);tl.to("#world-memory",{{autoAlpha:0,duration:.16,ease:"none"}},9.8);
      const v=prepare("mask-valuation","chunk-valuation","valuation",{json.dumps(valuation["rect"])},{valuation["rows"]},{valuation["stroke_width"]});
      const c=prepare("mask-capacity","chunk-capacity","capacity",{json.dumps(capacity["rect"])},{capacity["rows"]},{capacity["stroke_width"]});
      const r=prepare("mask-ram","chunk-ram","ram",{json.dumps(ram["rect"])},{ram["rows"]},{ram["stroke_width"]});
      const h=prepare("mask-hbm","chunk-hbm","hbm",{json.dumps(hbm["rect"])},{hbm["rows"]},{hbm["stroke_width"]});
      frame("memory-inner",0,9.8);frame("fab-inner",9.8,8.2);
      write("#m-chapter",.10,.35,320);draw(v,.82,.35);write(".memory-tag",1.28,.32,230);draw(c,1.05,4.12);write(".capacity-tag",5.38,.34,300);draw(r,1.10,7.10);write(".ram-tag",8.38,.32,245);write("#m-caption",8.58,.52,700);
      write("#f-chapter",9.98,.42,520);draw(h,1.05,12.02);write(".fab-tag",13.16,.32,230);write("#f-caption",15.30,.58,760);
      window.__timelines["{PROOF_ID}"]=tl;
    </script>
  </body>
</html>
'''


def stage_project(receipts: dict[str, Any]) -> dict[str, Any]:
    for directory in (PROOF_ROOT, ASSET_ROOT, SOURCE_ROOT, REVIEW_ROOT, RENDER_ROOT):
        directory.mkdir(parents=True, exist_ok=True)
    _, index = deck_proof.source_asset_index()
    worlds, decks = stage_assets(index)
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
    for art in decks:
        coverage_path = coverage_root / art["filename"]
        with Image.open(DECK_ROOT / art["filename"]) as source:
            source.convert("RGB").resize((art["width"], art["height"]), Image.Resampling.LANCZOS).save(coverage_path, optimize=True)
        chunks.append({"image": str(coverage_path), "rect": [-art["stroke_width"], -40, art["width"] + art["stroke_width"], art["height"] + 40], "sw": art["stroke_width"]})
    write_json(REVIEW_ROOT / "chunks.json", chunks)
    REVIEW_ROOT.joinpath("contact-sheet.html").write_text(
        "<!doctype html><meta charset='utf-8'><title>World plate evidence rail proof</title><style>body{margin:0;padding:32px;background:#092239;color:#f4ead3;font:16px Georgia,serif}main{display:grid;grid-template-columns:repeat(2,1fr);gap:20px}figure{margin:0;background:#f4ead3;color:#092239;border:3px solid #d3993d;padding:12px}img{width:100%;height:250px;object-fit:contain;background:#0b2135}figcaption{padding-top:8px;font:14px 'Segoe Print',sans-serif}</style><main>"
        + "".join(f"<figure><img src='../assets/deck/{html.escape(art['filename'])}' alt='{html.escape(art['display_name'])}'><figcaption>{html.escape(art['source_asset_id'])} · slot: {html.escape(art['source_slot'])}</figcaption></figure>" for art in decks)
        + "</main>\n",
        encoding="utf-8",
    )
    manifest = {
        "schema_version": "finance_world_plate_evidence_rail_manifest.v1",
        "proof_id": PROOF_ID,
        "renderer": "hyperframes:html-gsap",
        "duration_s": DURATION_S,
        "delivery_fps": FPS,
        "authoring_profile": {"width": 1920, "height": 1080, "fps": FPS},
        "render_profile": {"width": 1280, "height": 720, "fps": FPS, "label": "review"},
        "source_manifest": {"path": str(P28_MANIFEST.relative_to(REPO)).replace("\\", "/"), "sha256": receipts["p28_manifest_sha256"]},
        "world_assets": worlds,
        "deck_assets": decks,
        "canonical_audio": {"path": "assets/history_episode_1_master.mp3", "sha256": receipts["audio_sha256"], "duration_s": DURATION_S},
        "hand": {"a_path": "assets/draw-hand-a-v1.png", "b_path": "assets/draw-hand-b-v1.png", "source_sha256": receipts["hand_source_sha256"]},
        "composition_rule": "full-frame world plate owns attention; one source evidence crop occupies one reserved callout or inset at a time",
        "asset_policy": "world plates are canonical story surfaces; deck crops remain review-only source evidence",
        "provider_calls": 0,
        "status": "inputs_staged",
    }
    write_json(SOURCE_ROOT / "asset-binding.v1.json", {"schema_version": "finance_world_plate_evidence_rail_binding.v1", "proof_id": PROOF_ID, "source_receipts": receipts, "world_assets": worlds, "deck_assets": decks})
    write_json(PROOF_ROOT / "proof-manifest.v1.json", manifest)
    PROOF_ROOT.joinpath("index.html").write_text(html_document(worlds, decks), encoding="utf-8")
    return manifest


def command(*args: str, cwd: Path | None = None) -> None:
    subprocess.run(list(args), cwd=cwd, check=True)


def render_project(manifest: dict[str, Any]) -> None:
    coverage = Path("C:/Users/Snipe/.codex/skills/whiteboard-explainer/scripts/coverage-check.py")
    command(sys.executable, str(coverage), str(REVIEW_ROOT / "chunks.json"))
    npx = shutil.which("npx")
    if not npx:
        raise RuntimeError("npx is required for HyperFrames rendering")
    command(npx, "--yes", "hyperframes@0.7.104", "check", cwd=PROOF_ROOT)
    authoring = RENDER_ROOT / "hf-authoring.mp4"
    output = RENDER_ROOT / "finance-world-plate-evidence-rail-proof.mp4"
    command(npx, "--yes", "hyperframes@0.7.104", "render", "-o", str(authoring), cwd=PROOF_ROOT)
    ffprobe = shutil.which("ffprobe")
    ffmpeg = shutil.which("ffmpeg")
    if not ffprobe or not ffmpeg:
        raise RuntimeError("ffprobe and ffmpeg are required")
    command(ffmpeg, "-y", "-i", str(authoring), "-vf", "scale=1280:720:flags=lanczos", "-map", "0:v:0", "-map", "0:a?", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(output))
    probe = subprocess.run([ffprobe, "-v", "error", "-show_streams", "-show_format", "-of", "json", str(output)], check=True, capture_output=True, text=True)
    metadata = json.loads(probe.stdout)
    boundary_dir = REVIEW_ROOT / "boundaries"
    boundary_dir.mkdir(parents=True, exist_ok=True)
    for index, timestamp in enumerate((0.0, 0.5, 2.9, 3.2, 4.7, 6.8, 8.9, 9.7, 10.2, 12.5, 15.8, 17.9)):
        target = boundary_dir / f"boundary-{index + 1:02d}-{timestamp:05.1f}s.png"
        command(ffmpeg, "-y", "-ss", f"{timestamp:.3f}", "-i", str(output), "-frames:v", "1", "-update", "1", str(target))
    manifest["status"] = "review_render_complete"
    manifest["render"] = {"path": str(output.relative_to(PROOF_ROOT)).replace("\\", "/"), "authoring_path": str(authoring.relative_to(PROOF_ROOT)).replace("\\", "/"), "sha256": sha256(output), "ffprobe": metadata, "boundary_dir": str(boundary_dir.relative_to(PROOF_ROOT)).replace("\\", "/")}
    write_json(PROOF_ROOT / "proof-manifest.v1.json", manifest)
    write_json(REVIEW_ROOT / "watch-review-draft.v1.json", {"schema_version": "watch_review_draft.v1", "proof_id": PROOF_ID, "status": "draft", "review_required": True, "render_path": str(output.relative_to(PROOF_ROOT)).replace("\\", "/"), "checks": ["canonical world plates remain full-frame", "one evidence crop active at a time", "memory callout rail remains readable", "fab plate is not covered by a large card", "hand reveals evidence only"]})


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
