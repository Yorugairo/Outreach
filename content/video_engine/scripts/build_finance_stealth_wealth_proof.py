"""Build the isolated P24 Stealth Wealth presenter proof.

The builder stages only local, hash-bound inputs, snapshots the supplied Deep
Research report, emits the source/claim/design contracts, renders a 105-second
720p proxy, extracts cue evidence, and preserves an operator-draft watch packet.
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
PROOF_ROOT = PILOT / "finance-stealth-wealth-proof-v1"
EDITOR = REPO_ROOT / "content/video_engine/editor"
CANONICAL_AUDIO = PILOT / "audio/canonical/history_episode_1_master.mp3"
CANONICAL_WORDS = PILOT / "audio/canonical/history_episode_1_master.words.json"
REPORT_SOURCE = Path("C:/Users/Snipe/Downloads/Memory Deep Research.txt")
PROOF_ID = "finance-stealth-wealth-proof-v1"
DURATION_S = 105.0
DELIVERY_FPS = 24
AUTHORING_PROFILE = {"width": 1920, "height": 1080, "fps": 24}
REVIEW_PROFILE = {"width": 1280, "height": 720, "fps": 24, "label": "review-720p"}
REPORT_SHA256 = "f153216f319f96b52a1a420f58a2fe6809084a60273ca8cb5f321cc4774f8c96"
EXPECTED_AUDIO_SHA256 = "ecacf46c49aee85b912404bfa0e47c37acbae0397b637e2a966c51a625077ce1"

ASSET_SOURCES = (
    {
        "asset_id": "finance-host-presenter-plate-v1",
        "source": REPO_ROOT / "content/video_engine/projects/systems-and-blowups/assets/generated/host/finance-host-presenter-plate-v1.png",
        "path": "assets/finance-host-presenter-plate-v1.png",
        "kind": "presenter_full_body",
        "source_kind": "built_in_imagegen",
    },
    {
        "asset_id": "finance-host-presenter-direct-v1",
        "source": REPO_ROOT / "content/video_engine/projects/systems-and-blowups/assets/generated/stealth-wealth-v1/presenter-direct-v1.png",
        "path": "assets/generated/stealth-wealth-v1/presenter-direct-v1.png",
        "kind": "presenter_direct_to_camera",
        "source_kind": "built_in_imagegen_identity_preserve",
    },
    {
        "asset_id": "stealth-wealth-warm-study-v1",
        "source": REPO_ROOT / "content/video_engine/projects/systems-and-blowups/assets/generated/stealth-wealth-v1/warm-oak-study-v1.png",
        "path": "assets/generated/stealth-wealth-v1/warm-oak-study-v1.png",
        "kind": "world_warm_oak_study",
        "source_kind": "built_in_imagegen",
    },
    {
        "asset_id": "stealth-wealth-cool-wafer-v1",
        "source": REPO_ROOT / "content/video_engine/projects/systems-and-blowups/assets/generated/stealth-wealth-v1/cool-wafer-lab-v1.png",
        "path": "assets/generated/stealth-wealth-v1/cool-wafer-lab-v1.png",
        "kind": "world_cool_wafer_lab",
        "source_kind": "built_in_imagegen",
    },
)

BEATS = (
    {
        "id": "hook",
        "start_s": 0.0,
        "end_s": 8.0,
        "eyebrow": "HOOK",
        "spoken_job": "Establish the index promise",
        "narration_excerpt": "The market may be labeling the wrong bubble.",
        "source_refs": [],
    },
    {
        "id": "authority",
        "start_s": 8.0,
        "end_s": 16.0,
        "eyebrow": "AUTHORITY HOOK",
        "spoken_job": "Introduce the valuation contradiction",
        "narration_excerpt": "The valuation profile is the contradiction.",
        "source_refs": ["sp500-cape", "memory-forward-pe"],
    },
    {
        "id": "physical",
        "start_s": 16.0,
        "end_s": 45.0,
        "eyebrow": "PHYSICAL COUNTERCASE",
        "spoken_job": "Translate the contradiction through the wafer",
        "narration_excerpt": "The underlying shortage is not imaginary.",
        "source_refs": ["memory-triopoly", "hbm-capacity-penalty"],
    },
    {
        "id": "concentration",
        "start_s": 45.0,
        "end_s": 75.0,
        "eyebrow": "CONCENTRATION GAP",
        "spoken_job": "Explain weight versus earnings and passive flows",
        "narration_excerpt": "The index is feeding its own weight.",
        "source_refs": ["top-ten-weight", "top-ten-earnings", "passive-flow"],
    },
    {
        "id": "triopoly",
        "start_s": 75.0,
        "end_s": 105.0,
        "eyebrow": "SILENT TRIOPOLY",
        "spoken_job": "Open the memory-sector mechanism",
        "narration_excerpt": "The capital cycle removed more than thirty rivals.",
        "source_refs": ["thirty-rivals", "memory-triopoly", "thesis-undervalued"],
    },
)

CLAIMS = (
    {
        "claim_id": "sp500-cape",
        "display_text": "41.18",
        "claim_text": "By mid-2026, the S&P 500 Shiller CAPE ratio climbed to 41.18; the report compares this with the 44.2 peak of the December 1999 dot-com bubble.",
        "source_locator": "Memory Deep Research.txt:L159-L160",
        "citation": "[cite:7,8]",
        "as_of": "mid-2026",
        "qualifier": "CAPE is a long-horizon index valuation measure, not a single-stock multiple.",
        "kind": "metric",
    },
    {
        "claim_id": "memory-forward-pe",
        "display_text": "4×–7×",
        "claim_text": "SK hynix and Micron have traded at forward P/E ratios ranging between 4× and 7×.",
        "source_locator": "Memory Deep Research.txt:L5; L171-L172",
        "citation": "[cite:1,5]",
        "as_of": "mid-2026",
        "qualifier": "The report presents this as a valuation comparison; memory earnings remain cyclical.",
        "kind": "metric",
    },
    {
        "claim_id": "top-ten-weight",
        "display_text": "41%",
        "claim_text": "In 2025, the top ten stocks represented roughly 41% of the S&P 500's total weight.",
        "source_locator": "Memory Deep Research.txt:L168",
        "citation": "[cite:49]",
        "as_of": "2025",
        "qualifier": "The report uses roughly 41% for the 2025 expected-weight comparison.",
        "kind": "metric",
    },
    {
        "claim_id": "top-ten-earnings",
        "display_text": "32%",
        "claim_text": "In 2025, the top ten stocks were expected to generate roughly 32% of aggregate S&P 500 earnings.",
        "source_locator": "Memory Deep Research.txt:L168",
        "citation": "[cite:49]",
        "as_of": "2025",
        "qualifier": "This is an expected aggregate earnings contribution, not a claim about every constituent.",
        "kind": "metric",
    },
    {
        "claim_id": "passive-flow",
        "display_text": "$40 / $100",
        "claim_text": "The report says passive-indexing inflows systematically direct forty dollars of every one hundred invested dollars into the top ten companies.",
        "source_locator": "Memory Deep Research.txt:L168",
        "citation": "[cite:49]",
        "as_of": "2025",
        "qualifier": "The report presents this as a feedback-loop mechanism supporting index weights.",
        "kind": "mechanism",
    },
    {
        "claim_id": "memory-triopoly",
        "display_text": "3 COMPANIES",
        "claim_text": "Samsung Electronics, SK hynix, and Micron Technology control the critical memory bottleneck described by the report.",
        "source_locator": "Memory Deep Research.txt:L3",
        "citation": "[cite:1,2,3]",
        "as_of": "mid-2026",
        "qualifier": "The report calls the structure a highly consolidated oligopoly; it also documents emerging challengers elsewhere in memory.",
        "kind": "mechanism",
    },
    {
        "claim_id": "thirty-rivals",
        "display_text": ">30 RIVALS",
        "claim_text": "The mid-1980s DRAM market had more than thirty active manufacturers; price wars, capital requirements, and technology transitions drove almost every player into bankruptcy or forced mergers.",
        "source_locator": "Memory Deep Research.txt:L26-L27",
        "citation": "[cite:26,27,28,29]",
        "as_of": "mid-1980s through 2014",
        "qualifier": "The report's historical consolidation thesis is the setup for the triopoly argument.",
        "kind": "comparison",
    },
    {
        "claim_id": "hbm-capacity-penalty",
        "display_text": "3× CAPACITY",
        "claim_text": "Producing a single bit of HBM consumes roughly three times the wafer capacity required to produce a single bit of standard DDR5.",
        "source_locator": "Memory Deep Research.txt:L88",
        "citation": "[cite:10,36,39]",
        "as_of": "mid-2026",
        "qualifier": "This is the report's physical capacity-penalty mechanism, not a claim about a stock's fair value.",
        "kind": "mechanism",
    },
    {
        "claim_id": "thesis-undervalued",
        "display_text": "UNDERPRICED CHOKE POINT",
        "claim_text": "The report concludes that the three dominant memory manufacturers remain structurally undervalued relative to their role as AI-infrastructure enablers.",
        "source_locator": "Memory Deep Research.txt:L204-L207",
        "citation": "[cite:1,3,5,10,36,39,40,56]",
        "as_of": "mid-2026",
        "qualifier": "This is the report's investment thesis and is presented as such.",
        "kind": "thesis",
    },
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


def require_file(path: Path, label: str) -> None:
    if not path.is_file():
        raise FileNotFoundError(f"missing {label}: {path}")


def _run(command: list[str], *, cwd: Path | None = None) -> None:
    result = subprocess.run(command, cwd=cwd, check=False)
    if result.returncode:
        raise RuntimeError(f"command failed ({result.returncode}): {' '.join(command)}")


def _probe(path: Path) -> dict[str, Any]:
    result = subprocess.run(
        [
            "ffprobe", "-v", "error", "-select_streams", "v:0",
            "-show_entries", "stream=width,height,r_frame_rate,avg_frame_rate,nb_frames",
            "-show_entries", "format=duration", "-of", "json", str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    stream = payload["streams"][0]
    return {
        "width": int(stream["width"]),
        "height": int(stream["height"]),
        "r_frame_rate": str(stream["r_frame_rate"]),
        "avg_frame_rate": str(stream.get("avg_frame_rate") or stream["r_frame_rate"]),
        "nb_frames": int(stream.get("nb_frames") or 0),
        "duration_s": float(payload["format"]["duration"]),
    }


def _rate(value: str) -> float:
    numerator, denominator = value.split("/", 1)
    return float(numerator) / float(denominator)


def verify_inputs() -> dict[str, str]:
    require_file(CANONICAL_AUDIO, "canonical audio")
    require_file(CANONICAL_WORDS, "canonical words")
    require_file(REPORT_SOURCE, "Deep Research report")
    audio_hash = sha256(CANONICAL_AUDIO)
    if audio_hash != EXPECTED_AUDIO_SHA256:
        raise ValueError(f"canonical audio SHA-256 drift: expected {EXPECTED_AUDIO_SHA256}, got {audio_hash}")
    report_hash = sha256(REPORT_SOURCE)
    if report_hash != REPORT_SHA256:
        raise ValueError(f"Deep Research report SHA-256 drift: expected {REPORT_SHA256}, got {report_hash}")
    return {
        "canonical_audio": audio_hash,
        "canonical_words": sha256(CANONICAL_WORDS),
        "deep_research_report": report_hash,
    }


def read_words() -> list[dict[str, Any]]:
    payload = json.loads(CANONICAL_WORDS.read_text(encoding="utf-8"))
    words = payload.get("words")
    if not isinstance(words, list):
        raise ValueError("canonical words must contain a words list")
    end_index = next((index for index, word in enumerate(words) if float(word["end_s"]) >= DURATION_S), None)
    if end_index is None:
        raise ValueError("canonical audio word timings end before P24 duration")
    selected = words[: end_index + 1]
    if float(selected[0]["start_s"]) != 0.0 or float(selected[-1]["end_s"]) < DURATION_S:
        raise ValueError("P24 source window does not cover the full 105 seconds")
    return selected


def stage_assets(proof_root: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for spec in ASSET_SOURCES:
        source = Path(spec["source"])
        require_file(source, spec["asset_id"])
        asset_hash = sha256(source)
        target = proof_root / "public" / spec["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        if sha256(target) != asset_hash:
            raise ValueError(f"staged asset hash mismatch: {spec['asset_id']}")
        record = {
            "asset_id": spec["asset_id"],
            "path": spec["path"],
            "source_path": source.relative_to(REPO_ROOT).as_posix(),
            "sha256": asset_hash,
            "kind": spec["kind"],
            "source_kind": spec["source_kind"],
            "contains_factual_text": False,
            "render_state": "draft",
        }
        records.append(record)
    return records


def update_global_catalogs(assets: list[dict[str, Any]]) -> None:
    """Register P24 assets without disturbing existing catalog entries."""
    generation_path = REPO_ROOT / "content/video_engine/projects/systems-and-blowups/assets/generated/generation-manifest.v1.json"
    catalog_path = REPO_ROOT / "content/video_engine/projects/systems-and-blowups/asset-catalog.v1.json"
    require_file(generation_path, "global generation manifest")
    require_file(catalog_path, "global asset catalog")
    generation = read_json(generation_path)
    catalog = read_json(catalog_path)
    generation_assets = generation.setdefault("assets", [])
    catalog_assets = catalog.setdefault("assets", [])
    existing_generation = {item.get("asset_id") for item in generation_assets if isinstance(item, dict)}
    existing_catalog = {item.get("asset_id") for item in catalog_assets if isinstance(item, dict)}
    requests = {
        "finance-host-presenter-direct-v1": "Identity-preserving generated direct-to-camera finance presenter on flat chroma-key background.",
        "stealth-wealth-warm-study-v1": "Generated cinematic warm oak study with charcoal shadows, amber practicals, emerald accents, and negative space for cards.",
        "stealth-wealth-cool-wafer-v1": "Generated cool slate laboratory macro plate with an emerald silicon wafer and uncluttered card space.",
    }
    for asset in assets:
        asset_id = asset["asset_id"]
        if asset_id == "finance-host-presenter-plate-v1":
            continue
        global_rel = asset["path"].split("assets/", 1)[-1]
        if asset_id not in existing_generation:
            if asset["kind"].startswith("world_"):
                generation_assets.append({
                    "asset_id": asset_id,
                    "request": requests[asset_id],
                    "flattened_path": global_rel,
                    "flattened_sha256": asset["sha256"],
                    "render_state": "draft",
                })
            else:
                generation_assets.append({
                    "asset_id": asset_id,
                    "request": requests[asset_id],
                    "source_path": global_rel.replace(".png", "-keyed-source.png"),
                    "source_sha256": sha256(REPO_ROOT / asset["source_path"]),
                    "cutout_path": global_rel,
                    "cutout_sha256": asset["sha256"],
                    "background_removal": "flat-chroma-key-plus-local-alpha",
                    "render_state": "draft",
                })
            existing_generation.add(asset_id)
        if asset_id not in existing_catalog:
            catalog_assets.append({
                "asset_id": asset_id,
                "path": asset["path"],
                "sha256": asset["sha256"],
                "kind": "world" if asset["kind"].startswith("world_") else "actor",
                "visual_worlds": ["story", "mechanism", "evidence"],
                "semantic_tags": ["stealth-wealth", "finance-presenter" if "presenter" in asset_id else "blurred-world", "matte-glass-stage"],
                "identity_lenses": ["finance-host"] if "presenter" in asset_id else [],
                "resolution_tier": 2,
                "generated": True,
                "contains_factual_text": False,
                "rights_state": "original_review_only",
                "review_state": "review_only",
                "render_eligible": False,
            })
            existing_catalog.add(asset_id)
    write_json(generation_path, generation)
    write_json(catalog_path, catalog)


def stage_source(proof_root: Path, input_hashes: dict[str, str], words: list[dict[str, Any]]) -> None:
    source_dir = proof_root / "source"
    source_dir.mkdir(parents=True, exist_ok=True)
    report_target = source_dir / "Memory Deep Research.txt"
    shutil.copy2(REPORT_SOURCE, report_target)
    if sha256(report_target) != input_hashes["deep_research_report"]:
        raise ValueError("staged report hash mismatch")
    upstream_words = source_dir / "upstream.words.json"
    shutil.copy2(CANONICAL_WORDS, upstream_words)
    canonical_words = {
        "schema_version": "finance_stealth_wealth_words.v1",
        "source_path": CANONICAL_WORDS.relative_to(REPO_ROOT).as_posix(),
        "source_sha256": input_hashes["canonical_words"],
        "duration_s": DURATION_S,
        "source_word_start": 0,
        "source_word_end": len(words) - 1,
        "words": words,
    }
    write_json(source_dir / "canonical.words.json", canonical_words)
    transcript = " ".join(str(word["w"]) for word in words)
    narration = f"""# P24 Narration Lock\n\n- Proof: `{PROOF_ID}`\n- Duration: `105.000s`\n- Audio: first 105 seconds of the existing canonical finance master\n- Audio source SHA-256: `{input_hashes['canonical_audio']}`\n- Word timing source SHA-256: `{input_hashes['canonical_words']}`\n- Editorial source SHA-256: `{input_hashes['deep_research_report']}`\n\n## Render transcript window\n\n{transcript}\n\n## Beat map\n\n| Time | Job | Visual anchor |\n| --- | --- | --- |\n| 0:00–0:08 | Index promise | warm study, direct-to-camera presenter, S&P line |\n| 0:08–0:16 | Valuation contradiction | CAPE 41.18 and memory 4×–7× cards |\n| 0:16–0:45 | Physical countercase | cool wafer world, presenter, scarcity card |\n| 0:45–1:15 | Concentration mechanism | 41% versus 32% chart and $40/$100 funnel |\n| 1:15–1:45 | Memory triopoly setup | S&P 500: THE 1999 ILLUSION and three chips |\n\nThe report-backed metrics are permitted verbatim. The source packet retains\nline locators and report citation markers for every factual surface.\n"""
    (source_dir / "narration.locked.md").write_text(narration, encoding="utf-8")
    write_json(source_dir / "claim-ledger.v1.json", {
        "schema_version": "finance_claim_ledger.v1",
        "proof_id": PROOF_ID,
        "source_of_record": {
            "path": "Memory Deep Research.txt",
            "sha256": input_hashes["deep_research_report"],
            "provided_by": "operator",
            "usage": "report-backed metrics may be rendered verbatim",
        },
        "claims": list(CLAIMS),
    })


