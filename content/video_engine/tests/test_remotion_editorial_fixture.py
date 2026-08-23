from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[3]
EDITOR_ROOT = REPO_ROOT / "content" / "video_engine" / "editor"
FIXTURE_ROOT = EDITOR_ROOT / "fixtures" / "editorial-motion-two-shot"


def _fixture_props() -> dict:
    return json.loads((FIXTURE_ROOT / "props.json").read_text(encoding="utf-8"))


def _safe_local_asset(source: str | None) -> str | None:
    """Mirror the renderer's public-relative asset boundary for fixture cases."""

    if not isinstance(source, str) or not source.strip():
        return None
    normalized = source.replace("\\", "/").strip()
    if re.match(r"^(?:https?:|data:|blob:|file:|javascript:)", normalized, re.I):
        return None
    if normalized.startswith("/") or re.match(r"^[A-Za-z]:/", normalized):
        return None
    without_public = re.sub(r"^public/", "", normalized, flags=re.I)
    without_public = re.sub(r"^(?:\./)+", "", without_public)
    segments = without_public.split("/")
    if not without_public or any(segment in {"", ".", ".."} for segment in segments):
        return None
    return without_public


def test_editorial_motion_registers_dedicated_composition_and_preserves_legacy_lanes() -> None:
    source = (EDITOR_ROOT / "src" / "Root.tsx").read_text(encoding="utf-8")

    assert 'EditorialMotionComposition,' in source
    assert re.search(
        r'<Composition\s+id="Editorial"[\s\S]*?component=\{EditorialComposition\}',
        source,
    )
    assert re.search(
        r'<Composition\s+id="Documentary"[\s\S]*?component=\{DocumentaryComposition\}',
        source,
    )
    assert re.search(
        r'<Composition\s+id="EditorialMotion"[\s\S]*?component=\{EditorialMotionComposition\}',
        source,
    )
    assert "component={DocumentaryMotionComposition}" not in source


def test_two_shot_fixture_is_locked_local_and_uses_canonical_audio() -> None:
    props = _fixture_props()
    plan = props["plan"]
    shots = plan["shots"]

    assert len(shots) == 2
    assert [(shot["start_s"], shot["duration_s"]) for shot in shots] == [
        (0, 2),
        (2, 2),
    ]
    assert all(shot["camera"]["kind"] == "locked" for shot in shots)
    assert all(shot["camera"]["amount"] == 0 for shot in shots)
    assert all(shot["camera"]["move_s"] == 0 for shot in shots)

    asset_map = props["asset_map"]
    used_ids = {
        layer["asset_id"]
        for shot in shots
        for layer in shot["layers"]
    }
    assert used_ids == set(asset_map)
    for asset_id, relative_path in asset_map.items():
        assert _safe_local_asset(relative_path) == relative_path
        assert (FIXTURE_ROOT / "public" / relative_path).is_file(), asset_id

    audio_path = props["canonical_audio"]["path"]
    assert _safe_local_asset(audio_path) == audio_path
    assert audio_path.endswith(".wav")
    assert (FIXTURE_ROOT / "public" / audio_path).is_file()
    assert props["render_profile"] == {
        "width": 640,
        "height": 360,
        "fps": 15,
        "label": "p16-editorial-motion-two-shot",
    }


@pytest.mark.parametrize(
    "candidate",
    [
        "https://example.invalid/plate.svg",
        "data:image/svg+xml;base64,AAAA",
        "/absolute/plate.svg",
        "C:/absolute/plate.svg",
        "../outside/plate.svg",
        "assets/../outside/plate.svg",
        "assets/./plate.svg",
    ],
)
def test_fixture_negative_paths_fail_closed(candidate: str) -> None:
    assert _safe_local_asset(candidate) is None


def test_fixture_unknown_asset_id_is_not_resolvable() -> None:
    props = _fixture_props()
    approved = props["asset_map"]
    assert "fixture-not-approved" not in approved
    assert approved.get("fixture-not-approved") is None


def test_renderer_source_contains_fail_closed_asset_boundary() -> None:
    source = (EDITOR_ROOT / "src" / "EditorialMotion.tsx").read_text(encoding="utf-8")
    assert "remote, absolute, and traversal paths fail closed" in source
    assert "segments.some((segment) => !segment || segment === \".\" || segment === \"..\")" in source
    assert "return path ? staticFile(path) : undefined;" in source


def test_fixture_render_script_selects_local_composition_and_runtime_job() -> None:
    package = json.loads((EDITOR_ROOT / "package.json").read_text(encoding="utf-8"))
    script = package["scripts"]["render:editorial-motion-fixture"]
    render_script = (FIXTURE_ROOT / "render.mjs").read_text(encoding="utf-8")

    assert script == "node fixtures/editorial-motion-two-shot/render.mjs"
    assert '"EditorialMotion"' in render_script
    assert "--props=${propsPath}" in render_script
    assert "--public-dir=${publicDir}" in render_script
    assert 'path.join(runtimeDir, "jobs", "p16-fixture")' in render_script
    assert "Automator" not in render_script


def test_editorial_motion_asset_resolver_rejects_negative_cases_when_node_dependencies_exist(
    tmp_path: Path,
) -> None:
    """Exercise the TypeScript resolver when the local Remotion toolchain is present."""

    node = shutil.which("node")
    esbuild = EDITOR_ROOT / "node_modules" / "esbuild" / "bin" / "esbuild"
    if not node or not esbuild.is_file():
        pytest.skip("node_modules are not installed; source-level negative checks still run")

    bundle = tmp_path / "editorial-motion.cjs"
    result = subprocess.run(
        [
            node,
            str(esbuild),
            "src/EditorialMotion.tsx",
            "--bundle",
            "--platform=node",
            "--format=cjs",
            "--external:react",
            "--external:remotion",
            f"--outfile={bundle}",
        ],
        cwd=EDITOR_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode:
        pytest.skip(f"local esbuild could not bundle the resolver: {result.stderr}")

    probe = tmp_path / "probe.cjs"
    probe.write_text(
        """
const {normalizeEditorialMotionAsset, resolveEditorialMotionAsset} = require(process.argv[2]);
const invalid = [
  'https://example.invalid/plate.svg',
  '/absolute/plate.svg',
  'C:/absolute/plate.svg',
  '../outside/plate.svg',
  'assets/../outside/plate.svg',
];
for (const candidate of invalid) {
  if (normalizeEditorialMotionAsset(candidate) !== undefined) process.exit(10);
}
if (resolveEditorialMotionAsset('unapproved', {'approved': 'assets/plate.svg'}) !== undefined) process.exit(11);
if (normalizeEditorialMotionAsset('assets/plate.svg') !== 'assets/plate.svg') process.exit(12);
""",
        encoding="utf-8",
    )
    result = subprocess.run(
        [node, str(probe), str(bundle)],
        cwd=EDITOR_ROOT,
        env={**os.environ, "NODE_PATH": str(EDITOR_ROOT / "node_modules")},
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr or result.stdout
