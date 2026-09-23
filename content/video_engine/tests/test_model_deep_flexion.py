from __future__ import annotations

import hashlib
import json
import math
import struct
import zlib
from pathlib import Path
from types import SimpleNamespace

import pytest

from content.video_engine.scripts import model_deep_flexion as runner
from content.video_engine.src.modeling.blender import deep_flexion as flexion


def _png(width: int, height: int) -> bytes:
    def chunk(kind: bytes, data: bytes) -> bytes:
        body = kind + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)

    header = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    rows = b"".join(b"\x00" + b"\x00" * width * 4 for _ in range(height))
    return (
        flexion.PNG_SIGNATURE
        + chunk(b"IHDR", header)
        + chunk(b"IDAT", zlib.compress(rows))
        + chunk(b"IEND", b"")
    )


def _joint_pose(region_name: str, bend_degrees: float, center: list[float]) -> dict:
    upper_bone, lower_bone = flexion.REGIONS[region_name]["bones"]
    radians = math.radians(bend_degrees)
    return {
        "deform_bones": [upper_bone, lower_bone],
        "bone_vectors_world_m": {
            upper_bone: [1.0, 0.0, 0.0],
            lower_bone: [math.cos(radians), math.sin(radians), 0.0],
        },
        "bend_degrees": bend_degrees,
        "joint_center_world_m": center,
    }


def _fake_camera_matrix_with_back_direction(
    target_world_m: list[float], camera_back: list[float]
) -> list[list[float]]:
    back_length = math.sqrt(sum(value * value for value in camera_back))
    back = [value / back_length for value in camera_back]
    up_reference = [0.0, 0.0, 1.0]
    if abs(sum(up_reference[axis] * back[axis] for axis in range(3))) > 0.999:
        up_reference = [0.0, 1.0, 0.0]
    up_projected = [
        up_reference[axis] - sum(up_reference[j] * back[j] for j in range(3)) * back[axis]
        for axis in range(3)
    ]
    right = [
        up_projected[1] * back[2] - up_projected[2] * back[1],
        up_projected[2] * back[0] - up_projected[0] * back[2],
        up_projected[0] * back[1] - up_projected[1] * back[0],
    ]
    right_length = math.sqrt(sum(value * value for value in right))
    right = [value / right_length for value in right]
    up = [
        back[1] * right[2] - back[2] * right[1],
        back[2] * right[0] - back[0] * right[2],
        back[0] * right[1] - back[1] * right[0],
    ]
    rotation = [right, up, back]
    translation = [
        -sum(rotation[row][axis] * target_world_m[axis] for axis in range(3))
        + (-5.0 if row == 2 else 0.0)
        for row in range(3)
    ]
    return [
        [*rotation[row], translation[row]]
        for row in range(3)
    ] + [[0.0, 0.0, 0.0, 1.0]]


def _fake_saved_front_view_matrix() -> list[list[float]]:
    return [
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
        [0.0, -1.0, 0.0, -5.0],
        [0.0, 0.0, 0.0, 1.0],
    ]


def _fake_camera_view_matrix(
    region_name: str, target_world_m: list[float], state: dict
) -> list[list[float]]:
    normal = flexion._bone_plane_normal_world(state, region_name, f"fixture/{region_name}")
    return _fake_camera_matrix_with_back_direction(target_world_m, list(normal))


