from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.services.remediation_blueprint_service import (
    OfflinePrototypeRenderer,
    PrototypeSafetyError,
)
from tests.test_remediation_blueprint import snapshot


def test_approved_blueprint_renders_deterministic_offline_bundle(tmp_path: Path) -> None:
    renderer = OfflinePrototypeRenderer(tmp_path / "output")
    approved = snapshot(review_state="approved")

    first = renderer.render(approved)
    second = renderer.render(approved)

    assert first.id == second.id
    assert first.manifest_sha256 == second.manifest_sha256
    assert first.root == second.root
    assert (first.root / "index.html").read_bytes().startswith(b"<!doctype html>")
    assert (first.root / "data" / "blueprint.json").is_file()
    assert (first.root / "hashes.sha256").is_file()
    html = (first.root / "index.html").read_text(encoding="utf-8").casefold()
    assert "<script" not in html
    assert "javascript:" not in html
    assert "href=\"https://" not in html
    assert "confirm with operator" in html

    manifest = json.loads((first.root / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["manifest_version"] == "prototype-manifest.v1"
    assert manifest["publication"] == {"published": False, "deployment": False, "external_writes": False}
    assert manifest["assets"] == []
    assert renderer.validate(first)["valid"] is True


def test_prototype_manifest_detects_tampering_and_path_escape(tmp_path: Path) -> None:
    renderer = OfflinePrototypeRenderer(tmp_path)
    bundle = renderer.render(snapshot(review_state="approved"))
    html_path = bundle.root / "index.html"
    original = html_path.read_bytes()
    html_path.write_bytes(original + b"\n<!-- changed -->")
    with pytest.raises(PrototypeSafetyError, match="hash mismatch"):
        renderer.validate(bundle)

    with pytest.raises(PrototypeSafetyError, match="contained"):
        renderer._safe_path(bundle.root, "../outside.json")


def test_owner_prototype_is_marked_private_without_changing_renderer_surface(tmp_path: Path) -> None:
    approved = snapshot(review_state="approved")
    owner_payload = approved.to_dict()
    owner_payload["mode"] = "owner_verified"
    owner_payload["content_sha256"] = None
    owner = type(approved)(**owner_payload)
    bundle = OfflinePrototypeRenderer(tmp_path).render(owner)
    payload = json.loads((bundle.root / "data" / "blueprint.json").read_text(encoding="utf-8"))
    assert payload["visibility"] == "private_owner_only"
    assert OfflinePrototypeRenderer(tmp_path).validate(bundle)["published"] is False