def write_design_and_assets(proof_root: Path, input_hashes: dict[str, str], assets: list[dict[str, Any]]) -> None:
    beats_path = proof_root / "design-plan.v1.json"
    write_json(beats_path, {
        "schema_version": "finance_stealth_wealth_design_plan.v1",
        "proof_id": PROOF_ID,
        "aesthetic": {
            "style": "original stealth-wealth cinematic presenter",
            "palette": ["deep charcoal", "warm desaturated amber", "rich emerald"],
            "surface": "semi-transparent matte-glass cards",
            "pacing": "staccato, rhythmic, high-authority, analytical",
        },
        "beats": list(BEATS),
        "claims_are_compositor_owned": True,
        "world_motion": ["warm study", "cool wafer/lab", "warm study title return"],
        "camera": "deterministic parent transforms and opacity; no remote or random motion",
        "input_hashes": input_hashes,
    })
    selected = {
        "schema_version": "finance_selected_assets.v1",
        "proof_id": PROOF_ID,
        "assets": assets,
        "provider_calls": 0,
        "render_state": "draft",
    }
    write_json(proof_root / "assets/selected-assets.v1.json", selected)
    generation = {
        "schema_version": "finance_generation_manifest.v1",
        "proof_id": PROOF_ID,
        "assets": assets,
        "prompts": {
            "warm-oak-study-v1": "Generated cinematic warm oak study with left-side negative space, charcoal/amber/emerald palette, no text.",
            "cool-wafer-lab-v1": "Generated macro emerald silicon wafer in cool slate laboratory, no text.",
            "presenter-direct-v1": "Identity-preserving generated direct-to-camera finance presenter on flat green chroma-key background.",
        },
        "provider_calls": "built_in_imagegen",
        "promotion_state": "review_only",
        "render_eligible": False,
    }
    write_json(proof_root / "assets/generation-manifest.v1.json", generation)