def _verified_run(tmp_path: Path) -> tuple[dict, Path, Path]:
    review_root = tmp_path / "review"
    output = review_root / "run-1"
    output.mkdir(parents=True)
    raw_regions = {}
    region_reports = {}
    evaluated_ids = list(range(242))
    topology_digest = flexion._source_id_digest(evaluated_ids)

    for region_index, (region_name, contract) in enumerate(flexion.REGIONS.items()):
        offset = region_index * 121
        ids = list(range(offset, offset + 121))
        triangles = []
        for row in range(10):
            for column in range(10):
                top_left = offset + row * 11 + column
                top_right = top_left + 1
                bottom_left = top_left + 11
                bottom_right = bottom_left + 1
                triangles.extend(
                    ([top_left, bottom_left, bottom_right], [top_left, bottom_right, top_right])
                )
        weights = [1.0] * len(ids)
        pv_weights = [0.0] * len(ids)
        samples = {}
        for config_index, config in enumerate(flexion.CONFIGURATIONS):
            samples[config] = {}
            for pose in flexion.POSE_KEYS:
                points = []
                for local_index in range(121):
                    row, column = divmod(local_index, 11)
                    x = column * 0.1 + region_index * 2.0 + config_index * 0.03
                    y = row * 0.1
                    z = 0.0
                    if pose == "deep_flexion":
                        x = x * 1.10
                        y = y * 0.90
                        z = (column / 10) * 0.02
                    points.append([round(x, 9), round(y, 9), round(z, 9)])
                samples[config][pose] = {
                    "positions_world_m": points,
                    "source_id_map_sha256": topology_digest,
                    "evaluated_mesh_vertices": len(evaluated_ids),
                    "evaluated_mesh_triangles": 400,
                }
        raw_region = {
            "groups": list(contract["groups"]),
            "weight_threshold": flexion.REGION_WEIGHT_THRESHOLD,
            "selected_source_vertex_ids": ids,
            "selected_source_group_weight_sum": weights,
            "original_pv_mask_weights": pv_weights,
            "source_triangle_count": len(triangles),
            "source_vertex_ids": ids,
            "triangles": triangles,
            "edges": flexion._edge_pairs(triangles),
            "connected_components": 1,
            "samples": samples,
        }
        raw_regions[region_name] = raw_region
        region_reports[region_name] = {
            "selection": {
                "groups": list(contract["groups"]),
                "weight_threshold": flexion.REGION_WEIGHT_THRESHOLD,
                "source_vertex_count": len(ids),
                "measured_vertex_count": len(ids),
                "triangle_count": len(triangles),
                "edge_count": len(raw_region["edges"]),
                "connected_components": 1,
            },
            "skin_group_weight_sum": flexion._mask_summary(weights),
            "original_pv_mask_coverage": flexion._mask_summary(pv_weights),
            "measurements": flexion._metrics_for_region(raw_region),
        }

    evaluated_topology = {
        config: {
            pose: {
                "source_vertex_ids": evaluated_ids,
                "source_id_map_sha256": topology_digest,
                "evaluated_mesh_vertices": len(evaluated_ids),
                "evaluated_mesh_triangles": 400,
            }
            for pose in flexion.POSE_KEYS
        }
        for config in flexion.CONFIGURATIONS
    }
    geometry = {
        "schema": flexion.GEOMETRY_SCHEMA,
        "source_sha256": flexion.SOURCE_SHA256,
        "source_vertex_count": 19158,
        "evaluated_topology": evaluated_topology,
        "regions": raw_regions,
    }
    geometry_path = output / "geometry.json"
    geometry_path.write_bytes(flexion._json_bytes(geometry))

    pose_states = {
        "neutral": {
            "right_elbow": _joint_pose("right_elbow", 12.0, [0.0, 0.0, 0.0]),
            "left_knee": _joint_pose("left_knee", 18.0, [0.0, 0.0, 0.0]),
        },
        "right_elbow_deep": {
            "right_elbow": _joint_pose("right_elbow", 95.0, [0.1, 0.2, 1.3]),
            "left_knee": _joint_pose("left_knee", 18.0, [0.0, 0.0, 0.0]),
        },
        "left_knee_deep": {
            "right_elbow": _joint_pose("right_elbow", 12.0, [0.0, 0.0, 0.0]),
            "left_knee": _joint_pose("left_knee", 101.0, [0.2, 0.1, 0.4]),
        },
    }
    saved_front_matrix = _fake_saved_front_view_matrix()
    renders = {}
    png = _png(2, 2)
    for config in flexion.CONFIGURATIONS:
        for joint in flexion.REGIONS:
            for view in ("context", "closeup"):
                name = f"{config}-{joint}-{view}.png"
                (output / name).write_bytes(png)
                renders[name] = {
                    "path": name,
                    "sha256": hashlib.sha256(png).hexdigest(),
                    "bytes": len(png),
                    "resolution_px": [2, 2],
                    "view": "full_body_context" if view == "context" else "matched_joint_closeup",
                    "camera": "ReviewCamera_front" if view == "context" else "DeepFlexionCloseupCamera",
                }
                if view == "closeup":
                    pose_name = "right_elbow_deep" if joint == "right_elbow" else "left_knee_deep"
                    target = pose_states[pose_name][joint]["joint_center_world_m"]
                    profile = flexion.CLOSEUP_CAMERA_PROFILES[joint]
                    joint_state = pose_states[pose_name][joint]
                    matrix = _fake_camera_view_matrix(joint, target, joint_state)
                    renders[name]["target_world_m"] = target
                    renders[name]["joint_projection_normalized"] = [0.5, 0.5]
                    renders[name]["central_crop_bounds_normalized"] = list(
                        flexion.JOINT_CLOSEUP_CENTRAL_CROP_BOUNDS
                    )
                    renders[name]["camera_profile"] = profile["name"]
                    renders[name]["camera_direction_mode"] = profile["direction_mode"]
                    renders[name]["yaw_relative_to_saved_front_degrees"] = flexion._camera_yaw_delta_degrees(
                        saved_front_matrix, matrix
                    )
                    renders[name]["camera_view_matrix_world_to_camera"] = matrix
                    renders[name]["bone_plane_normal_world"] = list(
                        flexion._bone_plane_normal_world(joint_state, joint, f"fixture/{joint}")
                    )
                    renders[name]["bone_plane_camera_alignment"] = flexion._camera_plane_alignment(
                        matrix, joint_state, joint, f"fixture/{joint}"
                    )
                    renders[name]["projected_bone_vectors_camera"] = flexion._projected_bone_vectors_camera(
                        matrix, joint_state, joint, f"fixture/{joint}"
                    )
                    renders[name]["projected_bend_degrees"] = flexion._projected_bend_degrees_from_view_matrix(
                        matrix, joint_state, joint, f"fixture/{joint}"
                    )
                    renders[name]["orthographic_scale_m"] = profile["orthographic_scale_m"]
    stdout = output / "blender.stdout.log"
    stderr = output / "blender.stderr.log"
    stdout.write_bytes(b"pinned Blender completed\n")
    stderr.write_bytes(b"")
    logs = {
        "stdout": {"path": stdout.name, "sha256": flexion.sha256_file(stdout), "bytes": stdout.stat().st_size},
        "stderr": {"path": stderr.name, "sha256": flexion.sha256_file(stderr), "bytes": stderr.stat().st_size},
    }
    attempt = {
        "schema": flexion.ATTEMPT_SCHEMA,
        "status": "complete",
        "source_sha256": flexion.SOURCE_SHA256,
        "target_bend_degrees": flexion.TARGET_BEND_DEGREES,
        "observed_angles_deg": pose_states,
        "return_code": 0,
        "execution": {"offline": True, "factory_startup": True, "embedded_scripts": "disabled", "isolated_user_resources": True, "logs": logs},
    }
    attempt_path = output / "attempt.json"
    attempt_path.write_bytes(flexion._json_bytes(attempt))
    review = output / "REVIEW.md"
    review.write_text("# Diagnostic review\n", encoding="utf-8")

    config_receipts = {}
    for name, config in flexion.CONFIGURATIONS.items():
        if name == "saved_stack":
            stack = [
                {"name": "Armature", "type": "ARMATURE", "use_deform_preserve_volume": False, "vertex_group_mask": ""},
                {"name": "Armature PV", "type": "ARMATURE", "use_deform_preserve_volume": True, "vertex_group_mask": "mhmask-preserve-volume"},
                {"name": "Hide helpers", "type": "MASK"},
            ]
        else:
            stack = [
                {"name": "Deep Flexion Single Armature", "type": "ARMATURE", "use_deform_preserve_volume": config["preserve_volume"], "vertex_group_mask": ""},
                {"name": "Hide helpers", "type": "MASK"},
            ]
        config_receipts[name] = {**config, "stack": stack}

    receipt = {
        "schema": flexion.SCHEMA,
        "status": "diagnostic_only",
        "verdict": "diagnostic_only",
        "source": {"path": flexion.SOURCE_RELATIVE, "sha256_before": flexion.SOURCE_SHA256, "sha256_after": flexion.SOURCE_SHA256, "mutated": False},
        "tool": {"name": "Blender", "version": flexion.SUPPORTED_BLENDER_VERSION, "build_hash": flexion.SUPPORTED_BLENDER_BUILD_HASH, "network": "offline", "embedded_scripts": "disabled", "factory_startup": True, "isolated_user_resources": True},
        "inventory": {
            "body": {
                "object": "Human",
                "stored_vertices": 19158,
                "saved_modifiers": [
                    {"name": "Armature", "type": "ARMATURE", "use_deform_preserve_volume": False, "vertex_group_mask": ""},
                    {"name": "Armature PV", "type": "ARMATURE", "use_deform_preserve_volume": True, "vertex_group_mask": "mhmask-preserve-volume"},
                    {"name": "Hide helpers", "type": "MASK", "use_deform_preserve_volume": None, "vertex_group_mask": None},
                ],
            },
            "rig": {"object": "Human.rigify", "bone_count": 930, "saved_action": "Human.rigifyAction"},
            "camera": {
                "name": "ReviewCamera_front",
                "resolution_px": [2, 2],
                "view_matrix_world_to_camera": saved_front_matrix,
            },
        },
        "target_bend_degrees": flexion.TARGET_BEND_DEGREES,
        "pose_states": pose_states,
        "modifier_configurations": config_receipts,
        "thresholds": {
            "source_region_weight_inclusive_min": flexion.REGION_WEIGHT_THRESHOLD,
            "deep_bend_degrees_inclusive_min": flexion.TARGET_BEND_DEGREES,
            "degenerate_triangle_area_m2_inclusive_max": flexion.DEGENERATE_TRIANGLE_AREA_M2,
            "degenerate_edge_length_m_inclusive_max": flexion.DEGENERATE_EDGE_LENGTH_M,
            "distortion_quantiles": list(flexion.DISTORTION_QUANTILES),
            "quality_pass_threshold": None,
        },
        "regions": region_reports,
        "renders": renders,
        "raw_geometry": {"path": geometry_path.name, "sha256": flexion.sha256_file(geometry_path), "bytes": geometry_path.stat().st_size},
        "volume_measurement": "not measured: selected limb patches are open surfaces, not enclosed volumes",
        "execution": {"return_code": 0, "offline": True, "factory_startup": True, "embedded_scripts": "disabled", "isolated_user_resources": True, "logs": logs},
        "attempt": {"path": attempt_path.name, "sha256": flexion.sha256_file(attempt_path), "bytes": attempt_path.stat().st_size},
        "review_markdown": {"path": review.name, "sha256": flexion.sha256_file(review), "bytes": review.stat().st_size},
    }
    (output / "receipt.json").write_bytes(flexion._json_bytes(receipt))
    return receipt, output, review_root


