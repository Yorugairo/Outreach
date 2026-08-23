"""Build a six-minute P32 review cut from approved world plates and deck evidence.

This produces a derived review artifact only. It never promotes a source
surface or changes factual/evidence approvals. The renderer may apply a
non-destructive source-bound crop that retains the teacher stamp; it never
writes an altered deck file. The resulting timeline keeps a world plate as the
hero while completed evidence cards can remain together after their sequential
hand reveals.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
from argparse import ArgumentParser
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from content.video_engine.src.services.production_editor import (  # noqa: E402
    compile_production_editor_snapshot,
)


PROJECT = ROOT / "content/video_engine/projects/systems-and-blowups/pilots/current-bubble-mechanism"
COVERAGE_PATH = PROJECT / "edit/evidence-coverage-v1/full-episode-evidence-coverage.v1.json"
PUBLIC_ROOT = ROOT / "content/video_engine/editor/public"
STAGED_DIR = PUBLIC_ROOT / "current-bubble-six-minute-p32-v1"
OUTPUT_DIR = PROJECT / "six-minute-p32-evidence-demo-v1/render"
PROPS_PATH = OUTPUT_DIR / "current-bubble-six-minute-p32-v1.props.json"
MANIFEST_PATH = OUTPUT_DIR / "current-bubble-six-minute-p32-v1.manifest.json"
VIDEO_PATH = OUTPUT_DIR / "current-bubble-six-minute-p32-v1.mp4"
GATE_A_REVIEW_VIDEO_PATH = OUTPUT_DIR / "current-bubble-six-minute-p32-v1.gate-a-review.mp4"
GATE_A_REVIEW_V3_VIDEO_PATH = OUTPUT_DIR / "current-bubble-six-minute-p32-v1.gate-a-review-v3.mp4"
P33_REVIEW_VIDEO_PATH = OUTPUT_DIR / "current-bubble-six-minute-p33-first-five-review.mp4"
P33_OBLIGATION_PATH = PROJECT / "edit/evidence-coverage-v1/p33-first-five-minute-evidence-obligation.v1.json"
P33_ELEVATOR_APPROVAL_PATH = PROJECT / "edit/evidence-coverage-v1/p33-gate-a-two-elevator-review/two-elevator-mechanism-approval.v1.json"

FPS = 24
DURATION_SECONDS = 360
DURATION_FRAMES = DURATION_SECONDS * FPS
MAX_EVIDENCE_PER_WORLD = 3
EVIDENCE_CARD_SCALE = 1.20
# Hold evidence long enough for a mobile viewer to read the cropped, stamped
# source surface after its hand reveal completes.
EVIDENCE_HOLD_SECONDS = 8.0
EVIDENCE_REVEAL_SECONDS = 1.05
EVIDENCE_REVEAL_GAP_SECONDS = 2.50
MAX_SIMULTANEOUS_EVIDENCE = 3
FIRST_FIVE_MINUTES_SECONDS = 300.0

EVIDENCE_LAYOUTS = (
    # Two readable cards may share the lower evidence rail. A third, smaller
    # card can occupy the upper slot only after the two lower cards are drawn.
    {"x": -0.24, "y": -0.10, "width": 0.42, "height": 0.48, "scaleX": EVIDENCE_CARD_SCALE, "scaleY": EVIDENCE_CARD_SCALE},
    {"x": 0.23, "y": -0.10, "width": 0.42, "height": 0.48, "scaleX": EVIDENCE_CARD_SCALE, "scaleY": EVIDENCE_CARD_SCALE},
    {"x": 0.00, "y": -0.40, "width": 0.36, "height": 0.41, "scaleX": EVIDENCE_CARD_SCALE, "scaleY": EVIDENCE_CARD_SCALE},
)
# The crop's right and bottom edges are the source edges: that keeps the
# teacher stamp intact while trimming only the unused top/left slide gutter.
TEACHER_STAMP_SAFE_SOURCE_CROP = {"x": 0.012, "y": 0.012, "width": 0.988, "height": 0.988}
# Captions are a stable lower-third anchor. Evidence moves by semantic slot;
# the canonical narration should not send the viewer searching around the frame.
STANDARD_CAPTION_LOWER_THIRD = {"x": -0.18, "y": 0.34, "width": 0.80, "height": 0.16}

# The city-in-a-box plate reads as documents rather than an immediately legible
# world. Replace every appearance in this review cut with literal, already
# composition-approved scenes. These are local editorial substitutions only;
# the source coverage map remains immutable.
WORLD_BEAT_ASSET_OVERRIDES = {
    (0.0, 2.403): "hero-wrong-bubble-v1",
    (9.532, 12.875): "sentence-native-beat-01-003-bubble-reflex-v1",
    (53.046, 64.876): "sentence-native-beat-01-013-hidden-safe-index-loop-v1",
    (64.876, 70.901): "sentence-native-beat-02-003-next-buyer-belief-v1",
    (70.901, 78.935): "two-elevator-mechanism-v1",
    (78.935, 86.169): "two-elevator-mechanism-v1",
    (86.169, 89.803): "two-elevator-mechanism-v1",
    (89.803, 92.833): "sentence-native-beat-01-013-hidden-safe-index-loop-v1",
}
# These legacy resolution segments name fact graphics, not world plates. Keep
# the last approved automatic-allocation world as the hero while those facts
# enter through the evidence track.
WORLD_BEAT_ASSET_OVERRIDES.update({
    (464.548, 475.055): "shared-cause-automatic-allocation-v1",
    (475.055, 484.854): "shared-cause-automatic-allocation-v1",
    (484.854, 495.280): "shared-cause-automatic-allocation-v1",
})

# The source cadence map did not need a cut between the next-buyer visual and
# the literal elevator comparison. P33 adds that semantic boundary locally.
WORLD_BEAT_CUTS = (70.901,)
P33_WORLD_PLATE_SOURCES = {
    "two-elevator-mechanism-v1": {
        "asset_id": "two-elevator-mechanism-v1",
        "path": "pilots/current-bubble-mechanism/assets/quarantine/p33-two-elevator-mechanism-v1/two-elevator-mechanism-v1.png",
        "composition_approval": "p33_gate_a_approved",
    }
}

# P33 uses exact approved whole-slide bindings where automatic semantic
# candidates were sparse. These slots are deliberately off-center and remain
# one-at-a-time with no on-screen source label.
P33_EXPLICIT_EVIDENCE_BINDINGS = {
    (53.046, 64.876): {
        "asset_id": "silicon-reality-gap-s12-teacher-stamped",
        "cue_id": "cbm-cue-017",
        "layout_index": 1,
        "match_basis": "p33_explicit_safe_index_feedback",
    },
    (64.876, 70.901): {
        "asset_id": "silicon-antidote-s14-teacher-stamped",
        "cue_id": "cbm-cue-021",
        "layout_index": 1,
        "match_basis": "p33_explicit_next_buyer_diagnostic",
    },
    (70.901, 89.803): {
        "asset_id": "silicon-antidote-s02-teacher-stamped",
        "cue_id": "cbm-cue-024",
        "layout_index": 1,
        "match_basis": "p33_explicit_two_elevator_comparison",
    },
    (230.164, 239.664): {
        "asset_id": "memory-supercycle-s06-teacher-stamped",
        "cue_id": "cbm-cue-068",
        "layout_index": 0,
        "match_basis": "p33_explicit_strategic_agreements",
    },
}
P33_ANALOGY_EXEMPTIONS = {
    "fixed-oven-capacity-wedding-cake-v1": {
        "reason": "direct explanatory analogy; source-card evidence is not required",
        "permitted_future_evidence": "silicon-antidote-s09-teacher-stamped",
    }
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _frame(seconds: float) -> int:
    return round(seconds * FPS)


def _world_library(coverage: dict[str, Any]) -> dict[str, dict[str, Any]]:
    library = {entry["asset_id"]: dict(entry) for entry in coverage["world_plate_library"]}
    if not P33_ELEVATOR_APPROVAL_PATH.is_file():
        raise FileNotFoundError("P33 elevator plate requires its Gate A approval artifact")
    elevator_approval = json.loads(P33_ELEVATOR_APPROVAL_PATH.read_text(encoding="utf-8"))
    elevator_source = _resolve_repo_path(P33_WORLD_PLATE_SOURCES["two-elevator-mechanism-v1"]["path"])
    if (
        elevator_approval.get("operator_decision") != "approved_for_composition"
        or elevator_approval.get("asset_sha256") != _sha256(elevator_source)
    ):
        raise ValueError("P33 elevator plate approval is missing, stale, or not composition-approved")
    library.update(P33_WORLD_PLATE_SOURCES)
    return library


def _resolve_repo_path(relative_path: str) -> Path:
    """Resolve only against explicit project roots; reject absent inputs."""
    raw = Path(relative_path.replace("/", "\\"))
    roots = (
        ROOT,
        ROOT / "content/video_engine",
        ROOT / "content/video_engine/projects/systems-and-blowups",
    )
    for root in roots:
        candidate = (root / raw).resolve()
        try:
            candidate.relative_to(root.resolve())
        except ValueError:
            continue
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(f"Coverage asset could not be resolved: {relative_path}")


def _stage(asset_id: str, source_path: Path) -> str:
    """Stage a hash-checked, renderer-local copy and return its public path."""
    suffix = source_path.suffix.lower()
    target = STAGED_DIR / f"{asset_id}{suffix}"
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.is_file() or _sha256(target) != _sha256(source_path):
        shutil.copy2(source_path, target)
    return target.relative_to(PUBLIC_ROOT).as_posix()


def _timeline_frame(source_frame: int, source_fps: int) -> int:
    return round(source_frame * FPS / source_fps)


def _word_tokens(cue: dict[str, Any], words: list[dict[str, Any]], source_fps: int) -> list[dict[str, Any]]:
    cue_start = _timeline_frame(int(cue["start_frame"]), source_fps)
    selected = words[int(cue["start_word"]) : int(cue["end_word"]) + 1]
    split_at = (len(selected) + 1) // 2 if len(selected) > 6 else len(selected)
    tokens: list[dict[str, Any]] = []
    for index, word in enumerate(selected):
        absolute_start = _timeline_frame(int(word["start_frame"]), source_fps)
        if absolute_start >= DURATION_FRAMES:
            continue
        absolute_end = min(DURATION_FRAMES, max(absolute_start + 1, _timeline_frame(int(word["end_frame"]), source_fps)))
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
    start, end = _frame(start_s), min(DURATION_FRAMES, _frame(end_s))
    direction = -1 if index % 2 else 1
    return {
        "id": item_id,
        "type": "world_plate",
        "from": start,
        "durationInFrames": max(1, end - start),
        "assetId": asset_id,
        "zIndex": 0,
        "layout": {"fit": "cover"},
        # Use the curated Remotion Bits adapter for plate motion. Evidence
        # remains a separate, stable surface above this item.
        "bit": {
            "id": "ken-burns-effect",
            "props": {
                "images": [asset_id],
                "scaleFrom": 1.025,
                "scaleTo": 1.085,
                "direction": "right" if direction > 0 else "left",
            },
        },
        "keyframes": {
            "x": [
                {"frame": start, "value": -0.008 * direction, "easing": "ease_in_out"},
                {"frame": end - 1, "value": 0.008 * direction, "easing": "ease_in_out"},
            ],
            "scaleX": [
                {"frame": start, "value": 1.0, "easing": "ease_in_out"},
                {"frame": end - 1, "value": 1.01, "easing": "ease_in_out"},
            ],
            "scaleY": [
                {"frame": start, "value": 1.0, "easing": "ease_in_out"},
                {"frame": end - 1, "value": 1.01, "easing": "ease_in_out"},
            ],
        },
    }


def _motion_bit_item(
    item_id: str,
    bit_id: str,
    start_s: float,
    end_s: float,
    props: dict[str, Any],
    layout: dict[str, Any],
    z_index: int = 52,
) -> dict[str, Any]:
    start, end = _frame(start_s), min(DURATION_FRAMES, _frame(end_s))
    return {
        "id": item_id,
        "type": "remotion_bit",
        "from": start,
        "durationInFrames": max(1, end - start),
        "bit": {"id": bit_id, "props": props},
        "layout": layout,
        "zIndex": z_index,
    }


def _build_motion_bit_items() -> list[dict[str, Any]]:
    """Add restrained numeric and label motion to the first six minutes.

    These values are direct claims already present in the approved coverage
    map. Bits animate the compact emphasis; the evidence cards remain the
    factual reading surface.
    """
    return [
        _motion_bit_item(
            "bit-counter-index-concentration",
            "basic-counter",
            28.606,
            34.10,
            {
                "from": 0,
                "to": 40,
                "postfix": "%",
                "durationInFrames": _frame(2.4),
                "fontSize": 92,
                "color": "#f5d08a",
                "style": {"fontWeight": 850, "textShadow": "0 3px 14px rgba(0,0,0,.42)"},
            },
            {"x": -0.18, "y": -0.30, "width": 0.30, "height": 0.18},
            48,
        ),
        _motion_bit_item(
            "bit-label-index-concentration",
            "basic-typewriter",
            29.00,
            35.25,
            {
                "text": "NEARLY 40% OF INDEX WEIGHT",
                "typeSpeedFrames": 2,
                "showCursor": False,
                "fontSize": 28,
                "color": "#f7f1e4",
                "style": {"fontWeight": 760, "letterSpacing": 1.1, "textAlign": "left", "justifyContent": "flex-start"},
            },
            {"x": -0.06, "y": -0.18, "width": 0.46, "height": 0.10},
            49,
        ),
        _motion_bit_item(
            "bit-counter-contract-duration",
            "basic-counter",
            236.39,
            242.75,
            {
                "from": 0,
                "to": 5,
                "postfix": " yrs",
                "durationInFrames": _frame(2.1),
                "fontSize": 74,
                "color": "#a9ddc1",
                "style": {"fontWeight": 820, "textShadow": "0 3px 14px rgba(0,0,0,.42)"},
            },
            {"x": 0.18, "y": -0.29, "width": 0.34, "height": 0.16},
            48,
        ),
        _motion_bit_item(
            "bit-label-contract-duration",
            "basic-typewriter",
            237.00,
            244.00,
            {
                "text": "LONG-TERM AGREEMENTS",
                "typeSpeedFrames": 2,
                "showCursor": False,
                "fontSize": 26,
                "color": "#f7f1e4",
                "style": {"fontWeight": 760, "letterSpacing": 1.05, "textAlign": "left", "justifyContent": "flex-start"},
            },
            {"x": 0.18, "y": -0.17, "width": 0.38, "height": 0.10},
            49,
        ),
    ]


def _build_world_beats(coverage: dict[str, Any]) -> list[dict[str, Any]]:
    library = _world_library(coverage)
    turns_by_parent: dict[str, list[dict[str, Any]]] = {}
    for turn in coverage["cadence_turns"]:
        if turn["at_s"] < DURATION_SECONDS:
            turns_by_parent.setdefault(turn["parent_asset_id"], []).append(turn)

    beats: list[dict[str, Any]] = []
    last_approved_world_asset: str | None = None
    for segment in coverage["resolution_segments"]:
        segment_start, segment_end = float(segment["start_s"]), min(DURATION_SECONDS, float(segment["end_s"]))
        if segment_start >= DURATION_SECONDS or segment_end <= segment_start:
            continue
        active_asset = segment["asset_id"]
        boundaries = [segment_start]
        turns = [turn for turn in turns_by_parent.get(active_asset, []) if segment_start < float(turn["at_s"]) < segment_end]
        turns_by_boundary = {round(float(turn["at_s"]), 3): turn for turn in turns}
        boundaries.extend(float(turn["at_s"]) for turn in turns)
        boundaries.extend(cut for cut in WORLD_BEAT_CUTS if segment_start < cut < segment_end)
        boundaries.append(segment_end)
        boundaries = sorted(set(boundaries))
        for index in range(len(boundaries) - 1):
            if index:
                candidate = turns_by_boundary.get(round(boundaries[index], 3), {}).get("candidate_world_asset") or {}
                candidate_id = candidate.get("asset_id")
                if candidate_id in library:
                    active_asset = candidate_id
            override = WORLD_BEAT_ASSET_OVERRIDES.get(
                (round(boundaries[index], 3), round(boundaries[index + 1], 3))
            )
            if override:
                if override not in library:
                    raise ValueError(f"World plate override is absent from approved library: {override}")
                active_asset = override
            if active_asset not in library:
                if active_asset.startswith("evidence-") and last_approved_world_asset:
                    active_asset = last_approved_world_asset
                else:
                    raise ValueError(f"World plate is absent from approved library: {active_asset}")
            beats.append(
                {
                    "id": f"world-{len(beats) + 1:03d}-{active_asset}",
                    "asset_id": active_asset,
                    "start_s": boundaries[index],
                    "end_s": boundaries[index + 1],
                }
            )
            last_approved_world_asset = active_asset
    merged: list[dict[str, Any]] = []
    for beat in beats:
        if merged and merged[-1]["asset_id"] == beat["asset_id"] and abs(merged[-1]["end_s"] - beat["start_s"]) < 0.001:
            merged[-1]["end_s"] = beat["end_s"]
            continue
        merged.append(beat)
    for index, beat in enumerate(merged, start=1):
        beat["id"] = f"world-{index:03d}-{beat['asset_id']}"
    return merged


def _source_surface_library(coverage: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        source["asset_id"]: source
        for source in coverage["approved_source_surfaces"]
        if source.get("evidence_state") == "production_ready"
    }


def _explicit_evidence_beat(
    binding: dict[str, Any], world: dict[str, Any], source_surfaces: dict[str, dict[str, Any]], cues: dict[str, dict[str, Any]], ordinal: int
) -> dict[str, Any]:
    source = source_surfaces[binding["asset_id"]]
    cue = cues[binding["cue_id"]]
    start_s = max(float(world["start_s"]) + 0.55, float(cue["start_s"]) + 0.15)
    end_s = min(float(world["end_s"]) - 0.25, start_s + EVIDENCE_HOLD_SECONDS)
    if end_s - start_s < 2.2:
        raise ValueError(f"P33 binding cannot maintain a readable hold: {binding['asset_id']}")
    return {
        "id": f"evidence-{ordinal:03d}-{source['asset_id']}",
        "asset_id": source["asset_id"],
        "path": source["path"],
        "sha256": source["sha256"],
        "cue_id": cue["cue_id"],
        "world_id": world["id"],
        "binding_state": "p33_explicit_approved_source",
        "match_basis": binding["match_basis"],
        "start_s": start_s,
        "end_s": end_s,
        "layout": EVIDENCE_LAYOUTS[int(binding["layout_index"])],
        "sourceCrop": TEACHER_STAMP_SAFE_SOURCE_CROP,
        "source_ref": f"{source['deck_id']} · slide {source['slide_number']}",
    }


def _build_evidence_beats(coverage: dict[str, Any], world_beats: list[dict[str, Any]]) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []
    recent_asset_ids: list[str] = []
    cues = [cue for cue in coverage["cues"] if float(cue["start_s"]) < DURATION_SECONDS]
    cue_by_id = {cue["cue_id"]: cue for cue in cues}
    source_surfaces = _source_surface_library(coverage)
    for world in world_beats:
        world_key = (round(float(world["start_s"]), 3), round(float(world["end_s"]), 3))
        binding = P33_EXPLICIT_EVIDENCE_BINDINGS.get(world_key)
        if binding:
            evidence.append(_explicit_evidence_beat(binding, world, source_surfaces, cue_by_id, len(evidence) + 1))
            continue
        matching = [
            cue
            for cue in cues
            if cue.get("candidate_evidence")
            and float(cue["start_s"]) < world["end_s"]
            and float(cue["end_s"]) > world["start_s"]
        ]
        last_draw_start = float(world["start_s"]) - EVIDENCE_REVEAL_SECONDS
        inserted = 0
        for cue in matching:
            candidates = [
                candidate
                for candidate in cue.get("candidate_evidence", [])
                if candidate.get("evidence_state") == "production_ready"
                and candidate["asset_id"] not in recent_asset_ids
            ]
            for candidate in candidates:
                if inserted >= MAX_EVIDENCE_PER_WORLD:
                    break
                start_s = max(
                    world["start_s"] + 0.55,
                    float(cue["start_s"]) + 0.15,
                    last_draw_start + EVIDENCE_REVEAL_SECONDS + EVIDENCE_REVEAL_GAP_SECONDS,
                )
                end_s = min(world["end_s"] - 0.25, start_s + EVIDENCE_HOLD_SECONDS)
                if end_s - start_s < 2.2:
                    break
                evidence.append(
                    {
                        "id": f"evidence-{len(evidence) + 1:03d}-{candidate['asset_id']}",
                        "asset_id": candidate["asset_id"],
                        "path": candidate["path"],
                        "sha256": candidate["sha256"],
                        "cue_id": cue["cue_id"],
                        "world_id": world["id"],
                        "binding_state": "gate_a_review_candidate",
                        "match_basis": candidate["match_basis"],
                        "start_s": start_s,
                        "end_s": end_s,
                        "layout": EVIDENCE_LAYOUTS[inserted % len(EVIDENCE_LAYOUTS)],
                        "sourceCrop": TEACHER_STAMP_SAFE_SOURCE_CROP,
                        "source_ref": f"{candidate['deck_id']} · slide {candidate['slide_number']}",
                    }
                )
                recent_asset_ids = (recent_asset_ids + [candidate["asset_id"]])[-2:]
                last_draw_start, inserted = start_s, inserted + 1
    return evidence


def _validate_first_five_evidence_obligations(
    world_beats: list[dict[str, Any]], evidence_beats: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for world in world_beats:
        start_s, end_s = float(world["start_s"]), float(world["end_s"])
        duration_s = end_s - start_s
        if start_s >= FIRST_FIVE_MINUTES_SECONDS or duration_s <= 6.0:
            continue
        matches = [
            evidence for evidence in evidence_beats
            if float(evidence["start_s"]) < end_s and float(evidence["end_s"]) > start_s
        ]
        exemption = P33_ANALOGY_EXEMPTIONS.get(world["asset_id"])
        status = "exempt" if exemption else "covered" if matches else "missing"
        record: dict[str, Any] = {
            "world_id": world["id"], "asset_id": world["asset_id"],
            "start_s": round(start_s, 3), "end_s": round(end_s, 3),
            "duration_s": round(duration_s, 3), "status": status,
            "evidence_asset_ids": [evidence["asset_id"] for evidence in matches],
        }
        if exemption:
            record["exemption"] = exemption
        records.append(record)
    return records


def _assert_p33_obligations(records: list[dict[str, Any]], evidence_beats: list[dict[str, Any]]) -> None:
    missing = [record["asset_id"] for record in records if record["status"] == "missing"]
    if missing:
        raise ValueError(f"P33 factual world beats require evidence: {', '.join(missing)}")
    ordered = sorted(evidence_beats, key=lambda evidence: float(evidence["start_s"]))
    for index, evidence in enumerate(ordered):
        active = [
            other for other in ordered
            if float(other["start_s"]) <= float(evidence["start_s"]) < float(other["end_s"])
        ]
        if len(active) > MAX_SIMULTANEOUS_EVIDENCE:
            raise ValueError("P33 exceeds the three-card evidence attention budget")
        prior_same_world = next(
            (other for other in reversed(ordered[:index]) if other.get("world_id") == evidence.get("world_id")),
            None,
        )
        if prior_same_world and float(evidence["start_s"]) - float(prior_same_world["start_s"]) + 1e-6 < EVIDENCE_REVEAL_SECONDS + EVIDENCE_REVEAL_GAP_SECONDS:
            raise ValueError("P33 evidence hand reveals overlap")


def _caption_layout(start_frame: int, end_frame: int, cue_id: str, evidence_beats: list[dict[str, Any]]) -> dict[str, float]:
    # Keep the arguments for a deterministic call contract while intentionally
    # avoiding evidence-relative caption motion.
    del start_frame, end_frame, cue_id, evidence_beats
    return dict(STANDARD_CAPTION_LOWER_THIRD)


def main() -> None:
    global DURATION_SECONDS, DURATION_FRAMES
    parser = ArgumentParser(description="Build a standards-compliant current-bubble review cut.")
    parser.add_argument("--duration-seconds", type=int, default=DURATION_SECONDS)
    args = parser.parse_args()
    if args.duration_seconds < 60 or args.duration_seconds > 981:
        raise ValueError("duration must be between 60 seconds and the canonical narration length")
    DURATION_SECONDS = args.duration_seconds
    DURATION_FRAMES = DURATION_SECONDS * FPS
    cut_slug = (
        "episode-one-full-p34-evidence-standards-v1"
        if DURATION_SECONDS >= 900
        else "ten-minute-p33-evidence-standards-v1"
        if DURATION_SECONDS == 600
        else "six-minute-p32-v1"
    )
    props_path = OUTPUT_DIR / f"current-bubble-{cut_slug}.props.json"
    manifest_path = OUTPUT_DIR / f"current-bubble-{cut_slug}.manifest.json"
    coverage = json.loads(COVERAGE_PATH.read_text(encoding="utf-8"))
    snapshot = compile_production_editor_snapshot(PROJECT, repository_root=ROOT)
    world_beats = _build_world_beats(coverage)
    evidence_beats = _build_evidence_beats(coverage, world_beats)
    obligation_records = _validate_first_five_evidence_obligations(world_beats, evidence_beats)
    _assert_p33_obligations(obligation_records, evidence_beats)

    asset_map: dict[str, str] = {
        "canonical-narration": _stage(
            "canonical-narration",
            PUBLIC_ROOT / "current-bubble-fresh-60s-v1/history_episode_1_master.mp3",
        ),
        "whiteboard-draw-hand-a-v1": _stage(
            "whiteboard-draw-hand-a-v1",
            PUBLIC_ROOT / "current-bubble-fresh-60s-v1/draw-hand-a-v1.png",
        ),
    }
    library = _world_library(coverage)
    for beat in world_beats:
        asset = library[beat["asset_id"]]
        asset_map.setdefault(beat["asset_id"], _stage(beat["asset_id"], _resolve_repo_path(asset["path"])))
    for beat in evidence_beats:
        asset_map.setdefault(beat["asset_id"], _stage(beat["asset_id"], _resolve_repo_path(beat["path"])))

    items: list[dict[str, Any]] = [
        _world_item(beat["id"], beat["asset_id"], beat["start_s"], beat["end_s"], index)
        for index, beat in enumerate(world_beats)
    ]
    items.extend(_build_motion_bit_items())
    for beat in evidence_beats:
        start, end = _frame(beat["start_s"]), _frame(beat["end_s"])
        items.append(
            {
                "id": beat["id"], "type": "evidence", "from": start, "durationInFrames": end - start,
                "assetId": beat["asset_id"], "cue_id": beat["cue_id"],
                "binding_state": beat["binding_state"], "match_basis": beat["match_basis"],
                "source_ref": beat["source_ref"], "evidence_eligible": True,
                "zIndex": 40, "layout": beat["layout"],
                "keyframes": {"opacity": [
                    {"frame": start, "value": 1, "easing": "linear"},
                    {"frame": max(start, end - 12), "value": 1, "easing": "ease_out"},
                    {"frame": end - 1, "value": 0, "easing": "ease_out"},
                ]},
            }
        )
    # Evidence is the stable reading surface; the world plate keeps its subtle
    # Ken-Burns motion but dims beneath each card to guide attention without
    # becoming a competing composition.
    for world, item in zip(world_beats, items):
        focus_keyframes = []
        for evidence in evidence_beats:
            if evidence["start_s"] < world["end_s"] and evidence["end_s"] > world["start_s"]:
                start, end = _frame(evidence["start_s"]), _frame(evidence["end_s"])
                focus_keyframes.extend([
                    {"frame": max(item["from"], start - 4), "value": 1.0, "easing": "ease_in_out"},
                    {"frame": start + 4, "value": 0.72, "easing": "ease_in_out"},
                    {"frame": max(start + 4, end - 6), "value": 0.72, "easing": "ease_in_out"},
                    {"frame": end - 1, "value": 1.0, "easing": "ease_in_out"},
                ])
        if focus_keyframes:
            item["keyframes"]["opacity"] = focus_keyframes
    words = list(snapshot["words"])
    source_fps = int(snapshot.get("fps", 30))
    for cue in snapshot["cues"]:
        start = _timeline_frame(int(cue["start_frame"]), source_fps)
        if start >= DURATION_FRAMES:
            break
        end = min(DURATION_FRAMES, _timeline_frame(int(cue["end_frame"]), source_fps))
        tokens = _word_tokens(cue, words, source_fps)
        if tokens and end > start:
            items.append(
                {
                    "id": f"six-minute-caption-{cue['cue_id']}", "type": "caption", "from": start,
                    "durationInFrames": end - start, "cue_id": cue["cue_id"], "text": cue["excerpt"],
                    "caption_preset": "word_by_word", "word_tokens": tokens, "fontSize": 38,
                    "color": "#fffaf0", "backgroundColor": "transparent", "zIndex": 72,
                    "layout": _caption_layout(start, end, cue["cue_id"], evidence_beats),
                }
            )
    items.append({
        "id": "canonical-narration-first-six-minutes", "type": "narration", "from": 0,
        "durationInFrames": DURATION_FRAMES, "assetId": "canonical-narration", "volume": 1, "zIndex": 100,
    })
    props = {
        "schema_version": "production_console_snapshot.v2", "snapshot_id": "current-bubble-six-minute-p32-v1",
        "project_id": "current-bubble-mechanism", "composition_id": "ProductionTimeline", "width": 1920,
        "height": 1080, "fps": FPS, "durationInFrames": DURATION_FRAMES, "backgroundColor": "#0b1015",
        "diagnosticMode": False, "assetMap": asset_map, "items": items,
    }
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    props_path.write_text(json.dumps(props, indent=2) + "\n", encoding="utf-8")
    P33_OBLIGATION_PATH.write_text(json.dumps({
        "schema_version": "p33_first_five_minute_evidence_obligation.v1",
        "duration_boundary_s": FIRST_FIVE_MINUTES_SECONDS,
        "rule": "factual world plates longer than six seconds require evidence unless explicitly analogy_exempt",
        "records": obligation_records,
    }, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "schema_version": "p32_review_demo.v1", "cut_id": f"current-bubble-{cut_slug}",
        "duration_seconds": DURATION_SECONDS, "duration_frames": DURATION_FRAMES, "fps": FPS,
        "world_beat_count": len(world_beats), "evidence_beat_count": len(evidence_beats),
        "caption_item_count": sum(item["type"] == "caption" for item in items),
        "coverage_artifact": COVERAGE_PATH.relative_to(ROOT).as_posix(), "coverage_hash": coverage["artifact_hash"],
        "source_snapshot_hash": snapshot["artifact_hash"], "props_path": props_path.relative_to(ROOT).as_posix(),
        "props_sha256": _sha256(props_path),
        "visual_grammar": {"world_plate_is_hero": True, "maximum_evidence_per_plate": 3,
            "maximum_simultaneous_evidence": MAX_SIMULTANEOUS_EVIDENCE, "maximum_horizontal_comparison_items": 2,
            "evidence_reveal": "consecutive_hand_draw", "visible_source_badge": False,
            "caption_mode": "canonical_word_by_word", "evidence_card_scale": EVIDENCE_CARD_SCALE,
            "evidence_hold_seconds": EVIDENCE_HOLD_SECONDS,
            "plate_motion": "remotion_bits.ken-burns-effect",
            "numeric_emphasis": "remotion_bits.basic-counter",
            "short_label_motion": "remotion_bits.basic-typewriter",
            "first_five_minute_evidence_obligation": P33_OBLIGATION_PATH.relative_to(ROOT).as_posix(),
            "teacher_stamp_preserved": True, "source_bound_crop_only": True, "review_only": True},
        "asset_sha256": {asset_id: _sha256(PUBLIC_ROOT / public_path) for asset_id, public_path in asset_map.items()},
    }
    if VIDEO_PATH.is_file():
        manifest.update({"render_path": VIDEO_PATH.relative_to(ROOT).as_posix(), "render_sha256": _sha256(VIDEO_PATH), "render_bytes": VIDEO_PATH.stat().st_size})
    if GATE_A_REVIEW_VIDEO_PATH.is_file():
        manifest.update({
            "gate_a_review_render_path": GATE_A_REVIEW_VIDEO_PATH.relative_to(ROOT).as_posix(),
            "gate_a_review_render_sha256": _sha256(GATE_A_REVIEW_VIDEO_PATH),
            "gate_a_review_render_bytes": GATE_A_REVIEW_VIDEO_PATH.stat().st_size,
            "gate_a_review_binding_state": "candidate_only; no crops or generated illustrations included",
        })
    if GATE_A_REVIEW_V3_VIDEO_PATH.is_file():
        manifest.update({
            "gate_a_review_v3_render_path": GATE_A_REVIEW_V3_VIDEO_PATH.relative_to(ROOT).as_posix(),
            "gate_a_review_v3_render_sha256": _sha256(GATE_A_REVIEW_V3_VIDEO_PATH),
            "gate_a_review_v3_render_bytes": GATE_A_REVIEW_V3_VIDEO_PATH.stat().st_size,
            "gate_a_review_v3_delta": "five-second evidence holds; city-box plate removed from every beat",
        })
    if P33_REVIEW_VIDEO_PATH.is_file():
        manifest.update({
            "p33_review_render_path": P33_REVIEW_VIDEO_PATH.relative_to(ROOT).as_posix(),
            "p33_review_render_sha256": _sha256(P33_REVIEW_VIDEO_PATH),
            "p33_review_render_bytes": P33_REVIEW_VIDEO_PATH.stat().st_size,
        })
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(props_path)
    print(manifest_path)
    print(f"items={len(items)} worlds={len(world_beats)} evidence={len(evidence_beats)} captions={manifest['caption_item_count']}")


if __name__ == "__main__":
    main()
