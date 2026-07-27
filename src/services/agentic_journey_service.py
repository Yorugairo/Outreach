"""Bounded browser journeys over opaque, policy-filtered candidate actions."""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Protocol
from urllib.parse import urljoin, urlsplit

from src.fetchers.http_client import SafeHTTPClient
from src.models import (
    AGENTIC_ALLOWED_ACTIONS,
    AgenticToolStep,
    AgenticWorkItem,
    JourneyEvidenceRun,
    canonical_sha256,
)
from src.repositories.base import InsightRepository


def normalize_host(value: str) -> str:
    candidate = value.strip().casefold().rstrip(".")
    if "://" in candidate:
        candidate = (urlsplit(candidate).hostname or "").casefold().rstrip(".")
    return candidate.removeprefix("www.")


def host_is_allowed(host: str, allowed_hosts: set[str]) -> bool:
    normalized = normalize_host(host)
    return any(
        normalized == allowed or normalized.endswith(f".{allowed}")
        for allowed in allowed_hosts
    )


@dataclass(frozen=True, slots=True)
class BrowserCandidateAction:
    """Opaque action exposed to a model without a URL or selector control surface."""

    id: str
    action_kind: str
    label: str
    role: str
    destination_url: str | None = None
    mutates_state: bool = False
    enters_data: bool = False
    downloads_file: bool = False
    authenticates: bool = False

    def __post_init__(self) -> None:
        if not self.id.strip() or not self.label.strip() or not self.role.strip():
            raise ValueError("browser candidates require opaque ID, label, and role")
        if self.action_kind not in AGENTIC_ALLOWED_ACTIONS:
            raise ValueError(f"candidate action is not enumerated: {self.action_kind}")

    def model_view(self, allowed_hosts: set[str]) -> dict[str, Any]:
        destination_host = normalize_host(self.destination_url or "")
        policy = (
            "allowed"
            if not destination_host or host_is_allowed(destination_host, allowed_hosts)
            else "needs_approval"
        )
        return {
            "action_id": self.id,
            "action_kind": self.action_kind,
            "label": self.label[:240],
            "role": self.role,
            "destination_host": destination_host or None,
            "policy_decision": policy,
        }


@dataclass(frozen=True, slots=True)
class JourneyHostPolicy:
    version: str
    same_origin: bool
    known_hosts: tuple[str, ...]
    approved_unknown_hosts: tuple[str, ...] = ()

    @property
    def allowed_hosts(self) -> set[str]:
        return {
            normalized
            for value in (*self.known_hosts, *self.approved_unknown_hosts)
            if (normalized := normalize_host(value))
        }


class JourneySession(Protocol):
    @property
    def current_url(self) -> str: ...

    def accessibility_observation(self) -> dict[str, Any]: ...

    def candidate_actions(self) -> list[BrowserCandidateAction]: ...

    def perform(self, candidate: BrowserCandidateAction) -> dict[str, Any]: ...

    def evaluate_oracle(self, oracle: dict[str, Any]) -> dict[str, Any]: ...

    def capture(self, label: str) -> dict[str, Any]: ...

    def close(self) -> None: ...


DecisionProvider = Callable[[dict[str, Any]], dict[str, Any]]


class JourneyActionPolicy:
    """Fail-closed policy over an already-enumerated candidate."""

    @classmethod
    def evaluate(
        cls,
        candidate: BrowserCandidateAction,
        *,
        allowed_hosts: set[str],
    ) -> tuple[str, str | None]:
        if (
            candidate.mutates_state
            or candidate.enters_data
            or candidate.downloads_file
            or candidate.authenticates
        ):
            return "blocked", "candidate could change state, enter data, download, or authenticate"
        if candidate.destination_url:
            parsed = urlsplit(candidate.destination_url)
            if parsed.scheme not in {"http", "https"} or not parsed.hostname:
                return "blocked", "candidate destination is not a safe HTTP URL"
            if not host_is_allowed(parsed.hostname, allowed_hosts):
                return "needs_approval", "destination host is not present in this policy version"
        return "allowed", None

    @staticmethod
    def request_allowed(method: str, url: str, *, allowed_hosts: set[str]) -> bool:
        if method.casefold() not in {"get", "head"}:
            return False
        parsed = urlsplit(url)
        return bool(
            parsed.scheme in {"http", "https"}
            and parsed.hostname
            and host_is_allowed(parsed.hostname, allowed_hosts)
        )