def _refresh_attempt_echo(receipt: dict, output: Path) -> None:
    attempt_path = output / "attempt.json"
    attempt = json.loads(attempt_path.read_text(encoding="utf-8"))
    attempt["observed_angles_deg"] = receipt["pose_states"]
    attempt_path.write_bytes(flexion._json_bytes(attempt))
    receipt["attempt"] = {
        "path": attempt_path.name,
        "sha256": flexion.sha256_file(attempt_path),
        "bytes": attempt_path.stat().st_size,
    }


def _set_bend_vectors(state: dict, region_name: str, bend_degrees: float) -> None:
    _upper_bone, lower_bone = flexion.REGIONS[region_name]["bones"]
    radians = math.radians(bend_degrees)
    state["bone_vectors_world_m"][lower_bone] = [math.cos(radians), math.sin(radians), 0.0]


def test_receipt_recomputes_area_and_edge_metrics_and_checks_source(tmp_path):
    receipt, output, review_root = _verified_run(tmp_path)

    checked = flexion.validate_receipt(receipt, output, review_root=review_root)

    assert checked is receipt
    assert checked["regions"]["right_elbow"]["measurements"]["single_lbs"]["neutral"][
        "triangle_area_total_ratio_to_neutral"
    ] == 1.0
    assert checked["pose_states"]["right_elbow_deep"]["right_elbow"]["bend_degrees"] == 95.0
    elbow_closeup = checked["renders"]["saved_stack-right_elbow-closeup.png"]
    assert elbow_closeup["joint_projection_normalized"] == [0.5, 0.5]
    assert elbow_closeup["central_crop_bounds_normalized"] == [0.3, 0.3, 0.7, 0.7]
    assert elbow_closeup["camera_profile"] == "right_elbow_bone_plane_oblique"
    assert elbow_closeup["camera_direction_mode"] == "measured_deform_bone_plane_normal_z_positive"
    assert elbow_closeup["projected_bend_degrees"] == pytest.approx(95.0, abs=0.00001)
    assert elbow_closeup["bone_plane_camera_alignment"] >= flexion.BONE_PLANE_CAMERA_ALIGNMENT_MIN
    assert checked["renders"]["saved_stack-left_knee-closeup.png"]["projected_bend_degrees"] == pytest.approx(
        101.0, abs=0.00001
    )
    for joint in flexion.REGIONS:
        matrices = [
            checked["renders"][f"{configuration}-{joint}-closeup.png"][
                "camera_view_matrix_world_to_camera"
            ]
            for configuration in flexion.CONFIGURATIONS
        ]
        assert matrices[0] == matrices[1] == matrices[2]


