"""T9 — the generation request pack view compiles and exports, never calls.

The console mirrors the compile / record split: the route renders the pack the
service compiled and writes it where the operator says, and nothing in the
slice can reach a provider or spend money.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from content.video_engine.console.app import create_app
from content.video_engine.console.routes import generate as generate_routes
from content.video_engine.console.settings import load_settings
from content.video_engine.src.services.director import validate_director_proposal
from content.video_engine.src.services.provisional_coverage import (
    compile_provisional_coverage,
)
from content.video_engine.src.services.visual_prompt_pack import (
    compile_visual_prompt_pack,
)
from content.video_engine.tests.conftest import build_proposal

LANE = "stick_explainer"


@pytest.fixture()
def coverage(paste_brief):
    proposal = validate_director_proposal(build_proposal(paste_brief), brief=paste_brief)
    return compile_provisional_coverage(proposal, brief=paste_brief)


@pytest.fixture()
def coverage_path(coverage, tmp_path: Path) -> Path:
    path = tmp_path / "coverage.json"
    path.write_text(json.dumps(coverage), encoding="utf-8")
    return path


@pytest.fixture()
def client(tmp_path: Path) -> TestClient:
    """The console app with the generate router wired, project root at tmp_path."""

    app = create_app(load_settings(project_root=tmp_path))
    app.include_router(generate_routes.router)
    return TestClient(app)


def test_the_form_renders_without_a_coverage_artifact(client):
    body = client.get("/generate").text

    assert "Coverage artifact" in body
    assert "no provider client" in body


def test_renders_one_copyable_prompt_per_slot(client, coverage, coverage_path):
    body = client.get(
        "/generate", params={"coverage": str(coverage_path), "lane": LANE}
    ).text

    pack = compile_visual_prompt_pack(coverage, lane=LANE)
    # One readonly textarea per group, plus the anchor and negative-prompt blocks.
    assert body.count("<textarea readonly") == len(pack["groups"]) + 2
    assert "no lettering" in body
    assert pack["identity_anchor"] in body
    for group in pack["groups"]:
        assert group["slot_id"] in body


def test_shows_the_expected_delivery_layout_for_intake(client, coverage, coverage_path):
    body = client.get(
        "/generate", params={"coverage": str(coverage_path), "lane": LANE}
    ).text

    pack = compile_visual_prompt_pack(coverage, lane=LANE)
    assert ".manifest.json" in body
    assert "style_family" in body
    for group in pack["groups"]:
        for index in range(pack["variants_per_slot"]):
            assert f"{group['slot_id']}-v{index}.png" in body
    # The dimensions convention intake checks against is stated, not implied.
    assert "1536" in body and "1024" in body


def test_generation_is_stated_as_claims_with_no_provider_client(client, coverage, coverage_path):
    """The P17 promise: subscription-agent claims, never a metered API call."""

    body = client.get(
        "/generate", params={"coverage": str(coverage_path), "lane": LANE}
    ).text

    assert "claims" in body
    assert "no provider client" in body


def test_export_writes_the_pack_under_runtime_only(
    client, coverage, coverage_path, tmp_path
):
    r = client.post("/generate/export", data={
        "coverage": str(coverage_path), "lane": LANE, "variants": 3,
        "name": "energy-drains-pack",
    })

    out = tmp_path / "runtime" / "generation-requests" / "energy-drains-pack.json"
    assert out.exists()
    assert "runtime" in out.parts
    saved = json.loads(out.read_text(encoding="utf-8"))
    pack = compile_visual_prompt_pack(coverage, lane=LANE)
    assert saved["groups"] == pack["groups"]
    assert str(out) in r.text


def test_export_refuses_a_name_that_is_a_path(client, coverage_path, tmp_path):
    r = client.post("/generate/export", data={
        "coverage": str(coverage_path), "lane": LANE, "variants": 3,
        "name": "../../escape",
    })

    assert "bare filename" in r.text
    assert not (tmp_path.parent / "escape.json").exists()


def test_no_generate_route_opens_a_network_connection(
    client, coverage_path, monkeypatch
):
    import socket

    def _forbidden(*args, **kwargs):  # pragma: no cover - regression guard
        raise AssertionError("the generate slice must not touch the network")

    # Hold one portal open so asyncio's Windows self-pipe (a socketpair the
    # event loop builds for itself) exists before connects are forbidden; the
    # routes themselves must then never connect.
    with client:
        monkeypatch.setattr(socket.socket, "connect", _forbidden)

        assert client.get("/generate").status_code == 200
        assert client.get(
            "/generate", params={"coverage": str(coverage_path), "lane": LANE}
        ).status_code == 200
        assert client.post("/generate/export", data={
            "coverage": str(coverage_path), "lane": LANE, "variants": 3,
            "name": "no-network-pack",
        }).status_code == 200


def test_a_missing_coverage_artifact_renders_the_service_error(client, tmp_path):
    body = client.get(
        "/generate", params={"coverage": str(tmp_path / "absent.json"), "lane": LANE}
    ).text

    assert "not found" in body


def test_an_unknown_lane_renders_the_registry_error(client, coverage_path):
    body = client.get(
        "/generate", params={"coverage": str(coverage_path), "lane": "no-such-lane"}
    ).text

    assert "no-such-lane" in body


def test_variants_below_the_service_minimum_are_refused(client, coverage_path):
    body = client.get(
        "/generate",
        params={"coverage": str(coverage_path), "lane": LANE, "variants": 1},
    ).text

    assert "at least 2" in body


# --- Claims (P17 T2) ---------------------------------------------------------

def _claims_env(monkeypatch, tmp_path):
    from content.video_engine.src.services import generation_claim as gc

    monkeypatch.setenv(gc.ENV_CLAIMS_DIR, str(tmp_path / "claims-registry"))
    monkeypatch.setattr(gc, "_run_git", lambda args, cwd: "test-branch")


def test_a_claim_opens_from_explicit_slots_and_shows_its_work_order(tmp_path, monkeypatch, client):
    import json as _json

    _claims_env(monkeypatch, tmp_path)

    r = client.post("/generate/claims/open", data={
        "claim_id": "probe-claim",
        "style_family": "fam-v3",
        "slots_json": _json.dumps([
            {"asset_id": "object-a-v1", "kind": "prop", "prompt": "an abacus"},
        ]),
    }, follow_redirects=True)

    assert r.status_code == 200
    assert "Work Order" in r.text
    assert "object-a-v1" in r.text
    assert "approvals.json" in r.text


def test_an_invalid_claim_is_refused_with_named_errors(tmp_path, monkeypatch, client):
    _claims_env(monkeypatch, tmp_path)

    r = client.post("/generate/claims/open", data={
        "claim_id": "probe-claim", "style_family": "fam", "slots_json": "",
    })

    assert "Claim refused" in r.text


def test_open_claims_are_listed_on_the_generate_page(tmp_path, monkeypatch, client):
    import json as _json

    _claims_env(monkeypatch, tmp_path)
    client.post("/generate/claims/open", data={
        "claim_id": "listed-claim", "style_family": "fam",
        "slots_json": _json.dumps([{"asset_id": "x-v1", "kind": "prop", "prompt": "p"}]),
    })

    body = client.get("/generate").text

    assert "listed-claim" in body


def test_closing_a_claim_returns_to_the_generate_page(tmp_path, monkeypatch, client):
    import json as _json

    _claims_env(monkeypatch, tmp_path)
    client.post("/generate/claims/open", data={
        "claim_id": "closing-claim", "style_family": "fam",
        "slots_json": _json.dumps([{"asset_id": "x-v1", "kind": "prop", "prompt": "p"}]),
    })

    r = client.post("/generate/claims/close", data={"claim_id": "closing-claim"},
                    follow_redirects=True)

    assert r.status_code == 200
    from content.video_engine.src.services.generation_claim import load_claim
    assert load_claim("closing-claim")["status"] == "closed"
