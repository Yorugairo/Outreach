"""Pinned Blender proof of the editable two-rig source-clock exchange."""

from __future__ import annotations

from contextlib import contextmanager
import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from types import SimpleNamespace

import pytest

from content.video_engine.scripts.model_foot_contact_probe import _blender_environment, pinned_blender
from content.video_engine.src.modeling.blender.contact import ROOT, SOURCE_SHA256, sha256_file
from content.video_engine.src.modeling.blender import fight_motion
from content.video_engine.src.modeling.blender.fight_motion import (
    FIXTURE_SHA256,
    FightMotionError,
    RENDER_FRAMES,
    REVIEW_RELATIVE,
    validate_fixture,
    validate_output_target,
)


FIXTURE = Path(__file__).parent / "fixtures/modeling/blender/characters/source-exchange/exchange.v1.json"
WORKER = FIXTURE.parent / "run_exchange.py"
REVIEW_ROOT = ROOT / REVIEW_RELATIVE
REVIEW_TEST_PREFIX = ".test-fight-motion-"


@contextmanager
def _owned_review_child():
    review_root = REVIEW_ROOT.resolve(strict=True)
    temporary = tempfile.TemporaryDirectory(prefix=REVIEW_TEST_PREFIX, dir=review_root)
    child = Path(temporary.name)
    try:
        assert child.parent.resolve() == review_root
        assert child.is_dir() and not child.is_symlink()
        assert not any(child.iterdir())
        yield child
    finally:
        assert child.parent.resolve() == review_root
        assert child.name.startswith(REVIEW_TEST_PREFIX)
        assert not child.is_symlink()
        temporary.cleanup()


def _run_blender(tmp_path: Path, *args: str, marker: str) -> dict:
    command = [str(pinned_blender()), "--background", "--factory-startup", "--disable-autoexec",
               "--python", str(WORKER), "--", *args]
    run = subprocess.run(command, cwd=ROOT, env=_blender_environment(tmp_path),
                         capture_output=True, text=True, timeout=180, check=False)
    output = run.stdout + run.stderr
    assert run.returncode == 0 and "Traceback" not in output, output
    values = [line.removeprefix(marker) for line in run.stdout.splitlines()
              if line.startswith(marker)]
    assert len(values) == 1, output
    return json.loads(values[0])


def test_exchange_preflight_pins_source_roles_clock_and_budgets(tmp_path: Path) -> None:
    fixture = validate_fixture(ROOT, FIXTURE)
    assert fixture["source_blend"]["sha256"] == SOURCE_SHA256
    assert fixture["roles"] == {
        "attacker": "screen_right_light_shorts_faces_left",
        "receiver": "screen_left_dark_shorts_faces_right",
    }
    assert fixture["observed_windows"] == {
        "first_right_contact": [10, 11], "first_follow_through": 12,
        "left_hook_contact": 24, "left_head_response": 25,
        "left_follow_through": 26,
    }
    assert tuple(fixture["render_frames"]) == RENDER_FRAMES
    assert fixture["budgets_m"]["planted_sole_slip_xy"] == 0.01

    stale = json.loads(json.dumps(fixture))
    stale["source_video"]["sha256"] = "0" * 64
    changed = tmp_path / "stale.json"
    changed.write_text(json.dumps(stale), encoding="utf-8")
    with pytest.raises(FightMotionError, match="stale source_video hash"):
        validate_fixture(ROOT, changed)

    escaped = json.loads(json.dumps(fixture))
    escaped["source_video"]["path"] = "../outside.mkv"
    changed.write_text(json.dumps(escaped), encoding="utf-8")
    with pytest.raises(FightMotionError, match="unsafe source_video path"):
        validate_fixture(ROOT, changed)

    wrong_clock = json.loads(json.dumps(fixture))
    wrong_clock["fps"] = 24
    changed.write_text(json.dumps(wrong_clock), encoding="utf-8")
    with pytest.raises(FightMotionError, match="fixture/clock/render contract changed"):
        validate_fixture(ROOT, changed)


@pytest.mark.parametrize("variant", ["roles", "observed_windows", "budget", "keyframe"])
def test_fixture_rejects_full_document_changes_even_with_self_declared_hash(
    tmp_path: Path, variant: str,
) -> None:
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    if variant == "roles":
        fixture["roles"]["attacker"] = "altered_role"
    elif variant == "observed_windows":
        fixture["observed_windows"]["first_right_contact"] = [10, 12]
    elif variant == "budget":
        fixture["budgets_m"]["planted_sole_slip_xy"] = 0.011
    else:
        fixture["keyframes"][1]["attacker_x"] = 0.561

    # A plausible payload digest must not authorize an alternate fixture.
    declared_payload = (json.dumps(fixture, indent=2) + "\n").encode("utf-8")
    fixture["fixture_sha256"] = hashlib.sha256(declared_payload).hexdigest()
    changed = tmp_path / f"{variant}.json"
    changed.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")

    with pytest.raises(FightMotionError, match="SHA-256 differs from the pinned document"):
        validate_fixture(ROOT, changed)