def test_receipt_rejects_tampered_reported_metrics(tmp_path):
    receipt, output, review_root = _verified_run(tmp_path)
    receipt["regions"]["right_elbow"]["measurements"]["single_lbs"]["deep_flexion"][
        "triangle_area_ratio"
    ]["max"] += 0.01

    with pytest.raises(flexion.DeepFlexionError, match="do not recompute"):
        flexion.validate_receipt(receipt, output, review_root=review_root)


def test_receipt_rejects_tampered_raw_geometry_hash(tmp_path):
    receipt, output, review_root = _verified_run(tmp_path)
    with (output / "geometry.json").open("ab") as stream:
        stream.write(b" ")

    with pytest.raises(flexion.DeepFlexionError, match="digest mismatch"):
        flexion.validate_receipt(receipt, output, review_root=review_root)


def test_receipt_rejects_tampered_render_log_and_projection(tmp_path):
    receipt, output, review_root = _verified_run(tmp_path)
    render = next(path for path in output.glob("*.png"))
    render.write_bytes(render.read_bytes() + b"tampered")
    with pytest.raises(flexion.DeepFlexionError, match="digest mismatch"):
        flexion.validate_receipt(receipt, output, review_root=review_root)

    receipt, output, review_root = _verified_run(tmp_path / "projection")
    receipt["renders"]["saved_stack-right_elbow-closeup.png"]["joint_projection_normalized"] = [0.71, 0.5]
    with pytest.raises(flexion.DeepFlexionError, match="outside the central close-up crop"):
        flexion.validate_receipt(receipt, output, review_root=review_root)

    receipt, output, review_root = _verified_run(tmp_path / "view-mismatch")
    render = receipt["renders"]["single_lbs-right_elbow-closeup.png"]
    matrix = render["camera_view_matrix_world_to_camera"]
    target = render["target_world_m"]
    matrix[0][0] += 0.01
    matrix[0][3] -= 0.01 * target[0]
    with pytest.raises(flexion.DeepFlexionError, match="mismatched joint cameras"):
        flexion.validate_receipt(receipt, output, review_root=review_root)

    receipt, output, review_root = _verified_run(tmp_path / "logs")
    (output / "blender.stdout.log").write_bytes(b"changed")
    with pytest.raises(flexion.DeepFlexionError, match="digest mismatch"):
        flexion.validate_receipt(receipt, output, review_root=review_root)

    receipt, output, review_root = _verified_run(tmp_path / "foreshortened")
    target = receipt["pose_states"]["right_elbow_deep"]["right_elbow"]["joint_center_world_m"]
    foreshortened = _fake_camera_matrix_with_back_direction(target, [0.0, -1.0, 0.0])
    for configuration in flexion.CONFIGURATIONS:
        render = receipt["renders"][f"{configuration}-right_elbow-closeup.png"]
        render["camera_view_matrix_world_to_camera"] = foreshortened
        render["yaw_relative_to_saved_front_degrees"] = flexion._camera_yaw_delta_degrees(
            _fake_saved_front_view_matrix(), foreshortened
        )
    with pytest.raises(flexion.DeepFlexionError, match="not aligned to the measured bone plane"):
        flexion.validate_receipt(receipt, output, review_root=review_root)


