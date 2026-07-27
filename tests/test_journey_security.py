from __future__ import annotations

import json

import pytest

from src.services.agentic_journey_service import (
    ActionHostPolicyRegistry,
    BrowserCandidateAction,
    JourneyActionPolicy,
    normalize_host,
)


def test_request_policy_allows_only_safe_read_navigation() -> None:
    allowed = {"novaryu.test", "booking.novaryu.test"}
    assert JourneyActionPolicy.request_allowed(
        "GET", "https://novaryu.test/programs", allowed_hosts=allowed
    )
    assert JourneyActionPolicy.request_allowed(
        "HEAD", "https://booking.novaryu.test/start", allowed_hosts=allowed
    )
    assert not JourneyActionPolicy.request_allowed(
        "POST", "https://novaryu.test/forms", allowed_hosts=allowed
    )
    assert not JourneyActionPolicy.request_allowed(
        "GET", "https://third-party.test/", allowed_hosts=allowed
    )
    assert not JourneyActionPolicy.request_allowed(
        "GET", "file:///etc/passwd", allowed_hosts=allowed
    )


@pytest.mark.parametrize(
    "flag",
    ["mutates_state", "enters_data", "downloads_file", "authenticates"],
)
def test_action_policy_blocks_every_prohibited_capability(flag: str) -> None:
    kwargs = {flag: True}
    candidate = BrowserCandidateAction(
        id="candidate-1",
        action_kind="activate_candidate",
        label="Unsafe",
        role="button",
        **kwargs,
    )
    decision, reason = JourneyActionPolicy.evaluate(
        candidate,
        allowed_hosts={"novaryu.test"},
    )
    assert decision == "blocked"
    assert reason


def test_host_registry_is_versioned_and_operator_approval_is_explicit(tmp_path) -> None:
    policy_dir = tmp_path / "policies"
    policy_dir.mkdir()
    (policy_dir / "known-hosts.v1.json").write_text(
        json.dumps(
            {
                "version": "known-hosts.v1",
                "same_origin": True,
                "vertical_known_hosts": {
                    "national_bjj_registry": ["booking.registry.test"]
                },
            }
        ),
        encoding="utf-8",
    )
    policy = ActionHostPolicyRegistry(policy_dir).load(
        "known-hosts.v1",
        target_url="https://www.novaryu.test/",
        vertical_id="national_bjj_registry",
        approved_unknown_hosts=["approved.vendor.test"],
    )
    assert policy.allowed_hosts == {
        "novaryu.test",
        "booking.registry.test",
        "approved.vendor.test",
    }
    assert normalize_host("https://WWW.NovaRyu.test/path") == "novaryu.test"

    with pytest.raises(ValueError, match="unknown action-host"):
        ActionHostPolicyRegistry(policy_dir).load(
            "known-hosts.v2",
            target_url="https://novaryu.test",
            vertical_id="national_bjj_registry",
        )
