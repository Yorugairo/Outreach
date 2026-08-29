"""Build the isolated P25 native 2D stick proof.

The proof intentionally uses no raster assets or provider calls. It reuses the
immutable P23 finance narration window while changing only the visual language:
white paper, deterministic SVG primitives, and a face-readable recurring
character.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any, Mapping


REPO_ROOT = Path(__file__).resolve().parents[3]
PILOT = REPO_ROOT / "content/video_engine/projects/systems-and-blowups/pilots/current-bubble-mechanism"
PROOF_ROOT = PILOT / "finance-2d-stick-proof-v1"
EDITOR = REPO_ROOT / "content/video_engine/editor"
CANONICAL_AUDIO = PILOT / "audio/canonical/history_episode_1_master.mp3"
CANONICAL_WORDS = PILOT / "audio/canonical/history_episode_1_master.words.json"
CLAIM_LEDGER = PILOT / "claim-ledger.v1.json"

PROOF_ID = "finance-2d-stick-proof-v1"
SOURCE_WORD_START = 1025
SOURCE_WORD_END = 1188
SOURCE_START_S = 410.260
SOURCE_END_S = 470.992
DURATION_S = 60.732
DELIVERY_FPS = 24
REVIEW_PROFILE = {"width": 1280, "height": 720, "fps": 24, "label": "review-720p-12-on-24"}
AUTHORING_PROFILE = {"width": 1920, "height": 1080, "fps": 24}
EXPECTED_HASHES = {
    "canonical_audio": "ecacf46c49aee85b912404bfa0e47c37acbae0397b637e2a966c51a625077ce1",
    "canonical_words": "3773bdd611c96d5e431ed56749d9991825215bb3756043086f14fbbdbe0d1da3",
    "claim_ledger": "0f5c49a3ab764ba5ad6ed9d4b14b2fc24fa6c921b9d83342975a7cfe0080edcc",
}

STATE_SPECS = (
    {"id": "basket-product-qualities", "start_word_index": 1025, "end_word_index": 1058, "start_s": 410.260, "end_s": 422.590},
    {"id": "two-jobs", "start_word_index": 1059, "end_word_index": 1075, "start_s": 422.834, "end_s": 428.209},
    {"id": "concentration", "start_word_index": 1076, "end_word_index": 1121, "start_s": 428.534, "end_s": 444.335},
    {"id": "shared-exposure", "start_word_index": 1122, "end_word_index": 1155, "start_s": 444.614, "end_s": 459.614},
    {"id": "long-tail", "start_word_index": 1156, "end_word_index": 1170, "start_s": 460.218, "end_s": 464.223},
    {"id": "admission-versus-weighting", "start_word_index": 1171, "end_word_index": 1188, "start_s": 464.548, "end_s": 470.992},
)

ALLOWED_PRIMITIVES = (
    "stick_person",
    "face",
    "index_basket",
    "holding_dot",
    "weather_cloud",
    "company_token",
    "money_stack",
    "eligibility_gate",
    "weight_scale",
    "label",
    "arrow",
    "scene_cut",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object: {path}")
    return payload


def require_repo_file(path: Path, label: str) -> None:
    if not path.is_file():
        raise FileNotFoundError(f"missing {label}: {path}")


def verify_immutable_inputs() -> dict[str, str]:
    paths = {"canonical_audio": CANONICAL_AUDIO, "canonical_words": CANONICAL_WORDS, "claim_ledger": CLAIM_LEDGER}
    actual: dict[str, str] = {}
    for label, path in paths.items():
        require_repo_file(path, label)
        actual[label] = sha256(path)
        if actual[label] != EXPECTED_HASHES[label]:
            raise ValueError(f"{label} SHA-256 drift: expected {EXPECTED_HASHES[label]}, got {actual[label]}")
    return actual


def _words() -> list[dict[str, Any]]:
    words = read_json(CANONICAL_WORDS).get("words")
    if not isinstance(words, list):
        raise ValueError("canonical word timing must contain a words list")
    return words


def _near(actual: float, expected: float, label: str, tolerance: float = 0.001) -> None:
    if abs(actual - expected) > tolerance:
        raise ValueError(f"{label} drift: expected {expected:.3f}, got {actual:.3f}")


def validate_source_window(words: list[dict[str, Any]]) -> None:
    if SOURCE_WORD_START < 0 or SOURCE_WORD_END >= len(words) or SOURCE_WORD_START > SOURCE_WORD_END:
        raise ValueError("P25 source word window is outside canonical timing")
    _near(float(words[SOURCE_WORD_START]["start_s"]), SOURCE_START_S, "source start")
    _near(float(words[SOURCE_WORD_END]["end_s"]), SOURCE_END_S, "source end")
    _near(SOURCE_END_S - SOURCE_START_S, DURATION_S, "source duration", tolerance=0.0001)
    previous_end = None
    for index, spec in enumerate(STATE_SPECS):
        start_index = int(spec["start_word_index"])
        end_index = int(spec["end_word_index"])
        if end_index < start_index:
            raise ValueError(f"state {spec['id']} has a reversed word range")
        if index == 0 and start_index != SOURCE_WORD_START:
            raise ValueError("first P25 state does not start at source_word_start")
        if index and start_index != int(STATE_SPECS[index - 1]["end_word_index"]) + 1:
            raise ValueError(f"state {spec['id']} word range is not contiguous")
        _near(float(words[start_index]["start_s"]), float(spec["start_s"]), f"{spec['id']} start")
        _near(float(words[end_index]["end_s"]), float(spec["end_s"]), f"{spec['id']} end")
        previous_end = end_index
    if previous_end != SOURCE_WORD_END:
        raise ValueError("last P25 state does not end at source_word_end")


def build_states() -> list[dict[str, Any]]:
    return [
        {
            **spec,
            "relative_start_s": round(float(spec["start_s"]) - SOURCE_START_S, 6),
            "relative_end_s": round(float(spec["end_s"]) - SOURCE_START_S, 6),
        }
        for spec in STATE_SPECS
    ]


def concentration_claim() -> dict[str, Any]:
    claims = read_json(CLAIM_LEDGER).get("claims")
    if not isinstance(claims, list):
        raise ValueError("claim ledger must contain a claims list")
    claim = next((item for item in claims if item.get("claim_id") == "sp500-top-ten-concentration"), None)
    if not isinstance(claim, dict):
        raise ValueError("claim ledger is missing sp500-top-ten-concentration")
    expected_text = "The ten largest S&P 500 companies represented almost 40% of the index by mid-2025, a concentration level not seen since the mid-1960s."
    if claim.get("text") != expected_text or claim.get("as_of") != "2025-06-30":
        raise ValueError("concentration claim wording or as_of does not match the source contract")
    locators = claim.get("source_locators")
    if not isinstance(locators, list) or not locators or not isinstance(locators[0], dict):
        raise ValueError("concentration claim is missing its source locator")
    locator = locators[0]
    if not locator.get("location") or not locator.get("source_id"):
        raise ValueError("concentration source locator is incomplete")
    return {
        "claim_id": claim["claim_id"],
        "claim_text": claim["text"],
        "display_text": "≈40% of index weight",
        "as_of": claim["as_of"],
        "source_locator": claim["claim_id"],
        "source_location": locator["location"],
        "qualifier": claim.get("qualifier") or "Concentration alone does not prove overvaluation or predict a market decline.",
    }


def validate_local_path(value: str, label: str) -> None:
    normalized = value.replace("\\", "/")
    if normalized.startswith("/") or normalized.startswith("\\") or (len(normalized) > 1 and normalized[1] == ":") or "://" in normalized or normalized.startswith("data:") or any(part in {"", ".", ".."} for part in normalized.split("/")):
        raise ValueError(f"{label} must be a safe project-relative path")


def build_props(claim: dict[str, Any], states: list[dict[str, Any]]) -> dict[str, Any]:
    props = {
        "schema_version": "finance_2d_stick_proof.v1",
        "proof_id": PROOF_ID,
        "duration_s": DURATION_S,
        "source_start_s": SOURCE_START_S,
        "source_end_s": SOURCE_END_S,
        "source_word_start": SOURCE_WORD_START,
        "source_word_end": SOURCE_WORD_END,
        "delivery_fps": DELIVERY_FPS,
        "authoring_profile": AUTHORING_PROFILE,
        "render_profile": REVIEW_PROFILE,
        "canonical_audio": {"path": "audio/canonical.mp3", "start_s": SOURCE_START_S, "volume": 1.0},
        "states": states,
        "concentration_source": {key: claim[key] for key in ("claim_id", "claim_text", "display_text", "as_of", "source_locator", "source_location", "qualifier")},
    }
    validate_local_path(props["canonical_audio"]["path"], "canonical_audio.path")
    return props


def primitive_manifest() -> dict[str, Any]:
    return {
        "schema_version": "finance_2d_stick_primitive_manifest.v1",
        "proof_id": PROOF_ID,
        "composition": "Finance2DStickProof",
        "canvas": {"width": 1920, "height": 1080, "background": "white paper"},
        "primitives": list(ALLOWED_PRIMITIVES),
        "asset_paths": [],
        "generated_assets": [],
        "stock_assets": [],
        "provider_calls": 0,
        "notes": "All visible content is deterministic SVG/React. No raster or provider asset is used.",
    }


def source_binding(input_hashes: dict[str, str], claim: dict[str, Any], states: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": "finance_2d_stick_source_binding.v1",
        "proof_id": PROOF_ID,
        "inputs": {
            "canonical_audio": {"path": CANONICAL_AUDIO.relative_to(REPO_ROOT).as_posix(), "sha256": input_hashes["canonical_audio"]},
            "canonical_words": {"path": CANONICAL_WORDS.relative_to(REPO_ROOT).as_posix(), "sha256": input_hashes["canonical_words"]},
            "claim_ledger": {"path": CLAIM_LEDGER.relative_to(REPO_ROOT).as_posix(), "sha256": input_hashes["claim_ledger"]},
        },
        "source_window": {"word_start_index": SOURCE_WORD_START, "word_end_index": SOURCE_WORD_END, "start_s": SOURCE_START_S, "end_s": SOURCE_END_S, "duration_s": DURATION_S, "indexing": "zero_based_in_canonical_words_json"},
        "states": states,
        "numeric_claim": {"claim_id": claim["claim_id"], "claim_text": claim["claim_text"], "display_text": claim["display_text"], "as_of": claim["as_of"], "source_location": claim["source_location"], "qualifier": claim["qualifier"]},
        "visual_contract": {"character": "native_face_readable_stick_person", "world": "white_paper", "generated_assets": False},
        "status": "source_bound",
    }


def _run(command: list[str], *, cwd: Path | None = None) -> None:
    result = subprocess.run(command, cwd=cwd, check=False)
    if result.returncode:
        raise RuntimeError(f"command failed ({result.returncode}): {' '.join(command)}")


def _probe(path: Path) -> dict[str, Any]:
    result = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,r_frame_rate,avg_frame_rate,nb_frames", "-show_entries", "format=duration", "-of", "json", str(path)], check=True, capture_output=True, text=True)
    payload = json.loads(result.stdout)
    stream = payload["streams"][0]
    return {"width": int(stream["width"]), "height": int(stream["height"]), "r_frame_rate": str(stream["r_frame_rate"]), "avg_frame_rate": str(stream.get("avg_frame_rate") or stream["r_frame_rate"]), "nb_frames": int(stream.get("nb_frames") or 0), "duration_s": float(payload["format"]["duration"])}


def _rate(value: str) -> float:
    numerator, denominator = value.split("/", 1)
    return float(numerator) / float(denominator)


def stage_audio(proof_root: Path) -> Path:
    target = proof_root / "public/audio/canonical.mp3"
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(CANONICAL_AUDIO, target)
    if sha256(target) != EXPECTED_HASHES["canonical_audio"]:
        raise ValueError("staged canonical audio hash does not match immutable input")
    return target


def render_proxy(proof_root: Path, props_path: Path) -> tuple[Path, dict[str, Any]]:
    render_dir = proof_root / "render"
    render_dir.mkdir(parents=True, exist_ok=True)
    target = render_dir / "finance-2d-stick-proof.mp4"
    total_frames = round(DURATION_S * DELIVERY_FPS)
    npx = shutil.which("npx.cmd") or shutil.which("npx")
    if not npx:
        raise RuntimeError("npx is required for Remotion rendering")
    _run([npx, "remotion", "render", "src/index.tsx", "Finance2DStickProof", f"--props={props_path}", f"--public-dir={proof_root / 'public'}", f"--frames=0-{total_frames - 1}", "--scale=1", "--overwrite", str(target)], cwd=EDITOR)
    require_repo_file(target, "Finance 2D stick review render")
    # Remotion's AAC muxer can leave one encoder packet beyond the final video
    # frame. Trim the container to the authored 24 fps boundary without
    # re-encoding the deterministic render.
    trimmed = render_dir / "finance-2d-stick-proof.trimmed.mp4"
    frame_duration = round(DURATION_S * DELIVERY_FPS) / DELIVERY_FPS
    _run(["ffmpeg", "-y", "-i", str(target), "-t", f"{frame_duration:.3f}", "-c", "copy", str(trimmed)])
    require_repo_file(trimmed, "trimmed Finance 2D stick review render")
    trimmed.replace(target)
    probe = _probe(target)
    if (probe["width"], probe["height"]) != (REVIEW_PROFILE["width"], REVIEW_PROFILE["height"]):
        raise ValueError(f"review render dimensions drifted: {probe['width']}x{probe['height']}")
    if abs(_rate(probe["avg_frame_rate"]) - DELIVERY_FPS) > 0.001:
        raise ValueError("review render frame rate is not 24 fps")
    if abs(probe["duration_s"] - DURATION_S) > 1 / DELIVERY_FPS + 0.002:
        raise ValueError(f"review render duration is outside one frame: {probe['duration_s']}")
    return target, probe


def extract_boundary_frames(video: Path, proof_root: Path, states: list[dict[str, Any]]) -> list[dict[str, Any]]:
    boundary_dir = proof_root / "review/boundaries"
    if boundary_dir.exists():
        shutil.rmtree(boundary_dir)
    boundary_dir.mkdir(parents=True, exist_ok=True)
    frames: list[dict[str, Any]] = []
    review_offsets = (7.0, 3.8, 8.5, 8.5, 3.5, 4.5)
    for index, state in enumerate(states, start=1):
        relative = min(float(state["relative_end_s"]) - 0.25, float(state["relative_start_s"]) + review_offsets[index - 1])
        frame_index = round(relative * DELIVERY_FPS)
        destination = boundary_dir / f"{index:02d}-{state['id']}-f{frame_index:04d}.png"
        _run(["ffmpeg", "-y", "-i", str(video), "-vf", f"select=eq(n\\,{frame_index})", "-fps_mode", "vfr", "-frames:v", "1", str(destination)])
        require_repo_file(destination, f"boundary frame {state['id']}")
        frames.append({"state_id": state["id"], "relative_time_s": relative, "source_time_s": round(SOURCE_START_S + relative, 6), "frame_index": frame_index, "path": destination.relative_to(proof_root).as_posix(), "sha256": sha256(destination)})
    return frames


def write_watch_draft(proof_root: Path, render_path: Path, render_probe: dict[str, Any], boundary_frames: list[dict[str, Any]]) -> Path:
    review_dir = proof_root / "review"
    review_dir.mkdir(parents=True, exist_ok=True)
    frame_refs = [{"path": Path(item["path"]).relative_to("review").as_posix(), "sha256": item["sha256"], "timestamp_s": item["relative_time_s"]} for item in boundary_frames]
    draft = {
        "schema_version": "video_watch_review.v1",
        "review_id": f"{PROOF_ID}-draft",
        "project_id": "outreach-program",
        "lane_id": "systems-and-blowups-finance",
        "episode_id": PROOF_ID,
        "created_at": "2026-08-09T00:00:00Z",
        "reviewer": "operator-and-watch",
        "review_purpose": "Review the simple native 2D stick grammar against the reference production pattern.",
        "watch_detail": "focused",
        "source": {"kind": "local", "uri": os.path.relpath(render_path, review_dir).replace("\\", "/"), "sha256": sha256(render_path), "duration_s": render_probe["duration_s"]},
        "transcript": {"path": os.path.relpath(CANONICAL_WORDS, review_dir).replace("\\", "/"), "sha256": sha256(CANONICAL_WORDS), "source": "canonical_word_timing"},
        "summary": {"assessment": "Operator review is pending. This packet preserves the full native 2D proof and exact scene-boundary evidence.", "strengths": ["The character and all props are deterministic SVG primitives.", "The proof uses the same audio clock and source-bound state boundaries."], "priority_issues": ["Operator must review face readability, object clarity, and whether the style is passable enough to scale."], "overall_state": "revision_required"},
        "findings": [{"finding_id": "operator-review-pending", "start_s": 0.0, "end_s": DURATION_S, "transcript_excerpt": "Now open the other elevator: the S&P 500 index fund.", "evidence_frames": frame_refs, "kind": "other", "scope": "episode", "severity": "medium", "symptom": "The render has not received an explicit operator decision.", "root_cause": "P25 stops at the isolated proof review boundary.", "impact": "The easy 2D grammar must not be promoted until the user confirms it is passable.", "proposed_fix": "Review the full proxy and six boundary frames for face readability, object clarity, pacing, and source-bound number treatment.", "acceptance": "Operator records approved or changes_requested.", "confidence": "confirmed", "recurrence_key": "p25-operator-review-gate", "recurrence_count": 1, "learning_trigger": "When a native 2D proof reaches visual review.", "learning_action": "Promote only the approved subset of the easy 2D grammar.", "requires_human_decision": True, "promotion_state": "observation", "status": "open"}],
        "operator_decision": {"state": "draft", "approved_at": None, "notes": "Awaiting explicit visual review."},
        "artifact_hash": "0" * 64,
    }
    path = review_dir / "watch-review-draft.v1.json"
    write_json(path, draft)
    return path


def build_artifacts(*, proof_root: Path = PROOF_ROOT, render: bool = False) -> dict[str, Any]:
    input_hashes = verify_immutable_inputs()
    words = _words()
    validate_source_window(words)
    states = build_states()
    claim = concentration_claim()
    props = build_props(claim, states)
    primitive = primitive_manifest()
    binding = source_binding(input_hashes, claim, states)
    proof_root.mkdir(parents=True, exist_ok=True)
    stage_audio(proof_root)
    props_path = proof_root / "proof-props.v1.json"
    primitive_path = proof_root / "primitive-manifest.v1.json"
    binding_path = proof_root / "source-binding.v1.json"
    write_json(props_path, props)
    write_json(primitive_path, primitive)
    write_json(binding_path, binding)

    render_path: Path | None = None
    render_probe: dict[str, Any] | None = None
    boundary_frames: list[dict[str, Any]] = []
    if render:
        render_path, render_probe = render_proxy(proof_root, props_path)
        boundary_frames = extract_boundary_frames(render_path, proof_root, states)
        write_watch_draft(proof_root, render_path, render_probe, boundary_frames)

    manifest: dict[str, Any] = {"schema_version": "finance_2d_stick_render_manifest.v1", "proof_id": PROOF_ID, "renderer": "remotion:Finance2DStickProof", "source_window": {"start_s": SOURCE_START_S, "end_s": SOURCE_END_S, "duration_s": DURATION_S, "word_start_index": SOURCE_WORD_START, "word_end_index": SOURCE_WORD_END}, "input_hashes": input_hashes, "logical_profile": AUTHORING_PROFILE, "review_profile": REVIEW_PROFILE, "delivery_fps": DELIVERY_FPS, "props_path": props_path.relative_to(proof_root).as_posix(), "primitive_manifest_path": primitive_path.relative_to(proof_root).as_posix(), "source_binding_path": binding_path.relative_to(proof_root).as_posix(), "provider_calls": 0, "generated_assets": [], "status": "review_render_complete" if render_path else "inputs_staged"}
    if render_path and render_probe:
        manifest["render"] = {"path": render_path.relative_to(proof_root).as_posix(), "sha256": sha256(render_path), "ffprobe": render_probe, "duration_error_s": round(render_probe["duration_s"] - DURATION_S, 6)}
        manifest["boundary_frames"] = boundary_frames
        manifest["watch_draft_path"] = "review/watch-review-draft.v1.json"
    render_manifest_path = proof_root / "render/composition-render-manifest.v1.json"
    write_json(render_manifest_path, manifest)
    return {"proof_root": proof_root, "props_path": props_path, "primitive_manifest_path": primitive_path, "source_binding_path": binding_path, "render_manifest_path": render_manifest_path, "render_path": render_path, "boundary_frames": boundary_frames}


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the deterministic P25 Finance 2D stick proof.")
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--proof-root", type=Path)
    parser.add_argument("--render", action="store_true")
    args = parser.parse_args()
    global CANONICAL_AUDIO, CANONICAL_WORDS, CLAIM_LEDGER, EDITOR, PROOF_ROOT
    root = args.repo_root.resolve()
    CANONICAL_AUDIO = root / "content/video_engine/projects/systems-and-blowups/pilots/current-bubble-mechanism/audio/canonical/history_episode_1_master.mp3"
    CANONICAL_WORDS = root / "content/video_engine/projects/systems-and-blowups/pilots/current-bubble-mechanism/audio/canonical/history_episode_1_master.words.json"
    CLAIM_LEDGER = root / "content/video_engine/projects/systems-and-blowups/pilots/current-bubble-mechanism/claim-ledger.v1.json"
    EDITOR = root / "content/video_engine/editor"
    PROOF_ROOT = (args.proof_root or root / "content/video_engine/projects/systems-and-blowups/pilots/current-bubble-mechanism/finance-2d-stick-proof-v1").resolve()
    result = build_artifacts(proof_root=PROOF_ROOT, render=args.render)
    print(json.dumps({key: (str(value) if isinstance(value, Path) else value) for key, value in result.items()}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
