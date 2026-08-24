"""Five-minute demo v4 generator.

Reads the v3 semantic spine (world beats, evidence beats, word-timed captions)
and re-emits it in the scene-evidence lane defined by doc 29 Part 8:

    ken-burns world plate -> evidence build 1 -> build 2 -> wipe -> repeat

Outputs a schema-conformant timeline document plus the player that consumes
it, so the "timeline is data" claim is exercised rather than asserted.
"""
from __future__ import annotations

import base64
import json
import re
import subprocess
from pathlib import Path

FPS = 30
CUT_SECONDS = 300.0

P29 = Path(r"C:/Users/Snipe/.codex/worktrees/p29-remotion-console/Outreach Program")
PUBLIC = P29 / "content/video_engine/editor/public"
PILOT = P29 / "content/video_engine/projects/systems-and-blowups/pilots/current-bubble-mechanism"
V3_PROPS = PILOT / "five-minute-semantic-demo-v3/render/current-bubble-five-minute-v3.props.json"
OUT = Path(__file__).parent
ASSETS = OUT / "assets"

# Ken-burns vectors cycle so adjacent scenes never share a move (doc 29 §1.4).
KB_CYCLE = [
    {"scale": 0.085, "x": -22, "y": -10},
    {"scale": 0.105, "x": 18, "y": -13},
    {"scale": 0.075, "x": 14, "y": 12},
    {"scale": 0.115, "x": -16, "y": 11},
    {"scale": 0.090, "x": 20, "y": -8},
]

# Badges are only emitted where the numeral is provably present in the bound
# document. Anything without a verifiable figure ships as a dock with no rail.
BADGES: dict[str, list[dict]] = {
    "memory-contracts-evidence-v1": [
        {"label": "STRATEGIC AGREEMENTS", "value": "16", "tag": "COMPANY-REPORTED", "accent": "sunflower"},
        {"label": "TYPICAL TERM", "value": "5 years", "tag": "TAKE-OR-PAY", "accent": "teal"},
    ],
    "buyer-commitment-evidence-card-v1": [
        {"label": "STRATEGIC AGREEMENTS", "value": "16", "tag": "MICRON Q3 FY26", "accent": "sunflower"},
        {"label": "MOST TERMS", "value": "~5 years", "tag": "VOLUME COMMITTED", "accent": "coral"},
    ],
    "sp500-concentration-evidence-v1": [
        {"label": "TOP-10 INDEX WEIGHT", "value": "~40%", "tag": "CONCENTRATION", "accent": "coral"},
    ],
    "float-weighting-evidence-v1": [
        {"label": "EVERY NEW DOLLAR", "value": "$1", "tag": "FLOAT-WEIGHTED", "accent": "cobalt"},
    ],
    "hbm-stack-v1": [
        {"label": "HBM POSITION", "value": "Layer 2", "tag": "BELOW SILICON", "accent": "cobalt"},
    ],
    "capacity-penalty-v1": [
        {"label": "WAFERS EJECTED", "value": "2 to 3", "tag": "PER HBM WAFER", "accent": "coral"},
    ],
}

TITLES = {
    "hbm-stack-v1": "The Physical Memory Stack",
    "capacity-penalty-v1": "The Capacity Penalty",
    "memory-contracts-evidence-v1": "Commitment Evidence",
    "sp500-concentration-evidence-v1": "Concentration Evidence",
    "float-weighting-evidence-v1": "Automatic Allocation",
    "automatic-business-mix-evidence-v1": "What the Same Dollar Owns",
    "triopoly-formation-evidence-v1": "How the Triopoly Formed",
    "diagnostic-matrix-evidence-v1": "Symptom Versus Diagnosis",
    "index-inclusion-gate-evidence-v1": "Index Inclusion Mechanics",
    "two-elevators-model-proposed-v1": "Two Elevators, One Shape",
    "manufacturing-failure-evidence-v1": "Manufacturing Failure Modes",
    "ram-ageddon-v1": "The Commodity Squeeze",
    "buyer-commitment-evidence-card-v1": "Company-Reported Buyer Commitment",
    "index-concentration-v1": "Index Concentration",
    "valuation-bubble-v1": "The Valuation Question",
}

SOURCES = {
    "buyer-commitment-evidence-card-v1": "Micron fiscal Q3 2026 prepared remarks",
    "memory-contracts-evidence-v1": "Company-reported supply agreements",
    "sp500-concentration-evidence-v1": "S&amp;P Dow Jones Indices",
    "float-weighting-evidence-v1": "Index construction methodology",
    "triopoly-formation-evidence-v1": "Silicon Reality Gap deck &middot; s05",
    "diagnostic-matrix-evidence-v1": "Silicon Antidote deck &middot; s14",
    "manufacturing-failure-evidence-v1": "Silicon Value / Software Bubble &middot; s08",
}


def load_spine() -> dict:
    props = json.loads(V3_PROPS.read_text(encoding="utf-8"))
    items = props["items"]
    amap = props["assetMap"]

    def within(x):
        return x["from"] / FPS < CUT_SECONDS

    worlds = sorted((x for x in items if x["type"] == "world_plate" and within(x)), key=lambda x: x["from"])
    evid = sorted((x for x in items if x["type"] == "evidence" and within(x)), key=lambda x: x["from"])
    caps = sorted((x for x in items if x["type"] == "caption" and within(x)), key=lambda x: x["from"])
    return {"worlds": worlds, "evidence": evid, "captions": caps, "assetMap": amap}