def build_props(proof_root: Path, assets: list[dict[str, Any]], input_hashes: dict[str, str]) -> dict[str, Any]:
    by_id = {asset["asset_id"]: asset for asset in assets}
    def selected(asset_id: str) -> dict[str, Any]:
        item = by_id[asset_id]
        return {"asset_id": item["asset_id"], "path": item["path"], "sha256": item["sha256"], "render_state": "draft"}
    return {
        "schema_version": "finance_stealth_wealth_proof.v1",
        "proof_id": PROOF_ID,
        "duration_s": DURATION_S,
        "delivery_fps": DELIVERY_FPS,
        "authoring_profile": AUTHORING_PROFILE,
        "render_profile": REVIEW_PROFILE,
        "canonical_audio": {"path": "audio/canonical.mp3", "start_s": 0, "volume": 1.0},
        "presenter_assets": [selected("finance-host-presenter-plate-v1"), selected("finance-host-presenter-direct-v1")],
        "world_assets": [selected("stealth-wealth-warm-study-v1"), selected("stealth-wealth-cool-wafer-v1")],
        "beats": list(BEATS),
        "claims": list(CLAIMS),
        "report_source": {"path": "source/Memory Deep Research.txt", "sha256": input_hashes["deep_research_report"]},
    }


def stage_audio(proof_root: Path) -> None:
    target = proof_root / "public/audio/canonical.mp3"
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(CANONICAL_AUDIO, target)
    if sha256(target) != EXPECTED_AUDIO_SHA256:
        raise ValueError("staged audio hash mismatch")


