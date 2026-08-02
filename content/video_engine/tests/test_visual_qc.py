from __future__ import annotations

import json
from pathlib import Path

from content.video_engine.src.guards.visual_qc import run_visual_qc
from content.video_engine.src.services.style_board import COMPOSITION_FUNCTIONS, StyleBoardService


FUNCTIONS = [
    "result_preview",
    "wide_setup",
    "contact_closeup",
    "contact_closeup",
    "mechanic_transition",
    "wrong_right_compare",
    "force_diagram",
    "result_hold",
]


def _v2_storyboard() -> dict:
    scenes = []
    for index, function in enumerate(FUNCTIONS, start=1):
        params = {
            "function": function,
            "state_from": f"state-{index}",
            "action": f"action-{index}",
            "state_to": f"state-{index + 1}",
            "action_source": "deterministic_library",
            "cast": {"attacker": "white-gi", "defender": "black-gi"},
            "camera": {"framing": "close" if function == "contact_closeup" else function},
            "motion": {"path": "arc", "phases": ["anticipation", "action", "contact", "recovery"]},
            "reference_refs": [],
        }
        if function == "force_diagram":
            params = {
                "function": function,
                "action_source": "deterministic_library",
                "cast": {"attacker": "white-gi", "defender": "black-gi"},
                "camera": {"framing": "diagram"},
                "reference_refs": [],
            }
        scenes.append(
            {
                "scene_id": index,
                "visual_type": "bjj_action",
                "manim_class": "BJJActionScene",
                "visual_function": function,
                "parameters": params,
                "beats": [{"at_word": 0, "action": f"bjj_action:{params.get('action', 'diagram')}"}],
                "timing": {"target_s": 2.5},
                "layout_hints": {
                    "landscape": {"action_zone": "center"},
                    "vertical": {"action_zone": "middle"},
                },
            }
        )
    return {
        "global_settings": {
            "targets": ["landscape", "vertical"],
            "pacing": {"visual_change_max_s": 6, "shorts_visual_change_max_s": 3},
        },
        "scenes": scenes,
    }