def test_output_preflight_rejects_escape_before_blender_mutation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(fight_motion.sys, "argv", ["blender", "--disable-autoexec"])
    mutations = []
    bpy = SimpleNamespace(
        app=SimpleNamespace(version_string="5.2.2 LTS"),
        ops=SimpleNamespace(wm=SimpleNamespace(
            read_factory_settings=lambda **kwargs: mutations.append(kwargs),
        )),
    )
    outside = tmp_path / "outside-review"

    with pytest.raises(FightMotionError, match="approved review quarantine"):
        fight_motion.build_exchange(bpy, ROOT, FIXTURE, outside, render=False)

    assert not outside.exists()
    assert mutations == []


def test_output_preflight_rejects_review_root_and_nonempty_target() -> None:
    with pytest.raises(FightMotionError, match="direct child"):
        validate_output_target(ROOT, REVIEW_ROOT)

    with _owned_review_child() as output:
        preserved = output / "existing.txt"
        preserved.write_text("preserve this existing target", encoding="utf-8")
        with pytest.raises(FightMotionError, match="new or empty directory"):
            validate_output_target(ROOT, output)
        assert preserved.read_text(encoding="utf-8") == "preserve this existing target"


def _make_directory_redirect(link: Path, target: Path) -> None:
    assert not link.exists() and not link.is_symlink()
    try:
        link.symlink_to(target, target_is_directory=True)
        return
    except (NotImplementedError, OSError) as symlink_error:
        if os.name != "nt":
            pytest.skip(f"directory symlink unavailable: {symlink_error}")

    try:
        result = subprocess.run(
            ["cmd.exe", "/d", "/c", "mklink", "/J", str(link), str(target)],
            capture_output=True, text=True, check=False,
        )
    except OSError as junction_error:
        pytest.skip(f"Windows directory symlink and junction creation unavailable: {junction_error}")
    if result.returncode != 0:
        pytest.skip(f"Windows directory symlink and junction creation unavailable: {result.stderr}")


def test_output_preflight_rejects_ancestor_redirect(tmp_path: Path) -> None:
    target = tmp_path / "redirect-target"
    target.mkdir()
    sentinel = target / "preserve.txt"
    sentinel.write_text("outside target remains untouched", encoding="utf-8")

    with _owned_review_child() as owned:
        redirect = owned / "redirect"
        _make_directory_redirect(redirect, target)
        with pytest.raises(FightMotionError, match="symlink/junction redirection"):
            validate_output_target(ROOT, redirect / "derived-output")
        assert not (target / "derived-output").exists()

    assert sentinel.read_text(encoding="utf-8") == "outside target remains untouched"


def test_reopen_measurement_receipt_checks_all_rows_summary_budgets_and_exposure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    rows = [{"frame": frame, "probe": frame} for frame in range(36)]
    counts = {"attacker": {"hand_R": 1}, "receiver": {"hand_L": 1}}

    def summary(observed, budgets):
        return {
            "max_probe": max(row["probe"] for row in observed),
            "checks": {
                "nonnegative_probe": all(row["probe"] >= 0 for row in observed),
                "pinned_budget": budgets["planted_sole_slip_xy"] == 0.01,
            },
        }

    monkeypatch.setattr(fight_motion, "_summary", summary)
    receipt = {
        "fixture_sha256": fight_motion.FIXTURE_SHA256,
        "roles": fixture["roles"],
        "budgets_predeclared_m": fixture["budgets_m"],
        "exposure_24fps": fight_motion._exposure_map(),
        "mesh_witness_vertex_counts": counts,
        "frames": copy.deepcopy(rows),
        "metrics": summary(rows, fixture["budgets_m"]),
    }
    fight_motion._validate_reopened_measurements(rows, counts, receipt, fixture)

    changed = copy.deepcopy(receipt)
    changed["frames"][17]["probe"] = -17
    with pytest.raises(FightMotionError, match="frame 17"):
        fight_motion._validate_reopened_measurements(rows, counts, changed, fixture)

    changed = copy.deepcopy(receipt)
    changed["metrics"]["max_probe"] = 99
    with pytest.raises(FightMotionError, match="summary metrics differ"):
        fight_motion._validate_reopened_measurements(rows, counts, changed, fixture)

    changed = copy.deepcopy(receipt)
    changed["budgets_predeclared_m"]["planted_sole_slip_xy"] = 0.02
    with pytest.raises(FightMotionError, match="budgets differ"):
        fight_motion._validate_reopened_measurements(rows, counts, changed, fixture)

    changed = copy.deepcopy(receipt)
    changed["exposure_24fps"]["head_snap"]["output_frame_24fps"] += 1
    with pytest.raises(FightMotionError, match="exposure mapping differs"):
        fight_motion._validate_reopened_measurements(rows, counts, changed, fixture)

    failed_rows = copy.deepcopy(rows)
    failed_rows[17]["probe"] = -1
    failed_receipt = copy.deepcopy(receipt)
    failed_receipt["frames"] = copy.deepcopy(failed_rows)
    failed_receipt["metrics"] = summary(failed_rows, fixture["budgets_m"])
    with pytest.raises(FightMotionError, match="fails one or more declared motion checks"):
        fight_motion._validate_reopened_measurements(failed_rows, counts, failed_receipt, fixture)


