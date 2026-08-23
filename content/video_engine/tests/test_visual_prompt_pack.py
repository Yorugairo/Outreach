from __future__ import annotations

import pytest

from content.video_engine.src.services.director import validate_director_proposal
from content.video_engine.src.services.provisional_coverage import (
    compile_provisional_coverage,
)
from content.video_engine.src.services.visual_prompt_pack import (
    MIN_VARIANTS_PER_SLOT,
    VisualPromptPackError,
    compile_and_write,
    compile_visual_prompt_pack,
    validate_candidate_batch,
)
from content.video_engine.tests.conftest import build_candidate_batch, build_proposal


@pytest.fixture()
def coverage(paste_brief):
    proposal = validate_director_proposal(build_proposal(paste_brief), brief=paste_brief)
    return compile_provisional_coverage(proposal, brief=paste_brief)


@pytest.fixture()
def pack(coverage):
    return compile_visual_prompt_pack(coverage, lane="stick_explainer")


def test_one_group_per_slot_each_requesting_three_variants(coverage, pack):
    assert len(pack["groups"]) == coverage["slot_count"]
    assert pack["variants_per_slot"] == 3
    assert all(group["variant_count"] == 3 for group in pack["groups"])


def test_every_prompt_forbids_lettering_and_repeats_the_identity_anchor(pack):
    for group in pack["groups"]:
        assert "no lettering" in group["prompt"]
        assert "no numerals" in group["prompt"]
        assert "no logos" in group["prompt"]
        assert pack["identity_anchor"] in group["prompt"]


def test_identity_anchor_carries_costume_not_face(pack):
    # Face drift cannot break continuity if identity never lived in the face.
    assert "t-shirt" in pack["identity_anchor"]


def test_prompts_reserve_space_for_renderer_typography(pack):
    assert all("negative space for typography" in g["prompt"] for g in pack["groups"])


def test_variants_below_two_are_rejected(coverage):
    with pytest.raises(VisualPromptPackError) as excinfo:
        compile_visual_prompt_pack(coverage, lane="stick_explainer", variants_per_slot=1)

    assert any(str(MIN_VARIANTS_PER_SLOT) in error for error in excinfo.value.errors)


def test_pack_carries_the_coverage_timing_basis(coverage, pack):
    assert pack["timing_basis"] == "estimated"
    assert pack["coverage_hash"] == coverage["artifact_hash"]


def test_matching_batch_validates(pack, tmp_path):
    batch = build_candidate_batch(pack, job_root=tmp_path)

    normalized = validate_candidate_batch(batch, pack=pack, job_root=tmp_path)

    assert len(normalized["items"]) == len(pack["groups"]) * pack["variants_per_slot"]


def test_unknown_slot_id_is_rejected(pack, tmp_path):
    batch = build_candidate_batch(pack, job_root=tmp_path)
    batch["items"][0]["slot_id"] = "not-a-slot"

    with pytest.raises(VisualPromptPackError) as excinfo:
        validate_candidate_batch(batch, pack=pack, job_root=tmp_path)

    assert any("not a coverage slot" in error for error in excinfo.value.errors)


def test_duplicate_variant_index_within_a_slot_is_rejected(pack, tmp_path):
    batch = build_candidate_batch(pack, job_root=tmp_path)
    batch["items"][1]["variant_index"] = batch["items"][0]["variant_index"]
    batch["items"][1]["slot_id"] = batch["items"][0]["slot_id"]

    with pytest.raises(VisualPromptPackError) as excinfo:
        validate_candidate_batch(batch, pack=pack, job_root=tmp_path)

    assert any("duplicates" in error for error in excinfo.value.errors)


def test_missing_slot_id_is_rejected(pack, tmp_path):
    batch = build_candidate_batch(pack, job_root=tmp_path)
    del batch["items"][0]["slot_id"]

    with pytest.raises(VisualPromptPackError) as excinfo:
        validate_candidate_batch(batch, pack=pack, job_root=tmp_path)

    assert any("slot_id is required" in error for error in excinfo.value.errors)


def test_short_batch_names_the_starved_slot(pack, tmp_path):
    batch = build_candidate_batch(pack, job_root=tmp_path, variants=2)

    with pytest.raises(VisualPromptPackError) as excinfo:
        validate_candidate_batch(batch, pack=pack, job_root=tmp_path)

    assert any("the pack requested 3" in error for error in excinfo.value.errors)


def test_generated_text_in_a_plate_is_never_render_eligible(pack, tmp_path):
    batch = build_candidate_batch(pack, job_root=tmp_path)
    batch["items"][0]["contains_factual_text"] = True

    with pytest.raises(VisualPromptPackError) as excinfo:
        validate_candidate_batch(batch, pack=pack, job_root=tmp_path)

    assert any("contains_factual_text" in error for error in excinfo.value.errors)
    assert any("composited by the" in error for error in excinfo.value.errors)


def test_compile_and_write_reports_the_generation_budget(coverage, tmp_path):
    summary = compile_and_write(coverage, lane="stick_explainer", output_dir=tmp_path / "job")

    assert summary["requested_generations"] == summary["group_count"] * 3
