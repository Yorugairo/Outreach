"""Build the isolated v2 footage assembly without changing the reviewed v1.

This is intentionally a thin adapter around the proven v1 builder.  All
generated files stay below ``production/assembly-v2/``; the parent-owned
``edit-v2.json`` and ``audio/master-v2.wav`` are read but never rewritten.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
OLD_BUILDER = HERE.parent / "assembly" / "build_assembly.py"
SPEC = importlib.util.spec_from_file_location("knockout_assembly_base", OLD_BUILDER)
if SPEC is None or SPEC.loader is None:  # pragma: no cover - checkout invariant
    raise RuntimeError(f"cannot load v1 assembly builder: {OLD_BUILDER}")
BASE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = BASE
SPEC.loader.exec_module(BASE)
import gate_motion_density as MG
BASE.__doc__ = __doc__


EPISODE_ID = "knockout-brain-matchcut-001-v2"
TIMELINE_NAME = f"{EPISODE_ID}.timeline.json"
OUTPUT_NAME = f"{EPISODE_ID}.mp4"
SHOT_TABLE_RELATIVE = "production/assembly-v2/SHOT-TABLE.py"

# Override only the base module's path/configuration globals.  Its contract
# validation, seekable-clip encoding, scene compiler, and renderer remain the
# existing engine path used by the reviewed v1 assembly.
BASE.BUILD = HERE / "build"
BASE.SHOT_TABLE = HERE / "SHOT-TABLE.py"
BASE.TIMELINE_NAME = TIMELINE_NAME
BASE.EPISODE_ID = EPISODE_ID
BASE.DEFAULT_EDIT = PROJECT / "production" / "edit-v2.json"
BASE.DEFAULT_AUDIO = PROJECT / "production" / "audio" / "master-v2.wav"
# The spoken intro is unchanged; preserve its measured word clock.
BASE.DEFAULT_WORD_TIMINGS = PROJECT / "production" / "audio" / "intro.words.json"


_base_write_timeline_inputs = BASE._write_timeline_inputs


def _write_timeline_inputs_v2(edit: dict, audio: Path, word_timings_path: Path | None) -> None:
    _base_write_timeline_inputs(edit, audio, word_timings_path)
    path = BASE.BUILD / "timeline.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["script"] = "production/edit-v2.json"
    path.write_text(json.dumps(payload, indent=1), encoding="utf-8")


def _compile_v2() -> int:
    rc = BASE.T.compile_timeline(
        BASE.PROJECT,
        BASE.BUILD,
        timeline_name=BASE.TIMELINE_NAME,
        shot_table_file=SHOT_TABLE_RELATIVE,
        title=BASE.TITLE,
        subtitle=BASE.SUBTITLE,
        episode_id=BASE.EPISODE_ID,
        aspect=BASE.ASPECT,
        caption_style="phrase",
        kinetics={},
        render=False,
        form="short",
    )
    if rc:
        return rc

    # build_scene_timeline_f currently stamps a legacy project id.  Correct it
    # in this isolated build and regenerate the gate report against the same
    # final timeline hash; no shared engine source is changed.
    timeline_path = BASE.BUILD / BASE.TIMELINE_NAME
    timeline = json.loads(timeline_path.read_text(encoding="utf-8"))
    timeline["project_id"] = "martial-matters"
    timeline_path.write_text(json.dumps(timeline, indent=1), encoding="utf-8")
    MG.write_report(BASE.BUILD, BASE.TIMELINE_NAME)
    return 0


_base_render = BASE._render


def _render_v2(force_reason: str | None, workers: int, output_size: str) -> Path:
    rendered = _base_render(force_reason, workers, output_size)
    target = BASE.BUILD / "render" / OUTPUT_NAME
    if rendered.resolve() != target.resolve():
        rendered.replace(target)

    receipt_path = BASE.BUILD / "ASSEMBLY-RECEIPT.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    receipt["artifact"] = str(target)
    receipt["sha256"] = hashlib.sha256(target.read_bytes()).hexdigest()
    receipt["timeline"] = str(BASE.BUILD / BASE.TIMELINE_NAME)
    receipt["project_id"] = "martial-matters"
    receipt_path.write_text(json.dumps(receipt, indent=1), encoding="utf-8")
    return target


BASE._write_timeline_inputs = _write_timeline_inputs_v2
BASE._compile = _compile_v2
BASE._render = _render_v2


def main(argv: list[str] | None = None) -> int:
    """Delegate the CLI while retaining the v2 paths and output name."""
    return BASE.main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