class ActionHostPolicyRegistry:
    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path) if path else Path("config/agentic/action-host-policies")

    def load(
        self,
        version: str,
        *,
        target_url: str,
        vertical_id: str,
        approved_unknown_hosts: list[str] | None = None,
    ) -> JourneyHostPolicy:
        target_host = normalize_host(target_url)
        if not target_host:
            raise ValueError("journey host policy requires a target URL")
        policy_path = self.path / f"{version}.json"
        if not policy_path.is_file():
            raise ValueError(f"unknown action-host policy version: {version}")
        raw = json.loads(policy_path.read_text(encoding="utf-8"))
        if raw.get("version") != version or raw.get("same_origin") is not True:
            raise ValueError("action-host policy must be versioned and same-origin by default")
        vertical_hosts = raw.get("vertical_known_hosts", {}).get(vertical_id, [])
        if not isinstance(vertical_hosts, list):
            raise ValueError("vertical known-host policy must be a list")
        approved = tuple(
            normalized
            for value in (approved_unknown_hosts or [])
            if (normalized := normalize_host(value))
        )
        return JourneyHostPolicy(
            version=version,
            same_origin=True,
            known_hosts=(target_host, *(normalize_host(item) for item in vertical_hosts)),
            approved_unknown_hosts=approved,
        )


