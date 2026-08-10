"""Build the sentence-native index chapter review segment.

This is deliberately an isolated 50-second Remotion review composition.  It
uses the canonical narration clock from 410.260s to 460.218s, staged Wave 07
trace-cut layers, and one local source-bound evidence card.  It is not a
replacement for the episode's canonical full-edit props.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
PILOT = REPO_ROOT / "content/video_engine/projects/systems-and-blowups/pilots/current-bubble-mechanism"
SOURCE_START = 410.260
SOURCE_END = 460.218
DEMO_ID = "current-bubble-index-sentence-native-demo-v1"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"expected object: {path}")
    return data


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def stage_file(source: Path, public_root: Path, relative: str) -> str:
    if not source.is_file():
        raise FileNotFoundError(source)
    target = public_root / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    return relative.replace("\\", "/")


def layer(
    asset_id: str,
    role: str,
    action: str,
    z_index: int,
    layout: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {"asset_id": asset_id, "role": role, "action": action, "z_index": z_index}
    if layout:
        payload["layout"] = layout
    return payload


def shot(
    *,
    shot_id: str,
    start_s: float,
    end_s: float,
    excerpt: str,
    focal: tuple[float, float],
    layers: list[dict[str, Any]],
    action: str,
    information: str = "none",
    information_surface: dict[str, Any] | None = None,
    overlay_ids: list[str] | None = None,
    transition_in: dict[str, Any] | None = None,
    camera: dict[str, Any] | None = None,
) -> dict[str, Any]:
    duration_s = round(end_s - start_s, 6)
    return {
        "shot_id": shot_id,
        "parent_beat_ids": [shot_id.replace("demo-shot", "cbm-semantic-beat-06")],
        "parent_scene_bundle_id": "finance-scene-06-index",
        "start_s": round(start_s, 6),
        "duration_s": duration_s,
        "word_range": {"start_index": 0, "end_index": 0},
        "narration_excerpt": excerpt,
        "visual_intent": "explanation",
        "required_visual_actions": [{"kind": "object_cutaway", "subject": action}],
        "purpose": "explain",
        "shot_scale": "medium",
        "focal_point": {"x": focal[0], "y": focal[1]},
        "layers": layers,
        "subject_action": action,
        "ambient_actions": [],
        "information_reveal": information,
        "information_surface": information_surface or {"mode": "none", "x": 0, "y": 0, "width": 0, "height": 0},
        "camera": camera
        or {
            "kind": "foreground_parallax",
            "amount": 0.018,
            "easing": "smoothstep",
            "direction": "left",
            "hold_in_s": 0.18,
            "move_s": max(0.5, duration_s - 0.36),
            "hold_out_s": 0.18,
        },
        "transition_in": transition_in or {"kind": "hard_cut", "reason": "next sentence-native claim", "duration_s": 0.0},
        "transition_out": {"kind": "hard_cut", "reason": "next sentence-native claim", "duration_s": 0.0},
        "audio_bridge": "continuous_narration",
        "provider_motion": {"requirement": "none", "fallback": "local_layer_motion"},
        "overlay_ids": overlay_ids or [],
        "uniqueness_signature": f"{shot_id}:{action}:{focal[0]:.2f}:{focal[1]:.2f}",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--render", action="store_true")
    parser.add_argument("--scale", type=int, choices=(1, 2), default=1)
    args = parser.parse_args()

    revision = PILOT / "animatic/revisions/sentence-native-index-demo-v1"
    public = revision / "public"
    public.mkdir(parents=True, exist_ok=True)
    wave = PILOT / "assets/quarantine/sentence-native-wave-07"
    source_props = read_json(PILOT / "animatic/revisions/full-review-v1/remotion-props-review.json")
    source_audio = PILOT / "animatic/revisions/full-review-v1/public" / source_props["canonical_audio"]["path"]
    asset_map: dict[str, str] = {
        "canonical-audio": stage_file(source_audio, public, "audio/canonical.mp3"),
    }

    plate_stems = {
        "index": "beat-06-001-003-index-product-elevator-v1",
        "dual": "beat-06-004-007-dual-failure-v2",
        "weather": "beat-06-010-shared-causal-weather-v1",
    }
    for short, stem in plate_stems.items():
        for role in ("background", "midground", "foreground", "contact-shadow"):
            asset_id = f"wave07-{short}-{role}"
            asset_map[asset_id] = stage_file(
                wave / f"{stem}--{role}.png",
                public,
                f"assets/{asset_id}.png",
            )

    surface_source = PILOT / "animatic/revisions/full-review-v1/public/assets/evidence-sp500-concentration-v1.svg"
    asset_map["evidence-sp500-concentration-v1"] = stage_file(
        surface_source,
        public,
        "assets/evidence-sp500-concentration-v1.svg",
    )

    index_layers = [
        layer("wave07-index-background", "world", "locked", 0),
        layer("wave07-index-contact-shadow", "depth", "locked", 1),
        layer("wave07-index-midground", "mechanism", "mechanism_open", 5),
        layer("wave07-index-foreground", "prop", "prop_enter_from_left", 6),
    ]
    dual_layers = [
        layer("wave07-dual-background", "world", "locked", 0),
        layer("wave07-dual-contact-shadow", "depth", "locked", 1),
        layer("wave07-dual-midground", "mechanism", "mechanism_split", 5),
        layer("wave07-dual-foreground", "prop", "prop_enter_from_right", 6),
    ]
    weather_layers = [
        layer("wave07-weather-background", "world", "locked", 0),
        layer("wave07-weather-contact-shadow", "depth", "locked", 1),
        layer("wave07-weather-midground", "mechanism", "mechanism_connect", 5),
        layer("wave07-weather-foreground", "prop", "prop_enter_from_left", 6),
    ]
    surface = {"mode": "floating_label", "x": 0.63, "y": 0.10, "width": 0.29, "height": 0.13, "text_align": "left"}
    shots = [
        shot(shot_id="demo-shot-01", start_s=0.000, end_s=2.879, excerpt="Now open the other elevator: the S&P 500 index fund.", focal=(0.44, 0.47), layers=index_layers, action="open_index_product", transition_in={"kind": "paper_wipe", "reason": "moving foreground edge enters over an already-visible index world", "duration_s": 0.28}),
        shot(shot_id="demo-shot-02", start_s=2.879, end_s=6.293, excerpt="An S&P 500 fund can be an excellent product.", focal=(0.58, 0.47), layers=index_layers, action="show_accessible_basket", information="A useful product is not automatically a complete portfolio.", information_surface=surface),
        shot(shot_id="demo-shot-03", start_s=6.293, end_s=10.310, excerpt="It is cheap, liquid, tax-efficient, and historically difficult for active managers to beat after fees.", focal=(0.43, 0.47), layers=index_layers, action="show_index_strengths", camera={"kind": "push_settle", "amount": 0.014, "easing": "smoothstep", "direction": "toward_focal_point", "hold_in_s": 0.18, "move_s": 3.45, "hold_out_s": 0.24}),
        shot(shot_id="demo-shot-04", start_s=10.310, end_s=13.607, excerpt="But the problem is more subtle than concentration alone.", focal=(0.42, 0.48), layers=dual_layers, action="split_two_jobs"),
        shot(shot_id="demo-shot-05", start_s=13.607, end_s=17.765, excerpt="The index can fail both jobs at once. It can be too concentrated to deliver the diversification benefit people think they bought—", focal=(0.31, 0.50), layers=dual_layers, action="show_protection_failure", information="JOB ONE: independent protection", information_surface=surface),
        shot(shot_id="demo-shot-06", start_s=17.765, end_s=21.047, excerpt="—and still too diluted to capture the full upside of the exceptional companies driving its return.", focal=(0.72, 0.48), layers=dual_layers, action="show_upside_failure", information="JOB TWO: follow the strongest economic drivers", information_surface=surface),
        shot(shot_id="demo-shot-07", start_s=21.047, end_s=24.298, excerpt="By the middle of 2025, the ten largest companies", focal=(0.46, 0.45), layers=dual_layers, action="prepare_concentration_evidence"),
        shot(shot_id="demo-shot-08", start_s=24.298, end_s=27.549, excerpt="represented almost forty percent of the S&P 500.", focal=(0.65, 0.45), layers=dual_layers + [layer("evidence-sp500-concentration-v1", "evidence", "reveal", 7, {"x": 0.59, "y": 0.17, "width": 0.32, "height": 0.34, "fit": "contain"})], action="show_top_ten_concentration", overlay_ids=["source-top-ten"]),
        shot(shot_id="demo-shot-09", start_s=27.549, end_s=31.060, excerpt="That weakens the five hundred independent bets story.", focal=(0.49, 0.46), layers=weather_layers, action="move_to_shared_weather", information="One shared causal weather system can move many leaders together.", information_surface=surface),
        shot(shot_id="demo-shot-10", start_s=31.060, end_s=34.473, excerpt="Many of those leaders also share the same causal weather system:", focal=(0.52, 0.42), layers=weather_layers, action="connect_shared_causes"),
        shot(shot_id="demo-shot-11", start_s=34.473, end_s=37.225, excerpt="AI spending, cloud capital expenditure,", focal=(0.28, 0.47), layers=weather_layers, action="show_ai_and_cloud", information="AI spending + cloud capital expenditure", information_surface=surface),
        shot(shot_id="demo-shot-12", start_s=37.225, end_s=40.511, excerpt="semiconductor supply, digital advertising, and premium valuations for long-duration growth.", focal=(0.74, 0.46), layers=weather_layers, action="show_shared_growth_weather", information="Semiconductor supply + digital advertising + long-duration growth", information_surface=surface),
        shot(shot_id="demo-shot-13", start_s=40.511, end_s=46.706, excerpt="But the other four hundred and ninety companies are not there only to offset a top-ten concentration problem.", focal=(0.52, 0.47), layers=weather_layers, action="separate_cause_from_count"),
        shot(shot_id="demo-shot-14", start_s=46.706, end_s=49.958, excerpt="The index is a market-capitalization machine, not a best-ideas selector.", focal=(0.53, 0.46), layers=index_layers, action="return_to_size_weighting", information="The rule is market size—not a forward expected-return ranking.", information_surface=surface),
    ]
    plan = {
        "schema_version": "editorial_motion_plan.v1",
        "source_storyboard_hash": sha256(wave / "wave-07-review-manifest.v1.json"),
        "source_beat_plan_hash": sha256(PILOT / "edit/sentence-native-v1/semantic-beat-ledger.v1.json"),
        "scene_bundle_hashes": [sha256(wave / "wave-07-depth-layer-manifest.v1.json")],
        "scene_flow_graph_hash": sha256(PILOT / "edit/word-timed-v1/scene-flow-graph.v1.json"),
        "asset_map_hash": "pending_props_write",
        "audio_manifest_hash": sha256(PILOT / "audio/current-bubble-mechanism-narration-master.v1.json"),
        "pacing_recipe_hash": sha256(PILOT / "edit/word-timed-v1/pacing-recipe.v1.json"),
        "duration_s": 49.958,
        "source_start_s": SOURCE_START,
        "shots": shots,
        "provider_calls": 0,
        "revision_only": True,
        "artifact_hash": "pending_props_write",
    }
    overlay_map = {
        "source-top-ten": {
            "kind": "text",
            "text": "TOP 10 ≈ 40% OF THE S&P 500\nMid-2025 · Source: S&P Dow Jones Indices + Vanguard",
            "position": "top",
            "from_s": 0.55,
            "duration_s": 2.35,
            "style": {"fontSize": 24, "lineHeight": 1.22, "borderLeft": "6px solid #A44A32", "maxWidth": "43%"},
        }
    }
    props = {
        "plan": plan,
        "asset_map": asset_map,
        "canonical_audio": {"path": asset_map["canonical-audio"], "start_s": SOURCE_START, "volume": 1},
        "overlay_map": overlay_map,
        "caption_policy": "burned_in",
        "citation_policy": "on_screen",
        "diagnostic": False,
        "render_profile": {"width": 1280, "height": 720, "fps": 24, "label": "sentence-native-index-review-720p-12-on-24"},
    }
    asset_map_hash = hashlib.sha256(json.dumps(asset_map, sort_keys=True).encode()).hexdigest()
    plan["asset_map_hash"] = asset_map_hash
    plan["artifact_hash"] = hashlib.sha256(json.dumps(plan, sort_keys=True).encode()).hexdigest()
    props_path = revision / "remotion-props.index-demo.v1.json"
    write_json(props_path, props)

    manifest = {
        "schema_version": "sentence_native_index_demo.v1",
        "episode_id": "systems-and-blowups:current-bubble-mechanism",
        "source_window": {"start_s": SOURCE_START, "end_s": SOURCE_END, "duration_s": 49.958},
        "render_profile": props["render_profile"],
        "paper_motion_fps": 12,
        "delivery_fps": 24,
        "wave_07_review_manifest_sha256": sha256(wave / "wave-07-review-manifest.v1.json"),
        "wave_07_depth_manifest_sha256": sha256(wave / "wave-07-depth-layer-manifest.v1.json"),
        "props_path": props_path.relative_to(REPO_ROOT).as_posix(),
        "props_sha256": sha256(props_path),
        "deterministic_surfaces": ["top-ten concentration card", "short local explanation surfaces", "lower-band narration captions"],
        "status": "prepared",
    }
    write_json(revision / "index-demo-manifest.v1.json", manifest)

    if args.render:
        editor = REPO_ROOT / "content/video_engine/editor"
        target = revision / "current-bubble-index-sentence-native-review.mp4"
        npx = shutil.which("npx.cmd") or shutil.which("npx")
        if not npx:
            raise RuntimeError("npx is required for the Remotion review render")
        command = [
            npx,
            "remotion",
            "render",
            "src/index.tsx",
            "EditorialMotion",
            f"--props={props_path}",
            f"--public-dir={public}",
            f"--scale={args.scale}",
            str(target),
        ]
        result = subprocess.run(command, cwd=editor, check=False)
        if result.returncode != 0:
            raise RuntimeError(f"Remotion render failed: {result.returncode}")
        manifest["render_path"] = target.relative_to(REPO_ROOT).as_posix()
        manifest["render_sha256"] = sha256(target)
        manifest["status"] = "review_render_complete"
        write_json(revision / "index-demo-manifest.v1.json", manifest)
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
