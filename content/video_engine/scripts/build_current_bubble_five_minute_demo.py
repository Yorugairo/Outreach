"""Build the first five minutes of the current-bubble semantic demo.

The cut is intentionally independent from prior editor revisions. It combines
canonical narration/word timing, approved sentence-matched world plates, and
subordinate PowerPoint evidence surfaces in the production timeline renderer.
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
PUBLIC_ROOT = ROOT / "content/video_engine/editor/public"
OUTPUT_DIR = PROJECT / "five-minute-semantic-demo-v3/render"
PROPS_PATH = OUTPUT_DIR / "current-bubble-five-minute-v3.props.json"
MANIFEST_PATH = OUTPUT_DIR / "current-bubble-five-minute-v3.manifest.json"
VIDEO_PATH = OUTPUT_DIR / "current-bubble-five-minute-v3.mp4"
REVIEW_VIDEO_PATH = OUTPUT_DIR / "current-bubble-five-minute-v3.review.mp4"

FPS = 30
DURATION_SECONDS = 300
DURATION_FRAMES = DURATION_SECONDS * FPS


def _frame(seconds: float) -> int:
    return round(seconds * FPS)


ASSET_MAP = {
    "canonical-narration": "current-bubble-fresh-60s-v1/history_episode_1_master.mp3",
    "wrong-bubble-index-fund-world-v1": "current-bubble-fresh-60s-v1/wrong-bubble-index-fund-world-v1.png",
    "memory-skepticism-v2": "current-bubble-fresh-60s-v1/memory-skepticism-v2.png",
    "memory-three-supports-v1": "current-bubble-five-minute-v1/memory-three-supports-v1.png",
    "index-fund-weighted-inflows-v2": "current-bubble-fresh-60s-v1/index-fund-weighted-inflows-v2.png",
    "bottleneck-repricing-v1": "current-bubble-fresh-60s-v1/bottleneck-repricing-v1.png",
    "hidden-index-bubble-inspection-world-v1": "current-bubble-fresh-60s-v1/hidden-index-bubble-inspection-world-v1.png",
    "wrong-bubble-elevators-v2": "current-bubble-five-minute-v1/wrong-bubble-elevators-v2.png",
    "hbm-adjacent-accelerator-v1": "current-bubble-five-minute-v1/hbm-adjacent-accelerator-v1.png",
    "accelerator-memory-bandwidth-gate-v1": "current-bubble-five-minute-v1/accelerator-memory-bandwidth-gate-v1.png",
    "hbm-physical-inputs-gate-v1": "current-bubble-five-minute-v1/hbm-physical-inputs-gate-v1.png",
    "fixed-oven-capacity-wedding-cake-v1": "current-bubble-five-minute-v1/fixed-oven-capacity-wedding-cake-v1.png",
    "commodity-cycle-versus-qualified-agreements-v1": "current-bubble-five-minute-v1/commodity-cycle-versus-qualified-agreements-v1.png",
    "buyer-reservation-rail-v1": "current-bubble-five-minute-v1/buyer-reservation-rail-v1.png",
    "strategic-chokepoint-network-v1": "current-bubble-five-minute-v1/strategic-chokepoint-network-v1.png",
    "valuation-bubble-v1": "current-bubble-fresh-60s-v1/valuation-bubble-v1.png",
    "hbm-stack-v1": "current-bubble-fresh-60s-v1/hbm-stack-v1.png",
    "capacity-penalty-v1": "current-bubble-fresh-60s-v1/capacity-penalty-v1.png",
    "index-concentration-v1": "current-bubble-fresh-60s-v1/index-concentration-v1.png",
    "ram-ageddon-v1": "current-bubble-fresh-60s-v1/ram-ageddon-v1.png",
    "buyer-commitment-evidence-card-v1": "current-bubble-five-minute-v1/buyer-commitment-evidence-card-v1.svg",
    "memory-contracts-evidence-v1": "current-bubble-five-minute-v2/evidence-memory-contracts-v1.svg",
    "sp500-concentration-evidence-v1": "current-bubble-five-minute-v2/evidence-sp500-concentration-v1.svg",
    "index-inclusion-gate-evidence-v1": "current-bubble-five-minute-v2/evidence-index-inclusion-gate-v1.svg",
    "float-weighting-evidence-v1": "current-bubble-five-minute-v2/evidence-float-weighting-v1.svg",
    "automatic-business-mix-evidence-v1": "current-bubble-five-minute-v2/evidence-automatic-business-mix-v1.svg",
    "diagnostic-matrix-evidence-v1": "current-bubble-five-minute-v2/silicon-antidote-s14-diagnostic-matrix-v1.png",
    "triopoly-formation-evidence-v1": "current-bubble-five-minute-v2/silicon-reality-gap-s05-triopoly-formation-v1.png",
    "manufacturing-failure-evidence-v1": "current-bubble-five-minute-v2/silicon-value-software-bubble-s08-failure-triptych-v1.png",
    "two-elevators-model-proposed-v1": "current-bubble-five-minute-v2/two-elevators-mechanism-explainer-proposed-v1.png",
    "whiteboard-draw-hand-a-v1": "current-bubble-fresh-60s-v1/draw-hand-a-v1.png",
}


# Every boundary is a spoken causal turn from the approved composition spine.
WORLD_BEATS = (
    ("opening-wrong-bubble", "wrong-bubble-index-fund-world-v1", 0.000, 2.403),
    ("memory-skepticism", "memory-skepticism-v2", 2.403, 11.610),
    ("memory-supports", "memory-three-supports-v1", 11.610, 23.034),
    ("index-allocation", "index-fund-weighted-inflows-v2", 23.034, 37.720),
    ("memory-risk-return", "memory-three-supports-v1", 37.720, 45.766),
    ("bottleneck-repricing", "bottleneck-repricing-v1", 45.766, 51.920),
    ("safe-default-inspection", "hidden-index-bubble-inspection-world-v1", 51.920, 64.876),
    ("belief-versus-support", "wrong-bubble-elevators-v2", 64.876, 98.800),
    ("allocation-callback", "index-fund-weighted-inflows-v2", 98.800, 108.182),
    ("hbm-adjacent", "hbm-adjacent-accelerator-v1", 108.182, 121.104),
    ("bandwidth-gate", "accelerator-memory-bandwidth-gate-v1", 121.104, 144.613),
    ("physical-inputs", "hbm-physical-inputs-gate-v1", 144.613, 154.726),
    ("fixed-oven", "fixed-oven-capacity-wedding-cake-v1", 154.726, 178.096),
    ("capacity-return", "hbm-physical-inputs-gate-v1", 178.096, 210.164),
    ("cycle-versus-agreements", "commodity-cycle-versus-qualified-agreements-v1", 210.164, 239.664),
    ("buyer-reservations", "buyer-reservation-rail-v1", 239.664, 286.649),
    ("strategic-network", "strategic-chokepoint-network-v1", 286.649, 300.000),
)


EVIDENCE_BEATS = (
    {
        "id": "memory-support-hbm",
        "asset": "hbm-stack-v1",
        "from": 12.15,
        "to": 16.10,
        "layout": {"x": -0.16, "y": 0.22, "width": 0.28, "height": 0.54},
        "source_ref": "The Silicon Reality Gap · S07 · HBM stack",
    },
    {
        "id": "memory-support-capacity",
        "asset": "capacity-penalty-v1",
        "from": 15.75,
        "to": 19.95,
        "layout": {"x": 0.23, "y": 0.22, "width": 0.48, "height": 0.36},
        "source_ref": "The Silicon Antidote · S09 · Three-to-One Capacity Penalty",
    },
    {
        "id": "memory-support-contracts",
        "asset": "memory-contracts-evidence-v1",
        "from": 19.60,
        "to": 22.92,
        "layout": {"x": 0.02, "y": 0.28, "width": 0.54, "height": 0.30},
        "source_ref": "Micron Technology · Fiscal Q3 2026 prepared remarks · pp. 1–2",
    },
    {
        "id": "index-top-ten-concentration",
        "asset": "sp500-concentration-evidence-v1",
        "from": 23.75,
        "to": 28.10,
        "layout": {"x": -0.01, "y": -0.18, "width": 0.45, "height": 0.38},
        "source_ref": "S&P Dow Jones Indices + Vanguard · In the Shadows of Giants · mid-2025 snapshot",
    },
    {
        "id": "index-float-weighting",
        "asset": "float-weighting-evidence-v1",
        "from": 27.75,
        "to": 32.10,
        "layout": {"x": -0.01, "y": -0.18, "width": 0.45, "height": 0.38},
        "source_ref": "S&P Dow Jones Indices · float-adjusted market-cap weighting methodology",
    },
    {
        "id": "index-automatic-business-mix",
        "asset": "automatic-business-mix-evidence-v1",
        "from": 31.75,
        "to": 37.38,
        "layout": {"x": -0.01, "y": -0.18, "width": 0.45, "height": 0.38},
        "source_ref": "Episode mechanism illustration · not a claim about any named company",
    },
    {
        "id": "repricing-triopoly-formation",
        "asset": "triopoly-formation-evidence-v1",
        "from": 46.55,
        "to": 51.62,
        "layout": {"x": 0.21, "y": 0.24, "width": 0.51, "height": 0.34},
        "source_ref": "The Silicon Reality Gap · S05 · Capital-cycle consolidation",
    },
    {
        "id": "mechanism-diagnostic",
        "asset": "diagnostic-matrix-evidence-v1",
        "from": 53.05,
        "to": 59.15,
        "layout": {"x": -0.02, "y": 0.24, "width": 0.50, "height": 0.35},
        "source_ref": "The Silicon Antidote · S14 · Index versus memory diagnostic",
    },
    {
        "id": "mechanism-index-gate",
        "asset": "index-inclusion-gate-evidence-v1",
        "from": 58.80,
        "to": 64.60,
        "layout": {"x": -0.02, "y": 0.24, "width": 0.50, "height": 0.35},
        "source_ref": "S&P Dow Jones Indices · S&P U.S. Indices Methodology · inclusion rules",
    },
    {
        "id": "elevator-mechanism-model",
        "asset": "two-elevators-model-proposed-v1",
        "from": 75.80,
        "to": 89.45,
        "layout": {"x": -0.03, "y": 0.20, "width": 0.49, "height": 0.37},
        "source_ref": "Proposed illustrative model · factual-evidence approval pending",
    },
    {
        "id": "under-elevators-cables",
        "asset": "memory-contracts-evidence-v1",
        "from": 93.10,
        "to": 98.42,
        "layout": {"x": 0.18, "y": 0.23, "width": 0.50, "height": 0.29},
        "source_ref": "Micron Technology · Fiscal Q3 2026 prepared remarks · pp. 1–2",
    },
    {
        "id": "under-elevators-automatic-allocation",
        "asset": "automatic-business-mix-evidence-v1",
        "from": 100.00,
        "to": 107.75,
        "layout": {"x": -0.02, "y": -0.17, "width": 0.45, "height": 0.38},
        "source_ref": "Episode mechanism illustration · not a claim about any named company",
    },
    {
        "id": "hbm-adjacent-stack",
        "asset": "hbm-stack-v1",
        "from": 109.20,
        "to": 120.65,
        "layout": {"x": 0.29, "y": 0.23, "width": 0.28, "height": 0.53},
        "source_ref": "The Silicon Reality Gap · S07 · HBM stack",
    },
    {
        "id": "bandwidth-capacity-penalty",
        "asset": "capacity-penalty-v1",
        "from": 122.00,
        "to": 142.95,
        "layout": {"x": 0.27, "y": 0.23, "width": 0.48, "height": 0.36},
        "source_ref": "The Silicon Antidote · S09 · Three-to-One Capacity Penalty",
    },
    {
        "id": "physical-input-failure-points",
        "asset": "manufacturing-failure-evidence-v1",
        "from": 145.20,
        "to": 154.38,
        "layout": {"x": 0.19, "y": 0.24, "width": 0.53, "height": 0.35},
        "source_ref": "Silicon Value in a Software Bubble · S08 · HBM manufacturing failure points",
    },
    {
        "id": "hbm-capacity-stack",
        "asset": "hbm-stack-v1",
        "from": 180.20,
        "to": 209.40,
        "layout": {"x": -0.08, "y": 0.22, "width": 0.28, "height": 0.54},
        "source_ref": "The Silicon Reality Gap · S07 · HBM stack",
    },
    {
        "id": "hbm-capacity-trade",
        "asset": "capacity-penalty-v1",
        "from": 187.80,
        "to": 209.40,
        "layout": {"x": 0.28, "y": 0.22, "width": 0.48, "height": 0.36},
        "source_ref": "The Silicon Antidote · S09 · Three-to-One Capacity Penalty",
    },
    {
        "id": "cycle-supply-shock",
        "asset": "ram-ageddon-v1",
        "from": 216.00,
        "to": 238.90,
        "layout": {"x": 0.27, "y": 0.25, "width": 0.48, "height": 0.34},
        "source_ref": "The Silicon Antidote · S10 · RAM-ageddon",
    },
    {
        "id": "cycle-buyer-commitment",
        "asset": "buyer-commitment-evidence-card-v1",
        "from": 225.00,
        "to": 238.85,
        "layout": {"x": 0.05, "y": 0.30, "width": 0.64, "height": 0.22},
        "source_ref": "Micron fiscal Q3 2026 prepared remarks · June 24, 2026",
    },
    {
        "id": "buyer-commitment",
        "asset": "buyer-commitment-evidence-card-v1",
        "from": 247.00,
        "to": 262.80,
        "layout": {"x": 0.06, "y": 0.31, "width": 0.70, "height": 0.23},
        "source_ref": "Micron fiscal Q3 2026 prepared remarks · June 24, 2026",
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


def _world_item(item_id: str, asset_id: str, start_s: float, end_s: float, index: int) -> dict[str, Any]:
    start = _frame(start_s)
    end = min(DURATION_FRAMES, _frame(end_s))
    direction = -1 if index % 2 else 1
    return {
        "id": item_id,
        "type": "world_plate",
        "from": start,
        "durationInFrames": end - start,
        "assetId": asset_id,
        "zIndex": 0,
        "layout": {"fit": "cover"},
        "keyframes": {
            "x": [
                {"frame": start, "value": -0.008 * direction, "easing": "ease_in_out"},
                {"frame": end - 1, "value": 0.008 * direction, "easing": "ease_in_out"},
            ],
            "scaleX": [
                {"frame": start, "value": 1.0, "easing": "ease_in_out"},
                {"frame": end - 1, "value": 1.035, "easing": "ease_in_out"},
            ],
            "scaleY": [
                {"frame": start, "value": 1.0, "easing": "ease_in_out"},
                {"frame": end - 1, "value": 1.035, "easing": "ease_in_out"},
            ],
        },
    }


def _caption_layout(start_frame: int, end_frame: int) -> dict[str, float]:
    """Place captions adjacent to the evidence being discussed, never in a box."""
    cue_midpoint_s = ((start_frame + end_frame) / 2) / FPS
    matching = [
        evidence
        for evidence in EVIDENCE_BEATS
        if float(evidence["from"]) < (end_frame / FPS) and float(evidence["to"]) > (start_frame / FPS)
    ]
    if not matching:
        return {"x": -0.18, "y": -0.38, "width": 0.80, "height": 0.20}

    evidence = min(
        matching,
        key=lambda candidate: abs(((float(candidate["from"]) + float(candidate["to"])) / 2) - cue_midpoint_s),
    )
    evidence_layout = evidence["layout"]
    evidence_x = float(evidence_layout["x"])
    evidence_y = float(evidence_layout["y"])
    evidence_height = float(evidence_layout["height"])
    caption_height = 0.20
    vertical_offset = 0.33 * (evidence_height + caption_height) + 0.05
    caption_y = evidence_y + vertical_offset if evidence_y < 0 else evidence_y - vertical_offset
    return {
        "x": max(-0.20, min(0.20, evidence_x)),
        "y": max(-0.36, min(0.36, caption_y)),
        "width": 0.80,
        "height": caption_height,
    }


def _build_items(snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    items = [
        _world_item(item_id, asset_id, start, end, index)
        for index, (item_id, asset_id, start, end) in enumerate(WORLD_BEATS)
    ]

    for evidence in EVIDENCE_BEATS:
        start = _frame(float(evidence["from"]))
        end = _frame(float(evidence["to"]))
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
                        {"frame": max(start, end - 12), "value": 1, "easing": "ease_out"},
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
                "id": f"five-minute-caption-{cue['cue_id']}",
                "type": "caption",
                "from": start,
                "durationInFrames": end - start,
                "cue_id": cue["cue_id"],
                "text": cue["excerpt"],
                "caption_preset": "word_by_word",
                "word_tokens": tokens,
                "fontSize": 38,
                "color": "#fffaf0",
                "backgroundColor": "transparent",
                "zIndex": 72,
                "layout": _caption_layout(start, end),
            }
        )

    items.append(
        {
            "id": "canonical-narration-first-five-minutes",
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
    missing = [name for name in ASSET_MAP.values() if not (PUBLIC_ROOT / name).is_file()]
    if missing:
        raise FileNotFoundError(f"Missing staged five-minute assets: {missing}")

    snapshot = compile_production_editor_snapshot(PROJECT, repository_root=ROOT)
    items = _build_items(snapshot)
    props = {
        "schema_version": "production_console_snapshot.v2",
        "snapshot_id": "current-bubble-five-minute-v3",
        "project_id": "current-bubble-mechanism",
        "composition_id": "ProductionTimeline",
        "width": 1920,
        "height": 1080,
        "fps": FPS,
        "durationInFrames": DURATION_FRAMES,
        "backgroundColor": "#0b1015",
        "diagnosticMode": False,
        "assetMap": ASSET_MAP,
        "items": items,
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    PROPS_PATH.write_text(json.dumps(props, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "schema_version": "semantic_demo_cut.v1",
        "cut_id": "current-bubble-five-minute-v3",
        "duration_frames": DURATION_FRAMES,
        "duration_seconds": DURATION_SECONDS,
        "fps": FPS,
        "world_beat_count": len(WORLD_BEATS),
        "evidence_beat_count": len(EVIDENCE_BEATS),
        "caption_item_count": sum(item["type"] == "caption" for item in items),
        "visual_grammar": {
            "world_plate_is_hero": True,
            "maximum_evidence_per_plate": 3,
            "maximum_simultaneous_evidence": 2,
            "maximum_horizontal_comparison_items": 2,
            "evidence_reveal": "consecutive_hand_draw",
            "visible_source_badge": False,
            "caption_mode": "canonical_word_by_word",
            "plate_motion": "subtle_keyframed_push",
        },
        "source_snapshot_hash": snapshot["artifact_hash"],
        "composition_spine": "edit/semantic-v2/full-episode-composition-spine.v1.json",
        "props_path": PROPS_PATH.relative_to(ROOT).as_posix(),
        "props_sha256": _sha256(PROPS_PATH),
        "asset_sha256": {
            asset_id: _sha256(PUBLIC_ROOT / public_path)
            for asset_id, public_path in ASSET_MAP.items()
        },
    }
    if VIDEO_PATH.is_file():
        manifest["render_path"] = VIDEO_PATH.relative_to(ROOT).as_posix()
        manifest["render_sha256"] = _sha256(VIDEO_PATH)
        manifest["render_bytes"] = VIDEO_PATH.stat().st_size
    if REVIEW_VIDEO_PATH.is_file():
        manifest["review_render_path"] = REVIEW_VIDEO_PATH.relative_to(ROOT).as_posix()
        manifest["review_render_sha256"] = _sha256(REVIEW_VIDEO_PATH)
        manifest["review_render_bytes"] = REVIEW_VIDEO_PATH.stat().st_size
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(PROPS_PATH)
    print(MANIFEST_PATH)
    print(
        f"items={len(items)} worlds={len(WORLD_BEATS)} "
        f"evidence={len(EVIDENCE_BEATS)} captions={manifest['caption_item_count']}"
    )


if __name__ == "__main__":
    main()