class AgenticJourneyService:
    """Runs a single journey without giving the decision model browser primitives."""

    def __init__(
        self,
        repository: InsightRepository,
        *,
        artifact_prefix: str = "agentic/journeys",
    ) -> None:
        self.repository = repository
        self.artifact_prefix = artifact_prefix.strip("/")

    def run(
        self,
        *,
        work_item: AgenticWorkItem,
        task: dict[str, Any],
        session: JourneySession,
        host_policy: JourneyHostPolicy,
        decision_provider: DecisionProvider,
    ) -> JourneyEvidenceRun:
        if work_item.work_kind not in {"target_journey", "competitor_journey"}:
            raise ValueError("journey runner requires a journey work item")
        if work_item.max_model_decisions > 12 or work_item.max_browser_actions > 30:
            raise ValueError("journey work item exceeds the browser execution contract")
        target_host = normalize_host(session.current_url)
        allowed_hosts = host_policy.allowed_hosts
        if host_policy.same_origin:
            allowed_hosts.add(target_host)
        if not target_host or not host_is_allowed(target_host, allowed_hosts):
            raise ValueError("journey session is outside the approved host policy")
        task_id = str(task.get("task_id") or "").strip()
        viewport = str(task.get("viewport") or "").strip()
        oracle = task.get("success_oracle")
        if not task_id or viewport not in {"desktop", "mobile"} or not isinstance(oracle, dict):
            raise ValueError("journey task requires ID, viewport, and deterministic oracle")

        started = time.monotonic()
        steps: list[AgenticToolStep] = []
        screenshots: list[str] = []
        limitations: list[str] = []
        blockers: list[dict[str, Any]] = []
        result_status = "unknown"
        oracle_results: list[dict[str, Any]] = []
        initial_capture = session.capture("initial")
        if initial_capture.get("artifact_ref"):
            screenshots.append(str(initial_capture["artifact_ref"]))
        elif initial_capture.get("limitation"):
            limitations.append(str(initial_capture["limitation"]))

        try:
            while (
                len(steps) < work_item.max_browser_actions
                and work_item.model_decisions_used + len(steps)
                < work_item.max_model_decisions
                and time.monotonic() - started < work_item.timeout_seconds
            ):
                candidates = session.candidate_actions()
                by_id = {candidate.id: candidate for candidate in candidates}
                if len(by_id) != len(candidates):
                    raise ValueError("browser candidate IDs must be unique")
                observation = session.accessibility_observation()
                decision_input = {
                    "task": {
                        "task_id": task_id,
                        "objective": str(task.get("objective") or "")[:500],
                        "success_oracle": oracle,
                    },
                    "current": {
                        "url_host": normalize_host(session.current_url),
                        "url_path": urlsplit(session.current_url).path,
                        "accessibility": observation,
                    },
                    "candidate_actions": [
                        candidate.model_view(allowed_hosts) for candidate in candidates
                    ],
                    "budgets": {
                        "model_decisions_remaining": work_item.max_model_decisions - len(steps),
                        "browser_actions_remaining": work_item.max_browser_actions - len(steps),
                    },
                }
                decision = decision_provider(decision_input)
                if not isinstance(decision, dict):
                    raise ValueError("journey decision provider must return a structured decision")
                usage = decision.pop("_usage", {})
                usage = usage if isinstance(usage, dict) else {}
                model_call_ref = str(decision.pop("_model_call_ref", "") or "") or None
                if decision.get("finish") is True:
                    step = AgenticToolStep(
                        work_item_id=work_item.id,
                        sequence=len(steps) + 1,
                        action_kind="capture",
                        candidate_action_id=f"model-finish-{len(steps) + 1}",
                        policy_decision="allowed",
                        before_url=session.current_url,
                        after_url=session.current_url,
                        model_call_ref=model_call_ref,
                        input_tokens=int(usage.get("input_tokens") or 0),
                        output_tokens=int(usage.get("output_tokens") or 0),
                        actual_cost_usd=float(usage.get("actual_cost_usd") or 0.0),
                        outcome="model_finished",
                    )
                    self._persist_step(step)
                    steps.append(step)
                    oracle_result = session.evaluate_oracle(oracle)
                    oracle_results.append(oracle_result)
                    result_status = self._oracle_status(oracle_result)
                    break
                action_id = str(decision.get("action_id") or "").strip()
                candidate = by_id.get(action_id)
                if candidate is None:
                    step = AgenticToolStep(
                        work_item_id=work_item.id,
                        sequence=len(steps) + 1,
                        action_kind="wait",
                        candidate_action_id=action_id or f"invalid-{len(steps) + 1}",
                        policy_decision="blocked",
                        policy_reason="model selected no currently enumerated candidate",
                        before_url=session.current_url,
                        model_call_ref=model_call_ref,
                        input_tokens=int(usage.get("input_tokens") or 0),
                        output_tokens=int(usage.get("output_tokens") or 0),
                        actual_cost_usd=float(usage.get("actual_cost_usd") or 0.0),
                        outcome="invalid_candidate",
                    )
                    self._persist_step(step)
                    steps.append(step)
                    blockers.append(
                        {
                            "kind": "invalid_candidate",
                            "action_id": action_id,
                            "message": "The model selected no currently enumerated candidate.",
                        }
                    )
                    result_status = "blocked"
                    break
                policy_decision, policy_reason = JourneyActionPolicy.evaluate(
                    candidate,
                    allowed_hosts=allowed_hosts,
                )
                before_url = session.current_url
                if policy_decision != "allowed":
                    step = AgenticToolStep(
                        work_item_id=work_item.id,
                        sequence=len(steps) + 1,
                        action_kind=candidate.action_kind,
                        candidate_action_id=candidate.id,
                        policy_decision=policy_decision,
                        policy_reason=policy_reason,
                        before_url=before_url,
                        model_call_ref=model_call_ref,
                        input_tokens=int(usage.get("input_tokens") or 0),
                        output_tokens=int(usage.get("output_tokens") or 0),
                        actual_cost_usd=float(usage.get("actual_cost_usd") or 0.0),
                        outcome="blocked_before_execution",
                    )
                    self._persist_step(step)
                    steps.append(step)
                    blockers.append(
                        {
                            "kind": "unknown_host"
                            if policy_decision == "needs_approval"
                            else "prohibited_action",
                            "candidate_action_id": candidate.id,
                            "policy_decision": policy_decision,
                            "reason": policy_reason,
                        }
                    )
                    result_status = "blocked"
                    break
                outcome = session.perform(candidate)
                after_url = session.current_url
                after_host = normalize_host(after_url)
                if not host_is_allowed(after_host, allowed_hosts):
                    raise RuntimeError("browser escaped the approved host policy")
                step = AgenticToolStep(
                    work_item_id=work_item.id,
                    sequence=len(steps) + 1,
                    action_kind=candidate.action_kind,
                    candidate_action_id=candidate.id,
                    policy_decision="allowed",
                    before_url=before_url,
                    after_url=after_url,
                    dom_ref=outcome.get("dom_ref"),
                    screenshot_ref=outcome.get("screenshot_ref"),
                    model_call_ref=model_call_ref,
                    input_tokens=int(usage.get("input_tokens") or 0),
                    output_tokens=int(usage.get("output_tokens") or 0),
                    actual_cost_usd=float(usage.get("actual_cost_usd") or 0.0),
                    outcome=str(outcome.get("outcome") or "completed"),
                )
                self._persist_step(step)
                steps.append(step)
                if step.screenshot_ref:
                    screenshots.append(step.screenshot_ref)
                oracle_result = session.evaluate_oracle(oracle)
                oracle_results.append(oracle_result)
                if self._oracle_status(oracle_result) == "passed":
                    result_status = "passed"
                    break
            else:
                limitations.append("Journey stopped at its model, browser-action, or time budget.")
                result_status = "partial" if steps else "unknown"
        except Exception as exc:
            # Runtime/policy/budget failures belong to the durable worker's
            # retry and terminal-state machinery. Browser/DOM failures remain
            # bounded evidence limits so one capture problem does not erase an
            # otherwise useful journey.
            if getattr(exc, "failure_class", None):
                raise
            limitations.append(f"Journey execution stopped safely: {type(exc).__name__}: {str(exc)[:300]}")
            result_status = "partial" if steps else "unknown"
        finally:
            final_capture = session.capture("final")
            if final_capture.get("artifact_ref"):
                screenshots.append(str(final_capture["artifact_ref"]))
            elif final_capture.get("limitation"):
                limitations.append(str(final_capture["limitation"]))
            session.close()

        elapsed = min(time.monotonic() - started, float(work_item.timeout_seconds))
        source_sha = canonical_sha256(
            {
                "work_item_source_sha256": work_item.source_sha256,
                "task": task,
                "host_policy": {
                    "version": host_policy.version,
                    "allowed_hosts": sorted(allowed_hosts),
                },
                "step_ids": [step.id for step in steps],
                "oracle_results": oracle_results,
            }
        )
        journey = JourneyEvidenceRun(
            run_id=work_item.run_id,
            attempt_id=work_item.attempt_id,
            work_item_id=work_item.id,
            task_id=task_id,
            vertical_pack_version=work_item.vertical_pack_version,
            viewport=viewport,
            allowed_hosts=sorted(allowed_hosts),
            host_policy_version=host_policy.version,
            source_sha256=source_sha,
            result_status=result_status,
            mode=work_item.mode,
            tool_step_ids=[step.id for step in steps],
            oracle_results=oracle_results,
            blockers=blockers,
            screenshot_refs=list(dict.fromkeys(screenshots)),
            limitations=list(dict.fromkeys(limitations)),
            model_decisions=len(steps),
            browser_actions=sum(step.policy_decision == "allowed" for step in steps),
            elapsed_seconds=elapsed,
        )
        save = getattr(self.repository, "save_journey_evidence_run", None)
        return save(journey) if callable(save) else journey

    def _persist_step(self, step: AgenticToolStep) -> None:
        save = getattr(self.repository, "append_agentic_tool_step", None)
        if not callable(save):
            save = getattr(self.repository, "save_agentic_tool_step", None)
        if callable(save):
            save(step)

    @staticmethod
    def _oracle_status(result: dict[str, Any]) -> str:
        status = str(result.get("status") or "unknown")
        return status if status in {"passed", "failed", "partial", "unknown"} else "unknown"


