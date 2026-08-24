"""Headless Remotion renders: compose props, run npm, land output in runtime/.

The console composes props; it never implements camera, timing or easing (the
P15 T10 rule, held by the structural motion-arithmetic sweep). ``compose_props``
is pure translation — every value is **copied** from artifacts (delivery
manifests, catalogue entries, canonical audio paths); nothing is computed.

The render itself goes through the editor package's own npm scripts, mirroring
``cli.py verify-editor``: resolve npm via ``shutil.which``, run with the editor
directory as cwd, surface stderr tails verbatim. One process boundary
(``_run_command``) for tests to monkeypatch.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from content.video_engine.src.services import paths as _paths

_ENGINE_ROOT = Path(__file__).resolve().parents[2]
EDITOR_DIR = _ENGINE_ROOT / "editor"
OUTPUT_SUBPATH = _paths.EDITOR_RENDERS_SUBPATH

_RENDER_TIMEOUT_S = 1800
_STDERR_TAIL_LINES = 20

COMPOSITIONS = ("Editorial", "Documentary", "EditorialMotion")


class EditorRenderError(Exception):
    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__("; ".join(errors))


def _run_command(command: list[str], cwd: Path, timeout: int) -> subprocess.CompletedProcess:
    """The single process boundary; tests monkeypatch this."""

    return subprocess.run(
        command, cwd=str(cwd), capture_output=True, text=True, timeout=timeout,
    )


def compose_props(
    claim: Mapping[str, Any],
    *,
    project_root: str | Path,
    audio_path: str | None = None,
) -> Path:
    """Translate a claim's delivered assets into an input-props file.

    Pure translation: asset ids, paths and digests are copied from the
    delivery manifest; the audio path is copied when given. Any timing the
    composition needs comes from its own defaultProps — never from here.
    """

    root = Path(project_root)
    delivery = Path(str(claim["delivery_dir"]))
    manifests = sorted(delivery.glob("*.manifest.json"))
    if not manifests:
        raise EditorRenderError([f"no *.manifest.json in {delivery}"])
    manifest = json.loads(manifests[0].read_text(encoding="utf-8"))

    props = {
        "schema_version": "editor_input_props.v1",
        "claim_id": claim.get("claim_id"),
        "style_family": manifest.get("style_family"),
        "assets": [
            {
                "asset_id": entry.get("asset_id"),
                "path": str((delivery / str(entry.get("path"))).resolve()),
                "sha256": entry.get("sha256"),
                "kind": entry.get("kind"),
            }
            for group in ("worlds", "finance_objects", "mechanism_plates", "assets")
            for entry in manifest.get(group) or []
        ],
        "audio": audio_path,
        "composed_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    out_dir = _paths.runtime_dir(root, "editor-props", ensure=True)
    out_path = out_dir / f"{claim.get('claim_id', 'claim')}.props.json"
    out_path.write_text(json.dumps(props, indent=2), encoding="utf-8")
    return out_path


def render_headless(composition: str, props_path: str | None = None) -> dict[str, Any]:
    """``npx remotion render`` through the boundary; output under runtime/."""

    if composition not in COMPOSITIONS:
        raise EditorRenderError([
            f"unknown composition {composition!r}; the pinned root defines {COMPOSITIONS}"
        ])
    npm = shutil.which("npx")
    if npm is None:
        raise EditorRenderError(["npx is not on PATH; install Node.js"])
    if not EDITOR_DIR.is_dir():
        raise EditorRenderError([f"no editor directory at {EDITOR_DIR}"])

    out_dir = _ENGINE_ROOT.joinpath(*OUTPUT_SUBPATH)
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output = out_dir / f"{composition}-{stamp}.mp4"

    command = ["npx", "remotion", "render", "src/index.tsx", composition, str(output)]
    if props_path:
        if not Path(props_path).exists():
            raise EditorRenderError([f"no props file at {props_path}"])
        command += ["--props", str(props_path)]

    result = _run_command(command, EDITOR_DIR, _RENDER_TIMEOUT_S)
    if result.returncode != 0:
        tail = "\n".join((result.stderr or "").splitlines()[-_STDERR_TAIL_LINES:])
        raise EditorRenderError([
            f"remotion render exited {result.returncode}", tail or "(no stderr)",
        ])
    return {"output": str(output), "composition": composition}


def render_for_claim(claim: Mapping[str, Any], *, project_root: str | Path) -> dict[str, Any]:
    """The claim-resume hook: render only when the claim asks for it.

    A claim declares ``editor_composition`` to opt in; anything else is a
    recorded skip — claim-resume treats absence of this lane as normal.
    """

    composition = str(claim.get("editor_composition") or "")
    if not composition:
        return {"status": "skipped", "reason": "no editor_composition declared on the claim"}
    try:
        props = compose_props(claim, project_root=project_root)
        result = render_headless(composition, str(props))
        return {"status": "done", **result, "props": str(props)}
    except EditorRenderError as exc:
        return {"status": "failed", "errors": exc.errors}
