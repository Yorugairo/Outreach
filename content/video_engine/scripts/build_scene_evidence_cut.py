"""Five-minute demo v4 generator (scene-evidence lane, doc 29 Part 8).

Reads the v3 semantic spine for its world beats and canonical word-timed
captions, then selects evidence from the APPROVED teacher-stamped slide
catalogue (86 render-eligible slides) by semantic match against what is
actually being said inside each scene window.

Three rules this generator enforces, each a correction of the first pass:

1. Captions are their own track at their own canonical timings. They are
   never resampled onto beat boundaries (doc 29 Part 5).
2. Evidence comes only from teacher-stamped slides — never a cropped or
   unstamped one-off — and no slide repeats inside the cut.
3. A badge is emitted only where the numeral has been read off the bound
   slide. Everything else ships with no rail; the stamped slide already
   carries its own typeset figures, and inventing one to fill the layout
   is the failure this rule exists to prevent.
"""
from __future__ import annotations

import base64
import json
import math
import re
import subprocess
from collections import Counter
from pathlib import Path

FPS = 30
CUT_SECONDS = 300.0

P29 = Path(r"C:/Users/Snipe/.codex/worktrees/p29-remotion-console/Outreach Program")
PUBLIC = P29 / "content/video_engine/editor/public"
PROJ = P29 / "content/video_engine/projects/systems-and-blowups"
DECKS = PROJ / "sources/decks/teacher-stamped-production-visuals"
PILOT = PROJ / "pilots/current-bubble-mechanism"
V3_PROPS = PILOT / "five-minute-semantic-demo-v3/render/current-bubble-five-minute-v3.props.json"
OUT = Path(__file__).parent
ASSETS = OUT / "assets"

KB_CYCLE = [
    {"scale": 0.085, "x": -22, "y": -10},
    {"scale": 0.105, "x": 18, "y": -13},
    {"scale": 0.075, "x": 14, "y": 12},
    {"scale": 0.115, "x": -16, "y": 11},
    {"scale": 0.090, "x": 20, "y": -8},
]

# Numerals read directly off these slides during review.
VERIFIED_BADGES = {
    "memory-supercycle-s03": [
        {"label": "HBM WAFER SHARE", "value": "18% \u2192 23%", "tag": "2025\u20132026", "accent": "sunflower"},
        {"label": "WAFERS EJECTED", "value": "2 to 3", "tag": "PER HBM WAFER", "accent": "coral"},
    ],
    "memory-supercycle-s05": [
        {"label": "CXMT GROWTH", "value": "716%", "tag": "YoY", "accent": "coral"},
        {"label": "STUCK ON LEGACY", "value": "70%", "tag": "LPDDR4(X)", "accent": "teal"},
    ],
    "silicon-value-software-bubble-s04": [
        {"label": "SAMSUNG COMMITMENT", "value": "$400M", "tag": "1983", "accent": "sunflower"},
        {"label": "SK HYNIX DEBT", "value": "11T won", "tag": "IMF MERGER", "accent": "coral"},
    ],
    "sovereign-memory-infrastructure-s03": [
        {"label": "HBM POSITION", "value": "Layer 2", "tag": "BELOW SILICON", "accent": "cobalt"},
        {"label": "THERMAL ENVELOPE", "value": "1500W", "tag": "LIQUID COOLED", "accent": "sunflower"},
    ],
}

STOP = set("""a an the and or but of to in on for with as is are was were be been being that this those these
it its by from at into than then so such not no if we you they our their there here what which who how why
about over under more most less least can may might will would should could have has had do does did just
own same other another each any all some one two three now still even because""".split())


def tokens(text: str) -> list[str]:
    return [w for w in re.findall(r"[a-z]+", text.lower()) if w not in STOP and len(w) > 2]


def load_spine() -> dict:
    props = json.loads(V3_PROPS.read_text(encoding="utf-8"))
    items = props["items"]

    def inside(x):
        return x["from"] / FPS < CUT_SECONDS

    return {
        "worlds": sorted((x for x in items if x["type"] == "world_plate" and inside(x)), key=lambda x: x["from"]),
        "captions": sorted((x for x in items if x["type"] == "caption" and inside(x)), key=lambda x: x["from"]),
        "assetMap": props["assetMap"],
    }


def load_catalogue() -> list[dict]:
    m = json.loads((DECKS / "teacher-stamped-production-visuals-manifest.v1.json").read_text(encoding="utf-8"))
    cat = []
    for v in m["visuals"]:
        if not v.get("evidence_render_eligible"):
            continue
        ctx = v["context"]
        cat.append({
            "slide_id": v["slide_id"],
            "label": ctx["label"],
            "path": v["extracted_path"],
            "sha256": v["sha256"],
            "deck": v["deck_id"],
            "tokens": Counter(tokens(ctx["label"] + " " + ctx["summary"])),
        })
    return cat


def idf_weights(cat: list[dict]) -> dict[str, float]:
    n = len(cat)
    df = Counter()
    for s in cat:
        df.update(set(s["tokens"]))
    return {w: math.log(n / (1 + c)) + 1.0 for w, c in df.items()}


def pick(cat, weights, said: str, used: set[str], k: int) -> list[dict]:
    q = Counter(tokens(said))
    if not q:
        return []
    scored = []
    for s in cat:
        if s["slide_id"] in used:
            continue
        overlap = sum(weights.get(w, 1.0) * min(c, s["tokens"][w]) for w, c in q.items() if w in s["tokens"])
        if overlap <= 0:
            continue
        scored.append((overlap / (math.sqrt(sum(s["tokens"].values())) or 1), s))
    scored.sort(key=lambda x: -x[0])

    chosen: list[dict] = []
    for score, s in scored:
        if score < 0.3:
            break
        if any(c["deck"] == s["deck"] for c in chosen):
            continue  # a pair should not be two near-identical slides of one deck
        chosen.append(s)
        if len(chosen) == k:
            break
    return chosen


