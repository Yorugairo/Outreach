"""Real-Blender verification of independent native fighter instancing."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess

import pytest

from content.video_engine.scripts.model_foot_contact_probe import _blender_environment, pinned_blender
from content.video_engine.src.modeling.blender.character_instance import (
    CharacterInstanceError,
    append_character_instance,
)
from content.video_engine.src.modeling.blender.contact import (
    ROOT,
    SOURCE_RELATIVE,
    SOURCE_SHA256,
    sha256_file,
)


WORKER = Path(__file__).parent / "fixtures" / "modeling" / "blender" / "run_character_instance_probe.py"


def test_invalid_instance_request_fails_before_blender_append() -> None:
    base = {
        "source": ROOT / SOURCE_RELATIVE,
        "source_sha256": SOURCE_SHA256,
        "binding_id": "attacker",
        "rig_name": "Human.rigify",
        "object_names": ("Human.rigify", "Human"),
        "position_m": (0.0, 0.0, 0.0),
        "heading_rad": 0.0,
    }
    for replacement in (
        {"binding_id": "../unsafe"},
        {"object_names": ("Human.rigify", "Human.rigify")},
        {"position_m": (float("nan"), 0.0, 0.0)},
        {"heading_rad": float("inf")},
        {"source_sha256": "0" * 64},
    ):
        with pytest.raises(CharacterInstanceError):
            append_character_instance(None, **(base | replacement))


def test_two_real_blender_fighters_keep_rigs_actions_and_garments_private(tmp_path: Path) -> None:
    source = ROOT / SOURCE_RELATIVE
    assert sha256_file(source) == SOURCE_SHA256
    command = [
        str(pinned_blender()), "--background", "--factory-startup", "--disable-autoexec",
        "--python", str(WORKER), "--", str(source),
    ]
    run = subprocess.run(
        command,
        cwd=ROOT,
        env=_blender_environment(tmp_path),
        capture_output=True,
        text=True,
        timeout=90,
        check=False,
    )
    # Blender can exit 0 after a Python traceback; the marker is mandatory.
    assert run.returncode == 0 and "Traceback" not in run.stdout + run.stderr, run.stdout + run.stderr
    markers = [line.removeprefix("INSTANCE_JSON=") for line in run.stdout.splitlines()
               if line.startswith("INSTANCE_JSON=")]
    assert len(markers) == 1, run.stdout + run.stderr
    receipt = json.loads(markers[0])
    assert receipt["schema"] == "model_character_instance_probe.v1"
    assert receipt["status"] == "diagnostic_only"
    assert receipt["source_sha256_before_after"] == SOURCE_SHA256
    assert receipt["blender"] == "5.2.2 LTS"
    assert receipt["scene_fps"] == 30
    assert receipt["attacker_arm_movement_m"] > 0.015
    assert receipt["receiver_arm_movement_m"] < 0.000001
    assert set(receipt["instances"]) == {"attacker", "receiver"}
    attacker = receipt["instances"]["attacker"]
    receiver = receipt["instances"]["receiver"]
    assert attacker["root_x_m"] == 0.85
    assert receiver["root_x_m"] == -0.85
    assert attacker["face_axis_world_m"][0] < -0.08
    assert receiver["face_axis_world_m"][0] > 0.08
    assert receiver["body_bounds_m"][0][1] < attacker["body_bounds_m"][0][0]
    for binding_id, instance in receipt["instances"].items():
        assert instance["rig"] == f"{binding_id}__Human.rigify"
        assert instance["action"] == f"{binding_id}__source_action"
        assert len(instance["objects"]) == 11
        body_x = instance["body_bounds_m"][0]
        shorts_x = instance["shorts_bounds_m"][0]
        assert body_x[0] - 0.15 <= shorts_x[0] <= body_x[1] + 0.15
    assert sha256_file(source) == SOURCE_SHA256
