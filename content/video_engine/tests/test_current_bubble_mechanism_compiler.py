from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = REPO_ROOT / "content" / "video_engine" / "scripts" / "compile_current_bubble_mechanism_video.py"
PILOT_ROOT = (
    REPO_ROOT
    / "content"
    / "video_engine"
    / "projects"
    / "systems-and-blowups"
    / "pilots"
    / "current-bubble-mechanism"
)
SEMANTIC_MAP_PATH = PILOT_ROOT / "edit" / "semantic-v2" / "remotion-semantic-resolution-map.v3.json"
RESEARCH_SUPPLEMENT_PATH = PILOT_ROOT / "edit" / "semantic-v2" / "research-evidence-supplement.v1.json"
PROPS_PATH = PILOT_ROOT / "animatic" / "revisions" / "full-review-v1" / "remotion-props.json"
EDITOR_SOURCE_PATH = REPO_ROOT / "content" / "video_engine" / "editor" / "src" / "EditorialMotion.tsx"


def _module():
    spec = importlib.util.spec_from_file_location("current_bubble_compiler", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_legacy_rotation_is_retired_until_semantic_cues_are_resolved() -> None:
    module = _module()
    assert not hasattr(module, "_choose_visual")
    assert hasattr(module, "_resolve_visual")
    assert "sequence = sequences" not in SCRIPT_PATH.read_text(encoding="utf-8")


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_current_review_delivers_24fps_with_12fps_paper_motion() -> None:
    props = _json(PROPS_PATH)
    assert props["render_profile"]["fps"] == 24
    assert props["render_profile"]["label"] == "review-1080p-12-on-24"

    source = EDITOR_SOURCE_PATH.read_text(encoding="utf-8")
    assert "Math.round(fps / 12)" in source
    assert "const steppedFrame" in source


def test_semantic_map_restricts_elevator_and_splits_long_explainers() -> None:
    payload = _json(SEMANTIC_MAP_PATH)
    cues = payload["cues"]
    assert len(cues) == 290

    elevator_cues = {
        cue["cue_id"]
        for cue in cues
        if cue["asset_id"] == "wrong-bubble-elevators-v2"
    }
    assert elevator_cues == {
        "cbm-cue-001",
        "cbm-cue-025",
        "cbm-cue-026",
        "cbm-cue-284",
        "cbm-cue-285",
    }

    assets = {cue["cue_id"]: cue["asset_id"] for cue in cues}
    assert assets["cbm-cue-173"] == "evidence-wealth-target-path-v1"
    assert assets["cbm-cue-181"] == "evidence-return-comparison-v1"
    assert assets["cbm-cue-206"] == "two-sleeve-barbell-v1"
    assert assets["cbm-cue-212"] == "evidence-market-leaders-basket-v1"
    assert assets["cbm-cue-219"] == "evidence-market-leaders-backtest-v1"
    assert assets["cbm-cue-222"] == "evidence-market-leaders-drawdown-v1"
    assert assets["cbm-cue-236"] == "evidence-concentrated-selection-risk-v1"
    assert assets["cbm-cue-246"] == "evidence-equal-weight-countercase-v1"
    assert assets["cbm-cue-254"] == "memory-three-failure-points-v1"
    assert assets["cbm-cue-262"] == "evidence-bounded-conclusion-v1"


def test_index_section_uses_distinct_semantic_mechanisms_without_action_chips() -> None:
    payload = _json(SEMANTIC_MAP_PATH)
    assets = {cue["cue_id"]: cue["asset_id"] for cue in payload["cues"]}
    assert assets["cbm-cue-138"] == "evidence-index-inclusion-gate-v1"
    assert assets["cbm-cue-141"] == "evidence-float-weighting-v1"
    assert assets["cbm-cue-144"] == "evidence-automatic-business-mix-v1"
    assert assets["cbm-cue-147"] == "evidence-diworsification-plateau-v1"
    assert assets["cbm-cue-150"] == "index-roster-diworsification-v1"
    assert assets["cbm-cue-154"] == "evidence-portfolio-jobs-v1"
    assert assets["cbm-cue-158"] == "evidence-sp500-concentration-v1"
    assert assets["cbm-cue-161"] == "evidence-index-tail-absorption-v1"

    props = _json(PROPS_PATH)
    assert not any(str(key).startswith("overlay-headline-") for key in props["overlay_map"])


def test_research_supplement_binds_supplied_report_and_yfinance_packet() -> None:
    payload = _json(RESEARCH_SUPPLEMENT_PATH)
    source_kinds = {item["kind"] for item in payload["inputs"]}
    assert source_kinds == {
        "operator_verified_research",
        "yfinance_adjusted_close_packet",
    }
    claims = {item["id"]: item for item in payload["visual_claims"]}
    assert "2–3×" in claims["hbm-wafer-bit-output-tradeoff"]["display"]
    assert claims["hbm-wafer-bit-output-tradeoff"]["cue_ids"] == [
        "cbm-cue-057",
        "cbm-cue-058",
    ]
    assert claims["timely-trailing-return-comparison"]["display"] == (
        "MU +685.7% · KOSPI +93.9% · S&P 500 +22.4%"
    )
    assert "2026-08-07" in claims["timely-trailing-return-comparison"]["locator"]


def test_transition_and_caption_source_has_no_full_frame_paper_mask() -> None:
    source = EDITOR_SOURCE_PATH.read_text(encoding="utf-8")
    assert "TransitionInPaperSweep" in source
    assert "WebkitLineClamp: 2" in source
    assert "bottom: \"2.2%\"" in source
    assert "clipPath: transitionInClipPath" not in source
