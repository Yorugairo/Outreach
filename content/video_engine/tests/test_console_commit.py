from __future__ import annotations

import json
from pathlib import Path

from content.video_engine.tests.test_console_intake_routes import _project


def _triage(client, delivery):
    return client.get("/intake/triage", params={"delivery": delivery})


def test_the_dialog_names_every_asset_and_field_before_writing(tmp_path):
    client, delivery = _project(tmp_path, with_flag=True)
    _triage(client, delivery)
    client.post("/intake/decide", data={
        "delivery": delivery, "asset_id": "actor-odd-v1", "decision": "reject",
    })

    body = client.get("/intake/commit", params={"delivery": delivery}).text

    assert "actor-clean-v1" in body
    assert "rights_state=approved" in body
    assert "review_state=approved_reusable" in body
    assert "render_eligible=true" in body
    assert "bulk, zero exceptions" in body  # the clean default is named as bulk
    assert "actor-odd-v1" in body           # the rejection is listed too


def test_confirm_writes_through_register_assets_and_restamps_the_hash(tmp_path):
    client, delivery = _project(tmp_path)
    catalog_path = tmp_path / "asset-catalog.v1.json"
    before = json.loads(catalog_path.read_text(encoding="utf-8"))
    _triage(client, delivery)

    r = client.post("/intake/commit", data={"delivery": delivery})

    assert "Committed" in r.text
    after = json.loads(catalog_path.read_text(encoding="utf-8"))
    added = {a["asset_id"]: a for a in after["assets"]}
    assert "actor-clean-v1" in added
    entry = added["actor-clean-v1"]
    assert entry["rights_state"] == "approved"
    assert entry["review_state"] == "approved_reusable"
    assert entry["render_eligible"] is True
    # Path is rebound relative to the project root, into the delivery folder.
    assert entry["path"] == "review/batch1/actor-clean-v1.png"
    # The artifact hash is restamped by write_artifact.
    assert after.get("artifact_hash") != before.get("artifact_hash")
    assert len(after["artifact_hash"]) == 64


def test_rejected_and_undecided_assets_are_not_registered(tmp_path):
    client, delivery = _project(tmp_path, with_flag=True)
    catalog_path = tmp_path / "asset-catalog.v1.json"
    _triage(client, delivery)
    client.post("/intake/decide", data={
        "delivery": delivery, "asset_id": "actor-odd-v1", "decision": "reject",
    })

    r = client.post("/intake/commit", data={"delivery": delivery})

    after = json.loads(catalog_path.read_text(encoding="utf-8"))
    ids = {a["asset_id"] for a in after["assets"]}
    assert "actor-clean-v1" in ids
    assert "actor-odd-v1" not in ids
    assert "not registered" in r.text.lower() or "Rejected" in r.text


def test_an_undecided_flag_is_left_out_and_said_so(tmp_path):
    client, delivery = _project(tmp_path, with_flag=True)
    _triage(client, delivery)

    body = client.get("/intake/commit", params={"delivery": delivery}).text

    assert "actor-odd-v1" in body
    assert "undecided" in body.lower()


def test_a_forced_promote_on_a_failing_asset_is_rejected_at_commit(tmp_path):
    """Defence in depth: even a decision smuggled past the triage policy dies here."""

    client, delivery = _project(tmp_path)
    manifest_path = Path(delivery) / "batch1.manifest.json"
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    payload["assets"][0]["sha256"] = "a" * 64  # digest fail
    manifest_path.write_text(json.dumps(payload), encoding="utf-8")
    _triage(client, delivery)
    # Bypass validate_decision by writing into the session directly.
    session = client.app.state.triage.get(delivery)
    session.decisions["actor-clean-v1"] = "promote"

    body = client.get("/intake/commit", params={"delivery": delivery}).text

    assert "cannot be promoted" in body


def test_a_register_guard_failure_reaches_the_operator_verbatim(tmp_path):
    """A duplicate id is the catalogue service's refusal, rendered as-is."""

    client, delivery = _project(tmp_path)
    catalog_path = tmp_path / "asset-catalog.v1.json"
    payload = json.loads(catalog_path.read_text(encoding="utf-8"))
    payload["assets"].append(dict(payload["assets"][0], asset_id="actor-clean-v1"))
    # Keep the catalogue valid: distinct path, same id as the incoming asset.
    catalog_path.write_text(json.dumps(payload), encoding="utf-8")
    _triage(client, delivery)

    r = client.post("/intake/commit", data={"delivery": delivery})

    assert "Commit refused" in r.text or "already in the catalogue" in r.text


def test_commit_without_a_triage_session_is_refused(tmp_path):
    client, delivery = _project(tmp_path)

    body = client.get("/intake/commit", params={"delivery": delivery}).text

    assert "triage it before committing" in body


def test_the_session_is_dropped_after_a_successful_commit(tmp_path):
    client, delivery = _project(tmp_path)
    _triage(client, delivery)

    client.post("/intake/commit", data={"delivery": delivery})

    assert client.app.state.triage.get(delivery) is None
