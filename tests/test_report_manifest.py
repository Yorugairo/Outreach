from __future__ import annotations

import json
from pathlib import Path

from src.services.report_manifest_service import ReportManifestService


def test_manifest_hashes_and_rejects_missing_or_escaping_files(tmp_path: Path) -> None:
    root = tmp_path / "bundle"
    root.mkdir()
    (root / "report.html").write_text("<p>offline</p>", encoding="utf-8")
    service = ReportManifestService()
    entry = service.file_entry(root, "report.html", role="html")
    manifest = service.build_manifest(
        bundle_id="bundle-1",
        snapshot={
            "id": "snapshot-1", "run_id": "run-1", "report_contract": "operator-v5",
            "schema_version": 1, "source_snapshot_ids": {}, "source_hashes": {},
            "payload_sha256": "a" * 64, "created_at": "2026-07-26T00:00:00+00:00",
        },
        files=[entry], theme_version="client.default.v1", renderer_version="client-renderer.v1",
    )
    service.write_manifest(root, manifest)
    assert service.validate_manifest(root, manifest)["valid"] is True
    assert json.loads((root / "manifest.json").read_text(encoding="utf-8"))["bundle_id"] == "bundle-1"

