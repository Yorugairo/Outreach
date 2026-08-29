"""Persist the approved P33 Gate A decision against the exact candidate hash."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PROJECT = ROOT / "content/video_engine/projects/systems-and-blowups/pilots/current-bubble-mechanism"
ASSET = PROJECT / "assets/quarantine/p33-two-elevator-mechanism-v1/two-elevator-mechanism-v1.png"
OUTPUT = PROJECT / "edit/evidence-coverage-v1/p33-gate-a-two-elevator-review/two-elevator-mechanism-approval.v1.json"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    if not ASSET.is_file():
        raise FileNotFoundError(ASSET)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "p33_world_plate_approval.v1",
        "asset_id": "two-elevator-mechanism-v1",
        "asset_path": ASSET.relative_to(ROOT).as_posix(),
        "asset_sha256": _sha256(ASSET),
        "operator_decision": "approved_for_composition",
        "approved_at": "2026-08-16",
        "approval_basis": "operator approved Gate A review in current task",
        "render_eligible": True,
        "factual_evidence": False,
    }
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(OUTPUT)


if __name__ == "__main__":
    main()