def build(spine, cat, weights) -> dict:
    caps = [(c["from"] / FPS,
             min(c["from"] / FPS + c["durationInFrames"] / FPS, CUT_SECONDS),
             c.get("text", ""))
            for c in spine["captions"]]

    scenes: list[dict] = []
    evidence: dict[str, dict] = {}
    used: set[str] = set()

    for w in spine["worlds"]:
        start = w["from"] / FPS
        end = min(start + w["durationInFrames"] / FPS, CUT_SECONDS)
        if end - start < 4.0:
            continue
        said = " ".join(t for a, b, t in caps if a < end and b > start)
        slots = 2 if end - start >= 14 else 1
        picks = pick(cat, weights, said, used, slots)
        if not picks:
            continue

        span = end - start
        beats = [{"at": round(start, 2), "docks": [], "badges": "----"}]
        mask = ["-", "-", "-", "-"]
        for slot, s in enumerate(picks):
            used.add(s["slide_id"])
            badges = VERIFIED_BADGES.get(s["slide_id"], [])
            evidence[s["slide_id"]] = {
                "title": s["label"],
                "document": {"path": s["path"], "sha256": s["sha256"]},
                "source": f'{s["deck"].replace("-", " ").title()} &middot; slide {s["slide_id"].rsplit("-s", 1)[-1]}',
                "badges": [dict(b, verbatim_in_document=True) for b in badges],
            }
            at = start + 1.6 + slot * (span * 0.42)
            docks = [p["slide_id"] for p in picks[: slot + 1]]
            beats.append({"at": round(at, 2), "docks": docks, "badges": "".join(mask)})
            for bi in range(min(2, len(badges))):
                mask[slot * 2 + bi] = "X"
                step = at + 1.5 * (bi + 1)
                if step < end - 1.0:
                    beats.append({"at": round(step, 2), "docks": docks, "badges": "".join(mask)})

        scenes.append({
            "scene_id": f"s{len(scenes) + 1:02d}",
            "world": {"asset_id": w["assetId"], "sha256": "0" * 64,
                      "ken_burns": KB_CYCLE[len(scenes) % len(KB_CYCLE)]},
            "exit": "wipe_left" if len(scenes) % 2 == 0 else "wipe_right",
            "span": [round(start, 2), round(end, 2)],
            "beats": sorted(beats, key=lambda b: b["at"]),
        })

    return {
        "schema_version": "scene_evidence_timeline.v1",
        "episode_id": "current-bubble-five-minute-v4",
        "project_id": "systems-and-blowups",
        "narration": {"canonical_hash": "0" * 64, "words_path": "edit/semantic-v2/words.json"},
        "captions": [{"at": round(a, 2), "until": round(b, 2), "text": t} for a, b, t in caps],
        "evidence": evidence,
        "scenes": scenes,
    }


def media(tl, spine) -> dict:
    ASSETS.mkdir(parents=True, exist_ok=True)
    from PIL import Image
    uris: dict[str, str] = {}

    def enc(name: str, src: Path, width: int, q: int) -> str:
        dst = ASSETS / f"{name}.jpg"
        im = Image.open(src).convert("RGB")
        if im.width > width:
            im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
        im.save(dst, quality=q, optimize=True)
        return "data:image/jpeg;base64," + base64.b64encode(dst.read_bytes()).decode()

    for aid in {sc["world"]["asset_id"] for sc in tl["scenes"]}:
        uris[aid] = enc(aid, PUBLIC / spine["assetMap"][aid], 1150, 58)
    for sid, ev in tl["evidence"].items():
        uris[sid] = enc(sid, DECKS / ev["document"]["path"], 700, 74)

    dst = ASSETS / "narration.m4a"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i",
                    str(PUBLIC / "current-bubble-fresh-60s-v1/history_episode_1_master.mp3"),
                    "-t", str(CUT_SECONDS), "-ac", "1", "-ar", "32000",
                    "-c:a", "aac", "-b:a", "40k", str(dst)], capture_output=True)
    uris["__audio__"] = "data:audio/mp4;base64," + base64.b64encode(dst.read_bytes()).decode()
    return uris


if __name__ == "__main__":
    spine = load_spine()
    cat = load_catalogue()
    tl = build(spine, cat, idf_weights(cat))
    (OUT / "timeline.v4.json").write_text(json.dumps(tl, indent=1), encoding="utf-8")

    ev = tl["evidence"]
    print(f"scenes={len(tl['scenes'])} beats={sum(len(s['beats']) for s in tl['scenes'])}")
    print(f"evidence={len(ev)} slides, {len(set(e['document']['path'] for e in ev.values()))} distinct files")
    print(f"captions={len(tl['captions'])} at canonical timings")
    print(f"badged={sum(1 for e in ev.values() if e['badges'])} (verified numerals only)")
    for sc in tl["scenes"]:
        ids = sorted({d for b in sc["beats"] for d in b["docks"]})
        print(f"  {sc['scene_id']} {sc['span'][0]:6.1f}-{sc['span'][1]:6.1f}  {', '.join(ids) or '(none)'}")
    uris = media(tl, spine)
    (OUT / "uris.json").write_text(json.dumps(uris), encoding="utf-8")
    print(f"payload {sum(len(v) for v in uris.values()) / 1024 / 1024:.1f} MB")
