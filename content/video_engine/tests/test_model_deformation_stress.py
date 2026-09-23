from __future__ import annotations

import hashlib
import json
import struct
import zlib

import pytest

from content.video_engine.src.modeling.blender import deformation_stress as stress


def _png(width: int, height: int) -> bytes:
    def chunk(kind: bytes, data: bytes) -> bytes:
        body = kind + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    scanlines = b"".join(b"\x00" + b"\x00" * width * 4 for _ in range(height))
    return (
        stress.PNG_SIGNATURE
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(scanlines))
        + chunk(b"IEND", b"")
    )


def _verified_run(tmp_path):
    review_root = tmp_path / "review"
    output = review_root / "run-1"
    output.mkdir(parents=True)
    regions = {}
    eval_ids = []
    frames_by_region = {}

    for region_index, region_name in enumerate(stress.REGIONS):
        offset = region_index * 121
        vertex_ids = list(range(offset, offset + 121))
        eval_ids.extend(vertex_ids)
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

        raw_frames = {}
        for frame in stress.FRAME_NUMBERS:
            positions = []
            for local_index in range(121):
                row, column = divmod(local_index, 11)
                x = column * 0.1 + region_index * 1.5
                y = row * 0.1
                z = 0.0
                if frame == 27:
                    x = x * 1.15
                    y = y * 0.90
                    z = (column / 10) * 0.02
                elif frame == 52:
                    x = x * 0.95
                    y = y * 1.20
                    z = (row / 10) * 0.03
                positions.append([round(x, 9), round(y, 9), round(z, 9)])
            raw_frames[str(frame)] = {
                "evaluated_mesh_vertices": 242,
                "evaluated_mesh_triangles": 400,
                "source_id_map_sha256": stress._source_id_digest(eval_ids),
                "positions_world_m": positions,
            }
        selected_weights = [1.0] * 121
        selected_mask_weights = [0.0] * 121
        region = stress.REGIONS[region_name]
        regions[region_name] = {
            "label": region["label"],
            "side": region["side"],
            "groups": list(region["groups"]),
            "weight_threshold": stress.REGION_WEIGHT_THRESHOLD,
            "selected_source_vertex_indices": vertex_ids,
            "selected_source_group_weight_sum": selected_weights,
            "selected_source_pv_mask_weights": selected_mask_weights,
            "selected_source_triangle_count": len(triangles),
            "measured_vertex_indices": vertex_ids,
            "triangles": triangles,
            "edges": stress._edge_pairs(triangles),
            "connected_components": 1,
            "frames": raw_frames,
        }
        frames_by_region[region_name] = regions[region_name]

    eval_ids = sorted(eval_ids)
    id_digest = stress._source_id_digest(eval_ids)
    for raw_region in regions.values():
        for frame in raw_region["frames"].values():
            frame["source_id_map_sha256"] = id_digest

    geometry = {
        "schema": stress.GEOMETRY_SCHEMA,
        "source_sha256": stress.SOURCE_SHA256,
        "source_vertex_count": 19158,
        "evaluated_source_vertex_ids": {str(frame): eval_ids for frame in stress.FRAME_NUMBERS},
        "regions": regions,
    }
    geometry_bytes = (
        json.dumps(geometry, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n"
    ).encode("utf-8")
    (output / "geometry.json").write_bytes(geometry_bytes)

    reported_regions = {}
    for name, raw_region in regions.items():
        selected_weights = raw_region["selected_source_group_weight_sum"]
        pv_weights = raw_region["selected_source_pv_mask_weights"]
        reported_regions[name] = {
            "selection": {
                "label": raw_region["label"],
                "side": raw_region["side"],
                "groups": raw_region["groups"],
                "weight_threshold": stress.REGION_WEIGHT_THRESHOLD,
                "selected_source_vertex_count": 121,
                "selected_source_triangle_count": 200,
                "retained_region_vertices": 121,
                "retained_region_triangles": 200,
                "connected_components": 1,
            },
            "skin_group_weight_sum": stress._mask_stats(selected_weights),
            "pv_mask_weights": stress._mask_stats(pv_weights),
            "measurements": stress._region_measurements(raw_region),
        }

    renders = {}
    for frame in stress.FRAME_NUMBERS:
        name = f"frame-{frame:03d}.png"
        content = _png(2, 2)
        (output / name).write_bytes(content)
        renders[str(frame)] = {
            "path": name,
            "sha256": hashlib.sha256(content).hexdigest(),
            "bytes": len(content),
            "resolution_px": [2, 2],
            "frame": frame,
            "meters_per_blender_unit": 1.0,
        }

    receipt = {
        "schema": stress.SCHEMA,
        "status": "diagnostic_only",
        "verdict": "diagnostic_only",
        "source": {
            "path": stress.SOURCE_RELATIVE,
            "sha256_before": stress.SOURCE_SHA256,
            "sha256_after": stress.SOURCE_SHA256,
            "mutated": False,
        },
        "tool": {
            "name": "Blender",
            "version": stress.SUPPORTED_BLENDER_VERSION,
            "build_hash": stress.SUPPORTED_BLENDER_BUILD_HASH,
            "network": "offline",
            "embedded_scripts": "disabled",
        },
        "inventory": {
            "scene": {"name": "Scene"},
            "body": {
                "object": "Human",
                "stored_vertices": 19158,
                "skin_groups": [{"name": "DEF-example"}],
                "modifiers_in_stack_order": [
                    {
                        "name": "Armature",
                        "type": "ARMATURE",
                        "use_deform_preserve_volume": False,
                        "vertex_group_mask": "",
                    },
                    {
                        "name": "Armature PV",
                        "type": "ARMATURE",
                        "use_deform_preserve_volume": True,
                        "vertex_group_mask": "mhmask-preserve-volume",
                    },
                    {"name": "Hide helpers", "type": "MASK"},
                ],
            },
            "rig": {
                "object": "Human.rigify",
                "bone_count": 930,
                "active_actions": ["Human.rigifyAction"],
            },
        },
        "frames": [{"frame": frame, "label": stress.FRAME_LABELS[frame]} for frame in stress.FRAME_NUMBERS],
        "thresholds": {
            "region_weight_sum_inclusive_min": stress.REGION_WEIGHT_THRESHOLD,
            "degenerate_triangle_area_m2_inclusive_max": stress.DEGENERATE_TRIANGLE_AREA_M2,
            "degenerate_edge_length_m_inclusive_max": stress.DEGENERATE_EDGE_LENGTH_M,
            "quality_pass_threshold": None,
            "distortion_quantiles": [0.0, 0.05, 0.5, 0.95, 1.0],
        },
        "volume_measurement": "not measured: an open selected surface patch is not a closed volume",
        "configuration_comparison": (
            "not run: the saved arm/leg PV mask has zero positive weights in both measured regions; "
            "no LBS-versus-DQS or PV-benefit inference is made"
        ),
        "preserve_volume_mask_distribution": {
            "group": "mhmask-preserve-volume",
            "source_positive_vertex_count": 2880,
            "evaluated_visible_vertex_count": 2880,
            "top_deform_groups_by_mask_weighted_support": [{"name": "DEF-fingers"}],
        },
        "regions": reported_regions,
        "raw_geometry": {
            "path": "geometry.json",
            "sha256": hashlib.sha256(geometry_bytes).hexdigest(),
            "bytes": len(geometry_bytes),
        },
        "camera": {"name": "ReviewCamera_front", "projection": "ORTHO", "resolution_px": [2, 2]},
        "renders": renders,
    }
    return receipt, output, review_root


def test_receipt_reopens_geometry_recomputes_metrics_and_checks_source(tmp_path):
    receipt, output, review_root = _verified_run(tmp_path)

    checked = stress.validate_receipt(receipt, output, review_root=review_root)

    assert checked is receipt
    assert checked["regions"]["shoulder_elbow"]["measurements"]["1"]["triangle_area_total_ratio_to_frame_1"] == 1.0


def test_receipt_rejects_wrong_source_hash(tmp_path):
    receipt, output, review_root = _verified_run(tmp_path)
    receipt["source"]["sha256_after"] = "0" * 64

    with pytest.raises(stress.DeformationStressError, match="source does not match"):
        stress.validate_receipt(receipt, output, review_root=review_root)


def test_receipt_rejects_missing_png(tmp_path):
    receipt, output, review_root = _verified_run(tmp_path)
    (output / "frame-027.png").unlink()

    with pytest.raises(stress.DeformationStressError, match="missing or unsafe artifact"):
        stress.validate_receipt(receipt, output, review_root=review_root)


def test_receipt_rejects_changed_png(tmp_path):
    receipt, output, review_root = _verified_run(tmp_path)
    with (output / "frame-027.png").open("ab") as stream:
        stream.write(b"changed")

    with pytest.raises(stress.DeformationStressError, match="artifact digest mismatch"):
        stress.validate_receipt(receipt, output, review_root=review_root)


def test_receipt_rejects_output_escape(tmp_path):
    receipt, output, review_root = _verified_run(tmp_path)
    external_root = tmp_path / "external"
    external_root.mkdir()

    with pytest.raises(stress.DeformationStressError, match="outside the allowed quarantine"):
        stress.validate_receipt(receipt, output, review_root=external_root)


def test_receipt_rejects_escaping_artifact_name(tmp_path):
    receipt, output, review_root = _verified_run(tmp_path)
    receipt["renders"]["1"]["path"] = "../frame-001.png"

    with pytest.raises(stress.DeformationStressError, match="invalid artifact path"):
        stress.validate_receipt(receipt, output, review_root=review_root)


def test_receipt_rejects_evaluated_topology_change_across_frames(tmp_path):
    receipt, output, review_root = _verified_run(tmp_path)
    geometry_path = output / "geometry.json"
    geometry = json.loads(geometry_path.read_text(encoding="utf-8"))
    geometry["regions"]["shoulder_elbow"]["frames"]["27"]["evaluated_mesh_triangles"] += 1
    geometry_bytes = (
        json.dumps(geometry, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n"
    ).encode("utf-8")
    geometry_path.write_bytes(geometry_bytes)
    receipt["raw_geometry"]["sha256"] = hashlib.sha256(geometry_bytes).hexdigest()
    receipt["raw_geometry"]["bytes"] = len(geometry_bytes)

    with pytest.raises(stress.DeformationStressError, match="topology changed across frames"):
        stress.validate_receipt(receipt, output, review_root=review_root)


def test_source_integrity_check_rejects_changed_input(tmp_path):
    source = tmp_path / "source.blend"
    source.write_bytes(b"pinned Blender source")
    expected = hashlib.sha256(source.read_bytes()).hexdigest()
    stress._assert_source_integrity(source, expected)
    source.write_bytes(b"changed source")

    with pytest.raises(stress.DeformationStressError, match="source hash"):
        stress._assert_source_integrity(source, expected)
