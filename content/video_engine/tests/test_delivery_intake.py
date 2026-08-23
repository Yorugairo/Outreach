from __future__ import annotations

import hashlib
from pathlib import Path

import pytest
from PIL import Image

from content.video_engine.src.services.delivery_intake import (
    CLEAN,
    FAIL,
    FLAG,
    DeliveryIntakeError,
    scan_delivery,
)


def _cutout(path: Path, size=(1024, 1536), alpha_max=254) -> str:
    """A plausible cutout: transparent margin, opaque-ish figure, dark edge."""

    im = Image.new("RGBA", size, (0, 0, 0, 0))
    x0, y0 = size[0] // 4, size[1] // 4
    for y in range(y0, size[1] - y0):
        for x in range(x0, size[0] - x0):
            im.putpixel((x, y), (60, 50, 40, alpha_max))
    im.save(path)
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _plate(path: Path, size=(1536, 1024)) -> str:
    Image.new("RGB", size, (240, 230, 200)).save(path)
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _asset(asset_id: str, sha: str, **over) -> dict:
    asset = {
        "asset_id": asset_id,
        "path": f"{asset_id}.png",
        "sha256": sha,
        "kind": "actor",
        "style_version": "paper-cut-reduced-density-v2",
        "semantic_tags": ["host"],
        "resolution_tier": 2,
        "render_eligible": False,
        "review_state": "review_only",
    }
    asset.update(over)
    return asset


def _scan(tmp_path, *assets, **kwargs):
    return scan_delivery(list(assets), delivery_root=tmp_path, **kwargs)


def _row(report, asset_id):
    return next(r for r in report["assets"] if r["asset_id"] == asset_id)


def _status(row, check):
    return next(c for c in row["checks"] if c["check"] == check)


# --- the episode-1 v2 verdicts, held as regressions ---------------------------


def test_a_self_promoted_asset_fails_intake(tmp_path):
    """The v2 batch arrived with every asset already render-eligible."""

    sha = _cutout(tmp_path / "actor-host-v1.png")
    report = _scan(tmp_path, _asset(
        "actor-host-v1", sha,
        rights_state="approved", review_state="approved_reusable", render_eligible=True,
    ))

    row = _row(report, "actor-host-v1")
    check = _status(row, "promotion")
    assert row["status"] == FAIL
    assert check["status"] == FAIL
    assert "render_eligible=True" in check["measured"]
    assert "operator" in check["note"]


def test_a_tier_three_actor_is_failed_as_unreachable(tmp_path):
    """Nineteen v2 assets sat where the resolver could never return them."""

    sha = _cutout(tmp_path / "actor-host-v1.png")
    report = _scan(tmp_path, _asset("actor-host-v1", sha, resolution_tier=3))

    check = _status(_row(report, "actor-host-v1"), "tier")
    assert check["status"] == FAIL
    assert "invisible to the" in check["note"]
    assert check["measured"] == "tier 3"
    assert check["expected"] == "tier 2"


def test_an_interior_at_the_wrong_human_scale_fails_with_both_numbers(tmp_path):
    """The v2 interiors: chair back at 0.45 implies a 0.93 adult against 0.50."""

    sha = _plate(tmp_path / "world-office-v1.png")
    report = _scan(tmp_path, _asset(
        "world-office-v1", sha, kind="world_board",
        placement={"figure_zone": [0.55, 1.0], "baseline_y": 0.98, "figure_height": 0.50},
        scale_reference={"object": "chair back", "real_height_m": 0.85, "drawn_height": 0.45},
    ))

    check = _status(_row(report, "world-office-v1"), "scale")
    assert check["status"] == FAIL
    assert "0.93" in check["measured"] and "0.50" in check["measured"]


# --- file integrity -----------------------------------------------------------


def test_a_digest_mismatch_fails_naming_both_digests(tmp_path):
    _cutout(tmp_path / "actor-host-v1.png")
    report = _scan(tmp_path, _asset("actor-host-v1", "a" * 64))

    check = _status(_row(report, "actor-host-v1"), "digest")
    assert check["status"] == FAIL
    assert check["expected"] == "a" * 16
    assert check["measured"] != check["expected"]


