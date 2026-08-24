from __future__ import annotations

import json
from pathlib import Path

from content.video_engine.src.services.delivery_scan import APPROVALS_FILENAME
from content.video_engine.watchdog.__main__ import MARKER_FILENAME, WatchdogCore


def _claim(tmp_path: Path, claim_id: str = "batch-one", status: str = "open") -> dict:
    delivery = tmp_path / "review" / "claims" / claim_id
    delivery.mkdir(parents=True, exist_ok=True)
    return {"claim_id": claim_id, "status": status, "delivery_dir": str(delivery)}


def _core(results: list, sent: list, launched: list) -> WatchdogCore:
    return WatchdogCore(
        scan=lambda claim: {
            "claim_id": claim["claim_id"],
            "counts": {"clean": 2, "flag": 0, "fail": 0},
            "conflicts": [],
            "unresolved": [],
        },
        send=lambda message: sent.append(message),
        launch=lambda claim_id: launched.append(claim_id),
    )


def test_nothing_happens_before_the_completion_signal(tmp_path):
    claim = _claim(tmp_path)
    sent, launched = [], []
    core = _core([], sent, launched)

    assert core.poll_once([claim]) == []
    assert sent == [] and launched == []


def test_a_settled_delivery_is_scanned_notified_and_launched_once(tmp_path):
    claim = _claim(tmp_path)
    delivery = Path(claim["delivery_dir"])
    (delivery / APPROVALS_FILENAME).write_text("{}", encoding="utf-8")
    sent, launched = [], []
    core = _core([], sent, launched)

    # First pass: sighting — debounce, no scan yet.
    assert core.poll_once([claim]) == []
    # Second pass: size unchanged — settled, scan fires.
    performed = core.poll_once([claim])
    assert len(performed) == 1
    assert launched == ["batch-one"]
    assert "2 clean" in sent[0]
    assert (delivery / MARKER_FILENAME).exists()

    # Third pass: the marker suppresses any repeat.
    assert core.poll_once([claim]) == []
    assert len(sent) == 1


def test_a_still_growing_delivery_keeps_debouncing(tmp_path):
    claim = _claim(tmp_path)
    delivery = Path(claim["delivery_dir"])
    (delivery / APPROVALS_FILENAME).write_text("{}", encoding="utf-8")
    sent, launched = [], []
    core = _core([], sent, launched)

    core.poll_once([claim])
    (delivery / "late-file.png").write_bytes(b"still arriving")

    assert core.poll_once([claim]) == [], "size changed — wait another interval"
    assert core.poll_once([claim]) != [], "now settled"


def test_closed_claims_are_never_watched(tmp_path):
    claim = _claim(tmp_path, status="closed")
    (Path(claim["delivery_dir"]) / APPROVALS_FILENAME).write_text("{}", encoding="utf-8")
    sent, launched = [], []
    core = _core([], sent, launched)

    assert core.poll_once([claim]) == []
    assert core.poll_once([claim]) == []


def test_a_restart_does_not_renotify_a_handled_delivery(tmp_path):
    claim = _claim(tmp_path)
    delivery = Path(claim["delivery_dir"])
    (delivery / APPROVALS_FILENAME).write_text("{}", encoding="utf-8")
    (delivery / MARKER_FILENAME).write_text(json.dumps({"counts": {}}), encoding="utf-8")
    sent, launched = [], []
    fresh = _core([], sent, launched)  # a brand-new process

    assert fresh.poll_once([claim]) == []
    assert sent == []
