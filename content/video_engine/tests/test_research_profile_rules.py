"""The research lane never runs our layer regen (R26-128, 2026-09-14).

The first reply to R26-119 read "I am waiting for `build_docs_layers.py --write` to finish": the research profile told
the lane to run OUR regen, which blocked on a lock and stalled the order. The bridge's tier 0 runs the layers when a
report lands (`bridge_handlers.run_layers`); the lane reads with `docs_find.py` only. Every profile the bridge sends a
research order under carries the rule as its tier-0 line, and none of them tells the lane to run the regen.
"""
from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
PROFILES = ROOT / ".agents" / "agents"
RESEARCH_PROFILES = (
    "finance-narrative-researcher",
    "animation-video-researcher",
    "video-researcher",
    "video-watcher",
)
RULE = "Tier 0 - never run the layer regen"
REGEN = "build_docs_layers.py"


def profile(name: str) -> str:
    return (PROFILES / f"{name}.md").read_text(encoding="utf-8")


@pytest.mark.parametrize("name", RESEARCH_PROFILES)
def test_every_research_profile_carries_the_tier0_rule(name):
    text = profile(name)
    rule = next((line for line in text.splitlines() if RULE in line), None)
    assert rule is not None, f"{name}.md has no `{RULE}` line"
    assert "docs_find.py" in rule and "read-only" in rule


@pytest.mark.parametrize("name", RESEARCH_PROFILES)
def test_no_research_profile_tells_the_lane_to_run_the_regen(name):
    for number, line in enumerate(profile(name).splitlines(), start=1):
        if REGEN in line:
            assert "never run" in line.lower(), f"{name}.md:{number} names {REGEN} without forbidding it: {line.strip()}"


def test_the_rule_sits_in_the_repository_contract_that_overrides_the_generic_text():
    for name in RESEARCH_PROFILES:
        text = profile(name)
        contract = text.find("This repository's contract")
        assert contract != -1, name
        assert text.find(RULE, contract) != -1, f"{name}.md: the rule is not inside the repository contract"