def _v3_job(tmp_path: Path) -> tuple[dict, dict]:
    board = StyleBoardService().build({}, tmp_path / "style_board")
    manifest = {
        "schema_version": "render_manifest.v1",
        "segments": [
            {
                "id": f"segment-{index}",
                "composition": function,
                "visual_function": function,
                "treatment_id": f"treatment-{index}",
                "living_diagram": function in {
                    "mechanic_transition",
                    "force_diagram",
                },
            }
            for index, function in enumerate(COMPOSITION_FUNCTIONS, start=1)
        ]
        + [
            {"still_id": still["still_id"]}
            for still in board["stills"]
        ],
    }
    (tmp_path / "final_manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    return {"schema_version": "storyboard.v3"}, board


def _check(result: dict, check_id: str) -> dict:
    return next(item for item in result["checks"] if item["check_id"] == check_id)


def test_complete_visual_v2_storyboard_passes() -> None:
    result = run_visual_qc(_v2_storyboard())
    assert result["overall"] == "pass"
    assert all(check["status"] == "pass" for check in result["checks"])


def test_missing_coverage_and_repetition_fail() -> None:
    storyboard = _v2_storyboard()
    storyboard["scenes"] = storyboard["scenes"][:3]
    storyboard["scenes"].extend(
        [
            {**storyboard["scenes"][-1], "scene_id": 9},
            {**storyboard["scenes"][-1], "scene_id": 10},
        ]
    )
    result = run_visual_qc(storyboard)
    assert result["overall"] == "fail"
    assert _check(result, "visual_function_coverage")["status"] == "fail"
    assert _check(result, "visual_repetition")["status"] == "fail"


def test_cast_state_and_layout_fail_closed() -> None:
    storyboard = _v2_storyboard()
    storyboard["scenes"][0]["parameters"]["cast"] = {}
    storyboard["scenes"][1]["parameters"].pop("state_to")
    storyboard["scenes"][2]["layout_hints"]["vertical"] = {}
    result = run_visual_qc(storyboard)
    assert _check(result, "cast_continuity")["status"] == "fail"
    assert _check(result, "action_state_completeness")["status"] == "fail"
    assert _check(result, "layout_safe_zones")["status"] == "fail"


def test_unknown_reference_and_missing_editorial_scene_fail(tmp_path: Path) -> None:
    storyboard = _v2_storyboard()
    storyboard["scenes"][0]["parameters"]["reference_refs"] = ["missing-ref"]
    storyboard["scenes"][0]["parameters"]["action_source"] = "reviewed_reference"
    (tmp_path / "technique_manifest.json").write_text(
        json.dumps({"references": [{"reference_id": "known-ref"}]}), encoding="utf-8"
    )
    (tmp_path / "edit_manifest.json").write_text(
        json.dumps({"segments": [{"scene_id": scene["scene_id"]} for scene in storyboard["scenes"][:-1]]}),
        encoding="utf-8",
    )
    result = run_visual_qc(storyboard, tmp_path)
    assert _check(result, "reference_provenance")["status"] == "fail"
    assert _check(result, "final_plan_coverage")["status"] == "fail"


def test_legacy_storyboard_is_backwards_compatible() -> None:
    result = run_visual_qc({"scenes": [{"scene_id": 1, "visual_type": "title_card", "manim_class": "TitleConceptCard"}]})
    assert result["overall"] == "pass"
    assert result["checks"][0]["check_id"] == "visual_v2_applicability"


def test_v3_concept_qc_passes_complete_style_board(tmp_path: Path) -> None:
    storyboard, _board = _v3_job(tmp_path)
    result = run_visual_qc(storyboard, tmp_path)

    assert result["overall"] == "pass"
    assert all(_check(result, check_id)["status"] == "pass" for check_id in (
        "study_source_leakage",
        "art_bible_hash_integrity",
        "composition_treatment_coverage",
        "adjacent_signatures",
        "phash_distance",
        "v3_cast_continuity",
        "v3_safe_zones",
        "reviewed_overlay_anchors",
        "final_manifest_coverage",
    ))


def test_v3_qc_flags_source_leakage_and_phash_duplicate(tmp_path: Path) -> None:
    storyboard, board = _v3_job(tmp_path)
    board_path = tmp_path / "style_board" / "style_board.json"
    payload = json.loads(board_path.read_text(encoding="utf-8"))
    payload["study_path"] = "YouTube Reference Pack/study.json"
    payload["stills"][1]["phash"] = payload["stills"][0]["phash"]
    # The test intentionally corrupts the artifact hash; hash integrity should
    # report that independently of the two concept failures.
    board_path.write_text(json.dumps(payload), encoding="utf-8")

    result = run_visual_qc(storyboard, tmp_path)

    assert _check(result, "study_source_leakage")["status"] == "fail"
    assert _check(result, "phash_distance")["status"] == "fail"


def test_v3_qc_flags_unreviewed_overlay_and_missing_manifest(tmp_path: Path) -> None:
    storyboard, _board = _v3_job(tmp_path)
    payload = json.loads((tmp_path / "style_board" / "style_board.json").read_text(encoding="utf-8"))
    payload["stills"][2]["overlay_anchors"][0]["reviewed"] = False
    payload["stills"][2]["reviewed_overlay_anchors"][0]["reviewed"] = False
    (tmp_path / "style_board" / "style_board.json").write_text(json.dumps(payload), encoding="utf-8")
    (tmp_path / "final_manifest.json").unlink()

    result = run_visual_qc(storyboard, tmp_path)

    assert _check(result, "reviewed_overlay_anchors")["status"] == "fail"
    assert _check(result, "final_manifest_coverage")["status"] == "fail"


def test_v3_gate_a_defers_final_manifest_coverage(tmp_path: Path) -> None:
    storyboard, _board = _v3_job(tmp_path)
    (tmp_path / "final_manifest.json").unlink()

    result = run_visual_qc(
        storyboard,
        tmp_path,
        require_final_manifest=False,
    )

    check = _check(result, "final_manifest_coverage")
    assert check["status"] == "pass"
    assert "deferred until Gate B" in check["detail"]
