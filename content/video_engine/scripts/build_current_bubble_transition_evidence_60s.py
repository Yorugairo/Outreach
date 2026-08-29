"""Build the review-only one-minute transition palette proof.

The source beat map, canonical word timing, audio, and approved evidence are
identical to the fresh v3 cut. This emits a separate v4 props artifact that
selects the transition-palette composition instead of modifying the approved
baseline cut.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import build_current_bubble_fresh_60s as base


ROOT = Path(__file__).resolve().parents[3]
PROJECT = ROOT / "content/video_engine/projects/systems-and-blowups/pilots/current-bubble-mechanism"
OUTPUT_DIR = PROJECT / "fresh-60s-transition-evidence-v4/render"
PROPS_PATH = OUTPUT_DIR / "current-bubble-transition-evidence-60s-v4.props.json"
MANIFEST_PATH = OUTPUT_DIR / "current-bubble-transition-evidence-60s-v4.manifest.json"
VIDEO_PATH = OUTPUT_DIR / "current-bubble-transition-evidence-60s-v4.mp4"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    base.OUTPUT_DIR = OUTPUT_DIR
    base.PROPS_PATH = PROPS_PATH
    base.MANIFEST_PATH = MANIFEST_PATH
    base.VIDEO_PATH = VIDEO_PATH
    base.main()

    props = json.loads(PROPS_PATH.read_text(encoding="utf-8"))
    props["snapshot_id"] = "current-bubble-transition-evidence-60s-v4"
    props["composition_id"] = "TransitionEvidence60sProof"
    PROPS_PATH.write_text(json.dumps(props, indent=2) + "\n", encoding="utf-8")

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    manifest["cut_id"] = "current-bubble-transition-evidence-60s-v4"
    manifest["props_path"] = PROPS_PATH.relative_to(ROOT).as_posix()
    manifest["props_sha256"] = sha256(PROPS_PATH)
    manifest["transition_palette"] = {
        "world_plate_motion": "ken_burns",
        "scene_breaks": {
            "72": "clean_cut",
            "386": "3d_book_flip",
            "691": "directional_wipe",
            "1175": "clean_cut",
            "1592": "3d_book_flip",
        },
        "rule": "Use a transition only at a semantic scene break; no evidence item is active at a decorated break.",
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(PROPS_PATH)
    print(MANIFEST_PATH)


if __name__ == "__main__":
    main()
