"""Build the P33 Gate A review packet for the new elevator world plate."""

from __future__ import annotations

import hashlib
import html
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PROJECT = ROOT / "content/video_engine/projects/systems-and-blowups/pilots/current-bubble-mechanism"
ASSET = PROJECT / "assets/quarantine/p33-two-elevator-mechanism-v1/two-elevator-mechanism-v1.png"
OUTPUT_DIR = PROJECT / "edit/evidence-coverage-v1/p33-gate-a-two-elevator-review"
IMAGE = OUTPUT_DIR / "two-elevator-mechanism-v1.png"
MANIFEST = OUTPUT_DIR / "two-elevator-mechanism-candidate.v1.json"
SHEET = OUTPUT_DIR / "two-elevator-mechanism-review.html"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    if not ASSET.is_file():
        raise FileNotFoundError(f"P33 candidate is missing: {ASSET}")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ASSET, IMAGE)
    payload = {
        "schema_version": "p33_world_plate_candidate.v1",
        "asset_id": "two-elevator-mechanism-v1",
        "candidate_state": "review_only",
        "render_eligible": False,
        "factual_evidence": False,
        "sha256": _sha256(ASSET),
        "dimensions": {"width": 1672, "height": 941},
        "target_range": {"start_s": 70.901, "end_s": 89.803},
        "narration": [
            "somebody else will pay more, while the cash flow, productive use, or scarcity underneath it cannot keep up.",
            "Think of two elevators rising at the same speed.",
            "One is being pulled by a steel cable. The other is rising because everyone inside jumped at once.",
            "The chart looks identical for half a second. The mechanism is completely different.",
        ],
        "semantic_job": "Make the causal difference between a supported rise and a next-buyer rise visible without labels.",
        "visual_contract": {
            "left_elevator": "visible braided cable, motor, counterweight, and grounded industrial drive",
            "right_elevator": "slack/disconnected cable and visibly jumping passengers",
            "evidence_slot": "uncluttered upper-left quadrant",
            "prohibited": ["generated text", "numbers", "logos", "watermarks", "ticker symbols"],
        },
        "gate": "Gate A: operator approval required before any renderer or asset map can reference this candidate.",
    }
    MANIFEST.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    narration = "<br>".join(html.escape(line) for line in payload["narration"])
    SHEET.write_text(
        f'''<!doctype html><html><head><meta charset="utf-8"><title>P33 Gate A: elevator plate</title><style>
body{{margin:0;background:#101318;color:#f4eee5;font:16px/1.5 system-ui,sans-serif}}main{{max-width:1200px;margin:auto;padding:32px}}img{{width:100%;display:block;border:1px solid #4c5965;border-radius:10px;background:#000}}.tag{{display:inline-block;background:#724a28;color:#ffe4b2;border-radius:99px;padding:4px 10px;font-weight:700;font-size:12px;letter-spacing:.06em}}.panel{{margin-top:18px;padding:20px;background:#1b222b;border:1px solid #35414d;border-radius:10px}}h1{{margin:0 0 8px}}p{{color:#d5dde4}}blockquote{{border-left:3px solid #ce9a4e;margin:12px 0;padding-left:14px;color:#fff7df}}</style></head><body><main>
<span class="tag">REVIEW ONLY · NOT IN RENDERER</span><h1>Two-elevator mechanism</h1><p>Target: 70.901–89.803s. This is an explanatory world plate, not factual evidence. The upper-left negative space is reserved for one whole teacher-stamped evidence card.</p>
<img src="two-elevator-mechanism-v1.png" alt="Two adjacent elevator shafts: one cable-driven, one lifted by jumping passengers.">
<div class="panel"><strong>Requested read:</strong> same apparent rise, different mechanism.<blockquote>{narration}</blockquote><p><strong>Gate A decision:</strong> approve this plate for composition, reject it, or request a targeted regeneration. SHA-256: <code>{payload["sha256"]}</code></p></div></main></body></html>''',
        encoding="utf-8",
    )
    print(MANIFEST)
    print(SHEET)


if __name__ == "__main__":
    main()
