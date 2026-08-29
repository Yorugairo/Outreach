"""Steel and Paper — convert the Script F build into `scene_evidence_timeline.v1`
and render through the established player.

There is already a player: `samples/scene-evidence-player.template.html`.
This script feeds it. It does NOT write a new one — a bespoke player was
built and discarded once already, and it rendered black because it
referenced assets by path instead of embedding them.

The schema encodes things a flat cue list does not: a scene OWNS its world
plate and that plate's Ken Burns move; docks carry a semantic SLOT so
evidence roams while the caption anchor never moves; evidence carries badges
and a source line.
"""
from __future__ import annotations

import base64
import hashlib
import json
import mimetypes
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
EP = REPO / "content/video_engine/projects/systems-and-blowups/steel-and-paper"
BUILD = EP / "build-f"
TEMPLATE = REPO / "docs/content-video-engine/samples/scene-evidence-player.template.html"
sys.path.insert(0, str(Path(__file__).parent))
import build_render_f as R  # noqa: E402  (asset resolver + doc-29 durations)

# Ken Burns: doc 29 §1.4 — the world plate drifts while evidence holds locked,
# so the eye separates narrative world from evidence data with no labelling.
KEN = {"scale": 0.04, "x": 14, "y": -10}


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def data_uri(p: Path) -> str:
    mime = mimetypes.guess_type(p.name)[0] or "application/octet-stream"
    return f"data:{mime};base64,{base64.b64encode(p.read_bytes()).decode()}"


def title_for(asset: str) -> tuple[str, str]:
    """Human title and source line for an evidence asset."""
    if asset.startswith("ev-"):
        return asset[3:].replace("-", " ").replace(" v1", "").replace(" v2", "") \
            .replace(" v3", "").title(), "Money Physics — built evidence"
    stamped = json.loads((BUILD / "stamped-index.json").read_text(encoding="utf-8"))
    if asset in stamped:
        deck = asset.split("-s")[0].replace("-", " ").title()
        return asset.replace("-teacher-stamped", "").split("-")[-1].upper(), deck
    return asset.replace("-", " ").title(), "Research deck"


def main() -> int:
    tl = json.loads((BUILD / "timeline.json").read_text(encoding="utf-8"))
    # THE AUTHORED SHOT TABLE is the source. Not an allocator.
    import importlib.util
    sp = importlib.util.spec_from_file_location("shot", EP / "SHOT-TABLE-F.py")
    shot = importlib.util.module_from_spec(sp); sp.loader.exec_module(shot)
    plan = sorted(shot.W)
    dock = json.loads((BUILD / "evidence-dock.json").read_text(encoding="utf-8"))
    META = {d["asset"]: d for d in dock}
    pages = json.loads((BUILD / "caption-pages.json").read_text(encoding="utf-8"))
    audio = BUILD / "audio/episode.mp3"
    if not audio.exists():
        print(f"FAIL: {audio} missing — join the chained parts first")
        return 1

    evidence, uris, scenes = {}, {}, []
    for i, (a, b, plate, ken, ds) in enumerate(plan):
        # each window runs to the next so the world layer never drops out
        b = plan[i + 1][0] if i + 1 < len(plan) else tl["runtime_s"]
        wp = R.find_asset(plate)
        uris[plate] = data_uri(wp)
        docks = []
        for aid, slot, enter, exitt in ds:
            d = META.get(aid, {"title": aid, "source": "", "species": "deck",
                               "badges": []})
            if True:
                if aid not in evidence:
                    ap = R.find_asset(aid)
                    evidence[aid] = {
                        # Authored in the dock - a machine-mangled asset id is
                        # not a title, and empty badges leave the card's whole
                        # information layer blank (ruling B3: a badge numeral
                        # must appear verbatim in the document behind it).
                        "title": d["title"], "source": d["source"],
                        "species": d["species"],
                        "document": {"path": str(ap.relative_to(ap.anchor)),
                                     "sha256": sha(ap)},
                        "badges": d["badges"],
                    }
                    uris[aid] = data_uri(ap)
                # Spans come from the dock: evidence enters before its claim
                # and holds through the whole discussion. A flat hold drops the
                # document mid-argument, which is what left 42% of claims naked.
                docks.append({
                    "slide": aid, "slot": slot,
                    "enter": round(enter, 2), "exit": round(exitt, 2),
                    "badge_at": [round(enter + 0.75 + 1.3 * (n + 1), 2)
                                 for n in range(len(d["badges"]))],
                })
        scenes.append({
            "scene_id": f"s{i+1:02d}",
            # Ken Burns is AUTHORED per shot in the table, not one constant.
            "world": {"asset_id": plate, "sha256": sha(wp),
                      "ken_burns": {"scale": ken[0], "x": ken[1], "y": ken[2]}},
            "exit": "wipe_right" if docks else "cut",
            "span": [round(a, 2), round(b, 2)],
            "docks": docks,
        })

    uris["__audio__"] = data_uri(audio)

    timeline = {
        "schema_version": "scene_evidence_timeline.v1",
        "runtime_s": tl["runtime_s"],
        "title": "Steel and Paper",
        "subtitle": "Money Physics · answer to Bravos Research",
        "episode_id": "steel-and-paper", "project_id": "systems-and-blowups",
        "narration": {"canonical_hash": sha(audio),
                      "words_path": "build-f/timeline.json"},
        # Block captions for the template's own layer; the kinetic layer reads
        # caption_pages. Both carry CANONICAL timings — never resampled onto
        # beat boundaries (doc 29 Part 5, and the standing correction).
        "captions": [{"at": p["s"], "until": p["e"],
                      "text": " ".join(t["w"] for t in p["t"])} for p in pages],
        "caption_pages": pages,
        "evidence": evidence,
        "scenes": scenes,
    }
    (BUILD / "steel-and-paper.timeline.json").write_text(
        json.dumps(timeline, indent=1), encoding="utf-8")

    html = TEMPLATE.read_text(encoding="utf-8")
    html = html.replace("{{TIMELINE}}", json.dumps(timeline, separators=(",", ":")))
    html = html.replace("{{URIS}}", json.dumps(uris, separators=(",", ":")))
    out = BUILD / "player.html"
    out.write_text(html, encoding="utf-8")

    dur = float(subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(audio)], capture_output=True, text=True).stdout or 0)
    print(f"scene_evidence_timeline.v1")
    print(f"  scenes      : {len(scenes)}  (one per world plate)")
    print(f"  docks       : {sum(len(s['docks']) for s in scenes)} across "
          f"{sum(1 for s in scenes if s['docks'])} scenes")
    print(f"  evidence    : {len(evidence)} assets")
    print(f"  captions    : {len(timeline['captions'])} lines / "
          f"{sum(len(p['t']) for p in pages)} tokens")
    print(f"  audio       : {dur:.2f}s embedded as __audio__")
    print(f"  URIs        : {len(uris)} embedded, {out.stat().st_size/1e6:.0f} MB player")
    print(f"  wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
