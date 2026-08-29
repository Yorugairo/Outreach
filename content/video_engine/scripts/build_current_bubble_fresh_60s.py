"""Build an isolated one-minute semantic proof for current-bubble-mechanism.

The cut intentionally ignores editor-authored visual revisions. It uses only
canonical cue/word timing, reviewed world plates, and accepted deck evidence.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from content.video_engine.src.services.production_editor import (
    compile_production_editor_snapshot,
)


PROJECT = (
    ROOT
    / "content/video_engine/projects/systems-and-blowups/pilots/current-bubble-mechanism"
)
PUBLIC_DIR = ROOT / "content/video_engine/editor/public/current-bubble-fresh-60s-v1"
OUTPUT_DIR = PROJECT / "fresh-60s-semantic-cut-v3/render"
PROPS_PATH = OUTPUT_DIR / "current-bubble-fresh-60s-v3.props.json"
MANIFEST_PATH = OUTPUT_DIR / "current-bubble-fresh-60s-v3.manifest.json"
VIDEO_PATH = OUTPUT_DIR / "current-bubble-fresh-60s-v3.mp4"

FPS = 30
DURATION_FRAMES = 60 * FPS


ASSET_MAP = {
    "canonical-narration": "current-bubble-fresh-60s-v1/history_episode_1_master.mp3",
    "wrong-bubble-index-fund-world-v1": "current-bubble-fresh-60s-v1/wrong-bubble-index-fund-world-v1.png",
    "memory-skepticism-v2": "current-bubble-fresh-60s-v1/memory-skepticism-v2.png",
    "hero-fab-constraint-v1": "current-bubble-fresh-60s-v1/hero-fab-constraint-v1.png",
    "index-fund-weighted-inflows-v2": "current-bubble-fresh-60s-v1/index-fund-weighted-inflows-v2.png",
    "bottleneck-repricing-v1": "current-bubble-fresh-60s-v1/bottleneck-repricing-v1.png",
    "hidden-index-bubble-inspection-world-v1": "current-bubble-fresh-60s-v1/hidden-index-bubble-inspection-world-v1.png",
    "valuation-bubble-v1": "current-bubble-fresh-60s-v1/valuation-bubble-v1.png",
    "hbm-stack-v1": "current-bubble-fresh-60s-v1/hbm-stack-v1.png",
    "capacity-penalty-v1": "current-bubble-fresh-60s-v1/capacity-penalty-v1.png",
    "index-concentration-v1": "current-bubble-fresh-60s-v1/index-concentration-v1.png",
    "ram-ageddon-v1": "current-bubble-fresh-60s-v1/ram-ageddon-v1.png",
    "whiteboard-draw-hand-a-v1": "current-bubble-fresh-60s-v1/draw-hand-a-v1.png",
}


WORLD_BEATS = (
    ("wrong-bubble-world", "wrong-bubble-index-fund-world-v1", 0, 72),
    ("memory-world", "memory-skepticism-v2", 72, 386),
    ("fab-world", "hero-fab-constraint-v1", 386, 691),
    ("index-world", "index-fund-weighted-inflows-v2", 691, 1175),
    ("bottleneck-world", "bottleneck-repricing-v1", 1175, 1592),
    ("safe-default-world", "hidden-index-bubble-inspection-world-v1", 1592, DURATION_FRAMES),
)


EVIDENCE_BEATS = (
    {
        "id": "valuation-evidence",
        "asset": "valuation-bubble-v1",
        "from": 174,
        "to": 376,
        "layout": {"x": -0.31, "y": 0.22, "width": 0.36, "height": 0.70},
        "source_ref": "The Silicon Antidote · S02 · Great Valuation Paradox",
    },
    {
        "id": "hbm-stack-evidence",
        "asset": "hbm-stack-v1",
        "from": 402,
        "to": 681,
        "layout": {"x": -0.05, "y": 0.20, "width": 0.30, "height": 0.58},
        "source_ref": "The Silicon Reality Gap · S07 · HBM stack",
    },
    {
        "id": "capacity-penalty-evidence",
        "asset": "capacity-penalty-v1",
        "from": 512,
        "to": 681,
        "layout": {"x": 0.26, "y": 0.20, "width": 0.50, "height": 0.38},
        "source_ref": "The Silicon Antidote · S09 · Three-to-One Capacity Penalty",
    },
    {
        "id": "index-concentration-evidence",
        "asset": "index-concentration-v1",
        "from": 714,
        "to": 1163,
        "layout": {"x": 0.00, "y": -0.18, "width": 0.46, "height": 0.38},
        "source_ref": "The Silicon Antidote · S03 · Extreme Concentration",
    },
    {
        "id": "index-valuation-evidence",
        "asset": "valuation-bubble-v1",
        "from": 870,
        "to": 1163,
        "layout": {"x": 0.34, "y": -0.18, "width": 0.27, "height": 0.52},
        "source_ref": "The Silicon Antidote · S02 · Great Valuation Paradox",
    },
    {
        "id": "ram-ageddon-evidence",
        "asset": "ram-ageddon-v1",
        "from": 1380,
        "to": 1580,
        "layout": {"x": 0.29, "y": -0.18, "width": 0.48, "height": 0.34},
        "source_ref": "The Silicon Antidote · S10 · RAM-ageddon",
    },
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _word_tokens(cue: dict[str, Any], words: list[dict[str, Any]]) -> list[dict[str, Any]]:
    start_word = int(cue["start_word"])
    end_word = int(cue["end_word"])
    cue_start = int(cue["start_frame"])
    selected = words[start_word : end_word + 1]
    split_at = (len(selected) + 1) // 2 if len(selected) > 6 else len(selected)
    tokens: list[dict[str, Any]] = []
    for index, word in enumerate(selected):
        absolute_start = int(word["start_frame"])
        if absolute_start >= DURATION_FRAMES:
            continue
        absolute_end = min(DURATION_FRAMES, max(absolute_start + 1, int(word["end_frame"])))
        tokens.append(
            {
                "text": str(word["text"]),
                "startFrame": max(0, absolute_start - cue_start),
                "endFrame": max(1, absolute_end - cue_start),
                "lineGroup": 1 if index < split_at else 2,
            }
        )
    return tokens


def _build_items(snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for item_id, asset_id, start, end in WORLD_BEATS:
        items.append(
            {
                "id": item_id,
                "type": "world_plate",
                "from": start,
                "durationInFrames": end - start,
                "assetId": asset_id,
                "zIndex": 0,
                "layout": {"fit": "cover"},
            }
        )

    for evidence in EVIDENCE_BEATS:
        start = int(evidence["from"])
        end = int(evidence["to"])
        items.append(
            {
                "id": evidence["id"],
                "type": "evidence",
                "from": start,
                "durationInFrames": end - start,
                "assetId": evidence["asset"],
                "source_ref": evidence["source_ref"],
                "evidence_eligible": True,
                "zIndex": 40,
                "layout": evidence["layout"],
                "keyframes": {
                    "opacity": [
                        {"frame": start, "value": 1, "easing": "linear"},
                        {"frame": max(start, end - 10), "value": 1, "easing": "ease_out"},
                        {"frame": end - 1, "value": 0, "easing": "ease_out"},
                    ]
                },
            }
        )

    words = list(snapshot["words"])
    for cue in snapshot["cues"]:
        start = int(cue["start_frame"])
        if start >= DURATION_FRAMES:
            break
        end = min(DURATION_FRAMES, int(cue["end_frame"]))
        tokens = _word_tokens(cue, words)
        if not tokens or end <= start:
            continue
        items.append(
            {
                "id": f"fresh-caption-{cue['cue_id']}",
                "type": "caption",
                "from": start,
                "durationInFrames": end - start,
                "cue_id": cue["cue_id"],
                "text": cue["excerpt"],
                "caption_preset": "word_by_word",
                "word_tokens": tokens,
                "fontSize": 42,
                "color": "#fffaf0",
                "backgroundColor": "rgba(7, 24, 34, 0.84)",
                "zIndex": 72,
                "layout": {"x": -0.20, "y": -0.40, "width": 0.68, "height": 0.16},
            }
        )

    items.append(
        {
            "id": "canonical-narration-first-minute",
            "type": "narration",
            "from": 0,
            "durationInFrames": DURATION_FRAMES,
            "assetId": "canonical-narration",
            "volume": 1,
            "zIndex": 100,
        }
    )
    return items


def main() -> None:
    missing = [name for name in ASSET_MAP.values() if not (PUBLIC_DIR.parent / name).is_file()]
    if missing:
        raise FileNotFoundError(f"Missing staged fresh-cut assets: {missing}")

    snapshot = compile_production_editor_snapshot(PROJECT, repository_root=ROOT)
    props = {
        "schema_version": "production_console_snapshot.v2",
        "snapshot_id": "current-bubble-fresh-60s-v3",
        "project_id": "current-bubble-mechanism",
        "composition_id": "ProductionTimeline",
        "width": 1920,
        "height": 1080,
        "fps": FPS,
        "durationInFrames": DURATION_FRAMES,
        "backgroundColor": "#0b1015",
        "diagnosticMode": False,
        "assetMap": ASSET_MAP,
        "items": _build_items(snapshot),
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    PROPS_PATH.write_text(json.dumps(props, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "schema_version": "fresh_semantic_cut.v1",
        "cut_id": "current-bubble-fresh-60s-v3",
        "duration_frames": DURATION_FRAMES,
        "fps": FPS,
        "visual_grammar": {
            "world_plate_is_hero": True,
            "maximum_evidence_per_plate": 3,
            "maximum_simultaneous_evidence": 2,
            "maximum_horizontal_comparison_items": 2,
            "caption_mode": "canonical_word_by_word",
        },
        "source_snapshot_hash": snapshot["artifact_hash"],
        "props_path": PROPS_PATH.relative_to(ROOT).as_posix(),
        "props_sha256": _sha256(PROPS_PATH),
        "asset_sha256": {
            asset_id: _sha256(PUBLIC_DIR.parent / public_path)
            for asset_id, public_path in ASSET_MAP.items()
        },
    }
    if VIDEO_PATH.is_file():
        manifest["render_path"] = VIDEO_PATH.relative_to(ROOT).as_posix()
        manifest["render_sha256"] = _sha256(VIDEO_PATH)
        manifest["render_bytes"] = VIDEO_PATH.stat().st_size
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(PROPS_PATH)
    print(MANIFEST_PATH)
    print(f"items={len(props['items'])}")


if __name__ == "__main__":
    main()