def test_receipt_render_manifest_requires_verified_pngs_in_receipt_directory(tmp_path: Path) -> None:
    png_header = (
        b"\x89PNG\r\n\x1a\n" + (13).to_bytes(4, "big") + b"IHDR"
        + (540).to_bytes(4, "big") + (960).to_bytes(4, "big")
        + bytes((8, 2, 0, 0, 0))
    )
    renders = {}
    for frame in RENDER_FRAMES:
        name = f"frame-{frame:02d}.png"
        path = tmp_path / name
        path.write_bytes(png_header)
        renders[str(frame)] = {
            "path": name, "sha256": sha256_file(path), "bytes": path.stat().st_size,
        }
    receipt_path = tmp_path / "receipt.json"
    receipt = {"renders": renders}
    assert fight_motion._verify_receipt_renders(receipt, receipt_path) == "verified"
    assert fight_motion._verify_receipt_renders({"renders": {}}, receipt_path) == "not_listed"

    stale = copy.deepcopy(receipt)
    stale["renders"]["8"]["sha256"] = "0" * 64
    with pytest.raises(FightMotionError, match="SHA-256 differs"):
        fight_motion._verify_receipt_renders(stale, receipt_path)

    missing = copy.deepcopy(receipt)
    (tmp_path / "frame-08.png").unlink()
    with pytest.raises(FightMotionError, match="missing or redirected"):
        fight_motion._verify_receipt_renders(missing, receipt_path)


def test_saved_exchange_reopens_with_measured_contacts_and_follow_through(tmp_path: Path) -> None:
    source = ROOT / "content/video_engine/assets/modeling/native/fighter-family-v1.1.blend"
    before = sha256_file(source)
    with _owned_review_child() as output:
        built = _run_blender(tmp_path, "build", str(FIXTURE), str(output), "no-render",
                             marker="FIGHT_MOTION_JSON=")
        assert built["status"] == "review_only_diagnostic"
        receipt_path = output / "receipt.json"
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        assert receipt["schema"] == "model_fight_motion.v1"
        assert receipt["fps"] == 30
        assert receipt["frame_range"] == [0, 35]
        assert receipt["source_blend_sha256_after"] == before == SOURCE_SHA256
        assert receipt["fixture_sha256"] == FIXTURE_SHA256
        assert receipt["scene"]["sha256"] == sha256_file(output / "source-exchange.blend")
        assert receipt["actions"]["attacker"] != receipt["actions"]["receiver"]
        assert receipt["camera"]["resolution_px"] == [540, 960]
        assert len(receipt["frames"]) == 36
        assert all(receipt["metrics"]["checks"].values()), receipt["metrics"]
        assert receipt["exposure_24fps"]["left_hook_contact"]["output_frame_24fps"] == 19
        assert receipt["exposure_24fps"]["head_snap"]["output_frame_24fps"] == 20
        assert receipt["frames"][26]["l_hand_head_axial_gap_m"] < receipt["frames"][24]["l_hand_head_axial_gap_m"]
        assert receipt["frames"][12]["r_hand_head_axial_gap_m"] < receipt["frames"][11]["r_hand_head_axial_gap_m"]
        reopened = _run_blender(tmp_path, "reopen", str(output / "source-exchange.blend"),
                                str(receipt_path), marker="FIGHT_REOPEN_JSON=")
        assert reopened["status"] == "reopened_and_measured"
        assert reopened["scene_sha256"] == receipt["scene"]["sha256"]
        assert reopened["checked_frames"] == list(range(36))
        assert reopened["checked_frame_count"] == 36
        assert reopened["summary_verified"] is True
        assert reopened["exposure_verified"] is True
        assert reopened["render_verification"] == "not_listed"

        # Corrupt only a disposable copy, then refresh its receipt hash so the
        # reopen check reaches the skin-binding invariant.
        corrupt_scene = output / "missing-armature-modifier.blend"
        shutil.copy2(output / "source-exchange.blend", corrupt_scene)
        corruption = _run_blender(
            tmp_path, "remove-armature", str(corrupt_scene), "attacker__Human",
            marker="FIGHT_MOTION_CORRUPTION_JSON=",
        )
        assert corruption["armature_modifiers_removed"] >= 1
        corrupt_receipt = copy.deepcopy(receipt)
        corrupt_receipt["scene"] = {
            "path": corrupt_scene.name,
            "sha256": sha256_file(corrupt_scene),
            "bytes": corrupt_scene.stat().st_size,
        }
        corrupt_receipt_path = output / "missing-armature-modifier-receipt.json"
        corrupt_receipt_path.write_text(json.dumps(corrupt_receipt), encoding="utf-8")
        rejected = _run_blender(
            tmp_path, "reopen", str(corrupt_scene), str(corrupt_receipt_path),
            marker="FIGHT_REOPEN_REJECTED_JSON=",
        )
        assert "reopened skin rig binding differs" in rejected["error"]
        assert sha256_file(source) == before
