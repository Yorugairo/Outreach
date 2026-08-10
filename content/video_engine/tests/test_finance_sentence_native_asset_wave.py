from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PILOT = ROOT / "content/video_engine/projects/systems-and-blowups/pilots/current-bubble-mechanism"
WAVE_ROOT = PILOT / "assets/quarantine/sentence-native-wave-01"
MANIFEST = WAVE_ROOT / "wave-01a-review-manifest.v1.json"
MANIFEST_01B = WAVE_ROOT / "wave-01b-review-manifest.v1.json"
MANIFEST_01C = WAVE_ROOT / "wave-01c-review-manifest.v1.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_hook_wave_is_hash_bound_sentence_native_and_review_only() -> None:
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    artifact_hash = payload.pop("artifact_hash")
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    assert artifact_hash == hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    assert payload["next_wave_authorized"] is True
    assert payload["operator_decision"] == "approved_for_composition"
    assert [item["beat_id"] for item in payload["accepted_candidates"]] == [
        "cbm-semantic-beat-01-002",
        "cbm-semantic-beat-01-003",
        "cbm-semantic-beat-01-004",
        "cbm-semantic-beat-01-006",
    ]
    assert len({item["semantic_job"] for item in payload["accepted_candidates"]}) == 4
    for item in payload["accepted_candidates"]:
        path = ROOT / item["path"]
        assert path.is_file()
        assert item["sha256"] == _sha256(path)
        assert item["review_state"] == "operator_approved_for_composition"
        assert item["render_eligible"] is True
        assert item["promotion_eligible"] is False
        assert all(value == "pass" for key, value in item["qa"].items() if key != "readable_generated_text")
        assert item["qa"]["readable_generated_text"] == "none_observed"

    rejected = payload["rejected_candidates"]
    assert len(rejected) == 1
    assert rejected[0]["review_state"] == "rejected_internal_qa"
    assert rejected[0]["rejection_reasons"]
    contact_sheet = ROOT / payload["contact_sheet_path"]
    assert payload["contact_sheet_sha256"] == _sha256(contact_sheet)


def test_hook_wave_01b_is_distinct_and_operator_approved() -> None:
    payload = json.loads(MANIFEST_01B.read_text(encoding="utf-8"))
    artifact_hash = payload.pop("artifact_hash")
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    assert artifact_hash == hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    assert payload["operator_decision"] == "approved_for_composition"
    assert payload["next_wave_authorized"] is True
    assert [item["beat_id"] for item in payload["accepted_candidates"]] == [
        "cbm-semantic-beat-01-008",
        "cbm-semantic-beat-01-009",
        "cbm-semantic-beat-01-010",
        "cbm-semantic-beat-01-011",
    ]
    assert len({item["semantic_job"] for item in payload["accepted_candidates"]}) == 4
    for item in payload["accepted_candidates"]:
        path = ROOT / item["path"]
        assert item["sha256"] == _sha256(path)
        assert item["review_state"] == "operator_approved_for_composition"
        assert item["render_eligible"] is True
        assert item["promotion_eligible"] is False
    contact_sheet = ROOT / payload["contact_sheet_path"]
    assert payload["contact_sheet_sha256"] == _sha256(contact_sheet)


def test_semantic_wave_01c_crosses_the_chapter_boundary_without_merging_beats() -> None:
    payload = json.loads(MANIFEST_01C.read_text(encoding="utf-8"))
    artifact_hash = payload.pop("artifact_hash")
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    assert artifact_hash == hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    assert payload["operator_decision"] == "approved_for_composition"
    assert payload["next_wave_authorized"] is True
    assert [item["beat_id"] for item in payload["accepted_candidates"]] == [
        "cbm-semantic-beat-01-012",
        "cbm-semantic-beat-01-013",
        "cbm-semantic-beat-02-002",
        "cbm-semantic-beat-02-003",
    ]
    assert len({item["semantic_job"] for item in payload["accepted_candidates"]}) == 4
    for item in payload["accepted_candidates"]:
        path = ROOT / item["path"]
        assert item["sha256"] == _sha256(path)
        assert item["review_state"] == "operator_approved_for_composition"
        assert item["render_eligible"] is True
        assert item["promotion_eligible"] is False
    contact_sheet = ROOT / payload["contact_sheet_path"]
    assert payload["contact_sheet_sha256"] == _sha256(contact_sheet)
