from __future__ import annotations

import json
from pathlib import Path

import pytest

from content.video_engine.src.services import generation_claim as claims
from content.video_engine.src.services.generation_claim import (
    ENV_CLAIMS_DIR,
    GenerationClaimError,
    claim_for_delivery,
    close_claim,
    list_claims,
    open_claim,
    render_work_order,
    verify_claim_matches_worktree,
)

SLOTS = [
    {"asset_id": "object-abacus-v1", "kind": "prop", "prompt": "an abacus, paper collage",
     "semantic": "wooden abacus"},
    {"asset_id": "object-hourglass-v1", "kind": "prop", "prompt": "an hourglass, paper collage",
     "semantic": "hourglass mid-pour"},
]


@pytest.fixture(autouse=True)
def _stub_git(monkeypatch):
    monkeypatch.setattr(claims, "_run_git", lambda args, cwd: "feature-branch")


def _env(tmp_path: Path) -> dict[str, str]:
    return {ENV_CLAIMS_DIR: str(tmp_path / "registry")}


def _root(tmp_path: Path) -> Path:
    root = tmp_path / "project"
    root.mkdir()
    return root


def test_opening_a_claim_registers_it_and_creates_a_review_class_delivery(tmp_path):
    env = _env(tmp_path)
    root = _root(tmp_path)

    claim = open_claim(root, claim_id="batch-one", style_family="fam-v3",
                       slots=SLOTS, env=env)

    assert (tmp_path / "registry" / "batch-one.json").exists()
    delivery = Path(claim["delivery_dir"])
    assert delivery.is_dir()
    assert delivery == root.resolve() / "review" / "claims" / "batch-one"
    assert claim["branch"] == "feature-branch"


def test_the_registry_lives_outside_the_project_root(tmp_path):
    env = _env(tmp_path)
    root = _root(tmp_path)

    open_claim(root, claim_id="batch-one", style_family="f", slots=SLOTS, env=env)

    registry_files = list((tmp_path / "registry").glob("*.json"))
    assert registry_files, "registry written where configured"
    assert not list(root.rglob("batch-one.json")), "never inside the repo"


def test_concurrent_claims_are_allowed_but_duplicate_ids_are_not(tmp_path):
    env = _env(tmp_path)
    root = _root(tmp_path)
    open_claim(root, claim_id="ep1-plates", style_family="f", slots=SLOTS, env=env)
    open_claim(root, claim_id="ep2-plates", style_family="f", slots=SLOTS, env=env)

    assert [c["claim_id"] for c in list_claims(env)] == ["ep1-plates", "ep2-plates"]

    with pytest.raises(GenerationClaimError) as excinfo:
        open_claim(root, claim_id="ep1-plates", style_family="f", slots=SLOTS, env=env)
    assert "already exists" in " ".join(excinfo.value.errors)


def test_invalid_slots_are_named_individually(tmp_path):
    env = _env(tmp_path)
    root = _root(tmp_path)
    bad = [
        {"asset_id": "ok-slot-v1", "kind": "prop", "prompt": "fine"},
        {"asset_id": "NO CAPS", "kind": "prop", "prompt": "x"},
        {"asset_id": "no-prompt-v1", "kind": "prop", "prompt": "  "},
    ]

    with pytest.raises(GenerationClaimError) as excinfo:
        open_claim(root, claim_id="bad-batch", style_family="f", slots=bad, env=env)

    joined = " ".join(excinfo.value.errors)
    assert "NO CAPS" in joined and "no-prompt-v1" in joined


def test_a_missing_reference_image_blocks_the_claim(tmp_path):
    env = _env(tmp_path)
    root = _root(tmp_path)

    with pytest.raises(GenerationClaimError) as excinfo:
        open_claim(root, claim_id="ref-batch", style_family="f", slots=SLOTS,
                   reference_images=[str(tmp_path / "gone.png")], env=env)

    assert "does not exist" in " ".join(excinfo.value.errors)


def test_the_work_order_is_self_contained(tmp_path):
    env = _env(tmp_path)
    root = _root(tmp_path)
    reference = tmp_path / "style-board.png"
    reference.write_bytes(b"png")
    claim = open_claim(root, claim_id="batch-one", style_family="fam-v3",
                       slots=SLOTS, reference_images=[str(reference)], env=env)

    order = render_work_order(claim)

    assert str(Path(claim["delivery_dir"])) in order, "absolute delivery path stated"
    assert "objects/object-abacus-v1.png" in order
    assert "source/object-hourglass-v1-source.png" in order, "sources always ship"
    assert "style-board.png" in order and "read-only" in order.lower()
    assert "approvals.json" in order and "last" in order
    assert "unresolved" in order
    assert "batch-one.manifest.json" in order
    assert str(claims.EXTRACTION_ATTEMPT_CAP) in order


def test_closing_a_claim_is_recorded_not_deleted(tmp_path):
    env = _env(tmp_path)
    root = _root(tmp_path)
    open_claim(root, claim_id="batch-one", style_family="f", slots=SLOTS, env=env)

    closed = close_claim("batch-one", env)

    assert closed["status"] == "closed"
    assert (tmp_path / "registry" / "batch-one.json").exists()


def test_a_delivery_resolves_back_to_its_claim(tmp_path):
    env = _env(tmp_path)
    root = _root(tmp_path)
    claim = open_claim(root, claim_id="batch-one", style_family="f", slots=SLOTS, env=env)

    found = claim_for_delivery(claim["delivery_dir"], env)
    assert found and found["claim_id"] == "batch-one"
    assert claim_for_delivery(tmp_path / "unrelated", env) is None


def test_promotion_refuses_a_claim_from_another_root_or_branch(tmp_path, monkeypatch):
    env = _env(tmp_path)
    root = _root(tmp_path)
    other = tmp_path / "other-project"
    other.mkdir()
    claim = open_claim(root, claim_id="batch-one", style_family="f", slots=SLOTS, env=env)

    assert verify_claim_matches_worktree(claim, root) == []
    assert any("belongs to" in e for e in verify_claim_matches_worktree(claim, other))

    monkeypatch.setattr(claims, "_run_git", lambda args, cwd: "some-other-branch")
    errors = verify_claim_matches_worktree(claim, root)
    assert any("some-other-branch" in e for e in errors)


def test_the_work_order_grants_strengthen_only_prompt_adaptation(tmp_path):
    """The agent may push prompts harder, never loosen the guardrails."""

    claim = open_claim(_root(tmp_path), claim_id="adapt-probe", style_family="f",
                       slots=SLOTS, env=_env(tmp_path))
    order = render_work_order(claim)

    assert "strengthen" in order
    assert "never weaken or drop the NEGATIVE block" in order
    assert "prompt_adaptations" in order


def test_the_work_order_normalises_cutout_sizes(tmp_path):
    """Exact-size resize after padding — the probe's tolerance gap, closed."""

    claim = open_claim(_root(tmp_path), claim_id="size-probe", style_family="f",
                       slots=SLOTS, env=_env(tmp_path))
    order = render_work_order(claim)

    assert "resize the padded canvas to exactly 1024x1024" in order
