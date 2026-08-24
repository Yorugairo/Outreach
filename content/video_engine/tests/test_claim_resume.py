from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest
from PIL import Image

from content.video_engine.src.services import generation_claim as gc
from content.video_engine.src.services.claim_resume import ClaimResumeError, resume_claim
from content.video_engine.src.services.paid_gate import ENV_CONFIG, ENV_JOBS_DIR, list_jobs

STYLE = "fam-v3"


def _png(path: Path, *, rgba: bool = True, size=(1024, 1536)) -> str:
    im = Image.new("RGBA" if rgba else "RGB", size, (0, 0, 0, 0) if rgba else (240, 230, 200))
    if rgba:
        for y in range(size[1] // 4, 3 * size[1] // 4):
            for x in range(size[0] // 4, 3 * size[0] // 4):
                im.putpixel((x, y), (60, 50, 40, 254))
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path)
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.fixture()
def env(tmp_path, monkeypatch):
    monkeypatch.setattr(gc, "_run_git", lambda args, cwd: "test-branch")
    return {
        gc.ENV_CLAIMS_DIR: str(tmp_path / "registry"),
        ENV_JOBS_DIR: str(tmp_path / "paid-jobs"),
        ENV_CONFIG: str(tmp_path / "missing-config.json"),
    }


def _project(tmp_path: Path) -> Path:
    root = tmp_path / "project"
    world_sha = _png(root / "canonical" / "world.png", rgba=False, size=(1536, 1024))
    catalog = {
        "schema_version": "finance_asset_catalog.v1",
        "style_families": {"fam": [STYLE]},
        "assets": [{
            "asset_id": "world-desk-v1", "path": "canonical/world.png", "sha256": world_sha,
            "kind": "world_board", "style_version": STYLE, "semantic_tags": ["desk"],
            "visual_worlds": ["story"], "identity_lenses": [], "resolution_tier": 2,
            "render_eligible": True, "review_state": "approved_reusable",
            "placement": {"figure_zone": [0.45, 1.0], "baseline_y": 0.98,
                          "figure_height": 0.5, "max_figures": 2},
        }],
    }
    (root / "asset-catalog.v1.json").write_text(json.dumps(catalog), encoding="utf-8")
    return root


def _claim_with_delivery(tmp_path: Path, env: dict, *, paid_followups=None) -> dict:
    root = _project(tmp_path)
    claim = gc.open_claim(
        root, claim_id="batch-one", style_family=STYLE,
        slots=[{"asset_id": "object-a-v1", "kind": "prop", "prompt": "p"}], env=env,
    )
    if paid_followups:
        claim["paid_followups"] = paid_followups
        (Path(gc.claims_dir(env)) / "batch-one.json").write_text(
            json.dumps(claim), encoding="utf-8")
    delivery = Path(claim["delivery_dir"])
    sha = _png(delivery / "objects" / "object-a-v1.png", size=(1024, 1024))
    manifest = {"style_family": STYLE, "assets": [
        {"asset_id": "object-a-v1", "path": "objects/object-a-v1.png", "sha256": sha,
         "kind": "prop"}]}
    (delivery / "batch-one.manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    (delivery / "approvals.json").write_text(json.dumps({"approved": ["object-a-v1"]}),
                                             encoding="utf-8")
    return claim


def test_resume_scans_composes_and_writes_the_pack_summary(tmp_path, env):
    _claim_with_delivery(tmp_path, env)

    summary = resume_claim("batch-one", env=env)

    assert summary["scan"]["counts"]["fail"] == 0
    summary_path = Path(summary["summary_path"])
    assert summary_path.exists()
    assert "runtime" in summary_path.parts, "the pack summary is a disposable artifact"
    # A clean compositable asset got a placement composite under runtime/.
    assert summary["composites"], "expected at least one composite preview"
    composite = summary["composites"][0]
    assert "runtime" in Path(composite["path"]).parts


def test_the_editor_lane_skips_by_name_unless_the_claim_opts_in(tmp_path, env):
    """P16 installed the lane; a claim without editor_composition still skips."""

    _claim_with_delivery(tmp_path, env)

    summary = resume_claim("batch-one", env=env)

    assert summary["editor"]["status"] == "skipped"
    assert "editor_composition" in summary["editor"]["reason"]


def test_a_missing_editor_module_would_also_be_a_recorded_skip(tmp_path, env, monkeypatch):
    """The import-failure branch stays covered even with the lane installed."""

    _claim_with_delivery(tmp_path, env)

    def absent(claim, project_root):
        return {"status": "skipped", "reason": "editor render lane not installed"}

    summary = resume_claim("batch-one", env=env, editor_hook=absent)

    assert summary["editor"]["status"] == "skipped"


def test_declared_paid_followups_are_registered_never_released(tmp_path, env):
    _claim_with_delivery(tmp_path, env, paid_followups=[
        {"lane": "audio", "description": "narration TTS", "estimated_cost_usd": 3.0},
    ])

    summary = resume_claim("batch-one", env=env)

    assert summary["paid_jobs_registered"] == ["batch-one-audio-1"]
    jobs = list_jobs(env)
    assert jobs[0]["status"] == "pending", "resume registers; only the gate releases"


def test_a_missing_claim_is_a_named_error(env):
    with pytest.raises(ClaimResumeError) as excinfo:
        resume_claim("no-such-claim", env=env)

    assert "no claim" in " ".join(excinfo.value.errors)
