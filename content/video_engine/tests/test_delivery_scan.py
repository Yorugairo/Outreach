from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest
from PIL import Image

from content.video_engine.src.services.delivery_scan import (
    read_approvals,
    scan_claim_delivery,
    summary_line,
)

STYLE = "fam-v3"


def _cutout(path: Path) -> str:
    im = Image.new("RGBA", (1024, 1536), (0, 0, 0, 0))
    for y in range(400, 1100):
        for x in range(300, 700):
            im.putpixel((x, y), (60, 50, 40, 254))
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path)
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _delivery(tmp_path: Path, *, approvals: dict | None, tamper: bool = False) -> dict:
    delivery = tmp_path / "review" / "claims" / "batch-one"
    sha = _cutout(delivery / "objects" / "object-a-v1.png")
    if tamper:
        sha = "a" * 64
    manifest = {
        "style_family": STYLE,
        "assets": [{"asset_id": "object-a-v1", "path": "objects/object-a-v1.png",
                    "sha256": sha, "kind": "prop"}],
    }
    (delivery / "batch-one.manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    if approvals is not None:
        (delivery / "approvals.json").write_text(json.dumps(approvals), encoding="utf-8")
    return {"claim_id": "batch-one", "delivery_dir": str(delivery), "style_family": STYLE}


def test_a_clean_delivery_scans_clean_with_the_agents_approval_noted(tmp_path):
    claim = _delivery(tmp_path, approvals={"approved": ["object-a-v1"], "unresolved": []})

    summary = scan_claim_delivery(claim)

    assert summary["counts"]["fail"] == 0
    assert summary["conflicts"] == []
    assert summary["has_approvals"] is True


def test_an_agent_approval_the_arithmetic_rejects_is_a_named_conflict(tmp_path):
    claim = _delivery(tmp_path, approvals={"approved": ["object-a-v1"]}, tamper=True)

    summary = scan_claim_delivery(claim)

    assert summary["counts"]["fail"] >= 1
    assert summary["conflicts"] == ["object-a-v1"]
    assert "CONFLICTS" in summary_line(summary)


def test_unresolved_slots_from_the_agent_are_carried_into_the_summary(tmp_path):
    claim = _delivery(tmp_path, approvals={
        "approved": [], "unresolved": ["object-a-v1: halo after 2 attempts"],
    })

    summary = scan_claim_delivery(claim)

    assert len(summary["unresolved"]) == 1
    assert "unresolved: 1" in summary_line(summary)


def test_a_delivery_without_approvals_still_scans(tmp_path):
    claim = _delivery(tmp_path, approvals=None)

    summary = scan_claim_delivery(claim)

    assert summary["has_approvals"] is False
    assert read_approvals(claim["delivery_dir"]) is None