def test_a_missing_file_fails_and_skips_pixel_checks(tmp_path):
    report = _scan(tmp_path, _asset("actor-ghost-v1", "a" * 64))

    row = _row(report, "actor-ghost-v1")
    assert _status(row, "digest")["status"] == FAIL
    assert not any(c["check"] == "dimensions" for c in row["checks"])
    # Non-pixel governance checks still run.
    assert any(c["check"] == "promotion" for c in row["checks"])


def test_a_cutout_without_alpha_fails(tmp_path):
    sha = _plate(tmp_path / "actor-flat-v1.png", size=(1024, 1536))
    report = _scan(tmp_path, _asset("actor-flat-v1", sha))

    assert _status(_row(report, "actor-flat-v1"), "alpha")["status"] == FAIL


def test_off_contract_dimensions_flag_rather_than_fail(tmp_path):
    """In-scene mechanism plates legitimately ship at world size."""

    sha = _cutout(tmp_path / "mechanism-basket-v1.png", size=(1536, 1024))
    report = _scan(tmp_path, _asset(
        "mechanism-basket-v1", sha, kind="mechanism", resolution_tier=3,
    ))

    check = _status(_row(report, "mechanism-basket-v1"), "dimensions")
    assert check["status"] == FLAG
    assert check["measured"] == "1536x1024"
    assert check["expected"] == "1024x1024"


# --- ordering and shape -------------------------------------------------------


def test_assets_sort_failed_first_then_flagged_then_clean(tmp_path):
    clean_sha = _cutout(tmp_path / "actor-clean-v1.png")
    flag_sha = _cutout(tmp_path / "actor-odd-v1.png", size=(900, 1400))
    report = _scan(
        tmp_path,
        _asset("actor-clean-v1", clean_sha),
        _asset("actor-bad-v1", "a" * 64),
        _asset("actor-odd-v1", flag_sha),
    )

    assert [r["asset_id"] for r in report["assets"]] == [
        "actor-bad-v1", "actor-odd-v1", "actor-clean-v1",
    ]
    assert report["counts"] == {FAIL: 1, FLAG: 1, CLEAN: 1}


def test_a_clean_asset_is_clean_on_every_check(tmp_path):
    sha = _cutout(tmp_path / "actor-host-v1.png")
    report = _scan(tmp_path, _asset("actor-host-v1", sha))

    row = _row(report, "actor-host-v1")
    assert row["status"] == CLEAN
    assert all(c["status"] == CLEAN for c in row["checks"])


def test_every_verdict_carries_measured_and_expected(tmp_path):
    sha = _cutout(tmp_path / "actor-host-v1.png")
    report = _scan(tmp_path, _asset("actor-host-v1", sha, resolution_tier=3))

    for row in report["assets"]:
        for check in row["checks"]:
            assert check["measured"] is not None, check
            assert check["expected"] is not None, check


def test_a_missing_style_version_fails(tmp_path):
    sha = _cutout(tmp_path / "actor-host-v1.png")
    report = _scan(tmp_path, _asset("actor-host-v1", sha, style_version=None))

    assert _status(_row(report, "actor-host-v1"), "style")["status"] == FAIL


def test_a_version_outside_every_family_is_flagged(tmp_path):
    sha = _cutout(tmp_path / "actor-host-v1.png")
    report = _scan(
        tmp_path,
        _asset("actor-host-v1", sha, style_version="brand-new-style-v9"),
        style_families={"ep1": ["paper-cut-reduced-density-v2"]},
    )

    check = _status(_row(report, "actor-host-v1"), "style")
    assert check["status"] == FLAG
    assert "family" in check["note"]


def test_the_scan_writes_nothing(tmp_path):
    sha = _cutout(tmp_path / "actor-host-v1.png")
    before = {p: p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}

    _scan(tmp_path, _asset("actor-host-v1", sha))

    after = {p: p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}
    assert before == after


def test_an_empty_delivery_is_refused(tmp_path):
    with pytest.raises(DeliveryIntakeError):
        scan_delivery([], delivery_root=tmp_path)


def test_a_missing_delivery_root_is_refused(tmp_path):
    with pytest.raises(DeliveryIntakeError) as excinfo:
        scan_delivery([{"asset_id": "x"}], delivery_root=tmp_path / "absent")

    assert any("absent" in e for e in excinfo.value.errors)
