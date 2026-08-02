from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from content.video_engine.src.services.editorial import (
    EditorialManifestError,
    EditorialRenderError,
    EditorialService,
    ManifestImmutableError,
    MANIFEST_VERSION,
    manifest_sha256,
    validate_edit_manifest,
)


def _clips(tmp_path: Path) -> list[dict[str, object]]:
    paths: list[dict[str, object]] = []
    for index in range(1, 5):
        clip = tmp_path / f"scene_{index}.mp4"
        clip.write_bytes(b"scene")
        paths.append(
            {
                "scene_id": index,
                "path": str(clip),
                "duration_s": 1.0,
                "transition": {
                    1: "continuous",
                    2: "crossfade",
                    3: "match_cut",
                    4: "hard_cut",
                }[index],
            }
        )
    return paths


def test_manifest_is_canonical_and_immutable(tmp_path: Path) -> None:
    service = EditorialService()
    manifest = service.build_manifest(
        _clips(tmp_path),
        aspect="vertical",
        captions=[{"text": "Keep the hips framed", "from": 4, "duration_in_frames": 20}],
        overlays=[
            {
                "kind": "text",
                "text": "LEVERAGE",
                "from": 8,
                "duration_in_frames": 12,
            }
        ],
    )
    path = service.write_manifest(manifest, tmp_path / "edit_manifest.json", check_assets=True)

    loaded = json.loads(path.read_text(encoding="utf-8"))
    assert loaded["schema_version"] == MANIFEST_VERSION
    assert loaded["aspect"] == "vertical"
    assert loaded["width"] == 1080
    assert loaded["height"] == 1920
    assert [clip["transition"] for clip in loaded["clips"]] == [
        "continuous",
        "crossfade",
        "match_cut",
        "hard_cut",
    ]
    assert loaded["duration_in_frames"] == 102  # 4 x 30, less two 9-frame overlaps
    assert service.write_manifest(manifest, path, check_assets=True) == path

    changed = dict(manifest)
    changed["metadata"] = {"changed": True}
    with pytest.raises(ManifestImmutableError, match="immutable"):
        service.write_manifest(changed, path)


def test_manifest_validation_fails_closed_for_transition_and_assets(tmp_path: Path) -> None:
    with pytest.raises(EditorialManifestError, match="unsupported"):
        validate_edit_manifest(
            {
                "clips": [{"path": "scene.mp4", "duration_s": 1, "transition": "wipe"}]
            }
        )

    with pytest.raises(EditorialManifestError, match="does not exist"):
        validate_edit_manifest(
            {"clips": [{"path": "missing.mp4", "duration_s": 1}]},
            manifest_path=tmp_path / "edit_manifest.json",
            check_assets=True,
        )


def test_render_command_is_injected_and_does_not_require_chromium(tmp_path: Path) -> None:
    calls: list[tuple[list[str], dict[str, object]]] = []

    def runner(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        calls.append((list(command), kwargs))
        output = Path(command[5])
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(b"rendered")
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    service = EditorialService(editor_root=tmp_path / "editor", runner=runner)
    manifest = service.build_manifest(
        [{"path": "scene.mp4", "duration_s": 1.0}],
    )
    manifest_path = service.write_manifest(manifest, tmp_path / "edit_manifest.json")
    public_dir = tmp_path / "public"
    public_dir.mkdir()
    result = service.render_manifest(
        manifest_path,
        tmp_path / "out.mp4",
        public_dir=public_dir,
    )

    command, kwargs = calls[0]
    assert Path(command[0]).stem.casefold() == "npx"
    assert command[1:5] == ["remotion", "render", "src/index.tsx", "Editorial"]
    assert "--props" in command
    assert str(manifest_path) in command
    assert command[-2:] == ["--public-dir", str(public_dir.resolve())]
    assert kwargs["cwd"] == str(tmp_path / "editor")
    assert kwargs["encoding"] == "utf-8"
    assert kwargs["errors"] == "replace"
    assert result.output_path.exists()


def test_render_command_rejects_missing_public_directory(tmp_path: Path) -> None:
    service = EditorialService(editor_root=tmp_path / "editor")
    manifest_path = service.write_manifest(
        service.build_manifest([{"path": "scene.mp4", "duration_s": 1.0}]),
        tmp_path / "edit_manifest.json",
    )

    with pytest.raises(EditorialManifestError, match="public directory"):
        service.build_render_command(
            manifest_path,
            tmp_path / "out.mp4",
            public_dir=tmp_path / "missing",
        )


def test_render_can_report_missing_output_from_a_successful_runner(tmp_path: Path) -> None:
    service = EditorialService(
        editor_root=tmp_path / "editor",
        runner=lambda command, **kwargs: subprocess.CompletedProcess(
            command, 0, stdout="", stderr=""
        ),
    )
    manifest_path = service.write_manifest(
        service.build_manifest([{"path": "scene.mp4", "duration_s": 1.0}]),
        tmp_path / "edit_manifest.json",
    )
    with pytest.raises(EditorialRenderError, match="without output"):
        service.render_manifest(manifest_path, tmp_path / "missing.mp4")


def test_manifest_hash_is_stable_for_retries(tmp_path: Path) -> None:
    service = EditorialService()
    one = service.build_manifest([{"path": "scene.mp4", "duration_s": 1.0}])
    two = validate_edit_manifest(json.loads(json.dumps(one)))
    assert manifest_sha256(one) == manifest_sha256(two)


def test_build_edit_manifest_accepts_storyboard_and_scene_segments() -> None:
    service = EditorialService()
    manifest = service.build_edit_manifest(
        {"scenes": [{"scene_id": 1, "transition": {"in": "match_cut"}}]},
        {"segments": [{"scene_id": 1, "path": "scene.mp4", "duration_s": 1.0}]},
        target="vertical",
    )
    assert manifest["aspect"] == "vertical"
    assert manifest["segments"][0]["scene_id"] == 1
    assert manifest["clips"][0]["transition"] == "match_cut"