def test_receipt_rejects_stale_source_and_subthreshold_bend(tmp_path):
    receipt, output, review_root = _verified_run(tmp_path)
    receipt["source"]["sha256_after"] = "0" * 64
    with pytest.raises(flexion.DeepFlexionError, match="pinned read-only input"):
        flexion.validate_receipt(receipt, output, review_root=review_root)

    receipt, output, review_root = _verified_run(tmp_path / "angle")
    elbow_state = receipt["pose_states"]["right_elbow_deep"]["right_elbow"]
    elbow_state["bend_degrees"] = 89.9
    _set_bend_vectors(elbow_state, "right_elbow", 89.9)
    _refresh_attempt_echo(receipt, output)
    with pytest.raises(flexion.DeepFlexionError, match="target was not reached from bone vectors"):
        flexion.validate_receipt(receipt, output, review_root=review_root)


def test_receipt_rejects_tampered_bend_scalar_when_attempt_echo_matches_but_vectors_do_not(tmp_path):
    receipt, output, review_root = _verified_run(tmp_path)
    elbow_state = receipt["pose_states"]["right_elbow_deep"]["right_elbow"]
    elbow_state["bend_degrees"] = 95.1
    _refresh_attempt_echo(receipt, output)

    with pytest.raises(flexion.DeepFlexionError, match="does not match its world-bone vectors"):
        flexion.validate_receipt(receipt, output, review_root=review_root)


