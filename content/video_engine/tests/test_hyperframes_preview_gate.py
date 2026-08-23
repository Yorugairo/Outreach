from __future__ import annotations

import json
from pathlib import Path

import pytest
from PIL import Image

from content.video_engine.src.services.asset_resolver import file_sha256
from content.video_engine.src.services.hyperframes_render import (
    PREVIEW_INTENT,
    QUARANTINE_DIR,
    HyperframesUnitError,
    resolve_assets,
)


def _repo(tmp_path: Path, *, review_status: str, asset_rel: str = "assets/plate.png") -> Path:
    asset = tmp_path / asset_rel
    asset.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (64, 64), (200, 190, 160)).save(asset)
    manifest = {
        "review": {"status": review_status},
        "assets": [{"id": "plate-1", "path": asset_rel, "sha256": file_sha256(asset)}],
    }
    (tmp_path / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    return tmp_path


def _unit(kind: str, **over) -> dict:
    unit = {
        "unit_kind": kind,
        "manifest_path": "manifest.json",
        "plates": [{"asset_id": "plate-1"}],
    }
    unit.update(over)
    return unit


def test_a_publishable_unit_still_fails_closed_on_review_status(tmp_path):
    """The existing gate, held: nothing about publishable kinds changed."""

    root = _repo(tmp_path, review_status="review_only")

    with pytest.raises(HyperframesUnitError) as excinfo:
        resolve_assets(_unit("vertical_short"), repo_root=root)

    assert any("not an approved status" in e for e in excinfo.value.errors)


def test_an_animatic_without_the_intent_also_fails_closed(tmp_path):
    """The carve-out is the intent, not the unit kind."""

    root = _repo(tmp_path, review_status="review_only")

    with pytest.raises(HyperframesUnitError) as excinfo:
        resolve_assets(_unit("animatic_preview"), repo_root=root)

    assert any("not an approved status" in e for e in excinfo.value.errors)


def test_a_quarantined_preview_may_reference_review_only_assets(tmp_path):
    root = _repo(tmp_path, review_status="review_only")

    resolved = resolve_assets(
        _unit("animatic_preview", preview_intent=PREVIEW_INTENT), repo_root=root,
    )

    assert "plate-1" in resolved


def test_the_intent_on_a_publishable_kind_is_rejected_by_name(tmp_path):
    root = _repo(tmp_path, review_status="rights_reviewed")

    with pytest.raises(HyperframesUnitError) as excinfo:
        resolve_assets(
            _unit("vertical_short", preview_intent=PREVIEW_INTENT), repo_root=root,
        )

    joined = " ".join(excinfo.value.errors)
    assert "vertical_short" in joined
    assert "failing closed" in joined


def test_the_preview_carve_out_does_not_relax_digest_binding(tmp_path):
    """A preview of the wrong bytes is worse than no preview."""

    root = _repo(tmp_path, review_status="review_only")
    manifest_path = root / "manifest.json"
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    payload["assets"][0]["sha256"] = "a" * 64
    manifest_path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(HyperframesUnitError) as excinfo:
        resolve_assets(
            _unit("animatic_preview", preview_intent=PREVIEW_INTENT), repo_root=root,
        )

    assert any("sha256 mismatch" in e for e in excinfo.value.errors)


def test_a_quarantined_render_can_never_be_promoted_into_a_manifest(tmp_path):
    """The quarantine is enforced, not conventional.

    A manifest entry pointing into the quarantine directory is refused even by a
    fully approved manifest, so a preview render cannot be laundered into the
    asset flow by registering its output.
    """

    rel = f"{QUARANTINE_DIR}/unit-x-preview.png"
    root = _repo(tmp_path, review_status="rights_reviewed", asset_rel=rel)

    with pytest.raises(HyperframesUnitError) as excinfo:
        resolve_assets(_unit("vertical_short"), repo_root=root)

    joined = " ".join(excinfo.value.errors)
    assert "quarantine" in joined
    assert "never be promoted" in joined


def test_the_quarantine_guard_holds_even_for_previews_themselves(tmp_path):
    """A preview may not chain off another preview's output either."""

    rel = f"{QUARANTINE_DIR}/unit-x-preview.png"
    root = _repo(tmp_path, review_status="review_only", asset_rel=rel)

    with pytest.raises(HyperframesUnitError) as excinfo:
        resolve_assets(
            _unit("animatic_preview", preview_intent=PREVIEW_INTENT), repo_root=root,
        )

    assert any("quarantine" in e for e in excinfo.value.errors)