class PlaywrightJourneySession:
    """Playwright adapter with GET/HEAD-only networking and opaque locator storage."""

    DESKTOP_VIEWPORT = {"width": 1440, "height": 900}
    MOBILE_VIEWPORT = {"width": 390, "height": 844}

    def __init__(
        self,
        *,
        url: str,
        viewport: str,
        allowed_hosts: set[str],
        artifact_writer: Callable[[str, bytes | dict[str, Any]], str],
        timeout_ms: int = 15_000,
        http_client: SafeHTTPClient | None = None,
    ) -> None:
        if viewport not in {"desktop", "mobile"}:
            raise ValueError("Playwright journey viewport must be desktop or mobile")
        self.allowed_hosts = {normalize_host(item) for item in allowed_hosts}
        self.artifact_writer = artifact_writer
        self.timeout_ms = max(1_000, min(int(timeout_ms), 60_000))
        self.http_client = http_client or SafeHTTPClient()
        self.http_client.validate_destination(url, allowed_hosts=self.allowed_hosts)
        from playwright.sync_api import sync_playwright

        self._playwright_manager = sync_playwright()
        self._playwright = self._playwright_manager.start()
        self._browser = self._playwright.chromium.launch(headless=True)
        selected = (
            self.DESKTOP_VIEWPORT if viewport == "desktop" else self.MOBILE_VIEWPORT
        )
        self._context = self._browser.new_context(
            viewport=selected,
            accept_downloads=False,
            ignore_https_errors=False,
        )
        self._page = self._context.new_page()
        self._locators: dict[str, Any] = {}
        self._generation = 0

        def route_request(route: Any) -> None:
            request = route.request
            if not JourneyActionPolicy.request_allowed(
                request.method,
                request.url,
                allowed_hosts=self.allowed_hosts,
            ):
                route.abort("blockedbyclient")
                return
            route.continue_()

        self._context.route("**/*", route_request)
        self._page.on("dialog", lambda dialog: dialog.dismiss())
        self._page.on("download", lambda download: download.cancel())
        self._page.goto(url, wait_until="domcontentloaded", timeout=self.timeout_ms)
        self._validate_current_url()

    @property
    def current_url(self) -> str:
        return self._page.url

    def accessibility_observation(self) -> dict[str, Any]:
        title = self._page.title()[:300]
        headings = self._page.locator("h1,h2,h3").all_inner_texts()[:30]
        body_text = " ".join(self._page.locator("body").inner_text().split())[:4_000]
        return {"title": title, "headings": headings, "visible_text_excerpt": body_text}

    def candidate_actions(self) -> list[BrowserCandidateAction]:
        self._generation += 1
        self._locators.clear()
        candidates: list[BrowserCandidateAction] = []
        locator = self._page.locator("a,button,[role='link'],[role='button']")
        count = min(locator.count(), 100)
        for index in range(count):
            item = locator.nth(index)
            try:
                if not item.is_visible() or item.is_disabled():
                    continue
                tag = item.evaluate("(element) => element.tagName.toLowerCase()")
                label = " ".join(
                    (
                        item.get_attribute("aria-label")
                        or item.inner_text()
                        or item.get_attribute("title")
                        or tag
                    ).split()
                )[:240]
                href = item.get_attribute("href")
                destination = urljoin(self.current_url, href) if href else None
                inside_form = item.evaluate("(element) => Boolean(element.closest('form'))")
                downloads = item.get_attribute("download") is not None
                input_type = (item.get_attribute("type") or "").casefold()
                candidate_id = f"candidate-{self._generation}-{index + 1}"
                candidate = BrowserCandidateAction(
                    id=candidate_id,
                    action_kind="navigate_candidate" if destination else "activate_candidate",
                    label=label or f"{tag} action",
                    role=item.get_attribute("role") or tag,
                    destination_url=destination,
                    mutates_state=bool(
                        inside_form
                        or input_type in {"submit", "reset"}
                        or any(
                            token in label.casefold()
                            for token in ("buy now", "purchase", "send message", "log in", "sign in")
                        )
                    ),
                    downloads_file=downloads,
                    authenticates=any(
                        token in label.casefold()
                        for token in ("log in", "login", "sign in", "create account")
                    ),
                )
                self._locators[candidate_id] = item
                candidates.append(candidate)
            except Exception:
                continue
        return candidates

    def perform(self, candidate: BrowserCandidateAction) -> dict[str, Any]:
        locator = self._locators.get(candidate.id)
        if locator is None:
            raise ValueError("candidate is stale or was not enumerated by this session")
        before = self.current_url
        locator.click(timeout=self.timeout_ms, no_wait_after=False)
        self._page.wait_for_timeout(250)
        self._validate_current_url()
        dom_ref = self._write_dom_snapshot()
        return {
            "outcome": "navigated" if self.current_url != before else "activated",
            "dom_ref": dom_ref,
        }

    def evaluate_oracle(self, oracle: dict[str, Any]) -> dict[str, Any]:
        required_text = [
            str(value).casefold().strip()
            for value in oracle.get("required_text", [])
            if str(value).strip()
        ]
        required_url_fragments = [
            str(value).casefold().strip()
            for value in oracle.get("required_url_fragments", [])
            if str(value).strip()
        ]
        required_any_text = [
            str(value).casefold().strip()
            for value in oracle.get("required_any_text", [])
            if str(value).strip()
        ]
        required_any_url_fragments = [
            str(value).casefold().strip()
            for value in oracle.get("required_any_url_fragments", [])
            if str(value).strip()
        ]
        visible = self._page.locator("body").inner_text().casefold()
        current = self.current_url.casefold()
        checks = [
            *(
                {"kind": "visible_text", "value": value, "passed": value in visible}
                for value in required_text
            ),
            *(
                {"kind": "url_fragment", "value": value, "passed": value in current}
                for value in required_url_fragments
            ),
        ]
        groups = [
            {
                "kind": "any_visible_text",
                "values": required_any_text,
                "passed": any(value in visible for value in required_any_text),
            }
            for _ in [0]
            if required_any_text
        ] + [
            {
                "kind": "any_url_fragment",
                "values": required_any_url_fragments,
                "passed": any(value in current for value in required_any_url_fragments),
            }
            for _ in [0]
            if required_any_url_fragments
        ]
        if not checks and not groups:
            return {
                "status": "unknown",
                "checks": [],
                "limitation": "The task oracle has no deterministic text or URL checks.",
            }
        required_results = [bool(item["passed"]) for item in checks + groups]
        passed = sum(required_results)
        status = (
            "passed"
            if all(required_results)
            else ("partial" if passed else "failed")
        )
        return {"status": status, "checks": checks, "groups": groups}

    def capture(self, label: str) -> dict[str, Any]:
        try:
            png = self._page.screenshot(
                type="png",
                full_page=True,
                animations="disabled",
            )
            digest = hashlib.sha256(png).hexdigest()
            reference = self.artifact_writer(f"{label}-{digest[:12]}.png", png)
            return {"artifact_ref": reference, "sha256": digest}
        except Exception as exc:
            return {"limitation": f"Screenshot capture failed: {type(exc).__name__}: {exc}"}

    def close(self) -> None:
        for resource in (
            getattr(self, "_context", None),
            getattr(self, "_browser", None),
        ):
            if resource is not None:
                try:
                    resource.close()
                except Exception:
                    pass
        manager = getattr(self, "_playwright_manager", None)
        if manager is not None:
            try:
                manager.stop()
            except Exception:
                pass

    def _validate_current_url(self) -> None:
        host = normalize_host(self.current_url)
        if not host_is_allowed(host, self.allowed_hosts):
            raise RuntimeError("browser navigation escaped the allowed host policy")
        self.http_client.validate_destination(
            self.current_url,
            allowed_hosts=self.allowed_hosts,
        )

    def _write_dom_snapshot(self) -> str:
        payload = {
            "url": self.current_url,
            "observation": self.accessibility_observation(),
        }
        digest = canonical_sha256(payload)
        return self.artifact_writer(f"dom-{digest[:12]}.json", payload)
