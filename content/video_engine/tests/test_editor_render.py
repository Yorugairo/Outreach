from __future__ import annotations

import json
from pathlib import Path
from subprocess import CompletedProcess

import pytest

from content.video_engine.src.services import editor_render
from content.video_engine.src.services.editor_render import (
    EditorRenderError,
    compose_props,
    render_for_claim,
    render_headless,
)


def _claim(tmp_path: Path) -> dict:
    delivery = tmp_path / "review" / "claims" / "batch-one"
    (delivery / "objects").mkdir(parents=True)
    (delivery / "objects" / "object-a-v1.png").write_bytes(b"png")
    manifest = {
        "style_family": "fam-v3",
        "assets": [{"asset_id": "object-a-v1", "path": "objects/object-a-v1.png",
                    "sha256": "a" * 64, "kind": "prop"}],
    }
    (delivery / "batch-one.manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    return {"claim_id": "batch-one", "delivery_dir": str(delivery),
            "project_root": str(tmp_path)}


def test_compose_props_is_pure_translation_from_the_manifest(tmp_path):
    claim = _claim(tmp_path)

    props_path = compose_props(claim, project_root=tmp_path, audio_path="audio/take.wav")

    assert "runtime" in props_path.parts
    props = json.loads(props_path.read_text(encoding="utf-8"))
    asset = props["assets"][0]
    assert asset["asset_id"] == "object-a-v1"
    assert asset["sha256"] == "a" * 64, "copied, never recomputed here"
    assert props["audio"] == "audio/take.wav"
    assert props["style_family"] == "fam-v3"


def test_compose_props_without_a_manifest_is_a_named_error(tmp_path):
    claim = {"claim_id": "x", "delivery_dir": str(tmp_path / "empty")}
    (tmp_path / "empty").mkdir()

    with pytest.raises(EditorRenderError) as excinfo:
        compose_props(claim, project_root=tmp_path)

    assert "manifest" in " ".join(excinfo.value.errors)


def test_render_goes_through_the_boundary_with_props(tmp_path, monkeypatch):
    commands: list[list[str]] = []
    monkeypatch.setattr(editor_render, "_run_command",
                        lambda cmd, cwd, timeout: commands.append(cmd) or
                        CompletedProcess(cmd, 0, stdout="", stderr=""))
    monkeypatch.setattr(editor_render.shutil, "which", lambda name: "npx")
    monkeypatch.setattr(editor_render, "EDITOR_DIR", tmp_path)
    props = tmp_path / "p.json"
    props.write_text("{}", encoding="utf-8")

    result = render_headless("EditorialMotion", str(props))

    assert commands[0][:4] == ["npx", "remotion", "render", "src/index.tsx"]
    assert "--props" in commands[0]
    assert result["output"].endswith(".mp4")


def test_a_failed_render_surfaces_the_stderr_tail_verbatim(tmp_path, monkeypatch):
    monkeypatch.setattr(editor_render, "_run_command",
                        lambda cmd, cwd, timeout: CompletedProcess(
                            cmd, 1, stdout="", stderr="line1\nCannot find module 'remotion'"))
    monkeypatch.setattr(editor_render.shutil, "which", lambda name: "npx")
    monkeypatch.setattr(editor_render, "EDITOR_DIR", tmp_path)

    with pytest.raises(EditorRenderError) as excinfo:
        render_headless("Editorial")

    joined = " ".join(excinfo.value.errors)
    assert "exited 1" in joined
    assert "Cannot find module 'remotion'" in joined


def test_an_unknown_composition_is_refused_by_name(tmp_path):
    with pytest.raises(EditorRenderError) as excinfo:
        render_headless("NotAComposition")

    assert "NotAComposition" in " ".join(excinfo.value.errors)


def test_the_claim_hook_skips_unless_the_claim_opts_in(tmp_path):
    claim = _claim(tmp_path)

    result = render_for_claim(claim, project_root=tmp_path)

    assert result["status"] == "skipped"
    assert "editor_composition" in result["reason"]


def test_the_claim_hook_renders_when_declared(tmp_path, monkeypatch):
    monkeypatch.setattr(editor_render, "_run_command",
                        lambda cmd, cwd, timeout: CompletedProcess(cmd, 0, stdout="", stderr=""))
    monkeypatch.setattr(editor_render.shutil, "which", lambda name: "npx")
    monkeypatch.setattr(editor_render, "EDITOR_DIR", tmp_path)
    claim = {**_claim(tmp_path), "editor_composition": "EditorialMotion"}

    result = render_for_claim(claim, project_root=tmp_path)

    assert result["status"] == "done"
    assert result["props"].endswith("batch-one.props.json")
