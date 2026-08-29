"""Build a visual, timed review sheet for the P32 six-minute world-plate cut.

The sheet is derived from the rendered-timeline props. It deliberately labels
the matching assessment as a review aid rather than a new approval state.
"""

from __future__ import annotations

import html
import json
import shutil
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
PROJECT = ROOT / "content/video_engine/projects/systems-and-blowups/pilots/current-bubble-mechanism"
PROPS_PATH = PROJECT / "six-minute-p32-evidence-demo-v1/render/current-bubble-six-minute-p32-v1.props.json"
COVERAGE_PATH = PROJECT / "edit/evidence-coverage-v1/full-episode-evidence-coverage.v1.json"
PUBLIC_ROOT = ROOT / "content/video_engine/editor/public"
OUTPUT_DIR = PROJECT / "edit/evidence-coverage-v1/plate-audit-v1"
IMAGE_DIR = OUTPUT_DIR / "images"
JSON_PATH = OUTPUT_DIR / "six-minute-plate-audit.v1.json"
HTML_PATH = OUTPUT_DIR / "six-minute-plate-audit.html"
FPS = 30


def _excerpt(cue: dict[str, Any], limit: int = 170) -> str:
    text = " ".join(str(cue.get("excerpt", "")).split())
    return text if len(text) <= limit else f"{text[: limit - 1].rstrip()}…"


def _review_group(asset_id: str) -> tuple[str, str]:
    """Return transparent review labels, not editorial approvals."""
    if asset_id == "sentence-native-beat-01-003-bubble-reflex-v1":
        return "replacement_applied", "Literal bubble-reflex replacement for the removed city-box plate."
    if asset_id == "sentence-native-beat-01-013-hidden-safe-index-loop-v1":
        return "replacement_applied", "Literal hidden-feedback replacement for the removed city-box plate."
    if asset_id.startswith("sentence-native-"):
        return "sentence_matched", "Sentence-native plate; review visual readability against its displayed narration."
    if asset_id in {
        "index-fund-weighted-inflows-v2",
        "accelerator-memory-bandwidth-gate-v1",
        "hbm-adjacent-accelerator-v1",
        "hbm-physical-inputs-gate-v1",
        "fixed-oven-capacity-wedding-cake-v1",
        "commodity-cycle-versus-qualified-agreements-v1",
        "buyer-reservation-rail-v1",
        "strategic-chokepoint-network-v1",
    }:
        return "direct_mechanism", "Mechanism plate; review that its visual read lands before the next cut."
    return "contextual_review", "Contextual hero plate; needs a human check for immediate visual read."


def _copy_image(asset_id: str, public_path: str) -> str:
    source = (PUBLIC_ROOT / public_path).resolve()
    if not source.is_file():
        raise FileNotFoundError(f"Staged world plate missing: {source}")
    target = IMAGE_DIR / f"{asset_id}{source.suffix.lower()}"
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.is_file() or target.stat().st_size != source.stat().st_size:
        shutil.copy2(source, target)
    return target.relative_to(OUTPUT_DIR).as_posix()