def source_binding(proof_root: Path, input_hashes: dict[str, str], assets: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": "finance_stealth_wealth_source_binding.v1",
        "proof_id": PROOF_ID,
        "inputs": {
            "canonical_audio": {"path": CANONICAL_AUDIO.relative_to(REPO_ROOT).as_posix(), "sha256": input_hashes["canonical_audio"]},
            "canonical_words": {"path": CANONICAL_WORDS.relative_to(REPO_ROOT).as_posix(), "sha256": input_hashes["canonical_words"]},
            "deep_research_report": {"path": str(REPORT_SOURCE), "sha256": input_hashes["deep_research_report"]},
        },
        "source_window": {"start_s": 0.0, "end_s": DURATION_S, "duration_s": DURATION_S, "word_start_index": 0, "word_end_index": 276},
        "report_claims": list(CLAIMS),
        "selected_assets": [{"asset_id": item["asset_id"], "path": item["path"], "sha256": item["sha256"]} for item in assets],
        "status": "source_bound",
    }


def render_proxy(proof_root: Path, props_path: Path) -> tuple[Path, dict[str, Any]]:
    render_dir = proof_root / "render"
    render_dir.mkdir(parents=True, exist_ok=True)
    target = render_dir / "finance-stealth-wealth-presenter-proof.mp4"
    npx = shutil.which("npx.cmd") or shutil.which("npx")
    if not npx:
        raise RuntimeError("npx is required for Remotion rendering")
    _run([
        npx, "remotion", "render", "src/index.tsx", "FinanceStealthWealthProof",
        f"--props={props_path}", f"--public-dir={proof_root / 'public'}",
        f"--frames=0-{round(DURATION_S * DELIVERY_FPS) - 1}", "--scale=1", "--overwrite", str(target),
    ], cwd=EDITOR)
    require_file(target, "P24 review render")
    trimmed = render_dir / "finance-stealth-wealth-presenter-proof.trimmed.mp4"
    _run(["ffmpeg", "-y", "-i", str(target), "-t", f"{round(DURATION_S * DELIVERY_FPS) / DELIVERY_FPS:.3f}", "-c", "copy", str(trimmed)])
    require_file(trimmed, "trimmed P24 review render")
    trimmed.replace(target)
    probe = _probe(target)
    if (probe["width"], probe["height"]) != (REVIEW_PROFILE["width"], REVIEW_PROFILE["height"]):
        raise ValueError(f"P24 dimensions drifted: {probe['width']}x{probe['height']}")
    if abs(_rate(probe["avg_frame_rate"]) - DELIVERY_FPS) > 0.001:
        raise ValueError("P24 render frame rate is not 24 fps")
    if abs(probe["duration_s"] - DURATION_S) > 1 / DELIVERY_FPS + 0.01:
        raise ValueError(f"P24 duration is outside one frame: {probe['duration_s']}")
    return target, probe


