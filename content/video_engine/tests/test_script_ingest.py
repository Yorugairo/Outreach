from __future__ import annotations

import json
from pathlib import Path

import pytest

from content.video_engine.src.services.script_ingest import (
    DEFAULT_WORDS_PER_MINUTE,
    ScriptIngestError,
    estimated_duration_s,
    ingest_script,
    paste_lane_stages,
    word_count,
)


def test_paste_lane_omits_the_research_gate_but_keeps_publish():
    stages = paste_lane_stages()

    assert "validating_research" not in stages
    assert "awaiting_research_approval" not in stages
    assert "awaiting_publish_approval" in stages
    assert stages[0] == "ingesting_source"


def test_ingest_writes_attestation_then_brief(paste_script, paste_attestation, tmp_path):
    summary = ingest_script(
        script_path=paste_script,
        attestation=paste_attestation,
        output_dir=tmp_path / "job",
        brief_id="energy-drains",
        title="The Hidden Energy Drains",
        lane="stick_explainer",
    )

    attestation = json.loads(Path(summary["attestation_path"]).read_text(encoding="utf-8"))
    brief = json.loads(Path(summary["brief_path"]).read_text(encoding="utf-8"))
    assert attestation["schema_version"] == "source_attestation.v1"
    assert brief["attestation_hash"] == attestation["artifact_hash"]
    assert brief["script"]["word_count"] == word_count(paste_script.read_text(encoding="utf-8"))


def test_estimate_uses_word_count_over_wpm_not_audio():
    # 140 words at 140 wpm is exactly one minute. Audio is never consulted here.
    assert estimated_duration_s(140, DEFAULT_WORDS_PER_MINUTE) == pytest.approx(60.0)


def test_attachment_references_are_carried_for_later_deck_ingest(
    paste_script, paste_attestation, tmp_path
):
    summary = ingest_script(
        script_path=paste_script,
        attestation=paste_attestation,
        output_dir=tmp_path / "job",
        brief_id="energy-drains",
        title="Title",
        lane="stick_explainer",
    )

    attestation = json.loads(Path(summary["attestation_path"]).read_text(encoding="utf-8"))
    assert attestation["references"][0]["kind"] == "slide_deck"


@pytest.mark.parametrize("missing", ["asserted_by", "source_ref", "claim_basis"])
def test_missing_provenance_writes_nothing(paste_script, paste_attestation, tmp_path, missing):
    del paste_attestation[missing]
    job_dir = tmp_path / "job"

    with pytest.raises(ScriptIngestError) as excinfo:
        ingest_script(
            script_path=paste_script,
            attestation=paste_attestation,
            output_dir=job_dir,
            brief_id="energy-drains",
            title="Title",
            lane="stick_explainer",
        )

    assert any(missing in error for error in excinfo.value.errors)
    assert not job_dir.exists(), "a run without provenance must leave no artifacts"


def test_script_hash_binds_the_attestation_to_this_exact_script(
    paste_script, paste_attestation, tmp_path
):
    first = ingest_script(
        script_path=paste_script,
        attestation=paste_attestation,
        output_dir=tmp_path / "a",
        brief_id="x",
        title="T",
        lane="stick_explainer",
    )
    paste_script.write_text("A different script entirely.", encoding="utf-8")
    second = ingest_script(
        script_path=paste_script,
        attestation=paste_attestation,
        output_dir=tmp_path / "b",
        brief_id="x",
        title="T",
        lane="stick_explainer",
    )

    assert first["attestation_hash"] != second["attestation_hash"]


def test_empty_script_is_rejected(tmp_path, paste_attestation):
    script = tmp_path / "empty.txt"
    script.write_text("   \n  ", encoding="utf-8")

    with pytest.raises(ScriptIngestError):
        ingest_script(
            script_path=script,
            attestation=paste_attestation,
            output_dir=tmp_path / "job",
            brief_id="x",
            title="T",
            lane="stick_explainer",
        )


def test_slot_hold_above_the_coverage_cap_is_rejected(
    paste_script, paste_attestation, tmp_path
):
    with pytest.raises(ScriptIngestError) as excinfo:
        ingest_script(
            script_path=paste_script,
            attestation=paste_attestation,
            output_dir=tmp_path / "job",
            brief_id="x",
            title="T",
            lane="stick_explainer",
            target_slot_hold_s=9.0,
        )

    assert any("target_slot_hold_s" in error for error in excinfo.value.errors)