def main() -> None:
    props = json.loads(PROPS_PATH.read_text(encoding="utf-8"))
    coverage = json.loads(COVERAGE_PATH.read_text(encoding="utf-8"))
    cues = list(coverage["cues"])
    evidence_items = [item for item in props["items"] if item["type"] == "evidence"]
    records: list[dict[str, Any]] = []

    for ordinal, item in enumerate(item for item in props["items"] if item["type"] == "world_plate"):
        start_s = int(item["from"]) / FPS
        end_s = (int(item["from"]) + int(item["durationInFrames"])) / FPS
        overlapping_cues = [
            cue for cue in cues if float(cue["start_s"]) < end_s and float(cue["end_s"]) > start_s
        ]
        evidence = [
            beat for beat in evidence_items
            if int(beat["from"]) / FPS < end_s
            and (int(beat["from"]) + int(beat["durationInFrames"])) / FPS > start_s
        ]
        asset_id = str(item["assetId"])
        review_group, review_reason = _review_group(asset_id)
        records.append(
            {
                "ordinal": ordinal + 1,
                "asset_id": asset_id,
                "start_s": round(start_s, 3),
                "end_s": round(end_s, 3),
                "duration_s": round(end_s - start_s, 3),
                "image": _copy_image(asset_id, str(props["assetMap"][asset_id])),
                "review_group": review_group,
                "review_reason": review_reason,
                "narration": [_excerpt(cue) for cue in overlapping_cues],
                "evidence_count": len(evidence),
                "evidence_asset_ids": [str(beat["assetId"]) for beat in evidence],
            }
        )

    payload = {
        "schema_version": "p32_six_minute_plate_audit.v1",
        "source_props": str(PROPS_PATH.relative_to(ROOT).as_posix()),
        "source_coverage": str(COVERAGE_PATH.relative_to(ROOT).as_posix()),
        "world_beat_count": len(records),
        "removed_asset_ids": ["safe-default-inspection-v1"],
        "review_groups": {
            "replacement_applied": "Replaced an ambiguous city-box plate with a more literal, approved plate.",
            "direct_mechanism": "Existing mechanism plate; assess first-glance readability.",
            "sentence_matched": "Sentence-native plate; assess directness against the adjacent narration.",
            "contextual_review": "Existing contextual plate; assess whether its immediate read is strong enough.",
        },
        "records": records,
    }
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    JSON_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    cards: list[str] = []
    for record in records:
        narration = "<br>".join(html.escape(line) for line in record["narration"])
        evidence = ", ".join(html.escape(asset_id) for asset_id in record["evidence_asset_ids"]) or "No evidence card"
        cards.append(
            f'''<article class="card {html.escape(record["review_group"])}">
  <img src="{html.escape(record["image"])}" alt="{html.escape(record["asset_id"])}">
  <div class="copy"><div class="meta">#{record["ordinal"]:02d} · {record["start_s"]:.1f}s–{record["end_s"]:.1f}s · {record["duration_s"]:.1f}s</div>
  <h2>{html.escape(record["asset_id"])}</h2><p class="group">{html.escape(record["review_group"].replace("_", " "))}</p>
  <p>{html.escape(record["review_reason"])}</p><p class="narration">{narration}</p>
  <p class="evidence"><strong>Evidence cards:</strong> {record["evidence_count"]}<br>{evidence}</p></div></article>'''
        )
    HTML_PATH.write_text(
        f'''<!doctype html><html><head><meta charset="utf-8"><title>P32 six-minute plate audit</title><style>
body{{margin:0;background:#101318;color:#f4eee5;font:15px/1.45 system-ui,sans-serif}} header{{padding:28px 4vw;background:#1b222b;position:sticky;top:0;z-index:3;border-bottom:1px solid #4a5868}}h1{{margin:0;font-size:28px}} header p{{margin:.4rem 0 0;color:#c4cbd2;max-width:75rem}}.legend{{display:flex;gap:8px;flex-wrap:wrap;margin-top:12px}}.tag,.group{{display:inline-block;margin:0;padding:3px 8px;border-radius:99px;font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.04em}}.replacement_applied .group,.tag.replacement_applied{{background:#355b46;color:#d5f8dc}}.direct_mechanism .group,.tag.direct_mechanism{{background:#244968;color:#d5ecff}}.sentence_matched .group,.tag.sentence_matched{{background:#6b4d1d;color:#ffe3a6}}.contextual_review .group,.tag.contextual_review{{background:#5a3d57;color:#ffd9f9}}main{{padding:24px 4vw 56px;display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:18px}}.card{{background:#1b222b;border:1px solid #343f4b;border-radius:12px;overflow:hidden;box-shadow:0 8px 25px #0005}}.card img{{display:block;width:100%;aspect-ratio:16/9;object-fit:cover;background:#000}}.copy{{padding:14px 16px 18px}}.meta{{color:#9db0c0;font-variant-numeric:tabular-nums}}h2{{font-size:16px;line-height:1.2;margin:8px 0;overflow-wrap:anywhere}}.copy p{{margin:9px 0;color:#d1d8de}}.narration{{padding-left:10px;border-left:3px solid #ce9a4e;color:#fff7df!important}}.evidence{{font-size:13px;color:#aebbc6!important;overflow-wrap:anywhere}}</style></head><body>
<header><h1>P32 · Six-minute world-plate readability audit</h1><p>30 timed world beats from the current review cut. This is a grouped human-review sheet—not a new approval state. The ambiguous <code>safe-default-inspection-v1</code> city-box plate is absent; evidence cards remain subordinate and whole-stamped.</p><div class="legend"><span class="tag replacement_applied">replacement applied</span><span class="tag direct_mechanism">direct mechanism</span><span class="tag sentence_matched">sentence matched</span><span class="tag contextual_review">contextual review</span></div></header><main>{''.join(cards)}</main></body></html>''',
        encoding="utf-8",
    )
    print(JSON_PATH)
    print(HTML_PATH)
    print(f"world_beats={len(records)}")


if __name__ == "__main__":
    main()
