from __future__ import annotations

import copy
import hashlib
import json
import threading
import time
from http.client import HTTPConnection
from pathlib import Path
from urllib.parse import quote

import pytest
import content.video_engine.src.services.production_console as production_console_module

from content.video_engine.src.services.production_console import (
    ProductionConsoleService,
    create_production_console_server,
)


ROOT = Path(__file__).resolve().parents[3]
PROJECT = (
    ROOT
    / "content"
    / "video_engine"
    / "projects"
    / "systems-and-blowups"
    / "pilots"
    / "current-bubble-mechanism"
)
SNAPSHOT = PROJECT / "edit" / "production-console" / "current-bubble.snapshot.v1.json"


def _canonical_hash(payload: dict) -> str:
    core = {key: value for key, value in payload.items() if key != "artifact_hash"}
    return hashlib.sha256(
        json.dumps(core, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ).hexdigest()


@pytest.fixture
def running_console(tmp_path: Path):
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text("<!doctype html><title>console</title>", encoding="utf-8")
    service = ProductionConsoleService(
        PROJECT,
        ROOT,
        SNAPSHOT,
        tmp_path / "runtime",
        dist,
        queue_capacity=2,
    )
    server = create_production_console_server(service, port=0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield service, server
    finally:
        server.shutdown()
        thread.join(timeout=2)
        server.server_close()
        service.close()


def _request(server, method: str, path: str, body: dict | None = None):
    connection = HTTPConnection("127.0.0.1", server.server_address[1], timeout=3)
    encoded = None
    headers = {"X-Request-ID": "test-request-001"}
    if body is not None:
        encoded = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
        headers["Content-Length"] = str(len(encoded))
    connection.request(method, path, body=encoded, headers=headers)
    response = connection.getresponse()
    raw = response.read()
    connection.close()
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        payload = raw
    return response.status, payload


def test_bridge_binds_loopback_serves_static_health_and_snapshot(running_console) -> None:
    service, server = running_console
    assert server.server_address[0] == "127.0.0.1"

    status, body = _request(server, "GET", "/")
    assert status == 200
    assert b"console" in body if isinstance(body, bytes) else "console" in body

    status, body = _request(server, "GET", "/api/health")
    assert status == 200
    assert body["ok"] is True
    assert body["data"]["loopback_only"] is True

    status, body = _request(server, "GET", "/api/snapshot")
    assert status == 200
    assert body["data"]["snapshot_id"] == service.snapshot()["snapshot_id"]
    assert "path" not in body["data"]["assets"][0]
    assert "path_root" not in body["data"]["assets"][0]
    serialized = json.dumps(body)
    assert str(PROJECT) not in serialized
    assert str(ROOT) not in serialized

    for route, expected in (("/api/assets", list), ("/api/reviews", list), ("/api/revisions", list)):
        status, payload = _request(server, "GET", route)
        assert status == 200
        assert isinstance(payload["data"], expected)


def test_media_resolves_snapshot_asset_and_rejects_unknown_or_traversal(running_console) -> None:
    service, server = running_console
    roots = {"project": PROJECT, "repository": ROOT}
    asset = next(
        item
        for item in service.snapshot()["assets"]
        if (roots[item["path_root"]] / item["path"]).is_file()
    )
    status, body = _request(server, "GET", f"/media/{quote(asset['asset_id'])}")
    assert status == 200
    assert isinstance(body, bytes)

    status, body = _request(server, "GET", "/media/%2e%2e%2fprivate")
    assert status in {400, 404}
    assert body["ok"] is False
    assert str(PROJECT) not in json.dumps(body)

    status, body = _request(server, "GET", "/media/not-a-snapshot-asset")
    assert status == 404
    assert body["error"]["code"] == "ASSET_NOT_FOUND"


def test_editor_snapshot_catalog_and_immutable_revision_routes(running_console) -> None:
    service, server = running_console
    status, body = _request(server, "GET", "/api/editor/snapshot")
    assert status == 200
    snapshot = body["data"]
    assert snapshot["schema_version"] == "production_console_snapshot.v2"
    assert len(snapshot["tracks"]) == 8
    assert len(snapshot["words"]) == 2445
    assert "path" not in snapshot["assets"][0]
    assert "path" not in snapshot["project_profile"]["audio"]
    assert str(PROJECT) not in json.dumps(snapshot)

    status, body = _request(server, "GET", "/api/editor/components")
    assert status == 200
    assert len([component for component in body["data"]["components"] if component["source"] == "remotion_bits"]) == 11

    item = {
        "id": "bridge-overlay-001", "trackId": "track-overlays", "kind": "overlay",
        "range": {"startFrame": 30, "endFrame": 180}, "label": "Bridge annotation", "locked": False,
        "overlayKind": "text", "text": "The valuation paradox",
        "transform": {"x": 0, "y": 0, "scaleX": 1, "scaleY": 1, "rotation": 0, "opacity": 1, "zIndex": 60, "crop": {"x": 0, "y": 0, "width": 0.7, "height": 0.2}},
        "keyframes": {},
    }
    core = {
        "schema_version": "editorial_timeline_revision.v1", "revision_id": "bridge-revision-001", "revision_only": True,
        "base_snapshot_hash": snapshot["artifact_hash"], "base_artifact_hashes": snapshot["base_artifact_hashes"], "source_artifact_hashes": snapshot["base_artifact_hashes"],
        "operator": {"operator_id": "test-operator", "created_at": "2026-08-10T12:00:00Z"},
        "operations": [{"op": "insert_item", "item": item}], "note": "bridge proof",
    }
    revision = {**core, "artifact_hash": hashlib.sha256(json.dumps(core, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()}
    status, body = _request(server, "POST", "/api/editor/revisions/validate", revision)
    assert status == 200
    assert body["data"]["valid"] is True

    status, body = _request(server, "POST", "/api/editor/revisions", revision)
    assert status == 201
    assert body["data"]["revision_id"] == "bridge-revision-001"
    status, body = _request(server, "GET", "/api/editor/revisions")
    assert status == 200
    assert body["data"][0]["revision_id"] == "bridge-revision-001"


def test_editor_snapshot_refresh_recompiles_source_hash_boundary(running_console, monkeypatch) -> None:
    service, _server = running_console
    cached = service.editor_snapshot()
    refreshed = copy.deepcopy(cached)
    refreshed["artifact_hash"] = "f" * 64
    calls = 0

    def compile_refresh(*_args, **_kwargs):
        nonlocal calls
        calls += 1
        return refreshed

    monkeypatch.setattr(production_console_module, "compile_production_editor_snapshot", compile_refresh)
    assert service.editor_snapshot()["artifact_hash"] == cached["artifact_hash"]
    assert service.editor_snapshot(refresh=True)["artifact_hash"] == "f" * 64
    assert calls == 1


def test_job_api_is_typed_allowlisted_and_has_no_revision_mutation_route(running_console) -> None:
    service, server = running_console
    status, body = _request(
        server,
        "POST",
        "/api/jobs",
        {
            "operation": "validate_revision",
            "revision_id": "revision-001",
            "request_id": "request-001",
        },
    )
    assert status == 202
    assert body["ok"] is True
    job_id = body["data"]["job_id"]

    deadline = time.monotonic() + 2
    while time.monotonic() < deadline:
        status, job_body = _request(server, "GET", f"/api/jobs/{job_id}")
        if job_body["data"]["state"] in {"succeeded", "failed", "cancelled"}:
            break
        time.sleep(0.02)
    assert status == 200
    assert job_body["data"]["state"] == "succeeded"
    assert job_body["data"]["error"] is None

    status, body = _request(
        server,
        "POST",
        "/api/jobs",
        {
            "operation": "run_shell",
            "revision_id": "revision-001",
            "command": "whoami",
        },
    )
    assert status == 400
    assert body["error"]["code"] in {"OPERATION_NOT_ALLOWED", "INVALID_REQUEST"}
    assert "whoami" not in json.dumps(body)

    status, body = _request(
        server,
        "POST",
        "/api/jobs",
        {
            "operation": "render_preview",
            "revision_id": "revision-001",
            "arguments": {"artifact_ids": ["../escape"]},
        },
    )
    assert status == 400
    assert body["ok"] is False

    status, body = _request(server, "POST", "/api/revisions", {"operations": []})
    assert status == 404
    assert body["ok"] is False

    status, body = _request(server, "DELETE", f"/api/jobs/{job_id}")
    assert status == 200
    assert body["data"]["state"] == "succeeded"
    assert service.queue.get(job_id)["state"] == "succeeded"


def test_media_rejects_snapshot_path_traversal_without_disclosing_paths(tmp_path: Path) -> None:
    snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    snapshot["assets"][0]["path"] = "../escape.png"
    snapshot["artifact_hash"] = _canonical_hash(snapshot)
    repo = tmp_path / "repository"
    repo.mkdir()
    snapshot_path = repo / "snapshot.json"
    snapshot_path.write_text(json.dumps(snapshot), encoding="utf-8")
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text("ok", encoding="utf-8")
    service = ProductionConsoleService(PROJECT, repo, snapshot_path, tmp_path / "runtime", dist)
    server = create_production_console_server(service, port=0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        status, body = _request(server, "GET", "/api/snapshot")
        assert status == 409
        assert body["error"]["code"] == "SNAPSHOT_INVALID"
        assert "escape.png" not in json.dumps(body)
        assert str(tmp_path) not in json.dumps(body)
    finally:
        server.shutdown()
        thread.join(timeout=2)
        server.server_close()
        service.close()


def test_media_rejects_hash_mismatch(tmp_path: Path) -> None:
    snapshot = copy.deepcopy(json.loads(SNAPSHOT.read_text(encoding="utf-8")))
    asset = snapshot["assets"][0]
    asset["sha256"] = "0" * 64
    snapshot["artifact_hash"] = _canonical_hash(snapshot)
    repo = tmp_path / "repository"
    repo.mkdir()
    source_asset = ROOT / asset["path"]
    copied_asset = repo / asset["path"]
    copied_asset.parent.mkdir(parents=True, exist_ok=True)
    copied_asset.write_bytes(source_asset.read_bytes())
    snapshot_path = repo / "snapshot.json"
    snapshot_path.write_text(json.dumps(snapshot), encoding="utf-8")
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text("ok", encoding="utf-8")
    service = ProductionConsoleService(PROJECT, repo, snapshot_path, tmp_path / "runtime", dist)
    server = create_production_console_server(service, port=0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        status, body = _request(server, "GET", f"/media/{quote(asset['asset_id'])}")
        assert status == 409
        assert body["error"]["code"] == "ASSET_HASH_MISMATCH"
        assert str(tmp_path) not in json.dumps(body)
    finally:
        server.shutdown()
        thread.join(timeout=2)
        server.server_close()
        service.close()
