from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = REPO_ROOT / "content/video_engine/scripts/build_finance_2d_stick_proof.py"
COMPONENT_PATH = REPO_ROOT / "content/video_engine/editor/src/Finance2DStickProof.tsx"
ROOT_PATH = REPO_ROOT / "content/video_engine/editor/src/Root.tsx"


def _module():
    spec = importlib.util.spec_from_file_location("finance_2d_stick_builder", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_immutable_inputs_and_six_states_bind_to_canonical_window() -> None:
    module = _module()
    assert module.verify_immutable_inputs() == module.EXPECTED_HASHES
    words = module._words()
    module.validate_source_window(words)
    states = module.build_states()
    assert len(states) == 6
    assert [(state["start_word_index"], state["end_word_index"]) for state in states] == [
        (1025, 1058),
        (1059, 1075),
        (1076, 1121),
        (1122, 1155),
        (1156, 1170),
        (1171, 1188),
    ]
    assert states[-1]["relative_end_s"] == 60.732


def test_props_and_primitive_manifest_are_asset_free(tmp_path: Path) -> None:
    module = _module()
    claim = module.concentration_claim()
    result = module.build_artifacts(proof_root=tmp_path / "finance-2d-stick-proof-v1", render=False)
    proof_root = result["proof_root"]
    props = json.loads((proof_root / "proof-props.v1.json").read_text(encoding="utf-8"))
    primitive = json.loads((proof_root / "primitive-manifest.v1.json").read_text(encoding="utf-8"))
    binding = json.loads((proof_root / "source-binding.v1.json").read_text(encoding="utf-8"))
    assert props["duration_s"] == 60.732
    assert props["render_profile"] == module.REVIEW_PROFILE
    assert props["canonical_audio"]["path"] == "audio/canonical.mp3"
    assert props["concentration_source"]["display_text"] == claim["display_text"]
    assert primitive["asset_paths"] == []
    assert primitive["generated_assets"] == []
    assert primitive["provider_calls"] == 0
    assert binding["visual_contract"] == {"character": "native_face_readable_stick_person", "world": "white_paper", "generated_assets": False}


def test_component_is_native_2d_and_registered_separately() -> None:
    source = COMPONENT_PATH.read_text(encoding="utf-8")
    root = ROOT_PATH.read_text(encoding="utf-8")
    assert "Finance2DStickProof" in source
    assert "StickPerson" in source
    assert "Math.random" not in source
    assert "fetch(" not in source
    assert "https://" not in source
    assert "Finance2DStickProof" in root
    assert "id=\"FinanceSketchbookProof\"" in root
    assert "id=\"FinanceStealthWealthProof\"" in root


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


def test_watch_draft_remains_operator_draft(tmp_path: Path) -> None:
    module = _module()
    render = tmp_path / "render.mp4"
    render.write_bytes(b"review render")
    boundaries = []
    for index, state in enumerate(module.build_states(), start=1):
        frame = tmp_path / f"frame-{index}.png"
        frame.write_bytes(f"frame-{index}".encode())
        boundaries.append({"state_id": state["id"], "relative_time_s": state["relative_start_s"], "source_time_s": state["start_s"], "frame_index": round(state["relative_start_s"] * module.DELIVERY_FPS), "path": f"review/boundaries/{frame.name}", "sha256": module.sha256(frame)})
    review_dir = tmp_path / "review" / "boundaries"
    review_dir.mkdir(parents=True)
    for index in range(1, 7):
        (review_dir / f"frame-{index}.png").write_bytes(f"frame-{index}".encode())
    draft = module.write_watch_draft(tmp_path, render, {"duration_s": 60.75}, boundaries)
    payload = json.loads(draft.read_text(encoding="utf-8"))
    assert payload["operator_decision"]["state"] == "draft"
    assert payload["operator_decision"]["approved_at"] is None
    assert len(payload["findings"][0]["evidence_frames"]) == 6