@pytest.mark.parametrize(
    ("vector", "message"),
    [([0.0, 0.0, 0.0], "zero-length"), ([float("inf"), 1.0, 0.0], "non-finite")],
)
def test_receipt_rejects_invalid_deform_bone_vectors(tmp_path, vector, message):
    receipt, output, review_root = _verified_run(tmp_path)
    elbow_state = receipt["pose_states"]["right_elbow_deep"]["right_elbow"]
    upper_bone = flexion.REGIONS["right_elbow"]["bones"][0]
    elbow_state["bone_vectors_world_m"][upper_bone] = vector

    with pytest.raises(flexion.DeepFlexionError, match=message):
        flexion.validate_receipt(receipt, output, review_root=review_root)


def test_receipt_rejects_output_escape_and_artifact_traversal(tmp_path):
    receipt, output, review_root = _verified_run(tmp_path)
    outside = tmp_path / "outside"
    outside.mkdir()
    with pytest.raises(flexion.DeepFlexionError, match="outside the allowed quarantine"):
        flexion.validate_receipt(receipt, outside, review_root=review_root)

    receipt["renders"][next(iter(receipt["renders"]))]["path"] = "../outside.png"
    with pytest.raises(flexion.DeepFlexionError, match="invalid artifact path"):
        flexion.validate_receipt(receipt, output, review_root=review_root)


