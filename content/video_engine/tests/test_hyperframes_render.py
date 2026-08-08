from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from content.video_engine.src.services.hyperframes_render import (
    HyperframesConfig,
    HyperframesUnitError,
    compile_unit,
    render_unit,
    resolve_assets,
    validate_unit,
)

_PNG_BYTES = bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c489"
    "0000000d49444154789c626001000000ffff03000006000557bfabd40000000049454e44ae426082"
)


def _words(count: int = 8, step: float = 0.5) -> list[dict]:
    return [
        {"w": f"word{i}", "start_s": round(i * step, 3), "end_s": round((i + 1) * step, 3)}
        for i in range(count)
    ]


def _unit(**overrides) -> dict:
    unit = {
        "schema_version": "hyperframes_unit.v1",
        "unit_id": "teaser-ep1",
        "unit_kind": "vertical_short",
        "project_id": "history-of-bjj",
        "manifest_path": "manifest.json",
        "narration": {"canonical_hash": "a" * 64, "words": _words()},
        "plates": [
            {"asset_id": "plate-one", "start_s": 0.0, "end_s": 2.0},
            {"asset_id": "plate-two", "start_s": 2.0, "end_s": 4.0},
        ],
        "layout": {"aspect": "vertical", "background": "#0F0F12"},
        "output": {"quality": "draft", "format": "mp4", "max_duration_s": 58},
    }
    unit.update(overrides)
    return unit


def _write_manifest(root: Path, *, status: str = "rights_reviewed", corrupt_hash: bool = False) -> None:
    assets = []
    for asset_id in ("plate-one", "plate-two"):
        asset_path = root / "assets" / f"{asset_id}.png"
        asset_path.parent.mkdir(parents=True, exist_ok=True)
        asset_path.write_bytes(_PNG_BYTES)
        digest = hashlib.sha256(_PNG_BYTES).hexdigest()
        assets.append(
            {
                "id": asset_id,
                "path": f"assets/{asset_id}.png",
                "sha256": "0" * 64 if corrupt_hash else digest,
            }
        )
    (root / "manifest.json").write_text(
        json.dumps(
            {
                "schema_version": "asset_manifest.v1",
                "review": {"status": status},
                "assets": assets,
            }
        ),
        encoding="utf-8",
    )


def test_valid_unit_has_no_violations():
    assert validate_unit(_unit()) == []


def test_schema_rejects_renderer_paths_in_contract():
    violations = validate_unit(_unit(renderer_path="C:/somewhere/out.mp4"))
    assert any("renderer_path" in violation for violation in violations)


def test_plate_hold_bounds_are_enforced():
    short_hold = _unit(plates=[{"asset_id": "plate-one", "start_s": 0.0, "end_s": 1.0}])
    long_hold = _unit(plates=[{"asset_id": "plate-one", "start_s": 0.0, "end_s": 9.0}])
    assert any("minimum" in v for v in validate_unit(short_hold))
    assert any("ceiling" in v for v in validate_unit(long_hold))


def test_plate_gap_and_overlap_are_rejected():
    gapped = _unit(
        plates=[
            {"asset_id": "plate-one", "start_s": 0.0, "end_s": 2.0},
            {"asset_id": "plate-two", "start_s": 2.5, "end_s": 4.5},
        ]
    )
    assert any("gap/overlap" in v for v in validate_unit(gapped))


def test_resolve_rejects_unknown_asset(tmp_path: Path):
    _write_manifest(tmp_path)
    unit = _unit(plates=[{"asset_id": "plate-ghost", "start_s": 0.0, "end_s": 2.0}])
    with pytest.raises(HyperframesUnitError) as excinfo:
        resolve_assets(unit, repo_root=tmp_path)
    assert any("not in the approved manifest" in error for error in excinfo.value.errors)


def test_resolve_rejects_sha_mismatch(tmp_path: Path):
    _write_manifest(tmp_path, corrupt_hash=True)
    with pytest.raises(HyperframesUnitError) as excinfo:
        resolve_assets(_unit(), repo_root=tmp_path)
    assert any("sha256 mismatch" in error for error in excinfo.value.errors)


def test_resolve_rejects_unreviewed_manifest(tmp_path: Path):
    _write_manifest(tmp_path, status="draft")
    with pytest.raises(HyperframesUnitError) as excinfo:
        resolve_assets(_unit(), repo_root=tmp_path)
    assert any("approved status" in error for error in excinfo.value.errors)


def test_compile_is_deterministic_and_seek_safe(tmp_path: Path):
    _write_manifest(tmp_path)
    unit = _unit()
    assets = resolve_assets(unit, repo_root=tmp_path)
    first = compile_unit(unit, assets)
    second = compile_unit(unit, assets)
    assert first.html_text == second.html_text
    assert first.duration_s == 4.0
    assert 'data-duration="4.0"' in first.html_text
    assert 'data-width="1080"' in first.html_text and 'data-height="1920"' in first.html_text
    assert first.html_text.count('class="clip plate"') == 2
    assert first.html_text.count('class="clip caption"') == 2


def test_captions_can_be_disabled(tmp_path: Path):
    _write_manifest(tmp_path)
    unit = _unit(captions=False)
    compiled = compile_unit(unit, resolve_assets(unit, repo_root=tmp_path))
    assert 'class="clip caption"' not in compiled.html_text


def test_render_unit_dry_run_never_touches_cli(tmp_path: Path):
    _write_manifest(tmp_path)
    unit_path = tmp_path / "unit.json"
    unit_path.write_text(json.dumps(_unit()), encoding="utf-8")
    config = HyperframesConfig(project_dir=tmp_path / "does-not-exist")
    summary = render_unit(unit_path, config=config, repo_root=tmp_path, dry_run=True)
    assert summary["dry_run"] is True
    assert summary["expected_duration_s"] == 4.0
    assert summary["plates"] == 2


def test_render_unit_fails_closed_on_invalid_unit(tmp_path: Path):
    _write_manifest(tmp_path)
    broken = _unit()
    broken["narration"]["canonical_hash"] = "not-a-hash"
    unit_path = tmp_path / "unit.json"
    unit_path.write_text(json.dumps(broken), encoding="utf-8")
    with pytest.raises(HyperframesUnitError):
        render_unit(unit_path, config=HyperframesConfig(), repo_root=tmp_path, dry_run=True)
