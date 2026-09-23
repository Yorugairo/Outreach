"""Hash-pinned source-clock to 24 fps exchange layer evidence."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil

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
    review_root = tmp_path_factory.mktemp("model-exchange-layer-review")
    output = review_root / "verified-sequence"
    receipt_path = exchange.build_exchange_layers(
        output, root=root, source_dir=source_dir, blender=exchange.BLENDER, review_root=review_root,
    )
    return root, source_dir, review_root, receipt_path


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


def test_build_reopens_saved_scene_and_verifies_all_phone_frames(bundle) -> None:
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
    assert len(receipt["frames"]) == 29
    assert all(row["source_scene_sha256"] == result["source_scene_sha256"] for row in receipt["frames"])
    assert all(row["source_fixture_sha256"] == result["fixture_sha256"] for row in receipt["frames"])
    assert all(row["motion_layer"]["alpha_max"] == 255 for row in receipt["frames"])
    assert all(row["motion_layer"]["alpha_bounds_px"] for row in receipt["frames"])
    assert all(row["render_state"]["film_transparent"] is True for row in receipt["frames"])
    assert receipt["preview"]["label"] == exchange.PREVIEW_LABEL
    assert receipt["preview"]["width_px"] == exchange.WIDTH
    assert receipt["preview"]["height_px"] == exchange.HEIGHT
    with Image.open(receipt_path.parent / receipt["preview"]["path"]) as preview:
        assert preview.size == (exchange.WIDTH, exchange.HEIGHT)
        assert preview.n_frames == 29


def test_rejects_stale_motion_png_digest(bundle) -> None:
    root, source_dir, review_root, receipt_path = _copied_bundle(bundle, "stale-motion-hash")
    output = receipt_path.parent
    shutil.copyfile(output / "motion/frame-001.png", output / "motion/frame-000.png")
    with pytest.raises(exchange.ExchangeLayersError, match="motion PNG hash"):
        exchange.validate_bundle(receipt_path, root=root, source_dir=source_dir, review_root=review_root)


def test_rejects_missing_motion_frame(bundle) -> None:
    root, source_dir, review_root, receipt_path = _copied_bundle(bundle, "missing-motion-frame")
    (receipt_path.parent / "motion/frame-010.png").unlink()
    with pytest.raises(exchange.ExchangeLayersError, match="motion frame 10 path is missing"):
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
    with pytest.raises(exchange.ExchangeLayersError, match="unsupported or unapproved authored camera view"):
        exchange.validate_bundle(receipt_path, root=root, source_dir=source_dir, review_root=review_root)
