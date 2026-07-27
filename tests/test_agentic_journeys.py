from __future__ import annotations

from typing import Any

from src.models import AgenticWorkItem, canonical_sha256
from src.repositories.file_repository import FileBackedInsightRepository
from src.services.agentic_journey_service import (
    AgenticJourneyService,
    BrowserCandidateAction,
    JourneyHostPolicy,
)


SHA = canonical_sha256({"journey": "fixture"})


def work_item(**overrides: object) -> AgenticWorkItem:
    payload: dict[str, object] = {
        "run_id": "run-1",
        "attempt_id": "attempt-1",
        "evidence_pack_id": "pack-1",
        "vertical_pack_version": "national_bjj_registry.agentic.v1",
        "work_kind": "target_journey",
        "mode": "prospect",
        "source_sha256": SHA,
        "idempotency_key": "run-1:journey:offer",
        "requested_runtime": "hermes",
        "requested_provider": "openrouter",
        "requested_model": "deepseek/deepseek-v4-flash",
        "prompt_version": "journey.v1",
        "rubric_version": "journey.v1",
        "schema_version": "journey.v1",
    }
    payload.update(overrides)
    return AgenticWorkItem(**payload)


class FakeJourneySession:
    def __init__(self, candidate: BrowserCandidateAction) -> None:
        self._current_url = "https://novaryu.test/"
        self.candidate = candidate
        self.performed = 0
        self.closed = False

    @property
    def current_url(self) -> str:
        return self._current_url

    def accessibility_observation(self) -> dict[str, Any]:
        return {
            "title": "Nova Ryu",
            "headings": ["Brazilian Jiu-Jitsu"],
            "visible_text_excerpt": "Programs and beginner classes",
        }

    def candidate_actions(self) -> list[BrowserCandidateAction]:
        return [self.candidate]

    def perform(self, candidate: BrowserCandidateAction) -> dict[str, Any]:
        self.performed += 1
        if candidate.destination_url:
            self._current_url = candidate.destination_url
        return {"outcome": "navigated", "dom_ref": "agentic/dom-1.json"}

    def evaluate_oracle(self, oracle: dict[str, Any]) -> dict[str, Any]:
        passed = "programs" in self._current_url
        return {
            "status": "passed" if passed else "failed",
            "checks": [{"kind": "url_fragment", "value": "programs", "passed": passed}],
        }

    def capture(self, label: str) -> dict[str, Any]:
        return {"artifact_ref": f"agentic/{label}.png"}

    def close(self) -> None:
        self.closed = True


def service_and_item(tmp_path):
    repository = FileBackedInsightRepository(tmp_path)
    item = work_item()
    repository.save_agentic_work_item(item)
    return AgenticJourneyService(repository), repository, item


TASK = {
    "task_id": "offer",
    "task_kind": "offer_discovery",
    "viewport": "desktop",
    "objective": "Find available programs.",
    "success_oracle": {"required_url_fragments": ["programs"]},
}


def test_journey_model_receives_opaque_actions_and_deterministic_oracle(tmp_path) -> None:
    candidate = BrowserCandidateAction(
        id="candidate-1",
        action_kind="navigate_candidate",
        label="Programs",
        role="link",
        destination_url="https://novaryu.test/programs",
    )
    session = FakeJourneySession(candidate)
    decisions: list[dict[str, Any]] = []

    def decide(observation: dict[str, Any]) -> dict[str, Any]:
        decisions.append(observation)
        return {"action_id": "candidate-1"}

    service, repository, item = service_and_item(tmp_path)
    result = service.run(
        work_item=item,
        task=TASK,
        session=session,
        host_policy=JourneyHostPolicy(
            version="known-hosts.v1",
            same_origin=True,
            known_hosts=("novaryu.test",),
        ),
        decision_provider=decide,
    )

    assert result.result_status == "passed"
    assert result.browser_actions == 1
    assert result.model_decisions == 1
    assert result.tool_step_ids
    assert repository.list_agentic_tool_steps(work_item_id=item.id)
    assert session.performed == 1
    assert session.closed is True
    exposed = decisions[0]["candidate_actions"][0]
    assert exposed == {
        "action_id": "candidate-1",
        "action_kind": "navigate_candidate",
        "label": "Programs",
        "role": "link",
        "destination_host": "novaryu.test",
        "policy_decision": "allowed",
    }
    assert "selector" not in exposed
    assert "destination_url" not in exposed


def test_unknown_action_host_requires_approval_and_is_not_navigated(tmp_path) -> None:
    candidate = BrowserCandidateAction(
        id="candidate-external",
        action_kind="navigate_candidate",
        label="Start trial",
        role="link",
        destination_url="https://unknown-booking.test/start",
    )
    session = FakeJourneySession(candidate)
    service, repository, item = service_and_item(tmp_path)
    result = service.run(
        work_item=item,
        task=TASK,
        session=session,
        host_policy=JourneyHostPolicy(
            version="known-hosts.v1",
            same_origin=True,
            known_hosts=("novaryu.test",),
        ),
        decision_provider=lambda _: {"action_id": "candidate-external"},
    )

    assert result.result_status == "blocked"
    assert result.blockers == [
        {
            "kind": "unknown_host",
            "candidate_action_id": "candidate-external",
            "policy_decision": "needs_approval",
            "reason": "destination host is not present in this policy version",
        }
    ]
    assert session.performed == 0
    assert session.current_url == "https://novaryu.test/"
    recorded = repository.list_agentic_tool_steps(work_item_id=item.id)
    assert recorded[0].policy_decision == "needs_approval"
    assert recorded[0].after_url is None


def test_mutating_candidate_fails_closed(tmp_path) -> None:
    candidate = BrowserCandidateAction(
        id="candidate-submit",
        action_kind="activate_candidate",
        label="Submit",
        role="button",
        mutates_state=True,
    )
    session = FakeJourneySession(candidate)
    service, _, item = service_and_item(tmp_path)
    result = service.run(
        work_item=item,
        task=TASK,
        session=session,
        host_policy=JourneyHostPolicy(
            version="known-hosts.v1",
            same_origin=True,
            known_hosts=("novaryu.test",),
        ),
        decision_provider=lambda _: {"action_id": "candidate-submit"},
    )
    assert result.result_status == "blocked"
    assert result.blockers[0]["kind"] == "prohibited_action"
    assert session.performed == 0