def extract_boundaries(video: Path, proof_root: Path) -> list[dict[str, Any]]:
    boundary_dir = proof_root / "review/boundaries"
    if boundary_dir.exists():
        shutil.rmtree(boundary_dir)
    boundary_dir.mkdir(parents=True, exist_ok=True)
    frames: list[dict[str, Any]] = []
    for index, beat in enumerate(BEATS, start=1):
        offset_s = 3.0 if beat["id"] == "triopoly" else 0.5
        time_s = min(DURATION_S - 0.5, float(beat["start_s"]) + offset_s)
        frame_index = round(time_s * DELIVERY_FPS)
        target = boundary_dir / f"{index:02d}-{beat['id']}-f{frame_index:04d}.png"
        _run(["ffmpeg", "-y", "-i", str(video), "-vf", f"select=eq(n\\,{frame_index})", "-fps_mode", "vfr", "-frames:v", "1", str(target)])
        require_file(target, f"boundary frame {beat['id']}")
        frames.append({
            "beat_id": beat["id"],
            "timestamp_s": time_s,
            "frame_index": frame_index,
            "path": target.relative_to(proof_root).as_posix(),
            "sha256": sha256(target),
        })
    return frames


def write_watch_draft(proof_root: Path, render: Path, probe: dict[str, Any], frames: list[dict[str, Any]]) -> None:
    review_dir = proof_root / "review"
    refs = [
        {
            "path": Path(item["path"]).relative_to("review").as_posix(),
            "sha256": item["sha256"],
            "timestamp_s": item["timestamp_s"],
        }
        for item in frames
    ]
    draft = {
        "schema_version": "video_watch_review.v1",
        "review_id": "finance-stealth-wealth-proof-v1-draft",
        "project_id": "outreach-program",
        "lane_id": "systems-and-blowups-finance",
        "episode_id": PROOF_ID,
        "created_at": "2026-08-09T00:00:00Z",
        "reviewer": "operator-and-watch",
        "review_purpose": "Review the complete P24 105-second stealth-wealth presenter proof and five cue boundaries.",
        "watch_detail": "focused",
        "source": {"kind": "local", "uri": os.path.relpath(render, review_dir).replace("\\", "/"), "sha256": sha256(render), "duration_s": probe["duration_s"]},
        "transcript": {"path": os.path.relpath(proof_root / "source/narration.locked.md", review_dir).replace("\\", "/"), "sha256": sha256(proof_root / "source/narration.locked.md"), "source": "manual"},
        "summary": {
            "assessment": "Operator review is pending. The packet preserves the complete presenter-led proxy and exact cue evidence.",
            "strengths": ["Generated presenter and worlds are staged locally with hashes.", "Report-backed metrics are compositor-owned and citation-bound.", "Five semantic beats preserve the consultant's 105-second Act I structure."],
            "priority_issues": ["Review face readability, card hierarchy, timing, and whether the generated worlds feel premium at 720p."],
            "overall_state": "revision_required",
        },
        "findings": [{
            "finding_id": "operator-review-pending",
            "start_s": 0.0,
            "end_s": DURATION_S,
            "transcript_excerpt": "The market may be labeling the wrong bubble.",
            "evidence_frames": refs,
            "kind": "other",
            "scope": "episode",
            "severity": "medium",
            "symptom": "The render has not yet received operator visual acceptance.",
            "root_cause": "P24 stops at a review-only proof boundary.",
            "impact": "The grammar must not be promoted before the proxy is reviewed.",
            "proposed_fix": "Review the complete proxy and five boundaries for presenter quality, card readability, motivated movement, and source fidelity.",
            "acceptance": "Operator records approved or changes_requested.",
            "confidence": "confirmed",
            "recurrence_key": "p24-operator-review-gate",
            "recurrence_count": 1,
            "learning_trigger": "When a presenter proof reaches visual review.",
            "learning_action": "Require full proxy review before promotion.",
            "requires_human_decision": True,
            "promotion_state": "observation",
            "status": "open",
        }],
        "operator_decision": {"state": "draft", "approved_at": None, "notes": "Awaiting explicit visual review."},
        "artifact_hash": "0" * 64,
    }
    write_json(review_dir / "watch-review-draft.v1.json", draft)


