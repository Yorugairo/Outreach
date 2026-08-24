from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

_SCRIPT = Path(__file__).resolve().parents[3] / "scripts" / "migrate_layout.py"
_spec = importlib.util.spec_from_file_location("migrate_layout", _SCRIPT)
migrate = importlib.util.module_from_spec(_spec)
import sys as _sys

# dataclasses resolves annotations via sys.modules[cls.__module__]; a module
# loaded from a file path must be registered there before execution.
_sys.modules["migrate_layout"] = migrate
_spec.loader.exec_module(migrate)


def _write(path: Path, data: bytes) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return hashlib.sha256(data).hexdigest()


def _project(tmp_path: Path) -> Path:
    """A legacy tree: catalogue-referenced assets plus a review delivery."""

    root = tmp_path / "project"
    world_sha = _write(root / "assets" / "worlds" / "world-a.png", b"world-bytes")
    layer_sha = _write(root / "assets" / "worlds" / "world-a-far.png", b"far-bytes")
    _write(root / "assets" / "generated" / "review" / "batch1" / "cutout.png", b"cutout")
    _write(
        root / "assets" / "generated" / "review" / "batch1" / "batch1.manifest.json",
        json.dumps({"style_family": "s", "assets": []}).encode(),
    )
    catalog = {
        "schema_version": "finance_asset_catalog.v1",
        "assets": [
            {
                "asset_id": "world-a",
                "path": "assets/worlds/world-a.png",
                "sha256": world_sha,
                "layers": [
                    {"depth_layer": "building_or_environment",
                     "path": "assets/worlds/world-a-far.png", "sha256": layer_sha},
                ],
            },
        ],
    }
    (root / migrate.CATALOG_FILENAME).write_text(json.dumps(catalog), encoding="utf-8")
    return root


def test_the_dry_run_plans_every_move_and_touches_nothing(tmp_path):
    root = _project(tmp_path)
    before = sorted(p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file())

    plan = migrate.build_plan(root)
    rendered = migrate.render_plan(plan)

    assert "assets/worlds/world-a.png  ->  canonical/assets/worlds/world-a.png" in rendered
    assert "review/batch1/cutout.png" in rendered
    after = sorted(p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file())
    assert after == before, "a dry run must not move, create, or delete anything"


def test_execute_moves_files_and_rewrites_the_catalogue_atomically(tmp_path):
    root = _project(tmp_path)

    plan = migrate.build_plan(root)
    migrate.execute(plan)

    catalog = json.loads((root / migrate.CATALOG_FILENAME).read_text(encoding="utf-8"))
    asset = catalog["assets"][0]
    assert asset["path"] == "canonical/assets/worlds/world-a.png"
    assert asset["layers"][0]["path"] == "canonical/assets/worlds/world-a-far.png"
    # Every path the catalogue names exists; no original lingers.
    assert (root / asset["path"]).exists()
    assert (root / asset["layers"][0]["path"]).exists()
    assert not (root / "assets" / "worlds" / "world-a.png").exists()
    assert (root / "review" / "batch1" / "cutout.png").exists()
    assert not (root / "assets" / "generated").exists()


def test_a_second_run_is_a_noop(tmp_path):
    root = _project(tmp_path)
    migrate.execute(migrate.build_plan(root))

    second = migrate.build_plan(root)

    assert second.is_noop
    assert migrate.execute(second) == []


def test_corrupt_bytes_fail_the_migration_before_the_catalogue_is_touched(tmp_path):
    root = _project(tmp_path)
    (root / "assets" / "worlds" / "world-a.png").write_bytes(b"tampered")

    with pytest.raises(migrate.MigrationError) as excinfo:
        migrate.execute(migrate.build_plan(root))

    assert "sha256" in " ".join(excinfo.value.errors)
    catalog = json.loads((root / migrate.CATALOG_FILENAME).read_text(encoding="utf-8"))
    assert catalog["assets"][0]["path"] == "assets/worlds/world-a.png", (
        "the live catalogue must never be rewritten when verification fails"
    )


def test_an_interrupted_run_resumes_safely(tmp_path):
    """A copy that happened before a crash is verified, not clobbered or doubled."""

    root = _project(tmp_path)
    plan = migrate.build_plan(root)
    # Simulate: first file was copied, then the process died.
    first = plan.moves[0]
    destination = root / first.destination
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes((root / first.source).read_bytes())

    migrate.execute(migrate.build_plan(root))

    catalog = json.loads((root / migrate.CATALOG_FILENAME).read_text(encoding="utf-8"))
    assert catalog["assets"][0]["path"].startswith("canonical/")
    assert not (root / first.source).exists()


def test_deep_paths_survive_on_windows(tmp_path):
    """The core.longpaths lesson: nesting must not break the move."""

    root = tmp_path / "project"
    deep = "assets/generated/review/" + "/".join(["deeply-nested-directory-name"] * 6) + "/asset.png"
    _write(root / Path(deep), b"deep")
    (root / migrate.CATALOG_FILENAME).write_text(json.dumps({"assets": []}), encoding="utf-8")

    migrate.execute(migrate.build_plan(root))

    moved = root / ("review/" + "/".join(["deeply-nested-directory-name"] * 6) + "/asset.png")
    assert moved.exists()
