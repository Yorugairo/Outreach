from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from content.video_engine.src.services.asset_store import (
    AssetStore,
    AssetStoreError,
    audit_catalog,
    key_for,
    restore_catalog,
)
from content.video_engine.tests.test_asset_store import FakeClient


def _catalog_with_store(tmp_path: Path):
    client = FakeClient()
    store = AssetStore(client, "bucket")
    data = {"a": b"plate-a", "b": b"plate-b"}
    digests = {}
    for name, blob in data.items():
        digest = hashlib.sha256(blob).hexdigest()
        digests[name] = digest
        client.objects[key_for(digest)] = blob
    catalog = {
        "assets": [
            {"asset_id": "asset-a", "path": f"canonical/{'a'}.png", "sha256": digests["a"]},
            {"asset_id": "asset-b", "path": "canonical/b.png", "sha256": digests["b"]},
        ],
    }
    return catalog, store, client, digests


def test_audit_reports_ok_when_every_digest_is_in_the_store(tmp_path):
    catalog, store, _, _ = _catalog_with_store(tmp_path)

    payload = audit_catalog(catalog, store)

    assert payload["ok"] == 2
    assert payload["missing"] == []


def test_audit_names_each_missing_digest(tmp_path):
    catalog, store, client, digests = _catalog_with_store(tmp_path)
    del client.objects[key_for(digests["b"])]

    payload = audit_catalog(catalog, store)

    assert [m["asset_id"] for m in payload["missing"]] == ["asset-b"]


def test_audit_surfaces_the_debt_the_opt_out_created(tmp_path):
    catalog, store, client, digests = _catalog_with_store(tmp_path)
    catalog["assets"][1]["unsynced"] = True
    del client.objects[key_for(digests["b"])]

    payload = audit_catalog(catalog, store)

    assert [u["asset_id"] for u in payload["unsynced"]] == ["asset-b"]
    assert payload["missing"] == [], "unsynced is a named state, not a surprise"


def test_restore_rebuilds_the_canonical_tree_from_a_bare_catalogue(tmp_path):
    catalog, store, _, _ = _catalog_with_store(tmp_path)

    payload = restore_catalog(catalog, tmp_path, store)

    assert len(payload["restored"]) == 2
    assert (tmp_path / "canonical" / "a.png").read_bytes() == b"plate-a"


def test_restore_refuses_to_overwrite_without_force(tmp_path):
    catalog, store, _, _ = _catalog_with_store(tmp_path)
    live = tmp_path / "canonical" / "a.png"
    live.parent.mkdir(parents=True)
    live.write_bytes(b"live-bytes-not-to-be-clobbered")

    payload = restore_catalog(catalog, tmp_path, store)

    assert live.read_bytes() == b"live-bytes-not-to-be-clobbered"
    assert any(s["path"] == "canonical/a.png" for s in payload["skipped"])

    forced = restore_catalog(catalog, tmp_path, store, force=True)
    assert live.read_bytes() == b"plate-a"
    assert any(r["path"] == "canonical/a.png" for r in forced["restored"])


def test_restore_can_target_named_digests_only(tmp_path):
    catalog, store, _, digests = _catalog_with_store(tmp_path)

    payload = restore_catalog(catalog, tmp_path, store, digests=[digests["b"]])

    assert [r["asset_id"] for r in payload["restored"]] == ["asset-b"]
    assert not (tmp_path / "canonical" / "a.png").exists()


def test_restore_fails_loudly_when_the_store_is_missing_a_digest(tmp_path):
    catalog, store, client, digests = _catalog_with_store(tmp_path)
    del client.objects[key_for(digests["a"])]

    with pytest.raises((AssetStoreError, KeyError)):
        restore_catalog(catalog, tmp_path, store)