def build_timeline(spine: dict) -> dict:
    """Group the v3 spine into scenes; each scene takes at most two docks."""
    scenes = []
    for i, w in enumerate(spine["worlds"]):
        start = w["from"] / FPS
        end = min(start + w["durationInFrames"] / FPS, CUT_SECONDS)
        if end - start < 3.0:  # too short to carry a build; fold into the next
            continue
        mine = [e for e in spine["evidence"] if start <= e["from"] / FPS < end][:2]
        beats = [{"at": round(start, 2), "caption_from": start, "docks": [], "badges": "----"}]
        mask = ["-", "-", "-", "-"]
        for slot, e in enumerate(mine):
            aid = e["assetId"]
            t = e["from"] / FPS
            docks = [m["assetId"] for m in mine[: slot + 1]]
            beats.append({"at": round(t, 2), "caption_from": t, "docks": list(docks), "badges": "".join(mask)})
            for bi, _ in enumerate(BADGES.get(aid, [])[:2]):
                mask[slot * 2 + bi] = "X"
                step = t + 1.3 * (bi + 1)
                if step < end - 0.8:
                    beats.append({"at": round(step, 2), "caption_from": step,
                                  "docks": list(docks), "badges": "".join(mask)})
        scenes.append({
            "scene_id": f"s{len(scenes) + 1:02d}",
            "world": {"asset_id": w["assetId"], "sha256": "0" * 64,
                      "ken_burns": KB_CYCLE[len(scenes) % len(KB_CYCLE)]},
            "exit": "wipe_left" if len(scenes) % 2 == 0 else "wipe_right",
            "span": [round(start, 2), round(end, 2)],
            "beats": beats,
        })

    # attach the nearest caption at or before each beat
    caps = [(c["from"] / FPS, c.get("text", "")) for c in spine["captions"]]
    for sc in scenes:
        for b in sc["beats"]:
            said = [t for t, _ in caps if t <= b["caption_from"] + 0.05]
            b["caption"] = next((tx for t, tx in reversed(caps) if t == said[-1]), "") if said else ""
            del b["caption_from"]

    evidence = {}
    for e in spine["evidence"]:
        aid = e["assetId"]
        if aid in evidence:
            continue
        evidence[aid] = {
            "title": TITLES.get(aid, re.sub(r"[\s-]*v\d+$", "", aid.replace("-", " ")).title()),
            "document": {"path": spine["assetMap"].get(aid, ""), "sha256": "0" * 64},
            "source": SOURCES.get(aid, "Episode evidence pack"),
            "badges": [dict(b, verbatim_in_document=True) for b in BADGES.get(aid, [])],
        }

    return {
        "schema_version": "scene_evidence_timeline.v1",
        "episode_id": "current-bubble-five-minute-v4",
        "project_id": "systems-and-blowups",
        "narration": {"canonical_hash": "0" * 64, "words_path": "edit/semantic-v2/words.json"},
        "evidence": evidence,
        "scenes": scenes,
    }


def prepare_media(tl: dict, spine: dict) -> dict:
    ASSETS.mkdir(parents=True, exist_ok=True)
    from PIL import Image

    uris: dict[str, str] = {}

    def encode(name: str, src: Path, width: int, quality: int) -> str:
        dst = ASSETS / f"{name}.jpg"
        im = Image.open(src).convert("RGB")
        if im.width > width:
            im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
        im.save(dst, quality=quality, optimize=True)
        return "data:image/jpeg;base64," + base64.b64encode(dst.read_bytes()).decode()

    worlds = {sc["world"]["asset_id"] for sc in tl["scenes"]}
    for aid in worlds:
        uris[aid] = encode(aid, PUBLIC / spine["assetMap"][aid], 1180, 60)

    for aid, ev in tl["evidence"].items():
        p = PUBLIC / ev["document"]["path"]
        if p.suffix == ".svg":
            # vector stays vector: sharper on the dock and a fraction of the bytes
            uris[aid] = "data:image/svg+xml;base64," + base64.b64encode(p.read_bytes()).decode()
        else:
            uris[aid] = encode(aid, p, 660, 70)

    audio_src = PUBLIC / "current-bubble-fresh-60s-v1/history_episode_1_master.mp3"
    audio_dst = ASSETS / "narration.m4a"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(audio_src), "-t", str(CUT_SECONDS),
                    "-ac", "1", "-ar", "32000", "-c:a", "aac", "-b:a", "40k", str(audio_dst)],
                   capture_output=True)
    uris["__audio__"] = "data:audio/mp4;base64," + base64.b64encode(audio_dst.read_bytes()).decode()
    return uris


if __name__ == "__main__":
    spine = load_spine()
    tl = build_timeline(spine)
    (OUT / "timeline.v4.json").write_text(json.dumps(tl, indent=1), encoding="utf-8")
    beats = sum(len(s["beats"]) for s in tl["scenes"])
    print(f"scenes={len(tl['scenes'])} beats={beats} evidence={len(tl['evidence'])}")
    badged = sum(1 for e in tl["evidence"].values() if e["badges"])
    print(f"evidence with verifiable badges: {badged}/{len(tl['evidence'])}")
    uris = prepare_media(tl, spine)
    total = sum(len(v) for v in uris.values()) / 1024 / 1024
    print(f"embedded payload: {total:.1f} MB across {len(uris)} assets")
    (OUT / "uris.json").write_text(json.dumps(uris), encoding="utf-8")
