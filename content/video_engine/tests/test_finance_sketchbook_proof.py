from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = REPO_ROOT / "content/video_engine/scripts/build_finance_sketchbook_proof.py"
COMPONENT_PATH = REPO_ROOT / "content/video_engine/editor/src/FinanceSketchbookProof.tsx"
ROOT_PATH = REPO_ROOT / "content/video_engine/editor/src/Root.tsx"


def _module():
    spec = importlib.util.spec_from_file_location("finance_sketchbook_builder", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_immutable_inputs_and_six_states_bind_to_canonical_window() -> None:
    module = _module()
    hashes = module.verify_immutable_inputs()
    assert hashes == module.EXPECTED_HASHES

    words = module._words()
    module.validate_source_window(words)
    states = module.build_states()

    assert [(state["start_word_index"], state["end_word_index"]) for state in states] == [
        (1025, 1058),
        (1059, 1075),
        (1076, 1121),
        (1122, 1155),
        (1156, 1170),
        (1171, 1188),
    ]
    assert [state["relative_start_s"] for state in states] == [0.0, 12.574, 18.274, 34.354, 49.958, 54.288]
    assert states[-1]["relative_end_s"] == 60.732


def test_claim_card_is_source_bound_and_qualified() -> None:
    module = _module()
    claim = module.concentration_claim()
    assert claim["claim_id"] == "sp500-top-ten-concentration"
    assert claim["display_text"] == "≈40% of index weight"
    assert claim["as_of"] == "2025-06-30"
    assert "PDF page 4" in claim["source_location"]
    assert "does not prove overvaluation" in claim["qualifier"]


def test_builder_stages_contract_manifests_with_source_bound_presenter_plate(tmp_path: Path) -> None:
    module = _module()
    result = module.build_artifacts(proof_root=tmp_path / "finance-sketchbook-proof-v1", render=False)
    proof_root = result["proof_root"]

    assert (proof_root / "public/audio/canonical.mp3").is_file()
    assert (proof_root / "public/assets/finance-host-presenter-plate-v1.png").is_file()
    props = json.loads((proof_root / "proof-props.v1.json").read_text(encoding="utf-8"))
    primitive = json.loads((proof_root / "primitive-manifest.v1.json").read_text(encoding="utf-8"))
    binding = json.loads((proof_root / "source-binding.v1.json").read_text(encoding="utf-8"))
    render = json.loads((proof_root / "render/composition-render-manifest.v1.json").read_text(encoding="utf-8"))

    assert props["duration_s"] == 60.732
    assert props["delivery_fps"] == 24
    assert props["paper_motion_fps"] == 12
    assert props["canonical_audio"]["path"] == "audio/canonical.mp3"
    assert primitive["provider_calls"] == 0
    assert primitive["asset_paths"] == ["public/assets/finance-host-presenter-plate-v1.png"]
    assert primitive["generated_assets"][0]["asset_id"] == "finance-host-presenter-plate-v1"
    assert props["presenter_asset"]["render_state"] == "draft"
    assert binding["presenter_asset"]["asset_id"] == "finance-host-presenter-plate-v1"
    assert binding["source_window"]["indexing"] == "zero_based_in_canonical_words_json"
    assert binding["numeric_claim"]["claim_id"] == "sp500-top-ten-concentration"
    assert render["status"] == "inputs_staged"


def test_builder_rejects_non_contiguous_ranges(monkeypatch: pytest.MonkeyPatch) -> None:
    module = _module()
    broken = [dict(item) for item in module.STATE_SPECS]
    broken[1]["start_word_index"] = 1060
    monkeypatch.setattr(module, "STATE_SPECS", tuple(broken))
    with pytest.raises(ValueError, match="not contiguous"):
        module.validate_source_window(module._words())


def test_builder_rejects_remote_or_absolute_audio_paths() -> None:
    module = _module()
    for value in ("https://example.test/audio.mp3", "C:/audio.mp3", "/tmp/audio.mp3", "audio/../x.mp3"):
        with pytest.raises(ValueError, match="safe project-relative"):
            module.validate_local_path(value, "canonical_audio.path")


def test_component_is_primitive_only_and_registered_separately() -> None:
    source = COMPONENT_PATH.read_text(encoding="utf-8")
    root = ROOT_PATH.read_text(encoding="utf-8")
    assert "Math.random" not in source
    assert "fetch(" not in source
    assert "https://" not in source
    assert "FinanceSketchbookProof" in source
    assert "≈40% of index weight" in source
    assert "id=\"FinanceSketchbookProof\"" in root
    assert "id=\"EditorialMotion\"" in root


def test_watch_draft_remains_operator_draft(tmp_path: Path) -> None:
    module = _module()
    render = tmp_path / "render.mp4"
    render.write_bytes(b"review render")
    boundaries = []
    for index, state in enumerate(module.build_states(), start=1):
        frame = tmp_path / f"frame-{index}.png"
        frame.write_bytes(f"frame-{index}".encode())
        boundaries.append(
            {
                "state_id": state["id"],
                "relative_time_s": state["relative_start_s"],
                "source_time_s": state["start_s"],
                "frame_index": round(state["relative_start_s"] * module.DELIVERY_FPS),
                "path": frame.name,
                "sha256": module.sha256(frame),
            }
        )
    draft = module.write_watch_draft(tmp_path, render, {"duration_s": 60.75}, boundaries)
    payload = json.loads(draft.read_text(encoding="utf-8"))
    assert payload["operator_decision"]["state"] == "draft"
    assert payload["operator_decision"]["approved_at"] is None
    assert len(payload["findings"][0]["evidence_frames"]) == 6
