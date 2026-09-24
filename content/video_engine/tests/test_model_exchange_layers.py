"""Hash-pinned source-clock to 24 fps exchange layer evidence."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
from uuid import uuid4

import pytest
from PIL import Image

from content.video_engine.src.modeling import exchange_layers as exchange


@pytest.fixture(scope="module")
def bundle(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, Path, Path, Path]:
    root = exchange.ROOT
    source_dir = root / exchange.SOURCE_BUNDLE_RELATIVE
    if not (source_dir / "source-exchange.blend").is_file() or not (source_dir / "receipt.json").is_file():
        pytest.skip("requires the ignored parent-pinned T5a.3 saved-scene bundle")
    if not exchange.BLENDER.is_file():
        pytest.skip("requires the pinned offline Blender 5.2.2 LTS executable")
    pytest_temp_root = tmp_path_factory.getbasetemp().resolve(strict=True)
    review_root = tmp_path_factory.mktemp("fighter-planes-t7a5-review").resolve(strict=True)
    try:
        review_root.relative_to(pytest_temp_root)
    except ValueError as exc:
        raise AssertionError("test review output must stay below pytest's temporary base") from exc
    output = review_root / f"fighter-planes-29frame-t7a5-test-{uuid4().hex}"
    try:
        receipt_path = exchange.build_exchange_layers(
            output, root=root, source_dir=source_dir, blender=exchange.BLENDER, review_root=review_root,
        )
        assert receipt_path.parent == output
        yield root, source_dir, review_root, receipt_path
    finally:
        # This is the exact pytest-created directory, not the repository review quarantine.
        cleanup_root = review_root.resolve(strict=True)
        try:
            cleanup_root.relative_to(pytest_temp_root)
        except ValueError as exc:
            raise AssertionError("refusing to clean outside pytest's temporary base") from exc
        if cleanup_root == pytest_temp_root:
            raise AssertionError("refusing to clean pytest's temporary base itself")
        shutil.rmtree(cleanup_root)
        assert not cleanup_root.exists(), "fixture review output persisted after module teardown"


def _copied_bundle(bundle: tuple[Path, Path, Path, Path], name: str) -> tuple[Path, Path, Path, Path]:
    root, source_dir, review_root, receipt_path = bundle
    output = receipt_path.parent
    copied = review_root / name
    shutil.copytree(output, copied)
    return root, source_dir, review_root, copied / "receipt.json"


def _read_receipt(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_receipt(path: Path, receipt: dict) -> None:
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_exact_nearest_source_mapping_preserves_contact_samples() -> None:
    expected = tuple((5 * frame + 1) // 4 for frame in range(29))
    assert exchange.source_frame_map() == expected
    assert (expected[0], expected[-1]) == (0, 35)
    assert [exchange.source_frame_for_output(frame) for frame in (8, 9, 10, 19, 20, 21)] == [10, 11, 12, 24, 25, 26]
    assert [exchange.output_frames_for_source(frame) for frame in (10, 11, 12, 24, 25, 26)] == [
        [8], [9], [10], [19], [20], [21],
    ]
    assert exchange._event_ids(10) == ["right_hand_contact_window_start"]
    assert exchange._event_ids(11) == ["right_hand_contact_window_end"]
    assert exchange._event_ids(12) == ["right_hand_follow_through"]
    assert exchange._event_ids(24) == ["left_hook_contact"]
    assert exchange._event_ids(25) == ["receiving_head_response"]
    assert exchange._event_ids(26) == ["left_hand_follow_through"]


def test_single_actor_opaque_alpha_does_not_overflow_byte_inverse() -> None:
    exchange._ensure_host_dependencies()
    alpha = exchange.np.asarray([[255, 0, 128]], dtype=exchange.np.uint8)
    matte_a = exchange.np.asarray([[0.0, 0.0, 0.0]], dtype=exchange.np.float64)
    matte_b = exchange.np.asarray([[1.0, 0.0, 1.0]], dtype=exchange.np.float64)
    alpha_a, alpha_b, metrics = exchange._normalize_visible_coverage(alpha, matte_a, matte_b)

    assert alpha_a.tolist() == [[0, 0, 0]]
    assert alpha_b.tolist() == [[255, 0, 128]]
    assert metrics["unassigned_coverage_pixel_count_over_2_255"] == 0
    assert metrics["duplicate_coverage_pixel_count_over_2_255"] == 0


def test_two_fighter_scene_uses_equal_depth_and_authored_layer_order() -> None:
    assets = {
        key: {"path": f"planes/{key}/image/frame-000.png", "sha256": "0" * 64}
        for key in exchange.FIGHTER_LAYERS
    }
    document = exchange._scene_document(assets)
    fighters = [layer for layer in document["layers"] if layer["kind"] == "character"]

    assert [layer["layer_id"] for layer in fighters] == [
        exchange.FIGHTER_LAYERS[key]["layer_id"]
        for key in exchange.OCCLUSION_CONTRACT["source_over_order_back_to_front"]
    ]
    assert [layer["depth"] for layer in fighters] == [1.0, 1.0]
    assert document["projection_groups"] == [{
        "layer_ids": [
            exchange.FIGHTER_LAYERS[key]["layer_id"]
            for key in exchange.OCCLUSION_CONTRACT["projection_group"]["layer_keys_back_to_front"]
        ],
        "mode": "source_over_before_projection",
    }]
    assert document["camera"]["keyframes"] == [
        {**key, "ease": "smoothstep"} for key in exchange.CAMERA_KEYFRAMES
    ]
    assert "fixed_source_view_recomposition_verified" not in document


def test_post_camera_metrics_compare_rgba_and_rgb_canvas_extents() -> None:
    exchange._ensure_host_dependencies()
    rgb = Image.new("RGB", (3, 2), (10, 20, 30))
    rgba = exchange.np.zeros((2, 3, 4), dtype=exchange.np.uint8)
    rgba[..., :3] = (10, 20, 30)
    rgba[..., 3] = 255
    metrics = exchange._layered_rgb_metrics(rgb, rgb, rgba, rgba)

    assert metrics["max_channel_error_8bit"] == 0
    assert metrics["actor_alpha_max_error_8bit"] == 0
    assert metrics["affected_pixel_count_over_1"] == 0


def test_v1_receipt_rejects_stale_implementation_hash() -> None:
    old_receipt = exchange.ROOT / exchange.REVIEW_RELATIVE / "exchange-sequence-eol-v2" / "receipt.json"
    if not old_receipt.is_file():
        pytest.skip("requires the ignored historical v1 exchange receipt")
    with pytest.raises(exchange.ExchangeLayersError, match="exchange_layers.py implementation SHA-256 differs"):
        exchange.validate_bundle(old_receipt, root=exchange.ROOT)


def test_v2_receipt_rejects_missing_or_stale_layered_implementation_hash(bundle) -> None:
    root, source_dir, review_root, receipt_path = _copied_bundle(bundle, "stale-layered-implementation-hash")
    receipt = _read_receipt(receipt_path)
    implementation = receipt["implementation"]

    implementation["layered_module_sha256"] = "0" * 64
    _write_receipt(receipt_path, receipt)
    with pytest.raises(exchange.ExchangeLayersError, match="layered.py implementation SHA-256 differs"):
        exchange.validate_bundle(receipt_path, root=root, source_dir=source_dir, review_root=review_root)

    implementation.pop("layered_module_sha256")
    _write_receipt(receipt_path, receipt)
    with pytest.raises(exchange.ExchangeLayersError, match="layered.py implementation SHA-256 pin is malformed"):
        exchange.validate_bundle(receipt_path, root=root, source_dir=source_dir, review_root=review_root)


@pytest.mark.parametrize(
    ("recorded_bytes", "checkout_bytes"),
    [
        (b"VALUE = 42\nNEXT = True\n", b"VALUE = 42\r\nNEXT = True\r\n"),
        (b"VALUE = 42\r\nNEXT = True\r\n", b"VALUE = 42\nNEXT = True\n"),
        (b"VALUE = 42\nNEXT = True\n", b"VALUE = 42\nNEXT = True\n"),
    ],
)
def test_tracked_python_hash_accepts_exact_or_lf_crlf_equivalent_bytes(
    tmp_path: Path,
    recorded_bytes: bytes,
    checkout_bytes: bytes,
) -> None:
    implementation = tmp_path / "implementation.py"
    implementation.write_bytes(checkout_bytes)
    expected = hashlib.sha256(recorded_bytes).hexdigest()

    assert exchange._verify_tracked_python_sha256(implementation, expected, "test implementation") in {
        "exact", "lf_crlf_equivalent",
    }


def test_tracked_python_hash_rejects_code_changes_and_lone_cr_endings(tmp_path: Path) -> None:
    recorded = b"VALUE = 42\nNEXT = True\n"
    implementation = tmp_path / "implementation.py"
    implementation.write_bytes(b"VALUE = 43\r\nNEXT = True\r\n")
    with pytest.raises(exchange.ExchangeLayersError, match="only exact bytes or LF/CRLF-only"):
        exchange._verify_tracked_python_sha256(
            implementation, hashlib.sha256(recorded).hexdigest(), "test implementation",
        )

    implementation.write_bytes(recorded.replace(b"\n", b"\r"))
    with pytest.raises(exchange.ExchangeLayersError, match="only exact bytes or LF/CRLF-only"):
        exchange._verify_tracked_python_sha256(
            implementation, hashlib.sha256(recorded).hexdigest(), "test implementation",
        )


def test_build_reopens_saved_scene_and_verifies_independent_fighter_planes(bundle) -> None:
    root, source_dir, review_root, receipt_path = bundle
    receipt = _read_receipt(receipt_path)
    result = exchange.validate_bundle(
        receipt_path, root=root, source_dir=source_dir, review_root=review_root,
    )

    assert result["status"] == "verified_review_only"
    assert result["output_frame_count"] == 29
    assert result["shuffled_seek_count"] == 29
    assert result["review_eligible"] is False
    assert receipt["source_mapping"]["rule"] == "floor((5*n+1)/4)"
    assert receipt["source_events"] == exchange.EXPECTED_EVENTS
    assert receipt["source_scene_reopen"]["checked_frames"] == list(range(36))
    assert receipt["source_scene_reopen"]["exposure_verified"] is True
    assert receipt["render_state"]["embedded_scripts"] == "disabled"
    assert receipt["render_state"]["online_mode"] == "offline"
    assert receipt["art_note"] == exchange.DIAGNOSTIC_NOTE
    assert receipt["claims"]["fighter_art_approved"] is False
    assert receipt["claims"]["fall_or_ground_continuation"] is False
    assert receipt["claims"]["audio_changed_or_stretched"] is False
    assert receipt["occlusion_contract"]["hidden_surface_rgb_reconstructed"] is False
    assert receipt["occlusion_contract"]["arbitrary_independent_parallax_supported"] is False
    assert receipt["fixed_source_view_recomposition"]["status"] == "measured_within_declared_limits"
    assert receipt["fixed_source_view_recomposition"]["max_alpha_error_8bit"] == 0
    assert receipt["fixed_source_view_recomposition"]["max_visible_rgb_channel_error_8bit"] <= 1
    assert receipt["fixed_source_view_recomposition"]["max_layered_scene_rgb_channel_error_8bit"] <= 24
    assert receipt["fixed_source_view_recomposition"]["max_layered_scene_actor_alpha_error_8bit"] <= 24
    assert len(receipt["frames"]) == 29
    assert all(row["source_scene_sha256"] == result["source_scene_sha256"] for row in receipt["frames"])
    assert all(row["source_fixture_sha256"] == result["fixture_sha256"] for row in receipt["frames"])
    assert all(set(row["fighter_planes"]) == set(exchange.FIGHTER_LAYERS) for row in receipt["frames"])
    assert all(row["fighter_planes"][key]["image"]["alpha_max"] == 255
               for row in receipt["frames"] for key in exchange.FIGHTER_LAYERS)
    assert all(row["fixed_view_recomposition"]["alpha_max_error_8bit"] == 0
               and row["fixed_view_recomposition"]["visible_rgb_max_channel_error_8bit"] <= 1
               and row["fixed_view_recomposition"]["unassigned_coverage_pixel_count_over_2_255"] == 0
               and row["fixed_view_recomposition"]["duplicate_coverage_pixel_count_over_2_255"] == 0
               for row in receipt["frames"])
    assert all(row["layered_scene_recomposition"]["max_channel_error_8bit"] <= 24
               and row["layered_scene_recomposition"]["mean_channel_error_8bit"] <= 0.003
               and row["layered_scene_recomposition"]["actor_alpha_max_error_8bit"] <= 24
               for row in receipt["frames"])
    assert receipt["frames"][14]["layered_scene_recomposition"]["max_channel_error_8bit"] <= 24
    assert all(row["render_state"]["film_transparent"] is True for row in receipt["frames"])
    assert receipt["preview"]["label"] == exchange.PREVIEW_LABEL
    assert receipt["preview"]["width_px"] == exchange.WIDTH
    assert receipt["preview"]["height_px"] == exchange.HEIGHT
    with Image.open(receipt_path.parent / receipt["preview"]["path"]) as preview:
        assert preview.size == (exchange.WIDTH, exchange.HEIGHT)
        assert preview.n_frames == 29
    assert receipt["contact_sheet"]["frames"] == list(range(29))


def test_rejects_stale_actor_plane_digest(bundle) -> None:
    root, source_dir, review_root, receipt_path = _copied_bundle(bundle, "stale-actor-plane-hash")
    output = receipt_path.parent
    shutil.copyfile(
        output / "planes/fighter_a/image/frame-001.png",
        output / "planes/fighter_a/image/frame-000.png",
    )
    with pytest.raises(exchange.ExchangeLayersError, match="normalized image/mask digest differs at frame 0"):
        exchange.validate_bundle(receipt_path, root=root, source_dir=source_dir, review_root=review_root)


def test_rejects_missing_actor_mask(bundle) -> None:
    root, source_dir, review_root, receipt_path = _copied_bundle(bundle, "missing-actor-mask")
    (receipt_path.parent / "planes/fighter_b/mask/frame-010.png").unlink()
    with pytest.raises(exchange.ExchangeLayersError, match="fighter_b normalized mask path is missing"):
        exchange.validate_bundle(receipt_path, root=root, source_dir=source_dir, review_root=review_root)


def test_rejects_unsafe_receipt_path(bundle) -> None:
    root, source_dir, review_root, receipt_path = _copied_bundle(bundle, "unsafe-receipt-path")
    receipt = _read_receipt(receipt_path)
    receipt["blender_state"]["path"] = "../outside/blender-state.json"
    _write_receipt(receipt_path, receipt)
    with pytest.raises(exchange.ExchangeLayersError, match="unsafe Blender state report path"):
        exchange.validate_bundle(receipt_path, root=root, source_dir=source_dir, review_root=review_root)


def test_rejects_unsupported_authored_view(bundle) -> None:
    root, source_dir, review_root, receipt_path = _copied_bundle(bundle, "unsupported-view")
    output = receipt_path.parent
    receipt = _read_receipt(receipt_path)
    scene_path = output / receipt["layered_scene"]["path"]
    document = json.loads(scene_path.read_text(encoding="utf-8"))
    document["view_envelope_deg"]["yaw_deg"] = [-1, 1]
    scene_path.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    receipt["layered_scene"]["sha256"] = exchange.sha256(scene_path)
    _write_receipt(receipt_path, receipt)
    with pytest.raises(exchange.ExchangeLayersError, match="LayeredScene differs from the equal-depth two-plane source contract"):
        exchange.validate_bundle(receipt_path, root=root, source_dir=source_dir, review_root=review_root)