def build_artifacts(*, proof_root: Path = PROOF_ROOT, render: bool = False) -> dict[str, Any]:
    input_hashes = verify_inputs()
    words = read_words()
    proof_root.mkdir(parents=True, exist_ok=True)
    assets = stage_assets(proof_root)
    update_global_catalogs(assets)
    stage_audio(proof_root)
    stage_source(proof_root, input_hashes, words)
    write_design_and_assets(proof_root, input_hashes, assets)
    props = build_props(proof_root, assets, input_hashes)
    props_path = proof_root / "proof-props.v1.json"
    write_json(props_path, props)
    binding_path = proof_root / "source-binding.v1.json"
    write_json(binding_path, source_binding(proof_root, input_hashes, assets))
    primitive_path = proof_root / "primitive-manifest.v1.json"
    write_json(primitive_path, {
        "schema_version": "finance_stealth_wealth_primitive_manifest.v1",
        "proof_id": PROOF_ID,
        "composition": "FinanceStealthWealthProof",
        "canvas": AUTHORING_PROFILE,
        "primitives": ["matte_glass_card", "presenter_camera", "index_line", "valuation_metric_card", "wafer_beat", "concentration_chart", "passive_flow_funnel", "memory_triad", "lower_third", "generated_presenter", "generated_world"],
        "asset_paths": [item["path"] for item in assets],
        "generated_assets": assets,
        "stock_assets": [],
        "provider_calls": 0,
        "factual_text_owner": "Remotion compositor",
    })
    render_path: Path | None = None
    render_probe: dict[str, Any] | None = None
    frames: list[dict[str, Any]] = []
    if render:
        render_path, render_probe = render_proxy(proof_root, props_path)
        frames = extract_boundaries(render_path, proof_root)
        write_watch_draft(proof_root, render_path, render_probe, frames)
    render_manifest: dict[str, Any] = {
        "schema_version": "finance_stealth_wealth_composition_render_manifest.v1",
        "proof_id": PROOF_ID,
        "renderer": "remotion:FinanceStealthWealthProof",
        "source_window": {"start_s": 0.0, "end_s": DURATION_S, "duration_s": DURATION_S, "word_start_index": 0, "word_end_index": len(words) - 1},
        "input_hashes": input_hashes,
        "logical_profile": AUTHORING_PROFILE,
        "review_profile": REVIEW_PROFILE,
        "delivery_fps": DELIVERY_FPS,
        "props_path": props_path.relative_to(proof_root).as_posix(),
        "primitive_manifest_path": primitive_path.relative_to(proof_root).as_posix(),
        "source_binding_path": binding_path.relative_to(proof_root).as_posix(),
        "provider_calls": 0,
        "generated_assets": assets,
        "status": "review_render_complete" if render_path else "inputs_staged",
    }
    if render_path and render_probe:
        render_manifest["render"] = {"path": render_path.relative_to(proof_root).as_posix(), "sha256": sha256(render_path), "ffprobe": render_probe, "duration_error_s": round(render_probe["duration_s"] - DURATION_S, 6)}
        render_manifest["boundary_frames"] = frames
        render_manifest["watch_draft_path"] = "review/watch-review-draft.v1.json"
    render_manifest_path = proof_root / "render/composition-render-manifest.v1.json"
    write_json(render_manifest_path, render_manifest)
    return {"proof_root": proof_root, "props_path": props_path, "source_binding_path": binding_path, "render_manifest_path": render_manifest_path, "render_path": render_path, "boundary_frames": frames}


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the deterministic P24 Finance Stealth Wealth presenter proof.")
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--proof-root", type=Path)
    parser.add_argument("--render", action="store_true")
    args = parser.parse_args()
    global CANONICAL_AUDIO, CANONICAL_WORDS, REPORT_SOURCE, EDITOR, PROOF_ROOT
    root = args.repo_root.resolve()
    CANONICAL_AUDIO = root / "content/video_engine/projects/systems-and-blowups/pilots/current-bubble-mechanism/audio/canonical/history_episode_1_master.mp3"
    CANONICAL_WORDS = root / "content/video_engine/projects/systems-and-blowups/pilots/current-bubble-mechanism/audio/canonical/history_episode_1_master.words.json"
    REPORT_SOURCE = Path("C:/Users/Snipe/Downloads/Memory Deep Research.txt")
    EDITOR = root / "content/video_engine/editor"
    PROOF_ROOT = (args.proof_root or root / "content/video_engine/projects/systems-and-blowups/pilots/current-bubble-mechanism/finance-stealth-wealth-proof-v1").resolve()
    result = build_artifacts(proof_root=PROOF_ROOT, render=args.render)
    print(json.dumps({key: (str(value) if isinstance(value, Path) else value) for key, value in result.items()}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