def test_receipt_rejects_original_pv_mask_coverage_claim(tmp_path):
    receipt, output, review_root = _verified_run(tmp_path)
    geometry_path = output / "geometry.json"
    geometry = json.loads(geometry_path.read_text(encoding="utf-8"))
    geometry["regions"]["right_elbow"]["original_pv_mask_weights"][0] = 0.25
    geometry_path.write_bytes(flexion._json_bytes(geometry))
    receipt["raw_geometry"]["sha256"] = flexion.sha256_file(geometry_path)
    receipt["raw_geometry"]["bytes"] = geometry_path.stat().st_size

    with pytest.raises(flexion.DeepFlexionError, match="invalid source-ID-stable limb patch"):
        flexion.validate_receipt(receipt, output, review_root=review_root)


def test_run_names_reject_paths_and_reuse(tmp_path, monkeypatch):
    review_root = tmp_path / "review"
    review_root.mkdir()
    monkeypatch.setattr(runner, "_review_root", lambda **_kwargs: review_root)

    with pytest.raises(flexion.DeepFlexionError, match="lowercase slug"):
        runner._create_run_directory("../escape")
    created_root, output = runner._create_run_directory("run-1")
    assert created_root == review_root
    assert output.parent == review_root
    with pytest.raises(flexion.DeepFlexionError, match="already exists"):
        runner._create_run_directory("run-1")


def test_verify_requires_existing_quarantine_without_creating_it(tmp_path, monkeypatch):
    repo_root = tmp_path / "missing-repository"
    review_root = repo_root / flexion.REVIEW_RELATIVE
    monkeypatch.setattr(runner, "ROOT", repo_root)

    with pytest.raises(flexion.DeepFlexionError, match="quarantine is missing"):
        runner.verify_run("run-1")

    assert not review_root.exists()
    assert not repo_root.exists()


def test_review_root_rejects_redirected_ancestor_before_creating_paths(tmp_path, monkeypatch):
    repo_root = tmp_path / "missing-repository"
    monkeypatch.setattr(runner, "ROOT", repo_root)
    monkeypatch.setattr(flexion, "_path_chain_has_reparse", lambda _path: True)

    with pytest.raises(flexion.DeepFlexionError, match="contains a symlink or junction"):
        runner._review_root(create=True)

    assert not repo_root.exists()


def test_blender_exit_zero_without_receipt_is_failure_with_logs_preserved(tmp_path, monkeypatch):
    review_root = tmp_path / "review"
    review_root.mkdir()
    blender = tmp_path / "blender.exe"
    blender.write_bytes(b"test executable placeholder")
    monkeypatch.setattr(runner, "_review_root", lambda **_kwargs: review_root)

    def fake_run(_command, **kwargs):
        kwargs["stdout"].write(b"Blender exited 0 without a worker receipt\n")
        kwargs["stderr"].write(b"")
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(runner.subprocess, "run", fake_run)
    with pytest.raises(flexion.DeepFlexionError, match="exit 0 had no complete worker receipt"):
        runner.execute_probe("no-receipt", blender_path=blender)

    output = review_root / "no-receipt"
    attempt = json.loads((output / "attempt.json").read_text(encoding="utf-8"))
    assert attempt["status"] == "failed"
    assert attempt["return_code"] == 0
    assert attempt["execution"]["logs"]["stdout"]["sha256"] == flexion.sha256_file(
        output / "blender.stdout.log"
    )
    assert (output / "blender.stderr.log").exists()
