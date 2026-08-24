from __future__ import annotations

import hashlib
import shutil
from pathlib import Path

import pytest

from content.video_engine.src.services.asset_store import (
    ENV_ALLOW_UNSYNCED,
    ENV_BUCKET,
    ENV_ENDPOINT,
    ENV_KEY_ID,
    ENV_SECRET,
    AssetStore,
    AssetStoreError,
    from_env,
    key_for,
    sync_promoted_entries,
)


class FakeClient:
    """The store protocol in a dict; no network anywhere near these tests."""

    def __init__(self):
        self.objects: dict[str, bytes] = {}
        self.puts = 0

    def head(self, key: str) -> bool:
        return key in self.objects

    def put(self, key: str, path: Path) -> None:
        self.puts += 1
        self.objects[key] = path.read_bytes()

    def get(self, key: str, path: Path) -> None:
        path.write_bytes(self.objects[key])


def _file(tmp_path: Path, name: str, data: bytes) -> tuple[Path, str]:
    path = tmp_path / name
    path.write_bytes(data)
    return path, hashlib.sha256(data).hexdigest()


def test_keys_are_the_digest_and_nothing_else(tmp_path):
    assert key_for("a" * 64) == "sha256/" + "a" * 64

    with pytest.raises(AssetStoreError):
        key_for("not-a-digest")


def test_ensure_verifies_local_bytes_before_uploading(tmp_path):
    client = FakeClient()
    store = AssetStore(client, "bucket")
    path, digest = _file(tmp_path, "a.png", b"plate-bytes")

    assert store.ensure(digest, path) == "uploaded"
    assert store.ensure(digest, path) == "exists", "idempotent: head-then-skip"
    assert client.puts == 1

    with pytest.raises(AssetStoreError) as excinfo:
        store.ensure("b" * 64, path)
    assert "hashes to" in " ".join(excinfo.value.errors)
    assert key_for("b" * 64) not in client.objects, "wrong bytes never uploaded"


def test_fetch_refuses_bytes_that_do_not_match_their_key(tmp_path):
    client = FakeClient()
    store = AssetStore(client, "bucket")
    _, digest = _file(tmp_path, "a.png", b"real")
    client.objects[key_for(digest)] = b"poisoned"

    with pytest.raises(AssetStoreError):
        store.fetch(digest, tmp_path / "restored.png")

    assert not (tmp_path / "restored.png").exists(), "refused bytes do not stand"


def test_unconfigured_promotion_fails_closed_with_the_fix_named(tmp_path):
    path, digest = _file(tmp_path, "a.png", b"data")
    entries = [{"asset_id": "a", "path": "a.png", "sha256": digest}]

    with pytest.raises(AssetStoreError) as excinfo:
        sync_promoted_entries(entries, tmp_path, env={})

    joined = " ".join(excinfo.value.errors)
    assert ENV_ENDPOINT in joined and ENV_ALLOW_UNSYNCED in joined


def test_the_opt_out_promotes_but_marks_every_entry_unsynced(tmp_path):
    path, digest = _file(tmp_path, "a.png", b"data")
    entries = [{"asset_id": "a", "path": "a.png", "sha256": digest}]

    result = sync_promoted_entries(entries, tmp_path, env={ENV_ALLOW_UNSYNCED: "1"})

    assert result[0]["unsynced"] is True


def test_partial_configuration_is_an_error_not_a_guess(tmp_path):
    with pytest.raises(AssetStoreError) as excinfo:
        from_env({ENV_ENDPOINT: "https://x", ENV_BUCKET: "b"})

    joined = " ".join(excinfo.value.errors)
    assert ENV_KEY_ID in joined and ENV_SECRET in joined


def test_sync_uploads_entry_and_layer_files_by_their_own_digests(tmp_path):
    client = FakeClient()
    store = AssetStore(client, "bucket")
    _, main_digest = _file(tmp_path, "plate.png", b"plate")
    _, far_digest = _file(tmp_path, "far.png", b"far-plane")
    entries = [{
        "asset_id": "world-x",
        "path": "plate.png",
        "sha256": main_digest,
        "layers": [{"depth_layer": "building_or_environment", "path": "far.png", "sha256": far_digest}],
    }]

    result = sync_promoted_entries(entries, tmp_path, store=store)

    assert key_for(main_digest) in client.objects
    assert key_for(far_digest) in client.objects
    assert "unsynced" not in result[0]


def test_a_failed_upload_fails_the_whole_promotion(tmp_path):
    class Refusing(FakeClient):
        def put(self, key: str, path: Path) -> None:
            raise AssetStoreError(["bucket said no"])

    store = AssetStore(Refusing(), "bucket")
    _, digest = _file(tmp_path, "a.png", b"data")
    entries = [{"asset_id": "a", "path": "a.png", "sha256": digest}]

    with pytest.raises(AssetStoreError):
        sync_promoted_entries(entries, tmp_path, store=store)


def test_round_trip_restores_byte_identical_files(tmp_path):
    client = FakeClient()
    store = AssetStore(client, "bucket")
    source, digest = _file(tmp_path, "a.png", b"the-canonical-bytes")
    store.ensure(digest, source)
    source.unlink()  # the disk dies

    restored = store.fetch(digest, tmp_path / "canonical" / "a.png")

    assert restored.read_bytes() == b"the-canonical-bytes"
